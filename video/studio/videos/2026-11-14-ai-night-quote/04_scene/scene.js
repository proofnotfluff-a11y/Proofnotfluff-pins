/* Scene: The 11 pm quote request (fix-this, AI lane, arcade; Nov 1, 2026). One function per top-level cue in 03_cues/  */
/* cues.md. Numbers only from k.data (brief.md -> data.js); every time from a cue start (k.S) or a spoken word (wordT).  */
/* The reply and the prompt are the exact text of video/studio/demos/out/2026-11-14-ai-night-quote-4/run.json (facts). */
/* Worlds: hook = our own bedroom at night (nightstand phone) and the reply card; usual = flaps; guess = our own work   */
/* order card, then gauge; fix = the Gemini page shots in a phone frame, then the ITEM GET prompt card; check = the     */
/* reply card; button = levelup. None used by missed-call-text (workbench, boss, register, scores).                   */
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', GREY = '#9AA0AD';
const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eo = (x) => 1 - Math.pow(1 - clamp(x), 3);

/* ---- the pixel kit (low-res units: 360 x 640, one pixel = 3 frame units), the same primitives the sets use ---- */
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
    const base = o.base || '#253048', hi = o.hi || '#3B82C4', lo = o.lo || '#1B1420', rule = o.rule === undefined ? '#87CEEB' : o.rule;
    if (o.shadow !== false) P(x + 2, y + 2, w, h, INK);
    P(x + 1, y, w - 2, h, INK); P(x, y + 1, w, h - 2, INK);
    P(x + 1, y + 1, w - 2, h - 2, base); P(x + 2, y + 1, w - 4, 1, hi); P(x + 1, y + 2, 1, h - 4, hi); P(x + 2, y + h - 2, w - 4, 1, lo); P(x + w - 2, y + 2, 1, h - 4, lo);
    if (rule) { P(x + 3, y + 3, w - 6, 1, rule); P(x + 3, y + h - 4, w - 6, 1, rule); P(x + 3, y + 3, 1, h - 6, rule); P(x + w - 4, y + 3, 1, h - 6, rule); }
  };
  const fr = (t0) => Math.floor((T - t0) * 30 + 0.005);
  const ease = (t0, frames, dist) => Math.round(dist * (1 - eo(fr(t0) / frames)));
  const tx = (s, x, y, o = {}) => k.text(s, x * 3, y * 3, Object.assign({size: 39}, o));
  const tw = (s, size = 39) => k.measure(String(s), {size}) / 3;
  const clip = (x, y, w, h, fn) => { ctx.save(); ctx.beginPath(); ctx.rect(x * 3, y * 3, w * 3, h * 3); ctx.clip(); fn(); ctx.restore(); };
  const twinkle = (x, y, f, c = CREAM) => { const s = [0, 1, 2, 1][((f % 4) + 4) % 4]; DOT(x, y, c); for (let i = 1; i <= s; i++) { DOT(x - i, y, c); DOT(x + i, y, c); DOT(x, y - i, c); DOT(x, y + i, c); } };
  const coin = (x, y, f) => {
    const ws = [4, 3, 1, 3][((f % 4) + 4) % 4];
    for (let j = 0; j < 8; j++) { const dy = j - 3.5, hw = Math.max(0, Math.round(ws * Math.sqrt(Math.max(0, 1 - (dy * dy) / 16)))); if (!hw) continue; P(x + 4 - hw, y + j, 2 * hw, 1, '#B07A47'); if (hw > 1) P(x + 4 - hw + 1, y + j, 2 * hw - 2, 1, j < 4 ? GOLD : ORANGE); }
    if (ws >= 3) { P(x + 4, y + 2, 1, 4, '#B07A47'); DOT(x + 3, y + 2, CREAM); }
  };
  return {P, DOT, dith, disc, line, win, fr, ease, tx, tw, clip, twinkle, coin, F, T};
};

