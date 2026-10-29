// Scene: The text that revives a quote that went quiet (lesson 2, The Text, arcade). One function per top-level cue in
// 03_cues/cues.md. Numbers only from k.data (brief.md -> data.js). Every time comes from a cue start (k.S) or a spoken
// word (wordT, spoken), never a typed number, so the re-voiced takes move the picture with them.
// Worlds (brief.md): hook and stakes = the street (one section: the van parked at the job, then it pulls away); homework =
// the homeowner's fridge (our own piece); text = the chat set in the truck; turn = the mail desk (our own piece); cadence =
// the street again, three trips; close = the level-up screen. No stock room. The camera holds still (pixel art never scales).
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', GREY = '#9AA0AD';
const QUOTE_MSG = "Here's your quote for the new water heater.";
const LINE_A = "Hi [name], it's [you].";
const LINE_B = 'Still want that water heater swapped before winter?';
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eo = (x) => 1 - Math.pow(1 - clamp(x), 3);
const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };

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
  const spr = (rows, pal, x, y, s = 1) => rows.forEach((r, j) => { for (let i = 0; i < r.length; i++) { const c = pal[r[i]]; if (c) P(x + i * s, y + j * s, s, s, c); } });
  const twinkle = (x, y, f, c = CREAM) => { const s = [0, 1, 2, 1][((f % 4) + 4) % 4]; DOT(x, y, c); for (let i = 1; i <= s; i++) { DOT(x - i, y, c); DOT(x + i, y, c); DOT(x, y - i, c); DOT(x, y + i, c); } };
  return {P, DOT, dith, disc, ring, line, win, fr, ease, tx, tw, clip, spr, twinkle, F, T};
};

// ---- the words: every beat lands on a spoken word ----
const WS = () => (window.WORDS && window.WORDS.words) || [];
const norm = (s) => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
// the time a word is said, within 6 s after a cue (or a time); falls back to the cue's start plus dflt. Leading quote
// marks are ignored ('"Still' is Still), and the search never runs on into a later take's same word.
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && x.start < t0 + 6 && re.test(String(x.w).replace(/^[^\w]+/, '')));
  return w ? w.start : t0 + dflt;
};
// the start of each spoken word of a line, matched in order from t0 (a missing word takes the one before's time)
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
// a count that starts at 85% of its value and lands exactly on it
const cnt = (k, num, t0, o = {}) => k.count(num.value, k.lin(t0, t0 + 0.7) >= 1 ? 1 : 0.85 + 0.15 * k.lin(t0, t0 + 0.7), Object.assign({from: 0}, o));
const host = (k, pose) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150});

// ================================================================================================================
// the street: the library set, chained into trips. Each trip is its own k.sets.street call, started so the world
// position carries on from where the last one parked (no jump), and the last stop's sign is drawn again here so it
// slides off behind the van instead of vanishing.
const V = 30, SD = 0.8;
const streetPos = (T, o) => { const v = V * (o.speed || 1), sd = o.stopDur || SD; const d = Math.max(0, T - o.t0); if (o.stopAt == null) return v * d; const ds = Math.max(0, o.stopAt - o.t0); if (d <= ds) return v * d; const e = Math.min(d - ds, sd); return v * ds + v * (e - e * e / (2 * sd)); };
const parked = (o) => streetPos(o.stopAt + (o.stopDur || SD) + 1, o);
const sign = (d, sx, label) => {   // the yard sign as sets.js draws it, settled
  const w = Math.max(30, Math.ceil(d.tw(label)) + 10);
  if (sx < -60 || sx > 380) return;
  d.P(sx + 4, 270, 2, 22, '#6B4226'); d.P(sx + w - 6, 270, 2, 22, '#6B4226');
  d.P(sx - 1, 249, w + 2, 22, INK); d.P(sx, 250, w, 20, CREAM); d.P(sx + 1, 251, w - 2, 1, RED); d.P(sx + 1, 268, w - 2, 1, RED); d.P(sx, 269, w, 1, SAND);
  d.tx(label, sx + w / 2, 254, {align: 'center', color: '#7A3442'});
};
// base: the parked call ({t0, stopAt, sign}); trips: [{at, drive, sign, speed}] (drive null: keeps going)
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

