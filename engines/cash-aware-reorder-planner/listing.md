# Listing
#6, live at https://www.etsy.com/listing/4585004344. Title and tags stay as they are on Etsy (a redesign never changes them). This file holds the description wording that matches the v3 file.

# Title
Inventory Spreadsheet with Reorder Planner, Stock Tracker for Small Business, Excel Google Sheets

# Price
$2.99 (ledger PRICE rule; no agent changes it)

# Description
An inventory reorder spreadsheet for small shops that hold stock: it flags every SKU, works out how many to reorder, and checks whether you can pay for the order before you place it.

Most reorder sheets stop at "order 69 tote bags". This one also asks whether the cash is there. In the example inside, the planner wants $2,793.90 of stock against $1,500 of usable cash; the Cash Check funds every at-risk SKU's cover quantity first, orders $1,497.50 now and defers $1,296.40 to the next cycle.

WHAT IT DOES
- A status for every SKU: OK, REORDER, STOCKOUT RISK, OVERSTOCK, DEAD or NO SALES, from days of stock against lead time
- Reorder point, order-up-to level and a quantity to order, with safety stock, your order cycle and a sales trend
- Orders ranked by profit per day and days of stock left
- Cash Check: what to order now, what to part order and what to defer when cash is short
- One purchase order per supplier, up to 6 suppliers
- Dead stock: cash trapped in slow and dead SKUs, a 10%, 25% and 50% markdown ladder and one recommended action each

WHAT'S INSIDE
- Cash-Aware-Reorder-Planner.xlsx with 6 working tabs: 1 Your Shop, 2 SKU List, 3 Reorder Plan, 4 Purchase Orders, 5 Cash Check, 6 Dead Stock, plus Start Here and Terms
- Room for 30 SKUs; a fictional sample shop with 16 SKUs is filled in so you can see it working
- Start Here guide as a PDF in US Letter and A4
- LICENSE-AND-DISCLAIMER.txt

TESTED COMPATIBILITY
Works in Microsoft Excel for Windows and Mac, Google Sheets (upload to Google Drive, open, then File, Save as Google Sheets) and LibreOffice. No macros, no add-ons, no sign-up. Example numbers are included; replace them with your own.

HOW YOU GET IT
Instant download. Download from a web browser on your computer or phone (Etsy, You, Purchases); the Etsy app can't download digital files.

FAQ
Does it connect to my Etsy shop? No. You type your stock counts and daily sales; nothing syncs.
Where do I find daily sales? On Etsy, Shop Manager, Stats shows each listing's orders for the period you pick (checked Oct 7, 2026). Units sold in the last 30 days divided by 30 is the daily figure.
Does it know my supplier minimums? No. Check minimums and price breaks before you send a purchase order.

Made with AI assistance and reviewed and tested by the shop owner.
Information and planning tool only, not legal, tax, financial or other professional advice. Results are estimates based on your inputs.
Digital download. No physical item ships.
File problems fixed on request through Etsy messages.

# Change note
Version 3 (Oct 7, 2026): redesigned to the v3 dashboard (6 numbered working tabs, Start Here and Terms tabs); same inputs, maths and example, proved by tools/compare_xlsx.py on 9 cases x 634 outputs. Fixes: a sold-out SKU (0 days of stock) no longer ranks last for funding; with the as-of date blank, days since last sale and the run-out date stay blank instead of showing -46,000 days and a 1900 date; a SKU to order with no supplier now shows blank and is counted on 4 Purchase Orders; the cash verdict and dead-stock advice are in sentence case; the unsourced inventory-turns benchmark and the Amazon and eBay menu paths are gone, and the Etsy Stats path is cited and dated.

# Description edits for the redesign swap (shop run)
The live description was not readable from this run (Etsy page fetch not permitted), so the shop run checks it once in the editor:
- Any phrase that names the old tab names ("Setup", "SKU Master", "Reorder Planner", "Cash Check", "Dead Stock", "Dashboard", "Instructions") becomes the new names: 1 Your Shop, 2 SKU List, 3 Reorder Plan, 4 Purchase Orders, 5 Cash Check, 6 Dead Stock.
- Any line naming the old file list ("Cash-Aware-Reorder-Planner-Quick-Start.pdf" or "Quick Start") becomes "Start Here guide as a PDF in US Letter and A4, plus LICENSE-AND-DISCLAIMER.txt".
- Any mention of Amazon Business Reports or eBay Seller Hub menu paths is removed; any "4 to 20 turns" benchmark is removed.
