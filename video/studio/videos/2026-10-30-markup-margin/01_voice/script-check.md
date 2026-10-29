# Script check: 2026-10-30-markup-margin (the playbook's 12 points, _shared/voice.md)

Re-scored Oct 29, 2026 (fix round after the script gate's 10 of 12) on the real voice: words.json and takes.json from the
voice run of take 5 (voice cc1473b03244), cues.json (74.73 s with the end card), scene.js, captions.json. Take 5 now reads
"[warmly] Here's the part people skip. Screenshot this one. ..." (the opening [short pause] dropped, one tag); takes 1 to 4
and 6 are the gated takes, unchanged.

1 spoken hook: PASS 10 words ("Mark up a job fifty percent. Is that your margin?"), "your" and "job", concrete stake, no greeting; last word ends 3.28 s (limit 3.6 s)
2 on-screen hook: PASS 6 words ("50% markup is NOT 50% margin"), settled on frame 0 and readable through the cuts (cover, bench close-up on "job" at 0.74 s, back out on "Is" at 2.12 s), held 4.0 s and cleared: the scene cuts on "Nope" (4.06 s, clamped to 4.0 s) to the blueprint shot, which carries the answer (ONE THIRD, = 33.3% margin) without the hook sentence until the math room at 8.13 s; y 268 to 618 inside the safe area
3 one idea: PASS 14 words in brief.md ("a 50% markup is a 33% margin; price from margin, not markup"); every take serves it
4 stakes early: PASS "a thousand dollars" at 9.44 s, "fifty percent" at 0.96 s; limit 12 s
5 facts: PASS 14 on-screen numbers resolve from facts.json (`anim.py data`), 11 computed facts recompute exactly from their formulas, JLC and Xero re-read with WebFetch Oct 28; spoken "about thirty-three percent" for 33.3%, "about sixteen hundred sixty-seven dollars" for $1,666.67; says "margin", never "profit"; nothing from the do-not-use list
6 payoff timing: PASS the answer "It's a third" lands at 4.78 to 5.28 s (ONE THIRD stamped on "third" at 5.02 s), "the math, and the fix" promised by 7.5 s; the core answer (33.3% margin) is spoken by 20.4 s (27%); the formula is spoken by 53.68 s (72%) and complete on screen by about 50.1 s (67%)
7 copyable artifact: PASS "Price = Cost / (1 - margin)" spoken and on screen from 49.64 s, held big at least 3.6 s by code, then on the board to the section's end at 61.63 s
8 pace and length: FAIL on take 5 only. 194 words, 74.73 s (limit 75 s), longest sentence 13 words. Per-take pace on takes.json 169, 172, 165, 175, 147, 171 wpm. Take 5's words run 161 wpm (37 words, 46.16 to 59.92 s), but its file carries a 1.39 s silent tail (the other takes 0.25 to 0.58 s), so the file pace reads 147, under the 150 floor; the first voicing of the new text read 148 (same tail), the one allowed re-roll 147
9 talk test: PASS every take has a contraction and "you"; 0 banned words; 0 em or en dashes
10 voice markup: PASS takes carry 2, 1, 1, 1, 1, 1 tags, all on the allowed list, none non-vocal; 1 CAPS word (DOUBLE, take 4); 0 digits, $, %, / or & in voice text; no SSML
11 retention beats: PASS 34 cues, a new shot on "Nope" (4.0 s) and the math room at 8.13 s; turn line "Here's the part people skip" at 46.16 s of 74.73 s (61.8%)
12 ending: PASS one CTA, the send line naming a role ("Send this to whoever sets your prices, even if that's you"); last sentence "Was the margin half, or a third?" echoes the hook; no like, follow, comment or tag asks; HUD "LESSON 3" and the RUN THE NUMBERS chip on screen; captions carry the sources and the formula, no AI voice line

Result: 11 of 12 on the real timings. Point 8 fails on take 5's file pace only (147 wpm, a 1.39 s silent tail after "dollars."); its spoken pace is 161 wpm.
