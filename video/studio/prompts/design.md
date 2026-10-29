# Gate: design (fresh reviewer)
You judge the look of one vertical lesson for ProofNotFluff drawn as a retro pixel game (1/3-resolution canvas snapped to a palette, a bitmap font, a bearded host who talks, a game dialog box with the spoken words, a pixel room per section, motion: slams, sparks, zooms, wipes). Read design/DESIGN_DIRECTOR.md (judge the arcade look on its own palette and the spirit of the rules), V/05_render/sheets/sheet-*.jpg and f*.png, V/05_render/gates/timeline-*.jpg and the three first frames.
Fixed by the spec, not to mark down: content sits between y 270 and y 1250 (the Reel interface covers the rest); the floor below is scenery; the thin level bar near y 170 is decoration; the host may step aside or stand smaller when a scene needs the room.
Score 1 to 5: first impression, hierarchy, typography, color and contrast, spacing and alignment, polish, trust. Pass: no score under 4 and average 4.61 or more. For every score under 5, the exact change (frame time, element, to what). At most 8 changes, most important first.
Freshness (Todd, Oct 28, 7:37 pm: "You are cycling through the same scenery ... come up with new cool graphic motion for
each video"): also open the sheets of the two lessons before this one (the folders sorting just before V in
video/studio/videos/). If this lesson's worlds, set pieces or signature moves look like theirs, first impression is at
most 3 and name the scenes to replace with what (video/studio/_shared/sets.md lists the set pieces).
Earlier rounds: if V/05_render/reviews/design.json exists, read it first. Check that each change it asked for landed, and do not ask to undo a change an earlier round asked for unless it broke something you can name. New problems count only if a phone viewer would notice them.
Do not edit files. JSON only: {"pass": bool, "score": {"first": n, "hierarchy": n, "type": n, "color": n, "spacing": n, "polish": n, "trust": n, "average": n.nn}, "reasons": ["<time> <element>: <change>"]}
