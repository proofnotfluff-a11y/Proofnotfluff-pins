/* Trial video r2, Nov 13, 2026: result first. The yearly number on screen, an AI that read one sample statement, no bank link.
   27.5 s, 1080 x 1920, no presenter. Every number comes from DATA: the sample statement and the one-question run's answer. */
const BAR = 60 / 122 * 4, B = (n) => n * BAR;                 /* the music's bar: cuts land on it */
const T = {plug: B(1), file: B(2), ask: B(3), scan: B(4), stack: B(5), month: B(6), year: 12.82, twice: B(7), price: B(8), deliv: B(9), katch: B(10), cut: 21.42, end: B(12), stop: B(14)};
const ROWS = DATA.rows, MON = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const dshort = (d) => MON[+d.slice(5, 7)] + ' ' + d.slice(8, 10);
const amt = (v) => (v < 0 ? '-' : '+') + money(Math.abs(v));
const fit = (s, n) => { if (s.length <= n) return s; const c = s.slice(0, n + 1), k = c.lastIndexOf(' '); return (k > 3 ? c.slice(0, k) : s.slice(0, n)).replace(/ (AND|THANK)$/, ''); };   /* never a word cut in half */
const Q = DATA.run.question, QALL = Q.join(' ');
const SHORT = {'MEALCRATE WEEKLY BOX': 'MEALCRATE BOX'};
const SUBS = Object.entries(DATA.subs).map(([n, a]) => ({n: SHORT[n] || n, a})).sort((p, q) => p.a - q.a);
const MONTHLY = DATA.monthly, YEARLY = DATA.yearly, DEL = DATA.delivery, DELN = DATA.orders, SECS = Math.round(DATA.run.seconds_to_answer);
const YR = money(Math.round(YEARLY), false);                   /* $2,015: the caption's rounded figure */

const CAPS = [
  {a: -0.6, b: T.plug - .04, text: 'An AI read one sample statement.', hot: [4]},
  {a: T.plug, b: T.file - .04, text: 'With no bank link.', color: C.teal, hot: [1, 2, 3]},
  {a: T.file, b: T.ask - .05, text: 'Download your statement as a CSV.', hot: [5]},
  {a: T.ask, b: T.scan - .05, text: 'Ask Claude one question.', hot: [1]},
  {a: T.scan, b: 8.84, text: '159 transactions.', hot: [0]},
  {a: 8.88, b: T.stack - .04, text: 'Under a minute.'},
  {a: T.stack + .06, b: T.year + .26, text: SUBS.length + ' subscriptions.', hot: [0]},
  {a: T.year + .3, b: T.twice - .04, text: "That's " + YR + ' a year.', hot: [1]},
  {a: T.twice, b: T.price - .04, text: 'It also flagged a double charge.', color: C.red, hot: [4, 5]},
  {a: T.price, b: T.deliv - .04, text: 'A price that tripled.', hot: [3]},
  {a: T.deliv, b: T.katch - .04, text: 'Delivery orders doubled.', hot: [2]},
  {a: T.katch, b: T.cut - .04, text: 'The catch: the AI still sees the file.'},
  {a: T.cut, b: T.end - .04, text: 'So cut any rows you want kept private.', color: C.teal, hot: [1]},
  {a: T.end, b: 24.9, text: 'Try it.'},
  {a: 24.96, b: 99, text: 'Link your bank, or just upload a file?', hot: [1, 6]},
];
window.SFX = [[0, 'sting', .9], [.1, 'chime', .6], [T.plug - .05, 'whoosh', .7], [2.56, 'whoosh_1', .9], [2.66, 'stamp', .9], [T.file, 'tick', .5], [4.1, 'tick', .5], [4.25, 'tick', .5], [4.4, 'tick', .5], [4.62, 'pop', .7], [5.12, 'whoosh_2', .6], [5.6, 'blip', .9],
  [7.5, 'pop', .8], [7.6, 'whoosh', .6], [T.scan, 'blip', .5], [T.stack - .08, 'whoosh_1', .6], ...SUBS.map((s, i) => [9.9 + i * .17 + .3, 'blip_' + (i % 4), .55]), [T.month, 'chime', .9], [12.5, 'whoosh_2', .7], [T.year + .1, 'chime_1', .9],
  [T.twice - .08, 'whoosh', .6], [13.98, 'pop', .6], [14.62, 'stamp', 1], [T.price - .08, 'whoosh_1', .5], [16.0, 'tick', .6], [16.42, 'pop', .9], [16.82, 'blip', .6],
  [T.deliv - .08, 'whoosh_2', .5], [17.8, 'tick', .6], [18.2, 'tick', .7], [18.6, 'tick', .8], [19.0, 'pop', .9], [T.katch - .08, 'whoosh', .5], [20.3, 'blip', .8], [T.cut, 'pop', .6], [21.95, 'whoosh_1', .7], [22.3, 'whoosh_2', .7], [22.62, 'tick', .8], [22.97, 'tick', .8],
  [T.end - .08, 'whoosh', .6], [T.end + .1, 'chime_2', .9]];
const TINTS = [[0, '#B8862B', '#8F5A1C'], [T.plug, '#27509A', '#8F3A1C'], [T.file, '#1F6A86', '#2B6E63'], [T.stack, '#A8781F', '#2B6E63'],
  [T.twice, '#8F2733', '#6B2A55'], [T.deliv, '#8F3A1C', '#7A2A3A'], [T.katch, '#35409A', '#1F6A86'], [T.end, '#2B6E63', '#A8781F']];
