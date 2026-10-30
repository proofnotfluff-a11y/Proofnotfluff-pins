// Scene: Answer your reviews; many contractors don't (Lesson 7, Reviews Clinic, arcade). One function per top-level cue in
// 03_cues/cues.md. Numbers only from k.data (brief.md -> data.js). Every time comes from a cue start (k.S) or a spoken word
// (wordT), so a re-voiced take moves the picture with it.
// Worlds (brief.md): hook, replies, caveat = the chat in the truck (the review inbox; the hook cuts in to a close-up of the
// one-star review and back out); stakes, close = the slot machine;
// gap, turn = the arcade high-score table (its rows drawn here in the set's own style, each landing on its own word).
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', GREY = '#9AA0AD', PLUM = '#2B2033';
/* type on the phone's cream (design, Oct 29: the accent orange is 1.65:1 there, the grey 3.97:1): the tag maroon (7.1:1)
   for the loud words, slate (6.8:1) for the source line */
const MAROON = '#7A3442', SLATE = '#4A4E5A';
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eo = (x) => 1 - Math.pow(1 - clamp(x), 3);

// ---- the pixel kit (low-res units: 360 x 640, one pixel = 3 frame units), the same primitives the sets use ----
const px = (k) => {
  const ctx = k.ctx, T = k.T, F = Math.floor(T * 30 + 0.005);
  const P = (x, y, w, h, c) => { x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h); if (w > 0 && h > 0 && c) { ctx.fillStyle = c; ctx.fillRect(x * 3, y * 3, w * 3, h * 3); } };
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
  const clip = (x, y, w, h, fn) => { ctx.save(); ctx.beginPath(); ctx.rect(x * 3, y * 3, w * 3, h * 3); ctx.clip(); fn(); ctx.restore(); };
  return {P, win, fr, ease, tx, clip, F, T};
};

// ---- the words: every beat lands on a spoken word, so a re-voiced take moves everything with it ----
/* The speech bubble prints words.js as is, and anim.py display() lowercases every all-caps word (meant for a stressed
   word), so the acronyms came out "achr" and "hvac". Put back script.md's casing before the player reads the words
   (words.js loads before this file; the player builds its phrases after every script has loaded). */
