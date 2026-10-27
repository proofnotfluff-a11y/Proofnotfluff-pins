#!/usr/bin/env python3
"""Chicago Permit Wait Times: the free weekly page /chicago-permit-wait-times/ (site/pages.json kind "datapage", module
dp_permit_wait; tools/make_site.py calls page_html, lastmod and extra_pages here). Todd's go, Oct 27, 2026, 12:17 pm:
"Let's do them all" (coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md, research_notes/kimi-2026-10-27-r10.md item 2).

Data: site/datapages/dp_permit_wait/stats.json, written weekly in GitHub Actions by tools/dp_permit_wait_data.py from the
City's Building Permits dataset (ydr8-5enu). Day figures and counts only; no permit number, address, contact or
description exists in the file, so none can reach the page. The measure is the City's own processing_time field (days
from application_start_date to issue_date), for issued permits only.

Sub-pages: one per permit type with at least the data file's pageFloor issued permits in the last 12 months, and a CSV of
every figure on the pages (extra_pages).

The small chart and table helpers here are also used by tools/dp_demo_baiting.py (the same build).

Usage: python3 tools/dp_permit_wait.py --selftest
"""
import csv, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = "site/datapages/dp_permit_wait/stats.json"
CSV_NAME = "chicago-permit-wait-times.csv"
DOB_PERMITS = "https://chicago.gov/city/en/sites/guide-to-building-permits/home/instructions.html"   # read Oct 27, 2026

META = {"h1": "Chicago Permit Wait Times",
        "card": "Days from review to issue, by permit type, review path and neighborhood",
        "keywords": "permit wait times processing days building permits standard plan review express permit self certification "
                    "department of buildings how long does a permit take chicago"}

FAQ = [
    ("How long does a building permit take in Chicago?",
     "It depends most on the review path. The tables on this page show, for permits the City issued in the last 12 months, how many days "
     "half of them took and how many days 8 in 10 took, by permit type and review path. For your own permit, check with the Department of Buildings."),
    ("Where do these numbers come from?",
     "From the City of Chicago's Building Permits dataset. Each issued permit carries a processing time field, the number of days between "
     "the day the City began reviewing the application and the issue date. We count those days; we do not estimate them."),
    ("Why can a permit show zero days?",
     "Many Express Permit Program permits are issued the same day the City starts reviewing them, so their processing time is 0. The page "
     "shows the share issued the same day for each review path."),
    ("Does this include permits still waiting for review?",
     "No. Only issued permits have an issue date, so an application still in review is not counted until it is issued. When a review path "
     "slows down, its figures here catch up as those permits are issued."),
    ("How often is the page updated?",
     "Once a week, on Monday mornings, from the City's records up to the day before the update. The City updates the dataset daily."),
]


def load(p=None):
    f = os.path.join(ROOT, (p or {}).get("data", DATA))
    return json.load(open(f, encoding="utf-8")) if os.path.isfile(f) else None


def lastmod(p):
    d = load(p)
    return (d or {}).get("source", {}).get("fetchedAt", "")[:10] or None


