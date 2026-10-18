#!/usr/bin/env python3
"""CMBS maturity probe (research only, Oct 17, 2026): can we rebuild a "loans maturing soon that may not refinance" list
from the free Reg AB II asset-level data (Form ABS-EE, Exhibit 102) that public CMBS trusts file each month on EDGAR?

Runs in GitHub Actions (.github/workflows/cmbs-probe.yml) because the cloud agents cannot reach sec.gov.
EDGAR fair access: a User-Agent naming us and a contact email, and well under 10 requests a second
(https://www.sec.gov/os/accessing-edgar-data). Nothing raw is kept: probes/cmbs-<date>.json holds counts, totals and a
short list of property-level rows (property name, city, state, type, balance, dates). The data has no borrower names,
and this script never adds one.
"""
import datetime as dt, gzip, io, json, os, re, sys, time, urllib.request
import xml.etree.ElementTree as ET

UA = "ProofNotFluff hello@proofnotfluff.com"
TODAY = dt.date.today()
END = dt.date(2027, 6, 30)
SINCE = TODAY - dt.timedelta(days=55)          # latest monthly filing per trust
CHI = {"COOK", "DUPAGE", "LAKE", "WILL", "KANE", "MCHENRY"}
RATE, YEARS, DSCR_MIN, LTV_MAX = 0.07, 30, 1.25, 0.65
r = RATE / 12
CONST = 12 * r / (1 - (1 + r) ** (-12 * YEARS))   # annual debt constant, about 0.0798
_last = [0.0]


def get(url, limit=None, tries=4):
    for a in range(tries):
        wait = 0.16 - (time.time() - _last[0])  # about 6 requests a second at most
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw = resp.read(limit) if limit else resp.read()
                if resp.headers.get("Content-Encoding") == "gzip" and not limit:
                    raw = gzip.decompress(raw)
                return raw
        except Exception as e:
            code = getattr(e, "code", None)
            if code in (403, 404) and a >= 1:
                raise
            time.sleep(2 * (a + 1) + (10 if code in (429, 503) else 0))
    raise RuntimeError("gave up: " + url)


def head(url):  # first bytes only, uncompressed, to read the namespace
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    wait = 0.16 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read(3000).decode("utf-8", "replace")


