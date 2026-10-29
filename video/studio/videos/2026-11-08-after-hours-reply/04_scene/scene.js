// Scene: The after-hours quote request (AI lead lane, lesson 1, Lead Clinic v2, arcade). One function per top-level cue in
// 03_cues/cues.md. Numbers only from k.data (brief.md -> data.js). Every beat lands on a spoken word (window.WORDS).
// The five beats: hook = the drop-in in four shots under one title plate (the bedroom at night and the lit phone; the
// message close up; the bedside clock at eleven; the same clock ringing at seven in the morning); play = the chat set,
// the reply half typed while the day runs, "Still a draft.", the notification that they booked elsewhere; fix = an
// unbranded AI chat app (our own piece) where the prompt types on as said and the drafted reply lands, the owner ticks it
// and presses send; proof = the gauge, 26 for cleaning businesses that reply within an hour; button = the departures
// board, today: asleep at 11, the quote sent, the first job next.
const INK = '#120D14', CREAM = '#FFF7EA', PAPER = '#F4E6D3', SAND = '#E6D3BC', MUTED = '#B39A88', GOLD = '#F7C873', ORANGE = '#F2A541',
  RED = '#E2633B', MAROON = '#7A3442', TEAL = '#6FB7A8', GREY = '#9AA0AD', NAVY = '#253048', PLUM = '#2B2033', DUSK = '#1B1420',
  BLUE = '#3B82C4', SKY = '#87CEEB', GREEN = '#3E7A62';
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
    const base = o.base || NAVY, hi = o.hi || BLUE, lo = o.lo || DUSK, rule = o.rule === undefined ? SKY : o.rule;
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
const W = (re, from, dflt) => { const w = WS().find((x) => x.start >= from - 1.1 && re.test(x.w)); return w ? w.start : (dflt != null ? dflt : from); };
const WE = (re, from, dflt) => { const w = WS().find((x) => x.start >= from - 1.1 && re.test(x.w)); return w ? w.end : (dflt != null ? dflt : from); };
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
const cnt = (k, num, t0, o = {}) => k.count(num.value, k.lin(t0, t0 + 0.7) >= 1 ? 1 : 0.85 + 0.15 * k.lin(t0, t0 + 0.7), Object.assign({from: 0}, o));
const host = (k, pose) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150});
// a typed paragraph: each word lands as it is said (red while said, then ink); words not yet said are grey stubs
const typed = (k, T, text, t0, x, y, maxX, o = {}) => {
  const size = o.size || 39, lh = o.lh || 45, times = spoken(t0, text), words = text.split(/\s+/), sp = k.measure(' ', {size});
  let xx = x, yy = y, lines = 1;
  words.forEach((wd, j) => {
    const ww = k.measure(wd, {size});
    if (xx + ww > maxX && xx > x) { xx = x; yy += lh; lines++; }
    const [ws, we] = times[j] || [1e9, 1e9];
    if (T < ws) { if (o.stubs !== false) k.shape(k.rectPts(xx, yy + size - 6, ww, 3, 0), {fill: o.stub || '#C9CCD3', line: false}); }
    else k.text(wd, xx, yy, {size, color: T < we + 0.05 ? (o.hot || RED) : (o.color || PLUM)});
    xx += ww + sp;
  });
  return lines;
};
// a block of text written out fast from t0 (a pasted or drafted message), wrapped to maxX, at a pace of `cps` characters a second
const written = (k, T, text, t0, x, y, maxX, o = {}) => {
  const size = o.size || 30, lh = o.lh || 45, n = T < t0 ? 0 : Math.floor((T - t0) * (o.cps || 140)), words = text.split(/\s+/), sp = k.measure(' ', {size});
  let xx = x, yy = y, used = 0, lines = 1;
  words.forEach((wd) => {
    const ww = k.measure(wd, {size});
    if (xx + ww > maxX && xx > x) { xx = x; yy += lh; lines++; }
    if (used + wd.length <= n) k.text(wd, xx, yy, {size, color: (o.colorOf && o.colorOf(wd)) || o.color || PLUM, lint: o.lint});
    used += wd.length + 1; xx += ww + sp;
  });
  return lines;
};