# ---------------------------------------------------------------- shared look (both pages of this build)
CSS = ("<style>"
       ".pw-tw{overflow-x:auto;margin:12px 0 0;border:1px solid var(--line);border-radius:12px;background:var(--card)}"
       ".pw-tw:focus-visible{outline:3px solid var(--accent);outline-offset:2px}"
       ".pw-t{width:100%;border-collapse:collapse;font-size:14.5px}.pw-t th,.pw-t td{padding:10px 12px;border-bottom:1px solid var(--rule);text-align:right;font-variant-numeric:tabular-nums;vertical-align:baseline}"
       ".pw-t th:first-child,.pw-t td:first-child{text-align:left}.pw-t thead th{font-size:12.5px;line-height:1.3;color:var(--muted);font-weight:700;background:var(--card);position:sticky;top:0}"
       ".pw-t tbody th{font-weight:600;color:var(--ink)}.pw-t tbody th a{color:var(--teal);font-weight:700}.pw-t tr:last-child td,.pw-t tr:last-child th{border-bottom:0}"
       ".pw-t .pw-na{color:var(--muted);font-size:13px}.pw-t small{display:block;font-weight:400;color:var(--muted);font-size:12.5px}"
       ".pw-more{margin:12px 0 0}.pw-more summary{display:flex;align-items:center;min-height:44px;padding:0 16px;border:1px solid var(--line);border-radius:12px;background:var(--card);cursor:pointer;font-weight:600;color:var(--ink)}"
       ".pw-more[open] summary{margin-bottom:8px}"
       ".pw-ch{margin:12px 0 4px;padding:16px 18px 12px;background:var(--card);border:1px solid var(--line);border-radius:12px}"
       ".pw-ch figcaption{font-weight:700;color:var(--ink);margin:0 0 4px}"
       ".pw-key{display:flex;flex-wrap:wrap;gap:6px 18px;margin:0 0 8px;font-size:13px;color:var(--ink2)}.pw-key span{display:inline-flex;align-items:center;gap:6px}"
       ".pw-key i{display:inline-block;width:14px;height:10px;border-radius:3px;background:var(--accent)}.pw-key i.lt{background:var(--accent);opacity:.28}"
       ".pw-bars{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(0,1fr);gap:4px;align-items:end;height:180px}"
       ".pw-bars>div{position:relative;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;height:100%}"
       ".pw-bars .p8{position:absolute;bottom:18px;left:12%;right:12%;border-radius:4px 4px 0 0;background:var(--accent);opacity:.28}"
       ".pw-bars .md{position:relative;width:76%;max-width:30px;border-radius:4px 4px 0 0;background:var(--accent);margin-bottom:18px}"
       ".pw-bars .ct{position:relative;width:76%;max-width:30px;border-radius:4px 4px 0 0;background:var(--teal);margin-bottom:18px;opacity:.6}.pw-bars>div:last-child .ct{opacity:1}"
       ".pw-bars b{position:relative;font:600 11.5px system-ui,sans-serif;color:var(--ink);font-variant-numeric:tabular-nums;margin-bottom:3px}"
       ".pw-bars span{position:absolute;bottom:0;font-size:11px;color:var(--muted);white-space:nowrap}"
       ".pw-bars .gap{height:2px;width:60%;background:var(--line);margin-bottom:18px}.pw-bars.m24>div:not(:nth-child(3n+1)):not(:last-child) span{visibility:hidden}"
       ".pw-bars>div:last-child span{right:0}.pw-bars>div:first-child span{left:0}.pw-phone{display:none}@media(max-width:599px){.pw-phone{display:block}}"
       ".pw-seg{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 0}.pw-seg label{display:inline-flex;align-items:center;min-height:44px;padding:0 14px;border:1px solid var(--line);border-radius:999px;background:var(--card);cursor:pointer;font-weight:600;font-size:14px;color:var(--ink)}"
       ".pw-seg input{position:absolute;opacity:0;width:1px;height:1px}.pw-seg input:focus-visible+span{outline:3px solid var(--accent);outline-offset:4px;border-radius:4px}"
       ".pw-seg label:has(input:checked){background:var(--band);border-color:var(--band-line);color:#fff}"
       ".pw-pane{display:none}.pw-pane.on{display:block}"
       ".pw-note{margin:14px 0 0;padding:14px 16px;border-left:4px solid var(--teal);background:var(--teal-tint);border-radius:0 10px 10px 0;color:var(--ink2);max-width:760px}"
       ".pw-note b{color:var(--ink)}"
       ".pw-dl{display:inline-flex;align-items:center;gap:8px}"
       ".pw-steps{counter-reset:s;list-style:none;margin:14px 0 0;padding:0;display:grid;gap:10px;max-width:820px}"
       ".pw-steps li{counter-increment:s;position:relative;padding:14px 16px 14px 58px;background:var(--card);border:1px solid var(--line);border-radius:12px;color:var(--ink2)}"
       ".pw-steps li::before{content:counter(s);position:absolute;left:16px;top:13px;width:28px;height:28px;border-radius:50%;background:var(--band);color:#fff;font:700 14px/28px system-ui,sans-serif;text-align:center}"
       ".pw-steps b{display:block;color:var(--ink);font-size:16px;margin-bottom:2px}"
       ".pw-two{display:grid;gap:16px}@media(min-width:900px){.pw-two{grid-template-columns:1fr 1fr}}"
       ".pw-two .cta{grid-template-columns:1fr;height:100%;align-items:start}.pw-two .cta h2{margin-top:0;text-wrap:balance}"
       "@media(max-width:599px){.pw-t th,.pw-t td{padding:9px 8px}.pw-t .pw-hide{display:none}.pw-bars{height:150px;gap:2px}"
       ".pw-bars.m24>div:not(:nth-child(6n+1)):not(:last-child) span,.pw-bars.w12>div:not(:nth-child(3n+1)):not(:last-child) span,.pw-bars.m24>div:nth-child(19) span,.pw-bars.w12>div:nth-child(10) span{visibility:hidden}.pw-bars>div:not(:last-child) b{visibility:hidden}.pw-ch{padding:14px 12px 10px}}"
       "</style>")


def days(x, unit=True):
    if x is None:
        return "too few"
    return f"{x:,} day" + ("" if x == 1 else "s") if unit else f"{x:,}"


def month_word(m, short=True):
    import datetime as dt
    d = dt.date(int(m[:4]), int(m[5:7]), 1)
    return d.strftime("%b %Y") if short else d.strftime("%B %Y")


def months_span(ms):
    a, b = ms[0], ms[-1]
    if a[:4] == b[:4]:
        return f"{month_word(a).split()[0]} to {month_word(b)}"
    return f"{month_word(a)} to {month_word(b)}"


