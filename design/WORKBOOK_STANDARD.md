# ProofNotFluff workbook standard

Every Excel and Google Sheets product the shop sells is built to this standard, with `tools/wb_style.py`. A reviewer fails a workbook against it; a builder follows it without judgment calls. Nothing here needs a macro, a form control, an Excel table, a slicer, a sparkline or a dynamic array: everything renders the same in Excel for Windows, Excel for Mac and Google Sheets.

Reference build: #20 Hourly Rate Quick Calculator v3, built by `engines/hourly-rate-quick-calculator/build_xlsx.py` with `tools/pnf_dash.py`. Copy its structure for every new calculator.

## 0. Version 3: the dashboard layout (Oct 6, 2026; overrides sections 2, 5 and 9 wherever they differ)

Todd's bar: it must look like a world-class model builder and a product designer made it. v2's single long list with a note on every row failed that bar. Every working tab is now a dashboard built with `tools/pnf_dash.py`:

- **Canvas and cards.** Warm canvas F3F1EC behind white cards with a hairline frame E2DDD3. Content never sits on the bare canvas except the page header.
- **Page header** (rows 1 to 5): title 20 pt bold, brand at the right, the five-bar strip, a one-line promise of what the tab does, the as-of date at the right.
- **Answer tiles** (rows 6 to 9, frozen): two tiles side by side. Left: the main answer on ink, 28 pt white, with one sub line. Right: the answer to "what does my current choice really pay", on white, its number colored teal or accent by a conditional rule, with a sub line that says how far from the goal in words.
- **Two card columns** on one grid: A 3 | B 2 | C 31 | D 14 | E 2 | F 3 | G 2 | H 24 | I 12 | J 17 | K 2 | L 3. Left column: the inputs card first ("Your numbers"), then the scenario checker. Right column: "How it's built" (the derivation as a short, readable sum with a total rule) and a sensitivity card. Full-width cards below for anything that needs both halves (a quote) and for Notes and sources.
- **One row height** (21 pt) for every row in the card zone so the two columns never squeeze each other. Card top and bottom padding is one row.
- **Inside a card**: title 12 pt bold, one muted 9 pt sub line, small-caps eyebrow labels (8 pt bold muted, uppercase) to group rows, hairline dividers EFEBE4 under each row, an ink rule on top of total rows, a soft tint F6F3EE on the key total.
- **No per-row notes.** Explanations live in each input's validation message (shown when the cell is selected), in the card sub line, and in the Notes and sources card. The worksheet reads like a product, not a memo.
- **Inputs**: fill FFF6D6, border E3C978, bold blue 1F4E9E numbers, unlocked, validated, named.
- **In-cell bars** (REPT of a full block in a colored 9 pt font, indent 1) to show proportions: where each unit of money goes, sensitivity tables. No chart objects.
- **Status in words and color**: a pill row or sub line written by formula ("Short of your take-home goal by $29,940 a year"), colored by a conditional rule that ignores blanks.
- **Blank-safe**: clear every input and the tab still shows zero error values and no misleading status text. Stress-test blank, extreme and changed inputs with `render_xlsx.py` before shipping.
- **Print**: page breaks between cards so no card splits across pages.
- **Start Here and Terms** use the same card language in one column (A 3 | B 2 | C 8 | D 62 | E 18 | F 2 | G 3): What it does, Three steps (accent numbers), How to read the cells (input chip, plain number, dark answer chip), The example, Good to know, Before you rely on a number; Terms carries the links and the full Terms of Use with bold lead-ins.

## 1. Tab structure

Order is fixed. Tab names are exactly these, in this order:

