#!/usr/bin/env python3
"""Outreach Copy Gate: the post-draft check every email passes before Todd sees it. Exit 0 on pass, 1 on any problem.

Each draft in data/work/drafts.json (schema pnf.draft.v1, written by the outreach-drafter stage) is checked against the
validated GC lead and prospect it names:
  - body under 75 words (the fixed CAN-SPAM footer the sender appends is not counted and must not be in the body),
  - no URL or domain string anywhere (http://, https://, www., .com, gumroad and the rest of pnf_rules.URL_RE),
  - no upstream phrase (broke ground, breaking ground ...), no price or subscription pitch, no em or en dash,
    no leftover placeholder bracket,
  - opens "Hi <first name>," for the named decision-maker, names the lead's general contractor and its downstream
    stage, and ends with the permission question,
  - the To address is the prospect's validated address and passes the Inbox Gate again.

Usage: python3 tools/copy_gate.py [data/work/drafts.json] [--gc permits/downstream/gc_leads.json]
                                  [--prospects data/prospects/prospects.json] [--matches data/work/matches.json]
       Follow-ups: --prospects data/prospects/followups.json --matches ''  (prospects already emailed once)
       python3 tools/copy_gate.py --templates .claude/skills/outreach-drafter/templates.md
           renders every template (each trade vertical's too) with a fixture lead and prospect and checks it the same way;
           every vertical in pnf_rules.TRADE_VERTICALS needs at least one template, and a template's Stage must be one its
           vertical allows.
       python3 tools/copy_gate.py --live
           renders every live GC lead through each vertical's template(s) for that lead's stage and city.
       python3 tools/copy_gate.py --assign [data/work/matches.json]
           prints, for each validated match, the template id the draft must use (T2-B): the template slot comes from the
           prospect's trade vertical and the lead's stage, the letter from pnf_rules.assign_variant (a follow-up keeps the
           prospect's recorded CRM variant).

Variants (Todd, Oct 22, 2026, live chat): a template may carry a 'Variant: <letter>' line (blank means A); one template
per trade vertical, stage and letter. Every draft carries 'variant' (the template id), must be that template filled in
(its fixed words unchanged), and must be the prospect's arm. Follow-ups (run with --matches '') must name a lead the
prospect has not been sent before (first_example and followup_examples).

Signal leads (Todd, Oct 22, 2026, live chat, decision 2: gate extension for license and citation signals approved; the
permit checks above are unchanged):
       python3 tools/copy_gate.py --signal-templates
           every signal product's outreach file (pnf_rules.SIGNAL_PRODUCTS, email/L1-OUTREACH.md for the licenses
           product): a first email and two follow-ups per trade, each rendered on a fixture lead and passing
           pnf_rules.signal_copy_problems (every permit copy rule, plus street, the City date, the 30-day window, the
           signal words and, for a license, the shown business name).
       python3 tools/copy_gate.py --signal-live
           every lead in permits/licenses-chicago/sample.json rendered through every license template, on the pull date.
       python3 tools/copy_gate.py --signal [data/work/signal_drafts.json] --leads data/work/signal_leads.json
                                  [--prospects ...] [--matches ...] [--send-day YYYY-MM-DD]
           signal drafts (pnf.signal_draft.v1) against a validated signal lead file; follow-ups with --matches ''.
Pest seat email (Todd, Oct 24, 2026: subject "{n} Chicago restaurant inspections cited pests this week", {n} the 7-day
count only, never the daily file's total; "extend the copy gate to check that"):
       python3 tools/copy_gate.py --pest-templates
           email/P1-PEST-SEAT.md: every step present, rendered on today's permits/inspections-chicago/daily.json and on
           planted files, passing pest_problems; planted wrong counts (the daily total, the 14-day total, a stale file, an
           area outside the week, n = 1 on the plural template, a seat line that is no longer true) must all be caught.
       python3 tools/copy_gate.py --pest [data/work/pest_drafts.json] [--prospects data/prospects/pest_prospects.json]
                                  [--send-day YYYY-MM-DD]
           pest drafts (pnf.pest_draft.v1) against today's daily.json, the seat spec and the prospects they name.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pnf_rules as R  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFTS = os.path.join(ROOT, "data", "work", "drafts.json")
GC = os.path.join(ROOT, "permits", "downstream", "gc_leads.json")
PROSPECTS = os.path.join(ROOT, "data", "prospects", "prospects.json")
TEMPLATES = os.path.join(ROOT, ".claude", "skills", "outreach-drafter", "templates.md")

FIXTURE_LEAD = {"lead_id": "chi-fixture", "city": "chicago", "gc_company": "Bartlett Cocke, LLC", "stage": "Partial Occupancy Approved",
                "address": "4100 N Hampton Dr", "valuation": 45000000, "work_type": "New construction", "scope": "school"}
FIXTURE_FIELDS = {"first": "Dana", "gc": "Bartlett Cocke", "value": "$45M", "kind": "school", "street": "N Hampton Dr",
                  "zip": "78723"}


def templates(path):
    """(name, subject, body, stage, trade) for every template block: a '### T<n>' heading, optional 'Trade:' and
    'Stage:' lines, a 'Subject:' line, then a fenced body block. No Trade line means commercial_cleaning."""
    text = open(path, encoding="utf-8").read()
    out = []
    for m in re.finditer(r"^### (T\d+[^\n]*)\n(.*?)(?=^### |^## |\Z)", text, re.S | re.M):
        name, chunk = m.group(1).strip(), m.group(2)
        subj = re.search(r"^Subject:\s*(.+)$", chunk, re.M)
        body = re.search(r"```(?:text)?\n(.*?)```", chunk, re.S)
        stage = re.search(r"^Stage:\s*(.+)$", chunk, re.M)
        trade = re.search(r"^Trade:\s*(.+)$", chunk, re.M)
        if subj and body:
            out.append((name, subj.group(1).strip(), body.group(1).strip("\n"), (stage.group(1).strip() if stage else ""),
                        trade.group(1).strip() if trade else R.TRADE_DEFAULT))
    return out


def variant_templates(path):
    """Every template block as a dict: id (T2-B), letter, name, subject, body, stage, trade. A missing Variant line is A;
    the T number comes from the '### T<n>' heading."""
    text = open(path, encoding="utf-8").read()
    out = []
    for m in re.finditer(r"^### (T(\d+)[^\n]*)\n(.*?)(?=^### |^## |\Z)", text, re.S | re.M):
        name, num, chunk = m.group(1).strip(), m.group(2), m.group(3)
        subj = re.search(r"^Subject:\s*(.+)$", chunk, re.M)
        body = re.search(r"```(?:text)?\n(.*?)```", chunk, re.S)
        if not (subj and body):
            continue
        stage = re.search(r"^Stage:\s*(.+)$", chunk, re.M)
        trade = re.search(r"^Trade:\s*(.+)$", chunk, re.M)
        var = re.search(r"^Variant:\s*(.*)$", chunk, re.M)
        letter = (var.group(1).strip() if var else "") or "A"
        out.append({"id": f"T{num}-{letter}", "letter": letter, "name": name, "subject": subj.group(1).strip(),
                    "body": body.group(1).strip("\n"), "stage": stage.group(1).strip() if stage else "",
                    "trade": trade.group(1).strip() if trade else R.TRADE_DEFAULT})
    return out


def pattern(t):
    """A template as a regex: its fixed words exact, each {field} any text on one line."""
    parts = re.split(r"\{\w+\}", t)
    return re.compile("^" + "[^\n]+?".join(re.escape(x) for x in parts) + "$", re.S)


def slot_letters(ts, trade, stage):
    return [t["letter"] for t in ts if t["trade"] == trade and t["stage"] == stage]


def variant_problems(drafts, ts, leads, prospects, followup=False):
    """Each draft: a variant id, a template for its trade and stage, the prospect's arm, the template's fixed words, and
    for a follow-up a lead the prospect has not been sent before."""
    p = []
    for d in (drafts.get("drafts") or []):
        pid = d.get("prospect_id")
        pr, ld = prospects.get(pid), leads.get(d.get("lead_id"))
        if pr is None or ld is None:
            continue
        vid = str(d.get("variant") or "")
        if not R.VARIANT_ID_RE.match(vid):
            p.append(f"draft {pid}: variant {vid!r} must be a template id like T2-B")
            continue
        trade = R.trade_of(pr)
        t = next((x for x in ts if x["id"] == vid), None)
        if t is None or t["trade"] != trade or (t["stage"] and t["stage"] != ld.get("stage")):
            p.append(f"draft {pid}: variant {vid} is not a {trade} template for {ld.get('stage')!r}")
            continue
        arm = str(pr.get("variant") or "") or R.assign_variant(pid, slot_letters(ts, trade, t["stage"]))
        if t["letter"] != arm:
            p.append(f"draft {pid}: variant {vid} is not the prospect's arm {arm}")
        if trade in R.STEP2_TRADES and "{kind}" in t["body"] and not re.search(r"\b%s\b" % re.escape(R.kind_display(ld)), d.get("body") or ""):
            p.append(f"draft {pid}: {{kind}} must be {R.kind_display(ld)!r} (pnf_rules.kind_display of the City scope)")
        if not pattern(t["body"]).match((d.get("body") or "").strip("\n")):
            p.append(f"draft {pid}: body is not template {vid} filled in (its fixed words changed)")
        if not pattern(t["subject"]).match((d.get("subject") or "").strip()):
            p.append(f"draft {pid}: subject is not template {vid}'s subject filled in")
        if followup:
            sent = {pr.get("first_example") or ""} | set(pr.get("followup_examples") or [])
            if d.get("lead_id") in sent:
                p.append(f"draft {pid}: follow-up repeats a lead this prospect was already sent")
    return p


def fill(t, fields):
    return re.sub(r"\{(\w+)\}", lambda m: str(fields.get(m.group(1), m.group(0))), t)


def check_templates(path):
    problems, ts = [], variant_templates(path)
    if not ts:
        return ["no templates found (### T<n> heading, Subject: line, fenced body)"], 0
    seen, ids = set(), set()
    for t in ts:
        name, subj, body, stage, trade = t["name"], t["subject"], t["body"], t["stage"], t["trade"]
        if not re.match(r"^[A-Z]$", t["letter"]):
            problems.append(f"{name}: Variant {t['letter']!r} must be one capital letter")
        if t["id"] in ids:
            problems.append(f"{name}: a second template with id {t['id']}")
        ids.add(t["id"])
        if stage and stage not in R.DOWNSTREAM:
            problems.append(f"{name}: Stage {stage!r} is not a downstream stage")
        v = R.TRADE_VERTICALS.get(trade)
        if v is None:
            problems.append(f"{name}: unknown Trade {trade!r}")
        elif not stage and trade != R.TRADE_DEFAULT:
            problems.append(f"{name}: a {trade} template needs a Stage line")
        elif stage and stage not in v["stages"]:
            problems.append(f"{name}: {trade} cannot use the {stage!r} stage")
        if (trade, stage, t["letter"]) in seen:
            problems.append(f"{name}: a second {trade} template for {stage or 'any stage'!r}, variant {t['letter']}")
        seen.add((trade, stage, t["letter"]))
        lead = dict(FIXTURE_LEAD, stage=stage or FIXTURE_LEAD["stage"])
        for p in R.copy_problems(fill(subj, FIXTURE_FIELDS), fill(body, FIXTURE_FIELDS), FIXTURE_FIELDS["first"], lead):
            problems.append(f"{name}: {p}")
        unknown = set(re.findall(r"\{(\w+)\}", subj + body)) - set(FIXTURE_FIELDS)
        if unknown:
            problems.append(f"{name}: unknown fields {sorted(unknown)}")
    for trade in sorted(set(R.TRADE_VERTICALS) - {t["trade"] for t in ts}):
        problems.append(f"trade vertical {trade} has no template")
    return problems, len(ts)


def check_live(path, gc_path):
    """Every live GC lead rendered through each vertical's template for its stage must pass the gate (proves the
    templates and the display helpers work on real City names and streets, not only on the fixture). A vertical renders
    only the leads pnf_rules.trade_fits allows: its products' cities, its stages, work types and valuation floor. Returns (problems, leads, renders per vertical)."""
    gc = json.load(open(gc_path, encoding="utf-8"))
    ts = {}
    for t in variant_templates(path):
        ts.setdefault((t["trade"], t["stage"]), []).append((t["subject"], t["body"]))
    problems, n, per = [], 0, {t: 0 for t in R.TRADE_VERTICALS}
    for ld in gc.get("leads", []):
        f = {"first": "Dana", "gc": R.gc_display(ld.get("gc_company")), "value": R.value_display(ld.get("valuation")),
             "kind": R.kind_display(ld), "street": R.street_display(ld.get("address")), "zip": ld.get("zip") or ""}
        hit = False
        for trade, v in R.TRADE_VERTICALS.items():
            key = (trade, ld.get("stage"))
            if key not in ts or not R.trade_fits(trade, ld):
                continue
            hit = True
            per[trade] += 1
            for subj, body in ts[key]:
                problems += [f"{ld['lead_id']} {trade}: {p}" for p in R.copy_problems(fill(subj, f), fill(body, f), "Dana", ld)]
        n += hit
    return problems, n, per