function tintAt(t) {
  let i = 0; TINTS.forEach((k, j) => { if (t >= k[0]) i = j; });
  const cur = TINTS[i], prev = TINTS[Math.max(0, i - 1)], p = E.io3(seg(t, cur[0], cur[0] + .35));
  const mh = (a, b) => '#' + [1, 3, 5].map((q) => Math.round(lerp(parseInt(a.slice(q, q + 2), 16), parseInt(b.slice(q, q + 2), 16), p)).toString(16).padStart(2, '0')).join('');
  return [mh(prev[1], cur[1]), mh(prev[2], cur[2])];
}
function sampleTag(t) {   /* always in sight while sample numbers are on screen */
  const hide = seg(t, 7.5, 7.7) * (1 - seg(t, T.stack - .1, T.stack + .1)), a = (1 - hide) * (1 - seg(t, T.end - .1, T.end));
  if (a <= 0) return; ctx.save(); ctx.globalAlpha = a; const w = tw('SAMPLE STATEMENT', 25, 800, 'Inter') + 16 * 1.5 + 36;
  ctx.fillStyle = 'rgba(11,14,21,.82)'; rr(64, 276, w, 56, 28); ctx.fill(); ctx.strokeStyle = rgba(C.gold, .9); ctx.lineWidth = 3; rr(64, 276, w, 56, 28); ctx.stroke();
  text('SAMPLE STATEMENT', 64 + w / 2, 313, {size: 25, weight: 800, fam: 'Inter', color: C.gold, align: 'center', ls: 1.5}); ctx.restore();
}
function chipRow(s, w) {
  card(-w / 2, -29, w, 58, 19, C.cream, {blur: 18, dy: 8, shadow: .35});
  ctx.fillStyle = C.orange; ctx.beginPath(); ctx.arc(-w / 2 + 32, 0, 8, 0, 7); ctx.fill();
  text(s.n, -w / 2 + 56, 11, {size: 31, weight: 700, fam: 'Inter', color: C.ink}); text(money(s.a), w / 2 - 26, 13, {size: 37, weight: 800, color: C.ink, align: 'right'});
}

/* ------------------------------------------------------------------ 0 to 2 s: the result, first */
function open(t) {
  if (t >= T.plug) return;
  SUBS.filter((s, i) => i % 2 === 0).forEach((s, i) => {   /* a few of the charges fall past, behind the number */
    const sp = 300 + hash(i + 2) * 240, y = ((-200 + (t + 1.2 + hash(i) * 4) * sp) % 1300) + 150, x = 150 + ((i * 397) % 780), sc = .62 + hash(i + 5) * .34;
    at(x, y, sc, sc, (hash(i + 8) - .5) * .3, (.7 + sc * .3) * (1 - seg(y, 1040, 1160)) * seg(y, 230, 330), () => chipRow(s, 520));
  });
  ctx.save(); ctx.translate(540, 716); ctx.scale(1, .3); const sh = ctx.createRadialGradient(0, 0, 200, 0, 0, 620); sh.addColorStop(0, 'rgba(11,14,21,.97)'); sh.addColorStop(.7, 'rgba(11,14,21,.9)'); sh.addColorStop(1, 'rgba(11,14,21,0)'); ctx.fillStyle = sh; ctx.fillRect(-700, -700, 1400, 1400); ctx.restore();
  ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, 1150); ctx.clip(); ring(540, 690, 470 + 520 * E.out3(t / 1.0), C.gold, .9 * (1 - seg(t, 0, 1.0)), 10); ring(540, 690, 440 + 420 * E.out3((t - .15) / 1.0), C.orange, .7 * (1 - seg(t, .15, 1.15)) * seg(t, .15, .2), 6); ctx.restore();
  const s = lerp(1.22, 1, E.spring(seg(t + .25, 0, .8), 5, 9)) + .02 * Math.sin(t * 5);
  at(540, 712, s, s, 0, 1, () => {
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.6)'; ctx.shadowBlur = 44; ctx.shadowOffsetY = 14; roll(YEARLY, 0, 0, 176, C.gold, true); ctx.restore();
    text('a year in subscriptions', 0, 96, {size: 56, weight: 700, align: 'center'});
  });
}

