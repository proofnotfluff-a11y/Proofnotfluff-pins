/* Trial motion kit, Nov 13, 2026. Every value is worked out from the time alone, so any frame draws the same on its own. */
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const W = 1080, H = 1920;
const C = {bg0: '#0B0E15', bg1: '#161C29', cream: '#F6F1E7', paper: '#FBF8F1', ink: '#151922', mute: '#8B94A8', soft: '#C9CFDB', line: '#E4DDCE',
  orange: '#F26A3D', gold: '#F8C96F', teal: '#3CBBA8', red: '#E5484D', navy: '#1D2434', glass: '#232C3F', glass2: '#2E3950'};
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, p) => a + (b - a) * p;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const E = {
  out3: (p) => 1 - Math.pow(1 - clamp(p), 3),
  in3: (p) => Math.pow(clamp(p), 3),
  io3: (p) => { p = clamp(p); return p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2; },
  outExpo: (p) => { p = clamp(p); return p >= 1 ? 1 : 1 - Math.pow(2, -10 * p); },
  back: (p, s = 1.7) => { p = clamp(p); return 1 + (s + 1) * Math.pow(p - 1, 3) + s * Math.pow(p - 1, 2); },
  /* a spring that overshoots and settles: 0 at p=0, 1 at rest */
  spring: (p, damp = 5.5, freq = 9) => { p = clamp(p); return p >= 1 ? 1 : 1 - Math.exp(-damp * p) * Math.cos(freq * p); },
};
const hash = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const mixc = (a, b, p) => { const h = (s) => [1, 3, 5].map((i) => parseInt(s.slice(i, i + 2), 16)); const A = h(a), B = h(b); return `rgb(${A.map((v, i) => Math.round(lerp(v, B[i], clamp(p)))).join(',')})`; };
const rgba = (hex, a) => { const n = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)); return `rgba(${n[0]},${n[1]},${n[2]},${a})`; };

function rr(x, y, w, h, r) { r = Math.max(0, Math.min(r, w / 2, h / 2)); ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
function card(x, y, w, h, r, fill, o = {}) {
  ctx.save();
  if (o.shadow !== 0) { ctx.shadowColor = `rgba(0,0,0,${o.shadow || .45})`; ctx.shadowBlur = o.blur || 50; ctx.shadowOffsetY = o.dy === undefined ? 22 : o.dy; }
  ctx.fillStyle = fill; rr(x, y, w, h, r); ctx.fill(); ctx.restore();
  if (o.stroke) { ctx.save(); ctx.strokeStyle = o.stroke; ctx.lineWidth = o.lw || 3; rr(x, y, w, h, r); ctx.stroke(); ctx.restore(); }
}
function font(size, weight = 700, fam = 'Poppins') { ctx.font = `${weight} ${size}px ${fam}, Inter, sans-serif`; }
function text(s, x, y, o = {}) {
  font(o.size || 40, o.weight || 700, o.fam || 'Poppins');
  ctx.textAlign = o.align || 'left'; ctx.textBaseline = o.base || 'alphabetic'; ctx.fillStyle = o.color || C.cream;
  if (o.ls) { try { ctx.letterSpacing = o.ls + 'px'; } catch (e) {} }
  ctx.fillText(s, x, y);
  if (o.ls) { try { ctx.letterSpacing = '0px'; } catch (e) {} }
}
function tw(s, size, weight = 700, fam = 'Poppins') { font(size, weight, fam); return ctx.measureText(s).width; }
const money = (v, cents = true) => '$' + (cents ? v.toFixed(2) : Math.round(v).toString()).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
/* draw fn under a transform about a point */
function at(x, y, sx, sy, rot, alpha, fn) { ctx.save(); ctx.translate(x, y); if (rot) ctx.rotate(rot); ctx.scale(sx, sy === undefined ? sx : sy); if (alpha !== undefined && alpha < 1) ctx.globalAlpha *= clamp(alpha); fn(); ctx.restore(); }

/* ---- the room: deep ink, a slow dot field with depth, two soft lights whose color follows the story ---- */
function room(t, tint) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, C.bg1); g.addColorStop(1, C.bg0); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const blob = (x, y, r, col, a) => { const q = ctx.createRadialGradient(x, y, 0, x, y, r); q.addColorStop(0, rgba(col, a)); q.addColorStop(1, rgba(col, 0)); ctx.fillStyle = q; ctx.fillRect(x - r, y - r, r * 2, r * 2); };
  blob(240 + 90 * Math.sin(t * .23), 520 + 70 * Math.cos(t * .19), 760, tint[0], .20);
  blob(860 + 80 * Math.cos(t * .21), 1180 + 90 * Math.sin(t * .17), 820, tint[1], .16);
  for (let layer = 0; layer < 2; layer++) {
    const gap = layer ? 54 : 96, sp = layer ? 9 : 18, a = layer ? .05 : .09, sz = layer ? 2 : 3;
    const oy = (t * sp) % gap; ctx.fillStyle = `rgba(255,255,255,${a})`;
    for (let y = -gap + oy; y < H + gap; y += gap) for (let x = (layer ? 27 : 48); x < W; x += gap) ctx.fillRect(x, y, sz, sz);
  }
  const v = ctx.createRadialGradient(W / 2, H * .46, 500, W / 2, H * .46, 1250); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,.55)'); ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
}

