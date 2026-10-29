// The kit: everything scene.js can draw (_shared/kit.md). One drawing path for every look: shapes are polylines, so the
// chalk look can boil its lines and the line-art looks can trace them; the pixel look draws the same calls at a third of
// the size and the player snaps the frame to its palette.
(function () {
  const TAU = Math.PI * 2;
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const ease = (x) => { x = clamp(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
  const easeOut = (x) => 1 - Math.pow(1 - clamp(x), 3);
  const back = (x) => { x = clamp(x); const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
  const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
  const strHash = (s) => { let h = 7; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) % 100003; return h; };

  let CHUNKY = 0;
  const CLOUDS = {};   // pixel cloud sprites, built once
  function rectPts(x, y, w, h, r = 0) {
    if (CHUNKY) { const c = Math.min(CHUNKY, w / 4, h / 4); return [[x + c, y], [x + w - c, y], [x + w - c, y + c], [x + w, y + c], [x + w, y + h - c], [x + w - c, y + h - c], [x + w - c, y + h], [x + c, y + h], [x + c, y + h - c], [x, y + h - c], [x, y + c], [x + c, y + c]]; }
    r = Math.min(r, w / 2, h / 2);
    if (r <= 0.5) return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];
    const pts = [], seg = 6;
    const corner = (cx, cy, a0) => { for (let i = 0; i <= seg; i++) { const a = a0 + (i / seg) * (Math.PI / 2); pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]); } };
    corner(x + w - r, y + r, -Math.PI / 2); corner(x + w - r, y + h - r, 0); corner(x + r, y + h - r, Math.PI / 2); corner(x + r, y + r, Math.PI);
    return pts;
  }
  function ellPts(cx, cy, rx, ry, n = 36, a0 = 0, a1 = TAU) {
    const pts = []; for (let i = 0; i <= n; i++) { const a = a0 + (a1 - a0) * (i / n); pts.push([cx + rx * Math.cos(a), cy + ry * Math.sin(a)]); } return pts;
  }
  // A rounded limb from a to b (a capsule): a polygon so every look can fill or trace it.
  function capsule(a, b, r) {
    const dx = b[0] - a[0], dy = b[1] - a[1], ang = Math.atan2(dy, dx);
    const pts = [];
    for (let i = 0; i <= 10; i++) { const t = ang + Math.PI / 2 + (i / 10) * Math.PI; pts.push([a[0] + r * Math.cos(t), a[1] + r * Math.sin(t)]); }
    for (let i = 0; i <= 10; i++) { const t = ang - Math.PI / 2 + (i / 10) * Math.PI; pts.push([b[0] + r * Math.cos(t), b[1] + r * Math.sin(t)]); }
    return pts;
  }

  function make(ctx, look, T, env) {
    const C = look.c;
    CHUNKY = look.chunky ? 6 : 0;
    const boil = Math.floor(T * 8);
    let uid = 0;
    const col = (c) => (c && C[c]) ? C[c] : c;

    function trace(pts, closed) {
      ctx.beginPath();
      pts.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])));
      if (closed) ctx.closePath();
    }
    function jitter(pts, id, amt) {
      if (!amt) return pts;
      return pts.map((p, i) => [p[0] + (hash(id * 13.1 + i * 7.7 + boil * 3.3) - 0.5) * 2 * amt, p[1] + (hash(id * 5.3 + i * 3.1 + boil * 9.7) - 0.5) * 2 * amt]);
    }
    // the pixel looks move things in whole low-res pixels: a slide that lands between pixels redraws every edge half-lit,
    // and the palette snaps it thick or thin each frame (the "swimming" Todd saw). Rounding the current offset keeps edges crisp.
    const pin = () => { if (!look.bitmap) return; const m = ctx.getTransform(); ctx.setTransform(m.a, m.b, m.c, m.d, Math.round(m.e), Math.round(m.f)); };
    // shape(points, {fill, stroke, lw, closed, alpha, line: false}) in color roles or literal colors.
    function shape(pts, o = {}) {
      const id = o.id != null ? o.id : ++uid;
      const closed = o.closed !== false;
      ctx.save(); pin();
      if (o.alpha != null) ctx.globalAlpha *= o.alpha;
      const w = look.wobble;
      if (o.fill) { trace(jitter(pts, id, w * 0.6), closed); ctx.fillStyle = col(o.fill); ctx.fill(); }
      let st = o.stroke ? {color: col(o.stroke), w: o.lw || 3} : null;
      if (look.lineArt && o.line !== false && (o.fill || o.stroke)) {
        const ls = look.stroke('line', o.lw);
        st = {color: o.stroke ? col(o.stroke) : ls.color, w: o.lw || ls.w};
      }
      if (st) {
        ctx.lineJoin = 'round'; ctx.lineCap = 'round'; ctx.strokeStyle = st.color; ctx.lineWidth = st.w;
        trace(jitter(pts, id + 0.5, w), closed); ctx.stroke();
        if (w) { ctx.globalAlpha *= 0.45; ctx.lineWidth = st.w * 0.6; trace(jitter(pts, id + 0.9, w * 1.4), closed); ctx.stroke(); }
      }
      ctx.restore();
    }
    // ---- the arcade look's 1-bit pixel font (anim.py kit -> _runtime/pixfont.js) ----
    const PF = window.PIXFONT;
    const U = look.scale ? 1 / look.scale : 1;   // full-frame units per low-res pixel (3 in the arcade look)
    // the first and last rows that hold ink in a bitmap font (cached), so boxes hug the letters
    function inkRows(f) {
      if (f._ink) return f._ink;
      let lo = 1e9, hi = -1;
      Object.values(f.glyphs).forEach((g) => g.rows.forEach((r, i) => { if (r.indexOf('1') >= 0) { lo = Math.min(lo, i); hi = Math.max(hi, i); } }));
      return (f._ink = [lo === 1e9 ? 0 : lo, hi < 0 ? f.h - 1 : hi]);
    }
    function bmPick(size) {
      if (size >= 52) { const f = PF.display; return {f, m: Math.max(1, Math.round(size / (f.h * U)))}; }
      return {f: PF.body, m: Math.max(1, Math.round(size / (PF.body.h * U)))};
    }
    function bmWidth(s, size) { const {f, m} = bmPick(size); let w = 0; for (const ch of s) { const g = f.glyphs[ch] || f.glyphs['?']; w += (g.w + 1) * m * U; } return w; }
    function bmLine(s, x, y, size, color) {
      const {f, m} = bmPick(size), px = m * U;
      x = Math.round(x / U) * U; y = Math.round(y / U) * U;
      ctx.fillStyle = color;
      for (const ch of s) {
        const g = f.glyphs[ch] || f.glyphs['?'];
        g.rows.forEach((row, ry) => {
          let run = -1;
          for (let rx = 0; rx <= row.length; rx++) {
            if (row[rx] === '1') { if (run < 0) run = rx; }
            else if (run >= 0) { ctx.fillRect(x + run * px, y + ry * px, (rx - run) * px, px + 2); run = -1; }   // px + 2: rows overlap, so a zoom never opens seams
          }
        });
        x += (g.w + 1) * px;
      }
    }
    const bmHeight = (size) => { const {f, m} = bmPick(size); return f.h * m * U; };

    function fontStr(o) {
      const fam = o.font === 'body' ? look.font.body : look.font.display;
      return `${o.weight || 700} ${o.size || 48}px ${fam}`;
    }
    function measure(s, o) { if (look.bitmap) return bmWidth(look.font.caps && o.caps !== false ? s : s, o.size || 48); ctx.save(); ctx.font = fontStr(o); setTrack(o); const w = ctx.measureText(s).width; ctx.restore(); return w; }
    function setTrack(o) { const tr = o.track != null ? o.track : look.font.track; try { ctx.letterSpacing = `${(tr || 0) * (o.size || 48)}px`; } catch (e) {} }
    function wrap(s, o, maxW) {
      const words = s.split(/\s+/), lines = []; let cur = '';
      for (const wd of words) { const t = cur ? cur + ' ' + wd : wd; if (cur && measure(t, o) > maxW) { lines.push(cur); cur = wd; } else cur = t; }
      if (cur) lines.push(cur);
      return lines;
    }
    // text(s, x, y, {size, weight, font: 'display'|'body', color, align, maxW, lh, alpha, caps, track}) -> {w, h, lines}
    function text(s, x, y, o = {}) {
      s = String(s);
      const caps = o.caps != null ? o.caps : look.font.caps && o.font !== 'body';
      if (caps) s = s.toUpperCase();
      const size = o.size || 48, lh = look.bitmap ? bmHeight(size) * (o.lh ? Math.max(1.05, o.lh) : 1.15) : (o.lh || 1.15) * size;
      const lines = o.maxW ? wrap(s, o, o.maxW) : [s];
      if (look.bitmap) {
        ctx.save(); pin(); if (o.alpha != null) ctx.globalAlpha *= o.alpha;
        let wmax = 0;
        lines.forEach((ln, i) => {
          const w = bmWidth(ln, size); wmax = Math.max(wmax, w);
          const ax = o.align === 'center' ? x - w / 2 : (o.align === 'right' ? x - w : x);
          if (o.shadow !== false && o.drop) bmLine(ln, ax + U, y + i * lh + U, size, col(o.drop));
          bmLine(ln, ax, y + i * lh, size, col(o.color || 'ink'));
          if (window.__boxes) {   // the layout lint (anim.py lint): where this text really landed, in 1080 x 1920 units
            const {f, m} = bmPick(size), ink = inkRows(f), px = m * U, tr = ctx.getTransform(), sc = 1 / (look.scale || 1);
            const P = (qx, qy) => [(tr.a * qx + tr.c * qy + tr.e) * sc, (tr.b * qx + tr.d * qy + tr.f) * sc];
            const p0 = P(ax, y + i * lh + ink[0] * px), p1 = P(ax + w, y + i * lh + (ink[1] + 1) * px);
            window.__boxes.push({s: ln, x0: Math.min(p0[0], p1[0]), y0: Math.min(p0[1], p1[1]), x1: Math.max(p0[0], p1[0]), y1: Math.max(p0[1], p1[1]), a: ctx.globalAlpha, tag: o.lint === false ? 'deco' : (window.__tag || 'scene')});
          }
        });
        ctx.restore();
        return {w: wmax, h: lines.length * lh, lines};
      }
      ctx.save();
      if (o.alpha != null) ctx.globalAlpha *= o.alpha;
      ctx.font = fontStr(o); setTrack(o);
      ctx.textBaseline = 'top'; ctx.textAlign = o.align || 'left';
      ctx.fillStyle = col(o.color || 'ink');
      let wmax = 0;
      lines.forEach((ln, i) => {
        let dx = 0, dy = 0, rot = 0;
        if (look.wobble) { dx = (hash(strHash(ln) + boil) - 0.5) * 1.5; dy = (hash(strHash(ln) * 3 + boil) - 0.5) * 1.5; rot = (hash(strHash(ln) * 7) - 0.5) * 0.012; }
        ctx.save(); ctx.translate(x + dx, y + i * lh + dy); ctx.rotate(rot); ctx.fillText(ln, 0, 0); ctx.restore();
        wmax = Math.max(wmax, ctx.measureText(ln).width);
      });
      ctx.restore();
      return {w: wmax, h: lines.length * lh, lines};
    }

    const k = {
      T, look, C, ctx, env, ease, easeOut, back, clamp, rectPts, ellPts, capsule, shape, text, measure, wrap,
      W: 1080, H: 1920, X0: 72, X1: 930, TOP: 270, BAND: 1050,
      data: env.data,
      // cue timing
      S: (id) => env.cue(id).t,
      E: (id) => env.cue(id).end,
      live: (id) => { const c = env.cue(id); return T >= c.t && T < c.end; },
      since: (id) => T - env.cue(id).t,
      p: (a, b) => ease((T - a) / Math.max(0.001, b - a)),
      lin: (a, b) => clamp((T - a) / Math.max(0.001, b - a)),
      pop: (t0, d = 0.35) => back((T - t0) / d),
      talking: () => env.talking(T),
    };

    k.bg = function () {
      ctx.fillStyle = C.bg; ctx.fillRect(0, 0, 1080, 1920);
      const floor = () => { ctx.save(); ctx.fillStyle = C.bg2; ctx.globalAlpha = look.lineArt ? 0.6 : 0.9; ctx.fillRect(0, 1250, 1080, 670); ctx.restore();
        shape([[0, 1250], [1080, 1250]], {stroke: look.lineArt ? 'line' : 'line', lw: 3, closed: false, line: false}); };
      if (look.grid === 'blueprint') {
        ctx.save(); ctx.strokeStyle = 'rgba(214,232,255,0.10)'; ctx.lineWidth = 1;
        for (let x = 0; x <= 1080; x += 30) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, 1920); ctx.stroke(); }
        for (let y = 0; y <= 1920; y += 30) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(1080, y); ctx.stroke(); }
        ctx.strokeStyle = 'rgba(214,232,255,0.20)'; ctx.lineWidth = 1.5;
        for (let x = 0; x <= 1080; x += 150) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, 1920); ctx.stroke(); }
        for (let y = 0; y <= 1920; y += 150) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(1080, y); ctx.stroke(); }
        ctx.restore();
      } else if (look.grid === 'dots') {
        ctx.save(); ctx.fillStyle = C.bg2;
        for (let y = 12; y < 1920; y += 24) for (let x = (y / 24) % 2 ? 12 : 0; x < 1080; x += 24) ctx.fillRect(x, y, 6, 6);
        ctx.restore();
      } else if (look.grid === 'desk') {
        ctx.save(); ctx.fillStyle = 'rgba(255,240,225,0.045)';
        for (let y = 20; y < 1920; y += 40) for (let x = 20; x < 1080; x += 40) ctx.fillRect(x - 2, y - 2, 4, 4);
        const g = ctx.createRadialGradient(540, 620, 80, 540, 760, 1100); g.addColorStop(0, 'rgba(240,136,62,0.07)'); g.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = g; ctx.fillRect(0, 0, 1080, 1920); ctx.restore();
      } else if (look.grid === 'chalk') {
        ctx.save();
        for (let i = 0; i < 260; i++) { ctx.fillStyle = `rgba(255,255,255,${0.015 + hash(i) * 0.03})`; const x = hash(i * 3.1) * 1080, y = hash(i * 7.7) * 1920; ctx.fillRect(x, y, 2 + hash(i) * 60, 1.5); }
        ctx.restore();
      } else {
        const g = ctx.createRadialGradient(540, 700, 100, 540, 900, 1300); g.addColorStop(0, C.bg); g.addColorStop(1, C.bg2);
        ctx.fillStyle = g; ctx.fillRect(0, 0, 1080, 1920);
      }
      floor();
    };

    // A card: soft shadow in the clean look, a traced box in the line-art looks.
    k.card = function (x, y, w, h, o = {}) {
      if (!look.lineArt && (look.name === 'clean' || look.name === 'desk') && o.shadow !== false) shape(rectPts(x, y + 8, w, h, o.r != null ? o.r : 28), {fill: 'shadow', line: false, alpha: 1});
      shape(rectPts(x, y, w, h, o.r != null ? o.r : 28), {fill: o.fill || 'card', stroke: o.stroke || (look.name === 'clean' || look.name === 'desk' ? 'line' : null), lw: o.lw || 2, id: o.id});
      if (look.name === 'blueprint' && o.dims !== false) k.dim(x, y - 26, x + w, String(Math.round(w)));
    };
    // Blueprint dimension mark: a measured line with end ticks and its number.
    k.dim = function (x0, y, x1, label) {
      ctx.save(); ctx.strokeStyle = 'rgba(214,232,255,0.6)'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(x1, y); ctx.moveTo(x0, y - 8); ctx.lineTo(x0, y + 8); ctx.moveTo(x1, y - 8); ctx.lineTo(x1, y + 8); ctx.stroke();
      ctx.restore();
      if (label) text(label, (x0 + x1) / 2, y - 22, {size: 16, font: 'body', weight: 600, color: 'muted', align: 'center', caps: true, track: 0.1});
    };

    k.chip = function (s, x, y, o = {}) {
      const size = o.size || 30;
      const tw = measure(s.toUpperCase(), {size, weight: 700, track: 0.08});
      const w = tw + 36, h = size + 22;
      if (look.bitmap) k.finish(x, y, w, h, o.fill || 'tag');   // the game-UI edge: shadow, notch, light and shade
      else shape(rectPts(x, y, w, h, look.name === 'pixel' ? 0 : 10), {fill: o.fill || 'tag', line: false});
      text(s.toUpperCase(), x + 18, y + 11, {size, weight: 700, color: o.color || 'tagText', track: 0.08, caps: true});
      return {w, h};
    };
    k.title = function (s, y, o = {}) {
      return text(s, o.x || 72, y, {size: o.size || 64, weight: 700, color: o.color || 'ink', maxW: o.maxW || 858, lh: 1.08, alpha: o.alpha});
    };
    k.label = (s, x, y, o = {}) => text(s, x, y, Object.assign({size: 42, weight: 600, font: 'body', color: 'ink2'}, o));
    k.big = (s, x, y, o = {}) => text(s, x, y, Object.assign({size: 200, weight: 700, color: 'ink', lh: 1}, o));
    k.source = (s, y, o = {}) => text(s, o.x || 72, y, {size: 34, weight: 600, font: 'body', color: 'muted', alpha: o.alpha});

    // A number that counts to the brief's value and lands exactly on it.
    k.count = function (to, p, o = {}) {
      const from = o.from || 0, dec = o.dec || 0;
      const v = p >= 1 ? to : from + (to - from) * easeOut(p);
      let s = v.toFixed(dec);
      if (o.comma) s = Number(s).toLocaleString('en-US', {minimumFractionDigits: dec, maximumFractionDigits: dec});
      return (o.prefix || '') + s + (o.suffix || '');
    };

    k.spot = function (x, y, w, h, t0, o = {}) {
      const p = easeOut((T - t0) / 0.45); if (p <= 0) return;
      const pad = o.pad || 14, pts = rectPts(x - pad, y - pad, w + 2 * pad, h + 2 * pad, o.r || 18);
      const n = Math.max(2, Math.floor(pts.length * p));
      shape(pts.slice(0, n), {stroke: o.color || 'accent', lw: o.lw || 6, closed: p >= 1, line: false});
      if (o.chip && p >= 1) k.chip(o.chip, o.chipAt ? o.chipAt[0] : x - pad, o.chipAt ? o.chipAt[1] : y - pad - 58, {size: 24, fill: o.color || 'accent', color: 'pillText'});
    };
    k.arrow = function (a, b, p, o = {}) {
      p = clamp(p); if (p <= 0) return;
      const e = [a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p];
      shape([a, e], {stroke: o.color || 'accent', lw: o.lw || 6, closed: false, line: false});
      if (p > 0.9) { const ang = Math.atan2(b[1] - a[1], b[0] - a[0]), s = 22; shape([[e[0] - s * Math.cos(ang - 0.5), e[1] - s * Math.sin(ang - 0.5)], e, [e[0] - s * Math.cos(ang + 0.5), e[1] - s * Math.sin(ang + 0.5)]], {stroke: o.color || 'accent', lw: o.lw || 6, closed: false, line: false}); }
    };

    // ---- the map: the 77 community areas (the City's boundaries) ----
    k.map = function (x, y, w, o = {}) {
      const M = window.MAP; const s = w / M.w, h = M.h * s;
      const focus = o.focus, p = o.p == null ? 1 : o.p;
      const fc = M.areas.find((a) => a.n === focus);
      const dmax = 1300;
      M.areas.forEach((a) => {
        const d = fc ? Math.hypot(a.c[0] - fc.c[0], a.c[1] - fc.c[1]) : a.n * 12;
        const ap = clamp((p - (d / dmax) * 0.6) / 0.4);
        if (ap <= 0) return;
        const fill = a.n === focus && o.focusOn !== false ? 'accent' : (o.colorOf ? o.colorOf(a.n) : 'lo');
        a.polys.forEach((ring, ri) => shape(ring.map(([px, py]) => [x + px * s, y + py * s]), {fill, stroke: look.lineArt ? null : (look.name === 'pixel' ? 'bg' : 'ink2'), lw: look.name === 'pixel' ? 4 : 1.6, alpha: ap, id: a.n * 100 + ri}));
      });
      if (fc && o.pulse != null && T >= o.pulse) {
        const q = ((T - o.pulse) % 1.4) / 1.4;
        shape(ellPts(x + fc.c[0] * s, y + fc.c[1] * s, 20 + q * 70, 20 + q * 70), {stroke: 'accent', lw: 5, alpha: 1 - q, line: false});
      }
      return {w, h, at: (n) => { const a = M.areas.find((z) => z.n === n); return [x + a.c[0] * s, y + a.c[1] * s]; }};
    };

    // ---- a data card in the look of the City's table ----
    k.panel = function (x, y, w, o) {
      const rowH = o.rowH || 78, head = 120, h = head + rowH * o.rows.length + 24;
      const p = o.p == null ? 1 : o.p;
      k.card(x, y, w, h, {r: 22});
      shape(rectPts(x, y, w, head - 10, 22).slice(0, 14).concat([[x + w, y + head - 10], [x, y + head - 10]]), {fill: 'ink', line: false, alpha: look.lineArt ? 0.18 : 1});
      text(o.title, x + 32, y + 22, {size: 34, weight: 700, color: look.lineArt ? 'ink' : 'card', caps: true, track: 0.04});
      text(o.sub, x + 32, y + 66, {size: 26, weight: 600, font: 'body', color: look.lineArt ? 'muted' : 'line'});
      const cols = o.cols;
      cols.forEach((c, ci) => text(c.h, x + c.x, y + head + 6, {size: 24, weight: 700, font: 'body', color: 'muted', align: c.align || 'left', caps: true, track: 0.06}));
      o.rows.forEach((r, ri) => {
        const ry = y + head + 44 + ri * rowH, rp = clamp((p * (o.rows.length + 2) - ri) / 2);
        if (rp <= 0) return;
        if (r.hi) shape(rectPts(x + 14, ry - 8, w - 28, rowH - 6, 12), {fill: 'tealSoft', line: false, alpha: rp});
        r.cells.forEach((cv, ci) => text(cv, x + cols[ci].x, ry + 6, {size: ci ? 42 : 38, weight: ci ? 700 : 600, font: ci ? 'display' : 'body', color: r.hi && cols[ci].accent ? 'accent' : 'ink', align: cols[ci].align || 'left', alpha: rp}));
      });
      return {w, h};
    };

    // ---- a captured real page (anim.py grab) ----
    k.page = function (x, y, w, h, name, o = {}) {
      const img = env.img(name); if (!img) return;
      const sc = w / img.width, sy = o.scroll || 0;
      ctx.save(); trace(rectPts(x, y, w, h, 24), true); ctx.clip();
      ctx.fillStyle = '#fff'; ctx.fillRect(x, y, w, h);
      ctx.drawImage(img, 0, sy / sc, img.width, h / sc, x, y, w, h);
      ctx.restore();
      shape(rectPts(x, y, w, h, 24), {stroke: 'ink', lw: 4, line: false});
    };

    // ---- the cast ----
    function limb(sh, a1, a2, l1, l2, face) {
      const el = [sh[0] + face * l1 * Math.sin(a1), sh[1] + l1 * Math.cos(a1)];
      const ha = [el[0] + face * l2 * Math.sin(a1 + a2), el[1] + l2 * Math.cos(a1 + a2)];
      return {el, ha};
    }
    // ---- the host's life: blinks, breathing, fidgets, a mouth from the voice. All pure functions of T (frames render in any order).
    const FR = 30;
    const LPX = look.scale && look.scale !== 1 ? 1 / look.scale : (look.pixelHost ? 1 / look.pixelHost : 1);   // frame units per low-res pixel
    // blinks: every 2.5 to 6 s (hashed, so the same every render), 4 frames (half, shut, shut, half), 15% doubled,
    // moved into the nearest gap between words when one is close, so a blink never lands on a key word
    function blinks() {
      if (env._blinks) return env._blinks;
      const ws = env.words || [], gaps = [];
      for (let i = 0; i + 1 < ws.length; i++) if (ws[i + 1].start - ws[i].end >= 0.12) gaps.push([ws[i].end, ws[i + 1].start]);
      const out = []; let t = 0.9 + 1.2 * hash(5.1), n = 0;
      while (t < (env.duration || 600)) {
        let b = t, best = 1.0;
        const prev = out.length ? out[out.length - 1] : -9;
        if (ws.length && ws.some((w) => t >= w.start && t < w.end)) gaps.forEach(([g0, g1]) => { const c = Math.min(Math.max(t, g0 + 0.02), g1 - 0.02); if (Math.abs(c - t) < best && c - prev >= 2.5) { best = Math.abs(c - t); b = c; } });
        out.push(b);
        if (hash(n * 3.31 + 0.7) < 0.15) out.push(b + 6 / FR);   // a double blink: 2 open frames between
        n++; t = b + 2.5 + 3.5 * hash(n * 7.31 + 1.7);
      }
      return (env._blinks = out);
    }
    k.blinkAt = function (t = T) {   // 0 open, 1 half shut, 2 shut
      const bs = blinks(); let lo = 0, hi = bs.length - 1, i = -1;
      while (lo <= hi) { const m = (lo + hi) >> 1; if (bs[m] <= t) { i = m; lo = m + 1; } else hi = m - 1; }
      if (i < 0) return 0;
      const f = Math.floor((t - bs[i]) * FR + 0.005);
      return f === 0 || f === 3 ? 1 : (f === 1 || f === 2 ? 2 : 0);
    };
    // the mouth: 0 closed, 1 slightly open, 2 open, 3 wide open (anim.py mouth); null when the lesson has no mouth.js
    k.mouthAt = (t = T) => (env.mouth ? env.mouth(t) : null);

    // two-bone reach for a fidget: the hand goes to a point, the elbow bends out and down
    function reach(sh, tgt, l1, l2, face) {
      const dx = tgt[0] - sh[0], dy = tgt[1] - sh[1], d = Math.max(Math.abs(l1 - l2) + 1, Math.min(l1 + l2 - 1, Math.hypot(dx, dy)));
      const a = Math.atan2(dy, dx), c = clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1), b = Math.acos(c);
      const score = (e) => Math.sin(e) + 0.3 * face * Math.cos(e);   // the elbow that hangs lower, then the one further out
      const ea = score(a + b) >= score(a - b) ? a + b : a - b;
      const el = [sh[0] + l1 * Math.cos(ea), sh[1] + l1 * Math.sin(ea)];
      return {el, ha: [sh[0] + d * Math.cos(a), sh[1] + d * Math.sin(a)]};
    }

    // four mouth shapes drawn on the pixel grid itself (whole device pixels), so they read crisp at a third of the size:
    // 0 a closed lip line, 1 teeth and a sliver of dark, 2 open, 3 wide open with the tongue
    const MOUTHS = [
      [[0, 7, 'lip']],
      [[0, 7, 'teeth'], [1, 7, 'dark']],
      [[0, 8, 'teeth'], [1, 8, 'dark'], [2, 6, 'dark']],
      [[0, 8, 'teeth'], [1, 8, 'dark'], [2, 8, 'dark'], [3, 8, 'dark'], [4, 6, 'tongue']],
    ];
    function mouth(cx, top, level, s) {
      const m = ctx.getTransform();
      const u = Math.max(1, Math.round(Math.max(LPX, 3) * m.a / s));
      const px = m.a * cx + m.c * top + m.e, py = m.b * cx + m.d * top + m.f;
      const cl = {lip: C.skinShade || '#C98B63', teeth: C.paper || '#FFF7EA', dark: '#2B2033', tongue: '#7A3442'};
      ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
      MOUTHS[Math.max(0, Math.min(3, level))].forEach(([row, w, c]) => {
        ctx.fillStyle = cl[c]; ctx.fillRect(Math.round(px / u - w / 2) * u, (Math.round(py / u) + row) * u, w * u, u);
      });
      ctx.restore();
    }
    k.snow = function (x, y, o = {}) {
      const s = o.scale || 1, face = o.face || 1, pose = o.pose || 'stand';
      const L = LPX / s;   // one low-res pixel in the host's own units
      // breathing, held like a pixel idle: rest, a sub-pixel step (a lit shoulder edge), chest up 1 pixel, the step again
      const bp = ((T % 2.8) + 2.8) % 2.8, breath = bp < 1.0 ? 0 : (bp < 1.4 ? 1 : (bp < 2.4 ? 2 : 1));
      const bob = breath === 2 ? -L : 0;
      const talk = o.talk != null ? o.talk : k.talking();
      // a fidget after 8 to 12 s in the same pose (the player passes o.idle, seconds since the pose last changed)
      let fid = null;
      if (o.idle != null && (pose === 'stand' || pose === 'talk')) {
        const seed = o.idleSeed || 0, thr = 8 + 4 * hash(seed * 1.37 + 0.3), e = o.idle - thr;
        if (e >= 0) {
          const nth = Math.floor(e / thr), ph = Math.floor((e - nth * thr) * 15) / 15;   // on twos
          if (ph < 0.8) fid = {kind: ['scratch', 'cap', 'look'][Math.floor(hash(seed * 2.9 + nth * 5.3) * 3)], w: ph < 0.2 ? easeOut(ph / 0.2) : (ph > 0.6 ? 1 - easeOut((ph - 0.6) / 0.2) : 1), ph};
        }
      }
      ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
      const P = (px, py) => [px, py + (py < -140 ? bob : 0)];
      // legs and shoes
      shape(rectPts(-44, -158, 36, 150, 14), {fill: 'pants', id: 9001});
      shape(rectPts(8, -158, 36, 150, 14), {fill: 'pants', id: 9002});
      shape(ellPts(-30, -6, 34, 15), {fill: 'shoe', id: 9003});
      shape(ellPts(30, -6, 34, 15), {fill: 'shoe', id: 9004});
      // arms: angles from straight down, toward the face direction when positive
      const g = Math.sin(T * 5.2);
      const poses = {
        stand: [[0.12, -0.15], [0.12, -0.15]],
        talk: [[0.12, -0.2], [0.55 + 0.12 * g, 1.1 + 0.25 * g]],
        point: [[0.1, -0.15], null],
        shrug: [[1.0, -2.0], [1.0, -2.0]],
        wave: [[0.12, -0.15], [2.7, 0.5 + 0.45 * g]],
        clip: [[0.45, 1.75], [0.12, -0.2]],
        lean: [[0.45, 1.75], [0.35, 1.2]],
      };
      const pz = poses[pose] || poses.stand;
      const shL = P(-62 * face, -292), shR = P(62 * face, -292);
      let armR = pz[1];
      if (!armR) { // point at a frame spot: aim the whole arm
        const tx = ((o.at ? o.at[0] : x + 400) - x) / s, ty = ((o.at ? o.at[1] : y - 300) - y) / s;
        const a = Math.atan2(face * (tx - shR[0]), ty - shR[1]);
        armR = [a, 0.05];
      }
      const back = limb(shL, -pz[0][0], -pz[0][1], 82, 76, face);   // the far arm swings the other way
      let front = limb(shR, armR[0], armR[1], 82, 76, face);
      const hx0 = 4 * face, hy0 = -384 + bob;
      if (fid && fid.kind !== 'look') {   // the near hand goes to the beard or the cap and back, with a 1 pixel rub while it is there
        const rub = fid.w >= 1 ? (Math.floor(T * 15) % 2 ? L : -L) : 0;
        const tg = fid.kind === 'scratch' ? [hx0 + 24 * face + rub, hy0 + 80] : [hx0 + 62 * face, hy0 - 22 + rub];
        front = reach(shR, [front.ha[0] + (tg[0] - front.ha[0]) * fid.w, front.ha[1] + (tg[1] - front.ha[1]) * fid.w], 82, 76, face);
      }
      const drawArm = (sh, l, id) => { shape(capsule(sh, l.el, 19), {fill: 'jacket', id}); shape(capsule(l.el, l.ha, 16), {fill: 'jacket', id: id + 1}); shape(ellPts(l.ha[0], l.ha[1], 15, 15), {fill: 'skin', id: id + 2}); };
      drawArm(shL, back, 9010);
      // torso: the work jacket
      shape(rectPts(-66, -318 + bob, 132, 172, 30), {fill: 'jacket', id: 9020});
      if (breath === 1) shape(rectPts(-50, -318 + bob, 100, L, 0), {fill: C.jacketHi || '#3E7A62', line: false});   // the in-between breath: a lit shoulder edge, nothing moves
      shape([[0, -300 + bob], [0, -152 + bob]], {stroke: 'jacketShade', lw: 4, closed: false, line: false});
      shape(rectPts(-66, -170 + bob, 132, 22, 8), {fill: 'jacketShade', id: 9021});
      shape([[-30, -318 + bob], [0, -282 + bob], [30, -318 + bob]], {fill: 'skin', id: 9022});
      if (pose === 'clip' || pose === 'lean') { // the clipboard held in front
        const hx = back.ha[0], hy = back.ha[1];
        shape(rectPts(hx - 10, hy - 104, 84, 112, 6), {fill: 'clip', id: 9030});
        shape(rectPts(hx - 2, hy - 94, 68, 92, 3), {fill: 'paper', id: 9031});
        for (let i = 0; i < 4; i++) shape([[hx + 8, hy - 76 + i * 18], [hx + 52, hy - 76 + i * 18]], {stroke: 'muted', lw: 3, closed: false, line: false});
      }
      // head
      shape(ellPts(hx0, hy0, 60, 64), {fill: 'skin', id: 9040});
      shape(ellPts(hx0 + 52 * face, hy0 + 6, 9, 14), {fill: 'skinShade', id: 9041, line: false});
      // knit cap with a fold and a pom
      shape(ellPts(hx0, hy0 - 18, 64, 56, 24, Math.PI, TAU).concat([[hx0 + 64, hy0 - 12], [hx0 - 64, hy0 - 12]]), {fill: 'cap', id: 9042});
      shape(rectPts(hx0 - 66, hy0 - 30, 132, 26, 10), {fill: 'accent2', id: 9043});
      shape(ellPts(hx0, hy0 - 82, 16, 16), {fill: 'accent2', id: 9044});
      // face: eyes blink at natural, uneven intervals (k.blinkAt); a fidget can glance toward the board
      const bl = k.blinkAt(), ex = hx0 + 14 * face;
      const gx = fid && fid.kind === 'look' ? L * face * fid.w : 0, gy = fid && fid.kind === 'look' ? -L * fid.w : 0;
      [ex - 20, ex + 20].forEach((x0, i) => bl === 2 ? shape([[x0 - 7, hy0 + 12], [x0 + 7, hy0 + 12]], {stroke: look.lineArt ? 'ink' : 'shoe', lw: 4, closed: false, line: false})
        : shape(ellPts(x0 + gx, hy0 + 12 + gy + (bl ? 4 : 0), 6.5, bl ? 4 : 8), {fill: look.lineArt ? 'ink' : 'shoe', line: false, id: 9050 + i}));
      // the mouth level from the voice (anim.py mouth); without mouth.js, the old open-and-close while a word is said
      const ml = o.talk === false ? 0 : k.mouthAt();
      const jaw = ml != null && ml >= 2 ? L : 0;   // the open jaw drops the beard 1 low-res pixel
      // the beard: a full, trimmed beard over the jaw, with a moustache
      const bc = C.beard || '#5A3A22', bh = C.beardHi || '#7A4E2C';
      shape(ellPts(hx0 + 4 * face, hy0 + 30, 58, 46 + jaw, 24, 0, Math.PI).concat([[hx0 - 54 + 4 * face, hy0 + 18], [hx0 + 62 + 4 * face, hy0 + 18]]), {fill: bc, id: 9045});
      shape(ellPts(hx0 + 4 * face, hy0 + 44 + jaw, 50, 40, 20, 0.2, Math.PI - 0.2), {fill: bh, line: false, id: 9046, alpha: 0.6});
      shape(rectPts(ex - 30, hy0 + 26, 60, 12, 6), {fill: bc, line: false, id: 9047});
      [ex - 20, ex + 20].forEach((x0) => shape([[x0 - 10, hy0 - 4], [x0 + 10, hy0 - 6]], {stroke: bc, lw: 6, closed: false, line: false}));
      if (ml == null) {
        const mo = talk ? 3 + Math.abs(Math.sin(T * 17) * Math.sin(T * 7.3)) * 13 : 2.5;
        shape(ellPts(ex, hy0 + 40, talk ? 13 : 15, mo), {fill: talk ? 'ink' : null, stroke: talk ? null : 'ink', lw: 3.5, line: false, closed: !(!talk), id: 9060});
      } else mouth(ex, hy0 + 37, ml, s);
      drawArm(shR, front, 9070);
      ctx.restore();
      return {head: [x + hx0 * s, y + hy0 * s], hand: [x + front.ha[0] * s, y + front.ha[1] * s], top: y - 470 * s};
    };

    k.squeak = function (x, y, o = {}) {
      const s = o.scale || 1, face = o.face || 1, pose = o.pose || 'sit';
      const hop = pose === 'run' ? Math.abs(Math.sin(T * 14)) * 10 : 0;
      const jump = pose === 'startle' ? 26 : 0;
      ctx.save(); ctx.translate(x, y - hop - jump); ctx.scale(s * face, s);
      if (pose === 'peek') { ctx.beginPath(); ctx.rect(-200, -400, 400, 400); ctx.clip(); ctx.translate(0, 46); }
      const tw = Math.sin(T * 6) * 8;
      shape([[-52, -24], [-90, -10 + tw], [-128, -26 - tw], [-150, -8]], {stroke: 'ratPink', lw: 6, closed: false, line: false});
      shape(ellPts(0, -40, 58, 38), {fill: 'rat', id: 9101});
      shape(ellPts(4, -30, 34, 20), {fill: 'ratBelly', id: 9102});
      shape(ellPts(44, -84, 16, 16), {fill: 'rat', id: 9103});
      shape(ellPts(44, -84, 9, 9), {fill: 'ratPink', id: 9104, line: false});
      shape(ellPts(52, -60, 30, 26), {fill: 'rat', id: 9105});
      shape(ellPts(80, -54, 20, 13), {fill: 'rat', id: 9106});
      shape(ellPts(98, -56, 6, 6), {fill: 'ratPink', id: 9107, line: false});
      const blink = (T % 2.9) < 0.1;
      if (blink) shape([[56, -66], [66, -66]], {stroke: 'ink', lw: 3, closed: false, line: false});
      else shape(ellPts(61, -66, pose === 'startle' ? 7 : 5, pose === 'startle' ? 7 : 5), {fill: look.lineArt ? 'ink' : 'shoe', line: false, id: 9108});
      shape([[96, -50], [122, -44]], {stroke: 'muted', lw: 2, closed: false, line: false});
      shape([[96, -54], [124, -58]], {stroke: 'muted', lw: 2, closed: false, line: false});
      ctx.restore();
    };

    // bars: rows [{label, value, shown, focus}] drawn as a shared track so a small value still reads as a bar
    k.bars = function (x, y, w, rows, p, o = {}) {
      const vmax = o.vmax || Math.max(...rows.map((r) => Math.abs(r.value))) || 1;
      const bh = o.bh || 84, gap = o.gap || 150, valW = o.valW || 230, trackW = w - valW - 20;
      rows.forEach((r, i) => {
        const ry = y + i * gap, rp = clamp(p * 1.4 - i * 0.25);
        text(r.label, x, ry, {size: 34, weight: 700, color: 'muted', caps: true, track: 0.06});
        shape(rectPts(x, ry + 48, trackW, bh, look.name === 'pixel' ? 0 : 12), {fill: 'line', line: false, alpha: look.lineArt ? 0.35 : 0.55});
        const bw = Math.max(26, trackW * Math.abs(r.value) / vmax) * easeOut(rp);
        if (bw > 1) shape(rectPts(x, ry + 48, bw, bh, look.name === 'pixel' ? 0 : 12), {fill: r.focus ? 'accent' : 'ink2', id: 9200 + i});
        if (rp > 0.6) text(r.shown, x + trackW + 20, ry + 48 + bh / 2 - 40, {size: 80, weight: 700, color: r.focus ? 'accent' : 'ink', alpha: clamp((rp - 0.6) / 0.3)});
      });
    };

    k.compare = function (x, y, w, h, a, b, p) {
      const cw = (w - 28) / 2;
      [a, b].forEach((c, i) => {
        const cx = x + i * (cw + 28), cp = clamp(p * 2 - i * 0.6);
        if (cp <= 0) return;
        ctx.save(); ctx.globalAlpha *= clamp(cp * 2); ctx.translate(0, (1 - easeOut(cp)) * 40);
        k.card(cx, y, cw, h, {dims: false});
        text(c.label, cx + 30, y + 30, {size: 30, weight: 700, color: 'muted', maxW: cw - 60, caps: true, track: 0.06});
        const n = k.count(c.value, clamp(cp * 1.3 - 0.2), {dec: c.dec || 0});
        text(n, cx + 30, y + h - 280, {size: 220, weight: 700, color: c.focus ? 'accent' : 'ink', lh: 1});
        text(c.unit, cx + 32, y + h - 70, {size: 38, weight: 600, font: 'body', color: 'ink2'});
        ctx.restore();
      });
    };

    // ---- desk screens for lessons: an email being written, a text thread, an inbox, a checklist, a follow-up timeline ----
    // Every name on them is a role ("Property manager", "you@yourcompany.com"), never an invented person.
    k.window = function (x, y, w, h, title, o = {}) {
      k.card(x, y, w, h, {r: 20, dims: false});
      shape(rectPts(x, y, w, 64, 20).slice(0, 14).concat([[x + w, y + 64], [x, y + 64]]), {fill: 'bg2', line: false, alpha: look.lineArt ? 0.4 : 1});
      ['accent', 'accent2', 'teal'].forEach((c, i) => shape(ellPts(x + 34 + i * 30, y + 32, 9, 9), {fill: c, line: false}));
      text(title, x + w / 2, y + 16, {size: 28, weight: 600, font: 'body', color: 'muted', align: 'center'});
      return {x: x + 32, y: y + 92, w: w - 64};
    };
    // typed text: shows the first p share of the characters, with a cursor while typing
    const typed = (s, p) => { const n = Math.floor(s.length * clamp(p)); return s.slice(0, n) + (p > 0 && p < 1 && (T * 2) % 1 < 0.6 ? '|' : ''); };
    k.email = function (x, y, w, h, m, o = {}) {
      const a = k.window(x, y, w, h, o.title || 'New message');
      const fields = [['To', m.to], ['Subject', m.subject]];
      let yy = a.y;
      fields.forEach(([lab, val], i) => {
        text(lab, a.x, yy, {size: 30, weight: 600, font: 'body', color: 'muted'});
        text(i === 1 && o.typeSubject != null ? typed(val, o.typeSubject) : val, a.x + 150, yy, {size: 32, weight: 700, font: 'body', color: 'ink', maxW: a.w - 150});
        yy += 56; shape([[a.x, yy - 10], [a.x + a.w, yy - 10]], {stroke: 'line', lw: 2, closed: false, line: false});
      });
      yy += 18;
      const lines = m.body;
      let left = o.p == null ? 1 : o.p * lines.join('').length;
      const lineH = o.lineH || 50;
      lines.forEach((ln, i) => {
        const take = Math.max(0, Math.min(ln.length, left)); left -= ln.length;
        if (take <= 0 && ln) return;
        const hi = o.hi && o.hi.includes(i);
        const r = text(take >= ln.length ? ln : typed(ln, take / ln.length), a.x, yy, {size: 34, weight: hi ? 700 : 400, font: 'body', color: hi ? 'ink' : 'ink2', maxW: a.w, lh: 1.3});
        if (hi && take >= ln.length && o.hiAt != null) k.spot(a.x, yy, Math.min(a.w, r.w), r.h, o.hiAt[o.hi.indexOf(i)], {pad: 8, lw: 5});
        yy += Math.max(lineH, r.h + 10);
      });
      return {bottom: yy};
    };
    k.phone = function (x, y, w, h, msgs, o = {}) {
      const fs = o.size || 32, lh = Math.round(fs * 1.32);
      const bez = C.bezel || (look.lineArt ? 'bg2' : (look.name === 'desk' ? '#0F0C0E' : 'ink'));
      if (look.bitmap) {   // a crafted handset: a drop shadow, side buttons, a lit rim on the bezel, a shaded inner lip, a glint
        const u = 3;
        shape(rectPts(x + u, y + u, w, h, 0), {fill: '#2B2033', line: false});
        [[x - u, y + 120, u, 66], [x - u, y + 198, u, 40], [x + w, y + 150, u, 80]].forEach(([bx, by, bw, bh]) => shape([[bx, by], [bx + bw, by], [bx + bw, by + bh], [bx, by + bh]], {fill: '#3D2E45', line: false}));
        shape(rectPts(x, y, w, h, 0), {fill: bez, line: false, id: 9300});
        const q = (qx, qy, qw, qh, c) => shape([[qx, qy], [qx + qw, qy], [qx + qw, qy + qh], [qx, qy + qh]], {fill: c, line: false});
        q(x + 6, y, w - 12, u, '#3D2E45'); q(x, y + 6, u, h - 12, '#3D2E45'); q(x + u, y + u, u, u, '#3D2E45');
        shape(rectPts(x + 14, y + 14, w - 28, h - 28, 0), {fill: C.screen ? 'screen' : 'card', id: 9301});
        q(x + 20, y + 14, w - 40, u, '#120D14'); q(x + 14, y + 20, u, h - 40, '#120D14');
        q(x + w - 14 - 3 * u, y + 14 + 6 * u, u, u, '#3D2E45'); q(x + w - 14 - 4 * u, y + 14 + 7 * u, u, u, '#3D2E45'); q(x + w - 14 - 2 * u, y + 14 + 5 * u, u, u, '#3D2E45');
      } else {
      shape(rectPts(x, y, w, h, 60), {fill: bez, line: true, id: 9300});
      shape(rectPts(x + 14, y + 14, w - 28, h - 28, 48), {fill: C.screen ? 'screen' : 'card', id: 9301});
      }
      shape(rectPts(x + w / 2 - 64, y + 26, 128, 30, 15), {fill: bez, line: false});
      text(o.clock || '9:41', x + 56, y + 30, {size: 22, weight: 700, font: 'body', color: 'ink'});
      // the contact header
      const hy = y + 74;
      shape(ellPts(x + w / 2, hy + 26, 26, 26), {fill: 'line', line: false});
      text((o.who || 'Customer').slice(0, 1), x + w / 2, hy + 10, {size: 28, weight: 700, font: 'body', color: 'ink', align: 'center'});
      text(o.who || 'Customer', x + w / 2, hy + 60, {size: 24, weight: 600, font: 'body', color: 'muted', align: 'center'});
      shape([[x + 30, hy + 98], [x + w - 30, hy + 98]], {stroke: 'line', lw: 2, closed: false, line: false});
      let yy = hy + 124;
      const maxW = w - 120;
      msgs.forEach((m, i) => {
        const t0 = m.at != null ? m.at : -1; if (T < t0) return;
        if (m.ghost) { const gl = wrap(m.text, {size: fs, weight: 500, font: 'body'}, maxW - 44); yy += gl.length * lh + 26 + (m.stamp ? 46 : 22); return; }   // keeps its space, drawn under a note
        const pp = easeOut((T - t0) / 0.3);
        const lines = wrap(m.text, {size: fs, weight: 500, font: 'body'}, maxW - 44);
        const bw = Math.min(maxW, Math.max(...lines.map((ln) => measure(ln, {size: fs, weight: 500, font: 'body'}))) + 44);
        // a message being typed keeps its final width and grows down one line at a time
        let shown = lines.length;
        if (m.reveal != null) { let acc = 0; shown = 1; lines.forEach((ln, li) => { if (m.reveal > acc) shown = li + 1; acc += ln.length + 1; }); }
        const bh = shown * lh + 26;
        const bx = m.me ? x + w - 32 - bw : x + 32;
        ctx.save(); ctx.globalAlpha *= pp; ctx.translate(0, (1 - pp) * 24);
        const fill = m.me ? (C.sent ? 'sent' : 'teal') : (C.recv ? 'recv' : 'bg2');
        shape(rectPts(bx, yy, bw, bh, Math.min(30, bh / 2)), {fill, line: false, id: 9310 + i});
        const tx = m.me ? bx + bw - 8 : bx + 8;   // the bubble's tail
        shape([[tx, yy + bh - 22], [m.me ? tx + 18 : tx - 18, yy + bh + 2], [m.me ? tx - 20 : tx + 20, yy + bh - 6]], {fill, line: false});
        // m.reveal: how many characters are typed so far; the layout is the full message's, so the bubble never re-wraps
        let left = m.reveal != null ? m.reveal : 1e9, lastW = 0, lastLi = 0;
        lines.forEach((ln, li) => { if (left <= 0) return; const part = ln.slice(0, left); left -= ln.length + 1;
          text(part, bx + 22, yy + 13 + li * lh, {size: fs, weight: 500, font: 'body', color: m.me ? (C.sentText ? 'sentText' : 'pillText') : 'ink'});
          lastW = measure(part, {size: fs, weight: 500, font: 'body'}); lastLi = li; });
        if (m.typing && T < m.typing) {   // a typing cursor while the line is still going in
          const lw = lastW;
          if ((T * 2.2) % 1 < 0.6) shape(rectPts(bx + 24 + lw, yy + 15 + lastLi * lh, 4, fs, 1), {fill: m.me ? (C.sentText ? 'sentText' : 'pillText') : 'ink', line: false});
        }
        if (m.stamp) text(m.stamp, m.me ? bx + bw : bx, yy + bh + 8, {size: 22, weight: 600, font: 'body', color: 'muted', align: m.me ? 'right' : 'left'});
        if (m.box) m.box({x: bx, y: yy, w: bw, h: bh, lines, lh});
        ctx.restore();
        yy += bh + (m.stamp ? 46 : 22);
      });
      return {bottom: yy};
    };
    k.checklist = function (x, y, w, items, o = {}) {
      items.forEach((it, i) => {
        const t0 = it.at != null ? it.at : 0; if (T < t0 - 0.05) return;
        const pp = easeOut((T - t0) / 0.3), yy = y + i * (o.gap || 110);
        ctx.save(); ctx.globalAlpha *= pp; ctx.translate((1 - pp) * 40, 0);
        shape(rectPts(x, yy, 64, 64, look.name === 'pixel' ? 0 : 14), {fill: 'card', stroke: 'ink2', lw: 4});
        if (it.done != null && T >= it.done) { const q = easeOut((T - it.done) / 0.25); shape([[x + 14, yy + 34], [x + 28, yy + 48], [x + 28 + 24 * q, yy + 48 - 30 * q]], {stroke: 'accent', lw: 9, closed: false, line: false}); }
        text(it.text, x + 92, yy + 6, {size: o.size || 46, weight: 700, color: 'ink', maxW: w - 92, lh: 1.1});
        ctx.restore();
      });
    };
    // a follow-up timeline: steps [{day: 'Day 1', label, at}] along a line that draws on
    k.timeline = function (x, y, w, steps, p, o = {}) {
      shape([[x, y], [x + w * easeOut(p), y]], {stroke: 'ink2', lw: 6, closed: false, line: false});
      steps.forEach((s, i) => {
        const sx = x + (w * i) / Math.max(1, steps.length - 1), t0 = s.at != null ? s.at : 0;
        if (T < t0) return;
        const q = back((T - t0) / 0.35);
        shape(ellPts(sx, y, 22 * q, 22 * q), {fill: s.hi ? 'accent' : 'ink', id: 9400 + i});
        text(s.day, sx, y - 76, {size: 34, weight: 700, color: s.hi ? 'accent' : 'ink', align: 'center', alpha: clamp(q)});
        text(s.label, sx, y + 40, {size: 30, weight: 600, font: 'body', color: 'ink2', align: 'center', maxW: o.labelW || 200, alpha: clamp(q)});
      });
    };
    // the big lesson card: a rule in a few words, stamped in
    k.rule = function (s, y, t0, o = {}) {
      if (T < t0) return;
      const q = back((T - t0) / 0.4), sc = 0.8 + 0.2 * clamp(q);
      ctx.save(); ctx.translate(540, y); ctx.scale(sc, sc); ctx.rotate(-0.02);
      const r = wrap(s, {size: o.size || 76, weight: 700}, 780);
      const h = r.length * (o.size || 76) * 1.08 + 70;
      shape(rectPts(-430, -h / 2, 860, h, look.name === 'pixel' ? 0 : 26), {fill: o.fill || 'accent', id: 9500});
      text(s, 0, -h / 2 + 35, {size: o.size || 76, weight: 700, color: o.color || 'pillText', align: 'center', maxW: 780, lh: 1.08});
      ctx.restore();
    };

    // ---- rooms: pixel backdrops for the arcade look (blackboard, workshop, garage, framing) ----
    // Drawn on the low-res grid itself: G = 3 frame units is one low-res pixel, so a room is 360 x 640 pixels and every
    // edge is a whole pixel. Light comes from the top left: each object has a shadow, base and highlight tone and a 1 pixel
    // dark outline where it helps the shape read. The content areas that scenes draw into by coordinate stay flat and calm
    // (blackboard slate x 60 to 1020, y 246 to 998; workshop pegboard x 48 to 1032, y 240 to 840; garage door x 90 to 990,
    // y 230 to 1020); decor lives in the margins and on the floor. The ambient loops are frame-stepped (each changes every 2
    // to 4 frames, by whole pixels, never by a fraction) and are pure functions of T, so any frame renders on its own.
    const R = (x, y, w, h, c) => { ctx.fillStyle = col(c); if (look.bitmap) { x = Math.round(x / U) * U; y = Math.round(y / U) * U; } ctx.fillRect(x, y, w, h); };   // rooms sit on the pixel grid (clouds step, never smear)
    const G = 3;
    const P = (x, y, w, h, c) => { if (w > 0 && h > 0) { ctx.fillStyle = col(c); ctx.fillRect(x * G, y * G, w * G, h * G); } };
    const DOT = (x, y, c) => P(x, y, 1, 1, c);
    const dith = (x, y, w, h, c, ph = 0) => { ctx.fillStyle = col(c); for (let j = 0; j < h; j++) for (let i = (j + ph) & 1; i < w; i += 2) ctx.fillRect((x + i) * G, (y + j) * G, G, G); };
    const disc = (cx, cy, r, c) => { for (let dy = -r; dy <= r; dy++) { const hw = Math.floor(Math.sqrt(r * r - dy * dy) + 0.4); P(cx - hw, cy + dy, 2 * hw + 1, 1, c); } };
    const line = (x0, y0, x1, y1, c) => {
      const dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1; let e = dx + dy;
      for (let n = 0; n < 400; n++) { DOT(x0, y0, c); if (x0 === x1 && y0 === y1) break; const e2 = 2 * e; if (e2 >= dy) { e += dy; x0 += sx; } if (e2 <= dx) { e += dx; y0 += sy; } }
    };
    // a box lit from the top left: base, a highlight on the top and left edges, a shadow on the bottom and right, an outline
    const bevel = (x, y, w, h, base, hi, lo, out) => { if (out) P(x - 1, y - 1, w + 2, h + 2, out); P(x, y, w, h, base); P(x, y, w, 1, hi); P(x, y, 1, h, hi); P(x, y + h - 1, w, 1, lo); P(x + w - 1, y + 1, 1, h - 1, lo); };
    // wood grain: short darker streaks along a board (dir 'h' or 'v'), fixed by a seed so the grain never crawls
    const grain = (x, y, w, h, c, seed, dir = 'h', d = 0.72) => {
      if (dir === 'h') { for (let j = 0; j < h; j++) for (let i = 0; i < w; i += 5) { const r = hash(seed + j * 7.13 + i * 0.731); if (r > d) P(x + i + Math.floor(r * 4), y + j, 2 + Math.floor(r * 9) % 4, 1, c); } }
      else { for (let i = 0; i < w; i++) for (let j = 0; j < h; j += 5) { const r = hash(seed + i * 7.13 + j * 0.731); if (r > d) P(x + i, y + j + Math.floor(r * 4), 1, 2 + Math.floor(r * 9) % 4, c); } }
    };
    const F = Math.floor(T * 30 + 0.005);   // the frame number; loops step on whole frames
    // pixel clouds: bumps on a flat base, an underside in shadow; built once, then only stepped across
    function cloudSprite(w, seed) {
      const key = w + ':' + seed; if (CLOUDS[key]) return CLOUDS[key];
      const n = Math.max(2, Math.round(w / 9)), bumps = [];
      for (let i = 0; i < n; i++) bumps.push([Math.round((i + 0.5) * w / n), 3 + Math.round(hash(seed + i * 1.71) * 3) + (i > 0 && i < n - 1 ? 2 : 0)]);
      const h = Math.max(...bumps.map((b) => b[1])) * 2 - 1, rows = [];
      for (let y = 0; y < h; y++) {
        const sp = [];
        bumps.forEach(([cx, r]) => { const dy = y + 0.5 - (h - r); if (Math.abs(dy) <= r) { const hw = Math.sqrt(r * r - dy * dy); sp.push([Math.round(cx - hw), Math.round(cx + hw)]); } });
        if (y >= h - 3) sp.push([2, w - 3]);
        sp.sort((a, b) => a[0] - b[0]); const m = [];
        sp.forEach((s) => { if (m.length && s[0] <= m[m.length - 1][1] + 1) m[m.length - 1][1] = Math.max(m[m.length - 1][1], s[1]); else m.push(s.slice()); });
        rows.push(m);
      }
      return (CLOUDS[key] = {w, h, rows});
    }
    // a cloud at whole pixel (x, y), clipped to a window [x0, x1) x [y0, y1)
    function cloudAt(cl, x, y, clip) {
      cl.rows.forEach((spans, j) => {
        const yy = y + j; if (yy < clip[1] || yy >= clip[3]) return;
        const c = j >= cl.h - 2 ? '#C9CCD3' : (j >= cl.h - 3 ? '#E6D3BC' : '#FFF7EA');
        spans.forEach(([a, b]) => { const xa = Math.max(x + a, clip[0]), xb = Math.min(x + b, clip[2] - 1); if (xb >= xa) P(xa, yy, xb - xa + 1, 1, c); });
      });
    }
    // a sky (deep at the top, pale at the horizon, dithered between) with clouds drifting right, one pixel every few frames
    function sky(x, y, w, h, clouds, t) {
      const b1 = Math.round(h * 0.38), b2 = Math.round(h * 0.72);
      P(x, y, w, b1, '#5B8FB9'); P(x, y + b1, w, b2 - b1, '#87CEEB'); P(x, y + b2, w, h - b2, '#BDE6F5');
      dith(x, y + b1, w, 2, '#5B8FB9', 1); dith(x, y + b2, w, 2, '#87CEEB', 1);
      const clip = [x, y, x + w, y + h];
      clouds.forEach((c) => {
        const cl = cloudSprite(c.w, c.seed), span = w + cl.w + 8;
        const off = ((Math.floor(c.x0 + (t ? F / c.every : 0)) % span) + span) % span;
        cloudAt(cl, x - cl.w + off, y + c.y, clip);
      });
    }
    // a bird: 7 x 3, three wing frames, flapping on fours
    const BIRD = [[[0, 0], [6, 0], [1, 1], [5, 1], [2, 2], [3, 2], [4, 2]], [[0, 1], [1, 1], [2, 1], [3, 1], [4, 1], [5, 1], [6, 1], [3, 2]], [[2, 1], [3, 1], [4, 1], [1, 2], [5, 2], [0, 3], [6, 3]]];
    const bird = (x, y, f, c = '#2B2033') => BIRD[f % 3].forEach(([a, b]) => DOT(x + a, y + b, c));
    // a window in the wall with sky behind it: frame, sash bars, a sill, and the glass glint
    function windowAt(x, y, w, h, t, o) {
      const fr = o.frame || '#E6D3BC', hi = o.hi || '#FFF7EA', lo = o.lo || '#B39A88';
      P(x - 1, y - 1, w + 2, h + 2, '#120D14');
      P(x, y, w, h, fr); P(x, y, w, 1, hi); P(x, y, 1, h, hi); P(x, y + h - 1, w, 1, lo); P(x + w - 1, y, 1, h, lo);
      const gx = x + 3, gy = y + 3, gw = w - 6, gh = h - 6;
      sky(gx, gy, gw, gh, o.clouds, t);
      if (o.trees) {   // a tree line on the horizon
        for (let i = 0; i < gw; i++) { const th = 3 + Math.round(2.5 + 2.5 * Math.sin(i * 0.55 + o.seed) + hash(i * 1.3 + o.seed) * 1.5); P(gx + i, gy + gh - th, 1, th, i % 7 < 3 ? '#2F5A4A' : '#3E7A62'); DOT(gx + i, gy + gh - th, '#3E7A62'); }
      }
      if (o.birds && t) {   // a pair crossing now and then
        const per = 260, ph = (F + o.seed * 97) % per, bx = gx - 8 + Math.floor(ph / 2);
        if (bx < gx + gw) [[0, 0], [9, 3]].forEach(([dx, dy], i) => { const xx = bx - dx; if (xx >= gx && xx + 7 <= gx + gw) bird(xx, gy + 4 + dy + ((Math.floor(ph / 8) + i) % 2), Math.floor(ph / 4) + i); });
      }
      P(gx, gy, gw, 1, '#253048'); P(gx, gy, 1, gh, '#253048');   // the frame's shadow on the glass
      const mx = x + Math.floor(w / 2) - 1, my = y + Math.floor(h / 2) - 1;
      P(mx, gy, 2, gh, fr); P(mx + 2, gy, 1, gh, lo);
      if (o.bars !== 'v') { P(gx, my, gw, 2, fr); P(gx, my + 2, gw, 1, lo); DOT(mx, my, hi); }
      if (o.glint !== false) { line(gx + 3, gy + 7, gx + 7, gy + 3, '#FFF7EA'); line(gx + 3, gy + 10, gx + 10, gy + 3, '#BDE6F5'); }   // glint
      // the sill
      P(x - 3, y + h, w + 6, 3, '#120D14'); P(x - 2, y + h, w + 4, 1, o.sill || '#F7C873'); P(x - 2, y + h + 1, w + 4, 1, o.sill2 || '#D9A066'); P(x - 1, y + h + 3, w + 4, 1, '#1B1420');
    }

    k.room = function (name, o = {}) {
      const t = o.ambient === false ? 0 : 1, props = o.props !== false;
      if (name === 'blackboard') roomBoard(t, props);
      else if (name === 'workshop') roomShop(t, props);
      else if (name === 'garage') roomGarage(t, props);
      else if (name === 'framing') roomFraming(t, props);
      else R(0, 0, 1080, 1920, '#1B1420');
    };
    // a wood plank floor in perspective: boards get taller toward the viewer, joints staggered
    function planks(y0, base, hi, lo, seed) {
      let y = y0, h = 5, i = 0;
      while (y < 640) {
        P(0, y, 360, h, base); P(0, y, 360, 1, hi); P(0, y + h - 1, 360, 1, lo);
        const step = 64 + h * 5, off = Math.floor(hash(i * 3.3 + seed) * step);
        for (let x = off % step; x < 360; x += step) { P(x, y + 1, 1, h - 2, lo); P(x + 1, y + 1, 1, h - 2, hi); }
        if (h > 7) grain(0, y + 2, 360, h - 4, lo, seed + i * 11, 'h', 0.9);
        y += h; h = Math.round(h * 1.2) + 1; i++;
      }
    }

    // ---- the classroom: a slate board in a beveled oak frame, a chalk tray, a window, a clock, a teacher's desk ----
    function roomBoard(t, props) {
      P(0, 0, 360, 417, '#2B2033');
      for (let y = 12; y < 350; y += 8) for (let x = ((y >> 3) & 1) * 4 + 2; x < 360; x += 8) if (y < 72 || y > 343 || x < 11 || x > 348) DOT(x, y, '#3D2E45');   // a quiet wallpaper dot
      // the cornice
      P(0, 0, 360, 3, '#1B1420'); P(0, 3, 360, 1, '#D9A066'); P(0, 4, 360, 2, '#B07A47'); P(0, 6, 360, 1, '#6B4226'); P(0, 7, 360, 1, '#120D14');
      // the window: sky, clouds, birds now and then, a plant on the sill
      windowAt(20, 12, 98, 34, t, {seed: 3, trees: true, birds: true, clouds: [{w: 34, seed: 1, y: 2, x0: 10, every: 3}, {w: 22, seed: 5, y: 9, x0: 80, every: 2}, {w: 28, seed: 9, y: 4, x0: 120, every: 3}]});
      const sw = t ? [0, 1, 0, -1][Math.floor(F / 14) % 4] : 0;   // the plant leans in the draft from the window
      P(103, 41, 11, 2, '#120D14'); P(104, 43, 9, 4, '#120D14'); P(104, 41, 9, 1, '#F2A541'); P(104, 42, 9, 1, '#E2633B'); P(105, 43, 7, 3, '#E2633B'); P(110, 43, 2, 3, '#7A3442');
      [[106, 36, 2], [108, 33, 3], [111, 35, 2], [104, 38, 2], [112, 38, 2]].forEach(([lx, ly, lw], i) => { const s = i % 2 ? sw : 0; P(lx + s, ly, lw, 2, '#3E7A62'); DOT(lx + s, ly, '#6FB7A8'); DOT(lx + s + lw - 1, ly + 1, '#2F5A4A'); });
      P(108, 38, 1, 3, '#2F5A4A');
      // the wall clock: a raised steel rim, a cream face in the rim's shadow, a second hand that ticks
      const cx = 318, cy = 29;
      disc(cx + 1, cy + 1, 15, '#1B1420'); disc(cx, cy, 15, '#120D14'); disc(cx, cy, 14, '#C9CCD3'); disc(cx + 1, cy + 1, 13, '#6B7080'); disc(cx, cy, 13, '#9AA0AD');
      disc(cx, cy, 11, '#120D14'); disc(cx, cy, 10, '#E6D3BC'); disc(cx + 1, cy + 1, 9, '#FFF7EA');
      for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6, r = i % 3 ? 8 : 7; const x = cx + Math.round(Math.sin(a) * 8.6), y = cy - Math.round(Math.cos(a) * 8.6); DOT(x, y, i % 3 ? '#9AA0AD' : '#120D14'); if (!(i % 3)) DOT(cx + Math.round(Math.sin(a) * r), cy - Math.round(Math.cos(a) * r), '#120D14'); }
      line(cx, cy, cx - 4, cy - 3, '#120D14'); line(cx, cy, cx + 5, cy - 5, '#120D14');   // ten past ten
      const sa = ((t ? Math.floor(T * 2) : 0) + 40) % 120 * Math.PI / 60;   // a sweep-second clock: a step every half second keeps the room alive
      line(cx, cy, cx + Math.round(Math.sin(sa) * 8), cy - Math.round(Math.cos(sa) * 8), '#E2633B'); DOT(cx, cy, '#7A3442');
      // the board: a drop shadow, an outline, then the mitred frame ring by ring (top and left lit, bottom and right in shade)
      const X0 = 12, Y0 = 74, X1 = 348, Y1 = 341;
      P(X0 + 2, Y0 + 2, X1 - X0, Y1 - Y0, '#1B1420'); P(X0, Y0, X1 - X0, Y1 - Y0, '#120D14');
      const lit = [null, '#F7C873', '#D9A066', '#D9A066', '#B07A47', '#D9A066', '#B07A47', '#6B4226'];
      const shd = [null, '#B07A47', '#8C5A33', '#8C5A33', '#6B4226', '#8C5A33', '#8C5A33', '#B07A47'];
      for (let j = 1; j < 8; j++) {
        P(X0 + j, Y0 + j, 1, Y1 - Y0 - 2 * j, lit[j]); P(X1 - 1 - j, Y0 + j, 1, Y1 - Y0 - 2 * j, shd[j]);
        P(X0 + j, Y0 + j, X1 - X0 - 2 * j, 1, lit[j]); P(X0 + j, Y1 - 1 - j, X1 - X0 - 2 * j, 1, shd[j]);
      }
      grain(X0 + 9, Y0 + 2, X1 - X0 - 18, 2, '#B07A47', 11, 'h'); grain(X0 + 9, Y1 - 4, X1 - X0 - 18, 2, '#6B4226', 13, 'h');
      grain(X0 + 2, Y0 + 9, 2, Y1 - Y0 - 18, '#B07A47', 17, 'v'); grain(X1 - 4, Y0 + 9, 2, Y1 - Y0 - 18, '#6B4226', 19, 'v');
      [[X0 + 3, Y0 + 3], [X1 - 5, Y0 + 3], [X0 + 3, Y1 - 5], [X1 - 5, Y1 - 5]].forEach(([x, y]) => { DOT(x, y, '#6B4226'); DOT(x + 1, y + 1, '#F7C873'); });   // corner pegs
      // the slate: flat and calm where the writing goes; the frame's shadow on its top and left edges
      P(20, 82, 320, 251, '#24453A'); P(20, 82, 320, 2, '#1A332B'); P(20, 84, 2, 249, '#1A332B'); P(339, 84, 1, 249, '#2F5A4A'); P(22, 332, 317, 1, '#2F5A4A');
      // old chalk only along the frame: an eraser's arcs in the right strip and the bottom band, never in the writing
      [[327, 102, 9, 3, 0], [323, 168, 13, 2, 1], [329, 232, 7, 4, 0], [325, 292, 11, 3, 1], [34, 328, 24, 2, 0], [236, 327, 30, 3, 1], [292, 328, 22, 2, 0]].forEach(([x, y, w, h, ph]) => dith(x, y, w, h, '#2F5A4A', ph));
      // the chalk tray: a lit top, a front face in shade, its shadow on the wall
      P(14, 340, 332, 8, '#120D14'); P(15, 341, 330, 1, '#F7C873'); P(15, 342, 330, 1, '#D9A066'); P(15, 343, 330, 3, '#8C5A33'); P(15, 346, 330, 1, '#6B4226'); P(16, 348, 330, 2, '#1B1420');
      dith(296, 341, 18, 1, '#E6D3BC', 1);   // chalk dust on the ledge
      // chalk sticks and the eraser
      P(23, 337, 13, 4, '#120D14'); P(24, 338, 11, 1, '#FFF7EA'); P(24, 339, 11, 1, '#C9CCD3'); DOT(24, 338, '#E6D3BC');
      P(39, 338, 8, 3, '#120D14'); P(40, 339, 6, 1, '#F7C873'); P(40, 339, 1, 1, '#F2A541');
      P(316, 334, 20, 7, '#120D14'); P(317, 335, 18, 3, '#B07A47'); P(317, 335, 18, 1, '#D9A066'); P(334, 336, 1, 2, '#8C5A33'); P(317, 338, 18, 2, '#4A4E5A'); for (let i = 0; i < 18; i += 3) DOT(318 + i, 338, '#6B7080');
      // the wainscot under the board
      P(0, 352, 360, 1, '#120D14'); P(0, 353, 360, 1, '#D9A066'); P(0, 354, 360, 2, '#B07A47'); P(0, 356, 360, 1, '#6B4226'); P(0, 357, 360, 52, '#6B4226');
      for (let x = 4; x < 360; x += 46) { bevel(x, 361, 40, 43, '#8C5A33', '#B07A47', '#4A2E1B'); grain(x + 2, 363, 36, 39, '#6B4226', x, 'v', 0.9); }
      P(0, 408, 360, 1, '#8C5A33'); P(0, 409, 360, 8, '#4A2E1B'); P(0, 409, 360, 1, '#6B4226');
      // the floor
      P(0, 417, 360, 1, '#120D14'); planks(418, '#6B4226', '#8C5A33', '#4A2E1B', 5);
      if (props) boardProps(t);
      // ambient: a chalk puff from the eraser every 5 s (four frames on threes)
      if (t) {
        const ph = F % 150;
        if (ph < 12) { const s = Math.floor(ph / 3); const pts = [[[0, 0]], [[0, -1], [-1, 0], [1, -1]], [[-1, -2], [1, -2], [-2, -1], [2, 0], [0, -3]], [[-2, -3], [2, -3], [-3, -1], [3, -2], [0, -4]]][s];
          pts.forEach(([a, b]) => DOT(326 + a, 333 + b, s < 2 ? '#FFF7EA' : '#C9CCD3')); }
      }
    }
    function boardProps(t) {
      // a rug: border, field, a medallion, fringe
      P(121, 491, 217, 80, '#1B1420'); P(119, 489, 217, 80, '#4A2E1B'); P(120, 490, 215, 78, '#7A3442'); bevel(125, 494, 205, 70, '#253048', '#F2A541', '#F2A541');
      for (let dy = -18; dy <= 18; dy++) { const hw = (18 - Math.abs(dy)) * 2; P(227 - hw, 529 + dy, 2 * hw + 1, 1, '#7A3442'); if (hw > 8) P(227 - hw + 6, 529 + dy, 2 * hw - 11, 1, Math.abs(dy) < 6 ? '#E2633B' : '#7A3442'); }
      DOT(227, 529, '#F7C873');
      for (let y = 491; y < 568; y += 3) { P(116, y, 3, 1, '#E6D3BC'); P(336, y, 3, 1, '#E6D3BC'); }
      // the teacher's desk: a lit top, a pedestal of drawers, a kneehole in shadow, legs and a shadow on the rug
      P(212, 499, 132, 3, '#1B1420');
      P(209, 441, 134, 59, '#120D14');
      P(210, 442, 132, 1, '#F7C873'); P(210, 443, 132, 5, '#D9A066'); grain(212, 443, 128, 5, '#B07A47', 41, 'h'); P(210, 448, 132, 2, '#8C5A33');
      P(212, 450, 128, 47, '#8C5A33'); P(212, 450, 128, 1, '#6B4226');
      P(262, 452, 38, 45, '#4A2E1B'); P(262, 452, 38, 2, '#1B1420');
      for (let i = 0; i < 3; i++) { bevel(215, 453 + i * 14, 44, 12, '#B07A47', '#D9A066', '#6B4226'); P(234, 458 + i * 14, 6, 2, '#120D14'); P(235, 458 + i * 14, 4, 1, '#F7C873'); }
      bevel(303, 453, 34, 41, '#B07A47', '#D9A066', '#6B4226'); P(307, 457, 26, 33, '#8C5A33'); P(307, 457, 26, 1, '#6B4226');
      // books, an apple, a goldfish bowl
      [[296, 436, 38, '#3B82C4', '#87CEEB'], [299, 431, 33, '#7A3442', '#E2633B'], [297, 426, 36, '#2F6F67', '#6FB7A8']].forEach(([x, y, w, c, hi]) => {
        P(x - 1, y - 1, w + 2, 7, '#120D14'); P(x, y, w, 5, c); P(x, y, w, 1, hi); P(x + w - 4, y + 1, 3, 3, '#FFF7EA'); P(x + w - 4, y + 2, 3, 1, '#E6D3BC'); P(x + 3, y + 2, w - 9, 1, '#F7C873'); });
      disc(232, 437, 4, '#120D14'); disc(232, 437, 3, '#E2633B'); P(233, 438, 2, 2, '#7A3442'); DOT(230, 435, '#F7C873'); P(232, 431, 1, 3, '#5A3A22'); P(233, 431, 2, 1, '#3E7A62');
      const bx = 262, by = 433;
      disc(bx, by, 8, '#120D14'); disc(bx, by, 7, '#BDE6F5'); for (let dy = -3; dy <= 7; dy++) { const hw = Math.floor(Math.sqrt(49 - dy * dy) + 0.4); P(bx - hw, by + dy, 2 * hw + 1, 1, dy === -3 ? '#C9CCD3' : (dy > 5 ? '#B39A88' : '#6FB7A8')); }
      P(bx - 4, by - 7, 9, 1, '#120D14'); DOT(bx - 4, by - 4, '#FFF7EA'); DOT(bx - 5, by - 3, '#FFF7EA');
      // the goldfish swims back and forth on fours, bubbles rise
      const sp = t ? Math.floor(F / 4) % 12 : 0, fx = bx - 3 + (sp < 6 ? sp : 12 - sp), dir = sp < 6 ? 1 : -1;
      P(fx, by + 1, 3, 2, '#F2A541'); DOT(fx + (dir > 0 ? 2 : 0), by + 1, '#F7C873'); DOT(fx + (dir > 0 ? -1 : 3), by + 1, '#E2633B'); DOT(fx + (dir > 0 ? -1 : 3), by + 2, '#E2633B'); DOT(fx + (dir > 0 ? 2 : 0), by + 1, '#120D14');
      if (t) { const b = Math.floor(F / 5) % 6; if (b < 4) DOT(fx + 1, by - b, '#FFF7EA'); }
    }

    // ---- the workshop: a pegboard of hung tools, a workbench with a vise and a fan, a work light on a cord ----
    function roomShop(t, props) {
      P(0, 0, 360, 417, '#2B2033');
      for (let x = 0; x < 360; x += 12) { P(x, 0, 1, 417, '#1B1420'); P(x + 1, 0, 1, 417, '#3D2E45'); }   // board-and-batten wall
      [[30, 300], [102, 18], [270, 310], [190, 296]].forEach(([x, y]) => { DOT(x, y, '#1B1420'); DOT(x + 1, y, '#3D2E45'); });
      // the beam at the top
      P(0, 0, 360, 7, '#6B4226'); P(0, 0, 360, 1, '#8C5A33'); grain(0, 1, 360, 5, '#4A2E1B', 31, 'h'); P(0, 7, 360, 1, '#4A2E1B'); P(0, 8, 360, 1, '#120D14');
      windowAt(22, 14, 84, 30, t, {seed: 7, trees: true, birds: true, frame: '#8C5A33', hi: '#B07A47', lo: '#4A2E1B', sill: '#B07A47', sill2: '#8C5A33',
        clouds: [{w: 30, seed: 2, y: 2, x0: 40, every: 3}, {w: 20, seed: 6, y: 9, x0: 0, every: 2}, {w: 26, seed: 4, y: 5, x0: 95, every: 3}]});
      // the pegboard: a wooden trim, the board, a grid of holes; the content area stays plain board
      P(13, 77, 334, 206, '#120D14'); bevel(14, 78, 332, 204, '#8C5A33', '#D9A066', '#4A2E1B');
      P(16, 80, 328, 200, '#B07A47'); P(16, 80, 328, 1, '#8C5A33'); P(16, 80, 1, 200, '#8C5A33');
      for (let y = 84; y < 278; y += 6) for (let x = 20; x < 342; x += 6) DOT(x, y, '#8C5A33');
      shopTools();
      // the bench: a thick lit top, a front apron with grain, shadow beneath, legs and a lower shelf
      P(0, 330, 360, 1, '#120D14'); P(0, 331, 360, 1, '#F7C873'); P(0, 332, 360, 2, '#D9A066'); P(0, 334, 360, 6, '#B07A47'); grain(0, 334, 360, 6, '#8C5A33', 51, 'h'); P(0, 340, 360, 1, '#8C5A33'); P(0, 341, 360, 1, '#120D14');
      P(0, 342, 360, 75, '#1B1420');
      for (const x of [6, 340]) { P(x - 1, 342, 12, 75, '#120D14'); bevel(x, 342, 10, 75, '#8C5A33', '#B07A47', '#6B4226'); }
      P(0, 392, 360, 1, '#D9A066'); P(0, 393, 360, 3, '#8C5A33'); P(0, 396, 360, 1, '#120D14');
      [[318, 378, '#3B82C4', '#87CEEB'], [329, 381, '#E2633B', '#F2A541']].forEach(([x, y, c, hi]) => { P(x - 1, y - 1, 11, 393 - y + 1, '#120D14'); P(x, y, 9, 392 - y, '#9AA0AD'); P(x, y, 9, 1, '#C9CCD3'); P(x, y + 3, 9, 5, c); P(x, y + 3, 9, 1, hi); P(x + 7, y + 1, 2, 392 - y - 1, '#6B7080'); });
      // the vise on the right of the bench
      P(321, 318, 26, 14, '#120D14'); bevel(322, 322, 22, 9, '#3B82C4', '#87CEEB', '#253048'); P(322, 319, 6, 4, '#9AA0AD'); P(338, 319, 6, 4, '#9AA0AD'); P(322, 319, 6, 1, '#C9CCD3'); P(338, 319, 6, 1, '#C9CCD3');
      P(344, 325, 9, 2, '#120D14'); P(344, 325, 8, 1, '#C9CCD3'); P(351, 323, 2, 6, '#120D14'); DOT(351, 324, '#C9CCD3');
      // the work light: a cord from the beam, a cage lamp that sways a pixel at a time, its glow on the wall
      const sway = t ? [0, 1, 2, 2, 1, 0, -1, -2, -2, -1][Math.floor(F / 4) % 10] : 0;
      const lx = 232 + sway, ly = 34;
      { for (let r = 12; r >= 7; r -= 5) for (let dy = -r; dy <= r; dy++) { const hw = Math.floor(Math.sqrt(r * r - dy * dy)); for (let dx = -hw; dx <= hw; dx++) if (((lx + dx + ly + dy) & 1) === 0 && (r === 7 || Math.abs(dx) > 5 || Math.abs(dy) > 5) && ly + dy > 8 && ly + dy < 52) DOT(lx + dx, ly + dy + 3, r === 7 ? '#7A4E2C' : '#3D2E45'); } }
      line(232, 9, lx, ly - 5, '#120D14');
      P(lx - 4, ly - 5, 9, 1, '#120D14'); P(lx - 5, ly - 4, 11, 4, '#120D14'); P(lx - 4, ly - 4, 9, 1, '#F7C873'); P(lx - 4, ly - 3, 9, 2, '#F2A541'); P(lx + 2, ly - 3, 2, 2, '#B07A47');
      P(lx - 3, ly, 7, 5, '#FFF7EA'); P(lx - 2, ly + 5, 5, 1, '#FFF7EA'); DOT(lx - 2, ly + 1, '#F7C873');
      P(lx - 3, ly + 2, 7, 1, '#4A4E5A'); P(lx, ly, 1, 6, '#4A4E5A'); P(lx - 2, ly + 6, 5, 1, '#4A4E5A');
      // the desk fan on the left of the bench: blades turn on twos
      const fx = 15, fy = 314;
      P(fx - 7, 329, 15, 2, '#120D14'); P(fx - 6, 328, 13, 1, '#6B7080'); P(fx - 6, 329, 13, 1, '#4A4E5A'); P(fx - 1, 322, 3, 6, '#4A4E5A'); DOT(fx - 1, 322, '#9AA0AD');
      disc(fx, fy, 10, '#120D14'); disc(fx, fy, 9, '#9AA0AD'); disc(fx + 1, fy + 1, 8, '#4A4E5A'); disc(fx, fy, 8, '#1B1420');
      const ang = t ? (Math.floor(F / 2) % 3) * (Math.PI * 2 / 9) : 0;
      for (let dy = -7; dy <= 7; dy++) for (let dx = -7; dx <= 7; dx++) {
        const r = Math.hypot(dx, dy); if (r > 7.4 || r < 1.5) continue;
        let a = Math.atan2(dy, dx) - ang; a = ((a % (Math.PI * 2 / 3)) + Math.PI * 2 / 3) % (Math.PI * 2 / 3);
        if (a < 0.75) DOT(fx + dx, fy + dy, a < 0.25 ? '#FFF7EA' : '#C9CCD3');
      }
      P(fx - 1, fy - 1, 3, 3, '#6B7080'); DOT(fx - 1, fy - 1, '#C9CCD3');
      P(fx - 8, fy, 17, 1, '#6B7080'); P(fx, fy - 8, 1, 17, '#6B7080');   // the cage
      // sawdust drifting down off the bench edge
      if (t) for (let i = 0; i < 6; i++) { const x = 312 + i * 7 + Math.floor(hash(i * 3.1) * 4), ph = (F + i * 41) % 160, y = 342 + Math.floor(ph / 2); if (y < 416 && !(x > 338 && x < 352)) DOT(x + (Math.floor(ph / 16) % 2), y, '#D9A066'); }
      // the floor: sealed concrete with joints toward the back wall
      P(0, 417, 360, 1, '#120D14'); P(0, 418, 360, 222, '#4A4E5A'); P(0, 418, 360, 2, '#2B2033');
      [432, 456, 494, 556].forEach((y) => { P(0, y, 360, 1, '#3D2E45'); P(0, y + 1, 360, 1, '#6B7080'); });
      for (let i = -3; i <= 4; i++) line(180 + i * 70, 420, 180 + i * 230, 640, '#3D2E45');
      dith(60, 590, 40, 8, '#3D2E45', 0); dith(66, 588, 26, 2, '#3D2E45', 1);   // an oil stain
      if (props) shopProps();
    }
    // the hung tools, each casting a 1 pixel shadow on the board; all in the strip right of the text (x 936 on)
    function shopTools() {
      const T1 = [   // [x, y, w, h, color] in pixels
        // hammer: steel head with a claw, a wooden handle, a red grip
        [314, 86, 19, 6, '#120D14'], [315, 87, 17, 4, '#9AA0AD'], [315, 87, 17, 1, '#C9CCD3'], [315, 90, 17, 1, '#6B7080'], [314, 88, 3, 2, '#B07A47'],
        [321, 92, 5, 34, '#120D14'], [322, 92, 3, 33, '#B07A47'], [322, 92, 1, 33, '#D9A066'], [324, 92, 1, 33, '#8C5A33'], [322, 112, 3, 13, '#E2633B'], [324, 112, 1, 13, '#7A3442'], [322, 112, 3, 1, '#F2A541'],
        // wrench: open jaw, shaft, box end
        [334, 86, 9, 8, '#120D14'], [335, 87, 7, 6, '#9AA0AD'], [337, 86, 3, 4, '#B07A47'], [335, 87, 1, 6, '#C9CCD3'],
        [336, 93, 5, 30, '#120D14'], [337, 93, 3, 29, '#9AA0AD'], [337, 93, 1, 29, '#C9CCD3'], [339, 93, 1, 29, '#6B7080'],
        [334, 121, 9, 8, '#120D14'], [335, 122, 7, 6, '#9AA0AD'], [337, 124, 3, 2, '#B07A47'], [335, 122, 7, 1, '#C9CCD3'],
        // handsaw: wooden handle with a grip hole, a tapered blade, teeth down the right edge
        [313, 134, 22, 15, '#120D14'], [314, 135, 20, 13, '#B07A47'], [314, 135, 20, 1, '#D9A066'], [314, 135, 1, 13, '#D9A066'], [319, 138, 10, 5, '#B07A47'], [320, 139, 8, 3, '#120D14'], [333, 136, 1, 12, '#8C5A33'],
        [315, 149, 20, 12, '#120D14'], [316, 149, 18, 12, '#C9CCD3'], [316, 161, 17, 12, '#120D14'], [317, 161, 15, 12, '#C9CCD3'], [317, 173, 15, 12, '#120D14'], [318, 173, 13, 12, '#C9CCD3'], [318, 185, 12, 10, '#120D14'], [319, 185, 10, 9, '#C9CCD3'],
        [316, 149, 1, 12, '#FFF7EA'], [317, 161, 1, 12, '#FFF7EA'], [318, 173, 1, 12, '#FFF7EA'], [319, 185, 1, 9, '#FFF7EA'],
        // square: a steel L with tick marks
        [313, 203, 6, 36, '#120D14'], [314, 204, 4, 34, '#9AA0AD'], [314, 204, 1, 34, '#C9CCD3'], [313, 234, 30, 6, '#120D14'], [314, 235, 28, 4, '#9AA0AD'], [314, 235, 28, 1, '#C9CCD3'], [314, 238, 28, 1, '#6B7080'],
        // tape measure: a yellow case, a hub, the tape tongue and hook
        [318, 248, 20, 18, '#120D14'], [319, 249, 18, 16, '#F2A541'], [319, 249, 18, 1, '#F7C873'], [319, 249, 1, 16, '#F7C873'], [336, 250, 1, 15, '#B07A47'], [319, 264, 18, 1, '#B07A47'],
        [324, 253, 8, 8, '#120D14'], [325, 254, 6, 6, '#4A4E5A'], [325, 254, 6, 1, '#6B7080'], [327, 256, 2, 2, '#C9CCD3'],
        [313, 262, 6, 3, '#120D14'], [314, 263, 5, 1, '#F7C873'], [312, 261, 2, 5, '#120D14'], [312, 262, 1, 3, '#9AA0AD'],
      ];
      T1.forEach(([x, y, w, h]) => P(x + 1, y + 1, w, h, '#8C5A33'));   // shadows first
      T1.forEach(([x, y, w, h, c]) => P(x, y, w, h, c));
      for (let y = 151; y < 193; y += 2) DOT(y < 161 ? 334 : (y < 173 ? 332 : (y < 185 ? 331 : 329)), y, '#6B7080');   // saw teeth
      for (let x = 316; x < 342; x += 3) DOT(x, 236, '#4A4E5A'); for (let y = 206; y < 234; y += 3) DOT(316, y, '#4A4E5A');
      [[323, 84], [337, 84], [323, 132], [316, 201], [327, 246]].forEach(([x, y]) => { DOT(x, y, '#C9CCD3'); DOT(x, y + 1, '#4A4E5A'); });   // pegs
    }
    function shopProps() {
      // a red rolling tool chest with four drawers
      P(244, 513, 76, 3, '#2B2033');
      P(241, 431, 76, 82, '#120D14'); bevel(242, 432, 74, 80, '#E2633B', '#F2A541', '#7A3442');
      P(242, 432, 74, 1, '#F7C873'); P(243, 439, 72, 1, '#7A3442');
      P(266, 427, 26, 4, '#120D14'); P(268, 428, 22, 2, '#C9CCD3'); P(268, 429, 22, 1, '#6B7080');
      for (let i = 0; i < 4; i++) { const y = 442 + i * 16; bevel(246, y, 66, 14, '#E2633B', '#F2A541', '#7A3442'); P(262, y + 5, 34, 3, '#120D14'); P(263, y + 5, 32, 1, '#FFF7EA'); P(263, y + 6, 32, 1, '#9AA0AD'); }
      [[246, 512], [304, 512]].forEach(([x, y]) => { P(x, y, 8, 5, '#120D14'); P(x + 2, y + 1, 4, 3, '#6B7080'); });
      // a bucket with a label band and a wire handle
      P(166, 506, 32, 3, '#2B2033');
      line(170, 470, 182, 462, '#6B7080'); line(182, 462, 194, 470, '#6B7080');
      P(167, 469, 30, 40, '#120D14'); P(168, 470, 28, 38, '#C9CCD3'); P(168, 470, 28, 2, '#FFF7EA'); P(168, 470, 2, 38, '#FFF7EA'); P(191, 472, 5, 36, '#9AA0AD'); P(168, 482, 28, 8, '#F2A541'); P(168, 482, 28, 1, '#F7C873'); P(191, 482, 5, 8, '#B07A47');
      // a little hill of sawdust
      for (let i = 0; i < 9; i++) P(96 - i * 2, 530 + i, 8 + i * 4, 1, i < 2 ? '#F7C873' : '#D9A066'); dith(80, 535, 40, 4, '#B07A47', 1);
    }

    // ---- the garage: a sectional door with windows, rails and an opener; shelves of labeled bins; a fluorescent tube ----
    function roomGarage(t, props) {
      P(0, 0, 360, 417, '#4A4E5A');
      for (let y = 9; y < 417; y += 8) { P(0, y, 360, 1, '#3D2E45'); P(0, y + 1, 360, 1, '#6B7080'); for (let x = ((y >> 3) & 1) * 8; x < 360; x += 16) P(x, y + 1, 1, 7, '#3D2E45'); }   // painted block
      // the ceiling and joists
      P(0, 0, 360, 9, '#2B2033'); for (let x = 6; x < 360; x += 30) { P(x, 0, 8, 8, '#8C5A33'); P(x, 0, 1, 8, '#B07A47'); P(x + 7, 0, 1, 8, '#6B4226'); } P(0, 8, 360, 1, '#120D14');
      // the fluorescent fixture: a steel housing, two tubes; a soft flicker now and then (at most 2 changes a second)
      const ph = F % 210, dim = t && ((ph >= 100 && ph < 104) || (ph >= 110 && ph < 112));
      dith(140, 24, 80, 7, dim ? '#4A4E5A' : '#6B7080', 0);
      P(142, 12, 76, 10, '#120D14'); bevel(143, 13, 74, 6, '#C9CCD3', '#FFF7EA', '#6B7080');
      P(144, 19, 72, 3, '#120D14'); P(145, 19, 70, 1, dim ? '#9AA0AD' : '#FFF7EA'); P(145, 21, 70, 1, dim ? '#9AA0AD' : '#FFF7EA'); P(145, 20, 70, 1, dim ? '#6B7080' : '#F4E6D3');
      P(150, 9, 1, 4, '#120D14'); P(209, 9, 1, 4, '#120D14');
      // the opener: a motor box on the ceiling with a blinking light, its rail running to the door header
      P(262, 30, 30, 16, '#120D14'); bevel(263, 31, 28, 14, '#C9CCD3', '#FFF7EA', '#6B7080'); P(265, 41, 24, 2, '#9AA0AD'); P(268, 34, 18, 1, '#9AA0AD');
      const led = t ? (Math.floor(F / 20) % 3 === 0) : true; P(285, 35, 3, 2, '#120D14'); DOT(286, 35, led ? '#6FB7A8' : '#24453A');
      P(170, 36, 92, 3, '#120D14'); P(170, 37, 92, 1, '#9AA0AD'); P(274, 9, 2, 22, '#6B7080');
      // the header and jambs around the door, with the tracks and rollers
      P(22, 70, 316, 7, '#120D14'); bevel(23, 71, 314, 5, '#9AA0AD', '#C9CCD3', '#6B7080');
      for (const x of [22, 332]) { P(x, 76, 6, 266, '#120D14'); P(x + 1, 76, 4, 265, '#6B7080'); P(x + 1, 76, 1, 265, '#9AA0AD'); P(x + 4, 76, 1, 265, '#4A4E5A'); }
      // the door: four sections, each with a lit top lip, a shadowed joint and quiet raised panels; windows in the top one
      P(28, 77, 304, 264, '#6B7080');
      for (let s = 0; s < 4; s++) {
        const y = 77 + s * 66;
        P(28, y, 304, 1, '#9AA0AD'); P(28, y + 64, 304, 1, '#4A4E5A'); P(28, y + 65, 304, 1, '#2B2033');
        if (s > 0) for (let i = 0; i < 4; i++) { const x = 34 + i * 75; P(x, y + 8, 68, 1, '#9AA0AD'); P(x, y + 8, 1, 48, '#9AA0AD'); P(x, y + 56, 68, 1, '#4A4E5A'); P(x + 67, y + 8, 1, 49, '#4A4E5A'); }
        for (const x of [29, 329]) { P(x, y + 30, 2, 5, '#120D14'); DOT(x, y + 31, '#C9CCD3'); }   // hinges and rollers
      }
      for (let i = 0; i < 4; i++) {
        const x = 34 + i * 75;
        windowAt(x + 1, 80, 66, 12, t, {seed: 11 + i, frame: '#9AA0AD', hi: '#C9CCD3', lo: '#4A4E5A', sill: '#9AA0AD', sill2: '#6B7080', bars: 'v', glint: false,
          clouds: [{w: 26, seed: 3 + i, y: 0, x0: 20 + i * 66, every: 3}]});
      }
      P(166, 330, 28, 4, '#120D14'); P(167, 330, 26, 2, '#C9CCD3');   // the handle
      // shelves on both sides: steel uprights, boards, labeled bins
      for (const x0 of [0, 337]) {
        const w = 23;
        P(x0 + 1, 96, 2, 320, '#120D14'); P(x0 + w - 2, 96, 2, 320, '#120D14'); P(x0 + 1, 96, 1, 320, '#9AA0AD'); P(x0 + w - 2, 96, 1, 320, '#9AA0AD');
        [130, 196, 262, 328, 394].forEach((y, i) => {
          if (x0 && y === 328) { P(x0, y, w, 3, '#120D14'); P(x0, y, w, 1, '#C9CCD3'); P(x0, y + 1, w, 1, '#9AA0AD'); return; }   // the charger sits here
          P(x0, y, w, 3, '#120D14'); P(x0, y, w, 1, '#C9CCD3'); P(x0, y + 1, w, 1, '#9AA0AD');
          const c = [['#3B82C4', '#87CEEB', '#253048'], ['#E2633B', '#F2A541', '#7A3442'], ['#2F6F67', '#6FB7A8', '#245752'], ['#F2A541', '#F7C873', '#B07A47'], ['#3B82C4', '#87CEEB', '#253048']][(i + (x0 ? 2 : 0)) % 5];
          P(x0 + 2, y - 15, w - 4, 15, '#120D14'); bevel(x0 + 3, y - 14, w - 6, 14, c[0], c[1], c[2]); P(x0 + 6, y - 10, w - 12, 4, '#FFF7EA'); P(x0 + 7, y - 9, w - 15, 1, '#9AA0AD');
        });
      }
      // the battery charger on the right shelf, its light blinking slowly
      P(340, 316, 17, 12, '#120D14'); bevel(341, 317, 15, 11, '#4A4E5A', '#6B7080', '#2B2033'); P(343, 314, 8, 3, '#120D14'); P(344, 315, 6, 2, '#F2A541');
      const chg = t ? Math.floor(F / 15) % 2 : 0; P(352, 319, 2, 2, chg ? '#6FB7A8' : '#24453A');
      // the floor: concrete with a drain, joints and tire marks
      P(0, 417, 360, 1, '#120D14'); P(0, 418, 360, 222, '#6B7080'); P(0, 418, 360, 2, '#4A4E5A');
      [440, 480, 548].forEach((y) => { P(0, y, 360, 1, '#4A4E5A'); P(0, y + 1, 360, 1, '#9AA0AD'); });
      for (let i = -2; i <= 3; i++) line(180 + i * 90, 420, 180 + i * 260, 640, '#4A4E5A');
      dith(150, 600, 70, 12, '#4A4E5A', 0); dith(140, 604, 90, 4, '#4A4E5A', 1);   // tire marks and a stain
      P(172, 470, 16, 6, '#120D14'); for (let i = 0; i < 4; i++) P(174 + i * 4, 471, 2, 4, '#4A4E5A');   // the drain
      if (props) garageProps(t);
    }
    function garageProps(t) {
      // stacked tires: rounded sidewalls, a tread band of blocks, a sheen on the top one
      for (let i = 0; i < 3; i++) {
        const y = 500 - i * 20;
        P(260, y, 72, 20, '#120D14'); P(258, y + 2, 76, 16, '#120D14');
        P(261, y + 2, 70, 16, '#2B2033'); P(259, y + 4, 74, 12, '#2B2033');
        P(261, y + 2, 70, 2, '#4A4E5A'); P(259, y + 4, 2, 10, '#4A4E5A');
        for (let x = 263; x < 330; x += 4) { P(x, y + 7, 2, 6, '#1B1420'); DOT(x, y + 7, '#3D2E45'); }
        P(261, y + 16, 70, 1, '#1B1420');
      }
      P(276, 438, 40, 3, '#120D14'); P(278, 437, 36, 2, '#1B1420'); P(270, 441, 52, 1, '#6B7080');
      P(256, 520, 82, 3, '#4A4E5A');
      // the toolbox: a red box with a lid, a latch and a handle
      P(168, 520, 70, 3, '#4A4E5A');
      P(169, 482, 66, 39, '#120D14'); bevel(170, 483, 64, 37, '#E2633B', '#F2A541', '#7A3442'); P(170, 494, 64, 1, '#7A3442'); P(170, 495, 64, 1, '#F2A541');
      P(196, 490, 12, 7, '#120D14'); P(197, 491, 10, 5, '#C9CCD3'); P(197, 491, 10, 1, '#FFF7EA');
      P(186, 474, 32, 9, '#120D14'); P(188, 476, 28, 7, '#E2633B'); P(190, 478, 24, 5, '#4A4E5A'); P(188, 476, 28, 1, '#F2A541');
      // the shop vac
      P(96, 514, 44, 3, '#4A4E5A');
      P(97, 470, 42, 46, '#120D14'); bevel(98, 471, 40, 44, '#F2A541', '#F7C873', '#B07A47'); P(98, 471, 40, 8, '#4A4E5A'); P(98, 471, 40, 1, '#6B7080');
      [[100, 513], [130, 513]].forEach(([x, y]) => { P(x, y, 6, 5, '#120D14'); DOT(x + 2, y + 2, '#6B7080'); });
      line(138, 476, 150, 470, '#120D14'); line(150, 470, 158, 482, '#120D14'); line(139, 477, 151, 471, '#4A4E5A');
    }

    // ---- framing: a house going up: studs and plates against the sky, hills behind, a flag topping out, lumber and sawhorses ----
    function roomFraming(t, props) {
      // the sky with two layers of clouds (the far ones slower), hills and a tree line on the horizon
      sky(0, 0, 360, 405, [
        {w: 46, seed: 21, y: 6, x0: 30, every: 2}, {w: 30, seed: 22, y: 20, x0: 230, every: 3}, {w: 54, seed: 23, y: 2, x0: 330, every: 2},
        {w: 26, seed: 24, y: 34, x0: 120, every: 4}, {w: 38, seed: 25, y: 98, x0: 60, every: 3}, {w: 30, seed: 26, y: 160, x0: 300, every: 4},
        {w: 44, seed: 27, y: 230, x0: 180, every: 3}], t);
      for (let x = 0; x < 360; x++) { const h1 = 22 + Math.round(10 * Math.sin(x * 0.021 + 1) + 6 * Math.sin(x * 0.07)); P(x, 405 - h1, 1, h1, '#3E7A62'); DOT(x, 405 - h1, '#6FB7A8'); }
      for (let x = 0; x < 360; x++) { const h2 = 10 + Math.round(4 + 3 * Math.sin(x * 0.35) + hash(x * 0.71) * 3); P(x, 405 - h2, 1, h2, '#2F5A4A'); if (x % 9 < 2) DOT(x, 405 - h2, '#3E7A62'); }
      // birds cross the top of the sky (above the level bar)
      if (t) for (let i = 0; i < 3; i++) { const per = 760, ph = (F + i * 253) % per, x = -10 + Math.floor(ph / 2), y = 14 + i * 9 + (Math.floor(ph / 10) % 2); if (x < 366) bird(x, y, Math.floor(ph / 4) + i); }
      // the studs: lit on the left, shaded on the right, a little grain and a nail at each plate
      for (let s = 0; s < 9; s++) {
        const x = 10 + s * 44;
        P(x - 1, 76, 12, 330, '#8C5A33'); P(x, 76, 1, 330, '#F7C873'); P(x + 1, 76, 7, 330, '#D9A066'); P(x + 8, 76, 2, 330, '#B07A47');
        grain(x + 2, 78, 5, 326, '#B07A47', s * 13, 'v');
        [80, 400].forEach((y) => { DOT(x + 3, y, '#4A4E5A'); DOT(x + 6, y + 1, '#4A4E5A'); });
      }
      // the top plate, doubled, and the bottom plate
      const plate = (y, h, seed) => { P(0, y, 360, h, '#8C5A33'); P(0, y + 1, 360, 1, '#F7C873'); P(0, y + 2, 360, h - 4, '#D9A066'); P(0, y + h - 2, 360, 1, '#B07A47'); grain(0, y + 2, 360, h - 4, '#B07A47', seed, 'h'); };
      plate(62, 7, 61); plate(69, 8, 62); plate(405, 12, 63);
      // a flag topping out the frame, fluttering on threes
      P(346, 26, 2, 37, '#120D14'); P(346, 26, 1, 37, '#C9CCD3'); DOT(346, 25, '#F7C873');
      const fl = t ? Math.floor(F / 3) % 4 : 0, fy = [0, 1, 0, -1];
      for (let i = 0; i < 14; i++) { const yy = 28 + fy[(fl + Math.floor(i / 4)) % 4], c = (i + fl) % 8 < 4 ? '#E2633B' : '#F2A541'; P(332 + i, yy, 1, 8, c); DOT(332 + i, yy + 7, '#7A3442'); }
      DOT(331, 28 + fy[(fl + 3) % 4], '#E2633B');
      // the deck: plywood sheets in perspective, nail lines, cloud shadows drifting over it
      P(0, 417, 360, 223, '#B07A47'); P(0, 417, 360, 1, '#120D14');
      [[419, 18], [437, 30], [467, 48], [515, 72], [587, 60]].forEach(([y, h], i) => { P(0, y, 360, 1, '#D9A066'); P(0, y + h - 1, 360, 1, '#8C5A33'); for (let x = (i % 2) * 40 + 20; x < 360; x += 80 + i * 20) { P(x, y + 1, 1, h - 2, '#8C5A33'); P(x + 1, y + 1, 1, h - 2, '#D9A066'); } for (let x = 6; x < 360; x += 8) DOT(x, y + Math.floor(h / 2), '#8C5A33'); });
      if (t) [[70, 12, 3, 430, 0], [96, 16, 4, 520, 150]].forEach(([w, h, every, y, x0]) => { const span = 360 + w; const x = ((Math.floor(x0 + F / every) % span) + span) % span - w; for (let j = 0; j < h; j++) { const hw = Math.round(w / 2 * Math.sqrt(1 - Math.pow((j - h / 2 + 0.5) / (h / 2), 2))); dith(Math.max(0, x + w / 2 - hw), y + j, Math.min(360, x + w / 2 + hw) - Math.max(0, x + w / 2 - hw), 1, '#8C5A33', j & 1); } });
      if (props) framingProps(t);
    }
    function framingProps(t) {
      // a lumber stack: boards on stickers, end grain to the right
      P(122, 526, 152, 3, '#8C5A33');
      for (let i = 0; i < 5; i++) {
        const y = 520 - i * 7, x = 126 + (i % 2) * 6, w = 140 - (i % 2) * 8;
        P(x - 1, y - 1, w + 2, 8, '#120D14'); P(x, y, w, 6, '#D9A066'); P(x, y, w, 1, '#F7C873'); P(x, y + 5, w, 1, '#B07A47'); grain(x + 2, y + 1, w - 8, 4, '#B07A47', i * 7, 'h');
        P(x + w - 6, y, 6, 6, '#F7C873'); P(x + w - 5, y + 1, 4, 4, '#D9A066'); DOT(x + w - 3, y + 2, '#B07A47'); DOT(x + w - 4, y + 3, '#B07A47');
        if (i < 4) { P(x + 14, y - 1, 4, 1, '#6B4226'); P(x + w - 24, y - 1, 4, 1, '#6B4226'); }
      }
      // two sawhorses with a plank across them
      P(186, 467, 120, 2, '#1B1420'); P(185, 452, 122, 6, '#120D14'); P(186, 453, 120, 1, '#F7C873'); P(186, 454, 120, 3, '#D9A066'); P(186, 457, 120, 1, '#B07A47'); grain(188, 454, 116, 3, '#B07A47', 77, 'h');
      for (const x of [198, 284]) {
        P(x - 6, 459, 22, 4, '#120D14'); P(x - 5, 460, 20, 2, '#B07A47'); P(x - 5, 460, 20, 1, '#D9A066');
        line(x - 3, 463, x - 9, 504, '#120D14'); line(x - 2, 463, x - 8, 504, '#8C5A33'); line(x + 13, 463, x + 19, 504, '#120D14'); line(x + 12, 463, x + 18, 504, '#6B4226');
        line(x + 1, 463, x - 2, 500, '#120D14'); line(x + 9, 463, x + 12, 500, '#120D14');
        P(x - 6, 486, 22, 2, '#8C5A33');
      }
      P(196, 445, 50, 7, '#120D14'); P(197, 446, 48, 5, '#F4E6D3'); P(197, 446, 48, 1, '#FFF7EA'); P(197, 450, 48, 1, '#C9CCD3');   // a sheet of drywall offcut on the plank
      // a paint bucket and an orange cord
      P(312, 492, 28, 3, '#8C5A33'); P(312, 462, 26, 31, '#120D14'); P(313, 463, 24, 29, '#C9CCD3'); P(313, 463, 2, 29, '#FFF7EA'); P(332, 463, 5, 29, '#9AA0AD'); P(313, 472, 24, 9, '#3B82C4'); P(313, 472, 24, 1, '#87CEEB');
      P(0, 556, 100, 2, '#120D14'); P(0, 556, 100, 1, '#F2A541'); P(98, 556, 2, 22, '#120D14'); DOT(98, 556, '#F2A541'); P(99, 557, 1, 20, '#F2A541'); P(98, 576, 120, 2, '#120D14'); P(98, 576, 120, 1, '#F2A541');
    }
    // a game panel: a 1 pixel drop shadow, a notched box with a lit top-left edge and a shaded bottom-right edge, the
    // cream double border inside, an optional title tab
    const TONES = {'#1B1420': ['#3D2E45', '#120D14'], '#F2A541': ['#F7C873', '#B07A47'], '#24453A': ['#2F5A4A', '#1A332B'], '#2B2033': ['#3D2E45', '#120D14'],
      '#7A3442': ['#E2633B', '#3D2E45'], '#FFF7EA': ['#FFFFFF', '#E6D3BC'], '#3B82C4': ['#87CEEB', '#253048']};
    const tones = (c) => TONES[(col(c) || '').toUpperCase()] || ['#3D2E45', '#120D14'];
    const quad = (x, y, w, h, c) => shape([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], {fill: c, line: false});
    const finish = (x, y, w, h, fill, o = {}) => {   // the game-UI edge on any box: shadow, notched fill, light and shade lines
      const u = G, [hi, lo] = tones(fill), n = Math.min(2 * u, w / 4, h / 4);
      if (o.shadow !== false) shape(rectPts(x + u, y + u, w, h, 0), {fill: '#120D14', line: false});
      shape(rectPts(x, y, w, h, 0), {fill, line: false});
      quad(x + n, y, w - 2 * n, u, hi); quad(x, y + n, u, h - 2 * n, hi);
      quad(x + n, y + h - u, w - 2 * n, u, lo); quad(x + w - u, y + n, u, h - 2 * n, lo);
      if (n >= 2 * u) { quad(x + u, y + u, u, u, hi); quad(x + w - 2 * u, y + h - 2 * u, u, u, lo); }   // the inner corner pixel of the notch
    };
    k.finish = finish;
    k.panel2 = function (x, y, w, h, o = {}) {
      if (!look.bitmap) {
        shape(rectPts(x + 12, y + 12, w, h, 0), {fill: '#120D14', line: false, alpha: 0.6});
        shape(rectPts(x, y, w, h, 0), {fill: o.fill || 'card', line: false});
        shape(rectPts(x + 6, y + 6, w - 12, h - 12, 0), {stroke: o.border || 'line', lw: 6, line: false});
      } else {
        finish(x, y, w, h, o.fill || 'card');
        shape(rectPts(x + 6, y + 6, w - 12, h - 12, 0), {stroke: o.border || 'line', lw: 6, line: false});
      }
      if (o.title) { const tw = measure(o.title, {size: 30}) + 36; if (look.bitmap) finish(x + 24, y - 24, tw, 48, o.tag || 'tag'); else shape(rectPts(x + 24, y - 24, tw, 48, 0), {fill: o.tag || 'tag', line: false}); text(o.title, x + 42, y - 18, {size: 30, color: 'tagText'}); }
    };

    k.cam = function (sc, cx, cy) { ctx.translate(cx, cy); ctx.scale(sc, sc); ctx.translate(-cx, -cy); };

    // ---- motion: the moves that keep a lesson alive (Todd, Oct 28, 1:33 pm: "keep things moving") ----
    // pixel sparks flying out of a point for 0.7 s
    k.burst = function (x, y, t0, o = {}) {
      const d = T - t0, life = o.life || 0.7; if (d < 0 || d > life) return;
      const n = o.n || 16, r = o.r || 230, cols = o.colors || ['accent', 'accent2', 'paper'], q = easeOut(d / life);
      for (let i = 0; i < n; i++) {
        const a = hash(i * 1.7 + t0 * 3.1) * TAU, sp = (0.45 + hash(i * 4.3 + t0) * 0.75) * r;
        const s = Math.max(3, (o.size || 15) * (1 - d / life));
        R(x + Math.cos(a) * sp * q - s / 2, y + Math.sin(a) * sp * q + 260 * d * d - s / 2, s, s, cols[i % cols.length]);
      }
    };
    // a stamp that hits: k.stampIn(t0, (te) => draw, {at: [x, y]}). It drops in over 3 frames, lands at t0 (put the stamp
    // sound there), freezes 3 frames with a 1 pixel shiver (the hit-stop; the voice and host keep going), squashes 1.20 x 0.85
    // for 2 frames and 0.95 x 1.05 for 1, then settles over 6. draw gets the stamp's own clock te: negative while it drops,
    // 0 through the freeze, then the time since the freeze ended. at is where it lands (its bottom middle). Returns false
    // before it appears. o.freeze: frames (3; 5 for the one big verdict); o.drop: seconds to drop in (0.1; 0 to appear at t0).
    k.stampIn = function (t0, draw, o = {}) {
      const fr = o.freeze != null ? o.freeze : 3, drop = o.drop != null ? o.drop : 0.1;
      if (T < t0 - drop) return false;
      const f = (T - t0) * FR + 0.005, [ax, ay] = o.at || [540, 960];   // + a hair: frame times arrive with rounding
      let sx = 1, sy = 1, dx = 0, te;
      if (f < 0) { const q = clamp((T - t0 + drop) / Math.max(1e-6, drop)); sx = sy = 1 + 0.5 * (1 - q) * (1 - q); te = T - t0; }
      else if (f < fr) { te = 0; dx = (Math.floor(f) % 2 ? -1 : 1) * LPX; }
      else {
        te = T - t0 - fr / FR; const g = f - fr;
        if (g < 2) { sx = 1.2; sy = 0.85; } else if (g < 3) { sx = 0.95; sy = 1.05; }
        else if (g < 9) { const q = easeOut((g - 3) / 6); sx = 0.95 + 0.05 * q; sy = 1.05 - 0.05 * q; }
      }
      ctx.save(); ctx.translate(ax + dx, ay); ctx.scale(sx, sy); ctx.translate(-ax, -ay);
      draw(te);
      ctx.restore();
      return true;
    };
    // a line of text that slams in big and settles, with a short shake; {stamp: true} lands it with k.stampIn instead
    k.slam = function (s, x, y, t0, o = {}) {
      if (o.stamp) {
        const w = measure(s, o), h = o.size || 48, cx = o.align === 'center' ? x : (o.align === 'right' ? x - w / 2 : x + w / 2);
        return k.stampIn(t0, () => text(s, x, y, o), {at: [cx, y + h], freeze: o.freeze, drop: o.drop});
      }
      const d = T - t0; if (d < 0) return;
      const q = clamp(d / (o.dur || 0.2)), sc = 1 + (o.from || 0.9) * Math.pow(1 - q, 2);
      const sh = d < 0.25 ? (1 - d / 0.25) * (o.shake != null ? o.shake : 3) : 0;
      ctx.save(); ctx.translate(x + Math.sin(T * 97) * sh, y + Math.cos(T * 83) * sh); ctx.scale(sc, sc);
      text(s, 0, 0, Object.assign({}, o, {alpha: (o.alpha != null ? o.alpha : 1) * clamp(q * 3)}));
      // steady life (Todd, Oct 28: motion without the swim): once a slammed line has landed, a shine sweeps across it
      // every 1.4 s on whole low-res pixels. Nothing moves or rescales; only the glyphs light up as the band passes.
      const size = o.size || 48;
      if (look.bitmap && size >= 60 && o.glint !== false && d > 0.6) {
        const g = ((d - 0.6 + (o.glintAt || 0)) % 1.4) / 0.5;
        if (g < 1) {
          const w = measure(s, o), h = bmHeight(size), ax = o.align === 'center' ? -w / 2 : (o.align === 'right' ? -w : 0);
          const bw = Math.max(2 * U, Math.round(h * 0.22 / U) * U), sl = h * 0.45;
          const bx = Math.round((ax - bw + (w + 2 * bw + sl) * g) / U) * U;
          const light = /^#(FFF7EA|FFFFFF|F4E6D3)$/i.test(col(o.color || 'ink')) || o.color === 'paper';
          ctx.beginPath(); ctx.moveTo(bx, -U); ctx.lineTo(bx + bw, -U); ctx.lineTo(bx + bw - sl, h + U); ctx.lineTo(bx - sl, h + U); ctx.closePath(); ctx.clip();
          text(s, 0, 0, Object.assign({}, o, {color: light ? '#F7C873' : '#FFF7EA', lint: false, drop: null}));
        }
      }
      ctx.restore();
    };
    // a bar that sweeps across behind a line, like a highlighter (game style: hard edges)
    k.sweep = function (x, y, w, h, t0, o = {}) {
      const q = easeOut((T - t0) / (o.dur || 0.3)); if (q <= 0) return;
      shape(rectPts(x, y, w * q, h, 0), {fill: o.color || 'accent', line: false, alpha: o.alpha != null ? o.alpha : 1});
    };
    // drifting motes (dust in the light, chalk in the air)
    k.motes = function (x, y, w, h, c, n = 14) {
      for (let i = 0; i < n; i++) {
        const sp = 10 + hash(i * 9.1) * 24, px = x + ((hash(i * 3.7) * w + T * sp) % w), py = y + ((hash(i * 5.9) * h - T * sp * 0.6) % h + h) % h;
        R(px, py, 6, 6, c);
      }
    };
    return k;
  }
  window.Kit = {make};
})();
