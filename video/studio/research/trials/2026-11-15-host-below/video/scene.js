// Host-below trial (Todd, Nov 15, 2026; coo/DECISIONS-2026-11-15.md). One frame is a pure function of the time.
// Top: the real thing (captures of our own results file, three frames of our own lessons) or a card drawn from the
// file's numbers. Middle: one or two words. Bottom: the studio's host (kit.js k.snow, unchanged), drawn large, his
// mouth on the voice. Round 1 of the build (reviews/r0.json lists what round 0 got wrong).
(function () {
  const W = 1080, H = 1920, FPS = 30, q = new URLSearchParams(location.search);
  const D = window.DATA, SH = window.SHOTS, WD = window.WORDS.words, CAPS = window.CAPTIONS;
  const PIX = +(q.get('pix') || 8);                       // one host pixel, in frame pixels
  const HS = +(q.get('hs') || 2.62), HEADY = +(q.get('hy') || 1312), HX = 540;   // host scale, head center
  const look = Object.assign({}, window.LOOKS.arcade, {scale: 1 / PIX});
  const C = look.c, INK = '#120D14', CREAM = '#FFF7EA', GOLD = '#F7C873', AMBER = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', PLUM = '#2B2033', MUTED = '#B39A88', CARD = '#1F1726', TRACK = '#3D2E45';
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const easeOut = (x) => 1 - Math.pow(1 - clamp(x), 3);
  const wt = (i) => WD[i].start;
  const END = WD[WD.length - 1].end, DUR = Math.ceil((END + 0.6) * FPS) / FPS;
  const imgs = {};

  // ---- captions: one or two words, on the word, clear of the apps' right-hand buttons ----
  const caps = []; { let i = 0; CAPS.forEach(([text, n]) => { caps.push({text, i0: i, i1: i + n - 1}); i += n; }); if (i !== WD.length) throw new Error(`captions cover ${i} words, the voice has ${WD.length}`); }
  caps.forEach((c) => { c.t0 = Math.max(0, wt(c.i0) - 0.04); });
  caps.forEach((c, j) => { const nx = caps[j + 1]; c.t1 = nx ? nx.t0 : DUR; });   // a caption holds until the next one: never an empty beat
  const capAt = (T) => caps.find((c) => T >= c.t0 && T < c.t1);

  // ---- the storyboard, keyed to word numbers (voice/script.md). Every change is a plain cut on a word. ----
  // card: our own graphic from data.js. file: a real capture (capture.py), whole lines only, the line boxed as it is said.
  // split: the capture above, our running count below, the bar growing on the number.
  const A = {chatgpt: D.chatgpt, claude: D.second, local: D.winner, trades: D.trades};
  const ROWS = [   // the running count, in the order they are said: [key, label, color, word that reveals it]
    ['chatgpt', 'ChatGPT', TEAL, 53], ['claude', 'Claude', TEAL, 59], ['local', 'AI on your own computer', AMBER, 71], ['trades', 'AI for the trades (mine)', RED, 83]];
  const BEATS = [
    {w: 0, kind: 'card', card: 'hook'},
    {w: 11, kind: 'file', top: 'rules', lines: 4, cols: 20, hl: [['days', 20, 'amber']]},
    {w: 23, kind: 'file', top: 'videos', up: 1, lines: 3, cols: 15, hl: [['videos', 23, 'amber']]},
    {w: 28, kind: 'file', top: 'agents', lines: 4, cols: 19, hl: [['agents_kept', 34, 'amber'], ['agents_hot', 39, 'amber']]},
    {w: 41, kind: 'file', top: 'rules', lines: 4, cols: 20, hl: [['min_views', 43, 'amber'], ['ratio', 47, 'amber']]},
    {w: 51, kind: 'split', top: 'chatgpt', hl: [['chatgpt', 51, 'teal'], ['chatgpt_hot', 53, 'amber'], ['chatgpt_kept', 55, 'amber']]},
    {w: 56, kind: 'split', top: 'claude', hl: [['claude', 58, 'teal'], ['claude_hot', 59, 'amber']]},
    {w: 60, kind: 'split', top: 'local', hl: [['local', 63, 'teal'], ['local_hot', 71, 'amber']]},
    {w: 74, kind: 'card', card: 'ours'},
    {w: 83, kind: 'split', top: 'trades', hl: [['trades', 83, 'teal'], ['trades_hot', 83, 'red'], ['trades_kept', 85, 'red']]},
    {w: 86, kind: 'file', top: 'laptop_line', lines: 4, cols: 34, mine: true, hl: [['laptop_videos', 89, 'amber'], ['laptop', 97, 'teal'], ['laptop_small', 105, 'amber']]},
    {w: 114, kind: 'card', card: 'small'},
    {w: 120, kind: 'card', card: 'close'},
  ];
  BEATS.forEach((b, i) => { b.t = i ? wt(b.w) - 0.08 : 0; });
  const beatAt = (T) => { let b = BEATS[0]; for (const x of BEATS) if (T >= x.t) b = x; return b; };

  // ---- the host's poses, by word number ----
  const POSES = [[0, 'talk'], [6, 'shrug'], [8, 'point'], [11, 'talk'], [23, 'point'], [28, 'talk'], [41, 'point'], [51, 'talk'], [59, 'point'], [60, 'talk'],
                 [71, 'point'], [72, 'shrug'], [74, 'talk'], [83, 'shrug'], [86, 'talk'], [89, 'point'], [97, 'talk'], [105, 'point'], [114, 'talk'],
                 [120, 'shrug'], [128, 'talk'], [140, 'point']].map(([w, p]) => ({t: wt(w) - 0.08, p}));
  const poseAt = (T) => { let p = 'talk'; for (const x of POSES) if (T >= x.t) p = x.p; return p; };

  // ---- the two hits: a stamp half a second in, a stamp on the last word ----
  const HIT0 = 0.45, HIT1 = wt(144) - 0.02;
  const shakeAt = (T, t0) => (T >= t0 && T < t0 + 0.3 ? Math.round(Math.sin((T - t0) * 70) * 8 * (1 - (T - t0) / 0.3)) : 0);

  // ---- sound cues for render.py: [time, effect, volume] ----
  const SFX = [[HIT0, 'stamp', 0.9], [HIT1, 'stamp', 1.0], [wt(71) - 0.03, 'chime', 0.55]];
  BEATS.forEach((b, i) => { if (i) SFX.push([b.t, 'pop', 0.45]); (b.hl || []).forEach(([k, w, c]) => SFX.push([wt(w) - 0.03, 'tick', c === 'red' ? 0.9 : 0.6])); });
  [75, 76, 77].forEach((w) => SFX.push([wt(w) - 0.05, 'blip', 0.5]));
  [128, 130, 132].forEach((w) => SFX.push([wt(w) - 0.03, 'tick', 0.6]));

  // ---- the host: the kit's own Snow on a low-res canvas, then hard edges and the arcade palette ----
  const hostC = document.createElement('canvas'); hostC.width = Math.round(W / PIX); hostC.height = Math.round(H / PIX);
  const pal = look.palette.map((h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)]);
  const hex = (h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
  const SKIN = hex(C.skin), JACKET = hex(C.jacket);
  const M = window.MOUTH && window.MOUTH.shapes ? window.MOUTH : null;
  const shapeAt = (T) => { if (!M) return null; const i = Math.floor(T * M.fps + 0.005); return i >= 0 && i < M.shapes.length ? M.shapes[i] : 'X'; };
  const LEVEL = {X: 0, A: 0, B: 1, G: 1, C: 2, E: 2, F: 2, H: 2, D: 3};   // the kit's jaw: drops one pixel when open
  const env = {data: D, words: WD, duration: DUR, img: () => null, cue: () => { throw new Error('no cues here'); },
               talking: (T) => WD.some((w) => T >= w.start - 0.02 && T < w.end + 0.06),
               mouth: (t) => (M ? LEVEL[shapeAt(t)] || 0 : (env.talking(t) ? 1 + (Math.floor(t * 12) % 2) : 0))};
  // Rhubarb's nine mouth shapes on the host's pixel grid: [row, width, color], lips drawn so the mouth reads on a
  // phone against the beard (round 0's mouth, the kit's own size, was too small to read at this scale)
  const MOUTHS = {
    X: [[0, 10, 'lip']], A: [[0, 8, 'lip']],
    B: [[0, 10, 'lip'], [1, 10, 'lip'], [1, 8, 'teeth'], [2, 10, 'lip']],
    C: [[0, 10, 'lip'], [1, 10, 'lip'], [1, 8, 'teeth'], [2, 10, 'lip'], [2, 8, 'dark'], [3, 10, 'lip'], [3, 8, 'dark'], [4, 8, 'lip']],
    D: [[0, 12, 'lip'], [1, 12, 'lip'], [1, 10, 'teeth'], [2, 12, 'lip'], [2, 10, 'dark'], [3, 12, 'lip'], [3, 10, 'dark'], [4, 12, 'lip'], [4, 10, 'dark'], [4, 6, 'tongue'], [5, 10, 'lip']],
    E: [[0, 8, 'lip'], [1, 8, 'lip'], [1, 6, 'dark'], [2, 8, 'lip'], [2, 6, 'dark'], [3, 8, 'lip'], [3, 6, 'dark'], [3, 4, 'tongue'], [4, 6, 'lip']],
    F: [[0, 6, 'lip'], [1, 6, 'lip'], [1, 4, 'dark'], [2, 6, 'lip'], [2, 4, 'dark'], [3, 4, 'lip']],
    G: [[0, 10, 'lip'], [1, 10, 'lip'], [1, 8, 'teeth'], [2, 6, 'lip']],
    H: [[0, 10, 'lip'], [1, 10, 'lip'], [1, 8, 'teeth'], [2, 10, 'lip'], [2, 8, 'dark'], [2, 4, 'tongue'], [3, 8, 'lip']],
  };
  const MC = {lip: C.skinShade, teeth: C.paper, dark: '#2B2033', tongue: '#7A3442'};
  function host(ctx, T) {
    const h = hostC.getContext('2d'); h.setTransform(1, 0, 0, 1, 0, 0); h.clearRect(0, 0, hostC.width, hostC.height);
    h.setTransform(1 / PIX, 0, 0, 1 / PIX, 0, 0);
    const pose = poseAt(T), oy = HEADY + 384 * HS;
    // he bobs one pixel on each new caption (two frames), like a talking sprite, and dips on the two hits
    const cNow = capAt(T), bobNow = cNow && T - cNow.t0 < 2 / FPS && T <= END;
    const nod = [HIT0, HIT1].some((t) => T >= t && T < t + 4 / FPS) || bobNow ? PIX : 0;
    const k = window.Kit.make(h, look, T, env);
    k.snow(HX, oy + nod, {scale: HS, pose, face: 1, at: [1060, 770]});
    if (M) {   // the mouth shape for this frame, over the kit's own mouth, on the same pixel grid
      const bp = ((T % 2.8) + 2.8) % 2.8, bob = bp >= 1.4 && bp < 2.4 ? -1 : 0;   // the kit's breath lifts the head one pixel
      const mx = (HX + 18 * HS) / PIX, my = Math.round((oy + nod + (-384 + 37) * HS) / PIX) + bob - 1;
      h.setTransform(1, 0, 0, 1, 0, 0);
      h.fillStyle = C.beard; h.fillRect(Math.round(mx - 6), my, 12, 6);
      MOUTHS[shapeAt(T)].forEach(([row, w, c]) => { h.fillStyle = MC[c]; h.fillRect(Math.round(mx - w / 2), my + row, w, 1); });
    }
    const id = h.getImageData(0, 0, hostC.width, hostC.height), d = id.data, lowRow = hostC.height - 6;
    for (let i = 0; i < d.length; i += 4) {
      if (d[i + 3] <= 110) { d[i + 3] = 0; continue; }
      let best = 0, bd = 1e9; const r = d[i], g = d[i + 1], bl = d[i + 2];
      for (let j = 0; j < pal.length; j++) { const p = pal[j], dd = (p[0] - r) ** 2 + (p[1] - g) ** 2 + (p[2] - bl) ** 2; if (dd < bd) { bd = dd; best = j; } }
      d[i] = pal[best][0]; d[i + 1] = pal[best][1]; d[i + 2] = pal[best][2]; d[i + 3] = 255;
      // a hanging hand the bottom edge would cut to a stray patch stays sleeve colored (round 0, design)
      if ((i / 4 / hostC.width | 0) >= lowRow && d[i] === SKIN[0] && d[i + 1] === SKIN[1] && d[i + 2] === SKIN[2]) { d[i] = JACKET[0]; d[i + 1] = JACKET[1]; d[i + 2] = JACKET[2]; }
    }
    h.putImageData(id, 0, 0);
    ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(hostC, 0, 0, W, H); ctx.restore();
  }

  // ---- drawing helpers (full resolution: the real thing stays crisp) ----
  const font = (ctx, size, weight = 700, fam = 'Poppins') => { ctx.font = `${weight} ${size}px ${fam}`; };
  function text(ctx, s, x, y, o = {}) {
    font(ctx, o.size || 40, o.weight || 700, o.font || 'Poppins'); ctx.textAlign = o.align || 'left'; ctx.textBaseline = o.base || 'alphabetic';
    ctx.fillStyle = o.color || CREAM; ctx.fillText(s, x, y);
  }
  const WIN = {x: 60, y: 236, w: 960, h: 624, bar: 60};   // the window above the host: clear of the apps' top band
  const BODY = {x: WIN.x, y: WIN.y + WIN.bar, w: WIN.w, h: WIN.h - WIN.bar};
  function frame(ctx, title, tag, bodyFill) {
    const {x, y, w, h, bar} = WIN;
    ctx.fillStyle = 'rgba(0,0,0,0.45)'; ctx.fillRect(x + 12, y + 12, w, h);
    ctx.fillStyle = bodyFill; ctx.fillRect(x, y, w, h);
    ctx.fillStyle = PLUM; ctx.fillRect(x, y, w, bar);
    [RED, AMBER, TEAL].forEach((c, i) => { ctx.fillStyle = c; ctx.fillRect(x + 24 + i * 34, y + 20, 20, 20); });
    text(ctx, title, x + 140, y + 43, {size: 36, weight: 600, font: 'Inter', color: CREAM});
    if (tag) text(ctx, tag, x + w - 24, y + 43, {size: 36, weight: 700, font: 'Inter', color: GOLD, align: 'right'});
  }
  function border(ctx) { const {x, y, w, h} = WIN; ctx.strokeStyle = '#F4E6D3'; ctx.lineWidth = 6; ctx.strokeRect(x + 3, y + 3, w - 6, h - 6); }

  // a real capture: whole lines only, sized so no line in view is cut, the lines boxed as they are said
  const PG = SH.pages.results, BX = PG.boxes;
  const LH = BX.min_views[0][1] - BX.days[0][1];             // one line, in capture pixels
  const CW = BX.videos[0][2] / '"videos": 529'.length;       // one character, in capture pixels
  const HLC = {amber: ['rgba(242,165,65,0.42)', '#E08A1E'], red: ['rgba(226,99,59,0.40)', '#C9421B'], teal: ['rgba(111,183,168,0.45)', '#3D8F7F']};
  function capture(ctx, rect, v, T) {
    const top = BX[v.top][0], sy = top[1] - (v.up || 0) * LH, sx = top[0] - 6, sw = v.cols * CW + 12, sh = v.lines * LH;
    const z = Math.min((rect.h - 24) / sh, (rect.w - 72) / sw), dx = rect.x + 36, dy = rect.y + (rect.h - sh * z) / 2;
    ctx.fillStyle = '#FFFFFF'; ctx.fillRect(rect.x, rect.y, rect.w, rect.h);
    ctx.save(); ctx.beginPath(); ctx.rect(rect.x, rect.y, rect.w, rect.h); ctx.clip();
    ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(imgs.results, sx, sy, sw, sh, dx, dy, sw * z, sh * z);
    (v.hl || []).forEach(([key, w, col]) => {
      const t0 = wt(w) - 0.03; if (T < t0) return;
      const p = easeOut((T - t0) / 0.16), [fill, edge] = HLC[col];
      BX[key].forEach((r) => { const x = dx + (r[0] - sx) * z - 8, y = dy + (r[1] - sy) * z + 2, w2 = (r[2] * z + 16) * p, h2 = r[3] * z - 4;
        ctx.fillStyle = fill; ctx.fillRect(x, y, w2, h2); ctx.fillStyle = edge; ctx.fillRect(x, y + h2 - 6, w2, 6); });
    });
    ctx.restore();
  }

  // our own count: bars on one scale (hot videos out of the 40 fastest)
  function barRow(ctx, x, y, o) {   // o: label, n, color, labelW, barW, size (label), num (number size), h (bar), p (0 to 1), shake, lit
    const full = D.per_area, w = Math.max(10, o.barW * o.n / full) * (o.p == null ? 1 : o.p);
    text(ctx, o.label, x, y, {size: o.size, weight: 700, color: o.lit ? GOLD : CREAM, base: 'middle'});
    ctx.fillStyle = TRACK; ctx.fillRect(x + o.labelW, y - o.h / 2, o.barW, o.h);
    ctx.fillStyle = o.color; ctx.fillRect(x + o.labelW, y - o.h / 2, w, o.h);
    if (o.p == null || o.p > 0.5) text(ctx, o.q || String(o.n), x + o.labelW + o.barW + 24 + (o.shake || 0), y + 2, {size: o.num, weight: 700, color: o.color, base: 'middle'});
  }
  function scoreboard(ctx, rect, T, big) {
    ctx.fillStyle = CARD; ctx.fillRect(rect.x, rect.y, rect.w, rect.h);
    text(ctx, 'HOT, OUT OF THE ' + D.per_area + ' FASTEST', rect.x + 36, rect.y + (big ? 52 : 44), {size: big ? 40 : 36, weight: 700, color: GOLD});
    const rows = big ? ROWS.slice().sort((a, b) => A[b[0]].hot - A[a[0]].hot) : ROWS, pitch = big ? 80 : 56, y0 = rect.y + (big ? 112 : 92);
    rows.forEach(([key, label, color, w], i) => {
      const t0 = wt(w) - 0.03; if (!big && T < t0) return;
      const p = big ? easeOut((T - BEATS[BEATS.length - 1].t) / 0.35) : easeOut((T - t0) / 0.3);
      const mine = key === 'trades', win = key === 'local';
      barRow(ctx, rect.x + 36, y0 + i * pitch, {label, n: A[key].hot, color, p, labelW: 540, barW: 250, size: 40, num: big ? 64 : 52, h: big ? 44 : 34,
        lit: big && ((mine && T >= wt(120) - 0.05 && T < wt(128) - 0.1) || (win && T >= HIT1)), shake: big && win ? shakeAt(T, HIT1) : (!big && T < t0 + 0.3 ? shakeAt(T, t0) : 0)});
    });
  }

  function card(ctx, b, T) {
    const y0 = BODY.y, x0 = WIN.x + 48;
    if (b.card === 'ours') {   // three frames from our own posted lessons (capture.py), one landing on each word
      frame(ctx, 'OUR VIDEOS', 'AI for the trades', CARD);
      SH.lessons.forEach((L, i) => {
        const t0 = wt(75 + i) - 0.05; if (T < t0) return;
        const f = (T - t0) * FPS, sc = f < 1 ? 0.8 : (f < 2 ? 1.06 : (f < 3 ? 0.98 : 1)), w = 330, h = w * L.h / L.w, cx = WIN.x + 192 + i * 288, cy = y0 + 282 + (i === 1 ? -12 : 10);
        ctx.save(); ctx.translate(cx, cy); ctx.rotate([-0.045, 0, 0.045][i]); ctx.scale(sc, sc);
        ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.fillRect(-w / 2 + 10, -h / 2 + 10, w, h);
        ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high'; ctx.drawImage(imgs[L.slug], -w / 2, -h / 2, w, h);
        ctx.strokeStyle = '#F4E6D3'; ctx.lineWidth = 6; ctx.strokeRect(-w / 2, -h / 2, w, h); ctx.restore();
      });
      border(ctx); return;
    }
    frame(ctx, 'OUR COUNT', 'Nov 13', CARD);
    if (b.card === 'hook') {   // frame 0: the stake, settled. ChatGPT's number against a winner still hidden.
      const cg = D.chatgpt, wn = D.winner, ask = Math.floor(T * 3) % 2 === 0;
      text(ctx, 'HOTTEST AI TOPIC ON YOUTUBE?', x0, y0 + 70, {size: 44, weight: 700, color: GOLD});
      barRow(ctx, x0, y0 + 176, {label: 'ChatGPT', n: cg.hot, color: TEAL, labelW: 290, barW: 300, size: 60, num: 96, h: 70});
      font(ctx, 96, 700); const nw = ctx.measureText(String(cg.hot)).width;
      text(ctx, 'of ' + D.per_area, x0 + 290 + 300 + 24 + nw + 18, y0 + 192, {size: 40, weight: 700, color: MUTED});
      barRow(ctx, x0, y0 + 322, {label: '? ? ?', n: wn.hot, color: ask ? GOLD : AMBER, q: '?', labelW: 290, barW: 300, size: 60, num: 96, h: 70});
      if (T >= HIT0) { const f = (T - HIT0) * FPS, sc = f < 1 ? 1.5 : (f < 2 ? 1.2 : (f < 3 ? 0.94 : 1)), cx = x0 + 290 + 300 * cg.hot / D.per_area + 14 + 100, cy = y0 + 176;   // beside ChatGPT's bar, never over it
        ctx.save(); ctx.translate(cx, cy); ctx.rotate(-0.06); ctx.scale(sc, sc); ctx.fillStyle = RED; ctx.fillRect(-100, -30, 200, 60); ctx.fillStyle = CARD; ctx.fillRect(-94, -24, 188, 48);
        text(ctx, 'NOT FIRST', 0, 2, {size: 36, weight: 700, color: RED, align: 'center', base: 'middle'}); ctx.restore(); }
      text(ctx, 'My count: ' + D.areas + ' topics, ' + D.per_area + ' fastest videos each,', x0, y0 + 464, {size: 36, weight: 600, font: 'Inter', color: T >= wt(8) - 0.05 && T < wt(11) - 0.1 ? GOLD : MUTED});
      text(ctx, 'the last ' + D.days + ' days. Hot: see the rule in a moment.', x0, y0 + 512, {size: 36, weight: 600, font: 'Inter', color: T >= wt(8) - 0.05 && T < wt(11) - 0.1 ? GOLD : MUTED});
    } else if (b.card === 'small') {   // 7 of the 12, as squares
      const L = D.laptop, t0 = b.t;
      text(ctx, L.videos + ' HOT VIDEOS: A BIG AI MODEL ON A LAPTOP', x0, y0 + 70, {size: 36, weight: 700, color: GOLD});
      for (let i = 0; i < L.videos; i++) { const on = T >= t0 + 0.05 + i * 0.04, sm = i < L.small_channel_wins, sz = 112, gx = x0 + (i % 6) * (sz + 30), gy = y0 + 110 + Math.floor(i / 6) * (sz + 26);
        if (!on) continue; ctx.fillStyle = sm ? TEAL : TRACK; ctx.fillRect(gx, gy, sz, sz); }
      ctx.fillStyle = TEAL; ctx.fillRect(x0, y0 + 418, 36, 36);
      text(ctx, L.small_channel_wins + ' from channels under ' + L.small_means_under.toLocaleString('en-US') + ' subscribers', x0 + 54, y0 + 449, {size: 36, weight: 700, color: CREAM});
      text(ctx, 'Grouped by my read of the titles.', x0 + 54, y0 + 506, {size: 36, weight: 600, font: 'Inter', color: MUTED});
    } else {   // the close: all four bars, the limits said and shown, the winner stamped on the last word
      scoreboard(ctx, {x: BODY.x, y: BODY.y, w: BODY.w, h: BODY.h}, T, true);
      const chips = [[128, '1 COUNT'], [130, D.days + ' DAYS'], [132, 'YOUTUBE ONLY']]; let cx = x0;
      chips.forEach(([w, s]) => { font(ctx, 36, 700); const tw = ctx.measureText(s).width + 40;
        if (T >= wt(w) - 0.03) { const e = easeOut((T - wt(w) + 0.03) / 0.14); ctx.fillStyle = TRACK; ctx.fillRect(cx, y0 + 408 + (1 - e) * 16, tw, 60); text(ctx, s, cx + 20, y0 + 451 + (1 - e) * 16, {size: 36, weight: 700, color: CREAM}); }
        cx += tw + 16; });
      text(ctx, 'Hot = ' + D.min_views.toLocaleString('en-US') + '+ views and ' + D.ratio + 'x the channel\u2019s normal', x0, y0 + 528, {size: 36, weight: 600, font: 'Inter', color: MUTED});
      if (T >= HIT1) { const f = (T - HIT1) * FPS, sc = f < 1 ? 1.5 : (f < 2 ? 1.2 : (f < 3 ? 0.94 : 1)), cx2 = BODY.x + 36 + 540 + 190, cy = BODY.y + 112;
        ctx.save(); ctx.translate(cx2, cy); ctx.rotate(-0.07); ctx.scale(sc, sc); ctx.fillStyle = AMBER; ctx.fillRect(-74, -36, 148, 72); ctx.fillStyle = CARD; ctx.fillRect(-67, -29, 134, 58);
        text(ctx, 'HOT', 0, 3, {size: 46, weight: 700, color: AMBER, align: 'center', base: 'middle'}); ctx.restore(); }
    }
    border(ctx);
  }

  function fileShot(ctx, b, T) {
    frame(ctx, 'OUR FILE', PG.file, '#FFFFFF');
    capture(ctx, BODY, b, T);
    if (b.mine) {   // the topic groups are a person's reading of the titles: say so on the capture
      font(ctx, 36, 700); const s = 'TOPIC GROUPS: MY READ', tw = ctx.measureText(s).width + 40, cx = BODY.x + BODY.w - tw - 30, cy = BODY.y + BODY.h - 84;
      ctx.fillStyle = PLUM; ctx.fillRect(cx, cy, tw, 60); text(ctx, s, cx + 20, cy + 43, {size: 36, weight: 700, color: GOLD});
    }
    border(ctx);
  }
  function split(ctx, b, T) {
    frame(ctx, 'OUR FILE', PG.file, '#FFFFFF');
    const sbH = 300, top = {x: BODY.x, y: BODY.y, w: BODY.w, h: BODY.h - sbH};
    capture(ctx, top, {top: b.top, lines: 4, cols: 17, hl: b.hl}, T);
    scoreboard(ctx, {x: BODY.x, y: BODY.y + top.h, w: BODY.w, h: sbH}, T, false);
    border(ctx);
  }

  function captions(ctx, T) {
    const c = capAt(T); if (!c) return;
    const toks = c.text.split(' '), MAXW = 780; let size = 136;
    font(ctx, size); let tw = ctx.measureText(c.text).width; if (tw > MAXW) { size = Math.floor(size * MAXW / tw); font(ctx, size); tw = ctx.measureText(c.text).width; }
    const f = (T - c.t0) * FPS, sc = f < 1 ? 1.1 : (f < 2 ? 1.04 : 1), y = 968;
    ctx.save(); ctx.translate(540, y); ctx.scale(sc, sc); ctx.translate(-540, -y);
    let x = 540 - tw / 2; const sp = ctx.measureText(' ').width;
    ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
    const parts = toks.map((t) => { const w = ctx.measureText(t).width, p = {t, x, num: /\d/.test(t)}; x += w + sp; return p; });
    parts.forEach((p) => { ctx.fillStyle = INK; ctx.fillText(p.t, p.x, y + 9); ctx.lineWidth = 18; ctx.strokeStyle = INK; ctx.strokeText(p.t, p.x, y); });
    parts.forEach((p) => { ctx.fillStyle = p.num ? GOLD : CREAM; ctx.fillText(p.t, p.x, y); });
    ctx.restore();
  }

  function bg(ctx) {
    ctx.fillStyle = '#1B1420'; ctx.fillRect(0, 0, W, H);
    // a stepped glow behind the host, on the host's pixel grid
    [[470, '#221928'], [380, '#281E30'], [290, '#2E2337']].forEach(([r, c]) => { ctx.fillStyle = c;
      for (let y = -r; y < r; y += PIX) { const hw = Math.floor(Math.sqrt(r * r - y * y) / PIX) * PIX; ctx.fillRect(HX - hw, HEADY + 40 + y, hw * 2, PIX); } });
  }

  window.drawAt = function (T) {
    const ctx = document.getElementById('c').getContext('2d'); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1;
    bg(ctx);
    const b = beatAt(T);
    if (b.kind === 'card') card(ctx, b, T); else if (b.kind === 'split') split(ctx, b, T); else fileShot(ctx, b, T);
    host(ctx, T);
    captions(ctx, T);
    return true;
  };

  async function boot() {
    for (const L of SH.lessons) await new Promise((ok, bad) => { const im = new Image(); im.onload = () => { imgs[L.slug] = im; ok(); }; im.onerror = () => bad(new Error('missing ' + L.file + ' (run capture.py)')); im.src = L.file; });
    await new Promise((ok, bad) => { const im = new Image(); im.onload = () => { imgs.results = im; ok(); }; im.onerror = () => bad(new Error('missing shots/results.png (run capture.py)')); im.src = 'shots/results.png'; });
    await document.fonts.ready;
    await Promise.all(['700 40px Poppins', '600 40px Poppins', '600 40px Inter', '700 40px Inter'].map((f) => document.fonts.load(f)));
    window.DURATION = DUR; window.SFX = SFX; window.BEATS = BEATS; window.CAPS = caps; window.STAGE = {WIN, PIX, HS, HEADY, hasMouth: !!M};
    window.READY = true; drawAt(Number(q.get('t') || 0));
  }
  boot().catch((e) => { window.BOOT_ERROR = String(e && e.stack || e); console.error(e); });
})();
