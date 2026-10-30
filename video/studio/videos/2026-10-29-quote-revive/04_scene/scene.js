/* Scene: The text that revives a quote that went quiet (lesson 2, The Text, arcade). One function per top-level cue in */
/* 03_cues/cues.md. Numbers only from k.data (brief.md -> data.js). Every time comes from a cue start (k.S) or a spoken */
/* word (wordT, spoken), never a typed number, so the re-voiced takes move the picture with them. */
/* Worlds (brief.md): hook and stakes = the street (one section: the van parked at the job, a cut in to your phone, then it pulls away); homework = */
/* the homeowner's fridge (our own piece); text = the chat set in the truck with our own keyboard and composer, then the */
/* homeowner's lock screen (our own piece); turn = the mail desk (our own piece); */
/* close = the level-up screen. No stock room. The camera holds still (pixel art never scales). */
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', GREY = '#9AA0AD';
const LINE_A = "Hi [name], it's [you].";
const LINE_B = 'Still want that water heater swapped before winter?';
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eo = (x) => 1 - Math.pow(1 - clamp(x), 3);
const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };

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
  const spr = (rows, pal, x, y, s = 1) => rows.forEach((r, j) => { for (let i = 0; i < r.length; i++) { const c = pal[r[i]]; if (c) P(x + i * s, y + j * s, s, s, c); } });
  const twinkle = (x, y, f, c = CREAM) => { const s = [0, 1, 2, 1][((f % 4) + 4) % 4]; DOT(x, y, c); for (let i = 1; i <= s; i++) { DOT(x - i, y, c); DOT(x + i, y, c); DOT(x, y - i, c); DOT(x, y + i, c); } };
  return {P, DOT, dith, disc, ring, line, win, fr, ease, tx, tw, clip, spr, twinkle, F, T};
};

/* ---- the words: every beat lands on a spoken word ---- */
const WS = () => (window.WORDS && window.WORDS.words) || [];
const norm = (s) => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
/* the time a word is said, within 6 s after a cue (or a time); falls back to the cue's start plus dflt. Leading quote */
/* marks are ignored ('"Still' is Still), and the search never runs on into a later take's same word. */
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && x.start < t0 + 6 && re.test(String(x.w).replace(/^[^\w]+/, '')));
  return w ? w.start : t0 + dflt;
};
/* the start of each spoken word of a line, matched in order from t0 (a missing word takes the one before's time) */
const spoken = (t0, said) => {
  const ws = WS(); let i = ws.findIndex((x) => x.start >= t0 - 0.05); if (i < 0) i = ws.length;
  let last = t0;
  return said.split(/\s+/).map((wd) => {
    const want = norm(wd); let j = i;
    while (j < ws.length && j < i + 6 && norm(ws[j].w) !== want) j++;
    if (j < ws.length && j < i + 6) { i = j + 1; last = ws[j].start; return ws[j].start; }
    return last;
  });
};
/* a count that starts at 85% of its value and lands exactly on it */
const cnt = (k, num, t0, o = {}) => k.count(num.value, k.lin(t0, t0 + 0.7) >= 1 ? 1 : 0.85 + 0.15 * k.lin(t0, t0 + 0.7), Object.assign({from: 0}, o));
const host = (k, pose) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150});