# ------------------------------------------------------------------ signal leads (Todd, Oct 22, 2026, decision 2)
# A signal product's outreach file (pnf_rules.SIGNAL_PRODUCTS[...]["templates"]) holds '### T<n>' blocks with Product,
# Kind, Trade, Step (first, followup1, followup2) and Variant lines, a Subject line and a fenced body, checked here the
# same way as the permit templates: rendered on a fixture lead of their kind, then on the live sample's real leads.
SIGNAL_FIXTURES = {
    "license": {"lead_id": "lic-fixture", "kind": "license", "business": "Stew Kitchen", "address": "4329 N Mozart St",
                "community_area": "Irving Park", "license_type": "Retail Food Establishment", "issue_date": "2026-10-16",
                "dataset": "r5kz-chrr", "record_id": "1", "source_url": "https://example.invalid/r5kz-chrr"},
    "citation": {"lead_id": "cit-fixture", "kind": "citation", "address": "1600 W 63rd St", "community_area": "West Englewood",
                 "bureau": "ELEVATOR", "description": "MAINTAIN OR REPAIR ELECT ELEVA", "citation_date": "2026-10-16", "open": True,
                 "dataset": "22u3-xenr", "record_id": "1", "source_url": "https://example.invalid/22u3-xenr"},
}
SIGNAL_FIXTURE_SEND = "2026-10-19"
SIGNAL_FIELDS = {"license": {"first", "business", "street", "date", "area"}, "citation": {"first", "street", "date", "area"}}
LICENSE_SAMPLE = os.path.join(ROOT, "permits", "licenses-chicago", "sample.json")
SIGNAL_DRAFTS = os.path.join(ROOT, "data", "work", "signal_drafts.json")
SIGNAL_LEADS = os.path.join(ROOT, "data", "work", "signal_leads.json")


