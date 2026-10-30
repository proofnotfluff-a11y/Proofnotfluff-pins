// Scene: Raise your prices; most trades already did (Lesson 6, Pricing Clinic, arcade). One function per top-level cue in
// 03_cues/cues.md. Numbers only from k.data (brief.md -> data.js). Every time comes from a cue start (k.S) or a spoken word
// (wordT), so a re-voiced take moves the picture with it.
/* Worlds (brief.md): hook, stakes, caveat = the weather map (PRICE REPORT, a sun per trade); why = the register with the
   HUD's coins; note = the boss fight (k.sets.boss): the note is the move list against PRICE PUSHBACK;
   close = the calendar (NEXT MONTH, the note going out). */
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
const ICONS = {hvac: [0.07, 0.24], elec: [0.40, 0.24], plumb: [0.07, 0.55], roof: [0.07, 0.86], q: [0.40, 0.86], shop: [0.62, 0.86]};
/* o.panelY moves our panel up (the hook: over the title strip, so the sentence sits right under the big 83%) */
const weatherMap = (k, o) => {
  const icons = (o.icons || []).map(([key, kind, at, label]) => ({kind, x: ICONS[key][0], y: ICONS[key][1], at, label}));
  /* the strip's month letters sit under our panel, and on the hook the title too: neither is drawn */
  mute(k, (s, x, y) => (y === 915 && String(s).length === 1) || (o.noTitle && y === 732),
    () => k.sets.weather({title: o.title || 'PRICE REPORT', fronts: o.fronts || [], icons, months: []}));
  const d = px(k), py = o.panelY || 262;
  d.win(14, py, 332, 330 - py, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
};
/* every trade the voice names, settled (for the sections after the stakes) */
const allTrades = (n) => [['hvac', 'sun', -1, `HVAC ${n.hvac.shown}`], ['elec', 'sun', -1, `ELEC ${n.elec.shown}`], ['plumb', 'sun', -1, `PLUMB ${n.plumb.shown}`],
  ['roof', 'sun', -1, `ROOF ${n.roof.shown}`]];
/* one source format everywhere (hook, stakes) */
const SRC = (n) => `Jobber, ${n.owners.shown} home service owners, Dec ${n.field.shown}`;

// ================================================================================================================
// our own copy of the player's dialog box (same box, tail, name tag and typing) for one stretch where the player's
// paging would open on the note's last word: it shows only the words said from t0 on, until t1
const speechOwn = (k, T, t0, t1) => {
  const ws = WS().filter((w) => w.start >= t0 && w.start < t1);
  if (!ws.length) return;
  const x = 372, y = 1046, w = 560, h = 190, pad = 30, maxX = x + w - pad, o = {size: 39, weight: 600, font: 'body'};
  k.shape(k.rectPts(x + 10, y + 10, w, h, 0), {fill: '#120D14', line: false, alpha: 0.6});
  k.shape(k.rectPts(x, y, w, h, 0), {fill: 'bubble', stroke: null, lw: 2});
  k.shape(k.rectPts(x + 6, y + 6, w - 12, h - 12, 0), {stroke: 'bubbleText', lw: 6, line: false});
  k.shape([[x + 2, y + h - 70], [x - 40, y + h - 40], [x + 2, y + h - 30]], {fill: 'bubble', line: false});
  k.chip(window.SCENE.host_name || 'Snow', x + 24, y - 34, {size: 30, fill: 'tag', color: 'tagText'});
  const sp = k.measure(' ', o); let cx = x + pad, cy = y + 26;
  ws.forEach((wd) => {
    const ww = k.measure(wd.w, o);
    if (cx + ww > maxX && cx > x + pad) { cx = x + pad; cy += Math.round(39 * 1.18); }
    if (T >= wd.start) k.text(wd.w, cx, cy, Object.assign({}, o, {color: T < wd.end + 0.05 ? 'tag' : 'bubbleText'}));
    cx += ww + sp;
  });
  if ((T * 2) % 1 < 0.5) k.shape([[x + w - 52, y + h - 40], [x + w - 28, y + h - 40], [x + w - 40, y + h - 26]], {fill: 'bubbleText', line: false});
};

// ================================================================================================================
// the close-up (hook, from "raised" to "Did"): the weather map drawn at three times, the HVAC sun big in the middle of
// the frame (whole pixels: one low-res pixel = 9 frame units). The map's land runs out to the title plate's left edge
// (x 42), so the shot has one left edge. A warm front of big bright-red domes sweeps the land the whole time (our own,
// drawn at the zoom; the set's thin maroon one read as a crack). The sun's own label is not drawn at that size (it would
// run off the frame): ours sits beside the sun at heading size. The claim and its source ride on a title plate up top,
// the source well clear of the plate's inner border, and the segment tag at its top right.
const SUN_AT = [483, 860];   /* where the HVAC sun lands on screen in the close-up (the map's blue edge then sits at x 42) */
const warmFront = (d, x) => {
  for (let y = 82; y < 232; y++) { const fx = x + Math.round(5 * Math.sin((y - 82) * 0.06)); d.P(fx - 1, y, 1, 1, '#7A3442'); d.P(fx, y, 3, 1, RED); }
  for (let yc = 94; yc < 232; yc += 32) {
    const fx = x + Math.round(5 * Math.sin((yc - 82) * 0.06)) + 3;
    [[10, INK], [9, ORANGE], [7, RED]].forEach(([r, c]) => { for (let j = -r; j <= r; j++) d.P(fx, yc + j, Math.round(Math.sqrt(r * r - j * j)) + (r === 10 ? 1 : 0), 1, c); });
  }
};
const sunClose = (k, t0, t1) => {
  const n = k.data.numbers, d = px(k), c = k.ctx, sx = (14 + ICONS.hvac[0] * 332) * 3, sy = (82 + ICONS.hvac[1] * 150) * 3;
  c.save(); c.translate(SUN_AT[0], SUN_AT[1]); c.scale(3, 3); c.translate(-Math.round(sx / 3) * 3, -Math.round(sy / 3) * 3);
  mute(k, () => true, () => k.sets.weather({title: 'PRICE REPORT', fronts: [], icons: [{kind: 'sun', x: ICONS.hvac[0], y: ICONS.hvac[1], at: -1}], months: []}));
  /* the land runs left past the map's own edge (same dither phase), with the map's ink and blue rim moved out with it */
  d.P(-13, 79, 1, 156, INK); d.P(-12, 80, 2, 154, '#3B82C4');
  d.P(-10, 82, 24, 150, '#3E7A62'); d.dith(-10, 82, 24, 150, '#2F5A4A');
  /* the front: linear, so it is still moving on the cut back out */
  const p = clamp((k.T - t0) / Math.max(0.3, t1 - t0));
  d.clip(-10, 82, 346, 150, () => warmFront(d, Math.round(-24 + 136 * p)));
  /* the sun on top of the front */
  const x0 = Math.round(14 + ICONS.hvac[0] * 332), y0 = Math.round(82 + ICONS.hvac[1] * 150), ro = Math.floor(k.T * 2) % 2;
  d.disc(x0, y0, 7, '#B07A47'); d.disc(x0, y0, 6, ORANGE); d.disc(x0 - 1, y0 - 1, 4, GOLD);
  for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4 + (ro ? Math.PI / 8 : 0); d.P(x0 + Math.round(Math.cos(a) * 10), y0 + Math.round(Math.sin(a) * 10), 2, 2, GOLD); }
  c.restore();
  k.text('HVAC', SUN_AT[0] + 120, SUN_AT[1] - 36, {size: 66, color: CREAM, drop: INK});
  /* the title plate: the claim and its source (the source's descenders end about 31 px above the inner border) */
  d.win(14, 84, 332, 140, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
  k.chip('Pricing Clinic', 640, 276, {size: 30, fill: 'accent', color: INK});
  k.text(n.hvac.shown, 72, 276, {size: 132, color: 'accent', drop: INK});
  k.text('of HVAC companies raised', 72, 432, {size: 66, color: CREAM, drop: INK});
  k.text('prices last year.', 72, 506, {size: 66, color: CREAM, drop: INK});
  k.text(SRC(n), 72, 590, {size: 30, color: SAND});
};

// the weather desk under the map on the wide hook (the cover's lower third is no longer an empty floor): a presenter's
// desk with a sun emblem, no words. Snow stands in front of it once the hook cuts in.
const studioDesk = (k) => {
  const d = px(k), {P, disc} = d;
  P(22, 346, 316, 2, INK); P(22, 348, 316, 5, '#D9A066'); P(22, 348, 316, 1, GOLD); P(22, 353, 316, 2, '#6B4226');
  P(28, 355, 304, 60, INK); P(29, 355, 302, 59, '#7A3442'); P(29, 355, 34, 59, '#5A2A35'); P(297, 355, 34, 59, '#5A2A35');
  P(36, 362, 288, 1, GOLD); P(36, 406, 288, 1, GOLD);
  disc(180, 384, 12, '#B07A47'); disc(180, 384, 11, ORANGE); disc(179, 383, 7, GOLD);
  const ro = Math.floor(k.T * 2) % 2;
  for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4 + (ro ? Math.PI / 8 : 0); P(180 + Math.round(Math.cos(a) * 17) - 1, 384 + Math.round(Math.sin(a) * 17) - 1, 3, 3, GOLD); }
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 6',
  transitions: {stakes: 'dissolve', why: 'levelselect', note: 'iris', caveat: 'dissolve', close: 'gameover'},
  trauma: {'note.promise': 0.8},
  sections: {
    // ---- hook: three shots (IMPROVE 00a: the picture changes by 1 s and twice by 3 s, Snow on by 1 s). The cover: the
    // weather map, the 83% big and centered in the open land, its sentence and source in the panel, PRICING CLINIC on the
    // panel's edge, the weather desk below (frame 0, held still to "raised"); no host or dialog. Cut in on "raised" to the
    // close-up: the map at three times on the HVAC sun, a bright warm front sweeping the land, the claim on a title plate up
    // top, Snow big at the lower left. Cut back out on "Did" to the whole map: the front finishes, the sun's label reads
    // HVAC 83%, the "?" cloud asks about your shop, and just before "Here's the note" the panel clears.
    hook: (k, T) => {
      const n = k.data.numbers, d = px(k), tYou = k.S('hook.you');
      /* the panel clears about 0.15 s before "Here's" (the on-screen hook holds under 4.0 s) */
      const tNote = wordT(k, 'hook.note', /^Here/i, 0) - 0.15;
      const tIn = Math.min(0.8, Math.max(0.45, wordT(k, 'hook', /^raised/i, 0.65))), tOut = Math.min(2.6, wordT(k, 'hook.you', /^Did/i, 2.5));
      if (T >= tIn && T < tOut) {
        sunClose(k, tIn, tOut);
        return {hostPose: k.talking() ? 'talk' : 'point', hostScale: 0.8, hostX: 170};
      }
      weatherMap(k, {noTitle: true, panelY: 236,
        fronts: [{kind: 'warm', at: tIn + 0.1, dur: 2.2, x0: -0.05, x1: 1.05}],
        icons: [['hvac', 'sun', -1, T >= tOut ? `HVAC ${n.hvac.shown}` : 'HVAC'], ['shop', 'cloud', tYou, 'YOUR SHOP?']],
      });
      studioDesk(k);
      const [sx, sy] = [(14 + ICONS.hvac[0] * 332) * 3, (82 + ICONS.hvac[1] * 150) * 3];
      k.burst(sx, sy, tOut, {n: 18, r: 220});
      const pf = d.fr(tOut); if (pf >= 0 && pf < 12) { const g = 8 + pf * 2, cx = sx / 3, cy = sy / 3; d.P(cx - g, cy - g, 2 * g + 1, 1, CREAM); d.P(cx - g, cy + g, 2 * g + 1, 1, CREAM); d.P(cx - g, cy - g, 1, 2 * g + 1, CREAM); d.P(cx + g, cy - g, 1, 2 * g + 1, CREAM); }
      /* the cover, settled on frame 0: the 83% about 560 px wide, centered in the map's open land left of the lake (the one
         dominant number); its sentence in the panel under it, the block centered in the panel; the segment tag on the
         panel's top edge; on "Here's the note" the panel clears to the one headline, centered */
      k.text(n.hvac.shown, 345, 360, {size: 396, color: 'accent', drop: INK, align: 'center'});   // its box starts under the HVAC label
      k.chip('Pricing Clinic', 668, 684, {size: 30, fill: 'accent', color: INK});
      if (T < tNote) {
        k.text('of HVAC companies raised', 72, 738, {size: 66, color: CREAM, drop: INK});
        k.text('prices last year.', 72, 812, {size: 66, color: CREAM, drop: INK});
        k.text(SRC(n), 72, 912, {size: 30, color: SAND});
      } else {
        k.slam('The note that tells', 72, 762, tNote, {size: 66, color: 'accent', from: 0.5, drop: INK});
        k.slam('your customers.', 72, 836, tNote + 0.15, {size: 66, color: CREAM, from: 0.5, drop: INK});
        k.sweep(72, 918, 420, 6, tNote + 0.35, {color: 'accent'});
      }
      /* the cover frame has no host; Snow and the dialog box come in on the cut and stay */
      if (T < tIn) return {host: false, speech: false};
      return host(k, k.live('hook.note') ? 'point' : null);
    },

    /* ---- stakes: the same map; the 65% and the survey under it, then a sun per trade as it is named */
    stakes: (k, T) => {
      const n = k.data.numbers, t0 = k.S('stakes'), tAll = wordT(k, 'stakes.hvac', /^Eighty/i), t74 = wordT(k, 'stakes.74', /^seventy/i);
      const tPl = wordT(k, 'stakes.trades', /^Plumbing/i), tEl = wordT(k, 'stakes.trades', /^electrical/i), tRf = wordT(k, 'stakes.trades', /^roofing/i);
      weatherMap(k, {
        fronts: [{kind: 'warm', at: tAll, dur: 2.2, x0: -0.05, x1: 1.05}],
        icons: [['hvac', 'sun', -1, `HVAC ${n.hvac.shown}`], ['plumb', 'sun', tPl, T >= t74 ? `PLUMB ${n.plumb.shown}` : 'PLUMB'],
          ['elec', 'sun', tEl, T >= t74 ? `ELEC ${n.elec.shown}` : 'ELEC'], ['roof', 'sun', tRf, T >= t74 ? `ROOF ${n.roof.shown}` : 'ROOF']],
      });
      [['plumb', t74], ['elec', t74 + 0.1], ['roof', t74 + 0.2]].forEach(([key, at]) => k.burst((14 + ICONS[key][0] * 332 + 30) * 3, (82 + ICONS[key][1] * 150) * 3, at, {n: 10, r: 140}));
      /* the panel: the headline first (the question, then the HVAC 83% and the trades), the source under it */
      const [hx, hy] = [(14 + ICONS.hvac[0] * 332 + 30) * 3, (82 + ICONS.hvac[1] * 150) * 3];
      k.burst(hx, hy, tAll + 0.1, {n: 12, r: 160});
      /* on "seventy-four" the big number swaps to 74% at the same size as the 83%, over its own label, and the HVAC line
         drops under it */
      if (T >= t74) {
        k.slam(cnt(k, n.plumb, t74, {suffix: '%'}), 72, 798, t74, {size: 132, color: 'accent', from: 0.5, drop: INK});
        k.slam('Plumbing, electrical, roofing', 300, 812, t74 + 0.1, {size: 39, color: CREAM, from: 0.4});
        k.slam(`HVAC companies: ${n.hvac.shown}`, 300, 862, t74 + 0.3, {size: 39, color: GOLD, from: 0.4});
      } else if (T >= tAll) {
        k.slam(cnt(k, n.hvac, tAll, {suffix: '%'}), 72, 798, tAll, {size: 132, color: 'accent', from: 0.5, drop: INK});
        k.slam('of HVAC companies did.', 300, 812, tAll + 0.3, {size: 39, color: CREAM, from: 0.4});
        if (T >= tPl) k.slam('Plumbing, electrical, roofing', 300, 862, tPl, {size: 39, color: GOLD, from: 0.4});
      } else k.slam('Who raised prices last year?', 72, 806, t0 + 0.4, {size: 66, color: CREAM, from: 0.5, drop: INK});
      const src = SRC(n), typed = src.slice(0, Math.max(0, d0(k, t0 + 0.2)));
      k.text(typed, 72, 932, {size: 30, color: SAND, lint: typed.length === src.length});
      return host(k, k.live('stakes.74') ? 'point' : (k.live('stakes') ? 'clip' : null));
    },

    // ---- why: the register rings up the reasons, then (drawer open, coins raining) the BLS pay lines
    why: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('why');
      /* the 72% rings on "Seventy-two" (the number), not on "inflation" */
      const tInf = wordT(k, 'why', /^Seventy/i), tLab = wordT(k, 'why.labor', /^half/i), tFed = k.S('why.federal');
      const tRep = wordT(k, 'why.repair', /^three/i, 3.0), tCrew = k.S('why.crew'), tAll = wordT(k, 'why.crew', /^three/i, 1.2), crew = T >= tCrew;
      /* the receipt is tagged by source: a JOBBER SURVEY line over its two reasons, a BLS PAY DATA line over the pay lines */
      const SJ = 'JOBBER SURVEY', SB = 'BLS PAY DATA';
      const items = [{label: SJ, amount: 0, at: t0 + 0.3, src: true}, {label: 'INFLATION', amount: 72, at: tInf, show: n.inflation.shown},
        {label: 'LABOR', amount: 50, at: tLab, show: n.labor.shown}, {label: SB, amount: 0, at: tFed, src: true},
        {label: 'REPAIR PAY', amount: 3.7, at: tRep, show: n.repair.shown}, {label: 'ALL PAY', amount: 3.2, at: tAll, show: n.allPay.shown}];
      const rung = items.filter((it) => !it.src && T >= it.at), cur = rung[rung.length - 1];
      /* the set prints its own amounts and a running sum; the brief has no sum, so each amount is swapped for the line's
         own figure (with its % sign), the source lines print no amount, and the display shows the line just rung */
      const real = k.text, byAmt = {'72.0': n.inflation.shown, '50.0': n.labor.shown, '3.7': n.repair.shown, '3.2': n.allPay.shown};
      k.text = function (s, x, y, o) {
        if (x === 552) return byAmt[s] ? real.call(this, byAmt[s], x, y, o) : undefined;
        if (x === 168 && (s === SJ || s === SB)) return real.call(this, s, x, y, Object.assign({}, o, {color: '#7A3442'}));
        if (x === 948) return;
        return real.call(this, s, x, y, o);
      };
      try {
        k.sets.register({items: items.map(({label, amount, at}) => ({label, amount, at})), prefix: '', dec: 1, openAt: tFed,
          displayLabel: crew ? 'REPAIR PAY' : (cur && /PAY/.test(cur.label) ? 'PAY' : 'REASON')});
      } finally { k.text = real; }
      /* the display: right edge at x 918 (inside the 930 safe edge), no cursor */
      const val = crew ? n.repair.shown : (cur ? cur.show : '--'), size = d.tw(val, 66) <= 76 ? 66 : 39;
      d.tx(val, 306, 152 - (size >= 52 ? 11 : 6), {size, color: TEAL, align: 'right'});
      /* once ALL PAY has printed (after "That beat the three"): a gold line under REPAIR PAY (the receipt holds 6 lines by
         then, top at y 136) */
      const tLine = tAll + 0.3;
      if (T >= tLine) d.P(56, 136 + 6 + 4 * 18 + 15, Math.min(128, Math.round(128 * eo(d.fr(tLine) / 8))), 2, ORANGE);
      /* the shop floor: dark planks, staggered seams, a baseboard (the set's checker tiles read as a transparency grid) */
      d.P(0, 417, 360, 223, '#3D2E45'); d.P(0, 417, 360, 3, '#1B1420');
      for (let y = 420, r = 0; y < 640; y += 12, r++) { d.P(0, y + 11, 360, 1, '#2B2033'); for (let x = (r * 53) % 96; x < 360; x += 96) d.P(x, y, 1, 11, '#2B2033'); }
      /* the HUD: coins drop into the open drawer, drawn only between the display and the drawer (never over the display,
         the plate or the HUD bar) */
      d.clip(0, 182, 360, 118, () => {
        if (T >= tFed) k.sets.hud({coins: {at: tFed + 0.1, dur: Math.max(1.4, k.E('why') - tFed - 0.8), n: 34, x0: 222, x1: 320, floor: 288}});
        if (T >= tRep) k.sets.hud({coins: {at: tRep, dur: 1.0, n: 10, x0: 230, x1: 320, floor: 288}});
        if (T >= tAll) k.sets.hud({coins: {at: tAll, dur: 1.0, n: 10, x0: 230, x1: 320, floor: 288}});
      });
      /* the plate on the wall above the receipt: what is being rung up. The heading at heading size, the source a size
         step under it in the source sand (the pixel font has no body size under 30, so the step is made on the heading) */
      d.win(16, 84, 198, 50, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
      if (T < tFed) {
        k.slam('Why they raised prices', 66, 268, t0 + 0.2, {size: 66, color: CREAM, from: 0.4, drop: INK});
        k.text('Jobber survey, reasons named', 66, 338, {size: 30, color: SAND});
      } else {
        if (crew) k.slam('Repair pay beat all pay', 66, 268, tCrew, {size: 66, color: GOLD, from: 0.4, drop: INK});
        else k.slam('Federal pay data', 66, 268, tFed, {size: 66, color: GOLD, from: 0.4, drop: INK});
        k.text(`BLS, ${n.months.shown} months to June 2026`, 66, 338, {size: 30, color: SAND});
      }
      return host(k, k.live('why.federal') || k.live('why.crew') ? 'point' : (k.live('why') || k.live('why.labor') ? 'clip' : null));
    },

    // ---- note: the boss fight (k.sets.boss, not used in the two lessons before or the two after). The objection is
    // PRICE PUSHBACK; the price note is the move list, a game window that types each line as it is said. Lines 1 and 2
    // each land a hit as they finish; "That last line" rings line 3 in gold; "is a promise" is the big hit, PROMISE
    // stamping on the boss beside line 3. No defeat and no damage numbers (the note does not end pushback; the caveat
    // says the survey doesn't show how customers took it). On "Raise the next job" the rule lands on a card on the arena
    // floor.
    note: (k, T) => {
      const d = px(k), t0 = k.S('note'), tSkip = k.S('note.skip'), tLast = k.S('note.last'), tProm = wordT(k, 'note.promise', /^promise/i), tNext = k.S('note.next');
      const tThat = wordT(k, 'note.last', /^That/i, 0), WRAP = 505, sp = k.measure(' ', {size: 39});
      const rows = [
        {text: 'Starting the first of next month, our rates go up.', at: k.S('note.l1'), y: 134},
        {text: 'Our labor and material costs rose this year.', at: k.S('note.l2'), y: 168},
        {text: "Anything you've already approved stays at the price we quoted.", at: k.S('note.l3'), y: 202},
      ].map((r) => {
        const times = spoken(r.at, r.text), lay = []; let x = 0, line = 0;
        r.text.split(/\s+/).forEach((wd, j) => { const ww = k.measure(wd, {size: 39}); if (x > 0 && x + ww > WRAP) { x = 0; line++; } lay.push({wd, x, line, t: times[j]}); x += ww + sp; });
        return Object.assign(r, {lay, lines: line + 1, tEnd: times[times.length - 1][1]});
      });
      /* the set: its own move labels, menu tag and damage numbers are not drawn (our window carries the note) */
      mute(k, (s) => /^-\d+$/.test(String(s)) || String(s) === 'MOVES', () => k.sets.boss({name: 'PRICE PUSHBACK', hp: 100, t0: t0 + 0.3, menu: 'MOVES',
        hits: [{at: rows[0].tEnd, dmg: 20, label: ''}, {at: rows[1].tEnd, dmg: 20, label: ''}, {at: tProm, dmg: 40, label: ''}]}));
      /* the move window, over the set's menu and clear of the boss's arm */
      d.win(14, 122, 192, 138, {});
      const head = T >= tSkip ? 'THE PART PEOPLE SKIP' : 'YOUR PRICE NOTE (EXAMPLE)', tw = d.tw(head);
      d.P(22, 116, tw + 12, 14, INK); d.P(23, 117, tw + 10, 12, '#7A3442');
      if (T < tSkip || d.fr(tSkip) >= 3) d.tx(head, 29, 117, {color: T >= tSkip ? GOLD : CREAM}); else d.dith(29, 118, tw, 10, '#3D2E45');
      const next = rows.findIndex((r) => T < r.tEnd);
      rows.forEach((r, i) => {
        const on = T >= r.at;
        d.tx(String(i + 1), 20, r.y, {color: on ? GOLD : '#6B7080'});
        if (i === next && T >= t0 + 0.3) { const b = (d.F >> 3) & 1; d.P(15 + b, r.y + 3, 2, 7, GOLD); d.P(17 + b, r.y + 4, 1, 5, GOLD); }
        r.lay.forEach((L) => {
          const ly = r.y + L.line * 15;
          if (T < L.t[0]) { d.P(30 + Math.round(L.x / 3), ly + 11, Math.round(k.measure(L.wd, {size: 39}) / 3), 1, '#3D2E45'); return; }
          k.text(L.wd, 90 + L.x, ly * 3, {size: 39, color: T < L.t[1] + 0.05 ? GOLD : CREAM});
        });
      });
      /* the turn: line 3 ringed and swept in gold */
      const r3 = rows[2], y3 = r3.y - 3, h3 = r3.lines * 15 + 2;
      if (T >= tLast) {
        const g = ORANGE; d.P(27, y3, 172, 1, g); d.P(27, y3 + h3, 172, 1, g); d.P(27, y3, 1, h3 + 1, g); d.P(198, y3, 1, h3 + 1, g);
        k.sweep(84, (y3 + h3 + 3) * 3, 510, 6, tLast + 0.1, {color: 'accent'});
      }
      /* the promise lands as the big hit: PROMISE stamps on the boss, beside line 3 */
      if (T >= tProm - 0.1) {
        const yy = (y3 + h3 / 2) * 3 - 33;
        k.stampIn(tProm, () => {
          k.shape(k.rectPts(678, yy - 6, 216, 72, 0), {stroke: RED, lw: 6, line: false});
          k.text('PROMISE', 786, yy, {size: 66, color: RED, align: 'center', drop: INK});
        }, {at: [786, yy + 66]});
      }
      /* the rule on a card on the arena floor */
      if (T >= tNext) {
        const up = d.ease(tNext, 6, 10);
        d.win(14, 264 + up, 332, 58, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#7A3442'});
        if (up === 0) {
          k.slam('Raise the next job.', 540, 808, tNext, {size: 66, color: GOLD, from: 0.4, drop: INK, align: 'center'});
          if (T >= tNext + 0.4) k.slam('Never an approved one.', 540, 882, tNext + 0.4, {size: 66, color: CREAM, from: 0.4, drop: INK, align: 'center'});
        }
      }
      const r = host(k, k.live('note.last') || k.live('note.next') ? 'point' : null);
      /* the move window is the dialog while the note is said; then, until "That last line", our own box carries "Here's
         the part people skip." (the player's box would open on the note's last word and its closing quote) */
      if (T >= k.S('note.l1') - 0.05 && T < tThat - 0.05) r.speech = false;
      if (T >= tSkip - 0.05 && T < tThat - 0.05) speechOwn(k, T, tSkip - 0.05, tThat - 0.05);
      return r;
    },

    // ---- caveat: the map again, ONE HONEST NOTE; a cold front, a "?" cloud for how customers took it
    caveat: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('caveat'), tSell = k.S('caveat.sells'), tTook = k.S('caveat.took'), tWatch = k.S('caveat.watch');
      weatherMap(k, {title: 'ONE HONEST NOTE', fronts: [{kind: 'cold', at: t0 + 0.2, dur: 2.4, x0: 1.05, x1: -0.05}],
        icons: allTrades(n).concat([['q', 'cloud', tTook, 'CUSTOMERS?']])});
      /* the panel's text block is centered in it (top inset about 27 px, as on the stakes panel): one line in the middle,
         then on "doesn't show" it steps up to make room for the two more */
      if (T < tWatch) {
        const y1 = T < tTook ? 867 : 867 - Math.round(48 * eo(d.fr(tTook) / 6));
        if (T >= tSell) k.slam('Jobber sells software.', 72, y1, tSell, {size: 39, color: CREAM, from: 0.4});
        else k.slam('Where the numbers come from', 72, y1, t0 + 0.3, {size: 39, color: SAND, from: 0.4});
        if (T >= tTook + 0.2) k.slam("Its survey doesn't show", 72, 867, tTook + 0.2, {size: 39, color: GOLD, from: 0.4});
        if (T >= tTook + 0.45) k.slam('how customers took it.', 72, 915, tTook + 0.45, {size: 39, color: 'accent', from: 0.4});
      } else {
        k.slam('Watch your close rate', 72, 818, tWatch, {size: 66, color: CREAM, from: 0.5, drop: INK});
        k.slam('for a month after.', 72, 892, tWatch + 0.3, {size: 66, color: 'accent', from: 0.5, drop: INK});
      }
      return host(k, k.live('caveat.took') ? 'shrug' : (k.live('caveat.watch') ? 'point' : null));
    },

    /* ---- close: the calendar, NEXT MONTH (the note's "first of next month"): day 1 fills gold with a coin, the note
       window rises over the lower rows; on the send line an envelope flies from the window to day 1, which takes a
       check (the note going out). One column, one left edge (x 120); "Raise yours with a reason." the largest line. */
    close: (k, T) => {
      const d = px(k), t0 = k.S('close'), most = k.S('close.most'), send = k.S('close.send'), rs = k.S('close.reason');
      const tMark = t0 + 0.3, tFly = send + 0.3, FLY = 12, tLand = tFly + FLY / 30;
      const fills = [{day: 1, at: tMark, c: GOLD, mark: 'coin'}];
      if (T >= tLand) fills.push({day: 1, at: tLand, c: GOLD, mark: 'check'});
      /* the note window rises from the desk over rows 2 to 4 (rows 0 and 1, with day 1, stay in view); the day numbers
         it covers are not drawn (hidden text still counts for lint) */
      const open = d.ease(t0 + 0.25, 8, 120), WY = 182;
      const cal = mute(k, (s, x, y) => /^\d+$/.test(String(s)) && y >= (WY + open) * 3,
        () => k.sets.calendar({month: 'NEXT MONTH', start: 2, days: 30, fills, weeks: [{row: 0, at: tMark}]}));
      const [cx, cy, cw, ch] = cal.cell(1).map((v) => v / 3);
      d.clip(0, 0, 360, 334, () => d.win(14, WY + open, 332, 118, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#7A3442'}));
      if (open === 0) {
        if (T >= send) k.chip('ProofNotFluff', 120, WY * 3 - 22, {size: 30});
        k.slam('Your costs went up.', 120, 600, t0 + 0.3, {size: 39, color: CREAM, from: 0.4});
        if (T >= most) k.slam('Most trades already raised prices.', 120, 652, most, {size: 39, color: CREAM, from: 0.4});
        if (T >= send) k.slam('Send this to whoever writes your quotes.', 120, 704, send + 0.1, {size: 39, color: CREAM, from: 0.4});
        if (T >= rs) { k.slam('Raise yours with a reason.', 120, 768, rs, {size: 66, color: GOLD, from: 0.5, drop: INK}); k.sweep(120, 848, 621, 6, rs + 0.3, {color: 'accent'}); }
      }
      /* the envelope: out of the window's top right, an arc on whole pixels, into day 1 */
      const f = d.fr(tFly);
      if (f >= 0 && f < FLY) {
        const p = eo(f / FLY), sx = 300, sy = WY + 6, ex = cx + cw / 2 - 10, ey = cy + ch / 2 - 8;
        k.sets.icon('mail', Math.round(sx + (ex - sx) * p), Math.round(sy + (ey - sy) * p - 24 * Math.sin(Math.PI * p)), 2);
      }
      if (T >= rs) k.burst((cx + cw / 2) * 3, (cy + ch / 2) * 3, rs + 0.05, {n: 16, r: 180});
      return host(k, k.live('close.reason') ? 'wave' : (k.live('close.send') ? 'point' : null));
    },
  },
};

// characters typed since t0, two a frame (a typed source line)
function d0(k, t0) { return Math.floor((k.T - t0) * 60); }
