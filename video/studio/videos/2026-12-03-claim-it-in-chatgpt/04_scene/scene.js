/* 2026-12-03-claim-it-in-chatgpt (v4 update), from the v4 template's helpers (wordT, px, plate, stampPlate, steps),   */
/* kept whole (_shared/formats.md "v4" and "Update"). One section a cue. Every row of words is size 132 or more. The    */
/* real screens are strips cut from the captures in assets/ (facts.json "captures"): each is drawn as a paper clipping, */
/* its box painted in a key color and returned in `screens`, and the player lays the capture in at full resolution.    */
/* Never a drawn copy: no word of a screen is typed here.                                                              */
const INK = '#120D14', CREAM = '#FFF7EA', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', DTEAL = '#2F6F67', NIGHT = '#1B1420', PLUM = '#2B2033', WINE = '#7A3442', SLATE = '#253048';
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const WS = () => (window.WORDS && window.WORDS.words) || [];
/* the start of the first word matching re at or after a cue (id) or a time; dflt seconds after it when no word matches */
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
/* the low-res painter (360 x 640, one unit = 3 frame pixels) */
const px = (k) => {
  const ctx = k.ctx;
  return (x, y, w, h, c) => { x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h); if (w > 0 && h > 0 && c) { ctx.fillStyle = c; ctx.fillRect(x * 3, y * 3, w * 3, h * 3); } };
};
/* a centered plate of rows [[text, size, color], ...] with its top at y; returns its bottom */
const plate = (k, rows, y, o = {}) => {
  const cx = o.cx || 540, pad = o.pad || 36, gap = o.gap || 18;
  const hs = rows.map(([, z]) => Math.round(z * 1.0)), w = Math.ceil((Math.max(...rows.map(([s, z]) => k.measure(s, {size: z}))) + 2 * pad) / 6) * 6;
  const h = hs.reduce((a, b) => a + b, 0) + gap * (rows.length - 1) + 2 * pad - 6, x = Math.round((cx - w / 2) / 3) * 3;
  k.shape(k.rectPts(x + 9, y + 9, w, h, 0), {fill: INK, line: false});
  k.shape(k.rectPts(x, y, w, h, 0), {fill: o.bg || NIGHT, line: false});
  k.shape(k.rectPts(x, y, w, 9, 0), {fill: o.rule || ORANGE, line: false});
  let yy = y + pad;
  rows.forEach(([s, z, c], i) => { k.text(s, cx, yy, {size: z, color: c || CREAM, align: 'center'}); yy += hs[i] + gap; });
  return y + h;
};
/* the same plate landing as a stamp at t0 */
const stampPlate = (k, rows, y, t0, o = {}) => {
  const hgt = rows.reduce((a, [, z]) => a + z, 0) + 18 * (rows.length - 1) + 66;
  return k.stampIn(t0, () => plate(k, rows, y, o), {at: [o.cx || 540, y + hgt], freeze: o.freeze, drop: o.drop});
};
/* a row of plates in time: [[t, rows, stamp?], ...]; the last one whose time has come shows; a later one lands as a stamp */
const steps = (k, T, list, o = {}, y = 264) => {
  let i = 0; list.forEach(([t], j) => { if (j && T >= t - 0.06) i = j; });
  const [t, rows, st] = list[i];
  if (i === 0 && !st) return plate(k, rows, y, o);
  return stampPlate(k, rows, y, t, Object.assign({drop: 0.06, freeze: 4}, o));
};
const W = (k, id, re, d) => wordT(k, id, re, d) - 0.1;
const plateBottom = (rows, y = 264) => y + rows.reduce((a, [, z]) => a + z, 0) + 18 * (rows.length - 1) + 66;

