"""ProofNotFluff dashboard layer for openpyxl (design standard v3, Oct 6, 2026).

Builds on wb_style.py (workbook properties, validation, protection, print, text metrics)
and adds the card-and-tile layout every working tab uses:

    warm canvas  >  white cards with a hairline frame  >  label | value rows on a fixed grid
    hero tiles at the top (the answers), inputs on the left, the build-up on the right,
    in-cell bars instead of charts (they render the same in Excel and Google Sheets).

All rows inside the card zone share one height (GRID_ROW) so two card columns can sit
side by side without one column squeezing the other. Nothing here needs a macro, a chart
object, a table, data bars or a dynamic array.
"""
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

import wb_style as S

T = {  # design tokens (hex, no #)
    "canvas": "F3F1EC",      # sheet background
    "card": "FFFFFF",
    "frame": "E2DDD3",       # card outline
    "hair": "EFEBE4",        # row dividers inside a card
    "ink": "1D2433",
    "ink2": "4A5163",        # secondary text
    "muted": "7B818D",       # eyebrows, helper text (4.6:1 on white)
    "on_ink": "FFFFFF",
    "on_ink_soft": "B9C0CE",
    "accent": "C8502F",
    "accent_tint": "FBEAE4",
    "teal": "2E6B66",
    "teal_tint": "E2EFEC",
    "gold": "A87C1F",
    "blue": "2F5F9E",
    "input_fill": "FFF6D6",
    "input_line": "E3C978",
    "input_text": "1F4E9E",
    "total_tint": "F6F3EE",
}
FONT = S.FONT
GRID_ROW = 21          # every row inside the card zone
BAR_CHAR = "█"    # full block, drawn with REPT() for in-cell bars


def f(size=10, bold=False, color="ink", underline=None, italic=False):
    return Font(name=FONT, size=size, bold=bold, italic=italic, underline=underline, color=T.get(color, color))


def fill(key):
    return PatternFill("solid", fgColor=T.get(key, key))


def side(key, style="thin"):
    return Side(style=style, color=T.get(key, key))


def cols(a, b):
    from openpyxl.utils import column_index_from_string as ci, get_column_letter as gl
    return [gl(i) for i in range(ci(a), ci(b) + 1)]


def h(ws, row, height):
    ws.row_dimensions[row].height = height


def paint_canvas(ws, last_row, last_col="Z"):
    for r in range(1, last_row + 40):
        for c in cols("A", last_col):
            cell = ws[f"{c}{r}"]
            if cell.fill is None or cell.fill.fill_type is None:
                cell.fill = fill("canvas")


# ---------------------------------------------------------------- page header
def page_header(ws, title, tagline, as_of, span=("B", "K"), brand="ProofNotFluff", side_cols=3):
    """Rows 1-5: breathing room, title (brand at right), color strip, tagline (as-of at right).
    Returns the next row."""
    c0, c1 = span
    allc = cols(c0, c1)
    t_end, s_start = allc[-side_cols - 1], allc[-side_cols]
    h(ws, 1, 14)
    ws[f"{c0}2"] = title; ws[f"{c0}2"].font = f(20, True); ws[f"{c0}2"].alignment = Alignment(vertical="center")
    ws.merge_cells(f"{c0}2:{t_end}2")
    ws[f"{s_start}2"] = brand; ws[f"{s_start}2"].font = f(9, True, "muted")
    ws[f"{s_start}2"].alignment = Alignment(horizontal="right", vertical="center")
    ws.merge_cells(f"{s_start}2:{c1}2")
    h(ws, 2, 32)
    S.color_strip(ws, f"{c0}3"); h(ws, 3, 12)
    ws[f"{c0}4"] = tagline; ws[f"{c0}4"].font = f(10, False, "ink2"); ws[f"{c0}4"].alignment = Alignment(vertical="center")
    ws.merge_cells(f"{c0}4:{t_end}4")
    ws[f"{s_start}4"] = as_of; ws[f"{s_start}4"].font = f(9, False, "muted")
    ws[f"{s_start}4"].alignment = Alignment(horizontal="right", vertical="center")
    ws.merge_cells(f"{s_start}4:{c1}4")
    h(ws, 4, 20)
    h(ws, 5, 14)
    return 6


