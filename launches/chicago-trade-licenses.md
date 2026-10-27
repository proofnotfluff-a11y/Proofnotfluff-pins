# Chicago Trade License Finder (chicago-trade-licenses)

Free data page, built Oct 27, 2026 in build chat B5 on Todd's go (Oct 27, 12:17 pm, "Let's do them all"; coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md; research_notes/kimi-2026-10-27-r10.md item 5).

## What it is
- /chicago-trade-licenses/: 12 trades (general contractor, electrical, plumbing, HVAC and mechanical, roofing, pest control, cleaning, painting, landscaping and pesticide use, junk removal and hauling, pressure washing and surface cleaning, snow removal). A glance table (City, State, fee), a trade selector, and per trade: key facts (fee, insurance, bond, renewal), then City, State, fee, insurance, bond, exam, renewal, suburb licenses and federal lines, each with its agency page and read date, ending "Check with" the agency and its link.
- General contractor class picker: largest single project value plus demolition scope gives the smallest class, fee, renewal and insurance, from the Department of Buildings class table (A unlimited $2,000; B $10M $1,000; C $5M $750; D $2M $500; E $500,000 $300; renewal equals the fee).
- One sub-page per trade: /chicago-trade-licenses/<trade>/.
- No email capture, no price, no product, no person or business named (Continental Testing Services is named only as the City's and the State's own testing vendor).

## Files
- tools/dp_licenses.py (page, sub-pages, picker), tools/dp_licenses_check.py (validator; --fetch re-reads sources), site/datapages/dp_licenses/licenses.json (55 sources, 167 lines, all read Oct 27, 2026), site/datapages/dp_licenses/check.json (runner report), .github/workflows/dp_licenses.yml, verify/flows/chicago-trade-licenses.json.
- Data is hand-read from agency pages, not pulled from a dataset. chicago.gov refuses GitHub's runners (403) and some ilga.gov pages fail TLS there, so the workflow proves only the State and federal pages (22 of 55 ok on Oct 27). No schedule: a monthly re-check is Todd's call.

## Open
- Fee risk: BACP's license table printed the Limited Business license at $250 for 2 years on Oct 27, 2026, but a BACP file "20260127newfees.pdf" (Business License Fee Updates) would not open from any route we have, and a blog reports $500 from Jan 1, 2026. The page shows the table's $250 with "Fees change, so check with BACP for the current fee." Todd opening the PDF settles it.
- The surface cleaning permit covers sandblasting, grinding and chemical washing; no City page we read mentions power or pressure washing, and the page says so.
