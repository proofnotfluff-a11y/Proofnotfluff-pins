/* Scene: Ask ChatGPT who it would hire (short of 2026-11-19-ask-chatgpt; arcade; Nov 7, 2026). One function per top- */
/* level cue in 03_cues/cues.md. Numbers only from k.data; every time from a cue start or a spoken word (wordT).        */
/* Worlds (its own, not the parent's kitchen and chat): hook = the storefront with the price tag (counter set), then the */
/* dispatch board (who it sends the job to); send = THE CHECK as a work order (the send moment, held still); why = the  */
/* departures board (what it reads); small = the gauge (about 1% of revenue); button = the work order, small, still.    */
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', GREY = '#9AA0AD', SKY = '#87CEEB', NIGHT = '#1B1420';
const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eo = (x) => 1 - Math.pow(1 - clamp(x), 3);

/* ---- the pixel kit (low-res units: 360 x 640, one pixel = 3 frame units) ---- */
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
    const base = o.base || '#253048', hi = o.hi || '#3B82C4', lo = o.lo || NIGHT, rule = o.rule === undefined ? SKY : o.rule;
    if (o.shadow !== false) P(x + 2, y + 2, w, h, INK);
    P(x + 1, y, w - 2, h, INK); P(x, y + 1, w, h - 2, INK);
    P(x + 1, y + 1, w - 2, h - 2, base); P(x + 2, y + 1, w - 4, 1, hi); P(x + 1, y + 2, 1, h - 4, hi); P(x + 2, y + h - 2, w - 4, 1, lo); P(x + w - 2, y + 2, 1, h - 4, lo);
    if (rule) { P(x + 3, y + 3, w - 6, 1, rule); P(x + 3, y + h - 4, w - 6, 1, rule); P(x + 3, y + 3, 1, h - 6, rule); P(x + w - 4, y + 3, 1, h - 6, rule); }
  };
  const fr = (t0) => Math.floor((T - t0) * 30 + 0.005);
  const ease = (t0, frames, dist) => Math.round(dist * (1 - eo(fr(t0) / frames)));
  const tx = (s, x, y, o = {}) => k.text(s, x * 3, y * 3, Object.assign({size: 48}, o));
  const tw = (s, size = 39) => k.measure(String(s), {size}) / 3;
  const clip = (x, y, w, h, fn) => { ctx.save(); ctx.beginPath(); ctx.rect(x * 3, y * 3, w * 3, h * 3); ctx.clip(); fn(); ctx.restore(); };
  const twinkle = (x, y, f, c = CREAM) => { const s = [0, 1, 2, 1][((f % 4) + 4) % 4]; DOT(x, y, c); for (let i = 1; i <= s; i++) { DOT(x - i, y, c); DOT(x + i, y, c); DOT(x, y - i, c); DOT(x, y + i, c); } };
  return {P, DOT, dith, disc, line, win, fr, ease, tx, tw, clip, twinkle, F, T};
};

