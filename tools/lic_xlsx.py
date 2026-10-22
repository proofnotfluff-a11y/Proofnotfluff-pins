#!/usr/bin/env python3
"""Chicago New Business Licenses: the weekly workbook (WORKBOOK_STANDARD v3, the same card language as the restaurant
product's tools/rest_xlsx.py and the construction product's tools/leads_xlsx.py, whose card helpers this reuses).

Tabs: Start Here, one tab per trade (1 Food and drink to 6 Day care), Pitch kit, Terms. Built from the members' full
list that tools/licenses_chicago.py --full writes in the runner, so it matches the members' app row for row. Business
fields only: the name the City shows, the site address, the City's license type, business activity and issue date, the
community area, and what the City's own records add (earlier licenses for the same business, a food license inspection).

This file is the one source of the product's shared words: the trades, the left-out sentence, the pitch kit, the Terms
of Use and the City's Data Terms of Use (read from the Legal desk's snapshot, permits/licenses-chicago/city-terms.json).
The members' app (tools/lic_app.py) imports them, so the two cannot drift.

Usage: python3 tools/lic_xlsx.py FULL.json OUT.xlsx        (FULL from tools/licenses_chicago.py --full)
       python3 tools/lic_xlsx.py --terms-check TERMS.txt   stop when the City's fetched terms differ from the snapshot
       python3 tools/lic_xlsx.py --selftest
"""
import datetime as dt, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import wb_style as S  # noqa: E402
import pnf_dash as D  # noqa: E402
from leads_xlsx import _FUNCS, _flat, cache_values, card_sheet  # noqa: E402
from rest_xlsx import blue, card, lead_para  # noqa: E402
from openpyxl.styles import Alignment, Border  # noqa: E402
from openpyxl.utils import get_column_letter as gl  # noqa: E402

PRODUCT = "Chicago New Business Licenses"
VERSION = "Version 1, Oct 22, 2026"
CITY_TERMS_FILE = os.path.join(ROOT, "permits", "licenses-chicago", "city-terms.json")
RECORD = "https://data.cityofchicago.org/resource/r5kz-chrr.json?license_number="
RESTAURANT = "Chicago Restaurant Inspection Leads"

# ---------------------------------------------------------------- trades (keys from tools/licenses_chicago.py SEGMENTS)
from licenses_chicago import TRADES  # noqa: E402  (key, tab, short label, kinds: one source with the free page)
TAB = {k: t for k, t, _, _ in TRADES}
SHORT = {k: s for k, _, s, _ in TRADES}
KINDS = {k: w for k, _, _, w in TRADES}
ORDER = [k for k, _, _, _ in TRADES]
FOOT = "Public City of Chicago business license records. See the Terms tab."

# What the City's earlier records say about the business (tools/licenses_chicago.py add_history)
HISTORY = {"first": "First license", "site": "New site", "added": "Added license", "": "Not checked"}
HISTORY_LONG = {"first": "No Chicago license on the City's record for this business before the last 30 days (the record starts in 2002).",
                "site": "The business held a Chicago license at another site before the last 30 days, so this is a new location. "
                        "Since: the year of its first Chicago license.",
                "added": "The business held a license at this site before the last 30 days; this one adds a new license type there. "
                         "Since: the year of its first license at this site.",
                "": "The City's earlier records were not checked this week."}


def history_text(r):
    h, y = r.get("history") or "", r.get("since") or ""
    if h == "site" and y:
        return f"New site, licensed in Chicago since {y}"
    if h == "added" and y:
        return f"Added license, here since {y}"
    return HISTORY[h]


LEFT_OUT = ("Renewals and changes (including an older license the City re-dated), cancelled or revoked licenses, and licenses "
            "held by a person or for an event or a season are left out: peddler, special event, pop-up, raffle, tow truck, valet, "
            "chauffeur, home-sharing, vacation rental, bed-and-breakfast, mobile food, shared kitchen user, home occupation, home "
            "repair, massage therapist, body art practitioner, scavenger and expediter licenses, and street performers, flea "
            "market vendors and market stalls. So are home and mail-drop addresses: businesses the City marks as home based, "
            "addresses with an apartment number, upper-floor units in a building where the City has licensed home-based "
            "businesses, private mailboxes, and addresses with a City virtual office license. Office and shop suites stay. "
            "Sites outside Chicago are left out, and so is any business whose shown name could be a person's name: two to four "
            "plain words with no business word, with or without LLC or Inc, such as \"Golden Dragon\". "
            "That check leaves some real businesses out on purpose, because a wrong omission costs less than printing a "
            "person's name. A business with two licenses at one site is listed once. If a business on the list goes by a "
            "person's name, or asks to be left out, write to hello@proofnotfluff.com and it is removed from every later list.")

