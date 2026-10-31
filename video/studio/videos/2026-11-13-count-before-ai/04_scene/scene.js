/* Scene: Do you need an AI receptionist? Part 1 of 2, the count (playbook, arcade; Depth bank #3). One function per    */
/* top-level cue in 03_cues/cues.md. Numbers only from k.data (brief.md -> data.js); every time from a cue start (k.S)  */
/* or a spoken word (wordT), so a re-voiced take moves the picture with it. Every number is ours: EXAMPLE on screen.    */
/* Worlds: hook = dispatch (14 pins), a phone close-up, our own office laptop; usual = our office; step and button =    */
/* calendar; board = our own chalk board; check = our own balance scale; next = inventory. None used by the two lessons */
/* before it (lsa-missed-calls: chat, flaps, gauge, versus; missed-call-text: street, register, hud, scores).           */
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


/* text that fits: the biggest of the given sizes whose width fits maxW */
const fit = (k, s, maxW, sizes = [198, 132, 99, 66, 39]) => { for (const z of sizes) if (k.measure(String(s), {size: z}) <= maxW) return z; return sizes[sizes.length - 1]; };
const exTag = (k, d, x, y) => { d.P(x, y, 84, 18, INK); d.P(x + 1, y + 1, 82, 16, ORANGE); k.text('EXAMPLE', (x + 42) * 3, (y + 2) * 3, {size: 30, color: INK, align: 'center', lint: false}); };
const partTag = (k, d, n, x = 20, y = 160) => { const s = `PART ${n.part.shown} OF ${n.series.shown}`, w = Math.ceil((k.measure(s, {size: 39}) + 36) / 3); d.P(x, y, w + 2, 22, INK); d.P(x + 1, y + 1, w, 20, ORANGE); k.text(s, (x + 1 + w / 2) * 3, (y + 2) * 3, {size: 39, color: INK, align: 'center'}); };
const hookPlate = (k, d, n) => {
  d.win(14, 84, 332, 66, {base: '#253048', hi: '#3B82C4', lo: '#1B1420', rule: '#3B82C4'});
  k.text(`${n.missed.shown} missed calls.`, 540, 270, {size: 66, color: CREAM, align: 'center', drop: INK});
  k.text('Need an AI receptionist?', 540, 346, {size: 66, color: 'accent', align: 'center', drop: INK});
};

