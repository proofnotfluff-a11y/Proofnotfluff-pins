#!/usr/bin/env python3
"""What a Chicago Crew Costs: the data for tools/dp_crew_cost.py (Todd, Oct 27, 2026, 12:17 pm: "Let's do them all";
coo/PARALLEL_BUILDS.md, research_notes/kimi-2026-10-27-r10.md item 7).

Where each number comes from
- Metro pay: BLS OEWS May 2025, metropolitan area file oesm25ma.zip (MSA_M2025_dl.xlsx), Chicago-Naperville-Elgin
  rows. www.bls.gov refuses scripted downloads from our runners, so Todd downloaded the zip in his own browser on
  Oct 27, 2026; `ingest` reads that copy and records its sha256.
- Cook County prevailing wage: the Illinois Department of Labor's Cook County schedule (PDF titled "Cook", footer
  "Cook County Prevailing Wage Rates posted on 10/19/2026"), opened from the IDOL current rates page by Todd on Oct 27,
  2026 (the page lists county files by script, so no single link exists). Read by column position, every row kept.
- Chicago minimum wage and paid leave: the City's public notice (2026_MW and PL-English_Public Notice_FINAL_20260527.pdf,
  "Notice effective on July 1, 2026. Last updated May 27, 2026."), downloaded by Todd on Oct 27, 2026.
- Cook County minimum wage: the County's own notice page (June 1, 2026). Employer Social Security and Medicare: IRS
  Publication 15 (2026). Both are pages the weekly workflow can reach.

Modes
  ingest ZIP COOKPDF NOTICEPDF PAGES.json   run here on the downloaded files (PAGES.json: {"cook_news": text,
                                 "irs_p15": text} read by the workflow); writes site/datapages/dp_crew_cost/data.json
  watch [RAWDIR]                 run weekly in .github/workflows/dp-crew-cost.yml: re-reads the City minimum wage page,
                                 the Cook County notice, IRS Publication 15 and the IDOL current rates page, and writes
                                 site/datapages/dp_crew_cost/watch.json: each watched figure, what the source says now,
                                 PASS or FAIL. A FAIL means a source changed and data.json needs a new ingest.
  --selftest                     planted inputs, no network

Nothing here names a person or a business, and no raw page text is committed: only the figures and the short line
each figure was read from.
"""
import datetime as dt, hashlib, html, io, json, os, re, sys, time, urllib.error, urllib.request, zipfile
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "site", "datapages", "dp_crew_cost")
DATA = os.path.join(OUTDIR, "data.json")
WATCH = os.path.join(OUTDIR, "watch.json")
UA = {"User-Agent": "ProofNotFluff public data (hello@proofnotfluff.com; github.com/proofnotfluff-a11y/proofnotfluff-pins)",
      "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9"}

URLS = {
    "oews": "https://www.bls.gov/oes/special-requests/oesm25ma.zip",
    "oews_tables": "https://www.bls.gov/oes/tables.htm",
    "idol": "https://labor.illinois.gov/laws-rules/conmed/current-prevailing-rates.html",
    "chi_notice": "https://www.chicago.gov/content/dam/city/depts/bacp/OSL/2026_MW%20and%20PL-English_Public%20Notice_FINAL_20260527.pdf",
    "chi_mw": "https://www.chicago.gov/city/en/depts/bacp/supp_info/minimumwageinformation.html",
    "chi_ols": "https://www.chicago.gov/city/en/depts/bacp/supp_info/office-of-labor-standards.html",
    "cook_news": "https://www.cookcountyil.gov/news/cook-county-issues-notice-minimum-wage-ordinance-5",
    "irs_p15": "https://www.irs.gov/publications/p15",
}
MSA = "16980"   # Chicago-Naperville-Elgin, IL-IN; ingest checks AREA_TITLE

