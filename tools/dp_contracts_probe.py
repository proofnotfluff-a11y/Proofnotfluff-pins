#!/usr/bin/env python3
"""Chicago City Contracts by Trade: the daily source check, run in GitHub Actions (the cloud agents cannot reach
chicago.gov). Todd's go, Oct 27, 2026, 12:17 pm ("Let's do them all", coo/PARALLEL_BUILDS.md).

It opens, from the City's own servers, and writes site/datapages/dp_contracts/sources.json (URLs, dates, yes or no):
  1. the City's Data Terms of Use page, saved word for word as source-terms.txt for the Legal desk;
  2. the Procurement Services Current Bid Opportunities page, and the weekly bid opportunity list (PDF) it links
     today: the list's date comes from its file name (MMDDYY.pdf), and whether the PDF itself opened for us;
  3. the eProcurement bid list page (whether it loads).
The page says where open bids live from this file, never from memory. No open bid is listed on our page: the weekly
PDF refuses automated readers (HTTP 403, checked Oct 27, 2026) and the eProcurement list pages through a session, so
neither gives us a complete list we could stand behind.

Usage: python3 tools/dp_contracts_probe.py
       python3 tools/dp_contracts_probe.py --selftest
"""
import argparse, datetime as dt, html.parser, json, os, re, time, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "site", "datapages", "dp_contracts")
TERMS_URL = "https://www.chicago.gov/city/en/narr/foia/data_disclaimer.html"
DPS_URL = "https://www.chicago.gov/city/en/depts/dps/provdrs/contract/svcs/DPSOverview.html"
BIDS_URL = "https://www.chicago.gov/city/en/depts/dps/provdrs/contract/svcs/current_bid_opportunities.html"
EPROC_PAGE = "https://www.chicago.gov/city/en/depts/dps/isupplier/current-bids.html"
EPROC_LIST = "https://eprocurement.cityofchicago.org/OA_HTML/OA.jsp?OAFunc=PON_ABSTRACT_PAGE"
UA = {"User-Agent": "ProofNotFluff data page (github.com/proofnotfluff-a11y/proofnotfluff-pins)"}
CHI = ZoneInfo("America/Chicago")


def get(url, tries=3):
    """(body bytes, HTTP status). Status 0 when the host never answered."""
    last = 0
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return r.read(), r.status
        except urllib.error.HTTPError as e:
            if e.code in (403, 404, 410):
                return b"", e.code
            last = e.code
        except Exception:
            last = 0
        time.sleep(4 * (i + 1))
    return b"", last


class Page(html.parser.HTMLParser):
    def __init__(self, base):
        super().__init__(); self.base = base; self.links = []; self.cur = None; self.txt = []; self.text = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"): self.skip += 1
        if tag in ("p", "li", "h1", "h2", "h3", "h4", "br", "div", "tr"): self.text.append("\n")
        if tag == "a":
            self.cur = urllib.parse.urljoin(self.base, dict(attrs).get("href") or ""); self.txt = []
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip: self.skip -= 1
        if tag == "a" and self.cur:
            self.links.append((re.sub(r"\s+", " ", "".join(self.txt)).strip(), self.cur)); self.cur = None
    def handle_data(self, data):
        if self.cur is not None: self.txt.append(data)
        if not self.skip: self.text.append(data)


def parse(body, url):
    p = Page(url); p.feed(body.decode("utf-8", "replace"))
    lines = [re.sub(r"\s+", " ", x).strip() for x in "".join(p.text).split("\n")]
    return p.links, [x for x in lines if len(x) > 2]


def weekly_link(links):
    """The weekly bid opportunity list the page links, with the date in its file name (MMDDYY.pdf)."""
    for t, u in links:
        m = re.search(r"WeeklyBidOpportunities/(\d{4})WeeklyBidOpportunities/(\d{2})(\d{2})(\d{2})\.pdf$", u)
        if m:
            y, mm, dd, yy = m.groups()
            try:
                d = dt.date(2000 + int(yy), int(mm), int(dd))
            except ValueError:
                continue
            return {"url": u, "text": t, "date": d.isoformat(), "year": int(y)}
    return None


def check(now):
    res = {"checkedAt": now.isoformat(timespec="seconds"), "terms": {"url": TERMS_URL}, "overview": {"url": DPS_URL},
           "bids": {"url": BIDS_URL}, "eprocPage": {"url": EPROC_PAGE}, "eprocList": {"url": EPROC_LIST}}
    b, st = get(TERMS_URL)
    res["terms"]["status"] = st
    if st == 200:
        _, lines = parse(b, TERMS_URL)
        start = next((i for i, x in enumerate(lines) if x == "Data Terms of Use"), 0)
        open(os.path.join(OUT, "source-terms.txt"), "w", encoding="utf-8").write(
            f"Source: {TERMS_URL}\nFetched: {now.isoformat(timespec='seconds')}\n\n" + "\n".join(lines[start:]) + "\n")
        import sys; sys.path.insert(0, HERE)
        import make_site as M
        res["terms"]["ok"] = any("\u201c" + M.CITY_DISCLAIMER["Chicago"] + "\u201d" in x for x in lines)
        if not res["terms"]["ok"]:   # the City changed its required disclaimer: nothing publishes until the Legal desk has read it
            raise SystemExit("City Data Terms disclaimer no longer matches make_site.CITY_DISCLAIMER: stop and send to the Legal desk")
    for key, url in (("overview", DPS_URL), ("eprocPage", EPROC_PAGE)):
        b, st = get(url)
        res[key]["status"] = st
    b, st = get(BIDS_URL)
    res["bids"]["status"] = st
    if st == 200:
        links, lines = parse(b, BIDS_URL)
        res["bids"]["weekly"] = weekly_link(links)
        res["bids"]["mentionsEproc"] = any("eProcurement Bid Opportunities" in x for x in lines)
        w = res["bids"]["weekly"]
        if w:
            pb, pst = get(w["url"], tries=2)
            w["pdfStatus"] = pst
            w["pdfOpened"] = pst == 200 and pb[:4] == b"%PDF"
    b, st = get(EPROC_LIST, tries=2)
    res["eprocList"]["status"] = st
    res["eprocList"]["loads"] = st == 200 and b"Supplier Response Due Date" in b
    return res


def selftest():
    links = [("DOWNLOAD THE BID OPPORTUNITY LIST (PDF)", "https://www.chicago.gov/content/dam/city/depts/dps/WeeklyBidOpportunities/2026WeeklyBidOpportunities/102626.pdf")]
    w = weekly_link(links)
    assert w["date"] == "2026-10-26" and w["year"] == 2026, w
    assert weekly_link([("x", "https://www.chicago.gov/a/b.pdf")]) is None
    _, lines = parse(b"<html><body><nav>Menu</nav><p>Data Terms of Use</p><p>This site provides applications using data</p></body></html>", TERMS_URL)
    assert "Data Terms of Use" in lines
    print("dp_contracts_probe selftest: ok")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        return selftest()
    os.makedirs(OUT, exist_ok=True)
    res = check(dt.datetime.now(CHI))
    json.dump(res, open(os.path.join(OUT, "sources.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps(res))


if __name__ == "__main__":
    main()
