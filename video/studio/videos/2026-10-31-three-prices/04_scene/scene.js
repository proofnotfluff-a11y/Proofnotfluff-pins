// Scene: Three prices on every quote (Lesson 4, Quote Clinic, arcade). One function per top-level cue in 03_cues/cues.md.
// Numbers only from k.data (brief.md -> data.js). Every time comes from a cue start (k.S) or a spoken word (wordT), so a
// re-voiced take moves the picture with it.
// Worlds, one per section (brief.md, Worlds): hook and close = the storefront counter (the price tag flips from one price
// to three); stakes = the arcade high-score table; why = a street of 100 houses (our own piece: 68 light up and send out
// quote envelopes, then the three-price quote); card = a quote clipboard on a truck tailgate at dusk (our own
// piece); survey = the slot machine (4+ options lands 5 2 %, 1 to 3 lands 4 2 %, the 1 2 3 reels bracketed as one group,
// then 3 3 3). Steady camera: no stamps, no trauma; the motion lives in the things on screen.
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', GREY = '#9AA0AD', PLUM = '#3D2E45', WINE = '#7A3442';
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
  const twinkle = (x, y, f, c = CREAM) => { const s = [0, 1, 2, 1][((f % 4) + 4) % 4]; DOT(x, y, c); for (let i = 1; i <= s; i++) { DOT(x - i, y, c); DOT(x + i, y, c); DOT(x, y - i, c); DOT(x, y + i, c); } };
  // a line that types on, three letters a frame; it counts for the layout check once it is whole
  const type = (s, x, y, at, o = {}) => { if (T < at) return; const m = s.slice(0, Math.max(1, (fr(at) + 1) * 3)); k.text(m, x, y, Object.assign({size: 39}, o, {lint: m.length === s.length && o.lint !== false})); };
  return {P, DOT, dith, disc, line, bevel, win, fr, ease, tx, tw, clip, twinkle, type, F, T};
};

// ---- the words: every beat lands on a spoken word, so a re-voiced take moves everything with it ----
const WS = () => (window.WORDS && window.WORDS.words) || [];
const norm = (s) => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
// the time a word is said (words.json), at or after a cue; falls back to the cue's start plus dflt
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
/* a percent that counts up from 85% of its value and lands on its spoken word: the count starts LEAD s before the word
   and lands 0.15 s into it, so the figure is on screen as it is said */
const LEAD = 0.3;
const pct = (k, num, at) => k.count(num.value, clamp((k.T - (at - LEAD)) / 0.45), {from: num.value * 0.85, suffix: '%'});
/* sparks in whole low-res pixels, flying out in a fan (dir and spread in radians) and falling. A spark inside any avoid
   box (frame units [x0, y0, x1, y1]: words, cards, tags) is not drawn, so sparks never cross text */
const spray = (k, x, y, t0, o = {}) => {
  const dt = k.T - t0, life = o.life || 0.6; if (dt < 0 || dt > life) return;
  const P = px(k).P, n = o.n || 12, r = o.r || 150, cols = o.colors || [GOLD, ORANGE, CREAM], q = eo(dt / life), avoid = o.avoid || [];
  const dir = o.dir != null ? o.dir : -Math.PI / 2, spread = o.spread != null ? o.spread : Math.PI * 2;
  for (let i = 0; i < n; i++) {
    const a = dir + (hash(i * 1.7 + t0 * 3.1) - 0.5) * spread, sp = (0.45 + hash(i * 4.3 + t0) * 0.55) * r, sz = dt < life * 0.5 ? 2 : 1;
    const fx = Math.round((x + Math.cos(a) * sp * q) / 3), fy = Math.round((y + Math.sin(a) * sp * q + 200 * dt * dt) / 3);
    if (avoid.some(([x0, y0, x1, y1]) => (fx + sz) * 3 > x0 && fx * 3 < x1 && (fy + sz) * 3 > y0 && fy * 3 < y1)) continue;
    P(fx, fy, sz, sz, cols[i % cols.length]);
  }
};
/* twinkles that sit just outside a number's box (low-res points), one after another, for a second */
const sparkle = (k, pts, at, c = GOLD) => {
  const d = px(k), f = d.fr(at); if (f < 0 || f >= 30) return;
  pts.forEach(([x, y], j) => { const g = f - j * 4; if (g >= 0 && g < 20) d.twinkle(x, y, g, c); });
};
const host = (k, pose) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150});

// ================================================================================================================
// the storefront (hook, close): the library counter, plus a light that sweeps the shop glass every 2.4 s, the chalk
// board's words, and a twinkle on the tag once it shows three prices
const storefront = (k, o) => {
  const d = px(k), n = k.data.numbers;
  /* the set's own tag-flip sparks land on the tag's price; they are held while it draws (the scene's sprays keep off text) */
  const kb = k.burst; k.burst = () => {};
  const r = k.sets.counter({shop: 'QUOTE CLINIC', item: 'toolbox', tags: o.tags});
  k.burst = kb;
  // the chalk board on the wall (frame x 66 to 462, y 432 to 624): lines of 66, left edge 78
  (o.chalk || []).forEach(([s, at, c, y]) => { if (k.T >= at) k.slam(s, 78, y, at, {size: 66, color: c || CREAM, from: 0.4, glint: false}); });
  // once the tag shows three prices, a twinkle walks its edge
  if (o.threeAt != null && k.T >= o.threeAt + 0.5) { const f = d.fr(o.threeAt + 0.5); d.twinkle(220 + ((f >> 2) % 6) * 17, 132 + ((f >> 3) & 1) * 46, f, GOLD); }
  return r;
};

