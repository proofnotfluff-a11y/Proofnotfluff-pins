#!/usr/bin/env python3
"""Chicago Restaurant Inspection Leads: the list itself (ProofNotFluff product 3, Oct 2026).

Input: the raw Food Inspections pull the inspections workflow writes (tools/inspections_chicago.py --raw): the City's
own rows for the last 37 days, plus the 24-month inspection history of every license that failed, passed with
conditions or had a license inspection in that time. Output: one dataset the members' app (tools/rest_app.py), the
workbook (tools/rest_xlsx.py) and the free sample page (tools/rest_site.py) are all built from, so they cannot drift.

Who buys it: pest control companies, commercial kitchen hood and exhaust cleaners, grease trap and drain companies,
commercial kitchen cleaners, and (for openings) POS, linen and cleaning vendors.

The three lists (all from the City's own fields; the window is the 30 days up to the newest inspection the City has
published, so every weekly list has the same depth even though the City posts results a few days late):
  1 Failed or conditional: a routine, complaint or re-inspection (not a license inspection) in the window whose City
    result is "Fail" or "Pass w/ Conditions" and that cited at least one violation a buyer works on (CATEGORIES).
  2 Opening soon: a license inspection in the window. Chicago inspects a food business before its license is issued,
    so these places are weeks from opening, or just opened under a new license.
  3 Failed more than once: 2 or more "Fail" results on routine, complaint or re-inspections in the 90 days to the
    newest inspection, at least one of them in the window.

What is left out, and why (counted in counts.excluded): schools, day care and other children's facilities, hospitals,
nursing and senior sites, and mobile vendors (by the City's facility type and by name); any place whose business name
is a person's name (person_name); rows with no business name or no address; places the City last marked "Out of
Business" or "Business Not Located".

Wording rule (Todd, Oct 17): the list states the City's recorded result and the violation categories, dated, with
the City's disclaimer. It never says a business is dirty or unsafe, and it never republishes the inspector's notes:
the notes are read here only to place a violation in a category, and the dataset carries only the City's violation
code numbers and titles.

Usage: python3 tools/rest_leads.py RAW.json OUT.json      the dataset (members' data: keep it out of the repo)
       python3 tools/rest_leads.py --sample RAW.json      writes permits/inspections-chicago/rest-sample.json (public)
       python3 tools/rest_leads.py --selftest
"""
import collections, datetime as dt, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from inspections_chicago import dba_case, split_violations, street  # noqa: E402

PRODUCT = "Chicago Restaurant Inspection Leads"
WINDOW_DAYS, NEW_DAYS, REPEAT_DAYS = 30, 7, 90
SAMPLE = os.path.join(ROOT, "permits", "inspections-chicago", "rest-sample.json")
CITY_TERMS = "https://www.chicago.gov/city/en/narr/foia/data_disclaimer.html"
DATASET_PAGE = "https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5"
RECORD = "https://data.cityofchicago.org/resource/4ijn-s7e5.json?inspection_id="

# ---------------------------------------------------------------- what each buyer works on
CATEGORIES = [  # key, label, short label, who buys
    ("pests", "Pests and rodents", "Pests", "Pest control"),
    ("hood", "Hood and exhaust", "Hood", "Hood and exhaust cleaning"),
    ("drain", "Grease trap and drains", "Grease trap", "Grease trap and drain service"),
    ("clean", "Cleaning", "Cleaning", "Commercial kitchen cleaning"),
]
CAT_LABEL = {k: l for k, l, _, _ in CATEGORIES}
CAT_ORDER = [k for k, _, _, _ in CATEGORIES]

# The rules, written against the City's own violation titles (permits/inspections-chicago/violation-codes.json) and a
# read of 2,200 inspector notes from Sep and Oct 2026:
#   Pests:  38 "INSECTS, RODENTS, & ANIMALS NOT PRESENT" always (it also covers pest proofing, such as a gap under a door,
#           and a missing pest control log, which are pest control work too); 59 or 60 (a previous violation not
#           corrected) when the note names violation 38; any other violation whose note names droppings, live or dead
#           roaches, mice, rats, flies, gnats or pest activity. A note that only says "to prevent pests" does not count.
#   Hood:   56 "ADEQUATE VENTILATION & LIGHTING" when the note names a hood, a filter, an exhaust, a duct or grease (56
#           also covers lighting and toilet-room fans, which do not count); any violation whose note names a hood or an
#           exhaust fan.
#   Drains: 52 "SEWAGE & WASTE WATER PROPERLY DISPOSED" always; any note naming a grease trap or interceptor; 51
#           "PLUMBING INSTALLED" or 55 "PHYSICAL FACILITIES" when the note names a clogged, backed-up or slow drain,
#           standing water, sewage or a sewer line (a leaking faucet or a missing backflow device does not count).
#   Clean:  49 "NON-FOOD/FOOD CONTACT SURFACES CLEAN" always; 53 toilet facilities, 54 garbage and refuse, 55 physical
#           facilities and 60 previous core violation when the note asks for cleaning or names dirt, debris, grease,
#           grime, dust, mold, residue or a buildup ("easily cleanable" surfaces and ice buildup do not count).
PEST_EVIDENCE = re.compile(r"DROPPING|\bROACH|COCKROACH|\bMICE\b|\bMOUSE\b|\bRATS?\b|\bRODENT ACTIVITY|\bFLIES\b|FRUIT FL(?:Y|IES)|"
                           r"\bGNATS?\b|\bPEST ACTIVITY|\bINSECT ACTIVITY|\bGNAW|\bLIVE (?:INSECT|BUG)|\bBED ?BUGS?\b|\bRODENTS?\b")
PREVENT = re.compile(r"\b(?:TO\s+)?PREVENT(?:ING)?\b[^.;]*|\b(?:RODENT|INSECT|PEST)[\s/-]*(?:AND\s+|/)?(?:INSECT|RODENT|PEST)?[\s/-]*PROOF\w*|"
                     r"\bFREE (?:OF|FROM) [^.;]*|\bNO (?:EVIDENCE|SIGNS?) OF [^.;]*")