const ACRONYMS = {achr: 'ACHR', hvac: 'HVAC'};
((window.WORDS && window.WORDS.words) || []).forEach((w) => { w.w = w.w.replace(/^([^A-Za-z]*)([A-Za-z]+)/, (m, pre, core) => pre + (ACRONYMS[core.toLowerCase()] || core)); });
const WS = () => (window.WORDS && window.WORDS.words) || [];
// the time a word is said (words.json), at or after a cue (or a time); falls back to the cue's start plus dflt
const wordT = (k, id, re, dflt = 0) => {
  const t0 = typeof id === 'number' ? id : k.S(id);
  const w = WS().find((x) => x.start >= t0 - 0.05 && re.test(x.w));
  return w ? w.start : t0 + dflt;
};
// a count that starts at 85% of its value and lands exactly on it
const cnt = (k, value, t0, o = {}) => k.count(value, k.lin(t0, t0 + 0.7) >= 1 ? 1 : 0.85 + 0.15 * k.lin(t0, t0 + 0.7), Object.assign({from: 0}, o));
const host = (k, pose) => ({hostPose: pose || (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150});
// a set's own text that we redraw or cover is not drawn at all (hidden text still counts for the layout lint)
const mute = (k, drop, fn) => { const real = k.text; k.text = function (s, x, y, o) { if (drop(s, x, y, o)) return; return real.call(this, s, x, y, o); }; try { return fn(); } finally { k.text = real; } };
/* a set's own fill swapped while it draws (map: lowercase hex -> new colour), for a set that takes no colour option; the
   canvas's own fillStyle comes back after */
const recolor = (k, map, fn) => {
  const ctx = k.ctx; let pr = Object.getPrototypeOf(ctx), dsc = null;
  while (pr && !(dsc = Object.getOwnPropertyDescriptor(pr, 'fillStyle'))) pr = Object.getPrototypeOf(pr);
  if (!dsc || !dsc.set) return fn();
  Object.defineProperty(ctx, 'fillStyle', {configurable: true, get() { return dsc.get.call(this); }, set(v) { dsc.set.call(this, (typeof v === 'string' && map[v.toLowerCase()]) || v); }});
  try { return fn(); } finally { delete ctx.fillStyle; }
};

// ================================================================================================================
// the high-score table (gap, turn): k.sets.scores draws the cabinet, marquee and screen; the rows are drawn here in the
// set's own style so each one lands on the word that says it (the set spaces rows evenly). rows: [{rank, name, value, at,
// hi, count: {value, suffix}}]; heads: three column headers.
const COLS = ['#F2A541', '#E2633B', '#6FB7A8', '#87CEEB', '#FFF7EA', '#F7C873'];
const scoreTable = (k, title, heads, rows) => {
  const d = px(k), T = k.T;
  mute(k, (s, x, y) => y === 378 && ['RANK', 'NAME', 'SCORE'].includes(s), () => k.sets.scores({title, rows: []}));
  d.tx(heads[0], 40, 126, {color: TEAL}); d.tx(heads[1], 110, 126, {color: TEAL}); d.tx(heads[2], 306, 126, {color: TEAL, align: 'right'});
  rows.forEach((r, i) => { if (T < r.at) for (let x = 46; x < 306; x += 8) d.P(x, 156 + i * 24, 4, 1, '#3D2E45'); });
  rows.forEach((r, i) => {
    if (T < r.at) return;
    const y = 150 + i * 24, c = r.hi ? GOLD : COLS[i % COLS.length], slide = d.ease(r.at, 5, 40);
    if (r.hi) { d.P(32, y - 4, 280, 21, '#3D2E45'); if (Math.floor((T - r.at) * 4) % 2 === 0) d.tx('>', 32 + slide, y, {color: ORANGE}); }
    d.tx(r.rank, 46 + slide, y, {color: c});
    const off = r.hi && T >= r.at + 0.7 && Math.floor((T - r.at) * 4) % 2 === 1;
    d.tx(r.name, 110 + slide, y, {color: off ? RED : c});
    d.tx(r.count ? cnt(k, r.count.value, r.at, {suffix: r.count.suffix}) : r.value, 306 + slide, y, {color: c, align: 'right'});
  });
};

// ================================================================================================================
// the slot machine (stakes, close): one pull per entry, the latest pull drawn; plate: a line between the reels and the tray
const slotPull = (k, pulls, label) => {
  const T = k.T, cur = pulls.filter((p) => T >= p.t0).pop();
  if (!cur) k.sets.slots({t0: 1e6, stops: [1e6, 1e6, 1e6], idle: ['?', '?', '?'], label, win: false});
  else k.sets.slots({t0: cur.t0, stops: cur.stops, symbols: cur.symbols, label, win: true});
};
const plate = (k, s, at, o = {}) => {
  const d = px(k); d.P(58, 229, 244, 15, INK); d.P(59, 230, 242, 13, '#2B2033');
  if (s) { const shown = s.slice(0, Math.max(0, Math.floor((k.T - at) * 60))); d.clip(59, 229, 242, 15, () => d.tx(shown, 180, 230, {color: o.color || GOLD, align: 'center', lint: shown.length === s.length})); }
};

// ================================================================================================================
// the chat (hook, replies, caveat): lines of a bubble scrolled up under the app header are clipped, so they are not drawn
/* our bubbles: the set fills them #3B82C4 with no option to change it, and cream on that is 3.81:1 (design, Oct 29), so
   they draw in #2B6CB0 (5.1:1); nothing else in the chat set uses that blue */
const BUBBLE = {'#3b82c4': '#2B6CB0'};
const chat = (k, o) => recolor(k, BUBBLE, () => mute(k, (s, x, y, t) => y < 390 && !(x === 408 && y === 318) && !(t && t.lint === false), () => k.sets.chat(o)));
// the EXAMPLE tag on the left pillar
const exampleTag = (k) => { const d = px(k); d.P(8, 196, 60, 17, INK); d.P(9, 197, 58, 15, RED); d.tx('EXAMPLE', 38, 198, {color: CREAM, align: 'center'}); };

// ================================================================================================================
// the review close-up (hook, "one-star" to "Your move"): the cut in on the phone. Its screen fills the frame; the hook rides on
// the app's header plate; the example review sits big under it, one star lit of five (pulsing on "review"), tagged EXAMPLE.
const STAR = ['....#....', '...###...', '...###...', '#########', '.#######.', '..#####..', '..##.##..', '.##...##.', '##.....##'];
const star = (d, x, y, c, s = 2) => STAR.forEach((r, j) => { for (let i = 0; i < r.length; i++) if (r[i] === '#') d.P(x + i * s, y + j * s, s, s, c); });
const closeUp = (k, o) => {
  const d = px(k), {P, T, fr} = d, n = k.data.numbers;
  // the phone fills the frame top to bottom: its body, its screen, and the keyboard up in the lower third
  P(0, 0, 360, 640, '#1B1420');
  P(9, 73, 348, 567, INK); P(4, 66, 352, 574, INK); P(5, 67, 350, 573, '#2B2033'); P(5, 67, 350, 1, '#4A4E5A'); P(5, 67, 1, 573, '#4A4E5A');
  P(14, 76, 332, 564, '#F4E6D3');
  for (let y = 136; y < 316; y += 10) for (let x = 16 + ((y / 10) % 2) * 5; x < 346; x += 10) d.P(x, y, 1, 1, '#E6D3BC');
  // the header plate: the hook, held from the cover
  P(14, 76, 332, 46, '#2F6F67'); P(14, 122, 332, 1, '#245752');
  k.text(`New ${n.one.shown}-star review.`, 66, 270, {size: 66, color: CREAM, drop: '#245752'});
  // the review card: five stars, one lit; the example review in big type; the EXAMPLE tag
  P(27, 139, 308, 112, '#E6D3BC'); P(26, 136, 308, 112, '#FFF7EA'); P(26, 136, 308, 1, '#FFFFFF');
  const pulse = o.pulseAt != null && fr(o.pulseAt) >= 0 && fr(o.pulseAt) < 18 && Math.floor(fr(o.pulseAt) / 3) % 2 === 0;
  for (let i = 0; i < 5; i++) star(d, 38 + i * 24, 146, i === 0 ? (pulse ? GOLD : RED) : '#C9CCD3');
  if (pulse) { P(34, 142, 26, 1, GOLD); P(34, 167, 26, 1, GOLD); P(34, 142, 1, 26, GOLD); P(59, 142, 1, 26, GOLD); }
  k.text(`${n.one.shown} star`, 486, 444, {size: 39, color: '#6B7080'});
  k.text('The tech showed', 108, 540, {size: 66, color: PLUM});
  k.text('up late.', 108, 612, {size: 66, color: PLUM});
  /* the tag's box ends at x 924 (render-critic, Oct 29: it ran to 967, past the 930 safe line) */
  d.P(234, 226, 74, 17, INK); d.P(235, 227, 72, 15, RED); d.tx('EXAMPLE', 271, 228, {color: CREAM, align: 'center'});
  // under the card: the reply box, the promise typed in it as its placeholder, the cursor blinking
  P(26, 254, 308, 36, '#FFF7EA'); P(26, 254, 308, 1, '#E6D3BC'); P(30, 258, 260, 28, '#F4E6D3'); d.P(296, 258, 30, 28, '#2F6F67');
  d.P(306, 268, 10, 2, CREAM); d.P(312, 265, 2, 8, CREAM);
  if (Math.floor(T * 2) % 2 === 0) P(34, 261, 2, 22, '#2F6F67');
  k.text('Copy this reply.', 120, 780, {size: 66, color: MAROON});
  // the keyboard: four rows of keys on whole pixels, QWERTY letters in the grey label tone (design, Oct 29: blank keys read
  // as a placeholder); shift and delete are the darker function keys. Scenery under the Reel's UI band, so lint: false.
  P(14, 296, 332, 344, '#C9CCD3'); P(14, 296, 332, 1, '#9AA0AD');
  const rows = [[10, 0, 'QWERTYUIOP'], [9, 8, 'ASDFGHJKL'], [9, 8, ' ZXCVBNM '], [5, 0, '']];
  rows.forEach(([nk, off, keys], r) => {
    const kw = r === 3 ? 0 : 28, gap = 4, y = 420 + r * 50;
    if (r === 3) { P(30, y, 56, 40, '#9AA0AD'); P(96, y, 168, 40, '#FFF7EA'); P(96, y + 39, 168, 1, '#6B7080'); P(274, y, 56, 40, '#2F6F67'); return; }
    for (let i = 0; i < nk; i++) {
      const x = 24 + off + i * (kw + gap), fn = keys[i] === ' ';
      P(x, y, kw, 40, fn ? '#9AA0AD' : '#FFF7EA'); P(x, y + 39, kw, 1, '#6B7080');
      if (!fn) k.text(keys[i], (x + kw / 2) * 3, (y + 13) * 3, {size: 39, color: GREY, align: 'center', lint: false});
    }
  });
  return d;
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 7',
  transitions: {stakes: 'levelselect', gap: 'dissolve', replies: 'iris', turn: 'blinds', caveat: 'dissolve', close: 'gameover'},
  trauma: {'turn.never': 0.8},
  sections: {
    // ---- hook: three shots (IMPROVE 00a: the picture changes by 1 s and twice by 3 s, Snow on by 3 s). The cover: the phone
    // in the truck, the hook card on its screen, settled on frame 0, no host or dialog. Cut in on "one-star" to the review
    // close-up (Snow and the dialog on). Cut back out on "Your move" to the truck; the card turns to the 43% on "Forty-three".
    hook: (k, T) => {
      const n = k.data.numbers, t43 = wordT(k, 'hook.43', /^forty/i, 1.0), tStat = Math.min(4.0, k.S('hook.43')); /* clamp: the on-screen hook holds 2.5 to 4.0 s, then clears */
      const tIn = Math.min(0.8, Math.max(0.5, wordT(k, 'hook', /^one-star/i, 0.5))), tRev = wordT(k, 'hook', /^review/i, tIn + 0.3);
      const tOut = Math.min(2.6, k.S('hook.copy'));
      /* the close-up is a real reframe: the screen fills the frame and Snow steps in, bigger (0.75, hat clear of the reply box), in front of the keyboard */
      if (T >= tIn && T < tOut) { closeUp(k, {pulseAt: tRev}); return {hostPose: k.talking() ? 'talk' : 'point', hostScale: 0.75, hostX: 190}; }
      /* the New review banner drops on "Forty-three" with the number and holds past it */
      k.sets.chat({who: 'REVIEWS', clock: '7:42', msgs: [], notify: T >= tStat ? {text: 'New review', at: tStat, dur: Math.max(1.6, t43 + 1.0 - tStat)} : null});
      // the card on the screen (frame x 306..870, y 390..888): light wallpaper, dark words
      /* the hero words at size 198 (design, Oct 29: 132 sat under the 160 floor; the pixel font steps in 66s, so 160 draws as
         132 and 198 is the next step). Set at y 360 so the ink ends at y 504, where the 132 ink ended, and starts by y 396 */
      if (T < tStat) {
        /* the on-screen hook (Oct 29, 10:10 pm rebuild, your-move): "1-star review just landed. Your move." (6 words) */
        k.text(`${n.one.shown}-star`, 324, 360, {size: 198, color: MAROON});
        k.text('review just', 324, 548, {size: 66, color: PLUM});
        k.text('landed.', 324, 618, {size: 66, color: PLUM});
        k.text('Your move.', 324, 700, {size: 66, color: PLUM});
        if (T >= tOut) k.sweep(324, 770, k.measure('Your move.', {size: 66}), 6, tOut + 0.1, {color: 'accent'});
        k.chip('Reviews Clinic', 324, 800, {size: 30});
      } else {
        /* the sparks fire once on "Forty-three" (about 0.6 s), beside the 43% only: drawn first so every glyph sits on top,
           and clipped to the number's band (y 390 to 540) so none reach the body lines. No glint on this card (design and
           golden, Oct 29: the shine replaced letter pixels, "contrac ors"). They fly from just right of the %, and the clip
           starts 12 px past the number's right edge at its slam scale (shake included), so none land on the glyphs while it
           settles (design, Oct 29: spark pixels on the '4' and '3' entry frames) */
        const w43 = k.measure(n.noAnswer.shown, {size: 198}), q43 = clamp((T - tStat) / 0.2), x43 = 324 + w43 * (1 + 0.6 * (1 - q43) * (1 - q43)) + 12;
        if (x43 < 870) { k.ctx.save(); k.ctx.beginPath(); k.ctx.rect(x43, 390, 870 - x43, 150); k.ctx.clip(); k.burst(324 + w43 + 48, 450, t43, {n: 14, r: 170, life: 0.6}); k.ctx.restore(); }
        k.slam(n.noAnswer.shown, 324, 360, tStat, {size: 198, color: MAROON, from: 0.6, glint: false});
        k.slam('of contractors', 324, 548, tStat + 0.1, {size: 66, color: PLUM, from: 0.4, glint: false});
        k.slam("don't answer", 324, 618, tStat + 0.15, {size: 66, color: PLUM, from: 0.4, glint: false});
        k.slam('reviews', 324, 688, tStat + 0.2, {size: 66, color: PLUM, from: 0.4, glint: false});
        /* the scope as it is said: the survey on "in one HVAC survey", the sites on "on third-party sites" */
        k.slam(`ACHR News survey, ${n.year.shown}`, 324, 770, k.S('hook.survey'), {size: 30, color: SLATE, from: 0.4});
        k.slam('on third-party sites', 324, 816, k.S('hook.sites'), {size: 30, color: MAROON, from: 0.5});
      }
      if (T < tIn) return {host: false, speech: false};
      return host(k, k.live('hook.copy') ? 'point' : null);
    },

    // ---- stakes: the slot machine; 9, 1, % as it is said; a second pull for Google
    stakes: (k, T) => {
      const n = k.data.numbers, t0 = k.S('stakes'), tAsk = k.S('stakes.asked'), tPull = k.S('stakes.pull'), tG = k.S('stakes.google');
      const t91 = wordT(k, 'stakes.pull', /^ninety/i, 0.2), tPct = wordT(k, 'stakes.pull', /^percent/i, 0.8);
      const t56 = wordT(k, 'stakes.google', /^Fifty/i), tPct2 = wordT(k, 'stakes.google', /^percent/i, 0.8);
      /* the lever goes 0.7 s before the number, so the first reel stops on its word and the % on "percent" */
      const pull = (tNum, tP) => { const s0 = Math.min(tNum - 0.7, tP - 1.0); return {t0: s0, stops: [Math.max(s0 + 0.4, tNum), Math.max(s0 + 0.55, tNum + 0.25), Math.max(s0 + 0.7, tP)]}; };
      const pulls = [
        Object.assign(pull(t91, tPct), {symbols: [...String(n.important.value), '%']}),
        Object.assign(pull(t56, tPct2), {symbols: [...String(n.google.value), '%']}),
      ];
      const label = T >= pulls[1].stops[2] ? 'LOOK ON GOOGLE' : (T >= pulls[0].stops[2] ? 'SAY REVIEWS MATTER' : 'ACHR NEWS + CLEAR SEAS');
      slotPull(k, pulls, label);
      if (T >= tG) plate(k, `${n.google.shown} look on Google`, tPct2);
      else if (T >= k.S('stakes.hvac')) plate(k, `${n.important.shown}: picking an HVAC contractor`, k.S('stakes.hvac'));
      else if (T >= tAsk) plate(k, `${n.homeowners.shown} homeowners, ${n.year.shown}`, tAsk, {color: CREAM});
      else plate(k, 'Homeowners: do reviews matter?', t0 + 0.3, {color: SAND});
      return host(k, k.live('stakes.pull') || k.live('stakes.google') ? 'point' : (k.live('stakes.asked') ? 'clip' : null));
    },

    // ---- gap: the high-score table; NO (the blinking row, its 43% said in the hook) lands first, YES on "forty-five",
    // DON'T KNOW (on screen only) on "who do."
    gap: (k, T) => {
      const n = k.data.numbers, t0 = k.S('gap');
      const tNo = t0 + 0.4, tYes = wordT(k, 'gap.yes', /^forty/i, 0.2), tDk = k.S('gap.dk');
      scoreTable(k, 'DO CONTRACTORS ANSWER?', ['RANK', 'ANSWER', 'SHARE'], [
        {rank: '1ST', name: 'YES', at: tYes, count: {value: n.answer.value, suffix: '%'}},
        {rank: '2ND', name: 'NO', at: tNo, hi: true, count: {value: n.noAnswer.value, suffix: '%'}},
        {rank: '3RD', name: "DON'T KNOW", at: tDk, count: {value: n.dontKnow.value, suffix: '%'}},
      ]);
      const d = px(k);
      d.tx('Reviews on third-party sites', 180, 228, {color: CREAM, align: 'center'});
      d.tx(`Contractors, ACHR News survey, ${n.year.shown}`, 180, 252, {color: SAND, align: 'center', size: 30});
      return host(k, k.live('gap.yes') ? 'point' : null);
    },

    // ---- replies: the review inbox; the example review arrives, our reply goes out a sentence at a time as it is said
    replies: (k, T) => {
      const n = k.data.numbers, t0 = k.S('replies'), tOne = k.S('replies.one');
      /* script point 7 (Oct 29): each finished reply stays whole on screen 3 s or more. The five-star thread holds into
         take 5: the New review banner drops over it on "one-star" and the thread flips on "reply" */
      const tNote = wordT(k, 'replies.one', /^one-star/i, 0.5), tFlip = wordT(k, 'replies.one', /^reply/i, 1.0);
      const five = T < tFlip;
      /* the turn line is said over the finished one-star thread (a banner drops over the phone's top), so the whole reply
         holds from "Call" into "Answer your bad ones", where the table world takes over */
      const tSkip = k.S('replies.skip');
      const msgs = five ? [
        {me: false, text: `${n.five.shown} stars. Fixed our furnace fast.`, at: t0 + 0.6, typing: 0.5},
        /* two reply bubbles, not three, so the review stays whole at the top (no scroll); the first grows down a sentence at a time */
        {me: true, text: T >= k.S('replies.f2') ? "Thanks for trusting us with your furnace. Glad it's running right." : 'Thanks for trusting us with your furnace.', at: k.S('replies.f1')},
        {me: true, text: "We're here when you need us.", at: k.S('replies.f3'), read: k.S('replies.f3') + 0.9},
      ] : [
        {me: false, text: `${n.one.shown} star. The tech showed up late.`, at: Math.max(tFlip + 0.1, Math.min(tFlip + 0.3, k.S('replies.o1') - 0.1)), typing: 0.2},
        {me: true, text: T >= k.S('replies.o2') ? "Sorry we were late. That's on us. I want to make it right." : "Sorry we were late. That's on us.", at: k.S('replies.o1')},
        {me: true, text: 'Call me directly at the shop.', at: k.S('replies.o3'), read: k.S('replies.o3') + 0.9},
      ];
      chat(k, {who: five ? 'FIVE-STAR REPLY' : 'ONE-STAR REPLY', clock: '7:42', msgs, notify: T >= tSkip ? {text: 'The part people skip', at: tSkip, dur: 9} : (T >= tNote ? {text: `New review: ${n.one.shown} star`, at: tNote, dur: 1.6} : null)});
      exampleTag(k);
      const r = host(k, k.live('replies.f1') || k.live('replies.o1') ? 'point' : null);
      return r;
    },

    // ---- turn: THE PART PEOPLE SKIP as a rules table, each rule landing as it is said
    turn: (k, T) => {
      const t0 = k.S('turn'), tBad = wordT(k, 'turn', /^bad/i, 0.4);
      scoreTable(k, 'THE PART PEOPLE SKIP', ['NO.', 'RULE', 'DO'], [
        {rank: '01', name: 'BAD ONES', value: 'ANSWER', at: tBad},
        {rank: '02', name: 'LENGTH', value: 'SHORT', at: wordT(k, 'turn.short', /^short/i)},
        {rank: '03', name: 'TONE', value: 'CALM', at: wordT(k, 'turn.short', /^calm/i, 0.8)},
        {rank: '04', name: 'DETAILS', value: 'OFFLINE', at: wordT(k, 'turn.offline', /^offline/i, 0.6)},
        {rank: '05', name: 'ARGUING', value: 'NEVER', at: wordT(k, 'turn.never', /^Never/i), hi: true},
      ]);
      if (T < tBad) px(k).tx('Rules for every reply', 180, 284, {color: SAND, align: 'center'});
      else if (T >= k.S('turn.never')) k.slam('Never argue in public.', 540, 846, k.S('turn.never') + 0.2, {size: 39, color: RED, align: 'center', stamp: true, glint: false});
      return host(k, k.live('turn.never') ? 'point' : (T < k.S('turn.short') ? 'clip' : null));
    },

    // ---- caveat: the chat again, ONE HONEST NOTE; a Monday reminder and our reply
    caveat: (k, T) => {
      const n = k.data.numbers, t0 = k.S('caveat'), tMon = k.S('caveat.monday');
      chat(k, {who: 'ONE HONEST NOTE', clock: '7:42', msgs: [
        {me: false, text: 'The survey: reviews matter to homeowners.', at: k.S('caveat.survey') + 0.2, typing: Math.min(1.2, k.S('caveat.survey') - t0)},
        {me: false, text: "It doesn't prove a reply wins the job.", at: k.S('caveat.prove') + 0.2, typing: 0.6},
        {me: true, text: `Every Monday. ${n.minutes.shown} minutes. Answer every new one.`, at: tMon + 0.6, read: tMon + 1.6},
      ], notify: {text: `MON: reviews, ${n.minutes.shown} min`, at: tMon, dur: 2.0}});
      return host(k, k.live('caveat.prove') ? 'shrug' : (k.live('caveat.monday') ? 'point' : null));
    },

    // ---- close: a last pull lands Y, E, S; one column over the tray: the line, the send line, the echo of the hook
    close: (k, T) => {
      const d = px(k), n = k.data.numbers, t0 = k.S('close'), send = k.S('close.send'), ans = k.S('close.answer');
      slotPull(k, [{t0: t0 + 0.15, stops: [t0 + 0.8, t0 + 1.1, t0 + 1.4], symbols: ['Y', 'E', 'S']}], T >= t0 + 1.4 ? 'ANSWER EVERY REVIEW' : 'ONE MORE PULL');
      /* the column: a game window over the tray, one left edge (x 120), the line and the echo at headline size (lesson 9's 66),
         the echo the loudest (gold); the window ends by y 960 (shadow included) so the host's wave clears it */
      const open = d.ease(t0 + 0.25, 8, 110);
      /* design, Oct 29: about 14 px headline to chip and 12 px chip to send line; the window starts 9 px higher and is 9 px
         taller (same bottom), the headline moves up 11, the chip down 6, the send line down 15, the echo stays */
      d.clip(0, 0, 360, 320, () => d.win(14, 219 + open, 332, 99, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#7A3442'}));
      if (open === 0) {
        k.slam("Don't leave reviews hanging.", 120, 677, t0 + 0.3, {size: 66, color: 'accent', from: 0.5, drop: INK});
        if (T >= send) {
          k.chip('ProofNotFluff', 120, 758, {size: 30});
          /* it lands at its final width, no scale and no shake, and is clipped at x 930 (design, Oct 29: the 1.4x entry ran
             past the panel's right border to the frame edge for 3 frames; at size 39 its ink ends at x 930 exactly) */
          d.clip(0, 0, 310, 640, () => k.slam('Send this to whoever runs your Google profile.', 120, 817, send + 0.1, {size: 39, color: CREAM, from: 1e-6, shake: 0}));
        }
        const echo = `The next ${n.one.shown}-star gets a reply.`;
        if (T >= ans) { k.slam(echo, 120, 856, ans, {size: 66, color: GOLD, from: 0.5, drop: INK}); k.sweep(120, 916, k.measure(echo, {size: 66}), 6, ans + 0.3, {color: 'accent'}); }
      }
      return host(k, k.live('close.answer') ? 'wave' : (k.live('close.send') ? 'point' : null));
    },
  },
};
