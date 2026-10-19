// node email/sender/test.js : checks the sender's logic before it touches a real inbox.
const fs = require('fs');
const S = (() => { const m = { exports: {} }; new Function('module', fs.readFileSync(__dirname + '/Code.gs', 'utf8'))(m); return m.exports; })();
let fails = 0, n = 0;
function eq(name, got, want) {
  n++;
  const g = JSON.stringify(got), w = JSON.stringify(want);
  if (g !== w) { fails++; console.log('FAIL ' + name + ': got ' + g + ' want ' + w); }
}
const b64 = t => Buffer.from(t, 'utf8').toString('base64');

// do-not-email
eq('dne exact', S.isDoNotEmail('Bob@X.com', ['bob@x.com']), true);
eq('dne domain', S.isDoNotEmail('a@bad.com', ['@bad.com']), true);
eq('dne other', S.isDoNotEmail('a@good.com', ['@bad.com', 'b@good.com']), false);
eq('dne no partial domain', S.isDoNotEmail('a@notbad.com', ['@bad.com']), false);

// ramp and caps
const s = d => ({ sender: 'leads@x.com', startDate: d, capOverride: '', paused: false });
eq('cap day 0', S.capFor(s('2026-10-26'), '2026-10-26'), 10);
eq('cap day 6', S.capFor(s('2026-10-26'), '2026-11-01'), 10);
eq('cap week 2', S.capFor(s('2026-10-26'), '2026-11-02'), 20);
eq('cap week 4+', S.capFor(s('2026-10-26'), '2026-12-30'), 40);
eq('cap before start', S.capFor(s('2026-10-26'), '2026-10-25'), 0);
eq('cap no start', S.capFor(s(''), '2026-10-26'), 0);
eq('cap paused', S.capFor({ ...s('2026-10-01'), paused: 'TRUE' }, '2026-10-26'), 0);
eq('cap override', S.capFor({ ...s('2026-10-26'), capOverride: 25 }, '2026-10-26'), 25);
eq('cap override clamped', S.capFor({ ...s('2026-10-26'), capOverride: 500 }, '2026-10-26'), S.HARD_MAX);
eq('cap override zero', S.capFor({ ...s('2026-10-01'), capOverride: 0 }, '2026-10-26'), 0);

// window
eq('mon 8am', S.inWindow(1, 8), true);
eq('fri 10am', S.inWindow(5, 10), true);
eq('mon 11am', S.inWindow(1, 11), false);
eq('mon 7am', S.inWindow(1, 7), false);
eq('sat', S.inWindow(6, 9), false);
eq('sun', S.inWindow(7, 9), false);

// spreading: a full day of runs sends exactly the cap, never more
function simulate(cap) {
  let sent = 0, maxRun = 0;
  for (let h = 8; h < 11; h++) for (let m = 0; m < 60; m += 10) {
    const k = S.quotaThisRun(cap, sent, h, m); sent += k; maxRun = Math.max(maxRun, k);
  }
  return [sent, maxRun];
}
eq('spread 10', simulate(10), [10, 1]);
eq('spread 40', simulate(40), [40, 3]);
eq('spread 50', simulate(50), [50, 3]);
eq('quota at cap', S.quotaThisRun(10, 10, 9, 0), 0);
eq('quota last run catches up', S.quotaThisRun(10, 4, 10, 50), 5);

// picking
const rows = [
  { id: 'b2', sender: 'leads@x.com', status: 'queued', sendAfter: '' },
  { id: 'a1', sender: 'LEADS@x.com', status: 'queued', sendAfter: '2026-10-26' },
  { id: 'c3', sender: 'data@x.com', status: 'queued', sendAfter: '' },
  { id: 'd4', sender: 'leads@x.com', status: 'sent', sendAfter: '' },
  { id: 'e5', sender: 'leads@x.com', status: 'queued', sendAfter: '2026-10-27' },
];
eq('pick mine, due, sorted', S.pickRows(rows, 'leads@x.com', '2026-10-26').map(r => r.id), ['a1', 'b2']);

// decide
const first = { id: 'f1', sender: 'leads@x.com', to: 'a@co.com', subject: 'Who to call', body: 'x', kind: 'first', status: 'sent', threadId: 't1', messageId: 'm1', repliedAt: '' };
const fu = { id: 'f1-fu', sender: 'leads@x.com', to: 'a@co.com', subject: 'Re', body: 'y', kind: 'followup', firstId: 'f1', status: 'queued' };
eq('first ok', S.decide({ ...first, status: 'queued' }, [], []).action, 'send');
eq('first dne', S.decide({ ...first, status: 'queued' }, [], ['@co.com']).why, 'do not email');
eq('followup ok', S.decide(fu, [first, fu], []).action, 'reply');
eq('followup after reply', S.decide(fu, [{ ...first, repliedAt: '2026-10-27' }, fu], []).why, 'they replied');
eq('followup first bounced', S.decide(fu, [{ ...first, status: 'bounced' }, fu], []).action, 'skip');
eq('followup other inbox', S.decide({ ...fu, sender: 'data@x.com' }, [first, fu], []).action, 'skip');
eq('followup no first', S.decide(fu, [fu], []).why, 'first email not found');
eq('followup dne', S.decide(fu, [first, fu], ['a@co.com']).why, 'do not email');
eq('bad kind', S.decide({ ...first, status: 'queued', kind: 'blast' }, [], []).action, 'skip');
eq('no body', S.decide({ ...first, status: 'queued', body: '' }, [], []).action, 'skip');

