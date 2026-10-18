#!/usr/bin/env python3
"""Build the free calculator site (GitHub Pages, served from docs/) from site/pages.json.

Usage: python3 tools/make_site.py            writes docs/<slug>/index.html, docs/index.html,
                                             docs/sitemap.xml and docs/robots.txt
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
BASE = "https://proofnotfluff.com/"
SHOP = "https://proofnotfluff.etsy.com"
E = html.escape

HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}">
<link rel="canonical" href="{url}">{robots}{analytics}<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<meta property="og:type" content="website"><meta property="og:url" content="{url}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}assets/pnf.css">
{ld}
</head><body{bodycls}>
<header class="top"><div class="wrap"><div><a class="brand" href="{rel}">ProofNotFluff</a><div class="bars"><i></i><i></i><i></i><i></i><i></i></div></div>
<nav class="top"><a href="{rel}">Free calculators</a><a href="{shop}">Etsy shop</a></nav></div></header>
<main class="wrap">"""

FOOT = """</main>
<footer><div class="wrap">
<p>Estimates for planning only, based on the numbers you enter. Not tax, legal or financial advice. {sources}</p>
<p>Made by ProofNotFluff with AI assistance, reviewed and tested by the shop owner. Calculators run in your browser; nothing you type is sent anywhere.</p>
</div></footer>
<script src="{rel}assets/pnf-calc.js"></script>
{script}
</body></html>"""


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
            + (f'<div><a class="btn" href="{E(c["url"])}">{E(c["button"])}</a><br>' if c.get("url")
               else f'<div><span class="btn soon" aria-disabled="true">{E(c["button"])}</span><br>')
            + f'<a class="btn ghost" href="{SHOP}">All ProofNotFluff tools</a></div></div></section>')


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
<li><span>Cleaning hours (<span data-out="cleanHours" data-fmt="hrs">0</span>) and drive time at break-even</span><span data-out="laborCost">$0</span></li>
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


PAGE_KINDS = {"day_rate": day_rate_page, "cleaning_sqft": cleaning_sqft_page, "service": service_page, "service_sqft": service_sqft_page, "hourly": hourly_page, "cashflow": cashflow_page,
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
          ("SOME BUILDINGS FINALED", "Some buildings finaled", "hot"), ("PERMIT ACTIVE", "Permit active", "early")]   # Austin (no milestones)


def is_live(p):
    """A page is public when its draft flag is off; a leads page also needs its Kit waitlist form."""
    return not p.get("draft") and not (p.get("kind") == "leads" and not p.get("kitForm"))


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


def money(v, spell_billion=False):
    """One money rule on the leads pages (design director, Oct 17): $770K under $1M, $2.0M under $100M, whole millions
    from $100M up; "billion" is spelled out only in the hero tile."""
    d = max(0, int(float(v or 0) + 0.5))            # whole dollars; halves round up on integers, never on floats
    up = lambda n, unit: (2 * n + unit) // (2 * unit)   # n / unit rounded half up
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


def project_card(x, pill=True, city="Chicago", permit_label="Permit"):
    lab, cls = stage(x.get("milestone"))
    gc = "; ".join(x.get("gc") or [])
    units = f' · {x["units"]:,} homes' if x.get("units") else ""
    area = x.get("communityArea") or city
    pill_html = f'<p class="ld-pill s-{cls}">{E(lab)}</p>' if pill else ""
    return (f'<article class="ld-proj" data-type="{"new" if x["type"].startswith("New") else "ren"}" data-area="{E(area)}">{pill_html}'
            f'<div class="ld-ptop"><span class="ld-cost">{money(x["cost"])}</span><span class="ld-type">{E(x["type"])}{units}</span></div>'
            f'<p class="ld-scope">{E(x["scope"])}</p>'
            f'<dl class="ld-meta"><div><dt>Builder</dt><dd>{E(gc)}</dd></div>'
            f'<div><dt>Where</dt><dd>{E(x.get("address") or "")}, {E(area)}</dd></div>'
            f'<div><dt>{E(permit_label)}</dt><dd>{E(str(x.get("permit") or ""))}, issued {E(nice_date(x.get("issued", "")))}</dd></div></dl></article>')