def signal_fields(lead, first="Dana"):
    k = R.SIGNAL_KINDS[lead["kind"]]
    f = {"first": first, "street": R.street_display(lead.get("address")), "date": R.date_display(lead.get(k["date_field"])),
         "area": lead.get("community_area") or ""}
    if k["name_field"]:
        f["business"] = lead.get(k["name_field"]) or ""
    return f


def signal_templates(path):
    """Every '### T<n>' template block in a signal outreach file as a dict: id, letter, name, product, kind, trade, step,
    subject, body."""
    text = open(path, encoding="utf-8").read()
    out = []
    for m in re.finditer(r"^### (T(\d+)[^\n]*)\n(.*?)(?=^### |^## |\Z)", text, re.S | re.M):
        name, num, chunk = m.group(1).strip(), m.group(2), m.group(3)
        subj = re.search(r"^Subject:\s*(.+)$", chunk, re.M)
        body = re.search(r"```(?:text)?\n(.*?)```", chunk, re.S)
        if not (subj and body):
            continue
        line = lambda key: (re.search(r"^%s:\s*(.*)$" % key, chunk, re.M) or [None, ""])[1].strip()
        out.append({"id": f"T{num}-{line('Variant') or 'A'}", "letter": line("Variant") or "A", "name": name,
                    "product": line("Product"), "kind": line("Kind"), "trade": line("Trade") or R.TRADE_DEFAULT,
                    "step": line("Step") or "first", "subject": subj.group(1).strip(), "body": body.group(1).strip("\n")})
    return out


def signal_template_files():
    return {prod: os.path.join(ROOT, v["templates"]) for prod, v in R.SIGNAL_PRODUCTS.items()}


