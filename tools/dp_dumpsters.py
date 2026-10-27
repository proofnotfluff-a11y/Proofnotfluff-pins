#!/usr/bin/env python3
"""Chicago Dumpster Permits by Neighborhood: the free daily page /chicago-dumpster-permits/ (site/pages.json kind
"datapage", module dp_dumpsters; tools/make_site.py calls page_html here). Todd's go, Oct 27, 2026, 12:17 pm ("Let's do
them all", coo/PARALLEL_BUILDS.md, research_notes/kimi-2026-10-27-r10.md item 10).

Data: site/datapages/dp_dumpsters/counts.json (tools/dp_dumpsters_pull.py, daily GitHub Action): issued CDOT permits of
type DOT_DMPSTR from the City's Transportation Department Permits dataset (pubx-yq2d), joined to the 77 community areas
by latitude and longitude. Counts only; no name, address or permit record exists in the file, so none can reach the page.
The page links to the public way permit cost calculator (module dp_cdot_fees) for what a permit costs.

Usage: python3 tools/dp_dumpsters.py --selftest
"""
import csv, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = "site/datapages/dp_dumpsters/counts.json"
FEW = 10   # under 10 permits in the year-ago window, a percent change is noise: the page says "too few"
COST_SLUG = "chicago-public-way-permit-costs"

META = {"h1": "Chicago Dumpster Permits by Neighborhood",
        "card": "Where Chicago's dumpster permits are going: issued CDOT permits by community area, the last 90 days against a year ago, month by month. Updated daily.",
        "keywords": ["Chicago dumpster permit", "dumpster permits by neighborhood", "Chicago renovations by neighborhood",
                     "CDOT dumpster permit", "roll-off dumpster Chicago", "junk removal Chicago demand"]}


def load(p=None):
    f = os.path.join(ROOT, (p or {}).get("data", DATA))
    return json.load(open(f, encoding="utf-8")) if os.path.isfile(f) else None


def lastmod(p):
    d = load(p)
    return d["source"]["fetchedAt"][:10] if d else None


def change(now, before):
    """Whole-percent change, or "too few" when the earlier window is under FEW, or "same" within 1%."""
    if before < FEW:
        return None
    return (now / before - 1) * 100


def pct(x):
    if x is None:
        return "too few"
    return "same" if abs(x) < 1 else ("+" if x > 0 else "") + f"{x:.0f}%"


def month_name(ym, short=False):
    import calendar
    y, m = ym.split("-")
    return (calendar.month_abbr if short else calendar.month_name)[int(m)] + ("" if short else f" {y}")


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def full_months(d):
    """Index of the last whole month (the current month is partial until its last day is counted)."""
    return len(d["monthLabels"]) - (2 if d.get("partialMonth") else 1)


