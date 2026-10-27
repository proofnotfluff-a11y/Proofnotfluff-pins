#!/usr/bin/env python3
"""Chicago Rat Complaints by Neighborhood: the free weekly page (site/pages.json kind "rodents", written by
tools/make_site.py, which calls page_html here). Todd's go, Oct 26, 2026 ("Make all of them",
coo/DECISIONS-2026-10-26.md).

Data: permits/rodents-chicago/weekly.json (tools/rodents_chicago.py, weekly GitHub Action): City of Chicago 311
requests of type "Rodent Baiting/Rat Complaint", counted by community area. Counts only; no address, location or
resident text exists in the file, so none can reach the page. Residents get the City's own way to report rats (311);
pest control companies get the restaurant list and the daily pest seat, which are built from food inspection records,
not from these complaints (the page says so).

Rat Index (Todd, Oct 27, 2026, "Let's do them all", coo/DECISIONS-2026-10-27.md, R10 items 4 and 13): complaints per
1,000 residents and a rank for all 77 community areas (population: site/geo/chicago-community-area-population.json),
the rank against the 30 days before and the same 30 days a year earlier, median days to close, the top risers, a
yearly "rattiest neighborhoods" edition (the 12 months to September 30, out each October), one page per area with its
own numbers, an embeddable badge and a CSV (extra_pages), and the restaurant pest and ventilation index as map metrics
(permits/rodents-chicago/restaurants.json, tools/rodents_restaurants.py), counts only, never a restaurant name.

Usage: python3 tools/rodents_site.py --selftest
"""
import csv, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "permits", "rodents-chicago", "weekly.json")
POP = os.path.join(ROOT, "site", "geo", "chicago-community-area-population.json")
REST = os.path.join(ROOT, "permits", "rodents-chicago", "restaurants.json")
SHARE_FEW = 10   # under 10 restaurant inspections in 12 weeks: no share is shown for an area


