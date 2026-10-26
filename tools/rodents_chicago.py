#!/usr/bin/env python3
"""Chicago rat complaints: the data layer for the free weekly page /chicago-rat-complaints/ (site/pages.json kind
"rodents", page built by tools/rodents_site.py). Todd's go, Oct 26, 2026 ("Make all of them",
coo/DECISIONS-2026-10-26.md).

Runs in GitHub Actions (.github/workflows/rodents-chicago.yml), because the cloud agents cannot reach
data.cityofchicago.org. Source: City of Chicago Data Portal, 311 Service Requests (dataset v6vf-nfxy), service request
type "Rodent Baiting/Rat Complaint". Only counts leave the runner: requests by community area for the last 7 and
30 days, the same 30 days a year earlier, and the last 12 weeks citywide. No address, location, request number or
anything a resident typed is ever kept. Requests the City marks as duplicates are left out when the dataset carries
that flag (DUPES below).

Usage: python3 tools/rodents_chicago.py            pull and write permits/rodents-chicago/weekly.json
       python3 tools/rodents_chicago.py --selftest  planted responses, no network
"""
import argparse, datetime as dt, json, os, sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "permits", "rodents-chicago", "weekly.json")
PORTAL = "https://data.cityofchicago.org"
DATASET = "v6vf-nfxy"
DATASET_PAGE = f"{PORTAL}/Service-Requests/311-Service-Requests/{DATASET}"
SR_TYPE = "Rodent Baiting/Rat Complaint"
DUPES = " AND (duplicate IS NULL OR duplicate = false)"   # the City's own duplicate flag on a request
CHI = ZoneInfo("America/Chicago")

# The City's 77 community areas (dataset igwz-8jzy, read Oct 26, 2026), in plain capitals.
AREAS = {1: "Rogers Park", 2: "West Ridge", 3: "Uptown", 4: "Lincoln Square", 5: "North Center", 6: "Lake View",
         7: "Lincoln Park", 8: "Near North Side", 9: "Edison Park", 10: "Norwood Park", 11: "Jefferson Park", 12: "Forest Glen",
         13: "North Park", 14: "Albany Park", 15: "Portage Park", 16: "Irving Park", 17: "Dunning", 18: "Montclare",
         19: "Belmont Cragin", 20: "Hermosa", 21: "Avondale", 22: "Logan Square", 23: "Humboldt Park", 24: "West Town",
         25: "Austin", 26: "West Garfield Park", 27: "East Garfield Park", 28: "Near West Side", 29: "North Lawndale",
         30: "South Lawndale", 31: "Lower West Side", 32: "Loop", 33: "Near South Side", 34: "Armour Square", 35: "Douglas",
         36: "Oakland", 37: "Fuller Park", 38: "Grand Boulevard", 39: "Kenwood", 40: "Washington Park", 41: "Hyde Park",
         42: "Woodlawn", 43: "South Shore", 44: "Chatham", 45: "Avalon Park", 46: "South Chicago", 47: "Burnside",
         48: "Calumet Heights", 49: "Roseland", 50: "Pullman", 51: "South Deering", 52: "East Side", 53: "West Pullman",
         54: "Riverdale", 55: "Hegewisch", 56: "Garfield Ridge", 57: "Archer Heights", 58: "Brighton Park", 59: "McKinley Park",
         60: "Bridgeport", 61: "New City", 62: "West Elsdon", 63: "Gage Park", 64: "Clearing", 65: "West Lawn",
         66: "Chicago Lawn", 67: "West Englewood", 68: "Englewood", 69: "Greater Grand Crossing", 70: "Ashburn",
         71: "Auburn Gresham", 72: "Beverly", 73: "Washington Heights", 74: "Mount Greenwood", 75: "Morgan Park",
         76: "O'Hare", 77: "Edgewater"}


