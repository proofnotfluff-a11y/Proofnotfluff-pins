#!/usr/bin/env python3
"""Chicago City Contracts by Trade: the data layer for the free daily page /chicago-city-contracts/ (site/pages.json
kind "datapage", module tools/dp_contracts.py). Todd's go, Oct 27, 2026, 12:17 pm ("Let's do them all",
coo/PARALLEL_BUILDS.md, research_notes/kimi-2026-10-27-r10.md item 3).

Runs in GitHub Actions (.github/workflows/dp_contracts.yml), because the cloud agents cannot reach
data.cityofchicago.org. Source: City of Chicago Data Portal, Contracts (dataset rsxa-ify5): contracts and
modifications the City has awarded since 1993, updated daily. These are awards, not open bids.

What it keeps: for each trade in TRADES (a published keyword map on the description), the awards and modifications
approved in the last 36 months, and the contracts whose end date falls in the next 12 months, with the description,
department, vendor (a business name), amount, contract and procurement type, specification and contract numbers, dates
and the City's contract PDF link. The vendor's address, city, state and ZIP are never requested. A vendor name that
does not read as a business is replaced with "Name withheld" (a sole trader can file under their own name).

Rules the page relies on (all from the dataset's own description):
- revision_number 0 is the original award; any higher number is a modification. They are counted apart.
- a negative award_amount is a modification that took money out; it is never mixed into award totals.
- an award of $0 on a blanket contract "depends upon requirements": the City orders as needed, no amount is promised.
- only blanket contracts carry an FMPS end date; a standard contract (most construction) ends on completion.

Usage: python3 tools/dp_contracts_data.py            pull and write site/datapages/dp_contracts/contracts.json
       python3 tools/dp_contracts_data.py --selftest  planted rows, no network
"""
import argparse, datetime as dt, json, os, re, statistics, sys, time, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "site", "datapages", "dp_contracts")
PORTAL = "https://data.cityofchicago.org"
DATASET = "rsxa-ify5"
DATASET_PAGE = f"{PORTAL}/Administration-Finance/Contracts/{DATASET}"
UA = {"User-Agent": "ProofNotFluff data page (github.com/proofnotfluff-a11y/proofnotfluff-pins)"}
CHI = ZoneInfo("America/Chicago")
FIELDS = ["purchase_order_description", "purchase_order_contract_number", "revision_number", "specification_number",
          "contract_type", "start_date", "end_date", "approval_date", "department", "vendor_name", "award_amount",
          "procurement_type", "contract_pdf"]   # never address_1, address_2, city, state or zip

