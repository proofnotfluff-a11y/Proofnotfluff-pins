#!/usr/bin/env python3
"""Build the free calculator site (GitHub Pages, served from docs/) from site/pages.json.

Usage: python3 tools/make_site.py            writes docs/<slug>/index.html, docs/index.html,
                                             docs/sitemap.xml, docs/robots.txt and the IndexNow key file docs/<key>.txt
Each page is one search phrase with a working calculator whose maths is the paid workbook's
(docs/assets/pnf-calc.js, tested by `node docs/assets/pnf-calc.test.js`), a worked example
with the workbook's own numbers, a short method, an FAQ (FAQPage structured data) and one
link to the matching Etsy listing. Shop links use the Share & Save address proofnotfluff.etsy.com.
A page whose spec carries "draft": true is written with a noindex tag and left off the index page
and the sitemap until the Legal desk clears it and removes the flag (agents/legal-desk.md, SITE PAGES).
A permit leads page (kind "leads", data from permits/chicago/ via .github/workflows/permits-chicago.yml) also stays
noindex and off the index, hub and sitemap until its spec has "kitForm" (the Kit waitlist form number).
Hand-made pages named in site/extras.json (not written here) join the sitemap and the index, with a link card on the
pages in their "from" list, once their committed page has no robots meta (live_extras).
"""
import html, json, os, sys

if __name__ in sys.modules:
    sys.modules.setdefault("make_site", sys.modules[__name__])   # rest_site, lic_site and question_site share this module's state (nav, live questions)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
BASE = "https://proofnotfluff.com/"
SHOP = "https://proofnotfluff.etsy.com"
# IndexNow key (Todd's go, Oct 23, 2026): main() writes docs/<key>.txt holding the key, the proof of ownership Bing and
# the other IndexNow engines read; tools/indexnow_submit.py imports it from here, so the two can never drift.
INDEXNOW_KEY = "cdccc9befa99e9cfa2a85549b2b1160d"
E = html.escape

# Store build (Todd, Oct 22, 2026; seo/STORE.md): the heading font is served from this site with a preload (it was a
# render-blocking Google Fonts stylesheet, about 1.5 s of LCP on every page), the header leads to the shop, the footer
# carries the refund page on every page, and each page gets its own Open Graph image (docs/assets/og/<slug>.png).
HEAD_TPL = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}">
<link rel="canonical" href="{url}">{robots}{analytics}<meta name="color-scheme" content="light dark">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<meta property="og:type" content="{ogtype}"><meta property="og:url" content="{url}">{og}
<link rel="icon" href="{rel}assets/favicon.svg" type="image/svg+xml"><link rel="icon" href="{rel}assets/favicon-48.png" sizes="48x48" type="image/png">
<link rel="apple-touch-icon" href="{rel}assets/apple-touch-icon.png"><meta name="theme-color" content="#f3f1ec" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#12161f" media="(prefers-color-scheme: dark)">
<link rel="preload" href="{rel}assets/fonts/poppins-700.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{rel}assets/pnf.css"><script src="{rel}assets/pnf-ui.js" defer></script>
{ld}
</head><body{bodycls}>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap"><a class="brandlink" href="{rel}"><span class="brand">ProofNotFluff</span><span class="bars" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></span></a>
{nav}</div></header>
<main class="wrap" id="main">"""

FOOT_TPL = """</main>
<footer><div class="wrap">
{fnav}
<p>Estimates for planning only, based on the numbers you enter. Not tax, legal or financial advice. {sources}</p>
<p>Made by ProofNotFluff with AI assistance, reviewed and tested by the shop owner. Calculators run in your browser; nothing you type in them is sent anywhere.</p>
{notices}</div></footer>
<script src="{rel}assets/pnf-calc.js"></script>
{script}
</body></html>"""

CALC_GROUPS = []      # [(group title, [calculator pages])], set by home_html, used by calculators_html
LIVE_QUESTIONS = []   # live question pages, set by main() before any page is written (the Questions link shows only when one is live)
PAGES_LIVE = []       # every live page, set by main() (related calculators read it)
PAGES_ALL = []        # every page in site/pages.json, live or draft, set by main() (a live page never links to a draft)
CURRENT = {}          # the page being written: {"nav": "shop" | "calc" | "questions" | ""} for aria-current
EXTRA_URLS = {}       # sub-pages a data page writes under its own folder (extra_pages), {url: lastmod}, for the sitemap


# Free Chicago data pages built in parallel (Todd, Oct 27, 2026: "Let's do them all"; coo/PARALLEL_BUILDS.md). A page of
# kind "datapage" names its own module in tools/ (dp_*.py), which owns everything about it: page_html(p), META
# {h1, card, keywords}, and optionally lastmod(p) and extra_pages(p) -> [(relative path, html)]. This file never needs
# editing to add one: the page entry in site/pages.json and the module are enough.
def datapage_ready(p):
    return bool(p.get("module")) and os.path.isfile(os.path.join(ROOT, "tools", p["module"] + ".py"))


def kind_module(p):
    """The module that renders a page outside this file, for the kinds that can add sub-pages or a lastmod."""
    import importlib
    name = p.get("module") if p.get("kind") == "datapage" else {"rodents": "rodents_site", "tradesnews": "news_site"}.get(p.get("kind"))
    return importlib.import_module(name) if name and (p.get("kind") != "datapage" or datapage_ready(p)) else None


def live_datapages():
    return [p for p in PAGES_LIVE if p.get("kind") == "datapage"]


def nav_html(rel, current=""):
    items = [("shop", f"{rel}shop/", "Shop"), ("calc", f"{rel}calculators/", "Free calculators")]
    # the free trades news brief in every header once it is live (Todd, Oct 27, 2026: "Shouldn't new features like news be
    # an option to select rather than hiding at the bottom of the page?")
    items += [("news", f"{rel}{p['slug']}/", "Trades news") for p in PAGES_LIVE if p.get("kind") == "tradesnews"][:1]
    if LIVE_QUESTIONS:
        items.append(("questions", f"{rel}questions/", "Questions"))
    cur = ' aria-current="page"'
    plain = "".join(f'<a href="{h}"{cur if k == current else ""}>{t}</a>' for k, h, t in items)
    links = f'<span class="nav-links">{plain}</span>'
    # one clear action in every header (design review, Oct 24, 2026): the trade picker on the home hero, one tap from a free sample
    # store v2 quick-find (hidden until assets/pnf-ui.js wires it, so no dead button without the script)
    links += ('<button type="button" class="qf-btn" data-qf hidden aria-label="Search calculators, lead lists and guides">'
              '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
              '<span class="qf-lab">Search</span><kbd aria-hidden="true">/</kbd></button>')
    links += f'<a class="navcta" href="{rel or "./"}#trades">Free samples</a>'
    # phones: one slim row (logo, search, menu) with the links in a sheet; a details element, so it works without script
    # (store v2 review round 3, Oct 24: the header wrapped to two or three rows at 390)
    links += ('<details class="navm"><summary aria-label="Menu"><svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></summary>'
              f'<div class="navm-sheet">{plain}<a class="btn" href="{rel or "./"}#trades">Free samples</a></div></details>')
    return f'<nav class="top" aria-label="Main">{links}</nav>'


def foot_nav(rel):
    """The footer links on every page: the shop, the calculators, the refund and privacy pages, the Etsy workbooks and the mailbox."""
    q = f'<a href="{rel}questions/">Questions</a>' if LIVE_QUESTIONS else ""
    # the free Chicago data pages that are no calculator (rat tracker live Oct 26 on Todd's go): linked from every page
    q += "".join(f'<a href="{rel}{p["slug"]}/">Chicago rat complaints</a>' for p in PAGES_LIVE if p.get("kind") == "rodents")
    q += "".join(f'<a href="{rel}{p["slug"]}/">Chicago trades news</a>' for p in PAGES_LIVE if p.get("kind") == "tradesnews")   # Todd, Oct 27
    q += f'<a href="{rel}chicago-data/">Free Chicago data</a>' if live_datapages() else ""   # the hub of the data pages (Oct 27)
    return (f'<nav class="fnav" aria-label="Footer"><a href="{rel}shop/">Shop</a><a href="{rel}calculators/">Free calculators</a>{q}'
            f'<a href="{rel}refunds/">Refunds and cancelling</a><a href="{rel}privacy/">Privacy</a><a href="{SHOP}">Workbooks on Etsy</a>'
            '<a href="mailto:hello@proofnotfluff.com">hello@proofnotfluff.com</a></nav>')


def og_tags(url):
    slug = url[len(BASE):].strip("/") or "home"
    rel = f"assets/og/{slug.replace('/', '-')}.png"
    if not os.path.isfile(os.path.join(DOCS, rel)):
        rel = "assets/og/home.png"
    return (f'<meta property="og:image" content="{BASE}{rel}"><meta property="og:image:width" content="1200">'
            f'<meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">')


class _Tpl(str):
    """HEAD and FOOT keep their old .format() keywords (tools/rest_site.py, lic_site.py and question_site.py call them);
    the store's new pieces (nav, footer links, Open Graph image) are filled in here."""
    def format(self, **kw):
        # a title over 60 characters drops the brand suffix, so search results show the words that match the query
        # (SEO audit, Oct 24, 2026: 56 of 63 titles ran past 60; Google appends the site name on its own)
        if "title" in kw and len(html.unescape(kw["title"])) > 60 and kw["title"].endswith(" | ProofNotFluff"):
            kw["title"] = kw["title"][:-len(" | ProofNotFluff")]
        kw.setdefault("nav", nav_html(kw.get("rel", ""), CURRENT.get("nav", "")))
        kw.setdefault("og", og_tags(kw["url"]) if "url" in kw else "")
        kw.setdefault("fnav", foot_nav(kw.get("rel", "")))
        kw.setdefault("notices", "")
        kw.setdefault("ogtype", "website")
        return str.format(self, **kw)


HEAD = _Tpl(HEAD_TPL)
FOOT = _Tpl(FOOT_TPL)


def field(key, label, value, hint="", pre="", suf="", step="any"):
    cls = "field" + (" has-pre" if pre else "") + (" has-suf" if suf else "")
    return (f'<div class="row"><label for="{key}">{E(label)}{f"<small>{E(hint)}</small>" if hint else ""}</label>'
            f'<div class="{cls}">{f"<span class=pre>{pre}</span>" if pre else ""}'
            f'<input id="{key}" data-in="{key}" type="text" inputmode="decimal" value="{value}" autocomplete="off">'
            f'{f"<span class=suf>{suf}</span>" if suf else ""}</div></div>')


def faq_block(faqs):
    items = "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faqs)
    return f'<section class="block"><h2>Questions</h2>{items}</section>'


