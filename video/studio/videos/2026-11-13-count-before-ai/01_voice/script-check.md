# Script check: 2026-11-13-count-before-ai (playbook)

## Human test (viral-script step 8)
- Read-aloud: PASS. 18 sentences, longest 11 words; 89% at 10 words or fewer (16 of 18).
- Owner words: PASS. 0 banned words; trade nouns in the opening: "missed calls", "AI receptionist".
- Specific: PASS. "Fourteen missed calls in two weeks" in line 1; every number keyed in facts.json (all ours, EXAMPLE).
- Sameness: PASS. Opening "Fourteen missed calls in" differs from the last 6 openings (receptionist-myth opens "The demo says an AI receptionist": different first 4 words, held lesson).
- Do this week: PASS. Mark every missed call on a calendar for two weeks, circle the real jobs, then real jobs x what you clear a job, next to the quote's monthly price; the calendar and the board on screen and held.
- Ear test: PASS. Every sentence one breath; `anim.py script` PASS (125 words, 6 takes, 2 tags).

## The 12-point check (_shared/voice.md, playbook bands: 40 to 58 s, 100 to 150 words)
1. Drop-in: PASS. 11 words, one flowing sentence ("You missed fourteen calls, so do you need an AI receptionist?"; the two-sentence versions ran 138 and 128 wpm with long pauses at the full stop), a number and a trade object, no percent, no source, no call-out.
2. On-screen hook: PASS (planned). "14 missed calls. Need an AI?" style plate, 5 to 8 words, up from frame 0, held through the cuts to about 3.4 s, inside y 270 to 1250.
3. One idea: PASS. "Count your missed calls and what they're worth before you buy anything to answer them." (15 words)
4. Acted: PASS. The usual way is acted: the demo screen glowing, the pen going to the sign line, Snow shrugging at the unknown.
5. Facts: PASS. 14, 2, 4, $350, $1,400, $2,800, part 1 of 2, three options: all in facts.json; spoken forms match (fourteen hundred = 1,400; call it twenty-eight hundred = 2,800 rounded).
6. Artifact: PASS (planned). The board "4 jobs x $350 = $1,400" held 3 s or more, done by 65% of the runtime.
7. Proof: n/a for a playbook (no outside number by design; the check beat is the price next to the value).
8. Length: PASS. 125 words; planned 44 to 48 s with the end card.
9. Talk test: PASS. Contractions (don't, it's, That's, can't), "you" in most takes; no banned words; no dashes; no sentence over 20 words.
10. Voice markup: PASS. 2 tags ([matter-of-fact], [confident]), none soft; no CAPS words; no digits or symbols in the voice.
11. No tail: PASS. No turn line, no spoken ask.
12. Button: PASS. The last sentence is the rule and repeats "missed calls" from the hook; SCENE.sendLine names a role.