# The page's roles and the BLS rows behind each. Codes were matched against BLS's Occupational Outlook Handbook pages
# on Oct 27, 2026 (their job outlook tables); the titles shown come from the BLS file itself.
ROLES = [
    ("janitors", "Janitors", ["37-2011"]),
    ("maids", "Maids and housekeepers", ["37-2012"]),
    ("pest", "Pest control workers", ["37-2021"]),
    ("landscapers", "Landscapers", ["37-3011"]),
    ("roofers", "Roofers", ["47-2181"]),
    ("painters", "Painters", ["47-2141"]),
    ("helpers", "Construction helpers", ["47-3011", "47-3012", "47-3013", "47-3014", "47-3015", "47-3016", "47-3019"]),
    ("electricians", "Electricians", ["47-2111"]),
    ("plumbers", "Plumbers and pipefitters", ["47-2152"]),
    ("hvac", "HVAC techs", ["49-9021"]),
    ("carpenters", "Carpenters", ["47-2031"]),
    ("laborers", "Construction laborers", ["47-2061"]),
]
# Which Cook County schedule lines a role's work usually falls under. The public body or IDOL decides a worker's
# classification by the work done, not by job title; the page says so.
PREVAILING_MATCH = {
    "roofers": ["ROOFER"], "painters": ["PAINTER"], "electricians": ["ELECTRICIAN"], "plumbers": ["PLUMBER", "PIPEFITTER"],
    "hvac": ["SHEETMETAL WORKER", "PIPEFITTER"], "carpenters": ["CARPENTER"], "laborers": ["LABORER"],
    "landscapers": ["LABORER"],   # the schedule's own note: landscape laborers are covered by the laborer classification
}


def now_chicago():
    return dt.datetime.now(ZoneInfo("America/Chicago"))


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def plain_dashes(x):
    """Every em and en dash in every string becomes a plain hyphen (the repo's no-dash rule; check_repo em-dash)."""
    if isinstance(x, str):
        return x.replace("—", "-").replace("–", "-").replace("’", "'")
    if isinstance(x, list):
        return [plain_dashes(v) for v in x]
    if isinstance(x, dict):
        return {plain_dashes(k): plain_dashes(v) for k, v in x.items()}
    return x


def html_text(body):
    t = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", body)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def money(x):
    return float(str(x).replace("$", "").replace(",", ""))


# ---------------------------------------------------------------- BLS OEWS
def wage(v):
    """BLS cell: a number, '*' (wage not available), '#' (at or above $115.00 an hour), '**' (employment not available)."""
    if v is None or str(v).strip() in ("", "*", "**"):
        return None
    if str(v).strip() == "#":
        return "#"
    return round(float(v), 2)


def oews_rows(xlsx_bytes):
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes), read_only=True)
    it = wb.worksheets[0].iter_rows(values_only=True)
    head = [str(h).strip().upper() for h in next(it)]
    return [d for d in (dict(zip(head, r)) for r in it) if str(d.get("AREA")).split(".")[0] == MSA]


def oews_block(zip_path):
    z = zipfile.ZipFile(zip_path)
    name = next(n for n in z.namelist() if n.lower().endswith("msa_m2025_dl.xlsx"))
    rows = oews_rows(z.read(name))
    by = {r["OCC_CODE"]: r for r in rows if r.get("O_GROUP") in ("detailed", "total")}
    area = rows[0]["AREA_TITLE"]
    if area != "Chicago-Naperville-Elgin, IL-IN":
        raise SystemExit(f"oews: area {MSA} is {area!r}")

    def line(code):
        r = by[code]
        emp = r.get("TOT_EMP")
        return {"code": code, "title": r["OCC_TITLE"], "emp": None if str(emp).strip() in ("**", "*", "") else int(emp),
                **{k: wage(r.get(c)) for k, c in (("mean", "H_MEAN"), ("p10", "H_PCT10"), ("p25", "H_PCT25"), ("median", "H_MEDIAN"),
                                                   ("p75", "H_PCT75"), ("p90", "H_PCT90"))}}
    roles = []
    for key, label, codes in ROLES:
        roles.append({"key": key, "label": label, "lines": [line(c) for c in codes if c in by],
                      "notPublished": [c for c in codes if c not in by]})
    return {"period": "May 2025", "area": area, "areaCode": MSA, "url": URLS["oews"], "tablesUrl": URLS["oews_tables"],
            "file": name, "zipSha256": sha256(zip_path), "obtained": "Downloaded from bls.gov in a browser on Oct 27, 2026",
            "allOccupations": line("00-0000"), "roles": roles}


