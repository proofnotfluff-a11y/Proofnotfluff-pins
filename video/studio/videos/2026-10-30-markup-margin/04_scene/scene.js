/* Scene: Markup vs margin, payoff first (Lesson 3 in Lead Clinic v2, Run the Numbers, arcade; the payoff-first test,   */
/* Oct 29, 2026). One function per top-level cue in 03_cues/cues.md. The answer card is up by the fourth second.        */
/* Numbers only from k.data (brief.md -> data.js). Every time comes from a cue start (k.S) or a spoken word (wordT), so a */
/* re-voiced take moves the picture with it. */
/* Worlds, one per section (Todd, Oct 28: "new cool graphic motion for each video"): hook and why = a job site drawn */
/* here (a site sign, two planks on sawhorses priced like the quote, a contractor's tape measure whose blade is the thing */
/* a percentage is measured on, a tower crane); math = the register rings the quote up, then the gauge reads the margin; */
/* double = the gauge again, the needle climbing to 50 only on a 100% markup; formula = the RPG tool belt, the formula is */
/* the item you equip; close = the register asks about your last quote. */
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', GREY = '#9AA0AD';
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
  /* a spinning coin, 8 x 8, four frames (face, turning, edge, turning), as the sets draw it */
  const coin = (x, y, f) => {
    const ws = [4, 3, 1, 3][((f % 4) + 4) % 4];
    for (let j = 0; j < 8; j++) { const dy = j - 3.5, hw = Math.max(0, Math.round(ws * Math.sqrt(Math.max(0, 1 - (dy * dy) / 16)))); if (!hw) continue; P(x + 4 - hw, y + j, 2 * hw, 1, '#B07A47'); if (hw > 1) P(x + 4 - hw + 1, y + j, 2 * hw - 2, 1, j < 4 ? GOLD : ORANGE); }
    if (ws >= 3) { P(x + 4, y + 2, 1, 4, '#B07A47'); DOT(x + 3, y + 2, CREAM); }
  };
  /* a rectangle outline that draws itself on, clockwise from the top left, over `frames` frames (a chalk ring in pixels) */
  const ringOn = (x, y, w, h, t0, c, th = 2, frames = 9) => {
    const per = 2 * (w + h), n = Math.round(per * clamp(fr(t0) / frames)); if (n <= 0) return;
    const seg = [[x, y, 1, 0, w], [x + w, y, 0, 1, h], [x + w, y + h, -1, 0, w], [x, y + h, 0, -1, h]]; let left = n;
    seg.forEach(([sx, sy, ux, uy, len]) => { const m = Math.min(left, len); left -= m; if (m <= 0) return; P(ux < 0 ? sx - m : sx, uy < 0 ? sy - m : sy, ux ? m + (ux > 0 ? th : 0) : th, uy ? m + (uy > 0 ? th : 0) : th, c); });
  };
  return {P, DOT, dith, disc, line, bevel, win, fr, ease, tx, tw, clip, spr, twinkle, coin, ringOn, F, T};
};

/* ---- the words: every beat lands on a spoken word ---- */
const WS = () => (window.WORDS && window.WORDS.words) || [];
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
const host = (k, pose) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150});
/* a dark game plate for a set's words (low-res), the same one lesson 9 sets under its sets */
const plate = (d, x, y, w, h) => d.win(x, y, w, h, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
/* an ordered-dither wipe on 4-pixel blocks inside a section: closes over the 5 frames before t0, clears over the 7 after */
const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];
const wipe = (k, t0) => {
  const f = Math.floor((k.T - t0) * 30 + 0.005); if (f < -5 || f >= 7) return;
  const th = f < 0 ? Math.round((f + 6) / 6 * 16) : Math.round((1 - (f + 1) / 8) * 16); k.ctx.fillStyle = INK;
  for (let y = 0; y < 1920; y += 12) for (let x = 0; x < 1080; x += 12) if (BAYER[((y / 12) % 4) * 4 + ((x / 12) % 4)] < th) k.ctx.fillRect(x, y, 12, 12);
};
/* a rubber stamp in a dark box with a coloured rim, landed with the kit's hit-stop (k.stampIn); sizes on whole pixels */
const stampBox = (k, s, cx, y, t0, o = {}) => {
  const size = o.size || 66, c = o.color || GOLD, w = Math.round((k.measure(s, {size}) + 54) / 6) * 6, h = size + 36, x = Math.round((cx - w / 2) / 3) * 3;
  k.stampIn(t0, () => {
    k.shape(k.rectPts(x + 6, y + 6, w, h, 0), {fill: INK, line: false}); k.shape(k.rectPts(x, y, w, h, 0), {fill: '#1B1420', line: false});
    k.shape(k.rectPts(x + 6, y + 6, w - 12, 6, 0), {fill: c, line: false}); k.shape(k.rectPts(x + 6, y + h - 12, w - 12, 6, 0), {fill: c, line: false});
    k.shape(k.rectPts(x + 6, y + 6, 6, h - 12, 0), {fill: c, line: false}); k.shape(k.rectPts(x + w - 12, y + 6, 6, h - 12, 0), {fill: c, line: false});
    k.text(s, x + w / 2, y + 18, {size, color: c, align: 'center'});
  }, {at: [x + w / 2, y + h], freeze: o.freeze});
};
/* a thin strike through a line of text, drawn on 0.4 s after the line was read */
const strike = (k, x, y, w, t0, c = RED) => { const q = eo((k.T - t0) / 0.18); if (q > 0) k.shape(k.rectPts(x, y, Math.round(w * q / 3) * 3, 6, 0), {fill: c, line: false}); };

