#!/usr/bin/env python3
"""The fixed rules of the downstream leads pipeline, as pure functions with no network and no model.

Two entities, never mixed:
  Entity A, GC lead (pnf.gc_lead.v1): a City permit in a downstream completion stage with an adjacent Certificate of
    Occupancy or health inspection signal. Business-level fields only; it is committed to this public repo.
  Entity B, trade prospect (pnf.prospect.v1): the named decision-maker at a local finish-stage trade business (commercial
    cleaning, pressure washing, exterior work; see TRADE_VERTICALS) who gets our email. Personal data: it lives in the private CRM and in gitignored data/ files only.

Every validator returns a list of problem strings; an empty list is a pass. The CLIs (tools/validate_leads.py,
tools/copy_gate.py, tools/context_gate.py) turn any problem into exit code 1.
"""
import datetime as dt
import hashlib
import re

# ------------------------------------------------------------------ timing moat
# Canonical downstream stages. Only these pass the Timing Moat Gate.
DOWNSTREAM = (
    "Partial Occupancy Approved",
    "Inspections Under Way",
    "Final Inspection Scheduled",
    "Certificate of Occupancy Pending",
)
# How each City's own field maps onto a canonical stage. A value not listed here maps to None (rejected), so a new City
# label never slips through: it shows up in the ingest report's unmapped counts first.
CHICAGO_MILESTONES = {
    "CERTIFICATE OF OCCUPANCY PENDING (TEMPORARY OR PARTIAL OCCUPANCY APPROVED)": "Partial Occupancy Approved",
    "INSPECTIONS (CERTIFICATE OF OCCUPANCY REQUIRED)": "Inspections Under Way",
    "INSPECTIONS": "Inspections Under Way",
}
CHICAGO_UPSTREAM = {"PERMIT ISSUED (FEE DUE)", "PERMIT ISSUED", "APPLICATION", "PLAN REVIEW"}
CHICAGO_PAST = {"CERTIFICATE OF OCCUPANCY ISSUED", "COMPLETE"}
# Austin's permit dataset has no inspection milestone column. tools/permits_austin.py derives a stage from the City's own
# fields: a finaled building permit inside an open project ("Near finish") or an expiry the City pushed out after an
# inspection passed ("Work under way"). Both mean City inspections are under way; neither proves occupancy.
AUSTIN_STAGES = {"Near finish": "Inspections Under Way", "Work under way": "Inspections Under Way"}
AUSTIN_UPSTREAM = {"Permit issued"}

SIGNAL_TYPES = {
    "co_pending": "Certificate of Occupancy pending in the City's permit milestone",
    "co_required": "Certificate of Occupancy required at the City's final inspection",
    "co_flag": "Austin permit record carries the City's certificate_of_occupancy flag",
    "health_license_inspection": "food establishment license or pre-opening inspection at the same normalized address",
}
UPSTREAM_PHRASES = ("broke ground", "breaking ground", "break ground", "groundbreaking", "ground breaking", "just permitted",
                    "permit was just issued", "new permit filed")

# ------------------------------------------------------------------ inboxes
ROLE_LOCALPARTS = ("info", "contact", "sales", "admin", "office", "dispatch", "estimating", "bids", "support", "hello",
                   "team", "service", "services", "help", "enquiries", "inquiries", "general", "mail", "booking", "bookings",
                   "billing", "accounts", "accounting", "careers", "jobs", "hr", "marketing", "noreply", "no-reply",
                   "donotreply", "webmaster", "frontdesk", "reception", "quotes", "quote", "estimate", "estimates",
                   "cleaning", "clean", "customerservice", "operations", "ops", "orders", "schedule", "scheduling",
                   "infoteam", "contactus", "salesteam", "officemanager", "frontoffice", "theoffice", "customercare",
                   "inquiry", "enquiry", "projects", "project", "bid", "proposals", "leads", "work", "jobs", "crew")
ROLE_RE = re.compile(r"^(?:%s)(?:[._+-].*|\d+)?$" % "|".join(re.escape(x) for x in ROLE_LOCALPARTS), re.I)
FREEMAIL = {"gmail.com", "googlemail.com", "yahoo.com", "ymail.com", "outlook.com", "hotmail.com", "live.com", "msn.com",
            "icloud.com", "me.com", "mac.com", "aol.com", "comcast.net", "att.net", "sbcglobal.net", "verizon.net",
            "protonmail.com", "proton.me", "gmx.com", "mail.com", "zoho.com", "yandex.com"}
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z'.-]{0,39}(?: [A-Za-z][A-Za-z'.-]{0,39})?$")
DECISION_TITLE = re.compile(r"\b(?:owner|co-?owner|founder|co-?founder|president|ceo|chief|principal|partner|managing|"
                            r"general manager|gm|director|vice president|vp|head of|"
                            r"proprietor|operations manager|business manager|branch manager)\b", re.I)
OK_EMAIL_STATUS = {"verified", "valid", "deliverable", "catch_all", "accept_all"}
CATCH_ALL = {"catch_all", "accept_all"}
PRODUCTS = {"chicago-construction": "chicago", "austin-construction": "austin", "chicago-restaurant": "chicago"}
SOURCES = {"apollo", "hunter", "clay", "site", "manual"}
# Enrichment ladder (Todd, Oct 22, 2026, live chat: "Let's go with your suggestion"): the owner's name comes from a
# public record first, then the business's own site, then Hunter as a capped fallback. owner_source records where the
# name came from. A one-person business reads its own info@: an owner-read inbox published on the business's own site
# may carry a named owner's email ("Hi Maria" to info@) only when the name comes from the City's owner record or the
# business's own site. Every other role inbox stays out.
OWNER_SOURCES = {"city_owner_record", "site_about", "hunter", "apollo", "clay", "manual"}
OWNER_READ_SOURCES = {"city_owner_record", "site_about"}
OWNER_READ_ROLES = {"info", "contact", "hello", "office", "admin", "mail", "general", "inquiries", "inquiry", "sales", "team"}
PENDING_STATUS = "unverified"   # a site or pattern address waiting for the Bouncer check in the outreach run