def windows(today):
    """Whole days in Chicago time, ending at the start of `today` (the day the pull runs is left out as incomplete)."""
    end = dt.datetime.combine(today, dt.time(0))
    ago = lambda d: end - dt.timedelta(days=d)
    year = lambda t: t.replace(year=t.year - 1) if not (t.month == 2 and t.day == 29) else t.replace(year=t.year - 1, day=28)
    return {"to": end, "from7": ago(7), "from30": ago(30), "prevFrom": year(ago(30)), "prevTo": year(end), "from12w": ago(84)}


def soql_time(t):
    return t.strftime("%Y-%m-%dT%H:%M:%S")


def where(a, b, dupes=True):
    return (f"sr_type = '{SR_TYPE}' AND created_date >= '{soql_time(a)}' AND created_date < '{soql_time(b)}'"
            + (DUPES if dupes else ""))


def by_area(rows):
    out = {}
    for r in rows:
        n = int(float(r.get("n") or r.get("count") or 0))
        try:
            k = int(float(r.get("community_area")))
        except (TypeError, ValueError):
            k = 0          # no community area on the request
        if k not in AREAS:
            k = 0
        out[k] = out.get(k, 0) + n
    return out


def weeks_of(day_rows, w):
    """Twelve 7-day buckets ending at w["to"], oldest first, from per-day counts."""
    per = {}
    for r in day_rows:
        d = (r.get("d") or "")[:10]
        if d:
            per[d] = per.get(d, 0) + int(float(r.get("n") or 0))
    out = []
    for k in range(12, 0, -1):
        a = w["to"] - dt.timedelta(days=7 * k)
        days = [(a + dt.timedelta(days=j)).strftime("%Y-%m-%d") for j in range(7)]
        out.append({"from": days[0], "to": days[-1], "count": sum(per.get(x, 0) for x in days)})
    return out


def change(now, before):
    return round((now / before - 1) * 100, 1) if before else None


def build(a7, a30, prev, days, w, fetched, dupes=True):
    areas = []
    for k in sorted(AREAS):
        areas.append({"n": k, "name": AREAS[k], "d7": a7.get(k, 0), "d30": a30.get(k, 0), "prev30": prev.get(k, 0),
                      "change": change(a30.get(k, 0), prev.get(k, 0))})
    tot = lambda m: sum(m.values())
    last = w["to"] - dt.timedelta(days=1)
    return {
        "about": "Counts only: City of Chicago 311 requests of type Rodent Baiting/Rat Complaint by community area. No address, location, request number or resident text is kept. Built by tools/rodents_chicago.py.",
        "source": {"name": "311 Service Requests", "dataset": DATASET, "url": DATASET_PAGE, "srType": SR_TYPE,
                   "fetchedAt": fetched, "duplicatesLeftOut": bool(dupes)},
        "window": {"from7": w["from7"].strftime("%Y-%m-%d"), "from30": w["from30"].strftime("%Y-%m-%d"), "to": last.strftime("%Y-%m-%d"),
                   "prevFrom": w["prevFrom"].strftime("%Y-%m-%d"), "prevTo": (w["prevTo"] - dt.timedelta(days=1)).strftime("%Y-%m-%d")},
        "counts": {"d7": tot(a7), "d30": tot(a30), "prev30": tot(prev), "change": change(tot(a30), tot(prev)),
                   "noArea30": a30.get(0, 0), "areasWith30": sum(1 for k, v in a30.items() if k and v)},
        "areas": areas,
        "weeks": weeks_of(days, w),
    }


