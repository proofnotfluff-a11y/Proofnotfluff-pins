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

Rat Index (Todd, Oct 27, 2026, "Let's do them all", coo/DECISIONS-2026-10-27.md, R10 item 4): the same pull also
counts the 30 days before the last 30 (month over month rank), each area's last 12 weeks, a yearly edition (the 12
months to September 30, published each October for rat-list season, with the edition before it) and how long the
City took to close the requests it closed in the last 30 days (median days, from the created and closed dates only).
Rates per 1,000 residents use site/geo/chicago-community-area-population.json (--population): the City of Chicago's
"ACS 5 Year Data by Community Area" (dataset t68z-cikk, U.S. Census Bureau American Community Survey estimates
allocated to community areas by the City), total population only.

Usage: python3 tools/rodents_chicago.py              pull and write permits/rodents-chicago/weekly.json
       python3 tools/rodents_chicago.py --population  pull and write site/geo/chicago-community-area-population.json
       python3 tools/rodents_chicago.py --selftest    planted responses, no network
"""
import argparse, datetime as dt, json, os, statistics, sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "permits", "rodents-chicago", "weekly.json")
POP_OUT = os.path.join(ROOT, "site", "geo", "chicago-community-area-population.json")
POP_DATASET = "t68z-cikk"
POP_PAGE = f"https://data.cityofchicago.org/d/{POP_DATASET}"
MIN_CLOSED = 5     # fewer closed requests than this in an area: no median days to close
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
    ed = today.year if today.month >= 10 else today.year - 1        # the yearly edition: 12 months to Sep 30, out in October
    e = lambda y: dt.datetime(y, 10, 1)
    return {"to": end, "from7": ago(7), "from30": ago(30), "from60": ago(60), "prevFrom": year(ago(30)), "prevTo": year(end),
            "from12w": ago(84), "edition": ed, "edFrom": e(ed - 1), "edTo": e(ed), "edPrevFrom": e(ed - 2)}


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


def area_weeks(rows, w):
    """{area: [12 weekly counts, oldest first]} from per-area, per-day counts (no area counts under 0)."""
    by = {}
    for r in rows:
        try:
            k = int(float(r.get("community_area")))
        except (TypeError, ValueError):
            k = 0
        by.setdefault(k if k in AREAS else 0, []).append(r)
    return {k: [x["count"] for x in weeks_of(v, w)] for k, v in by.items()}


def days_open(created, closed):
    """Days from a request's created date to its closed date, or None when either is missing or out of order."""
    try:
        a, b = (dt.datetime.fromisoformat(x[:19]) for x in (created, closed))
    except (TypeError, ValueError):
        return None
    d = (b - a).total_seconds() / 86400
    return d if d >= 0 else None


def close_times(rows):
    """{area: (closed count, median days or None)} from created and closed dates, plus the citywide figure under "all"."""
    by, every = {}, []
    for r in rows:
        d = days_open(r.get("created_date"), r.get("closed_date"))
        if d is None:
            continue
        try:
            k = int(float(r.get("community_area")))
        except (TypeError, ValueError):
            k = 0
        by.setdefault(k if k in AREAS else 0, []).append(d)
        every.append(d)
    med = lambda v: round(statistics.median(v), 1) if len(v) >= MIN_CLOSED else None
    out = {k: (len(v), med(v)) for k, v in by.items()}
    out["all"] = (len(every), med(every))
    return out


