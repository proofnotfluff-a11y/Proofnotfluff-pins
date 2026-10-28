// Scene: Know your close rate (Lesson 8, Numbers Clinic, arcade). One function per top-level cue in 03_cues/cues.md.
// Numbers only from k.data (brief.md -> data.js). Rooms: framing, workshop, blackboard, garage, framing, workshop, blackboard.
// Modeled on lesson 4: a hook card settled on frame 0, slams, sparks, the zoom ladder, a room change every section.
const CHALK = '#FFF7EA', CHALK2 = '#F7C873', INK = '#1B1420', DARK = '#2B2033', GREY = '#9AA0AD', LIGHT = '#C9CCD3';
// the hook card holds from frame 0 until "by region" is said (2.5 to 4 s)
const hookEnd = (k) => Math.min(4.0, Math.max(2.5, k.S('hook.region')));
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
// a count-up that starts at 85% of its value and lands exactly on it
const cnt = (k, num, t0, o = {}) => k.count(num.value, 0.85 + 0.15 * k.lin(t0, t0 + 0.7), Object.assign({from: 0}, o));
// a 0 to 100% strip with one lit range (lo to hi); the range opens out from its middle starting at t0 (t0 null: already open)
const strip = (k, x, y, w, h, lo, hi, t0, color) => {
  k.shape(k.rectPts(x, y, w, h, 0), {fill: DARK, line: false});
  k.shape(k.rectPts(x, y, w, h, 0), {stroke: CHALK, lw: 6, line: false});
  for (let i = 1; i < 4; i++) k.shape(k.rectPts(x + (w * i) / 4 - 2, y + 8, 4, h - 16, 0), {fill: '#4A4E5A', line: false});
  if (t0 != null && k.T < t0) return 0;
  const p = t0 == null ? 1 : k.easeOut((k.T - t0) / 0.6);
  const a = x + (w * lo.value) / 100, b = x + (w * hi.value) / 100, m = (a + b) / 2, half = Math.max(4, ((b - a) / 2) * p);
  k.shape(k.rectPts(m - half, y - 6, half * 2, h + 12, 0), {fill: color, line: false});
  return p;
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 8',
  focus: {'hook.yours': [380, 700], 'stakes.top': [520, 560], 'stakes.measure': [580, 820], 'formula.div': [506, 640],
          'example.div': [500, 640], 'example.range': [480, 820], 'turn.yours': [480, 820], 'weekly.away': [480, 860],
          'close.send': [540, 760]},
  sections: {
    hook: (k, T) => {
      const n = k.data.numbers, he = hookEnd(k);
      if (T < he) {   // the hook card: settled on frame 0, no host, no dialog (nothing covers the claim or its source)
        k.room('framing');
        k.shape(k.rectPts(0, 230, 1080, 860, 0), {fill: INK, line: false});
        k.slam('Median close rate,', 540, 300, -1, {size: 60, color: CHALK, align: 'center'});
        k.slam('by region:', 540, 384, -1, {size: 60, color: CHALK, align: 'center'});
        k.slam(`${n.medLow.shown} to`, 540, 476, -1, {size: 120, color: 'accent', align: 'center'});
        k.slam(n.medHigh.shown, 540, 620, -1, {size: 120, color: 'accent', align: 'center'});
        k.burst(540, 600, 0.1, {n: 26, r: 380});
        k.burst(540, 600, 1.4, {n: 14, r: 300, colors: ['accent2', 'paper']});
        k.sweep(300, 770, 480, 10, 0.6, {color: 'accent'});
        k.text(`ServiceTitan customers, May to Jul ${n.stYear.shown}`, 540, 820, {size: 39, color: '#E6D3BC', align: 'center'});
        k.text('Numbers Clinic', 540, 890, {size: 39, color: CHALK2, align: 'center'});
        return {host: false, speech: false};
      }
      k.room('framing');
      k.shape(k.rectPts(60, 250, 900, 430, 0), {fill: INK, line: false});
      // the range strip: the regional medians on a 0 to 100% track
      k.ctx.save(); slideIn(k, he, -600, 0);
      k.text('Median close rate, by region', 96, 280, {size: 39, color: CHALK});
      const x0 = 96, w = 800, ax = (v) => x0 + (w * v) / 100;
      strip(k, x0, 360, w, 56, n.medLow, n.medHigh, he, 'accent');
      k.text('0%', x0, 434, {size: 30, color: GREY});
      k.text('100%', x0 + w, 434, {size: 30, color: GREY, align: 'right'});
      k.ctx.restore();
      if (T >= he + 0.3) {
        k.ctx.save(); slideIn(k, he + 0.3, 0, 60);
        k.text(`Northeast ${n.medLow.shown}`, ax(n.medLow.value) - 10, 476, {size: 39, color: 'accent', align: 'right'});
        k.text(`West ${n.medHigh.shown}`, ax(n.medHigh.value) + 10, 476, {size: 39, color: 'accent'});
        k.ctx.restore();
      }
      if (T >= k.S('hook.source')) {
        const t0 = k.S('hook.source');
        k.ctx.save(); popAt(k, t0, 300, 570); k.chip('ServiceTitan customer accounts', 96, 548, {size: 30}); k.ctx.restore();
      }
      if (T >= k.S('hook.window')) {
        k.ctx.save(); slideIn(k, k.S('hook.window'), 400, 0);
        k.text(`May to Jul ${n.stYear.shown}`, 96, 616, {size: 39, color: CHALK2});
        k.ctx.restore();
      }
      if (T >= k.S('hook.yours')) {   // their own number: a blank that pulses
        const t0 = k.S('hook.yours');
        k.ctx.save(); popAt(k, t0, 500, 760, 1.1);
        k.panel2(300, 690, 600, 150, {fill: CHALK, border: DARK});
        k.text('Your close rate:', 336, 740, {size: 39, color: DARK});
        const pulse = 1 + 0.08 * Math.sin((T - t0) * 6);
        k.ctx.save(); k.ctx.translate(800, 765); k.ctx.scale(pulse, pulse); k.ctx.translate(-800, -765);
        k.text('?%', 800, 706, {size: 120, color: 'accent', align: 'center'});
        k.ctx.restore();
        k.ctx.restore();
        k.burst(800, 760, t0 + 0.05, {n: 16});
      }
      if (T >= k.S('hook.math')) {
        k.ctx.save(); slideIn(k, k.S('hook.math'), 0, 200); k.chip('Numbers Clinic', 300, 870, {size: 30, fill: 'accent', color: INK}); k.ctx.restore();
      }
      return {hostPose: k.live('hook.yours') ? 'point' : (k.live('hook.math') ? 'clip' : (k.talking() ? 'talk' : 'stand')), hostAt: [300, 760], hostScale: 0.55, hostX: 150};
    },

    stakes: (k, T) => {
      const n = k.data.numbers, x0 = 96, w = 700, ax = (v) => x0 + (w * v) / 100;
      k.room('workshop');
      k.ctx.save(); slideIn(k, k.S('stakes'), 0, 700);
      k.panel2(60, 300, 870, 620, {title: `ServiceTitan, May to Jul ${n.stYear.shown}`});
      k.text('Median close rate, each region', 96, 340, {size: 30, color: GREY});
      // both rows show as the panel opens; the top row lights up and fills when it is said
      k.text('Median shop', 96, 392, {size: 39, color: CHALK});
      k.text(`${n.medLow.shown} to ${n.medHigh.shown}`, 894, 392, {size: 39, color: LIGHT, align: 'right'});
      strip(k, x0, 444, w, 48, n.medLow, n.medHigh, null, LIGHT);
      const ranked = T >= k.S('stakes.ranked');
      k.text(ranked ? `Top ${n.topShare.shown} by close rate` : `Top ${n.topShare.shown}`, 96, 532, {size: 39, color: ranked ? 'accent' : GREY});
      const tt = wordT(k, 'stakes.top', /^seventy$/i);
      if (T >= tt) k.slam(`${cnt(k, n.topLow, tt, {suffix: '%'})} to ${cnt(k, n.topHigh, tt, {suffix: '%'})}`, 894, 532, tt, {size: 39, color: 'accent', align: 'right', from: 0.5});
      strip(k, x0, 584, w, 48, n.topLow, n.topHigh, tt, 'accent');
      k.text('0%', x0, 650, {size: 30, color: GREY});
      k.text('100%', x0 + w, 650, {size: 30, color: GREY, align: 'right'});
      k.ctx.restore();
      if (T >= tt + 0.6) k.burst(ax((n.topLow.value + n.topHigh.value) / 2), 608, tt + 0.6, {n: 16, r: 200});
      if (ranked && k.live('stakes.ranked')) k.sweep(96, 576, 700, 4, k.S('stakes.ranked') + 0.2, {color: 'accent'});
      if (T >= k.S('stakes.gap')) {   // the gap: a bracket from the median's top to the top quarter's bottom
        const t0 = k.S('stakes.gap'), a = ax(n.medHigh.value), b = ax(n.topLow.value), q = k.easeOut((T - t0) / 0.4);
        k.shape(k.rectPts(a, 712, (b - a) * q, 8, 0), {fill: 'accent', line: false});
        k.shape(k.rectPts(a, 696, 8, 40, 0), {fill: 'accent', line: false});
        if (q >= 1) k.shape(k.rectPts(b - 8, 696, 8, 40, 0), {fill: 'accent', line: false});
        k.slam('the gap', (a + b) / 2, 740, t0 + 0.3, {size: 39, color: 'accent', align: 'center', from: 0.6});
      }
      if (T >= k.S('stakes.measure')) {   // a sticker under the gap, clear of every number
        const t0 = k.S('stakes.measure');
        k.ctx.save(); k.ctx.translate(560, 840); k.ctx.rotate(-0.03); k.ctx.translate(-560, -840); popAt(k, t0, 560, 840);
        k.panel2(250, 800, 620, 100, {fill: 'accent', border: INK});
        k.text("Can't close a gap", 560, 812, {size: 39, color: INK, align: 'center'});
        k.text('you never measured.', 560, 852, {size: 39, color: INK, align: 'center'});
        k.ctx.restore();
        k.burst(560, 850, t0 + 0.05, {n: 18});
      }
      return {hostPose: k.live('stakes.measure') ? 'point' : (k.talking() ? 'talk' : 'stand'), hostAt: [560, 840], hostScale: 0.55, hostX: 150};
    },

    formula: (k, T) => {
      k.room('blackboard'); boardClip(k);
      k.slam('The math', 96, 280, k.S('formula'), {size: 60, color: CHALK2, from: 0.5});
      if (T >= k.S('formula.shot')) { k.ctx.save(); popAt(k, k.S('formula.shot'), 520, 300); k.chip('Screenshot this', 400, 284, {size: 30, fill: 'accent', color: INK}); k.ctx.restore(); }
      // the copyable artifact: the formula card, held big (the host steps back, small, so nothing covers it)
      if (T >= k.S('formula') + 0.4) {
        k.ctx.save(); slideIn(k, k.S('formula') + 0.4, 0, 600);
        k.panel2(96, 390, 820, 400, {fill: CHALK, border: DARK, title: 'Numbers Clinic'});
        // the formula's slots show as the card opens (no empty card); each fills when it is said
        const tj0 = wordT(k, 'formula.eq', /^jobs$/i), td0 = wordT(k, 'formula.div', /^divided$/i), tg0 = wordT(k, 'formula.div', /^estimates$/i);
        if (T < k.S('formula.eq')) k.text('Close rate =', 506, 430, {size: 60, color: LIGHT, align: 'center'});
        if (T < tj0) k.shape(k.rectPts(376, 580, 260, 10, 0), {fill: LIGHT, line: false});
        if (T < td0) k.shape(k.rectPts(246, 614, 520, 10, 0), {fill: LIGHT, line: false});
        if (T < tg0) k.shape(k.rectPts(326, 700, 360, 10, 0), {fill: LIGHT, line: false});
        k.ctx.restore();
      }
      const te = k.S('formula.eq');
      if (T >= te) {
        k.slam('Close rate =', 506, 430, te, {size: 60, color: DARK, align: 'center', from: 0.5});
        const tj = wordT(k, 'formula.eq', /^jobs$/i);
        if (T >= tj) k.slam('jobs sold', 506, 530, tj, {size: 60, color: '#7A3442', align: 'center', from: 0.6});
      }
      const td = wordT(k, 'formula.div', /^divided$/i);
      if (T >= td) k.shape(k.rectPts(506 - 260 * k.easeOut((T - td) / 0.3), 614, 520 * k.easeOut((T - td) / 0.3), 10, 0), {fill: DARK, line: false});
      const tg = wordT(k, 'formula.div', /^estimates$/i);
      if (T >= tg) { k.slam('estimates given', 506, 650, tg, {size: 60, color: '#7A3442', align: 'center', from: 0.6}); k.burst(506, 680, tg + 0.2, {n: 16, r: 240}); }
      if (T >= k.S('formula.month')) {
        k.slam('Same month for both.', 506, 830, k.S('formula.month'), {size: 60, color: 'accent', align: 'center', stamp: true});
      }
      k.ctx.restore();
      return {hostPose: k.live('formula.shot') ? 'point' : (k.talking() ? 'talk' : 'stand'), hostAt: [400, 300], hostScale: 0.55, hostX: 150};
    },

    example: (k, T) => {
      const n = k.data.numbers;
      k.room('garage');
      k.shape(k.rectPts(72, 262, 840, 104, 0), {fill: INK, line: false});   // a dark band: no ruled lines through the header
      k.slam('Example', 96, 284, k.S('example'), {size: 60, color: 'accent', from: 0.8, shake: 6});
      if (T >= k.S('example.own')) { k.ctx.save(); popAt(k, k.S('example.own'), 640, 310); k.chip('Now yours: __ / __', 440, 290, {size: 30, fill: 'accent', color: INK}); k.ctx.restore(); }
      // the worked example card: all three rows show as it opens, each value lands when it is said
      k.ctx.save(); slideIn(k, k.S('example') + 0.2, 0, 700);
      k.panel2(72, 400, 840, 340, {fill: CHALK, border: DARK});
      const rows = ['Estimates given', 'Jobs sold', 'Close rate'];
      rows.forEach((r, i) => {
        k.text(r, 108, 432 + i * 100, {size: 39, color: DARK});
        if (i < 2) k.shape(k.rectPts(96, 500 + i * 100, 792, 6, 0), {fill: GREY, line: false});
      });
      const t40 = wordT(k, 'example.forty', /^forty$/i), t14 = wordT(k, 'example.forty', /^fourteen/i, 2.5);
      if (T >= t40) k.slam(cnt(k, n.exEst, t40), 876, 420, t40, {size: 60, color: DARK, align: 'right', from: 0.5});
      else k.text('__', 876, 420, {size: 60, color: GREY, align: 'right'});
      if (T >= t14) k.slam(cnt(k, n.exSold, t14), 876, 520, t14, {size: 60, color: DARK, align: 'right', from: 0.5});
      else k.text('__', 876, 520, {size: 60, color: GREY, align: 'right'});
      const tdv = k.S('example.div'), t35 = wordT(k, 'example.div', /^thirty/i, 1.5);
      if (T >= tdv) k.slam(`${n.exSold.shown} / ${n.exEst.shown} =`, 460, 632, tdv, {size: 39, color: '#6B7080', from: 0.5});
      if (T >= t35) k.slam(cnt(k, n.exRate, t35, {suffix: '%'}), 876, 620, t35, {size: 60, color: '#C8502F', align: 'right', from: 0.7});
      else k.text('__', 876, 620, {size: 60, color: GREY, align: 'right'});
      k.ctx.restore();
      if (T >= t35 + 0.7) k.burst(800, 650, t35 + 0.7, {n: 18, r: 220});
      if (T >= k.S('example.range')) {   // where the example sits: inside the regional medians
        const t0 = k.S('example.range'), x0 = 108, w = 700, ax = (v) => x0 + (w * v) / 100;
        k.ctx.save(); slideIn(k, t0, 0, 200);
        k.shape(k.rectPts(72, 768, 840, 160, 0), {fill: INK, line: false});
        strip(k, x0, 800, w, 40, n.medLow, n.medHigh, null, LIGHT);
        k.text(`Inside the ${n.medLow.shown} to ${n.medHigh.shown} medians`, 108, 866, {size: 39, color: CHALK});
        k.ctx.restore();
        const tm = t0 + 0.3, q = k.easeOut((T - tm) / 0.35), mx = ax(n.exRate.value);
        if (T >= tm) {
          k.shape([[mx - 18, 760 + 24 * q], [mx + 18, 760 + 24 * q], [mx, 790 + 24 * q]], {fill: 'accent', line: false});
          k.shape(k.rectPts(mx - 3, 790, 6, 56 * q, 0), {fill: 'accent', line: false});
        }
      }
      return {hostPose: k.live('example.own') ? 'point' : (k.talking() ? 'talk' : 'stand'), hostAt: [500, 300], hostScale: 0.55, hostX: 150};
    },

    turn: (k, T) => {
      k.room('framing');
      k.shape(k.rectPts(72, 262, 840, 104, 0), {fill: INK, line: false});   // the header on a dark band
      k.slam('The part people skip', 96, 280, k.S('turn') + 0.1, {size: 60, color: 'accent', from: 0.8, shake: 6});
      if (T >= k.S('turn.count')) {
        k.ctx.save(); slideIn(k, k.S('turn.count'), -600, 0);
        k.panel2(96, 390, 800, 100, {fill: DARK, border: CHALK});
        k.text('No close rate formula on the page.', 128, 420, {size: 39, color: CHALK});
        k.ctx.restore();
      }
      if (T >= k.S('turn.cust')) {
        k.ctx.save(); slideIn(k, k.S('turn.cust'), 600, 0);
        k.panel2(96, 520, 800, 140, {fill: DARK, border: CHALK});
        k.text('ServiceTitan customers only.', 128, 548, {size: 39, color: CHALK});
        k.text('Not every shop.', 128, 596, {size: 39, color: CHALK2});
        k.ctx.restore();
      }
      if (T >= k.S('turn.own')) {
        k.ctx.save(); slideIn(k, k.S('turn.own'), 0, 200);
        k.panel2(96, 680, 800, 252, {fill: INK, border: 'accent'});
        k.text('First number to beat:', 128, 704, {size: 39, color: CHALK});
        k.ctx.restore();
      }
      if (T >= k.S('turn.yours')) {
        const t0 = k.S('turn.yours');
        k.slam('Your own,', 128, 756, t0, {size: 60, color: 'accent', stamp: true});
        k.slam('last month.', 128, 830, t0 + 0.25, {size: 60, color: 'accent', from: 0.6});
        k.sweep(128, 900, k.measure('last month.', {size: 60}), 8, t0 + 0.6, {color: 'accent'});
        k.burst(300, 800, t0 + 0.1, {n: 20, r: 260});
      }
      return {hostPose: k.live('turn.yours') ? 'point' : (k.talking() ? 'talk' : 'stand'), hostAt: [300, 800], hostScale: 0.55, hostX: 150};
    },

    weekly: (k, T) => {
      k.room('workshop');
      // the Friday whiteboard: both rows show as it opens; the header sits on a dark band
      k.ctx.save(); slideIn(k, k.S('weekly'), 0, 700);
      k.panel2(72, 300, 840, 470, {fill: CHALK, border: DARK});
      k.shape(k.rectPts(84, 312, 816, 92, 0), {fill: INK, line: false});
      k.text('Every Friday', 108, 328, {size: 60, color: CHALK2});
      const rows = [['Estimates given', 'weekly.two', /^estimates$/i], ['Jobs sold', 'weekly.two', /^jobs$/i]];
      rows.forEach(([r, id, re], i) => {
        const y = 436 + i * 110, tr = wordT(k, id, re, 1.5 + i);
        const on = T >= tr;
        k.text(r, 108, y, {size: 60, color: on ? DARK : '#6B7080'});
        k.shape(k.rectPts(700, y - 6, 180, 76, 0), {stroke: '#6B7080', lw: 4, line: false});
        k.shape(k.rectPts(96, y + 90, 792, 6, 0), {fill: LIGHT, line: false});
        if (on) k.sweep(108, y + 70, k.measure(r, {size: 60}), 8, tr, {color: 'accent'});
      });
      if (T >= k.S('weekly.dollars')) {
        const t0 = k.S('weekly.dollars');
        k.ctx.save(); slideIn(k, t0, -600, 0);
        k.text('$ sold / $ quoted', 108, 656, {size: 60, color: '#7A3442'});
        k.shape(k.rectPts(700, 650, 180, 76, 0), {stroke: '#6B7080', lw: 4, line: false});
        k.ctx.restore();
        k.burst(300, 690, t0 + 0.3, {n: 14, r: 200});
      }
      k.ctx.restore();
      if (T >= k.S('weekly.lower')) {   // what the dollar rate tells you, under the board
        const t0 = k.S('weekly.lower');
        k.ctx.save(); slideIn(k, t0, 0, 200);
        k.panel2(72, 790, 840, 140, {fill: INK, border: 'accent'});
        k.text('$ rate lower than the count?', 108, 808, {size: 39, color: CHALK});
        k.ctx.restore();
        if (T >= k.S('weekly.away')) k.slam('Big quotes are getting away.', 108, 862, k.S('weekly.away'), {size: 39, color: 'accent', stamp: true});
      }
      return {hostPose: k.live('weekly.away') ? 'clip' : (k.talking() ? 'talk' : 'stand'), hostScale: 0.55, hostX: 150};
    },

    close: (k, T) => {
      k.room('blackboard'); boardClip(k);
      const t1 = k.S('close'), tj = wordT(k, 'close', /^divided$/i, 0.6), tg = wordT(k, 'close', /^estimates$/i, 1.0);
      // centered, so the board reads as one card; the send line is a full-width box, the biggest call on screen
      k.slam('Close rate =', 540, 262, t1, {size: 120, color: 'accent', from: 0.7, align: 'center'});
      k.slam('jobs sold', 540, 410, t1 + 0.1, {size: 60, color: CHALK, from: 0.7, align: 'center'});
      if (T >= tj) k.shape(k.rectPts(540 - 250 * k.easeOut((T - tj) / 0.3), 486, 500 * k.easeOut((T - tj) / 0.3), 10, 0), {fill: CHALK, line: false});
      if (T >= tg) k.slam('estimates given', 540, 512, tg, {size: 60, color: CHALK, from: 0.7, align: 'center'});
      k.burst(540, 320, t1 + 0.1, {n: 14, r: 200});
      if (T >= k.S('close.send')) {
        const t0 = k.S('close.send');
        k.ctx.save(); popAt(k, t0 - 0.2, 540, 640);
        k.panel2(340, 602, 400, 80, {fill: '#24453A', border: 'accent'}); k.text('ProofNotFluff', 540, 612, {size: 60, color: 'accent', align: 'center'});
        k.ctx.restore();
        k.burst(540, 642, t0 - 0.1, {n: 16});
        k.ctx.save(); slideIn(k, t0 + 0.2, 0, 200);
        k.panel2(84, 708, 900, 150, {fill: INK, border: 'accent'});
        k.text('Send this to whoever', 534, 726, {size: 60, color: CHALK, align: 'center'});
        k.text('writes your estimates.', 534, 790, {size: 60, color: CHALK2, align: 'center'});
        k.ctx.restore();
      }
      if (T >= k.S('close.friday')) {   // the payoff underlined as the last words echo the hook
        const t0 = wordT(k, 'close.friday', /^close$/i, 1.5), w = k.measure('Close rate =', {size: 120});
        if (T >= t0) { k.sweep(540 - w / 2, 398, w, 10, t0, {color: 'accent'}); k.burst(540 + w / 2, 400, t0 + 0.3, {n: 16}); }
      }
      k.ctx.restore();
      return {hostPose: T >= k.S('close.send') + 1.5 ? 'wave' : 'talk', hostScale: 0.55, hostX: 150};
    },
  },
};
