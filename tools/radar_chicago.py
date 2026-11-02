#!/usr/bin/env python3
"""Chicago Restaurant Radar v1 (launches/chicago-restaurant-radar.md; Todd, live chat, Nov 2, 2026): the data layer.

Follows every Chicago food business along the City's own records, from a build-out permit to opening, and joins three
datasets the crew already pulls on the address (and on the license number where the inspection carries it):

  Permitted   City of Chicago Building Permits (ydr8-5enu): a permit at the address
  Inspected   Food Inspections (4ijn-s7e5): the License (pre-opening) inspection, filed under the license number
  Licensed    Business Licenses (r5kz-chrr): a new food license, application type Issue
  Open        a routine City inspection (canvass or complaint) passed after the license, or 30 days since the license was
              issued after a passed license inspection (our rule, labelled as ours)

The stage order is the order the City's records actually run in: Chicago inspects a food business before it issues the
license (tools/licenses_chicago.py add_food_inspections found a license inspection in the 120 days before issue on 85 of 90
food licenses, Nov 2, 2026), so a business is Inspected before it is Licensed. match.json counts how often that holds.

Runs in GitHub Actions (.github/workflows/radar-chicago.yml): the cloud agents cannot reach data.cityofchicago.org.
Business fields only. The license layer is tools/licenses_chicago.py's own build and checks (person-like names, home and
mail-drop addresses, events and person-held licenses, its do-not-list). Inspection-only rows get tools/rest_leads.py's
person-name, institution and do-not-list rules. Permit contact names, inspector names and inspection comments are never
read into the output (the violations column is never selected).

Outputs: --full the members' list (runner temp only; the workflow seals it to a public key), --match counts only (public),
--holdout the City's own rows for a few businesses picked at random, pulled by separate plain queries, for the hand check.

Usage: python3 tools/radar_chicago.py --full OUT.json --match permits/radar-chicago/match.json --holdout HOLD.json
       python3 tools/radar_chicago.py --selftest
"""
import argparse, collections, datetime as dt, json, os, random, re, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import licenses_chicago as lc  # noqa: E402
import pnf_rules as R  # noqa: E402
import rest_leads as rl  # noqa: E402
from permits_chicago import clean_scope, RESIDENTIAL_SMALL  # noqa: E402

PORTAL = "https://data.cityofchicago.org"
LIC, FOOD, PERMITS = "r5kz-chrr", "4ijn-s7e5", "ydr8-5enu"
RECORD = {"license": f"{PORTAL}/resource/{LIC}.json?license_number=",
          "inspection": f"{PORTAL}/resource/{FOOD}.json?inspection_id=",
          "permit": f"{PORTAL}/resource/{PERMITS}.json?permit_="}
DATASET_PAGES = {"licenses": f"{PORTAL}/Community-Economic-Development/Business-Licenses/{LIC}",
                 "inspections": f"{PORTAL}/Health-Human-Services/Food-Inspections/{FOOD}",
                 "permits": f"{PORTAL}/Buildings/Building-Permits/{PERMITS}"}
TERMS = "https://www.chicago.gov/city/en/narr/foia/data_disclaimer.html"
OUT_DIR = os.path.join(ROOT, "permits", "radar-chicago")

WINDOW = 180          # days: a business enters the radar with a City record in the last 180 days
PRE_LICENSE = 150     # days before the license issue date a pre-opening inspection is looked for
PENDING = 120         # days: an inspected business with no license yet stays on the radar this long
PERMIT_BACK = 540     # days: a permit up to 18 months before the business's first other record counts as its build-out
OPEN_RULE_DAYS = 30
STAGES = ["permitted", "inspected", "licensed", "open"]
STAGE_LABEL = {"permitted": "Permitted", "inspected": "Inspected", "licensed": "Licensed", "open": "Open"}
BUILD_TYPES = re.compile(r"RENOVATION|ALTERATION|NEW CONSTRUCTION|EASY PERMIT|SIGNS", re.I)
PASSED = {"PASS", "PASS W/ CONDITIONS"}

# words in a permit's work text that tie it to a food business (a kitchen alone is any home's kitchen)
FOOD_WORDS = re.compile(r"RESTAURANT|RESTAURNT|\bCAFE\b|\bCAFÉ\b|COFFEE|BAKERY|BAKE SHOP|TAVERN|BREWERY|BREW ?PUB|TAPROOM|"
                        r"\bPIZZ|TAQUER|\bDELI\b|GROCERY|SUPERMARKET|ICE CREAM|JUICE BAR|\bTEA (?:SHOP|HOUSE|BAR)|DESSERT|DONUT|"
                        r"BAGEL|SUSHI|RAMEN|BAR (?:AND|&) GRILL|\bBAR/RESTAURANT|FOOD SERVICE|FOOD ESTABLISHMENT|FOOD HALL|"
                        r"COMMERCIAL KITCHEN|CATERING|TYPE (?:I|1|ONE) HOOD|KITCHEN HOOD|EXHAUST HOOD|HOOD (?:AND|&) DUCT|GREASE (?:TRAP|INTERCEPTOR)|"
                        r"CARRY[- ]?OUT|TAKE[- ]?OUT|FAST FOOD|\bEATERY|\bDINER\b|\bBISTRO|\bGRILL\b|KITCHEN EXHAUST|WALK[- ]IN (?:COOLER|FREEZER)", re.I)
NOT_FOOD = re.compile(r"GRAB BARS?|REBAR|\bBAR JOISTS?|TOWEL BAR", re.I)

