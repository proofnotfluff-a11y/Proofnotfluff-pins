#!/usr/bin/env python3
"""Video engine story finder (Phase 0, the Rat check MVP). Code only, never a model: it reads the week's rat file,
builds every candidate finding, scores it, plans the week and writes candidates.json. The scriptwriter only ever writes
words around the numbers this file chose; every number carries the file path and field it came from.

Spec: the PNF Video Engine Blueprint, "MVP build spec (pinned)" (https://claude.ai/artifact/3ssi8yGEKVxiL7JTD87kzS).
Settings: video/config.json (weights, floors, novelty window, pictures). Input contract: permits/rodents-chicago/weekly.json
(fields source.fetchedAt, window.to, counts and per area name, d7, d30, prev30, change, medClose, closed30, w12).

Candidate types
  A  a neighborhood's jump: d30 of 20 or more against the same 30 days last year (change not null)
  B  the city against last year (counts.change)
  C  the slowest and the fastest City response time (medClose) among areas with closed30 of 20 or more
  D  a run of rising weeks: the last 4 weekly counts in w12 rise every week (d30 floor from config "floors")
A candidate that needs a null field is dropped, never filled in.

Score parts, each 0 to 1 (weights in config): surprise (A, B: |change| / 100; C: distance from the city's median close
time as a share of it; D: the 4-week rise as a share of the first week), local identity (1 a named area, 0.5 the city),
work angle (1 for A and D, 0.5 for B and C), novelty (0 when the same area and type led a video in the last 14 days),
proof strength (d30 / 100; C uses closed30; B scores 1). Ties: larger d30, then the lower area number (the city is 0).

Plan: Monday, Wednesday and Friday use three different story types and three different pictures (map, ranked bars,
12-week line); over the MVP's three weeks every type runs at least twice. The plan is saved in candidates.json, so a
rerun on the same file picks the same story.

Usage
  python3 tools/video_story.py candidates [--data FILE] [--now ISO] [--ledger video/LEDGER.md] [--out FILE]
  python3 tools/video_story.py pick --slot Mon|Wed|Fri [--data FILE] [--now ISO]     the slot's story, as JSON
  python3 tools/video_story.py draft --slot Mon|Wed|Fri --video-id ID [--out FILE]  a spec skeleton (evidence, screen)
  python3 tools/video_story.py --selftest                                           the planted fixtures
Exit 1 on a stale or malformed file (one line, the reason): the engine never guesses a value.
"""
import argparse, datetime as dt, hashlib, itertools, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONFIG = os.path.join(ROOT, "video", "config.json")
TYPES = ("A", "B", "C", "D")
TYPE_NAMES = {"A": "neighborhood jump", "B": "city against last year", "C": "City response time", "D": "rising weeks"}
SLOTS = ("Mon", "Wed", "Fri")
REQUIRED_TOP = {"source": ["fetchedAt"], "window": ["to", "from30", "prevFrom", "prevTo"], "counts": ["d7", "d30", "prev30", "change", "medClose", "closed30"]}
REQUIRED_AREA = ["n", "name", "d7", "d30", "prev30", "change", "medClose", "closed30", "w12"]
CHI = dt.timezone(dt.timedelta(hours=-5))  # only used when an ISO time carries no offset


class DataError(Exception):
    pass


def load_config():
    return json.load(open(CONFIG, encoding="utf-8"))


def sha256_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def parse_time(s):
    s = s.strip()
    m = re.match(r"^(.*[T ]\d{2}:\d{2}(?::\d{2})?)([+-]\d{2})(\d{2})$", s)   # -0500 style offsets
    if m:
        s = f"{m.group(1)}{m.group(2)}:{m.group(3)}"
    t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    return t if t.tzinfo else t.replace(tzinfo=CHI)


def check_shape(d):
    """The input contract: a missing field or a changed shape stops the run with one line."""
    if not isinstance(d, dict):
        raise DataError("the rat file is not a JSON object")
    for k, fields in REQUIRED_TOP.items():
        if not isinstance(d.get(k), dict):
            raise DataError(f"the rat file has no {k} block")
        for f in fields:
            if f not in d[k]:
                raise DataError(f"the rat file lacks {k}.{f}")
    areas = d.get("areas")
    if not isinstance(areas, list) or len(areas) != 77:
        raise DataError(f"the rat file holds {len(areas) if isinstance(areas, list) else 'no'} areas, not 77")
    for a in areas:
        for f in REQUIRED_AREA:
            if f not in a:
                raise DataError(f"area {a.get('n', '?')} lacks {f}")
        if not isinstance(a["w12"], list) or len(a["w12"]) != 12:
            raise DataError(f"area {a['n']} w12 is not 12 weekly counts")
    if not isinstance(d.get("weeks"), list) or len(d["weeks"]) != 12:
        raise DataError("the rat file's weeks block is not 12 weeks")