def load_json(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def load(p):
    f = os.path.join(ROOT, p.get("data", "permits/rodents-chicago/weekly.json"))
    return json.load(open(f, encoding="utf-8")) if os.path.isfile(f) else None


FEW = 10   # under 10 complaints a year earlier, a percent change is noise: the page says "too few" instead


def area_change(a):
    return "too few" if a["prev30"] < FEW else pct((a["d30"] / a["prev30"] - 1) * 100)   # from the counts, rounded once


def pct(x):
    if x is None:
        return "new"
    return ("+" if x > 0 else "") + f"{x:.0f}%" if abs(x) >= 1 else "same"


def change_words(x):
    if x is None:
        return "with none a year earlier"
    if abs(x) < 1:
        return "about the same as a year earlier"
    return f'{abs(x):.0f}% {"more" if x > 0 else "fewer"} than the same 30 days a year earlier'


CSS = ("<style>.rc-bars{margin:12px 0 8px;padding:16px 18px;background:var(--card);border:1px solid var(--line);border-radius:12px}"
       ".rc-bars figcaption{font-weight:700;color:var(--ink);margin-bottom:6px}"
       ".rc-bar{display:grid;grid-template-columns:minmax(118px,190px) 1fr 52px;gap:2px 10px;align-items:center;margin:9px 0;font-size:14.5px;color:var(--ink2)}"
       ".rc-bar>span{font-weight:600;color:var(--ink)}.rc-bar i{display:block;height:12px;border-radius:6px;background:var(--accent)}"
       ".rc-bar b{text-align:right;color:var(--ink);font-variant-numeric:tabular-nums}.rc-bar small{grid-column:2/-1;font-size:13px;color:var(--muted)}"
       ".rc-wk{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:6px;align-items:end;height:170px;margin:12px 0 4px;padding:16px 18px 10px;"
       "background:var(--card);border:1px solid var(--line);border-radius:12px}"
       ".rc-wk div{display:flex;flex-direction:column;justify-content:flex-end;align-items:center;height:100%;gap:4px}"
       ".rc-wk i{flex:none;display:block;width:100%;max-width:38px;border-radius:5px 5px 0 0;background:var(--accent);opacity:.55}.rc-wk div:last-child i{opacity:1}"
       ".rc-wk b{font:600 12.5px system-ui,sans-serif;color:var(--ink);font-variant-numeric:tabular-nums}"
       ".rc-wk span{font-size:11.5px;color:var(--muted);white-space:nowrap}"
       ".rc-tw{overflow-x:auto;margin:12px 0 0;border:1px solid var(--line);border-radius:12px;background:var(--card)}"
       ".rc-tw:focus-visible{outline:3px solid var(--accent);outline-offset:2px}"
       ".rc-t{width:100%;border-collapse:collapse;font-size:14.5px;min-width:520px}.rc-t th,.rc-t td{padding:9px 12px;border-bottom:1px solid var(--rule);text-align:right;font-variant-numeric:tabular-nums}"
       ".rc-t th:first-child,.rc-t td:first-child{text-align:left}.rc-t thead th{font-size:13px;color:var(--muted);font-weight:700;background:var(--card);position:sticky;top:0}"
       ".rc-t tbody th{font-weight:600;color:var(--ink)}.rc-t tr:last-child td,.rc-t tr:last-child th{border-bottom:0}"
       ".rc-up{color:var(--warn-ink)}.rc-two{display:grid;gap:16px}@media(min-width:900px){.rc-two{grid-template-columns:1fr 1fr}}"
       ".rc-two .cta{grid-template-columns:1fr;height:100%;align-items:start}.rc-two .cta h2{margin-top:0;text-wrap:balance}"
       ".rc-steps{margin:8px 0 0;padding-left:22px}section.block .cta .rc-steps li{margin:6px 0;color:var(--band-text)}.cta .rc-more,.cta .rc-more a{color:var(--band-text)}"
       ".rc-more-t{margin:12px 0 0}.rc-more-t summary{display:flex;align-items:center;min-height:44px;padding:0 16px;border:1px solid var(--line);border-radius:12px;background:var(--card);cursor:pointer;font-weight:600;color:var(--ink)}"
       ".rc-more-t[open] summary{margin-bottom:8px}"
       "@media(max-width:599px){.rc-t{min-width:0}.rc-t th:nth-child(2),.rc-t td:nth-child(2){display:none}.rc-t th,.rc-t td{padding:9px 8px}.rc-wk div:not(:nth-child(3n+1)):not(:last-child) span{visibility:hidden}.rc-wk span{font-size:11.5px}.rc-wk{height:140px}.rc-wk div:not(:last-child) b{visibility:hidden}.rc-bar{grid-template-columns:minmax(96px,130px) 1fr 44px}}</style>")


CHANGE_BINS = [("d0", "var(--gmd0)", "At least 25% fewer", "25%+ fewer"), ("d1", "var(--gmd1)", "5 to 25% fewer", "5 to 25% fewer"), ("d2", "var(--gmd2)", "Within 5%", "Within 5%"),
               ("d3", "var(--gmd3)", "5 to 25% more", "5 to 25% more"), ("d4", "var(--gmd4)", "At least 25% more", "25%+ more"),
               ("nx", "repeating-linear-gradient(45deg,var(--gmn) 0 4px,var(--dash) 4px 5.5px)", "Too few a year ago to compare")]


def change_class(a):
    if a["prev30"] < FEW:
        return "nx"
    x = (a["d30"] / a["prev30"] - 1) * 100
    return "d0" if x <= -25 else "d1" if x <= -5 else "d2" if x < 5 else "d3" if x < 25 else "d4"


def range_legend(cuts):
    """Legend lines for the five count classes: under the first cut, each band, then the last cut or more."""
    if not cuts:
        return [("q0", "var(--gm0)", "Any")]
    out = [("q0", "var(--gm0)", f"Under {cuts[0]:,}", f"<{cuts[0]:,}")]
    for i in range(1, len(cuts)):
        lo, hi = cuts[i - 1], cuts[i] - 1
        out.append((f"q{i}", f"var(--gm{i})", f"{lo:,}" if lo == hi else f"{lo:,} to {hi:,}", f"{lo:,}"))
    out.append((f"q{len(cuts)}", f"var(--gm{len(cuts)})", f"{cuts[-1]:,} or more", f"{cuts[-1]:,}+"))
    return out


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def nn(n, word, many=None):
    """'1 complaint', '239 complaints'."""
    return f"{n:,} {word if n == 1 else (many or word + 's')}"


THE = {"Loop", "Near North Side", "Near West Side", "Near South Side", "Lower West Side"}


def dn(name, cap=False):
    """The name in running text: 'the Loop' (or 'The Loop' at the start of a sentence); other areas as they are."""
    return (("The " if cap else "the ") + name) if name in THE else name


def same_say(x):
    return "about the same" if x == "same" else x


def slug_of(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower().replace("'", "")).strip("-")


def ranks(vals):
    """{area: rank} with 1 the highest value; ties share a place. Values are compared at two decimals, as shown."""
    r = {k: round(v, 2) for k, v in vals.items()}
    return {k: 1 + sum(1 for x in r.values() if x > v) for k, v in r.items()}


def place(k, rk):
    """'12th', or 'tied 12th' when another area shares the place."""
    tied = sum(1 for v in rk.values() if v == rk[k]) > 1
    return ("tied " if tied else "") + ordinal(rk[k])


def move(x):
    return "same" if not x else (f"up {x}" if x > 0 else f"down {-x}")


def rate(n, pop):
    return n / pop * 1000 if pop else 0.0


def share(part, whole):
    return round(part / whole * 100) if whole else None


def index(d, pop, rest=None):
    """Everything the Rat Index shows, from weekly.json, the population file and (when present) restaurants.json.
    Returns None when the files lack what the index needs, so the page falls back to the plain complaint counts."""
    if not pop or "prior30" not in (d["areas"][0] if d.get("areas") else {}) or "edition" not in d:
        return None
    P = {a["n"]: a["population"] for a in pop["areas"]}
    if sorted(P) != sorted(a["n"] for a in d["areas"]):
        return None
    A = {a["n"]: dict(a) for a in d["areas"]}
    for key, src in (("r30", "d30"), ("rPrior", "prior30"), ("rPrev", "prev30"), ("rYear", "year"), ("rYearPrev", "yearPrev")):
        for n, a in A.items():
            a[key] = rate(a[src], P[n])
        rk = ranks({n: a[key] for n, a in A.items()})
        for n, a in A.items():
            a["k" + key[1:]] = rk[n]
    rk30 = {n: a["k30"] for n, a in A.items()}
    rky = {n: a["kYear"] for n, a in A.items()}
    R = {x["n"]: x for x in (rest or {}).get("areas", [])}
    for n, a in A.items():
        a["pop"], a["slug"] = P[n], slug_of(a["name"])
        a["mom"], a["yoy"] = a["kPrior"] - a["k30"], a["kPrev"] - a["k30"]
        a["place"], a["placeYear"] = place(n, rk30), place(n, rky)
        x = R.get(n)
        if x:
            a["insp"], a["pest"], a["vent"], a["rw"] = x["inspections"], x["pest"], x["vent"], x["weeks"]
            ok = x["inspections"] >= SHARE_FEW
            a["pestShare"], a["ventShare"] = (share(x["pest"], x["inspections"]), share(x["vent"], x["inspections"])) if ok else (None, None)
    order = sorted(A.values(), key=lambda a: (a["k30"], a["name"]))
    risers = sorted([a for a in order if a["d30"] >= FEW and a["mom"] > 0], key=lambda a: (-a["mom"], -a["r30"], a["name"]))[:5]
    year = sorted(A.values(), key=lambda a: (a["kYear"], a["name"]))
    c = d["counts"]
    city = {"r30": rate(c["d30"], pop["total"]), "rYear": rate(d["edition"]["total"], pop["total"])}
    if rest:
        rc = rest["counts"]
        city.update({"insp": rc["inspections"], "pest": rc["pest"], "vent": rc["vent"],
                     "pestShare": share(rc["pest"], rc["inspections"]), "ventShare": share(rc["vent"], rc["inspections"])})
    return {"areas": A, "order": order, "risers": risers, "year": year, "city": city, "pop": pop, "rest": rest}


def float_breaks(vals, k=5, nd=1):
    """k-1 rising cut points from the values' quantiles, rounded to nd decimals; classes are value >= cut."""
    v = sorted(x for x in vals if x is not None)
    cuts = []
    for i in range(1, k):
        if not v:
            break
        c = round(v[min(len(v) - 1, int(len(v) * i / k))], nd)
        step = 10 ** -nd
        if cuts and c <= cuts[-1]:
            c = round(cuts[-1] + step, nd)
        cuts.append(c)
    while cuts and v and cuts[-1] > v[-1]:
        cuts.pop()
    return cuts


def cls_of(x, cuts):
    return sum(1 for c in cuts if x >= c)


def float_legend(cuts, fmt, unit=""):
    if not cuts:
        return [("q0", "var(--gm0)", "Any")]
    out = [("q0", "var(--gm0)", f"Under {fmt(cuts[0])}{unit}", f"<{fmt(cuts[0])}{unit}")]
    for i in range(1, len(cuts)):
        out.append((f"q{i}", f"var(--gm{i})", f"{fmt(cuts[i - 1])}{unit} up to {fmt(cuts[i])}{unit}", f"{fmt(cuts[i - 1])}{unit}"))
    out.append((f"q{len(cuts)}", f"var(--gm{len(cuts)})", f"{fmt(cuts[-1])}{unit} or more", f"{fmt(cuts[-1])}{unit}+"))
    return out


FEW_HATCH = ("nx", "repeating-linear-gradient(45deg,var(--gmn) 0 4px,var(--dash) 4px 5.5px)")


def map_block(d, E, ix=None, rel=""):
    """The interactive community area map (Todd, Oct 27, 2026). Every number comes from the same weekly.json as the
    table (and, for the Rat Index metrics, the population and restaurant files); an area with no complaints in either
    window is shown in the lightest class. The first three metrics keep their order (verify/flows/rat-map.json)."""
    import geo_map as G
    w = d["window"]
    more = lambda a: sum(1 for b in d["areas"] if b["d30"] > a["d30"])              # ties share a place
    same = lambda a: sum(1 for b in d["areas"] if b["d30"] == a["d30"]) > 1
    with30 = sum(1 for a in d["areas"] if a["d30"])
    c30, c7 = G.nice_breaks([a["d30"] for a in d["areas"]]), G.nice_breaks([a["d7"] for a in d["areas"]])
    yr = E(w["prevTo"][:4])
    areas = {}
    for a in d["areas"]:
        ch = area_change(a)
        ch_say = "too few a year ago to compare" if ch == "too few" else ("about the same as a year ago" if ch == "same" else f"{ch} on a year ago")
        x = (ix or {}).get("areas", {}).get(a["n"])
        if x:
            rk = f'<p>Rat Index: {x["place"]} of 77, {x["r30"]:.2f} complaints per 1,000 residents in the last 30 days (1st has the most per resident).</p>'
        else:
            rk = (f'<p>{"Tied " if same(a) else ""}{ordinal(more(a) + 1)} of {with30} areas for complaints in the last 30 days (1st has the most).</p>' if a["d30"] else
                  "<p>No rat complaints in the last 30 days.</p>")
        dl = (f'<dt>Last 7 days</dt><dd>{a["d7"]:,}</dd><dt>Last 30 days</dt><dd>{a["d30"]:,}</dd>'
              f'<dt>Same 30 days, {yr}</dt><dd>{a["prev30"]:,}</dd><dt>Change</dt><dd>{E("about the same" if ch == "same" else ch)}</dd>')
        big = {"d30": (f'{a["d30"]:,}', ("complaint" if a["d30"] == 1 else "complaints") + ", last 30 days"),
               "d7": (f'{a["d7"]:,}', ("complaint" if a["d7"] == 1 else "complaints") + ", last 7 days"),
               "ch": (("Too few" if ch == "too few" else "About the same" if ch == "same" else ch),
                      f"under {FEW} a year ago" if ch == "too few" else (f"within 1% of the same 30 days of {yr}" if ch == "same" else f"against the same 30 days of {yr}"))}
        say = {"d30": f'{nn(a["d30"], "complaint")} in 30 days', "d7": f'{nn(a["d7"], "complaint")} in 7 days',
               "ch": ch_say + f' ({a["d30"]:,} against {a["prev30"]:,})'}
        if x:
            dl += f'<dt>Per 1,000 residents</dt><dd>{x["r30"]:.2f}</dd>'
            big["rate"] = (f'{x["r30"]:.2f}', f'per 1,000 residents, {x["place"]} of 77')
            say["rate"] = f'{x["r30"]:.2f} complaints per 1,000 residents, {x["place"]} of 77'
            if "insp" in x:
                ps, vs = x["pestShare"], x["ventShare"]
                dl += (f'<dt>Restaurant inspections, 12 weeks</dt><dd>{x["insp"]:,}</dd>'
                       f'<dt>Citing pests (violation 38)</dt><dd>{x["pest"]:,}{f" ({ps}%)" if ps is not None else ""}</dd>'
                       f'<dt>Citing a hood or ventilation (56)</dt><dd>{x["vent"]:,}{f" ({vs}%)" if vs is not None else ""}</dd>')
                few = f'too few restaurant inspections to give a share ({x["insp"]:,} in 12 weeks)'
                fewsub = ("no restaurant inspections in 12 weeks" if not x["insp"] else
                          f'under {SHARE_FEW} restaurant inspections ({nn(x["insp"], "inspection")} in 12 weeks)')
                big["rp"] = (f"{ps}%", f'of {nn(x["insp"], "restaurant inspection")} cited pests') if ps is not None else ("Too few", fewsub)
                big["rv"] = (f"{vs}%", f'of {nn(x["insp"], "restaurant inspection")} cited a hood or ventilation') if vs is not None else ("Too few", fewsub)
                say["rp"] = f'{ps}% of restaurant inspections cited pests ({x["pest"]:,} of {x["insp"]:,})' if ps is not None else few
                say["rv"] = f'{vs}% of restaurant inspections cited a hood or ventilation ({x["vent"]:,} of {x["insp"]:,})' if vs is not None else few
            dl += ""
        link = f'<p><a href="{rel}{x["slug"]}/">Open the {E(a["name"])} page</a></p>' if x else ""
        areas[a["n"]] = {"big": big, "say": say, "html": rk + "<dl>" + dl + "</dl>" + link}
    metrics = [{"key": "d30", "label": "Last 30 days", "legendTitle": "Rat complaints, last 30 days",
                "cls": {a["n"]: f"q{G.klass(a['d30'], c30)}" for a in d["areas"]}, "legend": range_legend(c30)},
               {"key": "d7", "label": "Last 7 days", "legendTitle": "Rat complaints, last 7 days",
                "cls": {a["n"]: f"q{G.klass(a['d7'], c7)}" for a in d["areas"]}, "legend": range_legend(c7)},
               {"key": "ch", "label": "Change on a year ago", "legendTitle": f"Last 30 days against the same 30 days of {yr}",
                "cls": {a["n"]: change_class(a) for a in d["areas"]}, "legend": CHANGE_BINS}]
    if ix:
        A = ix["areas"]
        cr = float_breaks([a["r30"] for a in A.values()], nd=1)
        metrics.append({"key": "rate", "label": "Per 1,000 residents", "legendTitle": "Rat complaints per 1,000 residents, last 30 days",
                        "cls": {n: f"q{cls_of(round(a['r30'], 2), cr)}" for n, a in A.items()}, "legend": float_legend(cr, lambda v: f"{v:.1f}")})
        if ix.get("rest"):
            for key, fld, label, title in (("rp", "pestShare", "Restaurant pests", "Share of restaurant inspections citing pests (violation 38), 12 weeks"),
                                           ("rv", "ventShare", "Restaurant hoods", "Share of restaurant inspections citing a hood or ventilation (violation 56), 12 weeks")):
                cs = float_breaks([a.get(fld) for a in A.values()], nd=0)
                cs = [int(c) for c in cs]
                metrics.append({"key": key, "label": label, "legendTitle": title,
                                "cls": {n: ("nx" if a.get(fld) is None else f"q{cls_of(a[fld], cs)}") for n, a in A.items()},
                                "legend": float_legend(cs, lambda v: f"{v:.0f}", "%") + [FEW_HATCH + (f"Under {SHARE_FEW} restaurant inspections",)]})
    c = d["counts"]
    top3 = sorted([a for a in d["areas"] if a["d30"]], key=lambda a: (-a["d30"], a["name"]))[:3]
    rises = sorted([a for a in d["areas"] if a["prev30"] >= FEW and a["d30"] > a["prev30"]],
                   key=lambda a: (-(a["d30"] - a["prev30"]), a["name"]))[:5]
    top_rate = ix["order"][:3] if ix else []
    hint = ('<h3>Citywide</h3>'
            f'<p class="gm-big"><span>{c["d30"]:,}</span><small>complaints, last 30 days, {E(same_say(pct(c["change"])))} on a year ago</small></p>'
            + ('<p>Most complaints per resident:</p><ul class="gm-top">'
               + "".join(f'<li><button type="button" data-pick="{a["n"]}">{E(a["name"])}, {a["r30"]:.2f} per 1,000</button></li>' for a in top_rate) + '</ul>'
               if top_rate else "")
            + ('<div class="ri-hx">' if top_rate else "") + '<p>Most complaints:</p><ul class="gm-top">'
            + "".join(f'<li><button type="button" data-pick="{a["n"]}">{E(a["name"])}, {a["d30"]:,}</button></li>' for a in top3) + '</ul>'
            + ('<p>Biggest rises in complaints on a year ago:</p><ul class="gm-top">'
               + "".join(f'<li><button type="button" data-pick="{a["n"]}">{E(a["name"])}, {a["d30"] - a["prev30"]:,} more</button></li>' for a in rises) + '</ul>' if rises else "")
            + ('</div>' if top_rate else "")
            + '<p class="gm-hint">Tap or hover any area on the map, or choose one from the list.</p>')
    cap = ("Community area outlines: City of Chicago, Boundaries - Community Areas. "
           + ("Residents: City of Chicago, ACS 5 Year Data by Community Area. Restaurant shares: City of Chicago Food Inspections. " if ix else "")
           + "Every number on the map is also in the tables below.")
    fig = G.choropleth(areas, metrics, uid="ratmap", title="Map of Chicago's 77 community areas, colored by rat complaints to 311",
                       hint=hint, caption=cap)
    return G.CSS + fig if fig else ""


IX_CSS = ("<style>.ri-mv{white-space:nowrap}.ri-up{color:var(--warn-ink);font-weight:600}.ri-dn{color:var(--teal-ink)}"
          ".rc-t td a,.rc-t th a{color:var(--ink);text-underline-offset:3px}.rc-t td.ri-rk{text-align:left;font-weight:700;color:var(--ink)}"
          ".ri-list{list-style:none;margin:10px 0 0;padding:0;display:grid;gap:8px}"
          ".ri-list li{display:grid;grid-template-columns:2.4em 1fr auto;gap:4px 10px;align-items:baseline;padding:12px 14px;background:var(--card);border:1px solid var(--line);border-radius:12px}"
          ".ri-list b{font:700 18px Poppins,system-ui,sans-serif;color:var(--accent-text);font-variant-numeric:tabular-nums}"
          ".ri-list a{font-weight:700;color:var(--ink);text-underline-offset:3px}.ri-list span{color:var(--ink2);font-size:14.5px;text-align:right;font-variant-numeric:tabular-nums}"
          ".ri-list small{grid-column:2/-1;color:var(--muted);font-size:13px}"
          ".ri-ed{padding:18px;border:1px solid var(--line);border-radius:14px;background:var(--canvas2)}"
          ".ri-ed .eyebrow{margin:0 0 4px}.ri-ed h2{margin-top:0}"
          ".ri-embed{display:grid;gap:14px;padding:18px;border:1px solid var(--line);border-radius:14px;background:var(--card)}"
          "@media(min-width:900px){.ri-embed{grid-template-columns:minmax(0,360px) 1fr;align-items:start}}"
          ".ri-embed img{display:block;max-width:100%;height:auto;border-radius:12px}.ri-embed label{display:block;font-weight:700;color:var(--ink);margin:0 0 6px}"
          ".ri-embed select{min-height:44px;width:100%;max-width:360px;font:inherit;padding:0 10px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink)}"
          ".ri-embed textarea{display:block;width:100%;box-sizing:border-box;min-height:118px;padding:10px 12px;font:13px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:var(--ink);"
          "background:var(--canvas2);border:1px solid var(--line);border-radius:10px;resize:vertical;overflow-wrap:anywhere;word-break:normal}"
          ".ri-embed textarea:focus-visible,.ri-embed select:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
          ".ri-copy{margin-top:10px;border:0;cursor:pointer;font:inherit;font-weight:700;min-height:46px}.ri-ok{min-height:1.4em;margin:6px 0 0;color:var(--teal-ink);font-weight:600}"
          ".ri-dl{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 0}"
          ".ri-near{display:flex;flex-wrap:wrap;gap:8px;list-style:none;margin:10px 0 0;padding:0}.ri-near a{display:inline-flex;align-items:center;min-height:44px;padding:0 14px;"
          "border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink);font-weight:600;text-decoration:none}.ri-near a:hover{border-color:var(--accent)}"
          ".ri-rest{display:grid;gap:12px}@media(min-width:700px){.ri-rest{grid-template-columns:repeat(3,minmax(0,1fr))}}"
          "@media(max-width:599px){.ri-t th:nth-child(4),.ri-t td:nth-child(4),.ri-t th:nth-child(5),.ri-t td:nth-child(5),.ri-t th:nth-child(6),.ri-t td:nth-child(6),"
          ".ri-t th:nth-child(9),.ri-t td:nth-child(9){display:none}.ri-list li{grid-template-columns:2em 1fr}.ri-list span{grid-column:2;text-align:left}}"
          ".ri-t th:nth-child(2),.ri-t td:nth-child(2){text-align:left}.ri-t td:first-child{width:3.2em}"
          "@media(min-width:900px){.ri-ed .ri-list{grid-template-columns:1fr 1fr;grid-auto-flow:column;grid-template-rows:repeat(5,auto)}}"
          ".ri-nw{white-space:nowrap}.ri-page-how a{display:inline-flex;align-items:center;min-height:44px}"
          ".rc-more-t{border:0;background:none;border-radius:0}"
          ".ri-end{display:flex;flex-wrap:wrap;gap:12px 20px}"
          ".ld-heroact .btn,.ld-heroact .st-btn2,.ri-end .btn,.ri-end .st-btn2{min-height:48px;box-sizing:border-box;display:inline-flex;align-items:center;justify-content:center;padding-top:0;padding-bottom:0}"
          ".ri-how{margin:8px 0 0}.ri-how summary{cursor:pointer;font-weight:600;color:var(--ink);min-height:44px;display:flex;align-items:center}.ri-how p{margin:4px 0 0}"
          ".ri-span{display:block;font-weight:400;color:var(--muted);font-size:13px;margin-top:2px}.ri-rank{max-width:760px}"
          ".ri-embed textarea{height:calc(18.85px * 7 + 22px)}"
          ".rc-two .cta>div{display:flex;flex-direction:column;height:100%}.rc-two .ld-buybtn{margin-top:auto;padding-top:16px}"
          "@media(prefers-color-scheme:dark){:root:not([data-theme=light]) .rc-two .cta{background:var(--card);border:1px solid var(--line);border-top:3px solid var(--accent)}"
          ":root:not([data-theme=light]) .ri-embed img{box-shadow:0 0 0 1px var(--accent)}}"
          ":root[data-theme=dark] .rc-two .cta{background:var(--card);border:1px solid var(--line);border-top:3px solid var(--accent)}:root[data-theme=dark] .ri-embed img{box-shadow:0 0 0 1px var(--accent)}"
          "@media(max-width:599px){.ld-heroact a,.ri-end a{flex:1 1 100%}.ri-embed textarea{height:calc(18.85px * 12 + 22px)}"
          ".ri-t th:nth-child(8),.ri-t td:nth-child(8){display:none}.ri-t th:nth-child(2),.ri-t td:nth-child(2){white-space:nowrap;min-width:120px}"
          ".rc-bar{grid-template-columns:1fr auto}.rc-bar>span{grid-column:1;grid-row:1}.rc-bar b{grid-column:2;grid-row:1}.rc-bar i{grid-column:1/-1;grid-row:2}.rc-bar small{grid-column:1/-1;grid-row:3}"
          ".ri-ed{border:0;padding:0;background:transparent}}"
          ".ld-hero+.ld-tiles{margin-top:22px}.ri-hs{display:none}"
          ".ri-act{display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;margin-top:10px}.ri-act .ri-copy{margin:0}.ri-act .ri-ok{margin:0;min-height:0}"
          "@media(min-width:900px){.ri-embed{align-items:center}.ri-t th:nth-child(2),.ri-t td:nth-child(2){white-space:nowrap;min-width:190px}"
          "#risers .ri-list{grid-template-columns:1fr 1fr}#risers .ri-list,#risers .ri-list li,.ri-ed .ri-list li{max-width:none}}"
          "@media(max-width:599px){.ri-hl{display:none}.ri-hs{display:inline}.ri-t tbody th a{display:block;padding:12px 0}.ri-hx{display:none}}"
          "@media(prefers-color-scheme:dark){:root:not([data-theme=light]) .rc-wk i{opacity:1;background:#b8664f}:root:not([data-theme=light]) .rc-wk div:last-child i{background:var(--accent)}}"
          ":root[data-theme=dark] .rc-wk i{opacity:1;background:#b8664f}:root[data-theme=dark] .rc-wk div:last-child i{background:var(--accent)}"
          "main ul.ri-near li a{padding:0 14px}"
          ".ri-jump{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 0;padding:2px}"
          ".ri-jump a{flex:none;display:inline-flex;align-items:center;min-height:44px;padding:0 14px;border:1px solid var(--line);border-radius:999px;background:var(--card);color:var(--ink);font-weight:600;font-size:14.5px;text-decoration:none}"
          ".ri-jump a:hover{border-color:var(--accent)}.ri-jump a:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
          ".ri-t{min-width:640px}@media(max-width:599px){.ri-t{min-width:0}.ri-t th,.ri-t td{padding:9px 6px}.ri-t thead th{font-size:12px}.ri-t th:nth-child(2),.ri-t td:nth-child(2){display:table-cell}}</style>")

COPY_JS = ("<script>document.querySelectorAll('.ri-copy').forEach(function(b){b.addEventListener('click',function(){"
           "var t=document.getElementById(b.dataset.for),ok=b.parentNode.querySelector('.ri-ok');"
           "function done(m){if(ok){ok.textContent=m;}}"
           "if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t.value).then(function(){done('Copied. Paste it into your page.');},function(){t.focus();t.select();done('Selected. Press Ctrl+C or Cmd+C to copy.');});}"
           "else{t.focus();t.select();try{document.execCommand('copy');done('Copied. Paste it into your page.');}catch(e){done('Selected. Press Ctrl+C or Cmd+C to copy.');}}});});</script>")

BADGE_W, BADGE_H = 340, 104


def badge_alt(name):
    return f"Chicago Rat Index badge for {name}: its rank for the last 30 days among the city's 77 community areas, updated weekly, from City of Chicago 311 data, by ProofNotFluff"


def badge_svg(a, d):
    """A small, self-contained, accessible SVG badge for one area (fixed colors: it is shown on other people's sites)."""
    to = d["window"]["to"]
    import make_site as M
    when = M.nice_date(to)
    line = f'{a["place"][:1].upper() + a["place"][1:]} of 77 areas · {a["r30"]:.2f} per 1,000 residents'
    sub = f"311 rat complaints, 30 days to {when}"
    title = f'Chicago Rat Index: {a["name"]}, {a["place"]} of 77'
    desc = (f'{dn(a["name"], True)} ranks {a["place"]} of Chicago\'s 77 community areas for rat complaints to 311 per 1,000 residents: '
            f'{a["r30"]:.2f} in the 30 days to {when} ({nn(a["d30"], "complaint")}). By ProofNotFluff, from City of Chicago data.')
    e = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    font = "system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{BADGE_W}" height="{BADGE_H}" viewBox="0 0 {BADGE_W} {BADGE_H}" role="img" aria-labelledby="t d">'
            f'<title id="t">{e(title)}</title><desc id="d">{e(desc)}</desc>'
            f'<rect width="{BADGE_W}" height="{BADGE_H}" rx="12" fill="#1d2433"/><rect x="0" y="0" width="6" height="{BADGE_H}" rx="3" fill="#c8502f"/>'
            f'<g font-family="{font}">'
            f'<text x="20" y="24" font-size="11" font-weight="700" letter-spacing="1.2" fill="#e88062">CHICAGO RAT INDEX</text>'
            f'<text x="{BADGE_W - 14}" y="24" font-size="11" fill="#b9c0ce" text-anchor="end">proofnotfluff.com</text>'
            f'<text x="20" y="51" font-size="20" font-weight="700" fill="#ffffff">{e(a["name"])}</text>'
            f'<text x="20" y="73" font-size="13.5" fill="#e8ebf1">{e(line)}</text>'
            f'<text x="20" y="92" font-size="11.5" fill="#b9c0ce">{e(sub)}</text></g></svg>\n')


