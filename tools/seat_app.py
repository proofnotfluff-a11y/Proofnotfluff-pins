#!/usr/bin/env python3
"""The members' page for the Chicago Pest Daily List, the $149 a month founding seat (move 3, Todd, Oct 23 and 24, 2026).

Pest control only (Todd, Oct 24: hood waits for volume), at most 3 seats in Chicago. Built every morning in GitHub Actions
(.github/workflows/inspections-daily.yml) from the daily list tools/rest_daily.py writes and tools/phones.py fills, after
the City's overnight refresh. Nothing for Todd to do day to day.

How a seat holder gets it: Gumroad's post-purchase content holds this page's link and the seat password. The page is one
AES-256-GCM box under a key derived with PBKDF2-SHA256 at 250,000 rounds from that password (tools/leads_page.py, the
same lock as the $39 list), opened in the member's browser. The password is the REST_SEAT_PASSWORD Actions secret; the
repo holds only ciphertext, and only once that secret exists. The Terms view (#/terms) opens before the password.

What the page shows: the pest places the City posted since the last morning ("New this morning"), then every pest place
sent in the last 14 days, by the morning it went out, so a missed morning loses nothing. Each place: name, street, ZIP,
community area, facility type, the City's result, inspection type, date and violation codes (one line built from the
codes, never the inspector's notes; wording rule, Todd Oct 17), failed visits in 90 days, the listed phone with a Call
button, and a link to the City's own record. Called marks and notes live in the member's browser only (localStorage).
One button downloads the 14 days as a CSV file.

Phones: the Legal desk's two member terms lines word for word, the attribution lines for the providers this list used,
and legal/licenses/phone-sources.txt (CDLA Permissive 2.0 and Apache 2.0 texts) on the Terms view
(legal/reviews/2026-10-23-phone-sources.md, "Open for move 3").

Usage (runner): REST_SEAT_PASSWORD=... python3 tools/seat_app.py build NAMED.json docs/chicago-pest-daily-members/index.html
                python3 tools/seat_app.py stamp NAMED.json permits/inspections-chicago/daily.json   (counts only)
                python3 tools/seat_app.py --pw-file PATH build NAMED.json OUT.html                   (live session preview)
                python3 tools/seat_app.py --selftest
"""
import datetime as dt, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from leads_page import decrypt, encrypt  # noqa: E402
from leads_xlsx import CITY_DISCLAIMER  # noqa: E402
import lic_xlsx  # noqa: E402  (phone_sources: the license texts, one source for every list that carries phones)
import phones  # noqa: E402  (TERMS_LINES: the Legal desk's two member terms lines)
import rest_leads as RL  # noqa: E402  (LEFT_OUT and pretty dates)

PRODUCT = "Chicago Pest Daily List"
PRICE = "149"
SEATS = 3
SLUG = "chicago-pest-daily-members"
SECRET = "REST_SEAT_PASSWORD"
FREE_PAGE = "https://proofnotfluff.com/chicago-restaurant-inspection-leads/"
TERMS_VERSION = "Version 1, Oct 24, 2026"
COMPANY = "ProofNotFluff LLC"
TRADE = "pests"


def terms_text(date):
    """The seat's Terms of Use: the restaurant list's terms (tools/rest_xlsx.py) adapted for a daily, capped seat, with the
    Legal desk's phone lines word for word. One source: this page's #/terms view."""
    P = phones.TERMS_LINES
    return [
        f"{COMPANY} | {PRODUCT} (founding seat) | {TERMS_VERSION} | List of {date}",
        "License. Your seat gives you a license to use this list for one business you own, for its own sales prospecting. You may "
        "edit it and print it for that use. You may not resell, share, give away, upload, publish or redistribute it, in original or "
        "edited form, share the password, or use it to make a competing product.",
        f"The seat cap. ProofNotFluff sells this daily list to at most {SEATS} Chicago pest control businesses at a time. When a seat "
        "ends, the members' password changes before the seat can be sold again. Before buying, a pest control company may get one free "
        "morning of the list by email. The same City records also appear on ProofNotFluff's weekly Chicago Restaurant Inspection Leads "
        "list each Monday, which is not capped. Seats are for pest control businesses that serve Chicago; if a buyer is not one, we "
        "refund the payment and cancel the seat.",
        "Ownership. The selection, layout, categories and text belong to ProofNotFluff. The inspection records themselves are public "
        "City of Chicago data. Buying a seat doesn't transfer ownership.",
        "Delivery. Each morning, after the City's overnight data refresh, the members' page shows the places the City posted since the "
        "last list, and keeps every place sent in the last 14 days. The page says when it was last updated. Some mornings the City "
        "posts nothing new, or posts late, and the list can be short or empty. The list is built by an automated job each morning. If a "
        "build fails or runs late, the next one catches up, and the 14 days kept on the page mean nothing is lost.",
        "Accuracy. The list is built from City of Chicago food inspection records as of the list date above. City data can be late, "
        "incomplete or wrong. The City says its dataset may contain duplicate reports, and that each result and the violations noted "
        "reflect what the inspector found at the time of that inspection and may not reflect other times. A place's result can change at "
        "its next inspection. The pest category is ProofNotFluff's reading of the City's violation codes and notes, not the City's own "
        "label. Confirm anything you rely on with the business or the City.",
        "Phones. " + P[0] + " A number is shown only when the business's name and street address both match the City record, so some "
        "rows have none. " + P[1] + " Phone data from Overture Maps Foundation places data is used under the CDLA Permissive 2.0, "
        "Apache 2.0 and CC0 1.0 licenses; the sources and license texts follow these terms.",
        "Who is left out. " + RL.LEFT_OUT + " The daily list also leaves out license inspections, the check the City does before it "
        "issues a food license.",
        "What the list does not say. A place on the list has a public inspection record; the list does not say it is clean or unsafe, "
        "open or closed, or in need of any service. Don't present the list, or anything in it, as a judgment about a business, and "
        "never say or imply that you call for the City.",
        "No promise of results. Counts are figures from City records. Nothing here promises any work, contract, income or outcome.",
        "Availability. The list depends on the City of Chicago publishing its food inspection data. If the City stops or changes that "
        "data, or asks us to stop using it, the list may pause or end, and future charges will stop.",
        "No warranty. The product is provided \"as is\", without warranties of any kind, to the extent the law allows.",
        "Limit of liability. To the extent the law allows, ProofNotFluff is not liable for any loss or damage from using or relying on "
        "this product, and its total liability for any claim is limited to the amount you paid for the most recent month of your "
        "seat. Nothing here limits rights you have under consumer protection laws that can't be waived.",
        "Trademarks. Gumroad and Microsoft Excel are trademarks of their owners, and business names on the list belong to those "
        "businesses. ProofNotFluff isn't affiliated with, sponsored or endorsed by them, by the City of Chicago, or by any business listed.",
        "AI assistance. This product was made with AI assistance and reviewed and tested by the shop owner.",
        f"Price and cancelling. ${PRICE} a month, billed by Gumroad, with no lock-in: no minimum term. Your seat renews each month until "
        "you cancel. Cancel any time from your Gumroad receipt or library; cancelling stops future charges, and the page stays open until "
        "the end of the month you paid for. If the page won't open or something looks wrong, write to hello@proofnotfluff.com with your "
        "Gumroad receipt and we will fix it or refund that month.",
    ]


