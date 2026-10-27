#!/usr/bin/env python3
"""Chicago Repair Demand by Trade: the free page /chicago-repair-demand/ (site/pages.json kind "datapage", built by
tools/make_site.py through page_html here). Todd's go, Oct 27, 2026 ("Let's do them all", coo/PARALLEL_BUILDS.md,
build B8; research_notes/kimi-2026-10-27-r10.md item 14). Audience: trade owners (masons, porch carpenters,
electricians, HVAC and boiler, elevator and plumbing companies).

Data: site/datapages/dp_repairs/monthly.json (tools/dp_repairs_data.py, daily GitHub Action): new City of Chicago
building violations by trade, community area and month, sorted into trades by the published hand mapping
site/datapages/dp_repairs/trade-map.json, which this page shows in full. Counts only; no address, location, property,
owner or inspector detail exists in the file, so none can reach the page.

Usage: python3 tools/dp_repairs.py --selftest
"""
import csv, datetime as dt, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join("site", "datapages", "dp_repairs", "monthly.json")
MAPF = os.path.join(ROOT, "site", "datapages", "dp_repairs", "trade-map.json")
FEW = 10
CSV_AREA = "chicago-repair-demand-by-area-month.csv"
MAP_JSON = "chicago-repair-demand-trade-map.json"

META = {"h1": "Chicago Repair Demand by Trade",
        "card": "New Chicago building violations by trade and community area each month: masonry, porches, electrical, HVAC, elevators and plumbing. Updated daily.",
        "keywords": "building violations repair demand masonry tuckpointing exterior wall porch carpenter smoke detector carbon monoxide electrical boiler hvac ventilation refrigeration elevator plumbing neighborhood community area chicago"}


def load(p=None):
    f = os.path.join(ROOT, (p or {}).get("data", DATA))
    return json.load(open(f, encoding="utf-8")) if os.path.isfile(f) else None


def load_map():
    return json.load(open(MAPF, encoding="utf-8"))


def trade_of(m, code):
    import dp_repairs_data as R
    return R.trade_of(m, code)


def cited(d, m, c):
    """The City's own wording for a violation code: from the records, else from the mapping."""
    t = (d.get("desc") or {}).get(c) or (m["codes"].get(c) or {}).get("description") or ""
    return t if t and t != "None" else ""


def city_words(d, m, c):
    """The City's wording in quote marks, so it reads as verbatim; our own note when the record has none."""
    t = cited(d, m, c)
    return f"\u201c{sentence(t)}\u201d" if t else "(no description on the record)"


def low(label):
    """A trade label inside a sentence: first letter small, short forms (HVAC) kept."""
    return label if label.split()[0].isupper() else label[:1].lower() + label[1:]


def arrow(x):
    """The change on a tile: an arrow and the size, the sign in the arrow (design director, Oct 27)."""
    if x is None:
        return "new "
    return "same " if abs(x) < 1 else ("\u2191 " if x > 0 else "\u2193 ") + f"{abs(x):.0f}% "


def viol(n):
    return f"{n:,} violation" + ("" if n == 1 else "s")


ACR = {"CO", "HWH", "GFCI", "GFCI'S", "CIS", "PRV", "EM", "JBS", "D&H", "DU", "HVAC", "LIC", "WC", "HWT", "ELE", "FRT", "INT."}


def sentence(t):
    """The City's capitals in sentence case, keeping its short forms (CO, D&H, GFCI) as written."""
    words = t.split()
    out = [w if w.upper() in ACR else w.lower() for w in words]
    if out and out[0] == out[0].lower():
        out[0] = out[0][:1].upper() + out[0][1:]
    return " ".join(out)


def lastmod(p):
    d = load(p)
    return d["through"] if d else None


def ym_name(ym, short=False):
    y, m = map(int, ym.split("-"))
    return dt.date(y, m, 1).strftime("%b %Y" if short else "%B %Y")


def pct(x):
    if x is None:
        return "new"
    return ("+" if x > 0 else "\u2212" if x < 0 else "") + f"{abs(x):.0f}%" if abs(x) >= 1 else "same"   # a true minus sign


def change(now, before):
    return None if not before else (now / before - 1) * 100


