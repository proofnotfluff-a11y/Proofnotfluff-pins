// Scene: The first reply wins the job. One function per top-level cue in 03_cues/cues.md; numbers only from k.data.
const LEAD_TEXT = 'Hi, can you give me a quote to replace our water heater? It started leaking.';
const REPLY = [
  ['build', 'Hi [name],', 'Their name'],
  ['build.answer', 'yes, we replace water heaters.', 'Answer their question'],
  ['build.ask', 'Gas or electric?', 'One question back'],
  ['build.time', 'I can come by Thursday, 2 to 4.', 'A real time'],
];

window.SCENE = {
  look: 'clean',
  images: [],
  host_name: 'Snow',
  sections: {
    lead: (k, T) => {
      k.chip('New lead', 72, 296);
      const tp = k.p(k.S('lead.send'), k.S('lead.send') + 0.5);
      k.title('Reply in the next', 368, {size: 46, maxW: 440});
      k.title('30 minutes', 424, {size: 68, maxW: 440, color: tp > 0.5 ? 'accent' : 'ink'});
      // the reply clock (a story clock, not data): how long the lead has waited
      const t0 = k.S('lead.ladder'), mins = Math.max(0, (T - t0) * 6);
      k.label('Waiting on you', 72, 560, {size: 32, color: 'muted', weight: 700, font: 'display'});
      k.big(`${Math.floor(mins)} min`, 72, 606, {size: 96, color: mins >= 25 ? 'accent' : 'ink'});
      k.phone(520, 330, 400, 600, [{text: LEAD_TEXT, at: -1, stamp: '9:14 am'}], {who: 'Homeowner'});
      return {hostPose: k.live('lead.ladder') ? 'clip' : (k.talking() ? 'talk' : 'stand')};
    },

    why: (k, T) => {
      const n = k.data.numbers;
      // the study row
      k.chip('The study', 72, 290);
      k.text('Speed Is a Signal', 72, 350, {size: 50, weight: 700});
      k.source(`Management Science, ${n.studyYear.shown}`, 414);
      const cp = k.lin(k.S('why') + 0.8, k.S('why') + 2.2);
      k.big(k.count(n.interactions.value, cp, {dec: 1, suffix: 'M'}), 560, 330, {size: 112});
      k.label('requests on Fiverr', 562, 446, {size: 34});
      if (T >= k.S('why.hour')) {
        k.label('1 hour late: less likely to get hired', 72, 500, {size: 32, color: 'muted', weight: 700, font: 'display'});
        k.bars(72, 500, 858, [{label: '', value: n.hourDrop.value, shown: n.hourDrop.shown}], k.lin(k.S('why.hour'), k.S('why.hour') + 0.8), {bh: 56, valW: 190, vmax: 100});
        if (T >= k.S('why.hour') + 0.9) k.chip('About half', 640, 492, {size: 24, fill: 'accent', color: 'pillText'});
      }
      // the Thumbtack row
      if (T >= k.S('why.tt')) {
        const q = k.easeOut((T - k.S('why.tt')) / 0.4);
        k.ctx.save(); k.ctx.globalAlpha *= q; k.ctx.translate(0, (1 - q) * 30);
        k.shape([[72, 660], [930, 660]], {stroke: 'line', lw: 3, closed: false, line: false});
        k.chip('Thumbtack, 2025', 72, 690);
        [[0, n.ttMinutes.shown, 'accent'], [1, n.ttHours.shown, 'ink2']].forEach(([i, s, c]) => {
          const x = 72 + i * 300;
          k.card(x, 760, 270, 150, {r: 22});
          k.text(s, x + 135, 782, {size: 62, weight: 700, color: c, align: 'center'});
          k.label('to reply', x + 135, 856, {size: 30, align: 'center', color: 'muted'});
        });
        if (T >= k.S('why.more')) {
          const p = k.pop(k.S('why.more'));
          k.ctx.save(); k.ctx.translate(780, 835); k.ctx.scale(k.clamp(p, 0, 1.2), k.clamp(p, 0, 1.2)); k.ctx.translate(-780, -835);
          k.text(n.ttMore.shown, 780, 760, {size: 100, weight: 700, color: 'accent', align: 'center'});
          k.label('more likely to get hired', 780, 862, {size: 28, maxW: 260, lh: 1.1, align: 'center', color: 'ink2', weight: 700, font: 'display'});
          k.ctx.restore();
        }
        k.ctx.restore();
      }
      return {};
    },

    catch: (k, T) => {
      k.chip('The catch', 72, 290);
      k.phone(72, 350, 430, 580, [
        {text: LEAD_TEXT, at: -1},
        {text: 'Thank you for your inquiry. A representative will be in touch.', me: true, at: k.S('catch') + 0.4, stamp: 'Auto-reply'},
      ], {who: 'Homeowner'});
      if (T >= k.S('catch.auto')) {
        const q = k.pop(k.S('catch.auto'), 0.3);
        k.ctx.save(); k.ctx.translate(735, 500); k.ctx.rotate(-0.12); k.ctx.scale(1.3 - 0.3 * k.clamp(q), 1.3 - 0.3 * k.clamp(q));
        k.shape(k.rectPts(-200, -88, 400, 176, 14), {stroke: 'accent', lw: 10, line: false, alpha: k.clamp(q)});
        k.text('Sounds automated', 0, -64, {size: 52, maxW: 360, lh: 1.05, weight: 700, color: 'accent', align: 'center', caps: true, alpha: k.clamp(q), track: 0.04});
        k.ctx.restore();
      }
      const pp = k.p(k.S('catch.type'), k.S('catch.type') + 0.5);
      if (pp > 0) k.title("Here's what to type.", 680, {x: 540, maxW: 390, size: 56, alpha: pp});
      return {hostPose: k.live('catch.auto') ? 'shrug' : (k.talking() ? 'talk' : 'stand')};
    },

    build: (k, T) => {
      // which part is being typed, and the reply so far
      let cur = 0; REPLY.forEach(([id], i) => { if (T >= k.S(id)) cur = i; });
      const parts = REPLY.map(([id, line]) => {
        if (T < k.S(id)) return '';
        const p = k.lin(k.S(id) + 0.1, k.S(id) + 0.1 + line.length * 0.035);
        return p >= 1 ? line : line.slice(0, Math.floor(line.length * p));
      }).filter(Boolean);
      const text = parts.join(' ');
      k.chip(`${cur + 1} of 4: ${REPLY[cur][2]}`, 72, 290, {fill: 'accent', color: 'pillText'});
      k.phone(72, 360, 858, 470, [
        {text: LEAD_TEXT, at: -1},
        {text: text || ' ', me: true, at: k.S('build') + 0.05},
      ], {who: 'Homeowner'});
      return {hostPose: k.talking() ? 'talk' : 'stand'};
    },

    close: (k, T) => {
      k.rule('Fast. Human. One question. A time.', 520, k.S('close'), {size: 72});
      const p = k.p(k.S('close.send'), k.S('close.send') + 0.5);
      k.text('Send this to whoever answers your phone.', 540, 730, {size: 38, maxW: 860, weight: 700, color: 'ink', align: 'center', alpha: p});
      k.text('Full text in the caption.', 540, 840, {size: 32, weight: 600, font: 'body', color: 'ink2', align: 'center', alpha: p});
      k.text('ProofNotFluff', 540, 900, {size: 36, weight: 700, color: 'accent', align: 'center', alpha: p});
      return {hostPose: k.since('close.send') > 0.4 ? 'wave' : 'talk'};
    },
  },
};
