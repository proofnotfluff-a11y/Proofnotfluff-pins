# GAP SWEEP: how ProofNotFluff finds market gaps with eRank (Oct 9, 2026)

Todd, Oct 9: "Our strategy is going after the market gaps in volume. We need to find and highlight all
market gaps and create digital products for them." This file is the method. The ledger DEMAND FLOOR v2
line and the plan file GAP SWEEP line bind the runs; this file explains the steps so every run does it the
same way.

## What eRank can and cannot tell us

- eRank gives search volume, clicks and keyword difficulty per phrase. It does not show where Etsy places us.
- Etsy places a listing by its own quality score (clicks, favorites, sales, reviews) and shop history. A shop
  with no sales on a phrase is shown on that phrase only when page 1 has room: weak shops already there,
  not a wall of 1,000-review listings and not a flood of brand-new AI shops.
- So a gap is three things at once: real US volume, a page 1 a new shop can enter, and a product angle page 1
  does not already own. Volume alone is not a gap. An empty page 1 with no volume is not a gap either.

## Step 1: screen volume in bulk (eRank Bulk Keyword Tool, Country USA)

- research/gap-seeds.txt holds 2,212 phrases in blocks of 20 (money, small business finance, home and family).
  One block = one of the 100 daily eRank searches. The R&D lab works through the blocks in file order and
  records where it stopped in scoreboard meta/shop.gapSweep {nextBlock, blocksDone, date}.
- For every row, write scoreboard gaps/<phrase-slug> {phrase, group, searches, clicks, ctr, competition, kd,
  tier, screenedAt}. Tier by US searches: A = 1,000+, B = 300 to 999, C = under 300 (C is recorded and
  never built; it still feeds tags).
- Also screen every phrase the Etsy Stats search-terms report shows for our listings (Monday shop run writes
  them to meta/shop.searchTerms): those are phrases Etsy already shows us on.

## Step 2: read page 1 (tools/etsy_page1_check.js, signed-out Etsy search, one page load each)

- Only tier A and B phrases get a page load; tier A first, highest searches first. At most 8 loads a run,
  15+ seconds apart (ledger ETSY RATE LIMIT). Set window.PNF_ERANK = {searches, clicks, kd} before running
  the script so the result carries the volume with it; save the whole object to gaps/<slug>.page1.
- The script's verdict (PROOF, not FLOOD, ENTRY) says whether buyers are there and a new shop can enter.
  Its gap fields say how hard the wall is: weakShops (page-1 shops with under 50 reviews), medianReviews,
  minPrice, medianPrice, and gap = PASS with 3+ weak shops.
- A tier B phrase counts as a gap only with gap = true. A tier A phrase counts with verdict PASS (weak shops
  help but are not required at that volume; the ads test and the listing kit do the rest).

## Step 3: name the angle (what page 1 does not do)

- For each gap, open the top 3 badged or best-selling listings (inside the same page cap) and write one line
  on gaps/<slug>.angle: what buyers complain about in their reviews, what the files lack (no Google Sheets
  version, no worked example, no video, printable only, $8+ price), and what ours does instead. Quote
  complaints under 15 words; never copy listing text, designs or files.
- gaps/<slug>.status: "gap" (build-ready), "wall" (volume, no entry), "thin" (entry, no volume), "closed"
  (ledger exclusions). A "gap" with an angle becomes ideas/<slug> {status:"ready", gapSlug, buyerProof}
  the same run, so the builders can take it.

## Step 4: build and title for the exact phrase

- The product is built to the angle. The title opens with the exact phrase (first 40 characters), tags carry
  the related tier A and B phrases from the sweep, the first description sentence repeats the phrase.
- The listing launches with the full kit (ETSY PLAYBOOK and LISTING KIT lines) because the first days decide
  whether Etsy keeps showing it.

## Step 5: judge by Etsy's own numbers, not eRank

- Monday shop run: Etsy Stats > Search terms per listing (SEARCH TERMS rule) and the signed-out rank check
  (MONDAY RANK CHECK). A gap listing with 0 impressions on its phrase after 14 days gets a retitle to the next
  gap phrase, not more tags.
- The scoreboard gaps collection is the market map. The COO reports every Monday: gaps found, built, live,
  and each one's rank and visits.

## Budget

- eRank: 100 searches a day (R&D lab 55, factory 30 as 10 x 3, 15 reserve). 55 bulk searches screen 1,100
  phrases a day; the seed file takes about two days. After that the lab re-screens the Etsy search terms and
  related phrases eRank suggests under each gap.
- Etsy page loads: R&D lab 8 a run, two runs a day; that is 16 page-1 reads a day, enough for every tier A
  and B phrase the screen produces (expect 30 to 60 of them in total).
