# Kit setup: free cleaning price cheat sheet and the Chicago leads waitlist (about 15 minutes, once)

## Status, Oct 17, 2026 (live session, on Todd's go)
- Done: Kit login email confirmed; from name ProofNotFluff, from address proofnotfluff@gmail.com.
- Done: form 10059686 "Cleaning price cheat sheet": the PDF opens straight after sign-up (https://proofnotfluff.com/downloads/cleaning-price-floor-cheat-sheet.pdf), and a double opt-in email (subject "Your cleaning price cheat sheet", with the PDF link and a "Confirm my email" button that reopens the PDF) confirms the address. Why: the first test confirmation, sent "ProofNotFluff via n.convertkit.com", landed in Gmail spam ("similar to messages identified as spam"), so the freebie no longer depends on that email. Wired into docs/free-cleaning-price-cheat-sheet/ (noindex off, in the sitemap, linked from the index and the house cleaning calculator through site/extras.json).
- Done: form 10059700 "Chicago construction leads waitlist" (double opt-in; subject "Confirm your spot on the Chicago leads waitlist", button "Confirm my spot"; after confirming it opens the leads page; the thank-you message tells people to check spam). Unconfirmed sign-ups still count as waitlist demand in Kit (Subscribers, status All). In site/pages.json kitForm, and the page is live (Legal desk cleared it Oct 17 pending only the form).
- Not built: the 3-email sequence (Step 3). Kit's Free plan has no sequences or visual automations (help.kit.com/en/articles/16627071, read Oct 17), and the account's Creator trial ends about Oct 21. The sign-up page promises only the cheat sheet. If Todd upgrades Kit, build Step 3 as written and restore the page's line about the three emails.
- Test sign-ups to leave out of any count: proofnotfluff+kittest@gmail.com (confirmed) and proofnotfluff+kittest2@gmail.com on the cheat sheet form. The waitlist test stopped at Kit's security check (repeat sign-ups from one browser), so the waitlist has no test row.
- Done Oct 17, 1:58 pm: Verified Sending Domain proofnotfluff.com in Kit (CNAMEs ckespa, cka._domainkey, cka2._domainkey and TXT _dmarc "v=DMARC1; p=none;", all DNS only, in the ProofNotFluff Cloudflare account). From address hello@proofnotfluff.com (from name ProofNotFluff) is confirmed and is Kit's default for new broadcasts and incentive emails. Cloudflare Email Routing forwards hello@proofnotfluff.com to proofnotfluff@gmail.com, so replies and Kit's notices land in that inbox. Why: the first test confirmation, sent from the gmail.com address 'via n.convertkit.com', landed in spam. Next check: one fresh test sign-up after Kit's trial ends (Oct 21), looking for the inbox, not spam.
- Done Oct 22, 8:50 pm (Todd's ask in a live chat): mailing address in Settings, Email set to 680 North Lake Shore Drive, Suite 110-2964, Chicago, IL 60611, United States (checked after a reload and in a confirmation email footer).
- Done Oct 22 (same chat): forms 10084986 "Free Monday jobs: Chicago" and 10084998 "Free Monday jobs: Austin" (email/M1-MONDAY.md). Inline, double opt-in on, auto-confirm off, confirmation email from hello@ with subject "Confirm your free Monday jobs email" and a one-line body naming 2 or 3 big jobs every Monday, after confirming they open that city's leads page, success message tells people to check spam. Saved and published in Kit; not on the site until the go-live step sets mondayForm. Live on the lead pages Oct 22, 9:34 pm. Test sign-ups Oct 22, 9:55 pm (Todd's yes), both reached Kit's success page; leave out of any count: proofnotfluff+monday-chicago@gmail.com (10084986) and proofnotfluff+monday-austin@gmail.com (10084998), both confirmed by Todd Oct 22 (the Chicago one landed in Gmail spam). Also leave out test-vstatcfwi@srv1.mail-tester.com (10084986, never confirmed). Oct 22, 10:30 pm (Todd's ask): both forms' confirmation email body changed to "Click below to confirm, and you'll get 2 or 3 big <City> jobs from the City's permit data, with the builder on each, on the Mondays there are new ones. Plain text, and you can unsubscribe any time." plus a line asking to mark it Not spam (Legal desk 2d: no "every Monday"). mail-tester.com on the Chicago confirmation: 9.1/10, SPF, DKIM and DMARC pass, the only penalty is the domain being under 14 days old (FROM_FMBLA_NEWDOM14). DMARC reports: Cloudflare DMARC Management wizard left for Todd's click (agents can't change DNS).

Everything below is ready to paste. Numbers come from the Service Pricing Calculator (#13) example, recalculated by docs/assets/pnf-calc.js (checked Oct 7, 2026). No em dashes, no invented people.

Cheat sheet PDF (public link used in email 1):
https://proofnotfluff.com/downloads/cleaning-price-floor-cheat-sheet.pdf

Sign-up page (goes live once the form ID is in it):
https://proofnotfluff.com/free-cleaning-price-cheat-sheet/

## Step 1. Account basics (Kit, Settings)
- Sender name: ProofNotFluff. Sender email: proofnotfluff@gmail.com (the address your Kit account uses) or another inbox you read (replies land there; agents never reply).
- Mailing address: Kit requires a physical postal address in every email footer (US CAN-SPAM rule). A P.O. box or a virtual mailbox works if you'd rather not show a home address. This one is your call.

## Step 2. Create the form
Grow, Landing Pages & Forms, Create new, Form, Inline, any template.
- Name: Cleaning price cheat sheet
- Settings, Incentive: turn ON "Send incentive email" (this is double opt-in, the safer default). Subject: Confirm and get your cheat sheet. Button text: Send me the cheat sheet. After confirming, redirect to: https://proofnotfluff.com/downloads/cleaning-price-floor-cheat-sheet.pdf
- Save. Copy the number in the form's address bar (app.kit.com/forms/designers/1234567/edit, the 1234567) and send it to the live chat. The agent puts it in the sign-up page and turns the page on.

## Step 2b. Create the waitlist form (the Chicago permit leads pilot, Oct 14)
Same place: Grow, Landing Pages & Forms, Create new, Form, Inline, any template.
- Name: Chicago construction leads waitlist
- Settings, Incentive: turn ON "Send incentive email" (double opt-in). Subject: Confirm your spot on the Chicago leads waitlist. Button text: Confirm my spot. After confirming, redirect to: https://proofnotfluff.com/chicago-construction-cleaning-leads/
- No sequence for this one. Save, copy its number the same way and send both numbers to the live chat. The agent puts this one in the leads page (site/pages.json "kitForm"), and the page can then go live once the Legal desk clears it.

## Step 3. Create the sequence
Send, Sequences, New sequence. Name: Cleaning price welcome. Paste the three emails below. Then in the form's Settings, add "Subscribe to sequence: Cleaning price welcome" (or a Visual Automation: form joined, then sequence).

### Email 1 (send immediately)
Subject: Your cleaning price cheat sheet
Preview: Four numbers, then price any clean from them

Hi {{ subscriber.first_name | default: "there" }},

Here's your cheat sheet:
https://proofnotfluff.com/downloads/cleaning-price-floor-cheat-sheet.pdf

It does one thing: shows what a clean has to cost so it pays you.

Most of us price by dividing the pay we want by the hours we work. In the sheet's example, that says $24.07 an hour. Once you count the hours nobody pays for (driving, quoting, invoicing), $545 a month of business costs and self-employment tax, the real break-even is $54.80 for every paid hour.

Print page 1 and fill in the yellow column with your own numbers. It takes about 10 minutes.

If you'd rather type than write, the same maths runs in the free calculator:
https://proofnotfluff.com/house-cleaning-price-calculator/

ProofNotFluff

Estimates for planning only, based on the numbers you enter. Not tax, legal or financial advice. Rates checked Oct 7, 2026.

### Email 2 (send 2 days later)
Subject: The drive that costs you $38.80
Preview: A $150 clean that loses money before you start

Hi {{ subscriber.first_name | default: "there" }},

Say you charge $150 for a 2.5-hour standard clean, one person, $8 of supplies, 15 miles round trip.

Using the cheat sheet's example break-even of $54.80 an hour:
- Time on site: 2.5 hours = $136.99
- Driving: 15 miles at 30 mph is 30 minutes = $27.40
- Vehicle: 15 miles at the IRS rate of 76 cents = $11.40
- Supplies: $8

Price floor: $183.79. At $150, that clean loses $33.79, and the drive alone is $38.80 of it.

The fix is not working faster. It's pricing the drive. Add a 15% margin and round up to the next $5, and the quote is $220, with $36.21 of profit inside it.

Two quick checks for this week:
1. Look at your farthest regular client. Is the drive in your price?
2. Is your price above your floor for every job, not just on average?

ProofNotFluff

Example numbers, not market prices for your area. IRS business mileage rate 76 cents a mile for July 1 to December 31, 2026 (IR-2026-29). Not tax, legal or financial advice.

### Email 3 (send 3 days after email 2)
Subject: Price every job in one place
Preview: The workbook version of the cheat sheet

Hi {{ subscriber.first_name | default: "there" }},

The cheat sheet works one job at a time. If you want every job type priced at once, the Service Pricing Calculator does the same maths in Excel and Google Sheets:

- A quote builder: hours, people, miles and supplies in, the floor and a rounded quote out
- A printable price sheet for each of your job types
- A job tracker that flags any job priced below your floor

It's $2.99, an instant download on Etsy:
https://www.etsy.com/listing/4587962930

Running a cleaning business specifically? The Cleaning Business Starter Kit adds client intake and checklists to the pricing side:
https://www.etsy.com/listing/4588330888

That's the last email in this series. If something in the cheat sheet looks wrong, reply and it will be fixed.

ProofNotFluff

Made with AI assistance and reviewed and tested by the shop owner. Estimates for planning only, not tax, legal or financial advice.

## Step 4. Tell the live chat
Send the form number. The agent then: puts it in the sign-up page, removes noindex, links the page from the free calculators and the house cleaning calculator, adds the page to the sitemap, and switches Short and Reel end cards to it.
