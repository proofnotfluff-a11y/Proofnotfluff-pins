# Launch record: Chicago Demolition Rodent Baiting (free data page), LIVE Oct 27, 2026

Todd's go, Oct 27, 2026, 12:17 pm: "Let's do them all" (coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md). R10 item 12 (research_notes/kimi-2026-10-27-r10.md). Build chat B2, built with the permit wait times page.

- Page: https://proofnotfluff.com/chicago-demolition-rodent-baiting/ (tools/dp_demo_baiting.py, site/pages.json kind "datapage", module dp_demo_baiting).
- Steps: our plain words for the rodent control approval of a demolition permit (licensed pest control company baits the site, rodent control affidavit, Streets and Sanitation inspection, approval by email, attached on Form 480 page 2), plus the other Form 480 approvals and three timing rules. Sources: the Department of Buildings demolition permits page and Form 480 (rev. 8/29/2021), both read Oct 27, 2026 (STEPS_READ in the module). Department names only; no City staff named. When the City page changes, a live chat rereads it and updates STEPS and STEPS_READ.
- Counts: wrecking and demolition permits issued, by week and community area, from the same weekly pull as the permit wait times page (.github/workflows/dp_permit_wait.yml, tools/dp_permit_wait_data.py build_wreck). Output: site/datapages/dp_demo_baiting/wrecking.json (counts only).
- Links: the live rat complaints page (/chicago-rat-complaints/) and the City demolition permits page.
- Flow: verify/flows/chicago-demolition-rodent-baiting.json (steps, other approvals, map tap, metric and list pick, rat page link).

## Gates and go-live (LIVE Oct 27, 2026)
- Facts: round 1 PASS (21 of 21 against the City API), final PASS (27 of 27, incl. the Mar 2026 wrecking switch: 437 permits, 61 and 103 days).
- Legal desk: CLEARED WITH FIXES (step titles recast as descriptions), applied.
- Copy: 4 rounds, every listed fix applied; last check left 2 wording items, applied word for word.
- Design director: 4 rounds. Round 1 4.29 / 4.57 / 4.43, round 2 4.43 / 4.57 / 4.57, round 3 4.29 / 4.43 / 4.57, final 4.43 / 4.57 / 4.71 (main / sub-page / demolition), no score under 4. Repeat FAILs went to Todd (DESIGN_DIRECTOR.md); [stated] Todd, live chat, Oct 27: "One final check round" with go-live if facts and copy pass and each design page averages 4.4 or more. Met.
- Build: make_site 0, verify --changed --before --flows PASS 82 of 82, check_repo 0.
- Open, for later: final design notes not done (review path bar cells, area lookup on sub-pages, phone toggle for hidden columns, CTA button alignment, map side gap in the shared geo_map.py); make_site does not delete a sub-page folder when a type drops under the floor (stale folders were removed by hand once).
- Data note: the City's records show 0 days for most wrecking and demolition permits up to Feb 2026; tools/dp_permit_wait_data.py record_change() detects that switch and the pages give figures from Mar 2026 on.
