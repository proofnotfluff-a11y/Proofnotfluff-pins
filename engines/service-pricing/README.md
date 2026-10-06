# Service pricing engine (source of listing #13)

Live general edition: https://www.etsy.com/listing/4587962930 (Service Pricing Calculator, listed Oct 3, 2026, quality gate PASS).

## Files
- `build.py` builds `Service-Pricing-Calculator.xlsx` with openpyxl (7 tabs: Start Here, 1 Your Numbers, 2 Trade Presets, 3 Quote Builder, 4 Price Sheet, 5 Job Tracker, Thank You). Recalculate with the xlsx skill's recalc.py and confirm 0 errors.
- `guide.html` is the 2-page Start Here guide; `node pdf.js` renders it to `pkg/Start-Here-Guide.pdf`.
- `mock.html` lays out the five listing images; it embeds real sheet screenshots from `hi/` (render each sheet to PDF with LibreOffice, then pdftoppm to PNG, then crop). `node shoot.js` writes `img/01.png` to `img/05.png`.
- `listing.md` and `desc.txt` are the general edition's listing copy; `LICENSE-AND-DISCLAIMER.txt` and `README.txt` go in the zip.
- Playwright needs `NODE_PATH=$(npm root -g)` in the cloud container.

## Making a trade edition (product factory)
A trade edition is a separate product, not a copy. Etsy treats near-duplicates as spam, so each edition must change all of these:
1. Presets: replace the 20 mixed-trade rows with 15 to 20 jobs for that one trade, with that trade's pricing unit (see the ledger Pipeline spec for each trade).
2. Trade logic: add the one or two calculations that trade prices by (per square foot, vehicle size multiplier, lot size, editing hours, chair rental vs commission, materials markup, surface type).
3. Words: tab names, labels, examples, guide and images use the trade's own terms.
4. Figures: re-verify self-employment tax (IRS Topic 554) and the IRS mileage rate (76 cents from July 1, 2026, IRS news release IR-2026-29) on the build date; cite trade-specific numbers with a dated source.
5. Listing: title leads with the trade phrase ("Cleaning Business Pricing Calculator ..."), 13 trade tags, trade-specific images, review complaints mined for that trade.
Keep the review page, the license, the AI disclosure line and the quality gate.
