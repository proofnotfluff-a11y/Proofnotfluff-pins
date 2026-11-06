# Gate: story (one fresh reviewer for retell, read-aloud and compare; from Nov 6, 2026)
Why (Todd, live chat, Nov 6, 2026, 10:54 am: "Go with your rec", to merging the three story checks into one Opus reviewer
to cut cloud usage): the local box now pre-checks retell and read-aloud on every round (_shared/local.md), so one fresh
agent can carry all three checks. The bars are the same three files, unchanged: retell.md, read-aloud.md, compare.md.

Running it: ONE fresh agent (model opus) that never saw the build, in two turns, so the listener never sees the message
line early.
- Turn 1 (Agent call): the text of retell.md, questions 1 to 4, with the words only (script.md before the voice,
  transcript.md after). It may open no other file.
- Turn 2 (SendMessage to the same agent): question 5 with the message line from 00_story/story.md, then the whole of
  read-aloud.md on the same words, then, only after the render, the whole of compare.md (it may now open the files
  compare.md names).

When it runs: on script.md before any voice (retell and read-aloud parts), on the transcript after the voice (same), and
after the render (all three parts). Each run writes V/05_render/reviews/story.json; a later run nests the earlier one under
"earlier".

Do not edit files. JSON only: {"pass": bool, "parts": {"retell": <retell.md JSON>, "read_aloud": <read-aloud.md JSON>,
"compare": <compare.md JSON, or "not yet" before the render>}, "reasons": ["<part>: <fault and exact fix>"]}
pass is true only when every part that ran passes its own file's bar, and after the render all three must have run.
