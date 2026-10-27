# Launch record: Chicago Permit Wait Times (free data page)

Todd's go, Oct 27, 2026, 12:17 pm: "Let's do them all" (coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md). R10 item 2 (research_notes/kimi-2026-10-27-r10.md). Build chat B2.

- Page: https://proofnotfluff.com/chicago-permit-wait-times/ (tools/dp_permit_wait.py, site/pages.json kind "datapage", module dp_permit_wait).
- Sub-pages: one per permit type with at least 300 issued permits in the last 12 months (`pageFloor`, set in tools/dp_permit_wait_data.py), plus chicago-permit-wait-times.csv with every figure on the pages.
- Data: City of Chicago Building Permits (ydr8-5enu, updated daily). Measure: the City's processing_time field, days from application_start_date to issue_date, issued permits only. Median and 80th and 90th percentiles by nearest rank; groups under 20 permits show a count only (`minN`).
- Pull: .github/workflows/dp_permit_wait.yml runs tools/dp_permit_wait_data.py on a push of its tools, by hand, and Mondays 11:50 UTC. The query asks for six columns only (permit_type, review_type, application_start_date, issue_date, processing_time, community_area); strip() drops anything else. Output: site/datapages/dp_permit_wait/stats.json (aggregates only). Separate from permits-chicago.yml, which it never touches.
- Checks built in: the pull refuses to write under 20,000 issued permits in 24 months, or when processing_time matches the two dates on under 95% of rows; planted selftests for the data tool and the page run in the workflow before the pull.
- Flow: verify/flows/chicago-permit-wait-times.json (chart path switch, month table, map tap, metric and list pick, sub-page open).
- Gates and go-live: see the scoreboard row todos/build-permit-wait.
