#!/usr/bin/env python3
"""Chicago permit leads pilot (Todd approved Oct 14, 2026; coo/OPPORTUNITIES.md Case 4).

Runs in GitHub Actions (.github/workflows/permits-chicago.yml) because the cloud agents' network
cannot reach data.cityofchicago.org. Pulls the City of Chicago Building Permits dataset, keeps big
commercial and apartment projects with a business listed as general contractor, and writes only
public, business-level fields to permits/chicago/:

  sample.json        the projects the free sample page shows, plus counts and the source line
  profile.json       column names, permit and contact type counts (tunes the filters; no names)
  source-terms.txt   the City's data terms page as text, for the Legal desk

Never written: owner names, any contact that is not a business acting as general contractor,
phone numbers, emails. Subscribers do their own outreach; the crew never contacts anyone.

Usage: python3 tools/permits_chicago.py [--days 730] [--min-cost 500000] [--top 25] [--full PATH]

--full PATH writes every kept project (the paid weekly list, A1 pre-sale) to PATH. The workflow keeps it
out of the repo and uploads it as a short-lived run artifact that tools/leads_xlsx.py turns into the workbook.
"""
import argparse, collections, datetime as dt, html.parser, json, os, re, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "permits", "chicago")
DATASET = "ydr8-5enu"
PORTAL = "https://data.cityofchicago.org"
DATASET_PAGE = f"{PORTAL}/Buildings/Building-Permits/{DATASET}"
TERMS_URL = "https://www.chicago.gov/city/en/narr/foia/data_disclaimer.html"
AREAS = "igwz-8jzy"   # Boundaries - Community Areas (area number to name)
CLOSED = {"COMPLETE", "COMPLETED", "SUSPENDED", "CANCELLED", "CANCELED", "REVOKED", "EXPIRED", "VOID", "WITHDRAWN", "CLOSED"}
# Window (Todd, Oct 17, 2026: "Keep open permits up to 24 months"): every permit issued in the last 730 days, counted from
# midnight UTC as before, whose City status is still open. Open means ACTIVE or PHASED PERMITTING (a job permitted in phases,
# still under way); anything else (COMPLETE, SUSPENDED, CANCELLED, EXPIRED, REVOKED, a blank or a status the City adds later)
# is left out and counted by name in profile.json, so a new open status shows up there before it costs a lead.
DAYS = 730
OPEN = {"ACTIVE", "PHASED PERMITTING"}


def is_open(status):
    return (status or "").strip().upper() in OPEN


def window_start(now, days=DAYS):
    """The first issue date the list keeps, as the City query writes it: counted back from the Chicago date of the pull, so a
    pull at 02:42 UTC on Oct 18 (Oct 17 in Chicago) keeps permits issued from Oct 17 two years back (holdout, Oct 18)."""
    if getattr(now, "tzinfo", None):
        from zoneinfo import ZoneInfo
        now = now.astimezone(ZoneInfo("America/Chicago"))
    return (now - dt.timedelta(days=days)).strftime("%Y-%m-%dT00:00:00")


def in_window(r, since):
    """True when a City row was issued on or after since and the City still has it open."""
    return (r.get("issue_date") or "")[:19] >= since and is_open(r.get("permit_status"))
UA = {"User-Agent": "ProofNotFluff permit pilot (github.com/proofnotfluff-a11y/Proofnotfluff-pins)"}

BUSINESS = re.compile(r"\b(LLC|L\.L\.C|INC|INCORPORATED|CORP|CORPORATION|CO|COMPANY|LTD|LP|LLP|PLLC|GROUP|BUILDERS?|"
                      r"CONSTRUCTION|CONSTRUCTORS|CONTRACTING|CONTRACTORS?|DEVELOPMENT|DEVELOPERS|ENTERPRISES?|SERVICES|"
                      r"PARTNERS|HOLDINGS|MANAGEMENT|RESTORATION|RENOVATIONS?|INTERIORS|BUILDING|HOMES|REALTY|PROPERTIES|"
                      r"ASSOCIATES|INDUSTRIES|SOLUTIONS|SYSTEMS|BUILD|VENTURES?|SONS?|HUMANITY|ASSOCIATION|AUTHORITY|JV|JOINT VENTURE)\b\.?")
RESIDENTIAL_SMALL = re.compile(r"SINGLE[- ]FAMILY|\bSFR\b|\bS\.F\.R\b|TWO[- ]FLAT|\b2[- ]FLAT|THREE[- ]FLAT|\b3[- ]FLAT|COACH HOUSE|"
                               r"\b(1|2|3|ONE|TWO|THREE)[- ]?(DWELLING UNITS?|DU|D\.U\.?|UNITS?)\b")
UNITS = re.compile(r"\(?(\d{1,4})\)?\s*[- ]?\s*(?:(?:NEW|EXISTING|STANDARD|EFFICIENCY|RESIDENTIAL|AFFORDABLE|AFFORABLE|HOUSING|MARKET[- ]RATE|STUDIO|SENIOR|LIVING|EAST|WEST|NORTH|SOUTH|"
                   r"TOWN ?HOME|TOWN ?HOUSE|RENTAL|CONDO(?:MINIUM)?|\d[- ]STORY)\s+)*(?:DWELLING(?:\s+UNITS?)?\b|D\.?U\.?S?\b|UNITS?\b|APARTMENTS?\b|TOWN ?(?:HOUSE|HOME)S?\b)")
TYPED_UNITS = re.compile(r"\(?(\d{1,4})\)?\s*(?:STANDARD|EFFICIENCY|AFFORDABLE|MARKET[- ]RATE|STUDIO)\s+(?:DWELLING\s+)?UNITS?\b")
# numbered units of a 2 or 3 flat ("UNITS 1 TO 3", "UNIT 1 + UNIT 2"), or a deconversion down to 3 or fewer homes
FLAT_UNITS = re.compile(r"\bUNITS?\s*#?\s*[1-3]\b(?:\s*(?:,|&|\+|AND|TO|THRU|THROUGH|-)\s*(?:UNITS?\s*#?\s*)?[1-3]\b)+|\bDE-?CONVER\w*\b.*?\bTO\s*\(?[1-3]\)?\s*(?:DWELLING|UNITS?|D\.?U)")
# one home inside a bigger building (a condo or a numbered apartment), not an office suite
ONE_HOME = re.compile(r"SINGLE\s+(?:RESIDENTIAL|DWELLING|CONDO\w*)\s+UNIT|CONDO(?:MINIUM)?\s+UNIT|APARTMENT\s*#\s*\d|\b(?:RESIDENTIAL|DWELLING|CONDO\w*)\s+UNIT\s*#?\s*\d{2,5}\b|PENTHOUSE UNIT")
# work that never needs a construction clean under this permit (Holdout QC Oct 17: about 10% of rows)
NON_CLEAN = re.compile(r"CAISSON|\bPILES?\b|PILING|FOUNDATION (?:ONLY|PERMIT)|\bDEMOLITION\b|\bDEMO\b|WRECKING|AIR HANDL|COOLING TOWER|CHILLER|"
                       r"\bBOILERS?\b|ROOF(?:ING)? REPLACEMENT|REPLACE(?:MENT OF)? (?:THE )?ROOF|RE-?ROOF|\bSOLAR\b|WATER ?MAIN|LANDSCAP|RIVERWALK|"
                       r"CURTAIN ?WALL|FACADE|MASONRY REPAIR|TUCKPOINT|RESURFAC|PARKING LOT|ANTENNA|ELEVATOR MODERNI|SPRINKLER SYSTEM|FIRE ALARM|"
                       r"(?:MECHANICAL|ELECTRICAL|PLUMBING|STRUCTURAL|SITE) (?:WORK )?ONLY|NO NEW CONSTRUCTION")
FINISH_WORK = re.compile(r"BUILD[- ]?OUT|INTERIOR (?:ALTERATION|RENOVATION|REMODEL|FINISH)|ALTERATIONS? (?:TO|OF|AND)|RENOVAT|REMODEL|FIT[- ]?OUT|"
                         r"TENANT IMPROVEMENT|CONVERSION|CONVERT|\bERECT|NEW (?:\d+|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN)[- ]STOR|"
                         r"FULL BUILDING PERMIT|DWELLING|RESIDENTIAL BUILDING|APARTMENT BUILDING|ADDITION")
ONLY_TRADE = re.compile(r"(?:CAISSON|PILE|PILING|FOUNDATION|FOUNDATIN|DEMOLITION|DEMO|MECHANICAL|EXCAVATION|SHORING|EARTH ?WORK)S?\b[^.;]{0,40}\bONLY\b|"
                        r"(?<!INTERIOR )\bONLY\b[^.;]{0,25}\b(?:CAISSON|PILE|FOUNDATION|DEMOLITION)|NO NEW CONSTRUCTION")
TRADE_GC = re.compile(r"MECHANICAL|HEATING|COOLING|HVAC|REFRIGERATION|ELECTRIC|PLUMBING|DEMOLITION|WRECKING|ROOFING|SHEET METAL|SPRINKLER|AIR\b")
AREA_NAMES = {"Mckinley Park": "McKinley Park", "Ohare": "O'Hare"}


WORDNUM = {w: i for i, w in enumerate("ZERO ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE TEN ELEVEN TWELVE THIRTEEN FOURTEEN FIFTEEN "
                                         "SIXTEEN SEVENTEEN EIGHTEEN NINETEEN TWENTY".split())}
TENS = {"TWENTY": 20, "THIRTY": 30, "FORTY": 40, "FIFTY": 50, "SIXTY": 60, "SEVENTY": 70, "EIGHTY": 80, "NINETY": 90}


def numerals(desc):
    """Spelled-out counts as digits ("SIX RESIDENTIAL UNIT", "ONE HUNDRED FOUR (104)"), a stated "(104)" winning over words;
    "6-FLAT" as 6 dwelling units; typos like DWELLLING fixed. Used for the homes count and the 4-home test only."""
    d = re.sub(r"\bDWEL+ING\b", "DWELLING", desc)
    d = re.sub(r"\b(?:[A-Z]+[ -]){1,3}\((\d{1,4})\)", lambda m: m.group(1) if re.fullmatch(r"(?:(?:" + "|".join(WORDNUM) + r"|HUNDRED|AND)[ -])+\(\d+\)", m.group(0)) else m.group(0), d)
    unitish = r"(?=[ -](?:(?:\d[- ]STORY[ -])?(?:UNITS?\b|TOWN ?(?:HOUSE|HOME)S?\b)|(?:\w+[ -]){0,2}(?:DWELLING|RESIDENTIAL|APARTMENTS?|D\.?U\b|CONDO\w*)))"
    d = re.sub(r"\b(" + "|".join(TENS) + r")(?:[- ](ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE))?\b" + unitish,
               lambda m: str(TENS[m.group(1)] + (WORDNUM[m.group(2)] if m.group(2) else 0)), d)
    d = re.sub(r"\b(" + "|".join(WORDNUM) + r")\b" + unitish, lambda m: str(WORDNUM[m.group(1)]), d)
    return re.sub(r"\b(\d{1,3})[- ]FLAT\b", r"\1 DWELLING UNITS", d)


