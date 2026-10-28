# Pipeline

| Stage | Command | Output in `videos/<slug>/` | Check before the next stage |
|---|---|---|---|
| `00_source` (series only) | save a proven video's details, write `teardown.md` | `00_source/teardown.md` | the angle, in our own words |
| `01_voice` | `new <slug>`, write `brief.md` and `script.md`, then `speak <slug>` (the Studio voice workflow) | `01_voice/brief.md`, `script.md`, `takes.json`; audio on `video-renders` | the whole take, start to finish; numbers heard right |
| `02_transcript` | `transcribe` (same workflow) | `02_transcript/words.json`, `transcript.md` | names and numbers spelled right, no dropped words, pace in range |
| `03_cues` | write `cues.md`, then `cues <slug>` | `03_cues/cues.md`, `cues.json` | every beat worth seeing; every number on screen comes from `brief.md`'s data |
| `04_scene` | write `scene.js`, then `stills <slug>` | `04_scene/scene.js`; sheets in `05_render/sheets/` | the sheets: nothing overlaps, nothing in Instagram's covered bands, every spoken number readable |
| `05_render` | `render <slug>`, then `check <slug>` | `05_render/<slug>.mp4`, `qa.json`, `caption.txt` | the gates in `stages/05_render/CONTEXT.md`, then Todd's "post" |

Status is what exists: `python3 video/studio/anim.py status <slug>`.
Going back is normal: re-roll a take (`speak <slug> --take N`), fix a word in `words.json` or a cue in `cues.md`, re-run `cues`; the scene re-times itself from `cues.json`.