def area_change(now, before):
    return "too few" if before < FEW else pct(change(now, before))


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def stats(d, m, names):
    months, through = d["months"], d["through"]
    t = dt.date.fromisoformat(through)
    L = months.index(through[:7]) if (t + dt.timedelta(days=1)).day == 1 else months.index(through[:7]) - 1
    win = lambda arr, end, n: sum(arr[max(0, end - n + 1):end + 1])
    out = {"L": L, "lm": months[L], "trades": []}
    for tr in m["trades"]:
        k = tr["key"]
        s = d["series"][k]
        c = s["city"]
        areas = []
        for n in range(1, 78):
            arr = s["area"][str(n)]
            areas.append({"n": n, "name": names.get(n, str(n)), "y12": win(arr, L, 12), "p12": win(arr, L - 12, 12), "m": arr[L]})
        for a in areas:
            a["rank"] = 1 + sum(1 for b in areas if b["y12"] > a["y12"])
            a["tied"] = sum(1 for b in areas if b["y12"] == a["y12"]) > 1
        codes = sorted(((cd, win(v, L, 12)) for cd, v in d["codes"].items() if trade_of(m, cd) == k), key=lambda x: (-x[1], x[0]))
        out["trades"].append({"key": k, "label": tr["label"], "short": tr.get("short", tr["label"]), "who": tr.get("who", ""),
                              "y12": win(c, L, 12), "p12": win(c, L - 12, 12), "m": c[L], "my": c[L - 12] if L >= 12 else None,
                              "city24": c[max(0, L - 23):L + 1], "ghost24": [c[i - 12] if i >= 12 else None for i in range(max(0, L - 23), L + 1)],
                              "noArea12": win(s["noArea"], L, 12), "areas": areas, "codes": codes})
        out["trades"][-1]["ch"] = change(out["trades"][-1]["y12"], out["trades"][-1]["p12"])
    allc = [sum(d["series"][k]["city"][i] for k in d["series"]) for i in range(len(months))]
    out["all12"] = win(allc, L, 12)
    out["traded12"] = sum(x["y12"] for x in out["trades"])
    out["labels"] = [ym_name(x, True) for x in months[max(0, L - 23):L + 1]]
    return out


