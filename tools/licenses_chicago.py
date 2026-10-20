#!/usr/bin/env python3
"""Chicago New Business Licenses (lead product #4 in the LEADS FOCUS line, coo/PIVOT.md): the weekly data layer.

Runs in GitHub Actions (.github/workflows/licenses-chicago.yml) because the cloud agents cannot reach
data.cityofchicago.org. Source: City of Chicago Data Portal, Business Licenses (dataset r5kz-chrr).

Buyers: vendors who sell to a business in its first months (POS and payments, signs, insurance, bookkeeping and
payroll, commercial cleaning, pest control, hood cleaning, waste and recycling, uniforms and supplies), sorted by
the trade of the new business. Every row is a newly issued license at a business site. Business-level fields only:
the legal name is read in the runner only to judge whether a name could be a person's; it is never written out.
Rows whose shown name could be a person's name, temporary or person-held licenses, and home-based licenses are left
out (the planted cases in selftest() pin every rule).

Usage: python3 tools/licenses_chicago.py --probe        column names and counts by license type and activity only
       python3 tools/licenses_chicago.py [--full PATH]  the weekly free sample (and the members' full list, never committed)
       python3 tools/licenses_chicago.py --selftest
"""
import argparse, collections, datetime as dt, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from permits_chicago import get, terms_text  # noqa: E402
from inspections_chicago import dba_case, street, load_areas, area_of  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "permits", "licenses-chicago")
PORTAL = "https://data.cityofchicago.org"
DATASET = "r5kz-chrr"
DATASET_PAGE = f"{PORTAL}/Community-Economic-Development/Business-Licenses/{DATASET}"
TERMS = "https://www.chicago.gov/city/en/narr/foia/data_disclaimer.html"
WINDOW_DAYS = 30      # members' list: licenses issued in the last 30 days; the free sample shows the last 7

# Licenses held by a person or for a day or a season, not a business site a vendor can visit (left out).
SKIP_LICENSES = re.compile(r"^(?:PEDDLER|PHARMACEUTICAL REPRESENTATIVE|SPECIAL EVENT|POP-UP|RAFFLE|TOWING|TOW TRUCK|SHARED HOUSING|"
                           r"HOME OCCUPATION|HOME REPAIR|MOBILE FOOD|PUBLIC CHAUFFEUR|VALET|BED-AND-BREAKFAST|VACATION RENTAL|"
                           r"ITINERANT|MASSAGE THERAPIST|BODY ART PRACTITIONER|SCAVENGER|EXPEDITOR|BUSINESS AFFAIRS|"
                           r"RESIDENTIAL REAL ESTATE DEVELOPER)", re.I)
