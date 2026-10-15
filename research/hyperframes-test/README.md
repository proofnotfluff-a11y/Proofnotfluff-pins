# HyperFrames side-by-side test (CMO, Oct 15, 2026; Todd: "Do what you recommend")

What: the Oct 14 #22 Short ("A long drive adds $65 to the same job") rebuilt in HeyGen's HyperFrames (npm hyperframes 0.8.159, Apache 2.0) with the same script, numbers, voice, music and beat timing as the make_demo.py render, so only the picture differs. Source: index.html here (assets: the make_demo mix, brand fonts, a local gsap 3.14.2). Frames: frames-22.png (left make_demo.py, right HyperFrames, at 0.1, 11, 16.2 and 21 s).

How it ran in the cloud sandbox: `npm i hyperframes`, `HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`, `npx hyperframes check` (lint, layout, contrast; it caught the fix row overlapping the captions on the first pass), `npx hyperframes render -q high`: 31.5 s video rendered in 1 min 20 s (screenshot capture, software GPU), 2.4 MB, -14.2 LUFS (the make_demo master: -14.1). No account, key or spend; nothing installed on Todd's computer.

Findings
- Same story, same look family. HyperFrames added a moving route bar on the 40-mile row, count-up numbers and a wipe into the end card; make_demo.py keeps its camera that follows the active row and dims the others, which keeps a phone viewer's eye on one number at a time.
- Its `check` gate (layout overlap, text occlusion, contrast, timing lint) is stronger than our render-time checks; its first pass found a real overlap.
- Its default would have opened on an empty frame; frame one had to be forced to show the hook and the product (our CONVERSION_STANDARD rule).
- Captions, voice, music rotation, the sonic logo and the safe band are ours either way: HyperFrames only replaces the picture layer.

Verdict: no switch. make_demo.py stays the renderer; worth borrowing into it: count-up on result values, the route/progress bar for distance or time rows, and a layout-overlap check before render. The talking-head features in the tutorial (text behind a head, hand tracking) do not apply to a faceless brand.
