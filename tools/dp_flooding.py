#!/usr/bin/env python3
"""Chicago Basement Flooding Calls by Neighborhood: the free page /chicago-basement-flooding/ (site/pages.json kind
"datapage", built by tools/make_site.py through page_html here). Todd's go, Oct 27, 2026 ("Let's do them all",
coo/PARALLEL_BUILDS.md, build B8; research_notes/kimi-2026-10-27-r10.md item 9). Audience: trade owners (plumbers,
waterproofing and restoration companies), Todd, Oct 27, 9:04 am: "trade owners only".

Data: site/datapages/dp_flooding/monthly.json (tools/dp_flooding_data.py, daily GitHub Action): City of Chicago 311
requests of the confirmed types, counted by community area per month and citywide per day. Counts only; no address,
location or resident text exists in the file, so none can reach the page. Population per community area comes from
build B4's site/geo/chicago-community-area-population.json and is used only when that file exists.

Usage: python3 tools/dp_flooding.py --selftest
"""
import csv, datetime as dt, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join("site", "datapages", "dp_flooding", "monthly.json")
POP = os.path.join(ROOT, "site", "geo", "chicago-community-area-population.json")
FEW = 10         # under 10 calls in the earlier 12 months, a percent change is noise: "too few" instead
CSV_AREA = "chicago-basement-flooding-by-area-month.csv"
CSV_DAY = "chicago-basement-flooding-citywide-daily.csv"

META = {"h1": "Chicago Basement Flooding Calls by Neighborhood",
        "card": "Water in basement and sewer cleaning requests to Chicago 311 by community area, month by month, with the busiest days. Updated daily.",
        "keywords": "basement flooding water in basement sewer backup sewer cleaning flood 311 plumber waterproofing restoration storm rain busiest days neighborhood community area chicago"}


def load(p=None):
    f = os.path.join(ROOT, (p or {}).get("data", DATA))
    return json.load(open(f, encoding="utf-8")) if os.path.isfile(f) else None


def load_pop():
    """{area number: residents} from build B4's file, or {} when it is not there. Reads a list of {"n", "population"}
    under "areas", or a plain {number: residents} map."""
    if not os.path.isfile(POP):
        return {}, {}
    try:
        d = json.load(open(POP, encoding="utf-8"))
    except ValueError:
        return {}, {}
    out = {}
    rows = d.get("areas") if isinstance(d, dict) else None
    if isinstance(rows, list):
        for r in rows:
            n = r.get("n") or r.get("number") or r.get("area")
            v = r.get("population") or r.get("pop") or r.get("residents")
            if n and v:
                out[int(n)] = int(v)
    elif isinstance(d, dict):
        for k, v in d.items():
            if str(k).isdigit() and isinstance(v, (int, float)):
                out[int(k)] = int(v)
    ok = len(out) == 77 and all(v > 0 for v in out.values())
    return (out, (d.get("source") or {}) if isinstance(d, dict) else {}) if ok else ({}, {})


def lastmod(p):
    d = load(p)
    return d["through"] if d else None


def ym_name(ym, short=False):
    y, m = map(int, ym.split("-"))
    return dt.date(y, m, 1).strftime("%b %Y" if short else "%B %Y")


def pct(x):
    if x is None:
        return "new"
    return ("+" if x > 0 else "") + f"{x:.0f}%" if abs(x) >= 1 else "same"


def change(now, before):
    return None if not before else (now / before - 1) * 100


def area_change(now, before):
    return "too few" if before < FEW else pct(change(now, before))


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def stats(d, names):
    """Everything the page shows, computed once from the counts."""
    months, through = d["months"], d["through"]
    t = dt.date.fromisoformat(through)
    L = months.index(through[:7]) if (t + dt.timedelta(days=1)).day == 1 else months.index(through[:7]) - 1
    s = d["series"]
    win = lambda arr, end, n: sum(arr[max(0, end - n + 1):end + 1])
    out = {"L": L, "lm": months[L], "partial": L < len(months) - 1, "types": {}}
    for ty in d["types"]:
        k = ty["key"]
        c = s[k]["city"]
        out["types"][k] = {"label": ty["label"], "srType": ty["srType"], "y12": win(c, L, 12), "p12": win(c, L - 12, 12),
                           "m": c[L], "my": c[L - 12] if L >= 12 else None, "mtd": c[-1] if L < len(months) - 1 else None,
                           "noArea12": win(s[k]["noArea"], L, 12)}
        out["types"][k]["ch"] = change(out["types"][k]["y12"], out["types"][k]["p12"])
    areas = []
    for n in range(1, 78):
        a = {"n": n, "name": names.get(n, str(n))}
        for ty in d["types"]:
            k = ty["key"]
            arr = s[k]["area"][str(n)]
            a[k + "12"], a[k + "p12"], a[k + "m"] = win(arr, L, 12), win(arr, L - 12, 12), arr[L]
            a[k + "my"] = arr[L - 12] if L >= 12 else 0
            a[k + "24"] = arr[max(0, L - 23):L + 1]
        areas.append(a)
    for a in areas:
        a["rank"] = 1 + sum(1 for b in areas if b["water12"] > a["water12"])
        a["tied"] = sum(1 for b in areas if b["water12"] == a["water12"]) > 1
    out["areas"] = areas
    d0 = dt.date.fromisoformat(d["dayFrom"])
    day = lambda i: (d0 + dt.timedelta(days=i)).isoformat()
    w, sw = s["water"]["daily"], s["sewer"]["daily"]
    out["days"] = {"water": w[-365:], "sewer": sw[-365:], "from": day(len(w) - min(365, len(w)))}
    top = sorted(range(len(w)), key=lambda i: (-w[i], i))[:10]
    out["topDays"] = [{"day": day(i), "water": w[i], "sewer": sw[i]} for i in sorted(top, key=lambda i: -w[i])]
    yr = list(range(max(0, len(w) - 365), len(w)))
    def spaced(v):     # the 3 busiest days at least 7 days apart, so one storm gets one label
        out_ = []
        for i in sorted(yr, key=lambda i: (-v[i], i)):
            if v[i] and all(abs(i - j) >= 7 for j in out_):
                out_.append(i)
            if len(out_) == 3:
                break
        return [{"day": day(i), "n": v[i], "i": i - yr[0]} for i in out_]
    out["peaks"] = {k: spaced(v) for k, v in (("water", w), ("sewer", sw))}
    out["since"] = d["dayFrom"][:4]
    return out


