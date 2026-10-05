# ProofNotFluff Legal Desk

The Legal desk checks every product before Etsy sees it, and works back through the live catalog. Its job is to keep Todd's exposure low: no claim a product can't back up, no missing disclaimer, no borrowed IP, no personal details leaking in file metadata, and nothing in a category the shop doesn't sell.

This is a risk-control checklist written by an AI, not legal advice, and the desk never says a product is "legally approved". Todd has a quest to have an attorney read this file once. Their edits override anything here.

Who uses this file:
- **Legal desk** (scheduled task, 7:35 am, 12:35 pm and 5:35 pm): runs the full review.
- **Cloud builder**: builds the Terms page from the clause library below, so most products pass on the first try.
- **Factory**: when it builds a product itself (empty shelf), its reviewer subagent runs the checklist before Publish.
- **CMO and promote runs**: follow the claims rules (section 3) for pins, Shorts and Reels.

---

## 1. Risk tiers (pick one per product; it sets how hard the review is)

| Tier | What it covers | Examples | Extra checks |
|---|---|---|---|
| **High** | Tax, payroll, benefits, HR or employment rules; estate and end-of-life; contracts, client agreements, waivers or forms another person signs; anything citing a law, rate or deadline | #8 payroll guide, #11 emergency binder, #14 forms, 2027 tax planner, minimum wage calculator | Every rule and rate re-checked against the primary source in this run; tier-specific clause (section 4) on page 1 **and** in the listing; reviewer must be Fable when available |
| **Medium** | Money math: pricing, profit, budget, debt, shipping, STR pricing; job search outcomes; property hosting | #5, #6, #7, #9, #12, #13, #15, #16, #2, #3 | Estimates clause; no outcome promises; worked examples match the file |
| **Low** | Planners, trackers, checklists, printables with no rules, rates or advice | Cleaning schedule, habit tracker, welcome book layout | Base terms only |

**Never sell (BLOCK, no fix possible):** medical or mental health advice or treatment plans, legal filings or court forms, immigration, investment advice (what to buy or sell), anything presented as a substitute for a doctor, lawyer, CPA or financial adviser. A product that drifts into one of these is blocked and Todd is told.

---

## 2. The checklist (the reviewer answers every line PASS, FIX or BLOCK, with the exact text to change)

**A. Scope**
1. The product is not in a never-sell category, and no page drifts into one (for example a budget planner that starts recommending investments, or a binder that becomes a fill-in will).
2. A form, contract or agreement that another person signs is labeled a sample, with the "have a local attorney review it" line (section 4, Forms).

**B. Disclaimers (in the product, not only the listing)**
3. Page 1 or the Start Here tab carries the short notice (section 4, Short notice) plus the tier clause for High tier.
4. The product includes the full Terms of Use page (section 4) as its own page, tab or LICENSE-AND-DISCLAIMER file, with the as-of date filled in.
5. A workbook carries a one-line footer or header notice on every input tab ("Estimates only. Not professional advice. See Terms tab.").
6. The listing description ends with the listing block (section 5), including the AI disclosure line word for word.

**C. Claims (also applies to titles, tags, images, pins and video)**
7. No promise of results: no "guaranteed", "will save you", "get hired", "pass any ATS", "never get audited", "stay compliant", "100% accurate", "IRS-approved", "lawyer-approved", "certified", "official".
8. Every number on an image, in the title or in the description appears in the product's own files, with the same math.
9. "Tested" or "verified" claims say what was tested (for example "ATS-tested" needs the test written in the product: which parser, what date, what result). If there's no record of the test, drop the word.
10. Credentials are only ones Todd really has ("written by a finance executive" only on finance and business products). No invented reviews, testimonials, people or case studies.

