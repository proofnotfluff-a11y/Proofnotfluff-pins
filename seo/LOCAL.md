# Question pages on the local box

Todd, live chat, Nov 7, 2026, 5:22 am: "Yes and to all your recommendations ... I want to be clear that the box is our work
horse and we should be heavily utilizing it on value add tasks." Question pages were the largest daily cloud cost on the
site (about 28 minutes a run). The box writes tomorrow's first draft during the day and night; the 7:10 am run edits
instead of writing from nothing. Same ladder as the studio (video/studio/_shared/local.md): rung 1 shadow, rung 2 after
3 clean in a row. Every gate stays a fresh Opus agent; nothing the box writes is published without them.

## Rung now: 1 (shadow)

## Who does what (the question-pages task cannot reach the private box lane; the studio's Code task can)
1. End of each question-pages run (after step 6): pick tomorrow's row by the SKILL's own rules (rotation, seasonal,
   drafts first), as if it were tomorrow, and write seo/NEXT.json: {"date": tomorrow, "slug", "group", "question",
   "url", "product", "stats"} (stats: the stats key the spec will use). Commit it with the page. Nothing else.
2. The studio's 21:33 run (video/studio/_shared/nightshift.md, first job of the night): if seo/NEXT.json is for tomorrow
   and seo/box-drafts/<slug>.json does not exist, send one job, model workhorse, kind draft, name
   `qpage-<slug>-draft-<date>-r1`:
   - a fetch job with the row's url when its host is on the box reader's list (pnf-local-jobs scripts/fetcher.py
     ALLOWED, for example community.getjobber.com), so the box reads the buyer's post itself; otherwise `send` with the
     question as input.
   - the prompt carries the question, the product's name and what it contains, the {placeholder} names and values from
     tools/question_site.py stats for that stats key, and one live question spec from site/pages.json as the shape.
   - schema: {title (under 60 characters), h1, answer (under 100 words), sections [{h2, body}], faq [{q, a}],
     placeholders_used [names], claims_without_source [lines]}. System: never invent a number, a person, a business, a
     quote or a law; a number appears only as a {placeholder} from the stats given.
   As the run's last step, copy an ok answer's output to seo/box-drafts/<slug>.json (page text only, public, it becomes
   a public page) and commit it with the run's push.
3. Start of each question-pages run (after step 1): when seo/box-drafts/<today's slug>.json exists:
   - Rung 1: write the spec yourself as the SKILL says, then compare. Log one line below: sections usable as written,
     sections that needed a fix, invented facts (any number not a {placeholder}, any unsourced claim), clean (no
     invented fact and at least half the sections usable) or not.
   - Rung 2 (3 clean in a row, written here as "Rung now: 2"): start from the box draft, fix it, then the same gates.
   No draft: write it yourself and note "no box draft".

## Log (newest last)
- 2026-11-08, carpet-cleaning-leads-price-shoppers: no box draft (seo/NEXT.json did not exist before this run).
