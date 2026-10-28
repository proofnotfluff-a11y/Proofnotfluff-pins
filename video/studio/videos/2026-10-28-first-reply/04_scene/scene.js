// Scene: The first reply wins the job (v2, arcade, with motion). One function per top-level cue in 03_cues/cues.md.
// Numbers only from k.data (brief.md -> data.js). Rooms: framing, blackboard, workshop, garage.
// Motion (Todd, Oct 28, 1:33 pm): a hook card in the first 2.4 s, slams, sparks, a zoom ladder, shakes, blinds between rooms.
const LEAD_TEXT = 'Can you quote a new water heater? Ours is leaking.';
const REPLY = [
  ['build.name', 'Hi [name],', '1 of 4: their name'],
  ['build.answer', 'yes, we replace water heaters.', '2 of 4: answer it'],
  ['build.ask', 'Gas or electric?', '3 of 4: one question'],
  ['build.time', 'I can come by tomorrow, 2 to 4.', '4 of 4: a real time'],
];
const CHALK = '#FFF7EA', CHALK2 = '#F7C873', HOOK_END = 2.4;
// everything written on the board stays inside the board, even while it slides in
const boardClip = (k) => { k.ctx.save(); k.ctx.beginPath(); k.ctx.rect(60, 246, 960, 752); k.ctx.clip(); };
const slideIn = (k, t0, dx = 0, dy = 0) => { const q = k.easeOut((k.T - t0) / 0.35); k.ctx.translate(dx * 0.4 * (1 - q), dy * 0.4 * (1 - q)); k.ctx.globalAlpha *= k.clamp(q * 1.6); return q; };

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  hud: 'LESSON 1',
  focus: {'study.count': [300, 520], 'study.hour': [400, 660], 'study.day': [400, 730], 'signal.alone': [400, 650],
          'tt.more': [500, 740], 'catch.canned': [665, 880], 'build.why': [650, 880], 'close.send': [600, 800]},
  sections: {
    lead: (k, T) => {
      const n = k.data.numbers;
      k.room('framing');
      if (T < HOOK_END) {   // the hook card: the number that makes a pro stop scrolling
        // the host steps aside for the hook, so nothing covers the claim or its source (gates, Oct 28)
        k.shape(k.rectPts(0, 230, 1080, 840, 0), {fill: '#1B1420', line: false});
        k.slam('Answer a lead', 540, 262, -1, {size: 120, color: CHALK, align: 'center'});
        k.slam('a day late?', 540, 366, -1, {size: 120, color: CHALK, align: 'center'});
        k.slam(n.dayDrop.shown, 540, 472, -0.3, {size: 330, color: 'accent', align: 'center', from: 1.4, shake: 8});
        k.slam('less likely', 540, 762, -0.3, {size: 120, color: 'accent', align: 'center'});
        k.slam('to get hired.', 540, 878, -0.3, {size: 120, color: CHALK, align: 'center'});
        k.burst(540, 620, 0.35, {n: 26, r: 380});
        k.text(`Fiverr study, Management Science ${n.studyYear.shown}`, 540, 1016, {size: 39, color: '#E6D3BC', align: 'center'});
        return {host: false, speech: false};
      }
      k.ctx.save(); slideIn(k, HOOK_END, -500, 0); k.chip('New lead', 72, 280, {size: 30}); k.ctx.restore();
      k.ctx.save(); slideIn(k, HOOK_END + 0.1, 600, 0);
      const tl0 = Math.max(k.S('lead.ladder'), HOOK_END + 0.2), m0 = 14 + Math.max(0, Math.floor((T - tl0) * 7));
      k.phone(470, 300, 460, 640, [{text: LEAD_TEXT, at: HOOK_END + 0.4, stamp: '9:14 am'}], {who: 'Homeowner', size: 39, clock: `${9 + Math.floor(m0 / 60)}:${String(m0 % 60).padStart(2, '0')}`});
      k.ctx.restore();
      k.burst(700, 470, HOOK_END + 0.45, {n: 10, r: 160, colors: ['accent2', 'paper']});
      // the ladder slides in, and the reply clock starts (a story clock, not data)
      const tl = Math.max(k.S('lead.ladder'), HOOK_END + 0.2);
      if (T >= tl) {
        const q = k.easeOut((T - tl) / 0.5), lx = 330 - (1 - q) * 300;
        for (const x of [lx, lx + 84]) k.shape(k.rectPts(x, 560, 18, 690, 0), {fill: '#B07A47', line: false});
        for (let y = 600; y < 1240; y += 84) k.shape(k.rectPts(lx, y, 102, 14, 0), {fill: '#D9A066', line: false});
      }
      const mins = Math.max(0, (T - tl) * 7);
      k.ctx.save(); slideIn(k, HOOK_END + 0.2, -500, 0);
      k.panel2(60, 400, 400, 160, {title: 'Waiting on you'});
      const tick = Math.floor(mins), jolt = (T - tl) * 7 % 1 < 0.15 && T >= tl ? 6 : 0;
      k.text(`${tick} min`, 260, 446 - jolt, {size: 100, color: mins > 20 ? 'accent' : 'ink', align: 'center'});
      k.ctx.restore();
      if (T >= k.S('lead.show')) {
        k.ctx.save(); k.ctx.translate(252, 670); k.ctx.rotate(-0.04);
        const q = k.clamp(k.pop(k.S('lead.show')), 0, 1.15); k.ctx.scale(q, q); k.ctx.translate(-252, -670);
        k.panel2(72, 610, 360, 130, {fill: 'accent', border: '#1B1420'});
        k.text('Tonight is', 252, 628, {size: 39, color: '#1B1420', align: 'center'});
        k.text('too late.', 252, 672, {size: 60, color: '#1B1420', align: 'center'});
        k.ctx.restore();
        k.burst(252, 675, k.S('lead.show') + 0.05, {n: 18});
      }
      return {hostPose: k.live('lead.ladder') ? 'clip' : (k.talking() ? 'talk' : 'stand')};
    },

    study: (k, T) => {
      const n = k.data.numbers;
      k.room('blackboard'); boardClip(k);
      k.slam('The study', 96, 280, k.S('study'), {size: 60, color: CHALK2, from: 0.5});
      k.ctx.save(); slideIn(k, k.S('study') + 0.25, -600, 0);
      k.text('"Speed Is a Signal"', 96, 352, {size: 39, color: CHALK});
      k.text(`Management Science, ${n.studyYear.shown}`, 96, 398, {size: 39, color: CHALK2});
      k.ctx.restore();
      if (T >= k.S('study.count')) {
        const p = k.lin(k.S('study.count'), k.S('study.count') + 1.2);
        const big = k.count(n.interactions.value, 1, {dec: 1, suffix: 'M'}), bx = 96 + k.measure(big, {size: 120}) + 24;
        k.slam(k.count(n.interactions.value, p, {dec: 1, suffix: 'M'}), 96, 440, k.S('study.count'), {size: 120, color: CHALK, from: 0.6});
        if (p >= 1) k.burst(250, 500, k.S('study.count') + 1.2, {n: 14, colors: ['paper', 'accent2']});
        if (p >= 1) { k.ctx.save(); slideIn(k, k.S('study.count') + 1.2, 400, 0); k.text('requests on Fiverr', bx, 490, {size: 39, color: CHALK}); k.ctx.restore(); }
      }
      const bar = (y, label, v, shown, t0, hot) => {
        if (T < t0) return;
        const p = k.easeOut((T - t0) / 0.7);
        k.ctx.save(); slideIn(k, t0, -500, 0); k.text(label, 96, y, {size: 39, color: CHALK}); k.ctx.restore();
        k.shape(k.rectPts(96, y + 50, 530, 48, 0), {stroke: CHALK, lw: 6, line: false});
        k.shape(k.rectPts(96, y + 50, 530 * (v / 100) * p, 48, 0), {fill: hot ? 'accent' : CHALK, line: false});
        if (p > 0.6) k.slam(`${shown} less`, 652, y + 40, t0 + 0.45, {size: 60, color: hot ? 'accent' : CHALK, from: 1.2});
        if (hot) k.burst(96 + 530 * (v / 100), y + 74, t0 + 0.7, {n: 18});
      };
      bar(570, '1 hour late: about half as likely', n.hourDrop.value, n.hourDrop.shown, k.S('study.hour'), false);
      bar(690, '1 day late:', n.dayDrop.value, n.dayDrop.shown, k.S('study.day'), true);
      // the journal itself, chalked onto the board while the voice names it (the board is never empty)
      if (T < k.S('study.count')) {
        const t0 = k.S('study') + 0.4, q = k.clamp(k.pop(t0, 0.4), 0, 1.1);
        k.ctx.save(); k.ctx.translate(790, 720); k.ctx.rotate(0.05); k.ctx.scale(q * 0.85, q * 0.85);
        k.shape(k.rectPts(-150, -190, 300, 380, 0), {fill: CHALK, line: false});
        k.shape(k.rectPts(-150, -190, 300, 70, 0), {fill: 'accent', line: false});
        k.text('JOURNAL', 0, -176, {size: 39, color: '#1B1420', align: 'center'});
        for (let i = 0; i < 6; i++) k.shape(k.rectPts(-118, -90 + i * 44, i % 3 === 2 ? 150 : 236, 12, 0), {fill: '#9AA0AD', line: false});
        k.ctx.restore();
        k.burst(790, 720, t0 + 0.05, {n: 14, colors: ['paper', 'accent2']});
      }
      k.ctx.restore();
      return {};
    },

    signal: (k, T) => {
      k.room('blackboard'); boardClip(k);
      k.slam('Why it works', 96, 280, k.S('signal'), {size: 60, color: CHALK2, from: 0.5});
      const t1 = k.S('signal') + 0.6;
      if (T >= t1) {
        k.ctx.save(); slideIn(k, t1, -600, 0); k.text('Your reply speed tells them', 96, 400, {size: 39, color: CHALK}); k.ctx.restore();
        k.slam('how you\'ll treat them later.', 96, 450, t1 + 0.35, {size: 60, color: CHALK, from: 0.4});
        k.sweep(96, 520, 760, 8, t1 + 0.6, {color: 'accent'});
      }
      if (T >= k.S('signal.alone')) {
        const t0 = k.S('signal.alone');
        k.slam('It helped on its own:', 96, 590, t0, {size: 39, color: CHALK2, from: 0.5});
        k.ctx.save(); slideIn(k, t0 + 0.2, -600, 0); k.text('same work, same message,', 96, 644, {size: 39, color: CHALK}); k.ctx.restore();
        k.ctx.save(); slideIn(k, t0 + 0.4, -600, 0); k.text('faster reply still won.', 96, 694, {size: 39, color: CHALK}); k.ctx.restore();
        k.sweep(96, 756, 560, 9, t0 + 0.7, {color: 'accent'});
      }
      k.ctx.restore();
      return {hostPose: k.talking() ? 'point' : 'stand', hostAt: [400, 480]};
    },

    tt: (k, T) => {
      const n = k.data.numbers;
      k.room('workshop');
      k.ctx.save(); slideIn(k, k.S('tt'), 0, 700);
      k.panel2(72, 300, 858, 510, {title: 'Thumbtack, 2025'});
      k.text('Time to reply, and who got hired', 112, 350, {size: 39, color: 'ink'});
      // each clock fills a wedge for the time that passes: half a face for 30 minutes, three full turns for 3 hours
      const clock = (cx, cy, r, turns, c, t0) => {
        k.shape(k.ellPts(cx, cy, r, r, 24), {fill: '#2B2033', stroke: c, lw: 9, line: false});
        const spin = k.easeOut((T - t0) / 1.4) * turns, part = Math.min(1, spin), a1 = -Math.PI / 2 + part * Math.PI * 2;
        if (part > 0.01) k.shape([[cx, cy]].concat(k.ellPts(cx, cy, r - 12, r - 12, 24, -Math.PI / 2, a1)), {fill: c, line: false, alpha: 0.55});
        const ang = -Math.PI / 2 + spin * Math.PI * 2;
        k.shape([[cx, cy], [cx + Math.cos(ang) * r * 0.75, cy + Math.sin(ang) * r * 0.75]], {stroke: 'ink', lw: 9, closed: false, line: false});
      };
      clock(260, 500, 80, 0.5, 'accent', k.S('tt') + 0.4); clock(640, 500, 80, 3, '#9AA0AD', k.S('tt') + 0.4);
      k.text(n.ttMinutes.shown, 260, 600, {size: 60, color: 'accent', align: 'center'});
      k.text(n.ttHours.shown, 640, 600, {size: 60, color: '#C9CCD3', align: 'center'});
      k.text('to reply', 260, 660, {size: 39, color: 'muted', align: 'center'});
      k.text('to reply', 640, 660, {size: 39, color: 'muted', align: 'center'});
      k.ctx.restore();
      if (T >= k.S('tt.more')) {
        const q = k.clamp(k.pop(k.S('tt.more')), 0, 1.15);
        k.ctx.save(); k.ctx.translate(500, 742); k.ctx.scale(q, q); k.ctx.translate(-500, -742);
        k.panel2(112, 712, 778, 72, {fill: 'accent', border: '#1B1420'});
        k.text(`${n.ttMore.shown} more likely to get hired`, 501, 726, {size: 39, color: '#1B1420', align: 'center'});
        k.ctx.restore();
        k.burst(260, 730, k.S('tt.more') + 0.05, {n: 20});
      }
      return {};
    },

    catch: (k, T) => {
      k.room('garage');
      k.ctx.save(); slideIn(k, k.S('catch'), -500, 0); k.chip('The catch', 72, 280, {size: 30}); k.ctx.restore();
      k.ctx.save(); slideIn(k, k.S('catch') + 0.1, 0, 800);
      k.phone(360, 290, 590, 670, [
        {text: LEAD_TEXT, at: -1},
        {text: '[Auto-reply] Thank you for your inquiry. A representative will be in touch.', me: true, at: k.S('catch') + 0.7},
      ], {who: 'Homeowner', size: 39});
      k.ctx.restore();
      const ws = (window.WORDS && window.WORDS.words) || [];
      const dc = ws.find((w) => w.start >= k.S('catch.canned') && /^doesn/i.test(w.w));
      const tStamp = dc ? dc.start : k.S('catch.canned') + 3;
      if (T >= tStamp) {
        const t0 = tStamp, q = k.clamp((T - t0) / 0.18);
        k.ctx.save(); k.ctx.translate(655, 392); k.ctx.rotate(-0.08); const s = (2.2 - 1.2 * q) * 0.8; k.ctx.scale(s, s);   // on the phone's header, clear of both messages
        k.shape(k.rectPts(-230, -60, 460, 120, 0), {fill: '#1B1420', line: false, alpha: q});
        k.shape(k.rectPts(-224, -54, 448, 108, 0), {stroke: 'accent', lw: 9, line: false, alpha: q});
        k.text("Doesn't count", 0, -30, {size: 60, color: 'accent', align: 'center', alpha: q, lint: false});
        k.ctx.restore();
        k.burst(655, 392, t0 + 0.18, {n: 22, r: 300, colors: ['accent', '#9AA0AD', 'paper']});
      }
      return {hostPose: T >= tStamp ? 'shrug' : (k.talking() ? 'talk' : 'stand')};
    },

    build: (k, T) => {
      k.room('workshop');
      let cur = -1; REPLY.forEach(([id], i) => { if (T >= k.S(id)) cur = i; });
      // typed so far: whole earlier lines plus part of the current one; the bubble is laid out for the full reply
      const FULL = REPLY.map((r) => r[1]).join(' ');
      let reveal = 0;
      REPLY.forEach(([id, line], i) => { if (T < k.S(id)) return;
        const p = k.lin(k.S(id) + 0.1, k.S(id) + 0.1 + line.length * 0.035);
        reveal = REPLY.slice(0, i).reduce((a, r) => a + r[1].length + 1, 0) + Math.floor(line.length * p); });
      const typingTo = cur >= 0 ? k.S(REPLY[cur][0]) + 0.1 + REPLY[cur][1].length * 0.035 : 0;
      k.ctx.save();
      if (cur >= 0) { const q = k.clamp(k.pop(k.S(REPLY[cur][0]), 0.3), 0, 1.2); k.ctx.translate(100, 300); k.ctx.scale(q, q); k.ctx.translate(-100, -300); }
      else slideIn(k, k.S('build'), -500, 0);
      k.chip(cur >= 0 ? REPLY[cur][2] : "What I'd send", 100, 280, {size: 30, fill: cur >= 0 ? 'accent' : 'tag', color: cur >= 0 ? '#1B1420' : 'tagText'});
      k.ctx.restore();
      k.ctx.save(); slideIn(k, k.S('build') + 0.1, 0, 800);
      k.phone(100, 330, 800, 640, [
        {text: LEAD_TEXT, at: -1, ghost: T >= k.S('build.why') && T < k.S('build.time')},
        ...(T >= k.S('build.name') ? [{text: FULL, reveal, me: true, at: k.S('build.name'), typing: typingTo}] : []),
      ], {who: 'Homeowner', size: 39});
      k.ctx.restore();
      if (cur >= 0) k.burst(240, 300, k.S(REPLY[cur][0]) + 0.05, {n: 12, r: 180});
      if (T >= k.S('build.why') && T < k.S('build.time')) {
        const t0 = k.S('build.why');
        k.ctx.save(); slideIn(k, t0, 700, 0);
        k.ctx.translate(500, 590); k.ctx.rotate(-0.02); k.ctx.translate(-500, -590);
        k.panel2(150, 480, 700, 172, {fill: 'accent', border: '#1B1420'});
        k.text('Easy to answer,', 180, 496, {size: 60, color: '#1B1420'});
        k.text('and you know what to bring.', 180, 586, {size: 39, color: '#1B1420'});
        k.ctx.restore();
      }
      // the host steps back (smaller) so his head never covers the reply being typed
      return {hostPose: k.talking() ? 'talk' : 'stand', hostScale: 0.55, hostX: 150};
    },

    close: (k, T) => {
      k.room('blackboard'); boardClip(k);
      const lines = ['Fast.', 'Human.', 'One question.', 'A time.'];
      const ws = (window.WORDS && window.WORDS.words) || [];
      lines.forEach((ln, i) => {   // each word slams in as it is said
        const key = ln.replace(/[.]/g, '').split(' ')[0].toLowerCase();
        const w = ws.find((x) => x.start >= k.S('close') - 0.05 && x.w.toLowerCase().replace(/[^a-z]/g, '') === key);
        const t0 = w ? w.start : k.S('close') + i * 0.35;
        k.slam(ln, 96, 280 + i * 100, t0, {size: 120, color: i === 3 ? 'accent' : CHALK, from: 0.7});
        k.burst(120, 340 + i * 100, t0 + 0.12, {n: 8, r: 140, colors: i === 3 ? ['accent', 'accent2'] : ['paper', '#2F5A4A']});
      });
      if (T >= k.S('close.send')) {
        const t0 = k.S('close.send');
        // the brand slams onto its own row, then the send line
        const tb = t0 - 0.3;
        k.ctx.save(); k.ctx.translate(96, 690); const qb = k.clamp(k.pop(tb, 0.3), 0, 1.15); k.ctx.scale(qb, qb); k.ctx.translate(-96, -690);
        k.panel2(96, 690, 440, 80, {fill: '#24453A', border: 'accent'}); k.text('ProofNotFluff', 316, 700, {size: 60, color: 'accent', align: 'center'});
        k.ctx.restore();
        k.burst(316, 730, tb + 0.1, {n: 16});
        k.ctx.save(); slideIn(k, t0, 700, 0);
        k.panel2(330, 800, 650, 116, {fill: '#1B1420', border: 'accent'});
        k.text('Send this to whoever', 360, 816, {size: 39, color: CHALK});
        k.text('answers your phone.', 360, 862, {size: 39, color: CHALK});
        k.ctx.restore();
        k.ctx.save(); slideIn(k, t0 + 0.8, 700, 0); k.text('Exact text in the caption.', 360, 930, {size: 30, color: CHALK2}); k.ctx.restore();
      }
      k.ctx.restore();
      return {hostPose: T >= k.S('close.send') + 1.5 ? 'wave' : 'talk'};
    },
  },
};
