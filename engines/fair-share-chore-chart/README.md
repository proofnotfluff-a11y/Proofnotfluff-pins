# Fair Share Chore Chart (scoreboard idea fair-share-adult-chore-chart)

Cloud builder, Oct 5, 2026. Gate: round 1 FAIL (3 medium, 3 low), round 2 PASS. Packed on the shelf (zip sha256 fc6b4cf2...7fcb).

Rebuild (about 2 minutes):
1. python3 build_xlsx.py out/sample.xlsx, plus test variants: --names "Alex,Jordan,Sam", --names "", --names "Alex", --names "Alex,,Sam", --shares "60,40"
2. cd out && soffice --headless --convert-to xlsx --outdir recalc *.xlsx (ship recalc/sample.xlsx; zero error cells in every variant)
3. python3 render.py (guide PDFs Letter and A4 into pkg/, five 2000x2000 images into img/; reads out/recalc sample, three, shares)
4. Copy recalc/sample.xlsx to pkg/Fair-Share-Chore-Chart.xlsx, add LICENSE-AND-DISCLAIMER.txt, set PDF metadata to ProofNotFluff with pikepdf, zip the 4 files.

How it works: Math tab ranks chores (pinned and rotating "Nobody wants it" jobs first, then by weighted minutes), and for each of 4 pattern weeks assigns each job to the person with the lowest load divided by share (greedy, biggest first). Rotating jobs move by MOD(rank, people) each week. The Printable Chart is one portrait list grouped by person (LibreOffice ignores dynamic print areas, so no multi-column layout).

Sources checked Oct 5, 2026: BLS ATUS 2025 results (bls.gov/news.release/atus.nr0.htm, released June 25, 2026); Etsy Help "Downloading a Digital Item".
