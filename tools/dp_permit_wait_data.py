#!/usr/bin/env python3
"""Chicago permit wait times and weekly wrecking permits: the data layer for two free pages
(/chicago-permit-wait-times/, tools/dp_permit_wait.py, and /chicago-demolition-rodent-baiting/, tools/dp_demo_baiting.py).
Todd's go, Oct 27, 2026, 12:17 pm: "Let's do them all" (coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md).

Runs in GitHub Actions (.github/workflows/dp_permit_wait.yml), because the cloud agents cannot reach
data.cityofchicago.org. Source: City of Chicago Data Portal, Building Permits (dataset ydr8-5enu, updated daily).
processing_time is the City's own field: days from application_start_date to issue_date.

What leaves the runner: counts and day figures by permit type, review type, month and community area. The query asks
the City for six columns only (KEEP); every contact_* column, the street address, coordinates, PINs, permit numbers and
work descriptions are never requested, and strip() drops anything else a row carries before it is counted. No row is
ever written to disk.

Usage: python3 tools/dp_permit_wait_data.py            pull and write both data files
       python3 tools/dp_permit_wait_data.py --selftest  planted rows, no network
"""
import argparse, datetime as dt, json, math, os, re, sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_WAIT = os.path.join(ROOT, "site", "datapages", "dp_permit_wait", "stats.json")
OUT_DEMO = os.path.join(ROOT, "site", "datapages", "dp_demo_baiting", "wrecking.json")
PORTAL = "https://data.cityofchicago.org"
DATASET = "ydr8-5enu"
DATASET_PAGE = f"{PORTAL}/Buildings/Building-Permits/{DATASET}"
CHI = ZoneInfo("America/Chicago")
KEEP = ("permit_type", "review_type", "application_start_date", "issue_date", "processing_time", "community_area")
MIN_N = 20        # fewer permits than this in a group: the page shows the count, never a median or 80th percentile
PAGE_FLOOR = 300  # a permit type gets its own sub-page with at least this many issued permits in the last 12 months
WRECK = re.compile(r"WRECK|DEMOLI")

# Plain words for the City's review paths (dataset values read through the profile each run; an unknown value keeps
# the City's own words in title case, so a new path shows up on the page instead of vanishing).
REVIEW_WORDS = {"EXPRESS PERMIT PROGRAM": "Express Permit Program", "STANDARD PLAN REVIEW": "Standard Plan Review",
                "SELF CERT": "Self Certification", "SELF CERTIFICATION": "Self Certification", "EASY PERMIT WEB": "Easy Permit (online)",
                "EASY PERMIT": "Easy Permit", "SIGNS": "Signs", "ELECTRIC WIRING": "Electrical wiring", "WRECKING/DEMOLITION": "Wrecking and demolition",
                "DIRECT DEVELOPER SERVICES": "Direct Developer Services", "SCAFFOLDING": "Scaffolding", "ELEVATOR EQUIPMENT": "Elevator equipment",
                "REVIEW PERMIT": "Review permit", "PORCH CONSTRUCTION": "Porch construction", "REINSTATE REVOKED PERMIT": "Reinstated permit"}
SMALL = {"and", "or", "of", "the", "a", "to", "for", "in"}


def title(s):
    words = re.sub(r"\s+", " ", (s or "").strip()).lower().split(" ")
    return " ".join(w if (i and w in SMALL) else w[:1].upper() + w[1:] for i, w in enumerate(words) if w) or "Not given"


def review_label(v):
    k = re.sub(r"\s+", " ", (v or "").strip().upper())
    return REVIEW_WORDS.get(k) or title(k)


def type_label(v):
    k = re.sub(r"^PERMIT\s*-\s*", "", re.sub(r"\s+", " ", (v or "").strip().upper()))
    return title(k.replace("/", " and ").replace("EASY PERMIT PROCESS", "EASY PERMIT"))


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def strip(r):
    """Keep the six columns the pages count; anything else on a row (contacts, address, location) is dropped here."""
    return {k: r.get(k) for k in KEEP}


def pctl(v, p):
    """Nearest rank: the smallest value with at least p of the permits at or under it ("8 in 10 were issued within")."""
    if not v:
        return None
    return v[max(0, math.ceil(p * len(v)) - 1)]