/* ------------------------------------------------------------------ 2 to 7.9 s: no bank link; a file; one question */
function aiBox(t) {
  if (t < T.plug) return;
  const m1 = E.spring(seg(t, T.file - .05, T.file + .6), 5, 8), m2 = E.io3(seg(t, 7.58, T.scan));
  const sq = {x: 395, y: 872, w: 290, h: 290, r: 62}, box = {x: 80, y: 880, w: 870, h: 290, r: 46}, pill = {x: 80, y: 330, w: 870, h: 122, r: 40};
  const L = (k) => lerp(lerp(sq[k], box[k], m1), pill[k], m2);
  const gulp = E.spring(seg(t, 5.6, 6.1), 6, 14), sy = t >= 5.6 && t < 6.1 ? lerp(.92, 1, gulp) : 1;
  const r = {x: L('x'), y: L('y'), w: L('w'), h: L('h') * sy, r: L('r')};
  const out = 1 - seg(t, T.stack - .1, T.stack); if (out <= 0) return;
  ctx.save(); ctx.globalAlpha = out;
  const live = (1 - seg(t, 2.56, 2.66)) * (t < T.file ? 1 : 0);
  if (live > 0) { const q = ctx.createRadialGradient(540, 880, 0, 540, 880, 280); q.addColorStop(0, rgba(C.gold, .38 * live * (.7 + .3 * Math.sin(t * 40)))); q.addColorStop(1, rgba(C.gold, 0)); ctx.fillStyle = q; ctx.fillRect(260, 600, 560, 560); }
  card(r.x, r.y, r.w, r.h, r.r, C.glass, {stroke: 'rgba(255,255,255,.14)', lw: 3});
  const gl = ctx.createLinearGradient(0, r.y, 0, r.y + r.h); gl.addColorStop(0, 'rgba(255,255,255,.07)'); gl.addColorStop(.5, 'rgba(255,255,255,0)'); ctx.fillStyle = gl; rr(r.x, r.y, r.w, r.h, r.r); ctx.fill();
  if (m1 < .98) {
    ctx.save(); ctx.globalAlpha = out * (1 - seg(m1, .1, .6));
    ctx.fillStyle = '#0A0D14'; rr(540 - 62, r.y - 12, 124, 40, 14); ctx.fill();
    ctx.fillStyle = rgba(C.gold, .3 + .7 * live); rr(540 - 26, r.y - 2, 16, 20, 5); ctx.fill(); rr(540 + 10, r.y - 2, 16, 20, 5); ctx.fill();
    sparkle(540, r.y + 122, 56 + 4 * Math.sin(t * 3), C.gold, Math.sin(t * .8) * .12); text('AI', 540, r.y + 244, {size: 58, weight: 800, align: 'center', ls: 6});
    ctx.restore();
  }
  if (m1 > .3 && m2 < 1) {
    ctx.save(); ctx.globalAlpha = out * seg(m1, .4, .9) * (1 - seg(m2, 0, .5));
    const n = Math.floor(clamp((t - T.ask - .05) * 36, 0, QALL.length + 1)), l1 = Q[0].slice(0, n), l2 = n > Q[0].length ? Q[1].slice(0, n - Q[0].length - 1) : '';
    sparkle(r.x + 66, r.y + r.h - 126, 26, C.gold, t * .5);
    if (t < T.ask + .05) text('Ask anything', r.x + 112, r.y + r.h - 112, {size: 40, weight: 500, fam: 'Inter', color: C.mute});
    else { text(l1, r.x + 112, r.y + r.h - 112, {size: 40, weight: 600, fam: 'Inter'}); text(l2, r.x + 112, r.y + r.h - 58, {size: 40, weight: 600, fam: 'Inter'});
      if (n <= QALL.length || Math.floor(t * 3) % 2 === 0) { ctx.fillStyle = C.gold; const two = n > Q[0].length; ctx.fillRect(r.x + 116 + tw(two ? l2 : l1, 40, 600, 'Inter'), r.y + r.h - (two ? 94 : 148), 4, 46); } }
    const press = t >= 7.5 ? lerp(.8, 1, E.spring(seg(t, 7.5, 7.85), 6, 16)) : 1, ready = seg(t, 7.3, 7.45);
    at(r.x + r.w - 70, r.y + r.h - 66, press, press, 0, 1, () => { ctx.fillStyle = mixc('#3A455C', C.orange, ready); ctx.beginPath(); ctx.arc(0, 0, 42, 0, 7); ctx.fill(); ctx.strokeStyle = '#fff'; ctx.lineWidth = 7; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.beginPath(); ctx.moveTo(0, 16); ctx.lineTo(0, -16); ctx.moveTo(-14, -3); ctx.lineTo(0, -17); ctx.lineTo(14, -3); ctx.stroke(); });
    ctx.restore();
  }
  if (m2 > .5) { ctx.save(); ctx.globalAlpha = out * seg(m2, .5, 1); fileIcon(r.x + 64, r.y + r.h / 2, .7); text(Q[0], r.x + 116, r.y + r.h / 2 - 6, {size: 36, weight: 600, fam: 'Inter'}); text(Q[1], r.x + 116, r.y + r.h / 2 + 40, {size: 36, weight: 600, fam: 'Inter'}); ctx.restore(); }
  if (t >= 5.6 && t < 6.2) ring(r.x + 240, r.y + 70, 60 + 340 * E.out3(seg(t, 5.6, 6.2)), C.teal, .8 * (1 - seg(t, 5.6, 6.2)), 8);
  ctx.restore();
}
function sheetRows(x, y, w, n, i0, size, o = {}) {
  for (let i = 0; i < n; i++) { const r = ROWS[i0 + i]; if (!r) break; const yy = y + i * (o.lh || size * 1.9);
    text(dshort(r[0]), x, yy, {size, weight: 500, fam: 'Inter', color: '#7C8496'}); text(fit(r[1], o.cut || 26), x + size * 3.9, yy, {size, weight: 600, fam: 'Inter', color: C.ink});
    text(amt(r[2]), x + w, yy, {size, weight: 600, fam: 'Inter', color: r[2] > 0 ? '#1F8A6D' : C.ink, align: 'right'}); }
}
function intro(t) {
  if (t < T.plug || t > T.ask) return;
  const up = E.io3(seg(t, T.file - .1, T.file + .4)), exit = E.in3(seg(t, 4.62, 4.86));
  const bs = lerp(.9, .8, up), by = lerp(458, 436, up) - exit * 70, slot = by + 168 * bs;
  /* plugged in and live; then pulled out, and the socket is crossed off */
  const yk = E.outExpo(seg(t, 2.56, 2.9)), hum = t < 2.56 ? Math.sin(t * 70) * 1.6 : 0;
  const py = lerp(778, slot - 70, yk) + hum, wob = t >= 2.56 ? 80 * Math.exp(-5 * (t - 2.56)) * Math.sin(22 * (t - 2.56)) : 10 * Math.sin(t * 6);
  if (yk < 1) { ctx.save(); ctx.globalAlpha = 1 - seg(yk, .7, 1); cable(540, slot - 10, 540, py - 54, wob); plug(540, py, 1); ctx.restore(); }
  if (t < 2.56) for (let i = 0; i < 6; i++) { const f = Math.floor(t * 30), a = hash(f * 7 + i) * Math.PI * 2, d = 20 + hash(f + i * 3) * 50, x = 540 + (i % 2 ? 40 : -40), y = 870;
    ctx.strokeStyle = rgba(C.gold, .9); ctx.lineWidth = 4; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + Math.cos(a) * d, y - Math.abs(Math.sin(a)) * d * .7); ctx.stroke(); }
  /* the statement prints out of the bank */
  const pp = seg(t, T.file + .02, 4.5), feed = (Math.floor(pp * 4) + E.out3((pp * 4) % 1)) / 4, ph = 330, pw = 400, fold = E.io3(seg(t, 4.5, 4.8));
  if (t >= T.file && fold < 1) {
    const top = slot + 6 - ph + ph * Math.min(1, feed);
    ctx.save(); ctx.beginPath(); ctx.rect(0, slot + 6, W, H); ctx.clip();
    at(540, top + ph / 2, lerp(1, 1.3, fold), lerp(1, .4, fold), 0, 1 - seg(fold, .2, .6), () => {
      card(-pw / 2, -ph / 2, pw, ph, 14, C.paper, {blur: 40, dy: 18}); text('Statement', -pw / 2 + 28, -ph / 2 + 52, {size: 32, weight: 800, color: C.ink});
      ctx.fillStyle = C.line; ctx.fillRect(-pw / 2 + 28, -ph / 2 + 70, pw - 56, 3); sheetRows(-pw / 2 + 28, -ph / 2 + 108, pw - 56, 7, 3, 18, {lh: 34, cut: 17});
    });
    ctx.restore();
  }
  bank(540, by, bs, 1 - exit);
  if (fold > .3 && t < 5.6) {
    const lift = E.io3(seg(t, 5.0, 5.14)), fall = E.in3(seg(t, 5.14, 5.6));
    const x = lerp(540, 330, fall), y = lerp(lerp(730, 690, lift), 946, fall), s = lerp(lerp(.4, 1.12, E.spring(seg(t, 4.55, 5.05), 5, 10)), .74, fall);
    fileChip(x, y, s, seg(fold, .3, .8));
  }
}
function noLink(t) {   /* the socket is crossed off, in front of the box */
  const hit = t - 2.66; if (hit < 0 || t >= T.file + .25) return; const fade = 1 - seg(t, T.file, T.file + .25);
  at(540, 846, lerp(2.4, 1, E.out3(hit / .16)), undefined, 0, clamp(hit * 12) * fade, () => { ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.5)'; ctx.shadowBlur = 24; ctx.shadowOffsetY = 8; ctx.fillStyle = C.red; ctx.beginPath(); ctx.arc(0, 0, 58, 0, 7); ctx.fill(); ctx.restore(); ctx.strokeStyle = '#fff'; ctx.lineWidth = 13; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-22, -22); ctx.lineTo(22, 22); ctx.moveTo(22, -22); ctx.lineTo(-22, 22); ctx.stroke(); });
  ring(540, 846, 80 + 300 * E.out3(hit / .5), C.red, .8 * (1 - seg(hit, 0, .5)) * fade, 8);
}
function attachment(t) { if (t >= 5.6 && t < 7.7) fileChip(330, 946, .74, 1 - seg(t, 7.55, 7.7)); }

/* ------------------------------------------------------------------ 7.9 to 9.8 s: 159 real rows go by */
const RH = 60, VIEW = {x: 70, y: 552, w: 880, h: 610, head: 78};
const scrollAt = (t) => (ROWS.length * RH - (VIEW.h - VIEW.head) + 20) * E.io3(seg(t, T.scan + .1, T.stack - .1));
function ledger(t) {
  if (t < 7.6 || t > T.stack) return;
  const inn = E.spring(seg(t, 7.62, 8.2), 5.5, 8);
  at(VIEW.x + VIEW.w / 2, VIEW.y + VIEW.h / 2 + (1 - inn) * 520, 1, 1, 0, clamp(inn * 3), () => {
    const x = -VIEW.w / 2, y = -VIEW.h / 2; card(x, y, VIEW.w, VIEW.h, 30, C.paper);
    ctx.save(); rr(x, y, VIEW.w, VIEW.h, 30); ctx.clip();
    const sc = scrollAt(t), v = Math.abs(scrollAt(t + 1 / 60) - scrollAt(t - 1 / 60)) * 30, fast = clamp(v / 4000), i0 = Math.max(0, Math.floor(sc / RH) - 1), scanY = y + VIEW.head + 270;
    for (let i = i0; i < Math.min(ROWS.length, i0 + 13); i++) {
      const r = ROWS[i], ry = y + VIEW.head + i * RH - sc, mid = ry + RH / 2; if (ry > VIEW.h / 2 || ry < y + VIEW.head - RH) continue;
      const hot = r[3] && mid < scanY;
      if (hot) { ctx.fillStyle = C.orange; ctx.fillRect(x, ry, VIEW.w, RH - 4); } else if (i % 2) { ctx.fillStyle = 'rgba(21,25,34,.035)'; ctx.fillRect(x, ry, VIEW.w, RH); }
      ctx.save(); ctx.globalAlpha *= hot ? 1 : lerp(1, .42, fast);
      text(dshort(r[0]), x + 32, mid + 11, {size: 30, weight: 500, fam: 'Inter', color: hot ? '#fff' : '#7C8496'});
      text(fit(r[1], 25), x + 160, mid + 11, {size: 30, weight: hot ? 800 : 600, fam: 'Inter', color: hot ? '#fff' : C.ink});
      text(amt(r[2]), x + VIEW.w - 32, mid + 11, {size: 30, weight: 700, fam: 'Inter', color: hot ? '#fff' : (r[2] > 0 ? '#1F8A6D' : C.ink), align: 'right'});
      ctx.restore();
    }
    if (fast > .05) { const g = ctx.createLinearGradient(0, y + VIEW.head, 0, VIEW.h / 2); g.addColorStop(0, rgba('#FBF8F1', .85 * fast)); g.addColorStop(.25, rgba('#FBF8F1', 0)); g.addColorStop(.8, rgba('#FBF8F1', 0)); g.addColorStop(1, rgba('#FBF8F1', .85 * fast)); ctx.fillStyle = g; ctx.fillRect(x, y + VIEW.head, VIEW.w, VIEW.h); }
    const live = seg(t, T.scan + .05, T.scan + .2);
    if (live > 0) { const g = ctx.createLinearGradient(0, scanY - 46, 0, scanY + 6); g.addColorStop(0, rgba(C.orange, 0)); g.addColorStop(1, rgba(C.orange, .30 * live)); ctx.fillStyle = g; ctx.fillRect(x, scanY - 46, VIEW.w, 52); ctx.fillStyle = rgba(C.orange, live); ctx.fillRect(x, scanY, VIEW.w, 5); }
    ctx.fillStyle = C.paper; ctx.fillRect(x, y, VIEW.w, VIEW.head); ctx.fillStyle = C.line; ctx.fillRect(x, y + VIEW.head - 3, VIEW.w, 3);
    fileIcon(x + 56, y + 39, .58); text('statement.csv', x + 94, y + 51, {size: 33, weight: 700, fam: 'Inter', color: C.ink});
    const tagw = tw('SAMPLE STATEMENT', 26, 800, 'Inter') + 16 * 2 + 40; ctx.fillStyle = C.ink; rr(x + VIEW.w - tagw - 24, y + 15, tagw, 48, 24); ctx.fill(); text('SAMPLE STATEMENT', x + VIEW.w - 24 - tagw / 2, y + 48, {size: 26, weight: 800, fam: 'Inter', color: C.gold, align: 'center', ls: 2});
    ctx.restore();
  });
  const cp = seg(t, T.scan + .1, T.stack - .1), secs = Math.round(SECS * cp), p = seg(t, T.scan - .05, T.scan + .25);
  if (p > 0) at(515, 500, lerp(.8, 1, E.back(p)), undefined, 0, clamp(p * 3), () => {
    card(-270, -38, 540, 76, 38, C.glass2, {blur: 24, dy: 10, stroke: 'rgba(255,255,255,.12)'});
    ctx.strokeStyle = C.gold; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(-222, 0, 20, 0, 7); ctx.stroke(); ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-222, 0); ctx.lineTo(-222 + 13 * Math.sin(cp * 12.566), -13 * Math.cos(cp * 12.566)); ctx.stroke();
    text('0:' + String(secs).padStart(2, '0'), -184, 17, {size: 48, weight: 800}); text('timed run, sped up', 240, 11, {size: 29, weight: 700, fam: 'Inter', color: C.soft, align: 'right'});
  });
}

