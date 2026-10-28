// The player: the clock, the cues, the speech box and the host. anim.py opens stage.html?v=<slug> in Chromium and calls
// drawAt(t) for every frame; the same page previews in a browser with ?play=1.
(function () {
  const W = 1080, H = 1920;
  const q = new URLSearchParams(location.search);
  const slug = q.get('v');
  const base = `../videos/${slug}/`;
  const scripts = [base + '04_scene/data.js', base + '03_cues/cues.js', base + '02_transcript/words.js', base + '04_scene/scene.js'];
  const imgs = {};
  let cues = [], byId = {}, words = [], phrases = [], look, lowCanvas, hostCanvas, pal = null;

  function load(src) { return new Promise((ok, bad) => { const s = document.createElement('script'); s.src = src + '?' + Date.now(); s.onload = ok; s.onerror = () => bad(new Error('missing ' + src)); document.head.appendChild(s); }); }

  function buildPhrases(ws) {
    const out = []; let cur = [];
    const ctx = document.createElement('canvas').getContext('2d');
    ctx.font = `600 46px ${look.font.body}`;
    const fitW = look.bitmap ? 470 : 520, maxL = look.bitmap ? 3 : 2;
    const fits = (arr) => {
      const lines = []; let line = '';
      arr.forEach((w) => { const t = line ? line + ' ' + w.w : w.w; if (line && ctx.measureText(t).width > fitW) { lines.push(line); line = w.w; } else line = t; });
      lines.push(line); return lines.length <= maxL;
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
    if (!ph) return;
    const arcade = !!look.bitmap;
    const B = arcade ? {x: 372, y: 1046, w: 560, h: 190} : {x: 300, y: 1088, w: 628, h: 150};
    const {x, y, w, h} = B;
    const r = look.name === 'pixel' || arcade ? 0 : (look.name === 'desk' ? 6 : 22);
    if (arcade) { k.shape(k.rectPts(x + 10, y + 10, w, h, 0), {fill: '#120D14', line: false, alpha: 0.6}); }
    k.shape(k.rectPts(x, y, w, h, r), {fill: 'bubble', stroke: look.name === 'clean' ? 'line' : null, lw: 2});
    if (arcade) k.shape(k.rectPts(x + 6, y + 6, w - 12, h - 12, 0), {stroke: 'bubbleText', lw: 6, line: false});
    k.shape([[x + 2, y + h - 70], [x - 40, y + h - 40], [x + 2, y + h - 30]], {fill: 'bubble', line: false});
    k.chip(window.SCENE.host_name || 'Snow', x + 24, y - 34, {size: arcade ? 30 : 24, fill: 'tag', color: 'tagText'});
    // lay the phrase out; step the size down until it fits the box
    let fs = arcade ? 39 : 46;
    const pad = arcade ? 30 : 26, maxX = x + w - pad;
    const lay = (size) => { const sp = k.measure(' ', {size, weight: 600, font: 'body'}); let cx2 = x + pad, rows = 1;
      ph.words.forEach((wd) => { const ww = k.measure(wd.w, {size, weight: 600, font: 'body'}); if (cx2 + ww > maxX && cx2 > x + pad) { cx2 = x + pad; rows++; } cx2 += ww + sp; }); return rows; };
    const maxRows = arcade ? 3 : 2;
    while (fs > 30 && lay(fs) > maxRows) fs -= arcade ? 3 : 2;
    const rows = lay(fs);
    const lh = arcade ? Math.round(fs * 1.18) : Math.round(fs * 1.22);
    const sp = k.measure(' ', {size: fs, weight: 600, font: 'body'});
    let cx = x + pad, cy = y + (h - rows * lh) / 2 + 4;
    ph.words.forEach((wd) => {
      const ww = k.measure(wd.w, {size: fs, weight: 600, font: 'body'});
      if (cx + ww > maxX && cx > x + pad) { cx = x + pad; cy += lh; }
      const on = T >= wd.start && T < wd.end + 0.05, said = T >= wd.start;
      if (arcade) {   // a game dialog box: words type on as they are said, the spoken word in the accent
        if (said) k.text(wd.w, cx, cy, {size: fs, weight: 600, font: 'body', color: on ? 'tag' : 'bubbleText'});
      } else {
        if (on) k.shape(k.rectPts(cx - 8, cy - 5, ww + 16, lh, look.name === 'pixel' ? 0 : 8), {fill: 'pill', line: false});
        k.text(wd.w, cx, cy, {size: fs, weight: 600, font: 'body', color: on ? 'pillText' : (said ? 'bubbleText' : (look.lineArt || look.name === 'pixel' ? 'muted' : '#9AA0AD'))});
      }
      cx += ww + sp;
    });
    if (arcade && (T * 2) % 1 < 0.5) k.shape([[x + w - 52, y + h - 40], [x + w - 28, y + h - 40], [x + w - 40, y + h - 26]], {fill: 'bubbleText', line: false});
  }

  // the game HUD: lesson tag and a level bar, one block per section, filling as the lesson plays (a reason to stay)
  function hud(k, T, tops, sec) {
    const h = window.SCENE.hud; if (!h) return;
    const x = 72, y = 168, n = tops.length, gap = 8, lw = k.measure(h, {size: 30}) + 36, bw = (936 - lw - gap * (n - 1)) / n;
    k.shape(k.rectPts(x - 6, y - 6, 948, 52, 0), {fill: '#120D14', line: false, alpha: 0.7});
    k.text(h, x + 6, y + 2, {size: 30, color: 'accent2'});
    tops.forEach((c, i) => {
      const bx = x + lw + i * (bw + gap), done = T >= c.end, on = c === sec;
      k.shape(k.rectPts(bx, y + 6, bw, 28, 0), {fill: '#3D2E45', line: false});
      const f = done ? 1 : (on ? k.clamp((T - c.t) / Math.max(0.1, c.end - c.t)) : 0);
      if (f > 0) k.shape(k.rectPts(bx, y + 6, bw * f, 28, 0), {fill: on ? 'accent' : 'teal', line: false});
    });
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
    const moving = !!look.bitmap || window.SCENE.motion;
    if (!moving && sec !== tops[0] && into < 0.28) { const e = k.easeOut(into / 0.28); ctx.translate((1 - e) * 140, 0); ctx.globalAlpha = 0.25 + 0.75 * e; }
    let zoom = 1 + 0.03 * Math.min(1, into / Math.max(1, sec.end - sec.t));   // a slow push-in through each section
    let fx = 540, fy = 620, sx = 0, sy = 0;
    if (moving) {
      // the zoom ladder: every beat inside a section steps the camera in a little, with a springy overshoot
      const beats = cues.filter((c) => c.level > 0 && c.t > sec.t && c.t <= T && c.t < sec.end);
      beats.forEach((c, i) => { if (i < 4) zoom += 0.028 * k.back((T - c.t) / 0.3); });
      const fo = (window.SCENE.focus || {});
      const last = beats.length ? beats[beats.length - 1] : sec;
      if (fo[last.id] || fo[sec.id]) { const [ax, ay] = fo[last.id] || fo[sec.id]; const q = k.easeOut((T - last.t) / 0.6); fx = 540 + (ax - 540) * 0.35 * q; fy = 620 + (ay - 620) * 0.35 * q; }
      // a short shake on every stamp
      cues.forEach((c) => { const d = T - c.t; if (c.sfx === 'stamp' && d >= 0 && d < 0.32) { const a = 7 * (1 - d / 0.32); sx += Math.sin(T * 91) * a; sy += Math.cos(T * 73) * a; } });
      // a section opens with a hard punch-in that settles
      if (sec !== tops[0]) zoom += 0.06 * (1 - k.easeOut(into / 0.5));
    }
    ctx.translate(sx, sy);
    ctx.translate(fx, fy); ctx.scale(zoom, zoom); ctx.translate(-fx, -fy);
    if (fn) ret = fn(k, T, sec) || {};
    ctx.restore();
    if (ret.host !== false && window.SCENE.host !== false) {
      const hp = typeof ret.hostPose === 'string' ? ret.hostPose : (k.talking() ? 'talk' : 'stand');
      if (look.pixelHost && !pixel) {   // the pixel cast over real screens (the gold standard's house look)
        const ph = look.pixelHost;
        if (!hostCanvas) { hostCanvas = document.createElement('canvas'); hostCanvas.width = Math.round(W * ph); hostCanvas.height = Math.round(H * ph); }
        const hctx = hostCanvas.getContext('2d'); hctx.setTransform(1, 0, 0, 1, 0, 0); hctx.clearRect(0, 0, hostCanvas.width, hostCanvas.height);
        hctx.setTransform(ph, 0, 0, ph, 0, 0);
        Kit.make(hctx, look, T, env).snow(160, 1246, {scale: 0.6, pose: hp, at: ret.hostAt, face: 1});
        const id = hctx.getImageData(0, 0, hostCanvas.width, hostCanvas.height), d = id.data;
        for (let i = 3; i < d.length; i += 4) d[i] = d[i] > 110 ? 255 : 0;   // hard pixel edges
        hctx.putImageData(id, 0, 0);
        ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.imageSmoothingEnabled = false; ctx.drawImage(hostCanvas, 0, 0, W, H); ctx.restore();
      } else if (look.bitmap) k.snow(190, 1246, {scale: 0.86, pose: hp, at: ret.hostAt, face: 1});
      else k.snow(160, 1246, {scale: 0.6, pose: hp, at: ret.hostAt, face: 1});
    }
    speechBox(k, T);
    if (moving) {
      hud(k, T, tops, sec);
      // room to room: pixel blinds close and open again (0.42 s), hiding the cut
      if (sec !== tops[0] && into < 0.42) {
        for (let i = 0; i < 16; i++) {
          const q = into < 0.12 ? 1 : 1 - k.easeOut((into - 0.12 - i * 0.008) / 0.26), w = W * k.clamp(q);
          ctx.fillStyle = '#120D14'; ctx.fillRect(i % 2 ? W - w : 0, i * 120, w, 120);
        }
      }
    }
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