def table(head, rows, label, E, hide=()):
    """head: [text]; rows: [[cell html]] with the first cell a row header. hide: column indexes dropped on phones."""
    hc = lambda i: ' class="pw-hide"' if i in hide else ""
    th = "".join(f'<th scope="col"{hc(i)}>{h}</th>' for i, h in enumerate(head))
    body = "".join("<tr>" + "".join((f'<th scope="row">{c}</th>' if i == 0 else f"<td{hc(i)}>{c}</td>") for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="pw-tw" role="region" aria-label="{E(label)}" tabindex="0"><table class="pw-t"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def split_table(head, rows, label, E, show=20, hide=(), what="rows"):
    out = table(head, rows[:show], label if len(rows) <= show else f"{label}, the first {show}", E, hide)
    if len(rows) > show:
        out += (f'<details class="pw-more"><summary>Show the other {len(rows) - show} {E(what)}</summary>'
                + table(head, rows[show:], f"{label}, the rest", E, hide) + "</details>")
    return out


def cell_days(s, k):
    return f'{s[k]:,}' if s.get(k) is not None else '<span class="pw-na">too few</span>'


def wait_chart(monthly, E, caption, uid):
    """24 monthly columns: the median as a solid bar, the 80th percentile as a light bar behind it. Months with too few
    permits show a flat line and no number."""
    peak = max((m.get("p80") or 0 for m in monthly), default=0) or 1
    cols = []
    for m in monthly:
        lab = E(month_word(m["m"]))
        if m.get("med") is None:
            cols.append(f'<div><i class="gap"></i><span>{lab}</span></div>')
            continue
        cols.append(f'<div><i class="p8" style="height:calc({m["p80"] / peak:.3f} * (100% - 34px))"></i>'
                    f'<b>{m["med"]:,}</b><i class="md" style="height:calc({max(m["med"], 0.6) / peak:.3f} * (100% - 34px))"></i><span>{lab}</span></div>')
    say = "; ".join(f'{month_word(m["m"])}: half within {days(m["med"])}, 8 in 10 within {days(m["p80"])}' if m.get("med") is not None
                    else f'{month_word(m["m"])}: too few permits' for m in monthly)
    return (f'<figure class="pw-ch" id="{uid}"><figcaption>{E(caption)}</figcaption>'
            '<p class="pw-key"><span><i></i>Half were issued within (days)</span><span><i class="lt"></i>8 in 10 were issued within</span></p>'
            f'<div class="pw-bars m24" role="img" aria-label="{E(caption)}. {E(say)}">{"".join(cols)}</div></figure>')


def count_chart(items, E, caption, label_of):
    peak = max((x["count"] for x in items), default=0) or 1
    cols = "".join(f'<div><b>{x["count"]:,}</b><i class="ct" style="height:calc({max(x["count"], 0.3) / peak:.3f} * (100% - 34px))"></i>'
                   f'<span>{E(label_of(x))}</span></div>' for x in items)
    say = ", ".join(f'{label_of(x)}: {x["count"]:,}' for x in items)
    return (f'<figure class="pw-ch"><figcaption>{E(caption)}</figcaption>'
            f'<div class="pw-bars w12" role="img" aria-label="{E(caption)}. {E(say)}">{cols}</div></figure>')


def foot(M, rel, src, extra=""):
    pulled = M.nice_date(src["fetchedAt"][:10])
    E = M.E
    return (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            f'<p>Source: City of Chicago Data Portal, <a href="{E(src["url"])}">{E(src["name"])} dataset</a>, pulled {E(pulled)}. {extra}'
            'Counts and day figures only: no permit number, address or contact is kept, and no figure is about any one permit, '
            'property or business.</p>'
            f'<p>{E(M.CITY_DISCLAIMER["Chicago"])}</p><p>ProofNotFluff is not affiliated with or endorsed by the City of Chicago.</p>'
            '<p>Public information, not legal or permit advice. For your own permit, check with the agency.</p>'
            '<p>Made by ProofNotFluff with AI assistance from public City data. The page counts visits with Cloudflare Web Analytics, which sets no '
            'cookies.</p></div></footer>\n</body></html>')


def breaks(vals):
    """Map class cuts from geo_map.nice_breaks, kept above zero so no class reads "under 0"."""
    import geo_map as G
    out = []
    for c in G.nice_breaks(vals):
        if c > 0 and (not out or c - out[-1] >= max(2, round(out[-1] * 0.1))):   # no one-value classes next to each other
            out.append(c)
    return out


def legend(cuts, unit="", zero="None"):
    """Legend lines for the map classes: the first class says what it holds in words (zero when the first cut is 1)."""
    u = f" {unit}" if unit else ""
    if not cuts:
        return [("q0", "var(--gm0)", "Any", "Any")]
    first = zero if cuts[0] == 1 else f"Under {cuts[0]:,}{u}"
    out = [("q0", "var(--gm0)", first, zero if cuts[0] == 1 else f"<{cuts[0]:,}")]
    for i in range(1, len(cuts)):
        lo, hi = cuts[i - 1], cuts[i] - 1
        out.append((f"q{i}", f"var(--gm{i})", (f"{lo:,}" if lo == hi else f"{lo:,} to {hi:,}") + (" day" if unit == "days" and lo == hi == 1 else u), f"{lo:,}"))
    out.append((f"q{len(cuts)}", f"var(--gm{len(cuts)})", f"{cuts[-1]:,} or more{u}", f"{cuts[-1]:,}+"))
    return out


SEG_JS = ('<script>document.querySelectorAll("[data-pw-seg]").forEach(function(g){var b=g.closest("section");'
          'g.addEventListener("change",function(e){var v=e.target.value;b.querySelectorAll(".pw-pane").forEach(function(p){'
          'p.classList.toggle("on",p.getAttribute("data-pane")===v)})})});</script>')


# ---------------------------------------------------------------- this page
def path_rows(items, E, link=None):
    rows = []
    for r in items:
        s = r["last12"]
        name = E(r["label"])
        if link and link(r):
            name = f'<a href="{link(r)}">{name}</a>'
        rows.append([name, f'{s["n"]:,}', cell_days(s, "med"), cell_days(s, "p80"), cell_days(s, "p90"),
                     (f'{s["sameDay"]:.0f}%' if s.get("sameDay") is not None else '<span class="pw-na">too few</span>')])
    return rows


PATH_HEAD = ["Review path", "Permits issued, 12 months", "Half within (days)", "8 in 10 within (days)", "9 in 10 within (days)", "Same day"]
TYPE_HEAD = ["Permit type"] + PATH_HEAD[1:]


def area_rows(d, E):
    std = {a["a"]: a for a in d.get("areaStd", [])}
    exp = {a["a"]: a for a in d.get("areaExp", [])}
    rows = []
    for a in sorted([a for a in d["all"]["areas"] if a["n"]], key=lambda a: (-a["n"], a["name"])):
        s, x = std.get(a["a"], {"n": 0}), exp.get(a["a"], {"n": 0})
        rows.append([E(a["name"]), f'{a["n"]:,}', f'{s["n"]:,}', cell_days(s, "med"), cell_days(s, "p80"), cell_days(x, "med")])
    return rows


AREA_HEAD = ["Community area", "Permits issued, 12 months", "Standard Plan Review permits", "Standard Plan Review, half within (days)",
             "Standard Plan Review, 8 in 10 within (days)", "Express Permit Program, half within (days)"]


def map_block(d, E, M):
    import geo_map as G
    mn = d["rules"]["minN"]
    std = {a["a"]: a for a in d.get("areaStd", [])}
    exp = {a["a"]: a for a in d.get("areaExp", [])}
    allp = {a["a"]: a for a in d["all"]["areas"]}
    vals = lambda m: [a["med"] for a in m.values() if a.get("med") is not None]
    cs, ce, cn = breaks(vals(std)), breaks(vals(exp)), breaks([a["n"] for a in allp.values()])
    leg = lambda cuts, unit: legend(cuts, unit, zero="Same day")
    nx = ("nx", "repeating-linear-gradient(45deg,var(--gmn) 0 4px,var(--dash) 4px 5.5px)", f"Fewer than {mn} permits, too few to say")
    cls = lambda m, cuts: {k: (f"q{G.klass(a['med'], cuts)}" if a.get("med") is not None else "nx") for k, a in m.items()}
    areas = {}
    for k, a in allp.items():
        s, x = std.get(k, {"n": 0}), exp.get(k, {"n": 0})
        sd = lambda q: (f"half within {days(q['med'])}" if q.get("med") is not None else f"too few permits to say ({q['n']:,})")
        areas[k] = {"big": {"std": (days(s.get("med"), False) if s.get("med") is not None else "Too few", "days, half of Standard Plan Review permits"),
                            "exp": (days(x.get("med"), False) if x.get("med") is not None else "Too few", "days, half of Express Permit Program permits"),
                            "n": (f'{a["n"]:,}', "permits issued, last 12 months")},
                    "say": {"std": "Standard Plan Review: " + sd(s), "exp": "Express Permit Program: " + sd(x), "n": f'{a["n"]:,} permit{"" if a["n"] == 1 else "s"} issued in 12 months'},
                    "html": ('<dl>'
                             f'<dt>Permits issued, 12 months</dt><dd>{a["n"]:,}</dd>'
                             f'<dt>Standard Plan Review permits</dt><dd>{s["n"]:,}</dd>'
                             f'<dt>Standard, half within</dt><dd>{E(days(s.get("med")))}</dd><dt>Standard, 8 in 10 within</dt><dd>{E(days(s.get("p80")))}</dd>'
                             f'<dt>Express Permit Program, half within</dt><dd>{E(days(x.get("med")))}</dd></dl>')}
    metrics = [{"key": "std", "label": "Standard Plan Review", "legendTitle": "Standard Plan Review: days for half the permits, last 12 months",
                "cls": cls(std, cs), "legend": leg(cs, "days") + [nx]},
               {"key": "exp", "label": "Express Permit Program", "legendTitle": "Express Permit Program: days for half the permits, last 12 months",
                "cls": cls(exp, ce), "legend": leg(ce, "days") + [nx]},
               {"key": "n", "label": "Permits issued", "legendTitle": "Permits issued, last 12 months",
                "cls": {k: f"q{G.klass(a['n'], cn)}" for k, a in allp.items()}, "legend": legend(cn)}]
    slow = sorted([a for a in std.values() if a.get("med") is not None], key=lambda a: (-a["med"], a["name"]))[:3]
    fast = sorted([a for a in std.values() if a.get("med") is not None], key=lambda a: (a["med"], a["name"]))[:3]
    btn = lambda a: f'<li><button type="button" data-pick="{a["a"]}">{E(a["name"])}, {a["med"]:,} days</button></li>'
    hint = ('<h3>Standard Plan Review</h3>'
            + (f'<p class="gm-big"><span>{d["reviews_std_med"]:,}</span><small>days for half the permits citywide, last 12 months</small></p>' if d.get("reviews_std_med") is not None else "")
            + (f'<p>Longest waits:</p><ul class="gm-top">{"".join(btn(a) for a in slow)}</ul><p>Shortest waits:</p><ul class="gm-top">{"".join(btn(a) for a in fast)}</ul>' if slow else "")
            + f'<p class="gm-hint">Tap or hover any area, or choose one from the list. Areas with fewer than {mn} permits on a path show as too few to say.</p>')
    fig = G.choropleth(areas, metrics, uid="pwmap", title="Map of Chicago's 77 community areas, colored by permit wait days",
                       hint=hint, caption=("Community area outlines: City of Chicago, Boundaries - Community Areas. "
                                           "A permit counts in the community area of its primary address. Every number on the map is also in the table below."))
    return G.CSS + fig if fig else ""


def by_key(items, key):
    return next((x for x in items if x["key"] == key), None)


def lede_of(d, E, M):
    a, w = d["all"]["last12"], d["window"]
    std = by_key(d["reviews"], "STANDARD PLAN REVIEW")
    s = (f'Chicago issued {a["n"]:,} building permits in the 12 months to {E(M.nice_date(w["to"]))}. '
         f'Half were issued within {days(a["med"])} of the City starting review, and 8 in 10 within {days(a["p80"])}.')
    if std and std["last12"].get("med") is not None:
        s += (f' On Standard Plan Review, half took {days(std["last12"]["med"])} '
              f'and 8 in 10 took {days(std["last12"]["p80"])}.')
    return s


def trend_line(r, E):
    t = r["trend"]
    a, b = t["now"], t["then"]
    if a.get("med") is None or b.get("med") is None:
        return ""
    diff = a["med"] - b["med"]
    how = "the same as" if diff == 0 else (f'{abs(diff):,} day{"" if abs(diff) == 1 else "s"} {"longer than" if diff > 0 else "shorter than"}')
    return (f'{E(r["label"])}, {E(months_span(t["months"]))}: half within {days(a["med"])} ({a["n"]:,} permits), '
            f'{how} the same months a year earlier ({days(b["med"])}, {b["n"]:,} permits).')


def tiles_html(d, E, M):
    a, w = d["all"]["last12"], d["window"]
    std = by_key(d["reviews"], "STANDARD PLAN REVIEW")
    exp = by_key(d["reviews"], "EXPRESS PERMIT PROGRAM")
    t = []
    if std and std["last12"].get("med") is not None:
        t.append(f'<div class="tile key"><div class="lab">Standard Plan Review</div><div class="val">{std["last12"]["med"]:,} days</div>'
                 f'<div class="sub">half issued within; 8 in 10 within {std["last12"]["p80"]:,}</div></div>')
    if exp and exp["last12"].get("med") is not None:
        t.append(f'<div class="tile"><div class="lab">Express Permit Program</div><div class="val">{exp["last12"]["med"]:,} days</div>'
                 f'<div class="sub">half issued within; {exp["last12"]["sameDay"]:.0f}% the same day</div></div>')
    t.append(f'<div class="tile"><div class="lab">All permits</div><div class="val">{a["med"]:,} days</div>'
             f'<div class="sub">half issued within; 8 in 10 within {a["p80"]:,}</div></div>')
    t.append(f'<div class="tile"><div class="lab">Permits issued</div><div class="val">{a["n"]:,}</div><div class="sub">in the last 12 months</div></div>')
    return (f'<div class="tiles ld-tiles">{"".join(t)}</div>'
            f'<p class="asof">Figures as of {E(M.nice_date(w["to"]))}: permits issued from {E(M.nice_date(w["from12"]))} to {E(M.nice_date(w["to"]))}, from City of Chicago records pulled '
            f'{E(M.nice_date(d["source"]["fetchedAt"][:10]))}. Updated weekly.</p>')


def chart_panes(series, E, uid, intro):
    """series: [(key, label, monthly)] -> segmented control plus one chart per path (first shown without script)."""
    series = [s for s in series if any(m.get("med") is not None for m in s[2])]
    if not series:
        return ""
    seg = "".join(f'<label><input type="radio" name="{uid}" value="{E(k)}"{" checked" if i == 0 else ""}><span>{E(l)}</span></label>' for i, (k, l, _) in enumerate(series))
    panes = "".join(f'<div class="pw-pane{" on" if i == 0 else ""}" data-pane="{E(k)}">{wait_chart(m, E, intro + l + ", by month issued", uid + "-" + str(i))}</div>'
                    for i, (k, l, m) in enumerate(series))
    return (f'<div class="pw-seg" role="radiogroup" aria-label="Review path for the chart" data-pw-seg>{seg}</div>' if len(series) > 1 else "") + panes


def month_table(series, E, label):
    head = ["Month issued"] + [f"{l}: half / 8 in 10 (days)" for _, l, _ in series]
    months = [m["m"] for m in series[0][2]]
    rows = []
    for i, mo in enumerate(reversed(months)):
        j = len(months) - 1 - i
        rows.append([E(month_word(mo))] + [(f'{s[2][j]["med"]:,} / {s[2][j]["p80"]:,}<small>{s[2][j]["n"]:,} permits</small>' if s[2][j].get("med") is not None
                                            else f'<span class="pw-na">too few</span><small>({s[2][j]["n"]:,} permits)</small>') for s in series])
    return f'<details class="pw-more"><summary>Every month as a table</summary>{table(head, rows, label, E)}</details>'


METHOD = [
    "The measure is the City's own processing time field on each issued permit: the number of days between the day the City began reviewing the application and the issue date. We do not estimate any wait.",
    "Issued permits only. An application still in review has no issue date yet, so it is counted only once it is issued. When a review path slows down, these figures catch up as the slow permits come through.",
    "For most permit types, the City's issue date is the day it found the permit ready to issue, subject to paying the fee. For the Express Permit Program it is the day the permit was issued after the fee was paid. The days count every day in between, whoever was working on the application at the time.",
    "Half within means half of the permits took that many days or fewer (the median). 8 in 10 within means at least 8 in 10 permits took that many days or fewer; 9 in 10 within is the same for 9 in 10. Each is the real day count of the permit at that spot in the line, not an average. Waits have a long tail: a few permits take far longer than most, which is why the page shows 8 in 10 and 9 in 10 beside half within.",
    "Same-day permits: many Express Permit Program permits are issued the same day the City starts reviewing them, so they show 0 days. The share issued the same day is shown for each path.",
    "A group with fewer than {minN} permits shows its count but no day figures, because a median from a handful of permits says little. A permit type gets its own page when the City issued at least {pageFloor} of them in the last 12 months.",
    "A permit counts in the community area of its primary address, as the City records it. Permits the City later voided or revoked are not in the dataset.",
]


def method_html(d, E):
    r = d["rules"]
    k = d["counts"]
    drop = k["dropped"]
    extra = []
    if drop.get("noDays") or drop.get("negative"):
        nd = drop.get("noDays", 0) + drop.get("negative", 0)
        extra.append(f'{nd:,} issued permit{"" if nd == 1 else "s"} in the 24 months had no usable processing time and {"is" if nd == 1 else "are"} left out.')
    if k.get("checkedAgainstDates"):
        extra.append(f'Check: on {k["matchesDates"]:,} of {k["checkedAgainstDates"]:,} permits ({k["matchesDates"] / k["checkedAgainstDates"] * 100:.1f}%), the processing time equals the days between the two dates on the record.')
    return ('<section class="block" id="method"><h2>How this page is made</h2>'
            + "".join(f"<p>{E(x.format(**r))}</p>" for x in METHOD) + "".join(f"<p>{E(x)}</p>" for x in extra) + "</section>")


def rows_csv(d):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["scope", "permit_type", "review_path", "community_area", "period", "permits", "median_days", "p80_days", "p90_days", "same_day_pct"])
    win = d["window"]
    p12 = f'{win["from12"]} to {win["to"]}'
    put = lambda scope, t, r, a, per, s: w.writerow([scope, t, r, a, per, s.get("n", 0), s.get("med", ""), s.get("p80", ""), s.get("p90", ""), s.get("sameDay", "")])
    put("citywide", "All", "All", "All", p12, d["all"]["last12"])
    for r in d["reviews"]:
        put("review path", "All", r["label"], "All", p12, r["last12"])
    for t in d["types"]:
        put("permit type", t["label"], "All", "All", p12, t["last12"])
        for r in t["reviews"]:
            put("permit type and path", t["label"], r["label"], "All", p12, r["last12"])
    for a in d["all"]["areas"]:
        put("community area", "All", "All", a["name"], p12, a)
    for key, lab in (("areaStd", "Standard Plan Review"), ("areaExp", "Express Permit Program")):
        for a in d.get(key, []):
            put("community area and path", "All", lab, a["name"], p12, a)
    for m in d["all"]["monthly"]:
        put("month", "All", "All", "All", m["m"], m)
    for r in d["reviews"]:
        for m in r["monthly"]:
            put("month and path", "All", r["label"], "All", m["m"], m)
    for t in d["types"]:
        for m in t["monthly"]:
            put("month and type", t["label"], "All", "All", m["m"], m)
    return out.getvalue()


def head_html(M, p, url, rel, title, desc, robots, ld):
    return M.HEAD.format(title=M.E(title), desc=M.E(desc), url=url, rel=rel, shop=M.SHOP, ld=ld + CSS,
                         bodycls=' class="ld-page"', robots=robots, analytics=M.analytics_tag())


def shell(M, p, url, rel, crumb):
    return (head_html(M, p, url, rel, p["title"], p.get("desc", ""), '<meta name="robots" content="noindex, nofollow">', "")
            + f'{crumb}<div class="ld-hero"><h1>{M.E(p["h1"])}</h1><p class="lede">The first weekly count is on its way.</p></div></main></body></html>')


def page_html(p):
    import make_site as M
    E = M.E
    url, rel = M.BASE + p["slug"] + "/", "../"
    d = load(p)
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), ("Free Chicago data", "chicago-data/"), (META["h1"], None)])
    if not d:
        return shell(M, p, url, rel, crumb)
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    std = by_key(d["reviews"], "STANDARD PLAN REVIEW")
    d["reviews_std_med"] = std["last12"].get("med") if std else None
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    ds_ld = {"@context": "https://schema.org", "@type": "Dataset", "name": "Chicago permit wait times by permit type, review path and community area",
             "description": "Median and 80th percentile days from review start to issue for City of Chicago building permits, from the City's processing time field.",
             "url": url, "isAccessibleForFree": True, "creator": {"@type": "Organization", "name": "ProofNotFluff"},
             "isBasedOn": d["source"]["url"], "temporalCoverage": f'{d["window"]["from"]}/{d["window"]["to"]}', "spatialCoverage": "Chicago, Illinois",
             "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": url + CSV_NAME}]}
    mn = d["rules"]["minN"]
    paths = [r for r in d["reviews"] if r["last12"]["n"]]
    types = [t for t in d["types"] if t["last12"]["n"]]
    path_tbl = table(PATH_HEAD, path_rows(paths, E), "Permit wait days by review path, last 12 months", E, hide=(4, 5))
    type_tbl = table(TYPE_HEAD, path_rows(types, E, link=lambda t: f'{t["slug"]}/' if t["page"] else None), "Permit wait days by permit type, last 12 months", E, hide=(4, 5))
    pref = ["STANDARD PLAN REVIEW", "SELF CERT", "EXPRESS PERMIT PROGRAM"]
    ordered = sorted(paths, key=lambda r: (pref.index(r["key"]) if r["key"] in pref else 9, -r["last12"]["n"]))
    series = [(r["key"], r["label"], r["monthly"]) for r in ordered[:4]]
    trends = "".join(f"<li>{trend_line(r, E)}</li>" for r in ordered[:4] if trend_line(r, E))
    charts = chart_panes(series, E, "pwc", "")
    mtab = month_table(series, E, "Permit wait days by month issued and review path") if series else ""
    mapb = map_block(d, E, M)
    area_tbl = split_table(AREA_HEAD, area_rows(d, E), "Permit wait days by community area, last 12 months", E, show=20, hide=(2, 4), what="community areas")
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(META["h1"])}</h1><p class="lede">{lede_of(d, E, M)}</p>'
            '<div class="ld-heroact rl-act"><a class="btn" href="#types">Find your permit type</a>'
            + ('<a class="st-btn2" href="#map">Open the map</a>' if mapb else "") + '</div></div>'
            + tiles_html(d, E, M)
            + ('<section class="block" id="paths"><h2>By review path</h2><p>The review path decides most of the wait. The Express Permit Program is the '
               f"City's online path for repairs, replacements and small improvements; Standard Plan Review and Self Certification are plan-based paths for "
               f'projects such as new construction and rehabs (<a href="{DOB_PERMITS}" rel="noopener">City permit application guide</a>). '
               f'Days are from the City starting review to the issue date, for permits issued in the last 12 months.</p>{path_tbl}')
            + '<p class="asof">Path names are the City\'s own, as they appear in its permit records.</p>'
            + '<p class="asof pw-phone">On a phone the 9 in 10 and same day columns are left out; they are in the CSV below.</p></section>'
            + f'<section class="block" id="types"><h2>By permit type</h2><p>Tap a permit type for its own page with every review path, month and community area.</p>{type_tbl}'
            + '</section>'
            + f'<section class="block" id="months"><h2>Month by month</h2><p>The last 24 complete months. Pick a review path; each column is the permits issued that month.</p>{charts}{mtab}'
            + (f'<h3>Against a year earlier</h3><ul>{trends}</ul>' if trends else "") + '</section>'
            + (f'<section class="block" id="map"><h2>Wait times on the map</h2>{mapb}</section>' if mapb else "")
            + f'<section class="block" id="areas"><h2>Every community area</h2>{area_tbl}'
            + f'<p class="asof">Last 12 months. Fewer than {mn} permits on a path shows as too few.'
            + (f' {d["all"]["noArea12"]:,} permits had no community area on the record and count only in the city totals.' if d["all"].get("noArea12") else "") + '</p></section>'
            + f'<section class="block" id="download"><h2>Download the numbers</h2><p>Every figure on this page and its permit type pages, as one CSV file: citywide, by review path, permit type, community area and month.</p>'
            + f'<p><a class="btn pw-dl" href="{CSV_NAME}" download>Download the CSV</a></p></section>'
            + '<section class="block"><div class="pw-two">'
            + '<div class="cta ld-cta"><div><h2>Planning a job around a permit?</h2><p>The 8 in 10 figure for your permit type and path is how long most permits took to come through; the 9 in 10 figure shows how long the slow ones ran. For your own permit, check with the Department of Buildings.</p>'
            + f'<p class="ld-buybtn"><a class="btn" href="{DOB_PERMITS}" rel="noopener">City permit application guide</a></p></div></div>'
            + f'<div class="cta ld-cta"><div><h2>More free Chicago data</h2><p>Trackers built from City records for trade owners: rat complaints by neighborhood, demolition rodent baiting, trades news and more.</p>'
            + f'<p class="ld-buybtn"><a class="btn" href="{rel}chicago-data/">See every free tracker</a></p></div></div>'
            + '</div></section>'
            + method_html(d, E) + M.faq_block(FAQ)
            + '<p class="rl-act"><a class="btn" href="#types">Find your permit type</a> <a class="st-btn2" href="#download">Download the CSV</a></p>'
            + SEG_JS)
    return (head_html(M, p, url, rel, p["title"], p.get("desc", ""), robots, M.ld_tags(crumb_ld, faq_ld, ds_ld)) + body
            + foot(M, rel, d["source"], "Measure: the City's processing time field, days from review start to issue, for issued permits only. "))


