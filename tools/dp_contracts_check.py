#!/usr/bin/env python3
"""Chicago City Contracts by Trade: the facts gate's own window on the City's records (coo/PARALLEL_BUILDS.md gate 1).

The cloud session cannot reach data.cityofchicago.org, so an independent checker that never saw the build writes the
SoQL queries it wants answered, and this runner (GitHub Actions, .github/workflows/dp_contracts_check.yml, by hand
only) asks the City's Contracts dataset (rsxa-ify5) exactly those, word for word, and commits the answers to
site/datapages/dp_contracts/check/answers.json, with the dataset's own description and update time.
Privacy holds here too: address, city, state and ZIP can never be selected, and any vendor_name in an answer passes the
same business-name test as the page (a name that does not read as a business comes back as "Name withheld").

Usage: QUERIES='[{"name": "...", "params": {"$where": "...", "$select": "..."}}]' python3 tools/dp_contracts_check.py
       python3 tools/dp_contracts_check.py --selftest
"""
import datetime as dt, json, os, re, sys, urllib.parse
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dp_contracts_data as DD

OUT = os.path.join(DD.OUT, "check")
BLOCKED = re.compile(r"address|\bcity\b|\bstate\b|\bzip\b|vendor_id", re.I)


def safe_params(p):
    p = {k: str(v) for k, v in p.items() if k in ("$select", "$where", "$group", "$order", "$limit", "$offset", "$having")}
    sel = p.get("$select", "")
    if not sel or sel.strip() == "*":
        p["$select"] = ",".join(DD.FIELDS)
    for k in ("$select", "$where", "$group", "$order", "$having"):
        if BLOCKED.search(p.get(k, "")):
            raise SystemExit(f"blocked column in {k}: address, city, state, zip and vendor_id are never read")
    p.setdefault("$limit", "5000")
    return p


def scrub(rows):
    for r in rows:
        for k in list(r):
            if BLOCKED.search(k):
                del r[k]
        if "vendor_name" in r:
            r["vendor_name"] = DD.vendor(r["vendor_name"])
    return rows


def main():
    qs = json.loads(os.environ.get("QUERIES") or "[]")
    meta = DD.get(f"{DD.PORTAL}/api/views/{DD.DATASET}.json")
    out = {"askedAt": dt.datetime.now(ZoneInfo("America/Chicago")).isoformat(timespec="seconds"),
           "dataset": {"url": DD.DATASET_PAGE, "name": meta.get("name"), "description": meta.get("description"),
                       "rowsUpdatedAt": dt.datetime.fromtimestamp(meta.get("rowsUpdatedAt") or 0, ZoneInfo("America/Chicago")).isoformat(timespec="seconds"),
                       "columns": [c.get("fieldName") for c in meta.get("columns", [])]},
           "answers": []}
    for q in qs[:40]:
        p = safe_params(q.get("params") or {})
        try:
            rows = scrub(DD.get(f"{DD.PORTAL}/resource/{DD.DATASET}.json?" + urllib.parse.urlencode(p), tries=2))
            out["answers"].append({"name": q.get("name"), "params": p, "rows": rows})
        except SystemExit as e:
            out["answers"].append({"name": q.get("name"), "params": p, "error": str(e)})
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, "answers.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"{len(out['answers'])} answers")


def selftest():
    assert safe_params({"$where": "x = 1"})["$select"] == ",".join(DD.FIELDS)
    for bad in ({"$select": "zip"}, {"$select": "address_1"}, {"$where": "city = 'X'"}, {"$group": "state"}):
        try:
            safe_params(bad); raise AssertionError(bad)
        except SystemExit:
            pass
    r = scrub([{"vendor_name": "JOHN SMITH", "zip": "60601", "award_amount": "1"}])[0]
    assert r == {"vendor_name": "Name withheld", "award_amount": "1"}, r
    print("dp_contracts_check selftest: ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
