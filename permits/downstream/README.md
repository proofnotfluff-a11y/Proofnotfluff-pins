# Downstream GC leads (Entity A)

`gc_leads.json` is written only by `.github/workflows/downstream-leads.yml` (tools/ingest_downstream.py) and checked by
`python3 tools/validate_leads.py gc`. Schema `pnf.gc_lead.v1`. Business-level fields only: this repo is public, so
`site_contact` is always null here and no person's name, phone or email appears in any field.

## Stage map (tools/pnf_rules.py)

| City field | City value | Canonical stage |
|---|---|---|
| Chicago `permit_milestone` | CERTIFICATE OF OCCUPANCY PENDING (TEMPORARY OR PARTIAL OCCUPANCY APPROVED) | Partial Occupancy Approved |
| Chicago `permit_milestone` | INSPECTIONS (CERTIFICATE OF OCCUPANCY REQUIRED) | Inspections Under Way |
| Chicago `permit_milestone` | INSPECTIONS | Inspections Under Way |
| Chicago `permit_milestone` | PERMIT ISSUED (FEE DUE) | rejected, upstream |
| Chicago `permit_milestone` | CERTIFICATE OF OCCUPANCY ISSUED, COMPLETE | rejected, past handover |
| Austin derived stage | Near finish (a building permit of the open project finaled) | Inspections Under Way |
| Austin derived stage | Work under way (expiry pushed out after an inspection) | Inspections Under Way |
| Austin derived stage | Permit issued | rejected, upstream |

Neither City publishes a field that says "Final Inspection Scheduled", so no record is ever given that stage; the
enum keeps it for a future source. Chicago milestone values were counted from the live dataset on Oct 18, 2026
(permits/chicago/profile.json).

## Adjacent signals and join keys

| Signal | Dataset | Join key |
|---|---|---|
| co_pending, co_required | Chicago ydr8-5enu (same record) | the permit's own row |
| co_flag | Austin 3syk-w9eu, column `certificate_of_occupancy` | `permit_number` of the project's building permits |
| health_license_inspection | Chicago 4ijn-s7e5, inspection_type License or License Re-Inspection, last 120 days | `(city, address_key(address))` |
| health_license_inspection | Austin ecmv-9xxi, any inspection in the last 120 days | `(city, address_key(address))` |

`address_key` is house number, direction, street name and suffix in upper case with standard abbreviations, no unit or
suite, and the first number of a range. The permit-to-health join uses it because the food datasets carry no permit
number. The Timing Moat Gate keeps a lead only with at least one signal. Live hit counts for every key are in
`probes/join-keys-<date>.json` (tools/join_probe.py, run by the data-probe workflow).