def check_signal_templates(files=None):
    """Each signal product's templates: well-formed slots, a full set of steps per trade with the same letters, ids
    unique across the permit templates too, and every template rendered on a fixture lead of its kind passing the signal
    copy check. Returns (problems, count)."""
    files = files or signal_template_files()
    problems, n = [], 0
    ids = {t["id"] for t in variant_templates(TEMPLATES)} if os.path.exists(TEMPLATES) else set()
    for prod, path in sorted(files.items()):
        sig = R.SIGNAL_PRODUCTS[prod]
        if not os.path.exists(path):
            problems.append(f"{prod}: outreach file {os.path.relpath(path, ROOT)} is missing")
            continue
        ts = signal_templates(path)
        if not ts:
            problems.append(f"{prod}: no templates found in {os.path.relpath(path, ROOT)}")
            continue
        seen = set()
        for t in ts:
            n += 1
            nm = f"{prod} {t['name']}"
            if not re.match(r"^[A-Z]$", t["letter"]):
                problems.append(f"{nm}: Variant {t['letter']!r} must be one capital letter")
            if t["id"] in ids:
                problems.append(f"{nm}: a second template with id {t['id']}")
            ids.add(t["id"])
            if t["product"] != prod:
                problems.append(f"{nm}: Product {t['product']!r} is not {prod}")
            if t["kind"] not in sig["kinds"]:
                problems.append(f"{nm}: Kind {t['kind']!r} is not one {prod} sells ({sorted(sig['kinds'])})")
                continue
            if t["trade"] not in sig["trades"]:
                problems.append(f"{nm}: Trade {t['trade']!r} does not buy {prod} ({sorted(sig['trades'])})")
            if t["step"] not in R.SIGNAL_STEPS:
                problems.append(f"{nm}: Step {t['step']!r} is not one of {list(R.SIGNAL_STEPS)}")
            if (t["trade"], t["step"], t["letter"]) in seen:
                problems.append(f"{nm}: a second {t['trade']} {t['step']} template, variant {t['letter']}")
            seen.add((t["trade"], t["step"], t["letter"]))
            unknown = set(re.findall(r"\{(\w+)\}", t["subject"] + t["body"])) - SIGNAL_FIELDS[t["kind"]]
            if unknown:
                problems.append(f"{nm}: unknown fields {sorted(unknown)}")
            lead = SIGNAL_FIXTURES[t["kind"]]
            f = signal_fields(lead)
            for p in R.signal_copy_problems(fill(t["subject"], f), fill(t["body"], f), "Dana", lead, SIGNAL_FIXTURE_SEND):
                problems.append(f"{nm}: {p}")
        for trade in sorted(sig["trades"]):
            letters = {s: sorted(l for tr, st, l in seen if tr == trade and st == s) for s in R.SIGNAL_STEPS}
            for s in R.SIGNAL_STEPS:
                if not letters[s]:
                    problems.append(f"{prod}: trade {trade} has no {s} template")
                elif letters[s] != letters["first"]:
                    problems.append(f"{prod}: trade {trade} {s} variants {letters[s]} differ from first {letters['first']}")
    return problems, n


def license_leads_from_sample(path=LICENSE_SAMPLE):
    """The committed free sample's rows as pnf.license_lead.v1 leads (business-level fields only), and its pull date."""
    d = json.load(open(path, encoding="utf-8"))
    leads = []
    for seg in (d.get("segments") or {}).values():
        for r in seg:
            key = f"{r.get('business')}|{r.get('address')}|{r.get('issued')}"
            leads.append({"lead_id": "lic-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:10], "kind": "license",
                          "business": r.get("business"), "address": R.signal_address(r.get("address")),
                          "community_area": r.get("communityArea") or "", "license_type": r.get("licenseType"),
                          "issue_date": r.get("issued"), "dataset": "r5kz-chrr", "record_id": "",
                          "source_url": (d.get("source") or {}).get("url") or ""})
    return leads, (d.get("window") or {}).get("to") or ""


def check_signal_live(files=None, sample=LICENSE_SAMPLE):
    """Every lead in the committed license sample, rendered through every license template, passes the signal copy check
    on the sample's pull date (real City names and streets, not only the fixture). Returns (problems, leads, renders)."""
    files = files or signal_template_files()
    leads, sent = license_leads_from_sample(sample)
    problems, renders = [], 0
    for prod, path in sorted(files.items()):
        if "license" not in R.SIGNAL_PRODUCTS[prod]["kinds"] or not os.path.exists(path):
            continue
        for t in signal_templates(path):
            if t["kind"] != "license":
                continue
            for ld in leads:
                renders += 1
                f = signal_fields(ld)
                problems += [f"{ld['business']} {t['id']}: {p}"
                             for p in R.signal_copy_problems(fill(t["subject"], f), fill(t["body"], f), "Dana", ld, sent)]
    return problems, len(leads), renders


