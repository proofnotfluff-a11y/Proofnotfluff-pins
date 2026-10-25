# Carousel standard (Canva, LinkedIn first)

Todd, Oct 25, 2026: the first Canva carousel "doesn't follow our brand palette and design standards"; carousels are made in Canva, organic only, Todd posts. This file says how a carousel looks. Brand truth: the ProofNotFluff design system https://claude.ai/artifact/JVnEj2N1KaTxoHMzMkQXHK (project/README.md, project/tokens.json; read with the Artifact tool). Where this file and the system differ, the system wins on a value, this file on a carousel rule. Judged by design/DESIGN_DIRECTOR.md (pass: no score under 4, average 4.61 or more).

## Format
- 1080 x 1350 portrait (4:5), 6 to 8 slides, posted to LinkedIn as a PDF document. Canva format "Instagram Post (Portrait)".
- Margins 96 px all round; nothing closer to an edge. Content width 888 px. Spacing in steps of 8 (16, 24, 32, 48, 64, 96).
- Every slide: the five bars top left (each 56 x 10 px, 3 px corners, 12 px apart, in order bar-1 to bar-5), "ProofNotFluff" bottom left (Poppins Bold 24, ink2 on canvas, on-ink-soft on ink), the slide count bottom right ("2/7", same style). Data slides add one source line above the footer (22 px, image-muted).

## Color (exact hex, nothing else)
| Role | Token | Hex |
|---|---|---|
| Ground of proof slides | canvas | #F3F1EC |
| Cards on canvas | card | #FFFFFF, 1 px line #E2DDD3, 24 px corners |
| Titles, numbers, the ink band | ink | #1D2433 |
| Body on canvas or card | ink2 | #4A5163 |
| Eyebrow, the one key bar, the button | accent | #C8502F (bold 26 px or more on canvas) |
| Eyebrow on ink | accent-on-ink | #E88062 |
| Text on ink | white #FFFFFF, subtitles on-ink-soft #B9C0CE |
| Good results, check marks | teal | #2E6B66 |
| Brand bars only | bar-3 #6B4FA0, bar-4 #2F5F9E, bar-5 #A87C1F |
Mix: canvas about 60%, ink about 30%, accent at most 10% (one element per slide). Cover and last slide on the ink band; the slides between on canvas. No gradients, tints outside the tokens, photos, stock art, illustrations, icons, emoji or AI imagery. Charts are flat rectangles: ink bars, the one bar that matters in accent, value labels on the bars, no axes or gridlines.

## Type
- Poppins only for display (titles, numbers, eyebrows, footer); Inter (or the Canva brand kit body font) for sentences. Two families at most.
- Cover number 300 px Poppins Bold, tabular; cover title 72 px Bold, line height 1.05, at most 3 lines; slide title 60 px Bold, at most 3 lines; eyebrow 26 px Bold uppercase, letter spacing 8%; body 36 px Regular, line height 1.35, at most 3 lines and 25 words; chart labels 30 px Medium. Nothing under 22 px. Left aligned, never centered paragraphs. No orphan word on a line of its own in a title.

## Slide pattern
1. Hook (ink): eyebrow (topic, accent-on-ink), the one number huge, a title that says what it counts in the buyer's words, the date range in on-ink-soft.
2. Proof: the number broken down (a bar chart or 3 tiles: white cards, label 22 px uppercase muted, value 96 px ink).
3. Where: neighborhoods or builders as a ranked list in a card, 5 rows at most.
4. Why it matters to the buyer: one sentence, one fact, no claim the data does not show.
5. Check it yourself: the free public source, named.
6. The offer (one product, its live price and terms from site/pages.json).
7. CTA (ink): "See this week's free sample" and the domain; the link itself goes in the first comment.

## Copy
Plain words, second person, one idea per slide, every number from a repo data file read in the run, its source on the slide. No em or en dashes, no hype words (tools/legal_scan.py), no guarantees, no invented people or results, no restaurant or other business named with a failed record. Builders from City permits may be named as on the live pages.
