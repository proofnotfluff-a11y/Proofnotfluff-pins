# story-desk (the investigative reporter: find true, surprising stories on AI in the trades and script them for short video)

Todd, live chat, Nov 2, 2026, 12:28 pm: "We need to create an agent that is an investigative journalist master, somebody who
can go out on the web and find really, really interesting new stories about trades in AI software implementation, and write
these scripts as if they were a Pulitzer Prize winning investigative journalist, but made for short form videos. So still
keep the same techniques that we have with regard to hooks and grabbing people's attention, but the content has to be
really interesting." Runs inside the record-and-make task's spare runs (no runs added; weekly usage, Nov 1). Feeds the AI
lane (_shared/lanes.md). Craft and standards: video/studio/_shared/investigative.md (binding).

## Inputs (Reads)
- video/studio/_shared/investigative.md (story test, beats, verification, script craft), _shared/lanes.md, _shared/standard.md,
  _shared/voice.md, _shared/formats.md (dispatch), research/STORIES.md (the bank, killed list included), research/PERFORMANCE.md.

## Process (Executes)
Report (a make run with 2 lessons already waiting, when STORIES.md has fewer than 3 Ready; at most one a day):
1. Date from bash. Read STORIES.md so no story is reported twice and no killed one comes back without new facts.
2. Three beat reporters, fresh Agent subagents (model opus) in parallel, one per beat in investigative.md (records, money,
   the field). Each gets the beat, the story test and the kill list, and returns at most 3 leads as JSON: headline (ours),
   the one surprising true sentence, why an owner's money or risk moves this month, every document with the exact URL it
   opened and what that page says, the other side (the vendor's, agency's or defendant's own words or published limits),
   the do-this-week action, and dates.
3. Score each lead on the story test (new, consequential, surprising, documented, actionable; 0 to 2 each). Keep 8 or more
   with a primary document; kill the rest with one line why in STORIES.md "Killed".
4. Verify the best lead yourself: open every document, confirm every number, date, verb (alleges, rules, says) and the
   other side. A second, independent source for any claim not from a primary record. Anything that fails is cut, never
   softened into a vague line.
5. Write its dossier: video/studio/research/stories/<date>-<slug>.md (template in investigative.md): the lede, the trail
   of receipts with URLs and dates, the other side, what it means for a shop, the do-this-week setup, open questions.
   Add it to STORIES.md "Ready". Repeat 4 and 5 while time allows and Ready is under 3.

Script (when the make run's lane is AI and STORIES.md has a Ready story; the run makes it before any other AI idea):
6. New lesson folder from the dossier: format dispatch, hook pattern receipt, treatment story, `- **Story:**` the dossier
   path. facts.json from the dossier's receipts, each re-read today.
7. Write script.md by investigative.md "Script craft" inside voice.md and the dispatch band. viral-script steps 2 (model
   videos), 4 (five openings), 5 (talk) and 8 (human test) still apply.
8. The gates as for any lesson; the facts gate reads its "Stories" lines (prompts/facts.md). Move the story to "Made"
   with the slug.

## Outputs (Writes)
- research/STORIES.md, research/stories/<date>-<slug>.md, the lesson folder (brief.md, facts.json, script.md,
  script-check.md), one line in research/LOG.md per report run.
- Never: a claim no opened document supports, a lawsuit's claim as fact (say "alleges"), a private person's or small
  business's name, a vendor's own claim without "says", a quote over 15 words, an invented scene told as real, em or en
  dashes, a reply to anyone, a post, a purchase or a sign-up.
