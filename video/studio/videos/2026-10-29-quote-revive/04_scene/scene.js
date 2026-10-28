// Scene: The text that revives a quote that went quiet (lesson 2, The Text, arcade). One function per top-level cue in
// 03_cues/cues.md. Numbers only from k.data (brief.md -> data.js). Rooms: framing, blackboard, garage, workshop, blackboard,
// framing, blackboard. Modeled on lesson 1 (2026-10-28-first-reply): hook card, slams, sparks, stamps, blinds between rooms.
const QUOTE_MSG = "Here's your quote for the new water heater.";
const NUDGE = 'Just checking in!';
const REPLY = [
  ['text.name', "Hi [name], it's [you].", '1 of 2: their name, then yours'],
  ['text.line', 'Still want that water heater swapped before winter?', '2 of 2: one question'],
];
const CHALK = '#FFF7EA', CHALK2 = '#F7C873', INK = '#1B1420', HOOK_END = 3.0;
// everything written on the board stays inside the board, even while it slides in
const boardClip = (k) => { k.ctx.save(); k.ctx.beginPath(); k.ctx.rect(60, 246, 960, 752); k.ctx.clip(); };
const slideIn = (k, t0, dx = 0, dy = 0) => { const q = k.easeOut((k.T - t0) / 0.35); k.ctx.translate(dx * 0.4 * (1 - q), dy * 0.4 * (1 - q)); k.ctx.globalAlpha *= k.clamp(q * 1.6); return q; };
// slides a block out (for a layout change inside a section)
const slideOut = (k, t0, dx = 0, dy = 0) => { const q = k.easeOut((k.T - t0) / 0.3); k.ctx.translate(dx * q, dy * q); k.ctx.globalAlpha *= k.clamp(1 - q * 1.4); return q; };
// the start of the first spoken word matching re at or after t (falls back to t + dt)
const wordAt = (k, re, t, dt = 0) => { const ws = (window.WORDS && window.WORDS.words) || []; const w = ws.find((x) => x.start >= t - 0.05 && re.test(x.w)); return w ? w.start : t + dt; };
// a pop-in scale around a point
const popAt = (k, t0, x, y, max = 1.15) => { const q = k.clamp(k.pop(t0), 0, max); k.ctx.translate(x, y); k.ctx.scale(q, q); k.ctx.translate(-x, -y); };
// a stamp that slams down and settles (lesson 1's DOESN'T COUNT stamp)
const stamp = (k, s, x, y, t0, o = {}) => {
  if (k.T < t0) return;
  const q = k.clamp((k.T - t0) / 0.18), sc = (2.2 - 1.2 * q) * (o.scale || 0.8), w = o.w || 460;
  k.ctx.save(); k.ctx.translate(x, y); k.ctx.rotate(o.rot != null ? o.rot : -0.08); k.ctx.scale(sc, sc);
  k.shape(k.rectPts(-w / 2, -60, w, 120, 0), {fill: INK, line: false, alpha: q});
  k.shape(k.rectPts(-w / 2 + 6, -54, w - 12, 108, 0), {stroke: 'accent', lw: 9, line: false, alpha: q});
  k.text(s, 0, -30, {size: 60, color: 'accent', align: 'center', alpha: q, lint: false});
  k.ctx.restore();
  k.burst(x, y, t0 + 0.18, {n: 22, r: 300, colors: ['accent', '#9AA0AD', 'paper']});
};

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 2',
  sections: {
    hook: (k, T) => {
      k.room('framing');
      if (T < HOOK_END) {   // the hook card: settled on frame 0, the host and the dialog box step aside
        k.shape(k.rectPts(0, 230, 1080, 840, 0), {fill: INK, line: false});
        const cw = k.measure('THE TEXT', {size: 30}) + 36;
        k.chip('The Text', 540 - cw / 2, 286, {size: 30, fill: 'accent', color: INK});
        k.slam('Quote went', 540, 380, -1, {size: 120, color: CHALK, align: 'center'});
        k.slam('quiet?', 540, 520, -1, {size: 180, color: 'accent', align: 'center'});
        k.slam('Send this text.', 540, 750, -1, {size: 120, color: CHALK, align: 'center'});
        k.sweep(270, 892, 540, 10, -1, {color: 'accent'});
        k.burst(540, 620, 0.1, {n: 26, r: 380});
        return {host: false, speech: false};
      }
      // the quote you left, read and unanswered
      k.ctx.save(); slideIn(k, HOOK_END, -500, 0); k.chip('No reply yet', 72, 300, {size: 30}); k.ctx.restore();
      k.ctx.save(); slideIn(k, HOOK_END + 0.1, 600, 0);
      k.phone(470, 300, 460, 620, [{text: QUOTE_MSG, me: true, at: -1, stamp: 'Read'}], {who: 'Homeowner', size: 39});
      k.ctx.restore();
      k.ctx.save(); slideIn(k, HOOK_END + 0.2, -500, 0);
      k.panel2(60, 400, 380, 150, {title: 'Waiting'});
      // a typing indicator that never turns into a reply
      for (let i = 0; i < 3; i++) { const b = Math.max(0, Math.sin(T * 6 - i * 0.9)) * 18; k.shape(k.rectPts(150 + i * 70, 456 - b, 40, 40, 0), {fill: i === Math.floor(T * 3) % 3 ? 'accent2' : 'muted', line: false}); }
      k.ctx.restore();
      const ts = Math.max(k.S('hook.send'), HOOK_END + 0.25);
      if (T >= ts) {
        k.ctx.save(); k.ctx.translate(252, 680); k.ctx.rotate(-0.04); k.ctx.translate(-252, -680); popAt(k, ts, 252, 680);
        k.panel2(72, 620, 360, 120, {fill: 'accent', border: INK});
        k.text('Send this.', 252, 648, {size: 60, color: INK, align: 'center'});
        k.ctx.restore();
        k.burst(252, 680, ts + 0.05, {n: 18});
      }
      return {hostPose: T >= ts ? 'point' : (k.talking() ? 'talk' : 'stand'), hostAt: [600, 520]};
    },

    stakes: (k, T) => {
      const n = k.data.numbers;
      k.room('blackboard'); boardClip(k);
      k.slam("ServiceTitan's own data", 96, 280, k.S('stakes'), {size: 60, color: CHALK2, from: 0.5});
      k.ctx.save(); slideIn(k, k.S('stakes') + 0.3, -600, 0);
      k.text(`ServiceTitan blog, ${n.stYear.shown}`, 96, 356, {size: 39, color: CHALK});
      k.ctx.restore();
      if (T < k.S('stakes.count')) {   // an estimate, chalked on the board while the voice names the source
        const t0 = k.S('stakes') + 0.4, q = k.clamp(k.pop(t0, 0.4), 0, 1.1);
        k.ctx.save(); k.ctx.translate(560, 660); k.ctx.rotate(-0.04); k.ctx.scale(q, q);
        k.shape(k.rectPts(-170, -200, 340, 400, 0), {fill: CHALK, line: false});
        k.shape(k.rectPts(-170, -200, 340, 70, 0), {fill: 'accent', line: false});
        k.text('ESTIMATE', 0, -186, {size: 39, color: INK, align: 'center'});
        for (let i = 0; i < 5; i++) k.shape(k.rectPts(-136, -96 + i * 50, i % 2 ? 170 : 270, 12, 0), {fill: '#9AA0AD', line: false});
        k.shape(k.rectPts(-136, 150, 140, 12, 0), {fill: INK, line: false});
        k.ctx.restore();
        k.burst(560, 660, t0 + 0.05, {n: 14, colors: ['paper', 'accent2']});
      }
      if (T >= k.S('stakes.count')) {
        const t0 = k.S('stakes.count'), p = k.lin(t0, t0 + 1.0);
        k.slam(k.count(n.closePct.value, p, {suffix: '%'}), 96, 420, t0, {size: 180, color: 'accent', from: 0.6});
        if (p >= 1) k.burst(230, 520, t0 + 1.0, {n: 16, colors: ['accent', 'paper']});
        k.ctx.save(); slideIn(k, t0 + 0.3, 500, 0);
        k.text('of estimates close', 402, 452, {size: 39, color: CHALK});
        k.text('on the first visit', 402, 502, {size: 39, color: CHALK});
        k.ctx.restore();
      }
      if (T >= k.S('stakes.bar')) {   // a bar for every estimate: the share that closed, and the rest still open
        const t0 = k.S('stakes.bar'), p = k.easeOut((T - t0) / 0.7), W = 700, f = n.closePct.value / 100;
        k.shape(k.rectPts(96, 650, W, 50, 0), {stroke: CHALK, lw: 6, line: false});
        k.shape(k.rectPts(96, 650, W * f * p, 50, 0), {fill: 'accent', line: false});
        if (p > 0.6) {
          k.slam('closed', 96, 722, t0 + 0.45, {size: 39, color: 'accent', from: 0.5});
          k.slam('still open', 96 + W * f + 30, 722, t0 + 0.6, {size: 39, color: CHALK, from: 0.5});
        }
      }
      // your van, parked at the job; on "driveway" it pulls away (the quote leaves with you)
      if (T >= k.S('stakes.bar') + 0.4 && T < k.S('stakes.rest') + 0.2) {
        const t0 = k.S('stakes.drive'), go = T >= t0 ? Math.pow((T - t0) / 1.4, 2) : 0;
        const q = k.clamp(k.pop(k.S('stakes.bar') + 0.4), 0, 1.1), vx = 640 + go * 520;
        k.ctx.save(); k.ctx.translate(vx + 100, 830); k.ctx.scale(q, q); k.ctx.translate(-(vx + 100), -830);
        k.shape(k.rectPts(vx, 780, 150, 70, 0), {fill: '#C9CCD3', line: false});
        k.shape(k.rectPts(vx + 150, 798, 54, 52, 0), {fill: '#C9CCD3', line: false});
        k.shape(k.rectPts(vx + 158, 806, 36, 22, 0), {fill: '#87CEEB', line: false});
        k.shape(k.rectPts(vx + 10, 800, 120, 12, 0), {fill: 'accent', line: false});
        for (const wx of [vx + 36, vx + 166]) k.shape(k.ellPts(wx, 852, 18, 18, 12), {fill: INK, line: false});
        if (go > 0) for (let i = 0; i < 3; i++) k.shape(k.rectPts(vx - 30 - i * 28, 836 - i * 6, 18, 12, 0), {fill: '#9AA0AD', line: false, alpha: 0.7 - i * 0.2});
        k.ctx.restore();
      }
      if (T >= k.S('stakes.rest')) {
        const t0 = k.S('stakes.rest');
        k.slam('The rest depend on your follow-up.', 96, 790, t0, {size: 39, color: CHALK, from: 0.5});
        k.sweep(96, 840, 549, 9, t0 + 0.4, {color: 'accent'});
      }
      k.ctx.restore();
      return {hostPose: k.talking() ? 'talk' : 'stand', hostScale: 0.6, hostX: 160};
    },

    homework: (k, T) => {
      k.room('garage');
      const tFix = k.S('homework.fix');
      if (T < tFix + 0.35) {
        k.ctx.save(); if (T >= tFix) slideOut(k, tFix, -900, 0);
        k.ctx.save(); slideIn(k, k.S('homework'), -500, 0); k.chip('Just checking in?', 72, 280, {size: 30}); k.ctx.restore();
        let nudge = null;
        k.ctx.save(); slideIn(k, k.S('homework') + 0.1, 0, 800);
        k.phone(72, 330, 540, 600, [
          {text: QUOTE_MSG, me: true, at: -1},
          {text: NUDGE, me: true, at: k.S('homework') + 0.7, box: (b) => { nudge = b; }},
        ], {who: 'Homeowner', size: 39});
        k.ctx.restore();
        // the homework sheet it hands them; on "puts homework off" it slides onto a pile
        const ts = k.S('homework.sheet');
        if (T >= ts) {
          const to = k.S('homework.off'), off = T >= to ? k.easeOut((T - to) / 0.5) : 0;
          k.ctx.save();
          k.ctx.translate(790, 520); k.ctx.rotate(0.04 + off * 0.18); const sc = (1 - 0.45 * off) * k.clamp(k.pop(ts + 0.25), 0, 1.1);
          k.ctx.scale(sc, sc); k.ctx.translate(-790, -520); k.ctx.translate(0, off * 300);
          k.shape(k.rectPts(650, 340, 290, 380, 0), {fill: CHALK, line: false});
          k.shape(k.rectPts(650, 340, 290, 56, 0), {fill: '#7A3442', line: false});
          k.text('Reply:', 672, 352, {size: 39, color: CHALK});
          for (let i = 0; i < 5; i++) k.shape(k.rectPts(672, 440 + i * 56, 246, 6, 0), {fill: '#9AA0AD', line: false});
          const tw = k.S('homework.write');
          if (T >= tw && T < to) {   // a pencil hovers over the blank lines and writes nothing
            const q = k.easeOut((T - tw) / 0.4), px = 760 + Math.sin((T - tw) * 5) * 60, py = 470 - (1 - q) * 120;
            k.ctx.save(); k.ctx.translate(px, py); k.ctx.rotate(0.6);
            k.shape(k.rectPts(-12, -120, 24, 110, 0), {fill: 'accent', line: false});
            k.shape(k.rectPts(-12, -140, 24, 20, 0), {fill: '#F09A9A', line: false});
            k.shape([[-12, -10], [12, -10], [0, 14]], {fill: '#D9A066', line: false});
            k.ctx.restore();
          }
          k.ctx.restore();
          if (T >= to) {
            k.ctx.save(); slideIn(k, to + 0.4, 400, 0); k.chip('Later', 700, 880, {size: 30, fill: '#4A4E5A'}); k.ctx.restore();
          }
          if (nudge) stamp(k, 'Homework', 342, nudge.y + nudge.h + 92, ts, {w: 420, scale: 0.75});
        }
        k.ctx.restore();
      }
      // Dean Jackson's fix: one short question about what they wanted, no pitch
      if (T >= tFix) {
        k.ctx.save(); slideIn(k, tFix + 0.1, 900, 0);
        k.panel2(72, 330, 858, 470, {title: "Dean Jackson's fix"});
        k.text('Are you still looking for ...?', 112, 380, {size: 39, color: 'muted'});
        k.ctx.restore();
        if (T >= k.S('homework.ask')) {
          const t0 = k.S('homework.ask');
          k.slam('One short question', 112, 470, t0, {size: 60, color: 'ink', from: 0.5});
          k.ctx.save(); slideIn(k, t0 + 0.4, 500, 0); k.text('about what they wanted.', 112, 556, {size: 39, color: 'ink'}); k.ctx.restore();
        }
        if (T >= k.S('homework.pitch')) {
          const t0 = k.S('homework.pitch');
          k.slam('No pitch.', 112, 660, t0, {size: 60, color: 'accent', from: 0.7});
          k.sweep(112, 736, 207, 9, t0 + 0.3, {color: 'accent'});
          k.burst(220, 690, t0 + 0.1, {n: 14});
        }
      }
      const shrug = T >= k.S('homework.off') && T < tFix;
      return {hostPose: shrug ? 'shrug' : (k.talking() ? 'talk' : 'stand'), hostScale: 0.6, hostX: 160};
    },

    text: (k, T) => {
      k.room('workshop');
      let cur = -1; REPLY.forEach(([id], i) => { if (T >= k.S(id)) cur = i; });
      // typed so far: whole earlier lines plus part of the current one; the bubble is laid out for the whole text
      const FULL = REPLY.map((r) => r[1]).join(' ');
      let reveal = 0;
      REPLY.forEach(([id, line], i) => { if (T < k.S(id)) return;
        const p = k.lin(k.S(id) + 0.1, k.S(id) + 0.1 + line.length * 0.035);
        reveal = REPLY.slice(0, i).reduce((a, r) => a + r[1].length + 1, 0) + Math.floor(line.length * p); });
      const typingTo = cur >= 0 ? k.S(REPLY[cur][0]) + 0.1 + REPLY[cur][1].length * 0.035 : 0;
      let bub = null;
      const knowOn = T >= k.S('text.know') && T < k.S('text.line');
      k.ctx.save(); slideIn(k, k.S('text') + 0.1, 0, 800);
      k.phone(90, 340, 820, 640, [
        ...(T >= k.S('text.name') ? [{text: FULL, reveal, me: true, at: k.S('text.name'), typing: typingTo, box: (b) => { bub = b; }}] : []),
      ], {who: 'Homeowner', size: 60});   // the copyable text, big
      k.ctx.restore();
      k.ctx.save();
      if (cur >= 0) popAt(k, k.S(REPLY[cur][0]), 100, 290, 1.2); else slideIn(k, k.S('text'), -500, 0);
      const done = T >= k.S('text.hold');
      k.chip(done ? 'The text' : (cur >= 0 ? REPLY[cur][2] : 'The text'), 100, 270, {size: 30, fill: cur >= 0 ? 'accent' : 'tag', color: cur >= 0 ? INK : 'tagText'});
      k.ctx.restore();
      if (cur >= 0) k.burst(240, 290, k.S(REPLY[cur][0]) + 0.05, {n: 12, r: 180});
      if (knowOn) {   // a side note under the bubble: why your name goes in
        const t0 = k.S('text.know');
        k.ctx.save(); slideIn(k, t0, 700, 0); k.ctx.translate(500, 730); k.ctx.rotate(-0.02); k.ctx.translate(-500, -730);
        k.panel2(150, 680, 700, 100, {fill: 'accent', border: INK});
        k.text("So they know it's you.", 500, 710, {size: 39, color: INK, align: 'center'});
        k.ctx.restore();
      }
      if (bub && T >= k.S('text.hold')) k.spot(bub.x, bub.y, bub.w, bub.h, k.S('text.hold'), {pad: 12, lw: 9});
      if (bub && T >= k.S('text.yesno')) {   // two reply buttons: a yes or a no is all it takes
        const t0 = k.S('text.yesno'), y = bub.y + bub.h + 30;
        [['Yes', 520], ['No', 700]].forEach(([s, x], i) => {
          k.ctx.save(); popAt(k, t0 + i * 0.15, x + 70, y + 30);
          k.panel2(x, y, 140, 60, {fill: '#3D2E45', border: 'accent'});
          k.text(s, x + 70, y + 12, {size: 39, color: CHALK, align: 'center'});
          k.ctx.restore();
          k.burst(x + 70, y + 30, t0 + i * 0.15 + 0.05, {n: 10, r: 140});
        });
      }
      // the host steps back (smaller) so he never covers the text being typed
      return {hostPose: k.talking() ? 'talk' : 'stand', hostScale: 0.55, hostX: 150};
    },

    turn: (k, T) => {
      const n = k.data.numbers;
      k.room('blackboard'); boardClip(k);
      k.slam('The part people skip', 96, 280, k.S('turn'), {size: 60, color: CHALK2, from: 0.5});
      if (T >= k.S('turn.own')) {
        const t0 = k.S('turn.own'), t1 = wordAt(k, /^own/i, t0, 0.6);
        k.slam('Keep it in', 96, 370, t0, {size: 120, color: CHALK, from: 0.6});
        k.slam('your own words.', 96, 490, t1, {size: 120, color: 'accent', from: 0.6});
        k.burst(300, 560, t1 + 0.1, {n: 16});
      }
      if (T >= k.S('turn.study')) {
        const t0 = k.S('turn.study');
        k.ctx.save(); slideIn(k, t0, -600, 0); k.text('"Speed Is a Signal"', 96, 660, {size: 39, color: CHALK}); k.ctx.restore();
        k.ctx.save(); slideIn(k, t0 + 0.25, -600, 0); k.text(`Management Science, ${n.studyYear.shown}`, 96, 706, {size: 39, color: CHALK2}); k.ctx.restore();
      }
      if (T >= k.S('turn.fast')) {
        k.ctx.save(); slideIn(k, k.S('turn.fast'), -600, 0); k.text('Fast replies stopped helping', 96, 770, {size: 39, color: CHALK}); k.ctx.restore();
      }
      if (T >= k.S('turn.bot')) {   // a chalk robot, crossed out: sounding like a bot cancels the speed
        const t0 = k.S('turn.bot');
        k.ctx.save(); slideIn(k, t0, -600, 0); k.text('once people thought a bot wrote them.', 96, 816, {size: 39, color: CHALK}); k.ctx.restore();
        k.ctx.save(); popAt(k, t0 + 0.1, 870, 730);
        k.shape(k.rectPts(864, 652, 12, 24, 0), {fill: CHALK, line: false}); k.shape(k.rectPts(856, 640, 28, 14, 0), {fill: 'accent', line: false});
        k.shape(k.rectPts(810, 676, 120, 84, 0), {stroke: CHALK, lw: 8, line: false});
        k.shape(k.rectPts(834, 700, 20, 20, 0), {fill: CHALK, line: false}); k.shape(k.rectPts(886, 700, 20, 20, 0), {fill: CHALK, line: false});
        k.shape(k.rectPts(840, 736, 60, 8, 0), {fill: CHALK, line: false});
        k.shape(k.rectPts(826, 768, 88, 40, 0), {stroke: CHALK, lw: 8, line: false});
        const xq = k.easeOut((T - t0 - 0.4) / 0.3);
        if (xq > 0) {
          k.shape([[800, 640], [800 + 140 * xq, 640 + 170 * xq]], {stroke: 'accent', lw: 12, closed: false, line: false});
          k.shape([[940, 640], [940 - 140 * xq, 640 + 170 * xq]], {stroke: 'accent', lw: 12, closed: false, line: false});
        }
        k.ctx.restore();
        k.burst(870, 720, t0 + 0.5, {n: 18});
      }
      k.ctx.restore();
      return {hostPose: k.talking() ? 'talk' : 'stand', hostScale: 0.6, hostX: 160};
    },

    cadence: (k, T) => {
      const n = k.data.numbers;
      k.room('framing');
      k.ctx.save(); slideIn(k, k.S('cadence'), 0, 700);
      k.panel2(60, 320, 900, 550, {title: 'Jobber says'});
      k.text('When to send it', 100, 372, {size: 60, color: 'ink'});
      const steps = [
        {id: 'cadence.first', day: `Within ${n.firstDays.shown}`, label: 'of the quote'},
        {id: 'cadence.week', day: n.secondDays.shown, label: 'a week after'},
        {id: 'cadence.final', day: `${n.finalMin.shown} to ${n.finalMax.shown}`, label: 'before it expires'},
      ].map((s) => ({day: s.day, label: s.label, at: k.S(s.id), hi: k.live(s.id)}));
      k.timeline(210, 610, 570, steps, k.lin(k.S('cadence') + 0.3, k.S('cadence') + 1.2), {labelW: 240});
      k.ctx.restore();
      steps.forEach((s, i) => k.burst(210 + 285 * i, 610, s.at + 0.05, {n: 12, r: 150}));
      if (T >= k.S('cadence.close')) {
        const t0 = k.S('cadence.close');
        k.ctx.save(); popAt(k, t0, 540, 790);
        k.panel2(190, 754, 700, 76, {fill: 'accent', border: INK});
        k.text(`After ${n.followUps.shown}, close the file.`, 540, 774, {size: 39, color: INK, align: 'center'});
        k.ctx.restore();
        k.burst(540, 790, t0 + 0.05, {n: 18});
      }
      return {hostPose: k.talking() ? 'point' : 'stand', hostAt: [500, 610], hostScale: 0.6, hostX: 160};
    },

    close: (k, T) => {
      k.room('blackboard'); boardClip(k);
      const tKnow = k.S('close.know');
      if (T < tKnow + 0.3) {   // the rule, one word slammed in as it is said
        k.ctx.save(); if (T >= tKnow) slideOut(k, tKnow, -900, 0);
        [['One name.', /^name/i], ['One job.', /^job/i], ['One question.', /^question/i]].forEach(([ln, re], i) => {
          const t0 = wordAt(k, re, k.S('close'), i * 0.5);
          k.slam(ln, 96, 280 + i * 124, t0, {size: 120, color: i === 2 ? 'accent' : CHALK, from: 0.7});
          k.burst(120, 340 + i * 124, t0 + 0.12, {n: 8, r: 140, colors: i === 2 ? ['accent', 'accent2'] : ['paper', '#2F5A4A']});
        });
        k.ctx.restore();
      }
      if (T >= tKnow) {   // the last words echo the hook card
        k.slam('Quote went quiet?', 96, 280, tKnow + 0.1, {size: 60, color: CHALK2, from: 0.5});
        k.slam('Now you know', 96, 370, tKnow + 0.25, {size: 120, color: CHALK, from: 0.6});
        k.slam('what to send.', 96, 500, wordAt(k, /^send/i, tKnow, 0.6), {size: 120, color: 'accent', from: 0.6});
      }
      if (T >= k.S('close.send')) {
        const t0 = k.S('close.send'), tb = t0 - 0.3;
        k.ctx.save(); popAt(k, tb, 96, 690);
        k.panel2(96, 690, 440, 80, {fill: '#24453A', border: 'accent'}); k.text('ProofNotFluff', 316, 700, {size: 60, color: 'accent', align: 'center'});
        k.ctx.restore();
        k.burst(316, 730, tb + 0.1, {n: 16});
        k.ctx.save(); slideIn(k, t0, 700, 0);
        k.panel2(300, 800, 650, 110, {fill: INK, border: 'accent'});
        k.text('Send this to whoever', 330, 814, {size: 39, color: CHALK});
        k.text('follows up on your quotes.', 330, 858, {size: 39, color: CHALK});
        k.ctx.restore();
      }
      if (T >= k.S('close.quiet')) {
        k.ctx.save(); slideIn(k, k.S('close.quiet'), 700, 0);
        k.text('Exact text', 580, 696, {size: 30, color: CHALK2});
        k.text('in the caption.', 580, 734, {size: 30, color: CHALK2});
        k.ctx.restore();
      }
      k.ctx.restore();
      return {hostPose: T >= tKnow + 0.8 ? 'wave' : 'talk', hostScale: 0.6, hostX: 160};
    },
  },
};
