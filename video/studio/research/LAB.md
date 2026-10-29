# Lab log (video-lab: Tue, Thu, Sat)

jake-commit: 02ba5d8 (RinDig/Interpretable-Context-Methodology, Jul 25, 2026; read Oct 29, 2026)

Newest run first. Each run: the ICM scorecard, the benchmark lines with values, what was built, shipped or sent to Todd.

## 2026-10-29: baseline (set up by hand before the first lab run)

### ICM scorecard (Jake Van Clief's method)
- One stage, one job: PASS for the five stages (stages/*/CONTEXT.md); GAP for the daily run, which posts, researches, makes and improves in one context (.claude/skills/video-studio/SKILL.md). The lab now carries the bigger improvement work.
- Layered loading: PASS for L0 to L2 and the context budget (tools/context_gate.py); GAP: stage contracts have no "do not load" table.
- Every output an edit surface: PASS (script.md, cues.md, scene.js, facts.json are plain text).
- Configure the factory, not the product: PASS (_runtime/ and _shared/ change every lesson; IMPROVE.md).
- Checkpoints and audits per creative stage: PASS by AI gates (prompts/, seven fresh reviewers); no human checkpoint, by Todd's choice.
- Audio wins over script: PASS (02_transcript words.json drives cues).
- Gap-fill with a background underlay: PASS (rooms and sets behind every beat).
- End card with lockup and proofnotfluff.com: GAP (none in any lesson; IMPROVE 000).
- Tone tags about one per beat: PASS (_shared/voice.md).

### Benchmark baseline (by eye from contact sheets, to be replaced by the first measured run)
- First picture change: FAIL, lesson 9 holds one card 0 to 7.6 s; lesson 1 holds 3.5 s (target under 1 s).
- Host on screen: FAIL, lesson 9 at 7.6 s, lesson 1 at 3.5 s (target by 3 s).
- Smallest text: FAIL, about 20 to 27 px at 1080 wide (targets 44 spoken, 36 labels).
- End card: FAIL, none.
- Length: FAIL, 6 of 9 over 75 s (71.7 to 86.8 s, about 173 words a minute).
- Frame rate: 30 fps (60 fps in the backlog).
- Design gate: 4.71 to 4.86 on all nine, judged against our own spec only. From Oct 29 (Todd: "go with rec") the design gate also grades against _shared/style-board/: type floor, hook and end card each cap a score at 4.
- Watch numbers: none yet (the Monday metrics step has not run).
