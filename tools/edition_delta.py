#!/usr/bin/env python3
"""What a trade edition changes compared with its engine's main product, for the Legal desk's short review.

Usage: python3 tools/edition_delta.py <engine slug> <edition.json> [--license <edition LICENSE.txt>] [--packed <shelf xlsx>] [--out report.md]
  e.g. python3 tools/edition_delta.py service-pricing engines/service-pricing/editions/pressure-washing.json \
         --license engines/service-pricing/editions/pressure-washing.LICENSE.txt

It builds the engine's default workbook and the edition workbook fresh from the repo, compares every cell
of every sheet, and reports:
  - the ENGINE FINGERPRINT: sha256 over the engine build script, its LICENSE, tools/wb_style.py
    (notices and clauses) and legal/README.md. The Legal desk compares it with the fingerprint recorded at the
    engine's last full review (scoreboard legal/engine-<slug>). Different = the engine changed = full review.
  - STRUCTURE: sheets, formulas and data validations. Any formula that is not the same as the main
    product's is listed; "formulas changed" in the summary means the short review is not enough.
  - TEXT the edition changed (labels, hints, Start Here and Terms wording): every pair, old and new.
  - NUMBERS the edition changed (example inputs, presets, costs).
  - LICENSE lines that differ from the engine's (only the product name and version may differ).
  - with --packed: the shelf zip's workbook must equal a fresh build cell for cell, so what was reviewed is
    what ships.
Exit code 0 = short review allowed, 2 = full review needed (formulas, sheets or validations changed, the
LICENSE differs beyond name and version, or the packed workbook isn't the repo build), 1 = the tool failed.
"""
import argparse, hashlib, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def engine_files(slug):
    # what decides the maths and the legal text; tools/pnf_dash.py is layout only and changes often, so a
    # layout fix there doesn't force every edition back to a full review (formulas are compared cell by cell anyway)
    return [f"engines/{slug}/build_xlsx.py", f"engines/{slug}/LICENSE-AND-DISCLAIMER.txt",
            "tools/wb_style.py", "legal/README.md"]


def fingerprint(slug):
    h = hashlib.sha256()
    for rel in engine_files(slug):
        p = os.path.join(ROOT, rel)
        h.update(rel.encode() + b"\0")
        h.update(open(p, "rb").read() if os.path.exists(p) else b"<missing>")
    return h.hexdigest()[:16]


def build(slug, out, edition=None):
    cmd = [sys.executable, os.path.join(ROOT, f"engines/{slug}/build_xlsx.py"), out]
    if edition:
        cmd += ["--edition", edition]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(out):
        sys.exit(f"build failed ({' '.join(cmd)}):\n{r.stderr[-2000:]}")


def cells(path):
    import openpyxl
    wb = openpyxl.load_workbook(path)
    out, dv = {}, {}
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if c.value is not None:
                    out[(ws.title, c.coordinate)] = c.value
        dv[ws.title] = sorted((d.type or "", d.operator or "", str(d.formula1), str(d.formula2), str(d.sqref))
                              for d in ws.data_validations.dataValidation)
    return [ws.title for ws in wb.worksheets], out, dv