# ------------------------------------------------------------------ trade verticals
# Todd, Oct 22: one downstream permit can be pitched to non-competing finish-stage trades. Each vertical lists the
# products its prospects may belong to and the lead stages its email may name; a prospect with no trade_vertical is
# commercial_cleaning, so every record written before Oct 22 keeps working. exterior_turnkey (pressure washing, window
# washing, lot striping and sealcoating) gets only Chicago Partial Occupancy Approved leads, where the timing claim holds.
# window_cleaning (a business whose main service is commercial window cleaning) gets new builds of $5M or more at
# partial occupancy or under inspection; dumpster_rental (roll-off rental and construction hauling) gets jobs under $5M under inspection,
# where the GC may still call around for cans; security (construction site guards, patrols and camera towers) gets new
# builds of $20M or more at either stage. A business offering two or more exterior trades stays
# exterior_turnkey.
TRADE_DEFAULT = "commercial_cleaning"
TRADE_VERTICALS = {
    "commercial_cleaning": {"products": set(PRODUCTS), "stages": set(DOWNSTREAM)},
    "exterior_turnkey": {"products": {"chicago-construction"}, "stages": {"Partial Occupancy Approved"}},
    # Step 2 buyer types (Todd, Oct 22, 2026, 10:55 pm, live chat: "Let's go with your recommendations"). Optional keys:
    # work_types maps a stage to the City work types allowed there (a stage not listed allows any); min_valuation and
    # max_valuation bound the permit valuation the vertical's email may name. Checker round 1 (Oct 22): interior fit-outs
    # have no exterior glass, big jobs under inspection already have a hauler, and small builds never hire guards.
    "window_cleaning": {"products": {"chicago-construction", "austin-construction"},
                        "stages": {"Partial Occupancy Approved", "Inspections Under Way"},
                        "work_types": {"Partial Occupancy Approved": {"New construction"}, "Inspections Under Way": {"New construction"}},
                        # the City tags some floor build-outs as new construction; those have no exterior glass
                        "min_valuation": 5_000_000,
                        "exclude_scope": re.compile(r"build ?-?out|fit ?-?out|finish ?-?out|first time|interior (?:alteration|remodel|renovation|work)", re.I)},
    "dumpster_rental": {"products": {"chicago-construction", "austin-construction"}, "stages": {"Inspections Under Way"},
                        "max_valuation": 5_000_000},
    "security": {"products": {"chicago-construction", "austin-construction"},
                 "stages": {"Partial Occupancy Approved", "Inspections Under Way"},
                 "work_types": {"Partial Occupancy Approved": {"New construction"}, "Inspections Under Way": {"New construction"}},
                 "min_valuation": 20_000_000},
}

STEP2_TRADES = {"window_cleaning", "dumpster_rental", "security"}   # their {kind} comes from kind_display, gate-checked


def trade_of(x):
    """The record's trade vertical; blank or missing means commercial_cleaning."""
    return str((x or {}).get("trade_vertical") or TRADE_DEFAULT)


def trade_problems(product, trade, lead=None):
    """A vertical that exists, a product it allows and, with a lead, a stage and city it allows."""
    v = TRADE_VERTICALS.get(trade)
    if v is None:
        return [f"unknown trade_vertical {trade!r} (one of {sorted(TRADE_VERTICALS)})"]
    p = []
    if product not in v["products"]:
        p.append(f"trade_vertical {trade} does not serve product {product!r}")
    if lead is not None:
        if lead.get("stage") not in v["stages"]:
            p.append(f"trade_vertical {trade} cannot use a {lead.get('stage')!r} lead")
        if lead.get("city") not in {PRODUCTS.get(x) for x in v["products"]}:
            p.append(f"trade_vertical {trade} cannot use a {lead.get('city')!r} lead")
        wt = (v.get("work_types") or {}).get(lead.get("stage"))
        if wt is not None and lead.get("work_type") not in wt:
            p.append(f"trade_vertical {trade} cannot use a {lead.get('work_type')!r} lead at {lead.get('stage')!r}")
        if v.get("min_valuation") and (lead.get("valuation") or 0) < v["min_valuation"]:
            p.append(f"trade_vertical {trade} needs a valuation of {value_display(v['min_valuation'])} or more")
        if v.get("exclude_scope") is not None and v["exclude_scope"].search(str(lead.get("scope") or "")):
            p.append(f"trade_vertical {trade} cannot use an interior fit-out (scope says {v['exclude_scope'].search(str(lead.get('scope'))).group(0)!r})")
        if v.get("max_valuation") and (lead.get("valuation") or 0) >= v["max_valuation"]:
            p.append(f"trade_vertical {trade} needs a valuation under {value_display(v['max_valuation'])}")
    return p


def trade_fits(trade, lead):
    """True when the vertical may name this lead: its city, stage, work type and valuation."""
    v = TRADE_VERTICALS.get(trade)
    prods = sorted(x for x in (v or {}).get("products", ()) if PRODUCTS.get(x) == (lead or {}).get("city"))
    return bool(prods) and not trade_problems(prods[0], trade, lead)

# ------------------------------------------------------------------ outreach copy
# Variants (Todd, Oct 22, 2026, live chat: "A and B, test 1" and the copy gate change). A template's id is its heading's
# T number plus its Variant letter (T2-B); blank Variant means A. Each prospect gets one arm for life, by a fixed split on
# its id, so the arms fill evenly and a rerun never moves anyone; its follow-ups use the same arm.
VARIANT_ID_RE = re.compile(r"^T\d+-[A-Z]$")
MAX_FOLLOWUPS = 2         # Todd, Oct 22, 2026, live chat: "Yes, two follow-ups", each with a new real job


def assign_variant(prospect_id, letters):
    """The test arm (a letter) for a prospect among the letters a template slot offers: sha256 of the id, mod the count."""
    ls = sorted(set(letters))
    if not ls:
        return ""
    return ls[int(hashlib.sha256(str(prospect_id).encode("utf-8")).hexdigest(), 16) % len(ls)]


MAX_WORDS = 75            # a draft fails at 75 words or more
MAX_SUBJECT_WORDS = 12
TLDS = ("com|net|org|io|co|ai|app|biz|info|us|me|ly|xyz|site|online|store|shop|dev|tech|pro|link|page|ws|tv|gg|"
        "cc|so|to|in|uk|ca|club|live|world|today|agency|services|solutions|cleaning|network|email|website|web")
URL_RE = re.compile(r"https?://|www\.|gumroad|bit\.ly|\b[a-z0-9-]+\.(?:%s)\b|\b[a-z0-9-]+\s\.\s?(?:com|net|org|io)\b|"
                    r"\b[a-z0-9-]+\.\s(?:com|net|org|io)\b|\bdot\s+(?:com|net|org|io|co|ai|app)\b|[a-z0-9-]+\.[a-z]{2,24}/" % TLDS, re.I)
PITCH_RE = re.compile(r"\$\s?\d+\s*(?:/|a|per)\s*(?:mo|month)\b|\bsubscri\w*|\bfree trial\b|\bsign up\b|\bcheckout\b|"
                      r"\bbuy now\b|\bdiscount\b|\bmembership\b|\bpricing\b|\bprice\b", re.I)
DASHES = ("\u2014", "\u2013")
# CAN-SPAM block the sender appends under every first email. It is fixed text, checked byte for byte, and not counted
# against the 75 words because it is compliance, not copy.
# Line 3 opens with the advertisement label 15 U.S.C. 7704(a)(5)(A)(i) asks of a cold email (no prior consent):
# legal/reviews/2026-10-24-cold-email-ad-label.md (Todd, Oct 24: "research this yourself and come up with what you think is best").
FOOTER = ("ProofNotFluff\n680 North Lake Shore Drive, Suite 110-2964, Chicago, IL 60611\n"
          "This is a sales email. Not interested? Reply \"no thanks\" and we will not email you again.")