KINDS = [  # key, label: the type of food business a rule can name
    ("restaurant", "Restaurant"), ("coffee", "Coffee or drinks"), ("bakery", "Bakery or dessert"), ("bar", "Bar or tavern"),
    ("grocery", "Grocery or market"), ("liquor", "Liquor store"), ("catering", "Caterer or shared kitchen"), ("other", "Other food business")]
KIND_LABEL = dict(KINDS)


def food_kind(*texts):
    """The type of food business from the City's own words, most specific first (business activity, license type, the
    inspection's facility type, permit text): the first text that names a kind decides."""
    for x in texts:
        k = _kind(x)
        if k != "other":
            return k
    return "other"


def _kind(x):
    t = (x or "").upper()
    if re.search(r"DINING|RESTAURANT|PREPARATION OF FOOD|PREPARED ONSITE|PREPARED ON-SITE|\bGRILL\b|PIZZ|TAQUER|SUSHI|RAMEN|EATERY|DINER", t):
        return "restaurant"
    if re.search(r"COFFEE|DRINKS|JUICE|\bTEA\b|SMOOTHIE|BOBA", t):
        return "coffee"
    if re.search(r"BAKERY|BAKED|PASTR|DESSERT|ICE CREAM|DONUT|BAGEL|CONFECTION|CANDY", t):
        return "bakery"
    if re.search(r"TAVERN|CONSUMPTION ON PREMISES|BREW|\bBAR\b|LOUNGE|TAPROOM", t):
        return "bar"
    if re.search(r"PACKAGE GOODS|PACKAGED LIQUOR", t):
        return "liquor"
    if re.search(r"GROCERY|PERISHABLE|MARKET|SUPERMARKET|PRODUCE|MEAT|BUTCHER|FISH", t):
        return "grocery"
    if re.search(r"CATER|SHARED KITCHEN|COMMISSARY|WHOLESALE", t):
        return "catering"
    return "other"


def building(addr):
    """The address key of a site: house number (first of a range), direction, street and suffix, no unit. Uses
    licenses_chicago.street_unit so "3509 S Dr Martin Luther King Jr Dr 2" keeps its whole street name."""
    st, _ = lc.street_unit(re.sub(r"\s+", " ", (addr or "").upper().strip()))
    return R.address_key(st)


def permit_key(p):
    return R.address_key(" ".join(x for x in (p.get("street_number"), p.get("street_direction"), p.get("street_name")) if x))


def day(v):
    return (v or "")[:10]


def lic_num(v):
    s = str(v or "").split(".")[0].strip()
    return s if s.isdigit() and s != "0" else ""


def permit_is_food(p, name=""):
    """A permit tied to a food business by its own text: food words, or the business's own distinctive name word."""
    d = NOT_FOOD.sub(" ", (p.get("work_description") or "").upper())
    if FOOD_WORDS.search(d):
        return True
    for w in lc.name_words(name):
        if len(w) >= 5 and w not in {"CHICAGO", "KITCHEN", "MARKET", "GROUP", "FOODS", "STORE", "HOUSE", "STREET", "COMPANY"} and re.search(r"\b" + re.escape(w) + r"\b", d):
            return True
    return False


def permit_event(p, food):
    scope = clean_scope(p.get("work_description") or "", limit=160)
    return {"t": "permit", "d": day(p.get("issue_date")), "id": str(p.get("permit_") or ""), "type": (p.get("permit_type") or "").replace("PERMIT - ", "").title(),
            "scope": scope, "food": bool(food), "link": RECORD["permit"] + str(p.get("permit_") or "")}


def insp_event(x):
    t = rl.type_title(x.get("inspection_type"))
    return {"t": "linsp" if t.upper().startswith("LICENSE") else "routine", "d": day(x.get("inspection_date")), "id": str(x.get("inspection_id") or ""),
            "type": t, "result": (x.get("results") or "").strip(), "link": RECORD["inspection"] + str(x.get("inspection_id") or "")}


def stage_of(b, today):
    """(stage, stage date, how): the furthest stage the City's records show, in the order they run."""
    ev = b["events"]
    lic = [e for e in ev if e["t"] == "license"]
    li = sorted([e for e in ev if e["t"] == "linsp"], key=lambda e: e["d"])
    issued = min((e["d"] for e in lic), default="")
    if issued:
        routine = sorted(e for e in ((e["d"], e["result"].upper()) for e in ev if e["t"] == "routine") if e[0] >= issued and e[1] in PASSED)
        if routine:
            return "open", routine[0][0], "routine"
        passed = [e["d"] for e in li if e["result"].upper() in PASSED]
        if passed and (today - dt.date.fromisoformat(max(issued, max(passed)))).days >= OPEN_RULE_DAYS:
            d = (dt.date.fromisoformat(max(issued, max(passed))) + dt.timedelta(days=OPEN_RULE_DAYS)).isoformat()
            return "open", d, "rule"
        return "licensed", issued, ""
    if li:
        return "inspected", li[-1]["d"], ""
    perm = [e["d"] for e in ev if e["t"] == "permit"]
    return "permitted", max(perm), ""