/* ------------------------------------------------------------------ 9.8 to 13.8 s: the list builds, the month, the year */
const chipT = (i) => 9.9 + i * .17, chipY = (i) => 648 + i * 64;
function payoff(t) {
  if (t < T.stack || t >= T.twice) return;
  const gather = (i) => E.in3(seg(t, 12.42 + (SUBS.length - 1 - i) * .02, 12.78));
  let sum = 0;
  SUBS.forEach((s, i) => {
    const p = seg(t, chipT(i), chipT(i) + .42); sum += s.a * E.out3(seg(t, chipT(i) + .26, chipT(i) + .46)); if (p <= 0) return;
    const k = E.spring(p, 5.5, 9), g = gather(i); if (g >= 1) return;
    const x = lerp(lerp(i % 2 ? 1300 : -280, 510, E.out3(p)), 510, g), y = lerp(lerp(chipY(i) + 60, chipY(i), E.out3(p)), 470, g), sc = lerp(lerp(.3, 1, k), .15, g);
    at(x, y, sc, sc, (1 - E.out3(p)) * (i % 2 ? .12 : -.12), clamp(p * 4) * (1 - seg(g, .6, 1)), () => chipRow(s, 800));
  });
  const yr = E.outExpo(seg(t, T.year, T.year + .3)), val = lerp(sum, YEARLY, yr), mv = E.io3(seg(t, 12.42, 12.86));
  const size = lerp(150, 172, mv), cy = lerp(500, 740, mv);
  const pulse = t >= T.month && t < T.month + .5 ? 1 + .1 * Math.sin(seg(t, T.month, T.month + .5) * Math.PI) : 1, punch = t >= T.year ? 1 + .14 * Math.exp(-6 * (t - T.year)) : 1;
  if (t >= T.year) { const q = t - T.year; ring(540, cy - 60, 340 + 560 * E.out3(q / .8), C.gold, .9 * (1 - seg(q, 0, .8)), 10); ring(540, cy - 60, 300 + 420 * E.out3((q - .1) / .8), C.orange, .6 * (1 - seg(q, .1, .9)), 6); }
  at(540, cy, pulse * punch, undefined, 0, 1, () => {
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.55)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 14; roll(val, 0, 0, size, mixc(C.cream, C.gold, seg(t, T.month, T.month + .2)), true); ctx.restore();
    const lm = seg(t, T.month, T.month + .2) * (1 - seg(t, 12.6, 12.8)), ly = seg(t, T.year + .05, T.year + .3);
    if (lm > 0) text('a month', 0, 76, {size: 50, weight: 700, color: rgba(C.cream, lm), align: 'center'});
    if (ly > 0) { text('a year', 0, 92, {size: 62, weight: 800, color: rgba(C.cream, ly), align: 'center'}); text(money(MONTHLY) + '  x  12 months', 0, 168, {size: 38, weight: 600, fam: 'Inter', color: rgba(C.soft, ly), align: 'center'}); }
  });
}