/* ================================================================================================================ */
/* the job site (hook, why): our own set piece. A tower crane swings a beam over a site sign (the scene's board, frame */
/* y 258 to 630); under it two planks lie on sawhorses, priced like the quote (the cost plank, the markup plank painted */
/* orange). A contractor's tape measure sits at the left: its blade whips out to what a percentage is measured on, its */
/* marks labelled in dollars. Coins hop onto the planks (what the customer pays), tags hang off the markup plank. */
const PXD = 0.19, TX0 = 28, XC = (usd) => Math.round(TX0 + usd * PXD);   /* plank pixels per dollar: $1,500 = 285 px */
const site = (k, o) => {
  const d = px(k), {P, DOT, dith, disc, line, bevel, fr, tx, T, F} = d, n = k.data.numbers;
  /* the sky and the crane */
  P(0, 0, 360, 80, '#5B8FB9'); P(0, 80, 360, 80, '#87CEEB'); P(0, 160, 360, 70, '#BDE6F5'); dith(0, 80, 360, 2, '#5B8FB9', 1); dith(0, 160, 360, 2, '#87CEEB', 1);
  const cloud = (x, y, w, seed) => { const m = Math.max(2, Math.round(w / 9)); for (let i = 0; i < m; i++) { const r = 3 + Math.round(hash(seed + i * 1.71) * 3) + (i > 0 && i < m - 1 ? 2 : 0); disc(x + Math.round((i + 0.5) * w / m), y - r + 6, r, CREAM); } P(x + 2, y + 3, w - 4, 3, CREAM); P(x + 3, y + 5, w - 6, 1, SAND); };
  [[30, 24, 34, 1], [170, 40, 26, 5], [260, 18, 30, 9]].forEach(([x, y, w, s]) => cloud(((x - Math.floor(F / 12)) % 420 + 420) % 420 - 40, y, w, s));
  /* the mast (a lattice), the jib along the top, the cab, the counterweight, a trolley with a swinging beam */
  for (let y = 26; y < 232; y += 8) { P(304, y, 2, 8, '#3B82C4'); P(316, y, 2, 8, '#3B82C4'); line(306, y, 315, y + 7, '#5B8FB9'); }
  P(110, 26, 250, 3, '#3B82C4'); P(110, 32, 250, 1, '#3B82C4'); for (let x = 112; x < 360; x += 8) line(x, 29, x + 4, 32, '#5B8FB9');
  P(296, 33, 26, 14, '#F2A541'); P(296, 33, 26, 1, GOLD); P(300, 36, 8, 5, '#BDE6F5'); P(330, 30, 24, 10, '#4A4E5A');
  const sway = [0, 1, 1, 1, 0, -1, -1, -1][Math.floor(F / 9) % 8], bx = 176 + sway;
  P(172, 28, 10, 5, '#253048'); line(177, 33, bx, 62, '#253048'); P(bx - 2, 62, 5, 3, '#4A4E5A');
  P(bx - 22, 66, 44, 4, '#E2633B'); P(bx - 22, 66, 44, 1, GOLD); P(bx - 22, 70, 44, 2, '#7A3442');
  /* the back fence and the ground */
  P(0, 204, 360, 26, '#9AA0AD'); for (let x = 0; x < 360; x += 6) { line(x, 204, x + 6, 216, '#6B7080'); line(x + 6, 216, x, 228, '#6B7080'); } P(0, 204, 360, 1, '#6B7080');
  P(0, 228, 360, 189, '#B07A47'); P(0, 228, 360, 2, '#8C5A33');
  for (let i = 0; i < 90; i++) DOT(Math.floor(hash(i * 2.3) * 360), 232 + Math.floor(hash(i * 5.1) * 180), i % 3 ? '#8C5A33' : '#D9A066');
  /* a cone and a brick stack (right), a cement bag (left), clear of the host and the dialog box */
  const cone = (x, y) => { P(x + 4, y, 4, 4, '#E2633B'); P(x + 3, y + 4, 6, 4, CREAM); P(x + 2, y + 8, 8, 5, '#E2633B'); P(x, y + 13, 12, 3, '#7A3442'); };
  cone(332, 300); cone(4, 300);
  for (let r = 0; r < 3; r++) for (let c = 0; c < 3 - (r === 2 ? 1 : 0); c++) { const xx = 290 + c * 12 + (r % 2) * 6, yy = 310 - r * 6; P(xx, yy, 11, 5, '#7A3442'); P(xx, yy, 11, 1, '#E2633B'); }
  /* the floor: packed gravel */
  P(0, 417, 360, 223, '#8C5A33'); for (let i = 0; i < 160; i++) DOT(Math.floor(hash(i * 7.7) * 360), 420 + Math.floor(hash(i * 3.9) * 216), i % 2 ? '#6B4226' : '#B07A47');
  /* a poured slab with its form boards, a lumber stack and a wheelbarrow under the Reel's caption band */
  P(0, 417, 360, 30, '#9AA0AD'); P(0, 417, 360, 2, '#C9CCD3'); P(0, 445, 360, 3, '#6B4226'); for (let x = 30; x < 360; x += 60) P(x, 419, 1, 26, '#6B7080');
  for (let r = 0; r < 4; r++) { const y = 492 - r * 7, w = 96 - r * 10; P(18 + r * 5, y, w, 7, INK); P(19 + r * 5, y + 1, w - 2, 5, '#D9A066'); P(19 + r * 5, y + 1, w - 2, 1, '#F7D79B'); DOT(19 + r * 5 + 3, y + 3, '#B07A47'); }
  P(236, 470, 64, 20, INK); P(238, 472, 60, 16, '#3B82C4'); P(238, 472, 60, 2, '#87CEEB'); P(244, 466, 48, 6, '#9AA0AD'); line(298, 478, 330, 470, '#6B4226', 2); line(240, 488, 232, 500, '#6B4226', 2);
  disc(262, 500, 8, INK); disc(262, 500, 6, '#4A4E5A'); disc(262, 500, 2, GREY); P(262 + [0, 4, 0, -4][Math.floor(F / 20) % 4] - 0, 499, 1, 1, GREY);
  /* the site sign: two posts, a painted board with bolts (the scene's words go on it) */
  P(56, 200, 6, 32, '#6B4226'); P(298, 200, 6, 32, '#6B4226'); P(56, 200, 2, 32, '#8C5A33'); P(298, 200, 2, 32, '#8C5A33');
  d.win(14, 82, 332, 130, {base: '#253048', hi: '#3B82C4', lo: '#1B1420', rule: '#3B82C4'});
  [[18, 86], [338, 86], [18, 204], [338, 204]].forEach(([a, b]) => { DOT(a, b, GREY); DOT(a + 1, b + 1, '#4A4E5A'); });
  /* the sawhorses */
  [[44, 30], [232, 30]].forEach(([x, w]) => { P(x - 4, 250, w + 8, 5, '#8C5A33'); P(x - 4, 250, w + 8, 1, '#D9A066'); line(x, 255, x - 6, 304, '#6B4226', 3); line(x + w, 255, x + w + 6, 304, '#6B4226', 3); P(x - 3, 280, w + 6, 2, '#6B4226'); });
  /* the planks: cost (raw wood), markup (painted orange); each carries its price */
  const plank = (x0, x1, base, hi, lo, label, lc) => {
    P(x0, 232, x1 - x0, 18, INK); P(x0 + 1, 233, x1 - x0 - 2, 16, base); P(x0 + 1, 233, x1 - x0 - 2, 1, hi); P(x0 + 1, 247, x1 - x0 - 2, 2, lo);
    for (let x = x0 + 9; x < x1 - 4; x += 23) P(x, 237 + (x % 3), 7, 1, lo);
    tx(label, (x0 + x1) / 2, 235, {color: lc, align: 'center'});
  };
  plank(XC(0), XC(n.cost.value), '#D9A066', '#F7D79B', '#B07A47', `COST ${n.cost.shown}`, '#4A2E1B');
  if (o.noMarkup) { const x0 = XC(n.cost.value) + 2, x1 = XC(n.price.value); for (let x = x0; x < x1; x += 5) { P(x, 232, 3, 1, GOLD); P(x, 249, 3, 1, GOLD); } P(x1 - 1, 232, 1, 18, GOLD);
    if (o.askAt == null || T < o.askAt || Math.floor(fr(o.askAt) / 8) % 2 === 0) tx('?', (x0 + x1) / 2, 235, {color: GOLD, align: 'center'}); }
  else plank(XC(n.cost.value), XC(n.price.value), '#F2A541', GOLD, '#B07A47', o.markupLabel || `+${n.markupUsd.shown}`, '#4A2E1B');
  /* the glow: the markup plank outlined in gold, blinking twice a second for its first second */
  const glow = () => { const x0 = XC(n.cost.value) - 1, x1 = XC(n.price.value) + 1; P(x0, 230, x1 - x0, 2, GOLD); P(x0, 250, x1 - x0, 2, GOLD); P(x0, 230, 2, 22, GOLD); P(x1 - 2, 230, 2, 22, GOLD); };
  if (o.glowAt != null && T >= o.glowAt && (fr(o.glowAt) >= 30 || Math.floor(fr(o.glowAt) / 8) % 2 === 0)) glow();
  /* a pulse: three quick blinks, then the plank goes back to plain */
  else if (o.pulseAt != null && fr(o.pulseAt) >= 0 && fr(o.pulseAt) < 24 && Math.floor(fr(o.pulseAt) / 4) % 2 === 0) glow();
  /* the tape measure: the blade length eases (with a little whip) from one mark to the next */
  const marks = (o.tape || []).filter((m) => T >= m.at), cur = marks[marks.length - 1], prev = marks[marks.length - 2];
  let L = 2;
  if (cur) { const from = prev ? XC(prev.usd) - TX0 : 2, to = XC(cur.usd) - TX0, f = fr(cur.at), q = clamp(f / 8);
    const back = q >= 1 ? 1 : 1 + 2.2 * Math.pow(q - 1, 3) + 1.2 * Math.pow(q - 1, 2); L = Math.round(from + (to - from) * back); }
  if (!cur && o.twitch != null && fr(o.twitch) >= 0 && fr(o.twitch) < 12) L = 2 + [2, 5, 7, 8, 8, 7, 6, 5, 4, 3, 2, 0][fr(o.twitch)];
  P(TX0, 226, L, 4, INK); P(TX0, 226, L, 3, GOLD); P(TX0, 226, L, 1, '#FFF2B8');
  for (let usd = 100; XC(usd) - TX0 <= L; usd += 100) P(XC(usd), 226, 1, 2, INK);
  (o.noMarkup ? [n.cost, n.price] : [n.markupUsd, n.cost, n.price]).forEach((m) => { const x = XC(m.value); if (x - TX0 > L) return; P(x, 226, 1, 4, INK); tx(m.shown, x - 1, 213, {color: CREAM, align: 'right', drop: INK}); });
  P(TX0 + L - 1, 224, 2, 8, INK); P(TX0 + L, 225, 1, 6, GREY);   /* the hook on the end */
  /* the case: yellow, a black grip, the belt clip, the lock button */
  bevel(6, 218, 24, 22, GOLD, '#FFF2B8', '#B07A47', INK); P(9, 230, 18, 7, '#2B2033'); P(9, 230, 18, 1, '#4A4E5A'); disc(18, 225, 3, '#B07A47'); DOT(17, 224, CREAM); P(28, 222, 3, 4, '#E2633B');
  /* the bracket under a span: end ticks and a gold line, built from the left over 6 frames */
  if (o.bracket && T >= o.bracket.at) { const x0 = XC(o.bracket.from), x1 = XC(o.bracket.to), w = Math.round((x1 - x0) * clamp(fr(o.bracket.at) / 6)); P(x0, 254, 2, 7, GOLD); P(x0, 257, w, 2, GOLD); if (w >= x1 - x0) P(x1 - 2, 254, 2, 7, GOLD); }
  /* coins hop in from the right and land on the planks with a twinkle (what the customer pays) */
  if (o.coinsAt != null) for (let i = 0; i < 5; i++) { const t = o.coinsAt + i * 0.13, dt = T - t; if (dt < 0) continue; const land = XC(n.price.value * (0.15 + i * 0.17)), q = clamp(dt / 0.45);
    if (q < 1) d.coin(Math.round(land - 4 + (1 - q) * 40), Math.round(262 - 10 * q * (1 - q) * 4), Math.floor(F / 2) + i); else { const g = Math.floor((dt - 0.45) * 15); if (g < 8) d.twinkle(land, 266, g, GOLD); } }
  /* tags hang off the markup plank on a string and swing to rest */
  (o.tags || []).forEach((tg) => {
    if (T < tg.at) return; const f = fr(tg.at), sw = [0, -4, -3, -1, 2, 3, 2, 0, -1, -1, 0, 1, 0][Math.min(12, Math.floor(f / 2))], drop = f < 4 ? [-10, -5, -2, 1][f] : 0;
    const x = tg.x + sw, y = tg.y + drop, w = Math.round(d.tw(tg.text)) + 10;
    line(tg.x, 250, x, y, CREAM);
    P(x - w / 2 - 1, y - 1, w + 2, 18, INK); P(x - w / 2, y, w, 16, tg.c || '#7A3442'); P(x - w / 2, y, w, 1, '#F09A9A'); DOT(x, y + 2, INK);
    tx(tg.text, x, y + 2, {color: CREAM, align: 'center', lint: f >= 26});
  });
};

