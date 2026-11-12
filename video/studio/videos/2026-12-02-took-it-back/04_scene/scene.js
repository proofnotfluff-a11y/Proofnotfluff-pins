/* 2026-12-02-took-it-back (v4 case), from the v4 template's helpers (wordT, px, plate, stampPlate), kept whole     */
/* (_shared/formats.md "v4" and "Case"). One section a cue, each its own shot; every row size 132 or more.          */
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

/* ---- the places, in the low-res painter's units (360 x 640). z 2 is the close shot (the same place at twice the size) ---- */
const zoom = (k, z, fn) => { const c = k.ctx; c.save(); if (z !== 1) { c.translate(540 * (1 - z), 836 * (1 - z)); c.scale(z, z); } fn(px(k)); c.restore(); };
const dimmer = (k, a) => { if (a) px(k)(0, 0, 360, 640, `rgba(18,13,20,${a})`); };
/* the bathroom: tiled wall, a vanity left, the shower on the right. st: 'new', 'hit' (chipped), 'broken', 'fixing' */
const bath = (k, st = 'new', dim = 0, z = 1) => {
  zoom(k, z, (P) => {
    P(0, 0, 360, 330, '#DDEDEA'); for (let x = 0; x < 360; x += 20) P(x, 0, 1, 330, '#B9D6D0'); for (let y = 10; y < 330; y += 20) P(0, y, 360, 1, '#B9D6D0');
    P(26, 150, 78, 70, INK); P(29, 153, 72, 64, SKY); P(29, 195, 72, 22, '#BDE6F5');   /* the mirror */
    P(14, 246, 104, 10, INK); P(17, 248, 98, 6, CREAM); P(20, 256, 92, 74, INK); P(23, 259, 86, 71, '#8C5A33'); P(64, 259, 2, 71, INK); P(54, 286, 3, 10, GOLD); P(71, 286, 3, 10, GOLD);   /* the vanity */
    P(176, 96, 168, 234, INK); P(180, 100, 160, 230, st === 'broken' ? '#9FBFB9' : '#8FCFC5');   /* the shower */
    for (let x = 180; x < 340; x += 16) P(x, 100, 1, 230, '#5FA79A'); for (let y = 100; y < 330; y += 16) P(180, y, 160, 1, '#5FA79A');
    P(322, 112, 4, 30, '#6B7080'); P(306, 112, 20, 4, '#6B7080'); P(300, 116, 14, 6, '#9AA0AD');   /* the shower head */
    if (st === 'hit' || st === 'broken' || st === 'fixing') {   /* the wall, chipped or broken open to the board behind */
      const holes = st === 'hit' ? [[214, 232, 34, 30]] : [[196, 180, 66, 60], [240, 226, 58, 70], [206, 252, 44, 50], [268, 168, 40, 44]];
      holes.forEach(([x, y, w, h], n) => {   /* a ragged hole: dark board, two studs, tile teeth left on its edge, cracks running out */
        P(x, y + 6, w, h - 12, '#3F3A38'); P(x + 6, y, w - 12, h, '#3F3A38');
        P(x + Math.round(w * 0.3), y + 2, 4, h - 4, '#5E5248'); P(x + Math.round(w * 0.7), y + 2, 4, h - 4, '#5E5248');
        for (let i = 0; i < 6; i++) { const e = (i * 7 + n * 3) % 4, a = 5 + ((i * 13 + n * 5) % 7); P(x + (i * 11) % Math.max(8, w - 8), e < 2 ? y : y + h - a, 7, a, '#8FCFC5'); P(e % 2 ? x : x + w - a, y + (i * 9) % Math.max(8, h - 8), a, 6, '#8FCFC5'); }
        P(x - 12, y + Math.round(h / 2), 12, 2, INK); P(x + w, y + Math.round(h / 3), 14, 2, INK); P(x + Math.round(w / 2), y - 10, 2, 10, INK); P(x + Math.round(w / 3), y + h, 2, 12, INK);
      });
      if (st === 'fixing') { [[194, 178, 70, 64], [266, 166, 44, 48]].forEach(([x, y, w, h]) => { P(x, y, w, h, '#BFE9E1'); for (let a = x; a < x + w; a += 16) P(a, y, 1, h, '#5FA79A'); for (let b = y; b < y + h; b += 16) P(x, b, w, 1, '#5FA79A'); }); }
    }
    P(0, 330, 360, 310, '#C9CCD3'); for (let y = 330; y < 640; y += 26) P(0, y, 360, 2, '#AEB3BD'); for (let x = 0; x < 360; x += 40) P(x, 330, 2, 310, '#AEB3BD');   /* the floor */
    if (st === 'broken') [[190, 334, 12, 6], [214, 340, 9, 5], [236, 333, 14, 7], [262, 342, 10, 5], [286, 336, 12, 6], [226, 350, 8, 4], [304, 346, 9, 5]].forEach(([x, y, w, h], i) => { P(x - 1, y - 1, w + 2, h + 2, INK); P(x, y, w, h, i % 2 ? '#8FCFC5' : CREAM); });
  });
  dimmer(k, dim);
};
/* the hallway: a warm wall, the bathroom door open */
const hall = (k, dim = 0) => {
  const P = px(k);
  P(0, 0, 360, 380, '#E9DCC4'); for (let y = 14; y < 380; y += 22) P(0, y, 360, 1, '#D8C7AA');
  P(0, 300, 360, 80, '#D8C7AA'); P(0, 298, 360, 3, '#B09A7C');
  P(96, 196, 168, 184, INK); P(102, 202, 156, 178, '#DDEDEA'); for (let x = 102; x < 258; x += 20) P(x, 202, 1, 178, '#B9D6D0'); for (let y = 212; y < 380; y += 20) P(102, y, 156, 1, '#B9D6D0');
  P(60, 198, 42, 184, INK); P(63, 201, 36, 178, '#8C5A33'); P(90, 290, 5, 8, GOLD);   /* the door, swung open */
  P(0, 380, 360, 260, '#B07A47'); for (let y = 380; y < 640; y += 20) P(0, y, 360, 2, '#8C5A33');
  dimmer(k, dim);
};
/* a phone on a dark wall, the clip playing, hearts rising beside it */
const phone = (k, T) => {
  const P = px(k);
  P(0, 0, 360, 640, NIGHT); for (let i = 0; i < 30; i++) P((i * 67) % 360, (i * 131) % 640, 2, 2, PLUM);
  P(104, 236, 152, 300, INK); P(108, 240, 144, 292, '#3A2F45'); P(114, 252, 132, 240, '#DDEDEA');
  for (let x = 114; x < 246; x += 16) P(x, 252, 1, 240, '#B9D6D0'); for (let y = 252; y < 492; y += 16) P(114, y, 132, 1, '#B9D6D0');
  P(150, 330, 60, 70, '#7A6650'); P(148, 328, 64, 2, INK); P(148, 400, 64, 2, INK);
  for (let i = 0; i < 14; i++) P(166 + i, 346 + Math.floor(i / 2), 2, 30 - i * 2 + (i % 2), RED);   /* the play mark */
  P(114, 500, 132, 6, '#5A4A6A'); P(114, 500, Math.round(132 * ((T * 0.35) % 1)), 6, GOLD);
  for (let i = 0; i < 7; i++) { const y = 520 - ((T * 70 + i * 43) % 280), x = 268 + (i % 3) * 22 + Math.round(Math.sin(T * 3 + i) * 3); P(x, y, 10, 4, RED); P(x + 1, y + 4, 8, 3, RED); P(x + 3, y + 7, 4, 3, RED); P(x + 4, y - 2, 2, 2, NIGHT); }
};
/* a police desk under a gold badge */
const station = (k, dim = 0) => {
  const P = px(k);
  P(0, 0, 360, 420, '#253048'); for (let y = 16; y < 420; y += 24) P(0, y, 360, 1, '#1D2740'); P(0, 236, 360, 6, GOLD);
  P(156, 252, 48, 40, INK); P(159, 255, 42, 34, GOLD); P(164, 289, 32, 10, GOLD); P(170, 299, 20, 8, GOLD); P(170, 264, 20, 16, '#253048'); P(176, 268, 8, 8, GOLD);
  P(40, 350, 280, 14, INK); P(43, 352, 274, 9, '#8C5A33'); P(56, 364, 248, 76, INK); P(59, 364, 242, 73, '#5A3A22');
  P(262, 310, 5, 40, '#9AA0AD'); P(246, 298, 36, 14, INK); P(248, 300, 32, 10, GOLD);
  P(80, 334, 44, 16, INK); P(82, 336, 40, 12, CREAM);
  P(0, 440, 360, 200, NIGHT);
  dimmer(k, dim);
};
/* a sheet on a desk; seal: a red seal on it */
const sheet = (k, seal) => {
  const P = px(k);
  P(0, 0, 360, 640, '#5A3A22'); for (let y = 0; y < 640; y += 28) P(0, y, 360, 2, '#4A2E1B');
  P(66, 250, 228, 300, INK); P(69, 253, 222, 294, CREAM);
  for (let y = 274; y < 500; y += 22) P(88, y, y % 44 === 10 ? 150 : 184, 5, '#C9B79C');
  if (seal) { P(214, 470, 56, 56, INK); P(217, 473, 50, 50, RED); P(225, 481, 34, 34, '#B8452A'); P(236, 492, 12, 12, RED); }
};
/* a courtroom: wood wall, the bench, a gavel that comes down at t */
const court = (k, T, t, dim = 0, z = 1) => {
  zoom(k, z, (P) => {
    P(0, 0, 360, 400, '#6B4A2E'); for (let x = 0; x < 360; x += 60) P(x, 0, 3, 400, '#4A3120'); P(0, 120, 360, 4, '#4A3120');
    P(158, 150, 44, 44, INK); P(161, 153, 38, 38, GOLD); P(169, 161, 22, 22, '#6B4A2E'); P(176, 168, 8, 8, GOLD);
    P(50, 236, 260, 164, INK); P(54, 240, 252, 160, '#8C5A33'); P(54, 240, 252, 12, '#B07A47'); P(70, 270, 220, 110, '#7A4A28');
    const d = T - t, a = d < 0 ? 0 : (d < 0.1 ? d / 0.1 : 1);   /* the gavel: up, then down on the block */
    P(232, 226, 40, 8, INK); P(234, 228, 36, 5, '#4A3120');
    const gy = 196 + Math.round(18 * a);
    P(238, gy, 28, 14, INK); P(240, gy + 2, 24, 10, '#B07A47'); P(266, gy + 5, 30, 5, INK); P(266, gy + 6, 30, 3, '#8C5A33');
    P(0, 400, 360, 240, '#3A2A1E'); P(0, 452, 360, 8, '#8C5A33'); P(0, 460, 360, 3, INK);
  });
  dimmer(k, dim);
};
/* a cell wall, and the bars drawn over whoever stands in it */
const cell = (k) => { const P = px(k); P(0, 0, 360, 640, '#33343D'); for (let y = 0; y < 640; y += 26) { P(0, y, 360, 2, '#26272E'); for (let x = (y / 26) % 2 ? 0 : 30; x < 360; x += 60) P(x, y, 2, 26, '#26272E'); } };
const bars = (k) => { const P = px(k); [16, 80, 144, 208, 272, 336].forEach((x) => { P(x - 1, 210, 10, 430, INK); P(x, 210, 8, 430, '#9AA0AD'); P(x + 5, 210, 3, 430, '#6B7080'); }); P(0, 210, 360, 12, INK); P(0, 212, 360, 8, '#6B7080'); };
/* a shop front, the shutter down and locked */
const shut = (k, dim = 0) => {
  const P = px(k);
  P(0, 0, 360, 470, '#4A4E5A'); for (let y = 12; y < 470; y += 20) P(0, y, 360, 1, '#3D414C');
  P(40, 250, 280, 220, INK); P(46, 256, 268, 214, '#9AA0AD'); for (let y = 256; y < 470; y += 12) P(46, y, 268, 2, '#6B7080');
  P(30, 222, 300, 32, INK); for (let x = 33; x < 327; x += 42) { P(x, 225, 21, 26, WINE); P(x + 21, 225, 21, 26, CREAM); }
  P(170, 448, 20, 18, INK); P(172, 450, 16, 14, GOLD); P(174, 440, 12, 10, INK); P(177, 443, 6, 8, '#9AA0AD');
  P(0, 470, 360, 170, '#8C8F99'); for (let x = 0; x < 360; x += 60) P(x, 470, 2, 170, '#75788A');
  dimmer(k, dim);
};
/* a courthouse: columns, steps, a sky */
const house = (k, dim = 0, z = 1) => {
  zoom(k, z, (P) => {
    P(0, 0, 360, 400, SKY); P(40, 60, 70, 14, CREAM); P(250, 96, 60, 12, CREAM);
    for (let i = 0; i < 11; i++) P(54 + i * 12, 268 - i * 5, 252 - i * 24, 5, i % 2 ? SAND : CREAM);
    P(50, 272, 260, 10, INK); P(54, 282, 252, 108, CREAM);
    [70, 118, 166, 214, 262].forEach((x) => { P(x - 1, 284, 24, 106, INK); P(x, 284, 22, 106, '#F4E6D3'); P(x + 4, 284, 3, 106, '#C9B79C'); P(x + 14, 284, 3, 106, '#C9B79C'); });
    P(166, 330, 28, 60, '#5A3A22');
    P(40, 390, 280, 10, INK); P(30, 400, 300, 10, '#C9B79C'); P(20, 410, 320, 10, '#B09A7C'); P(0, 420, 360, 220, '#7A8F6A');
  });
  dimmer(k, dim);
};
/* the split wall: the homeowner's side left (wine), the contractor's side right (slate) */
const split = (k) => { const P = px(k); P(0, 0, 180, 640, WINE); P(180, 0, 180, 640, '#4A4E5A'); P(178, 0, 4, 640, INK); for (let y = 20; y < 640; y += 22) { P(0, y + 11, 178, 1, '#5A2432'); P(182, y, 178, 1, '#6B7080'); } };