ABBREV_RE = re.compile(r"\b(?:L\.L\.C|L\.L\.P|P\.L\.L\.C|Inc|Co|Corp|Ltd|Bros|Assoc|Dr|St|Ave|Blvd|Rd|Ln|Ct|Pl|Pkwy|Hwy|Ste|Jr|Sr|Mt|Ft|N|S|E|W)\.",
                       re.I)


def link_safe(text):
    """Text with the dots of corporate and street abbreviations removed ('Henry Bros.Co.', 'L.L.C.', 'Dr.', 'St.'), so the
    link check judges only real domains. 'acme.co', 'x.com' and 'www.' are untouched and still caught."""
    t = text or ""
    for _ in range(3):
        t = ABBREV_RE.sub(lambda m: m.group(0)[:-1].replace(".", ""), t)
    return t


def street_display(address):
    """The street as an email names it: no house number, no building, unit or frontage-road tail.
    '7009 Ed Bluestein Blvd Svrd Nb Bldg 1' gives 'Ed Bluestein Blvd'."""
    a = re.sub(r"^\s*\d+[A-Za-z]?\s+", "", address or "")
    a = re.sub(r"\s+(?:#|Unit|Ste|Suite|Apt|Fl|Floor|Bldg|Building|Rm|Room|Spc|Space)\b.*$", "", a, flags=re.I)
    a = re.sub(r"\s+Svrd(?:\s+[NSEW]b)?\b.*$", "", a, flags=re.I)
    return a.strip()


def words(text):
    return re.findall(r"[A-Za-z0-9$][A-Za-z0-9$'.,%-]*", text or "")


GC_SUFFIX = re.compile(r",?\s+\b(?:L\.?L\.?C|INC(?:ORPORATED)?|CORP(?:ORATION)?|CO|COMPANY|LTD|L\.?P|LLP|PLLC)\b\.?\s*$", re.I)


def gc_display(name):
    """The general contractor as an email names it: the City's business name without a trailing legal suffix.
    'Bartlett Cocke General Contractors, LLC' gives 'Bartlett Cocke General Contractors'. Drafter and gate both use it."""
    n = (name or "").strip()
    # checkers, Oct 22: a trailing '(Chicago)' or ' Chicago', a leading 'The ', and a glued 'Edwardsconstruction' go
    n = re.sub(r"^The\s+(?=\S+\s+\S+\s+\S)", "", n)
    n = re.sub(r"(?<=[a-z])(construction|contracting|builders)\b", lambda m: " " + m.group(1).capitalize(), n)
    for _ in range(3):
        n = re.sub(r"\s*\([^)]*\)\s*$", "", GC_SUFFIX.sub("", n).strip(" ,")).strip(" ,")
        n = re.sub(r"(?:\s+-)?\s+(?:Chicago|Austin)$", "", n).strip(" ,-")
    return n


KIND_WORDS = (("townhouse", re.compile(r"townhouses?|town homes?|townhomes?", re.I)),
              ("apartment", re.compile(r"\bapartments?\b|dwelling units?|multi[- ]?family|\bR-2\b|residential", re.I)),
              ("school", re.compile(r"\bschools?\b|academic|\bE[- ]educational|\bE occupancy", re.I)),
              ("hotel", re.compile(r"\bhotels?\b", re.I)),
              ("office", re.compile(r"\boffices?\b|\bB[- ]business", re.I)))


# a scope naming another main use (a casino, a sports facility, a terminal) is a 'building', never one of the four words
KIND_OTHER = re.compile(r"casino|sports?\b|stadium|arena|terminal|\bstation\b|hospital|warehouse|laborator|church|museum|"
                        r"library|data cent|industrial|retail|restaurant|event cent|quantum", re.I)


def kind_display(lead):
    """The one {kind} word a step 2 email uses for a lead, from the City scope: townhouse or apartment when homes are
    named, else school, hotel or office when exactly one matches, else 'building' (Legal desk and checkers, Oct 22: a
    wrong kind word outs the sender)."""
    s = str((lead or {}).get("scope") or "")
    if KIND_OTHER.search(s):
        return "building"
    hits = [k for k, rx in KIND_WORDS if rx.search(s)]
    if hits and hits[0] in ("townhouse", "apartment"):   # homes first: a 'leasing office' does not make it an office
        return hits[0]
    return hits[0] if len(hits) == 1 else "building"


def value_display(v):
    """$45M style for an email: whole millions under $1 billion ($4.5M under $10M), $1.2B from $1 billion."""
    # halves round up, exactly (Oct 22 checker: float formatting gave $9.4M for 9,450,000 and $38M for 38,500,000)
    from decimal import Decimal, ROUND_HALF_UP
    d = Decimal(str(v or 0))
    q = lambda x, places: x.quantize(Decimal(places), rounding=ROUND_HALF_UP)
    if d >= Decimal("1e9"):
        return f"${q(d / Decimal('1e9'), '0.1')}B"
    if d >= Decimal("1e7"):
        return f"${q(d / Decimal('1e6'), '1')}M"
    return f"${q(d / Decimal('1e6'), '0.1')}M"


def domain_of(url_or_domain):
    d = (url_or_domain or "").strip().lower()
    d = re.sub(r"^[a-z]+://", "", d).split("/")[0].split("?")[0].split(":")[0]
    return d[4:] if d.startswith("www.") else d


# ------------------------------------------------------------------ address join key
SUFFIX = {"STREET": "ST", "ST.": "ST", "AVENUE": "AVE", "AV": "AVE", "AVE.": "AVE", "BOULEVARD": "BLVD", "BLVD.": "BLVD",
          "ROAD": "RD", "RD.": "RD", "DRIVE": "DR", "DR.": "DR", "PLACE": "PL", "COURT": "CT", "LANE": "LN", "PARKWAY": "PKWY",
          "HIGHWAY": "HWY", "TERRACE": "TER", "CIRCLE": "CIR", "EXPRESSWAY": "EXPY", "SQUARE": "SQ", "TRAIL": "TRL",
          "PLAZA": "PLZ", "CROSSING": "XING", "COVE": "CV", "PASS": "PASS", "WAY": "WAY", "LOOP": "LOOP", "BEND": "BND"}
DIRECTION = {"NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W", "N.": "N", "S.": "S", "E.": "E", "W.": "W",
             "NORTHEAST": "NE", "NORTHWEST": "NW", "SOUTHEAST": "SE", "SOUTHWEST": "SW"}
UNIT_RE = re.compile(r"\s+(?:#|UNIT|STE|SUITE|APT|FL|FLOOR|BLDG|BUILDING|RM|ROOM|SPC|SPACE)\b.*$")


