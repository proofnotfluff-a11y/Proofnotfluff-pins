#!/usr/bin/env python3
"""Holdout check for the free calculator pages (live session Oct 17, 2026, from Kem's holdout tests).

Usage:  python3 tools/holdout_check.py cases.json
        python3 tools/holdout_check.py --selftest

The page's own tests (docs/assets/pnf-calc.test.js) are written by the builder from its workbook,
so a builder that misreads a source passes its own tests. Holdout cases close that gap: someone who
did not build the page works them out by hand from the page's method lines and the dated primary
sources (never from pnf-calc.js, its tests, the engine or the workbook), keeps them outside the repo
so the builder never sees them, and runs them at the end. This tool is the deterministic half: it
types each case into the page the way a visitor would, reads what the page shows and compares.

cases.json:
  {"page": "docs/<slug>/index.html",          (or "url": "https://proofnotfluff.com/<slug>/")
   "cases": [
     {"name": "PO due in week 9, never recovers",
      "set": {"openingCash": 15000, "poWeek": 9},          inputs and selects, by data-in name
      "expect": {"lowest": -99500, "lowWeek": 13,          numbers as shown (a percent as 12.5)
                 "statusText": "~order now"},              "~text": shown text contains it, any case
      "tol": {"lowest": 1}}]}                              optional; default is half the shown step

Exit 0 when every expectation passes, 1 on any FAIL, 2 when the file or the page is unusable.
"""
import json, os, re, sys, tempfile

# Half of the smallest step each display format can show (pnf-calc.js wire() and after()).
STEP_TOL = {"money": 0.005, "money0": 0.5, "money3": 0.0005, "int": 0.5, "week": 0.5,
            "dec1": 0.05, "hrs": 0.005, "mult": 0.005, "pct": 0.05}


def shown_number(text):
    """'-$1,234.50' -> -1234.5, 'Week 13' -> 13, '12.5%' -> 12.5, '1.25x' -> 1.25; None if no number."""
    t = text.replace("−", "-").replace(",", "")
    m = re.search(r"(-)?\$?\s*(-)?(\d+(?:\.\d+)?)", t)
    if not m:
        return None
    v = float(m.group(3))
    return -v if (m.group(1) or m.group(2)) else v


def load_page(page, target):
    if re.match(r"https?://", target):
        page.goto(target, wait_until="load")
    else:
        page.goto("file://" + os.path.abspath(target), wait_until="load")
    page.wait_for_selector("[data-in]", state="attached", timeout=10000)


def set_inputs(page, values):
    for key, val in values.items():
        el = page.query_selector(f'[data-in="{key}"]')
        if el is None:
            raise LookupError(f'no input with data-in="{key}"')
        if el.evaluate("e => e.tagName") == "SELECT":
            try:
                el.select_option(value=str(val))
            except Exception:
                el.select_option(label=str(val))
        else:
            el.fill(str(val))
            el.dispatch_event("input")
    page.wait_for_timeout(60)


def read_output(page, key):
    """Returns (shown text, display format) for data-out="key", else data-pct="key"."""
    el = page.query_selector(f'[data-out="{key}"]')
    fmt = None
    if el is not None:
        fmt = el.get_attribute("data-fmt") or "money"
    else:
        el = page.query_selector(f'[data-pct="{key}"]')
        fmt = "pct" if el is not None else None
    if el is None:
        raise LookupError(f'no output with data-out or data-pct "{key}"')
    return (el.text_content() or "").strip(), fmt


def check_case(page, target, case):
    """One case on a freshly loaded page. Returns a list of (ok, line)."""
    load_page(page, target)
    set_inputs(page, case.get("set", {}))
    tols = case.get("tol", {})
    lines = []
    for key, want in case.get("expect", {}).items():
        shown, fmt = read_output(page, key)
        if isinstance(want, str):
            if want.startswith("~"):
                ok = want[1:].lower() in shown.lower()
            else:
                ok = shown == want
            lines.append((ok, f"{key}: shows {shown!r}, expected {want!r}"))
            continue
        got = shown_number(shown)
        tol = float(tols.get(key, STEP_TOL.get(fmt, 0.005))) + 1e-9
        ok = got is not None and abs(got - float(want)) <= tol
        lines.append((ok, f"{key}: shows {shown!r}, expected {want} (within {tol:g})"))
    return lines


