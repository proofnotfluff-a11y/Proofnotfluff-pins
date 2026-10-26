# Carousel standard (rendered in code, Instagram and Facebook)

Todd, Oct 25, 2026: the first Canva carousel "doesn't follow our brand palette and design standards"; carousels are made in Canva, organic only, Todd posts. This file says how a carousel looks. Brand truth: the ProofNotFluff design system https://claude.ai/artifact/JVnEj2N1KaTxoHMzMkQXHK (project/README.md, project/tokens.json; read with the Artifact tool). Where this file and the system differ, the system wins on a value, this file on a carousel rule. Judged by design/DESIGN_DIRECTOR.md (pass: no score under 4, average 4.61 or more).

## Format
- 1080 x 1350 portrait (4:5), 7 slides, rendered by tools/make_carousel.py (Todd, Oct 25: "Build in code"; Canva is no longer used for carousels) and posted to Instagram and the Facebook Page (.claude/skills/social-carousel/SKILL.md).
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
- Poppins only for display (titles, numbers, eyebrows, footer); Inter for sentences. Both are bundled in docs/assets/fonts; titles and body wrap balanced, so no orphan words. Two families at most.
- Cover number 300 px Poppins Bold, tabular; cover title 72 px Bold, line height 1.05, at most 3 lines; slide title 60 px Bold, at most 3 lines; eyebrow 26 px Bold uppercase, letter spacing 8%; body 36 px Regular, line height 1.35, at most 3 lines and 25 words; chart labels 30 px Medium. Nothing under 22 px. Left aligned, never centered paragraphs. No orphan word on a line of its own in a title.

## Slide pattern
1. Hook (ink): eyebrow (topic, accent-on-ink), the one number huge, a title that says what it counts in the buyer's words, the date range in on-ink-soft.
2. Proof: the number broken down (a bar chart or 3 tiles: white cards, label 22 px uppercase muted, value 96 px ink).
3. Where: neighborhoods or builders as a ranked list in a card, 5 rows at most.
4. Why it matters to the buyer: one sentence, one fact, no claim the data does not show.
5. What we do to the data: what comes in, what we drop and why, what is left, with the counts from the data file (Todd, Oct 25: the source is named for trust on the data slides' source line, never as a how-to).
6. The offer (one product, its live price and terms from site/pages.json).
7. CTA (ink): "See this week's free sample" and the domain; the link itself goes in the first comment.

## Copy
Plain words, second person, one idea per slide, every number from a repo data file read in the run, its source on the slide. No em or en dashes, no hype words (tools/legal_scan.py), no guarantees, no invented people or results, no restaurant or other business named with a failed record. Builders from City permits may be named as on the live pages.

## Rules that pass the design gate (Todd, live chat, Oct 26, 2026: "create rules so the design has a higher chance of passing")
Why carousels failed (Oct 25 and 26, six design gates, 3.86 to 4.43): the gate needs an average of 4.61, so at least 5 of the 7 scores must be a 5. Every fail had first impression at 5 and the rest stuck at 4 for the same few things: data slides top heavy with 170 to 370 px of empty canvas, the offer slide starting lower than the others, list type too small, a number said twice, eyebrow and sub saying the same thing, and a week count mixed into a month story. tools/make_carousel.py now builds the fixes in and refuses a render that breaks them.
- Fill the frame: on canvas slides (2 to 6) the eyebrow starts at y 186 and the data card grows to the source line. A render with more than 120 px empty under the content fails (tool check).
- Data is big: tiles carry a flat ink bar in proportion to their value; ranked rows are 40 px names and 56 px values, 3 to 5 rows, no rank column (the order is the rank; ties read as typos); the why card number is 280 px; bars are 96 px tall with 30 px Medium ink2 labels; the price is 112 px on one line.
- Say each number once: the why card number never repeats in its title (tool check). Title the meaning ("Most hold their first City license"), card the number.
- Order on every data slide: eyebrow, title, the data card, then one sentence under it.
- Eyebrow and sub never repeat each other (tool check). Sentence case titles, except the product name on the offer slide (tool check).
- One time window per carousel. A slide with a different window names it in the eyebrow ("LAST 7 DAYS, BY AREA").
- Slide 7 carries one proof line under the button saying what the free sample shows, from the page or the data file, and starts on the same top line as slide 1 (tool sets it).
- A number appears once per slide: a title never repeats a number its tiles, rows, bars or card show (tool check, all but the cover). Title the meaning ("Fewer than a third make the list").
- Every card label looks the same: 22 px uppercase muted Poppins, chart labels included. Curly apostrophes everywhere (tool sets them).
- A part of a whole gets a flat ink bar in proportion ("122 of 216": the why card takes "of" and draws it).
- The offer card is top aligned and lists what the buyer gets in 2 to 4 short lines with teal checks ("includes", each from site/pages.json), so the card shows the deliverable rather than empty space.
