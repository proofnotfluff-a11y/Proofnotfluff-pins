#!/usr/bin/env python3
"""Chicago Restaurant Inspection Leads (product #3, Oct 17, 2026): the weekly data layer.

Runs in GitHub Actions (.github/workflows/inspections-chicago.yml) because the cloud agents cannot reach
data.cityofchicago.org. Source: City of Chicago Data Portal, Food Inspections (dataset 4ijn-s7e5).

Buyers: pest control, commercial kitchen hood cleaning and grease trap companies. Every row is a licensed
food business; inspector names and inspection comments are never kept or published. Comments are read only
in the runner to set category labels, and travel onward only inside the encrypted review set (--full).

Usage: python3 tools/inspections_chicago.py --probe       violation codes, titles and keyword counts only
       python3 tools/inspections_chicago.py [--full PATH] the weekly sample (and the full list for members)
       python3 tools/inspections_chicago.py --selftest
"""
import argparse, collections, datetime as dt, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from permits_chicago import get, terms_text, title_name  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "permits", "inspections-chicago")
PORTAL = "https://data.cityofchicago.org"
DATASET = "4ijn-s7e5"
DATASET_PAGE = f"{PORTAL}/Health-Human-Services/Food-Inspections/{DATASET}"
AREAS = "igwz-8jzy"

VIOLATION = re.compile(r"^\s*(\d{1,2})\.\s*(.*?)(?:\s+-\s+Comments:\s*(.*))?$", re.S)
KEYWORDS = {
    "rodent": r"\bRODENT|\bMICE\b|\bMOUSE\b|\bRAT\b|\bRATS\b|GNAW",
    "droppings": r"DROPPING",
    "roach": r"ROACH",
    "flies": r"\bFLIES\b|\bFLY\b|FRUIT FLIES|GNATS",
    "insect": r"INSECT",
    "hood": r"\bHOOD",
    "filter": r"FILTER",
    "grease": r"GREASE",
    "grease_trap": r"GREASE TRAP|GREASE INTERCEPTOR|INTERCEPTOR",
    "exhaust": r"EXHAUST|VENTILATION",
    "plumbing": r"PLUMB|LEAK|DRAIN|BACKFLOW|SEWAGE",
}


def split_violations(text):
    """[(code, title, comments)] from the City's violations field ('38. TITLE - Comments: ... | 41. ...')."""
    out = []
    for part in (text or "").split(" | "):
        m = VIOLATION.match(part.strip())
        if m:
            out.append((int(m.group(1)), m.group(2).strip().upper(), (m.group(3) or "").upper()))
    return out


def pull(where, select=None, order="inspection_date DESC"):
    rows, offset = [], 0
    while True:
        params = {"$where": where, "$order": order, "$limit": 5000, "$offset": offset}
        if select:
            params["$select"] = select
        page = get(f"{PORTAL}/resource/{DATASET}.json", params)
        rows += page
        if len(page) < 5000 or offset > 50000:
            return rows
        offset += 5000


def probe():
    """Violation codes and titles with counts, and keyword hit counts per code. No business names, no comments."""
    since = (dt.date.today() - dt.timedelta(days=42)).isoformat()
    rows = pull(f"inspection_date >= '{since}'", select="inspection_type,results,facility_type,violations")
    titles, hits, by_result = collections.Counter(), collections.defaultdict(collections.Counter), collections.Counter()
    ftypes = collections.Counter()
    for r in rows:
        by_result[(r.get("results") or "", r.get("inspection_type") or "")] += 1
        ftypes[r.get("facility_type") or ""] += 1
        for code, title, comments in split_violations(r.get("violations")):
            titles[(code, title)] += 1
            for k, pat in KEYWORDS.items():
                if re.search(pat, comments):
                    hits[code][k] += 1
    out = {"ranAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "since": since, "inspections": len(rows),
           "codes": [{"code": c, "title": t, "count": n, "keywordHits": dict(hits[c])} for (c, t), n in sorted(titles.items())],
           "results": [{"result": a, "type": b, "count": n} for (a, b), n in by_result.most_common()],
           "facilityTypes": ftypes.most_common(40)}
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, "violation-codes.json"), "w"), indent=1)
    print(json.dumps({"inspections": len(rows), "codes": len(titles)}))


