/* Scene: Hail or wear (proven, source-matched: the structure of research/PROVEN.md row 3; Nov 8, 2026). The source is a   */
/* 20 s phone clip of a roof with one question caption and no answer; this is the same structure in our art: roof shots   */
/* one after another under one caption box, the clues, her line, the question, no answer. Every shot is ours (EXAMPLE).  */
/* The cover is hand-built rather than k.coverBoard: the source's move is a caption box over the picture, not a board.   */
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', DTEAL = '#2F6F67', GREY = '#9AA0AD', NIGHT = '#1B1420', SLATE = '#4A4E5A', PLUM = '#2B2033', CHALK = '#F4F1E8';
const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eo = (x) => 1 - Math.pow(1 - clamp(x), 3);

/* ---- the pixel kit (low-res units: 360 x 640, one pixel = 3 frame units), as in the lessons before ---- */
const px = (k) => {
  const ctx = k.ctx, T = k.T, F = Math.floor(T * 30 + 0.005);
  const P = (x, y, w, h, c) => { x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h); if (w > 0 && h > 0 && c) { ctx.fillStyle = c; ctx.fillRect(x * 3, y * 3, w * 3, h * 3); } };
  const DOT = (x, y, c) => P(x, y, 1, 1, c);
  const dith = (x, y, w, h, c, ph = 0) => { ctx.fillStyle = c; for (let j = 0; j < h; j++) for (let i = (j + ph) & 1; i < w; i += 2) ctx.fillRect((Math.round(x) + i) * 3, (Math.round(y) + j) * 3, 3, 3); };
  const ring = (cx, cy, r, c, from = 0, to = 1) => { const n = Math.max(12, Math.round(r * 7)); for (let i = 0; i < n * clamp(to); i++) { if (i < n * from) continue; const a = i / n * Math.PI * 2 - Math.PI / 2; DOT(cx + Math.round(Math.cos(a) * r), cy + Math.round(Math.sin(a) * r), c); } };
  const fr = (t0) => Math.floor((T - t0) * 30 + 0.005);
  const ease = (t0, frames, dist) => Math.round(dist * (1 - eo(fr(t0) / frames)));
  return {P, DOT, dith, ring, fr, ease, F, T};
};

/* ---- the words: every beat lands on a spoken word ---- */
const WS = () => (window.WORDS && window.WORDS.words) || [];
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
const host = (k, pose, sc = 0.55, x = 150) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: sc, hostX: x});
const stampBox = (k, s, cx, y, t0, o = {}) => {
  const size = o.size || 66, c = o.color || GOLD, w = Math.round((k.measure(s, {size}) + 54) / 6) * 6, h = size + 36, x = Math.round((cx - w / 2) / 3) * 3;
  k.stampIn(t0, () => {
    k.shape(k.rectPts(x + 6, y + 6, w, h, 0), {fill: INK, line: false}); k.shape(k.rectPts(x, y, w, h, 0), {fill: o.bg || NIGHT, line: false});
    k.shape(k.rectPts(x + 6, y + 6, w - 12, 6, 0), {fill: c, line: false}); k.shape(k.rectPts(x + 6, y + h - 12, w - 12, 6, 0), {fill: c, line: false});
    k.shape(k.rectPts(x + 6, y + 6, 6, h - 12, 0), {fill: c, line: false}); k.shape(k.rectPts(x + w - 12, y + 6, 6, h - 12, 0), {fill: c, line: false});
    k.text(s, x + w / 2, y + 18, {size, color: c, align: 'center'});
  }, {at: [x + w / 2, y + h], freeze: o.freeze});
};