# Trade segments, first match wins: (key, label, license or activity pattern)
SEGMENTS = [
    ("food", "Restaurants, cafes, bars and food shops",
     r"RETAIL FOOD|WHOLESALE FOOD|FOOD ESTABLISHMENT|SHARED KITCHEN|CONSUMPTION ON PREMISES|TAVERN|PACKAGE GOODS|LIQUOR|CATERER|"
     r"RESTAURANT|BAKERY|COFFEE|CAFE|GROCERY|FOOD|BEVERAGE"),
    ("beauty", "Salons, barbers, nails, spas and fitness",
     r"BARBER|HAIR|NAIL|BEAUTY|COSMETOLOG|SALON|ESTHETIC|SPA\b|MASSAGE|TANNING|BODY ART|TATTOO|LASH|BROW|GYM|FITNESS|HEALTH CLUB|YOGA"),
    ("auto", "Auto repair, tire and car wash shops",
     r"MOTOR VEHICLE|\bAUTO\b|AUTO ?BODY|\bTIRES?\b|CAR WASH|AUTOMOTIVE|VEHICLE REPAIR|BODY SHOP|FILLING STATION|COMMERCIAL GARAGE"),
    ("care", "Day care and children's services",
     r"CHILDREN'?S SERVICES|DAY ?CARE|CHILD CARE|EARLY LEARNING|PRESCHOOL"),
    ("venue", "Venues, entertainment and lodging",
     r"PUBLIC PLACE OF AMUSEMENT|AMUSEMENT|ENTERTAINMENT|HOTEL|MOTEL|HOSTEL|BANQUET|EVENT SPACE|THEATER|THEATRE"),
    ("retail", "Shops, offices and other services", r"."),
]
# A shown name could be a person's when it has two to four plain words and none of them is a business word.
BUSINESS_WORDS = re.compile(
    r"\b(?:LLC|L\.L\.C|INC|CORP|CORPORATION|CO|COMPANY|LTD|LP|LLP|PLLC|PC|GROUP|HOLDINGS|ENTERPRISES?|SERVICES?|SOLUTIONS|"
    r"STORE|SHOP|SHOPPE|MARKET|MART|FOODS?|GRILL|KITCHEN|CAFE|COFFEE|TEA|BAKERY|PIZZA|PIZZERIA|TAQUERIA|TACOS?|RESTAURANT|BAR|"
    r"LOUNGE|TAVERN|PUB|BBQ|SUSHI|DELI|LIQUORS?|WINES?|BEER|BREW\w*|SALON|SPA|NAILS?|BARBER\w*|BEAUTY|LASH\w*|BROWS?|STUDIO|FITNESS|"
    r"GYM|YOGA|AUTO|AUTOMOTIVE|TIRES?|REPAIR|MOTORS?|CAR|WASH|ACADEMY|LEARNING|CENTER|CENTRE|DAYCARE|CARE|KIDS|CLINIC|HEALTH|"
    r"PHARMACY|DENTAL|BOUTIQUE|APPAREL|CLOTHING|FASHION|JEWEL\w*|GALLERY|DESIGN|SUPPLY|SUPPLIES|WIRELESS|MOBILE|PHONES?|CELLULAR|"
    r"TECH\w*|CLEANERS?|CLEANING|LAUNDRY|LAUNDROMAT|TAILOR\w*|FLORIST|FLOWERS?|PET|PETS|GROOMING|HOTEL|INN|EVENTS?|HALL|"
    r"THEATER|THEATRE|CLUB|PARTNERS|ASSOCIATES|INTERNATIONAL|EXPRESS|PLUS|HOUSE|HOME|WORLD|CHICAGO|CITY|NORTH|SOUTH|EAST|WEST|"
    r"FURNITURE|HARDWARE|BOOKS?|MUSIC|TOBACCO|SMOKE|VAPE|CBD|CANDY|SWEETS|DESSERTS?|ICE|CREAM|JUICE|SMOOTHIE|WINGS?|BURGERS?|"
    r"CHICKEN|FISH|SEAFOOD|MEATS?|PRODUCE|CATERING|DISTRIBUT\w*|WHOLESALE|IMPORTS?|EXPORTS?|TRADING|LOGISTICS|MANAGEMENT|"
    r"REALTY|PROPERTIES|INSURANCE|TAX|FINANCIAL|CONSULTING|MEDIA|PRINT\w*|SIGNS?|PHOTO\w*|ART|ARTS|CRAFTS?|GAMES?|TOYS?)\b", re.I)
PLAIN_WORD = re.compile(r"^[A-Z][A-Z'\-]*\.?$")
HOME_ADDRESS = re.compile(r"\b(?:APT|APARTMENT|UNIT\s+\d+[A-Z]?\s*$|#\s*\d+[A-Z]?\s*$|\d+(?:ST|ND|RD|TH)\s+FL(?:OOR)?\s+APT)\b", re.I)


def could_be_person(name):
    """True when a shown business name could be a person's name: two to four plain words, no digit, no business word."""
    n = re.sub(r"\s+", " ", (name or "").upper().strip())
    if not n or re.search(r"\d|&|\bAND\b|'S\b", n) or BUSINESS_WORDS.search(n):
        return False
    words = [w for w in n.replace(",", " ").split(" ") if w]
    return 2 <= len(words) <= 4 and all(PLAIN_WORD.match(w) for w in words)


def name_case(name):
    """dba_case, except a leading "La" or "Las" reads as the Spanish word ("La Casa de las Flores"), not Los Angeles."""
    if re.match(r"\s*LA FITNESS\b", (name or "").upper()):   # the gym brand keeps its initials
        return dba_case(name)
    s = re.sub(r"^(LA|LAS|LOS) (?=[A-Z][a-z])", lambda m: m.group(1).capitalize() + " ", dba_case(name))
    return re.sub(r"(?<=\w )(Las|Los)(?= \w)", lambda m: m.group(1).lower(), s)


def segment(desc, activity):
    text = f"{desc} | {activity}".upper()
    for key, _, pat in SEGMENTS:
        if re.search(pat, text):
            return key
    return "retail"


