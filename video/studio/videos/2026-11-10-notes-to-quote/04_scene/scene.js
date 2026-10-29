// Scene: Walkthrough notes to a quote (AI lead lane, lesson 3, Lead Clinic v2, arcade). One function per top-level cue in
// 03_cues/cues.md. Numbers only from k.data (brief.md -> data.js). Every beat lands on a spoken word (window.WORDS).
// The five beats: hook = the result first in three shots under one plate (the finished quote, example, items only; its
// lines close up, ticked; the messy walkthrough notes); play = the street set, the van out all day with the notes, then
// night at the kitchen table, the quote rebuilt from memory, the oven forgotten; fix = before and after on one page, the
// prompt typed on in an unbranded AI chat app strip, the notes crossing over as clean lines, the unpriced line flagged, the
// owner ticking every line against the rates; proof = the tool belt, Jobber's 54% of AI users who use it for quoting;
// button = the XP bar, YOUR PRICES levels up. No price is shown; no AI product is named or shown.
const INK = '#120D14', CREAM = '#FFF7EA', PAPER = '#F4E6D3', SAND = '#E6D3BC', MUTED = '#B39A88', GOLD = '#F7C873', ORANGE = '#F2A541',
  RED = '#E2633B', MAROON = '#7A3442', TEAL = '#6FB7A8', GREY = '#9AA0AD', NAVY = '#253048', PLUM = '#2B2033', DUSK = '#1B1420',
  BLUE = '#3B82C4', SKY = '#87CEEB', GREEN = '#3E7A62';
const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eo = (x) => 1 - Math.pow(1 - clamp(x), 3);

// ---- the pixel kit (low-res units: 360 x 640, one pixel = 3 frame units), the same primitives the sets use ----
const px = (k) => {
  const ctx = k.ctx, T = k.T, F = Math.floor(T * 30 + 0.005);
  const P = (x, y, w, h, c) => { x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h); if (w > 0 && h > 0 && c) { ctx.fillStyle = c; ctx.fillRect(x * 3, y * 3, w * 3, h * 3); } };
  const DOT = (x, y, c) => P(x, y, 1, 1, c);
  const dith = (x, y, w, h, c, ph = 0) => { ctx.fillStyle = c; for (let j = 0; j < h; j++) for (let i = (j + ph) & 1; i < w; i += 2) ctx.fillRect((Math.round(x) + i) * 3, (Math.round(y) + j) * 3, 3, 3); };
  const disc = (cx, cy, r, c) => { for (let dy = -r; dy <= r; dy++) { const hw = Math.floor(Math.sqrt(r * r - dy * dy) + 0.4); P(cx - hw, cy + dy, 2 * hw + 1, 1, c); } };
  const ring = (cx, cy, r, c, th = 1) => { for (let dy = -r; dy <= r; dy++) { const ho = Math.floor(Math.sqrt(r * r - dy * dy) + 0.4), ri = r - th, hi = Math.abs(dy) <= ri ? Math.floor(Math.sqrt(ri * ri - dy * dy) + 0.4) : -1; if (hi < 0) P(cx - ho, cy + dy, 2 * ho + 1, 1, c); else { P(cx - ho, cy + dy, ho - hi, 1, c); P(cx + hi + 1, cy + dy, ho - hi, 1, c); } } };
  const line = (x0, y0, x1, y1, c, th = 1) => {
    x0 = Math.round(x0); y0 = Math.round(y0); x1 = Math.round(x1); y1 = Math.round(y1);
    const dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1; let e = dx + dy;
    for (let n = 0; n < 2000; n++) { P(x0, y0, th, th, c); if (x0 === x1 && y0 === y1) break; const e2 = 2 * e; if (e2 >= dy) { e += dy; x0 += sx; } if (e2 <= dx) { e += dx; y0 += sy; } }
  };
  const win = (x, y, w, h, o = {}) => {
    const base = o.base || NAVY, hi = o.hi || BLUE, lo = o.lo || DUSK, rule = o.rule === undefined ? SKY : o.rule;
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
  const spr = (rows, pal, x, y, s = 1) => rows.forEach((r, j) => { for (let i = 0; i < r.length; i++) { const c = pal[r[i]]; if (c) P(x + i * s, y + j * s, s, s, c); } });
  const twinkle = (x, y, f, c = CREAM) => { const s = [0, 1, 2, 1][((f % 4) + 4) % 4]; DOT(x, y, c); for (let i = 1; i <= s; i++) { DOT(x - i, y, c); DOT(x + i, y, c); DOT(x, y - i, c); DOT(x, y + i, c); } };
  return {P, DOT, dith, disc, ring, line, win, fr, ease, tx, tw, clip, spr, twinkle, F, T};
};

