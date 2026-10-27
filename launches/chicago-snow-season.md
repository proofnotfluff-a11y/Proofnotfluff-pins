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

## Gates
(filled in by the build chat)
