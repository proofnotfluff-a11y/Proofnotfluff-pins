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
from zoneinfo import ZoneInfo

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
                           r"RESIDENTIAL REAL ESTATE DEVELOPER|SHARED KITCHEN USER|PRIVATE BOOTING)", re.I)   # a shared kitchen user cooks in someone else's kitchen (holdout 1, Oct 22)
# The same kinds named only in the business activity, and any activity the City marks as home based.
SKIP_ACTIVITY = re.compile(r"STREET PERFORMER|FLEA MARKET|ORGANIZER OF EVENT|VACATION RENTAL|SHARED HOUSING|TOW TRUCK|SCAVENGER VEHICLE|"
                           r"MOBILE FOOD|SPECIAL EVENT|PEDDLER|BED[- ]AND[- ]BREAKFAST|HOME REPAIR|SHARED KITCHEN USER", re.I)
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
     r"MOTOR VEHICLE|\bAUTO\b|AUTO ?BODY|\bTIRES?\b|CAR WASH|AUTOMOTIVE|VEHICLE REPAIR|VEHICLE PARTS|\bRIMS\b|BODY SHOP|FILLING STATION"),
    ("care", "Day care and children's services",
     r"CHILDREN'?S SERVICES|DAY ?CARE|CHILD CARE|EARLY LEARNING|PRESCHOOL"),
    ("venue", "Venues, entertainment and lodging",
     r"PUBLIC PLACE OF AMUSEMENT|AMUSEMENT|ENTERTAINMENT|HOTEL|MOTEL|HOSTEL|BANQUET|EVENT SPACE|THEATER|THEATRE"),
    ("retail", "Shops, offices and other services", r"."),
]
# The trades as buyers read them (tab, short label, what kinds of business), in tab order: the workbook, the members' app
# and the free page all use these names (tools/lic_xlsx.py, tools/lic_app.py, tools/lic_site.py).
TRADES = [  # key, tab, short label, what kinds of business
    ("food", "1 Food and drink", "Food and drink", "Restaurants, cafes, bars, caterers and food stores, by their City food or liquor license or a prepared or perishable food activity"),
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
    r"REALTY|PROPERTIES|INSURANCE|TAX|FINANCIAL|CONSULTING|MEDIA|PRINT\w*|SIGNS?|PHOTO\w*|ART|ARTS|CRAFTS?|GAMES?|TOYS?|"
    # more plain business words, none of them a common first name or surname (holdout 2, Oct 22)
    r"PARKING|GARAGE|PAWN|GROCERY|GROCERIES|BAKESHOP|BAKE|NOODLES?|RAMEN|PHO|SUPPLEMENTS?|NUTRITION|LIGHTING|LED|EMPORIUM|"
    r"FACTORY|CUISINE|SAUCE|CERVECERIA|NEVERIA|PALETERIA|PANADERIA|CARNICERIA|TORTILLERIA|BOTANICA|DELICIAS|STATION|FUEL|GAS|"
    r"CORNER|EGGS?|DOGS?|PUPS?|PAWS|BABY|BABIES|SCHOOL|MONTESSORI|NURSERY|PRESCHOOL|TATTOO|PIERCING|CANNABIS|DISPENSARY|"
    r"BUFFET|DINER|BISTRO|CANTINA|EATERY|TAPROOM|WINERY|DISTILLERY|BREWERY|CREAMERY|DONUTS?|BAGELS?|CREPES?|BOBA|SPIRITS|"
    r"BOUTIQUE|TRAVEL|TOURS?|RENTALS?|STORAGE|MOVING|TRANSPORT|TRUCKING|CONSTRUCTION|ROOFING|PLUMBING|ELECTRIC|HVAC|DENTISTRY|"
    r"OPTICAL|VISION|THERAPY|WELLNESS|MASSAGE|AESTHETICS?|SKIN|MEDSPA|ACUPUNCTURE|CHIROPRACTIC|PHYSICAL|VETERINARY|ANIMAL|"
    # holdout 2, round 2
    r"GRAPHICS?|DEVELOPMENT|DEVELOPERS?|VENDING|SHIPPING|LOFTS?|BALLET|DANCE|EXPERTS?|WARDROBE|CLIPS|CUTZ|CUTS|HELADOS|"
    r"ARTESANALES|RAMYUN|CAPITAL|SCRAP|METALS?|RECYCLING|SECURITY|STAFFING|CONSULTANTS|ADVISORS|PAINTING|FLOORING|LANDSCAPING|"
    r"BUILDERS|MOVERS|DELIVERY|COURIER|CLOSET|THRIFT|RESALE|VINTAGE|OUTLET|DEPOT|WAREHOUSE|LAB|LABS|ROASTERS?|CREPERIA|BIRRIERIA|"
    r"MARISCOS|POLLERIA|TAQUERIAS|RESTAURANTE|PUPUSERIA|DULCERIA|DULCELANDIA|ABARROTES|SUPERMERCADO|LAVANDERIA|ESTETICA|SALONE|"
    r"HAIR|BRAIDING|BRAIDS|STUDIOS|ENTERTAINMENT|ENTERTAINING)\b", re.I)
PLAIN_WORD = re.compile(r"^[A-Z][A-Z'\-]*\.?$")
# "Unit 1" is not an apartment by itself: a shop unit stays like "Unit C-2" (holdout 2, round 3); "Apt", "Apartment" and a
# trailing "#12" are.
HOME_ADDRESS = re.compile(r"\b(?:APT|APARTMENT|#\s*\d+[A-Z]?\s*$|\d+(?:ST|ND|RD|TH)\s+FL(?:OOR)?\s+APT)\b", re.I)
# A stall or booth at a market ("4100 S ASHLAND AVE OUTSIDE 636" is an outdoor flea market space): a vendor, not a site (Oct 22).
STALL_ADDRESS = re.compile(r"\b(?:OUTSIDE\s+\d+|BOOTH|STALL)\b", re.I)
# A private mailbox ("PMB 353", "#453522"): a mail drop, not a site a vendor can visit (holdout 1, Oct 22).
MAILBOX_ADDRESS = re.compile(r"\bPMB\b|#\s*\d{5,}\b", re.I)
MAILBOX_REASON = "virtual office or mailbox address"
PERSON_EVENT_REASON = "license for one person's own work, work away from a fixed site, or an event or season"
RESIDENTIAL_REASON = "home or apartment address"
STREET_END = re.compile(r"^(?:ST|AVE|AV|BLVD|DR|RD|PL|PKWY|CT|HWY|TER|WAY|LN|SQ|PLZ|CIR|ROW|BROADWAY|WACKER)$", re.I)
GROUND_UNIT = re.compile(r"^(?:(?:#\s*)?1(?:ST|F|R|FL|FLR)?(?:\s.*)?|1ST FL(?:OOR)?.*|GROUND.*|GRND.*|BSMT.*|BASEMENT.*|STORE.*|REAR.*|FRONT.*|"
                         r"(?:STE|SUITE|SUIT)\b.*|RETAIL\b.*|COMMERCIAL\b.*|[A-Z])?$", re.I)   # "1 NW", "B", "Store 2" stay (holdout 2, round 2)


