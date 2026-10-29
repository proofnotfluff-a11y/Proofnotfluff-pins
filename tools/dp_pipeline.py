#!/usr/bin/env python3
"""Chicago's big building jobs by how far along they are: the free weekly page /chicago-construction-pipeline/
(site/pages.json kind "datapage", module dp_pipeline; tools/make_site.py calls page_html here). Todd's go, Oct 29, 2026,
3:56 pm: "Yes, please do. Go with your recommendations for everything" (counts only, a dated weekly snapshot, method and
sources; research_notes/stage-timing-2026-10-29.md for why the page never says "weeks before move-in").

Data: site/datapages/dp_pipeline/data.json (tools/dp_pipeline_data.py, on the Monday permit wait run): open permits of
$500,000 or more on the City's certificate of occupancy path, by community area and months since the permit, plus
issue-year cohorts. Counts only; no address, permit number or business name exists in the file, so none can reach the page.
The addresses and builders stay in the paid members' list (Todd, Oct 27: "lead seats and exports stay paid").

Usage: python3 tools/dp_pipeline.py --selftest
"""
import csv, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = "site/datapages/dp_pipeline/data.json"
CSV_NAME = "chicago-construction-pipeline-by-community-area.csv"
LEADS_SLUG = "chicago-construction-cleaning-leads"
BUCKET_WORDS = [("b0", "Under 6 months", "under 6 mo."), ("b1", "6 to 12 months", "6 to 12 mo."),
                ("b2", "1 to 2 years", "1 to 2 yrs"), ("b3", "Over 2 years", "over 2 yrs")]
SHORT = {"b0": "Under 6 mo", "b2": "1 to 2 yrs"}

META = {"h1": "Chicago's Big Building Jobs, by How Far Along They Are",
        "card": "Open Chicago building jobs of $500,000 or more still waiting on a certificate of occupancy, by neighborhood and by months since the permit. Updated weekly.",
        "keywords": "Chicago construction projects, new construction Chicago by neighborhood, Chicago certificate of occupancy, post construction cleaning leads Chicago, Chicago building permits in progress, construction pipeline Chicago"}


def load(p=None):
    f = os.path.join(ROOT, (p or {}).get("data", DATA))
    return json.load(open(f, encoding="utf-8")) if os.path.isfile(f) else None


def lastmod(p):
    d = load(p)
    return d["asOf"] if d else None


def plural(n, word, many=None):
    return f"{n:,} {word if n == 1 else (many or word + 's')}"


