# Studio gate prompts

Each gate is a fresh agent (model opus) that never saw the build. Give it this file's text with SLUG filled in and the
repo path /home/claude/proofnotfluff-pins. Inputs live in video/studio/videos/SLUG/ (V below); the reviewer pack comes
from `anim.py stills SLUG` (05_render/sheets/) and `anim.py gatepack SLUG` (05_render/gates/). Results go to
V/05_render/reviews/<gate>.json with the gate, round, pass, score and reasons. Fix rounds go on until every gate passes
(Todd, live chat, Oct 31, 2026, 4:19 pm: "Please change the rule so it keeps going until the design is fixed. After two
fails lower the threshold to 4.5"); nothing is held for Todd on a FAIL count. A gate rerun because another gate's fix changed its input starts at round 0.

The new line (REBUILD.md, build run Nov 5, 2026; PRINCIPLES.md outranks every bar here). Order: before any voice, on
script.md: retell, read-aloud, facts. After the voice: retell and read-aloud again on the transcript (the voice can change
the words), facts-captions. After the render: render-critic, design, send, compare. Bars: retell matches the story's
message line with a concrete action and no lost spot (retell.md); read-aloud no "and then" pair, no unset term, nothing
choppy, setup before payoff (read-aloud.md); compare top 2 on follow and top 2 on stop or understand against the gurus.md
compare set (compare.md). From Nov 6, 2026, 10:54 am the three run as ONE fresh reviewer in two turns (story.md; Todd:
"Go with your rec"), after the local box pre-checks retell and read-aloud (_shared/local.md). These replace buyer and golden for story lessons: CONSTITUTION 2
was amended by Todd in a live chat, Nov 6, 2026, 7:15 am ("Go with you recommendations"); anim.py STORY_GATES. Buyer and
golden stay only for the held old-line lessons.

Viewer gate (Todd, live chat, Nov 8, 2026, 10:11 pm: "Yes"): every lesson, short and proven video dated 2026-11-29 on runs viewer.md last, after the render: a fresh stranger with only the timeline sheets and the words, in two steps (the one idea is sent only in step 2). It decides whether a viewer gets it; no other gate does.

Proven lessons (Todd, live chat, Nov 7, 2026, 12:08 pm: "Go"; _shared/formats.md "Proven"; anim.py PROVEN_GATES): no story
gate. Before any voice: `anim.py copycheck` (code, gate copy) and facts on script.md. After the voice: facts-captions. After cues.md and before any scene code (from lessons dated 2026-11-26): facts on cues.md, the storyboard round (facts.md).
After the render: render-critic, design, send, then `anim.py copycheck` again. The reviewers never see the source video.

Old line order (lessons made before Nov 5): facts, facts-captions (after the script and captions exist), then after the
render: render-critic, buyer, send, design, golden. Pass bars: facts and facts-captions no mismatch; render-critic 0 faults; buyer stop and send or save yes;
send names one person by role and tie, a real line, a gain beyond "useful", a feeling, and thanks (send.md; Todd, live
chat, Nov 1, 2026, 4:35 pm: "Do both"), and from Nov 7, 9:27 am, from the video alone (no brief, no captions) the person
in the shop and the thing on screen held to screenshot, checked in code against brief.md's Send line (`anim.py sendcheck`); design no score under 4 and average 4.61 or more (4.50 from the third round,
after two FAILs); golden "post as is" (polish alone is not a FAIL).

The second opening (SLUG-hookb, anim.py hookb; same Todd message): the same lesson after the hook, so it reruns only
qa, facts, render-critic, buyer and design on its own files (anim.py HOOKB_GATES); send, golden and facts-captions carry
over from the lesson, and `anim.py hookready` refuses it if anything after the hook differs.

Kimi (Todd, Oct 29, 2026, 6:20 pm): facts and facts-captions run on Kimi first (.claude/skills/kimi-jobs/SKILL.md, tools/kimi_job.py
pastes these prompts with the files and source excerpts, since Kimi has no tools). Claude checks every Kimi FAIL reason and
confirms every "unconfirmed" item on its source page; the review JSON names the reviewer. Cap, error or no answer: the fresh
opus agent as before. Render critic, buyer, design and golden stay on Claude.