def split_address(addr):
    """(building, unit): "3950 N LAKE SHORE DR 20TH 2021" -> ("3950 N LAKE SHORE DR", "20TH 2021"). The building is the house
    number (or range) and the street through its suffix; no suffix found means no unit."""
    words = re.sub(r"\s+", " ", (addr or "").upper().strip()).split(" ")
    for i, w in enumerate(words[2:], 2):
        if STREET_END.match(w.strip(",.")):
            return " ".join(words[:i + 1]).strip(" ,"), " ".join(words[i + 1:]).strip(" ,")
    return " ".join(words), ""


def building_key(addr):
    b, _ = split_address(addr)
    return re.sub(r"[^A-Z0-9]", "", re.sub(r"^(\d+)-\d+", r"\1", b))


LEGAL_END = re.compile(r"[\s,]+(?:L\.?\s?L\.?\s?C\.?|INC\.?|INCORPORATED|CORP\.?|CORPORATION|CO\.?|LTD\.?|L\.?P\.?|L\.?L\.?P\.?|P\.?L\.?L\.?C\.?|P\.?C\.?)\s*$", re.I)


def _first_names():
    """Common first names: the restaurant product's list (tools/rest_leads.py) plus names it lacked that holdout 2 found
    (Oct 22). Read lazily so the free page build (make_site.py) never loads it."""
    try:
        from rest_leads import FIRST
    except Exception:                     # the rule still holds without the list; it only catches fewer names
        FIRST = set()
    return set(FIRST) | set("""ARIANNA ADELE NOEL ZOE ARIANA ADRIANA ALEXA ALEXIS ALINA AMIRA ANAYA ANGELINA ARIA ARIEL AUBREY AVA BELLA BRIANNA
        CAMILA CHLOE DANIELA ELENA ELLA EMMA ESTRELLA EVA GABRIELA GIANNA HAILEY ISABELLA JADE JASMINE KAYLA KIARA LAYLA LEAH LILY LUNA
        MADISON MAYA MIA MILA NADIA NAOMI NATALIA NOVA OLIVIA PAOLA PENELOPE RILEY SAMANTHA SARAI SOFIA SOPHIA STELLA VALENTINA VIOLET
        XIMENA ZARA AIDEN ALEJANDRO ANDRES ANGEL ANTONIO ASHER BENJAMIN BRANDON CALEB CAMERON CARLOS CHRISTIAN DAMIAN DIEGO DOMINIC
        ELIJAH EMILIANO ETHAN EZRA GAEL GAVIN HUDSON IAN ISAAC IVAN JADEN JAVIER JAYDEN JOSUE JULIAN KEVIN LEO LIAM LOGAN LUCAS MATEO
        MAXWELL MILES NICOLAS NOAH OLIVER OMAR OSCAR OWEN RAFAEL RYAN SANTIAGO SEBASTIAN THEO TRISTAN WYATT""".split())


_FIRST = None


def holds_full_name(name):
    """True when a name starts with a common first name and one more plain word that is not a business word ("ARIANNA BARONE
    BEAUTY"), so it prints a person's full name even with a business word after it (holdout 2, round 2). A possessive
    ("Maria's Kitchen") or a single first name ("Queen Nails by Zoe") stays."""
    global _FIRST
    if _FIRST is None:
        _FIRST = _first_names()
    n = re.sub(r"\s+", " ", (name or "").upper().strip())
    while LEGAL_END.search(n):
        n = LEGAL_END.sub("", n).strip()
    w = [x.strip(".,") for x in n.split(" ") if x.strip(".,")]
    return (len(w) >= 2 and w[0] in _FIRST and PLAIN_WORD.match(w[1]) is not None and not w[1].endswith("'S")
            and not BUSINESS_WORDS.search(w[1]) and w[1] not in ("AND", "&", "BY", "DE", "THE"))


def could_be_person(name):
    """True when a shown business name could be a person's name: two to four plain words, no digit, no business word, with or
    without LLC, Inc or Corp at the end ("NOEL MERCADO L.L.C." reads as a person's name; holdout 1, Oct 22)."""
    n = re.sub(r"\s+", " ", (name or "").upper().strip())
    while LEGAL_END.search(n):
        n = LEGAL_END.sub("", n).strip()
    if re.match(r"THE\s", n):            # "The Reserve", "The Smart Bar": a person's name never starts with "The"
        return False
    if not n or re.search(r"\d|&|\bAND\b|'S\b", n) or BUSINESS_WORDS.search(n):
        return False
    words = [w for w in n.replace(",", " ").split(" ") if w]
    return 2 <= len(words) <= 4 and all(PLAIN_WORD.match(w) for w in words)


def name_case(name):
    """dba_case, except a leading "La" or "Las" reads as the Spanish word ("La Casa de las Flores"), not Los Angeles. A name the City
    already writes in mixed case ("The UPS Store", "ChaTraMue") stays exactly as written (holdout 1, Oct 22)."""
    if re.search(r"[a-z]", name or ""):
        return re.sub(r"\s+", " ", name.strip())
    if re.match(r"\s*LA FITNESS\b", (name or "").upper()):   # the gym brand keeps its initials
        return dba_case(name)
    s = re.sub(r"^(LA|LAS|LOS) (?=[A-Z][a-z])", lambda m: m.group(1).capitalize() + " ", dba_case(name))
    s = re.sub(r"\b(\d+)(ST|ND|RD|TH)\b", lambda m: m.group(1) + m.group(2).lower(), s)            # "87th Quick Stop" (holdout 2, round 5)
    s = re.sub(r"(?<=\w )LA(?= [A-Z][a-z])", "La", s)                                              # "Neveria La Garrafita"
    for ac in re.findall(r"\(([A-Z0-9][A-Z0-9 .&-]{1,10})\)", name or ""):     # "(HAMOC)" stays in capitals (holdout 1, round 2)
        s = re.sub(r"\(" + re.escape(ac) + r"\)", "(" + ac + ")", s, flags=re.I)
    return re.sub(r"(?<=\w )(Las|Los)(?= \w)", lambda m: m.group(1).lower(), s)