// ================================================================================================================
// the bedside: our own set piece. A wall, a window (moon and stars at night, sun and a tree at morning), a nightstand with
// a lamp, the analog clock (hands at the hour, bells that shake when it rings) and the phone lying flat.
const clock = (d, cx, cy, r, hour, o = {}) => {
  const {P, disc, ring, line, DOT, F} = d, shake = o.ring ? ((F >> 1) & 1 ? 1 : -1) : 0;
  // the bells and the hammer
  if (o.bells !== false) {
    [[-1, 0], [1, 0]].forEach(([s]) => { const bx = cx + s * (r - 2) + (o.ring ? shake * s : 0), by = cy - r + 1; disc(bx, by, 6, INK); disc(bx, by, 5, o.night ? '#6B7080' : GOLD); DOT(bx - 2, by - 3, CREAM); });
    P(cx - 1, cy - r - 6, 3, 6, INK);
    if (o.ring) { P(cx - 2 + shake * 3, cy - r - 8, 5, 3, GREY); for (let i = 0; i < 3; i++) { const a = (F >> 2) % 2; P(cx - r - 10 - i * 3 - a, cy - r - 4 + i * 6, 4, 1, GOLD); P(cx + r + 7 + i * 3 + a, cy - r - 4 + i * 6, 4, 1, GOLD); } }
  }
  disc(cx, cy, r + 2, INK); disc(cx, cy, r, o.night ? '#2F3A55' : CREAM); ring(cx, cy, r, o.night ? '#4A5578' : MAROON, 2);
  for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6; DOT(cx + Math.round(Math.cos(a) * (r - 5)), cy + Math.round(Math.sin(a) * (r - 5)), i % 3 ? (o.night ? '#6B7080' : GREY) : (o.night ? SKY : INK)); }
  const ha = (hour % 12) * Math.PI / 6 - Math.PI / 2, ma = -Math.PI / 2, hc = o.night ? SKY : INK;
  line(cx, cy, cx + Math.round(Math.cos(ha) * r * 0.5), cy + Math.round(Math.sin(ha) * r * 0.5), hc, 2);
  line(cx, cy, cx + Math.round(Math.cos(ma) * r * 0.78), cy + Math.round(Math.sin(ma) * r * 0.78), hc);
  disc(cx, cy, 2, o.night ? GOLD : RED);
  // the legs
  line(cx - r + 4, cy + r - 2, cx - r, cy + r + 5, INK, 2); line(cx + r - 4, cy + r - 2, cx + r, cy + r + 5, INK, 2);
};
const bedroom = (k, d, o = {}) => {
  const {P, DOT, disc, dith, F} = d, night = !!o.night;
  // the wall
  P(0, 0, 360, 330, night ? '#1E2238' : '#E8C99A');
  for (let x = 6; x < 360; x += 18) P(x, 0, 2, 330, night ? '#232842' : '#EED6AE');
  // the window
  const wx = 196, wy = 164, ww = 140, wh = 92;
  P(wx - 4, wy - 4, ww + 8, wh + 8, INK); P(wx - 2, wy - 2, ww + 4, wh + 4, night ? '#4A4E5A' : '#B07A47');
  if (night) {
    P(wx, wy, ww, wh, '#0E1430'); dith(wx, wy + wh - 20, ww, 20, '#1B2450');
    for (let i = 0; i < 18; i++) { const sx = wx + 4 + Math.floor(hash(i * 2.3) * (ww - 8)), sy = wy + 4 + Math.floor(hash(i * 5.1) * (wh - 30)); DOT(sx, sy, (Math.floor(F / 12) + i) % 7 === 0 ? CREAM : '#6B7080'); }
    disc(wx + 104, wy + 24, 11, '#F4E6D3'); disc(wx + 109, wy + 20, 10, '#0E1430');
    for (let i = 0; i < 5; i++) P(wx + i * 30, wy + wh - 14 - (i % 2) * 6, 22, 14 + (i % 2) * 6, '#151A33');
  } else {
    P(wx, wy, ww, wh, '#BDE6F5'); P(wx, wy, ww, 30, '#9FD6EE');
    const sr = (F >> 2) % 2; disc(wx + 28, wy + 26, 10, GOLD); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4 + sr * 0.2; P(wx + 28 + Math.round(Math.cos(a) * 15), wy + 26 + Math.round(Math.sin(a) * 15), 2, 2, ORANGE); }
    disc(wx + 104, wy + 64, 18, GREEN); disc(wx + 92, wy + 70, 12, '#2F5A4A'); P(wx + 102, wy + 76, 4, 20, '#5A3A22');
  }
  P(wx + ww / 2 - 1, wy, 3, wh, night ? '#4A4E5A' : '#B07A47'); P(wx, wy + wh / 2 - 1, ww, 3, night ? '#4A4E5A' : '#B07A47');
  P(wx - 8, wy + wh + 4, ww + 16, 4, night ? '#3D2E45' : '#8C5A33');
  // the nightstand
  P(0, 330, 360, 6, night ? '#2B2033' : '#8C5A33'); P(0, 336, 360, 81, night ? '#151827' : '#B07A47');
  P(0, 282, 186, 48, night ? '#2B2033' : '#8C5A33'); P(0, 282, 186, 2, night ? '#3D2E45' : '#D9A066'); P(0, 296, 186, 1, INK);
  for (let y = 300; y < 330; y += 14) { P(12, y, 160, 10, night ? '#231B2A' : '#6B4226'); disc(92, y + 5, 2, night ? '#6B7080' : GOLD); }
  // the lamp (off at night, the shade dark)
  P(20, 236, 30, 4, INK); P(24, 218, 22, 18, night ? '#3D2E45' : CREAM); P(33, 240, 4, 42, night ? '#4A4E5A' : '#8C5A33'); P(26, 280, 18, 3, INK);
  // floor below
  for (let y = 417; y < 640; y += 16) for (let x = 0, c = 0; x < 360; x += 16, c++) P(x, y, 16, 16, ((y >> 4) + c) % 2 ? (night ? '#1B1420' : '#6B4226') : (night ? '#151020' : '#5A3A22'));
};
// the phone lying flat on the nightstand: dark, or lit with a notification card
const flatPhone = (k, d, x, y, lit, o = {}) => {
  const {P, DOT, F} = d;
  P(x + 2, y + 2, 58, 30, INK); P(x - 1, y, 58, 30, INK); P(x, y - 1, 56, 32, INK);
  P(x, y, 56, 30, lit ? '#2F6F67' : '#1B1420'); P(x + 1, y + 1, 54, 1, '#4A4E5A');
  if (lit) {
    P(x + 3, y + 4, 50, 22, CREAM); P(x + 5, y + 7, 8, 8, '#2F6F67'); P(x + 7, y + 9, 4, 4, CREAM);
    P(x + 16, y + 8, 30, 2, PLUM); P(x + 16, y + 13, 24, 2, MUTED); P(x + 16, y + 18, 34, 2, MUTED);
    if (((F >> 3) & 3) === 0) for (let i = 1; i < 4; i++) { P(x - 2 - i * 2, y - 2 - i * 2, 60 + i * 4, 1, '#4A8F86'); }
    // glow on the stand around it
    d.dith(x - 10, y + 30, 76, 3, '#2F6F67', F & 1);
  }
};
// the title plate: the time it came in, small; when it was seen, the hero line in the accent
const hookPlate = (k, d, n) => {
  d.win(14, 86, 332, 68, {base: DUSK, hi: '#3D2E45', lo: INK, rule: MAROON});
  k.text(`Quote request, ${n.nightHour.shown} pm.`, 540, 276, {size: 39, color: CREAM, align: 'center'});
  k.slam(`Seen at ${n.morningHour.shown} am.`, 540, 324, -1, {size: 132, color: GOLD, align: 'center', drop: INK});
};
const MSG = (n) => `Hi! Need a move-out clean before Friday. ${n.beds.shown} bed, ${n.baths.shown} bath. How much?`;
// the gold EXAMPLE tag (the story is ours, not data): x, y low-res; returns its width
const exampleTag = (d, x, y) => { const tag = 'EXAMPLE', w = d.tw(tag) + 8; d.P(x + 1, y + 1, w, 15, INK); d.P(x, y, w, 15, GOLD); d.tx(tag, x + 4, y + 1, {color: INK}); return w; };
// a dark label under a clock: centered at (cx, y) low-res
const clockTag = (k, d, s, cx, y, c) => { const w = d.tw(s) + 12; d.P(cx - w / 2 + 1, y + 1, w, 17, INK); d.P(cx - w / 2, y, w, 17, DUSK); k.text(s, cx * 3, (y + 2) * 3, {size: 39, color: c, align: 'center'}); };

