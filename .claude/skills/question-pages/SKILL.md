# question-pages (Mon, Wed, Fri 7:10 am; Fridays also results)

One job: draft one question page from seo/BACKLOG.md, gate it, and publish it if every gate passes. A minor change under coo/CONSTITUTION.md section 2 (Todd, Oct 22): no go needed when every gate passes; anything a gate flags goes to Todd instead. You never touch Gumroad, Kit, prices, the home, shop or lead page layouts, or message anyone but Todd.

## Inputs (Reads)
- seo/BACKLOG.md (the queue), seo/QUESTIONS.md (pages made), seo/STORE.md (rules), seo/RESULTS.md.
- Audience by day: Mon group A (lead trades), Wed group B (e-commerce, the kit), Fri group C (calculator trades). Take the top row of that group with no line in seo/QUESTIONS.md.
- The paid product's data file (site/pages.json "data") and the matching free calculator (site/store.json calcProducts, or the row's calculator).

## Process (Executes)
1. Date from bash. `python3 tools/check_repo.py --preflight question-pages`. Re-fetch the row's URL (WebFetch) and confirm the question still reads as recorded; if not, skip the row with a note.
2. Search the question (WebSearch) and read the top 3 Google results; note what each answers and misses.
3. Write a spec in site/pages.json, kind "question", "draft": true: the answer in the first 100 words; one worked example with real numbers as {placeholders} from the product's data (tools/question_site.py stats) or a dated primary source named in "sources"; one table or tiles block; one link to the paid product and one to a free calculator ("calculator"); the byline is built in. Length is what the question needs. No em or en dashes, no banned words (tools/legal_scan.py), no invented people, numbers or claims, no named failed restaurant.
4. `python3 tools/make_site.py`, `python3 tools/question_site.py`, `python3 tools/check_repo.py`: all exit 0.
5. Gates, each a fresh Agent subagent (model fable, else opus) that never saw the drafting:
   a. Copy and facts: every number traced to the data file or a dated primary source; dashes, banned words, legal lines, the Legal desk rules in legal/README.md. PASS or FAIL with lines.
   b. Search intent: does the page answer the question better than the current top 3 results? PASS or FAIL with reasons.
   One fix round per gate; a second FAIL stops the page and goes to Todd.
6. Both PASS: remove "draft", rebuild, check_repo exits 0, commit, push to main (pull --rebase once on a reject; never force). Add the row to seo/QUESTIONS.md and one line to seo/RESULTS.md: date, slug, "published, gates PASS".
7. Fridays: one line per live question page in seo/RESULTS.md from Search Console (impressions, clicks, average position, 28 days), read in the built-in browser; if the browser can't be reached, write "Search Console not read" with the date and tell Todd. First Friday of a month: list pages at average position 8 to 20 as refresh candidates; refreshing one is a run of its own.

## Outputs (Writes)
- site/pages.json (one spec), docs/ through tools/make_site.py only, seo/QUESTIONS.md, seo/RESULTS.md.
- Message to Todd only on a second FAIL, a blocked source, or a failed check.
