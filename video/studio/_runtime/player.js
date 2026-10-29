// The player: the clock, the cues, the speech box and the host. anim.py opens stage.html?v=<slug> in Chromium and calls
// drawAt(t) for every frame; the same page previews in a browser with ?play=1.
(function () {
  const W = 1080, H = 1920;
  const q = new URLSearchParams(location.search);
  const slug = q.get('v');
  const base = `../videos/${slug}/`;
  const scripts = [base + '04_scene/data.js', base + '03_cues/cues.js', base + '02_transcript/words.js', base + '04_scene/scene.js'];
  const optional = [base + '02_transcript/mouth.js'];   // lip sync from the voice (anim.py mouth); without it the mouth moves on a sine
  const imgs = {};
  const FPS = 30, FREEZE = 3, LEAD = 6 / FPS, CAM_RATE = 8, SHAKE_GAP = 10;
  let cues = [], byId = {}, words = [], phrases = [], look, lowCanvas, hostCanvas, pal = null;
  let stamps = [], shakes = [], survey = null;

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
      if (cur.length && (prev && w.start - prev.end > 0.55 || !fits(cur.concat([w])))) {
        // break at a clause end when there is one, and never start a page on a unit ("percent", "million", "hours")
        let cut = cur.length;
        for (let j = cur.length - 2; j >= 1; j--) if (/[,;:]$/.test(cur[j].w)) { cut = j + 1; break; }
        if (cut === cur.length && /^(percent|million|hours?|minutes?|dollars?)\b/i.test(w.w) && cur.length > 1) cut = cur.length - 1;
        out.push(cur.slice(0, cut)); cur = cur.slice(cut);
      }
      cur.push(w);
      if (/[.!?]$/.test(w.w) && cur.length >= 3) { out.push(cur); cur = []; }
    });
    if (cur.length) out.push(cur);
    // never leave one word alone in the box: join it to the phrase before when it fits, else to the one after
    for (let i = 0; i < out.length; i++) {
      if (out[i].length !== 1 || out.length < 2) continue;
      if (i > 0 && fits(out[i - 1].concat(out[i]))) { out[i - 1] = out[i - 1].concat(out[i]); out.splice(i, 1); i--; }
      else if (i + 1 < out.length && fits(out[i].concat(out[i + 1]))) { out[i + 1] = out[i].concat(out[i + 1]); out.splice(i, 1); i--; }
    }
    return out.map((ws2, i) => ({words: ws2, t0: ws2[0].start - 0.05, t1: out[i + 1] ? out[i + 1][0].start - 0.05 : ws2[ws2.length - 1].end + 0.6}));
  }

  function speechBox(k, T) {
    let i = phrases.findIndex((p) => T >= p.t0 && T < p.t1);
    // between takes the box keeps the last full line until the next word is said, so it never sits empty
    if (i > 0 && T < phrases[i].words[0].start) i -= 1;
    const ph = phrases[i];
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
    let cx = x + pad, cy = y + 26;   // every page starts on the same top line, so words never jump between pages
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
    data: null, words: [], duration: 600, mouth: null,
    cue: (id) => { const c = byId[id]; if (!c) throw new Error('no cue ' + id); return c; },
    talking: (T) => words.some((w) => T >= w.start - 0.02 && T < w.end + 0.06),
    img: (n) => imgs[n],
  };

  // ---- motion helpers. Every frame is drawn on its own, in any order (anim.py renders random access), so each effect
  // below is a pure function of T: nothing carries over from the frame before.
  const sectionAt = (tops, t) => { let s = tops[0]; tops.forEach((c) => { if (t >= c.t) s = c; }); return s; };
  // smooth value noise, about 14 steps a second, -1 to 1
  const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
  const vnoise = (x, seed) => { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return (hash(i + seed * 57.3) * (1 - u) + hash(i + 1 + seed * 57.3) * u) * 2 - 1; };
  // trauma: each stamp adds some (0.5; SCENE.trauma = {cueId: 0.8} for the one big verdict) when its freeze ends, at most
  // one shaking stamp in 10 s; it drains at 3 a second, and the shake is trauma squared, so small hits barely move the frame
  function trauma(T) {
    let tr = 0, tl = -1e9;
    for (const e of shakes) { if (e.t > T) break; tr = Math.min(1, Math.max(0, tr - 3 * (e.t - tl)) + e.a); tl = e.t; }
    return Math.max(0, tr - 3 * (T - tl));
  }
  // the scene's clock: it stops for 3 frames when a stamp lands (the hit-stop) and shivers 1 low-res pixel
  function sceneClock(T, sec) {
    for (const c of stamps) { const f = (T - c.t) * FPS + 0.005; if (c.t >= sec.t && f >= 0 && f < FREEZE) return {Ts: c.t, shiver: Math.floor(f) % 2 ? -1 : 1}; }
    return {Ts: T, shiver: 0};
  }
  // the camera leads the beat: it starts toward each beat's focus 6 frames before the cue and eases in at 1 - exp(-8 dt).
  // A target that steps is the sum of its steps, each eased from the moment it starts, which is exactly the frame-by-frame
  // ease, worked out from the time alone.
  function camera(k, T, sec) {
    const fo = window.SCENE.focus || {}, into = T - sec.t;
    const aim = (id) => { const f = fo[id] || fo[sec.id]; return f ? [540 + (f[0] - 540) * 0.2, 300 + (f[1] - 300) * 0.2] : [540, 300]; };
    let zoom = 1 + 0.03 * Math.min(1, into / Math.max(1, sec.end - sec.t));   // a slow push-in through each section
    const beats = cues.filter((c) => c.level > 0 && c.t > sec.t && c.t < sec.end);
    // the zoom ladder: every beat inside a section steps the camera in a little, with a springy overshoot
    beats.filter((c) => c.t <= T).forEach((c, i) => { if (i < 3) zoom += 0.018 * k.back((T - c.t) / 0.3); });
    let prev = aim(sec.id); const at = prev.slice();
    for (const b of beats) {
      const t0 = Math.max(sec.t, b.t - LEAD); if (t0 > T) break;
      const v = aim(b.id), w = 1 - Math.exp(-CAM_RATE * (T - t0));
      at[0] += (v[0] - prev[0]) * w; at[1] += (v[1] - prev[1]) * w; prev = v;
    }
    return {zoom, fx: at[0], fy: at[1]};
  }
  // where the pose last changed (talking and standing count as one idle pose), sampled at boot every 0.2 s by running
  // the scene on a tiny canvas; the same pass notes which room each section draws, for the room's own transition
  function runSurvey() {
    const step = 0.2, n = Math.ceil(window.DURATION / step) + 1, fam = [], runStart = [], rooms = {};
    const cv = document.createElement('canvas'); cv.width = cv.height = 4; const g = cv.getContext('2d');
    const tops = cues.filter((c) => c.level === 0), boxes = window.__boxes; window.__boxes = null;
    for (let i = 0; i < n; i++) {
      const t = i * step, sec = sectionAt(tops, t), fn = window.SCENE.sections[sec.id];
      if (g.reset) g.reset(); g.setTransform(0.004, 0, 0, 0.004, 0, 0);
      const kk = Kit.make(g, look, t, env), room0 = kk.room; let room = null;
      kk.room = (name, o) => { if (!room) room = name; return room0(name, o); };
      let ret = {};
      try { ret = (fn && fn(kk, t, sec)) || {}; } catch (e) { ret = {}; }
      if (room && !rooms[sec.id]) rooms[sec.id] = room;
      const pose = ret.host === false || window.SCENE.host === false ? 'none' : (typeof ret.hostPose === 'string' ? ret.hostPose : (env.talking(t) ? 'talk' : 'stand'));
      fam.push(pose === 'talk' || pose === 'stand' ? 'idle' : pose);
      runStart.push(i && fam[i] === fam[i - 1] ? runStart[i - 1] : t);
    }
    window.__boxes = boxes;
    return {step, fam, runStart, rooms};
  }
  function idleOf(T, pose) {
    if (!survey) return {};
    const i = Math.max(0, Math.min(survey.fam.length - 1, Math.floor(T / survey.step)));
    const f = pose === 'talk' || pose === 'stand' ? 'idle' : pose;
    return f === survey.fam[i] ? {idle: T - survey.runStart[i], idleSeed: survey.runStart[i]} : {idle: 0, idleSeed: 0};
  }
  // room to room: 12 frames, 5 closing over the old room, the cut, 1 held shut, 6 opening on the new one. The new room
  // picks the move: blinds (workshop), a chalk wipe (blackboard), a garage door (garage), an iris (framing); blinds otherwise.
  // A section names its room with SCENE.rooms = {sectionId: 'garage'}, or the player reads its k.room call.
  // SCENE.transitions = {sectionId: 'levelselect' | 'dissolve' | 'gameover'} picks a set piece's move (sets.js) instead.
  const STYLE = {workshop: 'blinds', blackboard: 'chalk', garage: 'door', framing: 'iris'};
  function transition(ctx, T, tops, sec, U, head) {
    const i = tops.indexOf(sec), nx = tops[i + 1];
    let u = null, to = null;
    const E = 0.005;   // frame times arrive with rounding; a frame on the boundary counts as the later one
    if (nx && (T - nx.t) * FPS + E >= -5) { u = (T - nx.t) * FPS + E; to = nx; }
    else if (i > 0 && (T - sec.t) * FPS + E < 7) { u = (T - sec.t) * FPS + E; to = sec; }
    if (u == null) return;
    const q = u < 0 ? Math.pow(Math.max(0, (u + 6) / 6), 2) : (u < 1 ? 1 : Math.pow(1 - u / 7, 2));   // how shut: eases in, eases out
    if (q <= 0) return;
    const room = (window.SCENE.rooms || {})[to.id] || (survey && survey.rooms[to.id]);
    const style = (window.SCENE.transitions || {})[to.id] || STYLE[room] || 'blinds', closing = u < 0;
    const cell = Math.max(U, 3), sn = (v) => Math.round(v / cell) * cell;
    const fill = (c, x, y, w, h) => { if (w > 0 && h > 0) { ctx.fillStyle = c; ctx.fillRect(x, y, w, h); } };
    const ext = window.SETS && window.SETS.transitions[style];   // the set pieces' moves (sets.js): levelselect, dissolve, gameover
    if (ext) { ext(ctx, q, {closing, u, cell, W, H, fill, hash, head}); return; }
    if (style === 'blinds') {   // slats slide in from alternate sides over the old room, then back out
      for (let s = 0; s < 16; s++) {
        const qs = Math.max(0, Math.min(1, q * 1.3 - s * 0.02)), w = sn(W * qs);
        fill('#8C5A33', s % 2 ? W - w : 0, s * 120, w, 120); fill('#D9A066', s % 2 ? W - w : 0, s * 120, w, cell); fill('#6B4226', s % 2 ? W - w : 0, s * 120 + 120 - cell, w, cell);   // wooden slats, so it reads as a shutter, not a glitch
      }
    } else if (style === 'chalk') {   // a board eraser sweeps across on a slant, a dithered chalk-dust edge on its front
      const D = W + H * 0.5, B = 12 * cell, span = D + 2 * B;
      const front = closing || u < 1 ? q * span - B : (1 - q) * span - B;
      for (let y = 0; y < H; y += cell) {
        const off = y * 0.5;
        if (closing || u < 1) {   // covered where x + y/2 < front, dust just ahead of it
          const x1 = sn(Math.min(W, front - off));
          fill('#24453A', 0, y, x1, cell);
          for (let x = Math.max(0, x1); x < Math.min(W, x1 + B); x += cell) if (((x / cell) + (y / cell)) % 2 === 0 && hash(x * 0.13 + y * 0.71) < 1 - (x - x1) / B) fill(x - x1 < 2 * cell ? '#C9CCD3' : '#2F5A4A', x, y, cell, cell);
        } else {   // the same sweep carries on and uncovers the new board behind it
          const x0 = sn(Math.max(0, front - off + B));
          fill('#24453A', x0, y, W - x0, cell);
          for (let x = Math.max(0, x0 - B); x < Math.min(W, x0); x += cell) if (((x / cell) + (y / cell)) % 2 === 0 && hash(x * 0.13 + y * 0.71) < (x - x0 + B) / B) fill(x0 - x <= 2 * cell ? '#C9CCD3' : '#2F5A4A', x, y, cell, cell);
        }
      }
    } else if (style === 'door') {   // a roll-up door comes down over the old room and rolls back up
      const Y = sn(H * q);
      fill('#6B7080', 0, 0, W, Y);
      for (let y = Y - 96; y > -96; y -= 96) { fill('#4A4E5A', 0, y, W, 2 * cell); fill('#9AA0AD', 0, y + 2 * cell, W, cell); }
      fill('#2B2033', 0, Y - 4 * cell, W, 4 * cell); fill('#C9CCD3', W / 2 - 60, Y - 3 * cell, 120, 2 * cell);
    } else {   // an iris closes on the host's head and opens again, a circle drawn on the pixel grid
      const [cx, cy] = head, R = Math.hypot(Math.max(cx, W - cx), Math.max(cy, H - cy)) + cell, r = R * (1 - q);
      for (let y = 0; y < H; y += cell) {
        const dy = y + cell / 2 - cy;
        if (Math.abs(dy) >= r) { fill('#120D14', 0, y, W, cell); continue; }
        const half = sn(Math.sqrt(r * r - dy * dy));
        fill('#120D14', 0, y, sn(cx) - half, cell); fill('#120D14', sn(cx) + half, y, W - sn(cx) - half, cell);
      }
    }
  }

  // the end card (IMPROVE 000, Oct 29): once the last word has landed, a plum plate drops in on whole low-res pixels and
  // holds the ProofNotFluff lockup and the site, music only, to the end of the tail (anim.py cues gives every lesson 2.9 s
  // after the last word). The host and the dialog box step out under it. SCENE.endCard = false turns it off.
  // SCENE.sendLine adds the send line under the plate (a v2 lesson's call to action lives here, not in the voice).
  let END_T = 1e9;
  function endCard(k, T) {
    if (T < END_T) return false;
    const ctx = k.ctx, f = Math.floor((T - END_T) * FPS + 0.005);
    const P = (x, y, w, h, c) => { if (w > 0 && h > 0) { ctx.fillStyle = c; ctx.fillRect(Math.round(x) * 3, Math.round(y) * 3, Math.round(w) * 3, Math.round(h) * 3); } };
    const drop = Math.round(640 * Math.pow(1 - Math.min(1, f / 9), 3));   // low-res pixels still to fall
    ctx.save(); ctx.translate(0, -drop * 3);
    P(0, 0, 360, 640, '#2B2033'); P(0, 636, 360, 4, '#F7C873');
    for (let y = 8; y < 636; y += 16) P(0, y, 360, 1, '#3D2E45');   // faint scanlines, so the plate reads as a screen
    P(40, 96, 280, 172, '#120D14'); P(38, 94, 280, 172, '#3D2E45'); P(38, 94, 280, 1, '#7A3442'); P(38, 265, 280, 1, '#120D14');
    const fit = (s, sizes, maxW) => sizes.find((z) => k.measure(s, {size: z}) <= maxW) || sizes[sizes.length - 1];
    const z1 = fit('ProofNotFluff', [132, 99, 66], 780);
    k.text('ProofNotFluff', 534, 380, {size: z1, color: '#FFF7EA', align: 'center', lint: drop === 0});
    k.text('proofnotfluff.com', 534, 576, {size: 66, color: '#F7C873', align: 'center', lint: drop === 0});
    const uw = Math.round(k.measure('proofnotfluff.com', {size: 66}) / 3), ux = 178 - Math.round(uw / 2);
    if (f >= 12) P(ux, 216, Math.min(uw, (f - 12) * 8), 2, '#F7C873');   // the site's underline draws on
    k.text('Lessons for trade owners', 534, 690, {size: 39, color: '#E6D3BC', align: 'center', lint: drop === 0});
    // the send line (Lead Clinic v2, Oct 29): a v2 lesson says no call to action, so the card carries it, word-wrapped
    // onto the dark floor under Snow's feet (above the apps' caption band), where nothing stands in front of it
    const send = window.SCENE.sendLine;
    if (send) {
      const words = String(send).split(/\s+/), rows = [''];
      words.forEach((w) => { const s = rows[rows.length - 1] ? rows[rows.length - 1] + ' ' + w : w; if (k.measure(s, {size: 45}) > 900 && rows[rows.length - 1]) rows.push(w); else rows[rows.length - 1] = s; });
      rows.forEach((s, i) => k.text(s, 534, 1380 + i * 57, {size: 45, color: '#FFF7EA', align: 'center', lint: drop === 0 && f >= 12}));
    }
    // a twinkle walks the plate's corners, one every 8 frames, so the held card is never a still picture
    const pts = [[46, 102], [310, 102], [310, 258], [46, 258]], g = f >= 10 ? Math.floor((f - 10) / 8) % 4 : -1;
    if (g >= 0) { const [x, y] = pts[g], s = [0, 1, 2, 1][Math.floor(f / 2) % 4]; P(x, y, 1, 1, '#FFF7EA'); for (let i = 1; i <= s; i++) { P(x - i, y, 1, 1, '#FFF7EA'); P(x + i, y, 1, 1, '#FFF7EA'); P(x, y - i, 1, 1, '#FFF7EA'); P(x, y + i, 1, 1, '#FFF7EA'); } }
    // Snow waves goodbye on a strip of floor under the plate
    P(0, 418, 360, 6, '#3D2E45'); P(0, 424, 360, 212, '#1B1420'); for (let x = (f >> 2) % 24 - 24; x < 360; x += 24) P(x, 430, 12, 2, '#2B2033');
    k.snow(540, 1254, {scale: 0.86, pose: 'wave', face: 1});
    ctx.restore();
    return true;
  }

  window.drawAt = function (T) {
    const main = document.getElementById('c'); const mctx = main.getContext('2d');
    const pixel = look.scale !== 1;
    const target = pixel ? lowCanvas : main; const ctx = target.getContext('2d');
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1;
    if (pixel) ctx.setTransform(look.scale, 0, 0, look.scale, 0, 0);
    const k = Kit.make(ctx, look, T, env);
    k.bg();
    const tops = cues.filter((c) => c.level === 0);
    const sec = sectionAt(tops, T);
    const fn = window.SCENE.sections[sec.id];
    const moving = !!look.bitmap || window.SCENE.motion;
    const U = pixel ? 1 / look.scale : 1, snap = (v) => Math.round(v / U) * U;   // one low-res pixel, in frame units
    const {Ts, shiver} = moving ? sceneClock(T, sec) : {Ts: T, shiver: 0};
    const ks = Ts === T ? k : Kit.make(ctx, look, Ts, env);   // during a hit-stop the scene draws at the frozen time
    let ret = {};
    ctx.save();
    const into = Ts - sec.t;
    if (!moving && sec !== tops[0] && into < 0.28) { const e = k.easeOut(into / 0.28); ctx.translate((1 - e) * 140, 0); ctx.globalAlpha = 0.25 + 0.75 * e; }
    let zoom = 1 + 0.03 * Math.min(1, into / Math.max(1, sec.end - sec.t)), fx = 540, fy = 300, sx = 0, sy = 0;   // zoom from the top band, so headers never climb under the Reel's top bar
    if (moving) {
      ({zoom, fx, fy} = camera(ks, Ts, sec));
      // a section opens with a hard punch-in that settles
      if (sec !== tops[0]) zoom += 0.06 * (1 - k.easeOut(into / 0.5));
      // pixel art never scales by a fraction: a 1.03x zoom resamples the low-res grid every frame, so lines swell and
      // thin and the set seems to swim (Todd, Oct 28: "the tile lines just keep moving"). The pixel looks hold the
      // camera still; the motion lives in the things on screen (slams, stamps, slides, the host).
      if (look.bitmap && !window.SCENE.zoom) zoom = 1;
      // the trauma shake: smooth noise, whole low-res pixels, at most 3
      const tr = trauma(T), amp = 3 * U * tr * tr;
      if (amp > 0) { sx = vnoise(T * 14, 1) * amp; sy = vnoise(T * 14, 2) * amp; }
      sx += shiver * U;
    }
    // the camera, its position on whole low-res pixels so the grid never swims
    ctx.translate(moving ? snap(sx + fx * (1 - zoom)) : fx * (1 - zoom), moving ? snap(sy + fy * (1 - zoom)) : fy * (1 - zoom)); ctx.scale(zoom, zoom);
    if (fn) ret = fn(ks, Ts, sec) || {};
    ctx.restore();
    let head = [540, 760];
    const ending = look.bitmap && window.SCENE.endCard !== false && T >= END_T;
    if (ending) { ret.host = false; ret.speech = false; }
    if (ret.host !== false && window.SCENE.host !== false) {
      const hp = typeof ret.hostPose === 'string' ? ret.hostPose : (k.talking() ? 'talk' : 'stand');
      const life = idleOf(T, hp);
      if (look.pixelHost && !pixel) {   // the pixel cast over real screens (the gold standard's house look)
        const ph = look.pixelHost;
        if (!hostCanvas) { hostCanvas = document.createElement('canvas'); hostCanvas.width = Math.round(W * ph); hostCanvas.height = Math.round(H * ph); }
        const hctx = hostCanvas.getContext('2d'); hctx.setTransform(1, 0, 0, 1, 0, 0); hctx.clearRect(0, 0, hostCanvas.width, hostCanvas.height);
        hctx.setTransform(ph, 0, 0, ph, 0, 0);
        Kit.make(hctx, look, T, env).snow(160, 1246, Object.assign({scale: 0.6, pose: hp, at: ret.hostAt, face: 1}, life));
        head = [162, 1246 - 384 * 0.6];
        const id = hctx.getImageData(0, 0, hostCanvas.width, hostCanvas.height), d = id.data;
        for (let i = 3; i < d.length; i += 4) d[i] = d[i] > 110 ? 255 : 0;   // hard pixel edges
        hctx.putImageData(id, 0, 0);
        ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.imageSmoothingEnabled = false; ctx.drawImage(hostCanvas, 0, 0, W, H); ctx.restore();
      } else if (look.bitmap) {
        const hx = ret.hostX || 190, hs = ret.hostScale || 0.86;
        k.snow(hx, 1246, Object.assign({scale: hs, pose: hp, at: ret.hostAt, face: 1}, life));
        head = [hx + 4 * hs, 1246 - 384 * hs];
        if (window.__boxes) window.__boxes.push({s: 'HOST', x0: hx - 95 * hs, y0: 1246 - 490 * hs, x1: hx + 95 * hs, y1: 1246, a: 1, tag: 'host'});
      }
      else { k.snow(160, 1246, Object.assign({scale: 0.6, pose: hp, at: ret.hostAt, face: 1}, life)); head = [162, 1246 - 384 * 0.6]; }
    }
    window.__tag = 'dialog';
    if (ret.speech !== false) { speechBox(k, T); const ph = phrases.find((p) => T >= p.t0 && T < p.t1);
      if (window.__boxes && ph) window.__boxes.push({s: 'DIALOG', x0: look.bitmap ? 372 : 300, y0: (look.bitmap ? 1046 : 1088) - 40, x1: (look.bitmap ? 932 : 928), y1: look.bitmap ? 1236 : 1238, a: 1, tag: 'dialogbox'}); }
    window.__tag = 'hud';   // a scene can hide the dialog box (the hook card)
    if (moving) {
      hud(k, T, tops, sec);
      transition(ctx, T, tops, sec, U, head);   // room to room, hiding the cut
    }
    if (ending) { if (window.__boxes) window.__boxes.length = 0; window.__tag = 'scene'; endCard(k, T); }   // the card covers the scene, so only its own words count for lint
    window.__tag = 'scene';
    if (pixel) {
      quantize(lowCanvas);
      mctx.setTransform(1, 0, 0, 1, 0, 0); mctx.imageSmoothingEnabled = false;
      mctx.drawImage(lowCanvas, 0, 0, W, H);
    }
    return true;
  };

  async function boot() {
    for (const s of scripts) await load(s);
    for (const s of optional) await load(s).catch(() => null);
    const lk = q.get('look') || window.SCENE.look || 'clean';
    look = window.LOOKS[lk];
    env.data = window.DATA;
    cues = window.CUES.cues; cues.forEach((c) => { byId[c.id] = c; });
    words = (window.WORDS.words || []);
    env.words = words; env.duration = window.CUES.duration;
    const M = window.MOUTH;   // a mouth level for every frame, already 2 frames early (anim.py mouth)
    if (M && M.levels) env.mouth = (t) => { const i = Math.floor(t * (M.fps || FPS) + 0.005); return i >= 0 && i < M.levels.length ? +M.levels[i] : 0; };
    stamps = cues.filter((c) => c.sfx === 'stamp').sort((a, b) => a.t - b.t);
    let lastShake = -1e9; const big = window.SCENE.trauma || {};
    stamps.forEach((c) => { if (c.t - lastShake >= SHAKE_GAP) { shakes.push({t: c.t + FREEZE / FPS, a: big[c.id] || 0.5}); lastShake = c.t; } });
    const c = document.getElementById('c'); c.width = W; c.height = H;
    if (look.scale !== 1) { lowCanvas = document.createElement('canvas'); lowCanvas.width = Math.round(W * look.scale); lowCanvas.height = Math.round(H * look.scale); }
    for (const n of (window.SCENE.images || [])) {
      await new Promise((ok) => { const im = new Image(); im.onload = () => { imgs[n] = im; ok(); }; im.onerror = ok; im.src = base + '04_scene/assets/' + n + '.png'; });
    }
    await document.fonts.ready;
    await Promise.all(['700 40px Poppins', '600 40px Poppins', '600 40px Inter', '700 40px Inter'].map((f) => document.fonts.load(f)));
    phrases = buildPhrases(words);
    if (words.length) END_T = words[words.length - 1].end + 0.35;   // after the fonts load, so the line breaks match what is drawn
    window.DURATION = window.CUES.duration;
    survey = runSurvey();
    window.STUDIO = {env, survey, trauma, look, camera};   // for checks: blinks, pose runs, rooms, the shake
    window.READY = true;
    if (q.get('play')) { const t0 = performance.now(); const tick = () => { const t = (performance.now() - t0) / 1000; drawAt(t % window.DURATION); requestAnimationFrame(tick); }; tick(); }
    else drawAt(Number(q.get('t') || 0));
  }
  boot().catch((e) => { window.BOOT_ERROR = String(e && e.stack || e); console.error(e); });
})();