// ---- the words: every beat lands on a spoken word ----
const WS = () => (window.WORDS && window.WORDS.words) || [];
const norm = (s) => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
const W = (re, from, dflt) => { const w = WS().find((x) => x.start >= from - 1.1 && re.test(x.w)); return w ? w.start : (dflt != null ? dflt : from); };
const WE = (re, from, dflt) => { const w = WS().find((x) => x.start >= from - 1.1 && re.test(x.w)); return w ? w.end : (dflt != null ? dflt : from); };
const spoken = (t0, said) => {
  const ws = WS(); let i = ws.findIndex((x) => x.start >= t0 - 1.1); if (i < 0) i = ws.length;
  let last = t0;
  return said.split(/\s+/).map((wd) => {
    const want = norm(wd); let j = i;
    while (j < ws.length && j < i + 6 && norm(ws[j].w) !== want) j++;
    if (j < ws.length && j < i + 6) { i = j + 1; last = ws[j].start; return [ws[j].start, ws[j].end]; }
    return [last, last + 0.2];
  });
};
const cnt = (k, num, t0, o = {}) => k.count(num.value, k.lin(t0, t0 + 0.7) >= 1 ? 1 : 0.85 + 0.15 * k.lin(t0, t0 + 0.7), Object.assign({from: 0}, o));
const host = (k, pose) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150});
// a typed paragraph: each word lands as it is said (red while said, then ink); words not yet said are grey stubs
const typed = (k, T, text, t0, x, y, maxX, o = {}) => {
  const size = o.size || 39, lh = o.lh || 45, times = spoken(t0, text), words = text.split(/\s+/), sp = k.measure(' ', {size});
  let xx = x, yy = y, lines = 1;
  words.forEach((wd, j) => {
    const ww = k.measure(wd, {size});
    if (xx + ww > maxX && xx > x) { xx = x; yy += lh; lines++; }
    const [ws, we] = times[j] || [1e9, 1e9];
    if (T < ws) { if (o.stubs !== false) k.shape(k.rectPts(xx, yy + size - 6, ww, 3, 0), {fill: o.stub || '#C9CCD3', line: false}); }
    else k.text(wd, xx, yy, {size, color: T < we + 0.05 ? (o.hot || RED) : (o.color || PLUM)});
    xx += ww + sp;
  });
  return lines;
};
// a block of text written out fast from t0 (a pasted or drafted message), wrapped to maxX, at a pace of `cps` characters a second
const written = (k, T, text, t0, x, y, maxX, o = {}) => {
  const size = o.size || 30, lh = o.lh || 45, n = T < t0 ? 0 : Math.floor((T - t0) * (o.cps || 140)), words = text.split(/\s+/), sp = k.measure(' ', {size});
  let xx = x, yy = y, used = 0, lines = 1;
  words.forEach((wd) => {
    const ww = k.measure(wd, {size});
    if (xx + ww > maxX && xx > x) { xx = x; yy += lh; lines++; }
    if (used + wd.length <= n) k.text(wd, xx, yy, {size, color: (o.colorOf && o.colorOf(wd)) || o.color || PLUM, lint: o.lint});
    used += wd.length + 1; xx += ww + sp;
  });
  return lines;
};


