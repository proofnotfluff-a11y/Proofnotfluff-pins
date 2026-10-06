"""ProofNotFluff workbook design system for openpyxl.

Implements design/WORKBOOK_STANDARD.md. Every product workbook is built with
this module so the catalog looks like one family: paper canvas, Arial, ink
titles, a five-bar color strip, yellow input cells with blue numbers, soft
calculated cells, an ink result card for the main answer, a Start Here tab
first and a Terms tab last.

Typical use:

    from tools import wb_style as S            # or: import wb_style as S
    wb = S.new_workbook("Hourly Rate Quick Calculator")
    ws = wb.create_sheet("Calculator")
    S.set_widths(ws, {"A": 2, "B": 40, "C": 14, "D": 2, "E": 52, "F": 2})
    r = S.title_block(ws, "Hourly Rate Quick Calculator",
                      "Type in the yellow cells. Everything else updates on its own.",
                      as_of="Figures checked Oct 6, 2026")
    r = S.result_card(ws, r, "YOUR MINIMUM HOURLY RATE", "=C20", S.FMT["usd2"], ...)
    r = S.section_header(ws, r, "1. What you want to take home")
    S.label(ws, f"B{r}", "Take-home pay you want per year")
    S.input_cell(ws, f"C{r}", 60000, S.FMT["usd0"], name="TakeHome",
                 validation=("decimal", 0, None), prompt="Whole dollars, after tax.")
    S.note(ws, f"E{r}", "What you want left in your pocket for the year.")
    ...
    S.finish_sheet(ws, product="Hourly Rate Quick Calculator", last_row=r, freeze="A10")
    S.start_here_tab(wb, ...); S.terms_tab(wb, ...)
    wb.save(path)

Everything here works in Excel (Windows and Mac) and Google Sheets: no macros,
no form controls, no tables, no dynamic arrays. Rows that hold wrapped text get
an explicit height from text_height() because Excel does not auto-fit rows in
files written by openpyxl.
"""
import math
from datetime import date

from openpyxl import Workbook
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import column_index_from_string, get_column_letter
from openpyxl.utils.indexed_list import IndexedList
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.page import PageMargins
from openpyxl.worksheet.properties import PageSetupProperties
from openpyxl.worksheet.protection import SheetProtection

# ----------------------------------------------------------------------------
# Palette (hex, no #). Derived from the pin and video brand tokens. Contrast
# ratios against the canvas are listed in WORKBOOK_STANDARD.md.
# ----------------------------------------------------------------------------
PALETTE = {
    "ink": "1D2433",         # titles, labels, values
    "ink_soft": "3A4152",    # secondary labels
    "note": "5C6370",        # notes and helper text (5.3:1 on canvas)
    "canvas": "FBF9F5",      # sheet background (soft paper)
    "paper": "F5F2EC",       # deeper paper, used for the Terms and Start Here panels
    "calc": "F2EEE6",        # calculated cell fill
    "line": "D9D2C3",        # input borders
    "rule": "ECE6DA",        # thin separators
    "input_fill": "FFF4CC",  # input cell fill
    "input_text": "1F4E9E",  # input cell text (hard-coded numbers are blue)
    "accent": "C8502F",      # orange-red: warnings, "bad" results, step numbers
    "accent_soft": "F08A66", # accent on ink backgrounds
    "teal": "2E6B66",        # "good" results
    "purple": "6B4FA0",
    "blue": "2F5F9E",        # hyperlinks
    "gold": "8A6A1F",
    "white": "FFFFFF",
    "on_ink_soft": "C9CED9", # small text on ink fills
}
STRIP = ["accent", "teal", "purple", "blue", "gold"]  # the five-bar motif, in order

FONT = "Arial"
SIZE = {"title": 18, "section": 11, "label": 10, "value": 10, "note": 9, "small": 8,
        "result": 24, "result_side": 16, "key": 11, "step": 16}