def embed_code(a):
    import make_site as M
    u = M.BASE + "chicago-rat-complaints/" + a["slug"] + "/"
    return (f'<a href="{u}" title="Chicago Rat Index: {a["name"]}">'
            f'<img src="{u}badge.svg" width="{BADGE_W}" height="{BADGE_H}" alt="{badge_alt(a["name"])}" loading="lazy"></a>')


def mv_cell(x):
    return f'<span class="ri-mv{" ri-up" if x > 0 else " ri-dn" if x < 0 else ""}">{move(x)}</span>'


def days_txt(x):
    return "too few" if x is None else f"{x:.1f}"


def index_table(ix, d, E, rel):
    yr = E(d["window"]["prevTo"][:4])
    thead = ('<thead><tr><th scope="col">Rank</th><th scope="col">Community area</th><th scope="col">Per 1,000 residents</th>'
             '<th scope="col">7 days</th><th scope="col">30 days</th><th scope="col">Change on a year ago</th>'
             '<th scope="col"><span class="ri-hl">Rank move, against 30 days before</span><span class="ri-hs">Move, 30 days</span></th>'
             '<th scope="col"><span class="ri-hl">Rank move, against a year ago</span><span class="ri-hs">Move, 1 year</span></th>'
             '<th scope="col">Median days to close</th></tr></thead>')
    row = lambda a: (f'<tr><td class="ri-rk">{a["k30"]}</td><th scope="row"><a href="{rel}{a["slug"]}/">{E(a["name"])}</a></th><td>{a["r30"]:.2f}</td>'
                     f'<td>{a["d7"]:,}</td><td>{a["d30"]:,}</td>'
                     f'<td{" class=rc-up" if a["prev30"] >= FEW and a["d30"] >= a["prev30"] * 1.25 else ""}>{E("about the same" if area_change(a) == "same" else area_change(a))}</td>'
                     f'<td>{mv_cell(a["mom"])}</td><td>{mv_cell(a["yoy"])}</td><td>{days_txt(a.get("medClose"))}</td></tr>')
    tbl = lambda rs, label: (f'<div class="rc-tw" role="region" aria-label="{E(label)}" tabindex="0"><table class="rc-t ri-t">{thead}'
                             f'<tbody>{"".join(row(a) for a in rs)}</tbody></table></div>')
    SHOW = 20
    o = ix["order"]
    c = d["counts"]
    return (tbl(o[:SHOW], f"Chicago Rat Index, ranks 1 to {SHOW}")
            + f'<details class="rc-more-t"><summary>Show the other {len(o) - SHOW} community areas</summary>'
            + tbl(o[SHOW:], "Chicago Rat Index, the other community areas") + '</details>'
            + '<p class="asof">Rank 1 has the most rat complaints per 1,000 residents in the last 30 days. "Up 3" means an area moved 3 places toward 1st.</p>'
            '<details class="ri-how"><summary>How the ranks are counted</summary><p class="asof">Tied areas share a rank. '
            f'Change compares the last 30 days with the same 30 days of {yr}, rounded to a whole '
            f'percent; within 1% shows as about the same, and under {FEW} complaints a year earlier as too few. Median days to close is for the requests the '
            f'City closed in the last 30 days, from each request\'s created and closed dates; under 5 closed shows as too few.'
            + (f' {c["noArea30"]:,} of the last 30 days\' complaints had no community area on the record and count only in the city total.' if c.get("noArea30") else "")
            + '</p></details>')


