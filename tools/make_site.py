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
<link rel="canonical" href="{url}">{robots}<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
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
            f'<div><a class="btn" href="{E(c["url"])}">{E(c["button"])}</a><br>'
            f'<a class="btn ghost" href="{SHOP}">All ProofNotFluff tools</a></div></div></section>')


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


def page_html(p):
    url = BASE + p["slug"] + "/"
    rel = "../"
    form, results, script = (service_page if p["kind"] == "service" else hourly_page)(p)
    body = (f'<p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{E(p["lede"])}</p>'
            f'<div class="grid">{form}{results}</div>'
            f'<section class="block"><h2>How it works</h2>{"".join(f"<p>{E(x)}</p>" for x in p["method"])}</section>'
            f'<section class="block"><h2>A worked example</h2><p>{E(p["example"])}</p></section>'
            f'{cta(p)}{faq_block(p["faq"])}')
    robots = '<meta name="robots" content="noindex, nofollow">' if p.get("draft") else ""
    return (HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=SHOP, ld=ld_json(p, url), bodycls=' class="has-mbar"', robots=robots) + body +
            FOOT.format(rel=rel, script=script, sources=E(p["sources"])))


def index_html(pages):
    cards = "".join(f'<a class="card" href="{p["slug"]}/"><h3>{E(p["h1"])}</h3><p>{E(p["card"])}</p></a>' for p in pages)
    body = ('<p class="eyebrow">Free tools</p><h1>Pricing calculators that show their work</h1>'
            '<p class="lede">Free calculators for people who sell their time: find your real hourly rate and price a job so it pays you. '
            'Each one uses the same maths as our tested Excel and Google Sheets workbooks.</p>'
            f'<div class="tools">{cards}</div>')
    return (HEAD.format(title="Free pricing calculators for service businesses | ProofNotFluff",
                        desc="Free hourly rate and job pricing calculators for cleaners, pressure washing, freelancers and other service businesses.",
                        url=BASE, rel="", shop=SHOP, ld="", bodycls="", robots="") + body +
            FOOT.format(rel="", script="", sources="IRS Topic 554 (self-employment tax) and IRS standard mileage rates, checked Oct 6, 2026."))


def main():
    spec = json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))
    pages = spec["pages"]
    for p in pages:
        out = os.path.join(DOCS, p["slug"]); os.makedirs(out, exist_ok=True)
        open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page_html(p))
        print("wrote", p["slug"])
    live = [p for p in pages if not p.get("draft")]
    open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8").write(index_html(live))
    urls = [BASE] + [BASE + p["slug"] + "/" for p in live]
    open(os.path.join(DOCS, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        "".join(f"  <url><loc>{u}</loc><lastmod>{spec['updated']}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    open(os.path.join(DOCS, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n")
    for p in pages:
        if chr(0x2014) in json.dumps(p, ensure_ascii=False):
            sys.exit(f"em dash in {p['slug']}")


if __name__ == "__main__":
    main()
