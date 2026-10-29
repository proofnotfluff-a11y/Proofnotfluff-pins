// Scene: Book the call, don't just answer it (Lesson 9, Lead Clinic, arcade). One function per top-level cue in 03_cues/cues.md.
// Numbers only from k.data (brief.md -> data.js). Every time comes from a cue start (k.S) or a spoken word (wordT), so a
// re-voiced take moves the picture with it.
// Worlds, one per section (brief.md, Worlds): hook = versus select screen; stakes and why = a telephone switchboard drawn
// here (lamps, jacks, patch cords, an operator's hand, a dial that flips to a stopwatch); ask = the wall calendar with a
// headset script card; skip = the boss fight; caveat = the split-flap board; close = the versus rematch with YOUR SHOP.
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', GREY = '#9AA0AD';
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
  const poly = (pts, c, th = 1) => { for (let i = 0; i + 1 < pts.length; i++) line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], c, th); };
  const bevel = (x, y, w, h, base, hi, lo, out) => { if (out) P(x - 1, y - 1, w + 2, h + 2, out); P(x, y, w, h, base); P(x, y, w, 1, hi); P(x, y, 1, h, hi); P(x, y + h - 1, w, 1, lo); P(x + w - 1, y + 1, 1, h - 1, lo); };
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
  const spr = (rows, pal, x, y, s = 1, flip = false) => rows.forEach((r, j) => { for (let i = 0; i < r.length; i++) { const c = pal[r[i]]; if (c) P(x + (flip ? r.length - 1 - i : i) * s, y + j * s, s, s, c); } });
  const twinkle = (x, y, f, c = CREAM) => { const s = [0, 1, 2, 1][((f % 4) + 4) % 4]; DOT(x, y, c); for (let i = 1; i <= s; i++) { DOT(x - i, y, c); DOT(x + i, y, c); DOT(x, y - i, c); DOT(x, y + i, c); } };
  return {P, DOT, dith, disc, ring, line, poly, bevel, win, fr, ease, tx, tw, clip, spr, twinkle, F, T};
};

// ---- the words: every beat lands on a spoken word, so a re-voiced take moves everything with it ----
const WS = () => (window.WORDS && window.WORDS.words) || [];
const norm = (s) => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
// the time a word is said (words.json), at or after a cue (or a time); falls back to the cue's start plus dflt
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
// the start and end of each spoken word of a line, matched in order from t0 (a missing word takes the one before's time)
const spoken = (t0, said) => {
  const ws = WS(); let i = ws.findIndex((x) => x.start >= t0 - 0.05); if (i < 0) i = ws.length;
  let last = t0;
  return said.split(/\s+/).map((wd) => {
    const want = norm(wd); let j = i;
    while (j < ws.length && j < i + 6 && norm(ws[j].w) !== want) j++;
    if (j < ws.length && j < i + 6) { i = j + 1; last = ws[j].start; return [ws[j].start, ws[j].end]; }
    return [last, last + 0.2];
  });
};
// a count that starts at 85% of its value and lands exactly on it
const cnt = (k, num, t0, o = {}) => k.count(num.value, k.lin(t0, t0 + 0.7) >= 1 ? 1 : 0.85 + 0.15 * k.lin(t0, t0 + 0.7), Object.assign({from: 0}, o));
const host = (k, pose) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150});

// ================================================================================================================
// the versus screen (hook, close): the library set plus the big scores painted into the portrait cards
const vsScreen = (k, o) => {
  const d = px(k), n = k.data.numbers;
  k.sets.versus({
    a: {name: 'TOP SHOPS', icon: 'star', stats: o.aStats || [{label: 'BOOKED', value: n.topBook.value, text: n.topBook.shown}]},
    b: o.b, at: o.at, vsAt: o.vsAt, max: 100,
  });
  // the portrait cards: the score, big, where the icon was (same slide as the card)
  [[true, '#2F6F67'], [false, '#E2633B']].forEach(([left, base]) => {
    const X = left ? 20 : 176, W = 140, x = X + d.ease(o.at, 8, left ? -170 : 190);
    d.P(x + 4, 90, W - 8, 84, base);
    for (let i = 0; i < 6; i++) d.DOT(x + 10 + i * 22, 96 + (i % 2) * 70, left ? TEAL : ORANGE);
    const big = left ? o.aBig : o.bBig;
    if (typeof big === 'function') big(x + W / 2, x); else k.text(big, (x + W / 2) * 3, 330, {size: 132, color: CREAM, align: 'center', drop: INK});
    const dim = o.winAt != null && k.T >= o.winAt && !left;
    if (dim) { k.ctx.fillStyle = INK; for (let yy = 84; yy < 244; yy++) for (let xx = x - 2 + (yy & 1); xx < x + W + 2; xx += 2) k.ctx.fillRect(xx * 3, yy * 3, 3, 3); }
    if (left && o.winAt != null && k.T >= o.winAt) k.slam('WIN', (x + W / 2) * 3, 276, o.winAt, {size: 66, color: CREAM, align: 'center', stamp: true, glint: false, drop: INK});
  });
  // VS sits across both cards: the bolt and the letters again, on top (the set's own copy is under the cards)
  if (k.T >= o.vsAt) {
    const MID = 168, bolt = [[MID + 8, 100], [MID - 4, 132], [MID + 6, 132], [MID - 8, 166], [MID + 12, 126], [MID + 2, 126], [MID + 14, 100]], ctx = k.ctx;
    ctx.fillStyle = INK; ctx.beginPath(); bolt.forEach(([x, y], i) => i ? ctx.lineTo((x + 1) * 3, (y + 1) * 3) : ctx.moveTo((x + 1) * 3, (y + 1) * 3)); ctx.closePath(); ctx.fill();
    ctx.fillStyle = GOLD; ctx.beginPath(); bolt.forEach(([x, y], i) => i ? ctx.lineTo(x * 3, y * 3) : ctx.moveTo(x * 3, y * 3)); ctx.closePath(); ctx.fill();
    k.slam('VS', MID * 3, 400, o.vsAt, {size: 132, color: CREAM, align: 'center', stamp: true, glint: false, drop: INK, lint: false});
  }
};

