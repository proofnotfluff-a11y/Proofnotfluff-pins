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
    if (o.maxY != null && (fy + sz) * 3 > o.maxY) continue;
    P(fx, fy, sz, sz, cols[i % cols.length]);
  }
};
/* twinkles that sit just outside a number's box (low-res points), one after another, for a second */
const sparkle = (k, pts, at, c = GOLD) => {
  const d = px(k), f = d.fr(at); if (f < 0 || f >= 30) return;
  pts.forEach(([x, y], j) => { const g = f - j * 4; if (g >= 0 && g < 20) d.twinkle(x, y, g, c); });
};
const host = (k, pose) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150});
/* the counter's tag flip shows its new price 8 frames after it starts, so a flip that should land on a word starts
   FLIP s before it */
const FLIP = 8 / 30;

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
  /* the banner's line at the label floor (size 66): its caps sit at frame y 282 to 315 in the cloth (261 to 333) */
  const ban = (o.banner || []).filter((b) => T >= b.at).pop();
  if (ban) d.type(ban.text, 540, 267, ban.at, {size: 66, color: GOLD, align: 'center'});
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
// the tag close-up (hook, "one" to "Top"): the cut in on the one price (IMPROVE 00a). Outside the shop, drawn big: the
// awning up top, the brick facade, the shop window with the price tag hanging in the glass over the toolbox on the
// display ledge, the door with its OPEN sign, the sidewalk in the awning's shade. The hook rides on a title plate over the
// glass with its source; Snow steps up big on the sidewalk (a reframe, not a backdrop swap). The tag sways a pixel, a
// glint crosses the glass, a twinkle walks the tag's corner.
const closeup = (k) => {
  const d = px(k), {P, F} = d, n = k.data.numbers;
  // the facade: big brick, wine mortar
  P(0, 0, 360, 312, '#7A3442');
  for (let y = 40, r = 0; y < 302; y += 8, r++) for (let x = (r & 1) ? -12 : 0; x < 360; x += 24) P(x, y, 23, 7, RED);
  // the shop window: a dark wood frame, the glass (dusk blue, a darker street reflection low down)
  P(4, 48, 252, 256, INK); d.bevel(6, 50, 248, 252, '#6B4226', '#B07A47', '#4A2E1B');
  P(14, 58, 232, 222, '#253048'); d.dith(14, 236, 232, 44, '#1B2A40', 0);
  /* a light that crosses the glass every 2.4 s on whole pixels, plus two still glints */
  d.clip(14, 58, 232, 222, () => {
    d.line(20, 270, 116, 62, '#2F3D5C', 6); d.line(40, 276, 132, 78, '#33476B', 2);
    const g = Math.round(((F % 72) / 72) * 420) - 120; d.line(g, 278, g + 100, 58, '#3B82C4', 3); d.line(g + 10, 278, g + 110, 58, '#2F3D5C', 2);
  });
  // the display ledge and the toolbox on it (under the tag)
  P(14, 280, 232, 6, '#B07A47'); P(14, 280, 232, 1, GOLD); P(14, 286, 232, 2, '#4A2E1B');
  P(150, 246, 60, 3, '#4A4E5A'); P(150, 246, 3, 9, '#4A4E5A'); P(207, 246, 3, 9, '#4A4E5A');
  P(129, 253, 102, 28, INK); P(130, 254, 100, 26, RED); P(130, 254, 100, 2, ORANGE); P(212, 256, 18, 24, '#7A3442'); P(130, 266, 100, 2, '#7A3442'); P(172, 262, 16, 8, '#C9CCD3'); P(172, 262, 16, 2, CREAM);
  // the door: teal, a glass pane with the OPEN sign hung in it (glowing on and off once a second), a brass knob, a kick plate
  P(258, 42, 98, 262, INK); d.bevel(262, 46, 92, 256, '#2F6F67', TEAL, '#1F4A44');
  P(272, 56, 72, 146, '#253048'); P(272, 56, 72, 2, '#1B2A40'); d.line(276, 196, 338, 70, '#2F3D5C', 3);
  P(278, 212, 60, 70, '#1F4A44'); d.bevel(280, 214, 56, 66, '#2F6F67', TEAL, '#1F4A44');
  d.disc(270, 230, 3, GOLD); P(269, 229, 1, 1, CREAM); P(264, 288, 88, 12, '#C9CCD3'); P(264, 288, 88, 1, CREAM);
  const on = Math.floor(k.T) % 2 === 0 || k.T < 1;
  d.line(300, 162, 308, 170, SAND); d.line(316, 162, 308, 170, SAND);
  P(285, 170, 48, 24, INK); P(286, 171, 46, 22, '#2B2033'); k.text('OPEN', 927, 522, {size: 39, color: on ? RED : '#7A3442', align: 'center', lint: false});
  // the stone base course, the sidewalk in the awning's shade (big joints), the curb and the street
  P(0, 302, 360, 10, '#9AA0AD'); P(0, 302, 360, 2, '#C9CCD3'); P(0, 311, 360, 1, '#4A4E5A');
  P(0, 312, 360, 208, '#6B7080'); d.dith(0, 312, 360, 16, '#4A4E5A', 0);
  for (let y = 360, r = 0; y < 520; y += 48, r++) { P(0, y, 360, 2, '#4A4E5A'); for (let x = (r & 1) ? 45 : 0; x < 360; x += 90) P(x, y - 48, 2, 48, '#4A4E5A'); }
  P(0, 520, 360, 8, '#C9CCD3'); P(0, 520, 360, 2, CREAM); P(0, 528, 360, 4, '#4A4E5A'); P(0, 532, 360, 108, '#2B2033');
  for (let x = 10; x < 360; x += 70) P(x, 588, 36, 4, GOLD);
  // a sandwich board on the sidewalk by the door: a chalk face with three bars, short to tall
  d.dith(262, 424, 70, 4, '#4A4E5A', 1);
  P(268, 412, 4, 14, '#4A2E1B'); P(322, 412, 4, 14, '#4A2E1B');
  P(265, 333, 64, 82, INK); d.bevel(266, 334, 62, 80, '#8C5A33', '#D9A066', '#4A2E1B'); P(272, 340, 50, 68, '#24453A'); P(272, 340, 50, 1, '#1A332B');
  P(279, 349, 36, 2, CREAM); P(279, 357, 24, 2, SAND);
  [[281, 10, CREAM], [293, 18, GOLD], [305, 26, CREAM]].forEach(([x, h, c]) => P(x, 400 - h, 8, h, c));
  // the awning, big: stripes and a scalloped edge (above the safe area: art only)
  for (let x = 0; x < 360; x += 40) { P(x, 0, 20, 30, RED); P(x + 20, 0, 20, 30, CREAM); }
  for (let x = 0; x < 360; x += 20) { d.disc(x + 10, 31, 8, (x / 20) % 2 ? CREAM : RED); }
  // the title plate: the hook and its source, held from the cover (frame y 258 to 486)
  d.win(14, 86, 332, 76, {base: '#253048', hi: '#3B82C4', lo: '#1B1420', rule: '#3B82C4'});
  k.text('Top shops usually', 540, 276, {size: 66, color: CREAM, align: 'center', drop: INK});
  const a = 'quote ', b = n.tiers.shown, c = ' prices', wa = k.measure(a, {size: 66}), wb = k.measure(b, {size: 66}), x0 = 540 - (wa + wb + k.measure(c, {size: 66})) / 2;
  k.text(a, x0, 352, {size: 66, color: CREAM, drop: INK}); k.text(b, x0 + wa, 352, {size: 66, color: GOLD, drop: INK}); k.text(c, x0 + wa + wb, 352, {size: 66, color: CREAM, drop: INK});
  k.text(`ServiceTitan data, ${n.stMonths.shown} months to Jan ${n.stYear.shown}`, 540, 432, {size: 30, color: SAND, align: 'center'});
  // the tag on its string, hanging in the window and swaying a pixel; one price on it
  const sw = [0, 1, 0, -1][Math.floor(F / 8) % 4], cx = 180 + sw;
  d.line(180, 162, cx, 176, SAND);
  P(cx - 61, 175, 122, 78, INK); P(cx - 60, 176, 120, 76, CREAM); P(cx - 60, 176, 120, 2, '#FFFFFF'); P(cx - 60, 248, 120, 4, SAND); P(cx - 2, 180, 5, 5, INK);
  k.text('$', cx * 3, 549, {size: 198, color: '#7A3442', align: 'center'});
  const f = F % 24; if (f < 12) d.twinkle(cx + 56, 180, f >> 1, GOLD);
};