def type_page(p, d, t, M):
    E = M.E
    url, rel = M.BASE + p["slug"] + "/" + t["slug"] + "/", "../../"
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    h1 = f'{t["label"]} Permit Wait Times in Chicago'
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), (META["h1"], p["slug"] + "/"), (t["label"], None)])
    s, w, mn = t["last12"], d["window"], d["rules"]["minN"]
    lede = (f'Chicago issued {s["n"]:,} {E(t["label"].lower())} permits in the 12 months to {E(M.nice_date(w["to"]))}. '
            + (f'Half were issued within {days(s["med"])} of the City starting review, and 8 in 10 within {days(s["p80"])}.' if s.get("med") is not None else ""))
    reviews = [r for r in t["reviews"] if r["last12"]["n"]]
    top = reviews[0] if reviews else None
    tiles = ('<div class="tiles ld-tiles">'
             + (f'<div class="tile key"><div class="lab">Half within</div><div class="val">{s["med"]:,} days</div><div class="sub">all review paths</div></div>'
                f'<div class="tile"><div class="lab">8 in 10 within</div><div class="val">{s["p80"]:,} days</div><div class="sub">9 in 10 within {s["p90"]:,}</div></div>' if s.get("med") is not None else "")
             + f'<div class="tile"><div class="lab">Permits issued</div><div class="val">{s["n"]:,}</div><div class="sub">in the last 12 months</div></div>'
             + (f'<div class="tile"><div class="lab">Most used path</div><div class="val" style="font-size:clamp(17px,9cqi,24px)">{E(top["label"])}</div><div class="sub">{top["last12"]["n"]:,} permits</div></div>' if top else "")
             + f'</div><p class="asof">Figures as of {E(M.nice_date(w["to"]))}: issued from {E(M.nice_date(w["from12"]))} to {E(M.nice_date(w["to"]))}, from City of Chicago records pulled {E(M.nice_date(d["source"]["fetchedAt"][:10]))}. Updated weekly.</p>')
    series = [("all", "All review paths", t["monthly"])] + [(r["key"], r["label"], r["monthly"]) for r in reviews[:3]]
    trs = "".join(f"<li>{trend_line(r, E)}</li>" for r in [dict(t, label="All review paths")] + reviews[:3] if trend_line(r, E))
    arows = []
    for a in sorted([a for a in t["areas"] if a["n"]], key=lambda a: (-a["n"], a["name"])):
        arows.append([E(a["name"]), f'{a["n"]:,}', cell_days(a, "med"), cell_days(a, "p80"), cell_days(a, "p90")])
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">Free Chicago permit tracker</p><h1>{E(h1)}</h1><p class="lede">{lede}</p>'
            f'<div class="ld-heroact rl-act"><a class="btn" href="#paths">See every review path</a><a class="st-btn2" href="{rel}{p["slug"]}/">All permit types</a></div></div>'
            + tiles
            + f'<section class="block" id="paths"><h2>By review path</h2>{table(PATH_HEAD, path_rows(reviews, E), "Wait days by review path, last 12 months", E, hide=(4, 5))}</section>'
            + f'<section class="block" id="months"><h2>Month by month</h2><p>The last 24 complete months, by month issued.</p>{chart_panes(series, E, "pwt", "")}{month_table(series, E, "Wait days by month issued")}'
            + (f'<h3>Against a year earlier</h3><ul>{trs}</ul>' if trs else "") + '</section>'
            + f'<section class="block" id="areas"><h2>Every community area</h2>'
            + split_table(["Community area", "Permits issued, 12 months", "Half within (days)", "8 in 10 within (days)", "9 in 10 within (days)"], arows,
                          f"{t['label']} permit wait days by community area", E, show=20, hide=(4,), what="community areas")
            + f'<p class="asof">Fewer than {mn} permits shows as too few.'
            + (f' {t["noArea12"]:,} permit{"" if t["noArea12"] == 1 else "s"} had no community area on the record and count only in the totals.' if t.get("noArea12") else "") + '</p></section>'
            + f'<section class="block"><h2>How this page is made</h2><p>{E(METHOD[0])}</p><p>{E(METHOD[1])}</p><p>{E(METHOD[3])}</p>'
            + f'<p>The full method and a CSV of every figure are on the <a href="{rel}{p["slug"]}/#method">main permit wait times page</a>.</p></section>'
            + f'<p class="rl-act"><a class="btn" href="{rel}{p["slug"]}/#types">Compare every permit type</a> <a class="st-btn2" href="{rel}{p["slug"]}/{CSV_NAME}">Download the CSV</a></p>'
            + SEG_JS)
    desc = f'How long {t["label"].lower()} permits take in Chicago: days from review start to issue by review path, month and neighborhood, from City records, updated weekly.'
    return (head_html(M, p, url, rel, f'{h1} | ProofNotFluff', desc, robots, M.ld_tags(crumb_ld)) + body
            + foot(M, rel, d["source"], "Measure: the City's processing time field, days from review start to issue, for issued permits only. "))


