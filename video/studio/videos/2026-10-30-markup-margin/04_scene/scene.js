// Scene: Markup vs margin (Lesson 3, Run the Numbers, arcade). One function per top-level cue in 03_cues/cues.md.
// Numbers only from k.data (brief.md -> data.js). Every time comes from a cue start (k.S) or a spoken word (wordT), so a
// re-voiced take moves the picture with it.
// Worlds, one per section (Todd, Oct 28: "new cool graphic motion for each video"): hook and why = a job site drawn
// here (a site sign, two planks on sawhorses priced like the quote, a contractor's tape measure whose blade is the thing
// a percentage is measured on, a tower crane); math = the register rings the quote up, then the gauge reads the margin;
// double = the gauge again, the needle climbing to 50 only on a 100% markup; formula = the RPG tool belt, the formula is
// the item you equip; close = the register asks about your last quote.
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
  const line = (x0, y0, x1, y1, c, th = 1) => {
    x0 = Math.round(x0); y0 = Math.round(y0); x1 = Math.round(x1); y1 = Math.round(y1);
    const dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1; let e = dx + dy;
    for (let n = 0; n < 2000; n++) { P(x0, y0, th, th, c); if (x0 === x1 && y0 === y1) break; const e2 = 2 * e; if (e2 >= dy) { e += dy; x0 += sx; } if (e2 <= dx) { e += dx; y0 += sy; } }
  };
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
  const spr = (rows, pal, x, y, s = 1) => rows.forEach((r, j) => { for (let i = 0; i < r.length; i++) { const c = pal[r[i]]; if (c) P(x + i * s, y + j * s, s, s, c); } });
  const twinkle = (x, y, f, c = CREAM) => { const s = [0, 1, 2, 1][((f % 4) + 4) % 4]; DOT(x, y, c); for (let i = 1; i <= s; i++) { DOT(x - i, y, c); DOT(x + i, y, c); DOT(x, y - i, c); DOT(x, y + i, c); } };
  // a spinning coin, 8 x 8, four frames (face, turning, edge, turning), as the sets draw it
  const coin = (x, y, f) => {
    const ws = [4, 3, 1, 3][((f % 4) + 4) % 4];
    for (let j = 0; j < 8; j++) { const dy = j - 3.5, hw = Math.max(0, Math.round(ws * Math.sqrt(Math.max(0, 1 - (dy * dy) / 16)))); if (!hw) continue; P(x + 4 - hw, y + j, 2 * hw, 1, '#B07A47'); if (hw > 1) P(x + 4 - hw + 1, y + j, 2 * hw - 2, 1, j < 4 ? GOLD : ORANGE); }
    if (ws >= 3) { P(x + 4, y + 2, 1, 4, '#B07A47'); DOT(x + 3, y + 2, CREAM); }
  };
  // a rectangle outline that draws itself on, clockwise from the top left, over `frames` frames (a chalk ring in pixels)
  const ringOn = (x, y, w, h, t0, c, th = 2, frames = 9) => {
    const per = 2 * (w + h), n = Math.round(per * clamp(fr(t0) / frames)); if (n <= 0) return;
    const seg = [[x, y, 1, 0, w], [x + w, y, 0, 1, h], [x + w, y + h, -1, 0, w], [x, y + h, 0, -1, h]]; let left = n;
    seg.forEach(([sx, sy, ux, uy, len]) => { const m = Math.min(left, len); left -= m; if (m <= 0) return; P(ux < 0 ? sx - m : sx, uy < 0 ? sy - m : sy, ux ? m + (ux > 0 ? th : 0) : th, uy ? m + (uy > 0 ? th : 0) : th, c); });
  };
  return {P, DOT, dith, disc, line, bevel, win, fr, ease, tx, tw, clip, spr, twinkle, coin, ringOn, F, T};
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
// a dark game plate for a set's words (low-res), the same one lesson 9 sets under its sets
const plate = (d, x, y, w, h) => d.win(x, y, w, h, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
// an ordered-dither wipe on 4-pixel blocks inside a section: closes over the 5 frames before t0, clears over the 7 after
const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];
const wipe = (k, t0) => {
  const f = Math.floor((k.T - t0) * 30 + 0.005); if (f < -5 || f >= 7) return;
  const th = f < 0 ? Math.round((f + 6) / 6 * 16) : Math.round((1 - (f + 1) / 8) * 16); k.ctx.fillStyle = INK;
  for (let y = 0; y < 1920; y += 12) for (let x = 0; x < 1080; x += 12) if (BAYER[((y / 12) % 4) * 4 + ((x / 12) % 4)] < th) k.ctx.fillRect(x, y, 12, 12);
};
// a rubber stamp in a dark box with a coloured rim, landed with the kit's hit-stop (k.stampIn); sizes on whole pixels
const stampBox = (k, s, cx, y, t0, o = {}) => {
  const size = o.size || 66, c = o.color || GOLD, w = Math.round((k.measure(s, {size}) + 54) / 6) * 6, h = size + 36, x = Math.round((cx - w / 2) / 3) * 3;
  k.stampIn(t0, () => {
    k.shape(k.rectPts(x + 6, y + 6, w, h, 0), {fill: INK, line: false}); k.shape(k.rectPts(x, y, w, h, 0), {fill: '#1B1420', line: false});
    k.shape(k.rectPts(x + 6, y + 6, w - 12, 6, 0), {fill: c, line: false}); k.shape(k.rectPts(x + 6, y + h - 12, w - 12, 6, 0), {fill: c, line: false});
    k.shape(k.rectPts(x + 6, y + 6, 6, h - 12, 0), {fill: c, line: false}); k.shape(k.rectPts(x + w - 12, y + 6, 6, h - 12, 0), {fill: c, line: false});
    k.text(s, x + w / 2, y + 18, {size, color: c, align: 'center'});
  }, {at: [x + w / 2, y + h], freeze: o.freeze});
};
// a thin strike through a line of text, drawn on 0.4 s after the line was read
const strike = (k, x, y, w, t0, c = RED) => { const q = eo((k.T - t0) / 0.18); if (q > 0) k.shape(k.rectPts(x, y, Math.round(w * q / 3) * 3, 6, 0), {fill: c, line: false}); };