def unit_count(desc, display=False):
    """Homes a residential permit describes: a stated total first ("80 TOTAL DWELLING UNITS", "CONTAINING 464 DWELLING UNITS"),
    then a conversion's end count ("FROM 5 TO 8 DWELLING UNITS"), then typed counts added up (101 standard + 48 efficiency = 149)
    when that beats every other count, else the largest count. display=True also drops counts of units being made accessible
    (13 DWELLING UNITS TO MOBILITY ACCESSIBLE UNITS), which describe the work, not the building (Holdout QC Oct 17, fourth pass)."""
    desc = numerals(desc)
    if display and max([int(x) for x in SLEEPING.findall(desc)] or [0]) >= 4:
        n = unit_count(desc)   # a shelter or group home: a caretaker's 1 dwelling unit is not shown as "1 home" (holdout, Oct 18)
        return n if n >= 4 else 0
    if display:
        desc = re.sub(r"\(?\d{1,4}\)?\s*(?:DWELLING |RESIDENTIAL )?UNITS? (?:IN)?TO (?:\w+ ){0,2}(?:ACCESSIBLE|ADA|HEARING|VISION)\w*", " ", desc)
    tot = re.search(r"\(?(\d{1,4})\)?\s+TOTAL (?:\w+ )?(?:UNITS|D\.?U|DWELLING|APARTMENTS)|TOTAL (?:OF )?\(?(\d{1,4})\)?\s*(?:\w+ )?(?:UNITS|D\.?U|DWELLING|APARTMENTS)|"
                    r"\(?(\d{1,4})\)?\s*(?:\w+ ){0,2}?(?:DWELLING UNITS?|UNITS|D\.?U\.?S?|APARTMENTS)\s+TOTAL\b|"
                    r"\b(?:TO|WILL) HAVE (?:A TOTAL OF )?\(?(\d{1,4})\)?\s*(?:\w+ )?(?:UNITS|D\.?U|DWELLING|APARTMENTS)", desc)
    if tot:
        return int(next(g for g in tot.groups() if g))
    # stated total first, then "CONTAINING N UNITS" (holdout, Oct 18: "A TOTAL OF FIFTEEN APARTMENTS" beats "EXISTING BUILDING CONTAINING 9")
    cont = re.search(r"CONTAINING (?:A TOTAL OF )?\(?(\d{1,4})\)?\s*(?:\w+ )?(?:DWELLING UNITS|UNITS|APARTMENTS|D\.?U)", desc)
    if cont:
        return int(cont.group(1))

    conv = re.search(r"FROM \(?\d{1,4}\)?\s*(?:D\.?U\.?|DWELLING UNITS?|UNITS?)?\s*TO \(?(\d{1,4})\)?\s*(?:D\.?U|DWELLING|UNITS?)", desc)
    if conv:
        return int(conv.group(1))
    # a conversion counts the homes after the work: "EXISTING 4 D.U. RESIDENTIAL TO 2 DWELLING UNIT" is 2, "CONVERT EXISTING
    # OFFICE BUILDING TO (12) DWELLING UNITS" is 12 (Holdout, Oct 18: 101062180 was kept with 4 homes)
    UNIT_WORD = r"(?:D\.?U\.?S?(?![A-Z])|DWELLING(?: UNITS?)?\b|UNITS?\b|APARTMENTS?\b|RESIDENCES?\b)"
    # only words that describe homes may sit between the count and "units" (not SLEEPING, GUEST or ADDITIONAL units)
    ADJ = r"(?:(?:NEW|STANDARD|EFFICIENCY|RESIDENTIAL|RESIDENTAIL|AFFORDABLE|MARKET[- ]RATE|STUDIO|SENIOR|TOWN ?HOME|RENTAL|CONDO(?:MINIUM)?)[- ]){0,3}"
    after = re.search(r"\bEXISTING\s+\(?\d{1,4}\)?\s*[- ]?" + ADJ + UNIT_WORD + r"[^.;]{0,60}?\bIN(?:TO)?\s+\(?(\d{1,4})\)?\s*[- ]?" + ADJ + UNIT_WORD
                      + r"|\bEXISTING\s+\(?\d{1,4}\)?\s*[- ]?" + ADJ + UNIT_WORD + r"[^.;]{0,60}?\bTO\s+\(?(\d{1,4})\)?\s*[- ]?" + ADJ + UNIT_WORD
                      + r"|\bCONVER(?:T|TS|TED|TING|SION)\b[^.;]{0,100}?\b(?:IN)?TO\s+(?:A\s+)?\(?(\d{1,4})\)?\s*[- ]?" + ADJ + UNIT_WORD, desc)
    if after:
        return int(next(g for g in after.groups() if g))
    found = list(UNITS.finditer(desc))
    # homes left untouched by the work count too ("WORK TO 6 D.U. (NO WORK ON REMAINING 18 D.U.)" is a 24-home building)
    rem = re.search(r"\bREMAINING\s+\(?(\d{1,4})\)?\s*(?:EXISTING\s+)?(?:D\.?U|DWELLING|UNITS?|APARTMENTS?)", desc)
    if rem:
        rest = [int(m.group(1)) for m in found if not (m.start() <= rem.start(1) < m.end())]
        return max(rest or [0]) + int(rem.group(1))
    # homes added to the existing ones ("13 UNITS ... CONVERTED INTO 9 ADDITIONAL UNITS" is 22; "23 EXISTING D.U.'S & ADD 1 NEW D.U." is 24)
    added = [m for m in re.finditer(r"\(?(\d{1,4})\)?\s+(?:ADDITIONAL|MORE)\s+(?:\w+\s+){0,2}?(?:D\.?U|DWELLING|UNITS?|APARTMENTS?)|"
                                    r"\bADD(?:ING|S)?\s+\(?(\d{1,4})\)?\s+(?:NEW\s+)?(?:D\.?U|DWELLING|UNITS?|APARTMENTS?|A\.?D\.?U)", desc)]
    if added:
        spans = [(a.start(), a.end()) for a in added]
        rest = [int(m.group(1)) for m in found if not any(a <= m.start(1) < b for a, b in spans)]
        adds = [int(a.group(1) or a.group(2)) for a in added]
        if rest and max(rest) in adds:   # the same new homes named twice, not existing plus new
            return max(rest)
        if rest:
            return max(rest) + sum(adds)
    typed = [int(m.group(1)) for m in TYPED_UNITS.finditer(desc)]
    counts = [int(m.group(1)) for m in found]
    if len(typed) >= 2 and sum(typed) >= max(counts or [0]):
        return sum(typed)
    # efficiency units are homes too, the same way the typed sum counts them ("103 DWELLING UNITS AND 50 EFFICIENCY UNITS" is 153)
    eff = [m for m in found if "EFFICIENCY" in m.group(0)]
    plain = [int(m.group(1)) for m in found if "EFFICIENCY" not in m.group(0) and re.search(r"DWELLING|D\.?U", m.group(0))]
    if eff and plain:
        e = sum(int(m.group(1)) for m in eff)
        if any(e + p == max(plain) for p in plain):   # "46 DWELLING UNITS; 37 EFFICIENCY UNITS + 9 DWELLING UNITS" is a 46-home breakdown
            return max(plain)
        return max(plain) + e
    final = re.search(r"\bTO\s*\(?(\d{1,4})\)?\s*(?:DWELLING|UNITS?|D\.?U|APARTMENTS?)", desc)
    if final and re.search(r"DE-?CONVER|REDUC", desc):
        return int(final.group(1))
    if not counts:   # numbered units only ("UNIT 1, UNIT 2 ... UNIT 5"): the highest number when it starts at 1
        nums = [int(x) for x in re.findall(r"\bUNIT\s*#?\s*(\d{1,2})\b", desc)]
        if nums and 1 in nums and max(nums) >= 4 and max(nums) <= len(set(nums)) + 1:
            return max(nums)
    return max(counts) if counts else 0


def gc_clean(nm):
    nm = re.split(r"\s+(?:ATTN|ATTENTION|C/O)\b.*$", nm, flags=re.I)[0].strip(" ,;:")
    if re.search(r"\s+D/?B/?A\s+", nm, re.I) and len(nm) >= 45:   # the City cuts names at 50 characters: keep the legal name
        return re.split(r"\s+D/?B/?A\s+", nm, flags=re.I)[0].strip(" ,;:")
    return nm   # as the City lists it: no ellipsis is ever added (holdout, Oct 18: "DINASO AND SONS ... INCORPORATED...")


CLEANER = re.compile(r"\b(?:CLEANING|JANITORIAL|MAID|CUSTODIAL)\b")


def gc_filter(nm):
    """The builder's name as the list prints it, or None when it names no one worth calling: a generic "CONSTRUCTION, INC."
    or a cleaning company (a cleaner would be calling a cleaner; Holdout QC Oct 17, third pass)."""
    nm = gc_clean(nm).lstrip("@ ")
    generic = re.sub(r"\b(?:CONSTRUCTION|CONSTRUCTORS|CONTRACTING|CONTRACTORS?|BUILDERS?|GENERAL|SERVICES|GROUP|COMPANY|CO|"
                     r"INC|INCORPORATED|LLC|L\.L\.C|CORP|CORPORATION|LTD|LP|THE|AND)\b\.?", "", nm.upper())
    if not re.search(r"[A-Z0-9]", generic) or CLEANER.search(nm.upper()):
        return None
    return title_name(nm)
COMMERCIAL = re.compile(r"RETAIL|COMMERCIAL|OFFICE|RESTAURANT|HOTEL|SCHOOL|WAREHOUSE|INDUSTRIAL|MIXED[- ]USE|MEDICAL|"
                        r"CLINIC|HOSPITAL|CHURCH|FITNESS|\bGYM\b|\bSTORE\b|\bBANK\b|\bLAB\b|LABORATORY|DATA CENTER|TENANT|"
                        r"BUILD[- ]?OUT|CAFE|\bBAR\b|THEATER|THEATRE|UNIVERSITY|COLLEGE|LIBRARY|DAY ?CARE|MANUFACTURING|"
                        r"DISTRIBUTION|SENIOR|ASSISTED LIVING|DORMITORY|STUDENT HOUSING|APARTMENT|MULTI[- ]?FAMILY|"
                        r"\bMF\b|CONDOMINIUM|HIGH[- ]RISE|MID[- ]RISE")


# Holdout, Oct 18 (145 good jobs dropped for "no commercial wording"): building types and rooms that are never a house,
# and the City's non-residential occupancy groups. WEAK words (a floor, a suite, a lobby) count only when no house word is near.
COMMERCIAL2 = re.compile(r"\bBUSINESS\b|\bASSEMBLY\b|RELIGIOUS|SYNAGOGUE|SANCTUARY|MOSQUE|\bTEMPLE\b|MUSEUM|GALLERY|CONSERVATORY|EXHIBIT|CULTURAL|"
                         r"ATHLETIC|FIELDHOUSE|GYMNASIUM|DANCE STUDIO|CAR ?WASH|MINI[- ]?MART|GAS STATION|DRIVE[- ]?(?:THRU|THROUGH)|"
                         r"STORAGE (?:FACILITY|BUILDING|USE)|SELF[- ]STORAGE|FACTORY|\bTERMINAL\b|CONCOURSE|AIRPORT|O'?HARE|POLICE|FIRE ?HOUSE|FIRE STATION|"
                         r"HOLDING CELLS|CONVENT|FUNERAL|COMMUNITY CENTER|COUNSELING|SURG(?:ERY|ICAL)|INTENSIVE CARE|CARDIOLOGY|HEALTH (?:CENTER|CLUB)|"
                         r"CLASSROOMS?|LOCKER ROOMS?|STUDENT TOILETS|CONFERENCE CENTER|PADEL|PICKLE ?BALL|CURRENCY EXCHANGE|AUTO BODY|CASINO|POOL DECK|"
                         r"BATH HOUSE|\bMALL\b|\bTSA\b|SPEC SUITES?|EXPERIENCE CENTER|INSTITUTIONAL|SHELL SPACE|GROCERY|TRADING|ADAPTIVE REUSE|DIALYSIS|"
                         r"ACCESSORY BUILDING|FOOD (?:PREP|SERVICE)|\bSHELTER\b|GROUP (?:HOME|LIVING)|TRANSITIONAL|CONGREGATE|SLEEPING UNITS|TRANSIT STATION|"
                         r"\bSTATION (?:ENCLOSURE|HOUSE)|\bMARKET\b|\bB[- ]BUSINESS\b|TOWN ?(?:HOUSE|HOME)S")
OCCUPANCY = re.compile(r"\b(?:OCC(?:UPANCY|UPACY)?\.?|USE|GROUPS?|CLASSIFICATIONS?)\s*(?:GROUPS?\s*|TYPE\s*|CLASSIFICATIONS?\s*|IS\s*)?[:\-]?\s*\(?"
                       r"(?:A-?[1-5]|B|E-?1?|F-?[12]|H-?[1-5]|I-?[1-4]|M|S-?[12])\b|\b(?:A-[1-5]|I-[1-4]|E-1|S-[12]|F-[12]|H-[1-5])\b")
WEAK_COMMERCIAL = re.compile(r"\bSUITES?\s*#?\s*[A-Z]?\d|\bFLOORS?\s+\d|\b\d{1,3}(?:ST|ND|RD|TH) FLOOR|\bLOBBY\b|REST?OOMS|TOILET ROOMS|CONFERENCE|EXAM ROOMS")
HOUSE = re.compile(r"\bRESIDENCE\b|(?<!TOWN)(?<!TOWN )(?<!FIRE)(?<!FIRE )(?<!BATH )(?<!STATION )\bHOUSE\b|(?<!FUNERAL )(?<!GROUP )(?<!COMMUNITY )\bHOME\b|"
                   r"SINGLE[- ]FAMILY|\bR-?3\b|\bCOACH HOUSE")
# work another permit covers ("CAISSON ONLY PERMIT UNDER 101050276", "H-PILE PERMIT NUMBER 101041429"): never decides this permit
OTHER_PERMIT = re.compile(r"(?:UPON |UNDER |WITH |PER |AND )?(?:A |THE )?(?:SEPARATE )?(?:PHASE \d+:? )?(?:CAISSONS?|PILES?|H-PILES?|FOUNDATIONS?|DEMOLITION|DEMO|WRECKING|"
                          r"EXCAVATION|SHORING|EX/ERS|ERS|EARTH RETENTION|SUPERSTRUCTURE|SUBSTRUCTURE|INFRASTRUCTURE)\b[^.;(]{0,40}?\(?"
                          r"(?:\b(?:PERMIT(?:TED)?|PERMIT NUMBER)\b\s*(?:UNDER|NO\.?|NUMBER|#)?|\bUNDER\b)\s*(?:PERMIT\s*)?(?:NO\.?\s*)?#?\s*10\d{6,7}\b")
# work on one home in a bigger building ("ALTERATIONS TO EXISTING DWELLING UNIT 22BC"), or two units made one (holdout, Oct 18)
ONE_UNIT_WORK = re.compile(r"(?:ALTERATIONS?|RENOVATIONS?|REMODEL\w*|BUILD[- ]?OUT|IMPROVEMENTS?)\s+(?:TO|OF|IN|FOR)\s+(?:AN?\s+|THE\s+)?(?:EXISTING\s+)?"
                           r"(?:DWELLING|RESIDENTIAL|CONDO\w*|APARTMENT)\s+UNIT\s*#?\s*\d{1,5}[A-Z]{0,3}\b(?!\s*(?:AND|&|,|-|TO|THRU|THROUGH)\s*#?\s*\d)|"
                           r"\bUNITS?\s*#?\s*\d{2,5}[A-Z]?\s*(?:AND|&)\s*#?\s*\d{2,5}[A-Z]?\b[^.;]{0,40}?\bTO\s+(?:1|ONE)\b|"
                           r"CONVERSION OF (?:2|TWO) (?:EXISTING )?(?:\w+ ){0,2}(?:DWELLING )?UNITS[^.;]{0,30}?\bTO (?:1|ONE)\b|"
                           r"(?:ALTERATIONS?|RENOVATIONS?|REMODEL\w*)\s+(?:TO|OF)\s+(?:AN?\s+|THE\s+)?(?:EXISTING\s+)?(?:\d{1,3}(?:ST|ND|RD|TH) FLOOR\s+)?"
                           r"(?:RESIDENTIAL|DWELLING|CONDO\w*)\s+UNIT\b(?!S)")
ONE_UNIT_PLAIN = re.compile(r"(?:ALTERATIONS?|RENOVATIONS?|REMODEL\w*)\s+(?:TO|OF|IN)\s+(?:EXISTING\s+)?UNIT\s*#?\s*\d{1,5}[A-Z]{0,3}\b(?!\s*(?:AND|&|,|-|TO|THRU|THROUGH)\s*#?\s*\d)")
SLEEPING = re.compile(r"\(?(\d{1,4})\)?\s+(?:[A-Z]+\s+){0,2}?SLEEPING (?:UNITS?|ROOMS?)")


def get(url, params=None, tries=3, as_text=False):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                body = r.read().decode("utf-8", "replace")
                return body if as_text else json.loads(body)
        except Exception as e:  # network hiccup or 5xx: wait and retry
            last = e
            time.sleep(5 * (i + 1))
    raise SystemExit(f"fetch failed: {url[:160]} ({last})")


class Text(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "nav", "header", "footer"): self.skip += 1
        if tag in ("p", "li", "h1", "h2", "h3", "h4", "br", "div", "tr"): self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "nav", "header", "footer") and self.skip: self.skip -= 1
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)


def terms_text():
    raw = get(TERMS_URL, as_text=True)
    t = Text(); t.feed(raw)
    lines = [re.sub(r"\s+", " ", x).strip() for x in "".join(t.parts).split("\n")]
    lines = [x for x in lines if len(x) > 2]
    return f"Source: {TERMS_URL}\nFetched: {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}\n\n" + "\n".join(lines)