// ================================================================================================================
// the fridge (homework): our own piece. A kitchen wall, a counter with a kettle and the homeowner's phone, a clock that
// ticks, and the fridge: freezer door with a kid's drawing and magnets, main door where sticky notes slap on.
const NOTE_W = 78, NOTE_H = 60;
const fridge = (k, o) => {
  const d = px(k), {P, DOT, disc, ring, line, fr, F, T} = d;
  // the wall and its stripes, the backsplash, the counter and its cabinets, the floor
  P(0, 0, 360, 417, '#F4E6D3'); for (let x = 4; x < 360; x += 12) P(x, 0, 1, 196, '#E6D3BC');
  for (let y = 196, r = 0; y < 250; y += 9, r++) for (let x = (r & 1) * 6 - 6; x < 150; x += 12) { P(x, y, 11, 8, '#BDE6F5'); P(x, y, 11, 1, CREAM); P(x, y + 7, 11, 1, '#87CEEB'); }
  P(0, 250, 150, 6, '#C9CCD3'); P(0, 250, 150, 1, CREAM); P(0, 255, 150, 1, '#6B7080');
  P(0, 256, 150, 161, '#8C5A33'); for (let x = 4; x < 150; x += 48) { P(x, 262, 42, 60, '#B07A47'); P(x, 262, 42, 1, '#D9A066'); P(x + 34, 288, 4, 2, '#6B4226'); }
  for (let y = 417, r = 0; y < 640; y += 16, r++) for (let x = (r & 1) * 16 - 16; x < 360; x += 32) { P(x, y, 16, 16, '#C9CCD3'); P(x + 16, y, 16, 16, '#9AA0AD'); }
  // the clock: the second hand steps once a second
  const cx = 52, cy = 120;
  disc(cx, cy, 17, INK); disc(cx, cy, 15, CREAM); ring(cx, cy, 15, '#B07A47', 2);
  for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6; DOT(cx + Math.round(Math.cos(a) * 11), cy + Math.round(Math.sin(a) * 11), '#6B7080'); }
  const sa = (Math.floor(T) % 60) * Math.PI / 30 - Math.PI / 2; line(cx, cy, cx + Math.round(Math.cos(sa) * 12), cy + Math.round(Math.sin(sa) * 12), RED);
  line(cx, cy, cx + 6, cy - 4, INK); line(cx, cy, cx, cy - 9, INK);
  // the kettle, steam puffing up on whole pixels
  P(16, 232, 26, 18, INK); P(17, 233, 24, 16, RED); P(17, 233, 24, 2, ORANGE); P(24, 228, 12, 5, INK); P(25, 229, 10, 3, '#7A3442'); P(41, 236, 6, 3, INK);
  for (let i = 0; i < 4; i++) { const a = (F + i * 9) % 36; P(44 + Math.floor(a / 6) % 2, 230 - a, 3 + (a > 18 ? 1 : 0), 3, a > 24 ? '#E6D3BC' : CREAM); }
  // the homeowner's phone, standing on the counter; it buzzes (a pixel either side) when a text lands
  const bz = o.buzzAt != null && T >= o.buzzAt && T < o.buzzAt + 0.5 ? ((F >> 1) & 1 ? 1 : -1) : 0;
  P(108 + bz, 220, 20, 30, INK); P(109 + bz, 221, 18, 28, '#253048'); P(110 + bz, 223, 16, 22, o.buzzAt != null && T >= o.buzzAt ? '#87CEEB' : '#3B82C4');
  if (o.buzzAt != null && T >= o.buzzAt) { P(112 + bz, 226, 12, 3, CREAM); P(112 + bz, 231, 8, 2, CREAM); }
  // the fridge
  const FX = 150, FY = 74, FW = 192, FH = 258;
  P(FX - 1, FY - 1, FW + 2, FH + 2, INK); P(FX, FY, FW, FH, '#F4E6D3'); P(FX, FY, FW, 1, '#FFFFFF'); P(FX, FY, 1, FH, CREAM); P(FX + FW - 3, FY, 3, FH, '#E6D3BC');
  P(FX, 144, FW, 2, '#B39A88'); P(FX, 146, FW, 1, CREAM);
  P(FX + 4, 92, 3, 40, '#9AA0AD'); P(FX + 4, 92, 1, 40, CREAM); P(FX + 4, 158, 3, 70, '#9AA0AD'); P(FX + 4, 158, 1, 70, CREAM);
  P(FX + 6, FY + FH + 1, FW - 12, 5, '#4A4E5A'); for (let x = FX + 10; x < FX + FW - 10; x += 4) P(x, FY + FH + 2, 2, 3, '#6B7080');
  // the freezer door: a kid's drawing (a house, a sun) under two magnets
  P(290, 82, 44, 54, INK); P(291, 83, 42, 52, CREAM);
  line(298, 112, 311, 100, '#3B82C4'); line(311, 100, 324, 112, '#3B82C4'); P(300, 112, 22, 16, '#E2633B'); P(308, 118, 6, 10, '#F2A541'); disc(325, 92, 4, ORANGE);
  for (let i = 0; i < 3; i++) P(294 + i * 12, 130, 6, 2, '#3E7A62');
  disc(298, 84, 3, TEAL); disc(326, 84, 3, RED);
  // magnets on the main door that the notes sit beside; they wobble a pixel now and then
  [[176, 300, RED], [218, 306, TEAL], [300, 296, GOLD]].forEach(([mx, my, c], i) => { const w = ((F >> 4) + i) % 5 === 0 ? 1 : 0; disc(mx, my - w, 4, INK); disc(mx, my - w, 3, c); DOT(mx - 1, my - 2 - w, CREAM); });
  return {fx: FX, fy: FY};
};
// a sticky note: it slaps on (a drop and a one-pixel squash) and its corner curls up and down
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

