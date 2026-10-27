#!/usr/bin/env python3
"""Chicago basement flooding calls: the data layer for the free page /chicago-basement-flooding/ (site/pages.json kind
"datapage", module tools/dp_flooding.py). Todd's go, Oct 27, 2026 ("Let's do them all", coo/PARALLEL_BUILDS.md,
build B8; research_notes/kimi-2026-10-27-r10.md item 9).

Runs in GitHub Actions (.github/workflows/dp_flooding.yml), because the cloud agents cannot reach
data.cityofchicago.org. Source: City of Chicago Data Portal, 311 Service Requests (dataset v6vf-nfxy), the request
types in TYPES (names and short codes confirmed in the data Oct 27, 2026 by tools/dp_probe_b8.py,
site/datapages/dp_flooding/source-check.json: Water in Basement Complaint, AAF; Sewer Cleaning Inspection Request, CHECKFOR).

One query per type and month (grouped queries over the whole table time out), grouped by day and community area. Only
counts leave the runner: requests per community area per month, and requests per day citywide. No address, location,
request number or anything a resident typed is ever kept. Requests the City marks as duplicates are left out when the
dataset carries that flag.

Each daily run pulls the last 3 months again (late records and duplicate flags settle) and keeps the older months
from the committed file; the 1st of each month, a missing file or --full pulls everything again.

Usage: python3 tools/dp_flooding_data.py            pull and write site/datapages/dp_flooding/monthly.json
       python3 tools/dp_flooding_data.py --full     pull every month again
       python3 tools/dp_flooding_data.py --selftest planted responses, no network
"""
import argparse, datetime as dt, json, os, sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "site", "datapages", "dp_flooding", "monthly.json")
PORTAL = "https://data.cityofchicago.org"
DATASET = "v6vf-nfxy"
DATASET_PAGE = f"{PORTAL}/Service-Requests/311-Service-Requests/{DATASET}"
CHI = ZoneInfo("America/Chicago")
START = "2019-01"          # the first whole month of the City's new 311 system (launched Dec 18, 2018; source check)
REPULL = 3                 # months pulled again every day
DUPES = " AND (duplicate IS NULL OR duplicate = false)"
TYPES = [
    {"key": "water", "srType": "Water in Basement Complaint", "label": "Water in basement", "short": "AAF"},
    {"key": "sewer", "srType": "Sewer Cleaning Inspection Request", "label": "Sewer cleaning", "short": "CHECKFOR"},
]
AREAS = range(1, 78)


def month_list(first, last):
    y, m = map(int, first.split("-"))
    out = []
    while f"{y:04d}-{m:02d}" <= last:
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def next_month(ym):
    y, m = map(int, ym.split("-"))
    return f"{y + 1:04d}-01" if m == 12 else f"{y:04d}-{m + 1:02d}"


def where(sr, a, b, dupes=True):
    return (f"sr_type = '{sr}' AND created_date >= '{a}T00:00:00' AND created_date < '{b}T00:00:00'" + (DUPES if dupes else ""))


def bounds(ym, today):
    """[first day, day after the last counted day) of month ym; the current month stops before today (incomplete)."""
    a = ym + "-01"
    b = next_month(ym) + "-01"
    return a, min(b, today.isoformat())


def fold(rows):
    """Grouped rows (d, community_area, n) -> ({area: n}, {day: n}); a missing or unknown area counts under 0."""
    areas, days = {}, {}
    for r in rows:
        n = int(float(r.get("n") or 0))
        try:
            k = int(float(r.get("community_area")))
        except (TypeError, ValueError):
            k = 0
        k = k if k in AREAS else 0
        areas[k] = areas.get(k, 0) + n
        d = (r.get("d") or "")[:10]
        if d:
            days[d] = days.get(d, 0) + n
    return areas, days


def assemble(per, months, through, fetched, dupes):
    """per: {type key: {month: (areas, days)}} -> the committed file."""
    first_day = months[0] + "-01"
    ndays = (dt.date.fromisoformat(through) - dt.date.fromisoformat(first_day)).days + 1
    out = {"about": "Counts only: City of Chicago 311 requests of the types below, by community area per month and citywide per day. "
                    "No address, location, request number or resident text is kept. Built by tools/dp_flooding_data.py.",
           "source": {"name": "311 Service Requests", "dataset": DATASET, "url": DATASET_PAGE, "fetchedAt": fetched,
                      "duplicatesLeftOut": bool(dupes)},
           "types": [dict(t) for t in TYPES], "months": months, "through": through, "dayFrom": first_day, "series": {}}
    for t in TYPES:
        k = t["key"]
        area = {str(n): [] for n in AREAS}
        city, noarea, daily = [], [], [0] * ndays
        for ym in months:
            a, d = per[k].get(ym, ({}, {}))
            for n in AREAS:
                area[str(n)].append(a.get(n, 0))
            city.append(sum(a.values()))
            noarea.append(a.get(0, 0))
            for day, v in d.items():
                i = (dt.date.fromisoformat(day) - dt.date.fromisoformat(first_day)).days
                if 0 <= i < ndays:
                    daily[i] += v
        out["series"][k] = {"area": area, "city": city, "noArea": noarea, "daily": daily}
    return out


