/* Scene: Google now bills you for calls you miss (two-shops, arcade; Depth bank #1). One function per top-level cue in   */
/* 03_cues/cues.md. Numbers only from k.data (brief.md -> data.js); every time from a cue start (k.S) or a spoken word   */
/* (wordT), so a re-voiced take moves the picture with it.                                                              */
/* Worlds: hook, one, two and button = our own night street, two shopfronts side by side (a phone in each window, a     */
/* ring bar with the 20 s notch under it) and its close-up on the two phones; text = chat; friday = flaps; proof =      */
/* gauge; score = versus. None of them used by the two lessons before it in line (brief.md, Worlds).                    */
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', GREY = '#9AA0AD';
const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eo = (x) => 1 - Math.pow(1 - clamp(x), 3);

/* ---- the pixel kit (low-res units: 360 x 640, one pixel = 3 frame units), the same primitives the sets use ---- */
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
  const coin = (x, y, f) => {
    const ws = [4, 3, 1, 3][((f % 4) + 4) % 4];
    for (let j = 0; j < 8; j++) { const dy = j - 3.5, hw = Math.max(0, Math.round(ws * Math.sqrt(Math.max(0, 1 - (dy * dy) / 16)))); if (!hw) continue; P(x + 4 - hw, y + j, 2 * hw, 1, '#B07A47'); if (hw > 1) P(x + 4 - hw + 1, y + j, 2 * hw - 2, 1, j < 4 ? GOLD : ORANGE); }
    if (ws >= 3) { P(x + 4, y + 2, 1, 4, '#B07A47'); DOT(x + 3, y + 2, CREAM); }
  };
  return {P, DOT, dith, disc, line, win, fr, ease, tx, tw, clip, twinkle, coin, F, T};
};

