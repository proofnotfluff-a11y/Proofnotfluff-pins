#!/usr/bin/env python3
"""Chicago Snow Season Board for Plow Owners (/chicago-snow-season/), a free data page (site/pages.json kind "datapage",
module dp_snow). Todd's go, Oct 27, 2026 ("Let's do them all", coo/PARALLEL_BUILDS.md; research_notes/kimi-2026-10-27-r10.md
item 1).

Data: site/datapages/dp_snow/daily.json (tools/dp_snow_fetch.py, GitHub Actions, daily October to April): NOAA NCEI
GHCN-Daily snowfall (SNOW) and snow depth (SNWD) at the O'Hare and Midway stations NOAA's own search names. Everything
on the page is counted here from those daily values; nothing is typed in.

What counts: a plowable day at a trigger is one station day whose new snowfall is at or over the trigger depth. A winter
is July 1 to June 30. A winter with more than MAXMISS snow-month days (October to May) missing is shown as incomplete
and left out of every summary. Past winters only: the page never forecasts the coming winter, never gives snowfall for
a neighborhood, and shows no prices.

The snow pricing calculator (tools/make_site.py snow_page) reads calc_counts() to fill its expected pushes.

Usage: python3 tools/dp_snow.py --selftest
"""
import datetime as dt, json, math, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "site", "datapages", "dp_snow", "daily.json")
SLUG = "chicago-snow-season"
TRIGGERS = (1, 2, 3, 6)
DEFAULT = ("ohare", 2)
MAXMISS = 3
LOW_P, HIGH_P = 0.2, 0.8
MONTHS = ((10, "Oct"), (11, "Nov"), (12, "Dec"), (1, "Jan"), (2, "Feb"), (3, "Mar"), (4, "Apr"), (5, "May"))
MONTH_NAMES = ("", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
NWS = ("https://www.weather.gov/lot/snowclimatology", "National Weather Service Chicago, Snow Climatology")
GHCN = ("https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily",
        "NOAA NCEI, Global Historical Climatology Network daily (GHCN-Daily)")
NWS_NOTE = (f'<p class="sn-note">For comparison at 1 inch, the National Weather Service\'s Chicago office puts O\'Hare\'s normal first day with 1 inch or more at '
            f'December 7 and the last at March 20, using 1991 to 2020 (<a href="{NWS[0]}" rel="noopener">Snow Climatology</a>). '
            'It uses different years and methods, so its dates may not match this page.</p>')
STATION_NOTE = {
    "ohare": "Its day runs midnight to midnight, local standard time.",
    "midway": ("It is a NOAA cooperative observer station. Its name puts it about 3 miles southwest of the airport, and it has the fullest snowfall record near Midway in NOAA's file. "
               "Its day is the 24 hours before the observer's daily reading, so it may not run midnight to midnight. "
               "NOAA's automated station at the airport itself reports snowfall on too few days to use."),
}

META = {"h1": "Chicago Snow Season Board for Plow Owners",
        "card": "Plowable days a winter at 1, 2, 3 and 6 inch triggers from 30 winters of NOAA records at O'Hare and Midway, and this winter so far.",
        "keywords": "snow plow plowable pushes trigger depth seasonal contract chicago o'hare midway snowfall winter salt"}

FAQ = [
    ("How many times do you plow in a Chicago winter?", None),   # the answer carries this winter's counts (faq())
    ("What counts as a plowable day here?",
     "One day at the weather station with new snowfall at or over your trigger depth. Two days in a row that each reach the trigger count as two. A storm that "
     "splits its snow across two days counts only on a day that alone reached the trigger."),
    ("Is this a forecast for this winter?",
     "No. It counts past winters only. Nobody can tell you this winter's count ahead of time, so price a seasonal contract with "
     "a cushion for a heavy winter."),
    ("Does my neighborhood get the same snow?", None),   # the answer uses the two stations' own gap (faq())
    ("Why are some winters marked incomplete?",
     f"NOAA's daily file has more than {MAXMISS} days with no snowfall value between October and May in those winters. "
     "A missing day could hide a storm, so those winters are left out of every count on this page."),
]


def faq(s0, sd=None):
    a1 = (f"It depends on your trigger. At O'Hare, the middle winter of the last {s0['n']} complete ones had {pushes(s0['mid'])} with "
          f"{inch(s0['t'])} or more of new snow; a light winter had {num(s0['low'])} or fewer and a heavy one {num(s0['high'])} or more. "
          "Pick your trigger and station at the top of this page for your counts.")
    a4 = "Not always. These are two weather stations, one at O'Hare and one near Midway. Check your own storm records too."
    if sd and {"ohare", "midway"} <= set(sd):
        mw = {r["y"]: r for r in sd["midway"]["rows"] if r["complete"] and not r["current"]}
        pairs = [(abs(r["snow"] - mw[r["y"]]["snow"]), r, mw[r["y"]]) for r in sd["ohare"]["rows"] if r["complete"] and not r["current"] and r["y"] in mw]
        if pairs:
            _, o, m = max(pairs, key=lambda x: (x[0], -x[1]["y"]))
            a4 = (f"Not always. Even these two stations can differ a lot: in {o['label']}, O'Hare had {o['snow']:.1f} inches and Midway "
                  f"{m['snow']:.1f}. Check your own storm records too.")
    return [(q, a if a else (a1 if i == 0 else a4)) for i, (q, a) in enumerate(FAQ)]


def load():
    return json.load(open(DATA, encoding="utf-8")) if os.path.isfile(DATA) else None


def winter_of(d):
    return d.year if d.month >= 7 else d.year - 1


def key(d):
    """Order within a winter: July 1 is first, June 30 last; Feb 29 sorts before March 1."""
    return ((d.month - 7) % 12, d.day)


def snow_month(d):
    return d.month >= 10 or d.month <= 5


def wlabel(y):
    return f"{y}-{str(y + 1)[2:]}"


def day_words(d, year=False):
    return f"{MONTH_NAMES[d.month]}\u00a0{d.day}" + (f", {d.year}" if year else "")


def short_day(d):
    return f"{MONTH_NAMES[d.month][:3]}\u00a0{d.day}"


def nr(vals, p):
    """Nearest-rank percentile of a sorted list (an actual winter's value)."""
    return vals[max(0, math.ceil(p * len(vals)) - 1)]


def num(x):
    return f"{x:g}" if isinstance(x, float) and x != int(x) else f"{int(x)}"


def winters(s, first, last):
    """One row per winter from first to last + 1 (the current one, to date)."""
    start = dt.date.fromisoformat(s["start"])
    end = dt.date.fromisoformat(s["end"])
    rows = {y: {"y": y, "label": wlabel(y), "miss": 0, "smiss": 0, "snow": 0.0, "ground": 0, "dates": {t: [] for t in TRIGGERS}}
            for y in range(first, last + 2)}
    for i, v in enumerate(s["snow"]):
        d = start + dt.timedelta(i)
        r = rows.get(winter_of(d))
        if r is None:
            continue
        g = s["snwd"][i]
        if snow_month(d):
            r["miss"] += v is None
            r["smiss"] += g is None
        if g is not None and g >= 1:
            r["ground"] += 1
        if v is None:
            continue
        r["snow"] += v
        for t in TRIGGERS:
            if v >= t:
                r["dates"][t].append(d)
    out = []
    for y in range(first, last + 2):
        r = rows[y]
        r["current"] = y == last + 1
        r["complete"] = r["miss"] <= MAXMISS
        r["snow"] = round(r["snow"], 1)
        r["groundOk"] = r["smiss"] <= MAXMISS
        r["events"] = {t: len(r["dates"][t]) for t in TRIGGERS}
        out.append(r)
    return out, end


REF = dt.date(2001, 7, 1)   # a winter with no Feb 29, to turn dates into days since July 1 and back


def mid_day(days):
    """The median date as a (month offset, day) key: halfway between the two middle dates when the count is even,
    rounded to the nearest day (a half day rounds later)."""
    if not days:
        return None
    offs = [(key_day(key(d), REF.year) - REF).days for d in days]
    m = math.floor(statistics.median(offs) + 0.5)
    return key(REF + dt.timedelta(m))


def summary(rows, end, t):
    past = [r for r in rows if not r["current"] and r["complete"]]
    cur = rows[-1]
    n = len(past)
    counts = sorted(r["events"][t] for r in past)
    low, high = nr(counts, LOW_P), nr(counts, HIGH_P)
    mid = statistics.median(counts)
    firsts = sorted((r["dates"][t][0] for r in past if r["dates"][t]), key=key)
    lasts = sorted((r["dates"][t][-1] for r in past if r["dates"][t]), key=key)
    fewest = min(past, key=lambda r: (r["events"][t], -r["y"]))
    most = max(past, key=lambda r: (r["events"][t], r["y"]))
    months = []
    for m, name in MONTHS:
        tot = sum(1 for r in past for d in r["dates"][t] if d.month == m)
        months.append({"m": m, "name": name, "avg": tot / n, "winters": sum(1 for r in past if any(d.month == m for d in r["dates"][t]))})
    if months[-1]["avg"] == 0:   # May shows only when a past winter had a push in May
        months.pop()
    to_date = sorted(sum(1 for d in r["dates"][t] if key(d) <= key(end)) for r in past)
    snow_to_date = None
    return {"t": t, "n": n, "counts": counts, "low": low, "high": high, "mid": mid, "lowN": sum(1 for c in counts if c <= low),
            "highN": sum(1 for c in counts if c >= high), "fewest": fewest, "most": most, "months": months,
            "firstMid": mid_day(firsts),
            "firsts": firsts, "lasts": lasts,
            "lastMid": mid_day(lasts),
            "none": n - len(firsts), "cur": cur["events"][t], "curDates": cur["dates"][t],
            "toDate": statistics.median(to_date), "toDateLow": nr(to_date, LOW_P), "toDateHigh": nr(to_date, HIGH_P),
            "end": end, "incomplete": [r for r in rows if not r["current"] and not r["complete"]], "snowToDate": snow_to_date}


def key_day(k, year):
    """A (month offset, day) key back to a date in the winter starting in year (for words only; never Feb 29 drift)."""
    m = (k[0] + 7 - 1) % 12 + 1
    y = year if m >= 7 else year + 1
    try:
        return dt.date(y, m, k[1])
    except ValueError:
        return dt.date(y, m, 28)


def cumulative(rows, end, t):
    """Running count of plowable days, October 1 to April 30, for the middle of past winters (with light and heavy
    edges) and for this winter to date."""
    past = [r for r in rows if not r["current"] and r["complete"]]
    cur = rows[-1]
    y0 = cur["y"]
    xs, d = [], dt.date(y0, 10, 1)
    while d <= dt.date(y0 + 1, 4, 30):
        xs.append(d)
        d += dt.timedelta(1)
    mid, lo, hi, now = [], [], [], []
    for x in xs:
        vals = sorted(sum(1 for e in r["dates"][t] if key(e) <= key(x)) for r in past)
        mid.append(statistics.median(vals))
        lo.append(nr(vals, LOW_P))
        hi.append(nr(vals, HIGH_P))
        if x <= end:
            now.append(sum(1 for e in cur["dates"][t] if key(e) <= key(x)))
    return {"x": [f"{MONTH_NAMES[x.month][:3]} {x.day}" for x in xs], "start": xs[0].isoformat(), "mid": mid, "lo": lo, "hi": hi, "now": now}


def station_data(d):
    out = {}
    for s in d["stations"]:
        rows, end = winters(s, d["winters"][0], d["winters"][1])
        out[s["key"]] = {"s": s, "rows": rows, "end": end, "sum": {t: summary(rows, end, t) for t in TRIGGERS},
                         "cum": {t: cumulative(rows, end, t) for t in TRIGGERS}}
    return out


def calc_counts():
    """For the snow pricing calculator: {station: {"label", "end", "n", "t": {trigger: [light, middle, heavy]}}}."""
    d = load()
    if not d:
        return None
    out = {}
    for k, v in station_data(d).items():
        out[k] = {"label": v["s"]["label"], "n": v["sum"][2]["n"],
                  "t": {str(t): [v["sum"][t]["low"], v["sum"][t]["mid"], v["sum"][t]["high"]] for t in TRIGGERS}}
    return out


def lastmod(p):
    d = load()
    return d["source"]["fetchedAt"][:10] if d else None


def cover_words(c):
    x = math.floor(c * 1000) / 10
    return f"more than {x:.1f}%" if c * 100 > x else f"{x:.1f}%"


def inch(t):
    return f"{t} inch" if t == 1 else f"{t} inches"


def pushes(x):
    return f"{num(x)} {'day' if x == 1 else 'days'}"


CSS = ("<style>"
       ":root{--sn-a:#2f6fb3;--sn-g:#8a909c;--sn-wash:rgba(47,111,179,.10);--sn-gwash:rgba(120,127,140,.30);--sn-grid:#ece8e0}"
       "@media (prefers-color-scheme:dark){:root{--sn-a:#5b95e0;--sn-g:#6b7180;--sn-wash:rgba(91,149,224,.14);--sn-gwash:rgba(140,147,163,.30);--sn-grid:#283041}}"
       ".sn-ctl{display:flex;flex-wrap:wrap;gap:14px 28px;margin:4px 0 16px;padding:14px 16px;background:var(--card);border:1px solid var(--line);border-radius:12px}"
       ".sn-seg{display:flex;flex-wrap:wrap;gap:6px;border:0;margin:0;padding:0;min-width:0}"
       ".sn-seg legend{font-size:13px;font-weight:700;color:var(--muted);margin:0 0 6px;padding:0}"
       ".sn-seg label{position:relative;display:inline-flex;align-items:center;min-height:46px;box-sizing:border-box;padding:0 15px;border:1.5px solid var(--line);border-radius:10px;"
       "background:var(--canvas2);color:var(--ink);font-weight:600;font-size:15px;cursor:pointer}"
       ".sn-seg input{position:absolute;opacity:0;inset:0;margin:0;cursor:pointer}"
       ".sn-seg label:has(input:checked){background:var(--ink);border-color:var(--ink);color:var(--card)}"
       ".sn-seg label:has(input:focus-visible){outline:3px solid var(--focus);outline-offset:2px}"
       ".sn-top{margin-top:18px}section.block .sn-ctl .sn-ctl-h{flex-basis:100%;margin:0 0 -4px;font-size:17px;line-height:1.3}"
       "@media(max-width:599px){.ld-hero .lede{margin-bottom:8px}.sn-top{margin-top:4px}.sn-tiles .tile.key{padding:12px 14px}.sn-act{margin-top:10px}.sn-ctl{margin-bottom:10px}}"
       "@media(max-width:599px){.sn-now{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}.sn-ctl{padding:12px 14px;gap:10px 20px}}.sn-now{margin:0 0 10px;font-size:15px;color:var(--ink2)}.sn-now b{color:var(--ink)}"
       ".sn-tiles{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.sn-tiles .tile.key{grid-column:1/-1;order:-1}.sn-tiles .sn-cur{display:none}"
       ".sn-strip{margin:12px 0 0;padding:10px 14px;border:1px solid var(--line);border-radius:12px;background:var(--card);font-size:14.5px;color:var(--ink2)}.sn-strip b{color:var(--ink)}"
       "@media(min-width:900px){.sn-tiles .sn-cur{display:block}.sn-strip{display:none}}"
       "@media(min-width:900px){.sn-tiles{grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.sn-tiles .tile.key{grid-column:auto;order:0}}"
       "@media(max-width:899px){.sn-tiles .tile:not(.key){padding:12px}.sn-tiles .tile:not(.key) .val{font-size:28px}.sn-tiles .tile.key .val{font-size:40px}}"
       ".sn-tiles .tile .sub{font-size:13.5px;margin-top:4px;line-height:1.35}.sn-tiles .tile:not(.key) .sub{color:var(--ink2)}"
       ".sn-act{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 0}"
       ".sn-fig{position:relative;margin:12px 0 6px;padding:16px 16px 12px;background:var(--card);border:1px solid var(--line);border-radius:12px}"
       ".sn-fig figcaption{font-weight:700;color:var(--ink);margin:0 0 2px}.sn-fig .sn-sub{font-size:13.5px;color:var(--muted);margin:0 0 12px}"
       ".sn-plot{position:relative;height:210px;margin:0 0 0 30px}"
       ".sn-plot.m{height:150px}.sn-plot.m .sn-col i{max-width:64px}.sn-plot:focus-visible{outline:3px solid var(--focus);outline-offset:4px;border-radius:4px}"
       ".sn-gl{position:absolute;left:0;right:0;height:0;border-top:1px solid var(--sn-grid)}"
       ".sn-gl span{position:absolute;right:100%;margin-right:8px;transform:translateY(-50%);font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}"
       ".sn-gl.base{border-top-color:var(--dash)}"
       ".sn-ref{position:absolute;left:0;right:0;height:0;border-top:1.5px solid var(--ink2);z-index:2;pointer-events:none}"
       ".sn-leg i.r{border-top:1.5px solid var(--ink2)}.sn-leg i.h{height:10px;border:0;background:repeating-linear-gradient(45deg,var(--sn-g) 0 2px,transparent 2px 5px)}"
       ".sn-cols{position:absolute;inset:0;display:flex;align-items:flex-end;gap:2px}"
       ".sn-col{position:relative;flex:1 1 0;min-width:0;height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;cursor:default}"
       ".sn-col i{display:block;width:100%;max-width:24px;background:var(--sn-a);border-radius:4px 4px 0 0}"
       ".sn-col.on i,.sn-col:hover i{filter:brightness(1.15)}"
       ".sn-col.miss i{height:18px;background:repeating-linear-gradient(45deg,var(--sn-g) 0 2px,transparent 2px 5px);border-radius:2px}"
       ".sn-col b{font:600 12.5px system-ui,sans-serif;color:var(--ink);margin-bottom:4px;font-variant-numeric:tabular-nums}"
       ".sn-xl{display:flex;gap:2px;margin:6px 0 0 30px}.sn-xl span{flex:1 1 0;min-width:0;display:flex;justify-content:center;font-size:11.5px;color:var(--muted);white-space:nowrap}"
       ".sn-xl.yr span:first-child{justify-content:flex-start}.sn-xl.yr span:last-child{justify-content:flex-end}"
       ".sn-xl.yr span:not(.k){visibility:hidden}"
       ".sn-tip{position:absolute;z-index:5;pointer-events:none;background:var(--ink);color:var(--card);font-size:13px;line-height:1.35;padding:7px 10px;border-radius:8px;"
       "box-shadow:var(--shadow-soft);max-width:240px;white-space:normal}.sn-tip b{display:block;font-size:14px}.sn-tip[hidden]{display:none}"
       ".sn-leg{display:flex;flex-wrap:wrap;gap:6px 18px;margin:0 0 10px;font-size:13.5px;color:var(--ink2)}"
       ".sn-leg span{display:inline-flex;align-items:center;gap:7px}.sn-leg i{display:inline-block;width:18px;height:0;border-top:2px solid var(--sn-a)}"
       ".sn-leg i.g{border-top-color:var(--sn-g)}.sn-leg i.w{height:10px;border:0;background:var(--sn-gwash);border-radius:2px}"
       ".sn-line{position:relative;height:230px;margin:0 0 0 30px}.sn-line svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}"
       ".sn-line:focus-visible{outline:3px solid var(--focus);outline-offset:4px;border-radius:4px}"
       ".sn-dot{position:absolute;width:10px;height:10px;margin:-5px 0 0 -5px;border-radius:50%;background:var(--sn-a);box-shadow:0 0 0 2px var(--card);z-index:3}"
       ".sn-lab{position:absolute;font-size:12.5px;font-weight:700;color:var(--ink);white-space:nowrap;transform:translateY(-50%);z-index:3;background:var(--card);padding:0 3px;border-radius:4px}"
       ".sn-x{position:absolute;top:0;bottom:0;width:0;border-left:1px solid var(--ink2);z-index:4;pointer-events:none}.sn-x[hidden]{display:none}"
       ".sn-mx{position:relative;height:18px;margin:6px 0 0 30px}.sn-mx span{position:absolute;transform:translateX(-50%);font-size:11.5px;color:var(--muted)}"
       ".sn-dates{grid-template-columns:1fr}@media(min-width:600px){.sn-dates{grid-template-columns:repeat(3,minmax(0,1fr))}}@media(min-width:900px){.sn-dates{grid-template-columns:repeat(3,minmax(0,1fr))}}"
       ".sn-note{font-size:14.5px;color:var(--ink2);margin:10px 0 0}"
       ".sn-tw{overflow-x:auto;margin:12px 0 0;border:1px solid var(--line);border-radius:12px;background:var(--card)}"
       ".sn-tw:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
       ".sn-t{width:100%;border-collapse:collapse;font-size:14.5px;min-width:560px}.sn-t th,.sn-t td{padding:9px 12px;border-bottom:1px solid var(--rule);text-align:right;font-variant-numeric:tabular-nums}"
       ".sn-t th:first-child,.sn-t td:first-child{text-align:left}.sn-t thead th{font-size:13px;color:var(--muted);font-weight:700;vertical-align:bottom}"
       ".sn-t tbody th{font-weight:600;color:var(--ink)}.sn-t tr:last-child td,.sn-t tr:last-child th{border-bottom:0}"
       ".sn-t td.x{color:var(--muted);text-align:left}.sn-t tbody th{white-space:nowrap}.sn-t thead th.grp{text-align:center;border-bottom:1px solid var(--line);white-space:nowrap}.sn-t thead tr+tr th,.sn-t thead tr+tr th:first-child{text-align:right}.sn-t th.gr,.sn-t td.gr{width:160px;padding-left:22px;border-left:1px solid var(--rule)}.sn-t tr.cur th small{display:block;font-weight:400;font-size:12.5px;color:var(--muted)}"
       "[data-sn-t='1'] .c1,[data-sn-t='2'] .c2,[data-sn-t='3'] .c3,[data-sn-t='6'] .c6{background:var(--sn-wash);font-weight:700;color:var(--ink)}"
       ".sn-defs{margin:8px 0 0;padding-left:20px}.sn-defs li{margin:8px 0;color:var(--ink2)}.sn-defs b{color:var(--ink)}"
       ".sn-end p{color:var(--ink2);margin:0 0 4px}.sn-lead{color:var(--ink2);margin:0 0 6px;max-width:780px}"
       ".sn-more{border:1px solid var(--line);border-radius:12px;background:var(--card);padding:0 16px}.sn-more>summary{display:flex;align-items:center;min-height:48px;color:var(--ink)}"
       ".sn-more[open]>summary{border-bottom:1px solid var(--rule);margin-bottom:6px}.sn-more>:not(summary){max-width:820px}@media(max-width:599px){.sn-dl a{flex:1 1 100%}}.sn-dl{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0 0}"
       ".vh{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}"
       "@media(max-width:599px){.sn-plot,.sn-line{margin-left:24px}.sn-xl,.sn-mx{margin-left:24px}.sn-plot{height:180px}.sn-line{height:200px}"
       ".sn-col b{font-size:11.5px}.sn-xl.yr span.k:not(.k0){visibility:hidden}.sn-t{min-width:0;font-size:13.5px}.sn-t th,.sn-t td{padding:8px 6px}.sn-t .gr,.asof.gr{display:none}section.block .asof,.sn-top .asof{font-size:13.5px}.sn-ctl{gap:12px}.sn-seg label{padding:0 13px}}"
       "</style>")


def gridlines(top):
    step = 1 if top <= 4 else 2 if top <= 10 else 5 if top <= 25 else 10
    ymax = max(step, math.ceil(top / step) * step)
    lines = "".join(f'<div class="sn-gl{" base" if v == 0 else ""}" style="bottom:{v / ymax * 100:.2f}%" aria-hidden="true"><span>{v}</span></div>'
                    for v in range(0, ymax + 1, step))
    return ymax, lines


def winters_chart(v, t, E):
    sm = v["sum"][t]
    rows = [r for r in v["rows"] if not r["current"]]
    top = max(r["events"][t] for r in rows if r["complete"])
    ymax, lines = gridlines(max(top, 1))
    cols = []
    for r in rows:
        if r["complete"]:
            c = r["events"][t]
            tip = f'{r["label"]}|{pushes(c)} at {inch(t)} or more; {r["snow"]:.1f} inches of snow that winter'
            cols.append(f'<div class="sn-col" data-tip="{E(tip)}"><i style="height:{c / ymax * 100:.2f}%"></i></div>')
        else:
            tip = f'{r["label"]}|Records incomplete: {r["miss"]} days between October and May have no snowfall value'
            cols.append(f'<div class="sn-col miss" data-tip="{E(tip)}"><i></i></div>')
    ref = f'<div class="sn-ref" style="bottom:{sm["mid"] / ymax * 100:.2f}%" aria-hidden="true"></div>'
    keys = {0, len(rows) - 1} | {i for i, r in enumerate(rows) if r["y"] % 10 == 0}
    tens = sorted((i for i, r in enumerate(rows) if r["y"] % 10 == 0), key=lambda i: abs(i - len(rows) // 2))
    core = {0, len(rows) - 1, tens[0] if tens else len(rows) // 2}   # phones show only the first, middle and last labels
    xl = "".join(f'<span{(" class=" + chr(34) + "k" + (" k0" if i in core else "") + chr(34)) if i in keys | core else ""}>{E(r["label"] if i in keys | core else "")}</span>'
                 for i, r in enumerate(rows))
    lab = (f'Plowable days at {inch(t)} or more at {v["s"]["label"]}, one column per winter from {rows[0]["label"]} to {rows[-1]["label"]}: '
           + ", ".join(f'{r["label"]} {r["events"][t] if r["complete"] else "incomplete"}' for r in rows))
    note = ""
    if sm["incomplete"]:
        note = (f'<p class="asof">Striped bars mark winters whose records are incomplete ({E(", ".join(r["label"] for r in sm["incomplete"]))}); '
                'they are left out of every count on this page.</p>')
    return (f'<figure class="sn-fig"><figcaption>Plowable days in each winter</figcaption>'
            f'<p class="sn-sub">Days with {E(inch(t))} or more of new snow at {E(v["s"]["label"])}.</p>'
            f'<div class="sn-leg" aria-hidden="true"><span><i class="r"></i>Middle winter, {E(num(sm["mid"]))}</span>'
            + ('<span><i class="h"></i>Records incomplete</span>' if sm["incomplete"] else "") + '</div>'
            f'<div class="sn-plot" tabindex="0" role="img" aria-label="{E(lab)}" data-sn-tips>{lines}{ref}<div class="sn-cols">{"".join(cols)}</div>'
            f'<div class="sn-tip" hidden></div></div><div class="sn-xl yr" aria-hidden="true">{xl}</div></figure>{note}')


def one_dp(x):
    """One decimal, a half rounds up (7 of 28 winters is 0.25, shown 0.3)."""
    return f"{math.floor(x * 10 + 0.5 + 1e-9) / 10:.1f}"


def avg_words(x):
    return "under 0.1" if 0 < x < 0.05 else one_dp(x)


def bar_words(x):
    return "<0.1" if 0 < x < 0.05 else one_dp(x)


def months_chart(v, t, E):
    sm = v["sum"][t]
    top = max((m["avg"] for m in sm["months"]), default=0)
    ymax = max(top, 0.1) * 1.18
    cols = "".join(f'<div class="sn-col" data-tip="{E(m["name"])}|{E(avg_words(m["avg"]).capitalize())} a winter on average; '
                   f'{(str(m["winters"]) + " of " + str(sm["n"]) + " winters had at least one") if m["winters"] else ("none of the " + str(sm["n"]) + " winters had one")}">'
                   f'<b>{E(bar_words(m["avg"]))}</b><i style="height:{m["avg"] / ymax * 100:.2f}%"></i></div>' for m in sm["months"])
    xl = "".join(f'<span class="k">{E(m["name"])}</span>' for m in sm["months"])
    lab = (f'Average plowable days a winter by month at {inch(t)} or more at {v["s"]["label"]}: '
           + ", ".join(f'{m["name"]} {avg_words(m["avg"])}' for m in sm["months"]))
    return (f'<figure class="sn-fig sn-fm"><figcaption>Plowable days by month</figcaption>'
            f'<p class="sn-sub">Average plowable days in each month, over the {sm["n"]} complete winters, at {E(inch(t))} or more.</p>'
            f'<div class="sn-plot m" tabindex="0" role="img" aria-label="{E(lab)}" data-sn-tips><div class="sn-gl base" style="bottom:0" aria-hidden="true"></div>'
            f'<div class="sn-cols">{cols}</div><div class="sn-tip" hidden></div></div>'
            f'<div class="sn-xl m" aria-hidden="true">{xl}</div></figure>')


def sx(i, n):
    return f"{i / (n - 1) * 1000:.1f}".rstrip("0").rstrip(".")


def sy(v, ymax):
    return f"{300 - v / ymax * 300:.1f}".rstrip("0").rstrip(".")


def path(vals, n, ymax):
    """A step line: flat until the count changes, then straight up (SVG H and V only)."""
    if not vals:
        return ""
    out = [f"M0,{sy(vals[0], ymax)}"]
    for i in range(1, len(vals)):
        if vals[i] != vals[i - 1]:
            out.append(f"H{sx(i, n)}V{sy(vals[i], ymax)}")
    out.append(f"H{sx(len(vals) - 1, n)}")
    return "".join(out)


def band_path(lo, hi, n, ymax):
    """Up the heavy edge left to right, back along the light edge right to left."""
    out = [path(hi, n, ymax), f"V{sy(lo[-1], ymax)}"]
    for i in range(len(lo) - 1, 0, -1):
        if lo[i] != lo[i - 1]:
            out.append(f"H{sx(i, n)}V{sy(lo[i - 1], ymax)}")
    out.append("H0Z")
    return "".join(out)


def season_chart(v, t, E):
    sm = v["sum"][t]
    c = v["cum"][t]
    n = len(c["x"])
    top = max(max(c["hi"]), max(c["now"] or [0]), 1)
    ymax, lines = gridlines(top)
    band = band_path(c["lo"], c["hi"], n, ymax)
    svg = ('<svg viewBox="0 0 1000 300" preserveAspectRatio="none" aria-hidden="true" focusable="false">'
           f'<path d="{band}" fill="var(--sn-gwash)" stroke="none"/>'
           f'<path d="{path(c["mid"], n, ymax)}" fill="none" stroke="var(--sn-g)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke"/>'
           + (f'<path d="{path(c["now"], n, ymax)}" fill="none" stroke="var(--sn-a)" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke"/>' if len(c["now"]) > 1 else "")
           + '</svg>')
    marks = ""
    if c["now"]:
        i = len(c["now"]) - 1
        x, y = i / (n - 1) * 100, c["now"][-1] / ymax * 100
        marks += f'<span class="sn-dot" style="left:{x:.2f}%;top:{100 - y:.2f}%"></span>'
        marks += f'<span class="sn-lab" style="left:calc({x:.2f}% + 9px);top:calc({100 - y:.2f}% - 14px)">This winter, {c["now"][-1]}</span>'
    marks += (f'<span class="sn-lab" style="right:0;top:calc({100 - c["mid"][-1] / ymax * 100:.2f}% - 13px)">Middle, {E(num(c["mid"][-1]))}</span>')
    ticks = "".join(f'<span style="left:{i / (n - 1) * 100:.2f}%">{E(lab.split()[0])}</span>' for i, lab in enumerate(c["x"]) if lab.endswith(" 1"))
    end = v["end"]
    lab = (f'Running count of plowable days at {inch(t)} or more at {v["s"]["label"]} from October 1. This winter so far: {sm["cur"]}, '
           f'through {day_words(end)}. The middle of past winters had {num(sm["toDate"])} by that date and {num(c["mid"][-1])} by April 30.')
    return (f'<figure class="sn-fig"><figcaption>This winter against past winters, by date</figcaption>'
            f'<p class="sn-sub">Running count of days with {E(inch(t))} or more since the winter began on July 1, shown from October 1.</p>'
            '<div class="sn-leg" aria-hidden="true"><span><i></i>This winter</span><span><i class="g"></i>Middle of past winters</span>'
            '<span><i class="w"></i>Light to heavy winters</span></div>'
            f'<div class="sn-line" tabindex="0" role="img" aria-label="{E(lab)}" data-sn-line="{v["s"]["key"]}-{t}">{lines}{svg}{marks}'
            '<div class="sn-x" hidden></div><div class="sn-tip" hidden></div></div>'
            f'<div class="sn-mx" aria-hidden="true">{ticks}</div></figure>')


def tiles(v, t, E):
    sm = v["sum"][t]
    end = v["end"]
    c, n = sm["counts"], sm["n"]
    low_words = (f'None in {sm["lowN"]} of {n} winters' if sm["low"] == 0 else f'{num(sm["low"])} or fewer in {sm["lowN"]} of {n} winters')
    mid_words = (f'Halfway between the two middle winters, {c[n // 2 - 1]} and {c[n // 2]}' if sm["mid"] != int(sm["mid"])
                 else f'The middle of the {n} winters, lined up by count')
    top = c[-1]
    high_words = f'{num(sm["high"])} or more in {sm["highN"]} of {n} winters'
    if sm["high"] == sm["mid"]:
        high_words += f'; the most was {top}, in {c.count(top)} {"winter" if c.count(top) == 1 else "winters"}'
    return ('<div class="tiles sn-tiles">'
            f'<div class="tile"><div class="lab">Light winter</div><div class="val">{E(num(sm["low"]))}</div>'
            f'<div class="sub">{low_words}</div></div>'
            f'<div class="tile key"><div class="lab">Middle winter</div><div class="val">{E(num(sm["mid"]))}</div>'
            f'<div class="sub">{E(mid_words)}</div></div>'
            f'<div class="tile"><div class="lab">Heavy winter</div><div class="val">{E(num(sm["high"]))}</div>'
            f'<div class="sub">{E(high_words)}</div></div>'
            f'<div class="tile sn-cur"><div class="lab">This winter so far</div><div class="val">{sm["cur"]}</div>'
            f'<div class="sub">{"None yet. " if not sm["cur"] else ""}Past winters\' middle by {E(short_day(end))}: {E(num(sm["toDate"]))}</div></div>'
            '</div>')


def sofar(v, t, E):
    sm = v["sum"][t]
    return (f'<p class="sn-strip"><b>This winter so far: {sm["cur"]}</b> {"(none yet). " if not sm["cur"] else ". "}'
            f'Past winters\' middle by {E(short_day(v["end"]))}: {E(num(sm["toDate"]))}.</p>')


def dates_block(v, t, E):
    sm = v["sum"][t]
    y0 = v["rows"][-1]["y"]
    if not sm["firsts"]:
        return f'<p class="sn-note">No past winter had a day with {E(inch(t))} or more at {E(v["s"]["label"])}.</p>'
    e1, l1 = sm["firsts"][0], sm["firsts"][-1]
    e2, l2 = sm["lasts"][0], sm["lasts"][-1]
    none = (f'<div class="tile"><div class="lab">Winters with none</div><div class="val">{sm["none"]}</div>'
            f'<div class="sub">of {sm["n"]} had no day at {E(inch(t))} or more</div></div>')
    return ('<div class="tiles sn-dates">'
            f'<div class="tile"><div class="lab">First plowable day, middle</div><div class="val">{E(short_day(key_day(sm["firstMid"], y0)))}</div>'
            f'<div class="sub">Earliest {E(day_words(e1, True))}; latest {E(day_words(l1, True))}</div></div>'
            f'<div class="tile"><div class="lab">Last plowable day, middle</div><div class="val">{E(short_day(key_day(sm["lastMid"], y0)))}</div>'
            f'<div class="sub">Earliest {E(day_words(e2, True))}; latest {E(day_words(l2, True))}</div></div>'
            + none + '</div>'
            + f'<p class="asof">Middle is the middle date across the {sm["n"] - sm["none"]} complete winters that had a day at {E(inch(t))} or more; '
              'with an even count it is halfway between the two middle dates, to the nearest day.</p>'
            + (NWS_NOTE if v["s"]["key"] == "ohare" else ""))


def table(v, E):
    rows = list(reversed(v["rows"]))
    trs = []
    for r in rows:
        if r["current"]:
            th = f'<th scope="row">{E(r["label"])}<small>so far, to {E(short_day(v["end"]))}</small></th>'
        else:
            th = f'<th scope="row">{E(r["label"])}</th>'
        if not r["complete"] and not r["current"]:
            trs.append(f'<tr>{th}<td class="x" colspan="6">Incomplete: {r["miss"]} days between October and May have no snowfall value</td></tr>')
            continue
        g = f'{r["ground"]}' if r["groundOk"] else "n/a"
        trs.append(f'<tr{" class=cur" if r["current"] else ""}>{th}<td>{r["snow"]:.1f}</td>'
                   + "".join(f'<td class="c{t}">{r["events"][t]}</td>' for t in TRIGGERS) + f'<td class="gr">{g}</td></tr>')
    head = ('<thead><tr><th scope="col" rowspan="2">Winter</th><th scope="col" rowspan="2">Snow, inches</th>'
            f'<th scope="colgroup" colspan="{len(TRIGGERS)}" class="grp">Plowable days</th>'
            '<th scope="col" rowspan="2" class="gr">Days with 1 inch or more on the ground</th></tr><tr>'
            + "".join(f'<th scope="col" class="c{t}">{t} in</th>' for t in TRIGGERS) + '</tr></thead>')
    return (f'<div class="sn-tw" role="region" aria-label="Every winter at {E(v["s"]["label"])}" tabindex="0" data-sn-t="{DEFAULT[1]}">'
            f'<table class="sn-t"><caption class="vh">Snow and plowable days at {E(v["s"]["label"])}, each winter July 1 to June 30</caption>'
            f'{head}<tbody>{"".join(trs)}</tbody></table></div>')


def csv_text(v):
    lines = ["winter,station_id,station_name,records_complete,days_missing_oct_to_may,snowfall_in,days_1in_plus_new_snow,days_2in_plus_new_snow,days_3in_plus_new_snow,days_6in_plus_new_snow,days_1in_plus_on_ground"]
    for r in v["rows"]:
        ok = r["complete"] or r["current"]
        lines.append(",".join([r["label"] + (f' so far (to {v["end"].isoformat()})' if r["current"] else ""), v["s"]["id"], '"' + v["s"]["name"] + '"',
                               ("so far" if r["current"] else "yes" if r["complete"] else "no"), str(r["miss"]), f'{r["snow"]:.1f}' if ok else ""]
                              + [str(r["events"][t]) if ok else "" for t in TRIGGERS] + [str(r["ground"]) if ok and r["groundOk"] else ""]))
    return "\n".join(lines) + "\n"


def extra_pages(p):
    d = load()
    if not d:
        return []
    return [(f'{k}-winters.csv', csv_text(v)) for k, v in station_data(d).items()]


SCRIPT = """<script>
(function(){var f=document.getElementById("sn-ctl");if(!f)return;
var q=new URLSearchParams(location.search),st=q.get("station"),t=String(parseInt(q.get("trigger"),10));
function pick(name,val){var i=f.querySelector('input[name="'+name+'"][value="'+val+'"]');if(i)i.checked=true;}
if(st)pick("st",st);if(t)pick("t",t);
function show(push){st=f.querySelector('input[name="st"]:checked').value;t=f.querySelector('input[name="t"]:checked').value;
document.querySelectorAll("[data-v]").forEach(function(el){var p=el.getAttribute("data-v").split("-");el.hidden=!(p[0]===st&&(p.length<2||p[1]===t));});
document.querySelectorAll("[data-sn-t]").forEach(function(el){el.setAttribute("data-sn-t",t);});
["sn-calc","sn-calc2"].forEach(function(id){var a=document.getElementById(id);if(a)a.href=a.getAttribute("data-base")+"?station="+st+"&trigger="+t+"#season";});
var s=document.getElementById("sn-say");if(s){var l=f.querySelector('input[name="st"]:checked').parentNode.textContent,d=f.querySelector('input[name="t"]:checked').parentNode.querySelector(".vh").textContent;s.textContent=l+", "+d;}
if(push){try{history.replaceState(null,"","?station="+st+"&trigger="+t+location.hash);}catch(e){}}}
f.addEventListener("change",function(){show(true);});show(false);
function tipAt(box,tip,el){var p=(el.getAttribute("data-tip")||"").split("|");tip.textContent="";var b=document.createElement("b");b.textContent=p[0];tip.appendChild(b);
tip.appendChild(document.createTextNode(p.slice(1).join("|")));tip.hidden=false;var r=box.getBoundingClientRect(),c=el.getBoundingClientRect();
var x=c.left-r.left+c.width/2-tip.offsetWidth/2;x=Math.max(-24,Math.min(x,r.width-tip.offsetWidth));tip.style.left=x+"px";tip.style.top="-8px";
box.querySelectorAll(".sn-col.on").forEach(function(o){o.classList.remove("on");});el.classList.add("on");}
document.querySelectorAll("[data-sn-tips]").forEach(function(box){var tip=box.querySelector(".sn-tip"),cols=[].slice.call(box.querySelectorAll(".sn-col")),k=-1;
cols.forEach(function(c,i){c.addEventListener("pointerenter",function(){k=i;tipAt(box,tip,c);});});
box.addEventListener("pointerleave",function(){tip.hidden=true;cols.forEach(function(o){o.classList.remove("on");});});
box.addEventListener("keydown",function(e){if(e.key==="ArrowRight"||e.key==="ArrowLeft"){e.preventDefault();k=e.key==="ArrowRight"?Math.min(cols.length-1,k+1):Math.max(0,k<0?cols.length-1:k-1);tipAt(box,tip,cols[k]);}
else if(e.key==="Escape"){tip.hidden=true;}});box.addEventListener("blur",function(){tip.hidden=true;});});
function fmt(x){return Math.round(x)===x?String(x):x.toFixed(1);}
var DATA={};try{DATA=JSON.parse(document.getElementById("sn-data").textContent);}catch(e){}
var MO=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
function lab(D,i){var p=D.s.split("-"),d=new Date(Date.UTC(+p[0],+p[1]-1,+p[2]+i));return MO[d.getUTCMonth()]+" "+d.getUTCDate();}
document.querySelectorAll("[data-sn-line]").forEach(function(box){var D=DATA[box.getAttribute("data-sn-line")];if(!D)return;var n=D.mid.length,tip=box.querySelector(".sn-tip"),xl=box.querySelector(".sn-x"),k=-1;
function at(i){k=i;var r=box.getBoundingClientRect(),px=i/(n-1)*r.width;xl.style.left=px+"px";xl.hidden=false;tip.textContent="";var b=document.createElement("b");b.textContent=lab(D,i);tip.appendChild(b);
tip.appendChild(document.createTextNode((i<D.now.length?"This winter: "+D.now[i]+". ":"")+"Middle of past winters: "+fmt(D.mid[i])+". Light to heavy: "+fmt(D.lo[i])+" to "+fmt(D.hi[i])+"."));
tip.hidden=false;var x=px+12;if(x+tip.offsetWidth>r.width)x=px-12-tip.offsetWidth;tip.style.left=Math.max(-24,x)+"px";tip.style.top="0px";}
function hide(){tip.hidden=true;xl.hidden=true;}
box.addEventListener("pointermove",function(e){var r=box.getBoundingClientRect();at(Math.max(0,Math.min(n-1,Math.round((e.clientX-r.left)/r.width*(n-1)))));});
box.addEventListener("pointerleave",hide);box.addEventListener("blur",hide);
box.addEventListener("keydown",function(e){var s=e.shiftKey?7:1;if(e.key==="ArrowRight"){e.preventDefault();at(Math.min(n-1,(k<0?D.now.length-1:k)+s));}
else if(e.key==="ArrowLeft"){e.preventDefault();at(Math.max(0,(k<0?D.now.length-1:k)-s));}else if(e.key==="Escape")hide();});});
})();</script>"""


def line_data(sd):
    """The running counts behind the by-date charts, for their hover readout (the chart and table carry the same values)."""
    out = {f"{k}-{t}": {"s": v["cum"][t]["start"], "mid": v["cum"][t]["mid"], "lo": v["cum"][t]["lo"], "hi": v["cum"][t]["hi"], "now": v["cum"][t]["now"]}
           for k, v in sd.items() for t in TRIGGERS}
    return json.dumps(out, separators=(",", ":")).replace("</", "<\\/")


def page_html(p):
    import make_site as M
    E = M.E
    url, rel = M.BASE + p["slug"] + "/", "../"
    d = load()
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), ("Free Chicago data", "chicago-data/"), (META["h1"], None)])
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": []}
    data_ld = None
    sd = station_data(d) if d else {}
    if d:
        faq_ld["mainEntity"] = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq(sd[DEFAULT[0]]["sum"][DEFAULT[1]], sd)]
    if d:
        data_ld = {"@context": "https://schema.org", "@type": "Dataset", "name": "Plowable snow days per winter at Chicago O'Hare and Midway",
                   "description": "Days per winter with new snowfall of 1, 2, 3 and 6 inches or more, counted from NOAA NCEI GHCN-Daily records.",
                   "url": url, "isAccessibleForFree": True, "creator": {"@type": "Organization", "name": "ProofNotFluff"},
                   "temporalCoverage": f'{d["winters"][0]}-07-01/{max(v["end"] for v in sd.values()).isoformat()}',
                   "spatialCoverage": "Chicago, Illinois", "isBasedOn": GHCN[0],
                   "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": url + f"{k}-winters.csv"} for k in sd]}
    head = lambda rb: M.HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=M.SHOP,
                                    ld=M.ld_tags(crumb_ld, faq_ld, data_ld) + CSS, bodycls=' class="ld-page"', robots=rb, analytics=M.analytics_tag())
    if not d:
        body = f'{crumb}<div class="ld-hero"><h1>{E(META["h1"])}</h1><p class="lede">The first pull of NOAA records is on its way.</p></div>'
        return head('<meta name="robots" content="noindex, nofollow">') + body + "</main></body></html>"
    st0, t0 = DEFAULT
    v0 = sd[st0]
    s0 = v0["sum"][t0]
    checked = day_words(dt.date.fromisoformat(d["source"]["fetchedAt"][:10]), True)
    lede = 'How many plowable days a Chicago winter brings at your trigger depth, from 30 winters of NOAA records.'
    st_opts = "".join(f'<label><input type="radio" name="st" value="{k}"{" checked" if k == st0 else ""}>{E(v["s"]["label"])}</label>' for k, v in sd.items())
    t_opts = "".join(f'<label><input type="radio" name="t" value="{t}"{" checked" if t == t0 else ""}><span aria-hidden="true">{t} in</span>'
                     f'<span class="vh">{E(inch(t))}</span></label>' for t in TRIGGERS)
    ctl = ('<form class="sn-ctl" id="sn-ctl" aria-labelledby="sn-h-board"><h2 id="sn-h-board" class="sn-ctl-h">Pick your station and trigger</h2>'
           f'<fieldset class="sn-seg"><legend>Weather station</legend>{st_opts}</fieldset>'
           f'<fieldset class="sn-seg"><legend>Your trigger depth</legend>{t_opts}</fieldset></form>')
    V = lambda fn: "".join(f'<div data-v="{k}-{t}"{"" if (k, t) == DEFAULT else " hidden"}>{fn(v, t, E)}</div>' for k, v in sd.items() for t in TRIGGERS)
    VS = lambda fn: "".join(f'<div data-v="{k}"{"" if k == st0 else " hidden"}>{fn(v, E)}</div>' for k, v in sd.items())
    calc = next((x for x in M.PAGES_LIVE if x.get("kind") == "snow"), None)
    calc_link = lambda i: (f'<a class="btn" id="{i}" data-base="{rel}{E(calc["slug"])}/" href="{rel}{E(calc["slug"])}/?station={st0}&amp;trigger={t0}#season">'
                           'Price it in the snow calculator</a>' if calc else "")
    calc_btn = calc_link("sn-calc")
    ends = {k: v["end"] for k, v in sd.items()}
    through = (f'{day_words(ends["ohare"], True)}' if len(set(ends.values())) == 1 else
               "; ".join(f'{sd[k]["s"]["label"]} {day_words(e, True)}' for k, e in ends.items()))
    top = (f'<section class="block sn-top" id="board" aria-labelledby="sn-h-board">{ctl}'
           f'<p class="sn-now" aria-live="polite">Showing <b id="sn-say">{E(v0["s"]["label"])}, {E(inch(t0))}</b>: days with new snow at or over your trigger. Every count, chart and table below changes to match.</p>'
           f'{V(tiles)}<div class="sn-act">{calc_btn}<a class="st-btn2" href="#winters">See every winter</a></div>{V(sofar)}'
           f'<p class="asof">Past winters only; this is not a forecast. NOAA records through {E(through)}, checked {E(checked)}. Updated daily from October to April.</p></section>')
    sec = lambda i, h, inner, extra="": f'<section class="block" id="{i}" aria-labelledby="sn-h-{i}"><h2 id="sn-h-{i}">{h}</h2>{inner}{extra}</section>'
    stations = "".join(f'<li><b>{E(v["s"]["label"])}:</b> NOAA station {E(v["s"]["id"])}, {E(v["s"]["name"].replace(", IL US", "").title().replace("Ohare", "O\'Hare").replace(" Sw", " SW"))}. '
                       f'{E(STATION_NOTE.get(k, ""))} Snowfall is reported on {cover_words(v["s"]["cover"])} of October to May days in the {d["winters"][1] - d["winters"][0] + 1} winters.</li>'
                       for k, v in sd.items())
    defs = ('<ul class="sn-defs">'
            '<li><b>Plowable day:</b> one day at the weather station with new snowfall at or over the trigger depth (1, 2, 3 or 6 inches). '
            'Two days in a row that each reach the trigger count as two. A storm that drops 3 inches split 1.5 and 1.5 over two days does not count at a 2 inch trigger, '
            'because neither day alone reached 2 inches.</li>'
            '<li><b>Winter:</b> July 1 to June 30, so a winter holds every snow from fall to spring.</li>'
            f'<li><b>Light, middle and heavy winter:</b> line up the complete winters from fewest days to most. Light is the winter one fifth of the way up. '
            'Middle is the one in the middle, or halfway between the two middle winters when they differ. Heavy is the winter four fifths of the way up. '
            'Each tile says how many winters came in at that count or lighter (light) or at that count or heavier (heavy).</li>'
            f'<li><b>Incomplete winter:</b> more than {MAXMISS} days between October and May with no snowfall value in NOAA\'s file. It is left out of '
            f'every count, because a missing day could hide a storm. A complete winter can still miss up to {MAXMISS} days; those days count as no snow.</li>'
            '<li><b>This winter so far:</b> the plowable days since the winter began on July 1, set against the past winters\' counts by the same date.</li>'
            '<li><b>Days with snow on the ground:</b> days NOAA measured 1 inch or more of snow depth. It shows how long snow stayed on the ground.</li></ul>')
    method = (f'<p>Every count here comes from NOAA\'s daily records: the Global Historical Climatology Network daily '
              f'(<a href="{GHCN[0]}" rel="noopener">GHCN-Daily</a>), read through the NCEI Access Data Service. It holds each station\'s new snowfall '
              'and snow depth, one value a day; this page reads them in inches. Station IDs come straight from NOAA\'s station list, and any value NOAA\'s quality checks flagged counts as missing.</p>'
              f'<ul class="sn-defs">{stations}</ul>'
              f'<p>The last {d["winters"][1] - d["winters"][0] + 1} finished winters are {wlabel(d["winters"][0])} to {wlabel(d["winters"][1])}. '
              'The page refreshes every morning from October to April; NOAA\'s file usually runs a few days behind today, and NOAA can revise recent daily values after its quality checks, so this winter\'s counts can change.</p>'
              '<p>Two weather stations cannot tell you the snow on every street: snowfall can differ across Chicago in a single storm. Use these counts as a starting point '
              'next to your own route records. This page counts past winters and does not forecast the coming one.</p>')
    dls = "".join(f'<a class="st-btn2" href="{k}-winters.csv" download>Download {E(v["s"]["label"])} (CSV)</a>' for k, v in sd.items())
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p.get("eyebrow", "Free Chicago snow season board"))}</p><h1>{E(META["h1"])}</h1>'
            f'<p class="lede">{E(lede)}</p></div>'
            + top
            + sec("by-winter", "How much winters swing", V(winters_chart))
            + sec("by-month", "When the plowable days come", V(months_chart))
            + sec("dates", "First and last plowable days", V(dates_block))
            + sec("this-winter", "This winter so far", V(season_chart),
                  '<p class="asof">Past winters only; the shaded band shows where the light to heavy winters stood on each date, not where this one will go.</p>')
            + sec("winters", "Every winter in a table", VS(table),
                  f'<p class="asof">Plowable days count days with new snow at or over each depth; your trigger column is shaded. Newest winter first; incomplete winters show no counts.</p>'
                  f'<p class="asof gr">n/a means NOAA\'s snow depth record is missing more than 3 days between October and May that winter; a few missing days count as no snow on the ground.</p><div class="sn-dl">{dls}</div>')
            + sec("counts", "What counts on this page",
                  '<p class="sn-lead">A plowable day is one day at the weather station with new snow at or over your trigger; a winter runs July 1 to June 30.</p>'
                  f'<details class="sn-more"><summary>Every definition on this page</summary>{defs}</details>')
            + sec("method", "How this page is made",
                  '<p class="sn-lead">Every count comes from NOAA\'s daily snowfall and snow depth records for two stations, refreshed each morning from October to April.</p>'
                  f'<details class="sn-more"><summary>Sources, stations and limits</summary>{method}</details>')
            + M.faq_block(faq(s0, sd))
            + (f'<section class="block sn-end"><h2>Put your counts to work</h2><p>Price a seasonal contract from your own costs and the plowable days at your trigger.</p>'
               f'<div class="sn-act">{calc_link("sn-calc2")}'
               '</div></section>' if calc else ""))
    foot = (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            f'<p>Source: NOAA National Centers for Environmental Information, <a href="{GHCN[0]}">GHCN-Daily</a> (Menne and others, 2012, doi:10.7289/V5D21VHZ), daily snowfall (SNOW) and snow depth (SNWD) '
            f'at stations {E(", ".join(v["s"]["id"] for v in sd.values()))}, checked {E(checked)}. Past winters only, not a forecast, and not the snowfall at any one address.</p>'
            '<p>ProofNotFluff is not affiliated with or endorsed by NOAA or the National Weather Service.</p>'
            '<p>Public information for planning, not legal, tax or financial advice.</p>'
            '<p>Made by ProofNotFluff with AI assistance, from public NOAA records. The page counts visits with Cloudflare Web Analytics, which sets no cookies.</p>'
            f'</div></footer>\n<script type="application/json" id="sn-data">{line_data(sd)}</script>\n{SCRIPT}\n</body></html>')
    return head(robots) + body + foot