CSS = ("<style>"
       ".dd-bars{display:grid;grid-template-columns:repeat(13,minmax(0,1fr));gap:6px;align-items:end;height:180px;margin:12px 0 4px;padding:16px 18px 10px;"
       "background:var(--card);border:1px solid var(--line);border-radius:12px}"
       ".dd-bars div{display:flex;flex-direction:column;justify-content:flex-end;align-items:center;height:100%;gap:4px;min-width:0}"
       ".dd-bars i{flex:none;display:block;width:100%;max-width:40px;border-radius:5px 5px 0 0;background:color-mix(in srgb,var(--accent) 45%,var(--card))}"
       ".dd-bars div.cur i{background:var(--accent)}.dd-bars div.part i{background:repeating-linear-gradient(45deg,color-mix(in srgb,var(--accent) 55%,var(--card)) 0 4px,transparent 4px 7px)}"
       ".dd-bars b{font:600 12px system-ui,sans-serif;color:var(--ink);font-variant-numeric:tabular-nums}"
       ".dd-bars span{font-size:11.5px;color:var(--muted);white-space:nowrap}"
       ".dd-tw{overflow-x:auto;margin:12px 0 0;border:1px solid var(--line);border-radius:12px;background:var(--card)}"
       ".dd-tw:focus-visible{outline:3px solid var(--focus,var(--accent));outline-offset:2px}"
       ".dd-t{width:100%;border-collapse:collapse;font-size:14.5px;min-width:560px}.dd-t th,.dd-t td{padding:9px 12px;border-bottom:1px solid var(--rule);text-align:right;font-variant-numeric:tabular-nums}"
       ".dd-t th:nth-child(2),.dd-t td:nth-child(2){text-align:left}.dd-t thead th{font-size:13px;color:var(--muted);font-weight:700;background:var(--card);position:sticky;top:0}"
       ".dd-t tbody th{font-weight:600;color:var(--ink);text-align:left}.dd-t td.rk{color:var(--muted)}.dd-t tr:last-child td,.dd-t tr:last-child th{border-bottom:0}"
       ".dd-up{color:var(--warn-ink);font-weight:700}"
       ".dd-more{margin:12px 0 0}.dd-more summary{display:flex;align-items:center;min-height:44px;padding:0 16px;border:1px solid var(--line);border-radius:12px;background:var(--card);cursor:pointer;font-weight:600;color:var(--ink)}"
       ".dd-more[open] summary{margin-bottom:8px}"
       ".dd-one .cta{grid-template-columns:1fr}.dd-two{display:grid;gap:16px}@media(min-width:900px){.dd-two{grid-template-columns:1fr 1fr}}"
       ".dd-two .cta{grid-template-columns:1fr;height:100%;align-items:start}.dd-two .cta h2{margin-top:0;text-wrap:balance}"
       ".dd-name{font-size:clamp(20px,2.6vw,26px);line-height:1.15}"
       ".dd-more .dd-tw{margin:0}@media(min-width:600px){.dd-t{table-layout:fixed}.dd-t .c1{width:7%}.dd-t .c2{width:31%}.dd-t th:first-child,.dd-t td.rk{text-align:left;padding-left:16px}.dd-t .c3{width:15%}.dd-t .c4{width:20%}.dd-t .c5{width:13%}.dd-t .c6{width:14%}}"".dd-more summary{box-shadow:none}.dd-more{border:0;background:none;border-radius:0}.dd-one .cta .ld-buybtn{margin-top:18px}#dmap .gm-big small{text-wrap:balance}"".ld-page .ld-tiles{margin-top:22px}.ld-page .ld-heroact .st-btn2{min-height:50px}.ld-page .eyebrow{text-wrap:balance}""#dmap .gm-a path.sel{stroke:var(--ink);stroke-width:4;paint-order:stroke}"".dd-two .cta>div{display:flex;flex-direction:column;height:100%}.dd-two .cta .ld-buybtn{margin-top:auto;padding-top:8px}"
              "@media(max-width:599px){.dd-t{min-width:0}.dd-t th:nth-child(4),.dd-t td:nth-child(4),.dd-t th:nth-child(6),.dd-t td:nth-child(6){display:none}"
       ".dd-t th,.dd-t td{padding:9px 7px}.dd-bars{height:150px;gap:3px;padding:14px 10px 8px}.dd-bars div:not(:nth-child(3n+1)):not(:last-child) span{visibility:hidden}"
       ".dd-bars div:not(.cur) b{visibility:hidden}.dd-bars div:first-child span{align-self:flex-start}}"
       "</style>")


CHANGE_BINS = [("d0", "var(--gmd0)", "Down 25% or more", "-25%+"), ("d1", "var(--gmd1)", "Down 5 to 25%", "-5 to 25%"), ("d2", "var(--gmd2)", "Within 5%", "Same"),
               ("d3", "var(--gmd3)", "Up 5 to 25%", "+5 to 25%"), ("d4", "var(--gmd4)", "Up 25% or more", "+25%+"),
               ("nx", "repeating-linear-gradient(45deg,var(--gmn) 0 4px,var(--dash) 4px 5.5px)", f"Under {FEW} a year ago, too few to compare")]