def signal_variant_problems(drafts, ts, leads, prospects, followup=False):
    """Each signal draft: a template id of the prospect's product, trade and the lead's kind; the right step (first, or
    the next follow-up, at most two); the prospect's arm (fixed by id across the first-email letters); the template's
    fixed words; and for a follow-up a lead the prospect has not been sent before."""
    p = []
    for d in (drafts.get("drafts") or []):
        pid = d.get("prospect_id")
        pr, ld = prospects.get(pid), leads.get(d.get("lead_id"))
        if pr is None or ld is None:
            continue
        vid = str(d.get("variant") or "")
        if not R.VARIANT_ID_RE.match(vid):
            p.append(f"draft {pid}: variant {vid!r} must be a template id like T11-A")
            continue
        trade = R.trade_of(pr)
        t = next((x for x in ts if x["id"] == vid), None)
        if t is None or t["product"] != pr.get("product") or t["trade"] != trade or t["kind"] != ld.get("kind"):
            p.append(f"draft {pid}: variant {vid} is not a {pr.get('product')} {trade} template for a {ld.get('kind')} lead")
            continue
        done = list(pr.get("followup_examples") or [])
        if not followup:
            want = "first"
        elif len(done) >= R.MAX_FOLLOWUPS:
            p.append(f"draft {pid}: already sent {len(done)} follow-ups, the limit is {R.MAX_FOLLOWUPS}")
            continue
        else:
            want = f"followup{len(done) + 1}"
        if t["step"] != want:
            p.append(f"draft {pid}: variant {vid} is a {t['step']} template, this draft is the {want}")
        firsts = [x["letter"] for x in ts if x["product"] == t["product"] and x["trade"] == trade and x["step"] == "first"]
        arm = str(pr.get("variant") or "") or R.assign_variant(pid, firsts)
        if t["letter"] != arm:
            p.append(f"draft {pid}: variant {vid} is not the prospect's arm {arm}")
        if not pattern(t["body"]).match((d.get("body") or "").strip("\n")):
            p.append(f"draft {pid}: body is not template {vid} filled in (its fixed words changed)")
        if not pattern(t["subject"]).match((d.get("subject") or "").strip()):
            p.append(f"draft {pid}: subject is not template {vid}'s subject filled in")
        if followup and d.get("lead_id") in ({pr.get("first_example") or ""} | set(done)):
            p.append(f"draft {pid}: follow-up repeats a lead this prospect was already sent")
    return p


# ------------------------------------------------------------------ pest seat email (Todd, Oct 24, 2026)
PEST_FILE = os.path.join(ROOT, "email", "P1-PEST-SEAT.md")
PEST_DAILY = os.path.join(ROOT, "permits", "inspections-chicago", "daily.json")
PEST_DRAFTS = os.path.join(ROOT, "data", "work", "pest_drafts.json")
PEST_PROSPECTS = os.path.join(ROOT, "data", "prospects", "pest_prospects.json")
PEST_STEPS = ("first", "followup1", "followup2")
PEST_FIELDS = {"first", "n", "neighborhood", "first_subject"}


def pest_seat():
    pages = json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"]
    return next(x for x in pages if x.get("kind") == "restleads").get("seat") or {}


def pest_the(area):
    """City community areas written with "the" in a sentence: the Loop and the Side areas (the Lower West Side)."""
    return area == "Loop" or area.endswith(" Side")


def pest_n(daily):
    """The email's {n}: the 7-day count of failed or conditional Restaurant inspections that cited pests. Never the daily
    file's totals (counts.places, counts.pests), the 14-day chart total or the seat's 14-day places."""
    return int(daily["pestLast7"]["restaurantInspections"])


def pest_problems(subject, body, step, daily, seat, send_day, first=None, letter="A"):
    """Every rule the pest seat email must meet, on one filled draft."""
    p = []
    l7 = daily.get("pestLast7") or {}
    if not l7 or "restaurantInspections" not in l7:
        return ["daily.json has no pestLast7 count (rest_daily.py older than Oct 24): no pest email can be filled"]
    n = pest_n(daily)
    try:
        age = (send_day - dt.date.fromisoformat(daily["asOf"])).days
    except (KeyError, ValueError):
        age = 99
    if age < 0 or age > 1:
        p.append(f"daily.json is from {daily.get('asOf')}, {age} days before the send day: refill from this morning's file")
    m = re.search(r"\b(\d+)\b", subject or "")
    if step == "first":
        want = f"{n} Chicago restaurant inspections cited pests this week" if n != 1 else "1 Chicago restaurant inspection cited pests this week"
        if subject != want:
            p.append(f"subject must be {want!r} (n is pestLast7.restaurantInspections = {n}), got {subject!r}")
    elif not (subject or "").startswith("Re: "):
        p.append("a follow-up keeps the first email's subject as a reply (Re: ...)")
    if n == 1 and letter != "S":
        p.append("n is 1: use this step's singular template (Variant S)")
    if n != 1 and letter == "S":
        p.append(f"n is {n}: a singular template (Variant S) is for n = 1 only")
    if n < 1:
        p.append("n is 0 this week: no pest email until the City posts one")
    totals = {"counts.places": daily.get("counts", {}).get("places"), "counts.pests": daily.get("counts", {}).get("pests"),
              "the 14-day chart total": sum(x.get("pests", 0) for x in daily.get("pestByDate") or []),
              "seat.places14": (daily.get("seat") or {}).get("places14"), "pestLast7.inspections": l7.get("inspections")}
    fixed = re.sub(r"(?i)at most 3 Chicago pest|all 3 seats|last 7 days|last 90 days|last 14 days", " ", (subject or "") + " " + (body or ""))
    nums = [int(x) for x in re.findall(r"(?<![\d,.])(\d+)(?![\d,.])", fixed)]
    for k in nums:
        if k != n:
            hit = [name for name, v in totals.items() if v == k and v != n]
            p.append(f"the number {k} is not this week's count {n}" + (f" (it is {', '.join(hit)})" if hit else ""))
    if f" {n} " not in f" {body} " and not (n == 1 and " 1 " in f" {body} "):
        p.append(f"the body does not carry this week's count {n}")
    areas = set(l7.get("areas") or [])
    named = re.search(r"(?:including one in|, in) ([^,.]+)\.", body or "")
    place = re.sub(r"^the ", "", named.group(1)) if named else ""
    if not named or place not in areas or pest_the(place) != named.group(1).startswith("the "):
        p.append(f"the neighborhood {named.group(1) if named else '(none)'!r} has no pest-cited restaurant inspection this week "
                 f"(pestLast7.areas: {', '.join(sorted(areas)) or 'none'})")
    taken = int(seat.get("taken") or 0)
    if "all 3 seats" in body.lower() and taken:
        p.append(f"{taken} of 3 seats are taken: 'all 3 seats are open' is no longer true")
    if "most of them" in body and float((daily.get("seat") or {}).get("coverage14") or 0) < 50:
        p.append("phone coverage is under 50%: 'a listed phone number for most of them' is no longer true")
    w = len(R.words(body))
    if w >= R.MAX_WORDS:
        p.append(f"body is {w} words, the limit is under {R.MAX_WORDS}")
    if R.URL_RE.search(R.link_safe(subject + " " + body)):
        p.append("a link or domain in the email")
    if R.PITCH_RE.search(body) or "$" in body:
        p.append("a price or subscription pitch in a first-touch email")
    if any(d in subject + body for d in R.DASHES):
        p.append("an em or en dash")
    if re.search(r"[{}\[\]]", subject + body):
        p.append("a leftover placeholder")
    if "FOOTER" in body or R.FOOTER.splitlines()[0] + "\n" in body:
        p.append("the footer is in the body; the sender appends it")
    if first is not None and not (body or "").startswith(f"Hi {first},"):
        p.append(f"must open 'Hi {first},'")
    if not (body or "").rstrip().endswith("?"):
        p.append("must end with the permission question")
    for word in ("dirty", "filthy", "infested", "unsafe", "violator", "rodents or insects"):
        if word in (body or "").lower():
            p.append(f"the word {word!r}: the City's record, in our words, without judgment or overstatement")
    return p


