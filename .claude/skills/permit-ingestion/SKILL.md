# permit-ingestion (Mondays 8:10 am, after the data workflows)

One job: prove this Monday's Entity A data is fresh, complete and true. Code fetches and filters; you only verify and report. You never publish, buy, message anyone but Todd, or touch Gumroad, Etsy or email.

## Inputs (Reads)
- GitHub Actions runs today for permits-chicago.yml, permits-austin.yml, inspections-chicago.yml, downstream-leads.yml (GitHub MCP actions_list; dispatch downstream-leads.yml once with actions_run_trigger if it has no run today).
- permits/downstream/gc_leads.json, permits/chicago/sample.json, permits/austin/sample.json, permits/inspections-chicago/rest-sample.json.
- launches/<slug>.md and the free pages (the holdout's only inputs).

## Process (Executes)
1. A failed or missing workflow run today is the first FIX line.
2. Gates, all must exit 0: `python3 tools/validate_leads.py gc --max-age-days 2`, `python3 tools/ingest_downstream.py --selftest`, `python3 tools/permits_chicago.py --selftest`, `python3 tools/permits_austin.py --selftest`, `python3 tools/inspections_chicago.py --selftest`. Each non-zero exit is a FIX line with its ERROR text.
3. Holdout (semantic): a fresh subagent that never opens tools/ or any test gets the inputs above and checks 10 GC leads per city against the City's own API by WebFetch: permit id, address, general contractor, the stage text, and the signal record (Chicago 4ijn-s7e5 inspection_id, Austin certificate_of_occupancy). It also checks every number on each free page against this week's file. It returns PASS or numbered problems with the record id and URL read.
4. Pages: Playwright at 390 px and 1280 px on each live members' app and free page: loads, password form, #/terms opens, this week's date, each checkout link opens the right Gumroad product (never buy).

## Outputs (Writes)
- qa/<YYYY-MM-DD>.md: one PASS or FIX line per check with the evidence (exit code, counts, URLs). Commit and push after `python3 tools/check_repo.py` exits 0.
- Scoreboard leadproducts/<slug> {thisWeek, updatedAt}; agents/leads-qa idle with lastRun, lastStatus, lastNote. CRM meta/desk.lastQa (one sentence).
- Todd hears only about failures: one plain line per FIX and who fixes it (the product-builder stage takes FIX lines first).
