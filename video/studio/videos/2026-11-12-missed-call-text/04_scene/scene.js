/* Scene: The missed-call text, part 1 of 3 (playbook, arcade; Depth bank #2). One function per top-level cue in        */
/* 03_cues/cues.md. Numbers only from k.data (brief.md -> data.js); every time from a cue start (k.S) or a spoken word   */
/* (wordT), so a re-voiced take moves the picture with it.                                                              */
/* Worlds: hook and button = our own workbench with a tape measure pulled out to the 160 mark (the text's whole budget), */
/* its close-up and a phone close-up; usual = street; parts = register; copy = our own big text card with a hud bar;    */
/* proof = scores. None of them used by the lesson before it in line (brief.md, Worlds).                                */
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

/* ================================================================================================================ */
/* the workshop wall and bench: a pegboard (holes in a grid, a few hooks), the bench top in planks, the floor dark   */
const bench = (k, o = {}) => {
  const d = px(k), {P, DOT, dith} = d;
  P(0, 0, 360, 417, '#2F4A55'); P(0, 0, 360, 2, '#3F6270');
  for (let y = 10; y < 300; y += 12) for (let x = 6 + ((y / 12) % 2) * 6; x < 360; x += 12) { P(x, y, 2, 2, '#1E333B'); DOT(x, y, '#18282E'); }
  /* hooks with a wrench and a hammer hanging, still (decor, top band, no text) */
  [[300, 22, 'wrench'], [330, 26, 'hammer']].forEach(([x, y, ic]) => { P(x + 8, y - 6, 2, 6, '#9AA0AD'); k.sets.icon(ic, x, y, 2); });
  const top = o.top || 300;
  P(0, top, 360, 6, '#B07A47'); P(0, top, 360, 1, '#E6C08A');
  for (let y = top + 6, i = 0; y < 417; y += 10, i++) { P(0, y, 360, 10, i % 2 ? '#8C5A33' : '#7A4E2C'); P(0, y + 9, 360, 1, '#5A3720'); const off = Math.floor(hash(i * 3.3) * 80); for (let x = off; x < 360; x += 80) P(x, y + 1, 1, 8, '#5A3720'); }
  P(0, 417, 360, 223, '#1B1420'); for (let x = 0; x < 360; x += 24) P(x, 417, 1, 223, '#231A29'); P(0, 417, 360, 2, '#3D2E45');
  if (o.dim) { k.ctx.save(); k.ctx.globalAlpha = o.dim; P(0, 0, 360, 417, '#120D14'); k.ctx.restore(); }
  return d;
};

/* the tape measure: a case on the left, the blade out to the right with ticks (unlabeled; only the brief's numbers are  */
/* written on it), the hook at the end. s = blade pixels a character. o: {x0, y, len, max, marks: [{v, c, label}]}       */
const tape = (k, d, o) => {
  const {P, DOT, line, F} = d, x0 = o.x0, y = o.y, len = o.len, h = o.h || 20, max = o.max, s = len / max, th = o.th || 1;
  /* the case: a rounded block, red with a black grip, the brake button */
  const cw = o.cw || 58, ch = o.ch || 58, cx = x0 - cw + 4, cy = y + Math.round(h / 2) - Math.round(ch / 2);
  P(cx + 3, cy + 3, cw, ch, INK); P(cx + 1, cy - 1, cw - 2, ch + 2, INK); P(cx - 1, cy + 1, cw + 2, ch - 2, INK);
  P(cx, cy, cw, ch, '#C8452B'); P(cx + 2, cy + 1, cw - 4, 2, '#E2633B'); P(cx, cy + ch - 4, cw, 4, '#8E2E1C');
  P(cx + 8, cy + 10, cw - 16, ch - 20, '#2B2033'); for (let j = cy + 12; j < cy + ch - 12; j += 4) P(cx + 10, j, cw - 20, 1, '#3D2E45');
  P(cx + cw - 12, cy - 5, 8, 6, INK); P(cx + cw - 11, cy - 4, 6, 4, GOLD);
  /* the blade */
  P(x0 - 1, y - 1, len + 2, h + 2, INK); P(x0, y, len, h, '#F7C873'); P(x0, y, len, 1, '#FFF2B8'); P(x0, y + h - 1, len, 1, '#C9963F');
  for (let v = 0; v <= max; v += 2) { const x = x0 + Math.round(v * s), big = v % 20 === 0, mid = v % 10 === 0; P(x, y + 1, th, big ? Math.round(h * 0.6) : mid ? Math.round(h * 0.4) : Math.round(h * 0.22), INK); }
  (o.marks || []).forEach((m) => { if (m.at != null && d.T < m.at) return; const x = x0 + Math.round(m.v * s); P(x - 1, y - 4, 3, h + 8, m.c); });
  /* the hook at the end: a steel L over the end of the blade */
  const hx = x0 + len; P(hx, y - 6, 5, h + 12, INK); P(hx + 1, y - 5, 3, h + 10, '#C9CCD3'); P(hx + 1, y - 5, 1, h + 10, '#FFFFFF');
  return {x: (v) => x0 + Math.round(v * s)};
};