FOOD_LICENSE = re.compile(r"RETAIL FOOD|WHOLESALE FOOD|FOOD ESTABLISHMENT|SHARED KITCHEN|CONSUMPTION ON PREMISES|TAVERN|PACKAGE GOODS|LIQUOR|"
                          r"CATERER", re.I)
STOCK_FOOD = re.compile(r"RETAIL SALES OF GENERAL MERCHANDISE AND NON-PERISHABLE FOOD|NON-PERISHABLE FOOD", re.I)


def segment(desc, activity):
    """The trade (holdout 1, Oct 22): a food or liquor license type is food; a Public Place of Amusement license is a venue;
    otherwise the most specific activity decides, in the order beauty, auto, day care, venue, food, and the City's stock
    "Retail Sales of General Merchandise and Non-Perishable Food" activity never makes a row food (a UPS Store, a gym)."""
    d = (desc or "").upper()
    if FOOD_LICENSE.search(d):
        return "food"
    if re.search(r"PUBLIC PLACE OF AMUSEMENT", d):
        return "venue"
    if re.search(r"ANIMAL CARE", d):           # dog day care and grooming are services, not children's day care (holdout 1, round 2)
        return "retail"
    text = f"{d} | {STOCK_FOOD.sub(' ', (activity or '').upper())}"
    pats = dict((k, p) for k, _, p in SEGMENTS)
    for key in ("beauty", "auto", "care", "venue", "food"):
        if re.search(pats[key], text):
            return key
    return "retail"


def chicago_now():
    return dt.datetime.now(ZoneInfo("America/Chicago")).replace(microsecond=0)


def keep(r, since, today):
    """(record or None, reason left out)."""
    if (r.get("application_type") or "").upper() != "ISSUE":
        return None, "not a new license (renewal or change)"
    issued = (r.get("date_issued") or "")[:10]
    if not issued or issued < since or issued > today:
        return None, "issued outside the window"
    approved = (r.get("license_approved_for_issuance") or "")[:10]
    # a re-dated old license: approved long before it was issued ("Domino's" 2971586, approved 2024, issued Oct 2026; holdout 1).
    # A license approved a few weeks or months before payment and issue is still new (McDonald's at O'Hare; holdout 2, round 3).
    if approved and approved < (dt.date.fromisoformat(issued) - dt.timedelta(days=180)).isoformat():
        return None, "not a new license (renewal or change)"
    if (r.get("license_status") or "").upper() != "AAI":   # AAI: issued; AAC cancelled, REV revoked, INQ under inquiry
        return None, "license not active (cancelled or revoked)"
    desc = (r.get("license_description") or "").strip()
    if SKIP_LICENSES.search(desc):
        return None, PERSON_EVENT_REASON
    act = r.get("business_activity") or ""
    if SKIP_ACTIVITY.search(act):
        return None, PERSON_EVENT_REASON
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
        return None, PERSON_EVENT_REASON
    if MAILBOX_ADDRESS.search(addr):
        return None, MAILBOX_REASON
    shown = (r.get("doing_business_as_name") or "").strip() or (r.get("legal_name") or "").strip()
    if could_be_person(shown) or holds_full_name(shown) or could_be_person(r.get("legal_name") if not r.get("doing_business_as_name") else ""):
        return None, "name could be a person's"
    num = lambda k: str(r.get(k) or "").split(".")[0]
    return {"license": num("license_number") or num("license_id"),
            "business": name_case(shown), "address": street(addr), "zip": (r.get("zip_code") or "")[:5],
            "licenseType": desc, "otherTypes": [], "activity": activity_text(r.get("business_activity")),
            "issued": issued, "segment": segment(desc, r.get("business_activity") or ""),
            "lat": _coord(r.get("latitude")), "lon": _coord(r.get("longitude")), "communityArea": "",
            "_acct": num("account_number"), "_site": num("site_number"), "_addr": addr.upper()}, ""


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
    more = len(parts) - len(out)
    return (" | ".join(out) + f" | and {more} more") if out else a[:cap].rsplit(" ", 1)[0]


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


def build(rows, areas, today, days=WINDOW_DAYS, dnl=None, left=None):
    """(records, reasons). left: an optional list that gets [license, reason] for every row left out (runner checks only)."""
    since = (today - dt.timedelta(days=days)).isoformat()
    dnl = dnl_load() if dnl is None else dnl
    recs, reasons, seen = [], collections.Counter(), {}
    lic_of = lambda r: str(r.get("license_number") or "").split(".")[0]
    # oldest first, so a site's row carries its first license in the window and later ones show as other licenses (Oct 22)
    for r in sorted(rows, key=lambda x: ((x.get("date_issued") or "")[:10], str(x.get("license_number") or ""))):
        rec, why = keep(r, since, today.isoformat())
        if rec and dnl and row_dnl_keys(r) & dnl:
            rec, why = None, DNL_REASON
        if not rec:
            reasons[why] += 1
            if left is not None:
                left.append([lic_of(r), why])
            continue
        # one row per business site: the same name at the same address, or the same City account and site (a site often gets
        # 2 licenses, sometimes under two spellings of its name; holdout 2, round 2)
        k = (rec["business"].upper(), rec["address"].upper())
        k2 = ("acct", rec["_acct"], rec["_site"]) if rec.get("_acct") and rec.get("_site") else None
        if k in seen or (k2 and k2 in seen):
            reasons["second license at the same site (listed once)"] += 1
            if left is not None:
                left.append([rec["license"], "second license at the same site (listed once)"])
            first = seen[k] if k in seen else seen[k2]
            if rec["licenseType"] != first["licenseType"] and rec["licenseType"] not in first["otherTypes"]:
                first["otherTypes"].append(rec["licenseType"])
            first["_lics"].append(rec["license"])
            continue
        seen[k] = rec
        if k2:
            seen[k2] = rec
        rec["_lics"] = [rec["license"]]
        rec["communityArea"] = area_of(rec["lat"], rec["lon"], areas) or (r.get("community_area_name") or "").title()
        recs.append(rec)
    for rec in recs:                       # a site with any food or liquor license is a food business (The New Factory, holdout 2)
        if rec["segment"] != "food" and any(FOOD_LICENSE.search(t) for t in rec["otherTypes"]):
            rec["segment"] = "food"
    recs.sort(key=lambda x: (x["issued"], x["business"]), reverse=True)
    return recs, reasons


