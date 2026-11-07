/* Scene: Angi charged you before you read it (proven, our own version of research/PROVEN.md row 2; Nov 7, 2026). One  */
/* function per top-level cue in 03_cues/cues.md; every time from a cue start or a spoken word (wordT). Worlds: hook =    */
/* our roof and a phone (EXAMPLE); receipt = Angi's own help lines typed on (the real screen), four phones ringing;      */
/* send = the new lead card, held still (the send card, cue marked [send]); race = the street set; button = the roof     */
/* again and the card pinned up on the ground. The roof, the phone and the card are ours (EXAMPLE), never Angi's UI.     */
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', GREY = '#9AA0AD', SKY = '#87CEEB', NIGHT = '#1B1420';
const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eo = (x) => 1 - Math.pow(1 - clamp(x), 3);

/* ---- the pixel kit (low-res units: 360 x 640, one pixel = 3 frame units), as in the lessons before ---- */
const px = (k) => {
  const ctx = k.ctx, T = k.T, F = Math.floor(T * 30 + 0.005);
  const P = (x, y, w, h, c) => { x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h); if (w > 0 && h > 0 && c) { ctx.fillStyle = c; ctx.fillRect(x * 3, y * 3, w * 3, h * 3); } };
  const DOT = (x, y, c) => P(x, y, 1, 1, c);
  const dith = (x, y, w, h, c, ph = 0) => { ctx.fillStyle = c; for (let j = 0; j < h; j++) for (let i = (j + ph) & 1; i < w; i += 2) ctx.fillRect((Math.round(x) + i) * 3, (Math.round(y) + j) * 3, 3, 3); };
  const disc = (cx, cy, r, c) => { for (let dy = -r; dy <= r; dy++) { const hw = Math.floor(Math.sqrt(r * r - dy * dy) + 0.4); P(cx - hw, cy + dy, 2 * hw + 1, 1, c); } };
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
  return {P, DOT, dith, disc, win, fr, ease, tx, F, T};
};