OVERLAP = ("Food businesses usually get a City food license inspection before the City issues their food license, and "
           f"{RESTAURANT} lists those inspections as Opening soon. A food and drink row here with a date under Food license "
           "inspection had that inspection in the 120 days before its license, so a member of both products most likely saw the "
           "business there first. The other food rows, and nearly all businesses in the other trades, are not on the "
           "restaurant product.")
OPEN_BEFORE = ("Food inspections since: the year of the City's earliest routine or complaint food inspection on file for the "
               "business before this license. It shows the business was open before the license was issued.")

OUR_NOTICE = ("For general business information only. Businesses appear because their licenses are public City of Chicago "
              "records. A new license shows the City issued it on that date; it does not say the business is open, hiring or "
              "buying anything. No business listed has endorsed or works with ProofNotFluff. You make your own calls, visits "
              "and emails, and you are responsible for following the law when you do. ProofNotFluff never contacts businesses "
              "or anyone else on your behalf.")

# ---------------------------------------------------------------- the pitch kit (one source: the app reads it too)
# [Brackets] are the parts the member fills in. Every opener names the City's public license record and its date, never
# a claim that the business is open, struggling or in need of anything.
PITCH = [
    {"key": "clean", "buyer": "Commercial cleaning", "short": "Cleaning",
     "call": "Hi, this is [your name] with [company], a commercial cleaning company in Chicago. I saw the City issued [business] "
             "a new [license type] license on [date], and new sites are often still choosing a cleaner. We clean [kind of "
             "business] in [community area] on a schedule that fits your hours. Who looks after that for you?",
     "email": ["Subject: Cleaning for [business] at [address]",
               "Hi [business] team, I'm [your name] with [company]. City of Chicago records show a new [license type] license "
               "for [address] on [date]. We clean [kind of business] across Chicago, nightly or weekly, and can walk the space "
               "this week to give you a quote. Is there a good day?",
               "[Your name], [company], [phone]"]},
    {"key": "pest", "buyer": "Pest control", "short": "Pest control",
     "call": "Hi, this is [your name] with [company], a licensed pest control company in Chicago. I saw the City issued [business] "
             "a new [license type] license on [date]. We set new [kind of business] up with a service plan and a written service "
             "record from the first visit. Is the owner or manager around for two minutes?",
     "email": ["Subject: Pest control for [business]",
               "Hi [business] team, I'm [your name] with [company], a licensed pest control company working across Chicago. City "
               "of Chicago records show a new [license type] license for [address] on [date].",
               "We can inspect this week, seal entry points and leave a dated service record. Would [day] work for a visit?",
               "[Your name], [company], [phone], Illinois structural pest control license [number]"]},
    {"key": "any", "buyer": "Any vendor to new businesses (POS, signs, insurance, bookkeeping, waste, supplies)", "short": "Other vendors",
     "call": "Hi, this is [your name] with [company]. I saw the City issued [business] a new [license type] license on [date], "
             "so you may be setting up your accounts. We help new Chicago businesses with [your service]. Who is putting the "
             "vendors together?",
     "email": ["Subject: [Your service] for [business]",
               "Hi [business] team, I'm [your name] with [company]. City of Chicago records show a new [license type] license for "
               "[address] on [date]. We set new Chicago businesses up with [your service], usually within [days] of the first "
               "call. Could I send a short quote?",
               "[Your name], [company], [phone]"]},
]
PITCH_RULES = ["Name the City's license and its date, and stop there. Don't say the business is open, new to Chicago or in need "
               "of your service unless it tells you so.",
               "Keep every claim about your company true, and never say you work with the City.",
               "One call and one email per business. Honor any request to stop, and follow the law on calls and email."]