REF_38 = re.compile(r"#\s*38\b|\b38\s*[-:)]|\(\s*#?\s*38\s*\)|\bVIOLATION\s*(?:#|NO\.?|NUMBER)?\s*38\b")
HOOD_56 = re.compile(r"\bHOODS?\b|\bFILTERS?\b|\bEXHAUST|\bDUCT|\bGREASE")
HOOD_ANY = re.compile(r"\bHOODS?\b|\bEXHAUST (?:FAN|HOOD|SYSTEM)")
TRAP = re.compile(r"GREASE\s+TRAP|GREASE\s+INTERCEPTOR|\bINTERCEPTOR")
DRAIN = re.compile(r"\bCLOG|\bBACK(?:ING|ED|S)?[\s-]+UP\b|\bSLOW(?:LY)?[\s-]+DRAIN|\bNOT\s+DRAINING|\bSTANDING\s+WATER|\bSEWAGE|\bSEWER")
CLEAN_WORDS = re.compile(r"\bCLEAN(?:ED|ING)?\b|\bDIRT|\bDEBRIS|\bGREASE|\bGREASY|\bGRIME|\bDUST|\bMOLD|\bMILDEW|\bRESIDUE|"
                         r"\bBUILD[\s-]?UP|\bBUILT[\s-]?UP|\bACCUMULAT|\bSOIL(?:ED)?\b|\bSLIME")
NOT_CLEAN = re.compile(r"\bEASILY\s+CLEANABLE|\bCLEANABLE|\bICE\s+BUILD[\s-]?UP|\bFROST\s+BUILD[\s-]?UP")


def categorize(violations):
    """{category: sorted City violation codes that put this inspection in it} from the City's violations text."""
    out = collections.defaultdict(set)
    for code, title, note in split_violations(violations):
        n = note.upper()
        evidence = PREVENT.sub(" ", n)
        if code == 38 or (code in (59, 60) and REF_38.search(n)) or PEST_EVIDENCE.search(evidence):
            out["pests"].add(code)
        if (code == 56 and HOOD_56.search(n)) or HOOD_ANY.search(n):
            out["hood"].add(code)
        if code == 52 or TRAP.search(n) or (code in (51, 55) and DRAIN.search(n)):
            out["drain"].add(code)
        if code == 49 or (code in (53, 54, 55, 60) and CLEAN_WORDS.search(NOT_CLEAN.sub(" ", n))):
            out["clean"].add(code)
    return {k: sorted(out[k]) for k in CAT_ORDER if out.get(k)}


def violation_list(violations):
    """[(code, City title)] in the City's order, titles only (inspector notes are never kept)."""
    seen, out = set(), []
    for code, title, _ in split_violations(violations):
        if code not in seen:
            seen.add(code)
            out.append((code, title))
    return out


# ---------------------------------------------------------------- who is left out
INSTITUTION_TYPE = re.compile(r"(?<!COOKING )\bSCHOOL|CHILDREN|CHILD\b|DAY ?CARE|HEAD START|PRE-?K\b|PRESCHOOL|HOSPITAL|LONG[- ]TERM CARE|"
                              r"NURSING|ASSISTED|REHAB|GOLDEN DINER|SENIOR|ADULT DAY|SHELTER|MOBILE FOOD|^MFP$|PEDDLER|"
                              r"UNIVERSITY|COLLEGE", re.I)
INSTITUTION_NAME = re.compile(r"(?<!COOKING )\bSCHOOL\b|\bACADEMY\b|\bELEMENTARY\b|\bELEM\b|\bMIDDLE SCHOOL|\bHIGH SCHOOL|\bH/?S\)|\bCOLLEGE PREP|"
                              r"\bCHARTER\b|\bCAMPUS\b|\bPRE-?K\b|\bPRESCHOOL|\bPRE-SCHOOL|\bMONTESSORI|\bDAY ?CARE|\bCHILD ?CARE|\bCHILDREN|"
                              r"\bKIDS?\b|\bKIDZ\b|\bKIDDIE|\bTOTS?\b|\bINFANT|\bTODDLER|\bHEAD START|\bLEARNING CENTER|\bEARLY LEARNING|"
                              r"\bCPS\b|\bCICS\b|\bKIPP\b|\bHOSPITAL|\bMEDICAL CENTER|\bNURSING|\bSENIORS?\b|\bASSISTED LIVING|\bUNIVERSITY\b|"
                              r"\bCLASSICAL\b|\bMAGNET\b|\bYCCS\b", re.I)
