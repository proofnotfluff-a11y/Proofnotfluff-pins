# Trial: a statement file instead of a bank link (Nov 13, 2026)

Not a lesson. It is not in videos/, not in the queue and cannot post: no format, gate, rule or anim.py line knows it.
Why it exists: Todd, live chat, Nov 13, 2026, 10:03 am: "Step up you animation game as well. Let's create a trial video when you are done." (coo/DECISIONS-2026-11-13.md). Topic picked from the heat read (../../heat/2026-11-13-results.json, topic claude-office-tools).

## What it is
A 27.5 s demo video, 1080 x 1920, no presenter and no voice (captions, one of our own music tracks, the studio's sound effects). Drawn at full resolution by code, not pixel art. Result first, then how, then the catch, then a card to save.

## Reads
- demo/statement.csv: a sample statement, 159 rows, 3 months, every merchant invented (demo/make_statement.py makes it, seeded).
- run/answer.md and run/runlog.txt: the real run. A fresh Claude Opus 5.5 agent was given the file and one question, "What am I paying for every month? Anything look off?", and wrote its answer 36.6 s later. Every number the video credits to the AI is in that answer.
- video/data.js: the rows and the answer's figures, as the scene reads them.

## Does
1. `python3 verify.py`: works every on-screen number out again from the statement and checks it against the answer (53 checks).
2. `python3 render.py <out_dir>`: draws 826 frames in a browser and encodes them (about 65 s), then lays the sound under. The MP4 stays off main.

## Writes
Nothing in the repo. Reviews: reviews/r0.json, r1.json, r2.json.

## Where it stands
Three review rounds, three fails (reviews/r0.json, r1.json, r2.json). Round 2 ran on Todd's word of Nov 13, 11:44 am ("Fix, then post as a test"): the viewer watched to the end for the first time but still had open questions, the facts check failed one claim (the yearly total leaves out the gym, which the statement's own script counts as a subscription), design scored 3.88 against 4.6. Nothing was posted. It waits for Todd.
post-captions.md holds the words that would have gone out with it.
An earlier run with three questions grouped the gym as a subscription (10 for $216.89); the one-question run filed it under bills (9 for $167.89). Same file, two answers: the end card's "check them" is earned.