/* ---- the real screens: strips of the captures (image, [x, y, w, h] in its own pixels, and the height of its capital  */
/* letters there), found by reading the capture. Each is drawn so its capitals stand 62 px tall or more in the frame.     */
/* A whole screen (tw: its width in the frame) is shown as a picture, with the point in a plate of big words and the spot   */
/* ringed (formats.md "Update", "Whole screens"); side: a tall one, set beside him.                                        */
const STRIPS = {"annBeta":{"img":"announce-beta","r":[500,11,270,49],"cap":24},"tt1":{"img":"terms-top","r":[20,119,477,86],"cap":57},"tt2":{"img":"terms-top","r":[500,119,570,86],"cap":57},"calls2":{"img":"terms-calls","r":[14,623,342,50],"cap":23},"loc1":{"img":"help-local","r":[417,56,181,42],"cap":22},"loc2":{"img":"help-local","r":[596,56,235,42],"cap":22},"gov0":{"img":"help-persona","r":[15,377,233,48],"cap":22},"gov":{"img":"help-persona","r":[247,376,330,49],"cap":23},"addr":{"img":"hub-address","r":[70,6,343,58],"cap":21},"optS":{"img":"terms-calls","r":[694,623,248,53],"cap":23},"shSearch":{"img":"hub-search","r":[0,0,1080,438],"tw":984},"shHub":{"img":"hub","r":[0,46,1060,444],"tw":984},"shAdd":{"img":"hub-add","r":[0,0,952,1276],"tw":501,"side":1},"shVerify":{"img":"hub-verify","r":[0,0,1060,440],"tw":984},"shSue":{"img":"terms-claims","r":[0,124,1230,224],"tw":984},"shCov":{"img":"terms-covered","r":[0,136,1384,170],"tw":984},"shCalls":{"img":"terms-calls","r":[0,566,1230,114],"tw":984},"shList":{"img":"terms-calls","r":[0,6,1230,170],"tw":984},"shLocal":{"img":"help-local","r":[0,0,1120,155],"tw":984},"covW":{"img":"terms-covered","r":[969,195,271,49],"cap":24},"covO":{"img":"terms-covered","r":[611,252,401,50],"cap":23},"ex1":{"img":"terms-covered","r":[515,27,354,44],"cap":24},"exO":{"img":"terms-covered","r":[867,28,275,50],"cap":24},"exT":{"img":"terms-covered","r":[1140,28,203,48],"cap":24},"reg1":{"img":"terms-calls","r":[557,119,339,51],"cap":23}};
/* the page each capture is from decides its key color: a dark page or a light one, so the cast's edge sits on a near color */
const DARK = '#212223', LIGHT = '#FCFDFC';
const TONE = (img) => (/^help/.test(img) ? LIGHT : DARK);
const q3 = (v) => Math.round(v / 3) * 3;
const CAP = 62, MAXW = 984;
const scaleOf = (n) => (STRIPS[n].tw ? STRIPS[n].tw / STRIPS[n].r[2] : Math.min(CAP / STRIPS[n].cap, MAXW / STRIPS[n].r[2]));
/* one clipping: strip `name` at scale sc with its top-left at (x, y); pushes the screen for the player; returns its box */
const clip = (k, L, name, x, y, sc) => {
  const s = STRIPS[name], P = px(k), key = TONE(s.img);
  const w = q3(s.r[2] * sc), h = q3(s.r[3] * sc); x = q3(x); y = q3(y);
  P(x / 3 + 1, y / 3 + 1, w / 3 + 4, h / 3 + 4, INK);
  P(x / 3 - 2, y / 3 - 2, w / 3 + 4, h / 3 + 4, CREAM);
  P(x / 3, y / 3, w / 3, h / 3, key);
  L.push({img: s.img, x, y, w, h, sx: s.r[0], sy: s.r[1], sw: s.r[2], sh: s.r[3], key});
  return {x, y, w, h, b: y + h};
};
/* a ring around a clipping (the place to look or tap) */
const ring = (k, b0, c = ORANGE, f) => { const b = f ? {x: b0.x + b0.w * f[0], y: b0.y + b0.h * f[1], w: b0.w * f[2], h: b0.h * f[3]} : b0; const P = px(k), x = b.x / 3 - 4, y = b.y / 3 - 4, w = b.w / 3 + 8, h = b.h / 3 + 8; P(x, y, w, 3, c); P(x, y + h - 3, w, 3, c); P(x, y, 3, h, c); P(x + w - 3, y, 3, h, c); };
/* a plain lined wall: each source has its own (openai.com night, the help page green, ChatGPT slate, the terms wine) */
const WALLS = {ai: [NIGHT, PLUM], help: ['#24453A', '#2F5A4A'], hub: [SLATE, '#1B1420'], terms: ['#5A2432', WINE], end: [PLUM, '#3D2E45'], news: [WINE, '#5A2432']};
const wall = (k, id) => { const P = px(k), [c, c2] = WALLS[id]; P(0, 0, 360, 640, c); for (let y = 20; y < 640; y += 22) P(0, y, 360, 1, c2); };
/* Snow, from the waist up behind a wood desk in the lower half: his head between y 840 and 1180, clear of the captions.  */
/* The desk fills the frame to the bottom, and a desk phone sits on it on the far side from him; it rings while the      */
/* terms' calls are the subject.                                                                                        */
const WOOD = '#8A5A2B', WOODD = '#5E3B1C', WOODL = '#B9803F';
const snow = (k, x, pose, o = {}, d = {}) => {
  k.snow(x, o.feet || 1788, Object.assign({scale: o.scale || 1.8, pose, face: x > 540 ? -1 : 1}, o));
  const P = px(k);
  P(0, 464, 360, 80, WOODL); P(0, 462, 360, 2, CREAM); P(0, 544, 360, 96, WOOD); P(0, 544, 360, 3, WOODD);
  for (let y = 570; y < 640; y += 26) P(0, y, 360, 1, WOODD);
  for (let xx = 30; xx < 360; xx += 100) P(xx, 547, 2, 93, WOODD);
  const f = 1.7, x0 = x > 540 ? 34 : 232, y0 = 530, j = d.ring ? (Math.floor(d.T * 15) % 2 ? 3 : -3) : 0;
  const R = (dx, dy, w, h, c) => P(x0 + dx * f, y0 + dy * f, w * f, h * f, c);
  R(0, -18, 52, 18, INK); R(5, -23, 42, 5, INK);
  for (let i = 0; i < 3; i++) for (let r = 0; r < 2; r++) R(15 + i * 8, -15 + r * 6, 4, 3, CREAM);
  P(x0 - 5 + j, y0 - 32 * f, 58 * f, 7 * f, INK); P(x0 - 8 + j, y0 - 32 * f, 13 * f, 12 * f, INK); P(x0 + 44 * f + j, y0 - 32 * f, 13 * f, 12 * f, INK);
  if (d.ring) [[-12, -36], [-20, -27], [-12, -18], [62, -36], [70, -27], [62, -18]].forEach(([dx, dy], i) => R(dx + (i % 2 ? j : -j) / 2, dy, 5, 5, GOLD));
};
const HEAD = 904;   /* a clipping across his side of the frame stops here, above his head */
/* where a pointing hand aims at time T: it runs back and forth along the bottom edge of clipping b, on whole low-res pixels */
const follow = (T, t0, b, sx, under) => { const c = sx > 540 ? b.x + b.w * 0.62 : b.x + b.w * 0.38, a = Math.min(190, b.w * 0.3); return [q3(c + a * Math.sin((T - t0) * 2.6)), under ? b.b + 21 : b.b - 12]; };

