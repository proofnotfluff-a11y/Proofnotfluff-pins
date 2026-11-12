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
const STRIPS = {"annTitle":{"img":"announce","r":[71,121,848,177],"cap":57},"ann12a":{"img":"announce-beta","r":[256,67,316,51],"cap":24},"ann12b":{"img":"announce-beta","r":[569,68,285,43],"cap":23},"annBeta":{"img":"announce-beta","r":[500,11,270,49],"cap":24},"annClaim":{"img":"announce-beta","r":[473,123,317,49],"cap":24},"tt1":{"img":"terms-top","r":[20,119,477,86],"cap":57},"tt2":{"img":"terms-top","r":[500,119,570,86],"cap":57},"helpOpen":{"img":"help-claim","r":[426,539,285,48],"cap":22},"hubHead2":{"img":"hub","r":[255,424,545,66],"cap":34},"hubBoxS":{"img":"hub-box","r":[0,16,373,94],"cap":23},"tl1":{"img":"hub-terms","r":[10,12,184,47],"cap":20},"tl2":{"img":"hub-terms","r":[191,13,265,46],"cap":20},"calls1":{"img":"terms-calls","r":[876,566,333,51],"cap":24},"calls2":{"img":"terms-calls","r":[14,623,342,50],"cap":23},"opt":{"img":"terms-calls","r":[694,623,330,53],"cap":23},"sue":{"img":"terms-claims","r":[79,127,333,43],"cap":24},"loc1":{"img":"help-local","r":[417,56,181,42],"cap":22},"loc2":{"img":"help-local","r":[596,56,235,42],"cap":22},"loc3":{"img":"help-local","r":[16,103,313,49],"cap":23},"loc4":{"img":"help-local","r":[330,103,162,49],"cap":23},"ph1":{"img":"help-phone","r":[15,154,295,58],"cap":30},"ph2":{"img":"help-phone","r":[309,154,290,58],"cap":30},"vf1":{"img":"hub-verify","r":[14,17,565,80],"cap":42},"vf2":{"img":"hub-verify","r":[583,17,448,79],"cap":42},"gov0":{"img":"help-persona","r":[15,377,233,48],"cap":22},"gov":{"img":"help-persona","r":[247,376,330,49],"cap":23},"id2":{"img":"help-claim","r":[76,402,241,49],"cap":23},"faq1":{"img":"help-faq","r":[156,209,295,49],"cap":23},"faq2":{"img":"help-faq","r":[450,209,270,49],"cap":23}};
/* the page each capture is from decides its key color: a dark page or a light one, so the cast's edge sits on a near color */
const DARK = '#212223', LIGHT = '#FCFDFC';
const TONE = (img) => (/^help/.test(img) ? LIGHT : DARK);
const q3 = (v) => Math.round(v / 3) * 3;
const CAP = 62, MAXW = 984;
const scaleOf = (n) => Math.min(CAP / STRIPS[n].cap, MAXW / STRIPS[n].r[2]);
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
const ring = (k, b, c = ORANGE) => { const P = px(k), x = b.x / 3 - 4, y = b.y / 3 - 4, w = b.w / 3 + 8, h = b.h / 3 + 8; P(x, y, w, 3, c); P(x, y + h - 3, w, 3, c); P(x, y, 3, h, c); P(x + w - 3, y, 3, h, c); };
/* a plain lined wall: each source has its own (openai.com night, the help page green, ChatGPT slate, the terms wine) */
const WALLS = {ai: [NIGHT, PLUM], help: ['#24453A', '#2F5A4A'], hub: [SLATE, '#1B1420'], terms: ['#5A2432', WINE], end: [PLUM, '#3D2E45'], news: [WINE, '#5A2432']};
const wall = (k, id) => { const P = px(k), [c, c2] = WALLS[id]; P(0, 0, 360, 640, c); for (let y = 20; y < 640; y += 22) P(0, y, 360, 1, c2); };
/* Snow, from the chest up behind a counter at the bottom of the frame: his head between y 840 and 1180, clear of the      */
/* captions; the counter hides everything below his chest, so he reads as a presenter at a desk.                           */
const snow = (k, x, pose, o = {}) => {
  k.snow(x, o.feet || 1722, Object.assign({scale: o.scale || 1.8, pose, face: x > 540 ? -1 : 1}, o));
  const P = px(k); P(0, 464, 360, 176, INK); P(0, 462, 360, 2, PLUM);
};
const HEAD = 838;   /* a clipping across his side of the frame stops here, above his head */
/* where a pointing hand aims at time T: it runs back and forth along the bottom edge of clipping b, on whole low-res pixels */
const follow = (T, t0, b, sx) => { const c = sx > 540 ? b.x + b.w * 0.62 : b.x + b.w * 0.38, a = Math.min(190, b.w * 0.3); return [q3(c + a * Math.sin((T - t0) * 2.6)), b.b - 12]; };