def ld_json(page, url):
    data = [{"@context": "https://schema.org", "@type": "WebApplication", "name": page["h1"], "url": url,
             "applicationCategory": "BusinessApplication", "operatingSystem": "Any", "isAccessibleForFree": True,
             "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "publisher": {"@type": "Organization", "name": "ProofNotFluff"}},
            {"@context": "https://schema.org", "@type": "FAQPage",
             "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in page["faq"]]}]
    return "".join(f'<script type="application/ld+json">{json.dumps(d)}</script>' for d in data)


def cta(page):
    c = page["cta"]
    bullets = " ".join(E(b) for b in c["bullets"])
    return (f'<section class="block"><div class="cta"><div><h2>{E(c["title"])}</h2><p>{bullets}</p></div>'
            + (f'<div><a class="btn" href="{E(c["url"])}">{E(c["button"])}</a>' if c.get("url")
               else f'<div><span class="btn soon" aria-disabled="true">{E(c["button"])}</span>')
            + '</div></div></section>')


def service_page(p):
    d = p["defaults"]
    presets = p["presets"]
    opts = "".join(f'<option value="{i}"{" selected" if i == p.get("preset_default", 0) else ""}>{E(x[0])}</option>' for i, x in enumerate(presets))
    q0 = presets[p.get("preset_default", 0)]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>Your year</legend>
{field("takeHome", "Take-home pay you want", d["takeHome"], "What you keep after tax, per year", pre="$")}
{field("weeks", "Weeks you work per year", d["weeks"], "52 minus vacation and slow weeks")}
{field("hours", "Hours you work per week, all of it", d["hours"], "Driving, quoting and admin included")}
{field("paidShare", "Share of those hours customers pay for", d["paidShare"], "Not sure? Try 60 to 70", suf="%")}
</fieldset>
<fieldset><legend>Costs and taxes</legend>
{field("monthlyCosts", "Business costs per month", d["monthlyCosts"], p["costs_hint"], pre="$")}
{field("incomeTax", "Income tax rate, your estimate", d["incomeTax"], "Self-employment tax of 15.3% is added for you", suf="%")}
{field("margin", "Profit margin in quotes", d["margin"], "", suf="%")}
{field("perMile", "Vehicle cost per mile", d["perMile"], "IRS business rate: 76 cents (Jul to Dec 2026)", pre="$")}
{field("mph", "Average speed between jobs", d["mph"], "Miles per hour")}
</fieldset>
<fieldset><legend>The job</legend>
<div class="row pick"><label for="preset">Start from an example job<small>Starting points, not market prices. Change any number.</small></label>
<div class="field"><select id="preset">{opts}</select></div></div>
{field("jobHours", "Hours on site per person", q0[1])}
{field("people", "People on the job", q0[2])}
{field("supplies", "Supplies for this job", q0[3], pre="$")}
{field("miles", "Round-trip miles", q0[4])}
</fieldset></form>"""
    results = f"""<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Quote for this job</div><div class="val" data-out="quote" data-fmt="money0">$0</div><div class="sub">Rounded up to the next $5</div></div>
<div class="tile"><div class="lab">Profit in the quote</div><div class="val" data-out="quoteProfit">$0</div><div class="sub">After your pay, costs and taxes</div></div>
<div class="tile"><div class="lab">Break-even per paid hour</div><div class="val" data-out="breakEven">$0</div></div>
<div class="tile"><div class="lab">Target rate per paid hour</div><div class="val" data-out="target">$0</div></div>
</div>
<ul class="lines">
<li><span>Your time on site</span><span data-out="labor">$0</span></li>
<li><span>Drive time (<span data-out="drive" data-fmt="hrs">0</span> each)</span><span data-out="driveCost">$0</span></li>
<li><span>Vehicle</span><span data-out="vehicle">$0</span></li>
<li><span>Supplies</span><span data-out="supplies">$0</span></li>
<li class="total"><span>Price floor, zero profit</span><span data-out="floor">$0</span></li>
</ul>
<div class="callout">Pay divided by all your hours says <b data-out="guess">$0</b> an hour. Your real break-even is <b data-out="breakEven">$0</b>.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Quote <b data-out="quote" data-fmt="money0">$0</b></span><span>Break-even <b data-out="breakEven">$0</b>/hr</span></div>"""
    presets_js = json.dumps([x[1:] for x in presets])
    script = f"""<script>
(function(){{var f=document.getElementById("calc"),P={presets_js};
document.getElementById("preset").addEventListener("change",function(e){{var v=P[+e.target.value];
["jobHours","people","supplies","miles"].forEach(function(k,i){{document.getElementById(k).value=v[i];}});
f.dispatchEvent(new Event("input"));}});
PNF.wire(f,PNF.service);}})();</script>"""
    return form, results, script


def hourly_page(p):
    d = p["defaults"]
    w = {"expenses": ("Business expenses per year", "Software, insurance, equipment, fees"),
         "materials": ("Materials and other project costs", "Stock, prints, software for this client, travel"),
         "jobHours": ("Billable hours for the project", "Your best estimate"),
         "quoteLegend": "Quote one project", "projectLabor": "Project labor at your rate card", "projectQuote": "Project quote"}
    w.update(p.get("wording", {}))  # trade wording (contractor page); the maths and fields stay the same
    quote_fs = quote_out = ""
    if p.get("quote"):  # #20's Quick quote card (rows 41 to 43) and its billable-share table (I31:I34)
        quote_fs = f"""
<fieldset><legend>{E(w["quoteLegend"])}</legend>
{field("jobHours", w["jobHours"][0], d["jobHours"], w["jobHours"][1])}
{field("materials", w["materials"][0], d["materials"], w["materials"][1], pre="$")}
{field("markup", "Markup on those costs", d["markup"], "0 to pass costs through", suf="%")}
</fieldset>"""
        quote_out = f"""
<ul class="lines">
<li><span>{E(w["projectLabor"])}</span><span data-out="quoteLabor" data-fmt="money2">$0</span></li>
<li><span>Costs with markup</span><span data-out="quoteMaterials" data-fmt="money2">$0</span></li>
<li class="total"><span>{E(w["projectQuote"])}</span><span data-out="quote" data-fmt="money2">$0</span></li>
</ul>
<details><summary>The rate you need if you bill more of your week</summary><ul class="lines">
<li><span>50% of your hours billed</span><span data-out="rateAt50">$0</span></li>
<li><span>60% of your hours billed</span><span data-out="rateAt60">$0</span></li>
<li><span>70% of your hours billed</span><span data-out="rateAt70">$0</span></li>
<li><span>80% of your hours billed</span><span data-out="rateAt80">$0</span></li>
</ul></details>"""
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>What you want to take home</legend>
{field("takeHome", "Take-home pay you want per year", d["takeHome"], "After tax", pre="$")}
{field("taxRate", "Tax set-aside rate", d["taxRate"], "Share of profit you set aside for tax", suf="%")}
{field("expenses", w["expenses"][0], d["expenses"], w["expenses"][1], pre="$")}
</fieldset>
<fieldset><legend>Your working time</legend>
{field("weeks", "Weeks you work per year", d["weeks"])}
{field("hours", "Hours you work per week", d["hours"])}
{field("billableShare", "Share of hours a client pays for", d["billableShare"], "Not sure? Try 50 to 70", suf="%")}
</fieldset>
<fieldset><legend>Check a rate you are considering</legend>
{field("checkRate", "Hourly rate to check", d["checkRate"], pre="$")}
</fieldset>{quote_fs}</form>"""
    results = f"""<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Your minimum hourly rate</div><div class="val" data-out="rate">$0</div><div class="sub">Rate card: <span data-out="rateCard" data-fmt="money0">$0</span> an hour</div></div>
<div class="tile"><div class="lab">Billable hours a year</div><div class="val" data-out="billable" data-fmt="int">0</div></div>
</div>
<ul class="lines">
<li><span>Revenue you need</span><span data-out="revenue" data-fmt="money0">$0</span></li>
<li><span>Hours you work per year</span><span data-out="worked" data-fmt="int">0</span></li>
<li class="total"><span>At the rate you are checking, you keep</span><span data-out="keep" data-fmt="money0">$0</span></li>
<li><span>Per hour you actually work</span><span data-out="keepPerHour">$0</span></li>
</ul>
<div class="callout warn" data-show-if="shortBy > 0">That rate leaves you <b data-out="shortBy" data-fmt="money0">$0</b> a year short of your goal.</div>
<div class="callout" data-show-if="shortBy < 0.01">That rate meets your take-home goal.</div>{quote_out}
</div></div>
<div class="mbar" aria-hidden="true"><span>Minimum rate <b data-out="rate">$0</b></span><span>At your rate <b data-out="keepPerHour">$0</b>/hr</span></div>"""
    script = '<script>PNF.wire(document.getElementById("calc"),PNF.hourly);</script>'
    return form, results, script


def cashflow_page(p):
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>Where you start</legend>
{field("openingCash", "Cash in the bank today", d["openingCash"], "All operating accounts together", pre="$")}
</fieldset>
<fieldset><legend>A normal week</legend>
{field("weeklyIn", "Cash in per week, after fees", d["weeklyIn"], "Payouts that reach your bank, not sales", pre="$")}
{field("weeklyOut", "Fixed costs and ads per week", d["weeklyOut"], "Payroll, rent, software, ad spend", pre="$")}
</fieldset>
<fieldset><legend>One purchase order</legend>
{field("poAmount", "PO payment", d["poAmount"], "Balance plus freight, or the whole PO", pre="$")}
{field("poWeek", "Week it is due, 1 to 13", d["poWeek"])}
</fieldset></form>"""
    weeks = "".join(f'<li><span>Week {t}</span><span data-out="end{t}" data-fmt="money0">$0</span></li>' for t in range(1, 14))
    results = f"""<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Lowest cash in 13 weeks</div><div class="val" data-out="lowest" data-fmt="money0">$0</div><div class="sub"><span data-out="lowWeek" data-fmt="week">Week 1</span></div></div>
<div class="tile"><div class="lab">Cash needed to stay above $0</div><div class="val" data-out="gap" data-fmt="money0">$0</div></div>
</div>
<div class="callout warn" data-show-if="gap > 0">Cash goes below zero. Cover <b data-out="gap" data-fmt="money0">$0</b> before that week, or move the PO.</div>
<div class="callout" data-show-if="gap < 0.01">Cash stays above zero in all 13 weeks.</div>
<details><summary>Ending cash, week by week</summary><ul class="lines">{weeks}</ul></details>
</div></div>
<div class="mbar" aria-hidden="true"><span>Lowest <b data-out="lowest" data-fmt="money0">$0</b></span><span>Needed <b data-out="gap" data-fmt="money0">$0</b></span></div>"""
    script = '<script>PNF.wire(document.getElementById("calc"),PNF.cashflow);</script>'
    return form, results, script


def asof_note(p):
    a = p["asof"]
    links = " and ".join(f'<a href="{E(u)}" rel="noopener">{E(t)}</a>' for t, u in a["from"])
    return f'<p class="asof">{E(a["lead"])} {E(a["date"])}, from {links}. {E(a.get("tail", ""))}</p>'


def etsy_fees_page(p):
    d, f = p["defaults"], p["fees"]
    ads = "".join(f'<option value="{v}"{" selected" if v == d["adsRate"] else ""}>{E(t)}</option>' for v, t in p["ads_options"])
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>The sale</legend>
{field("price", "Item price", d["price"], "What the buyer pays for the item", pre="$")}
{field("ship", "Shipping you charge", d["ship"], "0 for free shipping", pre="$")}
{field("tax", "Sales tax the buyer paid", d["tax"], "Processing is charged on it too. 0 if unsure", pre="$")}
</fieldset>
<fieldset><legend>Your costs</legend>
{field("cost", "Item cost", d["cost"], "Materials, packaging and your making time", pre="$")}
{field("label", "Shipping label cost", d["label"], "What postage really costs you", pre="$")}
</fieldset>
<fieldset><legend>Offsite Ads</legend>
<div class="row pick"><label for="adsRate">Did this sale come through an Offsite Ad?<small>Etsy charges the fee only on orders it attributes to its ads.</small></label>
<div class="field"><select id="adsRate" data-in="adsRate">{ads}</select></div></div>
</fieldset>
<fieldset><legend>Etsy's US fees</legend>
{field("tfRate", "Transaction fee", f["tfRate"], "On item price plus shipping, not on US sales tax", suf="%")}
{field("procRate", "Payment processing, percent", f["procRate"], "On the total paid, tax included", suf="%")}
{field("procFixed", "Payment processing, per order", f["procFixed"], "Outside the US? Type your rates", pre="$")}
{field("listFee", "Listing fee", f["listFee"], "Charged again when a listing renews after a sale", pre="$")}
</fieldset></form>"""
    results = f"""<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Profit per sale</div><div class="val" data-out="profit">$0</div><div class="sub"><span data-pct="margin">0%</span> of what the buyer paid you</div></div>
<div class="tile"><div class="lab">Etsy pays you</div><div class="val" data-out="payout">$0</div><div class="sub">Before your costs</div></div>
</div>
<ul class="lines">
<li><span>Item plus shipping</span><span data-out="revenue">$0</span></li>
<li><span>Transaction fee</span><span data-out="tf">$0</span></li>
<li><span>Payment processing</span><span data-out="pf">$0</span></li>
<li><span>Listing fee</span><span data-out="lf">$0</span></li>
<li><span>Offsite Ads fee</span><span data-out="ads">$0</span></li>
<li class="total"><span>Etsy fees, <span data-pct="feeShare">0%</span> of the sale</span><span data-out="fees">$0</span></li>
<li><span>Item cost</span><span data-out="cost">$0</span></li>
<li><span>Shipping label</span><span data-out="label">$0</span></li>
<li class="total"><span>Profit</span><span data-out="profit">$0</span></li>
</ul>
<div class="callout warn" data-show-if="profit < 0">This sale loses <b data-out="loss">$0</b> after fees and costs.</div>
<div class="callout" data-show-if="adsOff > 0">If this sale came through an Offsite Ad at 15%, the fee would be <b data-out="adsIf">$0</b> and profit <b data-out="profitIfAds">$0</b>.</div>
<div class="callout" data-show-if="adsOff < 1">Offsite Ads took <b data-out="ads">$0</b> of this sale.</div>
{asof_note(p)}
</div></div>
<div class="mbar" aria-hidden="true"><span>Profit <b data-out="profit">$0</b></span><span>Fees <b data-out="fees">$0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc"),CAP=""" + json.dumps(p["ads_cap"]) + """;
/* Maths: PNF.etsyFees in assets/pnf-calc.js, the Listings tab of engines/etsy-true-profit (#5). */
function M(i){return PNF.etsyFees(i,CAP);}
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def craft_fair_page(p):
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>The show</legend>
{field("booth", "Booth fee", d["booth"], "From the show's application", pre="$")}
{field("other", "Other costs of the day", d["other"], "Travel, parking, meals, extras, a share of your tent and display", pre="$")}
</fieldset>
<fieldset><legend>What you sell</legend>
{field("price", "Average price per piece", d["price"], "Before sales tax", pre="$")}
{field("cpp", "Cost per piece", d["cpp"], "Materials, packaging and your making time", pre="$")}
</fieldset>
<fieldset><legend>Card payments</legend>
{field("cardPct", "Card fee, percent", d["cardPct"], "Match your reader", suf="%")}
{field("cardFlat", "Card fee, per payment", d["cardFlat"], "The flat part, if your reader has one", pre="$")}
{field("cardShare", "Share of sales paid by card", d["cardShare"], "Cash has no fee", suf="%")}
{field("avgSale", "Average spend per customer", d["avgSale"], "Spreads the flat fee over a sale", pre="$")}
</fieldset>
<fieldset><legend>Your goal</legend>
{field("target", "Profit you want from the day", d["target"], "On top of every cost", pre="$")}
</fieldset></form>"""
    results = f"""<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Pieces to break even</div><div class="val" data-out="bePieces" data-fmt="int" data-never="Never">0</div><div class="sub" data-show-if="never < 1"><span data-out="beSales">$0</span> in sales</div></div>
<div class="tile"><div class="lab">Pieces for your profit</div><div class="val" data-out="tgtPieces" data-fmt="int" data-never="Never">0</div><div class="sub" data-show-if="never < 1"><span data-out="tgtSales">$0</span> in sales</div></div>
</div>
<ul class="lines">
<li><span>Booth fee</span><span data-out="booth">$0</span></li>
<li><span>Other costs of the day</span><span data-out="other">$0</span></li>
<li class="total"><span>What the day costs</span><span data-out="total">$0</span></li>
<li><span>Average price per piece</span><span data-out="price">$0</span></li>
<li><span>Cost per piece</span><span data-out="cpp">$0</span></li>
<li><span>Card fee per piece</span><span data-out="cardPer">$0</span></li>
<li class="total"><span>Each piece earns</span><span data-out="contrib">$0</span></li>
<li data-show-if="never < 1"><span>Profit at <span data-out="tgtPieces" data-fmt="int">0</span> pieces</span><span data-out="tgtProfit">$0</span></li>
</ul>
<div class="callout warn" data-show-if="never > 0">Each piece earns nothing after its cost and the card fee, so no number of sales covers the day. Raise the price or cut the cost per piece.</div>
<div class="callout" data-show-if="never < 1">The booth fee is <b data-pct="boothShare">0%</b> of what this day costs.</div>
{asof_note(p)}
</div></div>
<div class="mbar" aria-hidden="true"><span>Break even <b data-out="bePieces" data-fmt="int" data-never="Never">0</b> pieces</span><span>Goal <b data-out="tgtPieces" data-fmt="int" data-never="Never">0</b> pieces</span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.craftFair in assets/pnf-calc.js, the Break-Even tab of engines/craft-fair-profit (#12). */
var M=PNF.craftFair;
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


MONTHS3 = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def str_nightly_page(p):
    d = p["defaults"]
    curves = p["curves"]   # [[label, [12 values]], ...]; the first one is the default
    opts = "".join(f'<option value="{i}">{E(c[0])}</option>' for i, c in enumerate(curves))
    months = "".join(field(f"h{m + 1}", MONTHS3[m], f"{curves[0][1][m]:,}") for m in range(12))
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>Your listing</legend>
{field("base", "Base nightly rate", d["base"], "Your rate for an average month", pre="$")}
{field("floor", "Floor per night", d["floor"], "The lowest rate you take. No month goes under it", pre="$")}
{field("cleaning", "Cleaning fee", d["cleaning"], "Per stay", pre="$")}
{field("minStay", "Minimum stay", d["minStay"], "Nights")}
{field("fee", "Platform fee you pay", d["fee"], "Airbnb's single host fee: 15.5% for most hosts", suf="%")}
</fieldset>
<fieldset><legend>The shape of your year</legend>
<div class="row pick"><label for="curve">Start from<small>Last year's revenue by month, or a starter curve if you have no history. Only the shape counts: each month against the average month.</small></label>
<div class="field"><select id="curve">{opts}</select></div></div>
<div class="duo">{months}</div>
</fieldset></form>"""
    rows = "".join(f'<tr><th scope="row">{MONTHS3[m]}</th><td data-out="mult{m + 1}" data-fmt="mult">1.00x</td>'
                   f'<td><b data-out="night{m + 1}" data-fmt="money0">$0</b> <span class="tag" data-out="flag{m + 1}" data-fmt="text"></span></td>'
                   f'<td data-out="pay{m + 1}">$0</td></tr>' for m in range(12))
    results = f"""<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Busiest month</div><div class="val" data-out="hiNight" data-fmt="money0">$0</div><div class="sub"><span data-out="hiMonth" data-fmt="text">-</span>, <span data-out="hiMult" data-fmt="mult">1.00x</span> your base rate</div></div>
<div class="tile"><div class="lab">Quietest month</div><div class="val" data-out="loNight" data-fmt="money0">$0</div><div class="sub"><span data-out="loMonth" data-fmt="text">-</span><span data-show-if="loHeld > 0">: <span data-out="loBase" data-fmt="money0">$0</span> before your floor</span><span data-show-if="loHeld < 1">, <span data-out="loMult" data-fmt="mult">1.00x</span> your base rate</span></div></div>
</div>
<table class="mt"><thead><tr><th scope="col">Month</th><th scope="col">Season</th><th scope="col">Nightly rate</th><th scope="col">After fee</th></tr></thead><tbody>{rows}</tbody></table>
<ul class="lines">
<li><span>Months held at your floor</span><span data-out="atFloor" data-fmt="int">0</span></li>
<li><span>Shortest stay in <span data-out="loMonth" data-fmt="text">-</span>, <span data-out="minStay" data-fmt="int">0</span> nights</span><span data-out="stayNights" data-fmt="money0">$0</span></li>
<li><span>Cleaning fee</span><span data-out="cleaning" data-fmt="money0">$0</span></li>
<li class="total"><span>That stay, before platform fees</span><span data-out="stayTotal" data-fmt="money0">$0</span></li>
</ul>
<div class="callout warn" data-show-if="valid < 1">Type at least one month above zero to shape the year.</div>
<div class="callout warn" data-show-if="hasZero > 0">A month at 0 prices at your floor. A quiet month still needs a small number.</div>
<div class="callout" data-show-if="atFloor > 0">Your floor lifts <b data-out="atFloor" data-fmt="int">0</b> of 12 months. Without it, <span data-out="loMonth" data-fmt="text">-</span> would price at <b data-out="loBase" data-fmt="money0">$0</b>.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Busiest <b data-out="hiNight" data-fmt="money0">$0</b></span><span>Quietest <b data-out="loNight" data-fmt="money0">$0</b></span></div>"""
    curves_js = json.dumps([c[1] for c in curves])
    script = f"""<script>
(function(){{var f=document.getElementById("calc"),C={curves_js};
/* Maths: PNF.strNightly in assets/pnf-calc.js, the 2 Seasonality and 4 Stay Discounts tabs of engines/str-nightly-pricing (#9). */
document.getElementById("curve").addEventListener("change",function(e){{var v=C[+e.target.value];
for(var m=1;m<=12;m++)document.getElementById("h"+m).value=v[m-1].toLocaleString("en-US");
f.dispatchEvent(new Event("input"));}});
PNF.wire(f,PNF.strNightly);window.PNF_MODEL=PNF.strNightly;}})();</script>"""
    return form, results, script


def debt_payoff_page(p):
    d = p["defaults"]
    rows = ""
    for k in range(1, 6):
        b, a, m = d["debts"][k - 1] if k <= len(d["debts"]) else ("", "", "")
        rows += (f'<div class="drow"><div class="dname">Debt {k}</div>'
                 f'<div class="field has-pre"><span class=pre>$</span><input id="b{k}" data-in="b{k}" type="text" inputmode="decimal" value="{b}" autocomplete="off" aria-label="Debt {k} balance"></div>'
                 f'<div class="field has-suf"><input id="a{k}" data-in="a{k}" type="text" inputmode="decimal" value="{a}" autocomplete="off" aria-label="Debt {k} APR"><span class=suf>%</span></div>'
                 f'<div class="field has-pre"><span class=pre>$</span><input id="m{k}" data-in="m{k}" type="text" inputmode="decimal" value="{m}" autocomplete="off" aria-label="Debt {k} minimum payment"></div></div>')
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>Your debts</legend>
<p class="fsnote">Up to five. Leave a balance at 0 to skip a row.</p>
<div class="debts"><div class="drow dhead" aria-hidden="true"><div></div><div>Balance</div><div>APR</div><div>Minimum</div></div>{rows}</div>
</fieldset>
<fieldset><legend>Each month</legend>
{field("extra", "Extra on top of the minimums", d["extra"], "The minimums are added for you", pre="$")}
</fieldset></form>"""
    sno = p.get("focus") == "snowball"
    # A snowball page leads with smallest-balance-first; the default page leads with highest-APR-first.
    lead, other = (("sno", "Snowball"), ("ava", "Avalanche")) if sno else (("ava", "Avalanche"), ("sno", "Snowball"))
    plan_rows = {"ava": ("Avalanche, highest APR first", "avaMonths", "avaInt", "avaNever"),
                 "sno": ("Snowball, smallest balance first", "snoMonths", "snoInt", "snoNever")}
    def plan_tr(key):
        name, mo, it, nv = plan_rows[key]
        return (f'<tr><th scope="row">{name}</th><td data-out="{mo}" data-fmt="int" data-never="20+ yrs" data-never-if="{nv}">0</td>'
                f'<td data-out="{it}" data-fmt="money0" data-never="n/a" data-never-if="{nv}">$0</td></tr>')
    L = lead[0]
    compare = ('<div class="callout" data-show-if="avaVsSno > 0.5">Avalanche estimate on the same payment: about '
               '<b data-out="avaVsSno" data-fmt="money0">$0</b> less interest than snowball. Snowball clears its first debt sooner.</div>') if sno else ""
    results = f"""<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">{lead[1]}, months to pay off</div><div class="val" data-out="{L}Months" data-fmt="int" data-never="20+ years" data-never-if="{L}Never">0</div><div class="sub">Interest about <span data-out="{L}Int" data-fmt="money0" data-never="n/a" data-never-if="{L}Never">$0</span></div></div>
<div class="tile"><div class="lab">Minimums only, months</div><div class="val" data-out="minMonths" data-fmt="int" data-never="Never" data-never-if="minNever">0</div><div class="sub">Interest about <span data-out="minInt" data-fmt="money0" data-never="n/a" data-never-if="minNever">$0</span></div></div>
</div>
<table class="mt"><thead><tr><th scope="col">Plan</th><th scope="col">Months</th><th scope="col">Interest (est.)</th></tr></thead><tbody>
{plan_tr(lead[0])}
{plan_tr(other[0])}
<tr><th scope="row">Minimums only, no roll-over</th><td data-out="minMonths" data-fmt="int" data-never="Never" data-never-if="minNever">0</td><td data-out="minInt" data-fmt="money0" data-never="n/a" data-never-if="minNever">$0</td></tr>
</tbody></table>
<ul class="lines">
<li><span>Owed today</span><span data-out="owed">$0</span></li>
<li><span>Minimums add up to</span><span data-out="minSum">$0</span></li>
<li><span>Extra each month</span><span data-out="extra">$0</span></li>
<li class="total"><span>Paid each month in both plans</span><span data-out="monthly">$0</span></li>
</ul>
<div class="callout" data-show-if="savedOk > 0">{lead[1]} estimate: <b data-out="{L}Saved" data-fmt="money0">$0</b> less interest than minimums only.</div>
{compare}
<div class="callout warn" data-show-if="minNever > 0">At least one minimum does not cover its monthly interest, so on minimums only that balance keeps growing.</div>
<div class="callout warn" data-show-if="{L}Never > 0">At this payment the plans run past 20 years. Try a larger extra amount.</div>
<div class="callout warn" data-show-if="empty > 0">Type a balance for at least one debt.</div>
<details><summary>When each debt is paid off</summary>
<table class="mt"><thead><tr><th scope="col">Debt</th><th scope="col">{lead[1]}</th><th scope="col">{other[1]}</th><th scope="col">Minimums</th></tr></thead><tbody>""" + "".join(
        f'<tr><th scope="row">Debt {k}</th><td data-out="{lead[0]}{k}" data-fmt="text">-</td><td data-out="{other[0]}{k}" data-fmt="text">-</td><td data-out="min{k}" data-fmt="text">-</td></tr>'
        for k in range(1, 6)) + f"""</tbody></table></details>
</div></div>
<div class="mbar" aria-hidden="true"><span>{lead[1]} <b data-out="{L}Months" data-fmt="int" data-never="20+ yrs" data-never-if="{L}Never">0</b> mo</span><span>Minimums <b data-out="minMonths" data-fmt="int" data-never="Never" data-never-if="minNever">0</b> mo</span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.debtPayoff in assets/pnf-calc.js, the plan grids and minimums-only columns of engines/debt-payoff-tracker (#16). */
var M=PNF.debtPayoff;
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def shipping_cost_page(p):
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>What the buyer pays</legend>
{field("charged", "Shipping you charge", d["charged"], "0 for free shipping", pre="$")}
</fieldset>
<fieldset><legend>What the parcel costs you</legend>
{field("postage", "Label you paid", d["postage"], "From your label receipt", pre="$")}
{field("box", "Box or mailer", d["box"], pre="$")}
{field("filler", "Filler", d["filler"], "Wrap, tissue or peanuts", pre="$")}
{field("tape", "Tape", d["tape"], "A $34 roll that seals 400 parcels is 8.5 cents", pre="$")}
{field("labelPaper", "Label paper or ink", d["labelPaper"], pre="$")}
</fieldset>
<fieldset><legend>Your packing time</legend>
{field("minutes", "Minutes to pack one order", d["minutes"], "Time yourself twice and use the average")}
{field("hourly", "Your hourly rate", d["hourly"], "What an hour of your time is worth", pre="$")}
</fieldset>
<fieldset><legend>Fees on the shipping you charge</legend>
{field("feePct", "Marketplace fees on shipping", d["feePct"], "Etsy US: 6.5% transaction plus 3% processing. Type yours for other sites", suf="%")}
</fieldset></form>"""
    results = f"""<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">True cost per order</div><div class="val" data-out="total">$0</div><div class="sub">Parcel <span data-out="parcel">$0</span> plus <span data-out="fees">$0</span> of fees</div></div>
<div class="tile"><div class="lab">Over or under per order</div><div class="val" data-out="net">$0</div><div class="sub">Shipping charged minus true cost</div></div>
</div>
<ul class="lines">
<li><span>Label</span><span data-out="postage">$0</span></li>
<li><span>Box, filler, tape and label paper</span><span data-out="materials">$0</span></li>
<li><span>Packing time</span><span data-out="labor">$0</span></li>
<li class="total"><span>Parcel cost</span><span data-out="parcel">$0</span></li>
<li><span>Over or under before fees</span><span data-out="shortfall">$0</span></li>
<li><span>Fees on the shipping you charge</span><span data-out="fees">$0</span></li>
<li class="total"><span>True cost per order</span><span data-out="total">$0</span></li>
<li><span>Shipping you charge</span><span data-out="charged">$0</span></li>
<li class="total"><span>Over or under per order</span><span data-out="net">$0</span></li>
</ul>
<div class="callout warn" data-show-if="isUnder > 0">Each order is <b data-out="under">$0</b> short, <b data-out="underPer100" data-fmt="money0">$0</b> over 100 orders. Shipping of <b data-out="breakEven">$0</b> covers the parcel and its fees.</div>
<div class="callout" data-show-if="isUnder < 1">The shipping you charge covers the parcel and its fees. Break-even shipping: <b data-out="breakEven">$0</b>.</div>
{asof_note(p)}
</div></div>
<div class="mbar" aria-hidden="true"><span>True cost <b data-out="total">$0</b></span><span>Per order <b data-out="net">$0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.shippingCost in assets/pnf-calc.js, the 1 Parcel Costs tab of engines/shipping-true-cost (#7). */
var M=PNF.shippingCost;
PNF.wire(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def reorder_point_page(p):
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>How fast it sells</legend>
{field("daily", "Units sold per day", d["daily"], "Units sold in the last 30 days, divided by 30")}
{field("lead", "Supplier lead time, days", d["lead"], "From placing an order to having it on your shelf")}
</fieldset>
<fieldset><legend>Your cushion and rhythm</legend>
{field("safety", "Safety stock", d["safety"], "Extra on top of lead-time sales. Raise it for suppliers that run late", suf="%")}
{field("cycle", "Days between your orders", d["cycle"], "How often you order from this supplier")}
</fieldset>
<fieldset><legend>Where you are now</legend>
{field("onHand", "Units on hand", d["onHand"])}
{field("onOrder", "Units already on order", d["onOrder"], "Ordered but not arrived yet")}
{field("unitCost", "Unit cost", d["unitCost"], "What you pay the supplier per unit", pre="$")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Reorder point</div><div class="val"><span data-out="rop" data-fmt="dec1">0.0</span> units</div><div class="sub" data-out="statusText" data-fmt="text">-</div></div>
<div class="tile"><div class="lab"><span data-show-if="orderNow > 0">Order now</span><span data-show-if="orderNow < 1">Next order</span></div><div class="val"><span data-out="units" data-fmt="int">0</span> units</div><div class="sub"><span data-out="orderCost">$0</span> at your unit cost</div></div>
</div>
<ul class="lines">
<li><span>Sales while an order is on its way, plus cushion</span><span><span data-out="rop" data-fmt="dec1">0.0</span> units</span></li>
<li><span>Order up to</span><span><span data-out="upTo" data-fmt="dec1">0.0</span> units</span></li>
<li><span>Days of stock on hand</span><span data-out="days" data-fmt="dec1">0.0</span></li>
<li class="total"><span>Days until you reach the reorder point</span><span data-out="untilShow" data-fmt="dec1">0.0</span></li>
</ul>
<div class="callout warn" data-show-if="risk > 0">On hand lasts <b data-out="days" data-fmt="dec1">0.0</b> days, <b data-out="shortDays" data-fmt="dec1">0.0</b> fewer than your lead time, and nothing is on order. Order <b data-out="units" data-fmt="int">0</b> units now, and ask about faster shipping.</div>
<div class="callout warn" data-show-if="atRop > 0">On hand plus on order is at or under the reorder point. Ordering <b data-out="units" data-fmt="int">0</b> units brings you back up to <b data-out="upTo" data-fmt="dec1">0.0</b>.</div>
<div class="callout" data-show-if="soon > 0">You reach the reorder point in about <b data-out="untilShow" data-fmt="dec1">0.0</b> days. Plan about <b data-out="orderCost">$0</b> for that order.</div>
<div class="callout" data-show-if="later > 0">More than 30 days of stock above the reorder point. No order needed this month.</div>
<div class="callout warn" data-show-if="noSales > 0">Type units sold per day above zero. With no sales there is nothing to plan from.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Reorder at <b data-out="rop" data-fmt="dec1">0.0</b></span><span>Order <b data-out="units" data-fmt="int">0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.reorderPoint in assets/pnf-calc.js, the 2 SKU List tab of engines/cash-aware-reorder-planner (#6). */
var M=PNF.reorderPoint;
PNF.wire(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def inventory_turnover_page(p):
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>Your whole shop</legend>
{field("cogsYear", "Cost of goods sold, last 12 months", d["cogsYear"], "What the units you sold cost you, not what you sold them for", pre="$")}
{field("stockValue", "Stock on hand, valued at cost", d["stockValue"], "Units on hand x what you paid per unit, for every product", pre="$")}
</fieldset>
<fieldset><legend>Check one product</legend>
{field("daily", "Units sold per day", d["daily"], "Units sold in the last 30 days, divided by 30")}
{field("onHand", "Units on hand", d["onHand"])}
{field("overDays", "Overstock at this many days of stock", d["overDays"], "The workbook's default is 120")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Inventory turns a year</div><div class="val"><span data-out="turns" data-fmt="dec1">0.0</span></div><div class="sub">Cost of goods sold / stock at cost</div></div>
<div class="tile"><div class="lab">Days to sell through your stock</div><div class="val"><span data-out="days" data-fmt="dec1">0.0</span></div><div class="sub">365 / turns</div></div>
</div>
<ul class="lines">
<li><span>Cost of goods sold per day</span><span data-out="perDay">$0</span></li>
<li><span>Cost of goods sold per month</span><span data-out="perMonth">$0</span></li>
<li><span>This product: days of stock</span><span data-out="pDays" data-fmt="dec1">0.0</span></li>
<li><span>This product: turns a year</span><span data-out="pTurns" data-fmt="dec1">0.0</span></li>
<li class="total"><span>This product</span><span data-out="statusText" data-fmt="text">-</span></li>
</ul>
<div class="callout warn" data-show-if="noStock > 0">Type your stock value at cost above zero to see your turns.</div>
<div class="callout warn" data-show-if="noCogs > 0">Type your cost of goods sold for the last 12 months to see your turns.</div>
<div class="callout warn" data-show-if="overstock > 0">This product has <b data-out="pDays" data-fmt="dec1">0.0</b> days of stock, at or over your <b data-out="over" data-fmt="int">0</b>-day line. Stop reordering it until it sells down.</div>
<div class="callout" data-show-if="okP > 0">This product has <b data-out="pDays" data-fmt="dec1">0.0</b> days of stock, under your <b data-out="over" data-fmt="int">0</b>-day overstock line.</div>
<div class="callout warn" data-show-if="noSales > 0">Type units sold per day above zero to check a product. With no sales, its stock is not turning at all.</div>
<div class="callout warn" data-show-if="soldOut > 0">No units on hand: this product is sold out. Check its reorder point.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Turns <b data-out="turns" data-fmt="dec1">0.0</b></span><span>Days <b data-out="days" data-fmt="dec1">0.0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.inventoryTurnover in assets/pnf-calc.js, the 1 Your Shop turnover rows and 2 SKU List of engines/cash-aware-reorder-planner (#6). */
var M=PNF.inventoryTurnover;
PNF.wire(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def str_breakeven_page(p):
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>What the place costs</legend>
{field("fixed", "Fixed costs per month", d["fixed"], "Mortgage or rent, utilities, internet, insurance, software: what you pay booked or not", pre="$")}
</fieldset>
<fieldset><legend>What a booking pays</legend>
{field("rate", "Nightly rate", d["rate"], "What the guest is charged per night before fees", pre="$")}
{field("fee", "Platform fee you pay", d["fee"], "Airbnb's single host fee: 15.5% for most hosts", suf="%")}
{field("stay", "Average stay", d["stay"], "Nights per booking")}
{field("cleanKept", "Cleaning fee you keep", d["cleanKept"], "Per stay, after your cleaner and any platform cut. 0 if it all goes to cleaning", pre="$")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Break-even nights</div><div class="val"><span data-out="nights" data-fmt="int">0</span> nights</div><div class="sub">a month, <span data-pct="occupancy">0%</span> of an average month</div></div>
<div class="tile"><div class="lab">Each booked night pays</div><div class="val" data-out="perNight">$0</div><div class="sub">after the platform fee</div></div>
</div>
<ul class="lines">
<li><span>Nightly rate after the platform fee</span><span data-out="rateNet">$0</span></li>
<li><span>Cleaning fee kept, per night</span><span data-out="cleanPerNight">$0</span></li>
<li><span>Each booked night pays</span><span data-out="perNight">$0</span></li>
<li><span>Exact nights to cover fixed costs</span><span data-out="exact" data-fmt="dec1">0.0</span></li>
<li class="total"><span>Rate to break even at half the month booked</span><span data-out="rateAtHalf">$0</span></li>
</ul>
<div class="callout" data-show-if="ok > 0">Book <b data-out="nights" data-fmt="int">0</b> nights a month, about <b data-out="stays" data-fmt="dec1">0.0</b> stays, and the place pays for itself. Every night after that adds to what you keep, before taxes, repairs and your time.</div>
<div class="callout warn" data-show-if="over > 0">That is more nights than a month has. At this rate the place can't cover its fixed costs; the rate for half the month booked is shown above.</div>
<div class="callout warn" data-show-if="never > 0">Each booked night pays nothing after fees, so no number of nights covers the costs. Check the nightly rate and fee.</div>
<div class="callout warn" data-show-if="noCosts > 0">Type your fixed costs per month to see the break-even nights.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Break even <b data-out="nights" data-fmt="int">0</b> nights</span><span>Per night <b data-out="perNight">$0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.strBreakEven in assets/pnf-calc.js; the platform fee comes off the nightly rate as in engines/str-nightly-pricing (#9). */
function M(i){var r=PNF.strBreakEven(i);r.rateNet=PNF.num(i.rate)-r.feePerNight;return r;}
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def rental_cash_flow_page(p):
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>The period</legend>
{field("months", "Months these figures cover", d["months"], "12 for a full year; fewer for the year so far")}
</fieldset>
<fieldset><legend>Money in</legend>
{field("income", "Rent and other rental income", d["income"], "Rent collected plus late fees and pet rent. Leave out security deposits you plan to return", pre="$")}
</fieldset>
<fieldset><legend>Money out</legend>
{field("expenses", "Operating expenses", d["expenses"], "Property tax, insurance, repairs, utilities you pay, management, supplies, travel", pre="$")}
{field("interest", "Mortgage interest", d["interest"], "The interest part of your payments, from the lender's statements", pre="$")}
{field("principal", "Mortgage principal", d["principal"], "The part of each payment that pays down the loan", pre="$")}
{field("improve", "Capital improvements", d["improve"], "Upgrades like a new roof or water heater, not repairs", pre="$")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Cash flow (what you kept)</div><div class="val" data-out="cash">$0</div><div class="sub"><span data-out="cashMonth">$0</span> a month on average</div></div>
<div class="tile"><div class="lab">Profit before depreciation</div><div class="val" data-out="profit">$0</div><div class="sub">money in less expenses and interest</div></div>
</div>
<ul class="lines">
<li><span>Rent and other rental income</span><span data-out="income">$0</span></li>
<li><span>Less operating expenses</span><span data-out="expenses">$0</span></li>
<li><span>Less mortgage interest</span><span data-out="interest">$0</span></li>
<li><span>Profit before depreciation</span><span data-out="profit">$0</span></li>
<li><span>Less mortgage principal</span><span data-out="principal">$0</span></li>
<li><span>Less capital improvements</span><span data-out="improve">$0</span></li>
<li class="total"><span>Cash flow (what you kept)</span><span data-out="cash">$0</span></li>
<li><span>Kept from each dollar of rent</span><span data-pct="keptShare">0%</span></li>
</ul>
<div class="callout" data-show-if="pos > 0">You kept <b data-out="cash">$0</b> after every payment, about <b data-out="cashMonth">$0</b> a month.</div>
<div class="callout warn" data-show-if="gap > 0">The property shows a profit of <b data-out="profit">$0</b>, but principal and improvements took more than that, so cash went down by <b data-out="down">$0</b>.</div>
<div class="callout warn" data-show-if="neg > 0">Money out was more than money in: cash went down by <b data-out="down">$0</b> over the period.</div>
<div class="callout warn" data-show-if="noMonths > 0">Type how many months these figures cover to see the monthly average.</div>
<div class="callout warn" data-show-if="noIncome > 0">Type the rent you collected to see your cash flow.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Cash flow <b data-out="cash">$0</b></span><span>A month <b data-out="cashMonth">$0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.rentalCashFlow in assets/pnf-calc.js, the 4 Property P&L rows of engines/rental-property (#19). */
var M=PNF.rentalCashFlow;
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def business_expense_page(p):
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>The period</legend>
{field("months", "Months these figures cover", d["months"], "1 for a month, 3 for a quarter, 12 for a year")}
</fieldset>
<fieldset><legend>Money in</legend>
{field("sales", "Sales and services", d["sales"], "What customers paid you, before fees", pre="$")}
{field("otherIncome", "Other business income", d["otherIncome"], "Business income that is not a sale", pre="$")}
{field("refunds", "Refunds given to customers", d["refunds"], "Money you paid back. It comes off income", pre="$")}
</fieldset>
<fieldset><legend>Stock you sell</legend>
{field("inventory", "Inventory and materials for resale", d["inventory"], "Stock and materials that become what you sell", pre="$")}
</fieldset>
<fieldset><legend>Business expenses</legend>
{field("fees", "Commissions and selling fees", d["fees"], "Marketplace and payment fees on your sales", pre="$")}
{field("rent", "Rent or lease", d["rent"], "Studio, booth, storage, leased equipment", pre="$")}
{field("supplies", "Supplies", d["supplies"], "Used up in the business, not part of what you sell", pre="$")}
{field("ads", "Advertising", d["ads"], "Ads, promoted listings, flyers", pre="$")}
{field("car", "Car and truck expenses", d["car"], "Business driving costs, parking, tolls", pre="$")}
{field("otherExp", "Other expenses", d["otherExp"], "Software, subscriptions, bank fees, shipping labels", pre="$")}
{field("more", "Everything else", d["more"], "Insurance, accountant, licenses, utilities, travel, the full bill for business meals", pre="$")}
</fieldset>
<fieldset><legend>Logged, but not in profit</legend>
{field("equipment", "Equipment over a few hundred dollars", d["equipment"], "Your preparer decides on depreciation", pre="$")}
{field("draw", "Owner draw or personal", d["draw"], "Money you paid yourself", pre="$")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Business expenses</div><div class="val" data-out="expenses">$0</div><div class="sub"><span data-out="expMonth">$0</span> a month on average</div></div>
<div class="tile"><div class="lab">Profit before inventory count</div><div class="val" data-out="profit">$0</div><div class="sub"><span data-out="profitMonth">$0</span> a month</div></div>
</div>
<ul class="lines">
<li><span>Income after refunds</span><span data-out="income">$0</span></li>
<li><span>Less inventory and materials</span><span data-out="inventory">$0</span></li>
<li><span>Less business expenses</span><span data-out="expenses">$0</span></li>
<li class="total"><span>Profit before inventory count</span><span data-out="profit">$0</span></li>
<li><span>Expenses per dollar of income</span><span data-pct="expShare">0%</span></li>
<li><span>Logged but kept out of profit</span><span data-out="offProfit">$0</span></li>
</ul>
<div class="callout" data-show-if="pos > 0">After stock and expenses you kept <b data-out="profit">$0</b> of <b data-out="income">$0</b>, before your preparer adjusts for inventory still on hand.</div>
<div class="callout warn" data-show-if="neg > 0">Stock and expenses were more than income: a loss of <b data-out="loss">$0</b> for the period. One big stock order or a rent month can do this; look at a longer period too.</div>
<div class="callout" data-show-if="hasOff > 0">Equipment and owner draws (<b data-out="offProfit">$0</b>) are logged for your records but not counted as expenses here.</div>
<div class="callout warn" data-show-if="noMonths > 0">Type how many months these figures cover to see the monthly averages.</div>
<div class="callout warn" data-show-if="noIncome > 0">Type your sales to see your profit.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Expenses <b data-out="expenses">$0</b></span><span>Profit <b data-out="profit">$0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.businessExpense in assets/pnf-calc.js, the Summary tab of engines/business-expense-tracker (#18). */
var M=PNF.businessExpense;
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def se_tax_page(p):
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>Your self-employment year</legend>
{field("net", "Net profit from self-employment", d["net"], "Income from clients and sales less business expenses (Schedule C line 31)", pre="$")}
{field("wages", "W-2 wages from a job, if any", d["wages"], "Box 3 of your W-2s. They use up part of the Social Security limit", pre="$")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Self-employment tax</div><div class="val" data-out="se">$0</div><div class="sub"><span data-pct="share">0%</span> of your net profit</div></div>
<div class="tile"><div class="lab">A quarter of it</div><div class="val" data-out="quarter">$0</div><div class="sub">to set aside for each estimated payment</div></div>
</div>
<ul class="lines">
<li><span>Net profit</span><span data-out="net">$0</span></li>
<li><span>Net earnings (92.35% of profit)</span><span data-out="earnings">$0</span></li>
<li><span>Social Security part, 12.4%</span><span data-out="ssPart">$0</span></li>
<li><span>Medicare part, 2.9%</span><span data-out="medPart">$0</span></li>
<li class="total"><span>Self-employment tax</span><span data-out="se">$0</span></li>
<li><span>Half you can deduct from income</span><span data-out="half">$0</span></li>
<li><span>About a month</span><span data-out="month">$0</span></li>
</ul>
<div class="callout" data-show-if="pos > 0">Self-employment tax of <b data-out="se">$0</b> comes before any income tax. Setting aside <b data-out="month">$0</b> a month covers it.</div>
<div class="callout" data-show-if="capped > 0">Part of your earnings is above the 2026 Social Security limit of $184,500 (less your W-2 wages), so only the 2.9% Medicare part applies to that part. For 2027 earnings the limit is $192,300.</div>
<div class="callout warn" data-show-if="under > 0">Net earnings under $400 (92.35% of profit): no self-employment tax is due for the year.</div>
<div class="callout warn" data-show-if="noNet > 0">Type your net profit to see your self-employment tax. A loss means none is due.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>SE tax <b data-out="se">$0</b></span><span>A quarter <b data-out="quarter">$0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.seTax in assets/pnf-calc.js, Schedule SE with the 2026 Social Security wage base. */
var M=PNF.seTax;
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def profit_margin_page(p):
    d, f = p["defaults"], p["fees"]
    ads = "".join(f'<option value="{v}"{" selected" if v == d["adsRate"] else ""}>{E(t)}</option>' for v, t in p["ads_options"])
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>The margin you want</legend>
{field("target", "Target profit margin", d["target"], "Profit as a share of item price plus shipping", suf="%")}
</fieldset>
<fieldset><legend>Your costs for one item</legend>
{field("materials", "Materials", d["materials"], "What goes into one item", pre="$")}
{field("labor", "Labor", d["labor"], "What you pay yourself per item", pre="$")}
{field("packaging", "Packaging", d["packaging"], "Box, mailer, tissue, tape, insert card", pre="$")}
{field("label", "Shipping label", d["label"], "What postage really costs you", pre="$")}
{field("ship", "Shipping you charge the buyer", d["ship"], "0 for free shipping", pre="$")}
</fieldset>
<fieldset><legend>Offsite Ads</legend>
<div class="row pick"><label for="adsRate">Your Offsite Ads rate<small>Used only for the ad-sale price. Etsy charges it on orders it attributes to its ads.</small></label>
<div class="field"><select id="adsRate" data-in="adsRate">{ads}</select></div></div>
</fieldset>
<fieldset><legend>Etsy's US fees</legend>
{field("tfRate", "Transaction fee", f["tfRate"], "On item price plus shipping", suf="%")}
{field("procRate", "Payment processing, percent", f["procRate"], "On the total the buyer paid", suf="%")}
{field("procFixed", "Payment processing, per order", f["procFixed"], "Outside the US? Type your rates", pre="$")}
{field("listFee", "Listing fee", f["listFee"], "One per sale, when a listing renews after it sells", pre="$")}
</fieldset></form>"""
    results = f"""<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">List price for your margin</div><div class="val"><span data-out="price" data-never="No price works" data-never-if="none">$0</span></div><div class="sub">Plus the shipping you charge</div></div>
<div class="tile"><div class="lab">Profit per sale</div><div class="val" data-out="profit">$0</div><div class="sub">After Etsy fees and your costs</div></div>
</div>
<ul class="lines">
<li><span>Item price plus shipping</span><span data-out="revenue">$0</span></li>
<li><span>Etsy fees, no Offsite Ads</span><span data-out="fees">$0</span></li>
<li><span>Materials, labor, packaging</span><span data-out="costs">$0</span></li>
<li><span>Shipping label</span><span data-out="label">$0</span></li>
<li class="total"><span>Profit</span><span data-out="profit">$0</span></li>
<li><span>List price if the sale is an Offsite Ads order</span><span data-out="adPrice" data-never="None" data-never-if="adBlank">$0</span></li>
<li><span>Extra price an ad sale needs</span><span data-out="adGap">$0</span></li>
</ul>
<div class="callout" data-show-if="show > 0">Round up, never down: <b data-out="price">$0</b> becomes <b data-out="roundHalf">$0</b> or <b data-out="roundOne" data-fmt="money0">$0</b>.</div>
<div class="callout warn" data-show-if="none > 0">No price reaches this margin: Etsy's fee rates and your margin take all of it. Lower the margin or the costs.</div>
<div class="callout warn" data-show-if="adNone > 0">An Offsite Ads sale cannot reach this margin at any price.</div>
<div class="callout warn" data-show-if="neg > 0">The shipping you charge already covers this margin. Check your shipping and costs.</div>
{asof_note(p)}
</div></div>
<div class="mbar" aria-hidden="true"><span>Price <b data-out="price">$0</b></span><span>Profit <b data-out="profit">$0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.profitMargin in assets/pnf-calc.js, 3 Pricing "Your price for that margin" of engines/etsy-true-profit (#5). */
var M=PNF.profitMargin;
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def employer_cost_page(p):
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>The job</legend>
{field("wage", "Hourly wage", d["wage"], "What you will pay per hour, before anything is taken out", pre="$")}
{field("hours", "Hours a week", d["hours"], "Average paid hours in a week")}
{field("weeks", "Weeks a year", d["weeks"], "52 for a year-round employee")}
</fieldset>
<fieldset><legend>Your state and insurance</legend>
{field("sutaRate", "State unemployment rate", d["sutaRate"], "Your new-employer rate from your state's letter. The default is the guide's Ohio example", suf="%")}
{field("sutaBase", "State unemployment wage base", d["sutaBase"], "Wages per employee per year the rate applies to", pre="$")}
{field("compRate", "Workers' comp per $100 of wages", d["compRate"], "From your quote. Physical work costs several dollars, office work under $1", pre="$")}
{field("futaRate", "FUTA rate after the state credit", d["futaRate"], "0.6% in most states, on the first $7,000", suf="%")}
</fieldset>
<fieldset><legend>Extras, if any</legend>
{field("software", "Payroll software per employee per year", d["software"], "Your provider's fees divided by your employees", pre="$")}
{field("benefit", "Benefit allowance per month", d["benefit"], "For example a health reimbursement allowance. 0 if none", pre="$")}
</fieldset></form>"""
    results = f"""<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">True hourly cost</div><div class="val" data-out="trueHourly">$0</div><div class="sub"><span data-pct="over">0%</span> on top of the wage, before extras</div></div>
<div class="tile"><div class="lab">All in, with extras</div><div class="val" data-out="allIn">$0</div><div class="sub">per hour worked</div></div>
</div>
<ul class="lines">
<li><span>Wages a year</span><span data-out="pay">$0</span></li>
<li><span>Social Security and Medicare match, 7.65%</span><span data-out="fica">$0</span></li>
<li><span>FUTA (federal unemployment)</span><span data-out="futa">$0</span></li>
<li><span>State unemployment</span><span data-out="suta">$0</span></li>
<li><span>Workers' comp</span><span data-out="comp">$0</span></li>
<li class="total"><span>Taxes and insurance on top of wages</span><span data-out="taxes">$0</span></li>
<li><span>Payroll software and benefit</span><span data-out="extras">$0</span></li>
<li class="total"><span>Total cost a year</span><span data-out="totalYear">$0</span></li>
<li><span>Hours a year</span><span data-out="hoursYear" data-fmt="int">0</span></li>
</ul>
<div class="callout" data-show-if="pos > 0">At <b data-out="wage">$0</b> an hour the employee costs you <b data-out="trueHourly">$0</b> an hour in pay, taxes and insurance. FUTA is used up in the first <b data-out="futaWeeks" data-fmt="int">0</b> weeks of the year, so those weeks cost more.</div>
<div class="callout warn" data-show-if="none > 0">Type an hourly wage, hours a week and weeks a year to see the cost.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>True cost <b data-out="trueHourly">$0</b></span><span>All in <b data-out="allIn">$0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.employerCost in assets/pnf-calc.js, Section 6 true hourly cost of kdp/8 (#8 First-Time Employer guide). */
var M=function(v){var r=PNF.employerCost(v);r.wage=PNF.num(v.wage);return r;};
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def startup_cost_page(p):
    d, lines = p["defaults"], p["lines"]
    one = "".join(field(f"s{i + 1}", lab, d[f"s{i + 1}"], hint, pre="$") for i, (lab, hint) in enumerate(lines))
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>One-time spend before the first job</legend>
{one}
</fieldset>
<fieldset><legend>Cash cushion</legend>
{field("monthly", "Business costs per month", d["monthly"], p["monthly_hint"], pre="$")}
{field("months", "Months of costs to keep on hand", d["months"], "Whole months, your choice. The example uses " + d["months"])}
</fieldset>
<fieldset><legend>Earning it back</legend>
{field("profitJob", p["profit_label"], d["profitJob"], p["profit_hint"], pre="$")}
{field("jobsWeek", p["pace_label"], d["jobsWeek"], "Leave 0 if you are not sure yet")}
</fieldset></form>"""
    results = f"""<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Cash to start</div><div class="val" data-out="cash" data-fmt="money0">$0</div><div class="sub">One-time spend plus the cushion</div></div>
<div class="tile"><div class="lab">{E(p["jobs_tile"])}</div><div class="val"><span data-out="jobs" data-fmt="int" data-never="No profit to pay it" data-never-if="noProfit">0</span></div><div class="sub">To earn back the one-time spend</div></div>
</div>
<ul class="lines">
<li><span>One-time spend</span><span data-out="oneTime" data-fmt="money0">$0</span></li>
<li><span>Cushion: <span data-out="months" data-fmt="int">0</span> months of <span data-out="monthly" data-fmt="money0">$0</span></span><span data-out="cushion" data-fmt="money0">$0</span></li>
<li class="total"><span>Cash to start</span><span data-out="cash" data-fmt="money0">$0</span></li>
<li><span>{E(p["profit_label"])}</span><span data-out="profit">$0</span></li>
<li><span>{E(p["jobs_tile"])}</span><span data-out="jobs" data-fmt="int">0</span></li>
<li><span>Weeks at your pace</span><span data-out="weeks" data-fmt="int">0</span></li>
</ul>
<div class="callout" data-show-if="pace > 0">At your pace the one-time spend is paid back in about <b data-out="weeks" data-fmt="int">0</b> weeks of work, after you have paid yourself, your monthly costs and the tax on your pay.</div>
<div class="callout warn" data-show-if="noProfit > 0">Type the profit in one job. If your quote has no profit above your break-even, nothing pays the startup spend back. Check your prices first.</div>
<div class="callout warn" data-show-if="none > 0">Type what you will spend before the first job to see the cash you need.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Cash to start <b data-out="cash" data-fmt="money0">$0</b></span><span>To earn back <b data-out="jobs" data-fmt="int">0</b></span></div>"""
    script = f"""<script>
(function(){{var f=document.getElementById("calc");
/* Maths: PNF.startupCost in assets/pnf-calc.js; monthly costs and profit per job from {p["engine_ref"]}. */
var M=PNF.startupCost;
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;}})();</script>"""
    return form, results, script


def budget_page(p):
    d = p["defaults"]
    freqs = [("weekly", "Weekly"), ("biweekly", "Every 2 weeks"), ("twice", "Twice a month"), ("monthly", "Monthly"),
             ("quarterly", "Every 3 months"), ("yearly", "Yearly")]

    def pick(key, label, hint):
        opts = "".join(f'<option value="{v}"{" selected" if v == d[key] else ""}>{E(t)}</option>' for v, t in freqs)
        return (f'<div class="row pick"><label for="{key}">{E(label)}<small>{E(hint)}</small></label>'
                f'<div class="field"><select id="{key}" data-in="{key}">{opts}</select></div></div>')
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>Take-home pay</legend>
{field("pay1", "Paycheck 1", d["pay1"], "After tax and deductions, the amount that lands in the bank", pre="$")}
{pick("freq1", "How often paycheck 1 comes", "Every 2 weeks is 26 paychecks a year, not 24")}
{field("pay2", "Paycheck 2", d["pay2"], "A second job or a partner's pay. 0 if none", pre="$")}
{pick("freq2", "How often paycheck 2 comes", "Pick how it is paid; the calculator turns it into a month")}
{field("other", "Other income per month", d["other"], "Side income, child support or benefits. 0 if none", pre="$")}
</fieldset>
<fieldset><legend>Where it goes each month</legend>
{field("bills", "Bills", d["bills"], "Rent or mortgage, car payment, insurance, utilities, phone, internet, loans", pre="$")}
{field("spend", "Everyday spending", d["spend"], "Groceries, gas, eating out, household, kids, pets, fun", pre="$")}
{field("yearly", "Yearly costs, the full amount", d["yearly"], "Registration, memberships, gifts paid once a year. Spread over 12 months", pre="$")}
{field("save", "Savings and extra debt payments", d["save"], "Emergency fund, retirement, sinking funds, extra on a loan", pre="$")}
</fieldset></form>"""
    results = f"""<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Left to plan each month</div><div class="val" data-out="left">$0</div><div class="sub"><span data-pct="leftShare">0%</span> of take-home with no job yet</div></div>
<div class="tile"><div class="lab">Take-home per month</div><div class="val" data-out="income">$0</div><div class="sub">Every paycheck turned into a month</div></div>
</div>
<ul class="lines">
<li><span>Paycheck 1 per month</span><span data-out="pay1">$0</span></li>
<li><span>Paycheck 2 per month</span><span data-out="pay2">$0</span></li>
<li><span>Other income</span><span data-out="other">$0</span></li>
<li class="total"><span>Take-home income</span><span data-out="income">$0</span></li>
<li><span>Bills, <span data-pct="billsShare">0%</span></span><span data-out="bills">$0</span></li>
<li><span>Everyday spending with yearly costs, <span data-pct="everydayShare">0%</span></span><span data-out="everyday">$0</span></li>
<li><span>Savings and extra debt, <span data-pct="saveShare">0%</span></span><span data-out="save">$0</span></li>
<li class="total"><span>Planned out each month</span><span data-out="out">$0</span></li>
<li class="total"><span>Left to plan</span><span data-out="left">$0</span></li>
</ul>
<div class="callout" data-show-if="pos > 0">Give the <b data-out="left">$0</b> left over a job: more savings, an extra debt payment or a line you forgot. A plan with $0 left to plan spends every dollar on purpose.</div>
<div class="callout warn" data-show-if="neg > 0">This plan spends <b data-out="over">$0</b> a month more than comes in. Trim a line or add income until Left to plan is 0 or more.</div>
<div class="callout warn" data-show-if="none > 0">Type your take-home pay and how often it comes to see your month.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Left to plan <b data-out="left">$0</b></span><span>Income <b data-out="income">$0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.budgetPlan in assets/pnf-calc.js, 1 Setup "Your month at a glance" of engines/budget-planner (#29). */
var M=PNF.budgetPlan;
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def profit_loss_page(p):
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>Money in, for the period</legend>
{field("sales", "Sales and services", d["sales"], "Everything customers paid you, before fees", pre="$")}
{field("other", "Other business income", d["other"], "Fee refunds, rebates and other business income that is not a sale. 0 if none", pre="$")}
{field("refunds", "Refunds given to customers", d["refunds"], "Type it as a positive number; it subtracts", pre="$")}
</fieldset>
<fieldset><legend>Cost of goods sold</legend>
{field("goods", "Stock, materials and product labor bought", d["goods"], "Blanks or stock for resale, materials that go into what you sell, people paid to make it", pre="$")}
{field("stock0", "Stock on hand at the start", d["stock0"], "Optional. What unsold stock cost you at the start of the period", pre="$")}
{field("stock1", "Stock on hand at the end", d["stock1"], "Optional. Fill in both counts or leave both blank", pre="$")}
</fieldset>
<fieldset><legend>Operating expenses</legend>
{field("expenses", "Total operating expenses", d["expenses"], "Fees, ads, rent, insurance, software, shipping labels, supplies. Leave out equipment, owner pay and transfers", pre="$")}
</fieldset></form>"""
    results = f"""<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Net profit</div><div class="val" data-out="net">$0</div><div class="sub">Net margin <span data-pct="netMargin">0%</span> of net revenue</div></div>
<div class="tile"><div class="lab">Gross profit</div><div class="val" data-out="gross">$0</div><div class="sub">Gross margin <span data-pct="grossMargin">0%</span></div></div>
</div>
<ul class="lines">
<li class="total"><span>Net revenue</span><span data-out="revenue">$0</span></li>
<li><span>Stock, materials and labor bought</span><span data-out="goods">$0</span></li>
<li><span>Change in stock on hand</span><span data-out="stockChange">$0</span></li>
<li class="total"><span>Cost of goods sold</span><span data-out="cogs">$0</span></li>
<li class="total"><span>Gross profit</span><span data-out="gross">$0</span></li>
<li><span>Operating expenses</span><span data-out="expenses">$0</span></li>
<li class="total"><span>Net profit</span><span data-out="net">$0</span></li>
</ul>
<div class="callout" data-show-if="pos > 0">The business kept <b data-out="net">$0</b> after the cost of goods and expenses: <b data-pct="netMargin">0%</b> of every dollar of net revenue.</div>
<div class="callout warn" data-show-if="neg > 0">This period shows a loss of <b data-out="loss">$0</b>. Costs and expenses were more than net revenue.</div>
<div class="callout warn" data-show-if="noRev > 0">Type your sales for the period to see margins.</div>
<div class="callout warn" data-show-if="none > 0">Type your sales, costs and expenses for one month or the year to date.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Net profit <b data-out="net">$0</b></span><span>Revenue <b data-out="revenue">$0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.profitLoss in assets/pnf-calc.js, 2 Statement of engines/profit-and-loss (#28). */
var M=PNF.profitLoss;
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


CAKE_SIZE_ORDER = ["6 in round", "8 in round", "9 in round", "10 in round", "12 in round", "14 in round", "16 in round",
                   "6 in square", "8 in square", "10 in square", "12 in square", "14 in square", "16 in square",
                   "7 x 11 in sheet", "9 x 13 in sheet", "11 x 15 in sheet", "12 x 18 in sheet",
                   "6 in heart", "8 in heart", "9 in heart", "10 in heart", "12 in heart", "14 in heart", "16 in heart"]


def cake_page(p):
    d = p["defaults"]

    def pick(key, label, hint, opts, cur):
        o = "".join(f'<option value="{E(v)}"{" selected" if v == cur else ""}>{E(t)}</option>' for v, t in opts)
        return (f'<div class="row pick"><label for="{key}">{E(label)}<small>{E(hint)}</small></label>'
                f'<div class="field"><select id="{key}" data-in="{key}">{o}</select></div></div>')
    sizes = [("", "None")] + [(z, z) for z in CAKE_SIZE_ORDER]
    tiers = "".join(pick(f"t{n}", f"Tier {n}", "Biggest tier first" if n == 1 else "None if the cake has fewer tiers", sizes, d[f"t{n}"])
                    for n in range(1, 5))
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>The cake</legend>
{pick("style", "Serving style", "Wedding slices are about 1 x 2 in, party slices about 1.5 x 2 in", [("wedding", "Wedding"), ("party", "Party")], d["style"])}
{tiers}
{field("pps", "Your price per serving", d["pps"], "What you charge per slice for this finish, for example buttercream or fondant", pre="$")}
{field("minCake", "Minimum cake price", d["minCake"], "Small cakes price up to this. 0 for no minimum", pre="$")}
{field("extras", "Extras, total", d["extras"], "Sugar flowers, toppers, box and board, setup", pre="$")}
</fieldset>
<fieldset><legend>Delivery, rush, tax and deposit</legend>
{pick("method", "Pickup or delivery", "Delivery adds the base fee plus the miles", [("delivery", "Delivery"), ("pickup", "Pickup")], d["method"])}
{field("miles", "Delivery miles, one way", d["miles"], "", suf="mi")}
{field("delivBase", "Delivery base fee", d["delivBase"], "Charged on every delivery before mileage", pre="$")}
{field("perMile", "Delivery per mile", d["perMile"], "", pre="$")}
{field("days", "Days from order to event", d["days"], "Leave blank to skip the rush check")}
{field("rushDays", "Rush when fewer days than", d["rushDays"], "0 turns rush fees off")}
{field("rushPct", "Rush fee, % of cake and extras", d["rushPct"], "", suf="%")}
{field("taxRate", "Sales tax rate, if you charge it", d["taxRate"], "Check your own state and local rules", suf="%")}
{field("depositPct", "Deposit to book", d["depositPct"], "The share of the total that holds the date", suf="%")}
</fieldset></form>"""
    results = f"""<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Quote total</div><div class="val" data-out="total">$0</div><div class="sub"><span data-out="servings" data-fmt="int">0</span> servings</div></div>
<div class="tile"><div class="lab">Deposit to book</div><div class="val" data-out="deposit">$0</div><div class="sub">Balance <span data-out="balance">$0</span> at the event</div></div>
</div>
<ul class="lines">
<li><span>Servings from the tiers</span><span data-out="servings" data-fmt="int">0</span></li>
<li class="total"><span>Cake price</span><span data-out="cake">$0</span></li>
<li><span>Extras</span><span data-out="extras">$0</span></li>
<li><span>Delivery</span><span data-out="delivery">$0</span></li>
<li><span>Rush fee</span><span data-out="rush">$0</span></li>
<li class="total"><span>Subtotal</span><span data-out="sub">$0</span></li>
<li><span>Sales tax</span><span data-out="tax">$0</span></li>
<li class="total"><span>Total</span><span data-out="total">$0</span></li>
<li><span>Deposit to book</span><span data-out="deposit">$0</span></li>
<li><span>Balance due at the event</span><span data-out="balance">$0</span></li>
</ul>
<div class="callout" data-show-if="minUsed > 0">The servings at your price come to <b data-out="base">$0</b>, so the cake is priced up to your minimum cake price.</div>
<div class="callout warn" data-show-if="rushOn > 0">Rush fee applied: the event is inside your rush window.</div>
<div class="callout warn" data-show-if="none > 0">Pick at least one tier size to see the quote.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Total <b data-out="total">$0</b></span><span>Deposit <b data-out="deposit">$0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.cakeQuote in assets/pnf-calc.js, 2 Order Form "How it's built" of engines/cake-order-form (#26). */
var M=PNF.cakeQuote;
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def unit_cost_page(p):
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>What one unit costs you</legend>
{field("materials", "Materials per unit", d["materials"], "Everything that goes into one unit, for example wax, wick and jar", pre="$")}
{field("labor", "Labor per unit", d["labor"], "What making one unit costs in time, yours or a helper's. 0 to leave it out", pre="$")}
{field("packaging", "Packaging and other per unit", d["packaging"], "Label, box, tissue, insert card", pre="$")}
</fieldset>
<fieldset><legend>What it sells for</legend>
{field("price", "Selling price", d["price"], "What the buyer pays for one unit", pre="$")}
{field("feePct", "Selling and payment fees", d["feePct"], "Your fees as a share of the price. 0 if none", suf="%")}
{field("onHand", "Units on hand", d["onHand"], "Optional. Gives the money tied up in this item")}
</fieldset></form>"""
    results = f"""<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Profit per unit</div><div class="val" data-out="ppu">$0</div><div class="sub">Margin <span data-pct="margin">0%</span> of the price</div></div>
<div class="tile"><div class="lab">Unit cost</div><div class="val" data-out="uc">$0</div><div class="sub">Materials, labor and packaging</div></div>
</div>
<ul class="lines">
<li><span>Selling price</span><span data-out="price">$0</span></li>
<li><span>Unit cost</span><span data-out="uc">$0</span></li>
<li><span>Fees</span><span data-out="fees">$0</span></li>
<li class="total"><span>Profit per unit</span><span data-out="ppu">$0</span></li>
<li><span>Stock value at cost (<span data-out="onHand" data-fmt="int">0</span> units)</span><span data-out="stockValue">$0</span></li>
</ul>
<div class="callout" data-show-if="pos > 0">Each sale keeps <b data-out="ppu">$0</b> after the unit cost and fees: <b data-pct="margin">0%</b> of the price.</div>
<div class="callout warn" data-show-if="neg > 0">At this price each sale loses <b data-out="loss">$0</b> or breaks even. The unit cost and fees take the whole price.</div>
<div class="callout warn" data-show-if="noPrice > 0">Type the selling price to see the profit per unit.</div>
<div class="callout warn" data-show-if="none > 0">Type what one unit costs you and what it sells for.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Profit <b data-out="ppu">$0</b></span><span>Unit cost <b data-out="uc">$0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.unitCost in assets/pnf-calc.js, 1 Items of engines/inventory-tracker (#25). */
var M=function(i){var r=PNF.unitCost(i);r.price=Math.max(0,PNF.num(i.price));return r;};
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def chore_split_page(p):
    d = p["defaults"]
    rows = ""
    for k, n in (("a", 1), ("b", 2), ("c", 3)):
        rows += field(k, f"Person {n}: minutes a week", d[k], "Leave blank if only two people share the home" if n == 3 else "Add up the chores this person does in a normal week")
        rows += field(k + "Share", f"Person {n}: share of the work", d[k + "Share"], "Optional, for example 60 and 40. Blank for an even split", suf="%")
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>Who does what now</legend>
{rows}
</fieldset></form>"""
    li = "".join(f"""<li class="total"{sh}><span>Person {n}, now</span><span><span data-out="{k}Hours" data-fmt="hrs">0</span> a week</span></li>
<li{sh}><span>Fair target</span><span><span data-out="{k}Target" data-fmt="dec1">0</span> min</span></li>
<li{sh}><span>Over (+) or under (-) target</span><span><span data-out="{k}Diff" data-fmt="dec1">0</span> min</span></li>"""
                 for k, n, sh in (("a", 1, ""), ("b", 2, ""), ("c", 3, ' data-show-if="cOn > 0"')))
    results = f"""<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Minutes to move each week</div><div class="val"><span data-out="move" data-fmt="dec1">0</span> min</div><div class="sub">From the person furthest over to the one furthest under</div></div>
<div class="tile"><div class="lab">Whole home</div><div class="val"><span data-out="total" data-fmt="int">0</span> min</div><div class="sub"><span data-out="hours" data-fmt="hrs">0</span> a week</div></div>
</div>
<ul class="lines">
{li}
</ul>
<div class="callout" data-show-if="even > 0">The split is within 15 minutes a week of fair. Nothing big to move.</div>
<div class="callout warn" data-show-if="uneven > 0">Move about <b data-out="move" data-fmt="dec1">0</b> minutes of chores a week from the person furthest over to the person furthest under.</div>
<div class="callout warn" data-show-if="mixed > 0">Type a share for everyone or leave them all blank. Using an even split for now.</div>
<div class="callout warn" data-show-if="none > 0">Type the weekly chore minutes for at least two people.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Move <b data-out="move" data-fmt="dec1">0</b> min</span><span>Total <b data-out="total" data-fmt="int">0</b> min</span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.choreSplit in assets/pnf-calc.js, Fair Split tab of engines/fair-share-chore-chart (#24). */
var M=PNF.choreSplit;
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def client_mix_page(p):
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>Revenue from done jobs, by client</legend>
{field("c1", "Your biggest client", d["c1"], "Paid or not, every finished job for that client", pre="$")}
{field("c2", "Second client", d["c2"], "Any order works. The calculator ranks them", pre="$")}
{field("c3", "Third client", d["c3"], "0 if you only have two", pre="$")}
{field("rest", "Everyone else, together", d["rest"], "All your other clients added up", pre="$")}
</fieldset>
<fieldset><legend>Money still out</legend>
{field("unpaid", "Unpaid on finished jobs", d["unpaid"], "Optional. Done but not paid yet", pre="$")}
{field("quotes", "Open quotes", d["quotes"], "Optional. Quoted, waiting on an answer", pre="$")}
</fieldset></form>"""
    results = f"""<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Top client share</div><div class="val" data-pct="topShare">0%</div><div class="sub">Of revenue from done jobs</div></div>
<div class="tile"><div class="lab">Top three clients</div><div class="val" data-pct="top3Share">0%</div><div class="sub">Of the same revenue</div></div>
</div>
<ul class="lines">
<li><span>Revenue, done jobs</span><span data-out="total">$0</span></li>
<li><span>Top client</span><span data-out="top">$0</span></li>
<li><span>Second client (<span data-pct="secondVsTop">0%</span> of the top)</span><span data-out="second">$0</span></li>
<li><span>Third client (<span data-pct="thirdVsTop">0%</span> of the top)</span><span data-out="third">$0</span></li>
<li class="total"><span>Revenue without the top client</span><span data-out="withoutTop">$0</span></li>
<li><span>Unpaid on done jobs (<span data-pct="unpaidShare">0%</span>)</span><span data-out="unpaid">$0</span></li>
<li><span>Collected</span><span data-out="collected">$0</span></li>
<li><span>Open quotes, not counted above</span><span data-out="quotes">$0</span></li>
</ul>
<div class="callout warn" data-show-if="big > 0">One client brings half or more of this revenue. If they stopped booking, revenue from these jobs would drop to <b data-out="withoutTop">$0</b>.</div>
<div class="callout" data-show-if="mid > 0">Your top client brings <b data-pct="topShare">0%</b> of this revenue. Without them it would be <b data-out="withoutTop">$0</b>.</div>
<div class="callout" data-show-if="spread > 0">No single client brings a quarter of this revenue. Losing the biggest one would leave <b data-out="withoutTop">$0</b>.</div>
<div class="callout warn" data-show-if="overUnpaid > 0">Unpaid is more than the revenue typed. Showing all of it as unpaid.</div>
<div class="callout warn" data-show-if="none > 0">Type the revenue from your biggest client and everyone else.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Top client <b data-pct="topShare">0%</b></span><span>Revenue <b data-out="total">$0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.clientMix in assets/pnf-calc.js, 1 Today of engines/client-tracker (#27). */
var M=PNF.clientMix;
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def service_sqft_page(p):
    """#22 per square foot view: the #13 engine's job quote divided by the job's area (PNF.serviceSqft)."""
    d = p["defaults"]
    presets = p["presets"]  # [label, sq ft, hours, people, supplies, miles]: only jobs the workbook sizes
    opts = "".join(f'<option value="{i}"{" selected" if i == 0 else ""}>{E(x[0])}</option>' for i, x in enumerate(presets))
    q0 = presets[0]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>The job</legend>
<div class="row pick"><label for="preset">Start from an example job<small>From the workbook's price sheet. Change any number.</small></label>
<div class="field"><select id="preset">{opts}</select></div></div>
{field("area", "Area to clean, in sq ft", q0[1], "Measure it: length times width")}
{field("jobHours", "Hours on site per person", q0[2], "How long a job this size takes you")}
{field("people", "People on the job", q0[3])}
{field("supplies", "Supplies for this job", q0[4], "Chemicals, sealer, stain", pre="$")}
{field("miles", "Round-trip miles", q0[5])}
{field("checkPerSqFt", "A per-sq-ft price to check", d["checkPerSqFt"], "What you charge now, or a price you saw quoted", pre="$")}
</fieldset>
<fieldset><legend>Your year</legend>
{field("takeHome", "Take-home pay you want", d["takeHome"], "What you keep after tax, per year", pre="$")}
{field("weeks", "Weeks you work per year", d["weeks"], "52 minus vacation and rain weeks")}
{field("hours", "Hours you work per week, all of it", d["hours"], "Driving, quoting and admin included")}
{field("paidShare", "Share of those hours customers pay for", d["paidShare"], "Not sure? Try 60 to 70", suf="%")}
</fieldset>
<fieldset><legend>Costs and taxes</legend>
{field("monthlyCosts", "Business costs per month", d["monthlyCosts"], p["costs_hint"], pre="$")}
{field("incomeTax", "Income tax rate, your estimate", d["incomeTax"], "Self-employment tax of 15.3% is added for you", suf="%")}
{field("margin", "Profit margin in quotes", d["margin"], "", suf="%")}
{field("perMile", "Vehicle cost per mile", d["perMile"], "IRS business rate: 76 cents (Jul to Dec 2026)", pre="$")}
{field("mph", "Average speed between jobs", d["mph"], "Miles per hour")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Your price per sq ft</div><div class="val" data-out="perSqFt">$0</div><div class="sub">For this job: <span data-out="quote" data-fmt="money0">$0</span></div></div>
<div class="tile"><div class="lab">Floor per sq ft</div><div class="val" data-out="floorPerSqFt">$0</div><div class="sub">Zero profit</div></div>
<div class="tile"><div class="lab">Sq ft per person-hour</div><div class="val" data-out="sqftPerHour" data-fmt="int">0</div><div class="sub">Your speed on this job</div></div>
<div class="tile"><div class="lab">Break-even per paid hour</div><div class="val" data-out="breakEven">$0</div></div>
</div>
<ul class="lines">
<li><span>Your time on site</span><span data-out="labor">$0</span></li>
<li><span>Drive time</span><span data-out="driveCost">$0</span></li>
<li><span>Vehicle</span><span data-out="vehicle">$0</span></li>
<li><span>Supplies</span><span data-out="supplies">$0</span></li>
<li class="total"><span>Price floor, zero profit</span><span data-out="floor">$0</span></li>
<li><span>At the per-sq-ft price you are checking</span><span data-out="checkPrice">$0</span></li>
</ul>
<div class="callout warn" data-show-if="checkShort > 0">That per-sq-ft price comes to <b data-out="checkPrice">$0</b> for this job, <b data-out="checkLoss">$0</b> under your floor.</div>
<div class="callout" data-show-if="checkOk > 0">That per-sq-ft price covers your floor on this job.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Per sq ft <b data-out="perSqFt">$0</b></span><span>Job <b data-out="quote" data-fmt="money0">$0</b></span></div>"""
    presets_js = json.dumps([x[1:] for x in presets])
    script = f"""<script>
(function(){{var f=document.getElementById("calc"),P={presets_js};
document.getElementById("preset").addEventListener("change",function(e){{var v=P[+e.target.value];
["area","jobHours","people","supplies","miles"].forEach(function(k,i){{document.getElementById(k).value=v[i];}});
f.dispatchEvent(new Event("input"));}});
PNF.wire(f,PNF.serviceSqft);}})();</script>"""
    return form, results, script


def day_rate_page(p):
    """#20 in days: the Hourly Rate Quick Calculator's Calculator tab with the week entered as days x hours (PNF.dayRate)."""
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>What you want to take home</legend>
{field("takeHome", "Take-home pay you want per year", d["takeHome"], "After tax", pre="$")}
{field("taxRate", "Tax set-aside rate", d["taxRate"], "Share of profit you set aside for tax", suf="%")}
{field("expenses", "Business expenses per year", d["expenses"], p["expenses_hint"], pre="$")}
</fieldset>
<fieldset><legend>Your working time</legend>
{field("weeks", "Weeks you work per year", d["weeks"], "52 minus holidays, sick days and time off")}
{field("daysPerWeek", "Days you work per week", d["daysPerWeek"])}
{field("hoursPerDay", "Hours in a working day", d["hoursPerDay"], "The length of a day you would bill as one day")}
{field("billableShare", "Share of your working time a client pays for", d["billableShare"], "Quoting, travel, admin and gaps between jobs are the rest", suf="%")}
</fieldset>
<fieldset><legend>Check a day rate you are considering</legend>
{field("checkDayRate", "Day rate to check", d["checkDayRate"], pre="$")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Your minimum day rate</div><div class="val" data-out="dayRate">$0</div><div class="sub">Per billed day</div></div>
<div class="tile"><div class="lab">Hourly equivalent</div><div class="val" data-out="rate">$0</div><div class="sub">Rate card: <span data-out="rateCard" data-fmt="money0">$0</span> an hour</div></div>
<div class="tile"><div class="lab">Billable days a year</div><div class="val" data-out="billableDays" data-fmt="dec1">0</div></div>
<div class="tile"><div class="lab">Days you work a year</div><div class="val" data-out="daysWorked" data-fmt="int">0</div></div>
</div>
<ul class="lines">
<li><span>Revenue you need</span><span data-out="revenue" data-fmt="money0">$0</span></li>
<li class="total"><span>At the day rate you are checking, you keep</span><span data-out="keep" data-fmt="money0">$0</span></li>
<li><span>Per day you actually work</span><span data-out="keepPerDay">$0</span></li>
</ul>
<div class="callout warn" data-show-if="shortBy > 0">That day rate leaves you <b data-out="shortBy" data-fmt="money0">$0</b> a year short of your goal.</div>
<div class="callout" data-show-if="shortBy < 0.01">That day rate meets your take-home goal.</div>
<details><summary>The day rate you need if you bill more of your time</summary><ul class="lines">
<li><span>50% of your time billed</span><span data-out="dayAt50">$0</span></li>
<li><span>60% of your time billed</span><span data-out="dayAt60">$0</span></li>
<li><span>70% of your time billed</span><span data-out="dayAt70">$0</span></li>
<li><span>80% of your time billed</span><span data-out="dayAt80">$0</span></li>
</ul></details>
</div></div>
<div class="mbar" aria-hidden="true"><span>Day rate <b data-out="dayRate">$0</b></span><span>Hourly <b data-out="rate">$0</b></span></div>"""
    script = '<script>PNF.wire(document.getElementById("calc"),PNF.dayRate);</script>'
    return form, results, script


def cleaning_sqft_page(p):
    """#14 Price Sheet row: a home's price from its square feet (PNF.cleaningSqft)."""
    d = p["defaults"]
    sv = "".join(f'<option value="{i}"{" selected" if i == 0 else ""}>{E(t)}</option>' for i, t in
                 enumerate(["Standard clean", "Deep clean", "Move-in or move-out (empty home)"]))
    fq = "".join(f'<option value="{i}"{" selected" if i == 0 else ""}>{E(t)}</option>' for i, t in
                 enumerate(["One time", "Monthly (5% off)", "Every 2 weeks (10% off)", "Weekly (15% off)"]))
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>The home</legend>
{field("sqft", "Home size, in sq ft", d["sqft"], "From the listing or the client")}
<div class="row pick"><label for="serviceType">Service<small>Deep takes 1.75 times as long, move-out 2 times</small></label>
<div class="field"><select id="serviceType" data-in="serviceType">{sv}</select></div></div>
<div class="row pick"><label for="freq">How often<small>The kit's example discounts. Change them in the workbook.</small></label>
<div class="field"><select id="freq" data-in="freq">{fq}</select></div></div>
{field("miles", "Round-trip miles", d["miles"])}
</fieldset>
<fieldset><legend>How fast you clean</legend>
{field("minPer1000", "Person-minutes per 1,000 sq ft", d["minPer1000"], "Standard clean, one person. Time a few of your own")}
{field("minCharge", "Minimum charge per visit", d["minCharge"], "No price goes below this", pre="$")}
</fieldset>
<fieldset><legend>Your year</legend>
{field("takeHome", "Take-home pay you want", d["takeHome"], "What you keep after tax, per year", pre="$")}
{field("weeks", "Weeks you work per year", d["weeks"], "52 minus vacation and slow weeks")}
{field("hours", "Hours you work per week, all of it", d["hours"], "Driving, quoting and admin included")}
{field("paidShare", "Share of those hours you are cleaning", d["paidShare"], "Not sure? Try 60 to 70", suf="%")}
</fieldset>
<fieldset><legend>Costs and taxes</legend>
{field("monthlyCosts", "Business costs per month", d["monthlyCosts"], p["costs_hint"], pre="$")}
{field("incomeTax", "Income tax rate, your estimate", d["incomeTax"], "Self-employment tax of 15.3% is added for you", suf="%")}
{field("margin", "Profit margin in prices", d["margin"], "", suf="%")}
{field("perMile", "Vehicle cost per mile", d["perMile"], "IRS business rate: 76 cents (Jul to Dec 2026)", pre="$")}
{field("mph", "Average speed between jobs", d["mph"], "Miles per hour")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Your price per sq ft</div><div class="val" data-out="perSqFt" data-fmt="money3">$0</div><div class="sub">This visit: <span data-out="visit" data-fmt="money0">$0</span></div></div>
<div class="tile"><div class="lab">Per 1,000 sq ft</div><div class="val" data-out="per1000">$0</div></div>
<div class="tile"><div class="lab">One-time price</div><div class="val" data-out="oneTime" data-fmt="money0">$0</div><div class="sub">Before any discount</div></div>
<div class="tile"><div class="lab">Break-even per clean hour</div><div class="val" data-out="breakEven">$0</div></div>
</div>
<ul class="lines">
<li><span>Clean and drive time at break-even (<span data-out="cleanHours" data-fmt="hrs">0</span> cleaning)</span><span data-out="laborCost">$0</span></li>
<li><span>Vehicle</span><span data-out="vehicle">$0</span></li>
<li><span>Supplies for this service</span><span data-out="supplies">$0</span></li>
<li class="total"><span>Price floor, zero profit</span><span data-out="floor">$0</span></li>
<li><span>Floor per sq ft</span><span data-out="floorPerSqFt" data-fmt="money3">$0</span></li>
</ul>
<div class="callout" data-show-if="atMinimum > 0">This home prices at your minimum charge, so its per-sq-ft price is higher than a bigger home's.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Per sq ft <b data-out="perSqFt" data-fmt="money3">$0</b></span><span>Visit <b data-out="visit" data-fmt="money0">$0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
f.querySelectorAll("select").forEach(function(s){s.addEventListener("change",function(){f.dispatchEvent(new Event("input"));});});
PNF.wire(f,PNF.cleaningSqft);})();</script>"""
    return form, results, script


def handmade_page(p):
    """#12 2 Products, one row (PNF.handmadePrice): unit cost with your making time, the x2 check price, profit after fees."""
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>What one piece costs you</legend>
{field("materials", "Materials per piece", d["materials"], "Everything that goes into one piece, for example wax, wick and tin", pre="$")}
{field("minutes", "Minutes to make one", d["minutes"], "Your making time for one piece, in minutes")}
{field("rate", "Your hourly rate for making", d["rate"], "What an hour of your making time is worth", pre="$")}
{field("packaging", "Packaging per piece", d["packaging"], "Bag, box, label or tissue", pre="$")}
</fieldset>
<fieldset><legend>Fees and your price</legend>
{field("feePct", "Fees on each sale", d["feePct"], "Card, payment or marketplace fees as a share of the price. 0 for cash", suf="%")}
{field("price", "Your price", d["price"], "Optional. What you charge now, before sales tax", pre="$")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Formula price</div><div class="val" data-out="x2">$0</div><div class="sub">(Materials + labor) x 2</div></div>
<div class="tile"><div class="lab">Unit cost</div><div class="val" data-out="uc">$0</div><div class="sub">Materials, packaging and your time</div></div>
<div class="tile"><div class="lab">Lowest price</div><div class="val" data-out="floor">$0</div><div class="sub">Covers the unit cost and fees, no profit</div></div>
</div>
<ul class="lines">
<li><span>Materials and packaging</span><span data-out="mp">$0</span></li>
<li><span>Labor (your making time)</span><span data-out="labor">$0</span></li>
<li class="total"><span>Unit cost</span><span data-out="uc">$0</span></li>
<li><span>Profit at the formula price, after fees</span><span data-out="x2Profit">$0</span></li>
<li><span>Fees at your price</span><span data-out="fees">$0</span></li>
<li class="total"><span>Profit per piece at your price</span><span data-out="ppu">$0</span></li>
</ul>
<div class="callout" data-show-if="ok > 0">Your <b data-out="price">$0</b> price is at or above the formula price. Each sale keeps <b data-out="ppu">$0</b> after the unit cost and fees: <b data-pct="margin">0%</b> of the price, on top of paying your time.</div>
<div class="callout warn" data-show-if="belowGain > 0">Your <b data-out="price">$0</b> price is below the <b data-out="x2">$0</b> formula price. It still keeps <b data-out="ppu">$0</b> a piece after your time and fees, but your hours are carrying part of the price.</div>
<div class="callout warn" data-show-if="neg > 0">At <b data-out="price">$0</b> the unit cost and fees take the whole price: each sale loses <b data-out="loss">$0</b> or breaks even, so part of your making time goes unpaid.</div>
<div class="callout" data-show-if="noPrice > 0">Type your price to check it against the formula price.</div>
<div class="callout warn" data-show-if="none > 0">Type what one piece costs you in materials and time.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Formula <b data-out="x2">$0</b></span><span>Unit cost <b data-out="uc">$0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.handmadePrice in assets/pnf-calc.js, 2 Products of engines/craft-fair-profit (#12). */
var M=function(i){var r=PNF.handmadePrice(i);r.mp=Math.max(0,PNF.num(i.materials))+Math.max(0,PNF.num(i.packaging));return r;};
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def markup_page(p):
    """#25 Items tab seen as a markup (PNF.markup): price from unit cost and markup, margin, profit after fees."""
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>Your cost and markup</legend>
{field("unitCost", "Unit cost", d["unitCost"], "Materials, labor and packaging for one unit", pre="$")}
{field("markupPct", "Markup", d["markupPct"], "Profit as a share of your cost. 100% doubles the cost", suf="%")}
{field("feePct", "Selling and payment fees", d["feePct"], "Your fees as a share of the price. 0 if none", suf="%")}
</fieldset>
<fieldset><legend>Check a price (optional)</legend>
{field("checkPrice", "A price to check", d["checkPrice"], "What you charge now, or a price you are thinking about", pre="$")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Selling price</div><div class="val" data-out="price">$0</div><div class="sub">Cost plus <span data-pct="markup">0%</span> markup</div></div>
<div class="tile"><div class="lab">Gross margin</div><div class="val" data-pct="margin">0%</div><div class="sub">Profit before fees, share of price</div></div>
<div class="tile"><div class="lab">Profit per unit after fees</div><div class="val" data-out="ppu">$0</div><div class="sub"><span data-pct="netMargin">0%</span> of the price</div></div>
</div>
<ul class="lines">
<li><span>Unit cost</span><span data-out="cost">$0</span></li>
<li><span>Markup in dollars</span><span data-out="gp">$0</span></li>
<li class="total"><span>Selling price</span><span data-out="price">$0</span></li>
<li><span>Fees</span><span data-out="fees">$0</span></li>
<li class="total"><span>Profit per unit after fees</span><span data-out="ppu">$0</span></li>
</ul>
<div class="callout" data-show-if="pos > 0">Each sale at <b data-out="price">$0</b> keeps <b data-out="ppu">$0</b> after the unit cost and fees.</div>
<div class="callout warn" data-show-if="neg > 0">At this markup the fees and cost take the whole price: each sale loses <b data-out="loss">$0</b> or breaks even.</div>
<div class="callout warn" data-show-if="none > 0">Type what one unit costs you to see the price.</div>
<div class="callout" data-show-if="checkGain > 0">A <b data-out="checkPrice">$0</b> price is a <b data-pct="checkMarkup">0%</b> markup and a <b data-pct="checkMargin">0%</b> gross margin. It keeps <b data-out="checkProfit">$0</b> a unit after fees.</div>
<div class="callout warn" data-show-if="checkLoss > 0">A <b data-out="checkPrice">$0</b> price keeps <b data-out="checkProfit">$0</b> a unit after cost and fees: no profit.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Price <b data-out="price">$0</b></span><span>Profit <b data-out="ppu">$0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.markup in assets/pnf-calc.js, 1 Items of engines/inventory-tracker (#25). */
var M=function(i){return PNF.markup(i);};
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def break_even_page(p):
    """#28 Statement month split into costs that rise with sales and costs paid anyway (PNF.breakEven)."""
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>One month of your business</legend>
{field("sales", "Sales for the month", d["sales"], "Net revenue: sales less refunds", pre="$")}
{field("variable", "Costs that rise with each sale", d["variable"], "Stock and materials, selling and payment fees, shipping labels", pre="$")}
{field("fixed", "Costs you pay anyway", d["fixed"], "Rent, insurance, phone, software, ads and other monthly bills", pre="$")}
</fieldset>
<fieldset><legend>Orders (optional)</legend>
{field("avgSale", "Average sale", d["avgSale"], "Sales divided by orders. Leave blank to skip", pre="$")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Break-even sales a month</div><div class="val" data-out="be" data-never="Never">$0</div><div class="sub">Zero profit, zero loss</div></div>
<div class="tile"><div class="lab">Contribution margin</div><div class="val" data-pct="cm">0%</div><div class="sub">Of each sales dollar, after the costs that rise with it</div></div>
<div class="tile"><div class="lab">Profit this month</div><div class="val" data-out="profit">$0</div></div>
</div>
<ul class="lines">
<li><span>Sales</span><span data-out="sales">$0</span></li>
<li><span>Costs that rise with each sale (<span data-pct="varShare">0%</span> of sales)</span><span data-out="variable">$0</span></li>
<li class="total"><span>Left to cover the fixed costs</span><span data-out="cmDollars">$0</span></li>
<li><span>Costs you pay anyway</span><span data-out="fixed">$0</span></li>
<li class="total"><span>Profit this month</span><span data-out="profit">$0</span></li>
<li data-show-if="ordersOn > 0"><span>Orders a month to break even</span><span data-out="orders" data-fmt="int">0</span></li>
</ul>
<div class="callout" data-show-if="above > 0">You are <b data-out="cushion">$0</b> above break-even: sales could drop <b data-pct="cushionShare">0%</b> before the month turns to a loss.</div>
<div class="callout warn" data-show-if="below > 0">You are <b data-out="short">$0</b> short of break-even this month. Raise prices, cut a cost that rises with sales, or sell more.</div>
<div class="callout warn" data-show-if="never > 0">The costs that rise with each sale take the whole sale, so more sales never cover the fixed costs. Raise prices or cut those costs first.</div>
<div class="callout warn" data-show-if="noSales > 0">Type a month of sales to see your break-even.</div>
<div class="callout warn" data-show-if="none > 0">Type your sales and costs for one month.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Break-even <b data-out="be" data-never="Never">$0</b></span><span>Profit <b data-out="profit">$0</b></span></div>"""
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.breakEven in assets/pnf-calc.js, 2 Statement of engines/profit-and-loss (#28). */
var M=function(i){return PNF.breakEven(i);};
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


def _lead_lists(p):
    """The City-record lists the lead cost page compares with: our price and this week's counts, read from each list's
    own data file at build time (store_products), so the Monday refresh updates the page. Spec key "lists": [[key, trade]]."""
    by = {x["key"]: x for x in store_products()}
    out = []
    for key, trade in p.get("lists", []):
        x = by.get(key)
        if not x or not x.get("checkout"):
            continue
        c = x.get("counts", {})
        if key == "chicago-restaurant-inspection-leads":
            pests = c.get("byCat", {}).get("pests", 0)
            count = f'{pests:,} Chicago food places failed or passed with conditions with a pest violation in the last 30 days'
        elif key == "chicago-new-business-licenses":
            count = f'{c.get("keptWeek", 0):,} new business licenses at Chicago business sites in the latest week, {c.get("kept30", 0):,} in 30 days'
        else:
            near = c.get("nearFinish", 0)
            count = (f'{c.get("kept", 0):,} open {x["tag"].split(" · ")[0]} projects of $500,000 or more' + (f', {near:,} of them near finish' if near >= 5 else ""))
        count += f' (City data pulled {x["asof"]})'
        out.append({"key": key, "trade": trade, "name": x["name"], "tag": x["tag"], "price": int(x["price"]), "per": x["per"],
                    "trial": x.get("trial", 0), "checkout": x["checkout"], "campaign": x["campaign"], "href": x["href"],
                    "sample": x.get("sample", ""), "count": count, "asof": x.get("asof", "")})
    return out


def lead_cost_page(p):
    """Lead cost per won job (PNF.leadCost): a cleaning or pest owner's own month of platform leads, then break-even
    only against our City-record lists (Todd, Oct 24): jobs to cover each list's price, the most a won job can cost,
    and a scenario on the owner's own guess. Never a claim that a list costs less per won job (no conversion data)."""
    d = p["defaults"]
    lists = _lead_lists(p)
    prices = [x["price"] for x in lists]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>One month of platform leads</legend>
{field("spend", "What you paid for leads this month", d["spend"], "Angi, Thumbtack, HomeAdvisor, Bark, Google and the like, all together", pre="$")}
{field("leads", "Leads you paid for", d["leads"], "Every lead charged, good or bad")}
{field("quotes", "Quotes you sent", d["quotes"], "Leads you priced a job for")}
{field("jobs", "Jobs you won", d["jobs"], "Quotes the customer said yes to")}
</fieldset>
<fieldset><legend>An average won job</legend>
{field("avgJob", "Average job revenue", d["avgJob"], "What the customer pays for one job", pre="$")}
{field("jobCost", "Direct cost of one job", d["jobCost"], "Labor you pay, supplies or chemicals, gas. Not the lead.", pre="$")}
</fieldset>
<fieldset><legend>A scenario on your numbers (optional)</legend>
{field("scenJobs", "Won jobs a month a City-record list might bring you", d["scenJobs"], "Your own guess. We have no data on how many records become jobs")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Lead cost per won job</div><div class="val" data-out="cpj" data-never="No jobs yet" data-never-if="cpjNone">$0</div><div class="sub">What you paid in leads for each yes</div></div>
<div class="tile"><div class="lab">Cost per lead</div><div class="val" data-out="cpl">$0</div><div class="sub">Per quote: <span data-out="cpq">$0</span></div></div>
<div class="tile"><div class="lab">Profit left after lead spend</div><div class="val" data-out="profit" data-fmt="money0">$0</div><div class="sub">This month, all won jobs</div></div>
<div class="tile"><div class="lab">Most a won job can cost</div><div class="val" data-out="maxCost">$0</div><div class="sub">In leads, before the job loses money</div></div>
</div>
<ul class="lines">
<li><span>Revenue from won jobs</span><span data-out="revenue" data-fmt="money0">$0</span></li>
<li><span>Direct cost of those jobs</span><span data-out="direct" data-fmt="money0">$0</span></li>
<li class="total"><span>Left before lead spend</span><span data-out="gross" data-fmt="money0">$0</span></li>
<li><span>Lead spend</span><span data-out="spend" data-fmt="money0">$0</span></li>
<li class="total"><span>Profit left after lead spend</span><span data-out="profit" data-fmt="money0">$0</span></li>
<li><span>One job: profit before the lead</span><span data-out="perJob">$0</span></li>
<li><span>One job: after its share of lead spend</span><span data-out="afterLead">$0</span></li>
<li><span>Lead spend as a share of job revenue</span><span data-pct="leadShare">0%</span></li>
<li><span>Leads that became jobs</span><span data-pct="leadToJob">0%</span></li>
<li><span>Quotes won</span><span data-pct="winRate">0%</span></li>
</ul>
<div class="callout" data-show-if="pos > 0">Leads ate <b data-pct="eatsShare">0%</b> of what each job left you. You need <b data-out="breakEvenJobs" data-fmt="int">0</b> won jobs a month to cover this lead spend.</div>
<div class="callout warn" data-show-if="neg > 0">These leads cost <b data-out="loss" data-fmt="money0">$0</b> more than the jobs left you. You needed <b data-out="breakEvenJobs" data-fmt="int">0</b> won jobs, not <b data-out="jobs" data-fmt="int">0</b>, to cover the spend.</div>
<div class="callout warn" data-show-if="noJobs > 0">No jobs won yet, so every lead dollar this month is a loss so far. Type the jobs you won to see the cost of each.</div>
<div class="callout warn" data-show-if="underwater > 0">The direct cost of a job is as high as its price, so no number of leads can make these jobs pay. Check the price first.</div>
<div class="callout warn" data-show-if="odd > 0">More quotes than leads, or more jobs than quotes? Check the counts: the rates below the tiles use them.</div>
<div class="callout warn" data-show-if="none > 0">Type one month of lead spend, leads and jobs.</div>
<div class="callout" data-show-if="noSpend > 0">Type what you paid for leads to see the lead cost of each job.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Per won job <b data-out="cpj" data-never="No jobs yet" data-never-if="cpjNone">$0</b></span><span>Profit <b data-out="profit" data-fmt="money0">$0</b></span></div>"""
    by = {x["key"]: x for x in store_products()}
    rows, cards = "", ""
    for n, x in enumerate(lists):
        rows += (f'<tr><th scope="row"><b>{E(x["name"])}</b><br><small>For {E(x["trade"])}</small></th>'
                 f'<td>${x["price"]}/mo</td>'
                 f'<td><span data-out="cover{n}" data-fmt="int" data-never="Can&#39;t" data-never-if="coverNever{n}">0</span></td>'
                 f'<td><span data-out="scen{n}" data-fmt="money0">$0</span></td></tr>')
        # the shop's own card; its Gumroad link also names this page (utm_content) so paid starts from here can be counted
        tag = f'utm_campaign={x["campaign"]}"'
        cards += product_card(by[x["key"]], "../", "calculator").replace(tag, f'utm_campaign={x["campaign"]}&amp;utm_content={p["slug"]}"')
    compare = (f'<section class="block" id="compare"><h2>{E(p["compare"]["title"])}</h2>'
               + "".join(f"<p>{E(t)}</p>" for t in p["compare"]["intro"])
               + '<table class="mt lc-tbl"><thead><tr><th scope="col">List</th><th scope="col">Price</th>'
               '<th scope="col">Jobs to cover it</th><th scope="col">At your guess</th></tr></thead>'
               f'<tbody>{rows}</tbody></table>'
               + "".join(f'<p class="asof">{E(t)}</p>' for t in p["compare"]["notes"])
               + f'<div class="st-grid lc-cards">{cards}</div></section>')
    checklist = (f'<section class="block"><h2>{E(p["keep"]["title"])}</h2>'
                 + f'<p>{E(p["keep"]["lead"])}</p><ul class="checks">' + "".join(f"<li>{E(t)}</li>" for t in p["keep"]["items"])
                 + f'</ul><p>{E(p["keep"]["tail"])}</p></section>')
    script = f"""<script>
(function(){{var f=document.getElementById("calc"),L={json.dumps(prices)};
/* Maths: PNF.leadCost in assets/pnf-calc.js; L is our list prices, read from site/store.json at build. */
var M=function(i){{return PNF.leadCost(i,L);}};
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;PNF.stages(f,"../e/{p["slug"]}/");}})();</script>"""
    return form, results + "\n<!--LC-EXTRA-->" + compare + checklist, script


def _dd7_next(p):
    """Where the DD+7 page sends a seller next: the $79 workbook (Gumroad, utm-tagged so paid starts can be counted)
    and the Shopify payouts question page."""
    nx, pages = p["next"], _pages_by_slug()
    kit = next((x for x in store_products() if x["key"] == "ecommerce-13-week-cash-flow"), None)
    q = pages.get(nx["question"])
    out = f'<section class="block"><h2>{E(nx["title"])}</h2>'
    if kit:
        out += f'<p>{E(nx["workbook"])} <a href="../{kit["href"]}">13 week cash flow calculator</a>.</p>'
    if q and is_live(q):
        out += f'<p>{E(nx["shopify"])} <a href="../{q["slug"]}/">{E(q["h1"])}</a></p>'
    return out + '</section>'


def dd7_page(p):
    """Amazon DD+7 payout gap (PNF.payoutGap): money held, days from order to bank and the low point, from rules on
    Amazon's own US help pages (spec "rules", each with the URL and the date read)."""
    d = p["defaults"]
    sel = lambda key, label, hint, opts, val: (
        f'<div class="row"><label for="{key}">{E(label)}{f"<small>{E(hint)}</small>" if hint else ""}</label>'
        f'<div class="field"><select id="{key}" data-in="{key}">'
        + "".join(f'<option value="{v}"{" selected" if str(v) == str(val) else ""}>{E(t)}</option>' for v, t in opts)
        + '</select></div></div>')
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>Your Amazon sales</legend>
{field("sales", "Daily sales, after Amazon fees", d["sales"], "What Amazon pays you per day: sales less referral and FBA fees", pre="$")}
{sel("fulfil", "Who ships the orders", "Fulfilled by Amazon, or merchant fulfilled (you ship)", [(0, "FBA"), (1, "Merchant")], d["fulfil"])}
{field("deliverDays", "Days from order to delivery", d["deliverDays"], "Your usual, from the order date")}
<div data-show-if="mfn > 0">{sel("tracked", "Tracking on your shipments", "Valid tracking from an integrated carrier lets Amazon use the actual delivery date", [(1, "Valid"), (0, "None")], d["tracked"])}</div>
<div data-show-if="eddUsed > 0">{field("eddDays", "Days from order to the latest estimated delivery date", d["eddDays"], "Without valid tracking, Amazon counts from this date")}</div>
</fieldset>
<fieldset><legend>How you get paid</legend>
{sel("schedule", "Payout schedule", "Amazon's scheduled payout every 14 days, or a payout you request daily", [(0, "14 days"), (1, "Daily")], d["schedule"])}
</fieldset>
<fieldset><legend>Your cash (for the low point)</legend>
{field("cash", "Cash in the bank today", d["cash"], "All business accounts together", pre="$")}
{field("costs", "What you pay out per day", d["costs"], "Stock, ads, shipping, payroll and bills, as a daily average", pre="$")}
</fieldset>
<fieldset><legend>Fine tune (optional)</legend>
<div data-show-if="scheduled > 0">{field("nextPayout", "Days until your next scheduled payout", d["nextPayout"], "1 to 14. Manage Payouts or the Payments dashboard shows the date")}</div>
{field("bankDays", "Days for a payout to reach your bank", d["bankDays"], "Express Payout: within 24 hours, so 1. Standard: 3 to 5 business days")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Money Amazon holds at the most</div><div class="val" data-out="heldMax" data-fmt="money0">$0</div><div class="sub"><span data-out="heldDays" data-fmt="int">0</span> days of sales not yet in your bank</div></div>
<div class="tile"><div class="lab">Order to bank</div><div class="val"><span data-out="fastest" data-fmt="int">0</span><span data-show-if="range > 0"> to <span data-out="slowest" data-fmt="int">0</span></span> days</div><div class="sub"><span data-show-if="range > 0">Depends on the order's day in the payout cycle</span><span data-show-if="scheduled < 1">For every order, with a daily request</span></div></div>
<div class="tile"><div class="lab">Your bank's low point</div><div class="val" data-out="low" data-fmt="money0" data-never="Keeps falling" data-never-if="falling">$0</div><div class="sub"><span data-show-if="lowOn > 0">On day <span data-out="lowDay" data-fmt="int">0</span>, if sales start today</span><span data-show-if="falling > 0">You pay out more than Amazon pays you</span><span data-show-if="noSales > 0">Type your daily sales</span><span data-show-if="noCosts > 0">Add what you pay out per day</span></div></div>
<div class="tile"><div class="lab">Cash needed to stay above $0</div><div class="val" data-out="need" data-fmt="money0" data-never="No set amount" data-never-if="falling">$0</div><div class="sub"><span data-show-if="falling < 1">Before the first payouts catch up</span><span data-show-if="falling > 0">Until spend drops below sales</span></div></div>
</div>
<ul class="lines">
<li><span>Days to the delivery date Amazon uses</span><span data-out="dateDays" data-fmt="int">0</span></li>
<li><span>Days until Amazon releases the money</span><span data-out="avail" data-fmt="int">0</span></li>
<li><span>First money in your bank</span><span data-out="firstText" data-fmt="text">Day 0</span></li>
<li data-show-if="range > 0"><span>Money Amazon holds at the least</span><span data-out="heldMin" data-fmt="money0">$0</span></li>
</ul>
<div class="callout warn" data-show-if="short > 0">Your bank runs <b data-out="need" data-fmt="money0">$0</b> short on day <b data-out="lowDay" data-fmt="int">0</b>. Have that much more ready, or slow what you pay out before then.</div>
<div class="callout" data-show-if="ok > 0">Your cash covers the wait: the lowest it gets is <b data-out="low" data-fmt="money0">$0</b>, on day <b data-out="lowDay" data-fmt="int">0</b>.</div>
<div class="callout warn" data-show-if="falling > 0">You pay out more than Amazon pays you, so cash keeps falling whatever the payout timing. Lower the daily spend to see a low point.</div>
<div class="callout" data-show-if="eddUsed > 0">Without valid tracking, each order waits for its latest estimated delivery date, not the real one.</div>
<div class="callout" data-show-if="noCosts > 0">Add what you pay out per day to see your low point.</div>
<div class="callout warn" data-show-if="noSales > 0">Type your daily sales after Amazon fees.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Held <b data-out="heldMax" data-fmt="money0">$0</b></span><span>Low <b data-out="low" data-fmt="money0" data-never="Falling" data-never-if="falling">$0</b></span></div>"""
    rules = "".join(f'<li><span>{E(r["rule"])} Source: <a href="{E(r["url"])}" rel="noopener">{E(r["page"])}</a>.</span></li>' for r in p["rules"])
    extra = (f'<section class="block"><h2>{E(p["rulesTitle"])}</h2><ul class="checks">{rules}</ul>'
             + "".join(f"<p>{E(t)}</p>" for t in p["rulesNotes"]) + '</section>'
             + (f'<section class="block"><h2>{E(p["where"]["title"])}</h2><ul class="checks">'
                + "".join(f'<li><span>{E(w["text"])} Source: <a href="{E(w["url"])}" rel="noopener">{E(w["page"])}</a>.</span></li>' for w in p["where"]["items"])
                + '</ul></section>' if p.get("where") else "")
             + _dd7_next(p))
    script = """<script>
(function(){var f=document.getElementById("calc");
/* Maths: PNF.payoutGap in assets/pnf-calc.js; rules and dates in its comment and on this page. */
var M=function(i){return PNF.payoutGap(i);};
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;PNF.stages(f,"../e/amazon-dd7-payout-calculator/");})();</script>"""
    return form, results + "\n<!--LC-EXTRA-->" + extra, script


def _sel(key, label, hint, opts, val, wide=False):
    """A labelled select feeding the model (data-in), as on the DD+7 page; wide = full-width (row pick) for long options."""
    return (f'<div class="row{" pick" if wide else ""}"><label for="{key}">{E(label)}{f"<small>{E(hint)}</small>" if hint else ""}</label>'
            f'<div class="field"><select id="{key}" data-in="{key}">'
            + "".join(f'<option value="{v}"{" selected" if str(v) == str(val) else ""}>{E(t)}</option>' for v, t in opts)
            + '</select></div></div>')


def _model_script(model, slug):
    return f"""<script>
(function(){{var f=document.getElementById("calc");
/* Maths: PNF.{model} in assets/pnf-calc.js (trade season calculators, Oct 26, 2026). */
var M=function(i){{return PNF.{model}(i);}};
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;PNF.stages(f,"../e/{slug}/");}})();</script>"""


def _notes_block(p):
    """Optional spec "notes": {"title", "items": [[text, url, page]], "tail": [..]} under the calculator (sourced rules)."""
    n = p.get("notes")
    if not n:
        return ""
    lis = "".join(f'<li>{E(t)}' + (f' Source: <a href="{E(u)}" rel="noopener">{E(pg)}</a>.' if u else "") + '</li>' for t, u, pg in n["items"])
    return (f'<section class="block"><h2>{E(n["title"])}</h2><ul class="src-list">{lis}</ul>'
            + "".join(f"<p>{E(t)}</p>" for t in n.get("tail", [])) + '</section>')


def lights_page(p):
    """Christmas light installation quote (PNF.lightsQuote): roofline feet, bushes and trees, crew time for install and
    takedown, trips, and lights either owned by the business (spread over the seasons they last, plus storage) or bought
    by the customer (charged this year, dropped from next season's quote). Todd's go, Oct 26, 2026."""
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>The house</legend>
{field("feet", "Feet of roofline to light", d["feet"], "Gutters, peaks and ridges you will run lights along")}
{field("shrubs", "Bushes and trees to wrap", d["shrubs"], "0 if none")}
</fieldset>
<fieldset><legend>Your crew and pace</legend>
{field("ftPerHour", "Feet one person hangs an hour", d["ftPerHour"], "Your own pace on this kind of roof, ladder moves included")}
{field("shrubMin", "Minutes per bush or tree, one person", d["shrubMin"])}
{field("people", "People on the crew", d["people"])}
{field("rate", "Labor cost per person-hour", d["rate"], "What you pay, or your own break-even rate", pre="$")}
{field("takedownPct", "Takedown time, share of install time", d["takedownPct"], "Removal and packing after the season", suf="%")}
</fieldset>
<fieldset><legend>The lights</legend>
{_sel("owner", "Who owns the lights", "Lent each year and stored by you, or bought and kept by the customer", [(0, "Ours"), (1, "Customer")], d["owner"])}
{field("matPerFt", "Lights, wire and clips per foot", d["matPerFt"], "Your cost, per foot of roofline", pre="$")}
{field("shrubMat", "Lights per bush or tree", d["shrubMat"], pre="$")}
<div data-show-if="owned > 0">{field("seasons", "Seasons your lights last", d["seasons"], "Their cost is spread over these seasons")}
{field("storage", "Storage and handling per customer, per year", d["storage"], "Bins, labels, shelf space, testing", pre="$")}</div>
</fieldset>
<fieldset><legend>Trips and margin</legend>
{field("serviceCalls", "Service calls you expect", d["serviceCalls"], "Install and takedown trips are counted already")}
{field("tripMin", "Drive time per trip, round trip", d["tripMin"], "Minutes")}
{field("tripMiles", "Miles per trip, round trip", d["tripMiles"])}
{field("perMile", "Vehicle cost per mile", d["perMile"], "IRS business rate: 76 cents (Jul to Dec 2026)", pre="$")}
{field("margin", "Profit margin in the quote", d["margin"], "A share of the quote", suf="%")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Quote for this house</div><div class="val" data-out="quote" data-fmt="money0">$0</div><div class="sub">Install and takedown, rounded up to the next $5</div></div>
<div class="tile" data-show-if="perFtOn > 0"><div class="lab">Price per foot of roofline</div><div class="val" data-out="perFt">$0</div><div class="sub">Break-even <span data-out="floorPerFt">$0</span> a foot</div></div>
<div class="tile"><div class="lab">Profit in the quote</div><div class="val" data-out="profit">$0</div></div>
<div class="tile"><div class="lab">Install, crew on site</div><div class="val" data-out="crewHrs" data-fmt="hrs">0</div><div class="sub">Clock hours, crew working together</div></div>
</div>
<ul class="lines">
<li><span>Install and takedown, <span data-out="workHrs" data-fmt="hrs">0</span> of work</span><span data-out="labor">$0</span></li>
<li><span>Drive time and miles, <span data-out="trips" data-fmt="int">0</span> trips</span><span data-out="drive">$0</span></li>
<li><span>Lights for this season</span><span data-out="materials">$0</span></li>
<li data-show-if="owned > 0"><span>Storage and handling</span><span data-out="storage">$0</span></li>
<li class="total"><span>Price floor, zero profit</span><span data-out="floor">$0</span></li>
</ul>
<p class="asof">Takedown adds <span data-out="takedownHrs" data-fmt="hrs">0</span> of work (person-hours), counted in labor.</p>
<div class="callout" data-show-if="boughtOn > 0">Next season the customer already owns the lights: the same house quotes at <b data-out="quote2" data-fmt="money0">$0</b>, with <b data-out="profit2">$0</b> of profit.</div>
<div class="callout" data-show-if="ownedOn > 0">Your lights cost <b data-out="matAll">$0</b> for this house, spread over the seasons they last. A returning customer quotes the same next season.</div>
<div class="callout warn" data-show-if="noMargin > 0">Use a margin under 100%: the quote is your cost divided by one less the margin.</div>
<div class="callout warn" data-show-if="noRate > 0">Type how many feet one person hangs an hour to price the roofline.</div>
<div class="callout warn" data-show-if="noLabor > 0">Add a labor cost per person-hour, even if it is your own time.</div>
<div class="callout warn" data-show-if="none > 0">Type the feet of roofline, or the bushes and trees, to see a quote.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Quote <b data-out="quote" data-fmt="money0">$0</b></span><span>Per foot <b data-out="perFt">$0</b></span></div>"""
    return form, results + "\n<!--LC-EXTRA-->" + _notes_block(p), _model_script("lightsQuote", p["slug"])


def snow_page(p):
    """Snow removal per push and seasonal contract (PNF.snowQuote) for one stop on a route. Todd's go, Oct 26, 2026."""
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>One stop on your route</legend>
{field("pushMin", "Minutes on site for a normal push", d["pushMin"], "Plowing or blowing at your trigger depth, shoveling walks included")}
{field("deepMin", "Minutes on site for a deep storm", d["deepMin"], "Your time when the snow is well over the trigger. 0 to skip")}
{field("driveMin", "Drive minutes to this stop", d["driveMin"], "From the stop before it on your route")}
{field("salt", "Salt or ice melt per visit", d["salt"], "Your cost. 0 if you do not salt", pre="$")}
</fieldset>
<fieldset><legend>Crew and equipment</legend>
{field("people", "People on this stop", d["people"])}
{field("rate", "Labor cost per person-hour", d["rate"], "What you pay, or your own break-even rate", pre="$")}
{field("equip", "Truck, plow or blower cost per hour", d["equip"], "Fuel, wear, repairs and payments, spread per working hour", pre="$")}
{field("margin", "Profit margin in the quote", d["margin"], "A share of the quote", suf="%")}
</fieldset>
<fieldset><legend>A seasonal contract</legend>
{field("events", "Pushes you expect in a season", d["events"], "Storms over your trigger depth. Check your own records")}
{field("cushion", "Cushion for a heavy winter", d["cushion"], "Added on top of the expected pushes", suf="%")}
{field("months", "Months you bill the contract over", d["months"], "November to March is 5")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Price per push</div><div class="val" data-out="quote" data-fmt="money0">$0</div><div class="sub">Rounded up to the next $5</div></div>
<div class="tile"><div class="lab">Seasonal contract</div><div class="val" data-out="season" data-fmt="money0">$0</div><div class="sub"><span data-show-if="monthsOn > 0"><span data-out="monthly" data-fmt="money0">$0</span> a month</span><span data-show-if="monthsOn < 1">Type the months you bill over</span></div></div>
<div class="tile" data-show-if="deepOn > 0"><div class="lab">Deep storm push</div><div class="val" data-out="deepQuote" data-fmt="money0">$0</div><div class="sub">At your deep storm minutes</div></div>
<div class="tile" data-show-if="seasonOn > 0"><div class="lab">Pushes the contract covers</div><div class="val" data-out="covers" data-fmt="int">0</div><div class="sub">Before the season costs more than it pays</div></div>
</div>
<ul class="lines">
<li><span>Cost of one push</span><span data-out="cost">$0</span></li>
<li><span>Profit in one push</span><span data-out="profit">$0</span></li>
<li data-show-if="deepOn > 0"><span>Cost of a deep storm push</span><span data-out="deepCost">$0</span></li>
<li data-show-if="seasonOn > 0"><span>Season profit, expected pushes</span><span data-out="seasonProfit">$0</span></li>
<li><span>Price per hour on this stop, one push</span><span data-out="hourly">$0</span></li>
</ul>
<div class="callout" data-show-if="seasonOn > 0">A seasonal price of <b data-out="season" data-fmt="money0">$0</b> pays you whether it snows or not. It turns into a loss once your pushes pass <b data-out="covers" data-fmt="int">0</b>.</div>
<div class="callout warn" data-show-if="noMargin > 0">Use a margin under 100%: the quote is your cost divided by one less the margin.</div>
<div class="callout warn" data-show-if="deepLow > 0">Your deep storm minutes are under a normal push. Check the two times.</div>
<div class="callout warn" data-show-if="noEvents > 0">Type how many pushes you expect in a season to price a seasonal contract.</div>
<div class="callout warn" data-show-if="noRate > 0">Add a labor cost or an equipment cost per hour to see a price.</div>
<div class="callout warn" data-show-if="none > 0">Type the minutes on site for a normal push.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Per push <b data-out="quote" data-fmt="money0">$0</b></span><span>Season <b data-out="season" data-fmt="money0">$0</b></span></div>"""
    return form, results + "\n<!--LC-EXTRA-->" + _notes_block(p), _model_script("snowQuote", p["slug"])


def hood_page(p):
    """Kitchen exhaust hood cleaning price per visit and per year (PNF.hoodQuote); visits a year follow the NFPA 96
    inspection frequency for the cooking type (sourced in the spec's "notes"). Todd's go, Oct 26, 2026."""
    d = p["defaults"]
    opts = [(n, t) for n, t in enumerate(p["cookingTypes"])]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>The kitchen</legend>
{_sel("cooking", "Type of cooking", "High volume: 24-hour, charbroil or wok. Low volume: churches, day camps, seasonal. Sets how often NFPA 96 calls for an inspection", opts, d["cooking"], wide=True)}
{field("hoods", "Hoods to clean", d["hoods"])}
{field("hoodHrs", "Crew hours per hood", d["hoodHrs"], "Hood, filters and plenum, all people together")}
{field("ductHrs", "Crew hours for duct and fan", d["ductHrs"], "Duct runs, the roof fan and the grease containment, all people together")}
</fieldset>
<fieldset><legend>Your crew and costs</legend>
{field("people", "People on the crew", d["people"])}
{field("rate", "Labor cost per person-hour", d["rate"], "What you pay, or your own break-even rate", pre="$")}
{field("nightPct", "Night work premium on labor", d["nightPct"], "Most kitchens are cleaned after closing. 0 if none", suf="%")}
{field("supplies", "Chemicals and supplies per visit", d["supplies"], "Degreaser, plastic, tape, filters, stickers", pre="$")}
</fieldset>
<fieldset><legend>Trip and margin</legend>
{field("tripMin", "Drive time, round trip", d["tripMin"], "Minutes")}
{field("tripMiles", "Miles, round trip", d["tripMiles"])}
{field("perMile", "Vehicle cost per mile", d["perMile"], "IRS business rate: 76 cents (Jul to Dec 2026)", pre="$")}
{field("margin", "Profit margin in the quote", d["margin"], "A share of the quote", suf="%")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Price per visit</div><div class="val" data-out="quote" data-fmt="money0">$0</div><div class="sub">Rounded up to the next $5</div></div>
<div class="tile"><div class="lab">Visits a year</div><div class="val" data-out="visits" data-fmt="int">0</div><div class="sub">NFPA 96 inspection frequency</div></div>
<div class="tile"><div class="lab">Yearly contract</div><div class="val" data-out="year" data-fmt="money0">$0</div><div class="sub"><span data-out="monthly" data-fmt="money0">$0</span> a month</div></div>
<div class="tile"><div class="lab">Profit a year</div><div class="val" data-out="yearProfit" data-fmt="money0">$0</div></div>
</div>
<ul class="lines">
<li><span>Labor with night premium, <span data-out="crewHrs" data-fmt="hrs">0</span> of crew time</span><span data-out="labor">$0</span></li>
<li><span>Drive time and miles</span><span data-out="drive">$0</span></li>
<li><span>Chemicals and supplies</span><span data-out="supplies">$0</span></li>
<li class="total"><span>Cost of one visit</span><span data-out="cost">$0</span></li>
<li><span>Profit per visit</span><span data-out="profit">$0</span></li>
<li data-show-if="hoodsOn > 0"><span>Per hood, per visit</span><span data-out="perHood">$0</span></li>
<li><span>Price per crew hour</span><span data-out="perCrewHr">$0</span></li>
<li><span>Time on site for the crew</span><span data-out="siteHrs" data-fmt="hrs">0</span></li>
</ul>
<div class="callout" data-show-if="none < 1">NFPA 96 sets the inspection schedule; a kitchen is cleaned when the inspection finds grease deposits. This prices one cleaning per scheduled visit.</div>
<div class="callout warn" data-show-if="noMargin > 0">Use a margin under 100%: the quote is your cost divided by one less the margin.</div>
<div class="callout warn" data-show-if="noRate > 0">Add a labor cost per person-hour, even if it is your own time.</div>
<div class="callout warn" data-show-if="none > 0">Type the hoods and the crew hours per hood to see a price.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Per visit <b data-out="quote" data-fmt="money0">$0</b></span><span>Year <b data-out="year" data-fmt="money0">$0</b></span></div>"""
    return form, results + "\n<!--LC-EXTRA-->" + _notes_block(p), _model_script("hoodQuote", p["slug"])


def missed_calls_page(p):
    """What unanswered new-customer calls cost a month (PNF.missedCalls), set beside the monthly cost of an answering
    option the owner was quoted. Names and ranks no vendor. Todd's go, Oct 26, 2026."""
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>Your calls</legend>
{field("calls", "New-customer calls a week", d["calls"], "People calling for a quote or a booking, not existing clients")}
{field("missedPct", "Share of those calls nobody answers", d["missedPct"], "Check your phone log for a typical week", suf="%")}
{field("gonePct", "Missed callers who never call back", d["gonePct"], "Your guess. Count the ones you never hear from again", suf="%")}
{field("bookPct", "Answered new-customer calls that book", d["bookPct"], "From your own answered calls", suf="%")}
</fieldset>
<fieldset><legend>A typical job</legend>
{field("avgJob", "Average job price", d["avgJob"], pre="$")}
{field("marginPct", "Gross margin on a job", d["marginPct"], "What a job leaves after labor, supplies and gas", suf="%")}
{field("jobsPerCustomer", "Jobs a new customer books in their first year", d["jobsPerCustomer"], "1 for one-off work. More for repeat service: the profit lost counts a full first year")}
</fieldset>
<fieldset><legend>An answering option (optional)</legend>
{field("answerCost", "Monthly cost you were quoted", d["answerCost"], "An answering service, an AI receptionist or a part-time hire. 0 to skip", pre="$")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Profit lost a month</div><div class="val" data-out="lostProfit" data-fmt="money0">$0</div><div class="sub"><span data-out="year" data-fmt="money0">$0</span> a year<span data-show-if="repeat > 0">, counting each lost customer's first year</span></div></div>
<div class="tile"><div class="lab">Jobs lost a month</div><div class="val" data-out="lostJobs" data-fmt="dec1">0</div><div class="sub">From <span data-out="lostCallers" data-fmt="dec1">0</span> callers who went elsewhere</div></div>
<div class="tile"><div class="lab">Revenue lost a month</div><div class="val" data-out="lostRev" data-fmt="money0">$0</div><div class="sub" data-show-if="repeat > 0">Each lost customer's first year</div></div>
<div class="tile" data-show-if="optOn > 0"><div class="lab">Customers to cover the option</div><div class="val" data-out="cover" data-fmt="int">0</div><div class="sub">Saved new customers a month</div></div>
</div>
<ul class="lines">
<li><span>Missed new-customer calls a month</span><span data-out="missedMo" data-fmt="dec1">0</span></li>
<li><span>Callers who never call back</span><span data-out="lostCallers" data-fmt="dec1">0</span></li>
<li><span>Jobs those callers would have booked</span><span data-out="lostJobs" data-fmt="dec1">0</span></li>
<li><span>Profit from one new customer, first year</span><span data-out="perJobProfit">$0</span></li>
<li class="total"><span>Profit lost a month</span><span data-out="lostProfit" data-fmt="money0">$0</span></li>
<li data-show-if="optOn > 0"><span>Monthly cost of the option</span><span data-out="cost" data-fmt="money0">$0</span></li>
<li data-show-if="optOn > 0" class="total"><span>Left after the option, if it saved every one</span><span data-out="net" data-fmt="money0">$0</span></li>
</ul>
<div class="callout" data-show-if="pays > 0">The option costs less than the profit you lose. New customers it must save each month to pay for itself: <b data-out="cover" data-fmt="int">0</b>.</div>
<div class="callout warn" data-show-if="notPays > 0">The option costs as much as or more than the profit these calls lose you. Fix the missed calls another way, or price the option lower.</div>
<div class="callout warn" data-show-if="noMargin > 0">Add your gross margin on a job to see the profit lost.</div>
<div class="callout warn" data-show-if="none > 0">Type how many new-customer calls you get a week.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Lost <b data-out="lostProfit" data-fmt="money0">$0</b>/mo</span><span>Jobs <b data-out="lostJobs" data-fmt="dec1">0</b></span></div>"""
    return form, results + "\n<!--LC-EXTRA-->" + _notes_block(p), _model_script("missedCalls", p["slug"])


def price_raise_page(p):
    """The price that keeps a job's profit after costs rise (PNF.priceRaise): hold the profit dollars or the margin, then
    the client loss the raise can take. Todd's go, Oct 26, 2026."""
    d = p["defaults"]
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>One job today</legend>
{field("price", "Price you charge now", d["price"], "For one job or one visit", pre="$")}
{field("cost", "Your cost for that job now", d["cost"], "Labor you pay, supplies, gas. Not your own pay if you count it as profit", pre="$")}
{field("costUpPct", "How much those costs went up", d["costUpPct"], "Since you last set the price", suf="%")}
{field("jobs", "Jobs a month at this price", d["jobs"])}
</fieldset>
<fieldset><legend>Your new price</legend>
{_sel("keep", "What the new price keeps", "Your profit in dollars, or your margin as a share of the price", [(0, "Profit per job"), (1, "Margin")], d["keep"])}
{field("losePct", "Clients you expect to lose over the raise", d["losePct"], "Your guess. 0 if you expect none", suf="%")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">New price</div><div class="val" data-out="rounded" data-fmt="money0">$0</div><div class="sub">Up <span data-out="raise" data-fmt="money0">$0</span>, <span data-pct="raisePct">0%</span></div></div>
<div class="tile"><div class="lab">Lost each month without a raise</div><div class="val" data-out="squeeze" data-fmt="money0">$0</div><div class="sub">The cost rise, at today's price</div></div>
<div class="tile"><div class="lab">Profit a month after the raise</div><div class="val" data-out="after" data-fmt="money0">$0</div><div class="sub">Today: <span data-out="profitNow" data-fmt="money0">$0</span></div></div>
<div class="tile"><div class="lab">Clients you can lose</div><div class="val" data-pct="maxLose">0%</div><div class="sub">Before profit falls below today's</div></div>
</div>
<ul class="lines">
<li><span>Cost per job after the rise</span><span data-out="newCost">$0</span></li>
<li><span>Price that keeps your profit per job</span><span data-out="keepDollars">$0</span></li>
<li><span>Price that keeps your margin</span><span data-out="keepMargin">$0</span></li>
<li><span>Your margin today</span><span data-pct="marginNow">0%</span></li>
<li class="total"><span>Change in monthly profit after the raise</span><span data-out="change" data-fmt="money0">$0</span></li>
</ul>
<div class="callout" data-show-if="better > 0">At <b data-out="rounded" data-fmt="money0">$0</b> your monthly profit stays at or above today's, after the clients you expect to lose.</div>
<div class="callout warn" data-show-if="worse > 0">With the clients you expect to lose, profit ends <b data-out="shortBy" data-fmt="money0">$0</b> a month below today's. Raise a little more, or keep more clients.</div>
<div class="callout warn" data-show-if="under > 0">The job costs as much as you charge now. Price it from your costs first.</div>
<div class="callout warn" data-show-if="noCost > 0">Type what one job costs you now: labor, supplies and gas.</div>
<div class="callout" data-show-if="noUp > 0">Type how much your costs went up to see the price that keeps your profit.</div>
<div class="callout warn" data-show-if="none > 0">Type the price you charge now.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>New price <b data-out="rounded" data-fmt="money0">$0</b></span><span>Up <b data-pct="raisePct">0%</b></span></div>"""
    return form, results + "\n<!--LC-EXTRA-->" + _notes_block(p), _model_script("priceRaise", p["slug"])



def _bid_sel(key, label, opts, val):
    """A full-width select whose hint follows the chosen option (design director, Oct 27): opts [(hint, option text)]."""
    hints = "".join(f'<small data-h="{i}"{"" if str(i) == str(val) else " hidden"}>{E(h)}</small>' for i, (h, _) in enumerate(opts))
    return (f'<div class="row pick"><label for="{key}">{E(label)}{hints}</label><div class="field"><select id="{key}" data-in="{key}">'
            + "".join(f'<option value="{i}"{" selected" if str(i) == str(val) else ""}>{E(o)}</option>' for i, (_, o) in enumerate(opts))
            + '</select></div></div>')


def _bid_check(key, label, on=True):
    return (f'<label class="bid-ph"><input type="checkbox" id="ph-{key}"{" checked" if on else ""}>{E(label)}</label>')


def bid_page(p):
    """Post-construction cleaning bid (PNF.bidPrice, the same function the area seats' bid sheet calls): rough, final and
    touch-up prices from the owner's own size, crew speed, labor cost, supplies, travel and margin, then a one-page proposal
    to print or save as PDF (PNF.bidProposal). Published guide ranges show below as dated context, never as market rates.
    The proposal template download sits behind a Kit form (spec "download"). Todd's go, Oct 27, 2026 (coo/DECISIONS-2026-10-27.md)."""
    d, dl = p["defaults"], p["download"]
    form = f"""<link rel="stylesheet" href="../assets/pnf-bid.css"><form class="card" id="calc" novalidate>
<fieldset><legend>The job</legend>
{_bid_sel("measure", "Price it by", [("Square feet of the whole job", "Square feet"), ("Units times their average size, plus hallways and other common areas", "Apartment units")], d["measure"])}
<div data-bid="sqft">{field("sqft", "Square feet to clean", d["sqft"], "From the plans, the builder or a walk-through")}</div>
<div data-bid="units" hidden>{field("units", "Units", d["units"])}
{field("unitSize", "Average unit size", d["unitSize"], "Square feet")}
{field("common", "Common areas", d["common"], "Square feet of hallways, lobby, amenity rooms. 0 if none")}</div>
</fieldset>
<fieldset><legend>Cleans in this bid</legend>
<div class="bid-phs">{_bid_check("rough", "Rough")}{_bid_check("final", "Final")}{_bid_check("touch", "Touch-up")}</div>
</fieldset>
<fieldset><legend>How fast your crew cleans</legend>
{field("roughRate", "Rough clean", d["roughRate"], "Sq ft one cleaner does in an hour. Time your own jobs")}
{field("finalRate", "Final clean", d["finalRate"], "Sq ft one cleaner does in an hour")}
{field("touchRate", "Touch-up clean", d["touchRate"], "Sq ft one cleaner does in an hour")}
</fieldset>
<fieldset><legend>Your crew and costs</legend>
{field("wage", "Labor cost per cleaner-hour", d["wage"], "Pay plus payroll taxes and workers' comp", pre="$")}
{field("crew", "Cleaners on the crew", d["crew"])}
{field("dayHrs", "Hours in a crew day", d["dayHrs"], "Each day on site is one trip")}
{field("supplies", "Supplies per 1,000 sq ft", d["supplies"], "For each clean: chemicals, bags, pads, rags", pre="$")}
{field("trip", "Travel and parking per day", d["trip"], "Gas, parking, tolls, paid drive time", pre="$")}
</fieldset>
<fieldset><legend>Touch-up</legend>
{field("visits", "Touch-up visits", d["visits"], "Return visits the builder wants")}
{_bid_sel("touchMode", "Touch-up price", [("Priced from your touch-up speed and costs, like the other cleans", "From your rates"), ("Your own price for each visit", "Flat price a visit")], d["touchMode"])}
<div data-bid="flat" hidden>{field("touchFlat", "Your flat price a visit", d["touchFlat"], pre="$")}</div>
</fieldset>
<fieldset><legend>Your price</legend>
{_sel("priceMode", "Add profit as", "Margin is a share of the price. Markup is added on top of cost", [(0, "Margin"), (1, "Markup")], d["priceMode"])}
{field("pct", "Margin or markup", d["pct"], "Covers overhead and profit", suf="%")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
<div class="tiles">
<div class="tile key"><div class="lab">Total bid</div><div class="val" data-out="price" data-fmt="money0">$0</div><div class="val bid-fix" hidden>Fix the highlighted field</div><div class="sub"><span data-out="perSqFt" data-fmt="money3">$0</span> a sq ft<span data-show-if="unitOn > 0">, <span data-out="perUnit" data-fmt="money0">$0</span> a unit</span></div></div>
<div class="tile" data-show-if="roughOn > 0"><div class="lab">Rough clean</div><div class="val" data-out="roughPrice" data-fmt="money0">$0</div><div class="sub"><span data-out="roughHrs" data-fmt="dec1">0</span> cleaner-hours</div></div>
<div class="tile" data-show-if="finalOn > 0"><div class="lab">Final clean</div><div class="val" data-out="finalPrice" data-fmt="money0">$0</div><div class="sub"><span data-out="finalHrs" data-fmt="dec1">0</span> cleaner-hours</div></div>
<div class="tile" data-show-if="touchOn > 0"><div class="lab">Touch-up</div><div class="val" data-out="touchPrice" data-fmt="money0">$0</div><div class="sub"><span data-out="touchHrs" data-fmt="dec1">0</span> cleaner-hours</div></div>
</div>
<table class="bid-bt"><caption class="sr">Hours, days on site, cost and price for each clean</caption>
<thead><tr><th scope="col">Clean</th><th scope="col">Hours</th><th scope="col">Days</th><th scope="col">Cost</th><th scope="col">Price</th></tr></thead><tbody>
<tr data-show-if="roughOn > 0"><th scope="row">Rough</th><td data-label="Hours" data-out="roughHrs" data-fmt="dec1">0</td><td data-label="Days" data-out="roughDays" data-fmt="int">0</td><td data-label="Cost" data-out="roughCost" data-fmt="money0">$0</td><td data-label="Price" data-out="roughPrice" data-fmt="money0">$0</td></tr>
<tr data-show-if="finalOn > 0"><th scope="row">Final</th><td data-label="Hours" data-out="finalHrs" data-fmt="dec1">0</td><td data-label="Days" data-out="finalDays" data-fmt="int">0</td><td data-label="Cost" data-out="finalCost" data-fmt="money0">$0</td><td data-label="Price" data-out="finalPrice" data-fmt="money0">$0</td></tr>
<tr data-show-if="touchOn > 0"><th scope="row">Touch-up</th><td data-label="Hours" data-out="touchHrs" data-fmt="dec1">0</td><td data-label="Days" data-out="touchDays" data-fmt="int">0</td><td data-label="Cost" data-out="touchCost" data-fmt="money0">$0</td><td data-label="Price" data-out="touchPrice" data-fmt="money0">$0</td></tr>
</tbody><tfoot><tr><th scope="row">Total</th><td data-label="Hours" data-out="hrs" data-fmt="dec1">0</td><td data-label="Days" data-out="days" data-fmt="int">0</td><td data-label="Cost" data-out="cost" data-fmt="money0">$0</td><td data-label="Price" data-out="price" data-fmt="money0">$0</td></tr></tfoot></table>
<ul class="lines">
<li><span>Labor, cleaner-hours times your cost</span><span data-out="labor" data-fmt="money0">$0</span></li>
<li><span>Supplies</span><span data-out="supplies" data-fmt="money0">$0</span></li>
<li><span>Travel and parking, one trip a day</span><span data-out="travel" data-fmt="money0">$0</span></li>
<li class="total"><span>Profit in the bid (<span data-pct="profitPct">0%</span> of the price)</span><span data-out="profit" data-fmt="money0">$0</span></li>
</ul>
<div class="callout warn" id="bidFixNote" hidden>A field above needs a fix. The bid shows again once it reads as a number.</div>
<div class="callout" data-show-if="checkSize > 0">Check the size: <b data-out="sizeText" data-fmt="text">0</b>.</div>
<div class="callout" data-show-if="checkPer > 0">Check your numbers: this bid works out to <b data-out="perText" data-fmt="text">$0</b> a sq ft.</div>
<div class="callout warn" data-show-if="none > 0">Type the square feet to clean, or the units and their average size.</div>
<div class="callout warn" data-show-if="noPhase > 0">Pick at least one clean: rough, final or touch-up.</div>
<div class="callout warn" data-show-if="noRate > 0">A clean in the bid has no speed. Type the square feet one cleaner does in an hour.</div>
<div class="callout warn" data-show-if="noWage > 0">Type your labor cost per cleaner-hour, or the price leaves out your crew.</div>
<div class="callout warn" data-show-if="noVisits > 0">Touch-up is in the bid with 0 visits. Type how many return visits.</div>
<div class="callout warn" data-show-if="noMargin > 0">A margin of 100% or more has no price. Use a lower margin, or switch to markup.</div>
<div class="callout warn" data-show-if="noDay > 0">Type the hours in a crew day. Until then each clean counts as one day on site, one trip.</div>
<div class="callout warn" data-show-if="flatNoRate > 0">Type your touch-up speed, so the page can check your flat price against what the visits cost you.</div>
<div class="callout" data-show-if="visitsRounded > 0">Touch-up visits are whole visits: this bid counts <b data-out="touchVisits" data-fmt="int">0</b>.</div>
<div class="callout warn" data-show-if="flatLow > 0">Your flat touch-up price is under what the visits cost you: <b data-out="touchCost" data-fmt="money0">$0</b> at your rates.</div>
</div></div>
<div class="mbar" aria-hidden="true"><span>Bid <b data-out="price" data-fmt="money0">$0</b></span><span>Per sq ft <b data-out="perSqFt" data-fmt="money3">$0</b></span></div>"""
    docf = lambda key, label, ph, wide=False: (f'<div{" class=wide" if wide else ""}><label for="{key}">{E(label)}</label>'
                                               f'<input id="{key}" type="text" autocomplete="off" placeholder="{E(ph)}"></div>')
    proposal = f"""<section class="block bid-docsec" aria-labelledby="doc-title"><h2 id="doc-title">Your one-page proposal</h2>
<p>Built from the prices above. Add your details, then print it or save it as a PDF to send to the builder. Anything you leave blank prints in [brackets] to fill by hand.</p>
<form class="bid-docform" id="bidDoc" novalidate>
{docf("bizName", "Your business name", "Your business name")}
{docf("bizContact", "Your phone and email", "Phone and email")}
{docf("builder", "Builder or general contractor", "Who the proposal is for")}
{docf("address", "Project address", "Street address")}
{docf("work", "Project", "Optional: 6-story apartment building", True)}
<div class="wide"><label for="terms">Terms</label><textarea id="terms" placeholder="Your payment terms, and how long this price holds"></textarea></div>
</form>
<div class="bid-paper" id="bidPreview"></div>
<div class="bid-acts"><button type="button" class="btn" id="bidPrintBtn">Print or save as PDF</button><small>In the print window, pick Save as PDF to email it.</small></div>
<p class="bid-note">{E(dl["sampleNote"])}</p>
</section>
<section class="block" id="get" aria-labelledby="get-title"><div class="bid-get"><div><h2 id="get-title">{E(dl["title"])}</h2><p>{E(dl["text"])}</p>
<ul>{"".join(f"<li>{E(x)}</li>" for x in dl["items"])}</ul></div>
<form action="https://app.kit.com/forms/{E(dl["kitForm"])}/subscriptions" method="post">
<label for="kitFirst">First name <span class="opt">(optional)</span></label><input id="kitFirst" name="fields[first_name]" type="text" autocomplete="given-name">
<label for="kitEmail">Email</label><input id="kitEmail" name="email_address" type="email" required autocomplete="email">
<button class="btn" type="submit">{E(dl["button"])}</button>
<small>The files open as soon as you sign up, and a link to them comes by email. Unsubscribe in one click from any email. Your email is stored with Kit, our email provider, and never sold.</small></form></div></section>"""
    g = p["guide"]
    rows = "".join(f'<tr><th scope="row">{E(a)}</th><td>{E(b)}</td><td>{"; ".join(f"<a href={chr(34)}{E(u)}{chr(34)} rel={chr(34)}noopener{chr(34)}>{E(n)}</a>" for n, u in srcs)}</td></tr>'
                   for a, b, srcs in g["rows"])
    guide = (f'<section class="block" aria-labelledby="gr-title"><h2 id="gr-title">{E(g["title"])}</h2><p>{E(g["intro"])}</p>'
             f'<table class="bid-gr"><caption class="sr">{E(g["title"])}</caption><thead><tr><th scope="col">Clean</th><th scope="col">Published range</th>'
             f'<th scope="col">Where it was published</th></tr></thead><tbody>{rows}</tbody></table>'
             + "".join(f"<p>{E(t)}</p>" for t in g["tail"]) + '</section>')
    script = f"""<script>
(function(){{var f=document.getElementById("calc"),doc=document.getElementById("bidDoc"),pv=document.getElementById("bidPreview");
/* Maths: PNF.bidPrice in assets/pnf-calc.js, the same function the area seats' bid sheet calls. */
var cb=function(k){{var e=document.getElementById("ph-"+k);return e&&e.checked?1:0;}};
var M=function(i){{i.rough=cb("rough");i.final=cb("final");i.touch=cb("touch");return PNF.bidPrice(i);}};
var val=function(id){{return document.getElementById(id).value;}};
function read(){{var v={{}};f.querySelectorAll("[data-in]").forEach(function(e){{v[e.getAttribute("data-in")]=e.value;}});return v;}}
function show(){{var u=val("measure")==="1";f.querySelector('[data-bid="sqft"]').hidden=u;f.querySelector('[data-bid="units"]').hidden=!u;
f.querySelector('[data-bid="flat"]').hidden=val("touchMode")!=="1";
["measure","touchMode"].forEach(function(id){{var s=document.getElementById(id);s.closest(".row").querySelectorAll("small[data-h]").forEach(function(h){{h.hidden=h.getAttribute("data-h")!==s.value;}});}});}}
/* a typed "$2,000", "50%" or "1.2k" reads as a number at once and is shown clean when you leave the box; whole numbers where a count is whole */
var WHOLE={{visits:1,crew:1,units:1}};
f.addEventListener("focusout",function(e){{var el=e.target;if(!el.matches||!el.matches("input[data-in]"))return;var n=PNF.parseNum(el.value);if(!isFinite(n)||el.value.trim()==="")return;
if(WHOLE[el.id])n=Math.round(n);var s=n.toLocaleString("en-US",{{maximumFractionDigits:2}});if(s!==el.value){{el.value=s;f.dispatchEvent(new Event("input",{{bubbles:true}}));}}}});
function draw(){{pv.innerHTML=PNF.bidProposal(M(read()),{{business:val("bizName"),contact:val("bizContact"),builder:val("builder"),address:val("address"),work:val("work"),terms:val("terms"),date:PNF.bidToday()}});}}
f.addEventListener("input",function(){{show();draw();}});doc.addEventListener("input",draw);
/* a field showing its error greys the results and the total says so (design round 2); 0 cleaners gets its own note */
var card=document.querySelector("#calc+.sticky .card");
function guard(){{var c=document.getElementById("crew"),cn=PNF.parseNum(c.value),low=isFinite(cn)&&Math.round(cn)<1,note=document.getElementById("crew-min");
if(low&&!note){{note=document.createElement("small");note.id="crew-min";note.className="calc-err";note.textContent="At least 1 cleaner";c.closest(".row").appendChild(note);}}
if(!low&&note)note.remove();if(low){{c.setAttribute("aria-invalid","true");c.setAttribute("aria-describedby","crew-min");}}
var bad=[].some.call(f.querySelectorAll('input[aria-invalid="true"]'),function(el){{return el.offsetParent!==null;}});
card.classList.toggle("bid-err",bad);document.body.classList.toggle("bid-err-on",bad);card.querySelector(".bid-fix").hidden=!bad;card.querySelector('.tile.key [data-out="price"]').hidden=bad;
document.getElementById("bidFixNote").hidden=!bad;
/* the greyed figures are out of date while a field is wrong: inert, so nobody tabs to or reads them */
card.querySelectorAll(".tile:not(.key),.bid-bt,.lines").forEach(function(x){{if(bad){{x.setAttribute("inert","");x.setAttribute("aria-hidden","true");}}else{{x.removeAttribute("inert");x.removeAttribute("aria-hidden");}}}});
card.querySelectorAll(".tile .val").forEach(function(v){{PNF.fitText(v,12);}});
/* a table too wide for its card shows each row as label and value pairs, so no figure wraps or runs off the card */
var bt=card.querySelector(".bid-bt");bt.classList.remove("stack");if(bt.scrollWidth>bt.parentNode.clientWidth+1)bt.classList.add("stack");}}
f.addEventListener("input",function(){{setTimeout(guard,0);}});window.addEventListener("resize",guard);
/* Ctrl+P prints the proposal too, with the same title as the Print button (assets/pnf-bid.css hides the rest for print) */
var oldTitle=document.title;window.addEventListener("beforeprint",function(){{draw();if(!document.body.classList.contains("bid-printing")){{var a=val("address").trim();document.title="Proposal"+(a?", "+a:"");}}}});
window.addEventListener("afterprint",function(){{if(!document.body.classList.contains("bid-printing"))document.title=oldTitle;}});
PNF.wire(f,M);PNF.after(f,M);window.PNF_MODEL=M;PNF.stages(f,"../e/{p["slug"]}/");show();draw();setTimeout(guard,0);
document.getElementById("bidPrintBtn").addEventListener("click",function(){{draw();PNF.bidPrint(pv.innerHTML,val("address"));}});}})();</script>"""
    return form, results + "\n<!--LC-EXTRA-->" + proposal + guide, script


PAGE_KINDS = {"bid": bid_page, "lights": lights_page, "snow": snow_page, "hood": hood_page, "missed_calls": missed_calls_page, "price_raise": price_raise_page, "lead_cost": lead_cost_page, "dd7_payout": dd7_page, "day_rate": day_rate_page, "cleaning_sqft": cleaning_sqft_page, "service": service_page, "service_sqft": service_sqft_page, "hourly": hourly_page, "cashflow": cashflow_page,
              "etsy_fees": etsy_fees_page, "craft_fair": craft_fair_page, "str_nightly": str_nightly_page,
              "debt_payoff": debt_payoff_page, "shipping_cost": shipping_cost_page,
              "reorder_point": reorder_point_page, "str_breakeven": str_breakeven_page,
              "rental_cash_flow": rental_cash_flow_page,
              "business_expense": business_expense_page, "se_tax": se_tax_page,
              "inventory_turnover": inventory_turnover_page,
              "profit_margin": profit_margin_page,
              "employer_cost": employer_cost_page,
              "startup_cost": startup_cost_page,
              "budget": budget_page,
              "profit_loss": profit_loss_page,
              "cake": cake_page,
              "unit_cost": unit_cost_page,
              "chore_split": chore_split_page,
              "client_mix": client_mix_page,
              "markup": markup_page, "handmade": handmade_page, "break_even": break_even_page}


# ---------------------------------------------------------------- permit leads pilot (coo/OPPORTUNITIES.md Case 4)
CITY_DISCLAIMER = {
    "Chicago": ("This site provides applications using data that has been modified for use from its original source, "
                "www.cityofchicago.org, the official website of the City of Chicago. The City of Chicago makes no claims as to "
                "the content, accuracy, timeliness, or completeness of any of the data provided at this site. The data provided "
                "at this site is subject to change at any time. It is understood that the data provided at this site is being "
                "used at one’s own risk."),
}
STAGES = [("PARTIAL OCCUPANCY", "Partial occupancy approved", "hot"), ("OCCUPANCY PENDING", "Partial occupancy approved", "hot"),
          ("CERTIFICATE OF OCCUPANCY ISSUED", "Occupancy certificate issued", "done"),
          ("INSPECTIONS", "Inspections under way", "mid"), ("PERMIT ISSUED", "Permit issued", "early"),
          ("NEAR FINISH", "Near finish", "hot"), ("SOME PERMITS FINALED", "Near finish", "hot"), ("WORK UNDER WAY", "Work under way", "mid")]   # Austin (stages from the City's own fields)


def is_live(p):
    """A page is public when its draft flag is off; a leads page also needs its Kit waitlist form."""
    return (not p.get("draft") and not (p.get("kind") == "leads" and not (p.get("kitForm") or p.get("checkout")))
            and not (p.get("kind") == "datapage" and not datapage_ready(p)))


def normalize_extra(slug, h1):
    """A hand-made page in site/extras.json gets the generated pages' head (own font, Open Graph image, breadcrumbs) and
    header and footer links (technical SEO check, Oct 22). Idempotent: it only rewrites the parts it owns."""
    import re
    f = os.path.join(DOCS, slug, "index.html")
    if not os.path.isfile(f):
        return
    t = open(f, encoding="utf-8").read()
    url = BASE + slug + "/"
    t = re.sub(r'<link rel="preconnect" href="https://fonts.googleapis.com">.*?display=swap" rel="stylesheet">\n?', "", t, flags=re.S)
    t = re.sub(r'<!--pnf-head-->.*?<!--/pnf-head-->', "", t, flags=re.S)
    m = re.search(r"<title>(.*?)</title>.*?<meta name=\"description\" content=\"(.*?)\"", t, flags=re.S)
    title, desc = (m.group(1), m.group(2)) if m else (h1, "")
    if len(html.unescape(title)) > 60 and title.endswith(" | ProofNotFluff"):   # same rule as HEAD (SEO audit, Oct 24)
        short = title[:-len(" | ProofNotFluff")]
        t = t.replace(f"<title>{title}</title>", f"<title>{short}</title>", 1)
        title = short
    crumb, crumb_ld = crumbs("../", [("Home", ""), (h1, None)])
    headbits = ('<!--pnf-head--><meta name="color-scheme" content="light dark">'
                f'<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:type" content="website">'
                f'<meta property="og:url" content="{url}">{og_tags(url)}<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">'
                '<link rel="icon" href="../assets/favicon-48.png" sizes="48x48" type="image/png"><link rel="apple-touch-icon" href="../assets/apple-touch-icon.png">'
                '<meta name="theme-color" content="#f3f1ec" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#12161f" media="(prefers-color-scheme: dark)">'
                '<link rel="preload" href="../assets/fonts/poppins-700.woff2" as="font" type="font/woff2" crossorigin>'
                f'{ld_tags(crumb_ld)}<!--/pnf-head-->')
    t = t.replace('<link rel="stylesheet" href="../assets/pnf.css">', headbits + '<link rel="stylesheet" href="../assets/pnf.css">', 1)
    t = re.sub(r'<nav class="top"[^>]*>.*?</nav>', nav_html("../"), t, count=1, flags=re.S)
    t = re.sub(r'<!--pnf-fnav-->.*?<!--/pnf-fnav-->', "", t, flags=re.S)
    t = t.replace('<footer><div class="wrap">', '<footer><div class="wrap"><!--pnf-fnav-->' + foot_nav("../") + '<!--/pnf-fnav-->', 1)
    if 'class="skip"' not in t:
        t = t.replace("<body>", '<body><a class="skip" href="#main">Skip to content</a>', 1)
    t = re.sub(r"<main( class=\"wrap\")?>", '<main class="wrap" id="main">', t, count=1)
    # the visible trail matches the BreadcrumbList above (SEO audit, Oct 24, 2026)
    t = re.sub(r'<!--pnf-crumb-->.*?<!--/pnf-crumb-->', "", t, flags=re.S)
    t = t.replace('<main class="wrap" id="main">', '<main class="wrap" id="main"><!--pnf-crumb-->' + crumb + '<!--/pnf-crumb-->', 1)
    t = t.replace("<p>Made by ProofNotFluff.</p>", "<p>Made by ProofNotFluff with AI assistance, reviewed and tested by the shop owner.</p>")
    t = t.replace("and a copy comes by email.", "and a link to it comes by email.")
    t = t.replace("IRS news release IR-2026-29)", "IRS Standard Mileage Rates page and Internal Revenue Bulletin 2026-29)")   # copy check, Oct 22
    open(f, "w", encoding="utf-8").write(t)


def live_extras():
    """Hand-made pages listed in site/extras.json (the free cheat sheet sign-up page, Oct 17): this script never writes
    them, but once a page's committed docs/<slug>/index.html carries no robots meta it joins the sitemap, gets a card on
    the free calculators index and a link card on each page named in its "from" list. Until then it stays off all three."""
    f = os.path.join(ROOT, "site", "extras.json")
    if not os.path.exists(f):
        return []
    out = []
    for x in json.load(open(f, encoding="utf-8")).get("pages", []):
        page = os.path.join(DOCS, x["slug"], "index.html")
        if os.path.isfile(page) and 'name="robots"' not in open(page, encoding="utf-8").read():
            out.append(x)
    return out


def extra_cards(slug):
    """Link cards on a generated page for the live hand-made pages that name it in their "from" list."""
    cards = "".join(f'<a class="card" href="../{E(x["slug"])}/"><h3>{E(x["h1"])}</h3><p>{E(x["card"])}</p></a>'
                    for x in live_extras() if slug in x.get("from", []))
    return f'<section class="block"><div class="tools one">{cards}</div></section>' if cards else ""


def png_size(path):
    """(width, height) of a PNG from its header."""
    import struct
    with open(path, "rb") as f:
        head = f.read(24)
    return struct.unpack(">II", head[16:24])


def webp_of(rel_png, width=None, quality=82):
    """A WebP copy of a committed PNG for the page hero (SEO and speed audit, Oct 24, 2026: the PNGs ran 129 to 388 KB).
    The file name carries the PNG's hash, so it is written once per screenshot and the build stays byte for byte the same
    (tools/check_repo.py site-sync); older copies of the same screenshot and width are removed. Returns (path under docs/, w, h)."""
    import hashlib, glob, re
    src = os.path.join(DOCS, rel_png)
    h = hashlib.sha1(open(src, "rb").read()).hexdigest()[:10]
    stem, tag = rel_png[:-4], (f"-{width}" if width else "")
    out_rel = f"{stem}.{h}{tag}.webp"
    out = os.path.join(DOCS, out_rel)
    w0, h0 = png_size(src)
    w, hh = (width, round(h0 * width / w0)) if width and w0 > width else (w0, h0)
    if not os.path.isfile(out):
        from PIL import Image
        im = Image.open(src).convert("RGB")
        if (w, hh) != (w0, h0):
            im = im.resize((w, hh), Image.LANCZOS)
        im.save(out, "WEBP", quality=quality, method=6)
        mine = re.compile(r"^[0-9a-f]{10}" + re.escape(tag) + r"$")
        for old in glob.glob(os.path.join(DOCS, stem + ".*.webp")):
            mid = os.path.basename(old)[len(os.path.basename(stem)) + 1:-5]
            if old != out and mine.match(mid):
                os.remove(old)
    return out_rel, w, hh


def money(v, spell_billion=False, bil2=False):
    """One money rule on the leads pages (design director, Oct 17): $770K under $1M, $2.0M under $100M, whole millions
    from $100M up; "billion" is spelled out only in the hero tile. bil2 (Austin, design director Oct 18): $1 billion and up
    always reads "$1.57 billion", two decimals, everywhere."""
    d = max(0, int(float(v or 0) + 0.5))            # whole dollars; halves round up on integers, never on floats
    up = lambda n, unit: (2 * n + unit) // (2 * unit)   # n / unit rounded half up
    if bil2 and up(d, 10_000_000) >= 100:
        t = up(d, 10_000_000)
        return f"${t // 100}.{t % 100:02d} billion"
    if d >= 1_000_000_000 and spell_billion:
        t = up(d, 100_000_000)
        return f"${t // 10}.{t % 10} billion"
    if up(d, 100_000) >= 1000:                          # $99.95M and up: whole millions
        return f"${up(d, 1_000_000):,}M"
    if up(d, 1000) >= 1000:                             # $999,500 and up: millions to one decimal
        t = up(d, 100_000)
        return f"${t // 10}.{t % 10}M"
    return f"${up(d, 1000):,}K"


def nice_date(iso):
    """Oct 14, 2026. A timestamp with a zone is shown as the Chicago calendar date."""
    import datetime as _dt
    try:
        if "T" in iso and (iso.endswith("Z") or "+" in iso[10:] or "-" in iso[10:]):
            from zoneinfo import ZoneInfo
            d = _dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(ZoneInfo("America/Chicago")).date()
        else:
            d = _dt.date.fromisoformat(iso[:10])
    except ValueError:
        return iso
    return d.strftime("%b ") + str(d.day) + d.strftime(", %Y")


def stage(m):
    up = (m or "").upper()
    for key, label, cls in STAGES:
        if key in up:
            return label, cls
    return (m or "Open").capitalize(), "mid"


def project_card(x, pill=True, city="Chicago", permit_label="Permit", bil2=False, sep=" · "):
    lab, cls = stage(x.get("milestone"))
    gc = "; ".join(x.get("gc") or [])
    units = (f'{sep}{x["units"]:,} home{"s" if x["units"] != 1 else ""}' if x.get("units") else
             f'{sep}{x["sleeping"]:,} sleeping units' if x.get("sleeping") else "")   # shelter rooms are never homes (holdout round 6)
    area = x.get("communityArea") or city
    pill_html = f'<p class="ld-pill s-{cls}">{E(lab)}</p>' if pill else ""
    return (f'<article class="ld-proj" data-type="{"new" if x["type"].startswith("New") else "ren"}" data-area="{E(area)}">{pill_html}'
            f'<div class="ld-ptop"><span class="ld-cost">{money(x["cost"], bil2=bil2)}</span><span class="ld-type">{E(x["type"])}{units}</span></div>'
            f'<p class="ld-scope"><span class="ld-scl">City description</span>{E((x["scope"] or "")[:1].upper() + (x["scope"] or "")[1:])}</p>'
            f'<dl class="ld-meta{" wide" if len(permit_label) > 7 else ""}"><div><dt>Builder</dt><dd>{E(gc)}</dd></div>'
            f'<div><dt>Where</dt><dd>{E(x.get("address") or "").replace(" more)", "&nbsp;more)") if sep == ", " else E(x.get("address") or "")},{"&nbsp;" if str(area).isdigit() else " "}{E(area)}</dd></div>'
            f'<div><dt>{E(permit_label)}</dt><dd>{E(str(x.get("permit") or ""))}, issued {E(nice_date(x.get("issued", "")))}</dd></div></dl></article>')


LOCK = ('<svg class="ld-lock" viewBox="0 0 24 24" width="40" height="40" aria-hidden="true" focusable="false"><rect x="4.5" y="10.5" width="15" height="10" rx="2.2" '
        'fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M8 10.5V7.8a4 4 0 0 1 8 0v2.7" fill="none" stroke="currentColor" stroke-width="1.6"/>'
        '<circle cx="12" cy="15.3" r="1.4" fill="currentColor"/></svg>')


def window_months(d):
    """The sample's window as the tile says it ("24 months" for Chicago's 730 days, "12 months" for 365)."""
    import datetime as _dt
    w = d.get("window") or {}
    try:
        days = (_dt.date.fromisoformat(w["to"][:10]) - _dt.date.fromisoformat(w["from"][:10])).days
    except (KeyError, TypeError, ValueError):
        return "12 months"
    m = round(days / 30.4)
    return f"{m} months" if abs(m * 30.4 - days) <= 4 else f"{days} days"


def odd_note(c):
    """Austin's footnote on valuations filed a few dollars over a round figure, from the list's own examples (design round 3)."""
    odd = list(c.get("oddCosts") or [])[:2]
    return (" A few valuations end in a stray digit, such as " + " and ".join(f"${v:,}" for v in odd)
            + ": that is the figure the City filed, shown as filed.") if odd else ""


def leads_page_html(p):
    url = BASE + p["slug"] + "/"
    rel = "../"
    M = lambda v, sb=False: money(v, sb, bool(p.get("billions2")))
    d = json.load(open(os.path.join(ROOT, p["data"]), encoding="utf-8"))
    c, src = d["counts"], d["source"]
    kept, cost = c["kept"], c["keptCost"]
    new_n = c.get("keptByType", {}).get("New construction", 0)
    near = d.get("nearFinish", [])
    n_near = c.get("nearFinish", len(near))
    n_big = len(d["projects"])
    asof = nice_date(src["fetchedAt"])   # the Chicago date of the pull, the same date the members' pages and workbook print
    price = E(str(p["price"]))
    checkout = p.get("checkout")
    # funnel (Todd, Oct 22, 7:57 pm): a Gumroad free trial and the free Monday email, each switched on by its own key
    # ("trialDays", "mondayForm") only after Todd turns the trial on in Gumroad and makes the Kit forms
    trial = int(p.get("trialDays") or 0) if checkout else 0
    buy_label = f"Start your {trial}-day free trial" if trial else f"Get the full list: ${price} a month"
    # per-city wording (Austin, Oct 17): every key is optional and defaults to the Chicago page's words
    city = p["city"]
    card = lambda x, pill=True: project_card(x, pill, city, p.get("permitLabel", "Permit"), bool(p.get("billions2")), p.get("metaSep", " · "))
    near_title = p.get("nearTitle", "Partial occupancy approved")
    near_sub = p.get("nearSub", "partial occupancy approved")
    near_text = p.get("nearText", "The City has approved temporary or partial occupancy on these projects, so a final clean is close.")
    area_word, area_all, area_filter = (p.get("areaWord", "Neighborhood"), p.get("areaAll", "All neighborhoods"),
                                        p.get("areaFilter", "a neighborhood filter"))

    def buy(cls="btn ld-btnbig", label=buy_label):
        return f'<a class="{cls}" href="{E(checkout)}" rel="noopener">{label}</a>' if checkout else ""

    # hero: two lines of promise, then the price and the action on the first screen (design director, Oct 17)
    # near finish first (Todd, Oct 24, "5 yes", from the Kimi audit): lead with the jobs closest to a final clean when
    # there are enough of them to sell on; below the floor the page keeps the total-projects lede
    lead_near = bool(p.get("leadNear")) and n_near >= int(p.get("leadNearMin", 5))
    if lead_near:
        lede = (f'{n_near:,} big {E(p["city"])} projects have {E(p.get("nearLede", near_sub))}, so a final clean is close. You get the builder on each, '
                f'and on all {kept:,} open apartment and commercial projects of $500,000 or more'
                + (" in the areas no seat holder has taken" if c.get("heldAreas") else "") + f'. {E(p["lede"])}')
    else:
        lede = (f'{kept:,} open apartment and commercial projects of $500,000 or more in {E(p["city"])}, about {M(cost, True)} {"in City valuation" if p.get("costLabel") == "Valuation" else "of work"}, '
                f'and the builders running them. {E(p["lede"])}')
    if checkout:   # the free sample first, then subscribe (store design, Oct 22)
        hero_act = (f'<div class="ld-heroact" id="ldHeroCta"><a class="btn ld-btnbig" href="{"#near" if near else "#sample"}">See this week\'s free sample</a>'
                    + (f'<a class="ld-textlink ld-trialbtn" href="{E(checkout)}" rel="noopener">Try {trial} days free, then ${price} a month</a></div>'
                       '<p class="ld-heronote">Card at checkout, nothing charged for 7 days. No lock-in, cancel any time.</p>'
                       .replace("7 days", f"{trial} days") if trial else
                       f'<a class="ld-textlink" href="{E(checkout)}" rel="noopener">Subscribe, ${price} a month</a></div>'
                       '<p class="ld-heronote">New list every Monday. No lock-in, cancel any time.</p>'))
    elif p.get("kitForm"):
        hero_act = '<div class="ld-heroact" id="ldHeroCta"><a class="ld-textlink" href="#ldCta">Join the waitlist</a></div>'
    else:   # before launch with no waitlist form: no action that leads nowhere (design director, Oct 18)
        hero_act = f'<p class="ld-heronote" id="ldHeroCta">Planned price: ${price} a month, new list every Monday. Not on sale yet.</p>'
    t_open = f'<div class="tile{"" if lead_near else " key"}"><div class="lab">Open projects</div><div class="val">{kept:,}</div><div class="sub">issued in the last {window_months(d)}, still&nbsp;open</div></div>'
    t_near = f'<div class="tile{" key" if lead_near else ""}"><div class="lab">Near finish</div><div class="val">{n_near:,}</div><div class="sub">{E(near_sub)}</div></div>'
    tiles = (f'<div class="tiles ld-tiles">' + (t_near + t_open if lead_near else t_open) +
             f'<div class="tile"><div class="lab">{E(p.get("costLabel", "Reported cost"))}</div><div class="val">{M(cost, True)}</div><div class="sub">{E(p.get("costSub", "as filed with the City"))}</div></div>'
             f'<div class="tile"><div class="lab">New buildings</div><div class="val">{new_n:,}</div><div class="sub">at least {c.get("keptUnits", 0):,} new {E(p.get("unitsWord", "apartments"))}</div></div>'
             + ("" if lead_near else t_near) + '</div>'
             f'<p class="asof">The City\'s own public permit records, cleaned and sorted, with the builder on each. City data as of {E(asof)}. Refreshed every Monday.</p>')

    # near finish: the most valuable segment for a final clean, so the free page shows 2 and holds the rest back (owner, Oct 17)
    near_html = ""
    if near:
        show = near[:2]
        held = max(0, n_near - len(show))
        held_html = ""
        if held:
            noun = "project is" if held == 1 else "projects are"
            held_html = (f'<div class="ld-held">{LOCK}<p class="ld-heldtxt"><b>{held:,} more near-finish {noun} in the full list</b>'
                         '<span>With the builder, address and permit for each, every Monday.</span></p>'
                         f'{buy("btn ld-btnbig") if checkout else ""}</div>')
        near_html = (f'<section class="block" id="near"><h2>{E(near_title)}</h2>'
                     f'<p>{E(near_text)} '
                     + (f'Here are {len(show)} of the {n_near:,} on this week\'s list.' if len(show) < n_near else
                        "It is the only one on this week's list." if n_near == 1 else f"Both are on this week's list." if n_near == 2 else
                        f"All {n_near} are on this week's list.") + '</p>'
                     f'<div class="ld-list">{"".join(card(x, pill=False) for x in show)}{held_html}</div></section>')

    gcs = "".join(f'<li><span class="ld-gname">{E(g["name"])}</span><span class="ld-gn">{g["projects"]}<span class="ld-gu"> open jobs</span></span>'
                  f'<span class="ld-gv">{M(g["cost"])}</span></li>' for g in c.get("topGCs", [])[:10])
    gc_more = (f'<p class="ld-gmore">The full list ranks every builder with open work. <a href="{E(checkout)}" rel="noopener">'
               + (f'Try it free for {trial} days, then ${price} a month' if trial else f'Get it for ${price} a month') + '</a>.</p>'
               if checkout else "")
    gc_html = ('<section class="block"><h2>Builders with the most big jobs open</h2>'
               '<p>Counted from permits where the business is listed as general contractor.</p>'
               f'<ol class="ld-gcs"><li class="ld-ghead"><span>Builder</span><span>Open jobs</span><span>{"Valuation" if p.get("costLabel") == "Valuation" else "Work"}</span></li>'
               f'{gcs}</ol>{gc_more}</section>')

    areas = sorted({x.get("communityArea") for x in d["projects"] if x.get("communityArea")})
    opts = "".join(f'<option value="{E(a)}">{E(a)}</option>' for a in areas)
    big_line = (f'The {n_big} biggest of {kept:,} open projects. Members get all {kept:,}, with {area_filter} and near-finish and new tabs, plus the Excel file.')
    big_html = ('<section class="block" id="sample"><h2>Biggest open projects</h2>'
                '<div class="ld-filter" role="group" aria-label="Filter projects">'
                '<button type="button" class="ld-chip" aria-pressed="true" data-f="all">All</button>'
                '<button type="button" class="ld-chip" aria-pressed="false" data-f="new">New buildings</button>'
                f'<button type="button" class="ld-chip" aria-pressed="false" data-f="ren">{E(p.get("renLabel", "Renovations"))}</button>'
                f'<label class="ld-area"><span class="sr">{E(area_word)}</span><select id="ldArea"><option value="">{E(area_all)}</option>{opts}</select></label></div>'
                f'<p class="ld-count" id="ldCount" aria-live="polite" data-all="{E(big_line)}">{E(big_line)}</p>'
                f'<div class="ld-list ld-big" id="ldList">{"".join(card(x).replace("<article ", "<article data-x " if i >= 9 else "<article ", 1) for i, x in enumerate(d["projects"]))}</div>'
                + (f'<p class="ld-showall"><button type="button" class="st-btn2" id="ldAll" aria-controls="ldList" aria-expanded="false">Show all {n_big} in this sample</button></p>'  if n_big > 9 else "")
                + '<p class="ld-empty" id="ldEmpty" hidden>No projects in this sample match. The weekly list covers every open project.</p>'
                + (f'<div class="ld-after"><p>That is the top {n_big}. The full list has all {kept:,}, closest to a final clean first, with {area_filter}.</p>{buy()}</div>' if checkout else "")
                + '</section>')
    drafts = {x["slug"] for x in PAGES_ALL} - {x["slug"] for x in PAGES_LIVE}   # a link to a draft page waits until it is live
    links = "".join(f'<li><a href="{rel}{E(l[0])}/">{E(l[1])}</a></li>' for l in p.get("links", []) if l[0] not in drafts)
    method = ('<section class="block"><h2>How to use this list</h2>' + "".join(f"<p>{E(x)}</p>" for x in p["method"])
              + (f'<p>Price the work before you call:</p><ul class="qa-rel">{links}</ul>' if links else "") + "</section>")
    shots = ""
    sdir = p.get("shotsDir", "leads")   # each city's own screenshots (Austin: docs/assets/leads/austin/, tools/leads_check.py --capture)
    shot_f = [os.path.join(DOCS, "assets", sdir, f) for f in ("members-list.png", "workbook.png")]
    shots_ok = all(os.path.isfile(f) for f in shot_f)
    phone_f = os.path.join(DOCS, "assets", sdir, "workbook-phone.png")   # a readable crop for phones, when the city has one
    lphone_f = os.path.join(DOCS, "assets", sdir, "members-list-phone.png")   # the app on a phone, when the city has one (design round 3)
    if shots_ok and (checkout or p.get("shotsDir")):   # real screenshots of the paid product, made from the members' app and workbook
        (w1, h1), (w2, h2) = (png_size(f) for f in shot_f)
        alt1 = p.get("shotAltApp", "The members' app: every open project with the reported cost, address, builder and stage, filters for stage, community area, cost and building type, CSV export and a map of the projects")
        alt2 = p.get("shotAltBook", "The Excel file: the near finish tab with address, reported cost and builder columns, and a filter arrow on every column")
        shots = ('<section class="block ld-shots"><h2>What members get</h2>'
                 '<p>The same data as this page, every open project instead of a sample, in a members\' app and an Excel file.</p>'
                 '<div class="ld-shotgrid">'
                 f'<figure class="ld-shot">'
                 + (f'<picture><source media="(max-width:600px)" srcset="{rel}assets/{sdir}/members-list-phone.png" width="{png_size(lphone_f)[0]}" height="{png_size(lphone_f)[1]}">'
                    if os.path.isfile(lphone_f) else "")
                 + f'<img src="{rel}assets/{sdir}/members-list.png" width="{w1}" height="{h1}" loading="lazy" decoding="async" '
                 f'alt="{E(alt1)}">' + ('</picture>' if os.path.isfile(lphone_f) else "") +
                 '<figcaption>The members\' app, updated every Monday</figcaption></figure>'
                 f'<figure class="ld-shot">'
                 + (f'<picture><source media="(max-width:600px)" srcset="{rel}assets/{sdir}/workbook-phone.png" width="{png_size(phone_f)[0]}" height="{png_size(phone_f)[1]}">'
                    if os.path.isfile(phone_f) else "")
                 + f'<img src="{rel}assets/{sdir}/workbook.png" width="{w2}" height="{h2}" loading="lazy" decoding="async" alt="{E(alt2)}">'
                 + ('</picture>' if os.path.isfile(phone_f) else "") +
                 f'<figcaption>{E(p.get("shotCapBook", "The Excel file, filters on every column"))}</figcaption></figure></div></section>')
    monday = p.get("mondayForm") if checkout else None
    if monday:   # the free Monday email (email/M1-MONDAY.md): its own double opt-in Kit form, never the old waitlist
        form = (f'<form class="ld-form" action="https://app.kit.com/forms/{E(monday)}/subscriptions" method="post">'
                '<label for="ldEmail">Email</label><div class="ld-frow"><input id="ldEmail" name="email_address" type="email" required autocomplete="email" placeholder="you@company.com">'
                '<button class="btn" type="submit">Send me Monday\'s jobs</button></div></form>')
    elif p.get("kitForm"):
        form = (f'<form class="ld-form" action="https://app.kit.com/forms/{E(p["kitForm"])}/subscriptions" method="post">'
                '<label for="ldEmail">Email</label><div class="ld-frow"><input id="ldEmail" name="email_address" type="email" required autocomplete="email" placeholder="you@company.com">'
                '<button class="btn" type="submit">Join the waitlist</button></div></form>')
    else:
        form = '<p><span class="btn soon" aria-disabled="true">Waitlist opens soon</span></p>'
    if checkout:   # the paid weekly list is on sale (Todd, Oct 17, 3:18 pm: "Link the leads checkout on the site.")
        form = form.replace("Join the waitlist", "Keep me posted")
        cta_html = ('<section class="block" id="ldCta"><div class="cta ld-cta ld-buy"><div>'
                    f'<h2>{E(p["cta"]["title"])}</h2><p>{E(p["cta"]["text"])}</p>'
                    f'<p class="ld-buybtn">{buy()}</p>'
                    + (f'<p class="ld-secure">Secure checkout by Gumroad. Your card goes in at checkout and nothing is charged for {trial} days. '
                       f'Then it is ${price} a month until you cancel. Cancel in your Gumroad library before day {trial} and you pay nothing. '
                       f'<a href="{rel}refunds/">Refunds and cancelling</a></p></div>' if trial else
                       f'<p class="ld-secure">Secure checkout by Gumroad. Cancel any time. <a href="{rel}refunds/">Refunds and cancelling</a></p></div>')
                    + (f'<div class="ld-later" id="ldMonday"><p><b>Not ready to pay?</b> Get 2 or 3 new jobs from this week\'s list, free by plain email, on the Mondays there are new ones.</p>{form}'
                       f'<small class="ld-note">Kit, our email provider, asks you to confirm first. Unsubscribe in one click. Never sold. <a href="{rel}privacy/">Privacy</a></small></div>' if monday else
                       f'<div class="ld-later"><p><b>Not ready yet?</b> Leave your email and we will let you know when the list adds new cities or features.</p>{form}'
                       '<small class="ld-note">Unsubscribe in one click. Your email is stored with Kit, our email provider, and never sold.</small></div>' if p.get("kitForm") else "")
                    + '</div></section>')
        sbar = (f'<div class="ld-sbar" id="ldBar" aria-hidden="true"><div class="wrap"><p><b>{trial} days free</b><span> · then ${price} a month</span></p>'
                f'<a class="btn" href="{E(checkout)}" rel="noopener" tabindex="-1">Try free</a></div></div>' if trial else
                f'<div class="ld-sbar" id="ldBar" aria-hidden="true"><div class="wrap"><p><b>${price} a month</b><span> · <span class="ld-sbl">full list </span>every Monday</span></p>'
                f'<a class="btn" href="{E(checkout)}" rel="noopener" tabindex="-1">Subscribe</a></div></div>')
    elif not p.get("kitForm"):   # before launch, no waitlist: the offer and the planned price, no form (design director, Oct 18)
        cta_html = ('<section class="block" id="ldCta"><div class="cta ld-cta ld-solo"><div>'
                    f'<h2>{E(p["cta"]["title"])}</h2><p>{E(p["cta"]["text"])}</p>'
                    f'<p class="ld-price">Planned price: ${price} a month. Not on sale yet: this page shows the checkout once the list opens.</p></div></div></section>')
        sbar = ""
    else:
        cta_html = ('<section class="block" id="ldCta"><div class="cta ld-cta"><div>'
                    f'<h2>{E(p["cta"]["title"])}</h2><p>{E(p["cta"]["text"])}</p>'
                    f'<p class="ld-price">Planned price: ${price} a month. Joining the waitlist is free and commits you to nothing.</p></div>'
                    f'<div>{form}<small class="ld-note">We email you when the weekly list opens. Unsubscribe in one click. Your email is stored with Kit, our email provider, and never sold.</small></div></div></section>')
        sbar = ""
    faq = list(p["faq"])
    if c.get("heldAreas"):   # Legal desk, Oct 26, fix 11: the shared list says plainly which areas it leaves out
        faq = [[q, a.replace("the weekly list covers every permit that passes the filter.",
                             "the weekly list covers every permit that passes the filter in the areas no seat holder has taken.")] for q, a in faq]
        faq.append(["Which areas are held?", "The area seats section on this page shows them: " + ", ".join(c["heldAreas"])
                    + ". Their projects are not on this list."])
    if trial or monday:   # one plain answer on the two free ways in (email/M1-MONDAY.md)
        ways = ([f"The free Monday email sends 2 or 3 new jobs from the week's list on the Mondays there are new ones."] if monday else []) + (
            [f"Or start a {trial}-day free trial on Gumroad: your card goes in at checkout, nothing is charged for {trial} days, "
             f"then it is ${price} a month until you cancel. Cancel before day {trial} and you pay nothing."] if trial else [])
        faq.append(["Can I try it before I pay?", "Yes. " + " ".join(ways).replace("Yes. Or start", "Yes. Start")])
    crumb, crumb_ld = crumbs(rel, [("Home", ""), ("Shop", "shop/"), (p["h1"], None)])
    # area seats (Todd, Oct 26, 2026; tools/area_site.py): shown only once a seat has its checkout, or in a preview build
    seats_block = ""
    if p.get("areaSeats"):
        import area_site
        sp = area_site.seats_spec(p)
        if sp:
            seats_block = f'<style>{area_site.SEATS_CSS}</style>' + area_site.seats_html(p, sp, rel)
    # store v2 (design review, Oct 24, 2026): the members' app beside the promise on wide screens, so the product is on the
    # first screen; a WebP copy keeps it light, loaded first because it is the largest thing above the fold
    heroshot = ""
    if shots and os.path.isfile(shot_f[0]):
        wp, ww, wh = webp_of(os.path.relpath(shot_f[0], DOCS).replace(os.sep, "/"))
        heroshot = (f'<figure class="ld-heroshot"><img src="{rel}{wp}" width="{ww}" height="{wh}" fetchpriority="high" decoding="async" alt="{E(alt1)}">'
                    '<figcaption>A screen from the members\' app; its counts are from the week it was captured</figcaption></figure>')
    body = (f'{crumb}<div class="ld-herogrid{" has-shot" if heroshot else ""}"><div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{split_lede(lede)[0]}</p>{hero_act}</div>{heroshot}</div>{tiles}{lede_rest(split_lede(lede)[1])}{answer_box(p) if is_live(p) else ""}'
            f'{near_html}{gc_html}{big_html}{seats_block}{method}{shots}{cta_html}{guides_block(p["slug"], rel=rel)}{faq_block(faq)}')
    body = otp_bar(body)
    script = r"""<script>(function(){var list=document.getElementById('ldList');if(list){
var cards=[].slice.call(list.querySelectorAll('.ld-proj')),chips=[].slice.call(document.querySelectorAll('.ld-chip')),
area=document.getElementById('ldArea'),count=document.getElementById('ldCount'),empty=document.getElementById('ldEmpty'),f='all';
function run(){var a=area.value,n=0;cards.forEach(function(c){var ok=(f==='all'||c.dataset.type===f)&&(!a||c.dataset.area===a);c.hidden=!ok;if(ok)n++});
count.textContent=(f==='all'&&!a)?count.dataset.all:'Showing '+n+' of '+cards.length+' projects in this free sample.';empty.hidden=n>0}
chips.forEach(function(b){b.addEventListener('click',function(){f=b.dataset.f;chips.forEach(function(x){x.setAttribute('aria-pressed',String(x===b))});run()})});
area.addEventListener('change',run);run();
var all=document.getElementById('ldAll'),lab=all?all.textContent:'';if(all){all.addEventListener('click',function(){var open=all.getAttribute('aria-expanded')!=='true';
list.classList.toggle('all',open);all.setAttribute('aria-expanded',String(open));all.textContent=open?'Show the top 9':lab;
count.textContent=open?'Showing all '+cards.length+' projects in this free sample.':count.dataset.all;if(open){var c=cards[9];if(c){c.tabIndex=-1;c.focus()}}})}
chips.concat([area]).forEach(function(x){x.addEventListener(x===area?'change':'click',function(){var on=f!=='all'||area.value;list.classList.toggle('all',!!on||(all&&all.getAttribute('aria-expanded')==='true'));if(all)all.parentNode.hidden=!!on})})}
var bar=document.getElementById('ldBar'),hero=document.getElementById('ldHeroCta'),cta=document.getElementById('ldCta');
if(!bar||!hero||!cta||!('IntersectionObserver' in window))return;
var hv=true,cv=false,link=bar.querySelector('a');
function set(){var on=!hv&&!cv;bar.classList.toggle('on',on);bar.setAttribute('aria-hidden',String(!on));link.tabIndex=on?0:-1}
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.target===hero)hv=e.isIntersecting;else cv=e.isIntersecting});set()});
io.observe(hero);io.observe(cta)})();</script>"""
    if seats_block:   # the $29 sticky bar steps aside while the area seats are on screen (design director, Oct 26)
        script = (script.replace("var hv=true,cv=false,link=bar.querySelector('a');", "var hv=true,cv=false,av=false,link=bar.querySelector('a'),seats=document.getElementById('areas');")
                  .replace("var on=!hv&&!cv;", "var on=!hv&&!cv&&!av;")
                  .replace("if(e.target===hero)hv=e.isIntersecting;else cv=e.isIntersecting", "if(e.target===hero)hv=e.isIntersecting;else if(e.target===seats)av=e.isIntersecting;else cv=e.isIntersecting")
                  .replace("io.observe(hero);io.observe(cta)})", "io.observe(hero);io.observe(cta);if(seats)io.observe(seats)})"))
    prod = next((x for x in store_products() if x["key"] == p["slug"]), None)
    ld = ld_tags({"@context": "https://schema.org", "@type": "FAQPage",
                  "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
                 crumb_ld, product_ld(prod, url) if prod else None, page_ld(p, url) if is_live(p) else None)
    robots = "" if is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    foot = (f'</main>\n<footer><div class="wrap">{foot_nav(rel)}'
            f'<p>Source: {E(src["name"])} ({E(src["url"])}), City data as of {E(asof)}, the day it was pulled. {E(src["modified"])} '
            f'{E(p.get("costNote", "Reported cost is the figure filed with the City, not a contract value."))}{E(odd_note(c))} No contractor named here has endorsed or works with ProofNotFluff. '
            'Public information for planning sales calls; not legal or business advice and no promise of work.</p>'
            f'<p>{E(p.get("disclaimer") or CITY_DISCLAIMER.get(p["city"], ""))}</p>'
            f'<p>Made by ProofNotFluff with AI assistance from public City data.{" The Monday email form sends your email address to Kit." if monday else " The waitlist form sends your email address to Kit." if p.get("kitForm") else ""} The page counts visits with Cloudflare Web Analytics, which sets no cookies.</p>'
            f'</div></footer>\n{sbar}\n{script}\n</body></html>')
    bodycls = ' class="ld-page' + (' has-sbar' if sbar else '') + '"'
    return (HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=SHOP, ld=ld, bodycls=bodycls,
                        robots=robots, analytics=analytics_tag()) + body + foot)


def split_lede(lede):
    """Store v2 review round 4 (Oct 24, 2026): on phones the lead pages showed a 9-line lede before any number. The hero
    keeps the first sentence; the rest of the same words follows the stat tiles (lede_rest). Nothing is cut."""
    import re
    m = re.search(r"\.\s+(?=[A-Z0-9$])", lede)
    if not m or m.end() >= len(lede) - 1:
        return lede, ""
    return lede[:m.start() + 1], lede[m.end():]


def lede_rest(rest):
    return f'<p class="lede-rest">{rest}</p>' if rest else ""


OTP_LABELS = {"Partial occupancy approved": "Near finish", "Builders with the most big jobs open": "Builders", "Biggest open projects": "Biggest projects",
              "This week's free sample": "Free sample", "This week's sample": "Sample", "How to use this list": "How to use it",
              "What members get": "What you get", "Questions": "FAQ", "New licenses by trade, last 30 days": "By trade"}


def otp_bar(body):
    """Store v2 round 2 (Oct 24, 2026): a sticky "on this page" bar on the long lead pages, so a visitor on a phone can jump
    to the sample, the seat or the price, and sees where they are (assets/pnf-ui.js marks the section in view). Sections
    without an id get one from their heading; Guides stays out of the bar."""
    import re
    links, used = [], set()
    def tag(m):
        attrs, title = m.group(1), html.unescape(m.group(2))
        idm = re.search(r'id="([^"]+)"', attrs)
        sid = idm.group(1) if idm else "s-" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40]
        if title not in ("Guides", "Related pages", "Sources") and sid not in used:
            used.add(sid)
            links.append((sid, OTP_LABELS.get(title, title if len(title) <= 24 else title[:22].rsplit(" ", 1)[0])))
        return m.group(0) if idm else m.group(0).replace("<section ", f'<section id="{sid}" ', 1)
    body = re.sub(r'<section (class="block[^"]*"[^>]*)><h2[^>]*>(.*?)</h2>', tag, body)
    if 'id="seat"' in body:   # the pest seat sits after the sample
        at = next((i for i, (s, _) in enumerate(links) if s == "sample"), -1)
        links.insert(at + 1, ("seat", "Pest seat"))
    if 'id="areas"' in body:   # the area seats offer (tools/area_site.py) sits after the sample, before How to use it
        at = next((i for i, (s, _) in enumerate(links) if s.startswith("s-how")), len(links))
        links.insert(at, ("areas", "Area seats"))
    if 'id="ldCta"' in body:
        links.insert(len(links) - (1 if links and links[-1][1] == "FAQ" else 0), ("ldCta", "Pricing"))
    if len(links) < 3:
        return body
    nav = ('<nav class="otp" aria-label="On this page"><div class="otp-in">'
           + "".join(f'<a href="#{s}">{E(l)}</a>' for s, l in links) + '</div></nav>')
    j = min([k for k in (body.find('<section class="block'), body.find('<section id="')) if k >= 0], default=-1)
    return body[:j] + nav + body[j:] if j >= 0 else body


def page_html(p):
    if p.get("kind") == "leads":
        return leads_page_html(p)
    if p.get("kind") == "restleads":   # Chicago Restaurant Inspection Leads (tools/rest_site.py)
        import rest_site
        return rest_site.page_html(p)
    if p.get("kind") == "licleads":    # Chicago New Business Licenses (tools/lic_site.py)
        import lic_site
        return lic_site.page_html(p)
    if p.get("kind") == "rodents":     # Chicago rat complaints, the free weekly 311 page (tools/rodents_site.py)
        import rodents_site
        return rodents_site.page_html(p)
    if p.get("kind") == "tradesnews":  # Chicago Trades News, the free weekly brief (tools/news_site.py; Todd, Oct 27, 2026)
        import news_site
        return news_site.page_html(p)
    if p.get("kind") == "newin":       # New in Chicago, the free traffic page (tools/newin_site.py)
        import newin_site
        return newin_site.page_html(p)
    if p.get("kind") == "agentkit":    # Unattended Agent Kit offer and waitlist, a draft until Todd's go (tools/agentkit_site.py)
        import agentkit_site
        return agentkit_site.page_html(p)
    if p.get("kind") == "question":    # question pages for the lead products (tools/question_site.py)
        import question_site
        return question_site.page_html(p)
    if p.get("kind") == "datapage":    # a free Chicago data page with its own module (coo/PARALLEL_BUILDS.md)
        return kind_module(p).page_html(p)
    url = BASE + p["slug"] + "/"
    rel = "../"
    form, results, script = PAGE_KINDS[p["kind"]](p)
    results, _, after_grid = results.partition("\n<!--LC-EXTRA-->")   # sections a page puts right under the calculator
    body = (f'<p class="eyebrow">{E(p["eyebrow"])}</p><h1 style="view-transition-name:c-{p["slug"]}">{E(p["h1"])}</h1><p class="lede">{E(p["lede"])}</p>'
            f'<div class="grid">{form}{results}</div>{after_grid}'
            f'<section class="block"><h2>How it works</h2>{"".join(f"<p>{E(x)}</p>" for x in p["method"])}</section>'
            f'<section class="block"><h2>A worked example</h2><p>{E(p["example"])}</p></section>'
            f'{extra_cards(p["slug"])}{find_customers(p["slug"], rel)}{guides_block(calc=p["slug"], rel=rel)}{cta(p) if p.get("cta") else ""}{related_calcs(p["slug"], rel)}{faq_block(p["faq"])}'
            + (find_customers(p["slug"], rel) if p.get("kind") == "bid" else ""))   # the bid page ends on the next step again (design director, Oct 27)
    city_numbers = bool(p.get("lists")) or any(k != "ecommerce-13-week-cash-flow" for k in load_store().get("calcProducts", {}).get(p["slug"], []))
    robots = '<meta name="robots" content="noindex, nofollow">' if p.get("draft") else ""
    crumb, crumb_ld = crumbs(rel, [("Home", ""), ("Free calculators", "calculators/"), (p["h1"], None)])
    body = crumb + body
    extra_ld = []
    if p.get("kind") == "cashflow":   # the free calculator is the kit's own page: its Product data lives here
        kit = next((x for x in store_products() if x["key"] == "ecommerce-13-week-cash-flow"), None)
        if kit:
            extra_ld.append(product_ld(kit, url))
            up = (f'<section class="block"><div class="fc"><div><h2>Real payouts land late. The full workbook plans for it.</h2>'
                  f'<p>{E(" ".join(p["cta"]["bullets"]))} ${E(kit["price"])} {E(kit["per"])}.</p></div><div class="fc-acts">'
                  f'<a class="btn" href="{E(utm(kit["checkout"], "site", kit["campaign"]))}" rel="noopener">Get the workbook, ${E(kit["price"])}</a>'
                  f'<span class="st-note">Secure checkout by Gumroad. <a href="{rel}refunds/">Refunds</a></span></div></div>'
                  + (f'<div class="fc-mail">{kit_form(kit["kitForm"], "Not ready? Get an email when the workbook gets an update", "Keep me posted", "kitEmail", note="Unsubscribe in one click. Stored with Kit, our email provider, and never sold.")}</div>' if kit.get("kitForm") else "")
                  + '</section>')
            body = body.replace('<section class="block"><h2>How it works</h2>', up + '<section class="block"><h2>How it works</h2>', 1)
    if p.get("stages"):   # stage counts: Gumroad links count an upgrade click (PNF.stages, docs/e/<slug>/)
        body = body.replace('href="https://proofnotfluff.gumroad.com', 'data-stage="upgrade" href="https://proofnotfluff.gumroad.com')
    ld = ld_json(p, url) + ld_tags(crumb_ld, *extra_ld)
    return (HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=SHOP, ld=ld, bodycls=' class="has-mbar"', robots=robots, analytics=analytics_tag()) + body +
            FOOT.format(rel=rel, script=script, sources=E(p["sources"]), notices=data_notices() if city_numbers else ""))


def index_html(pages):
    cards = "".join(f'<a class="card" href="{p["slug"]}/"><h3>{E(p["h1"])}</h3><p>{E(p["card"])}</p></a>' for p in pages)
    extras = "".join(f'<a class="card" href="{E(x["slug"])}/"><h3>{E(x["h1"])}</h3><p>{E(x["card"])}</p></a>' for x in live_extras())
    body = ('<p class="eyebrow">Free tools</p><h1>Pricing calculators that show their work</h1>'
            '<p class="lede">Free calculators for people who sell their time: find your real hourly rate and price a job so it pays you. '
            'Each one uses the same math as our tested Excel and Google Sheets workbooks.</p>'
            f'<div class="tools">{cards}</div>'
            + (f'<section class="block"><h2>Free printables</h2><div class="tools">{extras}</div></section>' if extras else ""))
    return (HEAD.format(title="Free pricing calculators for service businesses | ProofNotFluff",
                        desc="Free hourly rate and job pricing calculators for cleaners, pressure washing, freelancers and other service businesses.",
                        url=BASE, rel="", shop=SHOP, ld="", bodycls="", robots="", analytics=analytics_tag()) + body +
            FOOT.format(rel="", script="", sources="IRS Topic 554 (self-employment tax) and IRS standard mileage rates, checked Oct 6, 2026."))


LISTING = "https://proofnotfluff.etsy.com/listing/{id}"   # Share & Save shop domain, so the click is credited and the referrer is ours


def analytics_tag():
    """Analytics tag from site/analytics.json: {"ga4": "G-XXXX"} or {"cloudflare": "<beacon token>"} (either or both);
    empty until Todd pastes one. Cloudflare Web Analytics is cookie-free, so no consent banner is needed for it."""
    f = os.path.join(ROOT, "site", "analytics.json")
    if not os.path.exists(f):
        return ""
    cfg = json.load(open(f))
    out = ""
    ga = cfg.get("ga4", "")
    if ga:
        out += (f'<script async src="https://www.googletagmanager.com/gtag/js?id={E(ga)}"></script>'
                f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","{E(ga)}",{{anonymize_ip:true}});</script>')
    cf = cfg.get("cloudflare", "")
    if cf:
        out += f'<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=\'{{"token": "{E(cf)}"}}\'></script>'
    return out


def load_links():
    f = os.path.join(ROOT, "site", "links.json")
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {"shop": SHOP, "groups": [], "products": [], "gumroad": []}


def product_url(p):
    if p.get("channel") == "gumroad":
        sep = "&" if "?" in p["url"] else "?"
        return f'{p["url"]}{sep}utm_source=proofnotfluff&utm_medium=hub&utm_campaign={E(p.get("slug", "premium"))}'
    return LISTING.format(id=p["listing"])


def featured(links):
    """The two newest products in dated promo specs (promo/specs/YYYY-MM-DD-*.json, today or earlier, Chicago):
    the hub shows them first, so "link in bio" lands on the product the viewer just saw (Todd, Oct 15)."""
    import datetime, glob, re
    try:
        from zoneinfo import ZoneInfo
        today = datetime.datetime.now(ZoneInfo("America/Chicago")).date().isoformat()
    except Exception:
        today = datetime.date.today().isoformat()
    specs = {}
    for f in glob.glob(os.path.join(ROOT, "promo", "specs", "????-??-??-*.json")):
        d = os.path.basename(f)[:10]
        if re.match(r"\d{4}-\d{2}-\d{2}$", d) and d <= today:
            specs.setdefault(d, []).append(f)
    if not specs:
        return []
    by = {str(p["id"]): p for p in links["products"]}
    by.update({p.get("slug", ""): p for p in links.get("gumroad", [])})
    out, seen = [], set()
    files = [f for d in sorted(specs, reverse=True) for f in sorted(specs[d], key=lambda x: ("-pm-" not in x, x))]
    for f in files:
        if len(out) >= 2:
            break
        try:
            sp = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        pid = str(sp.get("product_id", ""))
        if pid not in by or pid in seen:
            continue
        seen.add(pid)
        lines = sp.get("post", {}).get("youtube_description", "").split("\n")
        old_base = "https://proofnotfluff-a11y.github.io/Proofnotfluff-pins/"
        lines = [l.strip().replace(old_base, BASE) for l in lines]
        free = next((l for l in lines[1:3] if l.startswith(BASE) and "/go/" not in l), "")
        hook = re.sub(r"<[^>]+>", "", sp.get("hook", ""))
        out.append({"product": by[pid], "hook": hook, "free": free})
    return out


def featured_html(links):
    items = featured(links)
    if not items:
        return ""
    cards = ""
    for it in items:
        p = it["product"]
        price = "$2.99 on Etsy" if p.get("channel") != "gumroad" else f'${p.get("price", "")} on Gumroad'
        cards += (f'<div class="hubfeat"><p class="hubfeat-hook">{E(it["hook"])}</p>'
                  f'<a class="hubbtn shop" href="{E(product_url(p))}" rel="noopener"><b>{E(p["name"])}</b><span>Get the workbook: {E(price)}</span></a>')
        if it["free"]:
            cards += f'<a class="hubbtn" href="{E(it["free"])}"><b>Try the free calculator first</b><span>Same math, in your browser</span></a>'
        cards += '</div>'
    return f'<h2 class="hubh">From our latest videos</h2><div class="hublist">{cards}</div>'


def hub_html(links, pages):
    """docs/go/: the one link every bio points to. Free value first, then the shop, then every product by audience."""
    url = BASE + "go/"
    live = [p for p in pages if is_live(p)]
    by = {p["id"]: p for p in links["products"]}
    calc = "".join(f'<a class="hubbtn" href="../{p["slug"]}/"><b>{E(p["h1"])}</b><span>{E(p["card"])}</span></a>' for p in live)
    prem = "".join(f'<a class="hubbtn prem" href="{E(product_url(p))}" rel="noopener"><b>{E(p["name"])}</b><span>{E(p.get("tagline", "Premium workbook"))} · ${p.get("price", "")}</span></a>'
                   for p in links.get("gumroad", []))
    groups = ""
    for g in links["groups"]:
        rows = "".join(f'<a class="hubbtn" href="{E(product_url(by[i]))}" rel="noopener"><b>{E(by[i]["name"])}</b><span>$2.99 on Etsy</span></a>' for i in g["ids"] if i in by)
        if rows:
            groups += f'<h2 class="hubh">{E(g["title"])}</h2><div class="hublist">{rows}</div>'
    lede = ('The Etsy workbooks are $2.99 each, the premium workbooks are on Gumroad, and the free calculators use the same math.'
            if links.get("gumroad") else 'Every paid workbook is $2.99 on Etsy, and the free calculators use the same math.')
    body = ('<section class="hub"><p class="eyebrow">ProofNotFluff</p><h1>Calculators that show their work</h1>'
            f'<p class="lede">Saw a video? It is right here. {E(lede)}</p>'
            f'{featured_html(links)}'
            f'{"<h2 class=hubh>Free calculators</h2><div class=hublist>" + calc + "</div>" if calc else ""}'
            f'{"<h2 class=hubh>Premium workbooks</h2><div class=hublist>" + prem + "</div>" if prem else ""}'
            f'<div class="hublist"><a class="hubbtn shop" href="{E(links.get("shop", SHOP))}" rel="noopener"><b>The whole shop on Etsy</b><span>Every tool, $2.99 each</span></a></div>'
            f'{groups}</section>')
    _, hub_ld = crumbs("../", [("Home", ""), ("Links", None)])
    return (HEAD.format(title="ProofNotFluff: free calculators and $2.99 tools", desc="Free pricing and money calculators, and the Excel and Google Sheets workbooks behind them.",
                        url=url, rel="../", shop=SHOP, ld=ld_tags(hub_ld), bodycls=' class="hubpage"', robots='<meta name="robots" content="noindex, follow">', analytics=analytics_tag()) + body +
            FOOT.format(rel="../", script="", sources="Prices as listed on Etsy; checked " + links.get("updated", "") + "."))


def redirect_html(target, label):
    """docs/go/<key>/: a short link for captions and pins that lands on the product and leaves our referrer."""
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow">'
            f'<meta http-equiv="refresh" content="0; url={E(target)}"><title>{E(label)}</title>'
            f'<script>location.replace({json.dumps(target)});</script></head>'
            f'<body style="font:16px system-ui;padding:24px"><p>Taking you to <a href="{E(target)}">{E(label)}</a>.</p></body></html>')


def write_hub_and_redirects(pages):
    links = load_links()
    go = os.path.join(DOCS, "go"); os.makedirs(go, exist_ok=True)
    open(os.path.join(go, "index.html"), "w", encoding="utf-8").write(hub_html(links, pages))
    keys = {"shop": (links.get("shop", SHOP), "the ProofNotFluff shop on Etsy")}
    for p in links["products"]:
        keys[str(p["id"])] = (product_url(p), p["name"])
    for p in links.get("gumroad", []):
        keys[p["slug"]] = (product_url(p), p["name"])
    for p in pages:
        if is_live(p):
            keys["free-" + p["slug"]] = (BASE + p["slug"] + "/", p["h1"])
    for k, (target, label) in keys.items():
        d = os.path.join(go, k); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(redirect_html(target, label))
    print("hub + %d short links" % len(keys))
    return BASE + "go/"



# ---------------------------------------------------------------------------------------------------------------------
# The store (Todd, Oct 22, 2026; seo/STORE.md; design canvas https://claude.ai/artifact/LqgDbvVYjWCetbybrZ9JiY).
# site/store.json names the products, the home page's trade picker, the calculator-to-product map and the refund text;
# every number on a card is read here from the product's own committed data file, so a Monday refresh updates the store.

ARROW = ('<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
         'stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')


def load_store():
    f = os.path.join(ROOT, "site", "store.json")
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {"products": [], "trades": [], "calcProducts": {}}


def _pages_by_slug():
    return {p["slug"]: p for p in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"]}


def utm(url, medium, campaign, content=""):
    """A checkout link with our own utm tags (the medium says which kind of page sent the buyer)."""
    base = url.split("?")[0]
    out = f"{base}?utm_source=proofnotfluff&utm_medium={medium}&utm_campaign={campaign}"
    return out + (f"&utm_content={content}" if content else "")


def _campaign(url):
    import re
    m = re.search(r"utm_campaign=([^&]+)", url or "")
    return m.group(1) if m else "store"


def store_products():
    """The store's products, each merged with its page spec and this week's two headline numbers from its own data."""
    st, pages = load_store(), _pages_by_slug()
    out = []
    for s in st.get("products", []):
        x = dict(s)
        page = pages.get(s.get("page", s["key"]))
        if not page or not is_live(page):
            continue
        x["page"] = page["slug"]
        x["href"] = page["slug"] + "/"
        x.setdefault("price", str(page.get("price", "")))
        x.setdefault("checkout", page.get("checkout"))
        x.setdefault("campaign", _campaign(page.get("checkout")))
        x["trial"] = int(page.get("trialDays") or 0) if x.get("checkout") else 0   # Gumroad free trial on (page key trialDays)
        x["kitForm"] = s.get("kitForm") or page.get("kitForm")
        if page.get("kind") == "leads":
            d = json.load(open(os.path.join(ROOT, page["data"]), encoding="utf-8"))
            c = d["counts"]
            m = lambda v: money(v, True, bool(page.get("billions2")))
            x["nums"] = [[f'{c["kept"]:,}', f'open projects, about {m(c["keptCost"])}']]
            near = c.get("nearFinish", len(d.get("nearFinish", [])))
            if near >= 5:
                x["nums"].append([f"{near:,}", page.get("nearSub", "near finish")])
            else:
                x["nums"].append([f'{c["keptByType"].get("New construction", 0):,}', f'new buildings, at least {c.get("keptUnits", 0):,} {page.get("unitsWord", "apartments")}'])
            x["asof"] = nice_date(d["source"]["fetchedAt"])
            x["source"] = (f'{d["source"]["name"]}: {c["kept"]:,} open projects of $500,000 or more, about {m(c["keptCost"])}, '
                           f'City data as of {x["asof"]}.')
            x["sample"] = "#near" if d.get("nearFinish") else "#sample"
            x["counts"] = c
        elif page.get("kind") == "restleads":
            d = json.load(open(os.path.join(ROOT, page["data"]), encoding="utf-8"))
            c = d["counts"]
            x["nums"] = [[f'{c["flagged"]:,}', "failed or conditional in our four categories, 30 days"], [f'{c["opening"]:,}', "license inspections before a food license"]]
            x["asof"] = d["asOfText"]
            x["source"] = (f'{d["source"]["name"]}: {c["flagged"]:,} failed or conditional with a pest, hood, grease trap or cleaning violation and {c["opening"]:,} license inspections in the '
                           f'30 days to {d["throughText"]}, pulled {d["asOfText"]}.')
            x["sample"] = "#sample"
            x["counts"] = c
        elif page.get("kind") == "licleads":
            d = json.load(open(os.path.join(ROOT, page["data"]), encoding="utf-8"))
            c = d["counts"]
            x["nums"] = [[f'{c["kept30"]:,}', "new business licenses, last 30 days"], [f'{c["keptWeek"]:,}', "licensed this week"]]
            x["asof"] = nice_date(d["source"]["fetchedAt"])
            x["source"] = (f'{d["source"]["name"]}: {c["kept30"]:,} new business licenses at Chicago business sites in the 30 days to '
                           f'{nice_date(d["window"]["to"])}, pulled {x["asof"]}.')
            x["sample"] = "#sample"
            x["counts"] = c
        else:
            x["sample"] = ""
        out.append(x)
    return out


def store_coming():
    """The next list (licenses), with this week's numbers, while its page is a draft or not on sale."""
    st, pages = load_store(), _pages_by_slug()
    c = st.get("coming")
    if not c or c["key"] not in pages:
        return None
    page = pages[c["key"]]
    if page.get("checkout") and is_live(page):
        return None
    d = json.load(open(os.path.join(ROOT, page["data"]), encoding="utf-8"))
    n = d["counts"]
    x = dict(c)
    x["text"] = (f'{n["keptWeek"]:,} Chicago business sites got a new City business license in the week to {nice_date(d["window"]["to"])}, '
                 f'and {n["kept30"]:,} in the last 30 days. {c["for"]}')
    x["kitForm"] = page.get("kitForm")
    x["notify"] = page.get("notify") or "mailto:hello@proofnotfluff.com?subject=Chicago%20New%20Business%20Licenses%3A%20tell%20me%20when%20it%20opens"
    return x


def kit_form(form_id, label, button, field_id, note="One email when it opens. Stored with Kit, our email provider, and never sold."):
    """A Kit sign-up form (Kit's own subscribe endpoint, no script)."""
    return (f'<form class="st-form" action="https://app.kit.com/forms/{E(form_id)}/subscriptions" method="post">'
            f'<label for="{field_id}">{E(label)}</label><div class="st-frow">'
            f'<input id="{field_id}" name="email_address" type="email" required autocomplete="email" placeholder="you@company.com">'
            f'<button class="st-btn2" type="submit">{E(button)}</button></div><span class="st-note">{E(note)}</span></form>')


def crumbs(rel, items):
    """Visible breadcrumbs plus their BreadcrumbList data. items: [(name, path or None for the current page)]."""
    lis, ld = [], []
    for i, (name, path) in enumerate(items, 1):
        lis.append(f'<li><a href="{rel}{path}">{E(name)}</a></li>' if path is not None else f'<li aria-current="page">{E(name)}</li>')
        ld.append({"@type": "ListItem", "position": i, "name": name, **({"item": BASE + path} if path is not None else {})})
    html_ = f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(lis)}</ol></nav>'
    return html_, {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ld}


def ld_tags(*objs):
    return "".join(f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>' for o in objs if o)


def product_ld(x, url):
    """Product data for a paid list or workbook: a monthly price for the lists, a one-time price for the workbook."""
    offer = {"@type": "Offer", "price": str(x["price"]), "priceCurrency": "USD", "availability": "https://schema.org/InStock",
             "url": utm(x["checkout"], "site", x["campaign"]) if x.get("checkout") else url}
    if x.get("per") == "a month":
        offer["priceSpecification"] = {"@type": "UnitPriceSpecification", "price": str(x["price"]), "priceCurrency": "USD",
                                       "billingDuration": 1, "billingIncrement": 1, "unitCode": "MON", "referenceQuantity": {"@type": "QuantitativeValue", "value": 1, "unitCode": "MON"}}
    slug = url[len(BASE):].strip("/") or "home"
    return {"@context": "https://schema.org", "@type": "Product", "name": x["name"], "description": x["what"], "url": url,
            "image": BASE + f"assets/og/{slug}.png", "brand": {"@type": "Brand", "name": "ProofNotFluff"}, "offers": offer}


ORG = {"@type": "Organization", "name": "ProofNotFluff", "url": "https://proofnotfluff.com/", "email": "hello@proofnotfluff.com",
       "sameAs": [SHOP, "https://proofnotfluff.gumroad.com"]}


def data_date(rel):
    """The day a page's data was pulled from the City (source.fetchedAt or asOf), or "" when the file has none."""
    try:
        dd = json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return ""
    m = str((dd.get("source") or {}).get("fetchedAt") or dd.get("asOf") or "")[:10]
    return m if len(m) == 10 and m[4] == "-" else ""


def page_ld(p, url):
    """WebPage data for a lead page with true dates (radar, Oct 23, 2026; research_notes/ai-recommendation-2026-10-23.md):
    dateModified is the day its data was pulled, datePublished the launch day in launches/WIRING.json. Same publisher on
    every page, so assistants and search engines read one consistent business."""
    mod = data_date(p.get("data"))
    if not mod:
        return None
    try:
        w = json.load(open(os.path.join(ROOT, "launches", "WIRING.json"), encoding="utf-8"))["products"].get(p["slug"], {})
    except (OSError, ValueError):
        w = {}
    d = {"@context": "https://schema.org", "@type": "WebPage", "url": url, "name": p.get("h1", ""), "description": p.get("desc", ""),
         "dateModified": mod, "publisher": ORG}
    if w.get("launchedAt") and w["launchedAt"] <= mod:
        d["datePublished"] = w["launchedAt"]
    return d


def nb(text):
    """A title with its hyphenated words kept whole, so "E-commerce" never breaks at the hyphen (design check, Oct 22)."""
    import re
    return re.sub(r"(\S+-\S+)", r'<span class="nw">\1</span>', E(text))


def product_card(x, rel, medium):
    nums = "".join(f'<div><b>{E(a)}</b><span>{E(b)}</span></div>' for a, b in x.get("nums", []))
    if x["audience"] == "ecom":
        prim = f'<a class="btn" href="{rel}{x["href"]}">Try the free calculator</a>'
        sec = f'<a class="st-link" href="{E(utm(x["checkout"], medium, x["campaign"]))}" rel="noopener">Buy the workbook, ${E(x["price"])}{ARROW}</a>'
        t = 0
    else:
        prim = f'<a class="btn" href="{rel}{x["href"]}{x["sample"]}">See this week\'s free sample</a>'
        t = x.get("trial") if x.get("checkout") else 0
        # a list with a Gumroad trial shows the trial button and its terms, as the shop does (Todd, Oct 23: the home cards
        # said only "Subscribe")
        # one primary action per card (design review, Oct 24): the sample is the button, the trial a text link beside it
        sec = (f'<a class="st-link" href="{E(utm(x["checkout"], medium, x["campaign"]))}" rel="noopener">or try {t} days free{ARROW}</a>' if t else
               f'<a class="st-link" href="{E(utm(x["checkout"], medium, x["campaign"]))}" rel="noopener">Subscribe</a>' if x.get("checkout") else "")
    return (f'<article class="st-card"><div class="st-top"><span class="st-tag">{E(x["tag"])}</span>'
            f'<span class="st-price">${E(x["price"])}<small> {E(x["per"])}</small></span></div>'
            f'<h3>{nb(x["name"])}</h3><p>{E(x["card"])}</p><div class="st-nums">{nums}</div>'
            f'<p>{E(x["for"])}</p><div class="st-act">{prim}{sec}</div>'
            + (f'<p class="st-note st-trialnote">Card at checkout, nothing charged for {t} days. No lock-in, cancel any time.</p>' if t else "")
            + '</article>')


def coming_card(c, rel, field_id, cls="st-card soon", h="h3"):
    form = (kit_form(c["kitForm"], "Email me when it opens", "Notify me", field_id) if c.get("kitForm") else
            f'<div class="st-act"><a class="st-btn2" href="{E(c["notify"])}">Tell me when it opens</a></div>')
    return (f'<article class="{cls}"><div class="st-ctext"><div class="st-top"><span class="st-tag">{E(c["tag"])}</span><span class="st-soon">Coming next</span></div>'
            f'<{h}>{E(c["name"])}</{h}><p>{E(c["text"])}</p></div><div class="st-cact">{form}</div></article>')


def data_notices():
    """The cities' own data notices, for pages that show their numbers (copy check, Oct 22): Chicago's required wording,
    Austin's attribution and license from the source record."""
    out = [CITY_DISCLAIMER["Chicago"]]
    f = os.path.join(ROOT, "permits", "austin", "sample.json")
    if os.path.isfile(f):
        src = json.load(open(f, encoding="utf-8"))["source"]
        attr = src["attribution"].replace(" - ", " (") + ")" if " - " in src["attribution"] else src["attribution"]
        out.append(f'Austin data: {attr}, published under {src["license"]}. The City of Austin has not reviewed or endorsed this site.')
    return "".join(f"<p>{E(x)}</p>" for x in out)


def bento_html(by):
    """Store v2 round 2 (Oct 24, 2026; research: Stripe and Resend bento grids, Stripe and Attio numbers as proof): a dark
    band of this week's numbers, each tile linking to its list, every figure read from the lists' own data, plus what a
    member gets. No figure here that the list pages do not already show."""
    def pick(key, i):
        x = by.get(key)
        return (x, x["nums"][i]) if x and len(x.get("nums", [])) > i else (None, None)
    tiles = []
    for key, i, cls, line in (("chicago-construction-cleaning-leads", 1, "bt-wide", "Chicago projects with temporary or partial occupancy approved, so a final clean is close. The builder is on each."),
                              ("chicago-restaurant-inspection-leads", 1, "", "Chicago restaurants had the license inspection the City does before it opens."),
                              ("chicago-new-business-licenses", 1, "", "new Chicago business licenses this week, sorted by trade."),
                              ("austin-construction-cleaning-leads", 0, "", "open Austin projects of $500,000 or more, with the builders running them.")):
        x, num = pick(key, i)
        if not x:
            continue
        tiles.append(f'<a class="bt {cls}" href="{x["href"]}{x["sample"]}"><span class="bt-tag">{E(x["tag"])}</span>'
                     f'<b class="bt-n">{E(num[0])}</b><span class="bt-l">{E(line)}</span><span class="bt-go">See the free sample{ARROW}</span></a>')
    book = ""
    if os.path.isfile(os.path.join(DOCS, "assets", "leads", "workbook.png")):
        wp, ww, wh = webp_of("assets/leads/workbook.png", width=720)
        book = (f'<img src="{wp}" width="{ww}" height="{wh}" loading="lazy" decoding="async" alt="The Excel file members get: the near finish tab with address, reported cost and builder columns">')
    tiles.append('<div class="bt bt-tall"><span class="bt-tag">Every Monday</span><b class="bt-h">The full list, three ways</b>'
                 '<ul class="bt-ul"><li>A members\' web app with filters and a map</li><li>An Excel file, filters on every column</li><li>A pitch kit for your trade</li></ul>'
                 f'<div class="bt-shot">{book}</div></div>')
    return ('<section class="bento" aria-labelledby="bento-title"><div class="bento-in"><p class="eyebrow">This week in the lists</p>'
            '<h2 id="bento-title">Real records, counted from the City\'s own data</h2>'
            f'<div class="bt-grid">{"".join(tiles)}</div></div></section>')


def hero_feed(rows, dates):
    """The home hero's moving product view (store v2 round 2, Oct 24, 2026, Todd: "scrolling animation"): this week's
    counts, then real records from the free samples rolling past, the way the members' app lists them. Only what the free
    sample pages already show: builders on City permits, places that passed a license inspection by name, and failed or
    conditional places without their name. Still under prefers-reduced-motion (pnf.css), and readable without motion."""
    pb = _pages_by_slug()
    items = []
    try:
        d = json.load(open(os.path.join(ROOT, pb["chicago-construction-cleaning-leads"]["data"]), encoding="utf-8"))
        for x in (d.get("nearFinish") or [])[:4]:
            gc = (x.get("gc") or [""])[0]
            items.append(("Near finish", "chicago-construction-cleaning-leads/#near",
                          f'{money(x["cost"])} {x.get("type", "").lower()}, {x["address"]}', f'{x.get("communityArea", "")}' + (f' · {gc}' if gc else "")))
    except (OSError, KeyError, ValueError, TypeError):
        pass
    try:
        r = json.load(open(os.path.join(ROOT, pb["chicago-restaurant-inspection-leads"]["data"]), encoding="utf-8"))
        ex = r.get("examples") or {}
        fl = [(f'Failed inspection', "chicago-restaurant-inspection-leads/#sample", f'A {x.get("type", "place").lower()} in {x.get("area", "Chicago")}',
               f'{", ".join(x.get("categories", []))} · {nice_date(x["date"]).rsplit(",", 1)[0]}') for x in ex.get("flagged", [])[:3]]
        op = [("Opening soon", "chicago-restaurant-inspection-leads/#sample", f'{x["name"]}, {x["address"]}',
               f'Passed its license inspection · {nice_date(x["date"]).rsplit(",", 1)[0]}') for x in ex.get("opening", [])[:3]]
        mix = []
        for i in range(max(len(items), len(fl), len(op))):
            for src in (items, fl, op):
                if i < len(src):
                    mix.append(src[i])
        items = mix
    except (OSError, KeyError, ValueError, TypeError):
        pass
    short = {"Chicago food businesses failed or conditional in our four trade categories, 30 days": "food places failed, last 30 days",
             "open Chicago projects of $500,000 or more": "open Chicago projects, $500K+",
             "open Austin projects of $500,000 or more": "open Austin projects, $500K+"}
    stats = "".join(f'<div><dd>{E(n)}</dd><dt>{E(short.get(tx, tx))}</dt></div>' for n, tx in rows)
    li = lambda x, dup=False: (f'<li><a href="{x[1]}"{" tabindex=\"-1\"" if dup else ""}><span class="hf-tag hf-{"near" if x[0] == "Near finish" else "fail" if x[0].startswith("Failed") else "open"}">{E(x[0])}</span>'
                    f'<b>{E(x[2])}</b><span>{E(x[3])}</span></a></li>')
    feed = ""
    if items:
        # WCAG 2.2.2: the roll pauses on hover or focus, and the Pause button stops it (assets/pnf-ui.js)
        feed = (f'<div class="hf" role="region" aria-label="Records from this week\'s free samples"><div class="hf-track"><ul class="hf-list">{"".join(li(x) for x in items)}</ul>'
                f'<ul class="hf-list hf-dup" aria-hidden="true">{"".join(li(x, True) for x in items)}</ul></div></div>')
    return (f'<div class="hx-week"><p class="lab"><span class="hf-dot" aria-hidden="true"></span>This week in the City\'s records'
            + ('<button type="button" class="hf-pause" hidden aria-pressed="false">Pause</button>' if feed else "") + '</p>'
            f'<dl class="hx-stats">{stats}</dl>{feed}<p class="asof">City data pulled {E(" and ".join(dates))}. From this week\'s free samples.</p></div>')


def home_html(pages, live, doors=False):
    """The store home: what we sell and who for on the first screen, the lists, how it works, the calculators.
    doors=True is the two front doors draft (Todd, Oct 23, approved move 5: "Find work" and "Run the numbers", every
    calculator stays on proofnotfluff.com); a home layout change is major (CONSTITUTION 2), so it is written only as the
    noindex draft docs/home-two-doors.html until Todd's go."""
    CURRENT["nav"] = ""
    st = load_store()
    prods = store_products()
    by = {x["key"]: x for x in prods}
    trades = ""
    for t in st.get("trades", []):
        x = by.get(t["to"])
        if not x:
            continue
        frag = (x["sample"] if t.get("tab") is None else f'?trade={t["tab"]}#sample') if x["audience"] != "ecom" else ""
        trades += (f'<li><a href="{x["href"]}{frag}"><span><b>{E(t["label"])}</b><span class="sr">, </span><small>{E(t["where"])}</small></span>{ARROW}</a></li>')
    week = ""
    rest, chi, aus = by.get("chicago-restaurant-inspection-leads"), by.get("chicago-construction-cleaning-leads"), by.get("austin-construction-cleaning-leads")
    rows = []
    if rest:
        rows.append((rest["nums"][0][0], "Chicago food businesses failed or conditional in our four trade categories, 30 days"))
    if chi:
        rows.append((f'{chi["counts"]["kept"]:,}', "open Chicago projects of $500,000 or more"))
    if aus:
        rows.append((f'{aus["counts"]["kept"]:,}', "open Austin projects of $500,000 or more"))
    if rows:
        dates = sorted({x["asof"] for x in (rest, chi, aus) if x})
        week = ('<aside class="card st-week" aria-label="This week in the records"><p class="lab">This week in the records</p><dl>'
                + "".join(f"<div><dt>{E(t)}</dt><dd>{E(n)}</dd></div>" for n, t in rows)
                + f'</dl><p class="asof">City data pulled {E(" and ".join(dates))}. Refreshed every Monday.</p></aside>')
    # store v2 hero (design review, Oct 24, 2026): the product on the first screen and the trade picker in the hero, so a
    # visitor is one tap from a free sample; the counts sit on the product shot instead of a separate card
    shot = ""
    if os.path.isfile(os.path.join(DOCS, "assets", "leads", "members-list.png")):
        wp, ww, wh = webp_of("assets/leads/members-list.png")
        sp, sw, _ = webp_of("assets/leads/members-list.png", width=720)
        # below the trade picker on phones, so no fetch priority; phones get the 720 px copy (Lighthouse, Oct 24: LCP 2.0 s)
        shot = (f'<div class="hx-frame"><img src="{wp}" srcset="{sp} {sw}w, {wp} {ww}w" sizes="(min-width:1000px) 540px, 100vw" width="{ww}" height="{wh}" loading="lazy" decoding="async" '
                'alt="A screen from the members\' app for Chicago Construction Cleaning Leads: projects sorted closest to finish, with filters and a map"></div>')
    week_hx = hero_feed(rows, sorted({x["asof"] for x in (rest, chi, aus) if x})) if rows else ""
    hero = ('<section class="hx" aria-labelledby="hero-title"><div class="hx-copy"><p class="eyebrow">Lead lists from public records</p>'
            '<h1 id="hero-title">Sales leads from the City\'s own records, every Monday.</h1>'
            '<p class="lede">Weekly lists for cleaning, hood cleaning and pest control companies in Chicago and Austin. Each one has a free sample, new every Monday.</p>'
            '<p class="hx-cta"><a class="btn ld-btnbig" href="#trades">Pick your trade</a><a class="st-link" href="#calc-title">Pricing a job? Try a free calculator</a></p></div>'
            f'<div class="hx-side">{shot}{week_hx}</div>'
            f'<div class="hx-pickrow"><h2 class="hx-pick" id="trades">Open this week\'s free sample for your trade</h2><ul class="st-trades hx-trades">{trades}</ul></div></section>')
    calcs_live = [p for p in live if p.get("kind") not in ("leads", "restleads", "licleads", "question", "newin", "rodents", "agentkit", "tradesnews")]
    if doors:
        by_calc = {p["slug"]: p for p in calcs_live}
        feat = [by_calc[x] for x in st.get("doorCalcs", []) if x in by_calc][:4]
        feat_li = "".join(f'<li><a href="{p["slug"]}/"><b>{E(p["h1"])}</b><span>{E(p["card"])}</span></a></li>' for p in feat)
        hero = ('<section class="st-hero" aria-labelledby="hero-title"><div><p class="eyebrow">Public records and plain math</p>'
                '<h1 id="hero-title">Find work from the City\'s own records, or run the numbers first.</h1>'
                '<p class="lede">Weekly lead lists for cleaning, hood cleaning and pest control companies in Chicago and Austin, and free calculators for any small business owner.</p>'
                '<p class="st-jump"><a class="st-btn2" href="#door-work">Find work</a><a class="st-btn2" href="#door-num">Run the numbers</a></p>'
                f'</div>{week}</section>'
                '<section class="st-doors" aria-label="Two ways in">'
                '<div class="card st-door"><p class="st-cap">Find work</p><h2 id="door-work">Lead lists, with a free sample on each</h2>'
                '<p>Open this week\'s sample with no sign-up, then subscribe if it fits. No lock-in, cancel any time.</p>'
                f'<ul class="st-trades">{trades}</ul>'
                '<p class="st-dooract"><a class="btn ld-btnbig" href="#lists-title">See this week\'s free samples</a></p></div>'
                '<div class="card st-door"><p class="st-cap">Run the numbers</p><h2 id="door-num">Free calculators for owners</h2>'
                '<p>Price a job, see what your leads really cost, or plan around a payout hold. Nothing you type leaves your browser.</p>'
                f'<ul class="st-calcs">{feat_li}</ul>'
                f'<p class="st-dooract"><a class="st-btn2" href="calculators/">All {len(calcs_live)} free calculators</a></p></div></section>'
                # phones: both doors before the counts, so the second door is not five screens down
                + (week.replace('class="card st-week"', 'class="card st-week st-weeklow"', 1) if week else ""))
    coming = store_coming()
    cards = "".join(product_card(x, "", "home") for x in prods if x["audience"] != "ecom") + "".join(
        product_card(x, "", "home").replace('<article class="st-card">', '<article class="st-card st-wide">', 1) for x in prods if x["audience"] == "ecom")
    lists = ('<section class="st-sec" aria-labelledby="lists-title"><h2 id="lists-title">The lists</h2>'
             '<p>A free sample on every page. Members get every record, named, in a web app and an Excel file, every Monday. Cancel any time.</p>'
             f'<div class="st-grid">{cards}</div>{coming_card(coming, "", "homeLic", cls="st-strip") if coming else ""}</section>')
    how = ('<section class="st-sec" aria-labelledby="how-title"><h2 id="how-title">How it works</h2><ol class="st-steps">'
           '<li><span class="n" aria-hidden="true">1</span><div><h3>Open the free sample</h3><p>Real records from this week\'s pull sit on each list\'s page. No sign-up.</p></div></li>'
           '<li><span class="n" aria-hidden="true">2</span><div><h3>Subscribe when it fits</h3><p>$29 or $39 a month, paid through Gumroad. Cancel any time.</p></div></li>'
           '<li><span class="n" aria-hidden="true">3</span><div><h3>Work the list</h3><p>Every Monday: the named list, an Excel file and a pitch kit for your trade.</p></div></li></ol></section>')
    by_slug = {p["slug"]: p for p in calcs_live}
    groups, used = [], set()
    door_set = set(st.get("doorCalcs", [])[:4]) if doors else set()   # the doors already feature these (design review, Oct 24)
    for title, slugs in st.get("calcGroups", []):
        items = [by_slug[x] for x in slugs if x in by_slug and x not in door_set]
        used |= {p["slug"] for p in items}
        if items:
            groups.append((title, items))
    rest_ = [p for p in calcs_live if p["slug"] not in used]
    if rest_:
        groups.append(("More calculators", rest_))
    li = lambda p: f'<li><a href="{p["slug"]}/"><b>{E(p["h1"])}</b><span>{E(p["card"])}</span></a></li>'
    feat4 = [by_slug[x] for x in st.get("doorCalcs", []) if x in by_slug][:4]
    if doors or not feat4:
        calc_cards = "".join(f'<h3 class="st-cgroup">{E(t)}</h3><ul class="st-calcs">{"".join(li(p) for p in items[:4])}</ul>' for t, items in groups)
    else:   # store v2: four owner calculators, the rest one tap away (design review, Oct 24: 16 entries made a lead-list store read like a hobby site)
        calc_cards = f'<ul class="st-calcs st-calc4">{"".join(li(p) for p in feat4)}</ul>'
    calc_cards += f'<p class="st-all"><a class="st-btn2" href="calculators/">All {len(calcs_live)} free calculators</a></p>'
    if not doors:   # the calculators page reads the live home's groups, never the draft's
        CALC_GROUPS[:] = groups
    extras = "".join(f'<a class="card st-printable" href="{E(x["slug"])}/"><h3>{E(x["h1"])}</h3><p>{E(x["card"])}</p><span class="st-link">Get the sheet {ARROW}</span></a>' for x in live_extras())
    calcs = ('<section class="st-sec" id="calculators" aria-labelledby="calc-title"><h2 id="calc-title">Free calculators</h2>'
             '<p>Price the job before you call. The same math as our Excel and Google Sheets workbooks, and nothing you type leaves your browser.</p>'
             f'{calc_cards}</section>'
             + (f'<section class="st-sec" aria-labelledby="print-title"><h2 id="print-title">Free printables</h2><div class="tools">{extras}</div></section>' if extras else ""))
    qs = ""
    if LIVE_QUESTIONS:
        qs = ('<section class="st-sec" aria-labelledby="q-title"><h2 id="q-title">Questions owners ask</h2>'
              '<p>Plain answers with this week\'s numbers, written by a finance executive.</p><ul class="st-qs">'
              + "".join(f'<li><a href="{q["slug"]}/"><span><b>{E(q["h1"])}</b><small>{E(q.get("eyebrow", ""))}</small></span>{ARROW}</a></li>' for q in LIVE_QUESTIONS[:5])
              + '</ul></section>')
    # peak-end and serial position (Oct 25, UX principles): the page ends on the trust promise and the one next step
    band = ('<section class="st-band" aria-labelledby="trust-title"><h2 id="trust-title">Public records, read by a finance executive.</h2>'
            '<p>Every number here comes from the cities\' own open data or our own workbooks, with the date we pulled it. No business on a list '
            'endorses or works with ProofNotFluff, and we never contact anyone for you. Public information for planning sales calls; not legal or business advice and no promise of work.</p>'
            + ('<p class="st-band-act"><a class="btn ld-btnbig" href="#trades">Pick your trade, see this week\'s sample</a></p>' if not doors else "")
            + '</section>')
    org = {"@context": "https://schema.org", **ORG, "url": BASE, "logo": BASE + "assets/logo-512.png"}
    site = {"@context": "https://schema.org", "@type": "WebSite", "name": "ProofNotFluff", "alternateName": "Proof Not Fluff", "url": BASE,
            "publisher": {"@type": "Organization", "name": "ProofNotFluff", "url": BASE}}
    items = {"@context": "https://schema.org", "@type": "ItemList", "name": "ProofNotFluff lead lists and tools",
             "itemListElement": [{"@type": "ListItem", "position": i, "url": BASE + x["href"], "name": x["name"]} for i, x in enumerate(prods, 1)]}
    body = hero + (bento_html(by) if not doors else "") + lists + how + calcs + qs + band
    if doors:
        body += ("<style>.st-doors{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:20px;margin:28px 0 0}"
                 ".st-door{display:flex;flex-direction:column;padding:22px 22px 20px}.st-door h2{font-size:24px;line-height:1.2;margin:0 0 6px}"
                 ".st-door>p{color:var(--ink2);margin:0 0 16px}.st-door .st-trades{max-width:none;grid-template-columns:repeat(auto-fill,minmax(170px,1fr))}"
                 ".st-door .st-calcs{grid-template-columns:1fr}.st-dooract{margin:auto 0 0;padding-top:18px}.st-dooract .st-btn2{display:inline-flex}.st-weeklow{display:none}.st-jump{display:none}"
                 ".st-door .st-trades li:last-child:nth-child(odd){grid-column:1/-1}"
                 "@media(max-width:700px){.st-hero .st-week{display:none}.st-weeklow{display:block;margin:20px 0 0}"
                 ".st-door{padding:18px 16px}.st-door .st-trades{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}"
                 ".st-door .st-trades a{min-height:56px;padding:8px 8px 8px 12px}.st-door .st-trades b{font-size:13.5px}"
                 ".st-jump{display:flex;gap:10px;margin:16px 0 0}.st-jump .st-btn2{flex:1;min-height:44px;font-size:15px}"
                 ".st-door h2{scroll-margin-top:16px}}</style>")
    return (HEAD.format(title="Lead lists from public records, and free pricing calculators | ProofNotFluff",
                        desc="Weekly lead lists for cleaning, hood cleaning and pest control companies in Chicago and Austin, from City permits and inspections, with a free sample every Monday. Plus free pricing calculators.",
                        url=BASE, rel="", shop=SHOP, ld=ld_tags(site, org, items), bodycls=' class="st-page"', robots='<meta name="robots" content="noindex, nofollow">' if doors else "", analytics=analytics_tag()) + body +
            FOOT.format(rel="", script="", notices=data_notices(), sources="City of Chicago and City of Austin open data, pulled as dated on each list. IRS Topic 554 and IRS standard mileage rates, checked Oct 6, 2026."))


def shop_seat_row(rel):
    """The Chicago pest control daily seat as a shop row, in the restaurant page's own cleared words; its button opens the
    offer on the restaurant page (#seat), where the terms and the checkout sit, so the shop adds no new checkout."""
    p = _pages_by_slug().get("chicago-restaurant-inspection-leads")
    seat = (p or {}).get("seat") or {}
    if not p or not seat.get("checkout"):
        return ""
    cap, price = int(seat["seats"]), E(str(seat["price"]))
    gets = ["New places each morning, after the City's overnight refresh, with the last 14 days kept so a missed morning loses nothing.",
            "Each place: name, street, ZIP, community area, the City's result, date and violation codes, failed visits in 90 days, and a link to the City's record.",
            "A Call button, called marks and private notes on your phone or computer, and a CSV download."]
    return (f'<article class="sh-item" data-aud="trade" data-key="chicago-pest-seat"><div class="sh-main"><p class="st-tag">Chicago · Pest control, daily</p>'
            f'<h2>Chicago Pest Control Daily Seat</h2><p>At most {cap} Chicago pest control companies hold a seat at a time. Each morning, the Chicago food places '
            'whose failed or conditional inspection had a pest violation, named, with street address and the City\'s violation codes.</p></div>'
            f'<div class="sh-buy"><div class="amt">${price}<small> a month</small></div><p>No lock-in, cancel any time. At most {cap} seats.</p>'
            f'<a class="btn" href="{rel}chicago-restaurant-inspection-leads/#seat">See the pest seat</a>'
            f'<p class="st-note">Checkout and seat terms are on the next page. <a href="{rel}refunds/">Refunds and cancelling</a></p></div>'
            f'<div class="sh-gets"><h3 class="sr">What you get</h3><ul class="checks">{"".join(f"<li>{E(g)}</li>" for g in gets)}</ul></div></article>')


def shop_area_row(rel):
    """The Chicago cleaning area seats as a shop row (Todd, Oct 26, 2026), in the offer's own cleared words
    (tools/area_site.py); its button opens the offer on the cleaning page (#areas), where the map, terms and the six
    checkouts sit, so the shop adds no new checkout. Shown only while a seat has its checkout in site/pages.json."""
    p = _pages_by_slug().get("chicago-construction-cleaning-leads")
    spec = (p or {}).get("areaSeats") or {}
    co = spec.get("checkout") or {}
    if not p or not any(co.values()):
        return ""
    import area_seats as A
    cfg = A.load()
    cap = int(spec.get("seats") or len(cfg["territories"]))
    left = sum(1 for t in cfg["territories"] if t["slug"] not in set(cfg.get("held", [])) and co.get(t["slug"]))
    price = E(str(spec["price"]))
    gets = ["Every open apartment and commercial project of $500,000 or more in your area with a business as general contractor, "
            "closest to a final clean first, with the builder on each and the builder's office phone or email where their own website lists one.",
            "New permits each Monday, in a members' app with a map and in an Excel file, plus the pitch kit.",
            "Your area only, and only you. The permits are public City of Chicago records that anyone can read on the City's site; "
            "exclusive means we sell your area's list to you alone."]
    return (f'<article class="sh-item" data-aud="trade" data-key="chicago-cleaning-area-seats"><div class="sh-main"><p class="st-tag">Chicago · Construction cleaning, one company per area</p>'
            f'<h2>Chicago Cleaning Leads: Area Seats</h2><p>One cleaning company per area of Chicago. Hold an area and we sell its list to you and to no other company. '
            f'{left} of {cap} areas open.</p></div>'
            f'<div class="sh-buy"><div class="amt">${price}<small> a month per area</small></div><p>No lock-in, cancel any time. One company per area.</p>'
            f'<a class="btn" href="{rel}chicago-construction-cleaning-leads/#areas">See the areas</a>'
            f'<p class="st-note">The map, seat terms and checkout are on the next page. <a href="{rel}refunds/">Refunds and cancelling</a></p></div>'
            f'<div class="sh-gets"><h3 class="sr">What you get</h3><ul class="checks">{"".join(f"<li>{E(g)}</li>" for g in gets)}</ul></div></article>')


def shop_html():
    CURRENT["nav"] = "shop"
    rel = "../"
    url = BASE + "shop/"
    prods = store_products()
    crumb, crumb_ld = crumbs(rel, [("Home", ""), ("Shop", None)])
    rows = ""
    for x in prods:
        gets = "".join(f"<li>{E(g)}</li>" for g in x.get("gets", []))
        if x["audience"] == "ecom":
            acts = (f'<a class="btn" href="{rel}{x["href"]}">Try the free calculator</a>'
                    f'<a class="st-link" href="{E(utm(x["checkout"], "shop", x["campaign"]))}" rel="noopener">Buy the workbook, ${E(x["price"])}{ARROW}</a>')
            cadence = "Instant download."
        else:
            t = x.get("trial")
            buy_label = f"Start your {t}-day free trial" if t else f"Subscribe, ${E(x['price'])} {E(x['per'])}"
            acts = (f'<a class="btn" href="{rel}{x["href"]}{x["sample"]}">See this week\'s free sample</a>'
                    # shop keeps the trial as a full button (Todd's go on store v2, Oct 24, 2026: shoppers here are comparing lists to buy)
                    + (f'<a class="st-btn2" href="{E(utm(x["checkout"], "shop", x["campaign"]))}" rel="noopener">{buy_label}</a>' if x.get("checkout") else ""))
            cadence = (f"New list every Monday. {t} days free, then ${E(x['price'])} {E(x['per'])}." if t else "New list every Monday. Cancel any time.")
        rows += (f'<article class="sh-item" data-aud="{x["audience"]}" data-key="{E(x["key"])}"><div class="sh-main"><p class="st-tag">{E(x["tag"])}</p>'
                 f'<h2>{nb(x["name"])}</h2><p>{E(x["what"])}</p></div>'
                 f'<div class="sh-buy"><div class="amt">${E(x["price"])}<small> {E(x["per"])}</small></div><p>{cadence}</p>{acts}'
                 + (f'<p class="st-note">Secure checkout by Gumroad. Your card goes in at checkout and nothing is charged for {x["trial"]} days. '
                    f'Cancel in your Gumroad library before day {x["trial"]} and you pay nothing. <a href="{rel}refunds/">Refunds and cancelling</a></p></div>'
                    if x.get("trial") else f'<p class="st-note">Secure checkout by Gumroad. <a href="{rel}refunds/">Refunds and cancelling</a></p></div>')
                 + f'<div class="sh-gets"><h3 class="sr">What you get</h3><ul class="checks">{gets}</ul><p class="sh-src">{E(x.get("source", ""))}</p></div></article>')
    seat_row = shop_seat_row(rel)
    if seat_row:   # the $149 daily pest seat sits right under the restaurant list it comes from (design review, Oct 24)
        cut = rows.find('<article class="sh-item"', rows.find('data-key="chicago-restaurant-inspection-leads"') + 1)
        rows = rows + seat_row if cut < 0 or 'data-key="chicago-restaurant-inspection-leads"' not in rows else rows[:cut] + seat_row + rows[cut:]
    area_row = shop_area_row(rel)
    if area_row:   # the area seats sit right under the $29 Chicago cleaning list they come from (as the pest seat does)
        key = 'data-key="chicago-construction-cleaning-leads"'
        cut = rows.find('<article class="sh-item"', rows.find(key) + 1) if key in rows else -1
        rows = rows + area_row if cut < 0 else rows[:cut] + area_row + rows[cut:]
    coming = store_coming()
    if coming:
        rows += coming_card(coming, rel, "shopLic", cls="sh-item soon", h="h2").replace('<article class="sh-item soon">', '<article class="sh-item soon" data-aud="trade">', 1)
    filt = ('<div class="st-filter" role="group" aria-label="Show products for" id="shFilter">'
            '<button type="button" aria-pressed="true" data-a="all">All</button>'
            '<button type="button" aria-pressed="false" data-a="trade">Trades</button>'
            '<button type="button" aria-pressed="false" data-a="ecom">E-commerce</button></div><p class="sr" id="shCount" aria-live="polite"></p>')
    body = (f'{crumb}<p class="eyebrow">Lead lists and finance tools</p><h1>Pick the list that finds your customers.</h1>'
            '<p class="lede">Every list opens with this week\'s free sample. Subscribe when it fits; cancel any time.</p>'
            f'<div class="sh-list" id="shList">{rows}</div>'
            '<div class="sh-two"><div class="card"><h2>Refunds and cancelling</h2>'
            f'<p>{E(load_store().get("refunds", {}).get("lists", ""))}</p><p><a href="{rel}refunds/">The full policy</a></p></div>'
            '<div class="card"><h2>What these lists are, and are not</h2><p>Public City records, filtered and sorted for one trade, with the date '
            'we pulled them. We never contact anyone for you, and no business on a list endorses or works with ProofNotFluff. Not legal or '
            'business advice and no promise of work.</p></div></div>')
    script = ("<script>(function(){var f=document.getElementById('shFilter');if(!f)return;"
              "var bs=[].slice.call(f.querySelectorAll('button')),it=[].slice.call(document.querySelectorAll('#shList [data-aud]'));"
              "bs.forEach(function(b){b.addEventListener('click',function(){var a=b.dataset.a;bs.forEach(function(x){x.setAttribute('aria-pressed',String(x===b))});"
              "var n=0;it.forEach(function(e){e.hidden=!(a==='all'||e.dataset.aud===a);if(!e.hidden)n++});"
              "document.getElementById('shCount').textContent='Showing '+n+' of '+it.length+' products'})})})();</script>")
    ld = ld_tags(crumb_ld, *[product_ld(x, BASE + x["href"]) for x in prods])
    script = ""   # the All / Trades / E-commerce filter came off with six products (design review, Oct 24)
    return (HEAD.format(title="Shop: lead lists for cleaning, hood cleaning and pest control | ProofNotFluff",
                        desc="Weekly lead lists from Chicago and Austin public records, $29 or $39 a month with a free sample on every page, and the 13-Week E-commerce Cash Flow workbook.",
                        url=url, rel=rel, shop=SHOP, ld=ld, bodycls=' class="st-page"', robots="", analytics=analytics_tag()) + body +
            FOOT.format(rel=rel, script=script, notices=data_notices(), sources="Numbers on each list as dated on its page."))


def refunds_html():
    CURRENT["nav"] = ""
    rel = "../"
    url = BASE + "refunds/"
    r = load_store().get("refunds", {})
    crumb, crumb_ld = crumbs(rel, [("Home", ""), ("Refunds and cancelling", None)])
    body = (f'{crumb}<article class="prose"><p class="eyebrow">Policy</p><h1>Refunds and cancelling</h1>'
            f'<p class="lede">{E(r.get("lists", ""))}</p>'
            '<h2>Cancelling a list</h2><p>Each list is a monthly membership through Gumroad, our checkout. Cancel from the link in your Gumroad '
            'receipt or from your Gumroad library, any time, and you won\'t be charged again.</p>'
            '<h2>If something goes wrong</h2><p>If a Monday list does not arrive, the members\' app does not open or a file is broken, write to '
            '<a href="mailto:hello@proofnotfluff.com">hello@proofnotfluff.com</a> with your Gumroad receipt. We fix it, or refund that month.</p>'
            '<h2>Before you buy</h2><p>Every list has a free sample of this week\'s records on its page, and the workbook has a free calculator '
            'with the same math, so you can see what you get first.</p>'
            f'<p class="asof">Policy updated {E(nice_date(r.get("updated", "")))}. ProofNotFluff LLC, Chicago.</p></article>')
    return (HEAD.format(title="Refunds and cancelling | ProofNotFluff", desc="ProofNotFluff's refund and cancellation policy for the weekly lead lists and the workbook.",
                        url=url, rel=rel, shop=SHOP, ld=ld_tags(crumb_ld), bodycls=' class="st-page"', robots="", analytics=analytics_tag()) + body +
            FOOT.format(rel=rel, script="", sources=""))


def privacy_html():
    """/privacy/ (Legal desk FIX 2, legal/reviews/2026-10-22-monday-email-and-trial.md): what we collect, why, who holds it,
    never sold, how to stop, the contact. Every claim here matches how the funnel runs (email/M1-MONDAY.md, CLAUDE.md)."""
    CURRENT["nav"] = ""
    rel = "../"
    url = BASE + "privacy/"
    r = load_store().get("privacy", {})
    li = lambda xs: "<ul>" + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"
    mail = '<a href="mailto:hello@proofnotfluff.com">hello@proofnotfluff.com</a>'
    crumb, crumb_ld = crumbs(rel, [("Home", ""), ("Privacy", None)])
    body = (f'{crumb}<article class="prose"><p class="eyebrow">Policy</p><h1>Privacy</h1>'
            '<p class="lede">We collect as little as we can: an email address when you ask us for an email, and work contact details '
            'for the businesses we write to about leads. We never sell any of it.</p>'
            '<h2>What we collect</h2>' + li([
                "Your email address, when you sign up on this site for the free Monday jobs email, the New in Chicago email, a waitlist, product updates or the cleaning price cheat sheet.",
                "For businesses we email about leads: the business name, the decision maker&#39;s name and job title, and their work email, "
                "taken from public business records, the company&#39;s own website or an email finding service. We also keep your reply, "
                "such as a yes or a stop.",
                "When you buy a list: Gumroad, our checkout, gives us your name, your email and what you bought. Gumroad takes the card; "
                "we never see your full card number.",
                "Visits: Cloudflare Web Analytics counts page views without cookies and without identifying you. The calculators run in your "
                "browser and never send what you type. Some calculators also count, as an anonymous page view of a fixed address on this site, "
                "that someone used the calculator or clicked through to buy; no number you type is part of that count. In the members&#39; apps, contacted marks and notes stay in your own browser."]) +
            '<h2>Why</h2>' + li([
                "To send the email you asked for and to answer you.",
                "For businesses we email: to ask whether you want the free Monday email, with at most two follow ups, and to send it if you say yes.",
                "For members: to deliver the list and run your membership."]) +
            '<h2>Who holds it</h2>' + li([
                "Kit, our email provider, holds sign ups from this site and sends the Monday email to them.",
                "Our CRM, a private database only ProofNotFluff can open, kept in our Claude workspace (run by Anthropic), holds the business "
                "contacts and whether each said yes or stop.",
                "Google runs our inbox, so the emails you send us and our replies sit in Gmail.",
                "Gumroad holds checkout and membership records."]) +
            '<p>Nobody else gets it. Our site code and a few encrypted contact records sit on GitHub, where only we hold the key, and the email '
            'finding service gets only what we look up: a business website and, at times, the owner&#39;s name. We never sell or rent your '
            'details, and never share them for anyone else&#39;s marketing.</p>'
            '<h2>How to stop</h2>' + li([
                "Reply &quot;stop&quot; to any email from us, or use the unsubscribe link at the foot of any email Kit sends. "
                "We take you off before the next send, and you won&#39;t get another one.",
                f'Members cancel in their Gumroad library (see <a href="{rel}refunds/">Refunds and cancelling</a>).',
                f"To see what we hold about you, or to have it deleted, write to {mail}. We keep only the note that you asked us to stop, "
                "so we never email you again."]) +
            '<h2>Changes and tracking</h2><p>If this policy changes, the date below changes and the new text goes on this page; we do not '
            'email about changes. This site does not respond to browser Do Not Track signals, because it does not track you across sites '
            'in the first place. The Monday email form sends your address straight to Kit, which has its own privacy policy.</p>' +
            '<h2>Contact</h2>'
            f'<p>ProofNotFluff LLC, 680 North Lake Shore Drive, Suite 110-2964, Chicago, IL 60611. {mail}</p>'
            f'<p class="asof">Policy updated {E(nice_date(r.get("updated", "")))}.</p></article>')
    foot = (f'</main>\n<footer><div class="wrap">{foot_nav(rel)}'
            '<p>Made by ProofNotFluff LLC. Questions about this policy: hello@proofnotfluff.com.</p></div></footer>\n</body></html>')
    return (HEAD.format(title="Privacy: what this site collects and why | ProofNotFluff", desc="What ProofNotFluff collects, why, who holds it, and how to stop. We never sell your details.",
                        url=url, rel=rel, shop=SHOP, ld=ld_tags(crumb_ld), bodycls=' class="st-page"', robots="", analytics=analytics_tag()) + body + foot)


def calculators_html():
    """The calculator catalog (store v2, Oct 24, 2026, Todd: "organizing calculators with a search feature given the large
    number we have"): instant search with synonyms and category chips, every card in the HTML so search engines and
    no-script readers still see all of them; the script in assets/pnf-ui.js only hides what does not match."""
    CURRENT["nav"] = "calc"
    rel = "../"
    url = BASE + "calculators/"
    st = load_store()
    syn = st.get("searchSynonyms", {})
    crumb, crumb_ld = crumbs(rel, [("Home", ""), ("Free calculators", None)])
    n = sum(len(i) for _, i in CALC_GROUPS)
    gid = lambda t: "".join(ch if ch.isalnum() else "-" for ch in t.lower()).strip("-").replace("--", "-")
    chips = ('<button type="button" class="cx-chip" aria-pressed="true" data-g="">All <span>' + str(n) + '</span></button>'
             + "".join(f'<button type="button" class="cx-chip" aria-pressed="false" data-g="{gid(t)}">{E(t)} <span>{len(items)}</span></button>' for t, items in CALC_GROUPS))
    start = [p for s_ in st.get("doorCalcs", [])[:4] for _, items in CALC_GROUPS for p in items if p["slug"] == s_]
    card = lambda p, g, vt=True: (f'<li class="cx-item" data-g="{gid(g)}" data-k="{E((p["h1"] + " " + p["card"] + " " + g + " " + syn.get(p["slug"], "")).lower())}">'
                         f'<a href="{rel}{p["slug"]}/"><span class="cx-tag">{E(g)}</span><b{f' style="view-transition-name:c-{p["slug"]}"' if vt else ""}>{E(p["h1"])}</b><span class="cx-d">{E(p["card"])}</span></a></li>')
    groups = "".join(f'<section class="cx-group" data-g="{gid(t)}" aria-labelledby="cx-{gid(t)}"><h2 class="st-cgroup" id="cx-{gid(t)}">{E(t)}</h2>'
                     f'<ul class="cx-grid">{"".join(card(p, t) for p in items)}</ul></section>' for t, items in CALC_GROUPS)
    start_html = (f'<section class="cx-start" aria-labelledby="cx-start"><h2 class="st-cgroup" id="cx-start">Start here</h2><ul class="cx-grid">'
                  + "".join(card(p, next(t for t, items in CALC_GROUPS if p in items), False) for p in start) + '</ul></section>') if start else ""
    # the h1 names what the hub holds (SEO audit, Oct 24, 2026); the old line leads the lede
    body = (f'{crumb}<p class="eyebrow">Free calculators</p><h1>Free pricing and money calculators</h1>'
            f'<p class="lede">Price the job before you call. {n} free calculators with the same math as our Excel and Google Sheets workbooks. Nothing you type leaves your browser.</p>'
            '<div class="cx-bar" id="cxBar"><label class="cx-search"><span class="sr">Search the calculators</span>'
            '<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
            '<input id="cxQ" type="search" placeholder="Search: house cleaning, Amazon, hourly rate..." autocomplete="off" enterkeyhint="search"><kbd aria-hidden="true">/</kbd></label>'
            f'<div class="cx-chips" role="group" aria-label="Filter by category">{chips}</div>'
            '<p class="cx-count" id="cxCount" aria-live="polite"></p></div>'
            f'<div id="cxAll">{start_html}{groups}</div>'
            '<div class="cx-empty" id="cxEmpty" hidden><p><b>No calculator matches that yet.</b> Try a trade (cleaning, junk, lawn), a platform (Amazon, Etsy, Airbnb) or a word like price, rate or tax.</p>'
            '<p><button type="button" class="st-btn2" id="cxClear">Show all calculators</button> <a class="st-link" href="mailto:hello@proofnotfluff.com?subject=Calculator%20idea">Suggest a calculator</a></p></div>')
    coll = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Free pricing and money calculators", "url": url,
            "mainEntity": {"@type": "ItemList", "numberOfItems": n, "itemListElement": [
                {"@type": "ListItem", "position": i, "url": BASE + p["slug"] + "/", "name": p["h1"]}
                for i, p in enumerate((p for _, items in CALC_GROUPS for p in items), 1)]}}
    return (HEAD.format(title="Free pricing and money calculators | ProofNotFluff", desc=f"{n} free calculators for cleaning and trade pricing, e-commerce cash flow and margins, tax, rentals and household budgets.",
                        url=url, rel=rel, shop=SHOP, ld=ld_tags(crumb_ld, coll), bodycls=' class="st-page cx-page"', robots="", analytics=analytics_tag()) + body +
            FOOT.format(rel=rel, script="", sources=""))


def search_index(live):
    """docs/assets/search.json for the site-wide quick-find (store v2): every live calculator, lead list and question page,
    with the words a visitor might type. Loaded only when someone opens the search."""
    st = load_store()
    syn = st.get("searchSynonyms", {})
    group_of = {p["slug"]: t for t, items in CALC_GROUPS for p in items}
    out = []
    for x in store_products():
        out.append({"t": x["name"], "s": x["href"], "g": "Lead list" if x["audience"] != "ecom" else "Workbook",
                    "d": x.get("card", ""), "k": " ".join([x.get("tag", ""), x.get("for", ""), st.get("searchListWords", {}).get(x["key"], "")]).lower()})
    seat = (_pages_by_slug().get("chicago-restaurant-inspection-leads") or {}).get("seat") or {}
    if seat.get("checkout"):
        out.append({"t": "Chicago Pest Control Daily Seat", "s": "chicago-restaurant-inspection-leads/#seat", "g": "Lead list",
                    "d": f"At most {seat['seats']} pest control companies, ${seat['price']} a month, new places each morning", "k": "pest control exterminator daily seat restaurants rodents"})
    if compare_page():
        cp = compare_page()
        out.append({"t": cp["h1"], "s": cp["slug"] + "/", "g": "Guide", "d": "Compared, with prices", "k": "compare constructconnect dodge buildzoom angi thumbtack planhub post construction cleaning leads chicago"})
    for q in LIVE_QUESTIONS:
        out.append({"t": q["h1"], "s": q["slug"] + "/", "g": "Guide", "d": q.get("eyebrow", ""), "k": q.get("eyebrow", "").lower()})
    for p in live:   # the free Chicago pages that are no calculator (Todd, Oct 27: trades news; the rat map)
        if p.get("kind") == "tradesnews":
            out.append({"t": p["h1"], "s": p["slug"] + "/", "g": "Guide", "d": p.get("card", ""), "k": "news regulations permits licenses tax pay wages projects contractors trades chicago"})
        if p.get("kind") == "datapage":
            m = kind_module(p).META
            out.append({"t": m["h1"], "s": p["slug"] + "/", "g": "Chicago data", "d": m.get("card", ""), "k": m.get("keywords", "").lower()})
    if live_datapages():
        out.append({"t": "Free Chicago data", "s": "chicago-data/", "g": "Page", "d": "Every free Chicago data page in one place", "k": "chicago data trackers maps permits snow contracts"})
    for p in live:
        if p["slug"] in group_of:
            out.append({"t": p["h1"], "s": p["slug"] + "/", "g": "Calculator", "d": p.get("card", ""), "k": (group_of[p["slug"]] + " " + syn.get(p["slug"], "")).lower()})
    for s_, t_, d_ in (("shop/", "Shop: every lead list", "Compare the lists and prices"), ("calculators/", "All free calculators", "Search and filter all calculators"),
                       ("questions/", "Questions owners ask", "Plain answers with this week's numbers"), ("refunds/", "Refunds and cancelling", "The policy in plain words")):
        out.append({"t": t_, "s": s_, "g": "Page", "d": d_, "k": ""})
    return json.dumps(out, ensure_ascii=False, separators=(",", ":"))


def questions_html():
    CURRENT["nav"] = "questions"
    rel = "../"
    url = BASE + "questions/"
    crumb, crumb_ld = crumbs(rel, [("Home", ""), ("Questions", None)])
    hub = LIVE_QUESTIONS + ([compare_page()] if compare_page() else [])
    lis = "".join(f'<li><a href="{rel}{q["slug"]}/"><span><b>{E(q["h1"])}</b><small>{E(q.get("eyebrow", ""))}</small></span>{ARROW}</a></li>' for q in hub)
    body = (f'{crumb}<p class="eyebrow">Plain answers, with this week\'s numbers</p><h1>Questions owners ask</h1>'
            '<p class="lede">Real questions trade and e-commerce owners asked in public, answered from City records and our own workbooks. ProofNotFluff is run by a finance executive.</p>'
            f'<ul class="st-qs">{lis}</ul>')
    coll = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Questions owners ask", "url": url,
            "mainEntity": {"@type": "ItemList", "numberOfItems": len(LIVE_QUESTIONS), "itemListElement": [
                {"@type": "ListItem", "position": i, "url": BASE + q["slug"] + "/", "name": q["h1"]} for i, q in enumerate(LIVE_QUESTIONS, 1)]}}
    return (HEAD.format(title="Questions owners ask | ProofNotFluff", desc="Plain answers to questions cleaning, hood cleaning, pest control and e-commerce owners ask, with this week's numbers.",
                        url=url, rel=rel, shop=SHOP, ld=ld_tags(crumb_ld, coll), bodycls=' class="st-page"', robots="", analytics=analytics_tag()) + body +
            FOOT.format(rel=rel, script="", sources=""))


def data_hub_html():
    """docs/chicago-data/: every free Chicago data page in one list, written once a data page is live (Oct 27, 2026)."""
    CURRENT["nav"] = ""
    rel = "../"
    url = BASE + "chicago-data/"
    crumb, crumb_ld = crumbs(rel, [("Home", ""), ("Free Chicago data", None)])
    hub = ([(p["slug"], p["h1"], p.get("card", "")) for p in PAGES_LIVE if p.get("kind") in ("tradesnews", "rodents")]
           + [(p["slug"], kind_module(p).META["h1"], kind_module(p).META.get("card", "")) for p in live_datapages()])
    lis = "".join(f'<li><a href="{rel}{s}/"><span><b>{E(h)}</b><small>{E(c)}</small></span>{ARROW}</a></li>' for s, h, c in hub)
    body = (f'{crumb}<p class="eyebrow">Free, from public records</p><h1>Free Chicago data for trade owners</h1>'
            '<p class="lede">Trackers and tools built from City, County, state and federal records, refreshed on their own schedule. Each page says where its numbers come from and when they were checked.</p>'
            f'<ul class="st-qs">{lis}</ul>')
    coll = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Free Chicago data for trade owners", "url": url,
            "mainEntity": {"@type": "ItemList", "numberOfItems": len(hub), "itemListElement": [
                {"@type": "ListItem", "position": i, "url": BASE + s + "/", "name": h} for i, (s, h, _) in enumerate(hub, 1)]}}
    return (HEAD.format(title="Free Chicago Data for Trade Owners | ProofNotFluff", desc="Free Chicago trackers and tools for trade business owners, built from public records: permits, snow, City contracts, rats and more.",
                        url=url, rel=rel, shop=SHOP, ld=ld_tags(crumb_ld, coll), bodycls=' class="st-page"', robots="", analytics=analytics_tag()) + body +
            FOOT.format(rel=rel, script="", sources=""))


def notfound_html():
    """docs/404.html: the host serves it for any missing address, so every link is root-relative (SEO audit, Oct 24, 2026:
    a dead pin or old link landed on the host's bare 404 with no way back in)."""
    CURRENT["nav"] = ""
    rel = "/"
    picks = [("chicago-restaurant-inspection-leads", "Chicago restaurant inspection leads", "This week's free sample for pest control, hood and kitchen cleaning"),
             ("chicago-construction-cleaning-leads", "Chicago construction cleaning leads", "Open projects near a final clean, with the builder on each"),
             ("cost-per-lead-calculator", "Cost per lead calculator", "What a won job really costs you in leads"),
             ("amazon-dd7-payout-calculator", "Amazon DD+7 payout calculator", "How long Amazon holds your money, and your cash low point")]
    lis = "".join(f'<li><a href="/{s}/"><b>{E(h)}</b><span>{E(c)}</span></a></li>' for s, h, c in picks if os.path.isdir(os.path.join(DOCS, s)))
    body = ('<p class="eyebrow">Page not found</p><h1>That page isn\'t here.</h1>'
            '<p class="lede">The link may be old or mistyped. These are the pages most people come for, or start from the <a href="/">home page</a>.</p>'
            f'<ul class="st-calcs">{lis}</ul><p class="st-all"><a class="st-btn2" href="/shop/">All lead lists</a> <a class="st-btn2" href="/calculators/">All free calculators</a></p>')
    return (HEAD.format(title="Page not found | ProofNotFluff", desc="This page isn't here. Find the lead lists and free calculators from the links on this page.",
                        url=BASE + "404.html", rel=rel, shop=SHOP, ld="", bodycls=' class="st-page"', robots='<meta name="robots" content="noindex">', analytics=analytics_tag())
            + body + FOOT.format(rel=rel, script="", sources=""))


def guides_block(product=None, calc=None, rel="../"):
    """Links from a product or calculator page to the live question pages that point at it, so links run both ways
    (SEO change, Todd's go Oct 22, 2026). Empty until a question page is live."""
    qs = [q for q in LIVE_QUESTIONS if (product and q.get("product") == product) or (calc and (q.get("calculator") or [None])[0] == calc)]
    cp = compare_page()
    if cp and product == "chicago-construction-cleaning-leads":   # the honest comparison sits with the Chicago construction guides
        qs = qs + [cp]
    if not qs:
        return ""
    lis = "".join(f'<li><a href="{rel}{q["slug"]}/"><span><b>{E(q["h1"])}</b><small>{E(q.get("eyebrow", ""))}</small></span>{ARROW}</a></li>' for q in qs)
    return f'<section class="block"><h2>Guides</h2><ul class="st-qs">{lis}</ul></section>'


def related_calcs(slug, rel="../"):
    """Related calculators on a calculator page: up to 6 live calculators from every cluster in site/store.json
    calcRelated that holds this page, in cluster order (SEO audit, Oct 24, 2026: 37 of 45 calculators linked to no other
    calculator, so search engines saw 45 loose tools instead of topic clusters)."""
    live = {p["slug"]: p for p in PAGES_LIVE}
    seen, out = {slug}, []
    for cluster in load_store().get("calcRelated", []):
        if slug not in cluster:
            continue
        for s in cluster:
            if s not in seen and s in live:
                seen.add(s)
                out.append(live[s])
    if not out:
        return ""
    lis = "".join(f'<li><a href="{rel}{p["slug"]}/"><b>{E(p["h1"])}</b><span>{E(p["card"])}</span></a></li>' for p in out[:6])
    return f'<section class="block rel-calcs" aria-labelledby="rel-title"><h2 id="rel-title">Related calculators</h2><ul class="st-calcs">{lis}</ul></section>'


def find_customers(slug, rel="../"):
    """On a calculator page: the paid list (or the workbook) that fits the person who just priced a job."""
    st = load_store()
    keys = st.get("calcProducts", {}).get(slug)
    if not keys:
        return ""
    by = {x["key"]: x for x in store_products()}
    xs = [by[k] for k in keys if k in by]
    if not xs:
        return ""
    ecom = xs[0]["audience"] == "ecom"
    title = st.get("calcTitles", {}).get("ecom" if ecom else "trade", "")
    if ecom:
        x = xs[0]
        text = f'{x["name"]}: {x["what"]} ${x["price"]} {x["per"]}, Excel and Google Sheets.'
        acts = (f'<a class="st-btn2" href="{rel}{x["href"]}">See how it works</a>'
                f'<a class="st-link" href="{E(utm(x["checkout"], "calculator", x["campaign"], slug))}" rel="noopener">Buy, ${E(x["price"])}</a>')
    else:
        text = " ".join(f'{x["name"]}: {x["nums"][0][0]} {x["nums"][0][1]}, ${x["price"]} {x["per"]}.' for x in xs) + " Free sample on each page, new every Monday."
        labs = [x["tag"].split(" · ")[0] for x in xs]
        if len(set(labs)) < len(labs):   # two lists in one city (Oct 26): a short trade word per list, one line at every width
            SHORT = {"chicago-restaurant-inspection-leads": "Restaurants", "chicago-construction-cleaning-leads": "Construction",
                     "austin-construction-cleaning-leads": "Austin construction", "chicago-new-business-licenses": "New businesses"}
            labs = [SHORT.get(x["key"], x["name"]) for x in xs]
        acts = "".join(f'<a class="st-btn2" href="{rel}{x["href"]}{x["sample"]}">{E(lab)}: free sample</a>' for x, lab in zip(xs, labs))
    return (f'<section class="block"><div class="fc"><div><h2>{E(title)}</h2><p>{E(text)}</p></div>'
            f'<div class="fc-acts">{acts}</div></div></section>')


# Open Graph images: one 1200 x 630 card per page, drawn here with the brand's own fonts (docs/assets/fonts) so a shared link
# shows the page's promise. A card is redrawn only when its words change (the words' hash is kept in the PNG), so the
# committed images stay byte for byte what this script makes (tools/check_repo.py site-sync).
OG_DIR = os.path.join(DOCS, "assets", "og")


def og_image(slug, eyebrow, title, sub=""):
    import hashlib
    try:
        from PIL import Image, ImageDraw, ImageFont
        from PIL.PngImagePlugin import PngInfo
    except ImportError:
        return
    os.makedirs(OG_DIR, exist_ok=True)
    f = os.path.join(OG_DIR, slug + ".png")
    key = hashlib.sha256(json.dumps([3, eyebrow, title, sub]).encode()).hexdigest()[:16]
    if os.path.isfile(f):
        try:
            if Image.open(f).text.get("pnf") == key:
                return
        except Exception:
            pass
    fonts = os.path.join(DOCS, "assets", "fonts")
    P7, P6, I4 = (os.path.join(fonts, n) for n in ("poppins-700.woff2", "poppins-600.woff2", "inter-400.woff2"))
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), "#f3f1ec")
    d = ImageDraw.Draw(im)
    x0 = 80
    for i, c in enumerate(("#c8502f", "#2e6b66", "#6b4fa0", "#2f5f9e", "#a87c1f")):
        d.rounded_rectangle([x0 + i * 62, 76, x0 + i * 62 + 52, 90], 7, fill=c)
    d.text((x0, 132), eyebrow.upper(), font=ImageFont.truetype(P6, 26), fill="#a63e21")

    def wrap(text, font, width):
        lines, cur = [], ""
        for w in text.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=font) <= width:
                cur = t
            else:
                lines.append(cur); cur = w
        return lines + [cur] if cur else lines
    size = 66
    while True:
        ft = ImageFont.truetype(P7, size)
        lines = wrap(title, ft, W - 2 * x0)
        if len(lines) <= 3 or size <= 44:
            break
        size -= 4
    y = 180
    for ln in lines[:4]:
        d.text((x0, y), ln, font=ft, fill="#1d2433")
        y += int(size * 1.14)
    if sub and y < H - 96 - 110:
        fs = ImageFont.truetype(I4, 28)
        y += 26
        for ln in wrap(sub, fs, W - 2 * x0)[:2]:
            d.text((x0, y), ln, font=fs, fill="#4a5163")
            y += 40
    d.rectangle([0, H - 96, W, H], fill="#1d2433")
    d.text((x0, H - 66), "ProofNotFluff", font=ImageFont.truetype(P7, 30), fill="#ffffff")
    d.text((W - x0, H - 62), "proofnotfluff.com", font=ImageFont.truetype(P6, 24), fill="#c9cfdb", anchor="ra")
    meta = PngInfo()
    meta.add_text("pnf", key)
    im.save(f, "PNG", pnginfo=meta, optimize=True)


def og_all(pages, live):
    og_image("home", "Lead lists from public records", "Sales leads from the City's own records, every Monday.",
             "Weekly lists for cleaning, hood cleaning and pest control in Chicago and Austin.")
    og_image("shop", "ProofNotFluff shop", "Pick the list that finds your customers.", "Free sample on every list, new every Monday.")
    og_image("refunds", "Policy", "Refunds and cancelling")
    og_image("privacy", "Policy", "Privacy", "What we collect, why, and how to stop. Never sold.")
    og_image("questions", "Questions owners ask", "Plain answers, with this week's numbers")
    og_image("calculators", "Free calculators", "Price the job before you call", "Free pricing and money calculators, the same math as our workbooks.")
    for x in json.load(open(os.path.join(ROOT, "site", "extras.json"), encoding="utf-8")).get("pages", []) if os.path.exists(os.path.join(ROOT, "site", "extras.json")) else []:
        og_image(x["slug"], "Free printable", x["h1"], x.get("card", ""))
    import re
    clean = lambda t: re.sub(r"\s+", " ", re.sub(r"\{[^}]*\}", "", t or "")).strip()
    for p in pages:
        if p.get("kind") in ("leads", "restleads", "question", "licleads", "newin") and not os.path.isfile(os.path.join(ROOT, p["data"])):
            continue
        if p.get("kind") == "datapage" and not datapage_ready(p):
            continue
        og_image(p["slug"], clean(p.get("eyebrow")) or "ProofNotFluff", clean(p["h1"]), clean(p.get("card")))


def write_stage_pages(pages):
    """docs/e/<slug>/use/ and docs/e/<slug>/upgrade/ for pages with "stages": tiny noindex pages holding only the
    cookie-free analytics tag, loaded in a hidden frame by PNF.stages so Cloudflare Web Analytics counts each stage
    as a page view of a fixed address. No number a visitor types is ever part of the address or sent anywhere."""
    for p in pages:
        if not p.get("stages") or not is_live(p):
            continue
        for kind in ("use", "upgrade"):
            d = os.path.join(DOCS, "e", p["slug"], kind); os.makedirs(d, exist_ok=True)
            open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(
                f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow">'
                f'<link rel="icon" href="data:,"><title>Count: {E(kind)}</title>{analytics_tag()}</head><body></body></html>')


def main():
    spec = json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))
    pages = spec["pages"]
    live = [p for p in pages if is_live(p)]
    LIVE_QUESTIONS[:] = [p for p in live if p.get("kind") == "question"]
    PAGES_LIVE[:] = live
    PAGES_ALL[:] = pages
    og_all(pages, live)
    for p in pages:
        if p.get("kind") in ("leads", "restleads", "question", "licleads", "newin") and not os.path.isfile(os.path.join(ROOT, p["data"])):
            print("skipped", p["slug"], "(no data yet)")
            continue
        if p.get("kind") == "datapage" and not datapage_ready(p):   # a noindex stub until its module lands (never live, never linked)
            CURRENT["nav"] = ""
            out = os.path.join(DOCS, p["slug"]); os.makedirs(out, exist_ok=True)
            open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(
                HEAD.format(title=E(p["title"]), desc=E(p.get("eyebrow", "")), url=BASE + p["slug"] + "/", rel="../", shop=SHOP, ld="", bodycls=' class="st-page"',
                            robots='<meta name="robots" content="noindex, nofollow">', analytics="")
                + f'<h1>{E(p["h1"])}</h1><p class="lede">This page is being built.</p>' + FOOT.format(rel="../", script="", sources=""))
            print("stub", p["slug"], f"(no tools/{p.get('module')}.py yet)")
            continue
        CURRENT["nav"] = "questions" if p.get("kind") == "question" else ("shop" if p.get("kind") in ("leads", "restleads", "licleads") else ("news" if p.get("kind") == "tradesnews" else "" if p.get("kind") in ("newin", "rodents", "agentkit", "datapage") else "calc"))
        out = os.path.join(DOCS, p["slug"]); os.makedirs(out, exist_ok=True)
        open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page_html(p))
        if p.get("kind") == "tradesnews":   # the brief's RSS feed sits next to it
            import news_site
            open(os.path.join(out, "feed.xml"), "w", encoding="utf-8").write(news_site.feed_xml(p, news_site.load(p)))
        mod = kind_module(p) if p.get("kind") in ("rodents", "datapage") else None
        if mod and hasattr(mod, "extra_pages"):   # sub-pages under the page's own folder (one per community area, say)
            for relpath, page in mod.extra_pages(p):
                f = os.path.normpath(os.path.join(out, relpath))
                if not f.startswith(out + os.sep):
                    sys.exit(f"{p['slug']}: extra page outside its folder: {relpath}")
                os.makedirs(os.path.dirname(f), exist_ok=True)
                open(f, "w", encoding="utf-8").write(page)
                if is_live(p) and relpath.endswith("index.html"):
                    EXTRA_URLS[BASE + p["slug"] + "/" + relpath[:-len("index.html")]] = mod.lastmod(p) if hasattr(mod, "lastmod") else None
        CURRENT["nav"] = ""
        print("wrote", p["slug"])
    open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8").write(home_html(pages, live))
    # two front doors draft (move 5): noindex, not in the sitemap, not linked; goes live only on Todd's go
    open(os.path.join(DOCS, "home-two-doors.html"), "w", encoding="utf-8").write(home_html(pages, live, doors=True))
    store = ([("shop", shop_html()), ("refunds", refunds_html()), ("privacy", privacy_html()), ("calculators", calculators_html())] + ([("questions", questions_html())] if LIVE_QUESTIONS else [])
             + ([("chicago-data", data_hub_html())] if live_datapages() else []))
    for slug, page in store:
        d = os.path.join(DOCS, slug); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page)
    open(os.path.join(DOCS, "404.html"), "w", encoding="utf-8").write(notfound_html())
    open(os.path.join(DOCS, "assets", "search.json"), "w", encoding="utf-8").write(search_index(live))
    CURRENT["nav"] = ""
    for x in live_extras():
        normalize_extra(x["slug"], x["h1"])
    write_hub_and_redirects(pages)
    # Todd's go, Oct 25: the dated answers are on the live lead pages (answer_box) and the comparison page is live
    write_compare_draft()
    write_stage_pages(pages)
    urls = ([BASE] + [BASE + slug + "/" for slug, _ in store] + [BASE + p["slug"] + "/" for p in live]
            + [BASE + x["slug"] + "/" for x in live_extras()] + ([BASE + compare_page()["slug"] + "/"] if compare_page() else []))
    lastmod = {}
    for p in live:   # a lead page changes when its data does (radar, Oct 23): the sitemap says the true day
        if p.get("kind") in ("leads", "restleads", "licleads", "rodents") and data_date(p.get("data")):
            lastmod[BASE + p["slug"] + "/"] = data_date(p.get("data"))
        if p.get("kind") == "tradesnews":
            import news_site
            lastmod[BASE + p["slug"] + "/"] = news_site.load(p)["updated"]
        if p.get("kind") == "datapage" and hasattr(kind_module(p), "lastmod") and kind_module(p).lastmod(p):
            lastmod[BASE + p["slug"] + "/"] = kind_module(p).lastmod(p)
    for u, m in EXTRA_URLS.items():   # a data page's sub-pages (extra_pages)
        urls.append(u)
        if m:
            lastmod[u] = m
    for q in LIVE_QUESTIONS:   # a question page changes when its data does
        try:
            dd = json.load(open(os.path.join(ROOT, q["data"]), encoding="utf-8"))
            m = ((dd.get("source") or {}).get("fetchedAt") or dd.get("asOf") or "")[:10]
            if len(m) == 10 and m[4] == "-":
                lastmod[BASE + q["slug"] + "/"] = m
        except (OSError, ValueError):
            pass
    open(os.path.join(DOCS, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        "".join(f"  <url><loc>{u}</loc><lastmod>{lastmod.get(u, spec['updated'])}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    open(os.path.join(DOCS, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n")
    open(os.path.join(DOCS, INDEXNOW_KEY + ".txt"), "w").write(INDEXNOW_KEY)
    for p in pages:
        if chr(0x2014) in json.dumps(p, ensure_ascii=False):
            sys.exit(f"em dash in {p['slug']}")


def answer_text(p):
    """The 2 to 3 sentence dated answer for the top of a lead page (research_notes/ai-recommendation-2026-10-23.md item 4),
    every number read from the page's own data file. Draft only until Todd's go (Oct 24: "Build as drafts")."""
    d = json.load(open(os.path.join(ROOT, p["data"]), encoding="utf-8"))
    c, asof = d.get("counts") or {}, nice_date(d["source"]["fetchedAt"])
    k = p.get("kind")
    if k == "leads":
        near = int(c.get("nearFinish") or 0)
        near_s = (f' {near:,} {"has" if near == 1 else "have"} {E(p.get("nearLede", p.get("nearSub", "partial occupancy approved")))}, so a final clean is close.'
                  if near else "")
        return (f'Where to find post-construction cleaning leads in {E(p["city"])}: the City\'s building permit records list the general contractor '
                f'on big jobs. As of {E(asof)}, {int(c["kept"]):,} apartment and commercial projects of $500,000 or more are open.{near_s} '
                'This page lists them with the builder on each, refreshed every Monday.')
    if k == "restleads":
        return ('How pest control, hood cleaning and kitchen cleaning companies find restaurant clients in Chicago: the City posts its food '
                'inspections, and a failed or conditional result with a pest, hood, grease trap or cleaning violation is a dated reason to call. '
                f'In the 30 days to {E(d.get("throughText") or asof)}, {int(c["flagged"]):,} Chicago food businesses had one. This page sorts them by the violation that fits your trade.')
    if k == "licleads":
        return ('How vendors find new businesses in Chicago: the City records each new business license with its address and license type. '
                f'In the week to {E(nice_date(d["window"]["to"]))}, {int(c["keptWeek"]):,} business sites got one, and {int(c["kept30"]):,} in the last 30 days. '
                'This page sorts them by trade, refreshed every Monday.')
    return ""


def answer_box(p):
    """The dated short answer on a live lead page (Todd's go, Oct 25, 2026, on the Oct 24 drafts; research_notes/
    ai-recommendation-2026-10-23.md: answer-first, dated, sourced passages get cited more). It sits right after the counts,
    inside the first screen or two, and every number comes from the page's own data file."""
    text = answer_text(p)
    if not text:
        return ""
    try:
        d = json.load(open(os.path.join(ROOT, p["data"]), encoding="utf-8"))
        when = nice_date((d.get("source") or {}).get("fetchedAt") or d.get("asOf") or "")
    except (OSError, ValueError, KeyError):
        when = ""
    tag = "The short answer" + (f' <span>· updated {E(when)}</span>' if when else "")
    return f'<div class="ld-answer" role="note"><p class="qa-tag">{tag}</p><p>{text}</p></div>'


def write_answer_drafts(pages):
    """Draft copies of the live lead pages with the dated answer under the h1: docs/answer-draft-<slug>/index.html,
    noindex, not in the sitemap, not linked. The live pages are unchanged until Todd's go (visible change, major)."""
    style = ("<style>.ld-answer{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--ink);border-radius:12px;"
             "padding:16px 20px;margin:14px 0 4px;max-width:760px}.ld-answer .qa-tag{font:600 12px/1 Poppins,system-ui,sans-serif;"
             "letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 10px}.ld-answer p:last-child{margin:0;font-size:17px;"
             "line-height:1.6;color:var(--ink)}</style>")
    for p in pages:
        if p.get("kind") not in ("leads", "restleads", "licleads") or not is_live(p):
            continue
        live = os.path.join(DOCS, p["slug"], "index.html")
        if not os.path.isfile(live):
            continue
        html = open(live, encoding="utf-8").read()
        text = answer_text(p)
        if not text or "</h1>" not in html or "<head>" not in html:
            continue
        block = f'<div class="ld-answer" role="note"><p class="qa-tag">The short answer</p><p>{text}</p></div>'
        html = html.replace("</h1>", "</h1>" + block, 1).replace("<head>", '<head><meta name="robots" content="noindex, nofollow">', 1)
        html = html.replace("</head>", style + "</head>", 1)
        out = os.path.join(DOCS, "answer-draft-" + p["slug"]); os.makedirs(out, exist_ok=True)
        open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(html)


COMPARE_FILE = os.path.join(ROOT, "site", "compare-chicago-construction.json")


def compare_page():
    """The comparison page's slug and title, or None (used by the sitemap, the guides and the search index)."""
    if not os.path.isfile(COMPARE_FILE):
        return None
    d = json.load(open(COMPARE_FILE, encoding="utf-8"))
    return {"slug": d["slug"], "h1": d["title"], "eyebrow": "Compared, with prices", "updated": d.get("updated", "")}


def write_compare_draft():
    """The honest comparison page (research_notes/ai-recommendation-2026-10-23.md item 7), from site/compare-chicago-construction.json:
    every price read on a vendor page, third-party estimates labeled, our row labeled and never ranked first. Live on Todd's go
    (Oct 25, 2026); it was a noindex draft from Oct 24. Ends on the next step, quietly (peak-end)."""
    if not os.path.isfile(COMPARE_FILE):
        return
    d = json.load(open(COMPARE_FILE, encoding="utf-8"))
    CURRENT["nav"] = "questions" if LIVE_QUESTIONS else ""
    rel = "../"
    kind = {"vendor": "the company's own page", "third-party": "a third-party estimate", "listing": "a third-party listing", "city": "the City's dataset page", "ours": "our page"}
    rows = "".join(
        f'<article class="cmp-row{" cmp-ours" if x.get("sourceKind") == "ours" else ""}"><h2>{E(x["name"])}</h2><p>{E(x["what"])}</p>'
        f'<dl class="ld-meta"><div><dt>Price</dt><dd>{E(x["price"])}</dd></div><div><dt>What you get</dt><dd>{E(x["gets"])}</dd></div>'
        f'<div><dt>The catch</dt><dd>{E(x["con"])}</dd></div></dl>'
        f'<p class="cmp-src">Source: <a href="{E(x["sourceUrl"])}" rel="noopener">{E(kind.get(x.get("sourceKind"), "source"))}</a>, read {E(nice_date(x["readOn"]))}.</p></article>'
        for x in d["sources"])
    url = BASE + d["slug"] + "/"
    crumb, crumb_ld = crumbs(rel, [("Home", ""), ("Questions", "questions/"), ("Compared, with prices", None)] if LIVE_QUESTIONS else [("Home", ""), ("Compared, with prices", None)])
    chi = next((x for x in store_products() if x["key"] == "chicago-construction-cleaning-leads"), None)
    nxt = ('<section class="block"><h2>Next step</h2><ul class="qa-rel">'
           + (f'<li><a href="{rel}{chi["href"]}{chi["sample"]}">See this week\'s free sample of the City-record list</a></li>' if chi else "")
           + f'<li><a href="{rel}cost-per-lead-calculator/">Work out what a won job costs you in leads</a></li>'
           + f'<li><a href="{rel}price-post-construction-cleaning-bid/">Price the bid before you call</a></li></ul></section>')
    body = (f'{crumb}<article class="qa"><p class="eyebrow">Compared, with prices</p><h1>{E(d["title"])}</h1><p class="lede">{E(d["intro"])}</p>'
            f'<p class="asof">Updated {E(nice_date(d.get("updated", "")))}. Prices change; each row links the page it came from.</p>'
            f'<div class="cmp-list">{rows}</div>{nxt}</article>'
            '<style>.cmp-list{display:grid;gap:16px;margin:24px 0 0;max-width:860px}.cmp-row{background:var(--card);border:1px solid var(--line);'
            'border-radius:12px;padding:18px 20px}.cmp-row h2{font-size:21px;line-height:1.25;margin:0 0 6px}.cmp-row>p{margin:0 0 10px;color:var(--ink2)}'
            '.cmp-ours{border-left:4px solid var(--accent)}.cmp-src{font-size:14px;color:var(--muted)!important;margin:10px 0 0!important}</style>')
    art = {"@context": "https://schema.org", "@type": "Article", "headline": d["title"], "description": d["intro"], "mainEntityOfPage": url,
           "inLanguage": "en-US", "datePublished": d.get("updated", ""), "dateModified": d.get("updated", ""),
           "author": {"@type": "Organization", "name": "ProofNotFluff", "url": BASE},
           "publisher": {"@type": "Organization", "name": "ProofNotFluff", "url": BASE, "logo": {"@type": "ImageObject", "url": BASE + "assets/logo-512.png", "width": 512, "height": 512}}}
    html = (HEAD.format(title=E(d["title"]) + " | ProofNotFluff", desc=E(d.get("desc", d["intro"])[:158]), url=url, rel=rel, shop=SHOP, ld=ld_tags(crumb_ld, art),
                        bodycls=' class="ld-page"', robots="", analytics=analytics_tag(), ogtype="article") + body +
            FOOT.format(rel=rel, script="", notices="", sources="Each row names its source page and the day it was read."))
    out = os.path.join(DOCS, d["slug"]); os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(html)
    CURRENT["nav"] = ""


def add_product(argv):
    """make_site.py add <id> <listing id> <group key> "<name>" "<audience>": adds a newly listed Etsy product to
    site/links.json (hub card plus /go/<id>/) and rebuilds the site. Every run that lists a product runs it, and
    every promote run runs it before using a /go/<id>/ link that docs/go/<id>/ lacks."""
    pid, listing, group, name, audience = int(argv[0]), str(argv[1]), argv[2], argv[3], argv[4]
    f = os.path.join(ROOT, "site", "links.json")
    d = json.load(open(f, encoding="utf-8"))
    keys = [g["key"] for g in d["groups"]]
    if group not in keys:
        sys.exit(f"group must be one of {keys}")
    if not listing.isdigit():
        sys.exit("listing id must be digits only")
    if chr(0x2014) in name + audience:
        sys.exit("em dash in name or audience")
    d["products"] = [p for p in d["products"] if p["id"] != pid] + [
        {"id": pid, "name": name, "audience": audience, "channel": "etsy", "listing": listing}]
    for g in d["groups"]:
        g["ids"] = [i for i in g["ids"] if i != pid] + ([pid] if g["key"] == group else [])
    open(f, "w", encoding="utf-8").write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    main()
    print(f"added #{pid}: {BASE}go/{pid}/")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "add":
        add_product(sys.argv[2:])
    else:
        main()