// ================================================================================================================
// the quote and the notes: our own pieces. The quote is a clean sheet on a clipboard (example: items only; the price
// column is the owner's own list, drawn as bars marked YOUR RATE, never a figure). The notes are a yellow legal pad of
// walkthrough scribbles with a coffee ring, arrows and a circled question.
const ITEMS = (n) => [`Deep clean, ${n.beds.shown} bed, ${n.baths.shown} bath`, 'Inside oven', 'Inside fridge', 'Baseboards', 'Pet hair, living room'];
const NOTES = (n) => [`${n.beds.shown}bd ${n.baths.shown}ba deep`, 'ovn inside?', 'fridge yes', 'bseboards', 'pet hair LR', 'blinds?'];
const tick = (d, x, y, c = '#2F6F67', n = 99) => { const pts = [[0, 4], [1, 5], [2, 6], [3, 5], [4, 4], [5, 3], [6, 2], [7, 1], [8, 0]]; pts.slice(0, n).forEach(([a, b]) => d.P(x + a, y + b, 2, 2, c)); };
const quoteSheet = (k, d, n, X, Y, Wd, H, o = {}) => {
  const {P} = d, T = d.T;
  P(X + 3, Y + 3, Wd, H, INK); P(X - 1, Y - 1, Wd + 2, H + 2, INK); P(X, Y, Wd, H, '#FBF6EC');
  P(X, Y, Wd, 22, NAVY); d.tx('DEEP CLEAN QUOTE', X + 8, Y + 4, {color: CREAM});
  const tg = 'EXAMPLE', tgw = d.tw(tg); P(X + Wd - tgw - 12, Y + 4, tgw + 8, 14, GOLD); d.tx(tg, X + Wd - tgw - 8, Y + 4, {color: INK});
  d.tx(o.colHead || 'YOUR RATE', X + Wd - 8, Y + 27, {color: o.colHot ? ORANGE : MUTED, align: 'right'});
  P(X + 6, Y + 41, Wd - 12, 1, SAND);
  ITEMS(n).forEach((s, i) => {
    const y = Y + 46 + i * (o.row || 24), at = o.itemAt ? o.itemAt(i) : -1;
    if (T < at) { P(X + 22, y + 9, 110, 1, '#E2DACB'); return; }
    const pop = d.fr(at) < 3 ? [3, 1, 0][d.fr(at)] : 0;
    P(X + 6, y + 2 - pop, 11, 11, INK); P(X + 7, y + 3 - pop, 9, 9, '#FBF6EC');
    const ok = o.tickAt ? T >= o.tickAt(i) : true;
    if (ok) tick(d, X + 8, y + 3 - pop, '#2F6F67', o.tickAt ? Math.min(9, d.fr(o.tickAt(i)) * 3 + 1) : 99);
    d.tx(s, X + 22, y - pop, {color: PLUM});
    const bw = 24, bx = X + Wd - 8 - bw, filled = o.rateAt ? T >= o.rateAt(i) : true;
    P(bx, y + 3 - pop, bw, 9, filled ? GOLD : '#EDE3D2'); P(bx + 3, y + 6 - pop, bw - 10, 3, filled ? '#C8A24C' : '#E2DACB');
  });
  if (o.flagAt != null && T >= o.flagAt) {
    const y = Y + 46 + 5 * (o.row || 24), pop = d.fr(o.flagAt) < 3 ? [3, 1, 0][d.fr(o.flagAt)] : 0;
    P(X + 4, y - 2 - pop, Wd - 8, 20, '#FBE1D8'); P(X + 4, y - 2 - pop, 3, 20, RED);
    d.tx('Blinds: not on your list', X + 12, y + 1 - pop, {color: RED});
  }
};
const notesPad = (k, d, n, X, Y, Wd, H, o = {}) => {
  const {P, line, ring} = d;
  P(X + 3, Y + 3, Wd, H, INK); P(X - 1, Y - 1, Wd + 2, H + 2, INK); P(X, Y, Wd, H, '#F8E58C');
  P(X, Y, Wd, 14, '#C9402F'); for (let x = X + 6; x < X + Wd; x += 12) P(x, Y + 3, 4, 8, '#8C2A20');
  for (let y = Y + 30; y < Y + H - 4; y += 22) P(X + 2, y, Wd - 4, 1, '#B9C9E8');
  P(X + 18, Y + 14, 1, H - 14, '#E99A9A');
  ring(X + Wd - 26, Y + H - 34, 14, '#C9A35A', 2);
  NOTES(n).forEach((s, i) => {
    const gone = o.goneAt ? d.T >= o.goneAt(i) : false; if (gone) return;
    const y = Y + 16 + i * 22, x = X + 24 + ((i * 7) % 3) * 2;
    d.tx(s, x, y, {color: i % 2 ? '#2B3F7A' : NAVY});
    if (i === 3) line(x, y + 7, x + d.tw(s), y + 5, '#2B3F7A');
  });
  if (o.circle !== false) { const y = Y + 16 + 1 * 22; line(X + 20, y + 15, X + 20 + d.tw('ovn inside?') + 10, y + 15, RED); line(X + 20 + d.tw('ovn inside?') + 10, y + 15, X + 20 + d.tw('ovn inside?') + 18, y + 4, RED); }
};
const hookPlate = (k, d) => {
  d.win(14, 86, 332, 62, {base: DUSK, hi: '#3D2E45', lo: INK, rule: MAROON});
  k.text('This quote started as', 540, 276, {size: 39, color: GOLD, align: 'center'});
  k.slam('messy notes.', 540, 336, -1, {size: 66, color: CREAM, align: 'center', drop: INK});
};
const desk = (d, c1 = '#6B4226', c2 = '#5A3A22') => { const {P} = d; P(0, 0, 360, 417, c1); for (let y = 0; y < 417; y += 14) { P(0, y, 360, 1, c2); for (let x = ((y / 14) % 2) * 45; x < 360; x += 90) P(x, y, 1, 14, c2); } for (let y = 417; y < 640; y += 16) for (let x = 0, c = 0; x < 360; x += 16, c++) P(x, y, 16, 16, ((y >> 4) + c) % 2 ? '#3D2E45' : '#2B2033'); };
const ovenIcon = (d, x, y, s = 2) => { const R = (a, b, w, h, c) => d.P(x + a * s, y + b * s, w * s, h * s, c); R(0, 0, 16, 16, INK); R(1, 1, 14, 14, '#C9CCD3'); R(1, 1, 14, 3, '#9AA0AD'); [3, 7, 11].forEach((a) => R(a, 2, 2, 1, INK)); R(3, 6, 10, 7, INK); R(4, 7, 8, 5, '#4A4E5A'); R(5, 8, 3, 1, ORANGE); };
const quiet = (k, fn) => { const t = k.text; k.text = function (s, ...a) { return /^(LV \d+|XP)$/.test(String(s)) ? {w: 0, h: 0, lines: []} : t.call(this, s, ...a); }; try { return fn(); } finally { k.text = t; } };

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'AI LESSON 3',
  sendLine: 'Send this to whoever writes your quotes.',
  transitions: {play: 'dissolve', fix: 'levelselect', proof: 'dissolve', button: 'levelselect'},
  trauma: {'button.prices': 0.5},
  sections: {
    // ---- hook: the result first. Cover: the finished quote on the desk under the plate. Cut by 0.8 s to its lines close
    // up, each ticked. Cut on "messy" to the messy walkthrough notes.
    hook: (k, T) => {
      const d = px(k), {P} = d, n = k.data.numbers;
      const tFrom = W(/^messy/i, k.S('hook.notes'), 2.1);
      const cut1 = 0.8, cut2 = Math.min(2.6, Math.max(1.6, tFrom - 0.05));
      if (T < cut1) {
        desk(d);
        P(36, 150, 290, 6, '#4A4E5A'); P(160, 146, 40, 8, GREY);
        quoteSheet(k, d, n, 40, 158, 280, 172);
        hookPlate(k, d);
        return host(k);
      }
      if (T < cut2) {
        P(0, 0, 360, 640, '#FBF6EC'); for (let y = 160; y < 417; y += 34) P(0, y, 360, 1, SAND);
        const pop = d.fr(cut1) < 4 ? [6, 3, 1, 0][d.fr(cut1)] : 0;
        ITEMS(n).slice(0, 4).forEach((s, i) => {
          const y = 166 + i * 40 - pop;
          P(20, y + 2, 22, 22, INK); P(22, y + 4, 18, 18, '#FBF6EC');
          if (T >= cut1 + 0.15 * i) { const m = Math.min(9, d.fr(cut1 + 0.15 * i) * 3 + 1); const pts = [[0, 8], [2, 10], [4, 12], [6, 10], [8, 8], [10, 6], [12, 4], [14, 2], [16, 0]]; pts.slice(0, m).forEach(([a, b]) => P(23 + a, y + 5 + b, 3, 3, '#2F6F67')); }
          k.text(s, 50 * 3, (y + 1) * 3, {size: 66, color: PLUM});
        });
        hookPlate(k, d);
        return host(k);
      }
      desk(d, '#4A2E1B', '#3D2614');
      notesPad(k, d, n, 60, 158, 240, 172);
      d.disc(300, 320, 12, '#6B4226'); d.ring(300, 320, 12, '#8C5A33', 2);
      hookPlate(k, d);
      k.burst(180 * 3, 240 * 3, cut2 + 0.05, {n: 12, r: 180, colors: ['accent', 'paper']});
      return host(k, 'shrug');
    },

    // ---- play: the street set, the van out all day with the notepad on the dash; then night at the kitchen table, the
    // quote rebuilt from memory, the oven forgotten
    play: (k, T) => {
      const d = px(k), {P} = d, t0 = k.S('play');
      const tNight = W(/^You$/i, k.S('play.night'), t0 + 2.6), tMem = W(/^memory/i, tNight, tNight + 1.6), tOven = W(/^oven/i, k.S('play.oven'), tMem + 1.6);
      if (T < tNight) {
        const s = k.sets.street({t0, speed: 1, van: true});
        k.slam('Notes: in the car all day.', 150, 300, t0 + 0.1, {size: 39, color: NAVY, from: 0.4});
        return host(k);
      }
      // night: the kitchen table, a blank quote, the thought bubble
      P(0, 0, 360, 417, '#1E2238'); for (let x = 6; x < 360; x += 18) P(x, 0, 2, 280, '#232842');
      P(220, 100, 110, 70, INK); P(222, 102, 106, 66, '#0E1430'); d.disc(300, 120, 8, '#F4E6D3'); d.disc(304, 117, 7, '#0E1430');
      P(0, 280, 360, 137, '#4A2E1B'); P(0, 280, 360, 2, '#6B4226');
      for (let y = 417; y < 640; y += 16) for (let x = 0, c = 0; x < 360; x += 16, c++) P(x, y, 16, 16, ((y >> 4) + c) % 2 ? '#1B1420' : '#151020');
      // a lamp pool on the table
      d.dith(120, 282, 200, 40, '#6B4226', d.F & 1);
      P(170, 290, 120, 40, INK); P(171, 291, 118, 38, '#FBF6EC'); P(171, 291, 118, 8, NAVY);
      for (let i = 0; i < 3; i++) P(178, 304 + i * 8, 60 + i * 12, 2, '#E2DACB');
      // the bubble of half-remembered items
      const bx = 40, by = 150, bw = 168, bh = 112;
      P(bx - 1, by - 1, bw + 2, bh + 2, INK); P(bx, by, bw, bh, CREAM); P(bx + 30, by + bh, 8, 6, CREAM); P(bx + 40, by + bh + 8, 5, 5, CREAM);
      d.tx('From memory:', bx + 8, by + 6, {color: MUTED});
      [['Deep clean', tMem], ['Fridge', tMem + 0.4], ['Baseboards?', tMem + 0.8]].forEach(([s, at], i) => { if (T >= at) d.tx(s, bx + 8, by + 26 + i * 20, {color: PLUM}); });
      if (T >= tOven) {
        ovenIcon(d, bx + 124, by + 50, 2);
        const f = d.fr(tOven), m = Math.min(20, f * 4); for (let i = 0; i < m; i++) { P(bx + 118 + i * 2, by + 44 + i * 2, 3, 3, RED); P(bx + 156 - i * 2, by + 44 + i * 2, 3, 3, RED); }
        k.slam('Forgot: the oven.', 540, 864, tOven, {size: 66, color: RED, align: 'center', stamp: true, drop: INK});
      }
      return host(k, T >= tOven ? 'shrug' : null);
    },

    // ---- fix: before and after on one page. The prompt types on in the app strip; the notes cross over as clean items;
    // the price column turns to MY PRICE LIST; the blinds line is flagged; the owner ticks every line against the rates
    fix: (k, T) => {
      const d = px(k), {P} = d, n = k.data.numbers, t0 = k.S('fix');
      const tP1 = W(/^Turn$/i, k.S('fix.p1')), tP2 = W(/^Use$/i, k.S('fix.p2')), tP3 = W(/^Flag$/i, k.S('fix.p3'));
      const tCheck = W(/^check$/i, k.S('fix.check')), tRates = W(/^rates/i, tCheck, tCheck + 1.6), tItem = WE(/^quote/i, tP1, tP1 + 1.8), tPrice = W(/^price$/i, tP2, tP2 + 0.8), tFlag = WE(/^price/i, tP3, tP3 + 1.4);
      desk(d, '#2F6F67', '#285F58');
      // the app strip (top)
      const X = 10, Y = 84, Wd = 340, H = 68;
      P(X + 3, Y + 3, Wd, H, INK); P(X - 1, Y - 1, Wd + 2, H + 2, INK); P(X, Y, Wd, H, '#F7F1E6'); P(X, Y, Wd, 16, '#2B2033');
      [RED, GOLD, TEAL].forEach((c, i) => d.disc(X + 8 + i * 8, Y + 8, 2, c));
      d.tx('AI CHAT APP', X + 34, Y + 2, {color: CREAM});
      const tg = 'EXAMPLE', tgw = d.tw(tg); P(X + Wd - tgw - 12, Y + 2, tgw + 8, 13, GOLD); d.tx(tg, X + Wd - tgw - 8, Y + 2, {color: INK});
      let y = (Y + 19) * 3;
      [{text: 'Turn these notes into an itemized quote.', at: tP1}, {text: 'Use only my price list.', at: tP2}, {text: "Flag anything I didn't price.", at: tP3}].forEach((r) => {
        typed(k, T, r.text, r.at, (X + 8) * 3, y, (X + Wd - 8) * 3, {size: 39, color: NAVY}); y += 45;
      });
      // before (left) and after (right)
      notesPad(k, d, n, 8, 158, 128, 172, {circle: false, goneAt: (i) => tItem + i * 0.25 + 0.2});
      quoteSheet(k, d, n, 146, 158, 206, 172, {row: 20, itemAt: (i) => tItem + i * 0.25, colHead: T >= tPrice ? 'MY PRICE LIST' : 'PRICE', colHot: T >= tPrice && T < tPrice + 1,
        tickAt: (i) => (T >= tCheck ? tCheck + 0.2 + i * 0.3 : 1e9), rateAt: (i) => (T >= tRates ? tRates + i * 0.12 : 1e9), flagAt: tFlag + 0.1});
      // the flying items: a note line moves across as its clean line lands
      for (let i = 0; i < 5; i++) { const a = tItem + i * 0.25, f = d.fr(a); if (f >= 0 && f < 6) { const x = 30 + f * 22, yy = 176 + i * 22 + Math.round((i * 2) * f / 6); P(x, yy, 18, 6, '#F8E58C'); P(x, yy, 18, 1, INK); } }
      return host(k, k.live('fix.check') ? 'point' : null);
    },

    // ---- proof: the tool belt. Jobber: of owners who use AI, 54% use it for quoting
    proof: (k, T) => {
      const n = k.data.numbers, t0 = k.S('proof'), t54 = W(/^fifty/i, k.S('proof.pct'), t0 + 2.6);
      k.sets.inventory({title: 'AI USES', hint: 'Which job?', items: [
        {icon: 'clip', name: 'QUOTING', stats: [{label: 'Of AI users', value: n.quotingPct.value, max: 100, text: n.quotingPct.shown}]},
        {icon: 'coin'}, {icon: 'mail'}, {icon: 'phone'}], select: [{slot: 0, at: t54}]});
      k.text('Jobber survey', 72, 612, {size: 39, color: GOLD});
      k.text(`${n.owners.shown} owners, Dec ${n.surveyYear.shown}`, 72, 660, {size: 39, color: CREAM});
      k.text('Base: owners who use AI', 72, 708, {size: 39, color: SAND});
      return host(k, k.live('proof.pct') ? 'point' : null);
    },

    // ---- button: the XP bar fills on "typing"; YOUR PRICES levels up on "prices"; the perks land
    button: (k, T) => {
      const t0 = k.S('button'), tType = W(/^typing/i, t0, t0 + 1.0), tPrices = W(/^prices/i, k.S('button.prices')), tNotes = W(/^notes/i, k.S('button.notes'), tPrices + 1.4);
      k.slam('The AI does the typing.', 540, 300, t0 + 0.05, {size: 39, color: GOLD, align: 'center', from: 0.4, drop: INK});
      quiet(k, () => k.sets.levelup({from: 0, to: 100, max: 100, at: tType, dur: Math.max(0.6, tPrices - tType - 0.1), levelAt: tPrices, text: 'YOUR PRICES',
        stats: [{text: 'Your rates', at: tPrices + 0.5}, {text: 'Your notes', at: tNotes}]}));
      return host(k, T >= tNotes ? 'wave' : null);
    },
  },
};