OUR_NOTICE = ("For general business information only. Places appear because their food inspections are public City of Chicago records. "
              "This list repeats the City's recorded result, date and violation codes; it does not say whether any place is clean, safe or "
              "open today, and a result can change at the next inspection. No business listed has endorsed or works with ProofNotFluff. "
              "You make your own calls and emails, and are responsible for following the law when you do.")


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def pest_rows(named):
    """Today's new pest rows, then the earlier mornings' (rest_daily.py "earlier"), one row per place."""
    out, seen = [], set()
    for new, rows in ((True, named.get("items") or []), (False, named.get("earlier") or [])):
        for r in rows:
            if TRADE not in (r.get("trades") or []) or r["place"] in seen:
                continue
            seen.add(r["place"])
            out.append((new, r))
    return out


def later_text(lt):
    """The place's newer City result, in the same plain words as the summary (holdout, Oct 24)."""
    if not lt:
        return ""
    return f"Newer City result: {lt['result']} on {RL.pretty(lt['date'])}, {lt['inspectionType']}."    # Legal desk fix 9 pattern


def _coord(v):
    try:
        return round(float(v), 5)
    except (TypeError, ValueError):
        return None


# Leaflet for the map view (Todd, Oct 27, 2026: interactive maps on the paid products too); same file and hash as
# tools/leads_app.py, so every members' app loads one pinned copy.
LEAFLET_JS = ("https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js", "sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=")
LEAFLET_CSS = ("https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css", "sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=")


def payload(named):
    rows = []
    for new, r in pest_rows(named):
        rows.append({"id": r["place"], "n": r["name"], "a": r["address"], "z": r.get("zip") or "", "ar": r.get("area") or "",
                     "ty": r.get("type") or "", "d": r["date"], "r": r["result"], "it": r.get("inspectionType") or "",
                     "c": (r.get("codes") or {}).get(TRADE) or [], "s": r.get("summary") or "", "rec": r.get("record") or "",
                     "f90": int(r.get("fails90") or 0), "lo": r.get("listedOn") or named["asOf"], "nw": new, "ph": r.get("phone") or "",
                     "lt": later_text(r.get("later")), "y": _coord(r.get("lat")), "x": _coord(r.get("lon"))})
    return {"asOfIso": named["asOf"], "asOf": RL.pretty(named["asOf"]), "through": RL.pretty(named["through"]),
            "phonesChecked": bool(named.get("phoneNote")), "phoneAttr": list(named.get("phoneAttribution") or []), "rows": rows,
            "fileName": f"chicago-pest-daily-{named['asOf']}.csv"}


def counts(named):
    """Counts only (no names, no numbers): pest places on the members' page and how many carry a listed phone."""
    rows = [r for _, r in pest_rows(named)]
    new = [r for n, r in pest_rows(named) if n]
    got = sum(1 for r in rows if r.get("phone"))
    return {"asOf": named["asOf"], "places14": len(rows), "new": len(new), "withPhone14": got,
            "coverage14": round(100 * got / len(rows), 1) if rows else 0.0, "phonesChecked": bool(named.get("phoneNote"))}


def stamp(named, public_path):
    """The public daily file gets the seat's counts (move 3: the offer states exact phone coverage). Counts only."""
    pub = json.load(open(public_path))
    pub["seat"] = counts(named)
    tmp = public_path + ".tmp"
    json.dump(pub, open(tmp, "w"), indent=1)
    os.replace(tmp, public_path)
    return pub["seat"]


def words_json(as_of):
    t = terms_text(as_of)
    return json.dumps({"version": t[0], "paras": t[1:], "city": CITY_DISCLAIMER, "notice": OUR_NOTICE,
                       "phoneLicenses": lic_xlsx.phone_sources({}), "free": FREE_PAGE}, ensure_ascii=False).replace("</", "<\\/")


def build_html(named, password):
    box = encrypt(password, json.dumps(payload(named), separators=(",", ":")).encode())
    as_of = RL.pretty(named["asOf"])
    return (PAGE.replace("__BOX__", json.dumps(box)).replace("__WORDS__", words_json(as_of)).replace("__ASOF__", _esc(as_of))
            .replace("__FREE__", FREE_PAGE).replace("__CITY__", _esc(CITY_DISCLAIMER))
            .replace("__LJS__", LEAFLET_JS[0]).replace("__LJSI__", LEAFLET_JS[1]).replace("__LCSS__", LEAFLET_CSS[0]).replace("__LCSSI__", LEAFLET_CSS[1]))


def build(named, out, password):
    html = build_html(named, password)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    tmp = out + ".tmp"
    open(tmp, "w", encoding="utf-8").write(html)
    os.replace(tmp, out)
    return counts(named) | {"bytes": len(html)}


