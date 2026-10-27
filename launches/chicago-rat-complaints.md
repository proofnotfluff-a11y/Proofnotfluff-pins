# Launch record: Chicago Rat Index upgrade, LIVE Oct 27, 2026

Todd's go: Oct 27, 2026, 12:17 pm, "Let's do them all" (coo/DECISIONS-2026-10-27.md; R10 items 4 and 13; build chat B4).
Live: https://proofnotfluff.com/chicago-rat-complaints/ plus 77 area pages (/chicago-rat-complaints/<area>/), each with badge.svg and weekly.csv, and /chicago-rat-complaints/rat-index.csv.

## What it is
- Rat Index: rat complaints to 311 per 1,000 residents for all 77 community areas, ranked, with the rank against the 30 days before and the same 30 days a year earlier, median days to close, top risers, and a yearly "rattiest neighborhoods" list (12 months to Sep 30, new each October).
- Restaurant pest and hood citations: weekly share of restaurant food inspections citing violation 38 (pests) and violation 56 with a hood or vent note, by community area, as map metrics. Counts only, never a restaurant name.
- Free embeddable badge per area with copy-paste code; CSVs under CC BY 4.0.

## Data and code
- tools/rodents_chicago.py (311 v6vf-nfxy counts, prior 30 days, area weeks, close times, yearly edition; --population writes site/geo/chicago-community-area-population.json from City dataset t68z-cikk, ACS year 2023).
- tools/rodents_restaurants.py (Food Inspections 4ijn-s7e5, point in community area, counts only) writes permits/rodents-chicago/restaurants.json.
- tools/rodents_site.py (page, 77 area pages, badges, CSVs); .github/workflows/rodents-chicago.yml (Mondays, plus on push of these tools).
- Flows: verify/flows/rat-map.json (unchanged, passing) and verify/flows/chicago-rat-complaints.json (new).

## Gates (fresh opus checkers)
- Facts: PASS 16 of 16 against the City's own records (hood count 198 traced to the file, not independently re-run).
- Legal desk: PASS (legal_scan highs reviewed as false positives: "edison park" is a community area name; free page terms precedent).
- Design director: round 1 FAIL 4.39, round 2 FAIL 4.43, round 3 FAIL 4.50, round 4 PASS 4.71, min 4.
- Copy: rounds 1 to 9 FAIL (fixes each round), round 10 PASS.
- make_site, verify_site --changed --before --flows (92 checks), check_repo: all exit 0.

## Open, not this build's files
- site/pages.json entries chicago-basement-flooding and chicago-repair-demand say "Bucktown and Wicker Park are in West Town"; Bucktown is in Logan Square.
