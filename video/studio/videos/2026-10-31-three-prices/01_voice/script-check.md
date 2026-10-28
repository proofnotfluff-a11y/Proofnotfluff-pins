# Script check: Three prices on every quote (12-point check, research/runs/2026-10-28-script-playbook.md 6b)

Scored Oct 28, 2026 on script.md (225 words, 7 takes) against the stand-in timings (`anim.py estimate`, which runs slow at about 153 wpm)
and lesson 1's measured voice pace (250 words in 86.8 s). Lines marked "recheck" are re-scored on the real words.json after the voice workflow runs.

1 spoken hook: PASS 9 words ("One price on your quotes? The top shops quote three."), "your", stake = one price vs three, no greeting; ends 3.73 s on the slow estimate, about 2.9 s at lesson 1's measured pace (recheck on words.json, limit 3.0 s)
2 on-screen hook: PASS 7 words ("Top shops quote 3 prices. Not 1."), same idea as the spoken hook, settled on frame 0, held 0.0 to 3.2 s, y 290 to 808 inside the safe band, source on the card
3 one idea: PASS brief states it in 9 words ("put three prices on every quote: good, better, best"); all 7 takes serve it
4 stakes early: PASS "fifty-seven percent" spoken at 13.83 s (75 s slot limit 14 s); "top ten percent" at 10.47 s
5 facts: PASS 17 numbers in facts.json, each re-read on its page Oct 28 (ServiceTitan Top Performer Profile; Pinger et al. JEBO 128, 2016 on ScienceDirect; ACHR News Feb 10, 2026); spoken forms match the digits; scope words kept ("home jobs", "a German restaurant", "a heating and cooling trade group", "on average", "over a thousand"); nothing from the do-not-use list; three never claimed to beat one on close rate
6 payoff timing: PASS promise "Here's how you build them" at 4.00 s (limit 6 s); Good/Better/Best card complete at 47.90 s = 54% of 88.2 s (limit 70%)
7 copyable artifact: PASS the Good / Better / Best card spoken and on screen, full card held 47.90 to 52.80 s = 4.9 s (min 3 s)
8 pace and length: PASS 225 words (75 s band 200 to 240; this lesson's cap 230); longest sentence 19 words (max 20), average 8.0 (max 12); takes 15 to 51 words; per-take wpm recheck on words.json (target 160 to 195)
9 talk test: PASS every take has a contraction and "you"; 0 banned words; 0 em or en dashes
10 voice markup: PASS 1 tag per take (leaning in, matter-of-fact, curious, warmly, short pause, calm, confident), all on voice.md's allowed list; 0 CAPS words; 0 digits, $, %, /, & in voice text; no SSML
11 retention beats: PASS 34 cues, a visual change every 1.5 to 3.5 s except the artifact hold (card.best, 4.9 s, by design) and the end card (4.1 s incl. the 1.9 s tail); turn line "Here's the part people skip." at 52.80 s = 59% (band 55 to 75%)
12 ending: PASS one CTA, a send line naming a role ("Send this to whoever writes your quotes"); last sentence echoes the hook ("your quotes", "three prices"); no like/follow/comment/tag asks; LESSON 4 HUD and "Quote Clinic" on screen; captions.json carries the AI voice line and all three sources

Result: 12 of 12 PASS (1 and 8 re-scored on words.json after the voice run).

Notes for the gates
- Takes 2, 5 and 7 run 5 or 6 sentences because question-and-answer pairs ("Everyone else? Forty-one.") count as two; each take stays inside 9 to 18 s.
- ServiceTitan's "top performers" are the 90th revenue percentile in their trade and market: said "top ten percent", shown "Top 10% by revenue". Vendor data, correlational: the script calls it "a habit", not a cause.
- The survey caveat is spoken (take 6) and stays on screen from 69.3 s to the end of the section.