/* One section from a small table:                                                                                      */
/*   wall; snow [x, pose]; plates [[word or null, rows, stamp?], ...] (the first at the cue, the rest on a spoken word);  */
/*   strips [[word or null, [names], 'add' | 'new'], ...]: 'new' clears the clippings before it, 'add' joins the stack;   */
/*   ring [[word or null, name], ...].                                                                                   */
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
  let y = top, last = null; const boxes = {};
  items.forEach(([n, t]) => {
    const sc = scaleOf(n), w = q3(STRIPS[n].r[2] * sc), h = q3(STRIPS[n].r[3] * sc);
    /* a clipping that would reach below his cap is set on the other side of the frame */
    const low = y + h > HEAD, x = !low ? 540 - w / 2 : (sx > 540 ? 48 : 1032 - w);
    if (T >= t) { boxes[n] = clip(k, L, n, x, y, sc); last = boxes[n]; }
    y += h + gap;
  });
  (d.ring || []).forEach(([re, n, c]) => { if (boxes[n] && T >= (re ? W(k, id, re, 1) : t0)) ring(k, boxes[n], c); });
  /* he never stands still: a pointing hand runs along the newest clipping the way a finger follows a line; a shrug lifts */
  /* and drops. Motion lives in the things on screen, never in the camera.                                                */
  const beat = Math.floor((T - t0) / 0.9) % 2, pose = pose0 === 'shrug' ? (beat && last ? 'point' : 'shrug') : pose0;
  snow(k, sx, pose, pose === 'point' && last ? {at: follow(T, t0, last, sx)} : {});
  steps(k, T, pl);
  return {host: false, screens: L};
};
const STEP = (n) => ['STEP ' + n, 132, ORANGE];