# ---------------------------------------------------------------- the City's rows (runner only)
class City:
    """The plain pulls. Each takes a Socrata-like client so the selftest can plant rows."""
    INSP_COLS = "inspection_id,dba_name,aka_name,license_,facility_type,address,zip,inspection_date,inspection_type,results,latitude,longitude"
    PERMIT_COLS = "id,permit_,permit_type,permit_status,issue_date,street_number,street_direction,street_name,work_description,latitude,longitude"

    def __init__(self, client):
        self.c = client

    def inspections_for(self, lics, since):
        out = []
        lics = sorted({l for l in lics if l.isdigit()})
        for i in range(0, len(lics), 150):
            out += self.c.pull(FOOD, select=self.INSP_COLS, where=f"license_ in ({','.join(lics[i:i + 150])}) AND inspection_date >= '{since}'",
                               order="inspection_id", key="inspection_id")
        return out

    def license_inspections(self, since):
        return self.c.pull(FOOD, select=self.INSP_COLS, where=f"inspection_type in('License','License Re-Inspection') AND inspection_date >= '{since}'",
                           order="inspection_id", key="inspection_id")

    def license_rows(self, lics):
        out = []
        lics = sorted({l for l in lics if l.isdigit()})
        for i in range(0, len(lics), 150):
            out += self.c.pull(LIC, select="license_number,application_type,date_issued,license_status,license_description",
                               where=f"license_number in ({','.join(lics[i:i + 150])})", order="license_number")
        return out

    def permits_at(self, numbers, since):
        out = []
        nums = sorted({n for n in numbers if n.isdigit()}, key=int)
        for i in range(0, len(nums), 120):
            vals = ",".join("'" + n + "'" for n in nums[i:i + 120])
            out += self.c.pull(PERMITS, select=self.PERMIT_COLS, where=f"street_number in({vals}) AND issue_date >= '{since}'", order="id", key="id")
        return out

    def food_permits(self, since):
        words = ["RESTAURANT", "CAFE", "COFFEE", "BAKERY", "TAVERN", "BREWERY", "PIZZ", "TAQUER", "FOOD", "GROCERY", "HOOD", "GREASE", "DELI",
                 "CARRY", "EATERY", "DINER", "BISTRO", "GRILL", "SUSHI", "RAMEN", "DESSERT", "ICE CREAM", "JUICE", "DONUT", "BAGEL", "CATERING", "KITCHEN"]
        like = " OR ".join(f"upper(work_description) like '%{w}%'" for w in words)
        return self.c.pull(PERMITS, select=self.PERMIT_COLS, where=f"issue_date >= '{since}' AND ({like})", order="id", key="id")

    def zip_centers(self):
        """{zip: [lat, lon, n]}: the average point of every Chicago business license on record in each ZIP (the City's own
        points), the center a rule like "within 3 miles of 60631" measures from."""
        rows = self.c.rows(LIC, select="zip_code,avg(latitude) AS lat,avg(longitude) AS lon,count(*) AS n",
                           where="city='CHICAGO' AND latitude IS NOT NULL AND zip_code IS NOT NULL", group="zip_code", limit=5000)
        out = {}
        for r in rows:
            z = (r.get("zip_code") or "")[:5]
            try:
                if re.fullmatch(r"606\d\d|608\d\d", z) and int(r["n"]) >= 25:
                    out[z] = [round(float(r["lat"]), 5), round(float(r["lon"]), 5), int(r["n"])]
            except (KeyError, TypeError, ValueError):
                continue
        return out

    def food_licenses_at(self, keys_numbers):
        """Current food licenses at these street numbers (a permit-only row at a site that already holds one is a remodel,
        not a business on its way to opening)."""
        out = []
        nums = sorted({n for n in keys_numbers if n.isdigit()}, key=int)
        for i in range(0, len(nums), 80):
            where = " OR ".join(f"starts_with(address, '{n} ')" for n in nums[i:i + 80])
            out += self.c.pull(LIC, select="id,address,license_description,license_status,expiration_date,date_issued",
                               where=f"({where}) AND license_status='AAI'", order="id", key="id")
        return out


def licensed_food(today, licenses_rows, areas, checks_fn):
    """The license layer: tools/licenses_chicago.py's own build and checks over the radar window, food rows only."""
    left = []
    recs, reasons = lc.build(licenses_rows, areas, today, days=WINDOW, left=left)
    for r in recs:
        r["lics"] = r["_lics"]                 # the same list object; strip_internal drops only the private name
        r["acct_addr"] = r["_addr"]
    old = lc.WINDOW_DAYS
    lc.WINDOW_DAYS = WINDOW                    # run_checks reads the window to date "earlier licenses"; ours is 180 days
    try:
        recs, checks = checks_fn(recs, reasons, left)
    finally:
        lc.WINDOW_DAYS = old
    food = [r for r in recs if r["segment"] == "food"]
    return food, reasons, left, checks