// ================================================================================================================
// the chat set's message layout, worked out the way sets.js does it, so words can wait under the bubble until said
const CH = {sx: 102, sy: 90, sw: 188, cy0: 130, cy1: 296, maxW: 130};
const chatBoxes = (k, msgs) => {
  const d = px(k), items = [];
  msgs.forEach((m) => {
    if (k.T < m.at) return;
    const ls = k.wrap(m.text, {size: 39}, (CH.maxW - 12) * 3).slice(0, 6), w = Math.min(CH.maxW, Math.ceil(Math.max(...ls.map((l) => d.tw(l)))) + 10);
    items.push({m, ls, w, h: ls.length * 15 + 8});
  });
  const total = items.reduce((a, it) => a + it.h + 6, 0), scroll = Math.max(0, total - (CH.cy1 - CH.cy0 - 4));
  let y = CH.cy0 + 4 - scroll;
  return items.map((it) => { const r = Object.assign({}, it, {bx: it.m.me ? CH.sx + CH.sw - 8 - it.w : CH.sx + 8, by: y + d.ease(it.m.at, 4, 8)}); y += it.h + 6; return r; });
};
// covers the words of a bubble not yet said with the bubble's own blue, and puts a cursor after the last one said
const typeMask = (k, box, times) => {
  const d = px(k); let wi = 0;
  d.clip(CH.sx, CH.cy0, CH.sw, CH.cy1 - CH.cy0, () => {
    box.ls.forEach((l, li) => {
      let pos = 0;
      l.split(' ').forEach((wd) => {
        const x = box.bx + 5 + (pos ? d.tw(l.slice(0, pos)) : 0), y = box.by + 4 + li * 15, ww = d.tw(wd), t = times[wi] != null ? times[wi] : 1e9;
        if (k.T < t) d.P(x - 1, y - 1, Math.ceil(ww) + 3, 15, '#3B82C4');
        pos += wd.length + 1; wi++;
      });
    });
    // the cursor sits after the last word said, blinking twice a second
    if (Math.floor(k.T * 2) % 2 === 0) {
      let last = null; wi = 0;
      box.ls.forEach((l, li) => { let pos = 0; l.split(' ').forEach((wd) => { if (k.T >= (times[wi] != null ? times[wi] : 1e9)) last = [box.bx + 5 + d.tw(l.slice(0, pos + wd.length)) + 1, box.by + 4 + li * 15]; pos += wd.length + 1; wi++; }); });
      if (!last) last = [box.bx + 5, box.by + 4];
      if (times.some((t) => k.T < t)) d.P(last[0], last[1], 1, 13, CREAM);
    }
  });
};

