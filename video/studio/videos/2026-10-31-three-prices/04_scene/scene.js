// Scene: Three prices on every quote (Lesson 4, Quote Clinic, arcade). One function per top-level cue in 03_cues/cues.md.
// Numbers only from k.data (brief.md -> data.js). Rooms: framing, workshop, blackboard, workshop, garage, blackboard.
// Modeled on lesson 1: a hook card settled on frame 0, slams, sparks, the zoom ladder, blinds between rooms.
const CHALK = '#FFF7EA', CHALK2 = '#F7C873', INK = '#1B1420', DARK = '#2B2033', GREY = '#9AA0AD', RED = '#E2633B', HOOK_END = 3.2;
const TIERS = [
  ['card.good', 'Good', '$', 'The job done right.', 'Nothing extra.'],
  ['card.better', 'Better', '$$', "What you'd pick for", 'your own house.'],
  ['card.best', 'Best', '$$$', 'Plus upgrades: longer', 'warranty, faster start date.'],
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
// a bar that grows from t0 to its value, with the value counting up at its end (values from the brief)
const growBar = (k, x, y, w, h, num, t0, color, o = {}) => {
  k.shape(k.rectPts(x, y, w, h, 0), {fill: '#2B2033', line: false});
  k.shape(k.rectPts(x, y, w, h, 0), {stroke: o.track || CHALK, lw: 6, line: false});
  if (k.T < t0) return;
  const p = k.easeOut((k.T - t0) / 0.8);
  k.shape(k.rectPts(x, y, w * (num.value / 100) * p, h, 0), {fill: color, line: false});
  k.slam(k.count(num.value, 0.85 + 0.15 * k.lin(t0, t0 + 0.8), {suffix: '%'}), x + w + 24, y + h / 2 - 33, t0, {size: 60, color, from: 0.5});
  if (p >= 0.99 && o.sparks !== false) k.burst(x + w * (num.value / 100), y + h / 2, t0 + 0.8, {n: 16, r: 200});
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 4',
  focus: {'stakes.top57': [400, 620], 'stakes.rest': [400, 720], 'menu.lift': [480, 640], 'menu.five': [520, 760],
          'card.best': [500, 640], 'survey.many': [400, 700], 'survey.caveat': [500, 420], 'close.send': [600, 860]},
  sections: {
    hook: (k, T) => {
      const n = k.data.numbers;
      if (T < HOOK_END) {   // the hook card: settled on frame 0, no host, no dialog (nothing covers the claim or its source)
        k.room('framing');
        k.shape(k.rectPts(0, 230, 1080, 860, 0), {fill: INK, line: false});
        k.slam('Top shops quote', 540, 290, -1, {size: 120, color: CHALK, align: 'center'});
        k.slam(`${n.tiers.shown} prices.`, 540, 440, -1, {size: 200, color: 'accent', align: 'center'});
        k.slam(`on ${n.topGbb.shown}`, 540, 676, -1, {size: 120, color: CHALK, align: 'center'});
        k.slam('of home jobs.', 540, 800, -1, {size: 60, color: CHALK, align: 'center'});
        k.burst(540, 540, 0.1, {n: 26, r: 380});
        k.burst(540, 540, 1.4, {n: 14, r: 300, colors: ['accent2', 'paper']});
        k.sweep(300, 880, 480, 10, 0.6, {color: 'accent'});
        k.text(`ServiceTitan data, ${n.stMonths.shown} months to Jan ${n.stYear.shown}`, 540, 920, {size: 39, color: '#E6D3BC', align: 'center'});
        k.text('Quote Clinic', 540, 990, {size: 39, color: CHALK2, align: 'center'});
        return {host: false, speech: false};
      }
      k.room('framing');
      k.ctx.save(); slideIn(k, HOOK_END, -500, 0); k.chip('Quote Clinic', 96, 280, {size: 30}); k.ctx.restore();
      // the quote most shops send: one price
      k.ctx.save(); slideIn(k, HOOK_END + 0.1, -600, 0);
      k.panel2(96, 380, 400, 420, {fill: CHALK, border: DARK, title: `${n.single.shown} price`});
      k.text('Quote', 132, 418, {size: 60, color: DARK});
      for (let i = 0; i < 4; i++) k.shape(k.rectPts(132, 512 + i * 44, i === 3 ? 180 : 320, 14, 0), {fill: GREY, line: false});
      k.text('Total: $', 132, 712, {size: 60, color: DARK});
      k.ctx.restore();
      const tx = k.S('hook.build');
      if (T >= tx) {   // the one-price quote gets crossed out
        k.ctx.save(); popAt(k, tx, 296, 590, 1.1);
        k.shape([[120, 410], [150, 400], [470, 760], [440, 790]], {fill: RED, line: false});
        k.shape([[440, 400], [470, 410], [150, 790], [120, 760]], {fill: RED, line: false});
        k.ctx.restore();
        k.burst(296, 590, tx + 0.05, {n: 20, r: 260, colors: [RED, 'accent2', 'paper']});
      }
      // three prices slide in beside it
      const t3 = tx + 0.35;
      if (T >= t3) {
        k.ctx.save(); slideIn(k, t3, 600, 0);
        k.panel2(560, 380, 370, 420, {title: `${n.tiers.shown} prices`});
        k.ctx.restore();
        TIERS.forEach(([, name, price], i) => {
          const t0 = t3 + 0.2 + i * 0.18; if (T < t0) return;
          k.ctx.save(); slideIn(k, t0, 0, 80);
          k.text(name, 596, 430 + i * 120, {size: 60, color: i === 1 ? 'accent' : CHALK});
          k.text(price, 900, 430 + i * 120, {size: 60, color: i === 1 ? 'accent' : CHALK2, align: 'right'});
          k.ctx.restore();
        });
        k.burst(745, 590, t3 + 0.6, {n: 12, r: 200, colors: ['accent2', 'paper']});
      }
      return {hostPose: T >= tx ? 'point' : (k.talking() ? 'talk' : 'stand'), hostAt: [560, 560]};
    },

    stakes: (k, T) => {
      const n = k.data.numbers;
      k.room('workshop');
      k.ctx.save(); slideIn(k, k.S('stakes'), 0, 700);
      k.panel2(60, 300, 870, 480, {title: 'ServiceTitan'});
      k.text('Share of home jobs quoted', 96, 336, {size: 39, color: CHALK});
      k.slam('good, better, best', 96, 384, k.S('stakes') + 0.4, {size: 60, color: CHALK2, from: 0.5});
      k.ctx.restore();
      if (T >= k.S('stakes.window')) {
        k.ctx.save(); slideIn(k, k.S('stakes.window'), 500, 0);
        k.text(`${n.stMonths.shown} months to Jan ${n.stYear.shown}`, 96, 466, {size: 39, color: 'muted'});
        k.ctx.restore();
      }
      if (T >= k.S('stakes') + 0.3) {
        const t1 = wordT(k, 'stakes.top57', /^fifty/i), t2 = wordT(k, 'stakes.rest', /^forty/i);
        k.ctx.save(); slideIn(k, k.S('stakes') + 0.3, -500, 0);
        if (T >= k.S('stakes.top')) k.slam(`Top ${n.topPct.shown} by revenue`, 96, 520, k.S('stakes.top'), {size: 39, color: 'accent', from: 0.5});
        else k.text('Top shops', 96, 520, {size: 39, color: 'muted'});
        growBar(k, 96, 566, 600, 52, n.topGbb, t1, 'accent');
        k.text('Everyone else', 96, 640, {size: 39, color: T >= k.S('stakes.rest') ? CHALK : 'muted'});
        growBar(k, 96, 686, 600, 52, n.restGbb, t2, '#C9CCD3', {sparks: false});
        k.ctx.restore();
        if (k.live('stakes.top')) k.sweep(96, 562, 600, 4, k.S('stakes.top') + 0.2, {color: 'accent'});
      }
      if (T >= k.S('stakes.habit')) {   // a sticker on the panel's corner, clear of every number
        const t0 = k.S('stakes.habit');
        k.ctx.save(); k.ctx.translate(770, 420); k.ctx.rotate(-0.04); k.ctx.translate(-770, -420); popAt(k, t0, 770, 420);
        k.panel2(630, 372, 280, 96, {fill: 'accent', border: INK});
        k.text('A habit', 770, 382, {size: 39, color: INK, align: 'center'});
        k.text('you can copy.', 770, 420, {size: 39, color: INK, align: 'center'});
        k.ctx.restore();
        k.burst(770, 420, t0 + 0.05, {n: 18});
      }
      return {hostPose: k.live('stakes.habit') ? 'point' : (k.talking() ? 'talk' : 'stand'), hostAt: [560, 500]};
    },

    menu: (k, T) => {
      const n = k.data.numbers;
      k.room('blackboard'); boardClip(k);
      k.slam('Why the middle gains', 96, 280, k.S('menu'), {size: 60, color: CHALK2, from: 0.5});
      if (T >= k.S('menu.study')) {
        const t0 = k.S('menu.study');
        k.ctx.save(); slideIn(k, t0, -600, 0);
        k.text('A restaurant in Germany:', 96, 360, {size: 39, color: CHALK});
        k.text(`${n.menuYears.shown} years of orders`, 96, 404, {size: 39, color: CHALK});
        k.ctx.restore();
        k.ctx.save(); slideIn(k, t0 + 0.3, -600, 0);
        k.text('Journal of Economic Behavior', 96, 450, {size: 30, color: '#D8D0C0'});
        k.text(`and Organization, ${n.menuYear.shown}`, 96, 486, {size: 30, color: '#D8D0C0'});
        k.ctx.restore();
      }
      if (T >= k.S('menu.german')) {   // the size of the data counts up beside the years
        const t0 = k.S('menu.german'), p = k.lin(t0, t0 + 1.0);
        const x0 = 96 + k.measure(`${n.menuYears.shown} years of orders`, {size: 39}) + 30;
        k.slam(`${k.count(n.menuChoices.value, p, {comma: true})}+ choices`, x0, 404, t0, {size: 39, color: CHALK2, from: 0.4});
      }
      if (T < k.S('menu.dishes')) {   // a menu, chalked in while the voice asks why (the board is never empty)
        const t0 = k.S('menu') + 0.4, q = k.clamp(k.pop(t0, 0.4), 0, 1.1);
        k.ctx.save(); k.ctx.translate(540, 730); k.ctx.rotate(0.03); k.ctx.scale(1.4 * q, 1.4 * q);
        k.shape(k.rectPts(-130, -150, 260, 300, 0), {fill: CHALK, line: false});
        k.shape(k.rectPts(-130, -150, 260, 60, 0), {fill: '#7A3442', line: false});
        k.text('Menu', 0, -140, {size: 39, color: CHALK, align: 'center', lint: false});
        for (let i = 0; i < 3; i++) {
          k.shape(k.rectPts(-100, -60 + i * 66, 120, 12, 0), {fill: GREY, line: false});
          k.shape(k.rectPts(54, -60 + i * 66, 16 + i * 14, 12, 0), {fill: '#D9A066', line: false});
        }
        k.ctx.restore();
        k.burst(540, 730, t0 + 0.05, {n: 14, colors: ['paper', 'accent2']});
      }
      // the menu: three dishes, cheap to pricey; the middle one lifts
      if (T >= k.S('menu.dishes')) {
        const t0 = k.S('menu.dishes'), tl = k.S('menu.lift');
        [[230, '$'], [520, '$$'], [810, '$$$']].forEach(([cx, price], i) => {
          const ti = t0 + i * 0.15; if (T < ti) return;
          const lift = i === 1 ? -18 * k.easeOut((T - tl) / 0.5) : 0;
          k.ctx.save(); k.ctx.translate(0, lift); popAt(k, ti, cx, 660, 1.1);
          const hot = i === 1 && T >= tl, top = i === 2 && T >= k.S('menu.pricey');
          if (hot) k.shape(k.ellPts(cx, 684, 146, 80, 24), {fill: '#2F5A4A', line: false});
          k.text(price, cx, 556, {size: 60, color: hot ? 'accent' : (top ? CHALK2 : CHALK), align: 'center'});
          k.shape(k.ellPts(cx, 684, 116, 48, 24), {fill: CHALK, line: false});
          k.shape(k.ellPts(cx, 678, 80, 30, 20), {fill: hot ? 'accent' : (i === 2 ? RED : '#D9A066'), line: false});
          k.ctx.restore();
        });
        if (T >= tl) k.burst(520, 650, tl + 0.3, {n: 18, r: 220});
      }
      if (T >= k.S('menu.five')) {
        const t0 = wordT(k, 'menu.five', /^five/i);
        if (T >= t0) {
          k.slam(`+${n.menuGain.shown} pts share`, 260, 760, t0, {size: 60, color: 'accent', from: 0.8});
          k.ctx.save(); slideIn(k, t0 + 0.3, 300, 0); k.text('on average', 580, 782, {size: 39, color: CHALK2}); k.ctx.restore();
          k.burst(400, 790, t0 + 0.1, {n: 16});
        }
      }
      if (T >= k.S('menu.pricey')) {   // the pricey dish is the new one: the lift was bigger then
        const t0 = k.S('menu.pricey');
        k.ctx.save(); popAt(k, t0, 840, 500); k.chip('New', 790, 486, {size: 30, fill: 'accent', color: INK}); k.ctx.restore();
        if (T < k.S('menu.above')) {
          k.ctx.save(); slideIn(k, t0 + 0.2, 700, 0);
          k.text('Bigger when the pricey dish was new.', 540, 850, {size: 39, color: CHALK2, align: 'center'});
          k.ctx.restore();
        }
      }
      if (T >= k.S('menu.above')) {
        const t0 = k.S('menu.above');
        k.arrow([700, 600], [630, 600], k.lin(t0, t0 + 0.4), {color: 'accent', lw: 9});
        k.slam('Put a price above your middle.', 540, 850, t0 + 0.2, {size: 39, color: 'accent', align: 'center', from: 0.4});
        k.sweep(270, 898, 540, 8, t0 + 0.5, {color: 'accent'});
      }
      k.ctx.restore();
      return {hostPose: k.live('menu.lift') || k.live('menu.five') ? 'point' : (k.talking() ? 'talk' : 'stand'), hostAt: [400, 700], hostScale: 0.55, hostX: 150};
    },

    card: (k, T) => {
      k.room('workshop');
      // the copyable artifact: a three-row quote card, held big (the host steps back, small, so nothing covers it)
      k.ctx.save(); slideIn(k, k.S('card'), 0, 800);
      k.panel2(60, 300, 860, 580, {fill: CHALK, border: DARK, title: 'Your quote (example)'});
      k.ctx.restore();
      let cur = -1; TIERS.forEach(([id], i) => { if (T >= k.S(id)) cur = i; });
      if (cur < 0 && T >= k.S('card') + 0.4) {
        k.ctx.save(); slideIn(k, k.S('card') + 0.4, 0, 100);
        k.text('Good. Better. Best.', 490, 520, {size: 60, color: DARK, align: 'center'});
        k.text('Three prices, one quote.', 490, 610, {size: 39, color: '#6B7080', align: 'center'});
        k.ctx.restore();
      }
      TIERS.forEach(([id, name, price, d1, d2], i) => {
        const t0 = k.S(id); if (T < t0) return;
        const y = 336 + i * 178;
        k.ctx.save(); popAt(k, t0, 490, y + 80, 1.08);
        if (i === 1) k.shape(k.rectPts(84, y - 10, 812, 176, 0), {fill: '#F7C873', line: false});
        k.text(name, 100, y + 4, {size: 60, color: DARK});
        k.text(price, 880, y + 4, {size: 60, color: i === 1 ? '#7A3442' : DARK, align: 'right'});
        k.text(d1, 100, y + 80, {size: 39, color: DARK});
        k.text(d2, 100, y + 120, {size: 39, color: DARK});
        if (i < 2) k.shape(k.rectPts(84, y + 168, 812, 6, 0), {fill: GREY, line: false});
        k.ctx.restore();
        if (i === 1) { k.ctx.save(); popAt(k, t0 + 0.4, 640, y + 30); k.chip('The middle', 520, y + 6, {size: 30, fill: 'tag', color: 'tagText'}); k.ctx.restore(); }
        k.burst(200, y + 40, t0 + 0.05, {n: 12, r: 180});
      });
      return {hostPose: k.talking() ? 'talk' : 'stand', hostScale: 0.55, hostX: 150};
    },

    survey: (k, T) => {
      const n = k.data.numbers;
      k.room('garage');
      const ty = k.S('survey.yeses'), ts = k.S('survey.start');
      k.shape(k.rectPts(72, 262, 840, 196, 0), {fill: INK, line: false});   // a dark band: no ruled lines through the header
      if (T < ty) k.slam('One more from the data', 96, 280, k.S('survey') + 0.1, {size: 60, color: 'accent', from: 0.8, shake: 6});
      else if (T < ts) { k.burst(300, 312, ty + 0.4, {n: 18}); k.slam('More choices, more yeses.', 96, 280, ty + 0.3, {size: 60, color: 'accent', from: 0.6}); }
      else { k.burst(420, 330, ts + 0.1, {n: 22, r: 300}); k.slam(`Start with ${n.tiers.shown}.`, 96, 262, ts, {size: 120, color: 'accent', from: 0.6, shake: 6}); }
      const tc = k.S('survey.caveat');
      if (T >= k.S('survey.more') && T < tc) {
        k.ctx.save(); slideIn(k, k.S('survey.more'), -600, 0);
        k.text(`${n.tiers.shown} is not the ceiling.`, 96, 374, {size: 60, color: CHALK});
        k.ctx.restore();
      }
      if (T >= k.S('survey.group')) {
        const t0 = k.S('survey.group');
        k.ctx.save(); slideIn(k, t0, 0, 700);
        k.panel2(72, 530, 840, 370, {title: `ACCA survey, ACHR News ${n.accaYear.shown}`});
        k.text('"Contractor of the Future"', 108, 566, {size: 39, color: CHALK});
        if (T >= k.S('survey.n')) k.slam(`${k.count(n.accaN.value, k.lin(k.S('survey.n'), k.S('survey.n') + 0.8), {comma: true})}+ contractors`, 108, 610, k.S('survey.n'), {size: 39, color: CHALK2, from: 0.4});
        const t1 = wordT(k, 'survey.many', /^fifty/i), t2 = wordT(k, 'survey.few', /^forty/i);
        // both rows show as the panel opens (no empty box); each lights up and fills when it is said
        k.text(`${n.manyOpt.shown}+ options`, 108, 664, {size: 39, color: T >= k.S('survey.many') ? 'accent' : 'muted'});
        growBar(k, 108, 710, 520, 48, n.manyClose, t1, 'accent');
        k.text(`${n.single.shown} to ${n.fewMax.shown} options`, 108, 782, {size: 39, color: T >= k.S('survey.few') ? CHALK : 'muted'});
        growBar(k, 108, 828, 520, 48, n.fewClose, t2, '#C9CCD3', {sparks: false});
        k.ctx.restore();
        if (T >= tc) k.spot(108, 782, 660, 94, tc + 0.3, {color: 'accent', lw: 6, pad: 10});
      }
      if (T >= tc) {   // the caveat stays on screen: the survey can't separate one option from three
        k.ctx.save(); popAt(k, tc, 490, 450, 1.08);
        k.panel2(72, 392, 840, 118, {fill: INK, border: 'accent'});
        k.text(`${n.single.shown} to ${n.fewMax.shown} options: one group here.`, 108, 412, {size: 39, color: CHALK});
        k.ctx.restore();
        const tk = k.S('survey.cant');
        if (T >= tk) k.slam(`It can't show ${n.fewMax.shown} beats ${n.single.shown}.`, 108, 458, tk, {size: 39, color: 'accent', from: 0.6});
      }
      return {hostPose: T >= ty ? 'clip' : (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150};
    },

    close: (k, T) => {
      const n = k.data.numbers;
      k.room('blackboard'); boardClip(k);
      const t1 = k.S('close'), t2 = wordT(k, 'close.choice', /^three/i), ty = wordT(k, 'close', /^yes/i, 0.6), tc = wordT(k, 'close.choice', /^choice/i, 0.5);
      // centered, so the board reads as one card; the send line is a full-width box, the biggest call on screen
      k.slam(`${n.single.shown} price:`, 540, 262, t1, {size: 120, color: CHALK, from: 0.7, align: 'center'});
      k.slam('yes or no.', 540, 372, ty, {size: 120, color: CHALK, from: 0.7, align: 'center'});
      k.burst(540, 320, t1 + 0.1, {n: 10, r: 150, colors: ['paper', '#2F5A4A']});
      if (T >= t2) {
        k.slam(`${n.tiers.shown} prices:`, 540, 502, t2, {size: 120, color: 'accent', from: 0.7, align: 'center'});
        k.slam('a choice.', 540, 612, tc, {size: 120, color: 'accent', from: 0.7, align: 'center'});
        k.burst(540, 560, t2 + 0.1, {n: 16, r: 200});
      }
      if (T >= k.S('close.send')) {
        const t0 = k.S('close.send');
        k.ctx.save(); popAt(k, t0 - 0.2, 540, 790);
        k.panel2(340, 752, 400, 80, {fill: '#24453A', border: 'accent'}); k.text('ProofNotFluff', 540, 762, {size: 60, color: 'accent', align: 'center'});
        k.ctx.restore();
        k.burst(540, 792, t0 - 0.1, {n: 16});
        k.ctx.save(); slideIn(k, t0 + 0.2, 0, 200);
        k.panel2(84, 848, 900, 140, {fill: INK, border: 'accent'});
        k.text('Send this to whoever', 534, 862, {size: 60, color: CHALK, align: 'center'});
        k.text('writes your quotes.', 534, 922, {size: 60, color: CHALK2, align: 'center'});
        k.ctx.restore();
      }
      if (T >= k.S('close.next')) {   // the payoff line underlined as the last words echo the hook
        const t0 = k.S('close.next'), w = k.measure('a choice.', {size: 120});
        k.sweep(540 - w / 2, 732, w, 12, t0, {color: 'accent'});
        k.burst(540 + w / 2, 738, t0 + 0.3, {n: 16});
      }
      k.ctx.restore();
      return {hostPose: T >= k.S('close.send') + 1.5 ? 'wave' : 'talk', hostScale: 0.55, hostX: 150};
    },
  },
};
