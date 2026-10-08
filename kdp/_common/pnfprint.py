"""Shared print helpers for ProofNotFluff KDP paperback packs.

Everything here is black and white (gray levels only), US Letter trim
(612 x 792 pt), no bleed, fonts embedded as TrueType subsets.

Used by kdp/<id>/build.py. Keep it free of product content.
"""
import os
import re

from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas

PT = 72.0
TRIM_W = 8.5 * PT
TRIM_H = 11.0 * PT

# KDP minimums are 0.375 in inside and 0.25 in outside for 24 to 150 pages.
# These are the book's actual margins; they sit well inside the minimums so
# the preflight (which checks the minimums) has room to spare.
M_INSIDE = 0.80 * PT
M_OUTSIDE = 0.60 * PT
M_TOP = 0.72 * PT
M_BOTTOM = 0.66 * PT
CONTENT_W = TRIM_W - M_INSIDE - M_OUTSIDE

FONT_DIRS = [
    "/usr/share/fonts/truetype/google-fonts",
    "/usr/share/fonts/truetype/crosextra",
    "/usr/share/fonts/truetype/liberation",
]

FONT_FILES = {
    "Head": ("Poppins-Bold.ttf", "LiberationSans-Bold.ttf"),
    "HeadMed": ("Poppins-Medium.ttf", "LiberationSans-Bold.ttf"),
    "HeadReg": ("Poppins-Regular.ttf", "LiberationSans-Regular.ttf"),
    "Body": ("Carlito-Regular.ttf", "LiberationSans-Regular.ttf"),
    "BodyB": ("Carlito-Bold.ttf", "LiberationSans-Bold.ttf"),
    "BodyI": ("Carlito-Italic.ttf", "LiberationSans-Italic.ttf"),
    "BodyBI": ("Carlito-BoldItalic.ttf", "LiberationSans-BoldItalic.ttf"),
}

_registered = {}


def _find(fname):
    for d in FONT_DIRS:
        p = os.path.join(d, fname)
        if os.path.exists(p):
            return p
    return None


def register_fonts():
    """Register the brand fonts (Poppins, Carlito) with Liberation fallbacks.

    Returns a dict logical-name -> registered font name, plus a 'note' key
    naming any fallback that was used.
    """
    if _registered:
        return _registered
    notes = []
    for logical, (preferred, fallback) in FONT_FILES.items():
        path = _find(preferred)
        if path is None:
            path = _find(fallback)
            notes.append(f"{logical}: {preferred} missing, used {fallback}")
        if path is None:
            raise RuntimeError(f"No font file for {logical}")
        pdfmetrics.registerFont(TTFont(logical, path))
        _registered[logical] = logical
    pdfmetrics.registerFontFamily("Body", normal="Body", bold="BodyB", italic="BodyI",
                                  boldItalic="BodyBI")
    pdfmetrics.registerFontFamily("Head", normal="HeadReg", bold="Head", italic="HeadReg",
                                  boldItalic="Head")
    _registered["note"] = "; ".join(notes) if notes else "Poppins and Carlito embedded"
    return _registered


def page_margins(page_no):
    """Return (left, right, top, bottom) x/y limits of the content box for a
    1-based page number. Odd pages are right-hand pages: gutter on the left."""
    if page_no % 2 == 1:
        left = M_INSIDE
        right = TRIM_W - M_OUTSIDE
    else:
        left = M_OUTSIDE
        right = TRIM_W - M_INSIDE
    return left, right, TRIM_H - M_TOP, M_BOTTOM


def outside_x(page_no):
    """x of the outside edge of the content box."""
    left, right, _, _ = page_margins(page_no)
    return right if page_no % 2 == 1 else left


def wrap(text, font, size, width):
    return simpleSplit(text, font, size, width)


def text_height(text, font, size, width, leading=None):
    leading = leading or size * 1.25
    return len(wrap(text, font, size, width)) * leading