def extra_pages(p):
    import make_site as M
    d = load(p)
    if not d:
        return []
    out = [(CSV_NAME, rows_csv(d))]
    for t in d["types"]:
        if t["page"]:
            out.append((f'{t["slug"]}/index.html', type_page(p, d, t, M)))
    return out


def selftest():
    sys.path.insert(0, HERE)
    import make_site as M, tempfile, datetime as dt, random
    import dp_permit_wait_data as D
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("module") == "dp_permit_wait"][0]
    rnd = random.Random(7)
    rows = []
    today = dt.date(2026, 10, 27)
    for i in range(4000):
        iss = today - dt.timedelta(days=1 + rnd.randrange(730))
        rt, pt, dd = rnd.choice([("STANDARD PLAN REVIEW", "PERMIT - RENOVATION/ALTERATION", 20 + rnd.randrange(120)),
                                 ("EXPRESS PERMIT PROGRAM", "PERMIT - EASY PERMIT PROCESS", rnd.choice([0, 0, 0, 1, 3])),
                                 ("SELF CERT", "PERMIT - NEW CONSTRUCTION", 5 + rnd.randrange(40))])
        rows.append({"permit_type": pt, "review_type": rt, "issue_date": iss.isoformat() + "T00:00:00", "processing_time": str(dd),
                     "application_start_date": (iss - dt.timedelta(days=dd)).isoformat() + "T00:00:00", "community_area": str(1 + rnd.randrange(77))})
    from rodents_chicago import AREAS
    d = D.build(rows, today, "2026-10-27T07:00:00-0500", None, AREAS)
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, dir=ROOT)
    json.dump(d, tmp); tmp.close()
    try:
        q = dict(spec, data=os.path.relpath(tmp.name, ROOT))
        html = page_html(q)
        extras = dict(extra_pages(q))
    finally:
        os.unlink(tmp.name)
    for h in [html] + [v for k, v in extras.items() if k.endswith(".html")]:
        assert h.count("<h1>") == 1 and "—" not in h and "–" not in h, "one h1, no dashes"
        assert 'tabindex="0"' in h and M.E(M.CITY_DISCLAIMER["Chicago"]) in h, "keyboard tables, City disclaimer"
    std = by_key(d["reviews"], "STANDARD PLAN REVIEW")
    assert f'half took {std["last12"]["med"]} days' in html, "the Standard Plan Review median is in the lede"
    assert CSV_NAME in extras and extras[CSV_NAME].startswith("scope,permit_type") and "contact" not in extras[CSV_NAME].lower()
    assert all(t["slug"] + "/index.html" in extras for t in d["types"] if t["page"]), "a sub-page per type over the floor"
    assert "Every month as a table" in html and 'data-pw-seg' in html and "pwmap" in html, "chart switch, month table, map"
    shell_ = page_html(dict(spec, data="site/datapages/dp_permit_wait/none.json"))
    assert "noindex" in shell_ and extra_pages(dict(spec, data="site/datapages/dp_permit_wait/none.json")) == [], "no data: a noindex shell"
    print(f"dp_permit_wait selftest: ok ({len(extras)} extra files)")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
