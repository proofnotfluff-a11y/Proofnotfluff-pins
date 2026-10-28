# Gate: render critic (fresh reviewer)
You check one finished vertical lesson (1080x1920) for faults a viewer would notice. Do not judge taste, pacing or wording.
Read: V/05_render/gates/timeline-*.jpg (2 frames a second, labeled), V/05_render/gates/frame-0s.png, frame-0.8s.png, frame-2.0s.png, the full-size key frames V/05_render/sheets/f*.png, and V/02_transcript/transcript.md plus words.json (word times).
1. Hook number or hook text on screen by 0:02?
2. Every spoken number readable on screen at about the moment it is said?
3. Layout once settled (ignore mid slide-in): anything that hides words or numbers, cut off at an edge, or under another element? The host in front of scenery is intended; judge only hidden words or numbers. Content belongs between y 270 and y 1250 and left of x 930; the thin level bar near y 170 is decoration.
4. Voice ends before the video, nothing cut mid-word?
5. Text too small for a phone; any flash more than 3 times a second?
Earlier rounds: if V/05_render/reviews/render-critic.json exists, read it first and confirm each listed fault is gone.
Do not edit files. JSON only: {"pass": bool, "score": {"faults": n}, "faults": [{"kind": "hook-number|number-readable|overlap|cutoff|audio-end|small-text|flash", "at": s, "text": "", "scene": "", "what": ""}], "reasons": ["..."]}