def draw_wrapped(c, text, x, y, width, font, size, leading=None, gray=0.0,
                 align="left"):
    """Draw wrapped text with its first baseline at y. Returns the y of the
    next baseline after the block."""
    leading = leading or size * 1.25
    c.setFont(font, size)
    c.setFillGray(gray)
    for line in wrap(text, font, size, width):
        if align == "center":
            c.drawCentredString(x + width / 2, y, line)
        elif align == "right":
            c.drawRightString(x + width, y, line)
        else:
            c.drawString(x, y, line)
        y -= leading
    return y


def draw_label(c, text, x, y, font="HeadMed", size=6.3, gray=0.38, space=0.6):
    c.setFont(font, size)
    c.setFillGray(gray)
    c.drawString(x, y, text.upper(), charSpace=space)


def label_width(text, font="HeadMed", size=6.3, space=0.6):
    return pdfmetrics.stringWidth(text.upper(), font, size) + space * len(text)


def checkbox(c, x, y, size=8.5, gray=0.25, lw=0.7):
    c.setStrokeGray(gray)
    c.setLineWidth(lw)
    c.rect(x, y, size, size, stroke=1, fill=0)


def rule(c, x1, x2, y, gray=0.55, lw=0.55):
    c.setStrokeGray(gray)
    c.setLineWidth(lw)
    c.line(x1, y, x2, y)


def color_bars(c, x, y, w=14, h=3.2, gap=2.4, grays=(0.15, 0.32, 0.48, 0.62, 0.78)):
    """The five short brand bars, in gray steps for a black-and-white interior."""
    for i, g in enumerate(grays):
        c.setFillGray(g)
        c.rect(x + i * (w + gap), y, w, h, stroke=0, fill=1)


def _base_font():
    """Make the canvas start on an embedded font so no base-14 Helvetica
    resource is written into the file."""
    from reportlab import rl_config
    register_fonts()
    rl_config.canvas_basefontname = "Body"


def new_canvas(path, title, subject):
    _base_font()
    c = rl_canvas.Canvas(path, pagesize=(TRIM_W, TRIM_H), pageCompression=1, initialFontName="Body")
    c.setTitle(title)
    c.setAuthor("ProofNotFluff")
    c.setSubject(subject)
    c.setCreator("ProofNotFluff print build")
    c.setKeywords("")
    return c


class Overflow(Exception):
    pass


