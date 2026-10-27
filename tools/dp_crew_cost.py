#!/usr/bin/env python3
"""What a Chicago Crew Costs: the free page /chicago-crew-cost/ (site/pages.json kind "datapage", built by
tools/make_site.py through page_html here). Todd's go, Oct 27, 2026, 12:17 pm ("Let's do them all", coo/PARALLEL_BUILDS.md,
build B7; research_notes/kimi-2026-10-27-r10.md item 7). Audience: trade owners (Todd, Oct 27, 9:04 am: "trade owners only").

Data: site/datapages/dp_crew_cost/data.json (tools/dp_crew_cost_fetch.py ingest): BLS OEWS May 2025 hourly wages for the
Chicago metro, the IDOL Cook County prevailing wage schedule posted Oct 19, 2026, the City of Chicago notice effective
July 1, 2026, the Cook County minimum wage notice and IRS Publication 15 (2026). watch.json is the weekly re-check of
the pages a runner can reach. No person or business appears anywhere.

The page: pick a trade, see its pay range and its Cook County public works rate, and work out a crew day's cost from
crew size, hours and wage. One sub-page per trade (each with its own numbers) and two CSV downloads.

Usage: python3 tools/dp_crew_cost.py --selftest
"""
import csv, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "site", "datapages", "dp_crew_cost", "data.json")
WATCH = os.path.join(ROOT, "site", "datapages", "dp_crew_cost", "watch.json")
CSV_PAY = "chicago-metro-hourly-pay-by-trade-may-2025.csv"
CSV_PW = "cook-county-prevailing-wage-2026-10-19.csv"
CALC_CONTRACTOR = "contractor-hourly-rate-calculator"
CALC_HANDYMAN = "handyman-hourly-rate-calculator"
DEFAULT_ROLE = "electricians"

META = {"h1": "What a Chicago Crew Costs",
        "card": "Hourly pay for 12 trades in the Chicago metro, Cook County public works rates with fringes, the 2026 minimum wage and paid leave, and a crew day cost calculator.",
        "keywords": "crew cost labor cost wage hourly pay electrician plumber carpenter laborer roofer painter hvac janitor maid landscaper pest control helper "
                    "prevailing wage fringe benefits cook county public works minimum wage paid leave paid sick leave payroll tax chicago"}

# Plain names for the Cook County schedule's column codes (its own legend: Base Wage Rate, Health/Welfare benefit,
# Vacation, Training, and Other Ins: employer hourly cost for any other insurance for the worker)
FRINGE_NAMES = [("hw", "Health and welfare"), ("pension", "Pension"), ("vac", "Vacation"), ("trng", "Training"), ("otherIns", "Other insurance")]
TYPE_NAMES = {"ALL": "All", "BLD": "Building", "HWY": "Highway", "FLT": "Floating"}
ORDER = [("median", "Median"), ("p10", "10th"), ("p25", "25th"), ("p75", "75th"), ("p90", "90th")]
PCTS = [("p10", "10th"), ("p25", "25th"), ("median", "Median"), ("p75", "75th"), ("p90", "90th")]
SLUG_NAMES = {"janitors": "janitors", "maids": "maids-and-housekeepers", "pest": "pest-control-workers", "landscapers": "landscapers",
              "roofers": "roofers", "painters": "painters", "helpers": "construction-helpers", "electricians": "electricians",
              "plumbers": "plumbers", "hvac": "hvac-techs", "carpenters": "carpenters", "laborers": "construction-laborers"}
SINGULAR = {"janitors": "janitor", "maids": "maid or housekeeper", "pest": "pest control worker", "landscapers": "landscaper",
            "roofers": "roofer", "painters": "painter", "helpers": "construction helper", "electricians": "electrician",
            "plumbers": "plumber or pipefitter", "hvac": "HVAC tech", "carpenters": "carpenter", "laborers": "construction laborer"}
H1_NAMES = {"janitors": "Janitor", "maids": "Maid and Housekeeper", "pest": "Pest Control Worker", "landscapers": "Landscaper",
            "roofers": "Roofer", "painters": "Painter", "helpers": "Construction Helper", "electricians": "Electrician",
            "plumbers": "Plumber and Pipefitter", "hvac": "HVAC Tech", "carpenters": "Carpenter", "laborers": "Construction Laborer"}
PLURAL = {"janitors": "janitors", "maids": "maids and housekeepers", "pest": "pest control workers", "landscapers": "landscapers",
          "roofers": "roofers", "painters": "painters", "helpers": "construction helpers", "electricians": "electricians",
          "plumbers": "plumbers and pipefitters", "hvac": "HVAC techs", "carpenters": "carpenters", "laborers": "construction laborers"}


def load(p=None):
    f = os.path.join(ROOT, (p or {}).get("data", os.path.relpath(DATA, ROOT)))
    return json.load(open(f, encoding="utf-8")) if os.path.isfile(f) else None


