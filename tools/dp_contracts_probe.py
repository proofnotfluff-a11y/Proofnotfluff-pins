#!/usr/bin/env python3
"""Chicago City Contracts by Trade: one-off source check, run in GitHub Actions (the cloud agents cannot reach
chicago.gov or data.cityofchicago.org). Todd's go, Oct 27, 2026, 12:17 pm ("Let's do them all", coo/PARALLEL_BUILDS.md).

It reads, from the City's own servers:
  1. the Contracts dataset (rsxa-ify5): its column list, update time, row count and the spread of contract types,
     procurement types, revision numbers and award amounts (counts only);
  2. the City's Data Terms of Use page, saved as text for the Legal desk;
  3. the Department of Procurement Services pages and the 2026 weekly bid opportunity PDFs (which weeks exist).
Committed: site/datapages/dp_contracts/probe.json and source-terms.txt (counts, column names, URLs, no vendor
address and no person). Kept only as a short-lived workflow artifact, never committed: a few sample rows and the text
of the newest weekly bid PDF, so the build chat can read their layout.

Usage: python3 tools/dp_contracts_probe.py [--art DIR]
"""
import argparse, datetime as dt, html.parser, json, os, re, time, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "site", "datapages", "dp_contracts")
PORTAL = "https://data.cityofchicago.org"
DATASET = "rsxa-ify5"
TERMS_URL = "https://www.chicago.gov/city/en/narr/foia/data_disclaimer.html"
DPS_URL = "https://www.chicago.gov/city/en/depts/dps/provdrs/contract/svcs/DPSOverview.html"
WEEKLY = "https://www.chicago.gov/content/dam/city/depts/dps/WeeklyBidOpportunities/{y}WeeklyBidOpportunities/{mmddyy}.pdf"
UA = {"User-Agent": "ProofNotFluff data page (github.com/proofnotfluff-a11y/proofnotfluff-pins)"}
CHI = ZoneInfo("America/Chicago")
ADDRESS_LIKE = re.compile(r"address|city|state|zip|phone|email|fax|contact|location", re.I)


def get(url, tries=3, raw=False):
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                b = r.read()
                return (b, r.status, r.headers.get("Content-Type", "")) if raw else b.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if raw:
                return (b"", e.code, "")
            last = e
        except Exception as e:
            last = e
        time.sleep(4 * (i + 1))
    if raw:
        return (b"", 0, str(last))
    raise RuntimeError(f"fetch failed: {url[:160]} ({last})")


def soql(params):
    return json.loads(get(f"{PORTAL}/resource/{DATASET}.json?" + urllib.parse.urlencode(params)))


class Links(html.parser.HTMLParser):
    def __init__(self, base):
        super().__init__(); self.base = base; self.out = []; self.cur = None; self.txt = []
        self.text = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"): self.skip += 1
        if tag in ("p", "li", "h1", "h2", "h3", "h4", "br", "div", "tr"): self.text.append("\n")
        if tag == "a":
            self.cur = urllib.parse.urljoin(self.base, dict(attrs).get("href") or ""); self.txt = []
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip: self.skip -= 1
        if tag == "a" and self.cur:
            self.out.append((re.sub(r"\s+", " ", "".join(self.txt)).strip(), self.cur)); self.cur = None
    def handle_data(self, data):
        if self.cur is not None: self.txt.append(data)
        if not self.skip: self.text.append(data)


