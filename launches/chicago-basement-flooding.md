# Chicago Basement Flooding Calls by Neighborhood (build B8, Oct 27, 2026)

Todd's go: Oct 27, 2026, 12:17 pm, "Let's do them all" (coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md). R10 item 9.
Audience: trade owners (plumbers, waterproofing and restoration companies), Todd Oct 27, 9:04 am.

## What it is
- Page: /chicago-basement-flooding/ (site/pages.json kind "datapage", module tools/dp_flooding.py).
- Data: City of Chicago 311 Service Requests (v6vf-nfxy). Request types confirmed in the data Oct 27, 2026
  (site/datapages/dp_flooding/source-check.json): "Water in Basement Complaint" (short code AAF) and
  "Sewer Cleaning Inspection Request" (CHECKFOR). Related types seen but left out: Water On Street Complaint (AAE),
  Sewer Cave-In Inspection Request (AAD), Alley Sewer Inspection Request (AAI).
- Shows: requests per community area per month, the last 12 whole months against the 12 before, rank of 77,
  per 1,000 residents (build B4's site/geo/chicago-community-area-population.json, present Oct 27), a daily citywide
  series for 365 days with the busiest days, the 10 busiest days since 2019, a per-area month by month picker, the map
  (tools/geo_map.py) and two CSV downloads.
- City meaning of each type: Department of Water Management pages read Oct 27, 2026
  (chicago.gov .../water/provdrs/ops/svcs/waterbasement.html and .../engineer/svcs/request_sewer_cleaninginspection.html).

## Data workflow
- .github/workflows/dp_flooding.yml, daily 11:35 UTC, on push of its tools, and by hand. One query per type and month
  (grouped queries over the whole table time out), grouped by day and community area. Each run pulls the last 3 months
  again; the 1st of each month pulls everything from Jan 2019. Duplicates the City flags are left out.
- Writes site/datapages/dp_flooding/monthly.json (counts only) and rebuilds docs/.
- A push whose message says [probe] reruns tools/dp_probe_b8.py (columns, type names, City terms).

## Privacy
Counts only. No address, location, request number or resident text leaves the runner.

## Gates (each a fresh Opus subagent that never saw the build)
- Facts: PASS 16 of 16 (flooding), PASS 17 of 17 (repairs), every sampled number matched the City's Socrata API
  (duplicate=false for 311). Wording fixes applied: City code series, not bureaus; busiest days, not storm days.
- Legal desk: CLEARED WITH FIXES, all applied (Buildings not-liable note quoted word for word, FAQ wording, City page
  links for the 311 request types). Open for the attorney: the City terms' indemnity clause (same as the Oct 22 item 1).
- Design director: round 5 PASS 4.71 on both pages (rounds 1 to 4 FAIL, every listed fix applied).
- Copy: repairs PASS round 4; flooding round 6 found 1 must-fix (catch basin wording), applied word for word as given.
- Verify: `verify_site.py --changed --before --flows` PASS, 0 failing of 52 checks; check_repo 0 errors.
- Live Oct 27, 2026 (draft false), Todd's go of 12:17 pm.

## For the wrap-up
- New workflows: .github/workflows/dp_flooding.yml (daily 11:35 UTC), dp_repairs.yml (daily 11:50 UTC).
- Data: site/datapages/dp_flooding/monthly.json, site/datapages/dp_repairs/monthly.json and trade-map.json;
  source checks in site/datapages/*/source-check.json, City terms in site/datapages/dp_repairs/city-terms.txt.
- Found on the live rat page (not this build's file): its FAQ says Bucktown is in West Town; the City places Bucktown
  in Logan Square. The same line was fixed on both B8 pages.
