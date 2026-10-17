#!/usr/bin/env python3
"""Public-data probe for new lead-list products (Todd, Oct 17, 2026: "let's test multiple areas").

Runs in GitHub Actions (.github/workflows/data-probe.yml) because the cloud agents cannot reach the city portals.
Writes only aggregate counts and column names to probes/<date>.json: no rows, no business or person names.
"""
import datetime as dt, json, os, sys, urllib.parse, urllib.request

UA = {"User-Agent": "ProofNotFluff data probe (github.com/proofnotfluff-a11y/Proofnotfluff-pins)"}
SINCE = (dt.date.today() - dt.timedelta(days=42)).isoformat()   # six full weeks

PROBES = {
    "chicago_food_inspections_by_result_type": ("https://data.cityofchicago.org/resource/4ijn-s7e5.json",
        {"$select": "results,inspection_type,count(*)", "$where": f"inspection_date>='{SINCE}'", "$group": "results,inspection_type",
         "$order": "count(*) DESC", "$limit": 60}),
    "chicago_business_licenses_new_by_type": ("https://data.cityofchicago.org/resource/r5kz-chrr.json",
        {"$select": "license_description,count(*)", "$where": f"application_type='ISSUE' AND date_issued>='{SINCE}'",
         "$group": "license_description", "$order": "count(*) DESC", "$limit": 40}),
    "chicago_demolition_permits": ("https://data.cityofchicago.org/resource/ydr8-5enu.json",
        {"$select": "count(*)", "$where": f"permit_type='PERMIT - WRECKING/DEMOLITION' AND issue_date>='{SINCE}'"}),
    "austin_commercial_500k": ("https://data.austintexas.gov/resource/3syk-w9eu.json",
        {"$select": "count(*),count(contractor_company_name)", "$where": f"issue_date>='{SINCE}' AND total_job_valuation>=500000 AND permit_class_mapped='Commercial'"}),
    "austin_all_500k_by_class": ("https://data.austintexas.gov/resource/3syk-w9eu.json",
        {"$select": "permit_class_mapped,status_current,count(*)", "$where": f"issue_date>='{SINCE}' AND total_job_valuation>=500000",
         "$group": "permit_class_mapped,status_current", "$order": "count(*) DESC", "$limit": 40}),
    "seattle_500k": ("https://data.seattle.gov/resource/76t5-zqzr.json",
        {"$select": "count(*),count(contractorcompanyname)", "$where": f"issueddate>='{SINCE}' AND estprojectcost>=500000"}),
}
COLUMNS = {
    "chicago_food_inspections": "https://data.cityofchicago.org/api/views/4ijn-s7e5.json",
    "chicago_business_licenses": "https://data.cityofchicago.org/api/views/r5kz-chrr.json",
    "austin_permits": "https://data.austintexas.gov/api/views/3syk-w9eu.json",
    "seattle_permits": "https://data.seattle.gov/api/views/76t5-zqzr.json",
}


def get(url, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:
        return {"error": str(e)[:300]}


def main():
    out = {"ranAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "since": SINCE, "weeks": 6, "counts": {}, "columns": {}}
    for k, (url, params) in PROBES.items():
        out["counts"][k] = get(url, params)
    for k, url in COLUMNS.items():
        meta = get(url)
        out["columns"][k] = meta if "error" in meta else {
            "name": meta.get("name"), "rowsUpdatedAt": meta.get("rowsUpdatedAt"), "license": (meta.get("license") or {}).get("name", ""),
            "attribution": meta.get("attribution", ""), "fields": [c.get("fieldName") for c in meta.get("columns", [])]}
    os.makedirs("probes", exist_ok=True)
    path = os.path.join("probes", f"{dt.date.today().isoformat()}.json")
    json.dump(out, open(path, "w"), indent=1)
    print(path)


if __name__ == "__main__":
    main()