def address_key(addr):
    """The join key between a permit and an adjacent dataset row: house number, direction, street name and suffix, upper
    case, standard abbreviations, no unit or suite, the first number of a range. '1234-40 West Madison Street, Suite 2'
    and '1234 W MADISON ST' both give '1234 W MADISON ST'. Returns '' when there is no house number."""
    a = (addr or "").upper().replace(",", " ")
    a = re.sub(r"\s+", " ", a).strip()
    a = UNIT_RE.sub("", a)
    a = re.sub(r"^(\d+)[A-Z]?\s*-\s*\d+[A-Z]?\b", r"\1", a)
    parts = a.split(" ")
    if not parts or not parts[0].isdigit():
        return ""
    out = [parts[0]]
    for i, p in enumerate(parts[1:], 1):
        p = p.strip(".")
        if i == 1 and (p in DIRECTION or p in DIRECTION.values()):
            out.append(DIRECTION.get(p, p))
        else:
            out.append(SUFFIX.get(p, SUFFIX.get(p + ".", p)))
    return " ".join(x for x in out if x)


# ------------------------------------------------------------------ Entity A
GC_REQUIRED = ("lead_id", "city", "permit_id", "stage", "stage_source", "issue_date", "address", "address_key",
               "valuation", "gc_company", "signals", "source_url")


def validate_gc_lead(lead, today=None):
    """Schema plus the Timing Moat Gate for one GC lead."""
    p, lid = [], lead.get("lead_id", "?")
    for k in GC_REQUIRED:
        if lead.get(k) in (None, "", []) and k != "signals":
            p.append(f"{lid}: missing {k}")
    if lead.get("city") not in ("chicago", "austin"):
        p.append(f"{lid}: city must be chicago or austin")
    if lead.get("stage") not in DOWNSTREAM:
        p.append(f"{lid}: stage {lead.get('stage')!r} is not a downstream completion stage")
    src = (lead.get("stage_source") or "").upper()
    if src in CHICAGO_UPSTREAM or src in {s.upper() for s in AUSTIN_UPSTREAM}:
        p.append(f"{lid}: upstream City stage {lead.get('stage_source')!r}")
    if src in CHICAGO_PAST:
        p.append(f"{lid}: past handover ({lead.get('stage_source')!r})")
    sigs = lead.get("signals") or []
    if not isinstance(sigs, list) or not sigs:
        p.append(f"{lid}: no adjacent Certificate of Occupancy or health inspection signal")
    for s in sigs if isinstance(sigs, list) else []:
        if s.get("type") not in SIGNAL_TYPES:
            p.append(f"{lid}: unknown signal type {s.get('type')!r}")
        if not s.get("dataset") or not s.get("record_id"):
            p.append(f"{lid}: signal without dataset and record_id")
    try:
        v = float(lead.get("valuation") or 0)
        if v < 500000:
            p.append(f"{lid}: valuation {v:,.0f} under $500,000")
    except (TypeError, ValueError):
        p.append(f"{lid}: valuation not a number")
    if lead.get("site_contact") not in (None, {}):
        p.append(f"{lid}: site_contact must stay out of the public file (members' encrypted data only)")
    for k in ("scope", "gc_company", "address"):
        t = str(lead.get(k) or "")
        if re.search(r"@|\(?\b\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b", t):
            p.append(f"{lid}: {k} carries an email or phone number")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(lead.get("issue_date") or "")):
        p.append(f"{lid}: issue_date not YYYY-MM-DD")
    text = " ".join(str(lead.get(k) or "") for k in ("stage", "scope")).lower()
    for ph in UPSTREAM_PHRASES:
        if ph in text:
            p.append(f"{lid}: upstream phrase {ph!r}")
    return p


def validate_gc_file(doc, max_age_days=None, now=None):
    p = []
    if not isinstance(doc, dict):
        return ["gc file: not a JSON object"]
    if doc.get("schema") != "pnf.gc_lead.v1":
        p.append("gc file: schema must be pnf.gc_lead.v1")
    leads = doc.get("leads")
    if not isinstance(leads, list):
        return p + ["gc file: leads must be a list"]
    ids = [x.get("lead_id") for x in leads]
    if len(ids) != len(set(ids)):
        p.append("gc file: duplicate lead_id")
    if not leads:
        p.append("gc file: zero leads (a City column or label change would look like this; check the ingest report)")
    for x in leads:
        p += validate_gc_lead(x) if isinstance(x, dict) else ["gc file: a lead is not an object"]
    if max_age_days is not None:
        try:
            at = dt.datetime.fromisoformat(str(doc.get("generatedAt")).replace("Z", "+00:00"))
            if at.tzinfo is None:
                raise ValueError("no time zone")
            now = now or dt.datetime.now(dt.timezone.utc)
            if at > now + dt.timedelta(hours=1):
                p.append(f"gc file: generatedAt {doc.get('generatedAt')} is in the future")
            elif (now - at).days > max_age_days:
                p.append(f"gc file: generatedAt {doc.get('generatedAt')} is older than {max_age_days} days")
        except (ValueError, TypeError):
            p.append("gc file: generatedAt unreadable")
    return p


# ------------------------------------------------------------------ Entity B
PROSPECT_REQUIRED = ("prospect_id", "product", "business", "website_domain", "city", "first_name", "last_name", "title",
                     "email", "email_source", "email_status")


def owner_read_inbox(email, owner_source="", email_source=""):
    """True for the one role-inbox exception: an owner-read local part (info@, office@ ...) published on the business's
    own site, addressed to an owner named by the City's owner record or the business's own site."""
    local = (email or "").strip().lower().split("@", 1)[0]
    return local in OWNER_READ_ROLES and owner_source in OWNER_READ_SOURCES and email_source == "site"


def inbox_problems(email, website_domain="", first_name="", last_name="", owner_source="", email_source=""):
    """The Inbox Gate for one address: syntax, no role-based local part (except the owner-read exception above), no free
    mail, on the business's own domain, and, when the person's name is known, a local part built from that name (dana@,
    dreyes@, dana.reyes@, reyes@)."""
    e = (email or "").strip()
    if not EMAIL_RE.match(e):
        return [f"{e or '(blank)'}: not a valid email address"]
    local, dom = e.lower().split("@", 1)
    p = []
    owner_read = owner_read_inbox(e, owner_source, email_source)
    if ROLE_RE.match(local) and not owner_read:
        p.append(f"{e}: role-based inbox ({local}@), a named decision-maker is required")
    if dom in FREEMAIL:
        p.append(f"{e}: free-mail domain, a work address on the business's own domain is required")
    wd = domain_of(website_domain)
    if wd and not (dom == wd or dom.endswith("." + wd)):
        p.append(f"{e}: domain {dom} does not match the business website {wd}")
    f, l = re.sub(r"[^a-z]", "", (first_name or "").lower()), re.sub(r"[^a-z]", "", (last_name or "").lower())
    flat = re.sub(r"[^a-z]", "", local)
    if f and l and not owner_read and not (f in flat or l in flat or flat in (f[0] + l, f + l[0], f[0] + l[0])):
        p.append(f"{e}: the address is not {first_name} {last_name}'s own (local part does not carry the name)")
    return p


