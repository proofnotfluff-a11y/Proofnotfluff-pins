#!/usr/bin/env python3
"""Prove a redesigned workbook does the same maths as the file it replaces.

Usage: python3 tools/compare_xlsx.py <old.xlsx> <new.xlsx> <map.json> [--report out.md]

map.json names the inputs and outputs in each file and the cases to try:
{
  "tolerance": 0.005,                      # absolute, for numbers (default 0.005)
  "inputs":  {"take_home":  {"old": "Calculator!C5",  "new": "Calculator!D15"},
              "tax_rate":   {"old": "Calculator!C6",  "new": "Calculator!D16", "new_scale": 1}},
  "outputs": {"min_rate":   {"old": "Calculator!F20", "new": "Calculator!I21"}},
  "cases": [
    {"name": "example"},                               # the files as shipped
    {"name": "high earner", "set": {"take_home": 120000, "tax_rate": 0.32}},
    {"name": "blank take-home", "set": {"take_home": null}}   # null clears the cell
  ]
}
A fix that changes an answer on purpose is declared, never hidden:
  "intended": [{"case": "rate below costs", "outputs": ["check_keep"], "why": "v1 taxed a loss"}]
Those rows print "intended" with the reason and do not fail the run.
"new_scale" multiplies the value written to the new file (use it when one file stores
25 for 25% and the other 0.25). An output may give "old_scale"/"new_scale" too.

Both files are opened in one headless LibreOffice, inputs are written as values,
everything is recalculated, and every output is compared. Error values count as a
value: both files must show the same error or neither. Exits 1 on any mismatch, and
prints a table you can paste into the build notes. Never changes either file.
"""
import argparse, json, os, shutil, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_xlsx import start_office, connect, props, LO_ERRORS  # noqa: E402


def cell(doc, ref):
    sheet, addr = ref.rsplit("!", 1)
    sheet = sheet.strip("'")
    if not doc.Sheets.hasByName(sheet):
        sys.exit(f"no sheet {sheet!r} (have {list(doc.Sheets.ElementNames)})")
    return doc.Sheets.getByName(sheet).getCellRangeByName(addr.replace("$", ""))


def read(c):
    if c.Type.value == "FORMULA" and c.getError():
        return "ERR " + LO_ERRORS.get(c.getError(), str(c.getError()))
    if c.Type.value == "EMPTY":
        return None
    if c.Type.value == "TEXT" or (c.Type.value == "FORMULA" and c.FormulaResultType2 == 2):  # text result
        return c.getString()
    return c.getValue()


def write(c, v):
    if v is None:
        c.setString(""); c.setFormula("")
    elif isinstance(v, str):
        c.setString(v)
    else:
        c.setValue(float(v))


def same(a, b, tol):
    if isinstance(a, float) and isinstance(b, float):
        return abs(a - b) <= tol
    if a in (None, "") and b in (None, "", 0.0) or b in (None, "") and a in (None, "", 0.0):
        return True
    return a == b


def show(v):
    if isinstance(v, float):
        return f"{v:,.4f}".rstrip("0").rstrip(".")
    return "(blank)" if v in (None, "") else str(v)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("old"); ap.add_argument("new"); ap.add_argument("map")
    ap.add_argument("--report", help="also write the table as markdown here")
    a = ap.parse_args()
    m = json.load(open(a.map))
    tol = float(m.get("tolerance", 0.005))
    cases = m.get("cases") or [{"name": "example"}]
    intended = {(i["case"], o): i.get("why", "") for i in m.get("intended", []) for o in i["outputs"]}

    import uno
    work = tempfile.mkdtemp(prefix="compare_xlsx_")
    profile = os.path.join(work, "profile"); os.makedirs(profile)
    proc, pipe = start_office(profile)
    lines, bad, planned = [], 0, 0
    try:
        ctx = connect(pipe)
        desk = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        docs = {}
        for side in ("old", "new"):
            p = os.path.join(work, side + ".xlsx"); shutil.copy(getattr(a, side), p)
            docs[side] = desk.loadComponentFromURL(uno.systemPathToFileUrl(p), "_blank", 0, props(Hidden=True))
            if docs[side] is None:
                sys.exit(f"LibreOffice could not open the {side} file")
        originals = {side: {k: (cell(docs[side], v[side]).getFormula()) for k, v in m["inputs"].items()} for side in docs}
        lines.append("| case | output | old | new | match |")
        lines.append("|---|---|---|---|---|")
        for case in cases:
            for side, doc in docs.items():  # reset to shipped inputs, then apply the case
                for k, f in originals[side].items():
                    cell(doc, m["inputs"][k][side]).setFormula(f)
                for k, v in (case.get("set") or {}).items():
                    if k not in m["inputs"]:
                        sys.exit(f"case {case['name']!r} sets unknown input {k!r}")
                    spec = m["inputs"][k]
                    val = v * spec.get(side + "_scale", 1) if isinstance(v, (int, float)) else v
                    write(cell(doc, spec[side]), val)
                doc.calculateAll()
            for k, spec in m["outputs"].items():
                vals = {}
                for side, doc in docs.items():
                    v = read(cell(doc, spec[side]))
                    if isinstance(v, float):
                        v = v / spec.get(side + "_scale", 1)
                    vals[side] = v
                ok = same(vals["old"], vals["new"], tol)
                why = intended.get((case["name"], k))
                if ok:
                    verdict = "yes"
                elif why is not None:
                    verdict = f"intended: {why}"; planned += 1
                else:
                    verdict = "NO"; bad += 1
                lines.append(f"| {case['name']} | {k} | {show(vals['old'])} | {show(vals['new'])} | {verdict} |")
        for doc in docs.values():
            doc.close(True)
    finally:
        try:
            proc.terminate(); proc.wait(timeout=15)
        except Exception:
            proc.kill()
        shutil.rmtree(work, ignore_errors=True)

    print("\n".join(lines))
    summary = f"{len(cases)} cases x {len(m['outputs'])} outputs: {'ALL MATCH' if not bad else f'{bad} MISMATCH'}"
    if planned:
        summary += f" ({planned} intended differences, listed above)"
    print(summary)
    if a.report:
        with open(a.report, "w") as fh:
            fh.write("\n".join(lines) + "\n\n" + summary + "\n")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
