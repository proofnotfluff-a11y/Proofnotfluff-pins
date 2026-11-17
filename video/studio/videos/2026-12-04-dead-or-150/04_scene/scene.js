/* 2026-12-04-dead-or-150 (v4 call), from the v4 template (verdict) and 2026-12-01-where-100-goes, its helpers kept whole   */
/* (_shared/formats.md "v4"). Rules the lint holds: every row size 132 or more; words inside x 40 to 1040, y 250 to 1170;   */
/* nothing unchanged over 4 s; a plate gives way to its stamp at the stamp's own start (t0 minus its drop). The cast has  */
/* no walk: change the pose or cut. Close shots put the feet far below the frame so faces sit between y 700 and 1100.     */
/* Plumber one is the studio's plumber; plumber two is recolored every time he is drawn (blue cap, grey jacket, no beard) */
/* so the two never read as one person (brief staging: never the same person twice).                                     */
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', DTEAL = '#2F6F67', NIGHT = '#1B1420', PLUM = '#2B2033', WINE = '#7A3442', SKY = '#87CEEB', BLUE = '#3B82C4', SLATE = '#4A4E5A', STEEL = '#6B7080';
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const WS = () => (window.WORDS && window.WORDS.words) || [];
/* the start of the first word matching re at or after a cue (id) or a time; dflt seconds after it when no word matches */
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
/* the low-res painter (360 x 640, one unit = 3 frame pixels) */
const px = (k) => {
  const ctx = k.ctx;
  return (x, y, w, h, c) => { x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h); if (w > 0 && h > 0 && c) { ctx.fillStyle = c; ctx.fillRect(x * 3, y * 3, w * 3, h * 3); } };
};
/* a centered plate of rows [[text, size, color], ...] with its top at y; returns its bottom */
const plate = (k, rows, y, o = {}) => {
  const cx = o.cx || 540, pad = o.pad || 36, gap = o.gap || 18;
  const hs = rows.map(([, z]) => Math.round(z * 1.0)), w = Math.ceil((Math.max(...rows.map(([s, z]) => k.measure(s, {size: z}))) + 2 * pad) / 6) * 6;
  const h = hs.reduce((a, b) => a + b, 0) + gap * (rows.length - 1) + 2 * pad - 6, x = Math.round((cx - w / 2) / 3) * 3;
  k.shape(k.rectPts(x + 9, y + 9, w, h, 0), {fill: INK, line: false});
  k.shape(k.rectPts(x, y, w, h, 0), {fill: o.bg || NIGHT, line: false});
  k.shape(k.rectPts(x, y, w, 9, 0), {fill: o.rule || ORANGE, line: false});
  let yy = y + pad;
  rows.forEach(([s, z, c], i) => { k.text(s, cx, yy, {size: z, color: c || CREAM, align: 'center'}); yy += hs[i] + gap; });
  return y + h;
};
/* the same plate landing as a stamp at t0 (a [sfx: stamp] cue there gives the hit-stop) */
const stampPlate = (k, rows, y, t0, o = {}) => {
  const hgt = rows.reduce((a, [, z]) => a + z, 0) + 18 * (rows.length - 1) + 66;
  return k.stampIn(t0, () => plate(k, rows, y, o), {at: [o.cx || 540, y + hgt], freeze: o.freeze, drop: o.drop});
};

