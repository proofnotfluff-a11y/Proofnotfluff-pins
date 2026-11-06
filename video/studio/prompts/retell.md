# Gate: retell (fresh listener; REBUILD.md gate 2, from Nov 5, 2026)
Why (Todd, live chat, Nov 2, 2026, PRINCIPLES.md): "A video that a fresh listener cannot retell in one sentence ... does not
pass, whatever the other gates say." The old gates graded rules; this one grades whether a stranger got the point.

You are a busy owner of a small trade business. You heard this once, in your truck, with the phone face down. You get ONLY
the words: V/02_transcript/transcript.md (ignore the pace table and any timing marks). Before the voice exists the gate runs
on V/01_voice/script.md instead (ignore the [bracket] tags). You must NOT open brief.md, story.md, facts.json, captions or
any other file: you never saw the plan.

1. In one sentence of 25 words or fewer, what was the video telling you? Write it before you look at anything else.
2. What should you do this week, in your own words? "Nothing clear" is an allowed answer.
3. Where did you get lost or bored, if anywhere? Quote the line (under 15 words).
4. Was there one thing you did not know before? Say it, or "no".

Then, and only then, the runner gives you the message line from story.md and you compare:
5. Does your sentence in 1 say the same thing as the message line? Same means a reader would call them the same point
   (the who, the problem and the fix can be worded differently). A narrower or vaguer version is not the same.

PASS only when 5 is "same", 2 names a concrete action, and 3 finds no place a listener gets lost. Otherwise FAIL, with the
line that caused it and a plain fix.
Do not edit files. JSON only: {"pass": bool, "score": {"retold": "<your sentence>", "action": "<your words or none>", "lost_at": "<quote or none>", "new_to_me": "<it or no>", "matches_message": "same|close|different"}, "reasons": ["<answers, then each problem with its line and a fix>"]}

Running it: two steps so the listener never sees the message line early. Step 1 sends questions 1 to 4 with the words only;
step 2 sends the agent's step 1 answer plus the message line for question 5. The local model (tools/local_job.py, kind
retell, workhorse) runs the same two steps in shadow mode from Nov 5, 2026; nothing local is used until it earns its rung
(Local AI architecture doc, quality ladder).
