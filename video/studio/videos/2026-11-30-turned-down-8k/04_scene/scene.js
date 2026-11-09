/* Scene: Turned down $8,000 (v4 verdict, lesson 1 of the 14-day test; Nov 9, 2026). The whole 1080 x 1920 frame is the  */
/* scene: no host, no level bar, no end card (SCENE.v4; _shared/formats.md "v4"). One function per top-level cue in      */
/* 03_cues/cues.md; every time is a cue start or a spoken word. The story is a real reported one, told as the roofer's   */
/* own account (01_voice/facts.json); the roofer is drawn with the kit's worker and the client with k.client (buyer).    */
/* Words stay inside x 40 to 1040, y 250 to 1170 (the captions own y 1184 to 1382), every row size 132 or more (66 px    */
/* caps; render critic r0: the 66 rows read 33 px, too small for a phone); nothing stands unchanged over 4 s.            */
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', DTEAL = '#2F6F67', NIGHT = '#1B1420', PLUM = '#2B2033', WINE = '#7A3442', SKY = '#87CEEB';
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
/* a centered plate of rows [[text, size, color], ...] with its top at y; returns its bottom. Sizes are whole steps of */
/* the display face (66, 132, 198) so the pixels stay square. */
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
/* the same plate landing as a stamp at t0 (put a [sfx: stamp] cue there for the hit-stop) */
const stampPlate = (k, rows, y, t0, o = {}) => {
  const hgt = rows.reduce((a, [, z]) => a + z, 0) + 18 * (rows.length - 1) + 66;
  return k.stampIn(t0, () => plate(k, rows, y, o), {at: [o.cx || 540, y + hgt], freeze: o.freeze, drop: o.drop});
};

/* the yard: sky, a sun, a house with half its roof stripped and a ladder, the lawn running to the bottom of the frame. */
/* z 2 is the close shot: the same yard at twice the size (whole pixels), the lawn line near y 1000, the wall behind.   */
const yard = (k, dim = 0, z = 1) => {
  const ctx = k.ctx, P = px(k), F = Math.floor(k.T * 30 + 0.005);
  ctx.save();
  if (z !== 1) { ctx.translate(-540, -836); ctx.scale(z, z); }
  P(0, 0, 360, 250, SKY); P(0, 250, 360, 24, '#BDE6F5');
  P(286, 96, 26, 26, GOLD); P(290, 92, 18, 34, GOLD); P(282, 100, 34, 18, GOLD);
  const cx = (Math.floor(F / 5) % 440) - 70; P(cx, 110, 46, 9, CREAM); P(cx + 10, 103, 24, 7, CREAM); P((cx + 230) % 440 - 70, 150, 36, 8, CREAM);
  /* the house */
  P(54, 196, 252, 110, INK); P(57, 199, 246, 107, SAND); for (let y = 208; y < 306; y += 9) P(57, y, 246, 1, '#D2BCA2');
  for (let i = 0; i < 34; i++) P(40 + i * 3.6, 196 - i * 1.6, 280 - i * 7.2, 2, i % 6 === 5 ? '#5A2432' : WINE);   /* the roof, shingle rows */
  for (let i = 4; i < 20; i++) P(170 + (i - 4) * 1.2, 196 - i * 1.6, 90 - (i - 4) * 4.4, 2, i % 3 ? '#9AA0AD' : '#6B7080');   /* the stripped patch, felt showing */
  P(92, 232, 44, 40, INK); P(95, 235, 38, 34, '#5B8FB9'); P(113, 235, 2, 34, INK); P(95, 251, 38, 2, INK);
  P(196, 240, 40, 66, INK); P(199, 243, 34, 63, DTEAL); P(226, 274, 3, 3, GOLD);
  P(300, 150, 3, 156, '#8C5A33'); P(314, 150, 3, 156, '#8C5A33'); for (let y = 160; y < 300; y += 14) P(300, y, 17, 2, '#B07A47');   /* the ladder */
  /* the lawn, to the bottom of the frame */
  P(0, 306, 360, 334, '#3E7A62'); P(0, 306, 360, 3, '#2F5A4A');
  for (let i = 0; i < 70; i++) P((i * 53) % 360, 314 + (i * 37) % 320, 3, 1, '#2F5A4A');
  P(0, 388, 360, 252, '#2F5A4A'); for (let i = 0; i < 40; i++) P((i * 71) % 360, 394 + (i * 43) % 240, 3, 1, '#24453A');
  ctx.restore();
  if (dim) P(0, 0, 360, 640, `rgba(18,13,20,${dim})`);
};
/* the cast. Wide shot: whole figures, feet on the lawn (y 1150). Close shot: from the waist up, feet far below the frame's */
/* safe band, so the faces sit between y 700 and 1100 and the plates own the band above them. */
const roofer = (k, x, sc, pose, o = {}) => k.snow(x, o.feet || 1150, Object.assign({scale: sc, pose, face: 1, talk: false}, o));
const client = (k, x, sc, pose, mood, o = {}) => k.client(x, o.feet || 1150, Object.assign({role: 'buyer', scale: sc, pose, mood, face: -1}, o));