# The trade map, published on the page word for word (site shows each trade's words). Matching is on the contract
# description, in capitals, whole words where it matters. "out" words drop a match that is about something else.
TRADES = [
    {"key": "janitorial", "name": "Janitorial and cleaning", "short": "Janitorial",
     "words": ["janitor", "janitorial", "custodial", "cleaning services", "building cleaning", "cleaning of buildings, facilities or offices", "window washing", "window cleaning"],
     "re": r"\bJANITOR|\bCUSTODIAL|\bCLEANING SERV|\bBUILDING CLEANING|\bWINDOW (?:WASHING|CLEANING)|\bCLEANING OF (?:CITY )?(?:BUILDINGS?|FACILIT|OFFICES?)",
     "out": r"SEWER|CATCH BASIN|STREET CLEANING|STREET SWEEP|DUCT CLEANING|TANK CLEANING|LAGOON"},
    {"key": "pest-control", "name": "Pest control", "short": "Pest control",
     "words": ["pest", "pests", "exterminating", "rodent", "termite", "bed bug", "mosquito", "bird control", "vector control"],
     "re": r"\bPEST\b|\bPESTS\b|EXTERMINAT|\bRODENT|\bTERMITE|\bBED ?BUG|\bMOSQUITO|\bBIRD CONTROL|\bVECTOR CONTROL",
     "out": r"PESTICIDE SUPPL"},
    {"key": "landscaping", "name": "Landscaping and tree work", "short": "Landscaping",
     "words": ["landscape", "landscaping", "tree", "trees", "mow", "mowing", "turf", "forestry", "stump", "prune", "pruning", "lawn care", "lawn mowing", "lawn maintenance", "lawn service", "weed"],
     "re": r"\bLANDSCAP|\bTREES?\b|\bMOWING|\bMOW\b|\bTURF\b|\bFORESTRY|\bSTUMP|\bPRUN(?:E|ING)|\bLAWN (?:CARE|MOWING|MAINT|SERV)|\bWEED",
     "out": r"TREE OF LIFE|INVENTORY|TRAILERS?\b|HOLIDAY TREE|TREES STUDIO"},
    {"key": "snow-removal", "name": "Snow removal", "short": "Snow removal",
     "words": ["snow", "plow", "plowing", "ice control", "de-icing", "ice and snow"],
     "re": r"\bSNOW|\bPLOW|\bICE CONTROL|\bDE-?ICING|\bICE (?:AND|&) SNOW",
     "out": r"\bROCK SALT\b|SODIUM CHLORIDE|DE-?ICING FLUID|GLYCOL|AIRCRAFT DE-?ICING|DEICING FACILITY|BLOWERS?\b|SNOW EQUIPMENT|CHASSIS"},
    {"key": "roofing", "name": "Roofing", "short": "Roofing",
     "words": ["roof", "roofing"],
     "re": r"\bROOF",
     "out": ""},
    {"key": "painting", "name": "Painting", "short": "Painting",
     "words": ["paint", "painted", "painting", "repaint", "repainting", "protective coating", "coating services"],
     "re": r"\bPAINT(?:ING|ED)?\b|\bREPAINT|\bPROTECTIVE COATING|\bCOATING SERV",
     "out": r"PAVEMENT MARKING|TRAFFIC PAINT|LEAD[- ]BASED PAINT|\bMURAL|SPRAYERS?\b|ARTWORK|\bART\b|PAINTINGS\b"},
    {"key": "hvac", "name": "HVAC", "short": "HVAC",
     "words": ["HVAC", "heating", "air conditioning", "boiler", "chiller", "cooling tower", "ventilation", "refrigeration", "furnace"],
     "re": r"\bHVAC|\bHEATING|\bAIR CONDITION|\bBOILER|\bCHILLER|\bCOOLING TOWER|\bVENTILAT|\bREFRIGERAT|\bFURNACE|\bH\.V\.A\.C",
     "out": r"HEATING OIL|\bFUEL OIL|NATURAL GAS SUPPLY|ELEVATOR"},
    {"key": "electrical", "name": "Electrical", "short": "Electrical",
     "words": ["electrical", "electrician", "wiring", "street light", "streetlight", "lighting maintenance, installation, repair, retrofit or upgrade", "traffic signal", "electric work, service, repair or maintenance"],
     "re": r"\bELECTRICAL|\bELECTRICIAN|\bWIRING\b|\bSTREET ?LIGHT|\bLIGHTING (?:MAINT|INSTALL|REPAIR|RETROFIT|UPGRADE)|\bTRAFFIC SIGNAL|\bELECTRIC(?:AL)? (?:WORK|SERV|REPAIR|MAINT)",
     "out": r"ELECTRICITY SUPPLY|\bUTILIT(?:Y|IES)-ELECTRIC|ELECTRIC VEHICLE|ELECTRIC BUS|\bPOLES\b|\bBODY\b"},
    {"key": "plumbing", "name": "Plumbing", "short": "Plumbing",
     "words": ["plumbing", "plumber", "backflow", "water heater", "drain cleaning, repair or service", "sewer repair, rodding or cleaning service"],
     "re": r"\bPLUMB|\bBACKFLOW|\bWATER HEATER|\bDRAIN (?:CLEAN|REPAIR|SERV)|\bSEWER (?:REPAIR|RODDING|CLEANING) SERV",
     "out": ""},
    {"key": "demolition", "name": "Demolition", "short": "Demolition",
     "words": ["demolition", "wrecking"],
     "re": r"\bDEMOLI|\bWRECKING",
     "out": r"REPROCESSABLE"},
    {"key": "hauling", "name": "Hauling and junk removal", "short": "Hauling",
     "words": ["haul", "hauling", "junk", "debris removal", "debris hauling", "refuse", "dumpster", "roll-off", "waste removal, hauling or disposal", "board-up", "clean and seal"],
     "re": r"\bHAUL|\bJUNK\b|\bDEBRIS (?:REMOVAL|HAUL)|\bREFUSE\b|\bDUMPSTER|\bROLL[- ]?OFF|\bWASTE (?:REMOVAL|HAULING|DISPOSAL)|\bBOARD[- ]?UP|\bCLEAN (?:AND|&) SEAL",
     "out": r"HAULER LICENSE|REFUSE TRUCK|REFUSE BODY|REFUSE CART"},
    {"key": "pressure-washing", "name": "Pressure washing and graffiti", "short": "Pressure washing",
     "words": ["graffiti", "pressure washing", "power washing", "sandblasting"],
     "re": r"\bGRAFFITI|\bPRESSURE WASH|\bPOWER WASH|\bSANDBLAST|\bSAND BLAST",
     "out": r"CHEMICALS?\b|PRESSURE WASHERS\b|STEAM CLEANERS?\b"},
]
# A purchase of goods for a trade is not trade work: "JANITORIAL SUPPLIES" is left out unless the description also
# names work (service, repair, maintenance, installation, removal, labor).
SUPPLY = re.compile(r"\bSUPPL(?:Y|IES)\b|\bPARTS\b|\bMATERIALS?\b|\bPRODUCTS\b|\bCHEMICALS?\b|\bEQUIPMENT\b|\bVEHICLES?\b|\bTRUCKS?\b|\bSPREADERS?\b")
WORK = re.compile(r"SERVIC|REPAIR|MAINT|INSTALL|REMOV|LABOR|\bWORK\b|CLEANING|ABATEMENT|CONTROL\b|REPLACE|REHAB|CONSTRUCT|RENOVAT")
# Not trade work in any trade: buying goods or equipment, upkeep of the City's own machines, design and engineering,
# software, art, grants and redevelopment deals, deals with other public bodies (Board of Education, intergovernmental
# agreements) and airline-run terminal projects at O'Hare.
NOT_WORK = re.compile(r"\bPURCHASE OF\b|\bPURCHASE AND DELIVERY\b|^PURCHASE\b|PARTS AND (?:REPAIR )?SERVICES?\b|\bFLEET\b|"
                      r"DESIGN ENGINEERING|ENGINEERING SERVICES|PROFESSIONAL DESIGN|CONSULTING SERVICES|\bSOFTWARE\b|"
                      r"ARTWORK|\bGRANT\b|REDEVELOPMENT|INVENTORY MANAGEMENT|\bRENTAL OF HEAVY EQUIPMENT|"
                      r"BOARD OF EDUCATION|INTERGOVERNMENTAL|CONSTRUCTION SUPERVISION|\bIGA\b|^(?:AMERICAN|UNITED|DELTA|SOUTHWEST) AIRLINES\b")