CSS = ("<style>"
       ".rd-tabs{display:flex;flex-wrap:wrap;gap:6px;border:0;margin:0 0 14px;padding:0}.rd-tabs legend{font-size:13px;font-weight:700;color:var(--muted);margin:0 0 6px;padding:0}"
       ".rd-tabs label{position:relative;display:inline-flex;align-items:center;min-height:44px;padding:0 14px;border:1px solid var(--line);border-radius:999px;font-size:14.5px;font-weight:600;color:var(--ink2);cursor:pointer;background:var(--card)}"
       ".rd-tabs input{position:absolute;opacity:0;inset:0;margin:0;cursor:pointer}.rd-tabs label:has(input:checked){background:var(--ink);border-color:var(--ink);color:var(--card)}"
       ".rd-tabs label:has(input:focus-visible){outline:3px solid var(--focus);outline-offset:2px}"
       ".rd-p{display:none}@supports not selector(:has(*)){.rd-p{display:block}}"
       ".rd-card{margin:12px 0 8px;padding:16px 18px;background:var(--card);border:1px solid var(--line);border-radius:12px}.rd-card h3{margin:0 0 4px;font-size:20px;color:var(--ink)}.rd-card>p{margin:6px 0 0;color:var(--ink2)}"
       ".rd-nums{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:12px 0}@media(min-width:700px){.rd-nums{grid-template-columns:repeat(4,minmax(0,1fr))}}"
       ".rd-nums div{padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--canvas2)}.rd-nums b{display:block;font:700 24px/1.15 Poppins,system-ui,sans-serif;color:var(--ink);font-variant-numeric:tabular-nums}"
       ".rd-nums small{display:block;font-size:13px;color:var(--muted);margin-top:2px}"
       ".rd-chart{display:block;width:100%;height:auto}.rd-chart .b{fill:var(--accent)}.rd-chart .b2{fill:var(--accent);opacity:.35}.rd-chart .ax{stroke:var(--line);stroke-width:1}"
       ".rd-chart .gl{stroke:var(--rule);stroke-width:1}.rd-chart text{font:600 11px system-ui,sans-serif;fill:var(--muted)}.rd-chart .gt{font-weight:500}"
       ".rd-key{display:flex;flex-wrap:wrap;gap:14px;margin:6px 0 0;font-size:13.5px;color:var(--ink2)}.rd-key i{display:inline-block;width:14px;height:10px;border-radius:2px;background:var(--accent);margin-right:6px;vertical-align:middle}.rd-key .k2 i{opacity:.35}"
       ".rd-tw{overflow-x:auto;margin:12px 0 0;border:1px solid var(--line);border-radius:12px;background:var(--card)}.rd-tw:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
       ".rd-p .rd-t{max-width:760px}.rd-t{width:100%;border-collapse:collapse;font-size:14.5px}.rd-t th,.rd-t td{padding:9px 12px;border-bottom:1px solid var(--rule);text-align:right;font-variant-numeric:tabular-nums}"
       ".rd-t th:first-child,.rd-t td:first-child{text-align:left}.rd-t thead th{font-size:13px;color:var(--muted);font-weight:700;background:var(--card);vertical-align:bottom}"
       ".rd-t tbody th{font-weight:600;color:var(--ink);text-align:left}.rd-t tr:last-child td,.rd-t tr:last-child th{border-bottom:0}.rd-up{color:var(--warn-ink);font-weight:600}"
       ".rd-t td.rd-d,.rd-t th.rd-d{text-align:left;white-space:normal}.rd-t code{font-size:12.5px;color:var(--muted)}"
       ".rd-more{margin:12px 0 0}.rd-dl{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0 0}"
       ".rd-grid{display:grid;gap:10px;grid-template-columns:repeat(2,minmax(0,1fr));margin:8px 0}@media(min-width:900px){.rd-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}"
       ".rd-grid a{display:block;padding:12px 14px;border:1px solid var(--line);border-radius:12px;background:var(--card);text-decoration:none;color:var(--ink);min-height:44px}"
       ".rd-grid a.lead{background:var(--band);border-color:var(--band-line);color:#fff;--focus:#fff}.rd-grid a.lead small{color:var(--band-text)}.rd-grid a.lead em{display:inline-block;margin-left:6px;padding:1px 8px;border-radius:999px;background:var(--accent);color:#fff;font:700 11.5px/1.6 system-ui,sans-serif;font-style:normal;letter-spacing:.03em;text-transform:uppercase;vertical-align:2px}"
       ".rd-grid a{position:relative}.rd-grid .lab{display:block;font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);padding-right:56px}.rd-grid a.lead .lab{color:var(--band-soft)}"
       ".rd-grid a.lead em{position:absolute;top:10px;right:10px;margin:0}.rd-grid a:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
       ".rd-grid a:hover{border-color:var(--ink)}.rd-grid b{display:block;font:700 26px/1.1 Poppins,system-ui,sans-serif;font-variant-numeric:tabular-nums;margin-top:6px}.rd-grid small{display:block;color:var(--muted);font-size:13px;margin-top:2px}.rd-grid small.rd-ch{font-size:14px;font-weight:600;color:var(--ink2)}.rd-grid a.lead small.rd-ch{color:var(--band-text)}.rd-ls{display:none}@media(max-width:480px){.rd-lf{display:none}.rd-ls{display:inline}}"
       ".rd-two{display:grid;gap:16px}@media(min-width:900px){.rd-two{grid-template-columns:1fr 1fr}}.rd-two .cta{grid-template-columns:1fr;height:100%;align-items:start}.rd-two .cta h2{margin-top:0;text-wrap:balance}"
       ".rd-p .rd-t td,.rd-p .rd-t thead th{white-space:nowrap}.rd-t td:last-child,.rd-t th:last-child{padding-right:16px}.rd-s{display:none}.rd-swipe{display:none;margin:8px 0 0;font-size:13px;color:var(--muted)}"
       ".rd-chips{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 0;padding:0;list-style:none}.rd-chips li{padding:2px 10px;border-radius:999px;background:var(--canvas2);border:1px solid var(--line);font-size:13px;color:var(--ink2)}"
       "@media(max-width:599px){.rd-l{display:none}.rd-s{display:inline}.rd-swipe{display:block}.rd-p .rd-t{min-width:420px}.rd-t th,.rd-t td{padding:9px 8px}"
       ".rd-p .rd-t tbody th{min-width:140px;white-space:normal}.rd-p .rd-t tbody th,.rd-p .rd-t thead th:first-child{position:sticky;left:0;z-index:1;background:var(--card);box-shadow:1px 0 0 var(--rule)}}"
       "</style>")


