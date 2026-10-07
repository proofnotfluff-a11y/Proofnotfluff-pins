#!/usr/bin/env python3
"""Pack a finished workbook product into the zip buyers download, the same way every time.

Usage: python3 tools/pack_product.py <product.xlsx> <LICENSE-AND-DISCLAIMER.txt> <out_dir>
                                     [--tier low|medium|high] [--listing listing.md]
                                     [--extra other.xlsx ...] [--name Zip-Name]

Steps (each one fails loudly):
  1. Start Here PDFs: copies of the workbook set to US Letter and to A4, rendered with
     render_xlsx.py --print --keep-pdf; the Start Here sheet's PDF becomes
     Start-Here-Letter.pdf and Start-Here-A4.pdf. Every page also lands as PNG in
     <out_dir>/check/ so you can open and look at it.
  2. PDF metadata: Author, Creator and Producer "ProofNotFluff", Title from the file name.
  3. Ship folder <out_dir>/ship/ with the workbook, the two PDFs and the license file,
     zipped with zip -X into <out_dir>/<workbook name>.zip (must be under 10 MB).
  4. tools/legal_scan.py on the zip (any high finding fails the pack).
  5. <zip>.b64.txt for the scoreboard asset store, and the sha256 printed for the idea doc.
--extra adds more files to the zip as they are (for example a blank copy beside a filled-in
example workbook; each extra .xlsx must render with zero error values). --name sets the zip's
file name (default: the workbook's name). Both are optional; without them nothing changes.
The out_dir must be new or empty (no deleting inside the repo or anyone's folders).
"""
import argparse, hashlib, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(cmd, ok=(0,)):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode not in ok:
        sys.exit(f"failed: {' '.join(cmd)}\n{r.stdout}\n{r.stderr}")
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("xlsx"); ap.add_argument("license"); ap.add_argument("out")
    ap.add_argument("--tier", default="medium"); ap.add_argument("--listing")
    ap.add_argument("--extra", action="append", default=[]); ap.add_argument("--name")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    if os.path.exists(out) and os.listdir(out):
        sys.exit(f"{out} is not empty; use a new folder")
    os.makedirs(out, exist_ok=True)
    name = a.name or os.path.splitext(os.path.basename(a.xlsx))[0]

    import openpyxl
    from pypdf import PdfReader, PdfWriter
    pdfs = {}
    for label, size in (("Letter", 1), ("A4", 9)):
        wb = openpyxl.load_workbook(a.xlsx, rich_text=True)  # keep bold lead-ins and the colour strip
        if "Start Here" not in wb.sheetnames:
            sys.exit("the workbook has no 'Start Here' sheet")
        for ws in wb.worksheets:
            ws.page_setup.paperSize = size
        cp = os.path.join(out, f"paper-{label}.xlsx"); wb.save(cp)
        rdir = os.path.join(out, "check", label)
        r = run([sys.executable, os.path.join(HERE, "render_xlsx.py"), cp, rdir, "--print", "--keep-pdf"], ok=(0, 1))
        print(r.stdout.strip().splitlines()[-1])
        if "ERROR VALUES: 0" not in r.stdout:
            sys.exit(r.stdout)
        src = [p for p in os.listdir(rdir) if p.endswith(".pdf") and "Start-Here" in p]
        if len(src) != 1:
            sys.exit(f"could not find the Start Here PDF in {rdir}: {os.listdir(rdir)}")
        pdfs[label] = os.path.join(rdir, src[0])

    ship = os.path.join(out, "ship"); os.makedirs(ship)
    shutil.copy(a.xlsx, os.path.join(ship, os.path.basename(a.xlsx)))
    shutil.copy(a.license, os.path.join(ship, "LICENSE-AND-DISCLAIMER.txt"))
    for x in a.extra:
        if x.endswith(".xlsx"):
            r = run([sys.executable, os.path.join(HERE, "render_xlsx.py"), x, os.path.join(out, "check", "extra-" + os.path.basename(x))], ok=(0, 1))
            if "ERROR VALUES: 0" not in r.stdout:
                sys.exit(r.stdout)
        shutil.copy(x, os.path.join(ship, os.path.basename(x)))
    for label, p in pdfs.items():
        w = PdfWriter(clone_from=PdfReader(p))
        w.add_metadata({"/Author": "ProofNotFluff", "/Creator": "ProofNotFluff", "/Producer": "ProofNotFluff",
                        "/Title": f"{name.replace('-', ' ')}: Start Here ({label})"})
        with open(os.path.join(ship, f"Start-Here-{label}.pdf"), "wb") as fh:
            w.write(fh)

    z = os.path.join(out, name + ".zip")
    run(["zip", "-X", "-j", "-q", z] + sorted(os.path.join(ship, f) for f in os.listdir(ship)))
    mb = os.path.getsize(z) / 1e6
    if mb >= 10:
        sys.exit(f"zip is {mb:.1f} MB; Etsy's limit for us is 10 MB")
    scan = [sys.executable, os.path.join(HERE, "legal_scan.py"), z, "--tier", a.tier]
    if a.listing:
        scan += ["--listing", a.listing]
    r = run(scan, ok=(0, 1))
    print(r.stdout.strip())
    if r.returncode == 1:
        sys.exit("legal_scan found a high finding; fix it before shipping")
    sha = hashlib.sha256(open(z, "rb").read()).hexdigest()
    run(["bash", "-c", f"base64 -w0 '{z}' > '{z}.b64.txt'"])
    print(f"ZIP {z} ({mb:.2f} MB)\nSHA256 {sha}\nB64 {z}.b64.txt")


if __name__ == "__main__":
    main()
