# Kit: what can be drawn

Everything below draws in every look (`_shared/looks.md`); scene.js calls it through `k` (`_runtime/kit.js`).

## The cast (original, ours)
- **Snow**, the host: a Chicago data guy in a work jacket and knit cap with a clipboard. A nod to John Snow, whose 1854
  cholera map started mapping as proof. Poses: `stand`, `point` (toward a spot), `talk`, `shrug`, `wave`, `lean` (studying),
  `clip` (checks the clipboard). He talks (mouth moves) while the voice is speaking and blinks on his own.
  `k.snow(x, y, {pose, at: [x, y], scale, face: 1 | -1})`.
- **Squeak**, a small rat: comic relief only, never evidence. Poses: `sit`, `peek` (head over an edge), `run`, `startle`.
  `k.squeak(x, y, {pose, scale, face})`. Never stands in for a count.

## Real things (desk.md has the rules)
- `k.map(box, {focus, show, glow})`: the 77 community areas from the City's boundaries; focus gets the accent.
- `k.panel(box, title, rows)`: a data card in the look of the City's own table (dataset name, the window, real rows).
- `k.page(box, 'rat-page', {scroll})`: our live Chicago rat complaints page, captured from docs/ (`anim.py grab`).
- `k.count(box, from, to, p, fmt)`: a number counting up; lands exactly on the brief's value.
- `k.bars(box, rows, p)`, `k.compare(box, a, b, p)`: bars and a two-card comparison, values from the brief.

## Words on screen
- `k.title(text, y)`, `k.label(text, x, y, opts)`, `k.big(text, x, y, opts)`.
- The speech box (bottom band, y 1060 to 1240): Snow's name tag and the words being said, the spoken word lit. The
  player draws it from words.json; scene.js never draws captions itself.

## Motion
- `k.p(t0, t1)` eases 0 to 1, `k.pop(t)` a quick overshoot, `k.shake(t)`, `k.spot(box, t)` a highlight ring that
  draws on, `k.arrow(from, to, p)`, `k.chip(text, x, y)` a small tag like "THE CITY'S DATA".
- Sections cut on the cue; the camera can push in (`k.cam(scale, x, y)`) for emphasis.