# A revision 0 row that only moves an existing contract to a new number is not a new award (the City writes
# "NOT A NEW AWARD", "TRANSFER FROM PO" or "See PO" on it): counted apart as a transfer.
TRANSFER = re.compile(r"NOT A NEW AWARD|TRANSFER(?:RED)? FROM (?:PO|P\.O)|\bXFER|REPLACING PO|SEE PO\s*#", re.I)
# Contract types that are not trade work for hire: grants to agencies, leases, revenue deals, utility supply.
NOT_TRADE_TYPES = {"DELEGATE AGENCY", "PROPERTY LEASE", "REVENUE", "UTILITIES-ELECTRICITY", "UTILITIES-NATURAL GAS"}
# A word here makes a vendor name read as a business. Only legal forms and trade nouns that are not common surnames;
# generic words that are also surnames (SNOW, POWER, STEEL, CENTER, SHOP, SALES, NATIONAL, CHICAGO ...) and a bare CO, DBA,
# "&" or AND never count alone, so "JOHN SNOW" or "AL CO" is withheld.
BUSINESS = re.compile(r"\b(?:INC|INCORPORATED|LLC|L\.L\.C|CORP|CORPORATION|COMPANY|COMPANIES|LTD|LIMITED|LP|LLP|PLLC|PC|GROUP|SERVICES?|"
                      r"ENTERPRISES?|CONSTRUCTION|CONSTRUCTORS?|CONTRACTORS?|CONTRACTING|ROOFING|ELECTRIC(?:AL)?|PLUMBING|MECHANICAL|"
                      r"INDUSTRIES|ASSOCIATES|SOLUTIONS|SYSTEMS|SUPPLY|SONS|BROS|BROTHERS|PAINTING|LANDSCAP\w*|HAULING|"
                      r"DEMOLITION|WRECKING|ENVIRONMENTAL|TECHNOLOGIES|TECHNOLOGY|PARTNERS|HOLDINGS|INTERNATIONAL|MOTORS|EXCAVATING|"
                      r"PAVING|MAINTENANCE|CLEANING|JANITORIAL|JV|JOINT VENTURE|BUILDERS|ENGINEERING|CONSULTING|MANAGEMENT|"
                      r"FACILITY|FACILITIES|INDUSTRIAL|SUPPLIES|TRUCKING|ROOFERS|EXTERMINATING|PROPERTIES|DEVELOPMENT|"
                      r"NURSERY|NURSERIES|RECYCLING|DISPOSAL|TOWING|CONCRETE|ASPHALT|HEATING|COOLING|LIGHTING|ENERGY|"
                      r"ABATEMENT|RESTORATION|FOUNDATION|ASSOCIATION|AUTHORITY|UNIVERSITY|COLLEGE|AIRLINES)\b|"
                      r"&\s*CO\b|\bCO[.,]|\bCO\s+INC\b")