def check_fresh(d, now, days):
    fetched = parse_time(d["source"]["fetchedAt"])
    age = (now - fetched).total_seconds() / 86400
    if age > days:
        raise DataError(f"stale: fetchedAt {d['source']['fetchedAt']} is {age:.1f} days old (the limit is {days}); no video today")
    if age < -0.01:
        raise DataError(f"fetchedAt {d['source']['fetchedAt']} is in the future against {now.isoformat()}")
    return round(age, 2)


def cap(x):
    return max(0.0, min(1.0, x))


def r4(x):
    return round(x + 0.0, 4)


def num(label, path, value):
    return {"label": label, "path": path, "value": value}


def recent_leads(ledger_rows, now, days):
    """(type, area) pairs that led a published video in the last `days` days, from the ledger's rows."""
    out = set()
    for r in ledger_rows:
        if r.get("state") != "published" or not r.get("storyType"):
            continue
        try:
            at = parse_time(r["at"])
        except (KeyError, ValueError):
            continue
        if 0 <= (now - at).total_seconds() <= days * 86400:
            out.add((r["storyType"], int(r.get("area", 0))))
    return out


def build(d, cfg, recent=frozenset()):
    """Every candidate in the week's file, scored, sorted best first (ties: larger d30, then the lower area number)."""
    w, floors, cands = cfg["weights"], cfg["floors"], []
    win = d["window"]
    period = f"30 days to {win['to']}"
    city = d["counts"]

    def add(type_, area, name, d30, numbers, surprise, local, work, proof, extra=None):
        parts = {"surprise": r4(cap(surprise)), "local": local, "work": work,
                 "novelty": 0 if (type_, area) in recent else 1, "proof": r4(cap(proof))}
        score = r4(sum(w[k] * parts[k] for k in w))
        c = {"id": f"{type_}-{area}" + (f"-{extra['side']}" if extra and extra.get("side") else ""), "type": type_,
             "typeName": TYPE_NAMES[type_], "area": area, "name": name, "d30": d30, "numbers": numbers, "parts": parts, "score": score}
        if extra:
            c.update(extra)
        cands.append(c)

    for a in d["areas"]:                                       # A: a neighborhood's jump
        p = f"areas[n={a['n']}]"
        if a["d30"] is None or a["d30"] < floors["A"] or a["change"] is None:
            continue
        add("A", a["n"], a["name"], a["d30"],
            [num(f"{a['name']} rat complaints, {period}", f"{p}.d30", a["d30"]),
             num(f"{a['name']}, same 30 days last year", f"{p}.prev30", a["prev30"]),
             num(f"{a['name']} change against last year (%)", f"{p}.change", a["change"])],
            abs(a["change"]) / 100, 1, 1, a["d30"] / 100)
    if city["change"] is not None:                             # B: the city against last year
        add("B", 0, "Chicago", city["d30"],
            [num(f"Chicago rat complaints, {period}", "counts.d30", city["d30"]),
             num("Chicago, same 30 days last year", "counts.prev30", city["prev30"]),
             num("Chicago change against last year (%)", "counts.change", city["change"])],
            abs(city["change"]) / 100, 0.5, 0.5, 1)
    med = city["medClose"]                                     # C: slowest and fastest response time
    pool = [a for a in d["areas"] if a["closed30"] is not None and a["closed30"] >= floors["C"] and a["medClose"] is not None]
    if med and pool:
        slow = max(pool, key=lambda a: (a["medClose"], -a["n"]))
        fast = min(pool, key=lambda a: (a["medClose"], a["n"]))
        for side, a in (("slow", slow), ("fast", fast)):
            p = f"areas[n={a['n']}]"
            add("C", a["n"], a["name"], a["d30"],
                [num(f"{a['name']} median days to close a rat complaint, {period}", f"{p}.medClose", a["medClose"]),
                 num(f"{a['name']} complaints closed, {period}", f"{p}.closed30", a["closed30"]),
                 num(f"Chicago median days to close, {period}", "counts.medClose", med)],
                abs(a["medClose"] - med) / med, 1, 0.5, a["closed30"] / 100, {"side": side})
    for a in d["areas"]:                                       # D: a run of rising weeks
        p, x = f"areas[n={a['n']}]", a["w12"]
        last = x[8:12]
        if any(v is None for v in last) or not (last[0] < last[1] < last[2] < last[3]):
            continue
        if a["d30"] is None or a["d30"] < floors["D"] or last[0] == 0:
            continue
        weeks = d["weeks"][8:12]
        add("D", a["n"], a["name"], a["d30"],
            [num(f"{a['name']} complaints, week of {weeks[i]['from']} to {weeks[i]['to']}", f"{p}.w12[{8 + i}]", last[i]) for i in range(4)]
            + [num(f"{a['name']} rat complaints, {period}", f"{p}.d30", a["d30"])],
            (last[3] - last[0]) / last[0], 1, 1, a["d30"] / 100)
    cands.sort(key=lambda c: (-c["score"], -(c["d30"] or 0), c["area"], c["id"]))
    for i, c in enumerate(cands, 1):
        c["rank"] = i
    return cands