FMT = {
    "usd0": '"$"#,##0;-"$"#,##0',
    "usd2": '"$"#,##0.00;-"$"#,##0.00',
    "pct": "0%",
    "pct1": "0.0%",
    "int": "#,##0",
    "num1": "#,##0.0",
    "num2": "#,##0.00",
    "hours": '#,##0 "hrs"',
    "hours1": '#,##0.0 "hrs"',
    "date": "mmm d, yyyy",
    "text": "@",
}

ROW = {"spacer": 8, "title": 30, "strip": 12, "subtitle": 16, "section": 24,
       "line": 20, "card_top": 16, "card_mid": 40, "card_bottom": 16}

_THIN_LINE = Side(style="thin", color=PALETTE["line"])
_THIN_INK = Side(style="thin", color=PALETTE["ink"])
_MED_INK = Side(style="medium", color=PALETTE["ink"])
_HAIR_RULE = Side(style="thin", color=PALETTE["rule"])


# ----------------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------------
def fill(key):
    return PatternFill("solid", fgColor=PALETTE[key])


def font(size=None, bold=False, color="ink", italic=False, underline=None):
    return Font(name=FONT, size=size or SIZE["value"], bold=bold, italic=italic,
                color=PALETTE.get(color, color), underline=underline)


def _col(c):
    return column_index_from_string(c) if isinstance(c, str) else c


def col_range(span):
    """('B','E') -> ['B','C','D','E']"""
    a, b = _col(span[0]), _col(span[1])
    return [get_column_letter(i) for i in range(a, b + 1)]


_FONT_FILES = {
    False: "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    True: "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
}
_FONT_CACHE = {}


def _measure(size, bold=False):
    """A function text -> width in points, using Liberation Sans (metric-compatible with Arial)
    when Pillow and the font are available, else an average-width estimate."""
    key = (size, bold)
    if key not in _FONT_CACHE:
        fn = None
        try:
            from PIL import ImageFont
            f = ImageFont.truetype(_FONT_FILES[bold], size)
            fn = f.getlength
        except Exception:
            fn = lambda t, s=size: len(t) * s * (0.52 if bold else 0.47)
        _FONT_CACHE[key] = fn
    return _FONT_CACHE[key]


def text_height(text, width_chars, size=10, bold=False, min_height=None):
    """Row height (points) for wrapped text in a column `width_chars` wide.

    Excel draws a column of width w about w*7+5 pixels wide (7 px is the digit width of
    the default Arial 10) and pads the text by a few pixels, so about 5.2*w points of
    text fit on a line. Words are wrapped greedily with real Arial-compatible metrics.
    Excel does not auto-fit rows written by openpyxl, so every wrapped row gets this height.
    """
    usable = max(20.0, width_chars * 5.2 - 2)
    measure = _measure(size, bold)
    lines = 0
    for para in str(text).split("\n"):
        n, cur = 1, ""
        for word in para.split(" "):
            trial = f"{cur} {word}" if cur else word
            if measure(trial) <= usable:
                cur = trial
            else:
                n += 1; cur = word
        lines += n
    h = lines * size * 1.28 + 4
    return max(h, min_height or 0)


def set_widths(ws, widths):
    """widths: {"A": 2, "B": 40, ...}"""
    for col, w in widths.items():
        ws.column_dimensions[col].width = w


def width_of(ws, col):
    return ws.column_dimensions[col].width or 8.43


def set_height(ws, row, height):
    ws.row_dimensions[row].height = height


def spacer(ws, row, height=None):
    set_height(ws, row, height or ROW["spacer"])
    return row + 1


def canvas(ws, last_row, last_col="Z", min_rows=60):
    """Paint the paper background over the area a buyer scrolls through."""
    rows = max(min_rows, last_row + 30)
    f = fill("canvas")
    for row in ws.iter_rows(min_row=1, max_row=rows, min_col=1, max_col=_col(last_col)):
        for c in row:
            if c.fill is None or c.fill.fill_type is None:
                c.fill = f


