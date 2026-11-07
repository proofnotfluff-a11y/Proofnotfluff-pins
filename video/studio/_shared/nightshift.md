# The box is the workhorse: night shift and day queue

Todd, live chat, Nov 6, 2026, 10:16 pm: "Yes do it" (the night shift). Nov 7, 2026, 5:22 am, after night 1 kept the
box busy for 2 minutes: "Yes and to all your recommendations ... I want to be clear that the box is our work horse and we
should be heavily utilizing it on value add tasks." The rule: whenever useful work exists, the box has it queued.
Idle time costs little; what matters is cloud usage saved and work that would not happen otherwise. The box cannot
finish a lesson or a page alone: every gate is a fresh Opus agent (CONSTITUTION 2), every box answer is checked by
code or by Claude against its source, and nothing a box job writes is published, posted or sent.

## Every studio run, last step before the end message (at most 10 minutes; never wait for an answer)
1. `python3 tools/local_job.py health`: stop local off and alive_at within the last 24 hours, or skip and say so.
2. Fill the queue in this order, up to 60 jobs a run (trial twins are added by local_job.py and do not count). Skip a
   job whose name already has a job file. Names `<slug>-<kind>-<date>-r<n>`, date Chicago today; night jobs from the
   21 slot carry `-night-` in the slug.
   a. Question page draft (21 slot only): seo/LOCAL.md step 2 (one job; copy its answer to seo/box-drafts/ at the end
      of the run).
   b. Story finding (21 slot; 9 slot too when fewer than 2 stories are Ready): 6 to 10 `pulse-night-extract` fetch jobs,
      8 thread pages each (48 to 80 pages), on hosts the box reader allows (pnf-local-jobs scripts/fetcher.py ALLOWED).
      Find the pages: (1) thread links from the newest ok `pulse-feeds` answer (the forum feeds listed as working in
      video/studio/research/listen.json, read by the box; queue a new `pulse-feeds-<date>-r1` fetch job each 21 slot);
      (2) WebSearch site: queries only to fill up (low yield: on Nov 7 one of six forum hosts returned threads); skip
      pages already read (research/pulse/). Model workhorse; prompt: list every owner problem on each page;
      schema {items: [{problem (our plain words, under 200 characters), trade, quote_under_10_words, url (one of the
      pages given), date_on_page}]}. No person's name or username, no small business's name.
   c. Leads: each row under "## Leads" in research/STORIES.md (at most 3): its primary record read (fetch job when the
      host is allowed; otherwise WebFetch the page text word for word here, with emails, phone numbers and names cut,
      and `send` it), then `extract` (every fact, number, date and quote under 10 words a story would need, each with
      the sentence it came from; plus missing) and `draft` (a story.md draft from that page only, by storycraft.md).
   d. Lessons: for the first lesson `anim.py tomake` lists with 01_voice/script.md, `openings` unless one exists for
      these words, and `retell` and `read-aloud` pre-checks if the current round has none.
   e. Backtest: `python3 tools/box_backtest.py make` then `send` when tools/box_backtest.py pairs lists rounds with no
      replay yet (new Opus verdicts since the last make).
   f. Fill work, only after a to e: `python3 tools/permit_tags.py make --max 300` then `send` (untagged GC leads);
      and for each lesson waiting in the queue, `captions` variants (3 per platform, from its captions.json rules; the
      morning run checks them with the captions gate before anything uses them).
3. One line in LEARNINGS.md: "<date> <slot> box queue: N jobs (kinds)".

## Morning run (the 9:33 slot), right after step 1 Record
1. `python3 tools/local_job.py night --days 1`. A job with status none or not ok: note it in one line; do that work on
   Claude when it is needed; never wait for the box.
2. `python3 tools/pulse_merge.py`: code keeps only items whose url the box was asked to read and loaded, quotes of 10
   words or fewer, no contact details; writes research/pulse/night-<date>.json ranked by how many pages share the
   problem. The trade-pulse SKILL uses it in place of its own reading; Claude opens only the urls it keeps for the top
   problems before anything is Ready.
3. Leads: an extract that checks out against its page goes through the story-desk SKILL to Ready; Claude still opens the
   primary record itself before a story is marked Ready.
4. `python3 tools/box_backtest.py score` when replays came back: writes research/box-backtest.json. Report agree_pct and
   "box PASS where Opus FAIL" in the end message. Rung moves still follow local.md; the backtest is evidence for Todd.
5. `python3 tools/permit_tags.py merge`, then `sample --n 10` and check those 10 against their scopes; any wrong tag:
   say so in LEARNINGS.md and drop that job's tags (delete its lead ids from scope_tags.json). Tags are stored only;
   using them on a page or in outreach is a separate change.
6. Each other ok answer is used under its job's rung (local.md): rung 1, Claude does the job too and compares; rung 2,
   Claude checks it against the source and fixes it. Log clean or not in LEARNINGS.md and move rungs as local.md says.

## Measure (after 3 nights, then weekly, in the Sunday review)
Box jobs answered and hours busy, clean rate by kind, Ready stories added, question page drafts usable, backtest agree
rate, cloud minutes of the question-pages and studio runs before and after.
