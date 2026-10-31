# Script check: 2026-11-12-missed-call-text (playbook; viral-script human test and the 12-point check in _shared/voice.md)

Scored Oct 31, 2026 by the builder on script.md (125 words, 5 takes, 15 sentences; take 2 rewritten after it read 137 wpm on fragments) before the voice. Timing lines are
re-measured on the real words.json. The script gate should re-score it blind.

## The human test (viral-script step 8)
- Read-aloud: PASS longest sentence 17 words (bar 20); 9 of 15 sentences (60%) 10 words or fewer (bar 60%).
- Owner words: PASS 0 banned words; trade nouns in the opening: "missed-call text", "job".
- Specific: PASS "a hundred sixty characters" in line 1; every number (160, 70, 102, part 1 of 3, 3 parts, 2 segments)
  has a facts.json key (twilio.* or example.*).
- Sameness: PASS opening "Your missed-call text gets" differs from the last 6 openings ("HVAC owners, most of",
  "Estimate's done, and they", "A move-out clean quote", "The demo says an", "This deep clean quote", "One call rings two").
- Do this week: PASS write the text (who you are, sorry I missed your call, one question that books it), count it under
  160, no emoji, no curly quotes; the example text on screen and held, with its count.
- Ear test: PASS every sentence fits one breath (average 8.3 words); `anim.py script` PASS (2 tags, no "about").

## The 12-point check (format bands from _shared/formats.md: playbook 40 to 58 s, 100 to 150 words)
1 drop-in: PASS 12 words, one flowing sentence ("Your missed-call text gets a hundred sixty characters to book the job."), an object with a number, no percent, no source, no call-out, no greeting
2 on-screen hook: PASS planned "160 characters to book the job." and "PART 1 OF 3", settled on frame 0, held to about 3 s, in the safe area (measured by `anim.py hook`)
3 one idea: PASS 13 words in brief.md; every beat serves it
4 acted: PASS the usual paragraph is shown on a clipboard and stamped NO NAME, NO QUESTION, not explained to camera
5 facts: PASS 160 and 70 from Twilio's table, the emoji and curly quote switch, split and per-segment billing; 102, 3, 1 of 3 and 2 are example.* (EXAMPLE on screen)
6 artifact: PASS the exact text, spoken in take 3 and on a big card held 3 s or more, done by about 55% of the runtime
7 proof: PASS one sourced number after the fix (160 to 70), the tag "Twilio docs: How long can a message be?" on screen while it is said
8 length: PASS 125 words (100 to 150); runtime measured after the voice (40 to 58 s)
9 talk test: PASS "you" or "your" in takes 1, 2, 3, 5; contractions none needed in the short takes, "Twilio's" in 4; 0 banned words; 0 em or en dashes; no sentence over 20 words
10 voice markup: PASS 2 tags ([matter-of-fact], [confident]), none soft; 0 CAPS words; no digits, $, %, / or & in the voice
11 no tail: PASS no turn line, no honest note, no spoken send, save, like, follow or comment ask
12 button: PASS last sentence "Keep it plain, and keep it under a hundred sixty." repeats "a hundred sixty" from the hook and names part two before it; SCENE.sendLine "Send this to whoever answers your phones."
