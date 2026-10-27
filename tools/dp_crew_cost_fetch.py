#!/usr/bin/env python3
"""What a Chicago Crew Costs: the data pull for tools/dp_crew_cost.py (Todd, Oct 27, 2026, 12:17 pm: "Let's do them
all"; coo/PARALLEL_BUILDS.md, research_notes/kimi-2026-10-27-r10.md item 7).

Runs in GitHub Actions (.github/workflows/dp-crew-cost.yml), because the cloud agents cannot reach bls.gov, chicago.gov
or the Illinois Department of Labor's rate files. Every source is an official agency file; nothing here names a person
or a business. Two steps:

  fetch   download each source as-is into a raw folder (a short-lived workflow artifact, never committed) and write
          a manifest of what was reached, with HTTP status, size and the links found on each index page
  build   read the raw folder and write site/datapages/dp_crew_cost/data.json: hourly wage percentiles per role
          (BLS OEWS, Chicago metro), Cook County prevailing wage base and fringes per trade (IDOL), the Chicago and
          Cook County minimum wages and the Chicago paid leave rules (City and County notices), and the employer
          Social Security and Medicare rates (IRS). A field that could not be read from its source is left out.

Usage: python3 tools/dp_crew_cost_fetch.py fetch RAWDIR
       python3 tools/dp_crew_cost_fetch.py build RAWDIR
       python3 tools/dp_crew_cost_fetch.py --selftest
"""
import datetime as dt, html, io, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request, zipfile
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "site", "datapages", "dp_crew_cost")
OUT = os.path.join(OUTDIR, "data.json")
UA = {"User-Agent": "ProofNotFluff public data (hello@proofnotfluff.com; github.com/proofnotfluff-a11y/proofnotfluff-pins)",
      "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9"}

# Every source the page uses. Index pages are scanned for links that match `follow`, so a renamed file is still found.
SOURCES = {
    "oews_zip": {"url": "https://www.bls.gov/oes/special-requests/oesm25ma.zip"},
    "oews_msa_page": {"url": "https://www.bls.gov/oes/2025/may/oes_16980.htm"},
    "oews_current_page": {"url": "https://www.bls.gov/oes/current/oes_16980.htm"},
    "oews_tables_page": {"url": "https://www.bls.gov/oes/tables.htm", "follow": r"oesm25ma\.zip"},
    "oe_occupation": {"url": "https://download.bls.gov/pub/time.series/oe/oe.occupation"},
    "idol_current": {"url": "https://labor.illinois.gov/laws-rules/conmed/current-prevailing-rates.html", "follow": r"(?i)cook"},
    "chi_notice": {"url": "https://www.chicago.gov/content/dam/city/depts/bacp/OSL/2026_MW%20and%20PL-English_Public%20Notice_FINAL_20260527.pdf"},
    "chi_poster": {"url": "https://www.chicago.gov/content/dam/city/depts/bacp/OSL/2026_OLS_MINIMUM-WAGE_English.pdf"},
    "chi_onepager": {"url": "https://www.chicago.gov/content/dam/city/depts/bacp/OSL/july2026onepagerfinal.pdf"},
    "chi_mw_page": {"url": "https://www.chicago.gov/city/en/depts/bacp/supp_info/minimumwageinformation.html", "follow": r"(?i)2026.*\.pdf"},
    "chi_ols_page": {"url": "https://www.chicago.gov/city/en/depts/bacp/supp_info/office-of-labor-standards.html", "follow": r"(?i)2026.*\.pdf"},
    "cook_news": {"url": "https://www.cookcountyil.gov/news/cook-county-issues-notice-minimum-wage-ordinance-5"},
    "cook_faq": {"url": "https://www.cookcountyil.gov/sites/g/files/ywwepo161/files/documents/2026-07/_Final_Draft_Cook_County_Minimum_Wage_Ordinance_ENG_FAQ_07012026%20.pdf"},
    "cook_mw_page": {"url": "https://www.cookcountyil.gov/content/cook-county-minimum-wage", "follow": r"(?i)(2026|minimum).*\.pdf"},
    "irs_p15": {"url": "https://www.irs.gov/publications/p15"},
}


def now_chicago():
    return dt.datetime.now(ZoneInfo("America/Chicago"))


def get(url, tries=3):
    """(status, bytes, final url). Never raises; a blocked host is a status, not a crash."""
    last = (0, b"", url)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.status, r.read(), r.geturl()
        except urllib.error.HTTPError as e:
            last = (e.code, b"", url)
            if e.code in (403, 404, 410):
                break
        except Exception as e:   # timeouts, resets, DNS
            last = (-1, str(e).encode()[:300], url)
        time.sleep(4 * (i + 1))
    return last


