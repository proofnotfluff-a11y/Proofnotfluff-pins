# Walkthrough specs for the promo bank (built Oct 7, 2026)

One voiced YouTube walkthrough (16:9, `--format walkthrough`, voice am_michael) for each of the six Shorts in promo/specs/bank/. Each spec keeps the bank Short's verified numbers and its `sources` array. Any number new to the walkthrough was read from a fresh build of the engine (`engines/<engine>/build_xlsx.py`, recalculated in LibreOffice headless with tools/render_xlsx.py, 0 error values) and added to `sources`. Rows that show a computed cell are revealed as neutral results, so every row has its own spoken "why" line. Chapter times in `post.description` are the caption start times from make_demo.py's timeline for the same spec, and `post.render_seconds` matches the render. Renders are not committed.

Render: `python3 tools/make_demo.py promo/specs/walkthrough/<slug>.json <out>.mp4 --format walkthrough` (one at a time; all renders share tools/work_demo/frames).

| Spec | Product | Title | Length | Render |
|---|---|---|---|---|
| craft-fair-booth-fee-break-even.json | #12 Craft Fair Profit Calculator | Craft Fair Booth Fee Break-Even: How Many Pieces You Need to Sell | 111.6 s | scratchpad/walk/craft-fair-booth-fee-break-even.mp4 |
| etsy-shipping-cost-per-parcel.json | #7 Etsy and eBay Shipping Cost Calculator | Etsy Shipping Cost Calculator: What It Really Costs to Ship One Mug | 108.8 s | scratchpad/walk/etsy-shipping-cost-per-parcel.mp4 |
| debt-avalanche-vs-minimum-payments.json | #16 Debt Payoff Tracker | Debt Avalanche vs Minimum Payments: How Long Five Debts Take to Pay Off | 100.5 s | scratchpad/walk/debt-avalanche-vs-minimum-payments.mp4 |
| etsy-offsite-ads-pricing.json | #5 Pricing Calculator for Etsy Sellers | Etsy Offsite Ads Fee: How to Price So an Ad Sale Keeps Your Profit | 105.7 s | scratchpad/walk/etsy-offsite-ads-pricing.mp4 |
| inventory-reorder-planner-cash-short.json | #6 Inventory Spreadsheet with Reorder Planner | Inventory Reorder Planner: What to Order When Cash Is Short | 94.2 s | scratchpad/walk/inventory-reorder-planner-cash-short.mp4 |
| airbnb-seasonal-pricing.json | #9 Pricing Calculator for Airbnb and VRBO Hosts | Airbnb Seasonal Pricing: Set Nightly Rates From Your Last 12 Months | 88.5 s | scratchpad/walk/airbnb-seasonal-pricing.mp4 |

Render folder: /tmp/claude-0/-home-claude/3ea7b64d-e75d-5dd8-8e49-ea1efe5d1ba9/scratchpad/walk/ (session scratch; re-render from the spec if it is gone).

Notes for the reviewer
- Each Short in promo/specs/bank/ should set its related-video link to the walkthrough of the same product once uploaded.
- None of these six products has a cleared free page, so the spoken close is "Search ProofNotFluff for the full workbook." and description line one is the product's /go/<product id>/ short link.
- The debt tracker counts from TODAY(); "about $38,155 owed today" moves by cents a day, the month counts hold for any October 2026 date.
- YouTube chapters need 10 seconds each, so some chapters cover two captions.
