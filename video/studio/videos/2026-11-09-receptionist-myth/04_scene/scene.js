// Scene: The AI receptionist myth (AI lead lane, lesson 2, Lead Clinic v2, arcade). One function per top-level cue in
// 03_cues/cues.md. Numbers only from k.data (brief.md -> data.js). Every beat lands on a spoken word (window.WORDS).
// The five beats: hook = the drop-in in three shots under one plate (a laptop on a desk playing a generic voice bot demo;
// the robot close up with its phones checked off; the poster and a MYTH? stamp); play = the calendar set, a coin for the
// bot, two weeks of answered calls, then red x's while the quotes sit; fix = our own outbox tray, the prompt typed on as
// said, the drafted check-in held under a padlock until the owner reads it and presses send; proof = the high-score
// cabinet, ServiceTitan's trust numbers (11 high or complete, 58 little or none); button = the myth as a boss, beaten by
// two moves (you hit send, follow-up first). No AI product is named or shown.
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
// the demo: our own set piece. An office desk, a laptop playing a generic sales demo (no product, no logo): a robot in a
// headset and a speech balloon full of ringing phones
const robot = (d, cx, cy, s, o = {}) => {
  // drawn at whole scale s around (cx, cy): a boxy head, antenna, visor eyes that blink, a headset with a mic
  const {P, disc, F} = d, R = (x, y, w, h, c) => P(cx + x * s, cy + y * s, w * s, h * s, c);
  R(-1, -16, 2, 4, GREY); R(-2, -18, 4, 2, (F >> 3) & 1 ? RED : GOLD);
  R(-11, -12, 22, 20, INK); R(-10, -11, 20, 18, '#C9CCD3'); R(-10, -11, 20, 2, CREAM); R(-10, 5, 20, 2, GREY);
  R(-8, -7, 16, 7, NAVY); const bl = ((F >> 2) % 24) === 0; R(-6, -5, 4, bl ? 1 : 3, SKY); R(2, -5, 4, bl ? 1 : 3, SKY);
  R(-4, 2, 8, 1, INK);
  // the headset band and the ear cups, the mic arm
  R(-12, -14, 24, 2, INK); R(-14, -8, 4, 8, INK); R(10, -8, 4, 8, INK); R(-13, -7, 2, 6, RED); R(11, -7, 2, 6, RED);
  R(-12, 0, 2, 4, INK); R(-12, 4, 8, 1, INK); R(-5, 3, 3, 3, GREY);
  // shoulders
  R(-14, 8, 28, 8, INK); R(-13, 9, 26, 7, BLUE); R(-13, 9, 26, 1, SKY);
};
const ringPhone = (d, x, y, at, T, s = 2) => {
  // a handset icon that rings (shakes a pixel) until `at`, then gets a green check
  const {P, F} = d, rung = T >= at, sh = !rung && ((F >> 1) & 1) ? 1 : 0, R = (xx, yy, w, h, c) => P(x + sh + xx * s, y + yy * s, w * s, h * s, c);
  R(0, 0, 12, 12, INK); R(1, 1, 10, 10, rung ? '#2F6F67' : MAROON);
  R(2, 3, 3, 6, CREAM); R(7, 3, 3, 6, CREAM); R(4, 3, 4, 2, CREAM);
  if (rung) { const n = Math.min(6, d.fr(at) * 2); const pts = [[8, 13], [9, 14], [10, 13], [11, 12], [12, 11], [13, 10]]; for (let i = 0; i < n; i++) R(pts[i][0], pts[i][1], 2, 2, '#6FDC8C'); }
  else if (((F >> 2) & 1) === 0) { R(-3, 2, 2, 1, GOLD); R(-3, 8, 2, 1, GOLD); R(13, 2, 2, 1, GOLD); R(13, 8, 2, 1, GOLD); }
};
const office = (d) => {
  const {P, DOT} = d;
  P(0, 0, 360, 330, '#2F3A55'); for (let x = 0; x < 360; x += 24) P(x, 0, 1, 330, '#283149');
  for (let i = 0; i < 6; i++) P(14 + i * 60, 120, 40, 2, '#3B4868');
  P(0, 300, 360, 8, '#8C5A33'); P(0, 300, 360, 2, '#D9A066'); P(0, 308, 360, 109, '#6B4226'); for (let y = 314; y < 417; y += 12) P(0, y, 360, 1, '#5A3A22');
  for (let y = 417; y < 640; y += 16) for (let x = 0, c = 0; x < 360; x += 16, c++) P(x, y, 16, 16, ((y >> 4) + c) % 2 ? '#253048' : '#1B2440');
  // a plant and a mug
  P(18, 270, 20, 30, MAROON); P(20, 272, 16, 3, '#B07A47'); d.disc(28, 258, 12, GREEN); d.disc(20, 262, 7, '#2F5A4A'); d.disc(36, 262, 7, '#2F5A4A');
  P(316, 282, 14, 18, CREAM); P(330, 286, 4, 8, CREAM); P(316, 282, 14, 2, '#FFFFFF');
};
const laptop = (k, d, T, o = {}) => {
  const {P} = d, X = 70, Y = 152, Wd = 220, H = 140;
  P(X - 6, Y - 6, Wd + 12, H + 12, INK); P(X - 4, Y - 4, Wd + 8, H + 8, '#4A4E5A'); P(X, Y, Wd, H, '#0E1430');
  P(X - 24, Y + H + 6, Wd + 48, 8, INK); P(X - 22, Y + H + 6, Wd + 44, 6, '#9AA0AD'); P(X + Wd / 2 - 20, Y + H + 6, 40, 2, '#6B7080');
  // the demo: a stage light, the robot, the balloon with three phones
  for (let i = 0; i < 4; i++) d.dith(X + 20 + i * 10, Y, 30 - i * 4, H, '#151C40', i & 1);
  robot(d, X + 60, Y + 84, 3);
  const bx = X + 116, by = Y + 22;
  P(bx - 1, by - 1, 94, 74, INK); P(bx, by, 92, 72, CREAM); P(bx - 8, by + 50, 10, 6, CREAM); P(bx - 10, by + 54, 4, 4, CREAM);
  [[bx + 6, by + 8], [bx + 34, by + 8], [bx + 62, by + 8]].forEach(([x, y], i) => ringPhone(d, x, y, o.checks ? o.checks[i] : 1e9, T, 2));
  d.tx('EVERY CALL', bx + 46, by + 42, {align: 'center', color: PLUM}); d.tx('ANSWERED', bx + 46, by + 56, {align: 'center', color: '#2F6F67'});
  // the live dot, top left
  if (((d.F >> 4) & 1) === 0) d.disc(X + 10, Y + 10, 3, RED);
};
const hookPlate = (k, d) => {
  d.win(14, 86, 332, 62, {base: DUSK, hi: '#3D2E45', lo: INK, rule: MAROON});
  k.text('The demo: an AI receptionist', 540, 276, {size: 39, color: GOLD, align: 'center'});
  k.slam('answers every call.', 540, 336, -1, {size: 66, color: CREAM, align: 'center', drop: INK});
};
// the outbox tray: our own set piece. A pin board wall, a desk, an index card with the prompt, a wire tray with the
// drafted check-in held under a padlock, and the big green send key
const lockIcon = (d, x, y, open) => { const {P} = d; if (open) { P(x + 6, y - 7, 2, 7, GREY); P(x + 6, y - 9, 10, 2, GREY); P(x + 14, y - 9, 2, 3, GREY); } else { P(x + 2, y - 8, 2, 8, GREY); P(x + 2, y - 10, 10, 2, GREY); P(x + 10, y - 8, 2, 8, GREY); } P(x - 1, y - 1, 16, 13, INK); P(x, y, 14, 11, GOLD); P(x, y, 14, 2, '#FFE39A'); P(x + 6, y + 4, 2, 4, INK); };
const eye = (d, x, y, open) => { const {P} = d; P(x, y + 3, 18, 6, INK); if (open) { P(x + 1, y + 4, 16, 4, CREAM); P(x + 7, y + 3, 5, 6, NAVY); P(x + 8, y + 4, 2, 2, CREAM); } else P(x + 1, y + 6, 16, 1, CREAM); };

