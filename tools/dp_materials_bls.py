#!/usr/bin/env python3
"""BLS producer price indexes for the free Material Price Changes Since Your Quote page (tools/dp_materials.py).
Todd's go: Oct 27, 2026, 12:17 pm, "Let's do them all" (coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md).

Runs in GitHub Actions (.github/workflows/dp_materials.yml), because the cloud agents cannot reach bls.gov. Source:
U.S. Bureau of Labor Statistics, Producer Price Index by commodity (database "wp"), the public flat files at
https://download.bls.gov/pub/time.series/wp/. BLS asks automated readers to send contact details in the User-Agent.

Two outputs, both public statistics with no person or business in them:
- site/datapages/dp_materials/catalog.json: every active, not seasonally adjusted commodity series whose BLS title
  matches a building-material word, with BLS's own id, title, base date and last period. This is how series are
  chosen: ids and titles come from BLS on each run, never typed from memory.
- site/datapages/dp_materials/ppi.json: for each series in site/datapages/dp_materials/series.json, BLS's title
  (re-read from wp.series every run, so a renamed series shows BLS's new name) and every monthly value from
  START_YEAR on, with BLS's footnote codes ("P" marks a preliminary value BLS may still revise).

Usage: python3 tools/dp_materials_bls.py              catalog, then the chosen series
       python3 tools/dp_materials_bls.py --selftest   planted files, no network
"""
import datetime as dt, io, json, os, re, sys, urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "site", "datapages", "dp_materials")
BASE = "https://download.bls.gov/pub/time.series/wp/"
UA = {"User-Agent": "ProofNotFluff free data page (hello@proofnotfluff.com; github.com/proofnotfluff-a11y/proofnotfluff-pins)"}
START_YEAR = 2016
WORDS = re.compile(r"copper|wire|cable|steel|iron|lumber|plywood|wood|millwork|asphalt|roof|concrete|cement|gypsum|"
                   r"diesel|fuel oil|plastic|pipe|pvc|paint|insulation|brick|glass|aluminum|sand|gravel|stone|"
                   r"construction|structural|plumbing|fixture|heating|air.?condition|furnace|water heater|"
                   r"electrical|conduit|nails|fastener|floor|tile|sheet metal|rebar|reinforcing|building", re.I)


def get(name, tries=3):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(BASE + name, headers=UA)
            with urllib.request.urlopen(req, timeout=300) as r:
                return r.read().decode("utf-8", "replace"), r.headers.get("Last-Modified", "")
        except Exception as e:   # network blips on the runner: try again, then fail loudly
            last = e
    raise SystemExit(f"could not read {BASE + name}: {last}")


def rows(text):
    """BLS flat file (tab separated, header first, padded cells) to a list of dicts."""
    lines = [ln for ln in text.splitlines() if ln.strip()]
    head = [h.strip() for h in lines[0].split("\t")]
    return [dict(zip(head, [c.strip() for c in ln.split("\t")])) for ln in lines[1:]]


def active(r, year):
    try:
        return int(r.get("end_year") or 0) >= year - 1
    except ValueError:
        return False


def catalog(series_rows, year):
    out = []
    for r in series_rows:
        sid = r.get("series_id", "")
        if not sid.startswith("WPU") or r.get("seasonal") != "U" or not active(r, year):
            continue
        if WORDS.search(r.get("series_title", "")):
            out.append({"id": sid, "title": r["series_title"], "base": r.get("base_date", ""),
                        "begin": f'{r.get("begin_year")}-{r.get("begin_period", "")[1:]}',
                        "end": f'{r.get("end_year")}-{r.get("end_period", "")[1:]}'})
    return sorted(out, key=lambda x: x["id"])


def series_data(data_rows, wanted):
    """{series_id: [[YYYY-MM, value, footnote codes]]} for the wanted ids, months only (M13 is the annual average)."""
    out = {s: [] for s in wanted}
    for r in data_rows:
        sid, per = r.get("series_id", ""), r.get("period", "")
        if sid not in out or not re.fullmatch(r"M(0[1-9]|1[0-2])", per):
            continue
        try:
            y, v = int(r["year"]), float(r["value"])
        except (KeyError, ValueError):
            continue   # BLS writes "-" for a month it has no value for
        if y >= START_YEAR:
            out[sid].append([f"{y}-{per[1:]}", v, r.get("footnote_codes", "")])
    for sid in out:
        out[sid].sort()
    return out