def month_chart(vals, labels, ghost, E, label):
    """The same 24-month chart as the flooding page (gridlines, edge labels kept inside), in this page's classes."""
    import dp_flooding
    return dp_flooding.month_chart(vals, labels, ghost, E, label).replace('class="bf-chart ', 'class="rd-chart ')


def range_legend(cuts):
    if not cuts:
        return [("q0", "var(--gm0)", "Any")]
    out = [("q0", "var(--gm0)", f"Under {cuts[0]:,}", f"<{cuts[0]:,}")]
    for i in range(1, len(cuts)):
        lo, hi = cuts[i - 1], cuts[i] - 1
        out.append((f"q{i}", f"var(--gm{i})", f"{lo:,}" if lo == hi else f"{lo:,} to {hi:,}", f"{lo:,}"))
    out.append((f"q{len(cuts)}", f"var(--gm{len(cuts)})", f"{cuts[-1]:,} or more", f"{cuts[-1]:,}+"))
    return out


def map_block(st, E, period):
    import geo_map as G
    T = st["trades"]
    by = {t["key"]: {a["n"]: a for a in t["areas"]} for t in T}
    names = {a["n"]: a["name"] for a in T[0]["areas"]}
    areas = {}
    for n in range(1, 78):
        rows = "".join(f'<dt>{E(t["short"])}</dt><dd>{by[t["key"]][n]["y12"]:,}</dd>' for t in T)
        areas[n] = {"big": {t["key"]: (f'{by[t["key"]][n]["y12"]:,}', f'{"violation" if by[t["key"]][n]["y12"] == 1 else "violations"}, {low(t["label"])}, {period}') for t in T},
                    "say": {t["key"]: f'{viol(by[t["key"]][n]["y12"])}, {low(t["label"])}' for t in T},
                    "html": f'<p>New violations, {E(period)}, by trade:</p><dl>{rows}</dl>'}
    metrics = []
    for t in T:
        cuts = G.nice_breaks([a["y12"] for a in t["areas"]])
        metrics.append({"key": t["key"], "label": t["short"], "legendTitle": f'Violations, {low(t["label"])}, {period}',
                        "cls": {a["n"]: f"q{G.klass(a['y12'], cuts)}" for a in t["areas"]}, "legend": range_legend(cuts)})
    lead = T[0]
    top3 = sorted(lead["areas"], key=lambda a: (-a["y12"], a["name"]))[:3]
    hint = ('<h3>Citywide</h3>'
            f'<p class="gm-big"><span>{st["traded12"]:,}</span><small>new violations in these six trades, {E(period)}</small></p>'
            '<p>Most violations, by trade:</p><ul class="gm-top">'
            + "".join((lambda a: f'<li><button type="button" data-pick="{a["n"]}">{E(t["short"])}: {E(a["name"])}, {a["y12"]:,}</button></li>')(max(t["areas"], key=lambda a: (a["y12"], -a["n"]))) for t in T) + '</ul>'
            '<p class="gm-hint">Pick a trade above the map, then tap or hover any area, or choose one from the list.</p>')
    fig = G.choropleth(areas, metrics, uid="repairmap", title="Map of Chicago's 77 community areas, colored by the trade chosen above", hint=hint,
                       caption="Community area outlines: City of Chicago, Boundaries - Community Areas. Every number on the map is also in the trade tables below.")
    import dp_flooding
    return G.CSS + dp_flooding.pg_map(fig) if fig else ""