# ---------------------------------------------------------------- what the City's own records add to each row
# Both run in the runner after build(): one grouped query per 40 accounts or licenses. A failed fetch leaves the field
# blank and says so in counts (the list still ships; the app and workbook show the check as not run).
HISTORY_WORDS = {"first": "First license on the City's record for this business",
                 "site": "A new site for a business already licensed elsewhere in Chicago",
                 "added": "A new license at a site where this business already held one"}


def _label(r):
    """history and since from r["_prior"]: [(date, type, here)] of the business's licenses before the window. "relicensed": it held
    this same license type at this site before (a new owner, or the same business licensed again under a new account); "added":
    it held other license types at this site, and this one is new there; "site": it held licenses only at other Chicago sites, so
    this is a new location; "first": none found (holdout 1, round 2). since: the year of the earliest license that decides it."""
    if r.get("_noacct"):
        r["history"], r["since"] = "", ""
        return
    prior = r.get("_prior") or []
    here = [(d, t) for d, t, h in prior if h]
    same = [d for d, t in here if t and t.upper() == (r.get("licenseType") or "").upper()]
    if same:
        r["history"], r["since"] = "relicensed", min(same)[:4]
    elif here:
        r["history"], r["since"] = "added", min(d for d, _ in here)[:4]
    elif prior:
        r["history"], r["since"] = "site", min(d for d, _, _ in prior)[:4]
    else:
        r["history"], r["since"] = "first", ""


def add_history(recs, fetch, start):
    """The business's earlier Chicago licenses under its City account, before the list window starts (2002 on: a business that
    licenses in stages inside the window, say a food license on Oct 1 and a liquor license on Oct 19, is still new). Labels come
    from _label(). start: the window's first day. fetch(accounts) returns City rows with account_number, site_number,
    license_number, license_description, application_type and date_issued. Returns the license numbers that also carry a RENEW
    row: an old license the City re-dated, not a new one (holdout 1)."""
    accts = sorted({r["_acct"] for r in recs if r.get("_acct")})
    hist, renewed = collections.defaultdict(list), set()
    for i in range(0, len(accts), 40):
        for x in fetch(accts[i:i + 40]):
            a, d = str(x.get("account_number") or "").split(".")[0], (x.get("date_issued") or "")[:10]
            n = str(x.get("license_number") or "").split(".")[0]
            if (x.get("application_type") or "").upper() == "RENEW":
                renewed.add(n)
            if a and d:
                hist[a].append((d, str(x.get("site_number") or "").split(".")[0], x.get("license_description") or "", n))
    for r in recs:
        r["_noacct"] = not r.get("_acct")
        rows = [x for x in hist.get(r.get("_acct") or "", []) if x[0] < start]
        r["_prior"] = [(d, t, s == r.get("_site")) for d, s, t, _ in rows]
        r["_oldlics"] = sorted({n for d, s, t, n in rows if s == r.get("_site") and n})
        _label(r)
    return {r["license"] for r in recs if set(r.get("_lics") or [r["license"]]) & renewed}


def name_key(name):
    n = re.sub(r"\s+", " ", (name or "").upper().replace("&", " AND ").strip())
    while LEGAL_END.search(n):
        n = LEGAL_END.sub("", n).strip()
    return re.sub(r"[^A-Z0-9]", "", re.sub(r"^THE\s+", "", n))


def name_words(name):
    n = re.sub(r"\s+", " ", (name or "").upper().replace("&", " AND ").replace("'", "").replace("\u2019", "").strip())
    while LEGAL_END.search(n):
        n = LEGAL_END.sub("", n).strip()
    return [w for w in re.sub(r"[^A-Z0-9 ]", " ", re.sub(r"^THE\s+", "", n)).split() if w]


def add_name_history(recs, fetch, start):
    """The same business under another City account (holdout 2, Oct 22): "The Blackstone Hotel" holds licenses at 636 S Michigan
    Ave under one account and its new license under another. A license issued before the window at the same building (a range
    "636-638" counts as 636) under the same shown name ("&" and "and" alike; a longer name that starts with the other, as in "La
    Quinta Inn and Suites Chicago Downtown", counts) is the business's license at this site. fetch(buildings) returns City rows
    with address, doing_business_as_name, license_description, license_number and date_issued at those buildings."""
    blds = sorted({split_address(r.get("_addr") or r["address"])[0] for r in recs if not r.get("_noacct")})
    seen = collections.defaultdict(list)
    for i in range(0, len(blds), 15):
        for x in fetch(blds[i:i + 15]):
            d = (x.get("date_issued") or "")[:10]
            if d and d < start and x.get("address"):
                seen[building_key(x["address"])].append((x.get("doing_business_as_name") or "", d, x.get("license_description") or "",
                                                         str(x.get("license_number") or "").split(".")[0]))
    def same(a, b):
        """The same name, or one name is the other's first whole words with at least 5 letters ("Julie's" and "Julie's Salon and
        Spa"; "La Quinta Inn and Suites" and "... Chicago Downtown"; holdout 1, round 3)."""
        if a == b:
            return True
        ta, tb = name_words(a), name_words(b)
        short, long_ = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
        return bool(short) and len("".join(short)) >= 5 and long_[:len(short)] == short
    for r in recs:
        if r.get("_noacct"):
            continue
        rk = r["business"]
        hits = [x for x in seen.get(building_key(r.get("_addr") or r["address"]), []) if x[0] and same(x[0], rk)]
        if hits:
            r["_prior"] = (r.get("_prior") or []) + [(d, t, True) for _, d, t, _ in hits]
            r["_oldlics"] = sorted(set(r.get("_oldlics") or []) | {n for _, _, _, n in hits if n})
            _label(r)
    return recs


def fetch_by_building(blds):
    def q(b):
        b = b.replace("'", "''")
        m = re.match(r"^(\d+)(?:-\d+)? (.+)$", b)
        alt = f" OR address like '{m.group(1)}-% {m.group(2)}%'" if m else ""      # "636 S MICHIGAN AVE" also finds "636-638 S MICHIGAN AVE"
        return f"starts_with(address, '{b}'){alt}"
    return get(f"{PORTAL}/resource/{DATASET}.json", {"$select": "address,doing_business_as_name,license_description,license_number,date_issued",
                                                     "$where": " OR ".join(q(b) for b in blds), "$limit": 50000})


