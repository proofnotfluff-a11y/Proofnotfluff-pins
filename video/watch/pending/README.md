# Pending watch jobs

Jobs waiting for Gemini's free daily quota (20 requests, resets about 2 am Central). The workflow only reads
video/watch/jobs/, so nothing here runs on its own. The first run after the reset moves them with `git mv` into jobs/ and
pushes once, when no Video watch run is in progress (the Nov 8 push race), then deletes this folder's moved files.

- 2026-11-09-study-*.json (video-lab chat, Nov 8, 2026, Todd's ask: "Study what makes the 100K sources work"): the top 8
  PROVEN.md rows by views plus our best (missed-call-text) and worst (close-rate) public Shorts, one shared question so the
  answers compare. Rows 14, 15, 16, 17, 19 and 20 also give PROVEN.md their opening move and structure (items 4 and 7),
  so they replace the -r2 pattern jobs the Nov 8 lunch run planned: 10 requests, plus the -r3 sourceprints for rows 18
  and 21, is 12 of the 20.
- After the answers land: fill PROVEN.md's opening move, structure, on screen and forward columns for those rows, and
  add the study lines to research/STUDY-2026-11-08.md ("Gemini read" section).