def keep(r, since, today):
    """(record or None, reason left out)."""
    if (r.get("application_type") or "").upper() != "ISSUE":
        return None, "not a new license (renewal or change)"
    issued = (r.get("date_issued") or "")[:10]
    if not issued or issued < since or issued > today:
        return None, "issued outside the window"
    if (r.get("license_status") or "").upper() != "AAI":   # AAI: issued; AAC cancelled, REV revoked, INQ under inquiry
        return None, "license not active (cancelled or revoked)"
    desc = (r.get("license_description") or "").strip()
    if SKIP_LICENSES.search(desc):
        return None, "license held by a person or for an event or season"
    if (r.get("city") or "CHICAGO").upper().strip() != "CHICAGO":
        return None, "site outside Chicago"
    addr = (r.get("address") or "").strip()
    if not addr:
        return None, "no site address"
    if HOME_ADDRESS.search(addr):
        return None, "home or apartment address"
    shown = (r.get("doing_business_as_name") or "").strip() or (r.get("legal_name") or "").strip()
    if could_be_person(shown) or could_be_person(r.get("legal_name") if not r.get("doing_business_as_name") else ""):
        return None, "name could be a person's"
    return {"license": str(r.get("license_number") or r.get("license_id") or "").split(".")[0],
            "business": name_case(shown), "address": street(addr), "zip": (r.get("zip_code") or "")[:5],
            "licenseType": desc, "activity": re.sub(r"\s+", " ", (r.get("business_activity") or "").strip())[:160],
            "issued": issued, "segment": segment(desc, r.get("business_activity") or ""),
            "lat": r.get("latitude"), "lon": r.get("longitude"), "communityArea": ""}, ""


def build(rows, areas, today, days=WINDOW_DAYS):
    since = (today - dt.timedelta(days=days)).isoformat()
    recs, reasons, seen = [], collections.Counter(), set()
    for r in rows:
        rec, why = keep(r, since, today.isoformat())
        if not rec:
            reasons[why] += 1
            continue
        k = (rec["business"].upper(), rec["address"].upper())     # one row per business site (a site often gets 2 licenses)
        if k in seen:
            reasons["second license at the same site (listed once)"] += 1
            continue
        seen.add(k)
        rec["communityArea"] = area_of(rec.pop("lat"), rec.pop("lon"), areas) or (r.get("community_area_name") or "").title()
        recs.append(rec)
    recs.sort(key=lambda x: (x["issued"], x["business"]), reverse=True)
    return recs, reasons


def pull(since):
    rows, offset = [], 0
    while True:
        page = get(f"{PORTAL}/resource/{DATASET}.json",
                   {"$where": f"application_type='ISSUE' AND date_issued >= '{since}'", "$order": "date_issued DESC, id",
                    "$limit": 5000, "$offset": offset})
        rows += page
        if len(page) < 5000:
            return rows
        offset += 5000


