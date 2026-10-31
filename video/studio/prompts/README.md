# Studio gate prompts

Each gate is a fresh agent (model opus) that never saw the build. Give it this file's text with SLUG filled in and the
repo path /home/claude/proofnotfluff-pins. Inputs live in video/studio/videos/SLUG/ (V below); the reviewer pack comes
from `anim.py stills SLUG` (05_render/sheets/) and `anim.py gatepack SLUG` (05_render/gates/). Results go to
V/05_render/reviews/<gate>.json with the gate, round, pass, score and reasons. Fix rounds go on until every gate passes
(Todd, live chat, Oct 31, 2026, 4:19 pm: "Please change the rule so it keeps going until the design is fixed. After two
fails lower the threshold to 4.5"); nothing is held for Todd on a FAIL count. A gate rerun because another gate's fix changed its input starts at round 0.

Order: facts, facts-captions (after the script and captions exist), then after the render: render-critic, buyer, design,
golden. Pass bars: facts and facts-captions no mismatch; render-critic 0 faults; buyer stop and send or save yes;
design no score under 4 and average 4.61 or more (4.50 from the third round, after two FAILs); golden "post as is" (polish alone is not a FAIL).

Kimi (Todd, Oct 29, 2026, 6:20 pm): facts and facts-captions run on Kimi first (.claude/skills/kimi-jobs/SKILL.md, tools/kimi_job.py
pastes these prompts with the files and source excerpts, since Kimi has no tools). Claude checks every Kimi FAIL reason and
confirms every "unconfirmed" item on its source page; the review JSON names the reviewer. Cap, error or no answer: the fresh
opus agent as before. Render critic, buyer, design and golden stay on Claude.
