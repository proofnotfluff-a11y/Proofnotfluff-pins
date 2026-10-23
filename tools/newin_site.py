#!/usr/bin/env python3
"""New in Chicago: the free weekly page of businesses the City just licensed, by neighborhood (site/pages.json kind
"newin", written by tools/make_site.py, which calls page_html here). The traffic layer Todd asked for on Oct 23, 2026
(coo/DECISIONS-2026-10-23.md): a page locals search for ("new restaurants in Chicago"), which sends vendors to the
Chicago New Business Licenses list and locals to a free weekly email.

Data: permits/licenses-chicago/sample.json (tools/licenses_chicago.py), its "week" list: every business licensed in
the last 7 days, business fields only. The data layer has already left out names that could be a person's, person-held
and event licenses, home and mail-drop addresses, and any business with a City food inspection Fail on file. Before
that list exists (a sample from before Oct 23) the page falls back to the per-trade sample.

Until Todd's go the spec carries "draft": true: noindex, off the index and the sitemap, and the email box is a
"Tell me when it starts" note to the ProofNotFluff mailbox (an email-capture form is a major change, CONSTITUTION 2).

Usage: python3 tools/newin_site.py      selftest on the committed sample and planted rows
"""
import collections, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ORDER = ["food", "retail", "beauty", "venue", "auto", "care"]


def rows_of(d):
    if d.get("week") is not None:
        return list(d["week"])
    out = [dict(x, segment=k) for k in ORDER for x in (d.get("segments") or {}).get(k, [])]
    return sorted(out, key=lambda r: (r["issued"], r["business"]), reverse=True)