def probe():
    meta = get(f"{PORTAL}/api/views/{DATASET}.json")
    since = (dt.date.today() - dt.timedelta(days=42)).isoformat()
    rows = pull(since)
    out = {"ranAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "since": since,
           "columns": [c.get("fieldName") for c in meta.get("columns", [])], "rows": len(rows),
           "byLicense": collections.Counter(r.get("license_description") or "" for r in rows).most_common(60),
           "byActivity": collections.Counter((r.get("business_activity") or "")[:80] for r in rows).most_common(60),
           "byStatus": dict(collections.Counter(r.get("license_status") or "" for r in rows))}
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, "probe.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("rows", "byStatus")}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", default="", help="members' full list (runner temp only; never committed)")
    ap.add_argument("--top", type=int, default=10)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    today = now.date()
    meta = get(f"{PORTAL}/api/views/{DATASET}.json")
    cols = [c.get("fieldName") for c in meta.get("columns", [])]
    need = {"legal_name", "doing_business_as_name", "address", "license_description", "business_activity", "application_type",
            "date_issued", "license_status", "license_number"}
    if need - set(cols):
        raise SystemExit(f"dataset columns changed, missing {sorted(need - set(cols))}")
    upd = meta.get("rowsUpdatedAt")
    upd_iso = dt.datetime.fromtimestamp(upd, dt.timezone.utc).isoformat(timespec="seconds") if upd else ""
    rows = pull((today - dt.timedelta(days=WINDOW_DAYS + 7)).isoformat())
    areas = load_areas()
    recs, reasons = build(rows, areas, today)
    week_from = (today - dt.timedelta(days=7)).isoformat()
    week = [r for r in recs if r["issued"] >= week_from]
    labels = {k: lab for k, lab, _ in SEGMENTS}
    public = lambda r: {k: r[k] for k in ("business", "address", "communityArea", "licenseType", "activity", "issued")}
    source = {"name": "City of Chicago Data Portal, Business Licenses", "url": DATASET_PAGE, "rowsUpdatedAt": upd_iso,
              "fetchedAt": now.isoformat(timespec="seconds"), "terms": TERMS,
              "modified": ("Filtered by ProofNotFluff: new business licenses (application type Issue) issued in the last 30 days at a "
                           "Chicago business site, one row per business and address. Left out: licenses held by a person or for an "
                           "event or season (peddlers, special events, pop-ups, tow trucks, home-sharing), home or apartment "
                           "addresses, and any business whose name could be a person's name. Business-level fields only.")}
    sample = {"source": source,
              "window": {"from": week_from, "to": today.isoformat(), "listFrom": (today - dt.timedelta(days=WINDOW_DAYS)).isoformat()},
              "counts": {"fetched": len(rows), "kept30": len(recs), "keptWeek": len(week),
                         "segmentsWeek": {k: sum(r["segment"] == k for r in week) for k in labels},
                         "segments30": {k: sum(r["segment"] == k for r in recs) for k in labels},
                         "excluded": dict(reasons),
                         "areasWeek": collections.Counter(r["communityArea"] for r in week if r["communityArea"]).most_common(10)},
              "segmentNames": labels,
              "segments": {k: [public(r) for r in week if r["segment"] == k][: a.top] for k in labels}}
    profile = {"fetchedAt": source["fetchedAt"], "rowsUpdatedAt": upd_iso, "columns": cols,
               "byLicense": collections.Counter(r.get("license_description") or "" for r in rows).most_common(60),
               "keptByLicense": collections.Counter(r["licenseType"] for r in recs).most_common(40), "areasLoaded": len(areas)}
    json.dump(sample, open(os.path.join(OUT, "sample.json"), "w"), indent=1)
    json.dump(profile, open(os.path.join(OUT, "profile.json"), "w"), indent=1)
    try:
        open(os.path.join(OUT, "source-terms.txt"), "w").write(terms_text())
    except SystemExit as e:
        open(os.path.join(OUT, "source-terms.txt"), "w").write(f"Could not fetch the terms page: {e}\n")
    if a.full:
        json.dump({"source": source, "window": sample["window"], "counts": sample["counts"], "records": recs},
                  open(a.full, "w"), indent=1)
    print(json.dumps({"fetched": len(rows), "kept30": len(recs), "keptWeek": len(week), "excluded": dict(reasons)}))


