/* Scene: Know your close rate (Lesson 8, Numbers Clinic, arcade). One function per top-level cue in 03_cues/cues.md. */
/* Numbers only from k.data (brief.md -> data.js). Every time comes from a cue start (k.S) or a spoken word (wordT), so a */
/* re-voiced take moves the picture with it. */
/* Worlds, one per section: hook = the region cards drawn here (the hook on the plate on frame 0 with both region cards */
/* settled, a cut in to the Friday board close-up and back out, each card re-popping as its number is said, a plain US */
/* silhouette on the floor); stakes = the gauge (the median band, the top quarter's band, the gap between them); formula = */
/* the neon sign drawn here (the formula in tubes that switch on as it is said); example = the inventory (estimates and jobs */
/* sold as items, the close rate crafted from them); turn = the dispatch board once (a plain town grid of shops where only */
/* some are ServiceTitan customers), then the ghost lap board drawn here (last month is the ghost to beat); weekly = the */
/* Friday board drawn here (the lesson's one room-and-panel section: a whiteboard written in marker beside a cork strip of */
/* estimate slips that flip SOLD); close = the levelup set (the formula is the perk). */
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', GREY = '#9AA0AD';
const NAVY = '#253048', WINE = '#7A3442', PINE = '#2F6F67';
const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eo = (x) => 1 - Math.pow(1 - clamp(x), 3);

/* ---- the pixel kit (low-res units: 360 x 640, one pixel = 3 frame units), the same primitives the sets use ---- */
const px = (k) => {
  const ctx = k.ctx, T = k.T, F = Math.floor(T * 30 + 0.005);
  const P = (x, y, w, h, c) => { x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h); if (w > 0 && h > 0 && c) { ctx.fillStyle = c; ctx.fillRect(x * 3, y * 3, w * 3, h * 3); } };
  const DOT = (x, y, c) => P(x, y, 1, 1, c);
  const dith = (x, y, w, h, c, ph = 0) => { ctx.fillStyle = c; for (let j = 0; j < h; j++) for (let i = (j + ph) & 1; i < w; i += 2) ctx.fillRect((Math.round(x) + i) * 3, (Math.round(y) + j) * 3, 3, 3); };
  const disc = (cx, cy, r, c) => { for (let dy = -r; dy <= r; dy++) { const hw = Math.floor(Math.sqrt(r * r - dy * dy) + 0.4); P(cx - hw, cy + dy, 2 * hw + 1, 1, c); } };
  const ring = (cx, cy, r, c, th = 1) => { for (let dy = -r; dy <= r; dy++) { const ho = Math.floor(Math.sqrt(r * r - dy * dy) + 0.4), ri = r - th, hi = Math.abs(dy) <= ri ? Math.floor(Math.sqrt(ri * ri - dy * dy) + 0.4) : -1; if (hi < 0) P(cx - ho, cy + dy, 2 * ho + 1, 1, c); else { P(cx - ho, cy + dy, ho - hi, 1, c); P(cx + hi + 1, cy + dy, ho - hi, 1, c); } } };
  const line = (x0, y0, x1, y1, c, th = 1) => {
    x0 = Math.round(x0); y0 = Math.round(y0); x1 = Math.round(x1); y1 = Math.round(y1);
    const dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1; let e = dx + dy;
    for (let n = 0; n < 2000; n++) { P(x0, y0, th, th, c); if (x0 === x1 && y0 === y1) break; const e2 = 2 * e; if (e2 >= dy) { e += dy; x0 += sx; } if (e2 <= dx) { e += dx; y0 += sy; } }
  };
  const win = (x, y, w, h, o = {}) => {
    const base = o.base || '#253048', hi = o.hi || '#3B82C4', lo = o.lo || '#1B1420', rule = o.rule === undefined ? '#87CEEB' : o.rule;
    if (o.shadow !== false) P(x + 2, y + 2, w, h, INK);
    P(x + 1, y, w - 2, h, INK); P(x, y + 1, w, h - 2, INK);
    P(x + 1, y + 1, w - 2, h - 2, base); P(x + 2, y + 1, w - 4, 1, hi); P(x + 1, y + 2, 1, h - 4, hi); P(x + 2, y + h - 2, w - 4, 1, lo); P(x + w - 2, y + 2, 1, h - 4, lo);
    if (rule) { P(x + 3, y + 3, w - 6, 1, rule); P(x + 3, y + h - 4, w - 6, 1, rule); P(x + 3, y + 3, 1, h - 6, rule); P(x + w - 4, y + 3, 1, h - 6, rule); }
  };
  const fr = (t0) => Math.floor((T - t0) * 30 + 0.005);
  const ease = (t0, frames, dist) => Math.round(dist * (1 - eo(fr(t0) / frames)));
  const tx = (s, x, y, o = {}) => k.text(s, x * 3, y * 3, Object.assign({size: 39}, o));
  const tw = (s, size = 39) => k.measure(String(s), {size}) / 3;
  const clip = (x, y, w, h, fn) => { ctx.save(); ctx.beginPath(); ctx.rect(x * 3, y * 3, w * 3, h * 3); ctx.clip(); fn(); ctx.restore(); };
  const twinkle = (x, y, f, c = CREAM) => { const s = [0, 1, 2, 1][((f % 4) + 4) % 4]; DOT(x, y, c); for (let i = 1; i <= s; i++) { DOT(x - i, y, c); DOT(x + i, y, c); DOT(x, y - i, c); DOT(x, y + i, c); } };
  /* a ring that steps out from a box for 12 frames (a ping; never on frame 0, its times all come after the cover) */
  const ping = (t0, x, y, w, h, c = CREAM) => { const f = fr(t0); if (f >= 0 && f < 12) { const g = 1 + f; P(x - g, y - g, w + 2 * g, 1, c); P(x - g, y + h + g, w + 2 * g, 1, c); P(x - g, y - g, 1, h + 2 * g, c); P(x + w + g, y - g, 1, h + 2 * g + 1, c); } };
  return {P, DOT, dith, disc, ring, line, win, fr, ease, tx, tw, clip, twinkle, ping, F, T};
};

/* ---- the words: every beat lands on a spoken word ---- */
const WS = () => (window.WORDS && window.WORDS.words) || [];
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
/* a count that starts at 85% of its value and lands exactly on it */
const cnt = (k, num, t0, o = {}) => k.count(num.value, k.lin(t0, t0 + 0.7) >= 1 ? 1 : 0.85 + 0.15 * k.lin(t0, t0 + 0.7), Object.assign({from: 0}, o));
const host = (k, pose) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150});
/* a dark plate for words over a busy set (low-res box) */
const plate = (d, x, y, w, h, edge = '#3D2E45') => d.win(x, y, w, h, {base: '#1B1420', hi: edge, lo: INK, rule: edge});

/* ================================================================================================================ */
/* the region cards (hook): our own set piece. A studio wall, the claim panel, two card slots the region cards drop into, */
/* and on the floor a plain US silhouette (no state lines: the source names the regions, not their borders) */
const US = [[-124.7, 48.4], [-123, 49], [-95.2, 49], [-95.2, 49.4], [-89.6, 48], [-84.8, 46.5], [-82.4, 43], [-83.1, 42], [-79, 42.5],
  [-79, 43.3], [-76.3, 43.5], [-75, 44.9], [-71.5, 45], [-70, 46.7], [-69.2, 47.4], [-67.8, 47.1], [-67, 44.8], [-70.2, 43.7], [-70.6, 42.6],
  [-70, 41.8], [-71.8, 41.3], [-74, 40.5], [-74, 39.6], [-75, 38.8], [-75.5, 37.9], [-76, 37], [-75.5, 35.3], [-77.9, 33.9], [-79.9, 32.7],
  [-81.4, 30.4], [-80.1, 26.9], [-80.4, 25.2], [-81.8, 26.1], [-82.7, 28], [-83, 29.2], [-84.3, 30], [-86.5, 30.4], [-88, 30.7], [-89.6, 30.2],
  [-89.4, 29], [-91, 29.3], [-93.8, 29.7], [-95, 29.2], [-97.2, 27.7], [-97.4, 25.9], [-99.5, 27.5], [-101, 29.5], [-103, 29], [-104.5, 29.6],
  [-106.5, 31.8], [-108.2, 31.8], [-108.2, 31.3], [-111.1, 31.3], [-114.8, 32.5], [-117.1, 32.5], [-118.4, 33.8], [-120.6, 34.6], [-121.9, 36.6],
  [-122.5, 37.8], [-123.8, 39.8], [-124.4, 40.4], [-124.2, 42], [-124, 46.2]];
