#!/usr/bin/env python3
"""Daily snowfall and snow depth at Chicago's two airports for the free snow season board (/chicago-snow-season/,
tools/dp_snow.py). Todd's go, Oct 27, 2026 ("Let's do them all", coo/PARALLEL_BUILDS.md, research_notes/kimi-2026-10-27-r10.md item 1).

Runs in GitHub Actions (.github/workflows/dp_snow.yml), because the cloud agents cannot reach ncei.noaa.gov.
Source: NOAA National Centers for Environmental Information (NCEI), Global Historical Climatology Network daily
(GHCN-Daily, the "daily-summaries" dataset), read through the NCEI Access Data Service. Elements: SNOW (snowfall,
inches) and SNWD (snow depth on the ground, inches).

Stations are never typed in from memory. The NCEI Access Search Service lists the daily-summaries stations with snowfall
inside a box around the city; the run keeps the stations whose NOAA name says O'Hare or Midway, pulls each one, and for
each airport keeps the station with the most snowfall days reported in the snow months (October to May) of the 30
winters. Each data row's own STATION and NAME fields must match the station picked, or the run stops. Weather records
only: no person, address or business is in the file.

Writes site/datapages/dp_snow/daily.json: per station its NOAA id and name, how it was picked, the first date, and one
value per day for SNOW and SNWD (null where NOAA has no value that day).

Usage: python3 tools/dp_snow_fetch.py            pull and write the file
       python3 tools/dp_snow_fetch.py --selftest  planted responses, no network
"""
import datetime as dt, json, os, re, sys, time, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "site", "datapages", "dp_snow", "daily.json")
SEARCH = "https://www.ncei.noaa.gov/access/services/search/v1/data"
DATA = "https://www.ncei.noaa.gov/access/services/data/v1"
BBOX = "42.05,-87.98,41.70,-87.60"    # north, west, south, east: a box over the city and both airports
FIRST_WINTER = 1996                   # winters run July 1 to June 30; 1996-97 to 2025-26 are the 30 full winters
LAST_WINTER = 2025
START = dt.date(FIRST_WINTER, 7, 1)
UA = {"User-Agent": "ProofNotFluff snow board (github.com/proofnotfluff-a11y/proofnotfluff-pins)"}
AIRPORTS = {"ohare": ("O'Hare", re.compile(r"\bO\W?HARE\b")), "midway": ("Midway", re.compile(r"\bMIDWAY\b"))}
MIN_COVER = 0.9                       # a station with under 90% of its snow-month days reported is not used


def get(url, params, tries=4):
    q = url + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(q, headers=UA), timeout=180) as r:
                return json.load(r)
        except Exception as e:   # NCEI is slow at times: back off, then stop loudly
            if i == tries - 1:
                sys.exit(f"NCEI request failed: {q}: {e}")
            time.sleep(15 * (i + 1))


def snow_months(day):
    return day.month >= 10 or day.month <= 5


def in_winters(day):
    return START <= day < dt.date(LAST_WINTER + 1, 7, 1)


def candidates(search_pages):
    """Stations in the search results whose NOAA name names an airport: {key: [(id, name)]}."""
    seen, out = set(), {k: [] for k in AIRPORTS}
    for page in search_pages:
        for res in page.get("results", []):
            for st in res.get("stations", []):
                sid, name = st.get("id", ""), st.get("name", "")
                if not sid or sid in seen:
                    continue
                seen.add(sid)
                for k, (_, rx) in AIRPORTS.items():
                    if rx.search(name.upper()):
                        out[k].append((sid, name))
    return out


def search_all():
    pages, offset = [], 0
    while offset < 2000:
        page = get(SEARCH, {"dataset": "daily-summaries", "bbox": BBOX, "dataTypes": "SNOW", "limit": 100, "offset": offset})
        pages.append(page)
        if len(page.get("results", [])) < 100:
            break
        offset += 100
    return pages


def num(v):
    v = (v or "").strip()
    return None if v == "" else float(v)


def qflag(r, el):
    """NOAA's quality flag for one element (second field of <EL>_ATTRIBUTES: measurement, quality, source, time)."""
    a = (r.get(el + "_ATTRIBUTES") or "").split(",")
    return a[1].strip() if len(a) > 1 else ""


