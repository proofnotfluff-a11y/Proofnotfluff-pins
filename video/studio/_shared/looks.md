# Looks: one scene, any style

`SCENE.look` picks one; the kit draws the same scene in it (`_runtime/looks.js`).

| Look | What it is | Palette | Type |
|---|---|---|---|
| `clean` | the house look: warm canvas, ink, one accent; soft shadows | ProofNotFluff (#F3F1EC, #1D2433, #C8502F, #2E6B66) | Poppins, Inter |
| `pixel` | 16-bit: drawn at a third of the size, snapped to a 16-color palette, hard edges | dark plum ground, cream, accent orange | Poppins, snapped to pixels |
| `blueprint` | a drafting sheet: blue ground, grid, white line work, dimension marks | #123A6B, white, pale blue | Inter caps, wide tracking |
| `chalk` | hand-drawn: black board, chalky wobbling lines, one orange | #111, off-white, #E88062 | Poppins, slight hand jitter |

A look changes how things are drawn, never what they say. The facts and frame rules are the same in every look.

## Motion (arcade; Todd, Oct 28, 1:33 pm: "keep things moving"; rules from research run 2026-10-28-viral)
The player adds these to every arcade lesson; a scene adds the rest from the kit (`k.slam`, `k.burst`, `k.sweep`, `k.motes`).
- A hook card in the first 2.4 s: the hook in 5 to 8 words, its number slammed in, the source on screen from the start.
- The opening cuts (IMPROVE 00a): the picture changes by 1 s and twice in the first 3 s, the host is on by 3 s, the hook
  words stay up through the cuts (stages/04_scene/CONTEXT.md 3; `anim.py hook`, in `lint`).
- Every key number counts up or slams in as it is said, and lands with sparks. Highlight what matters (`k.sweep`).
- A new visual beat every 2 to 4 s (a slide-in, a count, a stamp); each beat steps the camera in a little (the zoom ladder).
- The camera leads the beat: it starts toward a beat's focus 6 frames before the cue and eases in (most of the way there
  on the word). Its position sits on whole pixels, so the pixel grid never swims.
- A stamp hits: the scene freezes for 3 frames with a 1 pixel shiver (the voice and Snow keep going), then lets go.
  A scene element stamped with `k.stampIn` also squashes (1.20 x 0.85 for 2 frames, 0.95 x 1.05 for 1) and settles.
- Shake only on a real hit, and small: each stamp adds a bit of "trauma" that drains in about a fifth of a second; the shake
  is trauma squared, smooth, on whole pixels, 3 pixels at most (a normal stamp moves about 1). Never more than once in 10 s.
- Rooms change in 12 frames: 5 closing over the old room, the cut, 1 held, 6 opening. The new room picks the move:
  blinds (workshop), a chalk wipe (blackboard), a garage door (garage), an iris on Snow's head (framing).
- Snow is alive: his mouth follows the voice (4 shapes from `mouth.js`, the beard drops a pixel when he opens wide); he
  blinks every 2.5 to 6 s, in the gaps between words when he can, sometimes twice; he breathes (a lit shoulder edge,
  then his chest up a pixel); after 8 to 12 s in one pose he fidgets (scratches his beard, fixes his cap, glances at the board).
- Every effect is worked out from the time alone, so any frame renders the same on its own.
- Every room has ambient motion; a level bar at the top fills as the lesson plays.
- Never flash more than 3 times a second.
