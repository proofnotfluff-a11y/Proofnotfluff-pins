#!/usr/bin/env python3
"""CDOT 2026 Permit Fee Schedule: the source pull for the free page /chicago-public-way-permit-costs/ (site/pages.json
kind "datapage", module dp_cdot_fees). The owner's go, Oct 27, 2026, 12:17 pm ("Let's do them all", coo/PARALLEL_BUILDS.md,
research_notes/kimi-2026-10-27-r10.md item 6).

Runs in GitHub Actions (.github/workflows/dp_cdot_fees.yml), because the cloud agents cannot open chicago.gov PDFs.
Downloads the City's own PDF, extracts its text with pdftotext (poppler) and writes, under site/datapages/dp_cdot_fees/:
  fee-schedule.layout.txt   pdftotext -layout (columns kept, the page is built from this)
  fee-schedule.raw.txt      pdftotext default reading order (a second view for checkers)
  source.json               url, fetchedAt, bytes, sha256, pages, the PDF's own metadata
The fee figures on the page are typed into tools/dp_cdot_fees.py by hand from the layout text, and its selftest checks
every one of them still appears in this text, so a new City schedule fails the build instead of showing stale fees.

Usage: python3 tools/dp_cdot_fees_pull.py            download and extract (needs network and pdftotext)
       python3 tools/dp_cdot_fees_pull.py --from-file <pdf>   extract a copy of the City's PDF downloaded by hand
       python3 tools/dp_cdot_fees_pull.py --selftest  no network
"""
import datetime as dt, hashlib, json, os, subprocess, sys, time, urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "site", "datapages", "dp_cdot_fees")
URL = "https://www.chicago.gov/content/dam/city/depts/cdot/permit/2026/CDOT%202026%20Permit%20Fee%20Schedule.pdf"
UA = {"User-Agent": "ProofNotFluff data pages (github.com/proofnotfluff-a11y/proofnotfluff-pins)", "Accept": "application/pdf"}


def fetch(url=URL, tries=4):
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                body = r.read()
                return body, r.headers.get("Content-Type", ""), r.geturl()
        except Exception as e:   # noqa: BLE001 (any failure is retried, then reported)
            last = e
            print(f"::warning title=CDOT fee schedule::try {i + 1}: {str(e)[:200]}")   # an annotation: readable without the log
            time.sleep(5 * (i + 1))
    raise SystemExit(f"could not download the CDOT fee schedule: {last}")


def is_pdf(b):
    return b[:5] == b"%PDF-"


def pdfinfo(path):
    """Title, dates and page count only. The Author field (a City employee's name) is never kept."""
    out = subprocess.run(["pdfinfo", path], capture_output=True, text=True, check=True).stdout
    info = {}
    for line in out.splitlines():
        k, _, v = line.partition(":")
        if k.strip() in ("Title", "CreationDate", "ModDate", "Pages"):
            info[k.strip()] = v.strip()
    return info


def extract(body, how, final=URL, ctype="application/pdf"):
    """Text only goes in the repo: the PDF is read from a temporary file and not kept (its metadata names a person)."""
    import tempfile
    if not is_pdf(body):
        print(f"::warning title=CDOT fee schedule::not a PDF: {ctype!r}, {len(body)} bytes, starts {body[:80]!r}")
        raise SystemExit(f"not a PDF ({ctype!r}, {len(body)} bytes, from {final}); nothing written")
    os.makedirs(OUT, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        pdf = os.path.join(tmp, "fee-schedule.pdf")
        open(pdf, "wb").write(body)
        subprocess.run(["pdftotext", "-layout", pdf, os.path.join(OUT, "fee-schedule.layout.txt")], check=True)
        subprocess.run(["pdftotext", pdf, os.path.join(OUT, "fee-schedule.raw.txt")], check=True)
        info = pdfinfo(pdf)
    for f in ("fee-schedule.layout.txt", "fee-schedule.raw.txt"):   # the site's no-dash rule covers site/ (check_repo em-dash)
        t = os.path.join(OUT, f)
        clean = open(t, encoding="utf-8").read().replace("\u2014", "-").replace("\u2013", "-")   # read fully, then write
        open(t, "w", encoding="utf-8").write(clean)
    src = {"name": "CDOT 2026 Permit Fee Schedule", "publisher": "City of Chicago, Department of Transportation",
           "url": URL, "finalUrl": final, "how": how, "bytes": len(body),
           "sha256": hashlib.sha256(body).hexdigest(), "textNote": "pdftotext 24 output; em and en dashes replaced with plain hyphens; sha256 is of the City's PDF", "pages": int(info.get("Pages", "0") or 0), "pdf": info,
           "fetchedAt": dt.datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%dT%H:%M:%S%z")}
    json.dump(src, open(os.path.join(OUT, "source.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(src, indent=1))


def main():
    if "--from-file" in sys.argv:   # the City's PDF as the shop owner downloaded it in his own browser (Oct 27, 2026)
        path = sys.argv[sys.argv.index("--from-file") + 1]
        extract(open(path, "rb").read(), "downloaded from the URL in a browser and attached in a build chat")
        return
    body, ctype, final = fetch()
    extract(body, "downloaded by the GitHub Action", final, ctype)


def selftest():
    assert is_pdf(b"%PDF-1.7\n") and not is_pdf(b"<html>"), "PDF check"
    assert URL.startswith("https://www.chicago.gov/") and URL.endswith(".pdf"), "official source only"
    print("dp_cdot_fees_pull selftest: ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