/* ---- the words: every beat lands on a spoken word ---- */
const WS = () => (window.WORDS && window.WORDS.words) || [];
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
const host = (k, pose, big) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: big ? 0.72 : 0.55, hostX: 150});   /* design r0: about 360 px where the band has room */
const plate = (d, x, y, w, h) => d.win(x, y, w, h, {base: NIGHT, hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
/* the two-line title plate at the top of the band (frame y 252 to 444) */
const topPlate = (k, d, a, b, t0, o = {}) => {
  d.win(14, 84, 332, 64, {base: o.base || '#253048', hi: o.hi || '#3B82C4', lo: NIGHT, rule: o.rule || '#3B82C4'});
  k.slam(a, o.align === 'left' ? 72 : 540, 266, t0, {size: 66, color: CREAM, align: o.align || 'center', drop: INK, from: 0.4});
  k.slam(b, o.align === 'left' ? 72 : 540, 344, t0 + 0.06, {size: 66, color: o.c2 || 'accent', align: o.align || 'center', drop: INK, from: 0.4});
};
/* a rubber stamp in a dark box with a coloured rim, landed with the kit's hit-stop */
const stampBox = (k, s, cx, y, t0, o = {}) => {
  const size = o.size || 66, c = o.color || GOLD, w = Math.round((k.measure(s, {size}) + 54) / 6) * 6, h = size + 36, x = Math.round((cx - w / 2) / 3) * 3;
  k.stampIn(t0, () => {
    k.shape(k.rectPts(x + 6, y + 6, w, h, 0), {fill: INK, line: false}); k.shape(k.rectPts(x, y, w, h, 0), {fill: NIGHT, line: false});
    k.shape(k.rectPts(x + 6, y + 6, w - 12, 6, 0), {fill: c, line: false}); k.shape(k.rectPts(x + 6, y + h - 12, w - 12, 6, 0), {fill: c, line: false});
    k.shape(k.rectPts(x + 6, y + 6, 6, h - 12, 0), {fill: c, line: false}); k.shape(k.rectPts(x + w - 12, y + 6, 6, h - 12, 0), {fill: c, line: false});
    k.text(s, x + w / 2, y + 18, {size, color: c, align: 'center'});
  }, {at: [x + w / 2, y + h], freeze: o.freeze});
};
const loopSweep = (k, x, y, w, t0, period = 1.0, h = 8) => { if (k.T < t0) return; const n = Math.floor((k.T - t0) / period); k.sweep(x, y, w, h, t0 + n * period, {color: 'accent'}); };
const exampleTag = (d, x, y) => { d.P(x, y, 80, 22, INK); d.P(x + 1, y + 1, 78, 20, ORANGE); d.tx('EXAMPLE', x + 40, y + 4, {size: 30, color: INK, align: 'center'}); };
const tag = (k, d, s, y = 290, s2) => { plate(d, 14, y, 332, s2 ? 46 : 30); k.text(s, 72, y * 3 + 20, {size: 36, color: SAND}); if (s2) k.text(s2, 72, y * 3 + 72, {size: 36, color: SAND}); };   /* design r0: 36 px floor */
/* THE CHECK as a work order (this short's own look: a paper work order, red header, not the parent's phone card). */
/* Every line lands once in the first half second, then nothing moves over it (the send card, held to screenshot). */
const workOrder = (k, d, t0, o = {}) => {
  const {P, win} = d, up = o.still ? 0 : d.ease(t0, 6, 160);
  d.clip(0, 0, 360, 336, () => { win(14, 84 + up, 332, 236, {base: '#FFF3D6', hi: '#FFFFFF', lo: SAND, rule: false}); P(14, 84 + up, 332, 26, RED);
    if (!up) { for (let y = 150; y < 316; y += 22) P(24, y, 312, 1, '#E6D3BC'); P(46, 110, 2, 206, '#F2A541'); } });
  if (up) return;
  const at = (i) => (o.still ? -10 : t0 + 0.2 + i * 0.05), sl = {from: 0.3, glint: false};
  k.text('WORK ORDER: TONIGHT', 72, 266, {size: 52, color: CREAM});
  k.text('FOR WHOEVER RUNS YOUR GOOGLE PROFILE', 160, 352, {size: 36, color: '#7A3442'});
  k.slam('1. Ask ChatGPT:', 160, 420, at(0), Object.assign({size: 52, color: INK}, sl));
  k.slam('"Who\'s the best [your', 160, 488, at(1), Object.assign({size: 56, color: '#2F6F67'}, sl));
  k.slam('trade] near me?"', 160, 554, at(2), Object.assign({size: 56, color: '#2F6F67'}, sl));
  k.slam('2. Not you? Fix your', 160, 690, at(3), Object.assign({size: 56, color: INK}, sl));
  k.slam('Google profile first.', 160, 756, at(4), Object.assign({size: 56, color: RED}, sl));
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'RUN THE CHECK',
  sendLine: 'Send this to whoever runs your Google profile.',
  transitions: {send: 'levelselect', why: 'mosaic', small: 'dissolve', button: 'gameover'},
  trauma: {},
  sections: {
    /* ---- hook: the cover is the storefront with the tag at the firm's average ticket; on "eleven" the tag sways in;   */
    /* on "Who" the dispatch board: three shops, a route from the homeowner, a "?" over YOU.                            */
    hook: (k, T) => {
      const tk = k.data.numbers.ticket, tWho = k.S('hook.who'), tEl = wordT(k, 'hook', /^eleven/i, 2.0) - 0.25;
      if (T < tWho) {
        const r = k.sets.counter({shop: 'JOBS FROM CHATGPT', item: 'heater', tags: [{price: '$?', at: -1}, {price: tk.shown, at: Math.min(tEl, 1.0) <= 0.05 ? -0.5 : -0.5}]});
        const d = px(k);
        k.text('AVG TICKET', 66, 450, {size: 39, color: CREAM}); k.text('ONE FIRM\'S', 66, 510, {size: 39, color: SAND}); k.text('DATA', 66, 570, {size: 39, color: SAND});
        if (T >= tEl) { const f = d.fr(tEl); if (f >= 0 && f < 3) d.P(230, 132, 64, 3, GOLD); }
        tag(k, d, 'ACHR News column, Mar 18, 2026', 290, '(SearchLight data)');
        return host(k, T >= tEl ? 'shock' : 'point');
      }
      const tPin = tWho + 0.1, tRoute = wordT(k, 'hook.who', /^send/i, 0.6) - 0.2;
      const r = k.sets.dispatch({pins: [{x: 0.30, y: 0.25, at: tPin, c: GREY}, {x: 0.78, y: 0.30, at: tPin + 0.1, c: GREY}, {x: 0.62, y: 0.70, at: tPin + 0.2, c: GOLD}, {x: 0.50, y: 0.45, at: tPin - 0.1, c: SKY}],
        routes: [{pts: [[0.50, 0.45], [0.30, 0.45], [0.30, 0.25]], at: tRoute, dur: 0.8, c: RED}]});
      const a = r.at ? r.at(0.62, 0.70) : [600, 700];
      if (T >= tPin + 0.4) { const b = [0, -1, -2, -1][(Math.floor(T * 30) >> 3) % 4]; k.text('YOU?', a[0], a[1] - 150 + b * 3, {size: 60, color: GOLD, align: 'center', drop: INK}); }
      if (r.area) k.text('Who gets the job?', r.area.x, r.area.y, {size: 52, color: CREAM});
      return host(k);
    },

    /* ---- send: the work order (cues.md [send]); held still while the voice says who to show it to.                    */
    send: (k, T) => {
      const t0 = k.S('send');
      const d = px(k), {P, dith} = d;
      P(0, 0, 360, 417, '#3D2E45'); for (let y = 0; y < 417; y += 4) dith(0, y, 360, 1, '#2B2033', (y / 4) % 2); P(0, 417, 360, 223, NIGHT);
      workOrder(k, d, t0 + 0.02);
      exampleTag(d, 250, 340);
      return host(k, 'point', true);
    },

    /* ---- why: the departures board, WHAT IT READS; each row flips to YOURS on its word.                               */
    why: (k, T) => {
      const t0 = k.S('why'), ts = [wordT(k, 'why', /^name/i, 3.0) - 0.3, wordT(k, 'why', /^website/i, 3.6) - 0.3, wordT(k, 'why', /^reviews/i, 4.2) - 0.3];
      const r = k.sets.flaps({title: 'WHAT IT READS', cols: 12, rows: [{label: 'NAME', value: 'YOURS', at: Math.min(ts[0], t0 + 0.4)}, {label: 'WEBSITE', value: 'YOURS', at: ts[1]}, {label: 'REVIEWS', value: 'YOURS', at: ts[2], hi: true}]});
      const d = px(k); tag(k, d, 'ACHR News column, Mar 18, 2026', 290, '(SearchLight data)');
      return host(k, 'point');
    },

    /* ---- small: the gauge, the needle barely leaves zero: about 1% of revenue, most contractors, today.               */
    small: (k, T) => {
      const t0 = k.S('small'), tOne = wordT(k, 'small', /^one$/i, 1.6) - 0.4, r1 = k.data.numbers.rev1;
      const r = k.sets.gauge({value: r1.value, max: 100, at: Math.max(t0 + 0.2, tOne - 0.6), dur: 0.8, zones: [[0, 10, RED], [10, 50, GOLD], [50, 100, TEAL]], label: 'SHARE OF REVENUE', suffix: '%'});
      const d = px(k);
      if (r.area) k.text('ABOUT, MOST CONTRACTORS', r.area.x, r.area.y + 70, {size: 39, color: SAND});
      tag(k, d, 'ACHR News column, Mar 18, 2026', 290, '(SearchLight data)');
      return host(k, T >= tOne ? 'shrug' : null);
    },

    /* ---- button: the work order small and still; the plate on "tonight"; then the end card.                          */
    button: (k, T) => {
      const tA = wordT(k, 'button', /^tonight/i, 0.8) - 0.2;
      const d = px(k), {P, dith} = d;
      P(0, 0, 360, 417, '#1B1420'); for (let y = 0; y < 417; y += 4) dith(0, y, 360, 1, '#241A2B', (y / 4) % 2);
      workOrder(k, d, 0, {still: true});
      if (T >= tA) { plate(d, 14, 340, 332, 34); k.slam('Ask it tonight.', 540, 1028, tA, {size: 60, color: GOLD, align: 'center', from: 0.4}); }
      return host(k, 'point', T < tA);
    },
  },
};

/* the drift (code QA: no flat stretch): a faint dither moves down the empty lower band, never over the work order. */
const drift = (k) => { const d = px(k), off = Math.floor(k.T * 30) % 16; for (let y = 418 - 16 + off; y < 640; y += 16) { const y0 = Math.max(418, y), y1 = Math.min(640, y + 8); if (y1 > y0) d.P(0, y0, 360, y1 - y0, '#3D2E45'); } };
for (const [n, f] of Object.entries(window.SCENE.sections)) window.SCENE.sections[n] = (k, T) => { const r = f(k, T); drift(k); return r; };
