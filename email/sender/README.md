# ProofNotFluff sender (Apps Script)

Todd, Oct 19, 2026, 4:34 pm: "using a script is a much better idea". It sends outreach from the sending inboxes on the new domain without a chat session composing each email, so sending costs almost no usage.

## How it works
- One Google Sheet, "PNF send queue", owned by leads@ on the sending domain and shared (edit) with the other sending inboxes. The script in this folder is bound to it.
- Tabs: Queue (one row per email), Senders (one row per inbox: start date, cap override, paused), DoNotEmail (addresses or @domains, never emailed again), Log.
- Each inbox opens the sheet once and clicks ProofNotFluff, Start sending. That installs a 10-minute trigger that runs as that inbox, so it sends only its own rows from its own Gmail, through the Gmail API (plain text, a List-Unsubscribe header, follow-ups threaded under the first email with In-Reply-To).
- The leads desk fills the queue through the web app (POST {secret, rows}) and reads results back (GET ?secret&since). The secret lives in Script Properties (SECRET) and in the private vault's GitHub secrets, never in this repo.

## Built-in limits (code, not the sheet, so a sheet edit cannot exceed them)
- Weekdays, 8:00 to 10:59 am Chicago time.
- Ramp per inbox from its start date: 10 a day in week 1, 20 in week 2, 30 in week 3, 40 after. A cap override can lower or set the number but never above 50.
- What is left of the day's cap is spread over the runs left, at most 5 per run, 20 to 45 seconds apart.
- Right before each send: do-not-email check (address or whole domain). A follow-up goes only from the first email's inbox, into its thread, and never after a reply, bounce or opt-out.
- Every run reads bounces (mailer-daemon, last 3 days) and replies on emails sent in the last 21 days. A bounce or an opt-out reply ("no thanks", "unsubscribe", "not interested" and similar, quoted text ignored) goes on DoNotEmail.
- An inbox pauses itself when more than 3% of its last 7 days of sends bounced (after 20 sends). Only a person or the leads desk un-pauses it.
- DRY_RUN=true in Script Properties marks rows "dry-run" and sends nothing.
- Any send error stops that run; the row shows "error" with the reason.

## Tests (run on every push by tools/check_repo.py, check sender-tests)
- `node email/sender/test.js`: the logic (caps, ramp, window, spreading, picking, do-not-email, follow-up rules, bounce parsing, bounce brake, opt-outs, incoming-row validation, MIME).
- `node email/sender/test_glue.js`: the real script against in-memory Sheets, Gmail and a clock, through a sending week: Sunday and out-of-window runs send nothing, day 1 sends exactly 10, a bounce, a reply and an opt-out are caught, follow-ups skip the right three and thread the fourth, the web app rejects a wrong secret and duplicate rows, dry run sends nothing.

## Setup (after the sending domain and inboxes exist)
1. Live session, in Todd's browser signed in as leads@: create the sheet, open Extensions, Apps Script, paste Code.gs and appsscript.json (show the manifest in Project Settings), run setupSheets, set Script Properties SECRET (random, generated in the session and stored only in the vault's secrets) and DRY_RUN=true.
2. Todd: approve Google's permission screen once for leads@ (Gmail send and read, the sheet, triggers).
3. Live session: deploy as a web app (execute as leads@, anyone with the link), store the URL in the vault's secrets, share the sheet with the other inboxes.
4. Each inbox (Todd's sign-in, about 1 minute each): open the sheet, ProofNotFluff, Start sending, approve the permission screen.
5. Test: queue 3 rows to Todd's own address with DRY_RUN=true and check the Log; then set DRY_RUN=false and send 2 real ones to his address (first plus follow-up) to check the From name, threading and the footer; then real prospects at the ramp.
