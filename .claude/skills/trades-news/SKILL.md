# trades-news (weekly, Tuesdays; Todd's go on the schedule pending)

One job: write this week's Chicago Trades News (site/news/chicago-trades.json, page /chicago-trades-news/, built by tools/news_site.py), gate it, and publish it if every gate passes. A weekly data refresh is a minor change under coo/CONSTITUTION.md section 2; a new page type, layout or email capture is major and goes to Todd. Todd's brief (Oct 27, 2026): "any major news impacting the trades in Chicago. New regulations, news events, tax related news, etc. Anything that would be useful to workers in the trades."

## Inputs (Reads)
- site/news/chicago-trades.json (last week's items), site/pages.json kind "tradesnews", seo/RESULTS.md.
- Beats, one fresh Agent subagent each (model opus), run in parallel: (1) rules, codes, permits, licensing, safety; (2) tax, pay, wage rates, utility rates; (3) projects, bids, programs, weather, events. Window: news from the last 8 days, or anything taking effect in the next 120 days not yet on the page.

## Process (Executes)
1. Date from bash. `python3 tools/check_repo.py --preflight trades-news`.
2. Each beat agent returns items as JSON (headline, stage, date, effective, category, trades, what, why, sources with exact URLs it opened). Primary sources first (chicago.gov, cityclerk, cookcountyil.gov, ilga.gov, idol.illinois.gov, irs.gov, ssa.gov, osha.gov, illinois.gov, transitchicago.com); reputable Chicago news when no primary exists.
3. Pick at most 8 new items a trade owner would act on. Drop duplicates of live items (update the live item instead: new stage, new date). Our own words only: no quotes, no em or en dashes, no named private people, proposed is never written as passed. Politics stays neutral: what the measure does, its stage, and that the Council or legislature still votes; no side's arguments.
4. Write the items (checked = today), set "updated" to today, `python3 tools/news_site.py --check`, `python3 tools/make_site.py`, `python3 tools/check_repo.py`: all exit 0.
5. Gates, each a fresh Agent subagent that never saw the drafting:
   a. Facts: open every source URL; every number, date, name and stage in what and why must be on the linked page. PASS or FAIL per item.
   b. Copy: plain words, useful to a trade owner, no advice beyond "check", legal/README.md lines, `python3 tools/legal_scan.py` on the page.
   An item that fails twice is removed, not argued. A FAIL on half the items or more stops the run and goes to Todd.
6. Pass: commit, push to main (pull --rebase once on a reject; never force). One line to seo/RESULTS.md: date, "trades news refresh", items added, removed, gates PASS.

## Outputs (Writes)
- site/news/chicago-trades.json, docs/ through tools/make_site.py only, seo/RESULTS.md.
- Message to Todd only on a stop, a blocked tool, or a failed check.