# Words that make a name a business, not a person ("Sofia Bakery", "Paul House", "George Street Pub").
BIZ = set("""RESTAURANT RESTAURANTE CAFE CAFFE COFFEE TEA BOBA KITCHEN GRILL GRILLE BAR PUB TAVERN LOUNGE CLUB BAKERY PANADERIA PASTRY
PIZZA PIZZERIA TACOS TACO TAQUERIA TAMALES BURRITO BURGER BURGERS DELI MARKET MART GROCERY FOOD FOODS FOODMART LIQUOR LIQUORS STORE
SHOP SHOPPE HOUSE PLACE STREET AVENUE CORNER CITY CHICAGO EXPRESS INN HOTEL CATERING CATERER BANQUET HALL BUFFET DINER DINING
CANTINA BISTRO BRASSERIE TRATTORIA OSTERIA EATERY EATS SWEETS SWEET CANDY ICE CREAM GELATO PALETERIA NEVERIA JUICE SMOOTHIE
SMOOTHIES BBQ BARBECUE WINGS WING CHICKEN FISH SEAFOOD MARISCOS STEAK STEAKHOUSE SUSHI RAMEN PHO NOODLE NOODLES WOK THAI CHINA
CHINESE MEXICAN ITALIAN INDIAN HALAL GYROS GYRO SHAWARMA FALAFEL KEBAB BAGEL BAGELS DONUT DONUTS BAKE BREAD BUTCHER CARNICERIA
MEAT MEATS PRODUCE FRESH FARM FARMS CO COMPANY INC LLC CORP CORPORATION LTD GROUP ENTERPRISES ENTERPRISE HOLDINGS SERVICES
STATION GAS MOBIL SHELL BP CIRCLE BREWING BREWERY BREWERS DISTILLERY WINE WINES SPIRITS CELLAR ROOM TABLE STUDIO GARDEN GARDENS
SOCIAL CENTER CENTRE THEATER THEATRE STADIUM ARENA PARK FIELD HUB SPOT STOP SNACK SNACKS TREATS DESSERT DESSERTS CUPCAKE CUPCAKES
COOKIE COOKIES CREPE CREPES WAFFLE WAFFLES BRUNCH BREAKFAST LUNCH DINNER CUISINE COCINA FONDA ANTOJITOS POLLO JUGOS MERCADO TIENDA
SUPERMERCADO MINI SUPER FOOD-MART DOLLAR WALGREENS CVS TARGET COSTCO JEWEL ALDI MARIANO MARIANOS PETE PETES MCDONALD MCDONALDS
SUBWAY WENDYS STARBUCKS DUNKIN POTBELLY CHIPOTLE PANERA POPEYES HAROLDS HAROLD'S ROTI SALAD BOWL BOWLS POKE BOX TRUCK
CARNITAS BIRRIA POZOLE POZOLERIA ELOTES TORTAS TORTILLERIA TAMALERIA MOLE MENUDO CEVICHE BIRRIERIA LONCHERIA BURRITOS QUESADILLAS
GYRO HOTDOG HOTDOGS DOGS BEEF PORK RIBS CHOPHOUSE TAPAS DUMPLING DUMPLINGS BAO CURRY BIRYANI KABOB KABOBS SAJ JERK PATTY""".split())
TITLES = {"CHEF", "MR", "MRS", "MS", "MISS", "DR", "DOCTOR", "SR", "JR", "II", "III", "IV", "SAINT", "ST"}
FIRST = set("""AARON ABDUL ABEL ABIGAIL ABRAHAM ADA ADAM ADRIAN ADRIANA AGNES AHMED AIDAN AISHA ALAN ALBERT ALBERTO ALEJANDRA ALEJANDRO ALEX
ALEXANDER ALEXANDRA ALEXIS ALFONSO ALFREDO ALI ALICE ALICIA ALINA ALISON ALLEN ALMA ALVARO ALVIN AMANDA AMBER AMELIA AMIR AMY ANA
ANDRE ANDREA ANDRES ANDREW ANDY ANGEL ANGELA ANGELICA ANGELINA ANITA ANN ANNA ANNE ANNIE ANTHONY ANTONIO APRIL ARMANDO ARNOLD ARTHUR
ARTURO ASHLEY AUDREY AURORA BARBARA BEATRIZ BEN BENJAMIN BERNARD BETH BETTY BEVERLY BILL BILLY BLANCA BOB BOBBY BONNIE BRAD BRANDON
BRENDA BRIAN BRITTANY BRUCE BRYAN CARL CARLA CARLOS CARMEN CAROL CAROLINA CAROLINE CAROLYN CATHERINE CECILIA CESAR CHAD CHARLES
CHARLIE CHARLOTTE CHERYL CHRIS CHRISTIAN CHRISTINA CHRISTINE CHRISTOPHER CINDY CLAIRE CLARA CLAUDIA CODY COLLEEN CONNIE CRAIG CRISTINA
CRYSTAL CYNTHIA DAISY DALE DAN DANA DANIEL DANIELA DANIELLE DANNY DARIUS DARLENE DARNELL DARRYL DAVE DAVID DAWN DEAN DEBBIE DEBORAH
DEBRA DENISE DENNIS DEREK DESTINY DIANA DIANE DIEGO DOLORES DOMINIC DON DONALD DONNA DORIS DOROTHY DOUG DOUGLAS DUSTIN DWAYNE DYLAN
EARL EDDIE EDGAR EDITH EDUARDO EDWARD EDWIN EILEEN ELAINE ELENA ELIAS ELIJAH ELIZABETH ELLA ELLEN EMILIO EMILY EMMA ENRIQUE ERIC ERICA
ERIK ERIKA ERIN ERNESTO ESPERANZA ESTHER ETHAN EUGENE EVA EVAN EVELYN FAITH FATIMA FELIPE FELIX FERNANDO FRANCES FRANCISCO FRANK
FRANKIE FRED FREDDIE FREDERICK GABRIEL GABRIELA GAIL GARY GENE GEORGE GERALD GERARDO GINA GLADYS GLENN GLORIA GRACE GREG GREGORY
GUADALUPE GUILLERMO GUSTAVO HAILEY HANNAH HAROLD HARRY HASSAN HEATHER HECTOR HELEN HENRY HERBERT HUGO HUNTER IAN IBRAHIM IGNACIO
IRENE IRMA ISAAC ISABEL ISABELLA ISAIAH IVAN JACK JACKIE JACKSON JACOB JACQUELINE JAIME JAMAL JAMES JAMIE JANE JANET JANICE JASMINE
JASON JAVIER JAY JEAN JEFF JEFFREY JENNIFER JENNY JEREMY JEROME JERRY JESSE JESSICA JESUS JILL JIM JIMMY JOAN JOANNA JOE JOEL JOHN
JOHNNY JON JONATHAN JORDAN JORGE JOSE JOSEFINA JOSEPH JOSH JOSHUA JOY JOYCE JUAN JUANA JUANITA JUDITH JUDY JULIA JULIAN JULIANA JULIE
JULIO JUSTIN KAREN KARINA KATHERINE KATHLEEN KATHRYN KATHY KATIE KAYLA KEITH KELLY KEN KENNETH KEVIN KIM KIMBERLY KRISTEN KYLE LANCE
LARRY LAURA LAUREN LAWRENCE LEAH LEE LEO LEON LEONARD LESLIE LETICIA LILIA LILIANA LILY LINDA LISA LIZ LOGAN LORENA LORENZO LORI
LOUIS LOUISE LUCAS LUCIA LUCY LUIS LUKE LUZ LYNN MADISON MANUEL MARCO MARCOS MARCUS MARGARET MARIA MARIAN MARIANA MARIE MARILYN MARIO
MARISOL MARK MARTHA MARTIN MARTINA MARY MATTHEW MAURICE MAX MAYA MEGAN MELISSA MELVIN MICHAEL MICHELLE MIGUEL MIKE MILDRED MIMI
MIRIAM MOHAMMED MOHAMMAD MOHAMED MONICA MORGAN MUHAMMAD NANCY NATALIE NATHAN NATHANIEL NELSON NICHOLAS NICK NICOLE NOAH NORA NORMA
OLGA OLIVER OLIVIA OMAR OSCAR PABLO PAMELA PATRICIA PATRICK PAUL PAULA PEARL PEDRO PEGGY PETER PHILIP PHILLIP PHYLLIS PRISCILLA
RACHEL RAFAEL RAMON RANDY RAQUEL RAUL RAY RAYMOND REBECCA REGINA REGINALD RENEE RICARDO RICHARD RICK RICKY RITA ROBERT ROBERTO ROBIN
RODNEY ROGELIO ROGER ROLANDO RON RONALD ROSA ROSE ROSEMARY ROSIE ROSS ROXANNE ROY RUBEN RUBY RUSSELL RUTH RYAN SABRINA SALVADOR
SAM SAMANTHA SAMUEL SANDRA SANDY SARA SARAH SAUL SCOTT SEAN SERGIO SHANNON SHARON SHAWN SHEILA SHIRLEY SILVIA SOFIA SONIA SOPHIA
STACY STANLEY STEPHANIE STEPHEN STEVE STEVEN SUE SUSAN SUZANNE SYLVIA TAMARA TAMMY TANYA TARYN TED TEDDY TERESA TERRENCE TERRY
THERESA THIAGO THOMAS TIFFANY TIM TIMOTHY TINA TODD TOM TOMMY TONY TONYA TRACY TRAVIS TROY TYLER VALERIE VANESSA VERONICA VICTOR
VICTORIA VINCENT VIRGINIA WALTER WANDA WAYNE WENDELL WENDY WESLEY WILLIAM WILLIE XAVIER YESENIA YOLANDA YVONNE ZACHARY
ADAMU AMINA ANIL ARJUN CHEN DEEPAK HUI JIN KENJI LI MEI MING PRIYA RAJ RAJESH RAVI SANJAY SUNIL WEI YAN YING YUKI
AGNIESZKA ANDRZEJ BOGDAN DARIUSZ JACEK JAN KRZYSZTOF MAREK PIOTR STANISLAW TADEUSZ TOMASZ WOJCIECH ZBIGNIEW""".split())