LOCK = ('<svg class="ld-lock" viewBox="0 0 24 24" width="40" height="40" aria-hidden="true" focusable="false"><rect x="4.5" y="10.5" width="15" height="10" rx="2.2" '
        'fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M8 10.5V7.8a4 4 0 0 1 8 0v2.7" fill="none" stroke="currentColor" stroke-width="1.6"/>'
        '<circle cx="12" cy="15.3" r="1.4" fill="currentColor"/></svg>')


def leads_page_html(p):
    url = BASE + p["slug"] + "/"
    rel = "../"
    d = json.load(open(os.path.join(ROOT, p["data"]), encoding="utf-8"))
    c, src = d["counts"], d["source"]
    kept, cost = c["kept"], c["keptCost"]
    new_n = c.get("keptByType", {}).get("New construction", 0)
    near = d.get("nearFinish", [])
    n_near = c.get("nearFinish", len(near))
    n_big = len(d["projects"])
    asof = nice_date(src.get("rowsUpdatedAt") or src["fetchedAt"])
    price = E(str(p["price"]))
    buy_label = f"Get the full list: ${price} a month"
    checkout = p.get("checkout")
    # per-city wording (Austin, Oct 17): every key is optional and defaults to the Chicago page's words
    city = p["city"]
    card = lambda x, pill=True: project_card(x, pill, city, p.get("permitLabel", "Permit"))
    near_title = p.get("nearTitle", "Partial occupancy approved")
    near_sub = p.get("nearSub", "partial occupancy approved")
    near_text = p.get("nearText", "The City has approved temporary or partial occupancy on these projects, so a final clean is close.")
    area_word, area_all, area_filter = (p.get("areaWord", "Neighborhood"), p.get("areaAll", "All neighborhoods"),
                                        p.get("areaFilter", "a neighborhood filter"))

    def buy(cls="btn ld-btnbig", label=buy_label):
        return f'<a class="{cls}" href="{E(checkout)}" rel="noopener">{label}</a>' if checkout else ""

    # hero: two lines of promise, then the price and the action on the first screen (design director, Oct 17)
    lede = (f'{kept:,} open apartment and commercial projects over $500,000 in {E(p["city"])}, about {money(cost, True)} of work, '
            f'and the builders running them. {E(p["lede"])}')
    if checkout:
        hero_act = (f'<div class="ld-heroact" id="ldHeroCta">{buy()}<a class="ld-textlink" href="#near">See this week\'s sample</a></div>'
                    '<p class="ld-heronote">New list every Monday. Cancel any time.</p>')
    else:
        hero_act = '<div class="ld-heroact" id="ldHeroCta"><a class="ld-textlink" href="#ldCta">Join the waitlist</a></div>'
    tiles = (f'<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">Open projects</div><div class="val">{kept:,}</div><div class="sub">issued in the last 12 months, still open</div></div>'
             f'<div class="tile"><div class="lab">Reported cost</div><div class="val">{money(cost, True)}</div><div class="sub">{E(p.get("costSub", "as filed with the City"))}</div></div>'
             f'<div class="tile"><div class="lab">New buildings</div><div class="val">{new_n:,}</div><div class="sub">at least {c.get("keptUnits", 0):,} new apartments</div></div>'
             f'<div class="tile"><div class="lab">Near finish</div><div class="val">{n_near:,}</div><div class="sub">{E(near_sub)}</div></div></div>'
             f'<p class="asof">City data as of {E(asof)}. Refreshed every Monday.</p>')

    # near finish: the most valuable segment for a final clean, so the free page shows 2 and holds the rest back (owner, Oct 17)
    near_html = ""
    if near:
        show = near[:2]
        held = max(0, n_near - len(show))
        held_html = ""
        if held:
            noun = "building is" if held == 1 else "buildings are"
            held_html = (f'<div class="ld-held">{LOCK}<p class="ld-heldtxt"><b>{held:,} more near-finish {noun} in the full list</b>'
                         '<span>With the builder, address and permit for each, every Monday.</span></p>'
                         f'{buy("btn ld-btnbig") if checkout else ""}</div>')
        near_html = (f'<section class="block" id="near"><h2>{E(near_title)}</h2>'
                     f'<p>{E(near_text)} '
                     f'Here are {len(show)} of the {n_near:,} on this week\'s list.</p>'
                     f'<div class="ld-list">{"".join(card(x, pill=False) for x in show)}{held_html}</div></section>')

    gcs = "".join(f'<li><span class="ld-gname">{E(g["name"])}</span><span class="ld-gn">{g["projects"]}<span class="ld-gu"> open jobs</span></span>'
                  f'<span class="ld-gv">{money(g["cost"])}</span></li>' for g in c.get("topGCs", [])[:10])
    gc_more = (f'<p class="ld-gmore">The full list ranks every builder with open work. <a href="{E(checkout)}" rel="noopener">Get it for ${price} a month</a>.</p>'
               if checkout else "")
    gc_html = ('<section class="block"><h2>Builders with the most big jobs open</h2>'
               '<p>Counted from permits where the business is listed as general contractor.</p>'
               '<ol class="ld-gcs"><li class="ld-ghead"><span>Builder</span><span>Open jobs</span><span>Work</span></li>'
               f'{gcs}</ol>{gc_more}</section>')

    areas = sorted({x.get("communityArea") for x in d["projects"] if x.get("communityArea")})
    opts = "".join(f'<option value="{E(a)}">{E(a)}</option>' for a in areas)
    big_line = (f'The {n_big} biggest of {kept:,} open projects. Members get all {kept:,}, with {area_filter} and near-finish and new tabs, plus the Excel file.')
    big_html = ('<section class="block"><h2>Biggest open projects</h2>'
                '<div class="ld-filter" role="group" aria-label="Filter projects">'
                '<button type="button" class="ld-chip" aria-pressed="true" data-f="all">All</button>'
                '<button type="button" class="ld-chip" aria-pressed="false" data-f="new">New buildings</button>'
                '<button type="button" class="ld-chip" aria-pressed="false" data-f="ren">Renovations</button>'
                f'<label class="ld-area"><span class="sr">{E(area_word)}</span><select id="ldArea"><option value="">{E(area_all)}</option>{opts}</select></label></div>'
                f'<p class="ld-count" id="ldCount" aria-live="polite" data-all="{E(big_line)}">{E(big_line)}</p>'
                f'<div class="ld-list" id="ldList">{"".join(card(x) for x in d["projects"])}</div>'
                '<p class="ld-empty" id="ldEmpty" hidden>No projects in this sample match. The weekly list covers every open project.</p>'
                + (f'<div class="ld-after"><p>That is the top {n_big}. The full list has all {kept:,}, closest to a final clean first, with {area_filter}.</p>{buy()}</div>' if checkout else "")
                + '</section>')
    links = "".join(f'<li><a href="{rel}{E(l[0])}/">{E(l[1])}</a></li>' for l in p.get("links", []))
    method = ('<section class="block"><h2>How to use this list</h2>' + "".join(f"<p>{E(x)}</p>" for x in p["method"])
              + (f'<p>Price the work before you call:</p><ul>{links}</ul>' if links else "") + "</section>")
    shots = ""
    shots_ok = all(os.path.isfile(os.path.join(DOCS, "assets", "leads", f)) for f in ("members-list.png", "workbook.png"))
    if checkout and shots_ok:   # real screenshots of the paid product (files in docs/assets/leads/, made from the live members' page and workbook)
        shots = ('<section class="block ld-shots"><h2>What members get</h2>'
                 '<p>The same data as this page, every open project instead of a sample, on a members\' page and in an Excel file.</p>'
                 '<div class="ld-shotgrid">'
                 f'<figure class="ld-shot"><img src="{rel}assets/leads/members-list.png" width="1064" height="665" loading="eager" decoding="async" '
                 'alt="The members\' page: this week\'s list as cards with the reported cost, the builder, the address and the stage, with tabs for near finish, new this week and all projects">'
                 '<figcaption>The members\' page, every Monday</figcaption></figure>'
                 f'<figure class="ld-shot"><img src="{rel}assets/leads/workbook.png" width="1200" height="772" loading="eager" decoding="async" '
                 'alt="The Excel file: the near finish tab with address, reported cost and builder columns, and a filter arrow on every column">'
                 '<figcaption>The Excel file, filters on every column</figcaption></figure></div></section>')
    if p.get("kitForm"):
        form = (f'<form class="ld-form" action="https://app.kit.com/forms/{E(p["kitForm"])}/subscriptions" method="post">'
                '<label for="ldEmail">Email</label><div class="ld-frow"><input id="ldEmail" name="email_address" type="email" required autocomplete="email">'
                '<button class="btn" type="submit">Join the waitlist</button></div></form>')
    else:
        form = '<p><span class="btn soon" aria-disabled="true">Waitlist opens soon</span></p>'
    if checkout:   # the paid weekly list is on sale (Todd, Oct 17, 3:18 pm: "Link the leads checkout on the site.")
        form = form.replace("Join the waitlist", "Keep me posted")
        cta_html = ('<section class="block" id="ldCta"><div class="cta ld-cta ld-buy"><div>'
                    f'<h2>{E(p["cta"]["title"])}</h2><p>{E(p["cta"]["text"])}</p>'
                    f'<p class="ld-buybtn">{buy()}</p><p class="ld-secure">Secure checkout by Gumroad. Cancel any time.</p></div>'
                    f'<div class="ld-later"><p><b>Not ready yet?</b> Leave your email and we will let you know when the list adds new cities or features.</p>{form}'
                    '<small class="ld-note">Unsubscribe in one click. Your email is stored with Kit, our email provider, and never sold.</small></div></div></section>')
        sbar = (f'<div class="ld-sbar" id="ldBar" aria-hidden="true"><div class="wrap"><p><b>${price} a month</b><span> · <span class="ld-sbl">full list </span>every Monday</span></p>'
                f'<a class="btn" href="{E(checkout)}" rel="noopener" tabindex="-1">Get it</a></div></div>')
    else:
        cta_html = ('<section class="block" id="ldCta"><div class="cta ld-cta"><div>'
                    f'<h2>{E(p["cta"]["title"])}</h2><p>{E(p["cta"]["text"])}</p>'
                    f'<p class="ld-price">Planned price: ${price} a month. Joining the waitlist is free and commits you to nothing.</p></div>'
                    f'<div>{form}<small class="ld-note">We email you when the weekly list opens. Unsubscribe in one click. Your email is stored with Kit, our email provider, and never sold.</small></div></div></section>')
        sbar = ""
    body = (f'<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{lede}</p>{hero_act}</div>{tiles}'
            f'{near_html}{gc_html}{big_html}{method}{shots}{cta_html}{faq_block(p["faq"])}')
    script = r"""<script>(function(){var list=document.getElementById('ldList');if(list){
var cards=[].slice.call(list.querySelectorAll('.ld-proj')),chips=[].slice.call(document.querySelectorAll('.ld-chip')),
area=document.getElementById('ldArea'),count=document.getElementById('ldCount'),empty=document.getElementById('ldEmpty'),f='all';
function run(){var a=area.value,n=0;cards.forEach(function(c){var ok=(f==='all'||c.dataset.type===f)&&(!a||c.dataset.area===a);c.hidden=!ok;if(ok)n++});
count.textContent=(f==='all'&&!a)?count.dataset.all:'Showing '+n+' of '+cards.length+' projects in this free sample.';empty.hidden=n>0}
chips.forEach(function(b){b.addEventListener('click',function(){f=b.dataset.f;chips.forEach(function(x){x.setAttribute('aria-pressed',String(x===b))});run()})});
area.addEventListener('change',run);run()}
var bar=document.getElementById('ldBar'),hero=document.getElementById('ldHeroCta'),cta=document.getElementById('ldCta');
if(!bar||!hero||!cta||!('IntersectionObserver' in window))return;
var hv=true,cv=false,link=bar.querySelector('a');
function set(){var on=!hv&&!cv;bar.classList.toggle('on',on);bar.setAttribute('aria-hidden',String(!on));link.tabIndex=on?0:-1}
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.target===hero)hv=e.isIntersecting;else cv=e.isIntersecting});set()});
io.observe(hero);io.observe(cta)})();</script>"""
    ld = ('<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}) + "</script>")
    robots = "" if is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    foot = (f'</main>\n<footer><div class="wrap">'
            f'<p>Source: {E(src["name"])} ({E(src["url"])}), City data as of {E(asof)}, pulled {E(nice_date(src["fetchedAt"]))}. {E(src["modified"])} '
            'Reported cost is the figure filed with the City, not a contract value. No contractor named here has endorsed or works with ProofNotFluff. '
            'Public information for planning sales calls; not legal or business advice and no promise of work.</p>'
            f'<p>{E(p.get("disclaimer") or CITY_DISCLAIMER.get(p["city"], ""))}</p>'
            '<p>Made by ProofNotFluff with AI assistance from public City data. The waitlist form sends your email address to Kit. The page counts visits with Cloudflare Web Analytics, which sets no cookies, and loads its heading font from Google Fonts.</p>'
            f'</div></footer>\n{sbar}\n{script}\n</body></html>')
    bodycls = ' class="ld-page' + (' has-sbar' if sbar else '') + '"'
    return (HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=SHOP, ld=ld, bodycls=bodycls,
                        robots=robots, analytics=analytics_tag()) + body + foot)