def change_class(a):
    x = change(a["d90"], a["yr90"])
    if x is None:
        return "nx"
    return "d0" if x <= -25 else "d1" if x <= -5 else "d2" if x < 5 else "d3" if x < 25 else "d4"


def range_legend(cuts):
    if not cuts:
        return [("q0", "var(--gm0)", "Any")]
    out = [("q0", "var(--gm0)", f"Under {cuts[0]:,}", f"<{cuts[0]:,}")]
    for i in range(1, len(cuts)):
        lo, hi = cuts[i - 1], cuts[i] - 1
        out.append((f"q{i}", f"var(--gm{i})", f"{lo:,}" if lo == hi else f"{lo:,} to {hi:,}", f"{lo:,}"))
    out.append((f"q{len(cuts)}", f"var(--gm{len(cuts)})", f"{cuts[-1]:,} or more", f"{cuts[-1]:,}+"))
    return out


def map_block(d, E):
    import geo_map as G
    lm = full_months(d)
    lmn = month_name(d["monthLabels"][lm])
    yr = d["window"]["yr90To"][:4]
    with90 = sum(1 for a in d["areas"] if a["d90"])
    tie = lambda a: sum(1 for b in d["areas"] if b["d90"] == a["d90"]) > 1
    c90 = G.nice_breaks([a["d90"] for a in d["areas"]])
    cm = G.nice_breaks([a["months"][lm] for a in d["areas"]])
    areas = {}
    for a in d["areas"]:
        ch = pct(change(a["d90"], a["yr90"]))
        ch_say = (f"under {FEW} a year ago, too few to compare" if ch == "too few" else "about the same as a year ago" if ch == "same" else f"{ch} vs. a year ago")
        rk = (f'<p>{"Tied " if tie(a) else ""}{ordinal(a["rank"])} of {with90} areas for dumpster permits in the last 90 days (1st has the most).</p>'
              if a["d90"] else "<p>No dumpster permits issued here in the last 90 days.</p>")
        areas[a["n"]] = {"big": {"d90": (f'{a["d90"]:,}', "permits, last 90 days"), "lm": (f'{a["months"][lm]:,}', f"permits in {lmn}"),
                                 "ch": ("Too few" if ch == "too few" else "Same" if ch == "same" else ch, f"against the same 90 days of {yr}")},
                         "say": {"d90": f'{a["d90"]:,} permits in 90 days', "lm": f'{a["months"][lm]:,} permits in {lmn}',
                                 "ch": ch_say + f' ({a["d90"]:,} against {a["yr90"]:,})'},
                         "html": (rk + "<dl>"
                                  f'<dt>Last 90 days</dt><dd>{a["d90"]:,}</dd><dt>Same 90 days, {E(yr)}</dt><dd>{a["yr90"]:,}</dd>'
                                  f'<dt>Change</dt><dd>{E(ch)}</dd><dt>{E(lmn)}</dt><dd>{a["months"][lm]:,}</dd></dl>')}
    metrics = [{"key": "d90", "label": "Last 90 days", "legendTitle": "Dumpster permits issued, last 90 days",
                "cls": {a["n"]: f"q{G.klass(a['d90'], c90)}" for a in d["areas"]}, "legend": range_legend(c90)},
               {"key": "ch", "label": "Change vs. a year ago", "legendTitle": f"Last 90 days against the same 90 days of {yr}",
                "cls": {a["n"]: change_class(a) for a in d["areas"]}, "legend": CHANGE_BINS},
               {"key": "lm", "label": lmn, "legendTitle": f"Dumpster permits issued in {lmn}",
                "cls": {a["n"]: f"q{G.klass(a['months'][lm], cm)}" for a in d["areas"]}, "legend": range_legend(cm)}]
    c = d["city"]
    top3 = sorted([a for a in d["areas"] if a["d90"]], key=lambda a: (-a["d90"], a["name"]))[:3]
    rises = sorted([a for a in d["areas"] if a["yr90"] >= FEW and a["d90"] > a["yr90"]], key=lambda a: (-(a["d90"] - a["yr90"]), a["name"]))[:5]
    hint = ("<h3>Citywide</h3>"
            f'<p class="gm-big"><span>{c["d90"]:,}</span><small>permits issued, last 90 days, {E("about the same as a year ago" if pct(change(c["d90"], c["yr90"])) == "same" else pct(change(c["d90"], c["yr90"])) + " vs. a year ago")}</small></p>'
            '<p>Most permits:</p><ul class="gm-top">'
            + "".join(f'<li><button type="button" data-pick="{a["n"]}">{E(a["name"])}, {a["d90"]:,}</button></li>' for a in top3) + "</ul>"
            + ('<p>Biggest rises vs. a year ago, in permits:</p><ul class="gm-top">'
               + "".join(f'<li><button type="button" data-pick="{a["n"]}">{E(a["name"])}, +{a["d90"] - a["yr90"]:,}</button></li>' for a in rises) + "</ul>" if rises else "")
            + '<p class="gm-hint">Tap or hover any area on the map, or choose one from the list.</p>')
    fig = G.choropleth(areas, metrics, uid="dmap", title="Map of Chicago's 77 community areas, colored by issued dumpster permits",
                       hint=hint, caption=("Community area outlines: City of Chicago, Boundaries - Community Areas. "
                                           "Every number on the map is also in the table below."))
    return G.CSS + fig if fig else ""


