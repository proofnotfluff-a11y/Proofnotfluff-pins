# Trial: a statement file instead of a bank link (Nov 13, 2026)

Not a lesson. It is not in videos/, not in the queue and cannot post: no format, gate, rule or anim.py line knows it.
Why it exists: Todd, live chat, Nov 13, 2026, 10:03 am: "Step up you animation game as well. Let's create a trial video when you are done." (coo/DECISIONS-2026-11-13.md). Topic picked from the heat read (../../heat/2026-11-13-results.json, topic claude-office-tools).

## What it is
A 29.5 s demo video, 1080 x 1920, no presenter and no voice (captions, one of our own music tracks, the studio's sound effects). Drawn at full resolution by code, not pixel art. Result first, then how, then the catch, then a card to save.

## Reads
- demo/statement.csv: a sample statement, 159 rows, 3 months, every merchant invented (demo/make_statement.py makes it, seeded).
- run/answer.md and run/runlog.txt: the real run. A fresh Claude Opus 5.5 agent was given the file and one question, "What am I paying for every month? Anything look off?", and wrote its answer 36.6 s later. Every number the video credits to the AI is in that answer.
- video/data.js: the rows and the answer's figures, as the scene reads them.

## Does
1. `python3 verify.py`: works every on-screen number out again from the statement and checks it against the answer (52 checks).
2. `python3 render.py <out_dir>`: draws 885 frames in a browser and encodes them (about 65 s), then lays the sound under. The MP4 stays off main.

## Writes
Nothing in the repo. Reviews so far: reviews/r0.json and reviews/r1.json.

## Where it stands
Round 1 failed the viewer check, the facts check (one caption) and the design review (4.31 against 4.6) after the one fix round. It waits for Todd's own watch and his word. What a first run got wrong and the second got right is in reviews/.
An earlier run with three questions grouped the gym as a subscription (10 for $216.89); the one-question run filed it under bills (9 for $167.89). Same file, two answers: the end card's "check them" is earned.