CSS = ("<style>"
       ".pp-co{display:grid;gap:10px;margin:14px 0 4px;padding:16px 18px;background:var(--card);border:1px solid var(--line);border-radius:12px}"
       ".pp-co .yr{display:grid;grid-template-columns:52px 1fr;gap:4px 12px;align-items:center}"
       ".pp-co .yr>b{grid-row:span 2;font:700 15px system-ui,sans-serif;color:var(--ink);font-variant-numeric:tabular-nums}"
       ".pp-co .bar{display:flex;align-items:center;gap:8px;min-width:0;font-size:13px;color:var(--muted)}"
       ".pp-co .bar i{display:block;height:14px;border-radius:0 5px 5px 0;min-width:3px;background:var(--accent)}"
       ".pp-co .bar.reno i{background:color-mix(in srgb,var(--accent) 40%,var(--card))}"
       ".pp-co .bar span{white-space:nowrap;font-variant-numeric:tabular-nums}.pp-co .bar span b{color:var(--ink)}"
       ".pp-key{display:flex;flex-wrap:wrap;gap:6px 18px;margin:0 0 2px;font-size:13px;color:var(--muted)}"
       ".pp-key span::before{content:'';display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:6px;vertical-align:-1px;background:var(--accent)}"
       ".pp-key span.reno::before{background:color-mix(in srgb,var(--accent) 40%,var(--card))}"
       ".pp-tw{overflow-x:auto;margin:12px 0 0;border:1px solid var(--line);border-radius:12px;background:var(--card)}"
       ".pp-tw:focus-visible{outline:3px solid var(--focus,var(--accent));outline-offset:2px}"
       ".pp-t{width:100%;border-collapse:collapse;font-size:14.5px;min-width:640px}"
       ".pp-t th,.pp-t td{padding:9px 12px;border-bottom:1px solid var(--rule);text-align:right;font-variant-numeric:tabular-nums}"
       ".pp-t th:first-child,.pp-t td:first-child{text-align:left}"
       ".pp-t thead th{font-size:13px;color:var(--muted);font-weight:700;background:var(--card);position:sticky;top:0}"
       ".pp-t tbody th{font-weight:600;color:var(--ink);text-align:left}.pp-t tr:last-child td,.pp-t tr:last-child th{border-bottom:0}"
       ".pp-t td.z{color:var(--muted)}.pp-t td.tot{font-weight:700;color:var(--ink)}"
       ".pp-more{margin:12px 0 0}.pp-more summary{display:flex;align-items:center;min-height:44px;padding:0 16px;border:1px solid var(--line);"
       "border-radius:12px;background:var(--card);cursor:pointer;font-weight:600;color:var(--ink)}.pp-more[open] summary{margin-bottom:8px}.pp-more .pp-tw{margin:0}"
       ".pp-dl{display:grid;gap:12px;margin:12px 0 0}.pp-dl div{padding:14px 16px;background:var(--card);border:1px solid var(--line);border-radius:12px}"
       ".pp-dl dt{font-weight:700;color:var(--ink);margin:0 0 4px}.pp-dl dd{margin:0;color:var(--ink)}.pp-dl dd small{display:block;margin-top:6px;color:var(--muted);font-size:13px}"
       "@media(min-width:900px){.pp-dl{grid-template-columns:1fr 1fr}}"
       ".pp-one .cta{grid-template-columns:1fr}.ld-page .ld-tiles{margin-top:22px}.ld-page .ld-heroact .st-btn2{min-height:50px}"
       "@media(max-width:599px){.pp-t{min-width:0}.pp-t th,.pp-t td{padding:9px 6px;font-size:13.5px}"
       ".pp-t .hm{display:none}.pp-co .yr{grid-template-columns:44px 1fr}.ld-tiles .lab{white-space:normal}}"
       ".pp-a{table-layout:fixed;min-width:640px}.pp-a th:first-child{width:28%}.pp-t .sh{display:none}"
       "#weeks tbody th{white-space:nowrap}.pp-one .ld-buybtn{margin-top:16px}.pp-one .cta p{text-wrap:pretty}.pp-more .pp-tw{border-color:transparent}"
       "@media(min-width:900px){#pmap .gm-side{align-content:space-between}#weeks .pp-tw{max-width:560px}}"
       "#pmap .gm-a path.sel{stroke:var(--ink);stroke-width:3;paint-order:normal}"
       ".gm-info .pp-by{margin:12px 0 0;padding-top:10px;border-top:1px solid var(--line);font-size:12.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}"
       ".gm-info .pp-by+dl{margin-top:6px}"
       "@media(min-width:860px){#pmap .gm-stage svg{max-height:600px}}"
       "@media(max-width:599px){.pp-more,.pp-more .pp-tw{min-width:0;max-width:100%}.pp-a{min-width:0}.pp-a th:first-child{width:30%}"
       ".pp-t th,.pp-t td{padding:9px 5px}.pp-t th:first-child,.pp-t td:first-child{padding-left:12px}.pp-t th:last-child,.pp-t td:last-child{padding-right:12px}"
       ".pp-t thead th{vertical-align:bottom;text-wrap:balance}.pp-t .lg{display:none}.pp-t .sh{display:inline}"
       "#pmap .gm-seg{display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}"
       "#pmap .gm-seg label{justify-content:center;padding:4px 6px;font-size:13.5px;line-height:1.15;text-align:center}}"
       "@media (prefers-color-scheme:dark){:root:not([data-theme=light]) .pp-co .bar.reno i,:root:not([data-theme=light]) .pp-key span.reno::before{background:color-mix(in srgb,var(--accent) 55%,var(--ink))}}:root[data-theme=dark] .pp-co .bar.reno i,:root[data-theme=dark] .pp-key span.reno::before{background:color-mix(in srgb,var(--accent) 55%,var(--ink))}@media (prefers-color-scheme:dark){:root:not([data-theme=light]) #next .ld-cta{background:#222a3b;border-color:#3a4152;border-top:3px solid var(--accent)}}:root[data-theme=dark] #next .ld-cta{background:#222a3b;border-color:#3a4152;border-top:3px solid var(--accent)}"
       "</style>")