// ================================================================================================================
// the mail desk (turn): our own piece. Night outside the window; a laptop whose inbox fills with envelopes nobody opens;
// the phone on its stand with your text, read.
const desk = (k, o) => {
  const d = px(k), {P, DOT, disc, line, fr, ease, F, T} = d;
  P(0, 0, 360, 417, '#253048'); for (let y = 0; y < 262; y += 6) P(0, y, 360, 1, '#1F2A40');
  // the window: the moon and stars, the frame
  P(206, 0, 140, 80, INK); P(209, 0, 134, 77, '#1B1420');
  disc(318, 30, 9, '#E6D3BC'); disc(321, 27, 8, '#1B1420');
  for (let i = 0; i < 9; i++) { const f = Math.floor(F / 6) + i * 3; d.twinkle(214 + Math.floor(hash(i * 3.3) * 120), 8 + Math.floor(hash(i * 7.7) * 60), f % 9 < 4 ? f % 4 : 0, i % 2 ? GOLD : CREAM); }
  P(275, 0, 3, 77, INK); P(209, 38, 134, 3, INK);
  // the desk
  P(0, 262, 360, 6, '#B07A47'); P(0, 262, 360, 1, '#D9A066'); P(0, 268, 360, 149, '#6B4226'); for (let y = 274; y < 417; y += 10) P(0, y, 360, 1, '#5A3A22');
  P(0, 417, 360, 223, '#2B2033'); for (let y = 424; y < 640; y += 12) P(0, y, 360, 1, '#3D2E45');
  // the laptop and its inbox: a new envelope row lands every half second and pushes the others down, all unread
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
  // the phone on its stand; the screen holds your text (pixel lines), read ticks, a glow that pulses twice a second
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
  if (o.checkAt != null && T >= o.checkAt) {   // a check pops on the screen
    const f = fr(o.checkAt), s = f < 3 ? 1 : 0, cx = PX + 45, cy = PY + 98 - s;
    disc(cx, cy, 8 + s, '#2F6F67'); disc(cx, cy, 7 + s, TEAL);
    line(cx - 4, cy, cx - 1, cy + 3, CREAM, 2); line(cx - 1, cy + 3, cx + 4, cy - 3, CREAM, 2);
  }
  return {phone: [PX, PY]};
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 2',
  transitions: {homework: 'dissolve', text: 'door', turn: 'blinds', cadence: 'dissolve', close: 'levelselect'},
  sections: {
    // ---- hook and stakes: the street. The cover is settled on frame 0 (the van parked at the job, the QUOTE sign,
    // the hook in a window in the sky); on "driveway" the van pulls away and the sign slides off behind it.
    hook: (k, T) => {
      const n = k.data.numbers, d = px(k);
      const tSkip = wordT(k, 'hook.skip', /^checking/i), tSend = k.S('hook.send'), tSt = k.S('hook.stakes');
      const tCount = wordT(k, 'hook.count', /^thirty/i), tBar = k.S('hook.bar'), tDrive = wordT(k, 'hook.drive', /^pull/i), tRest = k.S('hook.rest');
      route(k, {t0: -3, stopAt: -1.6, sign: 'QUOTE'}, [{at: tDrive, drive: null, speed: 2}]);
      // the window in the sky: tall for the hook card, then it shrinks to the sky (whole pixels, 8 frames)
      const hCard = 146, hSky = 114, h = T < tSend ? hCard : hSky + Math.round((hCard - hSky) * (1 - eo(d.fr(tSend) / 8)));
      skyWin(d, h);
      if (T < tSend) {   // the hook card
        const cw = k.measure('THE TEXT', {size: 30}) + 36;
        k.chip('The Text', 540 - cw / 2, 276, {size: 30, fill: 'accent', color: INK});
        k.slam('Quote went', 540, 330, -1, {size: 132, color: CREAM, align: 'center', drop: INK});
        k.slam('quiet?', 540, 466, -1, {size: 132, color: 'accent', align: 'center', drop: INK});
        k.text('Send this text.', 540, 612, {size: 66, color: CREAM, align: 'center'});
        k.burst(700, 530, 1.0, {n: 18, r: 260}); k.sweep(390, 600, 300, 6, 1.6, {color: 'accent'});
        // "just checking in" from the van, struck once it has been read
        if (T >= tSkip) {
          const s = 'Just checking in!', bw = Math.ceil(d.tw(s)) + 12, bx = 310 - bw, by = 238, f = d.fr(tSkip), up = f < 4 ? [4, 2, 1, 0][f] : 0;
          d.P(bx - 1, by - 1 + up, bw + 2, 21, INK); d.P(bx, by + up, bw, 19, CREAM); d.P(bx, by + up, bw, 1, '#FFFFFF'); d.P(bx + bw - 40, by + 19 + up, 5, 4, CREAM); d.P(bx + bw - 39, by + 23 + up, 3, 2, CREAM);
          d.tx(s, bx + 6, by + 3 + up, {color: '#4A4E5A'});
          if (T >= tSkip + 0.4) d.P(bx + 4, by + 9 + up, Math.round((bw - 8) * eo(d.fr(tSkip + 0.4) / 5)), 2, RED);
        }
        return {host: false, speech: false};
      }
      if (T < tSt) {   // "Send this text." in the sky window
        k.slam('Send this text.', 540, 330, tSend, {size: 66, color: 'accent', align: 'center', from: 0.5, drop: INK});
        k.slam('Not "just checking in."', 540, 440, tSend + 0.25, {size: 39, color: SAND, align: 'center', from: 0.4});
        k.burst(540, 360, tSend + 0.1, {n: 16, r: 240});
        return host(k, 'point');
      }
      // the stakes: ServiceTitan's own data, the 37%, the bar, the rest
      k.chip("ServiceTitan's own data", 72, 274, {size: 30, fill: 'accent', color: INK});
      k.text(`ServiceTitan blog, ${n.stYear.shown}`, 72, 318, {size: 30, color: SAND});
      if (T >= tCount) {
        k.slam(cnt(k, n.closePct, tCount, {suffix: '%'}), 72, 356, tCount, {size: 132, color: 'accent', from: 0.6, drop: INK});
        k.burst(200, 420, tCount + 0.7, {n: 16, r: 220});
        k.slam('of estimates close', 380, 372, tCount + 0.3, {size: 39, color: CREAM, from: 0.4});
        k.slam('on the first visit', 380, 420, tCount + 0.45, {size: 39, color: CREAM, from: 0.4});
      } else {   // until the number is said: the source fills the window, one estimate sheet after another lands
        k.slam('Estimates that close', 72, 372, tSt + 0.2, {size: 39, color: CREAM, from: 0.4});
        k.slam('on the first visit:', 72, 420, tSt + 0.4, {size: 39, color: CREAM, from: 0.4});
        for (let i = 0; i < 3; i++) { const at = tSt + 0.6 + i * 0.5, f = d.fr(at); if (f < 0) continue; const y = 138 - (f < 4 ? [6, 3, 1, 0][f] : 0); d.P(240 + i * 30, y, 22, 28, INK); d.P(241 + i * 30, y + 1, 20, 26, CREAM); d.P(241 + i * 30, y + 1, 20, 5, ORANGE); for (let j = 0; j < 3; j++) d.P(244 + i * 30, y + 10 + j * 5, 14 - j * 3, 1, GREY); }
      }
      if (T >= tBar) {   // a bar: the share that closed, and the rest still open
        const p = eo((T - tBar) / 0.7), x0 = 24, W = 286, f = n.closePct.value / 100;
        d.P(x0 - 1, 163, W + 2, 12, INK); d.P(x0, 164, W, 10, '#3D2E45'); d.P(x0, 164, Math.round(W * f * p), 10, ORANGE); d.P(x0, 164, Math.round(W * f * p), 2, GOLD);
        if (T < tRest && p > 0.6) {
          k.slam('closed', x0 * 3, 528, tBar + 0.45, {size: 39, color: 'accent', from: 0.5});
          k.slam('still open', (x0 + W * f + W * (1 - f) / 2) * 3, 528, tBar + 0.6, {size: 39, color: CREAM, from: 0.5, align: 'center'});
        }
      }
      if (T >= tRest) {
        k.slam('The rest depend on your follow-up.', 72, 528, tRest, {size: 39, color: CREAM, from: 0.5});
        k.sweep(72 + k.measure('The rest depend on your ', {size: 39}), 572, k.measure('follow-up.', {size: 39}), 6, tRest + 0.4, {color: 'accent'});
      }
      return host(k, k.live('hook.count') ? 'point' : null);
    },

    // ---- homework: the fridge. "Just checking in!" buzzes the phone, the reply becomes a sticky note, the week's
    // notes bury it; then Jobber's three tips on a card
    homework: (k, T) => {
      const d = px(k), t0 = k.S('homework'), tSheet = k.S('homework.sheet'), tWrite = wordT(k, 'homework.write', /^write/i);
      const tOff = wordT(k, 'homework.off', /^puts/i, 1), tFix = k.S('homework.fix');
      fridge(k, {buzzAt: t0 + 0.2});
      // the text on the phone: a bubble over the counter
      const cardIn = T >= tFix ? d.ease(tFix, 8, -160) : null;
      if (cardIn == null || cardIn < -120) {
        const s = 'Just checking in!', bw = Math.ceil(d.tw(s, 30)) + 12, f = d.fr(t0 + 0.2), up = f >= 0 && f < 4 ? [4, 2, 1, 0][f] : 0;
        if (f >= 0) { d.P(16, 196 - 2 + up, bw + 2, 18, INK); d.P(17, 197 - 2 + up, bw, 16, '#3B82C4'); d.P(104, 211 + up, 4, 4, '#3B82C4'); d.tx(s, 23, 199 + up, {size: 30, color: CREAM}); }
      }
      // the notes: the plumber's, then the week piles on; Dentist lands right on top of it
      const A = [166, 152], B = [254, 152], C = [166, 220], D = [254, 220];
      const tDent = tOff + 0.4, buried = T >= tDent + 0.1;
      const ay = note(k, A[0], A[1], GOLD, ['Reply to', 'plumber'], t0 + 0.6, {hidden: buried, seed: 1});
      if (!buried && T >= tWrite && ay != null) {   // the pencil writes a few squiggles, stops halfway and hovers
        const p = clamp((T - tWrite) / 0.8), len = Math.round(30 * p), y = ay + 44;
        for (let x = 0; x < len; x++) d.DOT(A[0] + 6 + x, y + [0, -1, -2, -1, 0, 1, 1, 0][x % 8], '#3D2E45');
        const px0 = A[0] + 6 + len, py0 = y - 12 + (p >= 1 ? ((d.F >> 3) & 1) : 0);
        d.line(px0, py0 + 10, px0 + 9, py0, INK, 2); d.line(px0 + 1, py0 + 9, px0 + 8, py0 + 1, ORANGE); d.P(px0 + 8, py0 - 1, 3, 3, '#E2633B'); d.DOT(px0, py0 + 11, INK);
      }
      note(k, B[0], B[1], '#87CEEB', ['Soccer', '4pm'], tOff, {pin: TEAL, seed: 2});
      note(k, A[0] + 4, A[1] + 4, '#F2A541', ['Dentist'], tDent, {pin: '#3B82C4', seed: 0});
      note(k, C[0], C[1], TEAL, ['Pay bills'], tOff + 0.8, {pin: GOLD, seed: 2, top: '#BDE6F5'});
      note(k, D[0], D[1], CREAM, ['Groceries'], tOff + 1.2, {pin: RED, seed: 1, top: '#E6D3BC'});
      // HOMEWORK: a red tag stamped onto the freezer door right above the note, an arrow stepping down at it
      if (T >= tSheet) {
        const f = d.fr(tSheet), sq = f < 2 ? 1 : 0, tw0 = Math.ceil(d.tw('HOMEWORK')) + 12;
        d.P(A[0] - 1, 118 - 1 + sq, tw0 + 2, 19 - sq, INK); d.P(A[0], 118 + sq, tw0, 17 - sq, RED); d.P(A[0], 118 + sq, tw0, 1, ORANGE);
        k.slam('HOMEWORK', (A[0] + 6) * 3, 121 * 3, tSheet, {size: 39, color: CREAM, stamp: true, glint: false});
        if (!buried) { const ab = (d.F >> 3) & 1; d.P(A[0] + 36, 138 + ab, 6, 4, RED); d.P(A[0] + 37, 142 + ab, 4, 2, RED); d.P(A[0] + 38, 144 + ab, 2, 2, RED); }
      }
      // Jobber's tips: a game window slides in over the counter; a check lands on each tip as it is said
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
          d.tx(`Jobber Academy, ${k.data.numbers.jbYear.shown}`, X + 8, 240, {size: 30, color: SAND});
        }
      }
      return host(k, k.live('homework.off') ? 'shrug' : (k.live('homework.sheet') ? 'point' : null));
    },

    // ---- the text: the chat set in the truck. Each bubble's words show as they are said; then a gold frame holds it
    text: (k, T) => {
      const d = px(k), t0 = k.S('text');
      const tA = [wordT(k, 'text.name', /^Their/i), wordT(k, 'text.name', /^name/i), wordT(k, 'text.name', /^then/i), wordT(k, 'text.name', /^yours/i)];
      const tB = spoken(wordT(k, 'text.line', /^Still/i, 1.6), LINE_B);
      const msgs = [
        {me: true, text: QUOTE_MSG, at: -1, read: -1},
        {me: true, text: LINE_A, at: tA[0] - 0.15},
        {me: true, text: LINE_B, at: tB[0] - 0.15, read: wordT(k, 'text.hold', /^That/i)},
      ];
      k.sets.chat({who: 'Homeowner', msgs});
      const boxes = chatBoxes(k, msgs), bA = boxes.find((b) => b.m === msgs[1]), bB = boxes.find((b) => b.m === msgs[2]);
      if (bA) typeMask(k, bA, tA);
      if (bB) typeMask(k, bB, tB);
      const tHold = wordT(k, 'text.hold', /^That/i), tYes = wordT(k, 'text.yesno', /^yes/i), tNo = wordT(k, 'text.yesno', /^no/i);
      if (bB && T >= tHold) {   // the gold frame steps in around the text and holds
        const f = d.fr(tHold), g = f < 4 ? 3 - f : 0, x = bB.bx - 3 - g, y = bB.by - 3 - g, w = bB.w + 6 + 2 * g, h = bB.h + 6 + 2 * g;
        d.clip(CH.sx, CH.cy0, CH.sw, CH.cy1 - CH.cy0, () => { [[x, y, w, 2], [x, y + h - 2, w, 2], [x, y, 2, h], [x + w - 2, y, 2, h]].forEach(([a, b, ww, hh]) => d.P(a, b, ww, hh, Math.floor((T - tHold) * 2) % 2 ? GOLD : ORANGE)); });
        k.burst((bB.bx + bB.w / 2) * 3, (bB.by + bB.h / 2) * 3, tHold + 0.1, {n: 14, r: 180});
      }
      if (bB) [['YES', tYes, '#2F6F67'], ['NO', tNo, '#7A3442']].forEach(([s, at, c], i) => {   // the two answers it asks for
        if (T < at) return;
        const f = d.fr(at), w = Math.ceil(d.tw(s)) + 10, x = bB.bx - 6 - w, y = bB.by + 6 + i * 22 - (f < 3 ? [3, 1, 0][f] : 0);
        d.P(x - 1, y - 1, w + 2, 19, INK); d.P(x, y, w, 17, c); d.P(x, y, w, 1, CREAM); d.tx(s, x + 5, y + 2, {color: CREAM});
      });
      return host(k, k.live('text.hold') || k.live('text.yesno') ? 'point' : null);
    },

    // ---- the turn: the mail desk. Text it, don't email it; then the 59%
    turn: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('turn'), tText = k.S('turn.text'), tDont = wordT(k, 'turn.text', /^Don/i, 0.6);
      const tSt = k.S('turn.st'), tHcp = k.S('turn.hcp'), tPct = wordT(k, 'turn.pct', /^fifty/i), tFits = wordT(k, 'turn.fits', /^fits/i);
      desk(k, {t0, textAt: tText + 0.2, laptopOut: tHcp, checkAt: tFits});
      d.win(14, 86, 332, 26, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: null});
      k.slam('The part people skip.', 72, 273, t0 + 0.1, {size: 39, color: GOLD, from: 0.5});
      if (T >= tText) { k.slam('Text it.', 920, 336, tText, {size: 66, color: 'accent', align: 'right', from: 0.5, drop: INK}); k.burst(820, 370, tText + 0.1, {n: 14, r: 200}); }
      if (T >= tDont && T < tHcp) k.slam("Don't email it.", 60, 350, tDont, {size: 39, color: CREAM, from: 0.4, drop: INK});
      if (T >= tSt && T < tHcp) {
        k.slam('Texts beat email', 300, 810, tSt, {size: 39, color: CREAM, from: 0.4});
        k.slam('on open rates.', 300, 856, tSt + 0.15, {size: 39, color: CREAM, from: 0.4});
        k.sweep(300, 900, k.measure('on open rates.', {size: 39}), 6, tSt + 0.5, {color: 'accent'});
        k.text(`ServiceTitan follow-up webinar, ${n.stYear.shown}`, 300, 920, {size: 30, color: SAND});
      }
      if (T >= tHcp) {   // the laptop is gone; the survey's window slides in where it was
        const sl = d.ease(tHcp + 0.15, 10, -230);
        d.win(14 + sl, 130, 196, 128, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#7A3442'});
        if (sl === 0) {
          if (T >= tPct) { k.slam(cnt(k, n.textPct, tPct, {suffix: '%'}), 84, 408, tPct, {size: 132, color: 'accent', from: 0.6, drop: INK}); k.burst(250, 470, tPct + 0.7, {n: 18, r: 220}); }
          else k.text('Homeowners:', 84, 420, {size: 39, color: SAND});
          if (T >= tPct + 0.3) { k.slam('of homeowners', 84, 572, tPct + 0.3, {size: 39, color: CREAM, from: 0.4}); k.slam('expect text updates.', 84, 618, tPct + 0.5, {size: 39, color: CREAM, from: 0.4}); }
        }
        k.slam('Housecall Pro survey,', 300, 810, tHcp + 0.3, {size: 39, color: CREAM, from: 0.4});
        k.text(`${n.hcpSample.shown} U.S. homeowners, ${n.hcpYear.shown}`, 300, 860, {size: 30, color: SAND});
        if (T >= tFits) { k.slam('Your text fits right in.', 300, 908, tFits, {size: 39, color: GOLD, from: 0.4}); k.burst(820, 690, tFits + 0.05, {n: 16, r: 200, colors: ['teal', 'paper']}); }
      }
      return host(k, k.live('turn.text') || k.live('turn.pct') ? 'point' : null);
    },

    // ---- cadence: the street again. Three trips, one sign each; then close the file
    cadence: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('cadence');
      const tFirst = wordT(k, 'cadence.first', /^within/i), tWeek = wordT(k, 'cadence.week', /^week/i, 0.4), tFinal = wordT(k, 'cadence.final', /^day/i, 0.2);
      const tStill = k.S('cadence.still'), tClose = wordT(k, 'cadence.close', /^close/i, 0.6);
      const gap = (a, b) => Math.max(0.6, Math.min(1.1, b - a - SD - 0.1));
      route(k, {t0: -20, stopAt: -1.6, sign: false}, [
        {at: tFirst, drive: gap(tFirst, tWeek), sign: 'TEXT 1', speed: 4},
        {at: tWeek, drive: gap(tWeek, tFinal), sign: 'TEXT 2', speed: 4},
        {at: tFinal, drive: 1.1, sign: 'TEXT 3', speed: 4},
      ]);
      skyWin(d, 114);
      k.slam("Jobber's timing", 72, 274, t0 + 0.1, {size: 39, color: GOLD, from: 0.5});
      k.text(`Jobber Academy, ${n.jbYear.shown}`, 72, 318, {size: 30, color: SAND});
      // the timeline: a line, three dots that light as each is said, two lines under each
      const xs = [200, 510, 800], ts = [tFirst, tWeek, tFinal];
      const labels = [['Within', n.firstDays.shown], [n.secondDays.shown, 'a week after'], [`${n.finalMin.shown} to ${n.finalMax.shown}`, 'before expiry']];
      const lineP = eo((T - t0 - 0.2) / 0.6);
      d.P(50, 128, Math.round(260 * lineP), 2, '#6B7080');
      xs.forEach((x, i) => {
        const cx = Math.round(x / 3), on = T >= ts[i];
        if (lineP < 1 && cx > 50 + 260 * lineP) return;
        d.disc(cx, 129, 6, INK); d.disc(cx, 129, 5, on ? ORANGE : '#3D2E45'); if (on) d.DOT(cx - 2, 127, CREAM);
        if (on) { const f = d.fr(ts[i]); if (f >= 0 && f < 10) d.ring(cx, 129, 7 + (f >> 1), GOLD); k.slam(labels[i][0], x, 420, ts[i], {size: 39, color: CREAM, align: 'center', from: 0.4}); k.slam(labels[i][1], x, 466, ts[i] + 0.15, {size: 39, color: SAND, align: 'center', from: 0.4}); }
        else {
          k.text(String(i + 1), x, 420, {size: 39, color: '#6B7080', align: 'center'});
          if (ts.findIndex((t) => T < t) === i && lineP >= 1 && Math.floor(T * 2) % 2 === 0) d.ring(cx, 129, 8, GOLD);   // the next stop blinks, twice a second
        }
      });
      if (T >= tStill) {   // a question mark pops over the house and bobs
        const f = d.fr(tStill), up = f < 4 ? [6, 3, 1, 0][f] : ((d.F >> 3) & 1);
        k.text('?', 300, 618 - up * 3, {size: 66, color: GOLD, align: 'center', drop: INK});
      }
      if (T >= tClose) {
        k.slam(`After ${n.followUps.shown}, close the file.`, 72, 534, tClose, {size: 39, color: 'accent', from: 0.5});
        const f = d.fr(tClose + 0.3), fx = 262, fy = 172;
        d.P(fx - 1, fy - 1, 52, 22, INK); d.P(fx, fy, 50, 20, ORANGE); d.P(fx, fy - 4, 18, 5, ORANGE); d.P(fx, fy, 50, 2, GOLD);
        if (f >= 0) { const s = f < 3 ? 1 : 0; d.P(fx + 4 - s, fy + 5 - s, 42 + 2 * s, 11 + 2 * s, RED); k.slam('CLOSED', (fx + 25) * 3, (fy + 6) * 3, tClose + 0.3, {size: 30, color: CREAM, align: 'center', stamp: true, glint: false}); }
      }
      return host(k, k.live('cadence.close') ? 'point' : null);
    },

    // ---- close: the level-up screen. A perk on each "one"; LEVEL UP on "question"; the send line in one column
    close: (k, T) => {
      const d = px(k), t0 = k.S('close');
      const tName = wordT(k, 'close', /^name/i), tJob = wordT(k, 'close', /^job/i, 0.8), tQ = wordT(k, 'close', /^question/i, 1.6);
      const send = k.S('close.send'), quiet = k.S('close.quiet'), know = k.S('close.know');
      k.sets.levelup({from: 0, to: 100, max: 100, at: t0, dur: Math.max(0.6, tQ - t0), levelAt: tQ, level: 2, text: 'LEVEL UP!',
        stats: [{text: 'ONE NAME', at: tName}, {text: 'ONE JOB', at: tJob}, {text: 'ONE QUESTION', at: tQ}]});
      if (T < tQ) k.slam('The rule:', 540, 400, t0 + 0.1, {size: 66, color: CREAM, align: 'center', from: 0.5, drop: INK});
      if (T >= quiet) {
        const echo = T >= know;
        k.slam(echo ? 'Now you know what to send.' : 'Exact text in the caption.', 540, 506, echo ? know : quiet, {size: 39, color: echo ? GOLD : CREAM, align: 'center', from: 0.4, drop: INK});
      }
      if (T >= send) {
        k.chip('ProofNotFluff', 366, 276, {size: 30});
        k.slam('Send this to whoever', 366, 870, send, {size: 39, color: 'accent', from: 0.5, drop: INK});
        k.slam('follows up on your quotes.', 366, 916, send + 0.15, {size: 39, color: 'accent', from: 0.5, drop: INK});
      }
      return host(k, k.live('close.know') ? 'wave' : (k.live('close.send') ? 'point' : null));
    },
  },
};