def risers_block(ix, E, rel):
    rs = ix["risers"]
    if not rs:
        return "<p>No community area with at least 10 complaints moved up the rank against the 30 days before.</p>"
    return ('<ol class="ri-list">' + "".join(
        f'<li><b>+{a["mom"]}</b><a href="{rel}{a["slug"]}/">{E(a["name"])}</a><span>{ordinal(a["kPrior"])} to {ordinal(a["k30"])}</span>'
        f'<small>Up {a["mom"]} places: {a["r30"]:.2f} per 1,000 residents ({nn(a["d30"], "complaint")}), against {a["rPrior"]:.2f} ({a["prior30"]:,}) in the 30 days before</small></li>'
        for a in rs) + '</ol>')


def edition_block(ix, d, E, rel, M):
    ed = d["edition"]
    yrs = ix["year"][:10]
    x = (ed["total"] / ed["prevTotal"] - 1) * 100 if ed["prevTotal"] else None
    ch = ("about the same as the 12 months before" if x is not None and abs(x) < 1 else
          f'{abs(x):.0f}% {"more" if x > 0 else "fewer"} than the 12 months before' if x is not None else "with nothing to compare a year before")
    head = (f'<p class="eyebrow">{ed["year"]} edition, from our own count of City 311 records</p>'
            f'<h2>The rattiest Chicago neighborhoods, {ed["year"]}</h2>'
            f'<p>Ranked by rat complaints to 311 per 1,000 residents in the 12 months from {E(M.nice_date(ed["from"]))} to {E(M.nice_date(ed["to"]))}: '
            f'{ed["total"]:,} complaints citywide, {E(ch)} '
            f'({ed["prevTotal"]:,}). A new edition comes out each October, when pest control companies publish their national rattiest cities lists. '
            'It ranks complaints, which also reflect how often people in an area call 311; it is not a count of rats.</p>')
    items = "".join(
        f'<li><b>{a["kYear"]}</b><a href="{rel}{a["slug"]}/">{E(a["name"])}</a><span>{a["rYear"]:.2f} per 1,000 a year</span>'
        f'<small>{a["year"]:,} complaints; {ordinal(a["kYearPrev"])} in the {ed["year"] - 1} edition</small></li>' for a in yrs)
    return f'<section class="block ri-ed" id="rattiest">{head}<ol class="ri-list">{items}</ol></section>'


