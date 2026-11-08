/* Scene: Members go first (proven, our own version of research/PROVEN.md row 4; Nov 8, 2026). One function per top-  */
/* level cue in 03_cues/cues.md; every time from a cue start or a spoken word (wordT). Worlds: hook = the cover plate   */
/* over the dispatch board, the weather map (the cold front), the dispatch board filling with calls; turn = the call    */
/* queue, members jump the line; send = the plan card, held still; receipt = the ACHR News line, then the 87% hero over */
/* 100 houses (data.js); why = twelve month boxes, a coin in each; button = the dispatch board, the first truck routed  */
/* to the member. The cold night, the calls, the trucks and the plan are ours (EXAMPLE).                               */
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
const stampBox = (k, s, cx, y, t0, o = {}) => {
  const size = o.size || 66, c = o.color || GOLD, w = Math.round((Math.max(k.measure(s, {size}), o.sub ? k.measure(o.sub, {size}) : 0) + 54) / 6) * 6, h = size + 36 + (o.sub ? size + 12 : 0), x = Math.round((cx - w / 2) / 3) * 3;
  k.stampIn(t0, () => {
    k.shape(k.rectPts(x + 6, y + 6, w, h, 0), {fill: INK, line: false}); k.shape(k.rectPts(x, y, w, h, 0), {fill: o.bg || NIGHT, line: false});
    k.shape(k.rectPts(x + 6, y + 6, w - 12, 6, 0), {fill: c, line: false}); k.shape(k.rectPts(x + 6, y + h - 12, w - 12, 6, 0), {fill: c, line: false});
    k.shape(k.rectPts(x + 6, y + 6, 6, h - 12, 0), {fill: c, line: false}); k.shape(k.rectPts(x + w - 12, y + 6, 6, h - 12, 0), {fill: c, line: false});
    k.text(s, x + w / 2, y + 18, {size, color: c, align: 'center'}); if (o.sub) k.text(o.sub, x + w / 2, y + 30 + size, {size, color: c, align: 'center'});
  }, {at: [x + w / 2, y + h], freeze: o.freeze});
};
const exampleTag = (d, x, y) => { d.P(x, y, 128, 32, INK); d.P(x + 1, y + 1, 126, 30, ORANGE); d.tx('EXAMPLE', x + 64, y + 5, {size: 52, color: INK, align: 'center'}); };

const fadeSteps = (d, step) => { if (step <= 0) return; if (step >= 4) { d.P(0, 0, 360, 417, INK); return; } for (let j = 0; j < 417; j++) if (step >= 2 || j % 2 === 0) d.dith(0, j, 360, 1, INK, j % 2); if (step === 3) d.dith(0, 0, 360, 417, INK, 1); };

