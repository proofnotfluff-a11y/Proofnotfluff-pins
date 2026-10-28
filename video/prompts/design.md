# Gate 8: design (fresh reviewer)

You judge the look of one short vertical video (1080 x 1920) from its contact sheet (twelve frames with times) and its
first frame, against design/DESIGN_DIRECTOR.md and design/CAROUSEL_STANDARD.md (read both; the colors, type and data
rules apply to video frames too). Load the `anthropic-skills:impeccable` and `design:accessibility-review` skills
before scoring. You have not seen how it was built.

Fixed by the spec, not design choices to mark down: all text sits between y 270 and y 1250 and out of the right 150 px,
because Instagram's caption, account name and buttons cover the rest on a phone; the band below the captions holds only
the voice wave. Judge the composition inside that band. Frame one must show the number.

Score the seven criteria 1 to 5 exactly as DESIGN_DIRECTOR.md says (first impression, hierarchy, typography, color and
contrast, spacing and alignment, polish, trust). Pass: no score under 4 and an average of 4.61 or more. For every score
under 5, the exact change that would raise it (which frame, which element, to what).

Answer with JSON only:
{"pass": true or false, "score": {"first": n, "hierarchy": n, "type": n, "color": n, "spacing": n, "polish": n, "trust": n, "average": n.nn},
 "reasons": ["<frame time> <element>: <change>", ...]}
