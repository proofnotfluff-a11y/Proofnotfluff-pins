# Chicago Repair Demand by Trade (build B8, Oct 27, 2026)

Todd's go: Oct 27, 2026, 12:17 pm, "Let's do them all" (coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md). R10 item 14.
Audience: trade owners (masons, porch carpenters, electricians, HVAC and boiler, elevator and plumbing companies).

## What it is
- Page: /chicago-repair-demand/ (site/pages.json kind "datapage", module tools/dp_repairs.py).
- Data: City of Chicago Building Violations (22u3-xenr), counted by the month of violation_date.
- Trades: the published hand mapping site/datapages/dp_repairs/trade-map.json (also downloadable from the page).
  A listed violation code goes to its trade; any other code in the City's EV, BR, VT, RF, PL or EL code series goes to
  the matching trade (the facts gate found the series do not map one to one to the issuing bureau, so the page names
  the code series, not a bureau); everything else is not counted by trade. 31 codes are left out on purpose
  (paperwork, permits, plans, records, arranging inspections, or wording that is only OPEN), each with its reason.
  Mapping built from the source check of 12 months of codes (site/datapages/dp_repairs/source-check.json, Oct 27).
- No community area column in the dataset: the runner places each violation's latitude and longitude inside the
  City's community area outlines (site/geo/chicago-community-areas.json). Points never leave the runner.

## Legal notes read word for word
- The dataset's description (Department of Buildings): "Lenders and title companies, please note: These data are
  historical in nature and should not be relied upon for real estate transactions..." and "The information presented
  on this website is informational only and does not necessarily reflect the current condition of the building or
  property." Both sentences are quoted in the page footer; the FAQ says the page is not for checking a property.
- City Data Terms of Use: site/datapages/dp_repairs/city-terms.txt (fetched by the runner Oct 27). The required
  disclaimer is in the footer (make_site CITY_DISCLAIMER).

## Data workflow
- .github/workflows/dp_repairs.yml, daily 11:50 UTC, on push of its tools or the mapping, and by hand. One month per
  query, grouped by code, description and map point, paged. Each run pulls the last 3 months again; the 1st of each
  month, a changed mapping or a missing file pulls the last 4 calendar years and this one.
- Writes site/datapages/dp_repairs/monthly.json (counts only) and rebuilds docs/.

## Privacy
Never an address, a property, an owner or a business. Counts by trade, community area and month only.

## Gates
(filled in at go-live)