def mvp_week(now, cfg):
    """(week index 0 to weeks-1, or None before or after the MVP) for a run time."""
    start = dt.date.fromisoformat(cfg["mvp"]["start"])
    day = now.astimezone(CHI).date() if now.tzinfo else now.date()
    k = (day - start).days // 7
    return k if 0 <= k < cfg["mvp"]["weeks"] else None


def done_types(plans):
    """How many slots each type already holds in earlier MVP weeks' plans."""
    out = {t: 0 for t in TYPES}
    for p in plans:
        for s in p.get("slots", []):
            out[s["type"]] = out.get(s["type"], 0) + 1
    return out


def plan_week(cands, cfg, week=None, earlier=()):
    """Three slots, three different types and pictures. Over the MVP every type runs at least twice: a type set is
    allowed only when the weeks left can still give each type its second run."""
    best = {}
    for c in cands:
        best.setdefault(c["type"], c)
    have = [t for t in TYPES if t in best]
    weeks = cfg["mvp"]["weeks"]
    done = done_types(earlier)
    left = (weeks - week) if week is not None else None
    sets, note = [], ""
    for combo in itertools.combinations(have, 3):
        if left is not None:
            ok = all(max(0, 2 - done[t] - (t in combo)) <= left - 1 for t in TYPES)
            if not ok:
                continue
        sets.append(combo)
    if not sets:
        sets = list(itertools.combinations(have, min(3, len(have))))
        note = (f"plan constraint unmet: types with a candidate this week are {have}; every type twice over "
                f"{weeks} weeks can't hold (tell Todd)") if have else "no candidate this week"
    if not sets:
        return {"slots": [], "note": note}
    combo = max(sets, key=lambda s: (round(sum(best[t]["score"] for t in s), 4), tuple(-ord(t) for t in s)))
    chosen = sorted((best[t] for t in combo), key=lambda c: (-c["score"], -(c["d30"] or 0), c["area"]))
    aff = cfg["affinity"]
    pics = cfg["pictures"]
    best_assign, best_val = None, -1
    for perm in itertools.permutations(pics, len(chosen)):
        if any(perm[i] not in aff[chosen[i]["type"]] for i in range(len(chosen))):
            continue
        val = sum(aff[chosen[i]["type"]][perm[i]] for i in range(len(chosen)))
        if val > best_val:
            best_assign, best_val = perm, val
    if best_assign is None:
        raise DataError("no picture assignment fits the chosen types")
    slots = [{"slot": SLOTS[i], "candidate": chosen[i]["id"], "type": chosen[i]["type"], "area": chosen[i]["area"],
              "name": chosen[i]["name"], "picture": best_assign[i], "score": chosen[i]["score"]} for i in range(len(chosen))]
    return {"week": week, "slots": slots, "note": note}


def git(*args):
    try:
        return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        return ""


def data_commit(path):
    """The commit whose tree holds this exact file (HEAD, when the working copy matches it)."""
    rel = os.path.relpath(os.path.abspath(path), ROOT)
    head = git("rev-parse", "HEAD")
    blob = git("rev-parse", f"HEAD:{rel}")
    work = git("hash-object", rel)
    return head if head and blob and blob == work else "uncommitted"


def read_ledger_rows(path):
    if not path or not os.path.exists(path):
        return []
    sys.path.insert(0, HERE)
    import video_ledger
    return video_ledger.read(path)["rows"]


def plans_before(cfg, week, cand_dir):
    """Earlier MVP weeks' plans from saved candidates files (video/candidates/*.json)."""
    out = []
    if week is None or not os.path.isdir(cand_dir):
        return out
    for f in sorted(os.listdir(cand_dir)):
        if not f.endswith(".json"):
            continue
        try:
            c = json.load(open(os.path.join(cand_dir, f), encoding="utf-8"))
        except ValueError:
            continue
        p = c.get("plan") or {}
        if p.get("week") is not None and p["week"] < week:
            out.append(p)
    return out


