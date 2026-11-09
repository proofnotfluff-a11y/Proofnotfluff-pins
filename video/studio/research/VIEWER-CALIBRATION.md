# Viewer gate calibration: does the stranger predict real viewers?

Written Nov 9, 2026, 11:05 am Central, before damage-or-not posted (11:37 am slot), so the test is set before any number exists. Todd's ask, live chat, Nov 9: "Once damage-or-not has numbers, compare its retention and drop-off point with the viewer gate's prediction, and log the result in LEARNINGS.md and the decisions file." No gate or rule changes here; this is a log.

## Lesson 1: 2026-11-26-damage-or-not (about 57 s with the end card)

The stranger's prediction (videos/2026-11-26-damage-or-not/05_render/reviews/viewer.json, calibration run Nov 8, before the five calls; the video posts as built under the old rules):
- P1 who stops: only roofers; any other trade owner scrolls at the start (the pixel house reads as a game).
- P2 where they leave: about 25 s, inside the held checklist card (20.0 to 33.5 s, unchanged while the voice reads it).
- P3 watch to the end: no. Other faults it named: a garbled frame at 19.5 s, a near-black frame at 49.0 s, a closing question at 51.4 s that asks for the call the video said not to make.

The test, read from research/metrics/2026-11-26-damage-or-not.json at the first read 24 h or more after posting, platform by platform, only where views are 200 or more (fewer: "too few to judge", read again at 72 h):
- P2 PASS: average watch time 20 to 30 s, or, where a curve exists (a Studio screenshot), the biggest drop after 3 s lands between 19 and 34 s. FAIL: average watch under 15 s (people leave before the card, so the gate missed an earlier exit) or over 35 s (the card did not lose them).
- P1 PASS: Instagram skip rate 35% or higher or YouTube viewed vs swiped 55% or lower (most strangers scroll). FAIL: skip rate under 26% (after-hours-robot's 26.0% is our best hold) or viewed vs swiped over 65%.
- P3 PASS: average watch under 50% of the runtime. FAIL: 70% or more.
- Verdict: the gate predicts well if P2 passes on the platform with the most views and no part fails; it predicts badly if P2 fails there. Mixed otherwise. One video is a hint, not proof: lesson 2 is the first lesson made under the five calls.

Result: (not yet; first read due on or after Nov 10, 11:37 am)