ICO_LOCK = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>'

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex, nofollow"><meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#1d2433">
<title>Members: Chicago Pest Daily List | ProofNotFluff</title>
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="../assets/fonts/inter-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../assets/fonts/poppins-700.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="__LCSS__" integrity="__LCSSI__" crossorigin="anonymous">
<script defer src="__LJS__" integrity="__LJSI__" crossorigin="anonymous"></script>
<style>
@font-face{font-family:Inter;font-weight:400;font-display:swap;src:url(../assets/fonts/inter-400.woff2) format("woff2")}
@font-face{font-family:Inter;font-weight:600;font-display:swap;src:url(../assets/fonts/inter-600.woff2) format("woff2")}
@font-face{font-family:Inter;font-weight:700;font-display:swap;src:url(../assets/fonts/inter-700.woff2) format("woff2")}
@font-face{font-family:Poppins;font-weight:700;font-display:swap;src:url(../assets/fonts/poppins-700.woff2) format("woff2")}
:root{--canvas:#f3f1ec;--card:#fff;--ink:#1d2433;--ink2:#3f4659;--muted:#565d6b;--line:#e2ddd3;--rule:#efebe4;--accent:#c8502f;
--btn:#b8462a;--btn-ink:#fff;--teal:#2e6b66;--teal-bg:#e2efec;--link:#2a5d93;--fail:#a63e21;--fail-bg:#fbeae4;--pwc:#7a5a12;--pwc-bg:#f6edd5;
--band:#1d2433;--band-text:#c9cfdb;--warn-bg:#fdf3d6;--warn-ink:#6b4e0a;--focus:rgba(46,107,102,.55);--r:14px;
--sh:0 1px 2px rgba(20,24,36,.05),0 6px 18px rgba(20,24,36,.06);
--head:Poppins,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;--body:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
@media (prefers-color-scheme:dark){:root{--canvas:#12161f;--card:#1b2130;--ink:#eef0f4;--ink2:#c9ced8;--muted:#a3aab6;--line:#2c3343;--rule:#242b3a;
--accent:#ef8c6b;--btn:#be4a2a;--btn-ink:#fff;--teal:#7fcdc3;--teal-bg:#1d3533;--link:#9cc2ff;--fail:#f4b29c;--fail-bg:#3a2219;--pwc:#e8d49b;--pwc-bg:#332a12;
--band:#0b0e14;--band-text:#c9cfdb;--warn-bg:#332a12;--key-bg:#16302c;--key-line:#2d5a54;--warn-ink:#f1dea6;--focus:rgba(127,205,195,.7);--sh:0 1px 2px rgba(0,0,0,.3),0 6px 18px rgba(0,0,0,.3)}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;color-scheme:light dark}
body{margin:0;background:var(--canvas);color:var(--ink);font:16px/1.5 var(--body);-webkit-font-smoothing:antialiased}
h1,h2,h3{font-family:var(--head);letter-spacing:-.015em;line-height:1.2;margin:0;text-wrap:balance}
a{color:var(--link);text-underline-offset:3px}
button,input,textarea{font:inherit;color:inherit}
:focus-visible{outline:3px solid var(--focus);outline-offset:2px;border-radius:6px}
[hidden]{display:none!important}
.sr{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.skip{position:absolute;left:12px;top:-80px;z-index:20;background:var(--card);color:var(--ink);padding:12px 14px;border-radius:8px;font-weight:600}
.skip:focus{top:10px}
.ico{width:18px;height:18px;flex:none;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
.num{font-variant-numeric:tabular-nums}
.bar{background:var(--band);color:#fff}
.bar-in{max-width:960px;margin:0 auto;padding:0 16px;min-height:60px;display:flex;align-items:center;gap:16px}
.brand{display:flex;flex-direction:column;gap:3px;color:#fff;text-decoration:none;min-height:44px;justify-content:center;min-width:0}
.brand b{font:700 16px/1 var(--head)}.brand small{font-size:13px;color:var(--band-text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar-sp{flex:1}
.bar a.tl{color:#fff;min-height:44px;display:inline-flex;align-items:center;padding:0 4px;font-weight:600;font-size:15px}
.wrap{max-width:960px;margin:0 auto;padding:0 16px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:48px;padding:0 20px;border:0;border-radius:10px;background:var(--btn);color:var(--btn-ink);
font-weight:700;text-decoration:none;cursor:pointer}
.btn.ghost{background:transparent;color:var(--ink);border:1.5px solid var(--line)}
.btn.sm{min-height:44px;padding:0 14px;font-size:15px;font-variant-numeric:tabular-nums}
/* gate */
.gate{padding:40px 16px 24px}
.gate-card{max-width:520px;margin:0 auto;background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh);padding:28px 24px}
.chip{display:inline-flex;align-items:center;gap:6px;height:28px;padding:0 10px;border-radius:999px;background:var(--teal-bg);color:var(--teal);font-size:13px;font-weight:700}
.gate-card h1{font-size:clamp(24px,5vw,30px);margin:14px 0 8px}
.gate-card .sub{color:var(--ink2);margin:0 0 20px}
.gate-card label.f{display:block;font-weight:600;margin:0 0 6px}
.pw{display:flex;gap:8px}
.pw input{flex:1;min-width:0;height:48px;border:1.5px solid var(--muted);border-radius:10px;padding:0 12px;background:var(--card)}
.pw .eye{width:48px;height:48px;border:1.5px solid var(--line);border-radius:10px;background:transparent;display:grid;place-items:center;cursor:pointer}
.keep{display:flex;align-items:center;gap:10px;min-height:44px;margin:8px 0 12px;color:var(--ink2)}
.keep input{width:22px;height:22px;accent-color:var(--teal)}
.gate-card .btn{width:100%}
.err{color:var(--fail);font-weight:600;min-height:24px;margin:10px 0 0}
.help{border-top:1px solid var(--rule);margin-top:16px;padding-top:14px;color:var(--ink2);font-size:15px}.help p{margin:0 0 8px}
.help a{display:inline;padding:12px 0}
/* app */
.page{padding:28px 16px 32px}
.page h1{font-size:clamp(26px,5vw,36px);margin:0 0 6px}
.meta{color:var(--ink2);margin:0 0 18px}
.stale{background:var(--warn-bg);color:var(--warn-ink);border-radius:10px;padding:12px 14px;margin:0 0 18px;font-weight:600}
.tiles{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:0 0 22px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;min-width:0}
.tile.key{background:var(--key-bg,var(--band));border-color:var(--key-line,var(--band));color:#fff}
.tile .lab{font-size:12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}
.tile.key .lab{color:var(--band-text)}
.tile .val{font:700 clamp(24px,6vw,34px)/1.1 var(--head);margin-top:4px;font-variant-numeric:tabular-nums}
.tile .sub{font-size:13.5px;color:var(--muted);margin-top:2px}.tile.key .sub{color:var(--band-text)}
@media(max-width:560px){.tiles{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}.tiles .tile.key{grid-column:1 / -1}
.card .acts{display:grid;grid-template-columns:auto 1fr;column-gap:16px;row-gap:4px;justify-items:start}.card .acts .called{grid-column:1 / -1}.card details{margin-top:0}}
.tools{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:0 0 14px}
.search{flex:1 1 260px;min-width:0}
.search input{width:100%;height:48px;border:1.5px solid var(--muted);border-radius:10px;padding:0 12px;background:var(--card)}
#q::placeholder{color:var(--muted);opacity:1}
#main:focus,#main:focus-visible{outline:none}
.seg{display:flex;flex-wrap:wrap;gap:8px}
.seg button{min-height:44px;padding:0 14px;border-radius:999px;border:1.5px solid var(--line);background:var(--card);font-weight:600;font-size:15px;cursor:pointer}
.seg button[aria-pressed="true"]{background:var(--ink);color:var(--canvas);border-color:var(--ink)}
.count{color:var(--ink2);margin:0 0 10px;font-size:15px}
.group{margin:22px 0 8px;font-size:19px}
.group small{font:600 14px/1.3 var(--body);color:var(--muted);margin-left:6px}
.list{display:grid;gap:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh);padding:16px 16px 14px;min-width:0}
.card.done{background:var(--canvas)}.card.done h3{text-decoration:line-through;text-decoration-thickness:2px}
.card .top{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:0 0 8px}
.pill{display:inline-flex;align-items:center;height:26px;padding:0 10px;border-radius:999px;font-size:13px;font-weight:700;white-space:nowrap}
.pill.fail{background:var(--fail-bg);color:var(--fail)}.pill.pwc{background:var(--pwc-bg);color:var(--pwc)}
.pill.new{background:var(--teal-bg);color:var(--teal)}
.card h3{font-size:19px;margin:0 0 2px;overflow-wrap:anywhere}
.card .ad{margin:0 0 8px;color:var(--ink2);overflow-wrap:anywhere}
.card .sm{margin:0 0 6px}
.card .rep{margin:0 0 6px;color:var(--fail);font-weight:600;font-size:15px}
.card .lt{margin:0 0 6px;color:var(--teal);font-weight:600;font-size:15px}
.card .acts{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:12px}
.card .ph{font-variant-numeric:tabular-nums}
.card .noph{color:var(--muted);font-size:15px;min-height:44px;display:inline-flex;align-items:center}
.card .rec{min-height:44px;display:inline-flex;align-items:center;padding:0 6px;font-size:15px}
.card .called{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 6px 0 2px;font-weight:600;font-size:15px;cursor:pointer}
.card .called input{width:22px;height:22px;accent-color:var(--teal)}
.card details{margin-top:6px}
.card summary{min-height:44px;display:inline-flex;align-items:center;cursor:pointer;color:var(--link);font-weight:600;font-size:15px}
.card textarea{width:100%;min-height:80px;border:1.5px solid var(--muted);border-radius:10px;padding:10px 12px;background:var(--card);resize:vertical}
.empty{background:var(--card);border:1px dashed var(--line);border-radius:var(--r);padding:20px;color:var(--ink2)}
.terms{padding:28px 16px 32px;max-width:792px}
.terms h1{font-size:clamp(24px,5vw,32px);margin:0 0 6px}.terms h2{font-size:19px;margin:26px 0 8px}
.terms p{margin:0 0 12px;overflow-wrap:anywhere}.terms p b{color:var(--ink)}.terms .ver{color:var(--muted);font-size:14px}
.terms .back{display:inline-flex;align-items:center;min-height:44px;font-weight:600}
footer{border-top:1px solid var(--line);margin-top:16px;padding:20px 0 36px;color:var(--muted);font-size:14px}
footer p{margin:0 0 10px;overflow-wrap:anywhere}
.toast{position:fixed;left:50%;bottom:20px;transform:translateX(-50%);background:var(--band);color:#fff;padding:12px 16px;border-radius:10px;font-weight:600;opacity:0;pointer-events:none;transition:opacity .2s}
.toast.on{opacity:1}
@media (prefers-reduced-motion:reduce){.toast{transition:none}}
/* map view (Oct 27, 2026) */
.mapbox{position:relative;height:min(68vh,620px);min-height:380px;margin:0 0 16px;border-radius:var(--r);overflow:hidden;border:1px solid var(--line);box-shadow:var(--sh);background:#E9E6E0}
.mapbox .map{position:absolute;inset:0}
.leaflet-container{font-family:var(--body);background:#E9E6E0}
.leaflet-tile-pane{filter:grayscale(1) sepia(.18) contrast(.88) brightness(1.06)}
.leaflet-control-attribution{font-size:11px;background:rgba(255,255,255,.92)!important}.leaflet-control-attribution a{color:#2a5d93}
.leaflet-bar a{width:40px!important;height:40px!important;line-height:40px!important;color:#1d2433!important}
.leaflet-popup-content-wrapper{border-radius:12px;box-shadow:0 8px 24px rgba(29,36,51,.18)}.leaflet-popup-content{margin:14px 16px;font:14.5px/1.45 var(--body);color:#1d2433}
.pop b{display:block;font:700 16px/1.25 var(--head);margin:0 0 4px}.pop .pa{display:block;color:#3f4659;margin:0 0 8px}.pop .pill{margin:0 0 10px}
.pop .pb{display:grid;gap:8px;margin:10px 0 0}.pop .btn{width:100%;min-height:44px}.pop .btn.ghost{color:#1d2433;border-color:#cfc8bb}
.legend{position:absolute;z-index:500;left:10px;top:10px;display:flex;flex-wrap:wrap;gap:6px 12px;background:rgba(255,255,255,.95);border:1px solid #e2ddd3;border-radius:10px;padding:8px 10px;font-size:13px;color:#1d2433;max-width:calc(100% - 70px)}
.legend span{display:inline-flex;align-items:center;gap:6px}.legend i{display:inline-block;border-radius:50%;border:2px solid #fff;box-shadow:0 0 0 1px rgba(29,36,51,.35)}
.legend .l0{width:16px;height:16px;background:#c8502f}.legend .l1{width:12px;height:12px;background:#2e6b66}.legend .l2{width:12px;height:12px;background:#fff;border-color:#3a4152;box-shadow:none}
.map-note{position:absolute;z-index:500;left:10px;bottom:10px;max-width:calc(100% - 140px);margin:0;background:rgba(255,255,255,.96);border:1px solid #e2ddd3;border-radius:8px;padding:6px 10px;font-size:12.5px;color:#565d6b}
.map-fail{position:absolute;inset:0;display:grid;place-content:center;justify-items:center;gap:10px;padding:20px;text-align:center;color:#3f4659;background:#f3f1ec}
.card.flash{outline:3px solid var(--accent);outline-offset:2px}
</style></head><body>
<a class="skip" href="#main" id="skip">Skip to main content</a>
<header class="bar"><div class="bar-in">
<a class="brand" href="#/" aria-label="ProofNotFluff, Chicago Pest Daily List, today's list"><b>ProofNotFluff</b><small>Chicago Pest Daily List</small></a>
<span class="bar-sp"></span><a class="tl" href="#/terms" id="termsTop">Terms</a>
</div></header>
<main id="main" tabindex="-1">
<div class="wrap gate" id="gateView">
<form class="gate-card" id="gate" novalidate>
<span class="chip">__LOCK__Founding seat</span>
<h1>Chicago pest daily list</h1>
<p class="sub">List of __ASOF__. Chicago food places whose failed or conditional City inspection had a pest violation, the morning the City posts them, with the last 14 days kept.</p>
<label class="f" for="pw">Seat password</label>
<div class="pw"><input id="pw" type="password" autocomplete="current-password" autocapitalize="off" spellcheck="false" required aria-describedby="err pwHelp">
<button type="button" class="eye" id="eye" aria-label="Show password" aria-pressed="false"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg></button></div>
<label class="keep"><input type="checkbox" id="keep"> Keep me signed in on this device</label>
<button class="btn" type="submit" id="go">Open today's list</button>
<p class="err" id="err" role="alert"></p>
<div class="help" id="pwHelp"><p>The password is on your Gumroad purchase page, linked from your receipt email. <a href="https://gumroad.com/library">Open your Gumroad library</a></p>
<p>Not a member? <a href="__FREE__">See the free restaurant sample</a> or <a href="#/terms">read the Terms</a>.</p></div>
</form>
</div>
<div class="wrap page" id="app" hidden></div>
<div class="wrap terms" id="termsView" hidden></div>
</main>
<footer><div class="wrap"><p>__CITY__</p><p>ProofNotFluff is not affiliated with or endorsed by the City of Chicago, and no business listed has endorsed or works with ProofNotFluff. Licensed to one business for its own prospecting. Made with AI assistance. <a href="#/terms">Terms of Use</a> · <a href="../privacy/">Privacy</a> · Questions? Write to hello@proofnotfluff.com.</p></div></footer>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script>
"use strict";
const BOX=__BOX__;
const W=__WORDS__;
const PKEY="pnf-pest-seat-pw",SKEY="pnf-pest-seat-marks-v1";
const $=s=>document.querySelector(s);
const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const b64=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
const MON=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const day=s=>{if(!s)return"";const[y,m,d]=s.split("-").map(Number);return MON[m-1]+" "+d+", "+y;};
const wday=s=>{const[y,m,d]=s.split("-").map(Number);return["Sun","Mon","Tue","Wed","Thu","Fri","Sat"][new Date(Date.UTC(y,m-1,d)).getUTCDay()];};
async function openBox(pw){const k0=await crypto.subtle.importKey("raw",new TextEncoder().encode(pw),"PBKDF2",false,["deriveKey"]);
const key=await crypto.subtle.deriveKey({name:"PBKDF2",salt:b64(BOX.salt),iterations:BOX.rounds,hash:"SHA-256"},k0,{name:"AES-GCM",length:256},false,["decrypt"]);
const pt=await crypto.subtle.decrypt({name:"AES-GCM",iv:b64(BOX.iv)},key,b64(BOX.ct));return JSON.parse(new TextDecoder().decode(pt));}
let D=null,MARKS={},STORE=true,F={q:"",v:"all",view:"list"},MAP=null,LAY=null,MK={};
try{const t="__pnf";localStorage.setItem(t,"1");localStorage.removeItem(t);MARKS=JSON.parse(localStorage.getItem(SKEY)||"{}")||{};}catch(e){STORE=false;MARKS={};}
function save(){try{localStorage.setItem(SKEY,JSON.stringify(MARKS));}catch(e){STORE=false;toast("Your browser is not saving marks on this device.");}}
function toast(t){const e=$("#toast");e.textContent=t;e.classList.add("on");clearTimeout(toast.h);toast.h=setTimeout(()=>e.classList.remove("on"),2600);}
function chicagoToday(){try{return new Intl.DateTimeFormat("en-CA",{timeZone:"America/Chicago",year:"numeric",month:"2-digit",day:"2-digit"}).format(new Date());}catch(e){return"";}}
const telHref=p=>{const d=String(p).replace(/\D/g,"");return d.length===10?"tel:+1"+d:"";};
const resCls=r=>/^fail$/i.test(r)?"fail":"pwc";
const mark=id=>MARKS[id]||{};
function card(r){const m=mark(r.id),t=telHref(r.ph);
const ph=r.ph&&t?`<a class="btn sm" href="${t}"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>Call <span class="ph">${esc(r.ph)}</span></a>`
:`<span class="noph">${D.phonesChecked?"No listed phone found":"Phone not checked this morning"}</span>`;
return `<article class="card${m.c?" done":""}" data-id="${esc(r.id)}" aria-labelledby="h-${esc(r.id)}">
<div class="top"><span class="pill ${resCls(r.r)}">City result: ${esc(r.r)}</span></div>
<h3 id="h-${esc(r.id)}">${esc(r.n)}</h3>
<p class="ad">${esc(r.a)}${r.z?", "+esc(r.z):""}${r.ar?" · "+esc(r.ar):""}${r.ty?" · "+esc(r.ty):""}</p>
<p class="sm">${esc(r.s)}</p>
${r.lt?`<p class="lt">${esc(r.lt)}</p>`:""}${r.f90>=2?`<p class="rep">${r.f90} failed City inspections in the last 90 days, not counting license inspections</p>`:""}
<div class="acts">${ph}${r.rec?`<a class="rec" href="${esc(r.rec)}" target="_blank" rel="noopener">City record<span class="sr"> for ${esc(r.n)} (opens in a new tab)</span></a>`:""}
<label class="called"><input type="checkbox" data-act="called" ${m.c?"checked":""}> Called${m.c&&m.on?` <span class="sr">on ${esc(day(m.on))}</span>`:""}</label></div>
<details${m.n?" open":""}><summary>${m.n?"Your note":"Add a note"}</summary><label class="sr" for="n-${esc(r.id)}">Note for ${esc(r.n)}</label>
<textarea id="n-${esc(r.id)}" data-act="note" maxlength="2000">${esc(m.n||"")}</textarea></details></article>`;}
function norm(s){return String(s||"").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"").replace(/[^a-z0-9 ]+/g," ").replace(/\s+/g," ").trim();}
function pass(r){if(F.v==="new"&&!r.nw)return false;if(F.v==="todo"&&mark(r.id).c)return false;
if(F.q){const hay=norm([r.n,r.a,r.z,r.ar,r.ty].join(" "));if(!norm(F.q).split(" ").every(w=>hay.includes(w)))return false;}return true;}
function listHtml(){const rows=D.rows.filter(pass);const by={};rows.forEach(r=>{(by[r.lo]=by[r.lo]||[]).push(r);});
const days=Object.keys(by).sort().reverse();
let h=`<p class="count" aria-live="polite">${rows.length} of ${D.rows.length} place${D.rows.length===1?"":"s"} shown</p>`;
if(!rows.length){h+=`<div class="empty">${D.rows.length?"No place matches. Clear the search or pick All.":"No pest places in the last 14 days of the City's records."}</div>`;return h;}
days.forEach(d=>{const lab=d===D.asOfIso?"New this morning":"Sent "+wday(d)+", "+day(d);
h+=`<h2 class="group">${esc(lab)} <small>${by[d].length} place${by[d].length===1?"":"s"}</small></h2><div class="list">${by[d].map(card).join("")}</div>`;});
return h;}
function drawList(){$("#results").innerHTML=listHtml();drawMap(false);}
/* map view: the same places the list shows, after the same search and filter */
const MS=[{radius:9,color:"#fff",weight:2.5,fillColor:"#c8502f",fillOpacity:1},{radius:6.5,color:"#fff",weight:1.5,fillColor:"#2e6b66",fillOpacity:.95},{radius:6,color:"#3a4152",weight:2,fillColor:"#fff",fillOpacity:1}];
function ensureMap(){if(MAP||!$("#map"))return;if(!window.L){const box=$("#mapbox");if(box&&!box.querySelector(".map-fail"))box.insertAdjacentHTML("beforeend",'<div class="map-fail"><p>The map did not load on this connection. The list has every place.</p><button class="btn sm" type="button" id="mfl">Show the list</button></div>');const b=$("#mfl");if(b)b.onclick=()=>setView("list");return;}
MAP=L.map("map",{zoomControl:true,scrollWheelZoom:false}).setView([41.85,-87.68],11);MAP.attributionControl.setPrefix('<a href="https://leafletjs.com">Leaflet</a>');
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(MAP);LAY=L.layerGroup().addTo(MAP);drawMap(true);}
function pop(r){const t=telHref(r.ph);return `<div class="pop"><b>${esc(r.n)}</b><span class="pa">${esc(r.a)}${r.z?", "+esc(r.z):""}${r.ar?" · "+esc(r.ar):""}</span><span class="pill ${resCls(r.r)}">City result: ${esc(r.r)}</span><span class="pa">${esc(r.nw?"New this morning":"Sent "+day(r.lo))}, inspected ${esc(day(r.d))}</span>
<span class="pb">${r.ph&&t?`<a class="btn sm" href="${t}">Call ${esc(r.ph)}</a>`:""}<button class="btn ghost sm" type="button" data-show="${esc(r.id)}">Show in the list</button></span></div>`;}
function drawMap(refit){if(!MAP)return;const rows=D.rows.filter(pass),geo=rows.filter(r=>r.y&&r.x),note=$("#mapnote");LAY.clearLayers();MK={};
const miss=rows.length-geo.length;note.hidden=!(miss||!rows.length);note.textContent=!rows.length?"No places match. Clear the search or pick All.":miss?`${miss} place${miss===1?"":"s"} on the list ${miss===1?"has":"have"} no map location in the City record.`:"";
geo.slice().sort((a,b)=>(a.nw?1:0)-(b.nw?1:0)).forEach(r=>{const st=mark(r.id).c?2:r.nw?0:1;const c=L.circleMarker([r.y,r.x],MS[st]).bindPopup(pop(r),{maxWidth:280});c.addTo(LAY);MK[r.id]=c;});
if(refit&&geo.length){const bb=L.latLngBounds(geo.map(r=>[r.y,r.x]));if(geo.length===1)MAP.setView(bb.getCenter(),15,{animate:false});else MAP.fitBounds(bb,{padding:[40,40],maxZoom:15,animate:false});}}
function setView(v){F.view=v;document.querySelectorAll("[data-view]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.view===v)));$("#mapbox").hidden=v!=="map";$("#results").hidden=v==="map";
if(v==="map"){ensureMap();if(MAP){MAP.invalidateSize();drawMap(true);}}}
document.addEventListener("click",e=>{const b=e.target.closest("[data-show]");if(!b)return;const id=b.dataset.show;if(MAP)MAP.closePopup();F.v="all";F.q="";const q=$("#q");if(q)q.value="";
document.querySelectorAll(".seg button[data-v]").forEach(x=>x.setAttribute("aria-pressed",String(x.dataset.v==="all")));setView("list");drawList();
const c=document.querySelector(`.card[data-id="${CSS.escape(id)}"]`);if(c){c.scrollIntoView({block:"center"});c.classList.add("flash");c.setAttribute("tabindex","-1");c.focus({preventScroll:true});setTimeout(()=>c.classList.remove("flash"),2200);}});
function home(){const nNew=D.rows.filter(r=>r.nw).length,nPh=D.rows.filter(r=>r.ph).length,today=chicagoToday();
const stale=today&&D.asOfIso<today?`<p class="stale" role="status">This list is from ${esc(day(D.asOfIso))}. This morning's update has not arrived yet; it usually does by 8 am. Reload the page to check again.</p>`:"";
const noneToday=nNew?"":`<div class="empty">The City posted no new pest records since the last list. The places from the last 14 days are below.</div>`;
$("#app").innerHTML=`<h1>This morning's pest list</h1>
<p class="meta">Updated ${esc(wday(D.asOfIso))}, ${esc(D.asOf)}. City records through ${esc(D.through)}.</p>${stale}
<div class="tiles"><div class="tile key"><div class="lab">New this morning</div><div class="val num">${nNew}</div><div class="sub">posted since the last list</div></div>
<div class="tile"><div class="lab">Last 14 days</div><div class="val num">${D.rows.length}</div><div class="sub">pest places kept here</div></div>
<div class="tile"><div class="lab">Listed phone</div><div class="val num">${nPh} of ${D.rows.length}</div><div class="sub">name and address both matched</div></div></div>
${noneToday}
<div class="tools"><div class="search"><label class="sr" for="q">Search by name, street, ZIP or area</label><input id="q" type="search" placeholder="Search name, street, ZIP or area" value="${esc(F.q)}" autocomplete="off"></div>
<div class="seg" role="group" aria-label="Show">${[["all","All"],["new","New this morning"],["todo","Not called yet"]].map(([k,l])=>`<button type="button" data-v="${k}" aria-pressed="${F.v===k}">${l}</button>`).join("")}</div>
<div class="seg" role="group" aria-label="View">${[["list","List"],["map","Map"]].map(([k,l])=>`<button type="button" data-view="${k}" aria-pressed="${F.view===k}">${l}</button>`).join("")}</div>
<button class="btn ghost sm" type="button" id="csv"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>Download CSV</button></div>
<div class="mapbox" id="mapbox" ${F.view==="map"?"":"hidden"}><div class="map" id="map" role="region" aria-label="Map of the places on this list. The list view has the same places."></div>
<div class="legend" aria-hidden="true"><span><i class="l0"></i>New this morning</span><span><i class="l1"></i>Earlier mornings</span><span><i class="l2"></i>Called</span></div>
<p class="map-note" id="mapnote" hidden></p></div>
<div id="results" ${F.view==="map"?"hidden":""}></div>
<p class="meta" style="margin-top:22px">${STORE?"Called marks and notes stay in this browser on this device.":"This browser is not saving called marks or notes."}</p><p><button class="btn ghost sm" type="button" id="out">Sign out on this device</button></p>`;
drawList();
$("#q").addEventListener("input",e=>{F.q=e.target.value;drawList();});
document.querySelectorAll(".seg button[data-v]").forEach(b=>b.addEventListener("click",()=>{F.v=b.dataset.v;document.querySelectorAll(".seg button[data-v]").forEach(x=>x.setAttribute("aria-pressed",String(x===b)));drawList();}));
document.querySelectorAll("[data-view]").forEach(b=>b.addEventListener("click",()=>setView(b.dataset.view)));if(F.view==="map")setTimeout(()=>setView("map"),60);
$("#csv").addEventListener("click",csv);
$("#out").addEventListener("click",()=>{try{localStorage.removeItem(PKEY);sessionStorage.removeItem(PKEY);}catch(e){}location.hash="#/";location.reload();});
$("#results").addEventListener("change",e=>{const c=e.target.closest(".card");if(!c)return;const id=c.dataset.id;const m=MARKS[id]=mark(id);
if(e.target.dataset.act==="called"){m.c=e.target.checked;m.on=m.c?chicagoToday():"";c.classList.toggle("done",m.c);save();toast(m.c?"Marked as called":"Mark removed");drawMap(false);}});
$("#results").addEventListener("input",e=>{if(e.target.dataset.act!=="note")return;const id=e.target.closest(".card").dataset.id;const m=MARKS[id]=mark(id);m.n=e.target.value;save();});}
function cell(v){let s=String(v==null?"":v);if(/^[=+\-@\t\r]/.test(s))s="'"+s;return /[",\n\r]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;}
function csv(){const head=["Sent on","Business","Address","ZIP","Community area","Facility type","Phone","City result","Inspection type","Inspection date","Pest violation codes","Summary","Newer City result","Failed City inspections in 90 days (not counting license inspections)","City record","Called","Called on","Your note"];
const lines=[head.map(cell).join(",")].concat(D.rows.map(r=>{const m=mark(r.id);return[r.lo,r.n,r.a,r.z,r.ar,r.ty,r.ph,r.r,r.it,r.d,r.c.join(" "),r.s,r.lt,r.f90,r.rec,m.c?"Yes":"",m.on||"",m.n||""].map(cell).join(",");}));
const blob=new Blob(["﻿"+lines.join("\r\n")+"\r\n"],{type:"text/csv;charset=utf-8"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=D.fileName;
document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},500);toast("CSV downloaded");}
function termsHtml(){const ph=((D&&D.phoneAttr)||[]).concat(W.phoneLicenses);
return `<a class="back" href="#/">${D?"Back to today's list":"Back to sign in"}</a><h1>Terms of Use</h1><p class="ver">${esc(W.version.split(" | ").join(" · "))}</p>
${W.paras.map(p=>{const m=p.match(/^([^.]{2,40}\.)\s(.*)$/s);return m?`<p><b>${esc(m[1])}</b> ${esc(m[2])}</p>`:`<p>${esc(p)}</p>`;}).join("")}<h2>About this list</h2><p>${esc(W.notice)}</p><h2>City of Chicago data</h2><p>${esc(W.city)}</p>
<h2 id="th3">Phone number sources and licenses</h2>${ph.map(t=>`<p>${esc(t)}</p>`).join("")}`;}
function route(){const t=location.hash.startsWith("#/terms");$("#termsView").hidden=!t;
if(t){$("#termsView").innerHTML=termsHtml();$("#gateView").hidden=true;$("#app").hidden=true;document.title="Terms: Chicago Pest Daily List | ProofNotFluff";$("#main").focus({preventScroll:true});scrollTo(0,0);return;}
document.title="Members: Chicago Pest Daily List | ProofNotFluff";
if(D){$("#gateView").hidden=true;$("#app").hidden=false;if(!$("#results"))home();}else{$("#gateView").hidden=false;$("#app").hidden=true;}}
async function unlock(pw,keep,quiet){try{D=await openBox(pw);}catch(e){D=null;if(!quiet){$("#err").textContent="That password doesn't match. Check it on your Gumroad purchase page and try again.";$("#pw").focus();}return false;}
try{sessionStorage.setItem(PKEY,pw);}catch(e){}if(keep){try{localStorage.setItem(PKEY,pw);}catch(e){}}$("#err").textContent="";route();$("#main").focus({preventScroll:true});scrollTo(0,0);return true;}
$("#gate").addEventListener("submit",async e=>{e.preventDefault();const pw=$("#pw").value.trim();if(!pw){$("#err").textContent="Enter the seat password.";$("#pw").focus();return;}
$("#go").disabled=true;$("#go").textContent="Opening…";await unlock(pw,$("#keep").checked,false);$("#go").disabled=false;$("#go").textContent="Open today's list";});
$("#eye").addEventListener("click",()=>{const i=$("#pw"),on=i.type==="password";i.type=on?"text":"password";$("#eye").setAttribute("aria-pressed",String(on));$("#eye").setAttribute("aria-label",on?"Hide password":"Show password");});
$("#skip").addEventListener("click",e=>{e.preventDefault();const t=D||location.hash.startsWith("#/terms")?$("#main"):$("#pw");t.focus();});
window.addEventListener("hashchange",route);
(async()=>{let pw="";try{pw=sessionStorage.getItem(PKEY)||localStorage.getItem(PKEY)||"";}catch(e){}if(pw&&await unlock(pw,false,true))return;if(pw){try{localStorage.removeItem(PKEY);sessionStorage.removeItem(PKEY);}catch(e){}}route();})();
</script>
</body></html>""".replace("__LOCK__", ICO_LOCK)


def _planted():
    """A planted daily file: new and earlier pest rows, a hood-only row (never on the seat page), phones and no phones."""
    base = {"zip": "60601", "area": "Loop", "type": "Restaurant", "inspectionType": "Canvass", "fails90": 1, "lat": 41.88, "lon": -87.63,
            "phoneSource": "", "record": RL.RECORD + "1"}
    rows = lambda *xs: [dict(base, **x) for x in xs]
    items = rows({"place": "L1", "name": "Acme Tacos", "address": "1234 W Main St", "date": "2026-10-22", "result": "Fail", "trades": ["pests"],
                  "codes": {"pests": [38]}, "summary": "Fail on a canvass inspection, Oct 22, 2026. The City cited pests (code 38).",
                  "listedOn": "2026-10-24", "phone": "(312) 555-0101", "phoneSource": "overture:meta"},
                 {"place": "L2", "name": "Fry House", "address": "9 N State St", "date": "2026-10-22", "result": "Pass w/ Conditions", "trades": ["hood"],
                  "codes": {"hood": [56]}, "summary": "x", "listedOn": "2026-10-24", "phone": ""},
                 {"place": "L3", "name": "=Bad Name Cafe", "address": "77 E Lake St", "date": "2026-10-21", "result": "Pass w/ Conditions",
                  "trades": ["pests", "hood"], "codes": {"pests": [38], "hood": [56]}, "fails90": 2,
                  "summary": "Pass w/ Conditions on a complaint inspection, Oct 21, 2026. The City cited pests (code 38) and hood and exhaust (code 56).",
                  "listedOn": "2026-10-24", "phone": ""})
    earlier = rows({"place": "L4", "name": "Corner Mart", "address": "5 S Wells St", "type": "Grocery Store", "date": "2026-10-15", "result": "Fail",
                    "trades": ["pests"], "codes": {"pests": [38]}, "summary": "Fail on a canvass inspection, Oct 15, 2026. The City cited pests (code 38).",
                    "listedOn": "2026-10-23", "phone": "(773) 555-0199", "phoneSource": "website",
                    "later": {"date": "2026-10-22", "result": "Pass", "inspectionType": "Canvass Re-Inspection"}},
                   {"place": "L1", "name": "Acme Tacos", "address": "1234 W Main St", "date": "2026-10-10", "result": "Fail", "trades": ["pests"],
                    "codes": {"pests": [38]}, "summary": "old", "listedOn": "2026-10-20", "phone": ""})
    return {"product": "Chicago Restaurant Daily List", "asOf": "2026-10-24", "through": "2026-10-23", "recentFrom": "2026-10-10",
            "items": items, "earlier": earlier, "phoneNote": phones.ATTRIBUTION, "phoneTerms": phones.TERMS_LINES,
            "phoneAttribution": ["Data from Meta. Available under CDLA Permissive 2.0."]}


def selftest():
    import tempfile
    named = _planted()
    pl = payload(named)
    assert [r["n"] for r in pl["rows"]] == ["Acme Tacos", "=Bad Name Cafe", "Corner Mart"], "pest rows only, today first, one row per place"
    assert [r["nw"] for r in pl["rows"]] == [True, True, False] and pl["rows"][2]["lo"] == "2026-10-23"
    assert pl["rows"][0]["c"] == [38] and pl["rows"][1]["c"] == [38], "only pest codes in the code column"
    assert pl["rows"][2]["lt"] == "Newer City result: Pass on Oct 22, 2026, Canvass Re-Inspection." and pl["rows"][0]["lt"] == ""
    c = counts(named)
    assert c == {"asOf": "2026-10-24", "places14": 3, "new": 2, "withPhone14": 2, "coverage14": 66.7, "phonesChecked": True}, c
    pw = "planted-seat-pw"
    html = build_html(named, pw)
    for leak in ("Acme", "Corner Mart", "Main St", "555-0101", "Fry House", "Bad Name"):
        assert leak not in html, f"members' page shows list data outside the box: {leak}"
    box = json.loads(re.search(r"const BOX=(\{.*?\});", html).group(1))
    assert box["rounds"] == 250_000 and box["kdf"] == "PBKDF2-SHA256"
    got = json.loads(decrypt(pw, box))
    assert got["rows"][0]["ph"] == "(312) 555-0101" and got["phoneAttr"] == ["Data from Meta. Available under CDLA Permissive 2.0."]
    try:
        decrypt("wrong", box)
        raise SystemExit("seat_app selftest FAIL: a wrong password opened the box")
    except SystemExit:
        raise
    except Exception:
        pass
    words = json.loads(re.search(r"const W=(\{.*?\});\n", html).group(1))
    blob = " ".join(words["paras"])
    for line in phones.TERMS_LINES:
        assert line in blob, "the Legal desk's phone terms line is missing"
    lic = " ".join(words["phoneLicenses"])
    assert "CDLA" in lic and "Apache License" in lic, "phone-sources license texts missing"
    assert words["city"] == CITY_DISCLAIMER and "one's own risk" in CITY_DISCLAIMER
    assert "at most 3 Chicago pest control businesses at a time" in blob and "not capped" in blob and "no lock-in" in blob
    assert "password changes before the seat can be sold again" in blob and "leaves out license inspections" in blob and "renews each month" in blob
    assert terms_text("x")[0].startswith("ProofNotFluff LLC |")
    assert 'id="th3">Phone number sources and licenses' in html and 'content="noindex, nofollow"' in html
    assert "prefers-color-scheme:dark" in html and 'name="color-scheme" content="light dark"' in html
    assert "#/terms" in html and 'autocomplete="current-password"' in html
    for t in (html, __doc__, json.dumps(terms_text("Oct 24, 2026"))):
        assert chr(0x2014) not in t and chr(0x2013) not in t, "dash in the page"
    for w in ("dirty", "filthy", "infested", "unsanitary", "violator"):
        assert w not in html.lower() and w not in blob.lower(), w
    tmp = tempfile.mkdtemp()
    pub = os.path.join(tmp, "daily.json")
    json.dump({"asOf": "2026-10-24", "counts": {}}, open(pub, "w"))
    s = stamp(named, pub)
    pj = json.load(open(pub))
    assert pj["seat"] == s and "Acme" not in json.dumps(pj) and "555" not in json.dumps(pj), "stamp leaked a name or number"
    out = os.path.join(tmp, "m", "index.html")
    assert build(named, out, pw)["places14"] == 3 and os.path.isfile(out)
    no_phones = dict(named)
    no_phones.pop("phoneNote")
    assert payload(no_phones)["phonesChecked"] is False and counts(no_phones)["phonesChecked"] is False
    empty = dict(named, items=[], earlier=[])
    assert payload(empty)["rows"] == [] and counts(empty)["coverage14"] == 0.0
    print("seat_app selftest ok (5 planted rows: pest only, today first, one row per place, box and wrong password, "
          "phone terms lines, license texts, seat cap and no lock-in in the Terms, dark mode, counts-only stamp, empty list)")


if __name__ == "__main__":
    a = sys.argv[1:]
    pw_file = None
    if a[:1] == ["--pw-file"]:
        pw_file, a = a[1], a[2:]
    if a == ["--selftest"]:
        selftest()
    elif a[:1] == ["stamp"] and len(a) == 3:
        print(json.dumps(stamp(json.load(open(a[1])), a[2])))
    elif a[:1] == ["build"] and len(a) == 3:
        pw = open(pw_file).read().strip() if pw_file else os.environ.get(SECRET, "")
        if not pw:
            print(f"seat_app: {SECRET} not set; members' page not built")
            sys.exit(0)
        print(json.dumps(build(json.load(open(a[1])), a[2], pw)))
    else:
        raise SystemExit(__doc__)