// ================================================================================================================
// the switchboard (stakes, why): our own set piece. A walnut cabinet: a brass name plate, a source strip, a field of ten
// lead lines (a lamp over each jack) above a row of BOOKED jacks, an instrument that is a dial and flips to a stopwatch,
// a key shelf of plugs, and a felt panel below for the scene's words (the content area, frame y 696 to 972).
// Patch cords hang between jacks as sagging curves on whole pixels; the operator's hand carries a plug to its jack.
const COL = (c) => 38 + c * 38;
const LAMP = (i) => [COL(i % 5), 146 + Math.floor(i / 5) * 28];
const JACK = (i) => [COL(i % 5), 157 + Math.floor(i / 5) * 28];
const BJACK = (c) => [COL(c), 198];
const SHELF = (c) => [COL(c) - 9, 218];
const board = (k, o) => {
  const d = px(k), {P, DOT, disc, ring, line, bevel, fr, tx, T, F} = d;
  const dy = o.slideAt != null ? d.ease(o.slideAt, 10, 240) : 0, Y = (y) => y + dy;
  // the room: a dark wall with a picture rail, wainscot under the cabinet, plank floor
  P(0, 0, 360, 640, '#2B2033');
  for (let x = 6; x < 360; x += 18) { P(x, 0, 2, 340, '#3D2E45'); DOT(x + 8, 40 + (x % 5) * 7, '#3D2E45'); }
  P(0, 74, 360, 3, '#4A2E1B'); P(0, 74, 360, 1, '#8C5A33');
  P(0, 336, 360, 81, '#4A2E1B'); for (let x = 0; x < 360; x += 40) { P(x, 340, 1, 77, '#2B2033'); P(x + 1, 340, 1, 77, '#6B4226'); }
  P(0, 336, 360, 2, '#8C5A33');
  for (let y = 417, i = 0; y < 640; y += 10, i++) { P(0, y, 360, 10, i % 2 ? '#6B4226' : '#5A3A22'); P(0, y, 360, 1, '#7A4E2C'); for (let x = (i * 37) % 60; x < 360; x += 60) P(x, y + 1, 1, 9, '#4A2E1B'); }
  // the cabinet
  P(9, Y(79), 342, 262, INK); P(10, Y(80), 340, 260, '#8C5A33'); P(10, Y(80), 340, 2, '#D9A066'); P(10, Y(80), 2, 260, '#B07A47'); P(347, Y(82), 3, 258, '#6B4226');
  for (let x = 14; x < 346; x += 6) DOT(x, Y(83), '#6B4226');
  // the name plate: brass, four screws, the engraved name; it flips (narrows to its edge on whole pixels) to a new name
  const plates = o.plates || [], cur = plates.filter((p) => T >= p.at).pop() || plates[0];
  const pf = cur && cur.at > 0 ? fr(cur.at) : 99, full = 236;
  let pw = full; if (pf < 4) pw = Math.max(2, Math.round(full * (1 - (pf + 1) / 4))); else if (pf < 6) pw = 2; else if (pf < 10) pw = Math.round(full * (pf - 5) / 4);
  const plx = 180 - Math.round(pw / 2), ply = Y(86);
  P(plx - 1, ply - 1, pw + 2, 30, INK); P(plx, ply, pw, 28, ORANGE); P(plx, ply, pw, 1, GOLD); P(plx, ply + 1, pw, 1, '#F7D79B'); P(plx, ply + 26, pw, 2, '#B07A47');
  if (pw === full) {
    [[3, 3], [full - 5, 3], [3, 23], [full - 5, 23]].forEach(([a, b]) => { DOT(plx + a, ply + b, '#B07A47'); DOT(plx + a + 1, ply + b, '#8C5A33'); DOT(plx + a, ply + b - 1, GOLD); });
    tx(cur.text, 180, ply + 3, {size: 66, color: '#4A2E1B', align: 'center', drop: GOLD});
    if (pf < 14) for (let i = 0; i < 3; i++) d.twinkle(plx + 20 + i * 98, ply + 4 + (i % 2) * 18, pf - 6 + i, CREAM);
  }
  // the source strip: types on, a character a frame
  const strips = o.strips || [], st = strips.filter((s) => T >= s.at).pop();
  P(30, Y(117), 300, 16, '#4A2E1B'); P(31, Y(118), 298, 14, '#6B4226'); P(31, Y(118), 298, 1, '#8C5A33');
  if (st) { const s = st.text.slice(0, Math.max(0, fr(st.at) + 1)); d.clip(31, Y(117), 298, 16, () => tx(s, 180 - d.tw(st.text) / 2, Y(118), {color: GOLD, lint: s.length === st.text.length})); }
  // the line field
  P(15, Y(135), 233, 75, INK); P(16, Y(136), 231, 73, '#1B1420'); P(16, Y(136), 231, 1, '#3D2E45'); P(16, Y(136), 1, 73, '#3D2E45');
  for (let c = 0; c < 5; c++) P(COL(c) + 18, Y(140), 1, 64, '#2B2033');
  P(18, Y(190), 196, 16, '#2B2033'); P(18, Y(190), 196, 1, '#4A2E1B');
  tx('LINES', 204, Y(152), {color: GREY});
  tx('BOOKED', 204, Y(192), {color: GOLD});
  const cords = o.cords || [], answer = o.answer;
  const lampState = (i) => {   // 'off' | 'ring' | 'booked' | 'talk' | 'dead'
    const lit = (o.lit || [])[i]; if (lit == null || T < lit) return 'off';
    const cd = cords.find((c) => c.line === i && T >= c.at + c.dur);
    if (cd) return 'booked';
    if (answer && answer.line === i && T >= answer.at + answer.dur) return answer.dropAt != null && T >= answer.dropAt ? 'dead' : 'talk';
    return 'ring';
  };
  for (let i = 0; i < 10; i++) {
    const [lx, ly] = LAMP(i), [jx, jy] = JACK(i), s = lampState(i);
    disc(lx, Y(ly), 5, INK);
    const ph = (Math.floor(T * 2 + hash(i) * 2)) % 2;
    const c = s === 'ring' ? (ph ? GOLD : ORANGE) : s === 'booked' ? TEAL : s === 'talk' ? CREAM : '#3D2E45';
    disc(lx, Y(ly), 4, c);
    if (s !== 'off' && s !== 'dead') { DOT(lx - 1, Y(ly) - 2, CREAM); DOT(lx - 2, Y(ly) - 1, CREAM); }
    if (s === 'ring' && ph) { [[-1], [1]].forEach(([sg]) => { DOT(lx + sg * 8, Y(ly) - 2, GOLD); DOT(lx + sg * 9, Y(ly), GOLD); DOT(lx + sg * 8, Y(ly) + 2, GOLD); }); }
    ring(jx, Y(jy), 4, '#B07A47'); disc(jx, Y(jy), 2, INK); DOT(jx - 2, Y(jy) - 3, GOLD);
  }
  for (let c = 0; c < 5; c++) { const [bx, by] = BJACK(c); ring(bx, Y(by), 4, GOLD); disc(bx, Y(by), 2, INK); DOT(bx - 2, Y(by) - 3, CREAM); }
  // the instrument: a dial (book rate) that flips to a stopwatch for the first minute
  const ix = 250, iy = Y(135), iw = 92, ih = 75, inst = o.inst || {};
  const ff = inst.flipAt != null ? fr(inst.flipAt) : -1, flipped = ff >= 6;
  let w2 = iw; if (ff >= 0 && ff < 4) w2 = Math.max(2, Math.round(iw * (1 - (ff + 1) / 4))); else if (ff >= 4 && ff < 6) w2 = 2; else if (ff >= 6 && ff < 10) w2 = Math.round(iw * (ff - 5) / 4);
  const ixx = ix + Math.round((iw - w2) / 2);
  P(ixx - 1, iy - 1, w2 + 2, ih + 2, INK); bevel(ixx, iy, w2, ih, '#4A4E5A', '#9AA0AD', '#2B2033');
  if (w2 === iw && !flipped) {   // the dial: 0 to 100, a mark at the top shops' rate, the needle overshoots and settles
    const cx = 296, cy = iy + 56, r = 33;
    for (let yy = -r; yy <= 0; yy++) { const hw = Math.floor(Math.sqrt(r * r - yy * yy) + 0.4); P(cx - hw, cy + yy, 2 * hw + 1, 1, yy > -3 ? '#E6D3BC' : '#F4E6D3'); }
    for (let v = 0; v <= 100; v += 10) { const a = Math.PI + (v / 100) * Math.PI; DOT(cx + Math.round(Math.cos(a) * (r - 2)), cy + Math.round(Math.sin(a) * (r - 2)), '#6B7080'); }
    const ma = Math.PI + (inst.mark / 100) * Math.PI;
    line(cx + Math.round(Math.cos(ma) * (r - 7)), cy + Math.round(Math.sin(ma) * (r - 7)), cx + Math.round(Math.cos(ma) * r), cy + Math.round(Math.sin(ma) * r), RED, 2);
    tx(String(inst.mark), cx + Math.round(Math.cos(ma) * (r - 15)), cy + Math.round(Math.sin(ma) * (r - 15)) - 6, {color: RED, align: 'center'});
    let v = 0;
    if (inst.at != null && T >= inst.at) { const q = clamp((T - inst.at) / 0.9); v = inst.value * (q >= 1 ? 1 : 1 + (1 - q) * 0.35 * Math.sin(q * 9) * (q > 0.25 ? 1 : 0)) * Math.min(1, q * 2.2); }
    const deg = Math.round(180 + clamp(v, 0, 100) * 1.8), a = deg * Math.PI / 180;
    line(cx, cy, cx + Math.round(Math.cos(a) * (r - 5)), cy + Math.round(Math.sin(a) * (r - 5)), RED, 1);
    disc(cx, cy, 3, INK); DOT(cx, cy, GREY);
    if (inst.at != null && T >= inst.at) tx(k.count(inst.value, clamp((T - inst.at) / 0.9), {from: inst.value * 0.85, suffix: '%'}), cx, cy + 4, {color: GOLD, align: 'center', drop: INK});
  } else if (w2 === iw) {   // the stopwatch: a sixty-second face, the elapsed slice filling red behind the sweep hand
    const cx = 296, cy = iy + 38, r = 31, el = Math.max(0, T - inst.clockAt), deg = Math.floor(el * 6) % 360;
    disc(cx, cy - r - 3, 3, GREY); P(cx - 1, cy - r - 1, 3, 2, GREY);
    disc(cx, cy, r + 1, INK); disc(cx, cy, r, '#F4E6D3');
    for (let yy = -r; yy <= r; yy++) for (let xx = -r; xx <= r; xx++) {
      if (xx * xx + yy * yy > (r - 2) * (r - 2)) continue; let ang = Math.atan2(xx, -yy) * 180 / Math.PI; if (ang < 0) ang += 360;
      if (ang < deg) DOT(cx + xx, cy + yy, ((xx + yy) & 1) ? '#F09A9A' : '#E2633B');
    }
    for (let s = 0; s < 12; s++) { const a = s * Math.PI / 6 - Math.PI / 2; DOT(cx + Math.round(Math.cos(a) * (r - 2)), cy + Math.round(Math.sin(a) * (r - 2)), s % 3 ? '#6B7080' : INK); }
    const a = deg * Math.PI / 180 - Math.PI / 2;
    line(cx, cy, cx + Math.round(Math.cos(a) * (r - 4)), cy + Math.round(Math.sin(a) * (r - 4)), '#7A3442', 1);
    disc(cx, cy, 2, INK);
    tx('60', cx, cy - r + 4, {color: INK, align: 'center', lint: false});
  }
  // the key shelf: a slanted ledge with a plug standing in each slot, toggle keys
  P(12, Y(211), 336, 22, '#6B4226'); P(12, Y(211), 336, 2, '#D9A066'); P(12, Y(213), 336, 1, '#B07A47'); P(12, Y(231), 336, 2, '#4A2E1B');
  const used = (c) => cords.some((cd) => cd.slot === c && T >= cd.at) || (answer && answer.slot === c && T >= answer.at);
  for (let c = 0; c < 5; c++) {
    const [sx, sy] = SHELF(c); P(sx - 2, Y(sy) + 4, 5, 3, INK);
    if (!used(c)) { P(sx - 1, Y(sy) - 4, 3, 8, '#4A4E5A'); P(sx - 1, Y(sy) - 6, 3, 2, c % 2 ? RED : TEAL); DOT(sx - 1, Y(sy) - 3, GREY); }
    const kx = COL(c) + 6; P(kx, Y(218), 4, 8, INK); P(kx + 1, Y(216) + ((c + Math.floor(F / 45)) % 4 === 0 ? 1 : 0), 2, 4, CREAM);
  }
  // the felt panel: where the scene's words go
  P(14, Y(236), 332, 94, INK); P(15, Y(237), 330, 92, '#24453A'); P(15, Y(237), 330, 1, '#3E7A62');
  for (let i = 0; i < 60; i++) DOT(18 + Math.floor(hash(i * 3.3) * 324), Y(240) + Math.floor(hash(i * 7.1) * 86), '#2F5A4A');
  [[18, 240], [338, 240], [18, 324], [338, 324]].forEach(([a, b]) => { DOT(a, Y(b), GOLD); DOT(a + 1, Y(b), '#B07A47'); });
  // the cords: a sag between two points, on whole pixels, a dark underside and a plug at each end
  const sag = (a, b, s) => { const c = [(a[0] + b[0]) / 2, Math.max(a[1], b[1]) + s], out = []; for (let i = 0; i <= 16; i++) { const t = i / 16; out.push([(1 - t) * (1 - t) * a[0] + 2 * (1 - t) * t * c[0] + t * t * b[0], (1 - t) * (1 - t) * a[1] + 2 * (1 - t) * t * c[1] + t * t * b[1]]); } return out.map(([x, y]) => [Math.round(x), Math.round(y)]); };
  const plug = (x, y, c) => { P(x - 2, y - 9, 5, 6, INK); P(x - 1, y - 8, 3, 4, c); P(x - 1, y - 4, 3, 3, GOLD); DOT(x - 1, y - 8, CREAM); };
  const hand = (x, y) => {   // the operator's hand from below the shelf: a blue sleeve, fingers round the plug
    d.clip(0, 0, 360, Y(231), () => {
      P(x - 5, y + 2, 11, 60, INK); P(x - 4, y + 3, 9, 60, '#3B82C4'); P(x - 4, y + 3, 2, 60, '#87CEEB'); P(x - 4, y + 10, 9, 2, '#253048');
      P(x - 4, y - 4, 9, 8, INK); P(x - 3, y - 3, 7, 6, '#F0B98D'); P(x + 2, y - 3, 2, 6, '#C98B63'); P(x - 4, y - 6, 3, 3, '#F0B98D'); DOT(x - 4, y - 6, INK);
    });
  };
  const travel = (cd) => { const q = eo((T - cd.at) / cd.dur); return [Math.round(cd.from[0] + (cd.to[0] - cd.from[0]) * q), Math.round(cd.from[1] + (cd.to[1] - cd.from[1]) * q)]; };
  let handAt = null;
  cords.forEach((cd, i) => {
    if (T < cd.at) return;
    const a = JACK(cd.line), b = T < cd.at + cd.dur ? travel(Object.assign({from: SHELF(cd.slot), to: BJACK(cd.b)}, cd)) : BJACK(cd.b);
    const A = [a[0], Y(a[1])], B = [b[0], Y(b[1])], pts = sag(A, B, 14);
    d.poly(pts.map(([x, y]) => [x, y + 1]), '#7A3442', 2); d.poly(pts, cd.c || RED, 2);
    plug(A[0], A[1], cd.c || RED); plug(B[0], B[1], cd.c || RED);
    const since = T - cd.at - cd.dur;
    if (since >= 0 && since < 0.1) ring(B[0], B[1], 7, CREAM);
    if (T < cd.at + cd.dur + 0.35) handAt = since < 0.15 ? B : [B[0], B[1] + Math.round(60 * eo((since - 0.15) / 0.2))];
  });
  if (answer && T >= answer.at) {   // the answering cord: from the shelf to the ringing line; it falls out at dropAt
    const sh = SHELF(answer.slot), to = JACK(answer.line);
    let b = T < answer.at + answer.dur ? travel({at: answer.at, dur: answer.dur, from: sh, to}) : to;
    if (answer.dropAt != null && T >= answer.dropAt) { const g = T - answer.dropAt, yy = to[1] + Math.round(Math.min(46, 30 * g + 260 * g * g)); b = [to[0] - Math.min(6, Math.round(g * 20)), yy]; }
    const A = [sh[0], Y(sh[1]) + 2], B = [b[0], Y(b[1])], pts = sag(A, B, 16);
    d.poly(pts.map(([x, y]) => [x, y + 1]), '#245752', 2); d.poly(pts, TEAL, 2); plug(B[0], B[1], TEAL);
    const since = T - answer.at - answer.dur;
    if (since >= 0 && since < 0.1) ring(B[0], B[1], 7, CREAM);
    if (T < answer.at + answer.dur + 0.35) handAt = since < 0.15 ? B : [B[0], B[1] + Math.round(60 * eo((since - 0.15) / 0.2))];
    // the call: two speech bubbles trade dots over the lamp while it talks
    if (since > 0.2 && (answer.dropAt == null || T < answer.dropAt)) {
      const [lx, ly] = LAMP(answer.line), turn = Math.floor((T - answer.at) / 0.8) % 2, dots = 1 + (fr(answer.at) >> 3) % 3;
      const bx = lx + (turn ? 10 : -34), by = Y(ly) - 22;
      P(bx - 1, by - 1, 26, 12, INK); P(bx, by, 24, 10, turn ? CREAM : '#87CEEB'); P(bx + (turn ? 2 : 18), by + 10, 4, 3, INK); P(bx + (turn ? 3 : 19), by + 10, 2, 2, turn ? CREAM : '#87CEEB');
      for (let j = 0; j < dots; j++) P(bx + 5 + j * 6, by + 4, 2, 2, INK);
    }
    // NO ASK: a red tag swings on the empty jack, then rests
    if (answer.dropAt != null && T >= answer.dropAt + 0.35) {
      const f = fr(answer.dropAt + 0.35), sw = [0, -5, -4, -1, 3, 4, 2, -1, -2, -1, 0, 1, 0][Math.min(12, Math.floor(f / 2))];
      const [jx, jy] = JACK(answer.line), tx0 = jx + sw, ty = Y(jy) + 12;
      line(jx, Y(jy) + 3, tx0, ty, CREAM);
      P(tx0 - 22, ty - 1, 45, 17, INK); P(tx0 - 21, ty, 43, 15, RED); P(tx0 - 21, ty, 43, 1, '#F09A9A'); DOT(tx0, ty + 2, INK);
      tx('NO ASK', tx0, ty + 2, {color: CREAM, align: 'center', lint: f >= 26});
    }
  }
  if (handAt) hand(handAt[0], handAt[1]);
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 9',
  transitions: {stakes: 'levelselect', why: 'dissolve', ask: 'door', skip: 'iris', caveat: 'blinds', close: 'gameover'},
  trauma: {'skip.ko': 0.8},
  sections: {
    // ---- hook: the versus screen, settled on frame 0 (both scores, the source), no host, no dialog until the first beat
    hook: (k, T) => {
      const n = k.data.numbers, tTop = k.S('hook.top'), tVs = wordT(k, 'hook.vs', /^Everyone/i), t39 = wordT(k, 'hook.vs', /^Thirty/i), tLine = k.S('hook.line');
      vsScreen(k, {at: -0.4, vsAt: -0.8, winAt: t39 + 0.35, aBig: n.topBook.shown, bBig: n.restBook.shown,
        b: {name: 'EVERYONE ELSE', icon: 'phone', stats: [{label: 'BOOKED', value: n.restBook.value, text: n.restBook.shown}]}});
      const d = px(k);
      // the pings: a ring that steps out from each score as it is said (never on frame 0)
      const ping = (t0, x, y) => { const f = d.fr(t0); if (f >= 0 && f < 12) { const g = 2 + f * 2; d.P(x - 70 - g, y - g, 140 + 2 * g, 1, CREAM); d.P(x - 70 - g, y + 26 + g, 140 + 2 * g, 1, CREAM); d.P(x - 70 - g, y - g, 1, 26 + 2 * g, CREAM); d.P(x + 70 + g, y - g, 1, 27 + 2 * g, CREAM); } };
      ping(tTop, 90, 212); ping(tVs, 246, 212);
      k.burst(270, 400, tTop, {n: 22, r: 260}); k.burst(738, 400, t39, {n: 16, r: 200, colors: ['paper', 'accent2']});
      // under the cards: what the numbers are, and the source, from frame 0 (on a plate, so the split line never runs through them)
      d.win(14, 270, 332, 56, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
      if (T < tLine) k.text('of lead calls booked', 540, 836, {size: 66, color: CREAM, align: 'center', drop: INK});
      else {
        k.slam('The line that asks for the booking.', 540, 846, tLine, {size: 39, color: 'accent', align: 'center', drop: INK, from: 0.5});
        k.sweep(180, 894, 720, 6, tLine + 0.25, {color: 'accent'});
      }
      k.text(`ServiceTitan customers, ${n.stMonths.shown} months to Jan ${n.stYear.shown}`, 528, 930, {size: 30, color: SAND, align: 'center'});
      if (T < tTop) return {host: false, speech: false};
      if (T < tLine) return {host: false};
      return host(k, k.live('hook.line') ? 'point' : null);
    },

    // ---- stakes: the switchboard slides up; lead lines light and ring; the hand books three of them
    stakes: (k, T) => {
      const n = k.data.numbers, t0 = k.S('stakes');
      const tTop = wordT(k, 'stakes.top', /^top$/i, 1), tRev = wordT(k, 'stakes.top', /^revenue/i, 2), tMk = wordT(k, 'stakes.marketing', /^marketing/i, 0.8);
      const lit = [0, 6, 3, 8, 1, 5, 9, 2, 7, 4].reduce((a, line, i) => { a[line] = t0 + 0.5 + i * 0.75; return a; }, []);
      board(k, {
        slideAt: t0, lit,
        plates: [{text: 'SERVICETITAN', at: -1}],
        strips: [{text: `Its customers, ${n.stMonths.shown} months to Jan ${n.stYear.shown}`, at: k.S('stakes.window')}],
        cords: [{line: 0, b: 0, slot: 0, at: tTop, dur: 0.4}, {line: 6, b: 1, slot: 1, at: tRev, dur: 0.4, c: '#3B82C4'}, {line: 3, b: 2, slot: 2, at: tMk, dur: 0.4}],
        inst: {at: wordT(k, 'stakes.near', /^thirty/i), value: n.restBook.value, mark: n.topBook.value, flipAt: k.S('stakes.minute'), clockAt: wordT(k, 'stakes.minute', /^first/i)},
      });
      // the felt panel (x 72 to 930, y 708 to 970), one idea at a time
      const near = k.S('stakes.near'), minute = k.S('stakes.minute');
      if (T < near) {
        k.ctx.save(); k.ctx.translate(0, px(k).ease(t0, 10, 240) * 3);
        k.text('Top shops', 72, 716, {size: 66, color: CREAM}); k.slam(n.topBook.shown, 930, 716, t0 + 0.3, {size: 66, color: 'accent', align: 'right', from: 0.5});
        k.text('Everyone else', 72, 790, {size: 66, color: SAND}); k.slam(n.restBook.shown, 930, 790, t0 + 0.6, {size: 66, color: SAND, align: 'right', from: 0.5});
        k.ctx.restore();
        if (T >= k.S('stakes.top')) { k.slam(`Top shops: top ${n.topPct.shown} by revenue`, 72, 884, k.S('stakes.top'), {size: 39, color: GOLD, from: 0.4}); k.sweep(72, 930, 600, 6, k.S('stakes.top') + 0.3, {color: 'teal'}); }
      } else if (T < minute) {
        k.slam(`Near ${n.restBook.shown}?`, 72, 716, near, {size: 66, color: 'accent', from: 0.5, drop: INK});
        if (T >= k.S('stakes.marketing')) k.slam('Probably not your marketing.', 72, 806, k.S('stakes.marketing'), {size: 39, color: CREAM, from: 0.4});
        k.text('ServiceTitan', 72, 900, {size: 30, color: SAND});
      } else {
        k.slam('"The first 60 seconds', 72, 716, minute, {size: 66, color: CREAM, from: 0.5, drop: INK});
        k.slam('after the phone rings."', 72, 792, minute + 0.15, {size: 66, color: CREAM, from: 0.5, drop: INK});
        k.text('ServiceTitan, on what to check first', 72, 900, {size: 30, color: SAND});
        k.sweep(72, 870, 300, 6, minute + 0.4, {color: 'accent'});
      }
      return host(k, k.live('stakes.near') || k.live('stakes.minute') ? 'point' : (k.live('stakes.window') ? 'clip' : null));
    },

    // ---- why: the same board, the first minute on the stopwatch; the operator answers a line, it talks, the cord falls out
    why: (k, T) => {
      const n = k.data.numbers, t0 = k.S('why'), st = k.S('stakes');
      const pct = k.S('why.pct'), noask = k.S('why.noask'), tJob = wordT(k, 'why.ends', /^job/i, 0.6);
      const lit = [0, 6, 3, 8, 1, 5, 9, 2, 7, 4].reduce((a, line, i) => { a[line] = st + 0.5 + i * 0.75; return a; }, []);
      board(k, {
        lit,
        plates: [{text: 'SERVICETITAN', at: -1}, {text: 'INVOCA', at: wordT(k, 'why.invoca', /^Invoca/i)}],
        strips: [{text: `Its customers, ${n.stMonths.shown} months to Jan ${n.stYear.shown}`, at: -1}, {text: 'Lead conversion benchmarks, Jul 2026', at: wordT(k, 'why.invoca', /^Invoca/i) + 0.35}],
        cords: [{line: 0, b: 0, slot: 0, at: -3, dur: 0.4}, {line: 6, b: 1, slot: 1, at: -2, dur: 0.4, c: '#3B82C4'}, {line: 3, b: 2, slot: 2, at: -1, dur: 0.4}],
        answer: {line: 8, slot: 3, at: t0 + 0.3, dur: 0.45, dropAt: tJob},
        inst: {flipAt: -1, clockAt: wordT(k, 'stakes.minute', /^first/i), value: n.restBook.value, mark: n.topBook.value},
      });
      if (T < pct) {
        k.slam('What goes wrong', 72, 716, t0 + 0.2, {size: 66, color: CREAM, from: 0.5, drop: INK});
        k.slam('on that call?', 72, 792, t0 + 0.6, {size: 66, color: 'accent', from: 0.5, drop: INK});
        if (T >= k.S('why.invoca')) k.text('Call tracker Invoca found...', 72, 900, {size: 39, color: SAND});
      } else {
        const tp = wordT(k, 'why.pct', /^fifty/i);
        k.slam(cnt(k, n.noAsk, tp, {suffix: '%'}), 72, 708, tp, {size: 132, color: 'accent', from: 0.5, drop: INK});
        k.burst(200, 760, tp + 0.7, {n: 18, r: 220});
        k.slam('of home service', 400, 724, tp + 0.4, {size: 39, color: CREAM, from: 0.4});
        k.slam('businesses', 400, 768, tp + 0.6, {size: 39, color: CREAM, from: 0.4});
        if (T >= tp + 0.9) k.text('(calls on its platform)', 400, 812, {size: 30, color: SAND});
        if (T >= noask) {
          k.slam("don't ask leads to", 72, 862, noask, {size: 39, color: CREAM, from: 0.4});
          k.slam('buy or book the job.', 72, 910, wordT(k, 'why.noask', /^buy/i), {size: 39, color: CREAM, from: 0.4});
          k.sweep(72, 900, 150, 6, noask + 0.3, {color: 'accent'});
        }
      }
      return host(k, k.live('why.noask') ? 'point' : null);
    },

    // ---- ask: the wall calendar; the script types on a headset card as it is said; two slots glow, one locks
    ask: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('ask');
      const tA = wordT(k, 'ask.l3', /^two/i), tB = wordT(k, 'ask.tomorrow', /^nine/i), tLock = wordT(k, 'ask.pick', /^better/i), tTwo = k.S('ask.two');
      const cal = k.sets.calendar({month: 'THIS WEEK', start: 0, days: 7,
        fills: [{day: 5, at: tA, c: GOLD}, {day: 6, at: tB, c: GOLD}, {day: 5, at: tLock, c: TEAL}],
        run: {from: 1, to: 4, at: t0 + 0.3, every: 0.1, c: '#E6D3BC'}, weeks: [{row: 0, at: t0 + 0.5}]});
      // the two slots: a gold frame that swaps light and shade twice a second, the time, then the lock on one
      const slot = (day, at, label, locked) => {
        if (T < at) return;
        const [x, y, w, h] = cal.cell(day).map((v) => Math.round(v / 3)), f = d.fr(at), pulse = T >= tTwo && d.fr(tTwo) < 8 ? 1 : 0;
        const c = locked ? TEAL : (Math.floor((T - at) * 2) % 2 ? GOLD : ORANGE);
        const g = (f < 4 ? 3 - f : 0) + pulse;
        [[x - 1 - g, y - 1 - g, w + 2 + 2 * g, 2], [x - 1 - g, y + h - 1 + g, w + 2 + 2 * g, 2], [x - 1 - g, y - 1 - g, 2, h + 2 + 2 * g], [x + w - 1 + g, y - 1 - g, 2, h + 2 + 2 * g]].forEach(([a, b, ww, hh]) => d.P(a, b, ww, hh, locked ? '#2F6F67' : c));
        d.tx(label, x + w / 2, y + 34, {color: locked ? CREAM : '#7A3442', align: 'center'});
      };
      const locked = T >= tLock + 0.1;
      slot(5, tA, `${n.timeA.shown} PM`, locked); slot(6, tB, `${n.timeB.shown} AM`, false);
      if (T >= tLock) {   // the padlock drops onto the booked slot and clicks shut
        const [x, y, w] = cal.cell(5).map((v) => Math.round(v / 3)), f = d.fr(tLock), ly = y + 16 + (f < 4 ? [-8, -5, -2, 1][f] : 0), lx = x + w - 13;
        const shut = f >= 4 ? 0 : 2;
        d.P(lx + 2, ly - 1 - shut, 7, 2, INK); d.P(lx + 2, ly - 1 - shut, 2, 6 + shut, INK); d.P(lx + 7, ly + 1 - shut, 2, 4 + shut, INK);
        d.P(lx + 3, ly - shut, 5, 1, GREY);
        d.P(lx, ly + 3, 11, 9, INK); d.P(lx + 1, ly + 4, 9, 7, ORANGE); d.P(lx + 1, ly + 4, 9, 1, GOLD); d.P(lx + 5, ly + 6, 1, 3, INK);
        if (f >= 4 && f < 10) d.twinkle(lx + 12, ly + 1, f - 4);
        k.burst((x + w / 2) * 3, (y + 40) * 3, tLock + 0.13, {n: 14, r: 160});
      }
      // the headset card over the calendar's last weeks (the two slots stay clear above it)
      const cy = 210, cx = 22, cw = 316, ch = 112, open = d.ease(t0 + 0.2, 8, 140);
      d.clip(0, 0, 360, 330, () => {
        const Y = cy + open;
        d.win(cx, Y, cw, ch, {base: '#253048', hi: '#3B82C4', lo: '#1B1420', rule: '#5B8FB9'});
        d.P(cx + 4, Y + 4, cw - 8, 15, '#7A3442'); d.P(cx + 4, Y + 18, cw - 8, 1, INK);
        // the headset: band, two cups, the mic boom
        d.ring(cx + 15, Y + 13, 6, CREAM); d.P(cx + 8, Y + 12, 4, 6, INK); d.P(cx + 9, Y + 13, 2, 4, GOLD); d.P(cx + 19, Y + 12, 4, 6, INK); d.P(cx + 20, Y + 13, 2, 4, GOLD); d.P(cx + 9, Y + 17, 1, 2, CREAM); d.P(cx + 10, Y + 18, 4, 1, CREAM);
        d.P(cx + 4, Y + 19, 18, 1, '#7A3442');
        const head = T >= tTwo ? 'TWO TIMES. NOT AN OPEN QUESTION.' : (T >= k.S('ask.skip') ? 'THE PART PEOPLE SKIP' : 'SAY THIS ON EVERY CALL (EXAMPLE)');
        const hs = T >= k.S('ask.skip') ? (T >= tTwo ? tTwo : k.S('ask.skip')) : -1;
        if (hs < 0 || d.fr(hs) >= 3) d.tx(head, cx + 30, Y + 5, {color: hs >= 0 ? GOLD : CREAM, lint: open === 0}); else d.dith(cx + 30, Y + 6, 200, 11, '#3D2E45');
      });
      const rows = [
        {show: 'Got it, water at the base of the heater.', said: 'Got it, water at the base of the heater.', at: k.S('ask.l1')},
        {show: 'We can take care of that.', said: 'We can take care of that.', at: k.S('ask.l2')},
        {show: `I can get a tech there today at ${n.timeA.shown}, or tomorrow at ${n.timeB.shown}. Which works better?`, said: 'I can get a tech there today at two, or tomorrow at nine. Which works better?', at: k.S('ask.l3')},
      ];
      if (open === 0) {
        let y = (cy + 25) * 3;
        rows.forEach((r, i) => {
          k.shape(k.rectPts(90, y + 3, 33, 39, 0), {fill: T >= r.at ? GOLD : '#3D2E45', line: false});
          k.text(String(i + 1), 106, y + 3, {size: 39, color: INK, align: 'center'});
          const times = spoken(r.at, r.said), words = r.show.split(/\s+/), sp = k.measure(' ', {size: 39});
          let x = 144, yy = y, lines = 1;
          words.forEach((wd, j) => {
            const ww = k.measure(wd, {size: 39});
            if (x + ww > 924 && x > 144) { x = 144; yy += 45; lines++; }
            const [ws, we] = times[j] || [1e9, 1e9];
            if (T < ws) { k.shape(k.rectPts(x, yy + 33, ww, 3, 0), {fill: '#3D2E45', line: false}); }
            else k.text(wd, x, yy, {size: 39, color: T < we + 0.05 ? GOLD : CREAM});
            x += ww + sp;
          });
          y += lines * 45 + 6;
        });
      }
      const quote0 = k.S('ask.l1') - 0.05, quote1 = k.S('ask.skip') - 0.05;
      const r = host(k, k.live('ask.pick') ? 'point' : (k.live('ask.two') ? 'point' : null));
      if (T >= quote0 && T < quote1) r.speech = false;   // the card is the dialog while the script is said
      return r;
    },

    // ---- skip: the boss fight. The open question spawns LET ME CHECK AND CALL YOU BACK; two times knock it out
    skip: (k, T) => {
      const d = px(k), t0 = k.S('skip'), tPick = k.S('skip.pick');
      const h1 = wordT(k, 'skip.pick', /^Two/i), h2 = wordT(k, 'skip.pick', /^pick/i), h3 = wordT(k, 'skip.ko', /^Mornings/i), h4 = wordT(k, 'skip.ko', /^afternoons/i);
      const tHw = wordT(k, 'skip.homework', /^homework/i);
      const n = k.data.numbers;
      k.sets.boss({name: 'LET ME CHECK AND CALL YOU BACK', hp: 100, t0: tPick, menu: 'TWO TIMES',
        hits: [{at: h1, dmg: 20, label: `TODAY ${n.timeA.shown} PM`}, {at: h2, dmg: 20, label: `TOMORROW ${n.timeB.shown} AM`}, {at: h3, dmg: 30, label: 'MORNINGS'}, {at: h4, dmg: 30, label: 'AFTERNOONS'}],
        defeatAt: h4 + 0.1, winText: 'BOOKED!'});
      // before the menu opens: the battle log in the menu window
      if (T < tPick) {
        const log = [['A wild boss appears!', t0 + 0.1, CREAM], ['It throws HOMEWORK!', tHw, GOLD], ["It's super effective.", tHw + 0.7, RED]];
        log.forEach(([s, at, c], i) => { if (T >= at) { const m = s.slice(0, Math.max(1, d.fr(at) + 1)); d.tx(m, 28, 138 + i * 22, {color: c, lint: m.length === s.length}); } });
        if ((d.F >> 3) & 1) d.P(160, 240, 5, 3, CREAM);
      }
      // the caller: a small tech between the menu and the boss; the homework sheet flies and knocks him back a step
      const hit = tHw + 0.5, hf = d.fr(hit), kb = hf >= 0 && hf < 8 ? [3, 3, 2, 2, 1, 1, 0, 0][hf] : 0, bob = (d.F >> 4) & 1;
      const TECH = ['..rrrr..', '.rrrrrr.', '..ssss..', '..sKsK..', '..ssss..', '.tttttt.', 'tttttttt', 'tt.tt.tt', 'ss.tt.ss', '..tttt..', '..nnnn..', '..n..n..', '..n..n..', '.kk..kk.'];
      d.spr(TECH, {r: RED, s: '#F0B98D', K: INK, t: '#2F6F67', n: '#253048', k: INK}, 184 - kb, 233 + bob, 2);
      if (hf >= 0 && T < tPick) { d.P(198 - kb, 216, 9, 13, INK); d.tx('?', 202 - kb, 216, {color: GOLD, align: 'center', lint: false}); }
      if (T >= tHw && T < hit) {   // the homework sheet: an arc from the boss to the tech, turning every 3 frames
        const q = (T - tHw) / (hit - tHw), x = Math.round(236 + (196 - 236) * q), y = Math.round(196 + (236 - 196) * q - 40 * Math.sin(q * Math.PI)), side = (d.F / 3 | 0) % 2;
        if (side) { d.P(x - 1, y - 1, 12, 14, INK); d.P(x, y, 10, 12, CREAM); for (let j = 0; j < 4; j++) d.P(x + 2, y + 2 + j * 3, 6, 1, '#6B7080'); d.P(x + 6, y, 4, 2, RED); }
        else { d.P(x - 1, y + 3, 14, 8, INK); d.P(x, y + 4, 12, 6, SAND); }
      }
      // the caption plate under the arena: one line at a time
      const cap = (s, at, o = {}) => k.slam(s, 540, o.y || 828, at, Object.assign({size: 66, color: CREAM, align: 'center', from: 0.5, drop: INK}, o));
      d.win(14, 268, 332, 56, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
      const st = k.S('skip.st');
      if (T < k.S('skip.homework')) cap('"When works for you?"', t0 + 0.05, {color: GOLD});
      else if (T < tPick) { cap('Open question', k.S('skip.homework')); cap('= homework.', k.S('skip.homework') + 0.2, {y: 896, color: GOLD}); }
      else if (T < st) { cap('Two times. Just pick.', tPick, {color: GOLD}); k.text('(example times)', 540, 906, {size: 30, color: SAND, align: 'center'}); }
      else {
        cap('"Are mornings or afternoons', st, {size: 39, y: 822});
        cap('better for you?"', st + 0.15, {size: 39, y: 866});
        k.text('ServiceTitan sample call script, Feb 2024', 540, 920, {size: 30, color: SAND, align: 'center'});
      }
      return host(k, k.live('skip.ko') ? 'point' : (k.live('skip.homework') ? 'shrug' : null));
    },

    // ---- caveat: the split-flap board. It says where the numbers come from, then flips row by row to the Friday habit
    caveat: (k, T) => {
      const n = k.data.numbers, t0 = k.S('caveat');
      const one = [
        {label: 'SERVICETITAN', value: '', at: Math.min(t0 + 0.45, wordT(k, 'caveat', /^ServiceTitan/i, 1.6))},   // lands as the board opens (never empty over 1 s)
        {label: 'CUSTOMERS', value: '', at: wordT(k, 'caveat', /^customers/i, 2.4)},
        {label: 'A PATTERN', value: '', at: wordT(k, 'caveat.pattern', /^pattern/i, 0.8)},
        {label: '', value: 'NOT PROOF', at: wordT(k, 'caveat.pattern', /^proof/i, 1.6), hi: true},
      ];
      const two = [
        {label: '', value: 'EVERY FRIDAY', at: wordT(k, 'caveat.friday', /^Friday/i, 1.2), hi: true},
        {label: 'BOOKED CALLS', value: '', at: wordT(k, 'caveat.formula', /^Booked/i)},
        {label: '/ LEAD CALLS', value: '', at: wordT(k, 'caveat.formula', /^divided/i, 0.6)},
        {label: '', value: '= BOOK RATE', at: wordT(k, 'caveat.formula', /^calls\./i, 1.7) + 0.15, hi: true},
      ];
      const rows = one.map((r, i) => (T >= two[i].at ? two[i] : r));
      k.sets.flaps({title: T >= k.S('caveat.friday') ? 'YOUR FRIDAY CHECK' : 'ONE HONEST NOTE', cols: 12, rows});
      const fri = k.S('caveat.friday'), form = k.S('caveat.formula'), d = px(k);
      d.win(14, 282, 332, 42, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
      if (T < fri) {
        k.slam(`ServiceTitan customers, ${n.stMonths.shown} months to Jan ${n.stYear.shown}`, 528, 864, t0 + 0.2, {size: 39, color: CREAM, align: 'center', from: 0.4});
        if (T >= k.S('caveat.pattern')) k.slam('Correlated, not shown to cause.', 540, 910, k.S('caveat.pattern'), {size: 39, color: GOLD, align: 'center', from: 0.4});
      } else if (T < form) {
        k.slam('Track your own.', 540, 870, fri, {size: 66, color: CREAM, align: 'center', from: 0.5, drop: INK});
      } else {
        k.slam('Your booking rate.', 540, 864, form, {size: 66, color: 'accent', align: 'center', from: 0.5, drop: INK});
        k.text('Screenshot this.', 540, 928, {size: 30, color: SAND, align: 'center'});
      }
      return host(k, k.live('caveat.formula') ? 'point' : (k.live('caveat.friday') ? 'clip' : null));
    },

    // ---- close: the rematch. TOP SHOPS 62% against YOUR SHOP ?, then one column: the line, the send line, the ask
    close: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('close'), send = k.S('close.send'), nx = k.S('close.next');
      vsScreen(k, {at: t0 - 0.1, vsAt: t0 + 0.15, aBig: n.topBook.shown,
        bBig: (cx) => {
          if (T < nx) k.text('?', cx * 3, 330, {size: 132, color: Math.floor((T - t0) * 2) % 2 ? GOLD : CREAM, align: 'center', drop: INK});
          else {   // the ? turns into a lit lamp: the next call, booked
            const f = d.fr(nx), cy = 131, r = f < 3 ? 6 + f * 5 : 20;
            d.disc(cx, cy, r + 2, INK); d.disc(cx, cy, r, GOLD); d.disc(cx - 3, cy - 3, Math.max(2, r - 8), '#F7D79B'); d.P(cx - 6, cy + r, 13, 6, GREY); d.P(cx - 6, cy + r + 2, 13, 1, '#6B7080');
            if (f >= 3) for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4 + ((d.F >> 2) & 1) * Math.PI / 8; d.P(cx + Math.round(Math.cos(a) * 30) - 1, cy + Math.round(Math.sin(a) * 30) - 1, 3, 3, CREAM); }
          }
        },
        b: {name: 'YOUR SHOP', icon: 'phone', stats: []}, aStats: []});
      // the column: a game window over the stat rows, one left edge (x 120), everything above y 930
      const open = d.ease(t0 + 0.25, 8, 110);
      d.clip(0, 0, 360, 330, () => d.win(14, 207 + open, 332, 106, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#7A3442'}));
      if (open === 0) {
        k.slam("Answering isn't booking.", 120, 642, t0 + 0.3, {size: 66, color: 'accent', from: 0.5, drop: INK});
        if (T >= send) {
          k.chip('ProofNotFluff', 120, 722, {size: 30});
          k.slam('Send this to whoever answers your phone.', 120, 790, send + 0.1, {size: 39, color: CREAM, from: 0.4});
        }
        if (T >= nx) { k.slam('Book the next call.', 120, 846, nx, {size: 66, color: GOLD, from: 0.5, drop: INK}); k.sweep(120, 914, 560, 6, nx + 0.3, {color: 'accent'}); }
      }
      return host(k, k.live('close.next') ? 'wave' : (k.live('close.send') ? 'point' : null));
    },
  },
};
