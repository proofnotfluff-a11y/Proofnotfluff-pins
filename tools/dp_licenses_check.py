#!/usr/bin/env python3
"""Checks for the Chicago Trade License Finder's data (site/datapages/dp_licenses/licenses.json; tools/dp_licenses.py).

Default: validate the file. Every line names a source that exists; every source has a URL, title, agency and checked
date; every trade has City and State lines and a check-with agency; every figure a line lists appears in its own text;
the general contractor classes run from A (unlimited) down with rising limits; no em or en dash anywhere.

--fetch (the dp_licenses GitHub Action; the cloud shell cannot reach agency sites): re-read every source page and
confirm each line's figures still appear on it. Writes site/datapages/dp_licenses/check.json with, per source,
"ok", "changed" (a figure is missing: the line needs a fresh read) or "blocked" (the page refused the runner, which
proves nothing either way). Exit 1 when any source is "changed".

Usage: python3 tools/dp_licenses_check.py [--fetch] [--selftest] [--print URL]
"""
import datetime as dt, html, json, os, re, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "site", "datapages", "dp_licenses", "licenses.json")
REPORT = os.path.join(ROOT, "site", "datapages", "dp_licenses", "check.json")
TOPICS = {"city", "state", "fee", "insurance", "bond", "exam", "renewal", "carryover", "federal"}
DASH = re.compile("[–—]")
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def norm(s):
    """Page text and figures compared the same way: lower case, one space, $2,000.00 reads as $2,000, nbsp as space."""
    s = html.unescape(s).replace(" ", " ").lower()
    s = re.sub(r"(\$[\d,]+)\.00\b", r"\1", s)
    return re.sub(r"\s+", " ", s)


def validate(d):
    errs = []
    if DASH.search(json.dumps(d, ensure_ascii=False)):
        errs.append("an em or en dash in the data")
    if not ISO.match(d.get("checked", "")):
        errs.append("checked is not YYYY-MM-DD")
    for k, s in d.get("sources", {}).items():
        for f in ("url", "title", "agency"):
            if not s.get(f):
                errs.append(f"source {k}: no {f}")
        if not str(s.get("url", "")).startswith("https://"):
            errs.append(f"source {k}: url is not https")
        if s.get("checked") and not ISO.match(s["checked"]):
            errs.append(f"source {k}: checked is not YYYY-MM-DD")
    used = set()
    slugs = set()
    for t in d.get("trades", []):
        n = t.get("slug", "?")
        if n in slugs:
            errs.append(f"{n}: slug twice")
        slugs.add(n)
        for f in ("name", "h1", "title", "desc", "summary", "page_summary", "card", "glance", "check", "rows"):
            if not t.get(f):
                errs.append(f"{n}: no {f}")
        if len(t.get("desc", "")) >= 160 or len(t.get("title", "")) > 60:
            errs.append(f"{n}: description 160 characters or more, or title over 60")
        if not re.match(r"^[a-z]+(-[a-z]+)*$", n):
            errs.append(f"{n}: slug is not lower-case words")
        for c in t.get("check", []):
            if c not in d.get("sources", {}):
                errs.append(f"{n}: check-with source {c} missing")
        topics = {r.get("topic") for r in t.get("rows", [])}
        for need in ("city", "state"):
            if need not in topics:
                errs.append(f"{n}: no {need} line")
        for i, r in enumerate(t.get("rows", [])):
            if r.get("topic") not in TOPICS:
                errs.append(f"{n} row {i}: topic {r.get('topic')!r}")
            if r.get("src") not in d.get("sources", {}):
                errs.append(f"{n} row {i}: source {r.get('src')!r} missing")
            used.add(r.get("src"))
            if not r.get("text", "").strip().endswith("."):
                errs.append(f"{n} row {i}: text does not end with a period")
            for fig in r.get("figures", []):
                if norm(fig) not in norm(r.get("text", "")):
                    errs.append(f"{n} row {i}: figure {fig!r} not in its own text")
    for k in d.get("sources", {}):
        if k not in used and k not in {c for t in d.get("trades", []) for c in t.get("check", [])} and k != d.get("gc", {}).get("src"):
            errs.append(f"source {k}: never used")
    cl = d.get("gc_classes", [])
    if [c.get("class") for c in cl] != ["A", "B", "C", "D", "E"]:
        errs.append("gc_classes are not A to E")
    else:
        if cl[0]["max"] is not None:
            errs.append("class A is not unlimited")
        maxes = [c["max"] for c in cl[1:]]
        if maxes != sorted(maxes, reverse=True):
            errs.append("class limits do not fall from B to E")
        for c in cl:
            if c.get("demo") not in ("none", "ordinary", "complex"):
                errs.append(f"class {c['class']}: demo {c.get('demo')!r}")
            if not (isinstance(c.get("fee"), (int, float)) and isinstance(c.get("renewal"), (int, float))):
                errs.append(f"class {c['class']}: fee or renewal not a number")
    if d.get("gc", {}).get("src") not in d.get("sources", {}):
        errs.append("gc picker source missing")
    return errs