def build(today, lic_recs, left, insp_rows, pending_rows, pending_license_rows, permits, food_permit_rows, site_food_licenses,
          rest_dnl=None, lic_dnl=None):
    """The joined businesses and the counts. Every argument is already fetched, so the selftest drives this with planted rows."""
    since = (today - dt.timedelta(days=WINDOW)).isoformat()
    rest_dnl = rl.dnl_load() if rest_dnl is None else rest_dnl
    reasons = collections.Counter()
    left_lics = {l for l, _ in left}
    insp_by_lic = collections.defaultdict(list)
    for x in insp_rows + pending_rows:
        n = lic_num(x.get("license_"))
        if n and all(x.get("inspection_id") != y.get("inspection_id") for y in insp_by_lic[n]):
            insp_by_lic[n].append(x)
    biz = []
    # 1. licensed food businesses
    for r in lic_recs:
        b = {"id": "L" + r["license"], "name": r["business"], "address": r["address"], "zip": r["zip"], "area": r["communityArea"],
             "lat": r["lat"], "lon": r["lon"], "licenseType": r["licenseType"], "otherTypes": r.get("otherTypes") or [], "activity": r["activity"],
             "history": r.get("history") or "", "lics": list(r["lics"]), "key": building(r.get("acct_addr") or r["address"]), "events": []}
        b["events"].append({"t": "license", "d": r["issued"], "id": r["license"], "type": r["licenseType"], "link": RECORD["license"] + r["license"]})
        start = (dt.date.fromisoformat(r["issued"]) - dt.timedelta(days=PRE_LICENSE)).isoformat()
        rows = [x for n in b["lics"] for x in insp_by_lic.get(n, [])]
        if rl.place_dnl_keys(rows) & rest_dnl:
            reasons["on the restaurant do-not-list"] += 1
            continue
        for x in rows:
            e = insp_event(x)
            if e["d"] >= start and not (e["t"] == "routine" and e["d"] < r["issued"]):
                b["events"].append(e)
            b.setdefault("ftype", x.get("facility_type") or "")
        if any((e.get("result") or "").upper() == "OUT OF BUSINESS" for e in b["events"]):
            reasons["the City recorded it out of business"] += 1
            continue
        biz.append(b)
    have = {n for r in lic_recs for n in r["lics"]}        # every new food license, kept or not, is never "not issued yet"
    # 2. inspected, license not issued yet: a pre-opening inspection under a license number the City has not issued
    issued_ever = collections.defaultdict(list)
    for x in pending_license_rows:
        issued_ever[lic_num(x.get("license_number"))].append(x)
    by_lic = collections.defaultdict(list)
    for x in pending_rows:
        n = lic_num(x.get("license_"))
        if n and n not in have:
            by_lic[n].append(x)
    pend_from = (today - dt.timedelta(days=PENDING)).isoformat()
    for n, rows in by_lic.items():
        rows.sort(key=lambda x: x.get("inspection_date") or "")
        last = rows[-1]
        why = ""
        if n in left_lics:
            why = "left out by the license rules (person-like name, home, event or person-held license)"
        elif any(day(x.get("date_issued")) for x in issued_ever.get(n, [])):
            why = "license already issued (before the window, a renewal, or not a food license)"
        elif day(last.get("inspection_date")) < pend_from:
            why = f"inspected more than {PENDING} days ago with no license since"
        elif any(rl.institution(x) for x in rows):
            why = "school, care or health site"
        elif any(rl.person_name(x.get("dba_name")) or lc.could_be_person(x.get("dba_name")) for x in rows):
            why = "name could be a person's"
        elif re.search(r"MOBILE|PEDDLER|TRUCK|CART", (last.get("facility_type") or "").upper()):
            why = "mobile food, no fixed site"
        elif not (last.get("address") or "").strip() or lc.HOME_ADDRESS.search(last.get("address") or ""):
            why = "no business site address"
        elif rl.place_dnl_keys(rows) & rest_dnl:
            why = "on the restaurant do-not-list"
        elif any((x.get("results") or "").upper() == "OUT OF BUSINESS" for x in rows):
            why = "the City recorded it out of business"
        if why:
            reasons[why] += 1
            continue
        b = {"id": "I" + n, "name": rl.biz_case(last.get("dba_name") or ""), "address": lc.street(last.get("address") or ""), "zip": (last.get("zip") or "")[:5],
             "area": last.get("_area") or "", "lat": rl._f(last.get("latitude")), "lon": rl._f(last.get("longitude")), "licenseType": "",
             "otherTypes": [], "activity": "", "history": "", "lics": [n], "key": building(last.get("address")), "ftype": last.get("facility_type") or "",
             "events": [insp_event(x) for x in rows]}
        biz.append(b)
    # 3. a building permit at the address, before or after the other records
    by_key = collections.defaultdict(list)
    for p in permits:
        if BUILD_TYPES.search(p.get("permit_type") or ""):
            by_key[permit_key(p)].append(p)
    shared = collections.Counter(b["key"] for b in biz)
    for b in biz:
        first = min(e["d"] for e in b["events"])
        lo = (dt.date.fromisoformat(first) - dt.timedelta(days=PERMIT_BACK)).isoformat()
        for p in sorted(by_key.get(b["key"], []), key=lambda p: p.get("issue_date") or ""):
            d = day(p.get("issue_date"))
            if not (lo <= d <= today.isoformat()):
                continue
            food = permit_is_food(p, b["name"])
            if shared[b["key"]] > 1 and not food:
                continue                       # two food businesses in one building: only a permit that names food work links
            b["events"].append(permit_event(p, food))
        b["shared"] = shared[b["key"]] > 1
    # 4. permit only: a food build-out permit at a site with no current food license, no license inspection, nothing else
    known = {b["key"] for b in biz}
    current = collections.defaultdict(list)
    for x in site_food_licenses:
        if lc.FOOD_LICENSE.search(x.get("license_description") or "") or re.search(r"RETAIL FOOD", x.get("license_description") or "", re.I):
            current[building(x.get("address"))].append(x)
    seen_keys = set()
    for p in sorted(food_permit_rows, key=lambda p: p.get("issue_date") or "", reverse=True):
        d, k = day(p.get("issue_date")), permit_key(p)
        desc = NOT_FOOD.sub(" ", (p.get("work_description") or "").upper())
        if d < since or not k or not BUILD_TYPES.search(p.get("permit_type") or "") or not FOOD_WORDS.search(desc):
            continue
        if k in known or k in seen_keys:
            continue
        why = ""
        if RESIDENTIAL_SMALL.search(desc) or re.search(r"\b(?:CONDO|APARTMENT|DWELLING UNIT|RESIDENCE)\b", desc) and not re.search(r"RESTAURANT|CAFE|COFFEE|BAKERY|TAVERN", desc):
            why = "a home's kitchen, not a food business"
        elif any(not x.get("expiration_date") or day(x.get("expiration_date")) >= d for x in current.get(k, [])):
            why = "a current food license already at the site (a remodel, not a new business)"
        if why:
            reasons[why] += 1
            seen_keys.add(k)
            continue
        seen_keys.add(k)
        street = lc.street(" ".join(x for x in (p.get("street_number"), p.get("street_direction"), p.get("street_name")) if x))
        evs = [permit_event(x, True) for x in by_key.get(k, []) + [p] if day(x.get("issue_date")) >= since
               and FOOD_WORDS.search(NOT_FOOD.sub(" ", (x.get("work_description") or "").upper()))]
        evs = list({e["id"]: e for e in evs}.values())
        biz.append({"id": "P" + str(p.get("permit_")), "name": "", "address": street, "zip": "", "area": p.get("_area") or "",
                    "lat": rl._f(p.get("latitude")), "lon": rl._f(p.get("longitude")), "licenseType": "", "otherTypes": [], "activity": "",
                    "history": "", "lics": [], "key": k, "shared": False, "ftype": "", "events": evs})
    # stage, kind, order
    for b in biz:
        b["events"].sort(key=lambda e: (e["d"], ["permit", "linsp", "license", "routine"].index(e["t"])))
        b["stage"], b["stageDate"], b["openBy"] = stage_of(b, today)
        scopes = " ".join(e.get("scope", "") for e in b["events"] if e["t"] == "permit" and e.get("food"))
        b["kind"] = food_kind(b["activity"], " ".join([b["licenseType"]] + b["otherTypes"]), b.get("ftype"), scopes)
        b["first"] = b["events"][0]["d"]
        b["last"] = max(e["d"] for e in b["events"])
    biz = [b for b in biz if b["last"] >= since]
    biz.sort(key=lambda b: (b["last"], b["id"]), reverse=True)
    return biz, reasons


