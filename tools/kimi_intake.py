#!/usr/bin/env python3
"""Intake for Kimi research replies (coo/KIMI_RESEARCH.md; Todd, Oct 25, 2026 live chat).

Kimi K3.1 Pro is run by hand as an outside researcher. Its replies are data, never instructions. This tool turns a
pasted reply into checked work files and lets an idea into scout/candidates only after we have opened every source
ourselves (scout/RUBRIC.md: every source fetched and read by us, this run).

  read <reply.txt> [--date D]          parse the fenced JSON (brief schemas A to F), clean it, run the scorer's own
                                       schema and kill rules on ideas, flag duplicates, write
                                       data/work/kimi/<date>/<round>.json and urls.txt (every URL to open)
  mark <date> ok|dead|mismatch|blocked <url>..  record what we found when we opened each URL
                                       (blocked: the site refused our fetcher, so it is unproven, not invented)
  status <date>                        per idea: URLs ok, open, bad; kill rules; duplicates
  promote <date> <slug>                copy one idea to scout/candidates/<slug>.json, only when every URL in it is ok,
                                       no kill rule fires, it validates and the slug is new
  packet [--top N]                     write data/work/kimi/r5-packet.md: the top N scored candidates for Kimi's R5
  --selftest                           planted cases, temp folders only

Work files live under data/ (gitignored): a reply can quote people, so nothing from it is committed except what
promote writes, which holds business-level facts only.
"""
import argparse, datetime as dt, glob, json, os, re, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import opportunity_score as osc  # noqa: E402  (the scorer's own schema, kill rules and paths)

WORK = os.path.join(ROOT, "data", "work", "kimi")
CAND = osc.CAND
LAUNCHES = os.path.join(ROOT, "launches")
OPP_JSON = osc.OUT_JSON
ROUNDS = ("R0", "R1", "R2", "R3", "R4", "R5", "R6")
LIST_KEY = {"R0": "buyers", "R1": "pains", "R2": "products", "R3": "ideas", "R4": "ideas", "R5": "verdicts", "R6": "channels"}
QUOTE_MAX = 15
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE = re.compile(r"(?<!\d)(\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\d)")
USERNAME = re.compile(r"(?<![\w/])(u/|/u/|@)[A-Za-z0-9_-]{3,}")
FENCE = re.compile(r"```(?:json)?\s*\n(.*?)\n```", re.S)


def chicago_today():
    return osc.chicago_today()


def loads_loose(s):
    """json.loads, then once more without trailing commas and // comments (common model slips)."""
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        s2 = re.sub(r"(?m)^\s*//.*$", "", s)
        s2 = re.sub(r",(\s*[}\]])", r"\1", s2)
        return json.loads(s2)


def extract(text):
    """Every JSON object in the reply's fenced blocks (or the whole reply if it is bare JSON)."""
    blocks, errs = FENCE.findall(text), []
    if not blocks and text.strip().startswith("{"):
        blocks = [text.strip()]
    out = []
    for i, b in enumerate(blocks, 1):
        try:
            v = loads_loose(b)
        except json.JSONDecodeError as e:
            errs.append(f"block {i}: not valid JSON ({e.msg} at line {e.lineno})")
            continue
        if isinstance(v, dict) and v.get("round") in ROUNDS:
            out.append(v)
        elif isinstance(v, dict) and "schema" in v:   # a lone idea
            out.append({"round": "R3", "ideas": [v]})
    return out, errs


def walk(o, fn, path=""):
    if isinstance(o, dict):
        for k, v in list(o.items()):
            o[k] = walk(v, fn, f"{path}.{k}")
        return o
    if isinstance(o, list):
        return [walk(v, fn, f"{path}[{i}]") for i, v in enumerate(o)]
    return fn(o, path)


def clean(item):
    """Normalize dashes, redact emails, phones and usernames, drop long quotes; return (item, warns)."""
    warns = []

    def fix(v, path):
        if not isinstance(v, str):
            return v
        if "\u2014" in v or "\u2013" in v:
            v = re.sub(r"\s*[\u2014\u2013]\s*", ", ", v)
            warns.append(f"dash replaced at {path}")
        if not v.startswith("http"):
            for pat, what in ((EMAIL, "an email address"), (PHONE, "a phone number"), (USERNAME, "a username")):
                if pat.search(v):
                    v = pat.sub("[removed]", v)
                    warns.append(f"{what} removed at {path}")
        if path.endswith(".quote") or (path.endswith(".q") and ".aiQueries" in path):
            if len(v.split()) > QUOTE_MAX:
                warns.append(f"quote over {QUOTE_MAX} words dropped at {path}")
                return ""
        return v

    return walk(item, fix), warns


