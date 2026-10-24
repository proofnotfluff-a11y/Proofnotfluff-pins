# index-request (Fridays 7:40 am Central, Todd's PC, after question-pages)

One job: ask Google to index the live proofnotfluff.com pages it has not indexed yet, and read the Friday Search Console numbers the cloud question-pages run cannot reach. Runs in the built-in browser on Todd's PC (scheduled task "PNF site: index request", requires the computer). Todd's go, Oct 23, 2026, 7:11 pm. coo/CONSTITUTION.md binds this run. You never sign in, accept terms, change a Search Console setting, remove a URL, or edit a page; you inspect, request indexing, read reports, and log.

## Inputs (Reads)
- `python3 tools/indexnow_submit.py --all --dry-run`: the live list (docs/sitemap.xml minus noindex pages). Nothing else counts as live.
- seo/index-requests.json: {url: last day requested}. seo/QUESTIONS.md: the live question pages. seo/RESULTS.md: past lines.
- Search Console, URL property https://proofnotfluff.com/, signed in as proofnotfluff@gmail.com in the built-in browser.

## Process (Executes)
1. Date from bash. `python3 tools/check_repo.py --preflight index-request`. git pull.
2. Load the built-in-browser skill. Open Search Console. Not signed in, or the browser can't be reached: write the step 7 line as "not run" with the reason, tell Todd in one line, stop.
3. Order the live list newest first: URLs added to docs/sitemap.xml since the last index-request line, then the rest in reverse sitemap order (site/pages.json appends new pages last).
4. For each URL: the top search box, URL Inspection, wait for the result. "URL is on Google" counts as indexed. Otherwise, unless seo/index-requests.json shows it requested in the last 7 days (a repeat request changes nothing), click Request indexing and wait for the dialog: "Indexing requested" counts as requested (write today in seo/index-requests.json); "Quota Exceeded" or any error counts as refused with its reason. After the first Quota Exceeded, request nothing more today and keep inspecting. Close every dialog with its Dismiss button before the next URL, never by pressing Return.
5. Friday Search Console lines (question-pages step 7 points here): Performance, Search results, last 28 days, Pages filter, one line per live question page in seo/RESULTS.md: page, impressions, clicks, average position, date. First Friday of a month, list pages at average position 8 to 20 as refresh candidates (a refresh is a run of its own).
6. Read numbers from the page text (get_page_text, read_page); screenshots only to read a dialog.
7. One line in seo/RESULTS.md: "YYYY-MM-DD (index-request): inspected N, already indexed N, requested N, refused N (reason), not requested N (quota or requested in the last 7 days)". `python3 tools/check_repo.py` exits 0, commit seo/ only, git push origin HEAD:main (pull --rebase once on a reject, never force).

## Outputs (Writes)
- seo/RESULTS.md (the run line and the Friday Search Console lines), seo/index-requests.json.
- Scoreboard agents/index-request {state, lastRun, lastStatus, lastNote}: counts only.
- A message to Todd only when the run could not start or a count is off (inspected not equal to the live list).
