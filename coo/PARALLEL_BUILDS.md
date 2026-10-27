# Parallel builds: free Chicago data pages (Todd, Oct 27, 2026, 12:17 pm: "Let's do them all")

Read by every build chat named in its prompt, after CLAUDE.md, coo/HANDOFF.md and coo/CONSTITUTION.md. The list and evidence: research_notes/kimi-2026-10-27-r10.md (merged R10). Todd's go covers building each page, its data workflow and taking it live once every gate below passes. Not covered, so ask Todd in chat first: email capture, checkout or pricing, outreach, any account, a scheduled task, paid data.

## How a page plugs in (tools/make_site.py, no edit needed)
- Your entry is already in site/pages.json: kind "datapage", your slug, your module, "draft": true. Edit only the lines inside your own entry, by hand (never re-dump or reformat the file, never touch "updated").
- Your module tools/<module>.py provides: META = {"h1", "card", "keywords"}; page_html(p) returning the whole page (pattern: tools/news_site.py and tools/rodents_site.py, which use make_site's HEAD, FOOT, crumbs, ld_tags, E); optional lastmod(p) -> "YYYY-MM-DD"; optional extra_pages(p) -> [(relative path, html or csv text)] for sub-pages and downloads under your own folder (they go in the sitemap with your lastmod when live).
- Until the module exists the build writes a noindex stub. Draft pages render noindex and stay out of the sitemap, search, hub and footer. Live data pages appear on /chicago-data/ (the hub) and in search by themselves.
- Maps: tools/geo_map.py (choropleth) and site/geo/chicago-community-areas.json; read only. Population per community area is owned by the rat build (site/geo/chicago-community-area-population.json); others use it only if present.

## Files: yours vs shared
- Yours: tools/<module>.py (and any tools/<module>_*.py), your data under site/datapages/<module>/, .github/workflows/<module>.yml, verify/flows/<slug>.json, launches/<slug>.md (your record), CSS inside your page or docs/assets/<module>.css.
- Shared, do not edit: tools/make_site.py, docs/assets/pnf.css, coo/HANDOFF.md, MAP.md, tools/README.md, seo/RESULTS.md, coo/DECISIONS-*.md, other builds' files. The wrap-up chat writes the shared records from your scoreboard row. A real bug in a shared file: smallest fix, own commit, reason in the message.

## Data
- The cloud shell cannot reach data hosts. Pull in your GitHub Actions workflow (pattern: .github/workflows/chicago-geo.yml with tools/chicago_geo.py), triggered on push of your tool, workflow_dispatch and a cron that fits the source; dispatch with GitHub MCP actions_run_trigger if available, then pull what it commits. Commit counts and tables, never raw rows with people in them.
- Privacy: aggregates by community area, ZIP, trade or month. Drop contact, name and street columns at ingest. Never a home address, a private person or a named business in trouble (failed inspection, violation, complaint). City vendors that won public contracts are fine by business name.
- Every number on the page traces to an official source with its link and a checked date. A field you could not open from a primary source is not published.

## Gates (each a fresh Agent subagent, model opus, that never saw the build)
1. Facts: opens every source, samples at least 10 published numbers against the City or agency's own records. PASS or FAIL per item.
2. Design director: design/DESIGN_DIRECTOR.md on the verify shots at 390 and 1280, light and dark; no score under 4, average over 4.6.
3. Legal desk: legal/README.md, the source's terms word for word, `python3 tools/legal_scan.py`; no advice beyond "check with the agency".
4. Copy: plain words, no em or en dashes, no invented numbers, written for trade owners.
5. `python3 tools/make_site.py`, `python3 tools/verify_site.py --changed --before --flows` (your flow file in the same commit), `python3 tools/check_repo.py`: all exit 0.
Fix and rerun with a new subagent until each passes. Then flip "draft" to false, rebuild, verify again, push.

## Pushing with others in the repo
`git fetch origin main && git rebase origin/main`. Conflicts only in docs/ (generated): `git checkout origin/main -- docs && python3 tools/make_site.py && git add docs && GIT_EDITOR=true git rebase --continue`. Any other conflict: stop and resolve by hand, keeping both sides. check_repo exits 0, then `git push origin HEAD:main`. Never force.

## Done means
Scoreboard row (todos/<row id>): done true, doneAt, and detail = the live URL, the gate lines (PASS/FAIL with the metric), what the wrap-up must record (new workflow, data paths, anything for HANDOFF). One message to Todd: the PASS/FAIL lines, the live URL, the 3 to 5 line handoff delta. Close the chat.
