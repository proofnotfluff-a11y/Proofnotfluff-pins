// Scene: Close it before you leave the driveway (Lesson 5, Quote Clinic, arcade). One function per top-level cue in 03_cues/cues.md.
// Numbers only from k.data (brief.md -> data.js). Every beat lands on a spoken word (window.WORDS) found from its cue, so a
// re-voiced take moves the picture with it (the words were re-timed after the cues, so the search looks back 0.6 s).
// Worlds, one per section: hook = the street (the van in the driveway rolls off with the quote still open, then a replay
// where it stays and the quote gets signed); stakes = the XP bars (77 against 62, the 15-point gap blinking as missing XP);
// why = the dispatch board (follow-up trips and a competitor pile onto one open quote, then clear when you close on the
// visit); ask = a kitchen-table close drawn here (the estimate on its clipboard, a coffee, the next-visit card where the pen
// writes Thursday, the three lines typing on as said); skip = LEVEL UP (what same-visit closes show, as perks; the ask
// unlocked); caveat = a notebook page the pen writes the honest note on; close = the street again, the van stays.
const INK = '#120D14', CREAM = '#FFF7EA', PAPER = '#F4E6D3', SAND = '#E6D3BC', MUTED = '#B39A88', GOLD = '#F7C873', ORANGE = '#F2A541',
  RED = '#E2633B', MAROON = '#7A3442', TEAL = '#6FB7A8', GREY = '#9AA0AD', NAVY = '#253048', PLUM = '#2B2033', DUSK = '#1B1420';
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
    const base = o.base || '#253048', hi = o.hi || '#3B82C4', lo = o.lo || DUSK, rule = o.rule === undefined ? '#87CEEB' : o.rule;
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
// the time a word is said, at or after `from` (looking back 0.6 s, since the cues sit up to half a second after the words)
const W = (re, from, dflt) => { const w = WS().find((x) => x.start >= from - 1.1 && re.test(x.w)); return w ? w.start : (dflt != null ? dflt : from); };
// the start and end of each spoken word of a line, matched in order from t0 (a missing word takes the one before's time)
const spoken = (t0, said) => {
  const ws = WS(); let i = ws.findIndex((x) => x.start >= t0 - 1.1); if (i < 0) i = ws.length;
  let last = t0;
  return said.split(/\s+/).map((wd) => {
    const want = norm(wd); let j = i;
    while (j < ws.length && j < i + 6 && norm(ws[j].w) !== want) j++;
    if (j < ws.length && j < i + 6) { i = j + 1; last = ws[j].start; return [ws[j].start, ws[j].end]; }
    return [last, last + 0.2];
  });
};
// how many characters of a line are written by now: each word writes on over the time it is said
const written = (T, text, times) => {
  const words = text.split(' '); let n = 0;
  for (let i = 0; i < words.length; i++) {
    const [a, b] = times[i] || [1e9, 1e9]; if (T < a) break;
    const q = clamp((T - a) / Math.max(0.12, b - a)), m = q >= 1 ? words[i].length : Math.floor(words[i].length * q);
    n += m + (i ? 1 : 0); if (q < 1) break;
  }
  return Math.min(text.length, n);
};
// a count that starts at 85% of its value and lands exactly on it
const cnt = (k, num, t0, o = {}) => k.count(num.value, k.lin(t0, t0 + 0.7) >= 1 ? 1 : 0.85 + 0.15 * k.lin(t0, t0 + 0.7), Object.assign({from: 0}, o));
const host = (k, pose) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150});
// the levelup set's own "LV n" and "XP" labels are left out: this lesson labels its bars itself
const bubble2 = (k, d, x, y, kind, pop = 0) => { const c = k.ctx; c.save(); c.translate(Math.round(x) * 3, Math.round(y) * 3); c.scale(2, 2); bubble(d, 0, 0, kind, pop); c.restore(); };
const quiet = (k, fn) => { const t = k.text; k.text = function (s, ...a) { return /^(LV \d+|XP)$/.test(String(s)) ? {w: 0, h: 0, lines: []} : t.call(this, s, ...a); }; try { return fn(); } finally { k.text = t; } };

// ================================================================================================================
// the street pieces: the work van at 2x on the grid (the library sprite), its exhaust, the house door, a thought bubble
// the van and the icons are the library's shared sprites, not set pieces: they are drawn from the built set object itself,
// so the variety count (anim.py lint, worlds.json) records only this lesson's worlds
const sprites = (k) => { const s = k.sets; return k.__sets || s; };
const van2 = (k, x, y, wheel) => { const c = k.ctx; c.save(); c.translate(Math.round(x) * 3, Math.round(y) * 3); c.scale(2, 2); sprites(k).van(0, 0, {wheel}); c.restore(); };
const exhaust = (d, vx, vy, fast) => { for (let i = 0; i < 3; i++) { const a = (d.F * (fast ? 1 : 0.5) + i * 6) % 18 | 0; d.P(vx - 4 - a, vy + 50 - Math.floor(a / 4), 3 + (a > 9 ? 1 : 0), 3, a > 9 ? GREY : '#C9CCD3'); } };
// the street set with the world at rest places its houses at x = i * 100; this is house i's door (the set's own layout)
const doorOf = (i) => { const w = 70 + Math.floor(hash(i * 1.9) * 12); return [i * 100 + Math.floor(w / 2) - 6, 267]; };
const QMARK = ['.###.', '#...#', '...#.', '..#..', '.....', '..#..'];
const CHECK = ['......#', '.....##', '#...##.', '##.##..', '.###...', '..#....'];
const CROSS = ['#...#', '.#.#.', '..#..', '.#.#.', '#...#'];
const bubble = (d, x, y, kind, pop = 0) => {   // 20 x 14 with a tail at the bottom left; kind: '?', 'dots', 'check', 'x'
  const yy = y - pop;
  d.P(x - 1, yy - 1, 22, 15, INK); d.P(x, yy, 20, 13, CREAM); d.P(x, yy + 12, 20, 1, SAND);
  d.P(x + 3, yy + 13, 5, 3, INK); d.P(x + 4, yy + 13, 3, 2, CREAM); d.DOT(x + 3, yy + 16, INK);
  if (kind === '?') d.spr(QMARK, {'#': RED}, x + 7, yy + 3);
  else if (kind === 'check') d.spr(CHECK, {'#': '#3E7A62'}, x + 6, yy + 3);
  else if (kind === 'x') d.spr(CROSS, {'#': RED}, x + 7, yy + 4);
  else { const n = 1 + (d.F >> 3) % 3; for (let j = 0; j < n; j++) d.P(x + 4 + j * 5, yy + 6, 2, 2, NAVY); }
};
// a stepped rectangle ring that grows out from a box for 12 frames (a ping)
const ping = (d, t0, x, y, w, h, c = CREAM) => { const f = d.fr(t0); if (f < 0 || f >= 12) return; const g = 1 + f; d.P(x - g, y - g, w + 2 * g, 1, c); d.P(x - g, y + h + g, w + 2 * g, 1, c); d.P(x - g, y - g, 1, h + 2 * g, c); d.P(x + w + g, y - g, 1, h + 2 * g + 1, c); };