def load_watch():
    try:
        return json.load(open(WATCH, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def lastmod(p):
    d = load(p)
    if not d:
        return None
    w = load_watch()
    return max(d["built"], (w or {}).get("checkedAt", "")[:10] if (w or {}).get("allOk") else "")


def m2(x):
    return "#" if x == "#" else ("" if x is None else f"${x:,.2f}")


def m0(x):
    return f"${x:,.0f}"


WORDS = {"pwr": "Power", "eqmt": "Equipment", "op": "Operator", "grndman": "Groundman", "abt-gen": "Abatement, General",
         "abt-mec": "Abatement, Mechanical", "sheetmetal": "Sheet Metal", "ii": "II", "i": "I"}


def title_case(t):
    """IDOL writes trade names in capitals and short forms; the page shows them as words (ELECTRIC PWR EQMT OP ->
    Electric Power Equipment Operator)."""
    out = []
    for n, w in enumerate(t.lower().split()):
        if w in WORDS:
            out.append(WORDS[w])
        elif w in ("and", "of", "the", "-") and n:
            out.append(w)
        else:
            out.append("/".join(x[:1].upper() + x[1:] for x in w.split("/")))
    return " ".join(out)


def bls_title(t):
    """BLS titles as words, with its double hyphen read as a colon (Helpers--Carpenters -> Helpers: Carpenters)."""
    return t.replace("--", ": ")


HELPER_NAMES = {"47-3011": "Helpers for masons and tile setters", "47-3012": "Helpers for carpenters", "47-3013": "Helpers for electricians",
                "47-3014": "Helpers for painters and plasterers", "47-3015": "Helpers for plumbers and pipefitters", "47-3016": "Helpers for roofers",
                "47-3019": "Helpers in other trades"}


def disp(role, ln):
    """The short name a trade owner would use: the trade itself, or for helpers which trade they help."""
    return role["label"] if len(role["lines"]) == 1 else HELPER_NAMES.get(ln["code"], bls_title(ln["title"]))


def line_key(role, ln):
    return role["key"] if len(role["lines"]) == 1 else f'{role["key"]}:{ln["code"]}'


def pw_rows(d, key):
    """The Cook County schedule lines a role's work usually falls under, in the order listed."""
    names = d["prevailing"]["match"].get(key, [])
    return [r for n in names for r in d["prevailing"]["rows"] if r["trade"] == n]


def crew_day(n, h, rate, ss, med, leave=True, fringe=0.0, ot_after=None, ot_mult=1.0, other=0.0):
    """One crew day. Wages: each person's hours at the rate, with hours past ot_after (Cook County schedule: hours over
    8 Monday to Friday) at ot_mult. Social Security and Medicare (IRS Publication 15) on wages only, not on fringe
    contributions. Chicago paid leave and paid sick leave earned: 1 hour of each per 35 hours worked (City notice),
    valued at the base rate. Fringes and other costs per hour worked."""
    reg = h if ot_after is None else min(h, ot_after)
    ot = 0 if ot_after is None else max(0.0, h - ot_after)
    c = lambda x: round(x + 1e-9, 2)   # every line to the cent, and the total is the sum of the lines shown
    wages = c(n * (reg * rate + ot * rate * ot_mult))
    tax = c(wages * (ss + med) / 100)
    lv_hours = n * h / 35 if leave else 0.0
    lv = c(2 * lv_hours * rate)
    fr = c(n * h * fringe)
    oth = c(n * h * other)
    total = c(wages + tax + lv + fr + oth)
    return {"wages": wages, "tax": tax, "leaveHours": lv_hours, "leave": lv, "fringes": fr, "other": oth, "total": total,
            "perPersonHour": total / (n * h) if n and h else 0, "otHours": n * ot}


CSS = ("<style>"
       ".cc-pick{display:grid;gap:12px;margin:0 0 16px}@media(min-width:760px){.cc-pick{grid-template-columns:minmax(0,1.3fr) minmax(0,1fr)}}"
       ".cc-pick label{display:grid;gap:6px;font-size:13px;font-weight:700;color:var(--muted)}"
       ".cc-sel{min-height:48px;font:inherit;font-size:16px;font-weight:600;color:var(--ink);background:var(--card) var(--sel-arrow) no-repeat right 14px center;"
       "border:1px solid var(--line);border-radius:10px;padding:0 40px 0 14px;appearance:none;-webkit-appearance:none;width:100%}"
       ".cc-sel:focus-visible,.cc-in:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
       ".cc-card{margin:0 0 16px;padding:18px 20px;background:var(--card);border:1px solid var(--line);border-radius:14px}"
       ".cc-card h3{margin:0;font-size:21px;color:var(--ink)}.cc-card .cc-sub{margin:4px 0 0;color:var(--ink2);font-size:15px}"
       ".cc-big{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 12px;margin:14px 0 6px}"
       ".cc-big b{font:700 40px/1.05 Poppins,system-ui,sans-serif;color:var(--ink);font-variant-numeric:tabular-nums;letter-spacing:-.01em}"
       ".cc-big span{color:var(--ink2);font-size:15px}"
       ".cc-pcts{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:6px;margin:14px 0 0;padding:0;list-style:none}"
       ".cc-pcts li{padding:8px 6px;border:1px solid var(--line);border-radius:10px;background:var(--canvas2);text-align:center}"
       ".cc-pcts li.md{border-color:var(--ink);background:var(--card)}"
       ".cc-pcts b{display:block;font:700 17px/1.2 Poppins,system-ui,sans-serif;color:var(--ink);font-variant-numeric:tabular-nums}"
       ".cc-pcts small{display:block;font-size:12px;color:var(--muted);margin-top:2px}"
       ".cc-range{position:relative;height:30px;margin:16px 0 4px}"
       ".cc-range .tr{position:absolute;left:0;right:0;top:13px;height:4px;border-radius:2px;background:var(--rule)}"
       ".cc-range .r9{position:absolute;top:10px;height:10px;border-radius:5px;background:var(--accent);opacity:.3}"
       ".cc-range .r5{position:absolute;top:10px;height:10px;border-radius:5px;background:var(--accent);opacity:.75}"
       ".cc-range .md{position:absolute;top:5px;width:4px;height:20px;margin-left:-2px;border-radius:2px;background:var(--ink)}"
       ".cc-axis{display:flex;justify-content:space-between;font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}"
       ".cc-key{display:flex;flex-wrap:wrap;gap:6px 16px;margin:6px 0 0;font-size:12.5px;color:var(--ink2)}.cc-key i{display:inline-block;width:16px;height:8px;border-radius:4px;margin-right:6px;vertical-align:middle;background:var(--accent)}"
       ".cc-key .k9{opacity:.3}.cc-key .k5{opacity:.75}.cc-key .km{width:4px;height:14px;border-radius:2px;background:var(--ink)}"
       ".tile.key{box-shadow:inset 0 3px 0 var(--accent)}"
       ".cc-multi>[data-cc-line]+[data-cc-line],.cc-multi>[data-cc-line]+.cc-note{border-top:1px solid var(--line);margin-top:28px;padding-top:28px}.cc-multi>[data-cc-line]+.cc-note{padding-top:14px;margin-top:20px}"
       ".cc-rules{align-items:start}.cc-t td:first-child{min-width:10em}"
       ".cc-two .cta>div{display:flex;flex-direction:column;height:100%}.cc-two .cta .ld-buybtn{margin-top:auto;padding-top:20px}"
       ".cc-reset{margin:12px 0 0}.cc-reset button{min-height:44px;padding:0 4px;border:0;background:none;color:var(--ink2);font:inherit;font-size:14.5px;font-weight:600;text-decoration:underline;text-underline-offset:3px;cursor:pointer}"
       ".cc-reset button:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
       ".cc-bar{display:none}@media(max-width:899px){.cc-bar:not([hidden]){position:fixed;left:0;right:0;bottom:0;z-index:30;display:flex;align-items:center;gap:12px;padding:10px 16px calc(10px + env(safe-area-inset-bottom));"
       "background:var(--band);color:#fff;border-top:1px solid var(--band-line);box-shadow:0 -6px 20px rgba(0,0,0,.18)}"
       ".cc-bar span{font-size:12px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--band-soft)}.cc-bar b{font:700 22px/1 Poppins,system-ui,sans-serif;font-variant-numeric:tabular-nums}"
       ".cc-bar a{margin-left:auto;display:inline-flex;align-items:center;min-height:44px;padding:0 4px;color:#fff;font-weight:600;font-size:14.5px}}"
       ".cc-note{margin:10px 0 0;font-size:13.5px;color:var(--muted)}"
       ".cc-pw{margin:16px 0 0;padding:14px 16px;border-radius:12px;background:var(--canvas2);border:1px solid var(--line)}"
       ".cc-pw h4{margin:0 0 6px;font-size:15.5px;color:var(--ink)}.cc-pw p{margin:4px 0 0;font-size:14.5px;color:var(--ink2)}"
       ".cc-pwl{width:100%;border-collapse:collapse;font-size:14.5px;margin:8px 0 0}.cc-pwl th,.cc-pwl td{padding:6px 4px;border-bottom:1px solid var(--rule);text-align:right;font-variant-numeric:tabular-nums}"
       ".cc-pwl th:first-child,.cc-pwl td:first-child{text-align:left}.cc-pwl thead th{font-size:12.5px;color:var(--muted);font-weight:700}.cc-pwl tr:last-child td{border-bottom:0}"
       ".cc-pwl .tot{font-weight:700;color:var(--ink)}"
       ".cc-calc{display:grid;gap:16px}@media(min-width:900px){.cc-calc{grid-template-columns:minmax(0,1fr) minmax(0,1fr);align-items:start}}"
       ".cc-form{padding:18px 20px;background:var(--card);border:1px solid var(--line);border-radius:14px}"
       ".cc-form .row{grid-template-columns:1fr 140px}.cc-form .row label small{display:block;font-weight:400;color:var(--muted);font-size:13px}"
       ".cc-in{width:100%;min-height:44px;box-sizing:border-box;font:inherit;font-size:16px;color:var(--input-ink);background:var(--input);border:1px solid var(--input-line);border-radius:10px;padding:0 12px;text-align:right}"
       ".cc-form .field.has-pre .cc-in{padding-left:24px}.cc-form .field .pre{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:var(--muted);pointer-events:none}"
       ".cc-chk{display:flex;gap:10px;align-items:flex-start;padding:10px 0;border-bottom:1px solid var(--rule);font-size:15px;color:var(--ink)}"
       ".cc-chk input{width:22px;height:22px;margin:1px 0 0;flex:none;accent-color:var(--ink)}.cc-chk small{display:block;color:var(--muted);font-size:13px}"
       ".cc-err{display:none;margin:4px 0 0;font-size:13px;color:var(--warn-ink)}.cc-bad .cc-err{display:block}.cc-bad .cc-in{border-color:var(--warn-ink)}"
       ".cc-out{padding:18px 20px;background:var(--card);border:1px solid var(--line);border-radius:14px}@media(min-width:900px){.cc-out{position:sticky;top:72px}}"
       ".cc-out .lab{font-size:12px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}"
       ".cc-out .val{font:700 44px/1.05 Poppins,system-ui,sans-serif;color:var(--ink);font-variant-numeric:tabular-nums;margin:4px 0 2px}"
       ".cc-out .sub{color:var(--ink2);font-size:15px}"
       ".cc-out ul{margin:14px 0 0;padding:0;list-style:none}.cc-out li{display:flex;justify-content:space-between;gap:12px;padding:9px 0;border-bottom:1px solid var(--rule);font-size:15px;color:var(--ink2)}"
       ".cc-out li span:last-child{font-variant-numeric:tabular-nums;color:var(--ink);font-weight:600;white-space:nowrap}.cc-out li.tot{border-bottom:0;font-weight:700}.cc-out li.tot span{color:var(--ink)}"
       ".cc-out li[hidden]{display:none}"
       ".cc-next{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0 0}"
       ".cc-tw{overflow-x:auto;margin:12px 0 0;border:1px solid var(--line);border-radius:12px;background:var(--card)}"
       ".cc-tw:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
       ".cc-t{width:100%;border-collapse:collapse;font-size:14.5px;min-width:680px}.cc-t th,.cc-t td{padding:9px 12px;border-bottom:1px solid var(--rule);text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}"
       ".cc-t th:first-child,.cc-t td:first-child{text-align:left;white-space:normal}.cc-t thead th{font-size:13px;color:var(--muted);font-weight:700;background:var(--card);vertical-align:bottom}"
       ".cc-t tbody th{font-weight:600;color:var(--ink);text-align:left;min-width:170px}.cc-t tbody th a{color:var(--ink)}.cc-t tr:last-child td,.cc-t tr:last-child th{border-bottom:0}"
       ".cc-t td.md,.cc-t th.md{font-weight:700;color:var(--ink)}.cc-t .cc-grp th{background:var(--canvas2);font-size:13px;color:var(--muted);font-weight:700}"
       ".cc-bt{display:block;margin-top:2px;font-size:12.5px;font-weight:400;color:var(--muted)}"
       ".cc-swipe{display:none;margin:8px 0 0;font-size:13px;color:var(--muted)}"
       ".cc-rules{display:grid;gap:16px}@media(min-width:900px){.cc-rules{grid-template-columns:1fr 1fr}}"
       ".cc-rules .cc-card{margin:0}.cc-rules dl{margin:10px 0 0;display:grid;grid-template-columns:auto 1fr;gap:6px 14px;font-size:15px}"
       ".cc-rules dt{color:var(--muted)}.cc-rules dd{margin:0;color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums}"
       ".cc-rules ul{margin:10px 0 0;padding-left:20px;color:var(--ink2);font-size:15px}.cc-rules li{margin:5px 0}"
       ".cc-two{display:grid;gap:16px}@media(min-width:900px){.cc-two{grid-template-columns:1fr 1fr}}.cc-two .cta{grid-template-columns:1fr;height:100%;align-items:start}.cc-two .cta h2{margin-top:0;text-wrap:balance}"
       ".cc-dl{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0 0}"
       "details.cc-more{margin:12px 0 0;padding:0;border:0;background:none;box-shadow:none}details.cc-more>summary{display:inline-flex;align-items:center;gap:10px;min-height:46px;padding:0 16px;"
       "border:1.5px solid var(--ink);border-radius:10px;background:transparent;color:var(--ink);font-weight:600;cursor:pointer;list-style:none}"
       "details.cc-more>summary::-webkit-details-marker{display:none}details.cc-more>summary::after{content:'+';font-size:18px;line-height:1}details.cc-more[open]>summary::after{content:'\\2212'}"
       "details.cc-more>summary:focus-visible{outline:3px solid var(--focus);outline-offset:2px}details.cc-more[open]>summary{margin-bottom:4px}"
       ".cc-roles{display:grid;gap:8px;margin:12px 0 0;padding:0;list-style:none;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}"
       "main .cc-roles li>a.cc-r{display:flex;justify-content:space-between;align-items:center;gap:8px;min-height:48px;padding:0 14px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink);font-weight:600;text-decoration:none}"
       "main .cc-roles li>a.cc-r span{color:var(--muted);font-weight:600;font-variant-numeric:tabular-nums;white-space:nowrap}main .cc-roles li>a.cc-r:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
       "@media(max-width:599px){.cc-pwl thead{display:none}.cc-pwl,.cc-pwl tbody,.cc-pwl tr{display:block}.cc-pwl tr{padding:8px 0;border-bottom:1px solid var(--rule)}.cc-pwl tr:last-child{border-bottom:0}"
       ".cc-pwl td{display:flex;justify-content:space-between;gap:12px;padding:3px 0;border:0;text-align:right}.cc-pwl td::before{content:attr(data-label);color:var(--muted);text-align:left}"
       ".cc-pwl td:first-child{font-weight:700;color:var(--ink);font-size:15.5px}.cc-pwl td:first-child::before{content:none}}"
       "@media(max-width:599px){.cc-bt{display:none}.cc-t{min-width:600px}.cc-t th,.cc-t td{padding:9px 8px}.cc-t tbody th,.cc-t thead th:first-child{position:sticky;left:0;z-index:1;background:var(--card);box-shadow:1px 0 0 var(--rule)}"
       ".cc-swipe{display:block}.cc-big b{font-size:34px}.cc-out .val{font-size:38px}.cc-pcts{gap:4px}.cc-pcts b{font-size:14px}.cc-pcts li{padding:7px 4px}.cc-t tbody th a{display:block;padding:12px 0}.cc-form .row{grid-template-columns:1fr 118px}}"
       "</style>")

SHARED_CSS = ("<style>"
              ".ld-heroact{margin-bottom:24px}.ld-heroact .btn,.ld-heroact .st-btn2,p.rl-act .btn,p.rl-act .st-btn2{min-height:48px;box-sizing:border-box;display:inline-flex;align-items:center;justify-content:center;vertical-align:middle;margin:0}"
              "p.rl-act{display:flex;flex-wrap:wrap;gap:10px;align-items:center}"
              "@media(max-width:599px){.ld-heroact{display:grid;grid-template-columns:1fr;gap:10px}.ld-heroact .btn,.ld-heroact .st-btn2{width:100%}"
              "p.rl-act .btn,p.rl-act .st-btn2,.cc-next .btn,.cc-next .st-btn2{width:100%;white-space:normal;text-align:center}}"
              ".pg-nav{position:sticky;top:0;z-index:20;margin:0 -16px 8px;padding:8px 16px;background:var(--canvas);border-bottom:1px solid var(--rule)}"
              ".pg-nav ul{display:flex;gap:6px;margin:0;padding:0;list-style:none;overflow-x:auto;scrollbar-width:none}.pg-nav ul::-webkit-scrollbar{display:none}"
              ".pg-nav a{display:inline-flex;align-items:center;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid var(--line);background:var(--card);color:var(--ink2);font-size:14px;font-weight:600;text-decoration:none;white-space:nowrap}"
              ".pg-nav a[aria-current=true]{background:var(--ink);border-color:var(--ink);color:var(--card)}.pg-nav a:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
              "section.block{scroll-margin-top:64px}"
              "</style>")

PG_JS = ("<script>(function(){var n=document.querySelector('.pg-nav');if(!n||!('IntersectionObserver' in window))return;var L={};"
         "n.querySelectorAll('a').forEach(function(a){L[a.getAttribute('href').slice(1)]=a;});"
         "var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){n.querySelectorAll('a').forEach(function(a){a.removeAttribute('aria-current');});"
         "var a=L[e.target.id];if(a){a.setAttribute('aria-current','true');a.scrollIntoView({block:'nearest',inline:'nearest'});}}});},{rootMargin:'-30% 0px -60% 0px'});"
         "Object.keys(L).forEach(function(id){var s=document.getElementById(id);if(s)o.observe(s);});})();</script>")

# The calculator and the trade picker. Every figure it shows comes from the JSON block on the page; the math is the
# same as crew_day() above (the selftest runs both on the same inputs).
JS = r"""<script>(function(){
var D=JSON.parse(document.getElementById('cc-data').textContent);
var $=function(id){return document.getElementById(id)};
var sel=$('cc-role'),lvl=$('cc-level'),rate=$('cc-rate'),crew=$('cc-crew'),hrs=$('cc-hours'),oth=$('cc-other'),tax=$('cc-tax'),lv=$('cc-leave');
function money(x){return '$'+x.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2})}
function num(el){var v=String(el.value).replace(/[$,\s]/g,'');var k=/k$/i.test(v);v=parseFloat(v.replace(/k$/i,''));if(k)v*=1000;return isFinite(v)?v:NaN}
function line(){return D.lines[sel.value]}
function fill(){
  var L=line(),o=['p10','p25','median','p75','p90'],names={p10:'10th percentile',p25:'25th percentile',median:'Median',p75:'75th percentile',p90:'90th percentile'};
  var keep=lvl.value;lvl.innerHTML='';
  o.forEach(function(k){if(typeof L[k]==='number'){var op=document.createElement('option');op.value=k;op.textContent=names[k]+', '+money(L[k]);lvl.appendChild(op)}});
  (L.pw||[]).forEach(function(r,i){var op=document.createElement('option');op.value='pw'+i;op.textContent='Cook County public works, '+r.name+', '+money(r.base)+' plus '+money(r.fringes)+' fringes';lvl.appendChild(op)});
  var op=document.createElement('option');op.value='own';op.textContent='My own rate';lvl.appendChild(op);
  lvl.value=[].some.call(lvl.options,function(x){return x.value===keep})&&keep!=='own'?keep:'median';
  if(!lvl.value)lvl.value=lvl.options[0].value;
  var c=$('cc-card-'+L.role);
  document.querySelectorAll('[data-cc-card]').forEach(function(x){x.hidden=x!==c});
  document.querySelectorAll('[data-cc-line]').forEach(function(x){x.hidden=x.getAttribute('data-cc-line')!==sel.value});
  setRate();
}
function setRate(){var L=line(),v=lvl.value;if(v==='own')return calc();var r=v.slice(0,2)==='pw'?L.pw[+v.slice(2)].base:L[v];rate.value=r.toFixed(2);calc()}
function calc(){
  var L=line(),v=lvl.value,pw=v.slice(0,2)==='pw'?L.pw[+v.slice(2)]:null;
  var n=num(crew),h=num(hrs),r=num(rate),o=num(oth);if(!(o>=0))o=NaN;
  var ok=true;[[crew,n>=1&&n<=100],[hrs,h>0&&h<=24],[rate,r>=1&&r<1000],[oth,o>=0&&o<1000]].forEach(function(p){p[0].closest('.row').classList.toggle('cc-bad',!p[1]);if(p[1])p[0].removeAttribute('aria-invalid');else{p[0].setAttribute('aria-invalid','true');ok=false}});
  if(!ok){$('cc-total').textContent='Check the fields';$('cc-ph').textContent='';$('cc-bar-v').textContent='Check the fields';return}
  var reg=pw?Math.min(h,D.otAfter):h,ot=pw?Math.max(0,h-D.otAfter):0,mult=pw?pw.otMF:1;
  var c=function(x){return Math.round((x+1e-9)*100)/100};
  var wages=c(n*(reg*r+ot*r*mult)),t=tax.checked?c(wages*D.fica/100):0,lh=lv.checked?n*h/35:0,lvv=c(2*lh*r),fr=pw?c(n*h*pw.fringes):0,ox=c(n*h*o);
  var tot=c(wages+t+lvv+fr+ox);
  $('cc-total').textContent=money(tot);$('cc-bar-v').textContent=money(tot);
  $('cc-ph').textContent=money(tot/(n*h))+' per person-hour, '+money(tot/h)+' per hour for the whole crew';
  $('cc-o-wages').textContent=money(wages);
  $('cc-o-wl').textContent=(ot>0?'Wages ('+(n*ot).toLocaleString('en-US',{maximumFractionDigits:2})+' overtime hours at '+mult+' times base)':'Wages');
  $('cc-o-tax').textContent=money(t);$('cc-o-tax').closest('li').hidden=!tax.checked;
  $('cc-o-leave').textContent=money(lvv);$('cc-o-ll').textContent='Chicago paid leave earned ('+(2*lh).toLocaleString('en-US',{maximumFractionDigits:2})+' hours)';$('cc-o-leave').closest('li').hidden=!lv.checked;
  $('cc-o-fr').textContent=money(fr);$('cc-o-fr').closest('li').hidden=!pw;
  $('cc-o-oth').textContent=money(ox);$('cc-o-oth').closest('li').hidden=!(o>0);
  $('cc-pwnote').hidden=!pw;
}
sel.addEventListener('change',fill);lvl.addEventListener('change',setRate);
rate.addEventListener('input',function(){lvl.value='own';calc()});
[crew,hrs,oth].forEach(function(x){x.addEventListener('input',calc)});[tax,lv].forEach(function(x){x.addEventListener('change',calc)});
$('cc-reset').addEventListener('click',function(){sel.value=D.start;crew.value='2';hrs.value='8';oth.value='0';tax.checked=true;lv.checked=true;lvl.value='median';fill();});
var q=new URLSearchParams(location.search).get('trade');if(q&&D.lines[q])sel.value=q;
fill();
var bar=$('cc-bar'),sec=$('crew'),out=$('cc-out');
if(bar&&'IntersectionObserver' in window){var inSec=false,outSeen=false,up=function(){bar.hidden=!(inSec&&!outSeen)};
new IntersectionObserver(function(es){inSec=es[0].isIntersecting;up()}).observe(sec);
new IntersectionObserver(function(es){outSeen=es[0].isIntersecting;up()}).observe(out);}
})();</script>"""


def range_bar(ln, lo, hi, E):
    """The 10th to 90th percentile band, the 25th to 75th inside it, the median as a tick, on one shared scale."""
    if not all(isinstance(ln.get(k), (int, float)) for k in ("p10", "p25", "median", "p75", "p90")):
        return ""
    x = lambda v: f"{(v - lo) / (hi - lo) * 100:.1f}%"
    w = lambda a, b: f"{(b - a) / (hi - lo) * 100:.1f}%"
    return (f'<div class="cc-range" role="img" aria-label="{E(f"Hourly pay from {m2(ln["p10"])} at the 10th percentile to {m2(ln["p90"])} at the 90th, median {m2(ln["median"])}")}">'
            f'<span class="tr"></span><span class="r9" style="left:{x(ln["p10"])};width:{w(ln["p10"], ln["p90"])}"></span>'
            f'<span class="r5" style="left:{x(ln["p25"])};width:{w(ln["p25"], ln["p75"])}"></span><span class="md" style="left:{x(ln["median"])}"></span></div>'
            f'<div class="cc-axis" aria-hidden="true"><span>{m0(lo)}</span><span>{m0((lo + hi) / 2)}</span><span>{m0(hi)} an hour</span></div>'
            '<p class="cc-key" aria-hidden="true"><span><i class="k9"></i>10th to 90th percentile</span><span><i class="k5"></i>25th to 75th</span><span><i class="km"></i>Median</span></p>')


def scale(d):
    vals = [ln[k] for r in d["oews"]["roles"] for ln in r["lines"] for k in ("p10", "p90") if isinstance(ln.get(k), (int, float))]
    return (int(min(vals) // 5 * 5), int(-(-max(vals) // 5) * 5))


def pw_table(rows, E, cls="cc-pwl"):
    head = ('<thead><tr><th scope="col">Cook County line</th><th scope="col">Base</th>'
            + "".join(f'<th scope="col">{E(n)}</th>' for _, n in FRINGE_NAMES) + '<th scope="col">Total</th></tr></thead>')
    body = "".join(f'<tr><td>{E(title_case(r["trade"]))}{" (" + E(TYPE_NAMES.get(r["type"], r["type"])) + ")" if r["type"] != "ALL" else ""}</td><td data-label="Base">{m2(r["base"])}</td>'
                   + "".join(f'<td data-label="{E(n)}">{m2(r[k]) if r[k] is not None else "none listed"}</td>' for k, n in FRINGE_NAMES)
                   + f'<td class="tot" data-label="Total">{m2(r["total"])}</td></tr>' for r in rows)
    return f'<table class="{cls}">{head}<tbody>{body}</tbody></table>'


PCT_NOTE = '<p class="cc-note">Half earn less than the median and half earn more. A 25th percentile wage means a quarter of these workers earn less.</p>'


def role_card(d, role, lo, hi, E, rel, sub=False):
    """One trade's pay and public works rate. On the main page each helpers line gets its own card body."""
    out = []
    pw = pw_rows(d, role["key"])
    lead = ('<p>The Cook County schedule says landscaping work on public works falls under its laborer, operating engineer and truck driver lines, '
            'and landscape laborers are paid as laborers. Here is the laborer line; which line applies depends on the work done, so check with the Illinois Department of Labor.</p>'
            if role["key"] == "landscapers" else
            '<p>Lines on the Cook County schedule posted October 19, 2026 that this work usually falls under. Base pay plus the listed fringes, per hour.</p>')
    pw_box = ('<div class="cc-pw"><h4>Cook County public works rate</h4>'
              + (lead
                 + f'<div class="cc-tw" role="region" aria-label="{E("Cook County public works rates for " + PLURAL[role["key"]])}" tabindex="0" style="margin-top:8px">{pw_table(pw, E)}</div>'
                 if pw else
                 '<p>The Cook County construction schedule has no line for this work. Public works pay depends on the work done; check with the Illinois Department of Labor.</p>')
              + '</div>')
    for ln in role["lines"]:
        k = line_key(role, ln)
        emp = f'{ln["emp"]:,} people employed in the metro' if ln["emp"] else "BLS does not publish an employment count for this line"
        pcts = "".join(f'<li class="{"md" if key == "median" else ""}"><b>{m2(ln[key]) if ln[key] is not None else "n/a"}</b><small>{E(lab)}</small></li>' for key, lab in PCTS)
        h = "h2" if sub else "h3"
        out.append(f'<div data-cc-line="{E(k)}"{" hidden" if (not sub and len(role["lines"]) > 1 and ln is not role["lines"][0]) else ""}>'
                   f'<{h}>{E(disp(role, ln))}</{h}><p class="cc-sub">BLS occupation {E(ln["code"])}, {E(bls_title(ln["title"]))}. {E(emp[:1].upper() + emp[1:])}.</p>'
                   f'<div class="cc-big"><b>{m2(ln["median"])}</b><span>median hourly pay, Chicago metro, May 2025</span></div>'
                   f'{range_bar(ln, lo, hi, E)}<ul class="cc-pcts" aria-label="Hourly pay percentiles">{pcts}</ul>'
                   + ('' if (sub and len(role["lines"]) > 1) else PCT_NOTE) + '</div>')
    miss = (f'<p class="cc-note">BLS publishes no Chicago metro figures for {E(" or ".join(HELPER_NAMES.get(c, c).lower() + " (" + c + ")" for c in role["notPublished"]))}.</p>' if role["notPublished"] else "")
    sep = (PCT_NOTE if (sub and len(role["lines"]) > 1) else "")
    return (f'<div class="cc-card{" cc-multi" if sub and len(role["lines"]) > 1 else ""}" id="cc-card-{E(role["key"])}" data-cc-card>'
            + "".join(out) + sep + miss + pw_box + '</div>')


def lines_json(d):
    out = {}
    for role in d["oews"]["roles"]:
        pw = [{"name": title_case(r["trade"]), "base": r["base"], "fringes": r["fringes"], "otMF": r["otMF"]} for r in pw_rows(d, role["key"])]
        for ln in role["lines"]:
            out[line_key(role, ln)] = {"role": role["key"], **{k: ln[k] for k in ("p10", "p25", "median", "p75", "p90")}, "pw": pw}
    return out


def option_list(d, E, chosen):
    opts = ""
    for role in d["oews"]["roles"]:
        if len(role["lines"]) == 1:
            k = line_key(role, role["lines"][0])
            opts += f'<option value="{E(k)}"{" selected" if k == chosen else ""}>{E(role["label"])}</option>'
        else:
            opts += f'<optgroup label="{E(role["label"])}">' + "".join(
                f'<option value="{E(line_key(role, ln))}">{E(disp(role, ln))}</option>'
                for ln in role["lines"]) + '</optgroup>'
    return opts


def calculator(d, E, rel):
    fica = d["irs"]["ss"] + d["irs"]["medicare"]
    return (
        '<div class="cc-calc">'
        '<form class="cc-form" id="cc-form" novalidate onsubmit="return false">'
        '<div class="cc-pick" style="grid-template-columns:1fr"><label for="cc-level">Pay rate to use'
        '<select class="cc-sel" id="cc-level"></select></label></div>'
        '<div class="row"><label for="cc-crew">People on the crew</label><div class="field"><input class="cc-in" id="cc-crew" type="text" inputmode="decimal" value="2" autocomplete="off"></div>'
        '<p class="cc-err">Enter 1 to 100 people.</p></div>'
        '<div class="row"><label for="cc-hours">Hours each person works that day<small>Paid hours, drive time included if you pay it</small></label>'
        '<div class="field"><input class="cc-in" id="cc-hours" type="text" inputmode="decimal" value="8" autocomplete="off"></div><p class="cc-err">Enter 1 to 24 hours.</p></div>'
        '<div class="row"><label for="cc-rate">Hourly pay<small>Fills from the trade; type your own</small></label>'
        '<div class="field has-pre"><span class="pre">$</span><input class="cc-in" id="cc-rate" type="text" inputmode="decimal" value="0" autocomplete="off"></div><p class="cc-err">Enter hourly pay from $1 to $999.</p></div>'
        '<div class="row"><label for="cc-other">Your other costs per hour worked<small>Workers\' comp, unemployment insurance, health plan, uniforms</small></label>'
        '<div class="field has-pre"><span class="pre">$</span><input class="cc-in" id="cc-other" type="text" inputmode="decimal" value="0" autocomplete="off"></div><p class="cc-err">Enter $0 to $999 an hour.</p></div>'
        f'<label class="cc-chk"><input type="checkbox" id="cc-tax" checked><span>Count employer Social Security and Medicare, {fica:.2f}%'
        f'<small>{d["irs"]["ss"]:g}% plus {d["irs"]["medicare"]:g}% of wages, IRS Publication 15 ({d["irs"]["year"]}). Counted on wages only, not on public works fringes; ask your payroll provider how your fringes are taxed.</small></span></label>'
        '<label class="cc-chk" style="border-bottom:0"><input type="checkbox" id="cc-leave" checked><span>The crew works in Chicago'
        '<small>Covered employees earn 1 hour of paid leave and 1 hour of paid sick leave per 35 hours worked, each up to 40 hours in a 12-month period (City notice, July 1, 2026). Counted at the hourly pay. The ordinance has exceptions; check with the City\'s Office of Labor Standards.</small></span></label>'
        '</form>'
        '<div class="cc-out" id="cc-out" aria-live="polite"><div class="lab">Crew day cost</div><div class="val" id="cc-total">$0.00</div><div class="sub" id="cc-ph"></div>'
        '<ul><li><span id="cc-o-wl">Wages</span><span id="cc-o-wages">$0.00</span></li>'
        '<li><span>Public works fringes</span><span id="cc-o-fr">$0.00</span></li>'
        '<li><span>Employer Social Security and Medicare</span><span id="cc-o-tax">$0.00</span></li>'
        '<li><span id="cc-o-ll">Chicago paid leave earned</span><span id="cc-o-leave">$0.00</span></li>'
        '<li><span>Your other costs</span><span id="cc-o-oth">$0.00</span></li></ul>'
        f'<p class="cc-note" id="cc-pwnote" hidden>Public works: hours past {d["prevailing"]["otDailyAfter"]} on a weekday are paid at the overtime multiple of base pay the schedule lists. '
        'Some lines list extra amounts owed on overtime hours; those are in the full table and not in this total.</p>'
        '<p class="cc-note">Not counted: overtime past 40 hours in a week, state and federal unemployment tax, and your own costs unless you type them in. An estimate from public figures, not legal, tax or payroll advice; check with the agency.</p>'
        '<div class="cc-next"><a class="btn" href="' + rel + CALC_CONTRACTOR + '/">Set your contractor rate</a>'
        '<a class="st-btn2" href="' + rel + CALC_HANDYMAN + '/">Set your handyman rate</a></div>'
        '<p class="cc-reset"><button type="button" id="cc-reset">Reset to the example</button></p></div>'
        '</div>')


def pay_table(d, E, rel=None):
    rows = ""
    for role in d["oews"]["roles"]:
        if len(role["lines"]) > 1:
            grp = f'<a href="{SLUG_NAMES[role["key"]]}/">{E(role["label"])}</a>' if rel is not None else E(role["label"])
            rows += f'<tr class="cc-grp"><th scope="rowgroup" colspan="7">{grp}</th></tr>'
        for ln in role["lines"]:
            name = E(disp(role, ln))
            if rel is not None and len(role["lines"]) == 1:
                name = f'<a href="{SLUG_NAMES[role["key"]]}/">{name}</a>'
            name += f'<small class="cc-bt">{E(ln["code"])} {E(bls_title(ln["title"]))}</small>'
            rows += (f'<tr><th scope="row">{name}</th>' + "".join(f'<td class="{"md" if k == "median" else ""}">{m2(ln[k]) if ln[k] is not None else "n/a"}</td>' for k, _ in ORDER)
                     + (f'<td>{ln["emp"]:,}</td>' if ln["emp"] else '<td>not published</td>') + '</tr>')
    head = ('<thead><tr><th scope="col">Trade</th>'
            + "".join(f'<th scope="col" class="{"md" if k == "median" else ""}">{E(lab)}</th>' for k, lab in ORDER) + '<th scope="col">Employed</th></tr></thead>')
    return (f'<p class="cc-swipe">Swipe the table sideways for more columns.</p><div class="cc-tw" role="region" aria-label="Hourly pay by trade, Chicago metro, May 2025" tabindex="0">'
            f'<table class="cc-t">{head}<tbody>{rows}</tbody></table></div>')


def full_pw_table(d, E):
    head = ('<thead><tr><th scope="col">Trade</th><th scope="col">Type</th><th scope="col">Class</th><th scope="col">Base</th><th scope="col">Foreman</th>'
            + "".join(f'<th scope="col">{E(n)}</th>' for _, n in FRINGE_NAMES)
            + '<th scope="col">Total</th><th scope="col">Weekday OT</th><th scope="col">Added for OT hours at 1.5x</th><th scope="col">Added for OT hours at 2.0x</th></tr></thead>')
    body = ""
    for r in d["prevailing"]["rows"]:
        reg = {"E": " (east)", "W": " (west)"}.get(r["region"], "")
        body += (f'<tr><th scope="row">{E(title_case(r["trade"]))}{reg}</th><td>{E(TYPE_NAMES.get(r["type"], r["type"] or ""))}</td><td>{E(r["class"] or "")}</td>'
                 f'<td>{m2(r["base"])}</td><td>{m2(r["foreman"]) if r["foreman"] is not None else "none listed"}</td>'
                 + "".join(f'<td>{m2(r[k]) if r[k] is not None else "none listed"}</td>' for k, _ in FRINGE_NAMES)
                 + f'<td class="md">{m2(r["total"])}</td><td>{r["otMF"]:g}x</td>'
                 + f'<td>{m2(r["addOT15"]) if r["addOT15"] is not None else "none listed"}</td><td>{m2(r["addOT20"]) if r["addOT20"] is not None else "none listed"}</td></tr>')
    return (f'<div class="cc-tw" role="region" aria-label="Every line of the Cook County prevailing wage schedule" tabindex="0"><table class="cc-t" style="min-width:1100px">{head}<tbody>{body}</tbody></table></div>')


def rules_block(d, E):
    c, k = d["chicago"], d["cook"]
    return ('<div class="cc-rules">'
            '<div class="cc-card"><h3>City of Chicago</h3><p class="cc-sub">From July 1, 2026, employers with 4 or more employees</p>'
            f'<dl><dt>Minimum wage</dt><dd>{m2(c["minWage"])} an hour</dd><dt>Tipped workers</dt><dd>{m2(c["tipped"])} an hour</dd>'
            f'<dt>Overtime minimum</dt><dd>{m2(c["otMin"])} an hour</dd><dt>Tipped overtime</dt><dd>{m2(c["otTipped"])} an hour</dd></dl>'
            f'<ul><li>{E(c["domesticYouth"].replace("All Domestic Workers and Youth Workers", "Domestic workers and youth workers").replace("minimum wage", "minimum"))}.</li>'
            '<li>Paid leave for any reason: 1 hour for every 35 hours worked, up to 40 hours in a 12-month period, usable from the 90th day of work. Up to 16 hours carry over if not frontloaded.</li>'
            '<li>Paid sick and safe leave: 1 hour for every 35 hours worked, up to 40 hours in a 12-month period, usable from the 30th day. Up to 80 hours carry over.</li>'
            '<li>Both apply to employees who work at least 80 hours within any 120-day period.</li>'
            '<li>When a job ends, employers with 51 or more employees pay out up to 56 hours of unused paid leave; employers with 1 to 50 do not.</li></ul>'
            f'<p class="cc-note">From the City\'s notice, effective July 1, 2026 and last updated May 27, 2026. The rules are in Chicago Municipal Code 6-105 (minimum wage) and 6-130 (paid leave).</p></div>'
            '<div class="cc-card"><h3>Cook County</h3><p class="cc-sub">From July 1, 2026, in towns that use the County rate</p>'
            f'<dl><dt>Minimum wage</dt><dd>{m2(k["minWage"])} an hour</dd><dt>Tipped workers</dt><dd>{m2(k["tipped"])} an hour</dd></dl>'
            '<ul><li>Covers employees over 18 who work at least 2 hours in any two-week period in Cook County, for an employer with 4 or more employees (or as a domestic worker), when the employer has a business facility or license in the County.</li>'
            '<li>A town can opt out or set its own minimum wage. Chicago sets its own, shown in the City of Chicago box.</li></ul>'
            f'<p class="cc-note">From the County\'s notice of {E(k["posted"])}.</p></div>'
            '</div>')


def example_day(d, ln, pw=None):
    """2 people, 8 hours, at the line's median (or a public works line's base and fringes), taxes and Chicago leave in."""
    ss, med = d["irs"]["ss"], d["irs"]["medicare"]
    if pw:
        return crew_day(2, 8, pw["base"], ss, med, True, pw["fringes"], d["prevailing"]["otDailyAfter"], pw["otMF"])
    return crew_day(2, 8, ln["median"], ss, med, True)


def watch_line(d, E):
    w = load_watch()
    if not w or not w.get("allOk"):
        return ""
    return f' The City minimum wage page, the County notice, IRS Publication 15 and the state\'s prevailing wage page were re-checked {E(nice(w["checkedAt"][:10]))}.'


def nice(iso):
    import make_site as M
    return M.nice_date(iso)


def head_html(p, M, E, url, rel, ld, robots, title=None, desc=None):
    return M.HEAD.format(title=E(title or p["title"]), desc=E(desc or p["desc"]), url=url, rel=rel, shop=M.SHOP, ld=ld + CSS + SHARED_CSS,
                         bodycls=' class="ld-page"', robots=robots, analytics=M.analytics_tag())


def foot_html(d, M, E, rel):
    o, pv, c, k, i = d["oews"], d["prevailing"], d["chicago"], d["cook"], d["irs"]
    return (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            f'<p>Pay: U.S. Bureau of Labor Statistics, Occupational Employment and Wage Statistics, {E(o["period"])}, {E(o["area"])} metropolitan area, '
            f'<a href="{E(o["url"])}">metropolitan area file</a> (listed on the <a href="{E(o["tablesUrl"])}">OEWS tables page</a>), read Oct 27, 2026. '
            'Per the <a href="https://www.bls.gov/oes/oes_ques.htm">OEWS questions page</a>, wages are straight-time gross pay, before overtime and other premium pay, with tips in and benefits out, '
            'and the survey leaves out the self-employed and owners and partners in unincorporated firms. They are what employers pay employees, not billed rates.</p>'
            f'<p>Public works: Illinois Department of Labor, Cook County prevailing wage schedule, {E(pv["postedLine"])}, opened from the '
            f'<a href="{E(pv["pageUrl"])}">current prevailing rates page</a>, which says the rates apply to work performed on or after October 19, 2026, on public works projects. Read Oct 27, 2026.</p>'
            f'<p>Chicago: City of Chicago Office of Labor Standards, <a href="{E(c["noticeUrl"])}">minimum wage and paid leave notice</a> and '
            f'<a href="{E(c["pageUrl"])}">minimum wage page</a>. Cook County: Commission on Human Rights, <a href="{E(k["url"])}">minimum wage notice</a>. '
            f'Payroll tax: IRS, <a href="{E(i["url"])}">Publication 15 ({i["year"]})</a>. All read Oct 27, 2026.{watch_line(d, E)}</p>'
            '<p>ProofNotFluff is not affiliated with or endorsed by the U.S. Bureau of Labor Statistics, the Illinois Department of Labor, the City of Chicago, Cook County or the IRS.</p>'
            '<p>Public information, not legal, tax or payroll advice. Which wage, classification or leave rule applies to a job depends on the work and the employer; '
            'check with the agency: the Illinois Department of Labor for public works, the City\'s Office of Labor Standards for Chicago, the IRS for payroll tax.</p>'
            '<p>Made by ProofNotFluff with AI assistance from public government data. The page counts visits with Cloudflare Web Analytics, which sets no cookies.</p></div></footer>\n</body></html>')


def stats(d):
    by = {r["key"]: r for r in d["oews"]["roles"]}
    med = lambda k: by[k]["lines"][0]["median"]
    return by, med


def page_html(p):
    import make_site as M
    E = M.E
    url, rel = M.BASE + p["slug"] + "/", "../"
    d = load(p)
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), ("Free Chicago data", "chicago-data/"), (META["h1"], None)])
    if not d:
        return (head_html(p, M, E, url, rel, "", '<meta name="robots" content="noindex, nofollow">') + f'{crumb}<div class="ld-hero"><h1>{E(META["h1"])}</h1>'
                '<p class="lede">The figures are on their way.</p></div></main></body></html>')
    by, med = stats(d)
    lo, hi = scale(d)
    c, k, i = d["chicago"], d["cook"], d["irs"]
    fica = i["ss"] + i["medicare"]
    lede = (f'In the Chicago metro, half of electricians earn more than {m2(med("electricians"))} an hour, construction laborers {m2(med("laborers"))} '
            f'and janitors {m2(med("janitors"))} (BLS, May 2025).')
    intro = ('Pick a trade to see its full pay range and its Cook County public works rate, '
             'then work out what a crew day costs you once payroll tax and Chicago paid leave are counted.')
    ex = example_day(d, by[DEFAULT_ROLE]["lines"][0])
    tiles = ('<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">Crew day</div><div class="val">{m2(ex["total"])}</div><div class="sub">2 electricians, 8 hours each at the {m2(med("electricians"))} median, with payroll tax and Chicago paid leave</div></div>'
             f'<div class="tile"><div class="lab">Chicago</div><div class="val">{m2(c["minWage"])}</div><div class="sub">minimum wage an hour from July 1, 2026, employers with 4 or more employees</div></div>'
             f'<div class="tile"><div class="lab">Cook County</div><div class="val">{m2(k["minWage"])}</div><div class="sub">minimum wage an hour from July 1, 2026, where the County rate applies</div></div>'
             '<div class="tile"><div class="lab">Paid leave</div><div class="val">1 per 35</div><div class="sub">covered employees earn 1 hour of paid leave and 1 of paid sick leave per 35 hours worked in Chicago</div></div>'
             '</div><p class="asof">Pay from BLS, May 2025. Public works rates posted by the Illinois Department of Labor October 19, 2026. Minimum wages and leave from the City and County notices for July 1, 2026.</p>')
    cards = "".join(role_card(d, r, lo, hi, E, rel) for r in d["oews"]["roles"])
    # main page: only the default trade's card shows until the picker changes
    cards = cards.replace('data-cc-card>', 'data-cc-card hidden>').replace(f'id="cc-card-{DEFAULT_ROLE}" data-cc-card hidden>', f'id="cc-card-{DEFAULT_ROLE}" data-cc-card>')
    picker = ('<div class="cc-pick"><label for="cc-role">Trade'
              f'<select class="cc-sel" id="cc-role">{option_list(d, E, DEFAULT_ROLE)}</select></label></div>')
    calc = calculator(d, E, rel)
    data_js = json.dumps({"lines": lines_json(d), "fica": round(fica, 4), "otAfter": d["prevailing"]["otDailyAfter"], "start": DEFAULT_ROLE},
                         ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    matched = [r for key in ("electricians", "plumbers", "hvac", "carpenters", "laborers", "painters", "roofers") for r in pw_rows(d, key)]
    seen, mrows = set(), []
    for r in matched:
        if r["trade"] not in seen:
            seen.add(r["trade"])
            mrows.append(r)
    pw_sec = (f'<p>Illinois law sets what workers on public works must be paid: the base rate plus each fringe, for every hour. These are the Cook County lines for the trades on this page, '
              f'for work on or after October 19, 2026. On public works the schedule also sets overtime: hours over {d["prevailing"]["otDailyAfter"]} a day Monday to Friday, and every hour on Saturdays, Sundays and holidays, at the multiple it lists.</p>'
              f'<div class="cc-tw" role="region" aria-label="Cook County public works rates for the trades on this page" tabindex="0">{pw_table(mrows, E, "cc-t")}</div>'
              f'<details class="cc-more"><summary>Show all {len(d["prevailing"]["rows"])} lines of the Cook County schedule</summary>'
              f'{full_pw_table(d, E)}<p class="asof">"None listed" is a blank on the schedule. Type is the schedule\'s own split (building, highway, floating); class is the operating engineer or truck driver class; east and west truck driver rates split at Barrington Road.</p></details>'
              '<p class="asof">Which line applies to a worker depends on the work done, and the public body on the project must tell contractors to comply. For a classification question, check with the Illinois Department of Labor.</p>')
    role_links = "".join(f'<li><a class="cc-r" href="{SLUG_NAMES[r["key"]]}/">{E(r["label"])}<span>{m2(r["lines"][0]["median"]) if len(r["lines"]) == 1 else str(len(r["lines"])) + " kinds"}</span></a></li>' for r in d["oews"]["roles"])
    pay_sec = (pay_table(d, E, rel="")
               + f'<p class="asof">Straight-time hourly pay, before overtime and premium pay, May 2025. "Not published" means BLS gives the wages but no employment count. '
               + (f'BLS publishes no Chicago metro figures for {E(" or ".join(HELPER_NAMES.get(c, c).lower() + " (" + c + ")" for r in d["oews"]["roles"] for c in r["notPublished"]))}. ' if any(r["notPublished"] for r in d["oews"]["roles"]) else "")
               + 'Employment leaves out the self-employed.</p>'
               f'<div class="cc-dl"><a class="st-btn2" href="{CSV_PAY}" download>Download the pay table (CSV)</a><a class="st-btn2" href="{CSV_PW}" download>Download the Cook County schedule (CSV)</a></div>'
               f'<h3 style="margin-top:22px">One page per trade</h3><ul class="cc-roles">{role_links}</ul>')
    two = ('<section class="block" id="next"><div class="cc-two">'
           + "".join(f'<div class="cta ld-cta"><div><h2>{E(x["title"])}</h2><p>{E(x["text"])}</p>'
                     f'<p class="ld-buybtn"><a class="btn" href="{rel}{E(x["slug"])}/">{E(x["button"])}</a></p></div></div>' for x in p["next"])
           + '</div></section>')
    method = '<section class="block" id="how"><h2>How this page is made</h2>' + "".join(f"<p>{E(x)}</p>" for x in p["method"]) + "</section>"
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(META["h1"])}</h1><p class="lede">{E(lede)}</p>'
            '<div class="ld-heroact rl-act"><a class="btn" href="#crew">Work out a crew day</a><a class="st-btn2" href="#pay">See pay for every trade</a></div></div>'
            + tiles
            + M_nav(E)
            + f'<section class="block" id="crew"><h2>Pick a trade, then price the crew day</h2><p>{E(intro)}</p>{picker}{cards}{calc}'
            f'<p class="asof">The example opens on 2 electricians for 8 hours at the median: {m2(ex["total"])} for the day, '
            f'{m2(ex["wages"])} of it wages, {m2(ex["tax"])} Social Security and Medicare and {m2(ex["leave"])} of Chicago paid leave earned.</p></section>'
            f'<section class="block" id="pay"><h2>Hourly pay for every trade</h2>{pay_sec}</section>'
            f'<section class="block" id="public"><h2>Cook County public works rates</h2>{pw_sec}</section>'
            f'<section class="block" id="rules"><h2>Minimum wage and paid leave</h2>{rules_block(d, E)}</section>'
            + two + method + M.faq_block(p["faq"]).replace('<section class="block">', '<section class="block" id="faq">', 1)
            + f'<p class="rl-act"><a class="btn" href="#crew">Work out a crew day</a> <a class="st-btn2" href="{rel}chicago-data/">More free Chicago data</a></p>'
            f'<div class="cc-bar" id="cc-bar" hidden><span>Crew day</span><b id="cc-bar-v">{m2(ex["total"])}</b><a href="#cc-out">See the breakdown</a></div>'
            f'<script type="application/json" id="cc-data">{data_js}</script>{JS}')
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}
    data_ld = {"@context": "https://schema.org", "@type": "Dataset", "name": META["h1"], "description": p["desc"], "url": url, "isAccessibleForFree": True,
               "creator": {"@type": "Organization", "name": "ProofNotFluff"}, "isBasedOn": [d["oews"]["url"], d["prevailing"]["pageUrl"], c["noticeUrl"]],
               "spatialCoverage": "Chicago, Illinois", "temporalCoverage": "2025-05/2026-10",
               "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": url + CSV_PAY},
                                {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": url + CSV_PW}]}
    return head_html(p, M, E, url, rel, M.ld_tags(crumb_ld, faq_ld, data_ld), robots) + body + foot_html(d, M, E, rel)


def M_nav(E):
    items = [("crew", "Crew day"), ("pay", "Pay by trade"), ("public", "Public works"), ("rules", "Minimum wage"), ("faq", "Questions")]
    return ('<nav class="otp" aria-label="On this page"><div class="otp-in">' + "".join(f'<a href="#{i}">{E(t)}</a>' for i, t in items) + '</div></nav>')


def sub_page(p, d, role, M, E):
    """/chicago-crew-cost/<trade>/: the trade's own numbers, a worked crew day and its public works lines."""
    slug = SLUG_NAMES[role["key"]]
    url, rel = M.BASE + p["slug"] + "/" + slug + "/", "../../"
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    lab = role["label"]
    one = role["lines"][0] if len(role["lines"]) == 1 else None
    h1 = f"{H1_NAMES[role['key']]} Pay in Chicago"
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), (META["h1"], p["slug"] + "/"), (lab, None)])   # 3 levels: a 4th runs off a phone
    lo, hi = scale(d)
    pw = pw_rows(d, role["key"])
    i = d["irs"]
    if one:
        ex = example_day(d, one)
        lede = (f'Half of the Chicago metro\'s {E(PLURAL[role["key"]])} earn more than {m2(one["median"])} an hour, and the middle half earn '
                f'{m2(one["p25"])} to {m2(one["p75"])} (BLS, May 2025). A 2-person crew for an 8-hour day at the median costs {m2(ex["total"])} with payroll tax and Chicago paid leave counted.')
        desc = (f'{lab} in the Chicago metro: median {m2(one["median"])} an hour, {m2(one["p10"])} to {m2(one["p90"])} from the 10th to the 90th percentile (BLS, May 2025), '
                + ('the Cook County public works rate with fringes, ' if pw else '') + 'and what a crew day costs.')
    else:
        pub = [ln for ln in role["lines"]]
        lede = (f'BLS publishes Chicago metro pay for {len(pub)} kinds of construction helper (May 2025), with medians from '
                f'{m2(min(ln["median"] for ln in pub))} to {m2(max(ln["median"] for ln in pub))} an hour. Each line below has its own pay range and a worked crew day.')
        desc = f'Construction helper pay in the Chicago metro by trade: medians from {m2(min(ln["median"] for ln in pub))} to {m2(max(ln["median"] for ln in pub))} an hour (BLS, May 2025), and what a crew day costs.'
    card = role_card(d, role, lo, hi, E, rel, sub=True).replace('data-cc-card', '')
    ex_rows = ""
    for ln in role["lines"]:
        e = example_day(d, ln)
        ex_rows += (f'<tr><th scope="row">{E(disp(role, ln))} at the median, {m2(ln["median"])}</th><td class="md">{m2(e["total"])}</td><td>{m2(e["wages"])}</td><td>{m2(e["tax"])}</td>'
                    f'<td>{m2(e["leave"])}</td><td>{m2(0)}</td></tr>')
    for r in pw:
        e = example_day(d, None, r)
        ex_rows += (f'<tr><th scope="row">Cook County public works, {E(title_case(r["trade"]))}, {m2(r["base"])} base plus {m2(r["fringes"])} fringes</th><td class="md">{m2(e["total"])}</td><td>{m2(e["wages"])}</td><td>{m2(e["tax"])}</td>'
                    f'<td>{m2(e["leave"])}</td><td>{m2(e["fringes"])}</td></tr>')
    ex_tbl = ('<p class="cc-swipe">Swipe the table sideways for more columns.</p>'
              f'<div class="cc-tw" role="region" aria-label="{E("A worked crew day for " + PLURAL[role["key"]])}" tabindex="0"><table class="cc-t"><thead><tr><th scope="col">2 people, 8 hours each</th>'
              '<th scope="col" class="md">Crew day</th><th scope="col">Wages</th><th scope="col">Social Security and Medicare</th><th scope="col">Chicago paid leave earned</th><th scope="col">Public works fringes</th></tr></thead>'
              f'<tbody>{ex_rows}</tbody></table></div>'
              f'<p class="asof">Social Security {i["ss"]:g}% and Medicare {i["medicare"]:g}% of wages (IRS, {i["year"]}). Chicago paid leave: 1 hour of paid leave and 1 of paid sick leave per 35 hours worked, valued at the hourly pay. '
              'Workers\' comp, unemployment insurance and benefits are not in these totals; add yours in the calculator. An estimate from public figures, not legal, tax or payroll advice; check with the agency.</p>')
    k0 = line_key(role, role["lines"][0])
    nxt = (f'<p class="rl-act" style="margin-top:14px"><a class="btn" href="../?trade={E(k0)}#crew">Price your own crew day</a>'
           f'<a class="st-btn2" href="{rel}{CALC_CONTRACTOR}/">Set your contractor rate</a><a class="st-btn2" href="{rel}{CALC_HANDYMAN}/">Set your handyman rate</a></p>')
    others = "".join(f'<li><a class="cc-r" href="../{SLUG_NAMES[r["key"]]}/">{E(r["label"])}<span>{m2(r["lines"][0]["median"]) if len(r["lines"]) == 1 else str(len(r["lines"])) + " kinds"}</span></a></li>'
                     for r in d["oews"]["roles"] if r["key"] != role["key"])
    faq = []
    if one:
        faq.append((f"How much does {('an ' if SINGULAR[role['key']][0] in 'aeiouH' else 'a ') + SINGULAR[role['key']]} make an hour in Chicago?",
                    f"In the Chicago-Naperville-Elgin metro the median is {m2(one['median'])} an hour, from BLS's May 2025 survey of employers. "
                    f"The 10th percentile is {m2(one['p10'])} and the 90th is {m2(one['p90'])}."))
    if pw:
        r = pw[0]
        if role["key"] == "landscapers":
            ans = (f"The Cook County schedule posted October 19, 2026 says landscape laborers are covered by its laborer line: {m2(r['base'])} an hour base plus "
                   f"{m2(r['fringes'])} of fringes, {m2(r['total'])} in all, for public works. Other landscaping work can fall under its operating engineer or truck driver lines; "
                   "check with the Illinois Department of Labor.")
        else:
            ans = (f"The Cook County schedule posted October 19, 2026 lists {title_case(r['trade'])} at {m2(r['base'])} an hour base plus {m2(r['fringes'])} of fringes, "
                   f"{m2(r['total'])} in all, for public works. Which line applies depends on the work; check with the Illinois Department of Labor.")
        faq.append((f"What is the Cook County prevailing wage for {PLURAL[role['key']]}?", ans))
    faq.append(("Are these the rates I should charge customers?", "No. BLS counts the straight-time pay employers give employees, before overtime and premium pay and without benefits. It leaves out the self-employed, and a rate you bill a customer also has to cover your costs and profit."))
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(h1)}</h1><p class="lede">{lede}</p></div>'
            f'<section class="block" id="pay">{card}{nxt}</section>'
            f'<section class="block" id="day"><h2>A worked crew day</h2>{ex_tbl}</section>'
            f'<section class="block" id="rules"><h2>Minimum wage and paid leave</h2>{rules_block(d, E)}</section>'
            f'<section class="block" id="more"><h2>Other trades</h2><ul class="cc-roles">{others}</ul>'
            f'<p class="rl-act" style="margin-top:14px"><a class="st-btn2" href="../">Back to What a Chicago Crew Costs</a></p></section>'
            + M.faq_block(faq)
            + f'<p class="rl-act"><a class="btn" href="../?trade={E(k0)}#crew">Price your own crew day</a> <a class="st-btn2" href="../">Back to What a Chicago Crew Costs</a></p>')
    title = f"{h1}: Hourly Wages, Public Works Rate, Crew Cost | ProofNotFluff" if pw else f"{h1}: Hourly Wages and Crew Cost | ProofNotFluff"
    return head_html(p, M, E, url, rel, M.ld_tags(crumb_ld, faq_ld), robots, title=title, desc=desc) + body + foot_html(d, M, E, rel)


