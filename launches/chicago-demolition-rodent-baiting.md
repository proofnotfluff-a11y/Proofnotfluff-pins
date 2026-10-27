# Launch record: Chicago Demolition Rodent Baiting (free data page)

Todd's go, Oct 27, 2026, 12:17 pm: "Let's do them all" (coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md). R10 item 12 (research_notes/kimi-2026-10-27-r10.md). Build chat B2, built with the permit wait times page.

- Page: https://proofnotfluff.com/chicago-demolition-rodent-baiting/ (tools/dp_demo_baiting.py, site/pages.json kind "datapage", module dp_demo_baiting).
- Steps: our plain words for the rodent control approval of a demolition permit (licensed pest control company baits the site, rodent control affidavit, Streets and Sanitation inspection, approval by email, attached on Form 480 page 2), plus the other Form 480 approvals and three timing rules. Sources: the Department of Buildings demolition permits page and Form 480 (rev. 8/29/2021), both read Oct 27, 2026 (STEPS_READ in the module). Department names only; no City staff named. When the City page changes, a live chat rereads it and updates STEPS and STEPS_READ.
- Counts: wrecking and demolition permits issued, by week and community area, from the same weekly pull as the permit wait times page (.github/workflows/dp_permit_wait.yml, tools/dp_permit_wait_data.py build_wreck). Output: site/datapages/dp_demo_baiting/wrecking.json (counts only).
- Links: the live rat complaints page (/chicago-rat-complaints/) and the City demolition permits page.
- Flow: verify/flows/chicago-demolition-rodent-baiting.json (steps, other approvals, map tap, metric and list pick, rat page link).
- Gates and go-live: see the scoreboard row todos/build-permit-wait.
