# Launch record: Seattle Permits (price not set), NOT STARTED, BLOCKED on a product decision

Product 5 in the launch line (coo/PIVOT.md LEADS FOCUS, 4 Seattle permits; scoreboard leadproducts/seattle-permits). Checklist: design/LAUNCH_CHECKLIST.md. Nothing is built past the data check below until Todd decides.

## Data check, Oct 23, 2026 (product-builder run, counts only)
- Source: City of Seattle, Building Permits (data.seattle.gov dataset 76t5-zqzr), Public Domain, attribution "City of Seattle". Columns in probes/2026-10-22.json; the field for the builder is contractorcompanyname.
- Probe: tools/data_probe.py, run in Actions on commit caa2210, result in probes/2026-10-23.json (commit 31f9f7f). Permits with an estimated cost of $500,000 or more.
- Last six weeks (issued since Sep 11): 111 permits, contractor named on 2.
- Last 24 months, still open (status Issued or Phase Issued, demolition and temporary left out): 1,126 permits, contractor named on 54 (about 5 in 100). Non-residential: 284, named on 21. Residential (houses and apartments together): 842, named on 33.
- By year of issue, contractor named: 2019 226 of 1,105; 2020 338 of 1,022; 2021 161 of 1,070; 2022 77 of 1,129; 2023 56 of 1,013; 2024 56 of 1,130; 2025 54 of 1,195; 2026 so far 28 of 1,003. The City stopped filling the field for most permits after 2021.

## Why the build stops here
- The Chicago and Austin products promise every open project "with a business as general contractor" and sell the builder as the lead. In Seattle the City names a builder on about 1 permit in 20, so the same product would hold about 54 permits from two years of open work, about 2 a month.
- Building it without a builder changes the promise and the buyer's job (they would look up the builder on each permit themselves). That is a new product shape, so it is Todd's call (CONSTITUTION 2: when unsure, it is major).

## Options for Todd
1. Seattle without a builder: address, cost, stage, homes and the City's permit link; the buyer finds the builder. Weaker than Chicago and Austin; the copy and the holdout promises change.
2. Skip Seattle and take the next city whose open permit data names the contractor (step 3, more cities, coo/DECISIONS-2026-10-22.md: "add cities with open permit data by reusing the Chicago and Austin scripts"). The builder probes candidate cities first, counts only, and brings the numbers.
3. Keep Seattle for a non-builder buyer who sells to the property (dumpster, portable toilets, security, window cleaning), using the address and stage only.

## Build log
- Oct 23, 2026 (builder run): data check above; no FIX lines in qa/2026-10-19.md (newest QA). Nothing else built.