def map_block(d, E):
    import geo_map as G
    areas, partial_cls, old_cls = {}, {}, {}
    c_open = [x for x in G.nice_breaks([a["open"] for a in d["areas"]]) if x > 0]
    c_b2 = [x for x in G.nice_breaks([a["b2"] for a in d["areas"]]) if x > 0]
    legend = lambda cuts: ([("q0", "var(--gm0)", "None" if cuts[0] == 1 else f"Under {cuts[0]:,}", "0" if cuts[0] == 1 else f"<{cuts[0]:,}")]
                           + [(f"q{i}", f"var(--gm{i})", f"{cuts[i - 1]:,}" if cuts[i - 1] == cuts[i] - 1 else f"{cuts[i - 1]:,} to {cuts[i] - 1:,}", f"{cuts[i - 1]:,}")
                              for i in range(1, len(cuts))]
                           + [(f"q{len(cuts)}", f"var(--gm{len(cuts)})", f"{cuts[-1]:,} or more", f"{cuts[-1]:,}+")]) if cuts else [("q0", "var(--gm0)", "Any")]
    for a in d["areas"]:
        areas[a["n"]] = {"big": {"open": (f'{a["open"]:,}', "open big jobs"), "b2": (f'{a["b2"]:,}', "permits 1 to 2 years old"),
                                 "partial": (f'{a["partial"]:,}', "with partial occupancy")},
                         "say": {"open": plural(a["open"], "open big job"), "b2": f'{a["b2"]:,} with permits 1 to 2 years old',
                                 "partial": f'{a["partial"]:,} with partial occupancy'},
                         "html": ("<dl>" + "".join(f"<dt>{E(w)}</dt><dd>{a[k]:,}</dd>" for k, w, _ in BUCKET_WORDS)
                                  + f'<dt>Partial occupancy</dt><dd>{a["partial"]:,}</dd></dl><p class="pp-by">By type</p><dl><dt>New buildings</dt><dd>{a["new"]:,}</dd>'
                                  f'<dt>Renovations</dt><dd>{a["reno"]:,}</dd></dl>')}
        partial_cls[a["n"]] = "q0" if not a["partial"] else "q2" if a["partial"] < 3 else "q4"
    metrics = [{"key": "open", "label": "All open jobs", "legendTitle": "Open building jobs of $500,000 or more",
                "cls": {a["n"]: f"q{G.klass(a['open'], c_open)}" for a in d["areas"]}, "legend": legend(c_open)},
               {"key": "b2", "label": "Permit 1 to 2 years", "legendTitle": "Open jobs whose permit is 1 to 2 years old",
                "cls": {a["n"]: f"q{G.klass(a['b2'], c_b2)}" for a in d["areas"]}, "legend": legend(c_b2)},
               {"key": "partial", "label": "Partial occupancy", "legendTitle": "Open jobs with partial occupancy approved",
                "cls": partial_cls, "legend": [("q0", "var(--gm0)", "None"), ("q2", "var(--gm2)", "1 or 2"), ("q4", "var(--gm4)", "3 or more")]}]
    c = d["city"]
    top3 = sorted([a for a in d["areas"] if a["open"]], key=lambda a: (-a["open"], a["name"]))[:3]
    hint = ("<h3>Citywide</h3>"
            f'<p class="gm-big"><span>{c["open"]:,}</span><small>open building jobs of $500,000 or more</small></p>'
            '<p>Most open jobs:</p><ul class="gm-top">'
            + "".join(f'<li><button type="button" data-pick="{a["n"]}">{E(a["name"])}, {a["open"]:,}</button></li>' for a in top3)
            + '</ul><p class="gm-hint">Tap or hover any area on the map, or choose one from the list.</p>')
    fig = G.choropleth(areas, metrics, uid="pmap", title="Map of Chicago's 77 community areas, colored by open building jobs of $500,000 or more",
                       hint=hint, caption=("Community area outlines: City of Chicago, Boundaries - Community Areas. "
                                           "Every number on the map is also in the table below."))
    return G.CSS + fig if fig else ""