def person_name(name):
    """True when the business name reads as a person's name ("Maria Garcia", "Chef Taryn", "Smith, Wendell"): two or three
    words, the first a common first name (after a title such as "Chef"), no business or food word, no possessive, no
    number, no ampersand. It errs toward leaving a place out, because a person's name never goes on the list."""
    raw = (name or "").strip().upper()
    if not raw or re.search(r"\d|&|'S\b|’S\b|@|\+", raw):
        return False
    if re.fullmatch(r"[A-Z.\-]+\s*,\s*[A-Z.\-]+(?:\s+[A-Z]\.?)?", raw):        # "SMITH, WENDELL"
        last, first = [x.strip() for x in raw.split(",", 1)]
        return first.split()[0].strip(".") in FIRST and last not in BIZ
    words = [w.strip(".,-") for w in re.split(r"\s+", raw) if w.strip(".,-")]
    if any(w in BIZ for w in words) or not all(re.fullmatch(r"[A-Z\-]+", w) for w in words):
        return False
    core = [w for w in words if w not in TITLES and len(w) > 1]
    titled = len(core) < len([w for w in words if len(w) > 1])
    return (2 <= len(core) <= 3 or (titled and len(core) == 1)) and core[0] in FIRST


def institution(r):
    return bool(INSTITUTION_TYPE.search(r.get("facility_type") or "") or INSTITUTION_NAME.search(r.get("dba_name") or "")
                or INSTITUTION_NAME.search(r.get("aka_name") or ""))


# ---------------------------------------------------------------- building the list
def chicago_day(iso):
    from zoneinfo import ZoneInfo
    t = dt.datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return t.astimezone(ZoneInfo("America/Chicago")).date()


def pretty(d):
    if isinstance(d, str):
        d = dt.date.fromisoformat(d[:10])
    return f"{d.strftime('%b')} {d.day}, {d.year}"


def lic_of(r):
    l = str(r.get("license_") or "").split(".")[0].strip()
    return l if l and l != "0" else ""


def place_key(r):
    l = lic_of(r)
    if l:
        return "L" + l
    return "N" + re.sub(r"[^A-Z0-9]", "", ((r.get("dba_name") or "") + "|" + (r.get("address") or "")).upper())[:60]


def _f(v):
    try:
        return round(float(v), 6)
    except (TypeError, ValueError):
        return None


def type_title(t):
    """The City's inspection type, in its own words, with consistent capitals ("Canvass Re-Inspection")."""
    t = re.sub(r"\s+", " ", (t or "").strip())
    return re.sub(r"(?<=-)([a-z])", lambda m: m.group(1).upper(), t.title()).replace("W/", "w/")


def is_license(t):
    return (t or "").strip().upper().startswith("LICENSE")