def validate_prospect(x, pending=False):
    """One prospect. pending=True: the same rules, except the address must be waiting for its Bouncer check
    (email_status unverified) instead of already deliverable."""
    p, pid = [], x.get("prospect_id", "?")
    for k in PROSPECT_REQUIRED:
        if not str(x.get(k) or "").strip():
            p.append(f"{pid}: missing {k}")
    sig = SIGNAL_PRODUCTS.get(x.get("product"))
    if sig is not None:
        if x.get("city") != sig["city"]:
            p.append(f"{pid}: city {x.get('city')!r} does not match product {x['product']}")
    elif x.get("product") not in PRODUCTS:
        p.append(f"{pid}: unknown product {x.get('product')!r}")
    elif x.get("city") != PRODUCTS[x["product"]]:
        p.append(f"{pid}: city {x.get('city')!r} does not match product {x['product']}")
    for k in ("first_name", "last_name"):
        if x.get(k) and not NAME_RE.match(str(x[k]).strip()):
            p.append(f"{pid}: {k} {x.get(k)!r} is not a plain name")
    if x.get("title") and not DECISION_TITLE.search(str(x["title"])):
        p.append(f"{pid}: title {x.get('title')!r} is not a decision-maker role")
    if x.get("email_source") and x["email_source"] not in SOURCES:
        p.append(f"{pid}: email_source must be one of {sorted(SOURCES)}")
    if pending:
        if x.get("email_status") != PENDING_STATUS:
            p.append(f"{pid}: a pending prospect must have email_status {PENDING_STATUS!r}")
    elif x.get("email_status") and x["email_status"] not in OK_EMAIL_STATUS:
        p.append(f"{pid}: email_status {x.get('email_status')!r} is not deliverable")
    if x.get("owner_source") and x["owner_source"] not in OWNER_SOURCES:
        p.append(f"{pid}: owner_source must be one of {sorted(OWNER_SOURCES)}")
    if x.get("do_not_email") is True:
        p.append(f"{pid}: do_not_email is set")
    cnt = COUNT_PRODUCTS.get(x.get("product")) or {}
    if sig is not None:
        if trade_of(x) not in sig["trades"] and trade_of(x) not in cnt.get("trades", ()):
            p.append(f"{pid}: trade_vertical {trade_of(x)} does not serve product {x.get('product')!r} (one of {sorted(sig['trades'])})")
    else:
        p += [f"{pid}: {m}" for m in trade_problems(x.get("product"), trade_of(x))]
    p += [f"{pid}: {m}" for m in inbox_problems(x.get("email"), x.get("website_domain"), x.get("first_name"), x.get("last_name"),
                                                x.get("owner_source") or "", x.get("email_source") or "")]
    return p


def validate_prospect_file(doc):
    p = []
    if not isinstance(doc, dict):
        return ["prospect file: not a JSON object"]
    if doc.get("schema") != "pnf.prospect.v1":
        p.append("prospect file: schema must be pnf.prospect.v1")
    rows = doc.get("prospects")
    if not isinstance(rows, list):
        return p + ["prospect file: prospects must be a list"]
    seen_e, seen_d = set(), set()
    for x in rows:
        p += validate_prospect(x)
        e = (x.get("email") or "").lower()
        d = (x.get("product"), domain_of(x.get("website_domain")))
        if e in seen_e:
            p.append(f"{x.get('prospect_id')}: duplicate email")
        if d in seen_d:
            p.append(f"{x.get('prospect_id')}: second contact at the same business for {d[0]} (one decision-maker per business)")
        seen_e.add(e)
        seen_d.add(d)
    if rows:
        ca = sum(1 for x in rows if x.get("email_status") in CATCH_ALL)
        if ca * 10 > len(rows):
            p.append(f"prospect file: {ca} of {len(rows)} addresses are catch-all, over the 10% cap")
    pend = doc.get("pending", [])
    if not isinstance(pend, list):
        return p + ["prospect file: pending must be a list"]
    for x in pend:
        p += validate_prospect(x, pending=True)
        d = (x.get("product"), domain_of(x.get("website_domain")))
        if d in seen_d:
            p.append(f"{x.get('prospect_id')}: second contact at the same business for {d[0]} (one decision-maker per business)")
        seen_d.add(d)
    return p


# ------------------------------------------------------------------ the agent's two outputs
def validate_matches(doc, leads_by_id, prospects_by_id):
    p = []
    rows = doc.get("matches") if isinstance(doc, dict) else None
    if not isinstance(doc, dict) or doc.get("schema") != "pnf.match.v1" or not isinstance(rows, list):
        return ["match file: schema must be pnf.match.v1 with a matches list"]
    used = set()
    for m in rows:
        pid, lid = m.get("prospect_id"), m.get("lead_id")
        if pid not in prospects_by_id:
            p.append(f"match {pid}: prospect not in the validated prospect file")
            continue
        if lid not in leads_by_id:
            p.append(f"match {pid}: lead {lid} not in the validated GC lead file")
            continue
        if pid in used:
            p.append(f"match {pid}: prospect matched twice")
        used.add(pid)
        if prospects_by_id[pid]["city"] != leads_by_id[lid]["city"]:
            p.append(f"match {pid}: prospect city and lead city differ")
        pr = prospects_by_id[pid]
        p += [f"match {pid}: {m}" for m in trade_problems(pr.get("product"), trade_of(pr), leads_by_id[lid])]
        if not str(m.get("reason") or "").strip():
            p.append(f"match {pid}: reason missing")
    return p