def num(v):
    try:
        return float(str(v).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def date(v):
    v = (v or "").strip()
    for f in ("%m-%d-%Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return dt.datetime.strptime(v[:10], f).date()
        except ValueError:
            pass
    return None


def local(t):
    return t.rsplit("}", 1)[-1]


def pick(d, *names):
    for n in names:
        v = d.get(n.lower())
        if v not in (None, ""):
            return v
    return None


def abs_ee_filings():
    rows = []
    q = (TODAY.month - 1) // 3 + 1
    quarters = [(TODAY.year, q)] + [((TODAY.year, q - 1) if q > 1 else (TODAY.year - 1, 4))]
    for y, qq in quarters:
        text = get(f"https://www.sec.gov/Archives/edgar/full-index/{y}/QTR{qq}/form.idx").decode("latin-1")
        for line in text.splitlines():
            if not line.startswith("ABS-EE "):
                continue
            parts = re.split(r"\s{2,}", line.strip())
            if len(parts) < 5:
                continue
            d = date(parts[-2])
            if d and d >= SINCE:
                rows.append((parts[-3], " ".join(parts[1:-3]), d, parts[-1].rsplit("/", 1)[-1].replace(".txt", "")))
    # one filing can be listed under the trust and its depositor; the trust is the filer with the fewest filings
    per_cik = {}
    for cik, name, d, acc in rows:
        per_cik.setdefault(cik, set()).add(acc)
    by_acc = {}
    for cik, name, d, acc in rows:
        cur = by_acc.get(acc)
        if cur is None or len(per_cik[cik]) < len(per_cik[cur[0]]):
            by_acc[acc] = (cik, name, d)
    seen = {}
    for acc, (cik, name, d) in by_acc.items():
        if cik not in seen or d > seen[cik][1]:
            seen[cik] = (name, d, acc)
    return seen


def main():
    out = {"ranAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "window": [TODAY.isoformat(), END.isoformat()],
           "rule": f"new loan = lower of {LTV_MAX:.0%} of latest valuation and NOI / ({DSCR_MIN} x {CONST:.5f}) "
                   f"({RATE:.0%}, {YEARS}-yr amortization); gap = estimated whole-loan balance minus new loan",
           "errors": []}
    try:
        filings = abs_ee_filings()
    except Exception as e:
        out["errors"].append("index: " + str(e)[:300])
        filings = {}
    out["absEeFilersSince"] = {"since": SINCE.isoformat(), "filers": len(filings)}
    tags, fill, trusts, loans = {}, {}, [], []
    nonc = {}
    for cik, (name, filed, acc) in sorted(filings.items(), key=lambda kv: kv[1][0]):
        base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}/"
        try:
            items = json.loads(get(base + "index.json"))["directory"]["item"]
        except Exception as e:
            out["errors"].append(f"{name}: index {str(e)[:120]}")
            continue
        xmls = [i for i in items if i["name"].lower().endswith(".xml") and "index" not in i["name"].lower()]
        xmls.sort(key=lambda i: ("102" not in i["name"], -int(i.get("size") or 0)))
        if not xmls:
            nonc["no_xml"] = nonc.get("no_xml", 0) + 1
            continue
        url = base + xmls[0]["name"]
        try:
            h = head(url)
        except Exception as e:
            out["errors"].append(f"{name}: head {str(e)[:120]}")
            continue
        m = re.search(r"absee/([a-z]+)/assetdata", h)
        kind = m.group(1) if m else "unknown"
        if kind != "cmbs":
            nonc[kind] = nonc.get(kind, 0) + 1
            continue
        try:
            raw = get(url)
        except Exception as e:
            out["errors"].append(f"{name}: xml {str(e)[:120]}")
            continue
        n_assets, period = 0, None
        for ev, el in ET.iterparse(io.BytesIO(raw), events=("end",)):
            if local(el.tag) != "assets":
                continue
            n_assets += 1
            d, props = {}, []
            for ch in el:
                t = local(ch.tag).lower()
                if t == "property":
                    p = {local(g.tag).lower(): (g.text or "").strip() for g in ch.iter() if g is not ch and len(g) == 0}
                    props.append(p)
                    for k, v in p.items():
                        tags[k] = tags.get(k, 0) + 1
                        if v:
                            fill[k] = fill.get(k, 0) + 1
                elif len(ch) == 0:
                    d[t] = (ch.text or "").strip()
                    tags[t] = tags.get(t, 0) + 1
                    if d[t]:
                        fill[t] = fill.get(t, 0) + 1
            el.clear()
            period = period or date(pick(d, "reportingPeriodEndDate"))
            loans.append((name, d, props))
        del raw
        trusts.append({"trust": name, "cik": cik, "filed": filed.isoformat(), "periodEnd": period.isoformat() if period else None,
                       "assets": n_assets})
        print(f"{len(trusts):4d} {name[:60]:60s} {n_assets}", flush=True)
    out["nonCmbsAbsEe"] = nonc
    out["errors"] = out["errors"][:60]
    out["trusts"] = {"count": len(trusts), "assetRows": sum(t["assets"] for t in trusts), "list": trusts}
    out["fieldsSeen"] = {k: [tags[k], fill.get(k, 0)] for k in sorted(tags)}
    analyse(out, loans)
    os.makedirs("probes", exist_ok=True)
    path = os.path.join("probes", f"cmbs-{TODAY.isoformat()}.json")
    s = json.dumps(out, separators=(",", ":"))
    if len(s) > 200_000:   # trim the row lists, never the counts
        for key in ("rowsNationalTopGap", "rowsIllinois"):
            while len(s) > 200_000 and out["results"].get(key):
                out["results"][key] = out["results"][key][: max(0, int(len(out["results"][key]) * 0.8))]
                s = json.dumps(out, separators=(",", ":"))
    open(path, "w").write(s)
    print(path, len(s))


def county(p):
    return re.sub(r"[^A-Z]", "", (pick(p, "propertyCounty") or "").upper()).replace("COUNTY", "")


def analyse(out, loans):
    res = {"activeLoanRows": 0}
    active = []
    for trust, d, props in loans:
        bal = num(pick(d, "reportPeriodEndActualBalanceAmount", "reportPeriodEndScheduledLoanBalanceAmount"))
        if not bal or bal <= 0:
            continue
        mat = date(pick(d, "maturityDate"))
        active.append((trust, d, props, bal, mat))
    res["activeLoanRows"] = len(active)
    # the same loan's notes sit in several trusts (pari passu splits); key on property and maturity to count loans once
    def key(d, props, mat):
        p = props[0] if props else {}
        return ((pick(p, "propertyName") or "").upper()[:40], (pick(p, "propertyCity") or "").upper(),
                (pick(p, "propertyState") or "").upper(), mat.isoformat() if mat else "")
    uniq = {}
    for a in active:
        uniq.setdefault(key(a[1], a[2], a[4]), []).append(a)
    res["activeDistinctLoans"] = len(uniq)
    res["activeBalance"] = round(sum(a[3] for a in active))
    res["maturityMissing"] = sum(1 for a in active if not a[4])
    res["pastMaturityStillOutstanding"] = {"rows": sum(1 for a in active if a[4] and a[4] < TODAY),
                                           "balance": round(sum(a[3] for a in active if a[4] and a[4] < TODAY))}
    win = [a for a in active if a[4] and TODAY <= a[4] <= END]
    by = lambda rows, f: sorted(((k, {"rows": len(v), "balance": round(sum(x[3] for x in v))}) for k, v in group(rows, f).items()))
    res["maturing"] = {"rows": len(win), "distinctLoans": len({key(a[1], a[2], a[4]) for a in win}),
                       "balance": round(sum(a[3] for a in win)),
                       "byMonth": dict(by(win, lambda a: a[4].strftime("%Y-%m"))),
                       "byType": dict(by(win, lambda a: ptype(a[2])))}
    il = [a for a in win if any((pick(p, "propertyState") or "").upper() == "IL" for p in a[2])]
    chi = [a for a in il if any((pick(p, "propertyState") or "").upper() == "IL" and county(p) in CHI for p in a[2])]
    for label, rows in (("illinois", il), ("chicagoMetro", chi)):
        res[label] = {"rows": len(rows), "distinctLoans": len({key(a[1], a[2], a[4]) for a in rows}),
                      "balance": round(sum(a[3] for a in rows)),
                      "byMonth": dict(by(rows, lambda a: a[4].strftime("%Y-%m"))), "byType": dict(by(rows, lambda a: ptype(a[2])))}
    res["illinoisAllActive"] = {"rows": sum(1 for a in active if any((pick(p, "propertyState") or "").upper() == "IL" for p in a[2]))}
    # refinance test, once per distinct loan in the window
    tests, rows = [], []
    for k, group_rows in {kk: v for kk, v in uniq.items() if v[0][4] and TODAY <= v[0][4] <= END}.items():
        t = refi(group_rows)
        tests.append(t)
        rows.append(t)
    gap = [t for t in tests if t["gap"] is not None and t["gap"] > 0]
    res["refi"] = {"tested": len(tests), "noData": sum(1 for t in tests if t["gap"] is None),
                   "gapCount": len(gap), "gapTotal": round(sum(t["gap"] for t in gap)),
                   "gapCountNoiOnly": sum(1 for t in tests if t["gapNoi"] is not None and t["gapNoi"] > 0),
                   "gapCountValueOnly": sum(1 for t in tests if t["gapVal"] is not None and t["gapVal"] > 0),
                   "gapBalanceAtRisk": round(sum(t["wholeLoan"] for t in gap)),
                   "valuationAgeYears": hist([t["valAge"] for t in tests if t["valAge"] is not None], (2, 5, 8)),
                   "valuationIsSecuritization": sum(1 for t in tests if t["valSrc"] == "securitization"),
                   "noiFromSecuritizationOnly": sum(1 for t in tests if t["noiSrc"] == "securitization"),
                   "splitLoans": sum(1 for t in tests if t["share"] < 0.95),
                   "specialServicedNow": sum(1 for t in tests if t["ss"]), "specialServicedWithGap": sum(1 for t in gap if t["ss"]),
                   "gapByType": dict(by([(None, None, None, t["gap"], None, t["type"]) for t in gap], lambda a: a[5]))}
    for g in res["refi"]["gapByType"].values():
        g.pop("balance", None)
    res["refi"]["gapByType"] = {k: {"loans": v["rows"], "gap": round(sum(t["gap"] for t in gap if t["type"] == k))}
                                for k, v in res["refi"]["gapByType"].items()}
    rows.sort(key=lambda t: -(t["gap"] or -1e18))
    res["rowColumns"] = list(SLIM)
    res["rowsNationalTopGap"] = [slim(t) for t in rows if t["gap"] and t["gap"] > 0][:260]
    res["rowsIllinois"] = [slim(t) for t in rows if t["state"] == "IL"]
    out["results"] = res


def group(rows, f):
    g = {}
    for a in rows:
        g.setdefault(f(a), []).append(a)
    return g


def hist(vals, cuts):
    h = {}
    for v in vals:
        lab = next((f"<{c}" for c in cuts if v < c), f">={cuts[-1]}")
        h[lab] = h.get(lab, 0) + 1
    return h


def ptype(props):
    ts = {(pick(p, "propertyTypeCode") or "NA").upper() for p in props} or {"NA"}
    return ts.pop() if len(ts) == 1 else "MULTI:" + "/".join(sorted(ts))[:20]


def refi(group_rows):
    trust, d, props, bal, mat = group_rows[0]
    note_sum = sum(a[3] for a in group_rows)
    p0 = props[0] if props else {}
    sumf = lambda f: sum(x for x in (num(pick(p, *f)) for p in props) if x) or None
    noi_now = sumf(("mostRecentNetOperatingIncomeAmount",))
    noi_sec = sumf(("netOperatingIncomeSecuritizationAmount",))
    val_now = sumf(("mostRecentValuationAmount",))
    val_sec = sumf(("valuationSecuritizationAmount",))
    vdate = date(pick(p0, "mostRecentValuationDate")) or date(pick(p0, "valuationSecuritizationDate"))
    noi, noi_src = (noi_now, "recent") if noi_now else (noi_sec, "securitization")
    val, val_src = (val_now, "recent") if val_now else (val_sec, "securitization")
    if val_now and val_sec and abs(val_now - val_sec) < 1 and vdate == date(pick(p0, "valuationSecuritizationDate")):
        val_src = "securitization"
    # whole-loan share: this trust's securitization P&I against whole-loan debt service implied by NOI / DSCR at securitization
    share = 1.0
    dscr_sec = num(pick(p0, "debtServiceCoverageNetOperatingIncomeSecuritizationPercentage"))
    pi = sum(num(pick(a[1], "periodicPrincipalAndInterestPaymentSecuritizationAmount")) or 0 for a in group_rows)
    freq = (pick(d, "paymentFrequencyCode") or "1").strip()
    mult = {"1": 12, "3": 4, "6": 2, "12": 1}.get(freq, 12)
    if dscr_sec and dscr_sec > 10:
        dscr_sec /= 100
    if noi_sec and dscr_sec and dscr_sec > 0.2 and pi:
        ds_whole = noi_sec / dscr_sec
        s = pi * mult / ds_whole
        if 0.02 < s < 1.0:
            share = s
    whole = note_sum / share
    new_val = LTV_MAX * val if val else None
    new_noi = noi / (DSCR_MIN * CONST) if noi and noi > 0 else (0.0 if noi is not None and noi <= 0 else None)
    caps = [c for c in (new_val, new_noi) if c is not None]
    ss_in = date(pick(d, "mostRecentSpecialServicerTransferDate"))
    ss_out = date(pick(d, "mostRecentMasterServicerReturnDate"))
    return {"name": (pick(p0, "propertyName") or "")[:60], "city": (pick(p0, "propertyCity") or "")[:30],
            "state": (pick(p0, "propertyState") or "").upper(), "county": county(p0).title(), "type": ptype(props),
            "props": len(props), "maturity": mat.isoformat(), "noteBal": round(note_sum), "trusts": len(group_rows),
            "share": round(share, 3), "wholeLoan": round(whole), "noi": round(noi) if noi else None, "noiSrc": noi_src,
            "val": round(val) if val else None, "valSrc": val_src, "valDate": vdate.isoformat() if vdate else None,
            "valAge": round((TODAY - vdate).days / 365.25, 1) if vdate else None,
            "dscrNow": num(pick(p0, "mostRecentDebtServiceCoverageNetOperatingIncomePercentage")),
            "occNow": num(pick(p0, "mostRecentPhysicalOccupancyPercentage")),
            "rate": num(pick(d, "reportPeriodInterestRatePercentage", "originalInterestRatePercentage")),
            "status": pick(d, "paymentStatusLoanCode"), "ss": bool(ss_in and (not ss_out or ss_out < ss_in)),
            "servicer": (pick(d, "primaryServicerName") or "")[:40], "originator": (pick(d, "originatorName") or "")[:40],
            "newLoan": round(min(caps)) if caps else None,
            "gap": round(whole - min(caps)) if caps else None,
            "gapNoi": round(whole - new_noi) if new_noi is not None else None,
            "gapVal": round(whole - new_val) if new_val is not None else None}


SLIM = ("name", "city", "state", "county", "type", "maturity", "wholeLoan", "noteBal", "share", "trusts", "noi", "noiSrc", "val",
        "valDate", "valSrc", "dscrNow", "occNow", "rate", "status", "ss", "servicer", "newLoan", "gap")


def slim(t):
    return [t[k] for k in SLIM]


if __name__ == "__main__":
    main()