# ---------------------------------------------------------------- what each buyer cares about
# Violation codes and titles are the City's own: every Food Inspections record carries them in its
# "violations" field ("38. INSECTS, RODENTS, & ANIMALS NOT PRESENT - Comments: ..."), and the probe of Oct 17,
# 2026 (permits/inspections-chicago/violation-codes.json, 1,353 inspections since Sep 5) lists the titles used:
#   38 "INSECTS, RODENTS, & ANIMALS NOT PRESENT"                       -> pests (always)
#   56 "ADEQUATE VENTILATION & LIGHTING; DESIGNATED AREAS USED"        -> hood, when the note names a hood, filter,
#                                                                         grease or exhaust (lighting-only notes are not)
#   52 "SEWAGE & WASTE WATER PROPERLY DISPOSED"                         -> plumbing (always), and grease trap when
#                                                                         the note names grease
#   51 "PLUMBING INSTALLED; PROPER BACKFLOW DEVICES", 10 "ADEQUATE HANDWASHING SINKS PROPERLY SUPPLIED AND
#      ACCESSIBLE", 48 "WAREWASHING FACILITIES: INSTALLED, MAINTAINED & USED; TEST STRIPS" -> plumbing, when the
#      note names plumbing, a leak, drain, pipe, clog, sewage or backflow
#   49 "NON-FOOD/FOOD CONTACT SURFACES CLEAN", 55 "PHYSICAL FACILITIES INSTALLED, MAINTAINED & CLEAN",
#   53 "TOILET FACILITIES: PROPERLY CONSTRUCTED, SUPPLIED, & CLEANED", 54 "GARBAGE & REFUSE PROPERLY DISPOSED;
#      FACILITIES MAINTAINED"                                           -> cleaning (grease buildup flagged on its own)
# Any code whose note names rodents, droppings, roaches, flies or insects also counts as pests (55, 54 and 59
# "PREVIOUS PRIORITY FOUNDATION VIOLATION CORRECTED" carry many such notes); any note naming a grease trap or
# interceptor counts as grease trap, and any note naming a hood counts as hood. Notes are read here only to set
# these labels; they are never written to the sample, the profile or the members' list.
PEST_WORDS = re.compile(r"\bRODENT|\bMICE\b|\bMOUSE\b|\bRATS?\b|GNAW|DROPPING|ROACH|\bFLIES\b|FRUIT FL|GNATS|INSECT")
HOOD_WORDS = re.compile(r"\bHOODS?\b|FILTER|EXHAUST|\bGREASE")
TRAP_WORDS = re.compile(r"GREASE TRAP|GREASE INTERCEPTOR|INTERCEPTOR")
PLUMB_WORDS = re.compile(r"PLUMB|LEAK|DRAIN|BACKFLOW|PIPE|SEWAGE|CLOG")
CATEGORY_LABELS = {"pests": "Pests", "hood": "Hood and ventilation", "greaseTrap": "Grease trap",
                   "greaseBuildup": "Grease buildup", "plumbing": "Plumbing", "cleaning": "Cleaning and sanitation"}


def categorize(violations):
    """(sorted codes, sorted category keys) from one inspection's violations text."""
    codes, cats = set(), set()
    for code, title, note in split_violations(violations):
        codes.add(code)
        if code == 38 or PEST_WORDS.search(note):
            cats.add("pests")
        if (code == 56 and HOOD_WORDS.search(note)) or re.search(r"\bHOODS?\b", note):
            cats.add("hood")
        if TRAP_WORDS.search(note) or (code == 52 and "GREASE" in note):
            cats.add("greaseTrap")
        if code == 52 or (code in (10, 48, 51) and PLUMB_WORDS.search(note)):
            cats.add("plumbing")
        if code in (49, 53, 54, 55):
            cats.add("cleaning")
        if code in (49, 54, 55) and re.search(r"GREASE", note) and not TRAP_WORDS.search(note):
            cats.add("greaseBuildup")
    return sorted(codes), sorted(cats)


