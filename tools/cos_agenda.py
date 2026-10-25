#!/usr/bin/env python3
"""Chief of Staff agenda (Todd, live chat, Oct 25, 2026: design https://claude.ai/artifact/9AWyGK1WPci1SRhqnEZByY,
answers in coo/DECISIONS-2026-10-25.md "Chief of Staff, 3:59 pm"; stage .claude/skills/chief-of-staff/SKILL.md).

Code builds the agenda; the model only sorts the inbox and judges the few lines this script flags. Every number in the
brief and the Sunday review comes from here, so the model never counts, ranks or dates anything itself.

Inputs, under --data (default data/cos, gitignored; the run fills it with ArtifactData list ... out_dir):
  sb/todos/<id>.json  sb/agents/<id>.json  sb/leadproducts/<id>.json  sb/meta/{money,brief,inbox,cos}.json
  runs.json           {"tasks":[{name, enabled, next, lastStatus, lastFired}]} from list_triggers, PNF tasks only
  crm/prospects/*.json  (review only, optional; read for counts, never copied out)
plus coo/DECISIONS-*.md and coo/HANDOFF.md (the chat closeouts) and git log (what shipped).

Ranking (Todd's rows, fixed score, highest first): money first (a prospect reply waiting on him or a row marked money),
then a row that blocks the crew, then a deadline today or past, then a "now" row 3 or more days old (it jumps above
plain age, marked Day 3; Day 7 asks do it, hand it to Claude or drop it), then a deadline within 3 days, then age, then
a quick win of 5 minutes or less. At most 3 "do now"
items; "now" rows first, "next" rows only fill empty slots. Never ticks, moves or deletes a row: it proposes.

Outputs, under --out (default data/cos):
  brief:  agenda.json, brief.txt (the message, word for word), brief_doc.json (scoreboard meta/brief, the panel),
          cos_doc.json (scoreboard meta/cos updates). agenda.json "quiet": true means nothing changed since the last
          brief, so no message goes out (the panel still records the check).
  review: review.md (the Sunday page, with one STRETCH line for the model to fill), review_doc.json.
  check-doc <file> --kind brief|inbox|review: the privacy and format gate for anything written to the scoreboard:
          counts and our own words only, no email address, phone, link, em or en dash, unknown key or person's words.

Usage: python3 tools/cos_agenda.py brief  [--data D] [--out D] [--now ISO] [--looks-done id,id] [--added "topic; topic"]
       python3 tools/cos_agenda.py review [--data D] [--out D] [--now ISO]
       python3 tools/cos_agenda.py check-doc FILE --kind brief|inbox|review
       python3 tools/cos_agenda.py --selftest
"""
import argparse, datetime as dt, glob, hashlib, json, math, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZNAME = "America/Chicago"
GOAL_DATE = dt.date(2027, 1, 31)
JUDGE_DATE = dt.date(2026, 11, 8)
MAX_NOW = 3

# fixed score weights, in Todd's order (design "The weekday brief")
W_MONEY, W_BLOCKS, W_DUE_NOW, W_DAY3, W_DUE, W_AGE, W_QUICK = 10000, 2000, 1500, 1000, 500, 5, 50

MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
SOURCE_DATE = re.compile(r"\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sept?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?\s(\d{1,2})\b")
SWEEP_SLOTS = ((7, 20), (12, 20))  # weekday inbox sweeps, Chicago time (25 minutes before each brief)
SLACK = dt.timedelta(minutes=5)
REASONS = ("PC asleep or Chrome closed", "Chrome extension not connected", "hello@ not signed in", "sales@ not signed in",
           "wrong account showing", "sign-in prompt", "a page did not load", "paused")
ACCOUNTS = {"hello", "sales"}
MINUTES = re.compile(r"\b(?:about |under |)(\d{1,3})\s*(?:minutes?|mins?)\b", re.I)
TODO_REF = re.compile(r"\btodos? ([a-z0-9][a-z0-9-]{2,60}[a-z0-9])\b")
ASK_CUE = re.compile(r"\b(Pending Todd|Open:|Todd to\b|for Todd'?s? (?:word|yes|go|answer)|waits? (?:for|on) Todd|needs? Todd|Todd (?:edits|approves|chooses|decides))", re.I)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\(?\b\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b")
LINK = re.compile(r"https?://|www\.", re.I)
DASH = re.compile("[—–]")
LOWER_FIRST = {"needs", "need", "your", "the", "its", "after", "waits", "wait", "next", "scheduled", "build", "quests", "outreach", "in", "a", "on"}
STOP = set("a an the and or of to for in on at by with is be it its this that your you our we from as into then than".split())

INBOX_KEYS = {"checkedAt", "ok", "reason", "since", "replies", "yes", "pendingReplies", "sales", "trials", "optouts", "bounces",
              "autoreplies", "fyi", "flagged", "actionRows", "replyLagHours", "accounts", "updatedAt"}
INBOX_NUM = INBOX_KEYS - {"checkedAt", "ok", "reason", "since", "accounts", "updatedAt"}
BRIEF_KEYS = {"date", "slot", "checkedAt", "sentAt", "quiet", "fingerprint", "headline", "items", "inbox", "crew", "moreForYou",
              "urgentMore", "proposal", "gapsAdded", "looksDone", "text", "paused", "updatedAt"}
TODO_KEYS = {"title", "detail", "project", "projectOrder", "owner", "state", "order", "where", "due", "done", "doneAt", "updatedAt",
             "source", "openedAt", "money", "blocks", "minutes"}
REVIEW_KEYS = {"date", "weekOf", "pace", "funnel", "shippedCount", "staleCount", "metrics", "updatedAt"}


# ---------- time ----------
def tz():
    from zoneinfo import ZoneInfo
    return ZoneInfo(TZNAME)


def parse_iso(s):
    if not s or not isinstance(s, str):
        return None
    try:
        d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        try:
            d = dt.datetime.fromisoformat(s[:10])
        except ValueError:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=tz())
    return d.astimezone(tz())


def short_date(d):
    return f"{d.strftime('%b')} {d.day}"


def clock(d):
    return d.strftime("%I:%M %p").lstrip("0").replace("AM", "am").replace("PM", "pm")