def pull():
    sys.path.insert(0, HERE)
    from permits_chicago import get
    now = dt.datetime.now(CHI)
    w = windows(now.date())
    api = f"{PORTAL}/resource/{DATASET}.json"
    group = lambda a, b, dupes: get(api, {"$select": "community_area, count(*) AS n", "$where": where(a, b, dupes),
                                          "$group": "community_area", "$limit": 200})
    dupes = True
    try:
        a30 = by_area(group(w["from30"], w["to"], True))
    except SystemExit:
        dupes = False          # the duplicate flag is not queryable: count every request and say so on the page
        a30 = by_area(group(w["from30"], w["to"], False))
    a7 = by_area(group(w["from7"], w["to"], dupes))
    prev = by_area(group(w["prevFrom"], w["prevTo"], dupes))
    days = get(api, {"$select": "date_trunc_ymd(created_date) AS d, count(*) AS n", "$where": where(w["from12w"], w["to"], dupes),
                     "$group": "d", "$order": "d", "$limit": 500})
    d = build(a7, a30, prev, days, w, now.strftime("%Y-%m-%dT%H:%M:%S%z"), dupes)
    if d["counts"]["d30"] < 100:
        raise SystemExit(f"only {d['counts']['d30']} requests in 30 days: the query or the dataset changed; not writing")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(d, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"rodents: 7 days {d['counts']['d7']}, 30 days {d['counts']['d30']}, a year earlier {d['counts']['prev30']} "
          f"({d['counts']['change']}%), no area {d['counts']['noArea30']}, duplicates left out: {dupes}")


def selftest():
    w = windows(dt.date(2026, 10, 26))
    assert soql_time(w["from30"]) == "2026-09-26T00:00:00" and soql_time(w["prevTo"]) == "2025-10-26T00:00:00", w
    assert soql_time(w["from7"]) == "2026-10-19T00:00:00"
    assert "2026-10-26T00:00:00" in where(w["from30"], w["to"]) and "duplicate" in where(w["from7"], w["to"])
    assert "duplicate" not in where(w["from7"], w["to"], dupes=False)
    leap = windows(dt.date(2028, 3, 1))     # Feb 29 a year back has no twin: falls to Feb 28
    assert leap["prevFrom"].strftime("%m-%d") == "01-31", leap
    a = by_area([{"community_area": "6", "n": "243"}, {"community_area": "24.0", "n": "208"}, {"n": "9"},
                 {"community_area": "99", "n": "2"}, {"community_area": "6", "n": "1"}])
    assert a == {6: 244, 24: 208, 0: 11}, a        # a missing or unknown area counts under 0, never dropped
    days = [{"d": "2026-10-25T00:00:00.000", "n": "150"}, {"d": "2026-10-19T00:00:00.000", "n": "10"},
            {"d": "2026-10-18T00:00:00.000", "n": "7"}, {"d": "2026-08-03T00:00:00.000", "n": "5"}]
    wk = weeks_of(days, w)
    assert len(wk) == 12 and wk[-1] == {"from": "2026-10-19", "to": "2026-10-25", "count": 160}, wk[-1]
    assert wk[-2]["count"] == 7 and wk[0]["from"] == "2026-08-03" and wk[0]["count"] == 5, wk[:2]
    d = build({6: 40, 0: 2}, {6: 243, 24: 208, 0: 9}, {6: 200, 24: 0}, days, w, "2026-10-26T06:00:00-0500")
    c = d["counts"]
    assert (c["d7"], c["d30"], c["prev30"], c["noArea30"], c["areasWith30"]) == (42, 460, 200, 9, 2), c
    assert c["change"] == 130.0 and d["window"]["to"] == "2026-10-25" and d["window"]["prevTo"] == "2025-10-25", d["window"]
    lv = next(x for x in d["areas"] if x["n"] == 6)
    assert lv == {"n": 6, "name": "Lake View", "d7": 40, "d30": 243, "prev30": 200, "change": 21.5}, lv
    wt = next(x for x in d["areas"] if x["n"] == 24)
    assert wt["change"] is None, wt                    # nothing a year earlier: no percent, never a divide by zero
    assert len(d["areas"]) == 77 and all("address" not in x and "lat" not in json.dumps(x) for x in d["areas"])
    assert change(0, 0) is None and change(90, 100) == -10.0
    print("rodents_chicago selftest: ok (windows, leap day, areas, weeks, change, counts only)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    selftest() if a.selftest else pull()
