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
compare set (compare.md). These replace buyer and golden for story lessons: CONSTITUTION 2
was amended by Todd in a live chat, Nov 6, 2026, 7:15 am ("Go with you recommendations"); anim.py STORY_GATES. Buyer and
golden stay only for the held old-line lessons.

Old line order (lessons made before Nov 5): facts, facts-captions (after the script and captions exist), then after the
render: render-critic, buyer, send, design, golden. Pass bars: facts and facts-captions no mismatch; render-critic 0 faults; buyer stop and send or save yes;
send names one person by role and tie, a real line, a gain beyond "useful", a feeling, and thanks (send.md; Todd, live
chat, Nov 1, 2026, 4:35 pm: "Do both"); design no score under 4 and average 4.61 or more (4.50 from the third round,
after two FAILs); golden "post as is" (polish alone is not a FAIL).

The second opening (SLUG-hookb, anim.py hookb; same Todd message): the same lesson after the hook, so it reruns only
qa, facts, render-critic, buyer and design on its own files (anim.py HOOKB_GATES); send, golden and facts-captions carry
over from the lesson, and `anim.py hookready` refuses it if anything after the hook differs.

Kimi (Todd, Oct 29, 2026, 6:20 pm): facts and facts-captions run on Kimi first (.claude/skills/kimi-jobs/SKILL.md, tools/kimi_job.py
pastes these prompts with the files and source excerpts, since Kimi has no tools). Claude checks every Kimi FAIL reason and
confirms every "unconfirmed" item on its source page; the review JSON names the reviewer. Cap, error or no answer: the fresh
opus agent as before. Render critic, buyer, design and golden stay on Claude.
