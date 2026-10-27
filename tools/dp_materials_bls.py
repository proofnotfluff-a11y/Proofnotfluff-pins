#!/usr/bin/env python3
"""BLS producer price indexes for the free Material Price Changes Since Your Quote page (tools/dp_materials.py).
Todd's go: Oct 27, 2026, 12:17 pm, "Let's do them all" (coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md).

Runs in GitHub Actions (.github/workflows/dp_materials.yml), because the cloud agents cannot reach bls.gov. Source:
U.S. Bureau of Labor Statistics, Producer Price Index by commodity (survey "wp"), read through the BLS Public Data API
(https://api.bls.gov/publicAPI/), the door BLS offers for programs. BLS's flat files refuse GitHub's runners (HTTP 403,
Oct 27, 2026), so they are not used.

Reads site/datapages/dp_materials/series.json (the series the page shows, each with BLS's title as read from BLS) and
writes site/datapages/dp_materials/ppi.json: every monthly value BLS returns for the last YEARS years, with BLS's
footnote codes ("P" marks a preliminary value BLS may still revise). Also writes status.json: per series, whether BLS
returned it, BLS's own catalog title when the API sends one, and BLS's messages, so a missing or renamed series is
seen the same day. Public statistics only; no person or business is in either file.

Usage: python3 tools/dp_materials_bls.py              pull and write
       python3 tools/dp_materials_bls.py --selftest   planted API answers, no network
"""
import datetime as dt, json, os, re, sys, urllib.error, urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "site", "datapages", "dp_materials")
API = {"v2": "https://api.bls.gov/publicAPI/v2/timeseries/data/", "v1": "https://api.bls.gov/publicAPI/v1/timeseries/data/"}
UA = {"User-Agent": "ProofNotFluff free data page (hello@proofnotfluff.com; github.com/proofnotfluff-a11y/proofnotfluff-pins)",
      "Content-Type": "application/json"}
YEARS = 10            # the API without a key returns at most 10 years per request
PER_CALL = 25         # and at most 25 series per request


