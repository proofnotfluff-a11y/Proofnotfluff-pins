# Test: payoff first (lesson 3, markup vs margin, rebuilt Oct 29, 2026)

Asked: Todd, Oct 29, 2026, 7:42 pm, "Build it for tomorrow" (to: a cut that gives the payoff in the first 8 seconds,
everything else the same, posted in the next normal slot).

## Why
Instagram insights Todd sent Oct 29: lesson 5 (v2, let-me-think) 103 views, 9 s average watch, 59.6% skip; lesson 1
(first-reply) 114 views, 8 s, 67.3% skip; lesson 9 (book-the-call) 9 views, 9 s, 66.7% skip. Zero real likes, saves or
shares on any. Views flatten near 100 to 110 within 3 hours. The hook holds about 4 in 10 past the swipe; those leave at
about 9 s, before the v2 fix beat (12 to 26 s) delivers anything they can use.

## Assumptions, and what the data says about each
1. People leave at 9 s because nothing useful has arrived yet. Untested; this test checks it.
2. The hook is the problem. Not supported: skip rates of 60 to 67% are in a normal band for a cold account, and the
   lessons with different hooks all stop at 8 to 9 s.
3. The format (v1 vs v2) is the problem. Not supported: v1 (lessons 1, 9) and v2 (lesson 5) stop at the same 8 to 9 s.
4. A saveable answer earns saves and shares. Untested; zero saves so far means there is no saveable moment early enough.

## The one variable
The answer (the exact action and number a trade owner can use: divide the cost by 0.6, about $1,667, a 40% margin) is
spoken and on screen inside the first 8 seconds. Everything else stays Lead Clinic v2: a 9 to 12 word drop-in with no
percent or source, the usual way, why, one sourced proof, a button echoing the hook, the end card send line, the AI label,
40 to 50 s. Topic differs from the baselines (each lesson posts once, never a re-post); the lessons it is read against
also differ from each other, and all stop at 8 to 9 s.

## Read (48 hours after the Instagram post)
Instagram insights: views, average watch (baseline 8 to 9 s), skip rate (baseline 59.6 to 67.3%), saves, shares.
- Kept: average watch over 9 s, or any real save or share. Payoff-first becomes the v2 default (Todd's yes first).
- Not kept: watch at 9 s or under and no saves. Next single variable: the opening picture, then the topic.

## Record
- Built Oct 29, 2026 at commit 96fdfd87 (outputs 8105b7c). Answer action said at 3.56 s, price at 6.26 s, full answer
  line ends 8.22 s; board shows 0.6 by 4.5 s, $1,666.67 at 132 px by 5.5 s, MARGIN 40% by 7.5 s. 45.67 s long.
- Gates: facts PASS, facts-captions PASS r1, buyer PASS, render-critic PASS 0 faults, golden PASS r1 (post as is),
  design FAIL r1 4.43 (type capped at 4 by the shared dialog size; held for Todd). Not queued yet: the queue still
  pins the earlier cut (e8e05da) for this slot until Todd's word on the design hold.