1. **Start Here** (tab color teal). What the product does, three numbered steps, the cell legend, the product's own help sections, then the short notice under "Before you rely on a number". Built with `start_here_tab()`.
2. **Working tabs**, one per job (tab color accent on the main one). A one-tab product has one working tab named for what it does ("Calculator", "Tracker", "Planner"). Never more than 6 working tabs; number them when there are more than 3 ("1 Your Numbers", "2 Price Sheet").
3. **Terms** (tab color note grey), always last. The full-version links, the Terms of Use text word for word from legal/README.md (or the product's own approved text), the two-line review ask. Built with `terms_tab()`.

No hidden sheets. No sheet named "Sheet", "More", "Notes" or "Data". Helper data lives at the bottom of the tab that uses it, under its own section header, never on a hidden tab.

## 2. Grid and spacing

- **Column A is a gutter**, width 2. The last content column is followed by a gutter of width 2 as well. Content never touches the sheet edge.
- **Working tab columns**: A 2 | B labels 40 | C values 14 | D gap 2 | E notes 52 | F 2. A second value column goes after C with D as its gap (B 40 | C 14 | D 14 | E 2 | F notes 48). Widths are in character units of the default font (Arial 10).
- **Start Here columns**: A 2 | B 10 (step numbers, legend swatches) | C 2 | D 56 | E 24 (brand, as-of date) | F 2.
- **Terms columns**: A 2 | B 78 | C 24 | D 2.
- **Row heights**: line rows 20 pt; section header rows 24 pt; spacer rows 8 pt between sections (4 pt between list items); title row 30 pt; strip row 12 pt; subtitle row 16 pt. A row with wrapped text gets its height from `text_height()` (Excel does not auto-fit rows written by openpyxl). Every row height is explicit; never leave one to the application.
- **Section spacing**: section header, then its rows, then one 8 pt spacer. Never two spacers in a row, never an empty 20 pt row as a spacer.
- **Merges** only for full-width text rows (title, subtitle, paragraphs, links). Never merge inside a label/value/note row and never merge a value cell.
- **Canvas**: the sheet background is painted with the canvas color from A1 to column Z, down to the last content row plus 30 (minimum 60 rows), so the buyer scrolls on paper, not white.

## 3. Typography

One family: **Arial**, set as the workbook default font (10 pt) so widths and unstyled cells match. Arial ships with Excel on Windows and Mac and is a Google Sheets built-in; LibreOffice substitutes Liberation Sans, which is metric-compatible, so renders are true to size.

| Role | Size | Weight | Color |
|---|---|---|---|
| Title | 18 | bold | ink |
| Section header | 11 | bold | ink |
| Label | 10 | regular (bold for subtotal, key and total rows) | ink |
| Value (input, calculated) | 10 | regular (bold on subtotal rows) | input text blue / ink |
| Note, helper text, subtitle, as-of date, sources | 9 | regular | note grey |
| Small text on the result card | 8 | bold for titles, regular for the line under the number | on-ink soft |
| Result card number | 24 | bold | white |
| Result card side number | 16 | bold | accent soft |
| Key cell | 11 | bold | white |
| Step number | 16 | bold | accent |

No italics (they render unevenly in Sheets and read as an afterthought). No all-caps except the two small titles on the result card. No underlines except hyperlinks. Sentence case for every heading and label.

## 4. Color palette

Derived from the pin and video brand tokens. Hex without `#` in code.

| Token | Hex | Use | Contrast |
|---|---|---|---|
| ink | 1D2433 | titles, labels, values, section rules, result card fill | 14.8:1 on canvas |
| ink_soft | 3A4152 | secondary labels | 9.7:1 on canvas |
| note | 5C6370 | notes, subtitles, as-of date, sources | 5.7:1 on canvas |
| canvas | FBF9F5 | sheet background | |
| paper | F5F2EC | deeper paper, print backgrounds in listing images | |
| calc | F2EEE6 | calculated cell fill | ink on calc 13.6:1 |
| line | D9D2C3 | input cell borders | |
| rule | ECE6DA | thin separators, legend gaps | |
| input_fill | FFF4CC | input cell fill | |
| input_text | 1F4E9E | input cell text | 7.2:1 on input_fill |
| accent | C8502F | negative results, warnings, step numbers (large text only), accent tab | white on accent 4.5:1; accent text on canvas 4.3:1, so 14 pt bold or larger only |
| accent_soft | F08A66 | the side number on the result card | 6.3:1 on ink |
| teal | 2E6B66 | positive results, Start Here tab color | white on teal 6.2:1 |
| purple 6B4FA0, blue 2F5F9E, gold 8A6A1F | | the color strip; blue also for hyperlinks | blue 6.2:1 on canvas |
| white | FFFFFF | text on ink, accent, teal | |
| on_ink_soft | C9CED9 | small text on ink fills | 9.9:1 on ink |

The brand motif, five short bars in the order accent, teal, purple, blue, gold, sits under every title as colored rich text in one cell (`color_strip()`). It is the only place purple and gold appear.

## 5. Cell roles

Each role has exactly one style. A reviewer can name the role of any cell from its look.

| Role | Fill | Text | Border | Locked | Helper |
|---|---|---|---|---|---|
| Input | input_fill FFF4CC | input_text 1F4E9E, 10 pt, right aligned | thin line D9D2C3 on all four sides | no | `input_cell()` |
| Calculated | calc F2EEE6 | ink, 10 pt, right aligned | none | yes | `output_cell()` |
| Subtotal (calculated) | calc | ink, bold | thin ink rule on top of label and value | yes | `output_cell(subtotal=True)` + `subtotal_label()` |
| Key result (secondary answer) | ink (or teal for good, accent for bad) | white, 11 pt bold | none | yes | `key_cell()` |
| Main answer | result card (section 9) | | | yes | `result_card()` |
| Label | none | ink, 10 pt, left, vertically centered | none | yes | `label()` |
| Note | none | note grey, 9 pt, wrapped | none | yes | `note()` |
| Warning | none | accent, 10 pt bold | none | yes | `warning()` |
| Section header | none | ink, 11 pt bold | medium ink rule under the whole span | yes | `section_header()` |
| Table heading | none | ink bold, first column left, others right | thin ink rule under | yes | `table_header()` |
| Hyperlink | none | blue, underlined | none | yes | `hyperlink()` |

Every value cell is vertically centered so tall note rows never leave numbers sitting at the bottom. Labels in B, values in C, notes in E. A note explains the formula in words ("Take-home divided by (1 minus the tax set-aside rate)") or names the cell it depends on.

## 6. Number formats

| Kind | Format | Example |
|---|---|---|
| Yearly or whole dollars | `"$"#,##0;-"$"#,##0` | $60,000, -$29,940 |
| Rates, per-hour and per-unit money, quotes | `"$"#,##0.00;-"$"#,##0.00` | $74.65 |
| Percent inputs and shares | `0%` (or `0.0%` when a decimal matters) | 25% |
| Counts, hours per year | `#,##0` | 1,920 |
| Job hours, decimals that matter | `#,##0.0` | 12.0 |
| Dates | `mmm d, yyyy` | Oct 6, 2026 |

Rules: no stray decimals (a yearly figure never shows cents; a rate always shows two). Negatives use a leading minus, never parentheses or red-only. A value whose sign carries meaning (a gap, a margin) also gets `negative_rule()`: accent when below zero, teal when zero or above. Percent cells are typed with the percent sign; the input message says so. Currency symbols are set by the number format, never typed into the cell.

## 7. Borders, gridlines, panes, zoom

- Gridlines off on every tab.
- Borders: input cells have the thin line border; section headers have a medium ink rule; subtotals a thin ink rule on top; table headings a thin ink rule under. Nothing else has a border. No boxes around sections, no outlines around notes, no double rules.
- Freeze panes on a working tab at the first row under the result card (so the answer stays on screen while the buyer scrolls the inputs). Start Here and Terms do not freeze.
- Zoom 100 on every tab. The active tab on open is Start Here, cell A1 selected.

## 8. Print setup

Every tab: Letter, portrait, fit to 1 page wide (any number tall), horizontally centered, margins 0.5 in left and right, 0.7 in top and bottom, header and footer at 0.3 in. Print area is the content span from row 1 to the last content row (never the canvas). Header: "ProofNotFluff" left, the product name right, 8 pt Arial. Footer: "Estimates only. Not professional advice. See the Terms tab." left and "Page &P of &N" right. This is the one-line notice legal/README.md asks for on every input tab. Put `page_break_before()` ahead of a section whose header would otherwise sit alone at the bottom of a page.

## 9. The result card

The main answer is impossible to miss: a three-row block across the content span, filled ink, directly under the title block and above the inputs, inside the frozen panes.

- Row 1 (16 pt): the question in 8 pt bold small text, on-ink soft, left; an optional side title at the right ("ROUNDED UP TO THE NEXT $5").
- Row 2 (40 pt): the number, 24 pt bold white, left; the optional side number 16 pt bold accent soft, right.
- Row 3 (16 pt): one sentence on what to do with it, 8 pt, on-ink soft ("Charge less than this and you will not reach your take-home target. Section 3 shows how it is built.").

One result card per working tab. Secondary answers use key cells inside their sections. The card's formula points at the section cell that computes the answer, so the build-up is one scroll away.

## 10. Protection, validation, names

- Every tab is protected, **no password**, so a buyer can unprotect from the Review tab or Data, Protect sheets and ranges. Formatting cells, columns and rows stays allowed (the buyer can change the currency symbol); inserting, deleting and sorting stay blocked so formulas survive.
- Formulas, labels and notes are locked. Inputs are unlocked. Nothing else is unlocked. Start Here says this in its legend.
- **Every input has data validation and an input message**: the kind (decimal, whole, list, date), the allowed range, a title (the label, 32 characters or fewer), a prompt that says the unit and gives an example ("Type a percent, for example 25%"), and a stop error that says the allowed range. `input_cell(validation=..., prompt=...)` does all of it.
- **Named ranges for every key input** (TakeHome, TaxRate, WeeksPerYear) so the Name box reads like a sentence. Formulas still use cell references so the sheet works even where names do not import.
- Formulas that can divide by zero or read a blank wrap in `IFERROR(..., "")`. Rendering with `tools/render_xlsx.py` must report zero error values.

## 11. The as-of date

Any rule, rate, limit, fee or deadline shows a visible as-of date: "Figures checked Oct 6, 2026" at the right of the subtitle row on every tab that uses one (the `as_of` argument of `title_block()`), the source and date in the note beside the cell that uses it, and the sources paragraph at the bottom of the working tab. The Terms tab repeats the date in the Information only paragraph.

## 12. Charts

Avoid them in calculators; a sorted table reads faster and prints the same everywhere. When a chart earns its place (a tracker over time, a payoff curve): bar or line only, one series in ink and at most one comparison series in accent, no 3D, no gradient, no gridlines heavier than the rule color, Arial 9 axis labels, title in sentence case, legend only with two or more series, anchored at the right of its section inside the content span, never over a cell the buyer edits. Google Sheets rebuilds Excel charts on import, so check the render after a Sheets round-trip before shipping.

## 13. Accessibility

- Text contrast 4.5:1 or better against its fill for text under 14 pt bold or 18 pt regular; 3:1 for larger. The palette table lists the ratios; accent text on canvas is allowed only at step-number size.
- Meaning never rides on color alone: a negative gap is also written with a minus sign, an input is also bordered and unlocked, a warning also says "warning" in words.
- Fonts never below 8 pt, and 8 pt only on the result card.
- Every input has a label in column B on the same row and an input message; a screen reader hears both.

## 14. Workbook properties

`new_workbook()` sets author and last-modified-by to ProofNotFluff, the title to the product name, the subject to the product and version, and the description to the copyright line. No comments, no tracked changes, no personal names anywhere in metadata (legal/README.md, section F).

## 15. Build and review flow

1. Build with `wb_style.py`; call `audit(wb)` before saving (it checks tab order, gridlines, protection, fonts, unlocked formulas, inputs without validation, em dashes).
2. `python3 tools/render_xlsx.py product.xlsx out/` and `--print`; open every PNG with the Read tool. Zero error values.
3. `python3 tools/legal_scan.py` on the zip.
4. Compare every number in the listing, the pin and the Start Here example against the rendered values.

## 16. What bad looks like

Fail a workbook that shows any of these:

- The main answer is one of several equally styled cells, or sits below the fold, or is not in a result card.
- Calibri, Segoe, Helvetica, Poppins or any font other than Arial in a cell.
- Gridlines on; a white sheet with floating cells; filled bars that run across empty columns.
- Values bottom-aligned in tall rows; labels and values at different heights; row heights that change from 19 to 33 to 47 with no reason.
- Input cells locked, or formulas unlocked, or no sheet protection, or a protection password.
- An input without a validation rule and an input message.
- Yearly dollars with cents, rates without cents, percents stored as 25 instead of 0.25, negatives in parentheses or red only.
- Notes in italic, headings in all caps, underlined text that is not a link, URLs that are not clickable.
- A rate or rule with no as-of date next to it.
- Merged cells inside a data row; a merged value cell.
- Printing that spills onto two pages wide, has no header or footer, or carries no product name.
- A section header orphaned at the bottom of a printed page.
- File author "openpyxl", "Todd" or blank; a tab named "Sheet1" or "More"; a hidden sheet.
- Any em dash, any banned word (seamless, unlock, elevate, effortless, game-changer, supercharge, delve, genuinely, honestly, straightforward).
- A render with a #DIV/0!, #REF!, #NAME?, #VALUE! or #N/A anywhere, including after clearing every input.