def build(series_rows, data_rows, chosen, foot_rows, fetched, files):
    by_id = {r["series_id"]: r for r in series_rows}
    data = series_data(data_rows, [c["id"] for c in chosen])
    series, missing = [], []
    for c in chosen:
        r = by_id.get(c["id"])
        if not r or not data[c["id"]]:
            missing.append(c["id"])
            continue
        series.append({"id": c["id"], "title": r["series_title"], "base": r.get("base_date", ""), "seasonal": r.get("seasonal"),
                       "obs": data[c["id"]]})
    if missing:
        raise SystemExit(f"BLS has no current series or no values for: {', '.join(missing)} (update series.json from catalog.json)")
    latest = max(s["obs"][-1][0] for s in series)
    return {"source": {"agency": "U.S. Bureau of Labor Statistics", "program": "Producer Price Index, commodity data (wp)",
                       "files": files, "fetchedAt": fetched,
                       "footnotes": {r.get("footnote_code", ""): r.get("footnote_text", "") for r in foot_rows if r.get("footnote_code")}},
            "latest": latest, "startYear": START_YEAR, "series": series}


def write_if_changed(path, obj, same, **kw):
    """Write only when the content changed, so a run that finds no new BLS release commits nothing."""
    if os.path.isfile(path):
        try:
            if same(json.load(open(path, encoding="utf-8")), obj):
                return False
        except ValueError:
            pass
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, **kw)
    return True


def main():
    now = dt.datetime.now(ZoneInfo("America/Chicago"))
    os.makedirs(OUT, exist_ok=True)
    stext, smod = get("wp.series")
    srows = rows(stext)
    cat = catalog(srows, now.year)
    write_if_changed(os.path.join(OUT, "catalog.json"),
                     {"fetchedAt": now.isoformat(timespec="seconds"), "file": BASE + "wp.series", "lastModified": smod,
                      "count": len(cat), "series": cat}, lambda a, b: a.get("series") == b["series"], indent=1)
    print("catalog:", len(cat), "series")
    spec = os.path.join(OUT, "series.json")
    if not os.path.isfile(spec):
        print("no series.json yet: catalog only")
        return
    chosen = json.load(open(spec, encoding="utf-8"))["series"]
    dtext, dmod = get("wp.data.0.Current")
    ftext, _ = get("wp.footnote")
    d = build(srows, rows(dtext), chosen, rows(ftext), now.isoformat(timespec="seconds"),
              {"series": {"url": BASE + "wp.series", "lastModified": smod}, "data": {"url": BASE + "wp.data.0.Current", "lastModified": dmod}})
    write_if_changed(os.path.join(OUT, "ppi.json"), d, lambda a, b: a.get("series") == b["series"],
                     indent=0, separators=(",", ":"))
    print("ppi:", len(d["series"]), "series, latest", d["latest"])


def selftest():
    s = ("series_id\tgroup_code\titem_code\tseasonal\tbase_date\tseries_title\tfootnote_codes\tbegin_year\tbegin_period\tend_year\tend_period\n"
         "WPU081      \t08\t1\tU\t198200\tLumber\t\t1947\tM01\t2026\tM09\n"
         "WPS081\t08\t1\tS\t198200\tLumber\t\t1947\tM01\t2026\tM09\n"
         "WPU0111\t01\t11\tU\t198200\tFresh fruits\t\t1947\tM01\t2026\tM09\n"
         "WPU1017\t10\t17\tU\t198200\tSteel mill products\t\t1947\tM01\t2009\tM12\n")
    d = ("series_id\tyear\tperiod\tvalue\tfootnote_codes\n"
         "WPU081\t2015\tM12\t180.0\t\nWPU081\t2025\tM09\t200.0\t\nWPU081\t2026\tM08\t210.5\tP\n"
         "WPU081\t2026\tM09\t212.0\tP\nWPU081\t2025\tM13\t199.0\t\nWPU081\t2026\tM07\t-\t\n")
    sr, dr = rows(s), rows(d)
    cat = catalog(sr, 2026)
    assert [c["id"] for c in cat] == ["WPU081"], cat   # NSA only, active only, building words only
    out = build(sr, dr, [{"id": "WPU081"}], [{"footnote_code": "P", "footnote_text": "Preliminary."}], "2026-10-27T12:00:00-05:00", {})
    obs = out["series"][0]["obs"]
    assert obs == [["2025-09", 200.0, ""], ["2026-08", 210.5, "P"], ["2026-09", 212.0, "P"]], obs   # no M13, no "-", no pre-2016
    assert out["latest"] == "2026-09" and out["source"]["footnotes"]["P"] == "Preliminary."
    try:
        build(sr, dr, [{"id": "WPU1017"}], [], "", {})
        raise AssertionError("a series with no values must stop the run")
    except SystemExit:
        pass
    print("dp_materials_bls selftest: ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