/* a shutter between rooms inside a cue (design: no plain cuts, and not the last lesson's blinds): eight ink columns   */
/* close from alternate ends over 3 frames and open over 3, never more than half dark                                  */
const shutter = (d, T, at, n = 3) => {
  const f = Math.floor((T - at) * 30 + 0.005); if (f < -n || f > n) return;
  const h = Math.round(208 * (1 - Math.abs(f) / (n + 0.5)));
  for (let i = 0; i < 8; i++) d.P(i * 45, i % 2 ? 417 - h : 0, 22, h, INK);
};
/* the question plate: two lines on a dark plate in the top band */
const plate = (k, d, a, b, t0, c = GOLD) => {
  d.win(14, 84, 332, 64, {base: '#253048', hi: '#3B82C4', lo: NIGHT, rule: '#3B82C4'});
  k.slam(a, 540, 266, t0, {size: 64, color: CREAM, align: 'center', drop: INK, from: 0.4});
  if (b) k.slam(b, 540, 340, t0 + 0.06, {size: 64, color: c, align: 'center', drop: INK, from: 0.4});
};
/* the call pins for the dispatch board: 40 calls spread over the city, landing a few per frame from t0 */
const CALLS = Array.from({length: 40}, (_, i) => ({x: 0.12 + 0.76 * hash(i + 3), y: 0.12 + 0.62 * hash(i + 71)}));
const MEMBER = [4, 17, 29];
/* three trucks parked in the yard strip under the map */
const trucks = (d, x, y, go = -1) => {
  for (let i = 0; i < 3; i++) {
    const X = x + i * 34 + (i === 0 && go >= 0 ? Math.min(60, go * 4) : 0);
    d.P(X, y + 8, 30, 12, INK); d.P(X + 1, y + 9, 20, 10, CREAM); d.P(X + 21, y + 11, 8, 8, TEAL); d.P(X + 2, y + 12, 18, 2, ORANGE);
    d.P(X + 4, y + 19, 6, 4, INK); d.P(X + 20, y + 19, 6, 4, INK);
  }
};
/* the call queue: six tickets; members (gold) move to the top at tUp */
const TICKETS = [['NO HEAT', 0], ['NO HEAT', 1], ['NO HEAT', 0], ['FURNACE OUT', 1], ['COLD HOUSE', 0]];
const queue = (k, d, t0, tUp, tCoin) => {
  const {P} = d, T = k.T, f = Math.floor((T - tUp) * 30), u = T < tUp ? 0 : eo(f / 8);
  P(0, 0, 360, 417, '#2B3A4E'); for (let y = (d.F >> 2) % 10 - 10; y < 417; y += 10) P(0, Math.max(0, y), 360, 2, '#25303F');
  const before = TICKETS.map((t, i) => i), mem = before.filter((i) => TICKETS[i][1]), rest = before.filter((i) => !TICKETS[i][1]), after = mem.concat(rest);
  TICKETS.forEach(([lab, m], i) => {
    const r0 = before.indexOf(i), r1 = after.indexOf(i), r = r0 + (r1 - r0) * u, land = d.ease(t0 + 0.1 + i * 0.08, 5, 40);
    const y = Math.round(140 + r * 36) + land, x = m && u > 0 && u < 1 ? 26 + Math.round(8 * Math.sin(u * Math.PI)) : 20;
    if (T < t0 + 0.1 + i * 0.08) return;
    P(x + 2, y + 2, 290, 30, INK); P(x, y, 290, 30, m && T >= tUp ? GOLD : CREAM); P(x, y, 8, 30, m && T >= tUp ? ORANGE : GREY);
    if (m && T >= tCoin) { const sx = Math.floor((T - tCoin) * 120) % 330 - 20; if (sx > 0 && sx < 250) P(x + sx, y + 2, 10, 26, '#FBE3A0'); }   /* r0: the shine runs under the words */
    k.text(String(r0 + 1), (x + 24) * 3, (y + 6) * 3, {size: 56, color: INK});
    k.text(lab, (x + 60) * 3, (y + 6) * 3, {size: 56, color: INK});
    if (m && T >= tUp) k.text('MEMBER', (x + 200) * 3, (y + 6) * 3, {size: 52, color: '#7A3442'});
    if (m && T >= tCoin) {   /* code QA r0 flat: the coin spins (4 frames) and a shine runs along the member ticket */
      const sp = [14, 10, 4, 10][Math.floor(d.F / 3) % 4]; P(x + 279 - sp / 2, y + 8, sp, 16, '#B07A47'); P(x + 280 - sp / 2, y + 10, Math.max(2, sp - 4), 12, GOLD);
    }
  });
};
/* the send card: the member plan on a paper sheet, held still; four steps, each marker lit on its words */
const STEPS = ['TWO TUNE-UPS A YEAR', 'MEMBERS FIRST WHEN IT BREAKS', 'A DISCOUNT ON REPAIRS', 'ONE PRICE, BILLED MONTHLY'];
const planCard = (k, d, t0, lit, shine = -1) => {
  const {P} = d, up = d.ease(t0 + 0.02, 5, 160);
  P(0, 0, 360, 417, '#3D2E45'); const so = d.F % 20; for (let x = so - 20; x < 360; x += 20) P(Math.max(0, x), 0, Math.max(0, Math.min(x + 10, 360) - Math.max(0, x)), 417, '#4E3A58');   /* code QA r1 flat: the stripes behind the card drift, the card never moves */
  P(16, 82 + up, 332, 254, INK); P(12, 78 + up, 336, 254, '#2B2033'); P(18, 86 + up, 324, 240, CREAM);
  P(18, 86 + up, 324, 26, '#7A3442');
  if (up !== 0) return false;
  if (shine > 0 && shine < 310) P(18 + shine, 86, 14, 26, '#9A4A5C');   /* r0: the header shine runs under the words */
  k.text('FOR WHOEVER DOES YOUR BOOKS', 72, 266, {size: 52, color: CREAM});
  k.text('THE MEMBER PLAN', 72, 352, {size: 84, color: INK});
  STEPS.forEach((s, i) => {
    const on = lit[i]; P(26, 152 + i * 34, 10, 26, on ? GOLD : SAND); P(28, 154 + i * 34, 6, 22, on ? ORANGE : SAND);
    k.text(String(i + 1), 132, 462 + i * 102, {size: 60, color: on ? INK : SLATE});
    k.text(s, 184, 462 + i * 102, {size: 54, color: on ? INK : SLATE});
  });
  P(24, 292, 312, 30, '#F4E6D3');
  P(26, 294, 120, 26, ORANGE); d.tx('EXAMPLE', 86, 297, {size: 48, color: INK, align: 'center'});
  k.text('OUR SUGGESTED PLAN', 500, 890, {size: 40, color: SLATE});
  return true;
};
/* The ACHR News line on a card, typed on, with its tag (the real screen, our drawing of it) */
const sourceCard = (k, d, t0, typeAt) => {
  const {P, win} = d, up = d.ease(t0, 6, 30), n0 = k.data.numbers.pay.shown;
  win(14, 84 + up, 332, 240, {base: CREAM, hi: '#FFFFFF', lo: SAND, rule: false});
  P(14, 84 + up, 332, 46, '#7A3442');
  k.text('THE ACHR NEWS', 72, 268 + up * 3, {size: 52, color: CREAM});
  k.text('SURVEY', 72, 322 + up * 3, {size: 52, color: GOLD});
  k.wrap('Source: The ACHR News with Clear Seas Research, Dec 2023. Read Nov 8, 2026.', {size: 48}, 840)
    .forEach((s, i) => k.text(s, 72, 778 + i * 52 + up * 3, {size: 48, color: SLATE}));
  if (up) return;
  const lines = ['"Per the survey, ' + n0, 'of homeowners are willing', 'to pay either $100 or $200', 'annually for a service', 'agreement."'];
  lines.forEach((s, i) => k.text(s, 72, 410 + i * 68, {size: 60, color: INK}));
};
/* 100 houses in a 10 x 10 grid, the first n lit (n from data.js), filling a few per frame from t0 */
const houseGrid = (k, d, n, t0) => {
  const {P} = d, lit = Math.min(n, Math.max(0, Math.floor((k.T - t0) * 90)));
  for (let i = 0; i < 100; i++) {
    const x = 44 + (i % 10) * 27, y = 240 + Math.floor(i / 10) * 9, on = i < lit;
    P(x + 6, y, 10, 2, on ? '#E2633B' : '#3D2E45'); P(x + 3, y + 2, 16, 2, on ? '#E2633B' : '#3D2E45');
    P(x + 3, y + 4, 16, 4, on ? GOLD : '#2B2033'); if (on) P(x + 9, y + 5, 3, 3, INK);
  }
};
/* twelve month boxes; a coin drops into each, one after another from t0 */
const MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
const monthRow = (k, d, t0, every) => {
  const {P} = d, T = k.T;
  P(0, 0, 360, 417, '#1F2A40'); for (let y = (d.F >> 2) % 8 - 8; y < 417; y += 8) P(0, Math.max(0, y), 360, 2, '#24304A');
  MONTHS.forEach((m, i) => {
    const x = 20 + (i % 6) * 48, y = 140 + Math.floor(i / 6) * 112, at = t0 + i * every, slow = i === 3 || i === 4 || i === 9;
    P(x + 2, y + 2, 42, 66, INK); P(x, y, 42, 66, slow ? '#4A4E5A' : '#2F6F67');
    k.text(m, (x + 21) * 3, (y + 6) * 3, {size: 48, color: CREAM, align: 'center'});
    if (T >= at - 0.2) {
      const fall = T < at ? Math.round((at - T) * 160) : 0, bounce = T >= at && T < at + 0.1 ? -2 : 0;
      P(x + 13, y + 38 - fall + bounce, 16, 18, '#B07A47'); P(x + 15, y + 40 - fall + bounce, 12, 14, GOLD);
    }
  });
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'MEMBERS GO FIRST',
  sendLine: 'Send this to whoever does your books this week.',
  transitions: {turn: 'dissolve', send: 'levelselect', receipt: 'mosaic', why: 'fade4', button: 'gameover'},
  trauma: {},
  sections: {
    /* ---- hook: frame 0 is the cover plate over the board; 0.6 s shutter to the weather map; on "Forty" a shutter to */
    /* the dispatch board, the calls land and count to 40; the question on "who" ---- */
    hook: (k, T) => {
      const d = px(k), tMap = 0.6, tBoard = wordT(k, 'hook', /^forty/i, 2.6) - 0.2, tWho = wordT(k, 'hook', /^who$/i, 5.2) - 0.25;
      if (T < tMap) {
        k.sets.dispatch({pins: CALLS.slice(0, 12).map((p) => ({x: p.x, y: p.y, at: -1, c: RED}))});
        d.win(14, 84, 332, 232, {base: '#253048', hi: '#3B82C4', lo: NIGHT, rule: '#3B82C4'});
        k.text('40 CALLS', 540, 272, {size: 230, color: ORANGE, align: 'center', drop: INK});
        k.text('3 TRUCKS', 540, 520, {size: 110, color: CREAM, align: 'center', drop: INK});
        k.text('WHO GOES FIRST?', 540, 672, {size: 84, color: GOLD, align: 'center', drop: INK});
        exampleTag(d, 116, 280);
        shutter(d, T, tMap);
        return host(k, 'point', 0.55);
      }
      if (T < tBoard) {
        k.sets.weather({title: ' ', fronts: [{kind: 'cold', at: tMap, dur: 1.4, x0: 0.05, x1: 0.8}], icons: [{kind: 'snow', x: 0.45, y: 0.4, at: tMap + 0.5, label: 'SNOW'}], months: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], monthsAt: 99});
        exampleTag(d, 180, 90);
        d.P(14, 226, 332, 96, INK); d.P(16, 228, 328, 92, '#253048');
        k.slam('FIRST COLD NIGHT', 450, 716, tMap + 0.15, {size: 96, color: CREAM, align: 'center', drop: INK, from: 0.4});
        { const ring = Math.floor(d.F / 4) % 2, px0 = 268 + (ring ? 1 : -1);   /* design r0: the panel is used: a phone starts to ring */
          d.P(px0, 240, 30, 56, INK); d.P(px0 + 2, 242, 26, 52, '#2B2033'); d.P(px0 + 4, 246, 22, 34, ring ? GOLD : '#3B82C4'); d.P(px0 + 11, 286, 8, 4, GREY);
          if (ring) { d.P(px0 - 8, 250, 3, 10, GOLD); d.P(px0 - 14, 246, 3, 18, GOLD); d.P(px0 + 35, 250, 3, 10, GOLD); d.P(px0 + 41, 246, 3, 18, GOLD); } }
        shutter(d, T, tMap); shutter(d, T, tBoard);
        return host(k, null, 0.55);
      }
      const lit = Math.min(40, Math.max(0, Math.floor((T - tBoard - 0.1) * 60)));
      k.sets.dispatch({pins: CALLS.slice(0, Math.max(1, lit)).map((p, i) => ({x: p.x, y: p.y, at: tBoard + 0.1 + i / 60, c: RED}))});
      if (T < tWho) {
        d.P(14, 84, 160, 40, INK); d.P(16, 86, 156, 36, NIGHT);
        k.text(String(lit), 72, 270, {size: 56, color: lit >= 40 ? ORANGE : CREAM, lint: false});
        k.text('NO-HEAT CALLS', 186, 268, {size: 48, color: CREAM});
      }
      exampleTag(d, 14, 280);
      if (T >= tWho) { d.P(14, 84, 332, 44, INK); d.P(16, 86, 328, 40, '#253048'); k.slam('WHO GETS A TECH FIRST?', 540, 266, tWho, {size: 64, color: GOLD, align: 'center', drop: INK, from: 0.4}); }   /* r0: over the counter, never over the EXAMPLE tag */
      d.P(150, 280, 110, 30, INK); d.P(152, 282, 106, 26, '#2B2033'); trucks(d, 156, 282);
      shutter(d, T, tBoard);
      return host(k, T >= tWho ? 'shrug' : null);
    },

    /* ---- turn: the call queue in call order; on "member" the members jump the line; MEMBERS FIRST on "first" ---- */
    turn: (k, T) => {
      const t0 = k.S('turn'), d = px(k), tUp = wordT(k, 'turn', /^member$/i, 2.4) - 0.2, tFirst = wordT(k, 'turn', /^first\.?$/i, 4.0, ) , tPay = wordT(k, 'turn', /^pay$/i, 5.4) - 0.2;
      const tF2 = WS().filter((w) => w.start >= tUp && /^first/i.test(w.w))[0];
      queue(k, d, t0, tUp, tPay);
      d.P(14, 84, 332, 36, INK); d.P(16, 86, 328, 32, NIGHT);
      const tStamp = (tF2 ? tF2.start : tUp + 1.2) - 0.2;
      if (T < tStamp) k.text(T < tUp ? 'CALL ORDER' : 'MEMBER PLAN', 66, 266, {size: 56, color: T < tUp ? CREAM : GOLD});
      exampleTag(d, 188, 86);
      if (T >= tStamp) stampBox(k, 'MEMBERS FIRST', 290, 252, tStamp, {color: '#7A3442', bg: CREAM, size: 56, freeze: 4});
      return host(k, T >= tUp ? 'point' : null);
    },

    /* ---- send: the plan card goes up whole, then holds still; each step's marker lights on its words ---- */
    send: (k, T) => {
      const t0 = k.S('send'), d = px(k), w = (re, dd) => wordT(k, 'send', re, dd) - 0.25;
      const at = [w(/^two$/i, 3.4), w(/^members$/i, 4.8), w(/^discount$/i, 6.4), w(/^price/i, 8.0)];
      const tMon0 = w(/^monthly/i, 9.0), shine = T >= tMon0 ? Math.floor(((T - tMon0) % 0.8) * 420) - 30 : -1;
      const up = planCard(k, d, t0, at.map((a) => T >= a), shine);
      /* code QA r0 flat: a sweep under each step on its words, the last on "monthly" (the card itself never moves) */
      const tMon = w(/^monthly/i, 9.0);
      STEPS.forEach((st, i) => { const a = i === 3 ? tMon : at[i]; if (up && T >= a) k.sweep(184, 462 + i * 102 + 60, k.measure(st, {size: 54}), 6, a, {color: 'accent'}); });
      if (up && T >= tMon) {   /* code QA r1 flat: after the last step a shine runs along the card's header bar, every 0.8 s */
        const ck = Math.min(6, Math.floor((T - tMon) * 20)); for (let i = 0; i < ck; i++) d.P(38 + i * 2, 262 - (i < 3 ? -i * 2 : (i - 3) * 3 - 4), 3, 3, DTEAL);
      }
      if (up && T >= w(/^books/i, 2.6)) k.sweep(72, 266 + 58, k.measure('FOR WHOEVER DOES YOUR BOOKS', {size: 52}), 6, w(/^books/i, 2.6), {color: 'accent'});
      return host(k, up ? 'point' : null);
    },

    /* ---- receipt: the ACHR News line typed on; on "eighty-seven" a four-step fade to the 87% hero over 100 houses ---- */
    receipt: (k, T) => {
      const t0 = k.S('receipt'), d = px(k), n = k.data.numbers.pay, tE = wordT(k, 'receipt', /^eighty/i, 5.0), tPct = wordT(k, 'receipt', /^percent/i, 5.8);
      const tSlot = tE - 0.9, sym = n.shown.split('');
      if (T < tSlot) {
        d.P(0, 0, 360, 417, '#253048'); for (let y = (d.F >> 2) % 8 - 8; y < 417; y += 8) d.P(0, Math.max(0, y), 360, 3, NIGHT);
        sourceCard(k, d, t0, t0);
        shutter(d, T, tSlot, 4);
        return host(k);
      }
      k.sets.slots({t0: tSlot, stops: [tE - 0.1, tE + 0.25, tPct - 0.1], symbols: sym, label: 'OF THOSE ASKED'});
      shutter(d, T, tSlot, 4);   /* design r1: drawn over the slot room, 8 frames, so the wipe shows */
      const tPlate = tPct + 0.3;
      if (T >= tPlate) {
        const up = d.ease(tPlate, 5, 20);
        d.P(16, 244 + up, 332, 76, INK); d.P(14, 242 + up, 332, 76, NIGHT); d.P(14, 242 + up, 332, 3, GOLD);
        k.text('WOULD PAY $100 OR $200', 540, 742 + up * 3, {size: 56, color: CREAM, align: 'center'});
        k.text('A YEAR FOR A SERVICE AGREEMENT', 540, 808 + up * 3, {size: 48, color: GOLD, align: 'center'});
        k.text('REPORTED DEC 2023', 540, 870 + up * 3, {size: 48, color: SAND, align: 'center'});
      }
      return host(k, T >= tPct ? 'point' : null);
    },

    /* ---- why: a coin drops into each month in turn; SLOW WEEKS TOO lands on "slow" ---- */
    why: (k, T) => {
      const t0 = k.S('why'), d = px(k), tSlow = wordT(k, 'why', /^slow/i, 3.2) - 0.2;
      monthRow(k, d, t0 + 0.3, 0.28);
      d.P(14, 84, 332, 40, INK); d.P(16, 86, 328, 36, NIGHT);
      k.text('BILLED MONTHLY', 66, 268, {size: 60, color: GOLD});
      exampleTag(d, 180, 88);
      if (T >= tSlow) stampBox(k, 'SLOW WEEKS TOO', 540, 640, tSlow, {color: GOLD, bg: NIGHT, size: 72, freeze: 4});
      k.sets.hud({coins: {at: t0 + 0.2, dur: 5.2, n: 28, x0: 24, x1: 300, floor: 334}});
      return host(k, T >= tSlow ? 'point' : null);
    },

    /* ---- button: the board again; the first truck's route draws to the gold member pin on "first truck" ---- */
    button: (k, T) => {
      const t0 = k.S('button'), d = px(k), tFirst = wordT(k, 'button', /^first$/i, 3.0) - 0.25;
      const m = CALLS[MEMBER[0]];
      k.sets.dispatch({pins: CALLS.map((p, i) => ({x: p.x, y: p.y, at: -1, c: MEMBER.includes(i) ? GOLD : RED})),
        routes: [{pts: [[0.1, 0.9], [m.x, 0.9], [m.x, m.y]], at: t0 + 0.6, dur: Math.max(0.6, tFirst - t0 - 0.6), c: GOLD}]});
      exampleTag(d, 14, 280);
      if (T >= tFirst) stampBox(k, 'FIRST TRUCK: MEMBER', 540, 640, tFirst, {color: '#7A3442', bg: CREAM, size: 66, freeze: 4});
      return host(k, T >= tFirst ? 'wave' : null);
    },
  },
};
/* a faint dither drifts down the empty lower band of every scene, below the host and every text, so no stretch goes   */
/* still (code QA, flat). It never crosses the send card (band y 84 to 336).                                          */
const drift = (k) => { const d = px(k), off = Math.floor(k.T * 30) % 16; for (let y = 418 - 16 + off; y < 640; y += 16) { const y0 = Math.max(418, y), y1 = Math.min(640, y + 8); if (y1 > y0) d.P(0, y0, 360, y1 - y0, '#2B2033'); } };
for (const [n, f] of Object.entries(window.SCENE.sections)) window.SCENE.sections[n] = (k, T) => { const r = f(k, T); drift(k); return r; };
