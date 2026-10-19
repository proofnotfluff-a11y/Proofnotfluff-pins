/**
 * ProofNotFluff sender (Google Apps Script, bound to the "PNF send queue" Google Sheet).
 *
 * One script, one shared sheet. Each sending inbox opens the sheet once and clicks
 * ProofNotFluff > Start sending: that installs a 10-minute trigger that runs as that
 * inbox, so it sends only its own rows, from its own Gmail.
 *
 * Sheets (made by setupSheets):
 *   Queue     one row per email. Filled by the leads desk through the web app (doPost).
 *   Senders   one row per inbox: start date (drives the ramp), cap override, paused.
 *   DoNotEmail addresses or @domains that are never emailed again (bounces, opt-outs).
 *   Log       one line per run per inbox.
 *
 * Safety: weekdays only, inside the sending window (Chicago time); per-inbox daily cap from
 * the ramp, never above HARD_MAX; a few emails per run with a random pause between them;
 * do-not-email checked right before every send; a follow-up goes only into its first
 * email's thread and never after a reply; an inbox pauses itself when its bounce rate
 * passes BOUNCE_PAUSE; DRY_RUN in Script Properties logs without sending.
 */

var TZ = 'America/Chicago';
var HARD_MAX = 50;                 // per inbox per day, whatever the sheet says
var RAMP = [10, 20, 30, 40];       // per inbox per day, by week since its start date
var WINDOW = { start: 8, end: 11 }; // 8:00 to 10:59 am Chicago, weekdays
var RUN_EVERY_MIN = 10;
var MAX_PER_RUN = 5;
var BOUNCE_PAUSE = 0.03;           // pause the inbox above 3% bounces...
var BOUNCE_MIN_SENT = 20;          // ...once it has sent at least this many in the look-back
var BOUNCE_LOOKBACK_DAYS = 7;
var FROM_NAME = 'ProofNotFluff';
var OPT_OUT_RE = /\b(no thanks|no thank you|unsubscribe|remove me|take me off|stop emailing|opt[ -]?out|not interested)\b/i;

var COLS = ['id', 'sender', 'to', 'subject', 'body', 'kind', 'firstId', 'sendAfter',
  'status', 'sentAt', 'messageId', 'threadId', 'repliedAt', 'note'];
var SENDER_COLS = ['sender', 'startDate', 'capOverride', 'paused', 'note'];

/* ---------------- pure logic (tested in Node: email/sender/test.js) ---------------- */

function lower(s) { return String(s || '').trim().toLowerCase(); }

function isDoNotEmail(address, dneList) {
  var a = lower(address);
  var dom = a.indexOf('@') >= 0 ? a.slice(a.indexOf('@')) : '';
  for (var i = 0; i < dneList.length; i++) {
    var d = lower(dneList[i]);
    if (!d) continue;
    if (d === a) return true;
    if (d.charAt(0) === '@' && d === dom) return true;
  }
  return false;
}

/** Days between two YYYY-MM-DD strings (b - a). */
function dayDiff(a, b) {
  var pa = a.split('-'), pb = b.split('-');
  var ta = Date.UTC(+pa[0], +pa[1] - 1, +pa[2]);
  var tb = Date.UTC(+pb[0], +pb[1] - 1, +pb[2]);
  return Math.round((tb - ta) / 86400000);
}

/** Today's cap for an inbox. A blank start date means not started: 0. */
function capFor(sender, today) {
  if (!sender || String(sender.paused).toUpperCase() === 'TRUE' || sender.paused === true) return 0;
  var override = Number(sender.capOverride);
  if (sender.capOverride !== '' && sender.capOverride != null && !isNaN(override)) {
    return Math.max(0, Math.min(HARD_MAX, Math.floor(override)));
  }
  if (!sender.startDate) return 0;
  var d = dayDiff(String(sender.startDate).slice(0, 10), today);
  if (d < 0) return 0;
  var week = Math.floor(d / 7);
  return Math.min(HARD_MAX, RAMP[Math.min(week, RAMP.length - 1)]);
}

/** Is this local time (weekday 1-7 Mon..Sun, hour 0-23) inside the sending window? */
function inWindow(weekday, hour) {
  return weekday >= 1 && weekday <= 5 && hour >= WINDOW.start && hour < WINDOW.end;
}

/** Runs left today including this one, given local hour and minute. */
function runsLeft(hour, minute) {
  var minsLeft = (WINDOW.end - hour) * 60 - minute;
  return Math.max(1, Math.ceil(minsLeft / RUN_EVERY_MIN));
}

