# Sets: full-screen game set pieces (`_runtime/sets.js`)

Todd, Oct 28, 2026: "You are cycling through the same scenery... Be creative and come up with new cool graphic motion
for each video." The four rooms (framing, blackboard, workshop, garage) stay; a lesson now picks its worlds from these
sets so no two lessons look alike. Rule of thumb: **at most one room-and-panel section per lesson; every other section
is a set, and no set repeats in two lessons in a row.**

## How a scene uses one
`sets.js` loads after `kit.js` (stage.html) and adds `k.sets` (alias `k.set`) to every kit object:

```js
mid: (k, T) => {
  const r = k.sets.scores({title: 'REPLY SPEED', t0: k.S('mid'), rows: [...], newAt: k.S('mid.record')});
  return {hostScale: 0.86};
},
```

- Every set draws the **whole frame** (sky to floor) and returns where its content lives, in frame units
  (`{area: {x, y, w, h}, ...}`), so scene text goes there and nowhere else.
- Times are seconds on the lesson clock: pass cue starts (`k.S('id')`) or word times, never typed numbers.
- Numbers come from `k.data` like everything else; a set only formats what it is given.
- Every move is whole low-res pixels on whole frames (`fr(t0)` frame counts, `ease()` slides rounded to pixels,
  Bresenham lines, stepped angles). No fractional zoom, no alpha fades of pixel art. Any frame renders on its own.
