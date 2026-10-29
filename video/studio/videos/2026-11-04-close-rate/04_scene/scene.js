// Scene: Know your close rate (Lesson 8, Numbers Clinic, arcade). One function per top-level cue in 03_cues/cues.md.
// Numbers only from k.data (brief.md -> data.js). Every time comes from a cue start (k.S) or a spoken word (wordT), so a
// re-voiced take moves the picture with it.
// Worlds, one per section: hook = the dispatch board as a territory map (West and Northeast light with their medians);
// stakes = the gauge (the median band, the top quarter's band, the gap between them); formula, weekly and close = the
// Friday board drawn here (a whiteboard written in marker beside a cork strip of estimate slips that flip SOLD);
// example = the inventory (estimates and jobs sold as items, the close rate crafted from them); turn = the dispatch
// board again, now a map of shops where only some are ServiceTitan customers, and YOUR pin drops.
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', GREY = '#9AA0AD';
const NAVY = '#253048', WINE = '#7A3442', PINE = '#2F6F67';
const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eo = (x) => 1 - Math.pow(1 - clamp(x), 3);

// ---- the pixel kit (low-res units: 360 x 640, one pixel = 3 frame units), the same primitives the sets use ----
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
  // a ring that steps out from a box for 12 frames (a ping; never on frame 0, its times all come after the cover)
  const ping = (t0, x, y, w, h, c = CREAM) => { const f = fr(t0); if (f >= 0 && f < 12) { const g = 1 + f; P(x - g, y - g, w + 2 * g, 1, c); P(x - g, y + h + g, w + 2 * g, 1, c); P(x - g, y - g, 1, h + 2 * g, c); P(x + w + g, y - g, 1, h + 2 * g + 1, c); } };
  return {P, DOT, dith, disc, ring, line, win, fr, ease, tx, tw, clip, twinkle, ping, F, T};
};

// ---- the words: every beat lands on a spoken word ----
const WS = () => (window.WORDS && window.WORDS.words) || [];
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
// a count that starts at 85% of its value and lands exactly on it
const cnt = (k, num, t0, o = {}) => k.count(num.value, k.lin(t0, t0 + 0.7) >= 1 ? 1 : 0.85 + 0.15 * k.lin(t0, t0 + 0.7), Object.assign({from: 0}, o));
const host = (k, pose) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150});
// a dark plate for words over a busy set (low-res box)
const plate = (d, x, y, w, h, edge = '#3D2E45') => d.win(x, y, w, h, {base: '#1B1420', hi: edge, lo: INK, rule: edge});

// ================================================================================================================
// the territory map (hook, turn): the library dispatch board, with territories tinted on the map
const MX = 18, MY = 82, MW = 324, MH = 196;
const territory = (d, x, y, w, h, c, edge, ph) => d.clip(MX, MY, MW, MH, () => {
  d.dith(x, y, w, h, c, ph);
  d.P(x, y, w, 2, edge); d.P(x, y + h - 2, w, 2, edge); d.P(x, y, 2, h, edge); d.P(x + w - 2, y, 2, h, edge);
});
// a small shop on the map (a roof and a door), 9 x 8, grey for any shop, teal-roofed when it is a ServiceTitan customer
const shop = (d, x, y, c) => { d.P(x - 1, y + 2, 11, 7, INK); d.P(x, y + 3, 9, 5, '#C9CCD3'); d.P(x + 3, y + 5, 3, 3, '#4A4E5A'); d.P(x - 1, y, 11, 3, INK); d.P(x, y, 9, 2, c); };