# ---------------------------------------------------------------- planted cases (invented businesses, real City field names)
def selftest():
    for name, want in [("JOHN SMITH", True), ("MARIA G LOPEZ", True), ("O'BRIEN KELLY", True), ("ANNA-MARIE DE LA CRUZ", True),
                       ("JOHN SMITH LLC", False), ("MARIA'S TAQUERIA", False), ("SMITH & SONS", False), ("KFC", False),
                       ("LUNA NAIL SPA", False), ("GOLDEN DRAGON", True), ("ACME 24 HOUR FITNESS", False), ("", False)]:
        assert could_be_person(name) == want, (name, could_be_person(name), want)
    for raw, want in [("LA CASA DE LAS FLORES", "La Casa de las Flores"), ("LA CALACA CANTINA", "La Calaca Cantina"),
                      ("LA FITNESS", "LA Fitness"), ("YATES LIQUOR", "Yates Liquor")]:
        assert name_case(raw) == want, (raw, name_case(raw))
    for desc, act, want in [("Regulated Business License", "Computer Consulting Services / Computer Automated Design", "retail"),
                            ("Motor Vehicle Services License", "Motor Vehicle Repair - Engine and Transmission Work", "auto"),
                            ("Limited Business License", "Hair Services", "beauty"), ("Filling Station", "", "auto"),
                            ("Package Goods", "Retail Sales of Packaged Liquor", "food")]:
        assert segment(desc, act) == want, (desc, act, segment(desc, act))
    today = dt.date(2026, 10, 20)
    base = {"application_type": "ISSUE", "license_status": "AAI", "city": "CHICAGO", "zip_code": "60601", "latitude": "41.88",
            "longitude": "-87.65", "date_issued": "2026-10-16T00:00:00.000", "address": "100 W RANDOLPH ST", "business_activity": ""}
    rows = [
        dict(base, license_number="1", doing_business_as_name="LUNA TACOS", legal_name="LUNA TACOS LLC",
             license_description="Retail Food Establishment"),
        dict(base, license_number="2", doing_business_as_name="LUNA TACOS", legal_name="LUNA TACOS LLC",
             license_description="Consumption on Premises - Incidental Activity"),                  # same site: listed once
        dict(base, license_number="3", doing_business_as_name="", legal_name="JOHN Q PUBLIC",
             license_description="Limited Business License", address="200 N STATE ST"),          # person's name: out
        dict(base, license_number="4", doing_business_as_name="FRESH CUTS BARBERSHOP", legal_name="JOHN Q PUBLIC",
             license_description="Limited Business License", business_activity="Barber Shop", address="300 S WABASH AVE"),
        dict(base, license_number="5", doing_business_as_name="QUICK LUBE AUTO", legal_name="QL INC",
             license_description="Motor Vehicle Services License", address="400 W LAKE ST"),
        dict(base, license_number="6", doing_business_as_name="PEDDLER CO", legal_name="PEDDLER CO",
             license_description="Peddler License", address="500 W LAKE ST"),                       # person-held: out
        dict(base, license_number="7", doing_business_as_name="BRIGHT KIDS ACADEMY", legal_name="BK LLC",
             license_description="Children's Services Facility License", address="600 W LAKE ST"),
        dict(base, license_number="8", doing_business_as_name="CRAFT STUDIO", legal_name="CS LLC",
             license_description="Limited Business License", address="700 W LAKE ST APT 2"),        # apartment: out
        dict(base, license_number="9", doing_business_as_name="OLD PLACE", legal_name="OP LLC", application_type="RENEW",
             license_description="Limited Business License", address="800 W LAKE ST"),               # renewal: out
        dict(base, license_number="10", doing_business_as_name="LATE SHOP", legal_name="LS LLC", date_issued="2026-08-01T00:00:00",
             license_description="Limited Business License", address="900 W LAKE ST"),               # outside 30 days: out
        dict(base, license_number="11", doing_business_as_name="SUBURB STORE", legal_name="SS LLC", city="EVANSTON",
             license_description="Limited Business License", address="1000 W LAKE ST"),              # not Chicago: out
        dict(base, license_number="12", doing_business_as_name="GONE BAR", legal_name="GB LLC", license_status="AAC",
             license_description="Tavern", address="1100 W LAKE ST"),                                # cancelled: out
        dict(base, license_number="13", doing_business_as_name="SUMMER FEST FOOD", legal_name="SFF LLC",
             license_description="Special Event Food", address="1200 W LAKE ST"),                     # event: out
        dict(base, license_number="14", doing_business_as_name="MAIN STREET PHONES", legal_name="MSP INC",
             license_description="Limited Business License", business_activity="Retail Sales of Electronics", address="1300 W LAKE ST"),
    ]
    recs, reasons = build(rows, [("Loop", [[[-87.7, 41.8], [-87.6, 41.8], [-87.6, 41.9], [-87.7, 41.9], [-87.7, 41.8]]])], today)
    by = {r["license"]: r for r in recs}
    assert set(by) == {"1", "4", "5", "7", "14"}, sorted(by)
    assert [by[k]["segment"] for k in ("1", "4", "5", "7", "14")] == ["food", "beauty", "auto", "care", "retail"], by
    assert by["1"]["business"] == "Luna Tacos" and by["1"]["communityArea"] == "Loop" and by["1"]["address"] == "100 W Randolph St"
    blob = json.dumps(recs).upper()
    assert "JOHN Q PUBLIC" not in blob and "LEGAL" not in blob, "a legal name leaked into the records"
    want = {"second license at the same site (listed once)": 1, "name could be a person's": 1,
            "license held by a person or for an event or season": 2, "home or apartment address": 1,
            "not a new license (renewal or change)": 1, "issued outside the window": 1, "site outside Chicago": 1,
            "license not active (cancelled or revoked)": 1}
    assert dict(reasons) == want, dict(reasons)
    print(f"licenses selftest ok (12 planted names, {len(rows)} planted licenses)")


if __name__ == "__main__":
    if sys.argv[1:] == ["--probe"]:
        probe()
    elif sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        main()