def pest_fill(t, daily, first="Dana", area=None, first_subject=None):
    n = pest_n(daily)
    area = area or (sorted(daily["pestLast7"].get("areas") or ["Chicago"]))[0]
    area = re.sub(r"^the ", "", area)
    f = {"first": first, "n": n, "neighborhood": ("the " + area) if pest_the(area) else area,
         "first_subject": first_subject or f"{n} Chicago restaurant inspections cited pests this week"}
    return fill(t["subject"], f), fill(t["body"], f)


def check_pest_templates(path=PEST_FILE, daily_path=PEST_DAILY, today=None):
    """The pest templates: well formed, all three steps, each rendered on today's daily file passing pest_problems, and the
    planted wrong counts caught."""
    problems = []
    ts = signal_templates(path)
    if not ts:
        return [f"{os.path.relpath(path, ROOT)}: no templates"], 0
    steps = {t["step"] for t in ts}
    for s in PEST_STEPS:
        if s not in steps:
            problems.append(f"no {s} template")
    for t in ts:
        bad = set(re.findall(r"\{(\w+)\}", t["subject"] + t["body"])) - PEST_FIELDS
        if bad:
            problems.append(f"{t['name']}: unknown slot(s) {sorted(bad)}")
    seat = pest_seat()
    daily = json.load(open(daily_path, encoding="utf-8")) if os.path.exists(daily_path) else None
    live = daily is not None and "pestLast7" in daily
    base = daily if live else {"asOf": "2026-10-24", "counts": {"places": 48, "pests": 42}, "seat": {"places14": 42, "coverage14": 69.0},
                               "pestByDate": [{"pests": 45}], "pestLast7": {"inspections": 24, "restaurantInspections": 22, "areas": ["West Town", "Loop"]}}
    day = today or dt.date.fromisoformat(base["asOf"])
    for t in ts:
        d = base if (t["letter"] == "S") == (pest_n(base) == 1) else None
        if d is None:                                        # the other plural form: render on a planted count that fits it
            d = json.loads(json.dumps(base))
            d["pestLast7"]["restaurantInspections"] = 1 if t["letter"] == "S" else 22
            d["pestLast7"]["inspections"] = max(d["pestLast7"]["inspections"], d["pestLast7"]["restaurantInspections"])
        subj, body = pest_fill(t, d)
        for q in pest_problems(subj, body, t["step"], d, seat if live else {"taken": 0}, day, "Dana", t["letter"]):
            problems.append(f"{t['name']}: {q}")
    # planted failures the gate must catch (the rule Todd set: never the daily file's total)
    t1 = next((t for t in ts if t["step"] == "first" and t["letter"] == "A"), None)
    planted = 0
    if t1:
        P = json.loads(json.dumps(base))
        P["counts"]["places"], P["pestLast7"]["restaurantInspections"] = 48, 22
        n = 22
        cases = [
            ("daily total in the subject", t1["subject"].replace("{n}", "48"), "first", P, {"taken": 0}, day, "A"),
            ("14-day total in the body", None, "first", P, {"taken": 0}, day, "A"),
            ("stale file", None, "first", P, {"taken": 0}, day + dt.timedelta(days=3), "A"),
            ("area outside the week", "area", "first", P, {"taken": 0}, day, "A"),
            ("seat taken", None, "first", P, {"taken": 1}, day, "A"),
            ("Loop without the", None, "first", dict(P, pestLast7=dict(P["pestLast7"], areas=sorted(set(P["pestLast7"]["areas"]) | {"Loop"}))), {"taken": 0}, day, "A"),
            ("n is 1 on the plural template", None, "first", dict(P, pestLast7=dict(P["pestLast7"], restaurantInspections=1)), {"taken": 0}, day, "A"),
        ]
        for label, override, step, d, st, sd, letter in cases:
            subj, body = pest_fill(t1, d)
            if label == "daily total in the subject":
                subj = override
            elif label == "14-day total in the body":
                body = body.replace(f" {n} ", " 45 ", 1)
            elif override == "area":
                body = re.sub(r"including one in [^,.]+\.", "including one in Hegewisch Park Ridge.", body)
            elif label == "Loop without the":
                body = re.sub(r"including one in [^,.]+\.", "including one in Loop.", body)
            if not pest_problems(subj, body, step, d, st, sd, "Dana", letter):
                problems.append(f"planted case not caught: {label}")
            planted += 1
    return problems, len(ts), planted, live, pest_n(base)


