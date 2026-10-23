# monday-email (Mondays after the leads refresh; not scheduled until Todd says so)

One job: build and draft the free Monday email for everyone who said yes, and the trial offer for anyone whose third Monday just went out. Design and wording: email/M1-MONDAY.md (Todd, Oct 22, 7:57 pm). Nothing sends until Todd says send in this session.

## Inputs (Reads)
- permits/downstream/gc_leads.json (refreshed that Monday), permits/<city>/sample.json counts, site/pages.json checkout and price.
- email/monday/sent.json (lead ids already sent, per city).
- CRM prospects (ArtifactData list, out_dir data/crm): status monday, mondayCity, mondaysSent, firstExample, sender, trialOfferedAt.
- email/SEND_RULES.md, only after Todd says send.

## Process (Executes)
1. `git fetch --depth=50 origin main` so the tool can compare with the previous edition; `python3 tools/check_repo.py --preflight monday-email`.
2. Per city: `python3 tools/monday_email.py --city <city> --avoid <its subscribers' firstExample ids>`. Exit 3 (fewer than 2 fresh leads): no issue for that city; tell Todd in one line.
3. Issue drafts: one per CRM subscriber of that city, not doNotEmail, with `--name <first> --office` at send time only (LEADS_PASSWORD set, builder office lines; never printed or logged). Kit broadcast for that city's site sign-ups: the same body with "Hi,"; its form numbers are in site/pages.json mondayForm once Todd makes them.
4. Trial drafts on the Wednesday: each subscriber whose mondaysSent is 3 and trialOfferedAt is blank, `--trial --sent-n <leads they were sent>`. Kit side: broadcast filtered to people confirmed on or before the date of the third issue back; confirm the filter exists the first time.
5. Write data/work/monday_drafts.json (schema pnf.monday_draft.v1) and run `python3 tools/monday_email.py --gate data/work/monday_drafts.json`. Exit 1: fix and rerun once, else drop that draft.
6. One private review page with every draft in full; ask Todd "Reply send". Send by email/SEND_RULES.md senders and caps (hello@ Gmail drafts in Todd's Chrome, sales@ Apps Script queue, Kit broadcast in Todd's Chrome), the same inbox as the prospect's cold email, plain text, 8 to 10 am Central.
- Stop, no thanks or unsubscribe in any words: opted-out and doNotEmail before the next send. A Gumroad sale: customer, off the list.

## Outputs (Writes)
- After send: `python3 tools/monday_email.py --record --city <city> --week <date> --leads <ids>`, committed (lead ids only).
- CRM: mondaysSent plus 1, mondayLastAt, mondaySentLeads; trialOfferedAt after a trial email.
- Scoreboard agents/monday-email idle with lastNote (counts only, no names); one message to Todd when a batch, a reply or a failure needs him.