def rest_block(ix, E, M):
    rest, city = ix["rest"], ix["city"]
    t38 = rest["codes"]["pest"]["title"].capitalize()
    t56 = rest["codes"]["vent"]["title"].capitalize()
    w = rest["window"]
    weeks = rest["weeks"]
    row = lambda x: (f'<tr><th scope="row">{E(M.nice_date(x["from"]).rsplit(",", 1)[0])} to {E(M.nice_date(x["to"]).rsplit(",", 1)[0])}</th>'
                     f'<td>{x["inspections"]:,}</td><td>{x["pest"]:,}</td><td>{share(x["pest"], x["inspections"]) if x["inspections"] else 0}%</td>'
                     f'<td>{x["vent"]:,}</td><td>{share(x["vent"], x["inspections"]) if x["inspections"] else 0}%</td></tr>')
    table = ('<details class="rc-more-t"><summary>Show the 12 weeks, citywide</summary>'
             '<div class="rc-tw" role="region" aria-label="Restaurant inspections citing pests and hoods, week by week" tabindex="0"><table class="rc-t">'
             '<thead><tr><th scope="col">Week</th><th scope="col">Inspections</th><th scope="col">Citing pests</th><th scope="col">Share</th>'
             '<th scope="col">Citing a hood or ventilation</th><th scope="col">Share</th></tr></thead><tbody>'
             + "".join(row(x) for x in reversed(weeks)) + '</tbody></table></div></details>')
    tiles = ('<div class="ri-rest">'
             f'<div class="tile"><div class="lab">Restaurant inspections</div><div class="val">{city["insp"]:,}</div><div class="sub">in the 12 weeks to {E(M.nice_date(w["to"]))}</div></div>'
             f'<div class="tile"><div class="lab">Cited pests</div><div class="val">{city["pestShare"]}%</div><div class="sub">{city["pest"]:,} inspections cited violation 38</div></div>'
             f'<div class="tile"><div class="lab">Cited a hood or ventilation</div><div class="val">{city["ventShare"]}%</div><div class="sub">{city["vent"]:,} cited violation 56 with a hood or vent note</div></div></div>')
    return ('<section class="block" id="restaurants"><h2>Restaurant pest and hood citations</h2>'
            f'<p>The share of City food inspections of restaurants that cited pests or a kitchen hood, from {E(M.nice_date(w["from"]))} to {E(M.nice_date(w["to"]))}. '
            'Pick Restaurant pests or Restaurant hoods on the map to see it by community area. These are counts only: this page never names a restaurant.</p>'
            f'{tiles}{table}'
            '<details class="ri-how"><summary>How these are counted</summary>'
            f'<p class="asof">Pests: the inspection cited violation 38, which the City titles "{E(t38)}". Hood or ventilation: it cited violation 56, '
            f'"{E(t56)}", with an inspector note naming a hood, filter, exhaust, ventilation, vent or fan (56 also covers lighting, which does not count). '
            'Inspections are of places whose facility type names a restaurant, with a result of pass, pass with conditions or fail. '
            f'A place inspected twice counts twice. Areas with under {SHARE_FEW} inspections in 12 weeks show as too few. '
            'A result reflects what the inspector found at the time of that inspection, and the City notes its dataset may contain duplicates.</p></details></section>')


def embed_block(ix, E, rel, one=None):
    """The badge and its copy-paste code: one area on its own page, or a pick list of all 77 on the main page."""
    a = one or ix["order"][0]
    pick = ""
    if not one:
        opts = "".join(f'<option value="{x["slug"]}"{" selected" if x is a else ""}>{E(x["name"])}</option>'
                       for x in sorted(ix["areas"].values(), key=lambda x: x["name"]))
        pick = f'<label for="ri-area">Community area</label><select id="ri-area">{opts}</select>'
    codes = {x["slug"]: embed_code(x) for x in ix["areas"].values()} if not one else {}
    js = ""
    if not one:
        js = ('<script type="application/json" id="ri-codes">' + json.dumps(codes, ensure_ascii=False).replace("</", "<\\/") + '</script>'
              "<script>(function(){var s=document.getElementById('ri-area'),t=document.getElementById('ri-code'),i=document.getElementById('ri-img'),"
              "c=JSON.parse(document.getElementById('ri-codes').textContent),ok=document.querySelector('#embed .ri-ok');"
              f"s.addEventListener('change',function(){{t.value=c[s.value];i.src='{rel}'+s.value+'/badge.svg';"
              "i.alt='Chicago Rat Index badge for '+s.options[s.selectedIndex].text;if(ok)ok.textContent='';});})();</script>")
    return ('<section class="block" id="embed"><h2>Put the Rat Index on your site</h2>'
            + (f'<p>A free badge for {E(dn(one["name"]))}: copy the code into your website. ' if one else '<p>A free badge for any community area: pick one, then copy the code into your website. ')
            + 'The badge updates by itself every Monday and links back to the numbers. '
            'Pest control companies, property managers and local news sites are welcome to use it.</p>'
            '<div class="ri-embed"><div>' + pick
            + f'<img id="ri-img" src="{rel}{a["slug"]}/badge.svg" width="{BADGE_W}" height="{BADGE_H}" alt="Chicago Rat Index badge for {E(a["name"])}"'
            + (' style="margin-top:12px"' if pick else "") + '></div>'
            f'<div><label for="ri-code">Code to paste</label><textarea id="ri-code" readonly spellcheck="false">{E(embed_code(a))}</textarea>'
            '<div class="ri-act"><button type="button" class="btn ri-copy" data-for="ri-code">Copy the code</button><p class="ri-ok" role="status"></p></div></div></div></section>'
            + js)


CSV_COLS = ["rank", "community_area_number", "community_area", "residents", "complaints_7_days", "complaints_30_days", "per_1000_residents_30_days",
            "complaints_30_days_before", "rank_30_days_before", "complaints_same_30_days_year_ago", "rank_year_ago", "change_on_year_ago_pct",
            "closed_last_30_days", "median_days_to_close", "edition", "edition_complaints", "edition_per_1000", "edition_rank", "previous_edition_rank",
            "restaurant_inspections_12_weeks", "restaurant_pest_citations", "restaurant_pest_share_pct", "restaurant_hood_citations", "restaurant_hood_share_pct",
            "window_from", "window_to", "source"]


def csv_text(rows):
    b = io.StringIO()
    wr = csv.writer(b, lineterminator="\n")
    for r in rows:
        wr.writerow(r)
    return b.getvalue()


def index_csv(ix, d):
    w, ed = d["window"], d["edition"]
    src = "City of Chicago 311 Service Requests v6vf-nfxy; ACS 5 Year Data by Community Area t68z-cikk; Food Inspections 4ijn-s7e5; by ProofNotFluff"
    rows = [CSV_COLS]
    for a in ix["order"]:
        rows.append([a["k30"], a["n"], a["name"], a["pop"], a["d7"], a["d30"], f'{a["r30"]:.2f}', a["prior30"], a["kPrior"], a["prev30"], a["kPrev"],
                     "" if a["change"] is None or a["prev30"] < FEW else f'{a["d30"] / a["prev30"] * 100 - 100:.1f}', a.get("closed30", ""),
                     "" if a.get("medClose") is None else a["medClose"], ed["year"], a["year"], f'{a["rYear"]:.2f}', a["kYear"], a["kYearPrev"],
                     a.get("insp", ""), a.get("pest", ""), "" if a.get("pestShare") is None else a["pestShare"],
                     a.get("vent", ""), "" if a.get("ventShare") is None else a["ventShare"], w["from30"], w["to"], src])
    return csv_text(rows)


def area_csv(a, d, rest):
    rows = [["week_from", "week_to", "community_area", "rat_complaints", "restaurant_inspections", "restaurant_pest_citations", "restaurant_hood_citations"]]
    rw = a.get("rw") or [[None] * 3] * 12
    rweeks = (rest or {}).get("weeks") or [{}] * 12
    for i, x in enumerate(d["weeks"]):
        same = rweeks[i].get("from") == x["from"] if rweeks[i] else False
        r = rw[i] if same else [None, None, None]
        rows.append([x["from"], x["to"], a["name"], a["w12"][i]] + ["" if v is None else v for v in r])
    return csv_text(rows)