def check_pest_drafts(drafts_path, prospects_path, send_day):
    try:
        drafts = json.load(open(drafts_path, encoding="utf-8"))
        pros = {x["prospect_id"]: x for x in json.load(open(prospects_path, encoding="utf-8"))["prospects"]}
        daily = json.load(open(PEST_DAILY, encoding="utf-8"))
    except (OSError, ValueError, KeyError) as e:
        return [f"cannot read inputs ({e})"], 0
    ts = {t["id"]: t for t in signal_templates(PEST_FILE)}
    seat, problems = pest_seat(), []
    if drafts.get("schema") != "pnf.pest_draft.v1":
        problems.append("schema must be pnf.pest_draft.v1")
    seen = set()
    for dft in drafts.get("drafts") or []:
        pid = dft.get("prospect_id", "?")
        pr = pros.get(pid)
        if pid in seen:
            problems.append(f"{pid}: two drafts")
        seen.add(pid)
        if pr is None:
            problems.append(f"{pid}: not in the prospect file")
            continue
        for q in R.inbox_problems(dft.get("to"), pr.get("website"), pr.get("first_name"), pr.get("last_name"),
                                  pr.get("owner_source", ""), pr.get("email_source", "")):
            problems.append(f"{pid}: {q}")
        if dft.get("to") != pr.get("email"):
            problems.append(f"{pid}: To is not the prospect's address")
        if pr.get("do_not_email") or pr.get("first_sent_at"):
            problems.append(f"{pid}: already emailed or do-not-email")
        t = ts.get(dft.get("variant"))
        if t is None:
            problems.append(f"{pid}: unknown template {dft.get('variant')!r}")
            continue
        area = (re.search(r"(?:including one in|, in) ([^,.]+)\.", dft.get("body") or "") or [None, ""])[1] or "(none)"
        subj, body = pest_fill(t, daily, pr.get("first_name"), area, dft.get("first_subject"))
        if (dft.get("subject"), dft.get("body")) != (subj, body):
            problems.append(f"{pid}: not template {t['id']} filled with this morning's count and its own neighborhood (fixed words changed)")
        for q in pest_problems(dft.get("subject"), dft.get("body"), t["step"], daily, seat, send_day, pr.get("first_name"), t["letter"]):
            problems.append(f"{pid}: {q}")
    return problems, len(drafts.get("drafts") or [])