/* ---- the words: every beat lands on a spoken word ---- */
const WS = () => (window.WORDS && window.WORDS.words) || [];
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
const host = (k, pose) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150});
const plate = (d, x, y, w, h) => d.win(x, y, w, h, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
/* a rubber stamp in a dark box with a coloured rim, landed with the kit's hit-stop */
const stampBox = (k, s, cx, y, t0, o = {}) => {
  const size = o.size || 66, c = o.color || GOLD, w = Math.round((k.measure(s, {size}) + 54) / 6) * 6, h = size + 36, x = Math.round((cx - w / 2) / 3) * 3;
  k.stampIn(t0, () => {
    k.shape(k.rectPts(x + 6, y + 6, w, h, 0), {fill: INK, line: false}); k.shape(k.rectPts(x, y, w, h, 0), {fill: '#1B1420', line: false});
    k.shape(k.rectPts(x + 6, y + 6, w - 12, 6, 0), {fill: c, line: false}); k.shape(k.rectPts(x + 6, y + h - 12, w - 12, 6, 0), {fill: c, line: false});
    k.shape(k.rectPts(x + 6, y + 6, 6, h - 12, 0), {fill: c, line: false}); k.shape(k.rectPts(x + w - 12, y + 6, 6, h - 12, 0), {fill: c, line: false});
    k.text(s, x + w / 2, y + 18, {size, color: c, align: 'center'});
  }, {at: [x + w / 2, y + h], freeze: o.freeze});
};

/* ================================================================================================================ */
/* a phone (low-res), w x h, screen colour by state; ringing shakes it a pixel every 2 frames and throws ring arcs */
const phone = (d, x, y, w, h, o = {}) => {
  const {P, DOT, line, F} = d, sh = o.ring ? [0, 1, 0, -1][(F >> 1) % 4] : 0, X = x + sh;
  P(X + 2, y + 2, w, h, INK); P(X - 1, y, w + 2, h, INK); P(X, y - 1, w, h + 2, INK);
  P(X, y, w, h, '#2B2033'); P(X + 1, y, w - 2, 1, '#4A4E5A');
  const scr = o.screen || (o.ring ? '#3B82C4' : '#1B1420');
  P(X + 2, y + 4, w - 4, h - 9, scr); if (o.ring) P(X + 2, y + 4, w - 4, 1, '#87CEEB');
  P(X + Math.round(w / 2) - 2, y + h - 4, 4, 2, '#4A4E5A');
  if (o.ring) { const g = (F >> 2) % 3; for (let i = 0; i <= g; i++) { const r = 4 + i * 4; line(X - 3 - i * 3, y + 4 + i, X - 3 - i * 3, y + 10 + i * 2, GOLD); line(X + w + 2 + i * 3, y + 4 + i, X + w + 2 + i * 3, y + 10 + i * 2, GOLD); } }
  if (o.icon === 'ring') { const cx = X + Math.round(w / 2), cy = y + Math.round(h / 2) - 3; P(cx - 4, cy - 1, 9, 3, CREAM); P(cx - 5, cy + 2, 3, 2, CREAM); P(cx + 3, cy + 2, 3, 2, CREAM); }
};

/* the ring bar under a window: fills from `at` over `dur`, a notch at the 20 s mark (60% of the bar) */
const NOTCH = 0.6;
const ringBar = (d, x, y, w, at, dur, o = {}) => {
  const {P, T} = d, q = at == null || T < at ? 0 : clamp((T - at) / dur) * (o.to != null ? o.to : 1);
  P(x - 1, y - 1, w + 2, 9, INK); P(x, y, w, 7, '#3D2E45');
  const fw = Math.round((w - 2) * q), past = q > NOTCH;
  P(x + 1, y + 1, fw, 5, past ? RED : TEAL); P(x + 1, y + 1, fw, 1, past ? '#F09A9A' : '#BDE6F5');
  const nx = x + Math.round(w * NOTCH); P(nx, y - 3, 2, 13, GOLD);
};

/* our own night street: two shopfronts side by side (SHOP 1 left in teal, SHOP 2 right in red). o: {lit: [a, b]       */
/* (window lights), ring: [a, b], screen: [a, b], signs: [a, b], bars: [{at, dur, to}, ...], day (the daytime strip)} */
const SHOPS = [{x: 8, w: 166, c: '#2F6F67', hi: TEAL, name: 'SHOP 1'}, {x: 186, w: 166, c: '#7A3442', hi: RED, name: 'SHOP 2'}];
const street = (k, o = {}) => {
  const d = px(k), {P, DOT, dith, disc, tx, F} = d;
  const day = !!o.day;
  /* the sky: night (stars twinkle at 2 a second) or day */
  P(0, 0, 360, 417, day ? '#87CEEB' : '#1B1420'); if (!day) { P(0, 0, 360, 60, '#120D14'); dith(0, 60, 360, 2, '#120D14', 1); }
  if (!day) for (let i = 0; i < 40; i++) { const x = Math.floor(hash(i * 3.1) * 360), y = 4 + Math.floor(hash(i * 7.9) * 140); DOT(x, y, (Math.floor(F / 15) + i) % 5 === 0 ? GOLD : '#6B7080'); }
  if (!day) { disc(318, 30, 10, '#FFF2B8'); disc(322, 27, 9, '#1B1420'); } else disc(318, 30, 10, GOLD);
  /* the skyline behind: dark blocks with a few lit windows */
  for (let i = 0; i < 9; i++) { const x = i * 42 - 6, h = 30 + Math.floor(hash(i * 5.3) * 40); P(x, 150 - h, 38, h, day ? '#9AA0AD' : '#253048'); if (!day) for (let j = 0; j < 4; j++) if (hash(i * 11 + j) > 0.6) P(x + 6 + j * 8, 150 - h + 8, 3, 4, '#F2A541'); }
  /* the two shopfronts */
  SHOPS.forEach((s, i) => {
    const lit = o.lit ? o.lit[i] : true, dim = o.dim && o.dim[i];
    P(s.x - 1, 150, s.w + 2, 267, INK); P(s.x, 151, s.w, 266, day ? '#B07A47' : '#4A2E1B');
    for (let y = 154; y < 417; y += 6) for (let x = s.x + ((y / 6) % 2) * 6; x < s.x + s.w - 4; x += 12) P(x, y, 11, 5, day ? '#C98B63' : '#5A3720');
    /* the sign band with the shop's name */
    P(s.x + 6, 156, s.w - 12, 22, INK); P(s.x + 7, 157, s.w - 14, 20, s.c); P(s.x + 7, 157, s.w - 14, 1, s.hi);
    tx(s.name, s.x + s.w / 2, 160, {color: CREAM, align: 'center', drop: INK, lint: false});
    /* the window: lit warm, or dark */
    const wx = s.x + 12, wy = 184, ww = s.w - 24, wh = 70;
    P(wx - 2, wy - 2, ww + 4, wh + 4, INK); P(wx, wy, ww, wh, lit ? '#F7D79B' : '#120D14');
    if (lit) { P(wx, wy, ww, 2, '#FFF2B8'); dith(wx, wy + wh - 6, ww, 6, '#E6C08A'); } else for (let j = 0; j < 6; j++) DOT(wx + 8 + j * 23, wy + 8 + (j % 3) * 9, '#3D2E45');
    P(wx + Math.round(ww / 2) - 1, wy, 2, wh, INK);
    /* the counter and the phone on it */
    P(wx, wy + wh - 16, ww, 4, lit ? '#8C5A33' : '#2B2033');
    phone(d, wx + Math.round(ww / 2) + 14, wy + wh - 44, 18, 28, {ring: o.ring && o.ring[i], screen: o.screen && o.screen[i]});
    /* the sign in the window (hours) */
    if (o.signs && o.signs[i]) { const sg = o.signs[i], sw = Math.round(d.tw(sg.text)) + 12, sx = wx + 6, sy = wy + 8, dy = sg.at != null && d.fr(sg.at) < 4 ? [-8, -4, -1, 1][Math.max(0, d.fr(sg.at))] : 0;
      if (sg.at == null || d.T >= sg.at) { P(sx - 1, sy - 1 + dy, sw + 2, 20, INK); P(sx, sy + dy, sw, 18, sg.c || '#1B1420'); tx(sg.text, sx + 6, sy + 2 + dy, {color: sg.tc || GOLD}); } }
    if (dim) { k.ctx.save(); k.ctx.globalAlpha = 0.62; P(s.x, 151, s.w, 266, '#120D14'); k.ctx.restore(); }
  });
  /* the ring bars, inside each shop under its window (clear of the host's band) */
  (o.bars || []).forEach((b, i) => { if (b) ringBar(d, SHOPS[i].x + 14, 262, SHOPS[i].w - 28, b.at, b.dur, b); });
  /* the sidewalk and the street under the caption band */
  P(0, 417, 360, 223, '#2B2033'); P(0, 417, 360, 3, '#4A4E5A'); for (let x = 0; x < 360; x += 24) P(x, 420, 1, 20, '#1B1420');
  P(0, 440, 360, 200, '#1B1420'); for (let x = ((-F * 2) % 48 + 48) % 48 - 48; x < 360; x += 48) P(x, 520, 24, 3, '#4A4E5A');
  return d;
};

/* the close-up: two phones big, split down the middle, both ringing, a ring bar under each */
const closeup = (k, o = {}) => {
  const d = px(k), {P, dith, tx} = d;
  P(0, 0, 180, 417, '#245752'); P(180, 0, 180, 417, '#5A2633'); P(178, 0, 4, 417, CREAM);
  for (let y = 0; y < 417; y += 4) { dith(0, y, 178, 1, '#2F6F67', y % 2); dith(182, y, 178, 1, '#7A3442', y % 2); }
  [[90, 'SHOP 1', TEAL], [270, 'SHOP 2', RED]].forEach(([cx, name, c], i) => {
    P(cx - 34, 166, 68, 22, INK); P(cx - 33, 167, 66, 20, '#1B1420'); tx(name, cx, 170, {color: c, align: 'center', lint: false});
    phone(d, cx - 22, 196, 44, 72, {ring: true, screen: o.dark ? '#253048' : '#3B82C4', icon: 'ring'});
    ringBar(d, cx - 60, 286, 120, o.barAt, o.barDur || 2.2, {to: 0.5});
  });
  P(0, 417, 360, 223, '#1B1420'); for (let y = 424; y < 640; y += 8) P(20, y, 320, 2, '#2B2033');
  return d;
};

/* the hook's title plate, held through every cut (frame y 252 to 450) */
const hookPlate = (k, d, lines) => {
  d.win(14, 84, 332, 66, {base: '#253048', hi: '#3B82C4', lo: '#1B1420', rule: '#3B82C4'});
  k.text(lines[0], 540, 270, {size: 66, color: CREAM, align: 'center', drop: INK});
  k.text(lines[1], 540, 346, {size: 66, color: 'accent', align: 'center', drop: INK});
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'MISSED CALLS',
  sendLine: 'Send this to whoever runs your Google ads.',
  transitions: {one: 'dissolve', text: 'levelselect', friday: 'dissolve', proof: 'levelselect', score: 'dissolve', button: 'gameover'},
  trauma: {'one.charged': 0.8},
  sections: {
    /* ---- hook: three shots. The cover: the night street, both windows lit, the plate "7 PM. Same call." / "Two shops." */
    /* with its EXAMPLE tag and the rule's source (no host). Cut in on "two" to the two phones close up, both ringing (Snow */
    /* and the dialog box come in). Cut back out on "nobody" to the street: both windows dark, the phones still ringing.  */
    hook: (k, T) => {
      const n = k.data.numbers;
      const tIn = Math.min(0.9, Math.max(0.4, wordT(k, 'hook', /^two/i, 0.8) - 0.03)), tOut = Math.min(2.8, k.S('hook.nobody'));
      if (T >= tOut) {
        const d = street(k, {lit: [false, false], ring: [true, true], bars: [{at: tOut, dur: 1.6, to: 0.55}, {at: tOut, dur: 1.6, to: 0.55}]});
        d.win(14, 84, 332, 66, {base: '#253048', hi: '#3B82C4', lo: '#1B1420', rule: '#3B82C4'});
        k.slam('Nobody', 540, 262, tOut, {size: 66, color: CREAM, align: 'center', drop: INK, from: 0.5});
        k.slam('picks up.', 540, 340, tOut + 0.08, {size: 66, color: 'accent', align: 'center', drop: INK, from: 0.5});
        return host(k, 'shrug');
      }
      if (T >= tIn) {
        const d = closeup(k, {barAt: tIn});
        hookPlate(k, d, [`Same ${n.callAt.shown} missed call.`, 'Google bills one shop.']);
        return host(k);
      }
      const d = street(k, {lit: [true, true], ring: [false, false]});
      /* the cover's one focal point (design gate, Oct 30: "cover has no single focal point"): the street dimmed, one big */
      /* phone ringing in front of both shops, the call time on its screen                                              */
      k.ctx.save(); k.ctx.globalAlpha = 0.6; d.P(0, 150, 360, 267, '#120D14'); k.ctx.restore();
      phone(d, 146, 176, 68, 112, {ring: true, screen: '#3B82C4'});
      d.P(30, 262, 60, 22, INK); d.P(31, 263, 58, 20, RED); d.tx('$ BILLED', 60, 266, {size: 30, color: CREAM, align: 'center'});
      d.P(270, 262, 60, 22, INK); d.P(271, 263, 58, 20, '#2F6F67'); d.tx('$0', 300, 266, {size: 30, color: CREAM, align: 'center'});
      k.text(n.callAt.shown, 540, 642, {size: 66, color: CREAM, align: 'center', drop: INK});
      k.text('CALLING', 540, 720, {size: 39, color: '#BDE6F5', align: 'center'});
      hookPlate(k, d, [`Same ${n.callAt.shown} missed call.`, 'Google bills one shop.']);
      k.chip('EXAMPLE', 66, 1008, {size: 30});
      d.P(20, 358, 300, 20, INK); d.P(21, 359, 298, 18, '#1B1420');
      k.text('Rule: Google Local Services Help', 78, 1086, {size: 39, color: SAND});
      return {host: false, speech: false};
    },

    /* ---- one: shop one lit, shop two dimmed. ADS ON TILL 9 PM in the window; on "waits" the ring bar runs past the 20 s */
    /* notch and the screen turns to VOICEMAIL; CHARGED LEAD stamps on "charged"; a coin drops out on "paid".            */
    one: (k, T) => {
      const n = k.data.numbers, t0 = k.S('one'), tSign = wordT(k, 'one', /^till/i, 2.4), tWait = k.S('one.wait'), tVm = wordT(k, 'one.wait', /^voicemail/i, 1.2);
      const tCh = k.S('one.charged'), tPaid = k.S('one.paid'), tPhone = wordT(k, 'one.paid', /^ringing/i, 0.8);
      const d = street(k, {lit: [true, false], dim: [false, true], ring: [T >= t0 + 0.3 && T < tVm, false], screen: [T >= tVm ? '#7A3442' : null, null],
        signs: [{text: `OPEN + ADS TILL ${n.oneUntil.shown}`, at: tSign}, null], bars: [{at: tWait, dur: 1.3, to: 0.85}, null]});
      d.win(14, 84, 332, 62, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
      const say = T >= tPaid ? ['You paid for a', 'ringing phone.', tPaid] : T >= tVm ? [`Caller waits ${n.secs.shown} s+`, 'into voicemail.', tVm] : T >= tWait ? ['The caller waits', 'it out...', tWait] : [`Shop 1, ${n.callAt.shown}:`, 'open, ads still on.', t0 + 0.1];
      k.slam(say[0], 72, 262, say[2], {size: 66, color: CREAM, from: 0.4, drop: INK});
      k.slam(say[1], 72, 336, say[2] + 0.06, {size: 66, color: 'accent', from: 0.4, drop: INK});
      if (T >= tVm && T < tCh) { const sx = SHOPS[0].x + 12 + 75 + 14; d.P(sx - 16, 238 - 12, 50, 12, INK); d.tx('VOICEMAIL', sx + 9, 238 - 12, {size: 30, color: CREAM, align: 'center', lint: false}); }
      if (T >= tCh) stampBox(k, 'CHARGED LEAD', 273, 640, tCh, {color: RED, freeze: 5});
      if (T >= tPaid) { const dt = T - tPhone; if (dt >= 0) { const q = clamp(dt / 0.5), y = Math.round(250 + 140 * q * q); if (q < 1) d.coin(76, y, Math.floor(d.F / 2)); else { const g = Math.floor((dt - 0.5) * 15); if (g < 8) d.twinkle(80, 394, g, GOLD); } } }
      return host(k, k.live('one.charged') ? 'point' : null);
    },

    /* ---- two: the split flips. Shop two lit with its setting card (AD SCHEDULE = HOURS A PERSON ANSWERS); on "five" the */
    /* sign reads ADS OFF AT 5 PM and the 7 PM call rings a dark window; NOT CHARGED lands on "nothing"; on "Daytime" a  */
    /* daytime strip: the desk phone rings out and an arrow carries it to a second phone, which lights up.                */
    two: (k, T) => {
      const n = k.data.numbers, t0 = k.S('two'), tFive = k.S('two.five'), tFree = wordT(k, 'two.free', /^nothing/i, 1.0), tDay = k.S('two.second');
      if (T >= tDay) {
        const tRoll = wordT(k, 'two.second', /^roll/i, 0.6), tSecond = wordT(k, 'two.second', /^second/i, 1.2);
        const d = street(k, {day: true, lit: [false, true], dim: [true, false], ring: [false, T < tRoll], bars: [null, {at: tDay, dur: 0.7, to: 0.4}]});
        /* the second phone: in a van out front, lit when the call rolls over */
        const vx = 236, vy = 300; d.P(vx - 1, vy - 1, 98, 42, INK); d.P(vx, vy, 96, 40, CREAM); d.P(vx, vy, 96, 2, '#FFFFFF'); d.P(vx + 70, vy + 6, 22, 14, '#87CEEB');
        d.disc(vx + 18, vy + 42, 6, INK); d.disc(vx + 76, vy + 42, 6, INK);
        phone(d, vx + 30, vy + 4, 16, 26, {ring: T >= tRoll && T < tSecond + 1.4, screen: T >= tRoll ? '#3B82C4' : null});
        if (T >= tRoll) d.line(296, 270, 266, vy, GOLD, 2);
        d.win(14, 84, 332, 62, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
        k.slam('Missed rings go', 72, 262, tDay, {size: 66, color: CREAM, from: 0.4, drop: INK});
        k.slam('to a second phone.', 72, 336, tDay + 0.06, {size: 66, color: 'accent', from: 0.4, drop: INK});
        return host(k, k.live('two.second') ? 'point' : null);
      }
      const after5 = T >= tFive;
      const d = street(k, {lit: [false, !after5], dim: [true, false], ring: [false, after5 && T < tFree + 0.6],
        signs: [null, after5 ? {text: `ADS OFF AT ${n.twoUntil.shown}`, at: tFive} : {text: 'ADS: STAFFED', at: t0 + 0.2, tc: TEAL}]});
      d.win(14, 84, 332, 62, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#3D2E45'});
      if (T < tFive) { k.slam('Ad schedule =', 72, 262, t0 + 0.1, {size: 66, color: CREAM, from: 0.4, drop: INK}); k.slam('hours a person answers', 72, 336, t0 + 0.16, {size: 66, color: TEAL, from: 0.4, drop: INK}); }
      else { k.slam(`${n.callAt.shown} call, ads off:`, 72, 262, tFive, {size: 66, color: CREAM, from: 0.4, drop: INK}); k.slam('costs nothing.', 72, 336, tFive + 0.06, {size: 66, color: TEAL, from: 0.4, drop: INK}); }
      if (T >= tFree) stampBox(k, 'NOT CHARGED', 700, 640, tFree, {color: TEAL});
      return host(k, k.live('two.free') ? 'point' : null);
    },

    /* ---- text: the chat set, the phone in the truck. MISSED CALL drops in; the text back types out on "every". On       */
    /* "follow-ups" the 15-day line lands in a gold box over the chat.                                                   */
    text: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('text'), tEvery = wordT(k, 'text', /^every/i, 0.6), tFol = k.S('text.follow');
      k.sets.chat({who: 'Missed caller', clock: '9:14', notify: {text: 'Missed call', at: t0 + 0.05, dur: 1.2},
        msgs: [{me: true, text: "Sorry I missed you. What's the job, and when works?", at: tEvery, read: tEvery + 1.6}]});
      d.P(10, 84, 80, 22, INK); d.P(11, 85, 78, 20, ORANGE); d.tx('EXAMPLE', 50, 88, {size: 30, color: INK, align: 'center'});
      if (T >= tFol) {
        const up = d.ease(tFol, 6, 40);
        d.clip(0, 0, 360, 322, () => { d.win(30, 226 + up, 300, 94, {base: '#1B1420', hi: '#7A3442', lo: INK, rule: GOLD});
          if (up === 0) { k.text(`Follow-ups in ${n.days.shown} days:`, 540, 714, {size: 66, color: CREAM, align: 'center', drop: INK}); k.text('not charged again.', 540, 800, {size: 66, color: GOLD, align: 'center', drop: INK}); } });
      }
      return host(k, k.live('text.follow') ? 'point' : null);
    },

    /* ---- friday: the split-flap board, CHARGE STATUS. The four statuses flip in row by row on "check", "charge",      */
    /* "status" and "Leads"; the strip under it: FRIDAYS: LEADS PAGE.                                                     */
    friday: (k, T) => {
      const d = px(k), t0 = k.S('friday'), tCheck = wordT(k, 'friday', /^check/i, 1.2), tSt = wordT(k, 'friday', /^status/i, 1.8), tLeads = wordT(k, 'friday', /^leads/i, 2.5);
      k.sets.flaps({title: 'CHARGE STATUS', cols: 11, rows: [
        {label: 'CHARGED', value: '', at: t0 - 0.8}, {label: 'NOT CHARGED', value: '', at: Math.min(t0 + 0.1, tCheck)},
        {label: 'IN REVIEW', value: '', at: tSt}, {label: 'CREDITED', value: '', at: tSt + 0.3, hi: true}]});
      { const s = 'Fridays: Leads page, Charge Status', w = Math.ceil((k.measure(s, {size: 39}) + 60) / 3);
        plate(d, Math.round(180 - w / 2), 284, w, 34); k.slam(s, 540, 870, t0 - 0.2, {size: 39, color: GOLD, align: 'center', from: 0.4});
        if (T >= tLeads) k.sweep(540 - k.measure(s, {size: 39}) / 2, 912, k.measure(s, {size: 39}), 6, tLeads, {color: 'accent'}); }
      return host(k, k.live('friday') ? 'point' : null);
    },

    /* ---- proof: the gauge as a ring timer. The needle climbs to 20 s on "twenty"; the zone past it is red (charged).   */
    /* The source on the hood the whole time it is said.                                                                */
    proof: (k, T) => {
      const n = k.data.numbers, d = px(k), tTw = wordT(k, 'proof.twenty', /^twenty/i, 0.2);
      k.sets.gauge({value: n.secs.value, max: n.secs.value * 2, at: tTw - 0.3, dur: 0.9, suffix: ' S', readout: false, labels: false, label: 'GOOGLE HELP: HOW LEADS WORK',
        zones: [[0, n.secs.value, '#2F6F67'], [n.secs.value, n.secs.value * 2, '#E2633B']]});
      /* the dial shows only the 0 (labels: false; only the brief's 20 is on the face): a gold notch on the bezel marks */
      /* the line, dropping in on "line" */
      const R = 100, cx = 180, cy = 214;
      /* the readout as the hero (design gate: "gauge readout still a 60 px chip, no 160 px hero"): the kit's chip is */
      /* left off (readout: false) and the count is drawn 144 px tall under the hub, counting with the needle                      */
      { const at = tTw - 0.3, dur = 0.9, dt = Math.max(0, T - at), v = T < at ? 0 : (dt >= dur ? n.secs.value : Math.round(n.secs.value * eo(clamp(dt / (dur * 0.55)))));
        k.text(String(v), 540, 640, {size: 264, color: GOLD, align: 'center', drop: INK});
        k.text('SEC', 668, 768, {size: 39, color: SAND}); }
      const tLine = wordT(k, 'proof', /^line/i, 1.4);
      if (T >= tLine) { const f = d.fr(tLine), lift = f < 4 ? [-6, -3, -1, 1][f] : 0; for (let j = 0; j < 6; j++) d.P(cx - 5 + j, 128 + j + lift, 11 - 2 * j, 1, j ? ORANGE : GOLD); d.P(cx - 6, 127 + lift, 13, 1, INK); }
      return host(k, k.live('proof.twenty') ? 'point' : null);
    },

    /* ---- score: the versus screen. SHOP 1 (CHARGED 1) against SHOP 2 (CHARGED 0); VS slams; WIN on shop two on      */
    /* "voicemail"; the line under it: Even voicemail counts.                                                          */
    score: (k, T) => {
      const n = k.data.numbers, d = px(k), t0 = k.S('score'), tVm = wordT(k, 'score', /^voicemail/i, 2.2);
      k.sets.versus({a: {name: 'SHOP 1', icon: 'phone', stats: [{label: 'CHARGED', value: n.oneCharged.value, max: 1, text: n.oneCharged.shown}]},
        b: {name: 'SHOP 2', icon: 'clock', stats: [{label: 'CHARGED', value: n.twoCharged.value, max: 1, text: n.twoCharged.shown}]},
        at: t0 - 0.05, vsAt: t0 + 0.35, winner: 'b', winAt: tVm, winText: 'WIN'});
      const tCnt = t0 + 0.8;
      if (T >= tCnt) { k.slam(n.oneCharged.shown, 270, 650, tCnt, {size: 330, color: RED, align: 'center', from: 0.5, drop: INK}); k.slam(n.twoCharged.shown, 738, 650, tCnt + 0.15, {size: 330, color: TEAL, align: 'center', from: 0.5, drop: INK}); }
      plate(d, 98, 300, 248, 38); k.slam('Even voicemail counts.', 312, 930, t0 + 0.2, {size: 39, color: GOLD, from: 0.4});
      if (T >= tVm) k.sweep(312, 972, k.measure('Even voicemail counts.', {size: 39}), 6, tVm, {color: 'accent'});
      return host(k, k.live('score') ? 'point' : null);
    },

    /* ---- button: back on the night street, both windows dark. The DO THIS WEEK card, four lines; the rule lands in gold */
    /* on "Run".                                                                                                       */
    button: (k, T) => {
      const n = k.data.numbers, t0 = k.S('button'), tRun = k.S('button.rule');
      const d = street(k, {lit: [false, false]});
      const up = d.ease(t0 + 0.05, 5, 160);
      const hh = 176 - d.ease(tRun, 6, 58);
      d.clip(0, 0, 360, 322, () => d.win(14, 84 + up, 332, hh, {base: '#1B1420', hi: '#7A3442', lo: INK, rule: ORANGE}));
      if (up === 0) {
        k.text(`DO THIS WEEK (${n.steps.shown})`, 72, 270, {size: 39, color: GOLD});
        ['1 Ads: only hours you answer', '2 Missed rings: second phone', '3 Text back every missed call', '4 Fridays: Charge Status'].forEach((s, i) => {
          const ti = t0 + 0.22 + i * 0.06; if (T >= ti) k.slam(s, 72, 330 + i * 58, ti, {size: 39, color: CREAM, from: 0.3}); });
        if (T >= tRun) { k.slam('Run ads only when', 72, 594, tRun, {size: 66, color: CREAM, from: 0.4, drop: INK}); k.slam('someone picks up.', 72, 670, tRun + 0.1, {size: 66, color: GOLD, from: 0.4, drop: INK}); k.sweep(72, 744, k.measure('someone picks up.', {size: 66}), 6, tRun + 0.4, {color: 'accent'}); }
      }
      return host(k, T >= tRun + 0.8 ? 'wave' : (k.live('button') ? 'point' : null));
    },
  },
};
