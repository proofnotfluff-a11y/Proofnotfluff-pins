/* 2026-12-05-wrong-house (v4 told), the v4 template's helpers (wordT, px, plate, stampPlate, steps, push) kept whole; */
/* places drawn by hand for this story; cards only for numbers and names, no label (formats.md "Told"; Todd, Nov 19). */
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', DTEAL = '#2F6F67', NIGHT = '#1B1420', PLUM = '#2B2033', WINE = '#7A3442', SKY = '#87CEEB';
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const WS = () => (window.WORDS && window.WORDS.words) || [];
/* the start of the first word matching re at or after a cue (id) or a time; dflt seconds after it when no word matches */
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
/* the low-res painter (360 x 640, one unit = 3 frame pixels) */
const px = (k) => {
  const ctx = k.ctx;
  return (x, y, w, h, c) => { x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h); if (w > 0 && h > 0 && c) { ctx.fillStyle = c; ctx.fillRect(x * 3, y * 3, w * 3, h * 3); } };
};
/* a centered plate of rows [[text, size, color], ...] with its top at y; returns its bottom. Sizes are whole steps of */
/* the display face (66, 132, 198) so the pixels stay square. */
const plate = (k, rows, y, o = {}) => {
  const cx = o.cx || 540, pad = o.pad || 36, gap = o.gap || 18;
  const hs = rows.map(([, z]) => Math.round(z * 1.0)), w = Math.ceil((Math.max(...rows.map(([s, z]) => k.measure(s, {size: z}))) + 2 * pad) / 6) * 6;
  const h = hs.reduce((a, b) => a + b, 0) + gap * (rows.length - 1) + 2 * pad - 6, x = Math.round((cx - w / 2) / 3) * 3;
  k.shape(k.rectPts(x + 9, y + 9, w, h, 0), {fill: INK, line: false});
  k.shape(k.rectPts(x, y, w, h, 0), {fill: o.bg || NIGHT, line: false});
  k.shape(k.rectPts(x, y, w, 9, 0), {fill: o.rule || ORANGE, line: false});
  let yy = y + pad;
  rows.forEach(([s, z, c], i) => { k.text(s, cx, yy, {size: z, color: c || CREAM, align: 'center'}); yy += hs[i] + gap; });
  return y + h;
};
/* the same plate landing as a stamp at t0 (put a [sfx: stamp] cue there for the hit-stop) */
const stampPlate = (k, rows, y, t0, o = {}) => {
  const hgt = rows.reduce((a, [, z]) => a + z, 0) + 18 * (rows.length - 1) + 66;
  return k.stampIn(t0, () => plate(k, rows, y, o), {at: [o.cx || 540, y + hgt], freeze: o.freeze, drop: o.drop});
};

const zoom = (k, z, fn) => { const c = k.ctx; c.save(); if (z !== 1) { c.translate(540 * (1 - z), 836 * (1 - z)); c.scale(z, z); } fn(px(k)); c.restore(); };
const dimmer = (k, a) => { if (a) px(k)(0, 0, 360, 640, `rgba(18,13,20,${a})`); };
const wall = (k, c, c2) => { const P = px(k); P(0, 0, 360, 640, c); for (let y = 20; y < 640; y += 22) P(0, y, 360, 1, c2); };
/* a second person as a plain dark shape (the business partner: no source describes them, so no face and no clothes) */
const shape2 = (k, x, y, s = 1) => { const c = k.ctx, q = (v) => Math.round(v / 3) * 3; c.fillStyle = '#3A2F45'; c.fillRect(q(x - 33 * s), q(y - 345 * s), q(66 * s), q(72 * s)); c.fillRect(q(x - 12 * s), q(y - 273 * s), q(24 * s), q(15 * s)); c.fillRect(q(x - 54 * s), q(y - 258 * s), q(108 * s), q(18 * s)); c.fillRect(q(x - 66 * s), q(y - 240 * s), q(132 * s), q(130 * s)); c.fillRect(q(x - 45 * s), q(y - 110 * s), q(36 * s), q(110 * s)); c.fillRect(q(x + 9 * s), q(y - 110 * s), q(36 * s), q(110 * s)); };
/* the cast. Close shots from the waist up, feet far below the frame (feet 1700 or so), faces between y 700 and 1100. */
const pro = (k, x, sc, pose, o = {}) => k.snow(x, o.feet || 1150, Object.assign({scale: sc, pose, face: 1, talk: false}, o));
const owner = (k, x, sc, pose, mood, o = {}) => k.client(x, o.feet || 1150, Object.assign({role: 'homeowner', scale: sc, pose, mood, face: -1}, o));
/* a row of plates in time: [[t, rows, stamp?], ...]; the last one whose time has come shows; a later one lands as a stamp */
const steps = (k, T, list, o = {}, y = 264) => {
  let i = 0; list.forEach(([t], j) => { if (j && T >= t - 0.06) i = j; });
  const [t, rows, st] = list[i];
  if (i === 0 && !st) return plate(k, rows, y, o);
  return stampPlate(k, rows, y, t, Object.assign({drop: 0.06, freeze: 4}, o));
};
const push = (k, T, t0, fn, amt = 0.07, cy = 1100) => { const c = k.ctx, z = 1 + amt * clamp((T - t0) / 4); c.save(); c.translate(540, cy); c.scale(z, z); c.translate(-540, -cy); fn(); c.restore(); };
const W = (k, id, re, d) => wordT(k, id, re, d) - 0.1;

