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
       python3 tools/copy_gate.py --templates .claude/skills/outreach-drafter/SKILL.md
           renders every template in the skill with a fixture lead and prospect and checks it the same way.
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
SKILL = os.path.join(ROOT, ".claude", "skills", "outreach-drafter", "SKILL.md")

FIXTURE_LEAD = {"lead_id": "chi-fixture", "city": "chicago", "gc_company": "Bartlett Cocke, LLC", "stage": "Partial Occupancy Approved",
                "address": "4100 N Hampton Dr", "valuation": 45000000, "work_type": "New construction", "scope": "school"}
FIXTURE_FIELDS = {"first": "Dana", "gc": "Bartlett Cocke", "value": "$45M", "kind": "school", "street": "N Hampton Dr",
                  "zip": "78723"}


def templates(path):
    """(name, subject, body) for every template block in the skill: a '### T<n>' heading, a 'Subject:' line, then a
    fenced body block."""
    text = open(path, encoding="utf-8").read()
    out = []
    for m in re.finditer(r"^### (T\d+[^\n]*)\n(.*?)(?=^### |^## |\Z)", text, re.S | re.M):
        name, chunk = m.group(1).strip(), m.group(2)
        subj = re.search(r"^Subject:\s*(.+)$", chunk, re.M)
        body = re.search(r"```(?:text)?\n(.*?)```", chunk, re.S)
        stage = re.search(r"^Stage:\s*(.+)$", chunk, re.M)
        if subj and body:
            out.append((name, subj.group(1).strip(), body.group(1).strip("\n"), (stage.group(1).strip() if stage else "")))
    return out


def fill(t, fields):
    return re.sub(r"\{(\w+)\}", lambda m: str(fields.get(m.group(1), m.group(0))), t)


def check_templates(path):
    problems, ts = [], templates(path)
    if not ts:
        return ["no templates found (### T<n> heading, Subject: line, fenced body)"], 0
    for name, subj, body, stage in ts:
        if stage and stage not in R.DOWNSTREAM:
            problems.append(f"{name}: Stage {stage!r} is not a downstream stage")
        lead = dict(FIXTURE_LEAD, stage=stage or FIXTURE_LEAD["stage"])
        for p in R.copy_problems(fill(subj, FIXTURE_FIELDS), fill(body, FIXTURE_FIELDS), FIXTURE_FIELDS["first"], lead):
            problems.append(f"{name}: {p}")
        unknown = set(re.findall(r"\{(\w+)\}", subj + body)) - set(FIXTURE_FIELDS)
        if unknown:
            problems.append(f"{name}: unknown fields {sorted(unknown)}")
    return problems, len(ts)


def check_live(skill, gc_path):
    """Every live GC lead rendered through its stage's template must pass the gate (proves the templates and the
    display helpers work on real City names and streets, not only on the fixture)."""
    gc = json.load(open(gc_path, encoding="utf-8"))
    ts = {stage: (subj, body) for _n, subj, body, stage in templates(skill)}
    problems, n = [], 0
    for ld in gc.get("leads", []):
        if ld.get("stage") not in ts:
            continue
        subj, body = ts[ld["stage"]]
        f = {"first": "Dana", "gc": R.gc_display(ld.get("gc_company")), "value": R.value_display(ld.get("valuation")),
             "kind": "office", "street": R.street_display(ld.get("address")), "zip": ld.get("zip") or ""}
        n += 1
        problems += [f"{ld['lead_id']}: {p}" for p in R.copy_problems(fill(subj, f), fill(body, f), "Dana", ld)]
    return problems, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("drafts", nargs="?", default=DRAFTS)
    ap.add_argument("--gc", default=GC)
    ap.add_argument("--prospects", default=PROSPECTS)
    ap.add_argument("--templates", nargs="?", const=SKILL, default=None)
    ap.add_argument("--live", action="store_true", help="render every lead in --gc through its stage template")
    ap.add_argument("--matches", default=os.path.join(ROOT, "data", "work", "matches.json"),
                    help="every draft's lead_id must equal its validated match (pass '' for follow-ups)")
    a = ap.parse_args()
    if a.live:
        problems, n = check_live(SKILL, a.gc)
        for p in problems[:40]:
            print(f"ERROR copy: {p}")
        if problems:
            sys.exit(1)
        print(f"OK copy: {n} of {n} live leads render through the templates and pass")
        sys.exit(0)
    if a.templates:
        problems, n = check_templates(a.templates)
        for p in problems:
            print(f"ERROR copy: {p}")
        if problems:
            sys.exit(1)
        print(f"OK copy: {n} templates under {R.MAX_WORDS} words, link-free, downstream, permission-based")
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