def copy_problems(subject, body, first_name=None, lead=None):
    """The Outreach Copy Gate for one drafted email (body without the fixed footer)."""
    p, b, s = [], body or "", subject or ""
    n = len(words(b))
    if n >= MAX_WORDS:
        p.append(f"body is {n} words, the limit is under {MAX_WORDS}")
    if len(words(s)) > MAX_SUBJECT_WORDS:
        p.append(f"subject is {len(words(s))} words, the limit is {MAX_SUBJECT_WORDS}")
    gc_name = gc_display(lead.get("gc_company")) if lead else ""
    for label, t in (("subject", s), ("body", b)):
        m = URL_RE.search(link_safe(t))
        if m:
            p.append(f"{label} carries a link or domain ({m.group(0)!r})")
        for d in DASHES:
            if d in t:
                p.append(f"{label} carries an em or en dash")
        low = t.lower().replace(gc_name.lower(), " ") if gc_name else t.lower()   # a builder's legal name is not copy
        for ph in UPSTREAM_PHRASES:
            if ph in low:
                p.append(f"{label} uses upstream phrase {ph!r}")
        m = PITCH_RE.search(t)
        if m:
            p.append(f"{label} pitches the paid product ({m.group(0)!r}); the first touch asks permission only")
        if re.search(r"[{}\[\]<>]", t):
            p.append(f"{label} has a leftover placeholder bracket")
    if first_name is not None:
        if not re.match(r"^Hi %s,\s" % re.escape(first_name), b):
            p.append(f"body must open with 'Hi {first_name},'")
    if not b.rstrip().endswith("?"):
        p.append("body must end with the permission question")
    if lead is not None:
        gc = gc_display(lead.get("gc_company"))
        if gc.lower() not in b.lower():
            p.append(f"body does not name the general contractor {gc!r}")
        for m in re.findall(r"\$\d+(?:\.\d+)?[MB]\b", b):
            if m != value_display(lead.get("valuation")):
                p.append(f"body states {m}, the lead's valuation is {value_display(lead.get('valuation'))}")
        street = street_display(lead.get("address")).lower()
        if street and street not in b.lower():
            p.append(f"body does not name the lead's street ({street!r})")
        stage_words = {"Partial Occupancy Approved": "partial occupancy", "Inspections Under Way": "inspection",
                       "Final Inspection Scheduled": "final inspection", "Certificate of Occupancy Pending": "certificate of occupancy"}
        want = stage_words.get(lead.get("stage"), "")
        if want and want not in b.lower():
            p.append(f"body does not state the lead's downstream stage ({want!r})")
    return p


def validate_drafts(doc, leads_by_id, prospects_by_id, matches_by_prospect=None):
    p = []
    rows = doc.get("drafts") if isinstance(doc, dict) else None
    if not isinstance(doc, dict) or doc.get("schema") != "pnf.draft.v1" or not isinstance(rows, list):
        return ["draft file: schema must be pnf.draft.v1 with a drafts list"]
    seen = set()
    for d in rows:
        if not isinstance(d, dict):
            p.append("draft file: a draft is not an object")
            continue
        if d.get("prospect_id") in seen:
            p.append(f"draft {d.get('prospect_id')}: second draft to the same prospect in one batch")
        seen.add(d.get("prospect_id"))
        if matches_by_prospect is not None and matches_by_prospect.get(d.get("prospect_id")) != d.get("lead_id"):
            p.append(f"draft {d.get('prospect_id')}: lead_id differs from the validated match")
        pid, lid = d.get("prospect_id"), d.get("lead_id")
        pr, ld = prospects_by_id.get(pid), leads_by_id.get(lid)
        if pr is None or ld is None:
            p.append(f"draft {pid}: prospect or lead not in the validated files")
            continue
        if (d.get("to") or "").lower() != pr["email"].lower():
            p.append(f"draft {pid}: to address differs from the prospect's validated email")
        p += [f"draft {pid}: {m}" for m in inbox_problems(d.get("to"), pr.get("website_domain"), pr.get("first_name"), pr.get("last_name"),
                                                          pr.get("owner_source") or "", pr.get("email_source") or "")]
        p += [f"draft {pid}: {m}" for m in trade_problems(pr.get("product"), trade_of(pr), ld)]
        p += [f"draft {pid}: {m}" for m in copy_problems(d.get("subject"), d.get("body"), pr["first_name"], ld)]
    return p


# ------------------------------------------------------------------ signal leads (license, citation)
# Todd, Oct 22, 2026, live chat (decision 2): "Copy gate extension for license and citation signals: approved". A signal
# lead is a City record that is not a permit: a new business license (r5kz-chrr) or an open building citation (22u3-xenr).
# Business-level fields only; the permit gate above is untouched. Each kind is one entry in SIGNAL_KINDS (its schema,
# fields, date field and signal words), so a third kind (a restaurant inspection) is one more entry and one more
# words function. The members' full lists stay in the runner; a signal lead file lives in data/work/ for a run.
SIGNAL_WINDOW_DAYS = 30   # the honest claim: the City record is dated inside the last 30 days on the send day
SIGNAL_STEPS = ("first", "followup1", "followup2")   # MAX_FOLLOWUPS follow-ups, each naming a lead not sent before
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
DATE_IN_COPY = re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}\b"
                          r"|\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b|\b\d{4}-\d{2}-\d{2}\b")
PERSONAL_TEXT = re.compile(r"@|\(?\b\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b")
STREET_TYPES = {"st", "ave", "av", "blvd", "rd", "dr", "pl", "ct", "ln", "pkwy", "hwy", "ter", "cir", "expy", "sq", "trl", "plz",
                "way", "row"}
UNIT_WORD = re.compile(r"^(?:#.*|unit|ste|suite|apt|fl|floor|bldg|building|rm|room|spc|space|bsmt|basement|mezz\.?|rear|front|"
                       r"strfrnt|storefront)$", re.I)
# Exterior repairs the City cites (the same words as tools/exterior_chicago.py EXTERIOR), matched on the lead's
# description to find the trade, and on the email to find the repair it names.
EXTERIOR_TRADES = {
    "masonry": r"\b(?:exterior wall|parapet|lintels?|cornice|chimney|masonry|tuckpoint\w*|coping|brick\w*)\b",
    "porch_stairs": r"\b(?:porch\w*|exterior stair\w*|fire escape\w*|balcon\w*)\b",
    "windows_doors": r"\b(?:window\w*|exterior door\w*|screens?)\b",
    "roof": r"\b(?:roof\w*|eaves|gutter\w*|downspout\w*|flashing)\b",
    "fence": r"\b(?:fence\w*)\b",
}
ELEVATOR_WORD = re.compile(r"\belevators?\b", re.I)


def signal_address(raw):
    """A City address cut to house number and street, the form a signal lead stores: the first number of a range, no
    unit, floor or suite. '495-499 N Milwaukee Ave Basement, 1, Mezz.' gives '495 N Milwaukee Ave'; '4329 N Mozart St 1f'
    gives '4329 N Mozart St'; 'N Broadway 2 P105' keeps 'N Broadway'. '' when there is no house number."""
    a = re.sub(r"\s+", " ", (raw or "").replace(",", " ")).strip()
    m = re.match(r"^(\d+)(?:\s*-\s*\d+)?[A-Za-z]?\s+(.+)$", a)
    if not m:
        return ""
    toks = m.group(2).split(" ")
    last = max((i for i, t in enumerate(toks) if i >= 1 and t.lower().rstrip(".") in STREET_TYPES), default=None)
    if last is not None:
        toks = toks[:last + 1]              # anything after the last street type is a unit or floor
    else:
        cut = next((i for i, t in enumerate(toks) if i >= 1 and UNIT_WORD.match(t)), len(toks))
        toks = toks[:cut]
        while len(toks) > 1 and re.search(r"\d", toks[-1]):
            toks = toks[:-1]
    return f"{m.group(1)} {' '.join(toks)}".strip()