const UX = 44, UY = 440, US_S = 6.0, US_K = 0.79;   /* low-res box origin, pixels per degree, cos(38) for longitude */
const usPt = (lon, lat) => [UX + Math.round((lon + 124.8) * US_K * US_S), UY + Math.round((49.5 - lat) * US_S)];
let usRows = null;   /* the silhouette as row spans, worked out once (point in polygon on the low-res grid) */
const usSpans = () => {
  if (usRows) return usRows;
  const poly = US.map(([a, b]) => usPt(a, b)), rows = [];
  for (let y = UY; y <= UY + 150; y++) {
    const xs = []; const yy = y + 0.5;
    for (let i = 0; i < poly.length; i++) { const [x0, y0] = poly[i], [x1, y1] = poly[(i + 1) % poly.length]; if ((y0 <= yy) !== (y1 <= yy)) xs.push(x0 + (yy - y0) * (x1 - x0) / (y1 - y0)); }
    xs.sort((a, b) => a - b);
    for (let i = 0; i + 1 < xs.length; i += 2) rows.push([y, Math.round(xs[i]), Math.round(xs[i + 1])]);
  }
  return (usRows = rows);
};
const usMap = (d, fill, edge) => {
  const rows = usSpans(), by = {};
  rows.forEach(([y, a, b]) => { (by[y] = by[y] || []).push([a, b]); });
  rows.forEach(([y, a, b]) => { d.P(a + 2, y + 2, b - a, 1, INK); });   /* the drop shadow */
  rows.forEach(([y, a, b]) => { d.P(a, y, b - a, 1, fill); d.DOT(a, y, edge); d.DOT(b - 1, y, edge); });
  /* top and bottom edges: where a row's span is not covered by the row above (or below) */
  const cover = (y, x) => (by[y] || []).some(([a, b]) => x >= a && x < b);
  rows.forEach(([y, a, b]) => { for (let x = a; x < b; x++) if (!cover(y - 1, x) || !cover(y + 1, x)) d.DOT(x, y, edge); });
};
/* one region card: label, the median, a 0 to 100 meter. Settled in its slot from frame 0 (the cover shows both numbers); */
/* when its number is said it re-pops: it lifts out, drops back in and its meter fills again from empty */
const regionCard = (k, d, x, y, label, num, c, edge, at) => {
  const f = d.fr(at), dy = f < 0 ? 0 : [-26, -16, -8, -2, 2, 0][Math.min(5, f)];
  /* the slot: a recessed socket */
  d.P(x, y, 164, 80, '#120D14'); d.P(x + 1, y + 1, 162, 78, '#1B1420'); d.P(x + 1, y + 1, 162, 2, '#2B2033');
  d.clip(x - 2, y - 2, 170, 86, () => {
    d.win(x, y + dy, 164, 80, {base: '#1B1420', hi: edge, lo: INK, rule: edge});
    d.tx(label, x + 8, y + 8 + dy, {color: c});
    k.text(num.shown, (x + 8) * 3, (y + 21 + dy) * 3, {size: 132, color: CREAM, drop: INK});
    /* the meter: a 0 to 100 track, full on the cover, refilled a step at a time once the card has dropped back in */
    const mx = x + 80, mw = 74, my = y + 44 + dy, q = f < 0 ? 1 : clamp((d.fr(at + 0.2) + 1) / 10);
    d.P(mx - 1, my - 1, mw + 2, 10, INK); d.P(mx, my, mw, 8, '#3D2E45');
    for (let i = 1; i < 4; i++) d.P(mx + Math.round(mw * i / 4), my + 2, 1, 4, '#6B7080');
    d.P(mx, my, Math.round(mw * num.value / 100 * q), 8, c);
  });
  d.ping(at + 5 / 30, x, y, 164, 80, c);
};
/* the studio wall and floor for the region cards */
const studio = (d) => {
  const {P} = d;
  P(0, 0, 360, 417, '#2B2033');
  for (let x = 0; x < 360; x += 30) P(x, 0, 1, 417, '#241B2B');
  P(0, 410, 360, 7, '#3D2E45'); P(0, 410, 360, 1, '#6B7080');
  P(0, 417, 360, 223, '#1B1420');
  for (let y = 426; y < 640; y += 20) P(0, y, 360, 1, '#241B2B');
};

/* ================================================================================================================ */
/* the ghost lap board (turn.own, turn.yours): our own set piece. Last month is the ghost car; this month races it. A lap */
/* board with two lanes (no numbers: it is the viewer's own), a checkered flag on the ghost's line, and the track on the */
/* floor where the two cars run, the lane dashes streaming past */
const ghostCar = (d, x, y, ghost, F) => {
  const body = ghost ? '#3D2E45' : GOLD, edge = ghost ? '#9AA0AD' : INK, bob = ghost ? 0 : (Math.floor(F / 4) % 2);
  y -= bob;
  d.P(x, y + 4, 30, 8, edge); d.P(x + 1, y + 5, 28, 6, body); d.P(x + 7, y, 14, 5, edge); d.P(x + 8, y + 1, 12, 4, ghost ? '#2B2033' : '#87CEEB');
  d.P(x + 26, y + 6, 3, 2, ghost ? '#9AA0AD' : CREAM);
  [5, 21].forEach((wx) => { d.P(x + wx, y + 10, 6, 5, ghost ? '#9AA0AD' : INK); d.P(x + wx + 2, y + 11 + ((Math.floor(F / 3) + wx) % 2), 2, 2, ghost ? '#2B2033' : GREY); });
};
const flag = (d, x, y, F) => {
  d.P(x, y, 2, 76, '#C9CCD3');
  const wave = Math.floor(F / 8) % 2;
  for (let j = 0; j < 4; j++) for (let i = 0; i < 6; i++) d.P(x + 2 + i * 3, y + 1 + j * 3 + (i >= 3 ? wave : 0), 3, 3, (i + j) % 2 ? INK : CREAM);
};
const ghostBoard = (k, o) => {
  const d = px(k), {P, F, T} = d;
  /* the night wall and the grandstand lights */
  P(0, 0, 360, 417, '#1B1420');
  for (let x = 0; x < 360; x += 12) P(x, 30, 8, 40, '#241B2B');
  [[24, 20], [324, 20]].forEach(([x, y]) => { P(x, y, 14, 8, '#C9CCD3'); P(x + 1, y + 1, 12, 6, Math.floor(F / 30) % 2 ? CREAM : GOLD); P(x + 6, y + 8, 2, 60, '#4A4E5A'); });
  /* the lap board */
  d.win(12, 86, 336, 124, {base: '#2B2033', hi: GOLD, lo: INK, rule: '#3D2E45'});
  k.slam('Beat your ghost', 60, 276, o.t0, {size: 66, color: 'accent', from: 0.4, drop: INK});
  const tx0 = 20, tw = 300, gx = tx0 + Math.round(tw * 0.72);
  const lane = (y, label, c, ghost, len) => {
    d.tx(label, 20, y, {color: c});
    P(tx0 - 1, y + 15, tw + 2, 14, INK); P(tx0, y + 16, tw, 12, '#3D2E45');
    if (ghost) { P(tx0, y + 16, len, 12, '#2B2033'); for (let x = tx0; x < tx0 + len; x += 6) { P(x, y + 16, 3, 1, '#9AA0AD'); P(x, y + 27, 3, 1, '#9AA0AD'); } P(tx0 + len - 1, y + 16, 1, 12, '#9AA0AD'); }
    else if (len > 0) { P(tx0, y + 16, len, 12, GOLD); P(tx0, y + 16, len, 2, '#FFE2A8'); P(tx0, y + 26, len, 2, ORANGE); }
  };
  lane(122, 'GHOST: LAST MONTH', '#C9CCD3', true, gx - tx0);
  /* this month: it sets off when the board opens, runs at the ghost, and is still on its tail when the lesson moves on */
  const run = clamp((T - o.t0 - 0.3) / Math.max(1, o.tLast - o.t0)), yl = Math.round((gx - tx0 - 6) * eo(run));
  lane(162, 'YOU: THIS MONTH', GOLD, false, yl);
  if (yl > 0) { P(tx0 + yl - 2, 176, 4, 14, CREAM); }
  flag(d, gx, 118, F);
  /* the floor: the track, a kerb, two lanes with dashes streaming past, the finish line, the two cars */
  P(0, 417, 360, 223, '#241B2B');
  for (let x = -((F * 2) % 16); x < 360; x += 16) { P(x, 424, 8, 5, RED); P(x + 8, 424, 8, 5, CREAM); }
  P(0, 430, 360, 120, '#2B2033'); P(0, 550, 360, 4, '#4A4E5A');
  for (let x = -((F * 4) % 24); x < 360; x += 24) P(x, 489, 12, 2, '#6B7080');
  for (let j = 0; j < 30; j++) P(300 + (j % 2) * 4, 430 + j * 4, 4, 4, CREAM);
  for (let j = 0; j < 30; j++) P(300 + ((j + 1) % 2) * 4, 430 + j * 4, 4, 4, INK);
  const gcx = 196, ycx = 40 + Math.round(140 * eo(run));
  ghostCar(d, gcx, 452, true, F); ghostCar(d, ycx, 506, false, F);
  if (ycx > 60) for (let i = 0; i < 3; i++) P(ycx - 8 - i * 7 - ((F + i) % 3), 516 + i * 2, 4, 1, '#6B7080');   /* speed lines */
  return d;
};

/* a small shop on the map (a roof and a door), 9 x 8, grey for any shop, teal-roofed when it is a ServiceTitan customer */
const shop = (d, x, y, c) => { d.P(x - 1, y + 2, 11, 7, INK); d.P(x, y + 3, 9, 5, '#C9CCD3'); d.P(x + 3, y + 5, 3, 3, '#4A4E5A'); d.P(x - 1, y, 11, 3, INK); d.P(x, y, 9, 2, c); };

