#!/usr/bin/env python3
"""Find one named decision-maker per cleaning business with the Hunter.io API (Domain Search, then Email Verifier).

Input: a CSV with columns business, website (one row per cleaning or pressure washing business the prospect finder
already confirmed fits; export it from the CRM's candidate list). Output: a CSV in the header shape
tools/prospects_import.py reads (--source hunter). Deterministic: for each domain it keeps the personal (non-generic)
address whose position matches a decision-maker title, highest confidence first, verifies it, and writes it only when
Hunter returns valid or accept_all. Nothing is guessed and no address is built from a pattern.

Needs HUNTER_API_KEY in the environment (Todd's account; never printed, logged or committed). Without it, or when
api.hunter.io is unreachable, the script exits 1 with one line saying so.

Usage: HUNTER_API_KEY=... python3 tools/enrich_hunter.py businesses.csv --out data/prospects/hunter-YYYY-MM-DD.csv
       [--limit 50] [--pause 1.2]
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pnf_rules as R  # noqa: E402

API = "https://api.hunter.io/v2"
HEAD = ["First name", "Last name", "Position", "Email", "Email status", "Company", "Website", "Source"]


def call(path, params, key, tries=3):
    q = dict(params, api_key=key)
    url = f"{API}/{path}?{urllib.parse.urlencode(q)}"
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "ProofNotFluff"}), timeout=60) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise SystemExit("ERROR hunter: the API key was refused (HTTP %d)" % e.code)
            if e.code == 429:
                time.sleep(10 * (i + 1))
                last = "HTTP 429"
                continue
            last = f"HTTP {e.code}"
            break
        except Exception as e:
            last = type(e).__name__
            time.sleep(3 * (i + 1))
    raise RuntimeError(f"{path} failed: {last}")


def best_contact(emails, domain):
    cands = []
    for e in emails or []:
        addr = (e.get("value") or "").lower()
        on_domain = addr.endswith("@" + domain) or addr.endswith("." + domain)
        if e.get("type") != "personal" or not on_domain:
            continue
        if R.inbox_problems(addr, domain):
            continue
        if not R.DECISION_TITLE.search(e.get("position") or ""):
            continue
        if not (e.get("first_name") and e.get("last_name")):
            continue
        cands.append(e)
    cands.sort(key=lambda e: -(e.get("confidence") or 0))
    return cands[0] if cands else None


def enrich(rows, key, pause=1.2):
    """rows: dicts with business and website. Returns (found rows in HEAD shape, misses). Raises RuntimeError when the
    API fails after retries, and SystemExit when the key is refused."""
    found, misses = [], 0
    for r in rows:
        domain = R.domain_of(r.get("website") or r.get("domain") or "")
        if not domain:
            misses += 1
            continue
        try:
            ds = call("domain-search", {"domain": domain, "type": "personal", "limit": 25}, key)
        except RuntimeError as e:
            raise RuntimeError(f"{domain}: {e}")
        pick = best_contact((ds.get("data") or {}).get("emails"), domain)
        if not pick:
            misses += 1
            continue
        ver = call("email-verifier", {"email": pick["value"]}, key)
        status = ((ver.get("data") or {}).get("status") or "").lower()
        if status not in ("valid", "accept_all"):
            misses += 1
            continue
        found.append({"First name": pick.get("first_name"), "Last name": pick.get("last_name"), "Position": pick.get("position"),
                      "Email": pick["value"], "Email status": status,
                      "Company": r.get("business") or (ds.get("data") or {}).get("organization") or "",
                      "Website": domain, "Source": "hunter"})
        time.sleep(pause)
    return found, misses


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("businesses")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--pause", type=float, default=1.2)
    a = ap.parse_args()
    key = os.environ.get("HUNTER_API_KEY", "")
    if not key:
        print("ERROR hunter: HUNTER_API_KEY is not set in this environment")
        sys.exit(1)
    rows = list(csv.DictReader(open(a.businesses, newline="", encoding="utf-8-sig")))[: a.limit]
    try:
        found, misses = enrich(rows, key, a.pause)
    except RuntimeError as e:
        print(f"ERROR hunter: {e}")
        sys.exit(1)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEAD)
        w.writeheader()
        w.writerows(found)
    print(f"{'OK' if found else 'ERROR'} hunter: {len(found)} verified decision-makers from {len(rows)} businesses, {misses} without one")
    sys.exit(0 if found else 1)


if __name__ == "__main__":
    main()