SEP = r"[\s*\[\]()/,.:;&-]*"
SEP_R = r"[\s*\])/,.:;&-]*"          # after a token: never eat an opening bracket that starts the real text
PREFIX = re.compile(r"^(?:" + SEP + r"(?:DDS|DIRECT DEVELOPER SERVICES|S?ELF[- ]?(?:CERT(?:IFIED|IFICATION)?|CRT|CER)(?: (?:OF|FOR) (?:A )?LIMITED SCOPE RENOVATION)?|"
                    r"SC|SPR|STANDARD PLAN(?: REVIEW)?(?: PROGRAM)?|EPR|EXPRESS PERMIT|EASY PERMIT|PMD\d*|(?:19|20)\d{2}(?=CPS)|(?:19|20)\d{2}|CB[A-Z]{1,3}|CRBC|"
                    r"CHICAGO BUILDING (?:REHABILITATION )?CODE|CHICAGO REHABILITATION CODE(?: \d{4})?|(?:WITH )?STRUC?TU?R?AL PEER REVIEW(?: INCLUDED)?|"
                    r"TITLE 14R|W/ \w+ \d{4} SUPPLEMENTS|CPS SCHOOL - NO CHANGE IN USE(?: OR OCCUPANCY)?|NO CHANGE IN USE(?: OR OCCUPANCY)?|EXISTING ZONED [A-Z]+[- ]?\d+(?:\.\d+)?|"
                    r"D[XCS]-?\d+(?:\.\d+)?|[A-Z]-\d(?=,)|ASSEMBLY USE|SCOPE OF WORK(?: TO INCLUDE| INCLUDES)?|SCOPE INCLUDED|FOR|&|AND)(?![A-Z0-9]|-[A-Z0-9])" + SEP_R + r")+", re.I)
ACRONYMS = re.compile(r"\b(?:(?:i{1,3}|iv|v)-?[ab]|[abemrs]-\d|dx-\d+|cps|mep|hvac|ada|adu|cta|uic|ups|rtus?|ahus?|sf|sqft|llc|ii|iii|iv|cvs|usps|cha|cdph|ohc|pru|hq)\b", re.I)


NOISE = re.compile(r"\s*\((?:[^()]*?\b(?:construction type|occupancy|use group|type [ivx]+[ab]?|sprinkl\w*|per plans|nfpa)\b[^()]*)\)", re.I)
TAIL = re.compile(r"[;,.]?\s*\b(?:occupancy group|use group|construction type|as per plans|per plans)\b.*$", re.I)


# Free-text permit descriptions can end with a plan reviewer's, consultant's or owner's name (Legal desk, Oct 15):
# everything from the first such tag on is dropped before anything else, so no person's name reaches the page or the list.
PERSON_TAG = re.compile(r"\b(?:plan\s+)?(?:reviewers?|consultants?|cons[a-z]{2,6}ants?|architects?|engineers?|owners?(?!['\u2019]s)|designers?|expeditors?|"
                        r"prepared\s+by|drawn\s+by|designed\s+by|attn|c/o|contact|mr|mrs|ms|dr)\b\.?", re.I)


WORK = re.compile(r"alter|renovat|build[- ]?out|\berect|construct|conver|remodel|install|replac|demol|repair|addition|finish|rehab", re.I)


def clean_scope(desc, limit=150, whole=False):
    """The permit's scope as the list prints it. whole=True keeps every sentence (the members' app's project page) and
    still cuts at the first reviewer, consultant or owner tag, so no person's name reaches the page."""
    d = re.sub(r"\s+", " ", (desc or "").replace("\u00bf", " ")).strip()
    d = re.sub(r"NO CHANGE IN USE(?=[A-Z])", "NO CHANGE IN USE. ", d)   # the City's text sometimes runs two words together here
    # a reviewer's initials at the very end ("... 2025 N RACINE. HLH)"): consonants only, after a stop (Holdout, Oct 18)
    d = re.sub(r"[.;,]\s*[B-DF-HJ-NP-TV-Z]{2,3}\)\s*$", ")", d)
    d = re.sub(r"[.;,]\s*[B-DF-HJ-NP-TV-Z]{2,3}\s*$", "", d)
    d = re.sub(r"\b((?:19|20)\d{2})(CPS)\b", r"\1 \2", d)
    d = PREFIX.sub("", d)
    d = re.sub(r"^\(\d+[A-Z]? [NSEW]\.? [^)]{2,40}\)\s*", "", d, flags=re.I)   # a leading street address the list already shows
    d = re.split(r"\*\*", d)[0]
    d = re.sub(r"\bINCLUDING\s*,\s*", "INCLUDING ", d, flags=re.I)
    d = re.sub(r"\b(?:AS )?PER \w+(?: \w+)? (?:E-?MAIL|EMAIL|CALL|CONVERSATION)\b[^.;]*", "", d, flags=re.I)
    d = re.sub(r"\b(\w+) \1\b", r"\1", d, flags=re.I)
    m = PERSON_TAG.search(d)
    if m:
        d = d[:m.start()]
    d = d.strip().rstrip(".")
    d = PREFIX.sub("", d).strip(" :-/.,")
    d = NOISE.sub("", d)
    d = re.sub(r"^\d{1,2}[.)]\s+", "", d)
    parts, out = re.split(r"(?<=[A-Za-z0-9)])\.\s+(?=[A-Za-z0-9])", d), []
    used = 0
    for part in parts:   # whole sentences until there is enough to say what the job is, and the work itself is named
        used += 1
        part = TAIL.sub("", part).strip(" :-/.,;")
        if part:
            out.append(part.lower() if part.isupper() else part)
        if not whole and len(". ".join(out)) >= 60 and WORK.search(" ".join(out)):
            break
    more = used < len([p for p in parts if TAIL.sub("", p).strip(" :-/.,;")])
    d = ". ".join(x[:1].upper() + x[1:] for x in out) if out else d
    if more and len(d) <= limit:
        d = d.rstrip(".") + "..."
    d = re.sub(r"\b(\d+)\s*du\b", r"\1-unit", d)
    d = ACRONYMS.sub(lambda m: m.group(0).upper(), d)
    d = re.sub(r"^\((\w)", lambda m: "(" + m.group(1).upper(), d)
    if len(d) > limit:
        d = d[:limit].rsplit(" ", 1)[0]
        if d.count("(") > d.count(")"):          # never cut inside parentheses
            d = d[:d.rfind("(")].rstrip()
        d = d.rstrip(" ,;:-&/") + "..."
    d = re.sub(r"\.{3,}$", "...", d)
    return d if re.search(r"[A-Za-z]{3}", d) else "No description in the City record."


SMALL_WORDS = {"AND", "OF", "THE", "FOR", "AT", "BY", "TO", "ON", "IN", "AN", "A"}
WORDS2 = {"TO", "BE", "AN", "ON", "IN", "OF", "BY", "OR", "IS", "IT", "MY", "UP", "SO", "NO", "GO", "DO", "WE", "LO", "DE", "LA", "LE",
          "DI", "DU", "EL", "MC", "ST", "OZ", "YE", "OH", "HO", "AM", "ME", "HE", "CO"}
ONSETS = {"BL", "BR", "CH", "CL", "CR", "DR", "DW", "FL", "FR", "GL", "GR", "GH", "KN", "KR", "PH", "PL", "PR", "PS", "QU", "RH", "SC", "SH", "SK", "SL",
          "SM", "SN", "SP", "SQ", "ST", "SW", "TH", "TR", "TW", "WH", "WR", "SCH", "SCR", "SHR", "SPL", "SPR", "STR", "THR", "CZ", "SZ", "ZB", "ZW", "VL"}
COMMON3 = {"INC", "CO", "LTD", "DBA", "NEW", "ONE", "TWO", "TEN", "OAK", "ELM", "BAY", "SUN", "SKY", "ACE", "ALL", "AIR", "BIG", "TOP", "PRO",
           "ART", "RED", "BEE", "BUY", "EST", "WAY", "KEY", "MAX", "JET", "OWN", "OUR", "DOT", "BOX", "FOX", "HUB", "ARC", "AXE", "LEE", "RAY",
           "KAY", "DON", "JOE", "TOM", "JIM", "BOB", "ROY", "SAM", "DAN", "AVE", "STE", "PLY", "ORR", "LAW", "GEN", "SON", "SONS",
           "THE", "OLD", "TIM", "MID", "AND", "FOR", "ARK", "ELK", "IVY", "OAK", "ASH", "YEW", "INN", "PAN", "ZEN", "EON", "BEN", "KEN", "LEO",
           "RON", "TED", "GUS", "AL", "VAN", "VON", "DEL", "LOS", "SAN", "BAR", "ACT", "AGE", "AIM", "END", "ERA", "EYE", "OWL", "ORE", "ICE",
           "OUT", "ONE", "SIX", "TEN", "TWO", "FIR", "PIN", "RIM", "RUN", "SEA", "BEL", "MAR", "RIO", "TOP", "WIN", "WOW"}
KEEP_UP = {"LLC", "LP", "LLP", "PLLC", "USA", "II", "III", "IV", "JV", "HVAC", "MEP", "GC", "DBA"}


def acronym(bare):
    """True when a word in an all-caps business name is letters to say one by one (MPI, CPMH, FGAC, JC), not a word (Old, Tim, To)."""
    if len(bare) < 2 or not bare.isalpha():
        return False
    if bare in KEEP_UP:
        return True
    if len(bare) == 2:
        return bare not in WORDS2
    if bare in COMMON3:
        return False
    if not re.search(r"[AEIOUY]", bare):
        return True
    if len(bare) == 3:
        return True
    return len(bare) <= 4 and bare[0] not in "AEIOU" and bare[1] not in "AEIOUY" and bare[:2] not in ONSETS and bare[:3] not in ONSETS


def part_acronym(x):
    """One part of a hyphenated name (US-Sino, Thermo-Pol): initials only when two letters or no vowel."""
    b = re.sub(r"[^A-Za-z]", "", x).upper()
    return bool(b) and ((len(b) == 2 and b not in WORDS2) or not re.search(r"[AEIOUY]", b))


def title_name(n):
    out = []
    for w in re.sub(r"\s+", " ", n).strip().split(" "):
        bare = re.sub(r"[^A-Za-z]", "", w).upper()
        if re.fullmatch(r"[A-Za-z]\.?,?", w):
            out.append(w.upper())
        elif out and bare in SMALL_WORDS:
            out.append(w.lower())
        elif re.fullmatch(r"(?:[A-Za-z]\.){2,}", w.strip(",")) or ("-" not in w and acronym(bare)):
            out.append(w.upper())
        elif "-" in w and any(part_acronym(x) for x in w.split("-")):
            out.append("-".join(x.upper() if part_acronym(x) else x.capitalize() for x in w.lower().split("-")))
        else:
            w = re.sub(r"[A-Za-z]+", lambda m: m.group(0).capitalize(), w.lower())
            out.append(re.sub(r"\bMc([a-z])", lambda m: "Mc" + m.group(1).upper(), w))
    s = re.sub(r"\s+,", ",", " ".join(out))
    s = re.sub(r"\b(\d+)(ST|ND|RD|TH)\b", lambda m: m.group(1) + m.group(2).lower(), s, flags=re.I)
    return re.sub(r"(\w)['\u2019]S\b", lambda m: m.group(1) + "'s", s)


def street(r):
    name = re.sub(r"[A-Za-z]+", lambda m: m.group(0).capitalize(), (r.get("street_name") or "").lower())
    name = re.sub(r"(\d)(St|Nd|Rd|Th)\b", lambda m: m.group(1) + m.group(2).lower(), name)
    return " ".join(x for x in [r.get("street_number", ""), r.get("street_direction", ""), name] if x).strip()


def coord(v):
    """A latitude or longitude from the City row, rounded to about a metre, or None when the record has none."""
    try:
        f = round(float(v), 6)
    except (TypeError, ValueError):
        return None
    return f if f else None


def builders(names):
    """Every business the City lists as general contractor, as the list prints them: business names only, each builder
    once, builders before trade contractors. All of them are kept (Holdout, Oct 18: a third contractor such as
    "RD'S HVAC INC" was cut by a two-name cap)."""
    out = []
    for nm in names:
        nm = (nm or "").strip()
        if nm and BUSINESS.search(nm.upper()):
            nm = gc_filter(nm)
            if nm and entity_key(nm) not in [entity_key(g) for g in out]:
                out.append(nm)
    return sorted(out, key=lambda g: bool(TRADE_GC.search(g.upper())))


LEGAL_SUFFIX = [(r"\bL\.?\s?L\.?\s?C\b\.?", "LLC"), (r"\bINCORPORATED\b", "INC"), (r"\bCORPORATION\b", "CORP"),
                (r"\bCOMPANY\b", "CO"), (r"\bLIMITED\b", "LTD")]


def entity_key(n):
    """One key per business as the City lists it: casing, punctuation and the spelling of the legal suffix do not matter
    ("AT MECHANICAL LLC" = "AT Mechanical, L.L.C."; "Acme Inc" = "Acme Incorporated"), but a different suffix is a different
    entity ("PANOPTIC GROUP LLC" is not "PANOPTIC GROUP INCORPORATED"; holdout, Oct 18). Every page, the workbook and the
    builder counts group builders by this key; gc_key below stays the suffix-free key the contacts file uses."""
    u = (n or "").upper()
    for pat, canon in LEGAL_SUFFIX:
        u = re.sub(pat, canon, u)
    return re.sub(r"[^A-Z0-9]", "", u)


def entity_names(projects):
    """{entity_key: the name to print}: the spelling most permits use, then the shortest, then A to Z, so every surface prints
    the same name for a builder whatever order it reads the permits in."""
    seen = collections.defaultdict(collections.Counter)
    for p in projects:
        for g in p.get("gc") or []:
            seen[entity_key(g)][g] += 1
    return {k: sorted(c.items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0]))[0][0] for k, c in seen.items()}


def list_day(iso):
    """The list's date: the Chicago calendar date of the pull (a 02:42 UTC Oct 18 pull is Oct 17 in Chicago), the same on the
    free page, the members' pages and the workbook (holdout, Oct 18)."""
    from zoneinfo import ZoneInfo
    t = dt.datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return t.astimezone(ZoneInfo("America/Chicago")).date()


def gc_key(n):
    return re.sub(r"[^A-Z0-9]", "", re.sub(r"\b(LLC|L\.L\.C|INC|INCORPORATED|CORP|CORPORATION|CO|COMPANY|LTD)\b\.?", "", n.upper()))


