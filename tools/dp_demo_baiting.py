#!/usr/bin/env python3
"""Chicago Demolition Rodent Baiting: the free page /chicago-demolition-rodent-baiting/ (site/pages.json kind "datapage",
module dp_demo_baiting; tools/make_site.py calls page_html and lastmod here). Todd's go, Oct 27, 2026, 12:17 pm:
"Let's do them all" (coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md, research_notes/kimi-2026-10-27-r10.md item 12).

Two parts:
- The rodent control step of a Chicago demolition permit, in our own plain words, from the Department of Buildings
  demolition permits page and Form 480 (rev. 8/29/2021), both read Oct 27, 2026 (STEPS_SOURCE below). Department names
  only; no City staff are named.
- Wrecking and demolition permits the City issued, by week and community area: site/datapages/dp_demo_baiting/wrecking.json,
  written weekly in GitHub Actions by tools/dp_permit_wait_data.py (the same pull as the permit wait times page). Counts
  only; no permit number, address, contact or description exists in the file.

Usage: python3 tools/dp_demo_baiting.py --selftest
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = "site/datapages/dp_demo_baiting/wrecking.json"
DEMO_PAGE = "https://www.chicago.gov/city/en/depts/bldgs/provdrs/permits/svcs/demo-permits.html"
FORM_480 = "https://www.Chicago.gov/content/dam/city/depts/bldgs/general/forms/Form480-08292021.pdf"
STEPS_READ = "2026-10-27"

META = {"h1": "Chicago Demolition Rodent Baiting",
        "card": "The rodent control step for a wrecking permit, with permits issued each week by neighborhood",
        "keywords": "demolition rodent baiting wrecking permit rat abatement affidavit streets and sanitation inspection form 480 "
                    "pest control demolition chicago"}

STEPS = [("A licensed pest control company baits the site.", ""),
         ("A rodent control affidavit is completed.",
          "A completed affidavit is part of the rodent control approval."),
         ("Streets and Sanitation inspects the site.", ""),
         ("Streets and Sanitation sends the approval by email.", ""),
         ("The approval is attached to the permit application.",
          "Page 2 of Form 480, the demolition permit application, is the checklist of approvals; the rodent control line has a box to show the Streets and Sanitation approval is attached.")]

OTHERS = ["Public Health: the demolition notice of intent, filed through the City's online permit portal (every applicant).",
          "Transportation: a public right of way permit, or written word that none is needed.",
          "Buildings, for Water Management: a sewer cut and seal permit and its inspection, and a water disconnection permit and its inspection, or written word that they are not needed.",
          "Water Management: a hydrant use permit or an approved other water source, such as a water truck.",
          "Only for some jobs: a pre-permit inspection for complex demolitions, Housing for buildings with dwelling units, Planning and Development for historic buildings, Transportation for the downtown freight tunnel area, Public Health for flammable liquid tanks, and soil contamination reviews in two areas."]

TIMES = [("120 days", "An application with no activity for 120 days expires. One 90-day extension can be asked for before then."),
         ("120 days", "After the City says the permit is ready, the fee is paid within 120 days; the permit certificate is issued at payment."),
         ("6 months", "Work starts within 6 months of payment and may not stop for more than 12 months in all.")]

FAQ = [
    ("Does a Chicago demolition permit need rodent baiting?",
     "Yes. The Department of Buildings lists rodent control from Streets and Sanitation among the approvals for every demolition permit applicant: "
     "a licensed pest control company baits the site, the affidavit is filled in, and the site passes a Streets and Sanitation inspection. Check with the agency for your job."),
    ("Who does the baiting?",
     "A licensed pest control company the applicant hires. Streets and Sanitation then inspects the site."),
    ("How does the approval arrive?",
     "By email from Streets and Sanitation. It is then attached to the demolition permit application, Form 480."),
    ("What do the permit counts on this page show?",
     "How many wrecking and demolition permits the City issued, by week and community area, from the City's Building Permits records. "
     "The rodent control step comes before a permit is issued, so the counts show where that step was recently needed, not where baiting is happening today."),
    ("How often is the page updated?",
     "The permit counts update once a week, on Monday mornings. The steps are checked against the City's demolition permit page when the page is rebuilt by hand; the date they were read is on the page."),
]


def load(p=None):
    f = os.path.join(ROOT, (p or {}).get("data", DATA))
    return json.load(open(f, encoding="utf-8")) if os.path.isfile(f) else None


def lastmod(p):
    d = load(p)
    return (d or {}).get("source", {}).get("fetchedAt", "")[:10] or None


def map_block(d, E):
    import geo_map as G
    from dp_permit_wait import breaks, legend
    by = {a["a"]: a for a in d["areas"]}
    c30, c12 = breaks([a["d30"] for a in by.values()]), breaks([a["d365"] for a in by.values()])
    areas = {k: {"big": {"d30": (f'{a["d30"]:,}', "wrecking and demolition permits, last 30 days"), "d365": (f'{a["d365"]:,}', "wrecking and demolition permits, last 12 months")},
                 "say": {"d30": f'{a["d30"]:,} wrecking and demolition permit{"" if a["d30"] == 1 else "s"} in 30 days', "d365": f'{a["d365"]:,} wrecking and demolition permit{"" if a["d365"] == 1 else "s"} in 12 months'},
                 "html": (f'<dl><dt>Last 7 days</dt><dd>{a["d7"]:,}</dd><dt>Last 30 days</dt><dd>{a["d30"]:,}</dd>'
                          f'<dt>Last 12 months</dt><dd>{a["d365"]:,}</dd></dl>')} for k, a in by.items()}
    metrics = [{"key": "d30", "label": "Last 30 days", "legendTitle": "Wrecking and demolition permits issued, last 30 days",
                "cls": {k: f"q{G.klass(a['d30'], c30)}" for k, a in by.items()}, "legend": legend(c30)},
               {"key": "d365", "label": "Last 12 months", "legendTitle": "Wrecking and demolition permits issued, last 12 months",
                "cls": {k: f"q{G.klass(a['d365'], c12)}" for k, a in by.items()}, "legend": legend(c12)}]
    top = sorted([a for a in by.values() if a["d30"]], key=lambda a: (-a["d30"], a["name"]))[:4]
    c = d["counts"]
    hint = ('<h3>Citywide</h3>'
            f'<p class="gm-big"><span>{c["d30"]:,}</span><small>wrecking and demolition permits issued, last 30 days</small></p>'
            + (f'<p>Most in the last 30 days:</p><ul class="gm-top">'
               + "".join(f'<li><button type="button" data-pick="{a["a"]}">{E(a["name"])}, {a["d30"]:,}</button></li>' for a in top) + '</ul>' if top else "")
            + '<p class="gm-hint">Tap or hover any area on the map, or choose one from the list.</p>')
    fig = G.choropleth(areas, metrics, uid="demomap", title="Map of Chicago's 77 community areas, colored by wrecking and demolition permits issued",
                       hint=hint, caption=("Community area outlines: City of Chicago, Boundaries - Community Areas. "
                                           "A permit counts in the community area of its primary address. Every number on the map is also in the table below."))
    return G.CSS + fig if fig else ""


def page_html(p):
    import make_site as M
    import dp_permit_wait as W
    E = M.E
    url, rel = M.BASE + p["slug"] + "/", "../"
    d = load(p)
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), ("Free Chicago data", "chicago-data/"), (META["h1"], None)])
    if not d:
        return W.shell(M, p, url, rel, crumb)
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    c, w, src = d["counts"], d["window"], d["source"]
    wait = d.get("wait") or {}
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    howto_ld = {"@context": "https://schema.org", "@type": "HowTo", "name": "The rodent control step of a Chicago demolition permit",
                "step": [{"@type": "HowToStep", "position": i, "name": t, "text": x or t} for i, (t, x) in enumerate(STEPS, 1)]}
    lede = ("Before Chicago issues a demolition permit, a licensed pest control company baits the site and Streets and Sanitation "
            f"inspects it. The City issued {c['d30']:,} wrecking and demolition permits in the 30 days to {E(M.nice_date(w['to']))}, "
            f"in {c['areasWith30']:,} of 77 community areas.")
    tiles = ('<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">Last 7 days</div><div class="val">{c["d7"]:,}</div><div class="sub">wrecking and demolition permits</div></div>'
             f'<div class="tile"><div class="lab">Last 30 days</div><div class="val">{c["d30"]:,}</div><div class="sub">in {c["areasWith30"]:,} community areas</div></div>'
             f'<div class="tile"><div class="lab">Last 12 months</div><div class="val">{c["d365"]:,}</div><div class="sub">wrecking and demolition permits</div></div>'
             + (f'<div class="tile"><div class="lab">Half within</div><div class="val">{wait["med"]:,} days</div><div class="sub">of review start, last 12 months</div></div>' if wait.get("med") is not None else "")
             + f'</div><p class="asof">Counts as of {E(M.nice_date(w["to"]))}, from City of Chicago records pulled {E(M.nice_date(src["fetchedAt"][:10]))}. Updated weekly.</p>')
    steps = ('<ol class="pw-steps">' + "".join(f"<li><b>{E(t)}</b>{E(x)}</li>" for t, x in STEPS) + '</ol>'
             f'<p class="asof">From the Department of Buildings <a href="{DEMO_PAGE}" rel="noopener">demolition permits page</a> and '
             f'<a href="{FORM_480}" rel="noopener">Form 480</a> (revised Aug 29, 2021), read {E(M.nice_date(STEPS_READ))}. Our words; the City\'s pages are the rule.</p>')
    others = ('<details class="pw-more"><summary>The other approvals on Form 480</summary><ul>'
              + "".join(f"<li>{E(x)}</li>" for x in OTHERS) + '</ul></details>')
    times = "".join(f'<div class="tile"><div class="lab">{E(a)}</div><div class="sub" style="font-size:14px;color:var(--ink2)">{E(b)}</div></div>' for a, b in TIMES)
    wk = W.count_chart(d["weeks"], E, "Wrecking and demolition permits issued each week, last 12 weeks",
                       lambda x: M.nice_date(x["from"]).rsplit(",", 1)[0])
    mapb = map_block(d, E)
    rows = [[E(a["name"]), f'{a["d7"]:,}', f'{a["d30"]:,}', f'{a["d365"]:,}']
            for a in sorted([a for a in d["areas"] if a["d365"]], key=lambda a: (-a["d30"], -a["d365"], a["name"]))]
    na12 = c["d365"] - sum(a["d365"] for a in d["areas"])
    tbl = W.split_table(["Community area", "Last 7 days", "Last 30 days", "Last 12 months"], rows,
                        "Wrecking and demolition permits issued by community area", E, show=20, what="community areas")
    wait_line = (f'<p class="pw-note"><b>How long a wrecking and demolition permit takes.</b> Half of the wrecking and demolition permits issued in the last 12 months '
                 f'were issued within {wait["med"]:,} days of the City starting review, and 8 in 10 within {wait["p80"]:,} days; '
                 f'{wait["sameDay"]:.0f}% were issued the same day review started. <a href="{rel}chicago-permit-wait-times/wrecking-and-demolition/">Wrecking and demolition permit wait times by month and community area</a>.</p>' if wait.get("med") is not None else "")
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(META["h1"])}</h1><p class="lede">{lede}</p>'
            '<div class="ld-heroact rl-act"><a class="btn" href="#steps">See the five steps</a>'
            + ('<a class="st-btn2" href="#map">Open the map</a>' if mapb else '<a class="st-btn2" href="#areas">Permits by area</a>') + '</div></div>'
            + tiles + W.otp([("steps", "Steps"), ("times", "Dates"), ("weeks", "Weekly")] + ([("map", "Map")] if mapb else []) + [("areas", "Areas"), ("questions", "Questions")], E)
            + f'<section class="block" id="steps"><h2>The rodent control step, in five parts</h2><p>Form 480 lists rodent control from the Department of Streets and Sanitation among the approvals for every demolition permit applicant.</p>{steps}{others}</section>'
            + f'<section class="block" id="times"><h2>Dates to keep in mind</h2><div class="tiles ld-tiles pw-dates">{times}</div>'
            + f'<p class="asof">From the Department of Buildings demolition permits page, read {E(M.nice_date(STEPS_READ))}.</p>{wait_line}</section>'
            + f'<section class="block" id="weeks"><h2>Wrecking and demolition permits, week by week</h2>{wk}'
            + f'<p class="asof">Each column is 7 days, oldest on the left; the last is the week to {E(M.nice_date(d["weeks"][-1]["to"]))}. The rodent control step comes before a permit is issued, so these counts show where it was recently needed.</p></section>'
            + (f'<section class="block" id="map"><h2>Where the wrecking and demolition permits are</h2>{mapb}</section>' if mapb else "")
            + f'<section class="block" id="areas"><h2>Every community area</h2>{tbl}'
            + (f'<p class="asof">{na12:,} of the last 12 months\' permits had no community area on the record and count only in the city totals.</p>' if na12 else "")
            + '</section>'
            + '<section class="block" id="help"><div class="pw-two">'
            + f'<div class="cta ld-cta"><div><h2>Where rats are being reported</h2><p>Rat complaints to 311 by community area, the last 7 and 30 days against a year earlier, on a map. Updated weekly.</p>'
            + f'<p class="ld-buybtn"><a class="btn" href="{rel}chicago-rat-complaints/">See rat complaints by neighborhood</a></p></div></div>'
            + f'<div class="cta ld-cta"><div><h2>Applying for a demolition permit?</h2><p>The Department of Buildings page has every approval, document and form for the permit. For your own job, check with the agency.</p>'
            + f'<p class="ld-buybtn"><a class="btn" href="{DEMO_PAGE}" rel="noopener">City demolition permits page</a></p></div></div>'
            + '</div></section>'
            + '<section class="block"><h2>How this page is made</h2>'
            + f'<p>The steps are our plain summary of the City\'s demolition permits page and Form 480, read {E(M.nice_date(STEPS_READ))}. The City\'s own pages are the rule; when they change, they win.</p>'
            + '<p>The permit counts are wrecking and demolition permits the City issued, from its Building Permits dataset, counted by issue date and by the community area of each permit\'s primary address. Counts only: no permit number, address or contact is kept.</p>'
            + (f'<p>The wait days are the City\'s processing time field, days from the City starting review to the issue date, for the {wait["n"]:,} wrecking and demolition permits issued in the last 12 months.</p>' if wait.get("med") is not None else "")
            + '</section>' + W.faq(M, FAQ)
            + f'<p class="pw-end"><a class="btn" href="#steps">See the five steps</a><a class="st-btn2" href="{rel}chicago-rat-complaints/">Rat complaints by neighborhood</a></p>')
    return (W.head_html(M, p, url, rel, p["title"], p.get("desc", ""), robots, M.ld_tags(crumb_ld, faq_ld, howto_ld)) + body
            + W.foot(M, rel, src, "Wrecking and demolition permits by issue date. Steps from the Department of Buildings demolition permits page and Form 480. "))


def selftest():
    sys.path.insert(0, HERE)
    import make_site as M, tempfile, datetime as dt
    import dp_permit_wait_data as D
    from rodents_chicago import AREAS
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("module") == "dp_demo_baiting"][0]
    today = dt.date(2026, 10, 27)
    rows = [{"permit_type": "PERMIT - WRECKING/DEMOLITION", "review_type": "WRECKING/DEMOLITION",
             "issue_date": (today - dt.timedelta(days=1 + i % 200)).isoformat() + "T00:00:00", "processing_time": str(20 + i % 40),
             "application_start_date": (today - dt.timedelta(days=1 + i % 200 + 20 + i % 40)).isoformat() + "T00:00:00",
             "community_area": str(1 + i % 77), "contact_1_name": "PLANTED", "street_name": "PLANTED"} for i in range(400)]
    d = D.build_wreck(rows, today, "2026-10-27T07:00:00-0500", None, AREAS)
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, dir=ROOT)
    json.dump(d, tmp); tmp.close()
    try:
        html = page_html(dict(spec, data=os.path.relpath(tmp.name, ROOT)))
    finally:
        os.unlink(tmp.name)
    assert html.count("<h1>") == 1 and "—" not in html and "–" not in html, "one h1, no dashes"
    assert "PLANTED" not in html and M.E(M.CITY_DISCLAIMER["Chicago"]) in html, "no person or address; City disclaimer"
    assert html.count("<li><b>") == len(STEPS) == 5 and "chicago-rat-complaints/" in html and DEMO_PAGE in html, "steps, rat page, City page"
    assert f'{d["counts"]["d30"]:,} wrecking and demolition permits' in html and "demomap" in html
    assert "noindex" in page_html(dict(spec, data="site/datapages/dp_demo_baiting/none.json"))
    print("dp_demo_baiting selftest: ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