def summary(days):
    v = sorted(days)
    n = len(v)
    out = {"n": n}
    if n >= MIN_N:
        out.update({"med": pctl(v, 0.5), "p80": pctl(v, 0.8), "p90": pctl(v, 0.9),
                    "sameDay": round(sum(1 for x in v if x == 0) / n * 100, 1),
                    "over90": round(sum(1 for x in v if x > 90) / n * 100, 1),
                    "over365": round(sum(1 for x in v if x > 365) / n * 100, 1)})
    return out


def parse_day(s):
    try:
        return dt.date.fromisoformat((s or "")[:10])
    except ValueError:
        return None


def area_of(v):
    try:
        k = int(float(v))
    except (TypeError, ValueError):
        return 0
    return k if 1 <= k <= 77 else 0


def months_back(first_of_this_month, k):
    y, m = first_of_this_month.year, first_of_this_month.month - k
    while m <= 0:
        m += 12; y -= 1
    return dt.date(y, m, 1)


def windows(today):
    """All windows end before `today` (the pull day is incomplete). Months: the 24 complete months before this one."""
    first = today.replace(day=1)
    return {"today": today, "yday": today - dt.timedelta(days=1), "from12": today - dt.timedelta(days=365),
            "months": [months_back(first, k).strftime("%Y-%m") for k in range(24, 0, -1)],
            "from": months_back(first, 24), "recent3": [months_back(first, k).strftime("%Y-%m") for k in (3, 2, 1)],
            "year3": [months_back(first, k).strftime("%Y-%m") for k in (15, 14, 13)]}


def clean(rows, w):
    """Rows to records. Kept: issued inside the window with a usable day count. Counted by reason when left out."""
    recs, drop = [], {"noDays": 0, "negative": 0, "outside": 0}
    match = checked = 0
    for raw in rows:
        r = strip(raw)
        iss = parse_day(r["issue_date"])
        if not iss or iss < w["from"] or iss >= w["today"]:
            drop["outside"] += 1
            continue
        try:
            days = int(float(r["processing_time"]))
        except (TypeError, ValueError):
            drop["noDays"] += 1
            continue
        if days < 0:
            drop["negative"] += 1
            continue
        st = parse_day(r["application_start_date"])
        if st:
            checked += 1
            match += (iss - st).days == days
        recs.append({"t": (r["permit_type"] or "").strip().upper(), "r": (r["review_type"] or "").strip().upper(),
                     "a": area_of(r["community_area"]), "day": iss, "m": iss.strftime("%Y-%m"), "d": days})
    return recs, drop, {"checked": checked, "match": match}


def monthly(recs, w):
    by = {}
    for x in recs:
        by.setdefault(x["m"], []).append(x["d"])
    return [dict(summary(by.get(m, [])), m=m) for m in w["months"]]


def trend(recs, w):
    now = [x["d"] for x in recs if x["m"] in w["recent3"]]
    then = [x["d"] for x in recs if x["m"] in w["year3"]]
    a, b = summary(now), summary(then)
    return {"months": w["recent3"], "yearMonths": w["year3"], "now": a, "then": b}


def areas(recs, names):
    out = []
    for k in sorted(names):
        v = [x["d"] for x in recs if x["a"] == k]
        out.append(dict(summary(v), a=k, name=names[k]))
    return out


def block(recs, w, names, with_areas=True):
    last12 = [x for x in recs if x["day"] >= w["from12"]]
    out = {"last12": summary([x["d"] for x in last12]), "monthly": monthly(recs, w), "trend": trend(recs, w)}
    if with_areas:
        out["areas"] = areas(last12, names)
        out["noArea12"] = sum(1 for x in last12 if not x["a"])
    return out