/* ================================================================================================================ */
/* the bench close-up (hook, 0.76 s to "Is"): the cut in on the quote. The claim rides on a title plate up top with its */
/* source; below it the same tape measure and planks drawn big on the workbench (one low-res pixel per 3 frame units, */
/* nothing scaled): the blade runs out to the cost mark on "fifty" and the orange markup plank blinks on "percent". */
const XB = (usd) => Math.round(8 + usd * 344 / 1500);   /* big plank pixels per dollar: $1,500 = 344 px */
const bench = (k, o) => {
  const d = px(k), {P, DOT, dith, disc, fr, tx, T} = d, n = k.data.numbers;
  /* the OSB wall, the bench edge, the bench top, the floor under the caption band */
  P(0, 0, 360, 300, o.ask ? '#4A2E1B' : '#C99A5B'); for (let i = 0; i < 260; i++) { const x = Math.floor(hash(i * 1.37) * 358), y = Math.floor(hash(i * 4.11) * 298); P(x, y, 2 + (i % 3), 1, o.ask ? (i % 4 ? '#3A2416' : '#6B4226') : (i % 4 ? '#B07A47' : '#E6C08A')); }
  P(0, 300, 360, 4, '#4A2E1B'); P(0, 304, 360, 113, '#6B4226'); for (let y = 310; y < 417; y += 9) P(0, y + (y % 2), 360, 1, '#5A3720');
  P(0, 417, 360, 223, '#8C5A33'); for (let i = 0; i < 160; i++) DOT(Math.floor(hash(i * 7.7) * 360), 420 + Math.floor(hash(i * 3.9) * 216), i % 2 ? '#6B4226' : '#B07A47');
  /* the title plate: the question and its source, held from the cover */
  if (o.ask) {   /* the third shot: the question big, the wall in shadow */
    d.win(14, 82, 332, 104, {base: '#253048', hi: '#3B82C4', lo: '#1B1420', rule: '#3B82C4'});
    k.slam('What do you', 540, 270, o.askAt, {size: 132, color: CREAM, align: 'center', drop: INK, from: 0.6});
    k.slam('quote?', 540, 410, o.askAt + 0.1, {size: 132, color: 'accent', align: 'center', drop: INK, from: 0.6});
  } else {
    d.win(14, 82, 332, 78, {base: '#253048', hi: '#3B82C4', lo: '#1B1420', rule: '#3B82C4'});
    k.text(`${n.cost.shown} job.`, 540, 268, {size: 66, color: CREAM, align: 'center', drop: INK});
    k.text('What do you quote?', 540, 344, {size: 66, color: 'accent', align: 'center', drop: INK});
    k.text('Example math. Sources: JLC, Xero', 540, 424, {size: 30, color: SAND, align: 'center'});
  }
  /* the planks, big, on the bench: cost (raw wood) and the markup (painted orange) */
  const plank = (x0, x1, base, hi, lo) => { P(x0, 222, x1 - x0, 44, INK); P(x0 + 1, 223, x1 - x0 - 2, 42, base); P(x0 + 1, 223, x1 - x0 - 2, 2, hi); P(x0 + 1, 261, x1 - x0 - 2, 4, lo);
    for (let x = x0 + 12; x < x1 - 8; x += 31) { P(x, 233 + (x % 5), 14, 1, lo); P(x + 5, 247 - (x % 3), 10, 1, lo); } };
  P(4, 266, 352, 6, '#4A2E1B');
  plank(XB(0), XB(n.cost.value), '#D9A066', '#F7D79B', '#B07A47');
  tx(`COST ${n.cost.shown}`, (XB(0) + XB(n.cost.value)) / 2, 233, {size: 66, color: '#4A2E1B', align: 'center'});
  /* the empty slot where the price goes: a dashed gold outline and a blinking question mark */
  { const x0 = XB(n.cost.value) + 3, x1 = XB(n.price.value); for (let x = x0; x < x1; x += 6) { P(x, 222, 3, 2, GOLD); P(x, 264, 3, 2, GOLD); } for (let y = 222; y < 266; y += 6) P(x1 - 2, y, 2, 3, GOLD);
    if (Math.floor(fr(0) / 10) % 2 === 0) tx('?', (x0 + x1) / 2, 233, {size: 66, color: GOLD, align: 'center', drop: INK}); }
  /* the tape: a big case at the left, the blade along the top of the planks, marks every hundred dollars */
  let L = 4;
  if (o.tapeAt != null && T >= o.tapeAt) { const to = XB(n.cost.value) - 30, q = clamp(fr(o.tapeAt) / 8), back = q >= 1 ? 1 : 1 + 2.2 * Math.pow(q - 1, 3) + 1.2 * Math.pow(q - 1, 2); L = Math.round(4 + (to - 4) * back); }
  P(30, 204, L, 10, INK); P(30, 205, L, 8, GOLD); P(30, 205, L, 2, '#FFF2B8');
  for (let usd = 100; XB(usd) - 30 <= L; usd += 100) P(XB(usd), 205, 2, usd % 500 ? 4 : 7, INK);
  if (L >= XB(n.cost.value) - 30) { P(XB(n.cost.value) - 1, 200, 3, 16, INK); tx(n.cost.shown, XB(n.cost.value) - 4, 180, {size: 39, color: CREAM, align: 'right', drop: INK}); }
  P(30 + L - 2, 200, 4, 18, INK); P(30 + L - 1, 201, 2, 16, GREY);
  d.bevel(2, 192, 34, 34, GOLD, '#FFF2B8', '#B07A47', INK); P(6, 210, 26, 10, '#2B2033'); P(6, 210, 26, 2, '#4A4E5A'); disc(19, 201, 5, '#B07A47'); DOT(17, 199, CREAM); P(33, 197, 4, 6, '#E2633B');
  k.chip('Run the numbers', 66, 846, {size: 30});
};