def cohort_block(d, E):
    rows = [r for r in d["cohorts"] if (r["new"]["path"] or r["reno"]["path"])]
    bar = lambda r, t, word: (f'<div class="bar{" reno" if t == "reno" else ""}"><i style="width:{max(1, r[t]["share"] or 0) * 0.82:.1f}%"></i>'
                              f'<span><b>{r[t]["share"]}%</b> of {r[t]["path"]:,} {word}</span></div>' if r[t]["path"] else "")
    label = ", ".join(f'{r["year"]}: new {r["new"]["share"]}%, renovations {r["reno"]["share"]}%' for r in rows)
    return ('<div class="pp-key" aria-hidden="true"><span>New buildings</span><span class="reno">Renovations</span></div>'
            f'<div class="pp-co" role="img" aria-label="{E("Share of big jobs on the certificate of occupancy path that have their certificate today, by permit year. " + label)}">'
            + "".join(f'<div class="yr"><b>{r["year"]}</b>{bar(r, "new", "new")}{bar(r, "reno", "renovations")}</div>' for r in rows)
            + "</div>")


def history_block(d, E):
    import make_site as M
    h = d["history"]
    first = len(h) == 1 or all(x["moves"] is None for x in h)
    mv = lambda x, k, cls="": "" if first else f'<td{cls}>{"" if x["moves"] is None else format(x["moves"][k], ",")}</td>'
    rows = "".join(f'<tr><th scope="row">{E(M.nice_date(x["week"]))}</th><td>{x["open"]:,}</td><td>{x["partial"]:,}</td>'
                   + mv(x, "gotCo") + mv(x, "toPartial") + mv(x, "newOnPath", ' class="hm"') + "</tr>"
                   for x in reversed(h))
    return ('<div class="pp-tw" role="region" aria-label="Weekly snapshots" tabindex="0"><table class="pp-t"' + (' style="min-width:0"' if first else "") + '><thead><tr>'
            '<th scope="col">Week of</th><th scope="col">Open jobs</th><th scope="col">Partial occupancy</th>'
            + ("" if first else '<th scope="col">Got their certificate</th><th scope="col">Moved to partial</th><th scope="col" class="hm">New on the list</th>')
            + '</tr></thead>'
            f"<tbody>{rows}</tbody></table></div>"
            + ('<p class="asof">This is the first weekly snapshot. Starting next week, each row also counts the jobs that got their certificate of occupancy, '
               "moved to partial occupancy or joined the list since the week before.</p>" if first else
               '<p class="asof">Each row is that week\'s count. The last three columns compare it with the week before; a blank means no earlier week to compare.</p>'))


