#!/usr/bin/env python3
"""Austin Construction Cleaning Leads: the weekly list from the City of Austin's Issued Construction Permits data.

Runs in GitHub Actions (.github/workflows/permits-austin.yml) because the cloud agents cannot reach data.austintexas.gov.
Source: City of Austin, Issued Construction Permits (dataset 3syk-w9eu), published under the City of Austin Open Data
Terms of Use. Written to permits/austin/: sample.json (the free page's sample and counts), profile.json (value counts that
tune the filter; no names) and source-terms.txt (the City's own terms and disclaimer text, for the Legal desk). --full PATH
writes the paid list for the runner only; the repo is public, so that file is never committed in the clear.

How Austin's data works (read Oct 18, 2026 from a de-identified audit of every candidate row, --audit; committed once at 0fbf3ae):
- One building permit (permittype BP) per building, and often one per floor or phase of finish-out. A development's
  building permits share a master permit number (masterpermitnum), so the lead is the project: its building permits
  grouped by master permit.
- Austin repeats a development's valuation on its building permits (Lake View East shows $830,000,000 on 77 of them, its
  pergolas and garages included), and many permits carry a placeholder ($1, $5). A project's valuation is the largest
  valuation on its kept building permits (open, in the window, real clean-up work), counted once; valuations on finaled,
  shell, garage or older permits of the same master never count (holdout, Oct 18). New work carries it in total_job_valuation,
  remodels and finish-outs in total_valuation_remodel.
- There is no inspection milestone. The stage comes from the City's own fields: a permit of the project marked Final while
  others are still Active, or an expiry date the City has pushed past the first 180 days (Austin extends a building permit's
  expiry when an inspection passes or an extension is granted).

The rules (Todd, Oct 17, 2026, the Chicago list's buyer promise; every rule has planted cases in --selftest):
1. Window: building permits issued in the last 24 months, counted from the Central date of the pull, still Active
   (and not past the City's expiry date). Final, Expired, Withdrawn, Void, Cancelled and Pending permits are not open.
2. Real construction clean-up work only: commercial and multifamily buildings. Left out: structures that are not buildings
   (City class 329: carports, pergolas, canopies, dumpster enclosures, pools, EV chargers), parking garages (class 321),
   houses and duplexes (classes 101 to 103), three-unit buildings (class 104 under 4 homes), shell-only buildings, interior
   demolition, repair work, and work that never needs a construction clean (roofs, equipment, generators, fuel systems,
   solar, signs, elevators, fences, retaining walls, site and exterior-only work).
3. Valuation: the project's valuation (the largest on its kept building permits) is $500,000 or more.
4. Builder: the general contractor the City lists on the kept permits, only when it is a business (never a person's name;
   no phone, applicant or owner field is ever read), cleaning companies left out, grouped by legal entity
   (permits_chicago.entity_key: "Acme Builders LLC" and "ACME BUILDERS, L.L.C." are one builder, LLC and Inc are two).
"""
import argparse, collections, datetime as dt, json, os, re, sys, time, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import permits_chicago as P  # noqa: E402  (clean_scope, gc_filter, entity_key, entity_names, window_start)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "permits", "austin")
PORTAL = "https://data.austintexas.gov"
DATASET = "3syk-w9eu"
DATASET_PAGE = f"{PORTAL}/d/{DATASET}"
TERMS_VIEW = "ranj-cccq"          # City of Austin Open Data Terms of Use (web version)
TERMS_URL = f"{PORTAL}/stories/s/{TERMS_VIEW}"
TERMS_PDF = f"{PORTAL}/download/2z87-8uh7/application/pdf"   # the same Terms of Use as a PDF (catalog.data.gov lists it)
RECORD = f"{PORTAL}/resource/{DATASET}.json?masterpermitnum="  # the City's own rows for one project
UA = {"User-Agent": "ProofNotFluff permit leads (github.com/proofnotfluff-a11y/Proofnotfluff-pins)"}
TZ = "America/Chicago"             # Austin is on Central time, the same zone as Chicago
DAYS = 730
MIN_COST = 500_000
OPEN = {"ACTIVE"}
KEEP_WORK = {"NEW", "ADDITION", "ADDITION AND REMODEL", "REMODEL"}
DEFAULT_EXPIRY = 181               # days from issue to the first expiry date the City sets (247 of the 1,268 open permits, Oct 18)
# Only these fields are read. Never: contractor_phone, contractor_address*, applicant_* (people). contractor_full_name is read only to
# tell a person filing as their own company from a business (builder_name); it is never written anywhere.
FIELDS = ("permit_number,masterpermitnum,permittype,permit_class_mapped,permit_class,work_class,description,status_current,"
          "statusdate,issue_date,expiresdate,completed_date,total_job_valuation,total_valuation_remodel,housing_units,"
          "number_of_floors,total_new_add_sqft,remodel_repair_sqft,original_address1,original_zip,council_district,"
          "latitude,longitude,location,contractor_trade,contractor_company_name,contractor_full_name,link")


def get(url, params=None, tries=4, as_text=False):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                body = r.read().decode("utf-8", "replace")
                return body if as_text else json.loads(body)
        except Exception as e:
            last = e
            time.sleep(5 * (i + 1))
    raise SystemExit(f"fetch failed: {url[:160]} ({last})")


# ---------------------------------------------------------------- reading one City row
def num(v):
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def money_of(r):
    return max(num(r.get("total_job_valuation")), num(r.get("total_valuation_remodel")))


def day(v):
    return (v or "")[:10]


def cls_no(r):
    m = re.search(r"\b(\d{3,4})\b", r.get("permit_class") or "")
    return int(m.group(1)) if m else 0


def central_today(now):
    from zoneinfo import ZoneInfo
    return now.astimezone(ZoneInfo(TZ)).date() if getattr(now, "tzinfo", None) else now.date()


def is_open(r, today):
    """Active in the City's record and not past its expiry date."""
    if (r.get("status_current") or "").strip().upper() not in OPEN:
        return False
    exp = day(r.get("expiresdate"))
    return not exp or exp >= today.isoformat()


def extended(r):
    """True when the City has pushed the expiry date past the first 180 days from issue (an inspection passed or an
    extension was granted). Read from the City's own issue and expiry dates."""
    try:
        i, e = dt.date.fromisoformat(day(r.get("issue_date"))), dt.date.fromisoformat(day(r.get("expiresdate")))
    except ValueError:
        return False
    return (e - i).days > DEFAULT_EXPIRY + 3


def coord(r):
    lat, lon = P.coord(r.get("latitude")), P.coord(r.get("longitude"))
    loc = r.get("location")
    if (lat is None or lon is None) and isinstance(loc, dict):
        if loc.get("type") == "Point" and len(loc.get("coordinates") or []) == 2:
            lon, lat = P.coord(loc["coordinates"][0]), P.coord(loc["coordinates"][1])
        else:
            lat, lon = P.coord(loc.get("latitude")), P.coord(loc.get("longitude"))
    if lat is None or lon is None or not (29.5 < lat < 31.0 and -98.5 < lon < -97.0):   # a pin outside the Austin area is a bad geocode
        return None, None
    return lat, lon


# ---------------------------------------------------------------- the City's description, cleaned for reading
PREFIX = re.compile(r"^\s*(?:\*[^*]{1,40}\*\s*)?(?:QT\s*-\s*)?(?:e-?plan\s*[:-]?\s*)?(?:(?:commercial|commerical)\s+)?(?:expedited\s+)?(?:BAUS\s*[-:]?\s*)?"
                    r"(?:review\s*[:-]?\s*)?(?:airport project\s*:\s*)?", re.I)
TAGS = re.compile(r"\[\s*(?:APPROVED|CONCURRENT|SMART HOUSING|AE GREEN BUILDING|GREEN BUILDING|PUBLIC PROJECT|BETTER BUILDER)(?:\s+SP)?\s*\]?\s*|"
                  r"\*+\s*SMART HOUSING\s*\*+\s*|\bSMART HOUSING\s*-\s*|^\s*\*FKA[^*]{1,60}\*\s*", re.I)
TAIL = re.compile(r"\s*(?:\[[^\]]{0,40}\]|\bSMART HOUSING\b|\bEPLAN REVIEW\b|\bPu ?PR2\b|\bConcurrent Revi\w*\b[^.]*|\*\*\s*Lands\w*|"
                  r"\(?Previous review expired[^)]*\)?|Per revision \d+[^.]*)\s*", re.I)
PHONE = re.compile(r"(?:\+?1[\s.-]*)?\(?\b\d{3}\)?[\s.-]+\d{3}[\s.-]+\d{4}\b")
EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")


def tidy(desc):
    """The City's text without the review prefixes, program tags, review notes, phone numbers or email addresses."""
    d = re.sub(r"\s+", " ", (desc or "").replace("¿", " ")).strip()
    d = PHONE.sub(" ", EMAIL.sub(" ", d))
    for _ in range(3):
        d2 = TAGS.sub("", PREFIX.sub("", d)).strip(" -:.*")
        if d2 == d:
            break
        d = d2
    d = TAIL.sub(" ", d)
    d = re.sub(r"\bsq\.\s*ft\b\.?", "sq ft", d, flags=re.I)
    d = re.sub(r"\s+\.", ".", re.sub(r"\s+", " ", d)).strip(" -:")
    return d


KEEP_CAPS = {"MEP", "HVAC", "ADA", "AISD", "CTE", "TI", "EV", "SF", "PV", "LLC", "BP", "ATD", "BOH", "IMP", "CU", "AE", "UT", "ACC", "II", "III", "IV",
             "LBJ", "MLK", "SH", "FM", "IH", "US", "RR", "ATX", "CISD", "ISD", "YMLA", "GSE", "FIS", "BAUS", "CMU", "PEMB", "RTU", "RTUS", "SMART", "HQ", "ER", "ICU"}


