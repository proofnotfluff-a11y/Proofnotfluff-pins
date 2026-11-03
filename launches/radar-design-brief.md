# Restaurant Radar redesign brief (Todd, live chat, Nov 2, 2026, 6:18 pm)

Todd: "This design doesn't look nearly as sharp as the one shown. what will it take to achieve that?" He re-shared the
joebrunner.ai New Home Radar screen recording (46 s, 1206 x 2622); the live session read every frame at 2 fps plus full
size stills of the app part (about 17 to 36 s). The recording is never stored in the repo. This file is our own words.
Scheduled by Todd for Wed Nov 4, 2026, 10:01 pm Central.

## What makes his app look sharp (the mechanism, not the asset)
1. Map is the hero: a large dark navy panel, the county drawn with a glowing outline (thick, warm), thousands of small bright
   dots colored by stage, one pin for the shop. Legend is small caps under it.
2. Solid stat tiles: each a saturated block (deep blue, mint, orange), one huge number (about 56 px, heavy), a small caps
   label, one muted source line ("Census, Jan to Sep 2026"), a tiny 8 to 10 bar sparkline at the right, a progress bar on one.
3. One dark frame plus one hot accent: dark indigo left sidebar (Today, New houses, Map, Mail runs, Rules, Sources; then the
   map legend and a mini map), the active item and the main button in a warm gradient. Content area white.
4. Business page in tabs (Overview, Timeline, Postcard). Timeline is horizontal on a month axis (Jan to Nov): the line is
   colored by stage, big date plus label above each key point ("Apr 14 / Permit issued", "Oct 27 / Sold"), smaller dated
   dots below for the steps between, a glowing ring on the current point. A status pill top right ("Sold Oct 27").
5. The letter is a designed object: a postcard with an illustrated header band, very large headline, one line of copy,
   the sender line small at the bottom; a gradient button under it; a counter card ("126 postcards in Friday's run").
6. Trade picker is a menu of app-style icon tiles (rounded square, saturated color, white glyph) with a check on the chosen one.
7. Rules: one large rounded input with a thick colored outline; the parsed result is a solid colored pill with a check.
8. Table: tight rows, small caps column headers on a faint tint, solid green stage pills, bold address.
9. Almost no explanatory text. Labels only.
10. Motion: counters roll, dots appear, timeline draws, cursor moves; plus video zooms (camera work, not app).
Likely a mockup for the video: a 555 phone number and invented builder names. Tidy fake data looks cleaner than real City text.

## Our version (CONSTITUTION and formula.md: never his colors, lines, scenes or 3D style)
- Frame: our ink #1D2433 as the dark sidebar on desktop (top bar plus bottom nav stay on phone). One hot accent: our burnt
  orange #C8502F, used only on the active item and the primary button.
- Today: map becomes the hero (left, about 60% wide on desktop): ink panel, Chicago outline glowing in our orange, dots
  larger with a soft glow, shape plus color per stage (keep the 4 shapes; axe and color-blind safe), community areas faint.
  Right: solid tiles in ink, teal #2E6B66, ochre #B88A1E, orange (dark text on light fills where contrast needs it), each with
  a real 12-week sparkline of that stage's weekly counts and the "new this week" number.
- One business: tabs Overview, Timeline, Letter. Horizontal month timeline from our records (permit, license inspections,
  license, routine inspection or the 30-day rule, labelled), status pill top right. Letter shown as letterhead or postcard
  with a header band in our colors; Copy stays off until the member's details are filled.
- Trades: icon tile menu (7 trades). Rules: big outlined input; chips solid with a check; unread words stay shown.
- Cut words: stage help text into the Terms "How stages are set" and tooltips; no paragraph over one line on Today.
- Motion: count up on tiles, dots fade in by stage, timeline draws left to right, chips pop in; all off under
  prefers-reduced-motion.
- Honest gap: about 490 businesses (232 not open) against his 4,900 houses, so our map is sparser. Never pad it.
- Real data cases to design for: long legal names, missing ZIPs (permit only rows), long City permit text, shared addresses.

## Run plan (one session; stop and report if usage runs short)
1. Data: tools/radar_chicago.py output. The old private key died with the Nov 2 session: make a new RSA key pair (private
   key outside the repo, mode 600), commit only permits/radar-chicago/radar-seal.pub.pem, dispatch radar-chicago.yml, open
   list.sealed.json. Fallback: the preview artifact (slug 24f47c3a-7d75-45be-80c8-56d899dc9a18) embeds the Nov 2 list.
2. Build Today and One business in tools/radar_app.py (keep its selftest, letters from tools/radar_letters.py, copy gate).
3. Then Rules and Trades.
4. Gates: radar_app selftest, copy_gate --radar-live, 10 typed rules, axe WCAG 2.1 AA at 390 and 1280, verify_site with the
   flow (copy the preview into docs/ only for the check, then remove it), check_repo. Design director: a fresh opus agent
   scored against this brief's 10 points as the bar (not lead-list sites), pass = no score under 4 and average 4.61 or more.
5. Republish the private preview artifact (same slug), update launches/chicago-restaurant-radar.md and coo/HANDOFF.md.
   Still major under CONSTITUTION 2: nothing on proofnotfluff.com, no price, nothing sent. SendUserMessage Todd the link and
   PASS/FAIL lines.