# Institutions (schools, day care, hospitals, senior meal sites) are left out: the buyers sell to food businesses,
# and a mobile food preparer is often one person with no fixed premises, so those are left out too.
EXCLUDE_FACILITY = re.compile(r"(?<!COOKING )\bSCHOOL\b|CHILDREN|DAYCARE|DAY CARE|HOSPITAL|LONG TERM CARE|NURSING|ASSISTED|"
                              r"GOLDEN DINER|SENIOR|MOBILE FOOD|^MFP$|PEDDLER", re.I)
FAILS = {"FAIL"}
FLAGGED = {"FAIL", "PASS W/ CONDITIONS"}


def street(addr):
    words = []
    for w in re.sub(r"\s+", " ", (addr or "").strip()).split(" "):
        if re.fullmatch(r"[NSEW]", w.upper()):
            words.append(w.upper())
        elif re.fullmatch(r"\d+(ST|ND|RD|TH)", w.upper()):
            words.append(w.lower())
        else:
            words.append(w.capitalize())
    return " ".join(words)


# ---------------------------------------------------------------- community areas (point in polygon)
def load_areas():
    """[(name, [rings])] from the City's Boundaries - Community Areas dataset (igwz-8jzy) as GeoJSON."""
    try:
        gj = get(f"{PORTAL}/resource/{AREAS}.geojson", {"$limit": 200})
    except SystemExit:
        return []
    from permits_chicago import AREA_NAMES
    out = []
    for f in gj.get("features", []):
        name = ((f.get("properties") or {}).get("community") or "").title()
        name = AREA_NAMES.get(name, name)
        g = f.get("geometry") or {}
        polys = g.get("coordinates") or []
        if g.get("type") == "Polygon":
            polys = [polys]
        out.append((name, [ring for poly in polys for ring in poly[:1]]))
    return out


def area_of(lat, lon, areas):
    try:
        x, y = float(lon), float(lat)
    except (TypeError, ValueError):
        return ""
    for name, rings in areas:
        for ring in rings:
            inside = False
            for i in range(len(ring)):
                x1, y1 = ring[i][0], ring[i][1]
                x2, y2 = ring[i - 1][0], ring[i - 1][1]
                if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-12) + x1:
                    inside = not inside
            if inside:
                return name
    return ""


# ---------------------------------------------------------------- the weekly build
def record(r, areas, fails30):
    codes, cats = categorize(r.get("violations"))
    result = (r.get("results") or "").strip()
    itype = (r.get("inspection_type") or "").strip()
    lic = str(r.get("license_") or "").split(".")[0]
    segs = []
    if result.upper() in FAILS and "pests" in cats:
        segs.append("pests")
    if result.upper() in FLAGGED and ({"hood", "greaseTrap", "greaseBuildup"} & set(cats)):
        segs.append("hoodGrease")
    if itype.upper().startswith("LICENSE") and result.upper() in {"PASS", "FAIL", "PASS W/ CONDITIONS", "NOT READY"}:
        segs.append("newOpening")
    if result.upper() in FAILS and fails30.get(lic, 0) >= 2:
        segs.append("repeatFail")
    return {
        "inspection": str(r.get("inspection_id") or ""),
        "business": title_name(r.get("dba_name") or r.get("aka_name") or ""),
        "license": lic,
        "address": street(r.get("address")),
        "zip": (r.get("zip") or "").split(".")[0],
        "communityArea": area_of(r.get("latitude"), r.get("longitude"), areas),
        "facilityType": (r.get("facility_type") or "").strip().title(),
        "risk": (r.get("risk") or "").strip(),
        "inspectionType": itype.title(),
        "result": result,
        "date": (r.get("inspection_date") or "")[:10],
        "codes": codes,
        "categories": [CATEGORY_LABELS[c] for c in cats],
        "categoryKeys": cats,
        "segments": segs,
        "failsLast30": fails30.get(lic, 0),
    }