// ================================================================================================================
// the Friday board (formula, weekly, close): our own set piece. A pegboard wall in the shop, an aluminium-framed
// whiteboard written in marker, a cork strip of estimate slips (each slip says $, $$ or $$$ once the dollars come in,
// and flips over to a red SOLD back), a marker tray with an eraser, a shop stool and the concrete floor.
// Whiteboard writing area (frame units): x 54 to 708 (or 1002 with no cork), y 270 to 918.
const BX = 14, BY = 84, BW = 222, BH = 226, CX0 = 242;
const SLIPS = [   // the cork strip: three columns, four rows, each a little off the grid; q is the quote size
  [250, 98, 1], [282, 102, 3], [313, 97, 1],
  [251, 141, 2], [283, 144, 1], [314, 139, 3],
  [249, 184, 1], [282, 186, 2], [313, 182, 1],
  [251, 226, 3], [283, 228, 1], [314, 224, 2],
];
const board = (k, o = {}) => {
  const d = px(k), {P, DOT, dith, F, T, fr} = d, cork = o.cork !== false, W = cork ? BW : 332;
  // the wall: pegboard (a hole every 6 pixels), a light from above, a baseboard
  P(0, 0, 360, 417, '#8C5A33');
  for (let y = 3; y < 330; y += 6) for (let x = 3 + ((y / 6) & 1) * 3; x < 360; x += 6) DOT(x, y, '#6B4226');
  dith(0, 0, 360, 40, '#B07A47', 0);
  P(0, 330, 360, 6, '#4A2E1B'); P(0, 330, 360, 1, '#B07A47');
  P(0, 336, 360, 81, '#5A3A22'); for (let x = 0; x < 360; x += 24) P(x, 336, 1, 81, '#4A2E1B');
  // the floor: sealed concrete, a crack, an oil spot
  P(0, 417, 360, 223, '#4A4E5A'); for (let y = 417; y < 640; y += 18) P(0, y, 360, 1, '#3D2E45');
  dith(0, 417, 360, 4, '#6B7080', 1); d.line(40, 470, 92, 520, '#3D2E45'); d.line(92, 520, 120, 600, '#3D2E45'); dith(250, 520, 40, 10, '#2B2033');
  // the whiteboard: a drop shadow, the aluminium frame (light top-left), the white with ghosted old writing
  P(BX + 3, BY + 3, W + 6, BH + 6, INK);
  P(BX - 3, BY - 3, W + 6, BH + 6, INK); P(BX - 2, BY - 2, W + 4, BH + 4, '#C9CCD3'); P(BX - 2, BY - 2, W + 4, 1, CREAM); P(BX - 2, BY - 2, 1, BH + 4, CREAM); P(BX + W + 1, BY - 1, 1, BH + 3, '#6B7080'); P(BX - 1, BY + BH + 1, W + 3, 1, '#6B7080');
  P(BX, BY, W, BH, CREAM);
  dith(BX + 6, BY + 150, 70, 4, '#F4E6D3', 1); dith(BX + 120, BY + 40, 60, 3, '#F4E6D3', 0); dith(BX + 30, BY + 200, 120, 3, '#F4E6D3', 1);
  // a glare that steps across the board once every 5 s (whole pixels, never on frame 0)
  if (T > 0.6) { const g = Math.floor(((T - 0.6) % 5) * 30); if (g < 40) { const gx = BX - 40 + g * Math.round((W + 80) / 40); for (let j = 0; j < BH; j++) { const xx = gx + Math.floor(j * 0.35); if (xx >= BX && xx + 2 < BX + W) { DOT(xx, BY + BH - 1 - j, '#FFFFFF'); DOT(xx + 1, BY + BH - 1 - j, '#FFFFFF'); } } } }
  // the tray, three markers and the eraser
  const ty = BY + BH + 2;
  P(BX - 4, ty, W + 8, 5, INK); P(BX - 3, ty, W + 6, 3, '#9AA0AD'); P(BX - 3, ty, W + 6, 1, CREAM);
  [[BX + 10, NAVY], [BX + 30, RED], [BX + 50, PINE]].forEach(([x, c], i) => { if (o.inHand !== i) { P(x, ty - 3, 14, 4, INK); P(x + 1, ty - 2, 9, 2, CREAM); P(x + 10, ty - 2, 3, 2, c); } });
  P(BX + W - 34, ty - 6, 24, 7, INK); P(BX + W - 33, ty - 5, 22, 3, '#3B82C4'); P(BX + W - 33, ty - 2, 22, 2, '#C9CCD3');
  // the cork strip
  if (cork) {
    const cx = CX0, cw = 104;
    P(cx - 3, BY - 3, cw + 6, BH + 6, INK); P(cx - 2, BY - 2, cw + 4, BH + 4, '#6B4226'); P(cx - 2, BY - 2, cw + 4, 1, '#B07A47');
    P(cx, BY, cw, BH, '#B07A47'); dith(cx, BY, cw, BH, '#8C5A33', 0);
    for (let i = 0; i < 70; i++) DOT(cx + Math.floor(hash(i * 2.7) * cw), BY + Math.floor(hash(i * 5.3) * BH), '#D9A066');
    if (o.corkTitle) { P(cx + 8, BY + 2, cw - 16, 9, INK); P(cx + 9, BY + 3, cw - 18, 7, '#F4E6D3'); }
    (o.slips || SLIPS).forEach((s, i) => slip(d, k, s, i, o));
  }
  // the stool by the board (when the host is not standing there it still holds the room together)
  P(300, 372, 44, 5, INK); P(301, 372, 42, 3, '#D9A066'); P(306, 377, 3, 40, '#6B4226'); P(335, 377, 3, 40, '#6B4226'); P(306, 398, 32, 2, '#6B4226');
  return d;
};
// one estimate slip: a paper slip on a pin. o.sold[i] is when it flips to SOLD (it narrows to its edge on whole pixels,
// then opens on its red back), o.dollars is when the quote size is written on it, o.fall {i, at} drops it off the cork.
const slip = (d, k, s, i, o) => {
  const {P, DOT, fr, T} = d, [x0, y0, q] = s, w = 26, h = 34;
  let x = x0, y = y0, tilt = 0;
  const fall = o.fall && o.fall.i === i ? o.fall : null;
  if (fall && T >= fall.wobble && T < fall.at) tilt = (Math.floor((T - fall.wobble) * 6) % 2) ? 1 : -1;   // 3 swings a second
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
  // the pin (it stays on the cork when the slip falls)
  P(x0 + w / 2 - 2, y0 - 2, 5, 5, INK); P(x0 + w / 2 - 1, y0 - 1, 3, 3, i % 3 === 1 ? '#3B82C4' : RED); DOT(x0 + w / 2 - 1, y0 - 1, CREAM);
};
// a month grid on a calendar page: 7 columns of day boxes
const DOTS = (d, x, y, w, h) => { for (let r = 0; r < 5; r++) for (let c = 0; c < 7; c++) d.P(x + 1 + c * Math.floor(w / 7), y + r * Math.floor(h / 5), Math.floor(w / 7) - 2, Math.floor(h / 5) - 2, (r * 7 + c) % 9 === 4 ? '#C9CCD3' : '#E6D3BC'); };
// marker writing: the line appears left to right (whole pixels) with the marker's tip riding the head of the ink
const write = (k, s, x, y, t0, o = {}) => {
  if (k.T < t0) return false;
  const d = px(k), size = o.size || 66, w = k.measure(s, {size}), frames = Math.max(5, Math.min(14, Math.round(s.length * 0.6)));
  const f = d.fr(t0), q = t0 <= 0 ? 1 : clamp((f + 1) / frames);
  const ax = o.align === 'center' ? x - w / 2 : (o.align === 'right' ? x - w : x), shown = Math.round((w * q) / 3) * 3;
  k.ctx.save(); k.ctx.beginPath(); k.ctx.rect(ax - 6, y - 12, shown + 6, size * 1.4); k.ctx.clip();
  k.text(s, x, y, {size, color: o.color || NAVY, align: o.align, lint: q >= 1});
  k.ctx.restore();
  if (q < 1) {   // the marker: a cap and a coloured tip at the head
    const hx = Math.round((ax + shown) / 3), hy = Math.round((y + size * 0.55) / 3);
    d.P(hx, hy - 12, 4, 12, INK); d.P(hx + 1, hy - 11, 2, 10, CREAM); d.P(hx + 1, hy - 3, 2, 3, o.color || NAVY);
  }
  return true;
};