def build(rows, today, fetched, rows_updated, names):
    w = windows(today)
    recs, drop, chk = clean(rows, w)
    last12 = [x for x in recs if x["day"] >= w["from12"]]
    tcount, rcount = {}, {}
    for x in recs:   # every type and path seen in the 24 months, ordered by the last 12 months, then the 24
        y = 1 if x["day"] >= w["from12"] else 0
        tcount[x["t"]] = [a + b for a, b in zip(tcount.get(x["t"], [0, 0]), (y, 1))]
        rcount[x["r"]] = [a + b for a, b in zip(rcount.get(x["r"], [0, 0]), (y, 1))]
    order = lambda c: sorted(c, key=lambda k: (-c[k][0], -c[k][1], k))
    reviews = []
    for r in order(rcount):
        sub = [x for x in recs if x["r"] == r]
        reviews.append(dict(block(sub, w, names), key=r, label=review_label(r)))
    types = []
    for t in order(tcount):
        sub = [x for x in recs if x["t"] == t]
        bt = dict(block(sub, w, names), key=t, label=type_label(t), slug=slug(type_label(t)), page=tcount[t][0] >= PAGE_FLOOR)
        bt["reviews"] = []
        for r in sorted({x["r"] for x in sub if x["day"] >= w["from12"]}, key=lambda k: -sum(1 for x in sub if x["r"] == k and x["day"] >= w["from12"])):
            rs = [x for x in sub if x["r"] == r]
            bt["reviews"].append(dict(block(rs, w, names, with_areas=False), key=r, label=review_label(r)))
        types.append(bt)
    std = next((r for r in reviews if r["key"] == "STANDARD PLAN REVIEW"), None)
    exp = next((r for r in reviews if r["key"] == "EXPRESS PERMIT PROGRAM"), None)
    return {
        "about": ("Counts and day figures only, from City of Chicago Building Permits (ydr8-5enu): issued permits by permit type, "
                  "review type, month and community area. No permit number, address, contact or description is kept. Built by tools/dp_permit_wait_data.py."),
        "source": {"name": "Building Permits", "dataset": DATASET, "url": DATASET_PAGE, "fetchedAt": fetched, "rowsUpdatedAt": rows_updated,
                   "field": "processing_time", "fieldMeans": "Number of days between APPLICATION_START_DATE and ISSUE_DATE"},
        "window": {"from": w["from"].isoformat(), "to": w["yday"].isoformat(), "from12": w["from12"].isoformat(),
                   "months": w["months"], "recent3": w["recent3"], "year3": w["year3"]},
        "rules": {"minN": MIN_N, "pageFloor": PAGE_FLOOR, "percentile": "nearest rank"},
        "counts": {"rows": len(rows), "kept": len(recs), "last12": len(last12), "dropped": drop,
                   "checkedAgainstDates": chk["checked"], "matchesDates": chk["match"]},
        "all": block(recs, w, names),
        "reviews": reviews,
        "types": types,
        "areaStd": std["areas"] if std else [],
        "areaExp": exp["areas"] if exp else [],
    }


def weeks_of(recs, today):
    out = []
    for k in range(12, 0, -1):
        a = today - dt.timedelta(days=7 * k)
        b = a + dt.timedelta(days=6)
        out.append({"from": a.isoformat(), "to": b.isoformat(), "count": sum(1 for x in recs if a <= x["day"] <= b)})
    return out


def build_wreck(rows, today, fetched, rows_updated, names):
    """Wrecking and demolition permits issued, counted by community area and week (from the same pull)."""
    w = windows(today)
    recs, drop, _ = clean(rows, w)
    wr = [x for x in recs if WRECK.search(x["t"])]
    d7, d30 = today - dt.timedelta(days=7), today - dt.timedelta(days=30)
    areas_out = []
    for k in sorted(names):
        v = [x for x in wr if x["a"] == k]
        areas_out.append({"a": k, "name": names[k], "d7": sum(1 for x in v if x["day"] >= d7), "d30": sum(1 for x in v if x["day"] >= d30),
                          "d365": sum(1 for x in v if x["day"] >= w["from12"])})
    last12 = [x for x in wr if x["day"] >= w["from12"]]
    return {
        "about": ("Counts only, from City of Chicago Building Permits (ydr8-5enu): wrecking and demolition permits issued, by community area "
                  "and week. No permit number, address, contact or description is kept. Built by tools/dp_permit_wait_data.py."),
        "source": {"name": "Building Permits", "dataset": DATASET, "url": DATASET_PAGE, "fetchedAt": fetched, "rowsUpdatedAt": rows_updated,
                   "types": sorted({x["t"] for x in wr})},
        "window": {"from7": d7.isoformat(), "from30": d30.isoformat(), "from12": w["from12"].isoformat(), "to": w["yday"].isoformat()},
        "counts": {"d7": sum(1 for x in wr if x["day"] >= d7), "d30": sum(1 for x in wr if x["day"] >= d30), "d365": len(last12),
                   "noArea30": sum(1 for x in wr if x["day"] >= d30 and not x["a"]),
                   "areasWith30": sum(1 for a in areas_out if a["d30"])},
        "wait": summary([x["d"] for x in last12]),
        "areas": areas_out,
        "weeks": weeks_of(wr, today),
        "monthly": [{"m": m, "count": sum(1 for x in wr if x["m"] == m)} for m in w["months"]],
    }


