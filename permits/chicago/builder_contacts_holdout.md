# Builder contacts holdout check

Status, Oct 17, 2026: **not run yet.** The session that filled permits/chicago/builder_contacts.json had no tool for starting independent checker agents, so Todd's holdout rule (two checkers that never see the build notes) is still open. Until both checkers pass an entry, treat every `verified` entry as self-checked only.

## What each checker gets

Only the file path `permits/chicago/builder_contacts.json` and these rules, never the build notes:

- Re-open the `source` URL of every entry listed below. Confirm the phone, email and website in the file appear on that page and belong to the same company as `name` (name match plus a Chicago-area office or project).
- Only the builder's own website counts. A directory, Yelp, BBB, LinkedIn, Google listing, data broker or aggregator as a source fails the entry.
- No person anywhere in the file: no person's name, no personal cell, no named employee's direct line or personal email. A general inbox (info@, office@, estimating@ and similar) and the main office line are fine.
- For each entry return `ok`, `fix` (the exact correction) or `drop`, with the URL read.

Keep only entries both checkers pass; apply fixes both agree on; set entries they disagree on to `no-contact` with a note.

## Entries to check (20 near finish or new this week, plus 30 drawn at random with seed 20261017)

| Builder | Status | Checker A | Checker B | Result |
|---|---|---|---|---|
| Skender Construction LLC | verified | | | |
| Redmond Construction Corp. | no-contact | | | |
| Triumph Design Build Corporation | verified | | | |
| JC Anderson Inc | verified | | | |
| Macon Construction Group, Inc. | verified | | | |
| Big Construction LLC | verified | | | |
| Lo Destro Construction Company | verified | | | |
| Development Solutions, Inc | verified | | | |
| Bear Construction Company | verified | | | |
| MPI Contracting, Inc. | no-site | | | |
| Knudsen Construction, Inc. | verified | | | |
| Allegiance Construction Group, Inc. | verified | | | |
| Spec Development LLC | no-site | | | |
| Sachse Construction and Development Company LLC | verified | | | |
| Promised Land Development | verified | | | |
| Plan North Construction Services LLC | verified | | | |
| Kasper Development LLC | verified | | | |
| Libot Construction Group Ltd | no-site | | | |
| Lorenzos Home Improvement Services | no-site | | | |
| SB Group Construction LLC | no-site | | | |
| Corebuilt Contracting, Inc | verified | | | |
| Accend Construction LLC | verified | | | |
| K.R. Miller Contractors, Inc. | no-contact | | | |
| Burling Builders, Inc | verified | | | |
| Reed Construction LLC | verified | | | |
| Berglund Construction Company | verified | | | |
| McInerney Builders, Inc. | no-site | | | |
| Treewright Construction Services LLC | no-site | | | |
| Midwest Heritage Builders, LLC | no-site | | | |
| Ujamaa Construction, Inc. | verified | | | |
| Metropole Holdings LLC | no-site | | | |
| The George Sollitt Construction Co | verified | | | |
| Novak Construction Company | verified | | | |
| Northshore Development Group LLC | no-site | | | |
| Enciso Operations LLC | no-site | | | |
| Panoptic Group LLC | no-contact | | | |
| Bulley & Andrews, L.L.C. | verified | | | |
| Mavrek, Inc | verified | | | |
| Method Construction Services, LLC | no-site | | | |
| Halo Masonry & Construction, Inc. | verified | | | |
| TM1 Construction, Inc. | no-site | | | |
| O'Malley Construction Company | verified | | | |
| Avenue Construction Inc | no-site | | | |
| The Bowa Group Inc | no-site | | | |
| William's Construction & Design Co | no-site | | | |
| Breaking Ground Contractors Inc | no-site | | | |
| Consortian Construction, Inc. | verified | | | |
| D.O.M. Properties Investment Inc | no-site | | | |
| Leopardo Construction Inc | verified | | | |
| Summit Design & Build, LLC. | verified | | | |