def result_word(r):
    return re.sub(r"\s+", " ", (r or "").strip())


def build(raw):
    """The dataset for this week's list (see the module docstring)."""
    src = raw["source"]
    as_of = chicago_day(src["fetchedAt"])
    rows = list(raw.get("rows", [])) + list(raw.get("history", []))
    dates = [(r.get("inspection_date") or "")[:10] for r in raw.get("rows", []) if r.get("inspection_date")]
    through = dt.date.fromisoformat(max(dates)) if dates else as_of
    w_from = (through - dt.timedelta(days=WINDOW_DAYS - 1)).isoformat()
    n_from = (through - dt.timedelta(days=NEW_DAYS - 1)).isoformat()
    r_from = (through - dt.timedelta(days=REPEAT_DAYS - 1)).isoformat()
    through_s = through.isoformat()

    # one record per inspection visit: the City's dataset "may contain some duplicate reports" (same place, day, type
    # and result under two ids), so those collapse into one, keeping the fuller violations text
    by_visit = {}
    for r in rows:
        d = (r.get("inspection_date") or "")[:10]
        if not d or d > through_s:
            continue
        k = (place_key(r), d, (r.get("inspection_type") or "").strip().upper(), (r.get("results") or "").strip().upper())
        old = by_visit.get(k)
        if old is None or len(r.get("violations") or "") > len(old.get("violations") or "") or \
                (len(r.get("violations") or "") == len(old.get("violations") or "") and str(r.get("inspection_id")) < str(old.get("inspection_id"))):
            by_visit[k] = r
    # one place per business at one address: rows join when they share a license number, or the same business name at
    # the same address (one bar can hold several licenses, and a license can be re-issued under the same name)
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    norm = lambda s: re.sub(r"[^A-Z0-9]", "", (s or "").upper())
    for r in by_visit.values():
        a, b = place_key(r), "A" + norm(r.get("dba_name")) + "|" + norm(r.get("address"))
        parent[find(a)] = find(b)
    per_place = collections.defaultdict(list)
    for r in by_visit.values():
        per_place[find(place_key(r))].append(r)

    excluded = collections.Counter()
    places, insp = {}, {}
    lists = {"flagged": [], "opening": [], "repeat": []}
    for pk, rs in per_place.items():
        rs.sort(key=lambda r: ((r.get("inspection_date") or "")[:10], str(r.get("inspection_id"))), reverse=True)
        latest = rs[0]
        in_win = [r for r in rs if (r.get("inspection_date") or "")[:10] >= w_from]
        if not in_win:
            continue
        # every exclusion is decided on the place, from any of its rows, so a place never slips in under another spelling
        reason = ""
        if any(institution(r) for r in rs):
            reason = "school, day care, hospital, senior or mobile vendor"
        elif any(person_name(r.get("dba_name")) or person_name(r.get("aka_name")) for r in rs):
            reason = "business name is a person's name"
        elif not (latest.get("dba_name") or "").strip() or not (latest.get("address") or "").strip():
            reason = "no business name or address"
        elif result_word(latest.get("results")).upper() in ("OUT OF BUSINESS", "BUSINESS NOT LOCATED"):
            reason = "the City's latest result is out of business or not located"
        recs = []
        for r in rs:
            cats = categorize(r.get("violations"))
            recs.append({"id": str(r.get("inspection_id")), "d": (r.get("inspection_date") or "")[:10],
                         "t": type_title(r.get("inspection_type")), "r": result_word(r.get("results")),
                         "v": violation_list(r.get("violations")), "c": cats, "lic": is_license(r.get("inspection_type"))})
        win = [x for x in recs if x["d"] >= w_from]
        flagged = [x for x in win if not x["lic"] and x["r"].upper() in ("FAIL", "PASS W/ CONDITIONS") and x["c"]]
        opening = [x for x in win if x["lic"]]
        fails90 = [x for x in recs if not x["lic"] and x["r"].upper() == "FAIL" and x["d"] >= r_from]
        repeat = len(fails90) >= 2 and any(x["d"] >= w_from for x in fails90) and any(x["c"] for x in fails90)
        on = [k for k, ok in (("flagged", flagged), ("opening", opening), ("repeat", repeat)) if ok]
        if not on:
            continue
        if reason:
            excluded[reason] += 1
            continue
        name = dba_case(latest.get("dba_name"))
        aka = dba_case(latest.get("aka_name") or "")
        union = lambda xs: sorted({c for x in xs for c in x["c"]}, key=CAT_ORDER.index)
        cats_by = {"flagged": union(flagged), "opening": union(opening), "repeat": union(fails90) if repeat else []}
        cats = union(flagged + opening + (fails90 if repeat else []))
        pk = "L" + lic_of(latest) if lic_of(latest) else place_key(latest)
        lics = sorted({lic_of(r) for r in rs if lic_of(r)}, key=lambda l: (len(l), l))
        p = {"id": pk, "name": name, "aka": aka if aka and re.sub(r"[^A-Z0-9]", "", aka.upper()) != re.sub(r"[^A-Z0-9]", "", name.upper()) else "",
             "license": lic_of(latest), "licenses": lics, "address": street(latest.get("address")), "zip": (latest.get("zip") or "").split(".")[0],
             "area": latest.get("_area") or "", "type": (latest.get("facility_type") or "").strip().title() or "Not given",
             "risk": (latest.get("risk") or "").strip(), "lat": _f(latest.get("latitude")), "lon": _f(latest.get("longitude")),
             "lists": on, "cats": cats, "catsBy": cats_by,
             "lead": (flagged or opening or fails90)[0]["id"],
             "flaggedIds": [x["id"] for x in flagged], "openingIds": [x["id"] for x in opening], "failIds": [x["id"] for x in fails90],
             "fails90": len(fails90), "new": any(x["d"] >= n_from for x in (flagged + opening + (fails90 if repeat else []))),
             "latestId": recs[0]["id"],
             "history": [x["id"] for x in recs]}
        for x in recs:
            insp[x["id"]] = x
        places[pk] = p
        for k in on:
            lists[k].append(pk)
    lead_day = lambda pk: insp[places[pk]["lead"]]["d"]
    for k in lists:
        lists[k].sort(key=lambda pk: places[pk]["name"])
        lists[k].sort(key=lambda pk: lead_day(pk), reverse=True)      # newest first, then A to Z
    counts = {
        "places": len(places), "flagged": len(lists["flagged"]), "opening": len(lists["opening"]), "repeat": len(lists["repeat"]),
        "new": sum(p["new"] for p in places.values()),
        "byCat": {k: sum(1 for pk in lists["flagged"] if k in places[pk]["catsBy"]["flagged"]) for k in CAT_ORDER},
        "flaggedFail": sum(1 for pk in lists["flagged"] if insp[places[pk]["flaggedIds"][0]]["r"].upper() == "FAIL"),
        "openingPassed": sum(1 for pk in lists["opening"] if insp[places[pk]["openingIds"][0]]["r"].upper().startswith("PASS")),
        "excluded": dict(sorted(excluded.items())),
        "rowsRead": len(raw.get("rows", [])), "historyRead": len(raw.get("history", [])),
        "areas": collections.Counter(p["area"] for p in places.values() if p["area"]).most_common(),
    }
    return {"product": PRODUCT, "asOf": as_of.isoformat(), "asOfText": pretty(as_of), "through": through_s, "throughText": pretty(through),
            "window": {"from": w_from, "to": through_s, "newFrom": n_from, "repeatFrom": r_from},
            "source": {"name": src.get("name"), "url": src.get("url") or DATASET_PAGE, "fetchedAt": src.get("fetchedAt"),
                       "rowsUpdatedAt": src.get("rowsUpdatedAt"), "terms": src.get("terms") or CITY_TERMS, "record": RECORD},
            "categories": [{"key": k, "label": l, "short": s, "buyer": b} for k, l, s, b in CATEGORIES],
            "places": places, "inspections": insp, "lists": lists, "counts": counts}