def parse(rows, sid, name, dropped=None):
    """{date: (snow, snwd)} from Access Data Service rows; every row must be the station asked for. A value NOAA's
    quality checks flagged (any quality flag) is treated as missing, as GHCN-Daily's documentation advises."""
    days = {}
    for r in rows:
        if r.get("STATION") != sid or (r.get("NAME") and r["NAME"].strip() != name.strip()):
            sys.exit(f"row for {r.get('STATION')} {r.get('NAME')!r} in the reply for {sid} {name!r}: stopping")
        d = dt.date.fromisoformat(r["DATE"][:10])
        snow, snwd = num(r.get("SNOW")), num(r.get("SNWD"))
        if snow is not None and qflag(r, "SNOW"):
            snow = None
            if dropped is not None:
                dropped["SNOW"] = dropped.get("SNOW", 0) + 1
        if snwd is not None and qflag(r, "SNWD"):
            snwd = None
            if dropped is not None:
                dropped["SNWD"] = dropped.get("SNWD", 0) + 1
        for v, top in ((snow, 40), (snwd, 60)):
            if v is not None and not 0 <= v <= top:
                sys.exit(f"{sid} {d}: value {v} out of range: stopping")
        days[d] = (snow, snwd)
    return days


def cover(days):
    """Share of snow-month days in the 30 winters with a snowfall value."""
    want = [START + dt.timedelta(i) for i in range((dt.date(LAST_WINTER + 1, 7, 1) - START).days)]
    want = [d for d in want if snow_months(d)]
    have = sum(1 for d in want if d in days and days[d][0] is not None)
    return have / len(want)


def pick(key, cands, pulled):
    """The candidate with the most snow-month days reported, if it clears MIN_COVER."""
    scored = sorted(((cover(pulled[sid]), sid, name) for sid, name in cands), reverse=True)
    if not scored or scored[0][0] < MIN_COVER:
        return None, scored
    return scored[0], scored


def station_doc(key, best, scored, days, end):
    c, sid, name = best
    n = (end - START).days + 1
    seq = [START + dt.timedelta(i) for i in range(n)]
    return {"key": key, "label": AIRPORTS[key][0], "id": sid, "name": name, "cover": round(c, 4),
            "considered": [{"id": s, "name": nm, "cover": round(cv, 4)} for cv, s, nm in scored],
            "start": START.isoformat(), "end": end.isoformat(),
            "snow": [days.get(d, (None, None))[0] for d in seq], "snwd": [days.get(d, (None, None))[1] for d in seq]}


def build(search_pages, pull, today, fetched):
    cands = candidates(search_pages)
    stations = []
    for key in AIRPORTS:
        if not cands[key]:
            if key == "ohare":
                sys.exit("no O'Hare station in the NCEI search reply: stopping")
            continue
        drops = {sid: {} for sid, _ in cands[key]}
        pulled = {sid: parse(pull(sid, today), sid, name, drops[sid]) for sid, name in cands[key]}
        best, scored = pick(key, cands[key], pulled)
        if not best:
            if key == "ohare":
                sys.exit(f"O'Hare snowfall too thin to use: {scored}")
            print(f"{key}: no station clears {MIN_COVER:.0%} of snow-month days: {scored}")
            continue
        days = pulled[best[1]]
        last = max((d for d, v in days.items() if v[0] is not None), default=None)
        if not last:
            continue
        doc = station_doc(key, best, scored, days, last)
        doc["flaggedDropped"] = drops[best[1]]
        stations.append(doc)
    return {"about": "Daily snowfall (SNOW) and snow depth (SNWD) in inches at Chicago's airport weather stations, "
                     "from NOAA NCEI GHCN-Daily. Built by tools/dp_snow_fetch.py. Weather records only.",
            "source": {"name": "NOAA NCEI Global Historical Climatology Network daily (GHCN-Daily), daily-summaries",
                       "service": DATA, "search": SEARCH, "fetchedAt": fetched},
            "winters": [FIRST_WINTER, LAST_WINTER], "stations": stations}