## v4 (Todd, live chat, Nov 9, 2026, 2:11 pm: "Make all the necessary changes"; coo/constitution/video.md; _shared/formats.md "v4")
A v4 lesson (Format verdict, invoice, call, case or update) runs four gates and nothing above this section: qa (code: `anim.py check`), facts,
render-critic, viewer (`anim.py gates_for`). Why: design score against views was r = 0.098, the send gate passed 18 of 18
lessons that earned 1 share between them, and one lesson burned 24 script rounds (the audit, coo/DECISIONS-2026-11-09.md).
- facts: on script.md before any voice; after the render once more on the transcript, cues.md, scene.js and captions.json
  (it judges the captions too; there is no separate facts-captions gate). facts.md rules 1 to 4 and 6, plus: a real story
  is the person's own account ("he says" for anything the source could not verify), names no person or business, lifts
  no run of 6 or more words from the source, and a plate on screen never reads as an exact quote. Rule 5 (trades first)
  holds. Rule 7's two-source bar is for dispatch only.
- render-critic: render-critic.md with the v4 frame: no host, level bar or end card; scene words inside x 40 to 1040 and
  y 250 to 1440; captions in y 1184 to 1382 may sit over bodies, never over a face or over scene words.
- viewer: viewer.md in two steps, with two more questions in step 1 (would you comment, and which side; would you send it,
  and to whom). The stranger has hired a contractor or works in the trades; not only an owner.
- Rounds: at most 2 fix rounds a gate; a round 1 or 2 reviewer gets the earlier faults and may FAIL on something new only
  for a blocker (a wrong fact, hidden or unreadable words, a broken frame, the message lost). Still failing after 2: shelve
  the lesson (`anim.py shelve`) and take the next story. Faults go in LEARNINGS.md.
- No design, send, story, copy, buyer or golden gate on a v4 lesson.

## Smoother line (Todd, live chat, Nov 6, 2026, 7:14 pm: "Go with your recommendations for all")
Why: on Nov 6 four runs queued 0 new lessons. Every round a new reviewer judged from scratch and found something new, so
fixes never converged (lsa-max-bid: 24 script rounds). These rules make a fix round converge. Every bar above stands.
1. Fix-check rounds. From round 1 on, any judgment gate (story, design, render-critic, send, compare) gets the faults from
   the last FAIL (its reviews/<gate>.json "reasons") in its prompt: "Earlier faults to check: ...". The reviewer confirms
   each one is fixed and may FAIL on something new only when it is a blocker: a wrong fact, unreadable or covered text, a
   broken or frozen scene, or the message lost. Any other new note is written as "note" (not a fault) and goes to
   LEARNINGS.md. Design: earlier scores carry for frames that did not change; a lower score needs a named visible fault.
2. Words that passed are not re-judged. When the story gate passes on script.md, run `anim.py storysnap <slug>`. After
   the voice, `anim.py storycarry <slug>`: carry true means retell and read-aloud carry over (write story.json with
   "carried": true and the snapshot's verdict); otherwise the story check reads the whole transcript but judges only the
   sentences it lists. Compare still runs after the render.
3. Counts in code first. `anim.py readcheck <slug>` (before the voice; `readcheck <slug> transcript` after) decides breath
   (over 32 words), choppy runs (3 or more sentences of 1 to 4 words) and "and then" starts. Fix every fault it prints
   before any AI gate; the AI read-aloud then judges only the chain, set-up, one voice and order, and does not count
   breath or choppy again.
4. Order of work: `anim.py tomake` (oldest first; 3 story FAILs in a row, back of line; 3 runs since Nov 6 without a
   queue spot, shelve it with `anim.py shelve <slug> "<reason>"`, set its story back to Ready in research/STORIES.md and
   take the next lesson). A shelved story is rebuilt later under a new slug.
5. Posting: `anim.py next` names no lesson when one already started posting today and fewer than 3 wait; 3 waiting lifts
   it back to 3 a day. A lesson started today always finishes its platforms.