/* ---- captions: the one channel for words. Words land as they would be spoken; the newest is lit. ---- */
function captions(t, lines) {
  const L = lines.find((l) => t >= l.a && t < l.b); if (!L) return;
  const words = L.text.split(' '), n = words.length, step = Math.min(.24, (L.b - L.a - .45) / n);
  const size = L.size || 84, maxW = 800; font(size, 800);
  const sp = size * .31, ms = words.map((w, i) => ({w, ww: ctx.measureText(w).width, i}));
  const wid = (xs) => xs.reduce((s, q) => s + q.ww, 0) + sp * Math.max(0, xs.length - 1);
  let rows = [ms];
  if (wid(ms) > maxW) { let best = 1, bw = 1e9; for (let k = 1; k < n; k++) { const m = Math.max(wid(ms.slice(0, k)), wid(ms.slice(k))); if (m < bw) { bw = m; best = k; } } rows = [ms.slice(0, best), ms.slice(best)]; }
  const lh = size * 1.12, y0 = 1312 - (rows.length - 1) * lh / 2, out = E.in3(seg(t, L.b - .12, L.b));
  rows.forEach((row, r) => {
    const total = row.reduce((s, q) => s + q.ww, 0) + sp * (row.length - 1); let x = W / 2 - total / 2;
    row.forEach((q) => {
      const ts = L.a + q.i * step, p = seg(t, ts, ts + .16); if (p > 0) {
        const s = lerp(.82, 1, E.back(p, 1.3)), lit = t < ts + step + .05 || (L.hot && L.hot.includes(q.i));
        ctx.save(); ctx.globalAlpha = clamp(p * 2) * (1 - out); ctx.translate(x + q.ww / 2, y0 + r * lh - out * 30); ctx.scale(s, s);
        font(size, 800); ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
        ctx.shadowColor = 'rgba(0,0,0,.75)'; ctx.shadowBlur = 26; ctx.shadowOffsetY = 8; ctx.lineJoin = 'round';
        ctx.strokeStyle = 'rgba(8,10,16,.9)'; ctx.lineWidth = 14; ctx.strokeText(q.w, 0, 0); ctx.shadowColor = 'transparent';
        ctx.fillStyle = lit ? (L.color || C.gold) : C.cream; ctx.fillText(q.w, 0, 0); ctx.restore();
      }
      x += q.ww + sp;
    });
  });
}

