#!/usr/bin/env python3
"""Render a workbook the way a buyer sees it, and report error cells.

Usage: python3 tools/render_xlsx.py <file.xlsx> <out_dir> [--dpi 110] [--print] [--keep-pdf]

What it does, with LibreOffice headless (soffice must be on PATH, python3-uno installed):
  1. opens the workbook, recalculates every formula (calculateAll), and saves the
     recalculated copy as <out_dir>/recalc.xlsx so the cached values are real;
  2. walks every cell on every visible sheet and lists error values
     (#DIV/0!, #REF!, #NAME?, #VALUE!, #N/A, #NUM!, circular references);
  3. exports every visible sheet to its own PNG: <out_dir>/NN-<sheet>.png.
     Default: one image per sheet, the whole sheet on one page (what the buyer sees on
     screen). With --print: the sheet is paged by its own print setup, one PNG per page
     (NN-<sheet>-pP.png), which is what the buyer gets from File, Print.

Prints a short report and exits 1 when any error value is found or a sheet could
not be rendered. This is the design gate's eyes: open every PNG with the Read tool
and look at it. The tool never changes the input file.
"""
import argparse, glob, os, re, shutil, subprocess, sys, tempfile, time, uuid

# LibreOffice error codes (FormulaError) to the Excel names buyers would see.
LO_ERRORS = {
    501: "#VALUE! (invalid character)", 502: "#VALUE! (invalid argument)", 503: "#NUM!",
    504: "#VALUE! (parameter list)", 507: "#VALUE! (missing bracket)", 508: "#VALUE! (bracket)",
    509: "#NAME? (missing operator)", 510: "#VALUE! (missing variable)", 511: "#VALUE! (missing variable)",
    512: "#VALUE! (formula overflow)", 513: "#VALUE! (string overflow)", 514: "#VALUE! (overflow)",
    516: "#VALUE! (internal)", 517: "#VALUE! (internal)", 518: "#VALUE! (internal)",
    519: "#VALUE!", 520: "#VALUE! (internal)", 521: "#VALUE! (internal)", 522: "circular reference",
    523: "no convergence", 524: "#REF!", 525: "#NAME?", 526: "#VALUE! (internal)",
    527: "#VALUE! (internal)", 532: "#DIV/0!", 533: "#N/A (nested array)", 538: "#N/A (array)",
    539: "#VALUE! (unsupported)", 540: "#VALUE! (external access)", 32767: "#N/A",
}
ERROR_RE = re.compile(r"^#(DIV/0!|REF!|NAME\?|VALUE!|N/A|NUM!|NULL!)$|^Err:\d+$")


def sh_run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def find_soffice():
    for name in ("soffice", "libreoffice"):
        p = shutil.which(name)
        if p:
            return p
    sys.exit("soffice not found. Install LibreOffice (apt-get install -y libreoffice-calc python3-uno).")


def start_office(profile_dir):
    """Start a private headless LibreOffice and return (process, pipe name)."""
    import uno  # noqa: F401  (fail early with a clear message)
    pipe = "pnf_" + uuid.uuid4().hex[:10]
    cmd = [find_soffice(), "--headless", "--invisible", "--nologo", "--norestore", "--nolockcheck",
           f"-env:UserInstallation=file://{profile_dir}",
           f"--accept=pipe,name={pipe};urp;StarOffice.ComponentContext"]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc, pipe


def connect(pipe, timeout=60):
    import uno
    from com.sun.star.connection import NoConnectException
    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
    deadline = time.time() + timeout
    while True:
        try:
            return resolver.resolve(f"uno:pipe,name={pipe};urp;StarOffice.ComponentContext")
        except NoConnectException:
            if time.time() > deadline:
                sys.exit("could not connect to LibreOffice within %ss" % timeout)
            time.sleep(0.5)


def props(**kw):
    from com.sun.star.beans import PropertyValue
    out = []
    for k, v in kw.items():
        p = PropertyValue(); p.Name = k; p.Value = v; out.append(p)
    return tuple(out)


