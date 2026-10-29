// Scene: Let me think about it (Lesson 5 in Lead Clinic v2, Quote Clinic, arcade). One function per top-level cue in
// 03_cues/cues.md. Numbers only from k.data (brief.md -> data.js). Every beat lands on a spoken word (window.WORDS).
// The five beats (_shared/voice.md, Lead Clinic v2): hook = the drop-in in three shots (the finished estimate on the
// kitchen table; the van in the driveway and the homeowner at the door; a close-up of the homeowner thinking it over);
// play = the street, "sure, no rush", the van rolls off and leaves the question behind; wait = the dispatch board, the
// hourglass, a competitor's van heading for the same door; fix = the kitchen table, the three lines typed on as said;
// proof = the XP bars, 77 against 62, the source tag with "Pattern, not proof."; button = the street, the van stays, a yes.
// The table, the van, the bubbles and the transitions are lesson 5's own pieces (videos/2026-11-01-same-visit-close).
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
/* runs a set without its own full-frame background fill, so a backdrop drawn first shows through (only that one fill) */
const backdrop = (k, fn) => {
  const c = k.ctx, own = Object.prototype.hasOwnProperty.call(c, 'fillRect'), f = c.fillRect; let first = true;
  c.fillRect = function (x, y, w, h) { if (first && x === 0 && y === 0 && w === 1080 && h === 1251) { first = false; return; } return f.call(this, x, y, w, h); };
  try { return fn(); } finally { if (own) c.fillRect = f; else delete c.fillRect; }
};

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
  /* the wall runs to y 114; the window, its curtains and the clock all start below y 76 (frame 228), clear of the
     lesson bar at the top */
  P(0, 0, 360, 114, SAND); for (let x = 4; x < 360; x += 14) { P(x, 0, 3, 114, PAPER); DOT(x + 8, 84 + (x % 21), '#D9A066'); }
  /* the window: frame, sky, a cloud a pixel every 10 frames, the cross bars, gingham curtains, the sill */
  P(232, 80, 108, 30, INK); P(234, 82, 104, 26, '#87CEEB'); P(234, 82, 104, 9, '#BDE6F5');
  clip(234, 82, 104, 26, () => { const cx = 234 + ((F / 10 | 0) % 150) - 30; disc(cx, 91, 3, CREAM); disc(cx + 6, 89, 4, CREAM); disc(cx + 12, 91, 3, CREAM); P(cx - 2, 92, 16, 2, CREAM); P(234, 101, 104, 7, '#3E7A62'); for (let x = 236; x < 338; x += 9) disc(x, 101, 2, '#2F5A4A'); });
  P(284, 82, 3, 26, SAND); P(234, 94, 104, 2, SAND);
  [[226, 0], [318, 1]].forEach(([x, s]) => { for (let y = 80; y < 108; y += 4) for (let i = 0; i < 26; i += 4) P(x + i, y, 4, 4, ((y / 4 + i / 4 + s) & 1) ? RED : CREAM); P(x, 80, 26, 2, MAROON); });
  P(226, 76, 118, 4, '#8C5A33'); P(228, 108, 114, 4, '#D9A066'); P(228, 111, 114, 2, '#8C5A33');
  /* the clock: the second hand steps once a second (time keeps moving while the quote sits open) */
  const ccx = 48, ccy = 96; disc(ccx, ccy, 16, INK); disc(ccx, ccy, 14, CREAM); ring(ccx, ccy, 14, MAROON, 2);
  for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6; DOT(ccx + Math.round(Math.cos(a) * 10), ccy + Math.round(Math.sin(a) * 10), i % 3 ? GREY : INK); }
  const sa = (Math.floor(T) % 60) * Math.PI / 30 - Math.PI / 2; line(ccx, ccy, ccx + Math.round(Math.cos(sa) * 9), ccy + Math.round(Math.sin(sa) * 9), RED);
  line(ccx, ccy, ccx + 5, ccy - 4, INK, 2); line(ccx, ccy, ccx, ccy - 8, INK); disc(ccx, ccy, 1, INK);
  /* the table: planks, a lit front edge, the floor under it */
  P(0, 114, 360, 4, '#4A2E1B');
  for (let y = 118, i = 0; y < 336; y += 14, i++) { P(0, y, 360, Math.min(14, 336 - y), i % 2 ? '#B07A47' : '#A9733F'); P(0, y, 360, 1, '#D9A066'); if (y + 13 < 336) P(0, y + 13, 360, 1, '#8C5A33'); for (let x = (i * 53) % 90; x < 360; x += 90) P(x, y + 1, 1, Math.min(12, 335 - y), '#8C5A33'); DOT((i * 71) % 360, y + 6, '#8C5A33'); }
  P(0, 336, 360, 6, '#8C5A33'); P(0, 336, 360, 1, '#D9A066'); P(0, 342, 360, 4, '#4A2E1B');
  for (let y = 346, r = 0; y < 640; y += 16, r++) for (let x = 0, c = 0; x < 360; x += 16, c++) P(x, y, 16, 16, (r + c) % 2 ? '#5A3A22' : '#4A2E1B');
  // the clipboard: board, metal clip, the estimate
  const cbx = 18, cby = 126;
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
  const mx = 168, my = 152;
  disc(mx + 1, my + 2, 12, '#8C5A33'); ring(mx + 13, my, 5, INK, 2); disc(mx, my, 12, INK); disc(mx, my, 11, RED); disc(mx, my, 8, MAROON); disc(mx, my, 7, '#4A2E1B'); DOT(mx - 3, my - 3, '#7A4E2C'); DOT(mx - 2, my - 3, '#7A4E2C');
  for (let i = 0; i < 3; i++) { const a = ((F >> 2) + i * 4) % 12; DOT(mx - 4 + i * 4 + ((a >> 1) & 1), my - 14 - a, PAPER); DOT(mx - 4 + i * 4 + ((a >> 1) & 1), my - 15 - a, CREAM); }
  // the next-visit card
  const ncx = 190, ncy = 132;
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
  let p = [158, 206];
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
  T2.xp = (ctx, q, e) => {
    const s = 96, cols = 10, cw = e.W / cols;
    for (let r = 0; r * s < e.H; r++) { const n = Math.floor(clamp(q * 1.5 - (r % 4) * 0.08) * cols + 0.0001); for (let c = 0; c < n; c++) { e.fill('#1B1420', c * cw, r * s, cw, s); e.fill('#2F6F67', c * cw + 6, r * s + 6, cw - 12, s - 12); e.fill('#6FB7A8', c * cw + 6, r * s + 6, cw - 12, 21); } }
  };
}