CSS = ("<style>"
       ".bf-tw{overflow-x:auto;margin:12px 0 0;border:1px solid var(--line);border-radius:12px;background:var(--card)}"
       ".bf-tw:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
       ".bf-t{width:100%;border-collapse:collapse;font-size:14.5px;min-width:640px}.bf-t th,.bf-t td{padding:9px 12px;border-bottom:1px solid var(--rule);text-align:right;font-variant-numeric:tabular-nums}"
       ".bf-t th:first-child,.bf-t td:first-child{text-align:left}.bf-t thead th{font-size:13px;color:var(--muted);font-weight:700;background:var(--card);vertical-align:bottom}"
       ".bf-t tbody th{font-weight:600;color:var(--ink);text-align:left}.bf-t tr:last-child td,.bf-t tr:last-child th{border-bottom:0}.bf-up{color:var(--warn-ink);font-weight:600}"
       ".bf-more{margin:12px 0 0}"
       ".bf-card{margin:12px 0 8px;padding:16px 18px;background:var(--card);border:1px solid var(--line);border-radius:12px}"
       ".bf-seg{display:flex;flex-wrap:wrap;gap:6px;border:0;margin:0 0 12px;padding:0}.bf-seg legend{font-size:13px;font-weight:700;color:var(--muted);margin:0 0 6px;padding:0}"
       ".bf-seg label{position:relative;display:inline-flex;align-items:center;min-height:44px;padding:0 14px;border:1px solid var(--line);border-radius:999px;font-size:14.5px;font-weight:600;color:var(--ink2);cursor:pointer;background:var(--card)}"
       ".bf-seg input{position:absolute;opacity:0;inset:0;margin:0;cursor:pointer}.bf-seg label:has(input:checked){background:var(--ink);border-color:var(--ink);color:var(--card)}"
       ".bf-seg label:has(input:focus-visible){outline:3px solid var(--focus);outline-offset:2px}"
       ".bf-chart{display:block;width:100%;height:auto}.bf-chart .b{fill:var(--accent)}.bf-chart .b2{fill:var(--accent);opacity:.35}.bf-chart .ax{stroke:var(--line);stroke-width:1}"
       ".bf-chart .gl{stroke:var(--rule);stroke-width:1}.bf-chart text{font:600 11px system-ui,sans-serif;fill:var(--muted)}.bf-chart .gt{font-weight:500}.bf-chart .pk{fill:var(--ink);font-weight:700}.bf-chart .pl{stroke:var(--ink);stroke-width:1;stroke-dasharray:2 2}"
       ".bf-cap{margin:8px 0 0;font-size:13.5px;color:var(--muted)}"
       ".bf-key{display:flex;flex-wrap:wrap;gap:14px;margin:6px 0 0;font-size:13.5px;color:var(--ink2)}.bf-key i{display:inline-block;width:14px;height:10px;border-radius:2px;background:var(--accent);margin-right:6px;vertical-align:middle}.bf-key .k2 i{opacity:.35}"
       ".bf-pick{display:grid;gap:6px;max-width:360px;font-size:13px;font-weight:700;color:var(--muted);margin:0 0 12px}"
       ".bf-pick select{min-height:44px;font:inherit;font-size:15px;font-weight:600;color:var(--ink);background:var(--card) var(--sel-arrow) no-repeat right 14px center;border:1px solid var(--line);border-radius:10px;padding:0 38px 0 12px;appearance:none;-webkit-appearance:none}"
       ".bf-pick select:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
       ".bf-area h3{margin:0 0 4px;font-size:20px;color:var(--ink)}.bf-area p{margin:4px 0 0;color:var(--ink2)}"
       ".bf-nums{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:12px 0}@media(min-width:700px){.bf-nums{grid-template-columns:repeat(4,minmax(0,1fr))}}"
       ".bf-nums div{padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--canvas2)}.bf-nums b{display:block;font:700 24px/1.15 Poppins,system-ui,sans-serif;color:var(--ink);font-variant-numeric:tabular-nums}"
       ".bf-nums small{display:block;font-size:13px;color:var(--muted);margin-top:2px}"
       ".bf-days{width:100%;border-collapse:collapse;font-size:14.5px}.bf-days th,.bf-days td{padding:8px 10px;border-bottom:1px solid var(--rule);text-align:right;font-variant-numeric:tabular-nums}"
       ".bf-days th:first-child,.bf-days td:first-child{text-align:left;white-space:nowrap}.bf-days thead th{font-size:13px;color:var(--muted)}.bf-days tr:last-child td{border-bottom:0}"
       ".bf-two{display:grid;gap:16px}@media(min-width:900px){.bf-two{grid-template-columns:1fr 1fr}}.bf-two .cta{grid-template-columns:1fr;height:100%;align-items:start}.bf-two .cta h2{margin-top:0;text-wrap:balance}"
       ".bf-dl{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0 0}"
       ".bf-t td{white-space:nowrap}.bf-t td:last-child,.bf-t th:last-child{padding-right:16px}.bf-t thead th{max-width:9em}"
       ".bf-swipe{display:none;margin:8px 0 0;font-size:13px;color:var(--muted)}"
       "@media(max-width:599px){.bf-t{min-width:600px}.bf-t tbody th{min-width:112px}.bf-t th,.bf-t td{padding:9px 8px}.bf-t tbody th,.bf-t thead th:first-child{position:sticky;left:0;z-index:1;background:var(--card);box-shadow:1px 0 0 var(--rule)}"
       ".bf-tw{background:linear-gradient(to left,var(--card) 0,var(--card) 100%)}.bf-swipe{display:block}.bf-days th,.bf-days td{padding:8px 6px}}"
       "</style>")

