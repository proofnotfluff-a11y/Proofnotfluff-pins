# Launch record: Chicago Exterior Repair Citations at Business Buildings (proposed $29 a month), SPEC ONLY, ON HOLD

Growth-research Phase B, Oct 22, 2026. Ranked third: real counts are thin. Nothing is built or emailed until Todd says go. Evidence: probes/exterior-chicago-2026-10-22.json.

## Buyer and problem
- Buyer: small masonry and tuckpointing, window, porch, roofing and fence contractors.
- Problem: a City citation for an exterior defect forces a repair, and the building owner picks a contractor fast.

## Signal and real counts (GitHub Actions, Oct 22, 2026)
- Building Violations (22u3-xenr), bureau CONSERVATION, exterior descriptions (exterior wall, parapet, lintels, cornice, chimney, porch, exterior stairs, windows, roof, eaves, fence): 358 buildings in 30 days.
- Only buildings at an address with an active City business license are kept: 59 in 30 days (177 in 90). By trade: masonry 38, windows and doors 33, porch and stairs 23, roof 16, fence 9.
- The other 299 buildings are homes or plain apartment buildings and stay out: selling a home's address with a citation to contractors targets a private person.

## Fields, cadence, free vs paid
- Kept: street address, community area, citation date and description, trade bucket. Weekly. Free sample: street only, last 7 days. Paid: full address and every open citation.

## Price: $29 a month (proposed)
- Parity with the construction cleaning list; 59 buildings a month is thin, so it sells only bundled across the exterior trades.

## Honest timing claim
- "Cited in the last 30 days and open in the City's data when pulled."

## Risks and Legal desk questions
1. Mixed-use buildings: a storefront below apartments may be owned by a person. Is the business-license test enough?
2. The address join (tools/exterior_chicago.py norm_address) misses some licenses; volume is a floor, not exact.
3. City data terms for resale.