# ---------------------------------------------------------------- the City's Data Terms of Use (word for word)
def parse_city_terms(text):
    """[(heading, [paragraph])] from the fetched terms page (permits/licenses-chicago/source-terms.txt): every line from
    DISCLAIMER OF LIABILITY up to the City site's menu, headings in capitals. None when the page did not parse."""
    lines = [x.strip() for x in (text or "").split("\n")]
    if "DISCLAIMER OF LIABILITY" not in lines:
        return None
    i = lines.index("DISCLAIMER OF LIABILITY")
    j = lines.index("I Want To", i) if "I Want To" in lines[i:] else len(lines)
    out = []
    for x in lines[i:j]:
        if not x:
            continue
        if re.fullmatch(r"[A-Z][A-Z ,]+", x):
            out.append([x, []])
        elif out:
            out[-1][1].append(x)
    heads = [h for h, _ in out]
    need = ["DISCLAIMER OF LIABILITY", "USE OF DATA", "RESERVATION OF RIGHTS", "INDEMNITY"]
    return out if all(h in heads for h in need) and all(p for _, p in out) else None


def city_terms():
    """The Legal desk's snapshot: {"url", "checked", "sections": [[heading, [paragraph]]]}."""
    return json.load(open(CITY_TERMS_FILE, encoding="utf-8"))


def city_disclaimer():
    """The disclaimer the City's terms require at the site, word for word, taken from the terms themselves."""
    for h, paras in city_terms()["sections"]:
        for p in paras:
            if p.startswith("“This site provides applications"):
                return p.strip("“”")
    raise SystemExit("the City's required disclaimer is missing from city-terms.json")


def terms_check(path):
    """Stop the weekly build when the City's freshly fetched terms differ from the snapshot the Legal desk cleared. A fetch
    that failed keeps the snapshot (the page was not read, so nothing is known to have changed)."""
    text = open(path, encoding="utf-8").read()
    if text.startswith("Could not fetch"):
        print("City terms not fetched this week; the Legal desk's snapshot stays")
        return True
    fresh = parse_city_terms(text)
    snap = city_terms()["sections"]
    norm = lambda secs: [[h, [re.sub(r"\s+", " ", p) for p in ps]] for h, ps in secs]
    if fresh is None or norm(fresh) != norm(snap):
        raise SystemExit("The City of Chicago changed its Data Terms of Use (or the page no longer parses). The members' list "
                         "is not built until the Legal desk reviews the new terms and updates permits/licenses-chicago/city-terms.json.")
    print("City terms unchanged since the Legal desk's snapshot")
    return True


def terms_text(date):
    """Our Terms of Use (legal/README.md clause library, adapted for a monthly membership like the restaurant product's).
    One source: the workbook's Terms tab and the members' app's #/terms view are both built from this list."""
    return [
        f"ProofNotFluff | {PRODUCT} | {VERSION} | List of {date}",
        "License. Your membership gives you a license to use this list for one business you own, for its own sales prospecting. You "
        "may edit it and print it for that use. You may not resell, share, give away, upload, publish or redistribute it, in original "
        "or edited form, or use it to make a competing product.",
        "Ownership. The selection, layout, trades, text and formulas belong to ProofNotFluff. The license records themselves are public "
        "City of Chicago data. Buying a membership doesn't transfer ownership.",
        "Accuracy. The list is built from the City of Chicago's Business Licenses data as of the list date above. City data can be "
        "late, incomplete or wrong. A new license shows the City issued it on that date. Most go to new businesses, but a business "
        "that opens another site, or adds a new license type at a site it already has, gets one too; the On the City's record column "
        "reads the City's earlier licenses for the same business to tell these apart. The trades are ProofNotFluff's sorting of the "
        "City's license type and business activity, not the City's labels. Confirm anything you rely on with the business or the City.",
        "Who is left out. " + LEFT_OUT,
        "What the list does not say. A business on the list holds a new City license. The list does not say it is open, hiring or "
        "buying, or that it needs any service. Don't present the list, or anything in it, as a judgment about a business.",
        "No promise of results. Counts and trades are figures from City records. Nothing here promises any work, contract, income or "
        "outcome.",
        "Availability. The list depends on the City of Chicago publishing its business license data. If the City stops or changes that "
        "data, or asks us to stop using it, the list may pause or end, and future charges will stop. The map uses OpenStreetMap's free "
        "public map service, which can limit or stop access at any time; the list and downloads work without it. Map data © "
        "OpenStreetMap contributors.",
        "No warranty. The product is provided \"as is\", without warranties of any kind, to the extent the law allows.",
        "Limit of liability. To the extent the law allows, ProofNotFluff is not liable for any loss or damage from using or relying on "
        "this product, and its total liability for any claim is limited to the amount you paid for the most recent month of your "
        "membership. Nothing here limits rights you have under consumer protection laws that can't be waived.",
        "Trademarks. Microsoft Excel, Google Sheets, Google Maps, OpenStreetMap and Gumroad are trademarks of their owners, and business "
        "names on the list belong to those businesses. ProofNotFluff isn't affiliated with, sponsored or endorsed by them, by the City "
        "of Chicago, or by any business listed.",
        "AI assistance. This product was made with AI assistance and reviewed and tested by the shop owner.",
        "Help and cancelling. If the file won't open or something looks wrong, reply to your Gumroad receipt and it will be fixed. Cancel "
        "any time from your Gumroad receipt or library; cancelling stops future charges.",
    ]


