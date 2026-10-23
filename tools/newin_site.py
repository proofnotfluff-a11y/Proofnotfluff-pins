#!/usr/bin/env python3
"""New in Chicago: the free weekly page of businesses the City just licensed, by type and neighborhood (site/pages.json
kind "newin", written by tools/make_site.py, which calls page_html here). The traffic layer Todd asked for on Oct 23, 2026
(coo/DECISIONS-2026-10-23.md): a page locals search for ("new restaurants in Chicago"), which sends vendors to the
Chicago New Business Licenses list and locals to a free weekly email. Todd's go to publish it and add an email signup:
Oct 23, 2026.

Data: permits/licenses-chicago/sample.json (tools/licenses_chicago.py), its "week" list: every business licensed in
the last 7 days, business fields only. The data layer has already left out names that could be a person's full name,
licenses for one person's own work or an event, home and mail-drop addresses, the do-not-list, and any business with a
City food inspection Fail on file (and, when the food inspection check could not run, every food business). This page
also drops every food row when that check did not run, so a refresh can never name a business with a failed record.
Before the "week" list exists (a sample from before Oct 23) the page falls back to the per-trade sample.

The email box stays a mailto note to the ProofNotFluff mailbox until the spec carries "kitForm" (a Kit form Todd makes
in his Kit account); then it is a Kit form with the privacy line (Legal desk review, Oct 23, items 10 and 11).

Usage: python3 tools/newin_site.py      selftest on the committed sample and planted rows
"""
import collections, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ORDER = ["food", "retail", "beauty", "venue", "auto", "care"]
LABEL = {"care": "Children's classes and care"}     # the City's day care group also holds classes (Legal desk 8, design 6)
FOOD_URL = "https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5"
# Plain labels for the City's license activity text (design director, Oct 23: the raw text read like an export).
# First match wins; the City's own wording stays in the paid list.
PLAIN = [
    (r"TAVERN|CONSUMPTION OF LIQUOR", "Bar"), (r"PACKAGED LIQUOR|PACKAGE GOODS", "Liquor store"),
    (r"DELI, BUTCHER OR BAKERY|BAKERY", "Bakery or deli"), (r"COFFEE", "Cafe"), (r"CATER", "Caterer"),
    (r"WITH DINING|DINING ON PREMISES|WITH SEATING", "Restaurant"), (r"WITHOUT DINING", "Takeout"),
    (r"PERISHABLE FOOD", "Grocery"), (r"FOOD", "Food business"),
    (r"BARBER", "Barber"), (r"NAIL", "Nail salon"), (r"HAIR", "Hair salon"), (r"MASSAGE", "Massage"),
    (r"SKIN ?CARE|WAX|ESTHETIC|AESTHETIC|FACIAL|LASH|BROW", "Skin care"), (r"TATTOO|BODY ART", "Tattoo studio"),
    (r"FITNESS|GYM|HEALTH CLUB|YOGA|PILATES", "Fitness"), (r"\bSPA\b", "Spa"),
    (r"PARKING", "Parking"), (r"ANIMAL GROOMING", "Pet grooming"), (r"ANIMAL|DOG|PET", "Pet services"),
    (r"TIRE", "Tire shop"), (r"CAR WASH", "Car wash"), (r"FILLING STATION", "Gas station"), (r"VEHICLE PARTS", "Auto parts"),
    (r"MOTOR VEHICLE|AUTO|HAZARDOUS MATERIALS", "Auto shop"),
    (r"DANCE|BALLET|MUSIC|INSTRUCTION|TUTOR|CLASS|SCHOOL", "Classes"), (r"DAY ?CARE|CHILD", "Child care"),
    (r"CONSULT", "Consulting"), (r"PHOTOGRAPH|VIDEO", "Photo and video"), (r"FURNITURE", "Furniture store"),
    (r"MANUFACTUR", "Manufacturing"), (r"HOTEL|LODGING|BED AND BREAKFAST", "Lodging"),
    (r"ENTERTAINMENT|AMUSEMENT|EVENT|BANQUET", "Entertainment and events"), (r"GENERAL MERCHANDISE|RETAIL", "Shop"),
]


FOOD_LABELS = {"Bar", "Liquor store", "Bakery or deli", "Cafe", "Caterer", "Restaurant", "Takeout", "Grocery", "Food business"}


