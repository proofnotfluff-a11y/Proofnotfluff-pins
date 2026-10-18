# Builder contacts holdout check

Status, Oct 17, 2026, about 9 pm: **run.** Two independent checkers (opus, given only this file and the contacts file) reopened every source page. Checker A: 49 ok, 1 fix, 0 drop. Checker B: 49 ok, 1 fix, 0 drop. They agreed on 48 entries. No agreed fix, so nothing was changed in place. Consortian stays as filed (A suggested adding a general inbox; B did not confirm it, so it is not added). The Bowa Group goes to no-contact because the checkers disagreed. Verdict files: session scratchpad holdout-A.json and holdout-B.json.

## What each checker gets

Only a decrypted copy of the contacts, written outside the repo with `python3 tools/builder_contacts.py --decrypt-to PATH` (the repo keeps only `permits/chicago/builder_contacts.enc.json`, since Oct 18, 2026), and these rules, never the build notes:

- Re-open the `source` URL of every entry listed below. Confirm the phone, email and website in the file appear on that page and belong to the same company as `name` (name match plus a Chicago-area office or project).
- Only the builder's own website counts. A directory, Yelp, BBB, LinkedIn, Google listing, data broker or aggregator as a source fails the entry.
- No person anywhere in the file: no person's name, no personal cell, no named employee's direct line or personal email. A general inbox (info@, office@, estimating@ and similar) and the main office line are fine.
- For each entry return `ok`, `fix` (the exact correction) or `drop`, with the URL read.

Keep only entries both checkers pass; apply fixes both agree on; set entries they disagree on to `no-contact` with a note.

## Entries to check (20 near finish or new this week, plus 30 drawn at random with seed 20261017)

| Builder | Status | Checker A | Checker B | Result |
|---|---|---|---|---|
| Skender Construction LLC | verified | ok | ok | kept |
| Redmond Construction Corp. | no-contact | ok | ok | kept |
| Triumph Design Build Corporation | verified | ok | ok | kept |
| JC Anderson Inc | verified | ok | ok | kept |
| Macon Construction Group, Inc. | verified | ok | ok | kept |
| Big Construction LLC | verified | ok | ok | kept |
| Lo Destro Construction Company | verified | ok | ok | kept |
| Development Solutions, Inc | verified | ok | ok | kept |
| Bear Construction Company | verified | ok | ok | kept |
| MPI Contracting, Inc. | no-site | ok | ok | kept |
| Knudsen Construction, Inc. | verified | ok | ok | kept |
| Allegiance Construction Group, Inc. | verified | ok | ok | kept |
| Spec Development LLC | no-site | ok | ok | kept |
| Sachse Construction and Development Company LLC | verified | ok | ok | kept |
| Promised Land Development | verified | ok | ok | kept |
| Plan North Construction Services LLC | verified | ok | ok | kept |
| Kasper Development LLC | verified | ok | ok | kept |
| Libot Construction Group Ltd | no-site | ok | ok | kept |
| Lorenzos Home Improvement Services | no-site | ok | ok | kept |
| SB Group Construction LLC | no-site | ok | ok | kept |
| Corebuilt Contracting, Inc | verified | ok | ok | kept |
| Accend Construction LLC | verified | ok | ok | kept |
| K.R. Miller Contractors, Inc. | no-contact | ok | ok | kept |
| Burling Builders, Inc | verified | ok | ok | kept |
| Reed Construction LLC | verified | ok | ok | kept |
| Berglund Construction Company | verified | ok | ok | kept |
| McInerney Builders, Inc. | no-site | ok | ok | kept |
| Treewright Construction Services LLC | no-site | ok | ok | kept |
| Midwest Heritage Builders, LLC | no-site | ok | ok | kept |
| Ujamaa Construction, Inc. | verified | ok | ok | kept |
| Metropole Holdings LLC | no-site | ok | ok | kept |
| The George Sollitt Construction Co | verified | ok | ok | kept |
| Novak Construction Company | verified | ok | ok | kept |
| Northshore Development Group LLC | no-site | ok | ok | kept |
| Enciso Operations LLC | no-site | ok | ok | kept |
| Panoptic Group LLC | no-contact | ok | ok | kept |
| Bulley & Andrews, L.L.C. | verified | ok | ok | kept |
| Mavrek, Inc | verified | ok | ok | kept |
| Method Construction Services, LLC | no-site | ok | ok | kept |
| Halo Masonry & Construction, Inc. | verified | ok | ok | kept |
| TM1 Construction, Inc. | no-site | ok | ok | kept |
| O'Malley Construction Company | verified | ok | ok | kept |
| Avenue Construction Inc | no-site | ok | ok | kept |
| The Bowa Group Inc | no-site | ok | fix | no-contact (disagreed) |
| William's Construction & Design Co | no-site | ok | ok | kept |
| Breaking Ground Contractors Inc | no-site | ok | ok | kept |
| Consortian Construction, Inc. | verified | fix | ok | kept as filed (fix not agreed) |
| D.O.M. Properties Investment Inc | no-site | ok | ok | kept |
| Leopardo Construction Inc | verified | ok | ok | kept |
| Summit Design & Build, LLC. | verified | ok | ok | kept |