def page_html(p):
    if p.get("kind") == "leads":
        return leads_page_html(p)
    url = BASE + p["slug"] + "/"
    rel = "../"
    form, results, script = PAGE_KINDS[p["kind"]](p)
    body = (f'<p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{E(p["lede"])}</p>'
            f'<div class="grid">{form}{results}</div>'
            f'<section class="block"><h2>How it works</h2>{"".join(f"<p>{E(x)}</p>" for x in p["method"])}</section>'
            f'<section class="block"><h2>A worked example</h2><p>{E(p["example"])}</p></section>'
            f'{extra_cards(p["slug"])}{cta(p)}{faq_block(p["faq"])}')
    robots = '<meta name="robots" content="noindex, nofollow">' if p.get("draft") else ""
    return (HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=SHOP, ld=ld_json(p, url), bodycls=' class="has-mbar"', robots=robots, analytics=analytics_tag()) + body +
            FOOT.format(rel=rel, script=script, sources=E(p["sources"])))


def index_html(pages):
    cards = "".join(f'<a class="card" href="{p["slug"]}/"><h3>{E(p["h1"])}</h3><p>{E(p["card"])}</p></a>' for p in pages)
    extras = "".join(f'<a class="card" href="{E(x["slug"])}/"><h3>{E(x["h1"])}</h3><p>{E(x["card"])}</p></a>' for x in live_extras())
    body = ('<p class="eyebrow">Free tools</p><h1>Pricing calculators that show their work</h1>'
            '<p class="lede">Free calculators for people who sell their time: find your real hourly rate and price a job so it pays you. '
            'Each one uses the same maths as our tested Excel and Google Sheets workbooks.</p>'
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
            cards += f'<a class="hubbtn" href="{E(it["free"])}"><b>Try the free calculator first</b><span>Same maths, in your browser</span></a>'
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
    lede = ('The Etsy workbooks are $2.99 each, the premium workbooks are on Gumroad, and the free calculators use the same maths.'
            if links.get("gumroad") else 'Every paid workbook is $2.99 on Etsy, and the free calculators use the same maths.')
    body = ('<section class="hub"><p class="eyebrow">ProofNotFluff</p><h1>Calculators that show their work</h1>'
            f'<p class="lede">Saw a video? It is right here. {E(lede)}</p>'
            f'{featured_html(links)}'
            f'{"<h2 class=hubh>Free calculators</h2><div class=hublist>" + calc + "</div>" if calc else ""}'
            f'{"<h2 class=hubh>Premium workbooks</h2><div class=hublist>" + prem + "</div>" if prem else ""}'
            f'<div class="hublist"><a class="hubbtn shop" href="{E(links.get("shop", SHOP))}" rel="noopener"><b>The whole shop on Etsy</b><span>Every tool, $2.99 each</span></a></div>'
            f'{groups}</section>')
    return (HEAD.format(title="ProofNotFluff: free calculators and $2.99 tools", desc="Free pricing and money calculators, and the Excel and Google Sheets workbooks behind them.",
                        url=url, rel="../", shop=SHOP, ld="", bodycls=' class="hubpage"', robots="", analytics=analytics_tag()) + body +
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



def main():
    spec = json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))
    pages = spec["pages"]
    for p in pages:
        if p.get("kind") == "leads" and not os.path.isfile(os.path.join(ROOT, p["data"])):
            print("skipped", p["slug"], "(no data yet)")
            continue
        out = os.path.join(DOCS, p["slug"]); os.makedirs(out, exist_ok=True)
        open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page_html(p))
        print("wrote", p["slug"])
    live = [p for p in pages if is_live(p)]
    open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8").write(index_html(live))
    write_hub_and_redirects(pages)
    urls = [BASE, BASE + "go/"] + [BASE + p["slug"] + "/" for p in live] + [BASE + x["slug"] + "/" for x in live_extras()]
    open(os.path.join(DOCS, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        "".join(f"  <url><loc>{u}</loc><lastmod>{spec['updated']}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    open(os.path.join(DOCS, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n")
    for p in pages:
        if chr(0x2014) in json.dumps(p, ensure_ascii=False):
            sys.exit(f"em dash in {p['slug']}")


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