# ---------------------------------------------------------------- helpers
def day(s):
    try:
        return dt.date.fromisoformat((s or "")[:10])
    except ValueError:
        return None


def pretty(s):
    d = day(s)
    return f"{d.strftime('%b')} {d.day}, {d.year}" if d else ""


def as_of_text(full):
    return pretty(full["source"]["fetchedAt"][:10])


def by_trade(full):
    """{trade: [records]} newest first, A to Z within a day. One order for the app and the workbook."""
    out = {k: [] for k in ORDER}
    for r in full["records"]:
        out.setdefault(r["segment"], []).append(r)
    for k in out:
        out[k].sort(key=lambda r: (-int(r["issued"].replace("-", "")), r["business"].upper(), r["address"]))
    return out


def is_new(r, full):
    return r["issued"] >= full["window"]["from"]


_FUNCS.setdefault("COUNT", lambda *a: sum(1 for v in _flat(a) if isinstance(v, (int, float, dt.date)) and not isinstance(v, bool)))

WRAP = ("name", "address", "area", "type", "activity", "history", "also")


def data_sheet(wb, key, rows, list_date, food):
    """One trade's tab: a stat strip with the ink answer tile, then the table (WORKBOOK_STANDARD v3, rest_xlsx's layout)."""
    cols = ([("name", "Business", 26, "left", None), ("address", "Address", 24, "left", None), ("area", "Community area", 16, "left", None),
             ("issued", "Licensed", 13, "left", "date"), ("type", "License type", 22, "left", None),
             ("activity", "Business activity", 30, "left", None), ("history", "On the City's record", 22, "left", None)]
            + ([("food", "Food license inspection", 14, "left", "date"), ("since", "Food inspections since", 11, "left", None)] if food else [])
            + [("new", "New this week", 9, "center", None), ("also", "Other licenses here", 22, "left", None),
               ("zip", "ZIP", 8, "left", None), ("license", "License", 11, "left", None), ("record", "City record", 11, "left", None)])
    print_cols = 8 if food else 7
    ws = wb.create_sheet(TAB[key])
    letters = [gl(i + 3) for i in range(len(cols))]
    pad_r, gut_r = gl(len(cols) + 3), gl(len(cols) + 4)
    S.set_widths(ws, {"A": 3, "B": 2, **{l: c[2] for l, c in zip(letters, cols)}, pad_r: 2, gut_r: 3})
    D.page_header(ws, SHORT[key], f"{KINDS[key]} with a new City license in the last 30 days. Newest first.", list_date,
                  span=("B", pad_r), side_cols=3)
    top = 10
    first, last = top + 2, top + 2 + max(len(rows), 1) - 1
    col = {c[0]: l for l, c in zip(letters, cols)}
    rng = {k: f"{l}{first}:{l}{last}" for k, l in col.items()}
    stats = [("Businesses", f'=COUNTIF({rng["name"]},"?*")'), ("New this week", f'=COUNTIF({rng["new"]},"New")'),
             ("First license", f'=COUNTIF({rng["history"]},"First license")')]
    if food:
        stats.append(("Food license inspection", f'=COUNT({rng["food"]})'))
    D.h(ws, 6, 10)
    k = len(stats)
    widths = [c[2] for c in cols[:print_cols]]
    total, acc, cuts = sum(widths), 0, []
    for w in widths:
        acc += w
        cuts.append(acc)
    starts = [0] + [min(range(len(cuts)), key=lambda j: abs(cuts[j] - total * i / k)) + 1 for i in range(1, k)]
    lastc = letters[print_cols - 1]
    groups = [f"{letters[starts[i]]}:{letters[starts[i + 1] - 1] if i < k - 1 else lastc}" for i in range(k)]
    D.stat_strip(ws, 7, [(g, e, fml, S.FMT["int"]) for g, (e, fml) in zip(groups, stats)])
    a, z = groups[0].split(":")
    for rr in range(6, 10):
        for c in [gl(i) for i in range(2, letters.index(z) + 4)]:
            ws[f"{c}{rr}"].fill = D.fill("ink")
    for g in groups[1:]:
        for rr in (7, 8):
            c = ws[f"{g.split(':')[0]}{rr}"]
            c.alignment = Alignment(horizontal="left", vertical=c.alignment.vertical, indent=1)
    ws[f"{a}7"].font = D.f(8, True, "on_ink_soft")
    ws[f"{a}8"].font = D.f(22, True, "on_ink")
    D.h(ws, 9, 10)
    D.frame(ws, 6, 9, "B", pad_r)
    spec = []
    for l, (ck, head, w, align, fmt) in zip(letters, cols):
        vals = [r.get(ck) for r in rows]
        spec.append({"col": l, "head": head, "kind": "text", "values": [None if v in ("", None) else v for v in vals], "align": align,
                     "fmt": "mmm d, yyyy" if fmt == "date" else None, "bold": ck == "name"})
    f1, f2, end = D.table_card(ws, top, "B", pad_r, spec, max(len(rows), 1), row_height=30)
    head = f1 - 1
    D.h(ws, head, 30)
    for l, (ck, head_, w, align, fmt) in zip(letters, cols):
        ws[f"{l}{head}"].alignment = Alignment(horizontal=align, vertical="bottom", wrap_text=True, indent=1 if align == "right" else 0)
    if not rows:
        ws[f"{letters[1]}{f1}"] = "None in the last 30 days."           # not in the Business column, so no count includes it
        ws[f"{letters[1]}{f1}"].font = D.f(10, False, "muted")
    for i, r in enumerate(rows):
        rr = f1 + i
        need = 30
        for l, (ck, head_, w, align, fmt) in zip(letters, cols):
            c = ws[f"{l}{rr}"]
            c.alignment = Alignment(horizontal=align, vertical="center", wrap_text=ck in WRAP)
            if ck in ("area", "zip") and not r.get(ck):
                c.value = "Not given"; c.font = D.f(10, False, "muted")
            elif ck == "food" and not r.get(ck):
                c.value = None
            elif ck == "history":
                c.font = D.f(10, r.get("hist") == "first", "teal" if r.get("hist") == "first" else "ink2")
            elif ck in ("address", "area", "issued", "type", "activity", "license", "zip", "food"):
                c.font = D.f(10, False, "ink2")
            elif ck == "also" and r.get(ck):
                c.font = D.f(9, False, "ink2")
            elif ck == "new" and r.get(ck):
                c.font = D.f(9, True, "accent")
            elif ck == "record" and r.get("recordUrl"):
                c.hyperlink = r["recordUrl"]; c.font = D.f(10, False, "blue", underline="single")
            if ck in WRAP and c.value:
                need = max(need, S.text_height(str(c.value), w, 10, bold=ck == "name") + 8)
        D.h(ws, rr, need)
    if rows:
        ws.auto_filter.ref = f"{letters[0]}{head}:{letters[-1]}{f2}"
    D.paint_canvas(ws, end + 1, gl(len(cols) + 6))
    S.finish_sheet(ws, PRODUCT, end, span=("A", gut_r), freeze=f"{letters[1]}{f1}", protect=False, footer_notice=FOOT,
                   tab_color="accent" if key == "food" else "teal" if key in ("retail", "beauty") else None, canvas_cols=gl(len(cols) + 6))
    ws.print_area = f"A1:{gl(print_cols + 2)}{end}"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_LEGAL
    ws.page_setup.fitToWidth = 1
    ws.page_margins.left = ws.page_margins.right = 0.3
    ws.print_title_rows = f"{head}:{head}"
    return ws, col