// ================================================================================================================
// the street (why): our own piece. A dusk sky with a hanging banner (the source), a 10 by 10 grid of houses whose windows
// light row by row, envelopes that rise off the lit roofs and drift right, and a plate under the street for the words.
const HX = (i) => 24 + (i % 10) * 32, HY = (i) => 120 + Math.floor(i / 10) * 14;
const street = (k, o) => {
  const d = px(k), {P, DOT, F, T} = d;
  // sky: plum to wine to an orange glow, stars that twinkle in turn, the moon
  P(0, 0, 360, 417, '#2B2033'); P(0, 40, 360, 30, PLUM); P(0, 70, 360, 26, WINE); P(0, 96, 360, 22, '#B4523A'); d.dith(0, 68, 360, 3, PLUM, 1); d.dith(0, 94, 360, 3, WINE, 1);
  for (let i = 0; i < 24; i++) { const x = Math.floor(hash(i * 2.3) * 356), y = 4 + Math.floor(hash(i * 5.1) * 60); const f = (Math.floor(F / 6) + i * 5) % 16; if (f < 4 && T >= 0.5) d.twinkle(x, y, f, CREAM); else DOT(x, y, '#6B7080'); }
  d.disc(318, 30, 9, '#F4E6D3'); d.disc(321, 28, 8, '#2B2033');
  // the banner on two poles
  P(10, 84, 3, 34, GREY); P(347, 84, 3, 34, GREY); P(16, 86, 328, 26, INK); P(17, 87, 326, 24, '#7A3442'); P(17, 87, 326, 1, RED); P(17, 110, 326, 1, PLUM);
  const ban = (o.banner || []).filter((b) => T >= b.at).pop();
  if (ban) d.type(ban.text, 540, 279, ban.at, {color: GOLD, align: 'center'});
  // the houses
  const lit = o.litAt != null && T >= o.litAt ? Math.min(o.lit, Math.floor(o.lit * clamp((T - o.litAt) / 0.9) + 0.0001)) : 0;
  for (let i = 0; i < 100; i++) {
    const x = HX(i), y = HY(i), on = i < lit, roof = on ? RED : '#6B4226';
    P(x + 5, y, 4, 1, roof); P(x + 3, y + 1, 8, 1, roof); P(x + 1, y + 2, 12, 1, roof); P(x, y + 3, 14, 1, roof);
    P(x + 1, y + 4, 12, 7, on ? '#C9CCD3' : '#4A4E5A'); P(x + 1, y + 4, 12, 1, on ? CREAM : '#6B7080');
    P(x + 3, y + 6, 3, 2, on ? GOLD : '#1B1420'); P(x + 9, y + 6, 3, 2, on ? GOLD : '#1B1420'); P(x + 6, y + 7, 2, 4, on ? ORANGE : '#1B1420');
    if (on && i === lit - 1 && lit < o.lit) d.twinkle(x + 7, y - 2, F, GOLD);
  }
  for (let r = 0; r < 10; r++) P(20, 131 + r * 14, 324, 1, '#1B1420');
  // envelopes off the lit roofs: each rises and drifts right on whole pixels, on its own 1.2 s loop
  if (o.envAt != null && T >= o.envAt && T < (o.envEnd || 1e9)) {
    for (let i = 0; i < lit; i += 2) {
      const st = o.envAt + (hash(i * 3.7) * 1.2), ph = T - st; if (ph < 0) continue;
      const q = (ph % 1.2) / 1.2, x = HX(i) + 4 + Math.round(q * 26), y = HY(i) - 2 - Math.round(q * 10);
      if (y < 118) continue;
      P(x - 1, y - 1, 8, 6, INK); P(x, y, 6, 4, CREAM); DOT(x + 1, y + 1, SAND); DOT(x + 4, y + 1, SAND); DOT(x + 2, y + 2, SAND); DOT(x + 3, y + 2, SAND);
    }
  }
  if (o.dimAt != null && T >= o.dimAt) d.dith(20, 118, 324, 142, INK, 0);
  // the ground and the plate
  P(0, 258, 360, 159, '#1B1420'); P(0, 258, 360, 2, PLUM);
  d.win(14, 263, 332, 64, {base: '#1B1420', hi: PLUM, lo: INK, rule: PLUM});
  P(0, 417, 360, 223, '#2B2033'); for (let y = 424; y < 640; y += 10) P(0, y, 360, 1, '#1B1420');
};
// a quote slip over the street: header, lines, and either one price or the three rows
const slip = (k, x, y, w, h, draw) => {
  const d = px(k);
  d.P(x + 3, y + 3, w, h, INK); d.P(x - 1, y - 1, w + 2, h + 2, INK); d.P(x, y, w, h, CREAM); d.P(x, y + h - 2, w, 2, SAND);
  for (let i = 0; i < w; i += 6) d.DOT(x + i + 2, y + h, CREAM);
  draw(x, y);
};