/* ================================================================================================================ */
/* the street: the library set, chained into trips. Each trip is its own k.sets.street call, started so the world */
/* position carries on from where the last one parked (no jump), and the last stop's sign is drawn again here so it */
/* slides off behind the van instead of vanishing. */
const V = 30, SD = 0.8;
const streetPos = (T, o) => { const v = V * (o.speed || 1), sd = o.stopDur || SD; const d = Math.max(0, T - o.t0); if (o.stopAt == null) return v * d; const ds = Math.max(0, o.stopAt - o.t0); if (d <= ds) return v * d; const e = Math.min(d - ds, sd); return v * ds + v * (e - e * e / (2 * sd)); };
const parked = (o) => streetPos(o.stopAt + (o.stopDur || SD) + 1, o);
const sign = (d, sx, label) => {   /* the yard sign as sets.js draws it, settled */
  const w = Math.max(30, Math.ceil(d.tw(label)) + 10);
  if (sx < -60 || sx > 380) return;
  d.P(sx + 4, 270, 2, 22, '#6B4226'); d.P(sx + w - 6, 270, 2, 22, '#6B4226');
  d.P(sx - 1, 249, w + 2, 22, INK); d.P(sx, 250, w, 20, CREAM); d.P(sx + 1, 251, w - 2, 1, RED); d.P(sx + 1, 268, w - 2, 1, RED); d.P(sx, 269, w, 1, SAND);
  d.tx(label, sx + w / 2, 254, {align: 'center', color: '#7A3442'});
};
/* base: the parked call ({t0, stopAt, sign}); trips: [{at, drive, sign, speed}] (drive null: keeps going) */
const route = (k, base, trips) => {
  const d = px(k), T = k.T;
  let call = base, prevSign = null;
  for (const tr of trips) {
    if (T < tr.at) break;
    const P0 = parked(call), v = V * (tr.speed || 1);
    if (call.sign !== false && call.stopAt != null) prevSign = {label: call.sign || 'JOB', ho: Math.floor(P0 * 0.5)};
    call = {t0: tr.at - P0 / v, stopAt: tr.drive == null ? null : tr.at + tr.drive, sign: tr.sign == null ? false : tr.sign, speed: tr.speed || 1};
  }
  const r = k.sets.street(call);
  if (prevSign) sign(d, 112 + prevSign.ho - Math.floor(streetPos(T, call) * 0.5), prevSign.label);
  return r;
};
const skyWin = (d, h) => d.win(14, 86, 332, h, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
/* the lawn under the fence: mowed stripes that widen toward us (they run with the road, so they hold still while it scrolls) */
const lawn = (d) => { for (let y = 392, r = 0, hh = 10; y < 640; y += hh, r++, hh += 3) if (r & 1) { d.P(0, y, 360, hh, '#346450'); } };

/* ================================================================================================================ */
/* the fridge (homework): our own piece. A kitchen wall, a counter with a kettle and the homeowner's phone, a clock that */
/* ticks, and the fridge: freezer door with a kid's drawing and magnets, main door where sticky notes slap on. */
const NOTE_W = 78, NOTE_H = 60;
const fridge = (k, o) => {
  const d = px(k), {P, DOT, disc, ring, line, fr, F, T} = d;
  /* the wall and its stripes, the backsplash, the counter and its cabinets, the floor */
  P(0, 0, 360, 417, '#F4E6D3'); for (let x = 4; x < 360; x += 12) P(x, 0, 1, 196, '#E6D3BC');
  for (let y = 196, r = 0; y < 250; y += 9, r++) for (let x = (r & 1) * 6 - 6; x < 150; x += 12) { P(x, y, 11, 8, '#BDE6F5'); P(x, y, 11, 1, CREAM); P(x, y + 7, 11, 1, '#87CEEB'); }
  P(0, 250, 150, 6, '#C9CCD3'); P(0, 250, 150, 1, CREAM); P(0, 255, 150, 1, '#6B7080');
  P(0, 256, 150, 161, '#8C5A33'); for (let x = 4; x < 150; x += 48) { P(x, 262, 42, 60, '#B07A47'); P(x, 262, 42, 1, '#D9A066'); P(x + 34, 288, 4, 2, '#6B4226'); }
  /* the floor: a cream baseboard, then honey oak planks (staggered end joints, a groove under each row, a little grain) */
  /* and a striped runner in front of the fridge */
  P(0, 417, 360, 6, CREAM); P(0, 422, 360, 1, '#B39A88'); P(0, 423, 360, 2, '#6B4226');
  for (let y = 425, r = 0; y < 640; y += 11, r++) {
    for (let x = -Math.floor(hash(r * 3.7) * 120), j = 0; x < 360; j++) {
      const L = 100 + Math.floor(hash(r * 5.1 + j * 2.3) * 70), c = ['#B07A47', '#A86F3F', '#BC8650'][Math.floor(hash(r * 1.9 + j * 4.7) * 3)];
      P(x, y, L, 10, c); P(x, y, L, 1, '#D9A066'); P(x + L - 1, y, 1, 10, '#6B4226');
      P(x + 14 + Math.floor(hash(r + j * 9.1) * 40), y + 4, 22, 1, '#8C5A33'); P(x + 50 + Math.floor(hash(r * 2 + j) * 30), y + 7, 14, 1, '#9C6A3C');
      x += L;
    }
    P(0, y + 10, 360, 1, '#6B4226');
  }
  P(168, 452, 172, 66, INK); P(170, 454, 168, 62, '#7A3442');
  for (let i = 0; i < 3; i++) { P(170, 460 + i * 20, 168, 3, GOLD); P(170, 465 + i * 20, 168, 1, CREAM); }
  for (let x = 172; x < 338; x += 4) { P(x, 449, 1, 3, CREAM); P(x, 518, 1, 3, CREAM); }
  /* the clock: the second hand steps once a second */
  const cx = 52, cy = 120;
  disc(cx, cy, 17, INK); disc(cx, cy, 15, CREAM); ring(cx, cy, 15, '#B07A47', 2);
  for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6; DOT(cx + Math.round(Math.cos(a) * 11), cy + Math.round(Math.sin(a) * 11), '#6B7080'); }
  const sa = (Math.floor(T) % 60) * Math.PI / 30 - Math.PI / 2; line(cx, cy, cx + Math.round(Math.cos(sa) * 12), cy + Math.round(Math.sin(sa) * 12), RED);
  line(cx, cy, cx + 6, cy - 4, INK); line(cx, cy, cx, cy - 9, INK);
  /* the kettle, steam puffing up on whole pixels */
  P(16, 232, 26, 18, INK); P(17, 233, 24, 16, RED); P(17, 233, 24, 2, ORANGE); P(24, 228, 12, 5, INK); P(25, 229, 10, 3, '#7A3442'); P(41, 236, 6, 3, INK);
  for (let i = 0; i < 4; i++) { const a = (F + i * 9) % 36; P(44 + Math.floor(a / 6) % 2, 230 - a, 3 + (a > 18 ? 1 : 0), 3, a > 24 ? '#E6D3BC' : CREAM); }
  /* the homeowner's phone, standing on the counter; it buzzes (a pixel either side) when a text lands */
  const bz = o.buzzAt != null && T >= o.buzzAt && T < o.buzzAt + 0.5 ? ((F >> 1) & 1 ? 1 : -1) : 0;
  P(108 + bz, 220, 20, 30, INK); P(109 + bz, 221, 18, 28, '#253048'); P(110 + bz, 223, 16, 22, o.buzzAt != null && T >= o.buzzAt ? '#87CEEB' : '#3B82C4');
  if (o.buzzAt != null && T >= o.buzzAt) { P(112 + bz, 226, 12, 3, CREAM); P(112 + bz, 231, 8, 2, CREAM); }
  /* the fridge */
  const FX = 150, FY = 74, FW = 192, FH = 258;
  P(FX - 1, FY - 1, FW + 2, FH + 2, INK); P(FX, FY, FW, FH, '#F4E6D3'); P(FX, FY, FW, 1, '#FFFFFF'); P(FX, FY, 1, FH, CREAM); P(FX + FW - 3, FY, 3, FH, '#E6D3BC');
  P(FX, 144, FW, 2, '#B39A88'); P(FX, 146, FW, 1, CREAM);
  P(FX + 4, 92, 3, 40, '#9AA0AD'); P(FX + 4, 92, 1, 40, CREAM); P(FX + 4, 158, 3, 70, '#9AA0AD'); P(FX + 4, 158, 1, 70, CREAM);
  P(FX + 6, FY + FH + 1, FW - 12, 5, '#4A4E5A'); for (let x = FX + 10; x < FX + FW - 10; x += 4) P(x, FY + FH + 2, 2, 3, '#6B7080');
  /* the freezer door: a kid's drawing (a house, a sun) under two magnets */
  P(290, 82, 44, 54, INK); P(291, 83, 42, 52, CREAM);
  line(298, 112, 311, 100, '#3B82C4'); line(311, 100, 324, 112, '#3B82C4'); P(300, 112, 22, 16, '#E2633B'); P(308, 118, 6, 10, '#F2A541'); disc(325, 92, 4, ORANGE);
  for (let i = 0; i < 3; i++) P(294 + i * 12, 130, 6, 2, '#3E7A62');
  disc(298, 84, 3, TEAL); disc(326, 84, 3, RED);
  /* magnets on the main door that the notes sit beside; they wobble a pixel now and then */
  [[176, 300, RED], [218, 306, TEAL], [300, 296, GOLD]].forEach(([mx, my, c], i) => { const w = ((F >> 4) + i) % 5 === 0 ? 1 : 0; disc(mx, my - w, 4, INK); disc(mx, my - w, 3, c); DOT(mx - 1, my - 2 - w, CREAM); });
  return {fx: FX, fy: FY};
};
/* a sticky note: it slaps on (a drop and a one-pixel squash) and its corner curls up and down */
const note = (k, x, y, c, lines, at, o = {}) => {
  const d = px(k), f = d.fr(at);
  if (f < 0) return;
  const dy = [-8, -4, -1, 1, 0][Math.min(4, f)], yy = y + dy, w = NOTE_W, h = NOTE_H;
  d.P(x + 2, yy + 2, w, h, 'rgba(18,13,20,0.25)');
  d.P(x - 1, yy - 1, w + 2, h + 2, '#B39A88'); d.P(x, yy, w, h, c); d.P(x, yy, w, 3, o.top || CREAM);
  if (((d.F >> 4) + (o.seed || 0)) % 3 === 0) { d.P(x + w - 5, yy + h - 5, 5, 5, '#E6D3BC'); d.P(x + w - 5, yy + h - 5, 1, 5, '#B39A88'); }
  d.disc(x + w / 2, yy + 1, 3, INK); d.disc(x + w / 2, yy + 1, 2, o.pin || RED);
  if (!o.hidden) lines.forEach((s, i) => d.tx(s, x + 6, yy + 9 + i * 16, {color: INK}));
  return yy;
};

/* ================================================================================================================ */
/* the truck phone's own build on the chat set (lesson 1 filled bubbles in place; this one types in the input bar): a
   keyboard rises, each line types into the composer word by word as it is said (the keys it hits flash), and the bubble
   goes up into the chat on the word that sends it. Screen in low-res units, as sets.js lays the chat phone out. */