/* ---- the shingle field at any zoom: field units are the close-up's low-res pixels; z scales them; (ox, oy) is the */
/* field point at the shot's top left. Bruises (round, dark center, a bare ring), wear streaks, a gutter at fy 330. ---- */
const FMARKS = [[60, 120], [150, 104], [118, 182], [220, 150], [300, 118], [262, 214], [80, 260], [196, 280]];
const FWEAR = [[30, 200], [180, 230], [250, 90], [320, 260], [120, 300], [10, 120], [290, 170]];
const field = (d, o = {}) => {
  const {P} = d, z = o.z || 1, ox = o.ox || 0, oy = o.oy || 0, X = (fx) => Math.round((fx - ox) * z), Y = (fy) => Math.round(84 + (fy - oy) * z);
  P(0, 0, 360, 417, '#2A2C33');
  for (let r = 0; r < 30; r++) {
    const fy = r * 13, off = r % 2 ? 11 : 0;
    if (Y(fy + 13) < 84 || Y(fy) > 334) continue;
    for (let fx = -off - 22; fx < 400; fx += 22) {
      const x0 = X(fx), y0 = Y(fy) + Math.floor(x0 * 0.08); if (x0 > 360 || x0 + 22 * z < 0) continue;   /* the courses fall to the right, so it reads as a sloped roof, not a wall */
      const c = ['#5B5F68', '#53575F', '#62666E', '#575B63'][Math.floor(hash(r * 17 + fx) * 4)];
      P(x0 + Math.ceil(z), y0, 21 * z, 12 * z, c); P(x0 + Math.ceil(z), y0, 21 * z, Math.max(1, Math.round(z)), '#70747D'); P(x0, y0 + 11 * z, 22 * z, Math.max(1, 2 * z), '#2E3036'); P(x0, y0, Math.max(1, z), 13 * z, '#1E2026');
      for (let i = 0; i < 5; i++) P(x0 + (2 + Math.floor(hash(r * 7 + fx + i) * 19)) * z, y0 + (2 + Math.floor(hash(r + fx * 3 + i) * 8)) * z, Math.max(1, Math.round(z)), Math.max(1, Math.round(z)), i % 2 ? '#6C7079' : '#45484F');
    }
  }
  const worn = o.worn ? FWEAR.concat(FWEAR.map(([a, b]) => [a + 160, b + 40])) : FWEAR.slice(0, 2);
  worn.forEach(([fx, fy]) => { for (let i = 0; i < 4; i++) P(X(fx - 10 + i * 3), Y(fy + i * 2) + Math.floor(X(fx) * 0.08), (22 - i * 4) * z, Math.max(1, z), i % 2 ? '#8A7A66' : '#7A6C5A'); if (o.worn) P(X(fx + 14), Y(fy - 3), 3 * z, Math.max(1, z), '#A7ABB5'); });
  FMARKS.forEach(([fx, fy]) => {
    const cx = X(fx), cy = Y(fy) + Math.floor(X(fx) * 0.08), r = Math.max(2, Math.round(6 * z));
    if (cy < 84 - r || cy > 334 + r) return;
    for (let j = -r; j <= r; j++) for (let i = -r; i <= r; i++) { const q = i * i + j * j; if (q <= r * r && cy + j >= 84 && cy + j < 334) d.DOT(cx + i, cy + j, q <= (r * 0.55) * (r * 0.55) ? '#1E2026' : (q <= (r * 0.85) * (r * 0.85) ? '#8A8E96' : '#6E727A')); }
  });
  P(0, 334, 360, 8, GREY); P(0, 342, 360, 3, '#6B7080'); P(0, 345, 360, 72, '#2B2033');   /* the gutter edge */
};
/* the caption box across the middle, like a phone clip's (frame 0 on; it stays up on every roof shot) */
const caption = (k, d) => {
  d.P(14, 202, 334, 70, INK); d.P(12, 200, 334, 70, '#120D14'); d.P(12, 200, 334, 3, GOLD);
  k.text('HAIL OR WEAR?', 534, 614, {size: 132, color: CREAM, align: 'center', drop: INK});
  k.text('YOU CALL IT.', 534, 742, {size: 66, color: GOLD, align: 'center'});
};
/* white camera corners around a box (low-res), no words */
const corners = (d, x, y, w, h) => { const L = 10, c = CREAM; [[x, y, 1, 1], [x + w, y, -1, 1], [x, y + h, 1, -1], [x + w, y + h, -1, -1]].forEach(([a, b, sx, sy]) => { d.P(sx > 0 ? a : a - L, b - (sy > 0 ? 0 : 2), L, 2, c); d.P(a - (sx > 0 ? 0 : 2), sy > 0 ? b : b - L, 2, L, c); }); };
/* a dime: a silver disc with a rim and a glint */
const dime = (d, cx, cy, r) => { for (let j = -r; j <= r; j++) for (let i = -r; i <= r; i++) { const q = i * i + j * j; if (q <= r * r) d.DOT(cx + i, cy + j, q >= (r - 1.5) * (r - 1.5) ? '#6B7080' : ((i + j) % 5 === 0 ? '#E6E9F0' : '#C9CCD3')); } d.P(cx - r / 3, cy - r / 2, 3, 2, '#FFFFFF'); };
/* the driveway: a frame house with a shingled roof (marks on it), the driveway, the lawn, dusk */
const driveway = (d) => {
  const {P} = d;
  P(0, 0, 360, 417, '#3A4A5E'); for (let y = 84; y < 200; y += 6) d.dith(0, y, 360, 1, '#425470', (y / 6) & 1);
  P(0, 300, 360, 117, '#4B5F2A'); for (let i = 0; i < 40; i++) P(Math.floor(hash(i + 5) * 150), 304 + Math.floor(hash(i + 44) * 100), 1, 3, '#5E7436');   /* design r0: an olive lawn, so the host's teal jacket reads */
  P(150, 300, 210, 117, '#5C606E');
  for (let x = (d.F % 30) - 30; x < 360; x += 30) P(Math.max(150, x + 180), 360, 10, 2, '#6B7080');
  P(26, 190, 150, 112, SAND); for (let y = 196; y < 300; y += 8) P(26, y, 150, 1, '#CDBA9F');
  /* design r0: a filled shingle roof (rows of tabs, bruises like the close-up), not loose lines */
  for (let r = 0; r < 9; r++) {
    const y = 116 + r * 8, half = 12 + r * 10, x0 = 101 - half;
    P(x0, y, half * 2, 8, '#4E525A');
    for (let x = x0 + (r % 2 ? 4 : 0); x < x0 + half * 2 - 2; x += 8) { P(x, y + 1, 7, 6, ['#5B5F68', '#53575F', '#62666E'][Math.floor(hash(r * 11 + x) * 3)]); P(x + 7, y, 1, 8, '#2E3036'); }
    P(x0, y + 7, half * 2, 1, '#2E3036');
  }
  P(84, 112, 34, 4, '#3E4148');
  [[70, 150], [118, 166], [140, 140], [56, 174], [98, 132]].forEach(([x, y]) => { d.P(x - 1, y - 1, 4, 4, '#6E727A'); d.P(x, y, 2, 2, '#1E2026'); });
  P(4, 188, 194, 4, '#2E3036');
  P(44, 214, 30, 30, '#253048'); P(46, 216, 26, 26, '#3B82C4'); P(58, 216, 2, 26, SAND); P(46, 228, 26, 2, SAND);
  P(116, 236, 30, 64, '#7A3442'); P(140, 266, 3, 3, GOLD);
  P(176, 250, 8, 52, '#6B7080');   /* a downspout */
  /* code QA r0 flat (3.7 to 5.0 s): clouds drift and leaves blow across the yard */
  for (let i = 0; i < 3; i++) { const x = Math.floor((i * 140 + d.F * (0.5 + i * 0.2)) % 460) - 80; P(x, 96 + i * 14, 50, 8, '#4B5E7A'); P(x + 8, 92 + i * 14, 30, 4, '#4B5E7A'); }
  for (let i = 0; i < 14; i++) { const x = Math.floor((hash(i + 3) * 360 + d.F * (2 + hash(i) * 2)) % 380) - 10, y = 250 + Math.floor(hash(i + 21) * 80) + Math.round(Math.sin(d.F / 5 + i) * 3); P(x, y, 3, 2, i % 2 ? '#B07A47' : ORANGE); }
};
/* a speech bubble (low-res box, frame text), each line typed on from its own time; the tail points down to tailX */
const bubble = (k, d, lines, ats, X, Y, w, tailX, o = {}) => {
  if (k.T < ats[0]) return null;
  const {P} = d, up = d.ease(ats[0], 5, 16), y = Y + up, h = 12 + lines.length * 24;
  P(X + 3, y + 3, w, h, INK); P(X, y, w, h, o.bg || CREAM); P(X, y, 3, h, o.edge || ORANGE);
  for (let i = 0; i < 6; i++) P(tailX - 6 + i, y + h + i, 12 - 2 * i, 1, o.bg || CREAM);
  lines.forEach((s, i) => {
    if (k.T < ats[i]) return;
    const n = Math.min(s.length, Math.floor((k.T - ats[i]) * 40) + 1);
    k.text(s.slice(0, n), (X + 10) * 3, (y + 7 + i * 24) * 3, {size: 66, color: o.ink || INK});
  });
  return {x: X, y, w, h};
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'HAIL OR WEAR',
  transitions: {marks: 'dissolve', worn: 'levelselect', vent: 'mosaic', her: 'fade4', ask: 'dissolve'},
  trauma: {},
  sections: {
    /* ---- hook: frame 0 is the roof with the caption box; 0.8 s blinds to a tighter shot; 1.6 s iris to one mark ---- */
    hook: (k, T) => {
      const d = px(k), t1 = 0.8, t2 = 1.6;
      if (T < t1) field(d, {z: 1.4, ox: 20, oy: 70});
      else if (T < t2) field(d, {z: 2.2, ox: 150, oy: 70});
      else field(d, {z: 3.4, ox: 95, oy: 80});
      caption(k, d);
      k.exampleTag(930, 820, {right: true});
      k.cut(t1); k.cut(t2, {kind: 'iris'});
      return T < t1 ? {host: false} : host(k, null, 0.5);
    },

    /* ---- marks: the camera walks across the shingles; each round mark passes through the camera corners ---- */
    marks: (k, T) => {
      const t0 = k.S('marks'), d = px(k), dur = Math.max(0.5, k.S('dime') - t0), q = clamp((T - t0) / dur);
      field(d, {z: 3, ox: 30 + Math.round(q * 150), oy: 92});
      corners(d, 120, 96, 120, 96);
      caption(k, d);
      k.exampleTag(930, 820, {right: true});
      return host(k, 'point', 0.5);
    },

    /* ---- dime: one mark, big; a dime slides in beside it on "dime"; on "granules" the bare center and loose granules ---- */
    dime: (k, T) => {
      const d = px(k), tD = wordT(k, 'dime', /^dime/i, 1.0) - 0.25, tG = wordT(k, 'dime', /^granules/i, 1.6) - 0.2;
      field(d, {z: 5, ox: 118 - 36, oy: 182 - 20});
      if (T >= tD) { const sl = d.ease(tD, 6, 120); dime(d, 268 + sl, 120, 30); }
      if (T >= tG) for (let i = 0; i < 14; i++) { const ft = clamp((T - tG - i * 0.05) * 1.5); d.P(150 + Math.floor(hash(i) * 70), 110 + Math.round(ft * 220), 3, 3, i % 2 ? '#45484F' : '#6C7079'); }
      caption(k, d);
      k.exampleTag(930, 820, {right: true});
      return host(k, null, 0.5);
    },

    /* ---- worn: out to the whole roof, wear on every slope ---- */
    worn: (k, T) => {
      const t0 = k.S('worn'), d = px(k);
      field(d, {z: 0.9 + 0.1 * clamp((T - t0) / 2), ox: 0, oy: 0, worn: true});
      caption(k, d);
      k.exampleTag(930, 820, {right: true});
      return host(k, null, 0.5);
    },

    /* ---- vent: two shots side by side, the vent with a dent, the gutter smooth ---- */
    vent: (k, T) => {
      const t0 = k.S('vent'), d = px(k), tG = wordT(k, 'vent', /^gutter/i, 1.4) - 0.3, {P} = d;
      P(0, 0, 360, 417, '#1F2A40');
      [[14, 'VENT'], [186, 'GUTTER']].forEach(([x, lab], i) => {
        const up = d.ease(t0 + i * 0.25, 6, 30), on = i === 0 || T >= tG;
        P(x + 3, 103 + up, 160, 170, INK); P(x, 100 + up, 160, 170, '#3A3F4C');
        if (i === 0) {   /* a box vent: louvers, and one dent (a dark crescent with a lit rim) */
          P(x + 30, 150 + up, 100, 80, GREY); for (let r = 0; r < 6; r++) P(x + 34, 156 + r * 12 + up, 92, 4, '#6B7080');
          for (let j = -9; j <= 9; j++) for (let ii = -9; ii <= 9; ii++) if (ii * ii + j * j <= 81) d.DOT(x + 78 + ii, 186 + j + up, ii * ii + j * j <= 30 ? '#4A4E5A' : '#C9CCD3');
        } else {   /* a gutter, smooth */
          P(x + 14, 170 + up, 132, 30, '#C9CCD3'); P(x + 14, 196 + up, 132, 6, '#9AA0AD'); P(x + 14, 170 + up, 132, 3, '#FFFFFF'); P(x + 20, 202 + up, 6, 40, '#9AA0AD');
        }
        if (!on) d.dith(x, 100 + up, 160, 170, INK, 0);
        k.text(lab, (x + 80) * 3, (108 + up) * 3, {size: 66, color: on ? CREAM : GREY, align: 'center'});
        k.exampleTag(i ? 930 : (x + 8) * 3, 718 + up * 3, {right: !!i});   /* facts storyboard r0: EXAMPLE on each shot */
      });
      return host(k, null, 0.5);
    },

    /* ---- her: the driveway; she points up at the roof; her bubble on "hail" ---- */
    her: (k, T) => {
      const t0 = k.S('her'), d = px(k);
      driveway(d);
      k.client(780, 990, {role: 'homeowner', pose: 'point', mood: 'cross', scale: 0.85, face: -1, talk: T < t0 + 1.2, at: [300, 420]});
      bubble(k, d, ["IT'S HAIL."], [t0], 160, 112, 130, 254);
      k.exampleTag(42, 270);
      return host(k, null, 0.5);
    },

    /* ---- ask: the one mark again, big; HAIL and WEAR cards, a cursor moving between them; YOUR CALL? No answer. ---- */
    ask: (k, T) => {
      const t0 = k.S('ask'), d = px(k), {P} = d;
      field(d, {z: 3.4, ox: 95, oy: 80});
      P(14, 92, 334, 40, INK); P(12, 90, 334, 40, '#120D14'); P(12, 90, 334, 3, GOLD);
      k.text('YOUR CALL?', 534, 288, {size: 66, color: GOLD, align: 'center'});
      /* facts storyboard r0: both cards look the same and never change; the cursor rests between them once the question is asked */
      [['HAIL', 40], ['WEAR', 196]].forEach(([s, x], i) => { const bg = '#253048', rim = '#3B82C4';
        const up = d.ease(t0 + i * 0.1, 5, 30);
        P(x + 3, 213 + up, 124, 50, INK); P(x, 210 + up, 124, 50, bg); P(x, 210 + up, 124, 3, rim);
        k.text(s, (x + 62) * 3, (218 + up) * 3, {size: 132, color: CREAM, align: 'center'});
      });
      const tEnd = (WS().length ? WS()[WS().length - 1].end : t0 + 1.5);
      if (T >= t0 + 0.4) { const pick = Math.floor((T - t0) * 2) % 2, cx = T >= tEnd ? 180 : (pick ? 258 : 102); P(cx - 5, 194, 11, 4, GOLD); P(cx - 3, 198, 7, 4, GOLD); d.DOT(cx, 202, GOLD); }
      k.exampleTag(930, 820, {right: true});
      return host(k, 'shrug', 0.5);
    },
  },
};
const drift = (k) => { const d = px(k), off = Math.floor(k.T * 30) % 16; for (let y = 418 - 16 + off; y < 640; y += 16) { const y0 = Math.max(418, y), y1 = Math.min(640, y + 8); if (y1 > y0) d.P(0, y0, 360, y1 - y0, '#2B2033'); } };
for (const [n, f] of Object.entries(window.SCENE.sections)) window.SCENE.sections[n] = (k, T) => { const r = f(k, T); drift(k); return r; };