/* ---- the places (low-res painter units, 360 x 640) ---- */
/* focus: the unit point (ux, uy) lands at frame (540, fy), scaled z (whole frame pixels at z 1; a close shot is z 2 to 6) */
const focus = (k, ux, uy, z, fn, fy = 880) => { const c = k.ctx; c.save(); c.translate(540, fy); c.scale(z, z); c.translate(-ux * 3, -uy * 3); fn(px(k)); c.restore(); };
/* a wide ground that reaches past the frame on every side, for focused shots */
const groundW = (P, F) => { P(-400, -400, 1200, 700, SKY); P(-400, 300, 1200, 16, '#BDE6F5'); const cx = (Math.floor(F / 6) % 440) - 70; P(cx, 92, 46, 9, CREAM); P(cx + 10, 85, 24, 7, CREAM); P(-400, 316, 1200, 700, '#3E7A62'); P(-400, 316, 1200, 3, '#2F5A4A'); for (let i = 0; i < 90; i++) P(-200 + (i * 53) % 760, 324 + (i * 37) % 300, 3, 1, '#2F5A4A'); };
/* sky and lawn; the street runs across the bottom third */
const ground = (P, F) => {
  P(0, 0, 360, 300, SKY); P(0, 300, 360, 16, '#BDE6F5');
  const cx = (Math.floor(F / 6) % 440) - 70; P(cx, 92, 46, 9, CREAM); P(cx + 10, 85, 24, 7, CREAM); P((cx + 250) % 440 - 70, 140, 36, 8, CREAM);
  P(0, 316, 360, 324, '#3E7A62'); P(0, 316, 360, 3, '#2F5A4A');
  for (let i = 0; i < 60; i++) P((i * 53) % 360, 324 + (i * 37) % 300, 3, 1, '#2F5A4A');
};
/* a tree: trunk at x, crown top at y, size s */
const tree = (P, x, y, s = 1) => { P(x - 4 * s, y + 46 * s, 8 * s, 40 * s, '#5A3A22'); P(x - 28 * s, y + 10 * s, 56 * s, 42 * s, '#24453A'); P(x - 20 * s, y, 40 * s, 56 * s, '#2F5A4A'); P(x - 12 * s, y + 6 * s, 14 * s, 12 * s, '#3E7A62'); };
/* a mailbox on a post; faded: the number barely there */
const mailbox = (P, x, y, s = 1, faded = false) => {
  P(x - 2 * s, y, 4 * s, 46 * s, INK); P(x - 1 * s, y, 2 * s, 46 * s, '#8C5A33');
  P(x - 16 * s, y - 16 * s, 32 * s, 18 * s, INK); P(x - 14 * s, y - 14 * s, 28 * s, 14 * s, faded ? '#8E949E' : '#C9CCD3');
  P(x + 10 * s, y - 22 * s, 3 * s, 10 * s, faded ? '#7A3442' : RED);
  if (faded) { P(x - 14 * s, y - 14 * s, 28 * s, 14 * s, '#7E848C'); P(x - 10 * s, y - 6 * s, 8 * s, 4 * s, '#8C5A33'); P(x + 2 * s, y - 12 * s, 6 * s, 3 * s, '#6E5040'); for (let i = 0; i < 4; i++) P(x - 10 * s + i * 6 * s, y - 9 * s, 3 * s, 2 * s, '#868C94'); }
  else { for (let i = 0; i < 4; i++) P(x - 10 * s + i * 6 * s, y - 10 * s, 4 * s, 6 * s, INK); }
};
/* their house: a small three-bedroom house; st 'whole', 'hit' (a bite out of it), 'rubble' */
const home = (P, x, y, s = 1, st = 'whole') => {
  const w = 150 * s, h = 70 * s;
  if (st === 'rubble') {
    P(x - 6 * s, y + h - 30 * s, w + 12 * s, 30 * s, INK);
    [[0, 6, 40, 24, SAND], [34, 0, 30, 30, '#8C5A33'], [60, 10, 44, 20, SAND], [96, 4, 26, 26, WINE], [118, 12, 34, 18, '#D2BCA2']].forEach(([a, b, c, d, col]) => P(x + a * s, y + h - 30 * s + b * s, c * s, d * s, col));
    return;
  }
  P(x, y, w, h, INK); P(x + 3 * s, y + 3 * s, w - 6 * s, h - 3 * s, SAND); for (let yy = y + 10 * s; yy < y + h; yy += 8 * s) P(x + 3 * s, yy, w - 6 * s, 1, '#D2BCA2');
  for (let i = 0; i < 18; i++) P(x - 8 * s + i * 3 * s, y - i * 2 * s, w + 16 * s - i * 6 * s, 2 * s, i % 5 === 4 ? '#5A2432' : WINE);
  [18, 104].forEach((a) => { P(x + a * s, y + 18 * s, 28 * s, 24 * s, INK); P(x + (a + 2) * s, y + 20 * s, 24 * s, 20 * s, '#5B8FB9'); P(x + (a + 13) * s, y + 20 * s, 2 * s, 20 * s, INK); });
  P(x + 62 * s, y + 26 * s, 26 * s, 44 * s, INK); P(x + 64 * s, y + 28 * s, 22 * s, 42 * s, DTEAL); P(x + 81 * s, y + 48 * s, 2 * s, 2 * s, GOLD);
  if (st === 'hit') { P(x + 96 * s, y - 24 * s, 60 * s, 94 * s, SKY); P(x + 96 * s, y + 30 * s, 60 * s, 40 * s, '#3F3A38'); for (let i = 0; i < 5; i++) P(x + (92 + i * 3) * s, y + (i * 14) * s, 6 * s, 10 * s, SAND); }
};
/* brush: tall weeds around a point */
const brush = (P, x, y) => { for (let i = 0; i < 16; i++) { const h = 10 + (i * 7) % 14; P(x - 40 + i * 5, y - h, 3, h, i % 2 ? '#2F5A4A' : '#24453A'); } };
/* the condemned house, back in the trees: boarded, sagging */
const wreck = (P, x, y, s = 1) => {
  const w = 120 * s, h = 60 * s;
  P(x, y, w, h, INK); P(x + 3 * s, y + 3 * s, w - 6 * s, h - 3 * s, '#8E8676'); for (let yy = y + 9 * s; yy < y + h; yy += 7 * s) P(x + 3 * s, yy, w - 6 * s, 1, '#6E6858');
  for (let i = 0; i < 14; i++) P(x - 6 * s + i * 3 * s, y - i * 2 * s + (i > 8 ? 2 * s : 0), w + 12 * s - i * 6 * s, 2 * s, i % 4 === 3 ? '#3A3430' : '#5A524A');
  [14, 80].forEach((a) => { P(x + a * s, y + 16 * s, 24 * s, 22 * s, '#3A3430'); P(x + (a - 2) * s, y + 22 * s, 28 * s, 4 * s, '#B07A47'); P(x + (a - 2) * s, y + 30 * s, 28 * s, 4 * s, '#B07A47'); });
  P(x + 50 * s, y + 24 * s, 22 * s, 36 * s, '#3A3430'); P(x + 30 * s, y - 20 * s, 3 * s, 8 * s, INK);
};
/* the excavator: body at x, ground at y; arm angle a (0 up, 1 down on the target), facing f */
const digger = (P, x, y, s = 1, a = 0, f = -1) => {
  P(x - 46 * s, y - 16 * s, 92 * s, 16 * s, INK); P(x - 44 * s, y - 14 * s, 88 * s, 12 * s, '#4A4E5A'); for (let i = 0; i < 6; i++) P(x - 40 * s + i * 15 * s, y - 12 * s, 8 * s, 8 * s, '#2B2033');
  P(x - 34 * s, y - 48 * s, 68 * s, 32 * s, INK); P(x - 32 * s, y - 46 * s, 64 * s, 28 * s, GOLD); P(x - 30 * s, y - 64 * s, 30 * s, 18 * s, INK); P(x - 28 * s, y - 62 * s, 26 * s, 14 * s, '#BDE6F5');
  const bx = x + f * 30 * s, by = y - 44 * s, ex = bx + f * (60 - 10 * a) * s, ey = by - (40 - 40 * a) * s, tx = ex + f * 40 * s, ty = ey + (30 + 10 * a) * s;
  const seg = (x0, y0, x1, y1, wd) => { const n = 12; for (let i = 0; i <= n; i++) { const u = i / n; P(x0 + (x1 - x0) * u - wd / 2, y0 + (y1 - y0) * u - wd / 2, wd, wd, i === 0 || i === n ? INK : ORANGE); } };
  seg(bx, by, ex, ey, 10 * s); seg(ex, ey, tx, ty, 8 * s);
  P(tx - 12 * s, ty - 4 * s, 24 * s, 14 * s, INK); P(tx - 10 * s, ty - 2 * s, 20 * s, 10 * s, '#6B7080'); for (let i = 0; i < 4; i++) P(tx - 9 * s + i * 6 * s, ty + 8 * s, 3 * s, 5 * s, '#9AA0AD');
};
/* the slab: a bare concrete pad lying flat on the lawn, nothing standing (viewer r0, Nov 19: the old block read as a grey house) */
const slab = (P, x, y, s = 1) => {   /* y is where the house's walls stood; the pad lies from y + 12 to y + 31, flush with the grass */
  P(x - 10 * s, y + 6 * s, 190 * s, 30 * s, '#3E7A62');
  for (let r = 0; r < 18; r++) { const inset = Math.round((18 - r) * 0.8) * s; P(x + inset, y + (12 + r) * s, 170 * s - 2 * inset, 1 * s, r % 6 === 3 ? '#B4B2AA' : '#C9C7BF'); }
  P(x, y + 30 * s, 170 * s, 2 * s, '#8E8C85');
  P(x + 34 * s, y + 20 * s, 34 * s, 1 * s, '#A09E96'); P(x + 98 * s, y + 25 * s, 28 * s, 1 * s, '#A09E96');
  [[52, 17], [120, 22]].forEach(([u, v]) => { P(x + u * s, y + v * s, 3 * s, 3 * s, INK); P(x + (u + 1) * s, y + (v + 1) * s, 1 * s, 1 * s, '#9AA0AD'); });
  for (let i = 0; i < 12; i++) P(x - 4 * s + i * 15 * s, y + (29 - i % 3) * s, 2 * s, (3 + i % 3) * s, '#2F5A4A');
};
/* the street scene: their house (left), the condemned house back in the trees (right), two mailboxes */
const street = (k, st = 'whole', dim = 0, f = [180, 300, 1.5], armA = null, mark = 0) => {
  focus(k, f[0], f[1], f[2], (P) => {
    const F = Math.floor(k.T * 30 + 0.005);
    groundW(P, F);
    tree(P, 236, 168, 1.1); tree(P, 330, 176, 1.2); tree(P, 268, 150, 0.9);
    wreck(P, 222, 236, 0.9);
    tree(P, 246, 210, 0.8); tree(P, 300, 214, 0.75);
    if (st === 'slab') slab(P, 14, 290, 1); else home(P, 20, 240, 1, st);
    if (mark && st !== 'rubble') { const c = clamp(mark); for (let i = 0; i < Math.round(16 * c); i++) { P(56 + i * 2, 252 + i * 2.6, 5, 5, ORANGE); P(88 - i * 2, 252 + i * 2.6, 5, 5, ORANGE); } }
    mailbox(P, 150, 336, 1, false); mailbox(P, 214, 330, 0.8, true);
    P(-400, 380, 1200, 40, '#5E6470'); P(-400, 380, 1200, 3, '#4A4E5A'); for (let x = -390; x < 760; x += 50) P(x, 399, 24, 3, GOLD);
    if (armA !== null) digger(P, 170, 372, 1, armA, -1);
  });
  dimmer(k, dim);
};
/* a sheet on a desk (the bill) */
const sheet = (k, seal) => {
  const P = px(k);
  P(0, 0, 360, 640, '#5A3A22'); for (let y = 0; y < 640; y += 28) P(0, y, 360, 2, '#4A2E1B');
  P(66, 250, 228, 300, INK); P(69, 253, 222, 294, CREAM);
  for (let y = 274; y < 500; y += 22) P(88, y, y % 44 === 10 ? 150 : 184, 5, '#C9B79C');
  if (seal) { P(214, 470, 56, 56, INK); P(217, 473, 50, 50, RED); P(225, 481, 34, 34, '#B8452A'); P(236, 492, 12, 12, RED); }
};
/* city hall: a flat civic front with a flag */
const hall = (k, dim = 0) => {
  const P = px(k);
  P(0, 0, 360, 420, SKY); P(30, 180, 300, 240, INK); P(34, 184, 292, 236, '#C9CCD3'); for (let x = 50; x < 320; x += 30) P(x, 200, 16, 200, '#9AA0AD');
  P(150, 330, 60, 90, '#4A4E5A'); P(176, 100, 3, 84, INK); P(179, 104, 40, 24, RED); P(179, 110, 40, 4, CREAM); P(179, 118, 40, 4, CREAM);
  P(0, 420, 360, 220, '#8C8F99');
  dimmer(k, dim);
};
/* a fence for the neighbor to stand behind */
const fence = (P, y) => { P(0, y, 360, 6, '#E6D3BC'); P(0, y + 30, 360, 6, '#E6D3BC'); for (let x = 6; x < 360; x += 24) { P(x, y - 14, 10, 70, INK); P(x + 1, y - 13, 8, 68, CREAM); } };
/* barrier tape across the frame */
const tape = (k, y) => { const P = px(k); for (let x = -20; x < 380; x += 24) { P(x, y, 12, 10, GOLD); P(x + 12, y, 12, 10, INK); } };
/* the split: city side left (slate blue), company side right (gold) */
const split = (k) => { const P = px(k); P(0, 0, 180, 640, '#253048'); P(180, 0, 180, 640, '#5A4A2A'); P(178, 0, 4, 640, INK); for (let y = 20; y < 640; y += 22) { P(0, y + 11, 178, 1, '#1D2740'); P(182, y, 178, 1, '#4A3C22'); } };
/* the couple: she (homeowner) and he (buyer role: grey jacket) */
const couple = (k, x, sc, pose, mood, o = {}) => {
  k.client(x + 110 * sc, o.feet || 1150, Object.assign({role: 'buyer', scale: sc, pose, mood, face: -1}, o));
  k.client(x - 90 * sc, o.feet || 1150, Object.assign({role: 'homeowner', scale: sc * 0.96, pose: o.pose2 || pose, mood, face: 1}, o));
};
/* the city worker: no source describes them, so a plain dark shape, and the orange can in hand */
const worker = (k, x, y, s = 1, spray = false) => { shape2(k, x, y, s); const c = k.ctx, q = (v) => Math.round(v / 3) * 3; c.fillStyle = INK; c.fillRect(q(x + 50 * s), q(y - 230 * s), q(30 * s), q(54 * s)); c.fillStyle = ORANGE; c.fillRect(q(x + 53 * s), q(y - 227 * s), q(24 * s), q(48 * s)); if (spray) { c.fillStyle = 'rgba(242,165,65,0.6)'; for (let i = 0; i < 8; i++) c.fillRect(q(x + 82 * s + i * 12), q(y - 250 * s - (i % 3) * 12), 9, 9); } };