/* ================================================================================================================ */
/* the Friday board (the hook close-up, weekly): our own set piece. A pegboard wall in the shop, an aluminium-framed */
/* whiteboard written in marker, a cork strip of estimate slips (each slip says $, $$ or $$$ once the dollars come in, */
/* and flips over to a red SOLD back), a marker tray with an eraser, a shop stool and the concrete floor. */
/* Whiteboard writing area (frame units): x 54 to 708 (or 1002 with no cork), y 270 to 918. */
const BX = 14, BY = 84, BW = 222, BH = 226, CX0 = 242;
const SLIPS = [   /* the cork strip: three columns, four rows, each a little off the grid; q is the quote size */
  [250, 98, 1], [282, 102, 3], [313, 97, 1],
  [251, 141, 2], [283, 144, 1], [314, 139, 3],
  [249, 184, 1], [282, 186, 2], [313, 182, 1],
  [251, 226, 3], [283, 228, 1], [314, 224, 2],
];
const board = (k, o = {}) => {
  const d = px(k), {P, DOT, dith, F, T, fr} = d, cork = o.cork !== false, W = cork ? BW : 332;
  /* the wall: pegboard (a hole every 6 pixels), a light from above, a baseboard */
  P(0, 0, 360, 417, '#8C5A33');
  for (let y = 3; y < 330; y += 6) for (let x = 3 + ((y / 6) & 1) * 3; x < 360; x += 6) DOT(x, y, '#6B4226');
  dith(0, 0, 360, 40, '#B07A47', 0);
  P(0, 330, 360, 6, '#4A2E1B'); P(0, 330, 360, 1, '#B07A47');
  P(0, 336, 360, 81, '#5A3A22'); for (let x = 0; x < 360; x += 24) P(x, 336, 1, 81, '#4A2E1B');
  /* the floor: sealed concrete, a crack, an oil spot */
  P(0, 417, 360, 223, '#4A4E5A'); for (let y = 417; y < 640; y += 18) P(0, y, 360, 1, '#3D2E45');
  dith(0, 417, 360, 4, '#6B7080', 1); d.line(40, 470, 92, 520, '#3D2E45'); d.line(92, 520, 120, 600, '#3D2E45'); dith(250, 520, 40, 10, '#2B2033');
  /* the whiteboard: a drop shadow, the aluminium frame (light top-left), the white with ghosted old writing */
  P(BX + 3, BY + 3, W + 6, BH + 6, INK);
  P(BX - 3, BY - 3, W + 6, BH + 6, INK); P(BX - 2, BY - 2, W + 4, BH + 4, '#C9CCD3'); P(BX - 2, BY - 2, W + 4, 1, CREAM); P(BX - 2, BY - 2, 1, BH + 4, CREAM); P(BX + W + 1, BY - 1, 1, BH + 3, '#6B7080'); P(BX - 1, BY + BH + 1, W + 3, 1, '#6B7080');
  P(BX, BY, W, BH, CREAM);
  dith(BX + 6, BY + 150, 70, 4, '#F4E6D3', 1); dith(BX + 120, BY + 40, 60, 3, '#F4E6D3', 0); dith(BX + 30, BY + 200, 120, 3, '#F4E6D3', 1);
  /* a glare that steps across the board once every 5 s (whole pixels, never on frame 0) */
  if (T > 0.6) { const g = Math.floor(((T - 0.6) % 5) * 30); if (g < 40) { const gx = BX - 40 + g * Math.round((W + 80) / 40); for (let j = 0; j < BH; j++) { const xx = gx + Math.floor(j * 0.35); if (xx >= BX && xx + 2 < BX + W) { DOT(xx, BY + BH - 1 - j, '#FFFFFF'); DOT(xx + 1, BY + BH - 1 - j, '#FFFFFF'); } } } }
  /* the tray, three markers and the eraser */
  const ty = BY + BH + 2;
  P(BX - 4, ty, W + 8, 5, INK); P(BX - 3, ty, W + 6, 3, '#9AA0AD'); P(BX - 3, ty, W + 6, 1, CREAM);
  [[BX + 10, NAVY], [BX + 30, RED], [BX + 50, PINE]].forEach(([x, c], i) => { if (o.inHand !== i) { P(x, ty - 3, 14, 4, INK); P(x + 1, ty - 2, 9, 2, CREAM); P(x + 10, ty - 2, 3, 2, c); } });
  P(BX + W - 34, ty - 6, 24, 7, INK); P(BX + W - 33, ty - 5, 22, 3, '#3B82C4'); P(BX + W - 33, ty - 2, 22, 2, '#C9CCD3');
  /* the cork strip */
  if (cork) {
    const cx = CX0, cw = 104;
    P(cx - 3, BY - 3, cw + 6, BH + 6, INK); P(cx - 2, BY - 2, cw + 4, BH + 4, '#6B4226'); P(cx - 2, BY - 2, cw + 4, 1, '#B07A47');
    P(cx, BY, cw, BH, '#B07A47'); dith(cx, BY, cw, BH, '#8C5A33', 0);
    for (let i = 0; i < 70; i++) DOT(cx + Math.floor(hash(i * 2.7) * cw), BY + Math.floor(hash(i * 5.3) * BH), '#D9A066');
    if (o.corkTitle) { P(cx + 8, BY + 2, cw - 16, 9, INK); P(cx + 9, BY + 3, cw - 18, 7, '#F4E6D3'); }
    (o.slips || SLIPS).forEach((s, i) => slip(d, k, s, i, o));
  }
  /* the stool by the board (when the host is not standing there it still holds the room together) */
  P(300, 372, 44, 5, INK); P(301, 372, 42, 3, '#D9A066'); P(306, 377, 3, 40, '#6B4226'); P(335, 377, 3, 40, '#6B4226'); P(306, 398, 32, 2, '#6B4226');
  /* the floor, so the bottom third is the shop and not bare concrete: a box fan turning, a bucket, a rolling tool chest */
  const fx = 30, fy = 452;
  P(fx + 3, fy + 3, 72, 76, INK); P(fx, fy, 72, 76, INK); P(fx + 2, fy + 2, 68, 72, '#6B7080'); P(fx + 4, fy + 4, 64, 64, '#2B2033');
  const ang = (Math.floor(F / 2) % 12) * Math.PI / 12;
  for (let b = 0; b < 4; b++) { const a = ang + b * Math.PI / 2; d.line(fx + 36, fy + 36, fx + 36 + Math.round(Math.cos(a) * 26), fy + 36 + Math.round(Math.sin(a) * 26), '#C9CCD3', 3); }
  d.disc(fx + 36, fy + 36, 5, INK); d.disc(fx + 36, fy + 36, 3, RED);
  for (let i = 0; i < 64; i += 8) { P(fx + 4 + i, fy + 4, 1, 64, '#4A4E5A'); P(fx + 4, fy + 4 + i, 64, 1, '#4A4E5A'); }
  P(fx + 6, fy + 70, 14, 4, '#3D2E45'); P(fx + 52, fy + 70, 14, 4, '#3D2E45'); P(fx + 26, fy + 72, 20, 2, GREY);
  const bx = 126, by0 = 500;
  P(bx + 2, by0 + 2, 40, 50, INK); P(bx, by0, 40, 50, INK); P(bx + 1, by0 + 1, 38, 48, ORANGE); P(bx + 1, by0 + 1, 38, 4, '#FFE2A8');
  P(bx + 1, by0 + 14, 38, 2, '#B07A47'); P(bx + 1, by0 + 36, 38, 2, '#B07A47'); d.line(bx + 3, by0, bx + 9, by0 - 12, '#9AA0AD'); d.line(bx + 9, by0 - 12, bx + 31, by0 - 12, '#9AA0AD'); d.line(bx + 31, by0 - 12, bx + 37, by0, '#9AA0AD');
  P(bx - 4, by0, 48, 3, INK); P(bx - 3, by0, 46, 2, '#B07A47');
  const cx2 = 206;
  P(cx2 + 3, 452, 120, 110, INK); P(cx2, 449, 120, 110, INK); P(cx2 + 2, 451, 116, 106, RED); P(cx2 + 2, 451, 116, 3, '#F09A9A');
  for (let i = 0; i < 4; i++) { P(cx2 + 6, 460 + i * 24, 108, 20, WINE); P(cx2 + 7, 461 + i * 24, 106, 18, RED); P(cx2 + 46, 468 + i * 24, 28, 3, CREAM); }
  [cx2 + 8, cx2 + 100].forEach((x) => { P(x, 559, 12, 8, INK); d.disc(x + 6, 568, 4, '#4A4E5A'); });
  return d;
};
/* one estimate slip: a paper slip on a pin. o.sold[i] is when it flips to SOLD (it narrows to its edge on whole pixels, */
/* then opens on its red back), o.dollars is when the quote size is written on it, o.fall {i, at} drops it off the cork. */
const slip = (d, k, s, i, o) => {
  const {P, DOT, fr, T} = d, [x0, y0, q] = s, w = 26, h = 34;
  let x = x0, y = y0, tilt = 0;
  const fall = o.fall && o.fall.i === i ? o.fall : null;
  if (fall && T >= fall.wobble && T < fall.at) tilt = (Math.floor((T - fall.wobble) * 6) % 2) ? 1 : -1;   /* 3 swings a second */
  if (fall && T >= fall.at) { const g = T - fall.at; y = y0 + Math.round(Math.min(330 - y0 - h, 60 * g + 420 * g * g)); x = x0 + Math.round(Math.min(18, g * 30)); }
  const soldAt = o.sold && o.sold[i] != null ? o.sold[i] : null, f = soldAt != null ? fr(soldAt) : -1;
  let sw = w; if (f >= 0 && f < 3) sw = Math.max(2, Math.round(w * (1 - (f + 1) / 3))); else if (f >= 3 && f < 6) sw = Math.round(w * (f - 2) / 3);
  const back = f >= 3, sx = x + Math.round((w - sw) / 2);
  P(sx + 1 + tilt, y + 2, sw, h, '#4A2E1B');
  P(sx + tilt, y, sw, h, back ? RED : CREAM);
  if (sw === w) {
    if (!back) {
      for (let j = 0; j < 4; j++) P(x + 4 + tilt, y + 9 + j * 5, w - 8 - (j === 3 ? 8 : 0), 1, '#C9CCD3');
      P(x + 3 + tilt, y + 3, 10, 2, '#9AA0AD');
      if (o.dollars != null && T >= o.dollars + i * 0.04) { const s2 = '$'.repeat(q); k.text(s2, (x + w / 2 + tilt) * 3, (y + 21) * 3, {size: 30, color: q === 3 ? RED : PINE, align: 'center', lint: false}); }
    } else {
      P(x + 2, y + 2, w - 4, 1, '#F09A9A');
      k.text('SOLD', (x + w / 2) * 3, (y + 12) * 3, {size: 30, color: CREAM, align: 'center', lint: false});
      if (f >= 6 && f < 14) d.twinkle(x + w - 2, y + 2, f - 6);
    }
  }
  /* the pin (it stays on the cork when the slip falls) */
  P(x0 + w / 2 - 2, y0 - 2, 5, 5, INK); P(x0 + w / 2 - 1, y0 - 1, 3, 3, i % 3 === 1 ? '#3B82C4' : RED); DOT(x0 + w / 2 - 1, y0 - 1, CREAM);
};
/* marker writing: the line appears left to right (whole pixels) with the marker's tip riding the head of the ink */
const write = (k, s, x, y, t0, o = {}) => {
  if (k.T < t0) return false;
  const d = px(k), size = o.size || 66, w = k.measure(s, {size}), frames = Math.max(5, Math.min(14, Math.round(s.length * 0.6)));
  const f = d.fr(t0), q = t0 <= 0 ? 1 : clamp((f + 1) / frames);
  const ax = o.align === 'center' ? x - w / 2 : (o.align === 'right' ? x - w : x), shown = Math.round((w * q) / 3) * 3;
  k.ctx.save(); k.ctx.beginPath(); k.ctx.rect(ax - 6, y - 12, shown + 6, size * 1.4); k.ctx.clip();
  k.text(s, x, y, {size, color: o.color || NAVY, align: o.align, lint: q >= 1});
  k.ctx.restore();
  if (q < 1) {   /* the marker: a cap and a coloured tip at the head */
    const hx = Math.round((ax + shown) / 3), hy = Math.round((y + size * 0.55) / 3);
    d.P(hx, hy - 12, 4, 12, INK); d.P(hx + 1, hy - 11, 2, 10, CREAM); d.P(hx + 1, hy - 3, 2, 3, o.color || NAVY);
  }
  return true;
};

