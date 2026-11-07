/* Scene: Screenshot your old lead reports before the move (short of 2026-11-18-lsa-max-bid; arcade; Nov 7, 2026). One */
/* function per top-level cue in 03_cues/cues.md. Every time from a cue start or a spoken word (wordT). Worlds: hook =  */
/* Google's help line typed on (the receipt); send = the save file with the two steps, held still (the send card, cue   */
/* marked [send]); catch = our download screen (SOON), then the help line on the max; button = the save slot. The ad   */
/* screen and the save file are ours (EXAMPLE where shown), never Google's UI. Helpers copied from the parent's scene. */
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
/* our own drawn ad screen on a desk monitor (EXAMPLE, never Google's UI). o.box: 'empty' | 'filled' | 'gone' | 'none'; */
/* o.goneAt: the time the dashed outline starts to crumble; o.report: draw the spend bars under the box from that time.  */
const monitor = (k, o = {}) => {
  const d = px(k), {P, dith, disc, F} = d;
  P(0, 0, 360, 417, '#3D2E45'); for (let y = 0; y < 417; y += 4) dith(0, y, 360, 1, '#2B2033', (y / 4) % 2);
  /* the desk, the stand */
  P(0, 300, 360, 10, '#8C5A33'); P(0, 300, 360, 2, '#B07A47'); P(0, 310, 360, 107, '#4A2E1B');
  P(166, 290, 28, 10, '#2B2033'); P(146, 297, 68, 4, '#2B2033');
  /* the screen under the title plate: bezel and glass, y 154 to 292 */
  P(26, 154, 308, 138, INK); P(30, 158, 300, 130, '#1F2A40'); P(30, 158, 300, 16, o.newScreen ? '#2F6F67' : '#3B82C4');
  d.tx(o.newScreen ? 'NEW AD SCREEN' : 'LEAD ADS', 40, 160, {size: 36, color: CREAM, lint: false});
  for (let i = 0; i < 3; i++) disc(300 + i * 9, 166, 2, [RED, GOLD, TEAL][i]);
  boxRow(k, d, 40, 184, o);
  if (o.report !== undefined && k.T >= o.report) {
    d.tx('SPENT, BY WEEK', 40, 222, {size: 36, color: GOLD, lint: false});
    const h = [12, 20, 14, 26, 18, 22];
    h.forEach((v, i) => { const g = Math.min(v, Math.max(0, Math.floor((k.T - o.report) * 30 - i * 3))); P(196 + i * 20, 282 - g, 14, g, ORANGE); });
    P(190, 283, 130, 1, SAND);
  } else {
    d.tx('BUDGET', 40, 222, {size: 39, color: SAND, lint: false}); P(196, 218, 112, 22, '#253048');
    d.tx('ADS RUNNING', 40, 256, {size: 39, color: SAND, lint: false}); P(196, 254, 30, 14, TEAL); P(218, 255, 7, 12, CREAM);
  }
  return d;
};
/* the MAX PER LEAD row and its box at x, y (low-res); scale s (1 on the monitor, 2 in the close-up). o.box: 'empty' |  */
/* 'filled' | 'gone' (o.goneAt: when the dashed outline starts to crumble).                                              */
const boxRow = (k, d, x, y, o = {}, s = 1) => {
  const {P, F} = d, state = o.box || 'empty';
  d.tx('MAX PER LEAD', x + 4, y + 6 * s - 2, {size: 39 * s, color: SAND, lint: false});
  const bx = x + 156 * s - (s - 1) * 40, by = y, bw = 112 * s - (s - 1) * 60, bh = 26 * s;
  if (state === 'empty' || state === 'filled') {
    P(bx - s, by - s, bw + 2 * s, bh + 2 * s, state === 'filled' ? GOLD : SKY); P(bx, by, bw, bh, state === 'filled' ? '#4A3A1A' : NIGHT);
    if (state === 'filled') d.tx('$45', bx + 6 * s, by + 4 * s, {size: 39 * s, color: GOLD, lint: false});
    if ((F >> 4) % 2 === 0) P(state === 'filled' ? bx + bw - 10 * s : bx + 6 * s, by + 5 * s, 2 * s, 16 * s, CREAM);
  } else if (state === 'gone') {
    const q = clamp((k.T - (o.goneAt || 0)) / 0.6);
    for (let i = 0; i < bw; i += 6) if (hash(i * 1.7) > q) { P(bx + i, by - 1, 3, 1, GREY); P(bx + i, by + bh, 3, 1, GREY); }
    for (let j = 0; j < bh; j += 6) if (hash(j * 2.3 + 9) > q) { P(bx - 1, by + j, 1, 3, GREY); P(bx + bw, by + j, 1, 3, GREY); }
    if (q > 0 && q < 1) for (let i = 0; i < 10; i++) { const dy = Math.round(q * 40 * (0.5 + hash(i))); P(bx + Math.round(hash(i * 3.3) * bw), by + bh + dy, 2, 2, GREY); }
  }
};
/* a help-page quote card in the band: header GOOGLE ADS HELP, lines typed on from t0, the source tag under it */
const helpCard = (k, d, lines, t0, o = {}) => {
  const {P, win} = d, up = d.ease(t0, 6, 30);
  win(14, 84 + up, 332, o.h || 150, {base: CREAM, hi: '#FFFFFF', lo: SAND, rule: false});
  P(14, 84 + up, 332, 20, '#3B82C4'); k.text('GOOGLE ADS HELP', 72, 258 + up * 3, {size: 39, color: CREAM});
  if (up) return;
  let n = Math.max(0, Math.floor((k.T - t0 - 0.15) * 90));
  lines.forEach((s, i) => { const m = Math.min(s.length, n); n -= m; if (m) k.text(s.slice(0, m), 72, 336 + i * 64, {size: 52, color: INK}); });
  k.text('Source: Ads Help, read Nov 7, 2026', 72, (84 + (o.h || 150) - 18) * 3, {size: 36, color: '#4A4E5A'});
};
/* our own pixel camera flash: white for 2 frames at t, then a frame */
const flash = (k, d, t) => { const f = d.fr(t); if (f >= 0 && f < 2) d.P(0, 0, 360, 417, '#FFFFFF'); };

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'SAVE YOUR NUMBERS',
  sendLine: 'Send this to whoever runs your Google ads.',
  transitions: {send: 'levelselect', catch: 'fade4', button: 'gameover'},
  trauma: {},
  sections: {
    /* ---- hook (receipt): the cover is the plate and the help card already up; on "reports" the line types on; on     */
    /* "won't" STAYS BEHIND stamps. The host steps in at 0.6 s.                                                           */
    hook: (k, T) => {
      const tLine = clamp(wordT(k, 'hook', /^help/i, 0.4) - 0.3, 0.15, 0.7), tF = k.S('hook.flaps'), tStamp = Math.min(2.6, wordT(k, 'hook', /^reports/i, 1.6) - 0.1);
      if (T >= tF) {
        /* the departures board: what goes to Google Ads and what stays (the page: lead history moves; impressions, */
        /* clicks and weekly spend don't)                                                                            */
        k.sets.flaps({title: 'TO GOOGLE ADS', cols: 12, rows: [{label: 'LEADS', value: 'MOVE', at: tF + 0.05}, {label: 'SPEND', value: 'STAYS', at: tF + 0.35, hi: true}, {label: 'CLICKS', value: 'STAY', at: tF + 0.65, hi: true}]});
        return host(k, 'point');
      }
      const d = px(k), {P, dith} = d;
      const red = T >= tStamp;   /* the receipt lands: the band turns alarm red (lint hook: the second picture change by 3 s) */
      P(0, 0, 360, 417, red ? '#5A1F22' : '#253048'); { const sc = Math.floor(d.F / 2) % 8; for (let y = -8; y < 417; y += 8) dith(0, y + sc, 360, 2, red ? '#3E1518' : '#1F2A40', 0); }
      P(0, 417, 360, 223, NIGHT);
      if (T < tLine) {
        /* the cover: the plate, our report card, a big pixel arrow toward a closed door */
        topPlate(k, d, 'Your old lead reports:', 'not coming with you.', -1);
        d.win(40, 170, 120, 110, {base: CREAM, hi: '#FFFFFF', lo: SAND, rule: false});
        for (let r = 0; r < 5; r++) P(54, 190 + r * 14, 92 - (r % 2) * 24, 4, GREY);
        P(200, 214, 50, 12, GOLD); for (let i = 0; i < 12; i++) P(250 + i, 208 + i, 2, 24 - 2 * i, GOLD);
        P(286, 160, 50, 124, '#4A2E1B'); P(290, 164, 42, 116, '#8C5A33'); d.disc(324, 222, 3, GOLD);
        return {host: false, speech: false};
      }
      helpCard(k, d, ['"Your Local Services Ads', 'performance reports will', 'not transition to', 'Google Ads."'], tLine, {h: 176});
      if (T >= tStamp + 0.6) loopSweep(k, 72, 528, k.measure('not transition to', {size: 52}), tStamp + 0.6, 0.8, 8);
      if (T >= tStamp) stampBox(k, 'STAYS BEHIND', 600, 830, tStamp, {color: RED, freeze: 4});
      return host(k, T >= tStamp ? 'point' : null);
    },

    /* ---- send: the save file, SLOT 1: YOUR NUMBERS; step 1 lights on "screenshot", step 2 on "max". After that the card */
    /* holds still (no sweep, no blink over it) while the voice says who to send it to. The send card (cues.md [send]).   */
    send: (k, T) => {
      const t0 = k.S('send'), tShot = wordT(k, 'send', /^screenshot/i, 0.4), tMax = wordT(k, 'send', /^max$/i, 2.6);
      const d = px(k), {P, dith, win} = d;
      P(0, 0, 360, 417, '#3D2E45'); for (let y = 0; y < 417; y += 4) dith(0, y, 360, 1, '#2B2033', (y / 4) % 2); P(0, 417, 360, 223, NIGHT);
      const up = d.ease(t0 + 0.02, 5, 160);
      d.clip(0, 0, 360, 340, () => { win(14, 84 + up, 332, 166, {base: '#253048', hi: '#3B82C4', lo: INK, rule: false}); P(14, 84 + up, 332, 20, '#3B82C4'); P(316, 84 + up, 30, 10, '#120D14'); });
      if (up !== 0) return host(k);
      k.text('SLOT 1: YOUR NUMBERS', 72, 258, {size: 48, color: CREAM});
      [['1. Screenshot every', 'report you have', tShot], ['2. Write your max', 'per lead beside them', tMax]].forEach(([a, b, ti], i) => {
        const lit = T >= ti - 0.3, y = 330 + i * 196;
        k.slam(a, 72, y, Math.min(ti - 0.3, t0 + 0.2 + i * 0.1), {size: 66, color: lit ? GOLD : SAND, from: 0.3});
        k.slam(b, 72, y + 76, Math.min(ti - 0.3, t0 + 0.25 + i * 0.1), {size: 66, color: lit ? CREAM : SAND, from: 0.3});
        if (lit && T < ti + 0.6) k.sweep(72, y + 150, k.measure(b, {size: 66}), 6, ti - 0.25, {color: 'accent'}); });
      return host(k, 'point');
    },

    /* ---- catch: our download screen, the button greyed, SOON blinking (the page's word); then on "after" the help line */
    /* on the max, typed on, NO MAX stamps on "no".                                                                        */
    catch: (k, T) => {
      const t0 = k.S('catch'), tN = k.S('catch.nomax'), tNo = wordT(k, 'catch.nomax', /^no$/i, 1.6) - 0.1;
      const d = px(k), {P, dith, win} = d;
      P(0, 0, 360, 417, '#1F2A40'); for (let y = 0; y < 417; y += 4) dith(0, y, 360, 1, '#253048', (y / 4) % 2); P(0, 417, 360, 223, NIGHT);
      if (T < tN) {
        /* the calendar: the gold week frame looks row to row for the download date and finds none: SOON */
        const c = k.sets.calendar({month: 'DOWNLOAD DAY', days: 30, start: 0, fills: [],
          weeks: [0, 1, 2, 3, 4].map((r) => ({row: r, at: t0 + 0.1 + r * 0.7}))});
        const on = Math.floor((T - t0) * 2) % 2 === 0, a = c.area || {x: 300, y: 900, w: 600, h: 200};
        k.text('SOON', a.x + a.w / 2, a.y + 10, {size: 66, color: on ? GOLD : '#7A6A3A', align: 'center', drop: INK});
        k.text('Source: Ads Help, read Nov 7, 2026', a.x + a.w / 2, a.y + 96, {size: 36, color: SAND, align: 'center'});
        return host(k);
      }
      helpCard(k, d, ['"Manual bidding (such as', 'setting a maximum cost-per-', 'lead) is no longer', 'supported in Google Ads."'], tN - 0.3, {h: 176});
      if (T >= tNo) stampBox(k, 'NO MAX', 640, 830, tNo, {color: RED, freeze: 5});
      return host(k, T >= tNo ? 'shrug' : null);
    },

    /* ---- button: the save file fills, SAVED on "reports"; then the end card with the send line.                       */
    button: (k, T) => {
      const t0 = k.S('button'), tShots = wordT(k, 'button', /^screenshots/i, 1.2) - 0.3, tKeep = wordT(k, 'button', /^keep/i, 2.6) - 0.3;
      k.sets.inventory({title: 'YOUR NUMBERS', items: [
        {icon: 'clip', name: 'SCREENSHOTS', stats: [{label: 'SAVED', value: 1, max: 1, text: 'YES'}]},
        {icon: 'coin', name: 'YOUR MAX', stats: [{label: 'NOTED', value: 1, max: 1, text: 'YES'}]}],
        select: [{slot: 0, at: Math.min(tShots, t0 + 0.3)}, {slot: 1, at: Math.max(tShots + 0.8, tKeep)}]});
      return host(k, T >= tKeep + 0.4 ? 'wave' : 'point');
    },
  },
};

/* the parent's r28 fix (code QA: flat stretches): a faint dither drifts down the empty lower band of every scene, below */
/* the host and every text, so no stretch goes still. It never crosses the send card (band y 84 to 250).                 */
const drift = (k) => { const d = px(k), off = Math.floor(k.T * 30) % 16; for (let y = 418 - 16 + off; y < 640; y += 16) { const y0 = Math.max(418, y), y1 = Math.min(640, y + 8); if (y1 > y0) d.P(0, y0, 360, y1 - y0, '#2B2033'); } };
for (const [n, f] of Object.entries(window.SCENE.sections)) window.SCENE.sections[n] = (k, T) => { const r = f(k, T); drift(k); return r; };
