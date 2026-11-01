# 05_render: render, gates, queue

**Reads:** `04_scene/scene.js`, `03_cues/cues.json`, `02_transcript/words.json`, the voice audio, `_shared/sound.md`, `_shared/captions.md`
**Makes:** `05_render/<slug>.mp4` (not committed), `05_render/sheet.jpg`, `05_render/qa.json`, `05_render/captions.json`, `05_render/reviews/*.json`, a queue entry

1. `anim.py lint <slug>`: the layout check in code (text off the safe area, text under the host, the dialog box or other
   text), the hook rules and, for a v2 lesson, the script rules and the end card send line (`SCENE.sendLine`). Fix every ERROR before rendering; it is cheaper than a gate round.
2. `anim.py render <slug>`: every frame in Chromium at 30 fps; voice, music bed and cue sounds mixed to -14 LUFS, true
   peak at or under -1.5 dBTP; H.264 and AAC. `anim.py check <slug>`: length 40 to 55 s for a v2 lesson, 45 to 75 s for v1 (end card included), loudness, black, frozen, file.
3. `captions.json` from `_shared/captions.md` (Instagram, TikTok, Facebook, YouTube: keyword line, proof, takeaway,
   send line, tags; no AI voice line, Todd Oct 29). Start from Kimi's draft (kimi-jobs skill) and edit it.
4. `anim.py stills <slug>` and `anim.py gatepack <slug>`, then the gates in `video/studio/prompts/` (README there): facts,
   facts-captions, render critic, buyer, send, design, golden, each a fresh agent (model opus); facts and facts-captions on Kimi first
   (prompts/README.md). Fix rounds go on until every gate
   passes (Todd, live chat, Oct 31, 2026, 4:19 pm: "keeps going until the design is fixed"); after two design FAILs the
   design bar is 4.50. A run that ends mid-fix leaves the lesson for the next run, which finishes it before a new one.
5. All PASS: commit the lesson, then `anim.py ready <slug>` (it pins the commit), commit and push. It posts on the next
   daily run (POSTING.md). Nothing posts that is not in the queue.
6. The second opening (Todd, live chat, Nov 1, 2026, 4:35 pm: "Do both", to two openings per lesson as Instagram trial
   reels): before the lesson's gates, write `01_voice/hook-b.md` and `03_cues/hook-b.md` (_templates/hook-b-voice.md
   and hook-b-cues.md: another hook pattern, the same stake and topic said another way) and draw it in the lesson's own
   scene.js under `if (window.HOOK === 'b')` in the hook cues, so the lesson's gates and pin include it. Once the
   lesson's voice is in, `anim.py hookb <slug>`, push, and run <slug>-hookb through fetch, cues, stills, lint, render,
   check, gatepack and its gates (prompts/README.md). All PASS, after the lesson's `ready`: commit, push, `anim.py
   hookready <slug>` (it compares with the lesson as pinned). The lesson never waits on it: if the second opening is not
   pinned when the lesson posts, the lesson goes up alone.