/* the utility room: block wall, a ceiling pipe run, the gas water heater with its two pipes on top, a drip at the top  */
/* joint, a concrete floor. z 2 is a close shot of the same room (whole pixels); fx, fy the point it zooms on. o.fixed: */
/* the top pipe has its new copper piece; o.drip: water drops fall from the joint.                                       */
const utility = (k, dim = 0, z = 1, o = {}) => {
  const ctx = k.ctx, P = px(k), fx = o.fx || 540, fy = o.fy || 836;
  ctx.save();
  if (z !== 1) { ctx.translate(fx * (1 - z), fy * (1 - z)); ctx.scale(z, z); }
  P(0, 0, 360, 360, '#C9CCD3');
  for (let y = 10; y < 360; y += 20) { P(0, y, 360, 2, '#9AA0AD'); for (let x = (y / 20) % 2 ? 0 : 20; x < 360; x += 40) P(x, y - 10, 2, 10, '#9AA0AD'); }   /* block wall */
  P(0, 40, 360, 8, INK); P(0, 42, 360, 4, '#6B7080');   /* the ceiling pipe run */
  P(30, 150, 70, 54, INK); P(33, 153, 64, 48, '#4A4E5A'); P(36, 156, 58, 6, '#6B7080'); P(60, 175, 10, 10, RED);   /* the breaker box */
  /* the heater: two pipes up from its top to the run, the tank, the dome, the gas control, the label plate */
  P(160, 46, 6, 150, INK); P(161, 46, 4, 150, '#9AA0AD'); P(194, 46, 6, 150, INK); P(195, 46, 4, 150, '#9AA0AD');
  P(156, 186, 14, 6, INK); P(190, 186, 14, 6, INK);   /* the unions */
  if (o.fixed) { P(193, 150, 8, 36, INK); P(194, 151, 6, 34, '#D9A066'); P(194, 151, 2, 34, '#F7C873'); }   /* the new copper piece */
  P(140, 196, 80, 14, INK); P(143, 198, 74, 12, '#9AA0AD');
  P(136, 208, 88, 262, INK); P(139, 210, 82, 258, '#E6D3BC'); P(139, 210, 10, 258, '#FFF7EA'); P(209, 210, 12, 258, '#B39A88');
  P(160, 300, 40, 26, INK); P(162, 302, 36, 22, '#FFF7EA'); P(166, 307, 28, 3, '#6B7080'); P(166, 314, 20, 3, '#6B7080');   /* the label */
  P(158, 392, 44, 34, INK); P(161, 395, 38, 28, '#4A4E5A'); P(172, 401, 14, 14, RED); P(176, 405, 6, 6, INK);   /* the gas control */
  P(180, 426, 4, 30, '#B07A47');
  P(134, 466, 92, 8, INK);
  if (o.drip) {   /* drops from the top joint, one every 0.6 s */
    for (let i = 0; i < 3; i++) { const ph = ((k.T + i * 0.2) % 0.6) / 0.6; P(197, 192 + Math.floor(ph * 18) * 1, 3, 4, '#5B8FB9'); }
    P(190, 206, 18, 3, '#BDE6F5');
  }
  P(0, 470, 360, 170, '#9AA0AD'); for (let y = 470; y < 640; y += 40) P(0, y, 360, 2, '#6B7080');   /* the floor */
  P(120, 474, 120, 8, '#6B7080');
  ctx.restore();
  if (dim) P(0, 0, 360, 640, `rgba(18,13,20,${dim})`);
};
/* the cast. plumber one: the studio's plumber. plumber two: the same rig recolored, every time. */
const plumber1 = (k, x, sc, pose, o = {}) => k.snow(x, o.feet || 1150, Object.assign({scale: sc, pose, face: 1, talk: false}, o));
const TWO = {cap: BLUE, jacket: STEEL, jacketShade: SLATE, beard: '#F0B98D', beardHi: '#F0B98D'};
const plumber2 = (k, x, sc, pose, o = {}) => {
  const C = (window.LOOKS && window.LOOKS.arcade && window.LOOKS.arcade.c) || {}, keep = {};
  Object.keys(TWO).forEach((n) => { keep[n] = C[n]; C[n] = TWO[n]; });
  try { return k.snow(x, o.feet || 1150, Object.assign({scale: sc, pose, face: -1, talk: false}, o)); }
  finally { Object.keys(TWO).forEach((n) => { C[n] = keep[n]; }); }
};
const owner = (k, x, sc, pose, mood, o = {}) => k.client(x, o.feet || 1150, Object.assign({role: 'homeowner', scale: sc, pose, mood, face: -1}, o));
/* a phone at a figure's ear: hd the figure's returned head point, side +1 right of the face, -1 left */
const phoneAt = (k, hd, sc, side) => {
  const w = Math.round(30 * sc / 3) * 3, h = Math.round(60 * sc / 3) * 3, x = Math.round((hd[0] + side * 52 * sc - w / 2) / 3) * 3, y = Math.round((hd[1] - 6 * sc) / 3) * 3;
  k.shape(k.rectPts(x, y, w, h, 0), {fill: INK, line: false});
  k.shape(k.rectPts(x + 6, y + 6, w - 12, h - 18, 0), {fill: '#5B8FB9', line: false});
};
/* a split frame, one wall a side */
const split = (k, left, right) => {
  const P = px(k);
  P(0, 0, 180, 640, left); P(180, 0, 180, 640, right); P(178, 0, 4, 640, INK);
  for (let y = 20; y < 640; y += 22) { P(0, y, 178, 1, 'rgba(18,13,20,0.25)'); P(182, y + 11, 178, 1, 'rgba(18,13,20,0.25)'); }
};