# ---------- loading ----------
def load_dir(path):
    out = []
    for f in sorted(glob.glob(os.path.join(path, "*.json"))):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, dict):
            d = dict(d)
            d.setdefault("id", os.path.splitext(os.path.basename(f))[0])
            out.append(d)
    return out


def load_json(path, default=None):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return default


def load(data):
    sb = os.path.join(data, "sb")
    meta = {m: load_json(os.path.join(sb, "meta", m + ".json"), {}) or {} for m in ("money", "brief", "inbox", "cos")}
    runs = load_json(os.path.join(data, "runs.json"), None)
    return {"todos": load_dir(os.path.join(sb, "todos")), "agents": load_dir(os.path.join(sb, "agents")),
            "leads": load_dir(os.path.join(sb, "leadproducts")), "meta": meta,
            "runs": (runs or {}).get("tasks") if isinstance(runs, dict) else None,
            "crm": load_dir(os.path.join(data, "crm", "prospects"))}


# ---------- rows ----------
def opened_on(row, now):
    """When a row first went on the list: openedAt, else the date in its source ("Oct 23 chat"), else updatedAt."""
    d = parse_iso(row.get("openedAt"))
    if d:
        return d.date()
    m = SOURCE_DATE.search(str(row.get("source") or ""))
    if m:
        try:
            y = now.year
            cand = dt.date(y, MONTHS[m.group(1).lower()[:3]], int(m.group(2)))
            if cand > now.date():
                cand = dt.date(y - 1, cand.month, cand.day)
            return cand
        except ValueError:
            pass
    d = parse_iso(row.get("updatedAt"))
    return d.date() if d else now.date()


def day_of(s):
    """A calendar date field ("2026-10-26", or an ISO time whose first 10 characters are the day)."""
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(s or ""))
    if not m:
        return None
    try:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def last_slot(now):
    """The most recent scheduled sweep (weekdays 7:20 am and 12:20 pm) at or before now."""
    for back in range(0, 8):
        day = (now - dt.timedelta(days=back)).date()
        if day.weekday() >= 5:
            continue
        for h, m in reversed(SWEEP_SLOTS):
            slot = dt.datetime(day.year, day.month, day.day, h, m, tzinfo=tz())
            if slot <= now:
                return slot
    return now - dt.timedelta(days=7)


def clean(t):
    """Our own words only on the scoreboard: an address or link in a row title is masked, never published."""
    return re.sub(r"\s{2,}", " ", re.sub(r"(?:https?://|www\.)\S+", "(link)", EMAIL.sub("(address)", str(t or "")))).replace("\u2014", ",").replace("\u2013", "-").strip()


def minutes_of(row):
    v = row.get("minutes")
    if isinstance(v, (int, float)) and v > 0:
        return int(v)
    m = MINUTES.search(f"{row.get('title') or ''} {row.get('detail') or ''}")
    return int(m.group(1)) if m else None


def is_todd(row):
    return str(row.get("owner") or "todd").strip().lower() != "claude"


def score(row, now):
    today = now.date()
    age = (today - opened_on(row, now)).days
    s = 0
    if row.get("money"):
        s += W_MONEY
    if row.get("state") == "now" and age >= 3:
        s += W_DAY3
    if row.get("blocks"):
        s += W_BLOCKS
    due = day_of(row.get("due"))
    if due:
        left = (due - today).days
        if left <= 0:
            s += W_DUE_NOW
        elif left <= 3:
            s += W_DUE - 50 * left
    s += W_AGE * min(max(age, 0), 30)
    mins = minutes_of(row)
    if mins is not None and mins <= 5:
        s += W_QUICK
    return s, age


def nudge(row, age):
    if row.get("state") != "now":
        return ""
    if age >= 7:
        return "day7"
    if age >= 3:
        return "day3"
    return ""


def due_text(row, today):
    due = day_of(row.get("due"))
    if not due:
        return ""
    left = (due - today).days
    if left < 0:
        return f"Was due {short_date(due)}."
    if left == 0:
        return "Due today."
    if left == 1:
        return "Due tomorrow."
    if left <= 3:
        return f"Due {due.strftime('%a')}."
    return ""


def pl(n, one, many):
    return f"{n} {one if n == 1 else many}"


def sentence(t):
    t = str(t).strip().rstrip(". ")
    return t if t[-1:] in "?!" else t + "."


def item_text(it):
    parts = [sentence(it["title"])]
    tail = []
    if it.get("minutes"):
        tail.append(f"{it['minutes']} min")
    if it.get("where"):
        w = it["where"]
        low = tail and w.split(" ")[0].strip(",").lower() in LOWER_FIRST
        tail.append(w[0].lower() + w[1:] if low else w)
    if tail:
        parts.append(", ".join(tail) + ".")
    if it.get("blocks"):
        parts.append(f"Blocks {it['blocks'].rstrip('.')}.")
    if it.get("due"):
        parts.append(it["due"])
    if it.get("nudge") == "day7":
        parts.append(f"Day {it['age']}: do it, hand it to Claude, or drop it?")
    elif it.get("nudge") == "day3":
        parts.append(f"Day {it['age']}, open since {it['opened']}.")
    elif it.get("age", 0) >= 1 and not it.get("synthetic"):
        parts.append(f"Open since {it['opened']}.")
    return " ".join(parts)


# ---------- gaps: chat closeouts the list does not carry ----------
def words(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 2}


def gap_hash(rel, line):
    return hashlib.sha1(f"{rel}|{line.strip()}".encode()).hexdigest()[:10]


def find_gaps(root, todos, seen, now, days=3):
    ids = {t["id"] for t in todos}
    open_titles = [words(f"{t.get('title') or ''} {t.get('detail') or ''}") for t in todos if not t.get("done")]
    refs, cands = [], []
    files = [os.path.join(root, "coo", "HANDOFF.md")]
    for f in sorted(glob.glob(os.path.join(root, "coo", "DECISIONS-*.md"))):
        m = re.search(r"(\d{4}-\d{2}-\d{2})", f)
        if m and (now.date() - dt.date.fromisoformat(m.group(1))).days <= days - 1:
            files.append(f)
    for f in files:
        if not os.path.exists(f):
            continue
        rel = os.path.relpath(f, root)
        heading = ""
        for line in open(f, encoding="utf-8"):
            if line.startswith("## "):
                heading = line[3:].strip()
                continue
            for slug in TODO_REF.findall(line):
                if slug not in ids and slug not in seen and not any(r["slug"] == slug for r in refs):
                    refs.append({"slug": slug, "file": rel, "topic": heading or "handoff"})
            if rel.endswith("HANDOFF.md") or not ASK_CUE.search(line):
                continue
            if TODO_REF.search(line):
                continue
            h = gap_hash(rel, line)
            if h in seen:
                continue
            w = words(ASK_CUE.split(line, 1)[-1] if ASK_CUE.search(line) else line)
            best = max((len(w & t) / max(1, min(len(w), 6)) for t in open_titles), default=0)
            if best >= 0.5:
                continue
            cands.append({"hash": h, "file": rel, "topic": heading, "line": line.strip()[:300]})
    return refs, cands


