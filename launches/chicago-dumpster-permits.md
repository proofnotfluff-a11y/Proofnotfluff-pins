# Launch record: Chicago Dumpster Permits by Neighborhood (B6 item 2), LIVE Oct 27, 2026

Decided: Todd, Oct 27, 12:17 pm ("Let's do them all", coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md), research_notes/kimi-2026-10-27-r10.md item 10. Page https://proofnotfluff.com/chicago-dumpster-permits/

## How it runs
- Daily about 7:05 am Chicago time (cron 5 12 UTC), .github/workflows/dp_dumpsters.yml runs tools/dp_dumpsters_pull.py: City of Chicago Data Portal, Transportation Department Permits (pubx-yq2d), applicationtype DOT_DMPSTR with an issue date. It asks for six fields only (record key, permit number, issue date, status, latitude, longitude); no primarycontact or other person field is ever requested. The permit number is used in memory to count each permit once (the City lists a multi-location permit as several rows) and is never written.
- Each location is joined to one of the 77 community areas by latitude and longitude (site/geo/chicago-community-areas.json). A permit counts once citywide and once in each area where it has a location.
- Output: site/datapages/dp_dumpsters/counts.json (counts only), then make_site rebuilds docs/. The page (tools/dp_dumpsters.py) shows the last 90 days against the same 90 days a year earlier, rank, 13 months citywide, a map (tools/geo_map.py), all 77 areas and a CSV of every area by month.
- The cost panel links to /chicago-public-way-permit-costs/ only once that page is live (it is on hold, launches/chicago-public-way-permit-costs.md); until then the page links the free junk removal truck load calculator.

## Gates
- Facts round 1: FAIL (the page counted dataset rows, about 13% more than permits; Bucktown is in Logan Square; an unverified fee schedule link). All fixed. Round 2 (fresh checker): PASS 22 of 23, every number matches the City, including all 77 area counts against the portal's own area join; the one figure the City could not confirm (permits in more than one area) is no longer printed.
- Design director: round 1 FAIL 4.57, round 2 FAIL 4.57, round 3 PASS 4.71 (no score under 4); round 3 polish applied after.
- Legal desk: CLEARED twice (City disclaimer word for word, counts only, no person fields, permit number never written). Open as on every Chicago page: the City's indemnity clause, for Todd's attorney.
- Copy: round 1 FAIL 4.20, round 2 PASS 4.60, its accuracy rewrites applied.
- verify_site: dumpster page PASS at 390 and 1280, light and dark, axe 0; flow 14 of 14 steps at both widths. check_repo 0 errors on the live push.

## For the wrap-up
- New workflow: .github/workflows/dp_dumpsters.yml (daily). Data: site/datapages/dp_dumpsters/counts.json.
- Shared-file notes from the design gate (not changed here): tools/geo_map.py dark lowest map band is close to the map background; pnf.css `details` border doubles on pages that style their own summary; `.cta p{margin:0}` cancels `.ld-buybtn` spacing in single-column CTAs. The rat page FAQ also says Bucktown is in West Town (it is in Logan Square).
