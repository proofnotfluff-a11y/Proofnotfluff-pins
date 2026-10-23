# Free Monday email and the trial offer (funnel steps 2 and 3)

Todd, Oct 22, 2026, 7:57 pm, live chat [stated]: "Let's do all of this as you recommend." The funnel: cold email, then a yes to a free Monday email with 2 or 3 real leads, then after the 3rd free Monday a 1-week Gumroad free trial with the card entered at signup, then $29 a month ($39 for restaurant leads when it goes live). Gumroad only allows 1-week or 1-month trials; 1 week was chosen. Full decision text: coo/DECISIONS-2026-10-22.md.

Status: designed and drafted Oct 22. Nothing here is switched on. Each send needs Todd's word in chat, and the site sign-up forms wait for Todd's Kit step.

## How a yes gets on the list
- Cold email yes, in any words that agree: the outreach-drafter inbox step sets the CRM prospect to status `monday` with mondayYesAt (the date of the reply) and mondayCity (chicago or austin, from its product). It drafts a one-line reply in the same thread ("Great, the first one comes Monday."), sent only when Todd names it. The reply in the inbox is the consent record; the CRM date points to it.
- Site visitor: the product page form, one Kit form per city, double opt-in. Clicking Kit's confirm link is the consent. These are new forms. The old waitlist forms asked only for news about new cities and features, so nobody on them is moved to the Monday email.
- Nobody else. No bought or scraped list, no one who replied anything but yes, no customer (a Gumroad sale moves the prospect to customer and off this list, since members already get the full list).
- Stop: a reply of stop, no thanks, unsubscribe or anything like it sets opted-out and doNotEmail before the next send. Kit subscribers can also use Kit's own unsubscribe link.

## How each Monday's email is built
1. The downstream-leads workflow refreshes permits/downstream/gc_leads.json (Mondays 12:05 UTC, about 7:05 am Chicago).
2. `python3 tools/monday_email.py --city chicago --require-prev` (then austin) picks the leads and prints the subject and body. The rules, all in code:
   - Fresh this week: a lead whose id was not in the previous Monday's edition, or whose stage moved up. A real run uses `--require-prev` and stops if no earlier edition is found. With no earlier edition (the checks, the first preview) the tool ranks the whole list and says so.
   - Closest to the final clean first (partial occupancy approved, or near finish in Austin), then the largest valuation, one lead per builder. The copy never says a job is near the final clean unless its stage line says so.
   - Never a lead an earlier issue for that city sent (email/monday/sent.json), and never the lead a subscriber's cold email named (`--avoid`).
   - 3 leads when there are 3, 2 when there are 2. Fewer than 2 fresh leads: no email that week, and Todd hears why.
   - A dated City signal (a food license inspection at the same address) never makes a lead fresh, only breaks ties, and is not printed, since at a big building it can belong to another tenant.
   - The builder's main office line is added only when tools/builder_contacts.py has it verified from the builder's own website, and only at send time (the contacts file is encrypted and never printed in a check).
3. Gate: `python3 tools/monday_email.py --check` renders both cities from the live file and checks every rule below; check_repo runs it on every push as the `monday` check.
4. Drafts: one per CRM subscriber in that city, "Hi {first},", from the same inbox that sent their cold email (hello@ as a Gmail draft, sales@ through the Apps Script queue), inside each sender's daily cap. Site subscribers get the same body as one Kit broadcast per city, opening "Hi,". Gated again with `--gate`.
5. Todd says send. After it goes: `--record` writes the lead ids to email/monday/sent.json, and each subscriber's CRM record gets mondaysSent plus 1 and mondayLastAt.

Rules every Monday email keeps: plain text, under 200 words above the footer, no links, no price or trial talk, no em or en dash, only City facts from the live file, the footer below byte for byte (our mailing address and the stop line).

## The trial offer
- Who: a CRM subscriber whose mondaysSent reaches 3, once (trialOfferedAt). Kit subscribers who confirmed on or before the date of the third issue back; the first run that needs it (no earlier than Nov 9) confirms Kit's broadcast filter on join date can do this before relying on it.
- When: the Wednesday after their third Monday, so it never lands on top of an issue.
- What: the email below with the product's Gumroad link (utm_campaign=trial-email). It says plainly that it is an offer, that the card goes in at signup, that nothing is charged for 7 days, the monthly price after, and how to cancel.
- After: the free Monday email keeps coming unless they buy (then customer, off the list) or say stop.
- Restaurant leads: the same funnel at $39 once its outreach goes live; no template for it yet.

## Go-live list (after Todd's checklist; the site part is major and goes to Todd first)
- site/pages.json on the Chicago and Austin lead pages: "trialDays": 7 and "mondayForm": the new Kit form number for that city.
- Chicago FAQ: "Will you cover other cities?" still says the waitlist decides; Austin is live and the waitlist form is gone from the page. New answer to show Todd: "Chicago and Austin now. More cities with open permit data are next."
- A short /privacy/ page (Legal desk FIX 2), linked from the footer.
- Rebuild, every gate in seo/STORE.md, then Todd's go, then push.

## Templates (tools/monday_email.py reads these blocks; change wording here only with Todd)

### Issue
Subject: This week's {n} big {City} jobs and their builders
```text
Hi{name},

Here are {n} big {City} jobs from this week's City permit data, with the builder and how far along each one is.

{leads}

To use one: call the builder's main office, give the address and the permit number, and ask who buys the final clean.

The full list has all {total} open {City} projects of $500,000 or more, with the builder on each, every Monday.
```

### Lead
```text
{i}. {value} {work} at {address}
   Builder: {gc}
   Stage: {stage}
   {permit_label} {permit}, issued {issued}
   Work: {scope}
```

### Footer
```text
ProofNotFluff
680 North Lake Shore Drive, Suite 110-2964, Chicago, IL 60611
You get this because you said yes to free Monday jobs. Reply "stop" and you won't get another one.
```

### Trial
Subject: The whole {City} list, free for a week
```text
Hi{name},

That was your third free Monday, {sent_n} jobs so far. They come from a list of all {total} open {City} projects of $500,000 or more, refreshed every Monday with the builder on each, in a members' app and an Excel file.

This one is an offer, so skip it if the free email is enough. If you want the whole list, you can try it free for 7 days:
{link}

Gumroad asks for your card when you start and charges nothing that day. After 7 days it is ${price} a month until you cancel. Cancel in your Gumroad library before the 7 days are up and you pay nothing.

The free Monday email keeps coming either way.
```
