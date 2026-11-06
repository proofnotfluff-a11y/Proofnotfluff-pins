# The local box: when a job moves from shadow to real work

Todd, live chat, Nov 6, 2026, 10:34 am: "Start leaning on delivery and a lot faster. We're burning through cloud usage
really, really quickly. I'm not sure we can afford 2 weeks of shadow. We'll probably need to reduce the testing period.
Because, practically speaking, we really need to find a way to make this hardware investment worthwhile."

## The ladder (replaces "two weeks of shadow")
1. **Shadow:** the box does the job, Claude does it too, the two are compared. A new job kind starts here.
2. **Local first:** after 3 clean comparisons in a row, the box does the job and Claude only reviews its answer against
   the source and fixes what is wrong. Claude no longer does the job from scratch. That is where cloud usage drops.
3. **Spot check:** after 10 clean reviews in a row, Claude checks 1 in 3 answers.

Clean means: no invented person, quote, number or fact; and the job's own bar (extract: under 10% difference from
Claude; a gate check: same verdict; openings: 3 or more of 5 usable). One unclean answer drops the job back one rung.
Log each comparison or review as one line in LEARNINGS.md with the job name and clean or not.

## Where each job stands (Nov 6)
- **retell and read-aloud pre-checks (rung 2 now):** on every script and story round, send the local retell and
  read-aloud jobs first (prompts/retell.md, prompts/read-aloud.md) and fix what they flag. Run the fresh Opus gates only
  once both local checks pass. The local check can only add a fix, never pass a lesson: the Opus gates still decide
  (CONSTITUTION 2). Each skipped Opus round is the saving.
- **pulse extract (rung 1):** 3 clean pulses in a row, then rung 2 (trade-pulse SKILL step 3).
- **five openings (rung 1):** 3 clean lessons in a row, then rung 2: the box's openings join Claude's pick list.
- **story draft (rung 1):** it invented an owner on Nov 5; 3 clean drafts in a row before rung 2.
- **trial model Qwen3.8-27B:** judged after 3 twin comparisons per job kind (tools/local_trial.json), not on a date.
