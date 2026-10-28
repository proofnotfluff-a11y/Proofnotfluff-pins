// The player: the clock, the cues, the speech box and the host. anim.py opens stage.html?v=<slug> in Chromium and calls
// drawAt(t) for every frame; the same page previews in a browser with ?play=1.
(function () {
  const W = 1080, H = 1920;
  const q = new URLSearchParams(location.search);
  const slug = q.get('v');
  const base = `../videos/${slug}/`;
  const scripts = [base + '04_scene/data.js', base + '03_cues/cues.js', base + '02_transcript/words.js', base + '04_scene/scene.js'];
  const imgs = {};
  let cues = [], byId = {}, words = [], phrases = [], look, lowCanvas, pal = null;

  function load(src) { return new Promise((ok, bad) => { const s = document.createElement('script'); s.src = src + '?' + Date.now(); s.onload = ok; s.onerror = () => bad(new Error('missing ' + src)); document.head.appendChild(s); }); }

  function buildPhrases(ws) {
    const out = []; let cur = [];
    const ctx = document.createElement('canvas').getContext('2d');
    ctx.font = `600 46px ${look.font.body}`;
    const fits = (arr) => {
      const lines = []; let line = '';
      arr.forEach((w) => { const t = line ? line + ' ' + w.w : w.w; if (line && ctx.measureText(t).width > 520) { lines.push(line); line = w.w; } else line = t; });
      lines.push(line); return lines.length <= 2;
    };
    ws.forEach((w, i) => {
      const prev = ws[i - 1];
      if (cur.length && (prev && w.start - prev.end > 0.55 || !fits(cur.concat([w])))) { out.push(cur); cur = []; }
      cur.push(w);
      if (/[.!?]$/.test(w.w) && cur.length >= 3) { out.push(cur); cur = []; }
    });
    if (cur.length) out.push(cur);
    return out.map((ws2, i) => ({words: ws2, t0: ws2[0].start - 0.05, t1: out[i + 1] ? out[i + 1][0].start - 0.05 : ws2[ws2.length - 1].end + 0.6}));
  }

  function speechBox(k, T) {
    const ph = phrases.find((p) => T >= p.t0 && T < p.t1);
    const x = 300, y = 1088, w = 628, h = 150;
    const ctx = k.ctx;
    if (!ph) return;
    k.shape(k.rectPts(x, y, w, h, look.name === 'pixel' ? 0 : 22), {fill: 'bubble', stroke: look.name === 'clean' ? 'line' : null, lw: 2});
    k.shape([[x + 2, y + 98], [x - 36, y + 120], [x + 2, y + 122]], {fill: 'bubble', line: false});
    const tag = k.chip(window.SCENE.host_name || 'Snow', x + 20, y - 30, {size: 24, fill: 'tag', color: 'tagText'});
    ctx.save(); ctx.textBaseline = 'top'; try { ctx.letterSpacing = '0px'; } catch (e) {}
    // lay the phrase out at 46 px; if it would need a third line, step the size down until it fits in two
    let fs = 46, lh = 56;
    const lay = (size) => { ctx.font = `600 ${size}px ${look.font.body}`; const sp = ctx.measureText(' ').width; let cx2 = x + 26, rows = 1;
      ph.words.forEach((wd) => { const ww = ctx.measureText(wd.w).width; if (cx2 + ww > x + w - 24 && cx2 > x + 26) { cx2 = x + 26; rows++; } cx2 += ww + sp; }); return rows; };
    while (fs > 34 && lay(fs) > 2) fs -= 2;
    lh = Math.round(fs * 1.22);
    ctx.font = `600 ${fs}px ${look.font.body}`;
    let cx = x + 26, cy = y + (h - 2 * lh) / 2 + 4; const maxX = x + w - 24;
    const space = ctx.measureText(' ').width;
    ph.words.forEach((wd) => {
      const ww = ctx.measureText(wd.w).width;
      if (cx + ww > maxX && cx > x + 26) { cx = x + 26; cy += lh; }
      const on = T >= wd.start && T < wd.end + 0.05, said = T >= wd.start;
      if (on) { k.shape(k.rectPts(cx - 8, cy - 5, ww + 16, lh, look.name === 'pixel' ? 0 : 8), {fill: 'pill', line: false}); }
      ctx.fillStyle = on ? k.C.pillText : (said ? k.C.bubbleText : (look.lineArt || look.name === 'pixel' ? k.C.muted : '#9AA0AD'));
      ctx.fillText(wd.w, cx, cy);
      cx += ww + space;
    });
    ctx.restore();
  }

  function quantize(c) {
    const g = c.getContext('2d'); const im = g.getImageData(0, 0, c.width, c.height); const d = im.data;
    if (!pal) pal = look.palette.map((h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)]);
    for (let i = 0; i < d.length; i += 4) {
      let best = 0, bd = 1e9; const r = d[i], gg = d[i + 1], b = d[i + 2];
      for (let j = 0; j < pal.length; j++) { const p = pal[j]; const dd = (p[0] - r) ** 2 + (p[1] - gg) ** 2 + (p[2] - b) ** 2; if (dd < bd) { bd = dd; best = j; } }
      d[i] = pal[best][0]; d[i + 1] = pal[best][1]; d[i + 2] = pal[best][2]; d[i + 3] = 255;
    }
    g.putImageData(im, 0, 0);
  }

  const env = {
    data: null,
    cue: (id) => { const c = byId[id]; if (!c) throw new Error('no cue ' + id); return c; },
    talking: (T) => words.some((w) => T >= w.start - 0.02 && T < w.end + 0.06),
    img: (n) => imgs[n],
  };

  window.drawAt = function (T) {
    const main = document.getElementById('c'); const mctx = main.getContext('2d');
    const pixel = look.scale !== 1;
    const target = pixel ? lowCanvas : main; const ctx = target.getContext('2d');
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1;
    if (pixel) ctx.setTransform(look.scale, 0, 0, look.scale, 0, 0);
    const k = Kit.make(ctx, look, T, env);
    k.bg();
    const tops = cues.filter((c) => c.level === 0);
    let sec = tops[0]; tops.forEach((c) => { if (T >= c.t) sec = c; });
    const fn = window.SCENE.sections[sec.id];
    let ret = {};
    ctx.save();
    const into = T - sec.t;
    if (sec !== tops[0] && into < 0.28) { const e = k.easeOut(into / 0.28); ctx.translate((1 - e) * 140, 0); ctx.globalAlpha = 0.25 + 0.75 * e; }
    if (fn) ret = fn(k, T, sec) || {};
    ctx.restore();
    if (ret.host !== false && window.SCENE.host !== false) {
      const hp = typeof ret.hostPose === 'string' ? ret.hostPose : (k.talking() ? 'talk' : 'stand');
      k.snow(160, 1246, {scale: 0.6, pose: hp, at: ret.hostAt, face: 1});
    }
    speechBox(k, T);
    if (pixel) {
      quantize(lowCanvas);
      mctx.setTransform(1, 0, 0, 1, 0, 0); mctx.imageSmoothingEnabled = false;
      mctx.drawImage(lowCanvas, 0, 0, W, H);
    }
    return true;
  };

  async function boot() {
    for (const s of scripts) await load(s);
    const lk = q.get('look') || window.SCENE.look || 'clean';
    look = window.LOOKS[lk];
    env.data = window.DATA;
    cues = window.CUES.cues; cues.forEach((c) => { byId[c.id] = c; });
    words = (window.WORDS.words || []);
    const c = document.getElementById('c'); c.width = W; c.height = H;
    if (look.scale !== 1) { lowCanvas = document.createElement('canvas'); lowCanvas.width = Math.round(W * look.scale); lowCanvas.height = Math.round(H * look.scale); }
    for (const n of (window.SCENE.images || [])) {
      await new Promise((ok) => { const im = new Image(); im.onload = () => { imgs[n] = im; ok(); }; im.onerror = ok; im.src = base + '04_scene/assets/' + n + '.png'; });
    }
    await document.fonts.ready;
    await Promise.all(['700 40px Poppins', '600 40px Poppins', '600 40px Inter', '700 40px Inter'].map((f) => document.fonts.load(f)));
    phrases = buildPhrases(words);   // after the fonts load, so the line breaks match what is drawn
    window.DURATION = window.CUES.duration;
    window.READY = true;
    if (q.get('play')) { const t0 = performance.now(); const tick = () => { const t = (performance.now() - t0) / 1000; drawAt(t % window.DURATION); requestAnimationFrame(tick); }; tick(); }
    else drawAt(Number(q.get('t') || 0));
  }
  boot().catch((e) => { window.BOOT_ERROR = String(e && e.stack || e); console.error(e); });
})();