/* beside a clipping that sits next to him, the hand bobs at its near edge and never crosses its words */
const beside = (T, t0, b, sx) => [q3(sx > 540 ? b.x + b.w + 42 : b.x - 42), q3(b.y + b.h / 2 + 15 * Math.sin((T - t0) * 2.6))];

/* One section from a small table:                                                                                      */
/*   wall; snow [x, pose]; plates [[word or null, rows, stamp?], ...] (the first at the cue, the rest on a spoken word);  */
/*   strips [[word or null, [names], 'add' | 'new'], ...]: 'new' clears the clippings before it, 'add' joins the stack;   */
/*   ring [[word or null, name], ...]; phone: true or a word (the desk phone rings from then); head: how low a centered  */
/*   clipping may reach.                                                                                               */
const section = (id, d) => (k, T) => {
  const t0 = k.S(id), L = [];
  if (!d.first) k.cut(t0);
  wall(k, d.wall);
  const pl = d.plates.map(([re, rows, st], i) => [i === 0 ? t0 + (st ? 0.08 : 0) : W(k, id, re, 1.4 * i), rows, st]);
  const top = Math.max(...d.plates.map(([, rows]) => plateBottom(rows))) + 30;
  const gs = (d.strips || []).map(([re, names, mode], i) => ({t: re ? W(k, id, re, 1.4 * i) : t0, names, mode: i === 0 ? 'new' : (mode || 'add')}));
  let a = 0; gs.forEach((g, i) => { if (g.mode === 'new' && T >= g.t) a = i; });
  let b = gs.length; for (let i = a + 1; i < gs.length; i++) if (gs[i].mode === 'new') { b = i; break; }
  const items = []; gs.slice(a, b).forEach((g) => g.names.forEach((n) => items.push([n, g.t])));
  const gap = 27, [sx, pose0] = d.snow;
  let y = top, last = null, lastLow = false, lastShot = false; const boxes = {};
  items.forEach(([n, t]) => {
    const s = STRIPS[n], sc = scaleOf(n), w = q3(s.r[2] * sc), h = q3(s.r[3] * sc);
    /* a clipping that would reach below his cap, and a tall screen, is set on the other side of the frame */
    const low = !!s.side || y + h > (d.head || HEAD), x = !low ? 540 - w / 2 : (sx > 540 ? 48 : 1032 - w);
    if (T >= t) { boxes[n] = clip(k, L, n, x, s.side ? top : y, sc); last = boxes[n]; lastLow = low; lastShot = !!s.tw; }
    if (!s.side) y += h + gap;
  });
  (d.ring || []).forEach(([re, n, c, f]) => { if (boxes[n] && T >= (re ? W(k, id, re, 1) : t0)) ring(k, boxes[n], c || ORANGE, f); });
  /* he never stands still: a pointing hand runs along the newest clipping the way a finger follows a line; a shrug lifts */
  /* and drops. Motion lives in the things on screen, never in the camera.                                                */
  const beat = Math.floor((T - t0) / 0.9) % 2, pose = pose0 !== 'point' ? (beat && last ? 'point' : pose0) : pose0;
  const ringing = d.phone ? T >= (d.phone === true ? t0 : W(k, id, d.phone, 1)) : false;
  snow(k, sx, pose, pose === 'point' && last ? {at: lastLow ? beside(T, t0, last, sx) : follow(T, t0, last, sx, lastShot)} : {}, {ring: ringing, T});
  steps(k, T, pl);
  return {host: false, screens: L};
};
const STEP = (n) => ['STEP ' + n, 132, ORANGE];