/* ------------------------------------------------------------------ 13.8 to 19.7 s: three more catches, each its own picture */
function rowCard(cx, cy, o = {}) {
  at(cx, cy, o.s || 1, undefined, o.rot || 0, o.alpha, () => {
    card(-440, -92, 880, 184, 34, C.cream, {stroke: o.stroke, lw: 8});
    text('OCT 16', -400, -30, {size: 28, weight: 800, fam: 'Inter', color: '#7C8496', ls: 3}); text('HOMEBASE HARDWARE', -400, 40, {size: 41, weight: 800, fam: 'Inter', color: C.ink});
    text(money(DATA.double.amount), 404, 34, {size: 66, weight: 800, color: o.amt || C.ink, align: 'right'});
  });
}
function twice(t) {
  if (t < T.twice || t >= T.price) return;
  const a = E.spring(seg(t, T.twice - .1, T.twice + .5), 5, 9), b = E.spring(seg(t, 13.9, 14.45), 5, 9), snap = E.io3(seg(t, 14.42, 14.62));
  const hit = t - 14.62, sh = hit >= 0 ? Math.exp(-9 * hit) * 12 : 0, jx = sh * Math.sin(hit * 80), red = hit >= 0;
  rowCard(lerp(-560, 510, a) + jx, 640, {stroke: red ? C.red : null, amt: red ? C.red : C.ink}); rowCard(lerp(1640, 510, b) - jx, lerp(880, 838, snap), {stroke: red ? C.red : null, amt: red ? C.red : C.ink});
  if (hit >= 0) { badge(622, 739, 'x2', C.red, lerp(2.6, 1, E.out3(hit / .16)), {size: 84, rot: -.1, alpha: clamp(hit * 12)}); ring(622, 739, 90 + 260 * E.out3(hit / .5), C.red, .8 * (1 - seg(hit, 0, .5)), 8); }
}
function title(s, sub, t, a) {
  const p = E.out3(seg(t, a - .08, a + .22)); ctx.save(); ctx.globalAlpha = p;
  text(s, 540, 440 + (1 - p) * 30, {size: 46, weight: 800, fam: 'Inter', align: 'center', ls: 3}); text(sub, 540, 494 + (1 - p) * 30, {size: 34, weight: 600, fam: 'Inter', color: C.soft, align: 'center'}); ctx.restore();
}
function price(t) {
  if (t < T.price || t >= T.deliv) return;
  const PJ = DATA.price, vals = [PJ.from, PJ.to, PJ.to], t0 = [T.price, 16.28, 16.52], base = 1090, k = 44;
  title('CLOUDBOX STORAGE', 'what it charges each month', t, T.price);
  vals.forEach((v, i) => {
    const p = i ? E.spring(seg(t, t0[i], t0[i] + .6), 5, 10) : E.out3(seg(t, t0[i], t0[i] + .3)), h = v * k * p, x = 240 + i * 280;
    if (seg(t, t0[i], t0[i] + .1) <= 0) return;
    card(x - 85, base - h, 170, h, 22, i ? C.orange : C.teal, {blur: 34, dy: 14});
    text(money(v), x, base - h - 26, {size: 62, weight: 800, align: 'center', color: i ? C.gold : C.cream}); text(['Aug', 'Sep', 'Oct'][i], x, base + 58, {size: 38, weight: 700, fam: 'Inter', color: C.soft, align: 'center'});
  });
  const bp = seg(t, 16.82, 17.05); if (bp > 0) badge(310, 800, (PJ.to / PJ.from).toFixed(1) + 'x', C.red, lerp(1.9, 1, E.out3(bp)), {size: 64, rot: -.08, alpha: clamp(bp * 5)});
}
function bag(x, y, s, alpha) {
  at(x, y, s, s, 0, alpha, () => {
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.4)'; ctx.shadowBlur = 16; ctx.shadowOffsetY = 8; ctx.fillStyle = '#E2C290'; rr(-38, -34, 76, 84, 8); ctx.fill(); ctx.restore();
    ctx.fillStyle = '#C9A772'; ctx.fillRect(-38, -34, 76, 18); ctx.strokeStyle = '#8B6B3D'; ctx.lineWidth = 5; ctx.beginPath(); ctx.arc(0, -36, 16, Math.PI, 0); ctx.stroke();
    ctx.fillStyle = C.orange; ctx.beginPath(); ctx.arc(0, 14, 13, 0, 7); ctx.fill();
  });
}
function delivery(t) {
  if (t < T.deliv || t >= T.katch) return;
  const t0 = [T.deliv + .05, 18.15, 18.55];
  title('DASHDISH DELIVERY', 'orders each month', t, T.deliv);
  DELN.forEach((n, i) => {
    const cx = 215 + i * 295;
    for (let j = 0; j < n; j++) { const p = seg(t, t0[i] + j * .028, t0[i] + j * .028 + .3); if (p > 0) bag(cx + (j % 3 - 1) * 90, 1000 - Math.floor(j / 3) * 106 - (1 - E.out3(p)) * 160, lerp(.4, 1, E.spring(p, 5, 10)), clamp(p * 4)); }
    const lp = seg(t, t0[i] + .2, t0[i] + .45); if (lp > 0) { ctx.save(); ctx.globalAlpha *= lp; text(n + ' orders', cx, 1104, {size: 46, weight: 800, align: 'center', color: i === 2 ? C.gold : C.cream}); text(['Aug', 'Sep', 'Oct'][i] + '  ' + money(DEL[i], false), cx, 1152, {size: 34, weight: 700, fam: 'Inter', color: C.soft, align: 'center'}); ctx.restore(); }
  });
  const bp = seg(t, 19.0, 19.22); if (bp > 0) badge(300, 640, (DELN[2] / DELN[0]) + 'x orders', C.orange, lerp(1.9, 1, E.out3(bp)), {size: 60, rot: -.06, alpha: clamp(bp * 5)});
}

