# Script check: Book the call, don't just answer it (12-point check, research/runs/2026-10-28-script-playbook.md 6b)

Scored Oct 28, 2026 on script.md (195 words, 7 takes) against the stand-in timings (`anim.py estimate`, 78.9 s, which runs slow at
about 148 wpm) and the measured pace of lessons 1 to 8 on Todd's voice (156 to 173 wpm; lesson 5, the same length, 213 words in
74.6 s). Real voice expected 68 to 75 s. Lines marked "recheck" are re-scored on the real words.json after the voice workflow runs.

1 spoken hook: PASS 9 words ("Plumbers, top shops book sixty-two percent of lead calls."), trade noun, stake = 62 vs 39 (next 2 words), no greeting; ends 3.70 s on the slow estimate, about 3.0 to 3.2 s at lessons 1 to 8's pace (lesson 4's 9-word hook: 3.73 estimate, 2.9 real). Recheck on words.json, limit 3.0 s
2 on-screen hook: PASS 7 words ("Top shops book 62% of lead calls."), same idea as the spoken hook, settled on frame 0 (cues.md hook), held 0.0 to 3.97 s (estimate) before the next beat changes the screen; source on the card. Safe-area placement checked at the scene stage (lint)
3 one idea: PASS brief states it in 13 words ("ask every lead caller to book, with two times to pick from"); all 7 takes serve it
4 stakes early: PASS "sixty-two" spoken at 1.77 s and "Thirty-nine" at 5.05 s (limit 14 s for a 75 s slot)
5 facts: PASS 12 numbers in facts.json, each re-read on its page Oct 28 (ServiceTitan Top Performer Profile, May 19, 2026; Invoca Home Services Lead Conversion Benchmarks Report 2026, Jul 2026; ServiceTitan HVAC call scripts, Feb 13, 2024); spoken forms match the digits; scope words kept ("lead calls", "everyone else" for "the rest", "top ten percent by revenue", "probably", "often", "home service businesses", "don't ask leads to buy or book the job", "a ServiceTitan sample script"); trade evidence only; nothing from the do-not-use list (the 2022 post's $3 million and 42% left out)
6 payoff timing: PASS promise "Here's the line that books yours" starts 5.94 s on the estimate (about 5.3 s real; limit 6 s, recheck); the full booking script complete at 48.77 s = 60% of 80.8 s (limit 70%)
7 copyable artifact: PASS the three-line booking script, spoken and on screen (cues ask.l1 to ask.pick), the full card held 48.77 to 52.61 s = 3.8 s on the estimate, about 3.4 s real (min 3 s): the turn line changes only the header band
8 pace and length: PASS 195 words (75 s band 200 to 240 and 60 s band 160 to 195: sits at the join, expected 68 to 75 s); longest sentence 19 words (max 20), average 7.2 (max 12); takes 15 to 41 words; per-take wpm recheck on words.json (target 160 to 195)
9 talk test: PASS every take has a contraction (That's, Here's, don't, It's, isn't) and you or your; 0 banned words; 0 em or en dashes
10 voice markup: PASS 1 tag per take (leaning in, matter-of-fact, curious, warmly, short pause, calm, confident), all on voice.md's list; 0 CAPS words; 0 digits, $, %, /, & in voice text; no SSML
11 retention beats: PASS 35 cues, a visual change every 1.4 to 3.8 s on the estimate (2.0 to 3.4 s at real pace except the 1.4 s header flip ask.two); turn line "Here's the part people skip." at 49.17 s = 61% (band 55 to 75%)
12 ending: PASS one CTA, a send line naming a role ("Send this to whoever answers your phone"); last sentence echoes the hook ("book", "call"); no like/follow/comment/tag asks; LEAD CLINIC / LESSON 9 chip on screen (hook.line); captions.json carries the AI voice line and all three sources with URLs

Result: 12 of 12 PASS (1, 6 and 8 re-scored on words.json after the voice run).

Notes for the gates
- ServiceTitan's "top performers" are the 90th revenue percentile in their trade and market segment: said "top ten percent by revenue", shown "Top 10% by revenue". "The rest average 39%": said "Everyone else? Thirty-nine." Vendor data, correlational: take 6 says "a pattern, not proof".
- "Probably not your marketing" and "often the first minute" keep the page's hedges ("probably", "often"); "first minute" = the page's "first 60 seconds", shown as the page has it.
- Invoca's 55% is a highlight tile with no paragraph, period or business count on the page: said with "found" and the page's words, never "never ask" or "most".
- "A ServiceTitan sample script does it too. Mornings or afternoons?" is the Expired Memberships script's step 6 ("Are mornings or afternoons better for you?"): it backs offering a choice, not a lead-call result.
- The booking script, the water heater, today at 2 and tomorrow at 9, and Friday are examples (tagged on screen).
