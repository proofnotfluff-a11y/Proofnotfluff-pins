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

## A lost line counts only when two listeners agree (from Nov 6, 2026, 6:04 pm)
Why (Todd, live chat, Nov 6, 2026, 6:04 pm: "Yes", to: a "lost at" line counts only when two fresh reviewers flag the same
moment, and a lesson that fails this gate 3 rounds in a row goes to the back of the line): on lsa-max-bid every reviewer
retold the message "same" for 24 script rounds, and each one named a different lost line. One listener's lost line is
noise until a second listener trips on the same moment.
- When turn 1's retell fails ONLY on lost_at (matches_message "same" and a concrete action), send the same words to a
  second fresh agent (model opus, turn 1 only, retell.md questions 1 to 4). Then run
  `python3 video/studio/anim.py lostmatch <slug> "<first lost_at>" "<second lost_at>"` on those same words.
  SAME: the line is real; fix it and the gate fails this round as before. DIFFERENT (or the second was lost nowhere): the
  lost-at part passes; record both quotes under parts.retell.second and carry on to turn 2 with the first agent.
- matches_message "close" or "different", or no concrete action, still fails at once: getting the point is a hard bar.
  Read-aloud and compare keep their own bars, unchanged.
- Every story.json written from now carries "rule": "lost-at-twice". `anim.py tomake` lists the lessons built but not
  queued in the order to work them: oldest first, but a lesson with 3 or more story FAILs in a row under this rule goes to
  the back, so the run starts the next lesson and the stuck one waits its turn.