/* a plain lined wall in one color (each side's own place in the close shots at the end and in the hook) */
const wall = (k, c, c2) => { const P = px(k); P(0, 0, 360, 640, c); for (let y = 20; y < 640; y += 22) P(0, y, 360, 1, c2); };
/* a second person as a plain dark shape (the business partner: no source describes them, so no face and no clothes) */
const shape2 = (k, x, y, s = 1) => { const c = k.ctx, q = (v) => Math.round(v / 3) * 3; c.fillStyle = '#2B2033'; c.fillRect(q(x - 45 * s), q(y - 330 * s), q(90 * s), q(90 * s)); c.fillRect(q(x - 75 * s), q(y - 235 * s), q(150 * s), q(235 * s)); };
/* the cast. Close shots from the waist up, feet far below the frame (feet 1700 or so), faces between y 700 and 1100. */
const pro = (k, x, sc, pose, o = {}) => k.snow(x, o.feet || 1150, Object.assign({scale: sc, pose, face: 1, talk: false}, o));
const owner = (k, x, sc, pose, mood, o = {}) => k.client(x, o.feet || 1150, Object.assign({role: 'homeowner', scale: sc, pose, mood, face: -1}, o));
/* the sledgehammer: a handle from (ax, ay) to (bx, by) and the head across its far end; s is the figure's scale */
const hammer = (k, ax, ay, bx, by, s = 1) => {
  const c = k.ctx, ang = Math.atan2(by - ay, bx - ax), len = Math.hypot(bx - ax, by - ay), q = (v) => Math.round(v / 3) * 3;
  c.save(); c.translate(q(ax), q(ay)); c.rotate(ang);
  c.fillStyle = INK; c.fillRect(-3, -q(9 * s) - 3, q(len) + 6, q(18 * s) + 6); c.fillStyle = '#8C5A33'; c.fillRect(0, -q(9 * s), q(len), q(18 * s));
  c.fillStyle = INK; c.fillRect(q(len - 26 * s) - 3, -q(46 * s) - 3, q(56 * s) + 6, q(92 * s) + 6); c.fillStyle = '#6B7080'; c.fillRect(q(len - 26 * s), -q(46 * s), q(56 * s), q(92 * s));
  c.fillStyle = '#9AA0AD'; c.fillRect(q(len - 26 * s), -q(46 * s), q(56 * s), q(14 * s));
  c.restore();
};
/* the hammer at rest on his shoulder (he faces f) and the contractor under it */
const proHammer = (k, x, sc, pose, o = {}) => {
  const f = o.face || 1, feet = o.feet || 1150;
  if (o.up) hammer(k, x + 70 * f * sc, feet - 230 * sc, x + (70 + 150 * Math.cos(o.up)) * f * sc, feet - (230 + 250 * Math.sin(o.up)) * sc, sc);
  pro(k, x, sc, pose, o);
  if (!o.up) hammer(k, x + 50 * f * sc, feet - 170 * sc, x - 105 * f * sc, feet - 420 * sc, sc);
};
/* a row of plates in time: [[t, rows, stamp?], ...]; the last one whose time has come shows; a later one lands as a stamp */
const steps = (k, T, list, o = {}, y = 264) => {
  let i = 0; list.forEach(([t], j) => { if (j && T >= t - 0.06) i = j; });
  const [t, rows, st] = list[i];
  if (i === 0 && !st) return plate(k, rows, y, o);
  return stampPlate(k, rows, y, t, Object.assign({drop: 0.06, freeze: 4}, o));
};
const push = (k, T, t0, fn, amt = 0.07, cy = 1100) => { const c = k.ctx, z = 1 + amt * clamp((T - t0) / 4); c.save(); c.translate(540, cy); c.scale(z, z); c.translate(-540, -cy); fn(); c.restore(); };
const W = (k, id, re, d) => wordT(k, id, re, d) - 0.1;
const SIDE_L = {cx: 290, bg: INK, rule: RED}, SIDE_R = {cx: 795, bg: INK, rule: TEAL};
const HELD = [['CLIENT', 132, CREAM], ['HELD', 132, GOLD], ['$4,225', 132, GOLD]], GOT = [['BUILDER', 132, CREAM], ['GOT', 132, RED], ['15 DAYS', 132, RED]];