def page_parts(p, d, M):
    """The pieces shared by the main page and the area pages."""
    E = M.E
    src = d["source"]
    pulled = M.nice_date(src["fetchedAt"][:10])
    resident, vendor = p["resident"], p["vendor"]

    def two(rel):
        return ('<section class="block" id="help"><div class="rc-two">'
                f'<div class="cta ld-cta"><div><h2>{E(resident["title"])}</h2>'
                + '<ol class="rc-steps">' + "".join(f"<li>{E(t)}</li>" for t in resident["steps"]) + '</ol>'
                + (f'<p class="rc-more"><a href="{E(resident["more"][1])}" rel="noopener">{E(resident["more"][0])}</a>, City of Chicago</p>' if resident.get("more") else "")
                + f'<p class="ld-buybtn"><a class="btn" href="{E(resident["url"])}" rel="noopener">{E(resident["button"])}</a></p></div></div>'
                f'<div class="cta ld-cta"><div><h2>{E(vendor["title"])}</h2><p>{E(vendor["text"])}</p>'
                + f'<p class="ld-buybtn"><a class="btn" href="{rel}{E(vendor["slug"])}/">{E(vendor["button"])}</a></p></div></div>'
                '</div></section>')

    def foot(rel, ix):
        extra = ""
        if ix:
            ps = ix["pop"]["source"]
            extra = (f' Residents: City of Chicago, <a href="{E(ps["url"])}">ACS 5 Year Data by Community Area</a> (U.S. Census Bureau American Community Survey '
                     f'five-year estimates, ACS year {ps["acsYear"]}, allocated to community areas by the City), total population only.')
            if ix.get("rest"):
                rs = ix["rest"]["source"]
                extra += (f' Restaurant citations: City of Chicago, <a href="{E(rs["url"])}">Food Inspections dataset</a>, pulled {E(M.nice_date(rs["fetchedAt"][:10]))}; '
                          'counts only, no restaurant is named.')
        return (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
                f'<p>Source: City of Chicago Data Portal, <a href="{E(src["url"])}">311 Service Requests dataset</a>, requests of type '
                f'{E(src["srType"])}, pulled {E(pulled)}'
                + (", with requests the City marked as duplicates left out" if src.get("duplicatesLeftOut") else "")
                + '. A complaint is one report to 311; it does not say rats were found, and a count says nothing about any '
                'one building, block or business. Counts only: no address or report details are kept.' + extra + '</p>'
                f'<p>{E(M.CITY_DISCLAIMER["Chicago"])}</p><p>ProofNotFluff is not affiliated with or endorsed by the City of Chicago.</p>'
                '<p>Public information, not legal, tax or financial advice, and not pest control advice for any property.</p>'
                '<p>Made by ProofNotFluff with AI assistance from public City data. The page counts visits with Cloudflare Web Analytics, which sets no '
                'cookies.</p></div></footer>\n</body></html>')
    return two, foot, pulled


def week_bars(weeks, counts, label, E, M, to):
    wpeak = max(counts, default=1) or 1
    return ('<div class="rc-wk" role="img" aria-label="' + E(label + ", " + ", ".join(f"{x:,}" for x in counts)) + '">'
            + "".join(f'<div><b>{n:,}</b><i style="height:{max(3, round(n / wpeak * 78))}%"></i>'
                      f'<span>{E(M.nice_date(x["from"]).rsplit(",", 1)[0])}</span></div>' for x, n in zip(weeks, counts))
            + '</div><p class="asof">Each bar is 7 days, oldest on the left; the last bar is the week to ' + E(M.nice_date(to)) + '.</p>')


def page_html(p):
    import make_site as M
    E = M.E
    url, rel = M.BASE + p["slug"] + "/", "../"
    d = load(p)
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), (p["h1"], None)])
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}
    ix = index(d, load_json(POP), load_json(REST)) if d else None
    ds_ld = ({"@context": "https://schema.org", "@type": "Dataset", "name": "Chicago Rat Index by community area",
              "description": "Rat complaints to Chicago 311 per 1,000 residents for each of the 77 community areas, with ranks, rank changes, median days to close and restaurant pest and hood citation counts. Updated every Monday.",
              "url": url, "creator": {"@type": "Organization", "name": "ProofNotFluff", "url": M.BASE}, "isAccessibleForFree": True,
              "license": "https://creativecommons.org/licenses/by/4.0/", "temporalCoverage": f'{d["window"]["from30"]}/{d["window"]["to"]}',
              "spatialCoverage": "Chicago, Illinois", "dateModified": d["source"]["fetchedAt"][:10],
              "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": url + "rat-index.csv"}]} if ix else None)
    head = lambda rb: M.HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=M.SHOP, ld=M.ld_tags(crumb_ld, faq_ld, ds_ld) + CSS + (IX_CSS if ix else ""),
                                    bodycls=' class="ld-page"', robots=rb, analytics=M.analytics_tag())
    if not d:   # before the first weekly pull: a draft shell, never published (is_live needs the data too)
        body = f'{crumb}<div class="ld-hero"><h1>{E(p["h1"])}</h1><p class="lede">The first weekly count is on its way.</p></div>'
        return head('<meta name="robots" content="noindex, nofollow">') + body + "</main></body></html>"
    c, w = d["counts"], d["window"]
    two, foot, pulled = page_parts(p, d, M)
    areas = [a for a in d["areas"] if a["d30"] or a["prev30"] or a["d7"]]
    top = sorted(areas, key=lambda a: (-a["d30"], a["name"]))
    lead = top[0] if top else None
    tie = bool(lead and len(top) > 1 and top[1]["d30"] == lead["d30"])
    lede = (f'{c["d30"]:,} rat complaints came in to Chicago 311 in the 30 days to {E(M.nice_date(w["to"]))}, '
            f'{change_words(c["change"])}. {c["d7"]:,} came in the last 7 days.')
    if ix:
        one = ix["order"][0]
        lede += (f' Per resident, {E(one["name"])} is {one["place"]} on the Rat Index, with {one["r30"]:.2f} complaints per 1,000 residents '
                 f'against {ix["city"]["r30"]:.2f} citywide.')
    tile4 = ""
    if ix:
        one = ix["order"][0]
        tile4 = (f'<div class="tile"><div class="lab">Rat Index, 1st</div><div class="val rc-name">{E(one["name"])}</div>'
                 f'<div class="sub">{one["r30"]:.2f} per 1,000 residents in 30 days</div></div>')
    elif lead and not tie:
        tile4 = f'<div class="tile"><div class="lab">Most complaints</div><div class="val rc-name">{E(lead["name"])}</div><div class="sub">{lead["d30"]:,} in 30 days</div></div>'
    tiles = ('<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">Last 7 days</div><div class="val">{c["d7"]:,}</div><div class="sub">rat complaints to 311</div></div>'
             f'<div class="tile"><div class="lab">Last 30 days</div><div class="val">{c["d30"]:,}</div><div class="sub">in {c["areasWith30"]:,} of 77 community areas</div></div>'
             f'<div class="tile"><div class="lab">Against a year ago</div><div class="val">{E("About the same" if pct(c["change"]) == "same" else pct(c["change"]))}</div><div class="sub">{c["prev30"]:,} in the same 30 days of {E(w["prevTo"][:4])}</div></div>'
             + tile4
             + f'</div><p class="asof">Counts as of {E(M.nice_date(w["to"]))}, from City of Chicago 311 records pulled {E(pulled)}. Updated every Monday.</p>')
    peak = max((a["d30"] for a in top[:10]), default=1) or 1
    bars = ('<figure class="rc-bars" aria-label="Community areas with the most rat complaints in the last 30 days">'
            '<figcaption>Most rat complaints, last 30 days</figcaption>'
            + "".join(f'<div class="rc-bar"><span>{E(a["name"])}</span><i style="width:{max(6, round(a["d30"] / peak * 100))}%"></i><b>{a["d30"]:,}</b>'
                      f'<small>{a["d7"]:,} in the last 7 days · {"too few a year ago to compare" if a["prev30"] < FEW else ("about the same as a year ago" if area_change(a) == "same" else E(area_change(a)) + " on a year ago")}</small></div>' for a in top[:10])
            + '</figure>')
    weeks = week_bars(d["weeks"], [x["count"] for x in d["weeks"]], "Rat complaints each week for the last 12 weeks", E, M, w["to"])
    row = lambda a: (f'<tr><th scope="row">{E(a["name"])}</th><td>{a["d7"]:,}</td><td>{a["d30"]:,}</td><td>{a["prev30"]:,}</td>'
                     f'<td{" class=rc-up" if a["prev30"] >= FEW and a["d30"] >= a["prev30"] * 1.25 else ""}>{E(area_change(a))}</td></tr>')
    thead = ('<thead><tr><th scope="col">Community area</th><th scope="col">7 days</th><th scope="col">30 days</th>'
             f'<th scope="col">Same 30 days, {E(w["prevTo"][:4])}</th><th scope="col">Change</th></tr></thead>')
    tbl = lambda rs, label: (f'<div class="rc-tw" role="region" aria-label="{E(label)}" tabindex="0"><table class="rc-t">{thead}'
                             f'<tbody>{"".join(row(a) for a in rs)}</tbody></table></div>')
    SHOW = 20
    if ix:
        table = index_table(ix, d, E, "")
    else:
        table = (tbl(top[:SHOW], f"Rat complaints, the {min(SHOW, len(top))} community areas with the most")
                 + (f'<details class="rc-more-t"><summary>Show the other {len(top) - SHOW} community areas</summary>'
                    + tbl(top[SHOW:], "Rat complaints, the other community areas") + '</details>' if len(top) > SHOW else "")
                 + f'<p class="asof">Change compares the last 30 days with the same 30 days a year earlier, rounded to a whole percent; within 1% shows as about the same, and under {FEW} complaints a year earlier as too few to compare.'
                 + (f' {c["noArea30"]:,} of the last 30 days\' complaints had no community area on the record and count only in the city total.' if c.get("noArea30") else "")
                 + '</p>')
    mapb = map_block(d, E, ix, "") if p.get("map") else ""
    method = '<section class="block"><h2>How this page is made</h2>' + "".join(f"<p>{E(x)}</p>" for x in p["method"]) + "</section>"
    ed = edition_block(ix, d, E, "", M) if ix else ""
    idx = ""
    if ix:
        cc = ix["city"]
        idx = ('<section class="block" id="areas"><h2>The Chicago Rat Index: every community area</h2>'
               f'<p>All 77 community areas ranked by rat complaints to 311 per 1,000 residents in the 30 days to {E(M.nice_date(w["to"]))}. '
               f'Citywide: {cc["r30"]:.2f} per 1,000. The City closed {c.get("closed30", 0):,} rat requests in those 30 days, '
               f'half of them within {days_txt(c.get("medClose"))} days of coming in (the median). Tap an area for its own page and badge.</p>'
               f'{table}'
               '<div class="ri-dl"><a class="st-btn2" href="rat-index.csv" download>Download the Rat Index (CSV)</a></div>'
               '<p class="asof">Our CSV is free to reuse if you credit ProofNotFluff (license CC BY 4.0); the City\'s data disclaimer at the foot of this page still applies.</p></section>'
               '<section class="block" id="risers"><h2>Top risers</h2>'
               '<p>The community areas that climbed the most places on the Rat Index against the 30 days before (areas with at least 10 complaints in the last 30 days).</p>'
               f'{risers_block(ix, E, "")}</section>')
    else:
        idx = f'<section class="block" id="areas"><h2>Every community area</h2>{table}</section>'
    jump = ""
    if ix:
        links = [("map", "Map"), ("areas", "Rat Index"), ("risers", "Top risers"), ("rattiest", f'Rattiest of {d["edition"]["year"]}')]
        links += [("restaurants", "Restaurants")] if ix.get("rest") else []
        links += [("embed", "Get the badge"), ("help", "Report rats")]
        jump = '<nav class="ri-jump" aria-label="On this page">' + "".join(f'<a href="#{k}">{E(t)}</a>' for k, t in links) + '</nav>'
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{lede}</p>'
            f'<div class="ld-heroact rl-act"><a class="btn" href="#areas">See every neighborhood</a>'
            + ('<a class="st-btn2" href="#map">Open the map</a>' if mapb else "") + '</div></div>'
            f'{tiles}' + (jump if ix else "")
            + (f'<section class="block" id="map"><h2>Rat complaints on the map</h2>{mapb}</section>' if mapb else "")
            + idx + ed
            + f'<section class="block" id="top"><h2>Where the complaints are</h2>{bars}</section>'
            f'<section class="block" id="weeks"><h2>Week by week</h2>{weeks}</section>'
            + (rest_block(ix, E, M) if ix and ix.get("rest") else "")
            + (embed_block(ix, E, "") if ix else "")
            + f'{two(rel)}{method}{M.faq_block(p["faq"])}'
            f'<p class="rl-act ri-end"><a class="btn" href="#areas">See every neighborhood</a> <a class="st-btn2" href="{E(p["resident"]["url"])}" rel="noopener">Report rats on CHI311</a></p>'
            + (COPY_JS if ix else ""))
    return head(robots) + body + foot(rel, ix)