/* our own office: a plum wall with a wainscot rail, a wall clock whose hand steps once a second, the desk top */
const office = (k, o = {}) => {
  const d = px(k), {P, DOT, disc, line, F, T} = d, top = o.top || 290;
  P(0, 0, 360, 417, '#3B3150'); for (let x = 0; x < 360; x += 18) P(x, 0, 1, top, '#342B47');
  P(0, top - 40, 360, 3, '#5A4A72'); P(0, top - 37, 360, 37, '#2E2640'); for (let x = 8; x < 360; x += 30) P(x, top - 33, 20, 29, '#352C49');
  if (o.clock !== false) { disc(326, 40, 13, INK); disc(326, 40, 12, CREAM); disc(326, 40, 10, '#F4E6D3'); const a = (Math.floor(T) % 60) / 60 * Math.PI * 2 - Math.PI / 2; line(326, 40, 326 + Math.round(Math.cos(a) * 8), 40 + Math.round(Math.sin(a) * 8), RED); line(326, 40, 326, 33, INK); DOT(326, 40, INK); }
  P(0, top, 360, 6, '#B07A47'); P(0, top, 360, 1, '#E6C08A');
  for (let y = top + 6, i = 0; y < 417; y += 10, i++) { P(0, y, 360, 10, i % 2 ? '#8C5A33' : '#7A4E2C'); P(0, y + 9, 360, 1, '#5A3720'); }
  P(0, 417, 360, 223, '#1B1420'); for (let x = 0; x < 360; x += 24) P(x, 417, 1, 223, '#231A29'); P(0, 417, 360, 2, '#3D2E45');
  return d;
};
/* a laptop: lid with the AI RECEPTIONIST screen and a talking wave, the base under it */
const laptop = (k, d, x, y, w, h, o = {}) => {
  const {P, F} = d;
  P(x + 3, y + 3, w, h, INK); P(x - 1, y - 1, w + 2, h + 2, INK); P(x, y, w, h, '#4A4E5A'); P(x + 1, y, w - 2, 1, '#9AA0AD');
  P(x + 4, y + 4, w - 8, h - 8, '#1B2A3F'); P(x + 4, y + 4, w - 8, 18, '#253048');
  k.text('AI RECEPTIONIST', (x + w / 2) * 3, (y + 7) * 3, {size: 39, color: CREAM, align: 'center', lint: o.lint});
  if (o.demo) { d.P(x + w - 46, y + 26, 40, 14, RED); k.text('DEMO', (x + w - 26) * 3, (y + 28) * 3, {size: 30, color: CREAM, align: 'center', lint: false}); }
  /* the wave: bars that move with the frame, all in whole pixels */
  const n = Math.floor((w - 24) / 6), cy = y + Math.round(h * 0.62);
  for (let i = 0; i < n; i++) { const a = Math.abs(Math.sin(i * 0.9 + F * 0.35) * Math.sin(i * 0.31 + F * 0.11)), hh = 2 + Math.round(a * (h * 0.28)); P(x + 12 + i * 6, cy - hh, 4, hh * 2, TEAL); }
  /* the base */
  P(x - 10, y + h + 1, w + 20, 6, INK); P(x - 9, y + h + 1, w + 18, 4, '#9AA0AD'); P(x - 9, y + h + 1, w + 18, 1, '#C9CCD3');
};
/* a desk phone close up: the handset, a screen with MISSED CALL and the red badge */
const deskPhone = (k, d, n) => {
  const {P, disc, F} = d;
  P(0, 0, 360, 417, '#24303F'); for (let y = 0; y < 417; y += 6) P(0, y, 360, 1, '#202A37');
  const o = 40;
  P(0, 330, 360, 87, '#1B1420'); P(0, 330, 360, 2, '#3D2E45');
  P(40, 120 + o, 286, 200, INK); P(42, 118 + o, 282, 200, '#2B2033'); P(44, 120 + o, 278, 4, '#4A4E5A');
  /* the handset on its cradle */
  P(58, 132 + o, 70, 170, INK); P(60, 134 + o, 66, 166, '#3D2E45'); P(60, 134 + o, 66, 4, '#6B7080'); disc(93, 150 + o, 12, '#1B1420'); disc(93, 284 + o, 12, '#1B1420');
  /* the screen: MISSED CALL and the count in big type, the one focal point */
  P(146, 132 + o, 164, 110, INK); P(148, 134 + o, 160, 106, '#253048'); P(148, 134 + o, 160, 30, '#7A3442'); P(148, 163 + o, 160, 1, RED);
  k.text('MISSED CALL', 684, (138 + o) * 3, {size: 39, color: CREAM, align: 'center'});
  k.text(n.missed.shown, 684, (172 + o) * 3, {size: 132, color: RED, align: 'center', drop: INK});
  /* the keys */
  for (let r = 0; r < 2; r++) for (let c = 0; c < 4; c++) { P(150 + c * 40, 252 + o + r * 16, 34, 12, '#1B1420'); P(150 + c * 40, 252 + o + r * 16, 34, 2, '#4A4E5A'); }
  /* the ring light blinks once a second */
  P(296, 300 + o, 14, 6, Math.floor(d.T * 2) % 2 ? '#E2633B' : '#7A3442'); P(0, 417, 360, 223, '#120D14');
  return d;
};
/* our own chalk board: green slate in a wood frame, chalk dust, the tray */
const chalk = (k) => {
  const d = px(k), {P, DOT, dith} = d;
  P(0, 0, 360, 417, '#2F2A3A');
  P(10, 80, 340, 222, '#6B4226'); P(10, 80, 340, 2, '#B07A47'); P(14, 84, 332, 214, '#1F3B33');
  for (let i = 0; i < 90; i++) DOT(16 + Math.floor(hash(i * 4.1) * 328), 86 + Math.floor(hash(i * 2.3) * 210), '#2C4A41');
  dith(30, 270, 120, 6, '#3E5C52', 0);
  P(10, 300, 340, 8, '#8C5A33'); P(10, 300, 340, 2, '#D9A066'); P(60, 296, 18, 4, CREAM); P(90, 297, 12, 3, '#E6D3BC');
  P(0, 308, 360, 109, '#2B2033'); P(0, 417, 360, 223, '#1B1420'); for (let x = 0; x < 360; x += 24) P(x, 417, 1, 223, '#231A29');
  return d;
};