**D. Accuracy**
11. Every law, rate, limit, fee or deadline names its primary source and an as-of date inside the product (IRS, SSA, DOL, a state agency, the platform's own help page). Third-party blogs don't count.
12. Anything the rule desk watches (repo research/rule-watch.json) uses the current value.

**E. Intellectual property**
13. No text, layout, images or structure copied from competitors or other sources. Short facts are fine; copied wording is not.
14. Fonts are licensed for commercial embedding (Poppins and Carlito are SIL Open Font License: fine). Images were made by us or carry a commercial license.
15. Brand names are used only to describe compatibility or audience ("works in Excel and Google Sheets", "for Etsy sellers"). No logos, no styling that implies a partnership. When a brand is in the title or on a cover, the Terms page carries the trademark line (section 4). No brand name at the start of a title in a way that reads as the brand's own product ("Airbnb Welcome Book" is weaker than "Welcome Book for Airbnb and VRBO Hosts"). Flag, don't auto-change, titles under a title freeze.
16. Etsy Creativity Standards: the product is seller-designed. AI is disclosed. A collection of AI prompts sold on its own is prohibited (#1 is already flagged to Todd).

**F. Privacy and personal data**
17. File metadata (xlsx, docx and pdf author, last-modified-by, company, comments, tracked changes, hidden sheets, PDF XMP data) says "ProofNotFluff" or is empty. Never Todd's real name, email, phone, address or employer. Check PDFs with `pdfinfo` and pypdf's metadata and XMP, and Office files by unzipping and reading docProps/core.xml, docProps/app.xml, comments and hidden sheets. Image EXIF goes through Pillow.
18. Worked examples use made-up placeholders, never a real person's data.
19. Forms that collect client or guest information carry the privacy line (section 4, Forms). Organizers that hold sensitive data (#11) carry the storage line.

**G. Etsy listing rules**
20. The description says what the buyer gets (file types, page or tab count, Letter and A4 where true) and that it's a digital download with no physical item. It doesn't promise support, updates or custom work beyond "file problems fixed through Etsy messages".
21. Nothing in the listing contradicts the shop's own policies. The agent never edits shop policies: a gap there becomes a Todd quest.

**H. Product function (the most common source of real complaints)**
22. Formulas work on a blank copy (no error cells after clearing the sample data), the buyer can't break a key formula by typing in an input cell, and dates aren't frozen (the Debt Payoff Tracker lesson).
23. A buyer can find the disclaimer before relying on a result: the result cell or page links or points to it.

Verdict: **CLEAR** (every line PASS), **FIX** (each problem with severity high, medium or low and the exact replacement text), or **BLOCK** (scope fail, or a claim that can't be made true).

---

## 3. Claims rules for promo (pins, Shorts, Reels, posts)

- Same as checklist C: no outcome promises, every number from the product's files, the as-of date for any rate.
- Frame results as an example: "On a $40 rate, the calculator shows about $20 an hour after costs" rather than "you only make $20".
- Use "estimate" or "example" in the caption when a number comes from the user's own inputs.
- Brand names only for compatibility or audience, never a logo.

---

## 4. Clause library (copy exactly, fill in the angle brackets)

### Short notice (page 1 or Start Here, every product)
```
For general information and planning only. This is not legal, tax, financial, medical or other professional advice, and using it doesn't create a professional relationship. Results are estimates based on the numbers you enter. Figures were checked on <Month D, YYYY> and can change. See the Terms of Use page before you rely on anything here.
```

### Terms of Use (its own page, tab or LICENSE-AND-DISCLAIMER file, every product)
```
TERMS OF USE AND DISCLAIMER
ProofNotFluff | <Product name> | Version <n>, <Month D, YYYY>

License. Your purchase gives you a personal license to use this product for yourself or one business you own. You may edit it and print it for that use. You may not resell, share, give away, upload or redistribute it, in original or edited form, or use it to make a competing product.

Ownership. The design, text and formulas belong to ProofNotFluff. Buying the product doesn't transfer ownership.

Information only. This product shares general information and tools for planning. It is not legal, tax, accounting, financial, employment, medical or other professional advice, and it doesn't create a client relationship of any kind. Your situation may differ. For decisions that matter, check with a qualified professional and the official source.

Accuracy. Rates, rules and figures were checked against the sources named in the product on the date above. Laws, prices and platform rules change, and state and local rules vary. You're responsible for confirming anything you rely on.

Estimates. Calculations depend on the numbers you enter and simplify real-world conditions. They are estimates, not promises of any result, income, savings, approval or outcome.

No warranty. The product is provided "as is", without warranties of any kind, to the extent the law allows.

Limit of liability. To the extent the law allows, ProofNotFluff is not liable for any loss or damage from using or relying on this product, and its total liability for any claim is limited to the price you paid for it. Nothing here limits rights you have under consumer protection laws that can't be waived.

Trademarks. <Brand names, e.g. Etsy, Excel, Google Sheets> are trademarks of their owners. ProofNotFluff isn't affiliated with, sponsored or endorsed by them.

AI assistance. This product was made with AI assistance and reviewed and tested by the shop owner.

Help. If a file won't open or something looks wrong, send a message through Etsy and it will be fixed.
```
(Leave out the Trademarks paragraph when no brand is named anywhere in the product or listing.)

### Tier clauses (add after the short notice on page 1, and in the listing block)

**Tax, payroll, benefits, HR**
```
This summarizes federal rules as of <date> from <IRS/DOL/SSA page names>. State and local rules can add to or change them. It is not tax, legal or HR advice. Before you file, pay or decide, confirm with the agency or a licensed CPA, enrolled agent or employment attorney.
```

**Estate, end of life, emergency binder**
```
This is an organizer, not a legal document. It is not a will, trust, power of attorney, health care directive or beneficiary form, and filling it in has no legal effect. Laws vary by state. Talk to an estate planning attorney about the documents you need. It will hold sensitive information: store it somewhere secure and share it only with people you trust.
```

**Forms, contracts and agreements another person signs**
```
These are sample forms to adapt, not legal documents written for your state or business. Have a local attorney review any agreement before you use it with clients. If you collect client information, you're responsible for keeping it secure and following the privacy laws that apply to you.
```

**Money: pricing, profit, budget, debt, shipping**
```
Calculations are estimates for planning and depend on your inputs. They aren't accounting, tax or financial advice. Check fees, rates and interest against your own statements and the provider's current terms.
```

**Job search**
```
These templates and guides improve how you present your experience. No product can guarantee interviews, offers or how any employer's screening system reads a file.
```

**Short-term rental hosting**
```
Short-term rental rules, permits, taxes, HOA limits and platform policies vary by location and change often. Check your local requirements and platform terms. You're responsible for the accuracy of safety and house information you share with guests.
```

**Food, fitness, wellness planners (organizers only)**
```
This planner is for organizing only. It is not medical, nutrition or fitness advice. Talk to a qualified professional before changing your diet, exercise or treatment.
```

---

## 5. Listing block (end of every description; the first line is required word for word by the shop's AI rule)

```
Made with AI assistance and reviewed and tested by the shop owner.
Information and planning tool only, not legal, tax, financial or other professional advice. Results are estimates based on your inputs.
Digital download. No physical item ships.
File problems fixed on request through Etsy messages.
```
High tier: add the tier clause's first two sentences as one extra line. A brand named in the title: add "Not affiliated with or endorsed by <brand>."

---

## 6. How the desk works

**Order each run (2 products per run, the gate first):**
1. **Shelf gate.** Every scoreboard idea with status "packed" and no `legal.status` of "cleared". The factory lists only cleared shelf items.
2. **Factory self-builds.** Products the factory built and listed itself (scoreboard products with no legal record), within 24 hours of listing.
3. **Live catalog backfill.** Highest risk first: #8, #11, #14, #9, #10, #13, #12, #5, #6, #7, #15, #16, #2, #3, #4, #1.

**Getting the files:** shelf items through the Artifact tool's read action (the zip comes as base64 text, check its sha256); live products from their Google Drive folder (ledger Systems line). Listing text from listing.md, or from the live listing page with one WebFetch.

**Fixing:**
- **Shelf items, text-level problems** (missing clause, metadata, claim wording, Terms page): the desk fixes the files itself, keeps the builder's QA (recalculate workbooks, render PDFs, look at every page), repacks, uploads new shelf assets, and reviews again.
- **Shelf items, a product problem** (a formula, a wrong rule, a scope drift): set the idea back to "ready" with the fix list for the builder.
- **Live products:** build the corrected file into the product's Drive folder as a new file (`<name> v<n>.<ext>`, never overwrite), and write scoreboard `legal/<id>` with status "queued" and the exact changes. The 6:50 am shop run applies up to 2 queued legal fixes per run as correction edits (file swap and description lines), inside its Etsy page cap. Titles under a freeze wait for the freeze to end unless the issue is high severity, which goes to Todd.
- **BLOCK:** never listed, idea set to "skipped"; for a live product, a message to Todd recommending "<id> retire". The desk never retires anything itself.

**Never:** touch Etsy, Chrome, eRank or Todd's computer; edit shop policies or settings (they become Todd quests); give Todd a firm legal conclusion; say anything is attorney-reviewed until Todd says it is.
