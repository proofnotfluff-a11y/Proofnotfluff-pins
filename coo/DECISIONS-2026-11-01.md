# Decisions, Nov 1, 2026

## Video lanes: AI for trades test (live chat)
- [stated] 8:41 am: "Should we do a video series on how the tradespeople can utilize Claude Cowork to manage their businesses or to optimize things like emails? Should we also talk about any really cool AI tools or free repos out there that the tradespeople can use to optimize their businesses?" ... "we have pretty good watch time and low skip rate, but all the other statistics are bad" ... "what do you think about pivoting into specifically focusing and purposing new AI innovations for tradespeople and their businesses?"
- Recommended: one AI lane of standalone lessons (no series), one tool doing one real job per lesson with real proof, free repos only when they run in a browser with no setup, the result on screen by 3 s in both lanes, and a 7-day test: 2 of 4 daily posts AI, 2 core; on Nov 8 AI at 2x core or better on shares + saves + follows per 1,000 views switches all 4 to AI.
- [stated] 9:01 am: "go with your recommendation".
- Applied: video/studio/_shared/lanes.md; video/config.json "lanes" mode alternate until Nov 8; anim.py `lanes` (next lane and each lane's numbers) and `lane_problems` in variety; brief template Lane line; standard.md C5; prompts/facts.md AI proof rule; tools/ai_demo.py and .github/workflows/studio-ai-demo.yml (real Gemini replies and phone shots of public pages, since the studio sandbox cannot reach AI sites); the record and make task reads lanes.md and makes the lane `anim.py lanes` names.

## Lunch slot empty; two a day (live chat)
- [stated] 11:57 am (screenshot of the lunch post run: no lesson ready): "why does this keep happening? I thought you fixed it."
- Cause: a make run finishes about one lesson in 2 to 2.5 hours (3 to 5 voice rounds, gate fix rounds), so 4 runs a day make at most 4 and the buffer never builds; the Oct 31 cut from 6 to 4 runs removed the slack. Weekly usage at 78% on Sunday rules out adding runs.
- [stated] 12:09 pm: "Let's go down to 2 videos a day until we get the formula and structure correct to go viral. use the spare capacity to focus on developing quality videos".
- Applied: morning and end-of-day post tasks turned off (not deleted); video/config.json posting 2 a day (lunch 11:37, evening 8:13 pm); CONSTITUTION 2 amendment line; _shared/formula.md (one test a lesson, research/FORMULA.md log, what a run does when 2 already wait); brief template Test line; lanes.md one AI and one core a day; anim.py `script` now estimates length at 160 words a minute before any voice (14 lessons measured, median about 159 including gaps); record and make prompt updated.

## 2 pm check (live chat)
- Evening 8:13 pm: 2026-11-14-ai-night-quote (AI) queued 1:40 pm, `anim.py next` names it, 0 of 4 platforms; evening post task on. Lunch post task on, morning off. Today's lunch slot posted nothing (no lesson ready).
- 2026-11-15-three-fixes (core, quick-math, test: length about 30 s): script PASS 79 words, script gates PASS round 3, 6 takes voiced, words 1:47 pm; cues, scene, render and gates still to do. Owed for Monday lunch 11:37.
- ElevenLabs: 1,524 of 133,571 credits used this cycle. preflight 0 errors.
- Devin Seymour audio reel (Openverse, Real SFX, earshot): same three tools judged Oct 31; IMPROVE 00s stands behind "The bar first"; no change. Research Wiki stale Sources line fixed.
- Open for Todd: Meta AI label (recommend on for Instagram and Facebook), Kimi Reddit prompt (given again), professional voice clone read-aloud script (offered).

## Sunday review: stretch move and stale rows (live chat)
- [stated] 5:43 pm, answering the Sunday review (coo/reviews/2026-11-01.md): "Go with your recommendations".
- Stretch move, yes: Overture Places pest discovery for the pest seat list (to-do decide-add-overture-pest). Built as tools/pest_discovery.py (count mode, selftest of 13 planted places) and .github/workflows/pest-discovery-dryrun.yml (run by hand, read-only, counts only; CRM pest domains not in prospects/businesses.json are passed as 12-hex hash prefixes, never in clear). The count comes first; new companies then go through the prospect-matching "Pest seat" steps (two checkers read each site, own-site address only, Bouncer and MX) like any other.
- Stale rows: approve-carousel-post-rule closed as done (the standing carousel post rule is in CONSTITUTION 2 since Oct 25, and the carousel was retired Oct 29); monday-cold-batch-oct26 closed (its date passed; Monday batches run under the standing send rule).
- Next week's three commitments stay Todd's: the carousel rule is already done, so two remain (the 1 bounce notice in hello@ Spam, the free EIN).
- Dry run (Actions run 3, release 2026-10-21.0, field taxonomy.primary): 395 pest places in the metro box, 385 open, 338 with their own site, 119 dropped as chains, 20 as wildlife only, 175 companies, 43 already held, 132 new (47 in the city). Runs 1 and 2 read 0 under basic_category; a category probe fixed the field.
- Hand-off: .github/workflows/pest-discovery-extract.yml seals the 132 (business, website, address, inCity; no email or phone) to prospects/pest_candidates.sealed.json; the prospect-matching "Pest seat" source line reads it first (sources.md).

## AI lane: systems, not tricks (live chat, 9:17 pm)
- [stated] 9:17 pm: "Right now, our video substance is lacking. We should be helping trades people set up ai systems to automate and improve." (on a reel naming the hypit-ai/hypit repo)
- hypit read at 0762c6b (Oct 29): a tool that copies a viral video's structure into many variants using paid image and video models. Skipped: it adds no substance, "100 variants" is the mass-produced risk we guard against (Oct 31), generated footage breaks our real-proof rule, and our studio already times words and renders in code. Nothing installed.
- Applied: _shared/lanes.md "Systems, not tricks" (each AI lesson sets up a system: trigger, tool, prompt or setting, where it lands, one check; the save card is a setup card of at most 5 steps; under 30 minutes, no code). research/FORMULA.md reference (charlieautomates, 6,678 saves).