# ----------------------------------------------------------------------------
# Workbook
# ----------------------------------------------------------------------------
def new_workbook(product, version="1"):
    """A workbook with Arial 10 as the default font and ProofNotFluff file properties."""
    wb = Workbook()
    base = Font(name=FONT, size=10)
    wb._fonts = IndexedList([base])
    wb._named_styles["Normal"].font = base
    wb.remove(wb.active)
    p = wb.properties
    p.creator = "ProofNotFluff"
    p.lastModifiedBy = "ProofNotFluff"
    p.title = product
    p.subject = f"{product}, version {version}"
    p.description = "Copyright ProofNotFluff. Personal and single-business use. Information only, not professional advice."
    p.keywords = "ProofNotFluff"
    p.category = ""
    return wb


def define_name(wb, name, ws, cell):
    """Named range for a key input, e.g. TakeHome -> Calculator!$C$12 (works in Excel and Sheets)."""
    col = "".join(ch for ch in cell if ch.isalpha()); row = "".join(ch for ch in cell if ch.isdigit())
    ref = f"'{ws.title}'!${col}${row}"
    dn = DefinedName(name, attr_text=ref)
    wb.defined_names[name] = dn


# ----------------------------------------------------------------------------
# Blocks
# ----------------------------------------------------------------------------
def color_strip(ws, cell, size=9):
    """The five-bar brand motif as colored rich text in one cell."""
    parts = []
    for i, key in enumerate(STRIP):
        parts.append(TextBlock(InlineFont(rFont=FONT, sz=size, b=True, color=PALETTE[key]), "▬▬"))
        if i < len(STRIP) - 1:
            parts.append(TextBlock(InlineFont(rFont=FONT, sz=size), " "))
    ws[cell] = CellRichText(*parts)
    ws[cell].alignment = Alignment(vertical="center")


def title_block(ws, title, subtitle=None, span=("B", "E"), as_of=None, brand="ProofNotFluff", start_row=1):
    """Rows: spacer, title (brand at the right), color strip, subtitle (as-of date at the right).

    With three or more columns in the span the title and subtitle are merged across every
    column but the last, which holds the brand and the as-of date. With two columns the
    title sits in the first (make it wide). With one column the as-of date joins the subtitle.
    Returns the next free row (after one spacer)."""
    cols = col_range(span)
    first, last = cols[0], cols[-1]
    text_cols = cols[:-1] if len(cols) >= 2 else cols
    merge_to = text_cols[-1] if len(cols) >= 3 else None
    r = start_row
    set_height(ws, r, 6); r += 1
    c = ws[f"{first}{r}"]; c.value = title; c.font = font(SIZE["title"], bold=True)
    c.alignment = Alignment(vertical="center")
    if merge_to:
        ws.merge_cells(f"{first}{r}:{merge_to}{r}")
    if len(cols) >= 2:
        b = ws[f"{last}{r}"]; b.value = brand; b.font = font(SIZE["note"], bold=True, color="note")
        b.alignment = Alignment(horizontal="right", vertical="center")
    set_height(ws, r, ROW["title"]); r += 1
    color_strip(ws, f"{first}{r}"); set_height(ws, r, ROW["strip"]); r += 1
    if len(cols) == 1 and as_of:
        subtitle = f"{subtitle} {as_of}." if subtitle else as_of
        as_of = None
    if subtitle or as_of:
        if subtitle:
            s = ws[f"{first}{r}"]; s.value = subtitle; s.font = font(SIZE["note"], color="note")
            s.alignment = Alignment(vertical="center", wrap_text=True)
            if merge_to:
                ws.merge_cells(f"{first}{r}:{merge_to}{r}")
            width = sum(width_of(ws, k) for k in text_cols)
            set_height(ws, r, text_height(subtitle, width, SIZE["note"], min_height=ROW["subtitle"]))
        else:
            set_height(ws, r, ROW["subtitle"])
        if as_of:
            a = ws[f"{last}{r}"]; a.value = as_of; a.font = font(SIZE["note"], color="note")
            a.alignment = Alignment(horizontal="right", vertical="center")
        r += 1
    return spacer(ws, r)


