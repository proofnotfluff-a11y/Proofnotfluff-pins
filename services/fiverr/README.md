# Fiverr services line (ProofNotFluff)

Todd, Oct 15, 2026, 12:23 pm: "Let's do it" to a Fiverr services line under the ProofNotFluff name, Fiverr first and Upwork later. This folder is the kit: what we sell, the copy to paste, how an order runs and who does what. The ledger's [stated] line and coo/CONSTITUTION.md bind everything here.

## Why
Etsy makes us find buyers; Fiverr buyers arrive searching, with budgets. One order here is worth dozens of $2.99 sales. The generic "financial model" category is crowded at $60 to $100 (https://www.fiverr.com/gigs/financial-model, Oct 15), so we sell three niche services where our tested engines and a real finance background are rare.

## The three gigs (copy in gigs.md)
1. 13-week cash flow forecast for e-commerce brands (Shopify, Amazon, multi-channel). Base: the premium 13-week kit.
2. Profit dashboard by channel (channel P and L plus unit economics) for e-commerce brands. Base: engines/profit-and-loss, engines/etsy-true-profit.
3. Job pricing and quote calculator for cleaning, pressure washing and junk removal businesses, with a website calculator in Premium. Base: engines/service-pricing, engines/cleaning-business-kit, docs/assets/pnf-calc.js.

New sellers may run 4 active gigs; we start with these 3.

## Fiverr facts we built to (checked Oct 15, 2026)
- Fiverr keeps 20% of every order, tips included (Fiverr community blog, payment process).
- Display name may be the business name; the profile picture may be a company logo (help: Creating your freelancer profile).
- AI-assisted work is allowed when it is meaningfully refined for the client and the seller stands behind it; AI may assist but is "not a substitute for freelancers' own skill and effort"; if a client asks for non-AI work, the workflow is disclosed before the order starts (replies.md has the message); misrepresenting AI use can cost the account (help: Using AI on Fiverr, read Oct 15).
- Gig: up to 5 search tags, description up to 1,200 characters, up to 10 FAQs, up to 3 packages, minimum $5; titles avoid the characters & / " +; no external contact details or links in title, description or tags; gallery 1 to 3 images (1280 x 769 recommended, own images only), one 20 to 60 s video (16:9, at least 1280 x 720, MP4 H.264 and AAC, under 50 MB), up to 2 PDFs (first 3 pages shown); file names letters, numbers and hyphens only (help: Creating a Gig).
- Publishing needs: US status and W-9, personal and business verification, phone verification, a display name and one gallery image. All of that is Todd's.
- Field limits the copy is held to by tools/fiverr_kit.py (the code gate runs it on every push): package description 100 characters, FAQ question 70 and answer 300, requirement question 200, each tag 20 letters, numbers and spaces, profile description 150 to 600 (eduearnhub.com's 2026 guide to Fiverr character limits; it is not Fiverr's own page, so the checker leaves margin, for example counting each line break in a description twice).
- Ownership: by default all rights in a delivery pass to the buyer "Unless clearly stated otherwise on the freelancer's Gig page/description" (help: "For Commercial Use" license details). Our engines are reused across orders and sold on Etsy, so every gig description, FAQ and custom offer carries a license line: once the order is complete the buyer may use and edit the file in their business with no time limit, the template and formulas stay ProofNotFluff's, and the file may not be resold or shared as a template. The Terms tab text and the order rules are in terms.md (Legal desk, Oct 15).
- Fiverr's Gig policies page suggests a new seller start with one gig. We have three ready, each aimed at a different search; the recommendation is to publish all three, and Todd decides.
- Video length: the Creating a Gig page says 20 to 60 seconds and the Gig policies page says up to 75; ours run 30 to 45.

## Who does what
| Step | Owner |
|---|---|
| Kit copy (gigs.md, profile.md, replies.md) | live session (done Oct 15); after any edit run python3 tools/fiverr_kit.py |
| Profile picture, gallery images, demo videos, sample PDFs (assets/), the website calculator template (templates/) and the gig 2 engine | live session crew, Oct 15; images by tools/fiverr_images.py from real renders with sample data |
| Terms and a review of everything here (terms.md) | a Legal desk reviewer (live session, Oct 15), before Todd publishes |
| Seller account, ID and phone verification, W-9, payout, accepting Fiverr's terms | Todd |
| Prices | Todd (launch prices approved Oct 15, 12:57 pm; only he changes them) |
| Creating the gigs from this kit | Todd, or the live session in his Chrome with his go-ahead for each publish |
| Every message to a buyer | the crew drafts it, Todd sends it |
| Building each order | the crew, through the live chat or the cloud builder |
| Delivering in Fiverr | Todd uploads the delivery files and the delivery message the crew prepared |

## How an order runs
1. Todd gets the order notice and pastes the buyer's answers (or drops their files) into a private Google Drive folder, "ProofNotFluff Fiverr orders/<order number>" (the parent folder exists in his Drive since Oct 15, shared with no one; its id stays in the memory plan file's Fiverr line, not in this public repo), then tells the live chat.
2. The crew screens it: inside the gig's scope; not on the private decline list in the memory plan file's Fiverr line (decline with the template, no reason given); no logins asked for or accepted.
3. Build from the matching engine to design/WORKBOOK_STANDARD.md: the buyer's numbers in the input cells, every tab rendered and opened (tools/render_xlsx.py), blank, extreme and changed inputs tried, 0 error values, tools/legal_scan.py 0 high, then one reviewer subagent checks the maths against the buyer's own numbers.
4. The delivery files and the delivery message go back to the order's Drive folder with the terms.md checklist done. Todd opens the file and reads the one-page summary against the buyer's numbers, then uploads them in Fiverr and sends the message. Fiverr's AI guidelines say AI may assist but is "not a substitute for freelancers' own skill and effort", and the gig FAQ says he checks every delivery.
5. Revisions: inside the package's count and scope, same build steps. Anything bigger becomes a custom offer the crew drafts and Todd sends.

## Rules
- Buyer data never goes in this repo, the scoreboard or memory. It stays in the order's Drive folder and the session that builds it, and is deleted on the schedule in terms.md.
- Never ask for or accept store, bank or ad-account logins. Exports and summaries only.
- Keep every conversation, file and payment on Fiverr; no outside links, emails or phone numbers.
- Plain words, no em dashes, no invented clients or results, no guarantees of profit or funding. Planning tools only, not tax, legal or investment advice (terms.md).
- Ask for honest reviews only; never offer anything for a review.
- Upwork comes after the first Fiverr orders and reviews, once Todd says so; its proposals cost Connects ($0.15 each, 10 free a month), which is spending.
