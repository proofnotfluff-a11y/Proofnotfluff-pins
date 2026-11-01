# Script check: 2026-11-14-ai-night-quote (fix-this, AI lane; Nov 1, 2026)

## Five openings (viral-script step 4), read aloud at pace
1. "This eleven pm quote reply took under seven seconds. One thing's wrong." (r2, Nov 1: the first voice of "Eleven pm quote request, this reply took under seven seconds" ended at 4.1 s, past the 3.6 s bar, so the hook is one 9-word sentence with no pause) KEPT: the result first (C5), a number, and an open loop the lesson answers at about 70%.
2. "A move-out quote came in at eleven. You saw it at seven." (stuck moment; the held after-hours-reply's own opening, which Todd held as too thin)
3. "What's wrong with this reply? Hey, prices vary, give me a call." (fix-this classic, but no result by 3 s)
4. "Free AI wrote this quote reply in six seconds." (result, no moment, reads as hype)
5. "Your eleven pm quote request. Answered before your coffee." (no number, no loop)
Why 1 is stronger: it opens on the finished thing (lanes.md 6, standard C5: through Oct 31 most viewers left by 4 to 8 s on TikTok) and the loop "one thing's wrong" pays off on the honest check, the beat the AI lane exists for (lanes.md 4).

## Human test (viral-script step 8)
- Read-aloud: PASS. Longest sentence 11 words (bar 20); 16 of 17 sentences (94%) 10 words or fewer (bar 60%).
- Owner words: PASS. 0 banned words; trade noun in the opening: "quote request".
- Specific: PASS. "Eleven pm" and "under seven seconds" in the first 2 lines; every claim keyed in facts.json (demo, gemini, jobber, story).
- Sameness: PASS. First 4 words "This eleven pm quote" differ from the last 6 lessons' openings (grep of their script.md line 3).
- Do this week: PASS. Paste the next quote request into Gemini under the 4-line prompt; the prompt on the ITEM GET card, held 4 s or more.
- Ear test: PASS. Every sentence one breath; `anim.py script` PASS (93 words, 6 takes, 2 tags).

## The 12-point check (_shared/voice.md, fix-this bands: 25 to 42 s, 60 to 100 words)
1. Drop-in: PASS. "This eleven pm quote reply took under seven seconds." 9 words, trade noun, no percent, no source, no call-out.
2. On-screen hook: PASS (planned). "11 pm quote. / Reply in 7 seconds." 7 words on the cover plate at frame 0, held to 3.2 s, in the safe area (lint and hook check it after cues).
3. One idea: PASS. "Every quote reply needs a price and one question." (9 words); every beat serves it.
4. Acted: PASS. The usual lunch reply types into the phone and the customer's "booked" tick lands; the work order's two empty boxes stamp.
5. Facts: PASS. 26% (jobber.cleaningWithinHourPct), under 7 s (demo.seconds 6.6), 2 questions (demo.questionsAsked), free (gemini.freePrice 0), 50 words (demo.promptWordLimit), 11 pm (story). Spoken forms match.
6. Artifact: PASS (planned). The prompt card, word for word as run, from "Type this" (about 55% of the runtime) held 4 s or more.
7. Proof: PASS. Jobber's 26% after the guess, with the source tag on screen while said; the real reply with model and date.
8. Length: PASS. 93 words (band 60 to 100; cut from 100 after the first voice ran 43 s); target under 42 s with the end card (band 25 to 42).
9. Talk test: PASS. Contractions ("thing's", "they've", "It's") and "you/your" across takes; no banned words; no dashes; longest 11 words.
10. Voice markup: PASS. 2 tags ([matter-of-fact], [confident]), none soft; 0 CAPS words; no digits or symbols.
11. No tail: PASS. No turn line, no spoken honest-note label, no spoken ask.
12. Button: PASS. "Every quote reply needs a price and one question. Send that reply before your first job." echoes "quote" and "reply"; sendLine names a role.

## The bar (_shared/standard.md)
- C1 stakes: "By then, they've booked someone" (story cost, acted) plus Jobber's 26% within an hour.
- C2 metaphor: the work order with PRICE and QUESTION boxes.
- C3 save card: the prompt, ITEM GET, held 4 s or more.
- C4 open loop: "One thing's wrong" at about 3 s, answered "It asked two questions" at about 70%.
- C5 result by 3 s: the real reply card is on screen by 2.5 s.
- S1 mechanism: "No question, so nothing to text back."
- S2 real screen: Gemini's plan page ($0 a month with a Google Account) and the app's start page, addresses on screen.
- S3 this week: paste the next quote into Gemini with the prompt.
- S4 proof: every number in facts.json with a source read Oct 29 to Nov 1.