// ================================================================================================================
// the tailgate (card): our own piece. Dusk over the rooftops, clouds drifting a pixel every 4 frames, leaves crossing the
// sky, a pickup's tailgate down, its hazard light, and the clipboard that rises onto it (the content: frame y 300 to 950)
const tailgate = (k, o) => {
  const d = px(k), {P, DOT, F, T} = d;
  P(0, 0, 360, 60, '#253048'); P(0, 60, 360, 50, PLUM); P(0, 110, 360, 50, WINE); P(0, 160, 360, 70, '#B4523A'); d.dith(0, 58, 360, 3, '#253048', 1); d.dith(0, 108, 360, 3, PLUM, 1); d.dith(0, 158, 360, 3, WINE, 1);
  for (let i = 0; i < 4; i++) { const w = 40 + i * 9, x = ((Math.floor(F / 4) + i * 97) % 440) - 60, y = 18 + i * 34; P(x, y, w, 4, '#E6D3BC'); P(x + 6, y - 3, w - 14, 3, '#E6D3BC'); P(x + 3, y + 4, w - 6, 1, '#B39A88'); }
  for (let i = 0; i < 9; i++) { const x = 30 + i * 38, h = 26 + Math.floor(hash(i * 3.1) * 30); P(x, 230 - h, 32, h, '#2B2033'); P(x + 4, 230 - h - 8, 24, 8, '#2B2033'); DOT(x + 10, 230 - h + 8, (i + (F >> 5)) % 3 ? GOLD : '#1B1420'); }
  P(0, 230, 360, 100, '#1B1420');
  // leaves in the top band, crossing on whole pixels
  for (let i = 0; i < 5; i++) { const q = ((T + i * 0.9) % 4.5) / 4.5, x = Math.round(-10 + q * 380), y = Math.round(10 + i * 14 + Math.sin(q * 12 + i) * 4); P(x, y, 3, 2, i % 2 ? ORANGE : RED); DOT(x + ((F >> 2) & 1) * 2, y - 1, i % 2 ? GOLD : ORANGE); }
  // the truck: bed walls, the tailgate down, two tail lights (the hazard blinks once a second)
  P(0, 330, 360, 87, '#4A2E1B'); P(0, 330, 360, 6, RED); P(0, 330, 360, 1, '#F09A9A'); P(0, 336, 360, 3, WINE);
  for (let x = 8; x < 360; x += 44) { P(x, 342, 30, 3, '#5A3A22'); }
  const on = Math.floor(T) % 2 === 0 && T >= 1;
  [[6, 340], [340, 340]].forEach(([x, y]) => { P(x, y, 14, 10, INK); P(x + 1, y + 1, 12, 8, on ? ORANGE : WINE); if (on) DOT(x + 2, y + 2, CREAM); });
  // the clipboard: board, clip, paper; it rises from below
  const dy = o.riseAt != null ? d.ease(o.riseAt, 10, 260) : 0, Y = (y) => y + dy;
  d.bevel(16, Y(92), 328, 236, '#8C5A33', '#D9A066', '#4A2E1B', INK);
  P(24, Y(100), 312, 220, CREAM); P(24, Y(318), 312, 2, SAND); P(334, Y(100), 2, 220, SAND);
  const fl = ((F >> 4) % 5) === 0 ? 1 : 0;   // the paper corner lifts a pixel now and then
  P(326 - fl, Y(310) - fl, 10 + fl, 10 + fl, SAND); d.line(326 - fl, Y(319), 335, Y(310) - fl, '#B39A88');
  P(148, Y(84), 64, 16, '#4A4E5A'); P(148, Y(84), 64, 2, '#C9CCD3'); P(160, Y(80), 40, 6, '#6B7080'); d.disc(180, Y(83), 3, '#9AA0AD');
  return dy;
};

