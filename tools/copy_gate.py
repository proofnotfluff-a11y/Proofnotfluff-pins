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
           renders every live GC lead through each vertical's template for that lead's stage and city.
"""
import argparse
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


def fill(t, fields):
    return re.sub(r"\{(\w+)\}", lambda m: str(fields.get(m.group(1), m.group(0))), t)


def check_templates(path):
    problems, ts = [], templates(path)
    if not ts:
        return ["no templates found (### T<n> heading, Subject: line, fenced body)"], 0
    seen = set()
    for name, subj, body, stage, trade in ts:
        if stage and stage not in R.DOWNSTREAM:
            problems.append(f"{name}: Stage {stage!r} is not a downstream stage")
        v = R.TRADE_VERTICALS.get(trade)
        if v is None:
            problems.append(f"{name}: unknown Trade {trade!r}")
        elif not stage and trade != R.TRADE_DEFAULT:
            problems.append(f"{name}: a {trade} template needs a Stage line")
        elif stage and stage not in v["stages"]:
            problems.append(f"{name}: {trade} cannot use the {stage!r} stage")
        if (trade, stage) in seen:
            problems.append(f"{name}: a second {trade} template for {stage or 'any stage'!r}")
        seen.add((trade, stage))
        lead = dict(FIXTURE_LEAD, stage=stage or FIXTURE_LEAD["stage"])
        for p in R.copy_problems(fill(subj, FIXTURE_FIELDS), fill(body, FIXTURE_FIELDS), FIXTURE_FIELDS["first"], lead):
            problems.append(f"{name}: {p}")
        unknown = set(re.findall(r"\{(\w+)\}", subj + body)) - set(FIXTURE_FIELDS)
        if unknown:
            problems.append(f"{name}: unknown fields {sorted(unknown)}")
    for trade in sorted(set(R.TRADE_VERTICALS) - {tr for *_x, tr in ts}):
        problems.append(f"trade vertical {trade} has no template")
    return problems, len(ts)


def check_live(path, gc_path):
    """Every live GC lead rendered through each vertical's template for its stage must pass the gate (proves the
    templates and the display helpers work on real City names and streets, not only on the fixture). A vertical renders
    only the leads its products' cities and its stages allow. Returns (problems, leads, renders per vertical)."""
    gc = json.load(open(gc_path, encoding="utf-8"))
    ts = {(trade, stage): (subj, body) for _n, subj, body, stage, trade in templates(path)}
    problems, n, per = [], 0, {t: 0 for t in R.TRADE_VERTICALS}
    for ld in gc.get("leads", []):
        f = {"first": "Dana", "gc": R.gc_display(ld.get("gc_company")), "value": R.value_display(ld.get("valuation")),
             "kind": "office", "street": R.street_display(ld.get("address")), "zip": ld.get("zip") or ""}
        hit = False
        for trade, v in R.TRADE_VERTICALS.items():
            key = (trade, ld.get("stage"))
            if key not in ts or ld.get("city") not in {R.PRODUCTS.get(x) for x in v["products"]}:
                continue
            subj, body = ts[key]
            hit = True
            per[trade] += 1
            problems += [f"{ld['lead_id']} {trade}: {p}" for p in R.copy_problems(fill(subj, f), fill(body, f), "Dana", ld)]
        n += hit
    return problems, n, per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("drafts", nargs="?", default=DRAFTS)
    ap.add_argument("--gc", default=GC)
    ap.add_argument("--prospects", default=PROSPECTS)
    ap.add_argument("--templates", nargs="?", const=TEMPLATES, default=None)
    ap.add_argument("--live", action="store_true", help="render every lead in --gc through its stage template")
    ap.add_argument("--matches", default=os.path.join(ROOT, "data", "work", "matches.json"),
                    help="every draft's lead_id must equal its validated match (pass '' for follow-ups)")
    a = ap.parse_args()
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
    problems = R.validate_drafts(drafts, {x["lead_id"]: x for x in gc["leads"]}, {x["prospect_id"]: x for x in pr["prospects"]}, matches)
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