def area_table(d, E):
    areas = sorted(d["areas"], key=lambda a: (-a["open"], a["name"]))
    cell = lambda v: f'<td class="z">0</td>' if not v else f"<td>{v:,}</td>"
    row = lambda a: (f'<tr><th scope="row">{E(a["name"])}</th><td class="tot">{a["open"]:,}</td>'
                     + "".join(cell(a[k]) if k in ("b0", "b2") else cell(a[k]).replace("<td", '<td class="hm"', 1).replace('class="hm" class="z"', 'class="hm z"')
                               for k, _, _ in BUCKET_WORDS)
                     + cell(a["partial"]) + "</tr>")
    two = lambda lg, sh: f'<span class="lg">{E(lg)}</span><span class="sh" aria-hidden="true">{E(sh)}</span>'
    thead = ('<thead><tr><th scope="col">' + two("Community area", "Area") + '</th><th scope="col">' + two("Open jobs", "Open") + "</th>"
             + "".join(f'<th scope="col"{"" if k in ("b0", "b2") else " class=hm"}>{two(w, SHORT[k]) if k in SHORT else E(w)}</th>' for k, w, _ in BUCKET_WORDS)
             + '<th scope="col">' + two("Partial occupancy", "Partial") + "</th></tr></thead>")
    tbl = lambda rs, label: (f'<div class="pp-tw" role="region" aria-label="{E(label)}" tabindex="0"><table class="pp-t pp-a">{thead}'
                             f'<tbody>{"".join(row(a) for a in rs)}</tbody></table></div>')
    SHOW = 20
    c = d["city"]
    return (tbl(areas[:SHOW], f"Open big building jobs, the {SHOW} community areas with the most")
            + f'<details class="pp-more"><summary>Show the other {len(areas) - SHOW} community areas</summary>'
            + tbl(areas[SHOW:], "Open big building jobs, the other community areas") + "</details>"
            + '<p class="asof">Open jobs are split by how long ago the City issued the permit; a job with partial occupancy approved is counted in the Partial occupancy column '
            "instead. On a phone the table shows two of the four age groups; the CSV has all of them."
            + (f' {plural(c["noArea"], "job")} had no community area in the City record, so {"it counts" if c["noArea"] == 1 else "they count"} only in the city total.' if c["noArea"] else "")
            + f' <a href="{CSV_NAME}" download>Download every area (CSV)</a>.</p>')


def csv_text(d):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["community_area_number", "community_area", "open_jobs"] + [f"permit_{s.replace(' ', '_').replace('.', '')}" for _, _, s in BUCKET_WORDS]
               + ["partial_occupancy", "new_buildings", "renovations", "as_of"])
    for a in d["areas"]:
        w.writerow([a["n"], a["name"], a["open"]] + [a[k] for k, _, _ in BUCKET_WORDS] + [a["partial"], a["new"], a["reno"], d["asOf"]])
    c = d["city"]
    w.writerow(["", "Chicago (all open jobs, including any with no community area)", c["open"]] + [c[k] for k, _, _ in BUCKET_WORDS]
               + [c["partial"], c["new"], c["reno"], d["asOf"]])
    return buf.getvalue()


def extra_pages(p):
    d = load(p)
    return [(CSV_NAME, csv_text(d))] if d else []


