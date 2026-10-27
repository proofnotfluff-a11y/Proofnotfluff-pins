#!/usr/bin/env python3
"""Source check for build B8 (free pages chicago-basement-flooding and chicago-repair-demand; Todd's go Oct 27, 2026,
coo/PARALLEL_BUILDS.md). Runs in GitHub Actions because the cloud agents cannot reach data.cityofchicago.org.

Writes only metadata and counts, never a row:
  site/datapages/dp_flooding/source-check.json   311 dataset columns, description, every water, sewer, basement or
                                                 flood request type with its monthly counts for 12 months
  site/datapages/dp_repairs/source-check.json    Building Violations columns, description and notes, counts by
                                                 description, code and bureau for 12 months, missing location share
  site/datapages/dp_repairs/city-terms.txt       the City's data terms page as text, for the Legal desk to read word for word

Usage: python3 tools/dp_probe_b8.py
"""
import datetime as dt, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from permits_chicago import get, terms_text, TERMS_URL  # noqa: E402

PORTAL = "https://data.cityofchicago.org"
WORDS = re.compile(r"WATER|SEWER|BASEMENT|FLOOD|DRAIN|CATCH BASIN|MANHOLE", re.I)


def months_back(n):
    t = dt.date.today().replace(day=1)
    out = []
    for _ in range(n):
        prev = (t - dt.timedelta(days=1)).replace(day=1)
        out.append((prev, t))
        t = prev
    return out[::-1]


def meta(ds):
    m = get(f"{PORTAL}/api/views/{ds}.json")
    return {"name": m.get("name"), "description": m.get("description"), "attribution": m.get("attribution"),
            "attributionLink": m.get("attributionLink"), "license": m.get("license"), "category": m.get("category"),
            "rowsUpdatedAt": m.get("rowsUpdatedAt"), "metadata": {k: v for k, v in (m.get("metadata") or {}).items() if k in ("custom_fields", "rowLabel")},
            "columns": [{"field": c.get("fieldName"), "name": c.get("name"), "type": c.get("dataTypeName"), "description": c.get("description")}
                        for c in m.get("columns", [])]}


def flooding():
    out = {"checkedAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "dataset": "v6vf-nfxy",
           "meta": meta("v6vf-nfxy"), "types": {}, "errors": []}
    api = f"{PORTAL}/resource/v6vf-nfxy.json"
    for a, b in months_back(12):
        try:
            rows = get(api, {"$select": "sr_type, sr_short_code, count(*) AS n",
                             "$where": f"created_date >= '{a}T00:00:00' AND created_date < '{b}T00:00:00'",
                             "$group": "sr_type, sr_short_code", "$limit": 2000})
        except SystemExit as e:
            out["errors"].append(f"{a}: {e}")
            continue
        for r in rows:
            t = r.get("sr_type") or ""
            if WORDS.search(t):
                x = out["types"].setdefault(t, {"codes": [], "months": {}})
                if r.get("sr_short_code") and r["sr_short_code"] not in x["codes"]:
                    x["codes"].append(r["sr_short_code"])
                x["months"][str(a)[:7]] = x["months"].get(str(a)[:7], 0) + int(float(r.get("n") or 0))
    for t, x in out["types"].items():
        try:
            r = get(api, {"$select": "min(created_date) AS first, count(*) AS n", "$where": f"sr_type = '{t}'"})
            x["first"], x["allTime"] = r[0].get("first"), int(float(r[0].get("n") or 0))
        except SystemExit as e:
            x["first"] = f"error: {e}"
        try:
            r = get(api, {"$select": "count(*) AS n", "$where": f"sr_type = '{t}' AND created_date >= '{months_back(1)[0][0]}T00:00:00' AND community_area IS NULL"})
            x["noAreaLastMonth"] = int(float(r[0].get("n") or 0))
        except SystemExit as e:
            x["noAreaLastMonth"] = f"error: {e}"
    return out


def repairs():
    out = {"checkedAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "dataset": "22u3-xenr",
           "meta": meta("22u3-xenr"), "byDesc": {}, "bureaus": {}, "months": {}, "statuses": {}, "errors": []}
    api = f"{PORTAL}/resource/22u3-xenr.json"
    for a, b in months_back(12):
        w = f"violation_date >= '{a}T00:00:00' AND violation_date < '{b}T00:00:00'"
        try:
            rows = get(api, {"$select": "violation_code, violation_description, department_bureau, count(*) AS n", "$where": w,
                             "$group": "violation_code, violation_description, department_bureau", "$limit": 20000})
        except SystemExit as e:
            out["errors"].append(f"{a}: {e}")
            continue
        tot = 0
        for r in rows:
            n = int(float(r.get("n") or 0))
            tot += n
            k = f'{r.get("violation_code")}|{r.get("violation_description")}|{r.get("department_bureau")}'
            out["byDesc"][k] = out["byDesc"].get(k, 0) + n
            out["bureaus"][r.get("department_bureau") or ""] = out["bureaus"].get(r.get("department_bureau") or "", 0) + n
        out["months"][str(a)[:7]] = tot
        try:
            r = get(api, {"$select": "violation_status, count(*) AS n", "$where": w, "$group": "violation_status"})
            for x in r:
                out["statuses"][x.get("violation_status") or ""] = out["statuses"].get(x.get("violation_status") or "", 0) + int(float(x.get("n") or 0))
        except SystemExit as e:
            out["errors"].append(f"status {a}: {e}")
    a = months_back(1)[0][0]
    try:
        r = get(api, {"$select": "count(*) AS n", "$where": f"violation_date >= '{a}T00:00:00' AND latitude IS NULL"})
        out["noLatLastMonth"] = int(float(r[0].get("n") or 0))
    except SystemExit as e:
        out["noLatLastMonth"] = f"error: {e}"
    out["byDesc"] = dict(sorted(out["byDesc"].items(), key=lambda kv: -kv[1]))
    return out


def main():
    for mod, fn in (("dp_flooding", flooding), ("dp_repairs", repairs)):
        d = os.path.join(ROOT, "site", "datapages", mod)
        os.makedirs(d, exist_ok=True)
        json.dump(fn(), open(os.path.join(d, "source-check.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("wrote", mod)
    try:
        open(os.path.join(ROOT, "site", "datapages", "dp_repairs", "city-terms.txt"), "w", encoding="utf-8").write(terms_text())
    except SystemExit as e:
        open(os.path.join(ROOT, "site", "datapages", "dp_repairs", "city-terms.txt"), "w", encoding="utf-8").write(f"Could not fetch {TERMS_URL}: {e}\n")


if __name__ == "__main__":
    main()