def build(rows, areas, today):
    """(records this week, counts) from inspections of the last 37 days (7 for the list, 30 for repeat failures)."""
    week = (today - dt.timedelta(days=7)).isoformat()
    month = (today - dt.timedelta(days=30)).isoformat()
    fails30 = collections.Counter()
    for r in rows:
        if (r.get("inspection_date") or "")[:10] >= month and (r.get("results") or "").upper() in FAILS:
            fails30[str(r.get("license_") or "").split(".")[0]] += 1
    reasons = collections.Counter()
    out, seen = [], set()
    for r in rows:
        if (r.get("inspection_date") or "")[:10] < week:
            continue
        if EXCLUDE_FACILITY.search(r.get("facility_type") or ""):
            reasons["institution or mobile vendor"] += 1; continue
        if not (r.get("dba_name") or r.get("aka_name")) or not r.get("address"):
            reasons["no business name or address"] += 1; continue
        rec = record(r, areas, fails30)
        if not rec["segments"]:
            reasons["no lead segment (passed, or no buyer-relevant violation)"] += 1; continue
        if rec["inspection"] in seen:
            continue
        seen.add(rec["inspection"])
        out.append(rec)
    out.sort(key=lambda x: (x["date"], x["business"]), reverse=True)
    return out, reasons