def csv_text(d):
    """Every community area by month, plus the city total, for the download."""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    last = (__import__("datetime").date.fromisoformat(d["window"]["to"]) - __import__("datetime").timedelta(days=1)).isoformat()
    labels = [m + f"_to_{last}" if m == d.get("partialMonth") else m for m in d["monthLabels"]]
    w.writerow(["community_area_number", "community_area"] + labels + ["last_90_days", "same_90_days_year_earlier", "rank_last_90_days"])
    for a in d["areas"]:
        w.writerow([a["n"], a["name"]] + a["months"] + [a["d90"], a["yr90"], a["rank"]])
    c = d["city"]
    w.writerow(["", "Chicago (all permits, including those with no community area)"] + c["months"] + [c["d90"], c["yr90"], ""])
    return buf.getvalue()


def extra_pages(p):
    d = load(p)
    return [("chicago-dumpster-permits-by-community-area.csv", csv_text(d))] if d else []


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
                 "isBasedOn": d["source"]["url"], "spatialCoverage": "Chicago, Illinois", "dateModified": d["source"]["fetchedAt"][:10],
                 "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv",
                                   "contentUrl": url + "chicago-dumpster-permits-by-community-area.csv"}]}
    lds = [x for x in (crumb_ld, faq_ld if faq else None, ds_ld) if x]
    head = lambda rb: M.HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=M.SHOP, ld=M.ld_tags(*lds) + CSS,
                                    bodycls=' class="ld-page"', robots=rb, analytics=M.analytics_tag())
    if not d:
        body = f'{crumb}<div class="ld-hero"><h1>{E(p["h1"])}</h1><p class="lede">The first daily count is on its way.</p></div>'
        return head('<meta name="robots" content="noindex, nofollow">') + body + "</main></body></html>"
    c, w, src = d["city"], d["window"], d["source"]
    pulled = M.nice_date(src["fetchedAt"][:10])
    to_day = M.nice_date(w["to"])
    last_day = M.nice_date(__import__("datetime").date.fromisoformat(w["to"]).fromordinal(__import__("datetime").date.fromisoformat(w["to"]).toordinal() - 1).isoformat())
    yr = w["yr90To"][:4]
    ch = change(c["d90"], c["yr90"])
    lm = full_months(d)
    lmn, lmv = month_name(d["monthLabels"][lm]), c["months"][lm]
    lm_yr = c["months"][lm - 12] if lm >= 12 else None
    areas = sorted(d["areas"], key=lambda a: (a["rank"], a["name"]))
    lead = areas[0] if areas and areas[0]["d90"] else None
    tie = bool(lead and len(areas) > 1 and areas[1]["d90"] == lead["d90"])
    with90 = sum(1 for a in d["areas"] if a["d90"])
    lede = (f'CDOT issued {c["d90"]:,} dumpster permits in the 90 days through {E(last_day)}, '
            + (f"{abs(ch):.0f}% {'more' if ch > 0 else 'fewer'} than the same 90 days of {E(yr)}. " if ch is not None and abs(ch) >= 1
               else f"about even with the same 90 days of {E(yr)}. " if ch is not None else "")
            + "Each is a City permit to put a dumpster on a street, alley or other public way, so the count shows where cleanouts, renovations and demolitions are likely going on.")
    tiles = ('<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">Last 90 days</div><div class="val">{c["d90"]:,}</div><div class="sub">dumpster permits issued</div></div>'
             f'<div class="tile"><div class="lab">Vs. a year ago</div><div class="val">{E("About the same" if pct(ch) == "same" else pct(ch).capitalize())}</div><div class="sub">{c["yr90"]:,} in the same 90 days of {E(yr)}</div></div>'
             f'<div class="tile"><div class="lab">{E(lmn)}</div><div class="val">{lmv:,}</div><div class="sub">'
             + (f'{lm_yr:,} in {E(month_name(d["monthLabels"][lm - 12]))}' if lm_yr is not None else "permits in the month") + '</div></div>'
             + (f'<div class="tile"><div class="lab">Most permits</div><div class="val dd-name">{E(lead["name"])}</div><div class="sub">{lead["d90"]:,} in 90 days</div></div>'
                if lead and not tie else "")
             + f'</div><p class="asof">Counts through {E(last_day)}, from City of Chicago permit records pulled {E(pulled)}. Updated every morning.</p>')
    show = d["monthLabels"][-13:]
    vals = c["months"][-13:]
    peak = max(vals) or 1
    part = d.get("partialMonth")
    bars = ('<div class="dd-bars" role="img" aria-label="Dumpster permits issued each month, '
            + E(", ".join(f"{month_name(m)} {v:,}" + (" so far" if m == part else "") for m, v in zip(show, vals))) + '">'
            + "".join(f'<div class="{"part" if m == part else "cur" if i == len(show) - (2 if part else 1) else ""}"><b>{v:,}</b>'
                      f'<i style="height:{max(3, round(v / peak * 78))}%"></i><span>{E(month_name(m, True))}{" " + m[:4] if m.endswith("-01") or i == 0 else ""}</span></div>'
                      for i, (m, v) in enumerate(zip(show, vals)))
            + "</div><p class=\"asof\">Each bar counts the permits CDOT issued in that month."
            + (f" {E(month_name(d['monthLabels'][lm]))}, the last full month, is highlighted; {E(month_name(part))} is striped because it is not over yet." if part else "") + "</p>")
    row = lambda a: (f'<tr><td class="rk">{a["rank"] if a["d90"] else ""}</td><th scope="row">{E(a["name"])}</th><td>{a["d90"]:,}</td><td>{a["yr90"]:,}</td>'
                     f'<td{" class=dd-up" if change(a["d90"], a["yr90"]) is not None and change(a["d90"], a["yr90"]) >= 25 else ""}>{E(pct(change(a["d90"], a["yr90"])))}</td>'
                     f'<td>{a["months"][lm]:,}</td></tr>')
    thead = ('<thead><tr><th scope="col">Rank</th><th scope="col">Community area</th><th scope="col">Last 90 days</th>'
             f'<th scope="col">Same 90 days, {E(yr)}</th><th scope="col">Change</th><th scope="col">{E(month_name(d["monthLabels"][lm], True))} {E(d["monthLabels"][lm][:4])}</th></tr></thead>')
    cols = '<colgroup>' + "".join(f'<col class="c{i}">' for i in range(1, 7)) + '</colgroup>'
    tbl = lambda rs, label: (f'<div class="dd-tw" role="region" aria-label="{E(label)}" tabindex="0"><table class="dd-t">{cols}{thead}'
                             f'<tbody>{"".join(row(a) for a in rs)}</tbody></table></div>')
    SHOW = 20
    table = (tbl(areas[:SHOW], f"Dumpster permits, the {SHOW} community areas with the most")
             + f'<details class="dd-more"><summary>Show the other {len(areas) - SHOW} community areas</summary>'
             + tbl(areas[SHOW:], "Dumpster permits, the other community areas") + "</details>"
             + f'<p class="asof">Rank is by permits in the last 90 days, 1 for the most; areas with the same count share a rank. Change compares the last 90 days with the same 90 days a year earlier, rounded to a whole percent; changes under 1% show as same, rises of 25% or more are in orange, and under {FEW} permits a year earlier show as too few to compare.'
             + ((f' 1 permit from the last 90 days had no map point inside a community area, so it counts only in the city total.' if c["noArea"]["d90"] == 1 else
                f' {c["noArea"]["d90"]:,} permits from the last 90 days had no map point inside a community area, so they count only in the city total.') if c["noArea"]["d90"] else "")
             + (f' A permit with locations in more than one community area counts in each, so the areas add up to more than the city total ({c["multiArea90"]:,} such permits in the last 90 days).' if c.get("multiArea90") else "")
             + f' <a href="chicago-dumpster-permits-by-community-area.csv" download>Download every area by month (CSV)</a>.</p>')
    cost, nxt = p["cost"], p["next"]
    cost_live = any(x.get("slug") == COST_SLUG for x in M.PAGES_LIVE)   # a live page never links to a draft
    cost_panel = (f'<div class="cta ld-cta"><div><h2>{E(cost["title"])}</h2><p>{E(cost["text"])}</p>'
                  f'<p class="ld-buybtn"><a class="btn" href="{rel}{COST_SLUG}/">{E(cost["button"])}</a></p></div></div>' if cost_live else "")
    two = (f'<section class="block" id="next"><div class="{"dd-two" if cost_live else "dd-one"}">' + cost_panel
           + f'<div class="cta ld-cta"><div><h2>{E(nxt["title"])}</h2><p>{E(nxt["text"])}</p>'
           f'<p class="ld-buybtn"><a class="btn" href="{rel}{E(nxt["slug"])}/">{E(nxt["button"])}</a></p></div></div>'
           "</div></section>")
    mapb = map_block(d, E)
    method = '<section class="block"><h2>How this page is made</h2>' + "".join(f"<p>{E(x)}</p>" for x in p["method"]) + "</section>"
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{lede}</p>'
            '<div class="ld-heroact rl-act"><a class="btn" href="#areas">See every neighborhood</a>'
            + ('<a class="st-btn2" href="#map">Open the map</a>' if mapb else "") + "</div></div>"
            + tiles
            + (f'<section class="block" id="map"><h2>Dumpster permits on the map</h2>{mapb}</section>' if mapb else "")
            + f'<section class="block" id="months"><h2>Month by month</h2>{bars}</section>'
            f'<section class="block" id="areas"><h2>Every community area</h2>{table}</section>'
            f"{two}{method}{M.faq_block(faq) if faq else ''}"
            '<p class="rl-act"><a class="btn" href="#areas">See every neighborhood</a>'
            + (f' <a class="st-btn2" href="{rel}{COST_SLUG}/">Price a dumpster permit</a>' if cost_live else
               f' <a class="st-btn2" href="{rel}{E(nxt["slug"])}/">{E(nxt["button"])}</a>') + "</p>")
    foot = (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            f'<p>Source: City of Chicago Data Portal, <a href="{E(src["url"])}">Transportation Department Permits dataset</a>, permits of type '
            f'{E(src["type"])} (dumpster placement in the public way) with an issue date, pulled {E(pulled)}. Each permit is placed in a community area '
            'by the map point the City gives for it. A permit is the City\'s approval to place a dumpster; it does not say a dumpster was set out on '
            'any given day, and a count says nothing about any one building, block or business. Counts only: no name, address or permit record is kept.</p>'
            f'<p>{E(M.CITY_DISCLAIMER["Chicago"])}</p><p>ProofNotFluff is not affiliated with or endorsed by the City of Chicago.</p>'
            "<p>Public information, not legal, tax or financial advice. Permit rules and fees are set by CDOT; check with the agency before you apply.</p>"
            "<p>Made by ProofNotFluff with AI assistance from public City data. The page counts visits with Cloudflare Web Analytics, which sets no "
            "cookies.</p></div></footer>\n</body></html>")
    return head(robots) + body + foot