DBA = re.compile(r"\s+(?:DBA|D/B/A|D\.B\.A\.?)\s+", re.I)
FMT = "%Y-%m-%dT%H:%M:%S"


def get(url, tries=4):
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            last = e
            time.sleep(5 * (i + 1))
    raise SystemExit(f"fetch failed: {url[:180]} ({last})")


def soql_all(where):
    rows, off = [], 0
    while True:
        q = {"$select": ",".join(FIELDS), "$where": where, "$order": ":id", "$limit": 50000, "$offset": off}
        page = get(f"{PORTAL}/resource/{DATASET}.json?" + urllib.parse.urlencode(q))
        rows += page
        if len(page) < 50000:
            return rows
        off += 50000


def months_back(d, n):
    y, m = divmod(d.year * 12 + d.month - 1 - n, 12)
    m += 1
    import calendar
    return dt.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def windows(today):
    return {"today": today.isoformat(), "from12": months_back(today, 12).isoformat(), "from36": months_back(today, 36).isoformat(),
            "endTo": months_back(today, -12).isoformat()}


def amount(r):
    try:
        return round(float(r.get("award_amount") or 0), 2)
    except ValueError:
        return 0.0


def rev(r):
    try:
        return int(str(r.get("revision_number") or "0").strip() or 0)
    except ValueError:
        return 0


def day(s):
    return (s or "")[:10]


def pdf(r):
    v = r.get("contract_pdf")
    u = v.get("url") if isinstance(v, dict) else v
    return u if isinstance(u, str) and u.startswith("http") else ""


def vendor(name):
    n = re.sub(r"\s+", " ", re.sub(r"\s*-{2,}\s*", " - ", (name or "").strip()))
    if not n:
        return "Not stated"
    parts = DBA.split(n, maxsplit=1)
    if len(parts) == 2 and not BUSINESS.search(parts[0].upper()):
        n = parts[1]  # "JOHN SMITH DBA SMITH PLUMBING": show the trade name only, never the owner's own name
    return n if BUSINESS.search(n.upper()) else "Name withheld"


def match(desc, ctype=""):
    """The trade keys a contract description falls under ([] for none). A description can name more than one trade."""
    d = re.sub(r"\s+", " ", (desc or "").upper())
    if (ctype or "").upper() in NOT_TRADE_TYPES or NOT_WORK.search(d):
        return []
    out = []
    for t in TRADES:
        if re.search(t["re"], d) and not (t["out"] and re.search(t["out"], d)):
            out.append(t["key"])
    if out and SUPPLY.search(d) and not WORK.search(d):
        return []
    return out