// ================================================================================================================
// the job site (hook, why): our own set piece. A tower crane swings a beam over a site sign (the scene's board, frame
// y 258 to 630); under it two planks lie on sawhorses, priced like the quote (the cost plank, the markup plank painted
// orange). A contractor's tape measure sits at the left: its blade whips out to what a percentage is measured on, its
// marks labelled in dollars. Coins hop onto the planks (what the customer pays), tags hang off the markup plank.
const PXD = 0.19, TX0 = 28, XC = (usd) => Math.round(TX0 + usd * PXD);   // plank pixels per dollar: $1,500 = 285 px
const site = (k, o) => {
  const d = px(k), {P, DOT, dith, disc, line, bevel, fr, tx, T, F} = d, n = k.data.numbers;
  // the sky and the crane
  P(0, 0, 360, 80, '#5B8FB9'); P(0, 80, 360, 80, '#87CEEB'); P(0, 160, 360, 70, '#BDE6F5'); dith(0, 80, 360, 2, '#5B8FB9', 1); dith(0, 160, 360, 2, '#87CEEB', 1);
  const cloud = (x, y, w, seed) => { const m = Math.max(2, Math.round(w / 9)); for (let i = 0; i < m; i++) { const r = 3 + Math.round(hash(seed + i * 1.71) * 3) + (i > 0 && i < m - 1 ? 2 : 0); disc(x + Math.round((i + 0.5) * w / m), y - r + 6, r, CREAM); } P(x + 2, y + 3, w - 4, 3, CREAM); P(x + 3, y + 5, w - 6, 1, SAND); };
  [[30, 24, 34, 1], [170, 40, 26, 5], [260, 18, 30, 9]].forEach(([x, y, w, s]) => cloud(((x - Math.floor(F / 12)) % 420 + 420) % 420 - 40, y, w, s));
  // the mast (a lattice), the jib along the top, the cab, the counterweight, a trolley with a swinging beam
  for (let y = 26; y < 232; y += 8) { P(304, y, 2, 8, '#3B82C4'); P(316, y, 2, 8, '#3B82C4'); line(306, y, 315, y + 7, '#5B8FB9'); }
  P(110, 26, 250, 3, '#3B82C4'); P(110, 32, 250, 1, '#3B82C4'); for (let x = 112; x < 360; x += 8) line(x, 29, x + 4, 32, '#5B8FB9');
  P(296, 33, 26, 14, '#F2A541'); P(296, 33, 26, 1, GOLD); P(300, 36, 8, 5, '#BDE6F5'); P(330, 30, 24, 10, '#4A4E5A');
  const sway = [0, 1, 1, 1, 0, -1, -1, -1][Math.floor(F / 9) % 8], bx = 176 + sway;
  P(172, 28, 10, 5, '#253048'); line(177, 33, bx, 62, '#253048'); P(bx - 2, 62, 5, 3, '#4A4E5A');
  P(bx - 22, 66, 44, 4, '#E2633B'); P(bx - 22, 66, 44, 1, GOLD); P(bx - 22, 70, 44, 2, '#7A3442');
  // the back fence and the ground
  P(0, 204, 360, 26, '#9AA0AD'); for (let x = 0; x < 360; x += 6) { line(x, 204, x + 6, 216, '#6B7080'); line(x + 6, 216, x, 228, '#6B7080'); } P(0, 204, 360, 1, '#6B7080');
  P(0, 228, 360, 189, '#B07A47'); P(0, 228, 360, 2, '#8C5A33');
  for (let i = 0; i < 90; i++) DOT(Math.floor(hash(i * 2.3) * 360), 232 + Math.floor(hash(i * 5.1) * 180), i % 3 ? '#8C5A33' : '#D9A066');
  // a cone and a brick stack (right), a cement bag (left), clear of the host and the dialog box
  const cone = (x, y) => { P(x + 4, y, 4, 4, '#E2633B'); P(x + 3, y + 4, 6, 4, CREAM); P(x + 2, y + 8, 8, 5, '#E2633B'); P(x, y + 13, 12, 3, '#7A3442'); };
  cone(332, 300); cone(4, 300);
  for (let r = 0; r < 3; r++) for (let c = 0; c < 3 - (r === 2 ? 1 : 0); c++) { const xx = 290 + c * 12 + (r % 2) * 6, yy = 310 - r * 6; P(xx, yy, 11, 5, '#7A3442'); P(xx, yy, 11, 1, '#E2633B'); }
  // the floor: packed gravel
  P(0, 417, 360, 223, '#8C5A33'); for (let i = 0; i < 160; i++) DOT(Math.floor(hash(i * 7.7) * 360), 420 + Math.floor(hash(i * 3.9) * 216), i % 2 ? '#6B4226' : '#B07A47');
  // a poured slab with its form boards, a lumber stack and a wheelbarrow under the Reel's caption band
  P(0, 417, 360, 30, '#9AA0AD'); P(0, 417, 360, 2, '#C9CCD3'); P(0, 445, 360, 3, '#6B4226'); for (let x = 30; x < 360; x += 60) P(x, 419, 1, 26, '#6B7080');
  for (let r = 0; r < 4; r++) { const y = 492 - r * 7, w = 96 - r * 10; P(18 + r * 5, y, w, 7, INK); P(19 + r * 5, y + 1, w - 2, 5, '#D9A066'); P(19 + r * 5, y + 1, w - 2, 1, '#F7D79B'); DOT(19 + r * 5 + 3, y + 3, '#B07A47'); }
  P(236, 470, 64, 20, INK); P(238, 472, 60, 16, '#3B82C4'); P(238, 472, 60, 2, '#87CEEB'); P(244, 466, 48, 6, '#9AA0AD'); line(298, 478, 330, 470, '#6B4226', 2); line(240, 488, 232, 500, '#6B4226', 2);
  disc(262, 500, 8, INK); disc(262, 500, 6, '#4A4E5A'); disc(262, 500, 2, GREY); P(262 + [0, 4, 0, -4][Math.floor(F / 20) % 4] - 0, 499, 1, 1, GREY);
  // the site sign: two posts, a painted board with bolts (the scene's words go on it)
  P(56, 200, 6, 32, '#6B4226'); P(298, 200, 6, 32, '#6B4226'); P(56, 200, 2, 32, '#8C5A33'); P(298, 200, 2, 32, '#8C5A33');
  d.win(14, 82, 332, 130, {base: '#253048', hi: '#3B82C4', lo: '#1B1420', rule: '#3B82C4'});
  [[18, 86], [338, 86], [18, 204], [338, 204]].forEach(([a, b]) => { DOT(a, b, GREY); DOT(a + 1, b + 1, '#4A4E5A'); });
  // the sawhorses
  [[44, 30], [232, 30]].forEach(([x, w]) => { P(x - 4, 250, w + 8, 5, '#8C5A33'); P(x - 4, 250, w + 8, 1, '#D9A066'); line(x, 255, x - 6, 304, '#6B4226', 3); line(x + w, 255, x + w + 6, 304, '#6B4226', 3); P(x - 3, 280, w + 6, 2, '#6B4226'); });
  // the planks: cost (raw wood), markup (painted orange); each carries its price
  const plank = (x0, x1, base, hi, lo, label, lc) => {
    P(x0, 232, x1 - x0, 18, INK); P(x0 + 1, 233, x1 - x0 - 2, 16, base); P(x0 + 1, 233, x1 - x0 - 2, 1, hi); P(x0 + 1, 247, x1 - x0 - 2, 2, lo);
    for (let x = x0 + 9; x < x1 - 4; x += 23) P(x, 237 + (x % 3), 7, 1, lo);
    tx(label, (x0 + x1) / 2, 235, {color: lc, align: 'center'});
  };
  plank(XC(0), XC(n.cost.value), '#D9A066', '#F7D79B', '#B07A47', `COST ${n.cost.shown}`, '#4A2E1B');
  plank(XC(n.cost.value), XC(n.price.value), '#F2A541', GOLD, '#B07A47', o.markupLabel || `+${n.markupUsd.shown}`, '#4A2E1B');
  // the glow: the markup plank outlined in gold, blinking twice a second for its first second
  if (o.glowAt != null && T >= o.glowAt && (fr(o.glowAt) >= 30 || Math.floor(fr(o.glowAt) / 8) % 2 === 0)) { const x0 = XC(n.cost.value) - 1, x1 = XC(n.price.value) + 1; P(x0, 230, x1 - x0, 2, GOLD); P(x0, 250, x1 - x0, 2, GOLD); P(x0, 230, 2, 22, GOLD); P(x1 - 2, 230, 2, 22, GOLD); }
  // the tape measure: the blade length eases (with a little whip) from one mark to the next
  const marks = (o.tape || []).filter((m) => T >= m.at), cur = marks[marks.length - 1], prev = marks[marks.length - 2];
  let L = 2;
  if (cur) { const from = prev ? XC(prev.usd) - TX0 : 2, to = XC(cur.usd) - TX0, f = fr(cur.at), q = clamp(f / 8);
    const back = q >= 1 ? 1 : 1 + 2.2 * Math.pow(q - 1, 3) + 1.2 * Math.pow(q - 1, 2); L = Math.round(from + (to - from) * back); }
  if (!cur && o.twitch != null && fr(o.twitch) >= 0 && fr(o.twitch) < 12) L = 2 + [2, 5, 7, 8, 8, 7, 6, 5, 4, 3, 2, 0][fr(o.twitch)];
  P(TX0, 226, L, 4, INK); P(TX0, 226, L, 3, GOLD); P(TX0, 226, L, 1, '#FFF2B8');
  for (let usd = 100; XC(usd) - TX0 <= L; usd += 100) P(XC(usd), 226, 1, 2, INK);
  [n.markupUsd, n.cost, n.price].forEach((m) => { const x = XC(m.value); if (x - TX0 > L) return; P(x, 226, 1, 4, INK); tx(m.shown, x - 1, 213, {color: CREAM, align: 'right', drop: INK}); });
  P(TX0 + L - 1, 224, 2, 8, INK); P(TX0 + L, 225, 1, 6, GREY);   // the hook on the end
  // the case: yellow, a black grip, the belt clip, the lock button
  bevel(6, 218, 24, 22, GOLD, '#FFF2B8', '#B07A47', INK); P(9, 230, 18, 7, '#2B2033'); P(9, 230, 18, 1, '#4A4E5A'); disc(18, 225, 3, '#B07A47'); DOT(17, 224, CREAM); P(28, 222, 3, 4, '#E2633B');
  // the bracket under a span: end ticks and a gold line, built from the left over 6 frames
  if (o.bracket && T >= o.bracket.at) { const x0 = XC(o.bracket.from), x1 = XC(o.bracket.to), w = Math.round((x1 - x0) * clamp(fr(o.bracket.at) / 6)); P(x0, 254, 2, 7, GOLD); P(x0, 257, w, 2, GOLD); if (w >= x1 - x0) P(x1 - 2, 254, 2, 7, GOLD); }
  // coins hop in from the right and land on the planks with a twinkle (what the customer pays)
  if (o.coinsAt != null) for (let i = 0; i < 5; i++) { const t = o.coinsAt + i * 0.13, dt = T - t; if (dt < 0) continue; const land = XC(n.price.value * (0.15 + i * 0.17)), q = clamp(dt / 0.45);
    if (q < 1) d.coin(Math.round(land - 4 + (1 - q) * 40), Math.round(262 - 10 * q * (1 - q) * 4), Math.floor(F / 2) + i); else { const g = Math.floor((dt - 0.45) * 15); if (g < 8) d.twinkle(land, 266, g, GOLD); } }
  // tags hang off the markup plank on a string and swing to rest
  (o.tags || []).forEach((tg) => {
    if (T < tg.at) return; const f = fr(tg.at), sw = [0, -4, -3, -1, 2, 3, 2, 0, -1, -1, 0, 1, 0][Math.min(12, Math.floor(f / 2))], drop = f < 4 ? [-10, -5, -2, 1][f] : 0;
    const x = tg.x + sw, y = tg.y + drop, w = Math.round(d.tw(tg.text)) + 10;
    line(tg.x, 250, x, y, CREAM);
    P(x - w / 2 - 1, y - 1, w + 2, 18, INK); P(x - w / 2, y, w, 16, tg.c || '#7A3442'); P(x - w / 2, y, w, 1, '#F09A9A'); DOT(x, y + 2, INK);
    tx(tg.text, x, y + 2, {color: CREAM, align: 'center', lint: f >= 26});
  });
};

