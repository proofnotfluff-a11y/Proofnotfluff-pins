/* Scene: The price list prompt (two-shops, AI lane, arcade; Nov 2, 2026). One function per top-level cue in           */
/* 03_cues/cues.md. Numbers only from k.data (brief.md -> data.js); every time from a cue start (k.S) or a word (wordT). */
/* The reply and the prompt are the exact text of video/studio/demos/out/2026-11-16-price-list-quote-1/run.json.       */
/* Worlds: hook = the reply card and our own living room with the stair railing; turn = slots; one = our own kitchen  */
/* table at night (the one room-and-panel section); two = street; why = inventory (the metaphor), then the reply card;*/
/* check = Gemini's plan page shot and the ITEM GET setup card; button = boss (FREE WORK). None used by three-fixes   */
/* (counter, chat, scores) or ai-night-quote (flaps, gauge, versus).                                                   */
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

/* a phone face (low-res units) with a glow; returns the screen box */
const bigPhone = (k, d, x, y, w, h, o = {}) => {
  const {P} = d;
  if (o.glow) { k.ctx.save(); k.ctx.globalAlpha = 0.18; P(x - 10, y - 10, w + 20, h + 20, '#87CEEB'); k.ctx.restore(); }
  P(x + 3, y + 3, w, h, INK); P(x - 1, y, w + 2, h, INK); P(x, y - 1, w, h + 2, INK);
  P(x, y, w, h, '#2B2033'); P(x + 1, y, w - 2, 1, '#4A4E5A');
  P(x + 4, y + 8, w - 8, h - 16, o.screen || '#F4E6D3'); P(x + Math.round(w / 2) - 6, y + 3, 12, 2, INK);
  return {x: x + 4, y: y + 8, w: w - 8, h: h - 16};
};
/* a tag on a dark chip (sources, addresses, EXAMPLE) */
const tag = (k, s, x, y, o = {}) => chipText(k, s, x, y, Object.assign({size: 39, color: SAND}, o));

/* ---- the run's own words (run.json, Nov 1, 2026): the reply without the stars, the ruler line and the warning sign ---- */
const QUOTE = ['Walls (Living Room): 1 room, [my price]', 'Ceiling (Living Room): 1 room, [my price]', 'Doors: 2, 2x [my price]', 'Drywall patch: 1 patch, [my price]'];
const FLAG = 'FLAGGED ITEM (Not on price list):';
const RAIL = 'Stair railing (painting): This item is not on your price list. A custom price is needed.';
const LABEL = ['REAL REPLY: GEMINI 3.8 FLASH (API)', 'NOV 1, 2026 (EXCERPT)'];
/* the prompt's rule line, word for word, and the setup the lesson teaches (facts.json setup.card) */
const STEPS = [['1. Type your price list in a phone note. Once.'], ['2. Put this prompt at the top.'], ['3. After each walkthrough, add your notes,', '    paste it all in the chat.'], ['4. Price the flags. Check every line.', '    Then send.']];
const RULE = ['Turn my walkthrough notes into', 'quote lines.', 'Use only my price list.', 'Flag anything that is not on it.', 'Never guess a price.'];