SEGMENTS = {"pests": "Failed with pests", "hoodGrease": "Hood, grease or grease trap problems",
            "newOpening": "About to open (license inspection)", "repeatFail": "Repeat failures in 30 days"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", default="")
    ap.add_argument("--top", type=int, default=10)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    today = now.date()
    meta = get(f"{PORTAL}/api/views/{DATASET}.json")
    cols = [c.get("fieldName") for c in meta.get("columns", [])]
    need = {"dba_name", "license_", "address", "inspection_date", "inspection_type", "results", "violations", "facility_type"}
    if need - set(cols):
        raise SystemExit(f"dataset columns changed, missing {sorted(need - set(cols))}")
    upd = meta.get("rowsUpdatedAt")
    upd_iso = dt.datetime.fromtimestamp(upd, dt.timezone.utc).isoformat(timespec="seconds") if upd else ""
    since = (today - dt.timedelta(days=37)).isoformat()
    rows = pull(f"inspection_date >= '{since}'")
    areas = load_areas()
    recs, reasons = build(rows, areas, today)
    seg_counts = {k: sum(k in r["segments"] for r in recs) for k in SEGMENTS}
    public = lambda r: {k: r[k] for k in ("business", "address", "communityArea", "facilityType", "result", "inspectionType", "date", "categories")}
    source = {"name": "City of Chicago Data Portal, Food Inspections", "url": DATASET_PAGE, "rowsUpdatedAt": upd_iso,
              "fetchedAt": now.isoformat(timespec="seconds"),
              "modified": ("Filtered by ProofNotFluff: food inspections of the last 7 days at licensed food businesses (schools, day "
                           "care, hospitals, senior meal sites and mobile vendors left out) that failed with pest violations, failed "
                           "or passed with conditions with hood, grease or grease trap violations, had a license (pre-opening) "
                           "inspection, or failed twice in 30 days. Violation notes are read only to set category labels; "
                           "inspector notes are not republished. Business-level fields only."),
              "terms": "https://www.chicago.gov/city/en/narr/foia/data_disclaimer.html"}
    sample = {"source": source, "window": {"from": (today - dt.timedelta(days=7)).isoformat(), "to": today.isoformat()},
              "counts": {"fetched": len(rows), "kept": len(recs), "segments": seg_counts, "excluded": dict(reasons),
                         "areas": collections.Counter(r["communityArea"] for r in recs if r["communityArea"]).most_common(10)},
              "segments": {k: [public(r) for r in recs if k in r["segments"]][: a.top] for k in SEGMENTS},
              "segmentNames": SEGMENTS}
    profile = {"fetchedAt": source["fetchedAt"], "rowsUpdatedAt": upd_iso, "columns": cols,
               "results": dict(collections.Counter(r.get("results") or "" for r in rows)),
               "inspectionTypes": dict(collections.Counter(r.get("inspection_type") or "" for r in rows).most_common(20)),
               "facilityTypes": dict(collections.Counter(r.get("facility_type") or "" for r in rows).most_common(30)),
               "codesThisWeek": dict(collections.Counter(c for r in recs for c in r["codes"]).most_common()),
               "areasLoaded": len(areas)}
    json.dump(sample, open(os.path.join(OUT, "sample.json"), "w"), indent=1)
    json.dump(profile, open(os.path.join(OUT, "profile.json"), "w"), indent=1)
    try:
        open(os.path.join(OUT, "source-terms.txt"), "w").write(terms_text())
    except SystemExit as e:
        open(os.path.join(OUT, "source-terms.txt"), "w").write(f"Could not fetch the terms page: {e}\n")
    if a.full:
        kept = {r["inspection"] for r in recs}
        review = [{"inspection": str(r.get("inspection_id")), "kept": str(r.get("inspection_id")) in kept,
                   "raw": r.get("violations") or "", "result": r.get("results"), "type": r.get("inspection_type"),
                   "facility": r.get("facility_type")}
                  for r in rows if (r.get("inspection_date") or "")[:10] >= (today - dt.timedelta(days=7)).isoformat()]
        json.dump({"source": source, "window": sample["window"], "counts": sample["counts"], "records": recs, "review": review},
                  open(a.full, "w"), indent=1)
    print(json.dumps({"fetched": len(rows), "kept": len(recs), "segments": seg_counts, "excluded": dict(reasons), "areas": len(areas)}))


# ---------------------------------------------------------------- planted cases (real City titles, invented notes)
V = {38: "38. INSECTS, RODENTS, & ANIMALS NOT PRESENT", 56: "56. ADEQUATE VENTILATION & LIGHTING; DESIGNATED AREAS USED",
     52: "52. SEWAGE & WASTE WATER PROPERLY DISPOSED", 51: "51. PLUMBING INSTALLED; PROPER BACKFLOW DEVICES",
     49: "49. NON-FOOD/FOOD CONTACT SURFACES CLEAN", 55: "55. PHYSICAL FACILITIES INSTALLED, MAINTAINED & CLEAN",
     2: "2. CITY OF CHICAGO FOOD SERVICE SANITATION CERTIFICATE", 59: "59. PREVIOUS PRIORITY FOUNDATION VIOLATION CORRECTED"}
CAT_CASES = [
    (f"{V[38]} - Comments: OBSERVED APPROX 25 MICE DROPPINGS ALONG WALL BASE IN DRY STORAGE.", ["pests"]),
    (f"{V[56]} - Comments: HEAVY GREASE BUILD UP ON HOOD FILTERS ABOVE COOKING LINE. CLEAN AND MAINTAIN.", ["hood"]),
    (f"{V[56]} - Comments: MUST PROVIDE LIGHT SHIELDS IN PREP AREA.", []),
    (f"{V[52]} - Comments: GREASE TRAP OVERFLOWING IN BASEMENT. MUST SERVICE.", ["greaseTrap", "plumbing"]),
    (f"{V[51]} - Comments: LEAKING PIPE UNDER 3 COMPARTMENT SINK.", ["plumbing"]),
    (f"{V[49]} - Comments: GREASE BUILD UP ON FRYERS AND SHELVING.", ["cleaning", "greaseBuildup"]),
    (f"{V[55]} - Comments: DEAD ROACHES ON FLOOR UNDER DISH MACHINE.", ["cleaning", "pests"]),
    (f"{V[2]} - Comments: NO CERTIFIED FOOD MANAGER ON DUTY.", []),
    (f"{V[59]} - Comments: PREVIOUS VIOLATION #38 NOT CORRECTED, STILL OBSERVED RODENT DROPPINGS.", ["pests"]),
    (f"{V[38]} - Comments: OBSERVED FLIES IN KITCHEN | {V[56]} - Comments: EXHAUST HOOD NOT WORKING", ["hood", "pests"]),
]


def selftest():
    bad = [(t[:60], categorize(t)[1], want) for t, want in CAT_CASES if categorize(t)[1] != sorted(want)]
    if bad:
        raise SystemExit("inspection selftest FAIL: " + json.dumps(bad))
    today = dt.date(2026, 10, 17)
    base = {"address": "1234 W MAIN ST", "zip": "60601", "latitude": "41.88", "longitude": "-87.63", "risk": "Risk 1 (High)"}
    rows = [
        dict(base, inspection_id="1", dba_name="ACME TACOS", license_="111", facility_type="Restaurant", inspection_type="Canvass",
             results="Fail", inspection_date="2026-10-15T00:00:00.000", violations=CAT_CASES[0][0]),
        dict(base, inspection_id="2", dba_name="ACME TACOS", license_="111", facility_type="Restaurant", inspection_type="Complaint",
             results="Fail", inspection_date="2026-09-30T00:00:00.000", violations=CAT_CASES[7][0]),
        dict(base, inspection_id="3", dba_name="NEW PLACE", license_="222", facility_type="Restaurant", inspection_type="License",
             results="Pass", inspection_date="2026-10-14T00:00:00.000", violations=""),
        dict(base, inspection_id="4", dba_name="SCHOOL LUNCH", license_="333", facility_type="School", inspection_type="Canvass",
             results="Fail", inspection_date="2026-10-14T00:00:00.000", violations=CAT_CASES[0][0]),
        dict(base, inspection_id="5", dba_name="FRY HOUSE", license_="444", facility_type="Restaurant", inspection_type="Canvass",
             results="Pass w/ Conditions", inspection_date="2026-10-13T00:00:00.000", violations=CAT_CASES[1][0]),
        dict(base, inspection_id="6", dba_name="CLEAN DINER", license_="555", facility_type="Restaurant", inspection_type="Canvass",
             results="Pass", inspection_date="2026-10-13T00:00:00.000", violations=CAT_CASES[1][0]),
    ]
    recs, reasons = build(rows, [("Loop", [[[-87.7, 41.8], [-87.6, 41.8], [-87.6, 41.9], [-87.7, 41.9], [-87.7, 41.8]]])], today)
    by = {r["inspection"]: r for r in recs}
    assert set(by) == {"1", "3", "5"}, sorted(by)
    assert by["1"]["segments"] == ["pests", "repeatFail"] and by["1"]["failsLast30"] == 2, by["1"]
    assert by["3"]["segments"] == ["newOpening"], by["3"]
    assert by["5"]["segments"] == ["hoodGrease"], by["5"]
    assert by["1"]["communityArea"] == "Loop" and by["1"]["address"] == "1234 W Main St" and by["1"]["business"] == "Acme Tacos"
    blob = json.dumps(recs)
    assert "COMMENTS" not in blob.upper() and "DROPPINGS" not in blob.upper(), "notes leaked into the records"
    assert reasons["institution or mobile vendor"] == 1
    assert street("3512 E 118TH ST") == "3512 E 118th St"
    print(f"inspection selftest ok ({len(CAT_CASES)} planted violation cases, 6 planted inspections)")


if __name__ == "__main__":
    if sys.argv[1:] == ["--probe"]:
        probe()
    elif sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        main()
