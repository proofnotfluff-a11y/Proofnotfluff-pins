#!/usr/bin/env python3
"""The fixed rules of the downstream leads pipeline, as pure functions with no network and no model.

Two entities, never mixed:
  Entity A, GC lead (pnf.gc_lead.v1): a City permit in a downstream completion stage with an adjacent Certificate of
    Occupancy or health inspection signal. Business-level fields only; it is committed to this public repo.
  Entity B, cleaning prospect (pnf.prospect.v1): the named decision-maker at a local commercial cleaning or pressure
    washing business who gets our email. Personal data: it lives in the private CRM and in gitignored data/ files only.

Every validator returns a list of problem strings; an empty list is a pass. The CLIs (tools/validate_leads.py,
tools/copy_gate.py, tools/context_gate.py) turn any problem into exit code 1.
"""
import datetime as dt
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
                   "cleaning", "clean", "customerservice", "operations", "ops", "orders", "schedule", "scheduling")
ROLE_RE = re.compile(r"^(?:%s)(?:[._+-].*|\d+)?$" % "|".join(re.escape(x) for x in ROLE_LOCALPARTS), re.I)
FREEMAIL = {"gmail.com", "googlemail.com", "yahoo.com", "ymail.com", "outlook.com", "hotmail.com", "live.com", "msn.com",
            "icloud.com", "me.com", "mac.com", "aol.com", "comcast.net", "att.net", "sbcglobal.net", "verizon.net",
            "protonmail.com", "proton.me", "gmx.com", "mail.com", "zoho.com", "yandex.com"}
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z'.-]{0,39}(?: [A-Za-z][A-Za-z'.-]{0,39})?$")
DECISION_TITLE = re.compile(r"\b(?:owner|co-?owner|founder|co-?founder|president|ceo|chief|principal|partner|managing|"
                            r"general manager|gm|director|vice president|vp|head of|operations manager|business manager|"
                            r"proprietor|manager)\b", re.I)
OK_EMAIL_STATUS = {"verified", "valid", "deliverable", "catch_all", "accept_all"}
CATCH_ALL = {"catch_all", "accept_all"}
PRODUCTS = {"chicago-construction": "chicago", "austin-construction": "austin", "chicago-restaurant": "chicago"}
SOURCES = {"apollo", "hunter", "clay", "site", "manual"}

# ------------------------------------------------------------------ outreach copy
MAX_WORDS = 75            # a draft fails at 75 words or more
MAX_SUBJECT_WORDS = 9
URL_RE = re.compile(r"https?://|www\.|\.com\b|\.net\b|\.org\b|\.io\b|\.co\b|\.us\b|gumroad|bit\.ly|[a-z0-9-]+\.[a-z]{2,6}/", re.I)
PITCH_RE = re.compile(r"\$\s?\d+\s*(?:/|a|per)\s*(?:mo|month)\b|\bsubscri\w*|\bfree trial\b|\bsign up\b|\bcheckout\b|"
                      r"\bbuy now\b|\bdiscount\b|\bmembership\b|\bpricing\b|\bprice\b", re.I)
DASHES = ("—", "–")
# CAN-SPAM block the sender appends under every first email. It is fixed text, checked byte for byte, and not counted
# against the 75 words because it is compliance, not copy.
FOOTER = ("ProofNotFluff\n680 North Lake Shore Drive, Suite 110-2964, Chicago, IL 60611\n"
          "Not interested? Reply \"no thanks\" and we will not email you again.")


def words(text):
    return re.findall(r"[A-Za-z0-9$][A-Za-z0-9$'.,%-]*", text or "")


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
    if doc.get("schema") != "pnf.gc_lead.v1":
        p.append("gc file: schema must be pnf.gc_lead.v1")
    leads = doc.get("leads")
    if not isinstance(leads, list):
        return p + ["gc file: leads must be a list"]
    ids = [x.get("lead_id") for x in leads]
    if len(ids) != len(set(ids)):
        p.append("gc file: duplicate lead_id")
    for x in leads:
        p += validate_gc_lead(x)
    if max_age_days is not None:
        try:
            at = dt.datetime.fromisoformat(str(doc.get("generatedAt")).replace("Z", "+00:00"))
            now = now or dt.datetime.now(dt.timezone.utc)
            if (now - at).days > max_age_days:
                p.append(f"gc file: generatedAt {doc.get('generatedAt')} is older than {max_age_days} days")
        except ValueError:
            p.append("gc file: generatedAt unreadable")
    return p


