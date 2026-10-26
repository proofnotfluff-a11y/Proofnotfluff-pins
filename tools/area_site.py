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


def seats_html(p, spec, rel):
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
    svg = A.svg(cfg, width=340, title="Map of the six Chicago cleaning lead areas")
    lo = min(t["avg"] for t in st["territories"])
    hi = max(t["avg"] for t in st["territories"])
    rng = f'{_month(st["from"])} to {_month(st["to"])}'
    items = []
    for i, (t, s) in enumerate(zip(cfg["territories"], st["territories"])):
        wk = week.get(t["slug"], {})
        open_n = wk.get("open", s["openNow"])
        new_n = wk.get("newWeek")
        link = co.get(t["slug"])
        if t["slug"] in held:
            act = '<span class="as-held">Held by a cleaning company</span>'
        elif link:
            act = f'<a class="btn as-btn" href="{E(link)}" rel="noopener" aria-label="Take the {E(t["name"])} seat, ${price} a month">Take this area</a>'
        else:
            act = '<span class="btn as-btn sb-off" aria-disabled="true">Take this area</span>'
        areas = ", ".join(t["areas"])
        more = (f'<details class="as-more"><summary>The {s["areas"]} community areas</summary><p>{E(areas)}</p></details>'
                if s["areas"] > 2 else f'<p class="as-ca">{E(areas)}</p>')
        items.append(
            f'<li class="as-item{" is-held" if t["slug"] in held else ""}"><span class="as-sw as-t{i + 1}" aria-hidden="true"></span>'
            f'<div class="as-body"><h3><span class="as-num">{i + 1}</span> {E(t["name"])}</h3>'
            f'<p class="as-stats"><b>About {s["avg"]:g} new projects a month</b> · {open_n:,} open now'
            + (f' · {new_n} new this week' if new_n is not None else "") + '</p>'
            f'<p class="as-range">Slowest month {s["low"]}, busiest {s["high"]}</p>{more}</div>'
            f'<div class="as-act">{act}</div></li>')
    asof = f"Open counts from the list of {E(wk_asof)}." if wk_asof else f"Open counts from City records pulled {E(M.nice_date(st['ranAt']))}."
    return (
        f'<section class="block sb as" id="areas" aria-labelledby="asH"><div class="sb-card as-card">'
        '<p class="eyebrow sb-eye">Area seats for cleaning companies</p>'
        '<h2 id="asH">One cleaning company per area of Chicago.</h2>'
        '<div class="as-top">'
        f'<p class="sb-left"><span class="sb-dots" aria-hidden="true">{"".join("<i class=on></i>" if i < left else "<i></i>" for i in range(cap))}</span>'
        f'<b>{left} of {cap} areas open</b></p>'
        f'<p class="sb-terms"><b>${price} a month per area.</b> No lock-in, cancel any time.</p>'
        '<p class="sb-lede">Hold an area and its projects go to you and to no other company we sell to. We take them out of our $'
        f'{E(str(p["price"]))} weekly list, our free sample and our emails to other cleaning companies from the next Monday.</p></div>'
        '<div class="as-cols"><figure class="as-map">'
        f'{svg}<figcaption>Six areas drawn from the City\'s 77 community areas so each one averaged 10 or more new qualifying '
        f'projects a month from {E(rng)}.</figcaption></figure>'
        f'<ol class="as-list" aria-label="The six areas">{"".join(items)}</ol></div>'
        f'<p class="as-note">New projects a month: permits the City issued from {E(rng)} that pass the list\'s rules, about {lo:g} to {hi:g} '
        'an area. Months vary: every area had some months under 10. ' + asof + '</p>'
        '<ul class="sb-get checks"><li>Every open project in your area, closest to a final clean first, with the builder on each and the builder\'s office phone or email where their own website lists one.</li>'
        '<li>New permits each Monday, in a members\' app with a map and in an Excel file, plus the pitch kit.</li>'
        '<li>Your area only, and only you. The permits are public City of Chicago records that anyone can read on the City\'s site; '
        'exclusive means we sell your area\'s list to you alone.</li></ul>'
        f'<p class="sb-same">Want to see your area first? Write to hello@proofnotfluff.com and we will send its 5 newest projects free. '
        f'Prefer the whole city, shared? The weekly list stays ${E(str(p["price"]))} a month for every area no one holds.</p>'
        f'<p class="ld-secure">Secure checkout by Gumroad. ${price} is charged at checkout and again each month until you cancel. '
        f'No lock-in: cancel any time from your Gumroad receipt or library and you are not charged again. '
        f'<a href="{rel}refunds/">Refunds and cancelling</a> · <a href="{rel}chicago-cleaning-area-members/loop/#/terms">Seat Terms</a></p>'
        '</div></section>')