def page(url):
    p = Links(url); p.feed(get(url))
    lines = [re.sub(r"\s+", " ", x).strip() for x in "".join(p.text).split("\n")]
    return p.out, [x for x in lines if len(x) > 2]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--art", default=None); ap.add_argument("--notices", action="store_true"); a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    now = dt.datetime.now(CHI)
    res = {"checkedAt": now.isoformat(timespec="seconds"), "dataset": {}, "terms": {}, "dps": {}, "errors": []}
    art = {}
    # 1. the dataset
    try:
        meta = json.loads(get(f"{PORTAL}/api/views/{DATASET}.json"))
        res["dataset"] = {"name": meta.get("name"), "rowsUpdatedAt": meta.get("rowsUpdatedAt"),
                          "rowsUpdatedAtIso": dt.datetime.fromtimestamp(meta.get("rowsUpdatedAt") or 0, CHI).isoformat(),
                          "columns": [{"field": c.get("fieldName"), "name": c.get("name"), "type": c.get("dataTypeName"),
                                       "description": (c.get("description") or "")[:400]} for c in meta.get("columns", [])],
                          "description": (meta.get("description") or "")[:2000],
                          "attribution": meta.get("attribution"), "license": (meta.get("license") or {}).get("name"),
                          "category": meta.get("category")}
        fields = [c["field"] for c in res["dataset"]["columns"]]
        res["dataset"]["rows"] = soql({"$select": "count(*) as n"})[0]["n"]
        for f in ("contract_type", "procurement_type", "revision_number", "department"):
            if f in fields:
                res["dataset"]["by_" + f] = soql({"$select": f"{f}, count(*) as n", "$group": f, "$order": "n DESC", "$limit": 80})
        if "award_amount" in fields:
            for k, w in (("negative", "award_amount < 0"), ("zero", "award_amount = 0"), ("positive", "award_amount > 0"), ("null", "award_amount IS NULL")):
                res["dataset"]["amount_" + k] = soql({"$select": "count(*) as n", "$where": w})[0]["n"]
        for f in ("approval_date", "start_date", "end_date"):
            if f in fields:
                res["dataset"]["range_" + f] = soql({"$select": f"min({f}) as lo, max({f}) as hi"})[0]
        if "revision_number" in fields and "approval_date" in fields:
            res["dataset"]["recent_by_revision"] = soql({"$select": "revision_number, count(*) as n, sum(award_amount) as s",
                                                         "$where": "approval_date >= '2025-10-01T00:00:00'", "$group": "revision_number",
                                                         "$order": "n DESC", "$limit": 30})
        keep = [f for f in fields if not ADDRESS_LIKE.search(f) and not f.startswith(":")]
        art["sample"] = soql({"$select": ",".join(keep), "$order": "approval_date DESC", "$limit": 25})
        art["sample_zero"] = soql({"$select": ",".join(keep), "$where": "award_amount = 0", "$order": "approval_date DESC", "$limit": 10})
        art["sample_neg"] = soql({"$select": ",".join(keep), "$where": "award_amount < 0", "$order": "approval_date DESC", "$limit": 10})
    except Exception as e:
        res["errors"].append(f"dataset: {e}")
    # 2. the terms page
    try:
        _, lines = page(TERMS_URL)
        open(os.path.join(OUT, "source-terms.txt"), "w", encoding="utf-8").write(
            f"Source: {TERMS_URL}\nFetched: {now.isoformat(timespec='seconds')}\n\n" + "\n".join(lines) + "\n")
        res["terms"] = {"url": TERMS_URL, "ok": True, "lines": len(lines)}
    except Exception as e:
        res["terms"] = {"url": TERMS_URL, "ok": False, "error": str(e)}
    # 3. procurement pages and the 2026 weekly bid list
    try:
        links, lines = page(DPS_URL)
        res["dps"]["overview"] = {"url": DPS_URL, "links": [(t, u) for t, u in links if re.search(r"bid|solicit|opportunit|weekly|isupplier|eprocure|contract", t + " " + u, re.I)][:80],
                                  "textHead": lines[:80]}
        seen = set()
        sub = []
        for t, u in res["dps"]["overview"]["links"]:
            if "chicago.gov" in u and u.endswith(".html") and u not in seen and re.search(r"bid|opportunit|weekly", t + u, re.I):
                seen.add(u)
                try:
                    l2, x2 = page(u)
                    sub.append({"url": u, "text": t, "links": [(a_, b_) for a_, b_ in l2 if re.search(r"bid|solicit|opportunit|weekly|isupplier|eprocure|pdf", a_ + " " + b_, re.I)][:120], "textHead": x2[:60]})
                except Exception as e:
                    sub.append({"url": u, "error": str(e)})
        res["dps"]["subpages"] = sub
    except Exception as e:
        res["errors"].append(f"dps: {e}")
    weeks = []
    d = dt.date(2026, 1, 1)
    while d <= now.date():
        if d.weekday() == 0 or d >= now.date() - dt.timedelta(days=21):   # Mondays, plus every day of the last three weeks
            u = WEEKLY.format(y=d.year, mmddyy=d.strftime("%m%d%y"))
            b, st, ct = get(u, tries=1, raw=True)
            if st == 200 and b[:4] == b"%PDF":
                weeks.append({"date": d.isoformat(), "url": u, "bytes": len(b)})
                last = b
        d += dt.timedelta(days=1)
    res["dps"]["weekly2026"] = weeks
    if weeks and a.art:
        os.makedirs(a.art, exist_ok=True)
        open(os.path.join(a.art, "latest-weekly.pdf"), "wb").write(last)
        try:
            import io, pypdf
            art["latest_weekly_text"] = "\n".join((pg.extract_text(extraction_mode="layout") or "") for pg in pypdf.PdfReader(io.BytesIO(last)).pages)[:60000]
        except Exception as e:
            art["latest_weekly_text"] = f"pdf text failed: {e}"
    json.dump(res, open(os.path.join(OUT, "probe.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    if a.art:
        os.makedirs(a.art, exist_ok=True)
        json.dump(art, open(os.path.join(a.art, "art.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    # The runner's logs and artifacts are not readable from the cloud session, so the layout the build chat needs comes
    # back as a few workflow notices: sample rows (business fields only) and the bid list text with contact lines left out.
    if a.notices:
        for i, r in enumerate((art.get("sample") or [])[:6] + (art.get("sample_zero") or [])[:3] + (art.get("sample_neg") or [])[:3]):
            r = {k: (v if not isinstance(v, str) else v[:160]) for k, v in r.items()}
            print(f"::notice title=sample {i}::" + json.dumps(r, ensure_ascii=False).replace("%", "%25").replace("\n", " ")[:3000])
        txt = "\n".join(l for l in (art.get("latest_weekly_text") or "").split("\n")
                         if not re.search(r"@|\(\d{3}\)|\d{3}[-.]\d{3}[-.]\d{4}|contact|buyer|specialist|officer|phone|e-?mail", l, re.I))
        txt = re.sub(r"[ \t]{3,}", "  |  ", txt)
        for i in range(0, min(len(txt), 30000), 2900):
            print(f"::notice title=weekly {i // 2900}::" + txt[i:i + 2900].replace("%", "%25").replace("\r", "").replace("\n", "%0A"))
    print(json.dumps({"rows": res["dataset"].get("rows"), "terms": res["terms"].get("ok"), "weeks": len(weeks), "errors": res["errors"]}))


if __name__ == "__main__":
    main()
