/* Scene: Three missed-call fixes, priced (quick-math, core lane; Nov 1, 2026). One function per top-level cue in       */
/* 03_cues/cues.md. Numbers only from k.data (brief.md -> data.js); every time from a cue start (k.S) or a spoken word. */
/* Page shots: video/studio/demos/out/2026-11-15-three-fixes-1/ (Quo, PATLive, Rosie pricing pages, Nov 1, 2026).      */
/* Worlds: hook = our supply-house counter (counter set) and a missed-call phone; guess = the AI tag up close; person,  */
/* ai, text = the pricing pages in a phone frame on our own blueprint desk; card = the ITEM SHOP save card. None used   */
/* by ai-night-quote (bedroom, flaps, work order, gauge, Gemini pages, versus).                                         */
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
  const coin = (x, y, f) => {
    const ws = [4, 3, 1, 3][((f % 4) + 4) % 4];
    for (let j = 0; j < 8; j++) { const dy = j - 3.5, hw = Math.max(0, Math.round(ws * Math.sqrt(Math.max(0, 1 - (dy * dy) / 16)))); if (!hw) continue; P(x + 4 - hw, y + j, 2 * hw, 1, '#B07A47'); if (hw > 1) P(x + 4 - hw + 1, y + j, 2 * hw - 2, 1, j < 4 ? GOLD : ORANGE); }
    if (ws >= 3) { P(x + 4, y + 2, 1, 4, '#B07A47'); DOT(x + 3, y + 2, CREAM); }
  };
  return {P, DOT, dith, disc, line, win, fr, ease, tx, tw, clip, twinkle, coin, F, T};
};

