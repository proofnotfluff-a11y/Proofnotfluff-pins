# Script check: Raise your prices; most trades already did (12-point check, research/runs/2026-10-28-script-playbook.md 6b)

Re-scored Oct 29, 2026 after the fix round: takes 2 (119 wpm) and 3 (145 wpm) were under the 150 floor and are rewritten
as tighter talk (same numbers; cleaning's 55% moved to the captions; the wage point said plainly). script.md: 221 words,
7 takes. Times are the stand-in words.json (takes 1, 4, 5, 6, 7 on Whisper's real timings; takes 2 and 3 estimated at 166
and 170 wpm), 80.3 s of voice. Lines marked "recheck" are re-scored on the real words.json after takes 2 and 3 are voiced.

1 spoken hook: PASS 10 words ("Eighty-three percent of HVAC companies raised their prices last year."), trade noun, stake = the 83% and "Did you?", no greeting. Recheck on words.json, limit 3.0 s
2 on-screen hook: PASS 8 words ("83% of HVAC companies raised prices last year."), the big 83% on the map and the panel lines, settled on frame 0; source on the card (Jobber survey, 1,050 home service owners, 2025)
3 one idea: PASS brief states it in 17 words; all 7 takes serve it
4 stakes early: PASS "Eighty-three" at 0.15 s (limit 14 s)
5 facts: PASS 14 numbers in facts.json, each re-read on its page Oct 28 (Jobber 2026 Home Service Trends Report; BLS ECI June 2026, Table 8); scope words kept ("last year", "inflation", "half named labor", "install and repair workers", "all workers", "in the year to June"); trade evidence only; the 1986 non-trade study is gone
6 payoff timing: PASS promise "Here's the note that tells your customers" at 5.48 s on the real take 1 (limit 6 s); the full note complete at 137 of 221 words = 62% (limit 70%), 49.3 of 80.3 s on the stand-in
7 copyable artifact: PASS the three-line price note, spoken and on screen (cues note.l1 to note.l3), held complete through note.skip and note.last (about 4 s on the estimate before the sweep, unchanged words after)
8 pace and length: PASS 221 words (75 s band 200 to 240); longest sentence 19 words (under 20); takes 19 to 49 words; takes 2 and 3 now run 2 and 4 sentences of 6 to 19 words instead of 5 and 6 short ones (the sentence gaps were what slowed them); per-take wpm recheck on words.json (target 160 to 195)
9 talk test: PASS a contraction in every take (Here's, That's, you've, doesn't, don't), you or your in every take (take 3: "your crew's pay"); 0 banned words; 0 em or en dashes
10 voice markup: PASS 1 tag per take (leaning in, matter-of-fact, curious, warmly, short pause, calm, confident); 0 CAPS words; 0 digits, $, %, / in voice text
11 retention beats: PASS 32 cues, a visual change every 1 to 5.2 s on the stand-in; turn line "Here's the part people skip." at word 138 of 221 = 62% (band 55 to 75%)
12 ending: PASS one CTA, a send line naming a role ("Send this to whoever writes your quotes"); last words echo the hook ("raise yours", "raised their prices"); no like/follow/comment asks; captions carry the AI voice line and both sources with URLs

Result: 12 of 12 PASS (1, 6 and 8 re-scored on words.json after the voice run).

Notes for the gates
- Jobber's shares are per trade among 1,050 surveyed owners (Dec 2025, Conjointly); "last year" is the page's word. The 72% is said "inflation" (the page text); the chart's "inflation and material costs" label is not relied on.
- BLS: "Installation, maintenance, and repair" 3.7% and "All workers" 3.2% (civilian wages and salaries, 12 months ending June 2026). The construction row (3.9%) includes farming, fishing and forestry, so it is not said. "So your crew's pay rose faster than average" is 3.7 against 3.2, the same table and window ("average" is the all-workers row).
- Cleaning's 55% (the lowest trade) is caption only since Oct 29: five percentages in 13 s was too many for the voice.
- "Jobber sells software" checked on getjobber.com ("home & commercial service software"). The note, "the first of next month", and "raise the next job, never the one on your calendar" are examples and advice, tagged EXAMPLE on screen.