def selftest():
    sys.path.insert(0, HERE)
    import make_site as M, tempfile, datetime as dt
    import dp_dumpsters_pull as P
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("module") == "dp_dumpsters"][0]
    w = P.windows(dt.date(2026, 10, 27))
    sq = [[[-87.70, 41.90], [-87.60, 41.90], [-87.60, 41.95], [-87.70, 41.95], [-87.70, 41.90]]]
    sq2 = [[[-87.70, 41.80], [-87.60, 41.80], [-87.60, 41.85], [-87.70, 41.85], [-87.70, 41.80]]]
    areas = [(6, "Lake View", sq, (-87.70, 41.90, -87.60, 41.95)), (61, "New City", sq2, (-87.70, 41.80, -87.60, 41.85))]
    import itertools
    ids = itertools.count(1)
    r = lambda day, lat: {"applicationnumber": f"T{next(ids)}", "applicationissueddate": day + "T10:00:00.000", "latitude": lat, "longitude": "-87.65", "applicationstatus": "Closed"}
    rows = ([r("2026-10-1%d" % (i % 10), "41.92") for i in range(24)] + [r("2025-10-1%d" % (i % 10), "41.92") for i in range(20)]
            + [r("2026-09-0%d" % (1 + i % 9), "41.82") for i in range(5)] + [r("2026-09-05", "40.0")])
    rows.append(dict(rows[0], latitude="41.82"))   # one permit at a location in each area: once citywide, once in each
    d = P.build(rows, areas, w, "2026-10-27T07:05:00-0500", {}, {"Closed": len(rows)})
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, dir=ROOT)
    json.dump(d, tmp); tmp.close()
    try:
        q = dict(spec, data=os.path.relpath(tmp.name, ROOT))
        html = page_html(q)
        ex = extra_pages(q)
    finally:
        os.unlink(tmp.name)
    assert html.count("<h1>") == 1 and "—" not in html and "–" not in html, "one h1, no dashes"
    assert "CDOT issued 30 dumpster permits" in html and "counts in each" in html and "+20%" in html, "lede and change (24 against 20)"
    assert ">too few<" in html, "New City: 0 a year earlier is too few"
    assert "1 permit from the last 90 days had" in html, "the point outside every area counts only in the city total"
    assert (f'href="../{COST_SLUG}/"' in html) == any(x.get("slug") == COST_SLUG for x in M.PAGES_LIVE), "the calculator link only once it is live"
    assert "content/dam" not in html, "no link to a fee schedule file we could not open"
    assert 'tabindex="0"' in html and 'role="region"' in html and 'id="dmap"' in html, "table and map"
    assert M.E(M.CITY_DISCLAIMER["Chicago"]) in html, "City disclaimer"
    assert ex and ex[0][0].endswith(".csv") and "Lake View" in ex[0][1] and ex[0][1].count("\n") == 4, "CSV: 2 areas and the city"
    assert "primarycontact" not in json.dumps(d) and "Closed" not in json.dumps(d["areas"]), "counts only"
    shell = page_html(dict(spec, data="site/datapages/dp_dumpsters/none.json"))
    assert "noindex" in shell, "no data: never indexed"
    print("dp_dumpsters selftest: ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