// ================================================================================================================
// the kitchen table (ask): our own set piece, seen from above like a JRPG table. A papered wall with a window (a cloud
// drifts past) and a clock whose second hand steps; the table in planks; the estimate on a clipboard (three options, a
// signature line); a coffee that steams; the next-visit card where the pen writes the day; a pen that travels between them.
const kitchen = (k, o) => {
  const d = px(k), {P, DOT, disc, ring, line, dith, clip, T, F} = d;
  // the wall
  P(0, 0, 360, 98, SAND); for (let x = 4; x < 360; x += 14) { P(x, 0, 3, 98, PAPER); DOT(x + 8, 20 + (x % 28), '#D9A066'); }
  // the window: frame, sky, a cloud a pixel every 10 frames, the cross bars, gingham curtains, the sill
  P(232, 18, 108, 72, INK); P(234, 20, 104, 68, '#87CEEB'); P(234, 20, 104, 24, '#BDE6F5');
  clip(234, 20, 104, 68, () => { const cx = 234 + ((F / 10 | 0) % 150) - 30; disc(cx, 40, 6, CREAM); disc(cx + 8, 37, 8, CREAM); disc(cx + 17, 41, 5, CREAM); P(cx - 5, 42, 28, 4, CREAM); P(234, 70, 104, 18, '#3E7A62'); for (let x = 236; x < 338; x += 9) disc(x, 70, 4, '#2F5A4A'); });
  P(284, 20, 3, 68, SAND); P(234, 52, 104, 3, SAND);
  [[226, 0], [318, 1]].forEach(([x, s]) => { for (let y = 14; y < 92; y += 4) for (let i = 0; i < 26; i += 4) P(x + i, y, 4, 4, ((y / 4 + i / 4 + s) & 1) ? RED : CREAM); P(x, 14, 26, 2, MAROON); });
  P(226, 10, 118, 4, '#8C5A33'); P(228, 88, 114, 5, '#D9A066'); P(228, 92, 114, 2, '#8C5A33');
  // the clock: the second hand steps once a second (time keeps moving while the quote sits open)
  const ccx = 48, ccy = 52; disc(ccx, ccy, 19, INK); disc(ccx, ccy, 17, CREAM); ring(ccx, ccy, 17, MAROON, 2);
  for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6; DOT(ccx + Math.round(Math.cos(a) * 13), ccy + Math.round(Math.sin(a) * 13), i % 3 ? GREY : INK); }
  const sa = (Math.floor(T) % 60) * Math.PI / 30 - Math.PI / 2; line(ccx, ccy, ccx + Math.round(Math.cos(sa) * 12), ccy + Math.round(Math.sin(sa) * 12), RED);
  line(ccx, ccy, ccx + 6, ccy - 5, INK, 2); line(ccx, ccy, ccx, ccy - 10, INK); disc(ccx, ccy, 1, INK);
  // the table: planks, a lit front edge, the floor under it
  P(0, 98, 360, 4, '#4A2E1B');
  for (let y = 102, i = 0; y < 336; y += 14, i++) { P(0, y, 360, 14, i % 2 ? '#B07A47' : '#A9733F'); P(0, y, 360, 1, '#D9A066'); P(0, y + 13, 360, 1, '#8C5A33'); for (let x = (i * 53) % 90; x < 360; x += 90) P(x, y + 1, 1, 12, '#8C5A33'); DOT((i * 71) % 360, y + 6, '#8C5A33'); }
  P(0, 336, 360, 6, '#8C5A33'); P(0, 336, 360, 1, '#D9A066'); P(0, 342, 360, 4, '#4A2E1B');
  for (let y = 346, r = 0; y < 640; y += 16, r++) for (let x = 0, c = 0; x < 360; x += 16, c++) P(x, y, 16, 16, (r + c) % 2 ? '#5A3A22' : '#4A2E1B');
  // the clipboard: board, metal clip, the estimate
  const cbx = 18, cby = 106;
  P(cbx + 2, cby + 2, 134, 92, INK); P(cbx - 1, cby - 1, 134, 92, INK); P(cbx, cby, 132, 90, '#6B4226'); P(cbx, cby, 132, 1, '#8C5A33');
  P(cbx + 6, cby + 7, 120, 80, PAPER); P(cbx + 6, cby + 86, 120, 1, MUTED);
  P(cbx + 50, cby - 4, 32, 9, INK); P(cbx + 51, cby - 3, 30, 7, GREY); P(cbx + 51, cby - 3, 30, 1, '#C9CCD3'); P(cbx + 60, cby - 1, 12, 3, '#4A4E5A');
  d.tx('ESTIMATE', cbx + 12, cby + 10, {color: NAVY});
  const opts = o.options || -1;
  ['A', 'B', 'C'].forEach((L, i) => {
    const y = cby + 30 + i * 15, on = o.optAt != null && T >= o.optAt + i * 0.15;
    P(cbx + 12, y, 9, 9, INK); P(cbx + 13, y + 1, 7, 7, PAPER);
    if (!on) { P(cbx + 26, y + 4, 90, 1, '#C9CCD3'); return; }
    const pop = d.fr(o.optAt + i * 0.15) < 3 ? 1 : 0;
    d.tx(L, cbx + 25, y - pop - 1, {size: 30, color: NAVY});
    P(cbx + 36, y + 2 - pop, 48 - i * 6, 2, MUTED); P(cbx + 36, y + 6 - pop, 30 + i * 5, 1, '#C9CCD3');
    P(cbx + 96, y + 1 - pop, 22, 6, i === 1 ? '#F7C873' : SAND); P(cbx + 98, y + 3 - pop, 14, 2, MUTED);   // the line total, a bar (no figure)
  });
  if (o.checkAt != null && T >= o.checkAt) {   // option B gets ticked
    const n = Math.min(CHECK.length * 7, d.fr(o.checkAt) * 6), y = cby + 45;
    let m = 0; CHECK.forEach((r, j) => { for (let i = 0; i < r.length; i++) if (r[i] === '#' && m++ < n) P(cbx + 12 + i, y - 1 + j, 1, 1, RED); });
  }
  // the signature line, and the scribble that signs it
  d.tx('X', cbx + 12, cby + 72, {size: 30, color: NAVY});
  P(cbx + 22, cby + 81, 96, 1, NAVY);
  const sig = []; for (let i = 0; i <= 80; i++) sig.push([cbx + 26 + i, cby + 77 + Math.round(3 * Math.sin(i * 0.42) - (i % 17 < 3 ? 2 : 0))]);
  if (o.signAt != null && T >= o.signAt) { const n = Math.min(sig.length, Math.floor((T - o.signAt) / 0.5 * sig.length)); for (let i = 1; i < n; i++) line(sig[i - 1][0], sig[i - 1][1], sig[i][0], sig[i][1], NAVY); }
  // the coffee, from above: a red mug, a handle, coffee with a light spot; steam rises in steps
  const mx = 168, my = 132;
  disc(mx + 1, my + 2, 12, '#8C5A33'); ring(mx + 13, my, 5, INK, 2); disc(mx, my, 12, INK); disc(mx, my, 11, RED); disc(mx, my, 8, MAROON); disc(mx, my, 7, '#4A2E1B'); DOT(mx - 3, my - 3, '#7A4E2C'); DOT(mx - 2, my - 3, '#7A4E2C');
  for (let i = 0; i < 3; i++) { const a = ((F >> 2) + i * 4) % 12; DOT(mx - 4 + i * 4 + ((a >> 1) & 1), my - 14 - a, PAPER); DOT(mx - 4 + i * 4 + ((a >> 1) & 1), my - 15 - a, CREAM); }
  // the next-visit card
  const ncx = 190, ncy = 112;
  P(ncx + 2, ncy + 2, 138, 66, '#6B4226'); P(ncx - 1, ncy - 1, 138, 66, INK); P(ncx, ncy, 136, 64, CREAM); P(ncx, ncy, 136, 18, MAROON); P(ncx, ncy + 17, 136, 1, INK);
  d.tx('NEXT VISIT', ncx + 8, ncy + 4, {size: 30, color: CREAM});
  P(ncx + 8, ncy + 46, 118, 1, '#87CEEB');
  const day = o.day || {}, dayText = day.text || 'Thursday';
  let head = null;
  if (day.at != null && T >= day.at) {
    const nch = Math.min(dayText.length, Math.floor((T - day.at) / 0.045) + 1), s = dayText.slice(0, nch);
    d.tx(s, ncx + 10, ncy + 28, {color: NAVY, lint: nch === dayText.length});
    head = [ncx + 10 + d.tw(s), ncy + 40];
    if (day.circleAt != null && T >= day.circleAt) {   // a red loop drawn round the day
      const w = d.tw(dayText) + 12, cx = ncx + 10 + w / 2 - 6, cy = ncy + 34, n = Math.min(48, d.fr(day.circleAt) * 4);
      for (let i = 0; i < n; i++) { const a = -Math.PI * 0.6 + i * Math.PI * 2.1 / 48; P(cx + Math.round(Math.cos(a) * w / 2), cy + Math.round(Math.sin(a) * 10), 2, 1, RED); }
    }
  }
  if (day.tag != null && T >= day.tag) d.tx('example day', ncx + 10, ncy + 50, {size: 30, color: MUTED});
  // the pen: rests on the table, travels to wherever it writes (tip at p, the body up and to the right)
  let p = [158, 186];
  if (head && T < day.at + dayText.length * 0.045 + 0.2) p = head;
  else if (o.checkAt != null && T >= o.checkAt - 0.25 && T < o.checkAt + 0.3) p = [cbx + 18, cby + 49];
  else if (o.signAt != null && T >= o.signAt && T < o.signAt + 0.6) { const n = Math.min(sig.length - 1, Math.floor((T - o.signAt) / 0.5 * sig.length)); p = sig[n]; }
  else if (o.signAt != null && T >= o.signAt + 0.6) p = [cbx + 112, cby + 70];
  else if (day.at != null && T >= day.at) p = [ncx + 14 + d.tw(dayText), ncy + 44];
  const [qx, qy] = p.map(Math.round);
  line(qx + 3, qy + 1, qx + 25, qy - 21, '#1B1420', 3);
  line(qx + 1, qy - 1, qx + 22, qy - 22, '#3B82C4', 3); line(qx + 2, qy - 3, qx + 21, qy - 22, '#87CEEB');
  P(qx, qy - 1, 2, 2, GOLD); DOT(qx, qy, INK); line(qx + 15, qy - 15, qx + 19, qy - 19, GREY, 2);
};