def add_food_inspections(recs, fetch):
    """Food and drink rows only (the restaurant product lists food businesses; holdout 1). foodInsp: the newest City food license
    inspection (type License or License Re-Inspection) on file for any license at the site (the City's Food Inspections dataset,
    4ijn-s7e5, files it under the business license number), in the 120 days before the license was issued: what Chicago
    Restaurant Inspection Leads lists as "Opening soon". inspSince: the year of the earliest other City food inspection (a
    canvass or a complaint) before the license was issued, which shows the business was open before this license. fetch(licenses)
    returns rows with license_, inspection_type and inspection_date."""
    food = [r for r in recs if r["segment"] == "food"]
    lic = sorted({n for r in food for n in (r.get("_lics") or [r["license"]]) + (r.get("_oldlics") or []) if n})
    seen = collections.defaultdict(list)
    for i in range(0, len(lic), 40):
        for x in fetch(lic[i:i + 40]):
            n, d = str(x.get("license_") or "").split(".")[0], (x.get("inspection_date") or "")[:10]
            if n and d:
                seen[n].append((d, (x.get("inspection_type") or "").upper()))
    for r in recs:
        r["foodInsp"], r["inspSince"] = "", ""
    for r in food:
        start = (dt.date.fromisoformat(r["issued"]) - dt.timedelta(days=120)).isoformat()
        got = [x for n in (r.get("_lics") or [r["license"]]) for x in seen.get(n, [])]
        old = [x for n in (r.get("_oldlics") or []) for x in seen.get(n, [])]       # the same business's earlier licenses here
        ds = [d for d, t in got if t.startswith("LICENSE") and start <= d <= r["issued"]]
        op = [d for d, t in got + old if not t.startswith("LICENSE") and d < r["issued"]]
        r["foodInsp"], r["inspSince"] = (max(ds) if ds else ""), (min(op)[:4] if op else "")
    return recs


def flagged_buildings(recs, home, virtual):
    """{license: reason} for rows the City's other licenses place in a home or a mail drop (holdout 1, Oct 22). home and virtual
    are building keys (building_key) with a City Home Based Business or Home Occupation license, or a Virtual Office Services
    license, on record. A row in a home-based building is left out when its address has a unit above the ground floor (the
    storefront of a mixed building stays). virtual maps a building key to the units of its current Virtual Office Services
    licenses: a row is a mail drop when that license covers the whole building (no unit) or the row's own unit, so a gym in an
    office tower with one virtual-office suite stays (Kinema Fitness, holdout 2, round 3)."""
    out = {}
    norm = lambda u: re.sub(r"[^A-Z0-9]", "", (u or "").upper())
    for r in recs:
        b, unit = split_address(r.get("_addr") or r["address"])
        k = building_key(r.get("_addr") or r["address"])
        vu = virtual.get(k) if isinstance(virtual, dict) else ({""} if k in virtual else None)
        first_no = (re.findall(r"\d+", unit) or [""])[0]
        # a box under a mail center's suite ("121-5113" under "1ST 121", My Mail Center at 332 S Michigan; holdout 2, round 4)
        boxed = bool(first_no) and len(re.findall(r"\d+", unit)) >= 2 and any(re.findall(r"\d+", v) and re.findall(r"\d+", v)[-1] == first_no for v in (vu or ()))
        if vu is not None and ("" in vu or norm(unit) in vu or boxed):
            out[r["license"]] = MAILBOX_REASON
        elif k in home and unit and not GROUND_UNIT.match(unit.strip()):
            out[r["license"]] = RESIDENTIAL_REASON
    return out


def fetch_buildings():
    """(home, virtual): building keys from the City's whole Business Licenses record (2002 on)."""
    def keys(where, at_least):
        n, off = collections.Counter(), 0
        while True:
            page = get(f"{PORTAL}/resource/{DATASET}.json", {"$select": "address", "$where": where, "$group": "address",
                                                            "$order": "address", "$limit": 50000, "$offset": off})
            n.update(building_key(x.get("address")) for x in page if x.get("address"))   # one count per distinct address in the building
            if len(page) < 50000:
                return {k for k, c in n.items() if c >= at_least}
            off += 50000
    # a building is residential when home-based licenses sit at two or more of its addresses (one home office in an office
    # tower or a loft building does not make it a home; holdout 2, round 2)
    def virtual_units():
        """{building key: {unit}} for virtual office licenses still current (not cancelled or expired): a cancelled one at
        625 W Adams says nothing about the building today (holdout 2, round 3)."""
        out, off = collections.defaultdict(set), 0
        today = chicago_now().date().isoformat()
        while True:
            page = get(f"{PORTAL}/resource/{DATASET}.json", {"$select": "address,license_status,expiration_date",
                                                            "$where": "upper(business_activity) like '%VIRTUAL OFFICE%'", "$limit": 50000, "$offset": off})
            for x in page:
                if x.get("address") and (x.get("license_status") or "").upper() == "AAI" and (x.get("expiration_date") or "9999")[:10] >= today:
                    out[building_key(x["address"])].add(re.sub(r"[^A-Z0-9]", "", split_address(x["address"])[1].upper()))
            if len(page) < 50000:
                return dict(out)
            off += 50000
    return (keys("upper(business_activity) like '%HOME BASED%' OR upper(license_description) like 'HOME OCCUPATION%'", 2), virtual_units())


def run_checks(recs, reasons, today, f_hist, f_food, f_build, f_name=None, left=None):
    """The City's own records on top of build(): the building checks (home and mail-drop addresses), the business's history
    (and old licenses the City re-dated), then the food inspections on the rows that are left. A check that cannot fetch is
    marked not run; the list still ships, and the app and workbook say so. Returns (records, checks)."""
    checks, drop = {}, {}
    try:
        home, virtual = f_build()
        drop.update(flagged_buildings(recs, home, virtual)); checks["buildings"] = True
    except SystemExit as e:
        print(f"buildings check did not run: {e}"); checks["buildings"] = False
    try:
        start = (today - dt.timedelta(days=WINDOW_DAYS)).isoformat()
        for lic in add_history(recs, f_hist, start):
            drop.setdefault(lic, "not a new license (renewal or change)")
        if f_name:
            add_name_history(recs, f_name, start)
        checks["history"] = True
    except SystemExit as e:
        print(f"history check did not run: {e}"); checks["history"] = False
        for r in recs:
            r["history"], r["since"] = "", ""
    for lic, why in drop.items():
        reasons[why] += 1
        if left is not None:
            left.append([lic, why])
    recs = [r for r in recs if r["license"] not in drop]
    try:
        add_food_inspections(recs, f_food); checks["foodInspections"] = True
    except SystemExit as e:
        print(f"foodInspections check did not run: {e}"); checks["foodInspections"] = False
        for r in recs:
            r["foodInsp"], r["inspSince"] = "", ""
    return strip_internal(recs), checks


