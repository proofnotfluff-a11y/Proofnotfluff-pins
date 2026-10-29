# /chicago-construction-pipeline/ (draft, noindex, waiting on Todd's preview yes)

Todd, Oct 29, 2026, 3:56 pm: "Yes, please do. Go with your recommendations for everything." (after the cfongai NYC call list read and Kimi's review). New page type, so Todd sees the preview before it goes live (CONSTITUTION 2).

- What: counts only. Open City of Chicago new construction and renovation permits of $500,000 or more since 2021 still waiting on a certificate of occupancy, by community area and months since permit; issue-year certificate shares; stage meanings; a weekly snapshot table. No address, permit number or business name.
- Why counts only: area seats and the $29 list sell addresses (Oct 27 "lead seats and exports stay paid").
- Timing finding behind it: research_notes/stage-timing-2026-10-29.md (inspections stage is months before a certificate, not weeks).
- Data: tools/dp_pipeline_data.py on the existing Monday run .github/workflows/dp_permit_wait.yml (no new schedule; step is continue-on-error). Writes site/datapages/dp_pipeline/data.json and state.sealed.json (permit number and milestone pairs sealed with PNF_DATA_KEY, for week to week moves).
- Page: tools/dp_pipeline.py, pages.json entry "chicago-construction-pipeline" (draft true), flow verify/flows/chicago-construction-pipeline.json (light and dark).
- Video: bank lesson 22 at the end of the trades-first table in video/studio/research/IDEAS.md.

## Gates (Oct 29, 2026)
- Facts: PASS 21 of 21 numbers against the City API (no drift since the pull); wording fixes applied word for word over two rounds; final recheck 5 of 5 spot checks plus all 77 rows by script.
- Legal desk: round 1 CLEARED WITH FIXES (all applied), round 2 CLEARED. Known scan findings only (edison park is an area name; no site Terms of Use, same as sister pages; "official" inside the City disclaimer).
- Copy: round 1 FAIL (3 must fix), applied; round 2 PASS.
- Design director: round 1 FAIL 4.00 (Polish 3), fixes applied; round 2 PASS 4.71 (5, 5, 4, 5, 4, 5, 5); optional polish notes applied.
- Build: verify 8 of 8 PASS (390 and 1280, light and dark, flow 18 of 18, axe 0), make_site 0, check_repo 0.

## Open
- For the attorney: City data terms indemnity (same as other City pages); no site-wide Terms of Use; whether area cells of 1 or 2 should be suppressed.
- Shared tools/geo_map.py: map touches its frame on the east and south edges (already open from the permit wait launch).
- Go live: flip "draft" to false on Todd's yes, rebuild, verify, push. Confirm state.sealed.json is on main before Monday Nov 2.