const quiet = (k, fn) => { const t = k.text; k.text = function (s, ...a) { return /^-\d+$/.test(String(s)) ? {w: 0, h: 0, lines: []} : t.call(this, s, ...a); }; try { return fn(); } finally { k.text = t; } };

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'AI LESSON 2',
  sendLine: 'Send this to whoever handles your follow-ups.',
  transitions: {play: 'levelselect', fix: 'dissolve', proof: 'levelselect', button: 'gameover'},
  trauma: {'hook.myth': 0.5},
  sections: {
    // ---- hook: three shots under one plate. Cover: the laptop on the desk playing the demo. Cut by 0.8 s to the robot
    // close up, its phones getting checks on "answers". Cut on "call" to the poster and the MYTH? stamp.
    hook: (k, T) => {
      const d = px(k), {P} = d;
      const tAns = W(/^answer/i, k.S('hook.bot'), 1.6), tCall = W(/^call$/i, k.S('hook.myth'), 2.3);
      const cut1 = 0.8, cut2 = Math.min(2.6, Math.max(1.6, tCall - 0.05));
      if (T < cut1) {
        office(d); laptop(k, d, T);
        hookPlate(k, d);
        return host(k);
      }
      if (T < cut2) {
        P(0, 0, 360, 640, '#0E1430'); for (let y = 150; y < 417; y += 8) for (let x = ((y >> 3) & 1) * 8; x < 360; x += 16) P(x, y, 2, 2, '#151C40');
        for (let i = 0; i < 6; i++) d.dith(110 + i * 14, 150, 30 - i * 3, 267, '#1B2450', i & 1);
        const pop = d.fr(cut1) < 4 ? [6, 3, 1, 0][d.fr(cut1)] : 0;
        robot(d, 180, 262 - pop, 6);
        [[44, 176], [268, 176], [268, 268]].forEach(([x, y], i) => ringPhone(d, x, y, tAns + i * 0.2, T, 3));
        hookPlate(k, d);
        return host(k);
      }
      // the poster and the stamp
      P(0, 0, 360, 640, '#2F3A55'); for (let x = 0; x < 360; x += 24) P(x, 0, 1, 417, '#283149');
      const X = 70, Y = 160, Wd = 220, H = 170;
      P(X + 4, Y + 4, Wd, H, INK); P(X - 1, Y - 1, Wd + 2, H + 2, INK); P(X, Y, Wd, H, CREAM); P(X, Y, Wd, 26, BLUE);
      d.tx('AI RECEPTIONIST', X + 10, Y + 6, {color: CREAM});
      robot(d, X + 50, Y + 92, 3);
      [[X + 104, Y + 44], [X + 140, Y + 44], [X + 176, Y + 44]].forEach(([x, y]) => ringPhone(d, x, y, 0, T, 2));
      P(0, 330, 360, 87, '#6B4226'); P(0, 330, 360, 2, '#B07A47');
      k.stampIn(cut2 + 0.05, () => {
        const sx = 150, sy = 230; d.P(sx - 4, sy - 4, 132, 58, RED); d.P(sx, sy, 124, 50, '#F7EDE0'); d.P(sx + 3, sy + 3, 118, 44, RED); d.P(sx + 6, sy + 6, 112, 38, '#F7EDE0');
        k.text('MYTH?', (sx + 62) * 3, (sy + 10) * 3, {size: 66, color: RED, align: 'center'});
      }, {at: [212 * 3, 280 * 3], freeze: 5});
      hookPlate(k, d);
      return host(k, 'shrug');
    },

    // ---- play: the calendar set. A coin on day 1 for the bot; checks run through the first two weeks (calls answered);
    // then red x's through the rest (the quotes sit, nobody follows up)
    play: (k, T) => {
      const d = px(k), t0 = k.S('play');
      const tPay = W(/^pay$/i, t0, t0 + 0.4), tAns = W(/^answered/i, k.S('play.answer')), tQuotes = W(/^quotes/i, k.S('play.sit')), tSit = W(/^sit$/i, tQuotes, tQuotes + 1.2), tFol = W(/^follows/i, tSit, tSit + 1.2);
      const c = k.sets.calendar({month: 'THIS MONTH', start: 0, days: 30,
        fills: [{day: 1, at: tPay, c: GOLD, mark: 'coin'}].concat(Array.from({length: 16}, (_, i) => ({day: 15 + i, at: tSit + i * 0.07, c: '#F2C2A0', mark: 'x'}))),
        run: {from: 2, to: 14, at: tAns, every: 0.06, c: '#BDE6CF', mark: 'check'}});
      if (T >= tAns) { d.P(22, 277, 316, 26, INK); d.P(22, 277, 316, 1, '#3D2E45'); }
      if (T >= tAns && T < tQuotes) k.slam('Calls: answered.', 120, 834, tAns, {size: 66, color: CREAM, from: 0.4});
      if (T >= tQuotes) {
        k.slam('Quotes:', 120, 834, tQuotes, {size: 66, color: CREAM, from: 0.4});
        const qx = 120 + k.measure('Quotes: ', {size: 66});
        if (T < tFol) k.slam('just sitting.', qx, 834, tQuotes, {size: 66, color: CREAM, from: 0.4});
        else k.slam('no follow-up.', qx, 834, tFol, {size: 66, color: ORANGE, from: 0.4});
      }
      return host(k, T >= tFol ? 'shrug' : null);
    },

    // ---- fix: the outbox tray. The prompt types on as said; the draft drops in under a padlock; an eye on "read"; the
    // send key on "send" opens the lock and the envelope flies out
    fix: (k, T) => {
      const d = px(k), {P} = d, t0 = k.S('fix');
      const tP1 = W(/^Write$/i, k.S('fix.p1')), tP2 = W(/^Ask$/i, k.S('fix.p2')), tHave = WE(/^have/i, tP2, tP2 + 1.2);
      const tRead = W(/^read$/i, k.S('fix.send')), tSend = W(/^send/i, tRead, tRead + 0.8);
      // the wall (a cork board) and the desk
      P(0, 0, 360, 330, '#B07A47'); for (let i = 0; i < 260; i++) d.DOT(Math.floor(hash(i * 1.7) * 360), Math.floor(hash(i * 3.9) * 330), i % 2 ? '#8C5A33' : '#C98B5B');
      P(0, 330, 360, 87, '#4A2E1B'); P(0, 330, 360, 2, '#8C5A33');
      for (let y = 417; y < 640; y += 16) for (let x = 0, c = 0; x < 360; x += 16, c++) P(x, y, 16, 16, ((y >> 4) + c) % 2 ? '#3D2E45' : '#2B2033');
      d.win(14, 86, 332, 40, {base: DUSK, hi: '#3D2E45', lo: INK, rule: MAROON});
      k.slam('Fix follow-up first.', 540, 276, t0 + 0.05, {size: 66, color: GOLD, align: 'center', from: 0.5, drop: INK});
      // the prompt card, pinned
      const cx = 18, cy = 134, cw = 324, ch = 60;
      P(cx + 3, cy + 3, cw, ch, '#5A3A22'); P(cx - 1, cy - 1, cw + 2, ch + 2, INK); P(cx, cy, cw, ch, CREAM); P(cx, cy, cw, 16, '#2B2033');
      d.disc(cx + cw / 2, cy + 2, 3, RED);
      d.tx('ASK AN AI CHAT APP', cx + 6, cy + 2, {size: 30, color: CREAM});
      const tg = 'EXAMPLE', tgw = d.tw(tg, 30), tgx = cx + 14 + d.tw('ASK AN AI CHAT APP', 30); P(tgx, cy + 1, tgw + 8, 15, GOLD); d.tx(tg, tgx + 4, cy + 2, {size: 30, color: INK});
      let y = (cy + 21) * 3;
      [{text: 'Write a short check-in on this quote, in my voice.', at: tP1}, {text: 'Ask what questions they have.', at: tP2}].forEach((r) => {
        const ln = typed(k, T, r.text, r.at, (cx + 8) * 3, y, (cx + cw - 8) * 3, {size: 39, color: NAVY}); y += ln * 45;
      });
      // on "Paste": the quote you sent clips onto the card (example), and the padlock drops into the empty tray
      const tPaste = W(/^Paste/i, t0, t0 + 2.2);
      if (T >= tPaste) {
        const pop = d.fr(tPaste) < 4 ? [6, 3, 1, 0][d.fr(tPaste)] : 0, ax = 24, ay = 198 - pop;
        P(ax + 2, ay + 2, 176, 18, '#5A3A22'); P(ax - 1, ay - 1, 178, 20, INK); P(ax, ay, 176, 18, '#DCE9F7'); P(ax, ay, 4, 18, BLUE);
        P(ax + 8, ay + 3, 3, 11, GREY); P(ax + 8, ay + 3, 7, 2, GREY); P(ax + 13, ay + 3, 2, 9, GREY);
        d.tx('Pasted: deep clean quote', ax + 20, ay + 3, {color: NAVY});
      }
      // the wire tray and the held draft
      const tx0 = 18, ty = 220, tw0 = 236;
      P(tx0, ty + 78, tw0, 6, GREY); P(tx0, ty + 78, tw0, 1, CREAM); P(tx0, ty + 30, 4, 54, GREY); P(tx0 + tw0 - 4, ty + 30, 4, 54, GREY);
      for (let x = tx0 + 12; x < tx0 + tw0 - 6; x += 16) P(x, ty + 48, 2, 30, '#6B7080');
      const hw = d.tw('HELD FOR YOU') + 12; P(tx0 + 1, ty + 87, hw, 17, INK); P(tx0, ty + 86, hw, 17, MAROON); d.tx('HELD FOR YOU', tx0 + 6, ty + 88, {color: GOLD});
      const tDrop = tHave + 0.1, sent = T >= tSend, fly = sent ? Math.floor(Math.pow(Math.max(0, T - tSend - 0.25) * 9, 2)) : 0;
      if (T >= tPaste && T < tDrop) { const f = d.fr(tPaste), dy = f < 6 ? [-30, -16, -6, 2, 1, 0][f] : 0; lockIcon(d, tx0 + tw0 / 2 - 7, ty + 52 + dy, false); }
      if (T >= tDrop && tx0 + 8 + fly < 360) {
        const dy = d.fr(tDrop) < 5 ? [-24, -12, -4, 1, 0][d.fr(tDrop)] : 0, ex = tx0 + 8 + fly, ey = ty + 10 + dy;
        P(ex + 2, ey + 2, 220, 66, '#5A3A22'); P(ex - 1, ey - 1, 222, 68, INK); P(ex, ey, 220, 66, '#F7F1E6');
        d.line(ex, ey, ex + 110, ey + 18, '#E6D3BC'); d.line(ex + 219, ey, ex + 110, ey + 18, '#E6D3BC');
        d.tx('DRAFT', ex + 6, ey + 4, {size: 30, color: TEAL});
        { const tg = 'EXAMPLE', tgw = d.tw(tg, 30), tgx = ex + 14 + d.tw('DRAFT', 30); P(tgx, ey + 3, tgw + 8, 15, GOLD); d.tx(tg, tgx + 4, ey + 4, {size: 30, color: INK}); }
        written(k, 1e9, 'Hi, just checking in on the quote I sent for your deep clean. Any questions I can answer?', 0, (ex + 6) * 3, (ey + 17) * 3, (ex + 214) * 3, {size: 30, lh: 45, color: PLUM, lint: fly === 0});
        lockIcon(d, ex + 202, ey + 1, sent);
      }
      if (T >= tRead && T < tSend + 0.3) eye(d, 226, 210, ((d.F >> 3) % 6) !== 0);
      // the send key
      const kx = 262, ky = 256, pr = sent && T < tSend + 0.25 ? 3 : (sent ? 1 : 0);
      P(kx + 3, ky + 3, 60, 48, INK); P(kx - 1, ky + pr - 1, 60, 48, INK); P(kx, ky + pr, 58, 46, sent ? '#2F6F67' : '#3E9A6E'); P(kx, ky + pr, 58, 3, '#6FDC8C');
      d.tx('SEND', kx + 29, ky + pr + 16, {color: CREAM, align: 'center'});
      if (sent) k.burst((kx + 29) * 3, (ky + 20) * 3, tSend + 0.05, {n: 14, r: 160, colors: ['teal', 'paper']});
      return host(k, k.live('fix.send') ? 'point' : null);
    },

    // ---- proof: the high-score cabinet. ServiceTitan, 1,000+ contractors: high or complete trust 11%; little or none 58%
    proof: (k, T) => {
      const n = k.data.numbers, t0 = k.S('proof');
      const t11 = W(/^eleven/i, k.S('proof.low'), t0 + 2), t58 = W(/^Fifty/i, k.S('proof.none'), t11 + 1.6);
      k.sets.scores({title: 'TRUST IN AI TOOLS', t0: t11, gap: Math.max(0.3, t58 - t11), count: 0.7, rows: [
        {rank: 'TOP', name: 'HIGH OR COMPLETE', value: n.highTrust.value, suffix: '%', hi: true},
        {rank: 'LOW', name: 'LITTLE OR NONE', value: n.lowTrust.value, suffix: '%'},
      ]});
      // one hero slot under the rows: the sample counts up to its size on "thousand", then each share lands as it is said
      const tSur = W(/^surveyed/i, t0, t0 + 0.7), tTh = W(/^thousand/i, tSur, tSur + 1.2);
      if (T >= tSur && T < t11) {
        const p = clamp((T - tSur) / Math.max(0.3, tTh - tSur));
        k.text(k.count(n.contractors.value, p, {from: Math.round(n.contractors.value * 0.85), comma: true, suffix: p >= 1 ? '+' : ''}), 120, 588, {size: 198, color: CREAM, drop: INK, lint: p >= 1});
        k.text('residential service', 120, 792, {size: 66, color: SAND}); k.text('contractors surveyed', 120, 858, {size: 66, color: SAND});
      } else if (T >= t11 && T < t58) {
        k.slam(n.highTrust.shown, 120, 588, t11, {size: 198, color: GOLD, from: 0.3, drop: INK});
        k.text('high or complete trust', 120, 792, {size: 66, color: GOLD});
      } else if (T >= t58) {
        k.slam(n.lowTrust.shown, 120, 588, t58, {size: 198, color: RED, from: 0.3, drop: INK});
        k.text('little or no trust', 120, 792, {size: 66, color: RED});
        k.burst(260, 680, t58 + 0.05, {n: 14, r: 200, colors: ['accent', 'paper']});
      }
      // the sample's scope stays on screen the whole beat (facts): two lines, inside x 930
      k.text(`ServiceTitan survey, ${n.reportYear.shown}`, 120, 936, {size: 39, color: SAND});
      k.text(`${n.contractors.shown}+ residential service contractors`, 120, 978, {size: 39, color: SAND});
      return host(k, k.live('proof.low') || k.live('proof.none') ? 'point' : null);
    },

    // ---- button: the boss arena. THE MYTH; the moves: you hit send (on "hand"), follow-up first (on "buy"); busted on "fix"
    button: (k, T) => {
      const t0 = k.S('button');
      const tHand = W(/^hand$/i, t0, t0 + 0.8), tBuy = W(/^buy$/i, k.S('button.fix')), tRec = W(/^receptionist/i, tBuy, tBuy + 0.6), tBefore = W(/^before$/i, tRec, tRec + 0.8);
      const tFix = tRec + 0.3, tEnd = tBefore + 0.3;
      quiet(k, () => k.sets.boss({name: 'THE MYTH', hp: 100, t0, menu: 'MOVES', hits: [{at: tHand, dmg: 50, label: 'You hit send'}, {at: tBuy, dmg: 50, label: 'Follow-up first'}], defeatAt: tFix, winText: 'BUSTED!'}));
      if (T >= tEnd) k.slam('Follow-up first.', 540, 690, tEnd, {size: 132, color: GOLD, align: 'center', from: 0.5, drop: INK});
      return host(k, T >= tFix ? 'wave' : (k.live('button') ? 'point' : null));
    },
  },
};