window.SCENE = {
  look: 'arcade',
  v4: true,
  host: false,
  endCard: false,
  images: ['announce', 'announce-beta', 'help-claim', 'help-local', 'help-faq', 'help-phone', 'help-persona', 'terms-top', 'terms-calls', 'terms-claims', 'hub', 'hub-box', 'hub-terms', 'hub-verify'],
  trauma: {step1: 0.5},
  sections: {
    /* ---- hook: frame 0 is the news, settled: OpenAI's own headline, Snow close, the news up top. At 0.5 s the wall     */
    /* turns and he points (the first change); on "listings" the second row stamps in and the headline is ringed.         */
    hook: (k, T) => {
      const L = [], t1 = 0.5, tL = Math.min(2.4, Math.max(1.1, W(k, 'hook', /^listings/i, 1.6)));
      wall(k, T < t1 ? 'ai' : 'news');
      const A = [['NEW IN CHATGPT', 132, CREAM]], B = [['NEW IN CHATGPT:', 132, CREAM], ['BUSINESS LISTINGS', 132, GOLD]];
      const sc = scaleOf('annTitle'), h1 = clip(k, L, 'annTitle', 540 - q3(STRIPS.annTitle.r[2] * sc) / 2, plateBottom(B) + 30, sc);
      if (T >= tL) ring(k, h1);
      snow(k, 830, T < t1 ? 'wave' : 'point', T < t1 ? {} : {at: follow(T, 0, h1, 830)});
      steps(k, T, [[0, A], [tL, B, 1]]);
      return {host: false, screens: L};
    },
    users: (k, T) => {
      const n = k.data.numbers.weeklyUsersBillion.shown;   /* OpenAI's own figure, from facts.json through data.js */
      return section('users', {wall: 'ai', snow: [230, 'point'],
        plates: [[null, [[n + ' BILLION', 198, GOLD]], 1], [/^week/i, [[n + ' BILLION', 132, GOLD], ['EVERY WEEK', 132, CREAM]], 1]],
        strips: [[null, ['ann12a']], [/^use/i, ['ann12b']]]})(k, T);
    },
    fine: section('fine', {wall: 'terms', snow: [830, 'point'],
      plates: [[null, [['FIRST: READ', 132, CREAM], ['THE SMALL PRINT', 132, RED]], 1]],
      strips: [[null, ['tt2']]]}),
    what: section('what', {wall: 'ai', snow: [230, 'point'],
      plates: [[null, [['BUSINESS HUB', 132, GOLD]]], [/^beta/i, [['IN BETA', 198, GOLD]], 1], [/^claim/i, [['CLAIM YOURS', 132, CREAM]], 1]],
      strips: [[null, ['annBeta']], [/^claim/i, ['annClaim'], 'new']], ring: [[/^beta/i, 'annBeta']]}),
    step1: section('step1', {wall: 'help', snow: [830, 'point'],
      plates: [[null, [STEP(1), ['OPEN THE HUB', 132, CREAM]], 1], [/^OpenAI/i, [['OPENAI SAYS:', 132, CREAM], ['THE SIDEBAR', 132, GOLD]], 1], [/^type/i, [['CHATGPT.COM', 132, GOLD], ['/BUSINESS-HUB', 132, GOLD]], 1]],
      strips: [[null, ['helpOpen']], [/^type/i, ['hubHead2'], 'new']], ring: [[/^OpenAI/i, 'helpOpen']]}),
    step2: section('step2', {wall: 'hub', snow: [230, 'point'],
      plates: [[null, [['STEP 2: SEARCH', 132, ORANGE]], 1]],
      strips: [[null, ['hubBoxS']]], ring: [[/^Search/i, 'hubBoxS']]}),
    terms: section('terms', {wall: 'hub', snow: [830, 'point'],
      plates: [[null, [['THE SMALL PRINT', 132, RED]], 1], [/^accept/i, [['YOU ACCEPT TERMS', 132, RED]], 1]],
      strips: [[null, ['tl1']], [/^continuing/i, ['tl2']]], ring: [[/^accept/i, 'tl2', RED]]}),
    calls: section('calls', {wall: 'terms', snow: [230, 'point'],
      plates: [[null, [['THE TERMS SAY:', 132, CREAM]]], [/^call/i, [['ITS AI MAY CALL', 132, RED]], 1]],
      strips: [[null, ['calls1']], [/^call/i, ['calls2']]]}),
    opt: section('opt', {wall: 'terms', snow: [830, 'shrug'],
      plates: [[null, [['YOU CAN OPT OUT', 132, TEAL]], 1]],
      strips: [[null, ['opt']]]}),
    claims: section('claims', {wall: 'terms', snow: [230, 'shrug'],
      plates: [[null, [['AND THIS:', 132, CREAM]]], [/^not/i, [['COVENANT', 132, CREAM], ['NOT TO SUE', 132, RED]], 1]],
      strips: [[null, ['sue']]], ring: [[/^not/i, 'sue', RED]]}),
    catch: section('catch', {wall: 'help', snow: [830, 'shrug'],
      plates: [[null, [['THE CATCH', 198, RED]], 1]],
      strips: [[null, ['loc1', 'loc2']]]}),
    local: section('local', {wall: 'help', snow: [230, 'point'],
      plates: [[null, [['OPENAI SAYS:', 132, CREAM]]], [/^claim/i, [['EXISTING ONLY', 132, GOLD]], 1]],
      strips: [[null, ['loc1', 'loc2']], [/^claim/i, ['loc3'], 'new'], [/^listing/i, ['loc4']]]}),
    usonly: section('usonly', {wall: 'help', snow: [830, 'point'],
      plates: [[null, [['U.S. ONLY', 198, GOLD]], 1]],
      strips: [[null, ['loc1', 'loc2', 'loc4']]], ring: [[null, 'loc4']]}),
    trade: section('trade', {wall: 'hub', snow: [230, 'shrug'],
      plates: [[null, [['PLUMBER? ROOFER?', 132, CREAM]], 1], [/^Search/i, [['SEARCH AND SEE', 132, GOLD]], 1]],
      strips: [[/^Search/i, ['hubBoxS']]]}),
    step3: section('step3', {wall: 'help', snow: [830, 'point'],
      plates: [[null, [['STEP 3: PROVE IT', 132, ORANGE]], 1], [/^phone/i, [['PHONE OR EMAIL', 132, GOLD]], 1], [/^website/i, [['OR YOUR WEBSITE', 132, GOLD]], 1]],
      strips: [[null, ['ph1', 'ph2']], [/^website/i, ['vf1', 'vf2'], 'new']]}),
    step4: section('step4', {wall: 'help', snow: [230, 'point'],
      plates: [[null, [['STEP 4: ID CHECK', 132, ORANGE]], 1], [/^before/i, [['BEFORE CHANGES', 132, GOLD]], 1]],
      strips: [[null, ['gov0', 'gov']], [/^before/i, ['id2'], 'new']]}),
    check: section('check', {wall: 'help', snow: [830, 'shrug'],
      plates: [[null, [['OPENAI SAYS:', 132, TEAL]]], [/^guarantee/i, [['NO GUARANTEE', 132, RED]], 1]],
      strips: [[null, ['faq1', 'faq2']]], ring: [[/^guarantee/i, 'faq1', RED]]}),
    /* ---- ask: save it, who to send it to, then the four steps as the last frame (the thing to save) ---- */
    ask: (k, T) => {
      const t0 = k.S('ask'), tS = W(k, 'ask', /^send/i, 0.9), tR = W(k, 'ask', /^Google/i, 2.6);
      k.cut(t0);
      wall(k, 'end');
      snow(k, 540, 'wave', {scale: 1.5, feet: 1660});
      steps(k, T, [[t0 + 0.08, [['SAVE THIS', 198, GOLD]], 1], [tS, [['SEND TO WHOEVER', 132, CREAM], ['RUNS YOUR', 132, CREAM], ['GOOGLE LISTING', 132, GOLD]], 1],
        [tR, [['1 OPEN THE HUB', 132, CREAM], ['2 SEARCH, READ', 132, CREAM], ['3 PROVE IT', 132, CREAM], ['4 ID CHECK', 132, CREAM]], 1]]);
      return {host: false};
    },
  },
};
