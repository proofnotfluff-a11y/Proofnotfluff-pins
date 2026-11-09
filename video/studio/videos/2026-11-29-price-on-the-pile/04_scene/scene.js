/* Scene: Price on the pile (proven, our own version of research/PROVEN.md row 11; Nov 9, 2026). One function per top-  */
/* level cue in 03_cues/cues.md; every time from a cue start or a spoken word (wordT). Worlds: hook = the cover board,  */
/* then the driveway (the van, its trailer heaped with junk, the homeowner, k.client, facing the viewer as if the viewer */
/* is the crew); offer = the same drive, her low offer; send = the driver's card, built line by line, held still; why = */
/* the before and after rows; receipt = the ACHR News line, then the slot machine (data.js); button = the drive before  */
/* the job, the pile on the ground, the two choices. The $400, the $200 and her lines are ours (EXAMPLE on the numbers). */
/* Every room change is a plain cut on the word (Todd's call 1, Nov 9).                                                 */
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', DTEAL = '#2F6F67', GREY = '#9AA0AD', NIGHT = '#1B1420', SLATE = '#4A4E5A', WINE = '#7A3442';
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eo = (x) => 1 - Math.pow(1 - clamp(x), 3);

/* ---- the pixel kit (low-res units: 360 x 640, one pixel = 3 frame units), as in the lessons before ---- */
const px = (k) => {
  const ctx = k.ctx, T = k.T, F = Math.floor(T * 30 + 0.005);
  const P = (x, y, w, h, c) => { x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h); if (w > 0 && h > 0 && c) { ctx.fillStyle = c; ctx.fillRect(x * 3, y * 3, w * 3, h * 3); } };
  const fr = (t0) => Math.floor((T - t0) * 30 + 0.005);
  const ease = (t0, frames, dist) => Math.round(dist * (1 - eo(fr(t0) / frames)));
  return {P, fr, ease, F, T};
};
const WS = () => (window.WORDS && window.WORDS.words) || [];
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
const host = (k, pose, sc = 0.55) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: sc, hostX: 150});
const stampBox = (k, s, cx, y, t0, o = {}) => {
  const size = o.size || 66, c = o.color || GOLD, w = Math.round((k.measure(s, {size}) + 54) / 6) * 6, h = size + 36, x = Math.round((cx - w / 2) / 3) * 3;
  k.stampIn(t0, () => {
    k.shape(k.rectPts(x + 6, y + 6, w, h, 0), {fill: INK, line: false}); k.shape(k.rectPts(x, y, w, h, 0), {fill: o.bg || NIGHT, line: false});
    k.shape(k.rectPts(x + 6, y + 6, w - 12, 6, 0), {fill: c, line: false}); k.shape(k.rectPts(x + 6, y + h - 12, w - 12, 6, 0), {fill: c, line: false});
    k.text(s, x + w / 2, y + 18, {size, color: c, align: 'center'});
  }, {at: [x + w / 2, y + h], freeze: o.freeze});
};

