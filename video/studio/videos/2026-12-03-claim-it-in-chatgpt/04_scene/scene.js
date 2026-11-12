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

/* ---- the real screens: strips of the captures (image, [x, y, w, h] in its own pixels), found by reading the capture ---- */
const STRIPS = {"hubHead":{"img":"hub","r":[207,365,645,125]},"hubBox":{"img":"hub-box","r":[0,0,560,125]},"annDate":{"img":"announce","r":[279,12,293,55]},"annTitle":{"img":"announce","r":[71,121,848,177]},"annBeta":{"img":"announce-beta","r":[500,11,270,49]},"annSub1":{"img":"announce","r":[67,350,319,51]},"annSub2":{"img":"announce","r":[386,350,467,51]},"localIf":{"img":"help-local","r":[17,8,445,48]},"localStores":{"img":"help-local","r":[417,56,414,42]},"localClaim":{"img":"help-local","r":[16,103,476,49]},"localOnline":{"img":"help-local","r":[463,7,525,49]},"localAdd":{"img":"help-local","r":[17,55,401,49]},"step1":{"img":"help-claim","r":[426,538,532,49]},"methods1":{"img":"help-claim","r":[684,170,354,49]},"methods2":{"img":"help-claim","r":[16,218,492,49]},"phoneHead":{"img":"help-phone","r":[15,154,584,58]},"persona1":{"img":"help-claim","r":[428,354,476,49]},"persona2":{"img":"help-claim","r":[16,402,539,49]},"email1":{"img":"help-email","r":[12,98,425,49]},"email2":{"img":"help-email","r":[773,98,389,49]},"faqQ":{"img":"help-faq","r":[8,12,938,112]},"faqA":{"img":"help-faq","r":[156,209,564,49]},"termsTitle":{"img":"terms-top","r":[22,119,1046,86]},"termsLine1":{"img":"hub-terms","r":[10,12,446,47]},"termsLine2":{"img":"hub-terms","r":[455,12,370,41]},"calls1":{"img":"terms-calls","r":[718,566,491,52]},"calls2":{"img":"terms-calls","r":[14,623,684,50]},"opt":{"img":"terms-calls","r":[694,623,330,53]},"sue1":{"img":"terms-claims","r":[12,127,400,43]},"sue2":{"img":"terms-claims","r":[648,184,513,50]},"searchBox":{"img":"hub-search","r":[20,200,540,122]},"createRow":{"img":"hub-search","r":[20,326,540,112]},"sideNav":{"img":"sidebar","r":[0,96,340,474]},"verifyHead":{"img":"hub-verify","r":[12,17,1021,80]},"verifyTxt":{"img":"hub-verify","r":[18,94,504,47]},"addrBar":{"img":"hub-address","r":[0,0,413,70]}};
/* the page each capture is from decides its key color: a dark page or a light one, so the cast's edge sits on a near color */
const DARK = '#212223', LIGHT = '#FCFDFC';
const TONE = (img) => (/^help/.test(img) ? LIGHT : DARK);
const q3 = (v) => Math.round(v / 3) * 3;
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
const WALLS = {ai: [NIGHT, PLUM], help: ['#24453A', '#2F5A4A'], hub: [SLATE, '#1B1420'], terms: ['#5A2432', WINE], end: [PLUM, '#3D2E45'], go: [DTEAL, '#3E7A62']};
const wall = (k, id) => { const P = px(k), [c, c2] = WALLS[id]; P(0, 0, 360, 640, c); for (let y = 20; y < 640; y += 22) P(0, y, 360, 1, c2); P(0, 386, 360, 254, INK); P(0, 384, 360, 2, c2); };
/* Snow, from the chest up at the bottom of the frame: his head between y 900 and 1180, clear of the captions */
const snow = (k, x, pose, o = {}) => k.snow(x, o.feet || 1632, Object.assign({scale: 1.5, pose, face: x > 540 ? -1 : 1}, o));
const HEAD = 885;
/* where a pointing hand aims at time T: it runs back and forth along the bottom edge of clipping b, on whole low-res pixels */
const follow = (T, t0, b, sx) => { const c = sx > 540 ? b.x + b.w * 0.62 : b.x + b.w * 0.38, a = Math.min(190, b.w * 0.3); return [q3(c + a * Math.sin((T - t0) * 2.6)), b.b - 12]; };
   /* clippings stop here, above his head */

