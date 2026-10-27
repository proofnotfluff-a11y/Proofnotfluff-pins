# Launch record: Chicago Permit Wait Times (free data page), LIVE Oct 27, 2026

Todd's go, Oct 27, 2026, 12:17 pm: "Let's do them all" (coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md). R10 item 2 (research_notes/kimi-2026-10-27-r10.md). Build chat B2.

- Page: https://proofnotfluff.com/chicago-permit-wait-times/ (tools/dp_permit_wait.py, site/pages.json kind "datapage", module dp_permit_wait).
- Sub-pages: one per permit type with at least 300 issued permits in the last 12 months (`pageFloor`, set in tools/dp_permit_wait_data.py), plus chicago-permit-wait-times.csv with every figure on the pages.
- Data: City of Chicago Building Permits (ydr8-5enu, updated daily). Measure: the City's processing_time field, days from application_start_date to issue_date, issued permits only. Median and 80th and 90th percentiles by nearest rank; groups under 20 permits show a count only (`minN`).
- Pull: .github/workflows/dp_permit_wait.yml runs tools/dp_permit_wait_data.py on a push of its tools, by hand, and Mondays 11:50 UTC. The query asks for six columns only (permit_type, review_type, application_start_date, issue_date, processing_time, community_area); strip() drops anything else. Output: site/datapages/dp_permit_wait/stats.json (aggregates only). Separate from permits-chicago.yml, which it never touches.
- Checks built in: the pull refuses to write under 20,000 issued permits in 24 months, or when processing_time matches the two dates on under 95% of rows; planted selftests for the data tool and the page run in the workflow before the pull.
- Flow: verify/flows/chicago-permit-wait-times.json (chart path switch, month table, map tap, metric and list pick, sub-page open).

## Gates and go-live (LIVE Oct 27, 2026)
- Facts: round 1 PASS (21 of 21 against the City API), final PASS (27 of 27, incl. the Mar 2026 wrecking switch: 437 permits, 61 and 103 days).
- Legal desk: CLEARED WITH FIXES (step titles recast as descriptions), applied.
- Copy: 4 rounds, every listed fix applied; last check left 2 wording items, applied word for word.
- Design director: 4 rounds. Round 1 4.29 / 4.57 / 4.43, round 2 4.43 / 4.57 / 4.57, round 3 4.29 / 4.43 / 4.57, final 4.43 / 4.57 / 4.71 (main / sub-page / demolition), no score under 4. Repeat FAILs went to Todd (DESIGN_DIRECTOR.md); [stated] Todd, live chat, Oct 27: "One final check round" with go-live if facts and copy pass and each design page averages 4.4 or more. Met.
- Build: make_site 0, verify --changed --before --flows PASS 82 of 82, check_repo 0.
- Open, for later: final design notes not done (review path bar cells, area lookup on sub-pages, phone toggle for hidden columns, CTA button alignment, map side gap in the shared geo_map.py); make_site does not delete a sub-page folder when a type drops under the floor (stale folders were removed by hand once).
- Data note: the City's records show 0 days for most wrecking and demolition permits up to Feb 2026; tools/dp_permit_wait_data.py record_change() detects that switch and the pages give figures from Mar 2026 on.