def section_header(ws, row, text, span=("B", "E"), tone="ink"):
    """Bold ink heading with a medium rule under it across the span. Returns row + 1."""
    first, last = span
    c = ws[f"{first}{row}"]; c.value = text; c.font = font(SIZE["section"], bold=True, color=tone)
    c.alignment = Alignment(vertical="bottom")
    for col in col_range(span):
        cell = ws[f"{col}{row}"]
        cell.border = Border(bottom=_MED_INK)
    set_height(ws, row, ROW["section"])
    return row + 1


def label(ws, cell, text, bold=False, color="ink", size=None, indent=0):
    c = ws[cell]; c.value = text; c.font = font(size or SIZE["label"], bold=bold, color=color)
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=indent)
    return c


def note(ws, cell, text, size=None, color="note"):
    """Helper text (9 pt, muted). Sets the row height from the column width."""
    c = ws[cell]; c.value = text; c.font = font(size or SIZE["note"], color=color)
    c.alignment = Alignment(vertical="center", wrap_text=True)
    col = "".join(ch for ch in cell if ch.isalpha()); row = int("".join(ch for ch in cell if ch.isdigit()))
    h = text_height(text, width_of(ws, col), size or SIZE["note"], min_height=ROW["line"])
    if (ws.row_dimensions[row].height or 0) < h:
        set_height(ws, row, h)
    return c


def paragraph(ws, cell, text, span=None, size=None, bold=False, color="ink"):
    """Body text that wraps inside one cell (or a merged span of cells on the same row)."""
    c = ws[cell]; c.value = text; c.font = font(size or SIZE["label"], bold=bold, color=color)
    c.alignment = Alignment(vertical="top", wrap_text=True)
    col = "".join(ch for ch in cell if ch.isalpha()); row = int("".join(ch for ch in cell if ch.isdigit()))
    width = width_of(ws, col)
    if span:
        ws.merge_cells(f"{span[0]}{row}:{span[1]}{row}")
        width = sum(width_of(ws, k) for k in col_range(span))
    set_height(ws, row, text_height(text, width, size or SIZE["label"], min_height=ROW["line"]))
    return c


def add_validation(ws, cell, kind="decimal", lo=None, hi=None, prompt_title=None, prompt=None,
                   error=None, allow_blank=False, options=None):
    """Data validation plus an input message. kind: decimal | whole | list | date.
    For list, pass options=["A", "B"]. Google Sheets keeps the rule and the reject-on-error behaviour."""
    if kind == "list":
        dv = DataValidation(type="list", formula1='"' + ",".join(options) + '"', allow_blank=allow_blank)
    elif lo is not None and hi is not None:
        dv = DataValidation(type=kind, operator="between", formula1=str(lo), formula2=str(hi), allow_blank=allow_blank)
    elif lo is not None:
        dv = DataValidation(type=kind, operator="greaterThanOrEqual", formula1=str(lo), allow_blank=allow_blank)
    elif hi is not None:
        dv = DataValidation(type=kind, operator="lessThanOrEqual", formula1=str(hi), allow_blank=allow_blank)
    else:
        dv = DataValidation(type=kind, allow_blank=allow_blank)
    dv.showInputMessage = bool(prompt)
    dv.showErrorMessage = True
    if prompt:
        dv.promptTitle = (prompt_title or "Your number")[:32]
        dv.prompt = prompt[:255]
    dv.errorTitle = "Check this cell"
    dv.error = (error or _default_error(kind, lo, hi, options))[:255]
    dv.errorStyle = "stop"
    ws.add_data_validation(dv)
    dv.add(cell)
    return dv


def _default_error(kind, lo, hi, options):
    if kind == "list":
        return "Pick one of: " + ", ".join(options)
    if lo is not None and hi is not None:
        return f"Enter a number between {lo} and {hi}."
    if lo is not None:
        return f"Enter a number of {lo} or more."
    if hi is not None:
        return f"Enter a number of {hi} or less."
    return "Enter a number."