/* ------------------------------------------------------------------ 19.7 to 23.6 s: the catch: it sees the file, so cut rows first */
function katch(t) {
  if (t < T.katch || t >= T.cut) return;
  const inn = E.spring(seg(t, T.katch - .08, T.katch + .5), 5.5, 8), B0 = {x: 250, y: 600, w: 580, h: 520};
  /* the file slides into the AI, and the rows show through its face: it reads them */
  const fall = E.in3(seg(t, 19.95, 20.3)), fy = lerp(420, B0.y + 80, fall);
  at(540, B0.y + B0.h / 2 + (1 - inn) * 500, 1, 1, 0, 1, () => {
    const x = -B0.w / 2, y = -B0.h / 2; card(x, y, B0.w, B0.h, 60, C.glass, {stroke: 'rgba(255,255,255,.16)', lw: 3});
    const see = seg(t, 20.3, 20.55);
    if (see > 0) { ctx.save(); rr(x + 26, y + 120, B0.w - 52, B0.h - 150, 26); ctx.clip(); ctx.fillStyle = rgba('#FBF8F1', see); ctx.fillRect(x, y, B0.w, B0.h);
      const sc = (t - 20.3) * 150; for (let i = 0; i < 12; i++) { const r = ROWS[100 + i], yy = y + 170 + i * 50 - sc; text(dshort(r[0]), x + 46, yy, {size: 25, weight: 500, fam: 'Inter', color: '#7C8496'}); text(fit(r[1], 16), x + 150, yy, {size: 25, weight: 700, fam: 'Inter', color: C.ink}); text(amt(r[2]), x + B0.w - 46, yy, {size: 25, weight: 700, fam: 'Inter', color: C.ink, align: 'right'}); }
      const sy = y + 130 + ((t * 260) % (B0.h - 170)); ctx.fillStyle = rgba(C.teal, .9); ctx.fillRect(x, sy, B0.w, 5); const g = ctx.createLinearGradient(0, sy - 60, 0, sy); g.addColorStop(0, rgba(C.teal, 0)); g.addColorStop(1, rgba(C.teal, .28)); ctx.fillStyle = g; ctx.fillRect(x, sy - 60, B0.w, 60); ctx.restore(); }
    sparkle(x + 70, y + 66, 30 + 3 * Math.sin(t * 5), C.gold, t * .4); text('AI', x + 116, y + 84, {size: 46, weight: 800, ls: 4});
    if (see > 0) { ctx.save(); ctx.globalAlpha = see; ctx.strokeStyle = C.teal; ctx.lineWidth = 7; ctx.lineCap = 'round'; const ex = B0.w / 2 - 84, ey = y + 68, bl = Math.abs(Math.sin(t * 2.2)) < .12 ? .15 : 1;
      ctx.beginPath(); ctx.ellipse(ex, ey, 42, 24 * bl, 0, 0, 7); ctx.stroke(); ctx.fillStyle = C.teal; ctx.beginPath(); ctx.arc(ex + 8 * Math.sin(t * 3), ey, 12 * bl, 0, 7); ctx.fill(); ctx.restore(); }
  });
  if (fall < 1) fileChip(540, fy, lerp(.9, .6, fall), seg(t, T.katch - .05, T.katch + .15) * (1 - seg(fall, .8, 1)));
  if (t >= 20.3 && t < 20.9) ring(540, B0.y + 60, 60 + 360 * E.out3(seg(t, 20.3, 20.9)), C.teal, .8 * (1 - seg(t, 20.3, 20.9)), 8);
}
function cutRows(t) {
  if (t < T.cut || t >= T.end) return;
  const find = (re) => ROWS.findIndex((r) => r[0] >= '2026-10-01' && re.test(r[1])), idx = [find(/GREENLEAF/), find(/PAYROLL/), find(/RENT/), find(/STREAMLY/)], gone = [1, 2], tg = [21.95, 22.3];
  const bx = 800, by = 1050, lid = Math.max(...tg.map((q) => Math.sin(seg(t, q + .15, q + .6) * Math.PI)));
  at(bx, by, lerp(.6, 1, E.spring(seg(t, T.cut, T.cut + .5), 5, 9)), undefined, 0, seg(t, T.cut - .05, T.cut + .15), () => {   /* the bin */
    ctx.fillStyle = '#3A455C'; rr(-56, -50, 112, 120, 14); ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,.3)'; ctx.lineWidth = 5; [-22, 0, 22].forEach((q) => { ctx.beginPath(); ctx.moveTo(q, -28); ctx.lineTo(q, 48); ctx.stroke(); });
    at(-64, -58, 1, 1, -lid * .7, 1, () => { ctx.fillStyle = '#56627D'; rr(0, -16, 128, 18, 8); ctx.fill(); rr(44, -30, 40, 16, 6); ctx.fill(); });
  });
  idx.forEach((ri, i) => {
    const r = ROWS[ri], g = gone.indexOf(i), inn = E.spring(seg(t, T.cut - .08 + i * .06, T.cut + .45 + i * .06), 5.5, 9);
    const closed = gone.filter((q) => q < i).reduce((s, q) => s + E.io3(seg(t, tg[gone.indexOf(q)] + .45, tg[gone.indexOf(q)] + .8)), 0);
    let x = lerp(-600, 510, inn), y = 600 + i * 122 - closed * 122, sc = 1, al = 1, rot = 0;
    if (g >= 0) { const p = seg(t, tg[g], tg[g] + .55), lift = E.out3(seg(p, 0, .3)), fly = E.in3(seg(p, .3, 1)); x = lerp(x + lift * 40, bx, fly); y = lerp(y - lift * 26, by - 40, fly); sc = lerp(1, .12, fly); rot = fly * .5; al = 1 - seg(p, .9, 1); if (p >= 1) return; }
    at(x, y, sc, sc, rot, al, () => {
      const hot = g >= 0 && t >= tg[g] - .15; card(-420, -50, 840, 100, 26, hot ? '#FFE1D6' : C.cream, {blur: 24, dy: 10, stroke: hot ? C.orange : null, lw: 6});
      text(dshort(r[0]), -388, 13, {size: 31, weight: 600, fam: 'Inter', color: '#7C8496'}); text(fit(r[1], 20), -268, 13, {size: 33, weight: 700, fam: 'Inter', color: C.ink}); text(amt(r[2]), 392, 14, {size: 36, weight: 800, color: r[2] > 0 ? '#1F8A6D' : C.ink, align: 'right'});
    });
  });
}