def selftest():
    sys.path.insert(0, HERE)
    # a planted station: 3 winters plus the current one, known storms
    start = dt.date(2020, 7, 1)
    end = dt.date(2023, 10, 24)
    n = (end - start).days + 1
    snow, snwd = [0.0] * n, [0.0] * n
    storms = {dt.date(2020, 12, 1): 2.0, dt.date(2020, 12, 2): 1.5, dt.date(2021, 1, 5): 6.5, dt.date(2021, 3, 20): 1.0,
              dt.date(2021, 11, 30): 3.0, dt.date(2022, 2, 2): 0.9, dt.date(2023, 10, 20): 1.2}
    for day, v in storms.items():
        snow[(day - start).days] = v
        snwd[(day - start).days] = 2.0
    for i in range(10):   # winter 2022-23: 10 missing January days, so it is incomplete
        snow[(dt.date(2023, 1, 1) - start).days + i] = None
    s = {"key": "ohare", "label": "O'Hare", "id": "X", "name": "X", "cover": 1, "start": start.isoformat(), "end": end.isoformat(), "snow": snow, "snwd": snwd}
    rows, e = winters(s, 2020, 2022)
    assert [r["label"] for r in rows] == ["2020-21", "2021-22", "2022-23", "2023-24"] and rows[-1]["current"], "winters July to June"
    assert rows[0]["events"] == {1: 4, 2: 2, 3: 1, 6: 1} and rows[1]["events"] == {1: 1, 2: 1, 3: 1, 6: 0}, "at or over the trigger, day by day"
    assert not rows[2]["complete"] and rows[2]["miss"] == 10 and rows[0]["complete"], "missing days mark a winter incomplete"
    sm = summary(rows, e, 2)
    assert sm["n"] == 2 and sm["low"] == 1 and sm["high"] == 2 and sm["mid"] == 1.5, "incomplete winters stay out of the counts"
    assert sm["cur"] == 0 and summary(rows, e, 1)["cur"] == 1, "this winter so far"
    assert summary(rows, e, 1)["toDate"] == 0, "past winters by the same date (Oct 24)"
    assert [m["name"] for m in sm["months"]] == ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr"], "May only when it ever had one"
    assert abs(sm["months"][2]["avg"] - 0.5) < 1e-9, "December average over complete winters"
    s6 = summary(rows, e, 6)
    assert s6["none"] == 1 and key_day(s6["firstMid"], 2023) == dt.date(2024, 1, 5), "winters with none, first day"
    assert key_day(sm["firstMid"], 2023) == dt.date(2023, 12, 1), "even count: halfway between Nov 30 and Dec 1, a half day rounds later"
    assert key_day(summary(rows, e, 1)["lastMid"], 2023) == dt.date(2024, 1, 24), "even count: true median of Nov 30 and Mar 20"
    c = cumulative(rows, e, 1)
    assert c["x"][0] == "Oct 1" and c["x"][-1] == "Apr 30" and c["now"][-1] == 1 and len(c["now"]) == 24, "running count to date"
    assert c["mid"][-1] == 2.5, "middle of past winters by April 30"
    assert "Incomplete" not in csv_text({"rows": rows, "end": e, "s": s}) and ",no,10," in csv_text({"rows": rows, "end": e, "s": s}), "csv marks incomplete"
    assert one_dp(7 / 28) == "0.3" and one_dp(1 / 28) == "0.0" and avg_words(1 / 28) == "under 0.1" and one_dp(2.2142) == "2.2", "half up"
    assert num(1.5) == "1.5" and num(6.0) == "6" and num(3) == "3", "numbers"
    # the real page, if the data is here
    d = load()
    if d:
        import make_site as M
        spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("slug") == SLUG][0]
        M.PAGES_LIVE[:] = []
        html = page_html(spec)
        assert html.count("<h1>") == 1 and "—" not in html and "–" not in html, "one h1, no dashes"
        assert html.count('data-v="') == 8 * 6 + 2 and 'data-v="ohare-2">' in html, "every station and trigger, default shown"
        for bad in ("forecast for this winter will", "expect this winter", "$"):
            assert bad not in html.split("<footer>")[0].split("</style>")[-1], f"no forecasts or prices: {bad}"
        assert "Half of the" not in html and "0 or fewer" not in html and "no push" not in html, "copy gate fixes hold"
        cc = calc_counts()
        assert set(cc) == {"ohare", "midway"} and all(len(cc[k]["t"]) == 4 for k in cc), "calculator counts"
    print("dp_snow selftest: ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
