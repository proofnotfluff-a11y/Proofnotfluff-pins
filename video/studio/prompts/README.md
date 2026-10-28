# Studio gate prompts

Each gate is a fresh agent (model opus) that never saw the build. Give it this file's text with SLUG filled in and the
repo path /home/claude/proofnotfluff-pins. Inputs live in video/studio/videos/SLUG/ (V below); the reviewer pack comes
from `anim.py stills SLUG` (05_render/sheets/) and `anim.py gatepack SLUG` (05_render/gates/). Results go to
V/05_render/reviews/<gate>.json with the gate, round, pass, score and reasons. One fix round per gate; a gate's own
second FAIL holds the lesson for Todd. A gate rerun because another gate's fix changed its input starts at round 0.

Order: facts, facts-captions (after the script and captions exist), then after the render: render-critic, buyer, design,
golden. Pass bars: facts and facts-captions no mismatch; render-critic 0 faults; buyer stop and send or save yes;
design no score under 4 and average 4.61 or more; golden "post as is" (polish alone is not a FAIL).