def post(version, ids, start, end, catalog):
    body = {"seriesid": ids, "startyear": str(start), "endyear": str(end)}
    if catalog:
        body["catalog"] = True
    req = urllib.request.Request(API[version], data=json.dumps(body).encode(), headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return {"status": f"HTTP {e.code}", "message": [e.read()[:200].decode("utf-8", "replace")]}
    except Exception as e:
        return {"status": "ERROR", "message": [repr(e)]}


def months(series):
    """API data rows to [[YYYY-MM, value, footnote codes]], oldest first; M13 (annual) and blank values left out."""
    out = []
    for r in series.get("data") or []:
        per = r.get("period", "")
        if not re.fullmatch(r"M(0[1-9]|1[0-2])", per):
            continue
        try:
            v = float(r["value"])
        except (KeyError, ValueError):
            continue
        codes = "".join(sorted({(f or {}).get("code", "") for f in r.get("footnotes") or [] if (f or {}).get("code")}))
        out.append([f'{r["year"]}-{per[1:]}', v, codes])
    return sorted(out)


def notes(series):
    return {(f or {}).get("code"): (f or {}).get("text", "") for r in series.get("data") or [] for f in r.get("footnotes") or []
            if (f or {}).get("code")}


def pull(ids, start, end, call=post):
    """{id: {"obs", "catalog", "notes"}}, the API version that answered, and BLS's messages."""
    got, msgs, used = {}, [], None
    for i in range(0, len(ids), PER_CALL):
        chunk = ids[i:i + PER_CALL]
        for version, catalog in (("v2", True), ("v1", False)):
            ans = call(version, chunk, start, end, catalog)
            msgs += [f"{version}: {m}" for m in ans.get("message") or []]
            if ans.get("status") == "REQUEST_SUCCEEDED" and (ans.get("Results") or {}).get("series"):
                used = used or version
                for s in ans["Results"]["series"]:
                    obs = months(s)
                    if obs:
                        got[s["seriesID"]] = {"obs": obs, "catalog": s.get("catalog") or {}, "notes": notes(s)}
                break
    return got, used, msgs


def build(chosen, got, fetched, version):
    series, foot = [], {}
    for c in chosen:
        g = got.get(c["id"])
        if not g:
            continue
        foot.update(g["notes"])
        series.append({"id": c["id"], "title": c["title"], "obs": g["obs"]})
    if not series:
        return None
    return {"source": {"agency": "U.S. Bureau of Labor Statistics", "program": "Producer Price Index by commodity (wp), not seasonally adjusted",
                       "api": API[version] if version else "", "fetchedAt": fetched, "footnotes": foot},
            "latest": max(s["obs"][-1][0] for s in series), "series": series}


def status(chosen, got, version, msgs, fetched):
    return {"checkedAt": fetched, "api": version, "messages": sorted(set(msgs))[:60],
            "series": [{"id": c["id"], "ourTitle": c["title"], "returned": c["id"] in got,
                        "blsTitle": (got.get(c["id"]) or {}).get("catalog", {}).get("series_title", ""),
                        "last": (got.get(c["id"]) or {}).get("obs", [[""]])[-1][0]} for c in chosen]}


def write_if_changed(path, obj, same, **kw):
    """Write only when the numbers changed, so a run that finds no new BLS release commits nothing."""
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
    fetched = now.isoformat(timespec="seconds")
    chosen = json.load(open(os.path.join(OUT, "series.json"), encoding="utf-8"))["series"]
    got, version, msgs = pull([c["id"] for c in chosen], now.year - YEARS + 1, now.year)
    write_if_changed(os.path.join(OUT, "status.json"), status(chosen, got, version, msgs, fetched),
                     lambda a, b: {k: v for k, v in a.items() if k != "checkedAt"} == {k: v for k, v in b.items() if k != "checkedAt"}, indent=1)
    for m in sorted(set(msgs))[:20]:
        print(f"::notice title=BLS said::{m}")
    if not got:
        print("::error title=BLS API::no series came back")
        raise SystemExit("BLS API returned no series")
    d = build(chosen, got, fetched, version)
    write_if_changed(os.path.join(OUT, "ppi.json"), d, lambda a, b: a.get("series") == b["series"], indent=0, separators=(",", ":"))
    print("ppi:", len(d["series"]), "of", len(chosen), "series, latest", d["latest"], "via", version)


def selftest():
    def fake(version, ids, start, end, catalog):
        if version == "v2":
            return {"status": "REQUEST_NOT_PROCESSED", "message": ["planted: v2 refused"]}
        series = []
        for sid in ids:
            if sid == "WPUBAD":
                continue
            series.append({"seriesID": sid, "data": [
                {"year": "2026", "period": "M09", "value": "212.0", "footnotes": [{"code": "P", "text": "Preliminary."}]},
                {"year": "2026", "period": "M08", "value": "210.5", "footnotes": [{"code": "P", "text": "Preliminary."}]},
                {"year": "2025", "period": "M13", "value": "199.0", "footnotes": [{}]},
                {"year": "2025", "period": "M10", "value": "-", "footnotes": [{}]},
                {"year": "2025", "period": "M09", "value": "200.0", "footnotes": [{}]}]})
        return {"status": "REQUEST_SUCCEEDED", "message": [f"Series does not exist for Series {s}" for s in ids if s == "WPUBAD"],
                "Results": {"series": series}}
    chosen = [{"id": "WPU081", "title": "Lumber"}, {"id": "WPUBAD", "title": "Nothing"}]
    got, version, msgs = pull([c["id"] for c in chosen], 2017, 2026, call=fake)
    assert version == "v1" and set(got) == {"WPU081"}, (version, got)
    assert got["WPU081"]["obs"] == [["2025-09", 200.0, ""], ["2026-08", 210.5, "P"], ["2026-09", 212.0, "P"]], got   # no M13, no "-"
    d = build(chosen, got, "2026-10-27T12:00:00-05:00", version)
    assert d["latest"] == "2026-09" and d["source"]["footnotes"]["P"] == "Preliminary." and len(d["series"]) == 1
    st = status(chosen, got, version, msgs, "x")
    assert [s["returned"] for s in st["series"]] == [True, False] and any("does not exist" in m for m in st["messages"])
    big = pull([f"WPU{i}" for i in range(30)], 2017, 2026, call=fake)[0]
    assert len(big) == 30, "more than 25 series go in two requests"
    print("dp_materials_bls selftest: ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