def sample(data, n=3):
    """The free page's public file: counts, and a few examples. Places on the failed lists are shown without their name or
    street address (the free page never names a business with a failed result); openings are shown in full."""
    P, I = data["places"], data["inspections"]

    def anon(pk):
        p = P[pk]
        x = I[p["lead"]]
        return {"type": p["type"], "area": p["area"] or "Chicago", "date": x["d"], "result": x["r"], "inspectionType": x["t"],
                "categories": [CAT_LABEL[c] for c in p["cats"]]}

    def full(pk):
        p = P[pk]
        x = I[p["openingIds"][0]]
        return {"name": p["name"], "address": p["address"], "area": p["area"] or "Chicago", "type": p["type"], "date": x["d"],
                "result": x["r"], "inspectionType": x["t"]}
    pick = lambda pks: [pk for pk in pks if P[pk]["area"]][:n]
    return {"product": PRODUCT, "asOf": data["asOf"], "asOfText": data["asOfText"], "through": data["through"],
            "throughText": data["throughText"], "window": data["window"], "source": data["source"], "counts": data["counts"],
            "categories": data["categories"],
            "examples": {"flagged": [anon(pk) for pk in pick(data["lists"]["flagged"])],
                         "repeat": [anon(pk) for pk in pick(data["lists"]["repeat"])],
                         "opening": [full(pk) for pk in pick(data["lists"]["opening"])]}}


# ---------------------------------------------------------------- planted cases
T = {38: "38. INSECTS, RODENTS, & ANIMALS NOT PRESENT", 56: "56. ADEQUATE VENTILATION & LIGHTING; DESIGNATED AREAS USED",
     52: "52. SEWAGE & WASTE WATER PROPERLY DISPOSED", 51: "51. PLUMBING INSTALLED; PROPER BACKFLOW DEVICES",
     49: "49. NON-FOOD/FOOD CONTACT SURFACES CLEAN", 55: "55. PHYSICAL FACILITIES INSTALLED, MAINTAINED & CLEAN",
     54: "54. GARBAGE & REFUSE PROPERLY DISPOSED; FACILITIES MAINTAINED", 2: "2. CITY OF CHICAGO FOOD SERVICE SANITATION CERTIFICATE",
     59: "59. PREVIOUS PRIORITY FOUNDATION VIOLATION CORRECTED", 60: "60. PREVIOUS CORE VIOLATION CORRECTED",
     53: "53. TOILET FACILITIES: PROPERLY CONSTRUCTED, SUPPLIED, & CLEANED", 47: "47. FOOD & NON-FOOD CONTACT SURFACES CLEANABLE, PROPERLY DESIGNED, CONSTRUCTED & USED"}