/* ------------------------------------------------------------------ 23.6 s to the end: the card worth saving */
function stepIcon(i, x, y, p) {
  ctx.save(); ctx.translate(x, y); ctx.fillStyle = C.orange; ctx.beginPath(); ctx.arc(0, 0, 46, 0, 7); ctx.fill(); ctx.strokeStyle = '#fff'; ctx.fillStyle = '#fff'; ctx.lineWidth = 7; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const b = Math.sin(clamp(p) * Math.PI) * 8;
  if (i === 0) { ctx.beginPath(); ctx.moveTo(0, -22 + b); ctx.lineTo(0, 8 + b); ctx.moveTo(-12, -4 + b); ctx.lineTo(0, 9 + b); ctx.lineTo(12, -4 + b); ctx.stroke(); ctx.beginPath(); ctx.moveTo(-20, 22); ctx.lineTo(20, 22); ctx.stroke(); }
  if (i === 1) { rr(-22, 0, 44, 24, 7); ctx.stroke(); rr(-11, -26 + b, 22, 26, 4); ctx.fill(); }
  if (i === 2) { rr(-24, -20, 48, 34, 10); ctx.stroke(); ctx.beginPath(); ctx.moveTo(-8, 14); ctx.lineTo(-14, 26); ctx.lineTo(4, 14); ctx.fill(); [-11, 0, 11].forEach((q, k) => { ctx.beginPath(); ctx.arc(q, -3 - (Math.floor(p * 6) % 3 === k ? 4 : 0), 3.5, 0, 7); ctx.fill(); }); }
  ctx.restore();
}
function endCard(t) {
  if (t < T.end) return;
  const inn = E.back(seg(t, T.end - .08, T.end + .4), 1.1), cy = 712 + (1 - inn) * 760;
  at(510, cy, 1, 1, 0, 1, () => {
    card(-440, -440, 880, 906, 44, C.cream);
    text('No bank link.', -384, -322, {size: 86, weight: 800, color: C.ink}); text('Just a file.', -384, -230, {size: 86, weight: 800, color: '#2B8C7C'});
    const steps = [['Download your statement', 'as a CSV'], ['Drop it into an AI chat'], ['Ask: ' + Q[0].slice(0, 20).replace('What', 'what'), Q[0].slice(21), Q[1]]], SY = [-126, 2, 124];
    steps.forEach((s, i) => {
      const p = i ? E.spring(seg(t, T.end + .25 + i * .3, T.end + .75 + i * .3), 6, 9) : 1, y = SY[i]; if (p <= 0) return;
      ctx.save(); ctx.globalAlpha = clamp(p * 2); ctx.translate((1 - p) * 60, 0); stepIcon(i, -336, y, seg(t, T.end + .5 + i * .3, T.end + 1.3 + i * .3));
      s.forEach((ln, k) => text(ln, -264, y + (s.length > 1 ? -8 : 18) + k * 54, {size: 47, weight: 700, fam: 'Inter', color: C.ink}));
      ctx.restore();
    });
    const f = seg(t, T.end + .2, T.end + .5); ctx.save(); ctx.globalAlpha = f; ctx.fillStyle = C.line; ctx.fillRect(-384, 270, 768, 3);
    ['Sample statement, made-up names.', 'Run: ' + DATA.run.model + ', ' + DATA.run.date + '.', 'AI gets numbers wrong. Check them.'].forEach((s, i) => text(s, -384, 326 + i * 50, {size: 39, weight: 700, fam: 'Inter', color: '#3F4758'})); ctx.restore();
  });
}