const PH = {sx: 102, sy: 90, sw: 188, sh: 228, cy0: 130, kb: 252};
/* a line split into the words said so far, laid out on its final wrap (so nothing reflows as it types) */
const typed = (k, text, times, wpx) => {
  const ls = k.wrap(text, {size: 39}, wpx * 3); let wi = 0, last = null;
  const shown = ls.map((l, li) => { const ws = l.split(' '), out = []; ws.forEach((w) => { if (k.T >= times[wi]) { out.push(w); last = li; } wi++; }); return out.join(' '); });
  return {ls, shown, n: last == null ? 1 : last + 1, done: times.every((t) => k.T >= t)};
};
/* a sent bubble (ours: blue, right side), drawn bottom-up from y; text lines only where they sit fully in the chat */
const bubble = (d, k, ls, bx, by, w, y0, y1) => {
  const h = ls.length * 15 + 8;
  d.P(bx + 1, by, w - 2, h, '#3B82C4'); d.P(bx, by + 1, w, h - 2, '#3B82C4'); d.P(bx + 1, by, w - 2, 1, '#87CEEB'); d.P(bx + 1, by + h - 1, w - 2, 1, '#253048');
  d.P(bx + w, by + h - 5, 2, 3, '#3B82C4'); d.P(bx + w + 2, by + h - 3, 2, 2, '#3B82C4');
  ls.forEach((l, li) => { const ly = by + 4 + li * 15; if (ly >= y0 && ly + 13 <= y1) d.tx(l, bx + 5, ly, {color: CREAM}); });
};
const truckPhone = (k, o) => {
  const d = px(k), {P, disc, ring, line, clip, fr, ease, T} = d, {sx, sy, sw, sh, cy0} = PH;
  clip(sx, sy, sw, sh, () => {
    /* the keyboard: four rows of blank keys on whole pixels; it rises from the screen's bottom edge */
    const ky = PH.kb + ease(o.kbAt, 6, 70);
    P(sx, ky - 1, sw, sy + sh - ky + 1, '#C9CCD3'); P(sx, ky - 1, sw, 1, '#9AA0AD');
    const keys = [];
    for (let r = 0; r < 3; r++) { const n = [10, 9, 7][r], x0 = sx + 5 + [0, 9, 27][r]; for (let i = 0; i < n; i++) keys.push([x0 + i * 18, ky + 3 + r * 16, 16, 13]); }
    keys.push([sx + 5, ky + 35, 22, 13], [sx + sw - 27, ky + 35, 22, 13], [sx + 5, ky + 51, 40, 12], [sx + 49, ky + 51, 90, 12], [sx + sw - 45, ky + 51, 40, 12]);
    /* the keys hit: each typed word presses one key per letter, 0.045 s apart, each lit for 2 frames */
    const hit = new Set();
    o.words.forEach(([w, t], wi) => { for (let j = 0; j < w.length; j++) { const f = fr(t + j * 0.045); if (f >= 0 && f < 2) hit.add(Math.floor(hash(wi * 7.3 + j * 1.9) * 26)); } });
    keys.forEach(([x, y, w, h], i) => { const on = hit.has(i); P(x, y + (on ? 1 : 0), w, h, on ? GOLD : CREAM); P(x, y + h - 1 + (on ? 1 : 0), w, 1, on ? ORANGE : '#9AA0AD'); });
    /* the composer: grows a line at a time over the keyboard; the send button lights while there is a draft */
    const dr = o.draft, nL = dr ? dr.n : 1, fh = nL * 15 + 4, fy = ky - 5 - fh, fx = sx + 4, fw = sw - 30;
    P(sx, fy - 4, sw, ky - fy + 3, CREAM); P(sx, fy - 4, sw, 1, '#E6D3BC');
    P(fx, fy, fw, fh, '#F4E6D3'); P(fx, fy, fw, 1, '#E6D3BC'); P(fx, fy + fh - 1, fw, 1, CREAM);
    const bcx = sx + sw - 13, bcy = fy + fh - 9, flash = o.sentAt != null && fr(o.sentAt) >= 0 && fr(o.sentAt) < 6;
    disc(bcx, bcy, 7, dr && dr.shown.some((s) => s) ? '#2F6F67' : '#9AA0AD'); if (flash) ring(bcx, bcy, 9 + (fr(o.sentAt) >> 1), GOLD);
    line(bcx - 3, bcy, bcx + 3, bcy, CREAM); line(bcx, bcy - 3, bcx + 3, bcy, CREAM); line(bcx, bcy + 3, bcx + 3, bcy, CREAM);
    let cx = fx + 5, cyy = fy + 2;
    if (dr) dr.shown.forEach((s, li) => { if (!s) return; d.tx(s, fx + 5, fy + 2 + li * 15, {color: INK}); cx = fx + 5 + Math.ceil(d.tw(s)) + 1; cyy = fy + 2 + li * 15; });
    if (!dr || !dr.shown.some((s) => s)) d.tx('Text message', fx + 5, fy + 2, {color: '#B39A88', lint: false});
    if (Math.floor(T * 2) % 2 === 0 && !(dr && dr.done)) P(cx, cyy, 1, 13, '#2F6F67');
    /* the chat: sent bubbles stacked up from the composer, each sliding up 8 px as it lands */
    const y1 = fy - 6;
    clip(sx, cy0, sw, y1 - cy0, () => {
      let y = y1;
      o.sent.filter((m) => T >= m.at).reverse().forEach((m) => {
        if (m.quote) {   /* the quote you sent: a PDF card, seen and never answered */
          const w = 98, h = 34, bx = sx + sw - 10 - w, by = y - h + ease(m.at, 4, 8);
          P(bx + 1, by, w - 2, h, '#3B82C4'); P(bx, by + 1, w, h - 2, '#3B82C4'); P(bx + 1, by, w - 2, 1, '#87CEEB');
          P(bx + 5, by + 5, 16, 24, CREAM); P(bx + 5, by + 5, 16, 5, ORANGE); for (let j = 0; j < 4; j++) P(bx + 8, by + 13 + j * 4, 10 - (j % 2) * 4, 1, GREY);
          if (by + 3 >= cy0) { d.tx('Quote.pdf', bx + 26, by + 3, {color: CREAM}); d.tx('Seen', bx + 26, by + 17, {color: '#BDE6F5'}); }
          y = by - 6; return;
        }
        const ls = k.wrap(m.text, {size: 39}, 138 * 3), w = Math.min(150, Math.ceil(Math.max(...ls.map((l) => d.tw(l)))) + 10), h = ls.length * 15 + 8;
        const by = y - h + ease(m.at, 4, 8);
        bubble(d, k, ls, sx + sw - 10 - w, by, w, cy0, y1);
        y = by - 6;
      });
    });
  });
};

/* the homeowner's lock screen (our own piece): their phone rises from behind the dash with your question on it as a
   notification, YES and NO as its quick replies; each reply button presses when it is said */
const lockScreen = (k, o) => {
  const d = px(k), {P, DOT, disc, ring, line, clip, fr, ease, F, T} = d;
  const LX = 120, LW = 190, LH = 188, LY = 134 + ease(o.at, 8, 200);
  clip(0, 0, 360, 330, () => {
    P(LX + 3, LY + 3, LW, LH, '#120D14'); P(LX - 1, LY, LW + 2, LH, INK); P(LX, LY - 1, LW, LH + 2, INK);
    P(LX, LY, LW, LH, '#1B1420'); P(LX + 1, LY, LW - 2, 1, '#4A4E5A');
    const sx = LX + 5, sy = LY + 5, sw = LW - 10, sh = LH - 10;
    /* the wallpaper: their street at night, a moon, stars that wink, the house with a lit window */
    P(sx, sy, sw, sh, '#253048'); for (let y = sy; y < sy + sh; y += 6) P(sx, y, sw, 1, '#1F2A40');
    disc(sx + sw - 22, sy + 16, 6, SAND); disc(sx + sw - 20, sy + 14, 5, '#253048');
    for (let i = 0; i < 6; i++) { const f = Math.floor(F / 6) + i * 3; d.twinkle(sx + 10 + Math.floor(hash(i * 5.1) * (sw - 20)), sy + 6 + Math.floor(hash(i * 8.3) * 14), f % 9 < 4 ? f % 4 : 0, i % 2 ? GOLD : CREAM); }
    const hy = sy + sh - 34;
    P(sx, hy + 22, sw, 12, '#1B1420');
    for (let j = 0; j < 14; j++) P(sx + 40 + j, hy + 8 - j, sw - 80 - 2 * j, 1, '#3D2E45');
    P(sx + 50, hy + 8, sw - 100, 14, '#3D2E45'); P(sx + 58, hy + 11, 10, 7, GOLD); P(sx + sw - 68, hy + 11, 10, 7, '#1B1420'); P(sx + sw / 2 - 4, hy + 12, 8, 10, '#1B1420');
    /* the padlock */
    const lx = sx + sw / 2;
    ring(lx, sy + 8, 4, CREAM); P(lx - 6, sy + 9, 12, 9, CREAM); P(lx - 1, sy + 12, 2, 3, '#253048');
    /* the notification */
    const ls = k.wrap(LINE_B, {size: 39}, 156 * 3), nx = sx + 6, nw = sw - 12, ny = sy + 26, nh = 22 + ls.length * 15 + 28;
    P(nx + 2, ny + 2, nw, nh, '#120D14'); P(nx + 1, ny, nw - 2, nh, CREAM); P(nx, ny + 1, nw, nh - 2, CREAM); P(nx + 1, ny, nw - 2, 1, '#FFFFFF');
    P(nx + 6, ny + 5, 11, 11, '#2F6F67'); P(nx + 8, ny + 8, 7, 5, CREAM); DOT(nx + 9, ny + 13, CREAM);
    d.tx('Messages', nx + 21, ny + 4, {color: '#6B7080'}); d.tx('now', nx + nw - 6, ny + 4, {color: '#6B7080', align: 'right'});
    ls.forEach((l, li) => d.tx(l, nx + 6, ny + 21 + li * 15, {color: INK}));
    const by = ny + 22 + ls.length * 15 + 4, bw = Math.floor((nw - 18) / 2);
    [['YES', o.yesAt, '#2F6F67', nx + 6], ['NO', o.noAt, '#7A3442', nx + 12 + bw]].forEach(([s, at, c, x]) => {
      const f = at != null ? fr(at) : -1, dn = f >= 0 && f < 3 ? 1 : 0;
      P(x, by + 1, bw, 18, INK); P(x, by + dn, bw, 17, c); P(x, by + dn, bw, 1, f >= 0 ? '#FFFFFF' : CREAM);
      d.tx(s, x + bw / 2, by + 2 + dn, {color: CREAM, align: 'center'});
      if (f >= 0 && f < 15 && Math.floor((T - at) * 2) % 2 === 0) { P(x - 2, by - 2, bw + 4, 1, GOLD); P(x - 2, by + 19, bw + 4, 1, GOLD); P(x - 2, by - 2, 1, 22, GOLD); P(x + bw + 1, by - 2, 1, 22, GOLD); }
      if (f >= 0 && f < 8) d.twinkle(x + bw - 4, by - 2, f >> 1, GOLD);
    });
    /* the gold frame steps in around the notification once it has landed, and holds (it swaps colors twice a second) */
    const st = o.at + 8 / 30;
    if (T >= st) { const f = fr(st), g = f < 4 ? 3 - f : 0, x = nx - 3 - g, y = ny - 3 - g, w = nw + 6 + 2 * g, h = nh + 6 + 2 * g, c = Math.floor((T - st) * 2) % 2 ? GOLD : ORANGE; [[x, y, w, 2], [x, y + h - 2, w, 2], [x, y, 2, h], [x + w - 2, y, 2, h]].forEach(([a, b, ww, hh]) => P(a, b, ww, hh, c)); }
    P(lx - 20, LY + LH - 9, 40, 2, CREAM);
  });
  return {card: [(LX + 5 + 6 + (LW - 22) / 2) * 3, (LY + 31 + 40) * 3]};
};

