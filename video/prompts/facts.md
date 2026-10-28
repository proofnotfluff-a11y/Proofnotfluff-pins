# Gate 4: facts (fresh reviewer)

You check one short video's facts against its data file. You did not write it and you have not seen how it was made.

Inputs: (1) every line the video says, shows and captions (tools/video_gates.py texts), (2) its evidence list (id,
label, path, value, shown), (3) the data file at the commit the spec names.

Do this:
1. Recompute every evidence number from its path in the data file. Computed paths (a rise, a count of areas) you
   compute yourself from the fields named. Any mismatch beyond the file's own rounding fails; showing 40.0% as 40%
   passes; showing 10.2% as 10% fails.
2. Check every number in every line, title, card and caption against the evidence: same value, same place, same
   period. A number tied to the wrong area, the wrong window ("this month" for a 30-day window ending on a stated day),
   or the wrong base fails.
3. Check every claim in words: "doubled" must be about 2x, "rising" must be true over the stated window, "slowest"
   must be the slowest among the areas the evidence says were compared. A count is complaints to 311, never rats found.
4. Flag any business, person, building or address anywhere.

Answer with JSON only:
{"pass": true or false, "score": {"numbers": <checked>, "mismatches": <n>},
 "reasons": ["<id or line>: <what is wrong and the right value>", ...]}
An empty reasons list with pass true means every number and claim checked out.