def match_counts(biz, reasons, extra):
    """Counts only (public): how the join landed. No names, no addresses."""
    lic = [b for b in biz if b["id"].startswith("L")]
    has = lambda b, t: any(e["t"] == t for e in b["events"])
    gaps = collections.defaultdict(list)
    order = collections.Counter()
    for b in lic:
        issued = min(e["d"] for e in b["events"] if e["t"] == "license")
        li = sorted(e["d"] for e in b["events"] if e["t"] == "linsp")
        pm = sorted(e["d"] for e in b["events"] if e["t"] == "permit" and e["d"] <= issued)
        rt = sorted(e["d"] for e in b["events"] if e["t"] == "routine" and e["d"] >= issued)
        D = lambda a, z: (dt.date.fromisoformat(z) - dt.date.fromisoformat(a)).days
        if li:
            order["inspection on or before the license" if li[0] <= issued else "inspection after the license"] += 1
            gaps["first license inspection to license"].append(D(li[0], issued))
        if pm and li:
            gaps["permit to first license inspection"].append(D(pm[-1], li[0]))
        if rt:
            gaps["license to first routine inspection"].append(D(issued, rt[0]))
    med = {k: {"median": statistics.median(v), "n": len(v)} for k, v in gaps.items() if v}
    pct = lambda a, n: round(100.0 * a / n, 1) if n else 0.0
    n = len(lic)
    li_n = sum(has(b, "linsp") for b in lic)
    pf = sum(any(e["t"] == "permit" and e["food"] for e in b["events"]) for b in lic)
    pa = sum(has(b, "permit") for b in lic)
    rt = sum(has(b, "routine") for b in lic)
    pend = [b for b in biz if b["id"].startswith("I")]
    ponly = [b for b in biz if b["id"].startswith("P")]
    return {"licensedFood": n,
            "licenseToInspection": {"matched": li_n, "pct": pct(li_n, n), "key": "license number (the inspection's license_ field)"},
            "licenseToPermit": {"matched": pa, "pct": pct(pa, n), "foodWorded": pf, "foodWordedPct": pct(pf, n),
                                "key": "address (house number, direction, street, suffix; no unit)", "lookback": f"{PERMIT_BACK} days before the first record"},
            "licenseToRoutine": {"matched": rt, "pct": pct(rt, n)},
            "allThree": {"matched": sum(has(b, "linsp") and has(b, "permit") for b in lic), "pct": pct(sum(has(b, "linsp") and has(b, "permit") for b in lic), n)},
            "inspectedNoLicense": {"n": len(pend), "withPermit": sum(has(b, "permit") for b in pend)},
            "permitOnly": len(ponly), "sharedBuildings": sum(bool(b.get("shared")) for b in biz),
            "order": dict(order), "daysBetween": med, "byStage": dict(collections.Counter(b["stage"] for b in biz)),
            "openBy": dict(collections.Counter(b["openBy"] for b in biz if b["stage"] == "open")),
            "byKind": dict(collections.Counter(b["kind"] for b in biz)), "leftOut": dict(reasons), **extra}


def holdout_pick(biz, n=5, seed=None):
    """n businesses at random, at least one from each kind of row present (licensed, inspected only, permit only)."""
    rng = random.Random(seed)
    groups = [[b for b in biz if b["id"][0] == c] for c in "LIP"]
    pick = [rng.choice(g) for g in groups if g]
    rest = [b for b in biz if b not in pick]
    rng.shuffle(rest)
    return (pick + rest)[:n]


