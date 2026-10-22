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
FOOD = "4ijn-s7e5"          # Food Inspections: the license inspection Chicago Restaurant Inspection Leads lists
DATASET_PAGE = f"{PORTAL}/Community-Economic-Development/Business-Licenses/{DATASET}"
TERMS = "https://www.chicago.gov/city/en/narr/foia/data_disclaimer.html"
WINDOW_DAYS = 30      # members' list: licenses issued in the last 30 days; the free sample shows the last 7

# Licenses held by a person or for a day or a season, not a business site a vendor can visit (left out).
SKIP_LICENSES = re.compile(r"^(?:PEDDLER|PHARMACEUTICAL REPRESENTATIVE|SPECIAL EVENT|POP-UP|RAFFLE|TOWING|TOW TRUCK|SHARED HOUSING|"
                           r"HOME OCCUPATION|HOME REPAIR|MOBILE FOOD|PUBLIC CHAUFFEUR|VALET|BED-AND-BREAKFAST|VACATION RENTAL|"
                           r"ITINERANT|MASSAGE THERAPIST|BODY ART PRACTITIONER|SCAVENGER|EXPEDITOR|BUSINESS AFFAIRS|"
                           r"RESIDENTIAL REAL ESTATE DEVELOPER)", re.I)
# The same kinds named only in the business activity, and any activity the City marks as home based.
SKIP_ACTIVITY = re.compile(r"STREET PERFORMER|FLEA MARKET|ORGANIZER OF EVENT|VACATION RENTAL|SHARED HOUSING|TOW TRUCK|SCAVENGER VEHICLE|"
                           r"MOBILE FOOD|SPECIAL EVENT|PEDDLER", re.I)