// ================================================================================================================
// the gauge (stakes): the library gauge; the needle is driven here (value given each frame, settled), the bands and
// the gap are painted on its rim, the readout is our own LCD text
const GX = 180, GY = 214, GR = 100;
const gAng = (v) => (135 + 2.7 * v) * Math.PI / 180;
const rim = (d, v0, v1, c, r0 = GR - 8, r1 = GR - 3) => { for (let a = gAng(v0); a <= gAng(v1) + 1e-6; a += 0.006) for (let r = r0; r <= r1; r++) d.DOT(GX + Math.round(Math.cos(a) * r), GY + Math.round(Math.sin(a) * r), c); };
const lcd = (k, d, s, c = GOLD, size = 66) => { d.P(GX - 37, GY + 19, 74, 28, '#1A332B'); d.P(GX - 36, GY + 20, 72, 26, '#24453A'); d.tx(s, GX, size >= 60 ? GY + 22 : GY + 27, {size, color: c, align: 'center'}); };

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 8',
  transitions: {stakes: 'levelselect', formula: 'blinds', example: 'dissolve', turn: 'iris', weekly: 'door', close: 'gameover'},
  trauma: {'turn.yours': 0.8},
  sections: {
    // ---- hook: the territory map, settled on frame 0 (both regions, both medians, the claim and its source); pings,
    // a sweep and the van's route bring it to life right after; the dialog and host wait until the range has been said
    hook: (k, T) => {
      const n = k.data.numbers, d = px(k);
      const t31 = wordT(k, 'hook', /^thirty-one/i, 2.4), t38 = wordT(k, 'hook', /^thirty-eight/i, 3.3), tYours = wordT(k, 'hook.yours', /^yours/i, 0.5);
      const src = k.S('hook.source'), win = k.S('hook.window'), yours = k.S('hook.yours'), math = k.S('hook.math');
      k.sets.dispatch({
        pins: [{x: 0.13, y: 0.857, at: -1, c: TEAL}, {x: 0.815, y: 0.235, at: -1, c: RED}, {x: 0.377, y: 0.602, at: tYours, c: GOLD}],
        routes: [{pts: [[0.815, 0.235], [0.815, 0.755], [0.13, 0.755], [0.13, 0.857]], at: t31, dur: Math.max(0.6, t38 - t31 + 0.3), c: ORANGE}],
      });
      // the territories: West (left, teal) and Northeast (upper right, orange), each with its median, big
      territory(d, 18, 82, 86, 196, TEAL, PINE, 0);
      territory(d, 192, 82, 82, 86, ORANGE, '#B07A47', 1);
      plate(d, 24, 154, 74, 66, PINE);
      d.tx('WEST', 61, 159, {align: 'center', color: TEAL});
      k.text(n.medHigh.shown, 183, 528, {size: 132, color: CREAM, align: 'center', drop: INK});
      plate(d, 168, 90, 100, 66, '#B07A47');
      d.tx('NORTHEAST', 218, 95, {align: 'center', color: ORANGE});
      k.text(n.medLow.shown, 654, 336, {size: 132, color: CREAM, align: 'center', drop: INK});
      // life after the cover: each median pings as it is said (a first ping before, so the cover breathes)
      d.ping(0.7, 168, 90, 100, 66, ORANGE); d.ping(1.5, 24, 154, 74, 66, TEAL);
      d.ping(t31, 168, 90, 100, 66, CREAM); d.ping(t38, 24, 154, 74, 66, CREAM);
      k.burst(846, 340, t31 + 0.1, {n: 18, r: 200}); k.burst(180, 720, t38 + 0.1, {n: 18, r: 200, colors: ['teal', 'paper', 'accent2']});   // sparks off the pins, clear of the numbers
      // YOURS: the gold pin's label, then the clinic tag
      if (T >= tYours) {
        const f = d.fr(tYours), dy = [-10, -6, -2, 1, 0][Math.min(4, f)];
        plate(d, 154, 172 + dy, 64, 30, GOLD);
        k.text('Yours?', 558, (178 + dy) * 3, {size: 66, color: GOLD, align: 'center', drop: INK});
        if (Math.floor((T - tYours) * 2) % 2 === 1) d.ping(tYours + Math.floor((T - tYours) * 2) * 0.5, 154, 172, 64, 30, GOLD);
      }
      if (T >= math) { k.ctx.save(); k.ctx.translate(0, d.ease(math, 6, 20) * 3); k.chip('Numbers Clinic', 474, 648, {size: 30, fill: 'accent', color: INK}); k.ctx.restore(); }
      // the claim and its source under the map, on a plate (the mug and the radio stay clear to its right)
      plate(d, 14, 280, 246, 48);
      k.text('Median close rate, by region', 72, 852, {size: 66, color: CREAM, drop: INK});
      const lit = T >= src, wl = T >= win;
      k.text('ServiceTitan customers,', 72, 930, {size: 39, color: lit ? GOLD : SAND});
      k.text(`May to Jul ${n.stYear.shown}`, 72 + k.measure('ServiceTitan customers, ', {size: 39}), 930, {size: 39, color: wl ? GOLD : SAND});
      if (lit) k.sweep(72, 966, k.measure('ServiceTitan customers,', {size: 39}), 6, src + 0.1, {color: 'teal'});
      if (wl) k.sweep(72 + k.measure('ServiceTitan customers, ', {size: 39}), 966, k.measure(`May to Jul ${n.stYear.shown}`, {size: 39}), 6, win + 0.1, {color: 'teal'});
      if (T < k.S('hook.region')) return {host: false, speech: false};
      return host(k, k.live('hook.yours') ? 'point' : (k.live('hook.math') ? 'clip' : null));
    },

    // ---- stakes: the gauge. The median band is lit; the top quarter's band lights when it is named; the needle swings
    // to it as the numbers are said; the gap fills red on the rim; then the readout has nothing to show
    stakes: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('stakes');
      const tTop = wordT(k, 'stakes', /^top$/i, 0.6), tRank = wordT(k, 'stakes.ranked', /^ranked/i), t70 = wordT(k, 'stakes.top', /^seventy$/i, 0.9), t73 = wordT(k, 'stakes.top', /^seventy-three/i, 1.7);
      const tGap = wordT(k, 'stakes.gap', /^big/i, 0.6), meas = k.S('stakes.measure'), tNever = wordT(k, 'stakes.measure', /^never/i, 1.7);
      // the needle: in the median band on entry, out to the top quarter on "seventy", back to zero on "never"
      const mid = (n.medLow.value + n.medHigh.value) / 2, top = (n.topLow.value + n.topHigh.value) / 2;
      const swing = (a, b, at, dur = 0.7) => { const q = clamp((T - at) / dur); if (q <= 0) return a; if (q >= 1) return b; const ov = Math.sin(q * Math.PI * 2.2) * (1 - q) * 0.12; return a + (b - a) * (eo(q * 1.4) + ov); };
      let v = swing(0, mid, t0 + 0.25, 0.8);
      if (T >= t70) v = swing(mid, top, t70, 0.9);
      if (T >= tNever) v = swing(top, 0, tNever, 0.6);
      // the set's own readout sits under our LCD; it is not drawn at all (hidden text still counts for the layout lint)
      const text0 = k.text;
      k.text = (s, x, y, o) => (o && o.size === 66 && y === (GY + 22) * 3 ? {w: 0, h: 0, lines: []} : text0(s, x, y, o));
      try { k.sets.gauge({value: Math.max(0, v), at: -10, dur: 1, zones: [[0, 100, '#3D2E45']]}); } finally { k.text = text0; }
      // the bands on the rim: the median (gold) from the start, the top quarter (teal) when it is named
      rim(d, n.medLow.value, n.medHigh.value, GOLD, GR - 10, GR - 2);
      if (T >= tTop) rim(d, n.topLow.value, n.topHigh.value, T >= tRank ? TEAL : '#4A4E5A', GR - 10, GR - 2);
      // the gap: the rim between the two bands fills red a step at a time
      if (T >= tGap) { const q = clamp(d.fr(tGap) / 12); rim(d, n.medHigh.value + 1, n.medHigh.value + 1 + (n.topLow.value - n.medHigh.value - 2) * q, RED, GR - 6, GR - 5); }
      // the corner plates, a leader line from each to its band
      const L = gAng((n.medLow.value + n.medHigh.value) / 2), Rr = gAng(top);
      plate(d, 10, 88, 128, 44, GOLD);
      d.tx('MEDIAN SHOP', 18, 93, {color: GOLD});
      d.tx(`${n.medLow.shown} TO ${n.medHigh.shown}`, 18, 111, {color: CREAM});
      d.line(74, 132, GX + Math.round(Math.cos(L) * (GR + 14)), GY + Math.round(Math.sin(L) * (GR + 14)), GOLD);
      if (T >= tTop) {
        const sl = d.ease(tTop, 8, 40), lit = T >= tRank;
        plate(d, 212 + sl, 88, 112, 44, lit ? TEAL : '#4A4E5A');
        d.tx(`TOP ${n.topShare.shown}`, 220 + sl, 93, {color: lit ? TEAL : GREY});
        if (T >= t70) d.tx(T >= t73 ? `${cnt(k, n.topLow, t70)}% TO ${cnt(k, n.topHigh, t73)}%` : `${cnt(k, n.topLow, t70)}% TO`, 220 + sl, 111, {color: CREAM});
        else d.tx('BY CLOSE RATE', 220 + sl, 111, {color: lit ? CREAM : GREY});
        if (sl === 0) d.line(268, 132, GX + Math.round(Math.cos(Rr) * (GR + 14)), GY + Math.round(Math.sin(Rr) * (GR + 14)), lit ? TEAL : GREY);
      }
      // the readout: the band the needle sits in, then nothing to read
      if (T >= tNever) lcd(k, d, '?%', Math.floor((T - tNever) * 2) % 2 ? RED : GOLD);
      else if (T >= t70 + 0.6) lcd(k, d, `${n.topLow.value} TO ${n.topHigh.value}`, TEAL, 39);
      else lcd(k, d, `${n.medLow.value} TO ${n.medHigh.value}`, GOLD, 39);
      if (T >= t70 + 0.6 && T < t70 + 1.3) k.burst(GX * 3, (GY + 32) * 3, t70 + 0.6, {n: 16, r: 200, colors: ['teal', 'paper']});
      // THE GAP, at the top of the dial, under the 50
      if (T >= tGap) { const f = d.fr(tGap + 0.35); if (f >= 0) { plate(d, GX - 34, 154, 68, 26, RED); k.slam('THE GAP', GX * 3, 157 * 3, tGap + 0.35, {size: 39, color: RED, align: 'center', from: 0.5}); } }
      // under the hub: the source while the numbers are on, then the verdict stamped on a red sticker
      if (T < meas) {
        k.text('ServiceTitan,', 540, 800, {size: 39, color: SAND, align: 'center'});
        k.text(`May to Jul ${n.stYear.shown}`, 540, 846, {size: 39, color: SAND, align: 'center'});
      } else {
        k.stampIn(meas, () => {
          d.win(116, 263, 128, 40, {base: RED, hi: '#F09A9A', lo: WINE, rule: CREAM});
          k.text("Can't close a gap", 540, 802, {size: 39, color: CREAM, align: 'center'});
          k.text('you never measured.', 540, 844, {size: 39, color: CREAM, align: 'center'});
        }, {at: [540, 906]});
      }
      return host(k, k.live('stakes.measure') ? 'point' : (k.live('stakes.gap') ? 'point' : null));
    },

    // ---- formula: the Friday board. The math is written in marker as it is said; SCREENSHOT flashes like a camera
    formula: (k, T) => {
      const t0 = k.S('formula'), shot = k.S('formula.shot');
      const tC = wordT(k, 'formula.eq', /^Close$/i), tJ = wordT(k, 'formula.eq', /^jobs$/i, 1.5), tD = wordT(k, 'formula.div', /^divided$/i), tE = wordT(k, 'formula.div', /^estimates$/i, 1), tM = k.S('formula.month');
      const sold = {}; [1, 5, 9].forEach((i, j) => { sold[i] = tJ + 0.2 + j * 0.12; });
      const d = board(k, {sold, inHand: T < tM + 1 ? 0 : null});
      write(k, 'The math', 72, 282, t0 + 0.15, {color: RED});
      // the camera: the board flashes white for 2 frames, a tag lands
      if (T >= shot) {
        const f = d.fr(wordT(k, 'formula.shot', /^Screenshot/i));
        if (f >= 0 && f < 2) { d.P(BX, BY, BW, BH, '#FFFFFF'); }
        k.ctx.save(); k.ctx.translate(0, d.ease(shot, 6, -14) * 3); k.chip('Screenshot this', 402, 282, {size: 30, fill: 'accent', color: INK}); k.ctx.restore();
      }
      // the fraction: slots show as the board opens (faint guides), each line is written when it is said
      // the slots show as the board opens (faint guides where each line will go), each written when it is said
      if (T < tC) k.text('Close rate =', 72, 392, {size: 66, color: '#E6D3BC', lint: false});
      if (T < tJ) d.dith(84, 172, 86, 2, '#C9CCD3');
      if (T < tE) d.dith(64, 208, 126, 2, '#C9CCD3');
      write(k, 'Close rate =', 72, 392, tC, {color: NAVY});
      write(k, 'jobs sold', 381, 494, tJ, {color: PINE, align: 'center'});
      if (T >= tD) { const w = Math.round(176 * clamp((d.fr(tD) + 1) / 8)); d.P(127 - Math.round(w / 2), 191, w, 3, NAVY); }
      else d.dith(39, 191, 176, 1, '#C9CCD3');
      write(k, 'estimates given', 381, 594, tE, {color: WINE, align: 'center'});
      if (T >= tE + 0.6) k.burst(381, 620, tE + 0.6, {n: 16, r: 220});
      // same month for both: a red box drawn round both lines, a calendar page pinned beside the note
      if (T >= tM) {
        const f = d.fr(tM), per = Math.min(1, (f + 1) / 10), x0 = 30, y0 = 158, w = 194, h = 76, len = 2 * (w + h), drawn = Math.round(len * per);
        const seg = [[x0, y0, w, 0], [x0 + w, y0, 0, h], [x0 + w, y0 + h, -w, 0], [x0, y0 + h, 0, -h]];
        let left = drawn; seg.forEach(([sx, sy, dx, dy]) => { const l = Math.abs(dx + dy), u = Math.min(l, left); left -= u; if (u > 0) d.P(dx < 0 ? sx - u : sx, dy < 0 ? sy - u : sy, dx ? u : 2, dy ? u : 2, RED); });
        write(k, 'Same month', 72, 752, tM + 0.3, {color: RED});
        write(k, 'for both.', 72, 826, tM + 0.7, {color: RED});
        // the calendar page: a red header, a grid, the whole month circled once it lands
        k.stampIn(tM + 0.5, () => {
          d.P(151, 248, 58, 50, INK); d.P(150, 247, 56, 48, CREAM); d.P(150, 247, 56, 10, RED);
          d.P(176, 244, 4, 5, INK); DOTS(d, 152, 260, 52, 32);
        }, {at: [534, 885]});
        if (T >= tM + 1.0) { const q = clamp((d.fr(tM + 1.0) + 1) / 8); d.ring(178, 276, Math.max(2, Math.round(30 * q)), RED); }
      }
      return host(k, k.live('formula.shot') ? 'point' : (k.live('formula.month') ? 'point' : null));
    },

    // ---- example: the inventory. Estimates and jobs sold are items; the close rate is crafted from them as it is said,
    // then it lands inside the median band, and an empty slot asks for yours
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
      k.sets.inventory({title: 'EXAMPLE: LAST MONTH', items, select: sel, hint: 'LAST MONTH'});
      const d = px(k);
      // the crafted item sparkles into its slot; the empty YOURS slot shows a ? instead of an icon
      if (T >= t35) { const f = d.fr(t35); if (f < 10) { d.twinkle(108 + 4, 108 + 4, f); d.twinkle(108 + 30, 108 + 28, f + 2); } k.burst(375, 375, t35, {n: 18, r: 180}); }
      if (T >= own) { d.P(149, 109, 32, 32, '#1B1420'); k.text('?', 495, 363, {size: 66, color: GOLD, align: 'center'}); }
      // the recipe under the belt: 14 / 40 writes in as it is said, = 35% slams on "thirty-five"
      const lhs = `${n.exSold.shown} / ${n.exEst.shown}`, eqx = 84 + k.measure(lhs + ' ', {size: 132});
      if (T < tDiv) k.text('__ / __', 84, 612, {size: 132, color: '#3B82C4', lint: false});
      else k.slam(lhs, 84, 612, tDiv, {size: 132, color: CREAM, from: 0.4, drop: INK});
      if (T < t35) k.text('= __', eqx, 612, {size: 132, color: '#3B82C4', lint: false});
      else k.slam(`= ${n.exRate.shown}`, eqx, 612, t35, {size: 132, color: 'accent', from: 0.6, drop: INK});
      if (T >= own) k.slam('Now yours: __ / __', 84, 756, own, {size: 39, color: GOLD, from: 0.4});
      // the range strip under the window: where the example sits against the medians
      if (T >= rng) {
        const x0 = 24, w = 300, ax = (v) => x0 + Math.round((w * v) / 100), up = d.ease(rng, 8, 30);
        d.clip(0, 272, 360, 60, () => {
          const y = 280 + up;
          d.P(x0 - 2, y - 2, w + 4, 14, INK); d.P(x0, y, w, 10, '#3D2E45');
          for (let i = 1; i < 4; i++) d.P(x0 + (w * i) / 4, y + 2, 1, 6, '#6B7080');
          d.P(ax(n.medLow.value), y - 2, ax(n.medHigh.value) - ax(n.medLow.value), 14, GOLD);
          const tm = rng + 0.35, f = d.fr(tm);
          if (f >= 0) { const mx = ax(n.exRate.value), dy = [-12, -7, -3, 1, 0][Math.min(4, f)]; d.P(mx - 1, y - 8 + dy, 3, 18, INK); d.P(mx, y - 7 + dy, 1, 16, CREAM); d.P(mx - 3, y - 11 + dy, 7, 4, RED); }
        });
        if (up === 0) {
          k.text(`Median ${n.medLow.shown} to ${n.medHigh.shown}`, 72, 888, {size: 39, color: GOLD});
          if (T >= rng + 0.5) k.text(`${n.exRate.shown} sits inside`, 72 + k.measure(`Median ${n.medLow.shown} to ${n.medHigh.shown}   `, {size: 39}), 888, {size: 39, color: CREAM});
        }
      }
      return host(k, k.live('example.own') ? 'point' : (k.live('example.range') ? 'point' : null));
    },

    // ---- turn: the map again, now of shops. Only some are ServiceTitan customers; then YOUR pin drops, last month to now
    turn: (k, T) => {
      const n = k.data.numbers, t0 = k.S('turn'), cnt0 = k.S('turn.count'), cust = k.S('turn.cust'), ownT = k.S('turn.own'), yours = k.S('turn.yours');
      const tShops = wordT(k, 'turn.cust', /^customers/i, 0.6), tYou = wordT(k, 'turn.yours', /^OWN/i, 0.5), tLast = wordT(k, 'turn.yours', /^last/i, 1.6);
      const stPins = [[0.47, 0.28], [0.56, 0.42], [0.42, 0.47], [0.62, 0.24]];
      const pins = T >= tShops ? stPins.map(([x, y], i) => ({x, y, at: tShops + i * 0.12, c: TEAL})) : [];
      if (T >= ownT) pins.push({x: 0.3, y: 0.62, at: tYou, c: GOLD});
      k.sets.dispatch({pins: T >= ownT ? [] : pins});
      const d = px(k);
      // the shops: every one on the map, before the pins say which are ServiceTitan's
      const SH = [[40, 100], [90, 96], [150, 104], [232, 92], [60, 150], [130, 140], [200, 150], [252, 132], [30, 210], [110, 200], [170, 190], [240, 196], [70, 250], [150, 246], [210, 240], [262, 236]];
      if (T < ownT) SH.forEach(([x, y], i) => { const on = T >= tShops && [2, 5, 6, 3].includes(i); shop(d, x, y + (d.fr(t0 + i * 0.06) < 4 && d.fr(t0 + i * 0.06) >= 0 ? -2 : 0), on ? TEAL : '#9AA0AD'); });
      // the coverage line round the customers, dashes marching
      if (T >= tShops && T < ownT) { const x0 = 124, y0 = 88, w = 128, h = 76, ph = Math.floor(d.F / 4) % 6; for (let i = -ph; i < w; i += 6) { d.P(x0 + Math.max(0, i), y0, Math.min(3, w - Math.max(0, i)), 1, TEAL); d.P(x0 + Math.max(0, i), y0 + h, Math.min(3, w - Math.max(0, i)), 1, TEAL); } for (let j = -ph; j < h; j += 6) { d.P(x0, y0 + Math.max(0, j), 1, Math.min(3, h - Math.max(0, j)), TEAL); d.P(x0 + w, y0 + Math.max(0, j), 1, Math.min(3, h - Math.max(0, j)), TEAL); } }
      // the notes on the map
      if (T >= cnt0 && T < ownT) { const sl = d.ease(cnt0, 8, -60); plate(d, 22 + sl, 222, 210, 30, RED); k.text('How it counts a close:', (28 + sl) * 3, 228 * 3, {size: 39, color: CREAM}); k.text('not on the page.', (28 + sl) * 3, 241 * 3, {size: 39, color: RED}); }
      if (T >= cust && T < ownT) { const sl = d.ease(cust, 8, 60); plate(d, 130 + sl, 170, 200, 32, TEAL); k.text('ServiceTitan customers.', (136 + sl) * 3, 176 * 3, {size: 39, color: TEAL}); k.text('Not every shop.', (136 + sl) * 3, 189 * 3, {size: 39, color: CREAM}); }
      // the turn: the map dims round YOUR pin
      if (T >= ownT) {
        // the map steps down to half light (one dither pass), the shops stay as shapes under it
        SH.forEach(([x, y]) => shop(d, x, y, '#9AA0AD'));
        d.clip(MX, MY, MW, MH, () => d.dith(MX, MY, MW, MH, '#1B1420', 0));
        // last month's pin (grey) and yours (gold) drop; a gold route runs from one to the other on "last"
        const pin = (x, y, at, c, dk) => { const f = d.fr(at); if (f < 0) return; const dy = [-20, -14, -8, -3, 0, -3, -1, 0][Math.min(7, f)]; d.P(x - 3, y + 1, 7, 2, INK); if (f >= 6 && f < 24) d.ring(x, y, 4 + Math.floor((f - 6) / 2), c); d.P(x - 1, y - 8 + dy, 2, 9, '#4A4E5A'); d.disc(x, y - 12 + dy, 7, INK); d.disc(x, y - 12 + dy, 6, c); d.disc(x + 1, y - 11 + dy, 4, dk); d.disc(x - 1, y - 13 + dy, 4, c); d.P(x - 3, y - 15 + dy, 2, 2, CREAM); };
        const LX = 70, YX = 200, PY = 214;
        if (T >= tLast) { const q = clamp((d.fr(tLast) + 1) / 14), x1 = LX + Math.round((YX - LX) * q); for (let x = LX; x < x1; x++) if (((x - LX + Math.floor(d.F / 3)) % 8) < 5) { d.P(x, PY + 3, 1, 3, WINE); d.P(x, PY + 2, 1, 3, GOLD); } }
        pin(YX, PY, ownT + 0.1, GOLD, '#B07A47'); plate(d, 156, 222, 88, 22, GOLD); d.tx('THIS MONTH', 200, 227, {color: GOLD, align: 'center'});
        if (T >= tYou) { pin(LX, PY, tYou, '#9AA0AD', '#4A4E5A'); plate(d, 30, 222, 80, 22, '#6B7080'); d.tx('LAST MONTH', 70, 227, {color: SAND, align: 'center'}); }
      }
      // under the map: the heading, then the first number to beat
      plate(d, 14, 280, 300, 48);
      if (T < ownT) k.slam('The part people skip', 72, 852, t0 + 0.1, {size: 66, color: 'accent', from: 0.6, drop: INK});
      else {
        k.slam('First number to beat:', 72, 846, ownT, {size: 39, color: CREAM, from: 0.4});
        if (T >= yours) { k.slam('Your own, last month.', 72, 898, yours, {size: 66, color: 'accent', stamp: true, drop: INK}); k.burst(330, 930, yours + 0.12, {n: 20, r: 240}); }
      }
      if (T >= t0 + 0.1 && T < cnt0) k.text(`ServiceTitan's medians, May to Jul ${n.stYear.shown}`, 72, 930, {size: 39, color: SAND});
      return host(k, k.live('turn.yours') ? 'point' : (k.live('turn.count') ? 'shrug' : null));
    },

    // ---- weekly: the Friday board. Two rows written up and tallied; slips flip SOLD; the dollars go on the slips; the
    // big quotes stay unsold, and one comes off the cork
    weekly: (k, T) => {
      const t0 = k.S('weekly'), two = k.S('weekly.two'), dol = k.S('weekly.dollars'), low = k.S('weekly.lower'), away = k.S('weekly.away');
      const tFri = wordT(k, 'weekly', /^Friday/i, 0.8), tEst = wordT(k, 'weekly.two', /^estimates/i, 1.8), tJobs = wordT(k, 'weekly.two', /^jobs/i, 2.9);
      const tDol = wordT(k, 'weekly.dollars', /^dollars/i, 0.9), tQuoted = wordT(k, 'weekly.dollars', /^quoted/i, 2.6), tBig = wordT(k, 'weekly.away', /^bigger/i, 0.4), tAway = wordT(k, 'weekly.away', /^away/i, 1.8);
      const sold = {}; [0, 4, 2, 6, 10, 8].forEach((i, j) => { sold[i] = tJobs + 0.15 + j * 0.15; });
      const d = board(k, {sold, dollars: tQuoted - 0.2, fall: {i: 5, wobble: tBig, at: tAway}, inHand: T >= tFri && T < tQuoted + 0.6 ? 1 : null});
      write(k, 'Every Friday', 72, 282, t0 + 0.2, {color: RED});
      if (T >= tFri) k.sweep(72, 352, k.measure('Every Friday', {size: 66}), 6, tFri, {color: RED});
      // the rows: shown as the board opens (faint), written in marker when they are said
      const row = (s, y, at, c) => { if (T < at) { k.text(s, 72, y, {size: 66, color: '#E6D3BC', lint: false}); return; } write(k, s, 72, y, at, {color: c}); };
      row('Estimates given', 400, tEst, NAVY);
      row('Jobs sold', 500, tJobs, PINE);
      [400, 500].forEach((y) => d.P(24, y / 3 + 26, 200, 1, '#C9CCD3'));
      // a box beside each row, ticked once the row is written (the check draws on, a pixel a frame)
      const tick = (x, y, at, c) => { d.P(x, y, 18, 18, '#C9CCD3'); d.P(x + 2, y + 2, 14, 14, CREAM); const f = d.fr(at + 0.4); if (f < 0) return; const pts = [[x + 3, y + 9], [x + 7, y + 14], [x + 17, y + 1]]; const n1 = Math.min(5, f + 1), n2 = Math.max(0, Math.min(11, f - 4)); d.line(pts[0][0], pts[0][1], pts[0][0] + Math.round((pts[1][0] - pts[0][0]) * n1 / 5), pts[0][1] + Math.round((pts[1][1] - pts[0][1]) * n1 / 5), c, 2); if (n2 > 0) d.line(pts[1][0], pts[1][1], pts[1][0] + Math.round((pts[2][0] - pts[1][0]) * n2 / 11), pts[1][1] + Math.round((pts[2][1] - pts[1][1]) * n2 / 11), c, 2); };
      tick(204, 132, tEst, NAVY); tick(204, 166, tJobs, PINE);
      if (T >= dol) row('$ sold / $ quoted', 600, tDol, WINE);
      // the sticky note: what a lower dollar rate means
      if (T >= low) {
        k.stampIn(low, () => {
          d.P(22, 233, 206, 70, '#B07A47'); d.P(20, 231, 206, 70, GOLD); d.P(20, 231, 206, 6, ORANGE);
          k.text('$ rate lower than the count?', 72, 714, {size: 39, color: INK});
          if (T >= away) { k.text('Big quotes are', 72, 762, {size: 66, color: RED}); k.text('getting away.', 72, 832, {size: 66, color: RED}); }
        }, {at: [330, 903], drop: 0.08});
      }
      return host(k, k.live('weekly.away') ? 'clip' : (k.live('weekly.two') ? 'point' : null));
    },

    // ---- close: the board wiped clean, one column at x 120: the formula, the send line, Friday
    close: (k, T) => {
      const t0 = k.S('close'), send = k.S('close.send'), fri = k.S('close.friday');
      const tJ = wordT(k, 'close', /^Jobs/i), tD = wordT(k, 'close', /^divided/i, 0.6), tE = wordT(k, 'close', /^estimates/i, 1.5), tF = wordT(k, 'close.friday', /^close$/i, 1.8);
      const d = board(k, {cork: false, inHand: T < fri + 2 ? 0 : null});
      k.slam('Close rate =', 120, 276, t0 - 0.05, {size: 132, color: NAVY, from: 0.4, glint: false});
      write(k, 'jobs sold', 120, 426, tJ, {color: PINE});
      if (T >= tD) { const w = Math.round(140 * clamp((d.fr(tD) + 1) / 8)); d.P(40, 166, w, 3, NAVY); }
      write(k, 'estimates given', 120, 514, tE, {color: WINE});
      if (T >= send) {
        k.chip('ProofNotFluff', 120, 616, {size: 30});
        k.slam('Send this to whoever', 120, 690, send + 0.1, {size: 66, color: NAVY, from: 0.4, glint: false});
        k.slam('writes your estimates.', 120, 762, send + 0.3, {size: 66, color: NAVY, from: 0.4, glint: false});
      }
      if (T >= fri) {
        write(k, 'Friday: your close rate.', 120, 846, fri + 0.1, {color: RED});
        if (T >= tF) { k.sweep(120, 918, k.measure('Friday: your close rate.', {size: 66}), 6, tF, {color: 'accent'}); k.burst(120 + k.measure('Friday: your close rate.', {size: 66}), 880, tF + 0.2, {n: 16}); }
      }
      return host(k, k.live('close.friday') ? 'wave' : (k.live('close.send') ? 'point' : null));
    },
  },
};
