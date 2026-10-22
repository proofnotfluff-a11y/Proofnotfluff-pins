# Send rules (read only after Todd says send)

Condensed Oct 22, 2026 from coo/LEADS_DESK.md Run 2 for the outreach-drafter stage. Todd's words behind it: "You send after my yes", "Yes, one follow-up" (Oct 18), "use sales@getproofnotfluff.com in tandem with hello@proofnotfluff.com" (Oct 19), keep bounces near 0% (Oct 20).

## What Todd's send covers
- Only the batch named in the message he answered. It is void once the next Monday's data refresh has run.
- First re-run the inbox step and re-read each prospect from the CRM. Skip anyone now replied, customer, opted-out, bounced or doNotEmail, and delete their draft.

## Before any email leaves
1. `python3 tools/copy_gate.py` exits 0 on the exact batch file. A draft edited after the gate is gated again.
2. Every address: Bouncer (app.usebouncer.com, signed in as hello@ in Todd's Chrome). Send only "Deliverable"; catch-all at most 10% of a batch; "Undeliverable" sets bounced-precheck and doNotEmail; "Risky" or "Unknown" waits a week. Credits out: tell Todd once.
3. Each address's domain returns MX records (dns.google lookup).
4. The footer below goes under the body exactly as written (tools/pnf_rules.py FOOTER):

```text
ProofNotFluff
680 North Lake Shore Drive, Suite 110-2964, Chicago, IL 60611
Not interested? Reply "no thanks" and we will not email you again.
```

## Senders and caps
- Every prospect gets one sender, written to its CRM field `sender`; its follow-up goes from the same inbox, as a reply in the first email's thread.
- hello@proofnotfluff.com: Gmail drafts in Todd's Chrome, at most 25 a day, Schedule send on weekdays 8 to 10 am Central, oldest checkedAt first. Steps to 40 only after a week under 2% bounces.
- sales@getproofnotfluff.com: the Apps Script sender (email/sender/, sheet "PNF send queue"), ramp 10, 20, 30, 40 a day by week from Oct 20, 2026, enforced in code.
- Plain text only: no links, images, tracking pixels or attachments.

## After each send
- Confirm it shows in Sent (hello@) or in the sheet's Log (sales@). Scheduled mail counts as sent only once it shows in Sent.
- CRM: first email `sent`, firstSentAt, followupDueAt = plus 5 business days, firstExample = the lead_id it named. Follow-up `followed-up`, followupSentAt.
- Scoreboard leadproducts/<slug>.outreach counts, counted fresh from the CRM (this stage is the only writer). One line to Todd with the counts.

## Never
- A second first email to anyone with firstSentAt. A follow-up after any reply, bounce or opt-out. More than one follow-up.
- Contact forms that ask for a phone number or a CAPTCHA, or say they are not for sales: list them for Todd.
- A person's name, phone or words in the scoreboard, repo or logs. Their name and work email live in the CRM only.
