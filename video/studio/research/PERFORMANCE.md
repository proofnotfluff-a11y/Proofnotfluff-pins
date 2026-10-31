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