window.SCENE = {
  look: 'arcade',
  v4: true,
  host: false,
  endCard: false,
  images: [],
  trauma: {smash: 0.6, result: 0.7, jail: 0.5},
  sections: {
    /* ---- hook: frame 0 is the wrong, settled: him at the shower, the hammer up, and what she held back; at 0.5 s her, ---- */
    /* arms folded, on her own wall (viewer r0: the hammer belongs in frame 0; facts r0: no source puts her in the room) ---- */
    hook: (k, T) => {
      const tHer = 0.5, tHim = Math.max(1.4, W(k, 'hook', /^so/i, 2.2));
      const rows = [['SHE HELD BACK', 132, CREAM], ['$4,225', 198, GOLD]];
      if (T < tHer) {
        bath(k, 'new', 0.15, 2);
        proHammer(k, 470, 2.2, 'stand', {feet: 1790, up: 1.15});
        plate(k, rows, 264);
      } else if (T < tHim) {
        k.cut(tHer);
        wall(k, WINE, '#5A2432');
        owner(k, 540, 2.4, 'refuse', 'cross', {feet: 1800, face: -1});
        plate(k, rows, 264);
      } else {
        k.cut(tHim);
        bath(k, 'new', 0.22, 2);
        proHammer(k, 500, 2.4, 'stand', {feet: 1850, up: 1.15 + 0.1 * Math.sin(T * 6)});
        steps(k, T, [[tHim, [['HE CAME BACK', 132, CREAM], ['WITH A HAMMER', 132, RED]], 1]]);
      }
      return {host: false};
    },
    /* ---- deal: the wide shot, the new shower ---- */
    deal: (k, T) => {
      k.cut(k.S('deal'));
      bath(k, 'new', 0.1, 1);
      pro(k, 330, 1.25, 'point', {feet: 1420, at: [760, 700]});
      plate(k, [['SHOWER REBUILD', 132, CREAM], ['COLORADO', 132, TEAL]], 264);
      return {host: false};
    },
    /* ---- bill: the bill, then what she paid ---- */
    bill: (k, T) => {
      const t0 = k.S('bill'), tPaid = W(k, 'bill', /^paid/i, 2.4);
      k.cut(t0);
      bath(k, 'new', 0.4, 2);
      pro(k, 905, 2.0, 'clip', {feet: 1740, face: -1});
      const o = {bg: CREAM, rule: RED, cx: 420};
      steps(k, T, [[t0, [['THE BILL', 132, INK], ['$7,555', 198, RED]]], [tPaid, [['THE BILL', 132, INK], ['$7,555', 198, RED], ['PAID $3,330', 132, DTEAL]]]], o);
      return {host: false};
    },
    /* ---- her: her side, close ---- */
    her: (k, T) => {
      k.cut(k.S('her'));
      wall(k, WINE, '#5A2432');
      owner(k, 560, 2.3, 'refuse', 'cross', {feet: 1790, face: -1});
      plate(k, [['SHE SAYS:', 132, CREAM], ['NOT HAPPY', 132, GOLD], ['WITH THE WORK', 132, GOLD]], 264);
      return {host: false};
    },
    /* ---- herline: her acted line, closer; the plate says whose side and that it is a reenactment (viewer r0) ---- */
    herline: (k, T) => {
      k.cut(k.S('herline'));
      wall(k, '#5A2432', WINE);
      owner(k, 540, 2.9, 'talk', 'calm', {feet: 2080, face: -1, talk: true});
      plate(k, [['HER SIDE', 132, CREAM], ['REENACTMENT', 132, ORANGE]], 264);
      return {host: false};
    },
    /* ---- himline: his acted line, close, the hammer on his shoulder ---- */
    himline: (k, T) => {
      k.cut(k.S('himline'));
      wall(k, '#4A4E5A', '#6B7080');
      proHammer(k, 520, 2.8, 'talk', {feet: 2060, talk: true});
      plate(k, [['HIS SIDE', 132, CREAM], ['REENACTMENT', 132, ORANGE]], 264);
      return {host: false};
    },
    /* ---- room: the hallway, the door open, him in the doorway, his partner a plain shape behind him ---- */
    room: (k, T) => {
      k.cut(k.S('room'));
      hall(k, 0.1);
      shape2(k, 640, 1150, 1.2);
      proHammer(k, 500, 1.25, 'stand', {feet: 1150, face: -1});
      plate(k, [['THE ROOMMATE', 132, CREAM], ['LET THEM IN', 132, GOLD]], 264);
      return {host: false};
    },
    /* ---- film: through the roommate's phone: corner marks, a red dot that blinks ---- */
    film: (k, T) => {
      const t0 = k.S('film');
      k.cut(t0);
      bath(k, 'new', 0.2, 1);
      proHammer(k, 520, 1.45, 'stand', {feet: 1500, up: 1.2 + 0.12 * Math.sin(T * 7)});
      const P = px(k);
      [[20, 236], [326, 236], [20, 600], [326, 600]].forEach(([x, y], i) => { P(x, y, 14, 3, CREAM); P(i % 2 ? x + 11 : x, i < 2 ? y : y - 11, 3, 14, CREAM); });
      if (Math.floor((T - t0) * 3) % 2 === 0) { P(36, 250, 12, 12, INK); P(38, 252, 8, 8, RED); }
      plate(k, [['AND FILMED IT', 132, RED]], 264);
      return {host: false};
    },
    /* ---- smash: he swings at the tile, chips fly on each hit ---- */
    smash: (k, T) => {
      const t0 = k.S('smash'), beat = 0.55, n = Math.floor((T - t0) / beat), ph = ((T - t0) / beat) % 1;
      k.cut(t0);
      bath(k, n >= 1 ? 'hit' : 'new', 0.15, 2);
      const up = ph < 0.6 ? 1.25 - 0.3 * (ph / 0.6) : 0.95 - 1.15 * ((ph - 0.6) / 0.4);
      proHammer(k, 330, 2.0, 'stand', {feet: 1760, up});
      for (let i = 1; i <= n; i++) k.burst(820, 640, t0 + i * beat, {colors: [CREAM, '#8FCFC5', '#5FA79A'], n: 14, r: 200});
      plate(k, [['THE HAMMER', 132, CREAM], ['TO THE TILE', 132, RED]], 264);
      return {host: false};
    },
    /* ---- says: him close, the wall broken behind; his claim builds a row at a time ---- */
    says: (k, T) => {
      const t0 = k.S('says'), tNo = W(k, 'says', /^no$/i, 0.8), tFix = W(k, 'says', /^fix/i, 3.0);
      k.cut(t0);
      bath(k, 'broken', 0.3, 2);
      proHammer(k, 480, 2.2, 'talk', {feet: 1780, talk: true});
      steps(k, T, [[t0, [['HE SAYS:', 132, CREAM]]], [tNo, [['HE SAYS:', 132, CREAM], ['NO CONTRACTOR', 132, GOLD]]], [tFix, [['HE SAYS:', 132, CREAM], ['NO CONTRACTOR', 132, GOLD], ['WILL FIX IT', 132, GOLD]]]]);
      return {host: false};
    },
    /* ---- repo: the wide shot, the shower broken open, the hammer down ---- */
    repo: (k, T) => {
      k.cut(k.S('repo'));
      bath(k, 'broken', 0.12, 1);
      pro(k, 300, 1.3, 'shrug', {feet: 1440});
      hammer(k, 450, 1430, 500, 1180, 1.2);
      plate(k, [['HIS COMPANY', 132, CREAM], ['CALLED IT', 132, CREAM], ['REPOSSESSING', 132, RED]], 264);
      return {host: false};
    },
    /* ---- viral: a phone, the clip playing, hearts rising; the phone shakes a little (viewer r0: dead air) ---- */
    viral: (k, T) => {
      const t0 = k.S('viral'), c = k.ctx;
      k.cut(t0);
      px(k)(0, 0, 360, 640, NIGHT);
      c.save(); c.translate(Math.round(Math.sin(T * 31) * 2) * 3, Math.round(Math.cos(T * 23) * 2) * 3); phone(k, T); c.restore();
      steps(k, T, [[t0 + 0.1, [['MILLIONS', 198, GOLD], ['OF VIEWS', 132, CREAM]], 1]]);
      return {host: false};
    },
    /* ---- rebuild: two tile workers at the wall, new tile going up ---- */
    rebuild: (k, T) => {
      const t0 = k.S('rebuild'), tCame = W(k, 'rebuild', /^came/i, 2.0);
      k.cut(t0);
      bath(k, 'fixing', 0.12, 1);
      pro(k, 230, 1.25, 'point', {feet: 1420, at: [700, 800]});
      pro(k, 480, 1.3, T >= tCame ? 'wave' : 'clip', {feet: 1440});
      steps(k, T, [[t0, [['STRANGERS IN', 132, CREAM], ['THE TILE TRADE', 132, CREAM]]], [tCame, [['CAME TO', 132, CREAM], ['REBUILD IT', 132, CREAM], ['FREE', 198, TEAL]]]]);
      return {host: false};
    },
    /* ---- police: a desk under a badge ---- */
    police: (k, T) => {
      k.cut(k.S('police'));
      push(k, T, k.S('police'), () => station(k, 0.05));
      plate(k, [['POLICE', 198, CREAM], ['LOOKED INTO IT', 132, GOLD]], 264);
      return {host: false};
    },
    /* ---- partner: a statement sheet; what his partner told police ---- */
    partner: (k, T) => {
      const t0 = k.S('partner'), tW = W(k, 'partner', /^wished/i, 2.0);
      k.cut(t0);
      push(k, T, t0, () => sheet(k, false), 0.06);
      steps(k, T, [[t0, [['HIS PARTNER', 132, CREAM], ['TOLD POLICE:', 132, CREAM]]], [tW, [['THEY WISHED', 132, CREAM], ['THEY HAD GONE', 132, CREAM], ['THE LEGAL ROUTE', 132, GOLD]]]]);
      return {host: false};
    },
    /* ---- rule: the courthouse, wide: there was a legal route ---- */
    rule: (k, T) => {
      k.cut(k.S('rule'));
      push(k, T, k.S('rule'), () => house(k, 0.1, 1), 0.1, 900);
      plate(k, [['THERE WAS', 132, CREAM], ['A LEGAL ROUTE', 132, GOLD]], 264);
      return {host: false};
    },
    /* ---- court: closer on the courthouse; the limit lands ---- */
    court: (k, T) => {
      const t0 = k.S('court'), tUp = W(k, 'court', /^up$/i, 2.8);
      k.cut(t0);
      push(k, T, t0, () => house(k, 0.3, 2), 0.06, 900);
      steps(k, T, [[t0, [['SMALL CLAIMS', 132, CREAM], ['COURT TAKES', 132, CREAM]]], [tUp, [['SMALL CLAIMS', 132, CREAM], ['COURT TAKES', 132, CREAM], ['UP TO $7,500', 132, GOLD]]]]);
      return {host: false};
    },
    /* ---- fit: the courthouse door, close; his bill under the limit ---- */
    fit: (k, T) => {
      const t0 = k.S('fit');
      k.cut(t0);
      push(k, T, t0, () => house(k, 0.45, 3), 0.12, 1000);
      steps(k, T, [[t0 + 0.1, [['HIS $4,225', 132, TEAL], ['FIT', 198, CREAM]], 1]]);
      return {host: false};
    },
    /* ---- warrants: the sheet, sealed ---- */
    warrants: (k, T) => {
      const t0 = k.S('warrants');
      k.cut(t0);
      push(k, T, t0, () => sheet(k, true), 0.06);
      steps(k, T, [[t0 + 0.1, [['FELONY', 198, RED], ['WARRANTS', 132, CREAM], ['FOR BOTH', 132, CREAM]], 1]]);
      return {host: false};
    },
    /* ---- result (the payoff, held to the last 40%): the courtroom, the gavel, the plea ---- */
    result: (k, T) => {
      const t0 = k.S('result'), tG = W(k, 'result', /^guilty/i, 0.7);
      k.cut(t0);
      court(k, T, tG, 0.2, 2);
      pro(k, 520, 2.2, 'stand', {feet: 1790});
      steps(k, T, [[t0, [['HE PLEADED', 132, CREAM]]], [tG, [['GUILTY PLEA', 132, CREAM], ['A FELONY', 198, RED]]]]);
      return {host: false};
    },
    /* ---- jail: the sentence, at the bench: the gavel comes down (facts r0: a cell would read as time served) ---- */
    jail: (k, T) => {
      const t0 = k.S('jail');
      k.cut(t0);
      push(k, T, t0, () => court(k, T, t0 + 0.1, 0.1, 3), 0.06, 900);
      steps(k, T, [[t0 + 0.1, [['SENTENCE:', 132, CREAM], ['15 DAYS', 198, GOLD], ['IN JAIL', 132, CREAM]], 1]]);
      return {host: false};
    },
    /* ---- prob: the courtroom, wider ---- */
    prob: (k, T) => {
      const t0 = k.S('prob');
      k.cut(t0);
      court(k, T, t0 - 5, 0.25, 1);
      pro(k, 540, 1.3, 'stand', {feet: 1440});
      steps(k, T, [[t0 + 0.1, [['3 YEARS', 198, GOLD], ['PROBATION', 132, CREAM]], 1]]);
      return {host: false};
    },
    /* ---- closed: the shop front, shut ---- */
    closed: (k, T) => {
      k.cut(k.S('closed'));
      push(k, T, k.S('closed'), () => shut(k, 0.1), 0.08);
      plate(k, [['THE COMPANY:', 132, CREAM], ['NO LONGER', 132, RED], ['ACTIVE', 132, RED]], 264);
      return {host: false};
    },
    /* ---- ask: her, close, on her wall: what she held ---- */
    ask: (k, T) => {
      const t0 = k.S('ask');
      k.cut(t0);
      wall(k, WINE, '#5A2432');
      owner(k, 540, 2.4, 'refuse', 'cross', {feet: 1800, face: -1});
      steps(k, T, [[t0 + 0.05, [['SHE HELD', 132, CREAM], ['$4,225', 198, GOLD]], 1]]);
      return {host: false};
    },
    /* ---- askhe: him, close, on his wall: what he got ---- */
    askhe: (k, T) => {
      const t0 = k.S('askhe');
      k.cut(t0);
      wall(k, '#4A4E5A', '#6B7080');
      proHammer(k, 520, 2.2, 'shrug', {feet: 1790});
      steps(k, T, [[t0 + 0.05, [['HE GOT', 132, CREAM], ['15 DAYS', 198, RED]], 1]]);
      return {host: false};
    },
    /* ---- who: the frame splits, one a side, the question between them ---- */
    who: (k, T) => {
      const t0 = k.S('who');
      k.cut(t0);
      split(k);
      owner(k, 270, 1.7, 'argue', 'cross', {feet: 1700, face: 1});
      proHammer(k, 780, 1.6, 'shrug', {feet: 1700, face: -1});
      steps(k, T, [[t0 + 0.05, [['WHO WAS', 132, CREAM], ['MORE WRONG?', 132, GOLD]], 1]]);
      return {host: false};
    },
    /* ---- send: the same split; each side's case lands, labeled as a kind of person ---- */
    send: (k, T) => {
      const t0 = k.S('send');
      split(k);
      owner(k, 270, 1.7, 'refuse', 'calm', {feet: 1700, face: 1});
      proHammer(k, 780, 1.6, 'stand', {feet: 1700, face: -1});
      steps(k, T, [[t0 + 0.05, HELD, 1]], SIDE_L, 264);
      steps(k, T, [[t0 + 0.3, GOT, 1]], SIDE_R, 264);
      return {host: false};
    },
  },
};
