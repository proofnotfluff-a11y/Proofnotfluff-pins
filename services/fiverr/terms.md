# Fiverr order terms (ProofNotFluff)

Written by the Legal desk reviewer (AI), Oct 15, 2026. It is a risk-control file, not legal advice, and no attorney has read it yet. Every Fiverr delivery follows all three parts. The license lines on the gig pages, the FAQs and custom offers say the same thing as part 1 in fewer words, so change them together.

## 1. Terms tab (last tab of every delivered workbook)

Build it with `terms_tab()` from tools/wb_style.py, text word for word. Fill every angle bracket. Leave out the Trademarks paragraph when no brand is named in the file. If no rate or figure in the file came from outside the buyer's files, the Rates paragraph reads instead: "Rates. Every figure in this file came from you, as of <Month D, YYYY>." The Etsy Terms sections (full-version links and the review ask) are never used in a Fiverr delivery.

```
TERMS OF USE
ProofNotFluff | <file name> | Fiverr order <order number> | Delivered <Month D, YYYY>

Your license. This file was built for <business name> through the Fiverr order above, under the license stated on the gig page and in the order. Once the order is complete, you can use and edit it for that business with no time limit, and share it with your own staff, accountant, lender or investors for that business. You may not resell it, give it away, share it as a template, or use it to make files for any other business. This license ends if the order is cancelled or refunded, or if these terms are broken.

What stays with ProofNotFluff. ProofNotFluff keeps its rights in the template, layout and formulas. This order licenses them to you; it does not transfer them.

Your numbers. The numbers and files you sent stay yours. They were used only to build this file, and ProofNotFluff deletes its copies within 30 days after the order is complete.

Planning tool only. This file is for planning. It is not tax, legal, accounting or investment advice, and ProofNotFluff is not acting as your accountant, attorney or financial adviser. For decisions that matter, check with a qualified professional.

Your estimates. Results depend on the numbers you gave. Any number you gave as an estimate is marked "Estimate" in the file; it is yours to confirm and change. Results are estimates for planning, not promises of any sales, profit, cash balance or other outcome.

Rates. Any tax rate or platform figure that didn't come from you names its source in the file and was checked on <Month D, YYYY>. Rates, fees and platform rules change, so confirm them before you rely on them.

How it was made. Made with AI assistance and tested before delivery: every formula tried with blank, extreme and changed inputs, and every number traced to the files you sent or marked as an estimate.

No other warranty. Beyond what Fiverr's terms give you, the file is provided as is, with no other warranty, to the extent the law allows.

Limit of liability. To the extent the law allows, ProofNotFluff's total liability for anything to do with this file or this order is limited to the price you paid for the order. Nothing here limits rights that the law doesn't let anyone limit.

Fiverr's terms. Fiverr's Terms of Service govern this order. If anything on this tab conflicts with them, Fiverr's terms apply.

Trademarks. <Brand names used in this file, for example Shopify, Amazon, Excel and Google Sheets> are trademarks of their owners. ProofNotFluff isn't affiliated with, sponsored or endorsed by them.

Help. If a formula breaks or something looks wrong, send a message through Fiverr.
```

Gig 3 Premium website calculator: the workbook in the same delivery carries the Terms tab, and this comment goes at the top of the page's code.

```
<!--
Quote calculator built by ProofNotFluff for <business name> (Fiverr order <order number>, <Month D, YYYY>).
Licensed for use on <business name>'s own website only, under the Terms of Use delivered with the order.
Not for resale or reuse on other sites. Prices shown are estimates from <business name>'s own numbers.
-->
```

## 2. Buyer data rule (the crew, every order)

- **Where it lives.** Only in the owner's Drive folder "ProofNotFluff Fiverr orders/<order number>" (shared with no one, never by link) and on the Fiverr order page. A build session works on copies in its own scratch folder and deletes them once the delivery files are saved to the order folder.
- **Who sees it.** The owner, and the crew session building or fixing that order. No scheduled run, other desk or other order's session opens the folder. It is never shared with anyone else.
- **What we take.** Exports and summaries, never logins. Buyers are asked to remove customer names, emails and addresses. If any arrive anyway, the crew drops those columns before building and they never reach the delivery. Staff appear by role, not by name.
- **Never in.** This repo (it is public), the scoreboard, memory or the ledger, reports, logs, chat summaries, screenshots, gallery images, demos, the portfolio, test files or any product. In chat, an order is named by its number. Anything shown in public uses made-up data marked SAMPLE.
- **Deleted.** 30 days after Fiverr marks the order complete, or the day a cancellation goes through, the whole order folder (the buyer's files, working files and our copy of the delivery) is deleted, then deleted forever from Drive's Trash. Agents never delete Drive files (coo/CONSTITUTION.md), so this step is the owner's: the crew gives him the delete date in its delivery hand-off.
- **Why 30 days.** It covers the buyer's first month-end with the file, when a broken formula or a wrongly mapped line usually shows up and the fix needs their source files; after that the raw exports have no use to us, and the buyer keeps the delivered file.

## 3. Pre-delivery legal checklist (every line must pass before the files go to the order folder)

1. `python3 tools/legal_scan.py <delivery folder>` shows 0 high for every delivered file: workbook, summary PDF, guide and web page.
2. The Terms tab is the last tab, word for word from part 1, every angle bracket filled. Start Here carries the short notice (legal/README.md, section 4). Every input tab has the footer "Estimates only. Not professional advice. See the Terms tab.", except the Customer Quote tab (Gig 3), which is the buyer's own document for their customers and carries no text of ours. No links anywhere in the files: no Etsy, site or Gumroad links and no review ask.
3. Every number is traced: each input ties to the buyer's file (file name and column or row) or written answer, or is marked "Estimate". Gig 2 totals tie to the buyer's exports by channel and month. Any rate we supplied names its primary source and as-of date, re-checked on the build day (the engines take `--checked <date>`), and a payroll tax line also takes the payroll clause (legal/README.md, section 4). The summary and the delivery message use only numbers that appear in the file.
4. No other client's data anywhere: the file starts from the engine, never from another order's file. No other buyer's name, number or logo in cells, hidden sheets (none allowed), named ranges, chart data, comments or document properties. Author and last modified by read "ProofNotFluff". No customer names, emails or addresses.
5. The summary and the delivery message describe what the numbers show. They never tell the buyer what to do about prices, spending, borrowing, hiring or investing.
6. Gig checks. Gig 1: each channel's payout delay, and any reserve the buyer named, is its own line. Gig 3: the customer quote template has no terms or signature line written by us (if the buyer wants one, the Forms clause from legal/README.md section 4 goes on it). The website calculator holds only this buyer's calculator code, makes no network calls, collects nothing, links nowhere, labels its result "Estimated price" and carries the license comment above, added at delivery after the page's tests pass (`website_config.py --license`), since the white-label tests refuse our name anywhere a customer sees it.
7. The owner opens the file and reads the one-page summary against the buyer's numbers before he uploads it. The gig FAQ says he does, and Fiverr expects the seller's own skill and effort alongside AI.