window.SCENE = {
  look: 'arcade',
  v4: true,
  host: false,
  endCard: false,
  images: [],
  trauma: {'ask.you': 0.8},
  sections: {
    /* ---- hook: frame 0 is the fight, close: the two of them and $8,000 JOB; at 0.8 s HE SAID NO. lands under it; on ---- */
    /* "eight" a cut to the roofer alone, close, who shrugs and waves it off (viewers r1 and r2: the wide shot shrank them ---- */
    /* and stood still; r2: the card in the client's hand read as "something small and blue", so his palms are up ---- */
    /* instead); on "The client only wanted" a cut to the client: $200 OFF ---- */
    hook: (k, T) => {
      const tNo = 0.8, tSolo = Math.max(1.7, wordT(k, 'hook', /^eight/i, 2.0) - 0.1), tAsk = k.S('hook.ask');
      const hero = () => (T < tNo - 0.1 ? plate(k, [['$8,000 JOB', 198, GOLD]], 264)
        : stampPlate(k, [['$8,000 JOB', 198, GOLD], ['HE SAID NO.', 132, RED]], 264, tNo, {freeze: 4}));
      if (T < tSolo) {
        yard(k, T >= tNo ? 0.22 : 0, 2);
        roofer(k, 250, 1.9, T >= tNo ? 'shrug' : 'stand', {feet: 1700}); client(k, 840, 2.1, 'argue', 'calm', {feet: 1700});
        hero();
      } else if (T < tAsk) {
        k.cut(tSolo);
        yard(k, 0.22, 2);
        /* render critic (final render, r0): a figure moved sideways with still legs reads as sliding; the kit has no */
        /* walk, so he stays put: a shrug, then he waves it off */
        roofer(k, 540, 2.3, T < tSolo + 0.9 ? 'shrug' : 'wave', {feet: 1840});
        plate(k, [['$8,000 JOB', 198, GOLD], ['HE SAID NO.', 132, RED]], 264);
      } else {
        k.cut(tAsk);
        yard(k, 0.22, 2);
        client(k, 700, 2.4, 'argue', 'smug', {feet: 1790, talk: T < tAsk + 1.4});
        stampPlate(k, [['CLIENT WANTED', 132, CREAM], ['$200 OFF', 198, RED]], 264, tAsk, {freeze: 4});
      }
      return {host: false};
    },

    /* ---- bids: the roofer tells it (viewer r0: "he" must be seen talking; r1: the account plate needs its 2 s), ---- */
    /* then on "two lower bids" the client close: a flipper, the two bids, then the ask ---- */
    bids: (k, T) => {
      const t0 = k.S('bids'), tTwo = k.S('bids.two'), tDrop = k.S('bids.drop');
      k.cut(t0);
      yard(k, 0.45, 2);
      if (T < tTwo) {
        roofer(k, 540, 2.0, 'talk', {feet: 1700, talk: true});
        plate(k, [['HIS ACCOUNT,', 132, CREAM], ['VIA THE DAILY DOT', 132, GOLD]], 264);
        return {host: false};
      }
      k.cut(tTwo);
      client(k, 860, 2.3, T >= tDrop ? 'argue' : 'stand', 'smug', {feet: 1790, talk: T >= tDrop && T < tDrop + 1.6});
      if (T < tDrop) {
        plate(k, [['THE CLIENT:', 132, CREAM], ['A FLIPPER', 132, GOLD]], 264, {cx: 370});
        if (T >= tTwo + 0.25) stampPlate(k, T >= tTwo + 0.8 ? [['LOWER BIDS:', 132, CREAM], ['$7,500', 132, TEAL], ['$7,800', 132, TEAL]] : [['LOWER BIDS:', 132, CREAM], ['$7,500', 132, TEAL]], 630, T >= tTwo + 0.8 ? tTwo + 0.8 : tTwo + 0.33, {cx: 370, drop: 0.08});
      } else stampPlate(k, [['CLIENT:', 132, INK], ['DROP', 132, WINE], ['$200?', 198, RED]], 264, tDrop, {cx: 330, bg: CREAM, rule: RED, drop: 0.08});
      return {host: false};
    },

    /* ---- no: the roofer, close; one stamp ---- */
    no: (k, T) => {
      const t0 = k.S('no'), tNo = wordT(k, 'no', /^no/i, 0.6) - 0.15;
      k.cut(t0);
      yard(k, 0.22, 2);
      roofer(k, 320, 2.2, T >= tNo ? 'shrug' : 'stand', {feet: 1720});
      if (T >= tNo - 0.1) stampPlate(k, [['NO.', 264, CREAM]], 290, tNo, {cx: 740, bg: RED, rule: INK, freeze: 4});
      return {host: false};
    },

    /* ---- why: he says it was not the $200; the client cared about price, not quality; a problem job; relief ---- */
    why: (k, T) => {
      const t0 = k.S('why'), tPrice = k.S('why.price'), tNot = wordT(k, 'why.price', /^not$/i, 1.6) - 0.15, tFlag = k.S('why.flag'), tJob = k.S('why.flag.job'), tRel = k.S('why.relief');
      if (T < tPrice) {
        k.cut(t0);
        yard(k, 0.45, 2);
        roofer(k, 250, 1.9, 'talk', {feet: 1740, talk: true}); client(k, 840, 2.1, 'refuse', 'cross', {feet: 1740});
        const b = plate(k, [['HE SAYS IT WAS', 132, CREAM], ['NOT ABOUT', 132, CREAM], ['THE $200', 132, GOLD]], 264);
        if (T >= t0 + 0.9) { const w = k.measure('THE $200', {size: 132}); k.shape(k.rectPts(540 - w / 2 - 12, b - 126, Math.round((w + 24) * clamp((T - t0 - 0.9) / 0.25) / 3) * 3, 15, 0), {fill: RED, line: false}); }
      } else if (T < tFlag) {
        k.cut(tPrice);
        yard(k, 0.45, 2);
        client(k, 540, 2.4, 'argue', 'smug', {feet: 1840, talk: T < tPrice + 1.5});
        if (T < tNot - 0.06) plate(k, [['CLIENT CARED', 132, CREAM], ['ABOUT PRICE', 132, GOLD]], 264);
        else stampPlate(k, [['CLIENT CARED', 132, CREAM], ['ABOUT PRICE', 132, GOLD], ['NOT QUALITY', 132, RED]], 264, tNot, {drop: 0.06});
      } else if (T < tRel) {
        k.cut(tFlag);
        yard(k, 0.5, 2);
        /* viewer r1: "To him," played over the client; the cut to the roofer now comes on "To", the stamp on "problem" */
        roofer(k, 290, 2.0, T >= tJob ? 'point' : 'talk', {feet: 1700, at: [700, 600], talk: T < tJob});
        const P = px(k);
        k.stampIn(tJob, () => { P(196, 92, 4, 46, INK); P(200, 92, 56, 30, RED); P(200, 122, 40, 5, WINE); }, {at: [660, 414], freeze: 4});
        if (T < tJob - 0.1) plate(k, [['TO HIM:', 132, CREAM]], 420, {cx: 740});   /* viewer r2: he stood on an empty frame for 1.4 s */
        else stampPlate(k, [['TO HIM:', 132, CREAM], ['PROBLEM', 132, CREAM], ['JOB', 198, RED]], 420, tJob, {cx: 740, freeze: 4});
      } else {
        k.cut(tRel);
        yard(k, 0.1, 2);
        roofer(k, 420, 2.0, 'wave', {feet: 1700});   /* he stays put (no sliding: the kit has no walk) */
        plate(k, [['HE FELT', 132, INK], ['RELIEF', 198, DTEAL]], 264, {bg: CREAM, rule: TEAL});
      }
      return {host: false};
    },

    /* ---- ask: the frame splits into two verdicts on the same man (viewer r1: the client under PRIDE read as roofer ---- */
    /* against client): the roofer stands on both sides, at ease on the navy side, shrugging on the wine side; both ---- */
    /* halves are there from the first frame; the caption says "You decide." (no mark between them: r2) ---- */
    ask: (k, T) => {
      const t0 = k.S('ask'), tPride = k.S('ask.pride'), tLost = wordT(k, 'ask.pride', /^cost/i, 1.4) - 0.15, tYou = k.S('ask.you');
      k.cut(t0);
      const P = px(k);
      /* render critic r1 note: navy hid his navy legs; slate keeps the jacket, the legs and the cap all off the wall */
      P(0, 0, 180, 640, '#4A4E5A'); P(180, 0, 180, 640, WINE); P(178, 0, 4, 640, INK);
      for (let y = 20; y < 640; y += 22) { P(0, y, 178, 1, '#6B7080'); P(182, y + 11, 178, 1, '#5A2432'); }
      roofer(k, 270, 1.6, T >= tYou ? 'point' : 'wave', {feet: 1690, at: [540, 1900]});   /* on "You decide" both of him turn it over to the viewer */
      roofer(k, 810, 1.6, T >= tPride ? 'shrug' : 'stand', {feet: 1690, face: -1});
      if (T < t0 + 0.34) plate(k, [['SMART', 132, CREAM], ['CALL:', 132, CREAM]], 264, {cx: 270, bg: INK, rule: TEAL});
      else stampPlate(k, [['SMART', 132, CREAM], ['CALL:', 132, CREAM], ['PROBLEM', 132, TEAL], ['JOB', 132, TEAL]], 264, t0 + 0.4, {cx: 270, bg: INK, rule: TEAL, drop: 0.06});
      if (T < tPride - 0.08) plate(k, [['OR', 132, CREAM]], 264, {cx: 810, bg: INK, rule: RED});   /* viewer r2: an empty right side looked unfinished */
      else if (T < tLost - 0.06) stampPlate(k, [['OR', 132, CREAM], ['PRIDE:', 132, CREAM]], 264, tPride, {cx: 810, bg: INK, rule: RED, drop: 0.08});
      else if (T >= tLost - 0.06) stampPlate(k, [['OR', 132, CREAM], ['PRIDE:', 132, CREAM], ['LOST', 132, GOLD], ['THE JOB', 132, GOLD]], 264, tLost, {cx: 810, bg: INK, rule: RED, drop: 0.06});
      return {host: false};
    },
  },
};
