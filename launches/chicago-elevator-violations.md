# Launch record: Chicago Elevator Citations (proposed $99 a month), SPEC ONLY, NOT BUILT

Growth-research Phase B, Oct 22, 2026 (live session with Todd). Nothing is built, published, priced or emailed until Todd says go. Evidence: the Claude Doc "ProofNotFluff growth research, Oct 22, 2026" and probes/elevator-chicago-2026-10-22.json.

## Buyer and problem
- Buyer: independent elevator service and repair companies in Chicago. One building is a service contract, so a few good leads a month carry the price.
- Problem: they learn about a building whose elevator the City has cited only when the owner calls around. The City publishes the citation within days.

## Signal and real counts (GitHub Actions, Oct 22, 2026)
- Building Violations (22u3-xenr), department_bureau ELEVATOR: 467 citations at 122 buildings in 30 days, 114 of them still open; 1,805 at 419 buildings in 90 days.
- Kinds: maintain or repair an electric elevator 346, a hydraulic one 101, other 20. Inspection category: periodic 248, permit 187, complaint 32.
- 48 of the 122 buildings also hold an active City business license (commercial); the rest are mostly larger residential buildings. No owner name is in the data.
- Elevator equipment permits (ydr8-5enu): 95 permits at 82 buildings in 30 days, every one already naming an elevator contractor, so permits are not a lead; 5 buildings were both cited and permitted.

## Fields and filters
- Kept: street address, community area, citation date, the City's citation description, inspection category, open or complied, and whether the building holds a business license (yes or no). Never kept: inspector id or comments, any person's name.
- Filter: bureau ELEVATOR, cited in the last 30 days, still open at pull time; one row per building with its open citations listed.
- Cadence: weekly (the dataset updates daily).

## Free sample vs paid
- Free: last 7 days, street and community area only, no house number.
- Paid: full address, every open citation, a weekly Excel file and a members' page.

## Price: $99 a month (proposed, inside the $29 to $199 band)
- Fewer buyers than cleaning, higher value per lead. Sits under Chicago Cityscape's $125 permit newsletter (market check in launches A1, Oct 17).

## Honest timing claim
- "Cited by the City in the last 30 days and still open in the City's data when the list was pulled." Never "needs a new contractor".

## Risks and Legal desk questions
1. City data terms (source-terms.txt pattern) for resale of addresses from Building Violations.
2. Residential buildings: an elevator building is never a single home, but condo and co-op buildings are people's homes. Is a building address with an open elevator citation acceptable, or keep only buildings with a business license (48 of 122)?
3. Buyer count: answered Oct 22, below (24 active independents a year).

## Next
- [stated] Todd, Oct 22, 2026, live chat: "Elevator: run the buyer-count probe only. No build." Probe: tools/elevator_contractors.py and .github/workflows/elevator-contractors.yml (counts only, names never written), results below.

## Buyer count (GitHub Actions run 39825200072, Oct 22, 2026; probes/elevator-contractors-2026-10-22.json)
- Elevator equipment permits (ydr8-5enu): 280 in 90 days, 1,109 in 365 days; every one names an elevator contractor.
- Distinct contractors: 34 in 90 days (6 national firm names across 4 brands, 28 independents); 49 in 365 days (8 national names across 5 brands, 41 independents).
- Independents with 5 or more permits: 11 in 90 days, 24 in 365 days. Median independent: 3 permits in 90 days, 9 in a year.
- The nationals hold 128 of 280 permit slots in 90 days (46%) and 542 of 1,109 in a year (49%).
- Caveat: independents are counted after name normalization (case, punctuation, legal suffix); spelling variants of one firm still count twice, so 41 is a ceiling.
- Verdict (Oct 22): the count does not support building a $99 list now. About 24 active independent firms is the whole market; $1,000 a month at $99 needs 11 of them paying, close to half the market from cold email. At best a small add-on. Stays spec only.