def finish_card(ws, r, tab):
    D.paint_canvas(ws, r, "S")
    S.finish_sheet(ws, PRODUCT, r - 1, span=("A", "Q"), protect=False, canvas_cols="S", footer_notice=FOOT, tab_color=tab)


def row_of(r, full):
    return {"name": r["business"], "address": r["address"], "area": r.get("communityArea") or "", "issued": day(r["issued"]),
            "type": r["licenseType"], "activity": r.get("activity") or "", "history": history_text(r), "hist": r.get("history") or "",
            "food": day(r.get("foodInsp")), "since": r.get("inspSince") or "", "new": "New" if is_new(r, full) else "", "also": "; ".join(r.get("otherTypes") or []),
            "zip": r.get("zip") or "", "license": r["license"], "recordUrl": RECORD + r["license"], "record": "City record"}


# ---------------------------------------------------------------- build
def build(full, out):
    list_date = f"List of {as_of_text(full)}"
    wb = S.new_workbook(PRODUCT)
    groups = by_trade(full)
    counts, cols = {}, {}
    for k in ORDER:
        rows = [row_of(r, full) for r in groups.get(k, [])]
        _, cols[k] = data_sheet(wb, k, rows, list_date, food=k == "food")
        counts[k] = len(rows)
    pitch_kit(wb, list_date)
    terms(wb, full, list_date)
    start_here(wb, full, list_date, counts, cols)
    wb.active = 0
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and ("—" in c.value or "–" in c.value):
                    raise SystemExit(f"em or en dash in {ws.title}!{c.coordinate}")
    wb.save(out)
    cache_values(out)
    return counts