- **Frame 0 is the cover:** with `t0 <= 0` (and `at <= -0.3` for slides) a set is fully settled on frame 0.
- Blinks and color swaps stay at 2 a second or slower (the 3-flashes rule).
- Shared layout (low-res px, frame = x 3): content band y 84 to 270 full width; y 270 to 322 only right of x 96 (the
  host stands at x 36 to 92 from y 273); text ends by x 316 (frame 950, the Reel's buttons); y 322 to 417 is the dialog
  box's band (calm decor); y 417 down is floor scenery.
- `k.sets.van(x, y, {wheel})` and `k.sets.icon(name, x, y, scale)` are the shared sprites (icons: wrench, phone,
  clip, mail, star, coin, clock, horn, hammer), in low-res units.

## Transitions
`SCENE.transitions = {sectionId: 'levelselect' | 'dissolve' | 'gameover'}` picks the move into that section (the
player falls back to the room's own move, then blinds). All are 12 frames on the pixel grid like the room moves.
- `levelselect`: square tiles grow out of nothing in a diagonal wave, gold-edged while they grow. Use into a "next level" section.
- `dissolve`: a 4x4 ordered (Bayer) dither of 4-pixel blocks fills in and clears. Use between two calm sets.
- `gameover`: black closes from top and bottom to a white line that shrinks to nothing (a CRT switching off). Use
  once, into the close or after "this is what loses the job".

## The catalog
Still references: the harness renders four moments of each (`sheet-<name>.jpg`; times in the table under each entry).
Run it again any time from the scratchpad helper (`render.py`, copied from how `anim.py stills` opens the stage).

### 1. `street`: side-scrolling street level
For: the trip to the job, being first, "while they wait, you're on the way". Parallax in whole pixels: clouds at a tenth,
the skyline at a quarter, two-flats and frame houses at a half, the road at full speed, the picket fence at 1.5x; the van
bobs a pixel, its hubs turn, exhaust puffs. At `stopAt` it brakes over `stopDur` and the yard sign lands beside it with a hop.
`k.sets.street({t0, speed: 1, stopAt, stopDur: 0.8, sign: 'JOB', van: true})` -> `{area (the sky), van}`.
Do: one line or a panel in the sky, the stop on the payoff word. Don't: text on the houses; more than 4 s of scrolling.
Stills: 0.0 parked cover, 1.0 driving, 2.3 braking, 3.2 parked with the sign.

### 2. `dispatch`: dispatch board, pins and routes
For: where jobs are, a route, density, "3 calls in one neighborhood". A city grid with the river, a diagonal avenue, a
park and the lakefront (ripples step every 10 frames). Pins drop with a bounce and ping once; routes draw on pixel by
pixel with a van at the head, then their dashes march.
`k.sets.dispatch({pins: [{x, y, at, c}], routes: [{pts: [[x, y], ...], at, dur, c}]})` (0..1 map coords) ->
`{map, at(x, y) -> frame point, area (the strip under the map, right of the host)}`.
Do: 2 to 5 pins, route along streets (axis-aligned points). Don't: pins in the bottom-left corner (behind the host).
Stills: 0.0 empty board, 0.7 pins landing, 2.0 route drawing, 3.0 done.

### 3. `scores`: arcade high-score table
For: rankings, "who wins", a benchmark list, the viewer's own place. A cabinet with chasing marquee bulbs, black screen
with scanlines; rows slide in one by one and count up from 85%; the `hi` row gets a cursor and blinking initials (2/s);
NEW RECORD swaps colors (2/s).
`k.sets.scores({title, t0, gap: 0.3, count: 0.7, rows: [{name, value, prefix, suffix, dec, comma, hi, rank}], newAt, newText})`.
Do: 3 to 5 rows, short names (3 to 5 letters), units in the suffix. Don't: long labels; more than one `hi` row.
Stills: 0.0 empty table, 0.9 rows landing, 1.6 blink off, 2.6 NEW RECORD.

### 4. `boss`: the objection as a boss fight
For: handling an objection, "3 ways to answer X". The boss bobs a pixel; each argument hits: 2 white frames, knockback,
a slash, the damage number rising, a lag bar that catches up. At `defeatAt` it breaks into pixels and VICTORY stamps in.
The command menu lists the arguments with a cursor on the next one; used ones go grey.
`k.sets.boss({name, hp: 100, t0, hits: [{at, dmg, label}], defeatAt, winText, menu})` -> `{area (the menu), boss, hp}`.
Do: hits on the words that land each argument; 2 to 4 hits; labels under 18 characters. Don't: a boss for a person
(it is the objection, never the customer).
Stills: 0.0 full HP, 1.03 hit flash, 2.4 second hit, 4.2 defeated.

### 5. `register`: the till rings it up
For: price build-ups, add-ons, averages per ticket, "what a visit is worth". A receipt prints a line per item (the paper
grows up on whole pixels), a key goes down, a $ flag pops in the display and the total steps; TOTAL prints; the drawer
slides out and coins jump.
`k.sets.register({items: [{label, amount, at}], prefix: '$', dec, totalAt, openAt, totalLabel, displayLabel})` -> `{area, display, total}`.
Do: 2 to 4 items, labels under 10 characters. Don't: show a total the brief doesn't have (the set sums what you give it).
Stills: 0.0 cover, 1.0 two items, 2.3 total and drawer, 2.9 coins.

### 6. `calendar`: the month fills in
For: follow-up cadences, days to book, seasonality inside a month, "day 14". Days fill with a 2-frame dither then solid,
marks land with a 2-pixel drop (x, check, coin, fill); a gold week frame slides row to row.
`k.sets.calendar({month, year, start, days, fills: [{day, at, c, mark, mc}], run: {from, to, at, every, c, mark}, weeks: [{row, at}]})`
-> `{area (right of the host, under the grid), grid, cell(day) -> [x, y, w, h]}`.
Stills: 0.0 blank month, 0.8 a run of x's, 1.7 the check and week frame, 2.5 the coin.

### 7. `flaps`: split-flap departures board
For: a short table that "updates": response times, callback odds, before/after. Each letter flips 3 to 7 times (top
half falls first, 2 frames a flap) and lands left to right; values in the `hi` row are gold. A train rolls along the title.
`k.sets.flaps({title, cols: 12, rows: [{label, value, at, hi}]})` (4 rows max) -> `{area, board}`.
Do: rows of 12 characters or fewer, value at the right. Don't: sentences.
Stills: 0.0 blank board, 0.5 first row flipping, 1.0 rows landing, 2.2 settled.

### 8. `chat`: messaging app in the truck
For: text replies, scripts, a lead coming in. A phone in a dash mount (the road rushes in the windshield, the air
freshener swings), app header with avatar, wallpaper, bubbles that slide up 8 pixels, typing dots, read ticks, a
notification that drops in and back up.
`k.sets.chat({who, clock, msgs: [{me, text, at, typing, read}], notify: {text, at, dur}})` -> `{area (the chat), phone}`.
Do: 3 to 4 short messages; type a message on the words that say it. Don't: more than 6 lines in a bubble.
Stills: 0.0 empty chat, 0.5 notification, 2.3 typing dots, 3.4 reply in.

### 9. `weather`: TV weather map and the season strip
For: season demand, "AC season", when calls spike. A region map with the lake and Chicago's star; fronts sweep across
(cold: teeth, warm: domes); sun rays step, snow and rain fall; the lower third has the title and 12 monthly bars that grow.
`k.sets.weather({title, fronts: [{kind, at, dur, x0, x1}], icons: [{kind: 'sun'|'snow'|'rain'|'cloud', x, y, at, label}], months: [12 x 0..1], monthsAt, hi})`
-> `{area (the map), strip, at(x, y)}`.
Do: month values from the brief's own series, scaled to its max. Don't: a temperature that isn't in the brief.
Stills: 0.0 map and strip empty, 1.0 fronts and bars, 1.8 snow, 3.0 settled.

### 10. `counter`: storefront and the flipping price tag
For: pricing, raising prices, three prices, "same job, new price". Brick, a striped awning, the shop sign, an OPEN sign
that glows on and off once a second, an item on the counter; the tag narrows to its edge on whole pixels, shows its
barcode back, turns to the new price, sways to rest with sparks. A chalk board on the wall holds the scene's words.
`k.sets.counter({shop, item: 'box'|'heater'|'toolbox', tags: [{price, at}]})` -> `{area (the chalk board), tag}`.
Stills: 0.0 old price, 1.3 flipping, 1.45 the back, 3.0 new price.

### 11. `gauge`: speedometer for a rate
For: one rate (close rate, reply rate, share). The needle rises from zero, overshoots and settles (angle stepped to whole
degrees, so the line is always clean pixels), the readout counts with it; zones in red, gold, teal.
`k.sets.gauge({value, max: 100, at, dur: 1, zones: [[from, to, color]], label, prefix, suffix: '%', dec})` -> `{area (the label line), readout}`.
Stills: 0.0 at zero, 0.8 rising, 1.3 overshoot, 2.4 settled.

### 12. `slots`: slot machine for a number
For: a surprising number, "the odds", a reveal. The lever pulls in 3 steps, reels spin 6 pixels a frame and stop left to
right with a bounce on the symbols; then the bulbs chase faster and coins jump in the tray.
`k.sets.slots({t0, stops: [t, t, t], symbols: ['5', '7', '%'], label, win})` -> `{area (the crown), reels}`.
Do: one character per reel, the stops on the number's words. Don't: use it for a negative number (it reads as a win).
Stills: 0.0 cover, 0.6 spinning, 1.5 two stopped, 2.6 jackpot.

### 13. `inventory`: RPG tool belt
For: "the tools that win", a checklist of habits, comparing options by stats. Eight slots with pixel icons; the cursor
jumps slot to slot (corner brackets breathe a pixel); the detail pane names the item and fills its stat bars.
`k.sets.inventory({title, items: [{icon, name, stats: [{label, value, max, text}]}], select: [{slot, at}], footer})` -> `{area, detail}`.
Stills: 0.0 belt, 0.5 first pick, 1.0 stats filling, 2.0 settled.

### 14. `levelup`: XP bar and LEVEL UP
For: the payoff of a habit, "do this and you level up", the close. The bar fills in 20 segments (the next one blinks
while filling), rolls over at `levelAt`: rays turn a step every 4 frames, LEVEL UP stamps in with sparks, new perks land.
`k.sets.levelup({from, to, max, at, dur, levelAt, level, text, stats: [{text, at}]})` -> `{area (the perks), bar}`.
Stills: 0.0 bar, 1.0 nearly full, 1.6 LEVEL UP, 2.8 perks.

### 15. `versus`: fighting-game select screen
For: two shops, two approaches, before/after. Teal and red halves on a slant with speed lines streaming in; the cards
slide in from the edges, VS stamps on the split with a bolt, stats fill toward the middle, the loser dims (dither) and
WIN stamps on the winner.
`k.sets.versus({a: {name, icon, stats: [{label, value, max, text}]}, b: {...}, at, vsAt, winner: 'a'|'b', winAt, winText, max})` -> `{a, b}`.
Do: 2 stats a side, values from the same base. Don't: a winner the data doesn't show.
Stills: 0.0 settled cover (at -0.4), 0.4 before VS, 1.4 stats filling, 2.8 the win.

### 16. `hud`: coins, counter, hearts, progress (an overlay)
For: any count that piles up, over any room or set. Draw it last. Coins rain with gravity and spin (4 frames), sparkle
where they land; the counter ticks with a coin; hearts light one by one with a 1-pixel pop; a bar fills.
`k.sets.hud({coins: {at, dur, n, x0, x1, floor}, counter: {x, y, from, to, at, dur, prefix, suffix}, hearts: {x, y, n, lit, at}, bar: {x, y, w, label, from, to, at, dur, max, c}})` (low-res positions).
Stills: over the workshop; 0.0, 0.7 coins falling, 1.2, 2.2 counted.

## Do and don't (all sets)
- Do let the set carry the motion and keep the scene's own text to one or two lines in the set's `area`.
- Do drive every `at` from a word or cue; a beat every 2 to 4 s still holds.
- Don't stack two sets in one section, or put a k.panel over a set's main element.
- Don't scale a set (no `k.cam`); pixel art never scales by a fraction.
- Check with `anim.py stills` and `lint` like any scene.