def fetch_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; ProofNotFluff license check; hello@proofnotfluff.com)",
                                               "Accept": "text/html,application/pdf;q=0.9,*/*;q=0.8"})
    with urllib.request.urlopen(req, timeout=40) as r:
        raw = r.read()
        ctype = r.headers.get("Content-Type", "")
    if "pdf" in ctype or url.lower().endswith(".pdf"):
        try:
            import io, pypdf
            return " ".join((pg.extract_text() or "") for pg in pypdf.PdfReader(io.BytesIO(raw)).pages)
        except Exception as e:   # no reader on the runner, or a scanned PDF: unproven, not changed
            raise OSError(f"pdf unreadable: {e}")
    t = raw.decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", t)
    return re.sub(r"<[^>]+>", " ", t)


def fetch_all(d, get=fetch_text):
    rep = {"checkedAt": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "dataChecked": d["checked"], "sources": {}}
    need = {}
    for t in d["trades"]:
        for r in t["rows"]:
            need.setdefault(r["src"], set()).update(r.get("figures", []))
    g = d["gc"]["src"]
    for c in d["gc_classes"]:
        need.setdefault(g, set()).update(c.get("figures", []))
    for k, s in sorted(d["sources"].items()):
        figs = sorted(need.get(k, set()))
        try:
            text = norm(get(s["url"]))
        except Exception as e:
            rep["sources"][k] = {"url": s["url"], "status": "blocked", "why": str(e)[:160], "figures": len(figs)}
            continue
        missing = [f for f in figs if norm(f) not in text]
        rep["sources"][k] = {"url": s["url"], "status": "changed" if missing else "ok", "figures": len(figs), "missing": missing}
    return rep


def selftest():
    d = json.load(open(DATA, encoding="utf-8"))
    assert validate(d) == [], validate(d)
    bad = json.loads(json.dumps(d))
    bad["trades"][0]["rows"][0]["src"] = "nope"
    bad["trades"][1]["rows"][0]["text"] += " —"
    bad["gc_classes"][2]["max"] = 99e9
    errs = validate(bad)
    assert any("nope" in e for e in errs) and any("dash" in e for e in errs) and any("limits" in e for e in errs), errs
    pages = {s["url"]: " ".join(r["text"] for t in d["trades"] for r in t["rows"] if r["src"] == k) + " "
             + " ".join(f for c in d["gc_classes"] for f in c.get("figures", [])) for k, s in d["sources"].items()}
    rep = fetch_all(d, get=lambda u: pages[u])
    assert all(v["status"] == "ok" for v in rep["sources"].values()), rep
    k0 = d["trades"][0]["rows"][0]["src"]
    rep = fetch_all(d, get=lambda u: "" if u == d["sources"][k0]["url"] else pages[u])
    assert rep["sources"][k0]["status"] in ("changed", "ok"), rep
    def boom(u):
        raise OSError("403")
    rep = fetch_all(d, get=boom)
    assert all(v["status"] == "blocked" for v in rep["sources"].values())
    print("dp_licenses_check selftest: ok")


def main():
    if "--selftest" in sys.argv:
        return selftest()
    if "--print" in sys.argv:   # read one page as text, for a line that needs a fresh read (the runner reaches what the cloud shell cannot)
        url = sys.argv[sys.argv.index("--print") + 1]
        try:
            print(re.sub(r"\s+", " ", html.unescape(fetch_text(url)))[:20000])
        except Exception as e:
            print("could not read", url, e)
        return
    d = json.load(open(DATA, encoding="utf-8"))
    errs = validate(d)
    for e in errs:
        print("ERROR dp_licenses:", e)
    if errs:
        sys.exit(1)
    n = sum(len(t["rows"]) for t in d["trades"])
    print(f"OK dp_licenses: {len(d['trades'])} trades, {n} lines, {len(d['sources'])} sources, checked {d['checked']}")
    if "--fetch" in sys.argv:
        rep = fetch_all(d)
        json.dump(rep, open(REPORT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        open(REPORT, "a").write("\n")
        cnt = {s: sum(1 for v in rep["sources"].values() if v["status"] == s) for s in ("ok", "changed", "blocked")}
        print(f"fetch: {cnt['ok']} ok, {cnt['changed']} changed, {cnt['blocked']} blocked of {len(rep['sources'])} sources")
        for k, v in rep["sources"].items():
            if v["status"] != "ok":
                print(f"  {v['status']} {k}: {v.get('missing') or v.get('why')}")
        if cnt["changed"]:
            sys.exit(1)


if __name__ == "__main__":
    main()
