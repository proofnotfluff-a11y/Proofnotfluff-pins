# Script check: 2026-10-30-markup-margin (the playbook's 12 points, _shared/voice.md)

Scored Oct 28, 2026 on script.md, the stand-in timings (`anim.py estimate`: 194 words, 77.3 s), cues.json, scene.js, lint and
captions.json. The stand-in runs slow by design (144 to 160 wpm); lesson 1's real takes ran 159 to 197 wpm. Points 1 and 8
are timed on the stand-in and must be re-scored on the real words.json after the voice workflow runs.

1 spoken hook: PASS 10 words ("Mark up a job fifty percent. Is that your margin?"), "your" and "job", concrete stake, no greeting; ends 3.6 s on the stand-in, about 2.9 s at take 1's real pace in lesson 1 (197 wpm); re-score on words.json
2 on-screen hook: PASS 6 words ("50% markup is NOT 50% margin"), settled on frame 0, held 3.0 s, y 380 to 830 inside the safe area, lint clean
3 one idea: PASS 14 words in brief.md ("a 50% markup is a 33% margin; price from margin, not markup"); every take serves it
4 stakes early: PASS "a thousand dollars" at 10.5 s (stand-in), "fifty percent" at 1.2 s; limit 12 s
5 facts: PASS 14 on-screen numbers resolve from facts.json (`anim.py data`), 11 computed facts recompute exactly from their formulas, JLC and Xero re-read with WebFetch today; spoken "about thirty-three percent" for 33.3%, "about sixteen hundred sixty-seven dollars" for $1,666.67; says "margin", never "profit"; nothing from the do-not-use list
6 payoff timing: PASS the answer "It's a third" lands at 5.0 s, "the math, and the fix" promised from 5.6 s; the core answer (33.3% margin) is complete at 22.3 s (29%); the formula artifact finishes at 58.0 s (75%) on the stand-in
7 copyable artifact: PASS "Price = Cost / (1 - margin)" spoken and on screen, held big 3.9 s (stand-in, at least 3.6 s by code), then on the board to the section's end (13.7 s in all)
8 pace and length: PASS 194 words (60 s band 160 to 195; asked 150 to 220), longest sentence 13 words, average 6.5; per-take pace is 144 to 160 wpm on the stand-in only, so the real check (160 to 195 wpm) waits on words.json
9 talk test: PASS every take has a contraction and "you"; 0 banned words; 0 em or en dashes
10 voice markup: PASS takes carry 2, 1, 1, 1, 2, 1 tags, all on the allowed list, none non-vocal; 1 CAPS word (DOUBLE, take 4); 0 digits, $, %, / or & in voice text; no SSML
11 retention beats: PASS 34 cues, median beat 2.3 s, 1 gap over 4 s on the stand-in (close.echo to the end, 4.2 s, the final card); turn line "Here's the part people skip" at 50.6 s of 77.3 s (65%)
12 ending: PASS one CTA, the send line naming a role ("Send this to whoever sets your prices, even if that's you"); last sentence "Was the margin half, or a third?" echoes the hook; no like, follow, comment or tag asks; HUD "LESSON 3" and the RUN THE NUMBERS chip on screen; every caption carries the AI voice line, the sources and the formula

Result: 12 of 12 on what can be scored before the voice; points 1 and 8 re-scored on the real words.json.