/* ------------------------------------------------------------------ the camera and the frame */
function camera(t) {
  let s = 1 + .012 * Math.sin(t * .9);                       /* the frame is never quite still */
  s += .04 * seg(t, 0, T.plug) * (t < T.plug ? 1 : 0);
  s += .03 * Math.sin(seg(t, T.scan, T.stack) * Math.PI);
  if (t >= T.year && t < T.twice) s += .05 * Math.exp(-5 * (t - T.year));
  return {s, cx: 540, cy: 960};
}
window.drawAt = function (t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1;
  room(t, tintAt(t));
  const c = camera(t); ctx.save(); ctx.translate(540, 960); ctx.scale(c.s, c.s); ctx.translate(-c.cx, -c.cy);
  open(t); intro(t); aiBox(t); noLink(t); attachment(t); ledger(t); payoff(t); twice(t); price(t); delivery(t); katch(t); cutRows(t); endCard(t);
  ctx.restore();
  sampleTag(t); captions(t, CAPS); grain(t);
};
window.DURATION = T.stop;
Promise.all(['800 84px Poppins', '700 40px Poppins', '500 30px Inter', '600 30px Inter', '700 30px Inter', '800 30px Inter'].map((f) => document.fonts.load(f)))
  .then(() => { window.drawAt(0); window.READY = true; }).catch((e) => { window.BOOT_ERROR = String(e); });
