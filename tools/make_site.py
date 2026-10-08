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


# Shared by the etsy_fees and craft_fair kinds: their maths lives on the page (same formulas as the
# engines named in each model), and PNF.wire renders it. pnfAfter() runs after each render for the
# outputs wire has no format for: data-pct (percent) and data-never (a break-even that cannot happen).
AFTER_JS = """function pnfNum(v){var n=parseFloat(String(v).replace(/[$,%\\s]/g,""));return isFinite(n)?n:0;}
function pnfAfter(f,M){function go(){var v={};f.querySelectorAll("[data-in]").forEach(function(e){v[e.getAttribute("data-in")]=e.value;});var r=M(v);
document.querySelectorAll("[data-pct]").forEach(function(e){var x=r[e.getAttribute("data-pct")];e.textContent=(isFinite(x)?(x*100).toFixed(1):"0.0")+"%";e.classList.toggle("neg",x<0);});
document.querySelectorAll("[data-never]").forEach(function(e){if(r.never){e.textContent=e.getAttribute("data-never");e.classList.add("neg");}});}
f.querySelectorAll("select").forEach(function(s){s.addEventListener("change",function(){f.dispatchEvent(new Event("input"));});});
f.addEventListener("input",go);go();}"""


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
""" + AFTER_JS + """
(function(){var f=document.getElementById("calc"),CAP=""" + json.dumps(p["ads_cap"]) + """;
/* Same per-sale maths as the Listings tab of engines/etsy-true-profit (#5), with sales tax added to the processing base
   and each fee rounded to the cent so the lines add up to the total shown. */
function M(i){var price=pnfNum(i.price),ship=pnfNum(i.ship),tax=pnfNum(i.tax),cost=pnfNum(i.cost),label=pnfNum(i.label);
function c(x){return Math.round(x*100+1e-6)/100;}
var rate=pnfNum(i.adsRate)/100,rev=price+ship,tf=c(pnfNum(i.tfRate)/100*rev),pf=c(pnfNum(i.procRate)/100*(rev+tax)+pnfNum(i.procFixed)),lf=c(pnfNum(i.listFee));
var ads=c(Math.min(rate*rev,CAP)),fees=tf+pf+lf+ads,payout=rev-fees,profit=payout-cost-label,adsIf=c(Math.min(0.15*rev,CAP));
return {revenue:rev,tf:tf,pf:pf,lf:lf,ads:ads,fees:fees,payout:payout,cost:cost,label:label,profit:profit,loss:-profit,
margin:rev>0?profit/rev:0,feeShare:rev>0?fees/rev:0,adsOff:rate>0?0:1,adsIf:adsIf,profitIfAds:profit-adsIf};}
PNF.wire(f,M);pnfAfter(f,M);window.PNF_MODEL=M;})();</script>"""
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
""" + AFTER_JS + """
(function(){var f=document.getElementById("calc");
/* Same maths as the Break-Even tab of engines/craft-fair-profit (#12): card cost per $1 = card share x (percent + flat / average spend);
   pieces round up to whole pieces. */
function M(i){var booth=pnfNum(i.booth),other=pnfNum(i.other),price=pnfNum(i.price),cpp=pnfNum(i.cpp),target=pnfNum(i.target);
var avg=pnfNum(i.avgSale),perDollar=pnfNum(i.cardShare)/100*(pnfNum(i.cardPct)/100+(avg>0?pnfNum(i.cardFlat)/avg:0));
var total=booth+other,cardPer=price*perDollar,contrib=price-cpp-cardPer,ok=contrib>1e-9;
var be=ok?Math.max(0,Math.ceil(total/contrib-1e-9)):0,tg=ok?Math.max(0,Math.ceil((total+target)/contrib-1e-9)):0;
return {booth:booth,other:other,total:total,price:price,cpp:cpp,cardPer:cardPer,contrib:contrib,bePieces:be,beSales:be*price,
tgtPieces:tg,tgtSales:tg*price,tgtProfit:ok?tg*contrib-total:0,boothShare:total>0?booth/total:0,never:ok?0:1};}
PNF.wire(f,M);pnfAfter(f,M);window.PNF_MODEL=M;})();</script>"""
    return form, results, script


PAGE_KINDS = {"service": service_page, "hourly": hourly_page, "cashflow": cashflow_page,
              "etsy_fees": etsy_fees_page, "craft_fair": craft_fair_page}


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


if __name__ == "__main__":
    main()