def filter_data(**kw):
    import uno
    from com.sun.star.beans import PropertyValue
    items = []
    for k, v in kw.items():
        p = PropertyValue(); p.Name = k; p.Value = v; items.append(p)
    return uno.Any("[]com.sun.star.beans.PropertyValue", tuple(items))


def safe_name(s):
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")
    return s or "sheet"


def scan_errors(doc):
    """Return [(sheet, address, formula, error_name)] for every error cell on visible sheets."""
    found = []
    sheets = doc.Sheets
    for i in range(sheets.Count):
        sheet = sheets.getByIndex(i)
        if not sheet.IsVisible:
            continue
        cur = sheet.createCursor(); cur.gotoEndOfUsedArea(False)
        end = cur.RangeAddress
        rng = sheet.getCellRangeByPosition(0, 0, end.EndColumn, end.EndRow)
        data = rng.DataArray  # values only, fast
        for r, row in enumerate(data):
            for c, _ in enumerate(row):
                cell = sheet.getCellByPosition(c, r)
                if cell.Type.value != "FORMULA":
                    continue
                code = cell.getError()
                shown = cell.getString()
                if code or ERROR_RE.match(shown):
                    name = LO_ERRORS.get(code, shown or f"Err:{code}")
                    found.append((sheet.Name, cell.AbsoluteName.split(".")[-1].replace("$", ""), cell.Formula, name))
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("xlsx"); ap.add_argument("out_dir")
    ap.add_argument("--dpi", type=int, default=110, help="PNG resolution (default 110)")
    ap.add_argument("--print", dest="paged", action="store_true", help="page each sheet by its print setup instead of one image per sheet")
    ap.add_argument("--keep-pdf", action="store_true", help="keep the per-sheet PDFs next to the PNGs")
    a = ap.parse_args()

    src = os.path.abspath(a.xlsx)
    if not os.path.isfile(src):
        sys.exit(f"not found: {src}")
    if not shutil.which("pdftoppm"):
        sys.exit("pdftoppm not found (apt-get install -y poppler-utils)")
    out = os.path.abspath(a.out_dir); os.makedirs(out, exist_ok=True)
    for old in glob.glob(os.path.join(out, "*.png")) + glob.glob(os.path.join(out, "*.pdf")):
        os.remove(old)

    import uno
    work = tempfile.mkdtemp(prefix="render_xlsx_")
    profile = os.path.join(work, "profile"); os.makedirs(profile)
    local_copy = os.path.join(work, "input.xlsx"); shutil.copy(src, local_copy)
    proc, pipe = start_office(profile)
    status = 0
    try:
        ctx = connect(pipe)
        desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        doc = desktop.loadComponentFromURL(uno.systemPathToFileUrl(local_copy), "_blank", 0, props(Hidden=True))
        if doc is None:
            sys.exit("LibreOffice could not open the file")
        doc.calculateAll()

        # 1. recalculated copy with real cached values
        recalc = os.path.join(out, "recalc.xlsx")
        doc.storeToURL(uno.systemPathToFileUrl(recalc), props(FilterName="Calc MS Excel 2007 XML", Overwrite=True))

        # 2. error cells
        errors = scan_errors(doc)

        # 3. PNGs per sheet
        sheets = doc.Sheets
        names = [sheets.getByIndex(i).Name for i in range(sheets.Count)]
        visible = [n for n in names if sheets.getByName(n).IsVisible]
        hidden = [n for n in names if n not in visible]
        rendered = []
        pdfs = []
        if not a.paged:
            # SinglePageSheets puts every sheet (hidden ones too) on exactly one page, in sheet order.
            pdf = os.path.join(work, "whole.pdf")
            doc.storeToURL(uno.systemPathToFileUrl(pdf), props(FilterName="calc_pdf_Export", Overwrite=True,
                                                               FilterData=filter_data(SinglePageSheets=True)))
            r = sh_run(["pdftoppm", "-png", "-r", str(a.dpi), pdf, os.path.join(work, "page")])
            if r.returncode:
                print(f"render failed: {r.stderr.strip()}"); status = 1
            pages = sorted(glob.glob(os.path.join(work, "page-*.png")), key=lambda p: int(re.search(r"-(\d+)\.png$", p).group(1)))
            if len(pages) != len(names):
                print(f"warning: {len(pages)} pages for {len(names)} sheets; mapping by order"); status = 1
            n = 0
            for name, page in zip(names, pages):
                if name in hidden:
                    continue
                n += 1
                base = f"{n:02d}-{safe_name(name)}"
                shutil.move(page, os.path.join(out, base + ".png"))
                rendered.append((name, 1))
            if a.keep_pdf:
                shutil.copy(pdf, os.path.join(out, "all-sheets.pdf"))
        else:
            # Paged export: isolate each sheet by pointing every other sheet's print range at one
            # empty far-away cell (LibreOffice skips empty pages) and hiding it. Hiding alone is not
            # enough once print areas are defined, so both are done, then restored.
            from com.sun.star.table import CellRangeAddress
            saved = {nm: sheets.getByName(nm).getPrintAreas() for nm in names}
            for n, name in enumerate(visible, 1):
                sheets.getByName(name).IsVisible = True  # first, or LibreOffice refuses to hide the last visible sheet
                for other in names:
                    if other == name:
                        sheets.getByName(other).setPrintAreas(saved[other])
                        continue
                    sh = sheets.getByName(other)
                    far = CellRangeAddress(); far.Sheet = sh.RangeAddress.Sheet
                    far.StartColumn = far.EndColumn = 200; far.StartRow = far.EndRow = 5000
                    sh.setPrintAreas((far,))
                    sh.IsVisible = False
                base = f"{n:02d}-{safe_name(name)}"
                pdf = os.path.join(out, base + ".pdf")
                doc.storeToURL(uno.systemPathToFileUrl(pdf), props(FilterName="calc_pdf_Export", Overwrite=True))
                r = sh_run(["pdftoppm", "-png", "-r", str(a.dpi), pdf, os.path.join(out, base)])
                if r.returncode:
                    print(f"render failed for sheet {name!r}: {r.stderr.strip()}"); status = 1
                pages = sorted(glob.glob(os.path.join(out, base + "-*.png")))
                if len(pages) == 1:
                    os.replace(pages[0], os.path.join(out, base + ".png")); pages = [os.path.join(out, base + ".png")]
                else:
                    for p in pages:  # pdftoppm pads page numbers; normalise to -p1, -p2
                        num = int(re.search(r"-(\d+)\.png$", p).group(1))
                        os.replace(p, os.path.join(out, f"{base}-p{num}.png"))
                    pages = sorted(glob.glob(os.path.join(out, base + "-p*.png")))
                if not a.keep_pdf:
                    os.remove(pdf)
                rendered.append((name, len(pages)))
            for other in names:
                sheets.getByName(other).setPrintAreas(saved[other])
                sheets.getByName(other).IsVisible = other in visible
        doc.close(True)
    finally:
        try:
            proc.terminate(); proc.wait(timeout=15)
        except Exception:
            proc.kill()
        shutil.rmtree(work, ignore_errors=True)

    print(f"Rendered {os.path.basename(src)} into {out}")
    for name, pages in rendered:
        print(f"  sheet {name!r}: {pages} image{'s' if pages != 1 else ''}")
    if hidden:
        print(f"  hidden sheets not rendered: {hidden}")
    print(f"  recalculated copy: {recalc}")
    if errors:
        status = 1
        print(f"ERROR VALUES: {len(errors)}")
        for sheet, addr, formula, name in errors:
            print(f"  {sheet}!{addr}: {name}  {formula}")
    else:
        print("ERROR VALUES: 0")
    sys.exit(status)


if __name__ == "__main__":
    main()