def plain(x):
    t = " ".join([x.get("activity") or "", x.get("licenseType") or ""]).upper()
    seg = x.get("segment")
    if seg == "venue" and re.search(r"ENTERTAINMENT|AMUSEMENT|EVENT|BANQUET|PLACE OF AMUSEMENT", t):
        return "Entertainment and events"
    for pat, lab in PLAIN:
        if seg not in (None, "food") and lab in FOOD_LABELS:
            continue        # a shop that also sells snacks is a shop, not a grocery
        if re.search(pat, t):
            return lab
    return "Services" if x.get("segment") == "retail" else "New business"


def rows_of(d):
    rows = d.get("week")
    if rows is None:
        rows = [dict(x, segment=k) for k in ORDER for x in (d.get("segments") or {}).get(k, [])]
    if not ((d.get("counts") or {}).get("checks") or {}).get("foodInspections"):
        rows = [r for r in rows if r.get("segment") != "food"]        # no food business named without the Fail check
    return sorted(rows, key=lambda r: (r["issued"], r["business"]), reverse=True)


def page_html(p):
    import make_site as M
    from licenses_chicago import TRADES, street_unit
    E = M.E
    d = json.load(open(os.path.join(ROOT, p["data"]), encoding="utf-8"))
    c, w = d["counts"], d["window"]
    label = {k: LABEL.get(k, s) for k, _, s, _ in TRADES}
    url, rel = M.BASE + p["slug"] + "/", "../"
    rows = rows_of(d)
    pulled = M.nice_date(d["source"]["fetchedAt"])
    by_area = collections.defaultdict(list)
    for r in rows:
        by_area[r.get("communityArea") or "Other areas"].append(r)
    areas = sorted(by_area.items(), key=lambda kv: (kv[0] == "Other areas", -len(kv[1]), kv[0]))
    named = [(a, xs) for a, xs in areas if a != "Other areas"]
    top = named[0] if named else None
    ties = sum(1 for a, xs in named[1:] if top and len(xs) == len(top[1]))   # a tie has no single top area
    by_type = collections.Counter(r["segment"] for r in rows)
    food, n = by_type.get("food", 0), len(rows)
    first = next((k for k in ORDER if by_type.get(k)), "")

    def card(x):
        st, _ = street_unit(x["address"])
        where = E(st) + (f' &middot; {E(x["communityArea"])}' if x.get("communityArea") else "")
        return (f'<li class="ni-c"><b>{E(x["business"])}</b><span class="ni-k">{E(plain(x))}</span>'
                f'<span class="ni-m">{where}</span><span class="ni-m">Licensed <span class="ni-d">{E(M.nice_date(x["issued"]))}</span></span></li>')

    lede = (f'{n:,} businesses got a new City of Chicago license in the week to {E(M.nice_date(w["to"]))}, {food:,} of them food and drink.')
    tiles = ('<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">New this week</div><div class="val">{n:,}</div><div class="sub">businesses on this page</div></div>'
             f'<div class="tile"><div class="lab">Food and drink</div><div class="val">{food:,}</div><div class="sub">restaurants, cafes, bars, food shops</div></div>'
             f'<div class="tile"><div class="lab">Neighborhoods</div><div class="val">{len(named):,}</div><div class="sub">with a new license this week</div></div>'
             + (f'<div class="tile ni-top"><div class="lab">Top area</div><div class="val">{E(top[0])}</div><div class="sub">{len(top[1]):,} new this week</div></div>'
                if top and not ties else "")
             + f'</div><p class="asof">From City records pulled {E(pulled)}. New page every week.</p>'
             f'<p class="ni-strip"><span>Sell to new businesses? All {c["kept30"]:,} from the last 30 days, sorted by trade.</span>'
             f'<a href="{rel}{E(p.get("vendorSlug", "chicago-new-business-licenses"))}/">See the business list</a></p>')
    chips = ('<p class="ni-chips">' + "".join(f'<a href="#t-{k}">{E(label[k])} <span>{by_type[k]:,}</span></a>' for k in ORDER if by_type.get(k)) + '</p>')
    groups = [f'<h3 class="lc-h3 ni-h3" id="t-{k}">{E(label[k])} <span class="ni-n">{by_type[k]:,}</span></h3><ul class="ni-l">{"".join(card(x) for x in rows if x["segment"] == k)}</ul>'
              for k in ORDER if by_type.get(k)]
    mini = (f'<div class="ni-mini"><b>Get New in Chicago by email</b><a class="btn" href="#mail">{"Get the Monday email" if p.get("kitForm") else "Ask for the email"}</a></div>')
    by_t = ('<section class="block" id="list"><h2>New licenses, by type</h2>' + chips + "".join(groups[:1]) + (mini if len(groups) > 1 else "")
            + "".join(groups[1:]) + '</section>')
    peak = max((len(xs) for _, xs in named), default=1)
    bars = ('<figure class="ni-bars" aria-label="Neighborhoods with the most new licenses this week"><figcaption>Most new licenses this week</figcaption>'
            + "".join(f'<div class="ni-bar"><span>{E(a)}</span><i style="width:{max(8, round(len(xs) / peak * 100))}%"></i><b>{len(xs):,}</b>'
                      f'<small>{E(", ".join(x["business"] for x in xs))}</small></div>'
                      for a, xs in named[:6]) + '</figure>')
    shown = {a for a, _ in named[:6]}
    by_a = ('<section class="block" id="areas"><h2>By neighborhood</h2>' + bars + '<h3 class="lc-h3 ni-h3">More neighborhoods</h3><div class="ni-g">'
            + "".join(f'<div class="ni-a"><b>{E(a)}</b><span>{E(", ".join(x["business"] for x in xs))}{f" ({len(xs):,})" if len(xs) > 1 else ""}</span></div>'
                      for a, xs in areas if a not in shown)
            + '</div></section>')
    HIST = {"first": "First license", "site": "New site", "added": "Added license", "relicensed": "Relicensed"}
    sample = [x for k in ("food", "beauty", "retail", "venue", "auto")    # one row per trade, so the preview shows the sorting
              for x in [next((r for r in rows if r["segment"] == k and r.get("history") in HIST and not street_unit(r["address"])[1]), None)] if x][:3]
    preview = ('<div class="ni-prev" aria-label="Preview of the members\' list"><p class="ni-prevh">What members see, this week\'s rows</p>'
               + "".join(f'<div class="ni-pr"><div><b>{E(x["business"])}</b><span>{E(label[x["segment"]])}, {E(x.get("communityArea") or "Chicago")}</span></div>'
                         f'<em>{HIST[x["history"]]}</em></div>' for x in sample) + '</div>') if sample else ""
    if p.get("kitForm"):
        mail = M.kit_form(p["kitForm"], "Your email", "Get the Monday email", "niEmail",
                          note="We use your address only for this email. Stop any time with one click. Stored with Kit, our email provider, and never sold.")
        mail_h, mail_p = 'Get <span class="ni-nw">New in Chicago</span> every week', "The week's new restaurants, shops and salons in one short email. Free."
    else:
        notify = p.get("notify") or "mailto:hello@proofnotfluff.com?subject=New%20in%20Chicago%3A%20send%20me%20the%20weekly%20email"
        mail = f'<p class="ld-buybtn"><a class="btn" href="{E(notify)}">Ask for the email</a></p>'
        mail_h, mail_p = 'Get <span class="ni-nw">New in Chicago</span> by email', "Starting soon: the week's new restaurants, shops and salons in one short email. Free."
    say = {"food": "restaurants, cafes, bars and food shops", "beauty": "salons, spas and gyms", "retail": "shops and services"}
    week_pts = [f'{by_type[k]:,} new {say[k]}' for k in say if by_type.get(k)]
    week_pts += [f'The busiest area: {top[0]}, {len(top[1]):,}\u00a0new'] if top and not ties else []
    week_box = ('<div class="ni-prev"><p class="ni-prevh">This week\'s email would have had</p>'
                + "".join(f'<div class="ni-pr"><div><b>{E(t)}</b></div></div>' for t in week_pts) + '</div>') if week_pts else ""
    boxes = (f'<section class="block" id="mail"><div class="ni-two">'
             f'<div class="cta ld-cta"><div><h2>{mail_h}</h2><p>{mail_p}</p>{week_box}'
             + ("" if p.get("kitForm") else f'<p class="ni-fine">We use your address only for this email, and you can stop any time. See <a href="{rel}privacy/">Privacy</a>.</p>')
             + f'{mail}</div></div>'
             f'<div class="cta ld-cta"><div><h2>Sell to new businesses?</h2><p>The full list has all {c["kept30"]:,} from the last 30 days, for cleaning, pest control and any vendor a new business needs.</p>'
             '<ul class="ni-pts"><li>Sorted by trade, with a map</li><li>Filters by area, date and license</li><li>An Excel file every Monday</li></ul>'
             + preview +
             f'<p class="ld-buybtn"><a class="btn" href="{rel}{E(p.get("vendorSlug", "chicago-new-business-licenses"))}/">See the business list</a></p></div></div>'
             '</div></section>')
    method = '<section class="block"><h2>How this page is made</h2>' + "".join(f"<p>{E(x)}</p>" for x in p["method"]) + "</section>"
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), (p["h1"], None)])
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}
    ld = M.ld_tags(crumb_ld, faq_ld) + ("<style>.ni-chips{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 4px}.ni-chips a{display:inline-flex;gap:6px;align-items:center;"
          "min-height:44px;padding:0 14px;border:1px solid var(--line);border-radius:999px;background:var(--card);color:var(--ink);text-decoration:none;font-weight:600}"
          ".ni-chips a span{color:var(--muted);font-weight:400}@media(max-width:759px){main .ni-chips a{padding:0 14px!important}}"
          ".ni-l{list-style:none;margin:0;padding:0;display:grid;gap:10px}"
          "@media(min-width:760px){.ni-l{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(min-width:1100px){.ni-l{grid-template-columns:repeat(3,minmax(0,1fr))}}"
          ".ni-c{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;display:flex;flex-direction:column;gap:3px}"
          ".ni-c b{font:600 17px/1.3 Poppins,system-ui,sans-serif;color:var(--ink)}.ni-c span{font-size:14.5px;color:var(--ink2)}"
          ".ni-c .ni-k{font-weight:600;color:var(--ink)}.ni-c .ni-m{color:var(--muted)}.ni-d{white-space:nowrap}"
          ".ni-g{display:grid;gap:0 24px;grid-template-columns:1fr;margin-top:12px;padding:4px 16px 14px;background:var(--card);border:1px solid var(--line);border-radius:12px}"
          "@media(min-width:480px){.ni-g{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(min-width:900px){.ni-g{grid-template-columns:repeat(3,minmax(0,1fr))}}"
          ".ni-g .ni-a{display:block;padding:8px 0;line-height:1.4;border-bottom:1px solid var(--rule)}.ni-g .ni-a span::before{content:' \\00b7  ';color:var(--muted)}.ni-a b{color:var(--ink);font-weight:600}"
          ".ni-a em{font-style:normal;font-size:12.5px;font-weight:700;color:var(--muted)}.ni-a span{font-size:14px;color:var(--ink2);line-height:1.35}"
          ".ni-g .ni-a{background:var(--card);border:1px solid var(--line);border:0;border-bottom:1px solid var(--rule);border-radius:0;margin:0;max-width:none;background:none}"
          ".ni-a summary{display:flex;justify-content:space-between;align-items:center;gap:10px;min-height:44px;padding:8px 14px;cursor:pointer;font-weight:600;color:var(--ink);list-style:none}"
          ".ni-a summary::-webkit-details-marker{display:none}.ni-a summary b{font:700 16px Poppins,system-ui,sans-serif;font-variant-numeric:tabular-nums}"
          ".ni-a p{margin:0;padding:0 14px 12px;font-size:14px;color:var(--ink2)}"
          ".ni-two{display:grid;gap:16px;align-items:stretch}@media(min-width:900px){.ni-two{grid-template-columns:1fr 1fr}}"
          ".ni-two .cta{grid-template-columns:1fr;align-items:stretch;height:100%}.ni-two .cta>div{display:flex;flex-direction:column;height:100%}"
          ".ni-two .cta h2{margin-top:0;text-wrap:balance}"
          ".ni-two .ld-buybtn,.ni-two .st-form{margin-top:auto!important;padding-top:20px;border-top:1px solid var(--band-rule)}.ni-fine{margin:12px 0 22px!important}"
          ".ni-strip{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;justify-content:space-between;margin:14px 0 0;padding:12px 16px;"
          "background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:10px;color:var(--ink)}"
          ".ni-strip a{font-weight:700;color:var(--accent-text)}"
          ".ni-mini{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;justify-content:space-between;margin:22px 0 4px;padding:14px 18px;"
          "background:var(--band);color:#fff;border-radius:12px}.ni-mini b{font:600 17px Poppins,system-ui,sans-serif}"
          ".ni-bars{margin:12px 0 18px;padding:16px 18px;background:var(--card);border:1px solid var(--line);border-radius:12px;max-width:none}"
          ".ni-bars figcaption{font-weight:700;color:var(--ink);margin-bottom:10px}"
          ".ni-bar{display:grid;grid-template-columns:minmax(110px,180px) 1fr 28px;gap:2px 10px;align-items:center;margin:10px 0;font-size:14.5px;color:var(--ink2)}"
          ".ni-bar>span{font-weight:600;color:var(--ink)}.ni-bar small{grid-column:1/-1;font-size:13px;color:var(--muted);line-height:1.35}"
          ".ni-bar i{display:block;height:12px;border-radius:6px;background:var(--accent)}.ni-bar b{text-align:right;color:var(--ink);font-variant-numeric:tabular-nums}"
          ".ni-prev{margin:16px 0 0;background:var(--card);border-radius:10px;overflow:hidden}.ni-prevh{margin:0!important;padding:8px 14px;font-size:12.5px;"
          "color:var(--muted)!important;border-bottom:1px solid var(--rule)}"
          ".ni-pr{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:9px 14px;border-bottom:1px solid var(--rule)}.ni-pr:last-child{border:0}"
          ".ni-pr b{display:block;color:var(--ink);font:600 15px Poppins,system-ui,sans-serif}.ni-pr span{display:block;font-size:13px;line-height:1.35;color:var(--ink2)}"
          ".ni-pr em{font-style:normal;font-size:12.5px;font-weight:700;color:var(--warn-ink);background:var(--warn-tint);border-radius:999px;padding:4px 10px;white-space:nowrap}"
          "@media(max-width:599px){.ld-page .crumbs{display:none}"
          ".ni-top .val{font-size:16px!important}}"
          ".lc-h3.ni-h3{font:600 24px/1.25 Poppins,system-ui,sans-serif;margin:48px 0 14px;display:block}"
          ".ni-n{display:inline-flex;vertical-align:4px;margin-left:8px;align-items:center;height:26px;padding:0 10px;border-radius:999px;background:var(--rule);color:var(--ink2);font:600 14px system-ui,sans-serif}"
          ".ld-page details summary{text-wrap:wrap!important}.ni-nw{white-space:nowrap}.ni-bar small,.ni-a span{text-wrap:pretty}"
          "@media (prefers-color-scheme:dark){.ni-mini{border:1px solid var(--accent)}}.ni-a summary span{text-align:left}.ni-pts{margin:4px 0 0;padding-left:20px}.cta .ni-pts li{margin:2px 0;color:var(--band-text)}"
          ".ni-prev .ni-pr b{font-size:14.5px}.ni-fine{font-size:13.5px;opacity:.85}.ni-fine a{color:inherit}"
          ".ni-top .val{font:600 18px/1.3 Poppins,system-ui,sans-serif}"
          "@media (prefers-color-scheme:dark){.ld-page .tile.key,.ni-two .cta{border:2px solid var(--accent)}}"
          ".lc-h3{font:600 18px/1.3 Poppins,system-ui,sans-serif;margin:26px 0 10px;color:var(--ink)}.lc-h3 span{font:400 15px/1.3 system-ui,sans-serif;color:var(--muted)}"
          ".rl-act{margin:18px 0 22px}.ld-page h2,.ld-page h3{text-wrap:balance}.ld-page summary{text-wrap:pretty}.ni-hero .lede{text-wrap:wrap}</style>")
    body = (f'{crumb}<div class="ld-hero ni-hero"><p class="eyebrow">Updated {E(pulled)}</p><h1>{E(p["h1"])}</h1><p class="lede">{lede}</p>'
            f'<div class="ld-heroact rl-act"><a class="btn" href="#t-{first}">See this week\'s {n:,}</a></div></div>'
            f'{tiles}{by_t}{by_a}{boxes}{method}{M.faq_block(p["faq"])}')
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    src = d["source"]
    foot = (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            f'<p>Sources: City of Chicago Data Portal, <a href="{E(src["url"])}">Business Licenses dataset</a> and <a href="{E(FOOD_URL)}">Food Inspections dataset</a>, pulled {E(pulled)}. '
            'A license shows the City issued it on that date; it does not say a business is open today. Names that could be a person\'s full name, '
            'licenses for one person\'s own work or for an event, home addresses, and businesses with a failed City food inspection on file are left off '
            'this page. A business can be missing for many reasons, and being listed or missing says nothing about its inspections, quality or standing. '
            'No business named here has endorsed or works with ProofNotFluff.</p>'
            f'<p>{E(M.CITY_DISCLAIMER["Chicago"])}</p><p>ProofNotFluff is not affiliated with or endorsed by the City of Chicago.</p>'
            '<p>Made by ProofNotFluff with AI assistance from public City data. The page counts visits with Cloudflare Web Analytics, which sets no '
            'cookies.</p></div></footer>\n</body></html>')
    return (M.HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=M.SHOP, ld=ld, bodycls=' class="ld-page"',
                          robots=robots, analytics=M.analytics_tag()) + body + foot)