def sentence_case(t):
    """The City's all-caps text in sentence case, acronyms kept (design director, Oct 18: "FIRST TIME FINISH OUT- 5 PHASE 1
    MULTIFAMILY FLOORS 1-5 CLUB AMENTITY" reads as shouting). Text that is mostly lower case is left as filed."""
    words = re.findall(r"[A-Za-z]{3,}", t)
    caps = [w for w in words if w.isupper()]
    if len(caps) < 3 or len(caps) < 0.4 * len(words):
        return t
    out = re.sub(r"[A-Za-z][A-Za-z']*", lambda m: m.group(0) if m.group(0).upper() in KEEP_CAPS else m.group(0).lower(), t)
    out = re.sub(r"(^|[.!?]\s+|\|\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), out)
    return P.ACRONYMS.sub(lambda m: m.group(0).upper(), out)


ALWAYS_CAPS = re.compile(r"\b(?:aisd|cisd|isd|ymla|cte|lbj|mlk|baus|pemb|atd|boh)\b", re.I)


def austin_scope(desc, limit=150, whole=False):
    d = tidy(desc)
    return ALWAYS_CAPS.sub(lambda m: m.group(0).upper(), sentence_case(P.clean_scope(d, limit=limit, whole=whole))) if d else "No description in the City record."


ROAD_CAPS = re.compile(r"^(?:LBJ|MLK|SH|FM|IH|US|RR|RM|CR|NE|NW|SE|SW|ATX)\d*$", re.I)


def street_title(a):
    """An address as the list prints it: words in title case, road names in capitals (LBJ, SH, FM, IH, US, RR, RM), Mc names
    whole ("MC CANN DR" is McCann Dr), ordinals in lower case (21st)."""
    a = re.sub(r"\s+", " ", (a or "").strip())
    a = re.sub(r"\bMC\s+(?=[A-Z]{3,})", "MC", a, flags=re.I) if a.isupper() else a
    words = []
    for w in a.split(" "):
        if ROAD_CAPS.match(w):
            words.append(w.upper())
        else:
            w = re.sub(r"[A-Za-z]+", lambda m: m.group(0).capitalize(), w.lower())
            words.append(re.sub(r"\bMc([a-z])", lambda m: "Mc" + m.group(1).upper(), w))
    out = re.sub(r"\b(\d+)(St|Nd|Rd|Th)\b", lambda m: m.group(1) + m.group(2).lower(), " ".join(words))
    # the City's internal floor tokens ("Unit Flr1", "Bldg 1Flr Unit 55", "Unit Fw3") are not part of the address (design director)
    out = re.sub(r"\s+(?:Unit\s+)?(?:Flr\d+|Fw\d+)\b|\s+\d+Flr\b", "", out, flags=re.I)
    out = re.sub(r"\s+Bldg(?=\s+Unit\b)|\s+(?:Unit|Bldg)$", "", out)
    return re.sub(r"\s+", " ", out).strip()


# ---------------------------------------------------------------- rule 2: real construction clean-up work
SHELL = re.compile(r"\bSHELL\b|CORE (?:AND|&) SHELL")
FINISH = re.compile(r"FINISH[- ]?OUTS?\b|FIRST TIME FINISH|TENANT IMPROVEMENT|\bTI\b|BUILD[- ]?OUT")
NOT_OCC = re.compile(r"NOT FOR OCCUPANCY|REMAIN UNFINISHED")
# a part of the text that names another permit's or another space's work ("also contains Retail Shell (Separate Building Permit)")
ASIDE = re.compile(r"\bALSO CONTAINS\b[^.]*|\([^)]*(?:SEPARATE|FUTURE)[^)]*\)|\bPOOL TO BE PERMITTED SEPARATELY\b|\bDEMO PERMIT SEPARATE\b[^.]*")
# work that never needs a construction clean (Chicago's NON_CLEAN in spirit, in Austin's words). Named anywhere, it drops the
# permit unless the text also names finish work in rooms (SPECIFIC below).
NOT_CLEAN = re.compile(r"\bRE[- ]?ROOF\w*|ROOF (?:OVERLAY|REPLACEMENT|RECOVER\w*|MEMBRANES?|TEAR|SYSTEM)|\bTPO\b|RESKIN|\bRTUS?\b|ROOF ?TOP UNITS|"
                       r"GENERATORS?|GEN ?SETS?\b|CATWALK|FUEL (?:TANK|INFRASTRUCTURE|SYSTEM|CANOPY|STATION)|HYDRANT FUEL|JET FUEL|COOLING TOWER|CHILLER|"
                       r"\bEV CHARG\w*|ELECTRIC VEHICLE|CHARGING STATION|\bSOLAR\b|\bPV SYSTEM|PHOTOVOLTAIC|TRANSFORMER PAD|EXTERIOR PAD|TRACKING EQUIPMENT|"
                       r"EQUIPMENT REPLACEMENT|EQUIPMENT YARD|STERILIZER|ATHLETIC LIGHTING|\bSIGNS?\b|SIGNAGE|RETAINING WALL|\bFENCE\b|CARPORT|PERGOLA|TRELLIS|"
                       r"TRASH ENCLOSURE|DUMPSTER|TRASH COMPACTOR|RECYCL\w* PAD|BOAT DOCK|ROLLER COASTER|\bCOASTER\b|FUNICULAR|ART INSTALLATION|SHADE STRUCTURE|"
                       r"INTERIOR (?:NON[- ]?STRUCTURAL )?DEMO\w*|NON[- ]?STRUCTURAL DEMOLITION|DEMOLITION ONLY|FOUNDATION ONLY|SITE WORK ONLY|ELEVATOR (?:REPLACEMENT|MODERNI\w*)|SCRUBBER|"
                       r"BAG(?:GAGE)? CLAIM SYSTEM|RAISED ACCESS FLOOR|SHIPPING CONTAINERS?|INTERMODAL|RACKING SYSTEM INSTALL\w*|TRITURATOR|WASH BAY|COVERED PORCH|"
                       r"RAISED DECK|IMPERVIOUS COVER|FLATWORK|\bPORTABLES?\b|EXTERIOR AMENITY SPACE|\(ROOF DECK\)|NO BUILDING\b")
# the work is on an elevator, a roof, a patio or the outside of a building, or replaces equipment
OBJECT_TRADE = re.compile(r"(?:REMODEL|RENOVATION|ALTERATION|REPAIR|UPGRADE|REPLACEMENT)S?\s+(?:TO|OF|FOR|AT)\s+(?:THE\s+|AN?\s+)?(?:EXISTING\s+)?"
                          r"(?:PARKING GARAGE\s+)?(?:ELEVATORS?|ROOF|PATIO|POOL\b|FACADE|EXTERIOR)|^EXTERIOR (?:REMODEL|RENOVATION|ALTERATION|IMPROVEMENT)|"
                          r"^(?:NEW\s+)?ADDITION OF (?:A\s+)?(?:NEW\s+)?(?:COVERED\s+)?(?:TERRACE|DECK|PATIO|CANOPY|TRELLIS|PORCH)|^REPLACEMENT OF|^REPAIRS?\b")
# small accessory structures and garages, named as the whole subject of the permit (never saved by finish words)
ACCESSORY = re.compile(r"^(?:NEW\s+)?(?:CONSTRUCTION\s+(?:OF\s+)?)?(?:AN?\s+|THE\s+)?(?:NEW\s+)?(?:PRE-?FAB\w*\s+|ACCESSORY\s+|DETACHED\s+|POOL\s+|DOG\s+|PICNIC\s+)?"
                       r"(?:TRELLIS|CABANA|PAVIL+ION|(?:\w+\s+)?STORAGE SHED|SHED|GUARD BOOTH|POLE BARNS?|PUMP HOUSE|CHEMICAL STORAGE|RECYCLING|MAINTENANCE AND TRASH|"
                       r"GARAGE|STRUCTURED PARKING|PARKING (?:GARAGE|STRUCTURE|DECK)|POOL EQUIPMENT|PIERS?)\b|\bNO BUILDING\b|ATTRACTION ONLY|EXTERIOR AMENITY SPACE")
# finish work in rooms a cleaner is hired after: it keeps a permit that also names roof, equipment or site work
SPECIFIC = re.compile(r"FINISH[- ]?OUT|FIRST TIME FINISH|TENANT (?:IMPROVEMENT|FINISH)|\bTI\b|CHANGE OF USE|CHANGED OF USE|PARTITIONS|CEILINGS|\bFINISHES\b|"
                      r"RESTROOMS?|TOILET ROOMS?|CLASSROOMS?|LOCKER ROOMS?|(?:DWELLING|RESIDENTIAL|APARTMENT|FAMILY|\d|FOR|OF)\s+UNITS\b|\bUNITS\s+(?:ON|IN)\b|APARTMENTS|KITCHENS?\b(?! GREASE| HOOD| EQUIPMENT)|LOBBY|DINING|BREAK ?ROOM|VESTIBULES?|"
                      r"NEW WALLS|NON-?LOAD BEARING WALLS|INTERIOR UPGRADES")
# an interior remodel named in so many words (allows a permit the City filed under the Repair work class)
REMODEL_WORDS = re.compile(r"INTERIOR (?:REMODEL|RENOVATION|FINISH)|FINISH[- ]?OUT|CHANGE OF USE|TENANT IMPROVEMENT")


def keep_permit(r, since, today):
    """(keep?, reason) for one building permit, in the order the reasons are counted."""
    if day(r.get("issue_date")) < since[:10]:
        return False, "issued before the 24-month window"
    if not is_open(r, today):
        return False, "permit closed (final, expired, withdrawn, void or cancelled)"
    if (r.get("permittype") or "BP") != "BP" or (r.get("permit_class_mapped") or "Commercial") != "Commercial":
        return False, "not a commercial building permit"
    c = cls_no(r)
    if c == 329:
        return False, "structure that is not a building (carport, pergola, canopy, enclosure, pool, EV charger)"
    if c == 321:
        return False, "parking garage"
    units = int(num(r.get("housing_units")))
    if c in (101, 102, 103) or (c == 104 and units < 4):
        return False, "house, duplex or three-unit building"
    work = (r.get("work_class") or "").strip().upper()
    d = tidy(r.get("description")).upper()
    main = ASIDE.sub(" ", d).strip()
    if work == "REPAIR" and REMODEL_WORDS.search(main):
        work = "REMODEL"          # the City's Repair class on an interior remodel or change of use
    if work == "SHELL" or SHELL.search(main):
        if not FINISH.search(main) or NOT_OCC.search(main):
            return False, "shell only, no finish work"
        work = "NEW" if work == "SHELL" else work
    if work not in KEEP_WORK:
        return False, f"work class {work.title() or 'blank'} (interior demolition or repair)"
    if ACCESSORY.search(main):
        return False, "small accessory structure or garage (shed, booth, cabana, pavilion, trellis, garage)"
    lead_trade = re.match(r"(?:REPLACEMENT OF|REPAIRS?\b|RE[- ]?ROOF|ROOF)", main)
    spec = SPECIFIC.findall(main)
    if c == 327 and work == "NEW" and re.search(r"CONVENIENCE STORE", main):
        spec.append("CONVENIENCE STORE")   # a new store building with its fuel canopy (holdout D, Oct 18: 13347837, 9,566 sq ft)
    if lead_trade:   # a permit that opens with trade work needs finish work in rooms, not just "finishes" (holdout, Oct 18)
        spec = [x for x in spec if not re.match(r"FINISHES|KITCHEN|CEILINGS", x)]
    if (NOT_CLEAN.search(main) or OBJECT_TRADE.search(main)) and not spec:
        return False, "no construction clean (roof, equipment, site, sign, elevator or exterior work only)"
    return True, "kept"


# ---------------------------------------------------------------- rule 4: the builder
FIRST_NAMES = set("""JAMES JOHN ROBERT MICHAEL WILLIAM DAVID RICHARD JOSEPH THOMAS CHARLES CHRISTOPHER DANIEL MATTHEW ANTHONY MARK DONALD STEVEN
PAUL ANDREW JOSHUA KENNETH KEVIN BRIAN GEORGE TIMOTHY RONALD EDWARD JASON JEFFREY RYAN JACOB GARY NICHOLAS ERIC JONATHAN STEPHEN LARRY JUSTIN
SCOTT BRANDON BENJAMIN SAMUEL GREGORY ALEXANDER FRANK PATRICK RAYMOND JACK DENNIS JERRY TYLER AARON JOSE ADAM NATHAN HENRY DOUGLAS ZACHARY PETER
KYLE ETHAN WALTER NOAH JEREMY CHRISTIAN KEITH ROGER TERRY SEAN GERALD CARL HAROLD DYLAN ARTHUR LAWRENCE JESSE BRYAN BILLY BRUCE
GABRIEL JOE LOGAN ALBERT WILLIE ALAN EUGENE RUSSELL VINCENT PHILIP BOBBY JOHNNY BRADLEY ROY RALPH RANDY LOUIS MARIO JUAN CARLOS LUIS MIGUEL JORGE
PEDRO RAFAEL RICARDO FRANCISCO ANTONIO MANUEL JESUS ALEJANDRO JAVIER FERNANDO ROBERTO EDUARDO SERGIO HECTOR MARY PATRICIA JENNIFER LINDA
ELIZABETH BARBARA SUSAN JESSICA SARAH KAREN LISA NANCY BETTY MARGARET SANDRA ASHLEY KIMBERLY EMILY DONNA MICHELLE CAROL AMANDA DOROTHY MELISSA
DEBORAH STEPHANIE REBECCA SHARON LAURA CYNTHIA KATHLEEN AMY ANGELA SHIRLEY ANNA BRENDA PAMELA EMMA NICOLE HELEN SAMANTHA KATHERINE CHRISTINE
DEBRA RACHEL CAROLYN JANET CATHERINE MARIA HEATHER DIANE RUTH JULIE OLIVIA JOYCE VIRGINIA VICTORIA KELLY LAUREN CHRISTINA JOAN EVELYN JUDITH
MEGAN ANDREA CHERYL HANNAH JACQUELINE MARTHA GLORIA TERESA ANN SARA MADISON FRANCES KATHRYN JANICE JEAN ABIGAIL ALICE JULIA JUDY SOPHIA GRACE
DENISE AMBER DORIS MARILYN DANIELLE BEVERLY ISABELLA THERESA DIANA NATALIE BRITTANY CHARLOTTE MARIE KAYLA ALEXIS LORI ROSA ANA CARMEN GUADALUPE
LETICIA VERONICA YOLANDA ADRIANA ALMA JIM BOB TOM MIKE DAN DAVE STEVE CHRIS MATT TONY BILL RICK RON KEN TODD SHANE TRAVIS CODY DUSTIN DEREK GORDON GLENN DALE WAYNE CRAIG
CURTIS TROY BRETT CLINT""".split())
ENTITY = re.compile(r"\b(?:L\.?\s?L\.?\s?C|INC(?:ORPORATED)?|CORP(?:ORATION)?|CO|COMPANY|LTD|LIMITED|L\.?\s?P|L\.?\s?L\.?\s?P|P\.?\s?L\.?\s?L\.?\s?C|P\.?\s?C)\b\.?")
TYPE_OF = [("LLC", r"\bL\.?\s?L\.?\s?C\b"), ("INC", r"\bINC(?:ORPORATED)?\b"), ("CORP", r"\bCORP(?:ORATION)?\b"), ("LTD", r"\bLTD\b|\bLIMITED\b"),
           ("LLP", r"\bL\.?\s?L\.?\s?P\b"), ("LP", r"(?<![L.\s])\s*\bL\.?\s?P\b(?!\.?\s?L)"), ("PLLC", r"\bP\.?\s?L\.?\s?L\.?\s?C\b"), ("PC", r"\bP\.?\s?C\b")]
MAIN_ANY = re.compile(r"\s*(?:[\[(]\s*\**\s*MAIN\s*\**\s*[\])]|\*+\s*MAIN\b\s*\**|\bMAIN\s*\*+)\s*", re.I)   # stars on one or both sides (holdout D, Oct 18: "*MAIN", "***Main")


def _norm_person(n):
    return re.sub(r"[^A-Z ]", "", re.sub(r"\s+", " ", (n or "").upper())).strip()


def is_person(company, full_name=""):
    """True when the City's company field holds a person's own name, not a business (holdout, Oct 18: "Hill & Wilkinson",
    "Kingham Dalton Wilson" and "XBiotech" are businesses; holdout D: "Gordon Highlander" is a person's name). A name with a business word or a legal suffix is a
    business. Otherwise it is a person's name when it is the contractor's own name in the City record (either order), or when it
    is two or three plain words that start with a common first name and carry no "&", digit or initials."""
    up = (company or "").upper()
    if P.BUSINESS.search(up) or re.search(r"\b(?:GC|COMPANIES|COMMERCIAL|INDUSTRIES|ARCHITECTURAL|DESIGN|BUILD|CONCRETE|STEEL|ELECTRIC|ROOFING|PAVING)\b", up):
        return False
    c, f = _norm_person(company), _norm_person(full_name)
    if f and (c == f or c == " ".join(reversed(f.split())) or c.replace(" ", "") == f.replace(" ", "")):
        return True
    words = c.split()
    if re.search(r"[&\d/]", up) or not 2 <= len(words) <= 3 or words[0] not in FIRST_NAMES:
        return False
    # two plain words that start with a first name are a person's name whatever the City's full name says (holdout D, Oct 18:
    # "Gordon Highlander"); three words need the contractor's own surname to match ("Kingham Dalton Wilson" stays a business)
    return len(words) == 2 or not f or words[-1] == f.split()[-1]


def builder_name(r):
    """The general contractor as the list prints it, or None: the City's company name when it is a business, never a person's
    name (is_person), never a cleaning company (Chicago's gc_filter), and only when the City lists it as General Contractor."""
    if (r.get("contractor_trade") or "General Contractor").strip().upper() not in ("GENERAL CONTRACTOR",):
        return None
    nm = MAIN_ANY.sub(" ", (r.get("contractor_company_name") or "")).strip(" *,")
    nm = re.sub(r"\s+", " ", nm)
    if not nm or is_person(nm, r.get("contractor_full_name") or ""):
        return None
    return P.gc_filter(nm)


def entity_root(n):
    """A builder's name without its legal suffix, punctuation, case or a leading "The"."""
    u = re.sub(r"^\s*THE\s+", "", (n or "").upper())
    return re.sub(r"[^A-Z0-9]", "", ENTITY.sub(" ", u))


def entity_types(n):
    """The legal entity types a name carries (Co and Company are words, not types)."""
    u = (n or "").upper()
    return frozenset(t for t, pat in TYPE_OF if re.search(pat, u))


# ---------------------------------------------------------------- projects
WORK_RANK = {"NEW": 0, "ADDITION": 1, "ADDITION AND REMODEL": 1, "REMODEL": 2}
TYPES = ["New construction", "Finish-out", "Remodel or addition"]


def ptype(r):
    w = (r.get("work_class") or "").upper()
    if w == "NEW":
        return "New construction"
    if cls_no(r) in (1001, 1002) or re.search(r"FIRST TIME FINISH|FINISH[- ]?OUT", (r.get("description") or "").upper()):
        return "Finish-out"
    return "Remodel or addition"


HOME_WORDS = re.compile(r"\bUNITS?\b|RESIDEN|MULTI-?\s?FAMILY|APARTMENT|DWELLING")


def homes(rs):
    """Homes on a set of building permits: the City's housing units, added up. When every permit lists the same number, it is the
    project's own count repeated (4208 Medical Pkwy: 70 on each of 3 permits; 13114310: 295 on each of 6), so it counts once.
    Counted only on residential buildings (classes 104 to 106) and on finish-outs or remodels of homes; elsewhere the City often
    files 1 on non-residential work, and the list leaves Homes blank. Class 104 permits (three and four family buildings, one
    building each) always add up: 13352064 is two fourplexes, 8 homes."""
    small = sum(int(num(r.get("housing_units"))) for r in rs if cls_no(r) == 104)   # a class 104 permit is one 3 or 4 home building: add them
    n = [int(num(r.get("housing_units"))) for r in rs if cls_no(r) != 104]
    n = [x for x in n if x > 0]
    if len(n) >= 2 and len(set(n)) == 1:
        return small + n[0]
    return small + sum(n)


def group_projects(rows, since, today, week, min_cost=MIN_COST):
    """Building permits grouped into projects by master permit. Returns (projects, project reasons, permit reasons)."""
    groups = collections.OrderedDict()
    for r in rows:
        groups.setdefault(r.get("masterpermitnum") or ("P" + str(r.get("permit_number"))), []).append(r)
    projects, reasons, preasons = [], collections.Counter(), collections.Counter()
    for key, rs in groups.items():
        decided = [(r, keep_permit(r, since, today)) for r in rs]
        for r, (k, why) in decided:
            preasons[why] += 1
        kept = [r for r, (k, _) in decided if k]
        if not kept:
            live = [why for r, (k, why) in decided if day(r.get("issue_date")) >= since[:10] and is_open(r, today)]
            reasons[live[0] if live else "no open building permit in the window"] += 1
            continue
        cost = max(money_of(r) for r in kept)   # the kept, open, in-window permits only (holdout, Oct 18)
        if cost < min_cost:
            reasons["project valuation under $500,000"] += 1
            continue
        names = [g for g in (builder_name(r) for r in sorted(kept, key=lambda r: day(r.get("issue_date")))) if g]
        count = collections.Counter(P.entity_key(g) for g in names)
        first = {}
        for g in names:
            first.setdefault(P.entity_key(g), g)
        gcs = [first[k] for k, _ in sorted(count.items(), key=lambda kv: -kv[1])]
        if not gcs:
            reasons["no business listed as general contractor"] += 1
            continue
        kept.sort(key=lambda r: (WORK_RANK.get((r.get("work_class") or "").upper(), 3), cls_no(r) not in (104, 105, 106),
                                 -(num(r.get("total_new_add_sqft")) + num(r.get("remodel_repair_sqft"))),
                                 day(r.get("issue_date")), str(r.get("permit_number"))))
        lead = kept[0]
        # finaled building permits of the project issued in the window, of the kind the list keeps (an earlier phase of a phased
        # remodel counts: 13521831 has 17 finaled phases and 2 open, Oct 18)
        finals = [r for r in rs if (r.get("status_current") or "").upper() == "FINAL" and day(r.get("issue_date")) >= since[:10]
                  and keep_permit(dict(r, status_current="Active", expiresdate=""), since, today)[0]]
        # an extended expiry on any open building permit of the project counts, older ones included (design round 4: 12872034, a
        # 55-story tower whose 2022 floor finish-outs are still open, is work under way, not a permit just issued)
        stage = ("Near finish" if finals else "Work under way" if any(extended(r) for r in rs if is_open(r, today)) else "Permit issued")
        new_units = homes([r for r in kept if cls_no(r) in (104, 105, 106)])
        fin_units = homes([r for r in kept if cls_no(r) in (1000, 1001, 1002) and HOME_WORDS.search((r.get("description") or "").upper())])
        units = max(new_units, fin_units)
        built_units = homes([r for r in kept if cls_no(r) in (104, 105, 106) and (r.get("work_class") or "").upper() == "NEW"])
        addrs = []
        for r in kept:
            a = street_title(r.get("original_address1"))
            if a and a not in addrs:
                addrs.append(a)
        lat = lon = None
        for r in kept:
            lat, lon = coord(r)
            if lat is not None:
                break
        types = {ptype(r) for r in kept}
        issued = min(day(r.get("issue_date")) for r in kept)
        scopes = []
        for r in kept:
            s = austin_scope(r.get("description"), limit=300)
            if s not in scopes:
                scopes.append(s)
        projects.append({
            "permit": str(key),
            "issued": issued,
            "lastIssued": max(day(r.get("issue_date")) for r in kept),
            "type": next(t for t in TYPES if t in types),
            "scope": austin_scope(lead.get("description")),
            "scopeFull": " | ".join(scopes[:12]) + (f" | and {len(scopes) - 12} more building permits" if len(scopes) > 12 else ""),
            "units": units or None,
            "newUnits": built_units,
            "cost": int(cost + 0.5),
            "address": addrs[0] + (f" (+{len(addrs) - 1} more)" if len(addrs) > 1 else "") if addrs else "",
            "communityArea": (lead.get("original_zip") or "").strip()[:5],
            "district": str(lead.get("council_district") or "").split(".")[0],
            "status": "Active",
            "milestone": stage,
            "buildings": len(kept),
            "buildingsFinal": len(finals),
            "permits": [{"n": r.get("permit_number"), "issued": day(r.get("issue_date")), "expires": day(r.get("expiresdate")),
                         "cls": r.get("permit_class") or "", "work": r.get("work_class") or "", "units": int(num(r.get("housing_units"))) or None,
                         "scope": austin_scope(r.get("description"), limit=160), "link": r.get("link") if isinstance(r.get("link"), str) else (r.get("link") or {}).get("url", "")}
                        for r in kept[:40]],
            "gc": gcs,
            "lat": lat, "lon": lon, "geo": "city" if lat is not None else "",
            "newThisWeek": issued >= week,
        })
        reasons["kept"] += 1
    return projects, reasons, preasons


def top_builders(projects, n=12):
    return P.top_builders(projects, n)


def unify_builders(projects):
    """One builder per legal entity, spelled one way everywhere (holdout and design director, Oct 18). Names with the same root
    (permits_chicago's punctuation and suffix spelling, plus Co and Company read as words) and the same entity types are one
    builder ("The Struthoff Company, Inc." = "The Struthoff Co. Inc."). A name with no entity type joins the one typed entity of
    its root ("Rogers Obrien Construction" joins "Rogers-O'Brien Construction Co. Ltd"; "Zapalac/Reed Construction Company" joins
    "Zapalac/Reed Construction Co., LP"); an LLC and an Inc of one root stay two builders. Every project then carries the
    group's one spelling: the one most permits use, then the shortest. Returns {spelling: canonical spelling}."""
    names = collections.Counter(g for x in projects for g in x["gc"])
    groups = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    for g, n in names.items():
        groups[entity_root(g)][entity_types(g)][g] += n
    change = {}
    for root, by_type in groups.items():
        typed = [t for t in by_type if t]
        if len(typed) == 1 and frozenset() in by_type:
            by_type[typed[0]].update(by_type.pop(frozenset()))
        for t, spellings in by_type.items():
            best = sorted(spellings.items(), key=lambda kv: (not entity_types(kv[0]), -kv[1], len(kv[0]), kv[0]))[0][0]
            for g in spellings:
                change[g] = best
    for x in projects:
        x["gc"] = list(dict.fromkeys(change.get(g, g) for g in x["gc"]))
    return change


def merge_twins(projects):
    """One development filed under two master permits is one lead (holdout spirit of Chicago's dedupe): two projects at the same
    street address, with the same valuation and the same builder, become one, with every building permit of both. The list,
    the free page, the app and the workbook then count its valuation once. Returns (projects, merged master numbers)."""
    groups = collections.OrderedDict()
    for x in projects:
        key = ((x["address"] or "").split(" (+")[0].upper(), x["cost"], P.entity_key(x["gc"][0]) if x["gc"] else "")
        groups.setdefault(key, []).append(x)
    out, merged = [], []
    order = {s: i for i, s in enumerate(["Near finish", "Work under way", "Permit issued"])}
    for (addr, _, _), xs in groups.items():
        if len(xs) == 1 or not addr:
            out += xs
            continue
        xs.sort(key=lambda x: (x["issued"], x["permit"]))
        m = dict(xs[0])
        m["masters"] = [x["permit"] for x in xs]
        merged += m["masters"][1:]
        m["issued"] = min(x["issued"] for x in xs)
        m["lastIssued"] = max(x["lastIssued"] for x in xs)
        m["type"] = next(t for t in TYPES if any(x["type"] == t for x in xs))
        m["milestone"] = min((x["milestone"] for x in xs), key=lambda st: order.get(st, 9))
        m["buildings"] = sum(x["buildings"] for x in xs)
        m["buildingsFinal"] = sum(x["buildingsFinal"] for x in xs)
        m["units"] = sum(x["units"] or 0 for x in xs) or None
        m["permits"] = [q for x in xs for q in x["permits"]][:40]
        m["scopeFull"] = " | ".join(dict.fromkeys(part for x in xs for part in x["scopeFull"].split(" | ")))
        m["gc"] = list(dict.fromkeys(g for x in xs for g in x["gc"]))
        n = sum(int(re.search(r"\(\+(\d+) more\)", x["address"]).group(1)) if "(+" in x["address"] else 0 for x in xs)   # same street address, the extras add
        m["address"] = xs[0]["address"].split(" (+")[0] + (f" (+{n} more)" if n else "")
        m["newThisWeek"] = all(x["newThisWeek"] for x in xs)
        if m.get("lat") is None:
            for x in xs:
                if x.get("lat") is not None:
                    m["lat"], m["lon"], m["geo"] = x["lat"], x["lon"], x.get("geo", "city")
                    break
        out.append(m)
    return out, merged


def total_cost(projects):
    """The list's total valuation: the sum of its projects' valuations (merge_twins has already counted each development once)."""
    return sum(x["cost"] for x in projects)


# ---------------------------------------------------------------- the pull
def pull(where, select=FIELDS, order=":id"):
    """Every row matching where, paged until a short page, then checked against the City's own count: the list is never a
    capped page."""
    want = int(get(f"{PORTAL}/resource/{DATASET}.json", {"$select": "count(*) AS n", "$where": where})[0]["n"])
    out, off, seen = [], 0, set()
    while True:
        page = get(f"{PORTAL}/resource/{DATASET}.json", {"$select": select, "$where": where, "$order": order, "$limit": 5000, "$offset": off})
        for r in page:
            k = r.get("permit_number")
            if k not in seen:
                seen.add(k); out.append(r)
        if len(page) < 5000:
            break
        off += 5000
    if len(out) < want:
        raise SystemExit(f"pull short: {len(out)} rows of {want} for {where[:120]}")
    return out


def fetch(now, days=DAYS):
    since = P.window_start(now, days)
    where = f"issue_date >= '{since}' AND permittype='BP' AND permit_class_mapped='Commercial'"
    rows = pull(where)
    have = {r.get("permit_number") for r in rows}
    masters = sorted({r.get("masterpermitnum") for r in rows if r.get("masterpermitnum")})
    for i in range(0, len(masters), 60):
        chunk = ",".join(f"'{m}'" for m in masters[i:i + 60])
        for r in pull(f"masterpermitnum in({chunk}) AND permittype='BP'"):
            if r.get("permit_number") not in have:
                have.add(r.get("permit_number")); rows.append(r)
    return since, where, rows


TERMS_READ = """== City of Austin Open Data Terms of Use, read Oct 18, 2026 at https://data.austintexas.gov/stories/s/ranj-cccq (in Todd's browser; the
runner cannot extract the PDF's text). Key terms as read:
- The data is public domain, "offered free and without restriction". No indemnity clause.
- Attribution should credit the City of Austin and the source department (here Austin Development Services). The City logo is not
  to be used, and ProofNotFluff does not use it.
- The City "may require the termination of any and all displays, distribution, or other use".
- Confidentiality: users "will not take any measures to re-identify the data or to contact individuals whose information is
  represented by the data" and "shall not combine the data with data from any other datasets for the purpose of re-identification
  of individuals".
Applied in the product: credit "City of Austin, Austin Development Services"; Terms clause "Businesses only" (contact businesses only,
never identify or contact individual people or combine the data to do so); Availability clause (the City may stop or change the feed).
"""


def terms_text():
    """The City of Austin's own words, for the Legal desk and the product's disclaimer: the Issued Construction Permits
    dataset description (it carries Austin Development Services' data disclaimer) and the Open Data Terms of Use."""
    parts = [f"Fetched: {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}", ""]
    try:
        m = get(f"{PORTAL}/api/views/{DATASET}.json")
        parts += [f"== Dataset {DATASET_PAGE}", f"Name: {m.get('name', '')}", f"Attribution: {m.get('attribution', '')}",
                  f"License: {(m.get('license') or {}).get('name', '')}", "", "Description:", m.get("description") or "", ""]
    except SystemExit as e:
        parts.append(f"Could not fetch the dataset description: {e}")
    try:
        import io
        from pypdf import PdfReader
        raw = urllib.request.urlopen(urllib.request.Request(TERMS_PDF, headers=UA), timeout=120).read()
        text = "\n".join((pg.extract_text() or "") for pg in PdfReader(io.BytesIO(raw)).pages)
        if sum(ch.isalpha() for ch in text) < 0.5 * max(1, len(text)):   # the PDF's embedded fonts give glyph codes, not words
            text = f"(The PDF's text could not be extracted as words; the same Terms of Use are on the web at {TERMS_URL}.)"
        parts += [f"== Terms of Use PDF {TERMS_PDF}", "", text.strip(), ""]
    except Exception as e:
        parts.append(f"Could not read the Terms of Use PDF {TERMS_PDF}: {e}")
    return "\n".join(parts) + "\n" + TERMS_READ


CENSUS = "https://geocoding.geo.census.gov/geocoder/locations/addressbatch"


def geo_street(addr):
    """The street address alone, for the geocoder: no "(+2 more)", unit, building, suite or floor parts."""
    a = re.sub(r"\s*\(\+\d+ more\)$", "", addr or "")
    return re.sub(r"\s+(?:Unit|Bldg|Building|Ste|Suite|Flr|Floor|Apt|#)\b.*$", "", a, flags=re.I).strip()


def geocode_missing(projects):
    """A map pin for projects whose City rows carry no coordinates (about half of Austin's building permits): the US Census
    Bureau's public geocoder, matched on the street address and ZIP code. Such a pin is marked geo "census" so the app can say
    so. A project the geocoder cannot match keeps no pin. Failures never stop the list."""
    want = [x for x in projects if x.get("lat") is None and geo_street(x.get("address"))]
    if not want:
        return 0
    lines = "".join(f'{i},"{geo_street(x["address"])}",Austin,TX,{x.get("communityArea") or ""}\n' for i, x in enumerate(want))
    bnd = "pnf" + str(int(time.time()))
    body = (f"--{bnd}\r\nContent-Disposition: form-data; name=\"benchmark\"\r\n\r\nPublic_AR_Current\r\n"
            f"--{bnd}\r\nContent-Disposition: form-data; name=\"addressFile\"; filename=\"a.csv\"\r\nContent-Type: text/csv\r\n\r\n{lines}\r\n--{bnd}--\r\n").encode()
    text = ""
    for i in range(3):   # the batch service is sometimes slow or down (Oct 18: 0 of 77 on one run): retry, then one address at a time
        try:
            req = urllib.request.Request(CENSUS, data=body, headers=dict(UA, **{"Content-Type": f"multipart/form-data; boundary={bnd}"}))
            text = urllib.request.urlopen(req, timeout=300).read().decode("utf-8", "replace")
            if "Match" in text:
                break
        except Exception as e:
            print(f"census batch geocoder try {i + 1} failed ({e})")
        time.sleep(10 * (i + 1))
    if "Match" not in text:
        rows = []
        for i, x in enumerate(want):
            q = urllib.parse.urlencode({"address": f"{geo_street(x['address'])}, Austin, TX {x.get('communityArea') or ''}",
                                        "benchmark": "Public_AR_Current", "format": "json"})
            try:
                m = json.loads(urllib.request.urlopen(urllib.request.Request(CENSUS.replace("addressbatch", "onelineaddress") + "?" + q, headers=UA),
                                                      timeout=60).read().decode())["result"]["addressMatches"]
            except Exception:
                continue
            if m:
                rows.append([str(i), "", "Match", "", "", f'{m[0]["coordinates"]["x"]},{m[0]["coordinates"]["y"]}'])
        import io as _io, csv as _csv
        buf = _io.StringIO(); _csv.writer(buf).writerows(rows); text = buf.getvalue()
    import csv, io
    n = 0
    for row in csv.reader(io.StringIO(text)):
        if len(row) >= 6 and row[2] == "Match" and row[0].isdigit() and int(row[0]) < len(want):
            try:
                lon, lat = (float(v) for v in row[5].split(","))
            except ValueError:
                continue
            if 29.5 < lat < 31.0 and -98.5 < lon < -97.0:
                x = want[int(row[0])]
                x["lat"], x["lon"], x["geo"] = round(lat, 6), round(lon, 6), "census"; n += 1
    return n


def slim(x):
    """A project as the public free sample shows it: no per-permit detail and no full scope text."""
    return {k: v for k, v in x.items() if k not in ("scopeFull", "permits", "lat", "lon", "geo", "lastIssued")}


def build_lists(rows, now, since, days=DAYS, min_cost=MIN_COST):
    today = central_today(now)
    week = (today - dt.timedelta(days=7)).isoformat()
    projects, reasons, preasons = group_projects(rows, since, today, week, min_cost)
    unify_builders(projects)
    projects, merged = merge_twins(projects)
    if merged:
        reasons["kept"] -= len(merged)
        reasons["second master permit of a development already listed"] += len(merged)
    projects.sort(key=lambda x: (-x["cost"], x["issued"], x["permit"]))
    return projects, reasons, preasons


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=DAYS)
    ap.add_argument("--min-cost", type=int, default=MIN_COST)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--full", default="", help="also write every kept project here (the paid list; runner only, never committed in the clear)")
    ap.add_argument("--audit", default="", help="also write the de-identified rules audit here")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    meta = get(f"{PORTAL}/api/views/{DATASET}.json")
    upd = meta.get("rowsUpdatedAt") or meta.get("viewLastModified")
    upd_iso = dt.datetime.fromtimestamp(upd, dt.timezone.utc).isoformat(timespec="seconds") if upd else ""
    since, where, rows = fetch(now, a.days)
    projects, reasons, preasons = build_lists(rows, now, since, a.days, a.min_cost)
    geocoded = geocode_missing(projects)
    near = [x for x in projects if x["milestone"] == "Near finish"]
    by_zip = collections.Counter(x["communityArea"] for x in projects if x["communityArea"])
    sample = {
        "source": {
            "name": "City of Austin, Issued Construction Permits", "url": DATASET_PAGE, "rowsUpdatedAt": upd_iso,
            "fetchedAt": now.isoformat(timespec="seconds"), "license": (meta.get("license") or {}).get("name", ""),
            "attribution": meta.get("attribution", ""),
            "modified": (f"Filtered by ProofNotFluff: commercial building permits issued in the last {P.months(a.days)}, still Active, grouped into "
                         f"projects by the City's master permit, project valuation ${a.min_cost:,} or more (the largest valuation on its open "
                         "building permits on the list, counted once; finaled, shell and garage permits do not count), with a business listed as general contractor; structures that are not buildings "
                         "(carports, pergolas, canopies, enclosures, pools, EV chargers), parking garages, houses, duplexes and three-unit "
                         "buildings, shell-only buildings, interior demolition, repairs, and roof, equipment, sign, elevator, site and exterior-only "
                         "work left out; cleaning companies listed as contractor left out; only project-level and business fields kept."),
            "terms": TERMS_URL,
        },
        "window": {"from": since[:10], "to": central_today(now).isoformat()},
        "counts": {"fetched": len(rows), "kept": len(projects), "excluded": dict(reasons), "permitReasons": dict(preasons),
                   "keptByType": dict(collections.Counter(x["type"] for x in projects)),
                   "keptCost": total_cost(projects),
                   "keptUnits": sum(x.get("newUnits") or 0 for x in projects),
                   # valuations the City filed one or a few dollars over a round figure ($18,000,001, $500,002): the footnote's examples
                   "oddCosts": sorted({x["cost"] for x in projects if 0 < x["cost"] % 1000 < 10}, reverse=True)[:2],   # homes in new buildings only (the free page says "new homes")
                   "keptBuildings": sum(x["buildings"] for x in projects),
                   "topAreas": by_zip.most_common(8), "topGCs": top_builders(projects), "nearFinish": len(near),
                   "builders": len({P.entity_key(g) for x in projects for g in x["gc"]}),
                   "mapped": sum(1 for x in projects if x.get("lat") is not None), "geocoded": geocoded},
        "projects": [slim(x) for x in projects[: a.top]],
        "nearFinish": [slim(x) for x in sorted(near, key=lambda x: (-x["cost"], x["issued"]))[:10]],
    }
    profile = {"fetchedAt": sample["source"]["fetchedAt"], "rowsUpdatedAt": upd_iso, "columns": [c.get("fieldName") for c in meta.get("columns", [])],
               "workClasses": dict(collections.Counter(r.get("work_class") for r in rows)),
               "statuses": dict(collections.Counter(r.get("status_current") for r in rows)),
               "classes": dict(collections.Counter(r.get("permit_class") for r in rows).most_common(40)),
               "contractorTrades": dict(collections.Counter(r.get("contractor_trade") for r in rows)),
               "permitReasons": dict(preasons), "license": sample["source"]["license"], "where": where}
    json.dump(sample, open(os.path.join(OUT, "sample.json"), "w"), indent=1)
    json.dump(profile, open(os.path.join(OUT, "profile.json"), "w"), indent=1)
    open(os.path.join(OUT, "source-terms.txt"), "w").write(terms_text())
    if a.audit:
        audit(rows, since, central_today(now), a.audit)
    if a.full:
        json.dump({"source": sample["source"], "window": sample["window"], "counts": sample["counts"], "projects": projects},
                  open(a.full, "w"), indent=1)
    print(json.dumps({"fetched": len(rows), "kept": len(projects), "near": len(near), "excluded": dict(reasons)}))