def row_out(r):
    """One published row: business fields only (the order is ROW_COLS)."""
    kind = -1 if rev(r) == 0 and TRANSFER.search(r.get("purchase_order_description") or "") else rev(r)
    return [day(r.get("approval_date")), kind, re.sub(r"\s+", " ", (r.get("purchase_order_description") or "").strip()),
            title_dept(r.get("department")), vendor(r.get("vendor_name")), amount(r), (r.get("contract_type") or "").strip(),
            (r.get("procurement_type") or "").strip(), (r.get("specification_number") or "").strip(),
            (r.get("purchase_order_contract_number") or "").strip(), day(r.get("start_date")), day(r.get("end_date")), pdf(r)]


ROW_COLS = ["approved", "revision",   # revision -1: a transfer to a new contract number, not a new award
 "description", "department", "vendor", "amount", "contractType", "procurementType",
            "spec", "contract", "start", "end", "pdf"]
SMALL = {"OF", "AND", "THE", "FOR", "ON", "IN", "AT", "TO"}
KEEP_UP = {"CDA", "DPS", "CDOT", "DFSS", "OEMC", "CPL", "DOB", "DWM", "DSS", "2FM", "IT"}


def title_dept(s):
    s = re.sub(r"\s+", " ", (s or "").strip())
    if not s:
        return "Not stated"
    s = s.replace("DEPT ", "DEPARTMENT ").replace("ENVIROMENT", "ENVIRONMENT").replace(" & ", " AND ")
    w = [x if x in KEEP_UP else (x.lower() if i and x in SMALL else x.capitalize()) for i, x in enumerate(s.split(" "))]
    return " ".join(w).replace("Ohare", "O'Hare").replace("O'hare", "O'Hare")


def stats(rows):
    """Counts and money for a set of published rows, originals and modifications apart."""
    orig = [r for r in rows if r[1] == 0]
    mods = [r for r in rows if r[1] > 0]
    moved = [r for r in rows if r[1] < 0]
    paid = [r[5] for r in orig if r[5] > 0]
    return {"awards": len(orig), "paid": len(paid), "total": round(sum(paid), 2),
            "median": round(statistics.median(paid), 2) if paid else None,
            "zero": sum(1 for r in orig if r[5] == 0), "negAwards": sum(1 for r in orig if r[5] < 0),
            "mods": len(mods), "modsUp": sum(1 for r in mods if r[5] > 0), "modsUpTotal": round(sum(r[5] for r in mods if r[5] > 0), 2),
            "modsDown": sum(1 for r in mods if r[5] < 0), "modsDownTotal": round(sum(r[5] for r in mods if r[5] < 0), 2),
            "modsZero": sum(1 for r in mods if r[5] == 0), "transfers": len(moved)}


def group(rows, idx, top=None):
    g = {}
    for r in rows:
        if r[1] != 0:
            continue
        k = r[idx] or "Not stated"
        x = g.setdefault(k, {"name": k, "n": 0, "paid": 0, "total": 0.0, "zero": 0})
        x["n"] += 1
        if r[5] > 0:
            x["paid"] += 1; x["total"] = round(x["total"] + r[5], 2)
        elif r[5] == 0:
            x["zero"] += 1
    out = sorted(g.values(), key=lambda x: (-x["total"], -x["n"], x["name"]))
    return out[:top] if top else out


