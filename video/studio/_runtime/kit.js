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

  function rectPts(x, y, w, h, r = 0) {
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
    // shape(points, {fill, stroke, lw, closed, alpha, line: false}) in color roles or literal colors.
    function shape(pts, o = {}) {
      const id = o.id != null ? o.id : ++uid;
      const closed = o.closed !== false;
      ctx.save();
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
    function fontStr(o) {
      const fam = o.font === 'body' ? look.font.body : look.font.display;
      return `${o.weight || 700} ${o.size || 48}px ${fam}`;
    }
    function measure(s, o) { ctx.save(); ctx.font = fontStr(o); setTrack(o); const w = ctx.measureText(s).width; ctx.restore(); return w; }
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
      const size = o.size || 48, lh = (o.lh || 1.15) * size;
      const lines = o.maxW ? wrap(s, o, o.maxW) : [s];
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
      if (!look.lineArt && look.name === 'clean' && o.shadow !== false) shape(rectPts(x, y + 8, w, h, o.r != null ? o.r : 28), {fill: 'shadow', line: false, alpha: 1});
      shape(rectPts(x, y, w, h, o.r != null ? o.r : 28), {fill: o.fill || 'card', stroke: o.stroke || (look.name === 'clean' ? 'line' : null), lw: o.lw || 2, id: o.id});
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
      shape(rectPts(x, y, w, h, look.name === 'pixel' ? 0 : 10), {fill: o.fill || 'tag', line: false});
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
    k.snow = function (x, y, o = {}) {
      const s = o.scale || 1, face = o.face || 1, pose = o.pose || 'stand';
      const bob = Math.sin(T * 2.4) * 3;
      const talk = o.talk != null ? o.talk : k.talking();
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
      const front = limb(shR, armR[0], armR[1], 82, 76, face);
      const drawArm = (sh, l, id) => { shape(capsule(sh, l.el, 19), {fill: 'jacket', id}); shape(capsule(l.el, l.ha, 16), {fill: 'jacket', id: id + 1}); shape(ellPts(l.ha[0], l.ha[1], 15, 15), {fill: 'skin', id: id + 2}); };
      drawArm(shL, back, 9010);
      // torso: the work jacket
      shape(rectPts(-66, -318 + bob, 132, 172, 30), {fill: 'jacket', id: 9020});
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
      const hx0 = 4 * face, hy0 = -384 + bob;
      shape(ellPts(hx0, hy0, 60, 64), {fill: 'skin', id: 9040});
      shape(ellPts(hx0 + 52 * face, hy0 + 6, 9, 14), {fill: 'skinShade', id: 9041, line: false});
      // knit cap with a fold and a pom
      shape(ellPts(hx0, hy0 - 18, 64, 56, 24, Math.PI, TAU).concat([[hx0 + 64, hy0 - 12], [hx0 - 64, hy0 - 12]]), {fill: 'cap', id: 9042});
      shape(rectPts(hx0 - 66, hy0 - 30, 132, 26, 10), {fill: 'accent2', id: 9043});
      shape(ellPts(hx0, hy0 - 82, 16, 16), {fill: 'accent2', id: 9044});
      // face: eyes blink about every 3.7 s, mouth moves with the voice
      const blink = (T % 3.7) < 0.12;
      const ex = hx0 + 14 * face;
      [ex - 20, ex + 20].forEach((x0, i) => blink ? shape([[x0 - 7, hy0 + 12], [x0 + 7, hy0 + 12]], {stroke: 'ink', lw: 4, closed: false, line: false})
        : shape(ellPts(x0, hy0 + 12, 6.5, 8), {fill: look.lineArt ? 'ink' : 'shoe', line: false, id: 9050 + i}));
      const mo = talk ? 3 + Math.abs(Math.sin(T * 17) * Math.sin(T * 7.3)) * 13 : 2.5;
      shape(ellPts(ex, hy0 + 40, talk ? 13 : 15, mo), {fill: talk ? 'ink' : null, stroke: talk ? null : 'ink', lw: 3.5, line: false, closed: !(!talk), id: 9060});
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
      shape(rectPts(x, y, w, h, 56), {fill: look.lineArt ? 'bg2' : 'ink', line: true, id: 9300});
      shape(rectPts(x + 16, y + 16, w - 32, h - 32, 44), {fill: 'card', id: 9301});
      shape(rectPts(x + w / 2 - 60, y + 26, 120, 26, 13), {fill: 'ink', line: false});
      text(o.who || 'Customer', x + w / 2, y + 70, {size: 30, weight: 700, font: 'body', color: 'ink', align: 'center'});
      let yy = y + 130;
      msgs.forEach((m, i) => {
        const t0 = m.at != null ? m.at : -1; if (T < t0) return;
        const pp = easeOut((T - t0) / 0.3);
        const maxW = w - 140; const r = wrap(m.text, {size: 32, weight: 600, font: 'body'}, maxW - 40);
        const bw = Math.min(maxW, Math.max(...r.map((ln) => measure(ln, {size: 32, weight: 600, font: 'body'}))) + 44), bh = r.length * 42 + 30;
        const bx = m.me ? x + w - 36 - bw : x + 36;
        ctx.save(); ctx.globalAlpha *= pp; ctx.translate(0, (1 - pp) * 20);
        shape(rectPts(bx, yy, bw, bh, 26), {fill: m.me ? 'teal' : 'bg2', line: false, id: 9310 + i});
        text(m.text, bx + 22, yy + 15, {size: 32, weight: 600, font: 'body', color: m.me ? 'pillText' : 'ink', maxW: maxW - 40, lh: 1.3});
        if (m.stamp) text(m.stamp, m.me ? bx + bw : bx, yy + bh + 6, {size: 22, weight: 600, font: 'body', color: 'muted', align: m.me ? 'right' : 'left'});
        ctx.restore();
        yy += bh + (m.stamp ? 40 : 18);
      });
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

    k.cam = function (sc, cx, cy) { ctx.translate(cx, cy); ctx.scale(sc, sc); ctx.translate(-cx, -cy); };
    return k;
  }
  window.Kit = {make};
})();