/* ================================================================================================================ */
/* the dial (math, double): the library gauge, with the needle driven here so it can swing from one margin to another */
/* (the set's needle only rises from zero). The set draws at rest; its resting needle is painted out and the 0 mark put */
/* back, then our needle goes on in the set's own style. The readout shows `shown`. */
const GX = 180, GY = 214, GR = 100, GA0 = Math.PI * 0.75, GSW = Math.PI * 1.5;
const dial = (k, label, v, shown, o = {}) => {
  const d = px(k), dec = Number.isInteger(shown) ? 0 : 1;
  /* one neutral zone: no source colours a margin red or orange */
  k.sets.gauge({value: 100, max: 100, at: 1e9, from: shown, dec, label, zones: o.zones || [[0, 100, '#3D2E45']]});
  const ex = Math.round(Math.cos(GA0) * (GR - 16)), ey = Math.round(Math.sin(GA0) * (GR - 16));
  d.line(GX + 1, GY + 1, GX + 1 + ex, GY + 1 + ey, INK, 2); d.line(GX, GY, GX + ex, GY + ey, INK, 2);
  d.line(GX + Math.cos(GA0) * (GR - 20), GY + Math.sin(GA0) * (GR - 20), GX + Math.cos(GA0) * (GR - 10), GY + Math.sin(GA0) * (GR - 10), CREAM, 2);
  d.tx('0', GX + Math.cos(GA0) * (GR - 32), GY + Math.sin(GA0) * (GR - 32) - 10, {color: '#C9CCD3', align: 'center', lint: false});
  /* the mark at 50: a gold notch on the bezel; a dotted ghost needle when o.ghost (what people picture, or the target) */
  if (o.notchAt != null && k.T >= o.notchAt) { const f = d.fr(o.notchAt), lift = f < 4 ? [-6, -3, -1, 1][f] : 0; for (let j = 0; j < 6; j++) d.P(GX - 5 + j, 103 + j + lift, 11 - 2 * j, 1, j ? ORANGE : GOLD); d.P(GX - 6, 102 + lift, 13, 1, INK); }
  if (o.ghostAt != null && k.T >= o.ghostAt) { const blink = d.fr(o.ghostAt) < 30 && Math.floor(d.fr(o.ghostAt) / 8) % 2; if (!blink) for (let r = 14; r < GR - 18; r += 4) d.P(GX - 1, GY - r - 1, 2, 2, o.ghostC || GOLD); }
  const na = Math.round((GA0 + GSW * clamp(v / 100, -0.02, 1.02)) * 180 / Math.PI) * Math.PI / 180, R1 = GR - 16, R2 = GR - 30;
  d.line(GX + 1, GY + 1, GX + 1 + Math.round(Math.cos(na) * R1), GY + 1 + Math.round(Math.sin(na) * R1), INK, 2);
  d.line(GX, GY, GX + Math.round(Math.cos(na) * R1), GY + Math.round(Math.sin(na) * R1), RED, 2);
  d.line(GX, GY, GX + Math.round(Math.cos(na) * R2), GY + Math.round(Math.sin(na) * R2), ORANGE, 1);
  d.disc(GX, GY, 9, INK); d.disc(GX, GY, 8, '#4A4E5A'); d.disc(GX - 1, GY - 1, 6, GREY); d.DOT(GX - 3, GY - 3, CREAM);
};
/* the needle's value: rests at v0, swings to v1 from t (overshoot, then settles), like the set's own needle */
const swing = (T, t, v0, v1, dur = 1.0) => { if (T < t) return v0; const dd = T - t, r = clamp(dd / (dur * 0.55)), w = dd > dur * 0.55 ? (v1 - v0) * 0.12 * Math.exp(-5 * (dd - dur * 0.55)) * Math.sin((dd - dur * 0.55) * 16) : 0; return v0 + (v1 - v0) * eo(r) + w; };