def csv_pay(d):
    b = io.StringIO()
    w = csv.writer(b, lineterminator="\n")
    w.writerow(["trade_group", "bls_code", "bls_title", "employed", "hourly_10th", "hourly_25th", "hourly_median", "hourly_75th", "hourly_90th", "hourly_mean",
                "area", "period", "source"])
    for r in d["oews"]["roles"]:
        for ln in r["lines"]:
            w.writerow([r["label"], ln["code"], ln["title"], ln["emp"] if ln["emp"] is not None else "", *[ln[k] if ln[k] is not None else "" for k in ("p10", "p25", "median", "p75", "p90", "mean")],
                        d["oews"]["area"], d["oews"]["period"], d["oews"]["url"]])
    return b.getvalue()


def csv_pw(d):
    b = io.StringIO()
    w = csv.writer(b, lineterminator="\n")
    w.writerow(["trade", "region", "type", "class", "base", "foreman", "ot_weekday", "ot_saturday", "ot_sunday", "ot_holiday", "health_welfare", "pension", "vacation",
                "training", "other_insurance", "add_ot_1_5x", "add_ot_2_0x", "fringes_total", "base_plus_fringes", "posted", "source"])
    for r in d["prevailing"]["rows"]:
        w.writerow([r["trade"], r["region"] or "", r["type"] or "", r["class"] or ""]
                   + ["" if r[k] is None else r[k] for k in ("base", "foreman", "otMF", "otSa", "otSu", "otHol", "hw", "pension", "vac", "trng", "otherIns", "addOT15", "addOT20", "fringes", "total")]
                   + [d["prevailing"]["posted"], d["prevailing"]["pageUrl"]])
    return b.getvalue()


