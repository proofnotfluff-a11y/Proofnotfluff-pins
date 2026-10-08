# Listing: Rental Property Spreadsheet for 1 to 10 Doors

Version 2 (redesign desk, Oct 7, 2026): rebuilt to the v3 workbook design with identical maths (compare_report.md). Title and tags unchanged.

Scoreboard idea: small-landlord-rental-spreadsheet (R&D score 24; phrase "rental property spreadsheet", 240 eRank searches, 954 competing listings). Built by the cloud builder Oct 5, 2026 (rebuilt and gated 3:10 pm run).

## Title (89 characters)
Rental Property Spreadsheet for 1 to 10 Doors, Landlord Rent Tracker, Excel Google Sheets

## Tags (13, each 20 characters or fewer)
rental property, landlord spreadsheet, rent tracker, rental tracker, rent roll, property management, landlord template, rental income, rental expenses, schedule e expenses, real estate investor, duplex tracker, excel rent tracker

## Category
Bookkeeping Templates (ledger category rule: profit, costs and income tracking for a business)

## Price
- $2.99 (PRICE rule, Todd Oct 6; live price). Buyer offers: OFF

## Digital file
Rental-Property-Spreadsheet-1-to-10-Doors.zip, version 2 (v3 design, Oct 7, 2026): Rental-Property-Spreadsheet-1-to-10-Doors.xlsx, Start-Here-Letter.pdf, Start-Here-A4.pdf, LICENSE-AND-DISCLAIMER.txt

## Images (in order, repo redesign/19)
1. Cover with the Rent Roll (badges Excel + Google Sheets, Instant download, 1 to 10 doors)
2. Worked example: Oak Street House $4,844 profit, $550 kept (Cash flow by property card)
3. How it works in 3 steps
4. Rent Roll table (Paid, Partial, LATE, lease heads-up)
5. Property P&L table on Schedule E lines
6. Monthly cash flow with running total
7. Setup: doors table
8. Categories on the Schedule E line names
9. Is this for you?
10. How you get it
11. What's inside
Video: listing-videos/19.mp4 (11.6 s, 4:3, silent: October rent roll, then two payments clear it)

## Description
A rental property spreadsheet sized for landlords with 1 to 10 doors: one Log tab for every dollar in or out, a Rent Roll that flags late rent, and a profit and cash flow summary for each property. It opens with a worked example (a duplex and a single-family house, January to October 2026) so you can see every tab working before you type your own numbers.

WHAT IT DOES
- Rent Roll: pick a month (or leave it blank for this month) and every door shows Paid, Partial, Due or LATE, based on today's date and your own due day and grace days. Leases ending within 60 days are highlighted.
- Property P&L: one column per property for the year, with 14 expense categories named after the IRS Schedule E (Form 1040) Part I expense lines, so your totals are easy to hand to a tax preparer.
- Cash flow, not only profit: mortgage principal and capital improvements are tracked on their own rows, so you see what you kept. In the sample, Oak Street House shows $4,844 profit but keeps $550 after principal and a $1,450 water heater.
- Monthly tab: money in, expenses, cash flow and a running total by month, for all properties or one.
- Security deposits stay out of income (IRS Publication 527, checked October 7, 2026).

BUILT TO FIX WHAT BUYERS OF OTHER RENTAL SPREADSHEETS COMPLAIN ABOUT
- Hard to set up: one 1 Setup tab, typed once, then three steps on the Start Here tab. Yellow cells are for typing; every tab is locked against accidental typing, with no password.
- Can't find or open the file, phone trouble: one workbook, plus a Start Here page that says exactly which file to open on a computer, in Google Sheets, or on a phone, and how to download from Etsy (the Etsy app can't download files; a browser can).
- Not what was expected: sized for 1 to 10 doors instead of a 50-unit company workbook. The Rent Roll, Property P&L and Monthly tabs are shown in the photos with the real sample numbers.

WHAT'S INSIDE
- Rental-Property-Spreadsheet-1-to-10-Doors.xlsx with 8 tabs: Start Here, 1 Setup, 2 Log, 3 Rent Roll, 4 Property P&L, 5 Monthly, 6 Categories, Terms
- Start Here guide, 3 pages, PDF in US Letter and A4
- LICENSE-AND-DISCLAIMER.txt

FORMATS
- .xlsx for Microsoft Excel (desktop, or the Excel app on a phone; on screens over 10.1 inches, editing in the Excel app needs a qualifying Microsoft 365 plan)
- Opens in Google Sheets with File > Import > Upload (uses only functions Google Sheets supports)
- Up to 10 properties and 10 doors; the Log reads down to row 5,000

HOW YOU GET IT
Instant download. Download from a web browser on your computer or phone (Etsy, You, Purchases); the Etsy app can't download digital files.

Made with AI assistance and reviewed and tested by the shop owner.
Information and planning tool only, not legal, tax, financial or other professional advice. Results are estimates based on your inputs.
This summarizes federal rules as of October 7, 2026 from IRS Schedule E (Form 1040) 2025, the 2025 Instructions for Schedule E and IRS Publication 527 (2025). State and local rules can add to or change them.
Digital download. No physical item ships.
File problems fixed on request through Etsy messages.
Not affiliated with or endorsed by Microsoft or Google.

## Pinterest board
Landlord Bookkeeping (new board, per the R&D spec); until it exists, Airbnb and VRBO Hosting (1138144205771245717)

## Pin facts (from the product's own files)
1. In the sample year, Oak Street House shows $4,844 profit before depreciation but keeps $550 in cash after $2,844 of mortgage principal and a $1,450 water heater (Property P&L tab, January to October 2026 worked example).
2. October rent roll in the sample: $3,900 due, $1,750 received, $2,150 still owed, one door paid in full, one paid $600 of $1,100, one paid nothing. LATE shows once your due day plus grace days has passed (Rent Roll tab).
3. IRS Publication 527 (2025): don't include a security deposit in income if you plan to return it to the tenant (checked October 7, 2026); the workbook keeps deposits on their own rows, out of income.

## Notes for Todd and the factory
- Google Sheets (v2, Oct 7, 2026): v1's Monthly tab used SUMPRODUCT(SUMIFS) with a range of categories, which Google Sheets reads as the first category only (tested in Sheets: 100 where Excel gives 110). v2 uses a plain SUMPRODUCT, tested in Google Sheets with the right answer (QA folder, files "QA rental-property v2 function test" 1 and 2). The rest of the workbook uses SUMIFS with single criteria, COUNTIF(S), SUMIF, EOMONTH, TEXT, INDEX/MATCH, REPT and TODAY.
- v2 fixes: blank Rent Roll month shows this month (v1 error values in Excel); blank P&L year shows this year (v1 showed 1900 zeros); a door with no rent says No rent set (v1 said Paid); Monthly picker ships blank for all properties (v1 told buyers to type text its dropdown rejected); new checks for rent rows with no door and category names not on the list; the P&L picked column is headed Selected: <property>; every input validated; Thank You tab folded into Terms.
- The spec's line "from an owner who runs two short-term rental cabins" was left out: this product is for long-term landlords, so the credential would not fit the claims rules.
- Risk tier: High (cites IRS Schedule E lines and Publication 527). The tax tier clause is on page 1 of the Start Here guide and tab (Before you rely on a number), on the P&L notes, the Terms and in the listing block. Legal desk fixes Oct 5, 5:35 pm run: tax clause, Excel app wording, Rent Roll month validation, advance-rent and state deposit lines.