/* the driveway: sky with clouds drifting a pixel every 4 frames, a house on the right, the lawn, the grey drive */
const drive = (k, d) => {
  const {P, F} = d;
  P(0, 0, 360, 140, '#8EC3E0'); P(0, 140, 360, 20, '#A9D3E8');
  const cx = (Math.floor(F / 4) % 420) - 60; P(cx, 40, 40, 8, CREAM); P(cx + 8, 34, 22, 6, CREAM); P((cx + 210) % 420 - 60, 70, 34, 7, CREAM);
  /* the house */
  P(214, 70, 140, 6, INK); for (let i = 0; i < 24; i++) P(220 + i * 2.5, 70 - i, 140 - i * 5, 1, '#7A3442');
  P(222, 76, 124, 160, INK); P(224, 76, 120, 158, '#E6D3BC'); for (let y = 82; y < 230; y += 8) P(224, y, 120, 1, '#D2BCA2');
  P(296, 170, 30, 64, INK); P(298, 172, 26, 62, DTEAL); P(318, 200, 3, 3, GOLD);
  P(238, 104, 36, 32, INK); P(240, 106, 32, 28, '#5B8FB9'); P(255, 106, 2, 28, INK); P(240, 119, 32, 2, INK);
  /* the lawn and the drive */
  P(0, 234, 360, 183, '#4F8A5B'); for (let i = 0; i < 40; i++) P((i * 47) % 360, 240 + (i * 29) % 170, 2, 1, '#3E7A62');
  P(0, 236, 214, 36, '#9AA0AD'); P(0, 236, 214, 2, '#C9CCD3'); P(0, 270, 214, 2, '#6B7080');
};
/* the trailer, drawn at twice the pixel size so it reads on a phone: heaped (full true) or empty; it sits on the drive */
/* with its tongue running off the left edge (the truck is off frame) */
const Q2 = (d, ox, oy) => (x, y, w, h, c) => d.P(ox + x * 2, oy + y * 2, w * 2, h * 2, c);
const trailer = (k, d, full) => {
  const Q = Q2(d, 6, 130);
  Q(-10, 52, 16, 2, INK);                                       /* the tongue, off frame left */
  Q(4, 44, 86, 4, INK); Q(6, 46, 82, 12, '#6B7080'); Q(6, 46, 82, 2, '#C9CCD3'); Q(4, 58, 86, 3, INK);
  Q(4, 30, 3, 16, INK); Q(87, 30, 3, 16, INK); Q(4, 30, 86, 2, '#4A4E5A');   /* the side rails */
  [[24, 62], [70, 62]].forEach(([x, y]) => { Q(x - 5, y - 1, 11, 8, INK); Q(x - 3, y, 7, 6, SLATE); Q(x - 1, y + 2, 3, 2, d.F % 16 < 8 ? GREY : '#C9CCD3'); });
  if (!full) return;
  junk(k, d, 6, 44, Q);
};
/* the junk: a couch, a mattress on edge, boxes, an old fridge; two of them bob a pixel on a slow beat so the pile never */
/* sits flat. Q is the 2x painter; x, base in its units */
const junk = (k, d, x, base, Q) => {
  const {F} = d, b = (F >> 4) % 2;
  Q(x + 2, base - 16, 40, 16, INK); Q(x + 3, base - 15, 38, 14, '#8C5A33'); Q(x + 3, base - 15, 38, 3, '#B07A47'); Q(x + 4, base - 21, 6, 6, '#8C5A33'); Q(x + 34, base - 21, 6, 6, '#8C5A33');
  Q(x + 46, base - 38 - b, 20, 38, INK); Q(x + 47, base - 37 - b, 18, 36, CREAM); for (let y = base - 34; y < base - 2; y += 6) Q(x + 47, y - b, 18, 2, '#9EC7E0');
  Q(x + 68, base - 44, 14, 44, INK); Q(x + 69, base - 43, 12, 42, '#C9CCD3'); Q(x + 69, base - 26, 12, 1, SLATE); Q(x + 79, base - 38, 1, 6, SLATE);
  Q(x + 8, base - 32 + b, 14, 14, INK); Q(x + 9, base - 31 + b, 12, 12, '#C99A5B'); Q(x + 9, base - 26 + b, 12, 1, '#8C5A33');
  Q(x + 24, base - 28, 12, 12, INK); Q(x + 25, base - 27, 10, 10, '#D9AE73');
};
/* the pile on the drive before the job, at the same 2x size, left of the empty trailer's spot */
const pile = (k, d) => junk(k, d, 6, 58, Q2(d, 6, 130));
/* her bubble: a cream box with a tail toward her head, left of her, text wrapped to fit inside x 72 to 650 */
const bubble = (k, d, s, t0, y = 96) => {
  if (k.T < t0) return null;
  const up = d.ease(t0, 4, 6), f = k.fit(s, 66, 560, 52), lh = f.size * 1.15, h = Math.ceil((f.lines.length * lh + 40) / 3) * 3, Y = y * 3 + up * 3;
  k.shape(k.rectPts(60, Y + 6, 618, h, 0), {fill: INK, line: false});
  k.shape(k.rectPts(54, Y, 618, h, 0), {fill: CREAM, line: false});
  k.shape(k.rectPts(660, Y + h - 42, 36, 24, 0), {fill: CREAM, line: false});
  f.lines.forEach((ln, i) => k.text(ln, 78, Y + 20 + i * lh, {size: f.size, color: INK}));
  return {y: Y, h};
};
const drift = (k) => { const d = px(k), off = Math.floor(k.T * 30) % 16; for (let y = 418 - 16 + off; y < 640; y += 16) { const y0 = Math.max(418, y), y1 = Math.min(640, y + 8); if (y1 > y0) d.P(0, y0, 360, y1 - y0, '#2B2033'); } };

