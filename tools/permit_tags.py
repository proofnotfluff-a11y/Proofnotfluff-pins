#!/usr/bin/env python3
"""Tag GC permit leads with the trades the job will hire, on the local box (Todd, live chat, Nov 7, 2026, 5:22 am: "the
box is our work horse and we should be heavily utilizing it on value add tasks").

Each lead in permits/downstream/gc_leads.json carries a free-text scope ("Interior Remodel level 1 for sectors 3 6 and
7..."). The box reads 25 scopes a job and names the subcontractor trades the work will need. Code keeps only what it can
prove: a lead id that was in the batch, trades from the fixed list below, a reason quoted from that lead's own scope.
Public business fields only (permit scope, work type, stage); never a person.

  python3 tools/permit_tags.py make [--max 300] [--date YYYY-MM-DD] [--out DIR]   batches of untagged leads, then
                                                    python3 tools/local_job.py send DIR/*.json
  python3 tools/permit_tags.py merge [--date YYYY-MM-DD]       ok answers -> permits/downstream/scope_tags.json
  python3 tools/permit_tags.py sample [--n 20]                 random tagged leads with their scope, for a spot check
"""
import argparse
import datetime as dt
import glob
import json
import os
import random
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEADS = os.path.join(ROOT, "permits", "downstream", "gc_leads.json")
TAGS = os.path.join(ROOT, "permits", "downstream", "scope_tags.json")
LANE = os.environ.get("PNF_LOCAL_JOBS", "/home/claude/pnf-local-jobs")
TRADES = ["electrical", "plumbing", "hvac", "roofing", "drywall", "painting", "flooring", "concrete", "masonry",
          "framing", "carpentry", "windows-glass", "doors-hardware", "insulation", "demolition", "fire-protection",
          "low-voltage", "elevator", "kitchen-hood", "cabinets-millwork", "tile", "steel", "excavation", "landscaping",
          "signage", "cleaning", "none-clear"]
BATCH = 25


def leads():
    return json.load(open(LEADS, encoding="utf-8"))["leads"]


def tags():
    return json.load(open(TAGS, encoding="utf-8")) if os.path.exists(TAGS) else {"rule": __doc__.split("\n")[0], "tags": {}}


def make(maxn, date, out):
    os.makedirs(out, exist_ok=True)
    for f in glob.glob(os.path.join(out, "permits-*.json")):
        os.remove(f)
    done = tags()["tags"]
    todo = [l for l in leads() if l.get("scope") and l["lead_id"] not in done][:maxn]
    for i in range(0, len(todo), BATCH):
        part = todo[i:i + BATCH]
        rows = [{"lead_id": l["lead_id"], "work_type": l.get("work_type"), "stage": l.get("stage"),
                 "scope": str(l.get("scope"))[:400]} for l in part]
        job = {"kind": "tag", "model": "workhorse",
               "system": "You are an estimator for a US general contractor. Use only the scope text given. Never invent work the scope does not describe.",
               "prompt": "For each permit below, name the subcontractor trades this work will need, from this list only: "
                         + ", ".join(TRADES) + ". Use none-clear when the scope does not say. For each lead give the words "
                         "from its own scope (under 12 words, copied exactly) that justify the trades.",
               "input": json.dumps(rows, ensure_ascii=False),
               "schema": {"type": "object", "required": ["leads"], "additionalProperties": False, "properties": {"leads": {
                   "type": "array", "items": {"type": "object", "required": ["lead_id", "trades", "because"],
                   "additionalProperties": False, "properties": {
                       "lead_id": {"type": "string", "maxLength": 40},
                       "trades": {"type": "array", "maxItems": 8, "items": {"type": "string", "enum": TRADES}},
                       "because": {"type": "string", "maxLength": 120}}}}}},
               "max_tokens": 3500}
        name = f"permits-b{i // BATCH + 1}-tag-{date}-r1"
        json.dump(job, open(os.path.join(out, name + ".json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"permit_tags: {len(todo)} untagged leads in {(len(todo) + BATCH - 1) // BATCH} jobs in {out}")


def merge(date):
    store, scope = tags(), {l["lead_id"]: str(l.get("scope") or "") for l in leads()}
    kept = dropped = 0
    for jf in sorted(glob.glob(os.path.join(LANE, "jobs", f"permits-b*-tag-{date}-r*.json"))):
        af = os.path.join(LANE, "answers", os.path.basename(jf))
        if not os.path.exists(af):
            continue
        a = json.load(open(af, encoding="utf-8"))
        if a.get("status") != "ok":
            continue
        asked = {r["lead_id"] for r in json.loads(json.load(open(jf, encoding="utf-8"))["input"])}
        for t in (a.get("output") or {}).get("leads", []):
            lid, because = t.get("lead_id"), str(t.get("because", "")).strip().strip('"')
            tr = [x for x in t.get("trades", []) if x in TRADES]
            norm = lambda s: re.sub(r"\s+", " ", s.lower())
            if lid not in asked or not tr or not because or norm(because) not in norm(scope.get(lid, "")):
                dropped += 1
                continue
            store["tags"][lid] = {"trades": tr, "because": because, "job": os.path.basename(jf)[:-5]}
            kept += 1
    store["updated"] = dt.date.today().isoformat()
    json.dump(store, open(TAGS, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"permit_tags: kept {kept}, dropped {dropped} (id not asked, no trade, or reason not in its own scope); "
          f"{len(store['tags'])} of {len(scope)} leads tagged")
    return 0


def sample(n):
    store, by = tags()["tags"], {l["lead_id"]: l for l in leads()}
    for lid in random.sample(sorted(store), min(n, len(store))):
        print(f"{lid} | {', '.join(store[lid]['trades'])} | because: {store[lid]['because']} | scope: {str(by[lid].get('scope'))[:160]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["make", "merge", "sample"])
    ap.add_argument("--max", type=int, default=300)
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--out", default=os.path.join(os.environ.get("TMPDIR", "/tmp"), "permit-tags"))
    a = ap.parse_args()
    if a.cmd == "make":
        make(a.max, a.date, a.out)
    elif a.cmd == "merge":
        return merge(a.date)
    else:
        sample(a.n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