def build(rows36, ending_rows, today, meta, fetched):
    """rows36: raw rows approved in the 36-month window; ending_rows: every revision of each contract that has a revision
    ending in the next 12 months. Returns the published file."""
    w = windows(today)
    pub = []
    for r in rows36:
        a = day(r.get("approval_date"))
        if not (w["from36"] <= a < w["today"]):
            continue
        keys = match(r.get("purchase_order_description"), r.get("contract_type"))
        if keys:
            pub.append((keys, row_out(r)))
    # contracts ending: the latest revision decides the end date; the value is every revision added up
    by_po = {}
    for r in ending_rows:
        by_po.setdefault((r.get("purchase_order_contract_number") or "").strip(), []).append(r)
    ending = []
    for po, rs in by_po.items():
        if not po:
            continue
        rs.sort(key=lambda r: (rev(r), day(r.get("approval_date"))))
        last, first = rs[-1], rs[0]
        end = day(last.get("end_date"))
        if not (w["today"] <= end <= w["endTo"]):   # the next 12 months, Oct 27, 2027 included
            continue
        keys = match(first.get("purchase_order_description") or last.get("purchase_order_description"), first.get("contract_type") or last.get("contract_type"))
        if not keys:
            continue
        orig = [r for r in rs if rev(r) == 0]
        value = round(sum(amount(r) for r in rs), 2)
        ending.append((keys, {"contract": po, "spec": (first.get("specification_number") or "").strip(),
                              "description": re.sub(r"\s+", " ", (first.get("purchase_order_description") or "").strip()),
                              "department": title_dept(last.get("department") or first.get("department")),
                              "vendor": vendor(last.get("vendor_name") or first.get("vendor_name")),
                              "contractType": (first.get("contract_type") or "").strip(), "procurementType": (first.get("procurement_type") or "").strip(),
                              "approved": day(first.get("approval_date")), "start": day(first.get("start_date")), "end": end,
                              "original": round(sum(amount(r) for r in orig), 2), "value": value, "revisions": max(rev(r) for r in rs), "changes": sum(1 for r in rs if rev(r) > 0),
                              "requirements": bool(orig) and all(amount(r) == 0 for r in orig),
                              "pdf": next((pdf(r) for r in reversed(rs) if pdf(r)), "")}))
    trades = []
    for t in TRADES:
        rows = [r for keys, r in pub if t["key"] in keys]
        rows.sort(key=lambda r: (r[0], r[9], r[1]), reverse=True)
        r12 = [r for r in rows if r[0] >= w["from12"]]
        end = sorted([e for keys, e in ending if t["key"] in keys], key=lambda e: (e["end"], -e["value"], e["contract"]))
        trades.append({"key": t["key"], "name": t["name"], "short": t["short"], "words": t["words"],
                       "m12": stats(r12), "m36": stats(rows),
                       "byDept": group(rows, 3), "byProc": group(rows, 7),
                       "topVendors": [v for v in group(rows, 4, None) if v["name"] not in ("Name withheld", "Not stated") and v["total"] > 0][:10],
                       "withheld": sum(1 for r in rows if r[4] == "Name withheld"),
                       "ending": end, "rows": rows})
    return {"source": {"dataset": DATASET, "url": DATASET_PAGE, "api": f"{PORTAL}/resource/{DATASET}.json",
                       "name": meta.get("name", "Contracts"), "rowsUpdatedAt": meta.get("rowsUpdatedAtIso", ""),
                       "fetchedAt": fetched, "rowsRead": len(rows36), "endingRowsRead": len(ending_rows)},
            "window": w, "rowCols": ROW_COLS, "trades": trades}


