// Scene: Raise your prices; most trades already did (Lesson 6, Pricing Clinic, arcade). One function per top-level cue in
// 03_cues/cues.md. Numbers only from k.data (brief.md -> data.js). Every time comes from a cue start (k.S) or a spoken word
// (wordT), so a re-voiced take moves the picture with it.
// Worlds (brief.md): hook, stakes, caveat, close = the weather map (PRICE FORECAST, a sun per trade); why = the register
// with the HUD's coins; note = the price note on a desk, drawn here (a ticking clock, a steaming mug, a letterhead sheet).
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', GREY = '#9AA0AD';
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
  return {P, DOT, dith, disc, line, win, fr, ease, tx, tw, clip, twinkle, F, T};
};

// ---- the words: every beat lands on a spoken word, so a re-voiced take moves everything with it ----
const WS = () => (window.WORDS && window.WORDS.words) || [];
const norm = (s) => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
// the time a word is said (words.json), at or after a cue (or a time); falls back to the cue's start plus dflt
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
// the start and end of each spoken word of a line, matched in order from t0 (a missing word takes the one before's time)
const spoken = (t0, said) => {
  const ws = WS(); let i = ws.findIndex((x) => x.start >= t0 - 0.05); if (i < 0) i = ws.length;
  let last = t0;
  return said.split(/\s+/).map((wd) => {
    const want = norm(wd); let j = i;
    while (j < ws.length && j < i + 6 && norm(ws[j].w) !== want) j++;
    if (j < ws.length && j < i + 6) { i = j + 1; last = ws[j].start; return [ws[j].start, ws[j].end]; }
    return [last, last + 0.2];
  });
};
// a count that starts at 85% of its value and lands exactly on it
const cnt = (k, num, t0, o = {}) => k.count(num.value, k.lin(t0, t0 + 0.7) >= 1 ? 1 : 0.85 + 0.15 * k.lin(t0, t0 + 0.7), Object.assign({from: 0}, o));
const host = (k, pose) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150});

// ================================================================================================================
// a set's own text that our panels cover is not drawn at all (hidden text still counts for the layout lint)
const mute = (k, drop, fn) => { const real = k.text; k.text = function (s, x, y, o) { if (drop(s, x, y, o)) return; return real.call(this, s, x, y, o); }; try { return fn(); } finally { k.text = real; } };

