#!/usr/bin/env python3
"""The members' web app for Chicago Restaurant Inspection Leads (ProofNotFluff product 3, Oct 2026).

Same quality bar and the same parts as the construction product's app (tools/leads_app.py, whose stylesheet, Leaflet
pins and encryption this reuses by import, never by editing it): one AES-256-GCM box under a key derived with
PBKDF2-SHA256 at 250,000 rounds from the members' password (held only as the REST_LEADS_PASSWORD Actions secret and on
the Gumroad product's post-purchase content), decrypted in the buyer's browser. The repo holds only ciphertext.

Buyers: pest control, hood and exhaust cleaning, grease trap and drain, and commercial kitchen cleaning companies, and
vendors to new restaurants (POS, linen, cleaning). Their job: pick their trade, open the places with a fresh City record
in their category, see the place's inspection history, call the place.

Drill-in: overview (leads by trade), a filtered list with a map (#/list?l=flagged|opening|repeat&cat=&res=&area=&days=
&type=&new=1&fu=&q=&sort=&view=map), a place page with its 24-month City inspection history (#/place/<id>), the pitch
kit (#/pitch?b=<trade>) and the Terms (#/terms). Hash routes, so views can be bookmarked and the back button works.
Contacted marks, notes and the chosen trade live in that buyer's browser only (localStorage).

Wording rule: every screen states the City's recorded result, date and violation codes, with our category for each,
and the City's disclaimer word for word. Nothing says a place is dirty or unsafe, and no inspector note is shown.

Usage: REST_LEADS_PASSWORD=... python3 tools/rest_app.py DATA.json LEADS.xlsx docs/chicago-restaurant-leads-members/index.html
       python3 tools/rest_app.py --pw-file PATH DATA.json LEADS.xlsx OUT.html
       python3 tools/rest_app.py --selftest
"""
import base64, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from leads_page import decrypt, encrypt  # noqa: E402
import leads_app  # noqa: E402  (stylesheet and the Leaflet pins only)
from leads_xlsx import CITY_DISCLAIMER  # noqa: E402
from rest_leads import CATEGORIES, PRODUCT  # noqa: E402
from rest_xlsx import OUR_NOTICE, PITCH, PITCH_RULES, terms_text  # noqa: E402

PRICE = "39"
FREE_PAGE = "https://proofnotfluff.com/chicago-restaurant-inspection-leads/"
SLUG = "chicago-restaurant-leads-members"
LEGAL = ("Public City of Chicago food inspection records, as of __ASOF__. This site provides applications using data that has been "
         "modified for use from its original source, www.cityofchicago.org, the official website of the City of Chicago. The City of "
         "Chicago makes no claims as to the content, accuracy, timeliness, or completeness of any of the data provided at this site. The "
         "data provided at this site is subject to change at any time. It is understood that the data provided at this site is being "
         "used at one's own risk. ProofNotFluff is not affiliated with or endorsed by the City of Chicago, and no business listed has "
         "endorsed or works with ProofNotFluff. A listing repeats the City's recorded result and violation codes; it does not say a place "
         "is clean, safe or open today. You make your own calls and emails and are responsible for following the law when you do. "
         "Licensed to one business for its own prospecting; no reselling or republishing. Provided as is, without warranties of any kind, "
         "to the extent the law allows, and ProofNotFluff's total liability for any claim is limited to the amount you paid for the most "
         "recent month of your membership. Made with AI assistance. Read the full Terms of Use (also on the Terms tab of the Excel file).")
TERMS_LINK = "Terms of Use"


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def base_css():
    """The construction app's stylesheet, read from tools/leads_app.py so the two products look like one family."""
    return re.search(r"<style>(.*?)</style>", leads_app.PAGE, re.S).group(1)


def payload(data, xlsx_bytes):
    P, I = data["places"], data["inspections"]
    titles = {}
    for x in I.values():
        for code, title in x["v"]:
            titles[str(code)] = title
    places = []
    for p in P.values():
        places.append({"id": p["id"], "n": p["name"], "k": p["aka"], "a": p["address"], "z": p["zip"], "ar": p["area"], "ty": p["type"],
                       "rk": p["risk"], "lic": p.get("licenses") or ([p["license"]] if p["license"] else []), "lat": p["lat"], "lon": p["lon"],
                       "ls": p["lists"], "cb": p["catsBy"], "lc": p["leadCats"], "al": p["alsoBy"], "nb": p["newBy"], "nw": p["new"], "f90": p["fails90"], "fl": p["flaggedIds"], "op": p["openingIds"],
                       "fa": p["failIds"], "lt": p["latestId"], "h": p["history"]})
    insp = {i: {"d": x["d"], "t": x["t"], "r": x["r"], "v": [c for c, _ in x["v"]], "c": x["c"]} for i, x in I.items()}
    return {"asOf": data["asOfText"], "asOfIso": data["asOf"], "through": data["through"], "throughText": data["throughText"],
            "window": data["window"], "cats": data["categories"], "titles": titles, "places": places, "insp": insp,
            "lists": data["lists"], "counts": {k: v for k, v in data["counts"].items() if k != "areas"},
            "record": data["source"]["record"], "fileName": f"chicago-restaurant-inspection-leads-{data['asOf']}.xlsx",
            "xlsx": base64.b64encode(xlsx_bytes).decode()}


def legal_html():
    assert LEGAL.count(TERMS_LINK) == 1
    return _esc(LEGAL).replace(TERMS_LINK, f'<a href="#/terms">{TERMS_LINK}</a>')


def terms_json(as_of, city_terms):
    t = terms_text(as_of)
    return json.dumps({"version": t[0], "paras": t[1:], "city": CITY_DISCLAIMER, "cityTerms": city_terms, "notice": OUR_NOTICE},
                      ensure_ascii=False).replace("</", "<\\/")


def pitch_json():
    return json.dumps({"kits": PITCH, "rules": PITCH_RULES}, ensure_ascii=False).replace("</", "<\\/")


def build_html(data, xlsx_bytes, password):
    box = encrypt(password, json.dumps(payload(data, xlsx_bytes), separators=(",", ":")).encode())
    js, jsi = leads_app.LEAFLET_JS
    css, cssi = leads_app.LEAFLET_CSS
    return (PAGE.replace("__BASECSS__", base_css()).replace("__BOX__", json.dumps(box))
            .replace("__TERMS__", terms_json(data["asOfText"], data["source"]["terms"])).replace("__PITCH__", pitch_json())
            .replace("__LEGAL__", legal_html()).replace("__ASOF__", data["asOfText"]).replace("__FREE__", FREE_PAGE)
            .replace("__SURVEY__", leads_app.survey_url(PRODUCT)).replace("__PRICE__", PRICE).replace("__LJS__", js).replace("__LJSI__", jsi).replace("__LCSS__", css).replace("__LCSSI__", cssi))