// ================================================================================================================
// the dial (math, double): the library gauge, with the needle driven here so it can swing from one margin to another
// (the set's needle only rises from zero). The set draws at rest; its resting needle is painted out and the 0 mark put
// back, then our needle goes on in the set's own style. The readout shows `shown`.
const GX = 180, GY = 214, GR = 100, GA0 = Math.PI * 0.75, GSW = Math.PI * 1.5;
const dial = (k, label, v, shown, o = {}) => {
  const d = px(k), dec = Number.isInteger(shown) ? 0 : 1;
  k.sets.gauge({value: 100, max: 100, at: 1e9, from: shown, dec, label, zones: o.zones});
  const ex = Math.round(Math.cos(GA0) * (GR - 16)), ey = Math.round(Math.sin(GA0) * (GR - 16));
  d.line(GX + 1, GY + 1, GX + 1 + ex, GY + 1 + ey, INK, 2); d.line(GX, GY, GX + ex, GY + ey, INK, 2);
  d.line(GX + Math.cos(GA0) * (GR - 20), GY + Math.sin(GA0) * (GR - 20), GX + Math.cos(GA0) * (GR - 10), GY + Math.sin(GA0) * (GR - 10), CREAM, 2);
  d.tx('0', GX + Math.cos(GA0) * (GR - 32), GY + Math.sin(GA0) * (GR - 32) - 10, {color: '#C9CCD3', align: 'center', lint: false});
  // the mark at 50: a gold notch on the bezel; a dotted ghost needle when o.ghost (what people picture, or the target)
  if (o.notchAt != null && k.T >= o.notchAt) { const f = d.fr(o.notchAt), lift = f < 4 ? [-6, -3, -1, 1][f] : 0; for (let j = 0; j < 6; j++) d.P(GX - 5 + j, 103 + j + lift, 11 - 2 * j, 1, j ? ORANGE : GOLD); d.P(GX - 6, 102 + lift, 13, 1, INK); }
  if (o.ghostAt != null && k.T >= o.ghostAt) { const blink = d.fr(o.ghostAt) < 30 && Math.floor(d.fr(o.ghostAt) / 8) % 2; if (!blink) for (let r = 14; r < GR - 18; r += 4) d.P(GX - 1, GY - r - 1, 2, 2, o.ghostC || GOLD); }
  const na = Math.round((GA0 + GSW * clamp(v / 100, -0.02, 1.02)) * 180 / Math.PI) * Math.PI / 180, R1 = GR - 16, R2 = GR - 30;
  d.line(GX + 1, GY + 1, GX + 1 + Math.round(Math.cos(na) * R1), GY + 1 + Math.round(Math.sin(na) * R1), INK, 2);
  d.line(GX, GY, GX + Math.round(Math.cos(na) * R1), GY + Math.round(Math.sin(na) * R1), RED, 2);
  d.line(GX, GY, GX + Math.round(Math.cos(na) * R2), GY + Math.round(Math.sin(na) * R2), ORANGE, 1);
  d.disc(GX, GY, 9, INK); d.disc(GX, GY, 8, '#4A4E5A'); d.disc(GX - 1, GY - 1, 6, GREY); d.DOT(GX - 3, GY - 3, CREAM);
};
// the needle's value: rests at v0, swings to v1 from t (overshoot, then settles), like the set's own needle
const swing = (T, t, v0, v1, dur = 1.0) => { if (T < t) return v0; const dd = T - t, r = clamp(dd / (dur * 0.55)), w = dd > dur * 0.55 ? (v1 - v0) * 0.12 * Math.exp(-5 * (dd - dur * 0.55)) * Math.sin((dd - dur * 0.55) * 16) : 0; return v0 + (v1 - v0) * eo(r) + w; };

