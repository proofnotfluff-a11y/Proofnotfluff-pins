#!/usr/bin/env python3
"""The free weekly sample page for Chicago Restaurant Inspection Leads (site/pages.json kind "restleads", written by
tools/make_site.py, which calls page_html here). Data: permits/inspections-chicago/rest-sample.json (tools/rest_leads.py
--sample), committed by the inspections workflow every Monday.

Public page rule (Oct 2026): the free page never names a business with a failed result. Failed, conditional and repeat
examples show the facility type, community area, date, the City's result and our categories only; the "opening soon"
examples show the business name and address, because a license inspection is a step toward opening. The paid list
(licensed to one business for its own prospecting) names every place.

Until Todd launches, the page spec carries "draft": true, so it is written with noindex and left off the index and the
sitemap; with no "checkout" key it shows the planned price and no buy button.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _res_cls(r):
    u = (r or "").upper()
    return {"FAIL": "fail", "PASS W/ CONDITIONS": "pwc", "PASS": "pass"}.get(u, "oth")


LOCK_S = ('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
          '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>')


def page_html(p):
    import make_site as M
    E = M.E
    d = json.load(open(os.path.join(ROOT, p["data"]), encoding="utf-8"))
    c = d["counts"]
    url = M.BASE + p["slug"] + "/"
    rel = "../"
    price = E(str(p["price"]))
    checkout = p.get("checkout")
    asof = E(d["asOfText"])
    w = d["window"]

    def card_anon(x):
        cats = ", ".join(x["categories"]) or "None in a category"
        kind = x["type"] if x["type"] not in ("", "Not given") else "Food business"
        return (f'<article class="ld-proj"><p class="ld-pill rp-{_res_cls(x["result"])}">City result: {E(x["result"])}</p>'
                f'<p class="rl-lock">{LOCK_S}Name and address on the members\' list</p>'
                f'<div class="ld-ptop"><span class="ld-cost" style="font-size:20px">{E(kind)} in {E(x["area"])}</span></div>'
                f'<dl class="ld-meta"><div><dt>Categories</dt><dd>{E(cats)}</dd></div>'
                f'<div><dt>Inspected</dt><dd>{E(M.nice_date(x["date"]))}, {E(x["inspectionType"])}</dd></div></dl></article>')

    def card_open(x):
        return (f'<article class="ld-proj"><p class="ld-pill rp-{_res_cls(x["result"])}">License inspection: {E(x["result"])}</p>'
                f'<div class="ld-ptop"><span class="ld-cost" style="font-size:20px">{E(x["name"])}</span><span class="ld-type">{E(x["type"])}</span></div>'
                f'<dl class="ld-meta"><div><dt>Where</dt><dd>{E(x["address"])}, {E(x["area"])}</dd></div>'
                f'<div><dt>Inspected</dt><dd>{E(M.nice_date(x["date"]))}, {E(x["inspectionType"])}</dd></div></dl></article>')

    notify = p.get("notify") or "mailto:hello@proofnotfluff.com?subject=Chicago%20Restaurant%20Inspection%20Leads%3A%20tell%20me%20when%20it%20opens"

    def buy(cls="btn ld-btnbig"):
        """The primary action: the checkout once the product is on sale, until then a note to the ProofNotFluff mailbox."""
        if checkout:
            return f'<a class="{cls}" href="{E(checkout)}" rel="noopener">Get the full list, ${price} a month</a>'
        return f'<a class="{cls}" href="{E(notify)}">Tell me when it opens</a>'

    lede = (f'{c["flagged"]:,} Chicago food businesses failed or passed with conditions in the last 30 days, and {c["opening"]:,} had '
            f'the license inspection Chicago does before it issues a food license. {E(p["lede"])}')
    hero_act = (f'<div class="ld-heroact rl-act" id="ldHeroCta">{buy()}<a class="ld-textlink" href="#sample">See this week\'s sample</a></div>'
                + ('<p class="ld-heronote">New list every Monday. Cancel any time.</p>' if checkout else
                   f'<p class="ld-heronote">${price} a month when it opens. New list every Monday.</p>'))
    bc = c["byCat"]
    tiles = (f'<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">Failed or conditional</div><div class="val">{c["flagged"]:,}</div><div class="sub">last 30 days</div></div>'
             f'<div class="tile"><div class="lab">Opening soon</div><div class="val">{c["opening"]:,}</div><div class="sub">license inspections</div></div>'
             f'<div class="tile"><div class="lab">Failed more than once</div><div class="val">{c["repeat"]:,}</div><div class="sub">2 or more fails in 90 days</div></div>'
             f'<div class="tile"><div class="lab">New this week</div><div class="val">{c["new"]:,}</div><div class="sub">inspected in the last 7 days</div></div></div>'
             f'<p class="asof">City records through {E(d["throughText"])}, pulled {asof}. Refreshed every Monday.</p>')
    trades = [("Pest control", bc["pests"], "with a pest violation"), ("Hood and exhaust cleaning", bc["hood"], "with a hood or exhaust violation"),
              ("Grease trap and drains", bc["drain"], "with a grease trap or drain violation"), ("Kitchen cleaning", bc["clean"], "with a cleaning violation"),
              ("POS, linen and new-account vendors", c["opening"], "with a license inspection")]
    trade_html = ('<section class="block"><h2>Leads by trade this week</h2><p>Places on the failed or conditional list, by the violation '
                  'category that fits your work, and places that had a license inspection.</p><ol class="rl-trades">'
                  + "".join(f'<li><span class="nm">{E(t)}<small>{E(s)}</small></span><span class="n">{n:,}</span></li>' for t, n, s in trades)
                  + '</ol></section>')
    ex = d["examples"]
    sample = (f'<section class="block" id="sample"><h2>Failed or conditional: a sample</h2>'
              '<p>The members\' list names each place, with its address, its 24-month City inspection history and the City\'s violation codes. '
              'This public sample shows the record without the name.</p>'
              f'<div class="ld-list rl3">{"".join(card_anon(x) for x in ex["flagged"])}</div></section>'
              f'<section class="block"><h2>Opening soon: a sample</h2><p>Chicago inspects a food business before it issues a food license, so many '
              'of these places are about to open or just opened. A new food business usually needs pest control, cleaning, linen and a point of '
              'sale, and many need hood and grease service. This public sample names only places that passed.</p>'
              f'<div class="ld-list rl3">{"".join(card_open(x) for x in ex["opening"])}</div></section>')
    method = ('<section class="block"><h2>How to use this list</h2>' + "".join(f"<p>{E(x)}</p>" for x in p["method"]) + "</section>")
    if checkout:
        cta_html = (f'<section class="block" id="ldCta"><div class="cta ld-cta ld-buy"><div><h2>{E(p["cta"]["title"])}</h2><p>{E(p["cta"]["text"])}</p>'
                    f'<p class="ld-buybtn">{buy()}</p><p class="ld-secure">Secure checkout by Gumroad. Cancel any time.</p></div></div></section>')
    else:
        cta_html = (f'<section class="block" id="ldCta"><div class="cta ld-cta"><div><h2>{E(p["cta"]["title"])}</h2><p>{E(p["cta"]["text"])}</p>'
                    f'<p class="ld-price">${price} a month when it opens.</p><p class="ld-buybtn">{buy()}</p></div></div></section>')
    body = (f'<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{lede}</p>{hero_act}</div>{tiles}'
            f'{trade_html}{sample}{method}{cta_html}{M.faq_block(p["faq"])}')
    ld = ('<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}) + "</script>"
          # small grey text darkened to pass WCAG AA on the warm canvas (axe, Oct 2026); scoped to this page only
          + "<style>.ld-page .asof,.ld-page footer p{color:#555B68}"
          ".ld-pill.rp-fail{background:#FBEAE4;color:#A63E21}.ld-pill.rp-pwc{background:#F6EDD5;color:#7A5A12}"
          ".ld-pill.rp-pass{background:#E3EFED;color:#2E6B66}.ld-pill.rp-oth{background:#E6EDF6;color:#2F5F9E}"
          ".rl-act{margin:18px 0 24px}.ld-page .ld-tiles .tile .lab{letter-spacing:.04em;overflow-wrap:anywhere}"
          "@media(max-width:600px){.ld-page .ld-tiles .tile .lab{font-size:10.5px;letter-spacing:.02em}}"
          ".rl3 .ld-pill{margin:0 0 10px}.rl3 .ld-ptop{margin:0 0 12px}"
          ".rl-lock{display:flex;align-items:center;gap:6px;margin:0 0 6px;font-size:13px;color:#555B68}.rl-lock svg{flex:none}"
          "@media(min-width:1000px){.ld-list.rl3{grid-template-columns:repeat(3,minmax(0,1fr))}}"
          ".rl-trades{list-style:none;margin:14px 0 0;padding:0;background:#fff;border:1px solid var(--line);border-radius:12px}"
          ".rl-trades li{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:12px 16px;border-top:1px solid #EFEBE4}"
          ".rl-trades li:first-child{border-top:0}.rl-trades .nm{font-weight:600;color:var(--ink)}"
          ".rl-trades .nm small{display:block;font-size:13.5px;font-weight:400;color:#555B68;margin-top:2px}"
          ".rl-trades .n{font:700 18px/1 Poppins,system-ui,sans-serif;color:var(--ink);font-variant-numeric:tabular-nums}</style>")
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    src = d["source"]
    foot = (f'</main>\n<footer><div class="wrap">'
            f'<p>Source: {E(src["name"])} ({E(src["url"])}), City records through {E(d["throughText"])}, pulled {asof}. Filtered by ProofNotFluff: '
            'inspections of the last 30 days at food businesses (schools, day care and other children\'s sites, hospitals, senior and nursing sites, '
            'mobile vendors and businesses named after a person left out) with a City result of Fail or Pass w/ Conditions and a violation in one of '
            'four categories, a license inspection, or two failed inspections in 90 days. Categories are ProofNotFluff\'s reading of the City\'s '
            'violation codes; inspector notes are not republished. A record repeats the City\'s result on that date; it does not say a place is '
            'clean, safe or open today. No business named here has endorsed or works with ProofNotFluff. Public information for planning sales calls; '
            'not legal or business advice and no promise of work.</p>'
            f'<p>{E(M.CITY_DISCLAIMER["Chicago"])}</p>'
            '<p>Made by ProofNotFluff with AI assistance from public City data. The page counts visits with Cloudflare Web Analytics, which sets no '
            'cookies, and loads its heading font from Google Fonts.</p></div></footer>\n</body></html>')
    return (M.HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=M.SHOP, ld=ld, bodycls=' class="ld-page"',
                          robots=robots, analytics=M.analytics_tag()) + body + foot)


def selftest():
    import re, sys, tempfile
    sys.path.insert(0, HERE)
    import rest_leads, rest_xlsx
    s = rest_leads.sample(rest_leads.build(rest_xlsx._planted()))
    tmp = tempfile.mkdtemp()
    f = os.path.join(tmp, "s.json")
    json.dump(s, open(f, "w"))
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json")))["pages"] if x.get("kind") == "restleads"][0]
    p = dict(spec, data=os.path.relpath(f, ROOT))
    html = page_html(p)
    assert 'content="noindex' in html or not spec.get("draft"), "draft page must be noindex"
    assert "Acme" not in html and "Fry House" not in html, "the free page names a place with a failed result"
    assert "New Place" in html, "openings are named"
    assert "Tell me when it opens" in html or "Get the full list, $" in html, "a primary action on the page"
    assert "one’s own risk" in html or "one's own risk" in html.replace("&#x27;", "'")
    assert "—" not in html
    for w in ("dirty", "filthy", "infested", "violator", "offender"):
        assert w not in re.sub(r"<[^>]+>", " ", html).lower(), w
    print("rest_site selftest ok")


if __name__ == "__main__":
    selftest()
