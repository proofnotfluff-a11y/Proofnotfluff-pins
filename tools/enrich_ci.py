#!/usr/bin/env python3
"""GitHub-native decision-maker enrichment (runs in .github/workflows/prospect-enrichment.yml).

Input: prospects/businesses.json (schema pnf.business.v1, business-level fields only, committed by the prospect-matching
run): {"businesses": [{prospect_id, product, business, website, trade_vertical}]}. trade_vertical is optional (blank
means commercial_cleaning) and rides onto each sealed prospect by website domain.
Sources, in order, for each business that has no decision-maker yet:
  1. Hunter (HUNTER_API_KEY secret): Domain Search plus Email Verifier (tools/enrich_hunter.py)
  2. Apollo (APOLLO_API_KEY secret): People Search plus People Match (tools/enrich_apollo.py)
  3. Local CSV drops data/enrichment/<product>-*.csv (gitignored; Apollo, Hunter or Clay export headers), for runs on
     a machine where Todd dropped a file
Every row goes through tools/prospects_import.to_prospect and the Inbox Gate. The validated pnf.prospect.v1 file is
sealed with tools/data_box.py (PNF_DATA_KEY secret) to prospects/enriched.sealed.json; the plain file never leaves the
runner. Output on stdout is counts only: no name or address is ever printed.

Exit 0 when the sealed box was written; 1 when PNF_DATA_KEY is missing, no source exists, an API fails, or the result
fails validation.

Usage: python3 tools/enrich_ci.py [--businesses prospects/businesses.json] [--out prospects/enriched.sealed.json]
                                  [--limit 50]
"""
import argparse
import csv
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data_box  # noqa: E402
import enrich_apollo  # noqa: E402
import enrich_hunter  # noqa: E402
import pnf_rules as R  # noqa: E402
import prospects_import as PI  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUSINESSES = os.path.join(ROOT, "prospects", "businesses.json")
OUT = os.path.join(ROOT, "prospects", "enriched.sealed.json")
DROPS = os.path.join(ROOT, "data", "enrichment")
BUSINESS_KEYS = {"prospect_id", "product", "business", "website", "trade_vertical"}


def validate_businesses(doc):
    p = []
    if not isinstance(doc, dict) or doc.get("schema") != "pnf.business.v1" or not isinstance(doc.get("businesses"), list):
        return ["businesses file: schema must be pnf.business.v1 with a businesses list"]
    for b in doc["businesses"]:
        extra = set(b) - BUSINESS_KEYS
        if extra:
            p.append(f"{b.get('prospect_id')}: business-level fields only, found {sorted(extra)}")
        if b.get("product") not in R.PRODUCTS:
            p.append(f"{b.get('prospect_id')}: unknown product")
        else:
            p += [f"{b.get('prospect_id')}: {m}" for m in R.trade_problems(b["product"], R.trade_of(b))]
        if not R.domain_of(b.get("website")):
            p.append(f"{b.get('prospect_id')}: no website")
        if "@" in json.dumps(b):
            p.append(f"{b.get('prospect_id')}: an email address in a business-level file")
    return p


def to_prospects(rows, product, source):
    kept, rejected = {}, 0
    for row in rows:
        p = PI.to_prospect(PI.map_row(row), product, source)
        if R.validate_prospect(p) or p["prospect_id"] in kept:
            rejected += 1
            continue
        kept[p["prospect_id"]] = p
    return kept, rejected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--businesses", default=BUSINESSES)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--limit", type=int, default=50)
    a = ap.parse_args()
    key = data_box.passphrase()   # exits 1 before any paid API call when the box cannot be sealed
    hunter, apollo = os.environ.get("HUNTER_API_KEY", ""), os.environ.get("APOLLO_API_KEY", "")
    drops = sorted(glob.glob(os.path.join(DROPS, "*.csv")))
    if not (hunter or apollo or drops):
        print("ERROR enrich: no source (set the HUNTER_API_KEY or APOLLO_API_KEY secret, or drop CSVs in data/enrichment/)")
        sys.exit(1)
    try:
        doc = json.load(open(a.businesses, encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"ERROR enrich: cannot read {a.businesses} ({type(e).__name__})")
        sys.exit(1)
    probs = validate_businesses(doc)
    if probs:
        for p in probs[:20]:
            print(f"ERROR enrich: {p}")
        sys.exit(1)

    by_product = {}
    for b in doc["businesses"][: a.limit]:
        by_product.setdefault(b["product"], []).append(b)
    found, counts = {}, {"businesses": sum(len(v) for v in by_product.values()), "hunter": 0, "apollo": 0, "csv": 0, "rejected": 0}
    try:
        for product, rows in by_product.items():
            todo = list(rows)
            for name, k, mod in (("hunter", hunter, enrich_hunter), ("apollo", apollo, enrich_apollo)):
                if not k or not todo:
                    continue
                got, _miss = mod.enrich(todo, k)
                kept, rej = to_prospects(got, product, name)
                counts[name] += len(kept)
                counts["rejected"] += rej
                found.update(kept)
                done = {p["website_domain"] for p in kept.values()}
                todo = [b for b in todo if R.domain_of(b["website"]) not in done]
    except RuntimeError as e:
        print(f"ERROR enrich: an API call failed ({str(e).split(':')[-1].strip()})")
        sys.exit(1)
    for path in drops:
        product = next((p for p in R.PRODUCTS if os.path.basename(path).startswith(p)), None)
        if not product:
            print(f"ERROR enrich: {os.path.basename(path)} must start with a product key ({', '.join(sorted(R.PRODUCTS))})")
            sys.exit(1)
        with open(path, newline="", encoding="utf-8-sig") as f:
            kept, rej = to_prospects(list(csv.DictReader(f)), product, "manual")
        kept = {k: v for k, v in kept.items() if k not in found}
        counts["csv"] += len(kept)
        counts["rejected"] += rej
        found.update(kept)

    trade = {(b["product"], R.domain_of(b["website"])): R.trade_of(b) for b in doc["businesses"]}
    for x in found.values():
        x["trade_vertical"] = trade.get((x["product"], x["website_domain"]), R.TRADE_DEFAULT)
    out = {"schema": "pnf.prospect.v1", "prospects": sorted(found.values(), key=lambda x: x["prospect_id"])}
    probs = R.validate_prospect_file(out)
    if probs:
        print(f"ERROR enrich: the result fails validation ({len(probs)} problems; first: {probs[0].split(':')[-1].strip()})")
        sys.exit(1)
    box = data_box.seal(json.dumps(out).encode("utf-8"), key)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(box, f, indent=1)
        f.write("\n")
    print(f"OK enrich: {len(out['prospects'])} named decision-makers sealed from {counts['businesses']} businesses "
          f"(hunter {counts['hunter']}, apollo {counts['apollo']}, csv {counts['csv']}, rejected {counts['rejected']})")
    sys.exit(0)


if __name__ == "__main__":
    main()
