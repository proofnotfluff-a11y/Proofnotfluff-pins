/* 2026-12-01-where-100-goes (v4 invoice), from the v4 template (verdict), its helpers kept whole (_shared/formats.md   */
/* "v4"). For a new lesson keep the helpers (wordT, px, plate, stampPlate, the cast) and change: the place (yard), the     */
/* rows on each plate, the words the times hang on, and the cue ids to match 03_cues/cues.md. Rules the lint holds: every */
/* row size 132 or more; words inside x 40 to 1040, y 250 to 1170; nothing unchanged over 4 s; no word set that drops out */
/* for a frame (switch a plate for its stamp at the stamp's own start: t0 minus its drop). The cast has no walk: never  */
/* move a figure sideways (it reads as sliding); change the pose or cut. Close shots put the feet far                    */
/* below the frame (feet 1700 or so) so the faces sit between y 700 and 1100 and the plates own the band above them.     */
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', DTEAL = '#2F6F67', NIGHT = '#1B1420', PLUM = '#2B2033', WINE = '#7A3442', SKY = '#87CEEB';
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
/* a centered plate of rows [[text, size, color], ...] with its top at y; returns its bottom. Sizes are whole steps of */
/* the display face (66, 132, 198) so the pixels stay square. */
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
/* the same plate landing as a stamp at t0 (put a [sfx: stamp] cue there for the hit-stop) */
const stampPlate = (k, rows, y, t0, o = {}) => {
  const hgt = rows.reduce((a, [, z]) => a + z, 0) + 18 * (rows.length - 1) + 66;
  return k.stampIn(t0, () => plate(k, rows, y, o), {at: [o.cx || 540, y + hgt], freeze: o.freeze, drop: o.drop});
};

/* the kitchen: a back wall, a window, upper cabinets, a counter with the sink, a water heater in the corner, a tile floor. */
/* z 2 is the close shot: the same kitchen at twice the size (whole pixels).                                              */
const kitchen = (k, dim = 0, z = 1) => {
  const ctx = k.ctx, P = px(k);
  ctx.save();
  if (z !== 1) { ctx.translate(-540, -836); ctx.scale(z, z); }
  P(0, 0, 360, 330, '#E9DCC4'); for (let y = 12; y < 330; y += 18) P(0, y, 360, 1, '#D8C7AA');   /* the wall */
  P(118, 118, 124, 92, INK); P(121, 121, 118, 86, SKY); P(121, 175, 118, 32, '#BDE6F5'); P(179, 121, 3, 86, INK); P(121, 162, 118, 3, INK);   /* the window */
  P(286, 140, 4, 4, GOLD);
  P(0, 70, 108, 70, INK); P(3, 73, 102, 64, DTEAL); P(54, 73, 2, 64, INK); P(44, 100, 3, 10, GOLD); P(63, 100, 3, 10, GOLD);   /* upper cabinets */
  P(252, 70, 108, 70, INK); P(255, 73, 102, 64, DTEAL); P(306, 73, 2, 64, INK); P(296, 100, 3, 10, GOLD); P(315, 100, 3, 10, GOLD);
  P(0, 236, 300, 10, INK); P(0, 239, 300, 6, '#C9B79C');   /* the counter */
  P(0, 246, 300, 84, INK); P(3, 249, 294, 81, TEAL); for (let x = 75; x < 300; x += 75) P(x, 249, 2, 81, DTEAL);
  P(150, 226, 64, 13, INK); P(153, 229, 58, 7, '#9AA0AD'); P(178, 204, 4, 24, '#6B7080'); P(178, 204, 16, 4, '#6B7080');   /* the sink and faucet */
  P(306, 196, 46, 134, INK); P(309, 199, 40, 128, '#B8BCC6'); P(309, 199, 40, 8, '#9AA0AD'); P(320, 176, 4, 22, '#8C5A33'); P(334, 176, 4, 22, '#8C5A33');   /* the water heater */
  P(320, 262, 18, 8, RED);
  P(0, 330, 360, 310, '#C9B79C'); for (let y = 330; y < 640; y += 24) P(0, y, 360, 2, '#B09A7C');   /* the floor */
  for (let x = 0; x < 360; x += 36) P(x, 330, 2, 310, '#B09A7C');
  ctx.restore();
  if (dim) P(0, 0, 360, 640, `rgba(18,13,20,${dim})`);
};
/* the cast. Close shots from the waist up, feet far below the frame (feet 1700 or so), faces between y 700 and 1100. */
const plumber = (k, x, sc, pose, o = {}) => k.snow(x, o.feet || 1150, Object.assign({scale: sc, pose, face: 1, talk: false}, o));
const owner = (k, x, sc, pose, mood, o = {}) => k.client(x, o.feet || 1150, Object.assign({role: 'homeowner', scale: sc, pose, mood, face: -1}, o));
/* a line struck through the last row of a plate whose bottom is b (row size z), drawn left to right over 0.25 s from t */
const strike = (k, s, z, b, t) => { const w = k.measure(s, {size: z}); k.shape(k.rectPts(540 - w / 2 - 12, b - 36 - z / 2, Math.round((w + 24) * clamp((k.T - t) / 0.25) / 3) * 3, 15, 0), {fill: RED, line: false}); };