/* the storefront base: the brick facade from low-res y0 down to the sidewalk (y 417), courses 5 high and 12 long. The hook
   hangs its card on it under the counter top, the close hangs its plate on it under the window sill */
const brick = (k, y0) => {
  const {P} = px(k);
  P(0, y0, 360, 417 - y0, '#7A3442');
  for (let y = y0, r = 0; y < 417; y += 5, r++) for (let x = (r & 1) ? 6 : 0; x < 360; x += 12) P(x, y, 11, 4, RED);
};

/* the close's storefront has no counter front: the shop window ends at a stone sill and the brick facade runs down to the
   sidewalk, so the plate hangs on the brick. The toolbox comes off the counter (the shelf behind it is put back). */
const facade = (k) => {
  const d = px(k), {P} = d;
  P(172, 180, 58, 40, '#3D2E45'); P(200, 180, 2, 40, '#2B2033');
  [172, 194, 216].forEach((x) => { const c = [TEAL, ORANGE, '#87CEEB', RED][Math.floor(hash(x + 222) * 4)]; P(x, 208, 14, 14, c); P(x, 208, 14, 1, CREAM); P(x + 12, 209, 2, 13, INK); });
  P(0, 218, 360, 6, '#C9CCD3'); P(0, 218, 360, 1, CREAM); P(0, 223, 360, 1, '#4A4E5A');
  brick(k, 224);
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 4',
  transitions: {stakes: 'dissolve', why: 'levelselect', card: 'dissolve', survey: 'levelselect', close: 'gameover'},
  sections: {
    // ---- hook: three shots (IMPROVE 00a: the picture changes by 1 s and twice by 3 s, Snow on by 1 s). The cover: the
    // storefront, settled on frame 0: one price on the tag, the hook card hung on the brick under the counter top (the
    // close's storefront base, not the drawer cabinets). Cut in on "one" to the tag close-up outside the shop window (the
    // hook on a title plate), Snow comes in; cut back out on "Top"; the tag shows three prices on "three". The card rolls up
    // onto its strings just before "Here's" (the on-screen hook is off by 4.0 s, playbook point 2) and the chalk board
    // carries the rest. The dialog box stays out through the hook; in the wide shot Snow stays off while the card hangs
    // (he would stand on its left third) and steps back on the frame it is gone.
    hook: (k, T) => {
      const n = k.data.numbers, d = px(k), tThree = wordT(k, 'hook.three', /^three/i, 0.6), tBuild = k.S('hook.build');
      const tIn = Math.min(0.8, Math.max(0.5, wordT(k, 'hook', /^one$/i, 0.6))), tOut = Math.min(2.6, Math.max(tIn + 0.6, wordT(k, 'hook', /^top$/i, 1.8)));
      /* a real reframe: Snow steps up big at the counter for the close-up (hostScale 0.86), back at his wide size once the
         card has rolled up */
      if (T >= tIn && T < tOut) { closeup(k); return Object.assign(host(k), {hostScale: 0.86, hostX: 200, speech: false}); }
      storefront(k, {tags: [{price: '$', at: -1}, {price: '$ $$ $$$', at: tThree - FLIP}], threeAt: tThree,
        chalk: T < tBuild ? [[`${n.single.shown} price?`, -1, CREAM, 450]] : [[`${n.tiers.shown} prices,`, tBuild, GOLD, 450], [`${n.single.shown} quote.`, tBuild + 0.3, CREAM, 528]]});
      /* under the counter top the brick facade runs down to the sidewalk (the close's base), a shadow line under the lip */
      brick(k, 259); d.P(0, 259, 360, 1, '#4A2E1B');
      // the hook card: cream, on two strings from the counter top (frame x 102 to 978, y 780 to 1158); no dialog in the hook
      // the card swings a pixel on its strings from 0.6 s (the cover holds still on frame 0), two steps a second
      const sw = T >= 0.6 ? [0, 1, 0, -1][Math.floor(d.F / 15) % 4] : 0;
      /* the card rolls up: its bottom edge climbs to the strings over 6 frames and it is gone a frame before "Here's"
         (and by 4.0 s whatever the voice does) */
      const tGone = Math.min(tBuild, 4.0) - 1 / 30, roll = clamp((T - (tGone - 0.2)) / 0.2);
      /* motion before 1 s that crosses no words: a chalk line draws under "1 price?" from 0.5 s */
      if (T < tBuild && T >= 0.5) d.P(26, 175, Math.round(k.measure(`${n.single.shown} price?`, {size: 66}) / 3 * clamp(d.fr(0.5) / 8)), 1, SAND);
      /* sparks off the price tag into the shelves, before the card is drawn and kept off the tag, chalk board, OPEN sign
         and card: at 0.4 s, every 0.6 s until the tag flips, and as it lands on three prices */
      const tagBox = T < tThree ? [672, 400, 900, 606] : [627, 400, 945, 540];
      const avoid = [tagBox, [36, 402, 492, 654], [880, 552, 1026, 654], [96, 774, 984, 1164]];
      spray(k, 786, 612, 0.4, {n: 14, r: 140, dir: Math.PI / 2, spread: 2.4, avoid});
      [1.0, 1.6, 2.2, 2.8].forEach((t, i) => { if (t < tThree - 0.2) spray(k, i % 2 ? 912 : 660, 470, t, {n: 10, r: 120, dir: i % 2 ? 0 : Math.PI, spread: 1.6, avoid}); });
      spray(k, 786, 548, tThree + 0.3, {n: 18, r: 170, dir: Math.PI / 2, spread: 2.6, avoid});
      if (roll < 1) {
      const cb = 260 + Math.round(128 * (1 - eo(roll)));
      d.line(60, 252, 60 + sw, 260, SAND); d.line(300, 252, 300 + sw, 260, SAND);
      k.ctx.save(); k.ctx.beginPath(); k.ctx.rect(0, 756, 1080, (cb - 252) * 3); k.ctx.clip(); k.ctx.translate(sw * 3, 0);
      d.P(36, 262, 292, 126, INK); d.P(34, 260, 292, 126, INK); d.P(35, 261, 290, 124, CREAM); d.P(35, 383, 290, 2, SAND); d.P(35, 261, 290, 1, '#FFFFFF');
      /* the on-screen hook in 6 words ("Top shops usually quote 3 prices"), then the number behind it at the label floor
         (size 66) and the source; every line is centred, since Snow is off while the card hangs */
      const l2 = `${n.tiers.shown} prices`, l3 = `Top ${n.topPct.shown}: ${n.topGbb.shown} of home jobs`;
      const x2 = 540 - k.measure(l2, {size: 132}) / 2, x3 = 540 - k.measure(l3, {size: 66}) / 2;
      /* no shine on the cream card: the kit's shine paints plum letters cream, which read as holes. Once the roll has
         passed a line it is not drawn at all (so nothing of the hook is left on screen, even for the layout check) */
      const vis = (y) => cb * 3 > y + 6;
      if (vis(798)) k.slam('Top shops usually quote', 540, 798, -1, {size: 66, color: PLUM, align: 'center', glint: false});
      if (vis(872)) k.slam(l2, x2, 872, -1, {size: 132, color: PLUM, glint: false});
      if (vis(872)) k.text(n.tiers.shown, x2, 872, {size: 132, color: RED, lint: false});
      if (vis(1008)) k.text(l3, x3, 1008, {size: 66, color: PLUM});
      if (vis(1008)) k.text(n.topGbb.shown, x3 + k.measure(`Top ${n.topPct.shown}: `, {size: 66}), 1008, {size: 66, color: RED, lint: false});
      if (vis(1089)) k.text(`ServiceTitan, ${n.stMonths.shown} months to Jan ${n.stYear.shown}`, 540, 1089, {size: 30, color: '#6B7080', align: 'center'});
      k.ctx.restore();
      if (roll > 0) { d.P(34 + sw, cb - 4, 292, 5, INK); d.P(35 + sw, cb - 3, 290, 3, SAND); d.P(35 + sw, cb - 3, 290, 1, CREAM); }   // the roll
      }
      /* no host on the cover, and none in the wide shot until the card has rolled up (he would cover its left third) */
      if (T < tGone) return {host: false, speech: false};
      return Object.assign(host(k), {speech: false});
    },

    // ---- stakes: the high-score table. Rows land as they are said; the habit line takes the NEW RECORD slot
    stakes: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('stakes'), tTop = k.S('stakes.top'), t57 = wordT(k, 'stakes.top57', /^fifty/i);
      const tRest = wordT(k, 'stakes.rest', /^Everyone/i), t41 = wordT(k, 'stakes.rest', /^Forty/i, 1), tHab = k.S('stakes.habit');
      const gap = Math.max(0.3, tRest - tTop), score = (at) => (T < at - LEAD ? ((d.F >> 3) & 1 ? '--' : '') : '');
      k.sets.scores({title: 'GOOD, BETTER, BEST', t0: tTop, gap,
        rows: [{name: `TOP ${n.topPct.shown}`, value: score(t57), hi: true}, {name: 'THE REST', value: score(t41)}]});
      /* the two scores at headline size in the SCORE column (gold, teal), sliding with their rows; twinkles at the box
         corners once each number has been read, never on it */
      [[n.topGbb, t57, GOLD], [n.restGbb, t41, TEAL]].forEach(([num, at, c], i) => {
        if (T < at - LEAD) return;
        const y = 150 + i * 24, x1 = 306 + d.ease(tTop + i * gap, 5, 40), w = Math.ceil(k.measure(`${num.shown}`, {size: 66}) / 3);
        k.text(pct(k, num, at), x1 * 3, y * 3 - 12, {size: 66, color: c, align: 'right'});
        sparkle(k, [[x1 + 4, y - 5], [x1 - w - 5, y + 18], [x1 + 4, y + 18]], at + 0.45, c);
      });
      /* the payoff takes the band between the rows and the footnote, at the label floor (size 66, its caps centred in the
         bar: frame y 606 to 639 inside 591 to 654), gold, on a row's plum bar (it lands on "habit", steady, with a twinkle
         at each end) */
      if (T >= tHab) {
        const tH = wordT(k, 'stakes.habit', /^habit/i, 0.3), w = Math.ceil(k.measure('A HABIT YOU CAN COPY', {size: 66}) / 3), q = clamp(d.fr(tHab) / 6);
        d.P(32, 197, 276, 21, '#3D2E45'); d.P(32, 197, Math.round(276 * q), 1, GOLD); d.P(32, 217, Math.round(276 * q), 1, GOLD);
        if (T >= tH) { k.slam('A HABIT YOU CAN COPY', 540, 591, tH, {size: 66, color: GOLD, align: 'center', from: 0.4, glint: false}); sparkle(k, [[180 - w / 2 - 8, 207], [180 + w / 2 + 7, 207]], tH + 0.3, GOLD); }
      }
      // under the table, on the black glass: what the score is, then the source, typing on (left edge 120)
      d.type('Home jobs offered good, better, best.', 120, 684, t0 + 0.1, {color: CREAM});
      d.type('ServiceTitan customers,', 120, 732, t0 + 0.6, {color: SAND});
      d.type(`${n.stMonths.shown} months to Jan ${n.stYear.shown}`, 120, 780, k.S('stakes.window'), {color: SAND});
      d.type(`Top ${n.topPct.shown} = by revenue in their trade`, 120, 828, tTop + 0.2, {color: TEAL});
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
            d.tx(nm, sx + 10, ry, {size: 66, color: PLUM, lint: x === 100});   // the tier names at the label floor, level with the prices
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
      /* the header band (dark, along the paper's top edge: frame y 300 to 366) with its line at the label floor (size 66,
         caps at y 315 to 348), then the rows (frame left edge 108, prices right at 930) */
      d.P(26, 100, 308, 22, PLUM);
      /* each row's sparks draw first, so every word on the card draws over them */
      ['card.good', 'card.better', 'card.best'].forEach((id, i) => spray(k, 110, 372 + i * 196 + 30, k.S(id) + 0.05, {n: 12, r: 160, colors: [ORANGE, GOLD, TEAL]}));
      d.type('YOUR QUOTE (EXAMPLE)', 108, 300, t0 + 0.35, {size: 66, color: CREAM});
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
      /* the short spin on "surveyed": the lever pulls and the reels land back on $ $ $ (no sparks, no coins), so the reels
         never hold still for long before "four"; the jackpot's stops, which the crown waits for */
      const tSurv = wordT(k, 'survey.group', /^surveyed/i, 1.5), spin = [tSurv + 0.5, tSurv + 0.65, tSurv + 0.8], jack = [tThree, tThree + 0.15, tThree + 0.3];
      const dig = (num) => String(num.value).split('');
      let reel;
      if (T >= tSurv && T < spin[2]) reel = {t0: tSurv, stops: spin, symbols: ['$', '$', '$'], win: false};
      else if (T < tOpt) reel = {t0: tFour, stops: [t52, t52 + 0.25, Math.max(t52 + 0.4, tP52)], symbols: [...dig(n.manyClose), '%'], win: false};
      else if (T < tCav) reel = {t0: tOpt, stops: [t42, t42 + 0.2, t42 + 0.45], symbols: [...dig(n.fewClose), '%'], win: false};
      else if (T < tStart) reel = {t0: tCav + 0.1, stops: [tCav + 0.6, tCav + 0.8, tCav + 1.0], symbols: [n.single.shown, '2', n.fewMax.shown], win: false};
      else reel = {t0: tStart, stops: jack, symbols: [n.tiers.shown, n.tiers.shown, n.tiers.shown], win: true};
      /* the crown flips to START WITH 3 on the frame the last reel lands 3, not on "Start" */
      const label = T >= jack[2] ? `START WITH ${n.tiers.shown}` : T >= tCav ? `${n.single.shown}, 2 AND ${n.fewMax.shown}: ONE GROUP`
        : T >= tOpt ? `${n.single.shown} TO ${n.fewMax.shown} OPTIONS: CLOSE RATE` : T >= tFour ? `${n.manyOpt.shown}+ OPTIONS: CLOSE RATE` : T >= tCeil ? `${n.tiers.shown} IS THE FLOOR` : 'THE PART PEOPLE SKIP';
      /* the set's crown line is drawn at the body size, so the set gets a blank one and the scene writes the label at the
         label floor (size 66): caps at frame y 303 to 336 in the crown's panel (x 150 to 870, y 282 to 360) */
      k.sets.slots(Object.assign({label: ' ', idle: ['$', '$', '$']}, reel));
      k.text(label, 510, 288, {size: 66, color: GOLD, align: 'center'});
      /* steady life on the cabinet (golden: no still run over 1 s): big bulbs chase up both sides of the cabinet, a step
         every 3 frames, and while the reels wait for the lever each one nudges a few pixels in turn, like a reel being
         jiggled; both run on whole low-res pixels */
      for (let i = 0; i < 19; i++) { const y = 92 + i * 12, lit = (i + Math.floor(d.F / 3)) % 3 === 0;
        [30, 318].forEach((x, s2) => { const l2 = s2 ? (18 - i + Math.floor(d.F / 3)) % 3 === 0 : lit; d.P(x, y, 5, 5, INK); d.P(x + 1, y + 1, 3, 3, l2 ? CREAM : '#B07A47'); if (l2) d.DOT(x + 2, y + 2, GOLD); }); }
      /* the short spin is the set's own; after it the last reel settles on $ (the set's bounce would paint a landed $ red,
         so the scene draws it: 6, -3, 1 pixels over 3 frames), all three hold 9 frames, then the nudges come back */
      if (T >= t0 && T < tFour - 0.05 && (T < tSurv || T >= spin[2])) {
        const SYM = ['7', '$', '%', '9', '3', '5', '1', '0', '8', '2', '4', '6'], lf = d.fr(spin[2]);
        for (let r = 0; r < 3; r++) {
          const rx = 58 + r * 77, ry = 136;
          let b = [0, 3, 0, -3, 0, 0][(Math.floor(d.F / 5) + r * 2) % 6];
          if (lf >= 0 && lf < 9) b = r === 2 && lf < 3 ? [6, -3, 1][lf] : 0;
          if (b === 0) continue;
          d.clip(rx, ry, 70, 92, () => {
            d.P(rx, ry, 70, 92, CREAM);
            k.text('$', (rx + 35) * 3, (ry + 24 + b) * 3, {size: 132, color: '#2B2033', align: 'center', lint: false});
            k.text(SYM[(r * 3 + 1) % 12], (rx + 35) * 3, (ry + 24 + b - 50) * 3, {size: 132, color: '#C9CCD3', align: 'center', lint: false});
            k.text(SYM[(r * 3 + 5) % 12], (rx + 35) * 3, (ry + 24 + b + 50) * 3, {size: 132, color: '#C9CCD3', align: 'center', lint: false});
            d.P(rx, ry, 70, 6, SAND); d.P(rx, ry + 86, 70, 6, SAND); d.P(rx, ry, 70, 2, '#B39A88'); d.P(rx, ry + 90, 70, 2, '#B39A88');
          });
        }
      }
      // sparks as the numbers land
      /* out of the cabinet's sides, never over the reels or the words */
      const cab = [[114, 246, 906, 966]], sn = reel.win ? 16 : 9;
      spray(k, 105, 520, reel.stops[2] + 0.05, {n: sn, r: 110, dir: Math.PI, spread: 1.6, avoid: cab});
      spray(k, 975, 520, reel.stops[2] + 0.05, {n: sn, r: 110, dir: 0, spread: 1.6, avoid: cab});
      /* the clamp: 1, 2 and 3 held as one group. A thick gold bar over the reel tops grows out from the middle, its jaws
         drop over the outer reels' edges, then a small ONE GROUP tag sits on it */
      if (T >= tCav + 1.0 && T < tStart) {
        const f = d.fr(tCav + 1.0), w = Math.min(232, f * 29), x0 = 170 - w / 2;
        d.P(x0 - 1, 128, w + 2, 6, INK); d.P(x0, 129, w, 4, GOLD); d.P(x0, 129, w, 1, CREAM); d.P(x0, 132, w, 1, '#B07A47');
        if (w >= 232) {
          const j = Math.min(12, (f - 8) * 3);
          [54, 282].forEach((x) => { d.P(x - 1, 128, 7, j + 2, INK); d.P(x, 129, 5, j, GOLD); d.P(x, 129, 1, j, CREAM); });
          if (f >= 12) { const tw2 = Math.ceil(k.measure('ONE GROUP', {size: 30}) / 3); d.P(170 - tw2 / 2 - 5, 124, tw2 + 10, 16, INK); d.P(170 - tw2 / 2 - 4, 125, tw2 + 8, 14, GOLD); d.P(170 - tw2 / 2 - 4, 125, tw2 + 8, 1, CREAM);
            k.text('ONE GROUP', 510, 378, {size: 30, color: PLUM, align: 'center'}); }
        }
      }
      // the strip on the cabinet front: the source, once the survey is named (frame y 909)
      d.P(52, 300, 236, 18, INK); d.P(53, 301, 234, 16, '#2B2033');
      d.type(`ACCA survey, ACHR News, Feb ${n.accaYear.shown}`, 510, 906, tGrp, {color: SAND, align: 'center'});
      // the tray: two lines (frame y 750 and 810, centered at 510), nothing once the coins come
      const tray = (a, b) => { if (a) d.type(a[0], 510, 750, a[1], {color: a[2] || CREAM, align: 'center'}); if (b) d.type(b[0], 510, 810, b[1], {color: b[2] || CREAM, align: 'center'}); };
      if (T < tN) tray(['How many options', t0 + 0.3], ['do you give?', t0 + 0.6, GOLD]);
      else if (T < tP52 + 0.2) tray([`${n.accaN.shown}+ HVAC contractors`, tN, GOLD], T >= tFour ? ['close rate by options given', tFour] : null);
      else if (T < tOpt) tray([`${n.manyOpt.shown}+ options: ${n.manyClose.shown}`, tP52 + 0.2, GOLD], [`Only ${n.accaShare.shown} offer ${n.manyOpt.shown}+.`, tP52 + 0.5]);
      /* the crown flips to 1 TO 3 on the same frame the tray clears its 4+ lines; the 1 to 3 line types, its figure lands on
         "Forty-two", then the 4+ figure comes back under it to compare */
      else if (T < t42) tray([`${n.single.shown} to ${n.fewMax.shown} options:`, tOpt, GOLD], null);
      else if (T < tCav) tray([`${n.single.shown} to ${n.fewMax.shown} options: ${n.fewClose.shown}`, -1, GOLD], [`${n.manyOpt.shown}+ options: ${n.manyClose.shown}`, t42 + 0.3, SAND]);
      else if (T < tStart) tray([`${n.single.shown} to ${n.fewMax.shown} options: one group here.`, tCav + 0.3], T >= tCant ? [`It can't show ${n.fewMax.shown} beats ${n.single.shown}.`, tCant, RED] : null);
      /* the jackpot's label: the tray's top band carries the line, the coins pile and hop under it */
      else { d.P(62, 248, 216, 15, '#2B2033'); d.type(`Start with ${n.tiers.shown} prices.`, 510, 747, tStart, {color: GOLD, align: 'center'}); }
      return host(k, k.live('survey.caveat') ? 'clip' : (k.live('survey.52') || k.live('survey.start') ? 'point' : null));
    },

    // ---- close: the storefront again, no counter front: the plate hangs on the brick facade between the window sill and
    // the sidewalk. One column (left edge 120), the plate growing a line at a time as each line is said: the send line,
    // then its second half, the line, the payoff; "a choice." lands on "That's", so the payoff holds about 0.7 s before
    // the end card (which drops 0.1 s after the last word). The tag shows three prices on "Three". The chalk board writes
    // "1 price?" as the room opens, so it is never just the chip
    close: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('close'), tOne = k.S('close.one'), tYes = wordT(k, 'close.one', /^yes/i, 0.6), tThree = wordT(k, 'close.choice', /^Three/i);
      const tCh = wordT(k, 'close.choice', /^That/i, 1.2), tWr = wordT(k, 'close', /^writes/i, 0.6);
      storefront(k, {tags: [{price: '$', at: -1}, {price: '$ $$ $$$', at: tThree - FLIP}], threeAt: tThree,
        chalk: T < tThree ? [[`${n.single.shown} price?`, t0, CREAM, 450]] : [[`${n.tiers.shown} prices.`, tThree, GOLD, 450]]});
      facade(k);
      /* the plate: one line's height when it opens, a line more (24 low-res, 72 frame) as each line lands; lines at frame
         y 696, 768, 840, 912 */
      const lands = [t0 + 0.3, tWr, Math.min(tOne + 0.2, tYes), tThree + 0.1], H = (m) => 9 + 24 * m;
      let h = 0;
      lands.forEach((at, i) => { const q = eo(d.fr(at - 0.17) / 5); if (T >= at - 0.17) h = Math.round(H(i) + (H(i + 1) - H(i)) * q); });
      if (h > 0) d.win(30, 227, 300, h, {base: '#1B1420', hi: PLUM, lo: INK, rule: WINE});
      /* no shine on the plate's lines: the kit's glint band reads as a stray spark on the words (round 0, 70.3 s on the
         's' of 'this'), so nothing on the plate lights up but the lines landing and the sweep */
      const Y = (i) => 696 + i * 72;
      if (T >= lands[0]) k.slam('Send this to whoever', 120, Y(0), lands[0], {size: 66, color: GOLD, from: 0.4, glint: false});
      if (T >= lands[1]) k.slam('writes your quotes.', 120, Y(1), lands[1], {size: 66, color: GOLD, from: 0.4, glint: false});
      if (T >= lands[2]) k.slam(`${n.single.shown} price: yes or no.`, 120, Y(2), lands[2], {size: 66, color: CREAM, from: 0.5, glint: false});
      if (T >= lands[3]) k.slam(`${n.tiers.shown} prices:`, 120, Y(3), lands[3], {size: 66, color: 'accent', from: 0.5, glint: false});
      const xc = 120 + k.measure(`${n.tiers.shown} prices: `, {size: 66});
      if (T >= tCh) k.slam('a choice.', xc, Y(3), tCh, {size: 66, color: 'accent', from: 0.5, glint: false});   /* on "That's", held past the last word */
      if (T >= tCh + 0.3) k.sweep(xc, Y(3) + 69, k.measure('a choice.', {size: 66}), 6, tCh + 0.3, {color: 'accent'});
      k.chip('ProofNotFluff', 78, 540, {size: 30});
      /* sparks off the tag's top into the awning, never below frame y 672 (the plate starts at 681), kept off the tag, the
         chalk board and the OPEN sign */
      const avoid = [[627, 400, 945, 600], [36, 402, 492, 654], [880, 552, 1026, 654], [300, 230, 780, 320]];
      spray(k, 786, 410, tThree + 0.35, {n: 18, r: 150, dir: -Math.PI / 2, spread: 2.4, avoid, maxY: 672});
      spray(k, 786, 410, tCh + 0.3, {n: 14, r: 130, dir: -Math.PI / 2, spread: 2.4, colors: [GOLD, CREAM], avoid, maxY: 672});
      return host(k, T >= tCh ? 'wave' : (T < tOne ? 'point' : null));
    },
  },
};