# ---------- runs ----------
def short_task(name):
    n = re.sub(r"^(PNF|ProofNotFluff)\s*(leads|site|credits)?:?\s*", "", str(name or ""), flags=re.I).strip()
    return n[:1].lower() + n[1:] if n else str(name or "")


def crew(runs, now):
    if runs is None:
        return {"known": False, "today": [], "runs24": 0, "failed24": 0, "failedNames": []}
    today, out, ran, failed = now.date(), [], 0, []
    for t in runs:
        nxt = parse_iso(t.get("next"))
        if t.get("enabled", True) and nxt and nxt.date() == today and nxt >= now:
            out.append((nxt, short_task(t.get("name"))))
        lf = parse_iso(t.get("lastFired"))
        if lf and now - lf <= dt.timedelta(hours=24):
            ran += 1
            st = str(t.get("lastStatus") or "").upper()
            if st and "SUCCEEDED" not in st and "RUNNING" not in st and "PENDING" not in st:
                failed.append(short_task(t.get("name")))
    out.sort()
    return {"known": True, "today": [f"{n} ({clock(d)})" for d, n in out], "runs24": ran, "failed24": len(failed),
            "failedNames": failed}


# ---------- money ----------
def money_line(meta, now):
    m = meta.get("money") or {}
    goal = int(m.get("goal") or 1000)
    month = now.strftime("%Y-%m")
    rev = m.get("revenueMonth") if m.get("month") in (None, month) else 0
    rev = rev if isinstance(rev, (int, float)) else 0
    goal_date = parse_iso(m.get("goalDate"))
    gd = goal_date.date() if goal_date else GOAL_DATE
    weeks = max(0, round((gd - now.date()).days / 7))
    return {"revenueMonth": rev, "goal": goal, "weeksLeft": weeks, "goalDate": gd.isoformat(),
            "mrr": m.get("mrr") or 0, "subscribers": m.get("subscribers") or 0}


def usd(v):
    v = float(v or 0)
    return f"${v:,.0f}" if v == int(v) else f"${v:,.2f}"


