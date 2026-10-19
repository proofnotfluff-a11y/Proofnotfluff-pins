// node email/sender/test_glue.js : runs the real Apps Script glue against in-memory fakes of
// Sheets, Gmail and the clock, through a full sending day, a bounce, a reply and a follow-up.
const fs = require('fs'), vm = require('vm');
let fails = 0, n = 0;
const eq = (name, got, want) => { n++; const g = JSON.stringify(got), w = JSON.stringify(want); if (g !== w) { fails++; console.log('FAIL ' + name + ': got ' + g + ' want ' + w); } };

// ---- fake sheets
const sheets = {};
function sheet(name) {
  if (!sheets[name]) sheets[name] = { name, data: [] };
  const s = sheets[name];
  return {
    getDataRange: () => ({ getValues: () => s.data.map(r => r.slice()) }),
    getLastRow: () => s.data.length,
    appendRow: r => s.data.push(r.slice()),
    setFrozenRows: () => {},
    getRange: (row, col, nr, nc) => {
      if (typeof row === 'string') return { setNumberFormat: () => {} };
      return {
        setValue: v => { while (s.data.length < row) s.data.push([]); s.data[row - 1][col - 1] = v; },
        setValues: vals => vals.forEach((r, i) => { while (s.data.length < row + i) s.data.push([]); s.data[row - 1 + i] = r.slice(); })
      };
    }
  };
}
const ss = { getSheetByName: n => sheets[n] ? sheet(n) : null, insertSheet: n => sheet(n) };

// ---- fake clock (Chicago = UTC-5 in late Oct after... use fixed offset for the test day)
let NOW = Date.UTC(2026, 9, 26, 13, 0); // Mon Oct 26, 8:00 am CDT (UTC-5)
class FakeDate extends Date { constructor(...a) { a.length ? super(...a) : super(NOW); } static now() { return NOW; } }
function fmt(d, tz, pattern) {
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-US', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23', weekday: 'short' }).formatToParts(d).map(x => [x.type, x.value]));
  const wd = { Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6, Sun: 7 }[p.weekday];
  return pattern.replace("yyyy-MM-dd'T'HH:mm:ss", `${p.year}-${p.month}-${p.day}T${p.hour}:${p.minute}:${p.second}`)
    .replace('yyyy-MM-dd', `${p.year}-${p.month}-${p.day}`).replace(/^u$/, String(wd)).replace(/^H$/, String(+p.hour)).replace(/^m$/, String(+p.minute));
}

