# Spec: Back Office demo, roofing (decided Nov 6, 2026; build not started)

Todd, live chat, Nov 6, 2026, 10:32 am: "Let's go with A". Option A, as offered in that chat: a clickable demo on labeled
sample data (about 1 to 2 weeks of build runs), then one demo reel and 5 owner calls. Not a full CRM. Major under
CONSTITUTION 2 (new product): nothing goes on proofnotfluff.com, gets a price, or is sent without Todd's word.

Why (live chat, Nov 6): the joebrunner.ai roofing CRM reel is an agency demo on sample data, not a product for sale. A full
roofing CRM loses on price (Roofr has no per-seat fees, $0 to $349 a month, roofr.com/pricing read Nov 6) and needs
accounts, texting registration, payments, e-sign and support we do not have. His three screens that matter are back-office
work: a morning list of drafted messages, quoted against spent per job, and who still owes. That is Todd's FP&A edge and fits
the Oct 29 outcome pivot. Wiki: Research Wiki, Sources, Nov 6 row.

## Trade: roofing (the live session's call; Todd can switch it)
Biggest tickets of the trades we serve, so job costing and unpaid invoices carry the most dollars per job; the reel already
showed the format draws roofers. Same screens fit pest or cleaning later by changing the sample jobs.

## What it is
A back office that sits beside whatever the roofer uses now (or replaces a spreadsheet). The owner opens it in the morning,
approves what is drafted, and sees which jobs are losing money and who owes him. Nothing in the demo sends, charges or signs.

## Screens (v1)
1. Morning list: everything drafted and waiting, grouped (first text to a new lead, follow-up on a sent estimate, invoice
   reminder, change order for a job running over). Approve, edit, hold, dismiss. A count and dollars at the top.
2. One job: stage line (lead, estimate sent, signed, in production, invoiced, paid), estimate total, quoted against spent for
   materials, labor and other costs, profit now against profit quoted, and a change order prompt when a line runs over.
3. Who still owes: open balance by age (0 to 30, 31 to 60, 61 to 90, over 90 days), oldest first, a drafted reminder per invoice.
4. Rules: when this happens, draft that (on or off), plus follow-up timing (days after estimate, days after invoice).
5. Leads in: where a lead comes from, including a ProofNotFluff signal card (sample), so the demo shows the step lists stop at.
6. Export: one button downloads every job and invoice as CSV. The answer to "they hold your data hostage" in reviews.

## Sample data rules (how invariant 6 holds)
- Every screen carries a "Sample data" label. The reel says so too.
- No person names: customers are "Customer A" to "Customer L", streets are "Sample Ave" and similar, phone numbers never shown.
- Dollar figures are sample amounts, shown as sample, and the arithmetic (totals, differences, aging buckets) is computed by the
  page from the sample rows, never typed in. No real company, supplier price or roofer is named.

## Where it lives
One self-contained HTML page, source in demos/back-office/, published as a private artifact for Todd's review. On the site only
after his yes (new page type, CONSTITUTION 2).

## Build runs
1. Data model and sample rows; screens 1 and 2.
2. Screens 3 to 6; keyboard, 390 px phone width, axe WCAG 2.1 AA, numbers checked by a script against the rows.
3. Design director and a fresh-eyes Agent review; fix to PASS; then the private artifact goes to Todd.

## After Todd's yes on the demo (each needs his word)
- Demo reel: one job from lead to paid in our own scenes and look (teardown beats from
  video/studio/research/runs/2026-11-02-new-home-radar-reel.md). No "comment a word" ask unless Todd changes FORMULA.md.
- 5 owner conversations: a new outreach template to roofing owners asking for 15 minutes to look at it (new template, so
  Todd's yes first). The question to answer: would they use the morning list and the job costing, and what would they pay.
- Price: Todd sets it after the 5 conversations.
