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
"""
import html, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
BASE = "https://proofnotfluff-a11y.github.io/Proofnotfluff-pins/"
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
    form = f"""<form class="card" id="calc" novalidate>
<fieldset><legend>What you want to take home</legend>
{field("takeHome", "Take-home pay you want per year", d["takeHome"], "After tax", pre="$")}
{field("taxRate", "Tax set-aside rate", d["taxRate"], "Share of profit you set aside for tax", suf="%")}
{field("expenses", "Business expenses per year", d["expenses"], "Software, insurance, equipment, fees", pre="$")}
</fieldset>
<fieldset><legend>Your working time</legend>
{field("weeks", "Weeks you work per year", d["weeks"])}
{field("hours", "Hours you work per week", d["hours"])}
{field("billableShare", "Share of hours a client pays for", d["billableShare"], "Not sure? Try 50 to 70", suf="%")}
</fieldset>
<fieldset><legend>Check a rate you are considering</legend>
{field("checkRate", "Hourly rate to check", d["checkRate"], pre="$")}
</fieldset></form>"""
    results = """<div class="sticky"><div class="card" aria-live="polite">
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
<div class="callout" data-show-if="shortBy < 0.01">That rate meets your take-home goal.</div>
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


PAGE_KINDS = {"service": service_page, "hourly": hourly_page, "cashflow": cashflow_page,
              "etsy_fees": etsy_fees_page, "craft_fair": craft_fair_page, "str_nightly": str_nightly_page,
              "debt_payoff": debt_payoff_page, "shipping_cost": shipping_cost_page,
              "reorder_point": reorder_point_page, "str_breakeven": str_breakeven_page,
              "rental_cash_flow": rental_cash_flow_page,
              "business_expense": business_expense_page}


def page_html(p):
    url = BASE + p["slug"] + "/"
    rel = "../"
    form, results, script = PAGE_KINDS[p["kind"]](p)
    body = (f'<p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{E(p["lede"])}</p>'
            f'<div class="grid">{form}{results}</div>'
            f'<section class="block"><h2>How it works</h2>{"".join(f"<p>{E(x)}</p>" for x in p["method"])}</section>'
            f'<section class="block"><h2>A worked example</h2><p>{E(p["example"])}</p></section>'
            f'{cta(p)}{faq_block(p["faq"])}')
    robots = '<meta name="robots" content="noindex, nofollow">' if p.get("draft") else ""
    return (HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=SHOP, ld=ld_json(p, url), bodycls=' class="has-mbar"', robots=robots, analytics=analytics_tag()) + body +
            FOOT.format(rel=rel, script=script, sources=E(p["sources"])))


def index_html(pages):
    cards = "".join(f'<a class="card" href="{p["slug"]}/"><h3>{E(p["h1"])}</h3><p>{E(p["card"])}</p></a>' for p in pages)
    body = ('<p class="eyebrow">Free tools</p><h1>Pricing calculators that show their work</h1>'
            '<p class="lede">Free calculators for people who sell their time: find your real hourly rate and price a job so it pays you. '
            'Each one uses the same maths as our tested Excel and Google Sheets workbooks.</p>'
            f'<div class="tools">{cards}</div>')
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


def hub_html(links, pages):
    """docs/go/: the one link every bio points to. Free value first, then the shop, then every product by audience."""
    url = BASE + "go/"
    live = [p for p in pages if not p.get("draft")]
    by = {p["id"]: p for p in links["products"]}
    calc = "".join(f'<a class="hubbtn" href="../{p["slug"]}/"><b>{E(p["h1"])}</b><span>{E(p["card"])}</span></a>' for p in live)
    prem = "".join(f'<a class="hubbtn prem" href="{E(product_url(p))}" rel="noopener"><b>{E(p["name"])}</b><span>{E(p.get("tagline", "Premium workbook"))} · ${p.get("price", "")}</span></a>'
                   for p in links.get("gumroad", []))
    groups = ""
    for g in links["groups"]:
        rows = "".join(f'<a class="hubbtn" href="{E(product_url(by[i]))}" rel="noopener"><b>{E(by[i]["name"])}</b><span>$2.99 on Etsy</span></a>' for i in g["ids"] if i in by)
        if rows:
            groups += f'<h2 class="hubh">{E(g["title"])}</h2><div class="hublist">{rows}</div>'
    body = ('<section class="hub"><p class="eyebrow">ProofNotFluff</p><h1>Calculators that show their work</h1>'
            '<p class="lede">Free tools first. Every paid workbook is $2.99 on Etsy and uses the same maths.</p>'
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
        if not p.get("draft"):
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
        out = os.path.join(DOCS, p["slug"]); os.makedirs(out, exist_ok=True)
        open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page_html(p))
        print("wrote", p["slug"])
    live = [p for p in pages if not p.get("draft")]
    open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8").write(index_html(live))
    write_hub_and_redirects(pages)
    urls = [BASE, BASE + "go/"] + [BASE + p["slug"] + "/" for p in live]
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