def candidates_doc(data_path, now, ledger_rows=(), cfg=None, earlier=None, cand_dir=None):
    cfg = cfg or load_config()
    d = json.load(open(data_path, encoding="utf-8"))
    check_shape(d)
    age = check_fresh(d, now, cfg["freshDays"])
    recent = recent_leads(ledger_rows, now, cfg["noveltyDays"])
    cands = build(d, cfg, recent)
    week = mvp_week(now, cfg)
    if earlier is None:
        earlier = plans_before(cfg, week, cand_dir or os.path.join(ROOT, "video", "candidates"))
    plan = plan_week(cands, cfg, week, earlier)
    return {"schema": "pnf.video.candidates.v1", "videoId": None, "dataFile": os.path.relpath(os.path.abspath(data_path), ROOT),
            "dataCommit": data_commit(data_path), "dataSha256": sha256_file(data_path),
            "fetchedAt": d["source"]["fetchedAt"], "windowTo": d["window"]["to"], "ageDays": age,
            "generatedAt": now.isoformat(timespec="seconds"), "weights": cfg["weights"], "floors": cfg["floors"],
            "candidates": cands, "plan": plan, "chosen": plan["slots"][0]["candidate"] if plan["slots"] else None}


def cand_path(doc):
    return os.path.join(ROOT, "video", "candidates", f"{doc['windowTo']}.json")


def reuse_or_write(doc, out=None):
    """A rerun on the same file picks the same story: an existing candidates file for the same data fingerprint wins."""
    path = out or cand_path(doc)
    if os.path.exists(path):
        old = json.load(open(path, encoding="utf-8"))
        if old.get("dataSha256") == doc["dataSha256"]:
            return old, path, False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    return doc, path, True


def slot_pick(doc, slot):
    for s in doc["plan"]["slots"]:
        if s["slot"] == slot:
            c = next(c for c in doc["candidates"] if c["id"] == s["candidate"])
            return dict(c, slot=slot, picture=s["picture"])
    return None


# ---------------------------------------------------------------------------------------------------------------------
# The spec skeleton: the evidence bundle and every on-screen number, written by code so the scriptwriter never types a
# figure. The scriptwriter adds hooks, lines and captions (words only); spec_lint and the facts gate check the rest.

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def short_date(iso):
    y, m, d = iso.split("-")
    return f"{MONTHS[int(m) - 1]} {int(d)}"


def pct(v):
    """The file's own rounding: one decimal, shown without a trailing .0 (40.0 is 40%)."""
    s = f"{abs(v):.1f}".rstrip("0").rstrip(".")
    return f"{s}%"