/* ================================================================================================================ */
/* the neon sign (formula): our own set piece. A brick wall at night, a black sign board bolted to it, the formula in */
/* neon tubes. Every tube is there from the first frame as grey unlit glass (so the whole formula is readable while it */
/* is said), and each one switches on, a warm-up frame then lit, on the word that says it. A conduit runs down to a */
/* transformer whose pilot lamp is on while any tube is lit; on the wet pavement below, the lit tubes throw a reflection. */
const NX0 = 12, NY0 = 88, NW = 336, NH = 174;
const neonWall = (k, lit) => {
  const d = px(k), {P, DOT, dith, F} = d;
  /* the wall: dark brick, mortar lines, a few odd bricks */
  P(0, 0, 360, 330, '#241B2B');
  for (let r = 0, y = 0; y < 330; r++, y += 7) for (let x = (r & 1) ? -8 : 0; x < 360; x += 16) P(x, y, 15, 6, hash(r * 7.3 + x * 0.17) > 0.86 ? '#3D2E45' : '#33263B');
  /* the sign board: a drop shadow, a steel edge (light top-left), black inside, a bolt at each corner */
  P(NX0 + 3, NY0 + 3, NW, NH, INK);
  P(NX0 - 1, NY0 - 1, NW + 2, NH + 2, INK); P(NX0, NY0, NW, NH, '#4A4E5A'); P(NX0, NY0, NW, 1, '#9AA0AD'); P(NX0, NY0, 1, NH, '#9AA0AD');
  P(NX0 + 2, NY0 + 2, NW - 4, NH - 4, '#120D14');
  [[NX0 + 5, NY0 + 5], [NX0 + NW - 7, NY0 + 5], [NX0 + 5, NY0 + NH - 7], [NX0 + NW - 7, NY0 + NH - 7]].forEach(([x, y]) => { P(x, y, 2, 2, '#9AA0AD'); DOT(x, y, CREAM); });
  /* the conduit down the wall to the transformer, its pilot lamp on while the sign is lit */
  P(328, NY0 + NH, 3, 276 - NY0 - NH, '#6B7080'); P(328, NY0 + NH, 1, 276 - NY0 - NH, '#9AA0AD');
  P(316, 276, 28, 18, INK); P(317, 277, 26, 16, '#4A4E5A'); P(317, 277, 26, 1, '#9AA0AD');
  for (let i = 0; i < 4; i++) P(320 + i * 4, 282, 2, 8, '#2B2033');
  P(337, 281, 3, 3, lit ? RED : '#7A3442'); if (lit) DOT(337, 281, '#F09A9A');
  /* the sill and the dark band under it */
  P(0, 330, 360, 6, '#4A4E5A'); P(0, 330, 360, 1, '#9AA0AD'); P(0, 336, 360, 81, '#1B1420');
  /* the sidewalk (slabs), a puddle that holds the sign's reflection (dithered streaks that step every 10 frames), the */
  /* kerb, the street with its lane dashes, a drain grate */
  P(0, 417, 360, 133, '#3D2E45'); P(0, 417, 360, 3, '#4A4E5A');
  for (let y = 444; y < 550; y += 27) P(0, y, 360, 1, '#2B2033');
  for (let r = 0, y = 420; y < 550; r++, y += 27) for (let x = (r & 1) ? 24 : 0; x < 360; x += 48) P(x, y, 1, Math.min(27, 550 - y), '#2B2033');
  const pw = (y) => Math.round(150 * Math.sqrt(Math.max(0, 1 - Math.pow((y - 474) / 22.5, 2))));   /* the puddle's half width on row y */
  for (let y = 452; y < 496; y++) P(180 - pw(y), y, 2 * pw(y), 1, '#1B1420');
  (lit || []).forEach(([x0, w, c], i) => { const ph = Math.floor(F / 10) + i; for (let j = 0; j < 4; j++) { const y = 458 + i * 8 + j * 2, a = Math.max(x0 + 16 + ((ph + j) % 3) - 1, 186 - pw(y)), b = Math.min(x0 + w - 4 - j * 8, 174 + pw(y)); if (b > a) dith(a, y, b - a, 1, c, j & 1); } });
  P(0, 550, 360, 6, '#9AA0AD'); P(0, 550, 360, 1, '#C9CCD3'); P(0, 556, 360, 84, '#241B2B');
  for (let x = 8; x < 360; x += 56) P(x, 596, 28, 4, '#6B7080');
  P(286, 557, 40, 10, INK); for (let i = 0; i < 6; i++) P(289 + i * 6, 559, 3, 6, '#4A4E5A');
  return d;
};
/* one neon line: grey glass before its word, then a warm-up frame (the halo only), then lit (a halo in the glow colour, */
/* one low-res pixel round every stroke, and the core) */
const neon = (k, s, x, y, at, o = {}) => {
  const size = o.size || 66, align = o.align, f = Math.floor((k.T - at) * 30 + 0.005), g = size >= 99 ? 6 : 3;
  if (k.T < at) { k.text(s, x, y, {size, color: '#4A4E5A', align}); return false; }
  [[-g, 0], [g, 0], [0, -g], [0, g]].forEach(([dx, dy]) => k.text(s, x + dx, y + dy, {size, color: o.glow, align, lint: false}));
  k.text(s, x, y, {size, color: f === 0 ? o.glow : o.core, align});
  return true;
};