window.SCENE = {
  look: 'arcade',
  v4: true,
  host: false,
  endCard: false,
  images: ['announce-beta', 'help-claim', 'help-local', 'help-phone', 'help-persona', 'terms-top', 'terms-calls', 'terms-claims', 'terms-covered', 'hub', 'hub-search', 'hub-add', 'hub-verify', 'hub-address'],
  trauma: {step1: 0.5},
  sections: {
    /* ---- hook: frame 0 is his own Business Hub search screen, settled, Snow at his desk. At 0.5 s the wall turns and he */
    /* points (the first change); on "ChatGPT" the search box is ringed and a stamp lands (the second).                   */
    hook: (k, T) => {
      const L = [], t1 = 0.5, tL = Math.min(2.3, Math.max(1.1, W(k, 'hook', /^ChatGPT/i, 1.5)));
      wall(k, T < t1 ? 'hub' : 'news');
      const A = [['BEFORE YOU CLAIM', 132, CREAM]], B = [['READ THIS FIRST', 132, RED]];
      const sc = scaleOf('shSearch'), h1 = clip(k, L, 'shSearch', 48, plateBottom(A) + 30, sc);
      if (T >= tL) ring(k, h1, ORANGE, [0.02, 0.48, 0.96, 0.24]);
      snow(k, 830, T < t1 ? 'wave' : 'point', T < t1 ? {} : {at: follow(T, 0, h1, 830, true)}, {T});
      steps(k, T, [[0, A], [tL, B, 1]]);
      return {host: false, screens: L};
    },
    /* ---- the terms in plain words, each over the terms' own page ---- */
    sue: section('sue', {wall: 'terms', snow: [230, 'point'],
      plates: [[null, [['YOU AGREE:', 132, CREAM]]], [/^sue/i, [['NO SUING OPENAI', 132, RED], ['OVER YOUR SITE', 132, RED]], 1]],
      strips: [[null, ['shSue']]], ring: [[/^sue/i, 'shSue', RED, [0.07, 0.0, 0.3, 0.26]]]}),
    site: section('site', {wall: 'terms', snow: [830, 'clip'], head: 930,
      plates: [[null, [['OVER WHAT?', 132, CREAM]]], [/^published/i, [['WHAT YOU PUBLISH', 132, RED]], 1]],
      strips: [[null, ['shCov', 'covW']], [/^your/i, ['covO']]], ring: [[/^website/i, 'covO', RED]]}),
    unless: section('unless', {wall: 'terms', snow: [230, 'shrug'], head: 930,
      plates: [[null, [['ONE EXCEPTION:', 132, TEAL]], 1], [/^breaks/i, [['IT BREAKS TERMS', 132, TEAL]], 1]],
      strips: [[null, ['ex1', 'exO', 'exT']]]}),
    terms: section('terms', {wall: 'terms', snow: [830, 'clip'],
      plates: [[null, [['IN THE TERMS', 132, CREAM]], 1]],
      strips: [[null, ['tt1', 'tt2']]]}),
    calls: section('calls', {wall: 'terms', snow: [230, 'point'], phone: /^call/i,
      plates: [[null, [['YOU ALSO AGREE:', 132, CREAM]]], [/^call/i, [['ITS AI MAY CALL', 132, RED]], 1]],
      strips: [[null, ['shCalls']], [/^call/i, ['calls2']]], ring: [[/^call/i, 'calls2', RED]]}),
    opt: section('opt', {wall: 'terms', snow: [830, 'shrug'],
      plates: [[null, [['YOU CAN OPT OUT', 132, TEAL]], 1]],
      strips: [[null, ['shCalls', 'optS']]], ring: [[null, 'optS', TEAL]]}),
    hub: section('hub', {wall: 'hub', snow: [230, 'point'],
      plates: [[null, [['BUSINESS HUB', 132, GOLD]], 1], [/^claim/i, [['CLAIM YOURS HERE', 132, CREAM]], 1]],
      strips: [[null, ['shHub']]]}),
    /* ---- the four steps, one line, each over the real screen ---- */
    step1: section('step1', {wall: 'hub', snow: [830, 'point'],
      plates: [[null, [['FOUR STEPS', 132, CREAM]], 1], [/^open/i, [['STEP 1: OPEN IT', 132, ORANGE]], 1]],
      strips: [[null, ['addr']]], ring: [[/^open/i, 'addr']]}),
    step2: section('step2', {wall: 'hub', snow: [230, 'point'],
      plates: [[null, [['STEP 2: SEARCH', 132, ORANGE]], 1]],
      strips: [[null, ['shSearch']]], ring: [[null, 'shSearch', ORANGE, [0.02, 0.48, 0.96, 0.24]]]}),
    step3: section('step3', {wall: 'hub', snow: [830, 'point'],
      plates: [[null, [['STEP 3: PROVE IT', 132, ORANGE]], 1]],
      strips: [[null, ['shVerify']]], ring: [[null, 'shVerify', ORANGE, [0.01, 0.04, 0.98, 0.17]]]}),
    step4: section('step4', {wall: 'help', snow: [230, 'clip'],
      plates: [[null, [['STEP 4: ID CHECK', 132, ORANGE]], 1]],
      strips: [[null, ['gov0', 'gov']]]}),
    beta: section('beta', {wall: 'ai', snow: [830, 'point'],
      plates: [[null, [['IN BETA', 198, GOLD]], 1]],
      strips: [[null, ['annBeta']]], ring: [[null, 'annBeta']]}),
    /* ---- the catch: the limit never shows without its owner, "Local stores" / "and restaurants" ---- */
    catch: section('catch', {wall: 'help', snow: [230, 'shrug'],
      plates: [[null, [['THE CATCH', 198, RED]], 1]],
      strips: [[null, ['shLocal']]], ring: [[null, 'shLocal', RED, [0.0, 0.36, 1.0, 0.64]]]}),
    local: section('local', {wall: 'help', snow: [830, 'point'], head: 930,
      plates: [[null, [['OPENAI SAYS:', 132, CREAM]]], [/^claim/i, [['EXISTING ONLY', 132, GOLD]], 1]],
      strips: [[null, ['shLocal', 'loc1', 'loc2']]], ring: [[null, 'shLocal', RED, [0.0, 0.36, 1.0, 0.64]]]}),
    usonly: section('usonly', {wall: 'help', snow: [230, 'point'], head: 930,
      plates: [[null, [['U.S. ONLY', 132, GOLD]], 1], [/^for/i, [['FOR NOW', 132, CREAM]], 1]],
      strips: [[null, ['shLocal', 'loc1', 'loc2']]], ring: [[null, 'shLocal', RED, [0.0, 0.66, 0.46, 0.34]]]}),
    /* ---- should you claim it: our call, said as ours ---- */
    should: section('should', {wall: 'end', snow: [540, 'shrug'],
      plates: [[null, [['SHOULD YOU', 132, CREAM], ['CLAIM IT?', 132, GOLD]], 1]]}),
    call: section('call', {wall: 'end', snow: [540, 'wave'],
      plates: [[null, [['OUR CALL', 198, GOLD]], 1]]}),
    list: section('list', {wall: 'terms', snow: [230, 'point'],
      plates: [[null, [['OPENAI MAY LIST', 132, CREAM]], 1], [/^whether/i, [['YOU EITHER WAY', 132, GOLD]], 1]],
      strips: [[null, ['shList']], [/^whether/i, ['reg1']]], ring: [[/^whether/i, 'reg1']]}),
    claimit: section('claimit', {wall: 'hub', snow: [830, 'point'], phone: /^calls/i,
      plates: [[null, [['ALREADY LISTED?', 132, CREAM]]], [/^Claim/, [['CLAIM IT', 132, GOLD]], 1], [/^opt/i, [['THEN OPT OUT', 132, TEAL]], 1]],
      strips: [[null, ['shAdd']]], ring: [[/^Claim/, 'shAdd', ORANGE, [0.05, 0.86, 0.9, 0.09]]]}),
    money: section('money', {wall: 'terms', snow: [230, 'shrug'],
      plates: [[null, [["SELL WHAT'S ON", 132, CREAM], ['YOUR WEBSITE?', 132, CREAM]]], [/^read/i, [['READ THE TERMS', 132, RED], ['FIRST', 132, RED]], 1], [/^We're/i, [["WE'RE NOT", 132, CREAM], ['LAWYERS', 132, CREAM]], 1]],
      strips: [[null, ['shCov']]], ring: [[/^read/i, 'shCov', RED]]}),
    /* ---- ask: save it, who to send it to, then the four steps as the last frame (the thing to save) ---- */
    ask: (k, T) => {
      const t0 = k.S('ask'), tS = W(k, 'ask', /^send/i, 0.8), tR = W(k, 'ask', /^handles/i, 1.8);
      k.cut(t0);
      wall(k, 'end');
      snow(k, 540, 'wave', {scale: 1.5, feet: 1660}, {T});
      steps(k, T, [[t0 + 0.08, [['SAVE THIS', 198, GOLD]], 1], [tS, [['SEND TO WHOEVER', 132, CREAM], ['HANDLES YOUR', 132, CREAM], ['LISTINGS', 132, GOLD]], 1],
        [tR, [['1 OPEN THE HUB', 132, CREAM], ['2 SEARCH NAME', 132, CREAM], ['3 PROVE IT', 132, CREAM], ['4 ID CHECK', 132, CREAM]], 1]]);
      return {host: false};
    },
  },
};