def page_html(p):
    import make_site as M
    E = M.E
    url, rel = M.BASE + p["slug"] + "/", "../"
    d = load(p)
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), ("Free Chicago data", "chicago-data/"), (p["h1"], None)])
    faq = p.get("faq") or []
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    ds_ld = None
    if d:
        ds_ld = {"@context": "https://schema.org", "@type": "Dataset", "name": p["h1"], "description": p["desc"], "url": url,
                 "isAccessibleForFree": True, "creator": {"@type": "Organization", "name": "ProofNotFluff"},
                 "isBasedOn": d["source"]["url"], "spatialCoverage": "Chicago, Illinois", "dateModified": d["asOf"],
                 "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": url + CSV_NAME}]}
    lds = [x for x in (crumb_ld, faq_ld if faq else None, ds_ld) if x]
    head = lambda rb: M.HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=M.SHOP, ld=M.ld_tags(*lds) + CSS,
                                    bodycls=' class="ld-page"', robots=rb, analytics=M.analytics_tag())
    if not d:
        body = f'{crumb}<div class="ld-hero"><h1>{E(p["h1"])}</h1><p class="lede">The first weekly count is on its way.</p></div>'
        return head('<meta name="robots" content="noindex, nofollow">') + body + "</main></body></html>"
    c, src = d["city"], d["source"]
    pulled = M.nice_date(d["asOf"])
    co = {r["year"]: r for r in d["cohorts"]}
    y1, y2 = int(d["asOf"][:4]) - 1, int(d["asOf"][:4]) - 2
    lede = (f'{c["open"]:,} building jobs in Chicago permitted since {src["since"][:4]} with a reported cost of $500,000 or more are still waiting on their certificate of occupancy, the City\'s final sign-off '
            f'before a building can be used. {plural(c["partial"], "of them already has", "of them already have")} temporary or partial occupancy approved. '
            "Here is where they are and how long ago each permit was issued.")
    tiles = ('<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">Open big jobs</div><div class="val">{c["open"]:,}</div><div class="sub">waiting on a certificate of occupancy</div></div>'
             f'<div class="tile"><div class="lab">Permit under 6 months</div><div class="val">{c["b0"]:,}</div><div class="sub">permit issued in the last 6 months</div></div>'
             f'<div class="tile"><div class="lab">Permit 1 to 2 years</div><div class="val">{c["b2"]:,}</div><div class="sub">permit issued 1 to 2 years ago</div></div>'
             f'<div class="tile"><div class="lab">Partial occupancy</div><div class="val">{c["partial"]:,}</div><div class="sub">temporary or part use approved</div></div>'
             f'</div><p class="asof">Week of {E(M.nice_date(d["week"]))}. Counts from City of Chicago permit records, checked {E(pulled)}. Updated every Monday.</p>')
    finish = (f'<p>Big jobs take a long time. Of the new buildings permitted in {y2}, {co[y2]["new"]["share"]}% have their certificate of occupancy today; '
              f'of those permitted in {y1}, {co[y1]["new"]["share"]}%. Recent renovations get theirs sooner: {co[y1]["reno"]["share"]}% of the {y1} renovations have theirs. '
              "So most new buildings permitted in the last year do not have their certificate yet. "
              "The City records cannot say how close any one job is.</p>") if y1 in co and y2 in co else ""
    nxt = p["next"]
    leads_live = any(x.get("slug") == LEADS_SLUG for x in M.PAGES_LIVE)
    nxt_panel = (f'<section class="block" id="next"><div class="pp-one"><div class="cta ld-cta"><div><h2>{E(nxt["title"])}</h2><p>{E(nxt["text"])}</p>'
                 f'<p class="ld-buybtn"><a class="btn" href="{rel}{LEADS_SLUG}/">{E(nxt["button"])}</a></p></div></div></div></section>' if leads_live else "")
    stages = '<dl class="pp-dl">' + "".join(f'<div><dt>{E(t)}</dt><dd>{E(x)}<small>{E(s)}</small></dd></div>' for t, x, s in p["stages"]) + "</dl>"
    mapb = map_block(d, E)
    method = '<section class="block"><h2>How this page is made</h2>' + "".join(f"<p>{E(x)}</p>" for x in p["method"]) + "</section>"
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{lede}</p>'
            '<div class="ld-heroact rl-act"><a class="btn" href="#areas">See every neighborhood</a>'
            + ('<a class="st-btn2" href="#map">Open the map</a>' if mapb else "") + "</div></div>"
            + tiles
            + f'<section class="block" id="timing"><h2>How long a big job takes</h2>{finish}{cohort_block(d, E)}'
            '<p class="asof">Each bar is the share of big jobs from that permit year, on the certificate of occupancy path, that have the certificate today. '
            "The bars also count permits the City now lists as suspended, expired, cancelled or revoked, and some City records are not updated, so older years stay below 100%.</p></section>"
            + (f'<section class="block" id="map"><h2>Open jobs on the map</h2>{mapb}'
               '<script>(function(){var g=document.querySelector("#pmap .gm-a");if(!g||!window.MutationObserver)return;'
               'new MutationObserver(function(){var s=g.querySelector("path.sel");if(s&&s!==g.lastElementChild)g.appendChild(s);})'
               '.observe(g,{subtree:true,attributes:true,attributeFilter:["class"]});})();</script></section>' if mapb else "")
            + f'<section class="block" id="areas"><h2>Every community area</h2>{area_table(d, E)}</section>'
            f'<section class="block" id="stages"><h2>What the stages mean</h2>{stages}</section>'
            f'<section class="block" id="weeks"><h2>Week by week</h2>{history_block(d, E)}</section>'
            f"{nxt_panel}{method}{M.faq_block(faq) if faq else ''}"
            + '<div class="ld-heroact rl-act">'
            + (f'<a class="btn" href="{rel}{LEADS_SLUG}/">{E(nxt["button"])}</a><a class="st-btn2" href="#areas">See every neighborhood</a>' if leads_live
               else '<a class="btn" href="#areas">See every neighborhood</a>') + "</div>")
    foot = (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            f'<p>Source: City of Chicago Data Portal, <a href="{E(src["url"])}">Building Permits dataset</a>, new construction and renovation permits '
            f'issued since {E(M.nice_date(src["since"]))} with a reported cost of ${src["minCost"]:,} or more, pulled {E(pulled)}. The page names no building, '
            "block or business. Counts only: no address, permit number or business name is shown or kept on this page.</p>"
            f'<p>{E(M.CITY_DISCLAIMER["Chicago"])}</p><p>ProofNotFluff is not affiliated with or endorsed by the City of Chicago.</p>'
            "<p>Public information, not legal, tax or financial advice. Certificates of occupancy are issued by the Chicago Department of Buildings; "
            "check with the department about any one building.</p>"
            "<p>Made by ProofNotFluff with AI assistance from public City data. The page counts visits with Cloudflare Web Analytics, which sets no "
            "cookies.</p></div></footer>\n</body></html>")
    return head(robots) + body + foot