/* ================================================================================================================ */
/* the gauge (stakes): the library gauge; the needle is driven here (value given each frame, settled), the bands and */
/* the gap are painted on its rim, the readout is our own LCD text */
const GX = 180, GY = 214, GR = 100;
const gAng = (v) => (135 + 2.7 * v) * Math.PI / 180;
const rim = (d, v0, v1, c, r0 = GR - 8, r1 = GR - 3) => { for (let a = gAng(v0); a <= gAng(v1) + 1e-6; a += 0.006) for (let r = r0; r <= r1; r++) d.DOT(GX + Math.round(Math.cos(a) * r), GY + Math.round(Math.sin(a) * r), c); };
/* our readout box, wider than the set's (x 138 to 222, frame 414 to 666) so '70% TO 73%' has room inside it */
const lcd = (k, d, s, c = GOLD, size = 66) => { d.P(GX - 42, GY + 18, 84, 30, INK); d.P(GX - 41, GY + 19, 82, 28, '#1A332B'); d.P(GX - 40, GY + 20, 80, 26, '#24453A'); d.tx(s, GX, size >= 60 ? GY + 22 : GY + 27, {size, color: c, align: 'center'}); };

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 8',
  transitions: {stakes: 'levelselect', formula: 'blinds', example: 'dissolve', turn: 'iris', weekly: 'door', close: 'chalk'},
  trauma: {'turn.yours': 0.8},
  sections: {
    /* ---- hook: three shots (IMPROVE 00a: the picture changes by 1 s and twice by 3 s, Snow on by 3 s). The cover: the */
    /* studio, the hook on the title plate (frame 0, held still, no host). Cut in on "close" to the Friday board close-up: */
    /* the hook written big on the whiteboard, the estimate slips flipping SOLD, Snow and the dialog box on. Cut back out */
    /* on "Here's" to the studio; the plate turns to the claim on "Median" and the region cards drop as it is said. */
    hook: (k, T) => {
      const n = k.data.numbers;
      const t31 = wordT(k, 'hook', /^thirty-one/i, 4.4), t38 = wordT(k, 'hook', /^thirty-eight/i, 5.2);
      const tIn = Math.min(0.8, Math.max(0.5, wordT(k, 'hook', /^close$/i, 0.7))), tRate = wordT(k, 'hook', /^rate/i, tIn + 0.3);
      const tOut = Math.min(2.6, k.S('hook.math')), med = Math.min(4.0, k.S('hook.median')) /* clamp: the on-screen hook holds 4.0 s at most */, src = k.S('hook.source'), win = k.S('hook.window');
      if (T >= tIn && T < tOut) {
        /* the close-up: the slips flip SOLD from "rate" on, a few at a time; the hook in marker, already up */
        const sold = {}; [1, 5, 9, 3, 7].forEach((i, j) => { sold[i] = tRate + j * 0.18; });
        board(k, {sold});
        k.text('Do you know your', 72, 300, {size: 66, color: NAVY});
        k.text('close rate?', 72, 400, {size: 99, color: RED});
        k.text('?', 381, 600, {size: 132, color: GOLD, align: 'center', drop: NAVY});
        /* a real reframe, not a backdrop swap: Snow steps up to the board, bigger and further in */
        return {hostPose: k.talking() ? 'talk' : 'point', hostScale: 0.9, hostX: 190};
      }
      const d = px(k);
      studio(d);
      /* the title plate: the hook from frame 0 to "Median", then the claim, the range colour-coded to the two cards */
      d.win(12, 88, 336, 78, {base: '#1B1420', hi: GOLD, lo: INK, rule: '#3D2E45'});
      if (T < med) {
        k.text('Do you know your', 60, 282, {size: 66, color: CREAM, drop: INK});
        k.text('close rate?', 60, 348, {size: 132, color: GOLD, drop: INK});
      } else {
        k.slam('Median close rate, by US region', 60, 282, med, {size: 66, color: CREAM, drop: INK, from: 0.5});
        const wA = k.measure(`${n.medLow.shown} `, {size: 132}), wB = k.measure('to ', {size: 132});
        k.slam(n.medLow.shown, 60, 348, med + 0.1, {size: 132, color: ORANGE, drop: INK, from: 0.6});
        k.slam('to', 60 + wA, 348, med + 0.15, {size: 132, color: CREAM, drop: INK, from: 0.6});
        /* the 38% slams from a smaller peak so it stays left of the NUMBERS CLINIC chip (x 640) at its largest */
        k.slam(n.medHigh.shown, 60 + wA + wB, 348, med + 0.2, {size: 132, color: TEAL, drop: INK, from: 0.3});
      }
      /* life on the cover before the cut: one ping round the plate */
      d.ping(0.3, 12, 88, 336, 78, GOLD);
      /* the segment chip lands on the plate with the cut back out */
      if (T >= tOut) { k.ctx.save(); k.ctx.translate(0, d.ease(tOut, 6, 20) * 3); k.chip('Numbers Clinic', 640, 404, {size: 30, fill: 'accent', color: INK}); k.ctx.restore(); }
      /* the region cards, settled from frame 0, re-pop (lift out, drop back in, refill) as their numbers are said */
      regionCard(k, d, 12, 172, 'US NORTHEAST', n.medLow, ORANGE, '#B07A47', t31);
      regionCard(k, d, 184, 172, 'US WEST', n.medHigh, TEAL, PINE, t38);
      k.burst(330, 640, t31 + 0.12, {n: 16, r: 180}); k.burst(846, 640, t38 + 0.12, {n: 16, r: 180, colors: ['teal', 'paper', 'accent2']});
      /* the source, on its own plate (text 48 px clear of the inner rule), on from frame 0 */
      plate(d, 12, 258, 262, 26);
      const lit = T >= src, wl = T >= win, wS = k.measure('ServiceTitan customers, ', {size: 39});
      k.text('ServiceTitan customers,', 60, 792, {size: 39, color: lit ? GOLD : SAND});
      k.text(`May to Jul ${n.stYear.shown}`, 60 + wS, 792, {size: 39, color: wl ? GOLD : SAND});
      if (lit) k.sweep(60, 834, k.measure('ServiceTitan customers,', {size: 39}), 3, src + 0.1, {color: 'teal'});
      if (wl) k.sweep(60 + wS, 834, k.measure(`May to Jul ${n.stYear.shown}`, {size: 39}), 3, win + 0.1, {color: 'teal'});
      /* the floor: a plain US silhouette, a scan line crossing it, a marker on each region as its number is said */
      usMap(d, '#3D2E45', '#6B7080');
      const sx = UX + (Math.floor(d.F / 2) * 2) % 300;
      usSpans().forEach(([y, a, b]) => { if (sx >= a && sx < b - 1) d.P(sx, y, 2, 1, '#4A4E5A'); });
      const mark = (lon, lat, c, at) => {
        const [x, y] = usPt(lon, lat), f = d.fr(at);
        if (f >= 0 && f < 24) d.ring(x, y, 4 + Math.floor(f / 2), c);
        d.disc(x, y, 5, INK); d.disc(x, y, 4, f >= 0 ? c : '#6B7080'); d.DOT(x - 1, y - 2, CREAM);
      };
      mark(-72.5, 43, ORANGE, t31); mark(-120.5, 40.5, TEAL, t38);
      /* the cover frame has no host; Snow and the dialog box come in with the cut and stay */
      if (T < tIn) return {host: false, speech: false};
      return host(k, k.live('hook.math') ? 'point' : (k.live('hook.region') ? 'point' : (k.live('hook.window') ? 'clip' : null)));
    },

    /* ---- stakes: the gauge. The median band is lit; the top quarter's band lights when it is named; the needle swings */
    /* to it as the numbers are said; the gap fills red on the rim; then the readout has nothing to show */
    stakes: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('stakes');
      const tTop = wordT(k, 'stakes', /^top$/i, 0.6), tRank = wordT(k, 'stakes.ranked', /^ranked/i), t70 = wordT(k, 'stakes.top', /^seventy$/i, 0.9), t73 = wordT(k, 'stakes.top', /^seventy-three/i, 1.7);
      const tGap = wordT(k, 'stakes.gap', /^big/i, 0.6), meas = k.S('stakes.measure'), tNever = wordT(k, 'stakes.measure', /^never/i, 1.7);
      /* the needle: in the median band on entry, out to the top quarter on "seventy", back to zero on "never" */
      const mid = (n.medLow.value + n.medHigh.value) / 2, top = (n.topLow.value + n.topHigh.value) / 2;
      const swing = (a, b, at, dur = 0.7) => { const q = clamp((T - at) / dur); if (q <= 0) return a; if (q >= 1) return b; const ov = Math.sin(q * Math.PI * 2.2) * (1 - q) * 0.12; return a + (b - a) * (eo(q * 1.4) + ov); };
      let v = swing(0, mid, t0 + 0.25, 0.8);
      if (T >= t70) v = swing(mid, top, t70, 0.9);
      if (T >= tNever) v = swing(top, 0, tNever, 0.6);
      /* the set's own readout sits under our LCD; it is not drawn at all (hidden text still counts for the layout lint). */
      /* Its '100' label moves 24 px right and its '0' 12 px left, clear of our wider readout box */
      const text0 = k.text;
      k.text = (s, x, y, o) => (o && o.size === 66 && y === (GY + 22) * 3 ? {w: 0, h: 0, lines: []} : text0(s, s === '100' ? x + 24 : (s === '0' ? x - 12 : x), y, o));
      try { k.sets.gauge({value: Math.max(0, v), at: -10, dur: 1, zones: [[0, 100, '#3D2E45']]}); } finally { k.text = text0; }
      /* the bands on the rim: the median (gold) from the start, the top quarter (teal) when it is named */
      rim(d, n.medLow.value, n.medHigh.value, GOLD, GR - 10, GR - 2);
      if (T >= tTop) rim(d, n.topLow.value, n.topHigh.value, T >= tRank ? TEAL : '#4A4E5A', GR - 10, GR - 2);
      /* the gap: the rim between the two bands fills red a step at a time */
      if (T >= tGap) { const q = clamp(d.fr(tGap) / 12); rim(d, n.medHigh.value + 1, n.medHigh.value + 1 + (n.topLow.value - n.medHigh.value - 2) * q, RED, GR - 6, GR - 5); }
      /* the corner plates: one line each (frame y 258 to 324), above the dial's rim, colour-coded to their bands */
      plate(d, 8, 86, 134, 22, GOLD);
      d.tx('MEDIAN', 15, 90, {color: GOLD});
      d.tx(`${n.medLow.shown} TO ${n.medHigh.shown}`, 15 + d.tw('MEDIAN '), 90, {color: CREAM});
      if (T >= tTop) {
        /* the plate hugs its words: 'TOP 25%' alone, then it grows in two steps (4 frames each, done as the word lands) */
        /* to hold '70% TO' and then '73%'; its right edge ends by frame x 921 */
        const sl = d.ease(tTop, 8, 40), lit = T >= tRank, lab = `TOP ${n.topShare.shown}`;
        const wOf = (s) => Math.round(d.tw(s)) + 16, w0 = wOf(lab), w1 = wOf(`${lab} ${n.topLow.shown} TO`), w2 = wOf(`${lab} ${n.topLow.shown} TO ${n.topHigh.shown}`);
        const grow = (a, b, at) => { const q = clamp((d.fr(at - 4 / 30) + 1) / 4); return q <= 0 ? a : a + Math.round((b - a) * eo(q)); };
        const pw = T >= t73 - 4 / 30 ? grow(w1, w2, t73) : (T >= t70 - 4 / 30 ? grow(w0, w1, t70) : w0);
        plate(d, 166 + sl, 86, pw, 22, lit ? TEAL : '#4A4E5A');
        d.tx(lab, 173 + sl, 90, {color: lit ? TEAL : GREY});
        if (T >= t70) d.tx(T >= t73 ? `${cnt(k, n.topLow, t70)}% TO ${cnt(k, n.topHigh, t73)}%` : `${cnt(k, n.topLow, t70)}% TO`, 173 + sl + d.tw(lab + ' '), 90, {color: CREAM});
      }
      /* the readout: the band the needle sits in, then yours, which nobody has measured yet */
      if (T >= tNever) lcd(k, d, 'YOURS: ?', Math.floor((T - tNever) * 2) % 2 ? RED : GOLD, 39);
      else if (T >= t70 + 0.6) lcd(k, d, `${n.topLow.shown} TO ${n.topHigh.shown}`, TEAL, 39);
      else lcd(k, d, `${n.medLow.shown} TO ${n.medHigh.shown}`, GOLD, 39);
      if (T >= t70 + 0.6 && T < t70 + 1.3) k.burst(GX * 3, (GY + 32) * 3, t70 + 0.6, {n: 16, r: 200, colors: ['teal', 'paper']});
      /* THE GAP, at the top of the dial, under the 50 */
      if (T >= tGap) { const f = d.fr(tGap + 0.35); if (f >= 0) { plate(d, GX - 34, 154, 68, 26, RED); k.slam('THE GAP', GX * 3, 157 * 3, tGap + 0.35, {size: 39, color: RED, align: 'center', from: 0.5}); } }
      /* under the hub: the source stays on to the end; the verdict stamps on a one-line red sticker below the gauge
         (frame y 930 to 1002, x 210 to 948), clear of the source line, the 0 and 100 labels and the dialog's name tag */
      k.text('ServiceTitan,', 540, 800, {size: 39, color: SAND, align: 'center'});
      k.text(`May to Jul ${n.stYear.shown}`, 540, 846, {size: 39, color: SAND, align: 'center'});
      if (T >= meas - 0.1) {
        k.stampIn(meas, () => {
          d.win(70, 310, 246, 24, {base: RED, hi: '#F09A9A', lo: WINE, rule: false});
          k.text("Can't close a gap you never measured.", 579, 945, {size: 39, color: CREAM, align: 'center'});
        }, {at: [579, 1002]});
      }
      return host(k, k.live('stakes.measure') ? 'point' : (k.live('stakes.gap') ? 'point' : null));
    },

    /* ---- formula: the neon sign. The formula is in tubes from the first frame (grey glass), and each tube switches on */
    /* as it is said; SCREENSHOT THIS lands with a camera flash; the month on a neon calendar is boxed on "same month" */
    formula: (k, T) => {
      const t0 = k.S('formula'), shot = k.S('formula.shot');
      const tC = wordT(k, 'formula.eq', /^Close$/i), tJ = wordT(k, 'formula.eq', /^jobs$/i, 1.5), tD = wordT(k, 'formula.div', /^divided$/i), tE = wordT(k, 'formula.div', /^estimates$/i, 1), tM = k.S('formula.month');
      /* the reflection on the pavement: one streak per lit tube, in its glow colour */
      const refl = [];
      if (T >= tC) refl.push([24, 190, RED]);
      if (T >= tJ) refl.push([60, 110, TEAL]);
      if (T >= tE) refl.push([40, 150, ORANGE]);
      if (T >= tM + 0.3) refl.push([30, 170, '#3B82C4']);
      const d = neonWall(k, refl.length ? refl : null);
      neon(k, 'THE MATH', 72, 288, t0 + 0.15, {size: 39, glow: ORANGE, core: '#FFE2A8'});
      /* the camera: the board flashes white for 2 frames, a tag lands */
      if (T >= shot) {
        const f = d.fr(wordT(k, 'formula.shot', /^Screenshot/i));
        if (f >= 0 && f < 2) d.P(NX0 + 2, NY0 + 2, NW - 4, NH - 4, '#FFFFFF');
        k.ctx.save(); k.ctx.translate(0, d.ease(shot, 6, -14) * 3); k.chip('Screenshot this', 300, 280, {size: 30, fill: 'accent', color: INK}); k.ctx.restore();
      }
      /* the formula: "Close rate =" big in white and red, the fraction in teal over amber, a teal tube for the line */
      neon(k, 'Close rate =', 72, 348, tC, {size: 132, glow: RED, core: CREAM});
      neon(k, 'jobs sold', 300, 504, tJ, {glow: TEAL, core: '#BDE6F5', align: 'center'});
      const bx = 32, by = 194, bw = 136;
      if (T >= tD) { const w = Math.min(bw, Math.round(bw * (d.fr(tD) + 1) / 8)); d.P(bx, by - 1, w, 3, TEAL); d.P(bx, by, w, 1, '#BDE6F5'); }
      else d.P(bx, by, bw, 1, '#4A4E5A');
      neon(k, 'estimates given', 300, 600, tE, {glow: '#B07A47', core: '#FFE2A8', align: 'center'});
      if (T >= tE + 0.6) k.burst(300, 630, tE + 0.6, {n: 16, r: 220});
      /* same month for both: the line lights blue, a neon calendar page beside the fraction, its month boxed in gold */
      neon(k, 'Same month for both.', 72, 696, tM + 0.3, {glow: '#3B82C4', core: CREAM});
      const cx0 = 206, cy0 = 174, cw = 96, ch = 56, calOn = T >= tM + 0.5;
      const cc = calOn ? '#F09A9A' : '#4A4E5A', ccg = calOn ? RED : null;
      if (ccg) { d.P(cx0 - 1, cy0 - 1, cw + 2, ch + 2, ccg); d.P(cx0 + 1, cy0 + 1, cw - 2, ch - 2, '#120D14'); }
      d.P(cx0, cy0, cw, 1, cc); d.P(cx0, cy0 + ch - 1, cw, 1, cc); d.P(cx0, cy0, 1, ch, cc); d.P(cx0 + cw - 1, cy0, 1, ch, cc);
      d.P(cx0, cy0 + 10, cw, 1, cc); [cx0 + 24, cx0 + cw - 26].forEach((x) => { d.P(x, cy0 - 4, 2, 8, cc); });
      for (let r = 0; r < 4; r++) for (let c = 0; c < 7; c++) d.P(cx0 + 7 + c * 12, cy0 + 16 + r * 10, 4, 3, calOn ? ((r * 7 + c) % 9 === 4 ? '#FFE2A8' : '#F09A9A') : '#3D2E45');
      if (T >= tM + 1.0) {   /* the gold box draws round the whole month, a pixel run a frame */
        const f = d.fr(tM + 1.0), x0 = cx0 - 5, y0 = cy0 - 8, w = cw + 10, h = ch + 13, len = 2 * (w + h), drawn = Math.round(len * Math.min(1, (f + 1) / 10));
        const seg = [[x0, y0, w, 0], [x0 + w, y0, 0, h], [x0 + w, y0 + h, -w, 0], [x0, y0 + h, 0, -h]];
        let left = drawn; seg.forEach(([sx, sy, dx, dy]) => { const l = Math.abs(dx + dy), u = Math.min(l, left); left -= u; if (u > 0) d.P(dx < 0 ? sx - u : sx, dy < 0 ? sy - u : sy, dx ? u : 2, dy ? u : 2, GOLD); });
      }
      return host(k, k.live('formula.shot') ? 'point' : (k.live('formula.month') ? 'point' : null));
    },

    /* ---- example: the inventory. Estimates and jobs sold are items; the close rate is crafted from them as it is said, */
    /* then it lands inside the median band, and an empty slot asks for yours */
    example: (k, T) => {
      const n = k.data.numbers, t0 = k.S('example');
      const t40 = wordT(k, 'example.forty', /^forty$/i), t14 = wordT(k, 'example.forty', /^fourteen/i, 2.5);
      const tDiv = wordT(k, 'example.div', /^Fourteen/i), t35 = wordT(k, 'example.div', /^thirty-five/i, 1.8), rng = k.S('example.range'), own = k.S('example.own');
      const items = [
        {icon: 'clip', name: 'ESTIMATES', stats: [{label: 'GIVEN', value: n.exEst.value, max: n.exEst.value, text: n.exEst.shown}]},
        {icon: 'hammer', name: 'JOBS SOLD', stats: [{label: 'SOLD', value: n.exSold.value, max: n.exEst.value, text: `${n.exSold.shown} OF ${n.exEst.shown}`}]},
      ];
      if (T >= t35) items.push({icon: 'star', name: 'CLOSE RATE', stats: [{label: 'RATE', value: n.exRate.value, max: 100, text: n.exRate.shown}]});
      if (T >= own) { while (items.length < 3) items.push(null); items.push({icon: 'clock', name: 'YOURS', stats: [{label: 'RATE', value: 0, max: 100, text: '?'}]}); }
      const sel = [{slot: 0, at: t40}, {slot: 1, at: t14}, {slot: 2, at: t35}, {slot: 3, at: own}];
      /* the set right-aligns its readout values at frame x 945; ours end at x 921, clear of a platform's right rail */
      const text0 = k.text;
      k.text = (s, x, y, o) => text0(s, o && o.align === 'right' && x === (16 + 178 + 121) * 3 ? 921 : x, y, o);
      try { k.sets.inventory({title: 'EXAMPLE: LAST MONTH', items, select: sel, hint: 'LAST MONTH'}); } finally { k.text = text0; }
      const d = px(k);
      /* the rest of the belt is stocked, dimmed (a checker of the slot's dark over each icon): the tools the example */
      /* doesn't use. Slot 2 stays empty for the close rate to be crafted into; slot 3 is yours, dim until "plug in yours" */
      [[3, 'clock'], [4, 'coin'], [5, 'phone'], [6, 'wrench'], [7, 'mail']].forEach(([i, ic]) => {
        if (items[i]) return;
        const sx = 16 + 12 + (i % 4) * 40, sy = 94 + 14 + Math.floor(i / 4) * 40;
        k.sets.icon(ic, sx + 7, sy + 7, 2); d.dith(sx + 2, sy + 2, 30, 30, '#1B1420', 0);
      });
      /* the crafted item sparkles into its slot; the empty YOURS slot shows a ? instead of an icon */
      if (T >= t35) { const f = d.fr(t35); if (f < 10) { d.twinkle(108 + 4, 108 + 4, f); d.twinkle(108 + 30, 108 + 28, f + 2); } k.burst(375, 375, t35, {n: 18, r: 180}); }
      if (T >= own) { d.P(149, 109, 32, 32, '#1B1420'); k.text('?', 495, 363, {size: 66, color: GOLD, align: 'center'}); }
      /* the recipe under the belt: 14 / 40 writes in as it is said, = 35% slams on "thirty-five" */
      const lhs = `${n.exSold.shown} / ${n.exEst.shown}`, eqx = 84 + k.measure(lhs + ' ', {size: 132});
      if (T < tDiv) k.text('__ / __', 84, 612, {size: 132, color: '#3B82C4', lint: false});
      else k.slam(lhs, 84, 612, tDiv, {size: 132, color: CREAM, from: 0.4, drop: INK});
      if (T < t35) k.text('= __', eqx, 612, {size: 132, color: '#3B82C4', lint: false});
      else k.slam(`= ${n.exRate.shown}`, eqx, 612, t35, {size: 132, color: 'accent', from: 0.6, drop: INK});
      if (T >= own) k.slam('Now yours: __ / __', 84, 756, own, {size: 39, color: GOLD, from: 0.4});
      /* the range strip under the window, on the dark gap above the band (frame y 825 to 885): a thin track that grows */
      /* from the left with the medians lit gold, a marker that drops in at 35%, the label under it */
      if (T >= rng) {
        const x0 = 24, w = 300, ax = (v) => x0 + Math.round((w * v) / 100), grow = Math.round(w * clamp((d.fr(rng) + 1) / 8));
        d.clip(x0 - 1, 274, grow + 2, 12, () => {
          d.P(x0 - 1, 278, w + 2, 6, INK); d.P(x0, 279, w, 4, '#3D2E45');
          for (let i = 1; i < 4; i++) d.P(x0 + (w * i) / 4, 280, 1, 2, '#6B7080');
          d.P(ax(n.medLow.value), 278, ax(n.medHigh.value) - ax(n.medLow.value), 6, GOLD);
        });
        const f = d.fr(rng + 0.35);
        if (f >= 0) d.clip(0, 274, 360, 12, () => { const mx = ax(n.exRate.value), dy = [-8, -5, -2, 1, 0][Math.min(4, f)]; d.P(mx - 1, 276 + dy, 3, 9, INK); d.P(mx, 277 + dy, 1, 7, CREAM); d.P(mx - 2, 275 + dy, 5, 3, RED); });
        if (grow >= w) {
          k.text(`Median ${n.medLow.shown} to ${n.medHigh.shown}`, 72, 852, {size: 39, color: GOLD});
          if (T >= rng + 0.5) k.text(`${n.exRate.shown} sits inside`, 72 + k.measure(`Median ${n.medLow.shown} to ${n.medHigh.shown}   `, {size: 39}), 852, {size: 39, color: CREAM});
        }
      }
      return host(k, k.live('example.own') ? 'point' : (k.live('example.range') ? 'point' : null));
    },

    /* ---- turn: the dispatch map once, as a map of shops where only some are ServiceTitan customers; then the ghost lap
       board: last month is the ghost car, this month races it (no map pins, no numbers: the number is the viewer's own) */
    turn: (k, T) => {
      const n = k.data.numbers, t0 = k.S('turn'), cnt0 = k.S('turn.count'), cust = k.S('turn.cust'), ownT = k.S('turn.own'), yours = k.S('turn.yours');
      const tShops = wordT(k, 'turn.cust', /^customers/i, 0.6), tLast = wordT(k, 'turn.yours', /^last/i, 1.6);
      const wipe = 10;   /* frames the lap board takes to close over the map, in blinds */
      if (T < ownT + wipe / 30) {
        const stPins = [[0.47, 0.28], [0.56, 0.42], [0.42, 0.47], [0.62, 0.24]];
        k.sets.dispatch({pins: []});
        const d = px(k);
        /* the set's board, its map redrawn as a plain town grid (no river, lakefront or avenue: no real city implied): */
        /* blocks with roofs, a park, streets every 22 pixels */
        d.clip(18, 82, 324, 196, () => {
          d.P(18, 82, 324, 196, '#E6D3BC');
          for (let by = 82; by < 278; by += 22) for (let bx = 18; bx < 342; bx += 22) { const r = hash(bx * 0.37 + by * 1.3); for (let j = 0; j < 3; j++) { const rx = bx + 4 + Math.floor(hash(r * 9 + j) * 10), ry = by + 4 + Math.floor(hash(r * 7 + j * 3) * 10); d.P(rx, ry, 4, 3, '#B39A88'); d.P(rx, ry, 4, 1, '#F4E6D3'); } }
          d.P(290, 100, 40, 38, '#3E7A62'); d.dith(290, 100, 40, 38, '#2F5A4A'); [[8, 8], [24, 12], [14, 26], [30, 28]].forEach(([a, b]) => { d.disc(290 + a, 100 + b, 3, '#24453A'); d.DOT(289 + a, 99 + b, '#6FB7A8'); });
          for (let x = 38; x < 342; x += 22) { d.P(x, 82, 3, 196, '#FFF7EA'); d.P(x + 3, 82, 1, 196, '#C9CCD3'); }
          for (let y = 102; y < 278; y += 22) { d.P(18, y, 324, 3, '#FFF7EA'); d.P(18, y + 3, 324, 1, '#C9CCD3'); }
        });
        /* the ServiceTitan pins, as the set drops them: a bounce, a shadow, one ping */
        if (T >= tShops) stPins.forEach(([nx, ny], i) => {
          const f = d.fr(tShops + i * 0.12); if (f < 0) return;
          const x = Math.round(18 + nx * 324), y = Math.round(82 + ny * 196), dy = [-20, -14, -8, -3, 0, -3, -1, 0][Math.min(7, f)];
          if (f >= 4) d.P(x - 3, y + 1, 7, 2, '#B39A88');
          if (f >= 6 && f < 24) d.ring(x, y, 4 + Math.floor((f - 6) / 2), TEAL);
          d.P(x - 1, y - 8 + dy, 2, 9, '#4A4E5A'); d.DOT(x - 1, y - 8 + dy, '#9AA0AD');
          d.disc(x, y - 12 + dy, 7, INK); d.disc(x, y - 12 + dy, 6, TEAL); d.disc(x + 1, y - 11 + dy, 4, '#245752'); d.disc(x - 1, y - 13 + dy, 4, TEAL); d.P(x - 3, y - 15 + dy, 2, 2, CREAM);
        });
        /* the shops: every one on the map, before the pins say which are ServiceTitan's */
        const SH = [[40, 100], [90, 96], [150, 104], [232, 92], [60, 150], [130, 140], [200, 150], [252, 132], [30, 210], [110, 200], [170, 190], [240, 196], [70, 250], [150, 246], [210, 240], [262, 236]];
        SH.forEach(([x, y], i) => { const on = T >= tShops && [2, 5, 6, 3].includes(i); shop(d, x, y + (d.fr(t0 + i * 0.06) < 4 && d.fr(t0 + i * 0.06) >= 0 ? -2 : 0), on ? TEAL : '#9AA0AD'); });
        /* the coverage line round the customers, dashes marching */
        if (T >= tShops) { const x0 = 124, y0 = 88, w = 128, h = 76, ph = Math.floor(d.F / 4) % 6; for (let i = -ph; i < w; i += 6) { d.P(x0 + Math.max(0, i), y0, Math.min(3, w - Math.max(0, i)), 1, TEAL); d.P(x0 + Math.max(0, i), y0 + h, Math.min(3, w - Math.max(0, i)), 1, TEAL); } for (let j = -ph; j < h; j += 6) { d.P(x0, y0 + Math.max(0, j), 1, Math.min(3, h - Math.max(0, j)), TEAL); d.P(x0 + w, y0 + Math.max(0, j), 1, Math.min(3, h - Math.max(0, j)), TEAL); } }
        /* the notes on the map: plates 44 tall so both lines sit inside, the second one ending by x 310 (frame 930) */
        if (T >= cnt0) { const sl = d.ease(cnt0, 8, -60); plate(d, 22 + sl, 222, 210, 44, RED); k.text('How it counts a close:', (30 + sl) * 3, 228 * 3, {size: 39, color: CREAM}); k.text('not on the page.', (30 + sl) * 3, 243 * 3, {size: 39, color: RED}); }
        if (T >= cust) { const sl = d.ease(cust, 8, 40); plate(d, 110 + sl, 170, 200, 44, TEAL); k.text('ServiceTitan customers.', (118 + sl) * 3, 176 * 3, {size: 39, color: TEAL}); k.text('Not every shop.', (118 + sl) * 3, 191 * 3, {size: 39, color: CREAM}); }
        /* under the map: the heading and its source line, both on until the lap board takes over */
        plate(d, 14, 280, 300, 48);
        k.slam('The part people skip', 72, 852, t0 + 0.1, {size: 66, color: 'accent', from: 0.6, drop: INK});
        if (T >= t0 + 0.1) k.text(`ServiceTitan's medians, May to Jul ${n.stYear.shown}`, 72, 930, {size: 39, color: SAND});
      }
      if (T >= ownT) {
        /* the lap board closes over the map in 16 blinds, then holds */
        const f = Math.floor((T - ownT) * 30 + 0.005), q = clamp((f + 1) / wipe);
        const draw = () => {
          const d = ghostBoard(k, {t0: ownT, tLast});
          plate(d, 12, 216, 336, 58, GOLD);
          k.slam('First number to beat:', 60, 666, ownT + 0.1, {size: 39, color: CREAM, from: 0.4});
          if (T >= yours) { k.slam('Your own, last month.', 60, 714, yours, {size: 66, color: 'accent', stamp: true, drop: INK}); k.burst(600, 760, yours + 0.12, {n: 20, r: 240}); }
        };
        if (q >= 1) draw();
        else { k.ctx.save(); k.ctx.beginPath(); for (let i = 0; i < 16; i++) k.ctx.rect(0, i * 120, 1080, Math.round(40 * q) * 3); k.ctx.clip(); draw(); k.ctx.restore(); }
      }
      return host(k, k.live('turn.yours') ? 'point' : (k.live('turn.count') ? 'shrug' : null));
    },

    /* ---- weekly: the Friday board. Two rows written up and ticked as they are said; slips flip SOLD on "jobs sold"; */
    /* a sticky note stamps on: that's all you need */
    weekly: (k, T) => {
      const t0 = k.S('weekly'), all = k.S('weekly.all');
      const tFri = wordT(k, 'weekly', /^Friday/i, 0.8), tEst = wordT(k, 'weekly.two', /^estimates/i, 1.8), tJobs = wordT(k, 'weekly.two', /^jobs/i, 2.9);
      const sold = {}; [0, 4, 2, 6, 10, 8].forEach((i, j) => { sold[i] = tJobs + 0.15 + j * 0.15; });
      const d = board(k, {sold, inHand: T >= tFri && T < all ? 1 : null});
      write(k, 'Every Friday', 72, 282, t0 + 0.2, {color: RED});
      if (T >= tFri) k.sweep(72, 352, k.measure('Every Friday', {size: 66}), 6, tFri, {color: RED});
      /* the rows: shown as the board opens (faint), written in marker when they are said */
      const row = (s, y, at, c) => { if (T < at) { k.text(s, 72, y, {size: 66, color: '#E6D3BC', lint: false}); return; } write(k, s, 72, y, at, {color: c}); };
      row('Estimates given', 400, tEst, NAVY);
      row('Jobs sold', 500, tJobs, PINE);
      [400, 500].forEach((y) => d.P(24, y / 3 + 26, 200, 1, '#C9CCD3'));
      /* a box beside each row, ticked once the row is written (the check draws on, a pixel a frame) */
      const tick = (x, y, at, c) => { d.P(x, y, 18, 18, '#C9CCD3'); d.P(x + 2, y + 2, 14, 14, CREAM); const f = d.fr(at + 0.4); if (f < 0) return; const pts = [[x + 3, y + 9], [x + 7, y + 14], [x + 17, y + 1]]; const n1 = Math.min(5, f + 1), n2 = Math.max(0, Math.min(11, f - 4)); d.line(pts[0][0], pts[0][1], pts[0][0] + Math.round((pts[1][0] - pts[0][0]) * n1 / 5), pts[0][1] + Math.round((pts[1][1] - pts[0][1]) * n1 / 5), c, 2); if (n2 > 0) d.line(pts[1][0], pts[1][1], pts[1][0] + Math.round((pts[2][0] - pts[1][0]) * n2 / 11), pts[1][1] + Math.round((pts[2][1] - pts[1][1]) * n2 / 11), c, 2); };
      tick(204, 132, tEst, NAVY); tick(204, 166, tJobs, PINE);
      /* the sticky note: that's all you need */
      if (T >= all) {
        k.stampIn(all, () => {
          d.P(22, 233, 206, 70, '#B07A47'); d.P(20, 231, 206, 70, GOLD); d.P(20, 231, 206, 6, ORANGE);
          k.text("That's all", 72, 726, {size: 66, color: INK});
          k.text('you need.', 72, 802, {size: 66, color: RED});
        }, {at: [330, 903], drop: 0.08});
      }
      return host(k, k.live('weekly.all') ? 'point' : (k.live('weekly.two') ? 'point' : null));
    },

    /* ---- close: the levelup set. The XP bar fills on "Jobs sold" and it levels up on "divided", so the rays and */
    /* LEVEL UP! fill the sky under a second in; the LV 2 bar flashes full, then fills gold from "given". The formula is */
    /* the perk, the biggest words on screen: + CLOSE RATE = / JOBS SOLD / / ESTIMATES GIVEN in three rows at size 99 */
    /* (66 px caps) under the bar, shown faint from the first frame and lit part by part as it is said. The send line */
    /* lands on a plate over the rays; the last perk line (+ Friday: your close rate.) and the ProofNotFluff tag share */
    /* the row between LEVEL UP! and the bar. */
    close: (k, T) => {
      const t0 = k.S('close'), send = k.S('close.send'), fri = k.S('close.friday');
      const tJ = wordT(k, 'close', /^Jobs/i), tD = wordT(k, 'close', /^divided/i, 0.6), tE = wordT(k, 'close', /^estimates/i, 1.5), tG = wordT(k, 'close', /^given/i, 2.0), tF = wordT(k, 'close.friday', /^close$/i, 1.8);
      const lvAt = tD + 0.15;
      k.sets.levelup({from: 30, to: 100, max: 100, at: t0, dur: Math.max(0.5, lvAt - t0), levelAt: lvAt, level: 1});
      const d = px(k), {P} = d;
      /* the LV 2 bar (the set's X 30, Y 208, 20 segments of 14): a 2-frame full flash as it levels up, then its first */
      /* four segments step in gold on "given" (one every 2 frames), two more on "Send" and two more on "close" */
      if (T >= lvAt) {
        const X = 30, Y = 208, W = 280, sw = W / 20, f = d.fr(lvAt);
        if (f >= 0 && f < 2) P(X, Y, W, 14, CREAM);
        const steps = [[tG, 4], [send, 6], [tF, 8]]; let lit = 0;
        steps.forEach(([at, to], j) => { if (T >= at) lit = Math.min(to, (j ? steps[j - 1][1] : 0) + Math.floor(d.fr(at) / 2) + 1); });
        for (let i = 0; i < lit; i++) { const x = Math.round(X + i * sw); P(x + 1, Y + 1, Math.round(sw) - 2, 12, GOLD); P(x + 1, Y + 1, Math.round(sw) - 2, 3, '#FFE2A8'); P(x + 1, Y + 10, Math.round(sw) - 2, 3, ORANGE); }
      }
      /* the formula perk: a teal + at frame x 48, rows 99 apart at y 669, 768 and 867 (caps ink 699 to 963, under the */
      /* bar's 672 and above Snow's cap at 976 and the floor band at 990; rows 99 apart keep the lint's font boxes under */
      /* 15 per cent overlap); ESTIMATES GIVEN ends at frame x 900. Unlit parts are grey glass */
      const big = (s, x, y, at, c) => { if (T < at) k.text(s, x, y, {size: 99, color: '#4A4E5A', lint: false}); else k.text(s, x, y, {size: 99, color: c, drop: INK}); };
      k.text('+', 48, 669, {size: 99, color: TEAL, drop: INK});
      big('CLOSE RATE =', 108, 669, t0, CREAM);
      big('JOBS SOLD', 108, 768, tJ, TEAL);
      big('/', 108 + k.measure('JOBS SOLD ', {size: 99}), 768, tD, CREAM);
      big('ESTIMATES GIVEN', 108, 867, tE, GOLD);
      if (T >= tE + 0.1 && T < tE + 0.9) k.burst(504, 930, tE + 0.1, {n: 16, r: 220});
      /* the Friday perk line, between LEVEL UP! (ink to 456) and the LV label (ink from 579): frame y 498, ink 507 to 528 */
      if (T >= fri + 0.1) {
        const sl = d.ease(fri + 0.1, 5, 30);
        d.tx('+', 20 + sl, 166, {color: TEAL, drop: INK});
        d.tx('Friday: your close rate.', 32 + sl, 166, {color: CREAM, drop: INK});
      }
      if (T >= tF) k.sweep(96, 540, k.measure('Friday: your close rate.', {size: 39}), 3, tF, {color: 'accent'});
      /* the send line, one line on its own plate over the rays (frame y 258 to 336); the ProofNotFluff tag lands straight */
      /* in its slot in the Friday row (frame x 600 to 912, y 489 to 541), right of where the Friday line will be, with a */
      /* ping round it, and never crosses the formula */
      if (T >= send) {
        plate(d, 12, 86, 336, 26, GOLD);
        k.slam('Send this to whoever writes your estimates.', 60, 279, send + 0.1, {size: 39, color: CREAM, from: 0.1});
        if (T >= send + 0.3) { const c = k.chip('ProofNotFluff', 600, 489, {size: 30}); d.ping(send + 0.3, 200, 163, Math.round(c.w / 3), Math.round(c.h / 3), GOLD); }
      }
      return host(k, k.live('close.friday') ? 'wave' : (k.live('close.send') ? 'point' : null));
    },
  },
};