# ---------- the brief ----------
def build_brief(data, root, now, looks_done=(), added=()):
    D = load(data)
    meta, todos = D["meta"], D["todos"]
    today = now.date()
    if not todos:
        raise SystemExit("ERROR cos brief: no to-do rows in " + os.path.join(data, "sb", "todos") + " (the pull failed or went to the wrong folder); no brief sent")
    open_rows = [t for t in todos if t.get("title") and not t.get("done")]
    mine = [t for t in open_rows if is_todd(t) and t.get("state") in ("now", "next") and t["id"] not in looks_done]

    # inbox: fails loud, never a quiet zero
    ib = meta.get("inbox") or {}
    ib_at = parse_iso(ib.get("checkedAt"))
    slot_at = last_slot(now)
    fresh = bool(ib_at and ib_at >= slot_at - SLACK)
    inbox = {k: (ib.get(k) or 0) for k in ("replies", "yes", "pendingReplies", "sales", "trials", "optouts", "bounces", "autoreplies", "fyi", "flagged")}
    ok = bool(ib.get("ok")) and fresh
    if ok:
        reason = ib.get("reason") or ""  # a partial sweep (one inbox reached) keeps its reason as a note
    elif ib_at and not fresh:
        reason = f"the {clock(slot_at)} sweep did not finish (last check {short_date(ib_at.date())} {clock(ib_at)})"
    else:
        reason = ib.get("reason") or "never checked"
    inbox.update({"ok": ok, "checkedAt": ib.get("checkedAt") or "", "reason": reason})

    items = []
    pending = int(inbox["pendingReplies"] or 0)
    if pending:
        items.append({"id": "inbox-replies", "synthetic": True, "score": W_MONEY * 2, "age": 0, "nudge": "",
                      "title": f"Send {pending} prospect repl{'y' if pending == 1 else 'ies'} drafted in the thread, or name {'it' if pending == 1 else 'them'} in chat",
                      "minutes": 2 * pending, "where": "Gmail drafts", "blocks": "", "due": "", "opened": ""})
    ranked = []
    for t in mine:
        s, age = score(t, now)
        ranked.append({"id": t["id"], "score": s, "age": age, "state": t.get("state"), "title": clean(t.get("title")),
                       "minutes": minutes_of(t), "where": clean(t.get("where")), "blocks": clean(t.get("blocks")),
                       "due": due_text(t, today), "nudge": nudge(t, age), "opened": short_date(opened_on(t, now)),
                       "money": bool(t.get("money")), "dueSoon": bool(day_of(t.get("due")) and (day_of(t.get("due")) - today).days <= 3)})
    nows = sorted([r for r in ranked if r["state"] == "now"], key=lambda r: (-r["score"], r["title"]))
    nexts = sorted([r for r in ranked if r["state"] == "next"], key=lambda r: (-r["score"], r["title"]))
    slots = MAX_NOW - len(items)
    picked = (nows + nexts)[:max(0, slots)]
    items += picked
    shown = {i["id"] for i in items}

    # more than 3 "now" rows: propose which move to next (Todd confirms with "apply the brief")
    proposal = None
    rest_now = [r for r in nows if r["id"] not in shown]
    if len(nows) > MAX_NOW or (pending and len(nows) > MAX_NOW - 1):
        movable = [r for r in rest_now if not (r["money"] or r["blocks"] or r["dueSoon"] or r["nudge"] == "day7")]
        if movable:
            proposal = {"move": [r["id"] for r in movable], "titles": [r["title"] for r in movable], "to": "next",
                        "nowCount": len(nows)}

    more = [r for r in ranked if r["id"] not in shown]
    urgent_more = any(r["dueSoon"] or r["nudge"] == "day7" or r["blocks"] for r in more)

    refs, cands = find_gaps(root, todos, set((meta.get("cos") or {}).get("seenGaps") or []), now)
    cr = crew(D["runs"], now)
    ml = money_line(meta, now)

    slot = "am" if now.hour < 11 else "pm"
    head = (f"PNF, {now.strftime('%a')} {short_date(today)}, {clock(now)}. {usd(ml['revenueMonth'])} of the {usd(ml['goal'])} month. "
            f"{ml['weeksLeft']} weeks to {short_date(dt.date.fromisoformat(ml['goalDate']))}.")
    lines = [head]
    if inbox["sales"] or inbox["trials"]:
        lines.append(f"New: {inbox['sales']} sale{'s' if inbox['sales'] != 1 else ''}, {inbox['trials']} trial{'s' if inbox['trials'] != 1 else ''}. Each prospect is now a customer in the CRM.")
    lines.append("")
    if items:
        lines.append("Do now:")
        lines += [f"{n}. {item_text(it)}" for n, it in enumerate(items, 1)]
    else:
        lines.append("Nothing needs you right now.")
    lines.append("")
    if inbox["ok"]:
        lines.append(f"Inbox ({clock(ib_at)} check): {pl(inbox['replies'], 'prospect reply', 'prospect replies')}"
                     f"{' (drafts ready)' if pending else ''}, {inbox['yes']} yes to the Monday email, {pl(inbox['sales'], 'sale', 'sales')}, "
                     f"{pl(inbox['optouts'], 'opt-out', 'opt-outs')}, {pl(inbox['bounces'], 'bounce', 'bounces')}, {inbox['fyi']} FYI"
                     f"{', ' + str(inbox['flagged']) + ' tax, state, bank or legal (subject only, on your list)' if inbox['flagged'] else ''}."
                     + (f" Partly checked: {inbox['reason']}." if inbox["reason"] else ""))
    else:
        lines.append(f"Inbox not checked: {inbox['reason']}.")
    if cr["known"]:
        today_txt = ", ".join(cr["today"]) if cr["today"] else "nothing else scheduled"
        fail_txt = f", {cr['failed24']} failed ({', '.join(cr['failedNames'])})" if cr["failed24"] else ", 0 failed"
        lines.append(f"Crew today: {today_txt}. Last 24h: {cr['runs24']} runs{fail_txt}.")
    else:
        lines.append("Crew: scheduled task list not read this run.")
    for t in looks_done:
        row = next((r for r in todos if r["id"] == t), None)
        if row:
            lines.append(f"Looks done already: {sentence(row.get('title'))} Tick it if so.")
    if added:
        lines.append("Added to your list from chats: " + "; ".join(added) + ".")
    if proposal:
        lines.append(f"You have {proposal['nowCount']} \"now\" items, more than 3. I'd move {len(proposal['move'])} to next: "
                     + sentence("; ".join(t.rstrip(".") for t in proposal["titles"][:6]) + (f" and {len(proposal['titles']) - 6} more" if len(proposal["titles"]) > 6 else ""))
                     + " Say \"apply the brief\" in any PNF chat to do it.")
    if more:
        lines.append(f"{len(more)} more wait on you{', none urgent' if not urgent_more else ', one or more due soon'}.")
    text = "\n".join(lines).strip() + "\n"

    fp_src = {"items": [(i["id"], i.get("nudge"), i.get("due")) for i in items], "inbox": [inbox[k] for k in ("replies", "pendingReplies", "sales", "trials", "flagged", "ok")],
              "failed": sorted(cr["failedNames"]), "gaps": sorted([r["slug"] for r in refs] + [c["hash"] for c in cands]),
              "proposal": (proposal or {}).get("move"), "looks": sorted(looks_done), "added": list(added)}
    fingerprint = hashlib.sha1(json.dumps(fp_src, sort_keys=True).encode()).hexdigest()[:12]
    last = meta.get("brief") or {}
    quiet = bool(last.get("fingerprint") == fingerprint and last.get("sentAt") and not added and not refs and not cands)

    nowiso = now.isoformat(timespec="seconds")
    panel_items = [{"id": i["id"], "title": i["title"], "minutes": i.get("minutes") or 0, "where": i.get("where") or "",
                    "why": " ".join(x for x in [("Blocks " + i["blocks"]) if i.get("blocks") else "", i.get("due") or "",
                                                 ("Day %d" % i["age"]) if i.get("nudge") else ""] if x).strip(),
                    "nudge": i.get("nudge") or ""} for i in items]
    doc = {"date": today.isoformat(), "slot": slot, "checkedAt": nowiso, "sentAt": (last.get("sentAt") if quiet else nowiso),
           "quiet": quiet, "fingerprint": fingerprint, "headline": head, "items": panel_items,
           "inbox": {k: inbox[k] for k in ("ok", "reason", "checkedAt", "replies", "yes", "pendingReplies", "sales", "trials", "optouts", "bounces", "fyi", "flagged")},
           "crew": cr, "moreForYou": len(more), "urgentMore": urgent_more,
           "proposal": ({"move": proposal["move"], "titles": proposal["titles"], "to": "next"} if proposal else None),
           "gapsAdded": list(added), "looksDone": list(looks_done), "text": text, "paused": False, "updatedAt": nowiso}

    cos = dict(meta.get("cos") or {})
    week = (today - dt.timedelta(days=today.weekday())).isoformat()
    wk = cos.get("week") if isinstance(cos.get("week"), dict) and cos["week"].get("weekOf") == week else {"weekOf": week, "gapsFound": 0, "maxReplyLagHours": 0, "nowMax": 0}
    wk["gapsFound"] = int(wk.get("gapsFound") or 0) + len(added)
    lag = ib.get("replyLagHours") if isinstance(ib.get("replyLagHours"), (int, float)) else 0
    wk["maxReplyLagHours"] = max(float(wk.get("maxReplyLagHours") or 0), float(lag or 0))
    wk["nowMax"] = max(int(wk.get("nowMax") or 0), len(nows))
    cos_doc = {"week": wk, "lastBriefAt": nowiso, "updatedAt": nowiso}

    agenda = {"now": nowiso, "slot": slot, "quiet": quiet, "items": items, "nowCount": len(nows), "proposal": proposal,
              "more": len(more), "urgentMore": urgent_more, "inbox": inbox, "crew": cr, "money": ml,
              "gaps": {"refs": refs, "candidates": cands}, "fingerprint": fingerprint}
    return agenda, text, doc, cos_doc