// ---- fake Gmail
let ME = 'leads@getproofnotfluff.com';
const sent = []; const threads = {}; let bounceInbox = [];
const Gmail = { Users: { Messages: { send: (res, uid) => {
  const raw = Buffer.from(res.raw.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf8');
  const id = 'm' + (sent.length + 1), threadId = res.threadId || 't' + (sent.length + 1);
  sent.push({ id, threadId, raw, from: ME, at: fmt(new Date(NOW), 'America/Chicago', "yyyy-MM-dd'T'HH:mm:ss") });
  (threads[threadId] = threads[threadId] || []).push({ id, from: ME, body: '', subject: '' });
  return { id, threadId };
} } } };
const msg = m => ({ getFrom: () => m.from, getPlainBody: () => m.body, getSubject: () => m.subject || '', getDate: () => new Date(NOW), getId: () => m.id, getHeader: h => h === 'Message-ID' ? '<' + m.id + '@mail.gmail.com>' : '' });
const GmailApp = {
  search: () => bounceInbox.map(b => ({ getMessages: () => [msg(b)] })),
  getThreadById: id => threads[id] ? { getId: () => id, getMessages: () => threads[id].map(msg) } : null,
  getMessageById: id => { for (const t of Object.values(threads)) for (const m of t) if (m.id === id) return msg(m); return null; }
};
const props = { SECRET: 's3cret' };
const ctx = {
  SpreadsheetApp: { getActiveSpreadsheet: () => ss, getUi: () => ({ alert: () => {}, createMenu: () => ({ addItem() { return this; }, addToUi() {} }) }) },
  PropertiesService: { getScriptProperties: () => ({ getProperty: k => props[k] || null }) },
  Session: { getEffectiveUser: () => ({ getEmail: () => ME }) },
  LockService: { getUserLock: () => ({ tryLock: () => true, releaseLock: () => {} }), getScriptLock: () => ({ waitLock: () => {}, releaseLock: () => {} }) },
  Utilities: { formatDate: fmt, sleep: () => {}, base64Encode: t => Buffer.from(t, 'utf8').toString('base64'),
    base64EncodeWebSafe: t => Buffer.from(t, 'utf8').toString('base64').replace(/\+/g, '-').replace(/\//g, '_'), Charset: { UTF_8: 'utf8' } },
  ContentService: { createTextOutput: t => ({ setMimeType() { return JSON.parse(t); } }), MimeType: { JSON: 'json' } },
  ScriptApp: { getProjectTriggers: () => [], newTrigger: () => ({ timeBased() { return this; }, everyMinutes() { return this; }, create() {} }) },
  GmailApp, Gmail, Date: FakeDate, Math, JSON, String, Number, Object, Array, RegExp, Buffer
};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(__dirname + '/Code.gs', 'utf8'), ctx);

ctx.setupSheets();
sheets.Senders.data.push([ME, '2026-10-26', '', false, '']);
sheets.Senders.data.push(['data@getproofnotfluff.com', '2026-10-26', '', false, '']);
const mk = (id, sender, to, kind, extra = {}) => ({ id, sender, to, subject: 'Who to call for a final clean in 606' + id.slice(-2), body: 'Hi,\nA real lead.\nReply no thanks and we will not email again.', kind, ...extra });
const rows = [];
for (let i = 10; i < 25; i++) rows.push(mk('2026-10-26-' + i, ME, 'owner' + i + '@co' + i + '.com', 'first'));
rows.push(mk('2026-10-26-90', 'data@getproofnotfluff.com', 'other@co90.com', 'first'));
rows.push(mk('2026-10-26-91', ME, 'blocked@bad.com', 'first'));

eq('post forbidden', ctx.doPost({ postData: { contents: JSON.stringify({ secret: 'x', rows }) } }).ok, false);
const pr = ctx.doPost({ postData: { contents: JSON.stringify({ secret: 's3cret', rows, dne: ['@bad.com'] }) } });
eq('post added', pr.added, 17);
eq('post again adds none', ctx.doPost({ postData: { contents: JSON.stringify({ secret: 's3cret', rows }) } }).added, 0);

// Sunday: nothing sends
NOW = Date.UTC(2026, 9, 25, 14, 0); ctx.runSender(); eq('sunday sends none', sent.length, 0);
// Monday 7:50 am: nothing
NOW = Date.UTC(2026, 9, 26, 12, 50); ctx.runSender(); eq('before window none', sent.length, 0);
// Monday 8:00 to 10:50, every 10 minutes
for (let t = Date.UTC(2026, 9, 26, 13, 0); t < Date.UTC(2026, 9, 26, 16, 0); t += 600000) { NOW = t; ctx.runSender(); }
eq('day 1 sends the cap of 10', sent.length, 10);
eq('all from leads@', sent.every(s => s.from === ME), true);
eq('all inside 8 to 11', sent.every(s => s.at >= '2026-10-26T08:00' && s.at < '2026-10-26T11:00'), true);
const q = () => { const [h, ...r] = sheets.Queue.data; return r.map(v => Object.fromEntries(h.map((k, i) => [k, v[i]]))); };
eq('data@ row untouched by leads@', q().find(r => r.id === '2026-10-26-90').status, 'queued');
eq('raw has subject and body', /Subject: =\?UTF-8\?B\?/.test(sent[0].raw) && sent[0].raw.includes('Content-Transfer-Encoding: base64'), true);
// 11:10 am: nothing more
NOW = Date.UTC(2026, 9, 26, 16, 10); ctx.runSender(); eq('after window none', sent.length, 10);

// a bounce and a reply come in
const r10 = q().find(r => r.id === '2026-10-26-10'), r11 = q().find(r => r.id === '2026-10-26-11'), r12 = q().find(r => r.id === '2026-10-26-12');
bounceInbox = [{ id: 'b1', from: 'mailer-daemon@googlemail.com', body: "Address not found\nYour message wasn't delivered to " + r10.to + ' because the address couldn\'t be found.' }];
threads[r11.threadId].push({ id: 'x1', from: 'Owner <' + r11.to + '>', body: 'Tell me more.\n\nOn Mon wrote:\n> Reply no thanks' });
threads[r12.threadId].push({ id: 'x2', from: r12.to, body: 'No thanks.' });
NOW = Date.UTC(2026, 9, 27, 12, 0); ctx.runSender();
eq('bounce marked', q().find(r => r.id === r10.id).status, 'bounced');
eq('bounce on do-not-email', sheets.DoNotEmail.data.some(r => r[0] === r10.to), true);
eq('reply marked', q().find(r => r.id === r11.id).note, 'replied');
eq('reply not an opt-out', sheets.DoNotEmail.data.some(r => r[0] === r11.to), false);
eq('opt-out marked and blocked', [q().find(r => r.id === r12.id).note, sheets.DoNotEmail.data.some(r => r[0] === r12.to)], ['opt-out', true]);

// follow-ups: to r11 (replied), r12 (opted out), r13 (ok), r10 (bounced)
const fus = [r10, r11, r12, q().find(r => r.id === '2026-10-26-13')].map(r => ({ id: r.id + '-fu', sender: ME, to: r.to, subject: 'x', body: 'Quick follow-up.', kind: 'followup', firstId: r.id, sendAfter: '2026-11-02' }));
eq('follow-ups added', ctx.doPost({ postData: { contents: JSON.stringify({ secret: 's3cret', rows: fus }) } }).added, 4);
// Tue Oct 27: 5 firsts left in queue, cap 10; follow-ups not due yet
const before = sent.length;
for (let t = Date.UTC(2026, 9, 27, 13, 0); t < Date.UTC(2026, 9, 27, 16, 0); t += 600000) { NOW = t; ctx.runSender(); }
eq('day 2 sends the 5 remaining firsts', sent.length - before, 5);
eq('blocked skipped when reached', q().find(r => r.id === '2026-10-26-91').status, 'skipped');
eq('no follow-up before its date', q().filter(r => r.kind === 'followup').every(r => r.status === 'queued'), true);
// Mon Nov 2: week 2, follow-ups due
const b2 = sent.length;
for (let t = Date.UTC(2026, 10, 2, 14, 0); t < Date.UTC(2026, 10, 2, 17, 0); t += 600000) { NOW = t; ctx.runSender(); }
const fq = Object.fromEntries(q().filter(r => r.kind === 'followup').map(r => [r.firstId.slice(-2), [r.status, r.note]]));
eq('follow-up statuses', fq, { '10': ['skipped', 'do not email'], '11': ['skipped', 'they replied'], '12': ['skipped', 'do not email'], '13': ['sent', ''] });
const fuSent = sent[sent.length - 1];
eq('follow-up in first thread', fuSent.threadId, r13Thread = q().find(r => r.id === '2026-10-26-13').threadId);
eq('follow-up threading headers', fuSent.raw.includes('In-Reply-To: <' + q().find(r => r.id === '2026-10-26-13').messageId + '@mail.gmail.com>'), true);
eq('follow-up Re: subject', Buffer.from(fuSent.raw.match(/=\?UTF-8\?B\?(.+)\?=/)[1], 'base64').toString().startsWith('Re: Who to call'), true);
eq('only one email sent Nov 2', sent.length - b2, 1);

// status read-back
const g = ctx.doGet({ parameter: { secret: 's3cret', since: '2026-10-26' } });
eq('doGet ok', [g.ok, g.rows.length > 0, g.dne.length >= 3], [true, true, true]);
eq('doGet forbidden', ctx.doGet({ parameter: { secret: 'no' } }).ok, false);

// dry run sends nothing but logs
props.DRY_RUN = 'true'; ME = 'data@getproofnotfluff.com'; const b3 = sent.length;
NOW = Date.UTC(2026, 10, 3, 14, 0); ctx.runSender();
eq('dry run sends nothing', [sent.length - b3, q().find(r => r.id === '2026-10-26-90').status], [0, 'dry-run']);

console.log((fails ? 'FAIL ' : 'PASS ') + (n - fails) + ' of ' + n + ' glue checks');
process.exit(fails ? 1 : 0);