/* ================================================================================================================ */
/* the mail desk (turn): our own piece. Night outside the window; a laptop whose inbox fills with envelopes nobody opens; */
/* the phone on its stand with your text, read. */
const desk = (k, o) => {
  const d = px(k), {P, DOT, disc, line, fr, ease, F, T} = d;
  P(0, 0, 360, 417, '#253048'); for (let y = 0; y < 262; y += 6) P(0, y, 360, 1, '#1F2A40');
  /* the window: the moon and stars, the frame */
  P(206, 0, 140, 80, INK); P(209, 0, 134, 77, '#1B1420');
  disc(318, 30, 9, '#E6D3BC'); disc(321, 27, 8, '#1B1420');
  for (let i = 0; i < 9; i++) { const f = Math.floor(F / 6) + i * 3; d.twinkle(214 + Math.floor(hash(i * 3.3) * 120), 8 + Math.floor(hash(i * 7.7) * 60), f % 9 < 4 ? f % 4 : 0, i % 2 ? GOLD : CREAM); }
  P(275, 0, 3, 77, INK); P(209, 38, 134, 3, INK);
  /* the desk */
  P(0, 262, 360, 6, '#B07A47'); P(0, 262, 360, 1, '#D9A066'); P(0, 268, 360, 149, '#6B4226'); for (let y = 274; y < 417; y += 10) P(0, y, 360, 1, '#5A3A22');
  P(0, 417, 360, 223, '#2B2033'); for (let y = 424; y < 640; y += 12) P(0, y, 360, 1, '#3D2E45');
  /* the laptop and its inbox: a new envelope row lands every half second and pushes the others down, all unread */
  const lx = 18 - (o.laptopOut != null ? Math.round(200 * eo(fr(o.laptopOut) / 10)) : 0);
  if (lx > -170) {
    P(lx - 4, 252, 162, 8, '#6B7080'); P(lx - 4, 252, 162, 1, '#C9CCD3'); P(lx + 60, 256, 34, 2, '#4A4E5A');
    P(lx, 136, 154, 116, INK); P(lx + 3, 139, 148, 110, '#C9CCD3'); P(lx + 3, 139, 148, 12, '#3B82C4'); P(lx + 6, 142, 30, 6, CREAM); disc(lx + 144, 145, 2, RED);
    d.clip(lx + 3, 152, 148, 97, () => {
      const n = Math.max(0, Math.floor((T - o.t0) * 2)) + 3;
      for (let j = 0; j < 9; j++) {
        const idx = n - j; if (idx < 0) continue;
        const slide = j === 0 ? ease(o.t0 + (n - 3) / 2, 4, -12) : 0, y = 154 + j * 12 + slide;
        P(lx + 5, y, 144, 11, j % 2 ? '#E6D3BC' : CREAM);
        P(lx + 9, y + 2, 12, 8, INK); P(lx + 10, y + 3, 10, 6, CREAM); line(lx + 10, y + 3, lx + 15, y + 6, '#9AA0AD'); line(lx + 19, y + 3, lx + 15, y + 6, '#9AA0AD');
        P(lx + 26, y + 3, 40 + Math.floor(hash(idx * 1.3) * 40), 2, '#4A4E5A'); P(lx + 26, y + 7, 30 + Math.floor(hash(idx * 2.9) * 50), 1, '#9AA0AD');
        disc(lx + 141, y + 5, 2, '#3B82C4');
      }
    });
  }
  /* the phone on its stand; the screen holds your text (pixel lines), read ticks, a glow that pulses twice a second */
  const PX = 228, PY = 136;
  P(PX + 30, 244, 30, 18, '#4A4E5A'); P(PX + 30, 244, 30, 1, '#9AA0AD');
  P(PX - 1, PY - 1, 92, 118, INK); P(PX, PY, 90, 116, '#1B1420'); P(PX + 4, PY + 6, 82, 102, '#F4E6D3'); P(PX + 4, PY + 6, 82, 12, '#2F6F67'); P(PX + 40, PY + 2, 10, 2, '#3D2E45');
  const lit = o.textAt != null && T >= o.textAt;
  if (lit) {
    const sl = ease(o.textAt, 4, 8), by = PY + 40 + sl;
    P(PX + 22, by, 60, 44, '#3B82C4'); P(PX + 22, by, 60, 1, '#87CEEB');
    for (let j = 0; j < 4; j++) P(PX + 27, by + 7 + j * 9, j === 3 ? 30 : 50, 3, CREAM);
    if (T >= o.textAt + 0.6) [0, 4].forEach((dx) => { DOT(PX + 66 + dx, by + 39, '#87CEEB'); DOT(PX + 67 + dx, by + 40, '#87CEEB'); line(PX + 68 + dx, by + 39, PX + 71 + dx, by + 36, '#87CEEB'); });
    if (Math.floor(T * 2) % 2 === 0) { P(PX - 3, PY - 3, 96, 1, GOLD); P(PX - 3, PY + 118, 96, 1, GOLD); P(PX - 3, PY - 3, 1, 122, GOLD); P(PX + 92, PY - 3, 1, 122, GOLD); }
  }
  if (o.checkAt != null && T >= o.checkAt) {   /* a check pops on the screen */
    const f = fr(o.checkAt), s = f < 3 ? 1 : 0, cx = PX + 45, cy = PY + 98 - s;
    disc(cx, cy, 8 + s, '#2F6F67'); disc(cx, cy, 7 + s, TEAL);
    line(cx - 4, cy, cx - 1, cy + 3, CREAM, 2); line(cx - 1, cy + 3, cx + 4, cy - 3, CREAM, 2);
  }
  return {phone: [PX, PY]};
};

