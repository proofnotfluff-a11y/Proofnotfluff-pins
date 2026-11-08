/* Scene: Pay before you leave (proven at the 100K bar, our own version of research/PROVEN.md row 1; Nov 8, 2026). One  */
/* function per top-level cue in 03_cues/cues.md; every time from a cue start or a spoken word (wordT). Worlds: hook =   */
/* the cover hero, the finished job, her porch, then the street set (the van drives off); weeks = the calendar set;       */
/* receipt = ServiceTitan's own line on a card, then the 94% hero over 100 cards (data.js); send = the driveway card,     */
/* held still; why = the levelup set; button = the street set again, parking with the reader. Story items are EXAMPLE.    */
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', DTEAL = '#2F6F67', GREY = '#9AA0AD', NIGHT = '#1B1420', SLATE = '#4A4E5A';
const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eo = (x) => 1 - Math.pow(1 - clamp(x), 3);

/* ---- the pixel kit (low-res units: 360 x 640, one pixel = 3 frame units), as in the lessons before ---- */
const px = (k) => {
  const ctx = k.ctx, T = k.T, F = Math.floor(T * 30 + 0.005);
  const P = (x, y, w, h, c) => { x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h); if (w > 0 && h > 0 && c) { ctx.fillStyle = c; ctx.fillRect(x * 3, y * 3, w * 3, h * 3); } };
  const DOT = (x, y, c) => P(x, y, 1, 1, c);
  const dith = (x, y, w, h, c, ph = 0) => { ctx.fillStyle = c; for (let j = 0; j < h; j++) for (let i = (j + ph) & 1; i < w; i += 2) ctx.fillRect((Math.round(x) + i) * 3, (Math.round(y) + j) * 3, 3, 3); };
  const win = (x, y, w, h, o = {}) => {
    const base = o.base || '#253048', hi = o.hi || '#3B82C4', lo = o.lo || NIGHT, rule = o.rule === undefined ? '#87CEEB' : o.rule;
    if (o.shadow !== false) P(x + 2, y + 2, w, h, INK);
    P(x + 1, y, w - 2, h, INK); P(x, y + 1, w, h - 2, INK);
    P(x + 1, y + 1, w - 2, h - 2, base); P(x + 2, y + 1, w - 4, 1, hi); P(x + 1, y + 2, 1, h - 4, hi); P(x + 2, y + h - 2, w - 4, 1, lo); P(x + w - 2, y + 2, 1, h - 4, lo);
    if (rule) { P(x + 3, y + 3, w - 6, 1, rule); P(x + 3, y + h - 4, w - 6, 1, rule); P(x + 3, y + 3, 1, h - 6, rule); P(x + w - 4, y + 3, 1, h - 6, rule); }
  };
  const fr = (t0) => Math.floor((T - t0) * 30 + 0.005);
  const ease = (t0, frames, dist) => Math.round(dist * (1 - eo(fr(t0) / frames)));
  const tx = (s, x, y, o = {}) => k.text(s, x * 3, y * 3, Object.assign({size: 48}, o));
  return {P, DOT, dith, win, fr, ease, tx, F, T};
};

/* ---- the words: every beat lands on a spoken word ---- */
const WS = () => (window.WORDS && window.WORDS.words) || [];
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
const host = (k, pose, sc = 0.55) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: sc, hostX: 150});
const topPlate = (k, d, a, b, t0) => {
  d.win(14, 84, 332, 64, {base: '#253048', hi: '#3B82C4', lo: NIGHT, rule: '#3B82C4'});
  k.slam(a, 540, 266, t0, {size: 66, color: CREAM, align: 'center', drop: INK, from: 0.4});
  k.slam(b, 540, 344, t0 + 0.06, {size: 66, color: GOLD, align: 'center', drop: INK, from: 0.4});
};
const stampBox = (k, s, cx, y, t0, o = {}) => {
  const size = o.size || 66, c = o.color || GOLD, w = Math.round((Math.max(k.measure(s, {size}), o.sub ? k.measure(o.sub, {size}) : 0) + 54) / 6) * 6, h = size + 36 + (o.sub ? size + 12 : 0), x = Math.round((cx - w / 2) / 3) * 3;
  k.stampIn(t0, () => {
    k.shape(k.rectPts(x + 6, y + 6, w, h, 0), {fill: INK, line: false}); k.shape(k.rectPts(x, y, w, h, 0), {fill: NIGHT, line: false});
    k.shape(k.rectPts(x + 6, y + 6, w - 12, 6, 0), {fill: c, line: false}); k.shape(k.rectPts(x + 6, y + h - 12, w - 12, 6, 0), {fill: c, line: false});
    k.shape(k.rectPts(x + 6, y + 6, 6, h - 12, 0), {fill: c, line: false}); k.shape(k.rectPts(x + w - 12, y + 6, 6, h - 12, 0), {fill: c, line: false});
    k.text(s, x + w / 2, y + 18, {size, color: c, align: 'center'}); if (o.sub) k.text(o.sub, x + w / 2, y + 30 + size, {size, color: c, align: 'center'});
  }, {at: [x + w / 2, y + h], freeze: o.freeze});
};
const exampleTag = (d, x, y) => { d.P(x, y, 128, 32, INK); d.P(x + 1, y + 1, 126, 30, ORANGE); d.tx('EXAMPLE', x + 64, y + 5, {size: 52, color: INK, align: 'center'}); };

