#!/usr/bin/env python3
"""The free weekly sample page for Chicago New Business Licenses (site/pages.json kind "licleads", written by
tools/make_site.py, which calls page_html here). Data: permits/licenses-chicago/sample.json (tools/licenses_chicago.py),
committed by .github/workflows/licenses-chicago.yml every Monday.

Every business on the sample was just licensed by the City at a business site; names that could be a person's,
person-held and event licenses and home addresses are already left out by the data layer. Until Todd launches, the
spec carries "draft": true (noindex, off the index and the sitemap) and no "checkout" key, so the page shows a
"Tell me when it opens" note to the ProofNotFluff mailbox and no buy button. With no "price" the page names no price.

Usage: python3 tools/lic_site.py      selftest on the committed sample and planted rows
"""
import datetime as dt, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ORDER = ["food", "retail", "beauty", "venue", "auto", "care"]
FOOD_URL = "https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5"   # the same dataset lic_xlsx names


def page_html(p):
    import make_site as M
    E = M.E
    d = json.load(open(os.path.join(ROOT, p["data"]), encoding="utf-8"))
    from licenses_chicago import TRADES      # the trade names the members' app and workbook use (one source)
    c, w = d["counts"], d["window"]
    names = {k: s for k, _, s, _ in TRADES}
    kinds = {k: x for k, _, _, x in TRADES}
    url = M.BASE + p["slug"] + "/"
    rel = "../"
    checkout, price = p.get("checkout"), p.get("price")
    pulled = M.nice_date(d["source"]["fetchedAt"])                     # the Chicago date of the pull
    notify = p.get("notify") or "mailto:hello@proofnotfluff.com?subject=Chicago%20New%20Business%20Licenses%3A%20tell%20me%20when%20it%20opens"

    def buy(cls="btn ld-btnbig"):
        if checkout:
            return f'<a class="{cls}" href="{E(checkout)}" rel="noopener">Get the full list: ${E(str(price))} a month</a>'
        return f'<a class="{cls}" href="{E(notify)}">Tell me when it opens</a>'

    HIST = {"first": "First license", "site": "New site", "added": "Added license", "relicensed": "Relicensed"}

    def card(x):
        from licenses_chicago import street_unit
        st, un = street_unit(x["address"])
        acts = [a for a in (x.get("activity") or "").split(" | ") if a]
        act = E(acts[0]) + (f' <span class="lc-more">and {len(acts) - 1} more</span>' if len(acts) > 1 else "") if acts else ""
        h = x.get("history") or ""
        return (f'<article class="ld-proj"><p class="lc-pills"><span class="ld-pill lc-pill">Licensed {E(M.nice_date(x["issued"]))}</span>'
                + (f'<span class="lc-hi {h}"><i></i>{HIST[h]}</span>' if h in HIST else "") + '</p>'
                f'<div class="ld-ptop"><span class="ld-cost" style="font-size:20px">{E(x["business"])}</span></div>'
                f'<dl class="ld-meta"><div><dt>Where</dt><dd>{E(st)}{" <span class=lc-more>&middot; " + E(un) + "</span>" if un else ""}{", " + E(x["communityArea"]) if x.get("communityArea") else ""}</dd></div>'
                f'<div><dt>License</dt><dd>{E(x["licenseType"])}</dd></div>'
                f'<div><dt>Activity</dt><dd>{act}</dd></div></dl></article>')

    s30, sw = c["segments30"], c["segmentsWeek"]
    note = (f'<p class="ld-heronote">New list every Monday. Cancel any time.</p>' if checkout else
            (f'<p class="ld-heronote">${E(str(price))} a month when it opens. New list every Monday.</p>' if price else
             '<p class="ld-heronote">Not on sale yet. New list every Monday.</p>'))
    lede = (f'{c["keptWeek"]:,} business sites on this week\'s list got a new City business license in the week to {E(M.nice_date(w["to"]))}, '
            f'and {c["kept30"]:,} in the last 30 days. {E(p["lede"])}')
    top_area = c["areasWeek"][0] if c.get("areasWeek") else None
    ties = sum(1 for a in (c.get("areasWeek") or [])[1:] if top_area and a[1] == top_area[1])   # a tie is said, never hidden (holdout 1, round 2)
    tiles = (f'<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">New in 30 days</div><div class="val">{c["kept30"]:,}</div><div class="sub">licensed business sites</div></div>'
             f'<div class="tile"><div class="lab">New this week</div><div class="val">{c["keptWeek"]:,}</div><div class="sub">licensed in the last 7 days</div></div>'
             f'<div class="tile"><div class="lab">Food businesses</div><div class="val">{s30.get("food", 0):,}</div><div class="sub">restaurants, bars, food shops</div></div>'
             + (f'<div class="tile"><div class="lab">Busiest area this week</div><div class="val lc-area">{E(top_area[0])}</div><div class="sub">{top_area[1]:,} new licenses'
                + (f', tied with {ties} more {"area" if ties == 1 else "areas"}' if ties else "") + '</div></div>' if top_area else "")
             + f'</div><p class="asof">City records pulled {E(dt.datetime.strptime(pulled, "%b %d, %Y").strftime("%A"))}, {E(pulled)}. The list is refreshed every Monday.</p>')
    trades = ('<section class="block"><h2>New licenses by trade, last 30 days</h2><p>Each business on the list, sorted by what it does, '
              'so you can work the trades that buy from you.</p><ol class="rl-trades">'
              + "".join(f'<li><span class="nm">{E(names[k])}<small>{E(kinds[k])}. {sw.get(k, 0):,} new this week</small></span><span class="n">{s30.get(k, 0):,}</span></li>'
                        for k in ORDER if k in names)
              + '</ol></section>')
    segs = "".join(f'<h3 class="lc-h3">{E(names[k])} <span>({sw.get(k, 0):,} this week)</span></h3><div class="ld-list rl3">{"".join(card(x) for x in d["segments"][k][:3])}</div>'
                   for k in ORDER if d["segments"].get(k))
    sample = (f'<section class="block" id="sample"><h2>This week\'s sample</h2><p>Up to three per trade shown here, from a free sample of up to ten per trade licensed in the last 7 days. '
              f'The members\' list has all {c["kept30"]:,} from the last 30 days, with a map, filters by trade, area and date, and an Excel file.</p>'
              f'{segs}</section>')
    method = '<section class="block"><h2>How to use this list</h2>' + "".join(f"<p>{E(x)}</p>" for x in p["method"]) + "</section>"
    cta_html = (f'<section class="block" id="ldCta"><div class="cta ld-cta"><div><h2>{E(p["cta"]["title"])}</h2><p>{E(p["cta"]["text"])}</p>'
                + (f'<p class="ld-price">${E(str(price))} a month when it opens.</p>' if price and not checkout else "")
                + f'<p class="ld-buybtn">{buy()}</p></div></div></section>')
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), ("Shop", "shop/"), (p["h1"], None)])
    shot = ('<figure class="lc-shot"><div class="lc-sh"><b>What members see</b><span>one row per business and site</span></div>'
            '<div class="lc-r"><div><b>Cafe, Logan Square</b><span>Retail Food Establishment</span></div><span class="lc-hi first"><i></i>First license</span></div>'
            '<div class="lc-r"><div><b>Tavern, Lake View</b><span>Tavern</span></div><span class="lc-hi site"><i></i>New site</span></div>'
            '<figcaption>Illustration. The list shows each business\'s name, address, license and what the City\'s record says about it.</figcaption></figure>')
    body = (f'{crumb}<div class="lc-herogrid"><div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{lede}</p>'
            f'<div class="ld-heroact rl-act">{buy()}<a class="ld-textlink" href="#sample">See this week\'s sample</a></div>{note}</div>{shot}</div>'
            f'{tiles}{trades}{sample}{method}{cta_html}{M.guides_block(p["slug"], rel=rel)}{M.faq_block(p["faq"])}')
    ld = (M.ld_tags({"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}, crumb_ld)
          + "<style>.ld-page .asof,.ld-page footer p{color:var(--muted)}.rl-act{margin:18px 0 8px}"
          ".lc-pill{background:var(--chip-near-bg);color:var(--chip-near)}.rl3 .ld-pill{margin:0}.rl3 .ld-ptop{margin:0 0 12px}"
          ".ld-page .tile .val.lc-area{font-size:22px;line-height:1.25}"
          ".lc-more{color:var(--muted)}.lc-pills{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0 0 10px}.lc-pills .ld-pill{margin:0}"
          ".lc-hi.added,.lc-hi.relicensed{color:#3A4152;background:#ECE6DA}"
          ".crumbs+.lc-herogrid .eyebrow{margin-top:14px}"
          "@media(min-width:1000px){.lc-herogrid{display:grid;grid-template-columns:minmax(0,1fr) 380px;gap:40px;align-items:center}.lc-herogrid .ld-hero .lede{max-width:none}}"
          ".lc-shot{margin:0 0 26px;background:var(--card);border:1px solid var(--line);border-radius:14px;box-shadow:0 8px 28px rgba(29,36,51,.08);overflow:hidden;max-width:460px}"
          ".lc-sh{display:flex;justify-content:space-between;align-items:baseline;gap:12px;padding:14px 18px;border-bottom:1px solid var(--rule)}"
          "@media(max-width:600px){.lc-sh{flex-direction:column;gap:2px}}"
          ".lc-sh b{font:600 15px Poppins,system-ui,sans-serif;color:var(--ink)}.lc-sh span{font-size:12.5px;color:var(--muted)}"
          ".lc-r{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:14px 18px;border-bottom:1px solid var(--rule)}"
          ".lc-r b{display:block;font:600 16px Poppins,system-ui,sans-serif;color:var(--ink)}.lc-r span{font-size:13.5px;color:var(--ink2)}"
          ".lc-hi{display:inline-flex;align-items:center;gap:7px;height:28px;padding:0 11px;border-radius:999px;font-weight:700;font-size:13px;white-space:nowrap}"
          ".lc-hi i{width:8px;height:8px;background:currentColor;border-radius:50%}.lc-hi.first{color:#A63E21;background:#FBEAE4}.lc-hi.first i{border-radius:2px}"
          ".lc-hi.site{color:#2F5F9E;background:#E6EDF6}"
          ".lc-shot figcaption{padding:10px 18px 12px;font-size:12.5px;color:var(--muted);background:var(--paper,#F7F5F0)}"
          ".lc-h3{font:600 18px/1.3 Poppins,system-ui,sans-serif;margin:26px 0 10px;color:var(--ink)}"
          ".lc-h3 span{font:400 15px/1.3 system-ui,sans-serif;color:var(--muted)}"
          ".ld-page .ld-tiles .tile .lab{letter-spacing:.04em;overflow-wrap:anywhere}.ld-page .ld-tiles .tile .sub{text-wrap:balance}"
          "@media(max-width:600px){.ld-page .ld-tiles .tile .lab{font-size:11.5px;letter-spacing:.02em;white-space:normal}}"
          "@media(min-width:1000px){.ld-list.rl3{grid-template-columns:repeat(3,minmax(0,1fr))}}"
          ".rl-trades{list-style:none;margin:14px 0 0;padding:0;background:var(--card);border:1px solid var(--line);border-radius:12px;max-width:760px}"
          ".rl-trades li{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:12px 16px;border-top:1px solid var(--rule)}"
          "section.block .rl-trades li{max-width:none}.rl-trades li:first-child{border-top:0}.rl-trades .nm{font-weight:600;color:var(--ink)}"
          ".rl-trades .nm small{display:block;font-size:13.5px;font-weight:400;color:var(--muted);margin-top:2px}"
          ".rl-trades .n{font:700 18px/1 Poppins,system-ui,sans-serif;color:var(--ink);font-variant-numeric:tabular-nums}"
          ".ld-page .ld-cta p.ld-buybtn{margin-top:16px}.ld-page h2,.ld-page h3,.ld-page summary{text-wrap:balance}</style>")
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    src = d["source"]
    foot = (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            f'<p>Sources: {E(src["name"])} ({E(src["url"])}) and City of Chicago Data Portal, Food Inspections ({E(FOOD_URL)}), pulled {E(pulled)}. {E(src["modified"])} A license shows the City issued it on '
            'that date; it does not say a business is open today or buying anything. No business named here has endorsed or works with '
            'ProofNotFluff. Public information for planning sales calls; not legal or business advice and no promise of work.</p>'
            f'<p>{E(M.CITY_DISCLAIMER["Chicago"])}</p><p>ProofNotFluff is not affiliated with or endorsed by the City of Chicago.</p>'
            '<p>Made by ProofNotFluff with AI assistance from public City data. The page counts visits with Cloudflare Web Analytics, which sets no '
            'cookies.</p></div></footer>\n</body></html>')
    return (M.HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=M.SHOP, ld=ld, bodycls=' class="ld-page"',
                          robots=robots, analytics=M.analytics_tag()) + body + foot)


def selftest():
    import re, sys, tempfile
    sys.path.insert(0, HERE)
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("kind") == "licleads"][0]
    html = page_html(spec)
    assert 'content="noindex' in html or not spec.get("draft"), "draft page must be noindex"
    assert spec.get("checkout") or "Tell me when it opens" in html, "no buy button before launch"
    assert "—" not in html and "–" not in html
    assert "one’s own risk" in html or "one's own risk" in html
    assert html.count("<h1>") == 1
    # planted: a sample with an empty trade and no area still renders, and the counts on the page are the file's
    d = json.load(open(os.path.join(ROOT, spec["data"]), encoding="utf-8"))
    d["segments"] = {k: [] for k in d["segments"]} | {"food": [{"business": "Planted Grill", "address": "1 N State St", "communityArea": "Loop",
                     "licenseType": "Retail Food Establishment", "activity": "Restaurant", "issued": d["window"]["to"]}]}
    d["counts"]["areasWeek"], d["counts"]["kept30"] = [], 4321
    tmp = tempfile.mkdtemp()
    f = os.path.join(tmp, "s.json")
    json.dump(d, open(f, "w"))
    h2 = page_html(dict(spec, data=os.path.relpath(f, ROOT)))
    assert "Planted Grill" in h2 and "4,321" in h2 and "has all 4,321 from" in h2 and "Busiest area" not in h2
    assert not re.search(r"\{[a-z_]+\[|\{c\[", html), "a template placeholder reached the page (holdout 1, round 4)"
    text = re.sub(r"<[^>]+>", " ", html).lower()
    for w in ("guarantee", "dirty", "violator"):
        assert w not in text, w
    print("lic_site selftest ok")


if __name__ == "__main__":
    selftest()
