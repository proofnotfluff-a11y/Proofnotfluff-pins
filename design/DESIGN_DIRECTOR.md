# Design director gate

Todd, Oct 17, 2026: "I just want to make sure that product design is so good the aesthetics cause these products to leap off the shelves." The workbook standard (design/WORKBOOK_STANDARD.md) says how to build; this file says how a finished product is judged, by a reviewer who did not build it.

## Who runs it and when

An independent reviewer (Agent tool, model "opus"), given only the rendered output and this file, never the build code or the builder's notes. It runs after the holdout check and before the Legal desk, on: every new product (all tabs rendered, screen and print), every page a buyer lands on (desktop 1280 and phone 390), every listing image set and every first video frame. A rebuild of a product that passed reruns it only on what changed.

## What it compares against

Before scoring, the reviewer looks at the three best-selling or best-reviewed competitors in the same category it can find through WebSearch and the vendors' own sites (never by loading Etsy pages: Etsy research comes only from the idea's recorded buyerProof notes, because the crew's Etsy page loads are capped and belong to the shop run), and writes one line per competitor on what makes their first impression work. The bar is "would a buyer choosing between these pick ours on looks alone".

## The score (1 to 5 each; pass is no score under 4 and an average higher than 4.6)

Todd, Oct 18, 2026, 1:38 pm: "Our threshold should be higher than 4.6". The average of the seven scores, to two decimals, must be 4.61 or more (it was 4.3 before Oct 18). A product that passed under the old bar is judged again against this one before its next promotion or rebuild.

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

## UX laws checklist (Todd, live chat, Oct 25, 2026: "If not doing already, employ these principals in design")

Every review of a page, product or flow also checks these 20, from the "20 UX laws to tell Claude" list Todd shared. Each line is the plain rule, then the check the reviewer runs. A clear miss is a note against the matching score above (most land in Hierarchy, Spacing or Polish); a miss that stops a buyer is a blocker.

1. Hick: reduce choices per screen. One primary action per screen or card; no more than about seven equal options in a group.
2. Fitts: make targets large. Every tap target at least 44 x 44 px on phones (inline links in running text excepted).
3. Jakob: follow familiar patterns. Logo top left goes home, search icon, menu icon, cards that look tappable.
4. Proximity: group related information. A price, its terms and its button sit together.
5. Miller: break content into chunks. Long pages split into named sections; lists of more than about seven get groups.
6. Doherty: keep interactions within 400 ms. Results update as you type, menus and search open at once, nothing waits on the network after a tap.
7. Von Restorff: highlight the primary action. One filled accent button; everything else quieter.
8. Minimize target distance: place key actions nearby. The next step is reachable from where the eye lands (sticky bars on phones, a header action).
9. Serial position: put essentials first (and last). The promise and the sample first; the next step again at the end.
10. Peak-end: end flows memorably. Every page ends on the next step, never a dead end.
11. Zeigarnik: show visible progress. Long pages show where you are (reading bar, on-this-page bar).
12. Pragnanz: simplify complex interfaces. Plain shapes, no decoration that carries no meaning.
13. Similarity: maintain pattern consistency. Same component, same look and behavior on every page.
14. Uniform connectedness: connect related elements visually. Related items share a box, a band or a line.
15. Tesler: use sensible defaults. Calculators open filled with a worked example; the system absorbs complexity.
16. Postel: be liberal in what you accept. Inputs take "$1,200", "1200", "25%" and "1.2k".
17. Error prevention and recovery: prevent errors proactively and make them recoverable. A short note under a bad field, never a silent wrong result; a reset or undo nearby.
18. Parkinson: reduce task completion time. Fewest taps from landing to the sample or the result; search for anything in a large set.
19. Occam and progressive disclosure: reveal complexity gradually. FAQs, full lists and fine print open on request.
20. Goal gradient and Pareto: make completion feel closer, and put effort on the 20 percent that drives 80 percent of results. The first step is free and small (the sample), and the steps that convert get the design time.