def area_html(p, d, ix, a, M):
    """One community area's own page: /chicago-rat-complaints/<area>/."""
    E = M.E
    rel, up = "../../", "../"
    url = M.BASE + p["slug"] + "/" + a["slug"] + "/"
    w, ed = d["window"], d["edition"]
    two, foot, pulled = page_parts(p, d, M)
    when = M.nice_date(w["to"])
    h1 = f'Rats in {dn(a["name"])}, Chicago'
    h1h = (f'Rats in <span class="ri-nw">{E(dn(a["name"]))},</span> Chicago' if len(dn(a["name"])) <= 15 else E(h1))   # keep a short place name on one line
    title = f'{a["name"]} Rat Complaints and Rat Index, Chicago | ProofNotFluff'
    desc = (f'{dn(a["name"], True)} is {a["place"]} of Chicago\'s 77 areas for rat complaints: {a["r30"]:.2f} per 1,000 residents '
            f'in the 30 days to {when}, from City records.')
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), ("Chicago Rat Index", p["slug"] + "/"), (a["name"], None)])
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    head = M.HEAD.format(title=E(title), desc=E(desc), url=url, rel=rel, shop=M.SHOP, ld=M.ld_tags(crumb_ld) + CSS + IX_CSS,
                         bodycls=' class="ld-page"', robots=robots, analytics=M.analytics_tag())
    ch = area_change(a)
    ch_t = "too few a year ago to compare" if ch == "too few" else ("about the same as" if ch == "same" else f"{ch} on")
    if a["d30"]:
        lede = (f'{E(dn(a["name"], True))} is {a["place"]} of Chicago\'s 77 community areas on the Rat Index: {a["r30"]:.2f} rat complaints to 311 per 1,000 residents '
                f'in the 30 days to {E(when)} ({nn(a["d30"], "complaint")}), against {ix["city"]["r30"]:.2f} citywide. ')
    else:
        lede = (f'{E(dn(a["name"], True))} had no rat complaints to 311 in the 30 days to {E(when)}, so it {"shares" if "tied" in a["place"] else "holds"} the bottom place on the Rat Index '
                f'({a["place"]} of 77), against {ix["city"]["r30"]:.2f} per 1,000 residents citywide. ')
    lede += ("" if not a["d30"] and not a["prior30"] else "It is the same place as in the 30 days before." if not a["mom"] else
               f'That is {move(a["mom"])} place{"s" if abs(a["mom"]) != 1 else ""} from the 30 days before, when it was {ordinal(a["kPrior"])}.')
    tiles = ('<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">Rat Index</div><div class="val">{E(a["place"].replace("tied ", ""))}</div><div class="sub">of 77 community areas{", tied" if "tied" in a["place"] else ""}</div></div>'
             f'<div class="tile"><div class="lab">Per 1,000 residents</div><div class="val">{a["r30"]:.2f}</div><div class="sub">last 30 days; {a["pop"]:,} residents</div></div>'
             f'<div class="tile"><div class="lab">Last 30 days</div><div class="val">{a["d30"]:,}</div><div class="sub">{E(ch_t + " a year ago" if ch not in ("too few",) else ch_t)}</div></div>'
             f'<div class="tile"><div class="lab">Days to close</div><div class="val">{E("none" if not a.get("closed30") else days_txt(a.get("medClose")))}</div><div class="sub">{(f'half of the {nn(a.get("closed30", 0), "request")} closed in the last 30 days took {days_txt(a["medClose"])} days or less' if a.get("medClose") is not None else ("no requests closed in the last 30 days" if not a.get("closed30") else f'only {nn(a["closed30"], "request")} closed in 30 days (under 5)'))}</div></div>'
             f'</div><p class="asof">Counts as of {E(when)}, from City of Chicago 311 records pulled {E(pulled)}. Updated every Monday.</p>')
    yr = E(w["prevTo"][:4])
    sd = lambda x: M.nice_date(x).rsplit(",", 1)[0]
    rows = [("Last 30 days", f'{sd(w["from30"])} to {sd(w["to"])}', a["d30"], a["r30"], ordinal(a["k30"])),
            ("The 30 days before", f'{sd(w["priorFrom"])} to {sd(w["priorTo"])}', a["prior30"], a["rPrior"], ordinal(a["kPrior"])),
            (f"Same 30 days, {yr}", f'{sd(w["prevFrom"])} to {sd(w["prevTo"])}, {yr}', a["prev30"], a["rPrev"], ordinal(a["kPrev"]))]
    rank_t = ('<div class="rc-tw ri-rank" role="region" aria-label="' + E(a["name"]) + ' rank over time" tabindex="0"><table class="rc-t">'
              '<thead><tr><th scope="col">Period</th><th scope="col">Complaints</th><th scope="col">Per 1,000 residents</th><th scope="col">Rank of 77</th></tr></thead><tbody>'
              + "".join(f'<tr><th scope="row">{E(n)}<small class="ri-span">{E(span)}</small></th><td>{c:,}</td><td>{r:.2f}</td><td>{E(k)}</td></tr>' for n, span, c, r, k in rows)
              + '</tbody></table></div>'
              f'<p class="asof">Rank against the 30 days before: {mv_cell(a["mom"])}. Rank against the same 30 days of {yr}: {mv_cell(a["yoy"])}. '
              'Rank 1 has the most complaints per resident; "up" means closer to 1st.</p>')
    weeks = week_bars(d["weeks"], a["w12"], f'Rat complaints in {dn(a["name"])} each week for the last 12 weeks', E, M, w["to"])
    edition = (f'<section class="block"><h2>{E(dn(a["name"], True))} in the {ed["year"]} rattiest neighborhoods list</h2>'
               f'<p>In the 12 months from {E(M.nice_date(ed["from"]))} to {E(M.nice_date(ed["to"]))}, {E(dn(a["name"]))} had {a["year"]:,} rat complaints, '
               f'{a["rYear"]:.2f} per 1,000 residents: {E(a["placeYear"])} of 77 (it was {ordinal(a["kYearPrev"])} in the {ed["year"] - 1} edition, with {a["yearPrev"]:,}). '
               f'The list ranks complaints to 311, not a count of rats. <a href="{up}#rattiest">See the {ed["year"]} top 10</a>.</p></section>')
    rest = ""
    if "insp" in a:
        cc = ix["city"]
        rw = ix["rest"]["window"]
        if a["pestShare"] is not None:
            rt = (f'<div class="ri-rest"><div class="tile"><div class="lab">Restaurant inspections</div><div class="val">{a["insp"]:,}</div><div class="sub">in 12 weeks</div></div>'
                  f'<div class="tile"><div class="lab">Cited pests</div><div class="val">{a["pestShare"]}%</div><div class="sub">{nn(a["pest"], "inspection")}; {cc["pestShare"]}% citywide</div></div>'
                  f'<div class="tile"><div class="lab">Cited a hood or ventilation</div><div class="val">{a["ventShare"]}%</div><div class="sub">{nn(a["vent"], "inspection")}; {cc["ventShare"]}% citywide</div></div></div>')
        else:
            rt = ("<p>No restaurant inspections in these 12 weeks.</p>" if not a["insp"] else
                  f'<p>{a["insp"]:,} restaurant inspection{"" if a["insp"] == 1 else "s"} in 12 weeks: {a["pest"]:,} cited pests and {a["vent"]:,} cited a hood or ventilation. '
                  f'That is too few to give a fair share (under {SHARE_FEW}).</p>')
        rest = (f'<section class="block"><h2>Restaurant inspections in {E(dn(a["name"]))}</h2>'
                f'<p>City food inspections of restaurants in {E(dn(a["name"]))} from {E(M.nice_date(rw["from"]))} to {E(M.nice_date(rw["to"]))}: how many cited pests '
                '(violation 38) or a kitchen hood or ventilation (violation 56 with a hood or vent note). Counts only; no restaurant is named.</p>'
                f'{rt}<p class="asof ri-page-how"><a href="{up}#restaurants">How these are counted</a></p></section>')
    i = ix["order"].index(a)
    nb = ix["order"][max(0, i - 2):i] + ix["order"][i + 1:i + 3]
    near = ('<section class="block"><h2>Nearby on the Rat Index</h2><ul class="ri-near">'
            + "".join(f'<li><a href="{up}{x["slug"]}/">{x["k30"]}. {E(x["name"])}</a></li>' for x in nb)
            + f'<li><a href="{up}#areas">All 77 community areas</a></li></ul>'
            f'<div class="ri-dl"><a class="st-btn2" href="weekly.csv" download>Download weekly counts (CSV)</a>'
            f'<a class="st-btn2" href="{up}rat-index.csv" download>Download all 77 areas (CSV)</a></div></section>')
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">Chicago Rat Index, community area {a["n"]}</p><h1>{h1h}</h1><p class="lede">{lede}</p>'
            f'<div class="ld-heroact rl-act"><a class="btn" href="{up}">See all 77 areas</a><a class="st-btn2" href="#embed">Get the badge</a></div></div>'
            f'{tiles}'
            f'<section class="block"><h2>How the rank moved</h2>{rank_t}</section>'
            f'<section class="block"><h2>Week by week in {E(dn(a["name"]))}</h2>{weeks}</section>'
            f'{edition}{rest}'
            + embed_block(ix, E, up, one=a).replace(f'src="{up}{a["slug"]}/badge.svg"', 'src="badge.svg"')
            + near + two(rel) + COPY_JS)
    return head + body + foot(rel, ix)