def selftest():
    sys.path.insert(0, HERE)
    import make_site as M, tempfile, datetime as dt
    import dp_pipeline_data as P
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("module") == "dp_pipeline"][0]
    N = "PERMIT - NEW CONSTRUCTION"
    r = lambda p, ms, iss, a="6": {"permit_": p, "permit_type": N, "permit_milestone": ms, "issue_date": iss + "T00:00:00.000",
                                  "reported_cost": "900000", "community_area": a, "permit_status": "ACTIVE", "street_name": "PLANTED ST"}
    rows = [r("1", P.CO_REQ, "2026-08-01"), r("2", P.CO_PART, "2025-01-15", "24"), r("3", P.CO_DONE, "2024-04-01"),
            r("4", P.CO_REQ, "2024-02-01"), r("5", P.CO_DONE, "2025-03-01")]
    d, _ = P.build(rows, dt.date(2026, 10, 29), "2026-10-29T07:00:00-05:00", "2026-10-28T06:00:00-05:00", {6: "Lake View", 24: "West Town"})
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, dir=ROOT)
    json.dump(d, tmp); tmp.close()
    try:
        q = dict(spec, data=os.path.relpath(tmp.name, ROOT))
        html = page_html(q)
        ex = extra_pages(q)
    finally:
        os.unlink(tmp.name)
    assert html.count("<h1>") == 1 and "—" not in html and "–" not in html, "one h1, no dashes"
    assert "3 building jobs in Chicago permitted since 2021 with a reported cost of $500,000" in html and "1 of them already has temporary or partial occupancy" in html, "lede counts"
    assert "permitted in 2024, 50%" in html and "permitted in 2025, 50%" in html, "cohort sentence from the counts"
    assert "first weekly snapshot" in html, "first week says moves start next week"
    assert "PLANTED" not in html and "PLANTED" not in json.dumps(d), "no street or address reaches the page"
    assert "weeks before" not in html.lower() and "move-in this week" not in html.lower(), "no unproven timing claim"
    assert (f'href="../{LEADS_SLUG}/"' in html) == any(x.get("slug") == LEADS_SLUG for x in M.PAGES_LIVE), "members' list link only when live"
    assert M.E(M.CITY_DISCLAIMER["Chicago"]) in html and 'id="pmap"' in html and 'tabindex="0"' in html, "disclaimer, map, table"
    assert ex and ex[0][0] == CSV_NAME and "Lake View" in ex[0][1] and ex[0][1].count("\n") == 4, "CSV: header, 2 areas and the city"
    assert isinstance(META["keywords"], str)
    shell = page_html(dict(spec, data="site/datapages/dp_pipeline/none.json"))
    assert "noindex" in shell, "no data: never indexed"
    print("dp_pipeline selftest: ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
