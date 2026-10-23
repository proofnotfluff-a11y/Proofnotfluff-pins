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
    trial = int(p.get("trialDays") or 0) if checkout else 0      # Gumroad free trial (Todd, Oct 22, 9:29 pm)
    faq = list(p["faq"]) + ([["Can I try it before I pay?",
                              f"Yes. Start a {trial}-day free trial on Gumroad: your card goes in at checkout, nothing is charged for {trial} days, "
                              f"then it is ${p['price']} a month until you cancel. Cancel before day {trial} and you pay nothing."]] if trial else [])
    asof = E(d["asOfText"])
    w = d["window"]

    keyof = {c["label"]: c["key"] for c in d.get("categories", [])}

    def card_anon(x):
        cats = ", ".join(x["categories"]) or "None in a category"
        kind = x["type"] if x["type"] not in ("", "Not given") else "Food business"
        keys = " ".join(keyof.get(k, "") for k in x["categories"]).strip()
        return (f'<article class="ld-proj" data-cats="{E(keys)}"><p class="ld-pill rp-{_res_cls(x["result"])}">City result: {E(x["result"])}</p>'
                f'<div class="ld-ptop"><span class="ld-cost" style="font-size:20px">{E(("An " if kind[:1].lower() in "aeiou" else "A ") + kind.lower())} in {E(x["area"])}</span></div>'
                f'<p class="rl-lock">{LOCK_S}Name and address hidden: on the members\' list</p>'
                f'<dl class="ld-meta"><div><dt>Categories</dt><dd>{E(cats)}</dd></div>'
                f'<div><dt>Inspected</dt><dd>{E(M.nice_date(x["date"]))}, {E(x["inspectionType"])}</dd></div></dl></article>')

    def card_open(x):
        return (f'<article class="ld-proj" data-cats="open"><p class="ld-pill rp-{_res_cls(x["result"])}">License inspection: {E(x["result"])}</p>'
                f'<div class="ld-ptop"><span class="ld-cost" style="font-size:20px">{E(x["name"])}</span><span class="ld-type">{E(x["type"])}</span></div>'
                f'<dl class="ld-meta"><div><dt>Where</dt><dd>{E(x["address"])}, {E(x["area"])}</dd></div>'
                f'<div><dt>Inspected</dt><dd>{E(M.nice_date(x["date"]))}, {E(x["inspectionType"])}</dd></div></dl></article>')

    notify = p.get("notify") or "mailto:hello@proofnotfluff.com?subject=Chicago%20Restaurant%20Inspection%20Leads%3A%20tell%20me%20when%20it%20opens"

    def buy(cls="btn ld-btnbig"):
        """The primary action: the checkout once the product is on sale, until then a note to the ProofNotFluff mailbox."""
        if checkout:
            return f'<a class="{cls}" href="{E(checkout)}" rel="noopener">' + (f"Start your {trial}-day free trial" if trial else f"Get the full list, ${price} a month") + '</a>'
        return f'<a class="{cls}" href="{E(notify)}">Tell me when it opens</a>'

    lede = (f'{c["flagged"]:,} Chicago food businesses failed or passed with conditions with a pest, hood, grease trap or cleaning violation in the last 30 days, and {c["opening"]:,} had '
            f'the license inspection Chicago does before it issues a food license. {E(p["lede"])}')
    sub_link = (f'<a class="ld-textlink" href="{E(checkout)}" rel="noopener">Try {trial} days free, then ${price} a month</a>' if trial else
                f'<a class="ld-textlink" href="{E(checkout)}" rel="noopener">Subscribe, ${price} a month</a>' if checkout else
                f'<a class="ld-textlink" href="{E(notify)}">Tell me when it opens</a>')
    hero_act = (f'<div class="ld-heroact rl-act" id="ldHeroCta"><a class="btn ld-btnbig" href="#sample">See this week\'s free sample</a>{sub_link}</div>'
                + (f'<p class="ld-heronote">New list every Monday. Card at checkout, nothing charged for {trial} days. Cancel any time.</p>' if trial else
                   '<p class="ld-heronote">New list every Monday. Cancel any time.</p>' if checkout else
                   f'<p class="ld-heronote">${price} a month when it opens. New list every Monday.</p>'))
    bc = c["byCat"]
    tiles = (f'<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">Failed or conditional</div><div class="val">{c["flagged"]:,}</div><div class="sub">last 30 days</div></div>'
             f'<div class="tile"><div class="lab">Opening soon</div><div class="val">{c["opening"]:,}</div><div class="sub">license inspections</div></div>'
             f'<div class="tile"><div class="lab">Failed more than once</div><div class="val">{c["repeat"]:,}</div><div class="sub">2 or more fails in 90 days</div></div>'
             f'<div class="tile"><div class="lab">New this week</div><div class="val">{c["new"]:,}</div><div class="sub">inspected in the last 7 days</div></div></div>'
             f'<p class="asof">City records through {E(d["throughText"])}, pulled {asof}. Refreshed every Monday.</p>')
    tabs = [("all", "All", c.get("places", c["flagged"] + c["opening"]), "on this week's lists: failed or conditional in our four categories, or a license inspection."),
            ("hood", "Hood and exhaust", bc["hood"], "failed or passed with conditions with a hood or exhaust violation."),
            ("pests", "Pests", bc["pests"], "failed or passed with conditions with a pest violation."),
            ("drain", "Grease trap", bc["drain"], "failed or passed with conditions with a grease trap or drain violation."),
            ("clean", "Kitchen cleaning", bc["clean"], "failed or passed with conditions with a cleaning violation."),
            ("open", "Opening soon", c["opening"], "had the license inspection the City does before it issues a food license. This sample names only places that passed.")]
    tab_btns = "".join(f'<button type="button" aria-pressed="{"true" if k == "all" else "false"}" data-t="{k}" data-n="{n:,}" data-b="{E(b)}">'
                       f'{E(lab)}<span class="c">{n:,}</span></button>' for k, lab, n, b in tabs)
    ex = d["examples"]
    seen, anon = set(), []
    for x in ex.get("flagged", []) + ex.get("repeat", []):   # repeat fails are failed records too; each record shows once
        k = (x.get("area"), x.get("date"), x.get("inspectionType"), tuple(x.get("categories", [])))
        if k not in seen:
            seen.add(k); anon.append(x)
    cards = "".join(card_anon(x) for x in anon) + "".join(card_open(x) for x in ex["opening"])
    sample = (f'<section class="block" id="sample"><h2>This week\'s free sample</h2>'
              '<p>Real records from this week\'s pull. Failed and conditional places show the record without the name; the members\' list names '
              'each place, with its address, its 24-month City inspection history and the City\'s violation codes. Places that passed a license '
              'inspection are named here, because a license inspection is a step toward opening.</p>'
              f'<div class="rl-tabs" role="group" aria-label="Show records for" id="rlTabs" hidden>{tab_btns}</div>'
              f'<p class="rl-tabnote" id="rlNote" aria-live="polite"><b>{tabs[0][2]:,} places</b> {E(tabs[0][3])} This free sample shows {len(anon) + len(ex["opening"])}.</p>'
              f'<div class="ld-list rl3" id="rlList">{cards}</div>'
              '<p class="rl-empty" id="rlEmpty" hidden>No place in this week\'s free sample has this category. Members see every one.</p>'
              f'<p class="rl-more" id="rlMore">Members see every place on all three lists, named, with address, the City\'s violation codes and 24 months of history. '
              + (f'<a href="{E(checkout)}" rel="noopener">Try {trial} days free, then ${price} a month</a>.' if trial else
                 f'<a href="{E(checkout)}" rel="noopener">Subscribe, ${price} a month</a>.' if checkout else "") + '</p></section>')
    links = "".join(f'<li><a href="{rel}{E(l[0])}/">{E(l[1])}</a></li>' for l in p.get("links", []))
    method = ('<section class="block"><h2>How to use this list</h2>' + "".join(f"<p>{E(x)}</p>" for x in p["method"])
              + (f'<p>Price the visit before you call:</p><ul>{links}</ul>' if links else "") + "</section>")
    later = ""
    if p.get("kitForm"):
        later = (f'<div class="ld-later"><p><b>Not ready yet?</b> Leave your email and we will let you know when the list adds new areas or features.</p>'
                 f'<form class="ld-form" action="https://app.kit.com/forms/{E(p["kitForm"])}/subscriptions" method="post"><label for="ldEmail">Email</label>'
                 '<div class="ld-frow"><input id="ldEmail" name="email_address" type="email" required autocomplete="email"><button class="btn" type="submit">Keep me posted</button></div></form>'
                 '<small class="ld-note">Unsubscribe in one click. Your email is stored with Kit, our email provider, and never sold.</small></div>')
    if checkout:
        cta_html = (f'<section class="block" id="ldCta"><div class="cta ld-cta ld-buy"><div><h2>{E(p["cta"]["title"])}</h2><p>{E(p["cta"]["text"])}</p>'
                    f'<p class="ld-buybtn">{buy()}</p>'
                    + (f'<p class="ld-secure">Secure checkout by Gumroad. Your card goes in at checkout and nothing is charged for {trial} days. '
                       f'Then it is ${price} a month until you cancel. Cancel in your Gumroad library before day {trial} and you pay nothing. '
                       f'<a href="{rel}refunds/">Refunds and cancelling</a></p>' if trial else
                       f'<p class="ld-secure">Secure checkout by Gumroad. Cancel any time. <a href="{rel}refunds/">Refunds and cancelling</a></p>')
                    + f'</div>{later}</div></section>')
    else:
        cta_html = (f'<section class="block" id="ldCta"><div class="cta ld-cta"><div><h2>{E(p["cta"]["title"])}</h2><p>{E(p["cta"]["text"])}</p>'
                    f'<p class="ld-price">${price} a month when it opens.</p><p class="ld-buybtn">{buy()}</p></div></div></section>')
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), ("Shop", "shop/"), (p["h1"], None)])
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{lede}</p>{hero_act}</div>{tiles}'
            f'{sample}{method}{cta_html}{M.guides_block(p["slug"], rel=rel)}{M.faq_block(faq)}')
    sbar = ((f'<div class="ld-sbar" id="ldBar" aria-hidden="true"><div class="wrap"><p><b>{trial} days free</b><span> · then ${price} a month</span></p>'
             f'<a class="btn" href="{E(checkout)}" rel="noopener" tabindex="-1">Try free</a></div></div>') if trial else
            (f'<div class="ld-sbar" id="ldBar" aria-hidden="true"><div class="wrap"><p><b>${price} a month</b><span> · <span class="ld-sbl">full list </span>every Monday</span></p>'
             f'<a class="btn" href="{E(checkout)}" rel="noopener" tabindex="-1">Subscribe</a></div></div>') if checkout else "")
    script = r"""<script>(function(){var tb=document.getElementById('rlTabs');if(tb){tb.hidden=false;
var bs=[].slice.call(tb.querySelectorAll('button')),cs=[].slice.call(document.querySelectorAll('#rlList .ld-proj')),
note=document.getElementById('rlNote'),empty=document.getElementById('rlEmpty');
function pick(t){var n=0;bs.forEach(function(b){var on=b.dataset.t===t;b.setAttribute('aria-pressed',String(on));});
cs.forEach(function(c){var ok=t==='all'||(' '+c.dataset.cats+' ').indexOf(' '+t+' ')>=0;c.hidden=!ok;if(ok)n++});empty.hidden=n>0;
bs.forEach(function(b){if(b.dataset.t===t)note.innerHTML='<b>'+b.dataset.n+' places</b> '+b.dataset.b+(n?' This free sample shows '+n+'.':'')})}
bs.forEach(function(b){b.addEventListener('click',function(){pick(b.dataset.t)})});
var q=(location.search.match(/[?&]trade=([a-z]+)/)||[])[1];if(q&&bs.some(function(b){return b.dataset.t===q}))pick(q)}
var bar=document.getElementById('ldBar'),hero=document.getElementById('ldHeroCta'),cta=document.getElementById('ldCta');
if(!bar||!hero||!cta||!('IntersectionObserver' in window))return;
var hv=true,cv=false,link=bar.querySelector('a');
function set(){var on=!hv&&!cv;bar.classList.toggle('on',on);bar.setAttribute('aria-hidden',String(!on));link.tabIndex=on?0:-1}
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.target===hero)hv=e.isIntersecting;else cv=e.isIntersecting});set()});
io.observe(hero);io.observe(cta)})();</script>"""
    prod = next((x for x in M.store_products() if x["key"] == p["slug"]), None)
    ld = (M.ld_tags({"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
          crumb_ld, M.product_ld(prod, url) if prod else None)
          # small grey text darkened to pass WCAG AA on the warm canvas (axe, Oct 2026); scoped to this page only
          + "<style>.ld-page .asof,.ld-page footer p{color:var(--muted)}"
          ".ld-pill.rp-fail{background:var(--rp-fail-bg);color:var(--rp-fail)}.ld-pill.rp-pwc{background:var(--rp-pwc-bg);color:var(--rp-pwc)}"
          ".ld-pill.rp-pass{background:var(--chip-near-bg);color:var(--chip-near)}.ld-pill.rp-oth{background:var(--chip-insp-bg);color:var(--chip-insp)}"
          ".rl-act{margin:18px 0 24px}.ld-page .ld-tiles .tile .lab{letter-spacing:.04em;overflow-wrap:anywhere}"
          "@media(max-width:600px){.ld-page .ld-tiles .tile .lab{font-size:11.5px;letter-spacing:.02em;white-space:normal}}"
          ".rl3 .ld-pill{margin:0 0 10px}.rl3 .ld-ptop{margin:0 0 12px}"
          ".rl-lock{display:flex;align-items:center;gap:6px;margin:0 0 6px;font-size:13px;color:var(--muted)}.rl-lock svg{flex:none}"
          "@media(min-width:1000px){.ld-list.rl3{grid-template-columns:repeat(3,minmax(0,1fr))}}"
          ".rl-trades{list-style:none;margin:14px 0 0;padding:0;background:var(--card);border:1px solid var(--line);border-radius:12px}"
          ".rl-trades li{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:12px 16px;border-top:1px solid var(--rule)}"
          ".rl-trades li:first-child{border-top:0}.rl-trades .nm{font-weight:600;color:var(--ink)}"
          ".rl-trades .nm small{display:block;font-size:13.5px;font-weight:400;color:var(--muted);margin-top:2px}"
          ".rl-trades .n{font:700 18px/1 Poppins,system-ui,sans-serif;color:var(--ink);font-variant-numeric:tabular-nums}"
          # design director round 2: the trade card is the FAQ's measure (C1), the price line clears the button (C2),
          # and no heading or question leaves one word alone on a phone (C3)
          ".rl-trades{max-width:760px}section.block .rl-trades li{max-width:none}"
          ".ld-page .ld-cta p.ld-buybtn{margin-top:16px}"
          ".ld-page h2,.ld-page summary{text-wrap:balance}</style>")
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    src = d["source"]
    foot = (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            f'<p>Source: {E(src["name"])} ({E(src["url"])}), City records through {E(d["throughText"])}, pulled {asof}. Filtered by ProofNotFluff: '
            'inspections of the last 30 days at food businesses, less the places under "Who is left out?" above, with a City result of Fail or '
            'Pass w/ Conditions and a violation in one of '
            'four categories, a license inspection, or two failed inspections in 90 days. Categories are ProofNotFluff\'s reading of the City\'s '
            'violation codes; inspector notes are not republished. A record repeats the City\'s result on that date; it does not say a place is '
            'clean, safe or open today. No business named here has endorsed or works with ProofNotFluff. Public information for planning sales calls; '
            'not legal or business advice and no promise of work.</p>'
            f'<p>{E(M.CITY_DISCLAIMER["Chicago"])}</p>'
            '<p>Made by ProofNotFluff with AI assistance from public City data. The page counts visits with Cloudflare Web Analytics, which sets no '
            f'cookies.</p></div></footer>\n{sbar}\n{script}\n</body></html>')
    return (M.HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=M.SHOP, ld=ld, bodycls=' class="ld-page' + (' has-sbar' if sbar else '') + '"',
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
    assert "Tell me when it opens" in html or "Get the full list, $" in html or "-day free trial</a>" in html, "a primary action on the page"
    if spec.get("checkout") and spec.get("trialDays"):   # a trial is never offered without its terms next to it (Legal, trial review item 9)
        assert html.count("nothing is charged for") >= 2 and "Can I try it before I pay?" in html, "trial terms on the page"
    assert "one’s own risk" in html or "one's own risk" in html.replace("&#x27;", "'")
    assert "—" not in html
    faq = dict((q, a) for q, a in spec["faq"])
    assert faq.get("Who is left out?") == rest_leads.LEFT_OUT, "the free page states the shared left-out sentence (holdout round 2)"
    assert "named after a person" not in html and "full name" not in html, "one wording for the person-name rule"
    for w in ("dirty", "filthy", "infested", "violator", "offender"):
        assert w not in re.sub(r"<[^>]+>", " ", html).lower(), w
    print("rest_site selftest ok")


if __name__ == "__main__":
    selftest()