/* ---- the words: every beat lands on a spoken word ---- */
const WS = () => (window.WORDS && window.WORDS.words) || [];
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
const bob2 = (T, t0) => (T - t0 < 0.3 ? 0 : [0, 6, 0, -6][Math.floor((T - t0 - 0.3) / 0.15) % 4]);
const host = (k, pose) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150});
const plate = (d, x, y, w, h) => d.win(x, y, w, h, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
/* a rubber stamp in a dark box with a coloured rim, landed with the kit's hit-stop */
const stampBox = (k, s, cx, y, t0, o = {}) => {
  const size = o.size || 66, c = o.color || GOLD, w = Math.round((k.measure(s, {size}) + 54) / 6) * 6, h = size + 36, x = Math.round((cx - w / 2) / 3) * 3;
  k.stampIn(t0, () => {
    k.shape(k.rectPts(x + 6, y + 6, w, h, 0), {fill: INK, line: false}); k.shape(k.rectPts(x, y, w, h, 0), {fill: '#1B1420', line: false});
    k.shape(k.rectPts(x + 6, y + 6, w - 12, 6, 0), {fill: c, line: false}); k.shape(k.rectPts(x + 6, y + h - 12, w - 12, 6, 0), {fill: c, line: false});
    k.shape(k.rectPts(x + 6, y + 6, 6, h - 12, 0), {fill: c, line: false}); k.shape(k.rectPts(x + w - 12, y + 6, 6, h - 12, 0), {fill: c, line: false});
    k.text(s, x + w / 2, y + 18, {size, color: c, align: 'center'});
  }, {at: [x + w / 2, y + h], freeze: o.freeze});
};

const mute = (k, drop, fn) => { const real = k.text; k.text = function (s, x, y, o) { if (drop(s, x, y, o)) return; return real.call(this, s, x, y, o); }; try { return fn(); } finally { k.text = real; } };
const chipText = (k, s, x, y, o) => { const w = k.measure(String(s), {size: o.size}), x0 = o.align === 'right' ? x - w : o.align === 'center' ? x - w / 2 : x; k.ctx.fillStyle = INK; k.ctx.fillRect(Math.floor(x0 - 15), y - 9, Math.ceil(w + 30), Math.round(o.size * 1.2)); k.text(s, x, y, o); };
const bigPhone = (k, d, x, y, w, h, o = {}) => {
  const {P} = d;
  if (o.glow) { k.ctx.save(); k.ctx.globalAlpha = 0.18; P(x - 10, y - 10, w + 20, h + 20, '#87CEEB'); k.ctx.restore(); }
  P(x + 3, y + 3, w, h, INK); P(x - 1, y, w + 2, h, INK); P(x, y - 1, w, h + 2, INK);
  P(x, y, w, h, '#2B2033'); P(x + 1, y, w - 2, 1, '#4A4E5A');
  P(x + 4, y + 8, w - 8, h - 16, o.screen || '#F4E6D3'); P(x + Math.round(w / 2) - 6, y + 3, 12, 2, INK);
  return {x: x + 4, y: y + 8, w: w - 8, h: h - 16};
};
/* a tag on a dark chip (sources, addresses, EXAMPLE) */
const tag = (k, s, x, y, o = {}) => chipText(k, s, x, y, Object.assign({size: 39, color: SAND}, o));

/* ---- this lesson's pieces (safe area: x 7 to 316, y 88 to 416 in low-res units; centre line x 162) ---- */
const CX = 486;   /* the safe area's centre in frame units */
const EXTEXT = "Sorry I missed you, I'm on a job. I'll call you back inside the hour. What do you need?";
const glyphs = (l) => l.replace(/’/g, "'");
/* a price tag (low-res units): cream card, a punched hole and string, the name small, the price big; sway in px */
const priceTag = (k, d, x, y, w, name, price, o = {}) => {
  const {P} = d, h = 60, sw = o.sway || 0, lit = o.lit;
  d.line(x + w / 2, y - 12, x + w / 2 + sw, y, '#E6D3BC');
  const X = x + sw;
  if (lit) { k.ctx.save(); k.ctx.globalAlpha = 0.35; P(X - 5, y - 5, w + 10, h + 10, GOLD); k.ctx.restore(); }
  P(X + 3, y + 3, w, h, INK); P(X - 1, y, w + 2, h, INK); P(X, y - 1, w, h + 2, INK);
  P(X, y, w, h, lit ? '#FFF2B8' : CREAM); P(X, y, w, 1, '#FFFFFF'); P(X, y + h - 2, w, 2, SAND);
  d.disc(X + w / 2, y + 6, 2, INK);
  k.text(name, (X + w / 2) * 3, (y + 12) * 3, {size: 39, color: '#7A3442', align: 'center'});
  k.text(price, (X + w / 2) * 3, (y + 27) * 3, {size: 99, color: INK, align: 'center'});
};
/* M4 travel: blinds open over 12 frames (whole-pixel strips), so a room change is never a plain cut */
const blinds = (k, t0) => { const f = Math.floor((k.T - t0) * 30 + 0.005); if (f < 0 || f >= 12) return; const d = px(k); for (let x = 0; x < 360; x += 24) d.P(x, 0, Math.round(24 * (1 - f / 12)), 417, INK); };
const swayAt = (T, t0) => (T < t0 || T > t0 + 0.8 ? 0 : [2, 1, 0, -1, -2, -1, 0, 1][Math.floor((T - t0) * 10) % 8]);
/* our blueprint desk: navy with a grid and drafting marks that drift, the room every page shot sits in */
const desk = (k) => {
  const d = px(k), {P, F} = d;
  P(0, 0, 360, 417, '#1E3350'); for (let y = 0; y < 417; y += 12) P(0, y, 360, 1, '#253F62'); for (let x = 0; x < 360; x += 12) P(x, 0, 1, 417, '#253F62');
  for (let i = 0; i < 6; i++) { const x = (Math.floor(F / 3) * (i + 1) + i * 67) % 380 - 10; P(x, 60 + i * 52, 6, 1, '#3B82C4'); }
  P(0, 417, 360, 223, '#1B1420'); P(0, 417, 360, 2, '#3D2E45');
  return d;
};
/* the page shot in a phone frame (left) with its address under it */
const pagePhone = (k, d, name, addr, scroll, t0) => {
  const sl = d.ease(t0, 6, -40);
  const s = bigPhone(k, d, 10 + sl, 96, 132, 196, {screen: '#FFFFFF'});
  k.page(s.x * 3, s.y * 3, s.w * 3, s.h * 3, name, {scroll});
  tag(k, addr, (12 + sl) * 3, 298 * 3, {color: SAND});
  return s;
};
/* the right-hand column (x 150 to 314): each line slides in on its own word */
const RX = 152;
const priceLines = (k, d, lines) => {
  lines.forEach((l) => {
    if (k.T < l.at - 0.25) return;
    const sl = d.ease(l.at - 0.25, 5, 24);
    k.text(l.s, (RX + sl) * 3, l.y * 3, {size: l.size || 66, color: l.c || CREAM, drop: INK});
  });
};
/* the save card: an RPG ITEM SHOP menu. Rows for the three fixes, a COPY THIS TEXT box with our example words, the */
/* cursor on TEXT blinking twice a second, a gold underline running along one line of the text at a time (M1).    */
const shopCard = (k, t0, o = {}) => {
  const d = px(k), {P} = d, T = k.T, n = k.data.numbers;
  const f = Math.floor((T - t0) * 30 + 0.005), Y = 94 + (f < 0 ? -40 : [-40, -26, -12, 0, 6, 4, 0, -2, 0][Math.min(8, f)]);   /* drops in, overshoots 6 px, settles (M4) */
  d.win(8, Y, 306, 236, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3B82C4'});
  const tab = 'ITEM SHOP: CALL FIXES', tw2 = d.tw(tab) + 14;
  P(18, Y - 7, tw2 + 2, 14, INK); P(19, Y - 6, tw2, 12, '#7A3442'); k.text(tab, 26 * 3, (Y - 5) * 3, {size: 39, color: CREAM});
  const rows = [['TEXT', `${n.text.shown}/mo`, TEAL], ['PERSON', `${n.person.shown}+${n.permin.shown}/min`, ORANGE], ['AI', `${n.ai.shown}, ${n.aimin.shown} min`, '#C9A7F0']];
  rows.forEach(([nm, pr, c], i) => {
    const y = Y + 12 + i * 24, tin = t0 + 0.1 + i * 0.12; if (T < tin) return;
    const sl = d.ease(tin, 5, 30);
    if (i === 0 && o.best != null && T >= o.best) P(14, y - 2, 296, 24, '#2F4A3A');
    k.text(nm, (34 + sl) * 3, y * 3, {size: 66, color: c});
    k.text(pr, (306 + sl) * 3, y * 3, {size: 66, color: CREAM, align: 'right'});
  });
  if (Math.floor(T * 2) % 2 === 0) { const cy = Y + 16; P(18, cy, 4, 12, GOLD); P(22, cy + 2, 2, 8, GOLD); P(24, cy + 4, 2, 4, GOLD); }
  const by = Y + 94, bh = 98;
  P(14, by, 296, bh, '#0E1F2A'); P(14, by, 3, bh, TEAL);
  const ct = 'COPY THESE WORDS', cw = d.tw(ct) + 12;
  P(22, by - 8, cw + 2, 17, INK); P(23, by - 7, cw, 15, GOLD); k.text(ct, 29 * 3, (by - 5) * 3, {size: 39, color: INK});
  tag(k, 'EXAMPLE', 906, (by - 4) * 3, {align: 'right', color: ORANGE});
  const ls = k.wrap(EXTEXT, {size: 66}, 840), li = Math.max(0, Math.floor((T - t0 - 0.6) / 1.2)) % ls.length;
  ls.forEach((l, i) => { const y = by + 10 + i * 22; if (T > t0 + 0.6 && i === li) { const lw = k.measure(glyphs(l), {size: 66}) / 3, sp = clamp(((T - t0 - 0.6) % 1.2) / 0.8); P(24, y + 20, Math.round(lw * sp), 2, GOLD); } k.text(glyphs(l), 24 * 3, y * 3, {size: 66, color: CREAM}); });
  return {Y, by, bh};
};

window.SCENE = {
  look: 'arcade',
  images: ['quo', 'patlive', 'rosie'],
  host_name: 'Snow',
  hud: 'CALL FIXES',
  sendLine: "Send this to whoever answers your phone when you can't.",
  transitions: {guess: 'dissolve', person: 'levelselect', ai: 'dissolve', text: 'dissolve'},
  trauma: {'button.win': 0.5},
  sections: {
    /* ---- hook: three shots. Cover (frame 0, no host): the counter (the metaphor), three tags, the plate $2,800 a  */
    /* month (EXAMPLE). By 0.8 s blinds open on the dash phone: missed-call rows drop in, $2,800 slams in (EXAMPLE).   */
    /* On "month" back to the counter with Snow; on "Which" the plate turns to the question and the tags swing.      */
    hook: (k, T) => {
      const n = k.data.numbers, tIn = 0.75, tBack = Math.min(2.6, Math.max(1.9, wordT(k, 'hook', /^month/i, 2.4) - 0.15)), tQ = k.S('hook.q');
      if (T >= tIn && T < tBack) {
        const c = k.sets.chat({who: 'CUSTOMER', clock: '9:12', msgs: [], notify: {text: 'Call not answered', at: tIn + 0.05, dur: 1.6}});
        const d = px(k), {P} = d;
        [['9:12 AM', 0], ['11:40 AM', 1], ['2:05 PM', 2]].forEach(([tm, i]) => { const ti = tIn + 0.15 + i * 0.25; if (T < ti) return; const sl = d.ease(ti, 4, -16), y = 140 + i * 26 + sl;
          P(106, y, 180, 22, '#F9D7CC'); P(106, y, 180, 1, '#FFFFFF'); P(110, y + 5, 12, 12, RED); P(113, y + 8, 6, 6, '#FFF7EA');
          k.text('No answer', 128 * 3, (y + 4) * 3, {size: 39, color: INK}); k.text(tm, 282 * 3, (y + 4) * 3, {size: 39, color: '#7A3442', align: 'right'}); });
        const tChip = tIn + 0.4;
        if (T >= tChip - 0.25) { k.slam(`${n.month.shown}`, 588, 222 * 3, tChip - 0.25, {size: 132, color: GOLD, align: 'center', from: 0.5, drop: INK, glint: false});
          tag(k, 'A MONTH LOST, EXAMPLE SHOP', 588, 268 * 3, {align: 'center', color: ORANGE}); }
        blinds(k, tIn);
        return {host: false, speech: false};
      }
      k.sets.counter({shop: 'CALL FIXES', item: 'box', tags: []});
      const d = px(k);
      if (T >= tBack) { /* blinds after the tags and plate draw, below */ }
      const sw = swayAt(T, tQ - 0.2);
      [['TEXT', n.text.shown, 10], ['PERSON', n.person.shown, 112], ['AI', n.ai.shown, 214]].forEach(([nm, pr, x], i) => priceTag(k, d, x, 254, 92, nm, pr, {sway: i % 2 ? -sw : sw}));
      plate(d, 8, 134, 308, 84);
      if (T < tQ - 0.25) {
        k.text(`${n.month.shown} a month.`, CX, 150 * 3, {size: 99, color: GOLD, align: 'center', drop: INK});
        tag(k, 'MISSED CALLS, EXAMPLE SHOP', CX, 190 * 3, {align: 'center', color: ORANGE});
      } else {
        k.slam('Which fix is worth it?', CX, 152 * 3, tQ - 0.25, {size: 66, color: CREAM, align: 'center', from: 0.4, drop: INK, glint: false});
        tag(k, `${n.month.shown} A MONTH, EXAMPLE`, CX, 190 * 3, {align: 'center', color: ORANGE});
      }
      blinds(k, tBack);
      if (T < tBack) return {host: false, speech: false};
      return host(k, T >= tQ ? 'point' : null);
    },

    /* ---- guess: the arcade high-score table, YOUR PICK: TEXT $19, PERSON $49, AI $49; the AI row lights as the pick   */
    /* on "AI"; IT BOOKS? flashes as the new record on "books" (a game moment).                                        */
    guess: (k, T) => {
      const n = k.data.numbers, t0 = k.S('guess'), tA = wordT(k, 'guess', /^AI/i, 0.8), tB = wordT(k, 'guess', /^books/i, 1.4);
      mute(k, (x) => String(x) === 'SCORE', () => k.sets.scores({title: 'YOUR PICK', t0: t0 - 0.3, gap: 0.2, count: 0.5, rows: [{name: 'TEXT', value: n.text.value, prefix: '$', suffix: '/mo', rank: '?'}, {name: 'PERSON', value: n.person.value, prefix: '$', suffix: '/mo', rank: '?'}, {name: 'AI', value: n.ai.value, prefix: '$', suffix: '/mo', rank: '?', hi: tA - 0.25 <= T}]}));
      k.text('PRICE', 306 * 3, 126 * 3, {size: 39, color: TEAL, align: 'right'});
      if (T >= tB - 0.25) k.slam('IT BOOKS?', CX, 236 * 3, tB - 0.25, {size: 132, color: Math.floor((T - tB) * 4) % 2 ? RED : GOLD, align: 'center', from: 0.5, drop: INK, glint: false});
      return host(k, 'point');
    },

    /* ---- person: PATLive's own page in the phone, its address; "$49/mo" and "+ $2.99/min" land on the words; a     */
    /* meter rolls 0 to 100 minutes and the bill to $348 (EXAMPLE, 100 minutes).                                        */
    person: (k, T) => {
      const n = k.data.numbers, t0 = k.S('person'), tF = wordT(k, 'person', /^forty/i, 0.6), tP = wordT(k, 'person', /^plus/i, 1.6), tMin = wordT(k, 'person', /^minute/i, 3.2);
      const d = desk(k);
      pagePhone(k, d, 'patlive', 'patlive.com/pricing, Nov 1', 0, t0);
      k.text('A PERSON', RX * 3, 98 * 3, {size: 39, color: ORANGE});
      priceLines(k, d, [{s: `${n.person.shown}/mo`, y: 112, at: Math.min(tF, t0 + 0.35), size: 99, c: GOLD}, {s: `+${n.permin.shown}/min`, y: 152, at: tP}]);
      if (T >= tMin - 0.1) {
        const p = clamp((T - tMin) / 0.7), m = Math.round(n.pmins.value * eo(p)), bill = n.person.value + m * n.permin.value;
        d.win(RX - 4, 184, 164, 86, {base: '#0E1F2A', hi: '#16323F', lo: INK, rule: TEAL});
        k.text(`${m} MIN`, (RX + 78) * 3, 194 * 3, {size: 66, color: CREAM, align: 'center'});
        k.text(p >= 1 ? `${n.ptotal.shown}/mo` : `$${bill.toFixed(0)}`, (RX + 78) * 3, 222 * 3, {size: 99, color: p >= 1 ? RED : GOLD, align: 'center'});
        tag(k, 'EXAMPLE USE', (RX + 78) * 3, 280 * 3, {align: 'center', color: ORANGE});
      }
      return host(k, T >= tP ? 'lean' : null);
    },

    /* ---- ai: Rosie's own page in the phone with its address; "$49/mo" and "250 min" land; on "only" SENDS A LINK   */
    /* stamps; a small tag: booking is on its $149 plan.                                                                */
    ai: (k, T) => {
      const n = k.data.numbers, t0 = k.S('ai'), tF = wordT(k, 'ai', /^forty/i, 0.5), tM = wordT(k, 'ai', /^hundred|^two/i, 1.6), tO = wordT(k, 'ai', /^only/i, 3.6);
      const d = desk(k);
      pagePhone(k, d, 'rosie', 'heyrosie.com/pricing, Nov 1', 230, t0);
      k.text('AN AI', RX * 3, 98 * 3, {size: 39, color: '#C9A7F0'});
      priceLines(k, d, [{s: `${n.ai.shown}/mo`, y: 112, at: Math.min(tF, t0 + 0.35), size: 99, c: GOLD}, {s: `${n.aimin.shown} min`, y: 152, at: tM}]);
      if (T >= tO - 0.25) {
        stampBox(k, 'SENDS A LINK', (RX + 80) * 3, 188 * 3, tO - 0.25, {color: RED, size: 66});
        tag(k, 'This plan. Booking', (RX + 80) * 3, 236 * 3, {align: 'center'});
        tag(k, `is on its ${n.aibook.shown} plan.`, (RX + 80) * 3, 254 * 3, {align: 'center'});
      }
      return host(k, T >= tO ? 'shrug' : null);
    },

    /* ---- text: Quo's own page in the phone (its yearly view) with its address; "$19/mo" lands, "$15 paid yearly"   */
    /* under it; a missed call buzzes and our example auto-reply pops back. On "It answers" the ITEM SHOP card.         */
    text: (k, T) => {
      const n = k.data.numbers, t0 = k.S('text'), tN = wordT(k, 'text', /^nineteen/i, 1.2), tCard = k.S('text.card');
      if (T >= tCard - 0.25) { shopCard(k, tCard - 0.25); blinds(k, tCard - 0.25); return host(k, 'point'); }
      const d = desk(k), {P} = d;
      pagePhone(k, d, 'quo', 'quo.com/pricing, Nov 1', 190, t0);
      k.text('MISSED-CALL TEXT', RX * 3, 98 * 3, {size: 39, color: TEAL});
      priceLines(k, d, [{s: `${n.text.shown}/mo`, y: 112, at: Math.min(tN, t0 + 0.35), size: 99, c: GOLD}]);
      if (T >= t0 + 0.2) { tag(k, `${n.textyr.shown}/mo paid yearly`, RX * 3, 150 * 3, {color: SAND}); tag(k, '+ carrier fees', RX * 3, 162 * 3, {color: SAND}); }
      const tBz = t0 + 0.3;
      if (T >= tBz) {
        const sh = T < tBz + 0.4 ? (Math.floor(T * 30) % 2 ? 2 : -2) : 0;
        d.win(RX - 2 + sh, 176, 162, 28, {base: '#2B2033', hi: '#3D2E45', lo: INK, rule: RED});
        k.text('MISSED CALL', (RX + 79 + sh) * 3, 184 * 3, {size: 39, color: RED, align: 'center'});
        if (T >= tBz + 0.5) { const sl = d.ease(tBz + 0.5, 5, 20); P(RX, 208 + sl, 160, 56, CREAM); P(RX, 208 + sl, 160, 1, '#FFFFFF');
          ['Sorry I missed you,', "I'm on a job..."].forEach((l, i) => k.text(l, (RX + 6) * 3, (214 + sl + i * 18) * 3, {size: 39, color: INK}));
          tag(k, 'AUTO-REPLY, EXAMPLE', (RX + 80) * 3, 276 * 3, {align: 'center', color: ORANGE}); }
      }
      return host(k, T >= tN ? 'lean' : null);
    },

    /* ---- button: the card stays; "Call back inside the hour." lands under the box; IF YOU CALL BACK stamps on the TEXT row (the rule, not a pick)   */
    /* on "worth" (a game moment).                                                                   */
    button: (k, T) => {
      const tCard = k.S('text.card'), tW = wordT(k, 'button', /^worth/i, 3.6), tH = wordT(k, 'button', /^hour/i, 1.2);
      const c = shopCard(k, tCard - 0.25, {best: tW - 0.25});
      if (T >= tH - 0.25) k.slam('Call back inside the hour.', CX, (c.by + c.bh + 6) * 3, tH - 0.25, {size: 66, color: GOLD, align: 'center', from: 0.4, drop: INK, glint: false});
      if (T >= tW - 0.25) stampBox(k, 'IF YOU CALL BACK', 520, (c.Y + 6) * 3, tW - 0.25, {color: TEAL, size: 39});
      return host(k, T >= tW + 0.8 ? 'wave' : 'point');
    },
  },
};
