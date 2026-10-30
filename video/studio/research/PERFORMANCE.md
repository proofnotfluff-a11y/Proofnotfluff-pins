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

Two signals need 3 lessons before a rule changes: one bad post is noise. A rule in `_shared/` or a gate changes only
when 3 lessons in a row show the same cause, and the change is logged in LEARNINGS.md with the numbers.

## Weekly (Mondays, the research step)
Rank formats, hook patterns and posting slots by median 72 h numbers. A posting slot that trails the other two by half or
more for two weeks moves (log it here and in video/config.json slots).

## Diagnosis log
| Lesson | Format | Slot | 72 h views (IG, TT, FB, YT) | Avg watch | Skip | Cause | Change made |
|---|---|---|---|---|---|---|---|
