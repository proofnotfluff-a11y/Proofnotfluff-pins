#!/usr/bin/env python3
"""Two-Entity Schema, Timing Moat and Inbox Gates, as one CLI. Exit 0 on pass, 1 on any problem (a hard gate: a run that
gets 1 stops the stage and tells Todd; it never edits the file or this script to get past it).

  python3 tools/validate_leads.py gc [permits/downstream/gc_leads.json] [--max-age-days 8]
        Entity A: schema pnf.gc_lead.v1 and the Timing Moat Gate on every lead (downstream stage plus an adjacent
        Certificate of Occupancy or health inspection signal; upstream groundbreaking stages fail).
  python3 tools/validate_leads.py prospects [data/prospects/prospects.json]
        Entity B: schema pnf.prospect.v1 and the Inbox Gate on every row (named decision-maker on the business's own
        domain; info@, contact@, sales@, admin@, office@, dispatch@, estimating@, bids@, support@, hello@ and the rest
        of pnf_rules.ROLE_LOCALPARTS fail; free mail fails; catch-all over 10% of the file fails).
  python3 tools/validate_leads.py matches [data/work/matches.json]
        The agent's matching output: every pair points at a validated lead and a validated prospect in the same city.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pnf_rules as R  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GC = os.path.join(ROOT, "permits", "downstream", "gc_leads.json")
PROSPECTS = os.path.join(ROOT, "data", "prospects", "prospects.json")
MATCHES = os.path.join(ROOT, "data", "work", "matches.json")


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, f"{os.path.relpath(path, ROOT)} does not exist"
    except ValueError as e:
        return None, f"{os.path.relpath(path, ROOT)} is not valid JSON ({e})"


def finish(name, problems, passed):
    for p in problems[:40]:
        print(f"ERROR {name}: {p}")
    if len(problems) > 40:
        print(f"ERROR {name}: and {len(problems) - 40} more")
    if problems:
        print(f"{name}: FAIL, {len(problems)} problem{'s' if len(problems) != 1 else ''}")
        sys.exit(1)
    print(f"OK {name}: {passed}")
    sys.exit(0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=("gc", "prospects", "matches"))
    ap.add_argument("path", nargs="?")
    ap.add_argument("--max-age-days", type=int, default=None)
    ap.add_argument("--gc", default=GC)
    ap.add_argument("--prospects", default=PROSPECTS)
    a = ap.parse_args()

    if a.what == "gc":
        doc, e = load(a.path or GC)
        if e:
            finish("gc", [e], "")
        finish("gc", R.validate_gc_file(doc, a.max_age_days), f"{len(doc['leads'])} downstream GC leads pass schema and timing moat")
    if a.what == "prospects":
        doc, e = load(a.path or PROSPECTS)
        if e:
            finish("prospects", [e], "")
        rows = doc.get("prospects") or []
        problems = R.validate_prospect_file(doc)
        if not rows:
            problems.append("no prospects: import named decision-makers first (tools/prospects_import.py)")
        finish("prospects", problems, f"{len(rows)} named decision-makers pass schema and inbox gate")
    gc, e1 = load(a.gc)
    pr, e2 = load(a.prospects)
    mt, e3 = load(a.path or MATCHES)
    errs = [x for x in (e1, e2, e3) if x]
    if errs:
        finish("matches", errs, "")
    errs = R.validate_gc_file(gc) + R.validate_prospect_file(pr)
    if errs:
        finish("matches", ["inputs do not validate: " + errs[0]], "")
    leads = {x["lead_id"]: x for x in gc["leads"]}
    pros = {x["prospect_id"]: x for x in pr["prospects"]}
    finish("matches", R.validate_matches(mt, leads, pros), f"{len(mt.get('matches') or [])} matches point at validated records")


if __name__ == "__main__":
    main()