/* ---- the words: every beat lands on a spoken word ---- */
const WS = () => (window.WORDS && window.WORDS.words) || [];
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
const bob2 = (T, t0) => (T - t0 < 0.3 ? 0 : [0, 6, 0, -6][Math.floor((T - t0 - 0.3) / 0.15) % 4]);
const host = (k, pose) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150});
const plate = (d, x, y, w, h) => d.win(x, y, w, h, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
/* a rubber stamp in a dark box with a coloured rim, landed with the kit's hit-stop */
const stampBox = (k, s, cx, y, t0, o = {}) => {
  const size = o.size || 66, c = o.color || GOLD, w = Math.round((k.measure(s, {size}) + 54) / 6) * 6, h = size + 36, x = Math.round((cx - w / 2) / 3) * 3;
  k.stampIn(t0, () => {
    k.shape(k.rectPts(x + 6, y + 6, w, h, 0), {fill: INK, line: false}); k.shape(k.rectPts(x, y, w, h, 0), {fill: '#1B1420', line: false});
    k.shape(k.rectPts(x + 6, y + 6, w - 12, 6, 0), {fill: c, line: false}); k.shape(k.rectPts(x + 6, y + h - 12, w - 12, 6, 0), {fill: c, line: false});
    k.shape(k.rectPts(x + 6, y + 6, 6, h - 12, 0), {fill: c, line: false}); k.shape(k.rectPts(x + w - 12, y + 6, 6, h - 12, 0), {fill: c, line: false});
    k.text(s, x + w / 2, y + 18, {size, color: c, align: 'center'});
  }, {at: [x + w / 2, y + h], freeze: o.freeze});
};

const mute = (k, drop, fn) => { const real = k.text; k.text = function (s, x, y, o) { if (drop(s, x, y, o)) return; return real.call(this, s, x, y, o); }; try { return fn(); } finally { k.text = real; } };
const chipText = (k, s, x, y, o) => { const w = k.measure(String(s), {size: o.size}), x0 = o.align === 'right' ? x - w : o.align === 'center' ? x - w / 2 : x; k.ctx.fillStyle = INK; k.ctx.fillRect(Math.floor(x0 - 15), y - 9, Math.ceil(w + 30), Math.round(o.size * 1.2)); k.text(s, x, y, o); };

/* ---- the run's own words (run.json, Nov 1, 2026), split only at its own line breaks ---- */
const PROMPT = ['Reply to this cleaning quote', 'text for me. Friendly,', 'under 50 words.', 'My price: [your price].', 'Ask one question if', "anything's missing."];
const REPLY = ["Hi! I’d love to help with your move-out clean. For a 2-bed, 1-bath, my rate is [your price].",
  'Could you let me know if you need the inside of the oven or fridge included?',
  'Let me know what day before Friday works best for you!'];
const CUSTOMER = 'Hi! Need a quote for a move-out clean, 2 bed 1 bath, before Friday. Thanks!';
const LABEL = ['REAL REPLY: GEMINI 3.6 FLASH (API)', 'NOV 1, 2026'];
const glyphs = (l) => l.replace(/\u2019/g, "'");   /* the pixel font has no curly apostrophe: the same word, drawn straight */

/* the bedroom at night: a dark wall, a window with the moon and a city line, the nightstand top, the phone glow */
const bedroom = (k, o = {}) => {
  const d = px(k), {P, DOT, dith, disc, F} = d;
  P(0, 0, 360, 417, '#1B1420'); for (let y = 0; y < 417; y += 6) P(0, y, 360, 1, '#1F1726');
  /* the window, top right: a navy sky, the moon, stars that twinkle slowly, a skyline */
  const wide = o.wide, wx = wide ? 14 : 214, wy = wide ? 20 : 20, ww = wide ? 332 : 128, wh = wide ? 150 : 88;
  P(wx - 4, wy - 4, ww + 8, wh + 8, '#3D2E45'); P(wx, wy, ww, wh, '#253048'); dith(wx, wy + wh - 30, ww, 30, '#2B3A5A');
  disc(wx + ww - 32, wy + 24, 9, '#FFF2B8'); disc(wx + ww - 28, wy + 21, 8, '#253048');
  for (let i = 0; i < (wide ? 22 : 9); i++) { const x = wx + 6 + Math.floor(hash(i * 3.1) * (ww - 12)), y = wy + 6 + Math.floor(hash(i * 7.3) * 40); DOT(x, y, (Math.floor(F / 18) + i) % 4 === 0 ? GOLD : '#6B7080'); }
  for (let x = wx; x < wx + ww; x += 8) { const h = 10 + Math.floor(hash(x * 0.37) * 26); P(x, wy + wh - h, 7, h, '#120D14'); if (hash(x * 1.7) > 0.5) DOT(x + 3, wy + wh - h + 4, GOLD); }
  P(wx + ww / 2 - 1, wy, 2, wh, '#3D2E45'); P(wx, wy + wh / 2 - 1, ww, 2, '#3D2E45');
  /* the nightstand */
  const top = o.top || 300;
  P(0, top, 360, 8, '#7A4E2C'); P(0, top, 360, 1, '#B07A47'); P(0, top + 8, 360, 417 - top - 8, '#5A3720');
  for (let y = top + 18; y < 417; y += 22) P(0, y, 360, 1, '#3D2717');
  P(0, 417, 360, 223, '#120D14'); for (let x = 0; x < 360; x += 24) P(x, 417, 1, 223, '#1B1420'); P(0, 417, 360, 2, '#2B2033');
  return d;
};
/* a phone face (low-res units) with a glow; returns the screen box */
const bigPhone = (k, d, x, y, w, h, o = {}) => {
  const {P} = d;
  if (o.glow) { k.ctx.save(); k.ctx.globalAlpha = 0.18; P(x - 10, y - 10, w + 20, h + 20, '#87CEEB'); k.ctx.restore(); }
  P(x + 3, y + 3, w, h, INK); P(x - 1, y, w + 2, h, INK); P(x, y - 1, w, h + 2, INK);
  P(x, y, w, h, '#2B2033'); P(x + 1, y, w - 2, 1, '#4A4E5A');
  P(x + 4, y + 8, w - 8, h - 16, o.screen || '#F4E6D3'); P(x + Math.round(w / 2) - 6, y + 3, 12, 2, INK);
  return {x: x + 4, y: y + 8, w: w - 8, h: h - 16};
};
/* the hook's title plate */
const hookPlate = (k, d, n) => {
  k.text(`${n.night.shown} pm quote.`, 540, 270, {size: 66, color: CREAM, align: 'center', drop: INK});
  k.text(`Reply in ${n.under.shown} seconds.`, 540, 346, {size: 66, color: GOLD, align: 'center', drop: INK});
};
/* a tag on a dark chip (sources, addresses, EXAMPLE) */
const tag = (k, s, x, y, o = {}) => chipText(k, s, x, y, Object.assign({size: 39, color: SAND}, o));
/* the reply card: cream, the label on an ink band, the reply's own lines wrapped at 39; o.hi = {lineIndex: color}, */
/* o.strike = [lineIndex], o.cut (dims), o.price (gold sweep on [your price]). Returns {x, y, w, h, lines}             */
const replyCard = (k, x, y, w, o = {}) => {
  const lh = 50, pad = 30, rows = [];
  REPLY.forEach((p, pi) => k.wrap(p, {size: 39}, w - 2 * pad).forEach((l) => rows.push([l, pi])));
  const n = o.max != null ? Math.min(o.max, rows.length) : rows.length, h = 126 + n * lh + 30 + (o.extra || 0);
  const fl = o.float ? bob2(k.T, o.float) / 2 : 0;
  k.ctx.fillStyle = INK; k.ctx.fillRect(x + 9, y + 9 + fl, w, h); k.ctx.fillRect(x - 3, y - 3 + fl, w + 6, h + 6);
  k.ctx.fillStyle = CREAM; k.ctx.fillRect(x, y + fl, w, h);
  k.ctx.fillStyle = '#2F6F67'; k.ctx.fillRect(x, y + fl, w, 108);
  k.text(LABEL[0], x + 24, y + 14 + fl, {size: 39, color: CREAM}); k.text(LABEL[1], x + 24, y + 58 + fl, {size: 39, color: GOLD});
  rows.slice(0, n).forEach(([l, pi], i) => {
    const ly = y + 126 + i * lh + fl;
    if (o.hi && o.hi[pi] && k.T >= o.hi[pi][1]) { k.ctx.fillStyle = o.hi[pi][0]; k.ctx.fillRect(x + 12, ly - 6, w - 24, lh - 2); }
    const dead = o.strike && o.strike.includes(pi) && k.T >= o.strikeAt;
    k.text(glyphs(l), x + pad, ly, {size: 39, color: dead ? '#B5524A' : INK});
    if (dead) { k.ctx.fillStyle = RED; k.ctx.fillRect(x + pad - 6, ly + 15, Math.min(w - 2 * pad + 12, k.measure(glyphs(l), {size: 39}) + 12), 6); }
    if (o.priceAt != null && k.T >= o.priceAt && l.includes('[your price]')) {
      const pre = glyphs(l).slice(0, l.indexOf('[your price]')), px0 = x + pad + k.measure(pre, {size: 39}), pw = k.measure('[your price]', {size: 39});
      k.sweep(px0 - 6, ly - 6, pw + 12, lh - 2, o.priceAt, {color: GOLD}); k.text('[your price]', px0, ly, {size: 39, color: INK, lint: false});
    }
  });
  return {x, y: y + fl, w, h, rows: n};
};

/* the save card (C3): a dark terminal-style PROMPT window. The lines type in as it lands (0.06 s a letter, all six in */
/* about 1.2 s), a block cursor blinks at 2 a second after the last letter and the window floats 1 px, so it is never */
/* flat (M1). A gold COPY THIS tab rides its top edge. o.red: line indexes lit red from o.redAt.                    */
const promptBox = (k, t0, o = {}) => {
  const T = k.T; if (T < t0) return null;
  const x = 54, w = 900, lh = 72, pad = 36, y0 = 300, h = pad * 2 + PROMPT.length * lh - 6;
  const q = eo(clamp((T - t0) / 0.25)), y = Math.round((y0 + (1 - q) * 60) / 3) * 3 + (T >= t0 + 1.6 ? bob2(T, t0 + 1.6) / 2 : 0);
  k.ctx.fillStyle = INK; k.ctx.fillRect(x + 9, y + 9, w, h); k.ctx.fillRect(x - 6, y - 6, w + 12, h + 12);
  k.ctx.fillStyle = '#0E1F2A'; k.ctx.fillRect(x, y, w, h);
  k.ctx.fillStyle = '#16323F'; for (let yy = y; yy < y + h; yy += 12) k.ctx.fillRect(x, yy, w, 3);
  k.ctx.fillStyle = TEAL; k.ctx.fillRect(x, y, 9, h);
  const tab = 'COPY THIS PROMPT', tw2 = k.measure(tab, {size: 39}) + 36;
  k.ctx.fillStyle = INK; k.ctx.fillRect(x + 24, y - 30, tw2 + 6, 48); k.ctx.fillStyle = GOLD; k.ctx.fillRect(x + 27, y - 27, tw2, 42);
  k.text(tab, x + 45, y - 21, {size: 39, color: INK});
  const per = 0.011, total = PROMPT.join('').length; let used = 0, lastX = x + pad + 18, lastY = y + pad;
  const shown = Math.floor((T - t0 - 0.15) / per);
  PROMPT.forEach((l, i) => {
    const c = clamp(shown - used, 0, l.length); used += l.length;
    const ly = y + pad + i * lh, red = o.red && o.red.includes(i) && T >= o.redAt;
    if (red) { k.ctx.fillStyle = '#5A1F24'; k.ctx.fillRect(x + 18, ly - 9, w - 36, lh - 6); }
    if (c > 0) { k.text(l.slice(0, c), x + pad + 18, ly, {size: 66, color: red ? '#FFB4A2' : CREAM}); lastX = x + pad + 18 + k.measure(l.slice(0, c), {size: 66}); lastY = ly; }
  });
  if (shown >= total && Math.floor(T * 2) % 2 === 0) { k.ctx.fillStyle = GOLD; k.ctx.fillRect(lastX + 9, lastY, 27, 60); }
  return {x, y, w, h};
};

window.SCENE = {
  look: 'arcade',
  images: ['gemini-app', 'gemini-free'],
  host_name: 'Snow',
  hud: 'QUOTE REPLY',
  sendLine: 'Send this to whoever answers your quote requests.',
  transitions: {usual: 'dissolve', guess: 'levelselect', fix: 'dissolve', check: 'dissolve', button: 'levelselect'},
  trauma: {'check.cut': 0.6},
  sections: {
    /* ---- hook: three shots. Cover (frame 0, no host): the bedroom, the phone on the nightstand glowing with the     */
    /* customer's text, 11 PM, the plate. By 0.8 s cut in close on the phone: the bubble big, EXAMPLE. On "reply"  */
    /* cut to the result: the real reply card with its label and the stopwatch 6.6 S (C5). "1 THING'S WRONG" stamps.   */
    hook: (k, T) => {
      const n = k.data.numbers;
      const tIn = Math.min(0.8, Math.max(0.4, wordT(k, 'hook', /^quote/i, 0.6))), tRes = Math.max(1.9, Math.min(2.6, wordT(k, 'hook', /^under/i, 2.3) - 0.25));
      const tWrong = k.S('hook.wrong');
      if (T >= tRes) {
        const d = bedroom(k, {top: 360});
        const c = replyCard(k, 72, 420, 870, {max: 6, float: tRes + 0.3});
        /* the stopwatch: 6.6 S counting up from the cut */
        const p = clamp((T - tRes) / 0.9), v = (n.secs.value * eo(p)).toFixed(1);
        d.win(14, 84, 332, 52, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: GOLD});
        k.text(`${v} S`, 540, 270, {size: 99, color: GOLD, align: 'center', drop: INK});
        if (T >= tWrong - 0.25) stampBox(k, "1 THING'S WRONG", 600, c.y + c.h + 24, tWrong - 0.25, {color: RED, size: 66});
        return host(k, T >= tWrong ? 'point' : null);
      }
      if (T >= tIn) {
        const d = bedroom(k, {top: 330, wide: true});
        const s = bigPhone(k, d, 40, 156, 280, 324, {glow: true});
        d.P(s.x, s.y, s.w, 30, '#2F6F67'); k.text(`${n.night.shown} PM`, (s.x + 8) * 3, (s.y + 4) * 3, {size: 39, color: CREAM, lint: false});
        const ls = k.wrap(CUSTOMER, {size: 66}, (s.w - 24) * 3);
        d.P(s.x + 8, s.y + 40, s.w - 16, ls.length * 28 + 14, CREAM); d.P(s.x + 8, s.y + 40, s.w - 16, 1, '#FFFFFF');
        ls.forEach((l, i) => k.text(l, (s.x + 14) * 3, (s.y + 46 + i * 28) * 3, {size: 66, color: INK}));
        tag(k, 'EXAMPLE', 860, (s.y + 46 + ls.length * 28 + 16) * 3, {align: 'right', color: ORANGE});
        hookPlate(k, d, n);
        return host(k);
      }
      const d = bedroom(k, {top: 318, wide: true});
      const s = bigPhone(k, d, 96, 182, 168, 144, {glow: true, screen: '#253048'});
      k.text(`${n.night.shown} PM`, 540, (s.y + 6) * 3, {size: 66, color: GOLD, align: 'center', drop: INK});
      d.P(s.x + 8, s.y + 34, s.w - 16, 62, CREAM); d.P(s.x + 8, s.y + 34, s.w - 16, 1, '#FFFFFF');
      ['Hi! Need a quote for', 'a move-out clean,', '2 bed 1 bath...'].forEach((l, i) => k.text(l, (s.x + 14) * 3, (s.y + 38 + i * 19) * 3, {size: 39, color: INK}));
      tag(k, 'EXAMPLE', (s.x + s.w - 8) * 3, (s.y + 104) * 3, {align: 'right', color: ORANGE});
      hookPlate(k, d, n);
      return {host: false, speech: false};
    },

    /* ---- usual: the flaps board, QUOTE BOARD (EXAMPLE). QUOTE IN 11 PM flips in, REPLY OUT 12 PM on "lunch" in red;   */
    /* our window types the usual reply on "Hey"; BOOKED ELSEWHERE stamps on "booked".                                    */
    usual: (k, T) => {
      const n = k.data.numbers, t0 = k.S('usual'), tLunch = wordT(k, 'usual', /^lunch/i, 1.2), tHey = k.S('usual.reply'), tLost = wordT(k, 'usual.lost', /^booked/i, 0.4);
      k.sets.flaps({title: 'QUOTE BOARD', cols: 12, rows: [{label: 'QUOTE IN', value: `${n.night.shown}PM`, at: t0 - 0.1}, {label: 'REPLY OUT', value: `${n.lunch.shown}PM`, at: tLunch - 0.25, hi: true}]});
      const d = px(k);
      tag(k, 'EXAMPLE', 930, 270, {align: 'right', color: ORANGE});
      if (T >= tHey - 0.25) {
        d.win(30, 196, 300, 76, {base: CREAM, hi: '#FFFFFF', lo: '#C9B79C', rule: '#3B82C4'});
        const s = 'Hey, prices vary, give me a call.', sh = Math.floor(clamp((T - (tHey - 0.25)) / 1.4) * s.length);
        k.wrap(s.slice(0, sh) || ' ', {size: 66}, 840).forEach((l, i) => k.text(l, 120, 618 + i * 84, {size: 66, color: INK}));
      }
      if (T >= tLost - 0.25) stampBox(k, 'BOOKED ELSEWHERE', 540, 860 + (T >= tLost + 0.3 ? bob2(T, tLost + 0.3) : 0), tLost - 0.25, {color: RED, size: 66});
      return host(k, T >= tLost ? 'shrug' : null);
    },

    /* ---- guess: the work order (the metaphor): QUOTE REPLY, two boxes, PRICE and QUESTION; EMPTY stamps on each word;  */
    /* "nothing to text back" lands. On "Jobber" the gauge: 26%, REPLY IN 1 HOUR, the source on screen while said.      */
    guess: (k, T) => {
      const n = k.data.numbers, t0 = k.S('guess'), tStake = k.S('guess.stake');
      if (T >= tStake) {
        const tTwenty = wordT(k, 'guess.stake', /^twenty/i, 1.0);
        k.sets.gauge({value: n.hourPct.value, max: 100, at: tTwenty - 0.25, dur: 1.0, zones: [[0, 40, RED], [40, 70, ORANGE], [70, 100, TEAL]], label: `CLEANING: REPLY IN ${n.hours.shown} HOUR`, suffix: '%'});
        tag(k, 'Source: Jobber, 2026 Home Service Trends', 540, 908 + (T >= tTwenty + 1.2 ? bob2(T, tTwenty + 1.2) / 2 : 0), {align: 'center'});
        tag(k, `Report, ${n.owners.shown} owners, Dec ${n.year.shown}`, 540, 958, {align: 'center'});
        return host(k, T >= tTwenty ? 'lean' : null);
      }
      const d = px(k), {P} = d;
      /* a clipboard on the wall: our work order */
      P(0, 0, 360, 417, '#2F4A55'); for (let y = 10; y < 417; y += 12) for (let x = 6 + ((y / 12) % 2) * 6; x < 360; x += 12) P(x, y, 2, 2, '#1E333B');
      P(0, 417, 360, 223, '#1B1420'); P(0, 417, 360, 2, '#3D2E45');
      const sl = d.ease(t0, 6, 30), X = 40, Y = 86 + sl, W = 280, H = 206;
      P(X + 4, Y + 4, W, H, INK); P(X - 1, Y, W + 2, H, INK); P(X, Y - 1, W, H + 2, INK); P(X, Y, W, H, '#FFF7EA');
      P(X + 110, Y - 8, 60, 14, '#9AA0AD'); P(X + 112, Y - 6, 56, 4, '#C9CCD3');
      for (let y = Y + 64; y < Y + H - 6; y += 16) P(X + 8, y, W - 16, 1, '#E6D3BC');
      k.text('WORK ORDER', (X + 14) * 3, (Y + 12) * 3, {size: 66, color: INK});
      k.text('Job: quote reply', (X + 14) * 3, (Y + 40) * 3, {size: 39, color: '#4A4E5A'});
      const tP = wordT(k, 'guess', /^price/i, 0.4), tQ = wordT(k, 'guess', /^question/i, 1.0), tN = wordT(k, 'guess', /^nothing/i, 1.6);
      [['PRICE', 96, tP], ['QUESTION', 156, tQ]].forEach(([lab, oy, ti]) => {
        P(X + 16, Y + oy, 30, 30, INK); P(X + 18, Y + oy + 2, 26, 26, '#FFFFFF');
        k.text(lab, (X + 56) * 3, (Y + oy + 4) * 3, {size: 66, color: INK});
        if (T >= ti - 0.25) stampBox(k, 'EMPTY', (X + 230) * 3, (Y + oy - 4) * 3, ti - 0.25, {color: RED, size: 39});
      });
      if (T >= tN - 0.25) k.slam('Nothing to text back.', 540, 912 + (T >= tN + 0.2 ? bob2(T, tN + 0.2) : 0), tN - 0.25, {size: 66, color: GOLD, align: 'center', from: 0.4, drop: INK, glint: false});
      return host(k, T >= tP ? 'point' : null);
    },

    /* ---- fix: a phone frame with Gemini's own start screen (shot Nov 1) and its address; the customer's text slides  */
    /* into the box. On "prompt" the ITEM GET card with the prompt word for word, held into check. On "free" the plan   */
    /* page shot ($0) cuts in beside it with its address.                                                              */
    fix: (k, T) => {
      const n = k.data.numbers, t0 = k.S('fix'), tPr = k.S('fix.prompt'), tFree = k.S('fix.free');
      const d = px(k), {P} = d;
      P(0, 0, 360, 417, '#253048'); for (let y = 0; y < 417; y += 4) P(0, y, 360, 1, '#1F2A40'); P(0, 417, 360, 223, '#1B1420'); P(0, 417, 360, 2, '#3D2E45');
      if (T < tPr - 0.25) {
        const s = bigPhone(k, d, 100, 112, 160, 214, {screen: '#F7F7F7'});
        k.page(s.x * 3, s.y * 3, s.w * 3, s.h * 3, 'gemini-app', {scroll: 398});
        /* their text pastes into the box */
        const q = clamp((T - (t0 + 0.4)) / 0.4);
        if (q > 0) { const sl = d.ease(t0 + 0.4, 6, 30), by = s.y + 92 + sl; d.P(s.x - 30, by, s.w + 60, 44, INK); d.P(s.x - 28, by + 2, s.w + 56, 40, CREAM);
          k.text('Their text, pasted in:', (s.x - 22) * 3, (by + 5) * 3, {size: 39, color: '#4A4E5A'}); k.text('Hi! Need a quote for a move-out', (s.x - 22) * 3, (by + 22) * 3, {size: 39, color: INK});
          tag(k, 'EXAMPLE', (s.x + s.w + 28) * 3, (by + 48) * 3, {align: 'right', color: ORANGE}); }
        tag(k, 'gemini.google.com, Nov 1, 2026', 540, 282, {align: 'center'});
        return host(k, 'point');
      }
      promptBox(k, tPr - 0.25);
      if (T >= tFree - 0.25) {
        k.slam(`Free: ${n.free.shown}/ month`, 560, 812 + (T >= tFree + 0.2 ? bob2(T, tFree + 0.2) : 0), tFree - 0.25, {size: 66, color: GOLD, align: 'center', from: 0.4, drop: INK, glint: false});
        tag(k, 'with a Google Account (Flash-Lite model)', 560, 894, {align: 'center'});
        tag(k, 'gemini.google/subscriptions, Nov 1', 560, 946, {align: 'center'});
      }
      return host(k, 'point');
    },

    /* ---- check: the reply card again, word for word, the two asks lit red with ?1 and ?2; 2 QUESTIONS stamps on     */
    /* "two"; on "Cut" the second ask greys and strikes; on "price" [your price] lights gold; a SEND button on         */
    /* "yourself"; Gemini's own line "Gemini is AI and can make mistakes." under it.                                    */
    check: (k, T) => {
      const n = k.data.numbers, t0 = k.S('check'), tTwo = wordT(k, 'check', /^two/i, 0.5), tOven = wordT(k, 'check', /^oven/i, 1.4), tDay = wordT(k, 'check', /^day/i, 2.4);
      const tCut = k.S('check.cut'), tPrice = wordT(k, 'check.cut', /^price/i, 1.0), tSelf = wordT(k, 'check.cut', /^yourself/i, 2.0);
      /* the prompt card stays up from fix (same window, no new slide) until "oven", so the save card holds 3 s or     */
      /* more and "It asked two questions" lands against its own line "Ask one question" (lit red)                     */
      if (T < tOven - 0.25) {
        const tPr = k.S('fix.prompt'), d = px(k), {P} = d;
        P(0, 0, 360, 417, '#253048'); for (let y = 0; y < 417; y += 4) P(0, y, 360, 1, '#1F2A40'); P(0, 417, 360, 223, '#1B1420'); P(0, 417, 360, 2, '#3D2E45');
        promptBox(k, tPr - 0.25, {red: [4, 5], redAt: tTwo - 0.25});
        if (T >= tTwo - 0.25) stampBox(k, `IT ASKED ${n.asked.shown}`, 600, 880, tTwo - 0.25, {color: RED, size: 66});
        return host(k, 'lean');
      }
      bedroom(k, {top: 300});
      const c = replyCard(k, 60, 300, 870, {hi: {1: ['#F9D7CC', tOven - 0.25], 2: ['#F9D7CC', tDay - 0.25]}, strike: [2], strikeAt: tCut, priceAt: tPrice - 0.25, extra: 0, float: tOven});
      if (T < tCut) stampBox(k, `${n.asked.shown} QUESTIONS`, 600, c.y + c.h + 24, tOven - 0.25, {color: RED, size: 66});
      if (T >= tCut) {
        k.slam(`Ask ${n.wanted.shown}. Add your price.`, 540, c.y + c.h + 36, tCut, {size: 66, color: GOLD, align: 'center', from: 0.4, drop: INK, glint: false});
        if (T >= tSelf - 0.25) { stampBox(k, 'SEND IT YOURSELF', 600, c.y + c.h + 110, tSelf - 0.25, {color: TEAL, size: 39}); }
      }
      return host(k, T >= tCut ? 'point' : (T >= tTwo ? 'lean' : null));
    },

    /* ---- button: the versus set: YOURS (price YES, question YES) against LUNCH (NO, NO), the work order's two boxes as */
    /* stats; QUEST COMPLETE stamps on the winner on "question" (the native move, M7); the rule lands in gold on "Send". */
    button: (k, T) => {
      const t0 = k.S('button'), tP = wordT(k, 'button', /^price/i, 1.2), tQ = wordT(k, 'button', /^question/i, 2.2), tRule = k.S('button.rule');
      const n = k.data.numbers;
      /* versus: the lunch reply against the fixed one, the two boxes of the work order as the stats (teal is the fix) */
      k.sets.versus({a: {name: 'YOURS', icon: 'phone', stats: [{label: 'PRICE', value: 1, max: 1, text: 'YES'}, {label: 'QUESTION', value: 1, max: 1, text: 'YES'}]},
        b: {name: 'LUNCH', icon: 'clock', stats: [{label: 'PRICE', value: 0, max: 1, text: 'NO'}, {label: 'QUESTION', value: 0, max: 1, text: 'NO'}]},
        at: t0 - 0.4, vsAt: t0 + 0.2, winner: 'a', winAt: tQ - 0.2, winText: 'QUEST COMPLETE'});
      if (T >= tRule - 0.25) {
        k.slam('Send it before', 540, 852, tRule - 0.25, {size: 66, color: CREAM, align: 'center', from: 0.4, drop: INK, glint: false});
        k.slam('your first job.', 540, 932, tRule - 0.15, {size: 66, color: GOLD, align: 'center', from: 0.4, drop: INK, glint: false});
      }
      return host(k, T >= tRule + 1.0 ? 'wave' : 'point');
    },
  },
};