def csv_area(d, m, names):
    f = io.StringIO()
    w = csv.writer(f, lineterminator="\n")
    keys = [t["key"] for t in m["trades"]] + ["other"]
    w.writerow(["community_area_number", "community_area", "month"] + [t["label"] for t in m["trades"]] + ["Not sorted into a trade"])
    for n in range(1, 78):
        for i, ym in enumerate(d["months"]):
            w.writerow([n, names.get(n, n), ym] + [d["series"][k]["area"][str(n)][i] for k in keys])
    for i, ym in enumerate(d["months"]):
        w.writerow(["", "No map point on the record", ym] + [d["series"][k]["noArea"][i] for k in keys])
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
    m = load_map()
    pub = {"about": m.get("about", ""), "checkedAt": m.get("checkedAt", ""), "trades": m["trades"], "prefixes": m["prefixes"],
           "codes": m["codes"]}
    return [(CSV_AREA, csv_area(d, m, area_names())), (MAP_JSON, json.dumps(pub, indent=1, ensure_ascii=False))]


def page_html(p):
    import make_site as M
    E = M.E
    url, rel = M.BASE + p["slug"] + "/", "../"
    d = load(p)
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), ("Free Chicago data", "chicago-data/"), (META["h1"], None)])
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}
    head = lambda rb, ld: M.HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=M.SHOP, ld=ld + CSS + __import__("dp_flooding").SHARED_CSS,
                                        bodycls=' class="ld-page"', robots=rb, analytics=M.analytics_tag())
    if not d:
        return (head('<meta name="robots" content="noindex, nofollow">', "") + f'{crumb}<div class="ld-hero"><h1>{E(META["h1"])}</h1>'
                '<p class="lede">The first count is on its way.</p></div></main></body></html>')
    m = load_map()
    names = area_names()
    st = stats(d, m, names)
    src = d["source"]
    pulled = M.nice_date(src["fetchedAt"][:10])
    L = st["L"]
    first_m = d["months"][L - 11]
    period = f'{ym_name(first_m, True)} to {ym_name(st["lm"], True)}'
    yr_before = f'{ym_name(d["months"][L - 23], True)} to {ym_name(d["months"][L - 12], True)}'
    T = st["trades"]
    big = max(T, key=lambda t: t["y12"])
    tuck = [c for c, v in d["codes"].items() if "TUCK" in cited(d, m, c).upper() and sum(v[max(0, L - 11):L + 1])]
    faq = []
    for q, a in p["faq"]:
        if "tuckpointing" in q.lower() and tuck:
            a = f"Yes, under {', '.join(city_words(d, m, c) for c in tuck)}, which this page counts only if the mapping above lists the code."
        faq.append([q, a.replace("{period}", period)])
    p = dict(p, faq=faq)
    lede = (f'The City\'s Department of Buildings cited {st["traded12"]:,} violations from {E(ym_name(first_m))} to {E(ym_name(st["lm"]))} '
            f'that we sort into six repair trades: masonry, porches, electrical, HVAC, elevators and plumbing. {E(big["label"])} led with {big["y12"]:,}. '
            'See every trade in every community area, with each month in the free download.')
    grid = ('<div class="rd-grid">' + "".join(
        f'<a href="#t-{t["key"]}" data-tab="{t["key"]}"{" class=lead" if t is big else ""}><span class="lab"><span class="rd-lf">{E(t["label"])}</span><span class="rd-ls">{E(t["short"])}</span></span>{"<em>Most</em>" if t is big else ""}<b>{t["y12"]:,}</b><small class="rd-ch">{arrow(t["ch"])}vs the 12 months before</small></a>' for t in T)
        + f'</div><p class="asof">New violations, {E(period)}. Counts to {E(M.nice_date(d["through"]))}, from City of Chicago building violation records pulled {E(pulled)}. Updated every day.</p>')
    mapb = map_block(st, E, period)
    tabs = ('<fieldset class="rd-tabs"><legend>Trade</legend>'
            + "".join(f'<label><input type="radio" name="rdt" value="{t["key"]}" id="t-{t["key"]}"{" checked" if i == 0 else ""}>{E(t["short"])}</label>' for i, t in enumerate(T))
            + '</fieldset>')
    sel_css = "<style>" + "".join(f'.rd-wrap:has(#t-{t["key"]}:checked) .rd-p[data-t="{t["key"]}"]{{display:block}}' for t in T) + "</style>"
    panels = ""
    for t in T:
        top = sorted(t["areas"], key=lambda a: (-a["y12"], a["name"]))
        row = lambda a: (f'<tr><th scope="row">{E(a["name"])}</th><td>{"=" if a["tied"] else ""}{a["rank"]}</td><td>{a["y12"]:,}</td>'
                         + (f'<td class="rd-up">\u2191 {E(area_change(a["y12"], a["p12"]))}</td>' if a["p12"] >= FEW and a["y12"] >= a["p12"] * 1.25 else f'<td>{E(area_change(a["y12"], a["p12"]))}</td>')
                         + f'<td class="rd-x">{a["m"]:,}</td></tr>')
        thead = (f'<thead><tr><th scope="col">Community area</th><th scope="col">Rank</th><th scope="col"><span class="rd-l">12 months</span><span class="rd-s">12 mo</span></th><th scope="col">Change</th>'
                 f'<th scope="col" class="rd-x">{E(ym_name(st["lm"], True))}</th></tr></thead>')
        tbl = lambda rs, lab: f'<div class="rd-tw" role="region" aria-label="{E(lab)}" tabindex="0"><table class="rd-t">{thead}<tbody>{"".join(row(a) for a in rs)}</tbody></table></div>'
        lead = top[0]
        codes = "".join(f'<tr><td class="rd-d">{E(city_words(d, m, c))} <code>{E(c)}</code></td><td>{n:,}</td></tr>' for c, n in t["codes"][:8] if n)
        panels += (f'<div class="rd-p" data-t="{t["key"]}"><div class="rd-card"><h3>{E(t["label"])}</h3><p>{E(t["who"])}</p>'
                   f'<div class="rd-nums"><div><b>{t["y12"]:,}</b><small>new violations, {E(period)}</small></div><div><b>{E(pct(t["ch"]))}</b><small>vs the 12 months before</small></div>'
                   f'<div><b>{t["m"]:,}</b><small>in {E(ym_name(st["lm"]))}</small></div><div><b>{lead["y12"]:,}</b><small>most, in {E(lead["name"])}</small></div></div>'
                   + month_chart(t["city24"], st["labels"], t["ghost24"], E, f'Violations each month, {low(t["label"])}, for 24 months, with the same month a year earlier behind each bar')
                   + '<p class="rd-key"><span><i></i>That month</span><span class="k2"><i></i>Same month a year earlier</span></p></div>'
                   + f'<p class="up-key"><b>\u2191 Red</b> marks a rise of 25% or more vs the 12 months before, where those months had at least {FEW} violations.</p>'
                   + '<p class="rd-swipe">Swipe the table sideways for more columns.</p>'
                   + tbl(top[:15], f'Violations, {low(t["label"])}: the 15 community areas with the most')
                   + f'<details class="rd-more"><summary>Show the other {len(top) - 15} community areas</summary>' + tbl(top[15:], f'Violations, {low(t["label"])}: the other community areas') + '</details>'
                   + (f'<details class="rd-more"><summary>What the City cited most for {E(low(t["label"]))}</summary><div class="rd-tw"><table class="rd-t">'
                      f'<thead><tr><th scope="col" class="rd-d">Violation as the City words it, with its code</th><th scope="col">12 months</th></tr></thead><tbody>{codes}</tbody></table></div></details>' if codes else "")
                   + '</div>')
    other12 = st["all12"] - st["traded12"]
    note = (f'<p class="asof">12 months is {E(period)}; change compares it with {E(yr_before)}, rounded to a whole percent. Within 1% shows as same, and under {FEW} in the earlier 12 months as too few. '
            f'Rank is within the trade; = marks a tie. {other12:,} of the {st["all12"]:,} violations in those months fit none of these trades (paperwork, permits, signs, general upkeep and more) and are not shown by trade.'
            + (f' {sum(t["noArea12"] for t in T):,} trade violations had no map point on the record and count only in the city totals.' if any(t["noArea12"] for t in T) else "")
            + '</p>'
            f'<div class="rd-dl"><a class="st-btn2" href="{CSV_AREA}" download>Download every area by month (CSV)</a>'
            f'<a class="st-btn2" href="{MAP_JSON}" download>Download the trade mapping (JSON)</a></div>')
    trades_sec = f'<div class="rd-wrap">{sel_css}{tabs}{panels}</div>{note}'
    # the published mapping
    mp_rows = ""
    for t in m["trades"]:
        cs = [c for c, v in sorted(m["codes"].items()) if v["trade"] == t["key"]]
        ps = [(x, v["series"]) for x, v in m["prefixes"].items() if v["trade"] == t["key"]]
        top = [c for c, n in next(x for x in T if x["key"] == t["key"])["codes"][:4] if n]
        mp_rows += (f'<tr><th scope="row">{E(t["label"])}</th><td class="rd-d">'
                    + (E("Codes in the City's " + (", ".join(f"{x} ({b})" for x, b in ps[:-1]) + " and " if len(ps) > 1 else "") + f"{ps[-1][0]} ({ps[-1][1]})"
                         + (" code series" if len(ps) > 1 else " code series")) + (", plus " if cs else ". ") if ps else "")
                    + ((f'{len(cs)} named codes. ' if ps else f'{len(cs)} named codes. ') if cs else "")
                    + ("Most cited, in the City's words:" + '<ul class="rd-chips">' + "".join(f"<li>{E(city_words(d, m, c))}</li>" for c in top) + "</ul>" if top else "")
                    + '</td></tr>')
    left = sum(1 for v in m["codes"].values() if v["trade"] == "other")
    mapping = (f'<p>{E(m.get("about", ""))}</p><details class="rd-more"><summary>See how each trade is counted</summary>'
               '<div class="rd-tw"><table class="rd-t"><thead><tr><th scope="col">Trade</th><th scope="col" class="rd-d">What we count</th></tr></thead>'
               f'<tbody>{mp_rows}</tbody></table></div></details><p class="asof">{left} codes in those series are left out on purpose, because their '
               'wording is paperwork, a permit, plans, records or arranging an inspection rather than a repair. The full list, with the reason for each code left out, is in the mapping download.</p>')
    tr = p["trade"]
    two = ('<section class="block" id="next"><div class="rd-two pg-two">'
           + "".join(f'<div class="cta ld-cta"><div><h2>{E(c["title"])}</h2><p>{E(c["text"])}</p>'
                     f'<p class="ld-buybtn"><a class="btn" href="{rel}{E(c["slug"])}/">{E(c["button"])}</a></p></div></div>' for c in tr)
           + '</div></section>')
    method = '<section class="block" id="how"><h2>How this page is made</h2>' + "".join(f"<p>{E(x)}</p>" for x in p["method"]) + "</section>"
    js = ('<script>(function(){var C=document.querySelectorAll("[data-tab]");'
          'function mark(k){'
          'var r=document.querySelector("#repairmap .gm-seg input[value=\'"+k+"\']");if(r&&!r.checked){r.checked=true;r.dispatchEvent(new Event("change"));}}'
          'document.querySelectorAll("input[name=rdt]").forEach(function(i){i.addEventListener("change",function(){mark(i.value);});});'
          'document.querySelectorAll("#repairmap .gm-seg input").forEach(function(i){i.addEventListener("change",function(){var t=document.getElementById("t-"+i.value);if(t&&!t.checked){t.checked=true;}});});'
          'C.forEach(function(a){a.addEventListener("click",function(e){var i=document.getElementById("t-"+a.dataset.tab);'
          'if(!i)return;e.preventDefault();i.checked=true;mark(a.dataset.tab);document.getElementById("trades").scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth"});i.focus({preventScroll:true});});});'
          '})();</script>'
          + __import__("dp_flooding").PG_JS + __import__("dp_flooding").HP_JS)
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(META["h1"])}</h1><p class="lede">{lede}</p>'
            '<div class="ld-heroact rl-act"><a class="btn" href="#trades">See your trade by neighborhood</a>'
            + __import__("dp_flooding").hero_pick(names, "#repairmap select", "map", E) + '</div></div>'
            f'{grid}'
            + __import__("dp_flooding").pg_nav([("map", "Map"), ("trades", "By trade"), ("mapping", "How trades are sorted"), ("faq", "Questions")], E)
            + (f'<section class="block" id="map"><h2>Violations on the map</h2>{mapb}</section>' if mapb else "")
            + f'<section class="block" id="trades"><h2>Every community area, by trade</h2>{trades_sec}</section>'
            f'<section class="block" id="mapping"><h2>How violations are sorted into trades</h2>{mapping}</section>'
            + two + method + M.faq_block(p["faq"]).replace('<section class="block">', '<section class="block" id="faq">', 1) +
            f'<p class="rl-act"><a class="btn" href="#trades">See your trade by neighborhood</a> <a class="st-btn2" href="{rel}chicago-data/">More free Chicago data</a></p>{js}')
    foot = (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}<div class="pg-notes">'
            f'<p>Source: City of Chicago Data Portal, <a href="{E(src["url"])}">Building Violations dataset</a>, by violation date, pulled {E(pulled)}. '
            'A violation is one item an inspector cited; it says nothing about whether the work is still open, and this page names no building, address or owner.</p>'
            + "".join(f"<p>{E(x)}</p>" for x in p.get("sourceNotes", []))
            + f'<p>{E(M.CITY_DISCLAIMER["Chicago"])}</p><p>ProofNotFluff is not affiliated with or endorsed by the City of Chicago.</p>'
            '<p>Public information, not legal, code or building advice for any property. For a question about a violation, check with the Department of Buildings.</p>'
            '<p>Made by ProofNotFluff with AI assistance from public City data. The page counts visits with Cloudflare Web Analytics, which sets no cookies.</p></div></div></footer>\n</body></html>')
    data_ld = {"@context": "https://schema.org", "@type": "Dataset", "name": META["h1"], "description": p["desc"], "url": url,
               "isAccessibleForFree": True, "creator": {"@type": "Organization", "name": "ProofNotFluff"}, "isBasedOn": src["url"],
               "temporalCoverage": f'{d["months"][0]}-01/{d["through"]}', "spatialCoverage": "Chicago, Illinois",
               "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": url + CSV_AREA}]}
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}
    return head(robots, M.ld_tags(crumb_ld, faq_ld, data_ld)) + body + foot