# ---------------------------------------------------------------- frames
def frame(ws, top, bottom, left, right, bg="card", line="frame"):
    """Paint a card: fill the block and draw a hairline outline."""
    cs = cols(left, right)
    for r in range(top, bottom + 1):
        for i, c in enumerate(cs):
            cell = ws[f"{c}{r}"]
            if cell.fill is None or cell.fill.fill_type is None:
                cell.fill = fill(bg)   # keep input, tint and chip fills already set
            b = Border(
                left=side(line) if i == 0 else None,
                right=side(line) if i == len(cs) - 1 else None,
                top=side(line) if r == top else None,
                bottom=side(line) if r == bottom else None,
            )
            # keep any inner borders already set (row dividers) on the inner cells
            old = cell.border
            cell.border = Border(left=b.left or old.left, right=b.right or old.right,
                                 top=b.top or old.top, bottom=b.bottom or old.bottom)


def tile(ws, top, left, right, eyebrow, value_formula, fmt, sub_formula, dark=False, value_size=28):
    """A hero tile: 4 rows (eyebrow, number, sub line, bottom pad). Text sits in the first inner
    column, merged across the tile. Returns (value_cell, sub_cell, next_row)."""
    inner = cols(left, right)[1:-1]
    a, z = inner[0], inner[-1]
    bg = "ink" if dark else "card"
    rows = [(top, 20), (top + 1, 44), (top + 2, 20), (top + 3, 10)]
    for r, ht in rows:
        h(ws, r, ht)
    e = ws[f"{a}{top}"]; e.value = eyebrow
    e.font = f(8, True, "on_ink_soft" if dark else "muted"); e.alignment = Alignment(vertical="bottom")
    v = ws[f"{a}{top+1}"]; v.value = value_formula; v.number_format = fmt
    v.font = f(value_size, True, "on_ink" if dark else "ink"); v.alignment = Alignment(horizontal="left", vertical="center")
    s = ws[f"{a}{top+2}"]; s.value = sub_formula
    s.font = f(9, False, "on_ink_soft" if dark else "ink2"); s.alignment = Alignment(vertical="top")
    for r in (top, top + 1, top + 2):
        ws.merge_cells(f"{a}{r}:{z}{r}")
    frame(ws, top, top + 3, left, right, bg=bg, line="ink" if dark else "frame")
    return v, s, top + 4


