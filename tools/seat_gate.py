#!/usr/bin/env python3
"""The copy gate for the area seat emails (email/S1-AREA-SEAT.md; Todd, Oct 26, 2026). tools/copy_gate.py --seat-templates
calls check_seat_templates here, and tools/check_repo.py runs that on every push and preflight.

One filled draft passes seat_problems when it meets every cleaning cold email rule (pnf_rules.copy_problems) and:
  - its lead is a Chicago downstream lead whose community area (permits/downstream/gc_areas.json) is in the seat it names
  - that seat is not held (site/area_seats.json), and "still open" appears only while it is not
  - {open} is that seat's open count in permits/chicago/area_week.json, at most 8 days old on the send day, and no other
    count appears (the lead's value, its street's numbers and "5 newest" aside)
  - the subject is "Final clean on <street>" on a first email and "Re: <first subject>" on a follow-up
"""
import datetime as dt, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
import pnf_rules as R  # noqa: E402
import area_seats as A  # noqa: E402

SEAT_FILE = os.path.join(ROOT, "email", "S1-AREA-SEAT.md")
GC = os.path.join(ROOT, "permits", "downstream", "gc_leads.json")
GC_AREAS = os.path.join(ROOT, "permits", "downstream", "gc_areas.json")
MAX_AGE = 8


def templates(path=SEAT_FILE):
    import copy_gate
    out = copy_gate.signal_templates(path)
    text = open(path, encoding="utf-8").read()
    for t in out:   # the Stage line, which signal_templates does not read
        m = re.search(r"^### %s\n(.*?)(?=^### |\Z)" % re.escape(t["name"]), text, re.S | re.M)
        st = re.search(r"^Stage:\s*(.+)$", m.group(1), re.M) if m else None
        t["stage"] = st.group(1).strip() if st else ""
    return out


def fields(lead, seat, week, first="Dana", first_subject=None):
    return {"first": first, "gc": R.gc_display(lead.get("gc_company")), "value": R.value_display(lead.get("valuation")),
            "kind": R.kind_display(lead), "street": R.street_display(lead.get("address")), "area": seat["name"],
            "open": week["open"], "first_subject": first_subject or f"Final clean on {R.street_display(lead.get('address'))}"}


def fill(text, f):
    return re.sub(r"\{(\w+)\}", lambda m: str(f.get(m.group(1), m.group(0))), text)


def seat_problems(subject, body, step, lead, area_of_lead, seat, cfg, week_doc, send_day, first="Dana", first_subject=None):
    p = []
    lead_for_rules = lead if lead is not None else None
    p += R.copy_problems(subject, body, first, lead_for_rules)
    held = set(cfg.get("held", []))
    if seat["slug"] in held:
        p.append(f"the {seat['name']} seat is held: no email may offer it or name its jobs")
    if lead is not None:
        if lead.get("city") != "chicago":
            p.append("a seat email names a Chicago lead only")
        if not area_of_lead:
            p.append(f"{lead.get('lead_id')}: no community area on file (gc_areas.json), so its seat cannot be checked")
        elif A.territory_of(area_of_lead, cfg) != seat["slug"]:
            p.append(f"{lead.get('lead_id')} is in {area_of_lead}, not in the {seat['name']} seat")
    if f"our {seat['name']} area" not in body:
        p.append(f"the body must name the seat as 'our {seat['name']} area'" if step != "third" else "")
    try:
        age = (send_day - dt.date.fromisoformat(week_doc["fetchedAt"][:10])).days
    except (KeyError, ValueError):
        age = 99
    wk = next((t for t in week_doc.get("territories", []) if t["slug"] == seat["slug"]), None)
    if step == "first":
        if wk is None:
            p.append(f"area_week.json has no count for {seat['slug']}")
        elif age < 0 or age > MAX_AGE:
            p.append(f"area_week.json is {age} days old on the send day: refill from this week's list")
        want = f"Final clean on {R.street_display((lead or {}).get('address'))}"
        if subject != want:
            p.append(f"subject must be {want!r}, got {subject!r}")
    elif not (subject or "").startswith("Re: "):
        p.append("a follow-up keeps the first email's subject as a reply (Re: ...)")
    if "still open" in body and seat["slug"] in held:
        p.append("'still open' is no longer true")
    # every number in the body is the seat's open count, except the lead's value, its street and "5 newest"
    rest = body
    if lead is not None:
        rest = rest.replace(R.value_display(lead.get("valuation")), " ").replace(R.street_display(lead.get("address")), " ")
    rest = re.sub(r"\b5 newest\b", " ", rest)
    nums = [int(x) for x in re.findall(r"(?<![\d,.$])(\d+)(?![\d,.])", rest)]
    for k in nums:
        if wk is None or k != wk["open"]:
            p.append(f"the number {k} is not the {seat['name']} seat's open count ({wk['open'] if wk else 'none'})")
    if step == "first" and wk is not None and str(wk["open"]) not in body:
        p.append(f"the body does not carry the seat's open count {wk['open']}")
    return [x for x in p if x]


