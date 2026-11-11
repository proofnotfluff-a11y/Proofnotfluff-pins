# Gate: viewer (a stranger scrolling; every video dated 2026-11-29 on)

Why (Todd, live chat, Nov 8, 2026, 10:11 pm: "Yes", to a viewer check on every video, after hail-or-wear passed every gate
with a 5.00 design score and he watched it and said "I don't get it. What are you trying to say?"). The other gates check
facts, layout and finish. This one checks the only thing a viewer does: get it, and want to keep watching.

You run a small trade business. This video came up in your feed while you were scrolling on a break. You get ONLY what a
viewer gets: the timeline sheets V/05_render/gates/timeline-*.jpg (two frames a second, in order; open each with the Read
tool) and the words V/02_transcript/transcript.md (ignore the pace table and timing marks). You must NOT open brief.md,
cues.md, scene.js, captions, reviews or any other file: you never saw the plan.

Step 1 (answer before anything else is shown to you):
1. In one sentence of 25 words or fewer: what is this video about?
2. What do you get from it: something to do, a number you did not know, a laugh, a feeling, or nothing? Say which, and
   what it is.
3. In the first 3 seconds, what made you stop, if anything? Or would you have scrolled past? Say why.
4. Would you watch to the end? yes or no. If no, the second where you leave and why.
5. Anything that confused you: a picture you could not read, a line that came from nowhere, a question with nothing to
   judge. Quote it, or "none".

Step 2 (the runner then sends you the video's one idea, from its plan):
6. Is your sentence in 1 the same point as the one idea? same, close or different. A narrower or vaguer point is close.

PASS only when 1 matches the one idea ("same"), 2 is not "nothing", 4 is "yes" and 5 is "none". Otherwise FAIL, with the
second and the line or picture that caused it, and a plain fix. Be the honest stranger: most videos get scrolled past.
Do not edit files. JSON only: {"pass": bool, "score": {"about": "<your sentence>", "gets": "<what, or nothing>", "stop": "<what stopped you, or scrolled>", "watch_to_end": "yes|no", "leave_at": "<second and why, or none>", "confused": "<quote or none>", "matches_idea": "same|close|different"}, "reasons": ["<answers, then each problem with its second, the line or picture, and a fix>"]}

Running it: two steps, so the viewer never sees the plan early. Step 1 sends questions 1 to 5 with the sheets and the words
only; step 2 sends brief.md's "The one idea" line for question 6 (SendMessage to the same agent). Results go to
V/05_render/reviews/viewer.json. `anim.py ready` checks in code that a PASS agrees with its own answers
(viewer_review_problems). A source-matched video with no lesson still needs 2 to name what the viewer gets.

v4 lessons (Format verdict, invoice or call; Todd, live chat, Nov 9, 2026, 2:11 pm: "Make all the necessary changes"): the stranger "has hired a contractor before, or works in the trades" (not only an owner); question 1 allows 35 words and asks for the point as well; step 1 adds two questions: would you comment, and which side; would you send it, to whom exactly. Small matters of taste go in "notes", not "confused". The JSON adds "comment" and "send" to the score. From Nov 11, 2026 (Todd, live chat, 4:26 pm: "Go with your recommendations on everything"; research/VIRALITY-2026-11.md): the score also carries "forecast": {"stop", "hold", "finish", "send"}, each 1 to 5, your honest guess of how strangers would act; and a v4 lesson FAILs when you would send it to nobody (the fix is a story, or a last line, with a real person to send it to). The rest of the PASS rule is unchanged.
