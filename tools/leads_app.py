#!/usr/bin/env python3
"""The members' web app for Chicago Construction Cleaning Leads, version 2 (Todd, Oct 17, 2026, 8:00 pm: "make the design
look more slick ... stunning with drill in capability"). The app is the main product; the Excel workbook stays as a
download inside it for people who live in spreadsheets.

Buyers are owners and estimators at Chicago commercial and post-construction cleaning companies, often on a phone
between jobs. Their job: find projects close to finishing, see who the builder is, call that builder's office.

Drill-in: overview, a filtered project list with a map, a project page, a builder page. Hash routes (#/projects?...,
#/project/<permit>, #/builders, #/builder/<key>, #/pitch) so a buyer can bookmark or share a view inside the app; the
browser's back button works. Contacted marks and private notes live in that buyer's browser only (localStorage).

Security is the same as v1 (tools/leads_page.py, whose encrypt() this reuses): the week's list, the builder contacts and
the workbook travel inside one AES-256-GCM box under a key derived with PBKDF2-SHA256 at 250,000 rounds from the
members' password; the page decrypts in the buyer's browser. The repo holds only ciphertext.

Builder contacts: tools/builder_contacts.py contact_for() (verified phone, website and general email read on the
builder's own site). Builders without an entry, and any builder on permits/chicago/builder_do_not_list.json, show a "no contact on file yet" card.
The contacts file is encrypted in the repo (builder_contacts.enc.json); this script hands its password to builder_contacts.

Terms: #/terms shows the City's disclaimer and the Terms of Use paragraphs from tools/leads_xlsx.py terms_text(), the same
list the workbook's Terms tab is built from, so the two cannot drift (Legal desk round 2, Fixes 2 and 3). The footer on
every view, and the gate, link to it.

Map: Leaflet 1.9.4 from cdnjs (exact version, SRI) on OpenStreetMap's standard tiles, desaturated with CSS, with the
OpenStreetMap attribution shown (CARTO's free basemaps are for non-commercial use, so they are not used here).

Usage: LEADS_PASSWORD=... python3 tools/leads_app.py chicago-full.json leads.xlsx docs/chicago-leads-members/index.html
       AUSTIN_LEADS_PASSWORD=... python3 tools/leads_app.py austin-full.json leads.xlsx docs/austin-leads-members/index.html
           (the city comes from the list's source block; tools/leads_cities.py holds what differs by city)
       LEADS_PASSWORD=... python3 tools/leads_app.py --from-review permits/chicago/review.enc.json OUT.html
           (rebuilds the week's list offline from the encrypted review set, for previews and checks)
       python3 tools/leads_app.py --selftest
"""
import base64, collections, datetime as dt, json, os, re, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from leads_page import decrypt, encrypt, pretty_date, FREE_PAGE  # noqa: E402
from leads_xlsx import BUILDER_EMAIL, CAPABILITY_SHEET, CITY_DISCLAIMER, OUR_NOTICE, prep, terms_text  # noqa: E402
from permits_chicago import DATASET, PORTAL, builders, clean_scope, entity_key, entity_names, gc_key, list_day, sleeping_count, unit_count  # noqa: E402
import leads_cities as LC  # noqa: E402  (per-city words; Chicago's are the strings this page shipped with)
import leads_xlsx  # noqa: E402

try:
    from builder_contacts import contact_for, set_password as contacts_password  # noqa: E402
except Exception:  # the contacts file and tool are optional: every builder then shows "no contact on file yet"
    contact_for = contacts_password = None

STAGES = ["Partial occupancy approved", "Inspections under way", "Permit issued"]
LEAFLET_JS = ("https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js", "sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=")
LEAFLET_CSS = ("https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css", "sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=")
RECORD = f"{PORTAL}/resource/{DATASET}.json?permit_="
CITY_TERMS = "https://www.chicago.gov/city/en/narr/foia/data_disclaimer.html"
# the footer on every view and under the gate: the City's disclaimer word for word, then ours (Legal desk round 2, Fixes 2
# and 4). "Terms of Use" becomes the link to #/terms.
CITY = LC.CHICAGO   # the city being built (build_html sets it)
LEGAL = ("Public City of Chicago permit records, as of __ASOF__. This site provides applications using data that has been modified "
         "for use from its original source, www.cityofchicago.org, the official website of the City of Chicago. The City of Chicago "
         "makes no claims as to the content, accuracy, timeliness, or completeness of any of the data provided at this site. The data "
         "provided at this site is subject to change at any time. It is understood that the data provided at this site is being used "
         "at one's own risk. ProofNotFluff is not affiliated with or endorsed by the City of Chicago, and no builder listed has "
         "endorsed or works with ProofNotFluff. Builder contacts come from each builder's own website, not the City. You make your "
         "own calls and emails and are responsible for following the law when you do. Licensed to one business for its own "
         "prospecting; no reselling or republishing. Provided as is, without warranties of any kind, to the extent the law allows, and "
         "ProofNotFluff's total liability for any claim is limited to the amount you paid for the most recent month of your membership. "
         "Made with AI assistance. Read the full Terms of Use (also on the Terms tab of the Excel file).")
TERMS_LINK = "Terms of Use"
EMAIL_OK = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def bkey(name):
    """The builder's key in the app's URLs: the same grouping key the list and the contacts file use, lower case."""
    return entity_key(name or "").lower()


def _url(u):
    u = (u or "").strip()
    return u if re.match(r"^https?://[^\s\"'<>]+$", u) else ""


def contact(name, suffix_free_twins=1):
    """No contacts for a city without a verified contacts file (Austin, Oct 18, 2026): every builder card says so plainly.
    The builder's verified contact entry (phone or email read on their own website), cleaned for the page, or None.
    Only verified entries reach the page; every other builder shows "no contact on file yet". Read at build time, so a
    holdout that moves an entry to fix or no-contact takes it off the page on the next build."""
    if contact_for is None or not CITY.get("contacts"):
        return None
    try:
        c = contact_for(name)
    except Exception:
        return None
    if not c or c.get("status") != "verified":
        return None
    # the contacts file is keyed without the legal suffix: its entry belongs to this builder only when it names the same
    # entity, or when no other builder on the list shares the suffix-free name (PANOPTIC GROUP LLC vs INCORPORATED)
    if entity_key(c.get("name") or "") != entity_key(name) and suffix_free_twins != 1:
        return None
    phone = c.get("phone") or ""
    email = c.get("email") or ""
    return {"status": c.get("status") or "", "phone": phone if re.search(r"\d{3}\D*\d{4}", phone) else "",
            "tel": re.sub(r"[^\d]", "", phone.split(" ext")[0])[-10:] if phone else "",
            "email": email if EMAIL_OK.match(email) else "", "website": _url(c.get("website")),
            "contactPage": _url(c.get("contactPage")), "source": _url(c.get("source")),
            "checkedAt": c.get("checkedAt") or "", "note": (c.get("note") or "").strip().rstrip(";").strip()}


def slim(p):
    st = p.get("stage")
    stages = CITY["stages"]
    out = {"id": str(p.get("permit")), "a": p.get("address") or "", "ca": p.get("communityArea") or "", "t": p.get("type") or "",
            "s": p.get("scope") or "", "sf": p.get("scopeFull") or p.get("scope") or "", "c": round(p.get("cost") or 0),
            "u": p.get("units") or 0, "sl": p.get("sleeping") or 0, "i": p.get("issued") or "", "g": [bkey(g) for g in (p.get("gc") or [])], "gn": list(p.get("gc") or []),
            "st": stages.index(st) if st in stages else 2, "m": p.get("milestone") or "", "cs": p.get("status") or "",
            "n": bool(p.get("new")), "lat": p.get("lat"), "lon": p.get("lon")}
    if CITY["key"] == "austin":   # a project of building permits grouped by master permit
        out.update({"ms": [str(x) for x in (p.get("masters") or [p.get("permit")])], "b": p.get("buildings") or 0, "bf": p.get("buildingsFinal") or 0, "di": p.get("district") or "", "gs": p.get("geo") or "",
                    "pm": [{"n": x.get("n") or "", "i": x.get("issued") or "", "e": x.get("expires") or "", "w": x.get("work") or "",
                            "k": x.get("cls") or "", "u": x.get("units") or 0, "s": x.get("scope") or "",
                            "l": x.get("link") if re.match(r"^https://[\w.-]*austintexas\.gov/", x.get("link") or "") else ""}
                           for x in p.get("permits") or []]})
    return out


def payload(rows, fetched, xlsx_bytes):
    builders, names = {}, entity_names(rows)
    twins = collections.Counter(gc_key(n) for n in names.values())
    for p in rows:
        for g in p.get("gc") or []:
            k = bkey(g)
            if k and k not in builders:
                nm = names[entity_key(g)]
                builders[k] = {"name": nm, "contact": contact(nm, twins[gc_key(nm)])}
    return {"asOf": pretty_date(fetched), "asOfIso": fetched.isoformat(), "projects": [slim(p) for p in rows],
            "builders": builders, "record": CITY["record"], "fileName": f"{CITY['slug']}-{fetched.isoformat()}.xlsx",
            "xlsx": base64.b64encode(xlsx_bytes).decode()}


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def pitch_json():
    return json.dumps({"sheet": CAPABILITY_SHEET, "email": BUILDER_EMAIL})


def legal_text():
    if CITY.get("seatName"):   # an area seat (tools/area_seats.py city_for): Chicago's line with the seat's licence words
        return LEGAL.replace("Licensed to one business for its own prospecting;",
                             f"Licensed to one business, the only seat holder for {CITY['seatName']}, for its own prospecting;")
    return LEGAL if CITY["key"] == "chicago" else CITY["legal"]


def legal_html():
    """The city's legal line, escaped, with "Terms of Use" linking to the in-app Terms view (the last mention: Austin's
    line names the City's Open Data Terms of Use first)."""
    t = legal_text()
    assert t.endswith("Read the full Terms of Use (also on the Terms tab of the Excel file).")
    head, tail = t.rsplit(TERMS_LINK, 1)
    return _esc(head) + f'<a href="#/terms">{TERMS_LINK}</a>' + _esc(tail)


def terms_json(as_of, city_terms=CITY_TERMS):
    """The Terms view's text: the workbook Terms tab's own paragraphs (tools/leads_xlsx.py terms_text), not a copy."""
    t = terms_text(as_of)
    return json.dumps({"version": t[0], "paras": t[1:], "city": leads_xlsx.CITY_DISCLAIMER, "cityTerms": city_terms, "notice": leads_xlsx.OUR_NOTICE},
                      ensure_ascii=False).replace("</", "<\\/")


# The cancellation survey (Todd, Oct 19, 2026): a Google Form in hello@proofnotfluff.com, responses in the Sheet
# "ProofNotFluff cancellation survey (Responses)"; the list question is prefilled per product. Gumroad "Member cancels"
# workflows with the same link are saved and publish once Gumroad allows it ($100 earned and a first payout).
SURVEY_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSdLrer5KtdADyASUCCdF1wY7kYvmVzS4I4ioo3sWpA4hV6Q0g/viewform"
SURVEY_LIST_FIELD = "entry.2001137123"


def survey_url(product):
    """The cancellation survey with the member's list already picked, as an HTML-safe href."""
    import urllib.parse
    return f"{SURVEY_FORM}?usp=pp_url&amp;{SURVEY_LIST_FIELD}=" + urllib.parse.quote_plus(product)


def city_json():
    keys = ("key", "city", "state", "product", "csvPrefix", "storageKey", "center", "zoom", "cityName", "records", "area", "areaLower",
            "areaAll", "areaPlural", "cost", "costLower", "costShort", "costAny", "bNoun", "bWeek", "permit", "permitLower", "types", "stages", "stagesShort",
            "stageLines", "contacts", "termsLabel", "nearEmpty", "midWords", "totalWord", "leaveList", "noGeo", "bil2")
    out = {k: CITY[k] for k in keys}
    out["seatName"] = CITY.get("seatName", "")   # an area seat (tools/area_seats.py): named above the overview headline
    return json.dumps(out, ensure_ascii=False).replace("</", "<\\/")


def use(c):
    """Point the app at one city (tools/leads_cities.py) and the workbook module with it (terms, pitch kit, stages)."""
    global CITY
    CITY = leads_xlsx.use(c)
    return CITY


def _depth(html):
    rel = CITY.get("rel") or "../"
    return html if rel == "../" else html.replace('"../assets/', f'"{rel}assets/').replace("url(../assets/", f"url({rel}assets/").replace('"../privacy/"', f'"{rel}privacy/"')


def build_html(rows, fetched, xlsx_bytes, password, city_terms=None, city=None):
    """The app page for prepared rows (tools/leads_xlsx.py prep: each with a stage and a new flag), the list date and the workbook."""
    if city is not None:
        use(city)
    box = encrypt(password, json.dumps(payload(rows, fetched, xlsx_bytes), separators=(",", ":")).encode())
    as_of = pretty_date(fetched)
    return _depth(PAGE.replace("__BOX__", json.dumps(box)).replace("__TERMS__", terms_json(as_of, city_terms or CITY["termsUrl"]))
            .replace("__HELPLINE__", _esc(CITY.get("helpLine") or "Questions about your membership? Reply to your Gumroad receipt."))
            .replace("__GATEH1__", _esc(CITY.get("gateH1") or f"This week's {CITY['city']} leads"))
            .replace("__RIBBON__", _esc(CITY.get("ribbon") or CITY["product"]))
            .replace("__GATEBUY__", CITY.get("gateBuy") or 'Not a member yet? <a href="__FREE__">Get the full list: $29&nbsp;a&nbsp;month</a>')
            .replace("__CITY__", city_json()).replace("__PRODUCT__", CITY["product"]).replace("__CITYNAME__", CITY["city"])
            .replace("__GATESUB__", _esc(CITY["gateSub"]))
            .replace("__LEGAL__", legal_html()).replace("__ASOF__", as_of)
            .replace("__FREE__", CITY["freePage"]).replace("__PITCH__", pitch_json()).replace("__SURVEY__", survey_url(CITY["product"]))
            .replace("__LJS__", LEAFLET_JS[0]).replace("__LJSI__", LEAFLET_JS[1])
            .replace("__LCSS__", LEAFLET_CSS[0]).replace("__LCSSI__", LEAFLET_CSS[1]))


def build(full, xlsx_path, out, password):
    use(LC.for_source(full["source"]))
    rows = [prep(p) for p in full["projects"]]
    fetched = list_day(full["source"]["fetchedAt"])
    html = build_html(rows, fetched, open(xlsx_path, "rb").read(), password, full["source"].get("terms") or CITY["termsUrl"])
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    d = payload(rows, fetched, b"")
    return {"rows": len(rows), "bytes": len(html), "builders": len(d["builders"]),
            "buildersWithContact": sum(1 for b in d["builders"].values() if b["contact"])}


def projects_from_review(review, fetched):
    """The week's kept projects rebuilt from the review set with the same functions tools/permits_chicago.py main() uses
    (review rows carry only general-contractor names, so no person's name can enter here). fetched is the pull's UTC
    date, the base main() uses for new this week."""
    week = (fetched - dt.timedelta(days=7)).isoformat()
    out = []
    for r in review:
        if not r.get("kept"):
            continue
        desc = (r.get("raw") or "").upper().replace("¿", " ")
        names, types = r.get("gcRaw") or [], r.get("gcType")
        if types and len(types) == len(names):   # main() never lists an owner acting as general contractor
            names = [n for n, t in zip(names, types) if "OWNER" not in (t or "").upper()]
        gcs = builders(names)
        out.append({"permit": r.get("permit"), "issued": r.get("issued") or "",
                    "type": "New construction" if "NEW CONSTRUCTION" in (r.get("type") or "") else "Renovation",
                    "scope": clean_scope(r.get("raw")), "scopeFull": clean_scope(r.get("raw"), limit=1200, whole=True),
                    "units": unit_count(desc, display=True) or None, "sleeping": sleeping_count(desc) or None,
                    "cost": round(r.get("cost") or 0), "address": r.get("address") or "",
                    "communityArea": r.get("communityArea") or "", "status": r.get("status") or "", "milestone": r.get("milestone") or "",
                    "gc": gcs, "lat": r.get("lat"), "lon": r.get("lon"), "newThisWeek": (r.get("issued") or "") >= week})
    out.sort(key=lambda x: (-x["cost"], x["issued"]))
    return out