/* a phone (low-res), w x h. o: {screen, missed (a red MISSED CALL band), bubble (a blank text bubble with a cursor)} */
const phone = (k, d, x, y, w, h, o = {}) => {
  const {P, F} = d;
  P(x + 3, y + 3, w, h, INK); P(x - 1, y, w + 2, h, INK); P(x, y - 1, w, h + 2, INK);
  P(x, y, w, h, '#2B2033'); P(x + 1, y, w - 2, 1, '#4A4E5A');
  P(x + 3, y + 6, w - 6, h - 14, o.screen || '#253048'); P(x + Math.round(w / 2) - 4, y + 2, 8, 2, '#120D14');
  if (o.missed) { P(x + 3, y + 6, w - 6, 26, '#7A3442'); P(x + 3, y + 31, w - 6, 1, RED); }
  if (o.bubble) { const bx = x + 10, by = y + h - 64, bw = w - 20; P(bx, by, bw, 34, '#3B82C4'); P(bx + 1, by + 1, bw - 2, 1, '#87CEEB'); P(bx + bw - 10, by + 34, 6, 4, '#3B82C4');
    if (((F / 15) | 0) % 2 === 0) P(bx + 8, by + 8, 2, 18, CREAM); }
};

/* the hook's title plate, held through every cut */
const hookPlate = (k, d, lines) => {
  d.win(14, 84, 332, 66, {base: '#253048', hi: '#3B82C4', lo: '#1B1420', rule: '#3B82C4'});
  k.text(lines[0], 540, 270, {size: 66, color: CREAM, align: 'center', drop: INK});
  k.text(lines[1], 540, 346, {size: 66, color: 'accent', align: 'center', drop: INK});
};
const HOOK = (n) => ['Your missed-call text', `gets ${n.plain.shown} characters.`];
const partTag = (k, d, n) => { const s = `PART ${n.part.shown} OF ${n.series.shown}`, w = Math.ceil((k.measure(s, {size: 39}) + 36) / 3); d.P(20, 160, w + 2, 22, INK); d.P(21, 161, w, 20, ORANGE); k.text(s, (21 + w / 2) * 3, 486, {size: 39, color: INK, align: 'center'}); };

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'TEXT BACK',
  sendLine: 'Send this to whoever answers your phones.',
  transitions: {usual: 'dissolve', parts: 'levelselect', copy: 'dissolve', proof: 'levelselect', button: 'gameover'},
  trauma: {'usual.no': 0.6},
  sections: {
    /* ---- hook: three shots. The cover: the bench, the tape out to 160 with the hero number over its hook, the plate    */
    /* "Your missed-call text / gets 160 characters." and PART 1 OF 3 (no host). Cut in by 0.8 s to the tape's hook close */
    /* up with the missed-call phone on the bench (Snow comes in). On "book" cut to the phone close up: a blank bubble.   */
    hook: (k, T) => {
      const n = k.data.numbers;
      const tIn = Math.min(0.8, Math.max(0.4, wordT(k, 'hook', /^text/i, 0.6))), tOut = Math.min(2.8, wordT(k, 'hook', /^book/i, 2.6));
      if (T >= tOut) {
        const d = bench(k, {top: 330});
        phone(k, d, 112, 158, 136, 168, {screen: '#253048', missed: true, bubble: true});
        k.text('MISSED CALL', 540, 492, {size: 39, color: CREAM, align: 'center', lint: false});
        hookPlate(k, d, HOOK(n));
        return host(k);
      }
      if (T >= tIn) {
        const d = bench(k, {top: 290});
        /* the close-up: the blade huge, its last stretch to the hook; 160 printed on the blade by the hook */
        const t = tape(k, d, {x0: -500, y: 196, len: 790, h: 52, max: n.plain.value, th: 2, cw: 0, ch: 0});
        k.text(n.plain.shown, (t.x(n.plain.value) - 12) * 3, 600, {size: 132, color: INK, align: 'right'});
        phone(k, d, 230, 262, 50, 30, {screen: '#7A3442'});
        hookPlate(k, d, HOOK(n));
        return host(k);
      }
      const d = bench(k);
      const t = tape(k, d, {x0: 84, y: 250, len: 250, h: 22, max: n.plain.value});
      /* the one focal point: the hero number over the hook, a gold arrow down to it */
      k.text(n.plain.shown, 924, 462, {size: 264, color: GOLD, align: 'right', drop: INK});
      d.line(t.x(n.plain.value) - 10, 230, t.x(n.plain.value) - 2, 244, GOLD, 2);
      hookPlate(k, d, HOOK(n));
      partTag(k, d, n);
      return {host: false, speech: false};
    },

    /* ---- usual: the clipboard on the bench. PART 1 OF 3: THE WORDS on the clip; the polite paragraph types out on    */
    /* "polite"; NO NAME stamps on "name", NO QUESTION on "question"; Snow shrugs on "Nobody".                          */
    usual: (k, T) => {
      const n = k.data.numbers, t0 = k.S('usual'), tPol = k.S('usual.polite');
      const tName = wordT(k, 'usual.no', /^name/i, 0.5), tQ = wordT(k, 'usual.no', /^question/i, 1.1), tNob = k.S('usual.nobody');
      const r = k.sets.street({t0, speed: 1, stopAt: tNob, stopDur: 0.8, sign: 'JOB', van: true});
      const d = px(k);
      /* the text bubble in the sky: the label, then the paragraph typing from the cut, done by "polite" */
      d.win(14, 84, 332, 150, {base: CREAM, hi: '#FFFFFF', lo: '#C9B79C', rule: '#3B82C4'});
      d.P(300, 234, 12, 8, '#C9B79C'); d.P(302, 234, 8, 6, CREAM);
      k.text(`THE WORDS (PART ${n.part.shown} OF ${n.series.shown})`, 540, 276, {size: 39, color: INK, align: 'center'});
      d.P(250, 212, 84, 18, ORANGE); k.text('EXAMPLE', 876, 640, {size: 30, color: INK, align: 'center', lint: false});
      const lines = ['Thanks for calling,', 'we value your', 'business.'], all = lines.join(' ').length;
      const shown = Math.floor(clamp((T - (t0 + 0.3)) / Math.max(0.6, tPol + 0.8 - (t0 + 0.3))) * all); let used = 0;
      lines.forEach((s2, i2) => { const c = clamp(shown - used, 0, s2.length); used += s2.length + 1; if (c > 0) k.text(s2.slice(0, c), 96, 360 + i2 * 78, {size: 66, color: INK}); });
      if (T >= tName) stampBox(k, 'NO NAME', 300, 600, tName, {color: RED, freeze: 4});
      if (T >= tQ) stampBox(k, 'NO QUESTION', 680, 600, tQ, {color: RED});
      return host(k, T >= tNob ? 'shrug' : (k.live('usual.no') ? 'point' : null));
    },

    /* ---- parts: the register set. WHO 29 rings on "Who", SORRY 26 on "Sorry", ASK 47 before the cut, CHARS 102 prints */
    /* as the total; the part's words land in the set's area.                                                         */
    parts: (k, T) => {
      const n = k.data.numbers, t0 = k.S('parts'), tWho = wordT(k, 'parts', /^who/i, 0.8), tSor = wordT(k, 'parts', /^sorry/i, 1.6), tEnd = k.S('copy');
      k.sets.register({prefix: '', totalLabel: 'CHARS', displayLabel: 'CHARS', items: [
        {label: 'WHO', amount: n.who.value, at: tWho}, {label: 'SORRY', amount: n.sorry.value, at: tSor}, {label: 'ASK', amount: n.ask.value, at: Math.max(tSor + 0.6, tEnd - 0.9)}],
        totalAt: Math.max(tSor + 0.9, tEnd - 0.5)});
      const say = T >= tSor ? ['Sorry I missed', 'your call.', tSor] : T >= tWho ? ['Who you are:', 'name and trade.', tWho] : ['Three parts.', 'Each one rings up.', t0];
      const d = px(k); d.win(14, 84, 332, 62, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
      k.slam(say[0], 72, 262, say[2], {size: 66, color: CREAM, from: 0.4, drop: INK, glint: false}); k.slam(say[1], 72, 336, say[2] + 0.06, {size: 66, color: GOLD, from: 0.4, drop: INK, glint: false});
      return host(k, k.live('parts') && T >= tWho ? 'point' : null);
    },

    /* ---- copy: the big text card, EXAMPLE. The four lines up at once, each part underlined in turn; the counter counts */
    /* to 102 / 160 and a tape strip fills to 102 under the 160 mark.                                                    */
    copy: (k, T) => {
      const n = k.data.numbers, t0 = k.S('copy'), d = bench(k, {top: 330, dim: 0.35});
      d.win(14, 84, 332, 154, {base: '#F4E6D3', hi: CREAM, lo: '#C9B79C', rule: '#3B82C4'});
      d.P(24, 92, 80, 20, INK); d.P(25, 93, 78, 18, ORANGE); k.text('EXAMPLE', 192, 282, {size: 30, color: INK, align: 'center', lint: false});
      const L = [['Hi, this is Sam the plumber.', TEAL], ['Sorry I missed your call.', ORANGE], ['What do you need fixed,', RED], ['and when works for you?', RED]];
      L.forEach((g, i) => { const ti = t0 - 0.2 + i * 0.12, y = 360 + i * 84; if (T >= ti) k.slam(g[0], 96, y, ti, {size: 66, color: INK, from: 0.3, glint: false}); if (T >= ti + 0.5 + i * 0.25) d.P(22, Math.round(y / 3) + 1, 4, 22, g[1]); });
      /* the counter: hero 102, then / 160, counting up */
      const p = clamp((T - (t0 + 0.4)) / 1.2), v = Math.round(n.len.value * eo(p));
      k.text(String(v), 640, 726, {size: 198, color: GOLD, align: 'right', drop: INK});
      k.text(`/ ${n.plain.shown}`, 664, 726, {size: 66, color: CREAM, drop: INK});
      k.text('CHARACTERS', 664, 804, {size: 39, color: SAND});
      /* the hud bar: the count against the 160 budget, a gold notch at the end */
      k.sets.hud({bar: {x: 104, y: 300, w: 220, from: 0, to: n.len.value, max: n.plain.value, at: t0 + 0.4, dur: 1.2, c: TEAL}});
      d.P(104 + 219, 296, 2, 16, GOLD);
      return host(k, k.live('copy') ? 'point' : null);
    },

    /* ---- proof: the scores set, CHARS PER TEXT. PLAIN 160 lands on "plain", EMOJI 70 (gold row) on "emoji", CURLY 70 */
    /* on "Curly"; the source on the screen the whole time it is said; 2 PIECES, 2 BILLS stamps on "bills".             */
    proof: (k, T) => {
      const n = k.data.numbers, t0 = k.S('proof'), tPl = wordT(k, 'proof', /^plain/i, 1.4), tEm = wordT(k, 'proof.emoji', /^emoji/i, 0.5);
      const tCu = wordT(k, 'proof.emoji', /^curly/i, 2.4), tBill = wordT(k, 'proof.split', /^piece/i, 2.4);
      k.sets.scores({title: 'CHARS PER TEXT', t0: tPl - 0.2, gap: 0, count: 0.6, rows: [
        {name: 'PLAIN', value: n.plain.value, rank: ' '}]});
      const d = px(k);
      /* rows 2 and 3 drawn on the table's grid (y 174, 198) as they are said, red: the drop */
      [[tEm, 'EMOJI', 174], [tCu, 'CURLY', 198]].forEach(([ti, name, y]) => { if (T < ti) return; const sl = d.ease(ti, 5, 40);
        d.P(32, y - 4, 280, 21, '#3D2E45'); d.tx(name, 110 + sl, y, {color: RED}); d.tx(n.emoji.shown, 306 + sl, y, {color: RED, align: 'right'}); });
      if (T >= tBill) { k.text("Sam's text plus an emoji:", 540, 600, {size: 39, color: CREAM, align: 'center'}); stampBox(k, `${n.segs.shown} PIECES, ${n.segs.shown} BILLS`, 540, 664, tBill, {color: RED, freeze: 4}); }
      else if (T >= tEm) k.slam(n.emoji.shown, 540, 640, tEm, {size: 198, color: RED, align: 'center', from: 0.5, drop: INK, glint: false});
      else if (T >= tPl) k.slam(n.plain.shown, 540, 640, tPl, {size: 198, color: GOLD, align: 'center', from: 0.5, drop: INK, glint: false});
      k.text('Source: Twilio docs,', 600, 846, {size: 39, color: SAND, align: 'center'});
      k.text('How long can a message be?', 600, 900, {size: 39, color: SAND, align: 'center'});
      return host(k, k.live('proof.split') ? 'point' : null);
    },

    /* ---- button: back on the bench, the tape out to 160, the clean text's 102 marked in teal. NEXT: PART 2, TURN IT ON; */
    /* the rule lands in gold on "Keep".                                                                               */
    button: (k, T) => {
      const n = k.data.numbers, t0 = k.S('button'), tKeep = k.S('button.rule');
      const d = bench(k);
      const pull = clamp((T - (t0 + 0.1)) / 0.9), lenNow = Math.max(40, Math.round(250 * eo(pull)));
      const t = tape(k, d, {x0: 84, y: 250, len: lenNow, h: 22, max: Math.max(1, Math.round(n.plain.value * lenNow / 250)), marks: [{v: n.len.value, c: TEAL, at: t0 + 0.9}]});
      if (T >= t0 + 0.9) k.text(n.len.shown, t.x(n.len.value) * 3, 696, {size: 66, color: TEAL, align: 'center', drop: INK});
      if (pull >= 1) k.text(n.plain.shown, 920, 696, {size: 66, color: GOLD, align: 'right', drop: INK});
      d.win(14, 84, 332, 70, {base: '#1B1420', hi: '#7A3442', lo: INK, rule: ORANGE});
      if (T < tKeep) { k.slam(`NEXT: PART ${n.next.shown},`, 540, 280, t0 + 0.1, {size: 66, color: CREAM, align: 'center', from: 0.4, drop: INK, glint: false}); k.slam('TURN IT ON.', 540, 358, t0 + 0.16, {size: 66, color: ORANGE, align: 'center', from: 0.4, drop: INK, glint: false}); }
      else { k.slam('Keep it plain.', 540, 280, tKeep, {size: 66, color: CREAM, align: 'center', from: 0.4, drop: INK, glint: false}); k.slam(`Under ${n.plain.shown}.`, 540, 358, tKeep + 0.1, {size: 66, color: GOLD, align: 'center', from: 0.4, drop: INK, glint: false}); k.sweep(540 - k.measure(`Under ${n.plain.shown}.`, {size: 66}) / 2, 432, k.measure(`Under ${n.plain.shown}.`, {size: 66}), 6, tKeep + 0.4, {color: 'accent'}); }
      return host(k, T >= tKeep + 0.8 ? 'wave' : (k.live('button') ? 'point' : null));
    },
  },
};