/* One section from a small table:                                                                                      */
/*   wall; snow [x, pose]; plates [[word or null, rows, stamp?], ...] (the first at the cue, the rest on a spoken word);  */
/*   strips [[word or null, [names], 'add' | 'new'], ...]: 'new' clears the clippings before it, 'add' joins the stack;   */
/*   ring [[word or null, name], ...]; mixed: each clipping at its own scale (a headline over body text).                */
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
  const gap = 27, maxW = d.maxW || 972;
  let scs = items.map(([n]) => Math.min(2.4, maxW / STRIPS[n].r[2]));
  if (!d.mixed) { const m = Math.min(...scs); scs = scs.map(() => m); }
  const room = (d.bottom || HEAD) - top - gap * (items.length - 1), tall = items.reduce((s, [n], i) => s + STRIPS[n].r[3] * scs[i], 0), fit = Math.min(1, room / tall);
  let y = top, last = null; const boxes = {};
  items.forEach(([n, t], i) => { const sc = scs[i] * fit, w = q3(STRIPS[n].r[2] * sc), h = q3(STRIPS[n].r[3] * sc); if (T >= t) { boxes[n] = clip(k, L, n, d.left != null ? d.left : 540 - w / 2, y, sc); last = boxes[n]; } y += h + gap; });
  (d.ring || []).forEach(([re, n, c]) => { if (boxes[n] && T >= (re ? W(k, id, re, 1) : t0)) ring(k, boxes[n], c); });
  const [sx, pose0] = d.snow;
  /* he never stands still: a pointing hand runs along the newest clipping the way a finger follows a line; a shrug lifts */
  /* and drops; talking moves his hand on its own (the kit). Motion lives in the things on screen, never in the camera.   */
  const beat = Math.floor((T - t0) / 0.9) % 2, pose = pose0 === 'shrug' ? (beat ? 'point' : 'shrug') : pose0;
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
  images: ['announce', 'announce-beta', 'help-claim', 'help-local', 'help-faq', 'help-email', 'help-phone', 'terms-top', 'terms-calls', 'terms-claims', 'sidebar', 'hub', 'hub-box', 'hub-terms', 'hub-search', 'hub-verify', 'hub-address'],
  trauma: {step1: 0.5},
  sections: {
    /* ---- hook: frame 0 is the news, settled: the Business Hub page's own headline, Snow close, the question up top.  */
    /* At 0.5 s the wall turns and the search box lands (the first change); on "listed" the plate stamps.                */
    hook: (k, T) => {
      const L = [], t1 = 0.5, tL = Math.max(1.2, W(k, 'hook', /^listed/i, 1.9));
      wall(k, T < t1 ? 'hub' : 'go');
      const A = [['YOUR BUSINESS', 132, CREAM], ['IN CHATGPT?', 132, GOLD]], B = [['ALREADY', 132, CREAM], ['LISTED?', 132, GOLD]];
      const top = plateBottom(A) + 30;
      const h1 = clip(k, L, 'hubHead', 540 - q3(STRIPS.hubHead.r[2] * 1.3) / 2, top, 1.3);
      let last = h1;
      if (T >= t1) last = clip(k, L, 'hubBox', 60, h1.b + 30, 1.05);
      if (T >= tL) ring(k, last);
      snow(k, 830, T < t1 ? 'wave' : 'point', T < t1 ? {} : {at: follow(T, 0, last, 830)});
      steps(k, T, [[0, A], [tL, B, 1]]);
      return {host: false, screens: L};
    },
    what: section('what', {wall: 'ai', snow: [200, 'point'], mixed: true,
      plates: [[null, [['OPENAI.COM', 132, TEAL]]], [/^Business/i, [['BUSINESS HUB', 132, GOLD]], 1]],
      strips: [[null, ['annDate', 'annTitle']]]}),
    beta: section('beta', {wall: 'ai', snow: [850, 'point'],
      plates: [[null, [['IN BETA', 198, GOLD]], 1], [/^claim/i, [['CLAIM IT.', 132, CREAM], ['KEEP IT CURRENT', 132, GOLD]], 1]],
      strips: [[null, ['annBeta']], [/^claim/i, ['annSub1', 'annSub2'], 'new']], ring: [[null, 'annBeta']]}),
    who: section('who', {wall: 'help', snow: [200, 'shrug'],
      plates: [[null, [['THE CATCH', 198, RED]], 1], [/^local/i, [['THE CATCH', 132, RED], ['IF YOU ARE LOCAL', 132, CREAM]], 1]],
      strips: [[null, ['localIf']]]}),
    local: section('local', {wall: 'help', snow: [850, 'point'],
      plates: [[null, [['HELP.OPENAI.COM', 132, TEAL]]], [/^claim/i, [['EXISTING', 132, GOLD], ['LISTINGS ONLY', 132, GOLD]], 1]],
      strips: [[null, ['localStores']], [/^claim/i, ['localClaim']]]}),
    usonly: section('usonly', {wall: 'help', snow: [200, 'point'],
      plates: [[null, [['U.S. ONLY', 198, GOLD], ['FOR NOW', 132, CREAM]], 1]],
      strips: [[null, ['localClaim']]], ring: [[null, 'localClaim']]}),
    step1: section('step1', {wall: 'help', snow: [850, 'point'],
      plates: [[null, [STEP(1), ['BUSINESS HUB', 132, CREAM]], 1], [/^OpenAI/i, [['OPENAI SAYS:', 132, CREAM], ['THE SIDEBAR', 132, GOLD]], 1]],
      strips: [[null, ['step1']]], ring: [[/^OpenAI/i, 'step1']]}),
    /* ---- addr: the sidebar as it was on our account (no Business Hub row), then the address bar from our own screenshot ---- */
    addr: (k, T) => {
      const t0 = k.S('addr'), L = [], tT = W(k, 'addr', /^type/i, 1.0);
      k.cut(t0);
      wall(k, 'hub');
      const A = [['NOT THERE?', 132, CREAM]], B = [['CHATGPT.COM', 132, GOLD], ['/BUSINESS-HUB', 132, GOLD]];
      let last;
      if (T < tT) last = clip(k, L, 'sideNav', 60, plateBottom(A) + 30, 1.3);
      else { last = clip(k, L, 'addrBar', 540 - q3(STRIPS.addrBar.r[2] * 2.3) / 2, plateBottom(B) + 36, 2.3); ring(k, last); }
      snow(k, 850, 'point', {at: follow(T, t0, last, 850)});
      steps(k, T, [[t0, A], [tT, B, 1]]);
      return {host: false, screens: L};
    },
    step2: section('step2', {wall: 'hub', snow: [200, 'point'],
      plates: [[null, [STEP(2), ['FIND YOUR NAME', 132, CREAM]], 1], [/^But/i, [['FIRST: READ', 132, CREAM], ['THE SMALL PRINT', 132, RED]], 1]],
      strips: [[null, ['hubBox']], [/^But/i, ['termsLine1', 'termsLine2'], 'new']], ring: [[/^But/i, 'termsLine2', RED]]}),
    terms: section('terms', {wall: 'terms', snow: [850, 'point'],
      plates: [[null, [['CONTINUE =', 132, CREAM], ['ACCEPT TERMS', 132, RED]], 1]],
      strips: [[null, ['termsTitle']]]}),
    calls: section('calls', {wall: 'terms', snow: [200, 'point'],
      plates: [[null, [['OPENAI TERMS', 132, TEAL]]], [/^call/i, [['ITS AI MAY', 132, CREAM], ['CALL YOU', 132, RED]], 1], [/^opt/i, [['YOU CAN', 132, CREAM], ['OPT OUT', 132, TEAL]], 1]],
      strips: [[null, ['calls1']], [/^call/i, ['calls2']], [/^opt/i, ['opt'], 'new']], mixed: true}),
    claims: section('claims', {wall: 'terms', snow: [850, 'shrug'],
      plates: [[null, [['TERMS 10.1', 132, TEAL]]], [/^certain/i, [['COVENANT', 132, CREAM], ['NOT TO SUE', 132, RED]], 1]],
      strips: [[null, ['sue1']], [/^not/i, ['sue2']]]}),
    ours: section('ours', {wall: 'hub', snow: [850, 'point'],
      plates: [[null, [['WE SEARCHED OURS', 132, CREAM]]], [/^not/i, [['NOT LISTED', 198, RED]], 1], [/^create/i, [['CREATE ONE?', 132, GOLD]], 1]],
      strips: [[null, ['searchBox', 'createRow']]], ring: [[/^create/i, 'createRow']], bottom: 960}),
    online: section('online', {wall: 'help', snow: [200, 'point'],
      plates: [[null, [['HELP.OPENAI.COM', 132, TEAL]]], [/^eligible/i, [['FOR ELIGIBLE', 132, CREAM], ['ONLINE BUSINESS', 132, GOLD]], 1]],
      strips: [[null, ['localOnline', 'localAdd']]]}),
    step3: section('step3', {wall: 'help', snow: [850, 'point'],
      plates: [[null, [STEP(3), ['PROVE IT', 132, CREAM]], 1], [/^phone/i, [['PHONE', 132, GOLD], ['OR EMAIL', 132, GOLD]], 1], [/^website/i, [['YOUR DOMAIN', 132, GOLD], ['OR SHOPIFY', 132, GOLD]], 1]],
      strips: [[null, ['phoneHead']], [/^phone/i, ['methods1', 'methods2'], 'new']]}),
    dns: section('dns', {wall: 'hub', snow: [200, 'point'], mixed: true,
      plates: [[null, [['OURS ASKED FOR', 132, CREAM], ['A DNS RECORD', 132, GOLD]], 1]],
      strips: [[null, ['verifyHead', 'verifyTxt']]]}),
    step4: section('step4', {wall: 'help', snow: [850, 'point'],
      plates: [[null, [STEP(4), ['BEFORE CHANGES', 132, CREAM]], 1], [/^identity/i, [['ID CHECK', 132, CREAM], ['WITH PERSONA', 132, GOLD]], 1]],
      strips: [[null, ['persona1', 'persona2']]], ring: [[/^identity/i, 'persona1']]}),
    email: section('email', {wall: 'help', snow: [200, 'point'],
      plates: [[null, [['OPENAI EMAILS', 132, CREAM], ['ITS DECISION', 132, GOLD]], 1]],
      strips: [[null, ['email1', 'email2']]]}),
    check: section('check', {wall: 'help', snow: [850, 'shrug'], mixed: true,
      plates: [[null, [['OPENAI SAYS:', 132, TEAL]]], [/^guarantee/i, [['CLAIMING IT:', 132, CREAM], ['NO GUARANTEE', 132, RED]], 1]],
      strips: [[null, ['faqQ', 'faqA']]], ring: [[/^guarantee/i, 'faqA']]}),
    /* ---- ask: save it, who to send it to, then the four steps as the last frame (the thing to save) ---- */
    ask: (k, T) => {
      const t0 = k.S('ask'), tS = W(k, 'ask', /^send/i, 0.9), tR = W(k, 'ask', /^runs/i, 2.4);
      k.cut(t0);
      wall(k, 'end');
      snow(k, 540, 'wave', {feet: 1668});
      steps(k, T, [[t0 + 0.08, [['SAVE THIS', 198, GOLD]], 1], [tS, [['SEND IT TO YOUR', 132, CREAM], ['LISTING PERSON', 132, GOLD]], 1],
        [tR, [['1 BUSINESS HUB', 132, CREAM], ['2 SEARCH, READ', 132, CREAM], ['3 PROVE IT', 132, CREAM], ['4 ID CHECK', 132, CREAM]], 1]]);
      return {host: false};
    },
  },
};