// ================================================================================================================
// the notebook page (caveat): a spiral pad on a dark desk, blue rules, a red margin, a coffee ring; the pen writes
const notebook = (k) => {
  const d = px(k), {P, DOT, ring} = d;
  P(0, 0, 360, 640, '#4A2E1B'); for (let y = 0, i = 0; y < 640; y += 12, i++) { P(0, y, 360, 1, '#5A3A22'); for (let x = (i * 47) % 80; x < 360; x += 80) P(x, y + 1, 1, 11, '#3D2E45'); }
  P(22, 96, 326, 240, INK); P(17, 89, 328, 244, INK); P(18, 90, 326, 242, PAPER); P(18, 90, 326, 1, CREAM);
  for (let y = 126; y < 330; y += 18) P(19, y, 324, 1, '#87CEEB');
  P(52, 91, 1, 240, RED); P(54, 91, 1, 240, '#F09A9A');
  for (let x = 30; x < 340; x += 14) { P(x, 82, 5, 14, INK); P(x + 1, 83, 3, 12, GREY); P(x + 1, 83, 1, 12, '#C9CCD3'); DOT(x + 2, 96, '#4A4E5A'); }
  ring(304, 300, 16, '#D9A066'); ring(304, 300, 15, '#E6D3BC'); P(296, 284, 10, 3, PAPER);   // a coffee ring, open at the top
  P(18, 332, 326, 4, DUSK);
};
// a line the pen writes as it is said: letters appear behind the tip; returns the tip while it writes
const pen = (d, x, y) => { const qx = Math.round(x), qy = Math.round(y); d.line(qx + 3, qy + 1, qx + 25, qy - 21, '#1B1420', 3); d.line(qx + 1, qy - 1, qx + 22, qy - 22, '#3B82C4', 3); d.line(qx + 2, qy - 3, qx + 21, qy - 22, '#87CEEB'); d.P(qx, qy - 1, 2, 2, GOLD); d.DOT(qx, qy, INK); d.line(qx + 15, qy - 15, qx + 19, qy - 19, GREY, 2); };