# ---------------------------------------------------------------- IDOL Cook County schedule
NUM = ["base", "foreman", "otMF", "otSa", "otSu", "otHol", "hw", "pension", "vac", "trng", "otherIns", "addOT15", "addOT20"]
HEAD = {"Rg": "region", "Type": "type", "C": "class", "Base": "base", "Foreman": "foreman", "M-F": "otMF", "Sa": "otSa",
        "Su": "otSu", "Hol": "otHol", "H/W": "hw", "Pension": "pension", "Vac": "vac", "Trng": "trng", "Ins": "otherIns"}
ISNUM = re.compile(r"^\d+(\.\d+)?$")
FRINGES = ["hw", "pension", "vac", "trng", "otherIns"]


def cook_rows(path):
    """Every row of the schedule, each cell put in the column whose header sits closest above it. Blank cells stay
    blank (None): the schedule lists nothing there."""
    import pdfplumber
    rows = []
    with pdfplumber.open(path) as pdf:
        ws0 = pdf.pages[0].extract_words()
        htop = next(w["top"] for w in ws0 if w["text"] == "Trade" and w["x0"] < 60)
        cen = {HEAD[w["text"]]: (w["x0"] + w["x1"]) / 2 for w in ws0 if abs(w["top"] - htop) < 3 and w["text"] in HEAD}
        adds = sorted([w for w in ws0 if w["text"] == "Add" and htop - 12 < w["top"] < htop], key=lambda w: w["x0"])
        cen["addOT15"], cen["addOT20"] = adds[0]["x0"] + 20, adds[1]["x0"] + 20
        for n, pg in enumerate(pdf.pages):
            ws = [w for w in pg.extract_words() if w["top"] > (htop + 6 if n == 0 else 40)]
            leg = [w["top"] for w in ws if w["text"] == "Legend" and w["x0"] < 60]
            if leg:
                ws = [w for w in ws if w["top"] < leg[0]]
            num_at = lambda t: any(abs(w["top"] - t) < 5 and ISNUM.match(w["text"]) and abs((w["x0"] + w["x1"]) / 2 - cen["base"]) < 18 for w in ws)
            anchors = sorted([w for w in ws if 150 < w["x0"] < 170 and num_at(w["top"])], key=lambda w: w["top"])
            for i, a in enumerate(anchors):
                lo = anchors[i - 1]["top"] + 5 if i else -1
                hi = anchors[i + 1]["top"] - 5 if i + 1 < len(anchors) else 1e9
                cells = {}
                for w in ws:
                    if w["x0"] > 150 and abs(w["top"] - a["top"]) < 5:
                        c = (w["x0"] + w["x1"]) / 2
                        k = min(cen, key=lambda k: abs(cen[k] - c))
                        cells[k] = (cells.get(k, "") + " " + w["text"]).strip()
                name = sorted([w for w in ws if w["x0"] < 150 and lo < w["top"] < hi and w["top"] > a["top"] - 12],
                              key=lambda w: (round(w["top"]), w["x0"]))
                r = {"trade": " ".join(w["text"] for w in name), "region": cells.get("region"), "type": cells.get("type"), "class": cells.get("class")}
                for k in NUM:
                    v = cells.get(k)
                    if v is not None and not ISNUM.match(v):
                        raise SystemExit(f"cook: page {n + 1}, {r['trade']}: {k} = {v!r}")
                    r[k] = float(v) if v is not None else None
                r["fringes"] = round(sum(r[k] or 0 for k in FRINGES), 2)
                r["total"] = round(r["base"] + r["fringes"], 2)
                rows.append(r)
            if leg:
                break
    return rows


