/* Scene: The robot is a better voicemail (story, shape owners-words, arcade; the first lesson on the new line, Nov 5,  */
/* 2026). One function per top-level cue in 03_cues/cues.md. Numbers only from k.data (brief.md -> data.js); every time */
/* from a cue start (k.S) or a spoken word (wordT), so a re-voiced take moves the picture with it.                      */
/* Worlds: hook = our own sunny workshop (a phone with a robot face, the 2 PM clock); roof and button = our own day     */
/* street with a house, a ladder and a truck; pitch = chat, then our forum card; survey = gauge; daytime = flaps;      */
/* owners = our own day and night split; setup = our setup card; button.night = versus. Labels say EXAMPLE where ours. */
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', GREY = '#9AA0AD', SKY = '#87CEEB', NIGHT = '#1B1420';
const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eo = (x) => 1 - Math.pow(1 - clamp(x), 3);

/* ---- the pixel kit (low-res units: 360 x 640, one pixel = 3 frame units) ---- */
const px = (k) => {
  const ctx = k.ctx, T = k.T, F = Math.floor(T * 30 + 0.005);
  const P = (x, y, w, h, c) => { x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h); if (w > 0 && h > 0 && c) { ctx.fillStyle = c; ctx.fillRect(x * 3, y * 3, w * 3, h * 3); } };
  const DOT = (x, y, c) => P(x, y, 1, 1, c);
  const dith = (x, y, w, h, c, ph = 0) => { ctx.fillStyle = c; for (let j = 0; j < h; j++) for (let i = (j + ph) & 1; i < w; i += 2) ctx.fillRect((Math.round(x) + i) * 3, (Math.round(y) + j) * 3, 3, 3); };
  const disc = (cx, cy, r, c) => { for (let dy = -r; dy <= r; dy++) { const hw = Math.floor(Math.sqrt(r * r - dy * dy) + 0.4); P(cx - hw, cy + dy, 2 * hw + 1, 1, c); } };
  const line = (x0, y0, x1, y1, c, th = 1) => {
    x0 = Math.round(x0); y0 = Math.round(y0); x1 = Math.round(x1); y1 = Math.round(y1);
    const dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1; let e = dx + dy;
    for (let n = 0; n < 2000; n++) { P(x0, y0, th, th, c); if (x0 === x1 && y0 === y1) break; const e2 = 2 * e; if (e2 >= dy) { e += dy; x0 += sx; } if (e2 <= dx) { e += dx; y0 += sy; } }
  };
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
  const tw = (s, size = 39) => k.measure(String(s), {size}) / 3;
  const clip = (x, y, w, h, fn) => { ctx.save(); ctx.beginPath(); ctx.rect(x * 3, y * 3, w * 3, h * 3); ctx.clip(); fn(); ctx.restore(); };
  const twinkle = (x, y, f, c = CREAM) => { const s = [0, 1, 2, 1][((f % 4) + 4) % 4]; DOT(x, y, c); for (let i = 1; i <= s; i++) { DOT(x - i, y, c); DOT(x + i, y, c); DOT(x, y - i, c); DOT(x, y + i, c); } };
  return {P, DOT, dith, disc, line, win, fr, ease, tx, tw, clip, twinkle, F, T};
};

