/* Scene: Damage or not (proven, our own version of research/PROVEN.md row 3; Nov 8, 2026). One function per top-level  */
/* cue in 03_cues/cues.md; every time from a cue start or a spoken word (wordT). Worlds: hook = the cover over a storm  */
/* sky, the roof close-up, the driveway with the homeowner (k.client, EXAMPLE); trap = a split, SAY NO / SAY YES, her   */
/* phone and the adjuster (k.client buyer role); send = the estimator's card (k.sendCard), held still; receipt =        */
/* Triple-I's line, then the gauge (k.sets.gauge); why = the tablet, four photos, both of them looking; button = the     */
/* roof again with the chalk square, the question and two choice cards. Every person and line here is ours (EXAMPLE).   */
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

/* ---- worlds ---- */
/* hail falling: every stone worked out from the time alone */
const hail = (d, n = 36, y0 = 0, y1 = 417, sp = 7) => {
  for (let i = 0; i < n; i++) {
    const x = Math.floor((hash(i + 11) * 360 + d.F * 0.6) % 360), y = y0 + Math.floor((hash(i + 57) * (y1 - y0) + d.F * sp * (0.7 + hash(i) * 0.6)) % (y1 - y0));
    d.P(x, y, 2, 2, '#E6E9F0'); d.DOT(x, y - 2, '#9AA0AD');
  }
};
const stormSky = (d) => {
  d.P(0, 0, 360, 417, '#1F2A40');
  for (let b = 0; b < 4; b++) { const y = 70 + b * 26, off = Math.floor(d.F / (6 + b * 2)) % 60; for (let x = -60 + off; x < 360; x += 60) { d.P(x, y, 44, 10, b % 2 ? '#2B3A4E' : '#253048'); d.P(x + 6, y - 4, 30, 4, b % 2 ? '#2B3A4E' : '#253048'); } }
  d.P(0, 330, 360, 87, '#2B2033'); d.P(0, 330, 360, 2, '#3D2E45');
  hail(d, 40);
};
/* the roof close-up (design r0: a sloped shingle field, not a wall): a ridge cap at the top, rows of staggered tabs that  */
/* fall to the right, granules, round bruises 36 px across (dark center, a lighter ring where granules are knocked off) */
/* and one streaky worn patch. All ours (EXAMPLE). */
const MARKS = [[70, 150, 'hit'], [146, 128, 'hit'], [118, 206, 'hit'], [204, 244, 'hit'], [262, 176, 'wear'], [96, 262, 'hit'], [276, 286, 'hit']];
const SQ = {x: 76, y: 140, w: 156, h: 148};   /* the chalk square, in low-res units */
const TILT = 0.07;
const bruise = (d, x, y, r = 7) => {
  for (let j = -r; j <= r; j++) for (let i = -r; i <= r; i++) { const q = i * i + j * j; if (q <= r * r) d.DOT(x + i, y + j, q <= (r - 3) * (r - 3) ? '#1E2026' : (q <= (r - 1) * (r - 1) ? '#8A8E96' : '#6E727A')); }
  d.DOT(x - 1, y - 1, '#2E3036'); d.DOT(x + 1, y, '#14161A');
};
const roof = (d, o = {}) => {
  const {P, DOT} = d;
  P(0, 0, 360, 417, '#2A2C33');
  for (let r = 0; r < 19; r++) {
    const off = r % 2 ? 11 : 0;
    for (let x = -off; x < 360; x += 22) {
      const y = 96 + r * 13 + Math.floor((x + 11) * TILT), c = ['#5B5F68', '#53575F', '#62666E', '#575B63'][Math.floor(hash(r * 17 + x) * 4)];
      P(x + 1, y, 21, 12, c); P(x + 1, y + 11, 21, 2, '#2E3036'); P(x, y, 1, 13, '#2E3036');
      for (let i = 0; i < 5; i++) DOT(x + 2 + Math.floor(hash(r * 7 + x + i) * 19), y + 2 + Math.floor(hash(r + x * 3 + i) * 8), i % 2 ? '#6C7079' : '#45484F');
    }
  }
  for (let x = 0; x < 360; x++) { const y = 84 + Math.floor(x * TILT); P(x, 84, 1, y - 84 + 12, '#3E4148'); DOT(x, y + 11, '#24262B'); }   /* the ridge cap */
  for (let x = 0; x < 360; x += 16) { const y = 84 + Math.floor(x * TILT); P(x, y + 2, 14, 8, '#4A4D55'); }
  P(0, 334, 360, 8, GREY); P(0, 342, 360, 3, '#6B7080'); P(0, 345, 360, 72, '#2B2033');   /* the gutter edge */
  MARKS.forEach(([x, y, kind]) => {
    if (kind === 'hit') bruise(d, x, y);
    else { for (let i = 0; i < 6; i++) { P(x - 16 + i * 2, y - 8 + i * 3, 30 - i * 3, 2, i % 2 ? '#8A7A66' : '#7A6C5A'); } DOT(x + 8, y - 6, '#9A8A74'); }
  });
  if (o.ring != null && o.ring > 0) d.ring(MARKS[2][0], MARKS[2][1], 12, CHALK, 0, o.ring); d.ring(MARKS[2][0], MARKS[2][1], 13, CHALK, 0, o.ring);   /* the chalk ring on "damage" */
  if (o.square) {   /* chalk lines draw on */
    const q = clamp(o.square), per = 2 * (SQ.w + SQ.h), L = Math.floor(per * q);
    for (let i = 0; i < L; i += 1) {
      let x, y; if (i < SQ.w) { x = SQ.x + i; y = SQ.y; } else if (i < SQ.w + SQ.h) { x = SQ.x + SQ.w; y = SQ.y + i - SQ.w; } else if (i < 2 * SQ.w + SQ.h) { x = SQ.x + SQ.w - (i - SQ.w - SQ.h); y = SQ.y + SQ.h; } else { x = SQ.x; y = SQ.y + SQ.h - (i - 2 * SQ.w - SQ.h); }
      P(x, y, 2, 2, CHALK);
    }
  }
};
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
/* the split for the trap: two halves on a slant, each dimmed until its beat */
const split = (d, litL, litR) => {
  const {P} = d;
  for (let y = 0; y < 417; y++) {
    const bx = 180 + Math.round((200 - y) * 0.12);
    P(0, y, bx, 1, '#1F3B3A'); P(bx, y, 360 - bx, 1, '#3B1F2A'); P(bx - 1, y, 3, 1, GOLD);
  }
  for (let i = 0; i < 22; i++) { const y = 160 + Math.floor(hash(i) * 170),   /* design r0: clear of the label rows */ x = ((Math.floor(hash(i + 9) * 400 + d.F * (i % 2 ? 6 : -6)) % 400) + 400) % 400 - 20; P(x, y, 24, 2, i % 2 ? '#6A3A4A' : '#3E6E6A'); }   /* code QA r0 flat: more, brighter speed lines */
  if (!litL) for (let y = 84; y < 340; y++) { const bx = 180 + Math.round((200 - y) * 0.12); d.dith(0, y, bx - 1, 1, INK, y & 1); }
  if (!litR) for (let y = 84; y < 340; y++) { const bx = 180 + Math.round((200 - y) * 0.12); d.dith(bx + 2, y, 360 - bx - 2, 1, INK, y & 1); }
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'DAMAGE OR NOT',
  sendLine: 'Send this to your estimator before the next storm.',
  transitions: {trap: 'levelselect', send: 'dissolve', receipt: 'mosaic', why: 'fade4', button: 'gameover'},
  trauma: {},
  sections: {
    /* ---- hook: frame 0 is the cover (k.coverBoard) over the storm; 0.7 s blinds to the roof close-up with the hook on */
    /* a plate; 2.3 s iris to the driveway, her arms folded; her bubble on "sure", "written", "insurance"; TODAY. ---- */
    hook: (k, T) => {
      const d = px(k), tRoof = 0.7, tDrive = 2.3;
      if (T < tRoof) {
        stormSky(d);
        k.coverBoard({hero: 'HAIL DAMAGE?', lines: ['OR JUST AN OLD ROOF?'], example: true, y: 300});
        k.cut(tRoof);
        return {host: false};
      }
      if (T < tDrive) {
        roof(d, {ring: clamp((T - (wordT(k, 0, /^damage/i, 0.9) - 0.1)) / 0.4)});   /* design r0: chalk-circle one bruise on "damage" */
        hail(d, 18, 84, 330, 6);
        d.P(16, 92, 334, 66, INK); d.P(14, 90, 334, 66, '#253048'); d.P(14, 90, 334, 3, '#3B82C4');
        k.text('HAIL DAMAGE?', 540, 288, {size: 66, color: ORANGE, align: 'center'});
        k.text('OR JUST AN OLD ROOF?', 540, 366, {size: 66, color: CREAM, align: 'center'});
        k.exampleTag(930, 480, {right: true});
        k.cut(tRoof); k.cut(tDrive, {kind: 'iris'});
        return host(k, null);   /* render critic r0: his pointing arm crossed the dialog box */
      }
      const tShe = k.S('hook.she'), tWrit = wordT(k, 'hook.she', /^written/i, 1.6) - 0.1, tIns = wordT(k, 'hook.she', /^insurance/i, 2.4) - 0.1, tToday = k.S('hook.today'), tWants = wordT(k, 'hook.she', /^wants/i, 1.3);
      driveway(d);
      const pose = T >= tToday + 0.4 ? 'refuse' : T >= tWants ? 'argue' : T >= tShe ? 'point' : 'refuse';
      k.client(780, 990, {role: 'homeowner', pose, mood: 'cross', scale: 0.85, face: -1, talk: T >= tShe && T < tToday + 0.4, at: [300, 420]});
      bubble(k, d, ["IT'S HAIL.", 'WRITE IT UP FOR', 'MY INSURANCE.'], [tShe, tWrit, tIns], 118, 92, 178, 254);
      if (T >= tToday) stampBox(k, 'TODAY.', 780, 506, tToday, {color: RED, bg: CREAM, size: 66, freeze: 4});
      k.exampleTag(42, 270);   /* its own row, left of the bubble, clear of the roof (stills r0) */
      k.cut(tDrive, {kind: 'iris'});
      return host(k, T >= tShe ? null : 'stand');
    },

    /* ---- trap: the split, both halves dim; SAY NO lights on "no" (her phone, SHE CALLS / ANOTHER ROOFER); SAY YES on */
    /* "yes" (the adjuster, NOT HAIL. WEAR.); YOUR WORD VS HIS stamps on "word" ---- */
    trap: (k, T) => {
      const d = px(k), tNo = k.S('trap.no'), tYes = k.S('trap.yes'), tWord = k.S('trap.word');
      split(d, T >= tNo, T >= tYes);
      k.text('SAY NO', 72, 268, {size: 66, color: T >= tNo ? TEAL : GREY});
      k.text('SAY YES', 930 - k.measure('SAY YES', {size: 66}), 268, {size: 66, color: T >= tYes ? RED : GREY});
      k.client(330, 980, {role: 'homeowner', pose: T >= tNo ? 'phone' : 'refuse', mood: 'cross', scale: 0.62, face: 1});
      k.client(830, 980, {role: 'buyer', pose: 'refuse', mood: T >= tYes ? 'smug' : 'calm', scale: 0.62, face: -1, talk: T >= tYes && T < tWord});
      if (T >= tNo) {
        k.text('SHE CALLS', 72, 350, {size: 52, color: CREAM});
        k.text('ANOTHER ROOFER', 72, 410, {size: 52, color: GOLD});
        k.exampleTag(72, 480);
      }
      if (T >= tYes) {
        k.text('THE ADJUSTER', 930 - k.measure('THE ADJUSTER', {size: 52}), 350, {size: 52, color: CREAM});
        k.exampleTag(930, 420, {right: true});
        if (T < tWord) bubble(k, d, ['NOT HAIL.', 'WEAR.'], [tYes + 0.5, tYes + 0.8], 196, 168, 100, 276, {edge: RED});   /* stills r0: inside x 930, under the tag; gone when the stamp lands */
      }
      if (T >= tWord) stampBox(k, 'YOUR WORD VS HIS', 540, 560, tWord, {color: GOLD, bg: NIGHT, size: 66, freeze: 4});   /* stills r0: above both heads */
      const tLose = wordT(k, 'trap', /^lose/i, 1.4) - 0.1;   /* design r0: the host out at the left, a shrug on "you lose either way", a lean on "your word against his" */
      return host(k, T >= tWord ? 'lean' : (T >= tLose && T < tLose + 1.6 ? 'shrug' : null), 0.55, 150);
    },

    /* ---- send: the estimator's card slides up and holds dead still; each step goes to ink on its words ---- */
    send: (k, T) => {
      const t0 = k.S('send'), d = px(k);
      const on = [true, true, true, true];   /* send r0: all four lit from the moment the card lands, so any screenshot is the whole list */
      d.P(0, 0, 360, 417, '#253048'); const so = (d.F * 2) % 24; for (let x = so - 24; x < 360; x += 24) d.P(Math.max(0, x), 0, Math.max(0, Math.min(x + 12, 360) - Math.max(0, x)), 417, '#34466A');   /* the stripes drift; the card never moves */
      hail(d, 60, 0, 417, 8);   /* code QA r0 flat (20.0 to 25.3 s): hail falls behind the card, never over it */
      const c = k.sendCard({at: t0, who: 'FOR THE ESTIMATOR', title: 'BEFORE YOU SAY HAIL', steps: ['THE HOUSE AND ADDRESS', 'A CHALK SQUARE EACH SLOPE', 'EVERY HIT CIRCLED, TAPE BESIDE IT', 'VENTS AND GUTTERS']   /* send r0: the tape is on the card too */, stepOn: on, example: true, colors: {step: '#A7ABB5'}});   /* stills r0: unlit steps lighter, so each lights clearly */
      return host(k, c ? 'point' : null);
    },

    /* ---- receipt: the gauge from the cue (0.3 s before "Triple-I"): the source on top, AS MUCH AS over the number, the */
    /* needle and the 80% on "eighty", the plate under it; on "storm after storm" a four-step fade to Triple-I's line, */
    /* typed on with its full tag (lint r0: every word on screen lands before the voice says it) ---- */
    receipt: (k, T) => {
      const d = px(k), n = k.data.numbers.share, tE = wordT(k, 'receipt.share', /^eighty/i, 0.6), tQ = k.S('receipt.again');
      if (T < tQ) {
        k.sets.gauge({value: n.value, max: 100, at: tE - 0.3, dur: 1.0, readout: false, labels: false, zones: [[0, 40, DTEAL], [40, 70, ORANGE], [70, 100, RED]]});
        d.P(0, 88, 360, 26, '#2B2033'); d.P(0, 114, 360, 2, '#3D2E45');   /* design r0: a visor band, so the source never runs into the ring */
        k.text('Source: Triple-I, Apr 14, 2026', 540, 276, {size: 52, color: SAND, align: 'center', drop: INK});
        d.P(136, 224, 104, 70, INK); d.P(138, 226, 100, 66, '#1A332B');   /* design r0: narrower, clear of the 0 and the 100 */
        k.text('100', 732, 744, {size: 39, color: '#C9CCD3'});
        k.text('AS MUCH AS', 564, 676, {size: 52, color: GOLD, align: 'center'});
        if (T >= tE - 0.3) { const rise = clamp((T - tE + 0.3) / 0.6), v = Math.round(n.value * eo(rise)); k.text(rise >= 1 ? n.shown : v + '%', 564, 734, {size: 132, color: ORANGE, align: 'center', drop: INK, lint: rise >= 1}); }
        d.P(102, 292, 210, 48, INK); d.P(100, 290, 210, 48, NIGHT); d.P(100, 290, 210, 3, GOLD);
        k.text('OF SEVERE STORM CLAIMS', 330, 884, {size: 52, color: CREAM});
        k.text('IN A YEAR ARE HAIL', 330, 942, {size: 52, color: GOLD});
        k.cut(tQ, {kind: 'fade4'});
        return host(k, T >= tE ? 'point' : null);
      }
      d.P(0, 0, 360, 417, '#1F2A40'); hail(d, 24, 0, 417, 5);
      const up = d.ease(tQ, 6, 30);
      d.P(18, 88 + up, 330, 240, INK); d.P(14, 84 + up, 330, 240, CREAM); d.P(14, 84 + up, 330, 26, DTEAL);
      k.text('TRIPLE-I', 72, 266 + up * 3, {size: 66, color: CREAM});
      if (!up) {
        const q = '"Hail alone accounts for as much as ' + n.shown + ' of severe convective storm claims in any given year"';
        let left = Math.max(0, Math.floor((T - tQ - 0.2) * 80));
        k.wrap(q, {size: 66}, 840).forEach((ln, i) => { const m = Math.min(ln.length, left); left -= m; if (m) k.text(ln.slice(0, m), 72, 362 + i * 76, {size: 66, color: INK}); });
        k.sourceTag('Source: Triple-I release, severe convective storms, Apr 14, 2026 (Business Wire). Read Nov 8, 2026.', 72, 700, {color: SLATE});
      }
      k.cut(tQ, {kind: 'fade4'});
      return host(k);
    },

    /* ---- why: the high-score table, PHOTOS SEEN: YOU, HER, ADJUSTER, each 4 (the same four shots); SAME PHOTOS on    */
    /* "Same photos", SAME ROOF on "roof" (lint r0: three new set pieces against the two lessons before) ---- */
    why: (k, T) => {
      const t0 = k.S('why'), d = px(k), tAdj = k.S('why.adjuster'), tSame = wordT(k, 'why.adjuster', /^same$/i, 1.6) - 0.25, tRoof = wordT(k, 'why.adjuster', /^roof/i, 2.4) - 0.25;
      const tHer = wordT(k, 'why', /^she$/i, 0.2) - 0.25;
      /* the rows land on "she", near "you" and on "and so does the adjuster" (one gap, so the third lands on its cue) */
      k.sets.scores({title: 'PHOTOS SEEN', size: 52, t0: tHer,   /* render critic r0: the table at 52 (sets.js scores size) */
        gap: Math.max(0.3, (tAdj - tHer) / 2), count: 0.4, rows: [
        {name: 'HER', value: 4, from: 0, suffix: ' PHOTOS'},
        {name: 'YOU', value: 4, from: 0, suffix: ' PHOTOS'},
        {name: 'ADJUSTER', value: 4, from: 0, suffix: ' PHOTOS', hi: true},
      ]});
      k.exampleTag(930, 700, {right: true});   /* stills r1: clear of the stamps */
      if (T >= tSame) stampBox(k, 'SAME PHOTOS', 480, 660, tSame, {color: GOLD, bg: NIGHT, size: 66, freeze: 4});
      if (T >= tRoof) stampBox(k, 'SAME ROOF', 480, 786, tRoof, {color: TEAL, bg: NIGHT, size: 66, freeze: 4});
      return host(k, null, 0.5, 150);
    },

    /* ---- button: the two calls face off (k.sets.versus, no winner: the viewer picks), the hits under each card; on    */
    /* "what" the question; a cursor moves between the cards twice a second ---- */
    button: (k, T) => {
      const t0 = k.S('button'), d = px(k), tQ = wordT(k, 'button', /^what$/i, 2.0) - 0.25;
      k.sets.versus({a: {name: 'HAIL DAMAGE', icon: 'hammer'}, b: {name: 'JUST WEAR', icon: 'clock'}, at: t0, vsAt: t0 + 0.4, iconScale: 8});   /* design r0: icons 2x */
      d.P(16, 214, 330, 40, INK); d.P(14, 212, 330, 40, '#253048'); d.P(14, 212, 330, 3, '#3B82C4');
      k.text(T >= tQ ? 'WHAT WOULD YOU TELL HER?' : 'LET THE PHOTOS MAKE THE CALL', 540, 654, {size: 66, color: T >= tQ ? GOLD : CREAM, align: 'center'});
      k.exampleTag(930, 780, {right: true});
      if (T >= tQ) { const pick = Math.floor((T - tQ) * 2) % 2, cx = pick ? 246 : 90; d.P(cx - 4, 262, 9, 3, GOLD); d.P(cx - 2, 265, 5, 3, GOLD); d.DOT(cx, 268, GOLD); }
      return host(k, T >= tQ ? 'shrug' : 'point');
    },
  },
};
/* a faint dither drifts down the empty lower band of every scene, below the host and every text, so no stretch goes   */
/* still (code QA, flat). */
const drift = (k) => { const d = px(k), off = Math.floor(k.T * 30) % 16; for (let y = 418 - 16 + off; y < 640; y += 16) { const y0 = Math.max(418, y), y1 = Math.min(640, y + 8); if (y1 > y0) d.P(0, y0, 360, y1 - y0, '#2B2033'); } };
for (const [n, f] of Object.entries(window.SCENE.sections)) window.SCENE.sections[n] = (k, T) => { const r = f(k, T); drift(k); return r; };
