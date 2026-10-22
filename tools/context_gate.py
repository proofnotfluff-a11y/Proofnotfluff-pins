#!/usr/bin/env python3
"""Context Gate (Interpretable Context Methodology): what a scheduled run loads before it starts must stay small and
must not include the legacy memory ledger. Exit 0 on pass, 1 on any problem.

Layers checked (wc -c bytes):
  Layer 0  CLAUDE.md                      under 2,048 bytes
  Layer 1  coo/HANDOFF.md                 under 2,048 bytes
  Layer 2  .claude/skills/<job>/SKILL.md  under 5,120 bytes each, with the three sections
           "## Inputs (Reads)", "## Process (Executes)", "## Outputs (Writes)"
  Budget   Layer 0 + Layer 1 + any single SKILL.md under 10,240 bytes
Also fails when any areas/digital-products*.md file sits anywhere outside archive/, when an active layer tells a run to
read /areas/digital-products* (the archived ledger), or when an active layer carries an em or en dash.

Usage: python3 tools/context_gate.py [--skill <job>] [--json]
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L0, L1 = "CLAUDE.md", "coo/HANDOFF.md"
CAP_L0 = CAP_L1 = 2048
CAP_SKILL = 5120
BUDGET = 10240
SECTIONS = ("## Inputs (Reads)", "## Process (Executes)", "## Outputs (Writes)")
LEGACY = re.compile(r"(^|/)areas/digital-products(?:-plan|-rules)?\.md$")
LEGACY_REF = re.compile(r"/?areas/digital-products(?:-plan|-rules)?\.md")


def size(rel):
    p = os.path.join(ROOT, rel)
    return os.path.getsize(p) if os.path.exists(p) else None


def tracked(root=ROOT):
    try:
        out = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True).stdout
        files = [l for l in out.splitlines() if l]
    except Exception:
        files = []
    extra = [os.path.relpath(p, root) for p in glob.glob(os.path.join(root, "**", "*.md"), recursive=True)
             if "/.git/" not in p]
    return sorted(set(files) | set(extra))


def check(skill=None):
    problems, table = [], {}
    s0, s1 = size(L0), size(L1)
    for rel, s, cap in ((L0, s0, CAP_L0), (L1, s1, CAP_L1)):
        table[rel] = s
        if s is None:
            problems.append(f"{rel} is missing")
        elif s >= cap:
            problems.append(f"{rel} is {s} bytes, the cap is under {cap}")
    skills = sorted(glob.glob(os.path.join(ROOT, ".claude", "skills", "*", "SKILL.md")))
    if not skills:
        problems.append("no .claude/skills/<job>/SKILL.md stage contracts")
    names = [os.path.basename(os.path.dirname(p)) for p in skills]
    if skill and skill not in names:
        problems.append(f"skill {skill!r} has no .claude/skills/{skill}/SKILL.md")
    for p, name in zip(skills, names):
        rel = os.path.relpath(p, ROOT)
        s = os.path.getsize(p)
        table[rel] = s
        text = open(p, encoding="utf-8").read()
        if s >= CAP_SKILL:
            problems.append(f"{rel} is {s} bytes, the cap is under {CAP_SKILL}")
        for sec in SECTIONS:
            if sec not in text:
                problems.append(f"{rel} lacks the section {sec!r}")
        total = (s0 or 0) + (s1 or 0) + s
        table[f"budget:{name}"] = total
        if total >= BUDGET:
            problems.append(f"Layer 0 + Layer 1 + {rel} = {total} bytes, the budget is under {BUDGET}")
    for rel in [L0, L1] + [os.path.relpath(p, ROOT) for p in skills]:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        text = open(p, encoding="utf-8").read()
        if LEGACY_REF.search(text):
            problems.append(f"{rel} points a run at the archived legacy ledger (/areas/digital-products*.md)")
        if "\u2014" in text or "\u2013" in text:
            problems.append(f"{rel} carries an em or en dash")
    for rel in tracked():
        if LEGACY.search(rel) and not rel.startswith("archive/"):
            problems.append(f"legacy ledger file {rel} is in an active path; it belongs in archive/legacy-memory/")
    return problems, table


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    problems, table = check(a.skill)
    if a.json:
        print(json.dumps({"problems": problems, "bytes": table}, indent=1))
    for p in problems:
        print(f"ERROR context: {p}")
    if problems:
        sys.exit(1)
    worst = max(v for k, v in table.items() if k.startswith("budget:"))
    print(f"OK context: L0 {table[L0]} B, L1 {table[L1]} B, largest pre-run load {worst} of {BUDGET} B")
    sys.exit(0)


if __name__ == "__main__":
    main()