def input_cell(ws, cell, value, fmt, name=None, wb=None, validation=None, prompt_title=None,
               prompt=None, error=None, align="right", allow_blank=False):
    """Yellow cell, blue text, thin border, unlocked. validation=(kind, lo, hi) or (list, options)."""
    c = ws[cell]; c.value = value; c.number_format = fmt
    c.font = font(SIZE["value"], color="input_text"); c.fill = fill("input_fill")
    c.border = Border(left=_THIN_LINE, right=_THIN_LINE, top=_THIN_LINE, bottom=_THIN_LINE)
    c.alignment = Alignment(horizontal=align, vertical="center")
    c.protection = c.protection.copy(locked=False)
    if validation:
        if validation[0] == "list":
            add_validation(ws, cell, "list", options=validation[1], prompt_title=prompt_title, prompt=prompt, error=error,
                           allow_blank=allow_blank)
        else:
            kind, lo, hi = validation
            add_validation(ws, cell, kind, lo, hi, prompt_title=prompt_title, prompt=prompt, error=error,
                           allow_blank=allow_blank)
    if name and wb is not None:
        define_name(wb, name, ws, cell)
    return c


def output_cell(ws, cell, formula, fmt, bold=False, subtotal=False, align="right", color="ink"):
    """Calculated cell: soft fill, ink text, locked. subtotal=True adds a thin ink rule above and bold."""
    c = ws[cell]; c.value = formula; c.number_format = fmt
    c.font = font(SIZE["value"], bold=bold or subtotal, color=color); c.fill = fill("calc")
    c.alignment = Alignment(horizontal=align, vertical="center")
    if subtotal:
        c.border = Border(top=_THIN_INK)
    return c


def subtotal_label(ws, cell, text):
    """Label that pairs with output_cell(subtotal=True): bold with the same rule above."""
    c = label(ws, cell, text, bold=True)
    c.border = Border(top=_THIN_INK)
    return c


def key_cell(ws, cell, formula, fmt, tone="ink"):
    """A secondary answer: filled (ink, accent or teal) with bold white text."""
    c = ws[cell]; c.value = formula; c.number_format = fmt
    c.font = font(SIZE["key"], bold=True, color="white"); c.fill = fill(tone)
    c.alignment = Alignment(horizontal="right", vertical="center")
    return c


def result_card(ws, row, title, formula, fmt, span=("B", "E"), sub=None,
                side_title=None, side_formula=None, side_fmt=None):
    """The main answer: a three-row ink card across the span.
    Row 1 small white title (and side title at right), row 2 the big number (and side value),
    row 3 a one-line explanation. Returns the next free row (after one spacer)."""
    first, last = span
    cols = col_range(span)
    rows = (row, row + 1, row + 2)
    for r in rows:
        for col in cols:
            ws[f"{col}{r}"].fill = fill("ink")
    t = ws[f"{first}{rows[0]}"]; t.value = title; t.font = font(SIZE["small"], bold=True, color="on_ink_soft")
    t.alignment = Alignment(vertical="bottom", indent=1)
    v = ws[f"{first}{rows[1]}"]; v.value = formula; v.number_format = fmt
    v.font = font(SIZE["result"], bold=True, color="white"); v.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    if side_title:
        st = ws[f"{last}{rows[0]}"]; st.value = side_title; st.font = font(SIZE["small"], bold=True, color="on_ink_soft")
        st.alignment = Alignment(horizontal="right", vertical="bottom", indent=1)
    if side_formula is not None:
        sv = ws[f"{last}{rows[1]}"]; sv.value = side_formula; sv.number_format = side_fmt or fmt
        sv.font = font(SIZE["result_side"], bold=True, color="accent_soft")
        sv.alignment = Alignment(horizontal="right", vertical="center", indent=1)
    if sub:
        s = ws[f"{first}{rows[2]}"]; s.value = sub; s.font = font(SIZE["small"], color="on_ink_soft")
        s.alignment = Alignment(vertical="top", indent=1)
    set_height(ws, rows[0], ROW["card_top"]); set_height(ws, rows[1], ROW["card_mid"]); set_height(ws, rows[2], ROW["card_bottom"])
    return spacer(ws, rows[2] + 1)