def from_review(review_path, out, password, sample_path=None):
    import leads_xlsx
    sample = json.load(open(sample_path or os.path.join(ROOT, "permits", "chicago", "sample.json")))
    fetched = dt.datetime.fromisoformat(sample["source"]["fetchedAt"]).astimezone(dt.timezone.utc).date()
    review = json.loads(decrypt(password, json.load(open(review_path))))
    full = {"source": sample["source"], "window": sample["window"], "counts": sample["counts"],
            "projects": projects_from_review(review, fetched)}
    tmp = tempfile.mkdtemp()
    xlsx = os.path.join(tmp, "leads.xlsx")
    leads_xlsx.build(full, xlsx)
    return build(full, xlsx, out, password)


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="color-scheme" content="light">
<meta name="robots" content="noindex, nofollow"><meta name="theme-color" content="#1D2433">
<title>Members: __PRODUCT__ | ProofNotFluff</title>
<link rel="preload" href="../assets/fonts/inter-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../assets/fonts/poppins-700.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="__LCSS__" integrity="__LCSSI__" crossorigin="anonymous">
<script defer src="__LJS__" integrity="__LJSI__" crossorigin="anonymous"></script>
<style>
@font-face{font-family:Inter;font-weight:400;font-display:swap;src:url(../assets/fonts/inter-400.woff2) format("woff2")}
@font-face{font-family:Inter;font-weight:600;font-display:swap;src:url(../assets/fonts/inter-600.woff2) format("woff2")}
@font-face{font-family:Inter;font-weight:700;font-display:swap;src:url(../assets/fonts/inter-700.woff2) format("woff2")}
@font-face{font-family:Poppins;font-weight:600;font-display:swap;src:url(../assets/fonts/poppins-600.woff2) format("woff2")}
@font-face{font-family:Poppins;font-weight:700;font-display:swap;src:url(../assets/fonts/poppins-700.woff2) format("woff2")}
:root{--paper:#F5F2EC;--paper2:#EDE8DF;--ink:#1D2433;--ink2:#3A4152;--muted:#565D6F;--line:#E2DDD3;--line2:#EFEBE4;--card:#fff;
--accent:#C8502F;--accent-ink:#A63E21;--teal:#2E6B66;--teal-bg:#E3EFED;--blue:#2F5F9E;--blue-bg:#E6EDF6;--iss:#3A4152;--iss-bg:#ECE6DA;
--focus:0 0 0 3px rgba(47,95,158,.45);--sh:0 1px 2px rgba(29,36,51,.05),0 6px 20px rgba(29,36,51,.06);--r:12px;
--head:Poppins,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;--body:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
--bar-h:60px;--nav-h:64px;--field:#8F887C}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scrollbar-color:#C9C2B5 var(--paper)}
body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 var(--body);font-feature-settings:"cv11","ss01";-webkit-font-smoothing:antialiased}
::selection{background:#F3D9CF;color:var(--ink)}
h1,h2,h3{font-family:var(--head);letter-spacing:-.015em;line-height:1.15;margin:0;text-wrap:balance}
a{color:var(--blue);text-underline-offset:3px;text-decoration-thickness:1px}
button,input,select,textarea{font:inherit;color:inherit}
:focus-visible{outline:none;box-shadow:var(--focus);border-radius:8px}
h1[tabindex="-1"]:focus,h1[tabindex="-1"]:focus-visible{outline:none;box-shadow:none}
.seatchip{display:inline-flex;align-items:center;gap:6px;margin:0 0 10px;padding:5px 12px;border-radius:999px;background:var(--teal-tint,#e2efec);color:var(--teal-ink,#1e4c48);font-weight:700;font-size:14px}
.num{font-variant-numeric:tabular-nums}
.skip{position:absolute;left:12px;top:-60px;z-index:2000;background:#fff;color:var(--ink);padding:12px 14px;min-height:44px;border-radius:8px;font-weight:600;box-shadow:var(--sh)}
.skip:focus{top:10px}
.sr{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
[hidden]{display:none!important}
.ico{width:20px;height:20px;flex:none;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.ico.s{width:16px;height:16px}
/* app bar */
.bar{position:sticky;top:0;z-index:900;background:var(--ink);color:#fff;height:var(--bar-h)}
.bar-in{max-width:1320px;margin:0 auto;height:100%;padding:0 16px;display:flex;align-items:center;gap:20px}
.brand{display:flex;flex-direction:column;justify-content:center;gap:5px;min-height:44px;text-decoration:none;color:#fff;min-width:0}
.brand b{font:700 16px/1 var(--head);letter-spacing:-.01em;white-space:nowrap}
.brand small{font-size:12.5px;line-height:1;color:#B9C0CE;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.marks{display:flex;gap:3px}.marks i{width:14px;height:3px;border-radius:2px}
.marks i:nth-child(1){background:#C8502F}.marks i:nth-child(2){background:#2E6B66}.marks i:nth-child(3){background:#6B4FA0}.marks i:nth-child(4){background:#2F5F9E}.marks i:nth-child(5){background:#A87C1F}
.tabs{display:flex;gap:4px;margin-left:12px}
.tabs a{display:flex;align-items:center;gap:8px;height:40px;padding:0 14px;border-radius:8px;color:#C9CFDB;text-decoration:none;font-weight:600;font-size:14.5px}
.tabs a:hover{color:#fff;background:rgba(255,255,255,.07)}
.tabs a[aria-current=page]{color:#fff;background:rgba(255,255,255,.12)}
.bar-sp{flex:1}
.bar .dl{display:inline-flex;align-items:center;gap:8px;height:40px;padding:0 14px;border-radius:8px;border:1px solid rgba(255,255,255,.22);background:transparent;color:#fff;font-weight:600;font-size:14px;cursor:pointer;white-space:nowrap}
.bar .dl:hover{background:rgba(255,255,255,.08)}
.bar .dl .ico{width:18px;height:18px}
.bar .dl .sh{display:none}
@media(max-width:860px){.tabs{display:none}.bar .dl .lg{display:none}.bar .dl .sh{display:inline}.bar .dl{height:44px;padding:0 12px;gap:6px}}
/* bottom nav (phone) */
.bnav{display:none}
@media(max-width:860px){
 .bnav{display:grid;grid-template-columns:repeat(4,1fr);position:fixed;left:0;right:0;bottom:0;z-index:900;background:#fff;border-top:1px solid var(--line);padding:4px 4px calc(4px + env(safe-area-inset-bottom));box-shadow:0 -6px 20px rgba(29,36,51,.06)}
 .bnav a{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;height:54px;border-radius:10px;color:var(--muted);text-decoration:none;font-size:12px;font-weight:600}
 .bnav a[aria-current=page]{color:var(--ink)}
 .bnav a[aria-current=page] .ico{color:var(--accent)}
 body.in{padding-bottom:calc(var(--nav-h) + env(safe-area-inset-bottom))}
}
/* layout */
.page{max-width:1320px;margin:0 auto;padding:28px 16px 48px}
@media(max-width:860px){.page{padding:20px 16px 36px}}
.ph{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;flex-wrap:wrap;margin:0 0 20px}
.ph h1{font-size:30px;font-weight:700}
.ph p{margin:6px 0 0;color:var(--muted);font-size:15px;max-width:680px;text-wrap:pretty}
@media(max-width:600px){.ph h1{font-size:24px}}
.panel{min-width:0;background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh)}
.sec-h{display:flex;align-items:baseline;justify-content:space-between;gap:12px;padding:18px 20px 12px}
.sec-h h2{font-size:18px;font-weight:600}
@media(max-width:600px){.sec-h{padding:16px 16px 10px}.sec-h h2{font-size:17px}.pg-main .sec-h{padding-left:20px;padding-right:20px}.grp{padding:10px 16px}}
.sec-h a{display:inline-flex;align-items:center;min-height:44px;margin:-12px 0;font-size:14px;font-weight:600;white-space:nowrap}
.sec-h .c{color:var(--muted);font:600 14px var(--body);margin-left:8px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 16px;border-radius:10px;border:1px solid var(--line);background:#fff;color:var(--ink);font-weight:600;font-size:14.5px;cursor:pointer;text-decoration:none;white-space:nowrap}
.btn:hover{background:#FAF8F4;border-color:#D6D0C4}
.btn.pri{background:var(--accent);border-color:var(--accent);color:#fff}.btn.pri:hover{background:var(--accent-ink);border-color:var(--accent-ink)}
.btn.ink{background:var(--ink);border-color:var(--ink);color:#fff}.btn.ink:hover{background:#2A3245}
.btn.sm{min-height:36px;padding:0 12px;font-size:13.5px;border-radius:8px}
.btn.on{background:var(--teal-bg);border-color:#B9D6D1;color:var(--teal)}
.lnk{background:none;border:0;padding:0;color:var(--blue);font-weight:600;cursor:pointer;text-decoration:underline;text-underline-offset:3px}
/* chips and the finish pips */
.chip{display:inline-flex;align-items:center;gap:7px;height:26px;padding:0 10px 0 8px;border-radius:999px;font-size:12.5px;font-weight:700;white-space:nowrap;line-height:1}
.chip.s0{color:var(--teal);background:var(--teal-bg)}.chip.s1{color:var(--blue);background:var(--blue-bg)}.chip.s2{color:var(--iss);background:var(--iss-bg)}
.pips{display:inline-flex;gap:2px}.pips i{width:6px;height:6px;border-radius:50%;border:1.5px solid currentColor}
.pips i.f{background:currentColor}
.badge{display:inline-flex;align-items:center;height:22px;padding:0 8px;border-radius:6px;font-size:12px;font-weight:700;background:var(--ink);color:#fff}
.badge.new{background:var(--accent);color:#fff}
.badge.done{background:#fff;color:var(--teal);border:1px solid #B9D6D1;gap:4px}
/* gate */
.gate{min-height:calc(100vh - var(--bar-h));display:grid;place-items:center;padding:32px 16px}
.gate-card{width:100%;max-width:460px;background:#fff;border:1px solid var(--line);border-radius:16px;box-shadow:var(--sh);padding:28px}
.gate-card h1{font-size:26px;font-weight:700;margin:14px 0 6px}
.gate-card p.sub{margin:0 0 20px;color:var(--muted)}
.gate label{display:block;font-weight:600;font-size:14.5px;margin:0 0 8px}
.pw{position:relative}
.pw input{width:100%;height:50px;font-size:16px;padding:0 52px 0 14px;border:1px solid var(--field);border-radius:10px;background:#fff}
.pw input:focus{outline:none;border-color:var(--blue);box-shadow:var(--focus)}
.pw input[aria-invalid=true]{border:2px solid var(--accent)}.pw input[aria-invalid=true]:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(200,80,47,.2)}
.eye{position:absolute;right:3px;top:3px;width:44px;height:44px;border:0;background:transparent;border-radius:8px;color:var(--muted);cursor:pointer;display:grid;place-items:center}
.eye:hover{background:#F3F1EC}
.gate .btn.pri{width:100%;height:50px;margin-top:12px;font-size:16px}
.err{color:var(--accent-ink);font-weight:600;font-size:14.5px;margin:12px 0 0;min-height:1px}
.err:empty{margin:0}
.gate-help{margin:20px 0 0;padding:16px 0 0;border-top:1px solid var(--line2);font-size:14px;color:var(--muted)}
.gate-help p{margin:0 0 8px}
@media(max-width:600px){.gate{place-items:start center;padding:24px 16px 32px;min-height:0}.gate-card{padding:22px}}
.gate-legal{max-width:720px;margin:0 auto;padding:0 16px 40px;font-size:12.5px;line-height:1.6;color:var(--muted)}
/* overview */
.ov{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(0,1fr);gap:20px;align-items:start}
@media(max-width:1020px){.ov{grid-template-columns:minmax(0,1fr)}}
.ov-col{display:grid;grid-template-columns:minmax(0,1fr);gap:20px;min-width:0}
.nb{display:flex;align-items:center;justify-content:space-between;gap:12px 16px;flex-wrap:wrap;padding:16px 20px}.nb p{margin:0;color:var(--ink2);font-size:15px;flex:1 1 260px}.nb b{color:var(--ink)}
.stn.z .n{color:var(--muted)}
.hero h1{font-size:34px;font-weight:700}
.hero p{margin:8px 0 0;color:var(--muted);font-size:16px;max-width:60ch}
@media(max-width:600px){.hero h1{font-size:26px}.hero p{font-size:15px}}
/* the finish line: the signature */
.line{position:relative;display:grid;grid-template-columns:repeat(3,minmax(0,1fr)) auto;gap:0;margin:22px 0 28px;padding:0}
.line::before{content:"";position:absolute;left:24px;right:96px;top:23px;height:2px;background:repeating-linear-gradient(90deg,#C9C2B5 0 8px,transparent 8px 14px)}
.stn{position:relative;display:block;text-decoration:none;color:var(--ink);padding:0 16px 0 0;min-width:0}
.stn .dot{position:relative;z-index:1;display:grid;place-items:center;width:48px;height:48px;border-radius:50%;background:#fff;border:2px solid var(--iss);color:var(--iss)}
.stn.s1 .dot{border-color:var(--blue);color:var(--blue)}
.stn.s0 .dot{border-color:var(--teal);background:var(--teal);color:#fff;box-shadow:0 0 0 6px var(--teal-bg)}
.stn .n{display:block;font:700 40px/1 var(--head);letter-spacing:-.02em;margin:16px 0 8px}
.stn.s0 .n{color:var(--teal)}
.stn .t{display:block;font-weight:600;font-size:15px}
.stn .m{display:block;color:var(--muted);font-size:13.5px;margin-top:2px}
@media(hover:hover){a.stn:hover .t{text-decoration:underline;text-underline-offset:3px}}
.flag{position:relative;z-index:1;display:flex;flex-direction:column;align-items:flex-start;color:var(--ink);width:120px}
.flag .t{display:block;font-weight:600;font-size:15px;margin-top:16px}.flag .m{display:block;color:var(--muted);font-size:13.5px;margin-top:2px}
.flag .dot{display:grid;place-items:center;width:48px;height:48px;border-radius:12px;background:var(--accent);color:#fff}
@media(max-width:700px){
 .line{grid-template-columns:minmax(0,1fr);gap:0;margin:18px 0 22px}
 .line::before{left:23px;right:auto;top:24px;bottom:40px;width:2px;height:auto;background:repeating-linear-gradient(180deg,#C9C2B5 0 8px,transparent 8px 14px)}
 .stn{display:grid;grid-template-columns:48px minmax(0,1fr) auto;column-gap:14px;align-items:center;padding:0 0 14px}
 .stn .n{grid-column:3;grid-row:1;margin:0;font-size:26px;text-align:right}
 .stn .tx{grid-column:2;grid-row:1}
 .flag{display:grid;grid-template-columns:48px minmax(0,1fr);column-gap:14px;align-items:center;width:auto}.flag .t{margin:0}.flag .tx{grid-column:2}
}
.list-rows{list-style:none;margin:0;padding:0}
.row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:4px 16px;padding:14px 48px 14px 20px;border-top:1px solid var(--line2);text-decoration:none;color:inherit;position:relative}
.row,.mini-b,.bars a,.stn{-webkit-tap-highlight-color:transparent}
@media(hover:hover) and (pointer:fine){.row:hover{background:#FBFAF7}}
.row:focus-visible{box-shadow:inset 0 0 0 3px rgba(47,95,158,.45);border-radius:0}
.row .mn{font:700 19px/1.2 var(--head);letter-spacing:-.01em;color:var(--ink)}
.row .mn small{font:500 13px var(--body);color:var(--muted);margin-left:8px;letter-spacing:0}
.row .ad{font-weight:600;font-size:15px;color:var(--ink);overflow-wrap:anywhere}
.row .ar{color:var(--muted);font-weight:400}
.row .bd{display:flex;align-items:center;gap:6px;font-size:14px;color:var(--ink2);min-width:0}
.row .bd span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.row .bd .ico{color:var(--teal)}
.row .rt{grid-column:2;grid-row:1 / span 3;display:flex;flex-wrap:wrap;justify-content:flex-end;align-content:flex-start;align-items:center;gap:6px;max-width:300px}
.row .chev{position:absolute;right:16px;top:50%;transform:translateY(-50%);color:var(--field)}
.row .nc{color:var(--muted);font-size:13px;white-space:nowrap}
.row .bd{flex-wrap:wrap;row-gap:2px}.row .bd>span:not(.nc){white-space:normal;overflow:visible}
.mine .btn{white-space:normal;text-align:center;height:auto;min-height:44px;padding-top:10px;padding-bottom:10px;max-width:100%}
.minimap:empty{height:auto}
.minimap:empty::after{content:"The map did not load on this connection. The address is above.";display:flex;align-items:center;justify-content:center;gap:8px;min-height:72px;padding:16px 20px 16px 48px;text-align:center;color:var(--muted);font-size:14px;background:no-repeat 20px 50%/18px url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236B7180' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z'/%3E%3Ccircle cx='12' cy='10' r='2.5'/%3E%3C/svg%3E")}
.row .bd{align-items:baseline}.row .bd .ico{align-self:center}
.row.hl{background:#F6F3EC}
.grp{display:flex;align-items:baseline;gap:8px;margin:0;padding:10px 20px;border-top:1px solid var(--line2);background:#FAF8F4;font:600 13px var(--body);color:var(--ink2);letter-spacing:0}
.grp .c{color:var(--muted)}
.grp+.list-rows .row{border-top:1px solid var(--line2)}
.row-more{padding:14px 20px;border-top:1px solid var(--line2);display:flex;gap:12px;align-items:center;flex-wrap:wrap;color:var(--muted);font-size:14px}
@media(max-width:600px){.row{grid-template-columns:minmax(0,1fr);padding:14px 16px;gap:3px}.row .rt{grid-column:1;grid-row:auto;order:-1;justify-content:flex-start;max-width:none;margin:0 0 4px}.row .rt:empty{display:none}.row .chev{display:none}}
.mini-b{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:2px 12px;padding:12px 20px;border-top:1px solid var(--line2);text-decoration:none;color:inherit}
@media(hover:hover) and (pointer:fine){.mini-b:hover{background:#FBFAF7}}
.mini-b b{font-weight:600;font-size:14.5px;color:var(--ink);overflow-wrap:anywhere}
.mini-b span{font-size:13.5px;color:var(--muted)}
.mini-b .r{grid-column:2;grid-row:1 / span 2;text-align:right;font:600 14.5px var(--body);color:var(--ink);white-space:nowrap;min-width:5.5em}
.mini-b .r small{font:inherit;color:var(--muted);margin-left:5px}
.bars{list-style:none;margin:0;padding:4px 20px 18px}
.bars li{margin:0}
.bars a{display:grid;grid-template-columns:minmax(0,9rem) minmax(0,1fr) 2.6rem 2.6rem;align-items:center;gap:12px;min-height:40px;padding:4px 0;text-decoration:none;color:var(--ink);font-size:14px;border-radius:6px}
.bars a span:first-child{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bars a:hover span:first-child{text-decoration:underline;text-underline-offset:3px}
.bars .tr{display:flex;gap:2px;height:12px;min-width:3px}
.bars .tr i,.blg i{display:block;height:12px;border-radius:2px;min-width:3px;flex-basis:0;flex-shrink:0}
.b0{background:var(--teal)}.b1{background:var(--blue)}.b2{background:#7E91B0}
.bars .tr i:last-child{border-radius:2px 4px 4px 2px}
.blg{display:flex;flex-wrap:wrap;gap:6px 16px;margin:0;padding:0 20px 6px;font-size:12.5px;color:var(--muted)}
.blg span{display:inline-flex;align-items:center;gap:6px}.blg i{width:12px;flex:none}
.bars .v{text-align:right;font-weight:600}.bars .nv{text-align:right;font-weight:700;color:var(--teal)}.bars .nv.z{color:var(--muted);font-weight:400}
.bars .hd{display:grid;grid-template-columns:minmax(0,9rem) minmax(0,1fr) 2.6rem 2.6rem;gap:12px;font-size:12px;color:var(--muted);padding:0 0 2px}.bars .hd span{text-align:right}
@media(hover:hover) and (pointer:fine){.bars a:hover{background:#FBFAF7}}
@media(max-width:600px){.bars{padding:4px 16px 16px}.bars a,.bars .hd{grid-template-columns:minmax(0,1fr) 3.4rem 2.6rem;gap:6px 10px;min-height:44px}.bars .tr{grid-column:1 / -1;grid-row:2;height:8px}.bars .hd .sp2{display:none}.bars .tr i{height:8px}.blg{padding:0 16px 6px}}
.mine{padding:0 20px 20px;color:var(--muted);font-size:13.5px}
.mine p{margin:0 0 10px}.mine .mh{color:var(--ink2);font-size:14.5px}.mine .mh b{color:var(--ink)}.mine .mh b.blk{display:block;margin:0 0 2px}
.mine .btn{margin-top:4px}
/* projects */
.tool{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:0 0 12px}
.search{position:relative;flex:1 1 280px;min-width:0;max-width:420px}
.search .ico{position:absolute;left:12px;top:12px;color:var(--muted)}
.search input{width:100%;height:44px;padding:0 40px 0 40px;border:1px solid var(--field);border-radius:10px;background:#fff;font-size:15px}
.search input:focus{outline:none;border-color:var(--blue);box-shadow:var(--focus)}
.search input::-webkit-search-cancel-button{-webkit-appearance:none;display:none}
.search .clr{position:absolute;right:2px;top:2px;width:40px;height:40px;border:0;background:none;border-radius:8px;color:var(--muted);cursor:pointer;display:grid;place-items:center}
.seg{display:inline-flex;background:#fff;border:1px solid var(--field);border-radius:10px;padding:3px;gap:2px;max-width:100%;overflow-x:auto;scrollbar-width:none}
.seg::-webkit-scrollbar{display:none}
.seg button{display:inline-flex;align-items:center;gap:7px;height:36px;padding:0 12px;border:0;border-radius:7px;background:none;color:var(--ink2);font-weight:600;font-size:14px;cursor:pointer;white-space:nowrap}
.seg button .c{color:var(--muted);font-weight:600}
.seg button[aria-pressed=true]{background:var(--ink);color:#fff}.seg button[aria-pressed=true] .c{color:#C9CFDB}
.seg button:hover:not([aria-pressed=true]){background:#F5F2EC}
.filters{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;align-items:end}
.filters .fld select{width:100%;max-width:none}.filters .tog{width:100%}
@media(max-width:1100px){.filters{grid-template-columns:repeat(3,minmax(0,1fr))}}
.fld label{display:block;font-size:12.5px;font-weight:600;color:var(--muted);margin:0 0 4px}
.fld select{appearance:none;-webkit-appearance:none;height:40px;min-width:0;max-width:215px;padding:0 34px 0 12px;border:1px solid var(--field);border-radius:10px;background:#fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1.5l5 5 5-5' fill='none' stroke='%231d2433' stroke-width='1.8' stroke-linecap='round'/%3E%3C/svg%3E") no-repeat right 12px center;font-size:14px;font-weight:600;cursor:pointer}
.fld select:focus{outline:none;box-shadow:var(--focus);border-color:var(--blue)}
.tog{display:inline-flex;align-items:center;gap:8px;height:40px;padding:0 12px;border:1px solid var(--field);border-radius:10px;background:#fff;font-size:14px;font-weight:600;cursor:pointer;user-select:none}
.tog input{width:18px;height:18px;margin:0;accent-color:var(--teal)}
.tog:has(input:focus-visible){box-shadow:var(--focus)}
.fbtn{display:none}
.rbar{display:flex;align-items:center;gap:10px 14px;flex-wrap:wrap;margin:16px 0 12px;font-size:14px;color:var(--muted)}
.rbar b{color:var(--ink)}
.rbar .sp{flex:1}
.vtog{display:none}
.tsp{flex:1}
#csv .m{display:none}
.fcount{display:inline-grid;place-items:center;min-width:20px;height:20px;padding:0 6px;border-radius:999px;background:var(--ink);color:#fff;font-size:12px;margin-left:2px}
.split{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,.9fr);gap:16px;align-items:start}
.split .panel.lst{min-width:0;overflow:hidden}
.split .panel.lst .list-rows .row:first-child{border-top:0}
.mapbox{position:sticky;top:calc(var(--bar-h) + 16px);height:calc(100vh - var(--bar-h) - 32px);min-height:420px;border-radius:var(--r);overflow:hidden;border:1px solid var(--line);box-shadow:var(--sh);background:#E9E6E0}
.mapbox .map{position:absolute;inset:0}
.legend{position:absolute;z-index:500;right:12px;top:12px;background:rgba(255,255,255,.96);border:1px solid var(--line);border-radius:10px;padding:8px 12px;font-size:12.5px;font-weight:600;color:var(--ink2);display:grid;gap:4px;box-shadow:0 2px 8px rgba(29,36,51,.08)}
.legend span{display:flex;align-items:center;gap:8px}
.legend i{display:inline-block;border-radius:50%}
.lg0{width:14px;height:14px;background:var(--teal);box-shadow:0 0 0 2px #fff,0 0 0 4px #1F4E4A}
.lg1{width:10px;height:10px;background:var(--blue);margin:0 2px}
.lg2{width:10px;height:10px;background:#fff;border:2px solid var(--iss);margin:0 2px}
.map-note{position:absolute;z-index:500;left:12px;bottom:12px;max-width:calc(100% - 140px);background:rgba(255,255,255,.96);border:1px solid var(--line);border-radius:8px;padding:6px 10px;font-size:12.5px;color:var(--muted)}
.map-fail{position:absolute;inset:0;display:grid;place-items:center;padding:24px;text-align:center;color:var(--muted);font-size:14px}
.split.nomap{display:flex;flex-direction:column-reverse;align-items:stretch;gap:12px}.split.nomap .mapbox{position:static;height:auto;min-height:0;display:block!important}.split.nomap .mapbox .map,.split.nomap .legend{display:none}.split.nomap .map-fail{position:static;display:flex;gap:8px;justify-content:center;padding:14px 20px}.split.nomap .map-fail p{margin:0}
.leaflet-container{font-family:var(--body);background:#E9E6E0}
.leaflet-tile-pane{filter:grayscale(1) sepia(.18) contrast(.88) brightness(1.06)}
.leaflet-control-attribution{font-size:11px;background:rgba(255,255,255,.9)!important}
.leaflet-control-attribution a{color:var(--blue)}
.leaflet-bar a{width:36px!important;height:36px!important;line-height:36px!important;color:var(--ink)!important}
.leaflet-popup-content-wrapper{border-radius:12px;box-shadow:0 8px 24px rgba(29,36,51,.18)}
.leaflet-popup-content{margin:14px 16px;font-size:14px;line-height:1.45;min-width:200px}
.pop .mn{font:700 18px var(--head);display:block}
.pop .ad{font-weight:600;display:block;margin:4px 0 2px}
.pop .bd{color:var(--muted);display:block;margin:0 0 10px}
.pop .btn{min-height:40px;width:100%;color:#fff}
.empty{padding:32px 20px;text-align:center;color:var(--muted)}
.empty h3{font:600 17px var(--head);color:var(--ink);margin:0 0 6px}
.empty .btn{margin-top:12px}
@media(max-width:860px){
 .seg button{height:44px}.btn.sm{min-height:44px}.bars a{min-height:44px}.fld select{height:44px}.tog{height:44px}
 .leaflet-bar a{width:44px!important;height:44px!important;line-height:44px!important}
 #fclose{width:44px;height:44px;padding:0}
 .legend{font-size:12px;padding:6px 10px;gap:2px}
 .split{display:block}
 .split[data-v=list] .mapbox{display:none}
 .split[data-v=map] .panel.lst{display:none}
 .mapbox{position:relative;top:0;height:calc(100vh - var(--bar-h) - var(--nav-h) - 128px);height:calc(100svh - var(--bar-h) - var(--nav-h) - 128px);min-height:360px}
 #csv .t{display:none}#csv .m{display:inline}#csv{min-height:44px;padding:0 12px}
 .tool{gap:8px}.tsp{display:none}.vtog{margin-left:auto}
 .tool .fbtn{padding:0 12px}
 .tool .vtog{flex:1;margin-left:0;padding:2px;height:44px}.tool .vtog button{flex:1;justify-content:center;height:38px;padding:0 8px}
 .btool{display:grid;grid-template-columns:1fr 1fr}.btool .search{grid-column:1 / -1}.btool .fld select{width:100%;max-width:none}.btool .tog{width:100%}
 .vtog{display:inline-flex}
 .tool .seg:not(.vtog){display:flex;flex-wrap:wrap;gap:8px;width:100%;margin:0;padding:0;background:none;border:0;border-radius:0;overflow:visible}
 .tool .seg:not(.vtog) button{flex:none;height:44px;padding:0 14px;border:1px solid var(--field);border-radius:999px;background:#fff}
 .tool .seg:not(.vtog) button[data-k=""]{order:1}
 .c-austin .tool .seg:not(.vtog) button[data-k=""]{order:0}
 .tool .seg:not(.vtog) button[aria-pressed=true]{background:var(--ink);border-color:var(--ink)}
 .rbar{gap:8px 12px}
 .search{max-width:none;flex-basis:100%}
 .fbtn{display:inline-flex}
 .filters{display:flex;position:fixed;z-index:1000;left:0;right:0;bottom:0;max-height:85vh;overflow:auto;background:#fff;border-radius:18px 18px 0 0;padding:8px 16px calc(16px + env(safe-area-inset-bottom));box-shadow:0 -10px 40px rgba(29,36,51,.25);flex-direction:column;align-items:stretch;flex-wrap:nowrap;gap:14px;transform:translateY(105%);transition:transform .28s cubic-bezier(.2,.8,.2,1);visibility:hidden}
 .filters.open{transform:none;visibility:visible}
 .filters .fld select{width:100%;max-width:none;height:48px;font-size:16px}
 .tog{height:48px;font-size:15px}
 .sheet-h{display:flex!important;align-items:center;justify-content:space-between;padding:8px 0 0}
 .sheet-h h2{font-size:18px}
 .sheet-f{display:flex!important;gap:10px;position:sticky;bottom:calc(-16px - env(safe-area-inset-bottom));background:#fff;padding:10px 0 4px}
 .sheet-f .btn{flex:1;min-height:48px}
 .scrim{position:fixed;inset:0;z-index:990;background:rgba(29,36,51,.4)}
}
.sheet-h,.sheet-f{display:none}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important;scroll-behavior:auto!important}}
/* project page */
.back{display:inline-flex;align-items:center;gap:6px;min-height:44px;padding:0 12px 0 6px;margin:-8px 0 8px -6px;border:0;background:none;color:var(--ink2);font-weight:600;font-size:14.5px;cursor:pointer;border-radius:8px;text-decoration:none}
.back:hover{background:var(--paper2)}
.pg{display:grid;grid-template-columns:minmax(0,1fr) 380px;grid-template-rows:auto 1fr;gap:20px;align-items:start}
.pg-head{grid-column:1;grid-row:1;min-width:0}.pg-main{grid-column:1;grid-row:2}.pg-side{grid-column:2;grid-row:1 / span 2;align-self:start}
@media(max-width:1020px){.pg{grid-template-columns:minmax(0,1fr)}.pg-head,.pg-main,.pg-side{grid-column:1;grid-row:auto}}
.pg-main,.pg-side{display:grid;gap:20px;min-width:0}
.pg-side{position:sticky;top:calc(var(--bar-h) + 16px)}
@media(max-width:1020px){.pg-side{position:static}}
.ph-chips{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 12px}
.p-title h1{font-size:32px;font-weight:700;overflow-wrap:anywhere}
.p-title .sub{margin:6px 0 0;color:var(--muted);font-size:15.5px}
.p-money{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin:18px 0 0}
.p-money b{font:700 40px/1 var(--head);letter-spacing:-.02em}
.p-money span{color:var(--muted);font-size:14.5px}
@media(max-width:600px){.p-title h1{font-size:25px}.p-money b{font-size:34px}}
.acts{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0 0}
.track{padding:20px}
.track h2{font-size:17px;font-weight:600;margin:0 0 18px}
.steps{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));position:relative}
.steps li{position:relative;padding:0 10px 0 0;font-size:13.5px;color:var(--muted)}
.steps li::before{content:"";position:absolute;left:14px;right:-14px;top:13px;height:2px;background:var(--line)}
.steps li:last-child::before{display:none}
.steps li.done::before{background:var(--ink2)}
.steps .k{position:relative;z-index:1;display:grid;place-items:center;width:28px;height:28px;border-radius:50%;background:#fff;border:2px solid var(--line);margin:0 0 10px;color:#fff}
.steps li.done .k{background:var(--ink2);border-color:var(--ink2)}
.steps li.now .k{border-color:var(--sc);background:var(--sc);box-shadow:0 0 0 5px var(--sb)}
.steps li.now.s0{--sc:var(--teal);--sb:var(--teal-bg);color:var(--teal)}.steps li.now.s1{--sc:var(--blue);--sb:var(--blue-bg);color:var(--blue)}.steps li.now.s2{--sc:var(--iss);--sb:var(--iss-bg);color:var(--iss)}
.steps li.now b{color:inherit}
.steps li.fin .k{border-radius:8px;border-color:var(--accent);color:var(--accent)}
.steps b{display:block;color:var(--ink);font-size:14px;font-weight:600;margin:0 0 2px}
.ms{margin:18px 0 0;padding:12px 14px;border-radius:10px;background:var(--paper);font-size:14px;color:var(--ink2)}
.ms b{color:var(--ink)}
@media(max-width:600px){
 .steps{grid-template-columns:minmax(0,1fr);gap:0}
 .steps li{display:grid;grid-template-columns:28px minmax(0,1fr);column-gap:14px;padding:0 0 18px}
 .steps li::before{left:13px;right:auto;top:28px;bottom:-0px;width:2px;height:auto}
 .steps .k{margin:0;grid-row:1 / span 2}
}
.facts{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0;margin:0;padding:0}
.facts div{padding:14px 20px;border-top:1px solid var(--line2);min-width:0}
.facts dt{font-size:12.5px;color:var(--muted);font-weight:600;margin:0 0 3px}
.facts dd{margin:0;font-weight:600;font-size:15px;overflow-wrap:anywhere}
@media(max-width:700px){.facts{grid-template-columns:repeat(2,minmax(0,1fr))}}
.scope{padding:0 20px 20px;font-size:15.5px;line-height:1.6;color:var(--ink2);margin:0;text-wrap:pretty}
.rec{padding:0 20px 18px;font-size:14px;color:var(--muted)}
.bps{list-style:none;margin:0 0 14px;padding:0;border-top:1px solid var(--line2)}
.bps li{padding:12px 20px;border-bottom:1px solid var(--line2)}
.bps .bp-h{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 12px}
.bps .bp-h b{font-weight:600;font-size:14.5px;color:var(--ink)}.bps .bp-h span{font-size:13.5px;color:var(--muted)}
.bps p{margin:4px 0 0;font-size:14.5px;line-height:1.5;color:var(--ink2);text-wrap:pretty}
@media(max-width:600px){.bps li{padding:12px 16px}}
.bps.cut li:nth-child(n+7){display:none}
.minimap{height:240px;border-top:1px solid var(--line2);border-radius:0 0 var(--r) var(--r);overflow:hidden;position:relative}
.bc{padding:20px}
.bc .who{display:flex;align-items:flex-start;gap:14px}
.bc .av{flex:none;display:grid;place-items:center;width:44px;height:44px;border-radius:10px;background:var(--paper);color:var(--ink2)}
.bc h2{font-size:19px;font-weight:600;overflow-wrap:anywhere}
.bc .meta{margin:3px 0 0;color:var(--muted);font-size:14px}
.bc .call{width:100%;min-height:52px;font-size:16px;margin:18px 0 0}
.cl{list-style:none;margin:14px 0 0;padding:0;display:grid;gap:2px}
.cl a{display:flex;align-items:center;gap:12px;min-height:44px;padding:4px 8px;margin:0 -8px;border-radius:8px;color:var(--ink);text-decoration:none;font-weight:600;font-size:14.5px;overflow-wrap:anywhere}
.cl a:hover{background:var(--paper)}
.cl a .ico{color:var(--muted)}
.cl a span{min-width:0;overflow:hidden;text-overflow:ellipsis}
.bc .src{margin:14px 0 0;padding:12px 0 0;border-top:1px solid var(--line2);font-size:13px;color:var(--muted)}
.bc .none{margin:16px 0 0;padding:14px;border-radius:10px;background:var(--paper);font-size:14px;color:var(--ink2)}
.bc .none b{display:block;color:var(--ink);margin:0 0 4px;font-size:14.5px}
.bc .foot{margin:16px 0 0;display:flex;gap:10px;flex-wrap:wrap}
.note{padding:20px 20px 24px}
.note .st:empty{display:none}
.note h2{font-size:17px;font-weight:600;margin:0 0 4px}
.note p.hint{margin:0 0 14px;color:var(--muted);font-size:13.5px}
.note textarea{width:100%;min-height:96px;resize:none;overflow:hidden;padding:12px;border:1px solid var(--field);border-radius:10px;background:#FFFEFB;font-size:16px;line-height:1.5}
.note textarea:focus{outline:none;border-color:var(--blue);box-shadow:var(--focus)}
.note .st{font-size:13px;color:var(--muted);margin:8px 0 0;min-height:18px}
.note .btn{width:100%;margin:0 0 12px}
/* builder page */
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0;margin:20px 0 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.stats div{padding:14px 16px 14px 0}
.stats div+div{padding-left:16px;border-left:1px solid var(--line)}
.stats b{display:block;font:700 26px/1.1 var(--head);letter-spacing:-.01em}
.stats span{font-size:13.5px;color:var(--muted)}
@media(max-width:600px){.stats{grid-template-columns:repeat(2,minmax(0,1fr))}.stats div:nth-child(3){padding-left:0;border-left:0}.stats div:nth-child(n+3){border-top:1px solid var(--line)}}
/* builders list */
.bt{width:100%;border-collapse:collapse;font-size:14.5px}
.bt th{text-align:left;font-size:12.5px;font-weight:600;color:var(--muted);padding:12px 20px;border-bottom:1px solid var(--line)}
.bt td{padding:0;border-top:1px solid var(--line2)}
.bt tr:first-child td{border-top:0}
.bt td a{display:block;padding:12px 20px;color:var(--ink);text-decoration:none}
.bt td.n{padding:12px 20px}
.bt tbody tr{cursor:pointer}
@media(hover:hover) and (pointer:fine){.bt tr:hover td{background:#FBFAF7}}
.bt .n{text-align:right;white-space:nowrap;color:var(--ink)}
.bt .nm b{font-weight:600}
.bt .nm small{display:flex;align-items:center;gap:5px;color:var(--muted);font-size:13px;margin-top:2px}
.bt .nm small .ico{color:var(--teal)}
.bt .z{color:var(--muted);font-weight:400}
.bt .nm small.mob{display:none}
.btool .fld select,.btool .tog{height:44px}
.bt td.n{vertical-align:middle}
.bt th .ico{width:14px;height:14px;vertical-align:-2px;margin-left:2px}
@media(max-width:700px){.bt thead{display:none}.bt td.n{display:none}.bt .nm small.mob{display:block;color:var(--ink2)}.bt td a{padding:13px 16px}}
/* pitch kit */
.pk{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px;align-items:start}
@media(min-width:901px){.pk .mail{position:sticky;top:calc(var(--bar-h) + 16px)}}
@media(max-width:900px){.pk{grid-template-columns:minmax(0,1fr)}}
.pk .panel{padding:20px}
.pk-h{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin:0 0 12px}
.pk-h h2{font-size:18px;font-weight:600}
.pk-h p{margin:4px 0 0;font-size:13.5px;color:var(--muted)}
.sheet{list-style:none;margin:0;padding:0}
.sheet li{display:grid;grid-template-columns:130px minmax(0,1fr);gap:12px;padding:10px 0;border-top:1px solid var(--line2);font-size:14.5px;color:var(--ink2)}
.sheet li b{color:var(--ink);font-weight:600}
@media(max-width:420px){.sheet li{grid-template-columns:minmax(0,1fr);gap:2px}}
.mail>p{margin:0 0 12px;font-size:15px;color:var(--ink2)}
.mail .f{color:var(--blue);font-weight:700}
/* terms */
.terms{display:grid;gap:20px;max-width:880px}
.terms .tx{padding:0 20px 20px;font-size:15px;line-height:1.65;color:var(--ink2)}
.terms .tx p{margin:0 0 12px;max-width:75ch;text-wrap:pretty}.terms .tx p:last-child{margin-bottom:0}
.terms .tx b{color:var(--ink);font-weight:600}
@media(max-width:600px){.terms .tx{padding:0 16px 16px}}
/* footer */
.foot-legal{border-top:1px solid var(--line);max-width:1320px;margin:8px auto 0;padding:20px 16px 32px;font-size:12.5px;line-height:1.6;color:var(--muted)}
.foot-legal p{margin:0 0 8px;max-width:110ch}
.foot-legal .leave{color:var(--ink2,var(--muted));font-weight:500}.foot-legal .leave a{color:inherit;text-decoration:underline;text-underline-offset:2px}
.toast{position:fixed;z-index:1100;left:50%;bottom:24px;transform:translate(-50%,20px);opacity:0;background:var(--ink);color:#fff;padding:12px 18px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border-radius:10px;font-weight:600;font-size:14.5px;box-shadow:0 10px 30px rgba(29,36,51,.3);transition:opacity .2s,transform .25s cubic-bezier(.2,.8,.2,1);pointer-events:none;max-width:calc(100vw - 32px)}
.toast.on{opacity:1;transform:translate(-50%,0)}
@media(max-width:860px){.toast{bottom:calc(var(--nav-h) + 12px + env(safe-area-inset-bottom))}}
.view-enter{animation:vin .32s cubic-bezier(.2,.8,.2,1)}
@keyframes vin{from{opacity:.55;transform:translateY(4px)}to{opacity:1;transform:none}}
</style></head><body>
<a class="skip" href="#/" id="skip">Skip to main content</a>
<header class="bar"><div class="bar-in">
<a class="brand" href="#/" aria-label="ProofNotFluff, __PRODUCT__, overview"><b>ProofNotFluff</b><span class="marks" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></span><small>__RIBBON__</small></a>
<nav class="tabs" id="tabs" aria-label="Sections" hidden></nav>
<span class="bar-sp"></span>
<button class="dl" id="dlTop" type="button" hidden><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg><span class="lg">Download workbook</span><span class="sh">Workbook</span><b class="sr">Download this week's Excel workbook</b></button>
</div></header>
<main id="gateView" class="gate">
<form class="gate-card" id="gate" novalidate>
<span class="chip s2"><svg class="ico s" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>Members</span>
<h1>__GATEH1__</h1>
<p class="sub">List of __ASOF__. __GATESUB__</p>
<label for="pw">Members' password</label>
<div class="pw"><input id="pw" type="password" autocomplete="current-password" autocapitalize="off" spellcheck="false" required aria-describedby="err pwHelp">
<button type="button" class="eye" id="eye" aria-label="Show password" aria-pressed="false"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/><path id="eyeslash" d="M3 3l18 18" hidden/></svg></button></div>
<button class="btn pri" type="submit" id="go">Open this week's list</button>
<p class="err" id="err" role="alert"></p>
<div class="gate-help" id="pwHelp"><p>The password is on your Gumroad purchase page, linked from your receipt email. <a href="https://gumroad.com/library">Open your Gumroad library</a></p>
<p>__GATEBUY__</p></div>
</form>
</main>
<p class="gate-legal" id="gateLegal">__LEGAL__</p>
<main id="app" class="page" hidden tabindex="-1"></main>
<footer class="foot-legal" id="appLegal" hidden><p>__LEGAL__</p><p>List of __ASOF__. __HELPLINE__ <a href="../privacy/">Privacy</a></p><p class="leave">Thinking of cancelling? <a href="__SURVEY__" target="_blank" rel="noopener">Tell us why first<span class="sr"> (opens in a new tab)</span></a>. It takes a minute and decides what we fix next.</p></footer>
<nav class="bnav" id="bnav" aria-label="Sections" hidden></nav>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script>
"use strict";
const BOX=__BOX__;
const PITCH=__PITCH__;
const TERMS=__TERMS__;
const CITY=__CITY__;const PROD=CITY.product;if(CITY.key!=="chicago")document.body.classList.add("c-"+CITY.key);
const b64=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
async function openBox(pw){const k0=await crypto.subtle.importKey("raw",new TextEncoder().encode(pw),"PBKDF2",false,["deriveKey"]);
const key=await crypto.subtle.deriveKey({name:"PBKDF2",salt:b64(BOX.salt),iterations:BOX.rounds,hash:"SHA-256"},k0,{name:"AES-GCM",length:256},false,["decrypt"]);
const pt=await crypto.subtle.decrypt({name:"AES-GCM",iv:b64(BOX.iv)},key,b64(BOX.ct));return JSON.parse(new TextDecoder().decode(pt));}
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const int=n=>Math.round(+n||0).toLocaleString("en-US");
function money(n){n=Math.round(+n||0);if(!n)return "$0";if(typeof CITY!=="undefined"&&CITY.bil2&&Math.round(n/1e7)>=100)return "$"+(Math.round(n/1e7)/100).toFixed(2)+" billion";if(n>=99.95e6)return "$"+int(n/1e6)+"M";if(n>=999.5e3)return "$"+(Math.round(n/1e5)/10).toFixed(1)+"M";return "$"+Math.round(n/1e3)+"K";}
function bigMoney(n){if(typeof CITY!=="undefined"&&CITY.bil2)return money(n);return n>=1e9?"$"+(Math.round(n/1e8)/10).toFixed(1)+" billion":money(n);}
const MON=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
function day(s){const m=/^(\d{4})-(\d{2})-(\d{2})/.exec(s||"");return m?MON[+m[2]-1]+" "+(+m[3])+", "+m[1]:"";}
const sent=s=>{s=String(s||"").toLowerCase();return s.charAt(0).toUpperCase()+s.slice(1);};
const nbh=s=>String(s).replace(/\b([A-Z0-9]{1,3})-(?=[A-Za-z0-9])/g,"$1\u2011");
const plural=(n,a,b)=>int(n)+" "+(n===1?a:(b||a+"s"));
const STG=CITY.stages;
const STG_SHORT=CITY.stagesShort;
const PIPS=[3,2,1];
const STG_LINE=CITY.stageLines;
const I={phone:'<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
mail:'<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
web:'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
copy:'<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h8"/>',
pin:'<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
dl:'<path d="M12 4v11M7 10l5 5 5-5M5 20h14"/>',search:'<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
filter:'<path d="M4 6h16M7 12h10M10 18h4"/>',check:'<path d="m5 12.5 4.5 4.5L19 7.5"/>',back:'<path d="M15 18l-6-6 6-6"/>',
chev:'<path d="m9 6 6 6-6 6"/>',down:'<path d="M12 5v14M6 13l6 6 6-6"/>',up:'<path d="M12 19V5M6 11l6-6 6 6"/>',lock:'<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',list:'<path d="M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01"/>',
map:'<path d="M9 4 3 6.5v13.5L9 17.5l6 2.5 6-2.5V4l-6 2.5z"/><path d="M9 4v13.5M15 6.5V20"/>',
home:'<path d="M3 10.5 12 4l9 6.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/>',
crane:'<path d="M4 21h8M8 21V5l12 3H8M8 5 4 9h4M17 8v5"/><path d="M15.5 13h3v2h-3z"/>',
build:'<path d="M4 21V7l8-4 8 4v14M9 21v-5h6v5M8 10h2M14 10h2M8 13.5h2M14 13.5h2"/>',
flag:'<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',x:'<path d="M6 6l12 12M18 6 6 18"/>',
kit:'<path d="M8 4h8M9 4V3h6v1M6 6h12v15H6z"/><path d="M9 11h6M9 15h6"/>',csv:'<path d="M14 3H6v18h12V7z"/><path d="M14 3v4h4M9 13h6M9 17h6"/>',
ext:'<path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>'};
const ico=(n,c)=>`<svg class="ico${c?" "+c:""}" viewBox="0 0 24 24" aria-hidden="true">${I[n]}</svg>`;
const chip=s=>`<span class="chip s${s}"><span class="pips" aria-hidden="true">${[0,1,2].map(i=>`<i${i<PIPS[s]?' class="f"':""}></i>`).join("")}</span>${STG[s]}</span>`;
function toast(t){const el=$("#toast");el.textContent=t;el.classList.add("on");clearTimeout(toast.t);toast.t=setTimeout(()=>el.classList.remove("on"),2500);}
function untoast(){clearTimeout(toast.t);$("#toast").classList.remove("on");}
async function copyText(t){try{await navigator.clipboard.writeText(t);return true;}catch(e){const a=document.createElement("textarea");a.value=t;a.setAttribute("readonly","");a.style.position="fixed";a.style.opacity="0";document.body.appendChild(a);a.select();let ok=false;try{ok=document.execCommand("copy");}catch(x){}a.remove();return ok;}}

/* private marks and notes: this browser only */
const SKEY=CITY.storageKey;let MARKS={},STORE_OK=true;
try{const t="__pnf";localStorage.setItem(t,"1");localStorage.removeItem(t);MARKS=JSON.parse(localStorage.getItem(SKEY)||"{}")||{};}catch(e){STORE_OK=false;MARKS={};}
function saveMarks(){try{localStorage.setItem(SKEY,JSON.stringify(MARKS));return true;}catch(e){STORE_OK=false;return false;}}
const mk=id=>MARKS[id]||{};
function setMark(id,patch){const m=Object.assign({},mk(id),patch);if(!m.c&&!(m.n||"").trim())delete MARKS[id];else MARKS[id]=m;return saveMarks();}
const STORE_LINE=()=>STORE_OK?"Saved in this browser on this device only. Nobody else sees it, including ProofNotFluff. Clearing your browser data removes it.":"This browser is blocking storage, so contacted marks and notes will be lost when you close the page.";

let D,P,B,BYID,TOTAL=0;
const STATE={trail:[],map:null,mini:null};
function prep(d){D=d;P=d.projects;B=d.builders;BYID={};P.forEach(p=>{BYID[p.id]=p;TOTAL+=p.c;});
for(const k in B){B[k].key=k;B[k].ps=[];}
P.forEach(p=>p.g.forEach(k=>{if(B[k])B[k].ps.push(p);}));
for(const k in B){const b=B[k];b.n=b.ps.length;b.cost=b.ps.reduce((s,p)=>s+p.c,0);b.near=b.ps.filter(p=>p.st===0).length;b.nw=b.ps.filter(p=>p.n).length;
 const ac={};b.ps.forEach(p=>{if(p.ca)ac[p.ca]=(ac[p.ca]||0)+1;});b.area=Object.entries(ac).sort((x,y)=>y[1]-x[1]||x[0].localeCompare(y[0]))[0]?.[0]||"";
 const c=b.contact;b.ok=!!(c&&c.status==="verified"&&(c.phone||c.email));}
}
const pn=(p,i)=>(p.gn&&p.gn[i])||(p.g[i]?B[p.g[i]].name:"");
const bname=p=>p.g.length?pn(p,0):"No builder listed";
const ORDER={clean:(a,b)=>a.st-b.st||b.c-a.c,big:(a,b)=>b.c-a.c,newest:(a,b)=>(b.i||"").localeCompare(a.i||"")||b.c-a.c,builder:(a,b)=>bname(a).localeCompare(bname(b))||b.c-a.c};
const COST=[["",CITY.costAny],["lt1","Under $1M",0,1e6],["1to5","$1M to $5M",1e6,5e6],["5to25","$5M to $25M",5e6,25e6],["25","$25M and up",25e6,Infinity]];
const STAGE_KEYS={near:0,insp:1,issued:2};

/* routing */
function parse(){const h=(location.hash||"#/").slice(1);const i=h.indexOf("?");const path=i<0?h:h.slice(0,i);return{parts:path.split("/").filter(Boolean).map(decodeURIComponent),q:new URLSearchParams(i<0?"":h.slice(i+1))};}
function go(h){location.hash=h;}
function back(fallback){if(STATE.trail.length>1)history.back();else go(fallback);}
function onHash(){const h=location.hash||"#/";const t=STATE.trail;if(t.length>1&&t[t.length-2].split("?")[0]===h.split("?")[0]&&t[t.length-2]===h)t.pop();else if(t[t.length-1]!==h)t.push(h);route(true);}
function setNav(v){const items=[["overview","#/","Overview","home"],["projects","#/projects","Projects","list"],["builders","#/builders","Builders","build"],["pitch","#/pitch","Pitch kit","kit"]];
const html=items.map(([k,h,t,i])=>`<a href="${h}"${k===v?' aria-current="page"':""}>${ico(i)}${t}</a>`).join("");$("#tabs").innerHTML=html;$("#bnav").innerHTML=html;}
function route(scroll){const {parts,q}=parse();const v=parts[0]||"overview";
untoast();for(const k of ["map","mini"]){const m=STATE[k];if(m){try{m.stop();m.off();m.remove();}catch(e){}STATE[k]=null;}}closeSheet();
const app=$("#app");let nav=v;
if(v==="projects")viewProjects(q);
else if(v==="project"&&BYID[parts[1]]){viewProject(BYID[parts[1]]);nav="projects";}
else if(v==="builders")viewBuilders(q);
else if(v==="builder"&&B[parts[1]]){viewBuilder(B[parts[1]]);nav="builders";}
else if(v==="pitch")viewPitch();
else if(v==="terms"){viewTerms();nav="";}
else if(v==="project"||v==="builder"){app.innerHTML=`<div class="panel empty"><h3>That ${v} is not on this week's list</h3><p>${esc(CITY.leaveList)}</p><a class="btn ink" href="#/projects">See this week's projects</a></div>`;nav=v==="project"?"projects":"builders";document.title="Not on this week's list | "+PROD;}
else viewOverview();
setNav(nav);app.classList.remove("view-enter");void app.offsetWidth;app.classList.add("view-enter");
if(scroll){window.scrollTo(0,0);const h=app.querySelector("h1");if(h){h.setAttribute("tabindex","-1");h.focus({preventScroll:true});}}}

/* shared pieces */
function row(p,ctx){const m=mk(p.id);const b=p.g.length?B[p.g[0]]:null;const other=ctx&&ctx!=="near"&&ctx!=="new"&&p.g.find(k=>k!==ctx);const kind=[p.t,p.u?plural(p.u,"home"):"",p.sl?plural(p.sl,"sleeping unit"):""].filter(Boolean).join(", ");
return `<li><a class="row" href="#/project/${encodeURIComponent(p.id)}" data-id="${esc(p.id)}">
<span class="mn num">${money(p.c)}<small>${esc(kind)}</small></span>
<span class="ad">${CITY.key==="austin"?esc(p.a).replace(/ more\)/g,"&nbsp;more)"):esc(p.a)}${p.ca?`<span class="ar">,${CITY.key==="austin"?"&nbsp;":" "}${esc(p.ca)}</span>`:""}</span>
${ctx&&ctx!=="near"&&ctx!=="new"?(other?`<span class="bd"><span>With ${esc(pn(p,p.g.indexOf(other)))}</span></span>`:""):`<span class="bd">${b&&b.ok?ico(b.contact.phone?"phone":"mail","s")+'<span class="sr">Contact on file: </span>':""}<span>${esc(b?pn(p,0):"No builder listed")}${p.g.length>1?` <span class="ar">and ${int(p.g.length-1)} more</span>`:""}</span>${b&&!b.ok&&CITY.contacts?'<span class="nc">No contact yet</span>':""}</span>`}
<span class="rt">${ctx&&ctx!=="new"?"":chip(p.st)}${p.n&&ctx!=="new"?'<span class="badge new">New this week</span>':""}${m.c?`<span class="badge done">${ico("check","s")}Contacted</span>`:""}</span>${ico("chev","chev")}</a></li>`;}
function rowsHtml(list,limit,ctx){if(!list.length)return "";const n=Math.min(limit||list.length,list.length);return `<ul class="list-rows">${list.slice(0,n).map(p=>row(p,ctx)).join("")}</ul>`;}

/* overview */
function viewOverview(){document.title="Overview | "+PROD;
const by=[0,1,2].map(s=>P.filter(p=>p.st===s));const near=by[0].slice().sort(ORDER.big);const nw=P.filter(p=>p.n).sort(ORDER.clean);
const addrs=new Set(P.map(p=>p.a)).size;
const top=Object.values(B).sort((a,b)=>b.near-a.near||b.n-a.n||b.cost-a.cost).slice(0,6);
const ac={};P.forEach(p=>{if(p.ca){const a=ac[p.ca]=ac[p.ca]||[0,0,0];a[p.st]++;}});const areas=Object.entries(ac).map(([a,c])=>[a,c[0]+c[1]+c[2],c]).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).slice(0,8);const amax=areas.length?areas[0][1]:1;
const marked=Object.keys(MARKS).filter(id=>BYID[id]);const cN=marked.filter(id=>MARKS[id].c).length,nN=marked.filter(id=>(MARKS[id].n||"").trim()).length;
const stn=s=>`<${by[s].length?"a":"span"} class="stn s${s}${by[s].length?"":" z"}"${by[s].length?` href="#/projects?stage=${["near","insp","issued"][s]}"`:""}><span class="dot">${ico(["check","search","crane"][s])}</span><span class="n num">${int(by[s].length)}</span><span class="tx"><span class="t">${STG[s]}</span><span class="m num">${bigMoney(by[s].reduce((x,p)=>x+p.c,0))} ${CITY.costShort}</span></span></${by[s].length?"a":"span"}>`;
$("#app").innerHTML=`<section class="hero">${CITY.seatName?`<p class="seatchip">Your seat: ${esc(CITY.seatName)}</p>`:""}<h1>${by[0].length||!by[1].length?`${int(by[0].length)} ${by[0].length===1?"project is":"projects are"} close to a final clean this week`:`${int(by[1].length)} ${by[1].length===1?"project has":"projects have"} ${esc(STG[1].toLowerCase())}, none at ${esc(STG[0].toLowerCase())} yet`}</h1>
<p>${CITY.key==="austin"?`${int(P.length)} open projects on the list (${int(P.reduce((x,p)=>x+(p.b||0),0))} building permits), ${bigMoney(TOTAL)} in valuation`:`${int(P.length)} open permits on the list, ${bigMoney(TOTAL)} in reported cost at ${int(addrs)} addresses`}. Built from ${esc(CITY.records)}, list of ${esc(D.asOf)}.</p></section>
<nav class="line" aria-label="Projects by stage, from permit to final clean">${stn(2)}${stn(1)}${stn(0)}<span class="flag"><span class="dot">${ico("flag")}</span><span class="tx"><span class="t">Final clean</span><span class="m">Your bid</span></span></span></nav>
<div class="ov"><div class="ov-col">
${near.length?`<section class="panel"><div class="sec-h"><h2>Closest to a final clean<span class="c num">${int(near.length)}</span></h2><a href="#/projects?stage=near">See all ${int(near.length)}</a></div>${rowsHtml(near,0,"near")}</section>
<section class="panel"><div class="sec-h"><h2>New this week<span class="c num">${int(nw.length)}</span></h2>${nw.length?`<a href="#/projects?new=1">See all ${int(nw.length)}</a>`:""}</div>${nw.length?rowsHtml(nw,5,"new"):`<p class="empty">No permits on the list were issued in the last 7 days.</p>`}</section>`:`<section class="panel"><div class="sec-h"><h2>Builders to call first</h2><a href="#/builders">All ${int(Object.keys(B).length)} builders</a></div>
${top.map(b=>`<a class="mini-b" href="#/builder/${encodeURIComponent(b.key)}"><b>${esc(b.name)}</b><span>${plural(b.n,CITY.bNoun)}${CITY.bWeek}${CITY.contacts?", "+(b.ok?"contact on file":"no contact on file yet"):""}</span>${top.some(x=>x.near)?`<span class="r num">${int(b.near)}<small>near finish</small></span>`:`<span class="r num">${int(b.n)}<small>${b.n===1?"project":"projects"}</small></span>`}</a>`).join("")}</section>
<section class="panel"><div class="sec-h"><h2>New this week<span class="c num">${int(nw.length)}</span></h2>${nw.length?`<a href="#/projects?new=1">See all ${int(nw.length)}</a>`:""}</div>${nw.length?rowsHtml(nw,5,"new"):`<p class="empty">No permits on the list were issued in the last 7 days.</p>`}</section>
<section class="panel nb"><p><b>None at ${esc(STG[0].toLowerCase())} this week.</b> The ${plural(by[1].length,"project")} with ${esc(STG[1].toLowerCase())} ${by[1].length===1?"is":"are"} next closest.</p>${by[1].length?`<a class="btn sm" href="#/projects?stage=insp">Open the ${int(by[1].length)}</a>`:""}</section>`}
</div><div class="ov-col">
${near.length?`<section class="panel"><div class="sec-h"><h2>Builders to call first</h2><a href="#/builders">All ${int(Object.keys(B).length)} builders</a></div>
${top.map(b=>`<a class="mini-b" href="#/builder/${encodeURIComponent(b.key)}"><b>${esc(b.name)}</b><span>${plural(b.n,CITY.bNoun)}${CITY.bWeek}${CITY.contacts?", "+(b.ok?"contact on file":"no contact on file yet"):""}</span>${top.some(x=>x.near)?`<span class="r num">${int(b.near)}<small>near finish</small></span>`:`<span class="r num">${int(b.n)}<small>${b.n===1?"project":"projects"}</small></span>`}</a>`).join("")}</section>`:""}
<section class="panel"><div class="sec-h"><h2>Where the work is</h2><a href="#/projects?view=map">Open the map</a></div>
<p class="blg" aria-hidden="true"><span><i class="b0"></i>${STG_SHORT[0]}</span><span><i class="b1"></i>${STG_SHORT[1]}</span><span><i class="b2"></i>${STG_SHORT[2]}</span></p>
<ul class="bars" aria-label="Open projects by ${CITY.areaLower} and stage"><li class="hd" aria-hidden="true"><span></span><span class="sp2"></span><span>Near finish</span><span>All</span></li>${areas.map(([a,n,c])=>`<li><a href="#/projects?area=${encodeURIComponent(a)}" aria-label="${esc(a)}: ${plural(n,"project")}, ${int(c[0])} near finish, ${int(c[1])} ${CITY.midWords}, ${int(c[2])} permit issued" title="${int(c[0])} near finish, ${int(c[1])} ${STG_SHORT[1].toLowerCase()}, ${int(c[2])} permit issued"><span>${esc(a)}</span><span class="tr" style="width:${Math.max(3,Math.round(n/amax*100))}%" aria-hidden="true">${[0,1,2].filter(s=>c[s]).map(s=>`<i class="b${s}" style="flex-grow:${c[s]}"></i>`).join("")}</span><span class="nv num${c[0]?"":" z"}">${int(c[0])}</span><span class="v num">${int(n)}</span></a></li>`).join("")}</ul></section>
<section class="panel"><div class="sec-h"><h2>Your follow-ups</h2>${cN||nN?`<a href="#/projects?fu=mine">Show them</a>`:""}</div>
<div class="mine">${cN||nN?`<p class="mh"><b>${plural(cN,"project")}</b> marked contacted, <b>${plural(nN,"note")}</b> written.</p>`:`<p class="mh"><b class="blk">No follow-ups yet</b>Mark a project as contacted or add a note on its page, and it shows up here.</p>`}<p>${esc(STORE_LINE())}</p>${cN||nN?"":(by[0].length||!by[1].length?`<a class="btn" href="#/projects?stage=near">Open the ${plural(by[0].length,"near-finish project")}</a>`:`<a class="btn" href="#/projects?stage=insp">Open the ${plural(by[1].length,"project")} with ${esc(STG[1].toLowerCase())}</a>`)}</div></section>
</div></div>`;}

/* projects: filters, list and map, in sync */
function readF(q){return{q:(q.get("q")||"").trim(),stage:q.get("stage")||"",area:q.get("area")||"",cost:q.get("cost")||"",type:q.get("type")||"",nw:q.get("new")==="1",fu:["todo","mine"].includes(q.get("fu"))?q.get("fu"):"",sort:ORDER[q.get("sort")]?q.get("sort"):"clean",view:q.get("view")==="map"?"map":"list"};}
function writeF(f){const q=new URLSearchParams();if(f.q)q.set("q",f.q);if(f.stage)q.set("stage",f.stage);if(f.area)q.set("area",f.area);if(f.cost)q.set("cost",f.cost);if(f.type)q.set("type",f.type);if(f.nw)q.set("new","1");if(f.fu)q.set("fu",f.fu);if(f.sort!=="clean")q.set("sort",f.sort);if(f.view==="map")q.set("view","map");const s=q.toString();return "#/projects"+(s?"?"+s:"");}
const norm=s=>String(s||"").toLowerCase().normalize("NFKD").replace(/[^a-z0-9 ]/g," ").replace(/\s+/g," ").trim();
function pass(p,f,skip){if(skip!=="q"&&f.q){const t=norm(f.q);const hay=norm([p.a,p.ca,p.id,...p.g.map(k=>B[k].name),...(p.pm||[]).map(x=>x.n),...(p.ms||[])].join(" "));if(!t.split(" ").every(w=>hay.includes(w)))return false;}
if(skip!=="stage"&&f.stage&&p.st!==STAGE_KEYS[f.stage])return false;if(skip!=="area"&&f.area&&p.ca!==f.area)return false;
if(skip!=="cost"&&f.cost){const c=COST.find(x=>x[0]===f.cost);if(c&&!(p.c>=c[2]&&p.c<c[3]))return false;}
if(skip!=="type"&&f.type&&p.t!==f.type)return false;if(skip!=="new"&&f.nw&&!p.n)return false;if(f.fu==="todo"&&mk(p.id).c)return false;
if(f.fu==="mine"&&!(mk(p.id).c||(mk(p.id).n||"").trim()))return false;return true;}
function activeCount(f){return [f.area,f.cost,f.type,f.nw,f.fu].filter(Boolean).length;}
function viewProjects(q){const f=readF(q);STATE.f=f;STATE.shown=60;document.title="Projects | "+PROD;
const areas=[...new Set(P.map(p=>p.ca).filter(Boolean))].sort();
$("#app").innerHTML=`<div class="ph"><h1>Projects</h1></div>
<div class="tool"><label class="search"><span class="sr">Search projects</span>${ico("search")}<input id="fq" type="search" placeholder="${CITY.key==="austin"?"Search address, builder, permit":"Search address, builder or permit"}" value="${esc(f.q)}" autocomplete="off" enterkeyhint="search"><button type="button" class="clr" id="fqx" aria-label="Clear search"${f.q?"":" hidden"}>${ico("x","s")}</button></label>
<div class="seg" id="fstage" role="group" aria-label="Stage"></div>
<button class="btn fbtn" id="fopen" type="button" aria-haspopup="dialog" aria-controls="fsheet">${ico("filter")}<span id="fopenT">Filters</span></button>
<span class="tsp"></span><button class="btn csvb" type="button" id="csv" aria-label="Export these projects as a CSV file">${ico("csv","s")}<span class="t" aria-hidden="true">Export CSV</span><span class="m" aria-hidden="true">CSV</span></button>
<div class="seg vtog" role="group" aria-label="Show as"><button type="button" data-v="list">${ico("list","s")}List</button><button type="button" data-v="map">${ico("map","s")}Map</button></div></div>
<div class="filters" id="fsheet" aria-label="Filters">
<div class="sheet-h"><h2 id="fsheetH">Filters</h2><button class="btn sm" type="button" id="fclose" aria-label="Close filters">${ico("x","s")}</button></div>
<div class="fld"><label for="farea">${CITY.area}</label><select id="farea"></select></div>
<div class="fld"><label for="fcost">${CITY.cost}</label><select id="fcost"></select></div>
<div class="fld"><label for="ftype">Building type</label><select id="ftype"></select></div>
<div class="fld"><label for="fsort">Sort</label><select id="fsort"><option value="clean">Closest to finish</option><option value="big">Biggest first</option><option value="newest">Newest permit first</option><option value="builder">Builder, A to Z</option></select></div>
<div class="fld"><label for="ffu">Follow-up</label><select id="ffu"><option value="">All projects</option><option value="todo">Not contacted yet</option><option value="mine">Contacted or with a note</option></select></div>
<label class="tog"><input type="checkbox" id="fnew"><span id="fnewT">New this week</span></label>
<div class="sheet-f"><button class="btn" type="button" id="freset">Clear filters</button><button class="btn ink" type="button" id="fdone">Show projects</button></div>
</div>
<div class="rbar" aria-live="polite"><span id="rcount"></span><button class="lnk" type="button" id="fclear" hidden>Clear filters</button></div>
<div class="split" id="split" data-v="${f.view}"><section class="panel lst" aria-label="Project list"><div id="plist"></div></section>
<div class="mapbox" id="mapbox"><div class="map" id="map" role="region" aria-label="Map of the projects in the list. The list has the same projects."></div>
<div class="legend" aria-hidden="true"><span><i class="lg0"></i>${STG_SHORT[0]}</span><span><i class="lg1"></i>${STG_SHORT[1]}</span><span><i class="lg2"></i>${STG_SHORT[2]}</span></div>
<p class="map-note" id="mapnote" hidden></p></div></div>`;
const upd=(patch,keepFocus)=>{Object.assign(STATE.f,patch);STATE.shown=60;history.replaceState(history.state,"",writeF(STATE.f));STATE.trail[STATE.trail.length-1]=location.hash;refresh(true);};
let tq;$("#fq").addEventListener("input",e=>{$("#fqx").hidden=!e.target.value;clearTimeout(tq);tq=setTimeout(()=>upd({q:e.target.value.trim()}),140);});
$("#fqx").onclick=()=>{$("#fq").value="";$("#fqx").hidden=true;upd({q:""});$("#fq").focus();};
$("#farea").onchange=e=>upd({area:e.target.value});$("#fcost").onchange=e=>upd({cost:e.target.value});$("#ftype").onchange=e=>upd({type:e.target.value});
$("#fsort").onchange=e=>upd({sort:e.target.value});$("#fnew").onchange=e=>upd({nw:e.target.checked});$("#ffu").onchange=e=>upd({fu:e.target.value});
const clear=()=>{$("#fq").value="";$("#fqx").hidden=true;upd({q:"",stage:"",area:"",cost:"",type:"",nw:false,fu:""});};
$("#fclear").onclick=clear;$("#freset").onclick=clear;
$("#fopen").onclick=openSheet;$("#fclose").onclick=closeSheet;$("#fdone").onclick=closeSheet;
document.querySelectorAll(".vtog button").forEach(b=>b.onclick=()=>{upd({view:b.dataset.v});$("#split").dataset.v=b.dataset.v;syncVtog();if(b.dataset.v==="map")showMap();});
$("#csv").onclick=exportCsv;
STATE.areas=areas;refresh(false);syncVtog();
const phone=window.matchMedia("(max-width:860px)").matches;if(!phone)ensureMap();else if(f.view==="map")setTimeout(showMap,60);}
function showMap(){const t=$("#fopen");if(t&&window.matchMedia("(max-width:860px)").matches){const y=t.getBoundingClientRect().top+window.scrollY-parseInt(getComputedStyle(document.documentElement).getPropertyValue("--bar-h"))-12;window.scrollTo(0,Math.max(0,y));}
setTimeout(()=>{ensureMap();if(STATE.map){STATE.map.invalidateSize();fit();}},40);}
function syncVtog(){document.querySelectorAll(".vtog button").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.v===STATE.f.view)));}
function filtered(){const f=STATE.f;return P.filter(p=>pass(p,f)).sort(ORDER[f.sort]);}
function refresh(refit){const f=STATE.f;
const facet=(skip,test)=>P.filter(p=>pass(p,f,skip)&&test(p)).length;
$("#fstage").innerHTML=[["","All",()=>true],["near",STG_SHORT[0],p=>p.st===0],["insp",STG_SHORT[1],p=>p.st===1],["issued",STG_SHORT[2],p=>p.st===2]].map(([k,t,fn])=>`<button type="button" data-k="${k}" aria-pressed="${f.stage===k}">${t}<span class="c num">${int(facet("stage",fn))}</span></button>`).join("");
$("#fstage").querySelectorAll("button").forEach(b=>b.onclick=()=>{Object.assign(STATE.f,{stage:b.dataset.k});STATE.shown=60;history.replaceState(history.state,"",writeF(STATE.f));STATE.trail[STATE.trail.length-1]=location.hash;refresh(true);});
const opt=(v,t,n,sel)=>`<option value="${esc(v)}"${sel?" selected":""}>${esc(t)}${n==null?"":` (${int(n)})`}</option>`;
$("#farea").innerHTML=opt("",CITY.areaAll,null,!f.area)+STATE.areas.map(a=>opt(a,a,facet("area",p=>p.ca===a),f.area===a)).join("");
$("#fcost").innerHTML=COST.map(c=>opt(c[0],c[1],c[0]?facet("cost",p=>p.c>=c[2]&&p.c<c[3]):null,f.cost===c[0])).join("");
$("#ftype").innerHTML=opt("","Any type",null,!f.type)+CITY.types.map(t=>opt(t,t,facet("type",p=>p.t===t),f.type===t)).join("");
$("#fsort").value=f.sort;$("#fnew").checked=f.nw;$("#ffu").value=f.fu;$("#fnewT").textContent=`New this week (${int(facet("new",p=>p.n))})`;
const ac=activeCount(f);$("#fopenT").innerHTML=ac?`Filters <span class="fcount num">${ac}</span>`:"Filters";
const rows=filtered();STATE.rows=rows;const sum=rows.reduce((s,p)=>s+p.c,0);
$("#rcount").innerHTML=!rows.length?`<b class="num">0</b> of <span class="num">${int(P.length)}</span> projects`:rows.length===P.length?`<b class="num">${int(rows.length)}</b> projects, <span class="num">${bigMoney(sum)}</span> ${CITY.costShort}`:`<b class="num">${int(rows.length)}</b> of <span class="num">${int(P.length)}</span> projects, <span class="num">${bigMoney(sum)}</span> ${CITY.costShort}`;
$("#fclear").hidden=!(f.q||f.stage||ac);$("#fdone").textContent=rows.length?`Show ${plural(rows.length,"project")}`:"No projects match";$("#csv").disabled=!rows.length;
drawList();drawMap(refit);}
function drawList(){const rows=STATE.rows,n=Math.min(STATE.shown,rows.length);const el=$("#plist");
if(!rows.length){const q=STATE.f.q,only=q&&!STATE.f.stage&&!activeCount(STATE.f);el.innerHTML=q?`<div class="empty"><h3>No projects match "${esc(q)}"</h3><p>Check the spelling, or clear the ${only?"search":"search and filters"} to see all ${int(P.length)}.</p><button class="btn ink" type="button" id="eclr">${only?"Clear search":"Clear search and filters"}</button></div>`:`<div class="empty"><h3>No projects match these filters</h3><p>Try another ${CITY.areaLower} or cost band, or clear the filters to see all ${int(P.length)}.</p><button class="btn ink" type="button" id="eclr">Clear filters</button></div>`;$("#eclr").onclick=()=>$("#fclear").click();return;}
el.innerHTML=rowsHtml(rows,n)+(n<rows.length?`<div class="row-more"><button class="btn" type="button" id="more">Show ${int(Math.min(60,rows.length-n))} more</button><span>${int(n)} of ${int(rows.length)} shown</span></div>`:"");
const m=$("#more");if(m)m.onclick=()=>{STATE.shown+=60;drawList();};
el.querySelectorAll(".row").forEach(a=>{a.addEventListener("mouseenter",()=>hot(a.dataset.id,true));a.addEventListener("mouseleave",()=>hot(a.dataset.id,false));});}

/* map */
const MS=[{radius:9,color:"#fff",weight:2.5,fillColor:"#2E6B66",fillOpacity:1},{radius:6,color:"#fff",weight:1.5,fillColor:"#2F5F9E",fillOpacity:.92},{radius:5.5,color:"#3A4152",weight:2,fillColor:"#fff",fillOpacity:1}];
function tiles(m){L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(m);}
function ensureMap(){STATE.lazyMap=false;if(STATE.map||!$("#map"))return;if(!window.L){const box=$("#mapbox");if(box&&!box.querySelector(".map-fail"))box.insertAdjacentHTML("beforeend",'<div class="map-fail"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg><p>The map did not load on this connection. The list has every project.</p></div>');const sp=$("#split");sp&&sp.classList.add("nomap");if(!ensureMap.tries){ensureMap.tries=1;window.addEventListener("load",()=>{if($("#map")&&!STATE.map){const f=$("#mapbox .map-fail");f&&f.remove();const sp=$("#split");sp&&sp.classList.remove("nomap");ensureMap();}},{once:true});}return;}
const m=L.map("map",{preferCanvas:true,zoomControl:true,scrollWheelZoom:true,attributionControl:true}).setView(CITY.center,CITY.zoom);
m.attributionControl.setPrefix('<a href="https://leafletjs.com">Leaflet</a>');tiles(m);STATE.map=m;STATE.layer=L.layerGroup().addTo(m);STATE.mk={};m.on("zoomend",declutter);drawMap(true);}
function popup(p){const b=p.g.length?B[p.g[0]]:null;return `<div class="pop"><span class="mn num">${money(p.c)}</span><span class="ad">${esc(p.a)}</span><span class="bd">${esc(b?pn(p,0):"No builder listed")}</span>${chip(p.st)}<p style="margin:10px 0 0"><a class="btn ink" href="#/project/${encodeURIComponent(p.id)}">Open project</a></p></div>`;}
function drawMap(refit){const m=STATE.map;const rows=STATE.rows||[];const geo=rows.filter(p=>p.lat&&p.lon);const note=$("#mapnote");
if(note){const miss=rows.length-geo.length;note.hidden=!(miss||!rows.length);note.textContent=!rows.length?"No pins for these filters.":miss?`${plural(miss,"project")} in the list ${miss===1?"has":"have"} ${CITY.noGeo}.`:"";}
if(!m)return;STATE.layer.clearLayers();STATE.mk={};
STATE.near=[];geo.slice().sort((a,b)=>b.st-a.st).forEach(p=>{let ring=null;if(p.st===0){ring=L.circleMarker([p.lat,p.lon],{radius:12,color:"#1F4E4A",weight:2,fill:false,interactive:false}).addTo(STATE.layer);}
const c=L.circleMarker([p.lat,p.lon],MS[p.st]).bindPopup(popup(p),{maxWidth:280});c.addTo(STATE.layer);STATE.mk[p.id]=c;if(ring)STATE.near.push({p,c,ring});});declutter();
if(refit&&geo.length){const bb=L.latLngBounds(geo.map(p=>[p.lat,p.lon]));if(geo.length===1)m.setView(bb.getCenter(),15,{animate:false});else m.fitBounds(bb,{padding:[48,48],maxZoom:15,animate:false});}declutter();}
function fit(){drawMap(true);}
/* near-finish pins that sit on top of each other are spread apart in screen space so each one can be tapped */
function declutter(){const m=STATE.map,ns=STATE.near||[];if(!m||!ns.length)return;const pts=ns.map(o=>m.latLngToLayerPoint([o.p.lat,o.p.lon]));
for(let it=0;it<30;it++){let moved=false;for(let i=0;i<pts.length;i++)for(let j=i+1;j<pts.length;j++){const dx=pts[j].x-pts[i].x,dy=pts[j].y-pts[i].y,d=Math.hypot(dx,dy),min=26;
if(d<min){const ux=d?dx/d:Math.cos(i+j),uy=d?dy/d:Math.sin(i+j),push=(min-d)/2;pts[i]=pts[i].subtract([ux*push,uy*push]);pts[j]=pts[j].add([ux*push,uy*push]);moved=true;}}if(!moved)break;}
ns.forEach((o,i)=>{const ll=m.layerPointToLatLng(pts[i]);o.c.setLatLng(ll);o.ring.setLatLng(ll);o.c.bringToFront();});}
function hot(id,on){const c=STATE.mk&&STATE.mk[id];if(!c)return;const p=BYID[id];c.setStyle(on?{radius:MS[p.st].radius+4,weight:3,color:"#C8502F"}:MS[p.st]);if(on)c.bringToFront();else if(p.st!==0)(STATE.near||[]).forEach(o=>o.c.bringToFront());}

/* filters sheet (phone) */
let lastFocus=null;
function openSheet(){const s=$("#fsheet");if(!s)return;lastFocus=document.activeElement;s.classList.add("open");s.setAttribute("role","dialog");s.setAttribute("aria-modal","true");s.setAttribute("aria-labelledby","fsheetH");
const sc=document.createElement("div");sc.className="scrim";sc.id="scrim";sc.onclick=closeSheet;document.body.appendChild(sc);setTimeout(()=>$("#farea").focus(),60);document.addEventListener("keydown",sheetKeys);}
function closeSheet(){const s=$("#fsheet");const sc=$("#scrim");if(sc)sc.remove();document.removeEventListener("keydown",sheetKeys);if(!s||!s.classList.contains("open"))return;s.classList.remove("open");s.removeAttribute("role");s.removeAttribute("aria-modal");if(lastFocus&&lastFocus.focus)lastFocus.focus();}
function sheetKeys(e){if(e.key==="Escape"){closeSheet();return;}if(e.key!=="Tab")return;const f=[...$("#fsheet").querySelectorAll("select,input,button")].filter(x=>x.offsetParent!==null);if(!f.length)return;const a=f[0],z=f[f.length-1];
if(e.shiftKey&&document.activeElement===a){e.preventDefault();z.focus();}else if(!e.shiftKey&&document.activeElement===z){e.preventDefault();a.focus();}}

/* CSV of the current view */
function cell(v){v=v==null?"":String(v);if(/^[=+\-@\t\r]/.test(v)&&!/^-?\d+(\.\d+)?$/.test(v))v="'"+v;return /[",\r\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v;}
function exportCsv(){const rows=STATE.rows||[];if(!rows.length)return;
if(CITY.key==="austin"){exportCsvAustin(rows);return;}
const head=["Address","Community area","Reported cost","Stage","City milestone","City permit status","Type","Homes","Sleeping units","Issued","Permit","Builder","All builders","Builder office phone","Builder email","Builder website","New this week","Contacted","Contacted on","Your note","What the permit covers","Latitude","Longitude"];
const lines=[head.map(cell).join(",")];
rows.forEach(p=>{const b=p.g.length?B[p.g[0]]:null;const c=b&&b.contact&&b.contact.status==="verified"?b.contact:{};const m=mk(p.id);
lines.push([p.a,p.ca,p.c,STG[p.st],p.m,p.cs,p.t,p.u||"",p.sl||"",p.i,p.id,b?pn(p,0):"",p.g.map((k,i)=>pn(p,i)).join("; "),c.phone||"",c.email||"",c.website||"",p.n?"Yes":"",m.c?"Yes":"",m.c||"",(m.n||"").trim(),p.sf,p.lat||"",p.lon||""].map(cell).join(","));});
const blob=new Blob(["﻿"+lines.join("\r\n")+"\r\n"],{type:"text/csv;charset=utf-8"});
const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=`${CITY.csvPrefix}-${D.asOfIso}-${rows.length}-projects.csv`;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),4000);
toast(`CSV exported: ${plural(rows.length,"project")}`);}
/* Austin: one row per project (building permits grouped by master permit), every building permit number in one cell */
function exportCsvAustin(rows){
const head=["Address","ZIP code","Council district","Valuation","Stage","Type","Homes","Building permits open","Building permits final","First issued","Master permit","Building permit numbers","Builder","All builders","New this week","Contacted","Contacted on","Your note","What the permits cover","Latitude","Longitude","Map location from"];
const lines=[head.map(cell).join(",")];
rows.forEach(p=>{const b=p.g.length?B[p.g[0]]:null;const m=mk(p.id);
lines.push([p.a,p.ca,p.di||"",p.c,STG[p.st],p.t,p.u||"",p.b||"",p.bf||"",p.i,p.id,(p.pm||[]).map(x=>x.n).join("; "),b?pn(p,0):"",p.g.map((k,i)=>pn(p,i)).join("; "),p.n?"Yes":"",m.c?"Yes":"",m.c||"",(m.n||"").trim(),p.sf,p.lat||"",p.lon||"",p.lat?(p.gs==="census"?"US Census Bureau geocoder":"City of Austin record"):""].map(cell).join(","));});
const blob=new Blob(["\ufeff"+lines.join("\r\n")+"\r\n"],{type:"text/csv;charset=utf-8"});
const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=`${CITY.csvPrefix}-${D.asOfIso}-${rows.length}-projects.csv`;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),4000);
toast(`CSV exported: ${plural(rows.length,"project")}`);}
function downloadWorkbook(){const blob=new Blob([b64(D.xlsx)],{type:"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"});
const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=D.fileName;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),4000);toast("Workbook downloaded");}

/* builder card */
function builderCard(b,p,showLink,onBuilderPage,shown){const c=b.contact;const subj=p?`?subject=${encodeURIComponent("Final clean for "+p.a)}`:"";
const host=u=>{try{return new URL(u).hostname.replace(/^www\./,"");}catch(e){return u;}};
let body="";
if(b.ok){body=`${c.phone?`<a class="btn pri call" href="tel:+1${esc(c.tel)}">${ico("phone")}Call ${esc(c.phone)}</a>`:""}
<ul class="cl">${c.email?`<li><a href="mailto:${esc(c.email)}${subj}">${ico("mail")}<span>${esc(c.email)}</span></a></li>`:""}${c.website?`<li><a href="${esc(c.website)}" target="_blank" rel="noopener">${ico("web")}<span>${esc(host(c.website))}</span><span class="sr"> (opens in a new tab)</span></a></li>`:""}${c.contactPage&&c.contactPage!==c.website?`<li><a href="${esc(c.contactPage)}" target="_blank" rel="noopener">${ico("ext")}<span>Their contact page</span><span class="sr"> (opens in a new tab)</span></a></li>`:""}</ul>
<p class="src">${c.note?esc(c.note.charAt(0).toUpperCase()+c.note.slice(1))+". ":""}Main office details from ${c.source?`<a href="${esc(c.source)}" target="_blank" rel="noopener">the builder's own website</a>`:"the builder's own website"}${c.checkedAt?`, checked ${esc(day(c.checkedAt))}`:""}. Ask for the project manager or the estimator on this job.</p>`;}
else if(!CITY.contacts){body=`<div class="none"><b>Reach the builder's main office</b>We list the general contractor the City names on the permits. Search for their main office and ask for the project manager or the estimator ${onBuilderPage?"on your project, with its":"on this project, with the"} address and ${esc(CITY.permitLower)} number ready.</div>
<div class="foot"><a class="btn" href="https://www.google.com/search?q=${encodeURIComponent(b.name+" "+CITY.city)}" target="_blank" rel="noopener">${ico("search","s")}Search the web for this builder<span class="sr"> (opens in a new tab)</span></a></div>`;}
else{body=`<div class="none"><b>No contact on file yet</b>We list a builder's office phone and general email only after reading them on the builder's own website. This builder is not checked yet, we found no website that is clearly theirs, or their site does not show them.</div>
<div class="foot"><a class="btn" href="https://www.google.com/search?q=${encodeURIComponent(b.name+" "+CITY.city)}" target="_blank" rel="noopener">${ico("search","s")}Search the web for this builder<span class="sr"> (opens in a new tab)</span></a></div>`;}
return `<section class="panel bc" aria-label="${onBuilderPage?"Contact":"Builder"}">${onBuilderPage?`<h2>Contact</h2>`:`<div class="who"><span class="av">${ico("build")}</span><div><h2>${esc(shown||b.name)}</h2><p class="meta num">${plural(b.n,CITY.bNoun)}${CITY.bWeek}<br>${money(b.cost)} ${CITY.costShort}${b.near?`, ${int(b.near)} near finish`:""}</p></div></div>`}${body}
${showLink?`<div class="foot"><a class="btn" href="#/builder/${encodeURIComponent(b.key)}">See all ${plural(b.n,"project")} by this builder</a></div>`:""}</section>`;}

/* project page */
function viewProject(p){document.title=`${p.a} | ${PROD}`;const m=mk(p.id);
const kind=[p.t,p.u?plural(p.u,"home"):"",p.sl?plural(p.sl,"sleeping unit"):""].filter(Boolean).join(", ");
const bs=p.g.map(k=>B[k]);
const sub=s=>p.st===s?(s===2&&p.i?"Issued "+day(p.i)+". Current stage":"Current stage"):p.st<s?(s===2&&p.i?"Issued "+day(p.i):"Done"):"Not yet";
const steps=[[2,STG[2],sub(2)],[1,STG[1],sub(1)],[0,STG[0],sub(0)]];
const where=", "+CITY.city+", "+CITY.state;const aus=CITY.key==="austin";
const maps="https://www.google.com/maps/search/?api=1&query="+encodeURIComponent(p.a.replace(/ \(\+\d+ more\)$/,"")+where);
$("#app").innerHTML=`<a class="back" href="#/projects" id="back">${ico("back")}Back</a>
<div class="pg"><section class="pg-head"><div class="ph-chips">${chip(p.st)}${p.n?'<span class="badge new">New this week</span>':""}${m.c?`<span class="badge done">${ico("check","s")}Contacted ${esc(day(m.c))}</span>`:""}</div>
<div class="p-title"><h1>${esc(p.a)}</h1><p class="sub">${esc([p.ca,CITY.city].filter(Boolean).join(", "))}${aus&&p.di?`, council district ${esc(p.di)}`:""}</p></div>
<div class="p-money"><b class="num">${money(p.c)}</b><span class="num">${esc(CITY.costLower)} ($${int(p.c)})</span></div>
<div class="acts"><button class="btn" type="button" id="cpy">${ico("copy","s")}Copy address</button><a class="btn" href="${maps}" target="_blank" rel="noopener">${ico("pin","s")}Directions<span class="sr"> (opens Google Maps in a new tab)</span></a></div></section>
<aside class="pg-side" aria-label="Builder and your follow-up">
${bs.length?bs.map((b,i)=>builderCard(b,p,true,false,pn(p,i))).join(""):`<section class="panel bc"><div class="none"><b>No builder listed</b>The City record names no general contractor business for this ${esc(CITY.permitLower)}.</div></section>`}
<section class="panel note" aria-labelledby="nh"><h2 id="nh">Your follow-up</h2><p class="hint">${esc(STORE_LINE())}</p>
<button class="btn${m.c?" on":""}" type="button" id="mark" aria-pressed="${!!m.c}">${ico("check","s")}<span id="markT">${m.c?"Contacted "+esc(day(m.c))+" (undo)":"Mark as contacted"}</span></button>
<label for="nt" class="sr">Private note</label><textarea id="nt" placeholder="Who you spoke to, the bid due date, the next call" maxlength="2000">${esc(m.n||"")}</textarea><p class="st" id="ntst" aria-live="polite"></p></section>
</aside><div class="pg-main"><section class="panel track"><h2>Where this job is</h2><ol class="steps">${steps.map(([s,t,sub])=>`<li class="${p.st===s?"now s"+s:p.st<s?"done":""}"${p.st===s?' aria-current="step"':""}><span class="k">${p.st<s?ico("check","s"):p.st===s?ico(["check","search","crane"][s],"s"):""}</span><b>${t}</b>${sub?`<span>${esc(sub)}</span>`:""}</li>`).join("")}<li class="fin"><span class="k">${ico("flag","s")}</span><b>Final clean</b><span>Your bid</span></li></ol>
${aus?`<p class="ms"><b>City record:</b> ${plural(p.b||0,"building permit")} open${p.bf?`, ${int(p.bf)} final`:""}. ${STG_LINE[p.st]}</p></section>
<section class="panel"><div class="sec-h"><h2>Project details</h2></div><dl class="facts">
<div><dt>Valuation</dt><dd class="num">$${int(p.c)}</dd></div><div><dt>Type</dt><dd>${esc(p.t)}</dd></div><div><dt>Homes</dt><dd class="num">${p.u?int(p.u):"None listed"}</dd></div><div><dt>First issued</dt><dd>${esc(day(p.i))}</dd></div>
<div><dt>${(p.ms||[]).length>1?"Master permits":"Master permit"}</dt><dd class="num">${esc((p.ms||[p.id]).join(", "))}</dd></div><div><dt>Building permits</dt><dd class="num">${int(p.b||0)} open${p.bf?`, ${int(p.bf)} final`:""}</dd></div><div><dt>ZIP code</dt><dd>${esc(p.ca||"Not given")}</dd></div><div><dt>Stage</dt><dd>${STG[p.st]}</dd></div></dl></section>
<section class="panel"><div class="sec-h"><h2>What the permits cover</h2></div><p class="scope">${esc(nbh(p.s))}</p>
<ul class="bps${(p.pm||[]).length>6?" cut":""}" id="bps">${(p.pm||[]).map(x=>`<li><div class="bp-h"><b class="num">${x.l?`<a href="${esc(x.l)}" target="_blank" rel="noopener">${esc(x.n)}<span class="sr"> (opens the City's permit page in a new tab)</span></a>`:esc(x.n)}</b><span>${esc([x.w,x.u?plural(x.u,"home"):"","issued "+day(x.i),x.e?"expires "+day(x.e):""].filter(Boolean).join(", "))}</span></div><p>${esc(nbh(x.s))}</p></li>`).join("")}</ul>
${(p.pm||[]).length>6?`<p class="rec"><button class="btn sm" type="button" id="bpsAll" aria-controls="bps" aria-expanded="false">Show all ${int((p.pm||[]).length)} building permits</button></p>`:""}
${(p.b||0)>(p.pm||[]).length?`<p class="rec">The first ${int((p.pm||[]).length)} of ${int(p.b)} open building permits are shown.</p>`:""}
<p class="rec">From the City's permit text, tidied for reading. ${(p.ms||[p.id]).map(m=>`<a href="${esc(D.record+encodeURIComponent(m))}" target="_blank" rel="noopener">See the City's raw records for master permit ${esc(m)}<span class="sr"> (opens in a new tab)</span></a>`).join(" ")}${p.lat&&p.gs==="census"?" The map pin is from the US Census Bureau's geocoder, because the City record gives no coordinates.":""}</p>
${p.lat&&p.lon?'<div class="minimap" id="minimap" role="region" aria-label="Map of the project location"></div>':""}</section>`:`<p class="ms"><b>City milestone:</b> ${esc(sent(p.m)||"Not given")}. ${STG_LINE[p.st]}</p></section>
<section class="panel"><div class="sec-h"><h2>Permit details</h2></div><dl class="facts">
<div><dt>Reported cost</dt><dd class="num">$${int(p.c)}</dd></div><div><dt>Type</dt><dd>${esc(p.t)}</dd></div><div><dt>Homes</dt><dd class="num">${p.u?int(p.u):"None listed"}</dd></div>${p.sl?`<div><dt>Sleeping units</dt><dd class="num">${int(p.sl)}</dd></div>`:""}<div><dt>Issued</dt><dd>${esc(day(p.i))}</dd></div>
<div><dt>Permit number</dt><dd class="num">${esc(p.id)}</dd></div><div><dt>City permit status</dt><dd>${esc(p.cs||"Not given")}</dd></div><div><dt>Community area</dt><dd>${esc(p.ca||"Not given")}</dd></div><div><dt>Stage</dt><dd>${STG[p.st]}</dd></div></dl></section>
<section class="panel"><div class="sec-h"><h2>What the permit covers</h2></div><p class="scope">${esc(nbh(String(p.sf||p.s).replace(/\s*(\.\.\.|\u2026)$/,"")))}</p>
<p class="rec">From the City's permit text, tidied for reading${/(\.\.\.|\u2026)$/.test(String(p.sf||p.s))?"; shortened here, and the City's record has the rest":""}. <a href="${esc(D.record+encodeURIComponent(p.id))}" target="_blank" rel="noopener">See the City's raw record for permit ${esc(p.id)}<span class="sr"> (opens in a new tab)</span></a></p>
${p.lat&&p.lon?'<div class="minimap" id="minimap" role="region" aria-label="Map of the project location"></div>':""}</section>`}
</div></div>`;
$("#back").onclick=e=>{e.preventDefault();back("#/projects");};
const ba=$("#bpsAll");if(ba)ba.onclick=()=>{const open=$("#bps").classList.toggle("cut");ba.setAttribute("aria-expanded",String(!open));ba.textContent=open?`Show all ${int(p.pm.length)} building permits`:"Show fewer";};
$("#cpy").onclick=async()=>{toast(await copyText(p.a.replace(/ \(\+\d+ more\)$/,"")+where)?"Address copied":"Copy did not work. Press and hold the address.");};
$("#mark").onclick=()=>{const now=mk(p.id).c?"":new Date().toISOString().slice(0,10);const ok=setMark(p.id,{c:now});const btn=$("#mark");btn.classList.toggle("on",!!now);btn.setAttribute("aria-pressed",String(!!now));$("#markT").textContent=now?"Contacted "+day(now)+" (undo)":"Mark as contacted";toast(ok?(now?"Marked as contacted":"Contacted mark removed"):"Not saved: this browser blocks saving");};
const grow=t=>{t.style.height="auto";t.style.height=Math.max(96,t.scrollHeight+2)+"px";};grow($("#nt"));
let tn;$("#nt").addEventListener("input",e=>{grow(e.target);clearTimeout(tn);$("#ntst").textContent="Saving...";tn=setTimeout(()=>{const ok=setMark(p.id,{n:e.target.value});$("#ntst").textContent=ok?"Note saved in this browser":"Not saved. This browser blocks saving here; private browsing is the usual cause.";},400);});
if(p.lat&&p.lon){const mm=()=>{if(!window.L||!$("#minimap"))return;const m2=L.map("minimap",{scrollWheelZoom:false,dragging:!L.Browser.mobile,tap:false,zoomControl:true}).setView([p.lat,p.lon],15);m2.attributionControl.setPrefix('<a href="https://leafletjs.com">Leaflet</a>');tiles(m2);if(p.st===0)L.circleMarker([p.lat,p.lon],{radius:17,color:"#1F4E4A",weight:2.5,fill:false,interactive:false}).addTo(m2);L.circleMarker([p.lat,p.lon],Object.assign({},MS[p.st],{radius:MS[p.st].radius*1.5})).addTo(m2);STATE.mini=m2;};if(window.L)mm();else window.addEventListener("load",mm,{once:true});}}

/* builders */
function viewBuilders(q){document.title="Builders | "+PROD;const s0=q.get("sort")||"near",q0=q.get("q")||"",ph=q.get("phone")==="1";
const all=Object.values(B);
$("#app").innerHTML=`<div class="ph"><div><h1>Builders</h1><p>Every general contractor on this week's list. A ${esc(CITY.key==="austin"?"project":"permit")} with two builders counts for each.</p></div></div>
<div class="tool btool"><label class="search"><span class="sr">Search builders</span>${ico("search")}<input id="bq" type="search" placeholder="Search builder name" value="${esc(q0)}" autocomplete="off"></label>
<div class="fld"><label for="bsort" class="sr">Sort builders</label><select id="bsort"><option value="near">Most near finish</option><option value="n">Most projects</option><option value="cost">Biggest total</option><option value="az">Name, A to Z</option></select></div>
<label class="tog"${CITY.contacts?"":" hidden"}><input type="checkbox" id="bph"${ph?" checked":""}><span>Has contact (${int(all.filter(b=>b.ok).length)})</span></label></div>
<div class="rbar" aria-live="polite"><span id="bcount"></span></div><section class="panel" id="blist"></section>`;
$("#bsort").value=s0;
const draw=()=>{const t=norm($("#bq").value),so=$("#bsort").value,only=$("#bph").checked;
const sorts={near:(a,b)=>b.near-a.near||b.n-a.n||b.cost-a.cost,n:(a,b)=>b.n-a.n||b.cost-a.cost,cost:(a,b)=>b.cost-a.cost,az:(a,b)=>a.name.localeCompare(b.name)};
const rows=all.filter(b=>(!t||t.split(" ").every(w=>norm(b.name).includes(w)))&&(!only||b.ok)).sort(sorts[so]);
const qs=new URLSearchParams();if(t)qs.set("q",$("#bq").value.trim());if(so!=="near")qs.set("sort",so);if(only)qs.set("phone","1");history.replaceState(history.state,"","#/builders"+(qs.toString()?"?"+qs:""));STATE.trail[STATE.trail.length-1]=location.hash;
$("#bcount").innerHTML=`<b class="num">${int(rows.length)}</b> ${rows.length===1?"builder":"builders"}`;
$("#blist").innerHTML=rows.length?`<table class="bt"><caption class="sr">Builders on this week's list</caption><thead><tr>${[["az","Builder",""],["n","Projects","n"],["near","Near finish","n"],["","New","n hm"],["cost",CITY.cost,"n hm"]].map(([k,t,c])=>`<th class="${c}"${k&&k===so?' aria-sort="'+(k==="az"?"ascending":"descending")+'"':""}>${t}${k&&k===so?ico(k==="az"?"up":"down"):""}</th>`).join("")}</tr></thead><tbody>${rows.map(b=>{const h="#/builder/"+encodeURIComponent(b.key);
return `<tr><td class="nm"><a href="${h}"><b>${esc(b.name)}</b><small>${CITY.contacts?(b.ok?ico(b.contact.phone?"phone":"mail","s")+"Contact on file":"No contact on file yet")+(b.area?", mostly "+esc(b.area):""):(b.area?"Mostly in "+esc(CITY.areaLower)+" "+esc(b.area):"")}</small><small class="mob num">${plural(b.n,"project")}${b.near?`, ${int(b.near)} near finish`:""}, ${money(b.cost)}</small></a></td><td class="n num">${int(b.n)}</td><td class="n num${b.near?"":" z"}">${int(b.near)}</td><td class="n num hm${b.nw?"":" z"}">${int(b.nw)}</td><td class="n num hm">${money(b.cost)}</td></tr>`;}).join("")}</tbody></table>`
:`<div class="empty"><h3>No builders match</h3><p>Check the spelling, or search part of the name.</p></div>`;};
$("#blist").onclick=e=>{if(e.target.closest("a"))return;const tr=e.target.closest("tr");const a=tr&&tr.querySelector("a");if(a)go(a.getAttribute("href"));};
let tb;$("#bq").addEventListener("input",()=>{clearTimeout(tb);tb=setTimeout(draw,120);});$("#bsort").onchange=draw;$("#bph").onchange=draw;draw();}
function viewBuilder(b){document.title=`${b.name} | ${PROD}`;const ps=b.ps.slice().sort(ORDER.clean);
$("#app").innerHTML=`<a class="back" href="#/builders" id="back">${ico("back")}Back</a>
<div class="pg"><section class="pg-head"><div class="p-title"><h1>${esc(b.name)}</h1><p class="sub">General contractor on ${plural(b.n,CITY.key==="austin"?"open project":"open permit")}${CITY.bWeek}${b.area?", mostly in "+(CITY.key==="austin"?esc(CITY.areaLower)+" ":"")+esc(b.area):""}</p></div>
<div class="stats"><div><b class="num">${int(b.n)}</b><span>${CITY.key==="austin"?(b.n===1?"open project":"open projects"):(b.n===1?"project":"projects")+" this week"}</span></div><div><b class="num">${money(b.cost)}</b><span>${esc(CITY.totalWord)}</span></div><div><b class="num">${int(b.near)}</b><span>near finish</span></div><div><b class="num">${int(b.nw)}</b><span>new this week</span></div></div></section>
<aside class="pg-side" aria-label="Builder contact">${builderCard(b,ps[0],false,true)}<section class="panel bc"><h2 style="font-size:17px">Pitch kit</h2><p class="meta" style="margin:6px 0 14px">The capability sheet builders ask for, and an email to send after you call.</p><a class="btn" href="#/pitch">${ico("kit","s")}Open the pitch kit</a></section></aside>
<div class="pg-main"><section class="panel"><div class="sec-h"><h2>Their projects<span class="c num">${int(ps.length)}</span></h2><a href="#/projects?q=${encodeURIComponent(b.name)}">Open in Projects</a></div>${[0,1,2].map(st=>{const g=ps.filter(p=>p.st===st);return g.length?`<h3 class="grp">${STG[st]}<span class="c num">${int(g.length)}</span></h3>${rowsHtml(g,0,b.key)}`:"";}).join("")}</section></div></div>`;
$("#back").onclick=e=>{e.preventDefault();back("#/builders");};}

/* terms: the workbook Terms tab's own paragraphs (tools/leads_xlsx.py terms_text) with the City's disclaimer first */
function termsHtml(){const para=t=>{const m=/^([A-Z][A-Za-z ]{1,40}?\.) (.+)$/.exec(t);return m?`<p><b>${esc(m[1])}</b> ${esc(m[2])}</p>`:`<p>${esc(t)}</p>`;};
return `<div class="ph"><div><h1>Terms of Use</h1><p>${esc(TERMS.version)}. The same terms are on the Terms tab of the Excel file.</p></div></div>
<div class="terms"><section class="panel" aria-labelledby="th1"><div class="sec-h"><h2 id="th1">${esc(CITY.cityName)} data</h2></div><div class="tx"><p>${esc(TERMS.city)}</p><p><a href="${esc(TERMS.cityTerms)}" target="_blank" rel="noopener">${esc(CITY.termsLabel)}<span class="sr"> (opens in a new tab)</span></a></p></div></section>
<section class="panel" aria-labelledby="th2"><div class="sec-h"><h2 id="th2">ProofNotFluff</h2></div><div class="tx"><p>${esc(TERMS.notice)}</p>${TERMS.paras.map(para).join("")}</div></section></div>`;}
function viewTerms(){document.title="Terms of Use | "+PROD;
$("#app").innerHTML=`<a class="back" href="#/" id="back">${ico("back")}Back</a>`+termsHtml();$("#back").onclick=e=>{e.preventDefault();back("#/");};}
/* before the list is open, the Terms link on the gate shows the same Terms view, with a way back to the password */
function gateHash(){if(D)return;const t=(location.hash||"")==="#/terms";$("#gateView").hidden=t;$("#gateLegal").hidden=t;$("#app").hidden=!t;$("#appLegal").hidden=!t;
if(t){document.title="Terms of Use | "+PROD;$("#app").innerHTML=`<a class="back" href="#/">${ico("back")}Back to the password</a>`+termsHtml();window.scrollTo(0,0);const h=$("#app h1");h.setAttribute("tabindex","-1");h.focus({preventScroll:true});}
else{$("#app").innerHTML="";document.title="Members: "+PROD+" | ProofNotFluff";}}
window.addEventListener("hashchange",gateHash);gateHash();

/* pitch kit */
function viewPitch(){document.title="Pitch kit | "+PROD;
const sheetTxt=PITCH.sheet.map(([k,v])=>k+": "+v).join("\n"),mailTxt=PITCH.email.join("\n\n");
const fill=s=>esc(s).replace(/\[([^\]]+)\]/g,'<span class="f">[$1]</span>');
$("#app").innerHTML=`<div class="ph"><div><h1>Pitch kit</h1><p>What to send a builder after you call. Copy it, then fill in the parts in blue brackets.</p></div></div>
<div class="pk"><section class="panel"><div class="pk-h"><div><h2>Your one-page capability sheet</h2><p>Builders ask for this before they add you to a bid list.</p></div><button class="btn sm" type="button" data-copy="s">${ico("copy","s")}Copy</button></div><ul class="sheet">${PITCH.sheet.map(([k,v])=>`<li><b>${esc(k)}</b><span>${esc(v)}</span></li>`).join("")}</ul></section>
<section class="panel mail"><div class="pk-h"><div><h2>An email to a builder</h2><p>Send it after you call.</p></div><button class="btn sm" type="button" data-copy="m">${ico("copy","s")}Copy</button></div>${PITCH.email.map(x=>`<p>${fill(x)}</p>`).join("")}</section></div>`;
document.querySelectorAll("[data-copy]").forEach(b=>b.onclick=async()=>{toast(await copyText(b.dataset.copy==="s"?sheetTxt:mailTxt)?"Copied":"Copy did not work. Select the text.");});}

$("#skip").onclick=e=>{e.preventDefault();const t=$("#app").hidden?$("#pw"):($("#app h1")||$("#app"));if(t){t.setAttribute("tabindex",t.id==="pw"?"0":"-1");t.focus();}};
/* gate */
const pw=$("#pw"),eye=$("#eye");pw.addEventListener("input",()=>{pw.removeAttribute("aria-invalid");});
eye.onclick=()=>{const show=pw.type==="password";pw.type=show?"text":"password";eye.setAttribute("aria-pressed",String(show));eye.setAttribute("aria-label",show?"Hide password":"Show password");$("#eyeslash").hidden=!show;pw.focus();};
$("#gate").onsubmit=async e=>{e.preventDefault();const err=$("#err"),btn=$("#go");
if(!pw.value.trim()){err.textContent="Type the password from your Gumroad purchase page.";pw.focus();return;}
btn.disabled=true;btn.textContent="Opening the list...";err.textContent="";
try{const d=await openBox(pw.value.trim());pw.value="";prep(d);
$("#gateView").hidden=true;$("#gateLegal").hidden=true;$("#app").hidden=false;$("#appLegal").hidden=false;$("#tabs").hidden=false;$("#bnav").hidden=false;$("#dlTop").hidden=false;document.body.classList.add("in");
$("#dlTop").onclick=downloadWorkbook;window.removeEventListener("hashchange",gateHash);window.addEventListener("hashchange",onHash);STATE.trail=[location.hash||"#/"];route(true);}
catch(x){btn.disabled=false;btn.textContent="Open this week's list";err.textContent="That password did not open the list. Check your Gumroad purchase page, or reply to your receipt for help.";pw.setAttribute("aria-invalid","true");pw.focus();}};
</script></body></html>
"""


def selftest():
    sys.path.insert(0, HERE)
    import voice_lint
    rows = [{"permit": "101000001", "address": "1 N Main St", "communityArea": "Loop", "type": "Renovation", "scope": "Interior <b>alterations</b>",
             "scopeFull": "Interior <b>alterations</b> to floors 2 to 5", "cost": 1988677, "units": None, "issued": "2025-12-01",
             "gc": ["Acme Builders LLC", "Beta Electric Inc"], "milestone": "Certificate Of Occupancy Pending (Temporary Or Partial Occupancy Approved)",
             "status": "Active", "lat": 41.88, "lon": -87.63, "newThisWeek": False},
            {"permit": "101000002", "address": "2 N Main St", "communityArea": "Loop", "type": "New construction", "scope": "Erect", "cost": 600000,
             "units": 40, "issued": "2026-10-14", "gc": ["Acme Builders, L.L.C."], "milestone": "Permit Issued (Fee Due)", "status": "Active",
             "lat": None, "lon": None, "newThisWeek": True}]
    prepped = [prep(p) for p in rows]
    html = build_html(prepped, dt.date(2026, 10, 17), b"PK", "correct horse battery")
    assert "<b>alterations</b>" not in html and "Acme" not in html and "1 N Main" not in html, "row data must stay inside the ciphertext"
    assert 'name="robots" content="noindex' in html and "List of Oct 17, 2026" in html
    text_only = re.sub(r"<[^>]+>", "", html).replace("&#x27;", "'")
    assert text_only.count(LEGAL.replace("__ASOF__", "Oct 17, 2026")) == 2, "the legal line must appear word for word on the gate and in the footer"
    assert html.count('<a href="#/terms">Terms of Use</a>') == 2, "the gate and the footer link to the Terms view"
    terms = json.loads(re.search(r"const TERMS=(\{.*?\});\n", html).group(1))
    import leads_xlsx
    assert [terms["version"]] + terms["paras"] == leads_xlsx.terms_text("Oct 17, 2026"), "the Terms view must be the workbook's own paragraphs"
    assert "Version 2, Oct 17, 2026" in terms["version"] and terms["city"] == leads_xlsx.CITY_DISCLAIMER and terms["notice"] == leads_xlsx.OUR_NOTICE
    assert any(p.startswith("Accuracy.") and "not City data" in p for p in terms["paras"]) and any("OpenStreetMap" in p for p in terms["paras"])
    assert 'v==="terms"' in html and "function viewTerms()" in html and "function gateHash()" in html
    assert "and the builder's office phone or email where their own website lists one." in html and "how to reach them" not in html
    assert "we found no website that is clearly theirs, or their site does not show them." in html
    for u, h in (LEAFLET_JS, LEAFLET_CSS):
        assert re.search(r"/leaflet/\d+\.\d+\.\d+/", u) and h.startswith("sha256-") and h in html and u in html
    assert "openstreetmap.org/copyright" in html, "map attribution"
    box = json.loads(re.search(r"const BOX=(\{.*?\});", html).group(1))
    assert box["rounds"] == 250_000 and box["kdf"] == "PBKDF2-SHA256"
    d = json.loads(decrypt("correct horse battery", box))
    assert [p["st"] for p in d["projects"]] == [0, 2] and d["projects"][1]["n"] is True and d["projects"][0]["n"] is False
    assert d["projects"][0]["g"] == ["acmebuildersllc", "betaelectricinc"] and d["projects"][1]["g"] == ["acmebuildersllc"], "one builder key for both spellings"
    assert set(d["builders"]) == {"acmebuildersllc", "betaelectricinc"} and d["projects"][0]["sf"].endswith("floors 2 to 5")
    assert d["projects"][1]["gn"] == ["Acme Builders, L.L.C."] and d["builders"]["acmebuildersllc"]["name"] == "Acme Builders LLC", "each permit keeps its own spelling"
    assert '"Builder","All builders"' in html and 'p.g.map((k,i)=>pn(p,i)).join("; ")' in html, "the CSV exports every builder"
    try:
        decrypt("wrong password", box)
        raise AssertionError("wrong password decrypted")
    except AssertionError:
        raise
    except Exception:
        pass
    # a contact entry is cleaned before it reaches the page: only http(s) links, a real email, digits for tel:
    global contact_for
    real = contact_for
    contact_for = lambda name, verified_only=True: {"status": "verified", "phone": "(312) 555-0100 ext. 4", "email": "info@acme.example",
                                                     "website": "javascript:alert(1)", "contactPage": "https://acme.example/contact",
                                                     "source": "https://acme.example/contact", "checkedAt": "2026-10-17", "note": "main office;"}
    try:
        c = contact("Acme Builders LLC")
        assert c["tel"] == "3125550100" and c["website"] == "" and c["contactPage"].startswith("https://") and c["note"] == "main office", c
        # suffix-free fallback only for a lone entity: PANOPTIC GROUP LLC and PANOPTIC GROUP INCORPORATED stay apart (holdout, Oct 18)
        contact_for = lambda name, verified_only=True: {"name": "Panoptic Group LLC", "status": "verified", "phone": "(312) 555-0101"}
        pan = [{"permit": "1", "address": "1 A St", "cost": 1_000_000, "gc": ["Panoptic Group LLC"], "milestone": "Inspections"},
               {"permit": "2", "address": "2 A St", "cost": 2_000_000, "gc": ["Panoptic Group Incorporated"], "milestone": "Inspections"}]
        pb = payload([prep(x) for x in pan], dt.date(2026, 10, 17), b"")["builders"]
        assert set(pb) == {"panopticgroupllc", "panopticgroupinc"}, set(pb)
        assert pb["panopticgroupllc"]["contact"] and pb["panopticgroupinc"]["contact"] is None, pb
        assert contact("Panoptic Group Inc", 1)["phone"] == "(312) 555-0101", "a lone entity may use the suffix-free entry"
    finally:
        contact_for = real
    review = [{"permit": "101000003", "kept": True, "raw": "INTERIOR ALTERATIONS TO 8TH FLOOR OFFICE SPACE. NEW RESTROOMS. PLAN REVIEWER JANE DOE",
               "cost": 750000.0, "type": "PERMIT - RENOVATION/ALTERATION", "gcRaw": ["ACME BUILDERS LLC", "JOHN SMITH"], "issued": "2026-10-15",
               "address": "3 N Main St", "status": "Active", "milestone": "Inspections", "communityArea": "Loop", "lat": 41.9, "lon": -87.6},
              {"permit": "101000005", "kept": True, "raw": "INTERIOR ALTERATIONS TO 3RD FLOOR OFFICE SPACE", "cost": 600000.0,
               "type": "PERMIT - RENOVATION/ALTERATION", "gcRaw": ["3312 LINCOLN LLC", "MANGAN BUILDERS, INC."],
               "gcType": ["Owner/General Contractor", "Contractor-General Contractor"], "issued": "2026-01-02", "address": "5 N Main St",
               "status": "Active", "milestone": "Inspections", "communityArea": "Loop"},
              {"permit": "101000004", "kept": False, "raw": "ROOF REPLACEMENT", "cost": 900000.0, "type": "PERMIT - RENOVATION/ALTERATION", "gcRaw": [],
               "issued": "2026-01-01", "address": "4 N Main St", "status": "Active", "milestone": "Inspections", "communityArea": "Loop"}]
    ps = projects_from_review(review, dt.date(2026, 10, 17))
    owner = [p for p in ps if p["permit"] == "101000005"]
    assert owner and owner[0]["gc"] == ["Mangan Builders, Inc."], "an owner acting as general contractor is never listed"
    ps = [p for p in ps if p["permit"] != "101000005"]
    assert len(ps) == 1 and ps[0]["gc"] == ["Acme Builders LLC"] and ps[0]["newThisWeek"] and "Jane" not in ps[0]["scopeFull"], ps
    assert "restrooms" in ps[0]["scopeFull"].lower()
    # short money: halves round up on whole dollars, the same in the app, the v1 page and the free page (Holdout, Oct 18)
    import importlib, shutil, subprocess
    ms = importlib.import_module("make_site")
    import leads_page
    cases = {950: "$1K", 9950: "$10K", 999499: "$999K", 999500: "$1.0M", 999950: "$1.0M", 1150000: "$1.2M", 62550000: "$62.6M",
             8450000: "$8.5M", 99949999: "$99.9M", 99950000: "$100M", 190000000: "$190M", 770000: "$770K", 5279012: "$5.3M"}
    for v, want in cases.items():
        assert ms.money(v) == want, (v, ms.money(v), want)
    assert ms.money(2_950_000_000, True) == "$3.0 billion" and ms.money(2_850_000_000, True) == "$2.9 billion"
    node = shutil.which("node")
    if node:
        for src in (PAGE, leads_page.PAGE):
            fns = "\n".join(m.group(0) for m in re.finditer(r"^(?:const int=|function money\(n\)|function bigMoney\(n\)).*$", src, re.M))
            js = fns + "\nconsole.log(JSON.stringify(%s.map(n=>money(n)).concat([bigMoney(2950000000),bigMoney(2850000000)])))" % json.dumps(list(cases))
            got = json.loads(subprocess.run([node, "-e", js], capture_output=True, text=True, check=True).stdout)
            assert got == list(cases.values()) + ["$3.0 billion", "$2.9 billion"], got
        # Austin (design director, Oct 18): $1 billion and up as "$1.57 billion", the same in the app and on the free page
        fns = "\n".join(m.group(0) for m in re.finditer(r"^(?:const int=|function money\(n\)|function bigMoney\(n\)).*$", PAGE, re.M))
        bcases = [1567000000, 994000000, 995000000, 6667343254, 999499]
        js = "const CITY={bil2:true};" + fns + "\nconsole.log(JSON.stringify(%s.map(n=>money(n)).concat([bigMoney(6667343254)])))" % json.dumps(bcases)
        got = json.loads(subprocess.run([node, "-e", js], capture_output=True, text=True, check=True).stdout)
        want = ["$1.57 billion", "$994M", "$1.00 billion", "$6.67 billion", "$999K", "$6.67 billion"]
        assert got == want and [ms.money(v, bil2=True) for v in bcases] == want[:5], (got, [ms.money(v, bil2=True) for v in bcases])
        # CSV export: the formula guard quotes text that starts with = + - @, but plain numbers such as longitudes stay numbers
        fn = re.search(r"^function cell\(v\).*$", PAGE, re.M).group(0)
        cells = [-87.637533, "-87.637533", 41.88, 1988677, "=SUM(A1)", "-1 call first", "+1 312", "@x", "", None, 'say "hi", then']
        js = fn + "\nconsole.log(JSON.stringify(%s.map(cell)))" % json.dumps(cells)
        got = json.loads(subprocess.run([node, "-e", js], capture_output=True, text=True, check=True).stdout)
        assert got == ["-87.637533", "-87.637533", "41.88", "1988677", "'=SUM(A1)", "'-1 call first", "'+1 312", "'@x", "", "",
                       '"say ""hi"", then"'], got
    else:
        print("node not found: browser money format and CSV cells not checked here")
    # Austin: the same page with the City of Austin's words; no builder contacts promised, no Chicago word left
    import leads_cities
    au = json.load(open(os.path.join(ROOT, "permits", "austin", "sample.json")))
    use("austin")
    try:
        arows = [prep(dict(p, newThisWeek=False)) for p in au["projects"]]
        ahtml = build_html(arows, dt.date(2026, 10, 18), b"PK", "correct horse battery")
        atext = re.sub(r"<[^>]+>", "", ahtml).replace("&#x27;", "'")
        assert atext.count(leads_cities.AUSTIN["legal"].replace("__ASOF__", "Oct 18, 2026").replace("\u2019", "\u2019")) == 2, "Austin legal line twice"
        assert ahtml.count('<a href="#/terms">Terms of Use</a>') == 2 and "Members: Austin Construction Cleaning Leads" in ahtml
        assert "phone or email where their own website lists one" not in ahtml and "Chicago" not in re.sub(r"const CITY=\{.*?\};", "", ahtml.split("<script>")[0])
        at = json.loads(re.search(r"const TERMS=(\{.*?\});\n", ahtml).group(1))
        assert at["city"] == leads_cities.AUSTIN["disclaimer"] and "City of Austin" in at["paras"][2] and at["cityTerms"].endswith("ranj-cccq")
        ad = json.loads(decrypt("correct horse battery", json.loads(re.search(r"const BOX=(\{.*?\});", ahtml).group(1))))
        assert ad["fileName"].startswith("austin-construction-cleaning-leads-") and ad["record"].endswith("masterpermitnum=")
        assert all(b["contact"] is None for b in ad["builders"].values()) and all("b" in p for p in ad["projects"])
        assert {p["st"] for p in ad["projects"]} <= {0, 1, 2}
    finally:
        use("chicago")
    text = PAGE + LEGAL + leads_cities.AUSTIN["legal"]
    assert "—" not in text, "em dash"
    for w in ("honestly", "genuinely", "straightforward", "delve", "unlock ", "elevate", "seamless", "game-changer", "effortless", "supercharge"):
        assert w not in text.lower(), w
    copy = re.sub(r"<[^>]+>|\$\{[^}]*\}", " ", text)
    tells = voice_lint.tells(copy)
    assert not tells, tells
    print("leads_app selftest ok")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--selftest"]:
        selftest()
    else:
        pw_file = ""
        if "--pw-file" in args:
            i = args.index("--pw-file")
            pw_file, args = args[i + 1], args[:i] + args[i + 2:]
        full = json.load(open(args[0])) if args[:1] != ["--from-review"] else None
        austin = bool(full) and LC.for_source(full.get("source"))["key"] == "austin"
        env = "AUSTIN_LEADS_PASSWORD" if austin else "LEADS_PASSWORD"   # each product has its own members' password
        pw = open(pw_file).read().strip() if pw_file else os.environ.get(env, "")
        if len(pw) < 12:
            raise SystemExit(f"{env} missing or shorter than 12 characters; nothing written")
        if contacts_password and not austin:
            contacts_password(pw)   # the encrypted contacts file uses the same members' password
        if args[:1] == ["--from-review"]:
            print(from_review(args[1], args[2], pw))
        else:
            print(build(full, args[1], args[2], pw))
