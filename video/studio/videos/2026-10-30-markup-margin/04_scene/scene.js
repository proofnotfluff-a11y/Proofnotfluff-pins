// Scene: Markup vs margin (Lesson 3, Run the Numbers, arcade). One function per top-level cue in 03_cues/cues.md.
// Numbers only from k.data (brief.md -> data.js). Rooms: framing (hook, close), blackboard (the math, the formula),
// workshop (why), garage (double your cost). Modeled on lesson 1 (2026-10-28-first-reply).
const CHALK = '#FFF7EA', CHALK2 = '#F7C873', DARK = '#1B1420', HOOK_END = 3.0;
const D1 = 60, D2 = 120, BODY = 39;   // the arcade font's three heights: display x1, display x2, body
// everything written on the board stays inside the board, even while it slides in
const boardClip = (k) => { k.ctx.save(); k.ctx.beginPath(); k.ctx.rect(60, 246, 960, 752); k.ctx.clip(); };
const slideIn = (k, t0, dx = 0, dy = 0) => { const q = k.easeOut((k.T - t0) / 0.35); k.ctx.translate(dx * 0.4 * (1 - q), dy * 0.4 * (1 - q)); k.ctx.globalAlpha *= k.clamp(q * 1.6); return q; };
// the start of the first spoken word matching re at or after t (falls back to t), so counts land as the number is said
const said = (k, re, t) => { const ws = (window.WORDS && window.WORDS.words) || []; const w = ws.find((x) => x.start >= t - 0.05 && re.test(x.w.toLowerCase())); return w ? w.start : t; };
// a rubber stamp: a dark box with an accent border, scaled down onto the spot (the player shakes on stamp cues)
const stamp = (k, s, cx, cy, t0, o = {}) => {
  if (k.T < t0) return;
  const size = o.size || D1, w = k.measure(s, {size}) + 72, h = (size >= D2 ? 132 : 66) + 44, q = k.clamp((k.T - t0) / 0.18);
  k.ctx.save(); k.ctx.translate(cx, cy); k.ctx.rotate(o.rot != null ? o.rot : -0.06); const sc = 2.2 - 1.2 * q; k.ctx.scale(sc, sc);
  k.shape(k.rectPts(-w / 2, -h / 2, w, h, 0), {fill: DARK, line: false, alpha: q});
  k.shape(k.rectPts(-w / 2 + 6, -h / 2 + 6, w - 12, h - 12, 0), {stroke: 'accent', lw: 9, line: false, alpha: q});
  k.text(s, 0, -h / 2 + 22, {size, color: 'accent', align: 'center', alpha: q, lint: false});
  k.ctx.restore();
  k.burst(cx, cy, t0 + 0.18, {n: 22, r: 300, colors: ['accent', '#9AA0AD', 'paper']});
};
// a bar block that grows upward from its base
const block = (k, x, base, w, h, p, fill) => { if (p <= 0) return; k.shape(k.rectPts(x, base - h * p, w, h * p, 0), {fill, line: false}); };
// the formula card holds big from "Price equals" for at least 3.6 s, and steps up no earlier than "Want forty percent?"
const shrinkAt = (k) => Math.max(k.S('formula.forty'), k.S('formula.eq') + 3.6);
const PX = 0.3, PX2 = 0.25;   // bar height per dollar (cost 1,000 = 300 px); the double-cost bar is drawn smaller so $2,000 fits

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 3',
  focus: {'hook.nope': [600, 600], 'math.margin': [320, 420], 'math.third': [700, 600], 'why.left': [720, 800],
          'double.quote': [730, 420], 'formula.eq': [540, 540], 'formula.forty': [540, 760], 'formula.div': [540, 760],
          'formula.result': [540, 760], 'formula.check': [540, 760], 'close.echo': [600, 860]},
  sections: {
    hook: (k, T) => {
      const n = k.data.numbers;
      k.room('framing');
      if (T < HOOK_END) {   // the hook card: settled on frame one, host and dialog box hidden, so nothing covers the claim
        k.shape(k.rectPts(0, 230, 1080, 840, 0), {fill: DARK, line: false});
        const cw = k.measure('RUN THE NUMBERS', {size: 30}) + 36;
        k.chip('Run the numbers', 540 - cw / 2, 276, {size: 30});
        k.slam(`${n.markupPct.shown} markup`, 540, 380, -1, {size: D2, color: CHALK, align: 'center'});
        k.slam('is NOT', 540, 540, -1, {size: D2, color: 'accent', align: 'center', shake: 6});
        k.slam(`${n.doubleMarginPct.shown} margin`, 540, 700, -1, {size: D2, color: CHALK, align: 'center'});
        k.shape(k.rectPts(540 - 150, 680, 300, 10, 0), {fill: 'accent', line: false});
        k.burst(540, 600, 0.35, {n: 26, r: 380});
        k.text('Example math. Sources: JLC, Xero', 540, 900, {size: BODY, color: '#E6D3BC', align: 'center'});
        return {host: false, speech: false};
      }
      // the quote on the wall: what a 50% markup looks like, and the margin people assume
      k.ctx.save(); slideIn(k, HOOK_END, 600, 0);
      k.panel2(300, 300, 630, 400, {title: 'Your quote'});
      const rows = [['Cost', n.cost.shown], ['Markup', n.markupPct.shown], ['Margin', `${n.doubleMarginPct.shown}?`]];
      rows.forEach(([a, b], i) => {
        k.text(a, 340, 360 + i * 100, {size: D1, color: i === 2 ? 'accent' : CHALK});
        k.text(b, 890, 360 + i * 100, {size: D1, color: i === 2 ? 'accent' : CHALK, align: 'right'});
      });
      k.ctx.restore();
      const tn = k.S('hook.nope');
      if (T >= tn) {   // the assumed 50% is struck out, and the truth is stamped under the card
        const q = k.easeOut((T - tn) / 0.25), sx = 890 - k.measure(`${n.doubleMarginPct.shown}?`, {size: D1}) - 12;
        k.shape(k.rectPts(sx, 588, (890 + 12 - sx) * q, 12, 0), {fill: 'accent', line: false});
        stamp(k, 'One third', 640, 790, tn, {rot: -0.07});
      }
      if (T >= k.S('hook.fix')) {
        const t0 = k.S('hook.fix');
        k.ctx.save(); slideIn(k, t0, 600, 0); k.chip('1  The math', 330, 880, {size: 30, fill: 'accent', color: DARK}); k.ctx.restore();
        k.ctx.save(); slideIn(k, t0 + 0.25, 600, 0); k.chip('2  The fix', 630, 880, {size: 30, fill: 'accent', color: DARK}); k.ctx.restore();
        k.burst(450, 905, t0 + 0.05, {n: 12, r: 180});
      }
      return {hostPose: T >= tn && T < k.S('hook.fix') ? 'shrug' : (k.live('hook') && T < tn ? 'clip' : (k.talking() ? 'talk' : 'stand'))};
    },

    math: (k, T) => {
      const n = k.data.numbers;
      k.room('blackboard'); boardClip(k);
      k.slam('Cost + markup = price', 96, 280, k.S('math'), {size: D1, color: CHALK2, from: 0.5});
      const BX = 640, BW = 180, BASE = 960, HC = n.cost.value * PX, HM = n.markupUsd.value * PX;
      // the empty bar waits for the cost
      k.shape(k.rectPts(BX, BASE - HC, BW, HC, 0), {stroke: '#2F5A4A', lw: 6, line: false});
      k.shape(k.rectPts(BX - 30, BASE, BW + 60, 8, 0), {fill: CHALK, line: false});
      // the cost block, counted as "a thousand" is said
      const tc = said(k, /^thousand/, k.S('math.cost'));
      if (T >= k.S('math.cost')) {
        const p = k.lin(tc, tc + 0.7);
        block(k, BX, BASE, BW, HC, k.easeOut((T - k.S('math.cost')) / 0.5), CHALK);
        k.text('Cost', BX + BW / 2, BASE - HC + 56, {size: BODY, color: DARK, align: 'center', alpha: k.clamp((T - k.S('math.cost')) / 0.4)});
        k.slam(p >= 1 ? n.cost.shown : k.count(n.cost.value, p, {comma: true, prefix: '$'}), 610, 690, tc, {size: D2, color: CHALK, align: 'right', from: 0.6});
        if (p >= 1) k.burst(470, 750, tc + 0.7, {n: 14, colors: ['paper', 'accent2']});
        k.ctx.save(); slideIn(k, tc + 0.3, 300, 0); k.text('cost', 610, 826, {size: BODY, color: CHALK2, align: 'right'}); k.ctx.restore();
      }
      // the markup slice stacks on top; +$500 counts on "five hundred"
      if (T >= k.S('math.markup')) {
        const tm = said(k, /^five$/, k.S('math.markup')), p = k.lin(tm, tm + 0.6);
        block(k, BX, BASE - HC, BW, HM, k.easeOut((T - tm) / 0.5), 'accent');
        k.slam(p >= 1 ? `+${n.markupUsd.shown}` : k.count(n.markupUsd.value, p, {prefix: '+$'}), 610, 512, tm, {size: D1, color: 'accent', align: 'right', from: 0.6});
        k.ctx.save(); slideIn(k, k.S('math.markup'), 300, 0); k.text(`${n.markupPct.shown} markup`, 610, 584, {size: BODY, color: CHALK, align: 'right'}); k.ctx.restore();
        if (p >= 1) k.burst(BX + BW / 2, BASE - HC - HM / 2, tm + 0.6, {n: 12, r: 160});
      }
      // the price lands on top of the bar on "fifteen hundred"
      if (T >= k.S('math.price')) {
        const tp = said(k, /^fifteen/, k.S('math.price')), p = k.lin(tp, tp + 0.7);
        if (T >= tp) {
          k.slam(p >= 1 ? n.price.shown : k.count(n.price.value, p, {comma: true, prefix: '$'}), BX + BW / 2, 424, tp, {size: D1, color: CHALK, align: 'center', from: 0.7});
          k.text('price', BX - 30, 440, {size: BODY, color: CHALK2, align: 'right', alpha: k.clamp((T - tp) / 0.3)});
          k.sweep(BX - 10, 496, BW + 20, 8, tp + 0.4, {color: CHALK2});
          if (p >= 1) k.burst(BX + BW / 2, 460, tp + 0.7, {n: 16});
        }
      }
      // three equal parts: the slice is one of them
      if (T >= k.S('math.third')) {
        const t0 = k.S('math.third'), third = (HC + HM) / n.thirds.value;
        for (let i = 1; i < n.thirds.value; i++) {
          const y = BASE - HC - HM + third * i, q = k.easeOut((T - t0 - i * 0.15) / 0.3);
          if (q > 0) for (let x = BX - 24; x < BX - 24 + (BW + 48) * q; x += 24) k.shape(k.rectPts(x, y - 3, 14, 6, 0), {fill: '#2F5A4A', line: false});
        }
        if ((T - t0) % 0.5 < 0.25 && T - t0 < 1.5) k.shape(k.rectPts(BX - 8, BASE - HC - HM - 8, BW + 16, HM + 16, 0), {stroke: CHALK2, lw: 8, line: false});
        k.ctx.save(); slideIn(k, t0 + 0.2, 300, 0); k.text('one third of the price', 610, 626, {size: BODY, color: 'accent', align: 'right'}); k.ctx.restore();
      }
      // the margin: 33.3% counts on "thirty-three" and slams in
      if (T >= k.S('math.margin')) {
        const tg = said(k, /^thirty/, k.S('math.margin')), p = k.lin(tg, tg + 0.7);
        k.ctx.save(); slideIn(k, k.S('math.margin'), -400, 0); k.text('Your margin:', 96, 364, {size: BODY, color: CHALK2}); k.ctx.restore();
        if (T >= tg) {
          k.slam(p >= 1 ? n.marginPct.shown : k.count(n.marginPct.value, p, {dec: 1, suffix: '%'}), 96, 410, tg, {size: D2, color: 'accent', from: 0.8, shake: 6});
          if (p >= 1) k.burst(230, 470, tg + 0.7, {n: 20});
        }
      }
      if (T >= k.S('math.not')) {
        const t0 = k.S('math.not'), s = `not ${n.markupPct.shown}`, w = k.measure(s, {size: D1});
        k.slam(s, 96, 560, t0, {size: D1, color: CHALK, from: 0.5});
        k.sweep(90, 590, w + 12, 10, t0 + 0.6, {color: 'accent'});
      }
      k.ctx.restore();
      return {hostPose: k.talking() ? 'point' : 'stand', hostAt: [600, 700]};
    },

    why: (k, T) => {
      const n = k.data.numbers;
      k.room('workshop');
      k.slam('Why the gap?', 96, 276, k.S('why'), {size: D1, color: CHALK, from: 0.5});
      const card = (x, title, top, base, on, res, t0) => {
        if (T < t0) return;
        k.ctx.save(); slideIn(k, t0, 0, 600);
        k.panel2(x, 380, 404, 290, {title});
        k.text(`${top} / ${base}`, x + 30, 414, {size: D1, color: CHALK});
        k.text(on, x + 30, 496, {size: BODY, color: 'accent2'});
        k.ctx.restore();
        k.slam(res, x + 30, 540, t0 + 0.5, {size: D2, color: 'accent', from: 0.6});
        k.sweep(x + 28, 540, k.measure(on, {size: BODY}) + 4, 6, t0 + 0.4, {color: 'accent2'});
        k.burst(x + 200, 600, t0 + 0.6, {n: 14, r: 180});
      };
      card(96, 'Markup', n.markupUsd.shown, n.cost.shown, 'on your cost', n.markupPct.shown, k.S('why.markup'));
      card(530, 'Margin', n.markupUsd.shown, n.price.shown, 'on the price', n.marginPct.shown, k.S('why.margin'));
      if (T >= k.S('why.pays') && T < k.S('why.left')) {
        k.ctx.save(); slideIn(k, k.S('why.pays'), 400, 0);
        k.text('the price = what the customer pays you', 530, 712, {size: BODY, color: CHALK, align: 'center'});
        k.ctx.restore();
        k.sweep(250, 752, 560, 8, k.S('why.pays') + 0.3, {color: 'accent'});
      }
      // the stamp holds until the answer replaces it on the same row: what margin has to cover
      if (T < k.S('why.cover')) stamp(k, 'Not take-home pay', 520, 740, k.S('why.left'), {rot: -0.04});
      if (T >= k.S('why.cover')) {
        const t0 = k.S('why.cover');
        k.ctx.save(); slideIn(k, t0, -300, 0); k.text('It covers:', 96, 724, {size: BODY, color: CHALK}); k.ctx.restore();
        k.ctx.save(); slideIn(k, t0 + 0.15, 0, -200); k.chip('Overhead', 290, 712, {size: 30, fill: 'accent', color: DARK}); k.ctx.restore();
        k.burst(410, 738, t0 + 0.2, {n: 10, r: 140});
      }
      if (T >= k.S('why.pay')) {
        const t0 = k.S('why.pay');
        k.ctx.save(); slideIn(k, t0, 0, -200); k.chip('+ Your pay', 566, 712, {size: 30, fill: 'accent', color: DARK}); k.ctx.restore();
        k.burst(680, 738, t0 + 0.05, {n: 10, r: 140});
      }
      return {hostPose: T >= k.S('why.left') && T < k.S('why.cover') ? 'shrug' : (k.talking() ? 'talk' : 'stand')};
    },

    double: (k, T) => {
      const n = k.data.numbers;
      k.room('garage');
      k.slam(`Want a ${n.doubleMarginPct.shown} margin?`, 110, 280, k.S('double'), {size: D1, color: CHALK, from: 0.5});
      const BX = 640, BW = 180, BASE = 960, HC = n.cost.value * PX2, HD = (n.doublePrice.value - n.cost.value) * PX2;
      k.shape(k.rectPts(BX - 30, BASE, BW + 60, 8, 0), {fill: CHALK, line: false});
      k.ctx.save(); slideIn(k, k.S('double') + 0.2, 0, 400);
      block(k, BX, BASE, BW, HC, 1, CHALK);
      k.text('Cost', BX + BW / 2, BASE - 70, {size: BODY, color: DARK, align: 'center'});
      k.text(n.cost.shown, 610, 744, {size: D1, color: CHALK, align: 'right'});
      k.text('cost', 610, 816, {size: BODY, color: CHALK2, align: 'right'});
      k.ctx.restore();
      // DOUBLE: a second cost-sized block stacks on top; the stamp holds until the markup is named
      const tx = k.S('double.x2'), td = said(k, /^double/, tx);
      if (T >= tx) {
        if (T < k.S('double.markup')) stamp(k, 'Double your cost', 330, 520, td, {rot: -0.05});
        block(k, BX, BASE - HC, BW, HD, k.easeOut((T - td) / 0.5), 'accent');
      }
      // 100% counts up as it is said
      if (T >= k.S('double.markup')) {
        const t0 = said(k, /^hundred/, k.S('double.markup')), p = k.lin(t0, t0 + 0.7);
        if (T >= t0) {
          k.slam(p >= 1 ? n.doubleMarkupPct.shown : k.count(n.doubleMarkupPct.value, p, {suffix: '%'}), 610, 500, t0, {size: D2, color: 'accent', align: 'right', from: 0.6});
          k.text('markup', 610, 640, {size: BODY, color: CHALK, align: 'right', alpha: k.clamp((T - t0) / 0.3)});
          if (p >= 1) k.burst(460, 560, t0 + 0.7, {n: 14});
        }
      }
      // two thousand on the quote; the top block is half of it
      if (T >= k.S('double.quote')) {
        const t0 = said(k, /^thousand/, k.S('double.quote'));
        k.slam(n.doublePrice.shown, BX + BW / 2, 384, t0, {size: D1, color: CHALK, align: 'center', from: 0.7});
        k.text('on the quote', 610, 400, {size: BODY, color: CHALK2, align: 'right', alpha: k.clamp((T - t0) / 0.3)});
        k.slam(n.doubleMarginPct.shown, BX + BW / 2, BASE - HC - HD / 2 - 60, t0 + 0.4, {size: D1, color: DARK, align: 'center', from: 0.6});
        k.text('margin', BX + BW / 2, BASE - HC - HD / 2 + 14, {size: BODY, color: DARK, align: 'center', alpha: k.clamp((T - t0 - 0.4) / 0.3)});
        k.burst(BX + BW / 2, 420, t0 + 0.1, {n: 18});
      }
      return {hostPose: k.talking() ? 'point' : 'stand', hostAt: [600, 600]};
    },

    formula: (k, T) => {
      const n = k.data.numbers;
      k.room('blackboard'); boardClip(k);
      const shot = T >= k.S('formula.shot');
      k.ctx.save(); slideIn(k, shot ? k.S('formula.shot') : k.S('formula'), -400, 0);
      k.chip(shot ? 'Screenshot this' : 'The part people skip', 96, 270, {size: 30, fill: shot ? 'accent' : 'tag', color: shot ? DARK : 'tagText'});
      k.ctx.restore();
      if (shot) {
        // the formula card: big from "Price equals" until "Want forty percent?", then it steps up to half size (still the
        // same pixel grid) and stays on the board while the worked example is written under it
        const t0 = k.S('formula.shot'), q = k.clamp(k.pop(t0, 0.35), 0, 1.12), tf = shrinkAt(k);
        const sm = 1 - 0.5 * k.easeOut((T - tf) / 0.35), CX = 510, CY = 350;
        k.ctx.save(); k.ctx.translate(CX, CY); k.ctx.scale(q * sm, q * sm); k.ctx.translate(-CX, -CY);
        // the literal line rides on the card's tab while the card is big (the copyable text, same as every caption)
        k.panel2(130, CY, 760, 470, sm > 0.9 ? {border: 'accent', title: 'Price = Cost / (1 - margin)'} : {border: 'accent'});
        const te = k.S('formula.eq');
        if (T >= te) {   // written in under a second as "Price equals" starts, so the whole formula holds big for seconds
          const num = 'Cost', den = '1 - margin', fw = Math.max(k.measure(num, {size: D2}), k.measure(den, {size: D2}));
          const a = (t) => k.clamp((T - t) / 0.2);
          k.text('Price =', CX, CY + 40, {size: D2, color: CHALK, align: 'center', alpha: a(te)});
          k.text(num, CX, CY + 182, {size: D2, color: CHALK, align: 'center', alpha: a(te + 0.25)});
          k.sweep(CX - fw / 2 - 10, CY + 322, fw + 20, 12, te + 0.45, {color: CHALK2});
          k.text(den, CX, CY + 344, {size: D2, color: 'accent', align: 'center', alpha: a(te + 0.6)});
          k.burst(CX, CY + 328, te + 0.55, {n: 14, r: 220, colors: ['paper', 'accent2']});
          const dw = k.measure(den, {size: D2});   // a chalk ring around the part people get wrong, as it is said
          if (T >= k.S('formula.minus')) k.spot(CX - dw / 2, CY + 356, dw, 100, k.S('formula.minus'), {pad: 8, r: 0, color: 'accent2', lw: 6});
        }
        k.ctx.restore();
      }
      // the worked example under the card, once the card has stepped up
      const tf = shrinkAt(k);
      if (T >= tf + 0.2) {
        const s = `${n.targetMarginPct.shown} margin:`, tdv = Math.max(k.S('formula.div'), tf + 0.5);
        k.slam(s, 120, 620, tf + 0.2, {size: D1, color: CHALK2, from: 0.5});
        if (T >= tdv) k.slam(`${n.cost.shown} / ${n.divisor.shown}`, 120 + k.measure(s, {size: D1}) + 36, 620, tdv, {size: D1, color: CHALK, from: 0.5});
      }
      if (T >= k.S('formula.result')) {
        const tr = said(k, /^sixteen/, k.S('formula.result')), p = k.lin(tr, tr + 0.9);
        if (T >= tr) {
          k.slam('= ' + (p >= 1 ? n.targetPrice.shown : k.count(n.targetPrice.value, p, {from: n.cost.value, dec: 2, comma: true, prefix: '$'})), 320, 700, tr, {size: D2, color: 'accent', from: 0.6});
          if (p >= 1) k.burst(560, 760, tr + 0.9, {n: 22, r: 300});
        }
      }
      if (T >= k.S('formula.check')) {
        const t0 = k.S('formula.check');
        k.ctx.save(); slideIn(k, t0, 400, 0);
        k.text(`${n.targetMarginUsd.shown} / ${n.targetPrice.shown} = ${n.targetCheck.shown}`, 320, 852, {size: BODY, color: CHALK});
        k.ctx.restore();
      }
      k.ctx.restore();
      return {hostPose: k.talking() ? (T < k.S('formula.result') ? 'point' : 'talk') : 'stand', hostAt: [500, 700], hostScale: 0.7};   // a smaller host keeps clear of the card
    },

    close: (k, T) => {
      k.room('framing');
      const t0 = k.S('close');
      k.ctx.save(); slideIn(k, t0, 0, 500); k.panel2(84, 290, 852, 190, {fill: DARK, border: 'accent'}); k.ctx.restore();
      const tg = said(k, /^margin/, t0 + 0.5);
      k.slam('Markup is on cost.', 510, 312, t0 + 0.1, {size: D1, color: CHALK, align: 'center', from: 0.7});
      k.slam('Margin is on price.', 510, 394, tg, {size: D1, color: 'accent', align: 'center', from: 0.7});
      k.burst(510, 424, tg + 0.12, {n: 12, r: 200});
      if (T >= k.S('close.send')) {
        const ts = k.S('close.send'), tb = ts - 0.3;
        k.ctx.save(); k.ctx.translate(540, 540); const qb = k.clamp(k.pop(tb, 0.3), 0, 1.15); k.ctx.scale(qb, qb); k.ctx.translate(-540, -540);
        k.panel2(330, 500, 420, 80, {fill: '#24453A', border: 'accent'}); k.text('ProofNotFluff', 540, 507, {size: D1, color: 'accent', align: 'center'});
        k.ctx.restore();
        k.burst(540, 540, tb + 0.1, {n: 16});
        k.ctx.save(); slideIn(k, ts, 700, 0);
        k.panel2(300, 600, 630, 160, {fill: DARK, border: 'accent'});
        k.text('Send this to whoever', 330, 616, {size: D1, color: CHALK});
        k.text('sets your prices.', 330, 684, {size: D1, color: CHALK});
        if (T >= k.S('close.you')) k.sweep(326, 738, k.measure('sets your prices.', {size: D1}) + 8, 8, k.S('close.you'), {color: 'accent2'});
        k.ctx.restore();
      }
      if (T >= k.S('close.last')) {
        const tl = k.S('close.last');
        k.ctx.save(); slideIn(k, tl, 700, 0);
        k.panel2(300, 780, 630, 154, {fill: DARK, border: 'line'});
        k.text('Your last quote?', 330, 794, {size: D1, color: CHALK});
        k.ctx.restore();
        if (T >= k.S('close.echo')) k.slam('Half, or a third?', 330, 860, k.S('close.echo'), {size: D1, color: 'accent', from: 0.6});
      }
      return {hostPose: T >= k.S('close.echo') + 1.2 ? 'wave' : (k.live('close.you') ? 'point' : 'talk'), hostAt: [420, 720]};
    },
  },
};
