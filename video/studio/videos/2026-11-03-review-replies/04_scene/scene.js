// Scene: Reply to every review (Lesson 7, Reviews Clinic, arcade). One function per top-level cue in 03_cues/cues.md.
// Numbers only from k.data (brief.md -> data.js). Rooms: framing, workshop, blackboard, framing, garage, workshop, blackboard.
// Modeled on lesson 4 (hook card settled on frame 0, slams, sparks, count-ups from 85%) and lesson 1 (the phone, a reply
// that types as it is said, keeping its final width and growing down).
const CHALK = '#FFF7EA', CHALK2 = '#F7C873', INK = '#1B1420', DARK = '#2B2033', GREY = '#9AA0AD', HOOK_END = 3.4;
const GOOD_REVIEW = 'Great work. On time, and they cleaned up after.';
const BAD_REVIEW = 'Late, and left a mess.';
// each reply is typed in pieces, each piece as its words are said: [cue, text, the first word it waits for, step chip]
const GOOD = [
  ['good.thanks', 'Thanks, [first name].', /^"?thanks/i, '1. Their name'],
  ['good.glad', 'Glad the [job] went well.', /^glad/i, '2. The job'],
  ['good.here', "We're here when you need us.", /^we/i, '3. Door open'],
  ['good.sign', '[Your name]', /^name/i, '4. Your name'],
];
const BAD = [
  ['bad.sorry', 'Sorry we fell short on [issue].', /^"?sorry/i],
  ['bad.right', 'I want to make it right.', /^i$/i],
  ['bad.call', 'Call me directly at [number]. [Your name]', /^call/i],
];
// everything written on the board stays inside the board, even while it slides in
const boardClip = (k) => { k.ctx.save(); k.ctx.beginPath(); k.ctx.rect(60, 246, 960, 752); k.ctx.clip(); };
const slideIn = (k, t0, dx = 0, dy = 0) => { const q = k.easeOut((k.T - t0) / 0.35); k.ctx.translate(dx * 0.4 * (1 - q), dy * 0.4 * (1 - q)); k.ctx.globalAlpha *= k.clamp(q * 1.6); return q; };
const popAt = (k, t0, cx, cy, max = 1.15) => { const q = k.clamp(k.pop(t0), 0, max); k.ctx.translate(cx, cy); k.ctx.scale(q, q); k.ctx.translate(-cx, -cy); };
// the time a word is said (from words.json), at or after a cue; falls back to the cue's start
const wordT = (k, id, re, dflt = 0) => {
  const ws = (window.WORDS && window.WORDS.words) || [];
  const w = ws.find((x) => x.start >= k.S(id) - 0.05 && re.test(x.w));
  return w ? w.start : k.S(id) + dflt;
};
// a five-point star in pixels; filled, or an outline for an empty one
const star = (k, cx, cy, r, fill) => {
  const pts = []; for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.45 : r; pts.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]); }
  if (fill) k.shape(pts, {fill, line: false}); else k.shape(pts, {stroke: GREY, lw: 5, line: false});
};
const starRow = (k, x, cy, r, step, lit, total, t0, color = 'accent') => {
  for (let i = 0; i < total; i++) {
    const ti = t0 + i * 0.08; if (k.T < ti) return;
    k.ctx.save(); popAt(k, ti, x + i * step, cy, 1.2); star(k, x + i * step, cy, r, i < lit ? color : null); k.ctx.restore();
  }
};
// a reply typed piece by piece: whole earlier pieces plus part of the one being said; the bubble is laid out for the full reply
const typed = (k, pieces) => {
  const startOf = ([id, , re]) => wordT(k, id, re, 0.1) - 0.05;
  let cur = -1, reveal = 0, typingTo = 0;
  pieces.forEach((pc, i) => {
    if (k.T < k.S(pc[0])) return; cur = i;
    const t0 = startOf(pc), p = k.lin(t0, t0 + pc[1].length * 0.035);
    reveal = pieces.slice(0, i).reduce((a, r) => a + r[1].length + 1, 0) + Math.floor(pc[1].length * p);
    typingTo = t0 + pc[1].length * 0.035;
  });
  return {cur, reveal, typingTo, full: pieces.map((r) => r[1]).join(' ')};
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 7',
  focus: {'hook.copy': [300, 600], 'stakes.stars': [500, 680], 'stakes.small': [700, 820], 'why.backup': [400, 800],
          'good.here': [500, 760], 'bad.call': [500, 820], 'turn.longer': [500, 640], 'turn.guide': [400, 360], 'close.send': [540, 860]},
  sections: {
    hook: (k, T) => {
      const n = k.data.numbers;
      k.room('framing');
      if (T < HOOK_END) {   // the hook card: settled on frame 0, no host, no dialog (nothing covers the claim or its source)
        k.shape(k.rectPts(0, 230, 1080, 860, 0), {fill: INK, line: false});
        k.slam('Hotels that started', 540, 290, -1, {size: 60, color: CHALK, align: 'center'});
        k.slam('replying got', 540, 370, -1, {size: 60, color: CHALK, align: 'center'});
        k.slam(n.morePct.shown, 540, 456, -1, {size: 330, color: 'accent', align: 'center'});
        k.slam('more reviews.', 540, 780, -1, {size: 120, color: CHALK, align: 'center'});
        k.burst(120, 1040, 0.15, {n: 14, r: 200}); k.burst(960, 1040, 0.3, {n: 14, r: 200});   // sparks from the card's corners, never on the words
        k.burst(540, 600, 1.5, {n: 14, r: 320, colors: ['accent2', 'paper']});
        k.sweep(300, 930, 480, 10, 0.6, {color: 'accent'});
        k.text(`Hotel study, Marketing Science ${n.year.shown}`, 540, 966, {size: 39, color: '#E6D3BC', align: 'center'});
        k.text('Reviews Clinic', 540, 1026, {size: 39, color: CHALK2, align: 'center'});
        return {host: false, speech: false};
      }
      k.ctx.save(); slideIn(k, HOOK_END, -500, 0); k.chip('Reviews Clinic', 96, 280, {size: 30}); k.ctx.restore();
      // a dark card behind the stars and the promise, so nothing sits on the bright sky and studs
      k.ctx.save(); slideIn(k, HOOK_END + 0.05, -500, 0); k.panel2(72, 370, 380, 420); k.ctx.restore();
      starRow(k, 124, 430, 26, 64, n.five.value, n.five.value, HOOK_END + 0.15);
      k.ctx.save(); slideIn(k, HOOK_END + 0.1, 600, 0);
      k.phone(480, 300, 450, 490, [{text: GOOD_REVIEW, at: HOOK_END + 0.4}], {who: 'Example review', size: 39});
      k.ctx.restore();
      k.burst(705, 520, HOOK_END + 0.45, {n: 10, r: 160, colors: ['accent2', 'paper']});
      const tc = k.S('hook.copy');
      if (T >= tc) {   // the promise: two replies to copy
        k.stampIn(tc, () => k.text(n.replies.shown, 104, 500, {size: 200, color: 'accent'}), {at: [160, 700]});
        k.ctx.save(); slideIn(k, tc + 0.15, -400, 0);
        k.text('replies', 220, 560, {size: 60, color: CHALK});
        k.text('to copy', 220, 630, {size: 60, color: CHALK});
        k.ctx.restore();
        k.burst(170, 620, tc + 0.1, {n: 18});
      }
      return {hostPose: T >= tc ? 'point' : (k.talking() ? 'talk' : 'stand'), hostAt: [300, 600], hostScale: 0.55, hostX: 150};
    },

    stakes: (k, T) => {
      const n = k.data.numbers;
      k.room('workshop');
      const t0 = k.S('stakes');
      k.ctx.save(); slideIn(k, t0, 0, 700);
      k.panel2(60, 300, 870, 520, {title: `Marketing Science, ${n.year.shown}`});
      k.text('Hotels that started replying', 96, 336, {size: 39, color: CHALK});
      k.ctx.restore();
      if (T >= k.S('stakes.trip')) {
        k.ctx.save(); slideIn(k, k.S('stakes.trip'), 500, 0);
        k.text('Tens of thousands of', 96, 386, {size: 39, color: CHALK2});
        k.text('TripAdvisor hotel reviews', 96, 430, {size: 39, color: CHALK2});
        k.ctx.restore();
      }
      // both rows show as the panel opens (no empty box); the reviews row is already in, the rating row fills when said
      if (T >= t0 + 0.3) {
        k.ctx.save(); slideIn(k, t0 + 0.3, -500, 0);
        k.text('Reviews', 96, 524, {size: 60, color: CHALK});
        k.slam(k.count(n.morePct.value, 0.85 + 0.15 * k.lin(t0 + 0.4, t0 + 1.0), {prefix: '+', suffix: '%'}), 400, 494, t0 + 0.4, {size: 120, color: 'accent', from: 0.5});
        const lit = T >= k.S('stakes.up');
        k.text('Rating', 96, 654, {size: 60, color: lit ? 'accent' : 'muted'});
        k.text('on average', 96, 720, {size: 39, color: lit ? CHALK2 : 'muted'});
        const ts = wordT(k, 'stakes.stars', /^point/i);
        if (T < ts) k.shape(k.rectPts(400, 630, 420, 110, 0), {stroke: GREY, lw: 6, line: false});   // the empty slot the rating lands in
        else {
          const s = k.count(n.stars.value, 0.85 + 0.15 * k.lin(ts, ts + 0.8), {prefix: '+', dec: 2});
          k.slam(s, 400, 624, ts, {size: 120, color: 'accent', from: 0.5});
          const w = k.measure(`+${n.stars.shown}`, {size: 120});
          k.ctx.save(); popAt(k, ts + 0.5, 400 + w + 60, 680, 1.2); star(k, 400 + w + 60, 680, 44, 'accent'); k.ctx.restore();
          k.burst(400 + w + 60, 680, ts + 0.6, {n: 16, r: 200});
        }
        k.ctx.restore();
        if (k.live('stakes.up')) k.sweep(96, 712, 210, 4, k.S('stakes.up') + 0.2, {color: 'accent'});
      }
      if (T >= k.S('stakes.small')) {   // a sticker below the rows, clear of every number
        const ty = k.S('stakes.small');
        k.ctx.save(); k.ctx.translate(735, 830); k.ctx.rotate(-0.03); k.ctx.translate(-735, -830); popAt(k, ty, 735, 830);
        k.panel2(540, 776, 390, 110, {fill: 'accent', border: INK});
        k.text('Small? Ratings', 735, 790, {size: 39, color: INK, align: 'center'});
        k.text('barely move.', 735, 834, {size: 39, color: INK, align: 'center'});
        k.ctx.restore();
        k.burst(735, 830, ty + 0.05, {n: 18});
      }
      const pose = k.live('stakes.small') ? 'shrug' : (k.live('stakes.stars') ? 'point' : (k.talking() ? 'talk' : 'stand'));
      return {hostPose: pose, hostAt: [500, 680], hostScale: 0.55, hostX: 150};
    },

    why: (k, T) => {
      k.room('blackboard'); boardClip(k);
      k.slam('Why a reply helps', 96, 280, k.S('why'), {size: 60, color: CHALK2, from: 0.5});
      if (T < k.S('why.care')) {   // a review card with a reply arrow, chalked in while the voice asks why (the board is never empty)
        const t0 = k.S('why') + 0.4, q = k.clamp(k.pop(t0, 0.4), 0, 1.1);
        k.ctx.save(); k.ctx.translate(540, 650); k.ctx.rotate(-0.03); k.ctx.scale(q * 1.2, q * 1.2);
        k.shape(k.rectPts(-200, -130, 400, 200, 0), {fill: CHALK, line: false});
        for (let i = 0; i < 5; i++) star(k, -150 + i * 56, -84, 22, i < 4 ? '#E2633B' : null);
        for (let i = 0; i < 2; i++) k.shape(k.rectPts(-170, -30 + i * 40, i ? 220 : 340, 14, 0), {fill: GREY, line: false});
        k.shape(k.rectPts(-120, 110, 320, 100, 0), {fill: '#2F6F67', line: false});
        k.shape(k.rectPts(-90, 140, 230, 14, 0), {fill: CHALK, line: false}); k.shape(k.rectPts(-90, 172, 150, 14, 0), {fill: CHALK, line: false});
        k.ctx.restore();
        k.burst(540, 650, t0 + 0.05, {n: 14, colors: ['paper', 'accent2']});
      }
      if (T >= k.S('why.care')) {
        const t0 = k.S('why.care');
        k.ctx.save(); slideIn(k, t0, -600, 0);
        k.text('It shows you care', 96, 400, {size: 60, color: CHALK});
        k.text('what customers think.', 96, 470, {size: 60, color: CHALK});
        k.ctx.restore();
      }
      if (T >= k.S('why.unhappy')) {
        const t0 = k.S('why.unhappy');
        k.slam('Unhappy customers', 96, 600, t0, {size: 60, color: 'accent', from: 0.5});
        k.ctx.save(); slideIn(k, t0 + 0.3, -600, 0); k.text('think twice', 96, 670, {size: 60, color: CHALK}); k.ctx.restore();
      }
      if (T >= k.S('why.backup')) {
        const t0 = k.S('why.backup');
        k.ctx.save(); slideIn(k, t0, 600, 0);
        k.text('before a complaint', 96, 760, {size: 60, color: CHALK});
        k.text("they can't back up.", 96, 830, {size: 60, color: CHALK2});
        k.ctx.restore();
        k.sweep(96, 902, 700, 8, t0 + 0.6, {color: 'accent'});
      }
      k.ctx.restore();
      return {hostPose: k.talking() ? 'talk' : 'stand', hostScale: 0.55, hostX: 150};
    },

    good: (k, T) => {
      const n = k.data.numbers;
      k.room('framing');
      const r = typed(k, GOOD);
      k.ctx.save();
      if (r.cur >= 0) { const q = k.clamp(k.pop(k.S(GOOD[r.cur][0]), 0.3), 0, 1.2); k.ctx.translate(96, 290); k.ctx.scale(q, q); k.ctx.translate(-96, -290); }
      else slideIn(k, k.S('good'), -500, 0);
      k.chip(r.cur >= 0 ? GOOD[r.cur][3] : 'Good review: copy this', 96, 280, {size: 30, fill: r.cur >= 0 ? 'accent' : 'tag', color: r.cur >= 0 ? INK : 'tagText'});
      k.ctx.restore();
      starRow(k, 672, 306, 26, 62, n.five.value, n.five.value, k.S('good') + 0.2);
      k.ctx.save(); slideIn(k, k.S('good') + 0.1, 0, 800);
      k.phone(100, 360, 800, 630, [
        {text: GOOD_REVIEW, at: -1},
        ...(r.cur >= 0 ? [{text: r.full, reveal: r.reveal, me: true, at: k.S(GOOD[0][0]), typing: r.typingTo}] : []),
      ], {who: 'Example review', size: 39});
      k.ctx.restore();
      if (r.cur >= 0) k.burst(240, 300, k.S(GOOD[r.cur][0]) + 0.05, {n: 12, r: 180});
      // the host steps back (smaller) so nothing covers the reply being typed
      return {hostPose: k.talking() ? 'talk' : 'stand', hostScale: 0.55, hostX: 150};
    },

    bad: (k, T) => {
      const n = k.data.numbers;
      k.room('garage');
      const tn = k.S('bad.name'), ta = k.S('bad.argue');
      k.shape(k.rectPts(72, 262, 840, 150, 0), {fill: INK, line: false});   // a dark band: no ruled lines through the header
      if (T < tn) {
        k.slam('Bad review:', 96, 280, k.S('bad') + 0.1, {size: 60, color: 'accent', from: 0.8});
        k.ctx.save(); slideIn(k, k.S('bad') + 0.3, -600, 0); k.text('a different reply.', 96, 346, {size: 60, color: CHALK}); k.ctx.restore();
        starRow(k, 600, 306, 26, 62, n.two.value, n.five.value, k.S('bad') + 0.3);
      } else {
        k.burst(300, 312, tn + 0.1, {n: 18});
        k.slam('Name the real problem.', 96, 280, tn, {size: 60, color: 'accent', from: 0.6});
        if (T >= ta) k.slam("Don't argue in public.", 96, 346, ta, {size: 60, color: CHALK, stamp: true});
      }
      const r = typed(k, BAD);
      k.ctx.save(); slideIn(k, k.S('bad') + 0.1, 0, 800);
      k.phone(100, 440, 800, 580, [
        {text: BAD_REVIEW, at: -1},
        ...(r.cur >= 0 ? [{text: r.full, reveal: r.reveal, me: true, at: k.S(BAD[0][0]), typing: r.typingTo}] : []),
      ], {who: 'Example review', size: 39});
      k.ctx.restore();
      if (r.cur >= 0) k.burst(820, 740, k.S(BAD[r.cur][0]) + 0.05, {n: 10, r: 160});
      return {hostPose: T >= ta ? 'clip' : (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150};
    },

    turn: (k, T) => {
      k.room('workshop');
      const th = k.S('turn.honest'), tg = k.S('turn.guide');
      k.shape(k.rectPts(60, 262, 870, 150, 0), {fill: INK, line: false});   // a dark band for the header
      if (T < th) k.slam('The part people skip', 96, 280, k.S('turn') + 0.1, {size: 60, color: 'accent', from: 0.8, shake: 6});
      else {
        k.burst(300, 312, th + 0.1, {n: 18});
        k.slam('Hotels, not trades.', 96, 280, th, {size: 60, color: 'accent', from: 0.6});
        if (T >= tg) k.slam('Treat the numbers as a guide.', 96, 354, tg, {size: 39, color: CHALK, stamp: true});
      }
      // the card: bad reviews once hotels replied. Both rows show as it opens, each lights when it is said
      const t0 = k.S('turn') + 0.3, tr = k.S('turn.rarer'), tl = k.S('turn.longer');
      k.ctx.save(); slideIn(k, t0, 0, 700);
      k.panel2(60, 456, 870, 330, {title: 'Bad reviews, once hotels replied'});
      k.text('Fewer', 96, 500, {size: 60, color: T >= tr ? 'accent' : 'muted'});
      k.text('but', 96, 600, {size: 39, color: T >= tl ? CHALK : 'muted'});
      k.text('longer', 96, 644, {size: 60, color: T >= tl ? 'accent' : 'muted'});
      // four short review cards; at "rarer" two drop away, at "longer" the two left stretch tall with more lines
      const grow = k.easeOut((T - tl) / 0.5), drop = k.easeOut((T - tr) / 0.45);
      [0, 1, 2, 3].forEach((i) => {
        const keep = i === 0 || i === 2, x = 320 + i * 140;
        if (!keep && drop >= 1) return;
        const h = keep && T >= tl ? 70 + 170 * grow : 70, w = keep && T >= tl ? 120 + 130 * grow : 120;
        const xx = keep && T >= tl ? 320 + (i === 2 ? 1 : 0) * 290 : x;
        k.ctx.save();
        if (!keep && T >= tr) { k.ctx.globalAlpha *= 1 - drop; k.ctx.translate(0, 120 * drop); }
        k.shape(k.rectPts(xx, 500, w, h, 0), {fill: CHALK, line: false});
        const lines = Math.max(2, Math.floor((h - 20) / 30));
        for (let j = 0; j < lines; j++) k.shape(k.rectPts(xx + 16, 516 + j * 30, j === lines - 1 ? w * 0.4 : w - 32, 10, 0), {fill: GREY, line: false});
        k.ctx.restore();
      });
      if (T >= tr && T < tr + 0.6) k.burst(530, 560, tr + 0.1, {n: 12, r: 160, colors: [GREY, 'paper']});
      if (T >= tl) k.burst(700, 620, tl + 0.4, {n: 16, r: 200});
      k.ctx.restore();
      if (T >= k.S('turn.detail')) {   // a sticker under the card, clear of the cards and the labels
        const td = k.S('turn.detail');
        k.ctx.save(); k.ctx.translate(735, 836); k.ctx.rotate(-0.03); k.ctx.translate(-735, -836); popAt(k, td, 735, 836);
        k.panel2(520, 790, 410, 110, {fill: 'accent', border: INK});
        k.text('More detail', 725, 804, {size: 39, color: INK, align: 'center'});
        k.text('you can act on.', 725, 848, {size: 39, color: INK, align: 'center'});
        k.ctx.restore();
        k.burst(735, 836, td + 0.05, {n: 18});
      }
      return {hostPose: T >= th ? 'shrug' : (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150};
    },

    close: (k, T) => {
      k.room('blackboard'); boardClip(k);
      const t1 = k.S('close'), ta = wordT(k, 'close', /^answer/i, 0.6), tr = wordT(k, 'close', /^review/i, 1.2);
      // centered, so the board reads as one card; the send line is a full-width box, the biggest call on screen
      k.slam('Good or bad,', 540, 270, t1, {size: 120, color: CHALK, from: 0.7, align: 'center'});
      k.burst(540, 330, t1 + 0.1, {n: 10, r: 150, colors: ['paper', '#2F5A4A']});
      if (T >= ta) k.slam('answer every', 540, 390, ta, {size: 120, color: 'accent', from: 0.7, align: 'center'});
      if (T >= tr) { k.slam('review.', 540, 510, tr, {size: 120, color: 'accent', from: 0.7, align: 'center'}); k.burst(540, 560, tr + 0.1, {n: 16, r: 200}); }
      if (T >= k.S('close.send')) {
        const t0 = k.S('close.send');
        k.ctx.save(); popAt(k, t0 - 0.2, 540, 676);
        k.panel2(340, 640, 400, 80, {fill: '#24453A', border: 'accent'}); k.text('ProofNotFluff', 540, 650, {size: 60, color: 'accent', align: 'center'});
        k.ctx.restore();
        k.burst(540, 680, t0 - 0.1, {n: 16});
        k.ctx.save(); slideIn(k, t0 + 0.2, 0, 200);
        k.panel2(84, 740, 900, 236, {fill: INK, border: 'accent'});
        k.text('Send this to whoever', 534, 760, {size: 60, color: CHALK, align: 'center'});
        k.text('runs your', 534, 830, {size: 60, color: CHALK, align: 'center'});
        k.text('Google profile.', 534, 900, {size: 60, color: CHALK2, align: 'center'});
        k.ctx.restore();
      }
      if (T >= k.S('close.next')) {   // the rule underlined as the last words echo the hook
        const t0 = k.S('close.next'), w = k.measure('answer every', {size: 120});
        k.sweep(540 - w / 2, 622, w, 10, t0, {color: 'accent'});
        k.burst(540 + w / 2, 626, t0 + 0.3, {n: 16});
      }
      k.ctx.restore();
      return {hostPose: T >= k.S('close.send') + 1.5 ? 'wave' : 'talk', hostScale: 0.55, hostX: 150};
    },
  },
};