// the register's display, painted over with our own words (the close asks a question, not a total)
const DPX = 222, DPY = 114;
const displayText = (k, s, c = TEAL) => { const d = px(k); d.P(DPX + 7, DPY + 19, 92, 38, '#24453A'); for (let y = DPY + 20; y < DPY + 57; y += 3) d.P(DPX + 7, y, 92, 1, '#1A332B'); d.tx(s, DPX + 53, DPY + 27, {size: 66, color: c, align: 'center'}); };

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 3',
  transitions: {math: 'door', why: 'dissolve', double: 'blinds', formula: 'levelselect', close: 'gameover'},
  trauma: {'double.x2': 0.8},
  sections: {
    // ---- hook: the job site, settled on frame 0 (the claim on the sign, the priced planks, the source); the tape whips
    // out to the whole price on "Nope" and the markup plank is a third of it
    hook: (k, T) => {
      const n = k.data.numbers, d = px(k);
      const tQ = wordT(k, 'hook', /^margin/i, 3), tNope = k.S('hook.nope'), tThird = wordT(k, 'hook.nope', /^third/i, 0.9), fix = k.S('hook.fix');
      site(k, {markupLabel: `+${n.markupPct.shown}`, twitch: 0.6,
        tape: [{at: tNope, usd: n.price.value}], glowAt: tNope + 0.3, bracket: {at: tNope + 0.3, from: n.cost.value, to: n.price.value}});
      // the claim on the sign, settled from frame 0
      const l3 = `${n.doubleMarginPct.shown} margin`, w3 = k.measure(l3, {size: 132}), x3 = 486 - w3 / 2;
      k.slam(`${n.markupPct.shown} markup`, 486, 268, -1, {size: 132, color: CREAM, align: 'center', drop: INK});
      k.slam('is NOT', 486, 412, -1, {size: 66, color: 'accent', align: 'center', drop: INK, glintAt: 0.5});
      k.slam(l3, 486, 486, -1, {size: 132, color: CREAM, align: 'center', drop: INK, glintAt: 0.9});
      if (T >= tQ) k.slam('?', x3 + w3 + 12, 486, tQ, {size: 132, color: GOLD, from: 0.8, drop: INK});
      strike(k, x3 - 6, 548, k.measure(n.doubleMarginPct.shown, {size: 132}) + 12, tNope + 0.4);
      k.burst(486, 330, 0.4, {n: 18, r: 300, colors: ['accent', 'paper']});
      // the ground: the chip and the source on a plate from frame 0; the stamp lands on the third; the two chips
      plate(d, 14, 256, 200, 44);
      k.chip('Run the numbers', 66, 786, {size: 30});
      k.text('Example math. Sources: JLC, Xero', 66, 856, {size: 30, color: SAND});
      if (T >= tThird) stampBox(k, 'A THIRD', 798, 786, tThird);
      if (T >= fix) {
        const c1 = d.ease(fix, 8, 120), c2 = d.ease(fix + 0.2, 8, 120);
        d.clip(0, 296, 360, 30, () => { k.chip('1  The math', 240, 912 + c1 * 3, {size: 30, fill: 'accent', color: INK}); k.chip('2  The fix', 560, 912 + c2 * 3, {size: 30, fill: 'accent', color: INK}); });
        k.burst(400, 925, fix + 0.1, {n: 12, r: 160});
      }
      if (T < 1.0) return {host: false, speech: false};
      if (T < tNope) return {host: false};
      return host(k, T < fix ? 'shrug' : null);
    },

    // ---- math: the register rings the quote up (cost, the markup, the price); the display splits the price in three;
    // then a dither wipe to the gauge, whose needle reads the margin on "thirty-three"
    math: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('math');
      const tCost = wordT(k, 'math.cost', /^thousand/i), tFive = wordT(k, 'math.markup', /^five/i, 1.5), tPrice = wordT(k, 'math.price', /^fifteen/i, 0.9);
      const tThird = k.S('math.third'), tMargin = k.S('math.margin'), t33 = wordT(k, 'math.margin', /^thirty/i, 1.4), tNot = k.S('math.not'), t50 = wordT(k, 'math.not', /^fifty/i, 0.8);
      if (T < tMargin) {
        k.sets.register({items: [{label: 'COST', amount: n.cost.value, at: tCost}, {label: `MARKUP ${n.markupPct.shown}`, amount: n.markupUsd.value, at: tFive}],
          totalAt: tPrice, totalLabel: 'PRICE', displayLabel: 'QUOTE', openAt: tPrice + 0.35});
        // the header and the beat's line on the wall above the first shelf
        k.slam('Cost + markup = price', 72, 270, t0 + 0.15, {size: 39, color: GOLD, from: 0.4, drop: INK});
        const say = T >= tThird ? [`${n.markupUsd.shown} = 1/3 of the price`, tThird + 0.15, 'accent'] : T >= tPrice ? [`The quote: ${n.price.shown}`, tPrice, CREAM]
          : T >= tFive ? [`${n.markupPct.shown} markup: +${n.markupUsd.shown}`, tFive, 'accent'] : T >= tCost ? [`Your cost: ${n.cost.shown}`, tCost, CREAM] : null;
        if (say) k.slam(say[0], 72, 318, say[1], {size: 66, color: say[2], from: 0.5, drop: INK});
        // the display splits the price into thirds: two cost thirds, the markup third in orange, a cursor over it
        if (T >= tThird) {
          const f = d.fr(tThird), x0 = DPX + 9, w = 28;
          d.P(DPX + 7, DPY + 19, 92, 38, '#24453A');
          for (let i = 0; i < n.thirds.value; i++) { if (f < 3 * i) continue; const last = i === n.thirds.value - 1; d.P(x0 + i * (w + 2), DPY + 30, w, 18, INK); d.P(x0 + i * (w + 2) + 1, DPY + 31, w - 2, 16, last ? ORANGE : TEAL); d.P(x0 + i * (w + 2) + 1, DPY + 31, w - 2, 1, last ? GOLD : '#BDE6F5'); }
          if (f >= 6) { d.tx('1/3', x0 + 2 * (w + 2) + w / 2, DPY + 20, {color: GOLD, align: 'center', lint: false}); /* over the painted-out total, which the set still reports */ if (Math.floor(f / 15) % 2 === 0) d.P(x0 + 2 * (w + 2) + 4, DPY + 50, w - 8, 2, GOLD); }
        }
        wipe(k, tMargin);
        return host(k, k.live('math.markup') || k.live('math.third') ? 'point' : null);
      }
      // the gauge: the margin, $500 over the $1,500 price; the needle swings to a third; the fifty people picture
      const tRise = Math.min(t33 - 0.5, tMargin + 0.3), v = swing(T, tRise, 0, n.marginPct.value, (t33 - tRise) / 0.55), shown = T >= t33 + 0.6 ? n.marginPct.value : Math.max(0, Math.min(n.marginPct.value, Math.round(v * 10) / 10));
      dial(k, 'YOUR MARGIN', v, Math.max(0, shown), {notchAt: t50, ghostAt: t50, ghostC: GOLD});
      if (T >= t33) k.burst(540, 740, t33 + 0.05, {n: 18, r: 240});
      plate(d, 14, 268, 332, 56);
      k.slam(`${n.markupUsd.shown} / ${n.price.shown} =`, 72, 822, tMargin + 0.1, {size: 39, color: CREAM, from: 0.4});
      if (T >= t33) k.slam(`${n.marginPct.shown} margin`, 72 + k.measure(`${n.markupUsd.shown} / ${n.price.shown} =`, {size: 39}) + 24, 808, t33 + 0.5, {size: 66, color: 'accent', from: 0.5, drop: INK});
      if (T >= tNot) {
        const pre = 'Not the ', s50 = n.doubleMarginPct.shown;
        k.slam(`${pre}${s50} you pictured.`, 72, 900, tNot, {size: 39, color: GOLD, from: 0.4});
        strike(k, 72 + k.measure(pre, {size: 39}) - 3, 915, k.measure(s50, {size: 39}) + 6, Math.max(tNot, t50) + 0.4);
      }
      wipe(k, tMargin);
      return host(k, k.live('math.not') ? 'shrug' : null);
    },

    // ---- why: back on the job site. The tape measures the cost, then the whole price; the same $500 plank is half of
    // one and a third of the other. Coins land (the price is what the customer pays); tags hang off the markup plank
    why: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('why');
      const tMk = k.S('why.markup'), tMg = k.S('why.margin'), tPay = wordT(k, 'why.pays', /^pays/i, 1.6), tLeft = k.S('why.left'), tCover = k.S('why.cover');
      const tOver = wordT(k, 'why.cover', /^overhead/i, 1.4), tYou = wordT(k, 'why.pay', /^pay$/i, 0.3);
      site(k, {tape: [{at: tMk, usd: n.cost.value}, {at: tMg, usd: n.price.value}], glowAt: tMk, bracket: {at: tPay, from: 0, to: n.price.value}, coinsAt: tPay,
        tags: [{text: 'OVERHEAD', at: tOver, x: 240, y: 262}, {text: 'YOUR PAY', at: tYou, x: 284, y: 284, c: '#2F6F67'}]});
      k.slam('Why the gap?', 72, 270, t0 + 0.15, {size: 66, color: GOLD, from: 0.5, drop: INK});
      // a row: the fraction big, its result at the right edge, and what it is measured on (the word swept) under it
      const row = (y, name, top, base, sub, on, res, t, tOn) => {
        if (T < t) return;
        k.slam(`${name}: ${top} / ${base}`, 72, y, t, {size: 66, color: CREAM, from: 0.5, drop: INK});
        k.slam(res, 930, y, t + 0.45, {size: 66, color: 'accent', align: 'right', from: 0.5, drop: INK});
        k.text(sub + on, 72, y + 76, {size: 30, color: SAND});
        k.sweep(72 + k.measure(sub, {size: 30}) - 3, y + 106, k.measure(on, {size: 30}) + 6, 6, tOn, {color: 'accent2'});
      };
      row(342, 'Markup', n.markupUsd.shown, n.cost.shown, 'measured on your ', 'cost', `= ${n.markupPct.shown}`, tMk, wordT(k, 'why.markup', /^cost/i, 1.2));
      row(462, 'Margin', n.markupUsd.shown, n.price.shown, 'measured on the ', 'price', `= ${n.marginPct.shown}`, tMg, wordT(k, 'why.margin', /^price/i, 1.3));
      if (T >= k.S('why.pays')) k.slam('Price = what the customer pays you', 72, 580, wordT(k, 'why.pays', /^money/i, 0.4), {size: 30, color: GOLD, from: 0.4});
      if (T >= tLeft && T < tCover) stampBox(k, 'NOT TAKE-HOME PAY', 600, 786, wordT(k, 'why.left', /^take/i, 0.6), {color: RED});
      if (T >= tCover) { plate(d, 14, 260, 172, 40); k.slam('Margin has to cover:', 66, 804, tCover, {size: 39, color: CREAM, from: 0.4}); }
      return host(k, T >= tLeft && T < tCover ? 'shrug' : (k.live('why.markup') || k.live('why.margin') ? 'point' : null));
    },

    // ---- double: the gauge again. The needle sits at a third; the gold notch is the target; doubling the cost (a
    // second cost-sized block in the plate) is a 100% markup, and only then does the needle climb to 50
    double: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('double');
      const tDbl = wordT(k, 'double.x2', /^double/i, 0.6), tHun = wordT(k, 'double.markup', /^hundred/i, 0.5);
      const tCost = wordT(k, 'double.markup', /^thousand/i, 2.1), tTwo = wordT(k, 'double.quote', /^thousand/i, 0.2);
      const v = swing(T, tHun, n.marginPct.value, n.doubleMarginPct.value, 1.1);
      const shown = T < tHun ? n.marginPct.value : (T >= tHun + 1.1 ? n.doubleMarginPct.value : clamp(Math.round(v * 10) / 10, n.marginPct.value, n.doubleMarginPct.value));
      dial(k, `WANT A ${n.doubleMarginPct.shown} MARGIN?`, v, shown, {notchAt: t0 + 0.4, ghostAt: t0 + 0.4, ghostC: ORANGE});
      if (T >= tHun + 1.1) { k.burst(540, 330, tHun + 1.1, {n: 22, r: 260}); }
      // the plate: two blocks, the cost and the markup; the markup block grows to match the cost on "double"
      plate(d, 14, 268, 332, 56);
      const bx = 22, bw = 96, by = 275, gw = T < tDbl ? 0 : Math.round(bw * eo(d.fr(tDbl) / 8));
      d.P(bx - 1, by - 1, bw + 2, 20, INK); d.P(bx, by, bw, 18, TEAL); d.P(bx, by, bw, 1, '#BDE6F5'); d.P(bx, by + 16, bw, 2, '#2F6F67');
      d.tx(`COST ${n.cost.shown}`, bx + bw / 2, by + 3, {color: INK, align: 'center'});
      if (gw > 0) { d.P(bx + bw + 1, by - 1, gw + 1, 20, INK); d.P(bx + bw + 2, by, gw - 1, 18, ORANGE); d.P(bx + bw + 2, by, gw - 1, 1, GOLD); d.P(bx + bw + 2, by + 16, gw - 1, 2, '#B07A47'); }
      if (gw === bw && T >= tHun) d.tx(`+${n.doubleMarkupPct.shown}`, bx + bw + 2 + bw / 2, by + 3, {color: INK, align: 'center'});
      if (T >= tTwo) k.slam(`= ${n.doublePrice.shown} quote`, 930, 822, tTwo, {size: 39, color: GOLD, align: 'right', from: 0.5});
      if (T >= tDbl && T < tHun) stampBox(k, 'DOUBLE YOUR COST', 560, 882, tDbl, {color: RED, freeze: 5});
      else if (T < tDbl) k.slam(`Now: ${n.markupPct.shown} markup = ${n.marginPct.shown} margin`, 72, 900, t0 + 0.2, {size: 39, color: SAND, from: 0.4});
      else {
        k.slam(`${n.doubleMarkupPct.shown} markup = ${n.doubleMarginPct.shown} margin`, 72, 900, tHun, {size: 39, color: CREAM, from: 0.4});
        if (T >= tCost) k.sweep(72, 942, k.measure(`${n.doubleMarkupPct.shown} markup`, {size: 39}), 6, tHun + 0.4, {color: 'accent'});
      }
      return host(k, k.live('double.x2') ? 'point' : (k.live('double.quote') ? 'point' : null));
    },

    // ---- formula: the tool belt. The cursor runs over the tools; the part people skip is a new item; equip it and its
    // card fills the screen (Price = Cost / (1 - margin)); then its stats fill as the 40% example is said
    formula: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('formula'), tShot = k.S('formula.shot'), tEq = k.S('formula.eq');
      const tMinus = wordT(k, 'formula.minus', /^minus/i, 0.4), tForty = k.S('formula.forty'), t40 = wordT(k, 'formula.forty', /^forty/i, 0.1);
      const tDiv = k.S('formula.div'), tSix = wordT(k, 'formula.div', /^point/i, 1.2), tRes = wordT(k, 'formula.result', /^sixteen/i, 1.4), tChk = k.S('formula.check');
      const tOff = Math.max(tForty, tEq + 3.6);   // the card holds big at least 3.6 s from "Price equals"
      const items = [{icon: 'wrench', name: 'WRENCH'}, {icon: 'hammer', name: 'HAMMER'}, {icon: 'phone', name: 'PHONE'},
        T >= tShot ? {icon: 'clip', name: 'FORMULA', stats: []} : null, {icon: 'clock', name: 'CLOCK'}, {icon: 'mail', name: 'MAIL'}, {icon: 'coin', name: 'COIN'}, {icon: 'star', name: 'STAR'}];
      k.sets.inventory({title: 'TOOL BELT', items,
        select: [{slot: 0, at: t0 + 0.15}, {slot: 1, at: wordT(k, 'formula', /^part/i, 0.4)}, {slot: 2, at: wordT(k, 'formula', /^skip/i, 0.8)}, {slot: 3, at: tShot}]});
      // the new item: twinkles round its slot as it lands
      if (T >= tShot && d.fr(tShot) < 16) for (let i = 0; i < 4; i++) d.twinkle([150, 184, 150, 184][i], [110, 110, 142, 142][i], d.fr(tShot) - i * 2, GOLD);
      // the stats, filled on their words (drawn here, in the set's own style)
      const stat = (j, label, frac, text, at) => {
        if (T < at) return; const y = 152 + j * 36, dx = 194, p = clamp((T - at) / 0.4), fw = Math.round(120 * clamp(frac) * eo(p));
        d.tx(label, dx, y, {color: CREAM}); d.P(dx, y + 17, 124, 8, INK); d.P(dx + 1, y + 18, 122, 6, '#3D2E45'); d.P(dx + 1, y + 18, fw, 6, TEAL); d.P(dx + 1, y + 18, fw, 1, '#BDE6F5');
        for (let x = dx + 13; x < dx + 122; x += 12) d.P(x, y + 18, 1, 6, INK);
        d.tx(text, dx + 121, y, {color: TEAL, align: 'right'});
      };
      stat(0, 'MARGIN', n.targetMarginPct.value / 100, n.targetMarginPct.shown, t40);
      stat(1, 'DIVIDE BY', n.divisor.value, n.divisor.shown, tSix);
      stat(2, 'PRICE', n.targetPrice.value / n.doublePrice.value, cnt(k, n.targetPrice, tRes, {dec: 2, comma: true, prefix: '$'}), tRes);
      // the formula, small, in the belt's own corner once the card has gone
      if (T >= tOff + 0.25) { k.slam('Price = cost', 84, 612, tOff + 0.25, {size: 39, color: GOLD, from: 0.4}); k.slam('/ (1 - margin)', 84, 660, tOff + 0.35, {size: 39, color: GOLD, from: 0.4}); }
      // the plate under the belt: the part people skip, then the worked example and its check
      plate(d, 14, 274, 332, 50);
      if (T < tShot) { k.chip('The part people skip', 66, 844, {size: 30}); k.slam('NEW ITEM!', 930, 852, wordT(k, 'formula', /^skip/i, 0.8), {size: 39, color: GOLD, align: 'right', from: 0.5}); }
      else if (T >= tOff) {
        if (T < tDiv) k.slam(`Want ${n.targetMarginPct.shown} margin?`, 72, 834, tForty, {size: 66, color: CREAM, from: 0.5, drop: INK});
        else {
          const lhs = `${n.cost.shown} / ${n.divisor.shown} =`;
          k.slam(lhs, 72, 834, tDiv, {size: 66, color: CREAM, from: 0.5, drop: INK});
          if (T >= tRes) { k.slam(cnt(k, n.targetPrice, tRes, {dec: 2, comma: true, prefix: '$'}), 72 + k.measure(lhs, {size: 66}) + 24, 834, tRes, {size: 66, color: 'accent', from: 0.5, drop: INK}); k.burst(760, 870, tRes + 0.7, {n: 18, r: 220}); }
          if (T >= tChk) k.slam(`Check: ${n.targetMarginUsd.shown} / ${n.targetPrice.shown} = ${n.targetCheck.shown}`, 72, 912, tChk, {size: 30, color: SAND, from: 0.4});
        }
      }
      // the item card: rises from behind the dash on "Screenshot this", holds the formula big, then sinks away
      if (T >= tShot && T < tOff + 0.5) {
        const up = d.ease(tShot, 8, 180), down = T >= tOff ? Math.round(190 * eo(d.fr(tOff) / 10)) : 0, Y = 148 + up + down, settled = up === 0 && down === 0;
        d.clip(0, 0, 360, 326, () => {
          d.win(14, Y, 332, 176, {base: '#1B1420', hi: '#7A3442', lo: INK, rule: '#F2A541'});
          k.ctx.save(); k.ctx.translate(0, (Y - 148) * 3);
          k.chip('Screenshot this', 66, 462, {size: 30, fill: 'accent', color: INK});
          const te = Math.min(tEq, tShot + 0.3), a = (t) => (T >= t ? 1 : 0), L = {lint: settled};
          if (a(te)) k.text('Price =', 60, 616, Object.assign({size: 132, color: CREAM, drop: INK}, L));
          if (a(te + 0.2)) k.text('Cost', 684, 530, Object.assign({size: 132, color: CREAM, align: 'center', drop: INK}, L));
          k.sweep(426, 676, 516, 12, te + 0.35, {color: GOLD});
          if (a(te + 0.5)) k.text('1 - margin', 684, 700, Object.assign({size: 132, color: 'accent', align: 'center', drop: INK}, L));
          if (a(te + 0.5)) k.text('Price = Cost / (1 - margin)', 66, 880, Object.assign({size: 30, color: SAND}, L));
          k.ctx.restore();
          if (T >= tMinus) d.ringOn(140, 228 + (Y - 148), 178, 54, tMinus, GOLD, 2);
          if (settled) k.burst(684, 690, te + 0.55, {n: 14, r: 220, colors: ['paper', 'accent2']});
        });
      }
      return host(k, k.live('formula.shot') || k.live('formula.minus') ? 'point' : null);
    },

    // ---- close: the register asks. One column in a game window, one left edge (x 120); the till rings each line and
    // its display asks about your last quote
    close: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('close'), tRule2 = wordT(k, 'close', /^Margin/i, 2), send = k.S('close.send'), you = k.S('close.you');
      const last = k.S('close.last'), echo = k.S('close.echo'), tHalf = wordT(k, 'close.echo', /^half/i, 0.5), tThird = wordT(k, 'close.echo', /^third/i, 1.6);
      k.sets.register({items: [], displayLabel: 'LAST QUOTE'});
      // the till rings each line: the red $ flag pops up over the display and drops back, as it does for an item
      const ring = [t0 + 0.1, tRule2, send, last, tHalf, tThird].filter((at) => T >= at).pop();
      if (ring != null && d.fr(ring) < 12) { const fy = [10, 6, 3, 1, 0, 0, 0, 0, 0, 1, 4, 8][d.fr(ring)]; d.P(DPX + 84, DPY - 18 + fy, 18, 16, INK); d.P(DPX + 85, DPY - 17 + fy, 16, 14, RED); d.tx('$', DPX + 93, DPY - 16 + fy, {color: CREAM, align: 'center', lint: false}); }
      // the display: the question, then the two answers it could be
      const blink = Math.floor((T - t0) * 2) % 2;
      if (T >= tThird) displayText(k, '1/3?', GOLD); else if (T >= tHalf) displayText(k, '1/2?', CREAM); else displayText(k, '?', blink ? GOLD : TEAL);
      // the column
      const open = d.ease(t0 + 0.1, 8, 120);
      d.clip(0, 0, 360, 326, () => d.win(14, 200 + open, 332, 116, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#7A3442'}));
      if (open === 0) {
        if (T < send) {
          k.slam('Markup is on cost.', 120, 640, t0 + 0.3, {size: 66, color: CREAM, from: 0.5, drop: INK});
          if (T >= tRule2) k.slam('Margin is on price.', 120, 730, tRule2, {size: 66, color: 'accent', from: 0.5, drop: INK});
        } else if (T < last) {
          k.slam('Margin is on price.', 120, 640, send - 0.05, {size: 66, color: 'accent', from: 0.3, drop: INK});
          k.chip('ProofNotFluff', 120, 736, {size: 30});
          k.slam('Send this to whoever', 120, 810, send + 0.1, {size: 39, color: CREAM, from: 0.4});
          k.slam('sets your prices.', 120, 858, send + 0.25, {size: 39, color: CREAM, from: 0.4});
          if (T >= you) k.sweep(116, 900, k.measure('sets your prices.', {size: 39}) + 8, 6, you, {color: 'accent2'});
        } else {
          k.slam('Your last quote?', 120, 640, last, {size: 66, color: CREAM, from: 0.5, drop: INK});
          if (T >= echo) k.slam('Half, or a third?', 120, 722, echo, {size: 66, color: GOLD, from: 0.5, drop: INK});
          k.chip('ProofNotFluff', 120, 818, {size: 30});
          k.text('Send this to whoever sets your prices.', 120, 886, {size: 30, color: SAND});
        }
      }
      return host(k, T >= echo + 1.2 ? 'wave' : (k.live('close.you') ? 'point' : null));
    },
  },
};