def strip_internal(recs):
    for r in recs:
        for k in ("_acct", "_site", "_lics", "_addr", "_prior", "_oldlics", "_noacct"):
            r.pop(k, None)
    return recs


def fetch_history(accts):
    return get(f"{PORTAL}/resource/{DATASET}.json",
               {"$select": "account_number,site_number,license_number,license_description,application_type,date_issued",
                "$where": f"account_number in ({','.join(accts)})", "$limit": 50000})


def fetch_food(lics):
    return get(f"{PORTAL}/resource/{FOOD}.json",
               {"$select": "license_,inspection_type,inspection_date", "$where": f"license_ in ({','.join(lics)})", "$limit": 50000})


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
    since = (chicago_now().date() - dt.timedelta(days=42)).isoformat()
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
    now = chicago_now()          # Chicago time: a run at 7 pm Central is still today's list, not tomorrow's (CLAUDE.md 0)
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
    left = []
    recs, reasons = build(rows, areas, today, left=left)
    recs, checks = run_checks(recs, reasons, today, fetch_history, fetch_food, fetch_buildings, fetch_by_building, left=left)
    week_from = (today - dt.timedelta(days=7)).isoformat()
    week = [r for r in recs if r["issued"] >= week_from]
    labels = {k: lab for k, lab, _ in SEGMENTS}
    public = lambda r: {k: r[k] for k in ("business", "address", "communityArea", "licenseType", "activity", "issued")}
    source = {"name": "City of Chicago Data Portal, Business Licenses", "url": DATASET_PAGE, "rowsUpdatedAt": upd_iso,
              "fetchedAt": now.isoformat(timespec="seconds"), "terms": TERMS,
              "modified": ("Filtered by ProofNotFluff: new business licenses (application type Issue) issued in the last 30 days at a "
                           "Chicago business site, one row per business and address. Left out: renewals, cancelled or revoked licenses, licenses for one person's own work, for work "
                           "away from a fixed business site, or for an event or season (peddlers, special events, pop-ups, "
                           "tow trucks, home-sharing, shared kitchen users, private booting), home "
                           "and mail-drop addresses, and any business whose name could be a person's name. Business-level fields only.")}
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
        json.dump({"source": source, "window": sample["window"], "counts": sample["counts"], "records": recs, "leftOut": left},
                  open(a.full, "w"), indent=1)
    print(json.dumps({"fetched": len(rows), "kept30": len(recs), "keptWeek": len(week), "excluded": dict(reasons),
                      "checks": checks, "history30": sample["counts"]["history30"], "foodInsp30": sample["counts"]["foodInsp30"]}))