HOME_BASED = re.compile(r"HOME[- ]BASED", re.I)
# Trade segments, first match wins: (key, label, license or activity pattern)
SEGMENTS = [
    ("food", "Restaurants, cafes, bars and food shops",
     r"RETAIL FOOD|WHOLESALE FOOD|FOOD ESTABLISHMENT|SHARED KITCHEN|CONSUMPTION ON PREMISES|TAVERN|PACKAGE GOODS|LIQUOR|CATERER|"
     r"RESTAURANT|BAKERY|COFFEE|CAFE|GROCERY|FOOD|BEVERAGE"),
    ("beauty", "Salons, barbers, nails, spas and fitness",
     r"BARBER|HAIR|NAIL|BEAUTY|COSMETOLOG|SALON|ESTHETIC|SPA\b|MASSAGE|TANNING|BODY ART|TATTOO|LASH|BROW|GYM|FITNESS|HEALTH CLUB|YOGA|"
     r"SKIN ?CARE|WAXING|THREADING|MICROBLAD|ELECTROLYSIS"),
    # "Commercial Garage" is the City's parking garage license, not a repair shop, so it stays with other services (Oct 22).
    ("auto", "Auto repair, tire and car wash shops",
     r"MOTOR VEHICLE|\bAUTO\b|AUTO ?BODY|\bTIRES?\b|CAR WASH|AUTOMOTIVE|VEHICLE REPAIR|BODY SHOP|FILLING STATION"),
    ("care", "Day care and children's services",
     r"CHILDREN'?S SERVICES|DAY ?CARE|CHILD CARE|EARLY LEARNING|PRESCHOOL"),
    ("venue", "Venues, entertainment and lodging",
     r"PUBLIC PLACE OF AMUSEMENT|AMUSEMENT|ENTERTAINMENT|HOTEL|MOTEL|HOSTEL|BANQUET|EVENT SPACE|THEATER|THEATRE"),
    ("retail", "Shops, offices and other services", r"."),
]
# The trades as buyers read them (tab, short label, what kinds of business), in tab order: the workbook, the members' app
# and the free page all use these names (tools/lic_xlsx.py, tools/lic_app.py, tools/lic_site.py).
TRADES = [  # key, tab, short label, what kinds of business
    ("food", "1 Food and drink", "Food and drink", "Restaurants, cafes, bars, caterers, groceries and other food shops"),
    ("retail", "2 Shops and services", "Shops and services", "Shops, offices, studios, manufacturers and other services"),
    ("beauty", "3 Salons, spas, fitness", "Salons, spas, fitness", "Salons, barbers, nails, skin care, spas, gyms and studios"),
    ("venue", "4 Venues and lodging", "Venues and lodging", "Event venues, entertainment, hotels and lodging"),
    ("auto", "5 Auto shops", "Auto shops", "Auto repair, tire shops, car washes and gas stations"),
    ("care", "6 Day care", "Day care", "Day care and children's services"),
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
# A stall or booth at a market ("4100 S ASHLAND AVE OUTSIDE 636" is an outdoor flea market space): a vendor, not a site (Oct 22).
STALL_ADDRESS = re.compile(r"\b(?:OUTSIDE\s+\d+|BOOTH|STALL)\b", re.I)


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
    act = r.get("business_activity") or ""
    if SKIP_ACTIVITY.search(act):
        return None, "license held by a person or for an event or season"
    if HOME_BASED.search(act):
        return None, "home or apartment address"
    if (r.get("city") or "CHICAGO").upper().strip() != "CHICAGO":
        return None, "site outside Chicago"
    addr = (r.get("address") or "").strip()
    if not addr:
        return None, "no site address"
    if HOME_ADDRESS.search(addr):
        return None, "home or apartment address"
    if STALL_ADDRESS.search(addr):
        return None, "license held by a person or for an event or season"
    shown = (r.get("doing_business_as_name") or "").strip() or (r.get("legal_name") or "").strip()
    if could_be_person(shown) or could_be_person(r.get("legal_name") if not r.get("doing_business_as_name") else ""):
        return None, "name could be a person's"
    num = lambda k: str(r.get(k) or "").split(".")[0]
    return {"license": num("license_number") or num("license_id"),
            "business": name_case(shown), "address": street(addr), "zip": (r.get("zip_code") or "")[:5],
            "licenseType": desc, "otherTypes": [], "activity": activity_text(r.get("business_activity")),
            "issued": issued, "segment": segment(desc, r.get("business_activity") or ""),
            "lat": _coord(r.get("latitude")), "lon": _coord(r.get("longitude")), "communityArea": "",
            "_acct": num("account_number"), "_site": num("site_number")}, ""


def activity_text(a, cap=300):
    """The City's business activity, whole activities only: a long list ends at the last full one (never mid-word)."""
    a = re.sub(r"\s+", " ", (a or "").strip())
    if len(a) <= cap:
        return a
    parts, out = a.split(" | "), []
    for x in parts:
        if len(" | ".join(out + [x])) > cap:
            break
        out.append(x)
    return " | ".join(out) if out else a[:cap].rsplit(" ", 1)[0]


def _coord(v):
    try:
        return round(float(v), 6)
    except (TypeError, ValueError):
        return None


# Do-not-list: a business that asks to be left out stays out of the members' list and the free sample on every later build.
# permits/licenses-chicago/do_not_list.json holds salted SHA-256 keys, never a name, address or license in the clear:
# "L:<license>" and "N:<name>|<address>" (letters and digits only, upper case). Add one with
#   python3 tools/licenses_chicago.py --dnl-add --license 1234567        (the License on the business page or workbook)
#   python3 tools/licenses_chicago.py --dnl-add --name "BUSINESS NAME" --address "123 W MAIN ST"
# The salt is public, so a key can be checked against the City's records; it keeps the list free of names, not secret.
DNL_FILE = os.path.join(OUT, "do_not_list.json")
DNL_SALT = "proofnotfluff-licenses-dnl-v1"
DNL_REASON = "the business asked to be left out"


def dnl_hash(key):
    import hashlib
    return hashlib.sha256((DNL_SALT + "|" + key).encode("utf-8")).hexdigest()


def dnl_key_name(name, address):
    n = lambda t: re.sub(r"[^A-Z0-9]", "", (t or "").upper())
    return "N:" + n(name) + "|" + n(address)


def row_dnl_keys(r):
    keys = set()
    lic = str(r.get("license_number") or "").split(".")[0]
    if lic:
        keys.add("L:" + lic)
    for nm in (r.get("doing_business_as_name"), r.get("legal_name")):
        if (nm or "").strip() and (r.get("address") or "").strip():
            keys.add(dnl_key_name(nm, r.get("address")))
    return {dnl_hash(k) for k in keys}


def dnl_load(path=DNL_FILE):
    """The set of keys. A missing file is an empty list; a broken one stops the build, so a removal is never dropped."""
    if not os.path.exists(path):
        return set()
    d = json.load(open(path, encoding="utf-8"))
    keys = d.get("keys") if isinstance(d, dict) else None
    if not isinstance(d, dict) or d.get("salt") != DNL_SALT or not isinstance(keys, list) or \
            not all(isinstance(k, str) and re.fullmatch(r"[0-9a-f]{64}", k) for k in keys):
        raise SystemExit(f"{path}: must be {{\"salt\": \"{DNL_SALT}\", \"keys\": [64-hex keys]}}")
    return set(keys)


def dnl_add(key, path=DNL_FILE):
    d = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    keys = set(d.get("keys") or [])
    keys.add(dnl_hash(key))
    out = {"about": "Businesses that asked to be left out of Chicago New Business Licenses. Salted SHA-256 keys only; see "
                    "tools/licenses_chicago.py.", "salt": DNL_SALT, "keys": sorted(keys)}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    return len(keys)


def build(rows, areas, today, days=WINDOW_DAYS, dnl=None):
    since = (today - dt.timedelta(days=days)).isoformat()
    dnl = dnl_load() if dnl is None else dnl
    recs, reasons, seen = [], collections.Counter(), {}
    # oldest first, so a site's row carries its first license in the window and later ones show as other licenses (Oct 22)
    for r in sorted(rows, key=lambda x: ((x.get("date_issued") or "")[:10], str(x.get("license_number") or ""))):
        rec, why = keep(r, since, today.isoformat())
        if rec and dnl and row_dnl_keys(r) & dnl:
            rec, why = None, DNL_REASON
        if not rec:
            reasons[why] += 1
            continue
        k = (rec["business"].upper(), rec["address"].upper())     # one row per business site (a site often gets 2 licenses)
        if k in seen:
            reasons["second license at the same site (listed once)"] += 1
            first = seen[k]
            if rec["licenseType"] != first["licenseType"] and rec["licenseType"] not in first["otherTypes"]:
                first["otherTypes"].append(rec["licenseType"])
            first["_lics"].append(rec["license"])
            continue
        seen[k] = rec
        rec["_lics"] = [rec["license"]]
        rec["communityArea"] = area_of(rec["lat"], rec["lon"], areas) or (r.get("community_area_name") or "").title()
        recs.append(rec)
    recs.sort(key=lambda x: (x["issued"], x["business"]), reverse=True)
    return recs, reasons


# ---------------------------------------------------------------- what the City's own records add to each row
# Both run in the runner after build(): one grouped query per 40 accounts or licenses. A failed fetch leaves the field
# blank and says so in counts (the list still ships; the app and workbook show the check as not run).
HISTORY_WORDS = {"first": "First license on the City's record for this business",
                 "site": "A new site for a business already licensed elsewhere in Chicago",
                 "added": "A new license at a site where this business already held one"}


def add_history(recs, fetch, start):
    """history: "first" (no Chicago license for this business account before the list window starts, 2002 on: a business that
    licenses in stages, say a food license on Oct 1 and a liquor license on Oct 19, is still new), "site" (the account held a
    license at another site before the window: a new location or a move), "added" (the account held a license at this site
    before the window: a new license type there). since: the year of the earliest such license. start: the window's first day.
    fetch(accounts) returns City rows with account_number, site_number and date_issued for those accounts."""
    accts = sorted({r["_acct"] for r in recs if r.get("_acct")})
    hist = collections.defaultdict(list)
    for i in range(0, len(accts), 40):
        for x in fetch(accts[i:i + 40]):
            a, d = str(x.get("account_number") or "").split(".")[0], (x.get("date_issued") or "")[:10]
            if a and d:
                hist[a].append((d, str(x.get("site_number") or "").split(".")[0]))
    for r in recs:
        prior = [(d, s) for d, s in hist.get(r.get("_acct") or "", []) if d < start]
        here = [d for d, s in prior if s == r.get("_site")]
        if not r.get("_acct"):
            r["history"], r["since"] = "", ""
        elif here:
            r["history"], r["since"] = "added", min(here)[:4]
        elif prior:
            r["history"], r["since"] = "site", min(d for d, _ in prior)[:4]
        else:
            r["history"], r["since"] = "first", ""
    return recs


def add_food_inspections(recs, fetch):
    """foodInsp: the newest City food license inspection on file for the row's license number (the City's Food Inspections
    dataset, 4ijn-s7e5, files it under the business license number), in the 120 days before the license was issued. That
    inspection is what Chicago Restaurant Inspection Leads lists as "Opening soon". fetch(licenses) returns rows with license_
    and inspection_date."""
    lic = sorted({n for r in recs for n in (r.get("_lics") or [r["license"]]) if n})
    seen = collections.defaultdict(list)
    for i in range(0, len(lic), 40):
        for x in fetch(lic[i:i + 40]):
            n, d = str(x.get("license_") or "").split(".")[0], (x.get("inspection_date") or "")[:10]
            if n and d:
                seen[n].append(d)
    for r in recs:
        start = (dt.date.fromisoformat(r["issued"]) - dt.timedelta(days=120)).isoformat()
        ds = [d for n in (r.get("_lics") or [r["license"]]) for d in seen.get(n, []) if start <= d <= r["issued"]]
        r["foodInsp"] = max(ds) if ds else ""
    return recs


def strip_internal(recs):
    for r in recs:
        r.pop("_acct", None); r.pop("_site", None); r.pop("_lics", None)
    return recs


def fetch_history(accts):
    return get(f"{PORTAL}/resource/{DATASET}.json",
               {"$select": "account_number,site_number,date_issued", "$where": f"account_number in ({','.join(accts)})", "$limit": 50000})


def fetch_food(lics):
    return get(f"{PORTAL}/resource/{FOOD}.json",
               {"$select": "license_,inspection_date", "$where": f"license_ in ({','.join(lics)}) AND upper(inspection_type) like 'LICENSE%'",
                "$limit": 50000})


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
    checks = {}
    for name, fn in (("history", lambda: add_history(recs, fetch_history, (today - dt.timedelta(days=WINDOW_DAYS)).isoformat())), ("foodInspections", lambda: add_food_inspections(recs, fetch_food))):
        try:
            fn(); checks[name] = True
        except SystemExit as e:                     # the list still ships; the app and workbook say the check did not run
            print(f"{name} check did not run: {e}")
            checks[name] = False
            for r in recs:
                r.setdefault("history", ""); r.setdefault("since", ""); r.setdefault("foodInsp", "")
    strip_internal(recs)
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
                         "areasWeek": collections.Counter(r["communityArea"] for r in week if r["communityArea"]).most_common(10),
                         "checks": checks, "history30": dict(collections.Counter(r["history"] or "unknown" for r in recs)),
                         "foodInsp30": sum(bool(r["foodInsp"]) for r in recs)},
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
    print(json.dumps({"fetched": len(rows), "kept30": len(recs), "keptWeek": len(week), "excluded": dict(reasons),
                      "checks": checks, "history30": sample["counts"]["history30"], "foodInsp30": sample["counts"]["foodInsp30"]}))


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
                            ("Package Goods", "Retail Sales of Packaged Liquor", "food"),
                            ("Limited Business License", "Skincare Services | Provide Waxing Services", "beauty"),
                            ("Commercial Garage", "Provide 4 or More Parking Spaces For a Fee", "retail")]:
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
        dict(base, license_number="15", doing_business_as_name="BRIGHT IDEAS CONSULTING", legal_name="BI LLC",
             license_description="Regulated Business License", business_activity="Professional Consulting (Home Based Business)",
             address="1500 W LAKE ST 2 202"),                                                       # home based: out
        dict(base, license_number="16", doing_business_as_name="SUNNY FLEA GOODS", legal_name="SFG LLC",
             license_description="Limited Business License",
             business_activity="Sale of General Merchandise at Flea Market 181-365 Consecutive Days", address="1600 W LAKE ST"),
        dict(base, license_number="14", doing_business_as_name="MAIN STREET PHONES", legal_name="MSP INC", account_number="501",
             site_number="2", license_description="Limited Business License", business_activity="Retail Sales of Electronics", address="1300 W LAKE ST"),
        dict(base, license_number="17", doing_business_as_name="SWAP TOOLS", legal_name="ST LLC",
             license_description="Limited Business License", business_activity="Retail Sales of General Merchandise",
             address="4100 S ASHLAND AVE OUTSIDE 636"),                                              # market stall: out
    ]
    for r in rows:
        r.setdefault("account_number", str(100 + int(r["license_number"])) + ".0"); r.setdefault("site_number", "1")
    loop = [("Loop", [[[-87.7, 41.8], [-87.6, 41.8], [-87.6, 41.9], [-87.7, 41.9], [-87.7, 41.8]]])]
    # the do-not-list: a planted removal by license, and one by name and address (case and punctuation do not matter)
    import tempfile
    tf = os.path.join(tempfile.mkdtemp(), "dnl.json")
    dnl_add("L:7", tf)
    dnl_add(dnl_key_name("Main Street Phones", "1300 W. Lake St."), tf)
    gone, why = build(rows, loop, today, dnl=dnl_load(tf))
    assert {r["license"] for r in gone} == {"1", "4", "5"} and why[DNL_REASON] == 2, (sorted(r["license"] for r in gone), dict(why))
    try:
        json.dump({"salt": "wrong", "keys": []}, open(tf, "w")); dnl_load(tf)
        raise AssertionError("a broken do-not-list must stop the build")
    except SystemExit:
        pass
    recs, reasons = build(rows, loop, today, dnl=set())
    by = {r["license"]: r for r in recs}
    assert set(by) == {"1", "4", "5", "7", "14"}, sorted(by)
    assert [by[k]["segment"] for k in ("1", "4", "5", "7", "14")] == ["food", "beauty", "auto", "care", "retail"], by
    assert by["1"]["business"] == "Luna Tacos" and by["1"]["communityArea"] == "Loop" and by["1"]["address"] == "100 W Randolph St"
    assert by["1"]["otherTypes"] == ["Consumption on Premises - Incidental Activity"] and by["1"]["lat"] == 41.88, by["1"]
    # the City's own history: account 101 (Luna Tacos) is new; 104 (the barbershop) held a license at this site since 2019;
    # 501 (the phone shop) held one at another site since 2015; 107's only earlier row is the same day (not earlier)
    hist = {"101": [], "104": [("2019-03-02", "1")], "105": [("2026-10-01", "1")], "107": [("2026-10-16", "1")],
            "501": [("2015-06-01", "1"), ("2020-01-01", "1")]}   # 105: a license earlier in the window is still a new business
    calls = []
    def fake_hist(accts):
        calls.append(len(accts))
        return [{"account_number": a + ".0", "site_number": s, "date_issued": d + "T00:00:00.000"} for a in accts for d, s in hist.get(a, [])]
    add_history(recs, fake_hist, "2026-09-20")
    assert [(by[k]["history"], by[k]["since"]) for k in ("1", "4", "5", "7", "14")] == [
        ("first", ""), ("added", "2019"), ("first", ""), ("first", ""), ("site", "2015")], [(by[k]["history"], by[k]["since"]) for k in by]
    assert calls == [5], calls
    food = {"2": ["2026-10-02", "2026-10-09", "2025-01-01"], "5": ["2026-10-17"]}   # filed under the site's second license
    add_food_inspections(recs, lambda lics: [{"license_": n + ".0", "inspection_date": d + "T00:00:00.000"} for n in lics for d in food.get(n, [])])
    assert by["1"]["foodInsp"] == "2026-10-09" and by["5"]["foodInsp"] == "" and by["4"]["foodInsp"] == "", "newest, 120 days before, never after the issue date"
    strip_internal(recs)
    assert not any(k.startswith("_") for r in recs for k in r), "account and site numbers never leave the runner"
    blob = json.dumps(recs).upper()
    assert "JOHN Q PUBLIC" not in blob and "LEGAL" not in blob, "a legal name leaked into the records"
    want = {"second license at the same site (listed once)": 1, "name could be a person's": 1,
            "license held by a person or for an event or season": 4, "home or apartment address": 2,
            "not a new license (renewal or change)": 1, "issued outside the window": 1, "site outside Chicago": 1,
            "license not active (cancelled or revoked)": 1}
    assert dict(reasons) == want, dict(reasons)
    long = " | ".join(["Retail Sales of General Merchandise and Non-Perishable Food"] * 8)
    assert activity_text(long) == " | ".join(["Retail Sales of General Merchandise and Non-Perishable Food"] * 4), activity_text(long)
    assert activity_text("Hair Services") == "Hair Services"
    print(f"licenses selftest ok (12 planted names, 7 planted trades, {len(rows)} planted licenses, 2 planted removals, 5 planted histories, 2 planted food inspections)")


def dnl_cli(args):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dnl-add", action="store_true")
    ap.add_argument("--license", default="")
    ap.add_argument("--name", default="")
    ap.add_argument("--address", default="")
    a = ap.parse_args(args)
    if a.license.strip():
        n = dnl_add("L:" + re.sub(r"\D", "", a.license))
    elif a.name.strip() and a.address.strip():
        n = dnl_add(dnl_key_name(a.name, a.address))
    else:
        raise SystemExit("give --license N, or --name and --address")
    print(f"do-not-list: {n} key(s); commit {os.path.relpath(DNL_FILE, ROOT)}")


if __name__ == "__main__":
    if sys.argv[1:] == ["--probe"]:
        probe()
    elif sys.argv[1:] == ["--selftest"]:
        selftest()
    elif sys.argv[1:2] == ["--dnl-add"]:
        dnl_cli(sys.argv[1:])
    else:
        main()