def links(body, base):
    out = []
    for m in re.finditer(rb'href\s*=\s*["\']([^"\']+)["\']', body):
        u = html.unescape(m.group(1).decode("utf-8", "replace")).strip()
        if u and not u.startswith(("javascript:", "mailto:", "#")):
            out.append(urllib.parse.urljoin(base, u))
    return list(dict.fromkeys(out))


def safe_name(key, url):
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower() or ".html"
    return key + (ext if len(ext) <= 6 else ".bin")


def fetch(raw):
    os.makedirs(raw, exist_ok=True)
    man = {"fetchedAt": now_chicago().isoformat(timespec="seconds"), "files": {}}
    queue = [(k, v["url"], v.get("follow")) for k, v in SOURCES.items()]
    seen = set()
    while queue:
        key, url, follow = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        st, body, final = get(url)
        name = safe_name(key, url)
        ok = st == 200 and len(body) > 200
        if ok:
            open(os.path.join(raw, name), "wb").write(body)
        rec = {"url": url, "final": final, "status": st, "bytes": len(body) if ok else 0, "file": name if ok else None}
        if ok and follow and name.endswith((".html", ".htm")):
            found = [u for u in links(body, final) if re.search(follow, u)]
            rec["followed"] = found[:40]
            for j, u in enumerate(found[:40]):
                queue.append((f"{key}_link{j}", u, None))
        if not ok and st == -1:
            rec["error"] = body.decode("utf-8", "replace")
        man["files"][key] = rec
        print(f"{st:>4} {rec['bytes']:>9} {key} {url}")
        time.sleep(1.5)
    # BLS API v1 (no key) as a second route to the same OEWS numbers, in case the zip is refused
    man["files"]["oews_api"] = api_fallback(raw)
    json.dump(man, open(os.path.join(raw, "manifest.json"), "w"), indent=1)
    return man


# The page's roles, matched to BLS occupation titles in the BLS file itself; the codes come from that file.
ROLES = [
    ("janitors", "Janitors and Cleaners, Except Maids and Housekeeping Cleaners"),
    ("maids", "Maids and Housekeeping Cleaners"),
    ("pest", "Pest Control Workers"),
    ("landscapers", "Landscaping and Groundskeeping Workers"),
    ("roofers", "Roofers"),
    ("painters", "Painters, Construction and Maintenance"),
    ("helpers", "Helpers, Construction Trades"),
    ("electricians", "Electricians"),
    ("plumbers", "Plumbers, Pipefitters, and Steamfitters"),
    ("hvac", "Heating, Air Conditioning, and Refrigeration Mechanics and Installers"),
    ("carpenters", "Carpenters"),
    ("laborers", "Construction Laborers"),
]
MSA = "16980"   # Chicago-Naperville-Elgin, IL-IN (BLS area code, confirmed against AREA_TITLE in the file at build time)


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower().replace("--", " ")).strip()


def api_fallback(raw):
    """Pull the same series from api.bls.gov when the zip is refused. Needs codes from BLS's own oe.occupation list."""
    occ = next((os.path.join(raw, f) for f in sorted(os.listdir(raw)) if f.startswith("oe_occupation.")), "")
    if os.path.isfile(os.path.join(raw, "oews_zip.zip")):
        return {"skipped": "zip reached"}
    if not os.path.isfile(occ):
        return {"skipped": "no oe.occupation list to take codes from"}
    codes = {}
    for line in open(occ, encoding="utf-8", errors="replace"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) > 1 and re.fullmatch(r"\d{6}", parts[0]):
            codes[norm(parts[1])] = parts[0]
    want = {k: codes.get(norm(t)) for k, t in ROLES}
    series = [f"OEUM00{MSA}000000{c}{dt_}" for c in want.values() if c for dt_ in ("01", "03", "06", "07", "08", "09", "10")]
    got = {}
    for i in range(0, len(series), 25):
        body = json.dumps({"seriesid": series[i:i + 25]}).encode()
        try:
            req = urllib.request.Request("https://api.bls.gov/publicAPI/v1/timeseries/data/", data=body,
                                         headers=dict(UA, **{"Content-Type": "application/json"}))
            with urllib.request.urlopen(req, timeout=90) as r:
                got[str(i)] = json.loads(r.read())
        except Exception as e:
            got[str(i)] = {"error": str(e)[:300]}
        time.sleep(2)
    json.dump({"codes": want, "responses": got}, open(os.path.join(raw, "oews_api.json"), "w"))
    return {"series": len(series), "codes": want}


