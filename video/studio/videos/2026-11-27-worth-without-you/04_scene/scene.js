/* Scene: Worth without you (proven, our own version of research/PROVEN.md row 19; Nov 8, 2026). One function per top-   */
/* level cue in 03_cues/cues.md; every time from a cue start or a spoken word (wordT). Worlds: hook = the cover board,   */
/* then the storefront counter (the price tag flips from $1,000,000 to $500,000) with the buyer; ask = the buyer's office (k.client in the homeowner look so she reads as "she", facing the viewer as if the viewer is the seller; her words in        */
/* bubbles, EXAMPLE); ask = her three questions, a tally on the wall; turn = the tool belt (inventory), WHO RUNS THE SHOP;      */
/* send = the how-we-do-it card, held still; receipt = the ACHR News line, then the 2.73x gauge (data.js); button = the  */
/* office again, her question, the stamp. The million, the half and her questions are ours (EXAMPLE).                   */
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', DTEAL = '#2F6F67', GREY = '#9AA0AD', NIGHT = '#1B1420', SLATE = '#4A4E5A', WINE = '#7A3442';
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eo = (x) => 1 - Math.pow(1 - clamp(x), 3);

/* ---- the pixel kit (low-res units: 360 x 640, one pixel = 3 frame units), as in the lessons before ---- */
const px = (k) => {
  const ctx = k.ctx, T = k.T, F = Math.floor(T * 30 + 0.005);
  const P = (x, y, w, h, c) => { x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h); if (w > 0 && h > 0 && c) { ctx.fillStyle = c; ctx.fillRect(x * 3, y * 3, w * 3, h * 3); } };
  const fr = (t0) => Math.floor((T - t0) * 30 + 0.005);
  const ease = (t0, frames, dist) => Math.round(dist * (1 - eo(fr(t0) / frames)));
  return {P, fr, ease, F, T};
};
const WS = () => (window.WORDS && window.WORDS.words) || [];
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
const host = (k, pose, sc = 0.55) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: sc, hostX: 150});
const stampBox = (k, s, cx, y, t0, o = {}) => {
  const size = o.size || 66, c = o.color || GOLD, w = Math.round((k.measure(s, {size}) + 54) / 6) * 6, h = size + 36, x = Math.round((cx - w / 2) / 3) * 3;
  k.stampIn(t0, () => {
    k.shape(k.rectPts(x + 6, y + 6, w, h, 0), {fill: INK, line: false}); k.shape(k.rectPts(x, y, w, h, 0), {fill: o.bg || NIGHT, line: false});
    k.shape(k.rectPts(x + 6, y + 6, w - 12, 6, 0), {fill: c, line: false}); k.shape(k.rectPts(x + 6, y + h - 12, w - 12, 6, 0), {fill: c, line: false});
    k.text(s, x + w / 2, y + 18, {size, color: c, align: 'center'});
  }, {at: [x + w / 2, y + h], freeze: o.freeze});
};