// ================================================================================================================
// the tag close-up (hook, "one" to "Top"): the cut in on the one price (IMPROVE 00a). The hook rides on a title plate up
// top with its source; below it the price tag drawn big on its string over the toolbox on the counter, the shop's shelves
// big behind, the counter front to the bottom of the frame; Snow steps up big (a reframe, not a backdrop swap). The tag
// sways a pixel; a twinkle walks its corner.
const closeup = (k) => {
  const d = px(k), {P, DOT, F} = d, n = k.data.numbers;
  // the shop behind the glass: plum wall, uprights, two shelves of stock drawn big
  P(0, 0, 360, 417, '#3D2E45'); for (let x = 0; x < 360; x += 60) P(x, 40, 3, 262, '#2B2033');
  [[206, 0], [300, 1]].forEach(([y, sh]) => { P(0, y, 360, 7, '#B07A47'); P(0, y, 360, 1, GOLD); P(0, y + 7, 360, 2, '#4A2E1B');
    for (let x = 4 + sh * 22; x < 356; x += 46) { const c = [TEAL, ORANGE, '#87CEEB', RED][Math.floor(hash(x + y) * 4)]; P(x, y - 30, 30, 30, c); P(x, y - 30, 30, 2, CREAM); P(x + 26, y - 28, 4, 28, INK); } });
  // the awning, big: stripes and a scalloped edge (above the safe area: art only)
  for (let x = 0; x < 360; x += 40) { P(x, 0, 20, 30, RED); P(x + 20, 0, 20, 30, CREAM); }
  for (let x = 0; x < 360; x += 20) { d.disc(x + 10, 31, 8, (x / 20) % 2 ? CREAM : RED); }
  // the title plate: the hook and its source, held from the cover (frame y 258 to 486)
  d.win(14, 86, 332, 76, {base: '#253048', hi: '#3B82C4', lo: '#1B1420', rule: '#3B82C4'});
  k.text('Top shops usually', 540, 276, {size: 66, color: CREAM, align: 'center', drop: INK});
  const a = 'quote ', b = n.tiers.shown, c = ' prices', wa = k.measure(a, {size: 66}), wb = k.measure(b, {size: 66}), x0 = 540 - (wa + wb + k.measure(c, {size: 66})) / 2;
  k.text(a, x0, 352, {size: 66, color: CREAM, drop: INK}); k.text(b, x0 + wa, 352, {size: 66, color: GOLD, drop: INK}); k.text(c, x0 + wa + wb, 352, {size: 66, color: CREAM, drop: INK});
  k.text(`ServiceTitan data, ${n.stMonths.shown} months to Jan ${n.stYear.shown}`, 540, 432, {size: 30, color: SAND, align: 'center'});
  // the counter and the toolbox on it, big
  /* the counter front fills the frame to the bottom (no bare floor): two rows of big panels, brass pulls, a kick plate */
  P(0, 302, 360, 10, '#D9A066'); P(0, 302, 360, 2, GOLD); P(0, 312, 360, 3, '#6B4226'); P(0, 315, 360, 325, '#8C5A33');
  for (let x = 6; x < 360; x += 70) [[324, 120], [452, 150]].forEach(([y, h]) => { d.bevel(x, y, 60, h, '#8C5A33', '#B07A47', '#4A2E1B'); P(x + 6, y + 6, 48, h - 12, '#6B4226'); P(x + 26, y + 12, 8, 3, GOLD); P(x + 26, y + 15, 8, 1, '#B07A47'); });
  P(0, 608, 360, 32, '#4A2E1B'); P(0, 608, 360, 2, '#B07A47');
  P(109, 265, 142, 38, INK); P(110, 266, 140, 36, RED); P(110, 266, 140, 3, ORANGE); P(226, 269, 24, 33, '#7A3442'); P(110, 284, 140, 3, '#7A3442'); P(170, 280, 20, 12, '#C9CCD3'); P(170, 280, 20, 2, CREAM);
  P(150, 254, 60, 4, '#4A4E5A'); P(150, 254, 4, 12, '#4A4E5A'); P(206, 254, 4, 12, '#4A4E5A');
  // the tag on its string, swaying a pixel; one price on it
  const sw = [0, 1, 0, -1][Math.floor(F / 8) % 4], cx = 180 + sw;
  d.line(180, 162, cx, 176, SAND);
  P(cx - 61, 175, 122, 78, INK); P(cx - 60, 176, 120, 76, CREAM); P(cx - 60, 176, 120, 2, '#FFFFFF'); P(cx - 60, 248, 120, 4, SAND); P(cx - 2, 180, 5, 5, INK);
  k.text('$', cx * 3, 549, {size: 198, color: '#7A3442', align: 'center'});
  const f = F % 24; if (f < 12) d.twinkle(cx + 56, 180, f >> 1, GOLD);
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 4',
  transitions: {stakes: 'dissolve', why: 'levelselect', card: 'dissolve', survey: 'levelselect', close: 'gameover'},
  sections: {
    // ---- hook: three shots (IMPROVE 00a: the picture changes by 1 s and twice by 3 s, Snow on by 1 s). The cover: the
    // storefront, settled on frame 0: one price on the tag, the hook card hung on the counter front. Cut in on "one" to the
    // tag close-up (the hook on a title plate), Snow comes in; cut back out on "Top"; the tag flips to three on "three".
    // The dialog box stays out through the hook (the card carries the words); Snow stays on from the cut in.
    hook: (k, T) => {
      const n = k.data.numbers, d = px(k), tThree = wordT(k, 'hook.three', /^three/i, 0.6), tBuild = k.S('hook.build');
      const tIn = Math.min(0.8, Math.max(0.5, wordT(k, 'hook', /^one$/i, 0.6))), tOut = Math.min(2.6, Math.max(tIn + 0.6, wordT(k, 'hook', /^top$/i, 1.8)));
      /* a real reframe: Snow steps up big at the counter for the close-up (hostScale 0.86), back to his wide size after */
      if (T >= tIn && T < tOut) { closeup(k); return Object.assign(host(k), {hostScale: 0.86, hostX: 200, speech: false}); }
      storefront(k, {tags: [{price: '$', at: -1}, {price: '$ $$ $$$', at: tThree}], threeAt: tThree,
        chalk: T < tBuild ? [[`${n.single.shown} price?`, -1, CREAM, 450]] : [[`${n.tiers.shown} prices,`, tBuild, GOLD, 450], [`${n.single.shown} quote.`, tBuild + 0.3, CREAM, 528]]});
      // the hook card: cream, on two strings from the counter top (frame x 102 to 978, y 780 to 1158); no dialog in the hook
      // the card swings a pixel on its strings from 0.6 s (the cover holds still on frame 0), two steps a second
      const sw = T >= 0.6 ? [0, 1, 0, -1][Math.floor(d.F / 15) % 4] : 0;
      /* motion before 1 s that crosses no words: a chalk line draws under "1 price?" from 0.5 s */
      if (T < tBuild && T >= 0.5) d.P(26, 175, Math.round(k.measure(`${n.single.shown} price?`, {size: 66}) / 3 * clamp(d.fr(0.5) / 8)), 1, SAND);
      /* sparks off the price tag into the shelves, before the card is drawn and kept off the tag, chalk board, OPEN sign
         and card: at 0.4 s, every 0.6 s until the tag flips, and as it lands on three prices */
      const tagBox = T < tThree + 0.3 ? [672, 400, 900, 606] : [627, 400, 945, 540];
      const avoid = [tagBox, [36, 402, 492, 654], [880, 552, 1026, 654], [96, 774, 984, 1164]];
      spray(k, 786, 612, 0.4, {n: 14, r: 140, dir: Math.PI / 2, spread: 2.4, avoid});
      [1.0, 1.6, 2.2, 2.8].forEach((t, i) => { if (t < tThree - 0.2) spray(k, i % 2 ? 912 : 660, 470, t, {n: 10, r: 120, dir: i % 2 ? 0 : Math.PI, spread: 1.6, avoid}); });
      spray(k, 786, 548, tThree + 0.3, {n: 18, r: 170, dir: Math.PI / 2, spread: 2.6, avoid});
      d.line(60, 252, 60 + sw, 260, SAND); d.line(300, 252, 300 + sw, 260, SAND);
      k.ctx.save(); k.ctx.translate(sw * 3, 0);
      d.P(36, 262, 292, 126, INK); d.P(34, 260, 292, 126, INK); d.P(35, 261, 290, 124, CREAM); d.P(35, 383, 290, 2, SAND); d.P(35, 261, 290, 1, '#FFFFFF');
      /* the on-screen hook in 6 words ("Top shops usually quote 3 prices"), then the number behind it and the source; the
         small lines sit right of centre so Snow (from the cut in) never stands on them */
      const l2 = `${n.tiers.shown} prices`, l3 = `Top ${n.topPct.shown}: ${n.topGbb.shown} of home jobs`;
      const x2 = 540 - k.measure(l2, {size: 132}) / 2, x3 = 590 - k.measure(l3, {size: 39}) / 2;
      /* no shine on the cream card: the kit's shine paints plum letters cream, which read as holes */
      k.slam('Top shops usually quote', 540, 798, -1, {size: 66, color: PLUM, align: 'center', glint: false});
      k.slam(l2, x2, 872, -1, {size: 132, color: PLUM, glint: false});
      k.text(n.tiers.shown, x2, 872, {size: 132, color: RED, lint: false});
      k.text(l3, x3, 1022, {size: 39, color: PLUM});
      k.text(n.topGbb.shown, x3 + k.measure(`Top ${n.topPct.shown}: `, {size: 39}), 1022, {size: 39, color: RED, lint: false});
      k.text(`ServiceTitan, ${n.stMonths.shown} months to Jan ${n.stYear.shown}`, 590, 1086, {size: 30, color: '#6B7080', align: 'center'});
      k.ctx.restore();
      if (T < tIn) return {host: false, speech: false};
      return Object.assign(host(k), {speech: false});
    },

    // ---- stakes: the high-score table. Rows land as they are said; the habit line takes the NEW RECORD slot
    stakes: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('stakes'), tTop = k.S('stakes.top'), t57 = wordT(k, 'stakes.top57', /^fifty/i);
      const tRest = wordT(k, 'stakes.rest', /^Everyone/i), t41 = wordT(k, 'stakes.rest', /^Forty/i, 1), tHab = k.S('stakes.habit');
      const gap = Math.max(0.3, tRest - tTop), score = (at) => (T < at - LEAD ? ((d.F >> 3) & 1 ? '--' : '') : '');
      k.sets.scores({title: 'GOOD, BETTER, BEST', t0: tTop, gap,
        rows: [{name: `TOP ${n.topPct.shown}`, value: score(t57), hi: true}, {name: 'THE REST', value: score(t41)}],
        newAt: tHab, newText: 'A HABIT YOU CAN COPY'});
      /* the two scores at headline size in the SCORE column (gold, teal), sliding with their rows; twinkles at the box
         corners once each number has been read, never on it */
      [[n.topGbb, t57, GOLD], [n.restGbb, t41, TEAL]].forEach(([num, at, c], i) => {
        if (T < at - LEAD) return;
        const y = 150 + i * 24, x1 = 306 + d.ease(tTop + i * gap, 5, 40), w = Math.ceil(k.measure(`${num.shown}`, {size: 66}) / 3);
        k.text(pct(k, num, at), x1 * 3, y * 3 - 12, {size: 66, color: c, align: 'right'});
        sparkle(k, [[x1 + 4, y - 5], [x1 - w - 5, y + 18], [x1 + 4, y + 18]], at + 0.45, c);
      });
      // under the table, on the black glass: what the score is, then the source, typing on (left edge 120)
      d.type('Home jobs offered good, better, best.', 120, 612, t0 + 0.1, {color: CREAM});
      d.type('ServiceTitan customers,', 120, 660, t0 + 0.6, {color: SAND});
      d.type(`${n.stMonths.shown} months to Jan ${n.stYear.shown}`, 120, 708, k.S('stakes.window'), {color: SAND});
      d.type(`Top ${n.topPct.shown} = by revenue in their trade`, 120, 756, tTop + 0.2, {color: TEAL});
      return host(k, k.live('stakes.habit') ? 'point' : (k.live('stakes.top57') ? 'point' : null));
    },

    // ---- why: the street. 1,100+ homeowners; 68 of 100 houses light and send out envelopes; then the three-price quote
    why: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('why'), tH = k.S('why.hcp'), t68 = wordT(k, 'why.68', /^sixty/i);
      const tQ = k.S('why.quotes'), t3 = k.S('why.three');
      const tCheap = wordT(k, 'why.three', /^cheaper/i, 0.9);
      street(k, {banner: [{text: `WHY ${n.tiers.shown} PRICES?`, at: t0 + 0.1}, {text: `HOUSECALL PRO SURVEY, ${n.hcpYear.shown}`, at: tH}],
        lit: n.hcpShop.value, litAt: t68, envAt: tQ, envEnd: t3 + 0.3, dimAt: t3});
      // a quote envelope flies in across the rooftops as the question is asked, and lands on the first house
      if (T >= t0 && T < t0 + 1.2) { const q = eo((T - t0) / 0.8), x = Math.round(-10 + q * (HX(0) + 14)), y = Math.round(96 + q * (HY(0) - 100)); d.P(x - 1, y - 1, 10, 8, INK); d.P(x, y, 8, 6, CREAM); d.line(x, y, x + 4, y + 3, SAND); d.line(x + 7, y, x + 4, y + 3, SAND); }
      // the plate (frame y 789 to 972), one idea at a time
      if (T < tH) k.slam(`Why ${n.tiers.shown}?`, 540, 840, t0 + 0.2, {size: 66, color: CREAM, align: 'center', from: 0.5});
      else if (T < t68 - LEAD) k.slam(`${k.count(n.hcpN.value, clamp((T - tH - 0.1) / 0.8), {from: n.hcpN.value * 0.85, comma: true})}+ homeowners`, 540, 840, tH + 0.1, {size: 66, color: GOLD, align: 'center', from: 0.5});
      else if (T < t3) {
        k.slam(pct(k, n.hcpShop, t68), 66, 820, t68 - LEAD, {size: 132, color: 'accent', from: 0.5});
        const w68 = Math.ceil(k.measure(`${n.hcpShop.shown}`, {size: 132}) / 3);
        sparkle(k, [[22 + w68 + 4, 272], [22 + w68 + 4, 318], [19, 318]], t68 + 0.45);
        d.type(`of ${n.hcpN.shown}+ homeowners`, 312, 816, t68 + 0.4, {color: CREAM});
        d.type('get more quotes when a', 312, 860, tQ, {color: CREAM});
        d.type('price is higher than expected.', 312, 904, tQ + 0.5, {color: GOLD});
      } else {
        k.slam("There's a cheaper option", 72, 806, t3 + 0.1, {size: 66, color: CREAM, from: 0.5});
        if (T >= tCheap) k.slam('already on your quote.', 72, 884, tCheap + 0.4, {size: 66, color: TEAL, from: 0.5});
      }
      // the three-price quote: slides in from the left; the cheaper row glows teal and gets a check on "cheaper"
      if (T >= t3) {
        const x = 100 - d.ease(t3, 8, 260), y = 126;
        d.clip(0, 84, 360, 176, () => slip(k, x, y, 160, 124, (sx, sy) => {
          d.P(sx, sy, 160, 18, '#2F6F67'); d.tx('YOUR QUOTE', sx + 80, sy + 3, {color: CREAM, align: 'center', lint: x === 100});
          [['GOOD', '$'], ['BETTER', '$$'], ['BEST', '$$$']].forEach(([nm, pr], i) => {
            const ry = sy + 24 + i * 32, hot = i === 0 && T >= tCheap;
            if (hot) { d.P(sx + 4, ry - 2, 152, 28, '#BDE6F5'); d.P(sx + 4, ry - 2, 3, 28, TEAL); }
            if (i === 1) d.P(sx + 4, ry - 2, 152, 28, '#F4E6D3');
            d.tx(nm, sx + 10, ry + 5, {color: PLUM, lint: x === 100});
            d.tx(pr, sx + 150, ry, {size: 66, color: hot ? '#2F6F67' : WINE, align: 'right', lint: x === 100});
            if (i < 2) d.P(sx + 6, ry + 27, 148, 1, SAND);
          });
          if (T >= tCheap) { const f = d.fr(tCheap), pts = [[0, 4], [1, 5], [2, 6], [3, 7], [4, 6], [5, 5], [6, 4], [7, 3], [8, 2], [9, 1], [10, 0]]; pts.slice(0, Math.min(pts.length, f + 1)).forEach(([a, b]) => d.P(sx + 62 + a, sy + 30 + b, 2, 2, '#2F6F67')); }
        }));
        spray(k, 800, 430, tCheap + 0.2, {n: 14, r: 180, dir: 0, spread: 2.0, colors: [TEAL, GOLD, CREAM], avoid: [[288, 366, 795, 762], [48, 255, 1032, 336]]});
      }
      return host(k, k.live('why.68') || k.live('why.three') ? 'point' : null);
    },

    // ---- card: the clipboard on the tailgate; the three rows land as they are said, the BEST upgrades light word by word
    card: (k, T) => {
      const t0 = k.S('card'), d = px(k);
      const dy = tailgate(k, {riseAt: t0});
      if (dy !== 0) return host(k);
      // the header band (dark), then the rows (frame left edge 108, prices right at 930)
      d.P(26, 102, 308, 16, PLUM);
      /* each row's sparks draw first, so every word on the card draws over them */
      ['card.good', 'card.better', 'card.best'].forEach((id, i) => spray(k, 110, 372 + i * 196 + 30, k.S(id) + 0.05, {n: 12, r: 160, colors: [ORANGE, GOLD, TEAL]}));
      d.type('YOUR QUOTE (EXAMPLE)', 108, 312, t0 + 0.35, {color: CREAM});
      const rows = [
        {id: 'card.good', name: 'Good', price: '$', l1: 'The job done right.', l2: 'Nothing extra.'},
        {id: 'card.better', name: 'Better', price: '$$', l1: "What you'd pick for", l2: 'your own house.'},
        {id: 'card.best', name: 'Best', price: '$$$', l1: 'Plus upgrades:', l2: null},
      ];
      rows.forEach((r, i) => {
        const y = 372 + i * 196, at = k.S(r.id);
        if (i < 2) d.P(30, (y + 172) / 3, 300, 1, SAND);
        if (T < at) { d.P(36, (y + 26) / 3, 40, 3, SAND); d.P(36, (y + 90) / 3, 120 + i * 20, 2, '#F4E6D3'); return; }   // an empty row's guide marks
        const sl = d.ease(at, 6, 40) * 3;
        k.ctx.save(); k.ctx.translate(sl, 0);
        if (i === 1) { d.P(28, (y - 12) / 3, 304, 60, GOLD); d.P(28, (y - 12) / 3, 304, 1, '#FFFFFF'); }
        k.text(r.name, 108, y, {size: 66, color: i === 1 ? WINE : PLUM});
        k.text(r.price, 930, y, {size: 66, color: i === 1 ? WINE : '#2F6F67', align: 'right'});
        k.text(r.l1, 108, y + 76, {size: 39, color: PLUM});
        if (r.l2) k.text(r.l2, 108, y + 118, {size: 39, color: PLUM});
        k.ctx.restore();
        if (i === 1 && T >= at + 0.4) { k.ctx.save(); k.ctx.translate(d.ease(at + 0.4, 5, 30) * 3, 0); k.chip('The middle', 300, y + 8, {size: 30}); k.ctx.restore(); }
      });
      // BEST's upgrades, each word lit gold while it is said, then plum
      const tw0 = k.S('card.warranty'), y3 = 372 + 2 * 196 + 118;
      if (T >= tw0 - 0.05) {
        const show = 'longer warranty, faster start date.', said = 'longer warranty or a faster start date.';
        const times = spoken(tw0, said), map = [0, 1, 4, 5, 6], words = show.split(' ');
        let x = 108; const sp = k.measure(' ', {size: 39});
        words.forEach((wd, j) => { const [ws, we] = times[map[j]] || [1e9, 1e9]; if (T >= ws) k.text(wd, x, y3, {size: 39, color: T < we + 0.1 ? '#B4523A' : PLUM}); else d.P(x / 3, (y3 + 33) / 3, k.measure(wd, {size: 39}) / 3, 1, SAND); x += k.measure(wd, {size: 39}) + sp; });
      }
      return host(k);
    },

    // ---- survey: the slot machine. 4+ options lands 5 2 %, 1 to 3 lands 4 2 %, the reels roll to 1 2 3 and get bracketed
    // as one group, then "Start with three" lands 3 3 3 with coins
    survey: (k, T) => {
      const n = k.data.numbers, d = px(k);
      const t0 = k.S('survey'), tCeil = k.S('survey.ceiling'), tGrp = k.S('survey.group'), tN = k.S('survey.n');
      const tFour = wordT(k, 'survey.pull', /^four/i, 0.5), t52 = wordT(k, 'survey.52', /^fifty/i), tP52 = wordT(k, 'survey.52', /^percent/i, 0.5);
      const tOpt = wordT(k, 'survey.few', /^three/i, 0.3), t42 = wordT(k, 'survey.few', /^Forty/i, 1.0);
      const tCav = k.S('survey.caveat'), tCant = k.S('survey.cant'), tStart = k.S('survey.start'), tThree = wordT(k, 'survey.start', /^three/i, 0.3);
      const dig = (num) => String(num.value).split('');
      let reel;
      if (T < tOpt) reel = {t0: tFour, stops: [t52, t52 + 0.25, Math.max(t52 + 0.4, tP52)], symbols: [...dig(n.manyClose), '%'], win: false};
      else if (T < tCav) reel = {t0: tOpt, stops: [t42, t42 + 0.2, t42 + 0.45], symbols: [...dig(n.fewClose), '%'], win: false};
      else if (T < tStart) reel = {t0: tCav + 0.1, stops: [tCav + 0.6, tCav + 0.8, tCav + 1.0], symbols: [n.single.shown, '2', n.fewMax.shown], win: false};
      else reel = {t0: tStart, stops: [tThree, tThree + 0.15, tThree + 0.3], symbols: [n.tiers.shown, n.tiers.shown, n.tiers.shown], win: true};
      const label = T >= tStart ? `START WITH ${n.tiers.shown}` : T >= tCav ? `${n.single.shown}, 2 AND ${n.fewMax.shown}: ONE GROUP`
        : T >= tOpt ? `${n.single.shown} TO ${n.fewMax.shown} OPTIONS: CLOSE RATE` : T >= tFour ? `${n.manyOpt.shown}+ OPTIONS: CLOSE RATE` : T >= tCeil ? `${n.tiers.shown} IS THE FLOOR` : 'THE PART PEOPLE SKIP';
      k.sets.slots(Object.assign({label, idle: ['$', '$', '$']}, reel));
      // sparks as the numbers land
      /* out of the cabinet's sides, never over the reels or the words */
      const cab = [[114, 246, 906, 966]], sn = reel.win ? 16 : 9;
      spray(k, 105, 520, reel.stops[2] + 0.05, {n: sn, r: 110, dir: Math.PI, spread: 1.6, avoid: cab});
      spray(k, 975, 520, reel.stops[2] + 0.05, {n: sn, r: 110, dir: 0, spread: 1.6, avoid: cab});
      // the bracket: 1, 2 and 3 clamped as one group (under the reels, above the tray)
      if (T >= tCav + 1.0 && T < tStart) { const f = d.fr(tCav + 1.0), w = Math.min(224, f * 28); d.P(170 - w / 2, 232, w, 3, GOLD); if (w >= 224) { d.P(58, 228, 3, 7, GOLD); d.P(279, 228, 3, 7, GOLD); d.P(168, 234, 5, 4, GOLD); } }
      // the strip on the cabinet front: the source, once the survey is named (frame y 909)
      d.P(52, 300, 236, 18, INK); d.P(53, 301, 234, 16, '#2B2033');
      d.type(`ACCA survey, ACHR News, Feb ${n.accaYear.shown}`, 510, 906, tGrp, {color: SAND, align: 'center'});
      // the tray: two lines (frame y 750 and 810, centered at 510), nothing once the coins come
      const tray = (a, b) => { if (a) d.type(a[0], 510, 750, a[1], {color: a[2] || CREAM, align: 'center'}); if (b) d.type(b[0], 510, 810, b[1], {color: b[2] || CREAM, align: 'center'}); };
      if (T < tN) tray(['How many options', t0 + 0.3], ['do you give?', t0 + 0.6, GOLD]);
      else if (T < tP52 + 0.2) tray([`${n.accaN.shown}+ HVAC contractors`, tN, GOLD], T >= tFour ? ['close rate by options given', tFour] : null);
      else if (T < t42) tray([`${n.manyOpt.shown}+ options: ${n.manyClose.shown}`, tP52 + 0.2, GOLD], [`Only ${n.accaShare.shown} offer ${n.manyOpt.shown}+.`, tP52 + 0.5]);
      else if (T < tCav) tray([`${n.manyOpt.shown}+ options: ${n.manyClose.shown}`, -1, GOLD], [`${n.single.shown} to ${n.fewMax.shown} options: ${n.fewClose.shown}`, t42 + 0.3]);
      else if (T < tStart) tray([`${n.single.shown} to ${n.fewMax.shown} options: one group here.`, tCav + 0.3], T >= tCant ? [`It can't show ${n.fewMax.shown} beats ${n.single.shown}.`, tCant, RED] : null);
      /* the jackpot's label: the tray's top band carries the line, the coins pile and hop under it */
      else { d.P(62, 248, 216, 15, '#2B2033'); d.type(`Start with ${n.tiers.shown} prices.`, 510, 747, tStart, {color: GOLD, align: 'center'}); }
      return host(k, k.live('survey.caveat') ? 'clip' : (k.live('survey.52') || k.live('survey.start') ? 'point' : null));
    },

    // ---- close: the storefront again. One column on a dark plate (left edge 120): the send line first, then the line
    // and the payoff; the tag flips to three prices on "Three"
    close: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('close'), tOne = k.S('close.one'), tYes = wordT(k, 'close.one', /^yes/i, 0.6), tThree = wordT(k, 'close.choice', /^Three/i);
      const tCh = wordT(k, 'close.choice', /^choice/i, 0.9);
      storefront(k, {tags: [{price: '$', at: -1}, {price: '$ $$ $$$', at: tThree}], threeAt: tThree,
        chalk: T < tThree ? [[`${n.single.shown} price?`, tOne, CREAM, 450]] : [[`${n.tiers.shown} prices.`, tThree, GOLD, 450]]});
      /* the plate holds four lines at one size (66): the send line on two lines, the line, the payoff */
      const open = d.ease(t0 + 0.05, 8, 120);
      d.clip(0, 227, 360, 190, () => d.win(30, 227 + open, 300, 108, {base: '#1B1420', hi: PLUM, lo: INK, rule: WINE}));
      if (open === 0) {
        k.slam('Send this to whoever', 120, 696, t0 + 0.3, {size: 66, color: GOLD, from: 0.4});
        k.slam('writes your quotes.', 120, 768, t0 + 0.6, {size: 66, color: GOLD, from: 0.4});
        if (T >= tOne) k.slam(`${n.single.shown} price: yes or no.`, 120, 846, Math.min(tOne + 0.2, tYes), {size: 66, color: CREAM, from: 0.5});
        if (T >= tThree) k.slam(`${n.tiers.shown} prices: a choice.`, 120, 918, tThree + 0.1, {size: 66, color: 'accent', from: 0.5});   /* on "Three", so it holds past the last word */
        if (T >= tCh + 0.3) { const x = 120 + k.measure(`${n.tiers.shown} prices: `, {size: 66}); k.sweep(x, 987, k.measure('a choice.', {size: 66}), 6, tCh + 0.3, {color: 'accent'}); }
      }
      k.chip('ProofNotFluff', 78, 540, {size: 30});
      /* sparks off the tag's foot into the shelves, kept off the tag, chalk board, OPEN sign and plate */
      const avoid = [[627, 400, 945, 540], [36, 402, 492, 654], [880, 552, 1026, 654], [84, 675, 996, 1011]];
      spray(k, 786, 548, tThree + 0.35, {n: 18, r: 170, dir: Math.PI / 2, spread: 2.6, avoid});
      spray(k, 786, 548, tCh + 0.3, {n: 14, r: 150, dir: Math.PI / 2, spread: 2.6, colors: [GOLD, CREAM], avoid});
      return host(k, T >= tCh ? 'wave' : (T < tOne ? 'point' : null));
    },
  },
};
