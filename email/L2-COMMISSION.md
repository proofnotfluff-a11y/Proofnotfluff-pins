# L2: Chicago New Business Licenses outreach to commission sellers (written Oct 24, 2026, nothing sent)

Product: Chicago New Business Licenses, $29 a month (launches/chicago-new-business-licenses.md). Buyers, in this order (Todd, Oct 24, 2026, live chat): POS and merchant services resellers (trade `pos_merchant`), then independent commercial insurance agents (trade `commercial_insurance`). Approved Oct 23, 2:26 pm, decision 4 (coo/DECISIONS-2026-10-23.md): "New Business Openings outreach aimed at commission-only sellers". Kill rule (Todd, Oct 24): Nov 30, 0 payers from 100 delivered emails, read as a focus decision, not proof. Nothing sends without Todd's "send" in a live chat (email/SEND_RULES.md).

## Rules the copy gate checks
`python3 tools/copy_gate.py --lic-templates` and `--lic data/work/lic_drafts.json` (pnf_rules.lic_count_problems):
- The hook is the City's own counts for one week, from the two committed weekly files, never a business:
  - {n}: `counts.keptWeek` in permits/licenses-chicago/sample.json, new business licenses issued at a Chicago business address from `window.from` to `window.to`. The list leaves some out (renewals, event and one-person licenses, homes, names that could be a person's), so the email says "at least {n}".
  - {m}: `counts.licensePlaces` in permits/inspections-chicago/sample.json: food businesses (one per license number) that had a License inspection in the same window, any result; re-inspections and task force visits left out (copy review round 1: `segments.newOpening` counts re-inspections, so one place could count twice). A license inspection also comes with a change of owner, so the email says "{m} food businesses at their license inspection", never "about to open". The first email of each trade carries {m}.
  - {food}: `counts.segmentsWeek.food` (licenses); {area} and {k}: one community area in `counts.areasWeek` and its count ("{k} of them in {area}").
  - {from} and {to}: the window as the City date ("Oct 17"). Both files must cover the same window; the newest file at most 7 days old on the send day.
- No business named, no street, no price, no trial or free-trial line, no promise of phone numbers (the word "phone" is not used), nothing about inspection results or violations.
- The POS email never says insurance, and the insurance email never says POS, card payments or merchant services.
- Body under 75 words, plain text, no link, no dash, opens "Hi {first},", ends with the question. The sender appends the footer (tools/pnf_rules.py FOOTER).
- Sender: sales@getproofnotfluff.com only (the Apps Script queue). hello@ is kept for the pest seat (Todd, Oct 24). The gate fails any draft with another sender.
- Follow-ups: at most two, each 5 business days after the last, in the same thread (subject "Re: " plus the first subject), each with a newer week's counts than the email before it (the draft carries `prev_window_from`; the gate fails a follow-up on the same week). Never after a reply, an opt-out or a bounce.

## How a batch runs (outreach-drafter, Todd's live ask or a Monday)
1. Inbox step and Bouncer as the SKILL says, then `python3 tools/crm_prospects.py data/crm --products chicago-licenses --trades pos_merchant,commercial_insurance --prefix lic_`.
2. POS prospects first, then insurance, oldest checkedAt first, at most the sales@ day's cap per send day. No match and no lead: the hook is the week's counts.
3. Fill the prospect's trade template (first email T21 or T24) with this Monday's counts; write data/work/lic_drafts.json, schema pnf.lic_draft.v1: {schema, drafts:[{prospect_id, to, subject, body, variant, sender: "sales@getproofnotfluff.com"}]} (follow-ups add first_subject and prev_window_from).
4. `python3 tools/copy_gate.py --lic`, then the independent checker, then one private review page for Todd. Nothing sends until he replies send.
5. CRM: status drafted, batch, variant, sender. After a send: firstSentAt (delivered once the queue Log shows it sent, no bounce), and the funnel fields below.

Funnel (Todd, Oct 24, 11:52 am, the same stages as the pest seat): per prospect firstSentAt (delivered), repliedAt, sampleRequestedAt, yesAt, trialStartedAt, paidAt; totals in CRM meta/products.chicago-licenses.funnel and scoreboard leadproducts/chicago-new-business-licenses.funnel, counted fresh from the CRM.

What a yes gets ("Want me to send you this week's sample?"): a reply, drafted in the thread and sent only on Todd's word, with the public free sample page and its 7-day trial (launches/chicago-new-business-licenses.md). No other list is sent.

### T21 POS, first email
Product: chicago-licenses
Kind: license_count
Trade: pos_merchant
Step: first
Variant: A
Subject: {n} new Chicago business licenses, {from} to {to}
```text
Hi {first},

If you set up POS and card payments for new businesses, here is the City of Chicago's count from {from} to {to}: at least {n} new business licenses, {food} to food and drink places, and {m} food businesses at their license inspection.

Each Monday I list the new licenses by trade, with address, license type and whether it is a first license.

Want me to send you this week's sample?
```

### T22 POS, follow-up 1
Product: chicago-licenses
Kind: license_count
Trade: pos_merchant
Step: followup1
Variant: A
Subject: Re: {first_subject}
```text
Hi {first},

A fresh count: from {from} to {to}, the City issued at least {n} new business licenses in Chicago, {k} of them in {area}.

The City's data is raw. My list leaves out renewals, event licenses and home addresses, and marks each one first license, new site, added license or relicensed.

Want me to send you this week's sample?
```

### T23 POS, follow-up 2
Product: chicago-licenses
Kind: license_count
Trade: pos_merchant
Step: followup2
Variant: A
Subject: Re: {first_subject}
```text
Hi {first},

Last note from me. From {from} to {to}, the City issued at least {n} new business licenses in Chicago, {food} of them to food and drink places.

If new businesses are not who you sell payments to, no need to reply and you won't hear from me again.

If they are, want me to send you this week's sample?
```

### T24 Insurance, first email
Product: chicago-licenses
Kind: license_count
Trade: commercial_insurance
Step: first
Variant: A
Subject: {n} new Chicago business licenses, {from} to {to}
```text
Hi {first},

If you write commercial policies for new businesses, here is the City of Chicago's count from {from} to {to}: at least {n} new business licenses, {food} to food and drink places, and {m} food businesses at their license inspection.

Each Monday I list the new licenses by trade, with address, license type and whether it is a first license.

Want me to send you this week's sample?
```

### T25 Insurance, follow-up 1
Product: chicago-licenses
Kind: license_count
Trade: commercial_insurance
Step: followup1
Variant: A
Subject: Re: {first_subject}
```text
Hi {first},

A fresh count: from {from} to {to}, the City issued at least {n} new business licenses in Chicago, {k} of them in {area}.

Each one shows its license type and business activity, so you know the class of risk before you reach out. Renewals, event licenses and home addresses are left out.

Want me to send you this week's sample?
```

### T26 Insurance, follow-up 2
Product: chicago-licenses
Kind: license_count
Trade: commercial_insurance
Step: followup2
Variant: A
Subject: Re: {first_subject}
```text
Hi {first},

Last note from me. From {from} to {to}, the City issued at least {n} new business licenses in Chicago, {food} of them to food and drink places.

If new businesses are not who you write policies for, no need to reply and you won't hear from me again.

If they are, want me to send you this week's sample?
```

## Review verdicts