# ---------- the Sunday review ----------
def git_lines(root, since):
    try:
        r = subprocess.run(["git", "log", f"--since={since}", "--pretty=%cs %s"], cwd=root, capture_output=True, text=True, timeout=30)
        oldest = subprocess.run(["git", "log", "--reverse", "--pretty=%cs", "-1"], cwd=root, capture_output=True, text=True, timeout=10)
        first = subprocess.run(["git", "rev-list", "--max-parents=0", "--pretty=%cs", "HEAD"], cwd=root, capture_output=True, text=True, timeout=10)
        lines = [l for l in r.stdout.splitlines() if l.strip()]
        dates = [l for l in first.stdout.splitlines() if re.match(r"\d{4}-\d{2}-\d{2}$", l)]
        truncated = bool(dates) and min(dates) >= since  # the local history starts inside the window: a shallow clone
        return lines, truncated
    except Exception:
        return [], True


def build_review(data, root, now):
    D = load(data)
    meta, todos, today = D["meta"], D["todos"], now.date()
    week0 = today - dt.timedelta(days=6)
    prev0 = week0 - dt.timedelta(days=7)
    ml = money_line(meta, now)
    live = [p for p in D["leads"] if p.get("status") == "live" and isinstance(p.get("price"), (int, float)) and p["price"] > 0]
    gap = max(0, ml["goal"] - float(ml["mrr"] or 0))
    prices = sorted({float(p["price"]) for p in live})
    payers_at = [f"{math.ceil(gap / pr)} at {usd(pr)}" for pr in prices] if gap else []
    weeks = max(1, ml["weeksLeft"])

    def count(field, a, b):
        n = 0
        for p in D["crm"]:
            d = parse_iso(p.get(field))
            if d and a <= d.date() <= b:
                n += 1
        return n
    fields = [("Emails sent", "firstSentAt"), ("Replies", "repliedAt"), ("Yes to the Monday email", "mondayYesAt"),
              ("Trial offers", "trialOfferedAt"), ("Customers", "customerAt")]
    funnel = [{"label": l, "week": count(f, week0, today), "prev": count(f, prev0, week0 - dt.timedelta(days=1))} for l, f in fields]

    shipped_git, shallow = git_lines(root, (week0 - dt.timedelta(days=1)).isoformat())
    done_rows = [t for t in todos if t.get("done") and (parse_iso(t.get("doneAt")) or now).date() >= week0]
    open_rows = [t for t in todos if t.get("title") and not t.get("done")]
    stale = []
    for t in open_rows:
        due = day_of(t.get("due"))
        up = parse_iso(t.get("updatedAt"))
        if due and due < today:
            stale.append((t, f"past its date ({short_date(due)})"))
        elif is_todd(t) and t.get("state") in ("now", "next") and (today - opened_on(t, now)).days >= 14:
            stale.append((t, f"open {(today - opened_on(t, now)).days} days"))
        elif up and (today - up.date()).days >= 14:
            stale.append((t, f"untouched {(today - up.date()).days} days"))
    mine = [t for t in open_rows if is_todd(t) and t.get("state") in ("now", "next")]
    ranked = sorted(mine, key=lambda t: (-score(t, now)[0], str(t.get("title"))))
    nows = [t for t in mine if t.get("state") == "now"]
    oldest = max([score(t, now)[1] for t in nows], default=0)
    cos = meta.get("cos") or {}
    wk = cos.get("week") or {}

    L = [f"# PNF Sunday review, {now.strftime('%a')} {short_date(today)}, {today.year}", ""]
    L += ["## Pace", f"- {usd(ml['revenueMonth'])} of the {usd(ml['goal'])} month in {now.strftime('%B')}; MRR {usd(ml['mrr'])}, "
          f"{ml['subscribers']} paying. {ml['weeksLeft']} weeks to {short_date(dt.date.fromisoformat(ml['goalDate']))}."]
    if payers_at:
        L.append(f"- A {usd(ml['goal'])} month from subscriptions takes about " + ", or ".join(payers_at)
                 + f" more payers; spread over {weeks} weeks that is about {math.ceil(gap / max(prices) / weeks * 10) / 10 if prices else 0} to "
                 f"{math.ceil(gap / min(prices) / weeks * 10) / 10 if prices else 0} new payers a week.")
    L += ["", "## Funnel (this week, last week)"]
    L += [f"- {f['label']}: {f['week']}, {f['prev']}" for f in funnel]
    if not D["crm"]:
        L.append("- CRM not read this run: funnel counts are zero by default.")
    L += ["", "## Shipped"]
    L += [f"- {t.get('title')}" for t in sorted(done_rows, key=lambda t: str(t.get("doneAt")))][:12] or ["- No rows ticked this week."]
    L.append(f"- {'At least ' if shallow else ''}{len(shipped_git)} commits to main this week" + (" (the clone's history starts inside the week)" if shallow else "") + ".")
    L += ["", "## Stale (keep, move or drop: your call)"]
    L += [f"- {t.get('title')}: {why}. Proposed: {'move to later' if is_todd(t) else 'Claude updates or drops it'}." for t, why in stale[:12]] or ["- Nothing stale."]
    L += ["", "## Next week: your 3 commitments, for your yes"]
    L += [f"{n}. {sentence(t.get('title'))}" for n, t in enumerate(ranked[:3], 1)] or ["Nothing open for you."]
    L += ["", "## One stretch move", "STRETCH: (filled by the run from scout/OPPORTUNITIES.md, coo/OPPORTUNITIES.md and the latest radar notes: one move, its cost, its expected effect in dollars, yes or no)"]
    L += ["", "## Is the Chief of Staff working (judged Nov 8)",
          f"- Your \"now\" items: {len(nows)} today, at most {wk.get('nowMax', len(nows))} this week (target 3 or fewer).",
          f"- Oldest \"now\" item: {oldest} days (target 7 or fewer).",
          f"- Slowest prospect reply caught: {wk.get('maxReplyLagHours', 0)} hours this week (target same weekday).",
          f"- Open items from chats found missing: {wk.get('gapsFound', 0)} this week (target 0)."]
    if today >= JUDGE_DATE and not cos.get("judgedAt"):
        moved = len(nows) <= 3 and oldest <= 7
        L.append(f"- Verdict due today: {'keep it as is' if moved else 'the first two numbers have not moved, so I propose dropping to the Sunday review only'}. Your call in chat.")
    text = "\n".join(L).rstrip() + "\n"
    doc = {"date": today.isoformat(), "weekOf": week0.isoformat(), "pace": {k: ml[k] for k in ("revenueMonth", "goal", "weeksLeft", "mrr", "subscribers")},
           "funnel": funnel, "shippedCount": len(done_rows), "staleCount": len(stale),
           "metrics": {"nowCount": len(nows), "oldestNowDays": oldest, "maxReplyLagHours": wk.get("maxReplyLagHours", 0), "gapsFound": wk.get("gapsFound", 0)},
           "updatedAt": now.isoformat(timespec="seconds")}
    return text, doc


