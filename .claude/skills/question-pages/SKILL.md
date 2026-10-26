# question-pages (daily 7:10 am; Fridays also results)

One job: draft one question page from seo/BACKLOG.md, gate it, and publish it if every gate passes. A minor change under coo/CONSTITUTION.md section 2 (Todd, Oct 22): no go needed when every gate passes; anything a gate flags goes to Todd instead. You never touch Gumroad, Kit, prices, the home, shop or lead page layouts, or message anyone but Todd.

## Inputs (Reads)
- seo/BACKLOG.md (the queue), seo/QUESTIONS.md (pages made), seo/STORE.md (rules), seo/RESULTS.md.
- Daily (Todd, Oct 22, 2026, 7:32 pm). Group: the one of A (lead trades), B (e-commerce, the kit), C (calculator trades) whose last page in seo/QUESTIONS.md is oldest (none yet counts as oldest; ties go A, B, C). Take the top row of that group with no line in seo/QUESTIONS.md; a group with no unused row is skipped. Seasonal next (Todd's go, Oct 26, 2026): a group D row with no line in seo/QUESTIONS.md whose Publish by date is 21 days away or less goes before the rotation, earliest date first; a D row whose date has passed still goes, the same day. Drafts come first: if seo/QUESTIONS.md has a page still marked draft, take the oldest one instead, whatever the day, and run it from step 4 (its spec exists).
- The paid product's data file (site/pages.json "data") and the matching free calculator (site/store.json calcProducts, or the row's calculator).

## Process (Executes)
1. Date from bash. `python3 tools/check_repo.py --preflight question-pages`. Re-fetch the row's URL (WebFetch) and confirm the question still reads as recorded; if not, skip the row with a note.
1b. Refill: add one new row to seo/BACKLOG.md, to the group with the fewest unused rows: a real question a buyer asked in public, fetched and read today (forums such as Jobber Community, The Grime Scene, Pressure Washing Resource, Seller Central; not Reddit, which the fetch tool can't read), mapped to one paid product, with URL and posted date, and not a repeat of any row or live page.
2. Search wording: no autocomplete fetches (coo/PIVOT.md bars them). WebSearch the question two or three ways and take the wording from the buyer's own post and the top results' titles for the title (under 60 characters before " | ProofNotFluff"), the H1 and the FAQ questions. Search the main wording (WebSearch) and read the top 3 results; note what each answers and misses.
3. Write a spec in site/pages.json, kind "question", "draft": true (the three Oct 22 specs are the model): the answer in the first 100 words; "tables" built from the data (stats rows such as gcRows, areaRows, catRows) or a dated primary source; "sections" for the subtopics the top results and suggestions cover; one worked example with real numbers as {placeholders} from the product's data (tools/question_site.py stats) or a dated primary source named in "sources"; one table or tiles block; one link to the paid product and one to a free calculator ("calculator"); the byline is built in. Length is what the question needs. No em or en dashes, no banned words (tools/legal_scan.py), no invented people, numbers or claims, no named failed restaurant.
4. `python3 tools/make_site.py`, `python3 tools/question_site.py`, `python3 tools/check_repo.py`: all exit 0.
5. Gates, each a fresh Agent subagent (model fable, else opus) that never saw the drafting:
   a. Copy and facts: every number traced to the data file or a dated primary source; dashes, banned words, legal lines, the Legal desk rules in legal/README.md. PASS or FAIL with lines.
   b. Search intent: does the page answer the question better than the current top 3 results? PASS or FAIL with reasons.
   c. `python3 tools/question_overlap.py <slug>` exits 0 (no other question page shares over 30 percent of its words in 8-word runs), and the search gate also compares the page with every live question page: same main search wording as a live page, or a thin rewrite of one, is a FAIL.
   One fix round per gate; a second FAIL stops the page and goes to Todd.
6. All of a, b and c pass: remove "draft", set "published" to today (YYYY-MM-DD), rebuild, check_repo exits 0, commit, push to main (pull --rebase once on a reject; never force). Add the row to seo/QUESTIONS.md with its group letter and one line to seo/RESULTS.md: date, slug, "published, gates PASS". If the built-in browser is reachable, ask Search Console (URL property https://proofnotfluff.com/) to index the new URL with URL inspection, Request indexing; else note "indexing not requested".
7. Fridays: the Search Console lines (impressions, clicks, average position, 28 days, per live question page) and the indexing requests are written by .claude/skills/index-request/SKILL.md, which runs at 7:40 am on Todd's PC in the built-in browser. This run does not read Search Console.

## Outputs (Writes)
- site/pages.json (one spec), docs/ through tools/make_site.py only, seo/QUESTIONS.md, seo/RESULTS.md.
- Message to Todd only on a second FAIL, a blocked source, or a failed check.
