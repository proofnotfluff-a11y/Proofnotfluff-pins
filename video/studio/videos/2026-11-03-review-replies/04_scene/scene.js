// Scene: Answer your reviews; many contractors don't (Lesson 7, Reviews Clinic, arcade). One function per top-level cue in
// 03_cues/cues.md. Numbers only from k.data (brief.md -> data.js). Every time comes from a cue start (k.S) or a spoken word
// (wordT), so a re-voiced take moves the picture with it.
// Worlds (brief.md): hook, replies, caveat = the chat in the truck (the review inbox); stakes, close = the slot machine;
// gap, turn = the arcade high-score table (its rows drawn here in the set's own style, each landing on its own word).
const INK = '#120D14', CREAM = '#FFF7EA', SAND = '#E6D3BC', GOLD = '#F7C873', ORANGE = '#F2A541', RED = '#E2633B', TEAL = '#6FB7A8', GREY = '#9AA0AD', PLUM = '#2B2033';
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
const chat = (k, o) => mute(k, (s, x, y, t) => y < 390 && !(x === 408 && y === 318) && !(t && t.lint === false), () => k.sets.chat(o));
// the EXAMPLE tag on the left pillar
const exampleTag = (k) => { const d = px(k); d.P(8, 196, 60, 17, INK); d.P(9, 197, 58, 15, RED); d.tx('EXAMPLE', 38, 198, {color: CREAM, align: 'center'}); };

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 7',
  transitions: {stakes: 'levelselect', gap: 'dissolve', replies: 'iris', turn: 'blinds', caveat: 'dissolve', close: 'gameover'},
  trauma: {'turn.never': 0.8},
  sections: {
    // ---- hook: the phone in the truck, the hook card on its screen, settled on frame 0; no host or dialog yet
    hook: (k, T) => {
      const n = k.data.numbers, t43 = wordT(k, 'hook.43', /^forty/i), tCopy = k.S('hook.copy');
      /* frame 0 is the settled cover; the New review banner drops at 1 s and holds past "forty-three" (motion before the number) */
      k.sets.chat({who: 'REVIEWS', clock: '7:42', msgs: [], notify: {text: 'New review', at: 1.0, dur: Math.max(2.2, t43 + 1.2 - 1.0)}});
      // the card on the screen (frame x 306..870, y 390..888): light wallpaper, dark words
      k.text(n.noAnswer.shown, 324, 404, {size: 132, color: 'accent'});
      k.text('of contractors', 324, 548, {size: 66, color: PLUM});
      k.text("don't answer", 324, 618, {size: 66, color: PLUM});
      k.text('reviews.', 324, 688, {size: 66, color: PLUM});
      k.text(`ACHR News survey, ${n.year.shown}`, 324, 770, {size: 30, color: '#6B7080'});
      if (T >= tCopy) { k.slam('Two replies to copy.', 324, 816, tCopy, {size: 39, color: 'accent', from: 0.5}); k.sweep(324, 860, 480, 6, tCopy + 0.25, {color: 'accent'}); }
      k.burst(470, 470, 0.6, {n: 10, r: 160}); k.burst(470, 470, 1.6, {n: 12, r: 180}); k.burst(470, 470, t43, {n: 18, r: 220});
      if (T < t43) return {host: false, speech: false};
      if (T < tCopy) return {host: false};
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

    // ---- gap: the high-score table; YES, NO (the blinking row), DON'T KNOW, each on its own number
    gap: (k, T) => {
      const n = k.data.numbers, t0 = k.S('gap');
      const tYes = wordT(k, 'gap.yes', /^Forty/i), tNo = wordT(k, 'gap.no', /^Forty/i), tDk = wordT(k, 'gap.dk', /^Thirteen/i);
      scoreTable(k, 'DO CONTRACTORS ANSWER?', ['RANK', 'ANSWER', 'SHARE'], [
        {rank: '1ST', name: 'YES', at: tYes, count: {value: n.answer.value, suffix: '%'}},
        {rank: '2ND', name: 'NO', at: tNo, hi: true, count: {value: n.noAnswer.value, suffix: '%'}},
        {rank: '3RD', name: "DON'T KNOW", at: tDk, count: {value: n.dontKnow.value, suffix: '%'}},
      ]);
      const d = px(k);
      d.tx('Reviews on third-party sites', 180, 228, {color: CREAM, align: 'center'});
      d.tx(`Contractors, ACHR News survey, ${n.year.shown}`, 180, 252, {color: SAND, align: 'center', size: 30});
      return host(k, k.live('gap.no') ? 'point' : null);
    },

    // ---- replies: the review inbox; the example review arrives, our reply goes out a sentence at a time as it is said
    replies: (k, T) => {
      const n = k.data.numbers, t0 = k.S('replies'), tOne = k.S('replies.one');
      const five = T < tOne;
      const msgs = five ? [
        {me: false, text: `${n.five.shown} stars. Fixed our furnace fast.`, at: t0 + 0.6, typing: 0.5},
        /* two reply bubbles, not three, so the review stays whole at the top (no scroll); the first grows down a sentence at a time */
        {me: true, text: T >= k.S('replies.f2') ? "Thanks for trusting us with your furnace. Glad it's running right." : 'Thanks for trusting us with your furnace.', at: k.S('replies.f1')},
        {me: true, text: "We're here when you need us.", at: k.S('replies.f3'), read: k.S('replies.f3') + 0.9},
      ] : [
        {me: false, text: `${n.one.shown} star. The tech showed up late.`, at: tOne + 0.6, typing: 0.5},
        {me: true, text: T >= k.S('replies.o2') ? "Sorry we were late. That's on us. I want to make it right." : "Sorry we were late. That's on us.", at: k.S('replies.o1')},
        {me: true, text: 'Call me directly at the shop.', at: k.S('replies.o3'), read: k.S('replies.o3') + 0.9},
      ];
      chat(k, {who: five ? 'FIVE-STAR REPLY' : 'ONE-STAR REPLY', clock: '7:42', msgs, notify: five ? null : {text: `New review: ${n.one.shown} star`, at: tOne, dur: 1.6}});
      exampleTag(k);
      const r = host(k, k.live('replies.f1') || k.live('replies.o1') ? 'point' : null);
      return r;
    },

    // ---- turn: THE PART PEOPLE SKIP as a rules table, each rule landing as it is said
    turn: (k, T) => {
      const t0 = k.S('turn');
      scoreTable(k, 'THE PART PEOPLE SKIP', ['NO.', 'RULE', 'DO'], [
        {rank: '01', name: 'BAD ONES', value: 'ANSWER', at: wordT(k, 'turn.bad', /^bad/i)},
        {rank: '02', name: 'LENGTH', value: 'SHORT', at: wordT(k, 'turn.short', /^short/i)},
        {rank: '03', name: 'TONE', value: 'CALM', at: wordT(k, 'turn.short', /^calm/i, 0.8)},
        {rank: '04', name: 'DETAILS', value: 'OFFLINE', at: wordT(k, 'turn.offline', /^offline/i, 0.6)},
        {rank: '05', name: 'ARGUING', value: 'NEVER', at: wordT(k, 'turn.never', /^Never/i), hi: true},
      ]);
      if (T < k.S('turn.bad')) px(k).tx('Rules for every reply', 180, 284, {color: SAND, align: 'center'});
      else if (T >= k.S('turn.never')) k.slam('Never argue in public.', 540, 846, k.S('turn.never') + 0.2, {size: 39, color: RED, align: 'center', stamp: true, glint: false});
      return host(k, k.live('turn.never') ? 'point' : (k.live('turn.bad') ? 'clip' : null));
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

    // ---- close: a last pull lands Y, E, S; one column over the tray: the line, the send line, the ask
    close: (k, T) => {
      const d = px(k), t0 = k.S('close'), dont = k.S('close.dont'), send = k.S('close.send'), ans = k.S('close.answer');
      slotPull(k, [{t0: t0 + 0.15, stops: [t0 + 0.8, t0 + 1.1, t0 + 1.4], symbols: ['Y', 'E', 'S']}], T >= t0 + 1.4 ? 'ANSWER EVERY REVIEW' : 'ONE MORE PULL');
      /* the column: a game window over the tray, one left edge (x 120), the line and the ask at headline size (lesson 9's 66),
         the ask the loudest (gold); the window ends by y 960 (shadow included) so the host's wave clears it */
      const open = d.ease(t0 + 0.25, 8, 110);
      d.clip(0, 0, 360, 320, () => d.win(14, 222 + open, 332, 96, {base: '#1B1420', hi: '#3D2E45', lo: INK, rule: '#7A3442'}));
      if (open === 0) {
        k.slam('Plenty leave reviews hanging.', 120, 688, t0 + 0.3, {size: 66, color: 'accent', from: 0.5, drop: INK});
        /* "Don't be one." holds its row until the send line comes; then the chip takes the row */
        if (T >= dont && T < send) k.slam("Don't be one.", 120, 754, dont, {size: 39, color: CREAM, from: 0.4});
        if (T >= send) {
          k.chip('ProofNotFluff', 120, 752, {size: 30});
          k.slam('Send this to whoever runs your Google profile.', 120, 802, send + 0.1, {size: 39, color: CREAM, from: 0.4});
        }
        if (T >= ans) { k.slam('Answer your reviews.', 120, 856, ans, {size: 66, color: GOLD, from: 0.5, drop: INK}); k.sweep(120, 916, 516, 6, ans + 0.3, {color: 'accent'}); }
      }
      return host(k, k.live('close.answer') ? 'wave' : (k.live('close.send') ? 'point' : null));
    },
  },
};