def holdout_rows(client, picks):
    """The City's own rows for each pick, by separate plain queries that do not use the join code: the license by number,
    every food inspection under the license number and at the house number and street, every permit at the house number
    on that street (business-level columns only). A person compares them with the app's timeline by hand."""
    out = []
    for b in picks:
        w = b["address"].upper().split()
        num = w[0] if w else ""
        dirn = w[1] if len(w) > 2 and w[1] in ("N", "S", "E", "W") else ""
        main = ((w[2] if dirn else w[1]) if len(w) > 1 else "").replace("'", "''")
        def q(ds, sel, where):
            try:
                return client.rows(ds, select=sel, where=where, limit=200, order=":id")
            except Exception as e:          # a failed hand-check query is recorded, never fatal to the list
                return [{"_queryFailed": str(e)[-160:], "_where": where}]
        lics = [l for l in b["lics"] if l.isdigit()]
        since = (dt.date.fromisoformat(b["first"]) - dt.timedelta(days=PERMIT_BACK)).isoformat()
        out.append({"id": b["id"], "shown": {k: b.get(k) for k in ("name", "address", "area", "kind", "stage", "stageDate", "openBy", "licenseType")},
                    "events": b["events"],
                    "cityLicenses": q(LIC, "license_number,doing_business_as_name,address,license_description,application_type,date_issued,license_status",
                                      f"license_number in({','.join(lics)})") if lics else [],
                    "cityInspectionsByLicense": q(FOOD, City.INSP_COLS, f"license_ in({','.join(lics)})") if lics else [],
                    "cityInspectionsByAddress": q(FOOD, City.INSP_COLS, f"starts_with(address, '{num} {dirn + ' ' if dirn else ''}{main}')") if num and main else [],
                    "cityPermitsAtAddress": q(PERMITS, City.PERMIT_COLS, f"street_number='{num}' AND street_name like '%{main}%' AND issue_date >= '{since}'") if num and main else []})
    return out


def run(a):
    from socrata import Socrata
    now = lc.chicago_now()
    today = now.date()
    since = (today - dt.timedelta(days=WINDOW)).isoformat()
    chi = Socrata(PORTAL)
    city = City(chi)
    meta = {k: chi._get(f"/api/views/{d}.json").get("rowsUpdatedAt") for k, d in (("licenses", LIC), ("inspections", FOOD), ("permits", PERMITS))}
    upd = {k: dt.datetime.fromtimestamp(v, dt.timezone.utc).isoformat(timespec="seconds") if v else "" for k, v in meta.items()}
    areas = lc.load_areas()
    rows = lc.pull((today - dt.timedelta(days=WINDOW + 7)).isoformat())
    checks_fn = lambda recs, reasons, left: lc.run_checks(recs, reasons, today, lc.fetch_history, lc.fetch_food, lc.fetch_buildings, lc.fetch_by_building, left=left)
    lic_recs, lic_reasons, left, checks = licensed_food(today, rows, areas, checks_fn)
    insp = city.inspections_for({n for r in lic_recs for n in r["lics"]}, (today - dt.timedelta(days=WINDOW + PRE_LICENSE)).isoformat())
    pend = city.license_inspections(since)
    for x in insp + pend:
        x["_area"] = lc.area_of(x.get("latitude"), x.get("longitude"), areas)
    have = {n for r in lic_recs for n in r["lics"]}
    cand = {lic_num(x.get("license_")) for x in pend} - have - {""}
    pend_lic_rows = city.license_rows(cand)
    keys_numbers = {building(r.get("acct_addr") or r["address"]).split(" ")[0] for r in lic_recs} | {building(x.get("address")).split(" ")[0] for x in pend}
    permits = city.permits_at(keys_numbers, (today - dt.timedelta(days=WINDOW + PRE_LICENSE + PERMIT_BACK)).isoformat())
    food_permits = city.food_permits(since)
    for p in permits + food_permits:
        p["_area"] = lc.area_of(p.get("latitude"), p.get("longitude"), areas)
    site_lics = city.food_licenses_at({permit_key(p).split(" ")[0] for p in food_permits if permit_key(p)})
    biz, reasons = build(today, lic_recs, left, insp, pend, pend_lic_rows, permits, food_permits, site_lics)
    zips = city.zip_centers()
    # the permit-only rows' community area comes from the permit's own point
    source = {"names": {"licenses": "City of Chicago Data Portal, Business Licenses", "inspections": "City of Chicago Data Portal, Food Inspections",
                        "permits": "City of Chicago Data Portal, Building Permits"},
              "pages": DATASET_PAGES, "rowsUpdatedAt": upd, "fetchedAt": now.isoformat(timespec="seconds"), "terms": TERMS, "record": RECORD,
              "modified": ("Joined by ProofNotFluff: new food business licenses (application type Issue) of the last 180 days, food license "
                           "(pre-opening) inspections under the same license number, building permits at the same address, and food "
                           "build-out permits with no license yet. Business-level fields only; inspector names, inspection comments and "
                           "permit contact names are never kept.")}
    extra = {"window": {"from": since, "to": today.isoformat(), "days": WINDOW}, "licenseChecks": checks,
             "licenseLeftOut": dict(lic_reasons), "pulled": {"licenseRows": len(rows), "inspectionRows": len(insp), "licenseInspectionRows": len(pend),
                                                              "permitsAtAddresses": len(permits), "foodWordPermits": len(food_permits)}}
    m = match_counts(biz, reasons, extra)
    m["ranAt"] = now.isoformat(timespec="seconds")
    m["rowsUpdatedAt"] = upd
    if a.match:
        os.makedirs(os.path.dirname(a.match) or ".", exist_ok=True)
        json.dump(m, open(a.match, "w"), indent=1)
    for b in biz:
        b.pop("key", None)
        b.pop("ftype", None)
    if a.full:
        json.dump({"source": source, "asOf": today.isoformat(), "window": extra["window"], "match": m, "zips": zips, "businesses": biz}, open(a.full, "w"), indent=1)
    print(json.dumps({k: m[k] for k in ("licensedFood", "licenseToInspection", "licenseToPermit", "inspectedNoLicense", "permitOnly", "byStage", "order")}))
    if a.holdout:
        picks = holdout_pick(biz, 5, seed=os.environ.get("GITHUB_RUN_ID") or now.isoformat())
        json.dump({"pickedAt": now.isoformat(timespec="seconds"), "picks": holdout_rows(chi, picks)}, open(a.holdout, "w"), indent=1)