// ================================================================================================================
// transitions of this lesson's own, on the pixel grid like the library's (12 frames): a road that paves over the frame
// with a van at its front (into the close), a notebook page that comes down (into the caveat), an XP bar that fills the
// screen row by row (into the level up)
if (window.SETS && window.SETS.transitions) {
  const T2 = window.SETS.transitions;
  T2.drive = (ctx, q, e) => {
    const s = 96, rows = Math.ceil(e.H / s);
    for (let r = 0; r < rows; r++) {
      const g = clamp(q * 1.35 - Math.abs(r - 10) * 0.018), w = Math.round(e.W * g / 6) * 6; if (w <= 0) continue;
      const x0 = e.closing || e.u < 1 ? 0 : e.W - w;
      e.fill('#4A4E5A', x0, r * s, w, s); e.fill('#6B7080', x0, r * s, w, 3);
      for (let x = x0 + 12; x < x0 + w - 42; x += 84) e.fill('#F7C873', x, r * s + 45, 42, 6);
      if (r === 10 && (e.closing || e.u < 1)) { const vx = x0 + w - 30; e.fill('#120D14', vx - 6, r * s + 18, 132, 66); e.fill('#FFF7EA', vx, r * s + 24, 120, 48); e.fill('#F2A541', vx, r * s + 48, 120, 9); e.fill('#5B8FB9', vx + 90, r * s + 30, 24, 15); }
    }
  };
  T2.page = (ctx, q, e) => {
    const h = Math.round(e.H * q / 6) * 6; if (h <= 0) return;
    e.fill('#F4E6D3', 0, 0, e.W, h);
    for (let y = 108; y < h - 6; y += 54) e.fill('#87CEEB', 0, y, e.W, 3);
    e.fill('#E2633B', 156, 0, 3, h);
    for (let x = 0; x < e.W; x += 24) { const t = (x / 24) % 2 ? 6 : 12; e.fill('#B39A88', x, h, 24, t); }
  };
  T2.xp = (ctx, q, e) => {
    const s = 96, cols = 10, cw = e.W / cols;
    for (let r = 0; r * s < e.H; r++) { const n = Math.floor(clamp(q * 1.5 - (r % 4) * 0.08) * cols + 0.0001); for (let c = 0; c < n; c++) { e.fill('#1B1420', c * cw, r * s, cw, s); e.fill('#2F6F67', c * cw + 6, r * s + 6, cw - 12, s - 12); e.fill('#6FB7A8', c * cw + 6, r * s + 6, cw - 12, 21); } }
  };
}

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 5',
  transitions: {stakes: 'levelselect', why: 'dissolve', ask: 'iris', skip: 'xp', caveat: 'page', close: 'drive'},
  trauma: {'hook.same': 0.6},
  sections: {
    // ---- hook: the street. Frame 0 is the cover: the claim on a plate in the sky, the van parked, no host, no dialog.
    // On "leave" the van rolls off and the customer is left with a question; on "Top shops" it backs in again (REPLAY),
    // the customer thinks it over with the tech still there, and on "same visit" the bubble turns to a check.
    hook: (k, T) => {
      const n = k.data.numbers, d = px(k), {P} = d;
      const tLeave = W(/^leave$/i, 0.6, 1.38), tTop = W(/^Top$/i, k.S('hook.top')), t77 = W(/^seventy/i, tTop), tSame = W(/^same$/i, k.S('hook.same')), tAsk = W(/^Here's$/i, k.S('hook.ask'));
      k.sets.street({t0: 1e6, van: false});
      // the van: parked; rolls off with the quote open; backs in on the replay
      let vx = 194, moving = false;
      if (T >= tLeave && T < tTop) { const t = T - tLeave; vx = 194 + Math.floor(70 * t * t + 8 * t); moving = true; }
      else if (T >= tTop) { vx = 194 + d.ease(tTop, 20, 176); moving = d.fr(tTop) < 20; }
      if (vx < 366) {
        const vy = 284 + (moving ? (d.F >> 2) & 1 : 0);
        van2(k, vx, vy, moving ? (d.F >> 1) & 1 : 0);
        if (T >= tLeave - 0.5 && T < tTop) exhaust(d, vx, vy, moving); else if (T >= tTop) exhaust(d, vx, vy, false);
      }
      // the replay tag on the road, while the van backs in
      if (T >= tTop && T < tTop + 1.6) {
        const on = Math.floor((T - tTop) * 2) % 2 === 0;
        for (let j = 0; j < 2; j++) for (let r = 0; r < 9; r++) { const h = 4 - Math.abs(r - 4); P(22 + j * 7 + (4 - h), 314 + r, h + 1, 1, on ? CREAM : GREY); }
        d.tx('REPLAY', 42, 312, {color: on ? CREAM : GREY});
      }
      // the customer at the door: left with a question; thinking it over on the replay; then a yes on the visit
      const [dx, dy] = doorOf(1), bx = dx - 12, by = dy - 36, bob = (d.F >> 4) & 1;
      if (T >= tLeave + 0.5 && T < tTop) bubble2(k, d, bx, by, '?', bob);
      else if (T >= tTop + 0.7 && T < tSame) bubble2(k, d, bx, by, 'dots');
      else if (T >= tSame) { bubble2(k, d, bx, by, 'check', d.fr(tSame) < 3 ? 1 : 0); d.twinkle(bx + 46, by - 2, d.fr(tSame) >> 1); }
      k.burst((bx + 20) * 3, (by + 12) * 3, tSame + 0.05, {n: 18, r: 200});
      if (T >= tLeave + 0.5 && T < tLeave + 0.9) ping(d, tLeave + 0.5, bx - 1, by - 1, 42, 28, GOLD);
      // the cover plate: the claim and its source, settled on frame 0
      d.win(14, 86, 332, 114, {base: DUSK, hi: '#3D2E45', lo: INK, rule: MAROON});
      k.slam('Top shops close', 540, 274, -1, {size: 66, color: CREAM, align: 'center', drop: INK});
      const w77 = k.measure(n.topClose.shown, {size: 132}), wR = Math.max(k.measure('of estimates', {size: 39}), k.measure('on the same visit.', {size: 39}));
      const x0 = Math.round((540 - (w77 + 36 + wR) / 2) / 3) * 3, xr = x0 + Math.round((w77 + 36) / 3) * 3;
      k.slam(n.topClose.shown, x0, 352, -1, {size: 132, color: 'accent', drop: INK});
      k.text('of estimates', xr, 372, {size: 39, color: CREAM});
      k.text('on the same visit.', xr, 420, {size: 39, color: T >= tSame ? GOLD : CREAM});
      if (T >= tSame) k.sweep(xr, 466, k.measure('on the same visit.', {size: 39}), 6, tSame + 0.1, {color: 'accent'});
      k.text(`ServiceTitan customers, ${n.stMonths.shown} months to Jan ${n.stYear.shown}`, 528, 522, {size: 30, color: SAND, align: 'center'});
      ping(d, t77, x0 / 3 - 3, 116, w77 / 3 + 6, 46);
      k.burst(x0 + w77 / 2, 420, 0.4, {n: 16, r: 240, colors: ['accent', 'paper']});   // life right after the cover
      k.burst(x0 + w77 / 2, 420, t77 + 0.3, {n: 22, r: 260});
      if (T < tLeave) return {host: false, speech: false};
      if (T < tAsk) return {host: false};
      return host(k, k.live('hook.ask') ? 'point' : null);
    },

    // ---- stakes: XP bars. ServiceTitan's top 10% fill to 77; everyone else to 62; the 3 segments between blink as the gap
    stakes: (k, T) => {
      const n = k.data.numbers, d = px(k), {P} = d, t0 = k.S('stakes');
      const tWin = W(/^up$/i, k.S('stakes.window')), tTopW = W(/^top$/i, k.S('stakes.top')), t77 = W(/^seventy/i, k.S('stakes.top77')), tElse = W(/^Everyone$/i, k.S('stakes.rest')), t62 = W(/^Sixty/i, tElse), tGap = t62 + 0.9;
      quiet(k, () => k.sets.levelup({from: 0, to: n.topClose.value, max: 100, at: t77, dur: 0.8}));
      // the status frame round both bars (an outline, so the set's own bar shows through), its tab and gold corners
      P(14, 164, 332, 2, INK); P(14, 300, 332, 2, INK); P(14, 164, 2, 138, INK); P(344, 164, 2, 138, INK);
      P(16, 166, 328, 1, MAROON); P(16, 299, 328, 1, MAROON); P(16, 166, 1, 134, MAROON); P(343, 166, 1, 134, MAROON);
      [[14, 164], [342, 164], [14, 298], [342, 298]].forEach(([x, y]) => { P(x, y, 4, 4, ORANGE); d.DOT(x + 1, y + 1, GOLD); });
      P(22, 157, 4 + d.tw('Same-visit close rate', 30), 12, INK); P(23, 158, 2 + d.tw('Same-visit close rate', 30), 10, MAROON);
      d.tx('Same-visit close rate', 24, 158, {size: 30, color: CREAM});
      // the header plate: who, what, and the window (types on as it is said)
      d.win(14, 84, 332, 70, {base: DUSK, hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
      sprites(k).icon('star', 304, 96, 3); if (T >= t0 + 1) d.twinkle(330, 98, (d.F >> 2) % 8 < 4 ? (d.F >> 2) % 4 : 0, GOLD);
      k.slam('ServiceTitan', 72, 270, t0 + 0.05, {size: 66, color: 'accent', from: 0.5, drop: INK});
      k.slam('Estimates closed on the same visit', 72, 354, t0 + 0.25, {size: 39, color: CREAM, from: 0.4});
      const win = `Its customers, ${n.stMonths.shown} months to Jan ${n.stYear.shown}`;
      if (T >= tWin) { const s = win.slice(0, Math.max(1, d.fr(tWin) + 1)); k.text(s, 72, 408, {size: 30, color: SAND, lint: s.length === win.length}); }
      else k.text('A year of its customers\' data', 72, 408, {size: 30, color: MUTED});
      // bar 1 is the set's own (x 30..310, y 208); its label and value
      if (T >= tTopW) k.slam(`Top ${n.topPct.shown} by revenue`, 90, 576, tTopW, {size: 39, color: GOLD, from: 0.4});
      else k.text('Top shops', 90, 576, {size: 39, color: MUTED});
      if (T >= t77) k.slam(cnt(k, n.topClose, t77, {suffix: '%'}), 930, 546, t77, {size: 66, color: TEAL, align: 'right', from: 0.5, drop: INK});
      if (T >= t77 && T < t77 + 1.4) { const f = d.fr(t77 + 0.8); if (f >= 0) ping(d, t77 + 0.8, 30, 208, Math.round(280 * 0.77), 14, TEAL); }
      k.burst(90 + 840 * 0.77, 645, t77 + 0.8, {n: 16, r: 200, colors: ['teal', 'paper']});
      if (T >= t77 + 0.8) {   // a crown lands on the top shops' bar end
        const cx = Math.round(30 + 280 * n.topClose.value / 100) - 6, f = d.fr(t77 + 0.8), cy = 196 - (f < 6 ? [6, 4, 2, 0, -1, 0][f] : 0);
        d.spr(['#..#..#', '##.#.##', '#######', '#######', '.......', '#######'], {'#': GOLD}, cx, cy); P(cx + 3, cy + 2, 1, 1, RED); P(cx, cy + 5, 7, 1, ORANGE);
      }
      // bar 2, drawn like the set's: 20 segments, the next one blinks while it fills
      const X = 30, Y = 248, BW = 280, seg = 20, sw = BW / seg;
      P(X - 2, Y - 2, BW + 4, 18, INK); P(X - 1, Y - 1, BW + 2, 16, '#6B7080'); P(X, Y, BW, 14, DUSK);
      const v = T >= t62 ? n.restClose.value * eo((T - t62) / 0.8) : 0, nn = Math.floor(seg * clamp(v / 100) + 0.0001);
      for (let i = 0; i < nn; i++) { const x = Math.round(X + i * sw); P(x + 1, Y + 1, Math.round(sw) - 2, 12, ORANGE); P(x + 1, Y + 1, Math.round(sw) - 2, 3, GOLD); P(x + 1, Y + 10, Math.round(sw) - 2, 3, '#B07A47'); }
      if (T >= t62 && T < t62 + 0.8 && nn < seg && (d.F >> 1) & 1) P(Math.round(X + nn * sw) + 1, Y + 1, Math.round(sw) - 2, 12, '#3D2E45');
      k.text('Everyone else', 90, 696, {size: 39, color: T >= tElse ? CREAM : MUTED});
      if (T >= t62) k.slam(cnt(k, n.restClose, t62, {suffix: '%'}), 930, 666, t62, {size: 66, color: ORANGE, align: 'right', from: 0.5, drop: INK});
      // the gap: the segments everyone else is missing against the top shops blink gold (twice a second), a bracket under
      if (T >= tGap) {
        const a = Math.floor(seg * n.restClose.value / 100 + 0.0001), b = Math.floor(seg * n.topClose.value / 100 + 0.0001), on = Math.floor((T - tGap) * 2) % 2 === 0;
        for (let i = a; i < b; i++) { const x = Math.round(X + i * sw); P(x + 1, Y + 1, Math.round(sw) - 2, 1, on ? GOLD : '#B07A47'); P(x + 1, Y + 12, Math.round(sw) - 2, 1, on ? GOLD : '#B07A47'); P(x + 1, Y + 1, 1, 12, on ? GOLD : '#B07A47'); P(x + Math.round(sw) - 2, Y + 1, 1, 12, on ? GOLD : '#B07A47'); }
        const x0 = Math.round(X + a * sw), x1 = Math.round(X + b * sw), q = clamp(d.fr(tGap) / 6);
        P(x0, 266, 1, 4, GOLD); P(x1 - 1, 266, 1, 4, GOLD); P(x0, 269, Math.round((x1 - x0) * q), 1, GOLD);
        if (q >= 1) k.slam(`${n.gap.shown}-point gap`, (x0 + x1) * 1.5, 822, tGap + 0.2, {size: 39, color: GOLD, align: 'center', from: 0.4});
      }
      return host(k, k.live('stakes.top77') || k.live('stakes.rest') ? 'point' : (k.live('stakes.window') ? 'clip' : null));
    },

    // ---- why: the dispatch board. One visit to one house; while the quote sits open the follow-up trips pile on and a
    // competitor's van heads for the same door; close on the visit and the extra trips clear
    why: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('why');
      const t15 = W(/^fifteen$/i, t0), tMom = W(/^momentum/i, k.S('why.momentum')), tWait = W(/^wait/i, k.S('why.wait')), tHave = W(/^have$/i, tWait);
      const tComp = W(/^competitor/i, k.S('why.competitor')), tTalk = W(/^talk$/i, k.S('why.talk')), tClose = W(/^Close$/i, k.S('why.fewer')), tFewer = W(/^fewer$/i, tClose);
      const clr = tClose + 0.3, open = T < clr;
      const SHOP = [0.09, 0.62], HOUSE = [0.64, 0.82], RIVAL = [0.79, 0.46];
      const pins = [{x: SHOP[0], y: SHOP[1], at: t0 + 0.05, c: TEAL}, {x: HOUSE[0], y: HOUSE[1], at: t0 + 0.35, c: RED}];
      const routes = [{pts: [SHOP, [0.31, 0.62], [0.31, 0.82], HOUSE], at: t0 + 0.6, dur: 1.0, c: TEAL}];
      if (open) {
        routes.push({pts: [[0.09, 0.67], [0.45, 0.67], [0.45, 0.87], [0.64, 0.87]], at: tWait, dur: 0.9});
        routes.push({pts: [[0.13, 0.62], [0.13, 0.5], [0.58, 0.5], [0.58, 0.77], [0.64, 0.77]], at: tHave, dur: 0.9});
        routes.push({pts: [RIVAL, [0.79, 0.73], [0.67, 0.73], [0.67, 0.8]], at: tComp + 0.15, dur: 0.7, c: '#3B82C4'});
        pins.push({x: RIVAL[0], y: RIVAL[1], at: tComp, c: '#3B82C4'});
      }
      const m = k.sets.dispatch({pins, routes});
      const at = (p) => m.at(p[0], p[1]).map((v) => Math.round(v / 3));
      // the extra trips clear with a puff where they were
      [[0.45, 0.77], [0.36, 0.5], RIVAL].forEach((p, i) => { const [x, y] = m.at(p[0], p[1]); k.burst(x, y, clr + i * 0.05, {n: 12, r: 140, colors: ['paper', 'accent2']}); });
      // over the house: an hourglass that flips once a second while they wait; a question, then a no; then a yes
      const [hx, hy] = at(HOUSE);
      if (T >= tWait && open) {
        const flip = Math.floor(T - tWait) % 2, sand = Math.min(4, Math.floor(((T - tWait) % 1) * 5)), gx = hx - 30, gy = hy - 34;
        d.P(gx - 1, gy - 1, 11, 16, INK); d.P(gx, gy, 9, 2, '#8C5A33'); d.P(gx, gy + 12, 9, 2, '#8C5A33');
        d.P(gx + 1, gy + 2, 7, 10, '#BDE6F5'); d.P(gx + 3, gy + 6, 3, 2, '#BDE6F5');
        const top = flip ? sand : 4 - sand; d.P(gx + 2, gy + 2 + (4 - top), 5, top, GOLD); d.P(gx + 2, gy + 12 - (4 - top), 5, 4 - top, GOLD); d.DOT(gx + 4, gy + 7, GOLD);
      }
      if (open && T >= tWait) bubble(d, hx + 6, hy - 38, T >= tTalk ? 'x' : '?', (d.F >> 4) & 1);
      if (!open) { bubble(d, hx + 6, hy - 38, 'check', d.fr(clr) < 3 ? 2 : 0); d.twinkle(hx + 28, hy - 40, d.fr(clr) >> 1); }
      // the plate across the top of the map
      d.win(24, 88, 312, 40, {base: DUSK, hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
      if (T < tMom) {
        const a = 'Why a ', b = n.gap.shown, c = ' point gap?', wa = k.measure(a, {size: 66}), wb = k.measure(b, {size: 66}), wc = k.measure(c, {size: 66}), x = Math.round((540 - (wa + wb + wc) / 2) / 3) * 3;
        k.slam(a, x, 282, t0 + 0.05, {size: 66, color: CREAM, from: 0.4, drop: INK});
        k.slam(b, x + wa, 282, Math.max(t0 + 0.05, t15), {size: 66, color: 'accent', from: 0.8, drop: INK});
        k.slam(c, x + wa + wb, 282, t0 + 0.05, {size: 66, color: CREAM, from: 0.4, drop: INK});
      } else if (T < tFewer) {
        k.slam('Momentum.', 96, 282, tMom, {size: 66, color: GOLD, from: 0.6, drop: INK});
        k.text('ServiceTitan', 960 - 66, 300, {size: 30, color: SAND, align: 'right'});
      } else {
        k.slam('Fewer follow-ups.', 96, 282, tFewer, {size: 66, color: 'accent', from: 0.6, drop: INK});
        k.burst(500, 316, tFewer + 0.1, {n: 18, r: 240});
      }
      // the strip under the map: what happens while they wait, then what closing on the visit does
      if (open) {
        if (T >= tComp) k.slam('Call a competitor,', 300, 846, tComp, {size: 39, color: '#87CEEB', from: 0.4});
        if (T >= tTalk) k.slam('or talk themselves out of it.', 300, 900, tTalk, {size: 39, color: CREAM, from: 0.4});
      } else k.slam('Close on the visit.', 300, 846, clr, {size: 39, color: TEAL, from: 0.4});
      return host(k, k.live('why.fewer') ? 'point' : null);
    },

    // ---- ask: the kitchen table. The script types on its card as it is said; options land on the estimate; the pen
    // writes Thursday on the next-visit card and circles it; on "pick one" it ticks B and signs
    ask: (k, T) => {
      const t0 = k.S('ask'), d = px(k);
      const tSay = W(/^Say$/i, t0 + 1), tL1 = W(/^Here$/i, k.S('ask.l1')), tOpt = W(/^options/i, tL1), tL2 = W(/^If$/i, k.S('ask.l2')), tL3 = W(/^What$/i, k.S('ask.l3'));
      const tThu = W(/^Thursday/i, tL2), tPick = W(/^pick$/i, tL3), tOne = W(/^one/i, tPick);
      kitchen(k, {optAt: tOpt, day: {at: tThu, circleAt: tThu + 0.6, tag: tThu + 0.4, text: 'Thursday'}, checkAt: tPick, signAt: tOne + 0.1});
      k.burst(84 * 3, 154 * 3, tPick + 0.1, {n: 10, r: 120});
      k.burst(250 * 3, 146 * 3, tThu + 0.5, {n: 12, r: 150, colors: ['accent', 'paper']});
      // the script card slides up over the table's lower half
      const cy = 194, cw = 332, ch = 130, op = d.ease(t0 + 0.15, 8, 150);
      d.clip(0, 0, 360, 334, () => {
        const Y = cy + op;
        d.P(14 + 2, Y + 2, cw, ch, '#4A2E1B'); d.P(13, Y - 1, cw + 2, ch + 2, INK); d.P(14, Y, cw, ch, CREAM);
        d.P(14, Y, cw, 18, MAROON); d.P(14, Y + 18, cw, 1, INK);
        const head = T >= tSay ? 'SAY THIS (EXAMPLE)' : 'ASK BEFORE YOU WALK OUT.';
        if (op === 0) d.tx(head, 24, Y + 3, {color: CREAM});
        if (T >= tSay && d.fr(tSay) < 6) d.P(14, Y + 19, Math.round(cw * d.fr(tSay) / 6), 1, GOLD);
      });
      const rows = [
        {show: 'Here are your options.', at: tL1},
        {show: 'If you want to go ahead today, I can get you on the schedule for Thursday.', at: tL2},
        {show: 'What questions do you have before you pick one?', at: tL3},
      ];
      if (op === 0) {
        let y = (cy + 24) * 3;
        rows.forEach((r, i) => {
          const on = T >= r.at;
          k.shape(k.rectPts(66, y + 3, 33, 39, 0), {fill: on ? MAROON : '#C9CCD3', line: false});
          k.text(String(i + 1), 82, y + 3, {size: 39, color: CREAM, align: 'center'});
          const times = spoken(r.at, r.show), words = r.show.split(/\s+/), sp = k.measure(' ', {size: 39});
          let x = 120, yy = y, lines = 1;
          words.forEach((wd, j) => {
            const ww = k.measure(wd, {size: 39});
            if (x + ww > 924 && x > 120) { x = 120; yy += 45; lines++; }
            const [ws, we] = times[j] || [1e9, 1e9];
            if (T < ws) k.shape(k.rectPts(x, yy + 33, ww, 3, 0), {fill: '#C9CCD3', line: false});
            else {
              if (/^Thursday/.test(wd) && T >= we) k.shape(k.rectPts(x - 3, yy - 3, ww + 6, 45, 0), {fill: GOLD, line: false});
              k.text(wd, x, yy, {size: 39, color: T < we + 0.05 ? RED : PLUM});
            }
            x += ww + sp;
          });
          y += lines * 45 + 9;
        });
      }
      const r = host(k, k.live('ask.l3') ? 'point' : null);
      if (T >= tL1 - 0.05) r.speech = false;   // the card is the dialog while the script is said
      return r;
    },

    // ---- skip: LEVEL UP. The last question is the part people skip; then what ServiceTitan says a same-visit close
    // shows lands as perks while the bar fills; it levels up on "sale", and the three-line ask unlocks
    skip: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('skip');
      const tLast = W(/^last$/i, k.S('skip.worry')), tBr = W(/^brings$/i, tLast), tWhile = W(/^while$/i, k.S('skip.there')), tST = W(/^ServiceTitan/i, k.S('skip.st'));
      const tObj = W(/^objections/i, k.S('skip.obj')), tFin = W(/^financing/i, tObj), tSale = W(/^sale/i, k.S('skip.sale')), lv = tSale + 0.15;
      const perks = [{text: 'Handles objections', at: tObj}, {text: 'Frames financing', at: tFin}, {text: 'Asks for the sale', at: tSale}];
      quiet(k, () => k.sets.levelup({from: 0, to: 100, max: 100, at: tST, dur: lv - tST, levelAt: lv, level: 1, text: 'LEVEL UP!', stats: perks}));
      // the bar's own label, and the locked perk slots (their rows show before they land)
      if (T < lv) k.text(T >= tST ? 'Your tech, on the visit' : 'Your tech', 90, 570, {size: 39, color: T >= tST ? CREAM : MUTED});
      if (T >= tST) perks.forEach((p, i) => { if (T >= p.at) return; const y = 236 + i * 18; d.tx('+', 110, y, {color: '#6B7080'}); d.P(122, y + 6, 140, 2, '#3D2E45'); d.P(264, y + 2, 7, 9, '#6B7080'); d.P(265, y, 5, 3, '#6B7080'); d.P(266, y + 1, 3, 2, '#2B2033'); });
      if (T >= tSale) k.sweep(366, 816 + 42, k.measure('Asks for the sale', {size: 39}), 6, tSale + 0.1, {color: 'accent'});
      // the worry: a little storm cloud the last question brings out; answered while you're there, it pops
      const tAns = W(/^answer$/i, tWhile), popT = tAns + 0.15;
      if (T >= tBr + 0.3 && T < popT + 0.07) {
        const f = d.fr(tBr + 0.3), cx = 236, cy = 254 - (f < 6 ? [-40, -26, -14, -5, 2, 0][f] : 0) + ((d.F >> 4) & 1), hit = T >= popT - 0.07, gc = hit ? CREAM : '#6B7080', lc = hit ? CREAM : GREY;
        const c2 = k.ctx; c2.save(); c2.translate(-cx * 3, -(cy + 2) * 3); c2.scale(2, 2);
        d.disc(cx - 12, cy + 2, 9, INK); d.disc(cx, cy - 4, 12, INK); d.disc(cx + 12, cy + 2, 9, INK); d.P(cx - 20, cy + 2, 41, 10, INK);
        d.disc(cx - 12, cy + 2, 8, gc); d.disc(cx, cy - 4, 11, lc); d.disc(cx + 12, cy + 2, 8, gc); d.P(cx - 19, cy + 3, 39, 8, gc); d.P(cx - 8, cy - 12, 6, 2, '#C9CCD3');
        if (!hit) { d.P(cx - 7, cy - 2, 2, 3, INK); d.P(cx + 5, cy - 2, 2, 3, INK); d.P(cx - 9, cy - 4, 4, 1, INK); d.P(cx + 5, cy - 4, 4, 1, INK); d.P(cx - 3, cy + 5, 6, 1, INK); d.DOT(cx - 4, cy + 6, INK); d.DOT(cx + 3, cy + 6, INK); }
        if (Math.floor(T * 2) % 2 === 0 && !hit) { d.P(cx - 2, cy + 11, 4, 4, GOLD); d.P(cx - 5, cy + 15, 4, 4, GOLD); d.P(cx - 2, cy + 19, 3, 3, GOLD); }
        c2.restore();
        d.tx('the worry', cx, cy + 34, {size: 30, color: MUTED, align: 'center', lint: f >= 6});
      }
      k.burst(236 * 3, 256 * 3, popT + 0.07, {n: 26, r: 280, colors: ['paper', 'accent2', 'accent']});
      // the plate: the part people skip, then what ServiceTitan says; it clears for LEVEL UP
      if (T < lv) {
        d.win(14, 84, 332, 98, {base: DUSK, hi: '#3D2E45', lo: INK, rule: MAROON});
        if (T < tST) {
          k.slam('The part people skip:', 72, 270, t0 + 0.05, {size: 39, color: GOLD, from: 0.4});
          k.text('"What questions do you have', 72, 318, {size: 39, color: CREAM});
          k.text('before you pick one?"', 72, 363, {size: 39, color: CREAM});
          if (T >= tBr) k.slam('It brings the worry out', 72, 426, tBr, {size: 39, color: CREAM, from: 0.4});
          if (T >= tWhile) { k.slam("while you're still there.", 72, 471, tWhile, {size: 39, color: 'accent', from: 0.4}); }
          if (T >= tLast && T < tLast + 0.6) ping(d, tLast, 22, 104, 316, 34, GOLD);
        } else {
          k.text('ServiceTitan says', 72, 276, {size: 30, color: SAND});
          k.slam('Same-visit closes show', 72, 318, tST + 0.1, {size: 39, color: CREAM, from: 0.4});
          k.slam('how well your tech:', 72, 363, tST + 0.3, {size: 39, color: CREAM, from: 0.4});
          d.P(24, 142, 120, 1, MAROON);
        }
      } else if (T >= lv + 0.45) {   // the unlock: our three-line ask
        d.tx('+', 110, 290, {color: GOLD});
        k.slam(`Unlocked: the ${n.askLines.shown}-line ask`, 366, 870, lv + 0.45, {size: 39, color: GOLD, from: 0.5});
      }
      return host(k, k.live('skip.there') || k.live('skip.sale') ? 'point' : null);
    },

    // ---- caveat: the notebook. The pen writes the honest note as it is said; "not proof" gets underlined
    caveat: (k, T) => {
      const d = px(k), t0 = k.S('caveat');
      const tThis = W(/^This$/i, k.S('caveat.pattern')), tProof = W(/^proof/i, tThis), tTopS = W(/^Top$/i, k.S('caveat.other')), tFor = W(/^for$/i, tTopS), tAsk = W(/^Asking$/i, k.S('caveat.cost')), tOne = W(/^one$/i, tAsk);
      notebook(k);
      // the header on a strip of dark tape, so no rule runs through it
      d.P(58, 96, 250, 26, PLUM); d.P(58, 96, 250, 1, '#3D2E45'); d.dith(58, 96, 4, 26, PAPER); d.dith(304, 96, 4, 26, PAPER, 1);
      k.slam('One honest note.', 192, 291, t0 + 0.05, {size: 66, color: CREAM, from: 0.5});
      const rows = [
        {text: 'This is a pattern, not proof.', at: tThis, y: 130, c: NAVY},
        {text: 'Top shops might close more', at: tTopS, y: 184, c: NAVY},
        {text: 'for other reasons.', at: tFor, y: 202, c: NAVY},
        {text: 'Asking still costs you', at: tAsk, y: 238, c: RED},
        {text: 'one sentence.', at: tOne, y: 256, c: RED},
      ];
      let tip = null;
      rows.forEach((r) => {
        if (T < r.at) return;
        const times = spoken(r.at, r.text), n = written(T, r.text, times), s = r.text.slice(0, n);
        if (n > 0) d.tx(s, 62, r.y + 2, {color: r.c, lint: n === r.text.length});
        if (n < r.text.length || T < times[times.length - 1][1] + 0.15) tip = [62 + d.tw(s) + 1, r.y + 15];
      });
      // the source line (not spoken: it lands once "proof" is said), a red line under "not proof", the double underline
      if (T >= tProof + 0.45) k.slam('ServiceTitan: correlated, not shown to cause.', 62, 448, tProof + 0.45, {size: 27, color: MAROON, from: 0.3});
      if (T >= tProof + 0.2) {
        const l = 62 + d.tw('This is a pattern, '), r = 62 + d.tw('This is a pattern, not proof.'), q = clamp(d.fr(tProof + 0.2) / 6); d.P(l, 146, Math.round((r - l) * q), 1, RED); for (let x = l; x < l + Math.round((r - l) * q); x += 4) d.DOT(x + 1, 147, RED);
      }
      const tEnd = W(/^sentence/i, tOne);
      if (T >= tEnd + 0.4) { const q = clamp(d.fr(tEnd + 0.4) / 6), w = d.tw('one sentence.'); d.P(62, 271, Math.round(w * q), 1, RED); if (q >= 1) d.P(64, 273, Math.round(w * clamp(d.fr(tEnd + 0.6) / 6)), 1, RED); }
      k.burst(62 * 3 + 200, 271 * 3, tEnd + 0.5, {n: 14, r: 180});
      pen(d, ...(tip || [300, 300]));
      return host(k, k.live('caveat.cost') ? 'shrug' : null);
    },

    // ---- close: the street again. The van idles and starts to roll on "drive off", backs in on "Ask", and the
    // customer says yes; then one column: the line, the send line, the plate
    close: (k, T) => {
      const d = px(k), t0 = k.S('close');
      const tDrive = W(/^drive$/i, t0), tAskW = W(/^Ask$/i, k.S('close.drive')), tDrv = W(/^driveway/i, tAskW), tSend = W(/^Send$/i, k.S('close.send')), tGoes = W(/^goes$/i, tSend);
      k.sets.street({t0: 1e6, van: false});
      let vx = 194, moving = false;
      if (T >= tDrive && T < tAskW) { vx = 194 + Math.min(14, Math.floor(10 * (T - tDrive) * (T - tDrive))); moving = vx > 194; }
      else if (T >= tAskW) { const f = d.fr(tAskW), from = Math.min(14, Math.floor(10 * (tAskW - tDrive) * (tAskW - tDrive))); vx = 194 + Math.round(from * (1 - eo(f / 10))); moving = f < 10; }
      const vy = 284 + (moving ? (d.F >> 2) & 1 : 0);
      van2(k, vx, vy, moving ? (d.F >> 1) & 1 : 0); exhaust(d, vx, vy, moving);
      if (T >= tDrv) { bubble(d, vx + 112, 263, 'check', d.fr(tDrv) < 3 ? 2 : 0); d.twinkle(vx + 136, 262, d.fr(tDrv) >> 1); }
      k.burst((vx + 122) * 3, 270 * 3, tDrv + 0.05, {n: 18, r: 220});
      // the column: one left edge (x 120), everything above y 930
      const op = d.ease(t0 + 0.05, 8, -130);
      d.clip(0, 78, 360, 190, () => d.win(14, 138 + op, 332, 124, {base: DUSK, hi: '#3D2E45', lo: INK, rule: MAROON}));
      if (op === 0) {
        k.slam("Don't drive off.", 120, 438, t0 + 0.1, {size: 66, color: CREAM, from: 0.5, drop: INK});
        if (T >= tAskW) k.slam('Ask in the driveway.', 120, 522, tAskW, {size: 66, color: 'accent', from: 0.5, drop: INK});
        if (T >= tGoes) k.sweep(120, 594, k.measure('Ask in the driveway.', {size: 66}), 6, tGoes, {color: 'accent'});
        if (T >= tSend) {
          k.chip('ProofNotFluff', 120, 622, {size: 30});
          k.slam('Send this to whoever goes out', 120, 690, tSend + 0.1, {size: 39, color: CREAM, from: 0.4});
          k.slam('on your estimates.', 120, 735, tSend + 0.25, {size: 39, color: CREAM, from: 0.4});
        }
      }
      return host(k, T >= tGoes ? 'wave' : (k.live('close.drive') ? 'point' : null));
    },
  },
};
