# Promo bank: ready-to-approve demo specs (built Oct 7, 2026)

Six make_demo specs for products with a v3 engine and few or no Shorts. Every number was read from the engine's own workbook: built with `engines/<engine>/build_xlsx.py`, recalculated in LibreOffice headless (tools/render_xlsx.py, 0 error values), and each spec carries a `sources` array (number, cell). Each one was rendered with `python3 tools/make_demo.py <spec> <out>.mp4 --format short` (voice am_michael, AAC track present). Frames were checked at 0.1 s, at the fix reveal and in the last second. All text stays clear of the right 150 px and the bottom 300 px. Captions match the spoken lines. Renders are not committed. Each spec's `post` block has the Short title, YouTube description, Reel caption and TikTok caption, and `hookId` is "bank" until the CMO assigns one.

| Spec | Product | Hook | The number | Source | Length |
|---|---|---|---|---|---|
| craft-fair-booth-315.json | #12 Craft Fair Profit Calculator | A $150 booth fee is really $315.60 for the day | $315.60 | 1 Show Costs I23 (total fixed show cost); 51 and 44 pieces from 3 Break-Even I14 | 29.6 s |
| shipping-mug-13-19.json | #7 Etsy and eBay Shipping Cost Calculator | $4.95 shipping on a mug that costs $13.19 to send | $13.19 | 1 Parcel Costs P22 (true cost per parcel); shortfall Q22 -8.24 | 23.1 s |
| debt-minimums-119-months.json | #16 Debt Payoff Tracker | Minimums only on five debts: 119 months to pay off | 119 months | 1 Dashboard J23 (minimums only); Avalanche J19 40 months, I21 $6,127 saved | 27.2 s |
| etsy-offsite-ads-27-48.json | #5 Pricing Calculator for Etsy Sellers | An Offsite Ads sale needs $27.48 to keep the same $8 | $27.48 | 3 Pricing I16 (list price if an ad sale); no-ads price I15 $22.01 | 28.9 s |
| reorder-plan-2793-vs-1500.json | #6 Inventory Spreadsheet with Reorder Planner | The reorder plan wants $2,793.90. Usable cash: $1,500 | $2,793.90 | 1 Your Shop I19 (recommended order); I22 $1,497.50 now, I23 $1,296.40 deferred | 32.9 s |
| str-july-242-november-104.json | #9 Pricing Calculator for Airbnb and VRBO Hosts | A $185 base rate means $242 a night in July | $242 | 2 Seasonality M22 (July rate); November M26 $104, floor 1 Your Property D23 $115 | 27.5 s |

Notes for the reviewer
- Short links use `/go/<product id>/` (docs/go/12/ and the others), because that is how the hub names them. Each one resolves to the listing id stored in the spec as `listing_id`. A `/go/<listing id>/` path does not exist.
- Debt tracker figures use TODAY(). The month counts hold for any October 2026 date. "Owed today" ($38,155) moves by cents a day.
- The reorder planner uses its typed sample date (2026-09-28), so its figures do not drift.
- #9 already has a fee-reset Short (demo-9-fee-reset.json). This one uses the seasonality angle instead. #12 had a 51-pieces slideshow Short on Oct 2. This one leads with the $315.60 day cost instead.