# ---------------------------------------------------------------- planted cases (invented businesses, real City field names)
def selftest():
    today = dt.date(2026, 11, 2)
    assert building("3509 S DR MARTIN LUTHER KING JR DR 2") == "3509 S DR MARTIN LUTHER KING JR DR"
    assert building("1234-40 W MADISON ST STE 2") == "1234 W MADISON ST" == permit_key({"street_number": "1234", "street_direction": "W", "street_name": "MADISON ST"})
    assert building("230 W MONROE ST 1ST") == "230 W MONROE ST"
    for t, want in [(("Preparation of Food and Dining on Premises With Seating", "Retail Food Establishment"), "restaurant"),
                    (("Preparation and Sale of Coffee and/or Drinks", "Retail Food Establishment", "Restaurant"), "coffee"),
                    (("Retail Sales of Packaged Liquor", "Package Goods"), "liquor"), (("", "Tavern"), "bar"),
                    (("Retail Sales of Perishable Foods", "Retail Food Establishment"), "grocery"), (("", "", "Bakery"), "bakery"),
                    (("", "Shared Kitchen User (Long Term)"), "catering"), (("", "Retail Food Establishment"), "other")]:
        assert food_kind(*t) == want, (t, food_kind(*t))
    assert permit_is_food({"work_description": "INTERIOR ALTERATION FOR NEW RESTAURANT WITH TYPE I HOOD"})
    assert not permit_is_food({"work_description": "INSTALL GRAB BARS IN BATHROOM"})
    assert permit_is_food({"work_description": "BUILD OUT FOR LUNA TACOS"}, "Luna Tacos")
    assert not permit_is_food({"work_description": "REPLACE ROOF"}, "Luna Tacos")
    lic = lambda n, name, addr, issued, **k: {"license": n, "business": name, "address": lc.street(addr), "zip": "60622", "communityArea": "West Town",
                                               "lat": 41.9, "lon": -87.67, "licenseType": k.get("lt", "Retail Food Establishment"), "otherTypes": [],
                                               "activity": k.get("act", "Preparation of Food and Dining on Premises With Seating"), "issued": issued,
                                               "history": "first", "lics": [n], "acct_addr": addr}
    ins = lambda i, n, d, t, res, addr="1000 W CHICAGO AVE", name="LUNA TACOS", ft="Restaurant": {
        "inspection_id": i, "license_": n, "inspection_date": d + "T00:00:00.000", "inspection_type": t, "results": res, "address": addr,
        "dba_name": name, "facility_type": ft, "zip": "60622", "latitude": "41.9", "longitude": "-87.67", "_area": "West Town"}
    per = lambda pid, d, desc, num="1000", name="CHICAGO AVE", typ="PERMIT - RENOVATION/ALTERATION", dr="W": {
        "id": "p" + pid, "permit_": pid, "permit_type": typ, "issue_date": d + "T00:00:00.000", "street_number": num, "street_direction": dr,
        "street_name": name, "work_description": desc, "latitude": "41.9", "longitude": "-87.67", "_area": "West Town"}
    lic_recs = [lic("101", "Luna Tacos", "1000 W CHICAGO AVE", "2026-09-10"),                         # permit, inspection, license, open by canvass
                lic("102", "Sol Cafe", "2000 W DIVISION ST 1ST", "2026-10-20",
                    act="Preparation and Sale of Coffee and/or Drinks"),                                  # licensed, no inspection on file
                lic("103", "Old Bakery", "3000 N CLARK ST", "2026-08-01", act="Bakery"),                  # 30-day rule
                lic("104", "Two Doors A", "4000 N BROADWAY", "2026-10-01"), lic("105", "Two Doors B", "4000 N BROADWAY", "2026-10-02"),
                lic("106", "Gone Grill", "5000 S HALSTED ST", "2026-09-01")]
    insp = [ins("1", "101", "2026-09-01", "License", "Fail"), ins("2", "101", "2026-09-08", "License Re-Inspection", "Pass"),
            ins("3", "101", "2026-10-15", "Canvass", "Pass"), ins("4", "101", "2026-08-01", "Canvass", "Pass"),   # a canvass before the license is not routine-after
            ins("5", "103", "2026-07-25", "License", "Pass", addr="3000 N CLARK ST", name="OLD BAKERY"),
            ins("6", "106", "2026-09-20", "Canvass", "Out of Business", addr="5000 S HALSTED ST", name="GONE GRILL")]
    pend = [ins("20", "201", "2026-10-25", "License", "Pass", addr="6000 N SHERIDAN RD", name="NEW NOODLE BAR"),     # pending: kept
            ins("21", "202", "2026-10-25", "License", "Pass", addr="6100 N SHERIDAN RD", name="MARIA GARCIA"),       # person: out
            ins("22", "203", "2026-10-25", "License", "Pass", addr="6200 N SHERIDAN RD", name="BRIGHT KIDS ACADEMY", ft="Children's Services Facility"),
            ins("23", "204", "2026-10-25", "License", "Pass", addr="6300 N SHERIDAN RD", name="OLDER SPOT"),         # issued long ago: out
            ins("24", "205", "2026-05-01", "License", "Pass", addr="6400 N SHERIDAN RD", name="STALE SPOT"),         # stale: out
            ins("2", "101", "2026-09-08", "License Re-Inspection", "Pass")]                                          # already licensed (same row)
    pend_lic = [{"license_number": "204", "application_type": "ISSUE", "date_issued": "2019-01-01T00:00:00"}]
    permits = [per("9001", "2026-05-01", "INTERIOR BUILD OUT FOR NEW RESTAURANT, TYPE I HOOD"),
               per("9002", "2026-06-01", "REPLACE ROOF", typ="PERMIT - EASY PERMIT PROCESS"),
               per("9003", "2026-06-01", "ELECTRIC SERVICE", typ="PERMIT - ELECTRIC WIRING"),                          # not a build type
               per("9004", "2026-05-01", "REMODEL COMMON CORRIDOR", num="4000", name="BROADWAY", dr="N"),                     # shared building, not food: out
               per("9005", "2026-05-02", "BUILD OUT FOR TWO DOORS A CAFE", num="4000", name="BROADWAY", dr="N"),
               per("9006", "2026-09-01", "ALTERATIONS FOR RESTAURANT", num="6000", name="SHERIDAN RD", dr="N", typ="PERMIT - RENOVATION/ALTERATION"),
               per("9007", "2023-01-01", "OLD WORK", num="1000")]                                                     # too early
    food_permits = [per("9101", "2026-10-01", "INTERIOR ALTERATION FOR NEW BAKERY AND CAFE", num="7000", name="ASHLAND AVE"),   # permit only: kept
                    per("9102", "2026-10-01", "NEW KITCHEN HOOD IN SINGLE FAMILY RESIDENCE", num="7100", name="ASHLAND AVE"),
                    per("9103", "2026-10-02", "NEW RESTAURANT BUILD OUT", num="7200", name="ASHLAND AVE"),                  # current license there: remodel
                    per("9104", "2026-10-03", "RESTAURANT BUILD OUT", num="1000", name="CHICAGO AVE"),                      # site already on radar
                    per("9105", "2026-10-04", "INSTALL GRAB BARS", num="7300", name="ASHLAND AVE")]
    site = [{"address": "7200 W ASHLAND AVE", "license_description": "Retail Food Establishment", "expiration_date": "2027-05-15T00:00:00"}]
    biz, reasons = build(today, lic_recs, [], insp, pend, pend_lic, permits, food_permits, site, rest_dnl=set())
    by = {b["id"]: b for b in biz}
    assert set(by) == {"L101", "L102", "L103", "L104", "L105", "I201", "P9101"}, sorted(by)
    L = by["L101"]
    assert [e["t"] for e in L["events"]] == ["permit", "permit", "linsp", "linsp", "license", "routine"], [e["t"] for e in L["events"]]
    assert L["stage"] == "open" and L["stageDate"] == "2026-10-15" and L["openBy"] == "routine"
    assert all(e["link"].startswith(PORTAL) for e in L["events"]) and L["events"][0]["food"] and not L["events"][1]["food"]
    assert by["L102"]["stage"] == "licensed" and by["L102"]["kind"] == "coffee" and [e["t"] for e in by["L102"]["events"]] == ["license"]
    assert by["L103"]["stage"] == "open" and by["L103"]["openBy"] == "rule" and by["L103"]["stageDate"] == "2026-08-31" and by["L103"]["kind"] == "bakery"
    assert [e["id"] for e in by["L104"]["events"] if e["t"] == "permit"] == ["9005"] and by["L104"]["shared"]
    assert by["I201"]["stage"] == "inspected" and by["I201"]["name"] == "New Noodle Bar" and [e["id"] for e in by["I201"]["events"] if e["t"] == "permit"] == ["9006"]
    assert by["P9101"]["stage"] == "permitted" and by["P9101"]["name"] == "" and by["P9101"]["kind"] == "bakery"
    assert reasons["the City recorded it out of business"] == 1 and reasons["name could be a person's"] == 1 and reasons["school, care or health site"] == 1
    assert reasons["license already issued (before the window, a renewal, or not a food license)"] == 1 and reasons[f"inspected more than {PENDING} days ago with no license since"] == 1
    assert reasons["a home's kitchen, not a food business"] == 1 and reasons["a current food license already at the site (a remodel, not a new business)"] == 1
    assert biz[0]["last"] >= biz[-1]["last"]
    m = match_counts(biz, reasons, {})
    assert m["licensedFood"] == 5 and m["licenseToInspection"]["matched"] == 2 and m["licenseToPermit"]["matched"] == 3
    assert m["order"] == {"inspection on or before the license": 2} and m["inspectedNoLicense"] == {"n": 1, "withPermit": 1}
    txt = json.dumps(m)
    assert "Luna" not in txt and "CHICAGO AVE" not in txt.upper(), "match counts carry no names or addresses"
    assert "violations" not in City.INSP_COLS and "contact" not in City.PERMIT_COLS and "inspector" not in City.INSP_COLS
    dnl = rl.place_dnl_keys([ins("1", "101", "2026-09-01", "License", "Fail")])
    biz2, r2 = build(today, lic_recs, [], insp, pend, pend_lic, permits, food_permits, site, rest_dnl=dnl)
    assert not {"L101", "I101"} & {b["id"] for b in biz2} and r2["on the restaurant do-not-list"] >= 1
    p = holdout_pick(biz, 5, seed=1)
    assert len(p) == 5 and {b["id"][0] for b in p} == {"L", "I", "P"}
    print("radar_chicago selftest ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--full", default="")
    ap.add_argument("--match", default="")
    ap.add_argument("--holdout", default="")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    run(a)


if __name__ == "__main__":
    main()