/* the buyer's office: a wall with a slow ceiling-fan shadow sweeping (so the room never sits flat), the desk in front */
const office = (k, d) => {
  const {P, F} = d;
  P(0, 0, 360, 417, '#3D3346'); for (let y = 0; y < 270; y += 18) P(0, y, 360, 1, '#463B50');
  const sw = (F * 2) % 420 - 60; P(Math.max(0, sw), 0, 30, 270, '#43394D');
  P(0, 230, 360, 6, INK); P(0, 236, 360, 40, '#6B4226'); P(0, 236, 360, 3, '#8C5A33');
};
/* the price sign on the wall: ASKING $1,000,000; struck in red from tStrike, OFFER: HALF under it */
const priceSign = (k, d, tStrike) => {
  const {P} = d;
  P(18, 92, 196, 66, INK); P(20, 94, 192, 62, CREAM); P(20, 94, 192, 14, DTEAL);
  k.text('ASKING', 72, 284, {size: 52, color: INK});
  k.text('$1,000,000', 72, 362, {size: 66, color: INK});
  if (tStrike != null && k.T >= tStrike) {
    const n = Math.min(184, d.fr(tStrike) * 30); P(24, 136, n, 4, RED);
    if (d.fr(tStrike) >= 4) { P(18, 162, 150, 22, INK); P(20, 164, 146, 18, RED); k.text('OFFER: HALF', 72, 494, {size: 52, color: CREAM}); }
  }
};
/* her bubble: a cream box with a tail toward her head, left of her, text wrapped to fit inside x 72 to 650 */
const bubble = (k, d, s, t0, y = 196) => {
  if (k.T < t0) return;
  const up = d.ease(t0, 4, 6), f = k.fit(s, 66, 560, 52), lh = f.size * 1.15, h = Math.ceil((f.lines.length * lh + 40) / 3) * 3, Y = y * 3 + up * 3;
  k.shape(k.rectPts(60, Y + 6, 618, h, 0), {fill: INK, line: false});
  k.shape(k.rectPts(54, Y, 618, h, 0), {fill: CREAM, line: false});
  k.shape(k.rectPts(660, Y + h - 42, 36, 24, 0), {fill: CREAM, line: false});
  f.lines.forEach((ln, i) => k.text(ln, 78, Y + 20 + i * lh, {size: f.size, color: INK}));
};
/* the tally on the wall: three boxes, each marked YOU in turn */
const tally = (k, d, at) => {
  const {P} = d;
  for (let i = 0; i < 3; i++) {
    const x = 20 + i * 66, y = 166, on = k.T >= at[i];
    P(x, y, 58, 26, INK); P(x + 2, y + 2, 54, 22, on ? GOLD : '#2B2033');
    k.text(on ? 'YOU' : String(i + 1), (x + 29) * 3, (y + 5) * 3, {size: 52, color: on ? INK : GREY, align: 'center'});
  }
};
const drift = (k) => { const d = px(k), off = Math.floor(k.T * 30) % 16; for (let y = 418 - 16 + off; y < 640; y += 16) { const y0 = Math.max(418, y), y1 = Math.min(640, y + 8); if (y1 > y0) d.P(0, y0, 360, y1 - y0, '#2B2033'); } };

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'WORTH WITHOUT YOU',
  sendLine: 'Send this to your office manager this week.',
  transitions: {ask: 'dissolve', turn: 'levelselect', send: 'mosaic', receipt: 'fade4', button: 'gameover'},
  trauma: {},
  sections: {
    /* ---- hook: frame 0 is the cover board; at 0.6 s a blinds cut to the office, the buyer faces the viewer; on "half" */
    /* her bubble and the strike on the price sign ---- */
    hook: (k, T) => {
      const d = px(k), tShop = 0.6, tMil = wordT(k, 'hook', /^million/i, 1.0) - 0.3, tHalf = wordT(k, 'hook', /^half/i, 2.6) - 0.25;
      if (T < tShop) {
        office(k, d);
        k.coverBoard({hero: 'HALF?', lines: ['YOU ASK A MILLION.', 'SHE OFFERS HALF.'], example: true});
        k.cut(tShop, {kind: 'blinds'});
        return host(k, 'point');
      }
      const r = k.sets.counter({shop: 'YOUR SHOP', item: 'toolbox', tags: [{price: '$1,000,000', at: -1}, {price: '$500,000', at: tHalf}]});
      const a = r && r.area;
      if (a) { k.text('ASKING', a.x + 24, a.y + 18, {size: 52, color: CREAM}); if (T >= tHalf) k.text('OFFER: HALF', a.x + 24, a.y + 90, {size: 52, color: GOLD}); }
      k.client(500, 830, {role: 'homeowner', pose: T >= tHalf ? 'talk' : 'stand', mood: 'smug', scale: 0.8, talk: T >= tHalf && T < tHalf + 1.0});
      k.exampleTag(72, 640);
      k.cut(tShop, {kind: 'blinds'});
      return host(k, T >= tHalf ? 'shrug' : null);
    },

    /* ---- ask: her three questions, one bubble each; the tally marks YOU on each ---- */
    ask: (k, T) => {
      const d = px(k), q = [wordT(k, 'ask', /^who$/i, 2.0), 0, 0];
      const whos = WS().filter((w) => w.start >= k.S('ask') - 0.05 && /^who$/i.test(w.w)).map((w) => w.start);
      for (let i = 0; i < 3; i++) q[i] = (whos[i] != null ? whos[i] : k.S('ask') + 2 + i * 1.4) - 0.25;
      office(k, d); priceSign(k, d, null);
      tally(k, d, q.map((t) => t + 0.6));
      k.client(780, 810, {role: 'homeowner', pose: 'argue', mood: 'calm', scale: 0.95, talk: true});
      const lines = ['WHO ANSWERS THE PHONE?', 'WHO PRICES THE JOBS?', 'WHO DO YOUR CUSTOMERS CALL?'];
      let i = -1; q.forEach((t, j) => { if (T >= t) i = j; });
      if (i >= 0) bubble(k, d, lines[i], q[i], 210);
      k.exampleTag(930, 252, {right: true});
      return host(k, i >= 2 ? 'shrug' : null);
    },

    /* ---- turn: the departures board, LEAVING WITH YOU; the stamp on "leaves"; the rows flash on "walks" ---- */
    turn: (k, T) => {
      const t0 = k.S('turn'), w = (re, dd) => wordT(k, 'turn', re, dd) - 0.25;
      const tBuy = w(/^buying/i, 3.8), tWalk = w(/^walks/i, 9.5);
      const need = [{label: 'NEEDS YOU', value: 100, max: 100, text: ' '}];
      k.sets.inventory({title: 'WHO RUNS THE SHOP', items: [
        {icon: 'phone', name: 'PHONES', stats: need}, {icon: 'coin', name: 'PRICING', stats: need},
        {icon: 'star', name: 'CUSTOMERS', stats: need}, {icon: 'clip', name: 'BOOKING', stats: need}],
        select: [{slot: 0, at: t0 + 0.2}, {slot: 1, at: t0 + 0.9}, {slot: 2, at: t0 + 1.6}, {slot: 3, at: tWalk}], hint: 'WHO DOES IT?'});
      if (T >= tBuy) stampBox(k, "SHE ISN'T BUYING YOU", 540, 600, tBuy, {color: GOLD, bg: WINE, size: 60, freeze: 4});
      return host(k, T >= tBuy ? 'point' : null);
    },

    /* ---- send: the card goes up whole, then holds dead still; each step's number lights on its words ---- */
    send: (k, T) => {
      const t0 = k.S('send'), d = px(k), w = (re, dd) => wordT(k, 'send', re, dd) - 0.2;
      const at = [w(/^answer/i, 4.0), w(/^price/i, 4.8), w(/^book/i, 5.5), w(/^send/i, 6.2)];
      d.P(0, 0, 360, 417, '#2B3A4E'); { const so = d.F % 20; for (let x = so - 20; x < 360; x += 20) d.P(Math.max(0, x), 0, Math.max(0, Math.min(x + 10, 360) - Math.max(0, x)), 417, '#34465C'); }   /* check flat: the stripes behind the card drift, the card never moves */
      const c = k.sendCard({at: t0, who: 'FOR YOUR OFFICE MANAGER', title: 'HOW WE DO IT', body: 'ONE PAGE EACH',
        steps: ['ANSWER A CALL', 'PRICE A JOB', 'BOOK THE WORK', 'SEND THE BILL'], stepOn: at.map((a) => T >= a), example: true});
      return host(k, c ? 'point' : null);
    },

    /* ---- receipt: the ACHR News line on a card; on "two" a fade to the 2.73x gauge (data.js); the plate on "leave" ---- */
    receipt: (k, T) => {
      const t0 = k.S('receipt'), d = px(k), n = k.data.numbers.multiple, tTwo = wordT(k, 'receipt', /^two$/i, 5.0) - 0.3;
      if (T < tTwo) {
        d.P(0, 0, 360, 417, '#253048'); for (let y = (d.F >> 2) % 8 - 8; y < 417; y += 8) d.P(0, Math.max(0, y), 360, 3, NIGHT);
        const up = d.ease(t0, 6, 30);
        k.shape(k.rectPts(54, 264 + up * 3, 984, 560, 0), {fill: INK, line: false}); k.shape(k.rectPts(42, 252 + up * 3, 984, 560, 0), {fill: CREAM, line: false});
        k.shape(k.rectPts(42, 252 + up * 3, 984, 84, 0), {fill: WINE, line: false});
        k.text('THE ACHR NEWS', 72, 270 + up * 3, {size: 52, color: CREAM});
        ['"In Florida, HVAC businesses', 'are selling for ' + n.shown, 'annual earnings."'].forEach((s, i) => k.text(s, 72, 360 + i * 70 + up * 3, {size: 60, color: INK}));
        k.sourceTag('The ACHR News, Mar 20, 2026, on a 2025 Florida exit report. Read Nov 8, 2026.', 72, 590 + up * 3, {color: SLATE});
        return host(k);
      }
      k.sets.gauge({value: n.value != null ? n.value : 2.73, max: 4, at: tTwo + 0.1, dur: 1, zones: [[0, 2, '#4A4E5A'], [2, 4, '#F2A541']], label: 'TIMES A YEAR OF OWNER EARNINGS', prefix: '', suffix: 'x', dec: 2});
      k.cut(tTwo, {kind: 'fade4'});
      return host(k, 'point');
    },

    /* ---- button: the office again; her question; the stamp on "what" ---- */
    button: (k, T) => {
      const d = px(k), tAsk = wordT(k, 'button', /^asks/i, 2.0) - 0.25, tWhat = wordT(k, 'button', /^what$/i, 3.6) - 0.25;
      office(k, d);
      k.client(780, 810, {role: 'homeowner', pose: T >= tAsk ? 'talk' : 'stand', mood: 'calm', scale: 0.95, talk: T >= tAsk && T < tAsk + 1.5});
      bubble(k, d, 'WHO ANSWERS THE PHONE?', tAsk, 96);
      k.exampleTag(72, 450);
      if (T >= tWhat) stampBox(k, 'WHAT WILL YOU TELL HER?', 540, 640, tWhat, {color: GOLD, bg: WINE, size: 60, freeze: 4});
      return host(k, T >= tWhat ? 'shrug' : null);
    },
  },
};
for (const [n, f] of Object.entries(window.SCENE.sections)) window.SCENE.sections[n] = (k, T) => { const r = f(k, T); drift(k); return r; };
