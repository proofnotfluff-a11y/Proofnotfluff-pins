#!/usr/bin/env python3
"""Overlap check for question pages (Todd, Oct 22, 2026: daily posting, no near-duplicate posts).

Compares one question spec in site/pages.json with every other question spec: the share of its own words (answer,
tables, steps, sections and FAQ answers) that sit in 8-word runs also found in another page. FAQs every page shares
word for word (same question and answer) are left out, since they are site boilerplate. Exit 1 when the share with
any one page is above the limit.

Usage: python3 tools/question_overlap.py <slug> [--limit 30]
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = 8


def words(spec, common):
    parts = list(spec.get("answer", []))
    for t in spec.get("tables", []):
        parts += t.get("intro", []) + t.get("notes", [])
        if isinstance(t.get("rows"), list):
            parts += [" ".join(r) for r in t["rows"]]
    for h, b in spec.get("steps", []):
        parts += [h, b]
    for h, paras in spec.get("sections", []):
        parts += [h] + list(paras)
    parts += [a for q, a in spec.get("faq", []) if (q, a) not in common]
    text = re.sub(r"\{[^}]*\}", " ", " ".join(parts).lower())
    return re.findall(r"[a-z0-9']+", text)


def shingles(ws):
    return {tuple(ws[i:i + N]) for i in range(len(ws) - N + 1)}


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    slug = args[0]
    limit = float(args[args.index("--limit") + 1]) if "--limit" in args else 30.0
    qs = [p for p in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if p.get("kind") == "question"]
    me = next((p for p in qs if p["slug"] == slug), None)
    if not me:
        sys.exit(f"no question page {slug}")
    faq_sets = [set(map(tuple, p.get("faq", []))) for p in qs]
    common = set.intersection(*faq_sets) if len(faq_sets) > 1 else set()
    mine = words(me, common)
    ms = shingles(mine)
    worst = 0.0
    for p in qs:
        if p["slug"] == slug:
            continue
        other = shingles(words(p, common))
        hit = [False] * len(mine)
        for i in range(len(mine) - N + 1):
            if tuple(mine[i:i + N]) in other:
                for j in range(i, i + N):
                    hit[j] = True
        share = 100.0 * sum(hit) / max(1, len(mine))
        worst = max(worst, share)
        print(f"{slug} vs {p['slug']}: {share:.1f}% of {len(mine)} words shared")
    if worst > limit:
        print(f"FAIL overlap {worst:.1f}% over {limit:.0f}%")
        sys.exit(1)
    print(f"PASS overlap {worst:.1f}% (limit {limit:.0f}%)")


if __name__ == "__main__":
    main()