SHARED_CSS = ("<style>"
    ".ld-heroact{margin-bottom:24px}.ld-heroact .btn,.ld-heroact .st-btn2,p.rl-act .btn,p.rl-act .st-btn2{min-height:48px;box-sizing:border-box;display:inline-flex;align-items:center;justify-content:center;vertical-align:middle;margin:0}"
    "p.rl-act{display:flex;flex-wrap:wrap;gap:10px;align-items:center}"
    "@media(max-width:599px){.ld-heroact{display:grid;grid-template-columns:1fr;gap:10px}.ld-heroact .btn,.ld-heroact .st-btn2{width:100%}}"
    ".pg-nav{position:sticky;top:0;z-index:20;margin:0 -16px 8px;padding:8px 16px;background:var(--canvas);border-bottom:1px solid var(--rule)}"
    ".pg-nav ul{display:flex;gap:6px;margin:0;padding:0;list-style:none;overflow-x:auto;scrollbar-width:none}.pg-nav ul::-webkit-scrollbar{display:none}"
    ".pg-nav a{display:inline-flex;align-items:center;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid var(--line);background:var(--card);color:var(--ink2);font-size:14px;font-weight:600;text-decoration:none;white-space:nowrap}"
    ".pg-nav a[aria-current=true]{background:var(--ink);border-color:var(--ink);color:var(--card)}.pg-nav a:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
    "section.block{scroll-margin-top:64px}"
    "svg.ch-ph{display:none}@media(max-width:599px){svg.ch-ph{display:block}svg.ch-dt{display:none}}"
    ".ch-ph text{font-size:12px!important}"
    ".up-key{margin:8px 0 0;font-size:13.5px;color:var(--ink2)}.up-key b{color:var(--warn-ink)}"
    "@media (prefers-color-scheme:dark){:root:not([data-theme=light]) .gm.pg-map{--gm0:#5b453d;--gmn:#323a4a;--gmedge:#58627a}}"
    ":root[data-theme=dark] .gm.pg-map{--gm0:#5b453d;--gmn:#323a4a;--gmedge:#58627a}"
    "</style>")

PG_JS = ("<script>(function(){var n=document.querySelector('.pg-nav');if(!n||!('IntersectionObserver' in window))return;var L={};"
         "n.querySelectorAll('a').forEach(function(a){L[a.getAttribute('href').slice(1)]=a;});"
         "var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){n.querySelectorAll('a').forEach(function(a){a.removeAttribute('aria-current');});"
         "var a=L[e.target.id];if(a){a.setAttribute('aria-current','true');a.scrollIntoView({block:'nearest',inline:'nearest'});}}});},{rootMargin:'-30% 0px -60% 0px'});"
         "Object.keys(L).forEach(function(id){var s=document.getElementById(id);if(s)o.observe(s);});})();</script>")


def pg_nav(items, E):
    return ('<nav class="pg-nav" aria-label="On this page"><ul>'
            + "".join(f'<li><a href="#{i}">{E(t)}</a></li>' for i, t in items) + '</ul></nav>')


def pg_map(fig):
    """Mark our maps so the page CSS can lift the lowest color off the dark backdrop (design director, Oct 27)."""
    return fig.replace('<figure class="gm"', '<figure class="gm pg-map"', 1)


CHANGE_BINS = [("d0", "var(--gmd0)", "Down 25% or more", "-25%+"), ("d1", "var(--gmd1)", "Down 5 to 25%", "-5 to 25%"), ("d2", "var(--gmd2)", "Within 5%", "Same"),
               ("d3", "var(--gmd3)", "Up 5 to 25%", "+5 to 25%"), ("d4", "var(--gmd4)", "Up 25% or more", "+25%+"),
               ("nx", "repeating-linear-gradient(45deg,var(--gmn) 0 4px,var(--dash) 4px 5.5px)", "Too few the year before to compare")]


def change_class(now, before):
    if before < FEW:
        return "nx"
    x = (now / before - 1) * 100
    return "d0" if x <= -25 else "d1" if x <= -5 else "d2" if x < 5 else "d3" if x < 25 else "d4"


def range_legend(cuts, fmt=lambda v: f"{v:,}"):
    if not cuts:
        return [("q0", "var(--gm0)", "Any")]
    out = [("q0", "var(--gm0)", f"Under {fmt(cuts[0])}", f"<{fmt(cuts[0])}")]
    for i in range(1, len(cuts)):
        lo, hi = cuts[i - 1], cuts[i] - 1
        out.append((f"q{i}", f"var(--gm{i})", fmt(lo) if lo == hi else f"{fmt(lo)} to {fmt(hi)}", fmt(lo)))
    out.append((f"q{len(cuts)}", f"var(--gm{len(cuts)})", f"{fmt(cuts[-1])} or more", f"{fmt(cuts[-1])}+"))
    return out


def map_block(st, pop, E, period):
    import geo_map as G
    A = st["areas"]
    cw, cs = G.nice_breaks([a["water12"] for a in A]), G.nice_breaks([a["sewer12"] for a in A])
    per = {a["n"]: a["water12"] / pop[a["n"]] * 1000 for a in A} if pop else {}
    areas = {}
    for a in A:
        ch = area_change(a["water12"], a["waterp12"])
        ch_say = "too few the 12 months before to compare" if ch == "too few" else ("about the same as the 12 months before" if ch == "same" else f"{ch} vs the 12 months before")
        big = {"w": (f'{a["water12"]:,}', f"water in basement calls, {period}"), "s": (f'{a["sewer12"]:,}', f"sewer cleaning requests, {period}"),
               "ch": ("Too few" if ch == "too few" else "Same" if ch == "same" else ch, "water in basement calls vs the 12 months before")}
        say = {"w": f'{a["water12"]:,} water in basement calls', "s": f'{a["sewer12"]:,} sewer cleaning requests',
               "ch": ch_say + f' ({a["water12"]:,} vs {a["waterp12"]:,})'}
        if pop:
            big["p"] = (f'{per[a["n"]]:.1f}', "water in basement calls per 1,000 residents")
            say["p"] = f'{per[a["n"]]:.1f} calls per 1,000 residents'
        rk = (f'<p>{"Ties for " if a["tied"] else "Ranks "}{ordinal(a["rank"])} of 77 community areas for water in basement calls, {E(period)}.</p>'
              if a["water12"] else f"<p>No water in basement calls, {E(period)}.</p>")
        areas[a["n"]] = {"big": big, "say": say,
                         "html": rk + '<dl>'
                                 f'<dt>Water in basement</dt><dd>{a["water12"]:,}</dd><dt>12 months before</dt><dd>{a["waterp12"]:,}</dd>'
                                 f'<dt>Sewer cleaning</dt><dd>{a["sewer12"]:,}</dd><dt>12 months before</dt><dd>{a["sewerp12"]:,}</dd></dl>'
                                 f'<p><a href="#area" data-area="{a["n"]}">Month by month for {E(a["name"])}</a></p>'}
    metrics = [{"key": "w", "label": "Water in basement", "legendTitle": f"Water in basement calls, {period}",
                "cls": {a["n"]: f"q{G.klass(a['water12'], cw)}" for a in A}, "legend": range_legend(cw)},
               {"key": "s", "label": "Sewer cleaning", "legendTitle": f"Sewer cleaning requests, {period}",
                "cls": {a["n"]: f"q{G.klass(a['sewer12'], cs)}" for a in A}, "legend": range_legend(cs)}]
    if pop:
        cp = G.nice_breaks([round(v) for v in per.values()])
        metrics.append({"key": "p", "label": "Per 1,000 residents", "legendTitle": f"Water in basement calls per 1,000 residents, {period}",
                        "cls": {n: f"q{G.klass(round(v), cp)}" for n, v in per.items()}, "legend": range_legend(cp)})
    metrics.append({"key": "ch", "label": "Change vs the 12 months before", "legendTitle": "Water in basement calls vs the 12 months before",
                    "cls": {a["n"]: change_class(a["water12"], a["waterp12"]) for a in A}, "legend": CHANGE_BINS})
    w = st["types"]["water"]
    top3 = sorted(A, key=lambda a: (-a["water12"], a["name"]))[:3]
    rises = sorted([a for a in A if a["waterp12"] >= FEW and a["water12"] > a["waterp12"]], key=lambda a: (-(a["water12"] - a["waterp12"]), a["name"]))[:4]
    hint = ('<h3>Citywide</h3>'
            f'<p class="gm-big"><span>{w["y12"]:,}</span><small>water in basement calls, {E(period)}, {E(pct(w["ch"]))} vs the 12 months before</small></p>'
            '<p>Most calls:</p><ul class="gm-top">'
            + "".join(f'<li><button type="button" data-pick="{a["n"]}">{E(a["name"])}, {a["water12"]:,}</button></li>' for a in top3) + '</ul>'
            + ('<p>Biggest rises:</p><ul class="gm-top">' + "".join(f'<li><button type="button" data-pick="{a["n"]}">{E(a["name"])}, +{a["water12"] - a["waterp12"]:,} calls</button></li>' for a in rises) + '</ul>' if rises else "")
            + '<p class="gm-hint">Tap or hover any area on the map, or choose one from the list.</p>')
    fig = G.choropleth(areas, metrics, uid="floodmap", title="Map of Chicago's 77 community areas, colored by basement flooding calls to 311", hint=hint,
                       caption="Community area outlines: City of Chicago, Boundaries - Community Areas. Every number on the map is also in the table below.")
    return G.CSS + pg_map(fig) if fig else ""