def page_html(p):
    import make_site as M
    from licenses_chicago import TRADES, street_unit
    E = M.E
    d = json.load(open(os.path.join(ROOT, p["data"]), encoding="utf-8"))
    c, w = d["counts"], d["window"]
    label = {k: s for k, _, s, _ in TRADES}
    url, rel = M.BASE + p["slug"] + "/", "../"
    rows = rows_of(d)
    pulled = M.nice_date(d["source"]["fetchedAt"])
    notify = p.get("notify") or "mailto:hello@proofnotfluff.com?subject=New%20in%20Chicago%3A%20send%20me%20the%20weekly%20email"
    by_area = collections.defaultdict(list)
    for r in rows:
        by_area[r.get("communityArea") or "Other areas"].append(r)
    areas = sorted(by_area.items(), key=lambda kv: (kv[0] == "Other areas", -len(kv[1]), kv[0]))
    by_type = collections.Counter(r["segment"] for r in rows)
    food = by_type.get("food", 0)

    def card(x):
        st, _ = street_unit(x["address"])
        act = (x.get("activity") or "").split(" | ")[0] or x.get("licenseType") or ""
        return (f'<li class="ni-c" data-t="{E(x["segment"])}"><b>{E(x["business"])}</b>'
                f'<span>{E(act)}</span><span class="ni-m">{E(st)} &middot; licensed {E(M.nice_date(x["issued"]))}</span></li>')

    named = [(a, xs) for a, xs in areas if a != "Other areas"]
    top = named[0] if named else None
    ties = sum(1 for a, xs in named[1:] if top and len(xs) == len(top[1]))   # a tie is said, never hidden
    lede = (f'{len(rows):,} new businesses got a City of Chicago business license in the week to {E(M.nice_date(w["to"]))}, '
            f'{food:,} of them restaurants, cafes, bars and food shops. Here they are by neighborhood, from the City\'s own records.')
    tiles = ('<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">New this week</div><div class="val">{len(rows):,}</div><div class="sub">businesses on this page</div></div>'
             f'<div class="tile"><div class="lab">Food and drink</div><div class="val">{food:,}</div><div class="sub">restaurants, cafes, bars, food shops</div></div>'
             f'<div class="tile"><div class="lab">Neighborhoods</div><div class="val">{sum(1 for a, _ in areas if a != "Other areas"):,}</div><div class="sub">with a new business this week</div></div>'
             + (f'<div class="tile"><div class="lab">Top area</div><div class="val lc-area">{E(top[0])}</div><div class="sub">{len(top[1]):,} new this week</div></div>'
               if top and not ties else "")   # a tie has no single top area, so the tile is left out
             + f'</div><p class="asof">From City records pulled {E(pulled)}. New page every Monday. Last 30 days: {c["kept30"]:,} new businesses citywide.</p>')
    chips = ('<p class="ni-chips">' + "".join(f'<a href="#t-{k}">{E(label[k])} <span>{by_type[k]:,}</span></a>' for k in ORDER if by_type.get(k)) + '</p>')
    by_t = ('<section class="block"><h2>What is opening, by type</h2>' + chips + "".join(
        f'<h3 class="lc-h3" id="t-{k}">{E(label[k])} <span>({by_type[k]:,})</span></h3><ul class="ni-l">{"".join(card(x) for x in rows if x["segment"] == k)}</ul>'
        for k in ORDER if by_type.get(k)) + '</section>')
    by_a = ('<section class="block" id="areas"><h2>New this week, by neighborhood</h2><ol class="rl-trades">'
            + "".join(f'<li><span class="nm">{E(a)}<small>{E(", ".join(x["business"] for x in xs))}</small></span><span class="n">{len(xs):,}</span></li>'
                      for a, xs in areas)
            + '</ol></section>')
    boxes = (f'<section class="block"><div class="ni-two">'
             f'<div class="cta ld-cta"><div><h2>Get New in Chicago every Monday</h2><p>The week\'s new restaurants, shops and salons in one short email. Free.</p>'
             f'<p class="ld-buybtn"><a class="btn" href="{E(notify)}">Tell me when it starts</a></p></div></div>'
             f'<div class="cta ld-cta"><div><h2>Sell to new businesses?</h2><p>The full list has all {c["kept30"]:,} from the last 30 days, sorted by trade, with a map, '
             f'filters and an Excel file, for cleaning, pest control and any vendor a new business needs.</p>'
             f'<p class="ld-buybtn"><a class="btn" href="{rel}{E(p.get("vendorSlug", "chicago-new-business-licenses"))}/">See the business list</a></p></div></div>'
             '</div></section>')
    method = '<section class="block"><h2>How this page is made</h2>' + "".join(f"<p>{E(x)}</p>" for x in p["method"]) + "</section>"
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), (p["h1"], None)])
    ld = M.ld_tags(crumb_ld) + ("<style>.ni-chips{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 4px}.ni-chips a{display:inline-flex;gap:6px;align-items:center;"
          "min-height:44px;padding:0 14px;border:1px solid var(--line);border-radius:999px;background:var(--card);color:var(--ink);text-decoration:none;font-weight:600}"
          ".ni-chips a span{color:var(--muted);font-weight:400}.ni-l{list-style:none;margin:0;padding:0;display:grid;gap:10px}"
          "@media(min-width:760px){.ni-l{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(min-width:1100px){.ni-l{grid-template-columns:repeat(3,minmax(0,1fr))}}"
          ".ni-c{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;display:flex;flex-direction:column;gap:3px}"
          ".ni-c b{font:600 17px/1.3 Poppins,system-ui,sans-serif;color:var(--ink)}.ni-c span{font-size:14.5px;color:var(--ink2)}"
          ".ni-c .ni-k{font-size:12.5px;font-weight:700;letter-spacing:.03em;text-transform:uppercase;color:var(--muted)}.ni-c .ni-m{color:var(--muted)}"
          ".ni-two{display:grid;gap:16px}@media(min-width:900px){.ni-two{grid-template-columns:1fr 1fr}}.ni-two .cta{height:100%}"
          ".lc-h3{font:600 18px/1.3 Poppins,system-ui,sans-serif;margin:26px 0 10px;color:var(--ink)}.lc-h3 span{font:400 15px/1.3 system-ui,sans-serif;color:var(--muted)}"
          ".ld-page .tile .val.lc-area{font-size:22px;line-height:1.25}"
          ".rl-trades{list-style:none;margin:14px 0 0;padding:0;background:var(--card);border:1px solid var(--line);border-radius:12px;max-width:760px}"
          ".rl-trades li{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:12px 16px;border-top:1px solid var(--rule)}"
          "section.block .rl-trades li{max-width:none}.rl-trades li:first-child{border-top:0}.rl-trades .nm{font-weight:600;color:var(--ink)}"
          ".rl-trades .nm small{display:block;font-size:13.5px;font-weight:400;color:var(--muted);margin-top:2px}"
          ".rl-trades .n{font:700 18px/1 Poppins,system-ui,sans-serif;color:var(--ink);font-variant-numeric:tabular-nums}"
          "@media(max-width:759px){main .ni-chips a{padding:0 14px!important}}.rl-act{margin:18px 0 22px}.ld-page h2,.ld-page h3{text-wrap:balance}</style>")
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{lede}</p>'
            f'<div class="ld-heroact rl-act"><a class="btn" href="#areas">Jump to neighborhoods</a></div></div>'
            f'{tiles}{by_t}{by_a}{boxes}{method}{M.faq_block(p["faq"])}')
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    src = d["source"]
    foot = (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            f'<p>Source: {E(src["name"])} ({E(src["url"])}), pulled {E(pulled)}. A license shows the City issued it on that date; it does not '
            'say a business is open today. Names that could be a person\'s, licenses held by one person or for an event, home addresses, and '
            'businesses with a failed City food inspection on file are left off this page. No business named here has endorsed or works with ProofNotFluff.</p>'
            f'<p>{E(M.CITY_DISCLAIMER["Chicago"])}</p><p>ProofNotFluff is not affiliated with or endorsed by the City of Chicago.</p>'
            '<p>Made by ProofNotFluff with AI assistance from public City data. The page counts visits with Cloudflare Web Analytics, which sets no '
            'cookies.</p></div></footer>\n</body></html>')
    return (M.HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=M.SHOP, ld=ld, bodycls=' class="ld-page"',
                          robots=robots, analytics=M.analytics_tag()) + body + foot)


