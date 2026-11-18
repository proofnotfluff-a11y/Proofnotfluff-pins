# Gate: pick (a fresh listener, two scripts, no labels; every `told` lesson)

Why (Todd, live chat, Nov 18, 2026, 9:07 am, after watching 2026-12-04-dead-or-150: "the script was kind of very robotic,
very uninteresting"; 9:20 am: "Go"; coo/DECISIONS-2026-11-18.md; BUILD-2026-11-18.md step 5). The other gates say a
script is true and clean. This one asks the only thing a listener decides: would I keep listening to this one or the
other one.

The benchmark is 2026-12-02-took-it-back (V/01_voice/script.md, its heading line dropped): our best held lesson
(Instagram average watch 52 s of about 76 s, 69%; research/metrics/2026-12-02-took-it-back.json, read Nov 18). It stays the benchmark until a `told` lesson
beats that Instagram average watch at 72 h on 200 or more views; then that lesson's script takes its place, logged in
that day's coo/DECISIONS file.

## The runner
1. Take our script.md and the benchmark's. Drop each heading line, every [bracket] tag and any NOTE line, so only the
   spoken words remain.
2. Flip a coin (`python3 -c "import random; print(random.choice('AB'))"`): that letter is ours. Write the two as
   "Script A" and "Script B", each sentence numbered (s1, s2, ...).
3. Send them to a fresh Opus agent that never saw the build, with the prompt below and nothing else: no brief, no
   facts, no names of files, no hint which is ours.
4. Write its JSON to V/05_render/reviews/pick.json, add "ours": "<A or B>", and set "pass" by the rule below.
   `anim.py ready` checks that a PASS agrees with the answers (pick_review_problems).

## The prompt
You are scrolling on a break. Two people tell you a story, one after the other. Read each one aloud at talking pace.
You did not ask for either and you can walk away at any sentence.
1. Which would you keep listening to: A, B, or tie (you could not choose)? Say why in one sentence each.
2. For each script, the sentence where you would stop listening (its number), or "none" if you would hear it to the end.
   Say why you would stop there.
3. One line from each that sounds like a real person talking, and one that sounds like a script or an ad (under 15 words
   each).
Do not edit anything. JSON only: {"score": {"keep": "A|B|tie", "stop": {"A": "s<n>|none", "B": "s<n>|none"}, "real": {"A": "", "B": ""}, "scripted": {"A": "", "B": ""}}, "reasons": ["<why for 1 and 2>"]}

## PASS
PASS only when "keep" is ours or "tie", and "stop" for ours is "none". Otherwise FAIL: the fix is the script (the
sentence it stopped at, and the "scripted" line), rewritten in the same voice and read again by read-aloud before the
next pick. At most 2 fix rounds, then the lesson is shelved (prompts/README.md "v4"). Faults go in LEARNINGS.md.
