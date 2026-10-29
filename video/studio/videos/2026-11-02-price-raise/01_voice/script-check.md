# Script check: Raise your prices; most trades already did (12-point check, research/runs/2026-10-28-script-playbook.md 6b)

Scored Oct 28, 2026 on script.md (200 words, 7 takes) against the stand-in timings (`anim.py estimate`, 82.7 s, which runs
slow at about 145 wpm) and the measured pace of earlier lessons on Todd's voice (156 to 173 wpm). Real voice expected 72 to
79 s (lesson 9: 195 words, 76.5 s). Lines marked "recheck" are re-scored on the real words.json after the voice workflow runs.

1 spoken hook: PASS 10 words ("Eighty-three percent of HVAC companies raised their prices last year."), trade noun, stake = the 83% and "Did you?", no greeting. Recheck on words.json, limit 3.0 s
2 on-screen hook: PASS 8 words ("83% of HVAC companies raised prices last year."), the big 83% on the map and the panel lines, settled on frame 0; source on the card (Jobber survey, 1,050 home service owners, 2025)
3 one idea: PASS brief states it in 17 words; all 7 takes serve it
4 stakes early: PASS "Eighty-three" at 0.15 s (limit 14 s)
5 facts: PASS 14 numbers in facts.json, each re-read on its page Oct 28 (Jobber 2026 Home Service Trends Report; BLS ECI June 2026, Table 8); scope words kept ("last year", "inflation", "half named labor", "install and repair workers", "all workers", "in the year to June"); trade evidence only; the 1986 non-trade study is gone
6 payoff timing: PASS promise "Here's the note that tells your customers" at about 5.3 s on the estimate (limit 6 s, recheck); the full note complete at 116 of 200 words = 58% (limit 70%)
7 copyable artifact: PASS the three-line price note, spoken and on screen (cues note.l1 to note.l3), held complete through note.skip and note.last (about 4 s on the estimate before the sweep, unchanged words after)
8 pace and length: PASS 200 words (75 s band 200 to 240); longest sentence 15 words; takes 19 to 35 words; per-take wpm recheck on words.json (target 160 to 195)
9 talk test: PASS a contraction in every take (Here's, That's, you've, doesn't, don't), you or your in every take but take 3, which is the numbers; 0 banned words; 0 em or en dashes
10 voice markup: PASS 1 tag per take (leaning in, matter-of-fact, curious, warmly, short pause, calm, confident); 0 CAPS words; 0 digits, $, %, / in voice text
11 retention beats: PASS 32 cues, a visual change every 1 to 4.4 s on the estimate; turn line "Here's the part people skip." at 116 of 200 words = 58% (band 55 to 75%)
12 ending: PASS one CTA, a send line naming a role ("Send this to whoever writes your quotes"); last words echo the hook ("raise yours", "raised their prices"); no like/follow/comment asks; captions carry the AI voice line and both sources with URLs

Result: 12 of 12 PASS (1, 6 and 8 re-scored on words.json after the voice run).

Notes for the gates
- Jobber's shares are per trade among 1,050 surveyed owners (Dec 2025, Conjointly); "last year" is the page's word. The 72% is said "inflation" (the page text); the chart's "inflation and material costs" label is not relied on.
- BLS: "Installation, maintenance, and repair" 3.7% and "All workers" 3.2% (civilian wages and salaries, 12 months ending June 2026). The construction row (3.9%) includes farming, fishing and forestry, so it is not said.
- "Jobber sells software" checked on getjobber.com ("home & commercial service software"). The note, "the first of next month", and "raise the next job, never the one on your calendar" are examples and advice, tagged EXAMPLE on screen.