const CARD = ['POINT AT THE PILE', '"THIS LOAD IS', '[YOUR PRICE].', 'GOOD TO START?"', 'WAIT FOR HER YES', 'NO YES, NO LIFT.'];

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'PRICE ON THE PILE',
  sendLine: 'Send this to your driver.',
  endSend: ['POINT AT THE PILE', '"THIS LOAD IS [YOUR PRICE].', 'GOOD TO START?"', 'WAIT FOR HER YES'],
  trauma: {},
  sections: {
    /* ---- hook: frame 0 is the cover board over the drive; at 0.6 s a plain cut to the drive, the full trailer, her ---- */
    /* arms folded; on "four" her bubble with the made-up $400 and its EXAMPLE tag ---- */
    hook: (k, T) => {
      const d = px(k), tShop = 0.9, tFour = Math.max(tShop + 0.6, wordT(k, 'hook', /^four/i, 2.0) - 0.25);
      drive(k, d); if (T >= tShop) trailer(k, d, true);
      if (T < tShop) {
        /* design r0: the cover is this lesson's own picture, the pile up close with its price tag, not a board */
        d.P(0, 0, 360, 417, 'rgba(18,13,20,0.25)');
        junk(k, d, 2, 44, (x, y, w, h, c) => d.P(40 + x * 3, 104 + y * 3, w * 3, h * 3, c));
        /* design r2: the tag bigger, hung up and left on a short string so the pile shows under it */
        k.shape(k.rectPts(498, 258, 6, 36, 0), {fill: INK, line: false});
        k.shape(k.rectPts(102, 300, 708, 240, 0), {fill: INK, line: false}); k.shape(k.rectPts(90, 288, 708, 240, 0), {fill: CREAM, line: false});
        k.text('$400?', 444, 300, {size: 280, color: RED, align: 'center', drop: INK});
        k.exampleTag(798, 546, {right: true});
        k.shape(k.rectPts(282, 816, 720, 138, 0), {fill: '#253048', line: false}); k.shape(k.rectPts(282, 816, 720, 6, 0), {fill: RED, line: false});
        k.text("THE TRAILER'S FULL.", 306, 834, {size: 52, color: CREAM}); k.text("SHE WON'T PAY IT.", 306, 894, {size: 52, color: CREAM});
        return host(k, 'point');
      }
      k.cut(tShop);
      if (T < tFour) {
        k.client(780, 810, {role: 'homeowner', pose: 'refuse', mood: 'cross', scale: 0.95});
        /* the cover's two lines stay up over the wide shot, so they can be read */
        k.shape(k.rectPts(54, 258, 636, 150, 0), {fill: '#253048', line: false}); k.shape(k.rectPts(54, 258, 636, 6, 0), {fill: RED, line: false});
        k.text("THE TRAILER'S FULL.", 78, 276, {size: 52, color: CREAM}); k.text("SHE WON'T PAY IT.", 78, 336, {size: 52, color: CREAM});
        return host(k);
      }
      /* the close shot on "four": a plain cut in, the drive darker behind her, her bubble with the made-up $400 */
      k.cut(tFour);
      d.P(0, 0, 360, 417, 'rgba(18,13,20,0.35)');
      k.client(760, 930, {role: 'homeowner', pose: 'talk', mood: 'cross', scale: 1.3, talk: T < tFour + 1.0});
      const b = bubble(k, d, '$400? TOO MUCH.', tFour, 96);
      if (b) k.exampleTag(72, b.y + b.h + 18);
      return host(k, 'shrug');
    },

    /* ---- offer: the same drive; her bubble on "two hundred" (EXAMPLE); the slam on "dump" ---- */
    offer: (k, T) => {
      const d = px(k), tTwo = wordT(k, 'offer', /^give$/i, 2.3) - 0.25, tDump = wordT(k, 'offer', /^dump/i, 5.5) - 0.25;
      /* design r2: a push-in, the full trailer up close and her nearer, so the room reads as a new shot */
      drive(k, d); d.P(0, 0, 360, 417, 'rgba(18,13,20,0.2)');
      junk(k, d, 2, 44, (x, y, w, h, c) => d.P(4 + x * 3, 120 + y * 3, w * 3, h * 3, c));
      d.P(4, 252, 260, 12, INK); d.P(6, 254, 256, 8, '#6B7080');
      k.client(800, 900, {role: 'homeowner', pose: 'argue', mood: 'smug', scale: 1.2, talk: T >= tTwo && T < tTwo + 1.2});
      const b = bubble(k, d, "I'LL GIVE YOU $200.", tTwo, 96);
      if (b) k.exampleTag(72, b.y + b.h + 18);
      if (T >= tDump) stampBox(k, 'DUMP IT BACK?', 540, 480, tDump, {color: GOLD, bg: WINE, size: 66, freeze: 4});   /* render critic r0: on a plate */
      return host(k, T >= tDump ? 'shrug' : null);
    },

    /* ---- fix: the drive before the job, the pile on the ground, the trailer empty; the slam on "say" ---- */
    fix: (k, T) => {
      const t0 = k.S('fix'), d = px(k), tSay = wordT(k, 'fix', /^say$/i, 1.0) - 0.2;
      k.cut(t0);
      drive(k, d); pile(k, d);
      k.client(780, 810, {role: 'homeowner', pose: 'stand', mood: 'calm', scale: 0.95});
      /* viewer r0 and render critic r0: the rewind said on screen, the line on a plate left of the house */
      k.shape(k.rectPts(60, 264, 618, 240, 0), {fill: INK, line: false}); k.shape(k.rectPts(54, 258, 618, 240, 0), {fill: '#253048', line: false}); k.shape(k.rectPts(54, 258, 618, 6, 0), {fill: TEAL, line: false});
      k.text('BEFORE YOU LOAD', 78, 276, {size: 52, color: CREAM});
      if (T >= tSay) { k.slam('SAY THE PRICE', 78, 342, tSay, {size: 66, color: GOLD, drop: INK, from: 0.4}); k.slam('AT THE PILE', 78, 418, tSay + 0.3, {size: 66, color: GOLD, drop: INK, from: 0.4}); }
      return host(k, T >= tSay ? 'point' : null);
    },

    /* ---- send: a plain cut to the card; its lines arrive as each is spoken; full, it holds dead still (only the ---- */
    /* stripes behind it drift); no EXAMPLE tag on it (no made-up number on the card) ---- */
    send: (k, T) => {
      const t0 = k.S('send'), d = px(k), w = (re, dd) => wordT(k, 'send', re, dd) - 0.2;
      const tThis = w(/^\W*this\b/i, 7.0), on = [w(/^point/i, 5.5), tThis, tThis + 0.6, Math.max(tThis + 0.7, w(/^\W*good/i, 8.2)), w(/^wait/i, 9.4), w(/^no$/i, 10.6)];   /* send r0, design r0: reading order */
      d.P(0, 0, 360, 417, '#2B3A4E'); { const so = d.F % 20; for (let x = so - 20; x < 360; x += 20) d.P(Math.max(0, x), 0, Math.max(0, Math.min(x + 10, 360) - Math.max(0, x)), 417, '#34465C'); }
      k.cut(t0);
      const c = k.sendCard({at: t0, who: 'FOR YOUR DRIVER', title: 'BEFORE YOU LIFT', lines: CARD, linesOn: on});
      return host(k, c ? 'point' : null);
    },

    /* ---- why: two rows, before (teal) and after (red); the after row shakes once on "fight" ---- */
    why: (k, T) => {
      const t0 = k.S('why'), d = px(k), tFight = wordT(k, 'why', /^fight/i, 2.0) - 0.15, tPrice = wordT(k, 'why', /^price/i, 0.6) - 0.2, {P} = d;
      k.cut(t0);
      P(0, 0, 360, 417, NIGHT);
      const so = d.F % 24;   /* qa r1: the stripes move a pixel every frame and are wider, so the row never sits flat */
      P(12, 84, 336, 90, INK); P(10, 82, 336, 90, DTEAL); for (let x = so - 24; x < 346; x += 24) P(Math.max(10, x), 82, 10, 90, '#357C73');
      { const u = Math.min(1, (T - t0) / 1.2); P(24, 166, Math.round(300 * u), 3, GOLD); }   /* a gold rule draws under A YES = A DEAL */
      const sh = T >= tFight && T < tFight + 0.25 ? ((d.F % 2) ? 2 : -2) : 0;
      if (T < tPrice) { P(10, 182, 336, 90, '#2B2033'); P(10, 182, 336, 2, '#5A3A48'); P(10, 270, 336, 2, '#5A3A48'); }   /* design r2: the empty row in place, dim */
      if (T >= tPrice) { P(12 + sh, 184, 336, 90, INK); P(10 + sh, 182, 336, 90, WINE); for (let x = 346 - so; x > 10; x -= 24) P(Math.max(10, x), 182, 4, 90, '#8A3E4C'); }   /* design r0: no empty panel */
      k.text('UP FRONT', 72, 270, {size: 52, color: CREAM});
      k.text('A YES = A DEAL', 72, 360, {size: 80, color: GOLD, drop: INK});
      if (T >= tPrice) k.text('AFTER THE WORK', 72 + sh * 3, 570, {size: 52, color: CREAM});
      if (T >= tFight - 0.6) k.text('A PRICE = A FIGHT', 72 + sh * 3, 660, {size: 80, color: GOLD, drop: INK});
      return host(k, T >= tFight ? 'shrug' : null);
    },

    /* ---- receipt (viewer r0, design r0): no clipping and no slot machine; the survey's own header, ten houses, seven ---- */
    /* light up on "Seventy" with 70% (data.js), the line it measured, the source tag held the whole time ---- */
    receipt: (k, T) => {
      const t0 = k.S('receipt'), d = px(k), n = k.data.numbers.pct, tSev = wordT(k, 'receipt', /^seventy/i, 6.0) - 0.3, {P} = d;
      const lit = Math.round(Number(n.value != null ? n.value : parseFloat(n.shown)) / 10);
      k.cut(t0);
      P(0, 0, 360, 417, '#253048'); for (let y = (d.F >> 2) % 8 - 8; y < 417; y += 8) P(0, Math.max(0, y), 360, 3, NIGHT);
      /* viewer r1 and design r1: the number from the first frame of the beat, big; the houses light one by one up to */
      /* "Seventy", the seventh on the word */
      /* design r2: 70% left-aligned and big; the lines under it; ten small houses light in the band right of Snow */
      k.slam(n.shown, 72, 330, t0, {size: 300, color: GOLD, drop: INK, from: 0.3});
      k.text('OF HOMEOWNERS SURVEYED', 72, 640, {size: 52, color: CREAM});
      k.text('MORE LIKELY TO CALL', 72, 696, {size: 52, color: CREAM});
      k.text('THE ONE UPFRONT ON PRICE', 72, 752, {size: 52, color: CREAM});
      for (let i = 0; i < 10; i++) {
        const x = 104 + i * 24, y = 278, on = i < lit && T >= t0 + 0.3 + (tSev + 0.3 - t0 - 0.3) * i / Math.max(1, lit - 1);
        P(x, y + 8, 20, 18, INK); P(x + 1, y + 9, 18, 16, on ? '#E6D3BC' : SLATE);
        for (let r = 0; r < 8; r++) P(x + 10 - r * 1.2, y + r, r * 2.4, 1, on ? WINE : '#3D2E45');
        P(x + 7, y + 17, 6, 9, INK); P(x + 3, y + 11, 4, 4, on ? GOLD : NIGHT); P(x + 13, y + 11, 4, 4, on ? GOLD : NIGHT);
      }
      k.sourceTag('ACHR News, Dec 23, 2024, HVAC', 72, 270, {color: SAND});
      return host(k, T >= tSev ? 'point' : null);
    },

    /* ---- button: the drive before the job: the pile on the ground, the trailer empty; the two choices; the stamp ---- */
    button: (k, T) => {
      const t0 = k.S('button'), d = px(k), tDoes = wordT(k, 'button', /^does/i, 1.6) - 0.25, tPile = wordT(k, 'button', /^pile/i, 2.5) - 0.25, tTr = wordT(k, 'button', /^trailer/i, 3.6) - 0.25;
      k.cut(t0);
      drive(k, d); pile(k, d);
      k.client(780, 810, {role: 'homeowner', pose: 'stand', mood: 'calm', scale: 0.95});
      const card = (s, x, at, c) => { if (T < at) return; const up = d.ease(at, 4, 8); k.shape(k.rectPts(x + 6, 396 + up * 3, 432, 96, 0), {fill: INK, line: false}); k.shape(k.rectPts(x, 390 + up * 3, 432, 96, 0), {fill: c, line: false}); k.text(s, x + 216, 406 + up * 3, {size: 52, color: INK, align: 'center'}); };
      card('ON THE PILE', 66, tPile, TEAL); card('ON THE TRAILER', 534, tTr, ORANGE);
      if (T >= tDoes) stampBox(k, 'WHERE DOES YOUR PRICE GO?', 540, 258, tDoes, {color: GOLD, bg: WINE, size: 52, freeze: 4});
      return host(k, T >= tTr ? 'shrug' : null);
    },
  },
};
for (const [n, f] of Object.entries(window.SCENE.sections)) window.SCENE.sections[n] = (k, T) => { const r = f(k, T); drift(k); return r; };