def months(days):
    """The window as people say it: 730 days is "24 months", 365 is "12 months"; anything else stays in days."""
    m = round(days / 30.4)
    return f"{m} months" if abs(m * 30.4 - days) <= 4 else f"{days} days"


def slim(k):
    """A kept project as the public free sample shows it: the members' app's whole scope text stays in the paid list."""
    return {x: v for x, v in k.items() if x != "scopeFull"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=DAYS)
    ap.add_argument("--min-cost", type=int, default=500000)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--full", default="", help="also write every kept project to this path (the paid weekly list; never inside the repo's committed folders)")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)

    meta = get(f"{PORTAL}/api/views/{DATASET}.json")
    cols = [c.get("fieldName") for c in meta.get("columns", [])]
    upd = meta.get("rowsUpdatedAt") or meta.get("viewLastModified")
    upd_iso = dt.datetime.fromtimestamp(upd, dt.timezone.utc).isoformat(timespec="seconds") if upd else ""
    need = {"issue_date", "permit_type", "work_description"}
    missing = sorted(need - set(cols))
    if missing:
        raise SystemExit(f"dataset columns changed, missing {missing}; columns: {cols}")
    cost_col = "reported_cost" if "reported_cost" in cols else None

    since = window_start(now, a.days)
    where = (f"issue_date >= '{since}' AND permit_type in('PERMIT - NEW CONSTRUCTION','PERMIT - RENOVATION/ALTERATION')"
             + (f" AND {cost_col} >= {a.min_cost}" if cost_col else ""))
    def pull(w):
        out, offset = [], 0
        while True:
            page = get(f"{PORTAL}/resource/{DATASET}.json", {"$where": w, "$order": "issue_date DESC", "$limit": 5000, "$offset": offset})
            out += page
            if len(page) < 5000 or offset > 50000:
                return out
            offset += 5000

    try:
        rows = pull(where)
    except SystemExit:
        # reported_cost stored as text in some vintages: pull without the cost test and apply it here
        where = f"issue_date >= '{since}' AND permit_type in('PERMIT - NEW CONSTRUCTION','PERMIT - RENOVATION/ALTERATION')"
        rows = [r for r in pull(where) if cost_col and float(r.get(cost_col) or 0) >= a.min_cost]

    areas = {}
    for params in ({"$select": "area_numbe,community", "$limit": 200}, {"$limit": 200}):
        try:
            areas = {str(int(float(r.get("area_numbe") or r.get("area_num_1") or 0))): (r.get("community") or "").title()
                     for r in get(f"{PORTAL}/resource/{AREAS}.json", params, tries=2)}
            break
        except SystemExit:
            continue

    ctype = collections.Counter(); ptype = collections.Counter(); reasons = collections.Counter()
    kept = []
    status = collections.Counter(); milestone = collections.Counter()
    for r in rows:
        ptype[r.get("permit_type", "")] += 1
        status[r.get("permit_status") or ""] += 1
        milestone[r.get("permit_milestone") or ""] += 1
        if not in_window(r, since):
            reasons["closed, complete or suspended" if (r.get("permit_status") or "").upper() in CLOSED else
                    f"status not open ({r.get('permit_status') or 'blank'})" if (r.get("issue_date") or "")[:19] >= since else "issued before the window"] += 1
            continue
        desc = (r.get("work_description") or "").upper().replace("\u00bf", " ")
        maxu = unit_count(desc)
        ok, why = decide(desc, r.get("permit_type") or "")
        if not ok:
            reasons[why] += 1; continue
        names = []
        for n in range(1, 16):
            t = (r.get(f"contact_{n}_type") or "").upper()
            if t:
                ctype[t] += 1
            if "GENERAL CONTRACTOR" in t and "OWNER" not in t:
                names.append(r.get(f"contact_{n}_name") or "")
        gcs = builders(names)   # the builder first, trade contractors after
        if not gcs:
            reasons["no business listed as general contractor"] += 1; continue
        addr = street(r)
        ca = str(r.get("community_area") or "").split(".")[0]
        cost = float(r.get(cost_col) or 0) if cost_col else 0
        kept.append({
            "permit": r.get("permit_") or r.get("permit_number") or r.get("id"),
            "issued": (r.get("issue_date") or "")[:10],
            "type": "New construction" if "NEW CONSTRUCTION" in (r.get("permit_type") or "") else "Renovation",
            "scope": clean_scope(r.get("work_description")),
            "scopeFull": clean_scope(r.get("work_description"), limit=1200, whole=True),
            "units": unit_count(desc, display=True) or None,
            "cost": round(cost),
            "address": addr,
            "communityArea": AREA_NAMES.get(areas.get(ca, ""), areas.get(ca, "")),
            "status": (r.get("permit_status") or "").title(),
            "milestone": (r.get("permit_milestone") or "").title(),
            "gc": gcs,
            "lat": coord(r.get("latitude")), "lon": coord(r.get("longitude")),
            "_rev": [x for m in re.finditer(r"REVISIONS? (?:TO|OF) (?:THE )?(?:[A-Z&]+ ){0,4}PERMITS?[:#\s]*((?:#?10\d{7}[,\s]*(?:AND\s*)?)+)", desc)
                     for x in re.findall(r"10\d{7}", m.group(1))],
        })
    # a revision of a permit that is also on the list is the same job: count it once (Holdout QC Oct 17, third pass)
    ids = {str(k["permit"]) for k in kept}
    dup = [k for k in kept if any(x in ids and x != str(k["permit"]) for x in k["_rev"])]
    reasons["revision of a permit already listed"] += len(dup)
    kept = [k for k in kept if k not in dup]
    for k in kept:
        k.pop("_rev", None)
    kept.sort(key=lambda x: (-x["cost"], x["issued"]))
    by_area = collections.Counter(k["communityArea"] for k in kept if k["communityArea"])
    gc_n, gc_cost, gc_name = collections.Counter(), collections.Counter(), {}
    for k in kept:
        g = k["gc"][0]; key = entity_key(g)
        gc_n[key] += 1; gc_cost[key] += k["cost"]; gc_name.setdefault(key, g)
    top_gcs = [{"name": gc_name[key], "projects": n, "cost": gc_cost[key]} for key, n in
               sorted(gc_n.items(), key=lambda kv: (-kv[1], -gc_cost[kv[0]]))[:12]]
    sample = {
        "source": {
            "name": "City of Chicago Data Portal, Building Permits", "url": DATASET_PAGE, "rowsUpdatedAt": upd_iso,
            "fetchedAt": now.isoformat(timespec="seconds"),
            "modified": (f"Filtered by ProofNotFluff: permits issued in the last {months(a.days)}, new construction or renovation, "
                         f"reported cost ${a.min_cost:,} or more, still open (City status Active or Phased Permitting; complete, suspended, cancelled, revoked and expired permits left out), "
                         "apartment buildings of 4+ units or commercial work, with a business listed as general contractor; work that never needs "
                         "a construction clean under its permit (foundation, superstructure, caisson, demolition, roof, facade, mechanical, equipment or site work only) "
                         "left out; cleaning companies listed as contractor left out; a revision of a permit already on the list counted once; "
                         "only project-level and business fields kept."),
            "terms": TERMS_URL,
        },
        "window": {"from": since[:10], "to": now.strftime("%Y-%m-%d")},
        "counts": {"fetched": len(rows), "kept": len(kept), "excluded": dict(reasons),
                   "keptByType": dict(collections.Counter(k["type"] for k in kept)),
                   "keptCost": sum(k["cost"] for k in kept), "keptUnits": sum(k["units"] or 0 for k in kept if k["type"] == "New construction"),
                   "topAreas": by_area.most_common(8), "topGCs": top_gcs,
                   "nearFinish": sum(1 for k in kept if "OCCUPANCY PENDING" in k["milestone"].upper() or "PARTIAL OCCUPANCY" in k["milestone"].upper())},
        "projects": [slim(k) for k in kept[: a.top]],
        "nearFinish": [slim(k) for k in kept if "OCCUPANCY PENDING" in k["milestone"].upper() or "PARTIAL OCCUPANCY" in k["milestone"].upper()][:10],
    }
    profile = {"fetchedAt": sample["source"]["fetchedAt"], "rowsUpdatedAt": upd_iso, "columns": cols,
               "permitTypes": dict(ptype), "contactTypes": dict(ctype.most_common(40)),
               "statuses": dict(status.most_common()), "milestones": dict(milestone.most_common(30)),
               "license": (meta.get("license") or {}).get("name", ""), "attribution": meta.get("attribution", ""),
               "where": where}
    json.dump(sample, open(os.path.join(OUT, "sample.json"), "w"), indent=1)
    json.dump(profile, open(os.path.join(OUT, "profile.json"), "w"), indent=1)
    try:
        open(os.path.join(OUT, "source-terms.txt"), "w").write(terms_text())
    except SystemExit as e:
        open(os.path.join(OUT, "source-terms.txt"), "w").write(f"Could not fetch {TERMS_URL}: {e}\n")
    if a.full:
        week = (now - dt.timedelta(days=7)).strftime("%Y-%m-%d")
        for k in kept:
            k["newThisWeek"] = k["issued"] >= week
        kept_ids = {str(k["permit"]) for k in kept}
        review = []   # every open candidate with the City's own text, so the filter can be tested offline (Holdout QC Oct 17)
        for r in rows:
            if not in_window(r, since):
                continue
            pid = str(r.get("permit_") or r.get("permit_number") or r.get("id"))
            review.append({"permit": pid, "kept": pid in kept_ids, "raw": r.get("work_description") or "",
                           "cost": float(r.get(cost_col) or 0) if cost_col else 0, "type": r.get("permit_type"),
                           "gcRaw": [r.get(f"contact_{n}_name") for n in range(1, 16)
                                     if "GENERAL CONTRACTOR" in (r.get(f"contact_{n}_type") or "").upper()],
                           # the City's contact type for each gcRaw name: an owner acting as general contractor is never listed
                           "gcType": [(r.get(f"contact_{n}_type") or "").title() for n in range(1, 16)
                                      if "GENERAL CONTRACTOR" in (r.get(f"contact_{n}_type") or "").upper()],
                           # enough of the City row to rebuild the whole list offline (no person's name: contacts are GC businesses only)
                           "issued": (r.get("issue_date") or "")[:10], "address": street(r), "status": (r.get("permit_status") or "").title(),
                           "milestone": (r.get("permit_milestone") or "").title(),
                           "communityArea": AREA_NAMES.get(areas.get(str(r.get("community_area") or "").split(".")[0], ""),
                                                           areas.get(str(r.get("community_area") or "").split(".")[0], "")),
                           "lat": coord(r.get("latitude")), "lon": coord(r.get("longitude"))})
        json.dump({"source": sample["source"], "window": sample["window"], "counts": sample["counts"], "projects": kept,
                   "review": review}, open(a.full, "w"), indent=1)
    print(json.dumps({"fetched": len(rows), "kept": len(kept), "excluded": dict(reasons), "top3": [(k["cost"], k["type"], k["communityArea"]) for k in kept[:3]]}))


# Work a cleaner gets hired for: new buildings and interior finish work (Holdout QC Oct 17, second pass: a permit must
# show this, not merely avoid an exclusion word; roofs, facades, risers, rooftop units, site work and similar fail it).
NEW_BUILDING = re.compile(r"\bERECT|NEW CONSTRUCTION|NEW (?:FREESTANDING |GROUND[- ]UP )?(?:\d+|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN)[- ]?\(?\d*\)?[- ]?STOR|"
                          r"NEW (?:FREESTANDING |GROUND[- ]UP )?(?:BUILDING|STRUCTURE|HOTEL|APARTMENT|RESIDENTIAL|MIXED[- ]USE|COMMERCIAL|OFFICE|SCHOOL|WAREHOUSE|RESTAURANT)|"
                          r"FULL BUILDING|SUPERSTRUCTURE|ADDITION (?:OF|TO) (?:AN? |THE )?|STORY (?:\w+ ){0,3}ADDITION|BUILDOUT OF ALL FLOORS|CORE (?:AND|&) SHELL|"
                          # holdout, Oct 18: a constructed addition, a proposed building, a new named building
                          r"\bCONSTRUCT\w*\s+(?:AN?\s+)?[^.;]{0,50}?\b(?:STORY|STOREY|FLOOR|DWELLING|MASONRY)\b[^.;]{0,40}?\bADDITION\b|"
                          r"\bPROPOSED (?:NEW )?(?:(?!TO\b|FOR\b|AT\b|OF\b|IN\b|ON\b|WITH\b|AND\b)[\w,'-]+ ){0,5}(?:BUILDING|DEVELOPMENT|CAR ?WASH)\b|"
                          r"\bTWO[- ]TENANT BUILDING|\bNEW (?:(?!TO\b|FOR\b|AT\b|OF\b|IN\b|ON\b|WITH\b|AND\b)[\w,'-]+ ){0,4}(?:BUILDING|FACILITY|CAR ?WASH|FIELDHOUSE|TOWN ?(?:HOUSE|HOME)S)\b|"
                          r"\bCONSTRUCTION OF (?:AN? )?(?:NEW )?(?:[\w,'-]+ ){0,3}(?:BUILDING|STATION|FACILITY)\b|\bCONSTRUCT \d+ TOWN ?(?:HOUSE|HOME)")
WORK_WORD = r"(?:ALTERATION|ALTERNATION|ATERATION|RENOVATION|RENO\b\.?|REMODEL(?:ING)?|REHAB(?:ILITATION)?|MODIFICATION|BUILD[- ]?OUT|BUILDING OUT|FIT[- ]?OUT|IMPROVEMENT|FINISHES|UPGRADE|RETROFIT)S?"
ROOM_WORD = (r"(?:OFFICE|RETAIL|RESTAURANT|SPACE|TENANT|SUITE|FLOOR|LEVEL|CLINIC|STORE|BANK|SCHOOL|CLASSROOM|LAB|LABORATORY|APARTMENT|BUILDING|"
             r"D\.?U\.?|DWELLING|UNITS|HOTEL|GYM|GYMNASIUM|FITNESS|BATHROOM|RESTROOM|TOILET|KITCHEN|LOBBY|CORRIDOR|AMENITY|EXAM|ROOMS|CAFE|BAR|"
             r"CHURCH|LIBRARY|THEATER|THEATRE|WAREHOUSE|DAY ?CARE|CENTER|FACILITY|SHOWROOM|STUDIO|SALON|HOSPITAL|PAVILION|WING|BASEMENT)")
INTERIOR = re.compile(r"\bINT(?:ERIOR)?\.?(?: AND EXT(?:ERIOR)?\.? | & EXT(?:ERIOR)?\.? |/EXTERIOR | )" + WORK_WORD + r"|" + WORK_WORD + r" (?:OF|TO|FOR|IN|WITHIN|AT|ON) (?:AN? |THE )?INTERIOR|"
                      r"INTERIOR (?:ARCHITECTURAL|DEMOLITION AND|FINISH)|NEW INTERIOR|TENANT IMPROVEMENT|WHITE[- ]?BOX|GUT REHAB|\bREHAB\b|CONVER(?:T|TS|TED|TING|SION)\b|ADAPTIVE REUSE|"
                      r"CHANGE OF (?:USE|OCCUPANCY)|NEW FINISHES|NEW PARTITIONS|BUILD[- ]?OUTS?\b|FIT[- ]?OUTS?\b|"
                      + WORK_WORD + r"\b[^.;]{0,80}?\b" + ROOM_WORD + r"S?\b|" + ROOM_WORD + r" (?:SPACE )?" + WORK_WORD)
TRADE_ONLY_WORK = re.compile(r"(?:MECHANICAL|ELECTRICAL|PLUMBING|STRUCTURAL|FACADE|ROOF|ROOFING|EXTERIOR|MASONRY|FIRE|SPRINKLER|HVAC|ELEVATOR|M\.?E\.?P\.?)"
                             r"(?: (?:AND|&) (?:MECHANICAL|ELECTRICAL|PLUMBING|STRUCTURAL|FIRE PROTECTION))* " + WORK_WORD + r"|"
                             r"(?:ELECTRICAL|MECHANICAL|DATA|SERVER|UPS|TELECOM|SWITCHGEAR|BOILER|PUMP|MER|PRE-ACTION) ROOMS?")
WASTED = re.compile(r"(?:MECHANICAL|ELECTRICAL|PLUMBING|MEP)[\w ,&]{0,40}DEMOLITION|REPLAC\w* ROOFS?\b|ROOF DRAINS|INFRASTRUCTURE (?:UPGRADES|WORK)|"
                    r"ELECTRICAL (?:POWER )?OUTLETS|\bMER ROOMS?|PRE-ACTION ROOMS?|REPLACEMENT ONLY|ROOF (?:TEAR[- ]OFF|REPLACEMENT)|FULL ROOF|RISERS?\b|ROOF[- ]?TOP (?:UNITS|HVAC|MAKE[- ]?UP)|\bRTUS?\b|"
                    r"CHILLER|BOILER|HEAT EXCHANGER|COOLING TOWER|AIR HANDL|MAKE[- ]?UP AIR|SOLAR|PHOTOVOLTAIC|PANELS|WASTEWATER|FIRE (?:SUPPRESSION|ALARM|PUMP)|"
                    r"SPRINKLER|ELECTRICAL SERVICE|COMED|SWITCHGEAR|GENERATOR|\bUPS\b|DATA CLOSET|CURTAIN ?WALL|FA[CÇ]ADE|WINDOWS?\b|STOREFRONT|"
                    r"TUCKPOINT|MASONRY REPAIR|STRUCTURAL REINFORCEMENT|DOOR REPLACEMENT|LANDSCAP|PLAYGROUND|TURF|SPORT FIELD|PLAY AREA|OPEN SPACE|SENSORY GARDEN|"
                    r"FLATWORK|RETAINING WALL|RIVERWALK|PARKING LOT|WATER ?MAIN|VALVES|PIPING|INTERIOR DEMOLITION|DEMOLITION OF|ANTENNA|SIGNAGE|ELEVATOR MODERNI|"
                    r"ELECTRICAL ROOM|DATA CENTER|EXTERIOR WALLS|REFRIGERATION PLANT|HEATING PLANT|CENTRAL PLANT|\bMRI\b|GRADE BEAMS|UNDERGROUND UTILITIES")
SITE_START = re.compile(r"^(?:[^:]{0,40}:\s*)?(?:NEW |PROPOSED )?(?:SHALLOW |MAT )?(?:FOUNDATI?ONS?|FOUNDATIN|CAISSONS?|PILES?|PILING|EARTH RETENTION|EXCAVATION|SHORING|RETAINING WALLS?|"
                        r"(?:INTERIOR )?DEMOLITION|WRECKING|LANDSCAP\w*|(?:ACCESSORY )?(?:SURFACE )?PARKING LOT|SITE WORK|RIVERWALK|PARK\b)")
SINGLE_HOME = re.compile(r"SINGLE[- ]FAMILY|\bSFR\b|SINGLE (?:RESIDENTIAL|DWELLING|CONDO\w*) UNIT|CONDO(?:MINIUM)? (?:RESIDENCE )?UNIT|"
                         r"(?:RESIDENTIAL|CONDO\w*|DWELLING) (?:UNITS? |RESIDENCE UNIT )\d{3,5}\b|\bUNIT\s*#?\s*\d{3,5}\b|"
                         r"SUITE\s*#?\s*\d{3,5}\b[^.]{0,60}RESIDENTIAL|RESIDENTIAL[^.]{0,60}SUITE\s*#?\s*\d{3,5}\b|APARTMENT\s*#\s*\d|PENTHOUSE (?:UNIT|RESIDENCE)|"
                         r"\b(?:ONE|1|A) (?:\(1\) )?(?:\d[- ]BEDROOM )?(?:CONDO\w*|RESIDENCE\b|DWELLING UNIT)|COMBINE\w* (?:TWO|2|\(2\)) (?:\w+ )?UNITS INTO|"
                         r"\d[- ]STORY (?:SINGLE[- ]FAMILY )?RESIDENCE|ENLARGE THE KITCHEN|\d[- ]BEDROOM[^;]{0,40}CONDO|CONDOMINIUM ON (?:THE )?\d+(?:ST|ND|RD|TH) FLOOR|"
                         r"(?:RESIDENTIAL )?UNITS \d{3,5}[A-Z]? (?:AND|&) \d{3,5}|COMBINATION OF UNITS|\bUNIT \w{1,5} ONLY\b")


def scope_start(d):
    d = re.sub(r"^\W*\((?:[^)]{0,60})\)\s*", "", d)   # a leading "(DIRECT DEVELOPER SERIVCES / 2019 CBRC)" with the City's typos
    return PREFIX.sub("", re.sub(r"^\W+", "", d)).strip(" :-/.,()")


ACTION = re.compile(r"\b(?:INTERIOR\b|ALTER|ALTERN|RENOVAT|REMODEL|REHAB|MODIF|BUILD[- ]?OUT|FIT[- ]?OUT|FINISH[- ]?OUT|IMPROVEMENT|UPGRADE|ERECT|NEW\b|"
                    r"CONSTRUCT(?!ION (?:TYPE|CLASS))|CONVER|INSTALL|REPLAC|REMOVE|REPAIR|PROVID|ADD\b|ADDITION|DEMOLI|ENLARGE|EXPAN|RECONFIG|COMPLETE|FULL BUILDING|FOUNDATI|"
                    r"OCCUPANCY CHANGE|CHANGE OF (?:USE|OCCUPANCY)|ADAPTIVE REUSE)")
STRONG_INTERIOR = re.compile(r"(?<!SELECTIVE )\bINT(?:ERIOR)?\.?(?: AND EXT(?:ERIOR)?\.? | & EXT(?:ERIOR)?\.? |/EXTERIOR | )(?:ALTERATION|ALTERNATION|ATERATION|RENOVATION|RENO\b|REMODEL|BUILD[- ]?OUT|"
                             r"BUILDING OUT|FIT[- ]?OUT|FINISH|RETROFIT|"
                             r"IMPROVEMENT|WORK|REHAB|REPAIRS? (?:&|AND) MODIFICATION|ARCHITECTURAL)|BUILD[- ]?OUTS?\b|FIT[- ]?OUTS?\b|FINISH[- ]?OUT|"
                             r"TENANT (?:IMPROVEMENT|SPACE|SUITE)|WHITE[- ]?BOX|GUT REHAB|\bREHAB\b|CONVER(?:T|TS|TED|TING|SION)\b|CHANGE OF (?:USE|OCCUPANCY)|"
                             r"OCCUPANCY CHANGE|ADAPTIVE REUSE|"
                             r"FIRE (?:DAMAGE|RESTORATION|REPAIR)|GUT RENOVATION|REPAIRS TO FIRE|NEW (?:ADU|ACCESSORY DWELLING|DWELLING UNIT)|NEW INTERIOR|NEW PARTITIONS|"
                             r"(?:ENLARGE|EXPAN\w*|RECONFIGUR\w*)\b[^.]{0,40}\b(?:SPACE|LAB|OFFICE|CLINIC|SUITE|AREA|FLOOR|SYNAGOGUE|CHURCH)|"
                             r"\bACCESSIBILITY (?:AND \w+ )?(?:UPDATES|UPGRADES|IMPROVEMENTS|ALTERATIONS)\b|\b\w+ FLOOR ADDITION\b|"
                             r"(?:RENOVATION|REMODEL\w*|ALTERATIONS?|ALTERNATIONS?|MODIFICATIONS?|REPAIRS?)\b[^.]{0,50}\b(?:APARTMENTS?|D\.?U\b|DWELLING|UNITS|"
                             r"OFFICE|RETAIL|RESTAURANT|TENANT|SUITE|CLINIC|CLASSROOM|BATHROOM|RESTROOM|TOILET ROOMS?|KITCHEN|EXAM ROOMS|LOBBY|CORRIDOR|"
                             r"AMENITY|GYM|FITNESS|HOTEL ROOMS|GUEST ROOMS|STORE|BANK|SALON|STUDIO|SHOWROOM|LAB\b|LABORATORY)|"
                             # holdout, Oct 18: renovation or alteration of whole rooms and buildings a cleaner is hired for (not repairs)
                             r"(?:RENOVATIONS?|REMODEL\w*|ALTERATIONS?|ATERATIONS?)\b[^.]{0,110}?\b(?:APARTMENTS|HOUSING UNITS|CLASSROOMS?|TOILETS|CHURCH|SYNAGOGUE|"
                             r"SANCTUARY|MUSEUM|GALLERY|CONCOURSE|TERMINAL|LOCKER ROOMS?|CONFERENCE|HEALTH CLUB|MALL|COMMON AREAS?|POOL DECK|DINING|SURGERY|BANKING|"
                             r"CEILINGS|SPACES? ON|INSTITUTIONAL|SHELL SPACE|COMMERCIAL SPACE|(?:TRANSIT|COMMUTER ?RAIL|METRA|RAIL) STATION)\b|INTERIOR DEMOLITION,? (?:AND )?RENOVATION|"
                             r"\bINTERIOR CHANGES ON (?:LEVELS|FLOORS)|"
                             r"(?:OFFICE|RETAIL|RESTAURANT|TENANT|CLINIC|CLASSROOM|LAB|AMENITY|LOBBY|STORE|BATHROOM|TOILET)(?: ROOMS?)?(?: SPACE)? "
                             r"(?:RENOVATION|ALTERATION|IMPROVEMENT|REMODEL|REPAIRS)")
TRADE_NOUN = (r"(?:FIRE(?![- ]?DAMAG| RESTOR)|HVAC|MECHANICAL|ELECTRICAL|SPRINKLER|PLUMBING|RISERS?|ROOF|ROOFTOP|MAKE[- ]?UP|BOILER|CHILLER|WINDOWS?|DOORS?|ESCALATORS?|"
              r"FA[CÇ]ADE|STOREFRONT|ELEVATOR|EXTERIOR|HEATING|COOLING|SOLAR|GENERATOR)")
PURPOSE_TRADE = re.compile(r"TO ACCOMM?ODATE (?:THE |A )?(?:NEW |REPLACEMENT OF |INSTALLATION OF )*(?:FIRE|HVAC|MECHANICAL|ELECTRICAL|SPRINKLER|PLUMBING|RISER)|"
                           r"TO INCLUDE (?:\w+ ){0,6}ELECTRICAL SERVICE|(?:ALTERATIONS?|WORK)(?: PERMIT)? (?:TO|FOR) (?:REPLACE|INSTALL|UPGRADE)\b[^.]{0,40}" + TRADE_NOUN + r"|"
                           # holdout, Oct 18: alterations whose purpose is structure, equipment or a utility
                           r"(?:TO INCLUDE|(?:ALTERATIONS?|WORK) FOR) (?:\w+ ){0,2}STRUC\w* (?:REPAIRS|UPGRADES)|DUE TO (?:\w+ ){0,2}(?:ELECTRICAL|MECHANICAL|STRUCTURAL)|"
                           r"FOR (?:A )?NEW COMED|COMED VAULT|FOR RELOCATION OF (?:EXISTING )?(?:UPS|ELECTRICAL|MECHANICAL|SERVER|DATA)|(?:REQUIRED )?FOR THE (?:\w+ )?ELEVATOR MODERNI|"
                           r"TO INCLUDE (?:THE )?INSTALLATION OF (?:A )?NEW ELEVATOR|FOR INSTALLATION OF (?:\w+ ){0,2}ELECTRICAL|"
                           r"^(?:[\w,-]+ ){0,3}(?:ALTERATIONS?|RENOVATION|IMPROVEMENTS?|REPAIRS?|UPGRADES?|(?:REPAIR AND )?REPLACEMENT) (?:TO|OF|FOR|AT) (?:THE |AN? )?"
                           r"(?:EXISTING )?(?:FULL )?" + TRADE_NOUN)
TRADE_WORK = re.compile(r"^(?:\w+ ){0,3}(?:EXTERIOR|LANDSCAPE|FLATWORK|SITE|ROOF|FA[CÇ]ADE|STOREFRONT|M\.?E\.?P\.?|MECHANICAL|ELECTRICAL|PLUMBING|STRUCTURAL|FIRE PROTECTION)"
                        r"(?: (?:AND|&) (?:\w+ )?\w+)* (?:ALTERATION|RENOVATION|IMPROVEMENT|UPGRADE|REPAIR|MODIFICATION|WORK)S?")
SITE_NEW = re.compile(r"NEW CONSTRUCTION OF (?:AN? |THE )?(?:\w+ )?(?:OPEN SPACE|PARK|PLAYGROUND|PLAZA|PARKING|SURFACE|FIELD|LANDSCAP|COURT|TRACK|SIGN|FENCE)|"
                      r"ROOF REPLACEMENT|REPLACEMENT OF (?:THE )?ROOF|VEHICLE STORAGE GARAGE|UTILITY PLANT|CENTRAL PLANT|\bTUNNEL\b")
# a parking lot or garage counts as the subject only when the scope names no building of people's use (holdout, Oct 18)
SITE_SOFT = re.compile(r"PARKING LOT|PARKING GARAGE|STORAGE GARAGE|OCCUPANCY(?: GROUP)?:? U\b")
PEOPLE_BUILDING = re.compile(r"\bBUILDING\b(?! SYSTEMS)|DWELLING|\bD\.?U\b|RESIDENTIAL|RELIGIOUS|RETAIL|OFFICE|HOTEL|SCHOOL|STORE|MART|CAR ?WASH|ASSEMBLY|"
                             r"HOUSING|APARTMENT|TOWN ?(?:HOUSE|HOME)|STATION")
ADD_BUILDING = re.compile(r"\bADD (?:A |AN )?(?:NEW )?\(?\d+\)?[- ]STOR")
# third holdout pass, Oct 17: structure-only phases, equipment rooms and equipment installs, washer hookups, parks and memorials
STRUCTURE_ONLY = re.compile(r"FOUNDATION\s*(?:AND|&|/)\s*SUPERSTRUCTURE|SUPERSTRUCTURE (?:PERMIT )?(?:ONLY|THROUGH|UP TO|TO LEVEL)|"
                            # holdout, Oct 18: below-grade, earth-retention and structural phases, and tunnels
                            r"^(?:NEW CONSTRUCTION[,.]?\s*)?(?:EX/ERS|ERS|TIEBACKS?|SHEET PILES?|EARTH RETENTION|GRADE BEAMS|SLAB ON GRADE|(?:\w+ )?SUBSTRUCTURE|"
                            r"(?:INSTALLATION OF )?AGGREGATE PIERS|BELOW[- ]GRADE CONSTRUCTION|FOUNDATION TO LEVEL|FULL BUILDING PERMIT FOR THE CONFINED SPACES)\b")
# structural work named anywhere in the permit (a revision of caissons, structural-only repairs) unless the scope names interior work
STRUCTURE_ANY = re.compile(r"\b(?:STRUCTURAL REVISIONS|STRUCTURAL ONLY|REPAIRS ONLY|CAISSONS FROM|TIEBACKS|SHEET PILES|SUPER-STRUCTURE PERMIT FOR FLOORS|"
                           r"SUPERSTRUCTURE ONLY)\b")
EQUIPMENT = re.compile(r"PROCESS EQUIPMENT|\bCT (?:SCANNER|EQUIPMENT)|SALES DISPLAY FIXTURES|\bREFLOW\b|UTILITY PLANT|CENTRAL PLANT|CONVEYORS?\b|CRYO ?PLANT|AUTOMATION EQUIPMENT|INSTALLATION OF (?:A )?NEW [\d,]+ ?(?:SQ\.? ?FT\.?|SF) (?:COOLER|FREEZER)|"
                       r"(?:COOLER|FREEZER) IN (?:AN? |THE )?EXISTING WAREHOUSE|IN-UNIT WASHER|WASHER ?/ ?DRYER|"
                       r"(?:BUILD[- ]?OUT|REMODEL|RENOVATION|ALTERATIONS?) (?:OF|TO) (?:THE )?(?:EXISTING )?(?:\w+ )?(?:MECHANICAL|ELECTRICAL|UPS|SERVER|TELECOM|PUMP|BOILER) ROOMS?|"
                       r"\(UPS\) ROOM|UNINTERRUPTIBLE POWER|DATA CENTER\b[^.]{0,80}(?:AHUS?|CRAH|CHILLERS?|COOLING|ELECTRICAL ROOMS?)|"
                       r"(?:AHUS?|CRAH|CHILLERS?|COOLING|ELECTRICAL ROOMS?)\b[^.]{0,120}DATA CENTER|"
                       r"TO MAKE STRU\w* REPAIRS|REPAIR (?:EXISTING )?DOCKS|M\.?E\.?P\.? IMPROVEMENTS|BUILD[- ]?OUT (?:WILL BE |TO BE )?(?:UNDER|BY) (?:A )?SEPARATE PERMIT")
PARK = re.compile(r"LANDSCAPED PARK|CONCRETE MEMORIAL|MEMORIAL (?:PARK|PLAZA|GARDEN|WALL)|AMPHITHEATER")


def decide(d, ptype=""):
    """(keep?, reason) for one permit's description. Judged on the main scope clause (the first one that names work),
    so building context ("3 STORY BUILDING.") and side notes do not decide it. Used by main(), the selftest and the
    offline review set."""
    d = d.upper().replace("\u00bf", " ").replace("M.E.P.", "MEP")
    d = OTHER_PERMIT.sub(" ", d)   # another permit's caissons, piles or demolition never decide this one (holdout, Oct 18)
    u = unit_count(d)
    sleeping = max([int(x) for x in SLEEPING.findall(numerals(d))] or [0])   # a shelter or group home of 4+ sleeping units: commercial scale
    small_units = {int(x) for x in re.findall(r"\bUNIT\s*#?\s*(\d)\b", d)}
    mixed = re.search(r"MIXED[- ]USE|COMMERCIAL|RETAIL|OFFICE|RESTAURANT", d)
    if sleeping < 4 and ((u and u < 4 and not (mixed and u == 1)) or (not u and (RESIDENTIAL_SMALL.search(d) or FLAT_UNITS.search(d) or re.search(r"\bR-?5\b", d)
                                    or (small_units and max(small_units) <= 3)))):
        return False, "house or 2 to 3 flat"
    m = SINGLE_HOME.search(d)
    if (m and (u < 4 or re.search(r"\d{3,5}|\d[A-Z]{1,3}\b|CONDO|BEDROOM|COMBIN|PENTHOUSE|APARTMENT\s*#|ONLY", m.group(0)))) or ONE_UNIT_WORK.search(d) \
            or (ONE_UNIT_PLAIN.search(d) and re.search(r"\bR-?2\b|RESIDENTIAL|CONDO", d)):
        return False, "one home inside a larger building"
    strong = COMMERCIAL.search(d) or COMMERCIAL2.search(d) or OCCUPANCY.search(d) or sleeping >= 4
    if not u and not strong and not (WEAK_COMMERCIAL.search(d) and not HOUSE.search(d)):
        return False, "no commercial or apartment wording"
    if not u and re.search(r"\b[1-3][- ]STORY WALK[- ]?UP\b", d) and not re.search(r"CONVER|MIXED|COMMERCIAL|RETAIL|OFFICE", d):
        return False, "apartment building with no unit count (could be a 2 or 3 flat)"
    start = scope_start(d)
    clauses = [c for c in re.split(r"(?<=[A-Z0-9)])\.\s+|;\s*", start) if c.strip()]
    i = next((k for k, c in enumerate(clauses) if ACTION.search(c)), 0)
    main = clauses[i] if clauses else start
    if len(main) < 25 and i + 1 < len(clauses):   # "NEW CONSTRUCTION." then the actual scope
        main = main + ". " + clauses[i + 1]
    if re.search(r"\bREVISION\b[^.]{0,60}\bTO DELETE\b", d):
        return False, "no construction clean (foundation, demolition, roof, mechanical or site work only)"
    if re.search(r"CORE (?:&|AND) SHELL IMPROVEMENTS", main) and not re.search(r"BUILD[- ]?OUT|TENANT IMPROVEMENT|FINISH", main):
        return False, "no construction clean (foundation, demolition, roof, mechanical or site work only)"
    if STRUCTURE_ONLY.search(main) or (STRUCTURE_ANY.search(d) and not STRONG_INTERIOR.search(main)) or ((EQUIPMENT.search(d) or PARK.search(main)) and not NEW_BUILDING.search(main)):
        return False, "no construction clean (foundation, demolition, roof, mechanical or site work only)"
    if ONLY_TRADE.search(d) or (SITE_START.search(main) and not re.search(r"SUPERSTRUCTURE|FULL BUILDING|(?:AND|,)\s*(?:NEW )?(?:BUILD|RENOVAT|ALTERAT|REMODEL)", main)):
        return False, "no construction clean (foundation, demolition, roof, mechanical or site work only)"
    if STRONG_INTERIOR.search(main) and not PURPOSE_TRADE.search(main):
        return True, "kept"
    new_bldg = (("NEW CONSTRUCTION" in (ptype or "").upper() or NEW_BUILDING.search(main) or ADD_BUILDING.search(main)) and not SITE_NEW.search(main)
                and not (SITE_SOFT.search(main) and not (PEOPLE_BUILDING.search(main) or COMMERCIAL.search(main) or COMMERCIAL2.search(main))))
    if new_bldg:
        return True, "kept"
    if WASTED.search(main) or PURPOSE_TRADE.search(main) or TRADE_WORK.search(main) or TRADE_ONLY_WORK.search(main):
        return False, "no construction clean (foundation, demolition, roof, mechanical or site work only)"
    if INTERIOR.search(d) and not (WASTED.search(d) and not STRONG_INTERIOR.search(d)):
        return True, "kept"
    return False, "no interior finish work or new building named"


FILTER_CASES = [  # planted cases from the Oct 17 holdout QC: (description, keep?, homes or None)
    ("COMPLETE RENOVATION AND CONVERSION OF EXISTING 3-STORY MASONRY CHURCH BUILDING TO (6) RESIDENTIAL UNITS", True, 6),
    ("BUILDOUT OF ALL FLOORS FOR NEW 9 STORY RESIDENTIAL BUILDING WITH 101 STANDARD DWELLING UNITS 48 EFFICIENCY UNITS", True, 149),
    ("REMOVAL AND REPLACEMENT OF THREE (3) AIR HANDLING UNITS AT 2ND FLOOR MECHANICAL SPACE AT EXISTING HOSPITAL", False, None),
    ("INTERIOR ALTERATIONS TO EXISTING FITNESS CENTER (5TH FLOOR) IN EXISTING 5-STORY BUILDING", True, None),
    ("ERECT NEW 3 STORY 4 UNIT RESIDENTIAL BUILDING WITH NEW 5 CAR DETACHED GARAGE", True, 4),
    ("INTERIOR RENOVATION OF 3 DWELLING APARTMENT BUILDING", False, None),
    ("INTERIOR REMODEL OF UNITS 1 TO 3 IN EXISTING MASONRY APARTMENT BUILDING", False, None),
    ("GUT REHAB UNIT 1 + UNIT 2 OF EXISTING APARTMENT BUILDING", False, None),
    ("DECONVERSION OF EXISTING APARTMENT BUILDING FROM 4 UNITS TO 3 DWELLING UNITS", False, None),
    ("CAISSONS (VERTICAL PENETRATION) ONLY FOR NEW 7 STORY 91-UNIT MIXED USE BUILDING", False, None),
    ("FOUNDATION ONLY FOR NEW 12 STORY 200 UNIT RESIDENTIAL BUILDING", False, None),
    ("INTERIOR DEMOLITION OF EXISTING LEVELS 14 AND 15 OF HOSPITAL PAVILION", False, None),
    ("LANDSCAPING, PARK AND RIVERWALK IMPROVEMENTS FOR CASINO AND HOTEL", False, None),
    ("ROOF REPLACEMENT AT EXISTING SCHOOL BUILDING", False, None),
    ("INTERIOR ALTERATIONS TO A SINGLE RESIDENTIAL UNIT 4103 IN EXISTING HIGH-RISE CONDOMINIUM", False, None),
    ("ALTERATIONS TO EXISTING OFFICE SPACE, SUITES 2600 AND 2652", True, None),
    ("INTERIOR DEMOLITION AND BUILDOUT OF NEW RESTAURANT TENANT SPACE", True, None),
    ("NEW CONSTRUCTION OF A 12-STORY RESIDENTIAL BUILDING (199 UNITS) W/ NO BASEMENT", True, 199),
    # second holdout pass, Oct 17 (real City wording)
    ("SC 2019 CBC: FULL BUILDING PERMIT FOR A FULL ROOF REPLACEMENT FOR A 4-STORY 76,262SF ELEMENTARY SCHOOL BUILDING.", False, None),
    ("SPR 2019 CBRC: PARTIAL NONSTRUCTURAL INTERIOR DEMOLITION AND ALTERATION OF SUITE 3904 IN EXISTING 74 STORY, 260 UNIT RESIDENTIAL BUILDING.", False, None),
    ("SELF CERT 2019 CBC: FULL BUILDING PERMIT FOR NEW 3-STORY + BASEMENT MULTIFAMILY RESIDENCE (OCCUPANCY GROUP R-5, TYPE V-A CONSTRUCTION)(BASEMENT + 1ST FLOOR: UNIT 1, 2ND FLOOR: UNIT 2, 3RD FLOOR: UNIT 3)", False, None),
    ("SELF-CERT 2019 CBRC - TENANT BUILDOUT OF 17,810 SQFT FOR BUSINESS OFFICE ON THE 8TH FLOOR, INCLUDING ALTERATIONS TO ELECTRICAL CIRCUITS, MECHANICAL AND PLUMBING.", True, None),
    ("SPR 2019 CBRC: REPAIRS FOR FIRE DAMAGE AND INTERIOR RENOVATION OF EXISTING 3 STORY, III-A, 17DU APARTMENT BUILDING AS PER PLANS", True, 17),
    ("DDS 2019 CBRC: INTERIOR ALTERATIONS 15-STORY RESIDENTIAL BUILDING (407 DWELLING UNITS) TO FLOORS 1-18 FOR ALTERATIONS TO ACCOMODATE NEW FIRE SUPPRESSION SYSTEM.", False, None),
    ("SELFCERT 2019-CBRC: ALTERATION TO REPLACE TWO EXISTING ROOFTOP MAKEUP AIR UNITS WITH TWO NEW ROOFTOP DOAS UNITS TO PROVIDE CONDITIONED VENTILATION TO RESIDENTIAL CORRIDORS", False, None),
    ("SPR 2019 CBRC: REPLACEMENT OF EXISTING PLUMING RISERS AND DISTRIBUTION LINES IN AN EXISTING 22-STORY RESIDENTIAL BUILDING AS PER PLANS.", False, None),
    ("DDS / 2019 CBC: FULL BUILDING PERMIT FOR THE NEW CONSTRUCTION OF A 13-STORY RESIDENTIAL BUILDING (80 TOTAL DWELLING UNITS; 60 DWELLING UNITS + 20 EFFICIENCY UNITS)", True, 80),
    ("NEW FOUNDATIN ONLY FOR NEW 2 STORY WAREHOUSE AND DISTRIBUTION AS PER PLANS", False, None),
    ("SELF-CERT 2019 CBC: LIMITED NONSTRUCTURAL ALTERATIONS TO EXISTING STOREFRONT AND FACADES ON GROUND FLOOR AND LEVEL 1 OF EXISTING 26 STORY FULLY SPRINKLERED MIXED USE BUILDING", False, None),
    # third holdout pass, Oct 17 (real City wording)
    ("DDS 2019 CBC:  FOUNDATION AND SUPERSTRUCTURE PERMIT THROUGH LEVEL 2 FOR A 5 STORY 40 UNIT RESIDENTIAL BUILDING WITH AMENITIES AND RETAIL SPACE.", False, None),
    ("(DIRECT DEVELOPER SERVICES / 2019 CBC)  FOUNDATION / SUPERSTRUCTURE PERMIT FOR THE NEW CONSTRUCTION OF A 14-STORY RESIDENTIAL BUILDING (199 UNITS)", False, None),
    ("SELF-CERT 2019 CRBC - CPS SCHOOL - NO CHANGE IN USE.  EXCEL ACADAMY OF ENGLEWOOD. M.E.P. IMPROVEMENTS AT EXISTING TWO-STORY BRICK SCHOOL BUILDING", False, None),
    ("2019 CBRC: INTERIOR ALTERATIONS FOR PROCESS EQUIPMENT EXPANSION AND SUPPORT SYSTEMS OF APPROXIMATELY 1,900 SF. GENERAL MANUFACTURING W/ACCESSORY OFFICE USE.", False, None),
    ("2019 SPR CBRC: INTERIOR ALTERATIONS INCLUDING NEW IN-UNIT WASHER/DRYER & MINIMAL ELEC/PLUMB WORK AS PER PLANS FOR EXISTING 16 D.U., 3 STORY BRICK BUILDING", False, None),
    ("SPR 2019 CBC: INTERIOR BUILDOUT OF UNINTERRUPTIBLE POWER SUPPLY (UPS) ROOM AT EXISTING BAKERY AS PER PLANS", False, None),
    ("SPR 2019 CBRC: TENANT IMPROVEMENT TO REMODEL ELECTRICAL ROOMS AND SUPPORT SPACES ON THE 6TH FLOOR SUITES S600A & S600B OF AN EXISTING DATA CENTER.", False, None),
    ("THIS PROJECT CONSISTS OF AN APPROXIMATE 6,200 SF RENOVATION OF THE 14TH FLOOR OF AN EXISTING MEDICAL OFFICE BUILDING OF NORTHWESTERN MEMORIAL HEALTHCARE.", True, None),
    ("SC 2019 CBC ERECT A 3 STORY TYPE IIIA SIX DWELLING UNIT MASONRY BUILDING WITH FRONT AND REAR OPEN METAL BALCONIES", True, 6),
    ("CURRENT R-2 PROPOSED R-2 OCCUPANCY. RENOVATION OF EXISTING RESIDENTIAL 6-FLAT, INCLUDING INTERIOR BUILD OUT", True, 6),
    ("DDS 2019 CBRC. RENOVATION OF THE SUNNYDALE COMMONS APARTMENTS CONSISTS OF ONE HUNDRED FOUR (104) SENIOR LIVING APARTMENTS LOCATED WITHIN ONE (1) EXISTING 9-STORY BUILDING.", True, 104),
    ("INTERIOR AND EXTERIOR ALTERATIONS TO EXISTING 3 STORY OFFICE AND WAREHOUSE BUILDING. ROOF WORK TO INCLUDE REMOVAL OF ALL RTU'S AND THE INSTALLATION OF THREE NEW UNITS.", True, None),
]
FILTER_CASES += [
    ("CORE & SHELL IMPROVEMENTS TO EXISTING VACANT INDUSTRIAL 2 STORY BUILDING. SCOPE OF WORK INCLUDES REPLACEMENT OF RTUS, FACADE IMPROVEMENTS, TO MAKE SUITABLE FOR LEASING", False, None),
    ("SPR 2019 CBRC: NONSTRUCTURAL INTERIOR DEMOLITION AND MINOR ARCHITECTURAL ALTERATIONS TO EXISTING 1-STORY RETAIL BUILDING. TENANT BUILDOUT UNDER SEPARATE PERMIT #101075900", False, None),
    ("FULL BUILDING PERMIT FOR NEW 19-STORY RESIDENTIAL BUILDING CONTAINING 464 DWELLING UNITS (140 EFFICIENCY UNITS, 81 AFFORDABLE UNITS)", True, 464),
    # conversions count the homes after the work (Holdout, Oct 18)
    ("INTERIOR RENOVATION TO CONVERT EXISTING 4 D.U. RESIDENTIAL TO 2 DWELLING UNIT", False, None),
    ("INTERIOR ALTERATIONS TO CONVERT EXISTING 2 DWELLING UNIT BUILDING TO 6 DWELLING UNITS", True, 6),
    ("GUT REHAB AND CONVERSION OF EXISTING 3 DWELLING UNITS TO 4 DWELLING UNITS", True, 4),
    ("INTERIOR RENOVATION TO CONVERT EXISTING 3-STORY OFFICE BUILDING TO (12) RESIDENTIAL DWELLING UNITS", True, 12),
    ("GUT RENOVATION OF AN EXISTING 3-STORY GROUP LIVING COMMUNITY HOME. EXISTING 16 SLEEPING UNITS ARE TO BE DEMOLISHED AND RECONFIGURED "
     "INTO 12 SLEEPING UNITS. BASEMENT TO BE RECONFIGURED TO INCLUDE A NEW RESIDENTIAL COMMUNAL KITCHEN, OFFICES AND RESIDENT LOUNGE SPACE", True, 0),
    ("RENOVATION AND ADAPTIVE REUSE OF THE EXISTING CHURCH. EXISTING USE IS A SANCTUARY AND 13 UNITS. THE SANCTUARY WILL BE CONVERTED INTO 9 "
     "ADDITIONAL UNITS. THE EXISTING 13 UNITS WILL BE RENOVATED INCLUDING KITCHEN AND BATHROOM UPGRADES", True, 22),
]
# holdout round 5, Oct 18 (real City wording, trimmed): every rule changed that day has a case here
FILTER_CASES += [
    ("DDS 2019 CBC: FULL BUILDING PERMIT FOR 8 STORY APARTMENT BUILDING WITH 98 DWELLING UNITS AND 20 CAR PARKING SPACES. CAISSON ONLY PERMIT UNDER 101050276 (OCCUPANCY GROUP R-2; TYPE IB CONSTRUCTION)", True, 98),
    ("DDS 2019 CBC: INTERIOR BUILDOUT OF NEW 7-STORY CASINO, PARKING, AND EVENT CENTER BUILDING AND 34-STORY HOTEL TOWER. CAISSONS AND PILES ONLY PERMITTED UNDER 101064196. EX/ERS, GRADE BEAMS, SLAB ON GRADE, TOWER CORE SUBSTRUCTURE PERMITTED UNDER 101064733.", True, None),
    ("DDS 2019 CBC: FULL BUILDING PERMIT FOR THE SUPERSTRUCTURE, ENCLOSURE, AND INTERIOR FIT OUT OF SATELLITE 1 CONCOURSE TERMINAL BUILDING AT O'HARE INTERNATIONAL AIRPORT. CAISSONS ONLY PERMIT UNDER 10106693. ERS ONLY PERMIT UNDER 101068757. SHALLOW FOUNDATIONS AND SUBSTRUCTURE UNDER 101071588. (CONSTRUCTION TYPE IB, OCC GROUP A-2, A-3, F-1)", True, None),
    ("SELF-CERT 2019 CBRC: SUITE B TENANT IMPROVEMENT FOR INDOOR PHYSICAL FITNESS CENTER. THE REST IS ALL NON-STRUCTURAL INTERIOR ONLY DEMOLITION. (OCCUPANCY GROUP A-3 & M)", True, None),
    ("SPR 2019 CBC - ERECT 1 STORY CARWASH BUILDING INCLUDING FENCE AND TRASH ENCLOSURE (CONSTRUCTION TYPE IIB - B OCCUPANCY)", True, None),
    ("DDS 2019 CBRC: INTERIOR ALTERATIONS TO EXISTING SYNAGOGUE (A-3 USE) ON THE 1ST FLOOR (NEW WALLS, DOORS, AND MEP WORK)", True, None),
    ("SELF-CERT 2019 CBRC: INTERIOR ALTERATIONS TO SUITE 2850. WORK TO INCLUDE DEMO, NEW PARTITIONS, CEILING, LIGHTING. B-BUSINESS OCCUPANCY", True, None),
    ("RENOVATION OF 1ST FLOOR GIRLS AND BOYS TOILET ROOMS, A NEW ALL-GENDER TOILET ROOM, ADA UPGRADES AT ENTRANCE #3, AND KEYLESS ACCESS.", True, None),
    ("CONSTRUCT A SECOND FLOOR ADDITION TO EXISTING 2 STORY FRAME RESIDENCE WITH NEW KITCHEN", False, None),
    ("DDS 2019 CBC: FULL BUILDING FOR 9 NEW 3-STORY TOWNHOUSES (R-2) WITH PRIVATE GARAGES, FULLY SPRINKLERED, TYPE V-A CONSTRUCTION AS PER PLANS", True, 9),
    ("PROPOSED TOWNHOME DEVELOPMENT W/FOUR 2 STORY UNITS, 4' IRON FENCE, AND TWO 3 CAR GARAGES, PER PLANS.", True, 4),
    ("DDS 2019 CBC: FULL BUILDING FOR 3 NEW 3-STORY TOWNHOUSES (R-2) WITH PRIVATE GARAGES", False, None),
    ("SPR 2019 CBC. ERECT A NEW 3 STORY WALKUP STRUCTURE WITH 44 AFFORABLE HOUSING UNITS. NEW PARKING LOT WITH 23 CARS. OCCUPANCY GROUP R5 TYPE 3B CONSTRUCTION", True, 44),
    ("SELF CERT 2019 CBC: FULL BUILDING PERMIT FOR NEW 3-STORY MULTI FAMILY RESIDENCE(DUPLEX UNITS - BASEMENT ((UNIT 1, UNIT 2, UNIT 3)) + 1ST FLOOR((UNIT 1, UNIT 2, UNIT 3)) + DUPLEX UNITS ((2ND FLOOR - UNIT 4, UNIT 5)) + 3RD FLOOR ((UNIT 4, UNIT 5)) + ROOF DECK) (OCCUPANCY GROUP R-2)", True, 5),
    ("DDS 2019 CBC: 3 STORY MASONRY BUILDING REMODEL UPDATE 23 EXISTING D.U.'S & ADD 1 NEW D.U. IN BASEMENT AND ADD NEW TRASH ENCLOSURE (R-2, IIIA)", True, 24),
    ("2019 SPR: INTERIOR ALTERATIONS WITH LIMITED MEP WORK AS PER PLANS TO 6 D.U. IN TIER #6521, (NO WORK ON REMAINING 18 D.U.) FOR EXISTING 3 1/2 STORY BRICK APARTMENT BUILDING", True, 24),
    ("(DDS / 2019 CBC) FULL BUILDING PERMIT FOR THE NEW CONSTRUCTION OF A 31-STORY RESIDENTIAL BUILDING (154 EFFICIENCY UNITS & 339 DWELLING UNITS)", True, 493),
    ("DDS 2019 CBC: NEW CONSTRUCTION OF A 5-STORY MIXED-USE BUILDING TO INCLUDE GROUND FLOOR RETAIL AND RESIDENTIAL (46 DWELLING UNITS;37 EFFICIENCY UNITS +9 DWELLING UNITS) ON FLOORS 2-5", True, 46),
    ("DDS 2019 CBC: FULL BUILDING PERMIT FOR FOUR STORY SIXTY UNIT APARTMENT BUILDING WITH GROUND FLOOR RETAIL. (OCC. R-2,TYPE IIA CONST.)", True, 60),
    ("CONVERSION OF 7-STORY OFFICE BUILDING TO A MIXED USE BUSINESS / RESIDENTIAL BUILDING WITH 74 DWELLING UNITS TOTAL AT ALL FLOORS. REVISION TO PERMIT #101070360 FOR 77 DWELLING UNITS", True, 74),
    ("DDS 2019 CBRC: 5TH FLOOR ADDITION - 8 ADDITIONAL UNITS - TO EXISTING 4 STORY 24 UNIT BUILDING. BUILDING TO HAVE 32 UNITS WHEN COMPLETED.", True, 32),
    ("SPR 2019 CBC CONSTRUCT A 4 STORY, 6 DWELLING UNIT TYPE IIIA MASONRY ADDITION AND A NEW BASEMENT. THERE WILL BE A TOTAL OF FIFTEEN APARTMENTS IN THE BUILDING. NO WORK TO THE EXISTING 5 STORY BUILDING CONTAINING 9 DWELLING UNITS.", True, 15),
    ("SPR 2019 CBRC: INTERIOR ALTERATIONS TO EXISTING DWELLING UNIT 22BC IN EXISTING 27-STORY 49 DWELLING UNIT RESIDENTIAL BUILDING. (OCCUPANCY GROUP R-2)", False, None),
    ("SELF-CERT 2019 CBRC: INTERIOR RENOVATIONS RELATED TO THE CONVERSION OF 2 EXISTING RESIDENTIAL DWELLING UNITS #509 AND 510 TO 1 RESIDENTIAL DWELLING UNIT. DE-CONVERT FROM 149 TO 148 DWELLING UNITS. R-2 OCC.", False, None),
    ("SELF CERT 2019 CBRC: INTERIOR ALTERATION TO UNIT 22A. SCOPE OF WORK INCLUDES DEMO, NEW WALLS AND CEILINGS, FINISHES. NO CHANGE IN USE R2 RESIDENTIAL", False, None),
    ("SPR 2019 CBRC: UNIT 14B ONLY - REMODEL KITCHEN AND TWO BATHS IN EXISTING CONDOMINIUM BUILDING", False, None),
    ("SPR 2019 CBC: INTERIOR RENOVATION, COMBINATION OF UNITS 4304 & 4305 ON THE 43RD FLOOR IN AN EXISTING 47 STORY CONDO BUILDING (OCCUPANCY GROUP R-2)", False, None),
    ("SELF-CERT 2019 CBRC: ALTERATIONS TO EXISTING 2 STORY GROUP HOME CONSISTING OF 1 EXISTING DWELLING UNIT AND 8 EXISTING SLEEPING UNITS. SCOPE INCLUDES NEW KITCHEN, NEW BATHROOM ON LEVEL 1, NEW FINISHES THROUGHOUT.", True, 0),
    ("SPR 2019 CBC CONVERTING AN EXISTING 2 STORY MOTEL TO A SINGLE ROOM TRANSITIONAL HOUSING (24 SLEEPING UNITS + 2 ADA SLEEPING UNITS FOR A TOTAL OF 26). INSTALLING A NEW WARMING KITCHEN.", True, None),
    ("INTERIOR RENOVATION OF A 2-STORY WALK-UP APARTMENT BUILDING.", False, None),
    ("DDS 2019 CBC: EX/ERS, GRADE BEAMS, SLAB ON GRADE, TOWER CORE SUBSTRUCTURE AND DEEP ELEVATOR PIT WITH STRIP FOOTINGS FOR THE NEW CONSTRUCTION OF A PROPOSED MIXED USE BUILDING INCLUDING SIX STORY CASINO", False, None),
    ("DDS 2019 CBC: SUPERSTRUCTURE ONLY PERMIT FOR A PROPOSED 4-STORY STADIUM WITH NO BASEMENT ON PILES. PILES ONLY PERMIT UNDER 101075594. (OCC GROUPS A-2, A-3, A-5, B; CONSTRUCTION TYPE IB)", False, None),
    ("DDS 2019 CBC. NEW CONSTRUCTION. INSTALLATION OF AGGREGATE PIERS TO A DEPTH OF 19' BELOW GRADE FOR A 137,410 SQFT STORAGE FACILITY (S-1)", False, None),
    ("DDS 2019 CBC: REVISION TO PERMIT # 101026543 TO DELETE THE CONSTRUCTION OF A PORTION OF THE RAIL PLATFORM END. (METRA STATION - OCCUPANCY GROUP A-3)", False, None),
    ("SPR 2019 CBRC: INTERIOR ALTERATIONS TO EXISTING 2-STORY WITH BASEMENT FIRE HOUSE TO INCLUDE STRUCTURAL REPAIRS TO BASEMENT AND APPARATUS FLOOR. (OCCUPANCY GROUP R-3 & S-2)", False, None),
    ("SELF CERT 2019 CBRC: INTERIOR ALTERATIONS TO AN EXISTING RESIDENTIAL CONDO BUILDING REQUIRED FOR THE ELEVATOR MODERNIZATION INCLUDING A 2-HOUR RATED ELEVATOR MACHINE ROOM", False, None),
    ("INSTALLATION OF NEW CT EQUIPMENT AND ASSOCIATED BUILDING ALTERATIONS ON 3RD FLOOR.", False, None),
    ("2019 SELF-CERT CBC: FULL BUILDING PERMIT FOR A NEW 1-STORY FOUR (4) BAY ACCESSORY VEHICLE PARKING GARAGE AS PER PLANS. (OCCUPANCY GROUP U; TYPE IIB CONSTRUCTION)", False, None),
    ("SPR 2019 CBC: FULL BUILDING PERMIT FOR 4-STORY, 10 DWELLING UNIT MULTI-FAMILY RESIDENTIAL BUILDING WITH 1 OUTDOOR PARKING SPACE, 4-CAR DETACHED GARAGE (OCCUPANCY GROUP U)", True, 10),
    ("CURRENT GYMNASIUM AND OFFICE ROOM NEXT TO IT IN THIRD FLOOR SOUTHEAST CORNER IS BEING CONVERTED IN TO A DANCE STUDIO AND SUPPORTING ROOMS.", True, None),
    ("EXISTING 2-STORY MASONRY (TYPE IIIA) FIREHOUSE OCCUPANCY CHANGE TO RETAIL, BUSINESS, AND AGRICULTURE. ALTERATIONS INCLUDE NEW ROOF, SPOT TUCKPOINTING", True, None),
    ("SELF CERT 2019 CBRC: INT BUILDING OUT OF SHELL SPACE ON GROUND FLOOR - TRADER JOES", True, None),
    ("SELF CERT 2019 CBRC ALDI - SOUTH LOOP STORE NUMBER #098 INTERIOR RETROFIT OF EXISTING BUILDING", True, None),
    ("SELF-CERT 2019 CBRC: ATERATIONS OF EXISTING OFFICE SPACE, SUITE 1400. INTERIORS WORK ONLY. (OCCUPANCY GROUP B - BUSINESS)", True, None),
    ("PROPOSED COMMERCIAL BUILDING DEVELOPMENT. TWO TENANT BUILDING BUFFALO WILD WINGS IS PART OF THE PROJECT. PARKING AND TRASH ENCLOSURE.", True, None),
    ("SC CBC 2019 CONSTRUCT A SECOND FLOOR ADDITION AND A 2 STORY TYPE IIIA REAR MASONRY ADDITION FOR AN EXISTIN ONE STORY COMMERCIAL SPACE", True, None),
]
NAME_CASES = [("THE BOWA GROUP INC", "The Bowa Group Inc"), ("TO BE SEEN LLC", "To Be Seen LLC"), ("CPMH CONSTRUCTION INC", "CPMH Construction Inc"),
              ("21ST CENTURY US-SINO SERVICE INC", "21st Century US-Sino Service Inc"), ("JC ANDERSON INC", "JC Anderson Inc"),
              ("M. A. MORTENSON COMPANY", "M. A. Mortenson Company"), ("THERMO-POL INC", "Thermo-Pol Inc"), ("MPI CONSTRUCTION", "MPI Construction"),
              ("THORNDALE CONSTRUCTION COMPANY DBA STASICA CONSTRU", "Thorndale Construction Company"), ("PARKS AND BELL CLEANING COMPANY", None),
              # holdout, Oct 18: no ellipsis is ever added, and these are businesses
              ("DINASO AND SONS CONSTRUCTION COMPANY, INCORPORATED", "Dinaso and Sons Construction Company, Incorporated"),
              ("G.A. JOHNSON & SON", "G.A. Johnson & Son"), ("SANDSMITH VENTURE", "Sandsmith Venture"), ("CLARK - W.E. O'NEIL JV", "Clark - W.E. O'Neil JV"),
              ("HABITAT FOR HUMANITY CHICAGO", "Habitat for Humanity Chicago")]
SCOPE_CASES = [("***SELF-CERT*** EXISTING ZONED PD 306. SCOPE OF WORK: INTERIOR ALTERATION OF EXISTING SPACE INTO A COMMERCIAL BANKING FACILITY", "Interior alteration"),
               ("SELF CERT 2019 CBRC: STRUCTURAL PEER REVIEW INCLUDED. INTERIOR ALTERATIONS TO 26TH AND 27TH FLOOR OFFICE SPACE.", "Interior alterations"),
               ("2019 CBRC: SELF CERTIFICATION OF A LIMITED SCOPE RENOVATION. SCOPE INCLUDED RENOVATION OF SPACE ON LEVEL 2 FOR OFFICES.", "Renovation of space"),
               ("SELF-CERT 2019 CBC FOR INITIAL BUILD OUT OF GROUND FLOOR SUITE 104 OF THE TRIBUNE TOWER BUILDING.", "Initial build out"),
               ("", "No description in the City record."),
               ("SELF-CERT 2019 CBC.(FACE 1) ERECT A 3-STORY TOWNHOUSE DEVELOPMENT", "(Face 1) erect"),
               ("SELF CERT: (3512 E 118TH) INTERIOR RENOVATION TO EXISTING PLANET FITNESS", "Interior renovation"),
               ("SELF CERT 2019 CBRC WITH STRUCTUAL PEER REVIEW.: INTERIOR ALTERATIONS TO GROUND FLOOR RETAIL", "Interior alterations"),
               ("ELF CERT 2019 CBRC: INTERIOR ALTERATIONS TO 8TH FLOOR OFFICE SPACE", "Interior alterations"),
               ("SC CBC 2019CPS SCHOOL - NO CHANGE IN USEBATHROOM AND STORAGE ROOM RENOVATION", "Bathroom and storage")]


def keep_desc(d, ptype=""):
    """The same decision main() makes, plus the homes count."""
    return decide(d, ptype)[0], unit_count(d.upper(), display=True)   # what the pages show


def selftest():
    bad = [(d, k, h, keep_desc(d, "PERMIT - NEW CONSTRUCTION" if "NEW CONSTRUCTION" in d else "")) for d, k, h in FILTER_CASES if keep_desc(d)[0] != k or (h is not None and keep_desc(d)[1] != h)]
    assert gc_clean("MEADE ELECTRIC COMPANY, INC. ATTN: D. POEMBA") == "MEADE ELECTRIC COMPANY, INC.", "Attn not stripped"
    assert title_name("WILLIAM'S CONSTRUCTION") == "William's Construction"
    for raw, want in NAME_CASES:
        assert unit_count("RENOVATION INCLUDING CONVERSION OF 13 DWELLING UNITS TO MOBILITY ACCESSIBLE UNITS", display=True) == 0
    assert gc_filter(raw) == want, (raw, gc_filter(raw), want)
    for raw, want in SCOPE_CASES:
        assert clean_scope(raw).startswith(want), (raw, clean_scope(raw), want)
    long = ("SELF-CERT 2019 CBC: INTERIOR ALTERATIONS TO 8TH FLOOR OFFICE SPACE FOR A NEW TENANT. NEW PARTITIONS, CEILINGS AND FINISHES. "
            "NEW RESTROOMS ON THE FLOOR. PLAN REVIEWER JANE DOE")
    whole = clean_scope(long, limit=1200, whole=True)
    assert whole.startswith("Interior alterations") and "restrooms" in whole and "Jane" not in whole and "Doe" not in whole, whole
    assert len(clean_scope(long)) < len(whole), "whole scope should keep every sentence"
    lab = clean_scope("INTERIOR RENOVATION OF LARGE LAB PROCESSING SPACE ON LEVEL 2. CONSUTLTANT REVIEWER: X3 JOHN SMITH", limit=1200, whole=True)
    assert lab.endswith("on level 2") and "Consut" not in lab and "Smith" not in lab, lab
    init = clean_scope("ERECT A 4 STORY BUILDING (THIS PERMIT INCLUDES THE ATTACHED 6-UNIT BUILDING AT 2025 N RACINE. HLH)", limit=1200, whole=True)
    assert init.lower().endswith("2025 n racine)") and "hlh" not in init.lower(), init
    assert clean_scope("INTERIOR ALTERATIONS TO OFFICE SPACE ON LEVEL PH)", limit=1200, whole=True).lower().endswith("level ph)"), "a level name is not initials"
    assert builders(["CPMH CONSTRUCTION INC", "RD'S HVAC INC", "THE BOWA GROUP INC"]) == ["CPMH Construction Inc", "The Bowa Group Inc", "RD's HVAC Inc"], \
        builders(["CPMH CONSTRUCTION INC", "RD'S HVAC INC", "THE BOWA GROUP INC"])
    assert builders(["ACME BUILDERS LLC", "Acme Builders, L.L.C.", "JOHN SMITH", "", None]) == ["Acme Builders LLC"]
    assert entity_key("AT MECHANICAL LLC") == entity_key("AT Mechanical, L.L.C.") == entity_key("at mechanical llc.")
    assert entity_key("Skender Construction LLC") == entity_key("Skender Construction, LLC.")
    assert entity_key("PANOPTIC GROUP LLC") != entity_key("PANOPTIC GROUP INCORPORATED") and gc_key("PANOPTIC GROUP LLC") == gc_key("PANOPTIC GROUP INCORPORATED")
    assert entity_key("Acme Inc") == entity_key("ACME INCORPORATED") and entity_key("Acme Corp") != entity_key("Acme Co")
    assert builders(["PANOPTIC GROUP LLC", "PANOPTIC GROUP INCORPORATED"]) == ["Panoptic Group LLC", "Panoptic Group Incorporated"]
    assert entity_names([{"gc": ["Skender Construction, LLC."]}, {"gc": ["Skender Construction LLC"]}, {"gc": ["Skender Construction LLC"]}]) == \
        {entity_key("Skender Construction LLC"): "Skender Construction LLC"}
    assert str(list_day("2026-10-18T02:42:43+00:00")) == "2026-10-17" and str(list_day("2026-10-18T15:00:00Z")) == "2026-10-18"
    assert coord("41.881832") == 41.881832 and coord(None) is None and coord("") is None and coord("0") is None
    # the 24-month open-permit window (Todd, Oct 17): planted rows as the City writes them, run on Oct 18, 2026
    run = dt.datetime(2026, 10, 18, 1, 25, tzinfo=dt.timezone.utc)
    since = window_start(run)
    assert since == "2024-10-17T00:00:00" and months(DAYS) == "24 months" and months(365) == "12 months", (since, months(DAYS))
    assert window_start(dt.datetime(2026, 10, 18, 15, 0, tzinfo=dt.timezone.utc)) == "2024-10-18T00:00:00", "counted from the Chicago date of the pull"
    row = lambda issued, status: {"issue_date": issued + "T00:00:00.000", "permit_status": status}
    for issued, status, want in [
            ("2025-10-17", "ACTIVE", True),               # 101070566 and 101070855: aged out of the old 365-day window, work still under way
            ("2025-09-18", "ACTIVE", True),               # 13 months old, still open: kept
            ("2025-09-18", "PHASED PERMITTING", True),
            ("2024-10-18", "ACTIVE", True),               # 101053956 (holdout, Oct 18): issued 729 days before the Chicago date of the pull
            ("2024-10-17", "ACTIVE", True),               # first day of the window: Oct 17, 2026 in Chicago, two years back
            ("2024-10-16", "ACTIVE", False),              # one day past 24 months
            ("2024-09-18", "ACTIVE", False),              # 25 months old: dropped
            ("2025-09-18", "COMPLETE", False),            # 13 months old but closed or expired: dropped
            ("2025-09-18", "EXPIRED", False),
            ("2025-09-18", "SUSPENDED", False),
            ("2025-09-18", "CANCELLED", False),
            ("2025-09-18", "", False)]:
        assert in_window(row(issued, status), since) is want, (issued, status, want)
    if bad:
        raise SystemExit("filter selftest FAIL: " + json.dumps(bad)[:800])
    print(f"filter selftest ok ({len(FILTER_CASES)} planted cases)")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        main()
