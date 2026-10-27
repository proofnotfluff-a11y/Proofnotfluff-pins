# Launch record: Chicago Public Way Permit Cost Calculator (B6 item 1), LIVE Oct 27, 2026

Decided: the owner, Oct 27, 12:17 pm ("Let's do them all", coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md), research_notes/kimi-2026-10-27-r10.md item 6. The owner's rule for this page: build only from the City's own CDOT 2026 Permit Fee Schedule PDF, never from other sites' numbers.

## Source
- Oct 27: the GitHub runner could not download https://www.chicago.gov/content/dam/city/depts/cdot/permit/2026/CDOT%202026%20Permit%20Fee%20Schedule.pdf (two runs; stopped as the owner asked, no other routes). The owner downloaded it in his own browser and attached it in the build chat.
- `python3 tools/dp_cdot_fees_pull.py --from-file <pdf>` extracted the text to site/datapages/dp_cdot_fees/ (fee-schedule.layout.txt, fee-schedule.raw.txt, source.json with the PDF's sha256 009061e5...d9b7). The PDF itself is never committed: its metadata names a City employee. Em and en dashes in the text are plain hyphens (site no-dash rule).
- The degradation fee box on schedule page 11 is an image, so it is typed into degradation-page11.json and was checked by eye against the page.
- .github/workflows/dp_cdot_fees.yml runs only by hand. For a new schedule: the owner downloads the new PDF, a build chat runs the pull tool with --from-file, and `python3 tools/dp_cdot_fees.py --selftest` fails until every fee in the module matches the new text.

## How it works
- tools/dp_cdot_fees.py: fees typed from the text, with a selftest that finds each row in the City's text and checks its amounts in order (planted wrong fees are caught). The calculator runs in the visitor's browser: dumpster, work vehicle or equipment, sidewalk or street closure (Types I, II, III, 30-day blocks, one-half outside the CBD), opening or cut (moratorium doubling and per-cut degradation fee). Readings of the schedule are labeled on the page.
- The dumpster permits page links here once this page is live, and this page links back.

## Gates
- Facts: round 1 FAIL (unlabeled readings, a caption error, the owner's name in files), round 2 FAIL 16 of 18, round 3 FAIL 11 of 14 (method and FAQ wording), round 4 PASS 14 of 14: 194 table cells match the PDF images, 11 of 11 flow totals and 11 of 11 hand-worked cases match.
- Design director: round 1 FAIL 3.79, round 2 FAIL 4.36, round 3 PASS 4.64 (no score under 4); its polish applied after.
- Legal desk: round 1 NOT CLEARED (City disclaimer missing), round 2 NOT CLEARED (wording), round 3 NOT CLEARED (one uncredited rule), round 4 CLEARED. Open as on every Chicago page: the City's indemnity clause, for the owner's attorney.
- Copy: round 1 FAIL 4.40, round 2 PASS 4.60.
- verify_site: PASS at 390 and 1280, light and dark, axe 0; flow 27 of 27 steps. check_repo 0 errors on the live push.

## For the wrap-up
- Suggested backstop (not done here, shared file): a .gitignore line for site/datapages/dp_cdot_fees/*.pdf.
- The Open Graph image subtitle is cut off at "from the City's fee" (shared OG generator in make_site).
