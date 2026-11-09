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


/* ---- the shingle field at any zoom (design r0: asphalt shingles, not a stone wall). Field units are low-res pixels at */
/* z 1; (ox, oy) is the field point at the shot's top left; courses fall to the right. Each course: a dark shadow band */
/* where it tucks under the course above, three tabs a strip (slots every 12), granule speckle in three greys. Marks are */
/* irregular bruises: a dark crushed center, a lighter rim of bare mat, loose granules beside them. All ours (EXAMPLE). */
const FMARKS = [[60, 118], [150, 100], [118, 182], [222, 148], [300, 120], [264, 214], [80, 262], [196, 284]];
const TILTF = 0.08;
const fxy = (o) => { const z = o.z || 1, ox = o.ox || 0, oy = o.oy || 0; return {z, X: (fx) => Math.round((fx - ox) * z), Y: (fx, fy) => Math.round(84 + (fy - oy) * z + (fx - ox) * z * TILTF)}; };
const focus = (fx, fy, z, sx, sy) => ({z, ox: fx - sx / z, oy: fy - (sy - 84 - sx * TILTF) / z});
const field = (d, o = {}) => {
  const {P} = d, {z, X, Y} = fxy(o), u = Math.max(1, Math.round(z));
  P(0, 0, 360, 417, '#2A2C33');
  for (let r = -2; r < 34; r++) {
    const fy = r * 13, off = (r * 6) % 36;
    for (let fx = -off - 36; fx < 420; fx += 12) {
      const x0 = X(fx), y0 = Y(fx, fy), w = Math.ceil(12 * z);
      if (x0 > 360 || x0 + w < 0 || y0 > 340 || y0 + 13 * z < 70) continue;
      const k2 = Math.floor(hash(r * 31 + Math.floor((fx + off) / 12) * 7) * 3);
      P(x0, y0, w, Math.ceil(13 * z), ['#575B63', '#5E626A', '#52565E'][k2]);
      P(x0, y0, w, Math.max(1, Math.round(3 * z)), '#2B2D33');   /* the shadow band under the course above */
      if (((fx + off) / 12) % 3 === 0) P(x0, y0, u, Math.ceil(13 * z), '#1E2026');   /* a tab slot every third */
      for (let i = 0; i < 4; i++) P(x0 + Math.floor(hash(r * 7 + fx + i) * 11) * z, y0 + (4 + Math.floor(hash(r + fx * 3 + i) * 8)) * z, u, u, ['#6C7079', '#45484F', '#63676F'][i % 3]);
      if (o.worn) {   /* wear: light streaks downslope, a curled tab edge with its shadow, bare patches spread evenly */
        const h = hash(r * 13 + fx * 0.7);
        if (h < 0.35) P(x0 + Math.floor(h * 30) * z % w, y0 + 3 * z, u, 9 * z, '#7E828A');
        if (h > 0.82) { P(x0, y0 + 11 * z, w, u, '#9AA0AD'); P(x0, y0 + 12 * z, w, u, '#14161A'); }
        if (Math.abs(h - 0.6) < 0.04) P(x0 + 3 * z, y0 + 5 * z, 5 * z, 3 * z, '#8A7A66');
      }
    }
  }
  FMARKS.forEach(([fx, fy], m) => {
    const cx = X(fx), cy = Y(fx, fy), r = Math.max(2, Math.round(6 * z));
    if (cy < 70 || cy > 345) return;
    [[0.4, -0.25, 0.7, 0], [-0.35, 0.3, 0.7, 0], [0, 0, 1, 1]].forEach(([dx, dy, k3, core]) => {   /* an irregular bruise: two rim blobs of bare mat, then one dark crushed center (stills r1: not twin holes) */
      const R = Math.max(2, Math.round(r * k3)), bx = cx + Math.round(dx * r), by = cy + Math.round(dy * r);
      for (let j = -R; j <= R; j++) for (let i = -R; i <= R; i++) { const q = i * i + j * j + (hash(m * 5 + i * 3 + j) > 0.8 ? R : 0); if (q <= R * R && by + j >= 84 && by + j < 334) d.DOT(bx + i, by + j, core && q <= (R * 0.55) * (R * 0.55) ? '#1E2026' : (core ? '#8A7A66' : '#7A6C5A')); }
    });
    for (let i = 0; i < 5; i++) P(cx + Math.round((hash(m * 9 + i) - 0.5) * 4 * r), cy + Math.round(r * (1.1 + hash(m + i * 3) * 0.8)), u, u, '#45484F');   /* loose granules */
  });
  P(0, 334, 360, 8, GREY); P(0, 342, 360, 3, '#6B7080'); P(0, 345, 360, 72, '#2B2033');   /* the drip edge and gutter line */
};
/* the caption box across the middle, like a phone clip's (frame 0 on; it stays up on every roof shot) */
const caption = (k, d) => {
  d.P(14, 94, 334, 64, INK); d.P(12, 92, 334, 64, '#120D14'); d.P(12, 92, 334, 3, GOLD);   /* design r0: up top, so the marks show whole */
  k.text('HAIL OR WEAR?', 534, 288, {size: 132, color: CREAM, align: 'center', drop: INK});
  k.text('YOU CALL IT.', 534, 410, {size: 66, color: GOLD, align: 'center'});
};
/* white camera corners around a box (low-res), no words */
const corners = (d, x, y, w, h) => { const L = 10, c = CREAM; [[x, y, 1, 1], [x + w, y, -1, 1], [x, y + h, 1, -1], [x + w, y + h, -1, -1]].forEach(([a, b, sx, sy]) => { d.P(sx > 0 ? a : a - L, b - (sy > 0 ? 0 : 2), L, 2, c); d.P(a - (sx > 0 ? 0 : 2), sy > 0 ? b : b - L, 2, L, c); }); };
/* a dime: a silver disc with a rim and a glint */
const dime = (d, cx, cy, r) => { for (let j = -r; j <= r + 2; j++) for (let i = -r; i <= r; i++) { const q = i * i + j * j, q2 = i * i + (j - 2) * (j - 2); if (q <= r * r) d.DOT(cx + i, cy + j, q >= (r - 2) * (r - 2) ? '#9AA0AD' : (q >= (r - 3) * (r - 3) ? '#E6E9F0' : '#C9CCD3')); else if (q2 <= r * r) d.DOT(cx + i, cy + j, '#6B7080'); } d.P(cx - Math.round(r / 2), cy - Math.round(r / 2), 4, 2, '#FFFFFF'); };   /* design r0: a coin, rim, edge band, no face */
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
    /* ---- hook: frame 0 is the roof with the caption box; 0.8 s blinds to a tighter shot; 1.6 s iris to one mark. The */
    /* caption box is drawn over the cuts, so the question holds (design r0) ---- */
    hook: (k, T) => {
      const d = px(k), t1 = 0.8, t2 = 1.6;
      if (T < t1) field(d, {z: 1.4, ox: 20, oy: 40});
      else if (T < t2) field(d, focus(222, 148, 2.4, 180, 250));
      else field(d, focus(118, 182, 4, 180, 260));
      k.cut(t1); k.cut(t2, {kind: 'iris'});
      caption(k, d);
      k.exampleTag(930, 480, {right: true});
      return T < t1 ? {host: false} : host(k, null, 0.5);
    },

    /* ---- marks: the camera walks across the shingles; each mark passes through the camera corners ---- */
    marks: (k, T) => {
      const t0 = k.S('marks'), d = px(k), dur = Math.max(0.5, k.S('dime') - t0), q = clamp((T - t0) / dur);
      field(d, focus(60 + q * 170, 118 + q * 40, 3, 180, 250));
      corners(d, 132, 200, 96, 96);
      caption(k, d);
      k.exampleTag(930, 480, {right: true});
      return host(k, 'point', 0.5);
    },

    /* ---- dime: one mark, whole and big; a coin slides in touching it, the same size; on "granules" a push in on the */
    /* bare center and loose granules collecting at the drip edge ---- */
    dime: (k, T) => {
      const d = px(k), tD = wordT(k, 'dime', /^dime/i, 1.0) - 0.25, tG = wordT(k, 'dime', /^granules/i, 1.6) - 0.2;
      const z = T < tG ? 5 : 5 + 2 * eo((T - tG) / 0.5), r = Math.round(6 * z);
      field(d, focus(118, 182, z, 150, 250));
      if (T >= tD && T < tG) { const sl = d.ease(tD, 6, 120); dime(d, 150 + 2 * r + 2 + sl, 250, r); }
      if (T >= tG) for (let i = 0; i < 18; i++) { const ft = clamp((T - tG - i * 0.04) * 1.8), x = 110 + Math.floor(hash(i) * 120), y = Math.min(330 - (i % 3), 250 + Math.round(ft * 90)); d.P(x, y, 3, 3, i % 2 ? '#8A8E96' : '#6C7079'); }
      caption(k, d);
      k.exampleTag(930, 480, {right: true});
      return host(k, null, 0.5);
    },

    /* ---- worn: out to the whole roof: streaks downslope, curled tab edges, bare patches spread evenly ---- */
    worn: (k, T) => {
      const t0 = k.S('worn'), d = px(k);
      field(d, {z: 1.6 + 0.2 * clamp((T - t0) / 2), ox: 10, oy: 60, worn: true});
      caption(k, d);
      k.exampleTag(930, 480, {right: true});
      return host(k, null, 0.5);
    },

    /* ---- vent: two shots side by side, the vent with a dent, the gutter smooth ---- */
    vent: (k, T) => {
      const t0 = k.S('vent'), d = px(k), tG = wordT(k, 'vent', /^gutter/i, 1.4) - 0.3, {P} = d;
      P(0, 0, 360, 417, '#1F2A40'); P(0, 334, 360, 8, GREY); P(0, 342, 360, 3, '#6B7080'); P(0, 345, 360, 72, '#2B2033');   /* design r0: the ledge under the host */
      [[14, 'VENT'], [186, 'GUTTER']].forEach(([x, lab], i) => {
        const up = d.ease(t0 + i * 0.25, 6, 30), on = i === 0 || T >= tG;
        P(x + 3, 103 + up, 160, 170, INK); P(x, 100 + up, 160, 170, '#3A3F4C');
        if (i === 0) {   /* a box vent on its strip of roof; the dent is a crescent shadow on a bent louver (design r0) */
          P(x + 6, 220 + up, 148, 44, '#575B63'); for (let r = 0; r < 3; r++) P(x + 6, 220 + r * 14 + up, 148, 3, '#2B2D33');
          P(x + 30, 140 + up, 100, 84, GREY); for (let r = 0; r < 6; r++) P(x + 34, 146 + r * 12 + up, 92, 4, '#6B7080');
          for (let ii = -12; ii <= 12; ii++) { const yy = Math.round(Math.sqrt(Math.max(0, 144 - ii * ii)) * 0.5); P(x + 84 + ii, 176 + yy + up, 1, 3, '#3A3D44'); P(x + 84 + ii, 174 + yy + up, 1, 1, '#E6E9F0'); }
        } else {   /* a K-style gutter hung on the roof edge, smooth, with its downspout elbow */
          P(x + 6, 140 + up, 148, 40, '#575B63'); for (let r = 0; r < 3; r++) P(x + 6, 140 + r * 13 + up, 148, 3, '#2B2D33');
          P(x + 6, 180 + up, 148, 6, GREY);
          P(x + 10, 186 + up, 140, 26, '#C9CCD3'); P(x + 10, 186 + up, 140, 3, '#FFFFFF'); P(x + 10, 196 + up, 140, 2, '#9AA0AD'); P(x + 10, 208 + up, 140, 4, '#9AA0AD');
          P(x + 120, 212 + up, 14, 10, '#9AA0AD'); P(x + 126, 222 + up, 14, 40, '#C9CCD3'); P(x + 126, 222 + up, 3, 40, '#FFFFFF');
        }
        if (!on) d.dith(x, 100 + up, 160, 170, INK, 0);
        k.text(lab, (x + 80) * 3, (108 + up) * 3, {size: 66, color: on ? CREAM : GREY, align: 'center'});
        k.exampleTag(i ? 930 : (x + 8) * 3, 718 + up * 3, {right: !!i});   /* facts storyboard r0: EXAMPLE on each shot */
      });
      return host(k, null, 0.5);
    },

    /* ---- her: a close two-shot at the foot of the ladder (design r0: not damage-or-not's driveway): the roof edge with the */
    /* vent at the top, siding, the ladder; she points up; her bubble on "hail" ---- */
    her: (k, T) => {
      const t0 = k.S('her'), d = px(k), {P} = d;
      P(0, 0, 360, 417, '#3A4A5E');
      field(d, {z: 2, ox: 0, oy: 130});
      P(0, 150, 360, 190, SAND); for (let y = 156; y < 340; y += 9) P(0, y, 360, 1, '#CDBA9F');
      P(0, 146, 360, 6, GREY);
      P(120, 112, 40, 32, GREY); for (let r = 0; r < 3; r++) P(123, 116 + r * 9, 34, 3, '#6B7080');
      for (let y = 140; y < 336; y++) { const xl = 96 + Math.round((336 - y) * 0.18); P(xl, y, 3, 1, '#9AA0AD'); P(xl + 30, y, 3, 1, '#9AA0AD'); if ((y - 140) % 18 === 0) P(xl, y, 33, 2, '#C9CCD3'); }
      P(0, 336, 360, 81, '#4B5F2A');
      k.client(800, 1000, {role: 'homeowner', pose: 'point', mood: 'cross', scale: 1.0, face: -1, talk: T < t0 + 1.2, at: [420, 400]});
      bubble(k, d, ["IT'S HAIL."], [t0], 176, 176, 108, 266);
      k.exampleTag(42, 480);
      return host(k, null, 0.5);
    },

    /* ---- ask (from "and you're the estimator", so the cards hold about 3 s; design r0): the one mark, big; HAIL and WEAR */
    /* cards, identical and unchanging; a big cursor moves between them, then rests between them from the last word on */
    /* (facts r0: never on a card while "wear?" is said) ---- */
    ask: (k, T) => {
      const t0 = k.S('ask'), d = px(k), {P} = d;
      field(d, focus(118, 182, 4, 180, 190));
      P(14, 94, 334, 40, INK); P(12, 92, 334, 40, '#120D14'); P(12, 92, 334, 3, GOLD);
      k.text('YOUR CALL?', 534, 294, {size: 66, color: GOLD, align: 'center'});
      [['HAIL', 70], ['WEAR', 196]].forEach(([s2, x], i) => {
        const up = d.ease(t0 + i * 0.1, 5, 30), bg = '#253048', rim = '#3B82C4';
        P(x + 3, 263 + up, 110, 50, INK); P(x, 260 + up, 110, 50, bg); P(x, 260 + up, 110, 3, rim);
        k.text(s2, (x + 55) * 3, (268 + up) * 3, {size: 132, color: CREAM, align: 'center'});
      });
      const ws = WS(), tRest = ws.length ? ws[ws.length - 1].start : t0 + 2.5;
      if (T >= t0 + 0.4) { const pick = Math.floor((T - t0) * 2) % 2, cx = T >= tRest ? 188 : (pick ? 251 : 125); P(cx - 9, 232, 19, 6, GOLD); P(cx - 6, 238, 13, 6, GOLD); P(cx - 3, 244, 7, 6, GOLD); P(cx - 1, 250, 3, 4, GOLD); }
      k.exampleTag(930, 480, {right: true});
      return host(k, 'shrug', 0.5);
    },
  },
};
const drift = (k) => { const d = px(k), off = Math.floor(k.T * 30) % 16; for (let y = 418 - 16 + off; y < 640; y += 16) { const y0 = Math.max(418, y), y1 = Math.min(640, y + 8); if (y1 > y0) d.P(0, y0, 360, y1 - y0, '#2B2033'); } };
for (const [n, f] of Object.entries(window.SCENE.sections)) window.SCENE.sections[n] = (k, T) => { const r = f(k, T); drift(k); return r; };
