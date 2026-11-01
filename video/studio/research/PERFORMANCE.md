# Performance: read every post, find the cause, change one thing

Todd, live chat, Oct 30, 2026: "Consistently monitor video performance and learn from each video. If something is not
working, diagnose the issue and improve." This replaces the Monday-only numbers read for the posting routine.

## Where we start (Instagram insights Todd sent, Oct 29, 2026)
| Lesson | Views | Avg watch | Skip rate | Likes, shares, saves |
|---|---|---|---|---|
| 1 first-reply (about 18 h) | 114 | 8 s | 67.3% | 0 (1 like was Todd's own) |
| 5 let-me-think (about 4.5 h) | 103 | 9 s | 59.6% | 0 |
| 9 (about 8 h) | 9 | 9 s | 66.7% | 0 |
Read: the problem is the first 3 seconds and the reason to share, not the posting volume. At about 45 s long, 9 s average
watch is about a fifth of the video. More posts multiply whatever a post does, good or bad.

## The daily read (the evening posting run, through Claude in Chrome, reading only)
For every lesson posted 24 h, 72 h and 7 days ago, write `research/metrics/<slug>.json` with one entry per platform and
age: views, average watch (s), percent watched or "viewed vs swiped away" (YouTube), skip rate (Instagram), likes,
comments, shares, saves, follows. Sources: Instagram professional dashboard insights, TikTok Studio analytics, YouTube
Studio Shorts analytics, Facebook Page reel insights. Read numbers only: never reply, like, change a setting or a post.
A sign-in prompt or a hidden number: write "hidden" and go on.

## Account health and reach (every evening; Todd, Oct 31, 2026, 11:58 am: "put measures in place to mitigate those
risks as much as possible", on being flagged for mass-produced content)
- The evening PC run also opens each account's own status page, read only: Instagram and Facebook "Account status"
  (Settings, or the Page's professional dashboard), TikTok "Account status" (Settings and privacy), YouTube Studio's
  dashboard and Earn (strikes, restrictions, "inauthentic" or "reused content" notices). It writes one videometrics doc,
  id `account-health.<YYYY-MM-DD>`, numbers only: per platform 0 (nothing flagged), 1 (any warning, strike, "can't be
  recommended", restriction or originality notice) or "hidden". Never click an appeal, a "learn more" that asks to act,
  or anything else; a sign-in prompt is "hidden".
- The recorder files it as research/metrics/account-health.json. A 1 on any platform: tell Todd that run, in one line
  with the platform and the words on the page (no names), and POSTING.md holds that platform until he answers.
- Reach collapse (the evening diagnosis, cloud): on one platform, the last 3 posts each under 20% of that platform's median
  24 h views of the 6 posts before them (under 10 views each when fewer than 6 exist). Tell Todd that day with the
  numbers and recommend 2 a day on that platform; volume changes only with his word (CONSTITUTION 2).

## Real time (Todd, live chat, Oct 31, 2026, 2:28 pm: "We don't need to wait until Sunday to examine video data and
implement changes. We should improve real time.")
- Every posting run (four a day) also reads the numbers of each lesson posted 2 h or more before that has no read in
  the last 6 h, on all four platforms, read only, the same way as the daily read below (videometrics doc
  `<slug>.<YYYY-MM-DD>T<HH>`). Instagram's early numbers (skip rate, average watch, views against "your typical reel")
  show by 2 to 3 h.
- Every recorder run (four a day) files those numbers and runs the diagnosis below on the newest read of every lesson
  under 72 h old, not only at 72 h. The first rule that fires is the cause.
- Act on one lesson for the next lesson's own choices (hook, format, stake, save card): the lesson made in that same run
  applies the change, and the diagnosis log names it. Change a shared rule (_shared/, a gate, a prompt) when 2 lessons in
  a row show the same cause (was 3), logged in LEARNINGS.md with the numbers.
- What works gets kept the same way: a lesson that beats "your typical reel" on skip and watch names what it did
  differently, and the next lesson keeps it.

## Diagnosis (each lesson at 72 h; one cause, one change)
Read the numbers top to bottom; the first rule that fires is the cause. Write one line per lesson in the table below.
1. Skip rate over 55% (Instagram) or viewed vs swiped under 60% (YouTube): **the opening.** Next lesson changes the hook
   pattern and the first frame; the viral-script 5-openings step must name why the new one is stronger.
2. Average watch under 35% of the length: **the middle.** Cut words (shorter format), more picture changes, answer sooner.
3. Average watch 35% or more but views flat under 300 after 72 h on every platform: **the topic or the packaging.** Test a
   different problem from IDEAS.md and a sharper first caption line.
4. Views fine, 0 shares and 0 saves: **nothing to keep.** Make the artifact more copyable (a line, a number, a formula).
5. Everything above passes: **a winner.** Note what it did in LEARNINGS.md and make the next lesson in the same format
   on a new problem (never a copy of the video).

One bad post is noise for shared rules: they change on 2 lessons in a row (Real time, above). A single lesson still
steers the next lesson's own choices.

## Weekly (Mondays, the research step)
Rank formats, hook patterns and posting slots by median 72 h numbers. A posting slot that trails the other two by half or
more for two weeks moves (log it here and in video/config.json slots).

## Diagnosis log
| Lesson | Format | Slot | 72 h views (IG, TT, FB, YT) | Avg watch | Skip | Cause | Change made |
|---|---|---|---|---|---|---|---|
| 2026-11-05-book-the-call (early read, 34 h) | v1 long, 77.5 s | Oct 29 11:23 am (pre 3/day) | 11, 85, 110, 11 | TT 4.7 s (6%), FB 1 s (2%) | IG hidden | Rule 1 unreadable (skip hidden); rule 2 fires: the middle. An average under 5 s on a 77 s video means most leave inside the opening. | None yet: 72 h read due Nov 1; one post is noise (3-lesson rule). |
| 2026-11-07-let-me-think (early read, 31 h) | v2, 42.5 s | Oct 29 1:43 pm (pre 3/day) | 103, 130, 11, 3 | TT 7.9 s (18%), FB 3 s (7%) | IG hidden | Rule 1 unreadable (skip hidden); rule 2 fires: the middle. The shorter v2 holds about 3x the share of the long cut on TikTok. | None yet: 72 h read due Nov 1; points toward the shorter v2 length. |
| 2026-11-11-lsa-missed-calls (early read, 2.7 h; Todd's screenshots) | two-shops, 50.1 s, Depth bank #1 | Oct 31 11:47 am (lunch) | IG 179 (others not read yet) | IG 18 s (36%) | IG 29.1% ("Lower") | Rules 1 and 2 pass (skip 29.1% vs 59.6 to 67.3% before; watch 36% vs about 20%). Rule 4 fires: 0 shares, 0 saves. What changed: a money stake in the hook plate and cover ("Google bills one shop."), a two-shop split, a real rule with a source. | Keep: stake on the cover and in the first line. Next lesson: a screen worth saving (the exact setting or checklist held 3 s). |
| 2026-10-28-first-reply (read 67 h, list views) | not named in brief | Oct 28 9:25 pm | 114, hidden, 38, 13 | not read | not read | Rules 1 and 2 unreadable (list views only). Under 300 on every platform at 67 h: rule 3 (topic or packaging) is the likely cause; confirm with watch numbers at the 72 h read. | Next lesson keeps a money stake on the cover (lsa-missed-calls, below). |
| 2026-11-05-book-the-call (read 53 h, list views) | v1 long, 77.5 s | Oct 29 11:23 am | 14, hidden, 113, 10 | not read (TT 4.7 s at 34 h) | not read | Rule 2 still the cause from the 34 h read (6% watched); views stalled since (FB 110 to 113). | No new change; the long v1 cut is retired already. |
| 2026-11-07-let-me-think (read 51 h, list views) | v2, 42.5 s | Oct 29 1:43 pm | 103, hidden, 13, 3 | not read (TT 7.9 s at 31 h) | not read | Rule 2 from the 31 h read (18%); no growth since (IG 103 to 103). | None new. |
| 2026-10-30-markup-margin (read 28 h, list views) | v2 | Oct 30 12:39 pm | 129, 180, 207, 21 | not read | not read | Rules 1 and 2 unreadable. Best FB and TT reach of the set so far; IG flat near 120 like the rest. | Watch read wanted at the next PC run. |
| 2026-11-04-close-rate (read 27 h, list views) | not named in brief | Oct 30 2:11 pm | 115, 87, 13, 30 | not read | not read | Rules 1 and 2 unreadable; IG flat near 115. | None new. |
| 2026-10-31-three-prices (read 21 h, list views) | not named in brief | Oct 30 7:22 pm | 111, 96, 31, 12 | not read | not read | Rules 1 and 2 unreadable; IG flat near 110. | None new. |
| 2026-10-29-quote-revive (read 7 h, list views) | not named in brief | Oct 31 9:41 am | 115, 88, 7, 22 | not read | not read | Rules 1 and 2 unreadable; IG at 115 by 7 h, the same ceiling as the others. | None new. |
| 2026-11-11-lsa-missed-calls (read 4.9 h, list views) | two-shops, 50.1 s | Oct 31 11:47 am | 480, 148, 6, 1 | IG 18 s (36%) at 2.7 h | IG 29.1% at 2.7 h | Rules 1 and 2 passed at 2.7 h; IG 480 at 4.9 h is about 4x every other lesson's IG at any age (103 to 129). Rule 4 still fires: 0 shares, 0 saves at the 2.7 h read. | Keep: money stake on the cover and the first line, two-shop split. The lesson made Oct 31 5:33 pm run applies it and adds a C3 save card held 3 s or more. |
| 2026-10-28-first-reply (72 h, full read Oct 31 evening) | not named, 88.7 s | Oct 28 9:25 pm | 114, 121, 38, 13 | TT 4.2 s (5%), FB 4 s (4%) | IG hidden; YT hidden | Rule 1 unreadable (skip and viewed vs swiped hidden); rule 2 fires: the middle (5% watched on an 89 s cut). | The lesson made Nov 1 (evening run) stays a 45 to 50 s clinic and answers by about 60% of the runtime. |
| 2026-10-30-markup-margin (32 h, full read) | v2 clinic, 45.7 s, object-number | Oct 30 12:39 pm | 129, 180, 207, 21 | TT 25.6 s (56%, best of any lesson), FB 4 s (8%) | IG hidden | Rule 1 unreadable; rule 2 passes on TT (56%), fails on FB (8%); views under 300 everywhere at 32 h (rule 3 is the watch at 72 h). 0 shares, 0 saves. | Keep: the 45 s clinic length and the object-number hook (the Nov 1 lesson is both). |
| 2026-11-04-close-rate (30 h, full read) | v1, 73.5 s | Oct 30 2:11 pm | 115, 87, 13, 32 | TT 3.4 s (5%), FB 2 s | IG hidden | Rule 2 fires: the middle. | Same as first-reply: long v1 cuts are retired (formats.md caps every format but case at 62 s). |
| 2026-10-31-three-prices (25 h, full read) | v1, 74.6 s | Oct 30 7:22 pm | 111, 97, 31, 15 | TT 7.8 s (11%), FB 1 s | IG hidden | Rule 2 fires: the middle. 1 save on IG and 1 on TT (the first saves on two platforms). | Shared rule check: rule 2 on 3 lessons in a row, all 73 to 89 s v1 cuts; the shared change (short formats) is already in place, so no new rule. The case format (70 to 92 s) is the one left at that length: next case lesson gets a watch read at 2 to 3 h before a second is made. |
| 2026-10-29-quote-revive (Nov 1 morning make, cloud; newest read 7 h, list views, no new read since) | not named in brief | Oct 31 9:41 am | 115, 88, 7, 22 | not read | not read | Rules 1 and 2 unreadable; no read newer than the Oct 31 7 h list views reached the log. | None new; a watch read wanted at 72 h (due Nov 3 9:41 am). |
| 2026-11-11-lsa-missed-calls (Nov 1 morning make; newest read 4.9 h, Oct 31) | two-shops, 50.1 s | Oct 31 11:47 am | 480, 148, 6, 1 | IG 18 s (36%) at 2.7 h | IG 29.1% at 2.7 h | Rule 4 still the newest cause: 0 shares, 0 saves. | Applied in 2026-11-14-ai-night-quote (AI lane): the save card is the exact prompt, held 4 s and more on the ITEM GET card and repeated in the caption; the result on screen by 2 s (C5). |
| 2026-11-13-count-before-ai (Nov 1 morning make; posted Oct 31 7:19 pm, about 14 h) | playbook | Oct 31 7:19 pm | no read yet | no read | no read | No read in the log (the PC runs read at 2 h and up; none filed for it). | None; read wanted at the next PC run. |
| 2026-11-12-missed-call-text (Nov 1 morning make; posted Nov 1 8:28 am, about 2 h) | clinic, standalone | Nov 1 8:28 am | no read yet | no read | no read | Too young to read (posted under 2 h before this run). | None. |
| All lessons under 72 h (Nov 1 lunch make, cloud, 1:25 pm): three-prices (66 h), close-rate (71 h), quote-revive (52 h), lsa-missed-calls (50 h), count-before-ai (42 h), missed-call-text (5 h) | as above | as above | no read newer than Oct 31 4 pm (videometrics holds none since; the scoreboard log has 0 uncommitted docs) | not read | not read | No new cause: the newest reads are the ones already logged. lsa-missed-calls (rule 4, 0 shares and 0 saves) stays the newest cause; the reads are 21 h stale. | Applied in 2026-11-15-three-fixes: a save card with the exact text to copy (C3) and the stake in the first line (C1); its test is length (about 29 s, quick-math). A watch read of missed-call-text and count-before-ai is wanted at the next PC run. |