def extra_pages(p):
    d = load(p)
    if not d:
        return []
    import make_site as M
    out = [(CSV_PAY, csv_pay(d)), (CSV_PW, csv_pw(d))]
    for role in d["oews"]["roles"]:
        out.append((f'{SLUG_NAMES[role["key"]]}/index.html', sub_page(p, d, role, M, M.E)))
    return out


def selftest():
    sys.path.insert(0, HERE)
    import make_site as M
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("slug") == "chicago-crew-cost"][0]
    d = load(spec)
    assert d, "data.json missing"
    # crew day math: 2 people, 8 hours, $20: wages 320, tax 24.48, leave 2*(16/35)*20
    e = crew_day(2, 8, 20, 6.2, 1.45, True)
    assert abs(e["wages"] - 320) < 1e-9 and abs(e["tax"] - 24.48) < 1e-9 and e["leave"] == round(2 * 16 / 35 * 20, 2) and e["total"] == round(e["wages"] + e["tax"] + e["leave"], 2)
    e = crew_day(1, 10, 50, 6.2, 1.45, False, 40, 8, 1.5)
    assert abs(e["wages"] - (8 * 50 + 2 * 75)) < 1e-9 and abs(e["fringes"] - 400) < 1e-9 and e["leave"] == 0 and e["otHours"] == 2
    # every Cook row: total is base plus the listed fringes
    for r in d["prevailing"]["rows"]:
        assert abs(r["total"] - (r["base"] + sum(r[k] or 0 for k, _ in FRINGE_NAMES))) < 0.006, r["trade"]
    # the FAQ's worked numbers (written in site/pages.json) still match the data
    ex = example_day(d, [r for r in d["oews"]["roles"] if r["key"] == DEFAULT_ROLE][0]["lines"][0])
    faq = json.dumps(spec["faq"])
    for want in (m2(ex["total"]), "$49.21", "$29.27", "$22.25", "$48.44", "$53.00", "$39.11", "$17.05", "$12.96", "$25.58"):
        assert want in faq, f"FAQ figure {want} not in the FAQ"
    lab = [r for r in d["oews"]["roles"] if r["key"] == "laborers"][0]["lines"][0]
    lpw = pw_rows(d, "laborers")[0]
    assert (m2(lab["median"]), m2(lab["p25"]), m2(lab["p75"]), m2(lpw["base"]), m2(lpw["fringes"])) == ("$29.27", "$22.25", "$48.44", "$53.00", "$39.11")
    assert (m2(d["chicago"]["minWage"]), m2(d["chicago"]["tipped"]), m2(d["chicago"]["otMin"])) == ("$17.05", "$12.96", "$25.58")
    html = page_html(spec)
    assert html.count("<h1>") == 1 and "—" not in html and "–" not in html, "one h1, no dashes"
    assert "$17.05" in html and "$15.40" in html and "7.65%" in html and "$49.21" in html, "headline figures"
    assert f'href="../{CALC_CONTRACTOR}/"' in html and f'href="../{CALC_HANDYMAN}/"' in html, "links to the rate calculators"
    assert html.count('data-cc-card hidden') == len(d["oews"]["roles"]) - 1, "one trade card shown"
    for relp, pg in extra_pages(spec):
        assert "—" not in pg and "–" not in pg, relp
        if relp.endswith("index.html"):
            assert pg.count("<h1>") == 1, relp
    print("dp_crew_cost selftest: ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