def nice_step(mx, lines=4):
    """A round gridline step (1, 2 or 5 times a power of ten) giving about `lines` lines up to mx."""
    import math
    raw = max(mx, 1) / lines
    p = 10 ** math.floor(math.log10(raw))
    return next(m * p for m in (1, 2, 5, 10) if m * p >= raw)


def short_num(v):
    return f"{v / 1000:g}k" if v >= 1000 else f"{v:,}"


def short_ym(label):
    """ "Mar 2026" -> "Mar \u201926" for the phone charts, where four-digit years collide."""
    return label[:-4] + "\u2019" + label[-2:] if label[-4:].isdigit() else label


def grid(mx, base, top, x0, W, E):
    st = nice_step(mx)
    out, v = "", st
    while v <= mx:
        y = base - v / mx * (base - top)
        out += (f'<line class="gl" x1="{x0}" y1="{y:.1f}" x2="{W}" y2="{y:.1f}"/>'
                f'<text class="gt" x="{x0 - 6}" y="{y + 4:.1f}" text-anchor="end">{short_num(v)}</text>')
        v += st
    return out


def peak_rows(peaks, xs, gap=118):
    """Rows for the peak labels so no two labels on one row sit closer than `gap` units."""
    rows = []
    for p, x in zip(peaks, xs):
        r = 0
        while any(abs(x - x2) < gap for x2, r2 in rows if r2 == r):
            r += 1
        rows.append((x, r))
    return [r for _, r in rows]


def day_chart(vals, start, peaks, E, label, cls="b", ph=False):
    """One bar per day for the last 365 days, the 3 busiest days labeled. Inline SVG, readable with scripts off.
    ph: the phone drawing (330 units wide, so its 12 px labels render at about 12 px on a 390 px screen)."""
    n = len(vals)
    W, H, top, base, x0 = (330, 230, 58, 200, 34) if ph else (730, 250, 58, 222, 44)
    bw = (W - x0) / max(n, 1)
    mx = max(vals) or 1
    d0 = dt.date.fromisoformat(start)
    bars = "".join(f'<rect class="{cls}" x="{x0 + i * bw:.2f}" y="{base - v / mx * (base - top):.1f}" width="{max(bw - (.1 if ph else .3), .4):.2f}" height="{v / mx * (base - top):.1f}"/>'
                   for i, v in enumerate(vals) if v)
    ticks = ""
    every = 3 if ph else 2
    for i in range(n):
        day = d0 + dt.timedelta(days=i)
        if day.day == 1:
            x = x0 + i * bw
            ticks += f'<line class="ax" x1="{x:.1f}" y1="{base}" x2="{x:.1f}" y2="{base + 5}"/>'
            if day.month % every == 1 % every and x < W - 30:
                ticks += f'<text x="{x + 2:.1f}" y="{base + 19}">{E(day.strftime("%b"))}</text>'
    peaks = peaks[:2] if ph else peaks
    xs = [x0 + (p["i"] + .5) * bw for p in peaks]
    rows = peak_rows(peaks, xs, gap=100 if ph else 118)
    pk = ""
    for p, x, r in zip(peaks, xs, rows):
        y = base - p["n"] / mx * (base - top)
        ty = 14 + 18 * r
        edge = 60 if ph else 70
        anchor = "end" if x > W - edge else "start" if x < x0 + edge else "middle"
        pk += (f'<line class="pl" x1="{x:.1f}" y1="{ty + 4}" x2="{x:.1f}" y2="{y - 2:.1f}"/>'
               f'<text class="pk" x="{x:.1f}" y="{ty}" text-anchor="{anchor}">{E(nice_short(p["day"]))}: {p["n"]:,}</text>')
    return (f'<svg class="bf-chart {"ch-ph" if ph else "ch-dt"}" viewBox="0 0 {W} {H}" role="img" aria-label="{E(label)}" xmlns="http://www.w3.org/2000/svg">'
            f'{grid(mx, base, top, x0, W, E)}<line class="ax" x1="{x0}" y1="{base}" x2="{W}" y2="{base}"/>{bars}{ticks}{pk}</svg>')


def nice_short(day):
    d = dt.date.fromisoformat(day)
    return d.strftime("%b ") + str(d.day)