// bounces
eq('bounce gmail', S.parseBounce("Address not found\nYour message wasn't delivered to info@rozalado.com because the address couldn't be found."), 'info@rozalado.com');
eq('bounce dsn', S.parseBounce('Reporting-MTA: dns; googlemail.com\nFinal-Recipient: rfc822; Sales@Example.com\nAction: failed'), 'sales@example.com');
eq('bounce none', S.parseBounce('Thanks for your note, we will call you.'), '');
const br = [];
for (let i = 0; i < 40; i++) br.push({ sender: 'leads@x.com', sentAt: '2026-10-26T08:10:00', status: i < 1 ? 'bounced' : 'sent' });
eq('rate 1/40 no pause', S.shouldPause(S.bounceRate(br, 'leads@x.com', '2026-10-27')), false);
br[1].status = 'bounced';
eq('rate 2/40 pauses', S.shouldPause(S.bounceRate(br, 'leads@x.com', '2026-10-27')), true);
eq('rate small sample no pause', S.shouldPause(S.bounceRate(br.slice(0, 10).map(r => ({ ...r, status: 'bounced' })), 'leads@x.com', '2026-10-27')), false);
eq('rate old sends ignored', S.bounceRate(br, 'leads@x.com', '2026-11-20').sent, 0);

// opt-outs read only the reply's own words
eq('optout no thanks', S.isOptOut('No thanks.'), true);
eq('optout subject', S.isOptOut('unsubscribe\n'), true);
eq('optout quoted only', S.isOptOut('Sounds good, call me.\n\nOn Mon, Oct 26, 2026 at 8:10 AM ProofNotFluff wrote:\n> Reply no thanks and we will not email again.'), false);
eq('optout gt lines', S.isOptOut('Interested!\n> reply no thanks to opt out'), false);
eq('optout not interested', S.isOptOut('We are not interested'), true);

// incoming rows
const v = S.validateIncoming([
  { id: 'r1', sender: 'Leads@X.com', to: 'A@co.com', subject: 's', body: 'b', kind: 'first' },
  { id: 'r1', sender: 'leads@x.com', to: 'a@co.com', subject: 's', body: 'b', kind: 'first' },
  { id: 'r2', sender: 'leads@x.com', to: 'a@co.com', subject: 's', body: 'b', kind: 'followup' },
  { id: 'old', sender: 'leads@x.com', to: 'a@co.com', subject: 's', body: 'b', kind: 'first' },
  { id: 'r3', sender: 'leads@x.com', to: 'nope', subject: 's', body: 'b', kind: 'first' },
], { old: true });
eq('incoming ok', v.ok.map(r => [r.id, r.sender, r.to, r.status]), [['r1', 'leads@x.com', 'a@co.com', 'queued']]);
eq('incoming bad', v.bad.map(b => b.why), ['duplicate id', 'follow-up needs firstId', 'duplicate id', 'no address']);

// MIME
const mime = S.buildMime({ from: 'leads@x.com', to: 'a@co.com', subject: 'Who to call for a final clean in 60614', body: 'Hi,\nLine two é\n', inReplyTo: '<abc@mail.gmail.com>' }, b64);
const [head, bodyPart] = mime.split('\r\n\r\n');
eq('mime from', head.includes('From: "ProofNotFluff" <leads@x.com>'), true);
eq('mime subject roundtrip', Buffer.from(head.match(/=\?UTF-8\?B\?(.+)\?=/)[1], 'base64').toString(), 'Who to call for a final clean in 60614');
eq('mime threading', head.includes('In-Reply-To: <abc@mail.gmail.com>') && head.includes('References: <abc@mail.gmail.com>'), true);
eq('mime unsubscribe', head.includes('List-Unsubscribe: <mailto:leads@x.com?subject=unsubscribe>'), true);
eq('mime body roundtrip', Buffer.from(bodyPart.replace(/\r\n/g, ''), 'base64').toString(), 'Hi,\r\nLine two é\r\n');
eq('mime body lines <= 76', bodyPart.split('\r\n').every(l => l.length <= 76), true);
eq('mime no threading on first', S.buildMime({ from: 'f@x.com', to: 't@y.com', subject: 's', body: 'b' }, b64).includes('In-Reply-To'), false);

console.log((fails ? 'FAIL ' : 'PASS ') + (n - fails) + ' of ' + n + ' sender checks');
process.exit(fails ? 1 : 0);