def main():
    now = dt.datetime.now(CHI)
    today = now.date()
    w = windows(today)
    meta = get(f"{PORTAL}/api/views/{DATASET}.json")
    meta = {"name": meta.get("name"), "rowsUpdatedAtIso": dt.datetime.fromtimestamp(meta.get("rowsUpdatedAt") or 0, CHI).isoformat(timespec="seconds")}
    rows36 = soql_all(f"approval_date >= '{w['from36']}T00:00:00' AND approval_date < '{w['today']}T00:00:00'")
    cand = soql_all(f"end_date >= '{w['today']}T00:00:00' AND end_date <= '{w['endTo']}T23:59:59'")
    pos = sorted({(r.get("purchase_order_contract_number") or "").strip() for r in cand
                  if match(r.get("purchase_order_description"), r.get("contract_type"))} - {""})
    ending_rows = []
    for i in range(0, len(pos), 80):   # every revision of each candidate contract, so a later extension moves the end date
        ids = ",".join("'" + p.replace("'", "''") + "'" for p in pos[i:i + 80])
        ending_rows += soql_all(f"purchase_order_contract_number in ({ids})")
    # a candidate whose description sits only on a later revision still needs that row
    d = build(rows36, ending_rows, today, meta, now.isoformat(timespec="seconds"))
    os.makedirs(OUT, exist_ok=True)
    json.dump(d, open(os.path.join(OUT, "contracts.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    tune = {t["key"]: {"n36": len(t["rows"]), "top": top_desc(t["rows"])} for t in d["trades"]}
    tune["_supplyLeftOut"] = supply_left_out(rows36)
    json.dump(tune, open(os.path.join(OUT, "trade-map-check.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"rows36": len(rows36), "candidates": len(pos), "endingRows": len(ending_rows),
                      "trades": {t["key"]: [t["m36"]["awards"], t["m36"]["mods"], len(t["ending"])] for t in d["trades"]}}))


def top_desc(rows, n=40):
    """The most common descriptions in a trade, for checking the map by eye (descriptions only, no vendor)."""
    c = {}
    for r in rows:
        c[r[2][:70]] = c.get(r[2][:70], 0) + 1
    return sorted(c.items(), key=lambda x: (-x[1], x[0]))[:n]


def supply_left_out(rows):
    c = {}
    for r in rows:
        d = re.sub(r"\s+", " ", (r.get("purchase_order_description") or "").upper())
        if any(re.search(t["re"], d) for t in TRADES) and SUPPLY.search(d) and not WORK.search(d):
            c[d[:70]] = c.get(d[:70], 0) + 1
    return sorted(c.items(), key=lambda x: -x[1])[:40]


def selftest():
    today = dt.date(2026, 10, 27)
    R = lambda desc, a, rv=0, ad="2026-05-01", ct="WORK SERVICES / FACILITIES MAINT.", po="P1", end=None, v="ACME CLEANING INC", pr="BID", pdfu="https://x/p.pdf": {
        "purchase_order_description": desc, "award_amount": str(a), "revision_number": str(rv), "approval_date": ad + "T00:00:00.000",
        "contract_type": ct, "purchase_order_contract_number": po, "end_date": (end + "T00:00:00.000") if end else None,
        "vendor_name": v, "procurement_type": pr, "department": "DEPT OF FLEET AND FACILITY MANAGEMENT", "contract_pdf": {"url": pdfu},
        "address_1": "1 MAIN ST", "zip": "60601"}
    rows = [R("JANITORIAL SERVICES - CITYWIDE", 100000, po="A"), R("JANITORIAL SERVICES - CITYWIDE", 300000, po="B", ad="2024-01-10"),
            R("JANITORIAL SUPPLIES", 5000, po="C"), R("JANITORIAL SERVICES", 0, po="D", v="JOHN Q SMITH"),
            R("JANITORIAL SERVICES", -2000, rv=2, po="A"), R("JANITORIAL SERVICES", 7000, rv=1, po="A"),
            R("ROOF REPLACEMENT AND TREE TRIMMING", 50000, po="E", v="ROOF & TREE CO"), R("SEWER CLEANING", 9, po="F"),
            R("PEST CONTROL", 9, po="G", ct="DELEGATE AGENCY"), R("SNOW PLOWING SERVICES", 20000, po="H", ad="2023-09-01"),
            R("ROCK SALT FOR SNOW", 1, po="I"), R("NOT A NEW AWARD - Replacing PO # 1 - JANITORIAL SERVICES", 900, po="J"),
            R("PARTS AND REPAIR SERVICES - MECHANICAL, ELECTRICAL", 5, po="L"), R("AMERICAN AIRLINES - TERMINAL 3 HVAC UPGRADES", 9, po="N"),
            R("Agreement between the City of Chicago and Board of Education - TURF Field", 9, po="O"), R("PURCHASE AND DELIVERY OF RODENTICIDES", 5, po="M")]
    ending = [R("JANITORIAL SERVICES", 0, po="D", end="2027-01-31", v="JOHN Q SMITH"), R("JANITORIAL SERVICES", 0, rv=3, po="D", end="2027-03-31"),
              R("JANITORIAL SERVICES", 5, po="Q", end="2027-10-27"),
              R("JANITORIAL SERVICES", 0, po="K", end="2026-12-31"), R("JANITORIAL SERVICES", 0, rv=1, po="K", end="2028-12-31")]
    d = build(rows, ending, today, {"name": "Contracts", "rowsUpdatedAtIso": "2026-10-27T03:17:28-05:00"}, "2026-10-27T08:00:00-05:00")
    T = {t["key"]: t for t in d["trades"]}
    j = T["janitorial"]
    assert j["m36"]["awards"] == 3 and j["m36"]["paid"] == 2 and j["m36"]["total"] == 400000 and j["m36"]["median"] == 200000, j["m36"]
    assert j["m12"]["awards"] == 2 and j["m12"]["total"] == 100000 and j["m12"]["zero"] == 1, j["m12"]
    assert j["m36"]["transfers"] == 1 and all(r[2][:3] != "NOT" or r[1] == -1 for r in j["rows"]), "a transfer is not a new award"
    assert T["electrical"]["m36"]["awards"] == 0 and T["pest-control"]["m36"]["awards"] == 0, "fleet repair and purchases are not trade work"
    assert j["m36"]["mods"] == 2 and j["m36"]["modsUpTotal"] == 7000 and j["m36"]["modsDownTotal"] == -2000, "modifications apart"
    assert all("SUPPLIES" not in r[2] for r in j["rows"]), "supplies left out"
    assert any(r[4] == "Name withheld" for r in j["rows"]) and j["withheld"] == 1, "a person's name is withheld"
    assert "JOHN" not in json.dumps(d) and "MAIN ST" not in json.dumps(d) and "60601" not in json.dumps(d), "no person, no address"
    assert [e["contract"] for e in j["ending"]] == ["D", "Q"] and j["ending"][0]["end"] == "2027-03-31" and j["ending"][0]["requirements"], "latest revision sets the end; the last day counts"
    assert j["ending"][0]["changes"] == 1 and j["ending"][0]["revisions"] == 3, "changes are counted records, not the revision number"
    assert T["hvac"]["m36"]["awards"] == 0 and T["landscaping"]["m36"]["awards"] == 1, "airline projects and school deals are not trade work"
    assert T["roofing"]["m36"]["awards"] == 1 and T["landscaping"]["m36"]["awards"] == 1, "one contract can name two trades"
    assert T["pest-control"]["m36"]["awards"] == 0, "delegate agency grants are not trade work"
    assert T["snow-removal"]["m36"]["awards"] == 0, "rock salt is a purchase; the plowing award is older than 36 months"
    assert d["window"] == {"today": "2026-10-27", "from12": "2025-10-27", "from36": "2023-10-27", "endTo": "2027-10-27"}
    assert match("MASTER AGREEMENT FOR DEMOLITION SERVICES") == ["demolition"] and match("TAXIWAY REHAB") == []
    assert vendor("MIDWEST WRECKING COMPANY 01") != "Name withheld" and vendor("MAX MADSON") == "Name withheld" and vendor("JOHN SMITH & MARY SMITH") == "Name withheld"
    assert vendor("MARIA LOPEZ AND JOSE LOPEZ") == "Name withheld" and vendor("A & M GENERAL CONTRACTOR, INC.") != "Name withheld"
    for p in ("JOHN SNOW", "MICHAEL POWER", "JAMES STEEL", "ANNA CENTER", "LEE NATIONAL", "AL CO", "JOHN Q SMITH &", "AND", "JOHN SMITH D/B/A JS"):
        assert vendor(p) == "Name withheld", p
    assert vendor("JOHN SMITH DBA SMITH PLUMBING") == "SMITH PLUMBING" and vendor("ALFRED BENESCH & CO") != "Name withheld"
    assert vendor("SEVEN-D CONSTRUCTION CO.") != "Name withheld" and vendor("SNOW SYSTEMS") != "Name withheld"
    assert title_dept("DEPT OF FLEET AND FACILITY MANAGEMENT") == "Department of Fleet and Facility Management"
    print("dp_contracts_data selftest: ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
    else:
        main()