const PINS = [[0.30, 0.52], [0.42, 0.47], [0.55, 0.55], [0.70, 0.50], [0.82, 0.62], [0.36, 0.66], [0.50, 0.70], [0.64, 0.68], [0.76, 0.78], [0.44, 0.84], [0.58, 0.88], [0.70, 0.92], [0.86, 0.86], [0.28, 0.80]];

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'THE COUNT',
  sendLine: 'Send this to whoever signs the software bills.',
  transitions: {usual: 'dissolve', step: 'levelselect', board: 'dissolve', check: 'dissolve', next: 'levelselect', button: 'gameover'},
  trauma: {'board.two': 0.6},
  sections: {
    /* ---- hook: three shots. The cover: the dispatch board with 14 red pins already down, the hero 14, the plate and  */
    /* PART 1 OF 2 (no host). By 0.8 s cut to the desk phone close up (MISSED CALL, badge 14); Snow comes in. On "Need" */
    /* cut to the laptop with the AI RECEPTIONIST screen. The plate stays up through every cut.                         */
    hook: (k, T) => {
      const n = k.data.numbers;
      const tIn = Math.min(0.8, Math.max(0.4, wordT(k, 'hook', /^missed/i, 0.6))), tOut = Math.min(2.9, wordT(k, 'hook', /^need/i, 2.8));
      if (T >= tOut) {
        const d = office(k, {top: 300});
        laptop(k, d, 70, 166, 220, 120, {demo: true});
        hookPlate(k, d, n);
        return host(k);
      }
      if (T >= tIn) {
        const d = deskPhone(k, px(k), n);
        hookPlate(k, d, n);
        return host(k);
      }
      k.sets.dispatch({pins: PINS.slice(0, n.missed.value).map(([x, y]) => ({x, y, at: -1, c: '#E2633B'}))});
      const d = px(k);
      k.text(n.missed.shown, 912, 880, {size: 264, color: GOLD, align: 'right', drop: INK});
      k.text('MISSED', 912, 836, {size: 39, color: CREAM, align: 'right', drop: INK});
      hookPlate(k, d, n);
      partTag(k, d, n);
      exTag(k, d, 250, 162);
      return {host: false, speech: false};
    },

    /* ---- usual: our office. The laptop's demo big; stars on "great"; the quote sheet slides up on "sign" with a     */
    /* SIGN HERE line and a pen; WORTH: ? stamps on "worth"; Snow shrugs.                                            */
    usual: (k, T) => {
      const n = k.data.numbers, t0 = k.S('usual'), tGreat = wordT(k, 'usual.great', /^great/i, 0.4), tSign = wordT(k, 'usual.great', /^sign/i, 1.2), tWorth = wordT(k, 'usual.worth', /^worth/i, 1.6);
      if (T >= k.S('usual.worth')) {
        const tW = k.S('usual.worth');
        k.sets.dispatch({pins: PINS.slice(0, n.missed.value).map(([x, y]) => ({x, y, at: tW - 1, c: '#E2633B'}))});
        const d2 = px(k);
        d2.win(14, 84, 332, 66, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
        k.slam(`${n.missed.shown} missed calls.`, 540, 270, tW + 0.05, {size: 66, color: CREAM, align: 'center', from: 0.4, drop: INK, glint: false});
        k.slam('Worth how much?', 540, 346, tW + 0.12, {size: 66, color: GOLD, align: 'center', from: 0.4, drop: INK, glint: false});
        if (T >= tWorth) stampBox(k, 'WORTH: ?', 540, 600, tWorth, {color: RED, freeze: 4});
        return host(k, T >= tWorth + 0.2 ? 'shrug' : null);
      }
      const d = office(k, {top: 300});
      laptop(k, d, 18, 166, 178, 112, {demo: true});
      d.win(14, 84, 332, 66, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: ORANGE});
      k.slam(`PART ${n.part.shown} OF ${n.series.shown}:`, 540, 270, t0 + 0.05, {size: 66, color: CREAM, align: 'center', from: 0.4, drop: INK, glint: false});
      k.slam('THE COUNT', 540, 346, t0 + 0.12, {size: 66, color: ORANGE, align: 'center', from: 0.4, drop: INK, glint: false});
      if (T >= tGreat) [[44, 204], [120, 196], [164, 212]].forEach(([x, y], i) => { const f = d.fr(tGreat + i * 0.12); if (f >= 0) { const yy = y - Math.min(6, f); d.P(x - 1, yy - 6, 3, 13, GOLD); d.P(x - 6, yy - 1, 13, 3, GOLD); d.P(x - 3, yy - 3, 7, 7, GOLD); d.DOT(x, yy, CREAM); d.twinkle(x + 8, yy - 6, f, CREAM); } });
      if (T >= tSign) {
        const sl = d.ease(tSign, 6, 120), x = 206, y = 162 + sl;
        d.P(x + 3, y + 3, 128, 134, INK); d.P(x, y, 128, 134, CREAM); d.P(x, y, 128, 20, '#E6D3BC');
        k.text('QUOTE', (x + 64) * 3, (y + 4) * 3, {size: 39, color: INK, align: 'center'});
        k.text('AI ANSWERING', (x + 64) * 3, (y + 30) * 3, {size: 30, color: '#3D2E45', align: 'center', lint: false});
        k.text('$ ? / MO', (x + 64) * 3, (y + 56) * 3, {size: 39, color: INK, align: 'center'});
        d.P(x + 12, y + 112, 104, 2, INK); k.text('SIGN HERE', (x + 64) * 3, (y + 92) * 3, {size: 30, color: RED, align: 'center', lint: false});
        const pp = clamp((T - tSign - 0.3) / 0.6); d.line(x + 112 - Math.round(40 * pp), y + 112, x + 92 - Math.round(40 * pp), y + 126, '#253048', 3);
      }
      return host(k, k.live('usual.great') ? 'point' : null);
    },

    /* ---- step: the calendar set, NOVEMBER. An X lands on days 1 to 14 on "mark every call"; the week strip on week 1, */
    /* then week 2 on "weeks"; 4 of the days take a coin on "real jobs"; 4 OF 14 lands on "four".                       */
    step: (k, T) => {
      const n = k.data.numbers, t0 = k.S('step'), tMark = wordT(k, 'step', /^mark/i, 1.4), tJobs = wordT(k, 'step.circle', /^jobs/i, 1.8), tFour = wordT(k, 'step.four', /^four/i, 0.4);
      const JOB_DAYS = [3, 6, 10, 13].slice(0, n.jobs.value);
      const fills = [];
      for (let dd = 1; dd <= n.days.value; dd++) fills.push({day: dd, at: tMark + (dd - 1) * 0.1, mark: 'x'});
      JOB_DAYS.forEach((dd, i) => fills.push({day: dd, at: tJobs - 0.3 + i * 0.25, mark: 'coin', c: '#F7C873'}));
      k.sets.calendar({month: 'NOVEMBER', year: 2026, start: 0, days: 30, fills, weeks: [{row: 0, at: t0 + 0.1}, {row: 1, at: tMark + 0.8}]});
      if (T >= tFour) {
        k.slam(`${n.jobs.shown} OF ${n.missed.shown}`, 920, 846, tFour, {size: 132, color: GOLD, align: 'right', from: 0.5, drop: INK, glint: false});
        k.text('REAL JOBS', 330, 870, {size: 39, color: CREAM, drop: INK});
        k.text('OF THE CALLS', 330, 918, {size: 39, color: CREAM, drop: INK});
      } else {
        const s = T >= k.S('step.circle') ? 'Circle the real jobs.' : 'Mark every missed call.';
        k.text(s, 920, 846, {size: fit(k, s, 600, [66, 39]), color: CREAM, align: 'right', drop: INK});
      }
      return host(k, k.live('step.circle') ? 'point' : null);
    },

    /* ---- board: our chalk board, EXAMPLE. "4 jobs x what you clear" chalks on; $350 takes its place on "three"; the   */
    /* hero $1,400 lands on "fourteen", "in 2 weeks" under it; "x 2: call it $2,800 a month" on "twenty".               */
    board: (k, T) => {
      const n = k.data.numbers, t0 = k.S('board'), tClr = wordT(k, 'board.clear', /^three/i, 0.3), tTwo = wordT(k, 'board.two', /^fourteen/i, 0.4), tMo = wordT(k, 'board.month', /^twenty/i, 0.4);
      const d = chalk(k);
      exTag(k, d, 22, 92);
      if (T < tClr) { k.slam(`${n.jobs.shown} jobs x`, 540, 330, t0 + 0.1, {size: 99, color: CREAM, align: 'center', from: 0.3, glint: false}); k.slam('what you clear', 540, 450, t0 + 0.3, {size: 99, color: SAND, align: 'center', from: 0.3, glint: false}); }
      else { const s = `${n.jobs.shown} jobs x ${n.clear.shown}`; k.slam(s, 540, 336, tClr, {size: 99, color: CREAM, align: 'center', from: 0.3, glint: false}); }
      if (T >= tTwo) {
        const hz = fit(k, n.two.shown, 760);
        k.text('=', 150, 470 + Math.round(hz * 0.2), {size: 99, color: CREAM, align: 'center'});
        k.slam(n.two.shown, 580, 450, tTwo, {size: hz, color: GOLD, align: 'center', from: 0.5, drop: INK, glint: false});
        k.text(`in ${n.weeks.shown} weeks`, 540, 690, {size: 66, color: SAND, align: 'center'});
      }
      if (T >= tMo) k.slam(`x 2: call it ${n.month.shown} a month`, 540, 780, tMo, {size: fit(k, `x 2: call it ${n.month.shown} a month`, 900, [66, 39]), color: TEAL, align: 'center', from: 0.3, glint: false});
      return host(k, k.live('board.two') ? 'point' : null);
    },

    /* ---- check: a balance scale on the office desk. Left pan: $2,800 / MO, the missed jobs; right pan: the quote.     */
    /* On "bigger" the quote pan drops and NOT PAID BACK YET stamps; on "Smaller" it swings up and TRY PART 2 lands.     */
    check: (k, T) => {
      const n = k.data.numbers, t0 = k.S('check'), tBig = k.S('check.bigger'), tSm = k.S('check.smaller');
      const d = office(k, {top: 300, clock: false}), {P, line, disc} = d;
      d.win(14, 84, 332, 66, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
      const say = T >= tSm ? ['Price smaller?', `Try part ${n.next.shown}.`, tSm, TEAL] : T >= tBig ? ['Price bigger?', 'Not paid back yet.', tBig, RED] : ['Missed jobs a month', 'next to the quote', t0, GOLD];
      k.slam(say[0], 540, 270, say[2] + 0.05, {size: 66, color: CREAM, align: 'center', from: 0.4, drop: INK, glint: false});
      k.slam(say[1], 540, 346, say[2] + 0.12, {size: 66, color: say[3], align: 'center', from: 0.4, drop: INK, glint: false});
      /* the tilt in whole pixels: level, then the quote side down on "bigger", up on "Smaller" */
      const Y0 = 236, tilt = T >= tSm ? -14 + d.ease(tSm, 6, 28) : (T >= tBig ? 14 - d.ease(tBig, 6, 14) : 0);
      P(176, Y0, 8, 296 - Y0, INK); P(177, Y0, 6, 296 - Y0, '#9AA0AD'); P(150, 292, 60, 8, INK); P(152, 292, 56, 6, '#6B7080'); disc(180, Y0, 6, GOLD);
      line(70, Y0 - tilt, 290, Y0 + tilt, INK, 4); line(70, Y0 - 1 - tilt, 290, Y0 - 1 + tilt, '#C9CCD3', 2);
      const pan = (cx, cy) => { line(cx - 30, cy + 30, cx, cy, '#9AA0AD'); line(cx + 30, cy + 30, cx, cy, '#9AA0AD'); P(cx - 40, cy + 30, 80, 6, INK); P(cx - 39, cy + 30, 78, 4, '#B07A47'); };
      const ly = Y0 - tilt, ry = Y0 + tilt; pan(70, ly); pan(290, ry);
      /* left pan: the money on it; right pan: the quote sheet */
      for (let i = 0; i < 4; i++) d.coin(50 + i * 10, ly + 22, 0);
      k.text(n.month.shown, 210, (ly - 30) * 3 - 30, {size: 66, color: GOLD, align: 'center', drop: INK});
      k.text('/ MO', 210, (ly - 30) * 3 + 30, {size: 39, color: CREAM, align: 'center', drop: INK});
      P(266, ry + 4, 48, 26, INK); P(267, ry + 5, 46, 24, CREAM); P(267, ry + 5, 46, 7, '#E6D3BC');
      k.text('QUOTE', 870, (ry - 30) * 3 - 30, {size: 66, color: CREAM, align: 'center', drop: INK});
      k.text('/ MO', 870, (ry - 30) * 3 + 30, {size: 39, color: CREAM, align: 'center', drop: INK});
      if (T >= tBig && T < tSm) stampBox(k, 'NOT YET', 540, 486, tBig, {color: RED, freeze: 4});
      return host(k, k.live('check.bigger') ? 'shrug' : null);
    },

    /* ---- next: the inventory set, PART 2. Three slots, TEXT BACK, A PERSON, AI; the cursor jumps slot to slot on     */
    /* "three", "options", "side".                                                                                      */
    next: (k, T) => {
      const n = k.data.numbers, t0 = k.S('next'), tA = wordT(k, 'next', /^three/i, 0.6), tB = wordT(k, 'next', /^options/i, 1.0), tC = wordT(k, 'next', /^side/i, 1.6);
      k.sets.inventory({title: `PART ${n.next.shown}`, hint: 'Next part', items: [{icon: 'mail', name: 'TEXT BACK'}, {icon: 'phone', name: 'A PERSON'}, {icon: 'star', name: 'AI'}],
        select: [{slot: 0, at: tA}, {slot: 1, at: tB}, {slot: 2, at: tC}]});
      if (T >= tA) k.slam(`${n.opts.shown} options,`, 72, 640, tA, {size: 66, color: CREAM, from: 0.4, drop: INK, glint: false});
      if (T >= tC) k.slam('side by side.', 72, 716, tC, {size: 66, color: GOLD, from: 0.4, drop: INK, glint: false});
      return host(k, k.live('next') ? 'point' : null);
    },

    /* ---- button: back on the calendar, every X and coin settled; the rule lands in gold on the plate; NEXT: PART 2  */
    /* in the strip; Snow waves.                                                                                       */
    button: (k, T) => {
      const n = k.data.numbers, t0 = k.S('button');
      const d = chalk(k);
      /* the tally from the calendar, chalked small in the corner: 14 strokes, 4 circled */
      for (let i = 0; i < n.missed.value; i++) { const g = Math.floor(i / 5), j = i % 5, x = 36 + g * 30 + j * 5; if (j === 4) d.line(x - 21, 116, x + 1, 100, CREAM, 1); else d.P(x, 98, 1, 20, CREAM); }
      k.slam('Count the', 540, 330, t0 + 0.05, {size: 132, color: CREAM, align: 'center', from: 0.4, glint: false});
      k.slam('missed calls', 540, 480, t0 + 0.12, {size: fit(k, 'missed calls', 900, [132, 99]), color: GOLD, align: 'center', from: 0.4, drop: INK, glint: false});
      k.slam('before you buy.', 540, 630, t0 + 0.2, {size: 99, color: CREAM, align: 'center', from: 0.4, glint: false});
      k.sweep(540 - k.measure('missed calls', {size: fit(k, 'missed calls', 900, [132, 99])}) / 2, 624, k.measure('missed calls', {size: fit(k, 'missed calls', 900, [132, 99])}), 6, t0 + 0.6, {color: 'accent'});
      k.text(`NEXT: PART ${n.next.shown}`, 540, 780, {size: 66, color: TEAL, align: 'center'});
      return host(k, T >= t0 + 1.2 ? 'wave' : 'point');
    },
  },
};
