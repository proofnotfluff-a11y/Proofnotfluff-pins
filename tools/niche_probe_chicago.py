#!/usr/bin/env python3
"""Niche probe for growth-research Phase B (Todd, Oct 22, 2026 live chat): which City of Chicago signals carry enough
monthly volume to sell as a lead list. Counts and column names only; no row, address, business or person name is written.

Runs in GitHub Actions (.github/workflows/niche-probe-chicago.yml) because the cloud agents cannot reach
data.cityofchicago.org. Writes probes/niches-chicago-<date>.json:
  violations   Building Violations (22u3-xenr): last 30 and 90 days by department bureau, inspection category, status, and
               the top violation descriptions; distinct buildings (counted in the runner, never written); trade buckets
               (TRADE_BUCKETS) counted from the descriptions
  permits      Building Permits (ydr8-5enu): last 30 days by permit type, demolition permits by first contact type and cost
               band, small renovations (under $500,000) with a general contractor by cost band
  licenses     Business Licenses (r5kz-chrr): last 30 days by application type (ISSUE, C_LOC change of location ...)
  catalog      the City's data catalog searched for other candidate signals: dataset id, name, last update, columns

Usage: python3 tools/niche_probe_chicago.py            run the probe (Actions)
       python3 tools/niche_probe_chicago.py --selftest offline: the trade buckets on planted descriptions
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request

UA = {"User-Agent": "ProofNotFluff niche probe (github.com/proofnotfluff-a11y/proofnotfluff-pins)"}
PORTAL = "https://data.cityofchicago.org"
TODAY = dt.date.today()
D30 = (TODAY - dt.timedelta(days=30)).isoformat()
D90 = (TODAY - dt.timedelta(days=90)).isoformat()

# Violation descriptions grouped by the small trade that fixes them. Word matches on the City's description text only.
TRADE_BUCKETS = {
    "masonry_tuckpointing": r"\b(masonry|tuckpoint\w*|parapet|brick\w*|mortar|coping|lintel\w*|exterior wall)\b",
    "porch_stairs": r"\b(porch\w*|stair\w*|guardrail\w*|handrail\w*|deck\w*|balcon\w*)\b",
    "roof_gutter": r"\b(roof\w*|gutter\w*|downspout\w*|flashing)\b",
    "windows_doors": r"\b(window\w*|glaz\w*|sash|screens?|exit door|door\w*)\b",
    "pest_rodent": r"\b(rodent\w*|rat|rats|mice|insect\w*|roach\w*|bed ?bugs?|pest\w*|vermin|harborage)\b",
    "fire_safety": r"\b(smoke detector\w*|carbon monoxide|fire extinguisher\w*|sprinkler\w*|fire alarm\w*|fire escape\w*|exit sign\w*)\b",
    "heat_boiler": r"\b(heat\w*|boiler\w*|furnace\w*|chimney\w*|flue)\b",
    "elevator": r"\b(elevator\w*|escalator\w*|lift)\b",
    "plumbing": r"\b(plumb\w*|water heater\w*|drain\w*|sewer\w*|fixture\w*)\b",
    "electrical": r"\b(electric\w*|wiring|outlet\w*|receptacle\w*)\b",
    "paint_plaster": r"\b(paint\w*|plaster\w*|peeling|lead)\b",
    "sign": r"\b(sign|signs|signage|awning\w*|canopy)\b",
    "registration_admin": r"\b(register\w*|registration|certificate\w*|post (?:name|owner)|arrange\w* (?:for )?(?:premises )?inspection)\b",
}
CATALOG_QUERIES = ["sidewalk cafe", "elevator", "boiler", "vacant building", "liquor", "special event", "311 service requests",
                   "rodent", "scofflaw", "towing", "food inspections", "affordable rental housing"]


def buckets(description):
    """The trade buckets one violation description falls in (several can match; none means 'other')."""
    d = (description or "").lower()
    hits = [k for k, rx in TRADE_BUCKETS.items() if re.search(rx, d)]
    return hits or ["other"]


def get(url, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:  # recorded in the output, the probe goes on
        return {"error": str(e)[:300]}


def columns(dataset):
    meta = get(f"{PORTAL}/api/views/{dataset}.json")
    if "error" in meta:
        return meta
    return {"name": meta.get("name"), "rowsUpdatedAt": meta.get("rowsUpdatedAt"), "license": (meta.get("license") or {}).get("name", ""),
            "fields": [c.get("fieldName") for c in meta.get("columns", [])]}


def grouped(dataset, field, where, limit=60):
    rows = get(f"{PORTAL}/resource/{dataset}.json", {"$select": f"{field},count(*) AS n", "$where": where, "$group": field,
                                                     "$order": "n DESC", "$limit": limit})
    return rows if isinstance(rows, dict) else [{"value": r.get(field), "n": int(r.get("n", 0))} for r in rows]


def count(dataset, where):
    rows = get(f"{PORTAL}/resource/{dataset}.json", {"$select": "count(*) AS n", "$where": where})
    return rows if isinstance(rows, dict) else int((rows or [{}])[0].get("n", 0))


def violations():
    ds, out = "22u3-xenr", {"dataset": "22u3-xenr"}
    cols = columns(ds)
    out["columns"] = cols
    fields = set(cols.get("fields") or [])
    date = next((f for f in ("violation_date", "violation_status_date", "violation_last_modified_date") if f in fields), None)
    if not date:
        out["error"] = "no violation date field found"
        return out
    out["dateField"] = date
    for label, since in (("d30", D30), ("d90", D90)):
        w = f"{date}>='{since}'"
        out[label] = {"total": count(ds, w)}
        for f in ("department_bureau", "inspection_category", "violation_status"):
            if f in fields:
                out[label][f] = grouped(ds, f, w, 40)
    w30 = f"{date}>='{D30}'"
    desc = grouped(ds, "violation_description", w30, 400) if "violation_description" in fields else []
    out["d30"]["topDescriptions"] = desc[:60] if isinstance(desc, list) else desc
    if isinstance(desc, list):
        tally = {}
        for r in desc:
            for b in buckets(r["value"]):
                tally[b] = tally.get(b, 0) + r["n"]
        out["d30"]["tradeBuckets"] = dict(sorted(tally.items(), key=lambda kv: -kv[1]))
    # distinct buildings in 30 days, open violations only where a status field exists (counted here, never written)
    for label, extra in (("buildings30", ""), ("buildingsOpen30", " AND violation_status='OPEN'" if "violation_status" in fields else None)):
        if extra is None or "address" not in fields:
            continue
        rows = get(f"{PORTAL}/resource/{ds}.json", {"$select": "address", "$where": w30 + extra, "$group": "address", "$limit": 50000})
        out["d30"][label] = len(rows) if isinstance(rows, list) else rows
    return out


def permits():
    ds, out = "ydr8-5enu", {"dataset": "ydr8-5enu"}
    w30 = f"issue_date>='{D30}'"
    out["byType30"] = grouped(ds, "permit_type", w30, 40)
    demo = f"{w30} AND permit_type='PERMIT - WRECKING/DEMOLITION'"
    out["demolition30"] = {"total": count(ds, demo), "byContact1": grouped(ds, "contact_1_type", demo, 20)}
    bands = [(0, 25000), (25000, 100000), (100000, 500000), (500000, 10 ** 12)]
    out["demolition30"]["byCost"] = {f"{lo}-{hi}": count(ds, f"{demo} AND reported_cost>={lo} AND reported_cost<{hi}") for lo, hi in bands}
    small = (f"{w30} AND permit_type='PERMIT - RENOVATION/ALTERATION' AND (contact_1_type='CONTRACTOR-GENERAL CONTRACTOR' OR "
             f"contact_2_type='CONTRACTOR-GENERAL CONTRACTOR' OR contact_3_type='CONTRACTOR-GENERAL CONTRACTOR')")
    out["renovationWithGc30"] = {f"{lo}-{hi}": count(ds, f"{small} AND reported_cost>={lo} AND reported_cost<{hi}") for lo, hi in bands}
    return out


def licenses():
    ds = "r5kz-chrr"
    w30 = f"date_issued>='{D30}'"
    return {"dataset": ds, "byApplicationType30": grouped(ds, "application_type", w30, 20),
            "changeOfLocation30ByType": grouped(ds, "license_description", f"{w30} AND application_type='C_LOC'", 30)}


def catalog():
    out = {}
    for q in CATALOG_QUERIES:
        res = get("https://api.us.socrata.com/api/catalog/v1", {"domains": "data.cityofchicago.org", "q": q, "only": "dataset", "limit": 5})
        if isinstance(res, dict) and "results" in res:
            out[q] = [{"id": r["resource"].get("id"), "name": r["resource"].get("name"), "updatedAt": r["resource"].get("data_updated_at"),
                       "fields": (r["resource"].get("columns_field_name") or [])[:40]} for r in res["results"]]
        else:
            out[q] = res
    return out


def selftest():
    cases = [
        ("REPAIR EXTERIOR WALL. TUCKPOINT MASONRY", "masonry_tuckpointing", True),
        ("Repair or replace defective porch system", "porch_stairs", True),
        ("Maintain roof in sound condition and repair", "roof_gutter", True),
        ("EXTERMINATE RODENTS AND REMOVE HARBORAGE", "pest_rodent", True),
        ("Install smoke detectors on each level", "fire_safety", True),
        ("BOILER CERTIFICATE OF INSPECTION EXPIRED", "heat_boiler", True),
        ("ELEVATOR - ANNUAL INSPECTION OVERDUE", "elevator", True),
        ("Arrange for premises inspection", "registration_admin", True),
        ("Post name and address of owner", "registration_admin", True),
        ("Maintain roof in sound condition", "masonry_tuckpointing", False),   # a roof is not masonry
        ("Repair window sash", "pest_rodent", False),
        ("Replace broken elevator door", "elevator", True),
    ]
    bad = [(d, k, want) for d, k, want in cases if (k in buckets(d)) != want]
    if buckets("Something the City wrote") != ["other"]:
        bad.append(("unmatched text", "other", True))
    for b in bad:
        print("FAIL", b)
    print(f"selftest {'FAIL' if bad else 'ok'}: {len(cases) + 1 - len(bad)} of {len(cases) + 1} planted descriptions right")
    return not bad


def main():
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    out = {"ranAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "d30From": D30, "d90From": D90,
           "violations": violations(), "permits": permits(), "licenses": licenses(), "catalog": catalog()}
    os.makedirs("probes", exist_ok=True)
    path = os.path.join("probes", f"niches-chicago-{TODAY.isoformat()}.json")
    json.dump(out, open(path, "w"), indent=1)
    print(path)


if __name__ == "__main__":
    main()
