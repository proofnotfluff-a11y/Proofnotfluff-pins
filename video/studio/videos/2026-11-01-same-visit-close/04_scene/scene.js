// Scene: Close it before you leave the driveway (Lesson 5, Quote Clinic, arcade). One function per top-level cue in 03_cues/cues.md.
// Numbers only from k.data (brief.md -> data.js). Rooms: framing, workshop, blackboard, garage, workshop, framing, blackboard.
// Modeled on lesson 4: a hook card settled on frame 0, slams, sparks, the zoom ladder, dark bands under ruled-board headers.
const CHALK = '#FFF7EA', CHALK2 = '#F7C873', INK = '#1B1420', DARK = '#2B2033', GREY = '#9AA0AD', RED = '#E2633B', HOOK_END = 3.2;
// the ask (our advice, from the topic bank T2 takeaway; Thursday is an example day), broken where it reads best
const ASK = [
  ['ask.l1', ['Here are your options.']],
  ['ask.l2', ['If you want to go ahead today,', 'I can get you on the schedule', 'for Thursday.']],
  ['ask.l3', ['What questions do you have', 'before you pick one?']],
];
// everything written on the board stays inside the board, even while it slides in
const boardClip = (k) => { k.ctx.save(); k.ctx.beginPath(); k.ctx.rect(60, 246, 960, 752); k.ctx.clip(); };
const slideIn = (k, t0, dx = 0, dy = 0) => { const q = k.easeOut((k.T - t0) / 0.35); k.ctx.translate(dx * 0.4 * (1 - q), dy * 0.4 * (1 - q)); k.ctx.globalAlpha *= k.clamp(q * 1.6); return q; };
const fadeOut = (k, t0, d = 0.3) => { k.ctx.globalAlpha *= 1 - k.clamp((k.T - t0) / d); };
const popAt = (k, t0, cx, cy, max = 1.15) => { const q = k.clamp(k.pop(t0), 0, max); k.ctx.translate(cx, cy); k.ctx.scale(q, q); k.ctx.translate(-cx, -cy); };
// the time a word is said (from words.json), at or after a cue; falls back to the cue's start
const wordT = (k, id, re, dflt = 0) => {
  const ws = (window.WORDS && window.WORDS.words) || [];
  const w = ws.find((x) => x.start >= k.S(id) - 0.05 && re.test(x.w));
  return w ? w.start : k.S(id) + dflt;
};
// a bar that grows from t0 to its value, with the value counting up at its end (values from the brief; the count starts at 85%)
const growBar = (k, x, y, w, h, num, t0, color, o = {}) => {
  k.shape(k.rectPts(x, y, w, h, 0), {fill: '#2B2033', line: false});
  k.shape(k.rectPts(x, y, w, h, 0), {stroke: o.track || CHALK, lw: 6, line: false});
  if (k.T < t0) return;
  const p = k.easeOut((k.T - t0) / 0.8);
  k.shape(k.rectPts(x, y, w * (num.value / 100) * p, h, 0), {fill: color, line: false});
  k.slam(k.count(num.value, 0.85 + 0.15 * k.lin(t0, t0 + 0.8), {suffix: '%'}), x + w + 24, y + h / 2 - 33, t0, {size: 60, color, from: 0.5});
  if (p >= 0.99 && o.sparks !== false) k.burst(x + w * (num.value / 100), y + h / 2, t0 + 0.8, {n: 16, r: 200});
};
// a dark band behind a header, so no ruled line or plank runs through it
const band = (k, y = 262, h = 110) => k.shape(k.rectPts(72, y, 840, h, 0), {fill: INK, line: false});
// a tick box that checks when its words are said
const tickBox = (k, x, y, t0) => {
  k.shape(k.rectPts(x, y, 44, 44, 0), {fill: CHALK, line: false});
  k.shape(k.rectPts(x + 4, y + 4, 36, 36, 0), {stroke: DARK, lw: 4, line: false});
  if (k.T < t0) return;
  const q = k.easeOut((k.T - t0) / 0.25);
  k.shape([[x + 8, y + 22], [x + 18, y + 34], [x + 18 + 22 * q, y + 34 - 30 * q]], {stroke: 'accent', lw: 8, closed: false, line: false});
};
// the work van in the driveway (ours, drawn in blocks)
const van = (k, x, y) => {
  k.shape(k.rectPts(x - 30, y + 210, 520, 40, 0), {fill: '#9AA0AD', line: false});   // the driveway slab
  k.shape(k.rectPts(x - 30, y + 210, 520, 8, 0), {fill: '#C9CCD3', line: false});
  k.shape(k.rectPts(x, y, 300, 190, 0), {fill: CHALK, line: false});                  // the cargo box
  k.shape(k.rectPts(x + 300, y + 60, 140, 130, 0), {fill: CHALK, line: false});       // the cab
  k.shape(k.rectPts(x + 320, y + 76, 90, 50, 0), {fill: '#5B8FB9', line: false});     // the windshield
  k.shape(k.rectPts(x, y + 110, 440, 22, 0), {fill: 'accent', line: false});          // the stripe
  k.shape(k.rectPts(x + 420, y + 150, 30, 18, 0), {fill: CHALK2, line: false});       // the headlight
  for (const wx of [x + 80, x + 350]) { k.shape(k.ellPts(wx, y + 196, 40, 40, 20), {fill: INK, line: false}); k.shape(k.ellPts(wx, y + 196, 16, 16, 12), {fill: GREY, line: false}); }
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 5',
  focus: {'hook.same': [740, 620], 'stakes.top77': [400, 600], 'stakes.rest': [400, 720], 'why.momentum': [400, 440],
          'why.fewer': [400, 860], 'ask.l2': [500, 640], 'ask.l3': [500, 820], 'skip.obj': [480, 800],
          'caveat.pattern': [480, 520], 'close.send': [540, 880]},
  sections: {
    hook: (k, T) => {
      const n = k.data.numbers;
      if (T < HOOK_END) {   // the hook card: settled on frame 0, no host, no dialog (nothing covers the claim or its source)
        k.room('framing');
        k.shape(k.rectPts(0, 230, 1080, 860, 0), {fill: INK, line: false});
        k.slam('Top shops close', 540, 290, -1, {size: 120, color: CHALK, align: 'center'});
        k.slam(n.topClose.shown, 540, 440, -1, {size: 200, color: 'accent', align: 'center'});
        k.slam('of estimates', 540, 676, -1, {size: 120, color: CHALK, align: 'center'});
        k.slam('on the same visit.', 540, 800, -1, {size: 60, color: CHALK, align: 'center'});
        k.burst(540, 540, 0.1, {n: 26, r: 380});
        k.burst(540, 540, 1.4, {n: 14, r: 300, colors: ['accent2', 'paper']});
        k.sweep(300, 880, 480, 10, 0.6, {color: 'accent'});
        k.text(`ServiceTitan data, ${n.stMonths.shown} months to Jan ${n.stYear.shown}`, 540, 920, {size: 39, color: '#E6D3BC', align: 'center'});
        k.text('Quote Clinic', 540, 990, {size: 39, color: CHALK2, align: 'center'});
        return {host: false, speech: false};
      }
      k.room('framing');
      k.ctx.save(); slideIn(k, HOOK_END, -500, 0); k.chip('Quote Clinic', 96, 280, {size: 30}); k.ctx.restore();
      // the van in the driveway
      k.ctx.save(); slideIn(k, HOOK_END, -700, 0); van(k, 96, 560); k.ctx.restore();
      // the estimate on its clipboard
      k.ctx.save(); slideIn(k, HOOK_END + 0.15, 600, 0);
      k.panel2(600, 380, 330, 440, {fill: CHALK, border: DARK, title: 'Estimate'});
      k.text('Estimate', 630, 418, {size: 60, color: DARK});
      for (let i = 0; i < 4; i++) k.shape(k.rectPts(630, 512 + i * 44, i === 3 ? 160 : 260, 14, 0), {fill: GREY, line: false});
      k.text('Total: $', 630, 712, {size: 60, color: DARK});
      k.ctx.restore();
      const ts = wordT(k, 'hook.same', /^same/i);
      if (T >= k.S('hook.same')) {   // signed on the visit: the stamp lands on the lines, never on the title or total
        k.stampIn(ts, () => {
          k.ctx.save(); k.ctx.translate(765, 560); k.ctx.rotate(-0.08); k.ctx.translate(-765, -560);
          k.panel2(640, 500, 250, 120, {fill: '#24453A', border: 'accent'});
          k.text('SIGNED.', 765, 512, {size: 39, color: CHALK, align: 'center'});
          k.text('Same visit.', 765, 556, {size: 39, color: 'accent', align: 'center'});
          k.ctx.restore();
        }, {at: [765, 620]});
        k.burst(765, 560, ts + 0.12, {n: 20, r: 240});
      }
      if (T >= k.S('hook.ask')) {   // the promise: ask before you leave
        const t0 = k.S('hook.ask');
        k.ctx.save(); popAt(k, t0, 290, 440);
        k.panel2(96, 390, 400, 110, {fill: 'accent', border: INK});
        k.text('Ask before', 296, 402, {size: 39, color: INK, align: 'center'});
        k.text('you leave.', 296, 446, {size: 39, color: INK, align: 'center'});
        k.shape([[250, 500], [290, 500], [262, 536]], {fill: 'accent', line: false});
        k.ctx.restore();
        k.burst(296, 446, t0 + 0.05, {n: 16});
      }
      return {hostPose: T >= k.S('hook.same') ? 'point' : (k.talking() ? 'talk' : 'stand'), hostAt: [700, 600], hostScale: 0.55, hostX: 150};
    },

    stakes: (k, T) => {
      const n = k.data.numbers;
      k.room('workshop');
      k.ctx.save(); slideIn(k, k.S('stakes'), 0, 700);
      k.panel2(60, 300, 870, 480, {title: 'ServiceTitan'});
      k.text('Estimates closed', 96, 336, {size: 39, color: CHALK});
      k.slam('on the same visit', 96, 384, k.S('stakes') + 0.4, {size: 60, color: CHALK2, from: 0.5});
      k.ctx.restore();
      if (T >= k.S('stakes.window')) {
        k.ctx.save(); slideIn(k, k.S('stakes.window'), 500, 0);
        k.text(`${n.stMonths.shown} months to Jan ${n.stYear.shown}`, 96, 466, {size: 39, color: 'muted'});
        k.ctx.restore();
      }
      if (T >= k.S('stakes') + 0.3) {   // both rows show as the panel opens; each lights up and fills when it is said
        const t1 = wordT(k, 'stakes.top77', /^seventy/i), t2 = wordT(k, 'stakes.rest', /^sixty/i);
        k.ctx.save(); slideIn(k, k.S('stakes') + 0.3, -500, 0);
        if (T >= k.S('stakes.top')) k.slam(`Top ${n.topPct.shown} by revenue`, 96, 520, k.S('stakes.top'), {size: 39, color: 'accent', from: 0.5});
        else k.text('Top shops', 96, 520, {size: 39, color: 'muted'});
        growBar(k, 96, 566, 600, 52, n.topClose, t1, 'accent');
        k.text('Everyone else', 96, 640, {size: 39, color: T >= k.S('stakes.rest') ? CHALK : 'muted'});
        growBar(k, 96, 686, 600, 52, n.restClose, t2, '#C9CCD3', {sparks: false});
        k.ctx.restore();
        if (k.live('stakes.top')) k.sweep(96, 562, 600, 4, k.S('stakes.top') + 0.2, {color: 'accent'});
      }
      return {hostPose: k.live('stakes.top77') ? 'point' : (k.talking() ? 'talk' : 'stand'), hostAt: [560, 600], hostScale: 0.55, hostX: 150};
    },

    why: (k, T) => {
      const n = k.data.numbers;
      k.room('blackboard'); boardClip(k);
      // the header, the gap in the accent
      const t0 = k.S('why'), x1 = 96 + k.measure('Why a ', {size: 60}), x2 = x1 + k.measure(`${n.gap.shown} `, {size: 60});
      k.slam('Why a', 96, 280, t0, {size: 60, color: CHALK2, from: 0.5});
      k.slam(n.gap.shown, x1, 280, wordT(k, 'why', /^fifteen/i), {size: 60, color: 'accent', from: 0.9});
      k.slam('point gap?', x2, 280, wordT(k, 'why', /^point/i), {size: 60, color: CHALK2, from: 0.5});
      if (T >= k.S('why.momentum')) {
        const tm = wordT(k, 'why.momentum', /^momentum/i, 1.2);
        k.text('ServiceTitan:', 96, 372, {size: 39, color: '#D8D0C0', alpha: k.clamp((T - k.S('why.momentum')) / 0.3)});
        if (T >= tm) { k.slam('Momentum.', 96, 420, tm, {size: 120, color: CHALK, from: 0.7}); k.burst(380, 480, tm + 0.1, {n: 14, colors: ['paper', 'accent2']}); }
      }
      // quote to decision: a chalk line that stretches while they wait, then snaps short when you close on the visit
      if (T >= k.S('why.wait')) {
        const tw = k.S('why.wait'), tf = k.S('why.fewer');
        const grow = k.easeOut((T - tw) / 2.2), snap = T >= tf ? k.easeOut((T - tf) / 0.4) : 0;
        const len = 120 + 560 * grow - 520 * snap, y = 620;
        k.text('Quote', 96, y - 70, {size: 39, color: CHALK});
        k.shape(k.rectPts(110, y, Math.max(8, len), 8, 0), {fill: CHALK, line: false});
        k.shape(k.ellPts(110, y + 4, 12, 12, 12), {fill: CHALK, line: false});
        k.shape(k.ellPts(110 + len, y + 4, 12, 12, 12), {fill: snap > 0.5 ? 'accent' : CHALK2, line: false});
        k.text('Decision', 110 + len, y - 70, {size: 39, color: snap > 0.5 ? 'accent' : CHALK2, align: snap > 0.5 ? 'left' : 'center'});
        if (T < tf) {   // the clock spins while they wait
          const cx = 860, cy = 470, a = (T - tw) * 4;
          k.shape(k.ellPts(cx, cy, 56, 56, 28), {stroke: CHALK, lw: 6, line: false});
          k.shape([[cx, cy], [cx + 40 * Math.sin(a), cy - 40 * Math.cos(a)]], {stroke: CHALK2, lw: 6, closed: false, line: false});
          k.shape([[cx, cy], [cx + 26 * Math.sin(a / 12), cy - 26 * Math.cos(a / 12)]], {stroke: CHALK, lw: 6, closed: false, line: false});
        }
      }
      if (T >= k.S('why.competitor')) {
        const tc = wordT(k, 'why.competitor', /^competitor/i, 0.3);
        k.ctx.save(); slideIn(k, k.S('why.competitor'), -600, 0);
        k.text('Call a competitor.', 96, 690, {size: 60, color: CHALK});
        k.ctx.restore();
        if (T >= tc && T < k.S('why.fewer')) {   // a phone rings beside it
          const sh = Math.sin(T * 40) * 4, px = 820;
          k.shape(k.rectPts(px + sh, 676, 64, 110, 0), {fill: CHALK2, line: false});
          k.shape(k.rectPts(px + 8 + sh, 690, 48, 70, 0), {fill: '#24453A', line: false});
          if ((T * 3) % 1 < 0.5) { k.shape([[px - 26, 700], [px - 12, 714]], {stroke: CHALK, lw: 5, closed: false, line: false}); k.shape([[px + 90, 700], [px + 76, 714]], {stroke: CHALK, lw: 5, closed: false, line: false}); }
        }
      }
      if (T >= k.S('why.talk')) {
        k.ctx.save(); slideIn(k, k.S('why.talk'), -600, 0);
        k.text('Talk themselves out.', 96, 770, {size: 60, color: CHALK});
        k.ctx.restore();
      }
      if (T >= k.S('why.fewer')) {
        const tf = wordT(k, 'why.fewer', /^fewer/i, 1.0);
        if (T >= tf) {
          k.slam('Fewer follow-ups.', 96, 870, tf, {size: 60, color: 'accent', from: 0.8});
          k.sweep(96, 940, k.measure('Fewer follow-ups.', {size: 60}), 8, tf + 0.3, {color: 'accent'});
          k.burst(420, 900, tf + 0.1, {n: 16});
        }
      }
      k.ctx.restore();
      return {hostPose: k.live('why.fewer') ? 'point' : (k.talking() ? 'talk' : 'stand'), hostAt: [400, 880], hostScale: 0.55, hostX: 150};
    },

    ask: (k, T) => {
      k.room('garage');
      band(k);
      k.slam('Ask before you leave.', 96, 280, k.S('ask') + 0.1, {size: 60, color: 'accent', from: 0.8});
      // the copyable line, held big; the rows show (numbers and empty lines) as the card opens, each fills when it is said
      k.ctx.save(); slideIn(k, k.S('ask') + 0.2, 0, 800);
      k.panel2(60, 420, 860, 540, {fill: CHALK, border: DARK, title: 'Say this (example)'});
      let y = 462;
      ASK.forEach(([id, lines], i) => {
        const t0 = k.S(id), on = T >= t0;
        k.shape(k.rectPts(96, y, 48, 48, 0), {fill: on ? 'accent' : GREY, line: false});
        k.text(String(i + 1), 120, y + 4, {size: 39, color: INK, align: 'center', lint: false});
        lines.forEach((ln, li) => {
          const ly = y + li * 52;
          if (!on) { k.shape(k.rectPts(170, ly + 18, li === lines.length - 1 ? 300 : 620, 14, 0), {fill: '#D8D0C0', line: false}); return; }
          if (id === 'ask.l2' && li === 2 && T >= k.S('ask.sched')) {   // the day is an example: highlighted, tagged
            const tx = 170 + k.measure('for ', {size: 39});
            k.sweep(tx - 6, ly - 4, k.measure('Thursday.', {size: 39}) + 12, 50, wordT(k, 'ask.sched', /^thursday/i, 1.5), {color: CHALK2});
          }
          k.ctx.save(); slideIn(k, t0 + li * 0.12, 0, 60);
          k.text(ln, 170, ly, {size: 39, color: DARK});
          k.ctx.restore();
        });
        if (on) k.burst(120, y + 24, t0 + 0.05, {n: 10, r: 150});
        y += lines.length * 52 + 46;
      });
      k.ctx.restore();
      if (T >= k.S('ask.sched')) {
        const td = wordT(k, 'ask.sched', /^thursday/i, 1.5);
        if (T >= td) { k.ctx.save(); popAt(k, td, 560, 700); k.chip('Your day', 470, 676, {size: 24, fill: 'tag', color: 'tagText'}); k.ctx.restore(); }
      }
      return {hostPose: k.talking() ? 'talk' : 'stand', hostScale: 0.55, hostX: 150};
    },

    skip: (k, T) => {
      k.room('workshop');
      band(k);
      k.slam('The part people skip.', 96, 280, k.S('skip') + 0.1, {size: 60, color: 'accent', from: 0.8, shake: 6});
      // the last line of the ask, quoted big
      k.ctx.save(); slideIn(k, k.S('skip') + 0.2, 0, 600);
      k.panel2(72, 400, 840, 140, {fill: INK, border: 'accent'});
      k.text('"What questions do you have', 108, 420, {size: 39, color: CHALK});
      k.text('before you pick one?"', 108, 470, {size: 39, color: CHALK});
      k.ctx.restore();
      const tst = k.S('skip.st');
      // why it works: under the quote, never on it
      if (T >= k.S('skip.worry') && T < tst + 0.3) {
        k.ctx.save(); if (T >= tst) fadeOut(k, tst);
        k.ctx.save(); slideIn(k, k.S('skip.worry'), -600, 0);
        k.panel2(72, 576, 840, 176, {fill: INK, border: 'line'});
        k.text('It brings the worry out', 108, 600, {size: 60, color: CHALK2});
        k.ctx.restore();
        if (T >= k.S('skip.there')) { k.ctx.save(); slideIn(k, k.S('skip.there'), -600, 0); k.text("while you're there.", 108, 670, {size: 60, color: 'accent'}); k.ctx.restore(); }
        k.ctx.restore();
      }
      if (T >= tst) {   // what ServiceTitan says the same-visit close shows: three rows, ticked as said
        k.ctx.save(); slideIn(k, tst + 0.2, 0, 700);
        k.panel2(72, 600, 840, 380, {title: 'ServiceTitan'});
        k.text('Same-visit closes show', 108, 636, {size: 39, color: CHALK});
        k.text('how well your tech:', 108, 680, {size: 39, color: CHALK});
        const rows = [['handles objections', wordT(k, 'skip.obj', /^objections/i, 0.4)], ['frames financing', wordT(k, 'skip.obj', /^financing/i, 1.2)], ['asks for the sale', wordT(k, 'skip.sale', /^sale/i, 0.6)]];
        rows.forEach(([s, t0], i) => {
          const ry = 752 + i * 72;
          tickBox(k, 108, ry, t0);
          if (i === 2 && T >= t0) k.sweep(176, ry - 2, k.measure(s, {size: 39}) + 12, 48, t0 + 0.1, {color: 'accent', alpha: 0.9});
          k.text(s, 182, ry + 2, {size: 39, color: T >= t0 ? (i === 2 ? INK : CHALK) : 'muted'});
        });
        k.ctx.restore();
        const ts = wordT(k, 'skip.sale', /^sale/i, 0.6);
        k.burst(300, 920, ts + 0.1, {n: 16});
      }
      return {hostPose: k.live('skip.there') ? 'point' : (k.talking() ? 'talk' : 'stand'), hostAt: [420, 680], hostScale: 0.55, hostX: 150};
    },

    caveat: (k, T) => {
      k.room('framing');
      band(k);
      k.slam('One honest note.', 96, 280, k.S('caveat') + 0.1, {size: 60, color: CHALK2, from: 0.6});
      const tp = k.S('caveat.pattern');
      if (T < tp) {   // while he says it: what the note is about, the two bars it qualifies
        const n = k.data.numbers;
        k.ctx.save(); slideIn(k, k.S('caveat') + 0.2, 0, 400);
        k.panel2(72, 400, 840, 150, {fill: INK, border: 'line'});
        k.text(`Top ${n.topPct.shown}: ${n.topClose.shown}`, 108, 420, {size: 39, color: 'accent'});
        k.text(`Everyone else: ${n.restClose.shown}`, 108, 476, {size: 39, color: CHALK});
        k.ctx.restore();
      } else {
        k.ctx.save(); popAt(k, tp - 0.1, 490, 640, 1.06);
        k.panel2(72, 400, 840, 520, {fill: INK, border: 'accent'});
        k.ctx.restore();
        k.stampIn(tp, () => {
          k.text('A pattern,', 108, 420, {size: 120, color: CHALK});
          k.text('not proof.', 108, 524, {size: 120, color: 'accent'});
        }, {at: [400, 640]});
        k.ctx.save(); slideIn(k, tp + 0.5, 500, 0);
        k.text('ServiceTitan: correlated, not a cause.', 108, 650, {size: 30, color: '#D8D0C0'});
        k.ctx.restore();
      }
      if (T >= k.S('caveat.other')) {
        k.ctx.save(); slideIn(k, k.S('caveat.other'), -600, 0);
        k.text('Top shops may close more', 108, 700, {size: 39, color: CHALK});
        k.text('for other reasons.', 108, 744, {size: 39, color: CHALK});
        k.ctx.restore();
      }
      if (T >= k.S('caveat.cost')) {
        const t0 = wordT(k, 'caveat.cost', /^costs/i, 0.3);
        if (T >= t0) {
          k.slam('Asking costs you', 108, 798, t0, {size: 60, color: CHALK2, from: 0.6});
          k.slam('one sentence.', 108, 856, wordT(k, 'caveat.cost', /^sentence/i, 0.8) - 0.2, {size: 60, color: 'accent', from: 0.8});
          k.burst(400, 880, t0 + 0.6, {n: 16});
        }
      }
      return {hostPose: k.live('caveat.cost') ? 'shrug' : (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150};
    },

    close: (k, T) => {
      k.room('blackboard'); boardClip(k);
      const t1 = k.S('close'), tw = wordT(k, 'close', /^wait/i, 0.6), td = k.S('close.drive'), tdw = wordT(k, 'close.drive', /^driveway/i, 0.6);
      // centered, so the board reads as one card; the send line is the biggest call on screen
      k.slam("Don't drive off", 540, 284, t1, {size: 120, color: CHALK, from: 0.7, align: 'center'});
      k.slam('and wait.', 540, 390, tw, {size: 120, color: CHALK, from: 0.7, align: 'center'});
      k.burst(540, 320, t1 + 0.1, {n: 10, r: 150, colors: ['paper', '#2F5A4A']});
      if (T >= td) {
        k.slam('Ask in the', 540, 500, td, {size: 120, color: 'accent', from: 0.7, align: 'center'});
        k.slam('driveway.', 540, 606, tdw, {size: 120, color: 'accent', from: 0.7, align: 'center'});
        k.burst(540, 560, td + 0.1, {n: 16, r: 200});
      }
      if (T >= k.S('close.send')) {
        const t0 = k.S('close.send');
        k.ctx.save(); popAt(k, t0 - 0.2, 540, 760);
        k.panel2(340, 734, 400, 66, {fill: '#24453A', border: 'accent'}); k.text('ProofNotFluff', 540, 738, {size: 60, color: 'accent', align: 'center'});
        k.ctx.restore();
        k.burst(540, 762, t0 - 0.1, {n: 16});
        k.ctx.save(); slideIn(k, t0 + 0.2, 0, 200);
        k.panel2(84, 812, 900, 160, {fill: INK, border: 'accent'});
        k.text('Send this to whoever', 534, 826, {size: 60, color: CHALK, align: 'center'});
        k.text('goes out on your estimates.', 534, 892, {size: 60, color: CHALK2, align: 'center'});
        k.ctx.restore();
      }
      if (T >= k.S('close.next')) {   // the payoff line underlined as the last words echo the hook
        const t0 = k.S('close.next'), w = k.measure('driveway.', {size: 120});
        k.sweep(540 - w / 2, 714, w, 10, t0, {color: 'accent'});
        k.burst(540 + w / 2, 714, t0 + 0.3, {n: 16});
      }
      k.ctx.restore();
      return {hostPose: T >= k.S('close.send') + 1.5 ? 'wave' : 'talk', hostScale: 0.55, hostX: 150};
    },
  },
};
