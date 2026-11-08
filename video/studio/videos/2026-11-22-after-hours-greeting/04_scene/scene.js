/* Scene: The message that plays after five (proven, our own version of research/PROVEN.md row 7; Nov 7, 2026). One      */
/* function per top-level cue in 03_cues/cues.md; every time from a cue start or a spoken word (wordT). Worlds: hook and  */
/* button = our house at night with her phone (EXAMPLE); receipt = ServiceTitan's own line on a card, then the gauge from */
/* data.js; send = the voicemail settings screen, held still (the send card, cue marked [send]); versus = our two         */
/* messages side by side (no stats, no winner: not data); texts = the chat in the truck. Numbers only from k.data.        */
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

/* ================================================================================================================ */
/* our house at night: stars that blink, a thin moon, the house with one lit kitchen window, light snow falling        */
const house = (k, d, o = {}) => {
  const {P, DOT, dith, F} = d;
  P(0, 0, 360, 417, '#16111F'); P(0, 0, 360, 70, '#100C17'); for (let y = 70; y < 130; y += 4) dith(0, y, 360, 1, '#100C17', (y / 4) % 2);
  for (let i = 0; i < 28; i++) { const x = Math.floor(hash(i * 3.3) * 360), y = Math.floor(hash(i * 7.1) * 150); if ((Math.floor(F / 9) + i) % 7) DOT(x, y, i % 3 ? '#C9CCD3' : GOLD); }
  for (let y = -6; y <= 6; y++) { const hw = Math.floor(Math.sqrt(36 - y * y)); P(300 - hw, 40 + y, hw * 2, 1, CREAM); P(303 - hw, 40 + y, hw * 2, 1, '#16111F'); }
  /* the yard and the house: wall, roof, chimney, door, the lit kitchen window with a pot on the sill */
  P(0, 360, 360, 57, '#1F2A26'); dith(0, 360, 360, 4, '#2F5A4A');
  P(30, 232, 230, 128, '#3D2E45'); P(30, 232, 230, 2, '#4A3A55');
  for (let y = 0; y < 60; y++) { const hw = Math.round(y * 2.1); P(145 - hw, 172 + y, hw * 2, 1, y % 6 ? '#2B2033' : '#231A2B'); }
  P(214, 178, 18, 40, '#2B2033'); P(212, 176, 22, 4, '#3D2E45');
  P(196, 290, 34, 70, '#2B2033'); DOT(224, 326, GOLD);
  const lit = o.dark ? '#3A3550' : GOLD;
  P(60, 262, 76, 56, INK); P(63, 265, 70, 50, lit); if (!o.dark) { P(63, 265, 70, 4, '#FFE7A8'); dith(63, 300, 70, 15, ORANGE); }
  P(97, 265, 2, 50, INK); P(63, 289, 70, 2, INK); P(76, 306, 12, 8, SLATE); P(74, 306, 16, 2, '#6B7080');
  /* light snow: every flake on whole pixels, a step every 3 frames */
  for (let i = 0; i < 70; i++) { const x = (Math.floor(hash(i * 5.7) * 360) + Math.floor(F / 9 + i)) % 360, y = (Math.floor(hash(i * 2.9) * 417) + Math.floor(F * (1 + (i % 3)) / 2)) % 417; P(x, y, 2, 2, i % 4 ? '#E6E9F0' : '#C9CCD3'); }
};
/* the kitchen at ten to seven (the close-up's world): a warm lit wall, tiles, a wall clock, the cold vent */
const kitchen = (k, d) => {
  const {P, dith, F} = d;
  P(0, 0, 360, 417, '#E8B866'); dith(0, 0, 360, 417, '#DDA955');
  for (let y = 300; y < 417; y += 12) for (let x = ((y / 12) % 2) * 12; x < 360; x += 24) P(x, y, 23, 11, '#F4E6D3');
  P(0, 296, 360, 4, '#B07A47');
  P(20, 200, 60, 30, '#8C8F99'); for (let i = 0; i < 5; i++) P(24, 204 + i * 5, 52, 2, '#5C606E');
  const fl = Math.floor(F / 6) % 2; P(30 + fl, 236, 3, 6, '#87CEEB'); P(60 - fl, 238, 3, 6, '#87CEEB');
};
/* the big kitchen wall clock: hands stepped to whole pixels, h and m as on a real face */
const clock = (k, d, cx, cy, r, h, m) => {
  const {P} = d;
  for (let y = -r - 3; y <= r + 3; y++) { const hw = Math.floor(Math.sqrt((r + 3) * (r + 3) - y * y)); P(cx - hw, cy + y, 2 * hw, 1, INK); }
  for (let y = -r; y <= r; y++) { const hw = Math.floor(Math.sqrt(r * r - y * y)); P(cx - hw, cy + y, 2 * hw, 1, CREAM); }
  for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6; P(cx + Math.round(Math.sin(a) * (r - 7)) - 1, cy - Math.round(Math.cos(a) * (r - 7)) - 1, 3, 3, i % 3 ? GREY : INK); }
  const hand = (a, len, w, c) => { for (let t = 0; t <= len; t++) P(cx + Math.round(Math.sin(a) * t) - (w >> 1), cy - Math.round(Math.cos(a) * t) - (w >> 1), w, w, c); };
  hand(((h % 12) + m / 60) * Math.PI / 6, r * 0.5, 4, INK); hand(m * Math.PI / 30, r * 0.8, 3, RED); P(cx - 3, cy - 3, 6, 6, INK);
};
const iris = (d, cx, cy, r) => { for (let y = 0; y < 417; y++) { const dy = y - cy, hw = dy * dy < r * r ? Math.floor(Math.sqrt(r * r - dy * dy)) : -1; if (hw < 0) d.P(0, y, 360, 1, INK); else { d.P(0, y, Math.max(0, cx - hw), 1, INK); d.P(cx + hw, y, 360 - cx - hw, 1, INK); } } };
/* the four held steps of a console fade (never an alpha ramp): 0 clear, 1 to 3 dither, 4 ink */
const fadeSteps = (d, step) => { if (step <= 0) return; if (step >= 4) { d.P(0, 0, 360, 417, INK); return; } for (let j = 0; j < 417; j++) if (step >= 2 || j % 2 === 0) d.dith(0, j, 360, 1, INK, j % 2); if (step === 3) d.dith(0, 0, 360, 417, INK, 1); };
/* her phone glowing inside the lit kitchen window, ring waves and the four ring marks above the window */
const windowPhone = (k, d, o = {}) => {
  const {P, F} = d, ring = o.ring && Math.floor(F / 3) % 2;
  P(104 + (ring ? 1 : 0), 270, 18, 32, INK); P(106 + (ring ? 1 : 0), 272, 14, 26, o.lit === false ? '#1F2A40' : '#87CEEB');
  if (o.ring) [[96, 276], [128, 280], [94, 290], [130, 292]].forEach(([x, y], i) => { if ((i + Math.floor(F / 3)) % 2) P(x, y, 3, 6, CREAM); });
  for (let i = 0; i < 4; i++) { const on = i < (o.rings || 0); P(66 + i * 18, 246, 12, 10, INK); P(67 + i * 18, 247, 10, 8, on ? GOLD : '#3D2E45'); }
};
/* her phone: body, screen; s >= 2 shows the full call screen (CALLING / YOUR SHOP / the clock); rings = ring marks lit */
const phone = (k, d, x, y, s, o = {}) => {
  const {P} = d, ringing = o.ring && (Math.floor(d.F / 3) % 2), X = x + (ringing ? 1 : 0);
  P(X + 2, y + 2, 60 * s, 110 * s, INK); P(X, y, 60 * s, 110 * s, '#2B2033'); P(X + 3 * s, y + 6 * s, 54 * s, 96 * s, '#1F2A40');
  P(X + 24 * s, y + 2 * s, 12 * s, 2 * s, INK);
  if (s >= 2) {
    k.text('CALLING', (X + 30 * s) * 3, (y + 12 * s) * 3, {size: 60, color: GREY, align: 'center', lint: false});
    k.text('YOUR SHOP', (X + 30 * s) * 3, (y + 24 * s) * 3, {size: 72, color: CREAM, align: 'center', lint: false});
    k.text('6:50 PM', (X + 30 * s) * 3, (y + 40 * s) * 3, {size: 80, color: GOLD, align: 'center', lint: false});
  } else {
    P(X + 8 * s, y + 20 * s, 44 * s, 6 * s, GREY); P(X + 12 * s, y + 32 * s, 36 * s, 8 * s, CREAM);
  }
  /* the red end-call button and the ring marks */
  P(X + 22 * s, y + 84 * s, 16 * s, 10 * s, RED);
  const n = o.rings || 0;
  for (let i = 0; i < 4; i++) P(X + (9 + i * 12) * s, y + 64 * s, 6 * s, 6 * s, i < n ? GOLD : '#2B3550');
  if (o.ring) { const ph = Math.floor(d.F / 3) % 2; [[-6, 20], [-10, 40], [60 * s + 4, 26], [60 * s + 8, 46]].forEach(([dx, dy], i) => { if ((i + ph) % 2) P(X + dx, y + dy, 3, 8, CREAM); }); }
};
/* the voicemail bubble over the band (frame y 252 up): a dark box with a speaker icon and the message */
const bubble = (k, d, lines, t0, o = {}) => {
  const {P} = d, up = d.ease(t0, 5, 40), Y = 84 - up, h = 26 + lines.length * 22;
  if (k.T < t0) return;
  P(16, Y + 2, 330, h, INK); P(14, Y, 330, h, o.base || CREAM); P(14, Y, 330, 2, '#FFFFFF');
  P(24, Y + 10, 6, 8, INK); P(30, Y + 7, 4, 14, INK);   /* the speaker */
  lines.forEach((s, i) => k.text(s, 120, (Y + 7 + i * 22) * 3, {size: 54, color: o.ink || INK}));
};
/* ServiceTitan's own line on a card: label, the quote typed on, the tag (the real screen, our drawing of it) */
const sourceCard = (k, d, t0, typeAt) => {
  const {P, win} = d, up = d.ease(t0, 6, 30), n0 = k.data.numbers.oct.shown;
  win(14, 84 + up, 332, 246, {base: CREAM, hi: '#FFFFFF', lo: SAND, rule: false});
  P(14, 84 + up, 332, 66, DTEAL);
  k.text('SHARE OF HOME HVAC', 72, 268 + up * 3, {size: 52, color: CREAM});
  k.text('CALLS OUTSIDE', 72, 328 + up * 3, {size: 52, color: GOLD});
  k.text('BUSINESS HOURS', 72, 388 + up * 3, {size: 52, color: GOLD});
  k.wrap('ServiceTitan, State of the Trades: 2025, its customers\' home HVAC calls. Off-hours: weekdays before 8 or after 5, plus weekends. Read Nov 7, 2026.', {size: 52}, 840).forEach((s, i) => k.text(s, 72, 680 + i * 54 + up * 3, {size: 52, color: SLATE}));
  if (up) return;
  const lines = [['"During October, that figure', INK], ['fell to ' + n0 + ', the lowest', INK], ['point of the year."', INK]];
  let n = Math.max(0, Math.floor((k.T - typeAt) * 90));
  lines.forEach(([s, c], i) => { const m = Math.min(s.length, n); n -= m; if (m) k.text(s.slice(0, m), 72, 472 + i * 66, {size: 60, color: c}); });
};
/* the send card: the phone's voicemail settings screen, held up over the office wall at dusk */
const MSG = "You've reached [shop]. We're off until 7 am. Text this number your address and what's wrong, and we'll phone you first thing.";
const settingsCard = (k, d, t0) => {
  const {P, dith} = d, up = d.ease(t0 + 0.02, 5, 160);
  P(0, 0, 360, 417, '#2E3A4F'); const so = d.F % 12; for (let y = so - 12; y < 360; y += 12) { P(0, Math.max(0, y), 360, Math.max(0, Math.min(y + 6, 360) - Math.max(0, y)), '#1C2333'); }   /* the wall's stripes drift slowly behind the still card */
  P(0, 360, 360, 57, '#3D2E45'); P(0, 360, 360, 3, '#5A4766');   /* the desk edge */
  P(16, 82 + up, 332, 226, INK); P(12, 78 + up, 336, 226, '#2B2033'); P(18, 86 + up, 324, 212, CREAM);
  P(18, 86 + up, 324, 26, DTEAL);
  if (up !== 0) return null;
  k.text('FOR YOUR OFFICE MANAGER', 72, 266, {size: 52, color: CREAM});
  k.text('AFTER-HOURS MESSAGE', 72, 354, {size: 80, color: INK});
  P(24, 150, 312, 112, '#E6F2EF'); P(24, 150, 3, 112, TEAL);
  const ls = k.wrap(MSG, {size: 60}, 840);
  ls.forEach((s, i) => k.text(s, 96, 476 + i * 78, {size: 60, color: INK}));
  exampleTag(d, 204, 264);
  return ls;
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'SAY WHAT HAPPENS NEXT',
  sendLine: 'Send this to your office manager.',
  transitions: {receipt: 'dissolve', send: 'levelselect', versus: 'mosaic', texts: 'fade4', button: 'gameover'},
  trauma: {},
  sections: {
    /* ---- hook (design r0: a new move): frame 0 is the cover, the sourced stake as hero over the night house; at 0.6 s */
    /* the kitchen wall clock at 4:59; a four-step console fade jumps it to 6:50 PM (1.3 to 1.7 s); at 2.4 s the house */
    /* wide, her phone ringing inside the lit window; ring marks on "four", the closed bubble and CLOSED on "closed". */
    hook: (k, T) => {
      const d = px(k), n = k.data.numbers.oct, tClock = 0.6, tFade = 1.3, tWide = 2.4, tFour = wordT(k, 'hook', /^four/i, 5.0) - 0.1, tClosed = wordT(k, 'hook', /^closed/i, 7.2) - 0.15;
      if (T < tClock) {
        house(k, d);
        d.win(14, 84, 332, 236, {base: '#253048', hi: '#3B82C4', lo: NIGHT, rule: '#3B82C4'});
        k.text(n.shown, 540, 268, {size: 340, color: ORANGE, align: 'center', drop: INK});
        k.text('OF CALLS TO HVAC SHOPS ON', 540, 612, {size: 52, color: CREAM, align: 'center'});
        k.text('SERVICETITAN CAME OFF-HOURS,', 540, 670, {size: 52, color: CREAM, align: 'center'});
        k.text('EVEN IN OCTOBER', 540, 728, {size: 52, color: CREAM, align: 'center'});
        k.text('Source: ServiceTitan, 2025 data', 540, 796, {size: 52, color: GOLD, align: 'center'});
        if (T >= tClock - 0.13) fadeSteps(d, 1 + Math.floor((T - tClock + 0.13) / 0.033));   /* design r1: a console fade into the clock, not a cut */
        return host(k, 'point', 0.75);
      }
      if (T < tWide) {   /* the clock close-up on her kitchen wall: 4:59, the fade, 6:50 */
        const late = T >= tFade + 0.2, step = T < tFade ? 0 : (T < tFade + 0.2 ? 1 + Math.floor((T - tFade) / 0.05) : Math.max(0, 4 - Math.floor((T - tFade - 0.2) / 0.05)));
        kitchen(k, d); clock(k, d, 180, 140, 56, late ? 6 : 4, late ? 50 : 59);
        if (late) { d.P(110, 206, 140, 36, INK); d.P(112, 208, 136, 32, NIGHT); } k.text(late ? '6:50 PM' : '4:59 PM', 540, 630, {size: 80, color: late ? ORANGE : INK, align: 'center'});   /* design r1: 6:50 on a dark pill */
        exampleTag(d, 176, 250);
        fadeSteps(d, Math.min(4, step));
        if (T < tClock + 0.13) fadeSteps(d, 4 - Math.floor((T - tClock) / 0.033));
        if (T >= tWide - 0.2) iris(d, 98, 290, Math.max(0, Math.round(260 * (1 - (T - tWide + 0.2) / 0.2))));   /* design r1: iris into the lit window */
        return {hostPose: 'stand', hostScale: 0.55, hostX: 150};
      }
      const rings = T < tFour ? 0 : Math.min(4, 1 + Math.floor((T - tFour) / 0.28)), closed = T >= tClosed;
      house(k, d); windowPhone(k, d, {ring: !closed, rings}); exampleTag(d, 180, 296);
      if (T < tWide + 0.2) iris(d, 98, 290, Math.round(260 * (T - tWide) / 0.2));
      if (closed) { bubble(k, d, ["We're closed."], tClosed); stampBox(k, 'CLOSED', 690, 600, tClosed + 0.25, {color: RED, freeze: 4}); }
      return host(k, closed ? 'shrug' : 'point', 0.75);
    },

    /* ---- receipt: ServiceTitan's line typed on; sweeps on "lowest" and "year"; on "one in ten" the gauge (design r0: */
    /* 0 to 20 so the needle swings to half, the readout as the hero, the source on the hood) ---- */
    receipt: (k, T) => {
      const t0 = k.S('receipt'), tOct = t0 + 0.5, tOne = wordT(k, 'receipt', /^one$/i, 8.8) - 0.2;
      const d = px(k), n = k.data.numbers.oct, tLow = wordT(k, 'receipt', /^lowest/i, 6.4) - 0.25, tYear = wordT(k, 'receipt', /^year/i, 7.3) - 0.25;
      if (T < tOne) { d.P(0, 0, 360, 417, '#253048'); for (let y = (d.F >> 2) % 8 - 8; y < 417; y += 8) d.P(0, Math.max(0, y), 360, 3, NIGHT); sourceCard(k, d, t0, tOct);
        if (T >= tLow) k.sweep(72, 472 + 66 + 62, k.measure('fell to ' + n.shown + ', the lowest', {size: 60}), 6, tLow, {color: 'accent'});
        if (T >= tYear) k.sweep(72, 472 + 132 + 62, k.measure('point of the year."', {size: 60}), 6, tYear, {color: 'accent'});
        if (T >= tOne - 0.13) fadeSteps(d, 1 + Math.floor((T - tOne + 0.13) / 0.033));   /* design r1: a console fade into the gauge */
        return host(k, T >= tLow ? 'point' : null); }
      const gIn = T < tOne + 0.13;
      k.sets.gauge({value: n.value, max: 20, at: tOne, dur: 1, zones: [[0, 10, GOLD], [10, 20, '#3D2E45']], labels: false, readout: false, suffix: '%', dec: 1});
      const shown = n.shown;   /* facts r1: no count-up value that is not on the source */
      d.P(70, 228, 220, 116, INK); d.P(72, 230, 216, 112, '#24453A');
      k.text('Source: ServiceTitan, 2025 data', 540, 700, {size: 52, color: CREAM, align: 'center'});
      k.text(shown, 540, 790, {size: 230, color: GOLD, align: 'center'});
      k.text('0%', 40, 630, {size: 52, color: CREAM, drop: INK}); k.text('20%', 915, 630, {size: 52, color: CREAM, align: 'right', drop: INK});   /* facts r1: the base on screen */
      if (T >= tOne + 1.6) { d.P(60, 86, 240, 22, INK); k.slam('LOWEST MONTH: OCTOBER', 540, 264, tOne + 1.6, {size: 52, color: GOLD, align: 'center', drop: INK, from: 0.3}); }
      if (gIn) fadeSteps(d, 4 - Math.floor((T - tOne) / 0.033));
      return host(k, T >= tOne + 1.0 ? 'point' : null);
    },

    /* ---- send: the new after-hours message goes up whole, then holds still while the voice reads it ---- */
    send: (k, T) => {
      const d = px(k), ls = settingsCard(k, d, k.S('send')), tCall = wordT(k, 'send', /^call$/i, 6.6) - 0.25, tText = wordT(k, 'send', /^text$/i, 8.4) - 0.25;
      if (ls) {
        const tCard = wordT(k, 'send', /^card/i, 4.9) - 0.25;
        if (T >= tCard) k.sweep(96, 476 + 66, k.measure(ls[0], {size: 60}), 6, tCard, {color: 'accent'});
        const iT = ls.findIndex((s) => /Text/.test(s)), iC = ls.findIndex((s) => /phone you/.test(s));
        if (iC >= 0 && T >= tCall) k.sweep(96, 476 + iC * 78 + 66, k.measure(ls[iC], {size: 60}), 6, tCall, {color: 'accent'});
        if (iT >= 0 && T >= tText) k.sweep(96, 476 + iT * 78 + 66, k.measure(ls[iT], {size: 60}), 6, tText, {color: 'accent'});
      }
      return host(k, ls ? 'point' : null);
    },

    /* ---- versus (design r0): our two messages typed in their cards, a voicemail waveform under each, NO NEXT STEP */
    /* stamps on "no", TEXT US on "does" ---- */
    versus: (k, T) => {
      const t0 = k.S('versus'), tNo = wordT(k, 'versus', /^no$/i, 2.5) - 0.2, tDoes = wordT(k, 'versus', /^does/i, 6.9) - 0.3, d = px(k), {P, F} = d;
      k.sets.versus({a: {name: ' ', icon: 'phone'}, b: {name: ' ', icon: 'phone'}, at: t0 + 0.05, vsAt: t0 + 0.45});
      const xa = 20 + d.ease(t0 + 0.05, 8, -170), xb = 176 + d.ease(t0 + 0.05, 8, 190);
      if (T >= t0 + 0.35) [[xa, '#2F6F67', ['We\'re', 'closed.'], 'BEFORE', TEAL, 6, 108], [xb, '#E2633B', ['Off until', '7 am. Text', 'this number.'], 'AFTER', ORANGE, 26, 108]].forEach(([x, base, ls, name, c, bx, bw]) => {
        P(x + bx, 92, bw, 80, base);
        ls.forEach((l, i) => k.text(l, (x + bx + bw / 2) * 3, 300 + i * 66 + (ls.length === 2 ? 30 : 0), {size: 52, color: CREAM, align: 'center', drop: INK}));
        k.text(name, (x + 70) * 3, 556, {size: 52, color: c, align: 'center'});
      });
      /* the voicemail waveforms: the old one plays a short clip and stops; the new one keeps going */
      for (let i = 0; i < 16; i++) {
        const ha = T < t0 + 2.2 ? 4 + Math.floor(10 * Math.abs(Math.sin((F + i * 5) * 0.4))) : 2, hb = 4 + Math.floor(14 * Math.abs(Math.sin((F * 0.7 + i * 3) * 0.5)));
        P(xa + 6 + i * 8, 232 - ha, 5, ha * 2, TEAL); P(xb + 6 + i * 8, 232 - hb, 5, hb * 2, GOLD);
      }
      stampBox(k, 'NO NEXT STEP', 270, 780, tNo, {color: CREAM, size: 52});
      stampBox(k, 'TEXT US', 738, 780, tDoes, {color: GOLD, size: 52, sub: 'YOUR ADDRESS'});
      return host(k, T >= tDoes ? 'point' : null);
    },

    /* ---- texts: the chat in the truck: her text arrives; JOB DETAILS IN on a dark pill on "details" ---- */
    texts: (k, T) => {
      const t0 = k.S('texts'), tDet = wordT(k, 'texts', /^details/i, 2.0) - 0.2;
      k.sets.chat({who: 'New number', clock: '6:52', notify: {text: 'New text message', at: t0 + 0.1, dur: 1.0}, msgs: []});
      const d = px(k), tMsg = t0 + 1.0;
      /* render critic r4: her text drawn large (the set's bubble type is 39), sliding up on whole pixels like the set's */
      if (T >= tMsg - 0.6 && T < tMsg) { d.P(110, 138, 40, 18, CREAM); for (let i = 0; i < 3; i++) d.P(116 + i * 10, 145 - (((d.F >> 2) - i) % 3 === 0 ? 1 : 0), 5, 5, GREY); }
      if (T >= tMsg) { const sl = d.ease(tMsg, 4, 8), y = 136 + sl; d.P(108, y, 176, 76, CREAM); d.P(108, y + 75, 176, 1, SAND); d.P(104, y + 64, 4, 6, CREAM);
        ["Furnace won't", 'start, no heat.', '[address]'].forEach((l, i) => k.text(l, 342, (y + 6) * 3 + i * 66, {size: 60, color: INK})); }
      if (T >= tDet) { d.P(110, 222, 176, 30, INK); d.P(112, 224, 172, 26, NIGHT); k.text('JOB DETAILS IN', 594, 676, {size: 60, color: GOLD, align: 'center'}); }   /* design r2: no spark over the letters */
      exampleTag(d, 160, 258);
      return host(k, T >= tDet ? 'point' : null);
    },

    /* ---- button: the house again at ten to seven; her phone rings in the window and the bubble now holds the new */
    /* message; WHAT TO DO NEXT over the roof ---- */
    button: (k, T) => {
      const t0 = k.S('button'), tRing = wordT(k, 'button', /^rings/i, 1.1) - 0.1;
      const tWhat = t0 + 0.25;
      const d = px(k);
      house(k, d); windowPhone(k, d, {ring: T < tRing + 0.9, rings: 4}); exampleTag(d, 180, 296);
      if (T >= tWhat) bubble(k, d, ['Off until 7 am.', 'We phone first thing.'], tWhat);
      if (T >= tWhat + 0.3) k.slam('SHE KNOWS WHAT TO DO', 470, 560, tWhat + 0.3, {size: 60, color: GOLD, align: 'center', drop: INK, from: 0.3});
      return host(k, T >= tWhat + 0.3 ? 'wave' : 'point');
    },
  },
};

/* a faint dither drifts down the empty lower band of every scene, below the host and every text, so no stretch goes   */
/* still (code QA, flat). It never crosses the send card (band y 84 to 316).                                          */
const drift = (k) => { const d = px(k), off = Math.floor(k.T * 30) % 16; for (let y = 418 - 16 + off; y < 640; y += 16) { const y0 = Math.max(418, y), y1 = Math.min(640, y + 8); if (y1 > y0) d.P(0, y0, 360, y1 - y0, '#2B2033'); } };
for (const [n, f] of Object.entries(window.SCENE.sections)) window.SCENE.sections[n] = (k, T) => { const r = f(k, T); drift(k); return r; };