def table_header(ws, row, cells, span=None):
    """Column headings for a small table: bold ink text, thin rule under. cells: {"B": "Share", "C": "Rate"}"""
    for col, text in cells.items():
        c = ws[f"{col}{row}"]; c.value = text; c.font = font(SIZE["label"], bold=True)
        c.alignment = Alignment(horizontal="right" if col != min(cells) else "left", vertical="center")
    for col in col_range(span) if span else cells:
        ws[f"{col}{row}"].border = Border(bottom=_THIN_INK)
    set_height(ws, row, max(ws.row_dimensions[row].height or 0, ROW["line"]))
    return row + 1


def negative_rule(ws, cell_range, good_tone="teal", bad_tone="accent"):
    """Conditional formatting: values below zero in accent, zero or more in teal (bold both)."""
    ws.conditional_formatting.add(cell_range, CellIsRule(operator="lessThan", formula=["0"], font=Font(name=FONT, bold=True, color=PALETTE[bad_tone])))
    ws.conditional_formatting.add(cell_range, CellIsRule(operator="greaterThanOrEqual", formula=["0"], font=Font(name=FONT, bold=True, color=PALETTE[good_tone])))


def page_break_before(ws, row):
    """Start a new printed page at `row` (Excel and LibreOffice honour it; Google Sheets ignores it).
    Use it so a section header is never the last line on a page."""
    from openpyxl.worksheet.pagebreak import Break
    ws.row_breaks.append(Break(id=row - 1))


def hyperlink(ws, cell, text, url, span=None):
    """A clickable link (works in Excel and Google Sheets). Shows `text`, opens `url`."""
    c = ws[cell]; c.value = text; c.hyperlink = url
    c.font = font(SIZE["label"], color="blue", underline="single")
    c.alignment = Alignment(vertical="center", wrap_text=True)
    col = "".join(ch for ch in cell if ch.isalpha()); row = int("".join(ch for ch in cell if ch.isdigit()))
    width = width_of(ws, col)
    if span:
        ws.merge_cells(f"{span[0]}{row}:{span[1]}{row}")
        width = sum(width_of(ws, k) for k in col_range(span))
    set_height(ws, row, text_height(text, width, SIZE["label"], min_height=ROW["line"]))
    return c


def warning(ws, cell, text):
    """A warning line: accent text, bold, 10 pt (use sparingly)."""
    c = ws[cell]; c.value = text; c.font = font(SIZE["label"], bold=True, color="accent")
    c.alignment = Alignment(vertical="center", wrap_text=True)
    return c


# ----------------------------------------------------------------------------
# Sheet finish: gridlines, freeze, zoom, print, protection, canvas
# ----------------------------------------------------------------------------
def finish_sheet(ws, product, last_row, span=("A", "F"), freeze=None, zoom=100, protect=True,
                 footer_notice="Estimates only. Not professional advice. See the Terms tab.",
                 canvas_cols="Z", tab_color=None):
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = zoom
    if freeze:
        ws.freeze_panes = freeze
    canvas(ws, last_row, canvas_cols)
    # print: Letter, portrait, one page wide, centred, product name in the header, notice in the footer
    ws.page_setup.orientation = "portrait"
    ws.page_setup.paperSize = ws.PAPERSIZE_LETTER
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.print_options.horizontalCentered = True
    ws.page_margins = PageMargins(left=0.5, right=0.5, top=0.7, bottom=0.7, header=0.3, footer=0.3)
    ws.print_area = f"{span[0]}1:{span[1]}{last_row}"
    ws.oddHeader.left.text = "ProofNotFluff"; ws.oddHeader.left.size = 8; ws.oddHeader.left.font = FONT
    ws.oddHeader.right.text = product; ws.oddHeader.right.size = 8; ws.oddHeader.right.font = FONT
    ws.oddFooter.left.text = footer_notice; ws.oddFooter.left.size = 8; ws.oddFooter.left.font = FONT
    ws.oddFooter.right.text = "Page &P of &N"; ws.oddFooter.right.size = 8; ws.oddFooter.right.font = FONT
    if tab_color:
        ws.sheet_properties.tabColor = PALETTE.get(tab_color, tab_color)
    if protect:
        # No password: a buyer can unprotect from the Review tab. Formatting stays allowed so they
        # can change the currency symbol; inserting or deleting rows is not, so formulas survive.
        ws.protection = SheetProtection(sheet=True, formatCells=False, formatColumns=False, formatRows=False,
                                        selectLockedCells=False, selectUnlockedCells=False, sort=True,
                                        autoFilter=True, insertRows=True, deleteRows=True,
                                        insertColumns=True, deleteColumns=True, objects=True, scenarios=True)