def selftest():
    sys.path.insert(0, HERE)
    import make_site as M
    import dp_repairs_data as R
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("slug") == "chicago-repair-demand"][0]
    m = R.load_map()
    months = R.month_list("2024-09", "2026-10")
    keys = [t["key"] for t in m["trades"]]
    per = {}
    code0 = next(c for c, v in m["codes"].items() if v["trade"] == keys[0])
    for i, ym in enumerate(months):
        tr = {k: {6: 5, 70: (30 if ym >= "2025-10" else 15)} for k in keys}
        tr["other"] = {6: 100, 0: 4}
        per[ym] = (tr, {code0: 35, "ZZ": 104}, {code0: "REPAIR EXTERIOR WALL"})
    d = R.assemble(per, months, "2026-10-26", "2026-10-27T06:00:00-0500", dict(m, _hash="x"))
    import tempfile
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, dir=ROOT)
    json.dump(d, tmp); tmp.close()
    try:
        q = dict(spec, data=os.path.relpath(tmp.name, ROOT))
        st = stats(d, m, area_names())
        t0 = st["trades"][0]
        assert st["lm"] == "2026-09" and t0["y12"] == 12 * 35 and t0["p12"] == 12 * 20 and round(t0["ch"]) == 75, t0
        ash = next(a for a in t0["areas"] if a["n"] == 70)
        assert ash["rank"] == 1 and ash["y12"] == 360 and t0["codes"][0] == (code0, 420)
        assert st["all12"] == st["traded12"] + 12 * 104
        html = page_html(q)
        ex = dict(extra_pages(q))
    finally:
        os.unlink(tmp.name)
    assert html.count("<h1>") == 1 and "—" not in html and "–" not in html, "one h1, no dashes"
    assert "Oct 2025 to Sep 2026" in html and "+75%" in html and "Ashburn" in html
    assert M.E(M.CITY_DISCLAIMER["Chicago"]) in html
    assert ex[CSV_AREA].count("\n") == 1 + 78 * len(months) and MAP_JSON in ex
    assert all(x not in html.lower() for x in ("latitude", "street_name", "inspector_id"))
    print("dp_repairs selftest: ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