def cook_block(path):
    from pypdf import PdfReader
    text = re.sub(r"\s+", " ", "\n".join(p.extract_text() or "" for p in PdfReader(path).pages))
    m = re.search(r"Cook County Prevailing Wage Rates posted on (\d{2})/(\d{2})/(\d{4})", text)
    if not m:
        raise SystemExit("cook: no 'posted on' line")
    ot = re.search(r"OT pay is required for any hour greater than (\d+) worked each day, Mon through Fri", text)
    land = [re.search(p_, text) for p_ in (r"Landscaping work falls under the existing classifications for laborer, operating engineer and truck driver\.",
                                           r"The work performed by landscape plantsman and landscape laborer is covered by the existing classification of laborer\.")]
    if not all(land):
        raise SystemExit("cook: landscaping note not found")
    rows = cook_rows(path)
    if len(rows) < 40 or not any(r["trade"] == "ELECTRICIAN" for r in rows):
        raise SystemExit(f"cook: only {len(rows)} rows read")
    return {"county": "Cook", "posted": f"{m.group(3)}-{m.group(1)}-{m.group(2)}", "postedLine": m.group(0), "pageUrl": URLS["idol"],
            "pdfSha256": sha256(path), "obtained": "Opened from the IDOL current rates page in a browser on Oct 27, 2026",
            "effective": "October 19, 2026", "otDailyAfter": int(ot.group(1)) if ot else None, "rows": rows, "match": PREVAILING_MATCH,
            "landscaping": [m.group(0) for m in land]}


# ---------------------------------------------------------------- City of Chicago notice
CHI_NEED = {
    "effective": r"Notice effective on (July 1, 2026)",
    "updated": r"Last updated (May 27, 2026)",
    "minWage": r"Min Wage \$(\d+\.\d\d) \$\d+\.\d\d",
    "tipped": r"Min Wage \$\d+\.\d\d \$(\d+\.\d\d)",
    "otMin": r"Overtime Min Wage \$(\d+\.\d\d) \$\d+\.\d\d",
    "otTipped": r"Overtime Min Wage \$\d+\.\d\d \$(\d+\.\d\d)",
    "employers": r"Standard Employer (4 or more employees)",
    "plAccrual": r"PL accrues at a rate of (1 hour of PL for every 35 hours worked \(up to 40 hours in a 12- ?month period\))",
    "pslAccrual": r"PSL accrues at a rate of (1 hour of PSL for every 35 hours worked \(up to 40 hours in a 12- ?month period\))",
    "eligible": r"Employers must provide Employees who (work at least 80 hours within any 120-day period)",
    "plUse": r"(use accrued PL no later than on the 90th day following the commencement of employment)",
    "pslUse": r"(use accrued PSL no later than on the 30th day following the commencement of employment)",
    "plCarry": r"(Up to 16 PL hours can be carried over between 12-month periods \(if PL is not frontloaded\))",
    "pslCarry": r"(Up to 80 PSL hours can be carried over between 12-month period)",
    "payout": r"(Employers with 51\+ employees must pay out up to 56 hours)",
    "smallExempt": r"(Small Employers \(1-50 employees\) are exempt)",
    "domesticYouth": r"(All Domestic Workers and Youth Workers must receive at least the \$\d+\.\d\d minimum wage)",
}