/** How many to send this run: spread what is left of the cap over the runs left. */
function quotaThisRun(cap, sentToday, hour, minute) {
  var left = cap - sentToday;
  if (left <= 0) return 0;
  return Math.min(MAX_PER_RUN, left, Math.ceil(left / runsLeft(hour, minute)));
}

/** Rows this inbox may send now, oldest id first. */
function pickRows(rows, me, today) {
  var mine = rows.filter(function (r) {
    return lower(r.sender) === lower(me) && r.status === 'queued' &&
      (!r.sendAfter || String(r.sendAfter).slice(0, 10) <= today);
  });
  mine.sort(function (a, b) { return String(a.id) < String(b.id) ? -1 : String(a.id) > String(b.id) ? 1 : 0; });
  return mine;
}

/** Decide what to do with one row. Returns {action:'send'|'reply'|'skip', why, first}. */
function decide(row, rows, dneList) {
  if (!row.to || String(row.to).indexOf('@') < 0) return { action: 'skip', why: 'no address' };
  if (isDoNotEmail(row.to, dneList)) return { action: 'skip', why: 'do not email' };
  if (!row.subject || !row.body) return { action: 'skip', why: 'missing subject or body' };
  if (row.kind === 'followup') {
    var first = null;
    for (var i = 0; i < rows.length; i++) if (String(rows[i].id) === String(row.firstId)) first = rows[i];
    if (!first) return { action: 'skip', why: 'first email not found' };
    if (first.status !== 'sent' || !first.threadId || !first.messageId) return { action: 'skip', why: 'first email not sent (' + first.status + ')' };
    if (lower(first.sender) !== lower(row.sender)) return { action: 'skip', why: 'follow-up must come from the first email\'s inbox' };
    if (first.repliedAt) return { action: 'skip', why: 'they replied' };
    return { action: 'reply', first: first };
  }
  if (row.kind !== 'first') return { action: 'skip', why: 'unknown kind ' + row.kind };
  return { action: 'send' };
}