# ---------- the privacy and format gate ----------
def check_doc(doc, kind):
    errs = []
    allowed = {"brief": BRIEF_KEYS, "inbox": INBOX_KEYS, "review": REVIEW_KEYS, "todo": TODO_KEYS}[kind]
    if not isinstance(doc, dict):
        return ["not a JSON object"]
    for k in doc:
        if k not in allowed:
            errs.append(f"unknown key {k!r}")

    def walk(v, path):
        if isinstance(v, dict):
            for k, x in v.items():
                walk(x, f"{path}.{k}")
        elif isinstance(v, list):
            for i, x in enumerate(v):
                walk(x, f"{path}[{i}]")
        elif isinstance(v, str):
            if EMAIL.search(v):
                errs.append(f"{path}: an email address")
            if PHONE.search(v) or re.search(r"\d{7,}", v):
                errs.append(f"{path}: a phone number")
            if LINK.search(v):
                errs.append(f"{path}: a link")
            if DASH.search(v):
                errs.append(f"{path}: an em or en dash")
            if kind == "inbox" and re.search(r"[\"“”][^\"“”\n]{25,}[\"“”]", v):
                errs.append(f"{path}: a long quote (someone's own words)")
    walk(doc, kind)
    if kind == "inbox":
        for k in INBOX_NUM:
            if k in doc and not isinstance(doc[k], (int, float)):
                errs.append(f"inbox.{k} must be a number")
        if "ok" not in doc or "checkedAt" not in doc:
            errs.append("inbox needs ok and checkedAt")
        if doc.get("ok") is False and not doc.get("reason"):
            errs.append("a failed sweep needs a reason (fails loud, never a quiet zero)")
        for part in [x.strip() for x in str(doc.get("reason") or "").split(";") if x.strip()]:
            if part not in REASONS:
                errs.append(f"inbox.reason {part!r} is not one of the fixed reasons (tools/cos_agenda.py REASONS)")
        acc = doc.get("accounts", [])
        if not isinstance(acc, list) or any(a not in ACCOUNTS for a in acc):
            errs.append("inbox.accounts must list only the labels hello and sales")
        for k in ("checkedAt", "since"):
            if doc.get(k) and not parse_iso(doc.get(k)):
                errs.append(f"inbox.{k} is not an ISO time")
    if kind == "todo":
        if not doc.get("title"):
            errs.append("a row needs a title")
        if str(doc.get("owner") or "").lower() not in ("todd", "claude"):
            errs.append("owner must be todd or claude")
        if doc.get("state") not in ("now", "next", "later", "waiting"):
            errs.append("state must be now, next, later or waiting")
        if len(str(doc.get("title") or "")) > 120 or len(str(doc.get("detail") or "")) > 400:
            errs.append("title over 120 or detail over 400 characters")
    if kind == "brief":
        if len(doc.get("items") or []) > MAX_NOW:
            errs.append(f"brief has more than {MAX_NOW} do-now items")
    return errs