def start_here(wb, full, list_date, counts, cols):
    ws = card_sheet(wb, "Start Here", PRODUCT, "New Chicago business licenses from the last 30 days, sorted by trade.",
                    list_date, "teal", position=0)
    rng = lambda k, key: f"'{TAB[k]}'!{cols[k][key]}12:{cols[k][key]}{11 + max(counts[k], 1)}"
    total = "=" + "+".join(f'COUNTIF({rng(k, "name")},"?*")' for k in ORDER)
    new = "=" + "+".join(f'COUNTIF({rng(k, "new")},"New")' for k in ORDER)
    first = "=" + "+".join(f'COUNTIF({rng(k, "history")},"First license")' for k in ORDER)
    food = f'=COUNTIF({rng("food", "name")},"?*")'
    w = full["window"]
    tiles = [("B", "D", "NEW LICENSES, 30 DAYS", total, f"issued {pretty(w['listFrom'])[:-6]} to {pretty(w['to'])[:-6]}", True),
             ("F", "H", "NEW THIS WEEK", new, f"issued {pretty(w['from'])[:-6]} or later", False),
             ("J", "L", "FIRST LICENSE", first, "none before the last 30 days", False),
             ("N", "P", "FOOD AND DRINK", food, "restaurants, bars, food shops", False)]
    D.h(ws, 6, 10)
    for left, right, eb, fml, sub, dark in tiles:
        D.tile(ws, 7, left, right, eb, fml, S.FMT["int"], sub, dark=dark, value_size=28 if dark else 20)
    r = card(ws, 12, "Three steps", [
        ("step", (1, "Open the tab for the trades you sell to. Filter New this week, or On the City's record for First license.")),
        ("step", (2, "Call or visit in the first weeks. Name the City's license and its date, nothing more.")),
        ("step", (3, "Send the matching email from the Pitch kit tab the same day.")),
    ])
    r = card(ws, r, "Find your trade", [("lead", (TAB[k], f"{KINDS[k]}.")) for k in ORDER])
    r = card(ws, r, "How the list is made", [
        ("para", f"From the City of Chicago's Business Licenses data, pulled {as_of_text(full)}. Every license the City issued as a new "
                 f"license (application type Issue) from {pretty(w['listFrom'])} to {pretty(w['to'])}, at a Chicago business site."),
        ("lead", ("Trades", "Ours, from the City's license type and business activity. A business goes in the first trade that fits, in "
                            "the order of the tabs.")),
        ("lead", ("City record", "We read the City's earlier licenses for the same business. " + " ".join(
            f"{HISTORY[k]}: {HISTORY_LONG[k]}" for k in ("first", "site", "added")))),
        ("lead", ("Restaurants", OVERLAP + " " + OPEN_BEFORE)),
        ("lead", ("Left out", LEFT_OUT)),
        ("lead", ("Not included", "The legal name of the business and anything about the people who own it. The legal name is read only "
                                  "to judge whether a name could be a person's, and is never written out.")),
        ("link", ("Source: City of Chicago Data Portal, Business Licenses", full["source"]["url"])),
    ])
    r = card(ws, r, "Before you rely on it", [
        ("notegrey", "For general information and planning only. This is not legal, tax, financial or other professional advice, and using it "
                     f"doesn't create a professional relationship. Figures come from City of Chicago records as of {as_of_text(full)} and can "
                     "change. See the Terms tab before you rely on anything here."),
        ("gap", None), ("notegrey", OUR_NOTICE), ("gap", None), ("notegrey", city_disclaimer())])
    finish_card(ws, r, "teal")
    return ws