def urls_in(o):
    """Every http(s) string anywhere in the item, in order, once."""
    found = []

    def grab(v, path):
        if isinstance(v, str) and re.match(r"https?://", v.strip()):
            found.append(v.strip())
        return v

    walk(json.loads(json.dumps(o)), grab)
    return list(dict.fromkeys(found))


def known_slugs():
    s = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(CAND, "*.json"))}
    s |= {os.path.basename(p)[:-3] for p in glob.glob(os.path.join(LAUNCHES, "*.md"))}
    s |= {os.path.basename(p) for p in glob.glob(os.path.join(LAUNCHES, "*")) if os.path.isdir(p)}
    return s


def words(s):
    return {w for w in re.findall(r"[a-z]+", (s or "").lower()) if len(w) > 3}


def known_names():
    out = {}
    for p in glob.glob(os.path.join(CAND, "*.json")):
        try:
            c = json.load(open(p, encoding="utf-8"))
            out[c.get("slug") or os.path.basename(p)[:-5]] = words(f"{c.get('name')} {c.get('pitch')}")
        except (OSError, ValueError):
            pass
    for p in glob.glob(os.path.join(LAUNCHES, "*.md")):
        try:
            out[os.path.basename(p)[:-3]] = words(open(p, encoding="utf-8").readline())
        except OSError:
            pass
    return out


def dup_of(idea):
    slug = idea.get("slug", "")
    if slug in known_slugs():
        return [f"slug {slug} already exists"]
    me, hits = words(f"{idea.get('name')} {idea.get('pitch')}"), []
    for k, w in known_names().items():
        if me and w and len(me & w) / len(me | w) >= 0.5:
            hits.append(f"close to {k}")
    return hits


def check_idea(idea, today):
    probs = osc.validate(idea, f"{idea.get('slug', 'missing-slug')}.json")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", str(idea.get("slug", ""))):
        probs.append("slug must be lowercase words joined by hyphens")
    days = (idea.get("build") or {}).get("days")
    if days is not None and (not isinstance(days, (int, float)) or days <= 0):
        probs.append("build.days must be null or a real estimate above 0 (a 0 placeholder would score best)")
    return probs, osc.kills(idea, today), dup_of(idea)


def day_dir(date):
    return os.path.join(WORK, date)