def month_chart(vals, labels, ghost, E, label, ph=None):
    """Bars for the last 24 complete months, with the same month a year earlier as a pale bar behind each one.
    Returns the desktop and the phone drawing together (CSS shows one); ph=True or False returns just one."""
    if ph is None:
        return month_chart(vals, labels, ghost, E, label, False) + month_chart(vals, labels, ghost, E, label, True)
    n = len(vals)
    W, H, top, base, x0 = (330, 214, 14, 184, 34) if ph else (730, 224, 14, 194, 44)
    slot = (W - x0) / n
    mx = max(vals + [g for g in ghost if g is not None]) or 1
    step = 6 if ph else 3
    out = ""
    for i, v in enumerate(vals):
        x = x0 + i * slot
        g = ghost[i]
        if g:
            out += f'<rect class="b2" x="{x + slot * .1:.1f}" y="{base - g / mx * (base - top):.1f}" width="{slot * .8:.1f}" height="{g / mx * (base - top):.1f}"/>'
        out += f'<rect class="b" x="{x + slot * .28:.1f}" y="{base - v / mx * (base - top):.1f}" width="{slot * .44:.1f}" height="{v / mx * (base - top):.1f}"/>'
        if (n - 1 - i) % step == 0:      # counted back from the last month, so the gaps are even and the newest month is always named
            a = "end" if i == n - 1 else "middle"
            tx = x + slot if i == n - 1 else x + slot / 2
            out += f'<text x="{tx:.1f}" y="{base + 19}" text-anchor="{a}">{E(short_ym(labels[i]) if ph else labels[i])}</text>'
    return (f'<svg class="bf-chart {"ch-ph" if ph else "ch-dt"}" viewBox="0 0 {W} {H}" role="img" aria-label="{E(label)}" xmlns="http://www.w3.org/2000/svg">'
            f'{grid(mx, base, top, x0, W, E)}<line class="ax" x1="{x0}" y1="{base}" x2="{W}" y2="{base}"/>{out}</svg>')


JS = r"""<script>(function(){var D=JSON.parse(document.getElementById("bf-data").textContent);
document.querySelectorAll("[data-bf-show]").forEach(function(i){i.addEventListener("change",function(){var g=i.name;document.querySelectorAll("[data-bf-group='"+g+"']").forEach(function(el){el.hidden=el.dataset.bfKey!==i.value;});});});
var sel=document.getElementById("bf-area-sel"),box=document.getElementById("bf-area-box");
function step(mx){var r=Math.max(mx,1)/4,p=Math.pow(10,Math.floor(Math.log10(r)));return [1,2,5,10].map(function(m){return m*p;}).filter(function(x){return x>=r;})[0];}
function sn(v){return v>=1000?(v/1000)+"k":v.toLocaleString("en-US");}function sy(l){return /\d{4}$/.test(l)?l.slice(0,-4)+"\u2019"+l.slice(-2):l;}
function bars(v,mx){var ph=window.matchMedia("(max-width:599px)").matches,W=ph?330:730,H=164,b=136,t=16,x0=ph?34:44,s=(W-x0)/v.length,o="",st=step(mx),k=ph?6:3;
for(var g=st;g<=mx;g+=st){var gy=b-g/mx*(b-t);o+='<line class="gl" x1="'+x0+'" y1="'+gy.toFixed(1)+'" x2="'+W+'" y2="'+gy.toFixed(1)+'"/><text class="gt" x="'+(x0-6)+'" y="'+(gy+4).toFixed(1)+'" text-anchor="end">'+sn(g)+'</text>';}
for(var i=0;i<v.length;i++){var h=v[i]/mx*(b-t),x=x0+i*s;o+='<rect class="b" x="'+(x+s*.2).toFixed(1)+'" y="'+(b-h).toFixed(1)+'" width="'+(s*.6).toFixed(1)+'" height="'+h.toFixed(1)+'"/>';
if((v.length-1-i)%k===0){var last=i===v.length-1;o+='<text x="'+(last?x+s:x+s/2).toFixed(1)+'" y="'+(b+18)+'" text-anchor="'+(last?"end":"middle")+'">'+(ph?sy(D.labels[i]):D.labels[i])+'</text>';}}
return '<svg class="bf-chart'+(ph?' ch-ph':'')+'" style="display:block" viewBox="0 0 '+W+' '+H+'" aria-hidden="true"><line class="ax" x1="'+x0+'" y1="'+b+'" x2="'+W+'" y2="'+b+'"/>'+o+'</svg>';}
function show(n){var a=D.areas[n];if(!a)return;var mx=Math.max.apply(null,a.w.concat(a.s,[1]));
box.innerHTML='<h3>'+a.name+'</h3><p>'+a.rank+'</p><div class="bf-nums"><div><b>'+a.w12+'</b><small>water in basement calls, '+D.period+'</small></div><div><b>'+a.wch+'</b><small>vs the 12 months before</small></div><div><b>'+a.s12+'</b><small>sewer cleaning requests, '+D.period+'</small></div><div><b>'+a.sch+'</b><small>vs the 12 months before</small></div></div>'
+'<p><b>Water in basement calls each month</b></p>'+bars(a.w,mx)+'<p><b>Sewer cleaning requests each month</b></p>'+bars(a.s,mx)+'<p class="bf-cap">'+D.cap+'</p>';}
if(sel){sel.addEventListener("change",function(){show(sel.value);});show(sel.value);var lw=innerWidth<600;addEventListener("resize",function(){if((innerWidth<600)!==lw){lw=innerWidth<600;show(sel.value);}});}
document.addEventListener("click",function(e){var t=e.target.closest("[data-area]");if(!t||!sel)return;sel.value=t.dataset.area;show(t.dataset.area);});
})();</script>"""


def csv_area(d, names):
    f = io.StringIO()
    w = csv.writer(f, lineterminator="\n")
    keys = [t["key"] for t in d["types"]]
    w.writerow(["community_area_number", "community_area", "month"] + [t["srType"] for t in d["types"]])
    for n in range(1, 78):
        for i, ym in enumerate(d["months"]):
            w.writerow([n, names.get(n, n), ym] + [d["series"][k]["area"][str(n)][i] for k in keys])
    for i, ym in enumerate(d["months"]):
        w.writerow(["", "No community area on the record", ym] + [d["series"][k]["noArea"][i] for k in keys])
    return f.getvalue()


def csv_day(d):
    f = io.StringIO()
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["date"] + [t["srType"] for t in d["types"]])
    d0 = dt.date.fromisoformat(d["dayFrom"])
    for i in range(len(d["series"]["water"]["daily"])):
        w.writerow([(d0 + dt.timedelta(days=i)).isoformat()] + [d["series"][t["key"]]["daily"][i] for t in d["types"]])
    return f.getvalue()


