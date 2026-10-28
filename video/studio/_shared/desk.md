# Desk: real things on screen

The rule from the gold standard: anything the words name that exists is shown for real. For a Rat check that means:

- **The City's numbers**: every count comes from the data file the brief names (for rats,
  `permits/rodents-chicago/weekly.json`), read by `anim.py` into `04_scene/data.js`. scene.js never types a number.
- **The map**: the 77 community areas from `site/geo/chicago-community-areas.json` (`anim.py kit` builds `_runtime/map.js`).
- **Our page**: `docs/chicago-rat-complaints/index.html`, captured at phone width by `anim.py grab` into
  `04_scene/assets/rat-page.png`. Capture it again for every video; never edit the capture.
- **The source line**: "City of Chicago 311 data" and the window ("30 days to Oct 26") on every data beat.

Never shown: an address, a block, a building, a business, a person, a resident's words, a request number.