def date_display(iso):
    """A City record's date as an email states it: '2026-10-16' gives 'Oct 16'. '' when unreadable."""
    try:
        d = dt.date.fromisoformat(str(iso)[:10])
    except ValueError:
        return ""
    return f"{MONTHS[d.month - 1]} {d.day}"


def exterior_trades(text):
    t = (text or "").lower()
    return [k for k, rx in EXTERIOR_TRADES.items() if re.search(rx, t)]


def _license_words(lead, low):
    """A license email says 'business license', or 'food license' when the City's license type is a food license."""
    p, food = [], bool(re.search(r"\bfood\b", str(lead.get("license_type") or ""), re.I))
    has_biz, has_food = "business license" in low, "food license" in low
    if not (has_biz or has_food):
        p.append("body does not name the signal ('business license', or 'food license' for a food license type)")
    if has_food and not food:
        p.append(f"body calls a {lead.get('license_type')!r} license a food license")
    return p


def _citation_words(lead, low):
    """A citation email names what the City cited: 'elevator' for the Elevator bureau, the cited exterior repair for a
    Conservation citation, and nothing the City did not cite. It is about an open citation only."""
    p, bureau = [], str(lead.get("bureau") or "").upper()
    if lead.get("open") is not True:
        p.append("the citation is not open in the City's data, and the email treats it as open")
    named = exterior_trades(low)
    if bureau == "ELEVATOR":
        if not ELEVATOR_WORD.search(low):
            p.append("body does not say 'elevator' for an Elevator bureau citation")
        if named:
            p.append(f"body names an exterior repair ({', '.join(named)}) on an elevator citation")
    elif bureau == "CONSERVATION":
        cited = exterior_trades(lead.get("description"))
        if not cited:
            p.append(f"citation description {lead.get('description')!r} is not an exterior repair the gate knows")
        elif not set(named) & set(cited):
            p.append(f"body does not name the cited repair ({', '.join(cited)} words, e.g. 'exterior wall')")
        extra = sorted(set(named) - set(cited))
        if cited and extra:
            p.append(f"body names a repair the City did not cite ({', '.join(extra)})")
        if ELEVATOR_WORD.search(low):
            p.append("body says 'elevator' on an exterior citation")
    else:
        p.append(f"bureau {lead.get('bureau')!r} has no signal words in the gate (ELEVATOR or CONSERVATION)")
    return p


SIGNAL_KINDS = {
    "license": {"schema": "pnf.license_lead.v1", "dataset": "r5kz-chrr", "date_field": "issue_date", "name_field": "business",
                "fields": ("lead_id", "kind", "business", "address", "community_area", "license_type", "issue_date", "dataset",
                           "record_id", "source_url"),
                "words": _license_words,
                "forbid": re.compile(r"\bcit(?:e|ed|es|ing|ation|ations)\b|\bviolations?\b|\belevators?\b", re.I)},
    "citation": {"schema": "pnf.citation_lead.v1", "dataset": "22u3-xenr", "date_field": "citation_date", "name_field": None,
                 "fields": ("lead_id", "kind", "address", "community_area", "bureau", "description", "citation_date", "open",
                            "dataset", "record_id", "source_url"),
                 "words": _citation_words,
                 "forbid": re.compile(r"\b(?:business|food) licen[sc]e[sd]?\b|\bnewly licensed\b", re.I)},
}
# Which signal kinds a product sells and which trades buy it (Todd, Oct 22, 2026, decision 1: licenses for commercial
# cleaning and pest control). pest_control is a signal trade only; the permit TRADE_VERTICALS are unchanged.
SIGNAL_PRODUCTS = {
    "chicago-licenses": {"city": "chicago", "kinds": {"license"}, "trades": {"commercial_cleaning", "pest_control"},
                         "templates": "email/L1-OUTREACH.md"},
}
SIGNAL_OPTIONAL = {"record_id", "source_url", "community_area"}
# Count emails (Todd, Oct 24, 2026, live chat): the licenses list sold to commission sellers, POS and merchant services
# resellers first, then independent commercial insurance agents. The hook is the City's own weekly counts, never a
# business, so these trades never take the L1 templates (validate_signal_drafts rejects them) and their drafts go through
# copy_gate --lic. They send from sales@ only: hello@ is kept for the pest seat.
SALES_SENDER = "sales@getproofnotfluff.com"
COUNT_PRODUCTS = {
    "chicago-licenses": {"city": "chicago", "trades": ("pos_merchant", "commercial_insurance"), "sender": SALES_SENDER,
                         "templates": "email/L2-COMMISSION.md"},
}


def validate_signal_lead(lead):
    """Schema for one signal lead: its kind's fields and no others (business-level only), a clean house-number-and-street
    address, a YYYY-MM-DD date, no email or phone anywhere, and for a license a shown name that could not be a person's."""
    lid = (lead or {}).get("lead_id", "?")
    if not isinstance(lead, dict):
        return ["signal lead: not an object"]
    k = SIGNAL_KINDS.get(lead.get("kind"))
    if k is None:
        return [f"{lid}: unknown signal kind {lead.get('kind')!r} (one of {sorted(SIGNAL_KINDS)})"]
    p = []
    for f in k["fields"]:
        if f not in SIGNAL_OPTIONAL and lead.get(f) in (None, "", []):
            p.append(f"{lid}: missing {f}")
    for f in sorted(set(lead) - set(k["fields"])):
        p.append(f"{lid}: {f} is not a business-level field of a {lead['kind']} lead")
    if lead.get("dataset") and lead.get("dataset") != k["dataset"]:
        p.append(f"{lid}: dataset {lead.get('dataset')!r} is not {k['dataset']}")
    a = str(lead.get("address") or "")
    if a and signal_address(a) != a:
        p.append(f"{lid}: address {a!r} is not house number and street ({signal_address(a)!r}); units and suites stay out")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(lead.get(k["date_field"]) or "")) or not date_display(lead.get(k["date_field"])):
        p.append(f"{lid}: {k['date_field']} not YYYY-MM-DD")
    for f in k["fields"]:
        if isinstance(lead.get(f), str) and f not in ("source_url",) and PERSONAL_TEXT.search(lead[f]):
            p.append(f"{lid}: {f} carries an email or phone number")
    if lead["kind"] == "citation":
        if not isinstance(lead.get("open"), bool):
            p.append(f"{lid}: open must be true or false")
        if str(lead.get("bureau") or "").upper() not in ("ELEVATOR", "CONSERVATION"):
            p.append(f"{lid}: bureau {lead.get('bureau')!r} is not ELEVATOR or CONSERVATION")
    if lead["kind"] == "license" and lead.get("business"):
        try:
            import licenses_chicago as LC   # the product's own person-name rule (planted cases in its selftest)
            if LC.could_be_person(lead["business"]):
                p.append(f"{lid}: business name could be a person's name; it stays out")
        except ImportError:
            p.append(f"{lid}: cannot load tools/licenses_chicago.py to judge the business name")
    return p


