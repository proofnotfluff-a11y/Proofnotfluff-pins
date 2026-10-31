// Sets: full-screen retro game set pieces (_shared/sets.md). Loaded after kit.js; every kit object gets k.sets (alias
// k.set), so a scene calls k.sets.street({...}) the way it calls k.room('garage'). Each set draws a whole world (or one
// large animated element) on the low-res grid: 360 x 640 pixels, one pixel is 3 frame units, 3-tone shading from the
// arcade palette, and every move steps in whole pixels on whole frames. Every set is a pure function of T (any frame
// renders on its own), settles fully by its t0 (put t0 <= 0 for a cover frame), and returns where its content area is,
// so scene text never lands on its decor, the host (bottom left) or the dialog box.
// Layout rules all sets share (low-res pixels; frame units = x 3):
//   y 0..56 under the Reel's top bar (decor only), y 56..72 the player's HUD, y 84..270 the content band (full width),
//   y 270..322 content only right of x 96 (the host stands at x 36..92 from y 273), y 322..417 the dialog box's band
//   (calm decor), y 417..640 the floor (scenery under the Reel's caption area).
(function () {
  const TAU = Math.PI * 2;
  const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const easeOut = (x) => 1 - Math.pow(1 - clamp(x), 3);
  // the arcade palette in ramps (light, base, shade, deep)
  const RAMP = {
    wood: ['#D9A066', '#B07A47', '#8C5A33', '#6B4226', '#4A2E1B'], gold: ['#F7C873', '#F2A541', '#B07A47'],
    red: ['#E2633B', '#7A3442', '#3D2E45'], teal: ['#6FB7A8', '#2F6F67', '#245752'], green: ['#3E7A62', '#2F5A4A', '#24453A', '#1A332B'],
    blue: ['#87CEEB', '#3B82C4', '#253048'], sky: ['#BDE6F5', '#87CEEB', '#5B8FB9'], steel: ['#C9CCD3', '#9AA0AD', '#6B7080', '#4A4E5A'],
    cream: ['#FFF7EA', '#F4E6D3', '#E6D3BC', '#B39A88'], plum: ['#3D2E45', '#2B2033', '#1B1420', '#120D14'], brown: ['#7A4E2C', '#5A3A22'],
  };
  const INK = '#120D14';

  function build(k) {
    const ctx = k.ctx, C = k.C, T = k.T, F = Math.floor(T * 30 + 0.005);
    const col = (c) => (c && C[c]) ? C[c] : c;
    // ---- the pixel primitives (low-res units) ----
    const P = (x, y, w, h, c) => { x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h); if (w > 0 && h > 0 && c) { ctx.fillStyle = col(c); ctx.fillRect(x * 3, y * 3, w * 3, h * 3); } };
    const DOT = (x, y, c) => P(x, y, 1, 1, c);
    const dith = (x, y, w, h, c, ph = 0) => { ctx.fillStyle = col(c); for (let j = 0; j < h; j++) for (let i = (j + ph) & 1; i < w; i += 2) ctx.fillRect((Math.round(x) + i) * 3, (Math.round(y) + j) * 3, 3, 3); };
    const disc = (cx, cy, r, c) => { for (let dy = -r; dy <= r; dy++) { const hw = Math.floor(Math.sqrt(r * r - dy * dy) + 0.4); P(cx - hw, cy + dy, 2 * hw + 1, 1, c); } };
    const ring = (cx, cy, r, c, th = 1) => { for (let dy = -r; dy <= r; dy++) { const ho = Math.floor(Math.sqrt(r * r - dy * dy) + 0.4), ri = r - th, hi = Math.abs(dy) <= ri ? Math.floor(Math.sqrt(ri * ri - dy * dy) + 0.4) : -1; if (hi < 0) P(cx - ho, cy + dy, 2 * ho + 1, 1, c); else { P(cx - ho, cy + dy, ho - hi, 1, c); P(cx + hi + 1, cy + dy, ho - hi, 1, c); } } };
    const line = (x0, y0, x1, y1, c, th = 1) => {
      x0 = Math.round(x0); y0 = Math.round(y0); x1 = Math.round(x1); y1 = Math.round(y1);
      const dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1; let e = dx + dy;
      for (let n = 0; n < 2000; n++) { P(x0, y0, th, th, c); if (x0 === x1 && y0 === y1) break; const e2 = 2 * e; if (e2 >= dy) { e += dy; x0 += sx; } if (e2 <= dx) { e += dx; y0 += sy; } }
    };
    const linePts = (pts) => {   // every pixel along a polyline, in order (for lines that draw on)
      const out = [];
      for (let s = 0; s + 1 < pts.length; s++) {
        let [x0, y0] = pts[s].map(Math.round); const [x1, y1] = pts[s + 1].map(Math.round);
        const dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1; let e = dx + dy;
        for (let n = 0; n < 2000; n++) { if (!out.length || out[out.length - 1][0] !== x0 || out[out.length - 1][1] !== y0) out.push([x0, y0]); if (x0 === x1 && y0 === y1) break; const e2 = 2 * e; if (e2 >= dy) { e += dy; x0 += sx; } if (e2 <= dx) { e += dx; y0 += sy; } }
      }
      return out;
    };
    // a box lit from the top left: outline, base, a light top and left edge, a dark bottom and right edge
    const bevel = (x, y, w, h, base, hi, lo, out) => { if (out) P(x - 1, y - 1, w + 2, h + 2, out); P(x, y, w, h, base); P(x, y, w, 1, hi); P(x, y, 1, h, hi); P(x, y + h - 1, w, 1, lo); P(x + w - 1, y + 1, 1, h - 1, lo); };
    // a game window: drop shadow, outline, a notched fill, a light inner rule
    const win = (x, y, w, h, o = {}) => {
      const base = o.base || '#253048', hi = o.hi || '#3B82C4', lo = o.lo || '#1B1420', rule = o.rule || '#87CEEB';
      if (o.shadow !== false) P(x + 2, y + 2, w, h, '#120D14');
      P(x + 1, y, w - 2, h, INK); P(x, y + 1, w, h - 2, INK);
      P(x + 1, y + 1, w - 2, h - 2, base); P(x + 2, y + 1, w - 4, 1, hi); P(x + 1, y + 2, 1, h - 4, hi); P(x + 2, y + h - 2, w - 4, 1, lo); P(x + w - 2, y + 2, 1, h - 4, lo);
      if (rule) { P(x + 3, y + 3, w - 6, 1, rule); P(x + 3, y + h - 4, w - 6, 1, rule); P(x + 3, y + 3, 1, h - 6, rule); P(x + w - 4, y + 3, 1, h - 6, rule); }
    };
    const fr = (t0) => Math.floor((T - t0) * 30 + 0.005);   // whole frames since t0 (negative before)
    const ease = (t0, frames, dist) => Math.round(dist * (1 - easeOut(fr(t0) / frames)));   // a slide that lands on whole pixels
    const tx = (s, x, y, o = {}) => k.text(s, x * 3, y * 3, Object.assign({size: 39}, o));   // text at a low-res point
    const tw = (s, size = 39) => k.measure(String(s), {size}) / 3;
    const th = (size = 39) => (size >= 52 ? 22 * Math.max(1, Math.round(size / 66)) : 13 * Math.max(1, Math.round(size / 39)));
    const clip = (x, y, w, h, fn) => { ctx.save(); ctx.beginPath(); ctx.rect(x * 3, y * 3, w * 3, h * 3); ctx.clip(); fn(); ctx.restore(); };
    // a sprite from strings: each character a palette key, '.' clear; s is a whole-number scale
    const spr = (rows, pal, x, y, s = 1, flip = false) => rows.forEach((r, j) => { for (let i = 0; i < r.length; i++) { const c = pal[r[i]]; if (c) P(x + (flip ? r.length - 1 - i : i) * s, y + j * s, s, s, c); } });
    const x2 = (x, y, fn) => { ctx.save(); ctx.translate(Math.round(x) * 3, Math.round(y) * 3); ctx.scale(2, 2); fn(); ctx.restore(); };   // a whole-number 2x, still on the grid
    const area = (x, y, w, h) => ({x: x * 3, y: y * 3, w: w * 3, h: h * 3});
    // a spinning coin, 8 x 8, four frames (face, turning, edge, turning)
    const coin = (x, y, f) => {
      const ws = [4, 3, 1, 3][((f % 4) + 4) % 4];
      for (let j = 0; j < 8; j++) { const dy = j - 3.5, hw = Math.max(0, Math.round(ws * Math.sqrt(Math.max(0, 1 - (dy * dy) / 16)))); if (!hw) continue; P(x + 4 - hw, y + j, 2 * hw, 1, '#B07A47'); if (hw > 1) P(x + 4 - hw + 1, y + j, 2 * hw - 2, 1, j < 4 ? '#F7C873' : '#F2A541'); }
      if (ws >= 3) { P(x + 4, y + 2, 1, 4, '#B07A47'); DOT(x + 3, y + 2, '#FFF7EA'); }
    };
    // a four-point twinkle, three sizes, cycling
    const twinkle = (x, y, f, c = '#FFF7EA') => { const s = [0, 1, 2, 1][((f % 4) + 4) % 4]; DOT(x, y, c); for (let i = 1; i <= s; i++) { DOT(x - i, y, c); DOT(x + i, y, c); DOT(x, y - i, c); DOT(x, y + i, c); } };
    // a pixel cloud from bumps; the underside in shade
    const cloud = (x, y, w, seed) => {
      const n = Math.max(2, Math.round(w / 9));
      for (let i = 0; i < n; i++) { const r = 3 + Math.round(hash(seed + i * 1.71) * 3) + (i > 0 && i < n - 1 ? 2 : 0); disc(x + Math.round((i + 0.5) * w / n), y - r + 6, r, '#FFF7EA'); }
      P(x + 2, y + 3, w - 4, 3, '#FFF7EA'); P(x + 3, y + 5, w - 6, 1, '#E6D3BC'); P(x + 4, y + 6, w - 8, 1, '#C9CCD3');
    };
    const sky3 = (y0, h, top = '#5B8FB9', mid = '#87CEEB', low = '#BDE6F5') => { const a = Math.round(h * 0.4), b = Math.round(h * 0.75); P(0, y0, 360, a, top); P(0, y0 + a, 360, b - a, mid); P(0, y0 + b, 360, h - b, low); dith(0, y0 + a, 360, 2, top, 1); dith(0, y0 + b, 360, 2, mid, 1); };
    const tiles = (y0, h, a, b, s = 16, joint = null) => { for (let y = y0, r = 0; y < y0 + h; y += s, r++) for (let x = 0, c = 0; x < 360; x += s, c++) { P(x, y, s, s, (r + c) % 2 ? a : b); if (joint) P(x, y, s, 1, joint); } };
    const planks = (y0, h, base, hi, lo, seed = 3) => { for (let y = y0, i = 0; y < y0 + h; y += 9, i++) { P(0, y, 360, 9, base); P(0, y, 360, 1, hi); P(0, y + 8, 360, 1, lo); const off = Math.floor(hash(i * 3.3 + seed) * 70); for (let x = off % 70; x < 360; x += 70) P(x, y + 1, 1, 7, lo); } };

    const S = {};

    // ================================================================================================================
    // 1. street: a side-scrolling street level. The world scrolls past the van in parallax layers (sky, skyline, houses,
    // road, the fence up front), each on whole pixels at its own speed; at stopAt the van brakes and parks, the job sign
    // slides in with the houses and lands beside it. o: {t0, speed (road pixels a frame, 1), stopAt, stopDur (0.8),
    // sign ('JOB'), van (true)}. Content: the sky, y 84..200.
    S.street = function (o = {}) {
      const t0 = o.t0 || 0, v = 30 * (o.speed || 1), sd = o.stopDur || 0.8;
      const posAt = (t) => { let d = Math.max(0, t - t0); if (o.stopAt == null) return v * d; const ds = Math.max(0, o.stopAt - t0); if (d <= ds) return v * d; const e = Math.min(d - ds, sd); return v * ds + v * (e - e * e / (2 * sd)); };
      const pos = posAt(T), moving = T >= t0 && (o.stopAt == null || T < o.stopAt + sd);
      const off = (m) => Math.floor(pos * m);
      sky3(0, 214);
      // the sun: a lit disc, its rays stepping every half second
      disc(322, 30, 12, '#F2A541'); disc(321, 29, 11, '#F7C873'); DOT(317, 25, '#FFF7EA'); DOT(318, 24, '#FFF7EA');
      const rs = Math.floor(T * 2) % 2;
      for (let i = 0; i < 8; i++) { const a = i * TAU / 8 + (rs ? TAU / 16 : 0); P(322 + Math.round(Math.cos(a) * 17), 30 + Math.round(Math.sin(a) * 17), 2, 2, '#F7C873'); }
      // clouds drift (a pixel every 10 frames, plus the world's scroll at a tenth)
      [[40, 96, 34, 1], [150, 130, 24, 5], [250, 104, 30, 9], [380, 150, 22, 3]].forEach(([x, y, w, s]) => { const span = 420; const xx = ((x - off(0.1) - Math.floor(F / 10)) % span + span) % span - 40; cloud(xx, y, w, s); });
      // the far skyline, a quarter speed
      const so = off(0.25);
      for (let i = Math.floor(so / 22) - 1; i < Math.floor(so / 22) + 18; i++) {
        const bw = 14 + Math.floor(hash(i * 2.1) * 10), bh = 22 + Math.floor(hash(i * 5.7) * 46) + (i % 7 === 0 ? 30 : 0), x = i * 22 - so;
        P(x, 236 - bh, bw, bh, '#5B8FB9'); P(x, 236 - bh, 1, bh, '#87CEEB');
        for (let wy = 236 - bh + 4; wy < 230; wy += 6) for (let wx = x + 3; wx < x + bw - 2; wx += 4) if (hash(i * 9 + wx * 0.7 + wy) > 0.55) DOT(wx, wy, '#87CEEB');
        if (i % 7 === 0) P(x + Math.floor(bw / 2), 236 - bh - 8, 1, 8, '#5B8FB9');
      }
      P(0, 236, 360, 4, '#3E7A62'); dith(0, 235, 360, 1, '#3E7A62');
      // the houses, half speed: Chicago two-flats, frame houses with gables, trees between, a mailbox at each walk
      const ho = off(0.5), SP = 100;
      const house = (x, i) => {
        const kind = Math.floor(hash(i * 3.7) * 3), w = 70 + Math.floor(hash(i * 1.9) * 12);
        const pal = [['#E2633B', '#7A3442', '#3D2E45'], ['#E6D3BC', '#B39A88', '#6B4226'], ['#6FB7A8', '#2F6F67', '#245752'], ['#87CEEB', '#3B82C4', '#253048']][Math.floor(hash(i * 8.3) * 4)];
        const top = kind === 0 ? 216 : 228, bot = 292;
        if (kind === 0) {   // a brick two-flat: flat roof, a cornice, bay windows
          P(x - 1, top - 1, w + 2, bot - top + 1, INK); P(x, top, w, bot - top, '#7A3442');
          for (let y = top + 6; y < bot; y += 4) for (let bx = x + ((y >> 2) & 1) * 3; bx < x + w; bx += 6) P(bx, y, 5, 1, '#E2633B');
          P(x - 3, top - 4, w + 6, 4, '#E6D3BC'); P(x - 3, top - 4, w + 6, 1, '#FFF7EA'); P(x - 3, top - 1, w + 6, 1, '#B39A88');
        } else {   // a frame house: siding, a stepped gable roof
          P(x - 1, top - 1, w + 2, bot - top + 1, INK); P(x, top, w, bot - top, pal[0]);
          for (let y = top + 3; y < bot; y += 4) P(x, y, w, 1, pal[1]);
          P(x + w - 2, top, 2, bot - top, pal[1]);
          const rh = 22;
          for (let r = 0; r < rh; r++) { const hw = Math.round((w / 2 + 4) * (r / rh)); P(x + w / 2 - hw - 1, top - rh + r, 2 * hw + 2, 1, INK); P(x + w / 2 - hw, top - rh + r, 2 * hw, 1, r % 4 === 0 ? '#5A3A22' : '#7A4E2C'); }
          P(x - 4, top - 1, w + 8, 2, '#5A3A22');
          if (kind === 2) { P(x + w - 18, top - rh + 2, 6, 10, INK); P(x + w - 17, top - rh + 3, 4, 9, '#7A3442'); }
        }
        // windows with a glint, a door with a step
        const wins = kind === 0 ? [[8, 10], [w - 26, 10], [8, 38], [w - 26, 38]] : [[8, 16], [w - 26, 16]];
        wins.forEach(([wx, wy]) => { P(x + wx - 1, top + wy - 1, 20, 16, INK); P(x + wx, top + wy, 18, 14, '#E6D3BC'); P(x + wx + 1, top + wy + 1, 16, 12, '#87CEEB'); P(x + wx + 1, top + wy + 1, 16, 4, '#BDE6F5'); P(x + wx + 8, top + wy + 1, 2, 12, '#E6D3BC'); DOT(x + wx + 3, top + wy + 3, '#FFF7EA'); P(x + wx - 1, top + wy + 14, 20, 2, '#FFF7EA'); });
        const dx = x + Math.floor(w / 2) - 6;
        P(dx - 1, bot - 25, 14, 25, INK); P(dx, bot - 24, 12, 24, kind === 0 ? '#5A3A22' : pal[2]); P(dx + 2, bot - 21, 8, 8, kind === 0 ? '#7A4E2C' : pal[1]); DOT(dx + 9, bot - 12, '#F7C873');
        P(dx - 4, bot - 1, 20, 2, '#C9CCD3');
        // a mailbox on a post at the walk
        if (hash(i * 4.4) > 0.35) { const mx = x + w + 6; P(mx + 3, bot - 12, 2, 12, '#5A3A22'); P(mx - 1, bot - 19, 10, 8, INK); P(mx, bot - 18, 8, 6, '#3B82C4'); P(mx, bot - 18, 8, 1, '#87CEEB'); P(mx + 8, bot - 22, 1, 6, '#E2633B'); P(mx + 8, bot - 22, 3, 2, '#E2633B'); }
        // a tree between the houses
        const tx0 = x + w + 20; P(tx0 + 4, bot - 18, 3, 18, '#5A3A22'); disc(tx0 + 5, bot - 28, 10, '#24453A'); disc(tx0 + 4, bot - 29, 9, '#2F5A4A'); disc(tx0 + 2, bot - 31, 5, '#3E7A62'); DOT(tx0, bot - 33, '#6FB7A8');
      };
      for (let i = Math.floor(ho / SP) - 1; i < Math.floor(ho / SP) + 5; i++) house(i * SP - ho, i);
      // the job sign: it rides in with the houses and lands beside the van when it parks
      if (o.stopAt != null && o.sign !== false) {
        const hoStop = Math.floor(posAt(o.stopAt + sd + 1) * 0.5), sx = 112 + hoStop - ho;
        const label = o.sign || 'JOB', w = Math.max(30, Math.ceil(tw(label)) + 10), hop = T >= o.stopAt + sd && T < o.stopAt + sd + 0.2 ? [2, 2, 1, 1, 0, 0][Math.min(5, fr(o.stopAt + sd))] : 0;
        if (sx > -60 && sx < 380) {
          P(sx + 4, 270 - hop, 2, 22 + hop, '#6B4226'); P(sx + w - 6, 270 - hop, 2, 22 + hop, '#6B4226');
          P(sx - 1, 249 - hop, w + 2, 22, INK); P(sx, 250 - hop, w, 20, '#FFF7EA'); P(sx + 1, 251 - hop, w - 2, 1, '#E2633B'); P(sx + 1, 268 - hop, w - 2, 1, '#E2633B'); P(sx, 269 - hop, w, 1, '#E6D3BC');
          tx(label, sx + w / 2, 254 - hop, {align: 'center', color: '#7A3442'});
          if (T >= o.stopAt + sd + 0.2) { const ay = 236 + ((F >> 3) & 1), ax = Math.round(sx + w / 2); for (let j = 0; j < 6; j++) P(ax - 5 + j, ay + j, 11 - 2 * j, 1, j === 0 ? '#F7C873' : '#F2A541'); P(ax - 2, ay - 6, 5, 6, '#F2A541'); P(ax - 2, ay - 6, 1, 6, '#F7C873'); }
        }
      }
      // the sidewalk, its seams at house speed
      P(0, 292, 360, 10, '#C9CCD3'); P(0, 292, 360, 1, '#FFF7EA'); for (let x = -(ho % 16); x < 360; x += 16) P(x, 293, 1, 9, '#9AA0AD');
      P(0, 302, 360, 2, '#6B7080'); P(0, 304, 360, 1, INK);
      // the road, full speed: lane dashes
      P(0, 305, 360, 46, '#4A4E5A'); dith(0, 305, 360, 2, '#6B7080', 1);
      const ro = off(1); for (let x = -(ro % 28); x < 360; x += 28) { P(x, 327, 14, 2, '#F7C873'); }
      for (let x = -((ro * 3 + 7) % 53); x < 360; x += 53) DOT(x, 340, '#6B7080');
      // the van
      if (o.van !== false) {
        const bob = moving ? ((F >> 2) & 1) : 0, vx = 194, vy = 284 + bob;
        x2(vx, vy, () => S.van(0, 0, {wheel: moving ? (F >> 1) & 1 : 0}));
        if (moving) for (let i = 0; i < 3; i++) { const a = (F + i * 6) % 18; P(vx - 4 - a, vy + 50 - Math.floor(a / 4), 3 + (a > 9 ? 1 : 0), 3, a > 9 ? '#9AA0AD' : '#C9CCD3'); }
      }
      // the near curb, the front walk, a picket fence at one and a half speed
      P(0, 351, 360, 3, '#9AA0AD'); P(0, 351, 360, 1, '#C9CCD3'); P(0, 354, 360, 12, '#C9CCD3'); P(0, 354, 360, 1, '#FFF7EA');
      const fo = off(1.5); P(0, 366, 360, 51, '#2F5A4A'); dith(0, 366, 360, 3, '#24453A');
      P(0, 372, 360, 2, '#E6D3BC'); P(0, 380, 360, 2, '#E6D3BC');
      for (let x = -(fo % 10); x < 360; x += 10) { P(x, 362, 5, 26, INK); P(x + 1, 361, 3, 26, '#FFF7EA'); DOT(x + 2, 360, '#FFF7EA'); P(x + 3, 363, 1, 24, '#E6D3BC'); }
      // the lawn below: grass tufts at fence speed
      P(0, 388, 360, 252, '#2F5A4A');
      for (let i = 0; i < 90; i++) { const gx = ((Math.floor(hash(i * 2.3) * 400) - fo) % 400 + 400) % 400 - 20, gy = 392 + Math.floor(hash(i * 7.9) * 240); DOT(gx, gy, '#3E7A62'); DOT(gx + 1, gy - 1, '#3E7A62'); DOT(gx + 2, gy, '#24453A'); }
      return {area: area(20, 84, 296, 116), van: [194 * 3, 284 * 3]};
    };
    // the work van, 72 x 34 (facing right): white body, an orange stripe, a ladder on the roof, wheels whose hubs turn
    S.van = function (x, y, o = {}) {
      P(x + 2, y + 32, 68, 2, '#1B1420');
      P(x - 1, y + 3, 54, 27, INK); P(x + 52, y + 9, 19, 21, INK); P(x + 54, y + 7, 12, 2, INK);
      P(x, y + 4, 52, 25, '#FFF7EA'); P(x, y + 4, 52, 1, '#FFFFFF'); P(x, y + 24, 52, 5, '#E6D3BC'); P(x, y + 28, 70, 1, '#B39A88');
      P(x + 52, y + 10, 18, 19, '#FFF7EA'); P(x + 53, y + 8, 12, 2, '#FFF7EA'); P(x + 52, y + 24, 18, 5, '#E6D3BC');
      P(x + 56, y + 11, 11, 8, '#253048'); P(x + 57, y + 11, 10, 7, '#5B8FB9'); P(x + 58, y + 12, 3, 1, '#BDE6F5'); P(x + 58, y + 13, 1, 2, '#BDE6F5');
      P(x + 68, y + 21, 2, 3, '#F7C873'); P(x + 70, y + 25, 1, 3, '#9AA0AD');
      P(x + 2, y + 16, 66, 4, '#F2A541'); P(x + 2, y + 16, 66, 1, '#F7C873'); P(x + 2, y + 19, 66, 1, '#B07A47');
      P(x + 30, y + 6, 1, 18, '#C9CCD3'); P(x + 22, y + 21, 5, 1, '#9AA0AD');   // the side door seam and handle
      P(x + 4, y + 1, 40, 1, '#9AA0AD'); P(x + 4, y + 2, 40, 1, '#6B7080'); for (let i = 6; i < 44; i += 6) P(x + i, y, 1, 3, '#9AA0AD');   // ladder
      [[x + 12, y + 29], [x + 58, y + 29]].forEach(([wx, wy]) => { disc(wx, wy, 5, INK); disc(wx, wy, 3, '#4A4E5A'); DOT(wx, wy, '#C9CCD3'); if (o.wheel) { DOT(wx - 1, wy - 1, '#9AA0AD'); DOT(wx + 1, wy + 1, '#9AA0AD'); } else { DOT(wx, wy - 2, '#9AA0AD'); DOT(wx, wy + 2, '#9AA0AD'); } });
    };

    // ================================================================================================================
    // 2. dispatch: a dispatch board on the wall, a city grid with the lake on the right and the river; pins drop in and
    // ping, routes draw on along the streets with a van at the head. Positions are 0..1 across the map.
    // o: {pins: [{x, y, at, c}], routes: [{pts: [[x, y], ...], at, dur}], t0}. Returns {map, at(x, y) -> frame point, area}.
    S.dispatch = function (o = {}) {
      P(0, 0, 360, 417, '#2B2033'); for (let x = 0; x < 360; x += 30) { P(x, 0, 1, 417, '#1B1420'); P(x + 1, 0, 1, 417, '#3D2E45'); }
      const X = 18, Y = 82, W = 324, H = 196;
      P(X - 5, Y - 5, W + 10, H + 10, INK); bevel(X - 4, Y - 4, W + 8, H + 8, '#6B7080', '#C9CCD3', '#4A4E5A'); P(X - 1, Y - 1, W + 2, H + 2, '#4A4E5A');
      clip(X, Y, W, H, () => {
        P(X, Y, W, H, '#E6D3BC');
        // blocks with roofs
        for (let by = Y; by < Y + H; by += 22) for (let bx = X; bx < X + W; bx += 22) { const r = hash(bx * 0.37 + by * 1.3); for (let j = 0; j < 3; j++) { const rx = bx + 4 + Math.floor(hash(r * 9 + j) * 10), ry = by + 4 + Math.floor(hash(r * 7 + j * 3) * 10); P(rx, ry, 4, 3, '#B39A88'); P(rx, ry, 4, 1, '#F4E6D3'); } }
        // the park
        P(X + 178, Y + 132, 40, 38, '#3E7A62'); dith(X + 178, Y + 132, 40, 38, '#2F5A4A'); [[8, 8], [24, 12], [14, 26], [30, 28]].forEach(([a, b]) => { disc(X + 178 + a, Y + 132 + b, 3, '#24453A'); DOT(X + 177 + a, Y + 131 + b, '#6FB7A8'); });
        // the river, winding down from the top
        for (let y = Y; y < Y + H; y++) { const rx = X + 96 + Math.round(10 * Math.sin((y - Y) * 0.045)) + Math.round((y - Y) * 0.2); P(rx - 1, y, 9, 1, '#5B8FB9'); P(rx, y, 7, 1, '#87CEEB'); }
        // streets every 22 pixels, an avenue on the diagonal
        for (let x = X + 20; x < X + W; x += 22) { P(x, Y, 3, H, '#FFF7EA'); P(x + 3, Y, 1, H, '#C9CCD3'); }
        for (let y = Y + 20; y < Y + H; y += 22) { P(X, y, W, 3, '#FFF7EA'); P(X, y + 3, W, 1, '#C9CCD3'); }
        line(X, Y + 150, X + 210, Y, '#F7C873', 2);
        // the lake, its shore, a ripple that steps
        for (let y = Y; y < Y + H; y++) { const sx = X + 270 + Math.round(5 * Math.sin(y * 0.11) + 3 * hash(Math.floor(y / 6))); P(sx, y, X + W - sx, 1, '#3B82C4'); DOT(sx, y, '#87CEEB'); }
        for (let i = 0; i < 14; i++) { const ry = Y + 8 + i * 14, rx = X + 286 + ((i * 7 + Math.floor(F / 10)) % 30); P(rx, ry, 4, 1, '#87CEEB'); }
      });
      const at = (nx, ny) => [X + nx * W, Y + ny * H];
      // routes: the line draws on pixel by pixel, a van rides its head, then the dashes march
      (o.routes || []).forEach((r, ri) => {
        if (T < r.at) return;
        const pts = linePts(r.pts.map(([a, b]) => at(a, b))), n = Math.floor(pts.length * clamp((T - r.at) / (r.dur || 1)));
        for (let i = 0; i < n; i++) { const done = n >= pts.length; if (((i + (done ? Math.floor(F / 3) : 0)) % 8) < 5) { P(pts[i][0] - 2, pts[i][1] - 1, 4, 4, '#7A3442'); P(pts[i][0] - 2, pts[i][1] - 2, 4, 3, r.c || '#E2633B'); } }
        if (n > 0 && n < pts.length) { const [hx, hy] = pts[n - 1]; P(hx - 7, hy - 6, 15, 10, INK); P(hx - 6, hy - 5, 13, 8, '#FFF7EA'); P(hx - 6, hy - 1, 13, 2, '#F2A541'); P(hx + 2, hy - 5, 4, 3, '#5B8FB9'); DOT(hx - 4, hy + 3, INK); DOT(hx + 4, hy + 3, INK); }
      });
      // pins: drop with a bounce, a shadow, one ping ring
      (o.pins || []).forEach((p, i) => {
        const f = fr(p.at); if (f < 0) return;
        const [px, py] = at(p.x, p.y).map(Math.round), dy = [-20, -14, -8, -3, 0, -3, -1, 0][Math.min(7, f)], c = p.c || '#E2633B';
        if (f >= 4) { P(px - 3, py + 1, 7, 2, '#B39A88'); }
        if (f >= 6 && f < 24) ring(px, py, 4 + Math.floor((f - 6) / 2), c);
        P(px - 1, py - 8 + dy, 2, 9, '#4A4E5A'); DOT(px - 1, py - 8 + dy, '#9AA0AD');
        disc(px, py - 12 + dy, 7, INK); disc(px, py - 12 + dy, 6, c); disc(px + 1, py - 11 + dy, 4, c === '#E2633B' ? '#7A3442' : '#245752'); disc(px - 1, py - 13 + dy, 4, c); P(px - 3, py - 15 + dy, 2, 2, '#FFF7EA');
        if (p.n != null && f >= 6) tx(String(p.n), px, py - 18, {align: 'center', color: '#FFF7EA', lint: false});
      });
      // the console below: a desk edge, a radio with a lamp that blinks once a second, a mug that steams on fours
      P(0, 300, 360, 4, '#8C5A33'); P(0, 300, 360, 1, '#D9A066'); P(0, 304, 360, 113, '#4A2E1B'); P(0, 304, 360, 2, '#1B1420');
      bevel(290, 284, 50, 16, '#4A4E5A', '#9AA0AD', '#1B1420', INK); for (let i = 0; i < 5; i++) P(294 + i * 4, 288, 2, 8, '#2B2033'); P(318, 288, 18, 6, '#1A332B'); P(319, 289, 8, 2, '#6FB7A8'); P(332, 280, 1, 4, '#9AA0AD');
      DOT(336, 296, Math.floor(T) % 2 ? '#E2633B' : '#7A3442');
      bevel(262, 288, 12, 12, '#FFF7EA', '#FFFFFF', '#C9CCD3', INK); P(274, 291, 3, 6, '#E6D3BC'); P(264, 289, 8, 1, '#5A3A22');
      for (let i = 0; i < 3; i++) { const a = (F >> 2) + i * 3; DOT(265 + i * 3 + (a % 2), 285 - (a % 9), '#C9CCD3'); }
      tiles(417, 223, '#3D2E45', '#2B2033', 20, '#1B1420');
      return {map: area(X, Y, W, H), at: (nx, ny) => { const [a, b] = at(nx, ny); return [a * 3, b * 3]; }, area: area(100, 282, 180, 16)};
    };

    // ================================================================================================================
    // 3. scores: an arcade high-score table in a cabinet: marquee bulbs chase, rows land one by one with their numbers
    // counting up, the new record's initials blink (2 a second) and NEW RECORD swaps colors (2 a second).
    // o: {title, rows: [{name, value, prefix, suffix, dec, comma, hi}], t0, gap (0.3), count (0.7), newAt, newText}
    S.scores = function (o = {}) {
      const t0 = o.t0 || 0, gap = o.gap != null ? o.gap : 0.3, cnt = o.count || 0.7;
      P(0, 0, 360, 417, '#1B1420');
      for (let i = 0; i < 40; i++) DOT(Math.floor(hash(i * 3.1) * 360), Math.floor(hash(i * 5.3) * 70), hash(i) > 0.5 ? '#3D2E45' : '#2B2033');
      P(0, 70, 360, 2, '#7A3442'); P(0, 74, 360, 1, '#3B82C4');
      // the cabinet sides
      [[0, 22], [338, 22]].forEach(([x, w]) => { P(x, 72, w, 345, '#7A3442'); P(x, 72, w, 1, '#E2633B'); P(x === 0 ? w - 2 : x, 72, 2, 345, x === 0 ? '#3D2E45' : '#E2633B'); for (let y = 90; y < 417; y += 26) P(x + 4, y, w - 8, 1, '#3D2E45'); });
      // the marquee: lit panel, the title, bulbs chasing
      P(22, 84, 316, 30, INK); P(24, 86, 312, 26, '#7A3442'); P(26, 88, 308, 22, '#2B2033');
      for (let i = 0; i < 39; i++) { const lit = (i + Math.floor(F / 4)) % 3 === 0; DOT(26 + i * 8, 86, lit ? '#FFF7EA' : '#B07A47'); DOT(26 + i * 8, 111, (i + Math.floor(F / 4) + 1) % 3 === 0 ? '#FFF7EA' : '#B07A47'); }
      tx(o.title || 'HIGH SCORES', 180, 93, {align: 'center', color: '#F7C873'});
      // the screen: bezel, black glass, scanlines, the glass glint
      P(22, 116, 316, 202, INK); P(26, 120, 308, 194, '#120D14'); for (let y = 121; y < 314; y += 2) P(26, y, 308, 1, '#1B1420');
      line(30, 136, 44, 122, '#2B2033'); line(30, 142, 50, 122, '#2B2033');
      const cols = ['#F2A541', '#E2633B', '#6FB7A8', '#87CEEB', '#FFF7EA', '#F7C873'];
      tx('RANK', 40, 126, {color: '#6FB7A8'}); tx('NAME', 110, 126, {color: '#6FB7A8'}); tx('SCORE', 306, 126, {color: '#6FB7A8', align: 'right'}); P(36, 142, 272, 1, '#2F6F67');
      (o.rows || []).forEach((r, i) => { if (T < t0 + i * gap) for (let x = 46; x < 306; x += 8) P(x, 156 + i * 24, 4, 1, '#3D2E45'); });
      (o.rows || []).forEach((r, i) => {
        const ti = t0 + i * gap; if (T < ti) return;
        const y = 150 + i * 24, c = r.hi ? '#F7C873' : cols[i % cols.length], slide = ease(ti, 5, 40);
        const rank = r.rank || (['1ST', '2ND', '3RD', '4TH', '5TH', '6TH'][i]);
        if (r.hi) { P(32, y - 4, 280, 21, '#3D2E45'); if (((Math.floor((T - ti) * 4)) % 2) === 0) tx('>', 32 + slide, y, {color: '#F2A541'}); }
        tx(rank, 46 + slide, y, {color: c});
        const blinkOff = r.hi && T >= ti + cnt && Math.floor((T - ti) * 4) % 2 === 1;
        tx(r.name, 110 + slide, y, {color: blinkOff ? '#E2633B' : c});
        const p = clamp((T - ti) / cnt), v = typeof r.value === 'number' ? k.count(r.value, p, {from: r.from != null ? r.from : r.value * 0.85, prefix: r.prefix, suffix: r.suffix, dec: r.dec, comma: r.comma}) : r.value;
        tx(v, 306 + slide, y, {color: c, align: 'right'});
      });
      if (o.newAt != null && T >= o.newAt) tx(o.newText || 'NEW RECORD!', 180, 284, {align: 'center', color: Math.floor((T - o.newAt) * 4) % 2 ? '#E2633B' : '#F7C873'});
      // the control panel: a joystick and three buttons
      P(22, 318, 316, 16, '#3D2E45'); P(22, 318, 316, 1, '#6B7080'); P(22, 333, 316, 1, '#120D14');
      P(258, 322, 6, 6, INK); disc(261, 324, 3, '#E2633B'); DOT(260, 323, '#F7C873');
      [['#F2A541', 292], ['#6FB7A8', 306], ['#3B82C4', 320]].forEach(([c, x]) => { disc(x, 326, 4, INK); disc(x, 325, 3, c); DOT(x - 1, 324, '#FFF7EA'); });
      P(22, 334, 316, 83, '#2B2033'); bevel(160, 360, 40, 30, '#4A4E5A', '#9AA0AD', '#1B1420', INK); P(176, 366, 8, 12, INK); P(178, 368, 4, 8, '#E2633B');
      // the arcade carpet: confetti on navy
      P(0, 417, 360, 223, '#253048');
      for (let i = 0; i < 70; i++) { const x = Math.floor(hash(i * 2.7) * 352), y = 420 + Math.floor(hash(i * 6.1) * 214), c = ['#F2A541', '#6FB7A8', '#E2633B', '#87CEEB'][i % 4], s = i % 3;
        if (s === 0) { P(x, y, 3, 1, c); P(x + 2, y + 1, 3, 1, c); } else if (s === 1) { DOT(x + 1, y, c); P(x, y + 1, 3, 1, c); } else P(x, y, 2, 2, c); }
      return {area: area(32, 136, 280, 150)};
    };

    // ================================================================================================================
    // 4. boss: an objection as a boss. The boss bobs, its health bar drains with each argument (a white hit-flash for 2
    // frames, a knockback, a slash, the damage number rising), a lag bar catches up, and at defeatAt it breaks into
    // pixels. The command menu lists the arguments; the cursor points at the next one, used ones go grey.
    // o: {name, hp, hits: [{at, dmg, label}], defeatAt, winText ('VICTORY!'), menu ('ARGUMENTS'), t0}
    S.boss = function (o = {}) {
      const hits = o.hits || [], max = o.hp || 100;
      // dusk arena: a banded sky, stars, mountains, stone ground
      P(0, 0, 360, 80, '#1B1420'); P(0, 80, 360, 70, '#2B2033'); P(0, 150, 360, 60, '#3D2E45'); P(0, 210, 360, 50, '#7A3442');
      dith(0, 78, 360, 3, '#2B2033'); dith(0, 148, 360, 3, '#3D2E45'); dith(0, 208, 360, 3, '#7A3442');
      for (let i = 0; i < 30; i++) { const x = Math.floor(hash(i * 1.3) * 360), y = Math.floor(hash(i * 4.9) * 140); DOT(x, y, (Math.floor(F / 20) + i) % 5 === 0 ? '#F7C873' : '#6B7080'); }
      for (let x = 0; x < 360; x++) { const h = 20 + Math.round(14 * Math.sin(x * 0.03) + 9 * Math.sin(x * 0.087 + 1)); P(x, 260 - h, 1, h, '#1B1420'); if (h > 30) DOT(x, 260 - h, '#3D2E45'); }
      P(0, 260, 360, 157, '#4A4E5A');
      for (let y = 262, r = 0; y < 417; y += 10, r++) { P(0, y, 360, 1, '#6B7080'); for (let x = (r % 2) * 14; x < 360; x += 28) P(x, y, 1, 10, '#1B1420'); }
      P(0, 260, 360, 2, '#9AA0AD');
      P(0, 417, 360, 223, '#2B2033'); for (let y = 420, r = 0; y < 640; y += 14, r++) { P(0, y, 360, 1, '#3D2E45'); for (let x = (r % 2) * 20; x < 360; x += 40) P(x, y, 1, 14, '#1B1420'); }
      // health
      const done = hits.filter((h) => T >= h.at), hp = Math.max(0, max - done.reduce((a, h) => a + h.dmg, 0));
      let lag = hp; const last = done[done.length - 1];
      if (last) { const before = max - done.slice(0, -1).reduce((a, h) => a + h.dmg, 0), d = T - last.at; lag = d < 0.4 ? before : before + (hp - before) * clamp((d - 0.4) / 0.3); }
      tx(o.name || 'THE OBJECTION', 22, 88, {color: '#FFF7EA', drop: INK});
      tx('HP', 314, 88, {color: '#F7C873', align: 'right'});
      P(20, 104, 320, 10, INK); P(21, 105, 318, 8, '#3D2E45');
      const bw = (v) => Math.round(318 * v / max);
      P(21, 105, bw(lag), 8, '#F7C873'); P(21, 105, bw(hp), 8, '#E2633B'); P(21, 105, bw(hp), 2, '#F2A541'); P(21, 111, bw(hp), 2, '#7A3442');
      for (let x = 21 + 32; x < 339; x += 32) P(x, 105, 1, 8, INK);
      // the menu of arguments
      const gone = o.defeatAt != null && T >= o.defeatAt + 0.4;
      if (!gone) {
      win(16, 124, 158, 136, {});
      P(24, 119, tw(o.menu || 'ARGUMENTS') + 12, 12, INK); P(25, 120, tw(o.menu || 'ARGUMENTS') + 10, 10, '#7A3442');
      tx(o.menu || 'ARGUMENTS', 31, 119, {color: '#FFF7EA'});
      const next = hits.findIndex((h) => T < h.at);
      hits.forEach((h, i) => {
        const y = 136 + i * 24, used = T >= h.at;
        if (T < (o.t0 || 0) + i * 0.15) return;
        if (i === next && T >= (o.t0 || 0)) { const b = (F >> 3) & 1; P(24 + b, y + 3, 2, 7, '#F7C873'); P(26 + b, y + 4, 1, 5, '#F7C873'); P(27 + b, y + 5, 1, 3, '#F7C873'); }
        tx(h.label, 32, y, {color: used ? '#9AA0AD' : '#FFF7EA'});
      });
      }
      // the boss
      const dead = o.defeatAt != null && T >= o.defeatAt, dd = dead ? T - o.defeatAt : 0;
      const recent = done.length ? done[done.length - 1] : null, hf = recent ? fr(recent.at) : 99;
      const flash = hf >= 0 && hf < 2, kb = hf < 2 ? 4 : (hf < 4 ? 2 : (hf < 6 ? 1 : 0));
      const bx = 262 + kb, by = 190 + (dead ? 0 : ((F >> 3) & 1));
      if (!dead || dd < 0.9) {
        const q = dead ? clamp(dd / 0.8) : 0;
        const plot = (x, y, w, h, c) => {
          if (flash || (dead && dd < 0.07)) c = '#FFF7EA';
          if (!dead) return P(x, y, w, h, c);
          for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) { const hx = hash((x + i) * 0.91 + (y + j) * 7.3); if (hx < q) continue; const rise = hx < q + 0.12 ? Math.floor((q + 0.12 - hx) * 40) : 0; DOT(x + i, y + j - rise, c); }
        };
        const blob = (cx, cy, r, c) => { for (let dy = -r; dy <= r; dy++) { const hw = Math.floor(Math.sqrt(r * r - dy * dy) * (dy > 0 ? 1.1 : 1) + 0.4); plot(cx - hw, cy + dy, 2 * hw + 1, 1, c); } };
        // horns, body in three tones, belly, arms
        [[-1, 1], [1, 1]].forEach(([s]) => { for (let j = 0; j < 14; j++) plot(bx + s * (26 + Math.floor(j / 3)) - (s < 0 ? 3 : 0), by - 50 - j, 4 - Math.floor(j / 5), 1, j < 4 ? '#B39A88' : '#E6D3BC'); });
        blob(bx, by, 44, INK); blob(bx, by, 43, '#3D2E45'); blob(bx - 2, by - 2, 40, '#7A3442');
        for (let dy = -36; dy < -10; dy++) { const hw = Math.floor(Math.sqrt(Math.max(0, 1600 - (dy + 2) * (dy + 2))) + 0.4); plot(bx - hw - 2, by + dy, 5, 1, '#E2633B'); }
        blob(bx + 4, by + 18, 18, '#3D2E45'); blob(bx + 3, by + 17, 16, '#7A3442');
        plot(bx - 52, by + 6, 12, 7, INK); plot(bx - 51, by + 7, 10, 5, '#7A3442'); plot(bx + 40, by + 6, 12, 7, INK); plot(bx + 41, by + 7, 10, 5, '#3D2E45');
        // angry eyes, brows, a toothed grin
        [[-15, 1], [15, -1]].forEach(([ex, s]) => { plot(bx + ex - 7, by - 16, 14, 8, INK); plot(bx + ex - 6, by - 15, 12, 6, '#F7C873'); plot(bx + ex - 2 + s, by - 14, 4, 4, INK); plot(bx + ex - 1 + s, by - 14, 1, 1, '#FFF7EA');
          for (let i = 0; i < 12; i++) plot(bx + ex - 6 + i, by - 22 + Math.round((s > 0 ? i : 11 - i) / 3), 1, 2, INK); });
        plot(bx - 18, by + 2, 36, 10, INK); plot(bx - 17, by + 3, 34, 8, '#3D2E45');
        for (let i = 0; i < 6; i++) { plot(bx - 16 + i * 6, by + 3, 4, 3, '#FFF7EA'); plot(bx - 13 + i * 6, by + 8, 4, 3, '#E6D3BC'); }
      }
      // the slash and the damage number for each hit
      done.forEach((h) => {
        const f = fr(h.at);
        if (!dead) k.burst((bx - 6) * 3, (by - 4) * 3, h.at, {n: 12, r: 200, life: 0.5, colors: ['accent2', 'paper', 'accent']});
        if (f < 4 && !dead) { line(bx - 30 + f * 4, by - 40, bx + 24 + f * 4, by + 30, f < 2 ? '#FFF7EA' : '#F7C873', 2); }
        if (f < 27) tx('-' + h.dmg, bx + 4, by - 72 - Math.min(10, Math.floor(f / 2)), {size: 66, color: '#F2A541', drop: INK});
      });
      if (dead && T >= o.defeatAt + 0.5) k.slam(o.winText || 'VICTORY!', 540, 520, o.defeatAt + 0.5, {size: 132, color: 'accent', align: 'center', stamp: true, glint: false});
      return {area: area(32, 136, 136, 120), boss: [bx * 3, by * 3], hp};
    };

    // ================================================================================================================
    // 5. register: a store counter with a brass till. Each item prints on the receipt as it rings (a key goes down, the
    // $ flag pops in the display, the total steps up); at openAt the drawer slides out and coins jump.
    // o: {items: [{label, amount, at}], prefix ('$'), totalAt, openAt, totalLabel ('TOTAL'), comma (true)}
    S.register = function (o = {}) {
      const items = o.items || [], pre = o.prefix != null ? o.prefix : '$';
      const money = (v) => pre + Number(v).toLocaleString('en-US', {maximumFractionDigits: o.dec || 0, minimumFractionDigits: o.dec || 0});
      // the shop wall: paneling, two shelves of stock
      P(0, 0, 360, 286, '#6B4226'); for (let x = 0; x < 360; x += 24) { P(x, 0, 1, 286, '#4A2E1B'); P(x + 1, 0, 1, 286, '#8C5A33'); }
      [[150, 0], [214, 1]].forEach(([y, s]) => {
        P(0, y, 360, 4, '#D9A066'); P(0, y + 4, 360, 2, '#4A2E1B');
        for (let x = 4 + s * 9; x < 356; x += 18) { const c = [['#E2633B', '#7A3442'], ['#6FB7A8', '#2F6F67'], ['#87CEEB', '#3B82C4'], ['#F7C873', '#F2A541']][Math.floor(hash(x * 0.3 + y) * 4)]; const h = 10 + Math.floor(hash(x + y) * 8);
          P(x - 1, y - h - 1, 14, h + 1, INK); P(x, y - h, 12, h, c[0]); P(x + 9, y - h, 3, h, c[1]); P(x + 2, y - h + 3, 6, 3, '#FFF7EA'); }
      });
      // the receipt printer and the paper (left); it grows a line per item
      const shown = items.filter((it) => T >= it.at), tot = shown.reduce((a, it) => a + it.amount, 0);
      const lines = shown.length + (o.totalAt != null && T >= o.totalAt ? 2 : 0);
      const lastAt = Math.max(...shown.map((it) => it.at), o.totalAt != null && T >= o.totalAt ? o.totalAt : -1e9);
      const grow = lastAt > -1e9 ? ease(lastAt, 5, 18) : 0;
      const ph = 12 + lines * 18 - grow, py = 256 - ph;
      P(48, py - 1, 144, ph + 1, INK); P(49, py, 142, ph, '#FFF7EA'); P(189, py, 2, ph, '#E6D3BC');
      for (let x = 49; x < 191; x += 4) { DOT(x, py, '#120D14'); DOT(x + 2, py - 1, '#FFF7EA'); }
      clip(49, py, 142, ph, () => {
        shown.forEach((it, i) => { const y = py + 6 + i * 18; tx(it.label, 56, y, {color: '#3D2E45'}); tx(money(it.amount), 184, y, {color: '#3D2E45', align: 'right'}); });
        if (o.totalAt != null && T >= o.totalAt) { const y = py + 6 + shown.length * 18; for (let x = 56; x < 184; x += 4) P(x, y + 3, 2, 1, '#B39A88'); tx(o.totalLabel || 'TOTAL', 56, y + 18, {color: '#7A3442'}); tx(money(tot), 184, y + 18, {color: '#7A3442', align: 'right'}); }
      });
      bevel(38, 256, 164, 30, '#4A4E5A', '#9AA0AD', '#1B1420', INK); P(48, 258, 144, 3, INK); P(44, 266, 50, 2, '#2B2033'); DOT(190, 270, shown.length ? '#6FB7A8' : '#245752');
      // the till: brass body, a key bank, the display tower
      const rx = 210, ry = 196;
      P(rx - 1, ry - 1, 132, 92, INK); P(rx, ry, 130, 90, '#B07A47'); P(rx, ry, 130, 2, '#F7C873'); P(rx, ry, 2, 90, '#D9A066'); P(rx + 126, ry + 2, 4, 88, '#8C5A33'); P(rx, ry + 86, 130, 4, '#6B4226');
      for (let i = 0; i < 6; i++) { DOT(rx + 8 + i * 20, ry + 6, '#F7C873'); DOT(rx + 9 + i * 20, ry + 7, '#8C5A33'); }
      P(rx + 8, ry + 14, 114, 52, '#2B2033'); P(rx + 8, ry + 14, 114, 1, '#120D14');
      const pressed = shown.length ? ((shown.length - 1) * 7) % 15 : -1, pf = shown.length ? fr(shown[shown.length - 1].at) : 99;
      for (let r = 0; r < 3; r++) for (let c = 0; c < 5; c++) { const i = r * 5 + c, down = i === pressed && pf >= 0 && pf < 5, kx = rx + 12 + c * 22, ky = ry + 18 + r * 16 + (down ? 1 : 0), red = (i % 5 === 4);
        P(kx, ky + 11, 18, 2, '#120D14'); P(kx, ky, 18, 11, red ? '#E2633B' : '#FFF7EA'); if (!down) P(kx, ky, 18, 1, red ? '#F7C873' : '#FFFFFF'); P(kx, ky + 10, 18, 1, red ? '#7A3442' : '#B39A88'); P(kx + 6, ky + 4, 6, 2, red ? '#7A3442' : '#C9CCD3'); }
      P(rx + 8, ry + 70, 114, 12, '#8C5A33'); P(rx + 8, ry + 70, 114, 1, '#6B4226'); P(rx + 56, ry + 74, 18, 3, '#F7C873');
      // the display tower and its $ flag
      const dx = 222, dy = 114;
      P(dx + 46, dy + 66, 14, 16, '#4A4E5A'); P(dx + 46, dy + 66, 2, 16, '#9AA0AD');
      P(dx - 1, dy - 1, 108, 68, INK); bevel(dx, dy, 106, 66, '#4A4E5A', '#9AA0AD', '#2B2033');
      P(dx + 6, dy + 18, 94, 40, '#1A332B'); P(dx + 7, dy + 19, 92, 38, '#24453A'); for (let y = dy + 20; y < dy + 57; y += 3) P(dx + 7, y, 92, 1, '#1A332B');
      tx(o.displayLabel || 'AMOUNT', dx + 8, dy + 4, {color: '#C9CCD3'});
      const val = money(tot), big = tw(val, 66) <= 86 ? 66 : 39;
      tx(val, dx + 94, dy + 38 - th(big) / 2, {size: big, color: '#6FB7A8', align: 'right'});
      if (shown.length && pf >= 0 && pf < 12) { const fy = [10, 6, 3, 1, 0, 0, 0, 0, 0, 1, 4, 8][pf]; P(dx + 84, dy - 18 + fy, 18, 16, INK); P(dx + 85, dy - 17 + fy, 16, 14, '#E2633B'); tx('$', dx + 93, dy - 16 + fy, {color: '#FFF7EA', align: 'center', lint: false}); }
      // the counter and the drawer that slides out, coins jumping
      P(0, 286, 360, 8, '#B07A47'); P(0, 286, 360, 1, '#F7C873'); P(0, 293, 360, 1, '#4A2E1B'); P(0, 294, 360, 123, '#8C5A33');
      for (let x = 10; x < 360; x += 70) { bevel(x, 304, 60, 100, '#8C5A33', '#B07A47', '#4A2E1B'); P(x + 6, 310, 48, 88, '#6B4226'); }
      const open = o.openAt != null && T >= o.openAt, od = open ? Math.min(14, Math.round(14 * easeOut(fr(o.openAt) / 5))) : 0;
      P(rx + 4, 288 + od - 2, 122, 10, INK); P(rx + 5, 288 + od - 1, 120, 8, '#D9A066'); P(rx + 5, 288 + od - 1, 120, 1, '#F7C873'); P(rx + 58, 291 + od, 14, 2, '#6B4226');
      if (od > 2) { P(rx + 5, 286, 120, od - 2, '#2B2033'); for (let i = 0; i < 4; i++) { P(rx + 8 + i * 30, 287, 26, Math.min(od - 3, 6), i < 2 ? '#3E7A62' : '#B07A47'); if (i >= 2) for (let j = 0; j < 3; j++) DOT(rx + 12 + i * 30 + j * 6, 288, '#F7C873'); } }
      if (open) for (let i = 0; i < 7; i++) { const d = T - o.openAt - 0.12 - i * 0.05; if (d < 0 || d > 0.9) continue; const vx = (hash(i * 3.3) - 0.5) * 120, vy = 150 + hash(i * 1.7) * 60, cx = rx + 65 + vx * d, cy = 286 - vy * d + 340 * d * d; if (cy < 300) coin(Math.round(cx), Math.round(cy), Math.floor(F / 2) + i); }
      // the floor: checker tiles
      tiles(417, 223, '#E6D3BC', '#B39A88', 20, '#FFF7EA');
      return {area: area(48, 90, 144, 166), display: [dx * 3, dy * 3], total: tot};
    };

    // ================================================================================================================
    // 6. calendar: a wall calendar, a month grid whose days fill as they are said (an X, a check, a coin or a color),
    // and a week strip that slides from row to row. o: {month, year, start (weekday of the 1st, 0 = Sunday), days (30),
    // fills: [{day, at, c, mark: 'x'|'check'|'coin'|'fill'}], run: {from, to, at, every, c, mark}, weeks: [{row, at}]}
    S.calendar = function (o = {}) {
      P(0, 0, 360, 417, '#245752'); for (let x = 0; x < 360; x += 12) P(x, 0, 4, 417, '#2F6F67');
      P(0, 0, 360, 4, '#1A332B');
      const X = 22, Y = 84, W = 316, cw = 44, start = o.start || 0, days = o.days || 30, rows = Math.ceil((start + days) / 7), ch = Math.floor(150 / rows);
      // the nail, the string, the binding
      line(180, 77, 150, 84, '#E6D3BC'); line(180, 77, 210, 84, '#E6D3BC'); disc(180, 77, 2, '#C9CCD3'); DOT(179, 76, '#FFF7EA');
      P(X + 2, Y + 2, W, 192, '#1A332B');
      P(X - 1, Y - 1, W + 2, 192, INK); P(X, Y, W, 190, '#FFF7EA');
      P(X, Y, W, 22, '#E2633B'); P(X, Y, W, 1, '#F2A541'); P(X, Y + 21, W, 1, '#7A3442');
      for (let i = 0; i < 14; i++) { const rx = X + 12 + i * 22; P(rx, Y - 5, 3, 8, INK); P(rx + 1, Y - 4, 1, 6, '#C9CCD3'); }
      tx(o.month || 'NOVEMBER', X + 8, Y + 5, {color: '#FFF7EA'}); if (o.year) tx(String(o.year), X + 14 + tw(o.month || 'NOVEMBER'), Y + 5, {color: '#F7C873'});
      P(X, Y + 22, W, 16, '#7A3442');
      'SMTWTFS'.split('').forEach((d, i) => tx(d, X + 4 + i * cw + cw / 2, Y + 24, {color: i === 0 ? '#F7C873' : '#FFF7EA', align: 'center'}));
      const gy = Y + 38;
      for (let r = 0; r <= rows; r++) P(X, gy + r * ch, W, 1, '#E6D3BC');
      for (let c = 1; c < 7; c++) P(X + 4 + c * cw, gy, 1, rows * ch, '#E6D3BC');
      const cell = (d) => { const i = start + d - 1; return [X + 4 + (i % 7) * cw, gy + Math.floor(i / 7) * ch]; };
      const fills = (o.fills || []).slice();
      if (o.run) for (let d = o.run.from, n = 0; d <= o.run.to; d++, n++) fills.push({day: d, at: o.run.at + n * (o.run.every || 0.08), c: o.run.c, mark: o.run.mark});
      const mark = (x, y, m, c) => {
        const cx = x + cw / 2, cy = y + ch / 2 + 3;
        if (m === 'x') { line(cx - 7, cy - 6, cx + 6, cy + 6, c || '#E2633B', 2); line(cx + 6, cy - 6, cx - 7, cy + 6, c || '#E2633B', 2); }
        else if (m === 'check') { line(cx - 7, cy, cx - 3, cy + 5, c || '#2F6F67', 2); line(cx - 3, cy + 5, cx + 7, cy - 7, c || '#2F6F67', 2); }
        else if (m === 'coin') coin(Math.round(cx - 4), Math.round(cy - 4), 0);
      };
      fills.forEach((f) => {
        const q = fr(f.at); if (q < 0) return; const [x, y] = cell(f.day);
        const c = f.c || (f.mark === 'fill' ? '#F7C873' : '#F4E6D3');
        if (q < 2) dith(x + 1, y + 1, cw - 1, ch - 1, c); else P(x + 1, y + 1, cw - 1, ch - 1, c);
        if (q >= 2 && f.mark && f.mark !== 'fill') { const d = q < 4 ? -2 : 0; mark(x, y + d, f.mark, f.mc); }
      });
      for (let d = 1; d <= days; d++) { const [x, y] = cell(d); tx(String(d), x + 3, y + 2, {color: (start + d - 1) % 7 === 0 ? '#E2633B' : '#3D2E45'}); }
      // the week strip
      const ws = (o.weeks || []).filter((w) => T >= w.at);
      if (ws.length) {
        const cur = ws[ws.length - 1], prev = ws.length > 1 ? ws[ws.length - 2].row : cur.row, f = fr(cur.at);
        const ry = gy + cur.row * ch + Math.round((prev - cur.row) * ch * (1 - easeOut(f / 5)));
        P(X + 2, ry - 1, W - 4, 3, '#F2A541'); P(X + 2, ry + ch - 1, W - 4, 3, '#F2A541'); P(X + 2, ry, 3, ch, '#F2A541'); P(X + W - 5, ry, 3, ch, '#F2A541');
        P(X - 6, ry + ch / 2 - 3, 5, 7, '#F2A541');
      }
      // the desk below: a mug with steam, a pencil cup
      P(0, 296, 360, 6, '#B07A47'); P(0, 296, 360, 1, '#D9A066'); P(0, 302, 360, 115, '#6B4226'); P(0, 302, 360, 2, '#4A2E1B');
      bevel(318, 280, 14, 16, '#E2633B', '#F2A541', '#7A3442', INK); P(332, 284, 3, 8, '#7A3442');
      for (let i = 0; i < 3; i++) { const a = (F >> 2) + i * 3; DOT(321 + i * 4 + (a % 2), 276 - (a % 9), '#C9CCD3'); }
      planks(417, 223, '#8C5A33', '#B07A47', '#6B4226');
      return {area: area(100, 278, 210, 16), grid: area(X, gy, W, rows * ch), cell: (d) => { const [x, y] = cell(d); return [x * 3, y * 3, cw * 3, ch * 3]; }};
    };

    // ================================================================================================================
    // 7. flaps: a split-flap departures board. Each row's letters flip through the alphabet (2 frames a flap: the top
    // half falls first, then the whole letter) and land left to right. o: {title, rows: [{label, value, at, hi}], cols (16)}
    S.flaps = function (o = {}) {
      // a station wall of tile under a dark beam
      P(0, 0, 360, 417, '#6B7080'); for (let y = 0; y < 417; y += 8) for (let x = ((y >> 3) & 1) * 8; x < 360; x += 16) { P(x, y, 15, 7, '#9AA0AD'); P(x, y, 15, 1, '#C9CCD3'); }
      P(0, 0, 360, 74, '#4A4E5A'); P(0, 74, 360, 2, '#2B2033');
      const cols = o.cols || 12, cw = 22, chh = 32, x0 = Math.round(180 - (cols * cw) / 2), rows = (o.rows || []).slice(0, 4);
      const X = x0 - 8, W = cols * cw + 14, Y = 84, H = 40 + 4 * 38 + 4;
      P(X + 3, Y + 3, W, H, '#2B2033'); P(X - 1, Y - 1, W + 2, H + 2, INK); P(X, Y, W, H, '#1B1420'); P(X, Y, W, 1, '#3D2E45');
      P(X + 4, Y + 4, W - 8, 24, '#253048'); P(X + 4, Y + 4, W - 8, 1, '#3B82C4');
      tx(o.title || 'DEPARTURES', X + 10, Y + 10, {color: '#F7C873'});
      // a little train rolls along the title band, a pixel every 2 frames
      const trx = X + W - 50 + ((Math.floor(F / 2)) % 40); clip(X + W - 54, Y + 4, 50, 24, () => { P(trx, Y + 13, 14, 8, '#FFF7EA'); P(trx + 2, Y + 15, 3, 2, '#3B82C4'); P(trx + 7, Y + 15, 3, 2, '#3B82C4'); P(trx - 16, Y + 13, 14, 8, '#C9CCD3'); DOT(trx + 2, Y + 21, INK); DOT(trx + 10, Y + 21, INK); DOT(trx - 12, Y + 21, INK); DOT(trx - 5, Y + 21, INK); });
      const CH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$%';
      for (let ri = 0; ri < 4; ri++) {
        const r = rows[ri], y = Y + 34 + ri * 38;
        const s = r ? (String(r.label).padEnd(Math.max(0, cols - String(r.value).length)) + r.value).slice(0, cols).toUpperCase() : '';
        for (let j = 0; j < cols; j++) {
          const cx = x0 + j * cw, ch = s[j] || ' ', h2 = chh / 2;
          P(cx, y, cw - 2, chh, '#2B2033'); P(cx, y, cw - 2, 1, '#3D2E45'); P(cx, y + h2 + 1, cw - 2, 1, '#3D2E45'); P(cx, y + h2, cw - 2, 1, INK); P(cx, y + chh - 1, cw - 2, 1, INK);
          if (!r || T < r.at) continue;
          const n = 3 + Math.floor(hash(ri * 31 + j * 7.7) * 5), f = fr(r.at + j * 0.035);
          if (f < 0 || (ch === ' ' && f >= 2 * n)) continue;
          const color = r.hi && j >= cols - String(r.value).length ? '#F2A541' : '#FFF7EA';
          const charAt = (idx) => idx >= n - 1 ? ch : CH[Math.floor(hash(ri * 13 + j * 3.1 + idx * 1.7) * CH.length)];
          const draw = (c, half, settled) => { if (c === ' ') return; clip(cx, half === 'b' ? y + h2 + 1 : y, cw - 2, half ? h2 : chh, () => tx(c, cx + (cw - 2) / 2, y + 5, {size: 66, color, align: 'center', lint: !!settled})); };
          if (f >= 2 * n) draw(ch, null, true);
          else if (f % 2 === 0) { const idx = Math.floor(f / 2); draw(charAt(idx), 't'); draw(charAt(idx - 1), 'b'); P(cx, y + h2 + 1, cw - 2, 5, '#1B1420'); P(cx, y + h2 + 1, cw - 2, 1, '#4A4E5A'); }
          else draw(charAt(Math.floor(f / 2)));
          P(cx, y + h2, cw - 2, 1, INK);
        }
      }
      // the platform: a yellow safety strip, tactile dots
      P(0, 330, 360, 87, '#4A4E5A'); P(0, 330, 360, 2, '#9AA0AD');
      P(0, 417, 360, 223, '#4A4E5A'); P(0, 420, 360, 12, '#F2A541'); for (let x = 2; x < 360; x += 6) for (let y = 422; y < 432; y += 4) DOT(x + ((y >> 2) & 1) * 3, y, '#B07A47');
      for (let y = 440; y < 640; y += 24) P(0, y, 360, 1, '#6B7080');
      return {area: area(X, Y + 34, W, 4 * 38), board: area(X, Y, W, H)};
    };

    // ================================================================================================================
    // 8. chat: a messaging app on a phone in a work truck's dash mount. Messages slide up a pixel at a time, the other
    // side shows a typing bubble first, sent ones get read ticks, a notification can drop in from the top.
    // o: {who, clock, msgs: [{me, text, at, typing (seconds of dots before), read (time)}], notify: {text, at, dur}}
    S.chat = function (o = {}) {
      // the windshield: sky, fields, a road whose dashes rush toward us
      sky3(0, 120); P(0, 120, 360, 70, '#3E7A62'); dith(0, 120, 360, 3, '#2F5A4A');
      for (let i = 0; i < 6; i++) { const x = ((i * 70 - Math.floor(F / 3)) % 420 + 420) % 420 - 30; disc(x, 112, 6, '#2F5A4A'); P(x - 1, 112, 2, 8, '#5A3A22'); }
      for (let y = 120; y < 190; y++) { const hw = Math.round(6 + (y - 120) * 1.9); P(180 - hw, y, 2 * hw, 1, '#4A4E5A'); }
      for (let i = 0; i < 4; i++) { const yy = 120 + (((Math.floor(F * 1.5) + i * 18) % 72)); const w = 1 + Math.floor((yy - 120) / 24); P(180 - w, yy, 2 * w, 2 + Math.floor((yy - 120) / 18), '#F7C873'); }
      cloud(40, 30, 30, 2); cloud(250, 50, 24, 7);
      // pillars, the mirror, the air freshener swinging
      for (let y = 0; y < 196; y++) { P(0, y, 18 - Math.floor(y / 14), 1, '#1B1420'); P(342 + Math.floor(y / 14), y, 18, 1, '#1B1420'); }
      P(0, 0, 360, 10, '#1B1420'); P(150, 10, 60, 14, INK); P(152, 11, 56, 11, '#4A4E5A'); P(153, 12, 54, 4, '#87CEEB'); P(178, 0, 4, 11, INK);
      const sw = [0, 1, 0, -1][(F >> 3) % 4]; line(196, 22, 196 + sw, 34, '#C9CCD3'); P(192 + sw, 34, 9, 10, '#3E7A62'); P(194 + sw, 32, 5, 2, '#3E7A62'); DOT(196 + sw, 30, '#3E7A62'); DOT(193 + sw, 35, '#6FB7A8');
      // the dash
      P(0, 190, 360, 227, '#2B2033'); P(0, 190, 360, 3, '#3D2E45'); P(0, 193, 360, 1, '#120D14');
      for (let i = 0; i < 6; i++) { P(16, 220 + i * 4, 50, 2, '#1B1420'); P(294, 220 + i * 4, 50, 2, '#1B1420'); }
      // the phone in its mount
      const X = 96, Y = 84, W = 200, H = 240;
      P(X + 90, Y + H, 20, 12, '#4A4E5A'); P(X + 92, Y + H, 4, 12, '#6B7080');
      P(X + 3, Y + 3, W, H, '#120D14'); P(X - 1, Y, W + 2, H, INK); P(X, Y - 1, W, H + 2, INK);
      P(X, Y, W, H, '#1B1420'); P(X + 1, Y, W - 2, 1, '#4A4E5A'); P(X, Y + 1, 1, H - 2, '#4A4E5A');
      P(X - 6, Y + 100, 8, 30, '#4A4E5A'); P(X + W - 2, Y + 100, 8, 30, '#4A4E5A'); P(X - 6, Y + 100, 8, 1, '#9AA0AD'); P(X + W - 2, Y + 100, 8, 1, '#9AA0AD');
      const sx = X + 6, sy = Y + 6, sw2 = W - 12, sh = H - 12;
      P(sx, sy, sw2, sh, '#F4E6D3');
      for (let y = sy + 40; y < sy + sh - 20; y += 10) for (let x = sx + ((y / 10) % 2) * 5 + 2; x < sx + sw2; x += 10) DOT(x, y, '#E6D3BC');
      // header: status bar, back arrow, avatar, name, a live dot
      P(sx, sy, sw2, 36, '#2F6F67'); P(sx, sy + 36, sw2, 1, '#245752');
      tx(o.clock || '9:41', sx + 4, sy + 2, {color: '#FFF7EA', lint: false});
      for (let i = 0; i < 4; i++) P(sx + sw2 - 30 + i * 3, sy + 9 - i * 2, 2, 2 + i * 2, '#FFF7EA');
      P(sx + sw2 - 15, sy + 4, 11, 7, '#FFF7EA'); P(sx + sw2 - 14, sy + 5, 6, 5, '#6FB7A8'); P(sx + sw2 - 4, sy + 6, 1, 3, '#FFF7EA');
      line(sx + 9, sy + 26, sx + 5, sy + 22, '#FFF7EA'); line(sx + 9, sy + 18, sx + 5, sy + 22, '#FFF7EA');
      disc(sx + 22, sy + 22, 7, '#F0B98D'); P(sx + 15, sy + 15, 14, 4, '#E2633B'); DOT(sx + 19, sy + 22, INK); DOT(sx + 25, sy + 22, INK); P(sx + 20, sy + 26, 5, 1, '#C98B63');
      tx(o.who || 'Customer', sx + 34, sy + 16, {color: '#FFF7EA'}); disc(sx + 36 + tw(o.who || 'Customer') + 5, sy + 22, 2, '#F7C873');
      // messages
      const cy0 = sy + 40, cy1 = sy + sh - 22, maxW = 130;
      const items = [];
      (o.msgs || []).forEach((m) => {
        const typing = !m.me && m.typing && T >= m.at - m.typing && T < m.at;
        if (T < m.at && !typing) return;
        if (typing) { items.push({typing: true, h: 16}); return; }
        const ls = k.wrap(m.text, {size: 39}, (maxW - 12) * 3).slice(0, 6), w = Math.min(maxW, Math.ceil(Math.max(...ls.map((l) => tw(l)))) + 10);
        items.push({m, ls, w, h: ls.length * 15 + 8 + (m.me ? 0 : 0)});
      });
      let total = items.reduce((a, it) => a + it.h + 6, 0);
      const scroll = Math.max(0, total - (cy1 - cy0 - 4));
      clip(sx, cy0, sw2, cy1 - cy0, () => {
        let y = cy0 + 4 - scroll;
        items.forEach((it) => {
          if (it.typing) { const bx = sx + 6; P(bx, y, 34, 16, '#FFF7EA'); P(bx, y + 15, 34, 1, '#E6D3BC'); for (let i = 0; i < 3; i++) { const up = ((F >> 2) - i) % 3 === 0 ? 1 : 0; P(bx + 8 + i * 7, y + 6 - up, 4, 4, up ? '#6B7080' : '#B39A88'); } y += 22; return; }
          const {m, ls, w, h} = it, sl = ease(m.at, 4, 8), bx = m.me ? sx + sw2 - 8 - w : sx + 8, by = y + sl;
          const base = m.me ? '#3B82C4' : '#FFF7EA', lo = m.me ? '#253048' : '#E6D3BC', hi = m.me ? '#87CEEB' : '#FFFFFF';
          P(bx + 1, by, w - 2, h, base); P(bx, by + 1, w, h - 2, base); P(bx + 1, by, w - 2, 1, hi); P(bx + 1, by + h - 1, w - 2, 1, lo);
          if (m.me) { P(bx + w, by + h - 5, 2, 3, base); P(bx + w + 2, by + h - 3, 2, 2, base); } else { P(bx - 2, by + h - 5, 2, 3, base); P(bx - 4, by + h - 3, 2, 2, base); }
          ls.forEach((l, li) => tx(l, bx + 5, by + 4 + li * 15, {color: m.me ? '#FFF7EA' : '#2B2033'}));
          if (m.me && m.read != null && T >= m.read) { const tcol = '#87CEEB'; [0, 4].forEach((d) => { DOT(bx + w - 12 + d, by + h - 5, tcol); DOT(bx + w - 11 + d, by + h - 4, tcol); line(bx + w - 10 + d, by + h - 5, bx + w - 7 + d, by + h - 8, tcol); }); }
          y += h + 6;
        });
      });
      // the composer
      P(sx, cy1, sw2, sh - (cy1 - sy), '#FFF7EA'); P(sx, cy1, sw2, 1, '#E6D3BC');
      P(sx + 5, cy1 + 4, sw2 - 30, 13, '#F4E6D3'); P(sx + 5, cy1 + 4, sw2 - 30, 1, '#E6D3BC');
      disc(sx + sw2 - 12, cy1 + 10, 7, '#2F6F67'); line(sx + sw2 - 15, cy1 + 10, sx + sw2 - 8, cy1 + 10, '#FFF7EA'); line(sx + sw2 - 11, cy1 + 7, sx + sw2 - 8, cy1 + 10, '#FFF7EA'); line(sx + sw2 - 11, cy1 + 13, sx + sw2 - 8, cy1 + 10, '#FFF7EA');
      // the notification banner drops from the top on whole pixels and goes back up
      const n = o.notify;
      if (n && T >= n.at && T < n.at + (n.dur || 2.5) + 0.3) {
        const inF = fr(n.at), outF = fr(n.at + (n.dur || 2.5)), dy = outF >= 0 ? -Math.round(30 * easeOut(outF / 6)) : -Math.round(30 * (1 - easeOut(inF / 6)));
        clip(sx, sy, sw2, sh, () => { const by = sy + 4 + dy; P(sx + 4, by + 2, sw2 - 8, 26, '#1B1420'); P(sx + 3, by, sw2 - 8, 26, '#FFF7EA'); P(sx + 3, by, sw2 - 8, 1, '#FFFFFF'); P(sx + 7, by + 5, 14, 14, '#2F6F67'); P(sx + 10, by + 9, 8, 6, '#FFF7EA'); tx(n.text, sx + 26, by + 7, {color: '#2B2033', lint: false}); });
      }
      // the cab floor
      P(0, 417, 360, 223, '#1B1420'); for (let y = 424; y < 640; y += 8) P(20, y, 320, 2, '#2B2033');
      return {area: area(sx, cy0, sw2, cy1 - cy0), phone: area(X, Y, W, H)};
    };

    // ================================================================================================================
    // 9. weather: a TV weather map of the region (land, the lake, Chicago's star). Fronts sweep across on whole pixels
    // (cold: blue with teeth, warm: red with domes), icons pop on (sun rays turn, snow falls, rain), and the lower third
    // shows a season strip of 12 monthly bars. o: {title, fronts: [{kind, at, dur, x0, x1}], icons: [{kind, x, y, at, label}],
    // months: [12 values 0..1], monthsAt, hi (month index)}
    S.weather = function (o = {}) {
      P(0, 0, 360, 417, '#253048'); for (let y = 0; y < 417; y += 4) P(0, y, 360, 1, '#1B1420');
      const X = 14, Y = 82, W = 332, H = 150;
      P(X - 3, Y - 3, W + 6, H + 6, INK); P(X - 2, Y - 2, W + 4, H + 4, '#3B82C4'); P(X - 2, Y - 2, W + 4, 1, '#87CEEB');
      clip(X, Y, W, H, () => {
        P(X, Y, W, H, '#3B82C4');
        P(X, Y, W, H, '#3E7A62'); dith(X, Y, W, H, '#2F5A4A');
        // the lake: a long blob, its shore in pale blue
        for (let y = Y; y < Y + 118; y++) { const t = (y - Y) / 118, cx = X + 236 + Math.round(8 * Math.sin(t * 3)), hw = Math.round(14 * Math.sin(Math.PI * Math.min(1, t * 1.05 + 0.05)) + 3); P(cx - hw - 1, y, 2 * hw + 2, 1, '#87CEEB'); P(cx - hw, y, 2 * hw, 1, '#3B82C4'); }
        for (let x = X + 10; x < X + W - 60; x += 3) DOT(x, Y + 64, '#24453A');
        for (let y = Y + 4; y < Y + H; y += 3) { DOT(X + 120, y, '#24453A'); DOT(X + 196, y, '#24453A'); }
        // Chicago's star, south-west corner of the lake
        const sx = X + 224, sy = Y + 112; P(sx - 2, sy, 5, 1, '#F7C873'); P(sx, sy - 2, 1, 5, '#F7C873'); DOT(sx, sy, '#FFF7EA');
        (o.fronts || []).forEach((fr0) => {
          if (T < fr0.at) return;
          const p = clamp((T - fr0.at) / (fr0.dur || 2)), x = X + Math.round(W * ((fr0.x0 != null ? fr0.x0 : 0) + ((fr0.x1 != null ? fr0.x1 : 0.7) - (fr0.x0 || 0)) * easeOut(p)));
          const cold = fr0.kind !== 'warm', c = cold ? '#253048' : '#7A3442', c2 = cold ? '#87CEEB' : '#F2A541';
          for (let y = Y; y < Y + H; y++) { const fx = x + Math.round(12 * Math.sin((y - Y) * 0.04)); P(fx, y, 2, 1, c); }
          for (let y = Y + 6; y < Y + H; y += 16) { const fx = x + Math.round(12 * Math.sin((y - Y) * 0.04)) + 2;
            if (cold) for (let j = 0; j < 7; j++) P(fx, y + j, 4 - Math.abs(3 - j) + 1, 1, j === 0 ? c2 : c);
            else for (let j = -3; j <= 3; j++) P(fx, y + j + 3, Math.round(Math.sqrt(9 - j * j)) + 1, 1, j === -3 ? c2 : c); }
        });
      });
      const icon = (ic) => {
        const f = fr(ic.at); if (f < 0) return;
        const x = Math.round(X + ic.x * W), y = Math.round(Y + ic.y * H) + [-6, -3, -1, 0, -1, 0][Math.min(5, f)];
        if (ic.kind === 'sun') { const r = Math.floor(T * 2) % 2; disc(x, y, 7, '#B07A47'); disc(x, y, 6, '#F2A541'); disc(x - 1, y - 1, 4, '#F7C873'); for (let i = 0; i < 8; i++) { const a = i * TAU / 8 + (r ? TAU / 16 : 0); P(x + Math.round(Math.cos(a) * 10), y + Math.round(Math.sin(a) * 10), 2, 2, '#F7C873'); } }
        else { cloud(x - 12, y - 4, 24, 3); P(x - 10, y + 2, 20, 1, '#9AA0AD');
          if (ic.kind === 'snow') for (let i = 0; i < 4; i++) { const fy = (Math.floor(F / 4) + i * 3) % 10; DOT(x - 8 + i * 5, y + 5 + fy, '#FFF7EA'); DOT(x - 9 + i * 5, y + 5 + fy, '#E6D3BC'); }
          if (ic.kind === 'rain') for (let i = 0; i < 4; i++) { const fy = (Math.floor(F / 2) + i * 3) % 10; P(x - 8 + i * 5, y + 5 + fy, 1, 3, '#87CEEB'); } }
        if (ic.label) { const lx = x + 12, ly = y - 6; P(lx - 2, ly - 2, tw(ic.label) + 6, 17, INK); tx(ic.label, lx + 1, ly + 1, {color: '#FFF7EA'}); }
      };
      (o.icons || []).forEach(icon);
      // the lower third: the title block (above the host), the season strip (right of him)
      P(14, 238, Math.max(120, tw(o.title || 'FORECAST') + 20), 24, INK); P(15, 239, Math.max(118, tw(o.title || 'FORECAST') + 18), 22, '#E2633B'); P(15, 239, Math.max(118, tw(o.title || 'FORECAST') + 18), 1, '#F2A541');
      tx(o.title || 'FORECAST', 24, 244, {color: '#FFF7EA'});
      const mx = 96, my = 266, mw = 222, mh = 58;
      win(mx, my, mw, mh, {base: '#1B1420', hi: '#3D2E45', lo: '#120D14', rule: null});
      const ms = o.months || [], L = 'JFMAMJJASOND';
      for (let i = 0; i < 12; i++) {
        const bx = mx + 6 + i * 18, v = ms[i] || 0, p = o.monthsAt != null ? clamp((T - o.monthsAt - i * 0.05) / 0.3) : 1, h = Math.round(28 * v * easeOut(p));
        const hi = o.hi === i || (Array.isArray(o.hi) && o.hi.includes(i)), c = hi ? '#F2A541' : '#6FB7A8';
        P(bx, my + 34 - h, 13, h, c); if (h > 1) P(bx, my + 34 - h, 13, 1, hi ? '#F7C873' : '#BDE6F5'); P(bx + 11, my + 35 - h, 2, Math.max(0, h - 1), hi ? '#B07A47' : '#2F6F67');
        tx(L[i], bx + 6, my + 39, {color: hi ? '#F7C873' : '#C9CCD3', align: 'center'});
      }
      // the studio floor: a cable, tape marks
      P(0, 336, 360, 81, '#1B1420'); P(0, 417, 360, 223, '#2B2033'); for (let y = 430; y < 640; y += 30) P(0, y, 360, 1, '#3D2E45');
      return {area: area(X, Y, W, H), strip: area(mx, my, mw, mh), at: (nx, ny) => [(X + nx * W) * 3, (Y + ny * H) * 3]};
    };

    // ================================================================================================================
    // 10. counter: a storefront: brick, a striped awning, a sign, an OPEN sign that glows on and off once a second, a
    // counter with the item; the price tag hangs from the awning and flips (it narrows to its edge on whole pixels,
    // shows its back, turns to the new price) and sways to rest. o: {shop, item ('box'|'heater'|'toolbox'), tags: [{price, at}], note}
    S.counter = function (o = {}) {
      P(0, 0, 360, 110, '#7A3442'); for (let y = 0; y < 110; y += 5) for (let x = ((y / 5) & 1) * 6; x < 360; x += 12) P(x, y, 11, 4, '#E2633B');
      // the sign board over the awning (inside the safe area)
      const sw = Math.max(150, Math.ceil(tw(o.shop || 'SHOP')) + 30);
      P(180 - sw / 2 - 1, 79, sw + 2, 26, INK); bevel(180 - sw / 2, 80, sw, 24, '#253048', '#3B82C4', '#1B1420'); tx(o.shop || 'SHOP', 180, 88, {color: '#F7C873', align: 'center'});
      // the shop interior behind the glass: shelves of stock
      P(0, 104, 360, 146, '#3D2E45'); for (let x = 0; x < 360; x += 40) P(x, 104, 2, 146, '#2B2033');
      [[176, 0], [222, 1]].forEach(([y, s]) => { P(0, y, 360, 3, '#B07A47'); for (let x = 8 + s * 10; x < 352; x += 22) { const c = ['#6FB7A8', '#F2A541', '#87CEEB', '#E2633B'][Math.floor(hash(x + y) * 4)]; P(x, y - 14, 14, 14, c); P(x, y - 14, 14, 1, '#FFF7EA'); P(x + 12, y - 13, 2, 13, '#120D14'); } });
      // the awning: stripes and a scalloped edge
      for (let x = 0; x < 360; x += 24) { P(x, 110, 12, 14, '#E2633B'); P(x + 12, 110, 12, 14, '#FFF7EA'); }
      P(0, 108, 360, 2, '#7A3442');
      for (let x = 0; x < 360; x += 12) { disc(x + 6, 124, 4, (x / 12) % 2 ? '#FFF7EA' : '#E2633B'); P(x + 2, 124, 9, 1, (x / 12) % 2 ? '#E6D3BC' : '#7A3442'); }
      P(0, 129, 360, 2, '#1B1420');
      // the text panel (left): a chalk board on the wall, where the scene writes
      P(13, 135, 150, 82, INK); bevel(14, 136, 148, 80, '#8C5A33', '#D9A066', '#4A2E1B'); P(18, 140, 140, 72, '#24453A'); P(18, 140, 140, 1, '#1A332B');
      // the OPEN sign, glowing on and off once a second
      const on = Math.floor(T) % 2 === 0 || T < 1;
      P(296, 196, 44, 20, INK); P(297, 197, 42, 18, '#2B2033'); P(317, 186, 1, 10, '#9AA0AD'); tx('OPEN', 318, 200, {color: on ? '#E2633B' : '#7A3442', align: 'center', lint: false});
      // the counter and the item on it
      P(0, 250, 360, 8, '#D9A066'); P(0, 250, 360, 1, '#F7C873'); P(0, 257, 360, 2, '#6B4226'); P(0, 259, 360, 158, '#8C5A33');
      for (let x = 6; x < 360; x += 60) { bevel(x, 268, 52, 140, '#8C5A33', '#B07A47', '#4A2E1B'); P(x + 5, 274, 42, 128, '#6B4226'); }
      const it = o.item || 'box', ix = 176;
      if (it === 'heater') { P(ix - 1, 183, 46, 68, INK); P(ix, 184, 44, 66, '#C9CCD3'); P(ix, 184, 6, 66, '#FFF7EA'); P(ix + 36, 184, 8, 66, '#9AA0AD'); P(ix + 4, 180, 36, 5, '#9AA0AD'); P(ix + 15, 206, 14, 10, '#E2633B'); P(ix + 16, 207, 4, 2, '#F2A541'); P(ix + 20, 170, 4, 11, '#B07A47'); P(ix + 6, 240, 32, 2, '#9AA0AD'); }
      else if (it === 'toolbox') { P(ix - 1, 215, 52, 36, INK); P(ix, 216, 50, 34, '#E2633B'); P(ix, 216, 50, 2, '#F2A541'); P(ix + 42, 218, 8, 32, '#7A3442'); P(ix + 15, 206, 20, 3, '#4A4E5A'); P(ix + 15, 206, 2, 10, '#4A4E5A'); P(ix + 33, 206, 2, 10, '#4A4E5A'); P(ix, 230, 50, 2, '#7A3442'); P(ix + 21, 228, 8, 6, '#C9CCD3'); }
      else { P(ix - 1, 205, 50, 46, INK); P(ix, 206, 48, 44, '#D9A066'); P(ix, 206, 48, 2, '#F7C873'); P(ix + 40, 208, 8, 42, '#B07A47'); P(ix + 19, 206, 10, 44, '#E6D3BC'); P(ix + 6, 224, 10, 8, '#FFF7EA'); }
      // the price tag on its string, flipping to the new price and swaying to rest
      const tags = (o.tags || []).filter((t) => T >= t.at), cur = tags[tags.length - 1], prev = tags[tags.length - 2];
      if (cur) {
        const f = fr(cur.at), steps = [1, 0.75, 0.45, 0.15, 0.04, 0.15, 0.45, 0.75, 1], i = Math.min(steps.length - 1, Math.max(0, f)), flipping = !!prev && f < steps.length;
        const sf = f - (prev ? steps.length : 0), sway = !flipping && sf >= 0 && sf < 24 ? [1, 0, -1, 0][Math.floor(sf / 4) % 4] : 0;
        const label = flipping && i < 4 ? prev.price : cur.price, size = tw(label, 132) <= 92 ? 132 : 66;
        const fw = Math.max(70, Math.ceil(tw(label, size)) + 22), fh = th(size) + 20, w = flipping ? Math.max(2, Math.round(fw * steps[i])) : fw;
        const cx = 262 + sway, ty = 136, x = Math.round(cx - w / 2);
        line(262, 128, cx, ty, '#E6D3BC');
        P(x - 1, ty - 1, w + 2, fh + 2, INK); P(x, ty, w, fh, '#FFF7EA'); P(x, ty, w, 1, '#FFFFFF'); P(x, ty + fh - 2, w, 2, '#E6D3BC');
        if (w > 10) { P(cx - 1, ty + 3, 3, 3, INK); }
        if (!flipping || steps[i] === 1) tx(label, cx, ty + 11, {size, color: '#7A3442', align: 'center'});
        else if (w > 6) { P(x, ty, w, fh, '#E6D3BC'); for (let bx = x + 2; bx < x + w - 2; bx += 2 + (bx % 3 === 0 ? 1 : 0)) P(bx, ty + 8, 1, fh - 16, '#3D2E45'); }   // the back: a barcode
        if (!flipping && f >= 0 && f < 18) k.burst(cx * 3, (ty + fh / 2) * 3, cur.at + (prev ? steps.length / 30 : 0), {n: 10, r: 160, life: 0.5});
      }
      // the sidewalk
      P(0, 417, 360, 223, '#9AA0AD'); for (let y = 417; y < 640; y += 24) { P(0, y, 360, 1, '#6B7080'); for (let x = ((y / 24) & 1) * 30; x < 360; x += 60) P(x, y, 1, 24, '#6B7080'); }
      return {area: area(22, 144, 132, 64), tag: [262 * 3, 136 * 3]};
    };

    // ================================================================================================================
    // 11. gauge: a dashboard speedometer for a rate. The needle swings from the low end, overshoots and settles (its
    // angle stepped so the line is always whole pixels), the readout counts up. o: {value, max (100), at, dur (1.0),
    // zones: [[from, to, color]], label, suffix ('%'), prefix, dec, ticks (10), readout (true),
    // labels (true; false keeps only the 0 at the low end)}
    S.gauge = function (o = {}) {
      const max = o.max || 100, val = o.value != null ? o.value : 0, at = o.at || 0;
      P(0, 0, 360, 417, '#1B1420'); for (let y = 0; y < 417; y += 3) dith(0, y, 360, 1, '#2B2033', y % 2);
      const cx = 180, cy = 214, R = 100, a0 = Math.PI * 0.75, sweep = Math.PI * 1.5;
      // the hood: a curved cowl over the cluster
      for (let x = 0; x < 360; x++) { const h = Math.round(46 - 0.0012 * (x - 180) * (x - 180)); P(x, 84, 1, Math.max(0, h), '#2B2033'); DOT(x, 84 + Math.max(0, h), '#3D2E45'); }
      disc(cx, cy, R + 12, INK); disc(cx, cy, R + 10, '#4A4E5A'); disc(cx - 1, cy - 1, R + 8, '#9AA0AD'); disc(cx, cy, R + 7, '#6B7080'); disc(cx, cy, R + 4, INK); disc(cx, cy, R + 3, '#120D14');
      // zones and ticks
      const ang = (v) => a0 + sweep * clamp(v / max);
      (o.zones || [[0, max * 0.4, '#E2633B'], [max * 0.4, max * 0.7, '#F2A541'], [max * 0.7, max, '#6FB7A8']]).forEach(([v0, v1, c]) => { for (let a = ang(v0); a <= ang(v1); a += 0.006) for (let r = R - 8; r <= R - 3; r++) DOT(cx + Math.round(Math.cos(a) * r), cy + Math.round(Math.sin(a) * r), c); });
      const nt = o.ticks || 10;
      for (let i = 0; i <= nt; i++) { const a = a0 + sweep * i / nt, r1 = i % 5 === 0 ? R - 20 : R - 14; line(cx + Math.cos(a) * r1, cy + Math.sin(a) * r1, cx + Math.cos(a) * (R - 10), cy + Math.sin(a) * (R - 10), '#FFF7EA', i % 5 === 0 ? 2 : 1); }
      (o.labels === false ? [[0, '0']] : [[0, '0'], [nt / 2, String(max / 2)], [nt, String(max)]]).forEach(([i, s]) => { const a = a0 + sweep * i / nt; tx(s, cx + Math.cos(a) * (R - 32), cy + Math.sin(a) * (R - 32) - 10, {color: '#C9CCD3', align: 'center'}); });
      // the needle: overshoot and settle, the angle stepped to whole degrees
      const d = Math.max(0, T - at), dur = o.dur || 1.0;
      const rise = clamp(d / (dur * 0.55)), base = val * easeOut(rise), wob = d > dur * 0.55 ? val * 0.06 * Math.exp(-5 * (d - dur * 0.55)) * Math.sin((d - dur * 0.55) * 16) : 0;
      const nv = T < at ? 0 : base + wob, na = Math.round((a0 + sweep * clamp(nv / max, -0.02, 1.02)) * 180 / Math.PI) * Math.PI / 180;
      line(cx + 1, cy + 1, cx + 1 + Math.round(Math.cos(na) * (R - 16)), cy + 1 + Math.round(Math.sin(na) * (R - 16)), '#120D14', 2);
      line(cx, cy, cx + Math.round(Math.cos(na) * (R - 16)), cy + Math.round(Math.sin(na) * (R - 16)), '#E2633B', 2);
      line(cx, cy, cx + Math.round(Math.cos(na) * (R - 30)), cy + Math.round(Math.sin(na) * (R - 30)), '#F2A541', 1);
      disc(cx, cy, 9, INK); disc(cx, cy, 8, '#4A4E5A'); disc(cx - 1, cy - 1, 6, '#9AA0AD'); DOT(cx - 3, cy - 3, '#FFF7EA');
      // the glass glint
      line(cx - 70, cy - 40, cx - 40, cy - 70, '#3D2E45'); line(cx - 66, cy - 34, cx - 34, cy - 66, '#3D2E45');
      // the readout under the hub (inside the dial), counting as the needle rises
      const shownV = T < at ? (o.from != null ? o.from : 0) : (d >= dur ? val : val * easeOut(rise));
      const s = (o.prefix || '') + (d >= dur ? val.toFixed(o.dec || 0) : shownV.toFixed(o.dec || 0)) + (o.suffix != null ? o.suffix : '%');
      if (o.readout !== false) {   // readout: false leaves the face clear for a scene's own hero number (Oct 31, 2026)
        P(cx - 38, cy + 18, 76, 30, INK); P(cx - 37, cy + 19, 74, 28, '#1A332B'); P(cx - 36, cy + 20, 72, 26, '#24453A');
        tx(s, cx, cy + 22, {size: 66, color: '#F7C873', align: 'center'});
      }
      if (o.label) tx(o.label, cx, 92, {align: 'center', color: '#FFF7EA', drop: INK});
      // side gauges: fuel and temp, small and still
      [[38, 'F'], [322, 'H']].forEach(([x, s2], i) => { const y = 150; disc(x, y, 18, INK); disc(x, y, 16, '#2B2033'); ring(x, y, 16, '#6B7080'); line(x, y, x + (i ? -8 : 10), y - 9, '#F2A541'); disc(x, y, 2, '#9AA0AD'); });
      // the dash and the floor
      P(0, 330, 360, 87, '#2B2033'); P(0, 330, 360, 2, '#3D2E45'); P(0, 417, 360, 223, '#1B1420'); for (let y = 424; y < 640; y += 8) P(20, y, 320, 2, '#2B2033');
      return {area: area(cx - 100, 84, 200, 30), readout: [(cx - 38) * 3, (cy + 18) * 3]};
    };

    // ================================================================================================================
    // 12. slots: a slot machine for a number. The lever is pulled at t0, three reels spin (whole pixels, 6 a frame) and
    // stop left to right with a bounce on the target symbols; then the lights chase and the coins jump.
    // o: {t0, stops: [t, t, t], symbols: ['5', '7', '%'], label, win (true)}
    S.slots = function (o = {}) {
      const t0 = o.t0 || 0, sy = o.symbols || ['7', '7', '7'], stops = o.stops || [t0 + 0.9, t0 + 1.3, t0 + 1.7];
      P(0, 0, 360, 417, '#3D2E45'); for (let i = 0; i < 60; i++) DOT(Math.floor(hash(i * 1.9) * 360), Math.floor(hash(i * 3.3) * 400), '#7A3442');
      const X = 40, Y = 84, W = 260, H = 236;
      // cabinet: red with gold trim, a lit crown with bulbs that chase
      P(X - 2, Y - 2, W + 4, H + 4, INK); P(X, Y, W, H, '#7A3442'); P(X, Y, W, 2, '#E2633B'); P(X, Y, 2, H, '#E2633B'); P(X + W - 3, Y, 3, H, '#3D2E45');
      P(X + 6, Y + 6, W - 12, 34, '#F2A541'); P(X + 6, Y + 6, W - 12, 2, '#F7C873'); P(X + 6, Y + 38, W - 12, 2, '#B07A47'); P(X + 10, Y + 10, W - 20, 26, '#7A3442');
      const allStop = T >= stops[2] + 0.2;
      for (let i = 0; i < 16; i++) { const lit = allStop ? (i + Math.floor(F / 3)) % 2 === 0 : (i + Math.floor(F / 6)) % 4 === 0; DOT(X + 12 + i * 15, Y + 8, lit ? '#FFF7EA' : '#B07A47'); DOT(X + 12 + i * 15, Y + 37, lit ? '#FFF7EA' : '#B07A47'); }
      tx(o.label || 'JACKPOT', X + W / 2, Y + 16, {color: '#F7C873', align: 'center'});
      // the reels
      const RW = 70, RH = 92, ry = Y + 52, SYM = ['7', '$', '%', '9', '3', '5', '1', '0', '8', '2', '4', '6'];
      for (let r = 0; r < 3; r++) {
        const rx = X + 18 + r * (RW + 7);
        P(rx - 2, ry - 2, RW + 4, RH + 4, INK); P(rx, ry, RW, RH, '#FFF7EA');
        clip(rx, ry, RW, RH, () => {
          const spinning = T >= t0 && T < stops[r], sf = fr(stops[r]), cell = 50;
          if (spinning) {
            const off = (fr(t0) * 6) % cell;
            for (let j = -1; j < 3; j++) { const idx = Math.floor(hash(r * 7 + Math.floor(fr(t0) * 6 / cell) - j) * SYM.length); tx(SYM[idx], rx + RW / 2, ry + 21 - cell + j * cell + off, {size: 132, color: '#2B2033', align: 'center', lint: false}); }
          } else {
            const b = T >= t0 && sf >= 0 ? [6, -3, 1, 0][Math.min(3, sf)] : 0;
            const shown = T < t0 ? (o.idle || ['7', '$', '7'])[r] : sy[r];
            tx(shown, rx + RW / 2, ry + 24 + b, {size: 132, color: T >= t0 && r === 2 && !/\d/.test(sy[r]) ? '#E2633B' : '#2B2033', align: 'center'});
            tx(SYM[(r * 3 + 1) % SYM.length], rx + RW / 2, ry + 24 + b - cell, {size: 132, color: '#C9CCD3', align: 'center', lint: false});
            tx(SYM[(r * 3 + 5) % SYM.length], rx + RW / 2, ry + 24 + b + cell, {size: 132, color: '#C9CCD3', align: 'center', lint: false});
          }
          P(rx, ry, RW, 6, '#E6D3BC'); P(rx, ry + RH - 6, RW, 6, '#E6D3BC'); P(rx, ry, RW, 2, '#B39A88'); P(rx, ry + RH - 2, RW, 2, '#B39A88');
        });
      }
      P(X + 10, ry + RH / 2, 6, 2, '#F2A541'); P(X + W - 16, ry + RH / 2, 6, 2, '#F2A541');   // the pay line arrows
      // the lever: a ball on a rod, pulled down in 3 steps and back
      const lf = fr(t0), pull = lf >= 0 && lf < 18 ? [6, 14, 22, 26, 26, 26, 24, 20, 16, 12, 9, 6, 4, 3, 2, 1, 0, 0][lf] : 0;
      P(X + W + 2, Y + 90, 8, 30, '#4A4E5A'); P(X + W + 2, Y + 90, 8, 2, '#9AA0AD');
      P(X + W + 6, Y + 54 + pull, 3, 46 - pull, '#9AA0AD'); P(X + W + 6, Y + 54 + pull, 1, 46 - pull, '#C9CCD3');
      disc(X + W + 7, Y + 50 + pull, 7, INK); disc(X + W + 7, Y + 50 + pull, 6, '#E2633B'); DOT(X + W + 5, Y + 47 + pull, '#FFF7EA'); DOT(X + W + 6, Y + 47 + pull, '#F7C873');
      // the tray and the coins
      P(X + 20, Y + 160, W - 40, 50, INK); P(X + 22, Y + 162, W - 44, 46, '#2B2033'); P(X + 22, Y + 162, W - 44, 2, '#120D14');
      P(X + 10, Y + 210, W - 20, 6, '#F2A541'); P(X + 10, Y + 210, W - 20, 1, '#F7C873');
      if (o.win !== false && allStop) { const n = Math.min(26, Math.max(0, fr(stops[2] + 0.4) >> 1)); for (let i = 0; i < n; i++) { const row = i < 10 ? 0 : (i < 18 ? 1 : (i < 23 ? 2 : 3)), idx = row === 0 ? i : (row === 1 ? i - 10 : (row === 2 ? i - 18 : i - 23)), w = [10, 8, 5, 3][row]; coin(X + W / 2 - w * 5 + idx * 10 + (row % 2) * 5, Y + 198 - row * 6, 0); } }
      if (o.win !== false && allStop) for (let i = 0; i < 12; i++) { const d = T - stops[2] - 0.2 - i * 0.06; if (d < 0) continue; const ph = d % 1.2, vx = (hash(i * 3.1) - 0.5) * 140, cx2 = X + W / 2 + vx * ph, cy2 = Y + 190 - 160 * ph + 260 * ph * ph; if (cy2 < Y + 206) coin(Math.round(cx2), Math.round(cy2), Math.floor(F / 2) + i); }
      // a casino carpet
      P(0, 320, 360, 97, '#2B2033'); P(0, 417, 360, 223, '#7A3442');
      for (let y = 420; y < 640; y += 16) for (let x = ((y / 16) & 1) * 16; x < 360; x += 32) { DOT(x + 8, y + 8, '#F2A541'); DOT(x + 7, y + 8, '#B07A47'); DOT(x + 9, y + 8, '#B07A47'); DOT(x + 8, y + 7, '#B07A47'); DOT(x + 8, y + 9, '#B07A47'); }
      return {area: area(X + 10, Y + 10, W - 20, 26), reels: area(X + 18, ry, 3 * RW + 14, RH)};
    };

    // ================================================================================================================
    // 13. inventory: an RPG item screen. A tool belt of eight slots with pixel icons; the cursor jumps from slot to slot
    // (its corner brackets breathing in and out a pixel), the detail pane names the item and fills its stat bars.
    // o: {title ('TOOL BELT'), items: [{icon, name, stats: [{label, value, max, text}]}], select: [{slot, at}]}
    const ICONS = {
      wrench: ['....aa....', '...aab....', '...ab.....', '...abb..a.', '....abbaab', '.....abbb.', '....abb...', '...abb....', '..abb.....', '.abb......'],
      phone: ['.cccccc...', '.cddddc...', '.cdeedc...', '.cddddc...', '.cddddc...', '.cddddc...', '.cddddc...', '.cccccc...', '.cc..cc...', '.cccccc...'],
      clip: ['...ff.....', '.gfggfg...', '.ghhhhg...', '.giiiig...', '.ghhhhg...', '.giiiig...', '.ghhhhg...', '.giiiig...', '.ghhhhg...', '.gggggg...'],
      mail: ['..........', 'jjjjjjjjj.', 'jkjjjjjkj.', 'jjkjjjkjj.', 'jjjkjkjjj.', 'jjjjkjjjj.', 'jjjjjjjjj.', 'jjjjjjjjj.', '..........', '..........'],
      star: ['....l.....', '....l.....', '...lml....', 'lllmmmlll.', '.lmmmmml..', '..lmmml...', '..lm.ml...', '.lm...ml..', '.l.....l..', '..........'],
      coin: ['...nnnn...', '..noooon..', '.nopppoon.', '.nopnnoon.', '.noppooon.', '.noonpoon.', '.nopppoon.', '..noooon..', '...nnnn...', '..........'],
      clock: ['...qqqq...', '..qrrrrq..', '.qrrsrrrq.', '.qrrsrrrq.', '.qrrssrrq.', '.qrrrrrrq.', '.qrrrrrrq.', '..qrrrrq..', '...qqqq...', '..........'],
      horn: ['.......t..', '......tt..', '.....tut..', 'tt..tuut..', 'tuttuuut..', 'tuttuuut..', 'tt..tuut..', '.....tut..', '......tt..', '.......t..'],
      hammer: ['.vvvvv....', '.vwwwvv...', '.vvvvv....', '...x......', '...x......', '...x......', '...x......', '...x......', '...y......', '..........'],
    };
    const IPAL = {a: '#C9CCD3', b: '#6B7080', c: '#120D14', d: '#3B82C4', e: '#87CEEB', f: '#9AA0AD', g: '#B07A47', h: '#FFF7EA', i: '#E6D3BC',
      j: '#F4E6D3', k: '#E2633B', l: '#B07A47', m: '#F7C873', n: '#B07A47', o: '#F2A541', p: '#F7C873', q: '#3D2E45', r: '#FFF7EA', s: '#E2633B',
      t: '#7A3442', u: '#E2633B', v: '#6B7080', w: '#C9CCD3', x: '#8C5A33', y: '#5A3A22'};
    S.icon = (name, x, y, s = 2) => spr(ICONS[name] || ICONS.star, IPAL, x, y, s);
    S.inventory = function (o = {}) {
      P(0, 0, 360, 417, '#1B1420'); for (let i = 0; i < 50; i++) twinkle(Math.floor(hash(i * 2.2) * 360), Math.floor(hash(i * 6.6) * 410), (Math.floor(F / 8) + i) % 12 < 4 ? (Math.floor(F / 8) + i) % 4 : 0, i % 3 ? '#3D2E45' : '#6B7080');
      const X = 16, Y = 94, W = 316, H = 178;
      win(X, Y, W, H, {});
      P(X + 10, Y - 6, tw(o.title || 'TOOL BELT') + 14, 13, INK); P(X + 11, Y - 5, tw(o.title || 'TOOL BELT') + 12, 11, '#7A3442'); tx(o.title || 'TOOL BELT', X + 17, Y - 5, {color: '#FFF7EA'});
      const items = o.items || [], sel = (o.select || []).filter((s) => T >= s.at), cur = sel[sel.length - 1], prev = sel[sel.length - 2];
      const slot = (i) => [X + 12 + (i % 4) * 40, Y + 14 + Math.floor(i / 4) * 40];
      for (let i = 0; i < 8; i++) { const [sx, sy] = slot(i); P(sx, sy, 34, 34, '#1B1420'); P(sx, sy, 34, 1, '#120D14'); P(sx, sy + 33, 34, 1, '#3B82C4'); P(sx + 33, sy, 1, 34, '#3B82C4'); if (items[i]) S.icon(items[i].icon, sx + 7, sy + 7, 2); }
      // the belt strap under the slots
      P(X + 8, Y + 98, 160, 4, '#6B4226'); P(X + 8, Y + 98, 160, 1, '#B07A47'); P(X + 80, Y + 96, 12, 8, '#F2A541'); P(X + 82, Y + 98, 8, 4, '#6B4226');
      if (!cur) { P(X + 178, Y + 14, 124, 34, '#1B1420'); tx(o.hint || 'Pick a tool', X + 186, Y + 25, {color: '#6B7080'}); }
      if (cur) {
        const [ax, ay] = slot(cur.slot), [bx0, by0] = prev ? slot(prev.slot) : [ax, ay], q = easeOut(fr(cur.at) / 4);
        const cx = Math.round(bx0 + (ax - bx0) * q), cy = Math.round(by0 + (ay - by0) * q), b = ((F >> 3) & 1);
        [[0, 0, 1, 1], [34, 0, -1, 1], [0, 34, 1, -1], [34, 34, -1, -1]].forEach(([dx, dy, sx2, sy2]) => { const px = cx + dx - sx2 * (2 + b), py = cy + dy - sy2 * (2 + b); P(sx2 > 0 ? px : px - 5, py - (sy2 > 0 ? 0 : 1), 6, 2, '#F7C873'); P(px - (sx2 > 0 ? 0 : 1), sy2 > 0 ? py : py - 5, 2, 6, '#F7C873'); });
        // the detail pane (right)
        const it = items[cur.slot]; const dx = X + 178, dy = Y + 14;
        P(dx, dy, 124, 34, '#1B1420'); if (it) { S.icon(it.icon, dx + 4, dy + 7, 2); tx(it.name, dx + 30, dy + 11, {color: '#F7C873'}); }
        if (it) (it.stats || []).forEach((s, j) => {
          const y = Y + 58 + j * 36; tx(s.label, dx, y, {color: '#FFF7EA'});
          const p = clamp((T - cur.at - 0.15 - j * 0.12) / 0.4), fw = Math.round(120 * clamp(s.value / (s.max || 100)) * easeOut(p));
          P(dx, y + 17, 124, 8, INK); P(dx + 1, y + 18, 122, 6, '#3D2E45'); P(dx + 1, y + 18, fw, 6, '#6FB7A8'); P(dx + 1, y + 18, fw, 1, '#BDE6F5');
          for (let x = dx + 13; x < dx + 122; x += 12) P(x, y + 18, 1, 6, INK);
          tx(s.text || String(s.value), dx + 121, y, {color: '#6FB7A8', align: 'right'});
        });
      }
      // the stash below: an item count line
      if (o.footer) tx(o.footer, X + 12, Y + 112, {color: '#C9CCD3'});
      P(0, 296, 360, 121, '#2B2033'); P(0, 296, 360, 2, '#3D2E45');
      planks(417, 223, '#6B4226', '#8C5A33', '#4A2E1B');
      return {area: area(X + 8, Y + 108, 160, 60), detail: area(X + 178, Y + 14, 124, 160)};
    };

    // ================================================================================================================
    // 14. levelup: an XP bar fills in segments, the level ticks over with LEVEL UP stamped in, rays turn behind it (a
    // step every 4 frames), new stats land one by one. o: {from, to, max, at, dur, levelAt, level, stats: [{text, at}]}
    S.levelup = function (o = {}) {
      P(0, 0, 360, 417, '#2B2033');
      const lv = o.levelAt != null && T >= o.levelAt, cx = 180, cy = 150;
      if (lv) { const rot = Math.floor(fr(o.levelAt) / 4) * (TAU / 96); for (let i = 0; i < 12; i++) { const a0 = rot + i * TAU / 12, a1 = a0 + TAU / 24; ctx.fillStyle = i % 2 ? '#3D2E45' : '#7A3442'; ctx.beginPath(); ctx.moveTo(cx * 3, cy * 3); ctx.lineTo((cx + Math.cos(a0) * 400) * 3, (cy + Math.sin(a0) * 400) * 3); ctx.lineTo((cx + Math.cos(a1) * 400) * 3, (cy + Math.sin(a1) * 400) * 3); ctx.closePath(); ctx.fill(); } }
      else for (let i = 0; i < 40; i++) DOT(Math.floor(hash(i * 3.9) * 360), Math.floor(hash(i * 1.1) * 330), '#3D2E45');
      for (let i = 0; i < 10; i++) { const f = Math.floor(F / 5) + i * 3; twinkle(Math.floor(hash(i * 7.1) * 340) + 10, 90 + Math.floor(hash(i * 2.9) * 180), f % 8 < 4 ? f % 4 : 0, i % 2 ? '#F7C873' : '#FFF7EA'); }
      // the bar
      const max = o.max || 100, from = o.from || 0, to = o.to != null ? o.to : max, at = o.at || 0, dur = o.dur || 1.2;
      const raw = from + (to - from) * easeOut(clamp((T - at) / dur)), seg = 20, X = 30, Y = 208, W = 280;
      const v = lv ? raw - max : Math.min(max, raw), lvl = (o.level || 1) + (lv ? 1 : 0);
      tx('LV ' + lvl, X, Y - 18, {color: '#F7C873'}); tx('XP', X + W, Y - 18, {color: '#C9CCD3', align: 'right'});
      P(X - 2, Y - 2, W + 4, 18, INK); P(X - 1, Y - 1, W + 2, 16, '#6B7080'); P(X, Y, W, 14, '#1B1420');
      const n = Math.floor(seg * clamp(v / max) + 0.0001), sw = W / seg;
      for (let i = 0; i < n; i++) { const x = Math.round(X + i * sw); P(x + 1, Y + 1, Math.round(sw) - 2, 12, '#6FB7A8'); P(x + 1, Y + 1, Math.round(sw) - 2, 3, '#BDE6F5'); P(x + 1, Y + 10, Math.round(sw) - 2, 3, '#2F6F67'); }
      if (n < seg && T >= at && T < at + dur && !lv) { const x = Math.round(X + n * sw); if ((F >> 1) & 1) P(x + 1, Y + 1, Math.round(sw) - 2, 12, '#3D2E45'); }
      if (lv) k.slam(o.text || 'LEVEL UP!', 540, 360, o.levelAt, {size: 132, color: 'accent', align: 'center', stamp: true, glint: false});
      if (lv) k.burst(540, 420, o.levelAt + 0.1, {n: 18, r: 300});
      (o.stats || []).forEach((s, i) => { if (T < s.at) return; const sl = ease(s.at, 5, 30); tx('+', 110 + sl, 236 + i * 18, {color: '#6FB7A8'}); tx(s.text, 122 + sl, 236 + i * 18, {color: '#FFF7EA'}); });
      P(0, 330, 360, 87, '#1B1420'); P(0, 330, 360, 2, '#3D2E45'); tiles(417, 223, '#2B2033', '#1B1420', 20, '#120D14');
      return {area: area(100, 232, 240, 50), bar: area(X, Y, W, 14)};
    };

    // ================================================================================================================
    // 15. versus: a fighting-game select screen. Two sides split on a slant, speed lines streaming toward the middle,
    // name plates slide in from the edges, VS slams in, the stats fill, and the winner's side lights up while the
    // loser dims. o: {a: {name, icon, stats: [{label, value, text}], c}, b: {...}, at, vsAt, winner ('a'|'b'), winAt, max}
    S.versus = function (o = {}) {
      const a = o.a || {name: 'SHOP A'}, b = o.b || {name: 'SHOP B'}, at = o.at || 0, vsAt = o.vsAt != null ? o.vsAt : at + 0.3, MID = 168;
      const split = (y) => MID - Math.round((y - 200) * 0.12);
      for (let y = 0; y < 417; y++) { const sx = split(y); P(0, y, sx, 1, '#245752'); P(sx, y, 360 - sx, 1, '#7A3442'); P(sx - 1, y, 2, 1, '#FFF7EA'); }
      for (let i = 0; i < 24; i++) { const y = 80 + Math.floor(hash(i * 1.7) * 330), l = 14 + Math.floor(hash(i * 4.1) * 24), sp = 4 + Math.floor(hash(i * 9.3) * 4), x = ((Math.floor(F * sp / 2) + Math.floor(hash(i) * 200)) % 220) - 40;
        const sx = split(y); if (i % 2) { if (x + l < sx - 4) P(x, y, l, 1, '#2F6F67'); } else { const xr = 360 - x - l; if (xr > sx + 4) P(xr, y, l, 1, '#E2633B'); } }
      const W = 140;
      const side = (s, left) => {
        const X = left ? 20 : 176, sl = ease(at, 8, left ? -170 : 190), win2 = o.winner && o.winAt != null && T >= o.winAt, dim = win2 && o.winner !== (left ? 'a' : 'b');
        const x = X + sl;
        // the portrait card: the icon at 4x on a lit panel
        win(x, 86, W, 92, {base: left ? '#2F6F67' : '#E2633B', hi: left ? '#6FB7A8' : '#F2A541', lo: left ? '#245752' : '#7A3442', rule: '#FFF7EA'});
        S.icon(s.icon || (left ? 'wrench' : 'clip'), x + W / 2 - 20, 112, 4);
        // the name plate
        P(x, 184, W, 20, INK); P(x + 1, 185, W - 2, 18, '#1B1420'); tx(s.name, x + W / 2, 188, {color: left ? '#6FB7A8' : '#F2A541', align: 'center'});
        // the stats
        (s.stats || []).forEach((st, j) => {
          const y = 212 + j * 30, p = clamp((T - vsAt - 0.3 - j * 0.15) / 0.4), max = st.max || o.max || 100, fw = Math.round((W - 4) * clamp(st.value / max) * easeOut(p));
          tx(st.label, x + 2, y, {color: '#FFF7EA', drop: INK}); tx(st.text || String(st.value), x + W - 4, y, {color: '#F7C873', align: 'right', drop: INK});
          P(x, y + 16, W, 8, INK); P(x + 1, y + 17, W - 2, 6, '#3D2E45'); P(left ? x + 1 : x + W - 1 - fw, y + 17, fw, 6, left ? '#6FB7A8' : '#F2A541'); P(left ? x + 1 : x + W - 1 - fw, y + 17, fw, 1, '#FFF7EA');
        });
        if (dim) { ctx.fillStyle = '#120D14'; for (let yy = 84; yy < 272; yy++) for (let xx = x - 2 + (yy & 1); xx < x + W + 2; xx += 2) ctx.fillRect(xx * 3, yy * 3, 3, 3); }
        if (win2 && !dim) k.slam(o.winText || 'WIN', (x + W / 2) * 3, 92 * 3, o.winAt, {size: 66, color: '#FFF7EA', align: 'center', stamp: true, glint: false, drop: INK});
      };
      side(a, true); side(b, false);
      // VS: a bolt behind the letters, slammed on the split
      if (T >= vsAt) {
        const bolt = [[MID + 8, 100], [MID - 4, 132], [MID + 6, 132], [MID - 8, 166], [MID + 12, 126], [MID + 2, 126], [MID + 14, 100]];
        ctx.fillStyle = '#120D14'; ctx.beginPath(); bolt.forEach(([x, y], i) => i ? ctx.lineTo((x + 1) * 3, (y + 1) * 3) : ctx.moveTo((x + 1) * 3, (y + 1) * 3)); ctx.closePath(); ctx.fill();
        ctx.fillStyle = '#F7C873'; ctx.beginPath(); bolt.forEach(([x, y], i) => i ? ctx.lineTo(x * 3, y * 3) : ctx.moveTo(x * 3, y * 3)); ctx.closePath(); ctx.fill();
        k.slam('VS', MID * 3, 400, vsAt, {size: 132, color: '#FFF7EA', align: 'center', stamp: true, glint: false, drop: '#120D14'});
      }
      P(0, 330, 360, 87, '#1B1420'); P(0, 330, 360, 2, '#3D2E45'); tiles(417, 223, '#2B2033', '#1B1420', 20, '#120D14');
      return {a: area(20, 86, W, 186), b: area(176, 86, W, 186)};
    };

    // ================================================================================================================
    // 16. hud: an overlay for any scene: coins rain (spinning, on whole pixels) and a counter ticks up; a row of hearts
    // fills; a progress bar with a label. Draw it last. o: {coins: {at, dur, n, x0, x1, floor}, counter: {x, y, from, to,
    // at, dur, prefix, suffix}, hearts: {x, y, n, lit, at}, bar: {x, y, w, label, from, to, at, dur, max}}
    S.hud = function (o = {}) {
      if (o.coins) { const c = o.coins, n = c.n || 24, x0 = c.x0 != null ? c.x0 : 20, x1 = c.x1 != null ? c.x1 : 340, fl = c.floor || 300;
        for (let i = 0; i < n; i++) { const t = c.at + hash(i * 3.7) * (c.dur || 1.2), d = T - t; if (d < 0) continue; const y = -10 + 360 * d * d + 40 * d, x = x0 + Math.floor(hash(i * 1.9) * (x1 - x0)); if (y > fl) { const f2 = Math.floor((y - fl) / 20); if (f2 < 4) twinkle(x + 4, fl + 4, f2 + 1, '#F7C873'); continue; } x2(x, Math.round(y), () => coin(0, 0, Math.floor(F / 2) + i)); } }
      if (o.counter) { const c = o.counter, x = c.x != null ? c.x : 230, y = c.y != null ? c.y : 84;
        x2(x, y + 3, () => coin(0, 0, Math.floor(F / 6))); tx('x', x + 20, y + 4, {color: '#FFF7EA', drop: INK});
        tx(k.count(c.to, clamp((T - c.at) / (c.dur || 1)), {from: c.from || 0, comma: true, prefix: c.prefix, suffix: c.suffix}), x + 30, y, {size: 66, color: '#F7C873', drop: INK}); }
      if (o.hearts) { const h = o.hearts; for (let i = 0; i < (h.n || 5); i++) { const x = (h.x || 20) + i * 18, y = h.y || 84, lit = i < (h.lit || 0) && T >= (h.at || 0) + i * 0.12, pop = lit && fr((h.at || 0) + i * 0.12) < 3 ? -1 : 0;
        const HEART = ['.aa.aa.', 'abbabba', 'abccbba', 'abbbbba', '.abbba.', '..aba..', '...a...']; spr(HEART, {a: INK, b: lit ? '#E2633B' : '#3D2E45', c: lit ? '#FFF7EA' : '#6B7080'}, x, y + pop, 2); } }
      if (o.bar) { const b = o.bar, x = b.x || 100, y = b.y || 300, w = b.w || 200, v = (b.from || 0) + ((b.to != null ? b.to : 100) - (b.from || 0)) * easeOut(clamp((T - (b.at || 0)) / (b.dur || 1))), fw = Math.round((w - 2) * clamp(v / (b.max || 100)));
        if (b.label) tx(b.label, x, y - 16, {color: '#FFF7EA', drop: INK});
        P(x - 1, y - 1, w + 2, 10, INK); P(x, y, w, 8, '#3D2E45'); P(x + 1, y + 1, fw, 6, b.c || '#6FB7A8'); P(x + 1, y + 1, fw, 2, '#BDE6F5'); }
    };

    // ---- transitions the player can use (SCENE.transitions = {sectionId: 'levelselect' | 'dissolve' | 'gameover'}) ----
    return S;
  }

  // Room-to-room moves for the player (player.js reads window.SETS.transitions). Each gets the 2D context (frame units),
  // q (0 open .. 1 shut), and {closing, cell, W, H, fill, hash, head}. Everything on the low-res grid.
  const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];
  const transitions = {
    // a level-select wipe: square tiles grow from nothing to full, in a diagonal wave from the top left
    levelselect(ctx, q, e) {
      const s = 24 * 3, cols = Math.ceil(e.W / s), rows = Math.ceil(e.H / s);
      for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
        const d = (c + r * 0.6) / (cols + rows * 0.6), g = clamp(q * 1.6 - d * 0.6), half = Math.round(g * 12) * 3;
        if (half <= 0) continue; const cx = c * s + s / 2, cy = r * s + s / 2;
        e.fill('#1B1420', cx - half, cy - half, 2 * half, 2 * half); if (half < s / 2 - 3 && half > 6) { e.fill('#F2A541', cx - half, cy - half, 2 * half, 3); e.fill('#F2A541', cx - half, cy - half, 3, 2 * half); }
      }
    },
    // a pixel dissolve: an ordered (Bayer) pattern of 4-pixel blocks fills in, then clears
    dissolve(ctx, q, e) {
      const b = 12, th = Math.round(q * 16);
      for (let y = 0; y < e.H; y += b) for (let x = 0; x < e.W; x += b) { const v = BAYER[((y / b) % 4) * 4 + ((x / b) % 4)]; if (v < th) e.fill('#120D14', x, y, b, b); }
    },
    // game over: black closes from the top and bottom to a bright line, the line shrinks to a dot (a CRT switching off)
    gameover(ctx, q, e) {
      const mid = 960, h = Math.round((1 - Math.min(1, q * 1.25)) * mid / 3) * 3;
      e.fill('#120D14', 0, 0, e.W, mid - h); e.fill('#120D14', 0, mid + h, e.W, e.H - mid - h);
      if (q > 0.75) { const w = Math.round((1 - (q - 0.75) / 0.25) * e.W / 6) * 3; e.fill('#120D14', 0, mid - 6, e.W, 12); if (w > 0) { e.fill('#BDE6F5', e.W / 2 - w - 6, mid - 6, 2 * w + 12, 12); e.fill('#FFF7EA', e.W / 2 - w, mid - 3, 2 * w, 6); } }
    },
  };

  const SETS_KEY = '__sets';
  const make0 = window.Kit.make;
  window.Kit.make = function (ctx, look, T, env) {
    const k = make0(ctx, look, T, env);
    Object.defineProperty(k, 'sets', {get() { return this[SETS_KEY] || (this[SETS_KEY] = build(this)); }, configurable: true});
    Object.defineProperty(k, 'set', {get() { return this.sets; }, configurable: true});
    return k;
  };
  window.SETS = {transitions, ramps: RAMP, names: ['street', 'dispatch', 'scores', 'boss', 'register', 'calendar', 'flaps', 'chat', 'weather', 'counter', 'gauge', 'slots', 'inventory', 'levelup', 'versus', 'hud']};
})();