# territory colours: six hues near the site's own (teal, terracotta), lighter in dark mode; the list carries every number in text
SEATS_CSS = (
    ":root{--t1:#3f5f8f;--t2:#c8502f;--t3:#2e6b66;--t4:#b0841f;--t5:#8a5a8e;--t6:#5f7f4f;--map-line:var(--card);--map-pin:var(--ink);--map-pin-ink:var(--card)}"
    "@media (prefers-color-scheme: dark){:root{--t1:#8fb0e0;--t2:#ef8c6b;--t3:#6cc0b6;--t4:#e0b65a;--t5:#c99ad0;--t6:#a8c995}}"
    ".sb .sb-card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:24px 20px}"
    ".sb .sb-card>p,.sb .sb-get{max-width:68ch;text-wrap:pretty}.sb .ld-secure{font-size:14px;color:var(--muted)}.sb .ld-secure a{color:var(--teal)}"
    ".sb .sb-eye{margin:0 0 6px}.sb h2{margin:0 0 10px}"
    ".sb-left{display:flex;align-items:center;gap:10px;margin:0 0 6px;font-size:17px}"
    ".sb-dots{display:inline-flex;gap:5px}.sb-dots i{width:14px;height:14px;border-radius:50%;border:2px solid var(--teal)}.sb-dots i.on{background:var(--teal)}"
    ".sb-terms{margin:0 0 12px;font-size:17px}.sb-lede{margin:0 0 18px;color:var(--ink2)}"
    ".sb-get{margin:0 0 12px;padding-left:0}.sb-get li{margin:0 0 6px}.sb-same{margin:0 0 6px;color:var(--ink2)}.sb-off{opacity:.55;cursor:not-allowed}"
    ".as-cols{display:grid;gap:20px;margin:4px 0 14px}"
    "@media(min-width:880px){.as-cols{grid-template-columns:minmax(260px,340px) minmax(0,1fr);align-items:start}}"
    ".as-map{margin:0;padding:12px;border:1px solid var(--line);border-radius:12px;background:var(--canvas2)}"
    ".as-map svg{display:block;width:100%;max-width:340px;height:auto;margin:0 auto}"
    ".as-map figcaption{margin:10px 0 0;color:var(--muted);font-size:14px}"
    ".as-list{list-style:none;margin:0;padding:0;display:grid;gap:0}"
    ".as-item{display:grid;grid-template-columns:10px minmax(0,1fr);column-gap:12px;row-gap:8px;padding:14px 0;border-top:1px solid var(--line)}"
    ".as-item:first-child{border-top:0;padding-top:4px}"
    "@media(min-width:560px){.as-item{grid-template-columns:10px minmax(0,1fr) auto;align-items:center}}"
    ".as-sw{width:10px;align-self:stretch;border-radius:5px;min-height:44px}"
    ".as-t1{background:var(--t1)}.as-t2{background:var(--t2)}.as-t3{background:var(--t3)}.as-t4{background:var(--t4)}.as-t5{background:var(--t5)}.as-t6{background:var(--t6)}"
    ".as-body h3{margin:0 0 4px;font-size:17px;line-height:1.3}.as-num{display:inline-block;min-width:1.4em;color:var(--muted);font-variant-numeric:tabular-nums}"
    ".as-stats{margin:0;font-size:15px;color:var(--ink);font-variant-numeric:tabular-nums}.as-range,.as-ca{margin:2px 0 0;font-size:14px;color:var(--muted)}"
    ".as .as-more{margin:4px 0 0;padding:0;border:0;background:none;box-shadow:none;font-size:14px;color:var(--muted)}"
    ".as .as-more summary{cursor:pointer;color:var(--teal);font-size:14px;font-weight:600;padding:2px 0;min-height:32px;display:inline-flex;align-items:center;justify-content:flex-start;gap:6px;list-style:none;background:none;border:0}"
    ".as .as-more summary::-webkit-details-marker{display:none}.as .as-more summary::after{content:'+';font-size:16px;font-weight:700;color:var(--teal)}.as .as-more[open] summary::after{content:'\\2212'}"
    ".as .as-more p{margin:6px 0 0;padding:0}"
    ".as-act{grid-column:2}@media(min-width:560px){.as-act{grid-column:3}}"
    ".as-btn{white-space:nowrap;min-height:44px;display:inline-flex;align-items:center}"
    ".as-held{display:inline-block;font-size:14px;font-weight:600;color:var(--muted);padding:10px 0}"
    ".as-item.is-held .as-sw{opacity:.35}.as-note{margin:0 0 14px;color:var(--muted);font-size:14px}"
    ".as-top{margin:0 0 6px}"
)
