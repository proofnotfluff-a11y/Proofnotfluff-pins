# Kit setup: free cleaning price cheat sheet (about 10 minutes, once)

Everything below is ready to paste. Numbers come from the Service Pricing Calculator (#13) example, recalculated by docs/assets/pnf-calc.js (checked Oct 7, 2026). No em dashes, no invented people.

Cheat sheet PDF (public link used in email 1):
https://proofnotfluff-a11y.github.io/Proofnotfluff-pins/downloads/cleaning-price-floor-cheat-sheet.pdf

Sign-up page (goes live once the form ID is in it):
https://proofnotfluff-a11y.github.io/Proofnotfluff-pins/free-cleaning-price-cheat-sheet/

## Step 1. Account basics (Kit, Settings)
- Sender name: ProofNotFluff. Sender email: proofnotfluff@gmail.com (the address your Kit account uses) or another inbox you read (replies land there; agents never reply).
- Mailing address: Kit requires a physical postal address in every email footer (US CAN-SPAM rule). A P.O. box or a virtual mailbox works if you'd rather not show a home address. This one is your call.

## Step 2. Create the form
Grow, Landing Pages & Forms, Create new, Form, Inline, any template.
- Name: Cleaning price cheat sheet
- Settings, Incentive: turn ON "Send incentive email" (this is double opt-in, the safer default). Subject: Confirm and get your cheat sheet. Button text: Send me the cheat sheet. After confirming, redirect to: https://proofnotfluff-a11y.github.io/Proofnotfluff-pins/downloads/cleaning-price-floor-cheat-sheet.pdf
- Save. Copy the number in the form's address bar (app.kit.com/forms/designers/1234567/edit, the 1234567) and send it to the live chat. The agent puts it in the sign-up page and turns the page on.

## Step 3. Create the sequence
Send, Sequences, New sequence. Name: Cleaning price welcome. Paste the three emails below. Then in the form's Settings, add "Subscribe to sequence: Cleaning price welcome" (or a Visual Automation: form joined, then sequence).

### Email 1 (send immediately)
Subject: Your cleaning price cheat sheet
Preview: Four numbers, then price any clean from them

Hi {{ subscriber.first_name | default: "there" }},

Here's your cheat sheet:
https://proofnotfluff-a11y.github.io/Proofnotfluff-pins/downloads/cleaning-price-floor-cheat-sheet.pdf

It does one thing: shows what a clean has to cost so it pays you.

Most of us price by dividing the pay we want by the hours we work. In the sheet's example, that says $24.07 an hour. Once you count the hours nobody pays for (driving, quoting, invoicing), $545 a month of business costs and self-employment tax, the real break-even is $54.80 for every paid hour.

Print page 1 and fill in the yellow column with your own numbers. It takes about 10 minutes.

If you'd rather type than write, the same maths runs in the free calculator:
https://proofnotfluff-a11y.github.io/Proofnotfluff-pins/house-cleaning-price-calculator/

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
