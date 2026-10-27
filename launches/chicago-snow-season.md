# Chicago Snow Season Board for Plow Owners (/chicago-snow-season/)

Free data page, kind "datapage", module tools/dp_snow.py. Todd's go: Oct 27, 2026, 12:17 pm, "Let's do them all" (coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md). Evidence: research_notes/kimi-2026-10-27-r10.md item 1. Build chat B1.

## What it is
- Days with new snowfall at or over 1, 2, 3 and 6 inches per winter (July 1 to June 30) at two NOAA stations, the 30 full winters 1996-97 to 2025-26 plus this winter to date.
- Light (nearest-rank 20th percentile), middle (median) and heavy (nearest-rank 80th percentile) winters, by month, first and last plowable days, this winter against past winters by the same date, a table of every winter, two CSV downloads.
- Feeds the live snow removal pricing calculator: a "Fill it from past Chicago winters" block (station, trigger, light, middle or heavy) fills "Pushes you expect in a season", shown only while the board is live. Edit confined to snow_page and its new helper _snow_fill in tools/make_site.py.
- Never: a forecast of the coming winter, neighborhood snowfall, prices.

## Data
- Source: NOAA NCEI GHCN-Daily (daily-summaries), SNOW and SNWD, through the NCEI Access Data Service.
- Pull: tools/dp_snow_fetch.py in .github/workflows/dp_snow.yml (daily 12:35 UTC, October to April; on push of its tools; by hand). Writes site/datapages/dp_snow/daily.json, rebuilds the site, commits. Weather records only.
- Stations come from NOAA's own station search (bbox over the city), never typed in: O'Hare USW00094846 (CHICAGO OHARE INTERNATIONAL AIRPORT), 98.4% of snow-month days reported. Midway: USC00111577 (CHICAGO MIDWAY AIRPORT 3 SW, cooperative observer), 99.97%; the airport's automated station USW00014819 reports snowfall on 4% of days and is passed over by the run.
- Incomplete winters (more than 3 missing snow-month days): O'Hare 1996-97 (40) and 1997-98 (79); left out of every summary, so O'Hare uses 28 winters and Midway 30.

- Values NOAA's quality checks flagged are dropped at the source (Oct 27, found by the facts gate: a W-flagged 11 inch September 2024 depth at Midway): O'Hare 4 snowfall and 8 depth values, Midway 2 depth values (daily.json flaggedDropped).
- Flow file: verify/flows/chicago-snow-season.json (trigger and station change the counts; the board's link opens the calculator filled; Light, Middle, Heavy fill the field; keyboard tooltip).

## Gates (Oct 27, 2026; each a fresh opus subagent that never saw the build)
- Facts: round 1 FAIL (middle dates used the lower of two), round 2 FAIL (n/a rule wording), round 3 FAIL (quality-flagged values counted; monthly tooltip "had one"), round 4 PASS 19 of 19 (all 8 variants recomputed, 50 daily values sampled against NOAA, flag handling confirmed, NWS Dec 7 and Mar 20 confirmed).
- Design director: 4.00, 4.29, 4.57, 4.57, 4.29, 4.57, then PASS 4.71 (5, 5, 4, 5, 4, 5, 5; no score under 4).
- Legal desk: CLEARED WITH FIXES (GHCN-Daily DOI in the footer, NOAA revisions line, NOAA credit in the calculator fill), all applied. NCEI and NWS terms read word for word; the legal_scan "no full Terms" high is the standing flag for free pages with no sale.
- Copy: FAIL rounds with 28, 15, 5, 4 and 8 fixes, all applied; final full-page round PASS, then fresh checks of the last calculator messages PASS (all 8 station and trigger hints).
- Build: make_site, verify_site --changed --before --flows, check_repo: all exit 0.

## For the wrap-up (shared files this build may not edit)
- tools/make_site.py home_html calcs_live counts and lists kind "datapage" as calculators (Chicago dumpster permits today, this board once live): add "datapage" to the excluded kinds. The fix was blocked in this chat as outside its edit scope.
- docs/assets/pnf-calc.js number-field error says "Use digits, like 1200 or 1,200." on count fields, and the sticky bar shows $0 while a field is invalid.
- The calculator's footer sources line (site/pages.json, snow-removal-pricing-calculator "sources") could add NOAA NCEI GHCN-Daily now that the fill block uses it (Legal desk, low).
- Shared FAQ question text wraps early at 390; "Reset to the example" keeps its hover fill after a tap on touch screens.
- Cross-page link clicks in verify flows raise a headless Chrome view transition error on every page; flows open other pages with goto.
- Midway's middle winter at 2 inches is 5.5, so the fill can put a half push in the field; the note says "halfway between the two middle winters". Rounding is Todd's call.
