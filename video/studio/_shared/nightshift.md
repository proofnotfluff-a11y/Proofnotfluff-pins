# The night shift: the box works while Todd sleeps

Todd, live chat, Nov 6, 2026, 10:08 pm: "Can you have the local ai work constantly throughout the night to build up
inventory?"; 10:16 pm: "Yes do it". Why: the box only works on jobs a cloud run hands it, so it sat idle every night,
and the real shortage is stories (after ask-chatgpt, 0 Ready, 2 leads unverified). The box cannot make a finished
lesson by itself: every gate is still a fresh Opus reviewer (CONSTITUTION 2) and every box answer is checked by Claude
against its source. What the night buys: tomorrow's runs start with the reading, extracting, drafting and pre-checks
done, and every night job is one more comparison toward the next rung (local.md).

## Evening slot (the 21:33 run): queue the night batch, last step before the end message
Spend at most 10 minutes on this. Never wait for an answer (`send` and `fetch` without --wait).
1. `python3 tools/local_job.py health`: stop local off and alive_at within the last 24 hours (the box writes it only when it
   answers), or skip the batch and say so in one line. A box that is down just leaves the jobs waiting; the morning sees "none".
2. Leads: each row under "## Leads" in research/STORIES.md (at most 3). Its primary record: when the page's host is on the
   box reader's list (pnf-local-jobs scripts/fetcher.py ALLOWED), a `fetch` job with urls; otherwise read it here with
   WebFetch (prompt: the page text word for word) and pass it as input to a `send` job, with every email address, phone number and person's name cut
   out first (the lane carries business fields only). Per lead, two jobs, model workhorse:
   - `extract`: every fact, number, date and quote under 10 words the story would need, each with the sentence it came
     from; schema items [{fact, kind, from_sentence}], plus missing: what the page does not say.
   - `draft`: a story.md draft in our words from that page only, by _shared/storycraft.md (rung 1, shadow).
3. The first lesson `anim.py tomake` lists that has 01_voice/script.md: `openings` (five openings, workhorse) unless one
   exists for these words; `retell` and `read-aloud` pre-checks if the current script round has none (rung 2).
4. Pulse: if research/pulse/ has no file dated tomorrow, one `extract` fetch job per 5 to 8 source pages the box can read,
   exactly as trade-pulse SKILL step 3 writes it, so tomorrow's pulse starts from it.
- Names: `<slug>-night-<kind>-<date>-r1`, date Chicago today, slug the lead's short name (for example `lead-fcc-optout`).
  At most 12 jobs a night (trial twins are added by local_job.py and do not count).
- One line in LEARNINGS.md: "<date> night batch: N jobs queued (kinds)".

## Morning slot (the 9:33 run): use the night's work, right after step 1 Record
1. `python3 tools/local_job.py night`. A job with status none or not ok: note it in one line and do that work on Claude
   when it is needed; never wait for the box.
2. Each ok answer is used under its job's rung (local.md): rung 1, Claude does the job too and compares; rung 2, Claude
   checks the answer against the source and fixes it. Log each as clean or not in LEARNINGS.md, and move rungs as local.md
   says. A lead whose extract checks out against its page goes through the story-desk SKILL to Ready with that reading;
   Claude still opens the primary record itself before a story is marked Ready.
3. Nothing a night job wrote is published, posted or sent, and no gate is skipped because of it.