V = lambda code, note: f"{T[code]} - Comments: {note}"
CAT_CASES = [  # (violations text, expected categories) with invented notes on the City's real titles
    (V(38, "OBSERVED APPROX 25 MICE DROPPINGS ALONG WALL BASE IN DRY STORAGE."), {"pests": [38]}),
    (V(38, "OBSERVED 1/4 INCH GAP AT BOTTOM OF REAR DOOR. INSTRUCTED TO MAKE TIGHT FITTING."), {"pests": [38]}),
    (V(38, "NO PEST CONTROL LOGBOOK ON SITE."), {"pests": [38]}),
    (V(56, "HEAVY GREASE BUILD UP ON HOOD FILTERS ABOVE COOKING LINE. CLEAN AND MAINTAIN."), {"hood": [56]}),
    (V(56, "OBSERVED BURNED OUT BULBS IN REAR PREP AREA. INSTRUCTED TO REPLACE."), {}),
    (V(56, "NO VENTILATION IN TOILET ROOM. INSTD TO PROVIDE MECHANICAL VENTILATION AND MAINTAIN"), {}),
    (V(52, "GREASE TRAP OVERFLOWING IN BASEMENT. MUST SERVICE."), {"drain": [52]}),
    (V(52, "WASTE LINE NOT PROPERLY FUNCTIONING."), {"drain": [52]}),
    (V(51, "LEAKING FAUCET AT 3 COMPARTMENT SINK."), {}),
    (V(51, "OBSERVED FRONT PREP HANDSINK SLOW DRAINING. INSTRUCTED TO REPAIR."), {"drain": [51]}),
    (V(55, "FLOOR DRAIN CLOGGED IN DISH ROOM WITH STANDING WATER."), {"clean": [], "drain": [55]}),
    (V(49, "GREASE BUILD UP ON FRYERS AND SHELVING."), {"clean": [49]}),
    (V(55, "DEAD ROACHES ON FLOOR UNDER DISH MACHINE. MUST CLEAN."), {"pests": [55], "clean": [55]}),
    (V(55, "MUST REPAINT CEILING TO BE SMOOTH AND EASILY CLEANABLE."), {}),
    (V(55, "OBSERVED ICE BUILDUP ON CONDENSER IN WALK IN FREEZER."), {}),
    (V(54, "GARBAGE AREA NOT MAINTAINED. INSTRUCTED TO CLEAN TO PREVENT A POSSIBLE FOOD SOURCE FOR PESTS."), {"clean": [54]}),
    (V(54, "OVERFLOWING DUMPSTER, LID OPEN."), {}),
    (V(49, "MUST CLEAN HOOD AND EXHAUST FAN ABOVE GRILL."), {"clean": [49], "hood": [49]}),
    (V(2, "NO CERTIFIED FOOD MANAGER ON DUTY."), {}),
    (V(59, "PREVIOUS PRIORITY FOUNDATION VIOLATION #38 FROM REPORT #2633345 NOT CORRECTED."), {"pests": [59]}),
    (V(60, "PREVIOUS CORE VIOLATIONS #37 AND #45 NOT CORRECTED. LABEL SPICES."), {}),
    (V(55, "DOORS NOT RODENT/INSECT PROOFED. INSTRUCTED TO RODENT PROOF AND MAINTAIN."), {}),
    (V(53, "TOILET ROOM DOOR NOT SELF CLOSING."), {}),
    (V(53, "TOILET ROOM FLOOR AND WALLS SOILED. MUST CLEAN."), {"clean": [53]}),
    (V(47, "STAINED CUTTING BOARDS, MUST REPLACE. GREASE ON SHELVES."), {}),
    (V(38, "OBSERVED FLIES IN KITCHEN") + " | " + V(56, "EXHAUST HOOD NOT WORKING"), {"pests": [38], "hood": [56]}),
    (V(55, "NO EVIDENCE OF RODENTS AT THIS TIME. MUST SEAL HOLE IN WALL."), {}),
]
CAT_CASES = [(t, {k: v for k, v in want.items() if v}) for t, want in CAT_CASES]

PERSON_CASES = [("MARIA GARCIA", True), ("JOHN SMITH", True), ("CHEF TARYN", True), ("Smith, Wendell", True), ("TED LENART", True),
                ("MIMI DAO", True), ("JOSE LUIS HERNANDEZ", True), ("SOFIA BAKERY", False), ("PAUL HOUSE", False),
                ("GEORGE STREET PUB", False), ("MARIA'S KITCHEN", False), ("LOU MALNATI'S PIZZERIA", False), ("SUBWAY", False),
                ("BIG STAR", False), ("THA WING LOUNGE", False), ("JIMENEZ RESTAURANT", False), ("TACO BELL", False),
                ("JJ FISH", False), ("CHARLIES CHICAGO", False), ("MAXWELL STREET CICERO", False), ("ROSAS TAMALES INC", False),
                ("THE HAT", False), ("FIVE GUYS", False), ("JULIANA RESTAURANT", False), ("CAFE MUSTACHE", False), ("DON PEDRO CARNITAS", False), ("", False)]