# ---------------------------------------------------------------- card content
class Card:
    """Rows inside one card column. Usage:
        k = Card(ws, top=12, left="B", label="C", value="D", right="E", extra=None)
        k.title("Your numbers", "Type over the yellow cells.")
        k.eyebrow("WHAT YOU WANT")
        k.input("Take-home pay you want", 60000, fmt, name=..., validation=..., prompt=...)
        k.calc("Revenue you need", "=...", fmt, total=True)
        k.close()   # pads the bottom and draws the frame; k.end is the last row
    """

    def __init__(self, ws, top, left, label, value, right, extra=None, wb=None):
        self.ws, self.top, self.left, self.label, self.value, self.right, self.extra, self.wb = \
            ws, top, left, label, value, right, extra, wb
        self.r = top
        self._pad()

    def _row(self):
        h(self.ws, self.r, GRID_ROW)
        r = self.r; self.r += 1
        return r

    def _pad(self):
        return self._row()

    def _span_cells(self):
        return cols(self.label, self.extra or self.value)

    def title(self, text, sub=None):
        r = self._row()
        c = self.ws[f"{self.label}{r}"]; c.value = text; c.font = f(12, True)
        c.alignment = Alignment(vertical="center")
        self.ws.merge_cells(f"{self.label}{r}:{(self.extra or self.value)}{r}")
        if sub:
            r = self._row()
            s = self.ws[f"{self.label}{r}"]; s.value = sub; s.font = f(9, False, "muted")
            s.alignment = Alignment(vertical="top")
            self.ws.merge_cells(f"{self.label}{r}:{(self.extra or self.value)}{r}")
        return r

    def eyebrow(self, text):
        r = self._row()
        c = self.ws[f"{self.label}{r}"]; c.value = text; c.font = f(8, True, "muted")
        c.alignment = Alignment(vertical="bottom")
        self.ws.merge_cells(f"{self.label}{r}:{(self.extra or self.value)}{r}")
        for k in self._span_cells():
            self.ws[f"{k}{r}"].border = Border(bottom=side("hair"))
        return r

    def _label(self, r, text, bold=False, color="ink"):
        c = self.ws[f"{self.label}{r}"]; c.value = text; c.font = f(10, bold, color)
        c.alignment = Alignment(vertical="center")

    def _divider(self, r, style="hair", top=False):
        for k in self._span_cells():
            cell = self.ws[f"{k}{r}"]
            if top:
                cell.border = Border(top=side("ink"), bottom=cell.border.bottom)
            else:
                cell.border = Border(bottom=side(style), top=cell.border.top)

    def input(self, text, value, fmt, name=None, validation=None, prompt=None, prompt_title=None):
        r = self._row()
        self._label(r, text)
        c = S.input_cell(self.ws, f"{self.value}{r}", value, fmt, name=name, wb=self.wb, validation=validation,
                         prompt=prompt, prompt_title=prompt_title or text[:32])
        c.fill = fill("input_fill"); c.font = f(10, True, "input_text")
        c.border = Border(left=side("input_line"), right=side("input_line"), top=side("input_line"), bottom=side("input_line"))
        if self.extra:
            self._divider(r)
            self.ws[f"{self.value}{r}"].border = c.border
        return r

    def calc(self, text, formula, fmt, bold=False, total=False, color="ink", tint=None, label_color="ink"):
        r = self._row()
        self._label(r, text, bold=bold or total, color=label_color)
        c = self.ws[f"{self.value}{r}"]; c.value = formula; c.number_format = fmt
        c.font = f(10, bold or total, color); c.alignment = Alignment(horizontal="right", vertical="center")
        if total:
            self._divider(r, top=True)
        else:
            self._divider(r)
        if tint:
            for k in self._span_cells():
                self.ws[f"{k}{r}"].fill = fill(tint)
        return r

    def bar(self, text, formula, fmt, max_ref, color, width=11, bold=False):
        """label | value | in-cell bar (needs an extra column)."""
        r = self.calc(text, formula, fmt, bold=bold)
        b = self.ws[f"{self.extra}{r}"]
        b.value = f'=IFERROR(REPT("{BAR_CHAR}",MAX(0,ROUND({self.value}{r}/{max_ref}*{width},0))),"")'
        b.font = f(9, False, color); b.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        return r

    def text(self, text_or_formula, size=9, color="muted", bold=False, height=None):
        r = self._row()
        c = self.ws[f"{self.label}{r}"]; c.value = text_or_formula; c.font = f(size, bold, color)
        c.alignment = Alignment(vertical="center", wrap_text=True)
        self.ws.merge_cells(f"{self.label}{r}:{(self.extra or self.value)}{r}")
        if height:
            h(self.ws, r, height)
        return r

    def close(self):
        self._pad()
        self.end = self.r - 1
        frame(self.ws, self.top, self.end, self.left, self.right)
        return self.end


def status_rule(ws, cell_range, formula_bad, bad="accent", good="teal", fill_tint=True, anchor=None):
    """Conditional color: bad when formula_bad is TRUE, good otherwise (font, and tint when asked)."""
    first = anchor or cell_range.split(":")[0].replace("$", "")
    col = "".join(ch for ch in first if ch.isalpha()); row = "".join(ch for ch in first if ch.isdigit())
    ref = f"${col}${row}"
    is_bad, is_good = f'AND({ref}<>"",{formula_bad})', f'AND({ref}<>"",NOT({formula_bad}))'
    ws.conditional_formatting.add(cell_range, FormulaRule(
        formula=[is_bad], font=Font(color=T[bad], bold=True),
        fill=PatternFill("solid", bgColor=T["accent_tint"]) if fill_tint else None, stopIfTrue=True))
    ws.conditional_formatting.add(cell_range, FormulaRule(
        formula=[is_good], font=Font(color=T[good], bold=True),
        fill=PatternFill("solid", bgColor=T["teal_tint"]) if fill_tint else None, stopIfTrue=True))


def highlight_rule(ws, cell_range, formula):
    """Tint a row (for example the billable share the buyer typed)."""
    ws.conditional_formatting.add(cell_range, FormulaRule(
        formula=[formula], font=Font(bold=True, color=T["ink"]), fill=PatternFill("solid", bgColor=T["input_fill"])))