def selftest():
    import re, sys, tempfile
    sys.path.insert(0, HERE)
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("kind") == "newin"][0]
    html = page_html(spec)
    assert 'content="noindex' in html or not spec.get("draft"), "draft page must be noindex"
    assert "—" not in html and "–" not in html and html.count("<h1>") == 1
    # planted: the week list wins over the per-trade sample; an area with no name goes last; a page never says more than it lists
    d = json.load(open(os.path.join(ROOT, spec["data"]), encoding="utf-8"))
    d["week"] = [{"business": "Planted Bakery", "address": "1 N State St", "communityArea": "Loop", "licenseType": "Retail Food Establishment",
                  "activity": "Bakery", "issued": d["window"]["to"], "history": "first", "segment": "food"},
                 {"business": "Planted Nails", "address": "2 W Lake St", "communityArea": "", "licenseType": "Limited Business License",
                  "activity": "Nail Services", "issued": d["window"]["to"], "history": "first", "segment": "beauty"}]
    f = os.path.join(tempfile.mkdtemp(), "s.json")
    json.dump(d, open(f, "w"))
    h2 = page_html(dict(spec, data=os.path.relpath(f, ROOT)))
    assert "Planted Bakery" in h2 and "Planted Nails" in h2 and ">2</div>" in h2, "the tile counts the rows shown"
    assert h2.index(">Loop<") < h2.index(">Other areas<"), "areas with a name first"
    assert "1 N State St" in h2, "street shown"
    text = re.sub(r"<[^>]+>", " ", html).lower()
    for word in ("guarantee", "dirty", "violator", "failed inspection list"):
        assert word not in text, word
    assert "tell me when it starts" in text, "no email form before Todd's go"
    print("newin_site selftest ok")


if __name__ == "__main__":
    selftest()