/* the reply card: cream, the label on a teal band, the four quote lines, then the flag and the railing line. */
/* o.lit (time) lights the railing rows red; o.float bobs it; returns the railing rows' top y and the card box.   */
const replyCard = (k, x, y, w, o = {}) => {
  const lh = 48, pad = 27, rows = [];
  QUOTE.forEach((l) => k.wrap(l, {size: 39}, w - 2 * pad).forEach((r) => rows.push([r, 0])));
  rows.push([FLAG, 1]);
  k.wrap(RAIL, {size: 39}, w - 2 * pad).forEach((r) => rows.push([r, 2]));
  const h = 120 + rows.length * lh + 24, fl = o.float != null ? bob2(k.T, o.float) / 2 : 0;
  k.ctx.fillStyle = INK; k.ctx.fillRect(x + 9, y + 9 + fl, w, h); k.ctx.fillRect(x - 3, y - 3 + fl, w + 6, h + 6);
  k.ctx.fillStyle = CREAM; k.ctx.fillRect(x, y + fl, w, h);
  k.ctx.fillStyle = '#2F6F67'; k.ctx.fillRect(x, y + fl, w, 102);
  k.text(LABEL[0], x + 24, y + 12 + fl, {size: 39, color: CREAM}); k.text(LABEL[1], x + 24, y + 54 + fl, {size: 39, color: GOLD});
  let railY = null;
  rows.forEach(([l, kind], i) => {
    const ly = y + 120 + i * lh + fl, lit = kind > 0 && o.lit != null && k.T >= o.lit;
    if (lit) { k.ctx.fillStyle = kind === 1 ? '#E2633B' : '#F9D7CC'; k.ctx.fillRect(x + 12, ly - 6, w - 24, lh - 2); }
    if (kind === 2 && railY == null) railY = ly;
    k.text(l, x + pad, ly, {size: 39, color: lit && kind === 1 ? CREAM : (kind === 0 && o.dim ? '#6E5B4F' : INK)});
  });
  return {x, y: y + fl, w, h, railY};
};
/* the plate for the cover and the cuts (5 to 8 words, C1) */
const hookPlate = (k) => {
  k.text('Make AI flag', 540, 276, {size: 66, color: CREAM, align: 'center', drop: INK});
  k.text('what you never priced.', 540, 352, {size: 66, color: GOLD, align: 'center', drop: INK});
};
/* a room change that travels (M4): 8 frames of vertical blinds in ink closing over the new room from the left */
const blinds = (k, t0) => { const f = Math.floor((k.T - t0) * 30 + 0.005); if (f < 0 || f >= 8) return; k.ctx.fillStyle = INK; for (let x = 0; x < 1080; x += 72) k.ctx.fillRect(x, 0, Math.round(72 * (1 - f / 8) / 3) * 3, 1920); };
/* our living room with the stair: a wall, a window, the stairs rising right with a white railing (EXAMPLE) */
const livingRoom = (k, o = {}) => {
  const d = px(k), {P, dith, line} = d;
  P(0, 0, 360, 417, '#6B5A7A'); for (let x = 0; x < 360; x += 18) P(x, 0, 1, 417, '#5E4E6D');
  P(24, 60, 90, 110, '#3D2E45'); P(28, 64, 82, 102, '#87CEEB'); dith(28, 130, 82, 36, '#6FB7A8'); P(68, 64, 2, 102, '#3D2E45'); P(28, 114, 82, 2, '#3D2E45');
  /* the stairs: steps up to the right */
  for (let i = 0; i < 9; i++) { const sx = 150 + i * 22, sy = 400 - i * 30; P(sx, sy, 360 - sx, 30, i % 2 ? '#8C5A33' : '#7A4E2C'); P(sx, sy, 360 - sx, 3, '#B07A47'); }
  /* the railing: posts and a rail, bright white (the unpriced job) */
  const c = o.railC || '#FFFFFF';
  line(150, 330, 344, 66, INK, 5); line(150, 326, 344, 62, c, 4);
  for (let i = 0; i < 9; i++) { const sx = 158 + i * 22, sy = 398 - i * 30; P(sx - 1, sy - 72, 6, 72, INK); P(sx, sy - 70, 4, 70, c); }
  P(0, 417, 360, 223, '#3D2717'); for (let x = 0; x < 360; x += 30) P(x, 417, 1, 223, '#2B1C10'); P(0, 417, 360, 2, '#5A3720');
  return d;
};
/* a price tag on a string, swinging a step every 4 frames */
const priceTag = (k, d, x, y, s, t0) => {
  const sw = [0, 2, 3, 2, 0, -2, -3, -2][Math.floor(Math.max(0, k.T - t0) * 7.5) % 8];
  d.line(x, y, x + sw, y + 20, INK, 1);
  const tx0 = x + sw - 40, ty0 = y + 20;
  d.P(tx0 - 2, ty0 - 2, 84, 60, INK); d.P(tx0, ty0, 80, 56, GOLD); d.P(tx0 + 5, ty0 + 5, 5, 5, INK);
  k.text(s, (tx0 + 44) * 3, (ty0 + 6) * 3, {size: 132, color: INK, align: 'center'});
};