def chicago_today():
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("America/Chicago")).date()
    except Exception:
        return dt.date.today()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("drafts", nargs="?", default=DRAFTS)
    ap.add_argument("--gc", default=GC)
    ap.add_argument("--prospects", default=PROSPECTS)
    ap.add_argument("--templates", nargs="?", const=TEMPLATES, default=None)
    ap.add_argument("--live", action="store_true", help="render every lead in --gc through its stage template")
    ap.add_argument("--matches", default=os.path.join(ROOT, "data", "work", "matches.json"),
                    help="every draft's lead_id must equal its validated match (pass '' for follow-ups)")
    ap.add_argument("--assign", nargs="?", const=os.path.join(ROOT, "data", "work", "matches.json"), default=None,
                    help="print the template id each validated match must use")
    ap.add_argument("--signal-templates", action="store_true", help="check every signal product's outreach templates")
    ap.add_argument("--signal-live", action="store_true", help="render the committed license sample through the license templates")
    ap.add_argument("--signal", nargs="?", const=SIGNAL_DRAFTS, default=None, help="check signal drafts (pnf.signal_draft.v1)")
    ap.add_argument("--leads", default=SIGNAL_LEADS, help="the validated signal lead file the signal drafts name")
    ap.add_argument("--send-day", default=None, help="YYYY-MM-DD for the 30-day window (default: today in Chicago)")
    ap.add_argument("--pest-templates", action="store_true", help="check email/P1-PEST-SEAT.md on today's daily file")
    ap.add_argument("--pest", nargs="?", const=PEST_DRAFTS, default=None, help="check pest seat drafts (pnf.pest_draft.v1)")
    a = ap.parse_args()
    if a.pest_templates:
        problems, nt, planted, live, n = check_pest_templates()
        for p in problems:
            print(f"ERROR copy: {p}")
        if problems:
            sys.exit(1)
        print(f"OK copy: {nt} pest seat templates pass on {'this morning' if live else 'a planted'} daily file (n = {n}, the 7-day "
              f"restaurant count); {planted} planted wrong counts caught")
        sys.exit(0)
    if a.pest:
        send = dt.date.fromisoformat(a.send_day) if a.send_day else chicago_today()
        pp = a.prospects if a.prospects != PROSPECTS else PEST_PROSPECTS
        problems, nd = check_pest_drafts(a.pest, pp, send)
        if not nd:
            problems.append("no drafts in the file")
        for p in problems[:60]:
            print(f"ERROR copy: {p}")
        if problems:
            print(f"copy: FAIL, {len(problems)} problems")
            sys.exit(1)
        print(f"OK copy: {nd} pest seat drafts pass (send day {send.isoformat()})")
        sys.exit(0)
    if a.signal_templates:
        problems, n = check_signal_templates()
        for p in problems:
            print(f"ERROR copy: {p}")
        if problems:
            sys.exit(1)
        print(f"OK copy: {n} signal templates for {len(R.SIGNAL_PRODUCTS)} signal product(s) pass the signal check "
              "(street, City date, 30-day window, signal words, business name)")
        sys.exit(0)
    if a.signal_live:
        problems, n, renders = check_signal_live()
        for p in problems[:40]:
            print(f"ERROR copy: {p}")
        if problems:
            sys.exit(1)
        print(f"OK copy: {n} of {n} sample license leads render through the license templates and pass ({renders} renders)")
        sys.exit(0)
    if a.signal:
        try:
            drafts = json.load(open(a.signal, encoding="utf-8"))
            leads_doc = json.load(open(a.leads, encoding="utf-8"))
            pr = json.load(open(a.prospects, encoding="utf-8"))
            send = dt.date.fromisoformat(a.send_day) if a.send_day else chicago_today()
        except (OSError, ValueError) as e:
            print(f"ERROR copy: cannot read inputs ({e})")
            sys.exit(1)
        pre = R.validate_signal_file(leads_doc) + R.validate_prospect_file(pr)
        if pre:
            print(f"ERROR copy: inputs do not validate ({pre[0]})")
            sys.exit(1)
        matches = None
        if a.matches and os.path.exists(a.matches):
            matches = {m.get("prospect_id"): m.get("lead_id") for m in json.load(open(a.matches, encoding="utf-8")).get("matches", [])}
        leads_by, pros_by = {x["lead_id"]: x for x in leads_doc["leads"]}, {x["prospect_id"]: x for x in pr["prospects"]}
        ts = [t for path in signal_template_files().values() if os.path.exists(path) for t in signal_templates(path)]
        problems = R.validate_signal_drafts(drafts, leads_by, pros_by, send, matches)
        problems += signal_variant_problems(drafts, ts, leads_by, pros_by, followup=(a.matches == ""))
        if not (drafts.get("drafts") or []):
            problems.append("no drafts in the file")
        for p in problems[:60]:
            print(f"ERROR copy: {p}")
        if problems:
            print(f"copy: FAIL, {len(problems)} problems")
            sys.exit(1)
        print(f"OK copy: {len(drafts['drafts'])} signal drafts pass (send day {send.isoformat()})")
        sys.exit(0)
    if a.assign:
        try:
            ms = json.load(open(a.assign, encoding="utf-8")).get("matches", [])
            leads = {x["lead_id"]: x for x in json.load(open(a.gc, encoding="utf-8"))["leads"]}
            pros = {x["prospect_id"]: x for x in json.load(open(a.prospects, encoding="utf-8"))["prospects"]}
        except (OSError, ValueError, KeyError) as e:
            print(f"ERROR copy: cannot read inputs ({e})")
            sys.exit(1)
        ts, bad = variant_templates(TEMPLATES), 0
        for m in ms:
            pr, ld = pros.get(m.get("prospect_id")), leads.get(m.get("lead_id"))
            if pr is None or ld is None:
                continue
            trade = R.trade_of(pr)
            slot = [t for t in ts if t["trade"] == trade and t["stage"] == ld.get("stage")]
            arm = str(pr.get("variant") or "") or R.assign_variant(pr["prospect_id"], [t["letter"] for t in slot])
            t = next((x for x in slot if x["letter"] == arm), None)
            if t is None:
                bad += 1
                print(f"ERROR copy: {pr['prospect_id']}: no {trade} template for {ld.get('stage')!r} variant {arm!r}")
            else:
                print(f"{pr['prospect_id']}\t{ld['lead_id']}\t{t['id']}")
        sys.exit(1 if bad else 0)
    if a.live:
        problems, n, per = check_live(TEMPLATES, a.gc)
        for p in problems[:40]:
            print(f"ERROR copy: {p}")
        if problems:
            sys.exit(1)
        print(f"OK copy: {n} of {n} live leads render through the templates and pass ("
              + ", ".join(f"{k} {v}" for k, v in per.items()) + ")")
        sys.exit(0)
    if a.templates:
        problems, n = check_templates(a.templates)
        for p in problems:
            print(f"ERROR copy: {p}")
        if problems:
            sys.exit(1)
        print(f"OK copy: {n} templates for {len(R.TRADE_VERTICALS)} trade verticals under {R.MAX_WORDS} words, link-free, "
              "downstream, permission-based")
        sys.exit(0)
    try:
        drafts = json.load(open(a.drafts, encoding="utf-8"))
        gc = json.load(open(a.gc, encoding="utf-8"))
        pr = json.load(open(a.prospects, encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"ERROR copy: cannot read inputs ({e})")
        sys.exit(1)
    pre = R.validate_gc_file(gc) + R.validate_prospect_file(pr)
    if pre:
        print(f"ERROR copy: inputs do not validate ({pre[0]})")
        sys.exit(1)
    matches = None
    if a.matches and os.path.exists(a.matches):
        matches = {m.get("prospect_id"): m.get("lead_id") for m in json.load(open(a.matches, encoding="utf-8")).get("matches", [])}
    leads_by, pros_by = {x["lead_id"]: x for x in gc["leads"]}, {x["prospect_id"]: x for x in pr["prospects"]}
    problems = R.validate_drafts(drafts, leads_by, pros_by, matches)
    problems += variant_problems(drafts, variant_templates(TEMPLATES), leads_by, pros_by, followup=(a.matches == ""))
    if not (drafts.get("drafts") or []):
        problems.append("no drafts in the file")
    for p in problems[:60]:
        print(f"ERROR copy: {p}")
    if problems:
        print(f"copy: FAIL, {len(problems)} problems")
        sys.exit(1)
    print(f"OK copy: {len(drafts['drafts'])} drafts pass")
    sys.exit(0)


if __name__ == "__main__":
    main()