def selftest():
    bad = [(t[:70], categorize(t), want) for t, want in CAT_CASES if categorize(t) != want]
    assert not bad, "category FAIL: " + json.dumps(bad)
    badp = [(n, person_name(n), w) for n, w in PERSON_CASES if person_name(n) != w]
    assert not badp, "person-name FAIL: " + json.dumps(badp)
    for r, want in [({"facility_type": "School", "dba_name": "X"}, True), ({"facility_type": "Children's Services Facility", "dba_name": "X"}, True),
                    ({"facility_type": "Daycare Above and Under 2 Years", "dba_name": "X"}, True), ({"facility_type": "Hospital", "dba_name": "X"}, True),
                    ({"facility_type": "Restaurant", "dba_name": "KIPP ONE ACADEMY"}, True), ({"facility_type": "", "dba_name": "TINY TOTS UNIVERSITY"}, True),
                    ({"facility_type": "Restaurant", "dba_name": "WISE OWL DAYCARE"}, True), ({"facility_type": "Mobile Food Preparer", "dba_name": "X"}, True),
                    ({"facility_type": "COOKING SCHOOL", "dba_name": "THE CHOPPING BLOCK"}, False), ({"facility_type": "Restaurant", "dba_name": "SUBWAY"}, False),
                    ({"facility_type": "Grocery Store", "dba_name": "LA GLORIA MARKET"}, False), ({"facility_type": "Restaurant", "dba_name": "ACADEMY"}, True)]:
        assert institution(r) == want, (r, want)
    # planted inspections: one of each list, each exclusion, a duplicate report, an out-of-window fail
    base = {"address": "1234 W MAIN ST ", "zip": "60601", "latitude": "41.88", "longitude": "-87.63", "risk": "Risk 1 (High)", "_area": "Loop",
            "facility_type": "Restaurant"}
    R = lambda i, name, lic, typ, res, day, v="", **kw: dict(base, inspection_id=str(i), dba_name=name, license_=lic, inspection_type=typ,
                                                            results=res, inspection_date=day + "T00:00:00.000", violations=v, **kw)
    rows = [
        R(1, "ACME TACOS", "111", "Canvass", "Fail", "2026-10-15", CAT_CASES[0][0]),
        R(2, "ACME TACOS", "111", "Canvass Re-Inspection", "Fail", "2026-09-30", V(2, "NO MANAGER")),
        R(3, "NEW PLACE", "222", "License", "Pass", "2026-10-14"),
        R(4, "KIPP ONE ACADEMY", "333", "Canvass", "Fail", "2026-10-14", CAT_CASES[0][0], facility_type="School"),
        R(5, "FRY HOUSE", "444", "Canvass", "Pass w/ Conditions", "2026-10-13", CAT_CASES[3][0]),
        R(6, "CLEAN DINER", "555", "Canvass", "Pass", "2026-10-13", CAT_CASES[3][0]),
        R(7, "MARIA GARCIA", "666", "Complaint", "Fail", "2026-10-12", CAT_CASES[0][0]),
        R(8, "FRY HOUSE", "444", "Canvass", "Pass w/ Conditions", "2026-10-13", CAT_CASES[3][0] + " | " + V(2, "X")),  # duplicate report
        R(9, "OLD FAIL", "777", "Canvass", "Fail", "2026-08-01", CAT_CASES[0][0]),
        R(10, "GONE BISTRO", "888", "Complaint", "Fail", "2026-10-02", CAT_CASES[0][0]),
        R(11, "GONE BISTRO", "888", "Canvass", "Out of Business", "2026-10-10"),
        R(12, "NO PESTS BAR", "999", "Canvass", "Fail", "2026-10-11", V(2, "NO MANAGER")),
        R(13, "NEW PLACE", "222", "Canvass", "Pass", "2025-01-01"),
        R(14, "NO PESTS BAR", "999", "Canvass Re-Inspection", "Fail", "2026-10-14", V(2, "NO MANAGER")),   # 2 fails, nothing a buyer does
        R(15, "TWO LICENSE TAVERN", "1001", "License", "Pass", "2026-10-15", address="925 W FULTON MARKET"),
        R(16, "TWO LICENSE TAVERN", "1002", "License", "Pass", "2026-10-15", address="925 W FULTON MARKET"),
    ]
    raw = {"source": {"name": "x", "url": DATASET_PAGE, "fetchedAt": "2026-10-18T03:00:00+00:00", "terms": CITY_TERMS},
           "rows": [r for r in rows if r["inspection_date"] >= "2026-09-11"], "history": [r for r in rows if r["inspection_date"] < "2026-09-11"]}
    d = build(raw)
    P, L = d["places"], d["lists"]
    assert d["asOf"] == "2026-10-17" and d["through"] == "2026-10-15" and d["window"]["from"] == "2026-09-16", (d["asOf"], d["through"], d["window"])
    assert L["flagged"] == ["L111", "L444"], L
    assert L["opening"] == ["L1002", "L222"] or L["opening"] == ["L1001", "L222"], L
    two = P[L["opening"][0]]
    assert two["licenses"] == ["1001", "1002"] and two["address"] == "925 W Fulton Market", two
    assert L["repeat"] == ["L111"] and P["L111"]["fails90"] == 2, L
    assert set(P) == {"L111", "L222", "L444", L["opening"][0]}, sorted(P)
    assert d["counts"]["excluded"] == {"business name is a person's name": 1, "school, day care, hospital, senior or mobile vendor": 1,
                                       "the City's latest result is out of business or not located": 1}, d["counts"]["excluded"]
    assert P["L444"]["flaggedIds"] == ["8"] and d["inspections"]["8"]["c"] == {"hood": [56]}, "duplicate report kept once, the fuller text"
    assert P["L111"]["cats"] == ["pests"] and P["L111"]["catsBy"] == {"flagged": ["pests"], "opening": [], "repeat": ["pests"]} and P["L111"]["address"] == "1234 W Main St" and P["L111"]["name"] == "Acme Tacos"
    assert P["L111"]["new"] and P["L222"]["new"] and P["L444"]["new"]
    assert P["L222"]["history"] == ["3", "13"], "a place's history spans its years on file"
    blob = json.dumps(d)
    assert "COMMENTS" not in blob.upper() and "DROPPINGS" not in blob.upper() and "MANAGER" not in blob.upper(), "notes leaked"
    assert d["inspections"]["1"]["v"] == [(38, "INSECTS, RODENTS, & ANIMALS NOT PRESENT")] or d["inspections"]["1"]["v"] == [[38, "INSECTS, RODENTS, & ANIMALS NOT PRESENT"]]
    s = sample(d)
    assert "Acme" not in json.dumps(s["examples"]["flagged"]) and "Main" not in json.dumps(s["examples"]["flagged"]), "free page names a failed place"
    assert [x["name"] for x in s["examples"]["opening"]] == ["Two License Tavern", "New Place"], s["examples"]["opening"]
    assert pretty("2026-10-05") == "Oct 5, 2026" and type_title("canvass re-inspection") == "Canvass Re-Inspection" and type_title("LICENSE") == "License"
    for t in (__doc__ or "",):
        assert "—" not in t
    print(f"rest_leads selftest ok ({len(CAT_CASES)} category cases, {len(PERSON_CASES)} name cases, 16 planted inspections)")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        selftest()
    elif a[:1] == ["--sample"]:
        d = build(json.load(open(a[1])))
        json.dump(sample(d), open(a[2] if len(a) > 2 else SAMPLE, "w"), indent=1)
        print(json.dumps({k: d["counts"][k] for k in ("places", "flagged", "opening", "repeat", "new")}))
    else:
        d = build(json.load(open(a[0])))
        json.dump(d, open(a[1], "w"), separators=(",", ":"))
        print(json.dumps({k: v for k, v in d["counts"].items() if k != "areas"}))