/* ---- the words: every beat lands on a spoken word ---- */
const WS = () => (window.WORDS && window.WORDS.words) || [];
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
const host = (k, pose, sc = 0.55) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: sc, hostX: 150});
/* the two-line title plate at the top of the band (frame y 252 to 444) */
const topPlate = (k, d, a, b, t0, o = {}) => {
  d.win(14, 84, 332, 64, {base: o.base || '#253048', hi: o.hi || '#3B82C4', lo: NIGHT, rule: o.rule || '#3B82C4'});
  k.slam(a, 540, 266, t0, {size: 66, color: CREAM, align: 'center', drop: INK, from: 0.4});
  k.slam(b, 540, 344, t0 + 0.06, {size: 66, color: o.c2 || 'accent', align: 'center', drop: INK, from: 0.4});
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
const exampleTag = (d, x, y) => { d.P(x, y, 80, 22, INK); d.P(x + 1, y + 1, 78, 20, ORANGE); d.tx('EXAMPLE', x + 40, y + 4, {size: 30, color: INK, align: 'center'}); };

/* ================================================================================================================ */
/* our roof: sky (red once charged), two drifting clouds, the shingle plane rising to a ridge at the top right         */
const roof = (k, d, o = {}) => {
  const {P, dith, F} = d, red = !!o.red;
  P(0, 0, 360, 417, red ? '#5A1F22' : '#5B8FB9'); P(0, 0, 360, 60, red ? '#3E1518' : '#3B82C4');
  for (let y = 60; y < 120; y += 4) dith(0, y, 360, 1, red ? '#3E1518' : '#3B82C4', (y / 4) % 2);
  [[40, 30, 46], [230, 54, 34]].forEach(([x, y, w], i) => { const xx = ((x + Math.floor(F / (12 + i * 6))) % 420) - 40; P(xx, y, w, 6, red ? '#7A3442' : CREAM); P(xx + 6, y - 4, w - 14, 4, red ? '#7A3442' : CREAM); });
  /* the shingle plane: rows of tabs, each row offset half a tab, from the ridge line down to the bottom */
  const ridge = (x) => 236 - Math.round(x * 0.12);
  for (let x = 0; x < 360; x++) P(x, ridge(x) - 3, 1, 3, '#3D2E45');
  for (let y = 0; y < 220; y += 10) for (let x = -((y / 10) % 2) * 12; x < 360; x += 24) {
    const yy = ridge(Math.max(0, x)) + y; if (yy > 640) continue;
    P(x, yy, 23, 9, (hash(x * 0.37 + y) > 0.5) ? '#4A4E5A' : '#5C606E'); P(x, yy + 9, 24, 1, '#2B2033');
  }
};
/* the phone on the shingles: body, screen, the notification card; buzzing shakes it a pixel every 2 frames */
const phone = (k, d, x, y, s, o = {}) => {
  const {P} = d, bz = o.buzz ? (Math.floor(d.F / 2) % 2 ? 1 : -1) : 0, X = x + bz;
  P(X + 2, y + 2, 60 * s, 110 * s, INK); P(X, y, 60 * s, 110 * s, '#2B2033'); P(X + 3 * s, y + 6 * s, 54 * s, 96 * s, '#1F2A40');
  P(X + 24 * s, y + 2 * s, 12 * s, 2 * s, INK);
  if (o.note) {
    P(X + 6 * s, y + 18 * s, 48 * s, 34 * s, CREAM); P(X + 6 * s, y + 18 * s, 48 * s, 8 * s, TEAL);
    const big = s >= 2;   /* a small phone shows the short line only, so nothing runs off its screen */
    k.text(big ? 'NEW ANGI LEAD' : 'NEW LEAD', (X + 9 * s) * 3, (y + 19 * s) * 3, {size: big ? 66 : 36, color: INK, lint: false});
    if (o.detail && big) { k.text('Roof repair', (X + 9 * s) * 3, (y + 30 * s) * 3, {size: 39, color: INK, lint: false}); k.text('2:00 PM', (X + 9 * s) * 3, (y + 40 * s) * 3, {size: 39, color: '#4A4E5A', lint: false}); }
  }
  if (o.buzz) { const ph = Math.floor(d.F / 3) % 2; [[-6, 20], [-10, 40], [60 * s + 4, 26], [60 * s + 8, 46]].forEach(([dx, dy], i) => { if ((i + ph) % 2) P(X + dx, y + dy, 3, 8, CREAM); }); }
};
/* Angi's own help lines on a card, typed on from t0, the source tag under it (the real screen, our drawing of it) */
const helpCard = (k, d, lines, t0, o = {}) => {
  const {P, win} = d, up = d.ease(t0, 6, 30), h = o.h || 176;
  win(14, 84 + up, 332, h, {base: CREAM, hi: '#FFFFFF', lo: SAND, rule: false});
  P(14, 84 + up, 332, 20, '#2F6F67'); k.text('ANGI LEADS: FAQ', 72, 258 + up * 3, {size: 39, color: CREAM});
  if (up) return;
  let n = Math.max(0, Math.floor((k.T - (o.typeAt == null ? t0 + 0.15 : o.typeAt)) * 90));
  lines.forEach((s, i) => { const m = Math.min(s.length, n); n -= m; if (m) k.text(s.slice(0, m), 72, 328 + i * 66, {size: 60, color: INK}); });
  k.text('Source: intercom.help/angi, read Nov 7, 2026', 72, (84 + h - 18) * 3, {size: 36, color: '#4A4E5A'});
};
/* a line drawn in parts, each its own colour: [[text, colour], ...] from frame x, y */
const runs = (k, parts, x, y, size) => { let cx = x; parts.forEach(([t, c]) => { k.text(t, cx, y, {size, color: c}); cx += k.measure(t, {size}); }); };
/* design r0: Angi's lines on a big phone held up over the roof (a new world, not the last lesson's card room). The */
/* page loads (grey bars) until typeAt, then the first quote lands; the second lands on "four". */
const phonePage = (k, d, t0, tQ1, tQ2) => {
  const {P} = d, up = d.ease(t0, 8, 220);
  roof(k, d);
  const Y = 84 + up;
  P(16, Y + 2, 332, 206, INK); P(12, Y - 4, 336, 208, '#2B2033'); P(20, Y + 4, 320, 196, CREAM);
  P(20, Y + 4, 320, 18, '#4A4E5A'); k.text('intercom.help/angi', 84, (Y + 6) * 3, {size: 44, color: CREAM});
  P(20, Y + 22, 320, 18, '#2F6F67'); k.text('ANGI LEADS: FAQ', 84, (Y + 24) * 3, {size: 44, color: CREAM});
  if (up) return;
  /* design r1: the page title is up the moment the page lands (no skeleton); each quote on two full-width lines */
  k.text('Angi Leads: Frequently Asked Questions', 84, 388, {size: 44, color: '#2F6F67'});
  if (k.T >= tQ1) { runs(k, [['"You\'ll be ', INK], ['charged', RED], [' for each new', INK]], 84, 456, 60); runs(k, [['lead ', INK], ['as soon as it\'s sent', RED], ['"', INK]], 84, 518, 60); }
  if (k.T >= tQ2) { runs(k, [['"connect customers with ', INK], ['up to 4', '#B8860B']], 84, 600, 60); runs(k, [['service professionals"', INK]], 84, 662, 60); }
  k.text('Source: Angi Leads FAQ, read Nov 7, 2026', 84, 790, {size: 44, color: '#4A4E5A'});
};
/* the new lead card (the send card): who it is for, the rule, the text to send, EXAMPLE */
const leadCard = (k, d, t0) => {
  const {P, dith} = d, up = d.ease(t0 + 0.02, 5, 160);
  /* design r0: the card on a clipboard hung on the shop's pegboard (a new setting) */
  P(0, 0, 360, 417, '#6B4226'); for (let y = 6; y < 417; y += 14) for (let x = 6; x < 360; x += 14) P(x, y, 2, 2, '#4A2E1B');
  P(0, 417, 360, 223, NIGHT);
  P(16, 82 + up, 332, 192, INK); P(14, 80 + up, 332, 192, '#8C5A33'); P(18, 92 + up, 324, 176, CREAM);
  P(150, 74 + up, 60, 14, GREY); P(156, 76 + up, 48, 4, '#C9CCD3');
  if (up !== 0) return false;
  /* design r1: the headline set larger and every line wrapped at the card's full width */
  k.text('FOR WHOEVER ANSWERS THE PHONES', 72, 290, {size: 48, color: '#2F6F67'});
  k.text('NEW LEAD?', 72, 352, {size: 84, color: INK});
  k.text('CALL IT BACK FIRST.', 72, 444, {size: 84, color: RED});
  k.text('NO ANSWER? TEXT THIS:', 72, 548, {size: 52, color: '#4A4E5A'});
  P(22, 202, 316, 50, '#E6F2EF'); P(22, 202, 3, 50, TEAL);
  ['Hi, it\'s [shop] about your [job].', 'Call or text me back here.'].forEach((s, i) => k.text(s, 90, 620 + i * 64, {size: 52, color: INK}));
  exampleTag(d, 222, 252);
  return true;
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'CALL IT BACK FIRST',
  sendLine: 'Send this to whoever answers the phones.',
  transitions: {receipt: 'mosaic', send: 'levelselect', race: 'dissolve', fast: 'fade4', button: 'gameover'},
  trauma: {},
  sections: {
    /* ---- hook: frame 0 is the cover (the roof, the plate, the tag); 0.9 s the phone close-up buzzes; 2.4 s back out  */
    /* wide with Snow and the phone beside him; on "charged" the sky turns red and CHARGED stamps.                     */
    hook: (k, T) => {
      const d = px(k), tClose = 0.6, tWide = 2.4, tCh = wordT(k, 'hook', /^charged/i, 8.0) - 0.15;
      if (T < tClose) {
        roof(k, d); topPlate(k, d, 'CHARGED BEFORE', 'YOU EVEN LOOKED', -1);
        phone(k, d, 220, 200, 1.4, {note: true}); exampleTag(d, 220, 186);
        d.P(96, 151, 168, 19, NIGHT); k.text('Source: Angi Leads FAQ', 540, 460, {size: 44, color: CREAM, align: 'center'});   /* design r0: on an ink strip, 4.5:1 */
        return host(k, 'point', 0.75);
      }
      if (T < tWide) {   /* the close-up: the phone fills the band, buzzing */
        roof(k, d); phone(k, d, 90, 100, 3, {note: true, detail: true, buzz: true}); exampleTag(d, 104, 92);
        return {hostPose: 'stand', hostScale: 0.55, hostX: 150};
      }
      const red = T >= tCh;
      roof(k, d, {red}); phone(k, d, 220, 200, 1.4, {note: true, detail: true, buzz: !red}); exampleTag(d, 220, 186);
      if (red) stampBox(k, 'CHARGED', 690, 412, tCh, {color: RED, freeze: 4});   /* render critic r0: clear of the EXAMPLE tag */
      return host(k, red ? 'shrug' : 'point', 0.75);
    },

    /* ---- receipt (design r0): Angi's own lines on a big phone held up over the roof; quote one just before "you're */
    /* charged", quote two on "four"; four phones ring under it ---- */
    receipt: (k, T) => {
      const t0 = k.S('receipt'), tFour = wordT(k, 'receipt', /^four/i, 8.0) - 0.25, tQ1 = wordT(k, 'receipt', /^you'?re$/i, 2.4) - 0.45;
      const d = px(k), {P} = d;
      phonePage(k, d, t0, tQ1, tFour - 0.1);
      if (T >= tFour) {
        if (T >= tFour) P(130, 292, 168, 22, NIGHT);   /* design r1: a dark plate, 4.5:1 */
        k.slam('UP TO 4 PROS', 640, 884, tFour, {size: 52, color: GOLD, align: 'center', drop: INK, from: 0.3});
      }
      return host(k, T >= tFour ? 'point' : null);
    },

    /* ---- send: the new lead card goes up whole, then holds still while the voice reads it (cues.md [send]) ---- */
    send: (k, T) => {
      const d = px(k), up = leadCard(k, d, k.S('send')), tCall = wordT(k, 'send', /^call$/i, 4.0) - 0.25, tText = wordT(k, 'send', /^text$/i, 8.0) - 0.25;
      if (up && T >= tCall) k.sweep(72, 534, k.measure('CALL IT BACK FIRST.', {size: 84}), 6, tCall, {color: 'accent'});   /* design r0: the card moves on its words */
      if (up && T >= tText) k.sweep(90, 740, k.measure('Call or text me back here.', {size: 52}), 6, tText, {color: 'accent'});
      return host(k, up ? 'point' : null, 0.75);
    },

    /* ---- race: the dispatch board: four pins drop around one house, four routes draw in toward it (the race) ---- */
    race: (k, T) => {
      const t0 = k.S('race'), tRace = wordT(k, 'race', /^race/i, 3.0) - 0.3, tOne = wordT(k, 'race', /^homeowner/i, 4.0) - 0.3;
      const home = [0.55, 0.52], from = [[0.1, 0.15], [0.9, 0.2], [0.12, 0.85], [0.88, 0.88]];
      const r = k.sets.dispatch({pins: [{x: home[0], y: home[1], at: t0 + 0.1, c: GOLD}].concat(from.map((p, i) => ({x: p[0], y: p[1], at: t0 + 0.3 + i * 0.15, c: TEAL}))),
        routes: from.map((p, i) => ({pts: [p, [p[0], home[1]], home], at: tRace + i * 0.12, dur: 1.6, c: [RED, ORANGE, TEAL, SKY][i]}))});
      const a = (r && r.area) || {x: 60, y: 900, w: 840, h: 200};
      k.slam('UP TO 4 PROS', 640, 935, tRace, {size: 52, color: CREAM, align: 'center', drop: INK, from: 0.3});   /* render critic r0: off the shelf edge and the mug */
      k.slam('ONE HOMEOWNER', 588, 600, tOne, {size: 52, color: INK, align: 'center', drop: CREAM, from: 0.3});   /* beside the home pin, on the map */
      return host(k, T >= tOne ? 'point' : null);
    },

    /* ---- fast: the street set, our van rolls and brakes at the job sign on "fast" ---- */
    fast: (k, T) => {
      const t0 = k.S('fast'), tFast = wordT(k, 'fast', /^fast/i, 3.0) - 0.6;
      const r = k.sets.street({t0, speed: 1, stopAt: tFast, stopDur: 0.8, sign: 'JOB', van: true});
      const a = r.area || {x: 60, y: 252, w: 888, h: 348};
      k.slam('HOW FAST', a.x + a.w / 2, a.y + 24, t0 + 0.2, {size: 66, color: CREAM, align: 'center', drop: INK, from: 0.3});
      k.slam('YOU CALL BACK', a.x + a.w / 2, a.y + 110, tFast - 0.2, {size: 66, color: GOLD, align: 'center', drop: INK, from: 0.3});
      return host(k);
    },

    /* ---- button: the level-up: the bar fills, CARD READY on "ground", the card's two lines land as perks ---- */
    button: (k, T) => {
      const t0 = k.S('button'), tStay = wordT(k, 'button', /^stay/i, 2.0) - 0.3, tGround = wordT(k, 'button', /^ground/i, 3.4) - 0.3;
      k.sets.levelup({from: 0, to: 100, max: 100, at: t0 + 0.1, dur: Math.max(1.0, tGround - t0 - 0.2), levelAt: tGround, level: 1, text: 'CARD READY',
        stats: [{text: 'CALL IT BACK FIRST', at: tGround + 0.5}, {text: 'NO ANSWER? TEXT', at: tGround + 0.9}]});
      if (T < tGround) { k.slam('THE NEW LEAD CARD', 540, 330, t0 + 0.1, {size: 66, color: GOLD, align: 'center', drop: INK, from: 0.3});   /* design r0: the band is never empty */
        }
      { const d = px(k), up = d.ease(t0 + 0.3, 8, 120), x = 128, y = 232 + up;   /* design r1: a mini copy of the clipboard card fills the band */
        if (T < tGround) { d.P(x + 2, y + 2, 104, 58, INK); d.P(x, y, 104, 58, '#8C5A33'); d.P(x + 4, y + 6, 96, 48, CREAM); d.P(x + 40, y - 3, 24, 6, GREY);
          d.P(x + 10, y + 12, 50, 4, INK); d.P(x + 10, y + 20, 80, 5, RED); d.P(x + 10, y + 30, 60, 3, '#4A4E5A'); d.P(x + 8, y + 37, 88, 12, '#E6F2EF'); d.P(x + 12, y + 40, 70, 2, INK); d.P(x + 12, y + 45, 56, 2, INK); } }
      return host(k, T >= tGround + 0.4 ? 'wave' : (T >= tStay ? 'point' : null));
    },
  },
};

/* a faint dither drifts down the empty lower band of every scene, below the host and every text, so no stretch goes   */
/* still (code QA, flat). It never crosses the send card (band y 84 to 270).                                          */
const drift = (k) => { const d = px(k), off = Math.floor(k.T * 30) % 16; for (let y = 418 - 16 + off; y < 640; y += 16) { const y0 = Math.max(418, y), y1 = Math.min(640, y + 8); if (y1 > y0) d.P(0, y0, 360, y1 - y0, '#2B2033'); } };
for (const [n, f] of Object.entries(window.SCENE.sections)) window.SCENE.sections[n] = (k, T) => { const r = f(k, T); drift(k); return r; };