window.SCENE = {
  look: 'arcade',
  v4: true,
  host: false,
  endCard: false,
  images: [],
  trauma: {'pay': 0.5, 'twist': 0.6},
  sections: {
    /* ---- hook: frame 0 is the fight, close: she folds her arms at him, $100 BILL / ALL HIS?; at 0.5 s she argues; ---- */
    /* on "kept" a cut to her alone ---- */
    hook: (k, T) => {
      const tArg = 0.5, tSolo = Math.max(1.0, wordT(k, 'hook', /^kept/i, 1.2) - 0.05), tOwn = k.S('hook.owner');
      const rows = [['$100 BILL', 198, GOLD], ['ALL HIS?', 132, RED]];
      if (T >= tOwn) return holdUp(k, T);
      if (T < tSolo) {
        kitchen(k, 0.15, 2);
        owner(k, 260, 2.1, T >= tArg ? 'argue' : 'refuse', 'cross', {feet: 1720, face: 1});
        plumber(k, 820, 1.9, 'clip', {feet: 1720, face: -1});
        plate(k, rows, 264);
      } else {
        k.cut(tSolo);
        kitchen(k, 0.22, 2);
        owner(k, 540, 2.4, 'argue', 'cross', {feet: 1800, face: 1, talk: T < tOwn - 0.2});
        plate(k, rows, 264);
      }
      return {host: false};
    },

  },
};
/* ---- hook.owner (inside hook): the plumber tells it; on "held" she is on the phone and the job goes on hold ---- */
const holdUp = (k, T) => {
      const t0 = k.S('hook.owner'), tHeld = wordT(k, 'hook.owner', /^held/i, 1.5) - 0.1;
      if (T < tHeld) {
        k.cut(t0);
        kitchen(k, 0.3, 2);
        plumber(k, 540, 2.2, 'talk', {feet: 1780, talk: true});
        plate(k, [['HIS ACCOUNT:', 132, CREAM]], 264);
      } else {
        k.cut(tHeld);
        kitchen(k, 0.3, 2);
        owner(k, 560, 2.4, 'phone', 'cross', {feet: 1800, face: -1});
        stampPlate(k, [['HIS ACCOUNT:', 132, CREAM], ['JOB ON HOLD', 132, RED]], 264, tHeld, {drop: 0.06, freeze: 4});
      }
      return {host: false};
};
Object.assign(window.SCENE.sections, {

    /* ---- pay: the answer by 40%: his example, a one-truck shop; on "nine" $9 LEFT lands ---- */
    pay: (k, T) => {
      const t0 = k.S('pay'), tNine = wordT(k, 'pay', /^nine/i, 2.0) - 0.15;
      k.cut(t0);
      kitchen(k, 0.3, 2);
      plumber(k, 560, 2.2, T >= tNine ? 'shrug' : 'clip', {feet: 1780, talk: T < tNine});
      if (T < tNine - 0.06) plate(k, [['HIS EXAMPLE:', 132, CREAM], ['1-TRUCK SHOP', 132, GOLD]], 264);
      else stampPlate(k, [['OF EVERY $100', 132, CREAM], ['$9 LEFT', 198, GOLD]], 264, tNine, {drop: 0.06, freeze: 4});
      return {host: false};
    },

    /* ---- bill: the invoice builds, one row as each is said; then they work from home ---- */
    bill: (k, T) => {
      const t0 = k.S('bill'), tHome = k.S('bill.home');
      if (T < tHome) {
        k.cut(t0);
        kitchen(k, 0.55, 2);
        const ts = [t0, wordT(k, 'bill', /^sixteen/i, 1.6) - 0.1, wordT(k, 'bill', /^eight/i, 3.0) - 0.1, wordT(k, 'bill', /^twenty/i, 4.5) - 0.1, wordT(k, 'bill', /^six$/i, 7.5) - 0.1];
        const all = [['TECH $41', 132, INK], ['OFFICE $16', 132, INK], ['TRUCK $8', 132, INK], ['FEES $20', 132, INK], ['INSURANCE $6', 132, INK]];
        let n = 0; ts.forEach((t) => { if (T >= t) n++; });
        n = Math.max(1, n);
        const rows = all.slice(0, n);
        if (n === 1 && T < t0 + 0.06) plate(k, rows, 264, {bg: CREAM, rule: RED});
        else stampPlate(k, rows, 264, ts[n - 1], {bg: CREAM, rule: RED, drop: 0.06});
      } else {
        k.cut(tHome);
        kitchen(k, 0.2, 2);
        plumber(k, 540, 2.2, 'talk', {feet: 1780, talk: true});
        plate(k, [['THEY WORK', 132, CREAM], ['FROM HOME', 132, GOLD]], 264);
      }
      return {host: false};
    },

    /* ---- twist (70 to 85%): pay for a shop: $9 LEFT struck, then UNDER $2 ---- */
    twist: (k, T) => {
      const t0 = k.S('twist'), tShop = wordT(k, 'twist', /^shop/i, 0.6) - 0.1, tTwo = wordT(k, 'twist', /^two/i, 2.0) - 0.15;
      k.cut(t0);
      kitchen(k, 0.3, 2);
      plumber(k, 540, 2.2, T >= tTwo ? 'shrug' : 'talk', {feet: 1780, talk: T < tTwo});
      if (T < tTwo - 0.06) {
        const b = plate(k, [['$9 LEFT', 198, GOLD]], 264);
        if (T >= tShop) strike(k, '$9 LEFT', 198, b, tShop);
      } else stampPlate(k, [['WITH A SHOP:', 132, CREAM], ['UNDER $2', 198, RED]], 264, tTwo, {drop: 0.06, freeze: 4});
      return {host: false};
    },

    /* ---- ask: the frame splits, one person a side: the plumber (fair, $2 left) and the client (too much, $100 bill) ---- */
    ask: (k, T) => {
      const t0 = k.S('ask'), tToo = wordT(k, 'ask', /^too/i, 1.0) - 0.1, tSend = k.S('ask.send');
      k.cut(t0);
      const P = px(k);
      P(0, 0, 180, 640, '#4A4E5A'); P(180, 0, 180, 640, WINE); P(178, 0, 4, 640, INK);
      for (let y = 20; y < 640; y += 22) { P(0, y, 178, 1, '#6B7080'); P(182, y + 11, 178, 1, '#5A2432'); }
      plumber(k, 270, 1.6, T >= tSend ? 'point' : 'talk', {feet: 1690, at: [540, 1900], talk: false});
      owner(k, 810, 1.75, 'refuse', 'cross', {feet: 1690, face: -1});
      if (T < t0 + 0.3) plate(k, [['PLUMBER:', 132, CREAM], ['FAIR,', 132, TEAL]], 264, {cx: 290, bg: INK, rule: TEAL});
      else stampPlate(k, [['PLUMBER:', 132, CREAM], ['FAIR,', 132, TEAL], ['$2 LEFT', 132, TEAL]], 264, t0 + 0.34, {cx: 290, bg: INK, rule: TEAL, drop: 0.06});
      if (T < tToo - 0.06) plate(k, [['CLIENT:', 132, CREAM]], 264, {cx: 800, bg: INK, rule: RED});
      else stampPlate(k, [['CLIENT:', 132, CREAM], ['TOO', 132, GOLD], ['MUCH,', 132, GOLD], ['$100 BILL', 132, GOLD]], 264, tToo, {cx: 800, bg: INK, rule: RED, drop: 0.06});
      return {host: false};
    },
});