def is_formula(v):
    return isinstance(v, str) and v.startswith("=")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug"); ap.add_argument("edition")
    ap.add_argument("--license"); ap.add_argument("--out")
    ap.add_argument("--packed", help="the workbook from the shelf zip: must match a fresh build of the edition cell for cell")
    a = ap.parse_args()
    fp = fingerprint(a.slug)
    with tempfile.TemporaryDirectory() as tmp:
        base, ed = os.path.join(tmp, "base.xlsx"), os.path.join(tmp, "edition.xlsx")
        build(a.slug, base); build(a.slug, ed, a.edition)
        s0, c0, v0 = cells(base); s1, c1, v1 = cells(ed)
    full, lines = [], []
    if a.packed:
        sp, cp, vp = cells(a.packed)
        pdiff = [f"- {k[0]}!{k[1]}: build {c1.get(k)!r} / packed {cp.get(k)!r}" for k in sorted(set(c1) | set(cp)) if c1.get(k) != cp.get(k)]
        if sp != s1 or pdiff or vp != v1:
            full.append(f"the packed workbook differs from a fresh build of the edition ({len(pdiff)} cells)")
            lines.append("## Packed workbook vs fresh build (must be identical)\n" + "\n".join(pdiff[:100]) + "\n")
    lines.append(f"# Edition delta: {os.path.basename(a.edition)} vs engine {a.slug}\n")
    lines.append(f"ENGINE FINGERPRINT: {fp}\n")
    # sheets
    if s0 != s1:
        full.append("sheets differ"); lines.append(f"## Sheets differ\nmain: {s0}\nedition: {s1}\n")
    # formulas
    fdiff = []
    for k in sorted(set(c0) | set(c1)):
        a0, a1 = c0.get(k), c1.get(k)
        if (is_formula(a0) or is_formula(a1)) and a0 != a1:
            fdiff.append(f"- {k[0]}!{k[1]}: `{a0}` -> `{a1}`")
    if fdiff:
        full.append(f"{len(fdiff)} formulas changed")
        lines.append("## Formulas changed (full review needed)\n" + "\n".join(fdiff[:200]) + "\n")
    # validations
    vdiff = [t for t in sorted(set(v0) | set(v1)) if v0.get(t) != v1.get(t)]
    if vdiff:
        full.append("data validations changed")
        lines.append("## Data validations changed on: " + ", ".join(vdiff) + "\n")
    # text and numbers
    tdiff, ndiff = [], []
    for k in sorted(set(c0) | set(c1)):
        a0, a1 = c0.get(k), c1.get(k)
        if a0 == a1 or is_formula(a0) or is_formula(a1):
            continue
        row = f"- {k[0]}!{k[1]}: {a0!r} -> {a1!r}"
        (ndiff if isinstance(a0, (int, float)) or isinstance(a1, (int, float)) else tdiff).append(row)
    lines.append(f"## Text the edition changed ({len(tdiff)} cells; review every one)\n" + "\n".join(tdiff) + "\n")
    lines.append(f"## Numbers the edition changed ({len(ndiff)} cells: example, presets, costs)\n" + "\n".join(ndiff) + "\n")
    # license
    if a.license:
        eng = open(os.path.join(ROOT, f"engines/{a.slug}/LICENSE-AND-DISCLAIMER.txt"), encoding="utf-8").read().splitlines()
        edl = open(a.license, encoding="utf-8").read().splitlines()
        import difflib
        d = [l for l in difflib.unified_diff(eng, edl, "engine", "edition", lineterm="", n=0) if not l.startswith(("---", "+++", "@@"))]
        lines.append("## LICENSE lines that differ\n" + ("\n".join(d) if d else "(none)") + "\n")
        import json, re
        ed_name = json.load(open(a.edition, encoding="utf-8")).get("product", "")
        m = re.search(r'^PRODUCT\s*=\s*"([^"]+)"', open(os.path.join(ROOT, f"engines/{a.slug}/build_xlsx.py"), encoding="utf-8").read(), re.M)
        eng_name = m.group(1) if m else "\0"
        def allowed(l):  # a changed line may only carry the product name or the version
            body = l[1:]
            name = ed_name if l.startswith("+") else eng_name
            return re.search(r"\bVersion \d+", body) or (name and name in body)
        bad = [l for l in d if not allowed(l)]
        if bad:
            full.append(f"LICENSE changes more than the product name and version ({len(bad)} lines)")
    verdict = "FULL REVIEW NEEDED: " + "; ".join(full) if full else "SHORT REVIEW ALLOWED (formulas, sheets and validations identical to the main product)"
    lines.insert(2, f"VERDICT: {verdict}\n")
    report = "\n".join(lines)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(report)
    print(report if not a.out else f"{verdict}\nfingerprint {fp}\nreport: {a.out}")
    sys.exit(2 if full else 0)


if __name__ == "__main__":
    main()