# ------------------------------------------------------------------ Entity B
PROSPECT_REQUIRED = ("prospect_id", "product", "business", "website_domain", "city", "first_name", "last_name", "title",
                     "email", "email_source", "email_status")


def inbox_problems(email, website_domain=""):
    """The Inbox Gate for one address: syntax, no role-based local part, no free mail, on the business's own domain."""
    e = (email or "").strip()
    if not EMAIL_RE.match(e):
        return [f"{e or '(blank)'}: not a valid email address"]
    local, dom = e.lower().split("@", 1)
    p = []
    if ROLE_RE.match(local):
        p.append(f"{e}: role-based inbox ({local}@), a named decision-maker is required")
    if dom in FREEMAIL:
        p.append(f"{e}: free-mail domain, a work address on the business's own domain is required")
    wd = domain_of(website_domain)
    if wd and not (dom == wd or dom.endswith("." + wd)):
        p.append(f"{e}: domain {dom} does not match the business website {wd}")
    return p


def validate_prospect(x):
    p, pid = [], x.get("prospect_id", "?")
    for k in PROSPECT_REQUIRED:
        if not str(x.get(k) or "").strip():
            p.append(f"{pid}: missing {k}")
    if x.get("product") not in PRODUCTS:
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
    if x.get("email_status") and x["email_status"] not in OK_EMAIL_STATUS:
        p.append(f"{pid}: email_status {x.get('email_status')!r} is not deliverable")
    if x.get("do_not_email") is True:
        p.append(f"{pid}: do_not_email is set")
    p += [f"{pid}: {m}" for m in inbox_problems(x.get("email"), x.get("website_domain"))]
    return p


def validate_prospect_file(doc):
    p = []
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
    return p


# ------------------------------------------------------------------ the agent's two outputs
def validate_matches(doc, leads_by_id, prospects_by_id):
    p = []
    rows = doc.get("matches") if isinstance(doc, dict) else None
    if doc.get("schema") != "pnf.match.v1" or not isinstance(rows, list):
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
    for label, t in (("subject", s), ("body", b)):
        m = URL_RE.search(t)
        if m:
            p.append(f"{label} carries a link or domain ({m.group(0)!r})")
        for d in DASHES:
            if d in t:
                p.append(f"{label} carries an em or en dash")
        low = t.lower()
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
        if (lead.get("gc_company") or "").lower() not in b.lower():
            p.append(f"body does not name the general contractor {lead.get('gc_company')!r}")
        stage_words = {"Partial Occupancy Approved": "partial occupancy", "Inspections Under Way": "inspection",
                       "Final Inspection Scheduled": "final inspection", "Certificate of Occupancy Pending": "certificate of occupancy"}
        want = stage_words.get(lead.get("stage"), "")
        if want and want not in b.lower():
            p.append(f"body does not state the lead's downstream stage ({want!r})")
    return p


def validate_drafts(doc, leads_by_id, prospects_by_id):
    p = []
    rows = doc.get("drafts") if isinstance(doc, dict) else None
    if doc.get("schema") != "pnf.draft.v1" or not isinstance(rows, list):
        return ["draft file: schema must be pnf.draft.v1 with a drafts list"]
    for d in rows:
        pid, lid = d.get("prospect_id"), d.get("lead_id")
        pr, ld = prospects_by_id.get(pid), leads_by_id.get(lid)
        if pr is None or ld is None:
            p.append(f"draft {pid}: prospect or lead not in the validated files")
            continue
        if (d.get("to") or "").lower() != pr["email"].lower():
            p.append(f"draft {pid}: to address differs from the prospect's validated email")
        p += [f"draft {pid}: {m}" for m in inbox_problems(d.get("to"), pr.get("website_domain"))]
        p += [f"draft {pid}: {m}" for m in copy_problems(d.get("subject"), d.get("body"), pr["first_name"], ld)]
    return p