# ---------------------------------------------------------------- planted cases (invented businesses, real City field names)
def selftest():
    for name, want in [("JOHN SMITH", True), ("MARIA G LOPEZ", True), ("O'BRIEN KELLY", True), ("ANNA-MARIE DE LA CRUZ", True),
                       ("JOHN SMITH LLC", True), ("NOEL MERCADO L.L.C.", True), ("ANNA LEE, INC.", True),   # LLC never makes a name a business
                       ("ACME HOLDINGS LLC", False), ("MARIA'S TAQUERIA", False), ("SMITH & SONS", False), ("KFC", False),
                       ("LUNA NAIL SPA", False), ("GOLDEN DRAGON", True), ("ACME 24 HOUR FITNESS", False), ("TAQUERO LLC", False), ("", False),
                       ("FAT PEACH BAKESHOP", False), ("LEGACY PARKING", False), ("THE RESERVE", False), ("ADELE BLOOM LLC", True)]:
        assert could_be_person(name) == want, (name, could_be_person(name), want)
    for name, want in [("ARIANNA BARONE BEAUTY", True), ("MARIA LOPEZ CLEANING LLC", True), ("MARIA'S KITCHEN", False),
                       ("QUEEN NAILS BY ZOE", False), ("BIG DAWG MARKET", False), ("JULIE'S SALON AND SPA", False), ("ANGEL NAILS", False)]:
        assert holds_full_name(name) == want, (name, holds_full_name(name), want)   # holdout 2, round 2
    assert GROUND_UNIT.match("1 NW") and GROUND_UNIT.match("B") and not GROUND_UNIT.match("20TH 2021") and not GROUND_UNIT.match("2 2R")
    for raw, want in [("LA CASA DE LAS FLORES", "La Casa de las Flores"), ("LA CALACA CANTINA", "La Calaca Cantina"),
                      ("LA FITNESS", "LA Fitness"), ("YATES LIQUOR", "Yates Liquor"), ("The UPS Store", "The UPS Store"),
                      ("ChaTraMue", "ChaTraMue"), ("(GEI-184)  Shop", "(GEI-184) Shop"), ("ACME (HAMOC)", "Acme (HAMOC)"),
                      ("87TH QUICK STOP", "87th Quick Stop"), ("NEVERIA LA GARRAFITA", "Neveria La Garrafita")]:
        assert name_case(raw) == want, (raw, name_case(raw))
    for desc, act, want in [("Regulated Business License", "Computer Consulting Services / Computer Automated Design", "retail"),
                            ("Motor Vehicle Services License", "Motor Vehicle Repair - Engine and Transmission Work", "auto"),
                            ("Limited Business License", "Hair Services", "beauty"), ("Filling Station", "", "auto"),
                            ("Package Goods", "Retail Sales of Packaged Liquor", "food"),
                            ("Limited Business License", "Skincare Services | Provide Waxing Services", "beauty"),
                            ("Commercial Garage", "Provide 4 or More Parking Spaces For a Fee", "retail"),
                            # holdout 1: the City's stock "non-perishable food" activity never makes a row food
                            ("Limited Business License", "Mail Services | Retail Sales of General Merchandise and Non-Perishable Food", "retail"),
                            ("Limited Business License", "Health Club / Fitness Center | Retail Sales of General Merchandise and Non-Perishable Food", "beauty"),
                            ("Limited Business License", "Hand Car Wash | Retail Sales of General Merchandise and Non-Perishable Food", "auto"),
                            ("Public Place of Amusement", "Charges a Fee for Entertainment | Retail Sales of General Merchandise and Non-Perishable Food", "venue"),
                            ("Retail Food Establishment", "Retail Sales of General Merchandise and Non-Perishable Food", "food"),
                            ("Animal Care License", "Dog Day Care | Boarding | Grooming", "retail"),
                            ("Limited Business License", "Sale of Vehicle Parts and Accessories", "auto"),
                            ("Children's Services Facility License", "Day Care Center", "care"),
                            ("Limited Business License", "Retail Sales of General Merchandise and Non-Perishable Food | Retail Sales of Perishable Foods", "food")]:
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
        dict(base, license_number="18", doing_business_as_name="OLD PIZZA STORE", legal_name="OPS INC", license_description="Retail Food Establishment",
             license_approved_for_issuance="2024-06-26T00:00:00.000", address="1700 W LAKE ST"),     # approved in 2024, re-dated: out
        dict(base, license_number="25", doing_business_as_name="AIRPORT BURGERS", legal_name="AB INC", license_description="Retail Food Establishment",
             license_approved_for_issuance="2026-08-20T00:00:00.000", address="2100 W LAKE ST"),     # approved 8 weeks before issue: new, kept
        dict(base, license_number="19", doing_business_as_name="ACME CONSULTING", legal_name="AC LLC", license_description="Limited Business License",
             address="980 N MICHIGAN AVE STE 1090 #453522"),                                        # private mailbox: out
        dict(base, license_number="20", doing_business_as_name="STEW KITCHEN", legal_name="SK LLC", license_description="Shared Kitchen User (Long Term)",
             address="4329 N MOZART ST 1F"),                                                         # shared kitchen user: out
        dict(base, license_number="21", doing_business_as_name="LAKE INN", legal_name="LI LLC", license_description="Limited Business License",
             business_activity="Bed and Breakfast Establishment, Owner-Occupied", address="1800 W LAKE ST"),   # bed and breakfast: out
        dict(base, license_number="22", doing_business_as_name="ZAS CONSULTING", legal_name="Z LLC", license_description="Limited Business License",
             business_activity="Home Repair Services | Snowplowing", address="1900 W LAKE ST"),       # home repair: out
        dict(base, license_number="23", doing_business_as_name="NEW FACTORY VENUE", legal_name="NF LLC", license_description="Public Place of Amusement",
             account_number="777", site_number="4", address="2000 W LAKE ST 1"),
        dict(base, license_number="24", doing_business_as_name="THE NEW FACTORY", legal_name="NF LLC", license_description="Retail Food Establishment",
             account_number="777", site_number="4", address="2000 W LAKE ST", date_issued="2026-10-17T00:00:00.000"),   # same account and site: one row, food
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
    assert {r["license"] for r in gone} == {"1", "4", "5", "23", "25"} and why[DNL_REASON] == 2, (sorted(r["license"] for r in gone), dict(why))
    try:
        json.dump({"salt": "wrong", "keys": []}, open(tf, "w")); dnl_load(tf)
        raise AssertionError("a broken do-not-list must stop the build")
    except SystemExit:
        pass
    recs, reasons = build(rows, loop, today, dnl=set())
    by = {r["license"]: r for r in recs}
    assert set(by) == {"1", "4", "5", "7", "14", "23", "25"}, sorted(by)
    assert by["23"]["segment"] == "food" and by["23"]["otherTypes"] == ["Retail Food Establishment"] and by["23"]["_lics"] == ["23", "24"], by["23"]
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
        rows_ = [{"account_number": a + ".0", "site_number": s, "date_issued": d + "T00:00:00.000", "license_number": "9" + a,
                  "application_type": "ISSUE"} for a in accts for d, s in hist.get(a, [])]
        return rows_ + [{"account_number": "105", "site_number": "1", "license_number": "5", "application_type": "RENEW",
                         "date_issued": "2026-10-16T00:00:00.000"}]       # license 5 also has a RENEW row: an old license
    renewed = add_history(recs, fake_hist, "2026-09-20")
    assert renewed == {"5"}, renewed
    assert [(by[k]["history"], by[k]["since"]) for k in ("1", "4", "5", "7", "14")] == [
        ("first", ""), ("added", "2019"), ("first", ""), ("first", ""), ("site", "2015")], [(by[k]["history"], by[k]["since"]) for k in by]
    assert calls == [7], calls
    # food inspections: food rows only; the License inspection under the site's second license; a canvass before the license
    food = {"2": [("2026-10-02", "License"), ("2026-10-09", "License Re-Inspection"), ("2025-01-01", "License"), ("2025-03-04", "Canvass")],
            "5": [("2026-10-17", "License")], "4": [("2026-10-01", "License")]}
    asked = []
    def fake_food(lics):
        asked.extend(lics)
        return [{"license_": n + ".0", "inspection_date": d + "T00:00:00.000", "inspection_type": t} for n in lics for d, t in food.get(n, [])]
    add_food_inspections(recs, fake_food)
    assert by["1"]["foodInsp"] == "2026-10-09" and by["1"]["inspSince"] == "2025", (by["1"]["foodInsp"], by["1"]["inspSince"])
    assert by["4"]["foodInsp"] == "" and "4" not in asked and by["5"]["foodInsp"] == "", "food rows only, never after the issue date"
    # the building checks: a unit above the ground floor in a building with home-based licenses, any row at a virtual office
    assert split_address("3950 N LAKE SHORE DR 20TH 2021") == ("3950 N LAKE SHORE DR", "20TH 2021")
    assert split_address("11611-11613 S HALSTED ST 1ST") == ("11611-11613 S HALSTED ST", "1ST") and building_key("11611-11613 S Halsted St") == "11611SHALSTEDST"
    probe = [{"license": "a", "address": "3950 N Lake Shore Dr 20th 2021"}, {"license": "b", "address": "2049 W Belmont Ave 1 1"},
             {"license": "c", "address": "1655 S Blue Island Ave 2 100"}, {"license": "d", "address": "2049 W Belmont Ave 2 2R"},
             {"license": "e", "address": "500 N State St Ste 300"}]
    fl = flagged_buildings(probe, {"3950NLAKESHOREDR", "2049WBELMONTAVE", "500NSTATEST"}, {"1655SBLUEISLANDAVE"})
    assert fl == {"a": RESIDENTIAL_REASON, "c": MAILBOX_REASON, "d": RESIDENTIAL_REASON}, fl
    gym = [{"license": "g", "address": "180 N Stetson Ave 1"}, {"license": "h", "address": "180 N Stetson Ave 35 3500"},
           {"license": "i", "address": "1655 S Blue Island Ave 2 100"}]
    assert flagged_buildings(gym, set(), {"180NSTETSONAVE": {"353500"}, "1655SBLUEISLANDAVE": {""}}) == {"h": MAILBOX_REASON, "i": MAILBOX_REASON}
    box = [{"license": "k", "address": "332 S Michigan Ave 121-5113"}, {"license": "l", "address": "332 S Michigan Ave 1200"}]
    assert flagged_buildings(box, set(), {"332SMICHIGANAVE": {"1ST121"}}) == {"k": MAILBOX_REASON}, "a box under the mail center's suite"
    # same license type at the same site before: relicensed (a new owner or a new account), not added (holdout 1, round 2)
    rl = [{"license": "p", "business": "Plush Pup", "address": "5344 N Cumberland Ave", "_addr": "5344 N CUMBERLAND AVE", "licenseType": "Retail Food Establishment",
           "_acct": "9", "_site": "1", "issued": "2026-10-10", "segment": "food"},
          {"license": "q", "business": "Spa Two", "address": "1 W Main St", "_addr": "1 W MAIN ST", "licenseType": "Limited Business License",
           "_acct": "8", "_site": "1", "issued": "2026-10-10", "segment": "beauty"}]
    add_history(rl, lambda a: [{"account_number": "8", "site_number": "1", "license_number": "77", "license_description": "Limited Business License",
                               "application_type": "ISSUE", "date_issued": "2014-02-01"},
                              {"account_number": "8", "site_number": "1", "license_number": "78", "license_description": "Tobacco",
                               "application_type": "ISSUE", "date_issued": "2010-02-01"}], "2026-09-22")
    add_name_history(rl, lambda b: [{"address": "5344 N CUMBERLAND AVE", "doing_business_as_name": "PLUSH PUP", "license_description": "Retail Food Establishment",
                                     "license_number": "1647850", "date_issued": "2005-03-01"}], "2026-09-22")
    assert [(x["history"], x["since"]) for x in rl] == [("relicensed", "2005"), ("relicensed", "2014")], [(x["history"], x["since"]) for x in rl]
    add_food_inspections(rl, lambda lics: [{"license_": "1647850", "inspection_type": "Canvass", "inspection_date": "2010-05-05"}] if "1647850" in lics else [])
    assert rl[0]["inspSince"] == "2010", "the same business's earlier license at the site counts for food inspections since"
    # the same business under another account at the same building is an added license, not a first (Blackstone Hotel)
    hrec = [{"license": "x", "business": "The Blackstone Hotel", "address": "636 S Michigan Ave", "_addr": "636 S MICHIGAN AVE",
             "history": "first", "since": ""},
            {"license": "y", "business": "New Cafe", "address": "636 S Michigan Ave", "_addr": "636 S MICHIGAN AVE", "history": "first", "since": ""},
            {"license": "z", "business": "La Quinta Inn and Suites Chicago Downtown", "address": "1 S Franklin St", "_addr": "1 S FRANKLIN ST",
             "history": "site", "since": "2020"}]
    add_name_history(hrec, lambda b: [{"address": "636 S MICHIGAN AVE LL-23", "doing_business_as_name": "BLACKSTONE HOTEL",
                                       "date_issued": "2018-10-16T00:00:00.000"},
                                      {"address": "1 S FRANKLIN ST", "doing_business_as_name": "LA QUINTA INN AND SUITES", "date_issued": "2016-05-01T00:00:00"},
                                      {"address": "636 S MICHIGAN AVE", "doing_business_as_name": "NEW", "date_issued": "2010-01-01"},
                                      {"address": "636 S MICHIGAN AVE", "doing_business_as_name": "NEW CAFETERIA", "date_issued": "2011-01-01"}], "2026-09-22")
    assert [(h["history"], h["since"]) for h in hrec] == [("added", "2018"), ("first", ""), ("added", "2016")], hrec   # "NEW CAFETERIA" is not "New Cafe"
    jr = [{"license": "j", "business": "Julie's Salon and Spa", "address": "7012 N Western Ave", "_addr": "7012 N WESTERN AVE",
           "licenseType": "Limited Business License", "history": "first", "since": ""}]
    add_name_history(jr, lambda b: [{"address": "7012 N WESTERN AVE", "doing_business_as_name": "JULIE'S", "license_description": "Limited Business License",
                                     "date_issued": "2003-05-01"}], "2026-09-22")
    assert (jr[0]["history"], jr[0]["since"]) == ("relicensed", "2003"), jr   # holdout 1, round 3
    # run_checks drops what the City's records rule out, counts the reasons, and marks a check that cannot fetch
    r2, rs2 = build(rows, loop, today, dnl=set())
    def boom(*a):
        raise SystemExit("fetch failed")
    got, ch = run_checks(r2, rs2, today, fake_hist, boom, lambda: ({"300SWABASHAVE"}, {"400WLAKEST"}))
    assert {r["license"] for r in got} == {"1", "4", "7", "14", "23", "25"} and rs2[MAILBOX_REASON] == 2, (sorted(r["license"] for r in got), dict(rs2))
    assert ch == {"buildings": True, "history": True, "foodInspections": False} and all(r["foodInsp"] == "" for r in got), ch
    strip_internal(recs)
    assert not any(k.startswith("_") for r in recs for k in r), "account and site numbers never leave the runner"
    blob = json.dumps(recs).upper()
    assert "JOHN Q PUBLIC" not in blob and "LEGAL" not in blob, "a legal name leaked into the records"
    want = {"second license at the same site (listed once)": 2, "name could be a person's": 1,
            PERSON_EVENT_REASON: 7, "home or apartment address": 2,
            "not a new license (renewal or change)": 2, "issued outside the window": 1, "site outside Chicago": 1,
            "license not active (cancelled or revoked)": 1, MAILBOX_REASON: 1}
    assert dict(reasons) == want, dict(reasons)
    long = " | ".join(["Retail Sales of General Merchandise and Non-Perishable Food"] * 8)
    assert activity_text(long) == " | ".join(["Retail Sales of General Merchandise and Non-Perishable Food"] * 4) + " | and 4 more", activity_text(long)
    assert activity_text("Hair Services") == "Hair Services"
    print(f"licenses selftest ok (17 planted names, 13 planted trades, {len(rows)} planted licenses, 2 planted removals, 5 planted histories, 2 planted food inspections)")


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