def days(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return s


def comma(v):
    return f"{v:,}"


def draft(doc, slot, video_id, data_path):
    """A spec skeleton for one slot: evidence (file, commit, sha256, numbers with label, path and value), the picture's
    data and the on-screen figures, all from the file."""
    d = json.load(open(data_path, encoding="utf-8"))
    pick = slot_pick(doc, slot)
    if not pick:
        raise DataError(f"no {slot} slot in the plan")
    win, city = d["window"], d["counts"]
    to = short_date(win["to"])
    by_n = {a["n"]: a for a in d["areas"]}
    nums = []

    def ev(id_, label, path, value, shown):
        nums.append({"id": id_, "label": label, "path": path, "value": value, "shown": shown})

    ev("windowTo", "Last whole day counted", "window.to", win["to"], [to])
    ev("line311", "The City's service line the complaints go to (311 Service Requests)", "source.name", d["source"]["name"], ["311"])
    t, a = pick["type"], by_n.get(pick["area"])
    p = f"areas[n={pick['area']}]"
    screen = {"eyebrow": "CHICAGO RAT CHECK", "period": f"30 days to {to}", "picture": pick["picture"]}
    if t == "A":
        up = a["change"] >= 0
        ev("d30", f"{a['name']} rat complaints, 30 days to {to}", f"{p}.d30", a["d30"], [comma(a["d30"])])
        ev("prev30", f"{a['name']}, same 30 days last year", f"{p}.prev30", a["prev30"], [comma(a["prev30"])])
        ev("change", f"{a['name']} change against last year", f"{p}.change", a["change"], [pct(a["change"])])
        ev("cityChange", "Chicago change against last year", "counts.change", city["change"], [pct(city["change"])])
        screen.update({"area": a["name"], "headline": {"number": ("+" if up else "-") + pct(a["change"]), "numberId": "change",
                       "label": f"rat complaints in {a['name']} vs. the same 30 days last year"}})
    elif t == "B":
        up = city["change"] >= 0
        ev("d30", f"Chicago rat complaints, 30 days to {to}", "counts.d30", city["d30"], [comma(city["d30"])])
        ev("prev30", "Chicago, same 30 days last year", "counts.prev30", city["prev30"], [comma(city["prev30"])])
        ev("change", "Chicago change against last year", "counts.change", city["change"], [pct(city["change"])])
        screen.update({"area": "Chicago", "headline": {"number": ("+" if up else "-") + pct(city["change"]), "numberId": "change",
                       "label": "rat complaints citywide vs. the same 30 days last year"}})
    elif t == "C":
        ev("medClose", f"{a['name']} median days to close a rat complaint", f"{p}.medClose", a["medClose"], [days(a["medClose"])])
        ev("closed30", f"{a['name']} complaints closed, 30 days to {to}", f"{p}.closed30", a["closed30"], [comma(a["closed30"])])
        ev("cityMedClose", "Chicago median days to close", "counts.medClose", city["medClose"], [days(city["medClose"])])
        word = "slowest" if pick.get("side") == "slow" else "fastest"
        screen.update({"area": a["name"], "side": pick.get("side"), "headline": {"number": days(a["medClose"]), "numberId": "medClose",
                       "unit": "days", "label": f"median wait to close a rat complaint in {a['name']}, the city's {word}"}})
    elif t == "D":
        w4 = a["w12"][8:12]
        wk = d["weeks"][8:12]
        for i in range(4):
            ev(f"w{i + 1}", f"{a['name']} complaints, week ending {short_date(wk[i]['to'])}", f"{p}.w12[{8 + i}]", w4[i], [comma(w4[i])])
        rise = round((w4[3] - w4[0]) / w4[0] * 100, 1)
        ev("rise", f"{a['name']} rise from the first to the fourth of the last 4 weeks (%, computed from w12[8] and w12[11])",
           f"({p}.w12[11]-{p}.w12[8])/{p}.w12[8]*100", rise, [pct(rise)])
        ev("d30", f"{a['name']} rat complaints, 30 days to {to}", f"{p}.d30", a["d30"], [comma(a["d30"])])
        ev("risesInARow", "Weeks in a row with more complaints than the week before (w12[9] to w12[11])", f"{p}.w12[8:12] rising", 3, ["3"])
        ev("w1To", "Last day of the first of the last 4 weeks", "weeks[8].to", wk[0]["to"], [short_date(wk[0]["to"])])
        screen.update({"area": a["name"], "headline": {"number": "+" + pct(rise), "numberId": "rise",
                       "label": f"more rat complaints a week in {a['name']} than 3 weeks ago, up every week since"}})
    screen["chart"] = chart_data(d, pick, ev)
    screen["chart"]["focusLabel"] = {"A": "vs. the same 30 days last year", "B": "citywide vs. last year",
                                     "C": "median days to close", "D": f"week to {to} vs. week to {short_date(d['weeks'][8]['to'])}"}[t]
    screen["compare"] = compare_data(d, pick, to)
    ev("windowDays", "Days in the window (window.from30 to window.to)", "window.from30..window.to", 30, ["30"])
    ev("areasTotal", "Chicago community areas", "len(areas)", len(d["areas"]), [str(len(d["areas"]))]) if not any(x["id"] == "areasTotal" for x in nums) else None
    return {"schema": "pnf.video.spec.v1", "videoId": video_id, "template": "rat-check", "storyType": t, "picture": pick["picture"],
            "slot": slot,
            "candidate": {k: pick[k] for k in ("id", "type", "area", "name", "parts", "score", "rank")},
            "evidence": {"file": doc["dataFile"], "commit": doc["dataCommit"], "sha256": doc["dataSha256"],
                         "fetchedAt": doc["fetchedAt"], "candidates": os.path.relpath(cand_path(doc), ROOT), "numbers": nums},
            "screen": screen, "hooks": [], "hook": None, "lines": [], "cta": {"say": load_config()["cta"]["say"]},
            "endCard": {"line": "See your neighborhood free", "path": load_config()["cta"]["path"]},
            "captions": {"instagram": ""}, "voice": {"model": load_config()["voice"]["model"], "voiceIds": []},
            "music": load_config()["music"]["id"], "gates": {}}


def compare_data(d, pick, to):
    """The two cards of the compare scene, both numbers already in the evidence."""
    t, n = pick["type"], pick["area"]
    a = next((x for x in d["areas"] if x["n"] == n), None)
    c = d["counts"]
    if t in ("A", "B"):
        src = a if t == "A" else c
        return {"unit": "complaints", "cards": [{"label": "Same 30 days last year", "value": src["prev30"], "shown": comma(src["prev30"]), "numberId": "prev30"},
                                                 {"label": f"30 days to {to}", "value": src["d30"], "shown": comma(src["d30"]), "numberId": "d30", "focus": True}]}
    if t == "C":
        return {"unit": "days", "cards": [{"label": a["name"], "value": a["medClose"], "shown": days(a["medClose"]), "numberId": "medClose", "focus": True},
                                           {"label": "All of Chicago", "value": c["medClose"], "shown": days(c["medClose"]), "numberId": "cityMedClose"}]}
    wk = d["weeks"]
    return {"unit": "complaints", "cards": [{"label": f"Week to {short_date(wk[8]['to'])}", "value": a["w12"][8], "shown": comma(a["w12"][8]), "numberId": "w1"},
                                             {"label": f"Week to {short_date(wk[11]['to'])}", "value": a["w12"][11], "shown": comma(a["w12"][11]), "numberId": "w4", "focus": True}]}


def chart_data(d, pick, ev):
    """What the picture draws, every value from the file (the map's classes and the bars' and line's numbers)."""
    t, pic, n = pick["type"], pick["picture"], pick["area"]
    by_n = {a["n"]: a for a in d["areas"]}
    if pic == "map":
        if t == "C":
            cm = d["counts"]["medClose"]
            areas = [{"n": a["n"], "cls": "focus" if a["n"] == n else ("hi" if (a["medClose"] or 0) > cm else "lo")} for a in d["areas"]]
            return {"kind": "map", "legend": [["hi", "Slower than the city"], ["lo", "Faster or same"]], "areas": areas, "focus": n}
        if t == "D":
            rising = {a["n"] for a in d["areas"] if a["w12"][8] < a["w12"][9] < a["w12"][10] < a["w12"][11]}
            areas = [{"n": a["n"], "cls": "focus" if a["n"] == n else ("hi" if a["n"] in rising else "lo")} for a in d["areas"]]
            return {"kind": "map", "legend": [["hi", "Rising 4 weeks"], ["lo", "Not rising"]], "areas": areas, "focus": n}
        areas = [{"n": a["n"], "cls": "focus" if a["n"] == n else ("hi" if (a["change"] or 0) > 0 else "lo")} for a in d["areas"]]
        up = sum(1 for a in d["areas"] if (a["change"] or 0) > 0)
        ev("areasUp", "Community areas with more complaints than the same 30 days last year", "count(areas[].change > 0)", up, [str(up)])
        ev("areasTotal", "Chicago community areas", "len(areas)", len(d["areas"]), [str(len(d["areas"]))])
        return {"kind": "map", "legend": [["hi", "Up vs. last year"], ["lo", "Down or flat"]], "areas": areas, "focus": n or None}
    if pic == "bars":
        if t == "C":
            pool = sorted([a for a in d["areas"] if a["closed30"] is not None and a["closed30"] >= load_config()["floors"]["C"] and a["medClose"] is not None],
                          key=lambda a: (-a["medClose"], a["n"]) if pick.get("side") == "slow" else (a["medClose"], a["n"]))[:5]
            rows = []
            for a in pool:
                ev(f"bar{a['n']}", f"{a['name']} median days to close", f"areas[n={a['n']}].medClose", a["medClose"], [days(a["medClose"])])
                rows.append({"label": a["name"], "value": a["medClose"], "shown": days(a["medClose"]), "focus": a["n"] == n})
            return {"kind": "bars", "unit": "days", "rows": rows}
        if t == "D":
            a = by_n[n]
            wk = d["weeks"][8:12]
            rows = [{"label": f"Week to {short_date(wk[i]['to'])}", "value": a["w12"][8 + i], "shown": comma(a["w12"][8 + i]), "focus": i == 3} for i in range(4)]
            return {"kind": "bars", "unit": "complaints", "rows": rows}
        key = "change"
        pool = [a for a in d["areas"] if a["d30"] >= load_config()["floors"]["A"] and a["change"] is not None]
        top = sorted(pool, key=lambda a: (-a[key], a["n"]))[:5]
        if n and n not in [a["n"] for a in top]:
            top = top[:4] + [by_n[n]]
        rows = []
        for a in top:
            ev(f"bar{a['n']}", f"{a['name']} change against last year", f"areas[n={a['n']}].change", a["change"], [pct(a["change"])])
            rows.append({"label": a["name"], "value": a["change"], "shown": ("+" if a["change"] >= 0 else "-") + pct(a["change"]), "focus": a["n"] == n})
        return {"kind": "bars", "unit": "%", "rows": rows}
    if pic == "line":
        if n:
            a = by_n[n]
            pts = [{"x": d["weeks"][i]["to"], "y": a["w12"][i]} for i in range(12)]
            ev("lineFirst", f"{a['name']} complaints, week ending {short_date(d['weeks'][0]['to'])}", f"areas[n={n}].w12[0]", a["w12"][0], [comma(a["w12"][0])])
            ev("lineLast", f"{a['name']} complaints, week ending {short_date(d['weeks'][11]['to'])}", f"areas[n={n}].w12[11]", a["w12"][11], [comma(a["w12"][11])])
        else:
            pts = [{"x": w["to"], "y": w["count"]} for w in d["weeks"]]
            ev("lineFirst", f"Chicago complaints, week ending {short_date(d['weeks'][0]['to'])}", "weeks[0].count", d["weeks"][0]["count"], [comma(d["weeks"][0]["count"])])
            ev("lineLast", f"Chicago complaints, week ending {short_date(d['weeks'][11]['to'])}", "weeks[11].count", d["weeks"][11]["count"], [comma(d["weeks"][11]["count"])])
        ev("lineFrom", "First week shown ends", "weeks[0].to", d["weeks"][0]["to"], [short_date(d["weeks"][0]["to"])])
        return {"kind": "line", "points": pts, "firstShown": comma(pts[0]["y"]), "lastShown": comma(pts[-1]["y"]),
                "fromShown": short_date(d["weeks"][0]["to"]), "toShown": short_date(d["weeks"][11]["to"]), "highlightLast": 4 if pick["type"] == "D" else 0}
    raise DataError(f"unknown picture {pic}")


# ---------------------------------------------------------------------------------------------------------------------

def selftest():
    cfg = load_config()
    fx = os.path.join(ROOT, "video", "fixtures")
    problems = []
    now = parse_time("2026-10-28T08:00:00-05:00")

    def expect(name, ok, detail=""):
        if not ok:
            problems.append(f"{name}{': ' + detail if detail else ''}")

    normal = candidates_doc(os.path.join(fx, "normal.json"), now, earlier=[], cfg=cfg)
    exp = json.load(open(os.path.join(fx, "expected.json"), encoding="utf-8"))
    top = normal["candidates"][0]
    expect("normal: picks the planted story", top["id"] == exp["normal"]["top"], f"got {top['id']}")
    expect("normal: three slots, three types", len({s["type"] for s in normal["plan"]["slots"]}) == 3, str(normal["plan"]))
    expect("normal: three pictures", len({s["picture"] for s in normal["plan"]["slots"]}) == 3, str(normal["plan"]))
    expect("normal: scores in 0 to 1", all(0 <= c["score"] <= 1 for c in normal["candidates"]))
    again = candidates_doc(os.path.join(fx, "normal.json"), now, earlier=[], cfg=cfg)
    expect("normal: a rerun picks the same plan", again["plan"] == normal["plan"] and again["chosen"] == normal["chosen"])
    tiny = candidates_doc(os.path.join(fx, "tiny-base.json"), now, earlier=[], cfg=cfg)
    ids = {c["id"] for c in tiny["candidates"]}
    for bad in exp["tiny"]["skipped"]:
        expect(f"tiny base: {bad} is skipped", bad not in ids)
    expect("tiny base: the real story still wins", tiny["candidates"][0]["id"] == exp["tiny"]["top"], tiny["candidates"][0]["id"])
    try:
        candidates_doc(os.path.join(fx, "stale.json"), now, earlier=[], cfg=cfg)
        expect("stale: refused", False, "a stale file produced candidates")
    except DataError as e:
        expect("stale: refused", "stale" in str(e), str(e))
    broken = json.load(open(os.path.join(fx, "normal.json"), encoding="utf-8"))
    del broken["areas"][3]["medClose"]
    try:
        check_shape(broken)
        expect("shape: a missing field stops the run", False)
    except DataError:
        pass
    pub = [{"videoId": "x", "state": "published", "storyType": top["type"], "area": top["area"], "at": "2026-10-25T09:00:00-05:00"}]
    nov = candidates_doc(os.path.join(fx, "normal.json"), now, ledger_rows=pub, earlier=[], cfg=cfg)
    t2 = next(c for c in nov["candidates"] if c["id"] == top["id"])
    expect("novelty: a story led 3 days ago scores novelty 0", t2["parts"]["novelty"] == 0)
    old = [dict(pub[0], at="2026-10-01T09:00:00-05:00")]
    t3 = next(c for c in candidates_doc(os.path.join(fx, "normal.json"), now, ledger_rows=old, earlier=[], cfg=cfg)["candidates"] if c["id"] == top["id"])
    expect("novelty: a story led 27 days ago is new again", t3["parts"]["novelty"] == 1)
    # Ties: same score, larger d30 wins, then the lower area number.
    tie = json.load(open(os.path.join(fx, "normal.json"), encoding="utf-8"))
    for a in tie["areas"]:
        a.update({"d30": 10, "change": None, "w12": [5] * 12, "closed30": 5, "medClose": None})
    tie["areas"][9].update({"d30": 150, "prev30": 100, "change": 50.0})
    tie["areas"][4].update({"d30": 150, "prev30": 100, "change": 50.0})
    tie["areas"][2].update({"d30": 120, "prev30": 80, "change": 50.0})
    c = build(tie, cfg)
    order = [x["id"] for x in c if x["type"] == "A"]
    expect("ties: larger d30 first, then the lower area number", order[:3] == ["A-5", "A-10", "A-3"], str(order[:3]))
    # Three weeks: every type runs at least twice.
    earlier = []
    week_types = []
    for k in range(3):
        p = plan_week(normal["candidates"], cfg, k, earlier)
        week_types.append([s["type"] for s in p["slots"]])
        earlier.append(p)
    counts = {t: sum(w.count(t) for w in week_types) for t in TYPES}
    expect("three weeks: every type at least twice", all(v >= 2 for v in counts.values()), str(week_types))
    # The spec skeleton: every number has a path and its value matches the file.
    d = json.load(open(os.path.join(fx, "normal.json"), encoding="utf-8"))
    for slot in SLOTS:
        sk = draft(normal, slot, f"2026-10-28-rats-{slot.lower()}", os.path.join(fx, "normal.json"))
        for x in sk["evidence"]["numbers"]:
            got = resolve(d, x["path"])
            if got is not None and got != x["value"]:
                problems.append(f"draft {slot}: {x['id']} value {x['value']} but {x['path']} is {got}")
    for p in problems:
        print("FAIL", p)
    print(f"video_story selftest: {'ok' if not problems else str(len(problems)) + ' failed'} (planted story, tiny base, stale file, "
          "missing field, novelty, ties, three-week plan, evidence paths)")
    return 1 if problems else 0


def resolve(d, path):
    """The value at an evidence path like areas[n=6].w12[11] or counts.change (None for computed paths)."""
    if not re.fullmatch(r"[A-Za-z0-9_.\[\]=]+", path):
        return None
    cur = d
    for part in re.findall(r"[A-Za-z0-9_]+(?:\[[^\]]+\])*", path):
        m = re.match(r"([A-Za-z0-9_]+)((?:\[[^\]]+\])*)$", part)
        cur = cur.get(m.group(1)) if isinstance(cur, dict) else None
        for idx in re.findall(r"\[([^\]]+)\]", m.group(2)):
            if cur is None:
                return None
            if "=" in idx:
                k, v = idx.split("=")
                cur = next((x for x in cur if str(x.get(k)) == v), None)
            else:
                i = int(idx)
                cur = cur[i] if isinstance(cur, list) and -len(cur) <= i < len(cur) else None
    return cur


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", nargs="?", choices=["candidates", "pick", "draft"])
    ap.add_argument("--data", default=None)
    ap.add_argument("--now", default=None, help="ISO time (default: now, Chicago)")
    ap.add_argument("--ledger", default=os.path.join(ROOT, "video", "LEDGER.md"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--slot", choices=SLOTS)
    ap.add_argument("--video-id")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    cfg = load_config()
    data = a.data or os.path.join(ROOT, cfg["data"])
    now = parse_time(a.now) if a.now else dt.datetime.now(dt.timezone.utc)
    try:
        doc = candidates_doc(data, now, read_ledger_rows(a.ledger), cfg)
        if a.cmd == "candidates":
            doc, path, wrote = reuse_or_write(doc, a.out)
            print(f"{'wrote' if wrote else 'kept'} {os.path.relpath(path, ROOT)}: {len(doc['candidates'])} candidates, plan "
                  + ", ".join(f"{s['slot']} {s['type']} {s['name']} ({s['picture']}, {s['score']})" for s in doc["plan"]["slots"])
                  + (f"; {doc['plan']['note']}" if doc["plan"].get("note") else ""))
        elif a.cmd == "pick":
            doc, _, _ = reuse_or_write(doc)
            print(json.dumps(slot_pick(doc, a.slot), indent=1))
        elif a.cmd == "draft":
            doc, _, _ = reuse_or_write(doc)
            sk = draft(doc, a.slot, a.video_id, data)
            out = a.out or os.path.join(ROOT, "video", "specs", f"{a.video_id}.json")
            open(out, "w", encoding="utf-8").write(json.dumps(sk, indent=1, ensure_ascii=False) + "\n")
            print(f"wrote {os.path.relpath(out, ROOT)}")
        else:
            ap.print_help()
    except DataError as e:
        print(f"ERROR video-story: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
