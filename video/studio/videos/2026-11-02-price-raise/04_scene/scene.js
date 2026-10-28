// Scene: Raise prices with a reason customers accept (Lesson 6, Pricing Clinic, arcade). One function per top-level cue
// in 03_cues/cues.md. Numbers only from k.data (brief.md -> data.js). Rooms: framing, garage, blackboard, workshop,
// garage, blackboard, framing. Modeled on lesson 4: a hook card settled on frame 0, slams, sparks, count-ups from 85%.
const CHALK = '#FFF7EA', CHALK2 = '#F7C873', INK = '#1B1420', DARK = '#2B2033', GREY = '#9AA0AD', RED = '#E2633B', TEAL = '#6FB7A8';
const LETTER = [
  ['line.l1', ['Starting next month,', 'our rates are going up.']],
  ['line.l2', ['Our labor and material', 'costs went up this year.']],
  ['line.l3', ["Anything you've already", 'approved stays at the', 'price we quoted.']],
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
// a bar that grows from t0 to its value, the value counting up from 85% at its end (values from the brief)
const growBar = (k, x, y, w, h, num, t0, color, o = {}) => {
  k.shape(k.rectPts(x, y, w, h, 0), {fill: DARK, line: false});
  k.shape(k.rectPts(x, y, w, h, 0), {stroke: o.track || CHALK, lw: 6, line: false});
  if (k.T < t0) return;
  const p = k.easeOut((k.T - t0) / 0.8);
  k.shape(k.rectPts(x, y, w * (num.value / 100) * p, h, 0), {fill: color, line: false});
  k.slam(k.count(num.value, 0.85 + 0.15 * k.lin(t0, t0 + 0.8), {suffix: '%'}), x + w + 24, y + h / 2 - 33, t0, {size: 60, color, from: 0.5});
  if (p >= 0.99 && o.sparks !== false) k.burst(x + w * (num.value / 100), y + h / 2, t0 + 0.8, {n: 16, r: 200});
};
// a verdict row: its label and empty track show from the start; the bar fills and the label lights when it is said
const verdict = (k, x, y, label, num, nShown, t0, color) => {
  const on = k.T >= t0;
  k.text(label, x, y, {size: 39, color: on ? color : 'muted'});
  growBar(k, x, y + 46, 520, 48, num, t0, color);
  if (on) { k.ctx.save(); slideIn(k, t0 + 0.4, 200, 0); k.text(`N = ${nShown}`, x + 520, y + 104, {size: 30, color: 'muted', align: 'right'}); k.ctx.restore(); }
};
// falling snow inside a box, worked out from the time alone
const snowfall = (k, x, y, w, h, t0) => {
  if (k.T < t0) return;
  const a = k.clamp((k.T - t0) / 0.4);
  for (let i = 0; i < 34; i++) {
    const sp = 70 + (i % 5) * 22, px = x + ((i * 137.3) % w) + Math.sin(k.T * 1.3 + i) * 8;
    const py = y + (((i * 59.7) + (k.T - t0) * sp) % h), s = 6 + (i % 3) * 3;
    k.shape(k.rectPts(px, py, s, s, 0), {fill: CHALK, line: false, alpha: 0.55 * a});
  }
};
const shovel = (k, x, y) => {   // a pixel snow shovel: handle, grip, blade
  k.shape(k.rectPts(x + 54, y, 16, 190, 0), {fill: '#B07A47', line: false});
  k.shape(k.rectPts(x + 34, y - 10, 56, 18, 0), {fill: '#5A3A22', line: false});
  k.shape([[x, y + 190], [x + 124, y + 190], [x + 112, y + 280], [x + 12, y + 280]], {fill: '#5B8FB9', line: false});
  k.shape(k.rectPts(x, y + 190, 124, 12, 0), {fill: '#87CEEB', line: false});
};
const lettuce = (k, cx, cy) => {
  k.shape(k.ellPts(cx, cy, 46, 40, 20), {fill: '#3E7A62', line: false});
  k.shape(k.ellPts(cx - 10, cy - 6, 30, 26, 16), {fill: '#6FB7A8', line: false});
  k.shape(k.ellPts(cx + 8, cy + 4, 16, 14, 12), {fill: '#24453A', line: false});
};
const house = (k, cx, cy) => {
  k.shape([[cx - 50, cy - 6], [cx, cy - 52], [cx + 50, cy - 6]], {fill: RED, line: false});
  k.shape(k.rectPts(cx - 40, cy - 6, 80, 58, 0), {fill: CHALK, line: false});
  k.shape(k.rectPts(cx - 12, cy + 16, 24, 36, 0), {fill: '#6B4226', line: false});
};
const jar = (k, x, y, tagT) => {
  k.shape(k.rectPts(x, y, 70, 96, 0), {fill: '#B07A47', line: false});
  k.shape(k.rectPts(x - 4, y - 18, 78, 22, 0), {fill: RED, line: false});
  k.shape(k.rectPts(x + 10, y + 30, 50, 40, 0), {fill: CHALK, line: false});
  if (k.T >= tagT) { const q = k.clamp(k.pop(tagT), 0, 1.1); k.ctx.save(); k.ctx.translate(x + 35, y + 50); k.ctx.scale(q, q); k.shape(k.rectPts(-24, -14, 48, 28, 0), {fill: RED, line: false}); k.ctx.restore(); }
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 6',
  focus: {'hook.most': [720, 560], 'shovel.twenty': [600, 560], 'shovel.82': [400, 830], 'costs.79': [460, 560],
          'costs.75': [460, 840], 'line.l3': [500, 720], 'stock.79': [400, 830], 'stock.keep': [700, 720],
          'caveat.fair': [500, 720]},
  sections: {
    hook: (k, T) => {
      const n = k.data.numbers, hookEnd = Math.min(k.S('hook.cost'), 4.0);
      if (T < hookEnd) {   // the hook card: settled on frame 0, no host, no dialog (nothing covers the claim or its source)
        k.room('framing');
        k.shape(k.rectPts(0, 230, 1080, 920, 0), {fill: INK, line: false});
        k.slam(n.shovelUnfair.shown, 540, 270, -1, {size: 200, color: RED, align: 'center'});
        k.slam('called a', 540, 500, -1, {size: 120, color: CHALK, align: 'center'});
        k.slam('snowstorm raise', 540, 630, -1, {size: 120, color: CHALK, align: 'center'});
        k.slam('unfair.', 540, 760, -1, {size: 120, color: RED, align: 'center'});
        k.burst(540, 400, 0.1, {n: 26, r: 380, colors: [RED, 'accent2', 'paper']});
        k.burst(540, 400, 1.4, {n: 14, r: 300, colors: ['accent2', 'paper']});
        k.sweep(300, 896, 480, 10, 0.6, {color: RED});
        k.text('Phone survey, Toronto and Vancouver,', 540, 930, {size: 39, color: '#E6D3BC', align: 'center'});
        k.text(`${n.fieldStart.shown} to ${n.fieldEnd.shown}`, 540, 976, {size: 39, color: '#E6D3BC', align: 'center'});
        k.text(`American Economic Review, ${n.year.shown}`, 540, 1024, {size: 30, color: '#E6D3BC', align: 'center'});
        k.text('Pricing Clinic', 540, 1076, {size: 39, color: CHALK2, align: 'center'});
        return {host: false, speech: false};
      }
      k.room('framing');
      k.ctx.save(); slideIn(k, hookEnd, -500, 0); k.chip('Pricing Clinic', 96, 280, {size: 30}); k.ctx.restore();
      // left: the storm raise, the verdict already in
      k.ctx.save(); slideIn(k, hookEnd + 0.05, -600, 0);
      k.panel2(96, 380, 400, 380, {border: RED, title: 'Snowstorm raise'});
      k.text(n.shovelUnfair.shown, 296, 440, {size: 120, color: RED, align: 'center'});
      k.text('unfair', 296, 600, {size: 60, color: CHALK, align: 'center'});
      k.ctx.restore();
      // right: the cost raise; "Most: acceptable" stamps in when it is said
      const tm = k.S('hook.most');
      k.ctx.save(); slideIn(k, hookEnd + 0.3, 600, 0);
      k.panel2(540, 380, 390, 380, {border: TEAL, title: 'Covers your costs'});
      if (T < tm) k.text('?', 735, 500, {size: 120, color: 'muted', align: 'center'});
      k.ctx.restore();
      if (T >= tm) {
        k.slam('Most:', 735, 450, tm, {size: 60, color: CHALK, align: 'center', stamp: true});
        k.slam('acceptable', 735, 560, tm + 0.15, {size: 60, color: TEAL, align: 'center', stamp: true});
        k.burst(735, 560, tm + 0.1, {n: 18, colors: [TEAL, 'accent2', 'paper']});
      }
      const tl = k.S('hook.line');
      if (T >= tl) {   // the artifact peeks up: a note with three lines, filled in later
        k.ctx.save(); slideIn(k, tl, 0, 300);
        k.panel2(300, 800, 630, 150, {fill: CHALK, border: DARK, title: 'Your price note'});
        for (let i = 0; i < 3; i++) k.shape(k.rectPts(336, 840 + i * 30, i === 2 ? 380 : 540, 12, 0), {fill: GREY, line: false});
        k.ctx.restore();
        k.burst(615, 870, tl + 0.3, {n: 12, r: 180, colors: ['accent2', 'paper']});
      }
      return {hostPose: k.live('hook.most') ? 'point' : (k.talking() ? 'talk' : 'stand'), hostAt: [735, 520], hostScale: 0.55, hostX: 150};
    },

    shovel: (k, T) => {
      const n = k.data.numbers, t0 = k.S('shovel');
      k.room('garage');
      k.ctx.save(); slideIn(k, t0, 0, 700);
      k.panel2(60, 300, 870, 640, {title: 'Question 1'});
      k.slam('A hardware store', 96, 336, t0 + 0.3, {size: 60, color: CHALK2, from: 0.5});
      k.text(`American Economic Review, ${n.year.shown}`, 96, 410, {size: 30, color: 'muted'});
      // the verdict row shows as the panel opens (label and empty track)
      verdict(k, 96, 770, 'Unfair', n.shovelUnfair, n.shovelN.shown, k.S('shovel.82'), RED);
      k.ctx.restore();
      const ts = k.S('shovel.storm');
      k.ctx.save(); k.ctx.beginPath(); k.ctx.rect(66, 306, 858, 450); k.ctx.clip(); snowfall(k, 66, 306, 858, 450, ts); k.ctx.restore();
      const tp = k.S('shovel.price');
      if (T >= tp) {
        k.ctx.save(); slideIn(k, tp, -500, 0); shovel(k, 120, 470); k.ctx.restore();
        k.ctx.save(); popAt(k, tp + 0.2, 400, 540);
        k.text(n.shovelFrom.shown, 300, 480, {size: 120, color: CHALK});
        k.ctx.restore();
      }
      const tw = wordT(k, 'shovel.twenty', /^twenty/i, 0.6);
      if (T >= tw) {   // the price jumps: $15 struck, $20 slams in red
        const q = k.easeOut((T - tw) / 0.25), w15 = k.measure(n.shovelFrom.shown, {size: 120});
        k.shape(k.rectPts(292, 536, (w15 + 16) * q, 12, 0), {fill: RED, line: false});
        k.slam(n.shovelTo.shown, 600, 480, tw, {size: 120, color: RED, from: 0.8, shake: 6});
        k.burst(680, 540, tw + 0.05, {n: 18, colors: [RED, 'accent2', 'paper']});
      }
      if (T >= ts) {
        k.ctx.save(); slideIn(k, ts, 500, 0);
        k.text('The morning after', 300, 640, {size: 39, color: CHALK});
        k.text('a big snowstorm', 300, 684, {size: 39, color: CHALK});
        k.ctx.restore();
      }
      if (T >= k.S('shovel.luck')) {   // a sticker on the panel's top corner, clear of the prices and the bar
        const tk = k.S('shovel.luck');
        k.ctx.save(); k.ctx.translate(790, 690); k.ctx.rotate(-0.04); k.ctx.translate(-790, -690); popAt(k, tk, 790, 690);
        k.panel2(660, 636, 250, 104, {fill: 'accent', border: INK});
        k.text('A raise on', 785, 650, {size: 39, color: INK, align: 'center'});
        k.text('bad luck.', 785, 690, {size: 39, color: INK, align: 'center'});
        k.ctx.restore();
        k.burst(785, 690, tk + 0.05, {n: 18});
      }
      return {hostPose: k.live('shovel.82') ? 'point' : (k.talking() ? 'talk' : 'stand'), hostAt: [400, 830], hostScale: 0.55, hostX: 150};
    },

    costs: (k, T) => {
      const n = k.data.numbers, t0 = k.S('costs');
      k.room('blackboard'); boardClip(k);
      k.shape(k.rectPts(72, 262, 840, 104, 0), {fill: INK, line: false});   // a dark band: no ruled lines through the header
      k.slam('The reason: costs', 96, 282, t0 + 0.1, {size: 60, color: CHALK2, from: 0.6});
      // both rows show as the board opens (labels and empty tracks); each lights up and fills when it is said
      const tl = k.S('costs.lettuce'), tc = k.S('costs.charged'), tr = k.S('costs.rent');
      k.ctx.save(); slideIn(k, t0 + 0.2, -600, 0);
      lettuce(k, 146, 450);
      k.text(`Lettuce: wholesale +${n.lettuceCents.shown} cents a head`, 220, 400, {size: 39, color: T >= tl ? CHALK : 'muted'});
      if (T >= tc) { k.arrow([230, 474], [290, 474], k.lin(tc, tc + 0.3), {color: TEAL, lw: 8}); k.slam(`Price +${n.lettuceCents.shown} cents`, 310, 452, tc + 0.2, {size: 39, color: CHALK2, from: 0.5}); }
      verdict(k, 220, 520, 'Acceptable', n.lettuceOk, n.lettuceN.shown, k.S('costs.79'), TEAL);
      k.ctx.restore();
      k.ctx.save(); slideIn(k, t0 + 0.4, -600, 0);
      house(k, 146, 760);
      k.text('Rent up at renewal, to cover costs', 220, 700, {size: 39, color: T >= tr ? CHALK : 'muted'});
      verdict(k, 220, 760, 'Acceptable', n.rentOk, n.rentN.shown, k.S('costs.75'), TEAL);
      k.ctx.restore();
      if (k.live('costs.lettuce')) k.spot(220, 400, 640, 40, tl + 0.1, {color: TEAL, lw: 5, pad: 8});
      if (k.live('costs.rent')) k.spot(220, 700, 640, 40, tr + 0.1, {color: TEAL, lw: 5, pad: 8});
      k.ctx.restore();
      return {hostPose: k.live('costs.79') || k.live('costs.75') ? 'point' : (k.talking() ? 'talk' : 'stand'), hostAt: [460, 600], hostScale: 0.55, hostX: 150};
    },

    line: (k, T) => {
      k.room('workshop');
      // the copyable artifact: a three-line note, held big (the host steps back, small, so nothing covers it)
      k.ctx.save(); slideIn(k, k.S('line'), 0, 800);
      k.panel2(60, 300, 860, 620, {fill: CHALK, border: DARK, title: 'Your price note (example)'});
      k.ctx.restore();
      let cur = -1; LETTER.forEach(([id], i) => { if (T >= k.S(id)) cur = i; });
      if (cur < 0 && T >= k.S('line') + 0.4) {
        k.ctx.save(); slideIn(k, k.S('line') + 0.4, 0, 100);
        k.text('Three lines.', 490, 520, {size: 60, color: DARK, align: 'center'});
        k.text('Copy them.', 490, 610, {size: 60, color: '#7A3442', align: 'center'});
        k.ctx.restore();
      }
      LETTER.forEach(([id, lines], i) => {
        const t0 = k.S(id); if (T < t0) return;
        const y = [340, 498, 656][i];
        k.ctx.save(); popAt(k, t0, 490, y + 50, 1.06);
        if (i === 2) k.shape(k.rectPts(84, y - 12, 812, 214, 0), {fill: CHALK2, line: false});
        lines.forEach((ln, j) => k.text(ln, 108, y + j * 64, {size: 60, color: DARK}));
        if (i < 2) k.shape(k.rectPts(84, y + 138, 812, 6, 0), {fill: GREY, line: false});
        k.ctx.restore();
        k.burst(860, y + 30, t0 + 0.05, {n: 12, r: 160});
      });
      return {hostPose: k.talking() ? 'talk' : 'stand', hostScale: 0.55, hostX: 150};
    },

    stock: (k, T) => {
      const n = k.data.numbers, t0 = k.S('stock');
      k.room('garage');
      // the note's last line rides at the top, on a dark band, so what is discussed stays in view
      k.shape(k.rectPts(72, 262, 840, 136, 0), {fill: INK, line: false});
      k.ctx.save(); slideIn(k, t0, 0, -200);
      k.text("Anything you've already approved", 96, 280, {size: 39, color: CHALK2});
      k.text('stays at the price we quoted.', 96, 326, {size: 39, color: CHALK2});
      k.ctx.restore();
      k.sweep(96, 374, 600, 8, t0 + 0.4, {color: 'accent'});
      k.ctx.save(); slideIn(k, t0 + 0.3, 0, 700);
      k.panel2(60, 450, 870, 500, {title: 'Question 10'});
      k.text('A grocery store', 96, 486, {size: 39, color: CHALK});
      verdict(k, 96, 780, 'Unfair', n.stockUnfair, n.stockN.shown, k.S('stock.79'), RED);
      k.ctx.restore();
      const tsh = k.S('stock.shelf'), tr = k.S('stock.rise');
      if (T >= tsh) {   // the shelf: jars bought before the cost went up
        k.ctx.save(); slideIn(k, tsh, -600, 0);
        for (let i = 0; i < 4; i++) jar(k, 110 + i * 104, 570, tr + 0.4 + i * 0.12);
        k.shape(k.rectPts(90, 666, 440, 14, 0), {fill: '#8C5A33', line: false});
        k.text('Already on the shelf', 96, 690, {size: 30, color: 'muted'});
        k.ctx.restore();
      }
      const tk = k.S('stock.keep');
      if (T >= tr && T < tk) {
        k.arrow([575, 680], [575, 560], k.lin(tr, tr + 0.35), {color: RED, lw: 9});
        k.ctx.save(); slideIn(k, tr + 0.1, 400, 0);
        k.text('Wholesale', 610, 560, {size: 39, color: CHALK});
        k.text('price up', 610, 604, {size: 39, color: CHALK});
        k.ctx.restore();
      }
      if (T >= tk) {   // the rule, stamped beside the shelf (never over the bar or the quoted line)
        k.stampIn(tk, () => {
          k.panel2(570, 540, 336, 150, {fill: 'accent', border: INK});
          k.text('Approved jobs', 738, 562, {size: 39, color: INK, align: 'center'});
          k.text('keep your', 738, 604, {size: 39, color: INK, align: 'center'});
          k.text('quoted price.', 738, 646, {size: 39, color: INK, align: 'center'});
        }, {at: [738, 690]});
        k.burst(738, 615, tk + 0.05, {n: 18});
      }
      return {hostPose: k.live('stock.keep') ? 'point' : (k.talking() ? 'talk' : 'stand'), hostAt: [700, 720], hostScale: 0.55, hostX: 150};
    },

    caveat: (k, T) => {
      const n = k.data.numbers, t0 = k.S('caveat');
      k.room('blackboard'); boardClip(k);
      k.shape(k.rectPts(72, 262, 840, 104, 0), {fill: INK, line: false});
      k.slam('The fine print', 96, 282, t0 + 0.1, {size: 60, color: 'accent', from: 0.8, shake: 6});
      const tp = k.S('caveat.phone');
      if (T >= tp) {
        k.ctx.save(); slideIn(k, tp, -600, 0);
        k.shape(k.rectPts(96, 410, 84, 150, 0), {fill: '#120D14', line: false});
        k.shape(k.rectPts(106, 430, 64, 100, 0), {fill: '#5B8FB9', line: false});
        k.shape(k.rectPts(126, 540, 24, 8, 0), {fill: GREY, line: false});
        k.text('Phone survey:', 214, 410, {size: 60, color: CHALK});
        k.text('Toronto and Vancouver', 214, 486, {size: 39, color: CHALK});
        k.ctx.restore();
      }
      const ty = wordT(k, 'caveat.years', /^nineteen/i);
      if (T >= ty) k.slam(`${n.fieldStart.shown} to ${n.fieldEnd.shown}`, 214, 536, ty, {size: 39, color: CHALK2, from: 0.6});
      const tf = k.S('caveat.fair');
      if (T >= tf) {
        k.ctx.save(); slideIn(k, tf, 600, 0);
        k.shape([[100, 660], [116, 676], [146, 640]], {stroke: TEAL, lw: 9, closed: false, line: false});
        k.text('Measured: what people called fair', 170, 640, {size: 39, color: CHALK});
        k.ctx.restore();
        k.ctx.save(); slideIn(k, tf + 0.5, 600, 0);
        k.shape([[102, 726], [140, 764]], {stroke: RED, lw: 9, closed: false, line: false});
        k.shape([[140, 726], [102, 764]], {stroke: RED, lw: 9, closed: false, line: false});
        k.text('Not measured: what they bought', 170, 726, {size: 39, color: CHALK});
        k.ctx.restore();
      }
      const tq = k.S('caveat.promise');
      if (T >= tq) {
        k.stampIn(tq, () => {
          k.panel2(72, 830, 840, 110, {fill: INK, border: 'accent'});
          k.text('No promise you keep every customer.', 108, 862, {size: 39, color: 'accent'});
        }, {at: [492, 940]});
      }
      k.ctx.restore();
      return {hostPose: k.live('caveat.fair') ? 'clip' : (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150};
    },

    close: (k, T) => {
      k.room('framing');
      k.shape(k.rectPts(60, 272, 960, 400, 0), {fill: INK, line: false});
      const t1 = k.S('close'), tr = wordT(k, 'close', /^say/i, 1.2), t2 = k.S('close.luck'), tn = wordT(k, 'close.luck', /^isn/i, 0.8);
      // centered, so the board reads as one card; the send line is a full-width box, the biggest call on screen
      k.slam('Your costs:', 540, 290, t1, {size: 120, color: TEAL, from: 0.7, align: 'center'});
      k.slam('a reason.', 540, 404, tr, {size: 60, color: TEAL, from: 0.7, align: 'center'});
      k.burst(540, 340, t1 + 0.1, {n: 12, r: 160, colors: [TEAL, 'paper']});
      if (T >= t2) {
        k.slam('Their bad luck:', 540, 480, t2, {size: 120, color: RED, from: 0.7, align: 'center'});
        k.slam('not a reason.', 540, 594, tn, {size: 60, color: RED, from: 0.7, align: 'center'});
        k.burst(540, 530, t2 + 0.1, {n: 16, r: 200, colors: [RED, 'accent2', 'paper']});
      }
      if (T >= k.S('close.send')) {
        const t0 = k.S('close.send');
        k.ctx.save(); popAt(k, t0 - 0.2, 540, 718);
        k.panel2(340, 680, 400, 80, {fill: '#24453A', border: 'accent'}); k.text('ProofNotFluff', 540, 690, {size: 60, color: 'accent', align: 'center'});
        k.ctx.restore();
        k.burst(540, 720, t0 - 0.1, {n: 16});
        k.ctx.save(); slideIn(k, t0 + 0.2, 0, 200);
        k.panel2(84, 776, 900, 136, {fill: INK, border: 'accent'});
        k.text('Send this to whoever', 534, 788, {size: 60, color: CHALK, align: 'center'});
        k.text('sets your prices.', 534, 846, {size: 60, color: CHALK2, align: 'center'});
        k.ctx.restore();
      }
      if (T >= k.S('close.raise')) {   // the send line underlined as the last words echo the hook
        const t0 = k.S('close.raise'), w = k.measure('sets your prices.', {size: 60});
        k.sweep(534 - w / 2, 900, w, 6, t0, {color: 'accent'});
        k.burst(534 + w / 2, 902, t0 + 0.3, {n: 16});
      }
      return {hostPose: T >= k.S('close.send') + 1.5 ? 'wave' : 'talk', hostScale: 0.55, hostX: 150};
    },
  },
};