def pitch_kit(wb, list_date):
    ws = card_sheet(wb, "Pitch kit", "Pitch kit", "A call opener and an email for each buyer. Fill in the blue parts.", list_date, "teal")
    r = card(ws, 6, "Three rules", [("step", (i + 1, t)) for i, t in enumerate(PITCH_RULES)])
    for i, x in enumerate(PITCH):
        if i:
            S.page_break_before(ws, r)
        r = card(ws, r, x["buyer"], [("lead", ("Call opener", blue(x["call"])))], eyebrow="CALL OR VISIT")
        lines = []
        for j, line in enumerate(x["email"]):
            if j:
                lines.append(("gap", None))
            lines.append(("rich", blue(line)))
        r = card(ws, r, None, lines, eyebrow="EMAIL: COPY, THEN FILL IN THE BLUE PARTS", bg="total_tint", line="frame")
    finish_card(ws, r, "teal")
    return ws


def terms(wb, full, list_date):
    t = terms_text(as_of_text(full))
    ws = card_sheet(wb, "Terms", "Terms of Use", f"{PRODUCT} | {VERSION}", list_date, "note")
    ct = city_terms()
    rows = [("note", "The City of Chicago's Data Terms of Use, word for word, as the City published them "
                     f"(checked {pretty(ct['checked'])}). They apply to the City data on this list.")]
    for h, paras in ct["sections"]:
        rows += [("gap", None), ("rich", [(h, True, "ink")])]
        rows += [("para", p) for p in paras]
    rows += [("gap", None), ("link", ("City of Chicago Data Terms of Use", ct["url"]))]
    r = card(ws, 6, "City of Chicago Data Terms of Use", rows)
    ours = [("para", OUR_NOTICE)]
    for x in t[1:]:
        ours += [("gap", None), lead_para(x)]
    r = card(ws, r, "ProofNotFluff", ours)
    finish_card(ws, r, "note")
    return ws


# ---------------------------------------------------------------- planted list (invented businesses, real field names)
def _planted():
    R = lambda lic, b, seg, issued, **kw: dict({"license": lic, "business": b, "address": "100 W Lake St", "zip": "60601",
                                                 "licenseType": "Limited Business License", "otherTypes": [], "activity": "Retail Sales",
                                                 "issued": issued, "segment": seg, "communityArea": "Loop", "lat": 41.88, "lon": -87.63,
                                                 "history": "first", "since": "", "foodInsp": ""}, **kw)
    recs = [R("1", "Luna Tacos", "food", "2026-10-20", licenseType="Retail Food Establishment", foodInsp="2026-10-02", inspSince="2025",
              otherTypes=["Consumption on Premises - Incidental Activity"]),
            R("2", "Bright Kids Academy", "care", "2026-10-01", licenseType="Children's Services Facility License"),
            R("3", "Fresh Cuts Barbershop", "beauty", "2026-10-19", history="added", since="2019"),
            R("4", "Main Street Phones", "retail", "2026-10-02", history="site", since="2015", communityArea=""),
            R("5", "Corner Market", "food", "2026-10-21", licenseType="Retail Food Establishment"),
            R("6", "Quick Lube Auto", "auto", "2026-09-25", history="")]
    return {"source": {"name": "City of Chicago Data Portal, Business Licenses",
                       "url": "https://data.cityofchicago.org/Community-Economic-Development/Business-Licenses/r5kz-chrr",
                       "fetchedAt": "2026-10-22T16:40:46+00:00", "terms": "https://www.chicago.gov/city/en/narr/foia/data_disclaimer.html"},
            "window": {"from": "2026-10-15", "to": "2026-10-22", "listFrom": "2026-09-22"},
            "counts": {"checks": {"history": True, "foodInspections": True}}, "records": recs}


def cached_note_ok(path):
    from openpyxl import load_workbook
    v = load_workbook(path, data_only=True)[TAB["venue"]]["C8"].value
    assert v == 0, f"an empty trade counts 0 businesses, not {v}"
    return True