/* ================================================================================================================ */
/* the phone close-up (hook, "quiet" to "One"): the cut in on the quiet quote (IMPROVE 00a). The hook rides on a title */
/* plate up top; below it your phone, big in its dash mount: the quote you sent, Seen, and no reply under it. The dash */
/* and its vents fill the lower frame; Snow steps up big in the cab (a reframe, not a backdrop swap). One low-res */
/* pixel per 3 frame units, nothing scaled. */
const quietPhone = (k) => {
  const d = px(k), {P, DOT, disc, line, F} = d;
  /* the windshield: dusk over the street; the cab around it, as in the chat set: roof liner, mirror, air freshener and
     the two A-pillars down the frame edges (no bare slabs beside the title plate) */
  P(0, 0, 360, 168, '#5A3042'); P(0, 0, 360, 52, '#3D2E45'); d.dith(0, 50, 360, 3, '#3D2E45', 1);
  for (let i = 0; i < 6; i++) { const x = 20 + i * 62, h = 30 + Math.floor(hash(i * 2.7) * 26); P(x, 168 - h, 46, h, '#2B2033'); P(x + 8, 168 - h + 8, 6, 5, (i + (F >> 4)) % 3 ? GOLD : '#1B1420'); }
  for (let y = 0; y < 170; y++) { const w = 30 - Math.floor(y / 12); P(0, y, w, 1, '#1B1420'); P(w, y, 1, 1, '#3D2E45'); P(360 - w, y, w, 1, '#1B1420'); P(359 - w, y, 1, 1, '#3D2E45'); }
  [[4, 104], [348, 104]].forEach(([x, y]) => { P(x, y, 8, 26, '#2B2033'); P(x, y, 8, 1, '#4A4E5A'); P(x + 3, y + 4, 2, 18, INK); });
  P(0, 0, 360, 12, '#1B1420'); P(150, 12, 60, 14, INK); P(152, 13, 56, 11, '#4A4E5A'); P(153, 14, 54, 4, '#87CEEB'); P(178, 0, 4, 13, INK);
  { const sw = [0, 1, 0, -1][(F >> 3) % 4]; line(196, 24, 196 + sw, 36, '#C9CCD3'); P(192 + sw, 36, 9, 10, '#3E7A62'); P(194 + sw, 34, 5, 2, '#3E7A62'); DOT(193 + sw, 37, '#6FB7A8'); }
  P(0, 160, 360, 8, '#1B1420');
  /* the dash: a dark shelf that runs to the bottom of the frame, two big vents with slats; under them the lower dash:
     a glovebox, the cup holder with your coffee, the keys on their ring, a clipboard of quotes on the console */
  P(0, 168, 360, 472, '#2B2033'); P(0, 168, 360, 3, '#4A4E5A'); P(0, 171, 360, 2, INK);
  [[14, 470], [222, 470]].forEach(([x, y]) => { P(x - 1, y - 1, 126, 62, INK); P(x, y, 124, 60, '#1B1420'); for (let j = 0; j < 6; j++) P(x + 4, y + 6 + j * 9, 116, 3, '#3D2E45'); });
  P(0, 548, 360, 92, '#241B2B'); P(0, 548, 360, 2, '#4A4E5A'); P(0, 550, 360, 1, INK);
  P(222, 560, 124, 56, '#2B2033'); P(222, 560, 124, 1, '#4A4E5A'); P(222, 615, 124, 1, INK); P(272, 584, 24, 6, '#4A4E5A'); P(273, 585, 22, 2, '#9AA0AD');
  P(150, 566, 56, 30, INK); P(152, 568, 52, 26, '#1B1420'); disc(178, 581, 11, '#3D2E45');
  P(168, 552, 20, 30, CREAM); P(168, 552, 20, 4, '#E6D3BC'); P(166, 550, 24, 4, '#9AA0AD'); P(171, 562, 14, 8, ORANGE); P(188, 558, 4, 12, CREAM);
  { const sk = [0, 1, 1, 0, -1, -1][(F >> 3) % 6]; line(134 , 520, 136 + sk, 532, '#C9CCD3'); disc(136 + sk, 536, 4, GOLD); P(132 + sk, 540, 4, 10, '#9AA0AD'); P(138 + sk, 538, 3, 8, '#6B7080'); }
  P(20, 566, 110, 64, '#5A3A22'); P(20, 566, 110, 1, '#7A5232'); P(58, 562, 34, 8, '#9AA0AD'); P(60, 563, 30, 3, '#C9CCD3');
  P(28, 574, 94, 52, CREAM); for (let j = 0; j < 6; j++) P(36, 584 + j * 7, 78 - (j % 3) * 14, 2, GREY); P(28, 574, 94, 6, '#E6D3BC');
  for (let x = 0; x < 360; x += 30) P(x + 6, 632, 18, 2, '#3D2E45');
  /* the title plate: the hook, held from the cover (frame y 258 to 486) */
  d.win(14, 86, 332, 80, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
  const a = 'Quote went ', wa = k.measure(a, {size: 66}), x0 = 540 - (wa + k.measure('quiet?', {size: 66})) / 2;
  k.text(a, x0, 276, {size: 66, color: CREAM, drop: INK}); k.text('quiet?', x0 + wa, 276, {size: 66, color: 'accent', drop: INK});
  k.text('Send this text.', 540, 352, {size: 66, color: CREAM, align: 'center', drop: INK});
  k.text('Sources: ServiceTitan, Jobber, Housecall Pro', 540, 432, {size: 30, color: SAND, align: 'center'});
  /* the phone in its mount, big: bezel, header, your quote (a PDF card, Seen), nothing after it */
  const X = 150, Y = 176, W = 182, H = 268;
  P(X + 50, Y + H, 82, 14, '#4A4E5A'); P(X + 50, Y + H, 82, 2, '#9AA0AD');
  P(X - 1, Y - 1, W + 2, H + 2, INK); P(X, Y, W, H, '#1B1420'); P(X + 1, Y, W - 2, 1, '#4A4E5A');
  const sx = X + 7, sy = Y + 8, sw = W - 14, sh = H - 16;
  P(sx, sy, sw, sh, '#F4E6D3');
  /* the header, the same chrome as the chat set's phone: status bar, back arrow, avatar, name, a live dot */
  P(sx, sy, sw, 36, '#2F6F67'); P(sx, sy + 36, sw, 1, '#245752');
  d.tx('9:41', sx + 4, sy + 2, {color: CREAM, lint: false});
  for (let i = 0; i < 4; i++) P(sx + sw - 30 + i * 3, sy + 9 - i * 2, 2, 2 + i * 2, CREAM);
  P(sx + sw - 15, sy + 4, 11, 7, CREAM); P(sx + sw - 14, sy + 5, 6, 5, TEAL); P(sx + sw - 4, sy + 6, 1, 3, CREAM);
  line(sx + 9, sy + 26, sx + 5, sy + 22, CREAM); line(sx + 9, sy + 18, sx + 5, sy + 22, CREAM);
  disc(sx + 22, sy + 22, 7, '#F0B98D'); P(sx + 15, sy + 15, 14, 4, RED); DOT(sx + 19, sy + 22, INK); DOT(sx + 25, sy + 22, INK); P(sx + 20, sy + 26, 5, 1, '#C98B63');
  d.tx('Homeowner', sx + 34, sy + 16, {color: CREAM}); disc(sx + 36 + Math.ceil(d.tw('Homeowner')) + 5, sy + 22, 2, GOLD);
  /* the quote you sent */
  const bw = 132, bh = 52, bx = sx + sw - 8 - bw, by = sy + 50;
  P(bx + 1, by, bw - 2, bh, '#3B82C4'); P(bx, by + 1, bw, bh - 2, '#3B82C4'); P(bx + 1, by, bw - 2, 1, '#87CEEB'); P(bx + bw, by + bh - 6, 3, 4, '#3B82C4');
  P(bx + 7, by + 7, 26, 38, CREAM); P(bx + 7, by + 7, 26, 7, ORANGE); for (let j = 0; j < 5; j++) P(bx + 11, by + 19 + j * 5, 18 - (j % 2) * 6, 1, GREY);
  d.tx('Quote.pdf', bx + 40, by + 9, {color: CREAM});
  d.tx('Seen', bx + 40, by + 29, {color: '#BDE6F5'});
  [0, 4].forEach((dx) => { DOT(bx + 72 + dx, by + 36, '#BDE6F5'); DOT(bx + 73 + dx, by + 37, '#BDE6F5'); line(bx + 74 + dx, by + 36, bx + 77 + dx, by + 33, '#BDE6F5'); });
  /* no typing bubble under it: Seen, and the chat stays empty (dots would read as "they're typing") */
  /* the empty composer at the screen's foot */
  P(sx, sy + sh - 30, sw, 30, CREAM); P(sx, sy + sh - 30, sw, 1, SAND); P(sx + 6, sy + sh - 24, sw - 40, 18, '#F4E6D3');
  d.tx('Text message', sx + 11, sy + sh - 22, {color: '#B39A88', lint: false});
  disc(sx + sw - 16, sy + sh - 15, 8, '#9AA0AD');
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 2',
  transitions: {homework: 'dissolve', text: 'door', turn: 'blinds', close: 'levelselect'},
  sections: {
    /* ---- hook and stakes: the street. The cover is settled on frame 0 (the van parked at the job, the QUOTE sign, */
    /* the hook in a window in the sky); a cut in to the phone close-up and back out; on "driveway" the van pulls away. */
    hook: (k, T) => {
      const n = k.data.numbers, d = px(k);
      const tSkip = wordT(k, 'hook.skip', /^bring/i), tSend = k.S('hook.send'), tSt = k.S('hook.stakes');
      /* three shots (IMPROVE 00a): the cover (frame 0) holds to "quiet"; cut in to the phone close-up, Snow comes in big;
         cut back out on "One" to the street, Snow on at his usual size. The dialog box waits for "Here's what you send". */
      const tIn = Math.min(0.8, Math.max(0.5, wordT(k, 'hook', /^quiet/i, 0.7))), tOut = Math.min(2.6, Math.max(tIn + 0.6, wordT(k, 'hook', /^one$/i, 1.7)));
      if (T >= tIn && T < tOut) { quietPhone(k); return Object.assign(host(k), {hostScale: 1.5, hostX: 200, speech: false}); }
      const tCount = wordT(k, 'hook.count', /^thirty/i), tBar = k.S('hook.bar'), tDrive = wordT(k, 'hook.drive', /^pull/i), tRest = k.S('hook.rest');
      route(k, {t0: -3, stopAt: -1.6, sign: 'QUOTE'}, [{at: tDrive, drive: null, speed: 2}]);
      lawn(d);
      /* the window in the sky: tall for the hook card, shrinks to its two lines on "text instead", grows back for the
         stakes (whole pixels, 8 frames each way) */
      const hCard = 158, hSend = 66;   /* 158: the Sources line keeps 15 px inside the inner rule */
      const h = T < tSend ? hCard : (T < tSt ? hSend + Math.round((hCard - hSend) * (1 - eo(d.fr(tSend) / 8))) : hSend + Math.round((hCard - hSend) * eo(d.fr(tSt) / 8)));
      skyWin(d, h);
      if (T < tSend) {   /* the hook card */
        const cw = k.measure('THE TEXT', {size: 30}) + 36;
        k.chip('The Text', 540 - cw / 2, 276, {size: 30, fill: 'accent', color: INK});
        k.slam('Quote went', 540, 320, -1, {size: 132, color: CREAM, align: 'center', drop: INK});
        k.slam('quiet?', 540, 456, -1, {size: 132, color: 'accent', align: 'center', drop: INK});
        k.text('Send this text.', 540, 594, {size: 66, color: CREAM, align: 'center'});
        k.text('Sources: ServiceTitan, Jobber, Housecall Pro', 540, 666, {size: 30, color: SAND, align: 'center'});
        /* two small bursts in the clear space either side of "quiet?" (x 396 to 684), never on its glyphs */
        k.burst(330, 520, 0.45, {n: 8, r: 60}); k.burst(760, 520, 0.45, {n: 8, r: 60}); k.sweep(390, 590, 300, 6, 1.2, {color: 'accent'});
        /* after frame 0: stars wink in the card's empty corners (never on a line of text). No typing bubble over the
           house: the quote was seen and nobody is answering */
        if (T >= 0.4) {
          [[32, 100], [328, 100], [42, 168], [318, 164], [30, 222], [330, 222]].forEach(([x, y], i) => { const f = Math.floor((T - 0.4) * 6) + i * 2; d.twinkle(x, y, f % 6 < 4 ? f % 4 : 0, i % 2 ? GOLD : CREAM); });
        }
        /* "just checking in" from the van, struck once it has been read */
        if (T >= tSkip) {
          const s = 'Just checking in!', bw = Math.ceil(d.tw(s)) + 12, bx = 310 - bw, by = 252, f = d.fr(tSkip), up = f < 4 ? [4, 2, 1, 0][f] : 0;
          d.P(bx - 1, by - 1 + up, bw + 2, 21, INK); d.P(bx, by + up, bw, 19, CREAM); d.P(bx, by + up, bw, 1, '#FFFFFF'); d.P(bx + bw - 40, by + 19 + up, 5, 4, CREAM); d.P(bx + bw - 39, by + 23 + up, 3, 2, CREAM);
          d.tx(s, bx + 6, by + 3 + up, {color: '#4A4E5A'});
          if (T >= tSkip + 0.4) d.P(bx + 4, by + 9 + up, Math.round((bw - 8) * eo(d.fr(tSkip + 0.4) / 5)), 2, RED);
        }
        if (T < tIn) return {host: false, speech: false};
        return Object.assign(host(k), {speech: false});
      }
      if (T < tSt) {   /* "Send this text." at the cover's headline size, the window hugging its two lines */
        k.slam('Send this text.', 540, 282, tSend, {size: 132, color: 'accent', align: 'center', from: 0.5, drop: INK});
        k.slam('Not "just checking in."', 540, 402, tSend + 0.25, {size: 39, color: SAND, align: 'center', from: 0.4});
        k.burst(130, 340, tSend + 0.1, {n: 8, r: 60}); k.burst(950, 340, tSend + 0.1, {n: 8, r: 60});   /* beside the line, never on its glyphs */
        return host(k, 'point');
      }
      /* the stakes: the chip, the source line 12 px under it, then the 37% at twice the size with its bar right under it
         (the empty track shows from the start; it fills with the count) */
      k.chip("ServiceTitan's own data", 72, 274, {size: 30, fill: 'accent', color: INK});
      k.text(`ServiceTitan blog, ${n.stYear.shown}`, 72, 334, {size: 30, color: SAND});
      const x0 = 24, W = 286, frac = n.closePct.value / 100, BY = 186;
      if (T >= tCount) {
        const big = cnt(k, n.closePct, tCount, {suffix: '%'}), rx = 72 + Math.ceil(k.measure(n.closePct.shown, {size: 264})) + 36;
        k.slam(big, 72, 354, tCount, {size: 264, color: 'accent', from: 0.6, drop: INK});
        k.burst(250, 470, tCount + 0.7, {n: 18, r: 260});
        k.slam('of estimates close', rx, 420, tCount + 0.3, {size: 39, color: CREAM, from: 0.4});
        k.slam('on the first visit', rx, 468, tCount + 0.45, {size: 39, color: CREAM, from: 0.4});
      } else {   /* until the number is said: the claim fills the window, one estimate sheet after another lands */
        k.slam('Estimates that close', 72, 384, tSt + 0.2, {size: 39, color: CREAM, from: 0.4});
        k.slam('on the first visit:', 72, 432, tSt + 0.4, {size: 39, color: CREAM, from: 0.4});
        for (let i = 0; i < 3; i++) { const at = tSt + 0.6 + i * 0.5, f = d.fr(at); if (f < 0) continue; const y = 130 - (f < 4 ? [6, 3, 1, 0][f] : 0); d.P(240 + i * 30, y, 22, 28, INK); d.P(241 + i * 30, y + 1, 20, 26, CREAM); d.P(241 + i * 30, y + 1, 20, 5, ORANGE); for (let j = 0; j < 3; j++) d.P(244 + i * 30, y + 10 + j * 5, 14 - j * 3, 1, GREY); }
      }
      if (h >= hCard) {   /* the bar: the share that closed fills with the count, the rest stays open */
        const p = T >= tCount ? eo((T - tCount) / 0.7) : 0, fw = Math.round(W * frac * p);
        d.P(x0 - 1, BY - 1, W + 2, 12, INK); d.P(x0, BY, W, 10, '#3D2E45'); d.P(x0, BY, fw, 10, ORANGE); d.P(x0, BY, fw, 2, GOLD);
        if (T >= tBar && T < tRest) {   /* the bar's two labels at the display font (33 px caps, over the 36 px label floor) */
          k.slam('closed', x0 * 3, 606, tBar, {size: 66, color: 'accent', from: 0.5});
          k.slam('still open', (x0 + W * frac + W * (1 - frac) / 2) * 3, 606, tBar + 0.15, {size: 66, color: CREAM, from: 0.5, align: 'center'});
        }
      }
      if (T >= tRest) {
        k.slam('The rest depend on your follow-up.', 72, 606, tRest, {size: 39, color: CREAM, from: 0.5});
        k.sweep(72 + k.measure('The rest depend on your ', {size: 39}), 650, k.measure('follow-up.', {size: 39}), 6, tRest + 0.4, {color: 'accent'});
      }
      return host(k, k.live('hook.count') ? 'point' : null);
    },

    /* ---- homework: the fridge. "Just checking in!" buzzes the phone, the reply becomes a sticky note, the week's */
    /* notes bury it; then Jobber's three tips on a card */
    homework: (k, T) => {
      const d = px(k), t0 = k.S('homework'), tSheet = k.S('homework.sheet'), tWrite = wordT(k, 'homework.write', /^write/i);
      const tOff = wordT(k, 'homework.off', /^puts/i, 1), tFix = k.S('homework.fix');
      fridge(k, {buzzAt: t0 + 0.2});
      /* the text on the phone: a bubble over the counter */
      const cardIn = T >= tFix ? d.ease(tFix, 8, -160) : null;
      if (cardIn == null || cardIn < -120) {
        const s = 'Just checking in!', bw = Math.ceil(d.tw(s, 30)) + 12, f = d.fr(t0 + 0.2), up = f >= 0 && f < 4 ? [4, 2, 1, 0][f] : 0;
        if (f >= 0) { d.P(16, 196 - 2 + up, bw + 2, 20, INK); d.P(17, 197 - 2 + up, bw, 18, '#3B82C4'); d.P(104, 213 + up, 4, 4, '#3B82C4');   /* 2 px taller: the J and g descenders clear the border; the text sits 2 px up so the space over the caps and under the descenders matches */ d.tx(s, 23, 197 + up, {size: 30, color: CREAM}); }
      }
      /* the notes: the plumber's, then the week piles on; Dentist lands right on top of it */
      const A = [166, 152], B = [254, 152], C = [166, 220], D = [254, 220];
      const tDent = tOff + 0.4, buried = T >= tDent + 0.1;
      const ay = note(k, A[0], A[1], GOLD, ['Reply to', 'plumber'], t0 + 0.6, {hidden: buried, seed: 1});
      if (!buried && T >= tWrite && ay != null) {   /* the pencil writes a few squiggles, stops halfway and hovers */
        const p = clamp((T - tWrite) / 0.8), len = Math.round(30 * p), y = ay + 44;
        for (let x = 0; x < len; x++) d.DOT(A[0] + 6 + x, y + [0, -1, -2, -1, 0, 1, 1, 0][x % 8], '#3D2E45');
        const px0 = A[0] + 6 + len, py0 = y - 12 + (p >= 1 ? ((d.F >> 3) & 1) : 0);
        d.line(px0, py0 + 10, px0 + 9, py0, INK, 2); d.line(px0 + 1, py0 + 9, px0 + 8, py0 + 1, ORANGE); d.P(px0 + 8, py0 - 1, 3, 3, '#E2633B'); d.DOT(px0, py0 + 11, INK);
      }
      note(k, B[0], B[1], '#87CEEB', ['Soccer', '4pm'], tOff, {pin: TEAL, seed: 2});
      note(k, A[0] + 4, A[1] + 4, '#F2A541', ['Dentist'], tDent, {pin: '#3B82C4', seed: 0});
      note(k, C[0], C[1], TEAL, ['Pay bills'], tOff + 0.8, {pin: GOLD, seed: 2, top: '#BDE6F5'});
      note(k, D[0], D[1], CREAM, ['Groceries'], tOff + 1.2, {pin: RED, seed: 1, top: '#E6D3BC'});
      /* HOMEWORK: a red tag stamped onto the freezer door right above the note, an arrow stepping down at it */
      if (T >= tSheet) {
        const f = d.fr(tSheet), sq = f < 2 ? 1 : 0, tw0 = Math.ceil(d.tw('HOMEWORK')) + 12;
        d.P(A[0] - 1, 118 - 1 + sq, tw0 + 2, 19 - sq, INK); d.P(A[0], 118 + sq, tw0, 17 - sq, RED); d.P(A[0], 118 + sq, tw0, 1, ORANGE);
        k.slam('HOMEWORK', (A[0] + 6) * 3, 121 * 3, tSheet, {size: 39, color: CREAM, stamp: true, glint: false});
        if (!buried) { const ab = (d.F >> 3) & 1; d.P(A[0] + 36, 138 + ab, 6, 4, RED); d.P(A[0] + 37, 142 + ab, 4, 2, RED); d.P(A[0] + 38, 144 + ab, 2, 2, RED); }
      }
      /* Jobber's tips: a game window slides in over the counter; a check lands on each tip as it is said */
      if (cardIn != null) {
        const X = 8 + cardIn, tips = [['Their name.', wordT(k, 'homework.name', /^name/i)], ['The job.', wordT(k, 'homework.job', /^job/i)], ['A question.', wordT(k, 'homework.ask', /^question/i)]];
        d.win(X, 86, 138, 176, {base: '#253048', hi: '#3B82C4', lo: '#1B1420', rule: '#5B8FB9'});
        if (cardIn === 0) {
          d.tx("Jobber's tips", X + 8, 94, {color: GOLD});
          d.P(X + 8, 110, 120, 1, '#5B8FB9');
          tips.forEach(([s, at], i) => {
            const y = 122 + i * 34;
            d.P(X + 8, y, 13, 13, INK); d.P(X + 9, y + 1, 11, 11, '#1B1420');
            if (T >= at) { const f = d.fr(at); d.line(X + 10, y + 6, X + 13, y + 9, TEAL, 2); d.line(X + 13, y + 9, X + 19, y + 1 - (f < 2 ? 1 : 0), TEAL, 2); if (f >= 0 && f < 8) d.twinkle(X + 20, y, f >> 1, GOLD); }
            if (T >= at) k.slam(s, (X + 28) * 3, y * 3, at, {size: 39, color: CREAM, from: 0.4}); else d.P(X + 28, y + 11, 90, 1, '#3B82C4');
          });
          d.tx('Jobber Academy,', X + 8, 222, {size: 30, color: SAND}); d.tx(k.data.numbers.jbYear.shown, X + 8, 235, {size: 30, color: SAND});   /* two lines: 12 px clear of the inner rule */
        }
      }
      return host(k, k.live('homework.off') ? 'shrug' : (k.live('homework.sheet') ? 'point' : null));
    },

    /* ---- the text: the chat set in the truck, our own build on it. The keyboard comes up; each line types into the
       input bar as it is said and goes up on the word that sends it; on "question" the homeowner's phone rises with it
       on the lock screen, YES and NO as its reply buttons, each pressed as it is said */
    text: (k, T) => {
      const t0 = k.S('text');
      const tA = [wordT(k, 'text.name', /^Their/i), wordT(k, 'text.name', /^name/i), wordT(k, 'text.name', /^then/i), wordT(k, 'text.name', /^yours/i)];
      const tSendA = wordT(k, 'text.know', /^know/i, 0.4);
      const tB = spoken(wordT(k, 'text.line', /^Still/i, 1.6), LINE_B);
      const tHold = wordT(k, 'text.hold', /^That/i), tQ = wordT(k, 'text.hold', /^question/i, 0.6);
      const tYes = wordT(k, 'text.yesno', /^yes/i), tNo = wordT(k, 'text.yesno', /^no/i);
      k.sets.chat({who: 'Homeowner', msgs: []});
      const settled = T >= tQ + 8 / 30;   /* once their phone covers ours, ours is not drawn under it */
      if (!settled) {
        const draft = T < tSendA ? typed(k, LINE_A, tA, 148) : (T >= tB[0] - 0.3 && T < tHold ? typed(k, LINE_B, tB, 148) : null);
        const words = LINE_A.split(' ').map((w, i) => [w, tA[i]]).concat(LINE_B.split(' ').map((w, i) => [w, tB[i]]));
        truckPhone(k, {kbAt: t0 + 0.15, draft, words, sentAt: T >= tHold ? tHold : (T >= tSendA ? tSendA : null),
          sent: [{quote: true, at: -1}, {text: LINE_A, at: tSendA}, {text: LINE_B, at: tHold}]});
      }
      if (T >= tQ) {
        const r = lockScreen(k, {at: tQ, yesAt: tYes, noAt: tNo});
        k.burst(r.card[0], r.card[1], tQ + 0.3, {n: 16, r: 220});
      }
      return host(k, k.live('text.hold') || k.live('text.yesno') ? 'point' : null);
    },

    /* ---- the turn: the mail desk. Text it, don't email it; then the 59% */
    turn: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('turn'), tText = k.S('turn.text'), tDont = wordT(k, 'turn.text', /^Don/i, 0.6);
      const tSt = k.S('turn.st'), tHcp = k.S('turn.hcp'), tPct = wordT(k, 'turn.hcp', /^fifty/i, 0.2), tFits = wordT(k, 'turn.pct', /^updates/i, 1.4) + 0.3;
      desk(k, {t0, textAt: tText + 0.2, laptopOut: tHcp, checkAt: tFits});
      d.win(14, 86, 332, 26, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: null});
      k.slam('The part people skip.', 72, 273, t0 + 0.1, {size: 39, color: GOLD, from: 0.5});
      if (T >= tText) { k.slam('Text it.', 920, 336, tText, {size: 66, color: 'accent', align: 'right', from: 0.5, drop: INK}); k.burst(820, 370, tText + 0.1, {n: 14, r: 200}); }
      if (T >= tDont && T < tHcp) k.slam("Don't email it.", 60, 336, tDont, {size: 66, color: GREY, from: 0.4, drop: INK});
      if (T >= tSt && T < tHcp) {
        k.slam('Texts beat email', 300, 810, tSt, {size: 39, color: CREAM, from: 0.4});
        k.slam('on open rates.', 300, 856, tSt + 0.15, {size: 39, color: CREAM, from: 0.4});
        k.sweep(300, 900, k.measure('on open rates.', {size: 39}), 6, tSt + 0.5, {color: 'accent'});
        k.text(`ServiceTitan follow-up webinar, ${n.stYear.shown}`, 300, 920, {size: 30, color: SAND});
      }
      if (T >= tHcp) {   /* the laptop is gone; the survey's window slides in where it was */
        const sl = d.ease(tHcp + 0.15, 10, -230);
        /* the window holds the 59% at the 37%'s size, its two lines, and both source lines (all inside 12 px of the rule) */
        d.win(14 + sl, 130, 196, 166, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#7A3442'});
        if (sl === 0) {   /* the 59% counts in the moment the box lands, so it is never an empty box; the sources land with it */
          const tBox = tHcp + 0.15 + 10 / 30, tLab = Math.max(tPct + 0.3, tBox + 0.2);
          k.slam(cnt(k, n.textPct, tBox, {suffix: '%'}), 72, 402, tBox, {size: 264, color: 'accent', from: 0.6, drop: INK}); k.burst(530, 520, tBox + 0.7, {n: 10, r: 60});
          if (T >= tLab) { k.slam('of homeowners', 72, 678, tLab, {size: 39, color: CREAM, from: 0.4}); k.slam('expect text updates.', 72, 720, tLab + 0.2, {size: 39, color: CREAM, from: 0.4}); }
          k.text('Housecall Pro survey,', 72, 776, {size: 30, color: SAND});
          k.text(`${n.hcpSample.shown} U.S. homeowners, ${n.hcpYear.shown}`, 72, 815, {size: 30, color: SAND});
        }
        if (T >= tFits) k.burst(820, 690, tFits + 0.05, {n: 16, r: 200, colors: ['teal', 'paper']});
      }
      return host(k, k.live('turn.text') || k.live('turn.pct') ? 'point' : null);
    },

    /* ---- close: the level-up screen. A perk on each "one"; LEVEL UP on "question"; the send line in one column */
    close: (k, T) => {
      const d = px(k), t0 = k.S('close');
      const tName = wordT(k, 'close', /^name/i), tJob = wordT(k, 'close', /^job/i, 0.8), tQ = wordT(k, 'close', /^question/i, 1.6);
      const send = k.S('close.send'), quiet = k.S('close.quiet'), know = k.S('close.know');
      k.sets.levelup({from: 0, to: 100, max: 100, at: t0, dur: Math.max(0.6, tQ - t0), levelAt: tQ, level: 2, text: 'LEVEL UP!', stats: []});
      /* the perks, the chip and the send line share one left edge (x 300, low-res 100): the send line at size 66 needs */
      /* 630 px for its second line, so the column starts there to end inside x 930. Each perk slides in on its "one" */
      const perks = [['ONE NAME', tName], ['ONE JOB', tJob], ['ONE QUESTION', tQ]], bx = 100;
      /* the floor: an arcade cabinet's control deck in place of the set's tiled stage (stick, three buttons, coin door) */
      { const {P, disc, DOT} = d;
        P(0, 417, 360, 223, '#3D2E45'); P(0, 417, 360, 3, '#5A4A63'); P(0, 420, 360, 2, INK); P(0, 470, 360, 2, '#2B2033');
        P(0, 422, 360, 48, '#4A3A55'); for (let x = 6; x < 360; x += 24) DOT(x, 446, '#2B2033');
        P(176, 430, 8, 24, '#9AA0AD'); disc(180, 428, 9, RED); DOT(177, 424, '#F2A541'); P(166, 452, 28, 6, INK);
        [[240, TEAL], [272, GOLD], [304, RED]].forEach(([x, c], i) => { const on = ((d.F >> 4) + i) % 3 === 0; disc(x, 446, 9, INK); disc(x, 445 + (on ? 1 : 0), 8, c); DOT(x - 3, 441 + (on ? 1 : 0), CREAM); });
        P(130, 500, 100, 120, '#2B2033'); P(130, 500, 100, 2, '#5A4A63'); P(130, 618, 100, 2, INK);
        [[150, 530], [194, 530]].forEach(([x, y]) => { P(x, y, 16, 34, INK); P(x + 1, y + 1, 14, 32, (d.F >> 4) % 2 ? ORANGE : '#F2A541'); P(x + 6, y + 6, 4, 22, INK); });
        P(152, 580, 56, 4, '#5A4A63');
        [[20, 506], [250, 506]].forEach(([x, y]) => { P(x - 1, y - 1, 92, 102, INK); P(x, y, 90, 100, '#1B1420'); for (let j = 0; j < 9; j++) P(x + 6, y + 8 + j * 10, 78, 4, '#352840'); }); }   /* the cabinet's two speaker grilles */
      /* the perks: while "The rule:" is up they are big, one line each; once the level ticks over they settle into a small */
      /* list (16 px low-res apart, so the send line gets its 50 px of air and still clears Snow's name tag at y 1012) */
      const big = T < tQ + 0.6, bigW = Math.max(...perks.map(([s]) => k.measure('+ ' + s, {size: 66}))), bigX = Math.round(540 - bigW / 2);
      perks.forEach(([s, at], i) => {
        if (T < at) return;
        if (big) { k.slam('+ ' + s, bigX, 708 + i * 78, at, {size: 66, color: CREAM, from: 0.4, drop: INK}); return; }
        const sl = d.ease(at, 5, 30); d.tx('+', bx + sl, 236 + i * 16, {color: TEAL}); d.tx(s, bx + 12 + sl, 236 + i * 16, {color: CREAM});
      });
      /* LV 3 starts earning: from "Send this" the first 3 segments fill one by one, each blinking while it fills */
      if (T >= tQ) for (let i = 0; i < 3; i++) {
        const at = send + 0.15 + i * 0.25; if (T < at) break;
        const x = Math.round(30 + i * 14), lit = T >= at + 0.25 || ((d.F >> 1) & 1);
        if (lit) { d.P(x + 1, 209, 12, 12, TEAL); d.P(x + 1, 209, 12, 3, '#BDE6F5'); d.P(x + 1, 218, 12, 3, '#2F6F67'); } else d.P(x + 1, 209, 12, 12, '#3D2E45');
      }
      if (T < tQ) k.slam('The rule:', 540, 420, t0 + 0.1, {size: 132, color: CREAM, align: 'center', from: 0.5, drop: INK});
      if (T >= quiet) {
        const echo = T >= know;
        k.slam(echo ? 'Now you know what to send.' : 'Exact text in the caption.', 540, 506, echo ? know : quiet, {size: 39, color: echo ? GOLD : CREAM, align: 'center', from: 0.4, drop: INK});
      }
      if (T >= send) {   /* the send line ranks second after LEVEL UP!: size 66, its ink 45 px under the perk list (ends */
        /* y 837), line 2 ending y 996, clear of Snow's name tag (y 1012) and inside x 930 (504 and 630 px wide from x 300) */
        k.chip('ProofNotFluff', 300, 276, {size: 30});
        k.slam('Send this to whoever', 300, 870, send, {size: 66, color: 'accent', from: 0.5, drop: INK});
        k.slam('follows up on your quotes.', 300, 936, send + 0.15, {size: 66, color: 'accent', from: 0.5, drop: INK});
      }
      return host(k, k.live('close.know') ? 'wave' : (k.live('close.send') ? 'point' : null));
    },
  },
};