def build(a7, a30, prev, days, w, fetched, dupes=True, prior=None, wk_area=None, closes=None, year=None, year_prev=None):
    areas = []
    for k in sorted(AREAS):
        a = {"n": k, "name": AREAS[k], "d7": a7.get(k, 0), "d30": a30.get(k, 0), "prev30": prev.get(k, 0),
             "change": change(a30.get(k, 0), prev.get(k, 0))}
        if prior is not None:
            a["prior30"] = prior.get(k, 0)
        if wk_area is not None:
            a["w12"] = wk_area.get(k, [0] * 12)
        if closes is not None:
            a["closed30"], a["medClose"] = closes.get(k, (0, None))
        if year is not None:
            a["year"], a["yearPrev"] = year.get(k, 0), (year_prev or {}).get(k, 0)
        areas.append(a)
    tot = lambda m: sum(m.values())
    last = w["to"] - dt.timedelta(days=1)
    out = {
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
    if prior is not None:
        out["window"].update({"priorFrom": w["from60"].strftime("%Y-%m-%d"), "priorTo": (w["from30"] - dt.timedelta(days=1)).strftime("%Y-%m-%d")})
        out["counts"]["prior30"] = tot(prior)
    if closes is not None:
        out["counts"]["closed30"], out["counts"]["medClose"] = closes.get("all", (0, None))
    if year is not None:
        day = lambda t: t.strftime("%Y-%m-%d")
        out["edition"] = {"year": w["edition"], "from": day(w["edFrom"]), "to": day(w["edTo"] - dt.timedelta(days=1)),
                          "prevFrom": day(w["edPrevFrom"]), "prevTo": day(w["edFrom"] - dt.timedelta(days=1)),
                          "total": tot(year), "prevTotal": tot(year_prev or {}), "noArea": year.get(0, 0)}
    return out


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
    prior = by_area(group(w["from60"], w["from30"], dupes))
    year = by_area(group(w["edFrom"], w["edTo"], dupes))
    year_prev = by_area(group(w["edPrevFrom"], w["edFrom"], dupes))
    wk = area_weeks(get(api, {"$select": "community_area, date_trunc_ymd(created_date) AS d, count(*) AS n",
                              "$where": where(w["from12w"], w["to"], dupes), "$group": "community_area, d", "$limit": 20000}), w)
    # closed in the last 30 days: only the area and the two dates are read, and only the counts and medians are kept
    closed_where = (f"sr_type = '{SR_TYPE}' AND closed_date >= '{soql_time(w['from30'])}' AND closed_date < '{soql_time(w['to'])}'"
                    + (DUPES if dupes else ""))
    rows, off = [], 0
    while True:
        page = get(api, {"$select": "community_area, created_date, closed_date", "$where": closed_where,
                         "$order": "closed_date", "$limit": 5000, "$offset": off})
        rows += page
        if len(page) < 5000:
            break
        off += 5000
    closes = close_times(rows)
    del rows
    d = build(a7, a30, prev, days, w, now.strftime("%Y-%m-%dT%H:%M:%S%z"), dupes, prior=prior, wk_area=wk, closes=closes,
              year=year, year_prev=year_prev)
    if d["counts"]["d30"] < 100:
        raise SystemExit(f"only {d['counts']['d30']} requests in 30 days: the query or the dataset changed; not writing")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    if sum(sum(a["w12"]) for a in d["areas"]) + sum(wk.get(0, [])) != sum(x["count"] for x in d["weeks"]):
        raise SystemExit("area weeks do not add up to the citywide weeks; not writing")
    json.dump(d, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"rodents: 7 days {d['counts']['d7']}, 30 days {d['counts']['d30']}, a year earlier {d['counts']['prev30']} "
          f"({d['counts']['change']}%), the 30 days before {d['counts']['prior30']}, no area {d['counts']['noArea30']}, "
          f"closed {d['counts']['closed30']} (median {d['counts']['medClose']} days), edition {w['edition']}: "
          f"{d['edition']['total']} against {d['edition']['prevTotal']}, duplicates left out: {dupes}")


def norm(name):
    return "".join(ch for ch in name.upper() if ch.isalnum())


def pop_build(rows, fetched):
    """The population file from the City's rows (acs_year, community_area name, total_population); newest year only."""
    years = sorted({int(float(r["acs_year"])) for r in rows if r.get("acs_year")})
    if not years:
        raise SystemExit("population: no ACS year in the rows; not writing")
    yr = years[-1]
    names = {norm(v): k for k, v in AREAS.items()}
    pop = {}
    for r in rows:
        if int(float(r.get("acs_year") or 0)) != yr:
            continue
        k = names.get(norm(r.get("community_area") or ""))
        if k is None:
            raise SystemExit(f"population: unknown community area {r.get('community_area')!r}; not writing")
        pop[k] = int(round(float(r["total_population"])))
    if sorted(pop) != sorted(AREAS) or min(pop.values()) <= 0:
        raise SystemExit(f"population: {len(pop)} of 77 areas for {yr}; not writing")
    return {"about": "Total population of each of Chicago's 77 community areas, the only column kept. Built by tools/rodents_chicago.py --population.",
            "source": {"name": "ACS 5 Year Data by Community Area", "publisher": "City of Chicago",
                       "dataset": POP_DATASET, "url": POP_PAGE,
                       "method": "U.S. Census Bureau American Community Survey 5-year estimates, census tracts allocated to community areas by the City",
                       "acsYear": yr, "fetchedAt": fetched},
            "total": sum(pop.values()),
            "areas": [{"n": k, "name": AREAS[k], "population": pop[k]} for k in sorted(pop)]}


def population():
    sys.path.insert(0, HERE)
    from permits_chicago import get
    rows = get(f"{PORTAL}/resource/{POP_DATASET}.json", {"$select": "acs_year, community_area, total_population", "$limit": 5000})
    d = pop_build(rows, dt.datetime.now(CHI).strftime("%Y-%m-%dT%H:%M:%S%z"))
    if not 2_400_000 <= d["total"] <= 2_900_000:
        raise SystemExit(f"population: city total {d['total']:,} is out of range; not writing")
    os.makedirs(os.path.dirname(POP_OUT), exist_ok=True)
    json.dump(d, open(POP_OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"population: ACS {d['source']['acsYear']}, 77 areas, city total {d['total']:,}")


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
    # Rat Index additions
    assert soql_time(w["from60"]) == "2026-08-27T00:00:00" and w["edition"] == 2026, w
    assert (soql_time(w["edFrom"]), soql_time(w["edTo"]), soql_time(w["edPrevFrom"])) == ("2025-10-01T00:00:00", "2026-10-01T00:00:00", "2024-10-01T00:00:00")
    assert windows(dt.date(2026, 9, 30))["edition"] == 2025 and windows(dt.date(2026, 10, 1))["edition"] == 2026
    wa = area_weeks([{"community_area": "6", "d": "2026-10-25T00:00:00.000", "n": "4"}, {"community_area": "6", "d": "2026-08-03T00:00:00.000", "n": "2"},
                     {"d": "2026-10-20T00:00:00.000", "n": "1"}], w)
    assert wa[6][-1] == 4 and wa[6][0] == 2 and sum(wa[6]) == 6 and wa[0][-1] == 1, wa
    assert days_open("2026-10-01T10:00:00.000", "2026-10-03T22:00:00.000") == 2.5 and days_open("2026-10-03T00:00:00", "2026-10-01T00:00:00") is None
    assert days_open(None, "2026-10-01T00:00:00") is None
    ct = close_times([{"community_area": "6", "created_date": f"2026-10-0{i}T00:00:00", "closed_date": "2026-10-09T00:00:00"} for i in range(1, 7)]
                     + [{"community_area": "24", "created_date": "2026-10-01T00:00:00", "closed_date": "2026-10-02T00:00:00"}])
    assert ct[6] == (6, 5.5) and ct[24] == (1, None) and ct["all"] == (7, 5.0), ct    # under 5 closed: no median
    d2 = build({6: 40}, {6: 243}, {6: 200}, days, w, "x", prior={6: 180}, wk_area={6: [1] * 12}, closes=ct, year={6: 2000, 0: 3}, year_prev={6: 1900})
    lv2 = next(x for x in d2["areas"] if x["n"] == 6)
    assert (lv2["prior30"], lv2["w12"], lv2["closed30"], lv2["medClose"], lv2["year"], lv2["yearPrev"]) == (180, [1] * 12, 6, 5.5, 2000, 1900), lv2
    ed = d2["edition"]
    assert (ed["year"], ed["from"], ed["to"], ed["prevFrom"], ed["prevTo"], ed["total"], ed["noArea"]) == (2026, "2025-10-01", "2026-09-30", "2024-10-01", "2025-09-30", 2003, 3), ed
    assert d2["window"]["priorFrom"] == "2026-08-27" and d2["window"]["priorTo"] == "2026-09-25" and d2["counts"]["medClose"] == 5.0
    assert "prior30" not in d["areas"][0] and "edition" not in d, "old callers get the old file shape"
    rows = [{"acs_year": "2023", "community_area": AREAS[k].upper().replace("'", ""), "total_population": f"{1000 + k}.0"} for k in AREAS]
    pb = pop_build(rows + [{"acs_year": "2022", "community_area": "LOOP", "total_population": "1.0"}], "t")
    assert pb["source"]["acsYear"] == 2023 and len(pb["areas"]) == 77 and pb["areas"][75] == {"n": 76, "name": "O'Hare", "population": 1076}, pb["areas"][75]
    for bad in (rows[:-1], rows + [{"acs_year": "2023", "community_area": "NOWHERE", "total_population": "5"}]):
        try:
            pop_build(bad, "t"); raise AssertionError("a missing or unknown area must stop the write")
        except SystemExit:
            pass
    print("rodents_chicago selftest: ok (windows, leap day, areas, weeks, change, counts only, prior 30 days, area weeks, "
          "close times, yearly edition, population)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--population", action="store_true")
    a = ap.parse_args()
    selftest() if a.selftest else population() if a.population else pull()