class Flow:
    """A top-down cursor for drawing one interior page on a canvas."""

    def __init__(self, c, page_no):
        self.c = c
        self.page_no = page_no
        self.L, self.R, self.top, self.bottom = page_margins(page_no)
        self.W = self.R - self.L
        self.y = self.top
        self.floor = self.bottom

    # geometry helpers
    def need(self, h, what=""):
        if self.y - h < self.floor - 0.01:
            raise Overflow(f"page {self.page_no}: {what} needs {h:.0f}pt, "
                           f"{self.y - self.floor:.0f}pt left")

    def gap(self, h):
        self.y -= h

    def remaining(self):
        return self.y - self.floor

    # text blocks
    def para(self, text, size=9.6, font="Body", gray=0.1, leading=None,
             after=4, width=None, x=None, align="left"):
        leading = leading or size * 1.26
        width = width or self.W
        x = self.L if x is None else x
        h = text_height(text, font, size, width, leading)
        self.need(h, "paragraph")
        self.y -= size
        self.y = draw_wrapped(self.c, text, x, self.y, width, font, size,
                              leading, gray, align)
        self.y += leading - after

    def bullets(self, items, size=9.6, font="Body", gray=0.1, leading=None,
                indent=12, after=5, bold_lead=False, marker="bullet"):
        """Bulleted (or numbered) paragraphs. marker: 'bullet' or 'number'."""
        leading = leading or size * 1.26
        for i, item in enumerate(items):
            lead, body = (item if isinstance(item, tuple) else (None, item))
            width = self.W - indent
            full = (lead + " " + body) if lead else body
            h = text_height(full, font, size, width, leading)
            self.need(h, "bullet")
            self.y -= size
            self.c.setFillGray(gray)
            if marker == "number":
                self.c.setFont("HeadMed", size - 0.5)
                self.c.drawString(self.L, self.y, f"{i + 1}.")
            else:
                self.c.setFont(font, size)
                self.c.drawString(self.L + 1, self.y, "•")
            if lead:
                # bold lead-in then body text on the same lines
                self.c.setFont("BodyB", size)
                self.c.drawString(self.L + indent, self.y, lead)
                lw = pdfmetrics.stringWidth(lead + " ", "BodyB", size)
                first_w = width - lw
                lines = wrap(body, font, size, first_w)
                if lines:
                    first_line = lines[0]
                    rest = body[len(first_line):].strip()
                    self.c.setFont(font, size)
                    self.c.drawString(self.L + indent + lw, self.y, first_line)
                    self.y -= leading
                    if rest:
                        self.y = draw_wrapped(self.c, rest, self.L + indent, self.y,
                                              width, font, size, leading, gray)
                    self.y += leading
            else:
                self.y = draw_wrapped(self.c, body, self.L + indent, self.y, width,
                                      font, size, leading, gray)
                self.y += leading
            self.y -= after
        self.y -= 2

    def subhead(self, text, size=12.5, after=5, before=6, gray=0.0):
        self.need(size + before + after, "subhead")
        self.y -= before + size
        self.c.setFont("Head", size)
        self.c.setFillGray(gray)
        self.c.drawString(self.L, self.y, text)
        self.y -= after

    def small_caps_head(self, text, size=7.2, after=5, before=4):
        self.need(size + before + after, "head")
        self.y -= before + size
        draw_label(self.c, text, self.L, self.y, size=size, gray=0.3, space=0.9)
        self.y -= after

    def title(self, kicker, title, intro=None, size=21, intro_size=10.2):
        """Section kicker, page title and intro paragraph."""
        self.y -= 8
        draw_label(self.c, kicker, self.L, self.y, size=6.8, gray=0.35, space=1.1)
        self.y -= 6 + size
        self.c.setFont("Head", size)
        self.c.setFillGray(0.0)
        self.c.drawString(self.L, self.y, title)
        self.y -= 7
        if intro:
            self.para(intro, size=intro_size, gray=0.22, after=3)
        self.y -= 9

    # form elements
    def fields(self, rows, h=31, gap=5, label_size=6.3, col_gap=12):
        """rows: list of rows; each row is a list of (label, weight) or
        label strings (weight 1). Draws a label and a writing rule."""
        for row in rows:
            self.need(h, "fields")
            cells = [(r, 1) if isinstance(r, str) else r for r in row]
            total = sum(w for _, w in cells)
            avail = self.W - col_gap * (len(cells) - 1)
            x = self.L
            for label, w in cells:
                cw = avail * w / total
                draw_label(self.c, label, x, self.y - label_size - 1, size=label_size)
                rule(self.c, x, x + cw, self.y - h + 3)
                x += cw + col_gap
            self.y -= h + gap
        self.y -= 2

    def option_row(self, label, options, h=30, extra=None, box=8.5,
                   opt_size=9.2, gap_after=5):
        """A label with checkbox options on one line; optional (label) writing
        field to the right taking the remaining width."""
        self.need(h, "options")
        draw_label(self.c, label, self.L, self.y - 7.3)
        x = self.L
        yb = self.y - h + 6
        for opt in options:
            checkbox(self.c, x, yb - 1, box)
            self.c.setFont("Body", opt_size)
            self.c.setFillGray(0.1)
            self.c.drawString(x + box + 4, yb, opt)
            x += box + 4 + pdfmetrics.stringWidth(opt, "Body", opt_size) + 15
        if extra:
            ex = x + 4
            draw_label(self.c, extra, ex, self.y - 7.3)
            rule(self.c, ex, self.R, self.y - h + 3)
        self.y -= h + gap_after

    def table(self, headers, weights, nrows=None, labels=None, fill=False,
              row_h=23, head_h=15, checks=(), label_size=8.9, reserve=0,
              min_rows=1, label_wrap=True):
        """Ruled table for handwriting. labels: list of first-column labels
        (sets nrows). fill: use remaining height down to floor minus reserve.
        checks: set of column indexes drawn as checkboxes."""
        if labels is not None:
            nrows = len(labels)
        avail = self.y - self.floor - reserve
        if fill:
            nrows = max(min_rows, int((avail - head_h) // row_h))
        h = head_h + nrows * row_h
        self.need(h, "table")
        total = sum(weights)
        xs = [self.L]
        for w in weights:
            xs.append(xs[-1] + self.W * w / total)
        c = self.c
        top = self.y
        # header
        c.setFillGray(0.9)
        c.rect(self.L, top - head_h, self.W, head_h, stroke=0, fill=1)
        for i, hdr in enumerate(headers):
            if hdr:
                draw_label(c, hdr, xs[i] + 4, top - head_h + 4.6, size=6.1, gray=0.2)
        # rows
        c.setStrokeGray(0.7)
        c.setLineWidth(0.45)
        y = top - head_h
        for r in range(nrows):
            if r % 2 == 1:
                c.setFillGray(0.965)
                c.rect(self.L, y - row_h, self.W, row_h, stroke=0, fill=1)
            c.setStrokeGray(0.7)
            c.line(self.L, y - row_h, self.R, y - row_h)
            if labels is not None and labels[r]:
                lines = wrap(labels[r], "Body", label_size, xs[1] - xs[0] - 8) \
                    if label_wrap else [labels[r]]
                lines = lines[:2]
                lh = label_size * 1.15
                ty = y - row_h / 2 + (len(lines) - 1) * lh / 2 - label_size * 0.35
                c.setFont("Body", label_size)
                c.setFillGray(0.08)
                for ln in lines:
                    c.drawString(xs[0] + 4, ty, ln)
                    ty -= lh
            for ci in checks:
                cx = (xs[ci] + xs[ci + 1]) / 2 - 4.25
                checkbox(c, cx, y - row_h / 2 - 4.25, 8.5)
            y -= row_h
        # column dividers
        c.setStrokeGray(0.72)
        c.setLineWidth(0.45)
        for x in xs[1:-1]:
            c.line(x, top - head_h, x, top - h)
        c.setStrokeGray(0.45)
        c.setLineWidth(0.6)
        c.line(self.L, top - head_h, self.R, top - head_h)
        c.line(self.L, top - h, self.R, top - h)
        self.y -= h + 7

    def lead_text(self, x, y, width, lead, body, size, leading, gray=0.1,
                  font="Body"):
        """Bold lead-in followed by body text, wrapped. y is the first
        baseline. Returns the number of lines used."""
        c = self.c
        c.setFillGray(gray)
        if not lead:
            lines = wrap(body, font, size, width)
            c.setFont(font, size)
            for ln in lines:
                c.drawString(x, y, ln)
                y -= leading
            return len(lines)
        c.setFont("BodyB", size)
        c.drawString(x, y, lead)
        lw = pdfmetrics.stringWidth(lead + " ", "BodyB", size)
        if not body:
            return 1
        first = wrap(body, font, size, max(width - lw, 30))
        c.setFont(font, size)
        c.drawString(x + lw, y, first[0])
        rest = body[len(first[0]):].strip()
        n = 1
        if rest:
            y -= leading
            lines = wrap(rest, font, size, width)
            for ln in lines:
                c.drawString(x, y, ln)
                y -= leading
            n += len(lines)
        return n

    def measure_lead(self, width, lead, body, size):
        if not lead:
            return len(wrap(body, "Body", size, width))
        lw = pdfmetrics.stringWidth(lead + " ", "BodyB", size)
        if not body:
            return 1
        first = wrap(body, "Body", size, max(width - lw, 30))
        rest = body[len(first[0]):].strip()
        return 1 + (len(wrap(rest, "Body", size, width)) if rest else 0)

    def checklist(self, items, cols=1, size=9.4, row_gap=4, box=8.5,
                  col_gap=14, gray=0.1, after=4):
        """Checkbox lines, in 1 or 2 columns. An item is a string or a
        (bold lead, body) tuple. Items may wrap."""
        leading = size * 1.22
        colw = (self.W - col_gap * (cols - 1)) / cols
        textw = colw - box - 6
        per_col = (len(items) + cols - 1) // cols
        y_start = self.y
        max_drop = 0
        for ci in range(cols):
            y = y_start
            x = self.L + ci * (colw + col_gap)
            for item in items[ci * per_col:(ci + 1) * per_col]:
                lead, body = item if isinstance(item, tuple) else (None, item)
                n = self.measure_lead(textw, lead, body, size)
                h = n * leading
                if y - h < self.floor:
                    raise Overflow(f"page {self.page_no}: checklist overflow")
                checkbox(self.c, x, y - size + 0.5, box)
                self.lead_text(x + box + 6, y - size + 1.5, textw, lead, body,
                               size, leading, gray)
                y -= h + row_gap
            max_drop = max(max_drop, y_start - y)
        self.y -= max_drop + after

    def lines(self, n=None, gap=21, fill=False, reserve=0, min_n=1, gray=0.6):
        """Horizontal writing rules."""
        if fill:
            n = max(min_n, int((self.y - self.floor - reserve) // gap))
        self.need(n * gap, "lines")
        for _ in range(n):
            self.y -= gap
            rule(self.c, self.L, self.R, self.y, gray=gray, lw=0.5)
        self.y -= 4

    def note(self, text, title="GOOD TO KNOW", size=9.0, pad=8, bar=True,
             fill=0.94, width=None, x=None, at_bottom=False):
        """Shaded note box. With at_bottom=True it is anchored to the floor
        and raises the floor for what is drawn above it."""
        width = width or self.W
        x = self.L if x is None else x
        leading = size * 1.25
        tw = width - 2 * pad - (4 if bar else 0)
        th = text_height(text, "Body", size, tw, leading)
        h = pad * 2 + (8 if title else 0) + th
        if at_bottom:
            top = self.floor + h
            self.floor = top + 10
            if self.y < self.floor:
                raise Overflow(f"page {self.page_no}: note at bottom overlaps")
        else:
            self.need(h, "note")
            top = self.y
            self.y -= h + 8
        c = self.c
        c.setFillGray(fill)
        c.rect(x, top - h, width, h, stroke=0, fill=1)
        if bar:
            c.setFillGray(0.2)
            c.rect(x, top - h, 2.2, h, stroke=0, fill=1)
        tx = x + pad + (4 if bar else 0)
        ty = top - pad - 5.5
        if title:
            draw_label(c, title, tx, ty, size=6.3, gray=0.25)
            ty -= 10
        else:
            ty -= 1
        ty = ty - size + 7
        draw_wrapped(c, text, tx, ty, tw, "Body", size, leading, 0.08)
        return h

    def two_col_notes(self, left, right, title_left, title_right, size=8.8):
        """Two side-by-side note boxes (used on the Start here page)."""
        gap = 10
        w = (self.W - gap) / 2
        leading = size * 1.25
        th = max(text_height(t, "Body", size, w - 20, leading) for t in (left, right))
        h = 16 + 12 + th
        self.need(h, "two notes")
        top = self.y
        for i, (ttl, txt) in enumerate(((title_left, left), (title_right, right))):
            x = self.L + i * (w + gap)
            self.c.setFillGray(0.94)
            self.c.rect(x, top - h, w, h, stroke=0, fill=1)
            self.c.setFillGray(0.2)
            self.c.rect(x, top - h, 2.2, h, stroke=0, fill=1)
            self.c.setFont("Head", 9.6)
            self.c.setFillGray(0.0)
            self.c.drawString(x + 12, top - 15, ttl)
            draw_wrapped(self.c, txt, x + 12, top - 28, w - 20, "Body", size, leading, 0.1)
        self.y -= h + 8


def running_head(c, page_no, section, book_title, updated_line=True,
                 show_page=True):
    """Footer: book title at the inside edge, page number at the outside edge,
    'Page updated' rule in the middle. Section kicker goes in the page title."""
    L, R, top, bottom = page_margins(page_no)
    y = bottom - 16
    c.setFont("HeadMed", 6.2)
    c.setFillGray(0.4)
    if page_no % 2 == 1:
        c.drawString(L, y, book_title.upper(), charSpace=0.9)
        if show_page:
            c.setFont("HeadMed", 8)
            c.drawRightString(R, y, str(page_no))
    else:
        c.drawRightString(R, y, book_title.upper(), charSpace=0.9)
        if show_page:
            c.setFont("HeadMed", 8)
            c.drawString(L, y, str(page_no))
    if updated_line:
        c.setFont("HeadMed", 6.2)
        c.setFillGray(0.4)
        mid = (L + R) / 2
        c.drawString(mid - 60, y, "PAGE UPDATED", charSpace=0.9)
        rule(c, mid - 2, mid + 62, y - 1.5, gray=0.6, lw=0.5)
    rule(c, L, R, bottom - 6, gray=0.8, lw=0.4)


# ---------------------------------------------------------------- cover ----

def spine_width_in(pages):
    return pages * 0.002252


def cover_geometry(pages):
    spine = spine_width_in(pages)
    total_w = 2 * 8.5 + spine + 0.25
    total_h = 11.25
    return spine * PT, total_w * PT, total_h * PT


def build_cover(path, pages, title_lines, subtitle, kicker, back_hook,
                bullets, byline, title_size=54, spine_text=None,
                back_intro=None, back_close=None, panel_title="INSIDE",
                panel_items=(), panel_cols=2):
    """Full-wrap cover: back, spine, front, with 0.125 in bleed on every side.
    Typography only, brand colors. Spine text only when the spine is at least
    0.25 in wide (KDP allows it from 79 pages)."""
    spine_pt, W, H = cover_geometry(pages)
    bleed = 0.125 * PT
    safe = 0.25 * PT  # keep text this far inside the trim
    paper = (0xF5 / 255, 0xF2 / 255, 0xEC / 255)
    ink = (0x1D / 255, 0x24 / 255, 0x33 / 255)
    accent = (0xC8 / 255, 0x50 / 255, 0x2F / 255)
    bars = [accent, (0x2E / 255, 0x6B / 255, 0x66 / 255), (0x6B / 255, 0x4F / 255, 0xA0 / 255),
            (0x2F / 255, 0x5F / 255, 0x9E / 255), (0x8A / 255, 0x6A / 255, 0x1F / 255)]
    _base_font()
    c = rl_canvas.Canvas(path, pagesize=(W, H), pageCompression=1, initialFontName="Body")
    c.setTitle(" ".join(title_lines) + " (cover)")
    c.setAuthor("ProofNotFluff")
    c.setCreator("ProofNotFluff print build")
    c.setFillColorRGB(*paper)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    back_x0 = bleed
    spine_x0 = bleed + 8.5 * PT
    front_x0 = spine_x0 + spine_pt
    c.setFillColorRGB(*ink)
    c.rect(spine_x0, 0, spine_pt, H, stroke=0, fill=1)
    if spine_text and spine_pt >= 0.25 * PT:
        c.saveState()
        c.translate(spine_x0 + spine_pt / 2 + 3, H / 2)
        c.rotate(-90)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Head", 11)
        c.drawCentredString(0, 0, spine_text)
        c.restoreState()

    def five_bars(x, y, bw=30, bh=8, bg=7):
        for i, col in enumerate(bars):
            c.setFillColorRGB(*col)
            c.rect(x + i * (bw + bg), y, bw, bh, stroke=0, fill=1)

    # ---- front
    margin = 0.8 * PT
    fx = front_x0 + margin
    fw = 8.5 * PT - 2 * margin
    y = H - bleed - 1.0 * PT
    five_bars(fx, y)
    y -= 36
    c.setFillColorRGB(*ink)
    c.setFont("HeadMed", 11.5)
    c.drawString(fx, y, kicker.upper(), charSpace=2.4)
    y -= 26 + title_size
    c.setFont("Head", title_size)
    for ln in title_lines:
        c.drawString(fx - 2, y, ln)
        y -= title_size * 1.06
    y += title_size * 0.3
    c.setFillColorRGB(*accent)
    c.rect(fx, y, 64, 5, stroke=0, fill=1)
    y -= 34
    c.setFillColorRGB(*ink)
    y = draw_wrapped(c, subtitle, fx, y, fw, "Body", 17.5, 23, 0)
    # ink panel with the section list; sized to its content
    panel_top = y - 22
    panel_bottom_min = bleed + 1.7 * PT
    if panel_items:
        items = list(panel_items)
        per = (len(items) + panel_cols - 1) // panel_cols
        colw = (fw - 60) / panel_cols
        size, lead_line, gap = 14.0, 17.0, 7.0
        while size >= 10:
            col_h = []
            for ci in range(panel_cols):
                h = 0
                for it in items[ci * per:(ci + 1) * per]:
                    h += len(wrap(it, "Body", size, colw - 30)) * lead_line + gap
                col_h.append(h)
            need = 78 + max(col_h) + 16
            if panel_top - need >= panel_bottom_min:
                break
            size -= 0.5
            lead_line = size * 1.22
            gap = 5.0
        panel_bottom = max(panel_bottom_min, panel_top - need)
        c.setFillColorRGB(*ink)
        c.rect(fx, panel_bottom, fw, panel_top - panel_bottom, stroke=0, fill=1)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("HeadMed", 9.5)
        c.drawString(fx + 30, panel_top - 34, panel_title.upper(), charSpace=2.2)
        five_bars(fx + 30, panel_top - 52, bw=18, bh=4, bg=4)
        for ci in range(panel_cols):
            yy = panel_top - 78
            for it in items[ci * per:(ci + 1) * per]:
                c.setFillColorRGB(*accent)
                c.rect(fx + 30 + ci * colw, yy + 3.5, 6, 6, stroke=0, fill=1)
                c.setFillColorRGB(1, 1, 1)
                c.setFont("Body", size)
                for ln in wrap(it, "Body", size, colw - 30):
                    c.drawString(fx + 30 + ci * colw + 14, yy, ln)
                    yy -= lead_line
                yy -= gap
    ay = bleed + 0.9 * PT
    c.setFillColorRGB(*ink)
    c.setFont("HeadMed", 10)
    c.drawString(fx, ay + 26, "WRITTEN BY A FINANCE EXECUTIVE", charSpace=1.8)
    c.setFont("Head", 22)
    c.drawString(fx, ay - 2, "ProofNotFluff")
    c.setFillColorRGB(*accent)
    c.rect(fx, ay - 13, 40, 3.5, stroke=0, fill=1)

    # ---- back
    bx = back_x0 + margin
    bw_ = 8.5 * PT - 2 * margin
    y = H - bleed - 1.0 * PT
    five_bars(bx, y)
    y -= 52
    c.setFillColorRGB(*ink)
    y = draw_wrapped(c, back_hook, bx, y, bw_, "Head", 30, 37, 0)
    y -= 8
    c.setFillColorRGB(*accent)
    c.rect(bx, y + 18, 64, 5, stroke=0, fill=1)
    y -= 14
    if back_intro:
        c.setFillColorRGB(*ink)
        y = draw_wrapped(c, back_intro, bx, y, bw_, "Body", 16, 21.5, 0)
        y -= 12
    for b in bullets:
        c.setFillColorRGB(*accent)
        c.rect(bx, y + 3.5, 8, 8, stroke=0, fill=1)
        c.setFillColorRGB(*ink)
        y = draw_wrapped(c, b, bx + 20, y, bw_ - 20, "Body", 16, 21.5, 0)
        y -= 10
    if back_close:
        y -= 8
        c.setFillColorRGB(*ink)
        y = draw_wrapped(c, back_close, bx, y, bw_, "BodyI", 14, 19, 0.0)
    by = bleed + 0.9 * PT
    c.setFillColorRGB(*ink)
    c.setFont("HeadMed", 10)
    c.drawString(bx, by + 40, byline.upper(), charSpace=1.8)
    c.setFont("Head", 18)
    c.drawString(bx, by + 16, "ProofNotFluff")
    c.setFillColorRGB(*accent)
    c.rect(bx, by + 5, 40, 3.5, stroke=0, fill=1)
    # barcode zone: 2 x 1.2 in, bottom right of the back cover, left blank
    bz_w, bz_h = 2.0 * PT, 1.2 * PT
    bz_x = back_x0 + 8.5 * PT - safe - bz_w
    bz_y = bleed + safe
    c.setFillColorRGB(1, 1, 1)
    c.rect(bz_x, bz_y, bz_w, bz_h, stroke=0, fill=1)
    c.showPage()
    c.save()
    return {"spine_in": round(spine_width_in(pages), 4), "width_in": round(W / PT, 4),
            "height_in": round(H / PT, 4), "spine_text": bool(spine_text and spine_pt >= 0.25 * PT),
            "barcode_zone_in": {"x_from_back_trim_left": round((bz_x - back_x0) / PT, 3),
                                "y_from_trim_bottom": round((bz_y - bleed) / PT, 3),
                                "w": 2.0, "h": 1.2}}


# ---------------------------------------------------------------- copy QA --

EM_DASH = "—"
BANNED = ["honestly", "genuinely", "straightforward", "delve", "unlock", "elevate",
          "seamless", "game-changer", "effortless", "supercharge"]


def copy_problems(text):
    """Return a list of copy-rule hits in a string."""
    hits = []
    if EM_DASH in text:
        hits.append("em dash")
    low = text.lower()
    for w in BANNED:
        if re.search(r"\b" + re.escape(w) + r"\w*", low):
            hits.append(w)
    return hits


def strip_unused_fonts(path):
    """Remove font resources no page uses (ReportLab's platypus canvas lists
    the base-14 Helvetica even when nothing is set in it). Font dictionaries
    can be shared between pages, so usage is pooled over the whole document.
    Rewrites the file in place; returns the base font names removed."""
    import pikepdf
    removed = set()
    with pikepdf.open(path, allow_overwriting_input=True) as pdf:
        used = set()
        for page in pdf.pages:
            contents = page.Contents
            if isinstance(contents, pikepdf.Array):
                data = b"".join(x.read_bytes() for x in contents)
            else:
                data = contents.read_bytes()
            used |= set(m.group(1).decode() for m in
                        re.finditer(rb"/([A-Za-z0-9+.\-]+)\s+[\d.]+\s+Tf", data))
        for page in pdf.pages:
            res = page.get("/Resources")
            if res is None or "/Font" not in res:
                continue
            for key in list(res.Font.keys()):
                if key.lstrip("/") not in used:
                    removed.add(str(res.Font[key].get("/BaseFont")))
                    del res.Font[key]
        pdf.save(path)
    return sorted(removed)
