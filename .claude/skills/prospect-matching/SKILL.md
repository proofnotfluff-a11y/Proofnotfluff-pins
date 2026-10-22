# prospect-matching (Wednesdays 10:10 am)

One job: turn local commercial cleaning and pressure washing businesses into validated Entity B prospects, one named decision-maker each, and pre-match each to this week's GC lead. You never contact a business, fill a form, sign up or buy.

## Inputs (Reads)
- CRM prospects (ArtifactData list, out_dir data/crm) and meta/products.
- permits/downstream/gc_leads.json (Entity A).
- Enrichment, first that exists: HUNTER_API_KEY in this environment; else new Apollo or Clay CSV exports in Todd's Google Drive folder "PNF enrichment" (Drive connector, read and download only).

## Process (Executes)
1. Find businesses (semantic): each product with live or outreachGo true keeps 80 businesses with status ready. Official lists first (City of Chicago business licenses, IDPH, Texas comptroller), then web search. Fit: the business's own site advertises post-construction, construction or commercial cleaning, or pressure washing, and serves the city. Two checker subagents re-read each site and return ok, fix or drop with the URL; keep what both pass.
2. Write data/prospects/businesses.csv (business, website) for checked businesses with no named contact yet.
3. Enrich, deterministic: `python3 tools/enrich_hunter.py data/prospects/businesses.csv --out data/prospects/hunter.csv` then `python3 tools/prospects_import.py --product <key> --source hunter data/prospects/hunter.csv`. Drive CSV instead: download to data/prospects/, then prospects_import with --source apollo or clay. No source: skip to step 6 and tell Todd once.
4. Gate: `python3 tools/validate_leads.py prospects`. Exit 1 stops this step; record the ERROR lines in meta/desk.note. Never hand-edit a rejected address to pass.
5. Pre-match (semantic): each validated prospect gets one lead_id from gc_leads.json in its city (same side of town when the area says so; Partial Occupancy Approved first, then valuation). Then `python3 tools/validate_leads.py matches` must exit 0.
6. CRM writes, pinned to the version read, batches of up to 50. New ids: create only, skip an id that exists. An existing id gets only the contact fields and matchedLeadId, and never when it has firstSentAt (one first email per business, ever). Todd's own edits win. Tools: email/SEND_RULES.md "Tools".

## Outputs (Writes)
- CRM prospects/<id> (id prefix cc-, cr-, ac- plus the website domain): {product, business, trade, area, website, contactType:"email", contact (the verified work email), contactFirstName, contactLastName, contactTitle, emailSource, emailStatus, matchedLeadId, sourceUrl, checkedAt, checkedBy:"twice", status:"ready", doNotEmail:false}. New businesses without a decision-maker: status candidate.
- Existing role-inbox prospects (info@, office@ ...) are left as they are; crm_prospects.py keeps them out of drafting.
- CRM meta/desk.lastFinder (one sentence). Scoreboard agents/leads-finder idle with lastNote, counts only, never a name.
- data/ stays local and gitignored: nothing about a person is committed.
- Message Todd only if a live product has under 40 eligible named prospects after this run, or no enrichment source exists.