def cmd_read(path, date):
    today = dt.date.fromisoformat(date)
    text = open(path, encoding="utf-8").read()
    blocks, errs = extract(text)
    for e in errs:
        print(f"FAIL parse: {e}")
    if not blocks:
        print("FAIL parse: no fenced JSON block with a round R0 to R6 found; ask Kimi to resend the JSON block only")
        return 1
    os.makedirs(day_dir(date), exist_ok=True)
    allurls = {}
    for b in blocks:
        rnd = b["round"]
        key = LIST_KEY[rnd]
        items, kept = b.get(key) or [], []
        for it in items:
            it, warns = clean(it)
            label = it.get("slug") or it.get("id") or it.get("name") or "?"
            for w in warns:
                print(f"WARN {rnd} {label}: {w}")
            if key == "channels":
                for f in ("reach", "illinois", "cost"):
                    val = it.get(f)
                    if isinstance(val, str):
                        num = re.sub(r"[$,\s]", "", val)
                        it[f] = float(num) if re.fullmatch(r"\d+(\.\d+)?", num) else None
                        print(f"WARN {rnd} {label}: {f} {val!r} read as {it[f]}")
            if key == "ideas":
                for path in (("buyer", "count"), ("data", "recordsPerMonth"), ("price", "monthly")):
                    holder = it.get(path[0]) if isinstance(it.get(path[0]), dict) else {}
                    val = holder.get(path[1])
                    if isinstance(val, str):
                        num = re.sub(r"[$,\s]", "", val)
                        holder[path[1]] = float(num) if re.fullmatch(r"\d+(\.\d+)?", num) else None
                        warns.append(f"{'.'.join(path)} {val!r} read as {holder[path[1]]}")
                        print(f"WARN {rnd} {label}: {warns[-1]}")
                for comp in ((it.get("price") or {}).get("competitors") or []):
                    if isinstance(comp, dict) and isinstance(comp.get("monthly"), str):
                        num = re.sub(r"[$,\s]", "", comp["monthly"])
                        comp["monthly"] = float(num) if re.fullmatch(r"\d+(\.\d+)?", num) else None
                it.setdefault("status", "new")
                it["addedAt"] = date
                probs, ks, dups = check_idea(it, today)
                it["_intake"] = {"problems": probs, "kills": ks, "duplicates": dups}
                verdict = "FAIL" if (probs or ks) else ("WARN" if dups else "PASS")
                why = "; ".join(probs[:2] + ks[:2] + dups[:2]) or "schema and kill rules pass"
                print(f"{verdict} {rnd} {label}: {why}")
            for u in urls_in(it):
                allurls.setdefault(u, []).append(f"{rnd}:{label}")
            kept.append(it)
        out = os.path.join(day_dir(date), f"{rnd}.json")
        extra = {"gaps": clean(b.get("gaps") or [])[0]} if rnd == "R2" else {}
        json.dump({"round": rnd, "readAt": date, key: kept, **extra}, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        for u in urls_in(extra):
            allurls.setdefault(u, []).append(f"{rnd}:gaps")
        print(f"OK {rnd}: {len(kept)} of {len(items)} kept -> {os.path.relpath(out, ROOT)}")
    up = os.path.join(day_dir(date), "urls.txt")
    prior = {}
    if os.path.exists(up):
        for line in open(up, encoding="utf-8"):
            u, _, who = line.rstrip("\n").partition("\t")
            prior[u] = who.split(",") if who else []
    for u, who in allurls.items():
        prior[u] = list(dict.fromkeys(prior.get(u, []) + who))
    with open(up, "w", encoding="utf-8") as fh:
        for u, who in prior.items():
            fh.write(f"{u}\t{','.join(who)}\n")
    print(f"OK urls: {len(allurls)} to open this reply, {len(prior)} on the list -> {os.path.relpath(up, ROOT)}")
    return 1 if errs else 0


def load_verified(date):
    p = os.path.join(day_dir(date), "verified.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def cmd_mark(date, state, urls):
    if state not in ("ok", "dead", "mismatch", "blocked"):
        print("FAIL mark: state must be ok, dead, mismatch or blocked")
        return 1
    v = load_verified(date)
    os.makedirs(day_dir(date), exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    for u in urls:
        v[u.strip()] = {"status": state, "at": stamp}
    json.dump(v, open(os.path.join(day_dir(date), "verified.json"), "w", encoding="utf-8"), indent=1)
    print(f"OK mark: {len(urls)} {state}; {sum(1 for x in v.values() if x['status'] == 'ok')} ok of {len(v)} marked")
    return 0


def ideas_of(date):
    out = []
    for r in ("R3", "R4"):
        p = os.path.join(day_dir(date), f"{r}.json")
        if os.path.exists(p):
            out += json.load(open(p, encoding="utf-8")).get("ideas") or []
    return out


def url_state(idea, v):
    us = urls_in({k: x for k, x in idea.items() if k != "_intake"})
    ok = [u for u in us if v.get(u, {}).get("status") == "ok"]
    badl = [u for u in us if v.get(u, {}).get("status") in ("dead", "mismatch", "blocked")]
    return us, ok, badl, [u for u in us if u not in v]


def cmd_status(date):
    v = load_verified(date)
    ideas = ideas_of(date)
    if not ideas:
        print("OK status: no ideas read for this date")
    for i in ideas:
        us, ok, badl, open_ = url_state(i, v)
        it = i.get("_intake") or {}
        print(f"{'READY' if us and len(ok) == len(us) and not it.get('kills') and not it.get('problems') else 'HOLD'} "
              f"{i.get('slug')}: urls ok {len(ok)} of {len(us)}, bad {len(badl)}, open {len(open_)}; "
              f"kills {len(it.get('kills') or [])}; problems {len(it.get('problems') or [])}; duplicates {len(it.get('duplicates') or [])}")
    rounds = {}
    up = os.path.join(day_dir(date), "urls.txt")
    if os.path.exists(up):
        for line in open(up, encoding="utf-8"):
            u, _, who = line.rstrip("\n").partition("\t")
            for r in {w.split(":", 1)[0] for w in who.split(",") if w}:
                rounds.setdefault(r, set()).add(u)
    listed = set().union(*rounds.values()) if rounds else set()
    rest = {u for u in v if u not in listed}
    if rest:
        rounds["unlisted"] = rest
    code = 0
    for r, us in sorted(rounds.items()):
        seen = [kv for kv in sorted(((u, v[u]) for u in us if u in v), key=lambda kv: kv[1]["at"]) if kv[1]["status"] != "blocked"]
        first = seen[:10]
        bad = sum(1 for _, x in first if x["status"] in ("dead", "mismatch"))
        if len(first) >= 5 and bad >= 2:
            print(f"FAIL {r} trust: {bad} of the first {len(first)} sources checked were dead or did not say what the reply said; "
                  "set this round aside (coo/KIMI_RESEARCH.md intake step 7)")
            code = 1
        elif first:
            print(f"OK {r} trust: {bad} of the first {len(first)} checked were dead or mismatched")
    return code


def cmd_promote(date, slug):
    today = dt.date.fromisoformat(date)
    v = load_verified(date)
    idea = next((i for i in ideas_of(date) if i.get("slug") == slug), None)
    if not idea:
        print(f"FAIL promote: no idea {slug} read on {date}")
        return 1
    idea = {k: x for k, x in idea.items() if k != "_intake"}
    us, ok, badl, open_ = url_state(idea, v)
    probs, ks, dups = check_idea(idea, today)
    stop = []
    if not us:
        stop.append("no sources at all")
    if badl:
        stop.append(f"{len(badl)} source(s) dead or mismatched: replace them with sources we opened")
    if open_:
        stop.append(f"{len(open_)} source(s) not opened yet: {open_[0]}")
    if probs or ks:
        stop.append("; ".join(probs + ks)[:300])
    if any(d.startswith("slug ") for d in dups):
        stop.append(dups[0])
    if stop:
        print(f"FAIL promote {slug}: " + " | ".join(stop))
        return 1
    idea["status"] = "new"
    idea["origin"] = {"by": "kimi-k3.1-pro", "round": (idea.get("kimi") or {}).get("round", ""), "readAt": date,
                      "verifiedUrls": len(ok), "note": "every source opened and marked ok by Claude before promote"}
    dest = os.path.join(CAND, f"{slug}.json")
    json.dump(idea, open(dest, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    open(dest, "a", encoding="utf-8").write("\n")
    print(f"OK promote {slug}: {len(ok)} sources ok -> {os.path.relpath(dest, ROOT)}"
          + (f" (note: {'; '.join(dups)})" if dups else "") + "; run tools/opportunity_score.py next")
    return 0


def cmd_packet(top):
    if not os.path.exists(OPP_JSON):
        print("FAIL packet: run tools/opportunity_score.py first")
        return 1
    rows = json.load(open(OPP_JSON, encoding="utf-8")).get("ranked") or []
    rows = [r for r in rows if r.get("status") in ("review", "fix", "todd", "new")][:top]
    if not rows:
        print("FAIL packet: no candidates at review, fix or todd")
        return 1
    os.makedirs(WORK, exist_ok=True)
    out = os.path.join(WORK, "r5-packet.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("# ProofNotFluff candidates for red team (R5)\n\nBusiness-level facts only. Each block is one idea as our scorer holds it.\n")
        for r in rows:
            c = json.load(open(os.path.join(CAND, f"{r['slug']}.json"), encoding="utf-8"))
            c.pop("kimi", None)
            fh.write(f"\n## {r['slug']} (score {r.get('score')}, status {r.get('status')})\n\n```json\n")
            fh.write(json.dumps(c, indent=1, ensure_ascii=False))
            fh.write("\n```\n")
    raw = open(out, encoding="utf-8").read()
    if EMAIL.search(raw.replace("noreply@", "")):
        os.remove(out)
        print("FAIL packet: an email address in a candidate; fix the candidate first")
        return 1
    print(f"OK packet: {len(rows)} candidates -> {os.path.relpath(out, ROOT)}")
    return 0


def selftest():
    global WORK, CAND, LAUNCHES, OPP_JSON
    fails, checks, saved = [], [0], (WORK, CAND, LAUNCHES, OPP_JSON)
    tmp = tempfile.mkdtemp(prefix="kimi-selftest-")
    try:
        WORK, CAND, LAUNCHES = os.path.join(tmp, "work"), os.path.join(tmp, "cand"), os.path.join(tmp, "launches")
        OPP_JSON = os.path.join(tmp, "opp.json")
        os.makedirs(CAND)
        os.makedirs(LAUNCHES)
        json.dump({"schema": osc.SCHEMA, "slug": "old-idea", "name": "New Trucking Companies by State", "pitch": "new carriers"},
                  open(os.path.join(CAND, "old-idea.json"), "w"))
        open(os.path.join(LAUNCHES, "chicago-pest-seat.md"), "w").write("# Launch record: Chicago Pest Daily List\n")
        src = {"url": "https://example.gov/a", "date": "2026-10-01"}

        def idea(slug, **ch):
            base = {"schema": osc.SCHEMA, "slug": slug, "name": "Cook County Fire Inspection Failures",
                    "status": "new", "pitch": "failed fire inspections at commercial buildings for fire protection contractors",
                    "categories": ["fire protection"], "provenAbroad": [],
                    "buyer": {"who": "fire protection contractors", "count": 120, "countSource": src,
                              "reach": "their own websites", "reachSource": {"url": "https://example.gov/roster", "date": "2026-10-02"}},
                    "price": {"monthly": 49, "reason": "x", "competitors": [], "freeSubstitute": {}},
                    "demand": {"searchQueries": [], "aiQueries": [{"q": "where do I find buildings that failed fire inspection", "url": "https://example.org/t", "date": "2026-09-01"}]},
                    "data": {"publisher": "Cook County", "dataset": "fire", "subject": "a commercial building", "url": "https://example.gov/data",
                             "cadence": "weekly", "license": {"commercialUse": "allowed", "url": "https://example.gov/terms", "date": "2026-01-01"}},
                    "build": {"days": 4}, "fit": {}, "overlap": "",
                    "kimi": {"round": "R3", "observed": ["the county posts — weekly"]}}
            base.update(ch)
            return base

        r3 = json.dumps({"round": "R3", "ideas": [
            idea("cook-fire-fails"),
            idea("home-owner-list", pitch="homeowners with expired permits", data={"subject": "homeowners", "license": {}}),
            idea("email-leak", pitch="call the owner at owner@example.com or 312-555-0142, posted by u/cleanpro99"),
            idea("old-idea", name="New Trucking Companies by State"),
            idea("zero-days", build={"days": 0}),
            idea("string-count", buyer={"who": "fire protection contractors", "count": "1,240", "countSource": src,
                                        "reach": "their own websites", "reachSource": src}),
            idea("long-quote", demand={"searchQueries": [], "aiQueries": [{"q": " ".join(["word"] * 20), "url": "https://example.org/q", "date": "2026-09-01"}]}),
        ]})
        # R1 carries trailing commas, a planted model slip that loads_loose must tolerate
        r1 = ('{"round": "R1", "pains": [{"id": "p1", "buyer": "pest control", "pain": "x", '
              '"evidence": [{"url": "https://example.org/p", "date": "2026-08-01", "quote": "short and fine",},],},],}')
        r2 = json.dumps({"round": "R2", "products": [], "gaps": [{"id": "g1", "gap": "no daily list \u2014 anywhere", "buyer": "pest"}]})
        r6 = json.dumps({"round": "R6", "channels": [{"id": "c1", "buyer": "pest control", "type": "software marketplace", "cost": "$1,200",
                                                      "url": "https://example.org/apps", "reachSource": {"url": "https://example.org/r6", "date": "2026-10-01"}}],
                         "top3": [{"id": "c1", "why": "x"}]})
        r0 = json.dumps({"round": "R0", "buyers": [{"buyer": "pest control", "evidence": [{"url": "https://example.org/r0", "date": "2026-10-01", "quote": "ok"}]}]})
        reply = (f"R3 | DATE: 2026-10-25\nSUMMARY: x\n```json\n{r3}\n```\n\n```json\n{r1}\n```\n\n```json\n{{not json\n```\n"
                 f"```json\n{r2}\n```\n```json\n{r0}\n```\n```json\n{r6}\n```\n")
        rp = os.path.join(tmp, "reply.txt")
        open(rp, "w").write(reply)
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cmd_read(rp, "2026-10-25")
        out = buf.getvalue()

        def want(cond, what):
            checks[0] += 1
            if not cond:
                fails.append(what)

        want("PASS R3 cook-fire-fails" in out, "a clean idea passes")
        want("FAIL R3 home-owner-list" in out and "K5" in out, "a homeowner list is killed by K5")
        want("an email address removed" in out and "a phone number removed" in out and "a username removed" in out,
             "emails, phones and usernames are removed")
        want("FAIL parse: block 3" in out, "a broken block is reported, not skipped silently")
        want("FAIL R3 old-idea" in out or "WARN R3 old-idea" in out, "an existing slug is flagged")
        want("quote over 15 words dropped" in out, "a long quote is dropped")
        want("FAIL R3 zero-days" in out, "a 0 day build placeholder fails")
        want("buyer.count '1,240' read as 1240.0" in out, "a quoted count is read as a number")
        want("dash replaced" in out, "an em dash is replaced")
        want("OK R1: 1 of 1 kept" in out, "trailing commas in a block are tolerated and R1 is kept")
        saved_r3 = json.load(open(os.path.join(WORK, "2026-10-25", "R3.json")))
        r2s = json.load(open(os.path.join(WORK, "2026-10-25", "R2.json")))
        want(r2s.get("gaps") and "\u2014" not in r2s["gaps"][0]["gap"], "R2 gaps are kept and cleaned")
        want("OK R6: 1 of 1 kept" in out and "cost '$1,200' read as 1200.0" in out and "https://example.org/r6" in open(os.path.join(WORK, "2026-10-25", "urls.txt")).read(),
             "R6 channels are read, a quoted cost is read as a number, and urls are listed")
        want("OK R0: 1 of 1 kept" in out and "https://example.org/r0" in open(os.path.join(WORK, "2026-10-25", "urls.txt")).read(), "R0 is read and its urls listed")
        raw3 = json.dumps(saved_r3, ensure_ascii=False)
        want("owner@example.com" not in raw3 and "555-0142" not in raw3 and "cleanpro99" not in raw3, "no email, phone or username is saved")
        want("—" not in json.dumps(saved_r3, ensure_ascii=False), "no em dash is saved")

        with contextlib.redirect_stdout(io.StringIO()):
            r_early = cmd_promote("2026-10-25", "cook-fire-fails")
        want(r_early == 1, "promote refuses before the sources are opened")
        urls = urls_in({k: x for k, x in next(i for i in saved_r3["ideas"] if i["slug"] == "cook-fire-fails").items() if k != "_intake"})
        want("https://example.gov/terms" in urls and "https://example.org/t" in urls, "urls are collected from nested sources")
        with contextlib.redirect_stdout(io.StringIO()):
            cmd_mark("2026-10-25", "ok", urls[:-1])
            cmd_mark("2026-10-25", "mismatch", urls[-1:])
            r_bad = cmd_promote("2026-10-25", "cook-fire-fails")
        want(r_bad == 1, "promote refuses with a mismatched source")
        with contextlib.redirect_stdout(io.StringIO()):
            cmd_mark("2026-10-25", "ok", urls[-1:])
            r_ok = cmd_promote("2026-10-25", "cook-fire-fails")
            r_k5 = cmd_promote("2026-10-25", "home-owner-list")
            r_dup = cmd_promote("2026-10-25", "old-idea")
        want(r_ok == 0 and os.path.exists(os.path.join(CAND, "cook-fire-fails.json")), "promote writes a verified idea")
        promoted = json.load(open(os.path.join(CAND, "cook-fire-fails.json")))
        want(promoted.get("origin", {}).get("by") == "kimi-k3.1-pro" and "_intake" not in promoted, "promoted file carries origin, not intake notes")
        want(not osc.validate(promoted, os.path.join(CAND, "cook-fire-fails.json")), "promoted file passes the scorer's validate")
        want(r_k5 == 1, "promote refuses a killed idea")
        want(r_dup == 1, "promote refuses an existing slug")
        bare = idea("no-sources", buyer={"who": "fire protection contractors", "reach": "their own websites"},
                    demand={}, data={"subject": "a commercial building", "license": {}}, provenAbroad=[])
        json.dump({"round": "R4", "readAt": "2026-10-25", "ideas": [bare]}, open(os.path.join(WORK, "2026-10-25", "R4.json"), "w"))
        with contextlib.redirect_stdout(io.StringIO()):
            want(cmd_promote("2026-10-25", "no-sources") == 1, "promote refuses an idea with no sources")

        v = {f"https://example.org/{i}": {"status": "dead" if i < 2 else "ok", "at": f"2026-10-25T00:00:{i:02d}+00:00"} for i in range(10)}
        json.dump(v, open(os.path.join(WORK, "2026-10-25", "verified.json"), "w"))
        with contextlib.redirect_stdout(io.StringIO()):
            want(cmd_status("2026-10-25") == 1, "2 dead of the first 10 checked sets the reply aside")
        v = {f"https://example.org/{i}": {"status": "blocked" if i < 2 else "ok", "at": f"2026-10-25T00:00:{i:02d}+00:00"} for i in range(12)}
        json.dump(v, open(os.path.join(WORK, "2026-10-25", "verified.json"), "w"))
        with contextlib.redirect_stdout(io.StringIO()):
            want(cmd_status("2026-10-25") == 0, "sites that refuse our fetcher do not count as invented")
        v = {f"https://example.org/a{i}": {"status": "ok", "at": f"2026-10-25T00:00:{i:02d}+00:00"} for i in range(10)}
        v.update({f"https://example.org/b{i}": {"status": "mismatch" if i < 3 else "ok", "at": f"2026-10-25T00:01:{i:02d}+00:00"} for i in range(6)})
        json.dump(v, open(os.path.join(WORK, "2026-10-25", "verified.json"), "w"))
        with open(os.path.join(WORK, "2026-10-25", "urls.txt"), "w") as fh:
            fh.writelines(f"https://example.org/a{i}\tR0:x\n" for i in range(10))
            fh.writelines(f"https://example.org/b{i}\tR1:y\n" for i in range(6))
        buf2 = io.StringIO()
        with contextlib.redirect_stdout(buf2):
            rc = cmd_status("2026-10-25")
        want(rc == 1 and "FAIL R1 trust" in buf2.getvalue() and "OK R0 trust" in buf2.getvalue(),
             "a bad round is set aside even when an earlier round that day was clean")

        want(bool(PHONE.search("call 312-555-0142 today")) and not PHONE.search("2026-10-25"), "phone pattern catches phones, not dates")
        want(bool(USERNAME.search("posted by u/cleanpro99")), "a reddit username is caught")
    except Exception as e:  # a crash is a failed selftest
        fails.append(f"crashed: {type(e).__name__}: {e}")
    finally:
        WORK, CAND, LAUNCHES, OPP_JSON = saved
        shutil.rmtree(tmp, ignore_errors=True)
    for f in fails:
        print(f"FAIL {f}")
    print(f"kimi_intake selftest: {'PASS' if not fails else 'FAIL'} ({checks[0]} checks, {len(fails)} failed)")
    return 1 if fails else 0


def main():
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("read")
    r.add_argument("file")
    r.add_argument("--date", default=None)
    m = sub.add_parser("mark")
    m.add_argument("date")
    m.add_argument("state")
    m.add_argument("urls", nargs="+")
    s = sub.add_parser("status")
    s.add_argument("date")
    p = sub.add_parser("promote")
    p.add_argument("date")
    p.add_argument("slug")
    k = sub.add_parser("packet")
    k.add_argument("--top", type=int, default=5)
    a = ap.parse_args()
    if a.cmd == "read":
        sys.exit(cmd_read(a.file, a.date or chicago_today().isoformat()))
    if a.cmd == "mark":
        sys.exit(cmd_mark(a.date, a.state, a.urls))
    if a.cmd == "status":
        sys.exit(cmd_status(a.date))
    if a.cmd == "promote":
        sys.exit(cmd_promote(a.date, a.slug))
    sys.exit(cmd_packet(a.top))


if __name__ == "__main__":
    main()
