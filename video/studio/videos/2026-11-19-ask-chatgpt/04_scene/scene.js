/* Scene: Ask the robot who it would hire (story, shape two-scenes, arcade; Nov 7, 2026, r10 words). One function per   */
/* top-level cue in 03_cues/cues.md. Numbers only from k.data; every time from a cue start or a spoken word (wordT).     */
/* Worlds: hook and button = our own drawn kitchen at night and her phone (EXAMPLE; our own chat box, never a real      */
/* ChatGPT screen, and no AI reply is drawn); forum = our own forum card (paraphrased, no names); stakes = the shop      */
/* phone on a truck dash; check = the save-screen card (the send moment); why, survey, small = the sources' cards.      */
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

/* ================================================================================================================ */
/* our own drawn kitchen at night (EXAMPLE): the window with frost, the furnace closet with its pilot light (out from  */
/* o.outAt), the counter, her phone lit on it. Everything above y 300 (low-res) so the band under it stays the host's. */
const kitchen = (k, o = {}) => {
  const d = px(k), {P, dith, disc, F} = d, out = o.outAt !== undefined && k.T >= o.outAt;
  P(0, 0, 360, 417, o.moon ? '#0B1220' : '#5A4A60'); for (let y = 0; y < 417; y += 4) dith(0, y, 360, 1, o.moon ? '#121B2E' : '#6A5A70', (y / 4) % 2);
  /* the window: night sky, frost creeping in the corners */
  P(196, 150, 130, 96, INK); P(200, 154, 122, 88, '#16233A'); P(259, 154, 4, 88, INK); P(200, 196, 122, 4, INK);
  for (let i = 0; i < 18; i++) d.DOT(204 + Math.floor(hash(i * 4.1) * 112), 158 + Math.floor(hash(i * 9.3) * 30), CREAM);
  for (let i = 0; i < 26; i++) { const fx = hash(i * 2.7), fy = hash(i * 5.9); d.DOT(i % 2 ? 202 + Math.floor(fx * 14) : 306 + Math.floor(fx * 14), 226 + Math.floor(fy * 14), '#CFE8F5'); }
  /* the furnace closet: a door, the furnace, its light */
  P(30, 150, 120, 150, INK); P(34, 154, 112, 146, '#3D2E45'); P(48, 170, 84, 110, '#4A4E5A'); P(52, 174, 76, 30, '#6B7080');
  for (let i = 0; i < 5; i++) P(56, 214 + i * 10, 68, 3, '#3D2E45');
  const flick = out ? 0 : ((F >> 2) % 3);
  disc(90, 262, 5, out ? '#2B2033' : [ORANGE, GOLD, ORANGE][flick]); if (!out) disc(90, 262, 2, CREAM);
  if (out) { d.tx('OFF', 270, 760, {size: 36, color: GREY, align: 'center', lint: false}); }
  /* the thermostat on the wall */
  P(166, 196, 22, 30, INK); P(168, 198, 18, 26, CREAM); d.tx(out ? 'COLD' : 'HEAT', 531, 610, {size: 24, color: out ? '#3B82C4' : RED, align: 'center', lint: false});
  /* the counter and the phone glowing on it */
  P(0, 292, 360, 8, '#8C5A33'); P(0, 300, 360, 117, '#4A2E1B');
  const glow = o.phoneLit !== false; P(214, 280, 40, 12, INK); P(216, 282, 36, 8, glow ? SKY : '#253048');
  if (glow) for (let i = 0; i < 6; i++) d.DOT(214 + Math.floor(hash(i + (F >> 3)) * 40), 274 + Math.floor(hash(i * 3 + (F >> 3)) * 4), SKY);
  return d;
};
/* our own drawn chat box on her phone (EXAMPLE, no brand, no reply): the question types from t0 */
const chatBox = (k, d, q, t0, o = {}) => {
  const {P, win} = d, up = d.ease(t0 - 0.1, 6, 40);
  win(30, 150 + up, 300, 150, {base: CREAM, hi: '#FFFFFF', lo: SAND, rule: false});
  P(30, 150 + up, 300, 20, '#2F6F67'); k.text('ASK THE CHAT', 132, 456 + up * 3, {size: 39, color: CREAM});
  if (up) return;
  const n = Math.max(0, Math.floor((k.T - t0) * 34)); let left = n;
  q.forEach((s, i) => { const m = Math.min(s.length, left); left -= m; if (m) k.text(s.slice(0, m), 120, 540 + i * 62, {size: 48, color: INK}); });
  const done = n >= q.join('').length;
  if (done) { P(290, 268, 28, 22, '#2F6F67'); d.line(298, 279, 310, 279, CREAM, 2); d.line(306, 274, 311, 279, CREAM, 2); d.line(306, 284, 311, 279, CREAM, 2);
    const dots = Math.floor((k.T - t0) * 3) % 4; for (let i = 0; i < 3; i++) d.disc(52 + i * 12, 280, 3, i < dots ? '#2F6F67' : SAND); }
};
/* a source card in the band: header, lines, tag (all our words or the page's own line) */
const srcCard = (k, d, head, t0, o = {}) => {
  const {P, win} = d, up = d.ease(t0, 6, 30), h = o.h || 170;
  win(14, 84 + up, 332, h, {base: CREAM, hi: '#FFFFFF', lo: SAND, rule: false});
  P(14, 84 + up, 332, 20, o.hc || '#3B82C4'); k.text(head, 72, 258 + up * 3, {size: 39, color: CREAM});
  return up;
};
const flash = (k, d, t) => { const f = d.fr(t); if (f >= 0 && f < 2) d.P(0, 0, 360, 417, '#FFFFFF'); };
const tag = (k, d, s, y = 290, s2) => { plate(d, 14, y, 332, s2 ? 46 : 30); k.text(s, 72, y * 3 + 24, {size: 33, color: SAND}); if (s2) k.text(s2, 72, y * 3 + 72, {size: 33, color: SAND}); };