# ---------------------------------------------------------------- planted cases
# Real City of Austin wording (the Oct 18, 2026 audit, commit 0fbf3ae, trimmed): (fields, keep?)
C = "Commercial"
PERMIT_CASES = [
    # rule 2: the work. Kept: new buildings, finish-outs, remodels with interior work
    ({"permit_class": "C- 105 Five or More Family Bldgs", "work_class": "New", "housing_units": "30",
      "description": "ePlan: Commercial Expedited Review - [APPROVED] New Construction of New Apartments with Private Garages (38520 SF)."}, True),
    ({"permit_class": "C-1001 Commercial Finish Out", "work_class": "Remodel", "description": "ePlan: Expedited Review - First Time Finish Out for Units."}, True),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel",
      "description": "ePlan: Expedited Review - First Time Tenant Finish-Out to create Restaurant with Mezzanine (10643 SF)"}, True),
    ({"permit_class": "C- 328 Commercial Other Nonresident Bldg", "work_class": "New",
      "description": "ePlan: Commercial Expedited Review - [APPROVED] New Construction of New club Building- Also Contains Leasing Mail Finess and Co- Work (8953 SF)."}, True),
    ({"permit_class": "C- 104 Three & Four Family Bldgs", "work_class": "New", "housing_units": "4",
      "description": "ePlan: Commercial Expedited Review - New Construction 4 Plex. (4 units - 9807 sf.)."}, True),
    ({"permit_class": "C- 437 Addn, Alter, Convn-NonRes", "work_class": "Addition",
      "description": "ePlan: Commercial Expedited Review - [Public Project] Addition to Existing High School. Work to include New Competition Gym and Locker Rooms ."}, True),
    ({"permit_class": "C- 437 Addn, Alter, Convn-NonRes", "work_class": "Addition and Remodel",
      "description": "ePlan: Commercial Expedited Review - Interior Remodel to Existing Convenience Store  Scope of Work to Include New Addition to Existing Building ."}, True),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel",
      "description": "Interior renovations new secure entry vestibule & security fencing re-roofing elevator replacement exterior facade renovations."}, True),
    ({"permit_class": "C- 105 Five or More Family Bldgs", "work_class": "New",
      "description": "ePlan: Expedited Review - New Apartments - Fire Area 1C - also contains Retail Shell (Separate Building Permit) 53870 SF"}, True),
    ({"permit_class": "C- 327 Stores & Customer Services", "work_class": "New",
      "description": "New Construction of a 7000 SF shell retail building which includes a 5000 SF convenience store finish-out and two (2) unfinished future tenant lease spaces"}, True),
    ({"permit_class": "C- 327 Stores & Customer Services", "work_class": "New",   # holdout D: a new store building, kept despite "fuel"
      "description": "New Construction of Convenience Store Fuel Canopy and Dumpster Enclosure (9566 SF)"}, True),
    ({"permit_class": "C- 437 Addn, Alter, Convn-NonRes", "work_class": "Addition and Remodel",
      "description": "Remodel and Addition to Existing Fuel Station 2023 001465 DA - Approved"}, False),
    ({"permit_class": "C-1001 Commercial Finish Out", "work_class": "Remodel",
      "description": "ePlan: Commercial Expedited Review - [APPROVED] Interior Finish out of Shell Space to a Dance Studio to include 3 Flex Spaces 3 Restrooms and Entry Se"}, True),
    ({"permit_class": "C- 326 Schools & Other Educational Bldgs", "work_class": "New",
      "description": "Construction of a new 51250 sq. ft single story middle school.                   210-850-8661"}, True),
    # left out: structures that are not buildings, parking garages, houses and small buildings
    ({"permit_class": "C- 329 Com Structures Other Than Bldg", "work_class": "New",
      "description": "ePlan: Commercial Expedited Review - [SMART HOUSING] New Construction of Dumpster Enclosure."}, False),
    ({"permit_class": "C- 329 Com Structures Other Than Bldg", "work_class": "New",
      "description": "ePlan: Expedited Review - New Construction of Pergola - Residential Units."}, False),
    ({"permit_class": "C- 329 Com Structures Other Than Bldg", "work_class": "New",
      "description": "ePlan: Expedited Review - New Construction of Restroom Cabana ."}, False),   # tricky: a building word, but the City's class 329
    ({"permit_class": "C- 321 Pkg Garage Bldg & Open Deck", "work_class": "New",
      "description": "ePlan: Commercial Expedited Review - [CONCURRENT] New Construction of New Detached Garage (1667 SF)."}, False),
    ({"permit_class": "C- 321 Pkg Garage Bldg & Open Deck", "work_class": "New",
      "description": "ePlan: Expedited Review - New Construction of Parking Garage - Amenities Area Contains Club Fitness Gaming Bowling Alley and Pool Deck."}, False),  # tricky
    ({"permit_class": "C- 104 Three & Four Family Bldgs", "work_class": "New", "housing_units": "3",
      "description": "ePlan: Expedited Review - New Construction of Multi Family Townhouse Building."}, False),
    ({"permit_class": "C- 103 Two Family Bldgs", "work_class": "New", "housing_units": "2",
      "description": "ePlan: Expedited Review - New Construction of Multi Family Townhouse Building."}, False),
    ({"permit_class": "R- 101 Single Family Houses", "permit_class_mapped": "Residential", "work_class": "New",
      "description": "New two story single family residence with attached garage"}, False),
    # left out: shell only, demolition, repair
    ({"permit_class": "C- 105 Five or More Family Bldgs", "work_class": "Shell",
      "description": "ePlan: Expedited Review - New Shell Building of a 57-Story Mixed Use Multi-Family Bldg. with Parking Garage."}, False),
    ({"permit_class": "C- 320 Industrial Bldgs", "work_class": "New",
      "description": "New ground-up tilt wall shell warehouse construction with potential future office areas for administrative purposes."}, False),
    ({"permit_class": "C- 324 Office, Bank & Professional Bldgs", "work_class": "New",
      "description": "CORE AND SHELL PRE-ENGINEERED METAL BUILDING WITH INDIVIDUAL TENANT LEASE SPACES."}, False),
    ({"permit_class": "C- 320 Industrial Bldgs", "work_class": "New",
      "description": "New construction of Office Warehouse Shell.(NOT FOR OCCUPANCY) (Previous review expired 2023-011412 PR)"}, False),
    ({"permit_class": "C- 437 Addn, Alter, Convn-NonRes", "work_class": "Addition",
      "description": "ePlan: Expedited Review - Addition and Change of Use from Mercantile to Administrative/Medical Office Shell Space  *NOT FOR OCCUPANCY*"}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Interior Demo Non-Structural", "description": "Interior non structural demolition"}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Repair", "description": "Repair of fire damaged wall"}, False),
    # left out: work that never needs a construction clean
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel",
      "description": "TPO Roof Overlay. Adding 1/2 Coverboard and TPO Membrane over Existing Roof. Existing warehouse."}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel", "description": "Simple re-roof. Existing Austin Water offices."}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel", "description": "Replacement of RTUs for existing shopping mall."}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel",
      "description": "Replacement of exterior mechanical units roofing membrane and roof rigid insulation clerestory glazing sidewalks improvements new kitchen grease trap"}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel",
      "description": "ePlan: Commercial Expedited Review - Remodel Hospital - Level 2 - Sterilizer Equipment Replacement ."}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel",
      "description": "ePlan: Commercial Expedited Review - Interior Remodel to Existing Elevator ."}, False),   # tricky: says interior remodel
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel",
      "description": "ePlan: Commercial Expedited Review - Interior Remodel to Existing Parking Garage Elevator ."}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel",
      "description": "ePlan: Commercial Expedited Review - [BETTER BUILDER] Interior Remodel for Sector 144 MEPs and Replaced Raised Access Floor ."}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel", "description": "ePlan: Commercial Expedited Review -Exterior Remodel to Patio ."}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel",
      "description": "ePlan: Expedited Review - New Construction of EV Charging Station for Multi-Family Bldgs."}, False),
    ({"permit_class": "C- 437 Addn, Alter, Convn-NonRes", "work_class": "Addition and Remodel",
      "description": "ePlan: Commercial Expedited Review - [APPROVED] Addition and Remodel to Existing Exterior Hospital Services. Work to include replacing existing Generator and Fuel Tank."}, False),
    ({"permit_class": "C- 437 Addn, Alter, Convn-NonRes", "work_class": "Addition",
      "description": "ePlan: Commercial Expedited Review - New Addition of Terrace with Lighted Trellis ."}, False),
    ({"permit_class": "C- 328 Commercial Other Nonresident Bldg", "work_class": "New",
      "description": "BAUS - Airport Project: Install Necessary Fuel Infrastructure and Equipment to Support a Future Concourse hydrant fuel system"}, False),
    ({"permit_class": "C- 328 Commercial Other Nonresident Bldg", "work_class": "New", "description": "ePlan: Commercial Expedited Review - New Gen Set and Catwalk. (400 SF)"}, False),
    ({"permit_class": "C- 322 Service Station & Repair Garage", "work_class": "New",
      "description": "Installation of fourteen (14) 40x8 intermodal shipping containers 12 of which will be connected via pre-engineered pre-manufactured roof systems"}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel",
      "description": "FIS- Expansion that will reconfigure the Existing Bag Claim system to be used as Domestic/ International."}, False),
    # holdout-style tricky cases from the Oct 18 audit of every open permit
    ({"permit_class": "C- 318 Amusement, Social & Rec Bldgs", "work_class": "New", "description": "Piers for Skyblazer attraction only no building"}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel",
      "description": "RE ROOF - Remove existing shingle roof down to the decking. Install all new materials including ice and water shield"}, False),
    ({"permit_class": "C- 328 Commercial Other Nonresident Bldg", "work_class": "New", "description": "New Garage (1566 SF)"}, False),
    ({"permit_class": "C- 328 Commercial Other Nonresident Bldg", "work_class": "New", "description": "New Cabana (100 SF)"}, False),
    ({"permit_class": "C- 328 Commercial Other Nonresident Bldg", "work_class": "New", "description": "ePlan: Commercial Expedited Review - [APPROVED] New Construction Prefab Guard Booth."}, False),
    ({"permit_class": "C- 318 Amusement, Social & Rec Bldgs", "work_class": "New",
      "description": "ePlan: Commercial Expedited Review - New Construction of Structured Parking with Tennis Court area on Top for Austin Country Club (20688 SF)"}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel",
      "description": "ePlan: Commercial Expedited Review - Interior Remodel to Existing Office - Phase 6A - 4TH floor Outdoor Trellis. (131364 SF Total)"}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel",
      "description": "ePlan: Commercial Expedited Review - [PUBLIC PROJECT] Interior Remodel to Austin High School. Roof Recovering at Theater Building.  ."}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel",
      "description": "ePlan: Commercial Expedited Review - Interior Remodel of Phase II to Existing Food Warehouse Facility. Autostore Automatic High-Pile racking system installation"}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel",
      "description": "ePlan: Commercial Expedited Review - Interior Remodel to Existing Food Warehouse Facility. Phase 1 includes all Remodel Scope Outside of the Autostore Racking Systems."}, True),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel", "description": "BAUS: GSE Renovation - New Triturator Wash Bay."}, False),
    ({"permit_class": "C-1001 Commercial Finish Out", "work_class": "Remodel",
      "description": "ePlan: Expedited Review - Fist Time Finish Out for Exterior Amenity Space - Contains Pool Deck (Pool to be permitted separately) and Terrace."}, False),
    ({"permit_class": "C- 105 Five or More Family Bldgs", "work_class": "New",
      "description": "Affordability Unlocked and Smart Housing development. 150 unit 4 story elevator served multifamily apartment."}, True),
    ({"permit_class": "C- 319 Churches and Othr Religious Bldgs", "work_class": "New",
      "description": "Replacement of new accessible platform and toilet rooms. New exterior and interior finishes and furnishes. Replacement of electrical and mechanical"}, True),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel",
      "description": "ePlan: Commercial Expedited Review - Exterior Remodel to Existing Office. Phase 1 Including non structural partitions ceilings finishes and food service improvements."}, True),
    ({"permit_class": "C- 437 Addn, Alter, Convn-NonRes", "work_class": "Addition",
      "description": "ePlan: Commercial Expedited Review - Changed of Use from Warehouse to Indoor Sports and Recreation. Scope of Work to Include New Wooden Deck Fence Drainage"}, True),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Repair",
      "description": "Interior Remodel and Change of Use from Business Office to Event Space (5128 SF)"}, True),   # the City's Repair class, a real remodel
    ({"permit_class": "C- 324 Office, Bank & Professional Bldgs", "work_class": "Shell",
      "description": "Tenant improvement for mercantile space on ground floor.  Floor 1 Building 1 Suite GAR 1."}, True),   # the City's Shell class, a real TI
    ({"permit_class": "C- 324 Office, Bank & Professional Bldgs", "work_class": "Shell",
      "description": "Remaining portion of shell building to remain unfinished after completion of TI work including restaurant for future development."}, False),
    ({"permit_class": "C- 327 Stores & Customer Services", "work_class": "Shell",
      "description": "ePlan: Expedited Review - New Retail Shell Building - Below the Podium in Fire Area 1C (Future Retail Finish-outs are addressed 2700 2704 2708)"}, False),
    ({"permit_class": "C- 437 Addn, Alter, Convn-NonRes", "work_class": "Addition",
      "description": "Phase B of Interior renovation to existing industrial facility CU area with added new exterior equipment including wet scrubber."}, False),
    ({"permit_class": "C- 326 Schools & Other Educational Bldgs", "work_class": "Addition", "description": "New portable and flatwork. 2026-067987 DA"}, False),
    ({"permit_class": "C- 437 Addn, Alter, Convn-NonRes", "work_class": "Addition",
      "description": "Addition of a covered porch and canopy. demolition of 4 parking spaces relocation of ADA parking and construction of ada access ramps."}, False),
    ({"permit_class": "C- 105 Five or More Family Bldgs", "work_class": "New", "description": "CONSTRUCT NEW MULTIFAMILY COMPLEX - CARPORT"}, False),
    ({"permit_class": "C- 105 Five or More Family Bldgs", "work_class": "New", "description": "CONSTRUCT NEW MULTIFAMILY COMPLEX     BLDG 1 TYPE A"}, True),
    # holdout, Oct 18: trade work first with only minor finishes is out; interior partitions and ceilings keep an exterior remodel in
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel",
      "description": "Replacement of exterior mechanical units roofing membrane and roof rigid insulation clerestory glazing sidewalks improvements new kitchen "
                     "grease trap and interior renovations to include ADA water cooler and kitchen finishes cabinets equipment"}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel",
      "description": "ePlan: Commercial Expedited Review - Exterior Remodel to Existing Office. Phase 1 Including non structural partitions ceilings finishes "
                     "and food service improvements. Work to include Remodel to Existing Patio. Phase 1 (163500 SF)"}, True),
    # rulings on the holdout's borderline cases (launch record): process equipment and a baggage system are out, a training building is in
    ({"permit_class": "C- 437 Addn, Alter, Convn-NonRes", "work_class": "Addition",
      "description": "Phase A of Interior renovation to existing industrial facility for photo metal & etch chemical storage and IMP areas with added new "
                     "exterior equipment including wet scrubber and emergency generator"}, False),
    ({"permit_class": "C- 328 Commercial Other Nonresident Bldg", "work_class": "New",
      "description": "ePlan: Commercial Expedited Review - New Construction of New Training Building."}, True),
    ({"permit_class": "C- 320 Industrial Bldgs", "work_class": "New",
      "description": "62435 SF ground up new light manufacturer. Project will be structural steel tilt wall construction with associated site work and interior finish out."}, True),
    ({"permit_class": "C- 322 Service Station & Repair Garage", "work_class": "New", "description": "New Construction of an Express Car Wash."}, True),
    ({"permit_class": "C- 104 Three & Four Family Bldgs", "work_class": "New", "housing_units": "4",
      "description": "New construction of a multi-family fourplex"}, True),
]