def run(spec):
    from playwright.sync_api import sync_playwright
    target = spec.get("url") or spec.get("page")
    if not target or not spec.get("cases"):
        print("cases file needs a page (or url) and at least one case")
        return 2
    fails = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 390, "height": 844})
        for case in spec["cases"]:
            try:
                lines = check_case(page, target, case)
            except Exception as e:  # a missing field or a page that does not load is a FAIL, not a pass
                lines = [(False, f"could not run: {e}")]
            for ok, line in lines:
                fails += 0 if ok else 1
                print(f"{'ok  ' if ok else 'FAIL'} {case.get('name', 'case')}: {line}")
        browser.close()
    print(f"{fails} failed" if fails else "all holdout cases pass")
    return 1 if fails else 0


SELFTEST_PAGE = """<!doctype html><meta charset="utf-8"><form id="calc">
<input data-in="units" value="2"><select data-in="mode"><option value="1">one</option><option value="3">three</option></select>
</form><b data-out="total" data-fmt="money0"></b><b data-out="each"></b><b data-out="status" data-fmt="text"></b>
<b data-pct="share"></b><b data-out="weeks" data-fmt="week"></b>
<script>
var f = document.getElementById("calc");
function go() {
  var u = +f.querySelector('[data-in="units"]').value, m = +f.querySelector('[data-in="mode"]').value;
  var t = u * m * 1234.4;
  document.querySelector('[data-out="total"]').textContent = (t < 0 ? "-$" : "$") + Math.round(Math.abs(t)).toLocaleString("en-US");
  document.querySelector('[data-out="each"]').textContent = "$" + (t / 7).toFixed(2);
  document.querySelector('[data-out="status"]').textContent = t > 5000 ? "Order now" : "OK";
  document.querySelector('[data-pct]').textContent = (m / 8 * 100).toFixed(1) + "%";
  document.querySelector('[data-out="weeks"]').textContent = "Week " + (u + m);
}
f.addEventListener("input", go); f.querySelector("select").addEventListener("change", go); go();
</script>"""


def selftest():
    """The checker must pass a right answer and fail a planted wrong one (a checker that cannot fail proves nothing)."""
    with tempfile.TemporaryDirectory() as d:
        page = os.path.join(d, "index.html")
        open(page, "w", encoding="utf-8").write(SELFTEST_PAGE)
        right = {"page": page, "cases": [{"name": "right", "set": {"units": "-3", "mode": "3"},
                 "expect": {"total": -11110, "each": -1587.09, "status": "~ok", "share": 37.5, "weeks": 0}}]}
        wrong = {"page": page, "cases": [{"name": "planted", "set": {"units": "5", "mode": "1"},
                 "expect": {"total": 6200, "status": "~order now"}}]}
        missing = {"page": page, "cases": [{"name": "missing field", "set": {"nope": 1}, "expect": {"total": 0}}]}
        print("-- right answers (must pass)")
        a = run(right)
        print("-- planted wrong total (must fail)")
        b = run(wrong)
        print("-- missing input (must fail)")
        c = run(missing)
    ok = a == 0 and b == 1 and c == 1
    print("selftest PASS" if ok else f"selftest FAIL (exits {a}, {b}, {c}; wanted 0, 1, 1)")
    return 0 if ok else 1


def main(argv):
    if len(argv) == 2 and argv[1] == "--selftest":
        return selftest()
    if len(argv) != 2:
        print(__doc__)
        return 2
    try:
        spec = json.load(open(argv[1], encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"cannot read {argv[1]}: {e}")
        return 2
    return run(spec)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