/* ---- things ---- */
function sparkle(cx, cy, r, color, rot = 0) {   /* a four point star: a plain mark for "an AI", nobody's logo */
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot); ctx.fillStyle = color; ctx.beginPath();
  for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4, q = i % 2 ? r * .34 : r; ctx.lineTo(Math.cos(a) * q, Math.sin(a) * q); }
  ctx.closePath(); ctx.fill(); ctx.restore();
}
function bank(cx, cy, s, alpha = 1) {
  at(cx, cy, s, s, 0, alpha, () => {
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.5)'; ctx.shadowBlur = 60; ctx.shadowOffsetY = 26;
    ctx.fillStyle = C.cream; ctx.beginPath(); ctx.moveTo(-250, -92); ctx.lineTo(0, -214); ctx.lineTo(250, -92); ctx.closePath(); ctx.fill();
    ctx.fillRect(-236, -92, 472, 44); ctx.fillRect(-250, 122, 500, 30); ctx.fillRect(-272, 152, 544, 32); ctx.restore();
    ctx.fillStyle = '#E9E1D0'; ctx.fillRect(-236, -48, 472, 170);
    for (let i = 0; i < 4; i++) { const x = -198 + i * 118; ctx.fillStyle = C.cream; ctx.fillRect(x, -48, 42, 170); ctx.fillStyle = 'rgba(0,0,0,.08)'; ctx.fillRect(x + 30, -48, 12, 170); ctx.fillStyle = C.cream; ctx.fillRect(x - 8, -48, 58, 12); ctx.fillRect(x - 8, 110, 58, 12); }
    ctx.fillStyle = C.ink; ctx.beginPath(); ctx.arc(0, -150, 22, 0, 7); ctx.fill(); ctx.fillStyle = C.gold; ctx.beginPath(); ctx.arc(0, -150, 13, 0, 7); ctx.fill();
    text('BANK', 0, -56, {size: 34, weight: 800, color: C.ink, align: 'center', ls: 10});
    ctx.fillStyle = C.ink; rr(-70, 160, 140, 16, 8); ctx.fill();   /* the slot things come out of */
  });
}
function plug(x, y, s = 1) {   /* prongs point down */
  at(x, y, s, s, 0, 1, () => {
    ctx.fillStyle = '#D8D2C4'; rr(-24, 50, 14, 44, 5); ctx.fill(); rr(10, 50, 14, 44, 5); ctx.fill();
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.5)'; ctx.shadowBlur = 24; ctx.shadowOffsetY = 10; ctx.fillStyle = C.cream; rr(-46, -40, 92, 96, 22); ctx.fill(); ctx.restore();
    ctx.fillStyle = C.orange; rr(-22, -64, 44, 34, 10); ctx.fill(); ctx.fillStyle = 'rgba(0,0,0,.1)'; rr(-46, 30, 92, 26, 12); ctx.fill();
  });
}
function cable(x0, y0, x1, y1, wob = 0) {
  const d = y1 - y0; ctx.save(); ctx.lineCap = 'round';
  const path = () => { ctx.beginPath(); ctx.moveTo(x0, y0); ctx.bezierCurveTo(x0 + wob * 1.2, y0 + d * .45, x1 - wob, y1 - d * .45, x1, y1); };
  ctx.shadowColor = 'rgba(0,0,0,.5)'; ctx.shadowBlur = 20; ctx.shadowOffsetY = 8; ctx.strokeStyle = C.orange; ctx.lineWidth = 22; path(); ctx.stroke();
  ctx.shadowColor = 'transparent'; ctx.strokeStyle = 'rgba(255,255,255,.28)'; ctx.lineWidth = 5; ctx.translate(-5, 0); path(); ctx.stroke(); ctx.restore();
}
function fileIcon(x, y, s) {
  at(x, y, s, s, 0, 1, () => {
    ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.moveTo(-30, -40); ctx.lineTo(12, -40); ctx.lineTo(30, -22); ctx.lineTo(30, 40); ctx.lineTo(-30, 40); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = C.line; ctx.lineWidth = 3; ctx.stroke(); ctx.fillStyle = C.line; ctx.beginPath(); ctx.moveTo(12, -40); ctx.lineTo(12, -22); ctx.lineTo(30, -22); ctx.closePath(); ctx.fill();
    ctx.fillStyle = C.teal; rr(-36, 2, 56, 26, 6); ctx.fill(); text('CSV', -8, 22, {size: 17, weight: 800, fam: 'Inter', color: '#fff', align: 'center'});
  });
}
function fileChip(cx, cy, s, alpha = 1) {
  at(cx, cy, s, s, 0, alpha, () => {
    card(-270, -66, 540, 132, 34, C.cream); fileIcon(-204, 0, 1.05);
    text('statement.csv', -150, -4, {size: 42, weight: 700, fam: 'Inter', color: C.ink});
    text('159 rows  ·  3 months', -150, 38, {size: 28, weight: 500, fam: 'Inter', color: '#6A7285'});
  });
}
function ring(cx, cy, r, color, a, lw = 6) { if (a <= 0 || r <= 0) return; ctx.save(); ctx.strokeStyle = rgba(color, clamp(a)); ctx.lineWidth = lw; ctx.beginPath(); ctx.arc(cx, cy, r, 0, 7); ctx.stroke(); ctx.restore(); }
function badge(cx, cy, label, bg, s = 1, o = {}) {
  at(cx, cy, s, s, o.rot || 0, o.alpha, () => { const size = o.size || 52, w = tw(label, size, 800) + 56; card(-w / 2, -size * .8, w, size * 1.6, size * .8, bg, {blur: 30, dy: 12}); text(label, 0, size * .36, {size, weight: 800, color: o.color || '#fff', align: 'center'}); });
}
/* a number that rolls like a counter: each digit column slides to its value */
function roll(value, cx, y, size, color, cents = true) {
  const s = money(value, cents); font(size, 800); const adv = [...s].map((ch) => ctx.measureText(ch).width); const total = adv.reduce((a, b) => a + b, 0);
  let x = cx - total / 2; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = color;
  [...s].forEach((ch, i) => { ctx.fillText(ch, x, y); x += adv[i]; });
  return total;
}

/* a fine film grain, so flat areas are never dead: one small tile, moved each frame */
const GRAIN = (() => { const g = document.createElement('canvas'); g.width = g.height = 256; const x = g.getContext('2d'), d = x.createImageData(256, 256); for (let i = 0; i < 65536; i++) { const v = Math.floor(hash(i * 1.37) * 255); d.data[i * 4] = d.data[i * 4 + 1] = d.data[i * 4 + 2] = v; d.data[i * 4 + 3] = 255; } x.putImageData(d, 0, 0); return g; })();
function grain(t) { const f = Math.floor(t * 30), ox = Math.floor(hash(f) * 256), oy = Math.floor(hash(f + 77) * 256); ctx.save(); ctx.globalAlpha = .05; ctx.globalCompositeOperation = 'overlay'; for (let y = -oy; y < H; y += 256) for (let x = -ox; x < W; x += 256) ctx.drawImage(GRAIN, x, y); ctx.restore(); }