/* ---- the words: every beat lands on a spoken word ---- */
const WS = () => (window.WORDS && window.WORDS.words) || [];
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
const host = (k, pose) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150});
const plate = (d, x, y, w, h) => d.win(x, y, w, h, {base: NIGHT, hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
/* the two-line title plate at the top of the band (frame y 252 to 444) */
const topPlate = (k, d, a, b, t0, o = {}) => {
  d.win(14, 84, 332, 64, {base: o.base || '#253048', hi: o.hi || '#3B82C4', lo: NIGHT, rule: o.rule || '#3B82C4'});
  k.slam(a, o.align === 'left' ? 72 : 540, 266, t0, {size: 66, color: CREAM, align: o.align || 'center', drop: INK, from: 0.4});
  k.slam(b, o.align === 'left' ? 72 : 540, 344, t0 + 0.06, {size: 66, color: o.c2 || 'accent', align: o.align || 'center', drop: INK, from: 0.4});
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
const loopSweep = (k, x, y, w, t0, period = 1.0, h = 8) => { if (k.T < t0) return; const n = Math.floor((k.T - t0) / period); k.sweep(x, y, w, h, t0 + n * period, {color: 'accent'}); };
const exampleTag = (d, x, y) => { d.P(x, y, 80, 22, INK); d.P(x + 1, y + 1, 78, 20, ORANGE); d.tx('EXAMPLE', x + 40, y + 4, {size: 30, color: INK, align: 'center'}); };

/* ================================================================================================================ */
/* a phone (low-res), w x h; ringing shakes it a pixel every 2 frames and throws ring arcs. o.face: the robot face on */
/* its screen (antenna, square eyes that blink every 2 s, a mouth bar that talks); o.screen: the screen colour.        */
const phone = (d, x, y, w, h, o = {}) => {
  const {P, DOT, line, F} = d, sh = o.ring ? [0, 1, 0, -1][(F >> 1) % 4] : 0, X = x + sh;
  P(X + 2, y + 2, w, h, INK); P(X - 1, y, w + 2, h, INK); P(X, y - 1, w, h + 2, INK);
  P(X, y, w, h, '#2B2033'); P(X + 1, y, w - 2, 1, '#4A4E5A');
  const scr = o.screen || (o.ring ? '#3B82C4' : NIGHT);
  P(X + 2, y + 4, w - 4, h - 9, scr); if (o.ring) P(X + 2, y + 4, w - 4, 1, SKY);
  P(X + Math.round(w / 2) - 2, y + h - 4, 4, 2, '#4A4E5A');
  if (o.ring) { const g = (F >> 2) % 3; for (let i = 0; i <= g; i++) { line(X - 3 - i * 3, y + 4 + i, X - 3 - i * 3, y + 10 + i * 2, GOLD); line(X + w + 2 + i * 3, y + 4 + i, X + w + 2 + i * 3, y + 10 + i * 2, GOLD); } }
  if (o.face) robot(d, X + Math.round(w / 2), y + Math.round(h * 0.45), Math.max(1, Math.floor(w / 18)), o.talk);
};
/* the robot face, centred on cx, cy, at a whole-pixel scale s */
const robot = (d, cx, cy, s, talk) => {
  const {P, F} = d, W = 14 * s, H = 11 * s, x = cx - W / 2, y = cy - H / 2;
  P(cx - s / 2, y - 4 * s, s, 3 * s, '#C9CCD3'); P(cx - s, y - 5 * s, 2 * s, 2 * s, F % 60 < 30 ? RED : GOLD);
  P(x - s, y - s, W + 2 * s, H + 2 * s, INK); P(x, y, W, H, '#C9CCD3'); P(x, y, W, s, CREAM); P(x, y + H - s, W, s, '#9AA0AD');
  const blink = F % 60 > 56;
  P(x + 3 * s, y + 3 * s, 3 * s, blink ? s : 3 * s, TEAL); P(x + 8 * s, y + 3 * s, 3 * s, blink ? s : 3 * s, TEAL);
  const m = talk ? [1, 2, 1, 0][(F >> 2) % 4] : 0;
  P(x + 4 * s, y + 8 * s - m * s / 2, 6 * s, Math.max(1, s + m * s / 2), INK);
};
/* a wall clock at cx, cy, radius r, hands at 2:00 */
const clock = (d, cx, cy, r) => {
  const {disc, line, P} = d;
  disc(cx, cy, r + 2, INK); disc(cx, cy, r, CREAM); disc(cx, cy, r - 2, '#FFFFFF');
  for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6; P(cx + Math.round(Math.sin(a) * (r - 4)), cy - Math.round(Math.cos(a) * (r - 4)), 2, 2, INK); }
  line(cx, cy, cx + Math.round(Math.sin(Math.PI / 3) * r * 0.5), cy - Math.round(Math.cos(Math.PI / 3) * r * 0.5), INK, 2);
  line(cx, cy, cx, cy - Math.round(r * 0.78), INK, 2); disc(cx, cy, 2, RED);
};

/* our own sunny workshop: a wall, a window with the sun, a pegboard, the bench with the phone, the 2 PM clock */
const shop = (k, o = {}) => {
  const d = px(k), {P, dith, disc, F} = d;
  P(0, 0, 360, 417, '#C98B63'); for (let y = 0; y < 417; y += 8) dith(0, y, 360, 1, '#B07A47', (y / 8) % 2);
  P(18, 160, 110, 90, INK); P(20, 162, 106, 86, SKY); disc(96, 188, 12, GOLD); P(20, 236, 106, 12, '#6FB7A8'); P(72, 162, 2, 86, INK); P(20, 204, 106, 2, INK);
  P(230, 156, 116, 96, '#8C5A33'); for (let j = 0; j < 6; j++) for (let i = 0; i < 7; i++) P(238 + i * 16, 162 + j * 15, 2, 2, '#5A3720');
  P(250, 172, 6, 30, GREY); P(246, 168, 14, 6, GREY); P(290, 176, 26, 6, RED); P(312, 170, 4, 18, RED);
  P(0, 300, 360, 14, '#5A3720'); P(0, 300, 360, 2, '#8C5A33'); P(0, 314, 360, 103, '#4A2E1B');
  if (o.clock !== false) clock(d, 300, 112, 18);
  P(0, 417, 360, 223, NIGHT); for (let y = 424; y < 640; y += 8) P(20, y, 320, 2, '#2B2033');
  return d;
};

/* our own day street: a house with a pitched roof and a ladder, a truck at the kerb; o.night steps the sky to night */
const roofStreet = (k, o = {}) => {
  const d = px(k), {P, DOT, dith, disc, line, F} = d, night = !!o.night;
  P(0, 0, 360, 417, night ? NIGHT : SKY); if (night) for (let i = 0; i < 36; i++) DOT(Math.floor(hash(i * 3.1) * 360), 4 + Math.floor(hash(i * 7.9) * 150), (Math.floor(F / 15) + i) % 5 === 0 ? GOLD : '#6B7080');
  if (night) { disc(312, 40, 11, '#FFF2B8'); disc(316, 37, 10, NIGHT); } else { disc(312, 40, 12, GOLD); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4 + (F >> 3) * 0.05; P(312 + Math.round(Math.cos(a) * 18), 40 + Math.round(Math.sin(a) * 18), 2, 2, GOLD); } }
  for (let i = 0; i < 3; i++) { const cxl = ((i * 140 - Math.floor(F / 4)) % 480 + 480) % 480 - 60; if (!night) { disc(cxl, 70 + i * 8, 10, CREAM); disc(cxl + 12, 66 + i * 8, 12, CREAM); disc(cxl + 26, 72 + i * 8, 9, CREAM); } }
  /* the house: walls, the roof, a window lit at night */
  P(60, 250, 230, 167, night ? '#4A2E1B' : '#C98B63'); for (let y = 254; y < 417; y += 8) dith(60, y, 230, 1, night ? '#3A2416' : '#B07A47', (y / 8) % 2);
  for (let j = 0; j < 90; j++) { const hw = Math.round(j * 1.45); P(175 - hw, 160 + j, 2 * hw, 1, j % 6 === 0 ? INK : (night ? '#3D2E45' : '#7A3442')); }
  P(100, 300, 40, 40, INK); P(102, 302, 36, 36, night ? '#F7D79B' : SKY); P(210, 300, 40, 40, INK); P(212, 302, 36, 36, night ? '#253048' : SKY);
  /* the ladder up to the roof edge */
  line(296, 417, 262, 236, '#C9CCD3', 2); line(312, 417, 278, 236, '#C9CCD3', 2); for (let r = 0; r < 9; r++) { const yy = 400 - r * 20, xx = 293 - r * 3.7; P(xx, yy, 17, 2, '#C9CCD3'); }
  /* the street and the truck */
  P(0, 417, 360, 223, '#2B2033'); P(0, 417, 360, 3, '#4A4E5A'); P(0, 440, 360, 200, NIGHT);
  return d;
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'AFTER HOURS',
  sendLine: 'Send this to whoever answers your phone after hours.',
  transitions: {roof: 'dissolve', pitch: 'levelselect', survey: 'mosaic', daytime: 'dissolve', owners: 'fade4', setup: 'levelselect', button: 'gameover'},
  trauma: {'pitch.stay': 0.7},
  sections: {
    /* ---- hook: three shots. The cover: the sunny workshop, a phone ringing on the bench with a robot face, the clock at */
    /* 2 PM; the plate "AI answering your phone? / Not at 2 PM." with EXAMPLE (no host). Cut in close on the robot face on   */
    /* "receptionist" (Snow comes in). Cut to the clock big on "two": NOT AT 2 PM stamps.                                   */
    hook: (k, T) => {
      const tIn = Math.min(0.9, Math.max(0.4, wordT(k, 'hook', /^receptionist/i, 0.6) - 0.03)), tTwo = Math.min(2.8, k.S('hook.two'));
      if (T >= tTwo) {
        const d = shop(k, {clock: false});
        d.P(0, 150, 360, 267, '#C98B63'); for (let y = 150; y < 300; y += 8) d.dith(0, y, 360, 1, '#B07A47', (y / 8) % 2);
        clock(d, 180, 222, 62);
        topPlate(k, d, 'AI answering your phone?', 'Not at 2 PM.', -1);
        if (T >= tTwo + 0.15) stampBox(k, 'NOT AT 2 PM', 540, 820, tTwo + 0.15, {color: RED, freeze: 4});
        exampleTag(d, 222, 296);
        return host(k);
      }
      if (T >= tIn) {
        const d = px(k), {P, dith} = d;
        P(0, 0, 360, 417, '#245752'); for (let y = 150; y < 417; y += 4) dith(0, y, 360, 1, '#2F6F67', (y / 4) % 2);
        phone(d, 110, 156, 140, 230, {ring: true, screen: '#253048', face: true, talk: true});
        P(214, 176, 128, 50, INK); P(216, 178, 124, 46, CREAM); P(228, 224, 10, 8, CREAM);
        d.tx('HELLO, I AM', 278, 184, {size: 30, color: INK, align: 'center'}); d.tx('AN AI.', 278, 202, {size: 30, color: INK, align: 'center'});
        topPlate(k, d, 'AI answering your phone?', 'Not at 2 PM.', -1);
        exampleTag(d, 222, 300);
        P(0, 417, 360, 223, NIGHT);
        return host(k);
      }
      const d = shop(k);
      phone(d, 136, 188, 88, 112, {ring: true, screen: '#253048', face: true});
      topPlate(k, d, 'AI answering your phone?', 'Not at 2 PM.', -1);
      exampleTag(d, 222, 296);
      return {host: false, speech: false};
    },

    /* ---- roof: the day street. The phone buzzes in the truck cab by the ladder; on "voicemail" its screen reads       */
    /* VOICEMAIL; on "night" the sky steps to night and CALL BACK lights.                                               */
    roof: (k, T) => {
      const tVm = wordT(k, 'roof.vm', /^voicemail/i, 0.5), tNight = wordT(k, 'roof.vm', /^night/i, 1.6);
      const night = T >= tNight;
      const d = roofStreet(k, {night});
      /* the truck by the ladder with the phone on the dash */
      const {P, disc} = d;
      P(186, 430, 120, 44, INK); P(188, 432, 116, 40, CREAM); P(188, 432, 116, 2, '#FFFFFF'); P(270, 438, 30, 16, SKY); disc(210, 476, 8, INK); disc(282, 476, 8, INK);
      phone(d, 196, 176, 40, 66, {ring: T < tVm, screen: T >= tNight ? '#2F6F67' : (T >= tVm ? '#7A3442' : null)});
      if (T >= tVm && T < tNight) { d.P(176, 248, 80, 14, INK); d.tx('VOICEMAIL', 216, 249, {size: 30, color: CREAM, align: 'center', lint: false}); }
      if (T >= tNight) { d.P(176, 248, 80, 14, INK); d.tx('CALL BACK', 216, 249, {size: 30, color: GOLD, align: 'center', lint: false}); }
      const tB = tVm - 0.3, say = T >= tB ? ['Voicemail.', 'Call back that night.', tB] : ['For years:', 'phone rings on the roof.', k.S('roof') + 0.1];
      topPlate(k, d, say[0], say[1], say[2], {align: 'left', base: NIGHT, hi: '#3D2E45', rule: '#3D2E45'});
      return host(k, k.live('roof.vm') ? 'shrug' : null);
    },

    /* ---- pitch: the chat set in the truck; three pitch messages drop in (EXAMPLE, no company named). On "forum" the    */
    /* forum card: JOBBER COMMUNITY, OWNER FORUM; the owner's line types in (our paraphrase), its tag under it. CALLER    */
    /* LEFT stamps on "Hardly".                                                                                          */
    pitch: (k, T) => {
      const t0 = k.S('pitch'), tF = k.S('pitch.forum'), tStay = k.S('pitch.stay');
      if (T < tF) {
        const d = px(k), {P, dith} = d;
        P(0, 0, 360, 417, '#7A3442'); for (let y = 0; y < 417; y += 4) dith(0, y, 360, 1, '#6A2C3A', (y / 4) % 2);
        phone(d, 96, 92, 168, 300, {screen: '#1F2A40', ring: T >= t0 + 2.2});
        k.text('AI SALES PITCHES', 540, 318, {size: 48, color: GOLD, align: 'center'});
        const pitches = [['Let a robot answer', 'your phone?'], ['Try our AI', 'receptionist free!'], ['Never pick up', 'the phone again?']];
        const tp = [t0 + 0.15, wordT(k, 'pitch', /^instead/i, 2.4) - 0.3, wordT(k, 'pitch', /^tried/i, 4.0) - 0.3];
        pitches.forEach(([a, b], i) => { const ti = tp[i]; if (T < ti) return; const sl = d.ease(ti, 5, 24);
          d.win(108, 120 + i * 76 - sl, 144, 66, {base: CREAM, hi: '#FFFFFF', lo: SAND, rule: false, shadow: false});
          d.P(116, 130 + i * 76 - sl, 14, 14, RED);
          if (sl === 0) { k.text(a, 408, 378 + i * 228, {size: 48, color: INK}); k.text(b, 408, 426 + i * 228, {size: 48, color: INK}); } });
        exampleTag(d, 10, 84);
        return host(k);
      }
      const d = px(k), {P, dith, win} = d;
      P(0, 0, 360, 417, '#253048'); { const sc = Math.floor(d.F / 2) % 8; for (let y = -8; y < 417; y += 8) dith(0, y + sc, 360, 2, '#1F2A40', 0); }
      win(14, 84, 332, 40, {base: '#2F6F67', hi: TEAL, lo: INK, rule: false});
      k.text('JOBBER COMMUNITY', 72, 264, {size: 48, color: CREAM, drop: INK}); k.text('OWNER FORUM', 72, 318, {size: 48, color: GOLD});
      const up = d.ease(tF + 0.1, 6, 30);
      win(14, 136 + up, 332, 128, {base: CREAM, hi: '#FFFFFF', lo: SAND, rule: false});
      P(26, 148 + up, 22, 22, '#3B82C4'); P(30, 152 + up, 14, 6, CREAM); P(28, 160 + up, 18, 8, CREAM);
      if (up === 0) {
        k.text('One owner, runs it after hours:', 168, 444, {size: 48, color: '#4A4E5A'});
        const s1 = 'Hardly anyone stays', s2 = "once they hear it's AI.";
        const n1 = Math.max(0, Math.min(s1.length, Math.floor((T - tF - 0.3) * 30))), n2 = Math.max(0, Math.min(s2.length, Math.floor((T - tF - 0.3) * 30) - s1.length));
        if (n1) k.text(s1.slice(0, n1), 72, 540, {size: 66, color: INK});
        if (n2) k.text(s2.slice(0, n2), 72, 616, {size: 66, color: INK});
        k.text('Our paraphrase. Jobber Community, Nov 2026', 72, 716, {size: 39, color: '#4A4E5A'});
      }
      if (T >= tStay + 0.6) for (let i = 0; i < 4; i++) { const q = ((T - tStay - 0.6) / 1.6 + i * 0.25) % 1; phone(d, Math.round(110 + q * 260), 296 + (i % 2) * 6, 22, 30, {screen: '#7A3442'}); }
      if (T >= tStay) stampBox(k, 'CALLER LEFT', 640, 830, tStay, {color: RED, freeze: 5});
      if (up === 0) { loopSweep(k, 72, 590, k.measure('Hardly anyone stays', {size: 66}), tF + 1.2, 1.0); phone(d, 300, 148 + up, 22, 36, {ring: T >= tF + 0.8 && T < tStay, screen: T >= tStay ? '#7A3442' : null}); }
      return host(k, k.live('pitch.stay') ? 'point' : null);
    },

    /* ---- survey: the gauge. The needle climbs to 36 on "thirty-six"; the zone past it is red; the hero 36% under the   */
    /* hub counts with the needle. The source on the hood the whole time it is said.                                     */
    survey: (k, T) => {
      const n = k.data.numbers, d = px(k), t36 = wordT(k, 'survey.36', /^thirty/i, 0.3);
      k.sets.gauge({value: n.survey36.value, max: 100, at: t36 - 0.3, dur: 0.9, suffix: '%', readout: false, labels: false, label: 'AI BOOKING OR BASIC QUESTIONS',
        zones: [[0, n.survey36.value, '#2F6F67'], [n.survey36.value, 100, '#E2633B']]});
      { const at = t36 - 0.3, dur = 0.9, dt = Math.max(0, T - at), v = T < at ? 0 : (dt >= dur ? n.survey36.value : Math.round(n.survey36.value * eo(clamp(dt / (dur * 0.55)))));
        const tAsk = k.S('survey') + 0.1;
        if (T < at) { const q = clamp((T - tAsk) / Math.max(0.3, at - tAsk)); k.text(String(Math.round(n.survey782.value * eo(q))), 726, 420, {size: 132, color: CREAM, align: 'center', drop: INK}); k.text('HOMEOWNERS', 726, 560, {size: 48, color: SAND, align: 'center'}); }
        else { const settled = T >= at + dur + 0.3, c = settled && Math.floor((T - at - dur - 0.3) * 2) % 2 === 1 ? CREAM : GOLD; k.text(String(v) + '%', 726, 420, {size: 165, color: c, align: 'center', drop: INK}); if (settled) k.text('COMFORTABLE', 726, 590, {size: 48, color: SAND, align: 'center'}); } }
      plate(d, 98, 290, 248, 30);
      k.text(`${n.survey782.shown} homeowners, spring 2026`, 312, 882, {size: 39, color: SAND});
      k.text('ACHR News, Oct 20, 2026', 312, 918, {size: 39, color: GOLD});
      return host(k, k.live('survey.36') ? 'point' : null);
    },

    /* ---- daytime: the flap board, 2 PM CALL. Rows land on the words that say them; the last in gold. EXAMPLE.        */
    daytime: (k, T) => {
      const t0 = k.S('daytime'), tGamble = wordT(k, 'daytime', /^gamble/i, 2.2), tHang = wordT(k, 'daytime.next', /^hang/i, 0.3), tNext = wordT(k, 'daytime.next', /^next/i, 1.2);
      k.sets.flaps({title: '2 PM CALL', cols: 12, rows: [
        {label: 'WANTS', value: 'YOU', at: t0 - 0.2}, {label: 'GETS', value: 'A ROBOT', at: wordT(k, 'daytime', /^robot/i, 3.2) - 0.8},
        {label: 'CAN', value: 'HANG UP', at: tHang - 0.3}, {label: 'NEXT SHOP', value: '', at: tNext - 0.3, hi: true}]});
      const d = px(k); exampleTag(d, 222, 290);
      return host(k, k.live('daytime.next') ? 'point' : null);
    },

    /* ---- owners: our own day and night split. Left the sun and YOU at the phone; right the moon and the robot phone,  */
    /* dim until "night". BETTER VOICEMAIL stamps on the night half; on "says" the labels DAY: YOU / NIGHT: AI land.     */
    owners: (k, T) => {
      const tNight = wordT(k, 'owners', /^night/i, 1.6), tVm = wordT(k, 'owners.vm', /^voicemail/i, 0.8), tAll = k.S('owners.all');
      const d = px(k), {P, DOT, dith, disc, F} = d;
      P(0, 0, 180, 417, SKY); P(180, 0, 180, 417, NIGHT); P(178, 0, 4, 417, CREAM);
      disc(90, 130, 18, GOLD); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4 + (F >> 3) * 0.06; P(90 + Math.round(Math.cos(a) * 26), 130 + Math.round(Math.sin(a) * 26), 2, 2, GOLD); }
      for (let i = 0; i < 24; i++) DOT(184 + Math.floor(hash(i * 2.3) * 172), 90 + Math.floor(hash(i * 5.1) * 150), (Math.floor(F / 15) + i) % 4 === 0 ? GOLD : '#6B7080');
      disc(270, 130, 16, '#FFF2B8'); disc(276, 125, 14, NIGHT);
      phone(d, 64, 186, 50, 82, {ring: true});
      phone(d, 246, 186, 50, 82, {ring: T >= tNight, screen: T >= tNight ? '#253048' : '#120D14', face: T >= tNight, talk: T >= tNight});
      if (T < tNight) { k.ctx.save(); k.ctx.globalAlpha = 0.55; P(182, 0, 178, 417, '#120D14'); k.ctx.restore(); }
      P(0, 417, 360, 223, '#2B2033');
      if (T >= tAll) { k.slam('DAY: YOU', 270, 474, tAll, {size: 66, color: INK, align: 'center', from: 0.4}); k.slam('NIGHT: AI', 810, 474, tAll + 0.1, {size: 66, color: GOLD, align: 'center', from: 0.4}); }
      if (T >= tVm) stampBox(k, 'BETTER VOICEMAIL', 744, 830, tVm, {color: TEAL, size: 48, freeze: 4});
      return host(k, k.live('owners.all') ? 'point' : null);
    },

    /* ---- setup: the setup card slides up (ITEM GET). Step 1 lights on "carrier"; step 2 and the Jobber help line on    */
    /* "AI"; on "greeting" the card turns to the greeting, word for word (EXAMPLE), held to the end of the section, with   */
    /* a cursor and a sweep so it never sits still; step 3 lights on "tonight".                                            */
    setup: (k, T) => {
      const t0 = k.S('setup'), tCar = wordT(k, 'setup', /^carrier/i, 1.2), tHon = k.S('setup.honest'), tGreet = k.S('setup.greet'), tTonight = wordT(k, 'setup.greet', /^tonight/i, 2.0);
      const d = px(k), {P, dith, win} = d;
      P(0, 0, 360, 417, '#3D2E45'); for (let y = 0; y < 417; y += 4) dith(0, y, 360, 1, '#2B2033', (y / 4) % 2);
      P(0, 417, 360, 223, NIGHT);
      const up = d.ease(t0 + 0.05, 6, 160);
      d.clip(0, 0, 360, 322, () => win(14, 84 + up, 332, 236, {base: NIGHT, hi: '#7A3442', lo: INK, rule: GOLD}));
      if (up !== 0) return host(k);
      if (T < tGreet) {
        k.text('ITEM GET: AFTER HOURS SETUP', 72, 270, {size: 48, color: GOLD});
        const tAi = wordT(k, 'setup.honest', /^ai$/i, 1.0);
        [['1. Carrier:', 'AI after hours only', tCar], ['2. Greeting:', "say it's AI", tAi]].forEach(([a, b, ti], i) => {
          const lit = T >= ti, y = 344 + i * 170;
          k.slam(a, 72, y, Math.min(ti, t0 + 0.3 + i * 0.1), {size: 66, color: lit ? GOLD : GREY, from: 0.3});
          k.slam(b, 72, y + 76, Math.min(ti, t0 + 0.35 + i * 0.1), {size: 66, color: lit ? CREAM : GREY, from: 0.3});
          if (lit) k.sweep(72, y + 150, k.measure(b, {size: 66}), 6, ti, {color: 'accent'}); });
        const tJ = wordT(k, 'setup.honest', /^even$/i, 2.0) - 0.2;
        if (T >= tJ) { k.slam('Jobber help: "We encourage you', 72, 700, tJ, {size: 48, color: SAND, from: 0.3}); k.slam('to let callers know" (Oct 28, 2026)', 72, 748, tJ + 0.08, {size: 48, color: SAND, from: 0.3}); }
        phone(d, 296, 100, 26, 44, {ring: true});
        loopSweep(k, 72, T >= tAi ? 664 : 494, k.measure(T >= tAi ? "say it's AI" : 'AI after hours only', {size: 66}), tCar + 0.6, 1.0);
        return host(k, 'point');
      }
      k.text('YOUR AFTER HOURS GREETING', 72, 270, {size: 48, color: GOLD});
      const g = ["You've reached us", "after hours. I'm our", 'AI assistant. I can book', 'you for tomorrow or', 'take the details now.'];
      g.forEach((s, i) => { const ti = tGreet + 0.1 + i * 0.12; if (T >= ti) k.slam(s, 72, 336 + i * 70, ti, {size: 52, color: CREAM, from: 0.3}); });
      const sw = Math.max(0, Math.floor((T - tGreet - 1.0) / 0.9)), row = sw % 5, tRow = tGreet + 1.0 + sw * 0.9;
      if (T >= tGreet + 1.0) k.sweep(72, 392 + row * 70, k.measure(g[row], {size: 52}), 8, tRow, {color: 'accent'});
      if ((d.F >> 4) % 2 === 0) P(318, 254, 3, 14, GOLD);
      phone(d, 296, 100, 26, 44, {ring: true, screen: '#253048', face: true, talk: true});
      exampleTag(d, 204, 92);
      const lit3 = T >= tTonight; k.slam('3. Test call tonight: "no heat"', 72, 742, Math.min(tTonight, tGreet + 0.6), {size: 48, color: lit3 ? CREAM : GREY, from: 0.3});
      if (lit3) k.sweep(72, 790, k.measure('3. Test call tonight: "no heat"', {size: 48}), 4, tTonight, {color: 'accent'});
      return host(k, 'point');
    },

    /* ---- button: the day street, the sun up: "2 PM: / they want you." Snow points. On "night" the versus screen:       */
    /* ROBOT against BEEP; VS slams; WIN stamps on ROBOT on "beep". Then the end card.                                 */
    button: (k, T) => {
      const tN = k.S('button.night'), tBeep = wordT(k, 'button.night', /^beep/i, 2.2);
      if (T < tN) {
        const d = roofStreet(k, {night: false});
        topPlate(k, d, '2 PM:', 'they want you.', k.S('button') + 0.05);
        exampleTag(d, 222, 290);
        return host(k, 'point');
      }
      k.sets.versus({a: {name: 'ROBOT', icon: 'phone', stats: [{label: 'ANSWERS', value: 1, max: 1, text: 'YES'}]},
        b: {name: 'BEEP', icon: 'clock', stats: [{label: 'ANSWERS', value: 0, max: 1, text: 'NO'}]},
        at: tN - 0.05, vsAt: tN + 0.3, winner: 'a', winAt: tBeep, winText: 'WIN', max: 1});
      { const d2 = px(k); if (T >= tN + 0.4 && T < tBeep) for (let r = 0; r < 3; r++) { const q = ((T - tN) * 1.6 + r / 3) % 1, w = Math.round(30 + q * 90), cx = 270, cy = 130; if (q < 0.9) { d2.P(cx - w / 2, cy - w / 2, w, 2, RED); d2.P(cx - w / 2, cy + w / 2, w, 2, RED); d2.P(cx - w / 2, cy - w / 2, 2, w, RED); d2.P(cx + w / 2, cy - w / 2, 2, w + 2, RED); } } }
      const d = px(k); plate(d, 98, 290, 248, 34); k.slam('At night, beat the beep.', 312, 876, tN + 0.2, {size: 48, color: GOLD, from: 0.4});
      return host(k, T >= tBeep + 0.6 ? 'wave' : 'point');
    },
  },
};