/* the register's display, painted over with our own words (the close asks a question, not a total) */
const DPX = 222, DPY = 114;
/* the register set right-aligns its display total at x 948; this draws the set with that one readout moved to x 918, so
   the monitor's numbers stay inside the x 930 content line (the set itself is not ours to change) */
const register = (k, o) => {
  const t = k.text;
  k.text = (s, x, y, oo) => t.call(k, s, oo && oo.align === 'right' && x === (DPX + 94) * 3 ? (DPX + 84) * 3 : x, y, oo);
  try { return k.sets.register(o); } finally { k.text = t; planks(k); }
};
const planks = (k) => {
  /* the shop floor: dark planks, staggered seams (the set's checker tiles read as a transparency grid; golden r0) */
  const pd = px(k); pd.P(0, 417, 360, 223, '#3D2E45'); pd.P(0, 417, 360, 3, '#1B1420');
  for (let y = 420, r = 0; y < 640; y += 12, r++) { pd.P(0, y + 11, 360, 1, '#2B2033'); for (let x = (r * 53) % 96; x < 360; x += 96) pd.P(x, y, 1, 11, '#2B2033'); }
};
const displayText = (k, s, c = TEAL) => { const d = px(k); d.P(DPX + 7, DPY + 19, 92, 38, '#24453A'); for (let y = DPY + 20; y < DPY + 57; y += 3) d.P(DPX + 7, y, 92, 1, '#1A332B'); d.tx(s, DPX + 53, DPY + 27, {size: 66, color: c, align: 'center'}); };