def selftest():
    bad = []
    since, today = "2024-10-18T00:00:00", dt.date(2026, 10, 18)
    base = {"permittype": "BP", "permit_class_mapped": C, "status_current": "Active", "issue_date": "2026-05-01T00:00:00.000",
            "expiresdate": "2026-12-01T00:00:00.000"}
    for fields, want in PERMIT_CASES:
        got = keep_permit(dict(base, **fields), since, today)
        if got[0] != want:
            bad.append((fields["description"][:90], want, got))
    # rule 1: the window and the City's status
    for issued, status, expires, want in [
            ("2026-10-12", "Active", "2027-04-10", True),
            ("2024-10-18", "Active", "2026-11-01", True),      # first day of the window: Oct 18, 2026 in Austin, two years back
            ("2024-10-17", "Active", "2026-11-01", False),     # one day past 24 months
            ("2025-01-10", "Final", "2025-07-10", False),
            ("2025-01-10", "Expired", "2025-07-10", False),
            ("2025-01-10", "Withdrawn", "", False), ("2025-01-10", "VOID", "", False),
            ("2025-01-10", "Cancelled - Contractor Required", "", False), ("2026-10-01", "Pending Permit", "", False),
            ("2025-01-10", "Active", "2026-10-17", False),     # Active in the record but past the City's expiry date
            ("2025-01-10", "Active", "", True)]:
        r = dict(base, **PERMIT_CASES[0][0], issue_date=issued + "T00:00:00.000", status_current=status, expiresdate=expires and expires + "T00:00:00.000")
        if keep_permit(r, since, today)[0] != want:
            bad.append(("window", issued, status, expires, want))
    assert P.window_start(dt.datetime(2026, 10, 18, 15, 0, tzinfo=dt.timezone.utc)) == "2024-10-18T00:00:00"
    assert P.window_start(dt.datetime(2026, 10, 19, 3, 30, tzinfo=dt.timezone.utc)) == "2024-10-18T00:00:00", "Central date of the pull"
    assert central_today(dt.datetime(2026, 10, 19, 3, 30, tzinfo=dt.timezone.utc)) == dt.date(2026, 10, 18)
    # rule 4: the builder is a business, never a person's name, never a cleaning company; one key per legal entity
    for raw, trade, want in [("HARVEY-CLEARY BUILDERS ***MAIN***", "General Contractor", "Harvey-Cleary Builders"),
                             ("CM CONSTRUCTORS *MAIN*", "General Contractor", "CM Constructors"),
                             ("Turner Construction Company", "General Contractor", "Turner Construction Company"),
                             ("JOHN SMITH", "General Contractor", None), ("Maria Lopez", "General Contractor", None),
                             ("SPARKLE CLEANING SERVICES LLC", "General Contractor", None),
                             ("ACME ELECTRIC LLC", "Electrical Contractor", None), ("", "General Contractor", None),
                             # completeness holdout, Oct 18: businesses whose names look like surnames are businesses
                             ("HILL & WILKINSON", "General Contractor", "Hill & Wilkinson"),
                             ("KINGHAM DALTON WILSON", "General Contractor", "Kingham Dalton Wilson"),
                             ("Gordon Highlander|Pat Jones", "General Contractor", None),   # holdout D: two plain words starting with a first name
                             ("FLYNN CONSTRUCTION ***Main", "General Contractor", "Flynn Construction"), ("*MAIN", "General Contractor", None),
                             ("AUSTIN BRIDGE", "General Contractor", "Austin Bridge"), ("Jordan Foster", "General Contractor", "Jordan Foster"),   # names that are businesses here
                             ("Gordon Highlander|Gordon Highlander", "General Contractor", None),   # the contractor's own name: a person
                             ("SMITH JOHN|JOHN SMITH", "General Contractor", None),
                             ("XBIOTECH", "General Contractor", "Xbiotech"), ("Speed Fab-Crete", "General Contractor", "Speed Fab-Crete"),
                             ("HCI Commercial", "General Contractor", "HCI Commercial"), ("Joseph Companies", "General Contractor", "Joseph Companies"),
                             ("ZAPALAC/REED (MAIN) CONSTRUCTION COMPANY", "General Contractor", "Zapalac/Reed Construction Company")]:
        raw, full = (raw.split("|") + [""])[:2]
        got = builder_name({"contractor_company_name": raw, "contractor_trade": trade, "contractor_full_name": full})
        if got != want:
            bad.append(("builder", raw, got, want))
    assert P.entity_key("Bailey Elliott Construction, Inc.") == P.entity_key("BAILEY ELLIOTT CONSTRUCTION INC")
    assert P.entity_key("The NRP Contractors, LLC") != P.entity_key("NRP Contractors II, LLC")
    # the description: prefixes and tags off, phone numbers and emails never printed, no person's name after a tag
    for raw, want in [("ePlan: Commercial Expedited Review - [SMART HOUSING] [APPROVED] New Construction of New Apartments with Private Garages (38520 SF).",
                       "New Construction of New Apartments"),
                      ("*FKA 92 RED RIVER ST* ePlan: Expedited Review - First Time Finish Out for Hotel", "First Time Finish Out for Hotel"),
                      ("ePlan-Expedited Review: [APPROVED] New Dumpster Enclosure", "New Dumpster Enclosure"),
                      ("ePlan: Commerical Expedited Review- New Construction 4 story Multi Family Building. .", "New Construction 4 story"),
                      ("ePlan: Commercial Expedited Review -*SMART HOUSING* New Construction of Pool Amenity", "New Construction of Pool Amenity"),
                      ("QT - Retaining Wall New Construction", "Retaining Wall"),
                      ("[APPROVED New Construction of Behavior Health Hospital", "New Construction of Behavior"),
                      ("ePlan: BAUS Review - Interior Remodel on Apron Level for Southwest Airlines .", "Interior Remodel on Apron")]:
        got = austin_scope(raw)
        if not got.startswith(want):
            bad.append(("scope", raw[:60], got))
    for raw, want in [("ePlan: Commercial Expedited Review - [APPROVED] First Time Finish Out- 5 PHASE 1 MULTIFAMILY FLOORS 1-5 CLUB AMENTITY TO INCLUDE LEASING OFFICE",
                       "First time finish out- 5 phase 1 multifamily floors 1-5 club amentity to include leasing office"),
                      ("NEW CONSTRUCTION OF AISD MIDDLE SCHOOL. MEP WORK INCLUDED", "New construction of AISD middle school. MEP work included"),
                      ("Interior Remodel to Existing Office (13000 SF)", "Interior Remodel to Existing Office (13000 SF)")]:
        if austin_scope(raw, limit=300) != want:
            bad.append(("sentence case", austin_scope(raw, limit=300), want))
    for raw, want in [("9711 LBJ FWY", "9711 LBJ Fwy"), ("4501 W SH 71", "4501 W SH 71"), ("8801 MC CANN DR", "8801 McCann Dr"),
                      ("11400 N IH 35 SVRD", "11400 N IH 35 Svrd"), ("3001 RR 620 S", "3001 RR 620 S"), ("1110 W 6TH ST UNIT FLR1", "1110 W 6th St"), ("610 DAVIS ST BLDG 1FLR UNIT 55", "610 Davis St Unit 55"),
                      ("62 EAST AVE UNIT FLR15", "62 East Ave"), ("2631 KRAMER LN UNIT FW3", "2631 Kramer Ln"),
                      ("2201 E MLK JR BLVD", "2201 E MLK Jr Blvd"), ("100 MCCALL LN", "100 McCall Ln")]:
        if street_title(raw) != want:
            bad.append(("address", raw, street_title(raw), want))
    for raw in ("Construction of a new 51250 sq. ft single story middle school.                   210-850-8661",
                "New office. Call (512) 974-2000 or plans@example.com", "New school. Owner John Smith"):
        s = austin_scope(raw, limit=1200, whole=True)
        if re.search(r"\d{3}\D{0,2}\d{4}|@|John|Smith", s):
            bad.append(("private detail in scope", s))
    # projects: grouped by master permit, valued once (the largest), stages from the City's own fields
    def row(n, **kw):
        r = dict(base, **PERMIT_CASES[0][0], permit_number=f"2026-{n:06d} BP", masterpermitnum="M1", contractor_trade="General Contractor",
                 contractor_company_name="EXAMPLE BUILDERS LLC", original_address1=f"{n} MAIN ST", original_zip="78701", council_district="9",
                 total_job_valuation="1", issue_date="2026-03-01T00:00:00.000", expiresdate="2026-08-29T00:00:00.000")
        r.update(kw)
        return r
    week = (today - dt.timedelta(days=7)).isoformat()
    rows = [row(1, total_job_valuation="245000000", expiresdate="2026-11-30T00:00:00.000"), row(2, expiresdate="2026-11-30T00:00:00.000"),
            row(3, status_current="Final"),
            row(4, permit_class="C- 329 Com Structures Other Than Bldg", total_job_valuation="830000000", description="New Construction of Pergola"),
            row(5, masterpermitnum="M2", total_job_valuation="499999", contractor_company_name="BETA CONSTRUCTION INC", expiresdate="2026-11-30T00:00:00.000"),
            row(6, masterpermitnum="M3", total_valuation_remodel="600000", work_class="Remodel", permit_class="C-1001 Commercial Finish Out",
                description="First Time Finish Out for Units", housing_units="7", issue_date="2026-10-13T00:00:00.000",
                expiresdate="2027-04-11T00:00:00.000", contractor_company_name="JOHN SMITH"),
            row(7, masterpermitnum="M4", total_valuation_remodel="600000", work_class="Remodel", permit_class="C-1001 Commercial Finish Out",
                description="First Time Finish Out for Units", housing_units="7", issue_date="2026-10-13T00:00:00.000", expiresdate="2027-04-12T00:00:00.000",
                contractor_company_name="Acme Builders, L.L.C."),
            row(8, masterpermitnum="M4", total_valuation_remodel="1", work_class="Remodel", permit_class="C-1001 Commercial Finish Out",
                description="First Time Finish Out for Units", housing_units="5", issue_date="2026-02-01T00:00:00.000", expiresdate="2027-01-15T00:00:00.000",
                contractor_company_name="ACME BUILDERS LLC"),
            row(9, masterpermitnum="M5", status_current="Final", issue_date="2022-01-05T00:00:00.000"),
            row(10, masterpermitnum="M5", total_job_valuation="900000", issue_date="2026-09-01T00:00:00.000", expiresdate="2027-03-01T00:00:00.000")]
    rows += [  # holdout, Oct 18: valued only from kept permits; repeated home counts once; a fourplex at exactly $500,000 on the window's edge
        row(11, masterpermitnum="M6", total_valuation_remodel="60000", work_class="Remodel", permit_class="C-1000 Commercial Remodel",
            description="Remodel for Common Spaces - Lobby Entrances Utilites and Restrooms", housing_units="3", expiresdate="2026-12-01T00:00:00.000"),
        row(12, masterpermitnum="M6", status_current="Final", total_valuation_remodel="1000000", work_class="Remodel", permit_class="C-1000 Commercial Remodel"),
        row(13, masterpermitnum="M7", total_valuation_remodel="5", work_class="Remodel", permit_class="C-1001 Commercial Finish Out",
            description="First Time Finish Out for Units", housing_units="7", expiresdate="2026-12-01T00:00:00.000"),
        row(14, masterpermitnum="M7", work_class="Shell", total_job_valuation="154000000", description="New Shell Building of a 57-Story Tower"),
        row(15, masterpermitnum="M8", total_job_valuation="20000000", housing_units="70", expiresdate="2026-12-01T00:00:00.000"),
        row(16, masterpermitnum="M8", total_job_valuation="20000000", housing_units="70", expiresdate="2026-12-01T00:00:00.000"),
        row(17, masterpermitnum="M8", total_job_valuation="20000000", housing_units="70", expiresdate="2026-12-01T00:00:00.000"),
        row(18, masterpermitnum="M9", permit_class="C- 104 Three & Four Family Bldgs", housing_units="4", total_job_valuation="500000",
            issue_date="2024-10-19T00:00:00.000", expiresdate="2026-11-30T00:00:00.000", contractor_company_name="Joseph Companies",
            description="New construction of a multi-family fourplex"),
        row(20, masterpermitnum="M9", permit_class="C- 104 Three & Four Family Bldgs", housing_units="4", total_job_valuation="500000",
            issue_date="2024-10-19T00:00:00.000", expiresdate="2026-11-30T00:00:00.000", contractor_company_name="Joseph Companies",
            description="New construction of a multi-family fourplex"),
        row(19, masterpermitnum="M10", permit_class="C-1000 Commercial Remodel", work_class="Remodel", housing_units="3", total_valuation_remodel="900000",
            description="Interior Remodel to Existing Office/Warehouse. Work to include subdividing Existing Interior into Multiple Suites",
            expiresdate="2026-12-01T00:00:00.000")]
    ps, why, _ = group_projects(rows, since, today, week)
    byp = {p["permit"]: p for p in ps}
    if set(byp) != {"M1", "M4", "M5", "M8", "M9", "M10"}:
        bad.append(("projects kept", sorted(byp), dict(why)))
    else:
        if byp["M1"]["cost"] != 245000000 or byp["M1"]["milestone"] != "Near finish" or byp["M1"]["buildings"] != 2 or byp["M1"]["units"] != 30:
            bad.append(("M1", byp["M1"]))   # valued from its kept permits only (the pergola's $830M does not count); 30 homes repeated on 2 permits count once
        if byp["M4"]["gc"] != ["Acme Builders LLC"] or byp["M4"]["milestone"] != "Work under way" or byp["M4"]["issued"] != "2026-02-01" or byp["M4"]["newThisWeek"]:
            bad.append(("M4", byp["M4"]))   # one legal entity, expiry pushed past 180 days, new only when its first permit is new
        if byp["M8"]["units"] != 70 or byp["M8"]["newUnits"] != 70 or byp["M9"]["units"] != 8 or byp["M9"]["cost"] != 500000 \
                or byp["M10"]["units"] is not None:
            bad.append(("homes", byp["M8"]["units"], byp["M9"]["units"], byp["M10"]["units"]))
        if byp["M5"]["milestone"] != "Permit issued":
            bad.append(("M5", byp["M5"]))   # a permit finaled before the window is an old phase, not a sign of this one finishing
    if why.get("project valuation under $500,000") != 3 or why.get("no business listed as general contractor") != 1:
        bad.append(("reasons", dict(why)))
    # one development under two master permits (6801 River Place Blvd, Oct 18: $1,525,000,000 on both): one project, valued once
    twins = [dict(byp["M1"], permit="T1", address="6801 River Place Blvd", cost=1525000000, gc=["Turner Construction"], milestone="Work under way"),
             dict(byp["M1"], permit="T2", address="6801 River Place Blvd (+1 more)", cost=1525000000, gc=["TURNER CONSTRUCTION"], milestone="Near finish"),
             dict(byp["M1"], permit="T3", address="6801 River Place Blvd", cost=9000000, gc=["Turner Construction"])] if "M1" in byp else []
    ub = [{"gc": ["Rogers Obrien Construction"]}, {"gc": ["Rogers-O'Brien Construction Co. Ltd"]}, {"gc": ["ROGERS-O'BRIEN CONSTRUCTION CO., LTD."]},
          {"gc": ["Panoptic Group"]}, {"gc": ["Panoptic Group LLC"]}, {"gc": ["Panoptic Group Inc"]}, {"gc": ["Acme Builders"]}, {"gc": ["Zeta Builders"]}]
    ub += [{"gc": ["Zapalac/Reed Construction Co., LP"]}, {"gc": ["Zapalac/Reed Construction Company"]},
           {"gc": ["The Struthoff Company, Inc."]}, {"gc": ["The Struthoff Co. Inc."]}, {"gc": ["The Struthoff Co. Inc."]}]
    unify_builders(ub)
    if [x["gc"][0] for x in ub] != ["Rogers-O'Brien Construction Co. Ltd"] * 3 + \
            ["Panoptic Group", "Panoptic Group LLC", "Panoptic Group Inc", "Acme Builders", "Zeta Builders"] + \
            ["Zapalac/Reed Construction Co., LP"] * 2 + ["The Struthoff Co. Inc."] * 3:
        bad.append(("one builder per legal entity", [x["gc"] for x in ub]))
    mt, gone = merge_twins(twins)
    if len(mt) != 2 or gone != ["T2"] or mt[0]["buildings"] != 4 or mt[0]["milestone"] != "Near finish" or mt[0]["address"] != "6801 River Place Blvd (+1 more)" \
            or total_cost(mt) != 1534000000 or mt[0]["masters"] != ["T1", "T2"]:
        bad.append(("merge twins", [(x["permit"], x["address"], x["buildings"], x["milestone"]) for x in mt], gone))
    if geo_street("507 E Howard Ln Bldg 3 Unit 10 (+2 more)") != "507 E Howard Ln" or geo_street("1110 W 6th St Unit Flr1") != "1110 W 6th St":
        bad.append(("geo street", geo_street("507 E Howard Ln Bldg 3 Unit 10 (+2 more)")))
    if coord({"latitude": "30.2672", "longitude": "-97.7431"}) != (30.2672, -97.7431) or coord({"latitude": "0", "longitude": "0"}) != (None, None) \
            or coord({"location": {"type": "Point", "coordinates": [-97.7, 30.3]}}) != (30.3, -97.7):
        bad.append(("coord",))
    if bad:
        raise SystemExit("austin selftest FAIL: " + json.dumps(bad, default=str)[:2500])
    print(f"austin selftest ok ({len(PERMIT_CASES)} planted permits, 11 window cases, 22 builder cases, 14 scope cases, 10 planted projects, 13 builder groupings, twin merge, 12 addresses)")


def audit(rows, since, today, path):
    """A de-identified audit of the real rows, for tuning the rules from the cloud (which cannot reach the portal): per
    building permit the City's class, work class, status, dates, valuations and tidied description, and the rule's decision.
    No address, ZIP, permit number, master number, coordinates or contractor name is written."""
    gid, out = {}, []
    for r in rows:
        g = r.get("masterpermitnum") or ("solo-" + str(r.get("permit_number")))
        gid.setdefault(g, len(gid))
        k, why = keep_permit(r, since, today)
        out.append({"g": gid[g], "cls": r.get("permit_class"), "work": r.get("work_class"), "status": r.get("status_current"),
                    "issued": day(r.get("issue_date")), "expires": day(r.get("expiresdate")), "units": r.get("housing_units"),
                    "tj": r.get("total_job_valuation"), "tr": r.get("total_valuation_remodel"), "trade": r.get("contractor_trade"),
                    "biz": bool(builder_name(r)), "geo": coord(r)[0] is not None, "zip": bool(r.get("original_zip")),
                    "desc": tidy(r.get("description")), "keep": k, "why": why})
    json.dump({"since": since, "rows": out}, open(path, "w"), indent=0)


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        main()