window.SCENE = {
  look: 'arcade',
  images: ['gemini-free'],
  host_name: 'Snow',
  hud: 'PRICE LIST',
  sendLine: 'Send this to your painter who still quotes from memory.',
  transitions: {turn: 'mosaic', one: 'levelselect', two: 'dissolve', why: 'levelselect', check: 'dissolve', button: 'gameover'},
  trauma: {'one.free': 0.6},
  sections: {
    /* ---- hook: three shots. Cover (frame 0, no host): the real reply card, the railing lit red, the plate. On       */
    /* "railing" cut in close on the flagged line. On "painted" cut to our living room: the white stair railing and a  */
    /* $0 tag swinging, PAINTED FOR FREE?. On "Gemini" back to the card: FLAGGED stamps, NO PRICE GUESSED.             */
    hook: (k, T) => {
      const n = k.data.numbers;
      const tClose = Math.min(0.8, Math.max(0.45, wordT(k, 'hook', /^railing/i, 0.6))), tRoom = Math.min(2.4, wordT(k, 'hook', /^painted/i, 1.6) - 0.1);
      const tFlag = k.S('hook.flag');
      if (T >= tFlag - 0.25) {
        const d = px(k); d.P(0, 0, 360, 640, '#1B1420'); for (let y = 0; y < 640; y += 6) d.P(0, y, 360, 1, '#1F1726');
        const c = replyCard(k, 60, 270, 900, {lit: 0, dim: true, float: tFlag + 0.3});
        stampBox(k, 'FLAGGED', 540, c.y + c.h + 18, tFlag - 0.25, {color: RED, size: 66});
        const tG = wordT(k, 'hook.flag', /^guessing/i, 1.4) - 0.25;
        if (T >= tG) k.slam('NO PRICE GUESSED', 540, c.y + c.h + 136, tG, {size: 66, color: GOLD, align: 'center', from: 0.4, drop: INK, glint: false});
        blinds(k, tFlag - 0.25);
        return host(k, 'point');
      }
      const room = (cover) => {
        const d = livingRoom(k);
        priceTag(k, d, 250, 150, n.railing.shown, cover ? 0 : tRoom);
        k.ctx.fillStyle = INK; k.ctx.fillRect(0, 258, 1080, cover ? 186 : 114); k.ctx.fillStyle = '#1B1420'; k.ctx.fillRect(0, 264, 1080, cover ? 174 : 102);
        tag(k, 'EXAMPLE', 920, cover ? 470 : 396, {align: 'right', color: ORANGE, size: 66});
        return d;
      };
      if (T >= tRoom) {
        room(false);
        k.slam('PAINTED FOR FREE?', 480, 282, tRoom + 0.1, {size: 66, color: GOLD, align: 'center', from: 0.4, drop: INK, glint: false});
        blinds(k, tRoom);
        return host(k, 'shrug');
      }
      if (T >= tClose) {
        const d = px(k); d.P(0, 0, 360, 640, '#1B1420'); for (let y = 0; y < 640; y += 6) d.P(0, y, 360, 1, '#1F1726');
        /* the close-up: the result, the flagged line big on the cream card */
        const x = 60, y = 450, w = 870, ls = k.wrap(RAIL, {size: 66}, w - 60);
        k.ctx.fillStyle = INK; k.ctx.fillRect(x - 6, y - 6, w + 12, 130 + ls.length * 84); k.ctx.fillStyle = CREAM; k.ctx.fillRect(x, y, w, 118 + ls.length * 84);
        k.ctx.fillStyle = RED; k.ctx.fillRect(x, y, w, 96); k.text(FLAG, x + 24, y + 30, {size: 39, color: CREAM});
        /* never frozen (M1): a red marker sweeps under each line in turn while it is read, whole pixels */
        const sp = clamp((T - tClose) / Math.max(0.6, tRoom - tClose - 0.1)) * ls.length;
        ls.forEach((l, i) => { const lw = k.measure(l, {size: 66}), q = clamp(sp - i); if (q > 0) { k.ctx.fillStyle = RED; k.ctx.fillRect(x + 30, y + 120 + i * 84 + 66, Math.round(lw * q / 3) * 3, 9); } });
        ls.forEach((l, i) => k.text(l, x + 30, y + 120 + i * 84, {size: 66, color: INK}));
        tag(k, LABEL[0], 495, y + 150 + ls.length * 84, {align: 'center'}); tag(k, LABEL[1], 495, y + 200 + ls.length * 84, {align: 'center'});
        hookPlate(k);
        return host(k, 'point');
      }
      /* the cover (frame 0, no host): the stake object, our railing with its $0 tag, under the plate */
      room(true);
      hookPlate(k);
      return {host: false, speech: false};
    },

    /* ---- turn: the slot machine, AI PRICES: the reels spin and stop on ? ? ? on "up" (made up). On "This time" the     */
    /* crown reads YOUR LIST and STUCK TO YOUR LIST stamps; on "So" the loop: what happens to the railing?              */
    turn: (k, T) => {
      const t0 = k.S('turn'), tUp = wordT(k, 'turn', /^up/i, 1.6), tList = k.S('turn.list'), tLoop = k.S('turn.loop');
      k.sets.slots({t0: t0 + 0.1, stops: [tUp - 0.5, tUp - 0.25, tUp], symbols: ['?', '?', '?'], label: T >= tList ? 'YOUR LIST' : 'AI PRICES', win: false, idle: ['$', '?', '$']});
      if (T < tList) { if (T >= tUp) k.slam('MADE UP?', 510, 760, tUp, {size: 66, color: RED, align: 'center', from: 0.4, drop: INK, glint: false}); }
      else if (T < tLoop) stampBox(k, 'STUCK TO YOUR LIST', 510, 738 + (T >= tList + 0.3 ? bob2(T, tList + 0.3) : 0), tList - 0.1, {color: TEAL, size: 66});
      else {
        k.ctx.fillStyle = INK; k.ctx.fillRect(84, 714, 852, 174); k.ctx.fillStyle = '#1B1420'; k.ctx.fillRect(90, 720, 840, 162);
        k.slam('What happens to', 510, 732, tLoop - 0.1, {size: 66, color: CREAM, align: 'center', from: 0.4, drop: INK, glint: false});
        k.slam('the railing?', 510, 812, tLoop + 0.05, {size: 66, color: GOLD, align: 'center', from: 0.4, drop: INK, glint: false});
      }
      return host(k, T >= tList ? 'point' : 'lean');
    },

    /* ---- one: painter one's kitchen table at night (EXAMPLE), the clock 10 PM, a laptop; the quote types from memory  */
    /* (Walls, Ceiling, Doors, Patch), a line on each word; no railing. FREE WORK stamps on "free".                      */
    one: (k, T) => {
      const n = k.data.numbers, t0 = k.S('one'), tTen = wordT(k, 'one', /^ten/i, 3.6), tMem = wordT(k, 'one', /^memory/i, 4.5), tNever = wordT(k, 'one', /^never/i, 5.9), tFree = k.S('one.free');
      const d = px(k), {P, dith, disc} = d;
      P(0, 0, 360, 417, '#253048'); for (let y = 0; y < 417; y += 6) P(0, y, 360, 1, '#202A40');
      /* the clock on the wall, the hand stepping */
      disc(300, 108, 18, INK); disc(300, 108, 16, CREAM); d.line(300, 108, 300, 96, INK, 2); d.line(300, 108, 290 + (Math.floor(T * 2) % 2), 112, INK, 2);
      k.text(`${n.late.shown} PM`, 750, 300, {size: 66, color: GOLD, align: 'center', drop: INK});
      tag(k, 'PAINTER ONE: EXAMPLE', 60, 300, {color: ORANGE, size: 66});
      /* the table and the laptop with its quote */
      P(0, 330, 360, 10, '#8C5A33'); P(0, 330, 360, 2, '#B07A47'); P(0, 340, 360, 77, '#5A3720');
      const X = 30, Y = 120, W = 300, H = 200;
      P(X - 2, Y - 2, W + 4, H + 4, INK); P(X, Y, W, H, '#3D2E45'); P(X + 6, Y + 6, W - 12, H - 12, CREAM); P(X - 20, Y + H + 2, W + 40, 8, '#9AA0AD'); P(X - 20, Y + H + 2, W + 40, 1, '#C9CCD3');
      k.text('QUOTE', (X + 14) * 3, (Y + 12) * 3, {size: 66, color: INK}); for (let i = 0; i < 5; i++) P(X + 14, Y + 66 + i * 30, W - 28, 1, '#E6D3BC');
      const lines = ['Walls', 'Ceiling', 'Doors', 'Patch'], at = [t0 + 0.1, t0 + 1.0, tTen - 0.2, tMem - 0.25];
      lines.forEach((l, i) => { if (T >= at[i]) { const sh = Math.floor(clamp((T - at[i]) / 0.3) * l.length); k.text(l.slice(0, Math.max(1, sh)), (X + 16) * 3, (Y + 44 + i * 30) * 3, {size: 66, color: INK}); } });
      if (T >= tNever - 0.25 && T < tFree - 0.25) { k.slam('NO RAILING', 540, 840, tNever - 0.25, {size: 66, color: RED, align: 'center', from: 0.4, drop: INK, glint: false}); }
      if (T >= tFree - 0.25) stampBox(k, 'FREE WORK', 540, 846 + (T >= tFree + 0.3 ? bob2(T, tFree + 0.3) : 0), tFree - 0.25, {color: RED, size: 132});
      dith(0, 417, 360, 4, '#2B2033');
      return host(k, T >= tFree ? 'shrug' : (T >= tNever ? 'lean' : null));
    },

    /* ---- two: the street. Painter two's van drives and parks on "driveway"; the phone note in the sky: MY PRICES, the */
    /* four items, each [my price]. On "pastes" the prompt slides on top and NOTES under it; PASTE INTO GEMINI.         */
    two: (k, T) => {
      const t0 = k.S('two'), tDrive = wordT(k, 'two', /^driveway/i, 3.2), tPaste = k.S('two.paste'), tGem = wordT(k, 'two.paste', /^gemini/i, 2.9);
      k.sets.street({t0: t0 - 0.2, speed: 1, stopAt: tDrive - 0.6, stopDur: 0.8, sign: 'JOB 2'});
      tag(k, 'PAINTER TWO', 60, 282, {color: ORANGE, size: 66}); tag(k, 'EXAMPLE', 60, 366, {color: ORANGE, size: 66});
      /* the phone note, top right */
      const x = 588, y = 300 + (T >= t0 + 0.6 ? bob2(T, t0 + 0.6) : 0), w = 420, d = px(k);
      const items = T < tPaste ? ['MY PRICES', 'Walls [my price]', 'Ceiling [my price]', 'Door [my price]', 'Patch [my price]'] : ['+ THIS PROMPT', `MY PRICES (${k.data.numbers.items.shown})`, '+ MY NOTES:', 'walls, ceiling,', '2 doors, patch,', 'stair railing'];
      if (T >= tGem - 0.3) items.push('PASTE IN GEMINI');
      const h = 40 + items.length * 54;
      k.ctx.fillStyle = INK; k.ctx.fillRect(x - 9, y - 9, w + 18, h + 18); k.ctx.fillStyle = '#F4E6D3'; k.ctx.fillRect(x, y, w, h);
      items.forEach((l, i) => { if (l === 'PASTE IN GEMINI') { k.ctx.fillStyle = GOLD; k.ctx.fillRect(x + 6, y + 12 + i * 54, w - 12, 50); } k.text(l, x + 18, y + 20 + i * 54, {size: 39, color: i === 0 || l.startsWith('+') ? '#2F6F67' : INK}); });
      return host(k, T >= tPaste ? 'point' : null);
    },

    /* ---- why: the tool belt (the metaphor): MY PRICE LIST, four items; the cursor steps through them on the words;   */
    /* footer USE ONLY MY LIST. On "The railing's" a mosaic into the real reply card: the flag and the railing lit red;  */
    /* FLAGGED stamps on "flagged".                                                                                     */
    why: (k, T) => {
      const t0 = k.S('why'), tOnly = wordT(k, 'why', /^only/i, 1.2), tFl = k.S('why.flag'), tFlagged = wordT(k, 'why.flag', /^flagged/i, 2.9);
      if (T < tFl) {
        const it = (name, icon) => ({icon, name, stats: [{label: 'PRICE', value: 1, max: 1, text: 'MINE'}]});
        k.sets.inventory({title: 'MY PRICE LIST', slots: 8, items: [it('WALLS', 'hammer'), it('CEILING', 'hammer'), it('DOOR', 'wrench'), it('PATCH', 'clip')],
          select: [{slot: 0, at: t0 + 0.2}, {slot: 1, at: t0 + 0.8}, {slot: 2, at: tOnly - 0.2}, {slot: 3, at: tOnly + 0.4}], footer: ''});
        k.slam('USE ONLY MY LIST', 96, 642, t0 + 0.3, {size: 66, color: TEAL, from: 0.4, drop: INK, glint: false});
        return host(k, 'point');
      }
      const d = px(k); d.P(0, 0, 360, 640, '#1B1420'); for (let y = 0; y < 640; y += 6) d.P(0, y, 360, 1, '#1F1726');
      const c = replyCard(k, 60, 270, 960, {lit: tFl, float: tFl + 0.4});
      blinds(k, tFl);
      if (T >= tFlagged - 0.25) stampBox(k, 'FLAGGED', 540, c.y + c.h + 24, tFlagged - 0.25, {color: RED, size: 66});
      return host(k, T >= tFlagged ? 'point' : 'lean');
    },

    /* ---- check: Gemini's own plan page (shot Nov 1) with its address: Free, $0. On "railing" the setup card slides in */
    /* (ITEM GET, SETUP: 4 STEPS), held to the end of the section, the hand stepping down; step 4 lights gold on "He".   */
    check: (k, T) => {
      const t0 = k.S('check'), tCard = wordT(k, 'check', /^and$/i, 1.3) - 0.25, tYou = k.S('check.you');
      const d = px(k), {P} = d;
      P(0, 0, 360, 640, '#253048'); for (let y = 0; y < 640; y += 4) P(0, y, 360, 1, '#1F2A40');
      if (T < tCard) {
        const x = 90, y = 330, w = 900, h = Math.round(w * 650 / 1180);
        k.ctx.fillStyle = INK; k.ctx.fillRect(x - 9, y - 9, w + 18, h + 18);
        k.page(x, y, w, h, 'gemini-free', {scroll: 0});
        tag(k, "Gemini's plan: gemini.google/subscriptions", 500, y + h + 30, {align: 'center'}); tag(k, 'read Nov 1, 2026', 540, y + h + 80, {align: 'center'});
        return host(k, 'point');
      }
      const lines = [];
      STEPS.forEach((s, i) => { s.forEach((l) => lines.push(i === 3 && T >= tYou - 0.25 ? [l, '#B5522A'] : l)); if (i === 1) RULE.forEach((l) => lines.push(['    ' + l, '#2F6F67'])); });
      k.itemGet({at: tCard, lines, size: 39, lh: 52, pad: 36, x: 96, y: 300, w: 900, title: `SETUP: ${k.data.numbers.steps.shown} STEPS`, tag: 'COPY THIS', step: 0.9});
      return host(k, T >= tYou ? 'point' : 'talk');
    },

    /* ---- button: the boss FREE WORK (the native move, M7): hits on "list" (MY LIST), "job" (QUOTE LINES), "price"     */
    /* (I PRICE IT); it breaks on "railing" and PAID stamps.                                                            */
    button: (k, T) => {
      const tL = wordT(k, 'button', /^list/i, 0.3), tJ = wordT(k, 'button', /^job/i, 1.1), tP = wordT(k, 'button', /^price$/i, 2.2), tR = wordT(k, 'button', /^railing/i, 2.8);
      k.sets.boss({name: 'FREE WORK', hp: 100, t0: k.S('button') - 0.3, menu: 'MOVES', hits: [{at: tL - 0.1, dmg: 50, label: 'MY LIST'}, {at: tP - 0.1, dmg: 50, label: 'I PRICE IT'}], defeatAt: tR, winText: 'PAID'});
      return host(k, T >= tR + 0.6 ? 'wave' : 'point');
    },
  },
};