window.SCENE = {
  look: 'arcade',
  v4: true,
  host: false,
  endCard: false,
  images: [],
  trauma: {'fix': 0.4, 'twist': 0.5},
  sections: {
    /* ---- hook: frame 0, the two prices on the two plumbers; 0.5 s the heater close with both prices; on "prices" back ---- */
    hook: (k, T) => {
      const tHeater = 0.5, tBack = Math.max(1.2, wordT(k, 'hook', /^prices/i, 1.3) - 0.05), tOne = k.S('hook.one');
      if (T >= tOne) return one(k, T);
      const L = [['$3,100', 132, RED]], R = [['$150', 132, GOLD]];
      if (T < tHeater || T >= tBack) {
        if (T >= tBack) k.cut(tBack);
        utility(k, 0.15, 1.6, {fx: 540, fy: 900, drip: true});
        plumber1(k, 250, 2.0, T >= tBack ? 'shrug' : 'clip', {feet: 1760});
        plumber2(k, 830, 2.0, T >= tBack ? 'talk' : 'stand', {feet: 1760});
        plate(k, L, 264, {cx: 270, rule: RED});
        plate(k, R, 264, {cx: 810, rule: GOLD});
      } else {
        k.cut(tHeater);
        utility(k, 0.1, 2.6, {fx: 540, fy: 820, drip: true});
        plate(k, L, 264, {cx: 270, rule: RED});
        plate(k, R, 264, {cx: 810, rule: GOLD});
      }
      return {host: false};
    },
  },
};
/* ---- hook.one: plumber one, close, at the heater: 2 MINUTES, then DEAD., then NEW ONE: $3,100 ---- */
const one = (k, T) => {
  const t0 = k.S('hook.one'), tPl = wordT(k, 'hook.one', /^plumber/i, 0.8) - 0.08, tTwo = wordT(k, 'hook.one', /^two/i, 1.5) - 0.1;
  const tDead = wordT(k, 'hook.one', /^dead/i, 2.5) - 0.12, tQuote = wordT(k, 'hook.one', /^thirty/i, 3.2) - 0.12;
  if (T < tPl) {   /* viewer r0: the voice names the homeowner first, so the picture does too */
    k.cut(t0);
    utility(k, 0.25, 2.0, {fx: 300, fy: 900, drip: true});
    owner(k, 540, 2.3, 'talk', 'cross', {feet: 1800, face: -1, talk: false});
    plate(k, [['HOMEOWNER', 132, TEAL]], 264, {rule: TEAL});
    return {host: false};
  }
  k.cut(tPl);
  utility(k, 0.25, 2.0, {fx: 400, fy: 900, drip: true});
  plumber1(k, 560, 2.3, T >= tQuote ? 'talk' : 'clip', {feet: 1800, talk: T >= tDead});
  if (T < tTwo - 0.06) plate(k, [['PLUMBER 1', 132, ORANGE]], 264);
  else if (T < tDead - 0.06) stampPlate(k, [['2 MINUTES', 132, CREAM]], 264, tTwo, {drop: 0.06});
  else if (T < tQuote - 0.06) stampPlate(k, [['DEAD.', 198, RED]], 264, tDead, {drop: 0.06, freeze: 3});
  else stampPlate(k, [['NEW ONE:', 132, CREAM], ['$3,100', 198, RED]], 264, tQuote, {drop: 0.06, freeze: 4});
  return {host: false};
};
Object.assign(window.SCENE.sections, {

    /* ---- call: the phone call, split: REENACTMENT, then her line (her side lit), then his (his side lit) ---- */
    call: (k, T) => {
      const t0 = k.S('call'), tHer = wordT(k, 'call', /^can/i, 0.9) - 0.1, tHim = wordT(k, 'call', /^i'?ll/i, 3.4) - 0.1;
      k.cut(t0);
      split(k, WINE, SLATE);
      const herTalk = T >= tHer && T < tHim, hisTalk = T >= tHim;   /* viewer r0: no dimming (it changed their colors) */
      const hd = owner(k, 290, 1.9, 'phone', herTalk ? 'cross' : 'calm', {feet: 1740, face: 1, talk: herTalk}).head;
      const hd2 = plumber2(k, 800, 1.9, 'stand', {feet: 1740, talk: hisTalk});
      phoneAt(k, hd2.head, 1.9, 1);
      if (T < tHer - 0.06) plate(k, [['REENACTMENT', 132, CREAM], ['THE CALL TO', 132, CREAM], ['PLUMBER 2', 132, BLUE]], 264, {rule: TEAL});
      else if (T < tHim - 0.06) stampPlate(k, [['HOMEOWNER', 132, TEAL], ['CAN YOU STILL', 132, CREAM], ['COME LOOK?', 132, CREAM]], 264, tHer, {drop: 0.06, rule: WINE});
      else stampPlate(k, [['PLUMBER 2', 132, BLUE], ["I'LL LOOK.", 132, CREAM]], 264, tHim, {drop: 0.06, rule: BLUE});
      void hd;
      return {host: false};
    },

    /* ---- fix (payoff by 40%): plumber two at the heater: IT WORKS, A LEAKING PIPE, $150; then her, hot water back ---- */
    fix: (k, T) => {
      const t0 = k.S('fix'), tPipe = wordT(k, 'fix', /^swapped/i, 1.4) - 0.1, tCash = wordT(k, 'fix', /^hundred/i, 3.6) - 0.35, tHot = wordT(k, 'fix', /^hot/i, 5.0) - 0.08;
      if (T < tHot) {
        k.cut(t0);
        utility(k, 0.2, 2.0, {fx: 640, fy: 760, drip: T < tPipe + 0.4, fixed: T >= tPipe + 0.4});
        plumber2(k, 470, 2.2, T >= tCash ? 'shrug' : 'point', {feet: 1780, face: 1, at: [700, 420], talk: false});
        const tFound = wordT(k, 'fix', /^found/i, 0.5) - 0.1;
        if (T < tFound - 0.06) plate(k, [['PLUMBER 2', 132, BLUE]], 264, {rule: BLUE});
        else if (T < tPipe - 0.06) stampPlate(k, [['IT WORKS.', 198, TEAL]], 264, tFound, {drop: 0.06});
        else if (T < tCash - 0.06) stampPlate(k, [['A LEAKING PIPE', 132, CREAM]], 264, tPipe, {drop: 0.06});
        else stampPlate(k, [['$150', 198, GOLD]], 264, tCash, {drop: 0.06, freeze: 4});
      } else {
        k.cut(tHot);
        utility(k, 0.3, 2.0, {fx: 300, fy: 900, fixed: true});
        owner(k, 540, 2.3, 'stand', 'smug', {feet: 1800, face: -1});
        const P = px(k), up = Math.floor((k.T * 6) % 3);
        P(206, 330, 22, 22, INK); P(208, 332, 18, 18, CREAM); P(226, 336, 6, 10, INK);   /* a mug */
        P(212, 318 - up * 3, 3, 8, CREAM); P(219, 314 - up * 3, 3, 8, CREAM);           /* its steam */
        plate(k, [['HOT WATER', 132, CREAM], ['IS BACK', 132, GOLD]], 264);
      }
      return {host: false};
    },

    /* ---- three: the homeowner on the phone: PLUMBER 3?, then CANCELLED ---- */
    three: (k, T) => {
      const t0 = k.S('three'), tCan = wordT(k, 'three', /^cancel/i, 1.0) - 0.1;
      k.cut(t0);
      utility(k, 0.3, 2.0, {fx: 300, fy: 900, fixed: true});
      owner(k, 540, 2.3, 'phone', 'calm', {feet: 1800, face: 1, talk: T >= tCan});
      if (T < tCan - 0.06) plate(k, [['PLUMBER 3?', 132, CREAM]], 264);
      else stampPlate(k, [['CANCELED', 132, RED]], 264, tCan, {drop: 0.06, freeze: 3});
      return {host: false};
    },

    /* ---- twist (70 to 85%): the tank, close: THE TANK, 10 YEARS OLD; then the heater a step back: SOME SAY / NEAR THE END ---- */
    twist: (k, T) => {
      const t0 = k.S('twist'), tTen = wordT(k, 'twist', /^ten/i, 0.8) - 0.12, tSome = wordT(k, 'twist', /^some/i, 2.0) - 0.08;
      if (T < tSome) {
        k.cut(t0);
        const zz = 2.6 + 0.2 * clamp((T - tTen) / 1.4);
        utility(k, 0.1, zz, {fx: 540, fy: 940, fixed: true});
        if (T < tTen - 0.06) plate(k, [['THE TANK', 132, CREAM]], 264);
        else stampPlate(k, [['10 YEARS OLD', 132, RED]], 264, tTen, {drop: 0.06, freeze: 4});
      } else {
        k.cut(tSome);
        utility(k, 0.15, 1.8 + 0.3 * clamp((T - tSome) / 2.0), {fx: 540, fy: 760, fixed: true});   /* facts r0 advisory: the age case is the commenters', not plumber one's; QA r0: a slow push-in (the shot sat flat 1.3 s) */
        plate(k, [['SOME SAY', 132, CREAM], ['NEAR THE END', 132, GOLD]], 264);
      }
      return {host: false};
    },

    /* ---- ask, the last frame: plumber one between the two readings of his quote: UPSELL? $3,100 against FAIR WARNING? 10 YEARS ---- */
    ask: (k, T) => {
      const t0 = k.S('ask'), tFair = wordT(k, 'ask', /^fair/i, 0.9) - 0.1;
      k.cut(t0);
      split(k, SLATE, DTEAL);
      plumber1(k, 540, 1.6, 'shrug', {feet: 1630});   /* facts r1 advisory: both readings hang on plumber one's verdict; faces between the plates and the captions */
      /* r1: side by side the two plates overlapped (both cannot fit at 132), so they stack */
      plate(k, [['UPSELL? $3,100', 132, RED]], 264, {bg: INK, rule: RED});
      if (T >= tFair) stampPlate(k, [['FAIR WARNING?', 132, TEAL], ['10 YEARS OLD', 132, CREAM]], 480, tFair, {bg: INK, rule: TEAL, drop: 0.06});
      return {host: false};
    },
});

/* ---- rule (viewer r0: the lesson gets its own beat before the question, tied to the tank's age) ---- */
window.SCENE.sections.rule = (k, T) => {
  const t0 = k.S('rule'), tShow = wordT(k, 'rule', /^show/i, 1.6) - 0.1;
  k.cut(t0);
  utility(k, 0.2, 1.6, {fx: 540, fy: 900, fixed: true});
  plumber1(k, 340, 1.6, T >= tShow ? 'clip' : 'talk', {feet: 1630, face: 1});   /* faces between the card (to y 873) and the captions (from y 1184) */
  owner(k, 760, 1.7, 'stand', 'calm', {feet: 1630, face: -1});
  if (T < tShow - 0.06) plate(k, [['OLD? SAY SO.', 132, CREAM]], 264);
  else stampPlate(k, [['SHOW WHAT', 132, CREAM], ['YOU TESTED', 198, GOLD], ['BEFORE REPLACE', 132, CREAM]], 264, tShow, {drop: 0.06, freeze: 4});
  return {host: false};
};
