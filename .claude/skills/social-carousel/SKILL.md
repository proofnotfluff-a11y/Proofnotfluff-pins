# social-carousel (weekly; Todd, Oct 25, 2026)

One job: build one on-brand LinkedIn carousel in Canva from this week's real data, gate it, and hand it to Todd to post. Organic only. Never post, schedule or publish anywhere; Todd posts (CONSTITUTION 3).

## Inputs (Reads)
- design/CAROUSEL_STANDARD.md (the look), design/DESIGN_DIRECTOR.md (the gate), cmo/CONVERSION_STANDARD.md sections 1, 2 and 5, cmo/HOOKS.md (hook formulas), coo/DECISIONS-2026-10-25.md, cmo/CAROUSELS.md (past carousels, the rotation).
- The design system with the Artifact tool, read: https://claude.ai/artifact/JVnEj2N1KaTxoHMzMkQXHK paths project/README.md and project/tokens.json.
- Data, one per week in turn (the topic after the last line in cmo/CAROUSELS.md): pest = permits/inspections-chicago/daily.json (pestLast7, pestByDate, seat); construction = permits/chicago/sample.json through tools/question_site.py stats("chicago_construction"); licenses = permits/licenses-chicago/sample.json; question = the newest page in seo/QUESTIONS.md. Offer facts from site/pages.json only.

## Process (Executes)
1. Date from bash. Preflight. Pick the topic. Write the slide copy to cmo/carousels/<date>.json: per slide the text and, per number, its file and key. 6 to 8 slides, the pattern in the standard.
2. Facts gate: a fresh Agent (model fable, else opus) recomputes every number from the files and checks the copy rules (dashes, banned words via tools/legal_scan.py, no business with a failed record). PASS or numbered fixes. One fix round.
3. Canva build. `list-brand-kits`; if a "ProofNotFluff" kit exists use `generate-design` (design_type instagram_post, brand_kit_id), else `create-design` (format "Instagram Post (Portrait)"). The brief carries the standard's exact hex values, sizes, margins, the five bars and every slide's exact text. Pick the candidate closest to the standard, then `create-design-from-candidate`.
4. Enforce with `read-design` (open_transaction) and `edit-design`: replace any text that differs from the json; `recolor_element` and `format_text` to the exact hexes and sizes; `insert_shape` the five bars and footer where missing; `delete_element` stock art, icons, gradients and stray shapes. Read thumbnails of every page; if not ready, wait and read again. Show nothing to Todd until the commit.
5. Design gate: a fresh Agent (model opus) that never saw the build gets the thumbnails, design/DESIGN_DIRECTOR.md and design/CAROUSEL_STANDARD.md, loads the `anthropic-skills:impeccable` critique and `design:accessibility-review` skills, and scores the seven criteria. Pass: none under 4, average 4.61 or more. One fix round through step 4; a second FAIL goes to Todd with the scores.
6. Commit the edit transaction only after both gates PASS. Export a PDF with `export-design` (link for Todd; this sandbox cannot download it).

## Outputs (Writes)
- cmo/carousels/<date>.json and one line in cmo/CAROUSELS.md: date, topic, Canva link, gate scores, the UTM link. check_repo exits 0, push to main.
- One PushNotification to Todd: the Canva edit link, the caption (hook first, 60 to 120 words, no link in the body), the first comment ("Free sample: <url>?utm_source=linkedin&utm_medium=social&utm_campaign=carousel&utm_content=<date>-<topic>"), and the gate scores. On a blocker (preflight, a gate's second FAIL, Canva unreachable) the notification says what and stops.
- Never: posting, a Canva brand kit or account change, a paid Canva feature, Higgsfield or any video tool.
