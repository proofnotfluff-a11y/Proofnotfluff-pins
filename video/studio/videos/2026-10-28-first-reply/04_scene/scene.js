// Scene: The first reply wins the job. One function per top-level cue in 03_cues/cues.md; numbers only from k.data.
window.SCENE = {
  look: 'clean',
  images: [],
  host_name: 'Snow',
  sections: {
    lead: (k, T) => {
      const n = k.data.numbers;
      k.chip('New lead', 72, 296);
      k.phone(500, 360, 410, 570, [
        {text: 'Hi, can you give me a quote to replace our water heater? It started leaking.', at: -1, stamp: '9:14 am'},
      ], {who: 'Homeowner'});
      // the reply clock: how long the lead has waited (a story clock, not data)
      const t0 = k.S('lead') + 0.6, mins = Math.max(0, Math.min(300, (T - t0) * (T < k.S('lead.job') ? 2 : 38)));
      const late = k.live('lead.cost');
      const label = mins < 60 ? `${Math.floor(mins)} min` : `${Math.floor(mins / 60)} hr ${String(Math.floor(mins % 60)).padStart(2, '0')}`;
      k.label('Waiting on you', 72, 420, {size: 34, color: 'muted', weight: 700, font: 'display'});
      k.big(late ? '5 hr 00' : label, 72, 470, {size: 120, color: late ? 'accent' : 'ink'});
      k.label(late ? 'and counting' : 'since they asked', 72, 610, {size: 36});
      if (late) k.spot(64, 480, 400, 118, k.S('lead.cost'), {r: 16, pad: 10});
      return {hostPose: k.live('lead.job') ? 'clip' : (k.talking() ? 'talk' : 'stand')};
    },

    study: (k, T) => {
      const n = k.data.numbers;
      k.chip('The study', 72, 290);
      k.title('Speed Is a Signal', 360, {size: 60});
      k.source(`Management Science, ${n.studyYear.shown}`, 432);
      const cp = k.lin(k.S('study') + 0.6, k.S('study') + 2.0);
      k.big(k.count(n.interactions.value, cp, {dec: 1, suffix: 'M'}), 72, 488, {size: 140});
      k.label('requests on Fiverr,', 520, 506, {size: 40, color: 'ink2'});
      k.label('the freelance site', 520, 556, {size: 40, color: 'ink2'});
      k.label('Drop in the odds of getting hired', 72, 676, {size: 32, color: 'muted', weight: 700, font: 'display'});
      if (T >= k.S('study.hour')) {
        k.bars(72, 728, 858, [{label: '1 hour late', value: n.hourDrop.value, shown: n.hourDrop.shown}], k.lin(k.S('study.hour'), k.S('study.hour') + 0.9), {bh: 60, valW: 200, vmax: 100});
        k.chip('About half', 520, 722, {size: 24, fill: 'accent', color: 'pillText'});
      }
      if (T >= k.S('study.day')) {
        k.bars(72, 860, 858, [{label: '1 day late', value: n.dayDrop.value, shown: n.dayDrop.shown, focus: true}], k.lin(k.S('study.day'), k.S('study.day') + 0.9), {bh: 60, valW: 200, vmax: 100});
      }
      return {};
    },

    tt: (k, T) => {
      const n = k.data.numbers;
      k.chip('Thumbtack, 2025', 72, 290);
      k.title('Not just freelancers', 360, {size: 60});
      const clock = (cx, cy, r, mins, color) => {
        k.shape(k.ellPts(cx, cy, r, r), {fill: 'card', stroke: color, lw: 8});
        const a = -Math.PI / 2 + (mins / 60) * Math.PI * 2;
        k.shape([[cx, cy], [cx + Math.cos(a) * r * 0.72, cy + Math.sin(a) * r * 0.72]], {stroke: color, lw: 9, closed: false, line: false});
        k.shape([[cx, cy], [cx, cy - r * 0.5]], {stroke: color, lw: 9, closed: false, line: false});
      };
      const p0 = k.pop(k.S('tt') + 0.3), p1 = k.pop(k.S('tt') + 0.6);
      [[0, n.ttMinutes.shown, 'accent', 30, p0], [1, n.ttHours.shown, 'ink2', 180, p1]].forEach(([i, s, c, m, p]) => {
        const x = 72 + i * 440;
        k.ctx.save(); k.ctx.globalAlpha *= k.clamp(p);
        k.card(x, 450, 418, 440, {r: 26});
        clock(x + 209, 590, 92, m, c);
        k.text(s, x + 209, 712, {size: 72, weight: 700, color: c, align: 'center'});
        k.label(i ? 'to reply' : 'to reply', x + 209, 800, {size: 34, align: 'center', color: 'muted'});
        k.ctx.restore();
      });
      if (T >= k.S('tt.more')) {
        const q = k.pop(k.S('tt.more'));
        k.ctx.save(); k.ctx.translate(281, 920); k.ctx.scale(0.7 + 0.3 * k.clamp(q), 0.7 + 0.3 * k.clamp(q)); k.ctx.translate(-281, -920);
        k.chip(`${n.ttMore.shown} more likely to get hired`, 72, 900, {size: 34, fill: 'accent', color: 'pillText'});
        k.ctx.restore();
      }
      return {};
    },

    catch: (k, T) => {
      k.chip('The catch', 72, 290);
      k.phone(72, 360, 430, 560, [
        {text: 'Hi, can you give me a quote to replace our water heater?', at: -1},
        {text: 'Thank you for your inquiry. A representative will be in touch.', me: true, at: k.S('catch') + 0.4, stamp: 'Auto-reply'},
      ], {who: 'Homeowner'});
      if (T >= k.S('catch.auto')) {
        const q = k.pop(k.S('catch.auto'), 0.3);
        k.ctx.save(); k.ctx.translate(735, 520); k.ctx.rotate(-0.12); k.ctx.scale(1.3 - 0.3 * k.clamp(q), 1.3 - 0.3 * k.clamp(q));
        k.shape(k.rectPts(-200, -88, 400, 176, 14), {stroke: 'accent', lw: 10, line: false, alpha: k.clamp(q)});
        k.text('Sounds automated', 0, -64, {size: 52, maxW: 360, lh: 1.05, weight: 700, color: 'accent', align: 'center', caps: true, alpha: k.clamp(q), track: 0.04});
        k.ctx.restore();
      }
      const pp = k.p(k.S('catch.person'), k.S('catch.person') + 0.6);
      if (pp > 0) k.title('Fast only works if it sounds like a person.', 680, {x: 540, maxW: 390, size: 50, alpha: pp});
      return {hostPose: k.live('catch.auto') ? 'shrug' : (k.talking() ? 'talk' : 'stand')};
    },

    reply: (k, T) => {
      k.chip('The reply', 72, 290);
      const out = T >= k.S('reply.time') ? k.easeOut((T - k.S('reply.time')) / 0.35) : 0;
      k.ctx.save(); k.ctx.globalAlpha *= 1 - out; k.ctx.translate(-out * 200, 0);
      k.checklist(72, 380, 858, [
        {text: 'Their name', at: k.S('reply') + 0.2, done: k.S('reply.name')},
        {text: 'Answer their question', at: k.S('reply') + 0.35, done: k.S('reply.answer')},
        {text: 'One question back', at: k.S('reply') + 0.5, done: k.S('reply.ask')},
        {text: 'A real time', at: k.S('reply') + 0.65, done: k.S('reply.time')},
      ], {gap: 140, size: 56});
      k.ctx.restore();
      if (T >= k.S('reply.time')) {
        const q = k.easeOut((T - k.S('reply.time')) / 0.4);
        k.ctx.save(); k.ctx.translate((1 - q) * 300, 0); k.ctx.globalAlpha *= q;
        k.phone(250, 360, 640, 470, [
          {text: 'Can you quote a new water heater?', at: -1},
          {text: 'Hi [name], yes, we replace those. Gas or electric? I can come by Thursday, 2 to 4.', me: true, at: k.S('reply.time') + 0.3},
        ], {who: 'Homeowner'});
        k.ctx.restore();
      }
      return {hostPose: k.talking() ? 'point' : 'stand', hostAt: [300, 600]};
    },

    rule: (k, T) => {
      k.rule('Fast. Human. One question. A time.', 560, k.S('rule'), {size: 74});
      const p = k.p(k.S('rule') + 1.0, k.S('rule') + 1.6);
      k.text('ProofNotFluff', 540, 780, {size: 52, weight: 700, color: 'ink', align: 'center', alpha: p});
      k.text('Next: the quote follow-up that wins it back', 540, 850, {size: 34, weight: 600, font: 'body', color: 'ink2', align: 'center', alpha: p});
      return {hostPose: k.since('rule') > 1.2 ? 'wave' : 'talk'};
    },
  },
};
