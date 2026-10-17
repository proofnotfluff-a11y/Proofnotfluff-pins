# Design director gate

Todd, Oct 17, 2026: "I just want to make sure that product design is so good the aesthetics cause these products to leap off the shelves." The workbook standard (design/WORKBOOK_STANDARD.md) says how to build; this file says how a finished product is judged, by a reviewer who did not build it.

## Who runs it and when

An independent reviewer (Agent tool, model "opus"), given only the rendered output and this file, never the build code or the builder's notes. It runs after the holdout check and before the Legal desk, on: every new product (all tabs rendered, screen and print), every page a buyer lands on (desktop 1280 and phone 400), every listing image set and every first video frame. A rebuild of a product that passed reruns it only on what changed.

## What it compares against

Before scoring, the reviewer looks at the three best-selling or best-reviewed competitors in the same category it can find through WebSearch and the vendors' own sites (never by loading Etsy pages: Etsy research comes only from the idea's recorded buyerProof notes, because the crew's Etsy page loads are capped and belong to the shop run), and writes one line per competitor on what makes their first impression work. The bar is "would a buyer choosing between these pick ours on looks alone".

## The score (1 to 5 each; pass is no score under 4 and an average of 4.3 or more)

1. First impression (the first screen, the first image, the first tab): one clear focal point, the main answer or promise visible without scrolling.
2. Hierarchy: a stranger finds the three things that matter in five seconds; headings, numbers and labels are clearly ranked.
3. Typography: one family, deliberate sizes and weights, no cramped or orphaned text, numbers aligned, nothing cut off.
4. Color and contrast: the palette in the standard, used with intent; contrast passes WCAG AA for body text; color never carries meaning alone.
5. Spacing and alignment: consistent rhythm, generous margins, nothing touching an edge, grid alignment holds at both widths.
6. Polish: no stray characters, inconsistent capitalization, placeholder text, broken icons, odd wraps, or default-looking controls.
7. Trust: it looks like a professional product a business would pay for, not a template; brand consistent with the site and the other products.

## What it returns

PASS or FAIL on the first line, the seven scores, the competitor lines, and for every score under 5 the exact change that would raise it (where, what, to what). A FAIL goes back to the builder with that list; the builder fixes and the reviewer judges again from fresh renders. Two FAILs on the same item go to the live session or the COO, who decides; they never loop.

## Rules

- Judge only what a buyer sees. Never rewrite numbers, claims or legal text; send those notes to the holdout check or the Legal desk.
- No copying a competitor's design, layout, wording or images: learn the mechanism, never the asset.
- No em dashes anywhere, as everywhere.