def chicago_block(path):
    from pypdf import PdfReader
    t = re.sub(r"\s+", " ", "\n".join(p.extract_text() or "" for p in PdfReader(path).pages))
    out = {}
    for k, pat in CHI_NEED.items():
        m = re.search(pat, t)
        if not m:
            raise SystemExit(f"chicago notice: {k} not found")
        out[k] = money(m.group(1)) if k in ("minWage", "tipped", "otMin", "otTipped") else re.sub(r"12- ?month", "12-month", m.group(1))
    out.update({"noticeUrl": URLS["chi_notice"], "pdfSha256": sha256(path), "pageUrl": URLS["chi_mw"], "olsUrl": URLS["chi_ols"],
                "obtained": "Downloaded from chicago.gov in a browser on Oct 27, 2026",
                "codes": "Chicago Municipal Code 6-105 (minimum wage) and 6-130 (paid leave and paid sick leave)"})
    return out


# ---------------------------------------------------------------- pages the workflow can reach (Cook County, IRS, City, IDOL)
PAGE_FIGURES = {
    "chi_mw": [("chicago.minWage", r"As of July 1, 2026, the minimum wage in Chicago is \$(\d+\.\d\d) per hour"),
               ("chicago.tipped", r"have a minimum wage of \$(\d+\.\d\d) for employers with 4 or more employees")],
    "cook_news": [("cook.minWage", r"minimum wage will increase to \$(\d+\.\d\d) for non-tipped workers"),
                  ("cook.tipped", r"for non-tipped workers and \$(\d+\.\d\d)\s+for tipped employees"),
                  ("cook.effective", r"Effective (July 1, 2026), the Cook County minimum wage"),
                  ("cook.employers", r"The employer has (four or more employees)")],
    "irs_p15": [("irs.year", r"Publication 15 \((\d{4})\), \(Circular E\)"),
                ("irs.ss", r"The rate of social security tax on taxable wages is (\d+\.\d+)% each for the employer and employee"),
                ("irs.medicare", r"The Medicare tax rate is (\d+\.\d+)% each for the employee and employer"),
                ("irs.ssBase", r"The social security wage base limit is \$([\d,]+)")],
    "idol": [("prevailing.effective", r"required to be paid for work performed on or after (\w+ \d{1,2}, \d{4})")],
}


def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:
        return -1, str(e).encode()[:200]


def read_figures(key, text):
    out = {}
    for fid, pat in PAGE_FIGURES[key]:
        m = re.search(pat, text)
        if m:
            out[fid] = {"value": m.group(1), "line": plain_dashes(m.group(0).strip())}
    return out


def pages_block(texts):
    f = {}
    for k, t in texts.items():
        f.update(read_figures(k, t))
    miss = [fid for k in ("cook_news", "irs_p15") for fid, _ in PAGE_FIGURES[k] if fid not in f]
    if miss:
        raise SystemExit(f"pages: not found {miss}")
    cook = {"minWage": money(f["cook.minWage"]["value"]), "tipped": money(f["cook.tipped"]["value"]), "effective": f["cook.effective"]["value"],
            "employers": f["cook.employers"]["value"], "posted": "June 1, 2026", "url": URLS["cook_news"],
            "covers": ("employees over 18 working in Cook County for an employer with four or more employees (or domestic workers) that has "
                       "a business facility or license in the County, in towns that have not opted out or set their own minimum wage")}
    irs = {"year": int(f["irs.year"]["value"]), "ss": float(f["irs.ss"]["value"]), "medicare": float(f["irs.medicare"]["value"]),
           "ssBase": int(money(f["irs.ssBase"]["value"])), "url": URLS["irs_p15"]}
    return cook, irs


def ingest(zip_path, cook_pdf, notice_pdf, pages_json):
    texts = json.load(open(pages_json))
    d = {"built": now_chicago().date().isoformat(), "oews": oews_block(zip_path), "prevailing": cook_block(cook_pdf),
         "chicago": chicago_block(notice_pdf)}
    d["cook"], d["irs"] = pages_block(texts)
    os.makedirs(OUTDIR, exist_ok=True)
    json.dump(plain_dashes(d), open(DATA, "w"), indent=1, ensure_ascii=False)
    print("ingest:", len(d["prevailing"]["rows"]), "Cook rows,", sum(len(r["lines"]) for r in d["oews"]["roles"]), "BLS lines")
    return d