def selftest():
    import tempfile
    from openpyxl import load_workbook
    full = _planted()
    out = os.path.join(tempfile.mkdtemp(), "t.xlsx")
    res = build(full, out)
    assert res == {"food": 2, "retail": 1, "beauty": 1, "venue": 0, "auto": 1, "care": 1}, res
    wb = load_workbook(out, rich_text=True)
    assert wb.sheetnames == ["Start Here", *TAB.values(), "Pitch kit", "Terms"], wb.sheetnames
    f = wb[TAB["food"]]
    heads = [f[f"{gl(i)}11"].value for i in range(3, 3 + 8)]
    assert heads == ["BUSINESS", "ADDRESS", "COMMUNITY AREA", "LICENSED", "LICENSE TYPE", "BUSINESS ACTIVITY", "ON THE CITY'S RECORD",
                     "FOOD LICENSE INSPECTION"], heads
    assert f["C12"].value == "Corner Market" and f["C13"].value == "Luna Tacos", "newest first"
    assert f["F13"].number_format == "mmm d, yyyy" and f["J13"].number_format == "mmm d, yyyy"
    assert f["M13"].value == "Consumption on Premises - Incidental Activity" and f["L12"].value == "New" and f["K13"].value == "2025"
    assert f["P13"].hyperlink.target == RECORD + "1" and f.auto_filter.ref.startswith("C11")
    assert wb[TAB["venue"]]["D12"].value == "None in the last 30 days." and cached_note_ok(out)
    r = wb[TAB["retail"]]
    assert r["I12"].value == "New site, licensed in Chicago since 2015" and r["E12"].value == "Not given"
    assert wb[TAB["beauty"]]["I12"].value == "Added license, here since 2019" and wb[TAB["auto"]]["I12"].value == "Not checked"
    assert wb[TAB["care"]]["J12"].value is None, "only the food tab has the food inspection column"
    cached = load_workbook(out, data_only=True)
    sh = cached["Start Here"]
    assert [sh[c].value for c in ("C8", "G8", "K8", "O8")] == [6, 3, 3, 2], [sh[c].value for c in ("C8", "G8", "K8", "O8")]
    assert cached[TAB["food"]]["C8"].value == 2 and [cached[TAB["food"]][c].value for c in ("C8",)] == [2]
    food_stats = [cached[TAB["food"]][f"{gl(i)}8"].value for i in range(3, 12) if cached[TAB["food"]][f"{gl(i)}8"].value is not None]
    assert food_stats == [2, 2, 2, 1], food_stats
    texts = [str(c.value) for ws in wb.worksheets for row in ws.iter_rows() for c in row if c.value is not None]
    blob = "\n".join(texts)
    assert city_disclaimer() in blob and LEFT_OUT in blob and OVERLAP in blob and OUR_NOTICE in blob
    for h, paras in city_terms()["sections"]:
        assert h in blob and all(p in blob for p in paras), f"City terms section {h} not word for word"
    assert any(VERSION in t for t in texts) and "Version 1" in blob
    from make_site import CITY_DISCLAIMER as SITE_CITY
    assert city_disclaimer() == SITE_CITY["Chicago"], "one City disclaimer on the site and in the product"
    assert len(wb["Pitch kit"].row_breaks.brk) == len(PITCH) - 1
    for x in PITCH:
        for s in [x["call"]] + x["email"]:
            assert not re.search(r"[–—]|\b(guarantee|struggling|dirty|unsafe|violation)\b", s, re.I), s
    # the City terms gate: unchanged passes, a changed word stops the build, a failed fetch keeps the snapshot
    src = os.path.join(ROOT, "permits", "licenses-chicago", "source-terms.txt")
    assert terms_check(src)
    tmp = os.path.join(tempfile.mkdtemp(), "t.txt")
    open(tmp, "w", encoding="utf-8").write(open(src, encoding="utf-8").read().replace("voluntarily provides", "provides"))
    try:
        terms_check(tmp)
        raise AssertionError("a change in the City's terms must stop the build")
    except SystemExit:
        pass
    open(tmp, "w").write("Could not fetch the terms page: timeout\n")
    assert terms_check(tmp)
    meta = open(out, "rb").read()
    assert b"Todd" not in meta and b"Millen" not in meta
    print("lic_xlsx selftest ok", res)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        selftest()
    elif a[:1] == ["--terms-check"]:
        terms_check(a[1])
    else:
        print(build(json.load(open(a[0], encoding="utf-8")), a[1]))
