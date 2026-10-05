# Rental Property Spreadsheet for 1 to 10 Doors (scoreboard idea small-landlord-rental-spreadsheet)

Cloud builder, Oct 5, 2026. Gate: round 1 FAIL (10 fixes applied), round 2 FAIL on one line (Setup tab claimed Log dropdowns reach row 5,000; LibreOffice clips them to row 1,005). That line is fixed in build_xlsx.py here but the fix has not been through the gate, so nothing was packed.

Rebuild (about 2 minutes):
1. python3 build_xlsx.py sample.xlsx && python3 build_xlsx.py blank.xlsx --blank (LICENSE-AND-DISCLAIMER.txt must sit next to the script)
2. soffice --headless --convert-to xlsx --outdir recalc sample.xlsx blank.xlsx  (ship recalc/sample.xlsx: it has cached values; check zero error cells in both)
3. python3 render.py  (writes pkg/START-HERE-Guide-Letter.pdf, -A4.pdf and img/01-05.png from recalc/sample.xlsx)
4. Copy recalc/sample.xlsx to pkg/Rental-Property-Spreadsheet-1-to-10-Doors.xlsx, add LICENSE-AND-DISCLAIMER.txt, set PDF Title/Author with pikepdf, zip, gate review, pack.

Sources checked Oct 5, 2026: IRS Schedule E 2025 (f1040se.pdf) Part I lines 3 to 19; Instructions for Schedule E line 14; IRS Pub 527 security deposits; Etsy Help "Downloading a Digital Item" (Etsy app can't download files).
