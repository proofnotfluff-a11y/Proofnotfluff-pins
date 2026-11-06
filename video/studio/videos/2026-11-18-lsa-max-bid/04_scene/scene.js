/* Scene: The box where you set your max is going away (story, shape moment, arcade; round 2 on the new line, Nov 6,  */
/* 2026). One function per top-level cue in 03_cues/cues.md. Numbers only from k.data; every time from a cue start or */
/* a spoken word (wordT). Worlds: hook, now, button = our own drawn ad screen on a desk monitor (EXAMPLE, never Google's */
/* UI); move = our own street and the wave strip; rule = Google's help line typed on, then the OLD and GOOGLE ADS split; */
/* download = our download screen and camera; setup = the save file and the calendar; button.end = the save slot.     */
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
    if (state === 'filled') d.tx('YOUR MAX', bx + 6 * s, by + 4 * s, {size: 39 * s, color: GOLD, lint: false});
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
  let n = Math.max(0, Math.floor((k.T - t0 - 0.25) * 34));
  lines.forEach((s, i) => { const m = Math.min(s.length, n); n -= m; if (m) k.text(s.slice(0, m), 72, 336 + i * 64, {size: 52, color: INK}); });
  k.text('Google Ads Help, read Nov 6, 2026', 72, (84 + (o.h || 150) - 18) * 3, {size: 36, color: '#4A4E5A'});
};
/* our own pixel camera flash: white for 2 frames at t, then a frame */
const flash = (k, d, t) => { const f = d.fr(t); if (f >= 0 && f < 2) d.P(0, 0, 360, 417, '#FFFFFF'); };

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'SAVE YOUR NUMBERS',
  sendLine: 'Send this to whoever runs your Google ads.',
  transitions: {move: 'dissolve', now: 'fade4', rule: 'mosaic', download: 'dissolve', setup: 'levelselect', button: 'gameover'},
  trauma: {'hook.gone': 0.6},
  sections: {
    /* ---- hook: scene one, the box (cover, no host): our ad screen, the cursor in the MAX PER LEAD box; on "type" it   */
    /* fills gold. Scene two on "Then": the new screen, the box crumbles on "gone", BOX GONE stamps.                      */
    hook: (k, T) => {
      const tIn = Math.min(0.9, Math.max(0.5, wordT(k, 'hook', /^open/i, 0.4) + 0.2)), tType = wordT(k, 'hook', /^type/i, 1.6) - 0.05, tTwo = k.S('hook.gone'), tGone = wordT(k, 'hook.gone', /^gone/i, 2.4);
      if (T >= tTwo) {
        const d = monitor(k, {box: 'gone', goneAt: tGone - 0.3, newScreen: true});
        topPlate(k, d, 'One day:', 'the box is gone.', tTwo + 0.02);
        if (T >= tGone) stampBox(k, 'BOX GONE', 540, 820, tGone, {color: RED, freeze: 4});
        exampleTag(d, 254, 296);
        return host(k, T >= tGone ? 'shrug' : null);
      }
      if (T >= tIn) {
        /* the close-up: the box big, the cursor in it; it fills gold on "type" */
        const d = px(k), {P, dith} = d;
        P(0, 0, 360, 417, '#1F2A40'); for (let y = 150; y < 417; y += 4) dith(0, y, 360, 1, '#253048', (y / 4) % 2);
        { const fill = T >= tType, bx = 40, by = 206, bw = 280, bh = 56;
          k.text('MAX PER LEAD', 120, 492, {size: 66, color: SAND});
          P(bx - 2, by - 2, bw + 4, bh + 4, fill ? GOLD : SKY); P(bx, by, bw, bh, fill ? '#4A3A1A' : NIGHT);
          const n = fill ? Math.min(8, Math.floor((T - tType) * 30)) : 0; if (n) k.text('YOUR MAX'.slice(0, n), 168, 642, {size: 99, color: GOLD});
          if ((d.F >> 4) % 2 === 0) P(fill ? bx + 16 + Math.round(k.measure('YOUR MAX'.slice(0, n), {size: 99}) / 3) + 4 : bx + 14, by + 10, 4, 36, CREAM); }
        topPlate(k, d, 'Your max per lead:', 'going away.', -1);
        exampleTag(d, 254, 296);
        P(0, 417, 360, 223, NIGHT);
        return host(k);
      }
      const d = monitor(k, {box: 'empty'});
      topPlate(k, d, 'Your max per lead:', 'going away.', -1);
      exampleTag(d, 254, 296);
      return {host: false, speech: false};
    },

    /* ---- move: our own street, a van carrying the LOCAL SERVICES ADS sign drives into the GOOGLE ADS building. On      */
    /* "waves" the wave strip: three tiles, a wave rolls along them; on "truck" a van drops on LATE 2026: YOUR WAVE.      */
    move: (k, T) => {
      const t0 = k.S('move'), tW = k.S('move.waves'), tTruck = wordT(k, 'move.waves', /^truck/i, 3.2), tLate = wordT(k, 'move.waves', /^late/i, 4.5);
      if (T < tW) {
        const d = px(k), {P, dith, F} = d;
        P(0, 0, 360, 417, SKY); for (let i = 0; i < 3; i++) { const cx = ((i * 140 - Math.floor(F / 5)) % 480 + 480) % 480 - 60; d.disc(cx, 60 + i * 10, 10, CREAM); d.disc(cx + 12, 56 + i * 10, 12, CREAM); }
        /* the building */
        P(200, 130, 150, 287, '#C9CCD3'); for (let y = 150; y < 400; y += 26) for (let x = 212; x < 340; x += 30) P(x, y, 18, 16, '#253048');
        P(200, 120, 150, 26, '#3B82C4'); k.text('GOOGLE ADS', 825, 372, {size: 48, color: CREAM, align: 'center'});
        P(250, 360, 50, 57, INK); P(254, 364, 42, 53, '#4A4E5A');
        P(0, 417, 360, 223, '#2B2033'); P(0, 417, 360, 3, '#4A4E5A');
        /* the van with its sign */
        const vx = Math.round(-80 + Math.min(1, (T - t0) / Math.max(0.8, tW - t0 - 0.2)) * 330);
        if (vx < 252) { k.sets.van(vx, 386, {wheel: F}); P(vx + 4, 352, 92, 26, INK); P(vx + 6, 354, 88, 22, ORANGE); k.text('LOCAL SERVICES', (vx + 10) * 3, 1064, {size: 30, color: INK, lint: false}); k.text('ADS', (vx + 10) * 3, 1094, {size: 30, color: INK, lint: false}); }
        topPlate(k, d, 'Local Services Ads', 'move into Google Ads.', t0 + 0.05, {base: NIGHT, hi: '#3D2E45', rule: '#3D2E45'});
        return host(k);
      }
      const d = px(k), {P, dith, win, F} = d;
      P(0, 0, 360, 417, '#245752'); for (let y = 0; y < 417; y += 4) dith(0, y, 360, 1, '#2F6F67', (y / 4) % 2);
      k.text('THE MOVE, IN WAVES', 72, 264, {size: 48, color: GOLD});
      const tiles = [['AUG 2026', 'FIRST WAVE', tW + 0.2], ['LATE 2026', 'NO STOREFRONT', tLate - 0.3], ['2027', 'THE REST', tLate + 0.4]];
      tiles.forEach(([a, b, ti], i) => { const x = 18 + i * 110, lit = T >= ti, mine = i === 1 && T >= tTruck;
        win(x, 104, 102, 120, {base: mine ? '#4A3A1A' : (lit ? '#253048' : NIGHT), hi: mine ? GOLD : '#3B82C4', lo: INK, rule: mine ? GOLD : false});
        k.text(a, (x + 51) * 3, 360, {size: 39, color: lit ? CREAM : GREY, align: 'center'});
        k.text(b, (x + 51) * 3, 420, {size: 30, color: lit ? SAND : GREY, align: 'center'}); });
      /* the wave: a crest rolling along under the tiles */
      { const q = ((T - tW) * 0.5) % 1, cx = Math.round(18 + q * 330); for (let i = -20; i <= 20; i++) { const h = Math.round(6 * Math.cos(i / 20 * Math.PI / 2)); P(cx + i, 236 - h, 1, h + 2, SKY); } P(0, 238, 360, 4, '#3B82C4'); }
      if (T >= tTruck) { const dy = d.ease(tTruck, 5, 30); k.sets.van(140, 182 - dy, {wheel: F}); if (!dy) k.slam('YOUR WAVE', 495, 700, tTruck + 0.1, {size: 48, color: GOLD, align: 'center', from: 0.4}); }
      plate(d, 98, 290, 248, 30); k.text('Google Ads Help, read Nov 6, 2026', 312, 900, {size: 36, color: SAND});
      return host(k, T >= tTruck ? 'point' : null);
    },

    /* ---- now: back on the monitor, the box filled with YOUR MAX and the report's spend bars growing (EXAMPLE).        */
    now: (k, T) => {
      const t0 = k.S('now'), tRep = wordT(k, 'now', /^reports?/i, 1.4) - 0.2;
      const d = monitor(k, {box: 'filled', report: tRep});
      topPlate(k, d, 'Until your move:', 'you set your max.', t0 + 0.05);
      exampleTag(d, 254, 296);
      loopSweep(k, 588, 444, k.measure('YOUR MAX', {size: 39}), t0 + 0.4, 1.0, 6);
      return host(k);
    },

    /* ---- rule: mosaic to Google's help page line, typed on; NO MAX stamps. Then the split: OLD reports on the left    */
    /* try to cross into GOOGLE ADS and bounce back: STAYS BEHIND, with the page's line.                                  */
    rule: (k, T) => {
      const t0 = k.S('rule'), tR = k.S('rule.reports'), tMax = wordT(k, 'rule', /^max/i, 2.6);
      if (T < tR) {
        const d = px(k), {P, dith} = d;
        P(0, 0, 360, 417, '#253048'); { const sc = Math.floor(d.F / 2) % 8; for (let y = -8; y < 417; y += 8) dith(0, y + sc, 360, 2, '#1F2A40', 0); }
        P(0, 417, 360, 223, NIGHT);
        helpCard(k, d, ['"Manual bidding (such as', 'setting a maximum cost-per-', 'lead) is no longer', 'supported in Google Ads."'], t0 + 0.05, {h: 176});
        if (T >= tMax) stampBox(k, 'NO MAX', 640, 830, tMax, {color: RED, freeze: 5});
        return host(k, T >= tMax ? 'point' : null);
      }
      const d = px(k), {P, dith, F} = d, tBack = tR + 1.0;
      P(0, 0, 180, 417, '#7A3442'); P(180, 0, 180, 417, '#2F6F67'); P(178, 0, 4, 417, CREAM);
      k.text('OLD', 270, 270, {size: 48, color: CREAM, align: 'center'}); k.text('GOOGLE ADS', 810, 270, {size: 48, color: CREAM, align: 'center'});
      /* the empty shelf on the right */
      P(206, 200, 130, 4, '#4A2E1B'); P(206, 150, 130, 4, '#4A2E1B');
      /* three report papers: they slide toward the line, hit it and bounce back */
      for (let i = 0; i < 3; i++) { const ph = T - tR - i * 0.12, push = ph < 0 ? 0 : (T < tBack ? Math.min(1, ph / 0.7) : Math.max(0, 1 - (T - tBack) / 0.25));
        const x = 40 + i * 40 + Math.round(push * (150 - (40 + i * 40) - 30 + i * 4)), y = 150 + (i % 2) * 18;
        P(x + 2, y + 2, 30, 40, INK); P(x, y, 30, 40, CREAM); for (let r = 0; r < 4; r++) P(x + 4, y + 8 + r * 7, 22 - (r % 2) * 6, 2, '#9AA0AD'); P(x + 4, y + 34, 10, 3, ORANGE); }
      if (T >= tBack) stampBox(k, 'STAYS BEHIND', 540, 670, tBack, {color: GOLD, size: 48, freeze: 4});
      P(0, 417, 360, 223, '#2B2033');
      plate(d, 98, 290, 248, 34);
      k.text('"performance reports will not', 312, 876, {size: 36, color: SAND}); k.text('transition" (Google Ads Help)', 312, 918, {size: 36, color: GOLD});
      return host(k, T >= tBack ? 'shrug' : null);
    },

    /* ---- download: our drawn download screen: the button greyed, a bar that crawls and slips back, COMING SOON        */
    /* blinking twice a second. On "Need": a camera flash and the page's line, "take screenshots of them before migrating". */
    download: (k, T) => {
      const t0 = k.S('download'), tShot = k.S('download.shot'), tTake = wordT(k, 'download.shot', /^screenshots?/i, 1.0) - 0.2;
      const d = px(k), {P, dith, win, F} = d;
      P(0, 0, 360, 417, '#1F2A40'); for (let y = 0; y < 417; y += 4) dith(0, y, 360, 1, '#253048', (y / 4) % 2); P(0, 417, 360, 223, NIGHT);
      if (T < tShot) {
        win(14, 84, 332, 200, {base: NIGHT, hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
        k.text('YOUR OLD REPORTS', 72, 276, {size: 48, color: CREAM});
        P(40, 140, 280, 40, '#4A4E5A'); P(42, 142, 276, 36, '#6B7080'); k.text('DOWNLOAD', 540, 444, {size: 52, color: '#9AA0AD', align: 'center'});
        const q = ((T - t0) * 0.45) % 1, w = Math.round(30 + 60 * Math.sin(q * Math.PI));
        P(40, 200, 280, 14, INK); P(42, 202, w, 10, ORANGE);
        const on = Math.floor((T - t0) * 2) % 2 === 0; k.text('COMING SOON', 540, 690, {size: 66, color: on ? GOLD : '#7A6A3A', align: 'center', drop: INK});
        plate(d, 98, 290, 248, 30); k.text('Google Ads Help, read Nov 6, 2026', 312, 900, {size: 36, color: SAND});
        return host(k);
      }
      /* the camera */
      P(40, 110, 120, 80, INK); P(44, 114, 112, 72, '#4A4E5A'); d.disc(100, 150, 26, INK); d.disc(100, 150, 22, '#253048'); d.disc(100, 150, 12, '#3B82C4'); d.disc(94, 144, 4, CREAM); P(130, 104, 20, 10, INK); P(132, 106, 16, 8, GOLD);
      flash(k, d, tShot + 0.05); flash(k, d, tTake);
      win(176, 96, 170, 120, {base: CREAM, hi: '#FFFFFF', lo: SAND, rule: false});
      k.text('Need them now?', 564, 312, {size: 48, color: '#4A4E5A'});
      if (T >= tTake) { k.slam('"take screenshots', 564, 400, tTake, {size: 52, color: INK, from: 0.3}); k.slam('of them before', 564, 460, tTake + 0.08, {size: 52, color: INK, from: 0.3}); k.slam('migrating."', 564, 520, tTake + 0.16, {size: 52, color: INK, from: 0.3}); }
      plate(d, 98, 290, 248, 30); k.text('Google Ads Help, read Nov 6, 2026', 312, 900, {size: 36, color: SAND});
      return host(k, T >= tTake ? 'point' : null);
    },

    /* ---- setup: the save screen (SAVE FILE, our game move at the turn): steps 1 and 2 light on their words, held. On   */
    /* "warning" the calendar: the move day, an envelope fourteen days before it (k.data), step 3 on the card below.     */
    setup: (k, T) => {
      const t0 = k.S('setup'), tShot = wordT(k, 'setup', /^screenshot/i, 1.0), tMax = wordT(k, 'setup', /^max$/i, 2.6), tE = k.S('setup.email'), tInbox = wordT(k, 'setup.email', /^inbox/i, 5.0);
      const n14 = k.data.numbers.notice.value;
      if (T < tE) {
        const d = px(k), {P, dith, win} = d;
        P(0, 0, 360, 417, '#3D2E45'); for (let y = 0; y < 417; y += 4) dith(0, y, 360, 1, '#2B2033', (y / 4) % 2); P(0, 417, 360, 223, NIGHT);
        const up = d.ease(t0 + 0.05, 6, 160);
        d.clip(0, 0, 360, 322, () => win(14, 84 + up, 332, 236, {base: NIGHT, hi: '#7A3442', lo: INK, rule: GOLD}));
        if (up !== 0) return host(k);
        k.text('SAVE FILE: YOUR NUMBERS', 72, 270, {size: 48, color: GOLD});
        [['1. Screenshot every', 'report you have', tShot], ['2. Write your max', 'beside them', tMax]].forEach(([a, b, ti], i) => {
          const lit = T >= ti - 0.25, y = 344 + i * 170;
          k.slam(a, 72, y, Math.min(ti - 0.25, t0 + 0.3 + i * 0.1), {size: 66, color: lit ? GOLD : GREY, from: 0.3});
          k.slam(b, 72, y + 76, Math.min(ti - 0.2, t0 + 0.35 + i * 0.1), {size: 66, color: lit ? CREAM : GREY, from: 0.3});
          if (lit) k.sweep(72, y + 150, k.measure(b, {size: 66}), 6, ti - 0.2, {color: 'accent'}); });
        loopSweep(k, 72, T >= tMax - 0.25 ? 664 : 494, k.measure(T >= tMax - 0.25 ? 'beside them' : 'report you have', {size: 66}), tShot + 0.6, 1.0);
        if ((d.F >> 4) % 2 === 0) d.P(318, 254, 3, 14, GOLD);
        return host(k, 'point');
      }
      const tEnv = wordT(k, 'setup.email', /^fourteen/i, 2.6) - 0.25;
      const c = k.sets.calendar({month: 'YOUR MOVE', days: 28, start: 0, numbersTo: 28,
        fills: [{day: 28, at: tE - 0.3, mark: 'fill', c: RED}, {day: 28 - n14, at: tEnv, mark: 'fill', c: GOLD}],
        run: {from: 28 - n14 + 1, to: 27, at: tEnv + 0.2, every: 0.05, c: '#F4E6D3', mark: 'check', mc: '#2F6F67'}});
      const d = px(k), {P} = d;
      { const [x, y] = c.cell ? c.cell(28 - n14) : [0, 0]; if (T >= tEnv + 0.1 && c.cell) { const dy = d.ease(tEnv + 0.1, 5, 16); P(x + 10, y + 6 - dy, 24, 16, INK); P(x + 11, y + 7 - dy, 22, 14, CREAM); d.line(x + 11, y + 7 - dy, x + 22, y + 15 - dy, '#9AA0AD'); d.line(x + 33, y + 7 - dy, x + 22, y + 15 - dy, '#9AA0AD'); } }
      plate(d, 98, 290, 248, 34);
      k.slam(`${n14} DAYS OUT: ADMIN EMAIL`, 312, 870, tEnv, {size: 39, color: GOLD, from: 0.3});
      const lit3 = T >= tInbox - 0.3; k.slam('3. Admin email: an inbox you read', 312, 918, Math.min(tInbox - 0.3, tE + 0.6), {size: 36, color: lit3 ? CREAM : GREY, from: 0.3});
      return host(k, 'point');
    },

    /* ---- button: the monitor, the box crumbled; on "Grab" the save slot fills: SAVED, the screenshots inside. Snow    */
    /* points. Then the end card with the send line.                                                                    */
    button: (k, T) => {
      const t0 = k.S('button'), tGrab = wordT(k, 'button', /^grab/i, 1.6);
      if (T < tGrab) {
        const d = monitor(k, {box: 'gone', goneAt: t0 - 1, newScreen: true});
        topPlate(k, d, 'The box is going,', 'whatever you do.', t0 + 0.05);
        exampleTag(d, 254, 296);
        return host(k, 'shrug');
      }
      const d = px(k), {P, dith, win, F} = d;
      P(0, 0, 360, 417, '#120D14'); for (let i = 0; i < 40; i++) d.DOT(Math.floor(hash(i * 3.7) * 360), Math.floor(hash(i * 9.1) * 300), (Math.floor(F / 15) + i) % 5 === 0 ? GOLD : '#4A4E5A');
      k.text('SAVE SLOT 1', 540, 270, {size: 52, color: GOLD, align: 'center'});
      win(30, 110, 300, 150, {base: NIGHT, hi: '#3B82C4', lo: INK, rule: '#3B82C4'});
      for (let i = 0; i < 4; i++) { const ti = tGrab + 0.1 + i * 0.15; if (T < ti) continue; const dy = d.ease(ti, 4, 20), x = 50 + i * 66; P(x + 2, 134 - dy + 2, 52, 66, INK); P(x, 134 - dy, 52, 66, CREAM); P(x + 4, 138 - dy, 44, 34, '#253048'); for (let r = 0; r < 3; r++) P(x + 8 + r * 12, 162 - dy - r * 6, 8, 8 + r * 6, ORANGE); }
      const tSaved = tGrab + 0.8; if (T >= tSaved) stampBox(k, 'SAVED', 540, 640, tSaved, {color: TEAL, freeze: 4});
      P(0, 417, 360, 223, NIGHT);
      plate(d, 98, 290, 248, 34); k.slam('Grab your numbers this week.', 312, 876, tGrab + 0.1, {size: 48, color: GOLD, from: 0.4});
      return host(k, T >= tSaved + 0.6 ? 'wave' : 'point');
    },
  },
};