def expected(d):
    """Each watched figure as its source writes it."""
    m = lambda x: f"{x:.2f}"
    return {"chicago.minWage": m(d["chicago"]["minWage"]), "chicago.tipped": m(d["chicago"]["tipped"]),
            "cook.minWage": m(d["cook"]["minWage"]), "cook.tipped": m(d["cook"]["tipped"]), "cook.effective": d["cook"]["effective"],
            "cook.employers": d["cook"]["employers"], "irs.year": str(d["irs"]["year"]), "irs.ss": str(d["irs"]["ss"]),
            "irs.medicare": str(d["irs"]["medicare"]), "irs.ssBase": f"{d['irs']['ssBase']:,}",
            "prevailing.effective": d["prevailing"]["effective"]}


def watch(raw=""):
    d = json.load(open(DATA))
    exp = expected(d)
    items = []
    for key in PAGE_FIGURES:
        st, body = get(URLS[key])
        text = html_text(body.decode("utf-8", "replace")) if st == 200 else ""
        if raw and st == 200:
            os.makedirs(raw, exist_ok=True)
            open(os.path.join(raw, key + ".html"), "wb").write(body)
        found = read_figures(key, text)
        for fid, _ in PAGE_FIGURES[key]:
            got = found.get(fid, {})
            items.append({"figure": fid, "source": URLS[key], "http": st, "expect": exp[fid], "found": got.get("value"),
                          "line": got.get("line"), "ok": got.get("value") == exp[fid]})
        time.sleep(1.5)
    w = {"checkedAt": now_chicago().isoformat(timespec="seconds"), "allOk": all(i["ok"] for i in items), "items": items}
    os.makedirs(OUTDIR, exist_ok=True)
    json.dump(plain_dashes(w), open(WATCH, "w"), indent=1, ensure_ascii=False)
    for i in items:
        print("PASS" if i["ok"] else "FAIL", i["figure"], "expect", i["expect"], "found", i["found"], "http", i["http"])
    return w


def selftest():
    assert plain_dashes({"a—": ["x–y", 1]}) == {"a-": ["x-y", 1]}
    assert wage("#") == "#" and wage("*") is None and wage(19.9) == 19.9 and wage("**") is None
    t = ("Publication 15 (2026), (Circular E), Employer's Tax Guide The rate of social security tax on taxable wages is 6.2% each "
         "for the employer and employee. The social security wage base limit is $184,500.The Medicare tax rate is 1.45% each for the "
         "employee and employer")
    f = read_figures("irs_p15", t)
    assert f["irs.ss"]["value"] == "6.2" and f["irs.medicare"]["value"] == "1.45" and f["irs.ssBase"]["value"] == "184,500" and f["irs.year"]["value"] == "2026"
    c = read_figures("cook_news", "Effective July 1, 2026, the Cook County minimum wage will increase to $15.40 for non-tipped workers and "
                                  "$9.25  for tipped employees. The employer has four or more employees (or")
    assert c["cook.minWage"]["value"] == "15.40" and c["cook.tipped"]["value"] == "9.25" and c["cook.employers"]["value"] == "four or more employees"
    assert read_figures("idol", "required to be paid for work performed on or after October 19, 2026 , on")["prevailing.effective"]["value"] == "October 19, 2026"
    assert read_figures("chi_mw", "As of July 1, 2026, the minimum wage in Chicago is $17.05 per hour for")["chicago.minWage"]["value"] == "17.05"
    print("dp_crew_cost_fetch selftest: ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--selftest"]:
        selftest()
    elif a[:1] == ["ingest"] and len(a) == 5:
        ingest(*a[1:])
    elif a[:1] == ["watch"]:
        w = watch(a[1] if len(a) > 1 else "")
        sys.exit(0 if w["allOk"] else 1)
    else:
        sys.exit(__doc__)