# ---------- selftest ----------
def selftest():
    cases, bad = [], 0
    now = dt.datetime(2026, 10, 26, 7, 45, tzinfo=tz())
    with tempfile.TemporaryDirectory() as tmp:
        data, root = os.path.join(tmp, "cos"), os.path.join(tmp, "repo")
        for sub in ("sb/todos", "sb/meta", "sb/agents", "sb/leadproducts"):
            os.makedirs(os.path.join(data, sub))
        os.makedirs(os.path.join(root, "coo"))

        def todo(i, **kw):
            json.dump(dict(kw), open(os.path.join(data, "sb", "todos", i + ".json"), "w"))
        todo("old", title="Get the EIN", owner="todd", state="now", source="Oct 23 chat", detail="About 10 minutes.", where="irs.gov")
        todo("blk", title="Approve the rule", owner="todd", state="now", source="Oct 25 chat", due="2026-10-26", blocks="the 11:40 post")
        todo("quick", title="Pick a name", owner="todd", state="now", source="Oct 25 chat", minutes=2)
        todo("week", title="Answer the history question", owner="todd", state="now", source="Oct 18 chat")
        todo("n5", title="Make the form", owner="todd", state="now", source="Oct 25 chat")
        todo("nx", title="Decide on a records request", owner="todd", state="next", source="Oct 24 chat")
        todo("cl", title="Claude row", owner="claude", state="now", source="Oct 20 chat")
        todo("dn", title="Done row", owner="todd", state="now", done=True)
        json.dump({"goal": 1000, "month": "2026-10", "revenueMonth": 0, "mrr": 0, "subscribers": 0, "goalDate": "2027-01-31"},
                  open(os.path.join(data, "sb", "meta", "money.json"), "w"))
        json.dump({"tasks": [{"name": "PNF leads: outreach", "enabled": True, "next": "2026-10-26T09:40:00-05:00", "lastStatus": "ROUTINE_RUN_STATUS_SUCCEEDED", "lastFired": "2026-10-25T09:00:00-05:00"},
                             {"name": "PNF radar", "enabled": True, "next": "2026-11-02T09:31:00-06:00", "lastStatus": "ROUTINE_RUN_STATUS_FAILED", "lastFired": "2026-10-26T06:00:00-05:00"}]},
                  open(os.path.join(data, "runs.json"), "w"))
        open(os.path.join(root, "coo", "HANDOFF.md"), "w").write("- build next chat: todo planted-missing-row.\n")
        open(os.path.join(root, "coo", "DECISIONS-2026-10-25.md"), "w").write(
            "## Facebook, 2:30 pm\n- Open: the zebra hosting contract renewal (Todd to choose).\n- Pending Todd: approve the rule today.\n")

        def check(name, cond):
            nonlocal bad
            cases.append(name)
            if not cond:
                bad += 1
                print(f"FAIL cos selftest: {name}")

        # 1. no inbox doc: fails loud, never a quiet zero
        ag, text, doc, _ = build_brief(data, root, now)
        check("inbox never read shows as not checked", "Inbox not checked" in text and not ag["inbox"]["ok"])
        check("at most 3 do-now items", len(ag["items"]) == 3)
        ids = [i["id"] for i in ag["items"]]
        check("a blocker due today leads, then Day 7, then Day 3, ahead of a quick win", ids == ["blk", "week", "old"])
        check("Claude's rows and done rows never in Todd's brief", "cl" not in ids and "dn" not in ids)
        check("Day 7 asks do it, hand it to Claude, or drop it", "do it, hand it to Claude, or drop it" in text)
        check("minutes read from the detail", "10 min" in text)
        check("more than 3 now items gets a move proposal that spares blockers and due rows",
              ag["proposal"] and "blk" not in ag["proposal"]["move"] and "n5" in ag["proposal"]["move"])
        check("next rows never fill while now rows wait", "nx" not in ids)
        check("failed run named", "1 failed (radar)" in text)
        check("crew today lists the 9:40 run", "outreach (9:40 am)" in text)
        check("missing todo reference found", any(r["slug"] == "planted-missing-row" for r in ag["gaps"]["refs"]))
        check("an ask already on the list is not flagged", not any("approve the rule" in c["line"] for c in ag["gaps"]["candidates"]))
        check("an ask not on the list is flagged", any("zebra" in c["line"] for c in ag["gaps"]["candidates"]))
        check("brief passes its own gate", not check_doc(doc, "brief"))
        check("no em or en dash in the message", not DASH.search(text))

        # 2. a prospect reply waiting: money first
        json.dump({"checkedAt": "2026-10-26T07:31:00-05:00", "ok": True, "replies": 1, "pendingReplies": 1, "sales": 0, "fyi": 3},
                  open(os.path.join(data, "sb", "meta", "inbox.json"), "w"))
        ag, text, doc, _ = build_brief(data, root, now)
        check("a waiting prospect reply is item 1", ag["items"][0]["id"] == "inbox-replies")
        check("inbox line reads the 7:31 check", "Inbox (7:31 am check): 1 prospect reply (drafts ready)" in text)

        # 3. a stale sweep (yesterday) fails loud
        json.dump({"checkedAt": "2026-10-25T12:31:00-05:00", "ok": True, "replies": 0}, open(os.path.join(data, "sb", "meta", "inbox.json"), "w"))
        ag, text, _, _ = build_brief(data, root, now)
        check("a sweep that missed the 7:20 slot shows as not checked", "Inbox not checked: the 7:20 am sweep did not finish (last check Oct 25" in text)
        json.dump({"checkedAt": "2026-10-26T07:33:00-05:00", "ok": True, "reason": "sales@ not signed in", "accounts": ["hello"]},
                  open(os.path.join(data, "sb", "meta", "inbox.json"), "w"))
        ag, text, _, _ = build_brief(data, root, now)
        check("a partial sweep counts but says which inbox was missed", ag["inbox"]["ok"] and "Partly checked: sales@ not signed in." in text)
        ag, text, _, _ = build_brief(data, root, now + dt.timedelta(hours=5, minutes=15))
        check("a crashed 12:20 sweep fails loud at 1 pm", "Inbox not checked: the 12:20 pm sweep did not finish" in text)

        # 4. quiet when nothing changed since the last brief
        json.dump({"checkedAt": "2026-10-26T07:31:00-05:00", "ok": True}, open(os.path.join(data, "sb", "meta", "inbox.json"), "w"))
        os.remove(os.path.join(root, "coo", "DECISIONS-2026-10-25.md"))
        open(os.path.join(root, "coo", "HANDOFF.md"), "w").write("- nothing\n")
        ag, _, doc, _ = build_brief(data, root, now)
        check("first brief is never quiet", not ag["quiet"])
        json.dump(doc, open(os.path.join(data, "sb", "meta", "brief.json"), "w"))
        json.dump({"checkedAt": "2026-10-26T12:32:00-05:00", "ok": True}, open(os.path.join(data, "sb", "meta", "inbox.json"), "w"))
        ag2, _, doc2, _ = build_brief(data, root, now + dt.timedelta(hours=5))
        check("same agenda later is quiet", ag2["quiet"] and doc2["sentAt"] == doc["sentAt"])
        todo("new", title="A brand new ask", owner="todd", state="now", source="Oct 26 chat", money=True)
        ag3, _, _, _ = build_brief(data, root, now + dt.timedelta(hours=5))
        check("a new money row breaks the quiet", not ag3["quiet"] and ag3["items"][0]["id"] == "new")
        ag4, text4, _, _ = build_brief(data, root, now, looks_done=("new",))
        todo("mkt", title="Market 12 look", owner="todd", state="next", source="Market 12 chat, Decide 3")
        todo("feb", title="Odd date https://x.co/a and jane@acme.com", owner="Claude", state="now", source="Feb 30 chat")
        todo("z", title="Due row", owner="todd", state="next", source="Oct 26 chat", due="2026-10-27T00:00:00Z")
        ag5, text5, doc5, _ = build_brief(data, root, now)
        check("Market 12 and Feb 30 are not dates and never crash", True)
        check("owner Claude with a capital C stays off Todd's brief", "feb" not in [i["id"] for i in ag5["items"]])
        z = next((r for r in json.load(open(os.path.join(data, "sb", "todos", "z.json"))).items()), None)
        check("a due date written as UTC midnight reads as that day", due_text({"due": "2026-10-27T00:00:00Z"}, now.date()) == "Due tomorrow.")
        check("addresses and links in titles are masked, the brief still passes", clean("see https://x.co/a or jane@acme.com") == "see (link) or (address)" and not check_doc(doc5, "brief"))
        json.dump({"seenGaps": ["planted-missing-row"]}, open(os.path.join(data, "sb", "meta", "cos.json"), "w"))
        open(os.path.join(root, "coo", "HANDOFF.md"), "w").write("- build next chat: todo planted-missing-row.\n")
        ag6, _, _, _ = build_brief(data, root, now)
        check("a judged todo ref is not flagged again", not ag6["gaps"]["refs"])
        for f in glob.glob(os.path.join(data, "sb", "todos", "*.json")):
            os.remove(f)
        try:
            build_brief(data, root, now)
            check("an empty to-do pull fails loud", False)
        except SystemExit as e:
            check("an empty to-do pull fails loud", "no to-do rows" in str(e))
        check("a looks-done row leaves the top 3 and is named", "new" not in [i["id"] for i in ag4["items"]] and "Looks done already: A brand new ask" in text4)

    # 5. the gate catches what must never reach the scoreboard
    planted = [("email", {"checkedAt": "x", "ok": True, "reason": "from jane@acme.com"}),
               ("phone", {"checkedAt": "x", "ok": True, "reason": "call 312 555 0199"}),
               ("link", {"checkedAt": "x", "ok": True, "reason": "see https://x.co"}),
               ("dash", {"checkedAt": "x", "ok": True, "reason": "ok — fine"}),
               ("unknown key", {"checkedAt": "x", "ok": True, "senderName": "Jane"}),
               ("non-number count", {"checkedAt": "x", "ok": True, "replies": "Jane said yes"}),
               ("quiet failure", {"checkedAt": "x", "ok": False}),
               ("long quote", {"checkedAt": "x", "ok": True, "reason": "\"we would love to try this next week please\""}),
               ("unseparated phone", {"checkedAt": "2026-10-26T07:31:00-05:00", "ok": True, "reason": "call 3125550199"}),
               ("free text reason", {"checkedAt": "2026-10-26T07:31:00-05:00", "ok": False, "reason": "Jane Smith replied"}),
               ("address in accounts", {"checkedAt": "2026-10-26T07:31:00-05:00", "ok": True, "accounts": ["hello@proofnotfluff.com"]})]
    for name, d in planted:
        if not check_doc(d, "inbox"):
            bad += 1
            print(f"FAIL cos selftest: gate missed a planted {name}")
        cases.append("gate " + name)
    if check_doc({"checkedAt": "2026-10-26T07:31:00-05:00", "ok": True, "replies": 0, "accounts": ["hello", "sales"]}, "inbox"):
        bad += 1
        print("FAIL cos selftest: gate refused a clean inbox doc")
    cases.append("gate clean doc")
    for name, d in [("row with a link", {"title": "Check https://bad.example", "owner": "todd", "state": "now"}),
                    ("row with an unknown owner", {"title": "Check Kit", "owner": "jane", "state": "now"})]:
        cases.append("gate " + name)
        if not check_doc(d, "todo"):
            bad += 1
            print(f"FAIL cos selftest: gate missed a planted {name}")
    cases.append("gate clean row")
    if check_doc({"title": "Check a notice in Kit, not the email", "owner": "todd", "state": "next", "openedAt": "2026-10-26T07:31:00-05:00"}, "todo"):
        bad += 1
        print("FAIL cos selftest: gate refused a clean row")
    print(f"{'OK' if not bad else 'ERROR'} cos selftest: {len(cases) - bad} of {len(cases)} planted cases right")
    return not bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", choices=["brief", "review", "check-doc"])
    ap.add_argument("file", nargs="?")
    ap.add_argument("--data", default=os.path.join(ROOT, "data", "cos"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--now", default=None)
    ap.add_argument("--kind", choices=["brief", "inbox", "review", "todo"])
    ap.add_argument("--looks-done", default="")
    ap.add_argument("--added", default="")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if a.mode == "check-doc":
        if not a.file or not a.kind:
            ap.error("check-doc needs FILE and --kind")
        errs = check_doc(load_json(a.file), a.kind)
        for e in errs:
            print(f"ERROR cos check-doc: {e}")
        print(f"{'OK' if not errs else 'ERROR'} cos check-doc {a.kind}: {len(errs)} problems")
        sys.exit(1 if errs else 0)
    now = parse_iso(a.now) if a.now else dt.datetime.now(tz())
    out = a.out or a.data
    os.makedirs(out, exist_ok=True)
    if a.mode == "brief":
        looks = tuple(x.strip() for x in a.looks_done.split(",") if x.strip())
        added = tuple(x.strip() for x in a.added.split(";") if x.strip())
        agenda, text, doc, cos_doc = build_brief(a.data, ROOT, now, looks, added)
        json.dump(agenda, open(os.path.join(out, "agenda.json"), "w"), indent=1, default=str)
        open(os.path.join(out, "brief.txt"), "w").write(text)
        json.dump(doc, open(os.path.join(out, "brief_doc.json"), "w"), indent=1)
        json.dump(cos_doc, open(os.path.join(out, "cos_doc.json"), "w"), indent=1)
        errs = check_doc(doc, "brief")
        print(text)
        g = agenda["gaps"]
        print(f"{'OK' if not errs else 'ERROR'} cos brief: {len(agenda['items'])} do-now items, {agenda['nowCount']} now rows, "
              f"quiet {str(agenda['quiet']).lower()}, {len(g['refs'])} missing todo refs, {len(g['candidates'])} ask lines to judge"
              + ("; " + "; ".join(errs) if errs else ""))
        sys.exit(1 if errs else 0)
    if a.mode == "review":
        text, doc = build_review(a.data, ROOT, now)
        open(os.path.join(out, "review.md"), "w").write(text)
        json.dump(doc, open(os.path.join(out, "review_doc.json"), "w"), indent=1)
        errs = check_doc(doc, "review")
        print(text)
        print(f"{'OK' if not errs else 'ERROR'} cos review: {doc['staleCount']} stale, {doc['shippedCount']} shipped" + ("; " + "; ".join(errs) if errs else ""))
        sys.exit(1 if errs else 0)
    ap.print_help()
    sys.exit(2)


if __name__ == "__main__":
    main()