def pull():
    sys.path.insert(0, HERE)
    from permits_chicago import get
    from rodents_chicago import AREAS
    now = dt.datetime.now(CHI)
    w = windows(now.date())
    api = f"{PORTAL}/resource/{DATASET}.json"
    where = f"issue_date >= '{w['from'].isoformat()}T00:00:00' AND issue_date < '{w['today'].isoformat()}T00:00:00'"
    total = int(float(get(api, {"$select": "count(*) AS n", "$where": where})[0]["n"]))
    rows, off = [], 0
    while off < total:
        page = get(api, {"$select": ",".join(KEEP), "$where": where, "$order": "issue_date, id", "$limit": 50000, "$offset": off})
        if not page:
            break
        rows += [strip(r) for r in page]   # nothing else ever exists in memory past this line
        off += len(page)
    if len(rows) < 20000:
        raise SystemExit(f"only {len(rows)} issued permits in 24 months: the query or the dataset changed; not writing")
    try:
        meta = get(f"{PORTAL}/api/views/{DATASET}.json")
        ru = dt.datetime.fromtimestamp(int(meta.get("rowsUpdatedAt")), dt.timezone.utc).isoformat()
    except Exception:
        ru = None
    fetched = now.strftime("%Y-%m-%dT%H:%M:%S%z")
    d = build(rows, now.date(), fetched, ru, AREAS)
    k = d["counts"]
    if k["checkedAgainstDates"] and k["matchesDates"] / k["checkedAgainstDates"] < 0.95:
        raise SystemExit(f"processing_time matches the two dates on only {k['matchesDates']} of {k['checkedAgainstDates']} rows; not writing")
    wr = build_wreck(rows, now.date(), fetched, ru, AREAS)
    for path, obj in ((OUT_WAIT, d), (OUT_DEMO, wr)):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump(obj, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"permit wait: {k['rows']} rows, kept {k['kept']}, last 12 months {k['last12']}, dropped {k['dropped']}, "
          f"dates match {k['matchesDates']} of {k['checkedAgainstDates']}; types {[(t['label'], t['last12']['n']) for t in d['types']]}; "
          f"reviews {[(r['label'], r['last12']['n']) for r in d['reviews']]}")
    print(f"wrecking: 7 days {wr['counts']['d7']}, 30 days {wr['counts']['d30']}, 12 months {wr['counts']['d365']}, types {wr['source']['types']}")