# ----------------------------------------------------------------------------
# Standard tabs
# ----------------------------------------------------------------------------
SHORT_NOTICE = ("For general information and planning only. This is not legal, tax, financial, medical or other "
                "professional advice, and using it doesn't create a professional relationship. Results are estimates "
                "based on the numbers you enter. Figures were checked on {date} and can change. See the Terms of Use "
                "page before you rely on anything here.")

# High tier tax clause (legal/README.md section 4): goes right after SHORT_NOTICE on Start Here and in the
# workbook's own notice whenever a product cites a tax rate, deadline or IRS/SSA rule.
TAX_TIER_CLAUSE = ("This summarizes federal rules as of {date} from {sources}. State and local rules can add to or change "
                   "them. It is not tax, legal or HR advice. Before you file, pay or decide, confirm with the agency or a "
                   "licensed CPA, enrolled agent or employment attorney.")


def start_here_tab(wb, product, tagline, what_it_does, steps, as_of, notice, sections=(),
                   legend_samples=(60000, 1152, 74.65), title="Start Here", position=0,
                   calculator_tab="Calculator"):
    """The first tab. steps: three strings. sections: [(heading, [paragraph | ("link", text, url), ...]), ...]
    placed after the legend. notice: the short notice text (word for word from legal/README.md).

    Columns: A gutter, B step numbers and legend swatches, C gap, D text, E brand and date, F gutter."""
    ws = wb.create_sheet(title, position)
    set_widths(ws, {"A": 2, "B": 10, "C": 2, "D": 56, "E": 24, "F": 2})
    SPAN = ("B", "E"); TEXT = ("D", "E")
    r = title_block(ws, product, tagline, span=SPAN, as_of=as_of)
    r = section_header(ws, r, "What it does", span=SPAN); r = spacer(ws, r, 6)
    paragraph(ws, f"B{r}", what_it_does, span=SPAN); r += 1
    r = spacer(ws, r)
    r = section_header(ws, r, "Three steps", span=SPAN); r = spacer(ws, r, 6)
    for i, text in enumerate(steps, 1):
        n = ws[f"B{r}"]; n.value = i; n.font = font(SIZE["step"], bold=True, color="accent")
        n.alignment = Alignment(horizontal="center", vertical="center")
        paragraph(ws, f"D{r}", text, span=TEXT)
        ws[f"D{r}"].alignment = Alignment(vertical="center", wrap_text=True)
        set_height(ws, r, max(ws.row_dimensions[r].height or 0, 26)); r += 1
        set_height(ws, r, 4); r += 1
    r = spacer(ws, r)
    r = section_header(ws, r, "How to read the cells", span=SPAN); r = spacer(ws, r, 6)
    inp, calc, key = legend_samples
    legend = [
        (lambda: input_cell(ws, f"B{r}", inp, FMT["usd0"]).protection.__class__ and setattr(ws[f"B{r}"], "protection", ws[f"B{r}"].protection.copy(locked=True)),
         "Yellow cells with blue numbers are yours to change. Type over the example."),
        (lambda: output_cell(ws, f"B{r}", calc, FMT["int"]),
         "Soft grey cells are formulas. They update on their own and are locked so stray typing can't break them."),
        (lambda: key_cell(ws, f"B{r}", key, FMT["usd2"], tone="ink"),
         f"Dark cells are your answers. The main one sits in the card at the top of the {calculator_tab} tab."),
    ]
    for make, text in legend:
        make()
        paragraph(ws, f"D{r}", text, span=TEXT)
        ws[f"D{r}"].alignment = Alignment(vertical="center", wrap_text=True)
        set_height(ws, r, max(ws.row_dimensions[r].height or 0, 22)); r += 1
        set_height(ws, r, 4); r += 1
    paragraph(ws, f"D{r}", "Each sheet is protected without a password, so a typo can't break a formula. To change anything else, "
                           "use Review, Unprotect Sheet in Excel, or Data, Protect sheets and ranges in Google Sheets.",
              span=TEXT, color="note", size=SIZE["note"]); r += 1
    r = spacer(ws, r)
    for heading, paras in sections:
        r = section_header(ws, r, heading, span=SPAN); r = spacer(ws, r, 6)
        for p in paras:
            if isinstance(p, tuple) and p[0] == "link":
                hyperlink(ws, f"B{r}", p[1], p[2], span=SPAN); r += 1
            else:
                paragraph(ws, f"B{r}", p, span=SPAN); r += 1
            set_height(ws, r, 4); r += 1
        r = spacer(ws, r)
    r = section_header(ws, r, "Before you rely on a number", span=SPAN); r = spacer(ws, r, 6)
    paragraph(ws, f"B{r}", notice, span=SPAN, color="note", size=SIZE["note"]); r += 1
    finish_sheet(ws, product, r, span=("A", "F"), tab_color="teal")
    return ws