const L_CITY = {cx: 250, bg: INK, rule: TEAL, pad: 24}, L_CO = {cx: 772, bg: INK, rule: GOLD, pad: 24};   /* side by side inside x 40 to 1040, a gap between (render critic r0, Nov 19: CO ran to x 1076) */
const CITY = [['CITY', 132, CREAM], ['$62,500', 132, GOLD]], CO = [['COMPANY', 132, CREAM], ['+ INSURER', 132, CREAM], ['$40,000', 132, GOLD]];
const LOT = [100, 300, 1.8], LOTC = [110, 310, 2.4];   /* the lot (slab and mailbox), wide and close */
const lot = (k, f, dim = 0) => { focus(k, f[0], f[1], f[2], (P) => { groundW(P, 0); tree(P, 165, 196, 1.0); tree(P, -40, 196, 1.1); slab(P, 14, 290, 1); mailbox(P, 150, 336, 1, false); }); dimmer(k, dim); };
const woods = (P) => { groundW(P, 0); tree(P, 214, 168, 1.1); tree(P, 330, 176, 1.2); tree(P, 268, 150, 0.9); wreck(P, 222, 236, 0.9); tree(P, 246, 210, 0.8); tree(P, 300, 214, 0.75); };

window.SCENE = {
  look: 'arcade',
  v4: true,
  host: false,
  endCard: false,
  images: [],
  trauma: {level: 0.6, other: 0.4, end: 0.5},
  sections: {
    /* ---- hook: frame 0 the lot, a bare slab and a mailbox; 0.5 s the couple (the first acted frame, the small label); ---- */
    /* on "mow" the mailbox alone, close; on "and the house was gone" the lot again, easing in ---- */
    hook: (k, T) => {
      const tC = 0.5, tMow = Math.max(1.6, W(k, 'hook', /^mow/i, 2.2)), tGone = Math.max(tMow + 1.2, W(k, 'hook', /^and$/i, 4.1));
      if (T < tC) {
        lot(k, LOT);
      } else if (T < tMow) {
        k.cut(tC);
        lot(k, LOTC, 0.25);
        couple(k, 540, 2.0, 'argue', 'calm', {feet: 1760});
      } else if (T < tGone) {
        k.cut(tMow);
        focus(k, 140, 318, 4.5, (P) => { groundW(P, 0); slab(P, 14, 290, 1); mailbox(P, 150, 336, 1, false); });
      } else {
        k.cut(tGone);
        push(k, T, tGone, () => lot(k, LOT), 0.08, 1000);
      }
      return {host: false};
    },
    /* ---- slab: closer on the slab and the mailbox, easing in ---- */
    slab: (k, T) => {
      const t0 = k.S('slab');
      k.cut(t0);
      push(k, T, t0, () => lot(k, [80, 318, 3.2]), 0.1, 1000);
      return {host: false};
    },
    /* ---- house: the house as it was; the name of the city ---- */
    house: (k, T) => {
      const t0 = k.S('house'), tF = W(k, 'house', /^fort/i, 3.0);
      k.cut(t0);
      const zz = 2.2 + 0.5 * clamp((T - t0) / 6.5);   /* a slow push in, so the shot never sits still (qa: frozen) */
      focus(k, 115, 300, zz, (P) => { groundW(P, Math.floor(T * 30)); tree(P, 250, 180, 1.1); home(P, 40, 240, 1, 'whole'); mailbox(P, 170, 336, 1, false); });
      if (T >= tF) steps(k, T, [[tF, [['FORT WORTH,', 132, CREAM], ['TEXAS', 132, GOLD]], 1]]);
      return {host: false};
    },
    /* ---- order: the street, wide: theirs left, the condemned one back in the trees ---- */
    order: (k, T) => {
      const t0 = k.S('order');
      k.cut(t0);
      push(k, T, t0, () => street(k, 'whole', 0, [160, 300, 1.45]), 0.05, 900);
      return {host: false};
    },
    /* ---- trees: close on the condemned house; then its faded mailbox ---- */
    trees: (k, T) => {
      const t0 = k.S('trees'), tM = W(k, 'trees', /^mailbox/i, 2.2);
      k.cut(t0);
      if (T < tM) focus(k, 275, 262, 3, woods);
      else { k.cut(tM); push(k, T, tM, () => focus(k, 214, 322, 5, (P) => { groundW(P, 0); P(150, 250, 140, 66, '#2F5A4A'); mailbox(P, 214, 330, 0.8, true); brush(P, 214, 340); }), 0.08, 1000); }
      return {host: false};
    },
    /* ---- mark: the city worker sprays an orange X on their house ---- */
    mark: (k, T) => {
      const t0 = k.S('mark'), tM = W(k, 'mark', /^marked/i, 0.9);
      k.cut(t0);
      focus(k, 95, 278, 3.1, (P) => { groundW(P, 0); home(P, 20, 240, 1, 'whole'); const c = clamp((T - tM) / 1.2); for (let i = 0; i < Math.round(16 * c); i++) { P(56 + i * 2, 252 + i * 2.6, 5, 5, ORANGE); P(88 - i * 2, 252 + i * 2.6, 5, 5, ORANGE); } });
      worker(k, 860, 1700, 2.2, T >= tM && T < tM + 1.3);   /* the head above the captions (render critic r0) */
      return {host: false};
    },
    /* ---- level: the arm comes down, the house breaks, dust ---- */
    level: (k, T) => {
      const t0 = k.S('level'), tL = W(k, 'level', /^leveled/i, 1.6), a = clamp((T - t0) / Math.max(0.4, tL - t0));
      k.cut(t0);
      street(k, T < tL + 0.3 ? (T < tL ? 'whole' : 'hit') : 'rubble', 0, [110, 320, 2.2], a, 1);
      k.burst(330, 860, tL, {colors: [SAND, WINE, '#C9CCD3'], n: 22, r: 280});
      k.burst(250, 940, tL + 0.6, {colors: [SAND, '#8C5A33'], n: 16, r: 220});
      return {host: false};
    },
    /* ---- neighbor: behind a fence, on the phone; the arm working beyond ---- */
    neighbor: (k, T) => {
      const t0 = k.S('neighbor');
      k.cut(t0);
      const u = clamp((T - t0) / 5);   /* the machine creeps toward the house while the neighbor waves and calls (viewer r0, Nov 19: six still seconds) */
      push(k, T, t0, () => focus(k, 170, 330, 2.0, (P) => { groundW(P, Math.floor(T * 30)); home(P, 40, 270, 0.8, 'hit'); digger(P, 222 - 22 * u, 330, 1.1, 0.5 + 0.4 * Math.sin(T * 3), -1); fence(P, 352); }), 0.08, 1000);
      const bob = Math.round(Math.sin(T * 7) * 1.5) * 3, up = Math.floor(T * 4) % 2 === 0, c = k.ctx;
      shape2(k, 300, 1720 + bob, 2.2);
      c.fillStyle = '#3A2F45'; if (up) { c.fillRect(111, 1002 + bob, 45, 192); c.fillRect(99, 954 + bob, 57, 60); } else { c.fillRect(81, 1047 + bob, 45, 150); c.fillRect(57, 1002 + bob, 60, 57); c.fillRect(111, 1137 + bob, 45, 60); }
      c.fillStyle = INK; c.fillRect(375, 990 + bob, 54, 105); c.fillStyle = '#5B8FB9'; c.fillRect(381, 996 + bob, 42, 87);   /* head and phone above the captions (render critic r0) */
      return {host: false};
    },
    /* ---- gets: the condemned house, still standing ---- */
    gets: (k, T) => {
      const t0 = k.S('gets');
      k.cut(t0);
      push(k, T, t0, () => focus(k, 278, 262, 3.4, woods), 0.06, 900);
      return {host: false};
    },
    /* ---- bill: the house held; the bill; over $6,000 ---- */
    bill: (k, T) => {
      const t0 = k.S('bill'), tB = W(k, 'bill', /^bill/i, 3.6), tO = W(k, 'bill', /^over/i, 4.2);
      if (T < tB) { k.cut(t0); focus(k, 282, 262, 4.2, woods); }
      else { k.cut(tB); push(k, T, tB, () => sheet(k, false), 0.06); if (T >= tO) steps(k, T, [[tO, [['OVER', 132, CREAM], ['$6,000', 198, RED]], 1]]); }
      return {host: false};
    },
    /* ---- closer: city hall; closer on the doors ---- */
    closer: (k, T) => {
      const t0 = k.S('closer'), tF = W(k, 'closer', /^found/i, 1.8);
      k.cut(t0);
      if (T < tF) hall(k, 0); else { k.cut(tF); focus(k, 130, 320, 1.6, (P) => { groundW(P, 0); tree(P, 40, 170, 1.0); P(40, 270, 100, 50, INK); P(43, 273, 94, 47, '#B09A7C'); for (let i = 0; i < 10; i++) P(34 + i * 3, 270 - i * 2, 112 - i * 6, 2, '#5A524A'); digger(P, 250, 372, 1, 0.1 + 0.05 * Math.sin(T * 2), -1); }); }
      return {host: false};
    },
    /* ---- other: another lot, the same machine on a small back building ---- */
    other: (k, T) => {
      const t0 = k.S('other'), hit = T > t0 + 0.8;
      k.cut(t0);
      focus(k, 120, 320, 2.2, (P) => {
        groundW(P, 0); tree(P, 40, 170, 1.0);
        if (!hit) { P(40, 270, 100, 50, INK); P(43, 273, 94, 47, '#B09A7C'); for (let i = 0; i < 10; i++) P(34 + i * 3, 270 - i * 2, 112 - i * 6, 2, '#5A524A'); }
        else { P(36, 300, 110, 20, INK); [[0, 4, 30, 16, '#B09A7C'], [26, 0, 30, 20, '#5A524A'], [52, 6, 40, 14, '#B09A7C'], [86, 2, 22, 18, '#8C5A33']].forEach(([a, b, c, d, col]) => P(40 + a, 300 + b, c, d, col)); }
        digger(P, 200, 372, 1, clamp((T - t0) / 0.8), -1);
      });
      k.burst(420, 840, t0 + 0.8, {colors: ['#B09A7C', '#5A524A'], n: 18, r: 240});
      return {host: false};
    },
    /* ---- stop: the machine parked, tape across ---- */
    stop: (k, T) => {
      const t0 = k.S('stop');
      k.cut(t0);
      focus(k, 180, 360, 2.0, (P) => { groundW(P, 0); tree(P, 330, 230, 1.1); digger(P, 190, 380, 1.4, 0.1, -1); });
      tape(k, 300); tape(k, 330);
      return {host: false};
    },
    /* ---- back: the couple at the slab, quiet ---- */
    back: (k, T) => {
      const t0 = k.S('back');
      k.cut(t0);
      lot(k, LOTC, 0.2);
      couple(k, 560, 2.0, 'stand', 'calm', {feet: 1760, pose2: 'refuse'});
      return {host: false};
    },
    /* ---- end (the payoff, 80% in): the lot; $102,500; then the city's share ---- */
    end: (k, T) => {
      const t0 = k.S('end'), tH = W(k, 'end', /^hundred/i, 1.9), tC = W(k, 'end', /^city/i, 4.8);
      k.cut(t0);
      { const c = k.ctx, z = 1 + 0.16 * clamp((T - t0) / 7); c.save(); c.translate(540, 1000); c.scale(z, z); c.translate(-540, -1000); lot(k, LOT, 0.35); c.restore(); }   /* a push in over the whole cue (qa: flat) */
      if (T >= tH) steps(k, T, [[tH, [['$102,500', 198, GOLD]], 1], [tC, [['$102,500', 198, GOLD], ['CITY $62,500', 132, CREAM]], 1]]);
      return {host: false};
    },
    /* ---- ask: the split, a side each, its share landing on its word ---- */
    ask: (k, T) => {
      const t0 = k.S('ask'), tCi = W(k, 'ask', /^city/i, 2.3), tCo = W(k, 'ask', /^company/i, 4.7);
      k.cut(t0);
      split(k);
      worker(k, 270, 1700, 2.0, false);
      digger(px(k), 250, 560, 1.6, 0.0, 1);
      if (T >= tCi) steps(k, T, [[tCi, CITY, 1]], L_CITY, 264);
      if (T >= tCo) steps(k, T, [[tCo, CO, 1]], L_CO, 264);
      return {host: false};
    },
  },
};