def lastmod(p):
    d = load(p)
    return d["source"]["fetchedAt"][:10] if d else None


def extra_pages(p):
    """One page, badge and weeks CSV per community area, and the all-areas CSV, under /chicago-rat-complaints/."""
    import make_site as M
    d = load(p)
    ix = index(d, load_json(POP), load_json(REST)) if d else None
    if not ix:
        return []
    out = [("rat-index.csv", index_csv(ix, d))]
    for a in ix["order"]:
        out += [(f'{a["slug"]}/index.html', area_html(p, d, ix, a, M)), (f'{a["slug"]}/badge.svg', badge_svg(a, d)),
                (f'{a["slug"]}/weekly.csv', area_csv(a, d, ix["rest"]))]
    return out


def selftest():
    sys.path.insert(0, HERE)
    import make_site as M
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("kind") == "rodents"][0]
    import rodents_chicago as R, datetime as dt
    w = R.windows(dt.date(2026, 10, 26))
    d = R.build({6: 40, 24: 30, 0: 2}, {6: 243, 24: 208, 22: 169, 0: 9}, {6: 200, 24: 0, 22: 169},
                [{"d": "2026-10-25T00:00:00.000", "n": "150"}], w, "2026-10-26T06:00:00-0500")
    import tempfile
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, dir=ROOT)
    json.dump(d, tmp); tmp.close()
    try:
        html = page_html(dict(spec, data=os.path.relpath(tmp.name, ROOT)))
    finally:
        os.unlink(tmp.name)
    assert html.count("<h1>") == 1 and "—" not in html and "–" not in html, "one h1, no dashes"
    assert "Lake View" in html and "629 rat complaints came in" in html, "total in the lede"
    assert ">+22%<" in html and ">too few<" in html and ">same<" in html, "change words"
    assert "9 of the last 30 days" in html and "too few to compare" in html, "notes under the table"
    assert M.E(M.CITY_DISCLAIMER["Chicago"]) in html, "City disclaimer"
    assert "address" not in json.dumps(d["areas"]), "counts only"
    assert 'tabindex="0"' in html and 'role="region"' in html, "scrollable table reachable by keyboard"
    shell = page_html(dict(spec, data="permits/rodents-chicago/none.json"))
    assert "noindex" in shell, "no data: the shell is never indexed"
    assert index(d, {"areas": [], "total": 1}) is None, "an old weekly file (no prior 30 days) keeps the plain page"
    # Rat Index: planted counts for all 77 areas with known residents
    d2 = R.build({k: k % 5 for k in R.AREAS}, {k: k if k != 77 else 75 for k in R.AREAS}, {k: 77 - k for k in R.AREAS}, [], w, "2026-10-26T06:00:00-0500",
                 prior={k: 2 * k if k != 76 else 1 for k in R.AREAS}, wk_area={k: [k] * 12 for k in R.AREAS},
                 closes={**{k: (k, 3.0) for k in R.AREAS}, "all": (100, 3.0)}, year={k: 10 * k for k in R.AREAS}, year_prev={k: 9 * k for k in R.AREAS})
    pop = {"areas": [{"n": k, "name": R.AREAS[k], "population": 1000} for k in R.AREAS], "total": 77000,
           "source": {"url": "https://data.cityofchicago.org/d/t68z-cikk", "acsYear": 2023}}
    rest = {"source": {"url": "u", "fetchedAt": "2026-10-26T06:00:00-0500"}, "window": {"from": "2026-08-03", "to": "2026-10-25"},
            "codes": {"pest": {"code": 38, "title": "INSECTS, RODENTS, & ANIMALS NOT PRESENT"}, "vent": {"code": 56, "title": "ADEQUATE VENTILATION & LIGHTING"}},
            "counts": {"inspections": 200, "pest": 40, "vent": 20, "noArea": 0},
            "weeks": [{"from": x["from"], "to": x["to"], "inspections": 1, "pest": 0, "vent": 0} for x in R.weeks_of([], w)],
            "areas": [{"n": k, "name": R.AREAS[k], "inspections": 20 if k == 6 else 3, "pest": 5 if k == 6 else 1, "vent": 2 if k == 6 else 0,
                       "weeks": [[1, 0, 0]] * 12} for k in R.AREAS]}
    ix = index(d2, pop, rest)
    A = ix["areas"]
    assert A[76]["k30"] == 1 and A[75]["k30"] == 2 and A[77]["k30"] == 2 and A[77]["place"] == "tied 2nd", (A[76]["k30"], A[77]["k30"], A[77]["place"])
    assert A[6]["kPrior"] - A[6]["k30"] == A[6]["mom"] and move(3) == "up 3" and move(-2) == "down 2" and move(0) == "same"
    assert A[76]["mom"] == 76 and ix["risers"][0]["n"] == 76, "O'Hare jumps from last to first"
    assert (A[6]["pestShare"], A[6]["ventShare"], A[7]["pestShare"]) == (25, 10, None), "shares only from 10 inspections up"
    assert slug_of("O'Hare") == "ohare" and slug_of("Greater Grand Crossing") == "greater-grand-crossing"
    spec2 = dict(spec, data=os.path.relpath(tmp.name, ROOT))
    svg = badge_svg(A[6], d2)
    assert svg.count("<title") == 1 and "<desc" in svg and 'role="img"' in svg and "Lake View" in svg and "—" not in svg
    rows = list(csv.reader(io.StringIO(index_csv(ix, d2))))
    assert len(rows) == 78 and rows[0] == CSV_COLS and rows[1][2] == "O'Hare" and rows[1][6] == "76.00", rows[1][:7]
    page = area_html(spec2, d2, ix, A[6], M)
    assert page.count("<h1>") == 1 and "Rats in <span class=\"ri-nw\">Lake View,</span> Chicago" in page and "Lake View Rat Complaints" in page and "—" not in page and "–" not in page
    assert "25%" in page and "INSECTS" not in page and 'src="badge.svg"' in page, "restaurant share, title only on the main page, badge"
    ac = list(csv.reader(io.StringIO(area_csv(A[6], d2, rest))))
    assert len(ac) == 13 and ac[-1][3] == "6", ac[-1]
    print("rodents_site selftest: ok (plain page, Rat Index ranks and ties, moves, risers, shares, badge, CSVs, area page)")
    return
    print("rodents_site selftest: ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