// the AI chat app: our own piece, unbranded. A window with a title bar, the conversation, and a send key
const appWindow = (k, d, x, y, w, h) => {
  const {P, DOT} = d;
  P(x + 3, y + 3, w, h, INK); P(x - 1, y, w + 2, h, INK); P(x, y - 1, w, h + 2, INK);
  P(x, y, w, h, '#F7F1E6'); P(x, y, w, 20, '#2B2033'); P(x, y + 20, w, 1, INK);
  [RED, GOLD, TEAL].forEach((c, i) => { d.disc(x + 9 + i * 9, y + 10, 3, c); });
  d.tx('AI CHAT APP', x + 40, y + 4, {color: CREAM});
  exampleTag(d, x + 46 + d.tw('AI CHAT APP'), y + 3);
  for (let yy = y + 26; yy < y + h - 4; yy += 8) for (let xx = x + 4 + ((yy >> 3) & 1) * 4; xx < x + w - 4; xx += 16) DOT(xx, yy, '#EDE3D2');
};
const bubbleBox = (d, x, y, w, h, c, edge) => { const {P} = d; P(x + 1, y, w - 2, h, c); P(x, y + 1, w, h - 2, c); P(x + 1, y + h - 1, w - 2, 1, edge); };
// the readout of a set we draw ourselves (the gauge's own small one is kept quiet)
const quiet = (k, re, fn) => { const t = k.text; k.text = function (s, ...a) { return re.test(String(s)) ? {w: 0, h: 0, lines: []} : t.call(this, s, ...a); }; try { return fn(); } finally { k.text = t; } };

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'AI LESSON 1',
  sendLine: 'Send this to whoever answers quote requests.',
  transitions: {play: 'dissolve', fix: 'levelselect', proof: 'dissolve', button: 'levelselect'},
  trauma: {'play.booked': 0.5},
  sections: {
    // ---- hook: four shots under one plate. Cover: the bedroom at night, the phone lit on the stand. Cut by 0.8 s to the
    // phone close up (the message, example, with the time it came in). Cut on "eleven" to the bedside clock at 11. Cut on
    // "You" to the same clock ringing at 7 in the morning sun.
    hook: (k, T) => {
      const d = px(k), {P} = d, n = k.data.numbers;
      const tEleven = W(/^eleven/i, k.S('hook.msg'), 2.2), tYou = W(/^You$/i, k.S('hook.seen'), 3.6);
      const cut1 = 0.8, cut2 = Math.min(2.6, Math.max(1.5, tEleven - 0.05)), cut3 = Math.max(cut2 + 0.6, tYou - 0.05);
      if (T < cut1) {
        bedroom(k, d, {night: true});
        clock(d, 140, 268, 14, n.nightHour.value, {night: true});
        flatPhone(k, d, 64, 268, true);
        hookPlate(k, d, n);
        return host(k);
      }
      if (T < cut2) {
        // the close up: the phone at night, the lead on its lock screen (example), the time it came in, an unread dot
        P(0, 0, 360, 640, '#151827'); for (let y = 160; y < 417; y += 8) for (let x = ((y >> 3) & 1) * 8; x < 360; x += 16) P(x, y, 2, 2, '#1E2238');
        const X = 50, Y = 166, Wd = 260, H = 150, pop = d.fr(cut1) < 4 ? [6, 3, 1, 0][d.fr(cut1)] : 0;
        P(X + 4, Y + 4, Wd, H, INK); P(X - 3, Y - 1, Wd + 6, H + 2, INK); P(X - 1, Y - 3, Wd + 2, H + 6, INK); P(X, Y, Wd, H, '#1B1420');
        // the card, then the reply bar and a dim keyboard under it
        const cy = Y + 6 - pop;
        P(X + 6, cy, Wd - 12, 76, PAPER); P(X + 6, cy, Wd - 12, 20, '#2F6F67');
        d.disc(X + 15, cy + 10, 3, GOLD);
        d.tx('New lead', X + 22, cy + 3, {color: CREAM});
        exampleTag(d, X + 28 + d.tw('New lead'), cy + 3);
        k.text(`${n.nightHour.shown} PM`, (X + Wd - 14) * 3, (cy + 3) * 3, {size: 39, color: GOLD, align: 'right'});
        bubbleBox(d, X + 12, cy + 26, Wd - 24, 44, CREAM, SAND);
        written(k, 1e9, MSG(n), 0, (X + 20) * 3, (cy + 32) * 3, (X + Wd - 18) * 3, {size: 39, lh: 46, color: PLUM});
        P(X + 6, Y + 88, Wd - 12, 14, '#2B2033'); P(X + 10, Y + 91, Wd - 44, 8, '#3D2E45'); d.disc(X + Wd - 18, Y + 95, 5, '#2F6F67');
        for (let r = 0; r < 3; r++) for (let c = 0; c < 10 - r; c++) P(X + 12 + r * 6 + c * 24, Y + 108 + r * 12, 20, 9, '#2B2033');
        hookPlate(k, d, n);
        k.burst((X + Wd - 30) * 3, (cy + 10) * 3, cut1 + 0.05, {n: 12, r: 160, colors: ['teal', 'paper']});
        return host(k);
      }
      if (T < cut3) {
        // the bedside clock at eleven: the cream face in the dark room, the time under it
        bedroom(k, d, {night: true});
        P(0, 156, 360, 176, '#151827'); for (let x = 6; x < 360; x += 18) P(x, 156, 2, 176, '#1B1F35');
        clock(d, 180, 236, 50, n.nightHour.value, {});
        clockTag(k, d, `${n.nightHour.shown} PM`, 180, 300, SKY);
        hookPlate(k, d, n);
        return host(k, 'shrug');
      }
      bedroom(k, d, {night: false});
      P(0, 156, 186, 126, '#E8C99A'); for (let x = 6; x < 186; x += 18) P(x, 156, 2, 126, '#EED6AE');
      clock(d, 100, 226, 42, n.morningHour.value, {ring: true});
      clockTag(k, d, `${n.morningHour.shown} AM`, 100, 300, GOLD);
      flatPhone(k, d, 128, 296, true);
      hookPlate(k, d, n);
      k.burst(100 * 3, 180 * 3, cut3 + 0.05, {n: 14, r: 200, colors: ['accent', 'paper']});
      return host(k, 'point');
    },

    // ---- play: the chat set. The message sits at the top (example); the reply is half typed in the box; three sticky notes
    // stack (rates, size, what's in); the bar's clock turns to LUNCH; "Still a draft." stamps; they booked elsewhere
    play: (k, T) => {
      const d = px(k), {P} = d, n = k.data.numbers, t0 = k.S('play');
      const tRates = W(/^Rates/i, k.S('play.rates')), tSize = W(/^size/i, tRates), tIn = W(/^included/i, tSize, tSize + 0.6);
      const tLunch = W(/^lunch/i, k.S('play.lunch')), tDraft = W(/^draft/i, tLunch, tLunch + 0.8), tBooked = W(/^booked/i, k.S('play.booked'));
      k.sets.chat({who: 'New lead', clock: T < tLunch ? `${n.morningHour.shown} AM` : 'LUNCH', msgs: [{me: false, text: MSG(n), at: -5}], notify: {text: 'Booked elsewhere.', at: tBooked, dur: 9}});
      // the EXAMPLE tag in the app's header, beside the name (the banner covers it when it drops)
      if (T < tBooked) exampleTag(d, 202, 105);
      // the reply, half typed in the composer, a cursor blinking
      const draft = 'Hi! So for a move-out we', m = T < t0 ? 0 : Math.min(draft.length, Math.floor((T - t0) / 0.07));
      const s = draft.slice(0, m);
      k.text(s, (102 + 5) * 3, 300 * 3, {size: 30, color: PLUM, lint: m === draft.length});
      if (((d.F >> 3) & 1) === 0) P(107 + d.tw(s, 30) + 1, 301, 1, 11, PLUM);
      // the sticky notes on the dash, left of the phone, inside the safe edge
      [['RATES', tRates, GOLD], ['SIZE', tSize, '#F2C2A0'], ["WHAT'S IN", tIn, '#BDE6F5']].forEach(([lbl, at, c], i) => {
        if (T < at) return;
        const yy = 196 + i * 30 - (d.fr(at) < 3 ? [4, 2, 1][d.fr(at)] : 0), xx = 21 + (i % 2);
        P(xx + 2, yy + 2, 66, 24, INK); P(xx, yy, 66, 24, c); P(xx, yy, 66, 3, '#FFFFFF');
        d.tx(lbl, xx + 5, yy + 6, {size: 30, color: INK});
      });
      if (T >= tDraft) k.slam('Still a draft.', 588, 696, tDraft, {size: 66, color: RED, align: 'center', stamp: true, drop: INK});
      return host(k, T >= tBooked ? 'shrug' : null);
    },

    // ---- fix: the AI chat app. Their message slides in from the phone; the prompt box waits with a cursor and types on as
    // said; the draft lands under it; the owner fills the rate, ticks it and presses send
    fix: (k, T) => {
      const d = px(k), {P} = d, n = k.data.numbers, t0 = k.S('fix');
      const tPaste = W(/^paste/i, t0, t0 + 0.4), tP1 = W(/^Write$/i, k.S('fix.p1')), tP2 = W(/^Use$/i, k.S('fix.p2')), tP3 = W(/^Ask$/i, k.S('fix.p3'));
      const tMiss = WE(/^missing/i, tP3, tP3 + 1.4), tRead = W(/^read$/i, k.S('fix.send')), tFix = W(/^fix$/i, tRead), tSend = W(/^send$/i, tFix);
      // the desk under the window
      P(0, 0, 360, 417, '#2B2033'); for (let y = 0; y < 417; y += 6) d.dith(0, y, 360, 1, '#3D2E45', (y / 6) & 1);
      P(0, 340, 360, 77, '#6B4226'); P(0, 340, 360, 2, '#B07A47');
      for (let y = 417; y < 640; y += 16) for (let x = 0, c = 0; x < 360; x += 16, c++) P(x, y, 16, 16, ((y >> 4) + c) % 2 ? '#5A3A22' : '#4A2E1B');
      const X = 20, Y = 84, Wd = 300, H = 252, op = d.ease(t0 + 0.05, 8, 40);
      appWindow(k, d, X, Y + op, Wd, H);
      if (op !== 0) return host(k);
      // their message, pasted as a grey block (it slides in from the left as "paste" comes)
      const tMsg = Math.min(tPaste - 0.3, t0 + 0.3);
      if (T >= tMsg) {
        const sl = d.ease(tMsg, 6, 24);
        bubbleBox(d, X + 8 - sl, Y + 25, Wd - 40, 50, '#E2DACB', '#C9BFAE');
        d.tx('THEIR MESSAGE', X + 14 - sl, Y + 27, {size: 30, color: MAROON});
        written(k, 1e9, MSG(n), 0, (X + 14 - sl) * 3, (Y + 42) * 3, (X + Wd - 46) * 3, {size: 30, lh: 45, color: PLUM, lint: sl === 0});
      }
      // the prompt box: up on "paste" with a blinking cursor, then typed on as said
      const bx = (X + 34) * 3, bmax = (X + Wd - 10) * 3, py = Y + 80;
      if (T >= tPaste) {
        const pop = d.fr(tPaste) < 3 ? [3, 1, 0][d.fr(tPaste)] : 0;
        bubbleBox(d, X + 30, py - pop, Wd - 38, 81, '#DCE9F7', '#A9C4E0');
        d.tx('YOUR PROMPT', X + 36, py + 2 - pop, {size: 30, color: BLUE});
        const rows = [
          {text: 'Write a short, friendly reply to this cleaning quote request.', at: tP1},
          {text: 'Use my rates below.', at: tP2},
          {text: "Ask one question if anything's missing.", at: tP3},
        ];
        let y = (py + 17) * 3;
        if (T < tP1 - 0.05) { if (((d.F >> 3) & 1) === 0) P(X + 38, py + 18, 2, 12, NAVY); }
        else rows.forEach((r, i) => {
          const ln = typed(k, T, r.text, r.at, bx + 12, y, bmax - 12, {size: 39, color: NAVY});
          if (i === 1 && T >= WE(/^below/i, tP2, tP2 + 1)) { const x0 = bx + 12 + k.measure(r.text + ' ', {size: 39}), cw = k.measure('[my rates]', {size: 30}); k.shape(k.rectPts(x0, y - 3, cw + 18, 45, 0), {fill: GOLD, line: false}); k.text('[my rates]', x0 + 9, y, {size: 30, color: INK}); }
          y += ln * 45;
        });
      }
      // the drafted reply (example), written out fast once the prompt is done
      const tDraft = tMiss + 0.15;
      if (T >= tDraft) {
        const dy = py + 86, pop = d.fr(tDraft) < 3 ? [3, 1, 0][d.fr(tDraft)] : 0;
        bubbleBox(d, X + 8, dy - pop, Wd - 16, 80, CREAM, SAND);
        d.tx('DRAFT', X + 14, dy + 2 - pop, {size: 30, color: TEAL});
        const reply = `Thanks for reaching out! A move-out clean for a ${n.beds.shown} bed, ${n.baths.shown} bath is [your rate]. Want the inside of the fridge and oven done too?`;
        written(k, T, reply, tDraft, (X + 14) * 3, (dy + 17 - pop) * 3, (X + Wd - 40) * 3, {size: 30, lh: 45, cps: 160, color: PLUM, lint: T >= tDraft + 1.2,
          colorOf: (w) => (/^\[your|^rate\]/.test(w) ? (T >= tFix ? '#2F6F67' : ORANGE) : null)});
        // the pen ticks it on "read"
        if (T >= tRead) { const nn = Math.min(14, d.fr(tRead) * 3); for (let i = 0; i < nn; i++) { const px2 = X + Wd - 58 + i, py2 = dy + 66 + (i < 5 ? i : 5 - (i - 5)); P(px2, py2, 2, 2, '#2F6F67'); } }
        // the send key: pressed on "send"
        const pressed = T >= tSend, sx = X + Wd - 34, sy = dy + 58, pd = pressed ? 2 : 0;
        P(sx + 2, sy + 2, 22, 18, INK); P(sx - 1, sy + pd, 22, 18, INK); P(sx, sy + 1 + pd, 20, 16, pressed ? '#2F6F67' : TEAL);
        d.line(sx + 5, sy + 9 + pd, sx + 14, sy + 9 + pd, CREAM); d.line(sx + 10, sy + 5 + pd, sx + 14, sy + 9 + pd, CREAM); d.line(sx + 10, sy + 13 + pd, sx + 14, sy + 9 + pd, CREAM);
        if (pressed) { k.burst((sx + 10) * 3, (sy + 10) * 3, tSend + 0.05, {n: 12, r: 140, colors: ['teal', 'paper']}); }
      }
      return host(k, k.live('fix.send') ? 'point' : null);
    },

    // ---- proof: the gauge. The source on the hood; the claim inside the dial; 26% as the hero under the hub; "Fastest
    // trade." on a pill in the opening at the bottom of the dial
    proof: (k, T) => {
      const d = px(k), {P} = d, n = k.data.numbers, t0 = k.S('proof');
      const t26 = W(/^twenty/i, k.S('proof.pct'), t0 + 1.4), tFast = W(/^fastest/i, k.S('proof.fast'));
      quiet(k, /^\d+%$/, () => k.sets.gauge({value: n.hourPct.value, max: 100, at: t26, dur: 1.0, zones: [[0, 40, RED], [40, 70, ORANGE], [70, 100, TEAL]], suffix: '%'}));
      k.text(`Jobber survey, ${n.owners.shown} owners, Dec ${n.surveyYear.shown}`, 540, 270, {size: 39, color: SAND, align: 'center'});
      k.slam('Cleaning businesses', 540, 456, t0 + 0.05, {size: 39, color: GOLD, align: 'center', from: 0.4, drop: INK});
      k.slam('reply within an hour', 540, 501, t0 + 0.25, {size: 39, color: CREAM, align: 'center', from: 0.4, drop: INK});
      // the hero readout, over the gauge's own box: it counts with the needle
      P(141, 226, 78, 46, INK); P(142, 227, 76, 44, '#1A332B'); P(143, 228, 74, 42, '#24453A');
      if (T >= t26) k.slam(cnt(k, n.hourPct, t26, {suffix: '%'}), 540, 681, t26, {size: 132, color: GOLD, align: 'center', from: 0.3, drop: INK});
      if (T >= tFast) {
        const pw = d.tw('Fastest trade.', 66) + 28, pop = d.fr(tFast) < 3 ? [2, 1, 0][d.fr(tFast)] : 0;
        P(180 - pw / 2 + 2, 276 + 2 - pop, pw, 28, INK); P(180 - pw / 2, 276 - pop, pw, 28, MAROON); P(180 - pw / 2, 276 - pop, pw, 2, RED);
        k.slam('Fastest trade.', 540, (279 - pop) * 3, tFast, {size: 66, color: GOLD, align: 'center', stamp: true, drop: INK});
      }
      k.burst(540, 760, t26 + 1.0, {n: 14, r: 180, colors: ['accent', 'paper']});
      return host(k, k.live('proof.pct') ? 'point' : null);
    },

    // ---- button: the departures board, today. Asleep at 11; the night quote sent; the first job up (landed well before the
    // end card); the rule on a plate under it
    button: (k, T) => {
      const d = px(k), n = k.data.numbers, t0 = k.S('button');
      const tNob = W(/^Nobody/i, t0, t0 + 0.1), tBut = W(/^But$/i, k.S('button.quote'), t0 + 2.2), tHave = W(/^have$/i, tBut, tBut + 1.0), tFirst = W(/^first/i, k.S('button.first')), tJob = WE(/^job/i, tFirst, tFirst + 0.6);
      k.sets.flaps({title: 'TODAY', cols: 12, rows: [
        {label: `${n.nightHour.shown} PM`, value: 'ASLEEP', at: tNob},
        {label: 'QUOTE', value: 'SENT', at: tBut, hi: true},
        {label: 'FIRST JOB', value: 'UP', at: tHave},
      ]});
      if (T >= tBut) d.win(30, 284, 300, 54, {base: DUSK, hi: '#3D2E45', lo: INK, rule: MAROON});
      if (T >= tBut) k.slam('Answer the night quote', 120, 870, tBut, {size: 66, color: CREAM, from: 0.4, drop: INK});
      if (T >= tFirst) k.slam('before your first job.', 120, 936, tFirst, {size: 66, color: GOLD, from: 0.4, drop: INK});
      if (T >= tJob) k.sweep(120, 1002, k.measure('before your first job.', {size: 66}), 3, tJob, {color: 'accent'});
      return host(k, T >= tJob ? 'wave' : null);
    },
  },
};