/* the tool belt behind a big card (answer, formula): the same inventory set, the FORMULA item selected */
const belt = (k, t0) => k.sets.inventory({title: 'TOOL BELT', select: [{slot: 3, at: t0}],
  items: [{icon: 'wrench', name: 'WRENCH'}, {icon: 'hammer', name: 'HAMMER'}, {icon: 'phone', name: 'PHONE'}, {icon: 'clip', name: 'FORMULA', stats: []},
    {icon: 'clock', name: 'CLOCK'}, {icon: 'mail', name: 'MAIL'}, {icon: 'coin', name: 'COIN'}, {icon: 'star', name: 'STAR'}]});

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 3',
  sendLine: 'Send this to whoever sets your prices.',
  transitions: {answer: 'levelselect', usual: 'door', why: 'dissolve', formula: 'iris', double: 'blinds', button: 'gameover'},
  trauma: {'double.x2': 0.8},
  sections: {
    /* ---- hook: the drop-in in three shots (IMPROVE 00a). The cover: the job site, the question on the sign (frame 0). */
    /* Cut in on "costs" to the bench close-up (the cost plank, the empty price slot; Snow and the dialog box come in, the */
    /* tape runs to the cost on "thousand"). Cut back out on "What" to the site: the "?" in the price slot blinks. */
    hook: (k, T) => {
      const n = k.data.numbers, d = px(k);
      const tQ = k.S('hook.q'), tCosts = Math.min(0.8, Math.max(0.4, wordT(k, 'hook', /^costs/i, 0.5) - 0.05));
      const tThou = wordT(k, 'hook', /^thousand/i, 1.1), tOut = Math.min(2.6, Math.max(tCosts + 0.6, tQ - 0.05));
      if (T >= tOut) { bench(k, {tapeAt: tThou, ask: true, askAt: tOut}); return host(k, 'shrug'); }   /* never back to the cover (design r0) */
      if (T >= tCosts) { bench(k, {tapeAt: tThou}); return host(k); }
      site(k, {noMarkup: true, askAt: tQ, twitch: 0.3, tape: [{at: Math.min(tThou, tOut), usd: n.cost.value}]});
      /* the question on the sign, settled from frame 0, centred on the sign (x 42 to 1038) */
      k.slam(`${n.cost.shown} job.`, 540, 268, -1, {size: 132, color: CREAM, align: 'center', drop: INK});
      k.slam('What do you', 540, 412, -1, {size: 66, color: 'accent', align: 'center', drop: INK, glintAt: 0.5});
      k.slam('quote?', 540, 486, -1, {size: 132, color: CREAM, align: 'center', drop: INK, glintAt: 0.9});
      plate(d, 14, 256, 200, 44);
      k.chip('Run the numbers', 66, 786, {size: 30});
      k.text('Example math. Sources: JLC, Xero', 66, 856, {size: 30, color: SAND});
      if (T >= tQ) k.burst(XC(n.cost.value + 250) * 3, 720, tQ + 0.1, {n: 12, r: 160});
      if (T < tCosts) return {host: false, speech: false};
      return host(k, T >= tQ ? 'shrug' : null);
    },

    /* ---- answer: the payoff, inside the first 8 s. The answer card rises at once over the tool belt; the division writes */
    /* in on "point", the price lands whole on "sixteen", the margin slams in on "forty". It holds to the section's end. */
    answer: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('answer');
      const tSix = wordT(k, 'answer', /^point/i, 0.6), tRes = wordT(k, 'answer.price', /^sixteen/i, 0.3), tForty = wordT(k, 'answer.margin', /^forty/i, 0.3);
      /* the answer on a split-flap board, row by row on its words (design r0: its own world, never empty on the cut) */
      k.sets.flaps({title: 'THE ANSWER', cols: 12, rows: [
        {label: 'COST', value: n.cost.shown, at: t0 + 0.05},
        {label: 'DIVIDE BY', value: n.divisor.shown, at: tSix},
        {label: '=', value: n.targetPrice.shown, at: tRes, hi: true},
        {label: 'MARGIN', value: n.targetMarginPct.shown, at: tForty, hi: true}]});
      d.win(14, 282, 332, 42, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
      if (T < tForty) k.text('Example math', 540, 884, {size: 30, color: SAND, align: 'center'});
      else k.slam(`${n.targetMarginPct.shown} margin`, 540, 864, tForty, {size: 66, color: 'accent', align: 'center', from: 0.5, drop: INK});
      if (T >= tRes) k.burst(780, 540, tRes + 0.4, {n: 18, r: 220});
      return host(k, k.live('answer') ? 'point' : null);
    },

    /* ---- usual: the register rings the usual quote up (cost, the 50% markup, the price), then splits the price in three */
    usual: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('usual');
      const tFive = wordT(k, 'usual', /^fifty/i, 0.6), tPrice = wordT(k, 'usual.price', /^fifteen/i, 0.6), tHalf = k.S('usual.half'), tThird = wordT(k, 'usual.third', /^third/i, 1.2);
      register(k, {items: [{label: 'COST', amount: n.cost.value, at: t0 + 0.15}, {label: `MARKUP ${n.markupPct.shown}`, amount: n.markupUsd.value, at: tFive}],
        totalAt: tPrice, totalLabel: 'PRICE', displayLabel: 'QUOTE', openAt: tPrice + 0.35});
      k.slam('The usual way', 72, 270, t0 + 0.15, {size: 39, color: GOLD, from: 0.4, drop: INK});
      const say = T >= tThird ? [`${n.markupUsd.shown} = 1/3`, tThird + 0.1, 'accent'] : T >= tHalf ? ['Half is margin?', tHalf, GOLD]
        : T >= tPrice ? [`The quote: ${n.price.shown}`, tPrice, CREAM] : T >= tFive ? [`Markup: +${n.markupUsd.shown}`, tFive, 'accent'] : [`Your cost: ${n.cost.shown}`, t0 + 0.15, CREAM];
      k.slam(say[0], 72, 318, say[1], {size: 66, color: say[2], from: 0.5, drop: INK});
      if (T >= tThird) {
        const f = d.fr(tThird), x0 = DPX + 12, w = 24;
        d.P(DPX + 7, DPY + 19, 92, 38, '#24453A');
        for (let i = 0; i < n.thirds.value; i++) { if (f < 3 * i) continue; const last = i === n.thirds.value - 1; d.P(x0 + i * (w + 2), DPY + 33, w, 16, INK); d.P(x0 + i * (w + 2) + 1, DPY + 34, w - 2, 14, last ? ORANGE : TEAL); d.P(x0 + i * (w + 2) + 1, DPY + 34, w - 2, 1, last ? GOLD : '#BDE6F5'); }
        if (f >= 6) { d.tx('1/3', x0 + 2 * (w + 2) + w / 2, DPY + 19, {color: GOLD, align: 'center', lint: false}); if (Math.floor(f / 15) % 2 === 0) d.P(x0 + 2 * (w + 2) + 4, DPY + 51, w - 8, 2, GOLD); }
      }
      return host(k, k.live('usual') || k.live('usual.third') ? 'point' : (k.live('usual.half') ? 'shrug' : null));
    },

    /* ---- why: back on the job site. The tape measures the cost, then the whole price; the same $500 is half of one and */
    /* a third of the other. Coins land on the planks (the price is what the customer pays). */
    why: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('why'), tMg = k.S('why.margin'), tPay = wordT(k, 'why.pays', /^pays/i, 0.6);
      site(k, {tape: [{at: t0, usd: n.cost.value}, {at: tMg, usd: n.price.value}], glowAt: t0, bracket: {at: tPay, from: 0, to: n.price.value}, coinsAt: tPay});
      k.slam('Markup vs margin', 72, 270, t0 + 0.15, {size: 66, color: GOLD, from: 0.5, drop: INK});
      const row = (y, name, top, base, sub, on, res, t, tOn) => {
        if (T < t) return;
        k.slam(`${name}: ${top} / ${base}`, 72, y + 12, t, {size: 39, color: CREAM, from: 0.4, drop: INK});
        k.slam(res, 930, y, t + 0.45, {size: 132, color: 'accent', align: 'right', from: 0.3, drop: INK});
        k.text(sub + on, 72, y + 60, {size: 30, color: SAND});
        k.sweep(72 + k.measure(sub, {size: 30}) - 3, y + 90, k.measure(on, {size: 30}) + 6, 6, tOn, {color: 'accent2'});
      };
      row(350, 'Markup', n.markupUsd.shown, n.cost.shown, 'measured on your ', 'cost', `= ${n.markupPct.shown}`, t0, wordT(k, 'why', /^cost/i, 1.2));
      row(482, 'Margin', n.markupUsd.shown, n.price.shown, 'measured on the ', 'price', `= ${n.marginPct.shown}`, tMg, wordT(k, 'why.margin', /^price/i, 1.0));
      if (T >= k.S('why.pays')) { plate(d, 14, 263, 332, 50); k.slam('Price = what the customer pays you', 72, 843, k.S('why.pays'), {size: 39, color: GOLD, from: 0.4}); }
      return host(k, k.live('why') || k.live('why.margin') ? 'point' : null);
    },

    /* ---- formula: the tool belt again. The formula card rises, Price = Cost over 1 - margin writes in on "Price is", the */
    /* ring draws round 1 - margin on "minus"; the worked 40% line sits on the card. Held to the section's end. */
    formula: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('formula'), tEq = k.S('formula.eq');
      const tMinus = wordT(k, 'formula.minus', /^minus/i, 0.3);
      belt(k, t0);
      const up = d.ease(t0, 8, 180), Y = 148 + up, settled = up === 0;
      d.clip(0, 0, 360, 326, () => {
        d.win(14, Y, 332, 176, {base: '#1B1420', hi: '#7A3442', lo: INK, rule: '#F2A541'});
        k.ctx.save(); k.ctx.translate(0, (Y - 148) * 3);
        k.chip('Start from the margin', 66, 462, {size: 30, fill: 'accent', color: INK});
        const te = t0 + 0.05, a = (t) => (T >= t ? 1 : 0), L = {lint: settled};
        const wP = k.measure('Price =', {size: 132}), wM = k.measure('1 - margin', {size: 132}), bw = Math.round((wM + 24) / 3) * 3;
        const fx = Math.max(102, Math.round((520 - (wP + 24 + bw) / 2) / 3) * 3), bx = Math.round((fx + wP + 24) / 3) * 3, fc = bx + bw / 2;
        if (a(te)) k.text('Price =', fx, 616, Object.assign({size: 132, color: CREAM, drop: INK}, L));
        if (a(te + 0.2)) k.text('Cost', fc, 530, Object.assign({size: 132, color: CREAM, align: 'center', drop: INK}, L));
        k.sweep(bx, 676, bw, 12, te + 0.35, {color: GOLD});
        if (a(te + 0.5)) k.text('1 - margin', fc, 700, Object.assign({size: 132, color: 'accent', align: 'center', drop: INK}, L));
        if (a(tMinus + 0.4)) k.text(`${n.targetMarginPct.shown}: ${n.cost.shown} / ${n.divisor.shown} = ${n.targetPrice.shown}`, 66, 880, Object.assign({size: 39, color: GOLD}, L));
        k.ctx.restore();
        if (T >= tMinus) d.ringOn(Math.round(bx / 3) - 2, 228 + (Y - 148), Math.round(bw / 3) + 4, 54, tMinus, GOLD, 2);
        if (settled) k.burst(684, 690, te + 0.55, {n: 14, r: 220, colors: ['paper', 'accent2']});
      });
      return host(k, k.live('formula.eq') || k.live('formula.minus') ? 'point' : null);
    },

    /* ---- double (the proof): the gauge. The needle sits at a third; the gold notch is the target; doubling the cost (a */
    /* second cost-sized block in the plate) is a 100% markup, and only then does the needle climb to 50. Source tag: JLC. */
    double: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('double');
      const tDbl = wordT(k, 'double.x2', /^double/i, 0.6), tHun = tDbl + 0.5, tTwo = wordT(k, 'double.quote', /^two$/i, 0.1);
      const v = swing(T, tHun, n.marginPct.value, n.doubleMarginPct.value, 1.1);
      const shown = T < tHun + 0.6 ? n.marginPct.value : n.doubleMarginPct.value;   /* no in-between readouts like 49.6 (golden r0) */
      dial(k, `WANT A ${n.doubleMarginPct.shown} MARGIN?`, v, shown, {notchAt: t0 + 0.4, ghostAt: t0 + 0.4, ghostC: ORANGE});
      if (T >= tHun + 1.1) k.burst(540, 330, tHun + 1.1, {n: 22, r: 260});
      plate(d, 14, 268, 332, 56);
      const bx = 22, bw = 96, by = 275, gw = T < tDbl ? 0 : Math.round(bw * eo(d.fr(tDbl) / 8));
      d.P(bx - 1, by - 1, bw + 2, 20, INK); d.P(bx, by, bw, 18, TEAL); d.P(bx, by, bw, 1, '#BDE6F5'); d.P(bx, by + 16, bw, 2, '#2F6F67');
      d.tx(`COST ${n.cost.shown}`, bx + bw / 2, by + 3, {color: INK, align: 'center'});
      if (gw > 0) { d.P(bx + bw + 1, by - 1, gw + 1, 20, INK); d.P(bx + bw + 2, by, gw - 1, 18, ORANGE); d.P(bx + bw + 2, by, gw - 1, 1, GOLD); d.P(bx + bw + 2, by + 16, gw - 1, 2, '#B07A47'); }
      if (gw === bw && T >= tHun) d.tx(`+${n.doubleMarkupPct.shown}`, bx + bw + 2 + bw / 2, by + 3, {color: INK, align: 'center'});
      if (T >= tTwo) k.slam(`= ${n.doublePrice.shown} quote`, 930, 822, tTwo, {size: 39, color: GOLD, align: 'right', from: 0.5});
      if (T >= tDbl && T < tHun + 0.6) stampBox(k, 'DOUBLE YOUR COST', 560, 882, tDbl, {color: RED, freeze: 5});
      else if (T < tDbl) k.slam(`Now: ${n.markupPct.shown} markup = ${n.marginPct.shown} margin`, 72, 900, t0 + 0.2, {size: 39, color: SAND, from: 0.4});
      else k.slam(`${n.doubleMarkupPct.shown} markup = ${n.doubleMarginPct.shown} margin`, 72, 900, tHun + 0.6, {size: 39, color: CREAM, from: 0.4});
      k.text('Math: JLC', 930, 276, {size: 30, color: SAND, align: 'right'});
      return host(k, k.live('double.x2') || k.live('double.quote') ? 'point' : null);
    },

    /* ---- button: the register asks again. One column, one left edge (x 72): the job, then the rule in two lines */
    button: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('button'), tQuote = wordT(k, 'button', /^quote$/i, 1.4), tNot = k.S('button.not');
      k.sets.register({items: [], displayLabel: 'NEXT QUOTE'}); planks(k);
      const ring = [t0 + 0.1, tQuote, tNot].filter((at) => T >= at).pop();
      if (ring != null && d.fr(ring) < 12) { const fy = [10, 6, 3, 1, 0, 0, 0, 0, 0, 1, 4, 8][d.fr(ring)]; d.P(DPX + 84, DPY - 18 + fy, 18, 16, INK); d.P(DPX + 85, DPY - 17 + fy, 16, 14, RED); d.tx('$', DPX + 93, DPY - 16 + fy, {color: CREAM, align: 'center', lint: false}); }
      if (T >= tQuote) { const dd = px(k); dd.P(DPX + 7, DPY + 19, 92, 38, '#24453A'); for (let y = DPY + 20; y < DPY + 57; y += 3) dd.P(DPX + 7, y, 92, 1, '#1A332B'); dd.tx(n.targetPrice.shown, DPX + 53, DPY + 31, {size: 39, color: GOLD, align: 'center'}); }
      else displayText(k, '?', Math.floor((T - t0) * 2) % 2 ? GOLD : TEAL);
      const open = d.ease(t0 + 0.1, 8, 120);
      d.clip(0, 0, 360, 326, () => d.win(14, 198 + open, 332, 120, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#7A3442'}));
      if (open === 0) {
        if (T < tQuote) k.slam(`${n.cost.shown} job?`, 72, 640, t0 + 0.3, {size: 132, color: CREAM, from: 0.4, drop: INK});
        else {
          k.slam('Quote from', 72, 606, tQuote, {size: 132, color: CREAM, from: 0.4, drop: INK});
          k.slam('the margin.', 72, 736, tQuote + 0.15, {size: 132, color: 'accent', from: 0.4, drop: INK});
        }
        if (T >= tNot) { k.slam('Not the markup.', 72, 878, tNot, {size: 66, color: GOLD, from: 0.4, drop: INK}); k.sweep(72, 950, k.measure('Not the markup.', {size: 66}), 6, tNot + 0.3, {color: 'accent'}); }
      }
      return host(k, T >= tNot + 0.6 ? 'wave' : (k.live('button') ? 'point' : null));
    },
  },
};