def selftest():
    names = {6: "Lake View", 24: "West Town", 25: "Austin"}
    today = dt.date(2026, 10, 27)
    w = windows(today)
    assert w["months"][0] == "2024-10" and w["months"][-1] == "2026-09" and len(w["months"]) == 24, w["months"]
    assert w["recent3"] == ["2026-07", "2026-08", "2026-09"] and w["year3"] == ["2025-07", "2025-08", "2025-09"], w
    assert pctl([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 0.5) == 4 and pctl([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 0.8) == 7 and pctl([5], 0.8) == 5
    rows = []
    for i in range(60):        # standard review, renovation, Lake View, 60 permits issued Sep 2026 taking 0 to 59 days
        iss = dt.date(2026, 9, 1 + i % 28)
        rows.append({"permit_type": "PERMIT - RENOVATION/ALTERATION", "review_type": "STANDARD PLAN REVIEW", "issue_date": iss.isoformat() + "T00:00:00.000",
                     "application_start_date": (iss - dt.timedelta(days=i)).isoformat() + "T00:00:00.000", "processing_time": str(i),
                     "community_area": "6", "contact_1_name": "PLANTED PERSON", "street_name": "PLANTED", "latitude": "41.9"})
    for i in range(25):        # express, same day, West Town, a year earlier
        rows.append({"permit_type": "PERMIT - EASY PERMIT PROCESS", "review_type": "EXPRESS PERMIT PROGRAM", "issue_date": "2025-08-04T00:00:00.000",
                     "application_start_date": "2025-08-04T00:00:00.000", "processing_time": "0", "community_area": "24.0"})
    for i in range(3):         # wrecking permits last week, one with no community area
        rows.append({"permit_type": "PERMIT - WRECKING/DEMOLITION", "review_type": "WRECKING/DEMOLITION", "issue_date": "2026-10-22T00:00:00.000",
                     "application_start_date": "2026-09-22T00:00:00.000", "processing_time": "30", "community_area": "25" if i else None})
    rows.append({"permit_type": "PERMIT - SIGNS", "review_type": "SIGNS", "issue_date": "2026-10-27T00:00:00.000", "processing_time": "3"})  # today: outside
    rows.append({"permit_type": "PERMIT - SIGNS", "review_type": "SIGNS", "issue_date": "2026-10-20T00:00:00.000", "processing_time": None})
    rows.append({"permit_type": "PERMIT - SIGNS", "review_type": "SIGNS", "issue_date": "2026-10-20T00:00:00.000", "processing_time": "-2"})
    d = build(rows, today, "2026-10-27T07:00:00-0500", None, names)
    text = json.dumps({k: v for k, v in d.items() if k != "about"})
    assert "PLANTED" not in text and "41.9" not in text and "contact" not in text and "street" not in text, "contacts and address never reach the file"
    assert d["counts"]["dropped"] == {"noDays": 1, "negative": 1, "outside": 1}, d["counts"]
    assert d["counts"]["checkedAgainstDates"] == 88 and d["counts"]["matchesDates"] == 88, d["counts"]
    ren = next(t for t in d["types"] if t["key"] == "PERMIT - RENOVATION/ALTERATION")
    assert ren["label"] == "Renovation and Alteration" and ren["slug"] == "renovation-and-alteration" and ren["page"] is False
    assert ren["last12"]["n"] == 60 and ren["last12"]["med"] == 29 and ren["last12"]["p80"] == 47, ren["last12"]
    lv = next(a for a in ren["areas"] if a["a"] == 6)
    assert lv["n"] == 60 and lv["med"] == 29 and "med" not in next(a for a in ren["areas"] if a["a"] == 24), "small groups: count only"
    exp = next(r for r in d["reviews"] if r["key"] == "EXPRESS PERMIT PROGRAM")
    assert exp["label"] == "Express Permit Program" and exp["last12"] == {"n": 0} and exp["trend"]["then"]["n"] == 25 and exp["trend"]["then"]["sameDay"] == 100.0
    assert next(m for m in d["all"]["monthly"] if m["m"] == "2026-09")["n"] == 60
    assert review_label("SOME NEW PATH") == "Some New Path" and type_label("PERMIT - WRECKING/DEMOLITION") == "Wrecking and Demolition"
    assert d["all"]["noArea12"] == 1
    wr = build_wreck(rows, today, "2026-10-27T07:00:00-0500", None, names)
    assert wr["counts"]["d7"] == 3 and wr["counts"]["noArea30"] == 1 and wr["counts"]["areasWith30"] == 1, wr["counts"]
    assert wr["weeks"][-1] == {"from": "2026-10-20", "to": "2026-10-26", "count": 3}, wr["weeks"][-1]
    assert next(a for a in wr["areas"] if a["a"] == 25)["d7"] == 2 and "PLANTED" not in json.dumps(wr)
    assert wr["wait"] == {"n": 3}, "three permits: no median"
    print("dp_permit_wait_data selftest: ok (windows, nearest rank, privacy strip, drops, date check, small groups, labels, wrecking weeks)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    selftest() if a.selftest else pull()
