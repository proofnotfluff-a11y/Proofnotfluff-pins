#!/usr/bin/env python3
"""The area seat offer on the Chicago Construction Cleaning Leads page (site/pages.json "areaSeats"; Todd, live chat, Oct 26,
2026, coo/DECISIONS-2026-10-26.md; launches/chicago-cleaning-area-seats.md). tools/make_site.py leads_page_html calls
seats_html here.

The block shows only once at least one seat has its Gumroad checkout in site/pages.json (areaSeats.checkout.<slug>), or
in a live session's preview build (PNF_SEAT_PREVIEW=1, never committed). Until then the live page does not change.

Every number comes from committed files: permits/chicago/area_counts.json (12 full months by community area,
tools/exclusive_areas.py), permits/chicago/area_week.json when the weekly workflow has written it (this week's open and new
projects per seat, tools/area_seats.py --week-counts), and site/area_seats.json (territories and held seats).
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def seats_spec(p):
    s = p.get("areaSeats") or {}
    if any((s.get("checkout") or {}).values()) or os.environ.get("PNF_SEAT_PREVIEW") == "1":
        return s
    return None


def _month(m):
    import datetime as dt
    d = dt.date.fromisoformat(m + "-01")
    return d.strftime("%b %Y")


def _whole(x):
    return int(x + 0.5)


def seats_html(p, spec, rel):
    import urllib.parse
    import make_site as M
    import area_seats as A
    E = M.E
    cfg = A.load()
    st = A.stats(cfg)
    week = {}
    wk_asof = ""
    if os.path.isfile(A.WEEK):
        w = json.load(open(A.WEEK, encoding="utf-8"))
        week = {t["slug"]: t for t in w["territories"]}
        wk_asof = M.nice_date(w["fetchedAt"])
    held = set(cfg.get("held", []))
    co = spec.get("checkout") or {}
    price = E(str(spec["price"]))
    cap = len(cfg["territories"])
    left = cap - len(held)
    # the map's text description uses the same open counts as the list (this week's when the weekly file exists; holdout B)
    st_map = dict(st, territories=[dict(t, openNow=week.get(t["slug"], {}).get("open", t["openNow"])) for t in st["territories"]])
    svg = A.svg(cfg, st=st_map, width=340, title="Map of the six Chicago cleaning lead areas")
    lo = min(_whole(t["avg"]) for t in st["territories"])
    hi = max(_whole(t["avg"]) for t in st["territories"])
    rng = f'{_month(st["from"])} to {_month(st["to"])}'
    legend = "".join(f'<li><span class="as-num as-t{i + 1}b">{i + 1}</span>{E(t["name"])}</li>'
                     for i, t in enumerate(cfg["territories"]))
    items = []
    for i, (t, s) in enumerate(zip(cfg["territories"], st["territories"])):
        wk = week.get(t["slug"], {})
        open_n = wk.get("open", s["openNow"])
        new_n = wk.get("newWeek")
        link = co.get(t["slug"])
        taken = t["slug"] in held
        mail = "mailto:hello@proofnotfluff.com?subject=" + urllib.parse.quote(f"5 newest projects: {t['name']}")
        if taken:
            act = '<span class="as-held">Taken</span>'
        elif link:
            act = (f'<a class="btn as-btn" href="{E(link)}" rel="noopener" aria-label="Take the {E(t["name"])} seat, ${price} a month">Take this area</a>'
                   f'<a class="as-free" href="{E(mail)}">Send me its 5 newest free</a>')
        else:
            act = ('<span class="btn as-btn sb-off" aria-disabled="true">Take this area</span>'
                   f'<a class="as-free" href="{E(mail)}">Send me its 5 newest free</a>')
        cnt = json.load(open(A.COUNTS))["areas"]   # busiest community areas first
        names = sorted(t["areas"], key=lambda n: (-cnt.get(n, {}).get("total12", 0), n))
        if len(names) <= 3:
            ca = f'<p class="as-ca">{E(", ".join(names))}</p>'
        else:
            ca = (f'<details class="as-more"><summary>{E(", ".join(names[:3]))} and {len(names) - 3} more</summary>'
                  f'<p>{E(", ".join(names))}</p></details>')
        items.append(
            f'<li class="as-item{" is-held" if taken else ""}"><span class="as-sw as-t{i + 1}" aria-hidden="true"></span>'
            f'<div class="as-body"><h3><span class="as-num as-t{i + 1}b" aria-hidden="true">{i + 1}</span>{E(t["name"])}</h3>'
            f'<p class="as-stats"><b>About {_whole(s["avg"])} new projects a month</b></p>'
            f'<p class="as-sub">{open_n:,} open now' + (f' · {new_n} new this week' if new_n is not None else "")
            + f'</p><p class="as-sub">Slowest month {s["low"]}, busiest {s["high"]}</p>{ca}</div>'
            f'<div class="as-act">{act}</div></li>')
    asof = f"Open counts from the list of {E(wk_asof)}." if wk_asof else f"Open counts from City records pulled {E(M.nice_date(st['ranAt']))}."
    return (
        f'<section class="block sb as" id="areas" aria-labelledby="asH"><div class="sb-card as-card">'
        '<p class="eyebrow sb-eye">Area seats for cleaning companies</p>'
        '<h2 id="asH">One cleaning company per area of Chicago.</h2>'
        f'<p class="as-price"><b>${price} a month per area.</b> No&nbsp;lock&#8209;in, cancel any time.</p>'
        f'<p class="sb-left"><span class="sb-dots" aria-hidden="true">{"".join("<i class=on></i>" if i < left else "<i></i>" for i in range(cap))}</span>'
        f'<b>{left} of {cap} areas open</b></p>'
        '<p class="sb-lede">Hold an area and we sell its list to you and to no other company. From the next Monday we take its projects '
        f'out of our ${E(str(p["price"]))} weekly list, our free sample and our emails to other cleaning companies.</p>'
        '<div class="as-cols"><div class="as-side"><figure class="as-map">'
        f'{svg}<ol class="as-legend" aria-hidden="true">{legend}</ol>'
        f'<figcaption>Six areas drawn from the City\'s 77 community areas so each averaged 10 or more new qualifying '
        f'projects a month from {E(rng)}.</figcaption>'
        f'<details class="as-how"><summary>How the numbers are counted</summary><p>New projects a month: permits the City issued from {E(rng)} that passed the list\'s rules when issued, '
        f'whatever their status today, about {lo} to {hi} an area. Months vary: every area had some months under 10. {asof}</p></details></figure>'
        '<ul class="sb-get checks"><li>Every open apartment and commercial project of $500,000 or more in your area with a business as general contractor, closest to a final clean first, with the builder on each and the builder\'s office phone or email where their own website lists one.</li>'
        '<li>New permits each Monday, in a members\' app with a map and in an Excel file, plus the pitch kit.</li>'
        '<li>Your area only, and only you. The permits are public City of Chicago records that anyone can read on the City\'s site; '
        'exclusive means we sell your area\'s list to you alone.</li></ul></div>'
        f'<ol class="as-list" aria-label="The six areas">{"".join(items)}</ol></div>'
        '<p class="sb-same">Want to see an area first? <a href="mailto:hello@proofnotfluff.com?subject=5%20newest%20projects">Write to hello@proofnotfluff.com</a> and we will send its 5 newest projects free, for any area no one holds yet. '
        f'Prefer the whole city, shared? The weekly list stays ${E(str(p["price"]))} a month for every area no one holds.</p>'
        f'<p class="ld-secure">Secure checkout by Gumroad. ${price} is charged at checkout and again each month until you cancel. '
        f'No lock-in: cancel any time from your Gumroad receipt or library and you are not charged again. '
        f'<a href="{rel}refunds/">Refunds and cancelling</a> · <a href="{rel}chicago-cleaning-area-members/loop/#/terms">Seat Terms</a> '
        '(the same in every area except the area named)</p>'
        '</div></section>')


# territory colours: six hues near the site's own (teal, terracotta), lighter in dark mode; the list carries every number in text
SEATS_CSS = (
    ":root{--t1:#3f5f8f;--t2:#c8502f;--t3:#2e6b66;--t4:#b0841f;--t5:#8a5a8e;--t6:#8a9a3b;--map-line:var(--card);--map-pin:var(--ink);--map-pin-ink:var(--card)}"
    "@media (prefers-color-scheme: dark){:root{--t1:#8fb0e0;--t2:#ef8c6b;--t3:#6cc0b6;--t4:#e0b65a;--t5:#c99ad0;--t6:#c9d27a}}"
    ".sb .sb-card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:24px 20px}"
    ".sb .sb-card>p{max-width:68ch;text-wrap:pretty}.sb .ld-secure{font-size:14px;color:var(--muted)}.sb .ld-secure a{color:var(--teal)}"
    ".sb .sb-eye{margin:0 0 6px}.as h2{font-size:28px;line-height:1.2;margin:0 0 10px;text-wrap:balance}"
    ".as-price{margin:0 0 8px;font-size:20px;color:var(--ink2)}.as-price b{color:var(--ink)}"
    ".sb-left{display:flex;align-items:center;gap:10px;margin:0 0 10px;font-size:16px}"
    ".sb-dots{display:inline-flex;gap:5px}.sb-dots i{width:14px;height:14px;border-radius:50%;border:2px solid var(--teal)}.sb-dots i.on{background:var(--teal)}"
    ".sb-lede{margin:0 0 18px;color:var(--ink2)}"
    ".sb-get{margin:14px 0 0;padding-left:0}.sb-get li{margin:0 0 6px}.sb-same{margin:16px 0 6px;color:var(--ink2)}.sb-off{opacity:.55;cursor:not-allowed}"
    ".as-cols{display:grid;gap:20px;margin:4px 0 0}"
    "@media(min-width:880px){.as-cols{grid-template-columns:minmax(280px,360px) minmax(0,1fr);align-items:start}}"
    ".as-map{margin:0;padding:12px;border:1px solid var(--line);border-radius:12px;background:var(--canvas2)}"
    ".as-map svg{display:block;width:100%;max-width:340px;height:auto;margin:0 auto}.as-map svg path{stroke-linejoin:round}"
    ".as-map figcaption{margin:10px 0 0;color:var(--muted);font-size:14px}"
    ".as-legend{list-style:none;margin:10px 0 0;padding:0;display:flex;flex-wrap:wrap;gap:6px 14px;font-size:14px;color:var(--ink2)}"
    ".as-legend li{display:inline-flex;align-items:flex-start;gap:6px;line-height:20px}.as-legend .as-num{width:20px;height:20px;font-size:11.5px}"
    ".as .as-how{margin:8px 0 0;padding:0;border:0;background:none;box-shadow:none;max-width:none;font-size:13.5px;color:var(--muted)}"
    ".as .as-how summary{min-height:44px;padding:10px 0;display:block;font-size:14px;font-weight:600;color:var(--teal);cursor:pointer;list-style:none;background:none;border:0}"
    ".as .as-how summary::-webkit-details-marker{display:none}.as .as-how summary::after{content:' +';font-weight:700}.as .as-how[open] summary::after{content:' \\2212'}"
    ".as .as-how p{margin:0;padding:0}.as-legend{flex-direction:column}.sb-same a{color:var(--teal)}"
    ".as-list{list-style:none;margin:0;padding:0;display:grid;gap:0}"
    ".as-item{display:grid;grid-template-columns:8px minmax(0,1fr);column-gap:12px;row-gap:10px;padding:16px 0;border-top:1px solid var(--line)}"
    ".as-item:first-child{border-top:0;padding-top:4px}"
    "@media(min-width:560px){.as-item{grid-template-columns:8px minmax(0,1fr) 190px;align-items:start}.as-act{padding-top:2px}}"
    ".as-sw{width:8px;align-self:stretch;border-radius:4px;min-height:44px}"
    ".as-t1{background:var(--t1)}.as-t2{background:var(--t2)}.as-t3{background:var(--t3)}.as-t4{background:var(--t4)}.as-t5{background:var(--t5)}.as-t6{background:var(--t6)}"
    ".as-num{display:inline-flex;align-items:center;justify-content:center;flex:none;width:24px;height:24px;border-radius:50%;background:var(--ink);color:var(--card);"
    "font:700 12.5px/1 var(--sans,inherit);font-variant-numeric:tabular-nums;box-shadow:0 0 0 2px var(--card)}"
    ".as-body h3{display:flex;align-items:center;gap:10px;margin:0 0 6px;font-size:17px;line-height:1.3}"
    ".as-stats{margin:0;font-size:15.5px;color:var(--ink)}.as-sub{margin:2px 0 0;font-size:14px;color:var(--muted);font-variant-numeric:tabular-nums}"
    ".as-ca{margin:4px 0 0;font-size:14px;color:var(--muted)}"
    ".as .as-more{margin:2px 0 0;padding:0;border:0;background:none;box-shadow:none;max-width:none;font-size:14px;color:var(--muted)}"
    ".as .as-more summary{cursor:pointer;color:var(--teal);font-size:14px;font-weight:600;padding:12px 0;min-height:44px;display:block;"
    "list-style:none;background:none;border:0;line-height:1.45}"
    ".as .as-more summary::-webkit-details-marker{display:none}.as .as-more summary::after{content:' +';font-size:16px;font-weight:700;color:var(--teal)}"
    ".as .as-more[open] summary::after{content:' \\2212'}.as .as-more p{margin:0 0 4px;padding:0}"
    ".as-act{grid-column:2;display:flex;flex-direction:column;gap:6px;align-items:stretch}@media(min-width:560px){.as-act{grid-column:3}}"
    ".as-btn{justify-content:center;white-space:nowrap;min-height:48px;display:inline-flex;align-items:center;width:100%}"
    ".as-free{display:inline-flex;align-items:center;justify-content:center;min-height:44px;font-size:14px;font-weight:600;color:var(--teal)}"
    ".as-held{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid var(--line);"
    "font-size:14px;font-weight:600;color:var(--muted)}"
    ".as-item.is-held .as-sw{opacity:.35}"
    ".as-t1b{}.as-t2b{}.as-t3b{}.as-t4b{}.as-t5b{}.as-t6b{}"
)
