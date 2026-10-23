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
             "kind": "office", "street": R.street_display(ld.get("address")), "zip": ld.get("zip") or ""}
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
    a = ap.parse_args()
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