def pull_station(sid, today):
    return get(DATA, {"dataset": "daily-summaries", "stations": sid, "dataTypes": "SNOW,SNWD", "startDate": START.isoformat(),
                      "endDate": today.isoformat(), "format": "json", "units": "standard", "includeStationName": "true",
                      "includeAttributes": "true"})


def write(doc):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, separators=(",", ":"))
    os.replace(tmp, OUT)


def selftest():
    def rows(sid, name, gaps=False, wrong=False):
        out, d = [], START
        while d <= dt.date(2026, 10, 20):
            if not (gaps and snow_months(d) and d.day % 3 == 0):
                out.append({"STATION": "XX" if wrong and d == START else sid, "NAME": name, "DATE": d.isoformat(),
                            "SNOW": " 2.5" if (d.month, d.day) == (1, 10) else ("9.0" if (d.month, d.day) == (2, 2) else "0.0"),
                            "SNOW_ATTRIBUTES": ",I,7," if (d.month, d.day) == (2, 2) else ",,7,", "SNWD": ""})
            d += dt.timedelta(1)
        return out
    search = [{"results": [{"stations": [{"id": "USW1", "name": "CHICAGO OHARE INTERNATIONAL AIRPORT, IL US"}]},
                           {"stations": [{"id": "USW2", "name": "CHICAGO MIDWAY AIRPORT, IL US"}]},
                           {"stations": [{"id": "USC3", "name": "CHICAGO MIDWAY AIRPORT 3 SW, IL US"}]},
                           {"stations": [{"id": "US1X", "name": "OAK LAWN 1.6 NW, IL US"}]}]}]
    c = candidates(search)
    assert [s for s, _ in c["ohare"]] == ["USW1"] and [s for s, _ in c["midway"]] == ["USW2", "USC3"], "names pick the airports"
    names = {"USW1": "CHICAGO OHARE INTERNATIONAL AIRPORT, IL US", "USW2": "CHICAGO MIDWAY AIRPORT, IL US", "USC3": "CHICAGO MIDWAY AIRPORT 3 SW, IL US"}
    pull = lambda sid, today: rows(sid, names[sid], gaps=(sid == "USW2"))
    doc = build(search, pull, dt.date(2026, 10, 27), "2026-10-27T07:00:00-0500")
    ids = {s["key"]: s["id"] for s in doc["stations"]}
    assert ids == {"ohare": "USW1", "midway": "USC3"}, f"the Midway station with fuller snowfall wins: {ids}"
    mid = [s for s in doc["stations"] if s["key"] == "midway"][0]
    assert any(x["id"] == "USW2" and x["cover"] < 0.9 for x in mid["considered"]), "the thin station is listed as considered"
    o = doc["stations"][0]
    assert o["end"] == "2026-10-20" and len(o["snow"]) == (dt.date(2026, 10, 20) - START).days + 1, "one value per day to the last report"
    assert o["snow"][(dt.date(1997, 1, 10) - START).days] == 2.5 and o["snwd"][0] is None, "values and nulls in place"
    assert o["snow"][(dt.date(1997, 2, 2) - START).days] is None and o["flaggedDropped"]["SNOW"] >= 30, "a quality-flagged value is dropped"
    for bad in (lambda sid, today: rows(sid, names[sid], wrong=True),
                lambda sid, today: [dict(r, SNOW="55.0") for r in rows(sid, names[sid])]):
        try:
            build(search, bad, dt.date(2026, 10, 27), "x")
            raise AssertionError("a wrong station row or an impossible value must stop the run")
        except SystemExit:
            pass
    try:
        build([{"results": search[0]["results"][1:]}], pull, dt.date(2026, 10, 27), "x")
        raise AssertionError("no O'Hare must stop the run")
    except SystemExit:
        pass
    print("dp_snow_fetch selftest: ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        now = dt.datetime.now(ZoneInfo("America/Chicago"))
        doc = build(search_all(), pull_station, now.date(), now.strftime("%Y-%m-%dT%H:%M:%S%z"))
        write(doc)
        for s in doc["stations"]:
            print(f"{s['key']}: {s['id']} {s['name']}, snow-month cover {s['cover']:.1%}, {s['start']} to {s['end']}; "
                  f"considered {[(x['id'], x['cover']) for x in s['considered']]}")
        print(f"wrote {OUT}: {os.path.getsize(OUT):,} bytes")