def validate_signal_file(doc):
    """A signal lead file: one kind's schema, a list of leads, unique ids, every lead valid."""
    if not isinstance(doc, dict):
        return ["signal file: not a JSON object"]
    kinds = {v["schema"]: k for k, v in SIGNAL_KINDS.items()}
    if doc.get("schema") not in kinds:
        return [f"signal file: schema must be one of {sorted(kinds)}"]
    leads = doc.get("leads")
    if not isinstance(leads, list) or not leads:
        return ["signal file: leads must be a non-empty list"]
    p, ids = [], [x.get("lead_id") for x in leads if isinstance(x, dict)]
    if len(ids) != len(set(ids)):
        p.append("signal file: duplicate lead_id")
    for x in leads:
        p += validate_signal_lead(x)
        if isinstance(x, dict) and x.get("kind") != kinds[doc["schema"]]:
            p.append(f"{x.get('lead_id')}: a {x.get('kind')} lead in a {doc['schema']} file")
    return p


def signal_copy_problems(subject, body, first_name, lead, send_day):
    """The Outreach Copy Gate for one email built on a signal lead (body without the fixed footer). Every rule of
    copy_problems still applies (under 75 words, no link, no pitch, no dash, 'Hi <first>,', the permission question);
    the lead's shown business name is City text, so it is masked only for the pitch and phrase checks ('Discount Tire'
    is a name, not a discount), never for the link or dash checks. Then: the street as street_display gives it, no house
    number, the lead's date exactly as the City record has it ('Oct 16') and no other date, that date inside the last 30
    days on send_day, the signal words of the lead's kind and none of another kind's, and a license email names the
    shown business name."""
    s, b = subject or "", body or ""
    k = SIGNAL_KINDS.get((lead or {}).get("kind"))
    if k is None:
        return [f"unknown signal kind {(lead or {}).get('kind')!r} (one of {sorted(SIGNAL_KINDS)})"]
    p = [f"lead {m}" for m in validate_signal_lead(lead)]
    if not first_name:
        p.append("a signal email needs the named decision-maker's first name")
    name = str(lead.get(k["name_field"]) or "") if k["name_field"] else ""

    def mask(t):
        return re.sub(re.escape(name), lambda m: " ".join(["Name"] * max(1, len(words(m.group(0))))), t, flags=re.I) if name else t
    p += copy_problems(mask(s), mask(b), first_name or None)
    for label, t in (("subject", s), ("body", b)):
        if not any(x.startswith(f"{label} carries a link") for x in p):
            m = URL_RE.search(link_safe(t))
            if m:
                p.append(f"{label} carries a link or domain ({m.group(0)!r})")
    low, both = b.lower(), (s + "\n" + b)
    street = street_display(lead.get("address")).lower()
    if not street or street not in low:
        p.append(f"body does not name the lead's street ({street!r}, as street_display gives it)")
    house = (re.match(r"^\s*(\d+)", str(lead.get("address") or "")) or [None, None])[1]
    rest = re.sub(re.escape(name), " ", both, flags=re.I) if name else both
    if house and re.search(r"(?<![\d$.,])%s(?![\d,%%])" % re.escape(house), rest):
        p.append(f"email gives the house number {house}; the first touch names the street only")
    want = date_display(lead.get(k["date_field"]))
    if want and want not in b:
        p.append(f"body does not state the lead's date as the City record has it ({want!r})")
    for m in DATE_IN_COPY.findall(rest):
        if m != want:
            p.append(f"email states {m!r}, the City record says {want!r}")
    try:
        sent = send_day if isinstance(send_day, dt.date) else dt.date.fromisoformat(str(send_day))
        age = (sent - dt.date.fromisoformat(str(lead.get(k["date_field"]))[:10])).days
        if age < 0:
            p.append(f"the lead's date {want} is after the send day {sent.isoformat()}")
        elif age > SIGNAL_WINDOW_DAYS:
            p.append(f"the lead's date {want} is {age} days before the send day, outside the {SIGNAL_WINDOW_DAYS}-day window")
    except (TypeError, ValueError):
        p.append("no readable send day or lead date to check the 30-day window")
    p += k["words"](lead, re.sub(re.escape(name), " ", low, flags=re.I) if name else low)
    m = k["forbid"].search(re.sub(re.escape(name), " ", both, flags=re.I) if name else both)
    if m:
        p.append(f"email uses {m.group(0)!r}, a word for another signal than a {lead['kind']}")
    if name and name.lower() not in low:
        p.append(f"body does not name the shown business name {name!r}")
    return p


def validate_signal_drafts(doc, leads_by_id, prospects_by_id, send_day, matches_by_prospect=None):
    """Signal drafts (schema pnf.signal_draft.v1, never mixed with permit drafts): one per prospect, its validated match,
    the prospect's own address through the Inbox Gate, a signal product that sells the lead's kind, and the signal copy
    check on send_day."""
    p = []
    rows = doc.get("drafts") if isinstance(doc, dict) else None
    if not isinstance(doc, dict) or doc.get("schema") != "pnf.signal_draft.v1" or not isinstance(rows, list):
        return ["signal draft file: schema must be pnf.signal_draft.v1 with a drafts list"]
    seen = set()
    for d in rows:
        if not isinstance(d, dict):
            p.append("signal draft file: a draft is not an object")
            continue
        pid, lid = d.get("prospect_id"), d.get("lead_id")
        if pid in seen:
            p.append(f"draft {pid}: second draft to the same prospect in one batch")
        seen.add(pid)
        if matches_by_prospect is not None and matches_by_prospect.get(pid) != lid:
            p.append(f"draft {pid}: lead_id differs from the validated match")
        pr, ld = prospects_by_id.get(pid), leads_by_id.get(lid)
        if pr is None or ld is None:
            p.append(f"draft {pid}: prospect or lead not in the validated files")
            continue
        sig = SIGNAL_PRODUCTS.get(pr.get("product"))
        if sig is None:
            p.append(f"draft {pid}: product {pr.get('product')!r} is not a signal product")
            continue
        if ld.get("kind") not in sig["kinds"]:
            p.append(f"draft {pid}: product {pr.get('product')} does not sell {ld.get('kind')!r} leads")
        if trade_of(pr) not in sig["trades"]:
            p.append(f"draft {pid}: trade_vertical {trade_of(pr)} does not serve product {pr.get('product')}")
        if (d.get("to") or "").lower() != str(pr.get("email") or "").lower():
            p.append(f"draft {pid}: to address differs from the prospect's validated email")
        p += [f"draft {pid}: {m}" for m in inbox_problems(d.get("to"), pr.get("website_domain"), pr.get("first_name"), pr.get("last_name"),
                                                          pr.get("owner_source") or "", pr.get("email_source") or "")]
        p += [f"draft {pid}: {m}" for m in signal_copy_problems(d.get("subject"), d.get("body"), pr.get("first_name"), ld, send_day)]
    return p
