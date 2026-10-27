# Chicago City Contracts by Trade (B3)

Todd's go: Oct 27, 2026, 12:17 pm, live chat, "Let's do them all" (coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md). Item 3 of research_notes/kimi-2026-10-27-r10.md.

## What it is
- /chicago-city-contracts/: City of Chicago contract awards in 12 trades (janitorial and cleaning, pest control, landscaping and tree work, snow removal, roofing, painting, HVAC, electrical, plumbing, demolition, hauling and junk removal, pressure washing and graffiti). Per trade: new awards in the last 12 and 36 months (count, total, median), by department and procurement type, top vendors by new award dollars, changes (modifications) apart with money added and taken out, transfers apart, and contracts whose latest end date falls in the next 12 months, each with the City's contract PDF.
- 12 sub-pages /chicago-city-contracts/<trade>/ and a CSV per trade (chicago-city-contracts-<trade>.csv) through extra_pages.
- Free, no email capture, no checkout. Links to where open bids live: eProcurement bid opportunities, the DPS Current Bid Opportunities page and the weekly bid opportunity list it links.

## Data
- Source: City of Chicago Data Portal, Contracts (rsxa-ify5), https://data.cityofchicago.org/Administration-Finance/Contracts/rsxa-ify5, updated daily by the City. Awards, not open bids.
- Workflow: .github/workflows/dp_contracts.yml, daily 12:05 UTC (7:05 am Chicago in daylight time), on push of its tools, and by hand. Steps: self-checks, tools/dp_contracts_probe.py (terms page, bid pages, weekly list), tools/dp_contracts_data.py (the pull), make_site, commit.
- Committed (site/datapages/dp_contracts/): contracts.json (business fields only, no vendor address, vendor names that do not read as a business shown as "Name withheld"), sources.json, source-terms.txt (the City's Data Terms of Use, word for word, fetched daily), trade-map-check.json (most common descriptions per trade, for checking the map by eye).
- Facts check: .github/workflows/dp_contracts_check.yml with tools/dp_contracts_check.py, by hand only: an independent checker's SoQL queries asked of the City dataset, answers in site/datapages/dp_contracts/check/ (address, city, state, ZIP and vendor_id can never be selected).

## Rules the numbers follow (from the dataset's own description)
- Revision 0 is the original award; later revisions are changes, counted apart. A revision 0 row the City marks "NOT A NEW AWARD", "TRANSFER FROM PO" or "See PO #" is a transfer, not a new award.
- Negative amounts are changes that took money out, never netted into award totals. A $0 award on a blanket contract depends upon requirements ("$0, orders as needed"), counted but kept out of totals and medians.
- End dates exist only on blanket contracts; the latest revision's end date decides "ending", and "value so far" adds every revision.
- Left out of every trade: purchases of goods or equipment unless the description names work, fleet and machine upkeep ("parts and service"), design and engineering, software, art, grants, leases, redevelopment deals, delegate agency, property lease, revenue and utility contract types.

## Open bids ("open now" list)
- Checked Oct 27, 2026 by the Action: the 2026 weekly bid list still exists. The Current Bid Opportunities page links the list dated Oct 26, 2026 (.../2026WeeklyBidOpportunities/102626.pdf), but the PDF answers HTTP 403 to our runner on every host form. The eProcurement abstract list loads, but pages ten rows at a time through a session. Neither gives a complete list we opened, so no "open now" list is published; the page links the City's lists instead. Revisit if the City posts open bids as a dataset.

## Gates
See the scoreboard row todos/build-city-contracts for the PASS/FAIL lines.
