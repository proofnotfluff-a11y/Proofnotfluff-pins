// Scene: The first reply wins the job (v2, arcade). One function per top-level cue in 03_cues/cues.md.
// Numbers only from k.data (brief.md -> data.js). Rooms: framing, blackboard, workshop, garage.
const LEAD_TEXT = 'Can you quote a new water heater? Ours is leaking.';
const REPLY = [
  ['build.name', 'Hi [name],', '1 of 4: their name'],
  ['build.answer', 'yes, we replace water heaters.', '2 of 4: answer it'],
  ['build.ask', 'Gas or electric?', '3 of 4: one question'],
  ['build.time', 'I can come by Thursday, 2 to 4.', '4 of 4: a real time'],
];
const CHALK = '#FFF7EA', CHALK2 = '#F7C873';

window.SCENE = {
  look: 'arcade',
  images: [],
  host_name: 'Snow',
  sections: {
    lead: (k, T) => {
      k.room('framing');
      k.chip('New lead', 72, 280, {size: 30});
      k.phone(470, 300, 460, 640, [{text: LEAD_TEXT, at: -1, stamp: '9:14 am'}], {who: 'Homeowner', size: 39});
      // the ladder slides in, and the reply clock starts (a story clock, not data)
      if (T >= k.S('lead.ladder')) {
        const q = k.easeOut((T - k.S('lead.ladder')) / 0.5), lx = 330 - (1 - q) * 300;
        for (const x of [lx, lx + 84]) k.shape(k.rectPts(x, 560, 18, 690, 0), {fill: '#B07A47', line: false});
        for (let y = 600; y < 1240; y += 84) k.shape(k.rectPts(lx, y, 102, 14, 0), {fill: '#D9A066', line: false});
      }
      const mins = Math.max(0, (T - k.S('lead.ladder')) * 7);
      k.panel2(72, 400, 360, 160, {title: 'Waiting on you'});
      k.text(`${Math.floor(mins)} min`, 252, 446, {size: 100, color: mins > 20 ? 'accent' : 'ink', align: 'center'});
      if (T >= k.S('lead.show')) {
        const q = k.pop(k.S('lead.show'));
        k.ctx.save(); k.ctx.translate(252, 670); k.ctx.scale(k.clamp(q, 0, 1.1), k.clamp(q, 0, 1.1)); k.ctx.translate(-252, -670);
        k.panel2(72, 610, 360, 130, {fill: 'accent', border: '#1B1420'});
        k.text('Tonight is', 252, 628, {size: 39, color: '#1B1420', align: 'center'});
        k.text('too late.', 252, 672, {size: 60, color: '#1B1420', align: 'center'});
        k.ctx.restore();
      }
      return {hostPose: k.live('lead.ladder') ? 'clip' : (k.talking() ? 'talk' : 'stand')};
    },

    study: (k, T) => {
      const n = k.data.numbers;
      k.room('blackboard');
      k.text('The study', 96, 280, {size: 60, color: CHALK2});
      k.text('"Speed Is a Signal"', 96, 352, {size: 39, color: CHALK});
      k.text(`Management Science, ${n.studyYear.shown}`, 96, 398, {size: 39, color: '#C9CCD3'});
      if (T >= k.S('study.count')) {
        k.text(k.count(n.interactions.value, k.lin(k.S('study.count'), k.S('study.count') + 1.2), {dec: 1, suffix: 'M'}), 96, 470, {size: 120, color: CHALK});
        k.text('requests on Fiverr', 470, 500, {size: 39, color: CHALK});
      }
      const bar = (y, label, v, shown, t0, hot) => {
        if (T < t0) return;
        const p = k.easeOut((T - t0) / 0.7);
        k.text(label, 96, y, {size: 39, color: CHALK});
        k.shape(k.rectPts(96, y + 50, 600, 48, 0), {stroke: CHALK, lw: 6, line: false});
        k.shape(k.rectPts(96, y + 50, 600 * (v / 100) * p, 48, 0), {fill: hot ? 'accent' : CHALK, line: false});
        if (p > 0.6) k.text(`${shown} less`, 720, y + 50, {size: 39, color: hot ? 'accent' : CHALK});
      };
      bar(610, '1 hour late: about half as likely', n.hourDrop.value, n.hourDrop.shown, k.S('study.hour'), false);
      bar(740, '1 day late:', n.dayDrop.value, n.dayDrop.shown, k.S('study.day'), true);
      return {};
    },

    signal: (k, T) => {
      k.room('blackboard');
      k.text('Why it works', 96, 280, {size: 60, color: CHALK2});
      const a = k.p(k.S('signal') + 0.6, k.S('signal') + 1.4);
      k.text('Your reply speed tells them', 96, 400, {size: 39, color: CHALK, alpha: a});
      k.text('how you\'ll treat them later.', 96, 450, {size: 60, color: CHALK, alpha: a});
      if (T >= k.S('signal.alone')) {
        const b = k.p(k.S('signal.alone'), k.S('signal.alone') + 0.6);
        k.text('It helped on its own:', 96, 620, {size: 39, color: CHALK2, alpha: b});
        k.text('same work, same message,', 96, 676, {size: 39, color: CHALK, alpha: b});
        k.text('faster reply still won.', 96, 726, {size: 39, color: CHALK, alpha: b});
        k.shape([[96, 790], [96 + 560 * b, 790]], {stroke: 'accent', lw: 9, closed: false, line: false});
      }
      return {hostPose: k.talking() ? 'point' : 'stand', hostAt: [400, 480]};
    },

    tt: (k, T) => {
      const n = k.data.numbers;
      k.room('workshop');
      k.panel2(72, 300, 858, 560, {title: 'Thumbtack, 2025'});
      k.text('Time to reply, and who got hired', 112, 350, {size: 39, color: 'ink'});
      const clock = (cx, cy, r, mins, c) => {
        k.shape(k.ellPts(cx, cy, r, r, 20), {fill: '#2B2033', stroke: c, lw: 9, line: false});
        const ang = -Math.PI / 2 + (mins / 60) * Math.PI * 2;
        k.shape([[cx, cy], [cx + Math.cos(ang) * r * 0.7, cy + Math.sin(ang) * r * 0.7]], {stroke: c, lw: 9, closed: false, line: false});
        k.shape([[cx, cy], [cx, cy - r * 0.5]], {stroke: c, lw: 9, closed: false, line: false});
      };
      clock(260, 540, 90, 30, 'accent'); clock(640, 540, 90, 180, '#9AA0AD');
      k.text(n.ttMinutes.shown, 260, 660, {size: 60, color: 'accent', align: 'center'});
      k.text(n.ttHours.shown, 640, 660, {size: 60, color: '#C9CCD3', align: 'center'});
      k.text('to reply', 260, 726, {size: 39, color: 'muted', align: 'center'});
      k.text('to reply', 640, 726, {size: 39, color: 'muted', align: 'center'});
      if (T >= k.S('tt.more')) {
        const q = k.pop(k.S('tt.more'));
        k.ctx.save(); k.ctx.translate(500, 800); k.ctx.scale(k.clamp(q, 0, 1.15), k.clamp(q, 0, 1.15)); k.ctx.translate(-500, -800);
        k.panel2(112, 774, 778, 72, {fill: 'accent', border: '#1B1420'});
        k.text(`${n.ttMore.shown} more likely to get hired`, 501, 788, {size: 39, color: '#1B1420', align: 'center'});
        k.ctx.restore();
      }
      return {};
    },

    catch: (k, T) => {
      k.room('garage');
      k.chip('The catch', 72, 280, {size: 30});
      k.phone(400, 300, 530, 660, [
        {text: LEAD_TEXT, at: -1},
        {text: 'Thank you for your inquiry. A representative will be in touch.', me: true, at: k.S('catch') + 0.5, stamp: 'auto-reply'},
      ], {who: 'Homeowner', size: 39});
      if (T >= k.S('catch.canned')) {
        const q = k.pop(k.S('catch.canned'), 0.3);
        k.ctx.save(); k.ctx.translate(665, 905); k.ctx.rotate(-0.1); k.ctx.scale(1.3 - 0.3 * k.clamp(q), 1.3 - 0.3 * k.clamp(q));
        k.shape(k.rectPts(-230, -60, 460, 120, 0), {fill: '#1B1420', line: false, alpha: k.clamp(q)});
        k.shape(k.rectPts(-224, -54, 448, 108, 0), {stroke: 'accent', lw: 9, line: false, alpha: k.clamp(q)});
        k.text("Doesn't count", 0, -30, {size: 60, color: 'accent', align: 'center', alpha: k.clamp(q)});
        k.ctx.restore();
      }
      return {hostPose: k.live('catch.canned') ? 'shrug' : (k.talking() ? 'talk' : 'stand')};
    },

    build: (k, T) => {
      k.room('workshop');
      let cur = -1; REPLY.forEach(([id], i) => { if (T >= k.S(id)) cur = i; });
      const parts = REPLY.map(([id, line]) => {
        if (T < k.S(id)) return '';
        const p = k.lin(k.S(id) + 0.1, k.S(id) + 0.1 + line.length * 0.035);
        return p >= 1 ? line : line.slice(0, Math.floor(line.length * p));
      }).filter(Boolean);
      const typingTo = cur >= 0 ? k.S(REPLY[cur][0]) + 0.1 + REPLY[cur][1].length * 0.035 : 0;
      k.chip(cur >= 0 ? REPLY[cur][2] : "What I'd send", 72, 280, {size: 30, fill: cur >= 0 ? 'accent' : 'tag', color: cur >= 0 ? '#1B1420' : 'tagText'});
      k.phone(72, 330, 858, 640, [
        {text: LEAD_TEXT, at: -1},
        ...(parts.length ? [{text: parts.join(' '), me: true, at: k.S('build.name'), typing: typingTo}] : []),
      ], {who: 'Homeowner', size: 39});
      if (T >= k.S('build.why') && T < k.S('build.time')) {
        const q = k.p(k.S('build.why'), k.S('build.why') + 0.4);
        k.panel2(380, 350, 550, 120, {fill: '#2B2033', border: 'accent'});
        k.text('Easy to answer, and you', 410, 368, {size: 39, color: 'ink', alpha: q});
        k.text('know what to bring.', 410, 414, {size: 39, color: 'accent', alpha: q});
      }
      return {hostPose: k.talking() ? 'talk' : 'stand'};
    },

    close: (k, T) => {
      k.room('blackboard');
      const lines = ['Fast.', 'Human.', 'One question.', 'A time.'];
      lines.forEach((ln, i) => {
        const t0 = k.S('close') + i * 0.35; if (T < t0) return;
        k.text(ln, 96, 300 + i * 120, {size: 120, color: i === 3 ? 'accent' : CHALK});
      });
      if (T >= k.S('close.send')) {
        const p = k.p(k.S('close.send'), k.S('close.send') + 0.5);
        k.text('Send this to whoever', 380, 800, {size: 39, color: CHALK2, alpha: p});
        k.text('answers your phone.', 380, 846, {size: 39, color: CHALK2, alpha: p});
        k.text('Exact text in the caption.', 380, 920, {size: 39, color: '#C9CCD3', alpha: p});
      }
      return {hostPose: k.since('close') > 1.2 && T >= k.S('close.send') + 1.5 ? 'wave' : 'talk'};
    },
  },
};
