# Studio (the video engine's gold standard)

Voice in, explainer out: 9:16 Reels (1080 x 1920, 30 fps) timed to the spoken words. Todd, Oct 28, 2026, 11:51 am:
"We need to use this as our gold standard." The method is Jake Van Clief's five-stage studio (coo/DECISIONS-2026-10-28.md):
record the voice first, time every word, storyboard against the words, draw the animation as code, render. Each stage is
a folder with a contract, and every output is a file that gets checked before the next stage runs.

The look: the real thing on screen (the City's 311 numbers, our map, our pages) with the ProofNotFluff cast acting on top
(`_shared/kit.md`). A look is a dial (`_shared/looks.md`): the same scene draws in any look.

## A video, start to finish
1. **Plan** (`stages/01_voice`): audience, the one idea, the numbers, real screens worth showing, a metaphor only if it earns its place. Write `brief.md`.
2. **Voice**: `script.md` written as talk (`_shared/voice.md`), then the Studio voice workflow speaks it in paragraph takes. Check: listen to the whole take.
3. **Words** (`stages/02_transcript`): the same workflow runs Whisper; `words.json` and `transcript.md`. Check: names and numbers spelled right, nothing dropped.
4. **Storyboard** (`stages/03_cues`): `cues.md`, one beat per visual change, then `python3 video/studio/anim.py cues <slug>`. Check: read it.
5. **Scene** (`stages/04_scene`): `scene.js` from the kit, `stills`, read the sheets, fix.
6. **Render** (`stages/05_render`): `render`, then the gates (stages/05_render/CONTEXT.md), then the preview to Todd.

Creative freedom inside each stage; the gates between them are fixed. Every number on screen or in the voice is computed
from the data file and checked by the facts gate. Nothing posts without Todd's "post" on that exact preview.

| Path | Holds |
|---|---|
| `CONTEXT.md` | the pipeline in one table |
| `stages/NN_*/CONTEXT.md` | one contract per stage |
| `videos/<slug>/` | one video; `01_` to `05_` are its stage outputs |
| `anim.py` | every command (`python3 video/studio/anim.py -h`) |
| `_runtime/` | `player.js` clock, cues and preview; `kit.js` the cast, props, rooms and real screens; `looks.js` the looks; `map.json` the 77 community areas |
| `_shared/` | `voice.md` script and voice rules, `kit.md` what can be drawn, `desk.md` real screens, `looks.md` the looks, `sound.md` sound rules |
| `_templates/` | what `anim.py new` copies |

Heavy files (voice takes, voice.mp3, MP4s, sheets) live on the `video-renders` branch under `studio/<slug>/`; text and JSON live on main.