def selftest():
    import sys, tempfile
    sys.path.insert(0, HERE)
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("kind") == "newin"][0]
    html = page_html(spec)
    assert 'content="noindex' in html or not spec.get("draft"), "draft page must be noindex"
    assert "—" not in html and "–" not in html and html.count("<h1>") == 1
    assert "Food Inspections dataset</a>" in html and "4ijn-s7e5" in html and "says nothing about its inspections" in html, "Legal desk 4 and 6"
    d = json.load(open(os.path.join(ROOT, spec["data"]), encoding="utf-8"))
    d["counts"]["checks"]["foodInspections"] = True
    d["week"] = [{"business": "Planted Bakery", "address": "1 N State St", "communityArea": "Loop", "licenseType": "Retail Food Establishment",
                  "activity": "Operation of a Deli, Butcher or Bakery", "issued": d["window"]["to"], "history": "first", "segment": "food"},
                 {"business": "Planted Nails", "address": "2 W Lake St", "communityArea": "", "licenseType": "Limited Business License",
                  "activity": "Nail Services", "issued": d["window"]["to"], "history": "first", "segment": "beauty"}]
    f = os.path.join(tempfile.mkdtemp(), "s.json")
    json.dump(d, open(f, "w"))
    h2 = page_html(dict(spec, data=os.path.relpath(f, ROOT)))
    assert "Planted Bakery" in h2 and "Planted Nails" in h2 and ">2</div>" in h2, "the tile counts the rows shown"
    assert "Bakery or deli" in h2 and "Nail salon" in h2 and "Operation of a Deli" not in h2, "plain labels"
    assert h2.index(">Loop<") < h2.index(">Other areas<"), "areas with a name first"
    # planted: the food inspection check did not run, so no food business is named
    d["counts"]["checks"]["foodInspections"] = False
    json.dump(d, open(f, "w"))
    h3 = page_html(dict(spec, data=os.path.relpath(f, ROOT)))
    assert "Planted Bakery" not in h3 and "Planted Nails" in h3, "food rows need the Fail check"
    # planted: with a Kit form the box is a real form with the privacy line; without one, a note
    h4 = page_html(dict(spec, kitForm="1234567"))
    assert "app.kit.com/forms/1234567/subscriptions" in h4 and "Stored with Kit" in h4 and "Starting soon" not in h4
    assert "Starting soon" in html or spec.get("kitForm")
    text = re.sub(r"<[^>]+>", " ", html).lower()
    for word in ("guarantee", "dirty", "violator"):
        assert word not in text, word
    assert "every new business the city" not in text and "every new business" not in spec["desc"].lower(), "Legal desk 1"
    assert plain({"activity": "Tavern - Consumption of Liquor on Premises"}) == "Bar"
    assert plain({"activity": "Provide 4 or More Parking Spaces For a Fee"}) == "Parking"
    assert plain({"activity": "Charges a Fee for Entertainment | Retail Sales of General Merchandise and Non-Perishable Food",
                  "licenseType": "Public Place of Amusement", "segment": "venue"}) == "Entertainment and events"
    assert plain({"activity": "Retail Sales of General Merchandise and Non-Perishable Food", "segment": "retail"}) == "Shop"
    print("newin_site selftest ok")


if __name__ == "__main__":
    selftest()