# ---------------------------------------------------------------- source extracts (committed, for the facts gate)
EXTRACTS = os.path.join(OUTDIR, "extracts.json")


def pdf_text(path):
    from pypdf import PdfReader
    return "\n\f\n".join((pg.extract_text() or "") for pg in PdfReader(path).pages)


def html_text(body):
    t = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", body)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return re.sub(r"[ \t\r\f\v]+", " ", re.sub(r"\n\s*\n+", "\n", html.unescape(t))).strip()


def oews_rows(path):
    """The Chicago metro rows of the OEWS May 2025 metro file: every occupation whose title matches a role, plus every
    helpers row, all columns as BLS wrote them. Public statistics only."""
    import openpyxl
    z = zipfile.ZipFile(path)
    name = next(n for n in z.namelist() if n.lower().endswith(".xlsx"))
    wb = openpyxl.load_workbook(io.BytesIO(z.read(name)), read_only=True)
    ws = wb.worksheets[0]
    it = ws.iter_rows(values_only=True)
    head = [str(h).strip().upper() for h in next(it)]
    want = {norm(t) for _, t in ROLES}
    out = []
    for r in it:
        d = dict(zip(head, r))
        if str(d.get("AREA")).split(".")[0] != MSA:
            continue
        t = norm(str(d.get("OCC_TITLE") or ""))
        if t in want or t.startswith("helpers") or str(d.get("OCC_CODE")) in ("00-0000",):
            out.append({k: (v if isinstance(v, (int, float)) or v is None else str(v)) for k, v in d.items()})
    return {"file": name, "columns": head, "rows": out}


def extract(raw):
    import hashlib
    man = json.load(open(os.path.join(raw, "manifest.json")))
    ex = {"fetchedAt": man["fetchedAt"], "files": {}}
    for key, rec in man["files"].items():
        e = {k: rec.get(k) for k in ("url", "final", "status", "bytes", "followed") if rec.get(k) is not None}
        f = rec.get("file") and os.path.join(raw, rec["file"])
        if f and os.path.isfile(f):
            b = open(f, "rb").read()
            e["sha256"] = hashlib.sha256(b).hexdigest()
            try:
                if f.endswith(".pdf"):
                    e["text"] = pdf_text(f)[:60000]
                elif f.endswith(".zip"):
                    e["oews"] = oews_rows(f)
                elif key == "oe_occupation" or f.endswith(".bin"):
                    e["text"] = "\n".join(l for l in b.decode("utf-8", "replace").splitlines() if re.search(r"(?i)helpers|janitor|maids|pest|landscap|roofer|painters, construction|electricians|plumbers|heating, air|carpenters|construction laborers", l))[:20000]
                else:
                    e["text"] = html_text(b.decode("utf-8", "replace"))[:40000]
            except Exception as err:
                e["error"] = f"{type(err).__name__}: {err}"[:300]
        ex["files"][key] = e
    api = os.path.join(raw, "oews_api.json")
    if os.path.isfile(api):
        ex["oews_api"] = json.load(open(api))
    os.makedirs(OUTDIR, exist_ok=True)
    json.dump(ex, open(EXTRACTS, "w"), indent=1, ensure_ascii=False)
    print("extracts:", {k: (v.get("status"), len(v.get("text", "")) or len(json.dumps(v.get("oews", "")))) for k, v in ex["files"].items()})


# ---------------------------------------------------------------- build (filled in once the raw files are seen)
def build(raw):
    print("build: parsers not written yet (probe run); extracts only")


def selftest():
    assert norm("Helpers--Carpenters") == "helpers carpenters"
    assert links(b'<a href="/a/b.pdf">x</a><a href="mailto:x">', "https://x.gov/c/d.html") == ["https://x.gov/a/b.pdf"]
    assert safe_name("k", "https://x.gov/a/b.PDF") == "k.pdf" and safe_name("k", "https://x.gov/a/") == "k.html"
    print("dp_crew_cost_fetch selftest: ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--selftest"]:
        selftest()
    elif a[:1] == ["fetch"] and len(a) == 2:
        fetch(a[1])
    elif a[:1] == ["build"] and len(a) == 2:
        extract(a[1])
        build(a[1])
    else:
        sys.exit(__doc__)