/* the check card (the send moment): two steps, lit on their words, held to screenshot */
const checkCard = (k, d, t1, t2, t0, o = {}) => {
  const {P, win} = d, small = o.small;
  if (small) { win(14, 84, 332, 150, {base: '#253048', hi: '#3B82C4', lo: INK, rule: false}); P(14, 84, 332, 20, GOLD); k.text('THE CHECK', 72, 258, {size: 39, color: INK});
    k.text('1. Ask ChatGPT who is', 72, 330, {size: 48, color: CREAM}); k.text('the best near you.', 72, 390, {size: 48, color: CREAM});
    k.text('2. Not you? Fix your', 72, 470, {size: 48, color: GOLD}); k.text('Google profile first.', 72, 530, {size: 48, color: GOLD}); return; }
  const up = d.ease(t0, 6, 160);
  d.clip(0, 0, 360, 330, () => { win(14, 84 + up, 332, 196, {base: '#253048', hi: '#3B82C4', lo: INK, rule: false}); P(14, 84 + up, 332, 20, GOLD); });
  if (up) return;
  k.text('THE CHECK: DO IT TONIGHT', 72, 258, {size: 39, color: INK});
  const rows = [['1. Ask ChatGPT:', '"Who\'s the best [your', 'trade] near me?"'], ['2. Not you? Fix your', 'Google profile first.', '']];
  /* the send moment (Todd, Nov 7, 9:27 am): every line lands once in the first half second, then nothing moves over the card */
  rows.forEach(([a, b, c], i) => { const y = 324 + i * 230, ti = t0 + 0.25 + i * 0.12, col = i ? GOLD : CREAM;
    k.slam(a, 72, y, ti, {size: 56, color: GOLD, from: 0.3});
    k.slam(b, 72, y + 66, ti + 0.04, {size: 56, color: col, from: 0.3});
    if (c) k.slam(c, 72, y + 132, ti + 0.08, {size: 56, color: col, from: 0.3}); });
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'ASK THE CHAT',
  sendLine: 'Send this to whoever runs your Google profile.',
  transitions: {forum: 'mosaic', stakes: 'dissolve', check: 'levelselect', why: 'fade4', small: 'mosaic', button: 'gameover'},
  trauma: {stakes: 0.4},
  sections: {
    /* ---- hook: scene one (cover, no host): the kitchen at night, her phone lit; the question plate. Change 1 when the  */
    /* host comes on: the moonlight drops (the wall goes blue). Change 2 on "quits": a flash, the furnace light goes out,  */
    /* NO HEAT. On "asks": her phone in the truck-dash chat set (our own app, EXAMPLE); her question goes up, no reply.     */
    hook: (k, T) => {
      const tIn = Math.min(0.9, Math.max(0.5, wordT(k, 'hook', /^furnace/i, 0.6) - 0.3)), tOut = Math.min(2.6, wordT(k, 'hook', /^quits/i, 1.4) - 0.1), tAsk = k.S('hook.ask'), tChat = Math.max(tOut + 0.6, wordT(k, 'hook', /^doesn/i, 2.4) - 0.2);   /* her phone from "doesn't call around": the chat set holds over 5% of the runtime */
      if (T < tChat) {
        const d = kitchen(k, {outAt: tOut, moon: T >= tIn});
        flash(k, d, tOut);
        topPlate(k, d, 'Who does ChatGPT', 'send her to?', -1);
        if (T >= tOut) stampBox(k, 'NO HEAT', 400, 640, tOut, {color: '#3B82C4', freeze: 3});
        exampleTag(d, 150, 256);   /* render critic r0: off the plate, it covered the '?' of the hook line */
        if (T < tIn) return {host: false, speech: false};
        return host(k, T >= tOut ? 'shock' : null);
      }
      k.sets.chat({who: 'CHAT (EXAMPLE)', clock: '9:02 PM', msgs: [{me: true, text: 'Who should I hire to fix my heat tonight?', at: tAsk - 0.25}]});
      return host(k);
    },

    /* ---- forum: scene two, the owner's side: our forum card, the owner's report paraphrased, each line on its words; a  */
    /* counter to 4 on "four". forum.hedge: the hedge line and a "?" bobbing.                                            */
    forum: (k, T) => {
      const t0 = k.S('forum'), tH = k.S('forum.hedge'), tFour = wordT(k, 'forum', /^four/i, 3.0) - 0.25, tLeast = wordT(k, 'forum', /^least/i, 2.8) - 0.25, tPeople = wordT(k, 'forum', /^people/i, 3.4) - 0.25, tChat = wordT(k, 'forum', /^chatgpt/i, 5.0) - 0.25, four = k.data.numbers.four.value;
      const d = px(k), {P, dith} = d;
      P(0, 0, 360, 417, '#2B2033'); for (let y = 0; y < 417; y += 4) dith(0, y, 360, 1, '#3D2E45', (y / 4) % 2);
      const up = srcCard(k, d, 'OWNER FORUM (JOBBER)', t0 + 0.05, {h: 190, hc: '#2F6F67'});
      if (!up) {
        k.text('One owner, paraphrased:', 72, 330, {size: 39, color: '#4A4E5A'});
        if (T >= tLeast) { k.slam(`At least ${four}`, 72, 392, tLeast, {size: 66, color: RED, from: 0.4}); }
        if (T >= tPeople) k.slam('people last month told', 72, 480, tPeople, {size: 52, color: INK, from: 0.3});
        if (T >= tChat) k.slam('them ChatGPT sent them.', 72, 544, tChat, {size: 52, color: INK, from: 0.3});
        if (T >= tH) { k.slam("But: didn't think they'd", 72, 628, tH - 0.25, {size: 52, color: '#2F6F67', from: 0.3}); k.slam('done a thing there.', 72, 692, tH - 0.2, {size: 52, color: '#2F6F67', from: 0.3});
          const b = [0, -1, -2, -1][(d.F >> 3) % 4]; k.text('?', 900, 610 + b * 3, {size: 99, color: GOLD, align: 'center', lint: false}); }
      }
      tag(k, d, 'Jobber Community, Nov 2026, paraphrased', 290);
      return host(k, T >= tH ? 'shrug' : null);
    },

    /* ---- stakes: the shop phone on a truck dash stays dark; the call bar never fills; NO RING on "never".              */
    stakes: (k, T) => {
      const t0 = k.S('stakes'), tNever = wordT(k, 'stakes', /^never$/i, 1.6) - 0.25;
      const d = px(k), {P, dith, F} = d;
      P(0, 0, 360, 417, '#1F2A40'); for (let y = 0; y < 417; y += 4) dith(0, y, 360, 1, '#253048', (y / 4) % 2);
      P(0, 250, 360, 50, '#2B2033'); P(0, 250, 360, 3, '#4A4E5A'); P(30, 262, 60, 24, INK); disc4(d, 60, 274);
      P(150, 140, 70, 108, INK); P(154, 144, 62, 100, '#120D14'); P(174, 248, 22, 6, INK);
      const q = ((T - t0) * 0.6) % 1; P(160, 228, 50, 6, '#253048'); P(160, 228, Math.round(50 * (0.15 + 0.2 * Math.sin(q * Math.PI))), 6, GREY);
      k.text('WAITING', 555, 560, {size: 33, color: GREY, align: 'center', lint: false});
      topPlate(k, d, 'It names someone else.', 'Your phone may stay dark.', t0 + 0.02);
      if (T >= tNever) stampBox(k, 'NO RING', 720, 600, tNever, {color: RED, freeze: 4});
      return host(k, T >= tNever ? 'shrug' : null);
    },

    /* ---- check: THE CHECK (the send moment): step 1 lights on "ask", step 2 on "isn't"; held through "first".         */
    check: (k, T) => {
      const t0 = k.S('check'), t1 = wordT(k, 'check', /^ask$/i, 0.6), t2 = wordT(k, 'check', /^isn/i, 3.0);
      const d = px(k), {P, dith} = d;
      P(0, 0, 360, 417, '#3D2E45'); for (let y = 0; y < 417; y += 4) dith(0, y, 360, 1, '#2B2033', (y / 4) % 2); P(0, 417, 360, 223, NIGHT);
      checkCard(k, d, t1, t2, t0 + 0.05);
      return host(k, 'point');
    },

    /* ---- why: what the chat reads, as an RPG tool belt (inventory set): the cursor lands on NAME, WEBSITE, REVIEWS   */
    /* on their words; the source tag under it.                                                                         */
    why: (k, T) => {
      const t0 = k.S('why'), ts = [wordT(k, 'why', /^name/i, 6.0) - 0.25, wordT(k, 'why', /^website/i, 6.6) - 0.25, wordT(k, 'why', /^reviews/i, 7.2) - 0.25];
      k.sets.inventory({title: 'WHAT THE CHAT READS', items: [{icon: 'clip', name: 'NAME', stats: []}, {icon: 'phone', name: 'WEBSITE', stats: []}, {icon: 'star', name: 'REVIEWS', stats: []}],
        select: [{slot: 0, at: Math.min(ts[0], t0 + 0.3)}, {slot: 1, at: ts[1]}, {slot: 2, at: ts[2]}], footer: 'FROM WHAT IS OUT THERE'});
      const d = px(k); tag(k, d, 'ACHR News column, Mar 18, 2026', 290, '(SearchLight data)');
      return host(k, 'point');
    },

    /* ---- small: ABOUT 1% on "about"; then the till rings up one job from the chat at the firm's average ticket.        */
    small: (k, T) => {
      const t0 = k.S('small'), tP = wordT(k, 'small', /^about$/i, 2.4) - 0.25, tAvg = wordT(k, 'small', /^average/i, 6.0) - 0.4, r1 = k.data.numbers.rev1.shown, tk = k.data.numbers.ticket;
      if (T < tAvg) {
        const d = px(k), {P, dith} = d;
        P(0, 0, 360, 417, '#2B2033'); for (let y = 0; y < 417; y += 4) dith(0, y, 360, 1, '#3D2E45', (y / 4) % 2);
        d.win(14, 84, 332, 196, {base: NIGHT, hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
        k.text('JOBS FROM CHATGPT', 72, 270, {size: 39, color: GOLD}); k.text('Share of revenue, most shops', 72, 330, {size: 36, color: SAND});
        P(30, 128, 300, 24, '#253048'); if (T >= tP) { P(30, 128, 4, 24, GOLD); k.slam(`ABOUT ${r1}`, 132, 480, tP, {size: 66, color: GOLD, from: 0.4}); }
        tag(k, d, 'ACHR News column, Mar 18, 2026', 290, '(SearchLight data)');
        return host(k);
      }
      k.sets.register({items: [{label: 'CHAT JOB', amount: tk.value, at: tAvg + 0.1}], prefix: '$', totalAt: tAvg + 0.5, openAt: tAvg + 0.9, totalLabel: 'AVG TICKET', displayLabel: 'AVG'});
      return host(k, 'shock');
    },

    /* ---- button: the kitchen phone, the question still on it; THE CHECK small; plate on the close; Snow points.         */
    button: (k, T) => {
      const t0 = k.S('button'), tA = wordT(k, 'button', /^ask$/i, 2.4) - 0.2;
      const d = px(k), {P, dith} = d;
      P(0, 0, 360, 417, '#1B1420'); for (let y = 0; y < 417; y += 4) dith(0, y, 360, 1, '#241A2B', (y / 4) % 2);
      checkCard(k, d, 0, 0, 0, {small: true});
      if (T >= tA) { plate(d, 14, 244, 332, 50); k.slam('Ask it before they do.', 540, 760, tA, {size: 66, color: GOLD, align: 'center', from: 0.4}); }
      return host(k, 'point');
    },
  },
};

/* a wheel on the dash speaker grille (tiny detail) */
function disc4(d, x, y) { d.disc(x, y, 8, '#3D2E45'); d.disc(x, y, 3, INK); }

/* the drift from lsa-max-bid r28 (code QA: no flat stretch): a faint dither moves down the empty lower band. */
const drift = (k) => { const d = px(k), off = Math.floor(k.T * 30) % 16; for (let y = 418 - 16 + off; y < 640; y += 16) { const y0 = Math.max(418, y), y1 = Math.min(640, y + 8); if (y1 > y0) d.P(0, y0, 360, y1 - y0, '#3D2E45'); } };   /* lighter than every floor here, so it reads as motion (code QA: flat in the forum) */
for (const [n, f] of Object.entries(window.SCENE.sections)) window.SCENE.sections[n] = (k, T) => { const r = f(k, T); drift(k); return r; };