def unpack(old):
    """The committed file back into {type key: {month: (areas, days)}}, so a daily run keeps the older months."""
    per = {t["key"]: {} for t in TYPES}
    if not old:
        return per
    d0 = dt.date.fromisoformat(old["dayFrom"])
    for t in TYPES:
        s = old["series"].get(t["key"])
        if not s:
            continue
        for i, ym in enumerate(old["months"]):
            areas = {int(n): v[i] for n, v in s["area"].items() if v[i]}
            if s["noArea"][i]:
                areas[0] = s["noArea"][i]
            days = {}
            for j, v in enumerate(s["daily"]):
                day = (d0 + dt.timedelta(days=j)).isoformat()
                if day[:7] == ym and v:
                    days[day] = v
            per[t["key"]][ym] = (areas, days)
    return per


def pull(full=False):
    sys.path.insert(0, HERE)
    from permits_chicago import get
    now = dt.datetime.now(CHI)
    today = now.date()
    last_day = today - dt.timedelta(days=1)
    months = month_list(START, last_day.isoformat()[:7])
    old = None
    if os.path.isfile(OUT) and not full and today.day != 1:
        old = json.load(open(OUT, encoding="utf-8"))
        if [t["srType"] for t in old.get("types", [])] != [t["srType"] for t in TYPES]:
            old = None     # the type list changed: everything again
    per = unpack(old)
    redo = months[-REPULL:] if old else months
    api = f"{PORTAL}/resource/{DATASET}.json"
    dupes = True
    for t in TYPES:
        for ym in redo:
            a, b = bounds(ym, today)
            q = lambda dp: get(api, {"$select": "date_trunc_ymd(created_date) AS d, community_area, count(*) AS n",
                                     "$where": where(t["srType"], a, b, dp), "$group": "d, community_area", "$limit": 5000})
            try:
                rows = q(dupes)
            except SystemExit:
                if not dupes:
                    raise
                dupes = False      # the duplicate flag is not queryable: count every request and say so on the page
                rows = q(False)
            if len(rows) >= 5000:
                raise SystemExit(f"{t['key']} {ym}: 5,000 grouped rows, the month did not fit in one query")
            per[t["key"]][ym] = fold(rows)
    d = assemble(per, months, last_day.isoformat(), now.strftime("%Y-%m-%dT%H:%M:%S%z"), dupes)
    if old and old["source"].get("duplicatesLeftOut") != dupes:
        return pull(full=True)     # never mix months counted two ways
    yr = {t["key"]: sum(d["series"][t["key"]]["city"][-13:-1]) for t in TYPES}
    if yr["water"] < 500 or yr["sewer"] < 500:
        raise SystemExit(f"12-month totals {yr}: the query or the dataset changed; not writing")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(d, open(OUT, "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print(f"flooding: months {months[0]} to {months[-1]} (pulled {len(redo)} per type), through {d['through']}, "
          f"last 12 complete months {yr}, duplicates left out: {dupes}")


def selftest():
    assert month_list("2025-11", "2026-02") == ["2025-11", "2025-12", "2026-01", "2026-02"]
    assert next_month("2026-12") == "2027-01"
    assert bounds("2026-10", dt.date(2026, 10, 27)) == ("2026-10-01", "2026-10-27"), "today left out"
    assert bounds("2026-09", dt.date(2026, 10, 27)) == ("2026-09-01", "2026-10-01")
    w = where("Water in Basement Complaint", "2026-09-01", "2026-10-01")
    assert "sr_type = 'Water in Basement Complaint'" in w and "duplicate" in w and "< '2026-10-01T00:00:00'" in w
    a, d = fold([{"d": "2026-09-03T00:00:00.000", "community_area": "6", "n": "12"}, {"d": "2026-09-03T00:00:00.000", "n": "2"},
                 {"d": "2026-09-04T00:00:00.000", "community_area": "6.0", "n": "1"}, {"d": "2026-09-04T00:00:00.000", "community_area": "99", "n": "3"}])
    assert a == {6: 13, 0: 5} and d == {"2026-09-03": 14, "2026-09-04": 4}, (a, d)
    per = {"water": {"2026-09": (a, d), "2026-10": ({70: 4}, {"2026-10-02": 4})}, "sewer": {"2026-09": ({}, {})}}
    out = assemble(per, ["2026-09", "2026-10"], "2026-10-26", "x", True)
    s = out["series"]["water"]
    assert s["area"]["6"] == [13, 0] and s["area"]["70"] == [0, 4] and s["city"] == [18, 4] and s["noArea"] == [5, 0]
    assert len(s["daily"]) == 56 and s["daily"][2] == 14 and s["daily"][31] == 4, "daily index from Sep 1"
    back = unpack(out)
    assert back["water"]["2026-09"] == ({6: 13, 0: 5}, {"2026-09-03": 14, "2026-09-04": 4}), back["water"]["2026-09"]
    assert assemble(back, ["2026-09", "2026-10"], "2026-10-26", "x", True)["series"] == out["series"], "round trip"
    js = json.dumps({k: v for k, v in out.items() if k != "about"})
    assert all(x not in js for x in ("address", "latitude", "street", "sr_number")), "counts only"
    print("dp_flooding_data selftest: ok (months, bounds, fold, assemble, round trip, counts only)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--full", action="store_true")
    x = ap.parse_args()
    selftest() if x.selftest else pull(x.full)
