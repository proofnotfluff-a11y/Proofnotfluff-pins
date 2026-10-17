# Launch checklist

Todd, Oct 17, 2026, 3:59 pm: "Going forward please make sure all products are 100% complete before we launch."

Launching means any of these: publishing a product on a store, linking a checkout from the site, sending an email about it, or promoting it in a post, pin or video. Publishing early "to test a link" counts as launching. Nothing launches until every box below is ticked, with proof in the product's launch record (scoreboard `launches/<slug>`, or repo `launches/<slug>.md` for products without a scoreboard doc).

Why this exists: the Chicago leads membership was published on Gumroad before it had a cover or thumbnail, and before the design director had judged it. Nobody bought it in that state, but the rule now prevents it from happening again.

## 1. The product itself
- [ ] Built to its standard (design/WORKBOOK_STANDARD.md v3, or the page templates in tools/make_site.py).
- [ ] Self-checks pass: tools/check_repo.py, the product's own --selftest, render_xlsx ERROR VALUES: 0, every tab rendered on screen and in print, and every PNG opened.
- [ ] **Holdout PASS.** An independent checker that never reads the build code tests a random sample against the primary source and every written promise.
- [ ] **Design director PASS** (design/DESIGN_DIRECTOR.md) on the product, every buyer-facing page, the storefront images and the first video frame.
- [ ] Legal desk cleared (legal/README.md): Terms, disclaimers, any data terms (for example the City of Chicago disclaimer) word for word.

## 2. The storefront (Gumroad, Etsy, the site)
- [ ] Name, price, summary and description final, verified against the product, no em dashes, the AI line where the store needs it.
- [ ] Cover image and thumbnail uploaded, and the design director judged both. No blank image slots.
- [ ] Gallery or listing images and the video, where the store shows them.
- [ ] Seller name and profile show ProofNotFluff, never a person's name.
- [ ] The post-purchase content (the download, or the members' link and password) is filled in and correct.

## 3. The buy and delivery path, tested
- [ ] Every checkout link on the site opens the right product at the right price, with its utm tags.
- [ ] Delivery tested end to end the way a buyer sees it: the receipt content opens the product, the password opens the members' page, and the download opens in Excel and Google Sheets.
- [ ] Cancel and refund wording matches the store's real terms.

## 4. Before any outreach or promotion
- [ ] Every number in the email or post matches this week's live product.
- [ ] Todd has seen the finished product and the storefront, and said go in chat.

## Who ticks it
The run that finishes each item ticks it with the proof (commit, report path, render path). The live session or the COO confirms every box before anything launches. A box that can only be done in Todd's account (an upload, a publish click) becomes a Todd quest. The product stays unlaunched until that quest is done and checked.