def build(data, xlsx_path, out, password):
    html = build_html(data, open(xlsx_path, "rb").read(), password)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    return {k: data["counts"][k] for k in ("places", "flagged", "opening", "repeat", "new")} | {"bytes": len(html)}


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex, nofollow"><meta name="theme-color" content="#1D2433">
<title>Members: Chicago Restaurant Inspection Leads | ProofNotFluff</title>
<link rel="preload" href="../assets/fonts/inter-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../assets/fonts/poppins-700.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="__LCSS__" integrity="__LCSSI__" crossorigin="anonymous">
<script defer src="__LJS__" integrity="__LJSI__" crossorigin="anonymous"></script>
<style>__BASECSS__
/* ---- restaurant leads additions ---- */
:root{--fail:#A63E21;--fail-bg:#FBEAE4;--pwc:#7A5A12;--pwc-bg:#F6EDD5;--pass:#2E6B66;--pass-bg:#E3EFED;--nr:#2F5F9E;--nr-bg:#E6EDF6;--oth:#3A4152;--oth-bg:#ECE6DA}
.res{display:inline-flex;align-items:center;gap:6px;height:26px;padding:0 10px;border-radius:999px;font-size:12.5px;font-weight:700;white-space:nowrap;line-height:1}
.res i{width:8px;height:8px;border-radius:50%;background:currentColor;flex:none}
.res.fail{color:var(--fail);background:var(--fail-bg)}.res.pwc{color:var(--pwc);background:var(--pwc-bg)}.res.pass{color:var(--pass);background:var(--pass-bg)}
.res.nr{color:var(--nr);background:var(--nr-bg)}.res.oth{color:var(--oth);background:var(--oth-bg)}
.res.lg{height:32px;padding:0 14px;font-size:14px}
.res.fail i{border-radius:2px;width:8px;height:8px}
.cat{display:inline-flex;align-items:center;gap:5px;height:26px;padding:0 9px 0 7px;border-radius:7px;font-size:12.5px;font-weight:600;color:var(--ink2);background:#F3F0EA;border:1px solid var(--line2);white-space:nowrap}
.cat .ico{width:15px;height:15px;color:var(--muted)}
.cat.on{background:#fff;border-color:#CFC8BB;color:var(--ink)}
.row .mn{font:700 17px/1.25 var(--head);letter-spacing:-.005em}
.row .mn small{font:500 13px var(--body)}
.row .bd{flex-wrap:wrap;gap:4px 8px}
.row .when{color:var(--ink2);font-size:14px}
.row .rt{max-width:340px}
.badge.rep{background:var(--fail-bg);color:var(--fail)}
.badge.since{background:var(--pass-bg);color:var(--pass)}
/* overview: leads by trade (the signature) */
.trades{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin:22px 0 26px}
@media(max-width:1100px){.trades{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:700px){.trades{grid-template-columns:minmax(0,1fr);gap:8px}}
.trade{position:relative;display:flex;flex-direction:column;gap:2px;padding:16px 16px 14px;border-radius:var(--r);background:#fff;border:1px solid var(--line);box-shadow:var(--sh);text-decoration:none;color:var(--ink);min-width:0}
.trade .ti{display:grid;place-items:center;width:40px;height:40px;border-radius:10px;background:var(--paper);color:var(--ink2);margin:0 0 10px}
.trade .ti .ico{width:22px;height:22px}
.trade .tn{font:700 34px/1 var(--head);letter-spacing:-.02em;margin:0 0 6px}
.trade .tt{font-weight:600;font-size:15px}
.trade .tm{color:var(--muted);font-size:13.5px}
.trade .tm b{color:var(--accent-ink)}
.trade.mine{background:var(--ink);border-color:var(--ink);color:#fff}
.trade.mine .ti{background:rgba(255,255,255,.1);color:#fff}.trade.mine .tm{color:#C9CFDB}.trade.mine .tm b{color:#F7B9A5}
.trade .yt{position:absolute;right:12px;top:12px;font-size:11.5px;font-weight:700;letter-spacing:.04em;padding:4px 8px;border-radius:6px;background:var(--accent);color:#fff}
@media(hover:hover){.trade:hover .tt{text-decoration:underline;text-underline-offset:3px}}
@media(max-width:700px){.trade{display:grid;grid-template-columns:40px minmax(0,1fr) auto;column-gap:14px;align-items:center;padding:12px 14px}
 .trade .ti{margin:0;grid-row:1 / span 2}.trade .tn{grid-column:3;grid-row:1 / span 2;font-size:28px;margin:0;text-align:right}.trade .tt{grid-column:2}.trade .tm{grid-column:2}
 .trade .yt{position:static;grid-column:2;justify-self:start;margin:4px 0 0;order:3}}
.pick{display:flex;flex-wrap:wrap;align-items:center;gap:10px 14px;margin:14px 0 0}
.pick .fld select{max-width:280px}
.pick p{margin:0;color:var(--muted);font-size:14px}
.lists3{display:flex;flex-wrap:wrap;gap:8px 20px;margin:0;padding:12px 20px 18px;font-size:14px;color:var(--muted)}
.lists3 a{font-weight:600}
/* place page */
.why{padding:20px}
.why h2{font-size:17px;font-weight:600;margin:0 0 14px}
.why .top{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin:0 0 14px}
.why .top .dt{font-weight:600;font-size:15px}.why .top .ty{color:var(--muted);font-size:14.5px}
.cv{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.cv li{display:grid;grid-template-columns:auto minmax(0,1fr);gap:4px 12px;align-items:start;padding:12px 14px;border-radius:10px;background:var(--paper)}
.cv li .cat{background:#fff}
.cv li p{margin:3px 0 0;font-size:14px;color:var(--ink2)}
.cv li p b{color:var(--ink);font-weight:600}
.cv .src{grid-column:1 / -1}
.tl{list-style:none;margin:0;padding:0 20px 8px}
.tl>li{position:relative;padding:0 0 18px 28px}
.tl>li::before{content:"";position:absolute;left:6px;top:20px;bottom:-2px;width:2px;background:var(--line)}
.tl>li:last-child::before{display:none}
.tl .dot{position:absolute;left:0;top:6px;width:14px;height:14px;border-radius:50%;border:2px solid currentColor;background:#fff}
.tl .dot.fail{color:var(--fail);background:var(--fail)}.tl .dot.pwc{color:var(--pwc);background:var(--pwc-bg)}.tl .dot.pass{color:var(--pass)}.tl .dot.nr{color:var(--nr)}.tl .dot.oth{color:var(--oth)}
.tl .hd{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px}
.tl .hd b{font-size:15px;font-weight:600}.tl .hd span.t{color:var(--muted);font-size:14px}
.tl .cs{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 0}
.tl details{margin:8px 0 0}
.tl summary{display:inline-flex;align-items:center;min-height:44px;margin:-10px 0 -8px;cursor:pointer;color:var(--blue);font-weight:600;font-size:14px;list-style:none}
.tl summary::-webkit-details-marker{display:none}
.tl summary::after{content:"";width:8px;height:8px;margin-left:8px;border-right:2px solid currentColor;border-bottom:2px solid currentColor;transform:rotate(45deg) translateY(-2px);transition:transform .15s}
.tl details[open] summary::after{transform:rotate(-135deg) translateY(-2px)}
.tl .vl{list-style:none;margin:6px 0 0;padding:0;display:grid;gap:4px;font-size:14px;color:var(--ink2)}
.tl .vl li{display:grid;grid-template-columns:2.4rem minmax(0,1fr);gap:8px}
.tl .vl li b{font-variant-numeric:tabular-nums;color:var(--ink);text-align:right}
.tl .vl li.k b{color:var(--accent-ink)}
.tl .rl{font-size:13.5px;margin:8px 0 0}
.tl .lead{border-radius:10px;background:#FBFAF7;box-shadow:0 0 0 1px var(--line2);margin:0 -10px;padding:10px 10px 12px}
.tl li.on .lead .flagt{display:inline-flex}
.flagt{display:none;font-size:12px;font-weight:700;color:var(--accent-ink);letter-spacing:.02em}
.acts .btn{min-height:44px}
.lic{font-variant-numeric:tabular-nums}
/* lists */
.lsw{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 14px}
.lsw a{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 16px;border-radius:999px;border:1px solid var(--line);background:#fff;color:var(--ink);font-weight:600;font-size:14.5px;text-decoration:none}
.lsw a .c{color:var(--muted)}
.lsw a[aria-current=page]{background:var(--ink);border-color:var(--ink);color:#fff}.lsw a[aria-current=page] .c{color:#C9CFDB}
@media(max-width:860px){.lsw{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;margin:0 -16px 12px;padding:0 16px}.lsw::-webkit-scrollbar{display:none}.lsw a{flex:none}}
.ldesc{margin:-6px 0 16px;color:var(--muted);font-size:14.5px;max-width:80ch}
.lg-f{width:12px;height:12px;background:#C8502F;box-shadow:0 0 0 2px #fff,0 0 0 3px #A63E21;border-radius:2px!important;margin:0 2px}
.lg-c{width:11px;height:11px;background:#E0B54A;border:2px solid #7A5A12;margin:0 2px}
.lg-p{width:10px;height:10px;background:#fff;border:2px solid #2E6B66;margin:0 2px}
.lg-o{width:10px;height:10px;background:#2F5F9E;margin:0 2px}
/* pitch kit */
.bk{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 18px}
@media(max-width:860px){.bk{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;margin:0 -16px 16px;padding:0 16px}.bk::-webkit-scrollbar{display:none}}
.bk a{flex:none;display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid var(--line);background:#fff;color:var(--ink);font-weight:600;font-size:14.5px;text-decoration:none}
.bk a[aria-current=page]{background:var(--ink);border-color:var(--ink);color:#fff}
.call{font-size:16px;line-height:1.6;color:var(--ink);margin:0;padding:16px 18px;border-radius:10px;background:var(--paper)}
.rules{margin:18px 0 0;padding:0 0 0 20px;color:var(--ink2);font-size:14.5px}.rules li{margin:0 0 6px}
/* design director round 1 */
.row{grid-template-columns:minmax(0,1fr) 172px}
.row .rt{grid-row:1 / span 4;flex-direction:column;align-items:flex-end;flex-wrap:nowrap;max-width:none;gap:6px}
.row .bd.cs{margin-top:8px;gap:6px}
.row .nwt{color:var(--accent-ink);font-weight:700}
.row .also{font-size:13px;color:var(--muted);align-self:center;margin-left:2px}
.row .ftx{color:var(--fail);font-weight:700}
.row .ctx{color:var(--teal);font-weight:700;display:inline-flex;align-items:center;gap:4px}
.res.nw{height:24px;font-size:12px;font-weight:600}
@media(max-width:600px){.row{grid-template-columns:minmax(0,1fr)}.row .rt{grid-row:auto;flex-direction:row;align-items:center;flex-wrap:wrap}}
.lg-f{width:12px;height:12px;background:#C8502F;box-shadow:0 0 0 1.5px #fff,0 0 0 2.5px #A63E21;border-radius:2px!important;margin:0 3px}
.pin-f{background:#C8502F;border:1.5px solid #fff;box-shadow:0 0 0 1px #A63E21,0 1px 3px rgba(29,36,51,.3);border-radius:2px;box-sizing:border-box}
.pin-f.hot{background:#1D2433;box-shadow:0 0 0 2px #C8502F}
@media(max-width:860px){.tool .seg:not(.vtog) button[data-k=""]{order:0}}
.pg{grid-template-rows:auto auto 1fr}
.pg-side{grid-row:1 / span 3}
.pg-facts{grid-column:1;grid-row:3;min-width:0}
@media(max-width:1020px){.pg-side,.pg-facts{grid-row:auto}}
.facts dd.nv{color:var(--muted);font-weight:400}
.tl .vl li{grid-template-columns:28px minmax(0,1fr)}
.tl .vl{margin-left:0}
@media(max-width:600px){.mini-b{padding:12px 16px}.mine{padding:0 16px 16px}}
.mini-b .r{min-width:84px;max-width:96px}.mini-b span .dt{white-space:nowrap}
@media(max-width:600px){.bars .hd{min-height:0;padding:0;margin:0 0 2px}}
.trade .yt{font-size:12px;font-weight:600;letter-spacing:0}
/* design director round 2 */
.row{grid-template-columns:minmax(0,1fr) auto}
.row .rt{grid-row:1 / span 2;max-width:240px}
.row .bd.mt,.row .bd.cs,.row .also{grid-column:1 / -1}
.row .bd.mt{flex-wrap:wrap;gap:2px 0}
.row .bd.mt .mi{white-space:nowrap;overflow:visible;display:inline-flex;align-items:center;gap:7px}
.row .bd.mt .mi .dot{margin:0 0 0 7px}
.row .also{display:block;font-size:13px;color:var(--muted);margin:6px 0 0;white-space:normal;text-wrap:pretty}
.facts dd .dn{font-size:12px;font-weight:400;color:var(--muted);margin-left:4px;white-space:nowrap}
.ph p .nd{white-space:nowrap}
@media(max-width:600px){.row{grid-template-columns:minmax(0,1fr)}.row .rt{grid-row:auto;max-width:none}}
.pick{align-items:flex-end}.pick p{line-height:40px}
@media(max-width:860px){.pick p{line-height:44px}}
@media(max-width:600px){.pick{row-gap:8px}.pick p{line-height:1.4;flex-basis:100%}}
.pk-h{align-items:center;margin:0 0 4px}.pk .sub{margin:0 0 14px;font-size:13.5px;color:var(--muted)}
.call .f{color:var(--blue);font-weight:700}
.terms{max-width:760px}.terms .tx p{max-width:none}
#fsheetH:focus{outline:none;box-shadow:none}
</style></head><body>
<a class="skip" href="#/" id="skip">Skip to main content</a>
<header class="bar"><div class="bar-in">
<a class="brand" href="#/" aria-label="ProofNotFluff, Chicago Restaurant Inspection Leads, overview"><b>ProofNotFluff</b><span class="marks" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></span><small>Chicago Restaurant Inspection Leads</small></a>
<nav class="tabs" id="tabs" aria-label="Sections" hidden></nav>
<span class="bar-sp"></span>
<button class="dl" id="dlTop" type="button" hidden><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg><span>Download workbook</span><b class="sr">Download this week's Excel workbook</b></button>
</div></header>
<main id="gateView" class="gate">
<form class="gate-card" id="gate" novalidate>
<span class="chip s2"><svg class="ico s" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>Members</span>
<h1>This week's Chicago restaurant leads</h1>
<p class="sub">List of __ASOF__. Food businesses with a fresh City of Chicago inspection record, sorted for pest control, hood cleaning, grease trap and kitchen cleaning companies, plus places with a new license inspection.</p>
<label for="pw">Members' password</label>
<div class="pw"><input id="pw" type="password" autocomplete="current-password" autocapitalize="off" spellcheck="false" required aria-describedby="err pwHelp">
<button type="button" class="eye" id="eye" aria-label="Show password" aria-pressed="false"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/><path id="eyeslash" d="M3 3l18 18" hidden/></svg></button></div>
<button class="btn pri" type="submit" id="go">Open this week's list</button>
<p class="err" id="err" role="alert"></p>
<div class="gate-help" id="pwHelp"><p>The password is on your Gumroad purchase page, linked from your receipt email. <a href="https://gumroad.com/library">Open your Gumroad library</a></p>
<p>Not a member yet? <a href="__FREE__">See the free sample</a></p></div>
</form>
</main>
<p class="gate-legal" id="gateLegal">__LEGAL__</p>
<main id="app" class="page" hidden tabindex="-1"></main>
<footer class="foot-legal" id="appLegal" hidden><p>__LEGAL__</p><p>List of __ASOF__. Questions about your membership? Reply to your Gumroad receipt.</p><p class="leave">Thinking of cancelling? <a href="__SURVEY__" target="_blank" rel="noopener">Tell us why first<span class="sr"> (opens in a new tab)</span></a>. It takes a minute and decides what we fix next.</p></footer>
<nav class="bnav" id="bnav" aria-label="Sections" hidden></nav>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script>
"use strict";
const BOX=__BOX__;
const PITCH=__PITCH__;
const TERMS=__TERMS__;
const b64=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
async function openBox(pw){const k0=await crypto.subtle.importKey("raw",new TextEncoder().encode(pw),"PBKDF2",false,["deriveKey"]);
const key=await crypto.subtle.deriveKey({name:"PBKDF2",salt:b64(BOX.salt),iterations:BOX.rounds,hash:"SHA-256"},k0,{name:"AES-GCM",length:256},false,["decrypt"]);
const pt=await crypto.subtle.decrypt({name:"AES-GCM",iv:b64(BOX.iv)},key,b64(BOX.ct));return JSON.parse(new TextDecoder().decode(pt));}
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const int=n=>Math.round(+n||0).toLocaleString("en-US");
const MON=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
function day(s){const m=/^(\d{4})-(\d{2})-(\d{2})/.exec(s||"");return m?MON[+m[2]-1]+" "+(+m[3])+", "+m[1]:"";}
function dayShort(s){const m=/^(\d{4})-(\d{2})-(\d{2})/.exec(s||"");return m?MON[+m[2]-1]+" "+(+m[3]):"";}
const plural=(n,a,b)=>int(n)+" "+(n===1?a:(b||a+"s"));
const sent=s=>{s=String(s||"").toLowerCase();return (s.charAt(0).toUpperCase()+s.slice(1)).replace(/\bchicago\b/g,"Chicago");};
const I={phone:'<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
mail:'<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
copy:'<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h8"/>',
pin:'<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
search:'<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',filter:'<path d="M4 6h16M7 12h10M10 18h4"/>',check:'<path d="m5 12.5 4.5 4.5L19 7.5"/>',
back:'<path d="M15 18l-6-6 6-6"/>',chev:'<path d="m9 6 6 6-6 6"/>',x:'<path d="M6 6l12 12M18 6 6 18"/>',list:'<path d="M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01"/>',
map:'<path d="M9 4 3 6.5v13.5L9 17.5l6 2.5 6-2.5V4l-6 2.5z"/><path d="M9 4v13.5M15 6.5V20"/>',
home:'<path d="M3 10.5 12 4l9 6.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/>',
kit:'<path d="M8 4h8M9 4V3h6v1M6 6h12v15H6z"/><path d="M9 11h6M9 15h6"/>',csv:'<path d="M14 3H6v18h12V7z"/><path d="M14 3v4h4M9 13h6M9 17h6"/>',
ext:'<path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
pests:'<ellipse cx="12" cy="13.5" rx="4.2" ry="5.5"/><path d="M12 8V5.5M9.5 4.5 11 6M14.5 4.5 13 6M7.8 11H4.5M7.8 15H4.5M8.4 18.5 6 20.5M16.2 11h3.3M16.2 15h3.3M15.6 18.5l2.4 2"/>',
hood:'<path d="M4 15h16l-3-7H7z"/><path d="M10 8V3h4v5M7 18.5h2M11 18.5h2M15 18.5h2"/>',
drain:'<path d="M12 3s-6 6.6-6 11a6 6 0 0 0 12 0c0-4.4-6-11-6-11z"/><path d="M9 14.5a3 3 0 0 0 3 3"/>',
clean:'<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6.3 6.3l2.4 2.4M15.3 15.3l2.4 2.4M6.3 17.7l2.4-2.4M15.3 8.7l2.4-2.4"/>',
opening:'<path d="M4 10 6 4h12l2 6"/><path d="M4 10a2.7 2.7 0 0 0 5.3 0 2.7 2.7 0 0 0 5.4 0 2.7 2.7 0 0 0 5.3 0M5.5 12.5V20h13v-7.5M10 20v-4.5h4V20"/>',
repeat:'<path d="M4 12a8 8 0 0 1 13.7-5.6L20 9M20 4v5h-5M20 12a8 8 0 0 1-13.7 5.6L4 15M4 20v-5h5"/>',
flag:'<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',doc:'<path d="M14 3H6v18h12V7z"/><path d="M14 3v4h4"/>'};
const ico=(n,c)=>`<svg class="ico${c?" "+c:""}" viewBox="0 0 24 24" aria-hidden="true">${I[n]}</svg>`;
function toast(t){const el=$("#toast");el.textContent=t;el.classList.add("on");clearTimeout(toast.t);toast.t=setTimeout(()=>el.classList.remove("on"),2500);}
function untoast(){clearTimeout(toast.t);$("#toast").classList.remove("on");}
async function copyText(t){try{await navigator.clipboard.writeText(t);return true;}catch(e){const a=document.createElement("textarea");a.value=t;a.setAttribute("readonly","");a.style.position="fixed";a.style.opacity="0";document.body.appendChild(a);a.select();let ok=false;try{ok=document.execCommand("copy");}catch(x){}a.remove();return ok;}}

/* results, categories, lists */
const RES=r=>{const u=String(r||"").toUpperCase();return u==="FAIL"?"fail":u==="PASS W/ CONDITIONS"?"pwc":u==="PASS"?"pass":u==="NOT READY"?"nr":"oth";};
const res=(r,lg,pre,post,cls)=>`<span class="res ${RES(r)}${lg?" lg":""}${cls?" "+cls:""}"><i aria-hidden="true"></i>${pre?esc(pre):""}${esc(r)}${post?" "+esc(post):""}</span>`;
let CATS=[],CAT={};
const cat=(k,on)=>`<span class="cat${on?" on":""}">${ico(k)}${esc(CAT[k].short)}</span>`;
const LISTS={flagged:{t:"Failed or conditional",s:"City result Fail or Pass w/ Conditions in the last 30 days, with a violation in at least one category.",ids:"fl"},
 opening:{t:"Opening soon",s:"A license inspection in the last 30 days. Chicago inspects a food business before it issues a food license, so many of these places are about to open or just opened.",ids:"op"},
 repeat:{t:"Failed more than once",s:"Two or more failed routine, complaint or re-inspections in 90 days, at least one in the last 30, with a violation in at least one category.",ids:"fa"}};
const TRADES=[["pests","Pest control","flagged","pests"],["hood","Hood cleaning","flagged","hood"],["drain","Grease trap and drains","flagged","drain"],["clean","Kitchen cleaning","flagged","clean"],["opening","New openings","opening",""]];

/* private marks, notes and trade: this browser only */
const SKEY="pnf-rest-v1",TKEY="pnf-rest-trade";let MARKS={},STORE_OK=true,TRADE="";
try{const t="__pnf";localStorage.setItem(t,"1");localStorage.removeItem(t);MARKS=JSON.parse(localStorage.getItem(SKEY)||"{}")||{};TRADE=localStorage.getItem(TKEY)||"";}catch(e){STORE_OK=false;MARKS={};}
function saveMarks(){try{localStorage.setItem(SKEY,JSON.stringify(MARKS));return true;}catch(e){STORE_OK=false;return false;}}
function setTrade(k){TRADE=k;try{localStorage.setItem(TKEY,k);}catch(e){}}
const mk=id=>MARKS[id]||{};
function setMark(id,patch){const m=Object.assign({},mk(id),patch);if(!m.c&&!(m.n||"").trim())delete MARKS[id];else MARKS[id]=m;return saveMarks();}
const STORE_LINE=()=>STORE_OK?"Saved in this browser on this device only. Nobody else sees it, including ProofNotFluff. Clearing your browser data removes it.":"This browser is blocking storage, so contacted marks and notes will be lost when you close the page.";

let D,P,BYID,INS;
const STATE={trail:[],map:null,mini:null};
function prep(d){D=d;P=d.places;INS=d.insp;BYID={};P.forEach(p=>{BYID[p.id]=p;});CATS=d.cats.map(c=>c.key);CAT={};d.cats.forEach(c=>{CAT[c.key]=c;});
P.forEach(p=>{p.lead={flagged:p.fl[0],opening:p.op[0],repeat:p.fa[0]};p.since={};
 const lt=INS[p.lt];for(const l of p.ls){const x=INS[p.lead[l]];if(x&&p.lt!==p.lead[l]&&lt.d>x.d)p.since[l]=lt;}});}
const leadOf=(p,l)=>INS[p.lead[l]||p.lead[p.ls[0]]];

/* routing */
function parse(){const h=(location.hash||"#/").slice(1);const i=h.indexOf("?");const path=i<0?h:h.slice(0,i);return{parts:path.split("/").filter(Boolean).map(decodeURIComponent),q:new URLSearchParams(i<0?"":h.slice(i+1))};}
function go(h){location.hash=h;}
function back(fallback){if(STATE.trail.length>1)history.back();else go(fallback);}
function onHash(){const h=location.hash||"#/";const t=STATE.trail;if(t.length>1&&t[t.length-2]===h)t.pop();else if(t[t.length-1]!==h)t.push(h);route(true);}
function setNav(v){const items=[["overview","#/","Overview","home"],["flagged","#/list","Leads","list"],["opening","#/list?l=opening","Openings","opening"],["pitch","#/pitch","Pitch kit","kit"]];
const html=items.map(([k,h,t,i])=>`<a href="${h}"${k===v?' aria-current="page"':""}>${ico(i)}${t}</a>`).join("");$("#tabs").innerHTML=html;$("#bnav").innerHTML=html;}
function route(scroll){const {parts,q}=parse();const v=parts[0]||"overview";
untoast();for(const k of ["map","mini"]){const m=STATE[k];if(m){try{m.stop();m.off();m.remove();}catch(e){}STATE[k]=null;}}closeSheet();
const app=$("#app");let nav=v;
if(v==="list"){const l=viewList(q);nav=l==="opening"?"opening":"flagged";}
else if(v==="place"&&BYID[parts[1]]){viewPlace(BYID[parts[1]],q.get("from"));nav=(q.get("from")==="opening")?"opening":"flagged";}
else if(v==="pitch")viewPitch(q);
else if(v==="terms"){viewTerms();nav="";}
else if(v==="place"){app.innerHTML=`<div class="panel empty"><h3>That place is not on this week's list</h3><p>Places leave the list when their City record is more than 30 days old.</p><a class="btn ink" href="#/list">See this week's leads</a></div>`;nav="flagged";document.title="Not on this week's list | Chicago Restaurant Inspection Leads";}
else{viewOverview();nav="overview";}
setNav(nav);app.classList.remove("view-enter");void app.offsetWidth;app.classList.add("view-enter");
if(scroll){window.scrollTo(0,0);const h=app.querySelector("h1");if(h){h.setAttribute("tabindex","-1");h.focus({preventScroll:true});}}}

/* a row in any list */
function row(p,l,ov){const x=leadOf(p,l);const m=mk(p.id);const cats=(p.lc[l]||[]);const nw=p.since[l];const also=p.al[l]||[];
const meta=[p.nb[l]&&!ov?'<span class="nwt">New</span>':"",`<span class="when">${dayShort(x.d)}, ${esc(x.t)}</span>`,
 l!=="opening"&&p.f90>=2?`<span class="ftx">${int(p.f90)} fails in 90 days</span>`:"",
 m.c?`<span class="ctx">${ico("check","s")}Contacted</span>`:""].filter(Boolean).map((t,i)=>`<span class="mi">${i?'<span class="dot" aria-hidden="true">&middot;</span>':""}${t}</span>`).join("");
return `<li><a class="row" href="#/place/${encodeURIComponent(p.id)}?from=${l}" data-id="${esc(p.id)}">
<span class="mn">${esc(p.n)}${p.ty&&p.ty!=="Not given"&&p.ty!=="Restaurant"?`<small>${esc(p.ty)}</small>`:""}</span>
<span class="ad">${esc(p.a)}${p.ar?`<span class="ar">, ${esc(p.ar)}</span>`:""}</span>
<span class="bd mt">${meta}</span>${cats.length?`<span class="bd cs">${cats.map(k=>cat(k)).join("")}</span>`:""}${also.length?`<span class="also">Also cited in the last ${l==="repeat"?"90":"30"} days: ${also.map(a=>esc(CAT[a.cat].short)+" ("+dayShort(a.d)+")").join(", ")}</span>`:""}
<span class="rt">${l==="opening"?res(x.r,0,"License: "):res(x.r)}${nw&&l!=="opening"?res(nw.r,0,"Newer: ",dayShort(nw.d),"nw"):""}</span>${ico("chev","chev")}</a></li>`;}
function rowsHtml(list,l,limit,ov){if(!list.length)return "";const n=Math.min(limit||list.length,list.length);return `<ul class="list-rows">${list.slice(0,n).map(p=>row(p,l,ov)).join("")}</ul>`;}
const inList=l=>D.lists[l].map(id=>BYID[id]);
function tradeRows(t){const tr=TRADES.find(x=>x[0]===t);if(!tr)return inList("flagged");return inList(tr[2]).filter(p=>!tr[3]||p.cb[tr[2]].includes(tr[3]));}
const tradeHref=t=>{const tr=TRADES.find(x=>x[0]===t);return tr[2]==="opening"?"#/list?l=opening":"#/list?cat="+tr[3];};

/* overview */
function viewOverview(){document.title="Overview | Chicago Restaurant Inspection Leads";
const c=D.counts,fl=inList("flagged"),op=inList("opening"),rp=inList("repeat");
const t=TRADES.find(x=>x[0]===TRADE);
const tile=([k,name,l,cf])=>{const rows=tradeRows(k);const nw=rows.filter(p=>p.nb[l]).length;const mine=k===TRADE;
return `<a class="trade${mine?" mine":""}" href="${tradeHref(k)}">${mine?'<span class="yt">Your trade</span>':""}<span class="ti">${ico(k)}</span><span class="tn num">${int(rows.length)}</span><span class="tt">${esc(name)}</span><span class="tm num">${nw?`<b>${int(nw)} new</b> this week`:"none new this week"}</span></a>`;};
const newest=(t?tradeRows(TRADE):fl).slice(0,6),tl=t?t[2]:"flagged";
const ac={};fl.concat(op).forEach(p=>{if(p.ar){const a=ac[p.ar]=ac[p.ar]||[0,0];a[p.ls.includes("flagged")?0:1]++;}});
const areas=Object.entries(ac).map(([a,v])=>[a,v[0]+v[1],v]).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).slice(0,8);const amax=areas.length?areas[0][1]:1;
const marked=Object.keys(MARKS).filter(id=>BYID[id]);const cN=marked.filter(id=>MARKS[id].c).length,nN=marked.filter(id=>(MARKS[id].n||"").trim()).length;
$("#app").innerHTML=`<section class="hero"><h1>${int(c.flagged)} places failed or passed with conditions in the last 30 days, and ${int(c.opening)} had a license inspection</h1>
<p>From City of Chicago food inspection records through ${esc(D.throughText)}. List of ${esc(D.asOf)}. Pick your trade to see your leads first.</p>
<div class="pick"><div class="fld"><label for="trade">Your trade</label><select id="trade"><option value="">All trades</option>${TRADES.map(([k,n])=>`<option value="${k}"${k===TRADE?" selected":""}>${esc(n)}</option>`).join("")}</select></div><p>${STORE_OK?"Remembered on this device.":""}</p></div></section>
<nav class="trades" aria-label="Leads by trade">${TRADES.map(tile).join("")}</nav>
<div class="ov"><div class="ov-col">
<section class="panel"><div class="sec-h"><h2>${t?esc(t[1])+": newest leads":"Newest leads"}<span class="c num">${int(t?tradeRows(TRADE).length:fl.length)}</span></h2><a href="${t?tradeHref(TRADE):"#/list"}">See all ${int(t?tradeRows(TRADE).length:fl.length)}</a></div>${newest.length?rowsHtml(newest,tl,0,true):`<p class="empty">None on this week's list.</p>`}</section>
${tl!=="opening"?`<section class="panel"><div class="sec-h"><h2>Opening soon<span class="c num">${int(op.length)}</span></h2><a href="#/list?l=opening">See all ${int(op.length)}</a></div>${rowsHtml(op,"opening",4,true)}</section>`:""}
</div><div class="ov-col">
<section class="panel"><div class="sec-h"><h2>Failed more than once<span class="c num">${int(rp.length)}</span></h2><a href="#/list?l=repeat">See all ${int(rp.length)}</a></div>
${rp.slice().sort((a,b)=>b.f90-a.f90||a.n.localeCompare(b.n)).slice(0,6).map(p=>`<a class="mini-b" href="#/place/${encodeURIComponent(p.id)}?from=repeat"><b>${esc(p.n)}</b><span>${esc(p.ar||"Chicago")}, last failed <span class="dt">${dayShort(INS[p.fa[0]].d)}</span></span><span class="r num">${int(p.f90)}<small>fails in 90 days</small></span></a>`).join("")}</section>
<section class="panel"><div class="sec-h"><h2>Where they are</h2><a href="#/list?view=map">Open the map</a></div>
<p class="blg" aria-hidden="true"><span><i class="b0" style="background:#C8502F"></i>Failed or conditional</span><span><i class="b1" style="background:#2F5F9E"></i>Opening soon</span></p>
<ul class="bars" aria-label="Places on the list by community area"><li class="hd" aria-hidden="true"><span></span><span class="sp2"></span><span>Failed</span><span>All</span></li>${areas.map(([a,n,v])=>`<li><a href="#/list?area=${encodeURIComponent(a)}" aria-label="${esc(a)}: ${plural(n,"place")}, ${int(v[0])} failed or conditional, ${int(v[1])} opening soon"><span>${esc(a)}</span><span class="tr" style="width:${Math.max(3,Math.round(n/amax*100))}%" aria-hidden="true">${v[0]?`<i style="flex-grow:${v[0]};background:#C8502F"></i>`:""}${v[1]?`<i style="flex-grow:${v[1]};background:#2F5F9E"></i>`:""}</span><span class="nv num${v[0]?"":" z"}" style="color:var(--fail)">${int(v[0])}</span><span class="v num">${int(n)}</span></a></li>`).join("")}</ul></section>
<section class="panel"><div class="sec-h"><h2>Your follow-ups</h2>${cN||nN?`<a href="#/list?fu=mine">Show them</a>`:""}</div>
<div class="mine">${cN||nN?`<p class="mh"><b>${plural(cN,"place")}</b> marked contacted, <b>${plural(nN,"note")}</b> written.</p>`:`<p class="mh"><b class="blk">No follow-ups yet</b>Mark a place as contacted or add a note on its page, and it shows up here.</p>`}<p>${esc(STORE_LINE())}</p></div></section>
</div></div>`;
$("#trade").onchange=e=>{setTrade(e.target.value);viewOverview();toast(e.target.value?"Your trade is saved on this device":"Showing all trades");};}

/* lists: filters, list and map, in sync */
const SORTS={newest:(l)=>(a,b)=>leadOf(b,l).d.localeCompare(leadOf(a,l).d)||a.n.localeCompare(b.n),az:()=>(a,b)=>a.n.localeCompare(b.n),
 fails:(l)=>(a,b)=>b.f90-a.f90||leadOf(b,l).d.localeCompare(leadOf(a,l).d),area:(l)=>(a,b)=>(a.ar||"~").localeCompare(b.ar||"~")||leadOf(b,l).d.localeCompare(leadOf(a,l).d)};
const DAYS=[["","Last 30 days"],["7","Last 7 days"],["14","Last 14 days"]];
function readF(q){const l=LISTS[q.get("l")]?q.get("l"):"flagged";return{l,q:(q.get("q")||"").trim(),cat:CATS.includes(q.get("cat"))?q.get("cat"):"",res:q.get("res")||"",area:q.get("area")||"",days:["7","14"].includes(q.get("days"))?q.get("days"):"",
type:q.get("type")||"",nw:q.get("new")==="1",fu:["todo","mine"].includes(q.get("fu"))?q.get("fu"):"",sort:SORTS[q.get("sort")]?q.get("sort"):"newest",view:q.get("view")==="map"?"map":"list"};}
function writeF(f){const q=new URLSearchParams();if(f.l!=="flagged")q.set("l",f.l);if(f.q)q.set("q",f.q);if(f.cat)q.set("cat",f.cat);if(f.res)q.set("res",f.res);if(f.area)q.set("area",f.area);if(f.days)q.set("days",f.days);if(f.type)q.set("type",f.type);if(f.nw)q.set("new","1");if(f.fu)q.set("fu",f.fu);if(f.sort!=="newest")q.set("sort",f.sort);if(f.view==="map")q.set("view","map");const s=q.toString();return "#/list"+(s?"?"+s:"");}
const norm=s=>String(s||"").toLowerCase().normalize("NFKD").replace(/[^a-z0-9 ]/g," ").replace(/\s+/g," ").trim();
function since(days){const t=new Date(D.through+"T12:00:00Z");t.setUTCDate(t.getUTCDate()-(+days-1));return t.toISOString().slice(0,10);}
function pass(p,f,skip){const x=leadOf(p,f.l);
if(skip!=="q"&&f.q){const t=norm(f.q);const hay=norm([p.n,p.k,p.a,p.ar,p.z,...p.lic].join(" "));if(!t.split(" ").every(w=>hay.includes(w)))return false;}
if(skip!=="cat"&&f.cat&&!(p.cb[f.l]||[]).includes(f.cat))return false;if(skip!=="res"&&f.res&&x.r!==f.res)return false;if(skip!=="area"&&f.area&&p.ar!==f.area)return false;
if(skip!=="days"&&f.days&&x.d<since(f.days))return false;if(skip!=="type"&&f.type&&p.ty!==f.type)return false;if(skip!=="new"&&f.nw&&!p.nb[f.l])return false;
if(f.fu==="todo"&&mk(p.id).c)return false;if(f.fu==="mine"&&!(mk(p.id).c||(mk(p.id).n||"").trim()))return false;return true;}
function activeCount(f){return [f.res,f.area,f.days,f.type,f.nw,f.fu].filter(Boolean).length;}
function viewList(q){const f=readF(q);STATE.f=f;STATE.shown=60;const L=LISTS[f.l];document.title=`${L.t} | Chicago Restaurant Inspection Leads`;
const base=inList(f.l);STATE.base=base;
STATE.areas=[...new Set(base.map(p=>p.ar).filter(Boolean))].sort();STATE.types=[...new Set(base.map(p=>p.ty).filter(Boolean))].sort();STATE.results=[...new Set(base.map(p=>leadOf(p,f.l).r))].sort();
$("#app").innerHTML=`<div class="ph"><div><h1>${esc(L.t)}</h1></div></div>
<nav class="lsw" aria-label="Lists">${Object.entries(LISTS).map(([k,v])=>`<a href="${writeF(Object.assign({},f,{l:k,cat:k==="opening"?"":f.cat,res:"",type:""}))}"${k===f.l?' aria-current="page"':""}>${esc(v.t)}<span class="c num">${int(D.lists[k].length)}</span></a>`).join("")}</nav>
<p class="ldesc">${esc(L.s)}</p>
<div class="tool"><label class="search"><span class="sr">Search this list</span>${ico("search")}<input id="fq" type="search" placeholder="Search name, address or license" value="${esc(f.q)}" autocomplete="off" enterkeyhint="search"><button type="button" class="clr" id="fqx" aria-label="Clear search"${f.q?"":" hidden"}>${ico("x","s")}</button></label>
<div class="seg" id="fcat" role="group" aria-label="Violation category"></div>
<button class="btn fbtn" id="fopen" type="button" aria-haspopup="dialog" aria-controls="fsheet">${ico("filter")}<span id="fopenT">Filters</span></button>
<span class="tsp"></span><button class="btn csvb" type="button" id="csv" aria-label="Export these places as a CSV file">${ico("csv","s")}<span class="t" aria-hidden="true">Export CSV</span><span class="m" aria-hidden="true">CSV</span></button>
<div class="seg vtog" role="group" aria-label="Show as"><button type="button" data-v="list">${ico("list","s")}List</button><button type="button" data-v="map">${ico("map","s")}Map</button></div></div>
<div class="filters" id="fsheet" aria-label="Filters">
<div class="sheet-h"><h2 id="fsheetH">Filters</h2><button class="btn sm" type="button" id="fclose" aria-label="Close filters">${ico("x","s")}</button></div>
<div class="fld"><label for="fres">City result</label><select id="fres"></select></div>
<div class="fld"><label for="fdays">Inspected</label><select id="fdays"></select></div>
<div class="fld"><label for="farea">Community area</label><select id="farea"></select></div>
<div class="fld"><label for="ftype">Facility type</label><select id="ftype"></select></div>
<div class="fld"><label for="fsort">Sort</label><select id="fsort"><option value="newest">Newest first</option><option value="az">Name, A to Z</option><option value="fails">Most fails in 90 days</option><option value="area">Community area</option></select></div>
<div class="fld"><label for="ffu">Follow-up</label><select id="ffu"><option value="">All places</option><option value="todo">Not contacted yet</option><option value="mine">Contacted or with a note</option></select></div>
<label class="tog"><input type="checkbox" id="fnew"><span id="fnewT">New this week</span></label>
<div class="sheet-f"><button class="btn" type="button" id="freset">Clear filters</button><button class="btn ink" type="button" id="fdone">Show places</button></div>
</div>
<div class="rbar" aria-live="polite"><span id="rcount"></span><button class="lnk" type="button" id="fclear" hidden>Clear filters</button></div>
<div class="split" id="split" data-v="${f.view}"><section class="panel lst" aria-label="Places on this list"><div id="plist"></div></section>
<div class="mapbox" id="mapbox"><div class="map" id="map" role="region" aria-label="Map of the places in the list. The list has the same places."></div>
<div class="legend" aria-hidden="true"><span><i class="lg-f"></i>Fail</span><span><i class="lg-c"></i>Pass w/ Conditions</span><span><i class="lg-p"></i>Pass</span><span><i class="lg-o"></i>Other</span></div>
<p class="map-note" id="mapnote" hidden></p></div></div>`;
const upd=patch=>{Object.assign(STATE.f,patch);STATE.shown=60;history.replaceState(history.state,"",writeF(STATE.f));STATE.trail[STATE.trail.length-1]=location.hash;refresh(true);};
let tq;$("#fq").addEventListener("input",e=>{$("#fqx").hidden=!e.target.value;clearTimeout(tq);tq=setTimeout(()=>upd({q:e.target.value.trim()}),140);});
$("#fqx").onclick=()=>{$("#fq").value="";$("#fqx").hidden=true;upd({q:""});$("#fq").focus();};
$("#fres").onchange=e=>upd({res:e.target.value});$("#fdays").onchange=e=>upd({days:e.target.value});$("#farea").onchange=e=>upd({area:e.target.value});$("#ftype").onchange=e=>upd({type:e.target.value});
$("#fsort").onchange=e=>upd({sort:e.target.value});$("#fnew").onchange=e=>upd({nw:e.target.checked});$("#ffu").onchange=e=>upd({fu:e.target.value});
const clear=()=>{$("#fq").value="";$("#fqx").hidden=true;upd({q:"",cat:"",res:"",area:"",days:"",type:"",nw:false,fu:""});};
$("#fclear").onclick=clear;$("#freset").onclick=clear;$("#fopen").onclick=openSheet;$("#fclose").onclick=closeSheet;$("#fdone").onclick=closeSheet;
document.querySelectorAll(".vtog button").forEach(b=>b.onclick=()=>{upd({view:b.dataset.v});$("#split").dataset.v=b.dataset.v;syncVtog();if(b.dataset.v==="map")showMap();});
$("#csv").onclick=exportCsv;STATE.upd=upd;
refresh(false);syncVtog();
const phone=window.matchMedia("(max-width:860px)").matches;if(!phone)ensureMap();else if(f.view==="map")setTimeout(showMap,60);
return f.l;}
function showMap(){const t=document.querySelector(".tool");if(t&&window.matchMedia("(max-width:860px)").matches){const y=t.getBoundingClientRect().top+window.scrollY-parseInt(getComputedStyle(document.documentElement).getPropertyValue("--bar-h"))-12;window.scrollTo(0,Math.max(0,y));}
setTimeout(()=>{ensureMap();if(STATE.map){STATE.map.invalidateSize();drawMap(true);}},40);}
function syncVtog(){document.querySelectorAll(".vtog button").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.v===STATE.f.view)));}
function refresh(refit){const f=STATE.f,base=STATE.base;
const facet=(skip,test)=>base.filter(p=>pass(p,f,skip)&&test(p)).length;
const catBtns=f.l==="opening"?[]:[["","All",()=>true]].concat(CATS.map(k=>[k,CAT[k].short,p=>(p.cb[f.l]||[]).includes(k)]));
$("#fcat").hidden=!catBtns.length;
$("#fcat").innerHTML=catBtns.map(([k,t,fn])=>`<button type="button" data-k="${k}" aria-pressed="${f.cat===k}">${k?ico(k,"s"):""}${esc(t)}<span class="c num">${int(facet("cat",fn))}</span></button>`).join("");
$("#fcat").querySelectorAll("button").forEach(b=>b.onclick=()=>STATE.upd({cat:b.dataset.k}));
const opt=(v,t,n,sel)=>`<option value="${esc(v)}"${sel?" selected":""}>${esc(t)}${n==null?"":` (${int(n)})`}</option>`;
$("#fres").innerHTML=opt("","Any result",null,!f.res)+STATE.results.map(r=>opt(r,r,facet("res",p=>leadOf(p,f.l).r===r),f.res===r)).join("");
$("#fdays").innerHTML=DAYS.map(([v,t])=>opt(v,t,v?facet("days",p=>leadOf(p,f.l).d>=since(v)):null,f.days===v)).join("");
$("#farea").innerHTML=opt("","All community areas",null,!f.area)+STATE.areas.map(a=>opt(a,a,facet("area",p=>p.ar===a),f.area===a)).join("");
$("#ftype").innerHTML=opt("","Any type",null,!f.type)+STATE.types.map(t=>opt(t,t,facet("type",p=>p.ty===t),f.type===t)).join("");
$("#fsort").value=f.sort;$("#fnew").checked=f.nw;$("#ffu").value=f.fu;$("#fnewT").textContent=`New this week (${int(facet("new",p=>p.nb[f.l]))})`;
const ac=activeCount(f);$("#fopenT").innerHTML=ac?`Filters <span class="fcount num">${ac}</span>`:"Filters";
const rows=base.filter(p=>pass(p,f)).sort(SORTS[f.sort](f.l));STATE.rows=rows;
$("#rcount").innerHTML=rows.length===base.length?`<b class="num">${int(rows.length)}</b> ${rows.length===1?"place":"places"}`:`<b class="num">${int(rows.length)}</b> of <span class="num">${int(base.length)}</span> places`;
$("#fclear").hidden=!(f.q||f.cat||ac);$("#fdone").textContent=rows.length?`Show ${plural(rows.length,"place")}`:"No places match";$("#csv").disabled=!rows.length;
drawList();drawMap(refit);}
function drawList(){const rows=STATE.rows,n=Math.min(STATE.shown,rows.length);const el=$("#plist");
if(!rows.length){const q=STATE.f.q;el.innerHTML=`<div class="empty"><h3>${q?`No places match "${esc(q)}"`:"No places match these filters"}</h3><p>${q?"Check the spelling, or clear the search":"Try another area or result, or clear the filters"} to see all ${int(STATE.base.length)}.</p><button class="btn ink" type="button" id="eclr">${q?"Clear search and filters":"Clear filters"}</button></div>`;$("#eclr").onclick=()=>$("#fclear").click();return;}
el.innerHTML=rowsHtml(rows,STATE.f.l,n)+(n<rows.length?`<div class="row-more"><button class="btn" type="button" id="more">Show ${int(Math.min(60,rows.length-n))} more</button><span>${int(n)} of ${int(rows.length)} shown</span></div>`:"");
const m=$("#more");if(m)m.onclick=()=>{STATE.shown+=60;drawList();};
el.querySelectorAll(".row").forEach(a=>{a.addEventListener("mouseenter",()=>hot(a.dataset.id,true));a.addEventListener("mouseleave",()=>hot(a.dataset.id,false));});}

/* map */
const MS={fail:{radius:7,color:"#A63E21",weight:2,fillColor:"#C8502F",fillOpacity:1},pwc:{radius:6.5,color:"#7A5A12",weight:2,fillColor:"#E0B54A",fillOpacity:1},
pass:{radius:6,color:"#2E6B66",weight:2.2,fillColor:"#fff",fillOpacity:1},nr:{radius:6,color:"#fff",weight:1.5,fillColor:"#2F5F9E",fillOpacity:.95},oth:{radius:6,color:"#fff",weight:1.5,fillColor:"#2F5F9E",fillOpacity:.95}};
function tiles(m){L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(m);}
function ensureMap(){if(STATE.map||!$("#map"))return;if(!window.L){const box=$("#mapbox");if(box&&!box.querySelector(".map-fail"))box.insertAdjacentHTML("beforeend",'<div class="map-fail"><p>The map did not load on this connection. The list has every place.</p></div>');if(!ensureMap.tries){ensureMap.tries=1;window.addEventListener("load",()=>{if($("#map")&&!STATE.map){const f=$("#mapbox .map-fail");f&&f.remove();ensureMap();}},{once:true});}return;}
const m=L.map("map",{zoomControl:true,scrollWheelZoom:true}).setView([41.85,-87.68],11);
m.attributionControl.setPrefix('<a href="https://leafletjs.com">Leaflet</a>');tiles(m);STATE.map=m;STATE.layer=L.layerGroup().addTo(m);STATE.mk={};drawMap(true);}
function popup(p){const x=leadOf(p,STATE.f.l);return `<div class="pop"><span class="mn" style="font-size:16px">${esc(p.n)}</span><span class="ad">${esc(p.a)}</span><span class="bd">${dayShort(x.d)}, ${esc(x.t)}</span>${res(x.r)}<p style="margin:10px 0 0"><a class="btn ink" href="#/place/${encodeURIComponent(p.id)}?from=${STATE.f.l}">Open place</a></p></div>`;}
function drawMap(refit){const m=STATE.map;const rows=STATE.rows||[];const geo=rows.filter(p=>p.lat&&p.lon);const note=$("#mapnote");
if(note){const miss=rows.length-geo.length;note.hidden=!(miss||!rows.length);note.textContent=!rows.length?"No pins for these filters.":miss?`${plural(miss,"place")} in the list ${miss===1?"has":"have"} no map location in the City record.`:"";}
if(!m)return;STATE.layer.clearLayers();STATE.mk={};
const rank={pass:0,oth:1,nr:1,pwc:2,fail:3};
geo.slice().sort((a,b)=>rank[RES(leadOf(a,STATE.f.l).r)]-rank[RES(leadOf(b,STATE.f.l).r)]).forEach(p=>{const k=RES(leadOf(p,STATE.f.l).r);const c=pin([p.lat,p.lon],k,1).bindPopup(popup(p),{maxWidth:280});c.addTo(STATE.layer);STATE.mk[p.id]=[c,k];});
if(refit&&geo.length){const bb=L.latLngBounds(geo.map(p=>[p.lat,p.lon]));if(geo.length===1)m.setView(bb.getCenter(),15,{animate:false});else m.fitBounds(bb,{padding:[40,40],maxZoom:15,animate:false});}}
/* fail pins are the legend's square (a div icon); the others stay circles */
function pin(ll,k,scale){if(k==="fail"){const z=Math.round(13*scale);return L.marker(ll,{icon:L.divIcon({className:"pin-f",iconSize:[z,z]}),keyboard:false,riseOnHover:true});}
return L.circleMarker(ll,Object.assign({},MS[k],{radius:MS[k].radius*scale}));}
function hot(id,on){const e=STATE.mk&&STATE.mk[id];if(!e)return;const [c,k]=e;
if(c.setStyle){c.setStyle(on?Object.assign({},MS[k],{radius:MS[k].radius+4,weight:3,color:"#1D2433"}):MS[k]);if(on)c.bringToFront();}
else{const el=c.getElement&&c.getElement();if(el)el.classList.toggle("hot",on);c.setZIndexOffset(on?1000:0);}}

/* filters sheet (phone) */
let lastFocus=null;
function openSheet(){const s=$("#fsheet");if(!s)return;lastFocus=document.activeElement;s.classList.add("open");s.setAttribute("role","dialog");s.setAttribute("aria-modal","true");s.setAttribute("aria-labelledby","fsheetH");
const sc=document.createElement("div");sc.className="scrim";sc.id="scrim";sc.onclick=closeSheet;document.body.appendChild(sc);setTimeout(()=>{const h=$("#fsheetH");h.setAttribute("tabindex","-1");h.focus();},60);document.addEventListener("keydown",sheetKeys);}
function closeSheet(){const s=$("#fsheet");const sc=$("#scrim");if(sc)sc.remove();document.removeEventListener("keydown",sheetKeys);if(!s||!s.classList.contains("open"))return;s.classList.remove("open");s.removeAttribute("role");s.removeAttribute("aria-modal");if(lastFocus&&lastFocus.focus)lastFocus.focus();}
function sheetKeys(e){if(e.key==="Escape"){closeSheet();return;}if(e.key!=="Tab")return;const f=[...$("#fsheet").querySelectorAll("select,input,button")].filter(x=>x.offsetParent!==null);if(!f.length)return;const a=f[0],z=f[f.length-1];
if(e.shiftKey&&document.activeElement===a){e.preventDefault();z.focus();}else if(!e.shiftKey&&document.activeElement===z){e.preventDefault();a.focus();}}

/* CSV of the current view */
function cell(v){v=v==null?"":String(v);if(/^[=+\-@\t\r]/.test(v)&&!/^-?\d+(\.\d+)?$/.test(v))v="'"+v;return /[",\r\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v;}
function exportCsv(){const rows=STATE.rows||[];if(!rows.length)return;const l=STATE.f.l;
const head=["Business","Also known as","Address","ZIP","Community area","Facility type","List","City result","Inspected","Inspection type"].concat(CATS.map(k=>CAT[k].short+" (violation codes)")).concat(["All violations cited","Also cited in the list window","Fails in 90 days","Newest City result","Newest result date","New this week","License","City record","Contacted","Contacted on","Your note","Latitude","Longitude"]);
const lines=[head.map(cell).join(",")];
rows.forEach(p=>{const x=leadOf(p,l);const lt=INS[p.lt];const m=mk(p.id);const cc=x.c||{};
lines.push([p.n,p.k,p.a,p.z,p.ar,p.ty,LISTS[l].t,x.r,x.d,x.t].concat(CATS.map(k=>cc[k]?cc[k].join(" "):"")).concat([x.v.join(" "),(p.al[l]||[]).map(a=>CAT[a.cat].short+" "+a.codes.join(" ")+" on "+a.d).join("; "),p.f90,lt.r,lt.d,p.nb[l]?"Yes":"",p.lic.join("; "),D.record+p.lead[l],m.c?"Yes":"",m.c||"",(m.n||"").trim(),p.lat||"",p.lon||""]).map(cell).join(","));});
const blob=new Blob(["﻿"+lines.join("\r\n")+"\r\n"],{type:"text/csv;charset=utf-8"});
const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=`chicago-restaurant-leads-${D.asOfIso}-${l}-${rows.length}.csv`;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),4000);
toast(`CSV exported: ${plural(rows.length,"place")}`);}
function downloadWorkbook(){const blob=new Blob([b64(D.xlsx)],{type:"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"});
const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=D.fileName;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),4000);toast("Workbook downloaded");}

/* place page */
/* the category's own violation code; anything else came from the inspector's note */
const CAT_BASE={pests:[38],drain:[52],clean:[49],hood:[]};
const CAT_NOTE={pests:"names pests",hood:"names a hood, filter, exhaust or grease",drain:"names a grease trap or a drain problem",clean:"asks for cleaning"};
const fromNote=(k,codes)=>codes.some(c=>!CAT_BASE[k].includes(c));
const nwDates=t=>t.replace(/([A-Z][a-z]{2} \d{1,2}, \d{4})/g,'<span class="nd">$1</span>');
const fv=(v,c)=>v?`<dd${c?` class="${c}"`:""}>${esc(v)}</dd>`:'<dd class="nv">Not on the City record</dd>';
function viewPlace(p,from){document.title=`${p.n} | Chicago Restaurant Inspection Leads`;const m=mk(p.id);
const l=p.ls.includes(from)?from:p.ls[0];const x=leadOf(p,l);
const why=Object.entries(x.c);const tr=TRADES.find(t=>t[0]===TRADE);
const listChips=p.ls.map(k=>`<span class="badge" style="background:var(--paper2);color:var(--ink)">${esc(LISTS[k].t)}</span>`).join("");
const maps="https://www.google.com/maps/search/?api=1&query="+encodeURIComponent(p.n+", "+p.a+", Chicago, IL");
const find="https://www.google.com/search?q="+encodeURIComponent(p.n+" "+p.a+" Chicago phone");
const hist=p.h.map(id=>{const y=INS[id];const isLead=id===p.lead[l];const cs=Object.keys(y.c);
return `<li class="${isLead?"on":""}"><span class="dot ${RES(y.r)}" aria-hidden="true"></span><div class="${isLead?"lead":""}"><div class="hd"><b>${day(y.d)}</b>${res(y.r)}<span class="t">${esc(y.t)}</span><span class="flagt">${ico("flag","s")}Why it is on this list</span></div>
${cs.length?`<div class="cs">${cs.map(k=>cat(k,true)).join("")}</div>`:""}
${y.v.length?`<details><summary>${plural(y.v.length,"violation")} cited</summary><ul class="vl">${y.v.map(c=>{const hit=cs.some(k=>y.c[k].includes(c));return `<li${hit?' class="k"':""}><b>${c}</b><span>${esc(sent(D.titles[c]||""))}${hit?`<span class="sr"> (in a category)</span>`:""}</span></li>`;}).join("")}</ul></details>`:`<p class="rl" style="color:var(--muted)">No violations listed in the City record.</p>`}
<p class="rl"><a href="${esc(D.record+id)}" target="_blank" rel="noopener">City record ${esc(id)}<span class="sr"> (opens in a new tab)</span></a></p></div></li>`;}).join("");
$("#app").innerHTML=`<a class="back" href="#/list" id="back">${ico("back")}Back</a>
<div class="pg"><section class="pg-head"><div class="ph-chips">${listChips}${p.nw?'<span class="badge new">New this week</span>':""}${m.c?`<span class="badge done">${ico("check","s")}Contacted ${esc(day(m.c))}</span>`:""}</div>
<div class="p-title"><h1>${esc(p.n)}</h1><p class="sub">${esc(p.a)}, ${esc([p.ar,"Chicago"].filter(Boolean).join(", "))}${p.k?`<br>Also listed as ${esc(p.k)}`:""}</p></div>
<div class="acts"><button class="btn" type="button" id="cpy">${ico("copy","s")}Copy address</button><a class="btn" href="${maps}" target="_blank" rel="noopener">${ico("pin","s")}Map and phone<span class="sr"> (opens Google Maps in a new tab)</span></a><a class="btn" href="${find}" target="_blank" rel="noopener">${ico("search","s")}Search the web<span class="sr"> (opens in a new tab)</span></a></div></section>
<div class="pg-main">
<section class="panel why" aria-labelledby="wh"><h2 id="wh">Why it is on the ${esc(LISTS[l].t.toLowerCase())} list</h2>
<div class="top">${res(x.r,true,l==="opening"?"License: ":"")}<span class="dt">${day(x.d)}</span><span class="ty">${esc(/inspection$/i.test(x.t)?x.t:x.t+" inspection")}</span></div>
${l==="opening"?`<p style="margin:0 0 ${why.length?"14px":"0"};color:var(--ink2)">Chicago inspects a food business before it issues a food license. ${/^PASS/i.test(x.r)?"This place passed its license inspection, so it may open soon.":"This place has not passed its license inspection yet."}${p.op.length>1?` ${plural(p.op.length,"license inspection")} in the last 30 days.`:""}</p>`:""}
${l==="repeat"?`<p style="margin:0 0 14px;color:var(--ink2)">${plural(p.f90,"failed inspection")} in the 90 days to ${esc(D.throughText)}: ${p.fa.map(i=>dayShort(INS[i].d)).join(", ")}.</p>`:""}
${why.length?`<ul class="cv">${why.map(([k,codes])=>`<li>${cat(k,true)}<div><p><b>City violation ${codes.map(c=>c+" ("+esc(sent(D.titles[c]||""))+")").join(", ")}</b></p>${fromNote(k,codes)?`<p>From the inspector's note, which ${esc(CAT_NOTE[k])}.</p>`:""}</div></li>`).join("")}</ul>`:""}
${(p.al[l]||[]).length?`<p class="ms"><b>Also cited in the last ${l==="repeat"?"90":"30"} days:</b> ${p.al[l].map(a=>`${esc(CAT[a.cat].short)}, violation ${a.codes.join(", ")} on ${day(a.d)}`).join("; ")}.</p>`:""}
${p.since[l]?`<p class="ms"><b>Newer City result:</b> ${esc(p.since[l].r)} on ${day(p.since[l].d)} (${esc(p.since[l].t)}).</p>`:""}
</section>
<section class="panel"><div class="sec-h"><h2>Inspection history<span class="c num">${int(p.h.length)}</span></h2></div><p class="rec" style="padding-top:0">Every City inspection on file for this place in the last 24 months, newest first. Results and violation numbers are the City's; categories are ours.</p><ol class="tl">${hist}</ol></section>
</div>
<aside class="pg-side" aria-label="Your follow-up">
<section class="panel note" aria-labelledby="nh"><h2 id="nh">Your follow-up</h2><p class="hint">${esc(STORE_LINE())}</p>
<button class="btn${m.c?" on":""}" type="button" id="mark" aria-pressed="${!!m.c}">${ico("check","s")}<span id="markT">${m.c?"Contacted "+esc(day(m.c))+" (undo)":"Mark as contacted"}</span></button>
<label for="nt" class="sr">Private note</label><textarea id="nt" placeholder="Who you spoke to, what they need, when to call back" maxlength="2000">${esc(m.n||"")}</textarea><p class="st" id="ntst" aria-live="polite"></p></section>
<section class="panel bc"><h2 style="font-size:17px">What to say</h2><p class="meta" style="margin:6px 0 14px">A call opener and an email ${tr?"for "+esc(tr[1].toLowerCase()):"for each trade"}, with this place's details to fill in.</p><a class="btn" href="#/pitch${tr?"?b="+tr[0]:""}">${ico("kit","s")}Open the pitch kit</a></section>
</aside>
<section class="panel pg-facts"><div class="sec-h"><h2>Facts from the City record</h2></div><dl class="facts">
<div><dt>Facility type</dt>${fv(p.ty==="Not given"?"":p.ty)}</div><div><dt>Community area</dt>${fv(p.ar)}</div><div><dt>ZIP</dt>${fv(p.z,"num")}</div><div><dt>City risk level</dt>${fv(p.rk)}</div>
<div><dt>License${p.lic.length>1?"s":""}</dt>${fv(p.lic.join(", "),"lic")}</div><div><dt>Newest result</dt><dd>${esc(INS[p.lt].r)}, ${dayShort(INS[p.lt].d)}</dd></div><div><dt>Fails in 90 days</dt><dd class="num">${int(p.f90)} <span class="dn">excl. license inspections</span></dd></div><div><dt>Inspections on file</dt><dd class="num">${int(p.h.length)}</dd></div></dl>
${p.lat&&p.lon?'<div class="minimap" id="minimap" role="region" aria-label="Map of the place"></div>':""}</section></div>`;
$("#back").onclick=e=>{e.preventDefault();back("#/list"+(l!=="flagged"?"?l="+l:""));};
$("#cpy").onclick=async()=>{toast(await copyText(p.n+", "+p.a+", Chicago, IL")?"Address copied":"Copy did not work. Press and hold the address.");};
$("#mark").onclick=()=>{const now=mk(p.id).c?"":new Date().toISOString().slice(0,10);const ok=setMark(p.id,{c:now});const b=$("#mark");b.classList.toggle("on",!!now);b.setAttribute("aria-pressed",String(!!now));$("#markT").textContent=now?"Contacted "+day(now)+" (undo)":"Mark as contacted";toast(ok?(now?"Marked as contacted":"Contacted mark removed"):"Not saved: this browser blocks saving");};
const grow=t=>{t.style.height="auto";t.style.height=Math.max(96,t.scrollHeight+2)+"px";};grow($("#nt"));
let tn;$("#nt").addEventListener("input",e=>{grow(e.target);clearTimeout(tn);$("#ntst").textContent="Saving...";tn=setTimeout(()=>{const ok=setMark(p.id,{n:e.target.value});$("#ntst").textContent=ok?"Note saved in this browser":"Not saved. This browser blocks saving here; private browsing is the usual cause.";},400);});
const lead=$(".tl li.on details");if(lead)lead.open=true;
if(p.lat&&p.lon){const mm=()=>{if(!window.L||!$("#minimap"))return;const m2=L.map("minimap",{scrollWheelZoom:false,dragging:!L.Browser.mobile,tap:false}).setView([p.lat,p.lon],15);m2.attributionControl.setPrefix('<a href="https://leafletjs.com">Leaflet</a>');tiles(m2);pin([p.lat,p.lon],RES(x.r),1.6).addTo(m2);STATE.mini=m2;};if(window.L)mm();else window.addEventListener("load",mm,{once:true});}}

/* pitch kit */
function viewPitch(q){const ks=PITCH.kits;const b=ks.find(k=>k.key===q.get("b"))||ks.find(k=>k.key===TRADE)||ks[0];
document.title="Pitch kit | Chicago Restaurant Inspection Leads";
const fill=s=>esc(s).replace(/\[([^\]]+)\]/g,'<span class="f">[$1]</span>');
$("#app").innerHTML=`<div class="ph"><div><h1>Pitch kit</h1><p>A short call opener and an email for each trade. Fill in the parts in blue brackets from the place's page, and keep every claim true.</p></div></div>
<nav class="bk" aria-label="Trades">${ks.map(k=>`<a href="#/pitch?b=${k.key}"${k===b?' aria-current="page"':""}>${ico(k.key==="opening"?"opening":k.key,"s")}${esc(TRADES.find(t=>t[0]===k.key)[1])}</a>`).join("")}</nav>
<div class="pk"><section class="panel"><div class="pk-h"><h2>Call opener</h2><button class="btn sm" type="button" data-copy="c">${ico("copy","s")}Copy</button></div><p class="sub">${esc(b.buyer)}. About 20 seconds.</p><p class="call">${fill(b.call)}</p>
<ol class="rules">${PITCH.rules.map(r=>`<li>${esc(r)}</li>`).join("")}</ol></section>
<section class="panel mail"><div class="pk-h"><h2>Email</h2><button class="btn sm" type="button" data-copy="m">${ico("copy","s")}Copy</button></div><p class="sub">Send it the same day as the call.</p>${b.email.map(x=>`<p>${fill(x)}</p>`).join("")}</section></div>
<p class="rec" style="padding:16px 0 0">Leads for this trade: <a href="${b.list==="opening"?"#/list?l=opening":"#/list?cat="+b.cat}">open the ${esc(b.list==="opening"?"opening soon":CAT[b.cat].label.toLowerCase())} list</a>.</p>`;
document.querySelectorAll("[data-copy]").forEach(x=>x.onclick=async()=>{toast(await copyText(x.dataset.copy==="c"?b.call:b.email.join("\n\n"))?"Copied":"Copy did not work. Select the text.");});
const on=document.querySelector('.bk a[aria-current="page"]');if(on&&on.scrollIntoView)on.scrollIntoView({block:"nearest",inline:"center"});}

/* terms */
function termsHtml(){const para=t=>{const m=/^([A-Z][A-Za-z ]{1,40}?\.) (.+)$/.exec(t);return m?`<p><b>${esc(m[1])}</b> ${esc(m[2])}</p>`:`<p>${esc(t)}</p>`;};
return `<div class="ph"><div><h1>Terms of Use</h1><p>${nwDates(esc(TERMS.version))}.<br>The same terms are on the Terms tab of the Excel file.</p></div></div>
<div class="terms"><section class="panel" aria-labelledby="th1"><div class="sec-h"><h2 id="th1">City of Chicago data</h2></div><div class="tx"><p>${esc(TERMS.city)}</p><p><a href="${esc(TERMS.cityTerms)}" target="_blank" rel="noopener">City of Chicago Data Terms of Use<span class="sr"> (opens in a new tab)</span></a></p></div></section>
<section class="panel" aria-labelledby="th2"><div class="sec-h"><h2 id="th2">ProofNotFluff</h2></div><div class="tx"><p>${esc(TERMS.notice)}</p>${TERMS.paras.map(para).join("")}</div></section></div>`;}
function viewTerms(){document.title="Terms of Use | Chicago Restaurant Inspection Leads";$("#app").innerHTML=`<a class="back" href="#/" id="back">${ico("back")}Back</a>`+termsHtml();$("#back").onclick=e=>{e.preventDefault();back("#/");};}
function gateHash(){if(D)return;const t=(location.hash||"")==="#/terms";$("#gateView").hidden=t;$("#gateLegal").hidden=t;$("#app").hidden=!t;$("#appLegal").hidden=!t;
if(t){document.title="Terms of Use | Chicago Restaurant Inspection Leads";$("#app").innerHTML=`<a class="back" href="#/">${ico("back")}Back to the password</a>`+termsHtml();window.scrollTo(0,0);const h=$("#app h1");h.setAttribute("tabindex","-1");h.focus({preventScroll:true});}
else{$("#app").innerHTML="";document.title="Members: Chicago Restaurant Inspection Leads | ProofNotFluff";}}
window.addEventListener("hashchange",gateHash);gateHash();

$("#skip").onclick=e=>{e.preventDefault();const t=$("#app").hidden?$("#pw"):($("#app h1")||$("#app"));if(t){t.setAttribute("tabindex",t.id==="pw"?"0":"-1");t.focus();}};
const pw=$("#pw"),eye=$("#eye");
eye.onclick=()=>{const show=pw.type==="password";pw.type=show?"text":"password";eye.setAttribute("aria-pressed",String(show));eye.setAttribute("aria-label",show?"Hide password":"Show password");$("#eyeslash").hidden=!show;pw.focus();};
$("#gate").onsubmit=async e=>{e.preventDefault();const err=$("#err"),btn=$("#go");
if(!pw.value.trim()){err.textContent="Type the password from your Gumroad purchase page.";pw.focus();return;}
btn.disabled=true;btn.textContent="Opening the list...";err.textContent="";
try{const d=await openBox(pw.value.trim());pw.value="";prep(d);
$("#gateView").hidden=true;$("#gateLegal").hidden=true;$("#app").hidden=false;$("#appLegal").hidden=false;$("#tabs").hidden=false;$("#bnav").hidden=false;$("#dlTop").hidden=false;document.body.classList.add("in");
$("#dlTop").onclick=downloadWorkbook;window.removeEventListener("hashchange",gateHash);window.addEventListener("hashchange",onHash);STATE.trail=[location.hash||"#/"];route(true);}
catch(x){btn.disabled=false;btn.textContent="Open this week's list";err.textContent="That password did not open the list. Check your Gumroad purchase page, or reply to your receipt for help.";pw.select();}};
</script></body></html>
"""


def selftest():
    import tempfile, shutil, subprocess
    import voice_lint
    import rest_leads, rest_xlsx
    data = rest_leads.build(rest_xlsx._planted())
    out = os.path.join(tempfile.mkdtemp(), "t.xlsx")
    rest_xlsx.build(data, out)
    html = build_html(data, open(out, "rb").read(), "correct horse battery")
    clear = re.sub(r"const BOX=\{.*?\};", "", html)          # base64 ciphertext can spell anything by chance
    assert "Acme" not in clear and "MAIN ST" not in clear.upper().replace("MAIN CONTENT", ""), "place data must stay inside the ciphertext"
    assert 'name="robots" content="noindex' in html and "List of Oct 17, 2026" in html
    text_only = re.sub(r"<[^>]+>", "", html).replace("&#x27;", "'")
    assert text_only.count(LEGAL.replace("__ASOF__", "Oct 17, 2026")) == 2, "the legal line word for word on the gate and the footer"
    assert CITY_DISCLAIMER in LEGAL and html.count('<a href="#/terms">Terms of Use</a>') == 2
    terms = json.loads(re.search(r"const TERMS=(\{.*?\});\n", html).group(1))
    assert [terms["version"]] + terms["paras"] == terms_text("Oct 17, 2026") and terms["city"] == CITY_DISCLAIMER and terms["notice"] == OUR_NOTICE
    pitch = json.loads(re.search(r"const PITCH=(\{.*?\});\n", html).group(1))
    assert [k["key"] for k in pitch["kits"]] == ["pests", "hood", "drain", "clean", "opening"] and pitch["rules"] == PITCH_RULES
    assert base_css()[:200] in html and ".trades{" in html, "the construction app's stylesheet plus ours"
    for u, h in (leads_app.LEAFLET_JS, leads_app.LEAFLET_CSS):
        assert u in html and h in html
    assert "openstreetmap.org/copyright" in html
    box = json.loads(re.search(r"const BOX=(\{.*?\});", html).group(1))
    assert box["rounds"] == 250_000 and box["kdf"] == "PBKDF2-SHA256"
    d = json.loads(decrypt("correct horse battery", box))
    by = {p["n"]: p for p in d["places"]}
    assert set(by) == {"Acme Tacos", "New Place", "Fry House", "Second Shop"}, set(by)
    assert by["Acme Tacos"]["ls"] == ["flagged", "repeat"] and by["Acme Tacos"]["f90"] == 2 and by["Acme Tacos"]["cb"]["flagged"] == ["pests"]
    assert d["insp"][by["Fry House"]["lt"]]["r"] == "Pass", "the newer pass is in the payload, so the place page can say so"
    assert by["Acme Tacos"]["lc"]["flagged"] == ["pests"] and by["Acme Tacos"]["nb"]["flagged"] is True and "al" in by["Acme Tacos"]
    assert d["titles"]["38"] == "INSECTS, RODENTS, & ANIMALS NOT PRESENT" and "COMMENTS" not in json.dumps(d).upper()
    assert d["lists"]["opening"] and d["xlsx"] and d["fileName"].endswith(".xlsx")
    try:
        decrypt("wrong password", box)
        raise AssertionError("wrong password decrypted")
    except AssertionError:
        raise
    except Exception:
        pass
    node = shutil.which("node")
    if node:   # browser helpers: dates, the CSV formula guard, the result classes
        fns = "\n".join(re.search(p, PAGE, re.M).group(0) for p in (r"^const MON=.*$", r"^function day\(s\).*$", r"^function dayShort\(s\).*$",
                                                                     r"^function cell\(v\).*$", r"^const RES=.*$"))
        js = fns + "\nconsole.log(JSON.stringify([day('2026-10-05'),dayShort('2026-10-15'),day(''),[-87.6,'=SUM(A1)','-1 call','@x','a,b'].map(cell),['Fail','Pass w/ Conditions','Pass','Not Ready','No Entry'].map(RES)]))"
        got = json.loads(subprocess.run([node, "-e", js], capture_output=True, text=True, check=True).stdout)
        assert got == ["Oct 5, 2026", "Oct 15", "", ["-87.6", "'=SUM(A1)", "'-1 call", "'@x", '"a,b"'], ["fail", "pwc", "pass", "nr", "oth"]], got
    else:
        print("node not found: browser helpers not checked here")
    text = PAGE + LEGAL + json.dumps(PITCH)
    assert "—" not in text, "em dash"
    for w in ("honestly", "genuinely", "straightforward", "delve", "unlock ", "elevate", "seamless", "game-changer", "effortless", "supercharge"):
        assert w not in text.lower(), w
    judged = re.sub(r"don't say a place is dirty, unsafe or closed|clean or unsafe", "", text.lower())   # the rules that forbid these words
    for w in ("dirty", "unsafe", "filthy", "disgusting", "infested", "shut down", "health hazard", "violator", "offender"):
        assert w not in judged, w
    tells = voice_lint.tells(re.sub(r"<[^>]+>|\$\{[^}]*\}", " ", PAGE + LEGAL))
    assert not tells, tells
    print("rest_app selftest ok")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--selftest"]:
        selftest()
    else:
        pw = os.environ.get("REST_LEADS_PASSWORD", "")
        if "--pw-file" in args:
            i = args.index("--pw-file")
            pw = open(args[i + 1]).read().strip()
            args = args[:i] + args[i + 2:]
        if len(pw) < 12:
            raise SystemExit("REST_LEADS_PASSWORD missing or shorter than 12 characters; nothing written")
        print(build(json.load(open(args[0])), args[1], args[2], pw))
