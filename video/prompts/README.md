# Video engine reviewer prompts (Phase 0)

Each file is the whole brief for one fresh agent (Agent tool, model opus, Opus 5.5) that never saw the build notes,
the build chat or another reviewer's verdict (blueprint, Review rubrics). The run pastes the file, then the listed
inputs, nothing else. Every verdict is saved as video/reviews/<videoId>/<gate>.json (schema pnf.video.review.v1) with
the model, this repo's commit (skillCommit) and the inputs, so a past verdict can be rerun exactly.

| Gate | File | Inputs, and only these |
|---|---|---|
| 4 Facts | facts.md | the spec (video_gates.py texts output and evidence numbers), the data file at the spec's commit |
| Hook pick | pairwise-hook.md | the hooks as heard, every pair in both orders (tools/video_pairwise.py pairs) |
| 5b Render critic | render-critic.md | the timeline sheets (5 frames a second) and transcript.txt |
| 6 Send test | pairwise-send.md | this video's script and contact sheet beside the reference video's, both orders |
| 7 Buyer test | buyer.md | the script as heard and the Instagram caption |
| 8 Design | design.md | the contact sheet and the first frame, design/DESIGN_DIRECTOR.md, design/CAROUSEL_STANDARD.md |
| Golden | golden.md | the golden render's sheets, contact sheet, transcript, spec texts and qa.json |
| Script | scriptwriter.md | the spec skeleton from tools/video_story.py draft and cmo/CONTENT_PLAYBOOK.md section 9 |

One fix round per gate, then that gate and every gate after it run again; a second fail stops the video and its slot
takes the next candidate as a new attempt (blueprint, Fix rounds and replacements). No agent overrides a fail.
