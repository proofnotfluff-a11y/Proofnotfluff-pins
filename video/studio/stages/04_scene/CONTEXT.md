# 04_scene: the animation

**Reads:** `03_cues/cues.md` and `cues.json`, `01_voice/brief.md`, `_shared/kit.md`, `_shared/desk.md`, `_shared/looks.md`, `_runtime/*.js`
**Makes:** `04_scene/scene.js`

1. `scene.js` defines `SCENE = {look, sections: {<cue id>: (k, T) => ...}}`: one function per top-level cue, drawing
   the frame at time `T` with the kit `k`. `k.S('map.count')` is a cue's start, `k.live('map.count')` is true from
   that cue to the next one at its level, `k.p(a, b)` eases 0 to 1 between two times. Draw only from the kit and the
   brief's numbers: no number typed into scene.js that is not in the brief.
2. Frame rules (Instagram covers the rest): text between y 270 and y 1250 and left of x 930 (lint fails scene text past 930 from lessons dated 2026-11-26; its old edge was 950); captions sit in the band
   the kit gives them; the hook's number is on screen by 0.5 s; nothing under 42 px tall.
3. The opening (IMPROVE 00a; Todd, Oct 29, 10:26 am, "get this fixed today"): frame 0 is the cover (the on-screen hook in
   5 to 8 words, its source, no host). The picture then changes by 1 s and again before 3 s, each a real change of
   shot (a cut to a close-up of the thing being said, a room, a big card), not a slam or sparks, and the host is on screen
   by 3 s. The on-screen hook stays readable through the cuts (on a title plate in the close-up). `anim.py hook` measures
   it (a change is 8% or more of the frame, against the last change) and `lint` fails a lesson that misses it. Worked
   example: lesson 3 (videos/2026-10-30-markup-margin, the bench close-up cut in on "job", out on "Is").
4. Kit pieces first (studio change 4; _shared/kit.md "Pieces"): the send card is `k.sendCard`, the cover `k.coverBoard`, source lines `k.sourceTag`, the EXAMPLE tag `k.exampleTag`, and a shot change inside a section `k.cut`. They keep text left of x 930, at size 52 or more, the tag on its own row and the send card still. Hand-build one only when the lesson needs a shape they cannot make, and say why in a scene.js comment.
5. `python3 video/studio/anim.py stills <slug>` renders the opening every 0.5 s to 3 s, then a frame at every cue, into sheets.

6. `python3 video/studio/anim.py fresh <slug>` (studio change 2): the cover and the first hook cut against the two lessons before (text layout match under 0.85), and send and close transitions not both the same as one of them. Lint runs it again from lessons dated 2026-11-26.

**Check:** read the sheets. Nothing overlaps or is cut off, every number readable while it is said, the cast never
covers data. Fix and re-run `stills` until clean, then render.
