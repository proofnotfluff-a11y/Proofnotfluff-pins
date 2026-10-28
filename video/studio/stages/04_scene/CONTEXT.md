# 04_scene: the animation

**Reads:** `03_cues/cues.md` and `cues.json`, `01_voice/brief.md`, `_shared/kit.md`, `_shared/desk.md`, `_shared/looks.md`, `_runtime/*.js`
**Makes:** `04_scene/scene.js`

1. `scene.js` defines `SCENE = {look, sections: {<cue id>: (k, T) => ...}}`: one function per top-level cue, drawing
   the frame at time `T` with the kit `k`. `k.S('map.count')` is a cue's start, `k.live('map.count')` is true from
   that cue to the next one at its level, `k.p(a, b)` eases 0 to 1 between two times. Draw only from the kit and the
   brief's numbers: no number typed into scene.js that is not in the brief.
2. Frame rules (Instagram covers the rest): text between y 270 and y 1250 and left of x 930; captions sit in the band
   the kit gives them; the hook's number is on screen by 0.5 s; nothing under 42 px tall.
3. `python3 video/studio/anim.py stills <slug>` renders a frame at every cue (and frame one) into sheets.

**Check:** read the sheets. Nothing overlaps or is cut off, every number readable while it is said, the cast never
covers data. Fix and re-run `stills` until clean, then render.