def check_seat_templates(path=SEAT_FILE, today=None):
    """Well formed (all three steps, a first email for each downstream stage the cleaning list uses), each rendered on a
    fixture and on every live Chicago lead with a community area passing seat_problems, and planted wrong drafts caught.
    Returns (problems, templates, planted caught, live renders)."""
    today = today or dt.date.today()
    ts = templates(path)
    probs = []
    if not ts:
        return [f"{os.path.relpath(path, ROOT)}: no templates"], 0, 0, 0
    steps = {t["step"] for t in ts}
    for s in ("first", "second", "third"):
        if s not in steps:
            probs.append(f"no {s} step template")
    for st in ("Partial Occupancy Approved", "Inspections Under Way", "Certificate of Occupancy Pending"):
        if not any(t["step"] == "first" and t["stage"] == st for t in ts):
            probs.append(f"no first email for {st}")
    cfg = A.load()
    week_doc = json.load(open(A.WEEK)) if os.path.exists(A.WEEK) else {"fetchedAt": today.isoformat(), "territories": []}
    send = dt.date.fromisoformat(week_doc["fetchedAt"][:10])
    seat0 = cfg["territories"][0]
    wk0 = next((t for t in week_doc["territories"] if t["slug"] == seat0["slug"]), {"slug": seat0["slug"], "open": 170})
    if not week_doc["territories"]:
        week_doc = dict(week_doc, territories=[wk0])
    fix = {"lead_id": "chi-fixture", "city": "chicago", "gc_company": "Bartlett Cocke, LLC", "address": "100 W Randolph St",
           "valuation": 45000000, "work_type": "New construction", "scope": "office"}
    for t in ts:
        lead = dict(fix, stage=t["stage"]) if t["stage"] else None
        f = fields(dict(fix, stage=t["stage"] or "Inspections Under Way"), seat0, wk0)
        subj, body = fill(t["subject"], f), fill(t["body"], f)
        probs += [f"{t['name']} (fixture): {x}" for x in
                  seat_problems(subj, body, t["step"], lead, "Loop" if lead else "", seat0, cfg, week_doc, send)]
        unknown = set(re.findall(r"\{(\w+)\}", t["subject"] + t["body"])) - set(f)
        if unknown:
            probs.append(f"{t['name']}: unknown fields {sorted(unknown)}")
    # live: every Chicago downstream lead with an area, through the first and second templates for its stage
    live = 0
    if os.path.exists(GC) and os.path.exists(GC_AREAS):
        areas = json.load(open(GC_AREAS))["areas"]
        for ld in json.load(open(GC))["leads"]:
            ca = areas.get(ld["lead_id"])
            if ld.get("city") != "chicago" or not ca:
                continue
            seat = next((x for x in cfg["territories"] if x["slug"] == A.territory_of(ca, cfg)), None)
            wk = next((x for x in week_doc["territories"] if seat and x["slug"] == seat["slug"]), None)
            if not seat or not wk or seat["slug"] in set(cfg.get("held", [])):
                continue
            for t in ts:
                if t["stage"] != ld.get("stage"):
                    continue
                f = fields(ld, seat, wk)
                subj, body = fill(t["subject"], f), fill(t["body"], f)
                probs += [f"{ld['lead_id']} {t['name']}: {x}" for x in
                          seat_problems(subj, body, t["step"], ld, ca, seat, cfg, week_doc, send, first_subject=f["first_subject"])]
                live += 1
    # planted wrong drafts, each must be caught
    first = next(t for t in ts if t["step"] == "first" and t["stage"] == "Partial Occupancy Approved")
    ld = dict(fix, stage="Partial Occupancy Approved")
    f = fields(ld, seat0, wk0)
    good_s, good_b = fill(first["subject"], f), fill(first["body"], f)
    other = next((x for x in cfg["territories"] if x["slug"] != seat0["slug"]), seat0)
    planted = [
        ("wrong open count", good_s, good_b.replace(f"{wk0['open']} open jobs", f"{wk0['open'] + 7} open jobs"), "Loop", seat0, cfg, week_doc, send),
        ("lead outside the seat", good_s, good_b, "Hyde Park", seat0, cfg, week_doc, send),
        ("held seat", good_s, good_b, "Loop", seat0, dict(cfg, held=[seat0["slug"]]), week_doc, send),
        ("stale counts", good_s, good_b, "Loop", seat0, cfg, week_doc, send + dt.timedelta(days=MAX_AGE + 1)),
        ("other seat named", good_s, good_b.replace(seat0["name"], other["name"]), "Loop", seat0, cfg, week_doc, send),
        ("a price", good_s, good_b.replace("Want its", "It is $149 a month. Want its"), "Loop", seat0, cfg, week_doc, send),
        ("a link", good_s, good_b.replace("judge it?", "judge it at proofnotfluff.com?"), "Loop", seat0, cfg, week_doc, send),
        ("wrong subject", "Leads for you", good_b, "Loop", seat0, cfg, week_doc, send),
        ("no area on file", good_s, good_b, "", seat0, cfg, week_doc, send),
        ("an extra count", good_s, good_b.replace("this week,", "this week, 12 near finish,"), "Loop", seat0, cfg, week_doc, send),
    ]
    caught = 0
    for name, s_, b_, ca, seat, c_, w_, day in planted:
        if seat_problems(s_, b_, "first", ld, ca, seat, c_, w_, day):
            caught += 1
        else:
            probs.append(f"planted case not caught: {name}")
    if seat_problems(good_s, good_b, "first", ld, "Loop", seat0, cfg, week_doc, send):
        probs.append("the planted good draft fails: " + "; ".join(seat_problems(good_s, good_b, "first", ld, "Loop", seat0, cfg, week_doc, send)))
    return probs, len(ts), caught, live


if __name__ == "__main__":
    pr, n, c, live = check_seat_templates()
    for x in pr:
        print(f"ERROR copy: {x}")
    if pr:
        sys.exit(1)
    print(f"OK copy: {n} area seat templates pass; {live} live renders; {c} planted wrong drafts caught")