def terms_tab(wb, product, sections, title="Terms"):
    """The last tab. sections: [(heading, [paragraph | ("link", text, url), ...]), ...].
    Paragraphs are written exactly as given (the legal desk keeps them word for word)."""
    ws = wb.create_sheet(title)
    set_widths(ws, {"A": 2, "B": 78, "C": 24, "D": 2})
    SPAN = ("B", "C")
    r = title_block(ws, "Terms of Use", f"{product}. Read this before you rely on a number.", span=SPAN)
    for heading, paras in sections:
        r = section_header(ws, r, heading, span=SPAN); r = spacer(ws, r, 6)
        for p in paras:
            if isinstance(p, tuple) and p[0] == "link":
                hyperlink(ws, f"B{r}", p[1], p[2], span=SPAN); r += 1
            else:
                paragraph(ws, f"B{r}", p, span=SPAN); r += 1
            set_height(ws, r, 4); r += 1
        r = spacer(ws, r)
    finish_sheet(ws, product, r, span=("A", "D"), tab_color="note")
    return ws


# ----------------------------------------------------------------------------
# Checks a builder can run before saving
# ----------------------------------------------------------------------------
def audit(wb):
    """Return a list of problems against the standard (empty list = pass)."""
    problems = []
    names = wb.sheetnames
    if names[0] != "Start Here":
        problems.append("first tab must be 'Start Here'")
    if names[-1] != "Terms":
        problems.append("last tab must be 'Terms'")
    for ws in wb.worksheets:
        if ws.sheet_view.showGridLines:
            problems.append(f"{ws.title}: gridlines on")
        if not ws.protection.sheet:
            problems.append(f"{ws.title}: sheet not protected")
        if ws.protection.password:
            problems.append(f"{ws.title}: protection has a password")
        if not ws.print_area:
            problems.append(f"{ws.title}: no print area")
        validated = set()
        for dv in ws.data_validations.dataValidation:
            for rng in str(dv.sqref).split():
                validated.add(rng)
        for row in ws.iter_rows():
            for c in row:
                if c.value is None:
                    continue
                if c.font and c.font.name and c.font.name != FONT:
                    problems.append(f"{ws.title}!{c.coordinate}: font {c.font.name}")
                if isinstance(c.value, str) and c.value.startswith("=") and not c.protection.locked:
                    problems.append(f"{ws.title}!{c.coordinate}: formula is unlocked")
                if not c.protection.locked and c.fill.fgColor.rgb[-6:] == PALETTE["input_fill"] and c.coordinate not in validated:
                    if ws.title != "Start Here":
                        problems.append(f"{ws.title}!{c.coordinate}: input without validation")
                if isinstance(c.value, str) and "—" in c.value:
                    problems.append(f"{ws.title}!{c.coordinate}: em dash")
    return problems


def today_text(d=None):
    d = d or date.today()
    return f"{d:%b} {d.day}, {d.year}"
