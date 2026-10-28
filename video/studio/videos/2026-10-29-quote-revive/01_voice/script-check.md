# Script check: 2026-10-29-quote-revive (playbook 6b, 12 points)

Scored Oct 28, 2026 on script.md, brief.md, cues.md and the scene. Times are from `anim.py estimate` (stand-in word timings,
about 155 wpm, slower than Todd's voice: lesson 1 measured 159 to 197 wpm per take). Points 1 and 8 carry a timing part
that only the real voice can settle: re-score them on Whisper's words.json after the voice workflow runs.

1 spoken hook: PASS 10 words ("Your quote's gone quiet? Skip "just checking in." Send this."), "your", stake = a quiet quote, ends on the promise, no greeting; ends 4.06 s on the estimate, about 3.0 s projected at lesson 1's measured take-1 pace (197 wpm); confirm at or under 3.0 s on words.json, else re-roll take 1
2 on-screen hook: PASS 6 words ("Quote went quiet? Send this text."), same idea as the spoken hook, settled on frame 0, held 0.0 to 3.0 s (3.0 s), y 286 to 892 (safe band 269 to 1248), host and dialog box hidden
3 one idea: PASS 12 words in brief.md ("When a quote goes quiet, text one yes-or-no question about the job."); every take serves it
4 stakes early: PASS "thirty-seven percent" spoken at 7.85 s (limit 14 s for the 75 s slot)
5 facts: PASS 4 sources re-read Oct 28 (ServiceTitan 37% vendor data said as "its data"; Management Science bot finding; Jobber cadence as "Jobber says"; Dean Jackson method, no numbers); spoken forms match facts.json (thirty-seven percent = 37; within two days = 2; a week = 7 days; a day or two = 1 to 2 days, from 24 to 48 hours); 0 do-not-use claims (the page's 64% / 72% / 87% left out); scope words kept ("estimates", "on the first visit", "fast replies", not "follow-ups")
6 payoff timing: PASS "Send this." named at 3.09 s (limit 6 s); the text is complete at 44.9 s of 86.7 s (52%, limit 70%)
7 copyable artifact: PASS "Still want that water heater swapped before winter?" spoken and typed on the phone at 60 px, with "Hi [name], it's [you]."; held from 43.9 s to 49.8 s (5.9 s)
8 pace and length: PASS 219 words (75 s band 200 to 240), longest sentence 18 words, average 7.6; per-take pace on the estimate 143 to 166 wpm (the estimator, not the voice); confirm 160 to 195 per take on words.json
9 talk test: PASS every take has a contraction and a "you" or "your" (7 of 7); 0 banned words; 0 em or en dashes
10 voice markup: PASS 1 tag per take, all allowed ([leaning in], [matter-of-fact] x2, [curious], [warmly], [short pause], [confident]); 0 CAPS words; 0 digits, $, %, / or &; no SSML; [name] placeholders are on screen only, never in the voice
11 retention beats: PASS 34 cues, longest gap between visual beats 3.8 s; turn line "Here's the part people skip." at 49.8 s of 86.7 s (57%, band 55 to 75%)
12 ending: PASS one CTA, a send line naming a role ("Send this to whoever follows up on your quotes."); last sentence echoes the hook ("Next time a quote goes quiet, you'll know what to send."); no like, follow, comment or tag asks; LESSON 2 in the HUD and THE TEXT chip on the hook card and the phone; captions carry the AI voice line and the sources

Result: 12 of 12 on the script; points 1 and 8 re-checked on the real word timings before render.
