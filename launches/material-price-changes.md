# Material Price Changes Since Your Quote (build B9)

Todd's go: Oct 27, 2026, 12:17 pm, "Let's do them all" (coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md). R10 item 11 (research_notes/kimi-2026-10-27-r10.md).

## What it is
- /material-price-changes/: since-your-quote calculator (material, quote month, amount; result, difference, preliminary note, copy-as-a-sentence), 12-month change bar chart, table of 23 materials by group with 1-month and 12-month change and a 12-month sparkline, notes on reading the numbers, method, FAQ, CSV of every month.
- 23 sub-pages /material-price-changes/<slug>/: tiles, line chart (phone and desktop drawings, crosshair, arrow keys), the calculator opened on that material, every month in a table, its own CSV.
- The free rival named in R10 (consight.ai) has a fresh table with no download and no since-my-quote math.

## Data
- Source: U.S. Bureau of Labor Statistics, Producer Price Index by commodity, not seasonally adjusted, through the BLS Public Data API (v2 without a key; catalog disabled without a key, so titles come from BLS pages, recorded per series in site/datapages/dp_materials/series.json).
- BLS's flat files (download.bls.gov) refuse GitHub runners with HTTP 403 (Oct 27, 2026); the API answers. No workaround was attempted.
- Files: site/datapages/dp_materials/series.json (23 ids, BLS titles and where each was read), ppi.json (monthly values since Jan 2017, P = preliminary), status.json (what BLS returned and said), schedule.json (BLS release dates read Oct 27, 2026; refresh by hand after Nov 2027).
- Workflow: .github/workflows/dp_materials.yml runs tools/dp_materials_bls.py on push of its files, by hand, and weekdays 15:10 UTC; it commits only when a number changed. Each run uses 1 to 2 of the API's daily requests (25 series per request).
- Page: tools/dp_materials.py (selftest: `python3 tools/dp_materials.py --selftest`). Flow: verify/flows/material-price-changes.json.

## Gates (fresh opus subagents, Oct 27, 2026)
- Facts: PASS, 15 samples (group 13 values against BLS's Mid-Atlantic table, ids and titles against wp.item and BLS's 2013 notice, release date against BLS's schedule, 12-month diesel +115.2% against BLS's Economics Daily of Oct 21, 2026), 0 mismatches. Values for groups 05 to 10 and the Midwest series were not opened by the checker (the API needs a permission prompt here); they come straight from the BLS Public Data API.
- Design director: PASS 4.71 on round 5 (5, 5, 4, 5, 4, 5, 5). Rounds 1 to 4 FAIL (4.57, 4.43, 4.57, 4.57); Todd, 2:43 pm: "Get design over the hurdle then go live".
- Legal desk: PASS (BLS API terms: disclaimer word for word, retrieval date cited, no logo, derived numbers labeled as ours; guide named by its BLS title; no advice beyond "check with BLS"). legal_scan: 0 lines on this page.
- Copy: PASS on the final build.
- Build and verify: make_site, verify_site --changed --before --flows PASS 88 of 88, check_repo 0 errors.

## For the wrap-up
- New workflow: dp_materials.yml. New data folder: site/datapages/dp_materials/.
- A free BLS API key (Todd's account, his call) would turn on BLS's catalog so titles are re-read every run; today a renamed series would keep its recorded title until series.json is edited.