/** Pull the failed address out of a Gmail bounce message body, or ''. */
function parseBounce(body) {
  var t = String(body || '');
  var pats = [
    /wasn't delivered to\s+([^\s<>"']+@[^\s<>"']+)/i,
    /Final-Recipient:\s*rfc822;\s*([^\s<>"']+@[^\s<>"']+)/i,
    /Original-Recipient:\s*rfc822;\s*([^\s<>"']+@[^\s<>"']+)/i,
    /delivery to the following recipient[s]? failed[^\n]*\n\s*([^\s<>"']+@[^\s<>"']+)/i,
    /<([^\s<>"']+@[^\s<>"']+)>:?\s*(?:host|recipient address rejected|user unknown|mailbox unavailable)/i
  ];
  for (var i = 0; i < pats.length; i++) {
    var m = t.match(pats[i]);
    if (m) return lower(m[1].replace(/[.,;]+$/, ''));
  }
  return '';
}

/** Bounce rate for an inbox over its recent sends. */
function bounceRate(rows, me, today) {
  var sent = 0, bounced = 0;
  rows.forEach(function (r) {
    if (lower(r.sender) !== lower(me) || !r.sentAt) return;
    if (dayDiff(String(r.sentAt).slice(0, 10), today) > BOUNCE_LOOKBACK_DAYS) return;
    if (r.status === 'sent' || r.status === 'bounced') sent++;
    if (r.status === 'bounced') bounced++;
  });
  return { sent: sent, bounced: bounced, rate: sent ? bounced / sent : 0 };
}

function shouldPause(br) { return br.sent >= BOUNCE_MIN_SENT && br.rate > BOUNCE_PAUSE; }

function isOptOut(text) {
  // Only the reply's own words: drop quoted lines and everything after "On ... wrote:".
  var own = String(text || '').split(/\nOn .{0,200}wrote:/)[0]
    .split('\n').filter(function (l) { return l.trim().charAt(0) !== '>'; }).join('\n');
  return OPT_OUT_RE.test(own);
}

/** Plain-text MIME message for the Gmail API. b64 encodes a UTF-8 string to standard base64. */
function buildMime(f, b64) {
  var lines = [
    'From: "' + FROM_NAME + '" <' + f.from + '>',
    'To: ' + f.to,
    'Subject: =?UTF-8?B?' + b64(f.subject) + '?=',
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset="UTF-8"',
    'Content-Transfer-Encoding: base64',
    'List-Unsubscribe: <mailto:' + f.from + '?subject=unsubscribe>'
  ];
  if (f.inReplyTo) { lines.push('In-Reply-To: ' + f.inReplyTo); lines.push('References: ' + f.inReplyTo); }
  var body = b64(String(f.body).replace(/\r?\n/g, '\r\n')).replace(/(.{76})/g, '$1\r\n');
  return lines.join('\r\n') + '\r\n\r\n' + body;
}

/** Validate rows arriving through the web app. Returns {ok:[...], bad:[{id,why}]}. */
function validateIncoming(list, existingIds) {
  var ok = [], bad = [], seen = {};
  (list || []).forEach(function (r) {
    var id = String(r && r.id || '');
    var why = '';
    if (!id) why = 'no id';
    else if (existingIds[id] || seen[id]) why = 'duplicate id';
    else if (!r.sender || String(r.sender).indexOf('@') < 0) why = 'no sender';
    else if (!r.to || String(r.to).indexOf('@') < 0) why = 'no address';
    else if (r.kind !== 'first' && r.kind !== 'followup') why = 'kind must be first or followup';
    else if (r.kind === 'followup' && !r.firstId) why = 'follow-up needs firstId';
    else if (!r.subject || !r.body) why = 'missing subject or body';
    if (why) { bad.push({ id: id, why: why }); return; }
    seen[id] = true;
    ok.push({ id: id, sender: lower(r.sender), to: lower(r.to), subject: String(r.subject), body: String(r.body),
      kind: r.kind, firstId: String(r.firstId || ''), sendAfter: String(r.sendAfter || ''), status: 'queued',
      sentAt: '', messageId: '', threadId: '', repliedAt: '', note: '' });
  });
  return { ok: ok, bad: bad };
}

/* ---------------- Apps Script glue ---------------- */

function ss_() { return SpreadsheetApp.getActiveSpreadsheet() || SpreadsheetApp.openById(PropertiesService.getScriptProperties().getProperty('SHEET_ID')); }

function readTable_(name, cols) {
  var sh = ss_().getSheetByName(name);
  var vals = sh.getDataRange().getValues();
  var head = vals[0].map(String), out = [];
  for (var i = 1; i < vals.length; i++) {
    var o = { _row: i + 1 };
    cols.forEach(function (c) {
      var j = head.indexOf(c), v = j >= 0 ? vals[i][j] : '';
      if (v instanceof Date) v = Utilities.formatDate(v, TZ, "yyyy-MM-dd'T'HH:mm:ss");
      o[c] = v === null ? '' : v;
    });
    if (o[cols[0]] !== '') out.push(o);
  }
  return { sheet: sh, head: head, rows: out };
}

function setCells_(t, row, fields) {
  Object.keys(fields).forEach(function (k) {
    var j = t.head.indexOf(k);
    if (j >= 0) t.sheet.getRange(row._row, j + 1).setValue(fields[k]);
    row[k] = fields[k];
  });
}

function dneList_() {
  var sh = ss_().getSheetByName('DoNotEmail');
  return sh.getDataRange().getValues().slice(1).map(function (r) { return String(r[0]); }).filter(String);
}

function addDne_(address, why) {
  if (isDoNotEmail(address, dneList_())) return;
  ss_().getSheetByName('DoNotEmail').appendRow([lower(address), why, nowIso_()]);
}

function nowIso_() { return Utilities.formatDate(new Date(), TZ, "yyyy-MM-dd'T'HH:mm:ss"); }
function today_() { return Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd'); }
function b64_(t) { return Utilities.base64Encode(t, Utilities.Charset.UTF_8); }
function me_() { return lower(Session.getEffectiveUser().getEmail()); }
function dryRun_() { return PropertiesService.getScriptProperties().getProperty('DRY_RUN') === 'true'; }

function log_(me, text) {
  ss_().getSheetByName('Log').appendRow([nowIso_(), me, text]);
}

/** The 10-minute trigger. */
function runSender() {
  var lock = LockService.getUserLock();
  if (!lock.tryLock(1000)) return;
  try {
    var me = me_();
    var now = new Date();
    var weekday = Number(Utilities.formatDate(now, TZ, 'u'));
    var hour = Number(Utilities.formatDate(now, TZ, 'H'));
    var minute = Number(Utilities.formatDate(now, TZ, 'm'));
    var today = today_();

    var q = readTable_('Queue', COLS);
    checkBounces_(me, q);
    checkReplies_(me, q);
    if (!inWindow(weekday, hour)) return;

    var st = readTable_('Senders', SENDER_COLS);
    var sender = st.rows.filter(function (s) { return lower(s.sender) === me; })[0];
    if (!sender) { log_(me, 'not in Senders sheet, nothing sent'); return; }

    var br = bounceRate(q.rows, me, today);
    if (shouldPause(br) && String(sender.paused).toUpperCase() !== 'TRUE') {
      setCells_(st, sender, { paused: true, note: 'auto-paused ' + today + ': ' + br.bounced + ' of ' + br.sent + ' bounced' });
      log_(me, 'auto-paused for bounces ' + br.bounced + '/' + br.sent);
      return;
    }

    var cap = capFor(sender, today);
    var sentToday = q.rows.filter(function (r) {
      return lower(r.sender) === me && r.sentAt && String(r.sentAt).slice(0, 10) === today &&
        (r.status === 'sent' || r.status === 'bounced' || r.status === 'dry-run');
    }).length;
    var n = quotaThisRun(cap, sentToday, hour, minute);
    if (n <= 0) return;

    var dne = dneList_();
    var picked = pickRows(q.rows, me, today), done = 0;
    for (var i = 0; i < picked.length && done < n; i++) {
      var r = picked[i];
      var d = decide(r, q.rows, dne);
      if (d.action === 'skip') { setCells_(q, r, { status: 'skipped', note: d.why }); continue; }
      if (done > 0) Utilities.sleep(20000 + Math.floor(Math.random() * 25000));
      try {
        if (dryRun_()) {
          setCells_(q, r, { status: 'dry-run', sentAt: nowIso_(), note: d.action });
        } else {
          var mime = { from: me, to: r.to, subject: r.subject, body: r.body };
          var threadId = '';
          if (d.action === 'reply') {
            var firstMsg = GmailApp.getMessageById(d.first.messageId);
            mime.inReplyTo = firstMsg.getHeader('Message-ID');
            mime.subject = /^re:/i.test(d.first.subject) ? d.first.subject : 'Re: ' + d.first.subject;
            threadId = d.first.threadId;
          }
          var raw = Utilities.base64EncodeWebSafe(buildMime(mime, b64_), Utilities.Charset.UTF_8);
          var res = Gmail.Users.Messages.send(threadId ? { raw: raw, threadId: threadId } : { raw: raw }, 'me');
          setCells_(q, r, { status: 'sent', sentAt: nowIso_(), messageId: res.id, threadId: res.threadId });
        }
        done++;
      } catch (e) {
        setCells_(q, r, { status: 'error', note: String(e).slice(0, 200) });
        log_(me, 'error on ' + r.id + ': ' + String(e).slice(0, 200));
        break; // stop this run on any send error (quota, auth); the next run retries nothing automatically
      }
    }
    log_(me, 'cap ' + cap + ', sent today ' + (sentToday + done) + ', this run ' + done);
  } finally {
    lock.releaseLock();
  }
}

function checkBounces_(me, q) {
  var threads = GmailApp.search('from:(mailer-daemon OR postmaster) newer_than:3d', 0, 50);
  threads.forEach(function (t) {
    t.getMessages().forEach(function (m) {
      var addr = parseBounce(m.getPlainBody());
      if (!addr) return;
      q.rows.forEach(function (r) {
        if (lower(r.sender) === me && lower(r.to) === addr && r.status === 'sent') {
          setCells_(q, r, { status: 'bounced', note: 'bounce ' + Utilities.formatDate(m.getDate(), TZ, 'yyyy-MM-dd') });
          addDne_(addr, 'bounced');
        }
      });
    });
  });
}

function checkReplies_(me, q) {
  var today = today_(), checked = 0;
  q.rows.forEach(function (r) {
    if (checked >= 60) return;
    if (lower(r.sender) !== me || r.status !== 'sent' || !r.threadId || r.repliedAt || r.kind !== 'first') return;
    if (dayDiff(String(r.sentAt).slice(0, 10), today) > 21) return;
    checked++;
    var t = GmailApp.getThreadById(r.threadId);
    if (!t) return;
    t.getMessages().forEach(function (m) {
      if (r.repliedAt) return;
      var from = lower(m.getFrom());
      if (from.indexOf(me) >= 0 || /mailer-daemon|postmaster/.test(from)) return;
      var opt = isOptOut(m.getSubject() + '\n' + m.getPlainBody());
      setCells_(q, r, { repliedAt: Utilities.formatDate(m.getDate(), TZ, "yyyy-MM-dd'T'HH:mm:ss"), note: opt ? 'opt-out' : 'replied' });
      if (opt) addDne_(r.to, 'opted out');
    });
  });
}

/* ---------------- web app (deployed once, from the leads@ inbox) ---------------- */

function secretOk_(s) {
  var want = PropertiesService.getScriptProperties().getProperty('SECRET');
  return want && s && String(s) === want;
}

function json_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

/** POST {secret, rows:[...]} adds queue rows. POST {secret, dne:[...]} adds do-not-email entries. */
function doPost(e) {
  var body = {};
  try { body = JSON.parse(e.postData.contents); } catch (x) { return json_({ ok: false, error: 'bad json' }); }
  if (!secretOk_(body.secret)) return json_({ ok: false, error: 'forbidden' });
  var lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    var q = readTable_('Queue', COLS), ids = {};
    q.rows.forEach(function (r) { ids[String(r.id)] = true; });
    var v = validateIncoming(body.rows || [], ids);
    if (v.ok.length) {
      var vals = v.ok.map(function (r) { return COLS.map(function (c) { return r[c]; }); });
      q.sheet.getRange(q.sheet.getLastRow() + 1, 1, vals.length, COLS.length).setValues(vals);
    }
    (body.dne || []).forEach(function (a) { addDne_(a, 'from CRM'); });
    return json_({ ok: true, added: v.ok.length, rejected: v.bad });
  } finally { lock.releaseLock(); }
}

/** GET ?secret=...&since=YYYY-MM-DD returns status of rows touched since that date. */
function doGet(e) {
  var p = (e && e.parameter) || {};
  if (!secretOk_(p.secret)) return json_({ ok: false, error: 'forbidden' });
  var since = String(p.since || '0000');
  var q = readTable_('Queue', COLS);
  var out = q.rows.filter(function (r) {
    return String(r.sentAt) >= since || String(r.repliedAt) >= since || r.status === 'queued' || r.status === 'error' || r.status === 'skipped';
  }).map(function (r) {
    return { id: r.id, sender: r.sender, to: r.to, status: r.status, sentAt: r.sentAt, repliedAt: r.repliedAt, threadId: r.threadId, note: r.note };
  });
  return json_({ ok: true, rows: out, dne: dneList_() });
}

/* ---------------- menu and setup ---------------- */

function onOpen() {
  SpreadsheetApp.getUi().createMenu('ProofNotFluff')
    .addItem('Start sending from this inbox', 'startSending')
    .addItem('Stop sending from this inbox', 'stopSending')
    .addToUi();
}

function setupSheets() {
  var ss = ss_();
  [['Queue', COLS], ['Senders', SENDER_COLS], ['DoNotEmail', ['address', 'why', 'addedAt']], ['Log', ['time', 'sender', 'text']]]
    .forEach(function (s) {
      var sh = ss.getSheetByName(s[0]) || ss.insertSheet(s[0]);
      if (sh.getLastRow() === 0) sh.appendRow(s[1]);
      sh.setFrozenRows(1);
    });
  ss.getSheetByName('Queue').getRange('A:A').setNumberFormat('@');
}

function startSending() {
  stopSending();
  ScriptApp.newTrigger('runSender').timeBased().everyMinutes(RUN_EVERY_MIN).create();
  var me = me_();
  var st = readTable_('Senders', SENDER_COLS);
  if (!st.rows.some(function (s) { return lower(s.sender) === me; })) {
    st.sheet.appendRow([me, today_(), '', false, 'started']);
  }
  SpreadsheetApp.getUi().alert('Sending is on for ' + me + '. It sends weekdays 8 to 11 am Chicago time, starting at 10 a day.');
}

function stopSending() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'runSender') ScriptApp.deleteTrigger(t);
  });
}

if (typeof module !== 'undefined') {
  module.exports = { isDoNotEmail: isDoNotEmail, dayDiff: dayDiff, capFor: capFor, inWindow: inWindow, runsLeft: runsLeft,
    quotaThisRun: quotaThisRun, pickRows: pickRows, decide: decide, parseBounce: parseBounce, bounceRate: bounceRate,
    shouldPause: shouldPause, isOptOut: isOptOut, buildMime: buildMime, validateIncoming: validateIncoming, HARD_MAX: HARD_MAX };
}