// a thought bubble at any whole scale (the hook's close-up)
const bubbleN = (k, d, x, y, kind, s, pop = 0) => { const c = k.ctx; c.save(); c.translate(Math.round(x) * 3, Math.round(y) * 3); c.scale(s, s); bubble(d, 0, 0, kind, pop); c.restore(); };
// an hourglass at a whole scale whose sand runs once a second and flips
const hourglass = (k, d, x, y, s, t0) => {
  const c = k.ctx; c.save(); c.translate(Math.round(x) * 3, Math.round(y) * 3); c.scale(s, s);
  const T = k.T, flip = Math.floor(Math.max(0, T - t0)) % 2, sand = Math.min(4, Math.floor((Math.max(0, T - t0) % 1) * 5));
  d.P(-1, -1, 11, 16, INK); d.P(0, 0, 9, 2, '#8C5A33'); d.P(0, 12, 9, 2, '#8C5A33');
  d.P(1, 2, 7, 10, '#BDE6F5'); d.P(3, 6, 3, 2, '#BDE6F5');
  const top = flip ? sand : 4 - sand; d.P(2, 2 + (4 - top), 5, top, GOLD); d.P(2, 12 - (4 - top), 5, 4 - top, GOLD); d.DOT(4, 7, GOLD);
  c.restore();
};
// the title plate that carries the on-screen hook through the three shots
const hookPlate = (k, d) => {
  d.win(14, 86, 332, 62, {base: DUSK, hi: '#3D2E45', lo: INK, rule: MAROON});
  k.text("The estimate's done.", 540, 276, {size: 39, color: GOLD, align: 'center'});
  const s = '"Let me think about it."', z = k.measure(s, {size: 66}) <= 900 ? 66 : 39;
  k.slam(s, 540, 336, -1, {size: z, color: CREAM, align: 'center', drop: INK});
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 5',
  sendLine: 'Send this to whoever runs your estimates.',
  transitions: {play: 'dissolve', wait: 'levelselect', fix: 'iris', proof: 'xp', button: 'drive'},
  trauma: {'wait.comp': 0.5},
  sections: {
    // ---- hook: the drop-in in three shots under one title plate. Cover: the finished estimate on the kitchen table, Snow
    // in his spot. Cut by 0.8 s to the street (the van in the drive, the homeowner's door, a thinking bubble; Snow comes in).
    // Cut on "let" to the close-up: a big thought bubble and an hourglass on plum.
    hook: (k, T) => {
      const d = px(k), {P} = d;
      const tHome = W(/^they$/i, k.S('hook.home'), 0.8), tLet = W(/^let$/i, k.S('hook.let'), 2.0);
      const cut1 = Math.min(0.8, Math.max(0.5, tHome - 0.05)), cut2 = Math.min(2.6, Math.max(cut1 + 0.6, tLet - 0.05));
      if (T < cut1) {
        // the room drops 100 px-rows so the plate sits on the wall and the estimate, the coffee and the card show whole
        P(0, 0, 360, 100, SAND); for (let x = 4; x < 360; x += 14) P(x, 0, 3, 100, PAPER);
        k.ctx.save(); k.ctx.translate(0, 300); kitchen(k, {optAt: -1, day: {}}); k.ctx.restore();
        hookPlate(k, d);
        k.burst(540, 780, 0.35, {n: 14, r: 220, colors: ['accent', 'paper']});
        return host(k);
      }
      if (T < cut2) {
        k.sets.street({t0: 1e6, van: false});
        van2(k, 194, 284, 0); exhaust(d, 194, 284, false);
        const [dx, dy] = doorOf(1);
        bubble2(k, d, dx - 12, dy - 36, 'dots', d.fr(cut1) < 3 ? 1 : 0);
        hookPlate(k, d);
        return host(k);
      }
      // the close-up: plum, a dither floor, the thought bubble at 6x with its dots stepping, the hourglass at 4x
      P(0, 0, 360, 640, PLUM); for (let y = 160; y < 417; y += 8) for (let x = ((y >> 3) & 1) * 8; x < 360; x += 16) P(x, y, 2, 2, '#3D2E45');
      const pop = d.fr(cut2) < 4 ? [6, 3, 1, 0][d.fr(cut2)] : 0;
      bubbleN(k, d, 112, 176, 'dots', 6, pop);
      hourglass(k, d, 34, 200, 4, cut2);
      hookPlate(k, d);
      k.burst(272 * 3, 216 * 3, cut2 + 0.05, {n: 12, r: 180, colors: ['paper', 'accent2']});
      return host(k, 'shrug');
    },

    // ---- play: the street. "Sure, no rush." The van rolls off on "drive"; the question is left at the door
    play: (k, T) => {
      const d = px(k), t0 = k.S('play');
      const tDrive = W(/^drive$/i, k.S('play.drive'), t0 + 1.2);
      k.sets.street({t0: 1e6, van: false});
      let vx = 194, moving = false;
      if (T >= tDrive) { const t = T - tDrive; vx = 194 + Math.floor(70 * t * t + 8 * t); moving = true; }
      if (vx < 366) { const vy = 284 + (moving ? (d.F >> 2) & 1 : 0); van2(k, vx, vy, moving ? (d.F >> 1) & 1 : 0); exhaust(d, vx, vy, moving); }
      const [dx, dy] = doorOf(1), bx = dx - 12, by = dy - 36;
      if (T < tDrive + 0.5) bubble2(k, d, bx, by, 'dots');
      else { bubble2(k, d, bx, by, '?', (d.F >> 4) & 1); if (T < tDrive + 0.9) ping(d, tDrive + 0.5, bx - 1, by - 1, 42, 28, GOLD); }
      d.win(14, 86, 332, 62, {base: DUSK, hi: '#3D2E45', lo: INK, rule: MAROON});
      if (T < tDrive) k.slam('"Sure, no rush."', 540, 300, t0 + 0.05, {size: 66, color: CREAM, align: 'center', from: 0.5, drop: INK});
      else k.slam('And you drive off.', 540, 300, tDrive, {size: 66, color: 'accent', align: 'center', from: 0.5, drop: INK});
      return host(k, T < tDrive ? 'wave' : 'shrug');
    },

    // ---- wait: the dispatch board. One visit to one house; while the quote sits open the follow-up trips pile on and a
    // competitor's van heads for the same door
    wait: (k, T) => {
      const d = px(k), t0 = k.S('wait');
      const tWait = W(/^waiting/i, t0, t0 + 0.3), tComp = W(/^competitor/i, k.S('wait.comp')), tTalk = W(/^talk$/i, k.S('wait.talk'));
      const SHOP = [0.09, 0.62], HOUSE = [0.64, 0.82], RIVAL = [0.79, 0.46];
      const pins = [{x: SHOP[0], y: SHOP[1], at: t0 + 0.05, c: TEAL}, {x: HOUSE[0], y: HOUSE[1], at: t0 + 0.25, c: RED}, {x: RIVAL[0], y: RIVAL[1], at: tComp, c: '#3B82C4'}];
      const routes = [
        {pts: [SHOP, [0.31, 0.62], [0.31, 0.82], HOUSE], at: t0 + 0.4, dur: 0.8, c: TEAL},
        {pts: [[0.09, 0.67], [0.45, 0.67], [0.45, 0.87], [0.64, 0.87]], at: tWait + 0.4, dur: 0.9},
        {pts: [RIVAL, [0.79, 0.73], [0.67, 0.73], [0.67, 0.8]], at: tComp + 0.15, dur: 0.7, c: '#3B82C4'},
      ];
      const m = k.sets.dispatch({pins, routes});
      const [hx, hy] = m.at(HOUSE[0], HOUSE[1]).map((v) => Math.round(v / 3));
      if (T >= tWait) {
        const flip = Math.floor(T - tWait) % 2, sand = Math.min(4, Math.floor(((T - tWait) % 1) * 5)), gx = hx - 30, gy = hy - 34;
        d.P(gx - 1, gy - 1, 11, 16, INK); d.P(gx, gy, 9, 2, '#8C5A33'); d.P(gx, gy + 12, 9, 2, '#8C5A33');
        d.P(gx + 1, gy + 2, 7, 10, '#BDE6F5'); d.P(gx + 3, gy + 6, 3, 2, '#BDE6F5');
        const top = flip ? sand : 4 - sand; d.P(gx + 2, gy + 2 + (4 - top), 5, top, GOLD); d.P(gx + 2, gy + 12 - (4 - top), 5, 4 - top, GOLD); d.DOT(gx + 4, gy + 7, GOLD);
      }
      bubble(d, hx + 6, hy - 38, T >= tTalk ? 'x' : '?', (d.F >> 4) & 1);
      if (T >= tTalk && T < tTalk + 0.4) ping(d, tTalk, hx + 5, hy - 39, 22, 15, RED);
      d.win(24, 88, 312, 40, {base: DUSK, hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
      k.slam('The waiting starts.', 96, 282, t0 + 0.05, {size: 66, color: CREAM, from: 0.5, drop: INK});
      if (T >= tComp && T < tTalk) k.slam('Call a competitor.', 270, 846, tComp, {size: 39, color: '#87CEEB', from: 0.4});
      if (T >= tTalk) k.slam('Or talk themselves out of it.', 120, 846, tTalk, {size: 39, color: CREAM, from: 0.4});
      return host(k, T >= tTalk ? 'shrug' : null);
    },

    // ---- fix: the kitchen table. The script types on its card as it is said; options land on the estimate; the pen
    // writes Thursday on the next-visit card and circles it; on "pick one" it ticks B and signs
    fix: (k, T) => {
      const t0 = k.S('fix'), d = px(k);
      const tL1 = W(/^Here$/i, k.S('fix.l1')), tOpt = W(/^options/i, tL1), tL2 = W(/^If$/i, k.S('fix.l2')), tL3 = W(/^What$/i, k.S('fix.l3'));
      const tThu = W(/^Thursday/i, tL2), tPick = W(/^pick$/i, tL3), tOne = W(/^one/i, tPick), tSay = tL1;
      kitchen(k, {optAt: tOpt, day: {at: tThu, circleAt: tThu + 0.6, tag: tThu + 0.4, text: 'Thursday'}, checkAt: tPick, signAt: tOne + 0.1});
      k.burst(84 * 3, 174 * 3, tPick + 0.1, {n: 10, r: 120});
      k.burst(250 * 3, 166 * 3, tThu + 0.5, {n: 12, r: 150, colors: ['accent', 'paper']});
      const cy = 214, cw = 332, ch = 110, op = d.ease(t0 + 0.15, 8, 150);
      d.clip(0, 0, 360, 334, () => {
        const Y = cy + op;
        d.P(14 + 2, Y + 2, cw, ch, '#4A2E1B'); d.P(13, Y - 1, cw + 2, ch + 2, INK); d.P(14, Y, cw, ch, CREAM);
        d.P(14, Y, cw, 18, MAROON); d.P(14, Y + 18, cw, 1, INK);
        const head = T >= tSay ? 'SAY THIS (EXAMPLE)' : 'TRY THIS BEFORE YOU LEAVE.';
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
      const r = host(k, k.live('fix.l3') ? 'point' : null);
      if (T >= tL1 - 0.05) r.speech = false;   // the card is the dialog while the script is said
      return r;
    },

    // ---- proof: the XP bars. ServiceTitan's top 10% fill to 77; everyone else to 62; the segments between blink as the
    // gap; the source tag says "Pattern, not proof." the whole time the numbers are on screen
    proof: (k, T) => {
      const n = k.data.numbers, d = px(k), {P} = d, t0 = k.S('proof');
      const tTopW = W(/^top$/i, t0, t0 + 0.6), t77 = W(/^seventy/i, k.S('proof.top')), tElse = W(/^Everyone$/i, k.S('proof.rest')), t62 = W(/^sixty/i, tElse);
      const tGap = W(/^gap$/i, k.S('proof.why')), tMom = W(/^momentum/i, tGap);
      quiet(k, () => k.sets.levelup({from: 0, to: n.topClose.value, max: 100, at: t77, dur: 0.8}));
      P(14, 174, 332, 2, INK); P(14, 300, 332, 2, INK); P(14, 174, 2, 128, INK); P(344, 174, 2, 128, INK);
      P(16, 176, 328, 1, MAROON); P(16, 299, 328, 1, MAROON); P(16, 176, 1, 124, MAROON); P(343, 176, 1, 124, MAROON);
      [[14, 174], [342, 174], [14, 298], [342, 298]].forEach(([x, y]) => { P(x, y, 4, 4, ORANGE); d.DOT(x + 1, y + 1, GOLD); });
      P(20, 157, 10 + d.tw('Same-visit close rate', 30), 16, INK); P(21, 158, 8 + d.tw('Same-visit close rate', 30), 14, MAROON);
      d.tx('Same-visit close rate', 25, 160, {size: 30, color: CREAM});
      k.text('Pattern, not proof.', 930, 480, {size: 30, color: GOLD, align: 'right'});
      d.win(14, 84, 332, 70, {base: DUSK, hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
      sprites(k).icon('star', 304, 96, 3); if (T >= t0 + 1) d.twinkle(330, 98, (d.F >> 2) % 8 < 4 ? (d.F >> 2) % 4 : 0, GOLD);
      k.slam('ServiceTitan', 72, 270, t0 + 0.05, {size: 66, color: 'accent', from: 0.5, drop: INK});
      if (T < tMom) k.slam('Estimates closed on the same visit', 72, 354, t0 + 0.25, {size: 39, color: CREAM, from: 0.4});
      else k.slam('The gap: momentum.', 72, 354, tMom, {size: 39, color: GOLD, from: 0.4});
      k.text(`Its customers, ${n.stMonths.shown} months to Jan ${n.stYear.shown}`, 72, 408, {size: 30, color: SAND});
      if (T >= tTopW) k.slam(`Top ${n.topPct.shown} by revenue`, 90, 576, tTopW, {size: 39, color: GOLD, from: 0.4});
      else k.text('Top shops', 90, 576, {size: 39, color: MUTED});
      if (T >= t77) k.slam(cnt(k, n.topClose, t77, {suffix: '%'}), 930, 546, t77, {size: 66, color: TEAL, align: 'right', from: 0.5, drop: INK});
      if (T >= t77 && T < t77 + 1.4) { const f = d.fr(t77 + 0.8); if (f >= 0) ping(d, t77 + 0.8, 30, 208, Math.round(280 * 0.77), 14, TEAL); }
      k.burst(90 + 840 * 0.77, 645, t77 + 0.8, {n: 16, r: 200, colors: ['teal', 'paper']});
      if (T >= t77 + 0.8) {
        const cx = Math.round(30 + 280 * n.topClose.value / 100) - 6, f = d.fr(t77 + 0.8), cy = 196 - (f < 6 ? [6, 4, 2, 0, -1, 0][f] : 0);
        d.spr(['#..#..#', '##.#.##', '#######', '#######', '.......', '#######'], {'#': GOLD}, cx, cy); P(cx + 3, cy + 2, 1, 1, RED); P(cx, cy + 5, 7, 1, ORANGE);
      }
      const X = 30, Y = 248, BW = 280, seg = 20, sw = BW / seg;
      P(X - 2, Y - 2, BW + 4, 18, INK); P(X - 1, Y - 1, BW + 2, 16, '#6B7080'); P(X, Y, BW, 14, DUSK);
      const v = T >= t62 ? n.restClose.value * eo((T - t62) / 0.8) : 0, nn = Math.floor(seg * clamp(v / 100) + 0.0001);
      for (let i = 0; i < nn; i++) { const x = Math.round(X + i * sw); P(x + 1, Y + 1, Math.round(sw) - 2, 12, ORANGE); P(x + 1, Y + 1, Math.round(sw) - 2, 3, GOLD); P(x + 1, Y + 10, Math.round(sw) - 2, 3, '#B07A47'); }
      if (T >= t62 && T < t62 + 0.8 && nn < seg && (d.F >> 1) & 1) P(Math.round(X + nn * sw) + 1, Y + 1, Math.round(sw) - 2, 12, '#3D2E45');
      k.text('Everyone else', 90, 696, {size: 39, color: T >= tElse ? CREAM : MUTED});
      if (T >= t62) k.slam(cnt(k, n.restClose, t62, {suffix: '%'}), 930, 666, t62, {size: 66, color: ORANGE, align: 'right', from: 0.5, drop: INK});
      if (T >= tGap) {
        const a = Math.floor(seg * n.restClose.value / 100 + 0.0001), b = Math.floor(seg * n.topClose.value / 100 + 0.0001), on = Math.floor((T - tGap) * 2) % 2 === 0;
        for (let i = a; i < b; i++) { const x = Math.round(X + i * sw); P(x + 1, Y + 1, Math.round(sw) - 2, 1, on ? GOLD : '#B07A47'); P(x + 1, Y + 12, Math.round(sw) - 2, 1, on ? GOLD : '#B07A47'); P(x + 1, Y + 1, 1, 12, on ? GOLD : '#B07A47'); P(x + Math.round(sw) - 2, Y + 1, 1, 12, on ? GOLD : '#B07A47'); }
        const x0 = Math.round(X + a * sw), x1 = Math.round(X + b * sw), q = clamp(d.fr(tGap) / 6);
        P(x0, 266, 1, 4, GOLD); P(x1 - 1, 266, 1, 4, GOLD); P(x0, 269, Math.round((x1 - x0) * q), 1, GOLD);
      }
      k.text('The gap', 90, 834, {size: 39, color: T >= tGap ? GOLD : MUTED});
      if (T >= tGap) k.slam(`${n.gap.shown} points`, 930, 810, tGap, {size: 66, color: GOLD, align: 'right', from: 0.5, drop: INK});
      else { P(250, 284, 60, 2, '#3D2E45'); for (let x = 250; x < 310; x += 8) P(x, 284, 4, 2, '#6B7080'); }
      return host(k, k.live('proof.top') || k.live('proof.rest') ? 'point' : null);
    },

    // ---- button: the street again. The van stays in the drive; on "driveway" the customer says yes; the rule lands
    button: (k, T) => {
      const d = px(k), t0 = k.S('button');
      const tDrv = W(/^driveway/i, k.S('button.drive')), tSo = W(/^So$/i, k.S('button.alone')), tAlone = W(/^alone/i, tSo);
      k.sets.street({t0: 1e6, van: false});
      van2(k, 194, 284, 0); exhaust(d, 194, 284, false);
      if (T >= tDrv) { bubble(d, 306, 263, 'check', d.fr(tDrv) < 3 ? 2 : 0); d.twinkle(330, 262, d.fr(tDrv) >> 1); }
      else bubble(d, 306, 263, 'dots');
      k.burst(316 * 3, 270 * 3, tDrv + 0.05, {n: 18, r: 220});
      const op = d.ease(t0 + 0.05, 8, -130);
      const grow = (t, a, b) => (T < t ? a : a + Math.round((b - a) * eo(d.fr(t) / 6)));
      const bh = T < tSo ? 42 : grow(tSo, 42, 96);
      d.clip(0, 78, 360, 190, () => d.win(14, 138 + op, 332, bh, {base: DUSK, hi: '#3D2E45', lo: INK, rule: MAROON}));
      if (op === 0) {
        k.slam('Ask before you leave.', 120, 438, t0 + 0.1, {size: 66, color: CREAM, from: 0.5, drop: INK});
        if (T >= tSo) {
          k.slam("Don't let them think", 120, 522, tSo, {size: 66, color: 'accent', from: 0.5, drop: INK});
          k.slam('about it alone.', 120, 600, tSo + 0.3, {size: 66, color: 'accent', from: 0.5, drop: INK});
        }
        if (T >= tAlone) k.sweep(120, 672, k.measure('about it alone.', {size: 66}), 6, tAlone, {color: 'accent'});
      }
      return host(k, T >= tAlone ? 'wave' : (k.live('button.drive') ? 'point' : null));
    },
  },
};