const fadeSteps = (d, step) => { if (step <= 0) return; if (step >= 4) { d.P(0, 0, 360, 417, INK); return; } for (let j = 0; j < 417; j++) if (step >= 2 || j % 2 === 0) d.dith(0, j, 360, 1, INK, j % 2); if (step === 3) d.dith(0, 0, 360, 417, INK, 1); };

/* a blinds wipe between rooms inside a cue (design: no plain cuts): six ink bars close over 3 frames, open over 3 */
const blinds = (d, T, at) => {
  const f = Math.floor((T - at) * 30 + 0.005); if (f < -3 || f > 3) return;
  const h = Math.round(70 * (1 - Math.abs(f) / 3.5)); for (let i = 0; i < 6; i++) d.P(0, i * 70, 360, Math.min(70, h), INK);
};
/* her porch: siding, the front door with its glass, a porch light, the mat, a potted plant */
const porch = (k, d) => {
  const {P, dith, F} = d;
  P(0, 0, 360, 417, '#5B7A8C'); for (let y = 0; y < 330; y += 9) P(0, y, 360, 1, '#4E6A7A');
  P(0, 330, 360, 87, '#8C6A4E'); for (let x = 0; x < 360; x += 24) P(x, 330, 1, 87, '#7A5A40');
  P(130, 120, 100, 210, INK); P(134, 124, 92, 206, '#7A3442'); P(150, 140, 60, 50, '#87CEEB'); P(150, 164, 60, 2, '#7A3442');
  P(206, 230, 8, 8, GOLD); P(110, 316, 140, 14, '#3D2E45');
  const fl = Math.floor(F / 12) % 2; P(256, 150, 20, 26, INK); P(258, 152, 16, 22, fl ? '#FFE7A8' : GOLD);
  P(60, 280, 36, 50, '#B07A47'); P(64, 250, 28, 34, '#2F6F67'); dith(64, 250, 28, 34, '#24453A');
};
/* the finished job: a new water heater in a clean utility room, pipes, a drain pan */
const utility = (k, d) => {
  const {P, dith} = d;
  P(0, 0, 360, 417, '#D9CBB5'); dith(0, 0, 360, 417, '#CBBBA2'); P(0, 340, 360, 77, '#9AA0AD');
  P(120, 110, 120, 230, INK); P(124, 114, 112, 222, '#E6E9F0'); P(124, 114, 12, 222, '#FFFFFF'); P(226, 114, 10, 222, '#B9BEC8');
  P(150, 80, 8, 34, '#B07A47'); P(202, 80, 8, 34, '#6FB7A8'); P(150, 76, 60, 6, '#8C8F99');
  P(110, 334, 140, 10, '#5C606E'); P(160, 200, 40, 26, INK); P(164, 204, 32, 18, '#24453A'); P(168, 208, 6, 6, '#6FB7A8');
};
/* the 100 cards: a 10 x 10 grid, the first n lit (n from data.js), filling a few per frame from t0 */
const cardGrid = (k, d, n, t0) => {
  const {P} = d, lit = Math.min(n, Math.max(0, Math.floor((k.T - t0) * 90)));
  for (let i = 0; i < 100; i++) {
    const x = 95 + (i % 10) * 17, y = 196 + Math.floor(i / 10) * 12, on = i < lit;
    P(x, y, 14, 9, on ? GOLD : '#3D2E45'); P(x, y + 2, 14, 2, on ? '#B07A47' : '#2B2033');
  }
};
/* ServiceTitan's line on a card, typed on, with its tag (the real screen, our drawing of it) */
const sourceCard = (k, d, t0, typeAt) => {
  const {P, win} = d, up = d.ease(t0, 6, 30);
  win(14, 84 + up, 332, 246, {base: CREAM, hi: '#FFFFFF', lo: SAND, rule: false});
  P(14, 84 + up, 332, 46, DTEAL);
  k.text('HOME SERVICE', 72, 268 + up * 3, {size: 52, color: CREAM});
  k.text('CUSTOMERS', 72, 322 + up * 3, {size: 52, color: GOLD});
  k.wrap('Source: ServiceTitan blog, May 6, 2026, citing Visa figures. Read Nov 8, 2026.', {size: 48}, 840)
    .forEach((s, i) => k.text(s, 72, 720 + i * 52 + up * 3, {size: 48, color: SLATE}));
  if (up) return;
  const n0 = k.data.numbers.own.shown;
  const lines = ['"Visa figures show that', n0 + ' of home service', 'customers own a', 'credit card"'];
  let n = Math.max(0, Math.floor((k.T - typeAt) * 90));
  lines.forEach((s, i) => { const m = Math.min(s.length, n); n -= m; if (m) k.text(s.slice(0, m), 72, 420 + i * 70, {size: 64, color: INK}); });
};
/* the send card: the driveway line on a clipboard card, held still over the driveway at dusk */
const LINE = "Let's walk the job together. If you're happy with it, I can take payment right here.";
const driveCard = (k, d, t0) => {
  const {P} = d, up = d.ease(t0 + 0.02, 5, 160), so = d.F % 12;
  P(0, 0, 360, 417, '#3A4A5E'); for (let y = so - 12; y < 340; y += 12) P(0, Math.max(0, y), 360, Math.max(0, Math.min(y + 6, 340) - Math.max(0, y)), '#33415A');
  P(0, 340, 360, 77, '#5C606E'); for (let x = (d.F % 24) - 24; x < 360; x += 24) P(Math.max(0, x), 376, 12, 3, '#E6E9F0');
  P(16, 82 + up, 332, 238, INK); P(12, 78 + up, 336, 238, '#2B2033'); P(18, 86 + up, 324, 224, CREAM);
  P(18, 86 + up, 324, 26, DTEAL);
  if (up !== 0) return null;
  k.text('FOR THE LEAD TECHNICIAN', 72, 266, {size: 52, color: CREAM});
  k.text('BEFORE YOU PACK UP', 72, 354, {size: 80, color: INK});
  P(24, 146, 312, 136, '#E6F2EF'); P(24, 146, 3, 136, TEAL);
  const ls = k.wrap(LINE, {size: 60}, 840);
  ls.forEach((s, i) => k.text(s, 96, 462 + i * 78, {size: 60, color: INK}));
  exampleTag(d, 204, 282);
  return ls;
};
const sweepLine = (k, ls, re, at, T) => { const i = ls.findIndex((s) => re.test(s)); if (i >= 0 && T >= at) k.sweep(96, 462 + i * 78 + 66, k.measure(ls[i], {size: 60}), 6, at, {color: 'accent'}); };
/* a speech bubble in the band top (frame y 262 down): cream box, a tail, the line */
const bubble = (k, d, lines, t0, o = {}) => {
  if (k.T < t0) return; const {P} = d, up = d.ease(t0, 5, 30), Y = 92 - up, h = 20 + lines.length * 24, w = o.w || 300, X = o.x || 30;
  P(X + 2, Y + 2, w, h, INK); P(X, Y, w, h, CREAM); P(X + 40, Y + h, 14, 8, CREAM);
  lines.forEach((s, i) => k.text(s, (X + 14) * 3, (Y + 8 + i * 24) * 3, {size: 60, color: INK}));
};
/* the card reader panel in the sky: TAP TO PAY, then APPROVED */
const reader = (k, d, ok, x, y) => {
  const {P} = d; P(x + 2, y + 2, 120, 64, INK); P(x, y, 120, 64, '#2B2033'); P(x + 6, y + 6, 108, 36, ok ? '#2F6F67' : '#1F2A40');
  k.text(ok ? 'APPROVED' : 'TAP TO PAY', (x + 60) * 3, (y + 14) * 3, {size: 52, color: ok ? CREAM : GOLD, align: 'center'});
  P(x + 40, y + 48, 40, 10, GREY);
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'GET PAID BEFORE YOU GO',
  sendLine: 'Send this to your lead technician.',
  transitions: {weeks: 'wipe', receipt: 'mosaic', send: 'fade4', why: 'glitch', button: 'iris'},
  trauma: {},
  sections: {
    /* ---- hook: frame 0 is the cover hero; 0.5 s blinds to the finished job, DONE on "done"; 2.4 s blinds to her */
    /* porch, the bubble on "I'll"; 4.5 s blinds to the street, the van drives off ---- */
    hook: (k, T) => {
      const d = px(k), n = k.data.numbers.own, tJob = 0.5, tPorch = 2.4, tStreet = 4.5, tSays = wordT(k, 'hook', /^"?i'll/i, 3.1) - 0.2;
      if (T < tJob) {
        porch(k, d);
        d.win(14, 84, 332, 236, {base: '#253048', hi: '#3B82C4', lo: NIGHT, rule: '#3B82C4'});
        k.text(n.shown, 540, 268, {size: 340, color: ORANGE, align: 'center', drop: INK});
        k.text('OF HOME SERVICE CUSTOMERS', 540, 618, {size: 52, color: CREAM, align: 'center'});
        k.text('OWN A CREDIT CARD', 540, 676, {size: 52, color: CREAM, align: 'center'});
        k.text('Source: ServiceTitan, citing Visa', 540, 760, {size: 52, color: GOLD, align: 'center'});
        blinds(d, T, tJob);
        return host(k, 'point', 0.75);
      }
      if (T < tPorch) {
        utility(k, d); exampleTag(d, 176, 90);
        stampBox(k, 'DONE', 540, 760, 0.55, {color: TEAL, size: 80, freeze: 4});
        blinds(d, T, tJob); blinds(d, T, tPorch);
        return host(k, 'point', 0.55);
      }
      if (T < tStreet) {
        porch(k, d); exampleTag(d, 176, 290);
        bubble(k, d, ["I'll mail you", 'a check."'], tSays);
        blinds(d, T, tPorch); blinds(d, T, tStreet);
        return host(k, 'shrug', 0.55);
      }
      const r = k.sets.street({t0: tStreet, speed: 1, van: true});
      exampleTag(d, 176, 92); blinds(d, T, tStreet);
      return host(k, null, 0.55);
    },

    /* ---- weeks: three weeks crossed off; NO CHECK, NO ANSWER, STILL CHASING on their words ---- */
    weeks: (k, T) => {
      const t0 = k.S('weeks'), d = px(k), tNo = wordT(k, 'weeks', /^no$/i, 1.3) - 0.2, tStop = wordT(k, 'weeks', /^won't/i, 2.5) - 0.2, tChase = wordT(k, 'weeks', /^chasing/i, 5.5) - 0.2;
      const r = k.sets.calendar({month: 'NOVEMBER', year: 2026, start: 0, days: 30, run: {from: 3, to: 24, at: t0 + 0.2, every: 0.09, c: '#7A3442', mark: 'x'}});
      exampleTag(d, 150, 276);
      const a = (r && r.area) || {x: 330, y: 840, w: 600, h: 300};
      /* one slot under the month, each line replacing the last */
      if (T >= tChase) k.slam('STILL CHASING', 610, 936, tChase, {size: 56, color: CREAM, align: 'center', drop: INK, from: 0.3});
      else if (T >= tStop) k.slam('NO ANSWER', 610, 936, tStop, {size: 56, color: GOLD, align: 'center', drop: INK, from: 0.3});
      else if (T >= tNo) k.slam('NO CHECK', 610, 936, tNo, {size: 56, color: RED, align: 'center', drop: INK, from: 0.3});
      return host(k, T >= tChase ? 'shrug' : null);
    },

    /* ---- receipt: ServiceTitan's line typed on; on "ninety-four" a four-step fade to the 94% hero over 100 cards ---- */
    receipt: (k, T) => {
      const t0 = k.S('receipt'), d = px(k), n = k.data.numbers.own, tHero = wordT(k, 'receipt', /^ninety/i, 3.3) - 0.2, tHas = wordT(k, 'receipt', /^has$/i, 8.7) - 0.25;
      if (T < tHero) {
        d.P(0, 0, 360, 417, '#253048'); for (let y = (d.F >> 2) % 8 - 8; y < 417; y += 8) d.P(0, Math.max(0, y), 360, 3, NIGHT);
        sourceCard(k, d, t0, t0 + 0.5);
        if (T >= tHero - 0.13) fadeSteps(d, 1 + Math.floor((T - tHero + 0.13) / 0.033));
        return host(k);
      }
      d.P(0, 0, 360, 417, '#1F2A40'); for (let y = (d.F >> 2) % 8 - 8; y < 417; y += 8) d.P(0, Math.max(0, y), 360, 2, '#24304A');
      k.text('Source: ServiceTitan, citing Visa', 540, 266, {size: 52, color: CREAM, align: 'center', drop: INK});
      k.text(n.shown, 540, 318, {size: 200, color: GOLD, align: 'center', drop: INK});
      k.text('OWN A CREDIT CARD', 540, 530, {size: 56, color: CREAM, align: 'center', drop: INK});
      cardGrid(k, d, n.value, tHero + 0.1);
      if (T >= tHas) k.sweep(330, 590, 420, 6, tHas, {color: 'accent'});
      if (T < tHero + 0.13) fadeSteps(d, 4 - Math.floor((T - tHero) / 0.033));
      return host(k, T >= tHero + 0.6 ? 'point' : null);
    },

    /* ---- send: the driveway card goes up whole, then holds still; sweeps land on the words ---- */
    send: (k, T) => {
      const d = px(k), ls = driveCard(k, d, k.S('send'));
      if (ls) {
        const w = (re, dd) => wordT(k, 'send', re, dd) - 0.25;
        const tLead = w(/^lead/i, 5.6), tLine = w(/^line/i, 8.7), tPay = w(/^payment/i, 11.8), tCard = w(/^card$/i, 13.2);
        if (T >= tLead) k.sweep(72, 266 + 58, k.measure('FOR THE LEAD TECHNICIAN', {size: 52}), 6, tLead, {color: 'accent'});
        sweepLine(k, ls, /walk/, tLine, T);
        sweepLine(k, ls, /payment/, tPay, T);
      }
      return host(k, ls ? 'point' : null);
    },

    /* ---- why: the bar fills; PAID ON SITE stamps on "there's"; the two reasons land on their words ---- */
    why: (k, T) => {
      const t0 = k.S('why'), tThere = wordT(k, 'why', /^there's/i, 1.8) - 0.1, tFix = wordT(k, 'why', /^there$/i, 6.3) - 0.15;
      k.sets.levelup({from: 0, to: 100, max: 100, at: t0 + 0.1, dur: 1.4, levelAt: tThere, text: 'PAID ON SITE'});
      if (T >= tThere) k.slam('+ NO CHECK TO CHASE', 540, 820, tThere, {size: 56, color: CREAM, align: 'center', drop: INK, from: 0.3});
      if (T >= tFix) k.slam('+ FIX IT WHILE THERE', 540, 900, tFix, {size: 56, color: GOLD, align: 'center', drop: INK, from: 0.3});
      return host(k, T >= tThere ? 'point' : null);
    },

    /* ---- button: the van drives up and parks with the PAID sign on "card reader"; her bubble, then the reader ---- */
    button: (k, T) => {
      const t0 = k.S('button'), d = px(k), tShe = wordT(k, 'button', /^she'll/i, 1.6) - 0.2, tReader = wordT(k, 'button', /^card$/i, 4.6) - 0.2;
      k.sets.street({t0: t0 + 0.6, speed: 1, stopAt: tReader - 0.6, stopDur: 0.8, sign: 'PAID', van: true});
      if (T < tReader) bubble(k, d, ["I'll mail", 'a check."'], tShe, {w: 200, x: 20});
      else reader(k, d, T >= tReader + 0.4, 120, 96);
      exampleTag(d, 182, 164);
      return host(k, T >= tReader ? 'wave' : null);
    },
  },
};
/* a faint dither drifts down the empty lower band of every scene, below the host and every text, so no stretch goes   */
/* still (code QA, flat). It never crosses the send card (band y 84 to 316).                                          */
const drift = (k) => { const d = px(k), off = Math.floor(k.T * 30) % 16; for (let y = 418 - 16 + off; y < 640; y += 16) { const y0 = Math.max(418, y), y1 = Math.min(640, y + 8); if (y1 > y0) d.P(0, y0, 360, y1 - y0, '#2B2033'); } };
for (const [n, f] of Object.entries(window.SCENE.sections)) window.SCENE.sections[n] = (k, T) => { const r = f(k, T); drift(k); return r; };