// the weather map: k.sets.weather with a sun per trade (a cloud for the lowest), then our own panel over the season strip
// (the brief has no monthly series, so no month bars are drawn). Panel: low-res x 14..346, y 262..330 (frame y 786..990).
const ICONS = {hvac: [0.07, 0.24], elec: [0.40, 0.24], plumb: [0.07, 0.55], clean: [0.40, 0.55], roof: [0.07, 0.86], q: [0.40, 0.86]};
const weatherMap = (k, o) => {
  const icons = (o.icons || []).map(([key, kind, at, label]) => ({kind, x: ICONS[key][0], y: ICONS[key][1], at, label}));
  // the strip's month letters sit under our panel and the title under the close's window: neither is drawn
  mute(k, (s, x, y) => (y === 915 && String(s).length === 1) || (o.noTitle && y === 732),
    () => k.sets.weather({title: o.title || 'PRICE FORECAST', fronts: o.fronts || [], icons, months: []}));
  const d = px(k);
  d.win(14, 262, 332, 68, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
};
// every trade on the map, settled (for the sections after the stakes)
const allTrades = (n) => [['hvac', 'sun', -1, `HVAC ${n.hvac.shown}`], ['elec', 'sun', -1, `ELEC ${n.elec.shown}`], ['plumb', 'sun', -1, `PLUMB ${n.plumb.shown}`],
  ['roof', 'sun', -1, `ROOF ${n.roof.shown}`], ['clean', 'cloud', -1, `CLEAN ${n.clean.shown}`]];

// ================================================================================================================
// the desk (note): an office wall with a ticking clock, a desk, a steaming mug; the scene puts the letterhead on top
const desk = (k) => {
  const d = px(k), {P, DOT, disc, line, F, T} = d;
  P(0, 0, 360, 286, '#2F5A4A'); for (let x = 0; x < 360; x += 16) { P(x, 0, 8, 286, '#24453A'); DOT(x + 4, 20 + (x % 7) * 9, '#3E7A62'); }
  P(0, 236, 360, 50, '#5A3A22'); P(0, 236, 360, 2, '#8C5A33'); for (let x = 0; x < 360; x += 30) P(x, 238, 1, 48, '#4A2E1B');
  // the clock on the wall right of the sheet: the second hand steps every half second
  const cx = 334, cy = 104; disc(cx, cy, 15, INK); disc(cx, cy, 14, '#B07A47'); disc(cx, cy, 12, CREAM);
  for (let s = 0; s < 12; s++) { const a = s * Math.PI / 6; DOT(cx + Math.round(Math.cos(a) * 10), cy + Math.round(Math.sin(a) * 10), s % 3 ? GREY : INK); }
  const sa = (Math.floor(T * 2) % 120) * Math.PI / 60 - Math.PI / 2; line(cx, cy, cx + Math.round(Math.cos(sa) * 10), cy + Math.round(Math.sin(sa) * 10), RED);
  line(cx, cy, cx, cy - 7, INK); line(cx, cy, cx + 5, cy, INK); DOT(cx, cy, INK);
  // the desk top and its front
  P(0, 286, 360, 8, '#D9A066'); P(0, 286, 360, 1, '#F7C873'); P(0, 293, 360, 2, '#6B4226'); P(0, 295, 360, 122, '#8C5A33');
  for (let x = 12; x < 360; x += 80) { P(x, 306, 64, 100, '#6B4226'); P(x, 306, 64, 1, '#B07A47'); P(x + 28, 352, 8, 3, '#F7C873'); }
  // the mug at the desk's right edge, steam rising on whole pixels every 3 frames
  const mx = 326; P(mx - 1, 266, 20, 21, INK); P(mx, 267, 18, 19, RED); P(mx, 267, 18, 2, '#F09A9A'); P(mx + 14, 269, 4, 17, '#7A3442'); P(mx + 18, 271, 5, 9, INK); P(mx + 18, 273, 3, 5, RED);
  for (let i = 0; i < 3; i++) for (let j = 0; j < 6; j++) { const y = 262 - ((Math.floor(F / 3) + j * 4 + i * 5) % 24); if (y > 238 && y < 263) DOT(mx + 4 + i * 5 + (Math.floor((y + i) / 4) % 2), y, '#C9CCD3'); }
  // the floor
  P(0, 417, 360, 223, '#4A2E1B'); for (let y = 417, r = 0; y < 640; y += 10, r++) { P(0, y, 360, 1, '#6B4226'); for (let x = (r * 37) % 60; x < 360; x += 60) P(x, y + 1, 1, 9, '#2B2033'); }
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 6',
  transitions: {stakes: 'dissolve', why: 'levelselect', note: 'iris', caveat: 'dissolve', close: 'gameover'},
  trauma: {'note.promise': 0.8},
  sections: {
    // ---- hook: the weather map, settled on frame 0 (the HVAC sun, the hook card, the source); no host or dialog yet
    hook: (k, T) => {
      const n = k.data.numbers, d = px(k), tRaised = k.S('hook.raised'), tYou = k.S('hook.you'), tNote = k.S('hook.note');
      weatherMap(k, {
        fronts: [{kind: 'warm', at: tRaised, dur: 2, x0: -0.05, x1: 1.05}],
        icons: [['hvac', 'sun', -1, `HVAC ${n.hvac.shown}`], ['q', 'cloud', tYou, 'YOUR SHOP?']],
      });
      // the cover breathes after frame 0: sparks off the HVAC sun at 1 s, a ping as "raised" is said
      const [sx, sy] = [(14 + ICONS.hvac[0] * 332) * 3, (82 + ICONS.hvac[1] * 150) * 3];
      k.burst(sx, sy, 1.0, {n: 14, r: 180}); k.burst(sx, sy, tRaised, {n: 18, r: 220});
      const pf = d.fr(tRaised); if (pf >= 0 && pf < 12) { const g = 8 + pf * 2, cx = sx / 3, cy = sy / 3; d.P(cx - g, cy - g, 2 * g + 1, 1, CREAM); d.P(cx - g, cy + g, 2 * g + 1, 1, CREAM); d.P(cx - g, cy - g, 1, 2 * g + 1, CREAM); d.P(cx + g, cy - g, 1, 2 * g + 1, CREAM); }
      // the hook card in the panel: settled on frame 0
      k.text(n.hvac.shown, 384, 426, {size: 132, color: 'accent', align: 'center', drop: INK});
      k.text('of HVAC companies raised', 72, 792, {size: 66, color: CREAM, drop: INK});
      if (T < tNote) k.text('prices last year.', 72, 866, {size: 66, color: CREAM, drop: INK});
      else { k.slam('The note that tells your customers.', 72, 880, tNote, {size: 39, color: 'accent', from: 0.5, drop: INK}); k.sweep(72, 926, 640, 6, tNote + 0.25, {color: 'accent'}); }
      k.text(`Jobber survey, ${n.owners.shown} home service owners, ${n.field.shown}`, 72, 944, {size: 30, color: SAND});
      if (T < tRaised) return {host: false, speech: false};
      if (T < tNote) return {host: false};
      return host(k, k.live('hook.note') ? 'point' : null);
    },

    // ---- stakes: the same map; the survey's size, the 65%, then a sun per trade as it is named, cleaning a cloud
    stakes: (k, T) => {
      const n = k.data.numbers, t0 = k.S('stakes'), tAll = wordT(k, 'stakes.all', /^Sixty/i), t74 = wordT(k, 'stakes.74', /^Seventy/i);
      const tPl = wordT(k, 'stakes.trades', /^Plumbing/i), tEl = wordT(k, 'stakes.trades', /^electrical/i), tRf = wordT(k, 'stakes.trades', /^roofing/i);
      const tCl = wordT(k, 'stakes.clean', /^Cleaning/i), t55 = wordT(k, 'stakes.clean', /^fifty/i, 1.2);
      weatherMap(k, {
        fronts: [{kind: 'warm', at: tAll, dur: 2.2, x0: -0.05, x1: 1.05}],
        icons: [['hvac', 'sun', -1, `HVAC ${n.hvac.shown}`], ['plumb', 'sun', tPl, T >= t74 ? `PLUMB ${n.plumb.shown}` : 'PLUMB'],
          ['elec', 'sun', tEl, T >= t74 ? `ELEC ${n.elec.shown}` : 'ELEC'], ['roof', 'sun', tRf, T >= t74 ? `ROOF ${n.roof.shown}` : 'ROOF'],
          ['clean', 'cloud', tCl, T >= t55 ? `CLEAN ${n.clean.shown}` : 'CLEAN']],
      });
      [['plumb', t74], ['elec', t74 + 0.1], ['roof', t74 + 0.2], ['clean', t55]].forEach(([key, at]) => k.burst((14 + ICONS[key][0] * 332 + 30) * 3, (82 + ICONS[key][1] * 150) * 3, at, {n: 10, r: 140}));
      // the panel: the source types on, then the 65% and what it is
      const src = `Jobber: ${n.owners.shown} home service owners, Dec ${n.field.shown}`, typed = src.slice(0, Math.max(0, d0(k, t0 + 0.2)));
      k.text(typed, 72, 798, {size: 30, color: SAND, lint: typed.length === src.length});
      if (T >= tAll) {
        k.slam(cnt(k, n.all, tAll, {suffix: '%'}), 72, 840, tAll, {size: 132, color: 'accent', from: 0.5, drop: INK});
        k.slam('of them raised prices.', 360, 850, tAll + 0.3, {size: 39, color: CREAM, from: 0.4});
        if (T >= t55) k.slam(`Cleaning, the lowest: ${n.clean.shown}`, 360, 906, t55, {size: 39, color: GOLD, from: 0.4});
        else if (T >= t74) k.slam(`Plumbing, electrical, roofing: ${n.plumb.shown}`, 360, 906, t74, {size: 39, color: GOLD, from: 0.4});
        else if (T >= tPl) k.slam('Plumbing, electrical, roofing', 360, 906, tPl, {size: 39, color: GOLD, from: 0.4});
      } else k.slam('Who raised prices last year?', 72, 860, t0 + 0.4, {size: 66, color: CREAM, from: 0.5, drop: INK});
      return host(k, k.live('stakes.74') || k.live('stakes.clean') ? 'point' : (k.live('stakes') ? 'clip' : null));
    },

    // ---- why: the register rings up the reasons, then (drawer open, coins raining) the BLS pay lines
    why: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('why');
      const tInf = wordT(k, 'why.inflation', /^inflation/i), tLab = wordT(k, 'why.labor', /^Half/i), tFed = k.S('why.federal');
      const tRep = wordT(k, 'why.repair', /^three/i, 3.2), tAll = wordT(k, 'why.all', /^Three/i, 0.9);
      const items = [{label: 'INFLATION', amount: 72, at: tInf, show: n.inflation.shown}, {label: 'LABOR', amount: 50, at: tLab, show: n.labor.shown},
        {label: 'REPAIR PAY', amount: 3.7, at: tRep, show: n.repair.shown}, {label: 'ALL PAY', amount: 3.2, at: tAll, show: n.allPay.shown}];
      const shown = items.filter((it) => T >= it.at), cur = shown[shown.length - 1];
      // the set prints its own amounts and a running sum; the brief has no sum, so the till's text is swapped for each
      // line's own figure (with its % sign) and the display shows the line just rung
      const real = k.text, byAmt = {'72.0': n.inflation.shown, '50.0': n.labor.shown, '3.7': n.repair.shown, '3.2': n.allPay.shown};
      k.text = function (s, x, y, o) { if (x === 552 && byAmt[s]) return real.call(this, byAmt[s], x, y, o); if (x === 948) return; return real.call(this, s, x, y, o); };
      try {
        k.sets.register({items: items.map(({label, amount, at}) => ({label, amount, at})), prefix: '', dec: 1, openAt: tFed, displayLabel: cur && items.indexOf(cur) >= 2 ? 'PAY' : 'REASON'});
      } finally { k.text = real; }
      const val = cur ? cur.show : '--', size = d.tw(val, 66) <= 86 ? 66 : 39;
      d.tx(val, 316, 152 - (size >= 52 ? 11 : 6), {size, color: TEAL, align: 'right'});
      if (Math.floor(T * 2) % 2) d.P(318, 144, 2, 16, TEAL);   // the display's cursor blinks twice a second: the till is live
      // the HUD: coins rain into the open drawer, and again as each pay line prints
      if (T >= tFed) k.sets.hud({coins: {at: tFed + 0.1, dur: Math.max(1.4, k.E('why') - tFed - 0.8), n: 34, x0: 222, x1: 320, floor: 288}});   // a steady drip into the drawer
      if (T >= tRep) k.sets.hud({coins: {at: tRep, dur: 1.0, n: 10, x0: 230, x1: 320, floor: 288}});
      if (T >= tAll) k.sets.hud({coins: {at: tAll, dur: 1.0, n: 10, x0: 230, x1: 320, floor: 288}});
      // the plate on the wall above the receipt: what is being rung up, and whose numbers
      d.win(16, 84, 198, 42, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
      if (T < tFed) {
        k.slam('Why they raised prices', 66, 264, t0 + 0.2, {size: 39, color: CREAM, from: 0.4});
        k.text('Jobber survey, reasons named', 66, 318, {size: 30, color: SAND});
      } else {
        k.slam('Federal pay data', 66, 264, tFed, {size: 39, color: GOLD, from: 0.4});
        k.text(`BLS, ${n.months.shown} months to June 2026`, 66, 318, {size: 30, color: SAND});
      }
      return host(k, k.live('why.federal') ? 'point' : (k.live('why.inflation') || k.live('why.labor') ? 'clip' : null));
    },

    // ---- note: the price note types on a letterhead as it is said; the turn lights the last line and stamps it
    note: (k, T) => {
      const d = px(k), t0 = k.S('note'), tSkip = k.S('note.skip'), tLast = k.S('note.last'), tProm = wordT(k, 'note.promise', /^promise/i), tNext = k.S('note.next');
      desk(k);
      // the letterhead slides up onto the desk; header band, EXAMPLE tag
      const open = d.ease(t0 + 0.15, 8, 160), X = 16, Y = 84 + open, W = 296, H = 168;
      d.clip(0, 0, 360, 286, () => {
        d.P(X + 3, Y + 3, W, H, '#1A332B'); d.P(X - 1, Y - 1, W + 2, H + 2, INK); d.P(X, Y, W, H, CREAM); d.P(X + W - 3, Y, 3, H, SAND);
        d.P(X, Y, W, 18, '#7A3442'); d.P(X, Y + 17, W, 1, INK);
        const head = T >= tSkip ? 'THE PART PEOPLE SKIP' : 'YOUR PRICE NOTE (EXAMPLE)', hs = T >= tSkip ? tSkip : -1;
        if (hs < 0 || d.fr(hs) >= 3) d.tx(head, X + 8, Y + 3, {color: hs >= 0 ? GOLD : CREAM, lint: open === 0}); else d.dith(X + 8, Y + 4, 200, 11, '#3D2E45');
      });
      const n = k.data.numbers, rows = [
        {text: 'Starting the first of next month, our rates go up.', at: k.S('note.l1')},
        {text: 'Our labor and material costs rose this year.', at: k.S('note.l2')},
        {text: "Anything you've already approved stays at the price we quoted.", at: k.S('note.l3')},
      ];
      let lastY = 0, last0 = 0;
      if (open === 0) {
        let y = (84 + 24) * 3;
        rows.forEach((r, i) => {
          const dim = T >= tLast && i < rows.length - 1;
          k.shape(k.rectPts(72, y + 3, 33, 39, 0), {fill: T >= r.at ? (dim ? SAND : GOLD) : '#E6D3BC', line: false});
          k.text(String(i + 1), 88, y + 3, {size: 39, color: INK, align: 'center'});
          const times = spoken(r.at, r.text), words = r.text.split(/\s+/), sp = k.measure(' ', {size: 39});
          let x = 126, yy = y, lines = 1;
          if (i === rows.length - 1) last0 = y;
          words.forEach((wd, j) => {
            const ww = k.measure(wd, {size: 39});
            if (x + ww > 900 && x > 126) { x = 126; yy += 45; lines++; }
            const [ws, we] = times[j] || [1e9, 1e9];
            if (T < ws) k.shape(k.rectPts(x, yy + 33, ww, 3, 0), {fill: '#E6D3BC', line: false});
            else k.text(wd, x, yy, {size: 39, color: T < we + 0.05 ? '#B07A47' : (dim ? '#6B7080' : '#2B2033')});
            x += ww + sp;
          });
          y += lines * 45 + 12; lastY = y;
        });
        // the turn: a gold bar under the last line, then the PROMISE stamp in the sheet's lower right, clear of the words
        if (T >= tLast) k.sweep(126, lastY - 12, 760, 6, tLast + 0.1, {color: 'accent'});
        if (T >= tProm - 0.1) k.slam('PROMISE', 880, lastY + 24, tProm, {size: 66, color: RED, align: 'right', stamp: true, glint: false});
        if (T >= tProm) k.burst(760, lastY + 50, tProm + 0.05, {n: 16, r: 200});
      }
      // under the sheet, over the desk: the rule in two lines (right of the host)
      if (T >= tNext) {
        d.win(100, 284, 216, 38, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#7A3442'});
        k.slam('Raise the next job.', 324, 868, tNext, {size: 39, color: GOLD, from: 0.4});
        k.slam('Never an approved one.', 324, 916, tNext + 0.4, {size: 39, color: CREAM, from: 0.4});
      }
      const r = host(k, k.live('note.last') || k.live('note.next') ? 'point' : null);
      if (T >= k.S('note.l1') - 0.05 && T < tSkip - 0.05) r.speech = false;   // the sheet is the dialog while the note is said
      return r;
    },

    // ---- caveat: the map again, ONE HONEST NOTE; a cold front, a "?" cloud for how customers took it
    caveat: (k, T) => {
      const n = k.data.numbers, t0 = k.S('caveat'), tSell = k.S('caveat.sells'), tShow = k.S('caveat.shows'), tTook = k.S('caveat.took'), tWatch = k.S('caveat.watch');
      weatherMap(k, {title: 'ONE HONEST NOTE', fronts: [{kind: 'cold', at: t0 + 0.2, dur: 2.4, x0: 1.05, x1: -0.05}],
        icons: allTrades(n).concat([['q', 'cloud', tTook, 'CUSTOMERS?']])});
      if (T < tWatch) {
        if (T >= tSell) k.slam('Jobber sells software.', 72, 796, tSell, {size: 39, color: CREAM, from: 0.4});
        else k.slam('Where the numbers come from', 72, 796, t0 + 0.3, {size: 39, color: SAND, from: 0.4});
        if (T >= tShow) k.slam('Its survey: who raised prices.', 72, 852, tShow, {size: 39, color: GOLD, from: 0.4});
        if (T >= tTook) k.slam('Not how customers took it.', 72, 908, tTook, {size: 39, color: 'accent', from: 0.4});
      } else {
        k.slam('Watch your close rate', 72, 800, tWatch, {size: 66, color: CREAM, from: 0.5, drop: INK});
        k.slam('for a month after.', 72, 874, tWatch + 0.3, {size: 66, color: 'accent', from: 0.5, drop: INK});
      }
      return host(k, k.live('caveat.took') ? 'shrug' : (k.live('caveat.watch') ? 'point' : null));
    },

    // ---- close: every sun up, coins rain over the map; one column: the line, the send line, the ask
    close: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('close'), most = k.S('close.most'), send = k.S('close.send'), rs = k.S('close.reason');
      weatherMap(k, {noTitle: true, fronts: [{kind: 'warm', at: t0 + 0.1, dur: 2.2, x0: -0.05, x1: 1.05}], icons: allTrades(n)});
      k.sets.hud({coins: {at: t0 + 0.2, dur: 2.6, n: 26, x0: 20, x1: 330, floor: 200}});
      if (T >= rs) k.sets.hud({coins: {at: rs, dur: 1.6, n: 18, x0: 20, x1: 330, floor: 200}});
      // the column: a game window over the map's lower half and the panel, one left edge (x 120), everything above y 930
      const open = d.ease(t0 + 0.25, 8, 110);
      d.clip(0, 0, 360, 334, () => d.win(14, 226 + open, 332, 104, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#7A3442'}));
      if (open === 0) {
        k.slam('Your costs went up.', 120, 696, t0 + 0.3, {size: 66, color: 'accent', from: 0.5, drop: INK});
        if (T >= most) k.slam('Most trades already raised prices.', 120, 772, most, {size: 39, color: CREAM, from: 0.4});
        if (T >= send) {
          k.chip('ProofNotFluff', 120, 820, {size: 30});
          k.slam('Send this to whoever writes your quotes.', 120, 880, send + 0.1, {size: 39, color: CREAM, from: 0.4});
        }
        if (T >= rs) { k.slam('Raise yours with a reason.', 120, 928, rs, {size: 39, color: GOLD, from: 0.5, drop: INK}); k.sweep(120, 970, 560, 6, rs + 0.3, {color: 'accent'}); }
      }
      return host(k, k.live('close.reason') ? 'wave' : (k.live('close.send') ? 'point' : null));
    },
  },
};

// characters typed since t0, two a frame (a typed source line)
function d0(k, t0) { return Math.floor((k.T - t0) * 60); }