def area_names():
    import geo_map as G
    g = G.load()
    if g:
        return {a["n"]: a["name"] for a in g["areas"]}
    import rodents_chicago as R
    return dict(R.AREAS)


def extra_pages(p):
    d = load(p)
    if not d:
        return []
    names = area_names()
    return [(CSV_AREA, csv_area(d, names)), (CSV_DAY, csv_day(d))]


def page_html(p):
    import make_site as M
    E = M.E
    url, rel = M.BASE + p["slug"] + "/", "../"
    d = load(p)
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), ("Free Chicago data", "chicago-data/"), (META["h1"], None)])
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}
    head = lambda rb, ld: M.HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=M.SHOP, ld=ld + CSS + SHARED_CSS,
                                        bodycls=' class="ld-page"', robots=rb, analytics=M.analytics_tag())
    if not d:
        return (head('<meta name="robots" content="noindex, nofollow">', "") + f'{crumb}<div class="ld-hero"><h1>{E(META["h1"])}</h1>'
                '<p class="lede">The first count is on its way.</p></div></main></body></html>')
    names = area_names()
    pop, pop_src = load_pop()
    st = stats(d, names)
    src = d["source"]
    pulled = M.nice_date(src["fetchedAt"][:10])
    w, s = st["types"]["water"], st["types"]["sewer"]
    first_m = d["months"][st["L"] - 11]
    period = f'{ym_name(first_m, True)} to {ym_name(st["lm"], True)}'
    yr_before = f'{ym_name(d["months"][st["L"] - 23], True)} to {ym_name(d["months"][st["L"] - 12], True)}'
    A = st["areas"]
    top = sorted(A, key=lambda a: (-a["water12"], a["name"]))
    lead = top[0]
    tie = top[1]["water12"] == lead["water12"]
    say = lambda x: "about the same as" if x is None or abs(x) < 1 else f'{abs(x):.0f}% {"more" if x > 0 else "fewer"} than'
    td = st["topDays"][0] if st["topDays"] and st["topDays"][0]["water"] else None
    in_prev = bool(td and d["months"][st["L"] - 23] <= td["day"][:7] <= d["months"][st["L"] - 12])
    lede = (f'Chicago 311 took {w["y12"]:,} water in basement calls and {s["y12"]:,} sewer cleaning requests in the 12 months from '
            f'{E(ym_name(first_m))} to {E(ym_name(st["lm"]))}. That is {say(w["ch"])} the 12 months before'
            + (f', which held the busiest day since {E(st["since"])}: {E(M.nice_date(td["day"]))}, with {td["water"]:,} water in basement calls.' if in_prev else
               '.' + (f' The busiest day since {E(st["since"])} was {E(M.nice_date(td["day"]))}, with {td["water"]:,} water in basement calls.' if td else "")))
    peak = st["peaks"]["water"][0] if st["peaks"]["water"] else None
    tiles = ('<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">Basement calls</div><div class="val">{w["y12"]:,}</div><div class="sub">water in basement calls, last 12 months, {E(pct(w["ch"]))} vs the 12 months before</div></div>'
             f'<div class="tile"><div class="lab">Sewer requests</div><div class="val">{s["y12"]:,}</div><div class="sub">sewer cleaning requests, last 12 months, {E(pct(s["ch"]))} vs the 12 months before</div></div>'
             f'<div class="tile"><div class="lab">{E(ym_name(st["lm"], True))}</div><div class="val">{w["m"]:,}</div><div class="sub">water in basement calls; {w["my"] or 0:,} in {E(ym_name(d["months"][st["L"] - 12], True))}</div></div>'
             + (f'<div class="tile"><div class="lab">Year\u2019s busiest day</div><div class="val">{peak["n"]:,}</div><div class="sub">water in basement calls on {E(M.nice_date(peak["day"]))}, the most in the last 365 days</div></div>' if peak else "")
             + f'</div><p class="asof">Counts to {E(M.nice_date(d["through"]))}, from City of Chicago 311 records pulled {E(pulled)}. Updated every day.</p>')
    mapb = map_block(st, pop, E, period) if p.get("map", True) else ""
    # citywide charts with one toggle for the type
    mlab = [ym_name(m, True) for m in d["months"][max(0, st["L"] - 23):st["L"] + 1]]
    charts = ""
    for k, ty in (("water", w), ("sewer", s)):
        c = d["series"][k]["city"]
        vals = c[max(0, st["L"] - 23):st["L"] + 1]
        ghost = [c[i - 12] if i >= 12 else None for i in range(max(0, st["L"] - 23), st["L"] + 1)]
        peaks = st["peaks"][k]
        nm = ty["label"].lower()
        noun = "calls" if k == "water" else "requests"
        charts += (f'<div data-bf-group="bfc" data-bf-key="{k}"{" hidden" if k != "water" else ""}>'
                   f'<div class="bf-card"><p><b>{E(ty["label"])} {noun} each day, the last 365 days</b></p>'
                   + "".join(day_chart(st["days"][k], st["days"]["from"], peaks, E, f"{ty['label']} {noun} to 311 each day for the last 365 days; the busiest days at least a week apart are labeled", ph=ph) for ph in (False, True))
                   + f'<p class="bf-cap">One bar per day, to {E(M.nice_date(d["through"]))}. The three busiest days at least a week apart are labeled.</p></div>'
                   f'<div class="bf-card"><p><b>{E(ty["label"])} {noun} each month</b></p>'
                   + month_chart(vals, mlab, ghost, E, f"{ty['label']} {noun} each month for 24 months, with the same month a year earlier behind each bar")
                   + '<p class="bf-key"><span><i></i>That month</span><span class="k2"><i></i>Same month a year earlier</span></p></div></div>')
    toggle = ('<fieldset class="bf-seg"><legend>Show</legend>'
              '<label><input type="radio" name="bfc" value="water" data-bf-show checked>Water in basement</label>'
              '<label><input type="radio" name="bfc" value="sewer" data-bf-show>Sewer cleaning</label></fieldset>')
    days_rows = "".join(f'<tr><td>{E(M.nice_date(x["day"]))}</td><td>{x["water"]:,}</td><td>{x["sewer"]:,}</td></tr>' for x in st["topDays"])
    days_tbl = (f'<div class="bf-card"><p><b>The 10 busiest days for water in basement calls since {E(st["since"])}</b></p>'
                '<div class="bf-tw" role="region" aria-label="Busiest days for water in basement calls" tabindex="0" style="border:0;margin:0"><table class="bf-days">'
                '<thead><tr><th scope="col">Day</th><th scope="col">Water in basement</th><th scope="col">Sewer cleaning</th></tr></thead>'
                f'<tbody>{days_rows}</tbody></table></div>'
                '<p class="bf-cap">These are the days with the most calls in the City\'s records. This page holds no rainfall data; the National Weather Service keeps daily rain totals for Chicago.</p></div>')
    # one community area, month by month
    def ch_txt(now, before):
        c = area_change(now, before)
        return "Too few" if c == "too few" else "Same" if c == "same" else c
    adata = {"period": E(period), "labels": [E(x) for x in mlab],
             "cap": E(f"Each bar is one month, {mlab[0]} to {mlab[-1]}. Both charts use the same scale."),
             "areas": {str(a["n"]): {"name": E(a["name"]), "w": a["water24"], "s": a["sewer24"], "w12": f'{a["water12"]:,}', "s12": f'{a["sewer12"]:,}',
                                     "wch": E(ch_txt(a["water12"], a["waterp12"])), "sch": E(ch_txt(a["sewer12"], a["sewerp12"])),
                                     "rank": E(f'{"Ties for " if a["tied"] else "Ranks "}{ordinal(a["rank"])} of 77 community areas for water in basement calls, {period}.'
                                               if a["water12"] else f"No water in basement calls, {period}.")} for a in A}}
    opts = "".join(f'<option value="{a["n"]}"{" selected" if a["n"] == lead["n"] else ""}>{E(a["name"])}</option>' for a in sorted(A, key=lambda a: a["name"]))
    la = adata["areas"][str(lead["n"])]
    area_sec = (f'<div class="bf-card"><label class="bf-pick" for="bf-area-sel">Choose a community area<select id="bf-area-sel">{opts}</select></label>'
                f'<div class="bf-area" id="bf-area-box" aria-live="polite"><h3>{la["name"]}</h3><p>{la["rank"]}</p>'
                f'<div class="bf-nums"><div><b>{la["w12"]}</b><small>water in basement calls, {E(period)}</small></div><div><b>{la["wch"]}</b><small>vs the 12 months before</small></div>'
                f'<div><b>{la["s12"]}</b><small>sewer cleaning requests, {E(period)}</small></div><div><b>{la["sch"]}</b><small>vs the 12 months before</small></div></div>'
                f'<p class="bf-cap">Every count for every month is also in the download below.</p></div></div>')
    js_data = json.dumps(adata, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    # the 77 areas table
    has_pop = bool(pop)
    row = lambda a: (f'<tr><th scope="row">{E(a["name"])}</th><td>{"=" if a["tied"] else ""}{a["rank"]}</td><td>{a["water12"]:,}</td>'
                     + (f'<td class="bf-up">\u2191 {E(area_change(a["water12"], a["waterp12"]))}</td>' if a["waterp12"] >= FEW and a["water12"] >= a["waterp12"] * 1.25 else f'<td>{E(area_change(a["water12"], a["waterp12"]))}</td>')
                     + (f'<td class="bf-x">{a["water12"] / pop[a["n"]] * 1000:.1f}</td>' if has_pop else "")
                     + f'<td>{a["sewer12"]:,}</td><td class="bf-x">{E(area_change(a["sewer12"], a["sewerp12"]))}</td><td class="bf-x">{a["waterm"]:,}</td></tr>')
    thead = ('<thead><tr><th scope="col">Community area</th><th scope="col">Rank</th><th scope="col">Water in basement, 12 months</th><th scope="col">Basement change</th>'
             + ('<th scope="col" class="bf-x">Basement calls per 1,000 residents</th>' if has_pop else "")
             + f'<th scope="col">Sewer cleaning, 12 months</th><th scope="col" class="bf-x">Sewer change</th><th scope="col" class="bf-x">{E(ym_name(st["lm"], True))}</th></tr></thead>')
    tbl = lambda rs, lab: f'<div class="bf-tw" role="region" aria-label="{E(lab)}" tabindex="0"><table class="bf-t">{thead}<tbody>{"".join(row(a) for a in rs)}</tbody></table></div>'
    SHOW = 20
    table = (f'<p class="up-key"><b>\u2191 Red</b> marks a rise of 25% or more vs the 12 months before, where those months had at least {FEW} calls.</p>'
             '<p class="bf-swipe">Swipe the table sideways for more columns.</p>'
             + tbl(top[:SHOW], "Basement flooding calls, the 20 community areas with the most")
             + f'<details class="bf-more"><summary>Show the other {len(top) - SHOW} community areas</summary>' + tbl(top[SHOW:], "Basement flooding calls, the other community areas") + '</details>'
             + f'<p class="asof">12 months is {E(period)}; change compares it with {E(yr_before)}, rounded to a whole percent. Within 1% shows as same, and under {FEW} calls in the earlier 12 months as too few. '
             f'Rank is by water in basement calls; = marks a tie. The {E(ym_name(st["lm"], True))} column is water in basement calls that month.'
             + (f' {w["noArea12"]:,} water in basement calls and {s["noArea12"]:,} sewer cleaning requests in those 12 months had no community area on the record and count only in the city totals.' if w["noArea12"] or s["noArea12"] else "")
             + (f' Per 1,000 residents uses the City\'s {E(pop_src.get("name", "population figures"))}' + (f' ({E(str(pop_src["acsYear"]))} estimates)' if pop_src.get("acsYear") else "") + '.' if has_pop else "")
             + '</p>'
             f'<div class="bf-dl"><a class="st-btn2" href="{CSV_AREA}" download>Download every area by month (CSV)</a>'
             f'<a class="st-btn2" href="{CSV_DAY}" download>Download citywide by day (CSV)</a></div>')
    tr = p["trade"]
    two = ('<section class="block" id="next"><div class="bf-two">'
           + "".join(f'<div class="cta ld-cta"><div><h2>{E(c["title"])}</h2><p>{E(c["text"])}</p>'
                     f'<p class="ld-buybtn"><a class="btn" href="{rel}{E(c["slug"])}/">{E(c["button"])}</a></p></div></div>' for c in tr)
           + '</div></section>')
    method = '<section class="block" id="how"><h2>How this page is made</h2>' + "".join(f"<p>{E(x)}</p>" for x in p["method"]) + "</section>"
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(META["h1"])}</h1><p class="lede">{lede}</p>'
            '<div class="ld-heroact rl-act"><a class="btn" href="#areas">See every neighborhood</a>'
            + ('<a class="st-btn2" href="#map">Open the map</a>' if mapb else "") + '</div></div>'
            f'{tiles}'
            + pg_nav([("map", "Map"), ("days", "Busy days"), ("area", "One area"), ("areas", "Every area"), ("faq", "Questions")] if mapb else
                     [("days", "Busy days"), ("area", "One area"), ("areas", "Every area"), ("faq", "Questions")], E)
            + (f'<section class="block" id="map"><h2>Basement flooding calls on the map</h2>{mapb}</section>' if mapb else "")
            + f'<section class="block" id="days"><h2>The busiest days and months</h2>{toggle}{charts}{days_tbl}</section>'
            f'<section class="block" id="area"><h2>One community area, month by month</h2>{area_sec}</section>'
            f'<section class="block" id="areas"><h2>Every community area</h2>{table}</section>'
            + two + method + M.faq_block(p["faq"]).replace('<section class="block">', '<section class="block" id="faq">', 1) +
            f'<p class="rl-act"><a class="btn" href="#areas">See every neighborhood</a> <a class="st-btn2" href="{rel}chicago-data/">More free Chicago data</a></p>'
            f'<script type="application/json" id="bf-data">{js_data}</script>{JS}{PG_JS}')
    types = " and ".join(E(t["srType"]) for t in d["types"])
    foot = (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            f'<p>Source: City of Chicago Data Portal, <a href="{E(src["url"])}">311 Service Requests dataset</a>, requests of type {types}, pulled {E(pulled)}'
            + (", with requests the City marked as duplicates left out" if src.get("duplicatesLeftOut") else "")
            + '. A call is one request to 311; it does not say what the City found, and a count says nothing about any one building or block.</p>'
            + (f'<p>Residents per community area: {E(pop_src.get("publisher", "City of Chicago"))}, <a href="{E(pop_src.get("url", ""))}">{E(pop_src.get("name", ""))}</a>'
               f'{" (U.S. Census Bureau American Community Survey 5-year estimates, " + E(str(pop_src["acsYear"])) + ")" if pop_src.get("acsYear") else ""}; '
               'per 1,000 residents is calls divided by residents, times 1,000.</p>' if has_pop else "")
            + '<p>What each request type is for: Department of Water Management, '
            '<a href="https://chicago.gov/city/en/depts/water/provdrs/ops/svcs/waterbasement.html">Water in Basement</a> and '
            '<a href="https://www.chicago.gov/city/en/depts/water/provdrs/engineer/svcs/request_sewer_cleaninginspection.html">Sewer Cleaning Inspection</a> pages, read Oct 27, 2026.</p>'
            + f'<p>{E(M.CITY_DISCLAIMER["Chicago"])}</p><p>ProofNotFluff is not affiliated with or endorsed by the City of Chicago.</p>'
            '<p>Public information, not legal, insurance or plumbing advice for any property. For a problem at a property, check with the City or a licensed plumber.</p>'
            '<p>Made by ProofNotFluff with AI assistance from public City data. The page counts visits with Cloudflare Web Analytics, which sets no cookies.</p></div></footer>\n</body></html>')
    data_ld = {"@context": "https://schema.org", "@type": "Dataset", "name": META["h1"], "description": p["desc"], "url": url,
               "isAccessibleForFree": True, "license": "https://www.chicago.gov/city/en/narr/foia/data_disclaimer.html",
               "creator": {"@type": "Organization", "name": "ProofNotFluff"}, "isBasedOn": src["url"],
               "temporalCoverage": f'{d["dayFrom"]}/{d["through"]}', "spatialCoverage": "Chicago, Illinois",
               "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": url + CSV_AREA},
                                {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": url + CSV_DAY}]}
    return head(robots, M.ld_tags(crumb_ld, faq_ld, data_ld)) + body + foot


def selftest():
    sys.path.insert(0, HERE)
    import make_site as M
    import dp_flooding_data as F
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("slug") == "chicago-basement-flooding"][0]
    months = F.month_list("2024-09", "2026-10")
    per = {"water": {}, "sewer": {}}
    for i, ym in enumerate(months):
        last = 26 if ym == "2026-10" else 28
        per["water"][ym] = ({6: 10 + i, 70: 40 if ym >= "2025-10" else 20, 0: 1}, {f"{ym}-0{1 + j}": (60 if ym == "2026-07" and j == 3 else 2) for j in range(5)})
        per["sewer"][ym] = ({6: 5, 70: 3}, {f"{ym}-01": 8})
        del last
    d = F.assemble(per, months, "2026-10-26", "2026-10-27T06:00:00-0500", True)
    import tempfile
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, dir=ROOT)
    json.dump(d, tmp); tmp.close()
    try:
        q = dict(spec, data=os.path.relpath(tmp.name, ROOT))
        names = area_names()
        st = stats(d, names)
        assert st["lm"] == "2026-09" and st["partial"], "Sep is the last complete month when data runs to Oct 26"
        ash = next(a for a in st["areas"] if a["n"] == 70)
        assert ash["water12"] == 480 and ash["waterp12"] == 240 and ash["rank"] == 1, ash
        lv = next(a for a in st["areas"] if a["n"] == 6)
        assert lv["water12"] == sum(10 + i for i in range(13, 25)), lv["water12"]
        assert st["types"]["water"]["y12"] == 480 + lv["water12"] + 12, st["types"]["water"]
        assert st["topDays"][0] == {"day": "2026-07-04", "water": 60, "sewer": 0}, st["topDays"][0]
        html = page_html(q)
        ex = dict(extra_pages(q))
    finally:
        os.unlink(tmp.name)
    assert html.count("<h1>") == 1 and "—" not in html and "–" not in html, "one h1, no dashes"
    assert "Oct 2025 to Sep 2026" in html and "+100%" in html, "period and change"
    assert "Jul 4, 2026" in html and "Ashburn" in html, "storm day and the top area"
    assert M.E(M.CITY_DISCLAIMER["Chicago"]) in html and 'tabindex="0"' in html
    assert CSV_AREA in ex and ex[CSV_AREA].count("\n") == 1 + 78 * len(months), "77 areas and the no-area line per month"
    assert ex[CSV_DAY].splitlines()[0].startswith("date,Water in Basement Complaint"), "CSV header names the City's request types"
    assert "address" not in ex[CSV_AREA].lower() and "latitude" not in html.lower()
    assert change_class(5, 9) == "nx" and change_class(130, 100) == "d4" and area_change(100, 100) == "same"
    shell = page_html(dict(spec, data="site/datapages/dp_flooding/none.json"))
    assert "noindex" in shell
    print("dp_flooding selftest: ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
