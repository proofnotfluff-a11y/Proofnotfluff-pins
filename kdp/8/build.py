#!/usr/bin/env python3
"""Build the KDP paperback print pack for #8, First-Time Employer Payroll and
Benefits Setup Guide.

Source of truth: the legally cleared v2 digital guide (legal/reviews/
8-2026-10-06.md), 23 pages US Letter. This print edition re-sets it with
platypus: no form fields (ruled cells and drawn checkboxes instead), black and
white, fonts embedded, 8.5 x 11 in trim, no bleed. Added for print: a second
copy of Worksheet 3 (one per state), a notes page and the review page, so the
book runs 26 pages.

Outputs (same folder): interior.pdf, cover.pdf.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_common"))

import pnfprint as P  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_LEFT  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, KeepTogether,  # noqa: E402
                                NextPageTemplate, PageBreak, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle)

AS_OF = "October 6, 2026"
VERSION_LINE = "Paperback edition 2, October 2026"
BOOK = "First-Time Employer Guide"
PAGES_EXPECTED = int(os.environ.get("PAGES_EXPECTED", "0")) or None

SHORT_NOTICE = ("For general information and planning only. This is not legal, tax, financial, "
                "medical or other professional advice, and using it doesn't create a professional "
                "relationship. Results are estimates based on the numbers you enter. Figures were "
                "checked on " + AS_OF + " and can change. See the Terms of Use page before you rely "
                "on anything here.")
TIER_CLAUSE = ("This summarizes federal rules as of " + AS_OF + " from IRS Publication 15, IRS Tax "
               "Topics 751 and 759, IRS Employment Tax Due Dates, the SSA Contribution and Benefit "
               "Base page, IRS Rev. Proc. 2025-32, 8 CFR 274a.2 (Form I-9) and the HHS Office of "
               "Child Support Services new-hire page. State and local rules can add to or change "
               "them. It is not tax, legal or HR advice. Before you file, pay or decide, confirm "
               "with the agency or a licensed CPA, enrolled agent or employment attorney.")

# symmetric margins for a flowing text book (both sides clear the KDP gutter minimum)
SIDE = 0.8 * P.PT
TOP = 0.75 * P.PT
BOTTOM = 0.7 * P.PT
CW = P.TRIM_W - 2 * SIDE

G = {k: colors.Color(v, v, v) for k, v in {"ink": 0.0, "dark": 0.15, "mid": 0.4, "rule": 0.7,
                                             "light": 0.9, "pale": 0.95, "white": 1.0}.items()}

ST = {}


def styles():
    # every platypus table cell starts on an embedded font, never Helvetica
    from reportlab.platypus.tables import CellStyle
    CellStyle.fontname = "Body"
    ST["kicker"] = ParagraphStyle("kicker", fontName="HeadMed", fontSize=6.8, leading=9,
                                  textColor=G["mid"], spaceAfter=4)
    ST["h1"] = ParagraphStyle("h1", fontName="Head", fontSize=20, leading=24, textColor=G["ink"],
                              spaceAfter=6)
    ST["h2"] = ParagraphStyle("h2", fontName="Head", fontSize=12.5, leading=15, textColor=G["ink"],
                              spaceBefore=9, spaceAfter=4)
    ST["h3"] = ParagraphStyle("h3", fontName="Head", fontSize=10.5, leading=13, textColor=G["ink"],
                              spaceBefore=6, spaceAfter=2)
    ST["intro"] = ParagraphStyle("intro", fontName="Body", fontSize=10.6, leading=13.6,
                                 textColor=G["dark"], spaceAfter=7)
    ST["body"] = ParagraphStyle("body", fontName="Body", fontSize=9.9, leading=12.6,
                                textColor=G["ink"], spaceAfter=5)
    ST["small"] = ParagraphStyle("small", fontName="Body", fontSize=8.8, leading=11,
                                 textColor=G["dark"], spaceAfter=4)
    ST["bullet"] = ParagraphStyle("bullet", parent=ST["body"], leftIndent=12, bulletIndent=1,
                                  spaceAfter=3, bulletFontName="Body")
    ST["cell"] = ParagraphStyle("cell", fontName="Body", fontSize=8.8, leading=10.8, textColor=G["ink"])
    ST["cellb"] = ParagraphStyle("cellb", parent=ST["cell"], fontName="BodyB")
    ST["cellhead"] = ParagraphStyle("cellhead", fontName="HeadMed", fontSize=6.4, leading=8,
                                    textColor=G["dark"])
    ST["note"] = ParagraphStyle("note", fontName="Body", fontSize=9.2, leading=11.6, textColor=G["ink"])
    ST["notetitle"] = ParagraphStyle("notetitle", fontName="HeadMed", fontSize=6.6, leading=9,
                                     textColor=G["dark"], spaceAfter=2)
    ST["label"] = ParagraphStyle("label", fontName="HeadMed", fontSize=6.4, leading=8.5,
                                 textColor=G["mid"])
    ST["check"] = ParagraphStyle("check", fontName="Body", fontSize=9.6, leading=12, textColor=G["ink"])
    ST["step"] = ParagraphStyle("step", fontName="HeadMed", fontSize=6.6, leading=9, textColor=G["mid"])
    ST["done"] = ParagraphStyle("done", parent=ST["body"], fontName="BodyB", fontSize=9.2, leading=11.6)
    for st in ST.values():
        st.bulletFontName = "Body"


# ------------------------------------------------------------- flowables --

class CheckBox(Flowable):
    def __init__(self, size=8.5):
        Flowable.__init__(self)
        self.size = size
        self.width = size
        self.height = size

    def draw(self):
        P.checkbox(self.canv, 0, 0, self.size)


class Rule(Flowable):
    def __init__(self, width, gray=0.6, lw=0.5, space=0):
        Flowable.__init__(self)
        self.width = width
        self.height = space + 1
        self.gray, self.lw = gray, lw

    def draw(self):
        P.rule(self.canv, 0, self.width, 0.5, gray=self.gray, lw=self.lw)


class Lines(Flowable):
    """n horizontal writing rules, gap pt apart."""

    def __init__(self, width, n, gap=21):
        Flowable.__init__(self)
        self.width = width
        self.n, self.gap = n, gap
        self.height = n * gap

    def draw(self):
        for i in range(self.n):
            P.rule(self.canv, 0, self.width, self.height - (i + 1) * self.gap, gray=0.6, lw=0.5)


def para(text, style="body"):
    return Paragraph(text, ST[style])


def kicker(text):
    return Paragraph(text.upper(), ST["kicker"])


def h1(text):
    return Paragraph(text, ST["h1"])


def h2(text):
    return Paragraph(text, ST["h2"])


def h3(text):
    return Paragraph(text, ST["h3"])


def bullets(items, style="bullet"):
    return [Paragraph(t, ST[style], bulletText="•") for t in items]


def note(text, title=None, width=CW, size=None):
    st = ST["note"] if size is None else ParagraphStyle("n2", parent=ST["note"], fontSize=size,
                                                        leading=size * 1.26)
    cells = []
    if title:
        cells.append([Paragraph(title.upper(), ST["notetitle"])])
    for chunk in text.split("\n"):
        cells.append([Paragraph(chunk, st)])
    t = Table(cells, colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), G["pale"]),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, G["dark"]),
        ("LEFTPADDING", (0, 0), (-1, -1), 11), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, 0), 7), ("BOTTOMPADDING", (0, -1), (-1, -1), 7),
        ("TOPPADDING", (0, 1), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -2), 1),
    ]))
    return t


def grid(headers, rows, widths, head=True, row_pad=3.5, zebra=True, bold_first=False,
         min_row_h=None):
    """Text table with a gray header row. rows: list of lists of strings or
    flowables."""
    data = []
    if head:
        data.append([Paragraph(h.upper(), ST["cellhead"]) for h in headers])
    for r in rows:
        row = []
        for i, cell in enumerate(r):
            if isinstance(cell, str):
                row.append(Paragraph(cell, ST["cellb"] if (bold_first and i == 0) else ST["cell"]))
            else:
                row.append(cell)
        data.append(row)
    rh = None
    if min_row_h:
        rh = [None] * (1 if head else 0) + [min_row_h] * len(rows)
    t = Table(data, colWidths=widths, rowHeights=rh, repeatRows=1 if head else 0)
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "Body"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), row_pad), ("BOTTOMPADDING", (0, 0), (-1, -1), row_pad),
        ("LINEBELOW", (0, 0), (-1, -1), 0.45, G["rule"]),
        ("LINEAFTER", (0, 0), (-2, -1), 0.45, G["rule"]),
    ]
    if head:
        style += [("BACKGROUND", (0, 0), (-1, 0), G["light"]),
                  ("LINEBELOW", (0, 0), (-1, 0), 0.6, G["mid"]),
                  ("VALIGN", (0, 0), (-1, 0), "MIDDLE")]
    if zebra:
        for i in range(1 if head else 0, len(data)):
            if (i - (1 if head else 0)) % 2 == 1:
                style.append(("BACKGROUND", (0, i), (-1, i), colors.Color(0.965, 0.965, 0.965)))
    style.append(("LINEBELOW", (0, -1), (-1, -1), 0.6, G["mid"]))
    t.setStyle(TableStyle(style))
    return t


def worksheet_rows(labels, label_w=None, row_h=30, widths=None):
    """Label on the left, ruled writing cell on the right."""
    label_w = label_w or CW * 0.42
    data = [[Paragraph(lb, ST["cell"]), ""] for lb in labels]
    t = Table(data, colWidths=[label_w, CW - label_w], rowHeights=[row_h] * len(labels))
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Body"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -1), 0.45, G["rule"]),
        ("LINEAFTER", (0, 0), (0, -1), 0.45, G["rule"]),
        ("BACKGROUND", (0, 0), (0, -1), colors.Color(0.965, 0.965, 0.965)),
        ("LINEABOVE", (0, 0), (-1, 0), 0.6, G["mid"]),
        ("LINEBELOW", (0, -1), (-1, -1), 0.6, G["mid"]),
    ]))
    return t


def checklist(items, size=9.6, box=8.5, gap=4):
    st = ParagraphStyle("ck", parent=ST["check"], fontSize=size, leading=size * 1.25)
    data = [[CheckBox(box), Paragraph(t, st)] for t in items]
    t = Table(data, colWidths=[box + 8, CW - box - 8])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), gap / 2 + 1), ("BOTTOMPADDING", (0, 0), (-1, -1), gap / 2),
        ("TOPPADDING", (0, 0), (0, -1), gap / 2 + 2),
    ]))
    return t


def yesno_rows(questions):
    """Numbered questions with yes / no checkboxes."""
    data = []
    for q in questions:
        data.append([Paragraph(q, ST["check"]), CheckBox(), Paragraph("yes", ST["cell"]),
                     CheckBox(), Paragraph("no", ST["cell"])])
    t = Table(data, colWidths=[CW - 96, 14, 30, 14, 30])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -1), 0.45, G["rule"]),
    ]))
    return t


def step_head(when, num, title, sub):
    t = Table([[Paragraph(when.upper(), ST["step"]),
                Paragraph(f'<font name="Head" size="13">{num}&nbsp;&nbsp;{title}</font><br/>'
                          f'<font name="Body" size="9.4" color="#555555">{sub}</font>',
                          ParagraphStyle("sh", fontName="Head", fontSize=13, leading=14.5))]],
              colWidths=[82, CW - 82])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                           ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                           ("TOPPADDING", (0, 0), (0, 0), 11)]))
    return t


def done_line(text):
    return note("<b>You're done with this step when:</b> " + text, size=9.2)


def example_box(rows, title="EXAMPLE, filled in for Blue Door Cleaning Co. (fictional)", widths=None,
                after=None):
    widths = widths or [CW * 0.34 - 20, CW * 0.66 - 4]
    data = [[Paragraph(title.upper(), ST["notetitle"]), ""]]
    for a, b in rows:
        data.append([Paragraph(a, ST["cellb"]), Paragraph(b, ST["cell"])])
    if after:
        data.append([Paragraph(after, ST["cell"]), ""])
    t = Table(data, colWidths=widths)
    st = [
        ("FONTNAME", (0, 0), (-1, -1), "Body"),
        ("SPAN", (0, 0), (-1, 0)), ("BACKGROUND", (0, 0), (-1, -1), G["pale"]),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, G["dark"]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 11), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, 0), 7), ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
        ("LINEBELOW", (0, 1), (-1, -2 if after else -1), 0.4, colors.Color(0.8, 0.8, 0.8)),
    ]
    if after:
        st.append(("SPAN", (0, -1), (-1, -1)))
        st.append(("TOPPADDING", (0, -1), (-1, -1), 8))
    t.setStyle(TableStyle(st))
    return t


# ------------------------------------------------------------------ pages --

def title_page(c, doc):
    """Page 1, drawn straight on the canvas."""
    L, R = SIDE, P.TRIM_W - SIDE
    W = R - L
    y = P.TRIM_H - TOP - 20
    P.color_bars(c, L, y, w=20, h=4.5, gap=4)
    y -= 26
    P.draw_label(c, "A PROOFNOTFLUFF OPERATOR'S GUIDE", L, y, size=7.5, gray=0.3, space=1.6)
    y -= 56
    c.setFont("Head", 30)
    c.setFillGray(0)
    for ln in ("First-Time Employer", "Payroll and Benefits", "Setup Guide"):
        c.drawString(L, y, ln)
        y -= 36
    y -= 2
    c.setFillGray(0.15)
    c.rect(L, y, 44, 3.2, stroke=0, fill=1)
    y -= 30
    y = P.draw_wrapped(c, "From \"I want to hire\" to a first legal paycheck in 30 days. Every step "
                          "in order, nothing assumed.", L, y, W, "BodyI", 15, 19.5, 0.15)
    y -= 14
    c.setFillGray(0.15)
    c.roundRect(L, y - 8, 236, 20, 3, stroke=0, fill=1)
    c.setFillGray(1)
    c.setFont("HeadMed", 8.5)
    c.drawString(L + 10, y - 2, "Written by someone who set it up from zero")
    y -= 40
    items = [
        "The 30-day sequence: EIN, state accounts, workers' comp, provider, paperwork, first payroll",
        "W-2 vs 1099 decision checklist, with the misclassification risk in plain words",
        "Payroll-provider comparison, September 2026 pricing, a \"pick this if\" line for each",
        "State registration checklist and the out-of-state warning",
        "ICHRA and QSEHRA explained, with a cost worksheet",
        "Every pay-stub line defined, the true hourly cost of an employee, the filing calendar",
        "Five first-timer mistakes, what they cost, the one fix for each",
    ]
    for it in items:
        c.setFillGray(0.2)
        c.rect(L, y + 2.5, 5, 5, stroke=0, fill=1)
        y = P.draw_wrapped(c, it, L + 13, y, W - 13, "Body", 10.6, 13.5, 0.1)
        y -= 4
    y -= 8
    y = P.draw_wrapped(c, "Four worksheets, each with a worked example for a fictional 3-person "
                          "business, then blank, written in by hand.", L, y, W, "BodyB", 10, 13, 0.15)
    # legal block at the bottom
    f = P.Flow(c, 1)
    f.L, f.R, f.W = L, R, W
    f.floor = BOTTOM
    f.y = y
    f.note(SHORT_NOTICE + "\n" + TIER_CLAUSE, title="BEFORE YOU RELY ON THIS BOOK", size=8.0,
           at_bottom=True)
    c.setFont("HeadMed", 6.2)
    c.setFillGray(0.4)
    c.drawString(L, BOTTOM - 16, "PROOFNOTFLUFF", charSpace=0.9)
    c.drawRightString(R, BOTTOM - 16, VERSION_LINE.upper(), charSpace=0.6)


def body_footer(c, doc):
    n = doc.page
    L, R = SIDE, P.TRIM_W - SIDE
    y = BOTTOM - 16
    c.setFont("HeadMed", 6.2)
    c.setFillGray(0.4)
    if n % 2 == 1:
        c.drawString(L, y, BOOK.upper() + "  |  PROOFNOTFLUFF", charSpace=0.9)
        c.setFont("HeadMed", 8)
        c.drawRightString(R, y, str(n))
    else:
        c.drawRightString(R, y, BOOK.upper() + "  |  PROOFNOTFLUFF", charSpace=0.9)
        c.setFont("HeadMed", 8)
        c.drawString(L, y, str(n))
    P.rule(c, L, R, BOTTOM - 6, gray=0.8, lw=0.4)


def story():
    s = []
    PB = PageBreak

    def step(when, num, title, sub, intro, items, done):
        return [KeepTogether([step_head(when, num, title, sub), para(intro)] + bullets(items)
                             + [done_line(done)])]

    # p2 how to use this book
    s += [kicker("Start here"), h1("How to use this book"),
          para("Read this page first. It sets the terms for everything after it.", "intro"),
          para("I ran finance and HR from zero at a fast-growing e-commerce company: I set up payroll "
               "and benefits for the first employees myself and kept running them as the team grew. "
               "This guide is that sequence written down for the owner who is about to hire employee "
               "number one, knows nothing about employer payroll, and is afraid of the IRS. The fear is "
               "reasonable. The fix is a sequence, not a lawyer."),
          h2("What this guide is not")]
    s += bullets([
        "<b>Not legal or tax advice.</b> It's an operator's guide: what I did, in what order, and what I'd tell a friend. Your state and your situation may differ. Confirm with a CPA or attorney before you file anything.",
        "<b>Not 50-state legal text.</b> Section 4 gives you the method to look up your own state's rules and a checklist to fill in. It does not contain state-by-state filing instructions, because those change and because a wrong one is worse than none.",
        "<b>Not ongoing HR.</b> No handbooks, performance reviews, firing or employee relations. This guide ends at your first payroll run and the filing calendar that follows it.",
        "<b>Not a compliance guarantee.</b> Doing everything here reduces your risk a lot. It does not make penalties impossible. Nobody can promise that, and anyone who does is selling something.",
        "<b>Not payroll software.</b> It helps you choose software (Section 3). It is not software.",
    ])
    s += [Spacer(1, 4), note(SHORT_NOTICE + "\n" + TIER_CLAUSE, title="Read this first", size=8.6),
          h2("How to use it")]
    s += bullets([
        "Read Section 1 once, start to finish, before you do anything. Twenty minutes. It's the map.",
        "Then work the steps in order. Each one ends with a checkpoint: \"You're done with this step when...\" Don't move on until you can say yes.",
        "Fill in the four worksheets as you reach them. Each has a worked example first so you can see what a finished one looks like. Write in the book, or copy the page first if you want a clean one. The fillable digital version is at the ProofNotFluff shop on Etsy.",
        "Keep Section 6 open the day you run your first payroll. Keep the filing calendar on the wall after that.",
        "Read Section 7 last, or first if you want to know what this guide is protecting you from.",
    ])
    s += [h2("The fictional business in every example"),
          para("Every worksheet in this guide is filled in first for a fictional business, then given to you "
               "blank. The business is Blue Door Cleaning Co., a residential cleaning company in Ohio owned "
               "by Sam Okafor, who has run it solo for two years and is hiring three people: Maria (cleaner, "
               "$20 an hour, about 30 hours a week), Devon (cleaner, $18 an hour, about 25 hours a week) and "
               "Priya (scheduler and office help, $22 an hour, about 15 hours a week). Same three people, "
               "same wages, same state, in all four worksheets, so the examples agree with each other. Blue "
               "Door, Sam and the three employees are invented for this guide."),
          PB()]

    # p3 section 1
    s += [kicker("Section 1"), h1("The 30-day sequence"),
          para("Being an employer is a set of registrations and a rhythm. The registrations happen once, in "
               "this order, because each one needs the one before it. The rhythm is payroll, deposits and "
               "filings, and a payroll provider does most of it. Here is the whole sequence. Nothing is "
               "assumed; if you already have a step, skip it.", "intro")]
    s += step("Days 1 to 2", 1, "Get your EIN", "Employer Identification Number",
              "An EIN is a nine-digit number the IRS uses to identify your business, the way a Social "
              "Security number identifies you. You need one to pay employees, file payroll returns and open "
              "a business bank account. If you formed an LLC or corporation you may already have one; check "
              "your formation paperwork or any prior tax filing. If you've been a sole proprietor with no "
              "employees, you probably don't.",
              [
        "It's free. Apply at irs.gov (search \"apply for an EIN online\"). The online application takes about 15 minutes and gives you the number immediately (the tool has posted hours, roughly 6 a.m. to 1 a.m. Eastern on weekdays). Your payroll provider will use the EIN for electronic filings and deposits, and some IRS and state systems can take days to recognize a new number, so get it first.",
        "Never pay a third-party site to \"get your EIN.\" They charge for a free form.",
        "Write the number down somewhere you'll find it. Every form from here on asks for it.",
              ],
              "You have a nine-digit EIN from the IRS, on paper or in a saved PDF.")
    s += step("Days 2 to 7", 2, "Register as an employer in your state", "State tax ID and unemployment account",
              "The EIN is federal. Your state has its own two registrations: a withholding account (so you "
               "can send the state the income tax you withhold from paychecks) and an unemployment insurance "
               "account (so you can pay state unemployment tax, usually called SUTA or SUI). Some states "
               "combine them in one application; most don't. Some cities and counties have a local tax too.",
              [
        "Section 4 has the lookup method and a checklist. Start with your state's Department of Revenue (withholding) and its workforce or labor department (unemployment).",
        "Do this in every state where an employee will physically work, not just the state where your business is. A remote employee in another state means registering there too.",
        "Registration is usually free and usually online. It can take days to weeks for account numbers to arrive. That's why it's early in the sequence.",
              ],
              "You have a state withholding account number and a state unemployment account number "
                    "(and any local ones), for every state where someone will work.")

    # p4 steps 3-5
    s += step("Days 5 to 10", 3, "Get workers' compensation insurance", "Required in almost every state once you have an employee",
              "Workers' comp pays medical bills and lost wages if an employee is hurt on the job, and in "
               "exchange the employee generally can't sue you for the injury. Most states require it from the "
               "first employee; Texas is the well-known exception where it's optional, and about a dozen "
               "states set a minimum headcount, usually three to five, before it's required. Look yours up "
               "either way; the injury doesn't wait for the threshold. Some states run their own fund you "
               "must buy from (Ohio, for example); most let you buy from private insurers.",
              [
        "Get two quotes: one from your state's fund or an insurer directly, and one through your payroll provider, most of which sell pay-as-you-go workers' comp that's billed from each payroll run instead of an annual estimate.",
        "The price depends on what the work is. A desk job costs well under $1 per $100 of wages; physical work costs several dollars per $100. Ask for the classification code they're using and make sure it matches the job.",
        "Don't skip this to save money. In most states operating without it is a fine on its own, before any injury.",
              ],
              "You have a workers' comp policy in force with a start date on or before your employee's first day.")
    s += step("Days 8 to 14", 4, "Choose a payroll provider", "The one decision that makes the rest of this easy",
              "A full-service payroll provider calculates every paycheck, withholds the taxes, deposits them "
              "with the IRS and your state on the right schedule, files the quarterly and annual returns, "
              "sends W-2s in January, and usually files your new-hire reports. For a first-time employer "
              "this is not optional. The math isn't hard; the deadlines and the deposit rules are where "
              "people get hurt, and a provider turns them into a monthly bill.",
              [
        "Section 3 compares five providers with September 2026 pricing and a \"pick this if\" line for each. A 3-person shop pays roughly $50 to $70 a month.",
        "\"Full service\" means they file and deposit for you. A cheaper \"basic\" plan that only calculates is a trap for a first-timer: you'd be doing the deposits yourself.",
        "Sign up before your first hire's start date. Setup asks for your EIN, state account numbers and bank details, and takes a few days.",
              ],
              "You have a payroll account set up with your EIN, state accounts and bank connected, and a first pay date scheduled.")
    s += step("First day of work", 5, "Collect the new-hire paperwork", "I-9, W-4, state withholding form, direct deposit",
              "Three forms, each with a different job. The I-9 proves the person may legally work in the US; "
               "you and the employee both sign it and you keep it (it's never sent anywhere unless asked). "
               "The W-4 tells you how much federal income tax to withhold; the employee fills it in. Most "
               "states have their own withholding form; the employee fills that in too. Your payroll provider "
               "usually collects all three digitally.",
              [
        "I-9: the employee completes Section 1 by their first day of work for pay. You complete Section 2, after seeing their original documents, within three business days of that first day. Keep it for three years after the hire date or one year after they leave, whichever is later.",
        "W-4: the employee's form; you don't fill it in for them or advise them on it. Enter it in payroll exactly as written.",
        "New-hire report: federal law requires you to report each new hire to your state's directory within 20 days (some states say sooner). Most payroll providers do this automatically; confirm yours does, because it's on you if it doesn't.",
              ],
              "Signed I-9 (both sections), W-4 and state form on file, direct-deposit details entered, new-hire report submitted.")

    # p5 step 6
    s += step("First pay date", 6, "Run your first payroll", "Section 6 walks through it line by line",
              "Enter hours, review the preview, approve. The provider calculates gross pay, withholding and "
               "the employer taxes, pays the employee, and schedules the deposits. Your job is to check three "
               "things before you approve: the hours are right, the pay rate is right, and the total cash "
               "leaving your account (net pay plus taxes) is what you expected.",
              [
        "Section 6 shows what every line on the pay stub means and what an employee really costs you per hour, so nothing on the preview surprises you.",
        "Move the employer tax money out of your operating account mentally, if not literally, the day you run payroll. It's not yours.",
        "Put the filing calendar (Section 6) on the wall. The provider files; you check that they did.",
              ],
              "Your employee has been paid, you can read every line of the stub, and the first deposit is scheduled.")
    s += [Spacer(1, 10),
          para("That's the whole sequence: EIN, state accounts, workers' comp, provider, paperwork, first "
               "payroll. Thirty days is comfortable; it's been done in a week when the state accounts come "
               "back fast. What you can't do is skip the order.", "intro"),
          h2("Your 30-day plan"),
          para("Write the date you expect to finish each step, then the date you did.", "small"),
          grid(["Step", "Target date", "Done on", "Account number or confirmation (last 4 only)"],
               [["1. EIN", "", "", ""], ["2. State withholding account", "", "", ""],
                ["2. State unemployment account", "", "", ""], ["2. Local tax account, if any", "", "", ""],
                ["3. Workers' comp policy", "", "", ""], ["4. Payroll provider", "", "", ""],
                ["5. New-hire paperwork and report", "", "", ""], ["6. First payroll run", "", "", ""]],
               [CW * 0.34, CW * 0.16, CW * 0.16, CW * 0.34], min_row_h=27),
          PB()]

    # p6 section 2
    s += [kicker("Section 2"), h1("W-2 or 1099? Decide before you agree on a rate"),
          para("Before anything else: is the person you're hiring an employee (W-2) or an independent "
               "contractor (1099)? You don't get to pick. The IRS decides based on the working relationship, "
               "and \"I'll just call them a contractor to keep it simple\" is the most expensive sentence in "
               "this guide.", "intro"),
          h2("What the IRS looks at"),
          para("Three areas. No single factor decides; the whole picture does.", "small"),
          grid([], [
              ["Behavioral control", "Do you decide how, when and where the work is done? Set the hours, provide training, give detailed instructions, require them to do it your way? That's employee territory. A contractor decides how to do the job and you judge the result."],
              ["Financial control", "Do you provide the tools and supplies? Are they paid by the hour or the week rather than by the job? Can they not make a profit or a loss on the work? Do they work only for you? Each of those points toward employee. A contractor has their own tools, their own other clients, and can lose money on a job."],
              ["Type of relationship", "Is the work a core part of what your business does, ongoing rather than a defined project, with benefits or the expectation of continuing? Employee. A written contract calling them a contractor does not, by itself, make them one."],
          ], [CW * 0.24, CW * 0.76], head=False, bold_first=True, row_pad=5),
          Spacer(1, 8),
          note("If you treat an employee as a contractor and the IRS or your state disagrees, you can be "
               "assessed the employment taxes you should have withheld and paid, including the employee's "
               "share, plus penalties and interest, going back years. State agencies (unemployment and "
               "workers' comp) run their own tests and some are stricter than the IRS's; several states use "
               "an \"ABC test\" that presumes a worker is an employee unless you prove otherwise. If you're "
               "unsure, the IRS will decide for you: file Form SS-8, and expect the answer to take six months "
               "or more, so don't wait on it to hire. If you've already been getting it wrong, the IRS "
               "Voluntary Classification Settlement Program (Form 8952) lets you reclassify with reduced back "
               "taxes. Both are worth a conversation with a CPA first.",
               title="What happens if you get it wrong"),
          h2("Worksheet 2: the W-2 vs 1099 decision checklist"),
          para("Ten yes/no questions about the working relationship. Count the yes answers. \"Yes\" points to "
               "employee every time, on purpose: the test is built to be hard to talk yourself out of.")]

    # p7 example + score
    questions = [
        "1. Will you set their schedule, or require specific hours?",
        "2. Will you tell them how to do the work, not just what result you want?",
        "3. Will you train them in your way of doing things?",
        "4. Will you provide the tools, equipment or supplies?",
        "5. Will you pay by the hour, day or week rather than by the job?",
        "6. Is this work a core part of what your business sells?",
        "7. Is the relationship open-ended rather than a defined project with an end?",
        "8. Will they work mostly or only for you, rather than running their own business with other clients?",
        "9. Can they NOT lose money on the work (no chance of a loss, only a wage)?",
        "10. Would you expect to give them benefits, paid time off, or a raise over time?",
    ]
    s += [KeepTogether([example_box([(q, "yes") for q in questions], widths=[CW * 0.82, CW * 0.18],
                      after="<b>Score: 10 of 10.</b> Sam sets the schedule, provides the supplies and the van, trains Maria on the Blue Door checklist, pays by the hour, and cleaning is the whole business. 10 of 10. Maria is an employee. Sam also ran the test on the bookkeeper he pays $150 a month: she sets her own hours, uses her own software, has 30 other clients, and is paid by the job. 0 of 10. She stays a contractor."),
          Spacer(1, 10),
          grid(["Your score", "What it means"], [
              ["8 to 10 yes answers", "Likely W-2. Hire them as an employee. This is most first hires."],
              ["4 to 7 yes answers", "Mixed. Get a CPA or employment attorney to look at it before you decide. Ten minutes of their time is cheaper than one reclassification."],
              ["0 to 3 yes answers", "Likely 1099. They run their own business and you're a client. Get a written agreement, collect a W-9, and send a 1099-NEC if you pay them $2,000 or more in a year (the threshold was $600 through 2025; it is $2,000 for payments made in 2026 and after, indexed for inflation from 2027)."],
          ], [CW * 0.26, CW * 0.74], bold_first=True, row_pad=5)]),
          PB()]

    # p8 worksheet 2
    s += [kicker("Your worksheet (write here)"), h1("W-2 vs 1099 decision checklist"),
          worksheet_rows(["Person or role:"], label_w=CW * 0.22, row_h=28),
          Spacer(1, 8),
          yesno_rows(questions),
          Spacer(1, 10),
          worksheet_rows(["Number of yes answers", "Result (likely W-2 / mixed, ask a CPA / likely 1099)"],
                         label_w=CW * 0.42, row_h=28),
          Spacer(1, 10),
          para("Notes (what made it close, what you'll ask the CPA):", "small"),
          Lines(CW, 5, gap=21),
          Spacer(1, 10),
          para("If the result is 1099: get a written agreement, collect a Form W-9 before the first payment, "
               "and set a reminder for January to send the 1099-NEC if you cross the threshold. If the result "
               "is W-2: go back to Section 1, step 4."),
          PB()]

    # p9 section 3 providers
    s += [kicker("Section 3"), h1("Choosing a payroll provider"),
          para("Five providers a first-time employer actually considers, with pricing pulled from their public "
               "pricing pages on September 29, 2026 and re-checked " + AS_OF + ". Two of them (Rippling and "
               "ADP) don't publish prices; they quote. That's not a knock, but a first-timer should know it "
               "before booking a demo.", "intro"),
          grid(["Provider", "Monthly base", "Per employee", "Tax filing included?", "Benefits admin?", "Who it's for"], [
              ["Gusto (Simple plan)", "$49 / month", "$6 / person / month", "Yes, federal and state, single state on Simple; multi-state needs Plus ($80 + $12)", "Yes, health benefits through Gusto's broker at no extra Gusto fee; workers' comp pay-as-you-go available", "Small teams that want the easiest setup and a clean employee app"],
              ["Rippling", "Quote-based (site says \"starts at $8 a month, per user\"; some products carry a base fee)", "Quote-based", "Yes (verify what's in your quote)", "Yes, as add-on modules (verify)", "Companies that expect to grow fast and want payroll, HR and IT in one platform"],
              ["QuickBooks Payroll (Workforce Payroll plan)", "Not published on Intuit's page; check current price", "Per-employee fee applies; check current price", "Yes, federal and state; one state included, $12 / month per additional state", "Access to benefits and workers' comp through partners; HR support on higher tiers", "Businesses already keeping their books in QuickBooks Online"],
              ["ADP Run (Essential)", "Quote-based (site advertises 3 months free)", "Quote-based", "Yes (all packages; verify)", "Available as add-ons (verify)", "Owners who want a big-name provider and a phone number to call"],
              ["Patriot Payroll (Full Service)", "$37 / month", "$5 / worker paid / month", "Yes, federal, state and local filings and deposits, year-end at no extra fee; $12 / month per additional state", "Basic; HR add-on $6 + $2 per employee; no built-in benefits broker", "Owners who want the cheapest full-service option and don't need frills"],
          ], [CW * 0.15, CW * 0.16, CW * 0.14, CW * 0.2, CW * 0.19, CW * 0.16], bold_first=True, row_pad=4),
          Spacer(1, 5),
          para("Pricing checked " + AS_OF + " on each provider's own page except QuickBooks, whose payroll-only "
               "price was not published that day. Verify current pricing on each provider's site before you "
               "buy. Promotional prices (50% off for 3 months, months free) are excluded above; ask what the "
               "price is after the promotion ends.", "small"),
          h2("Pick this if..."),
          grid([], [
              ["Gusto (Simple plan)", "You're a 1 to 10 person single-state shop and you'd like benefits later without changing systems."],
              ["Rippling", "You expect 20+ people within two years and want one system for everything. Otherwise it's more than you need."],
              ["QuickBooks Payroll (Workforce Payroll plan)", "You already use QuickBooks Online and want payroll to post straight into it. If you don't, this isn't a reason to start."],
              ["ADP Run (Essential)", "You want a rep and don't mind negotiating. Get the quote in writing, ask what happens after the free months, and compare it to the two published prices on this page."],
              ["Patriot Payroll (Full Service)", "Cost is the deciding factor and you're comfortable with a plainer interface. Do NOT pick the Basic plan; it doesn't file or deposit for you."],
          ], [CW * 0.3, CW * 0.7], head=False, bold_first=True, row_pad=4),
          PB()]

    # p10 example + worksheet 1
    s += [example_box([
        ("Shortlist", "Gusto Simple vs. Patriot Full Service"),
        ("Gusto Simple, 3 employees", "$49 + 3 x $6 = $67 / month, $804 / year"),
        ("Patriot Full Service, 3 employees", "$37 + 3 x $5 = $52 / month, $624 / year"),
        ("QuickBooks Workforce Payroll", "Skipped (Sam doesn't use QuickBooks Online; Intuit showed only bundle prices)."),
        ("Pick", "Gusto Simple. Blue Door is single-state, so Simple covers it. The $15 a month over Patriot buys pay-as-you-go workers' comp in the same system, an employee app the three cleaners can use from their phones, and a benefits broker if Sam ever moves to a group plan. (Gusto does not administer a QSEHRA; the Section 5 arrangement runs through a separate administrator either way.) If Sam were strictly minimizing cost, Patriot Full Service at $52 would do the job. Both file and deposit. ADP and Rippling: Sam skipped the demos; three employees don't justify a quote-based product."),
    ], widths=[CW * 0.3, CW * 0.7]),
        Spacer(1, 10),
        kicker("Your worksheet (write here)"), h1("Worksheet 1: payroll-provider comparison"),
        para("Fill in the top four from your own situation, then price your shortlist from the table on the "
             "Section 3 table (or the providers' sites) and write your pick and why.", "small"),
        worksheet_rows(["Number of employees in year one", "Number of states where employees will work",
                        "Do you already use QuickBooks Online?", "Do you want to offer health benefits in year one?",
                        "Provider 1 and monthly cost", "Provider 2 and monthly cost", "Provider 3 and monthly cost",
                        "Your pick and why"], row_h=26),
        Spacer(1, 8),
        para("Questions to ask before you sign (write the answers here):", "small"),
        worksheet_rows(["Will you register me for state accounts, or do I? Which states?",
                        "Do you file new-hire reports?", "What is the price after the promotion ends?",
                        "Is workers' comp available pay-as-you-go?"], row_h=26),
        PB()]

    # p11 section 4
    s += [kicker("Section 4"), h1("Registering as an employer in your state"),
          para("\"Registering as an employer\" in a state means two accounts, sometimes three. This section "
               "gives you the map, not the territory: the method to find your own state's offices and the "
               "checklist to complete. It does not contain 50-state instructions, because they change and a "
               "stale one is worse than none.", "intro"),
          grid([], [
              ["State withholding account", "So you can send the state the income tax you withhold from paychecks. Issued by the state's Department of Revenue (also called Department of Taxation, Tax Commission, or similar). Nine states have no income tax and skip this: Alaska, Florida, Nevada, New Hampshire, South Dakota, Tennessee, Texas, Washington, Wyoming. Washington taxes capital gains but not wages, so it skips this too."],
              ["State unemployment insurance account (SUTA / SUI)", "So you can pay state unemployment tax. Issued by the state's workforce, labor or employment department. Every state has this one. You'll be assigned a \"new employer rate,\" a percentage of each employee's wages up to a state wage base, that applies for your first few years until you get an experience rating."],
              ["Local taxes (some states)", "Cities, counties or school districts in some states levy their own wage taxes (Ohio, Pennsylvania, Indiana, Kentucky, Maryland and others). Your payroll provider handles most; ask specifically."],
          ], [CW * 0.26, CW * 0.74], head=False, bold_first=True, row_pad=5),
          h2("The lookup method")]
    s += [Paragraph(t, ST["bullet"], bulletText=f"{i + 1}.") for i, t in enumerate([
        "Search: \"[your state] register as an employer withholding account\" and \"[your state] employer unemployment insurance registration.\" Go to the .gov results only.",
        "Most states have a combined business portal (search \"[your state] business gateway\" or \"one stop\"). Register there if it exists; it often creates both accounts.",
        "Note every account number, the login, and the filing frequency the state assigns you (monthly, quarterly). Your payroll provider will ask for all of it.",
        "Ask your payroll provider which states they will register you in and which they won't. Get the answer in writing. This is the step behind Mistake 2 (Section 7).",
        "Repeat for every state where an employee physically works. Where the employee sits, not where your business sits.",
    ])]
    s += [Spacer(1, 6),
          note("The out-of-state trap (composite, not one person's story). An owner hires a first "
               "out-of-state employee and assumes the payroll company is handling that state's paperwork. "
               "It isn't, and the fines arrive a year later. The rule: a remote employee in another state "
               "means you register in that state, and you are responsible for it happening even if you pay "
               "someone else to do it.", title="The out-of-state trap"),
          PB()]

    # p12 example + worksheet 3
    ws3_labels = ["State", "Withholding account (agency, number, date received)",
                  "Unemployment account (agency, number, new employer rate, wage base)",
                  "Local taxes (which, rate, who files)",
                  "Workers' comp (state fund or private, carrier, policy start date)",
                  "Does your payroll provider register you here? (get it in writing)",
                  "New-hire reporting (agency, deadline, who files)"]
    s += [example_box([
        ("State", "Ohio (Blue Door's only state; all three employees work in Ohio)"),
        ("Withholding account", "Ohio Department of Taxation, employer withholding account. Registered through the Ohio Business Gateway. Account number received in 6 days."),
        ("Unemployment account", "Ohio Department of Job and Family Services, employer account. New employer rate 2.85% on the first $9,000 of each employee's wages for 2026 (2.7% plus a 0.15% technology fee Ohio added for 2026 and 2027; verify each January)."),
        ("Local taxes", "Yes. Ohio municipalities levy income tax; Blue Door's city withholds at 2.5%. Sam confirmed Gusto files it."),
        ("Workers' comp", "Ohio is a state-fund state: coverage comes from the Ohio Bureau of Workers' Compensation, not a private insurer. Sam applied at bwc.ohio.gov before Maria's first day."),
        ("Provider registers?", "Gusto: no. Sam registered himself and entered the account numbers. Confirmed in writing via support chat."),
        ("New-hire reporting", "Ohio New Hire Reporting Center, within 20 days. Gusto files it automatically; Sam confirmed the first one went through."),
    ], widths=[CW * 0.26, CW * 0.74]),
        Spacer(1, 10),
        kicker("Your worksheet (write here)"), h1("Worksheet 3: state registration checklist"),
        para("One copy per state where an employee will work. The next page is a second copy; photocopy it if you have more than two states.", "small"),
        worksheet_rows(ws3_labels, row_h=36),
        Spacer(1, 8),
        checklist(["All accounts open, numbers entered in payroll, provider's registration answer received in writing."]),
        PB()]

    # p13 worksheet 3, second copy (print addition)
    s += [kicker("Your worksheet (write here)"), h1("Worksheet 3: state registration checklist, second state"),
          para("Use this copy for a second state where an employee will work. Same rows, same rule: where the "
               "employee sits, not where your business sits.", "small"),
          worksheet_rows(ws3_labels, row_h=52),
          Spacer(1, 8),
          checklist(["All accounts open, numbers entered in payroll, provider's registration answer received in writing."]),
          Spacer(1, 8),
          para("Notes for this state:", "small"),
          Lines(CW, 5, gap=21),
          PB()]

    # p14 section 5
    s += [kicker("Section 5"), h1("Benefits for a team under ten: ICHRA and QSEHRA"),
          para("Owners of tiny teams postpone benefits because the options look either too expensive or too "
               "complicated. A law firm's blog put it as a question its clients keep asking: \"Have you found "
               "yourself postponing decisions about employee benefits because the options seem either too "
               "expensive or too complicated?\" For teams under ten there are two tools built for exactly "
               "this. Neither is a group health plan. Both let you set a monthly budget and reimburse "
               "employees, tax-free, for health insurance they buy themselves.", "intro"),
          h2("QSEHRA <font name='Body' size='9' color='#555555'>Qualified Small Employer Health Reimbursement Arrangement</font>"),
          para("For employers with fewer than 50 full-time-equivalent employees that don't offer a group "
               "health plan. You set a monthly allowance; employees buy their own individual coverage (on the "
               "marketplace or elsewhere) and submit proof; you reimburse them, tax-free to them and "
               "deductible to you. The IRS caps how much you can give: for 2026, $6,450 a year for an employee "
               "with self-only coverage and $13,100 for one with family coverage (Rev. Proc. 2025-32). You "
               "must offer it to all full-time employees on the same terms and give written notice at least "
               "90 days before the plan year. Employees need minimum essential coverage for reimbursements to "
               "be tax-free. Two things to tell employees: a QSEHRA reduces any marketplace premium subsidy "
               "they get, dollar for dollar, and can eliminate it if the allowance makes coverage "
               "\"affordable\" under the rules; and the allowance shows up on their W-2 (box 12, code FF). "
               "The annual cap is prorated for anyone covered less than the full year."),
          h2("ICHRA <font name='Body' size='9' color='#555555'>Individual Coverage Health Reimbursement Arrangement</font>"),
          para("(In September 2026 healthcare.gov began calling these \"CHOICE Arrangements\"; the rules below "
               "are unchanged and most administrators still say ICHRA.) Same idea, no cap on the allowance, "
               "any size employer, and you can set different allowances for different classes of employees "
               "(full-time vs. part-time, for example). Employees must be enrolled in individual coverage or "
               "Medicare. More flexible, slightly more rules, and administrators charge a bit more for it. If "
               "you're under 50 employees and your budget is under the QSEHRA cap, QSEHRA is usually the "
               "simpler pick."),
          h2("What it costs"),
          para("What it actually costs is your allowance times your headcount, plus an administrator. You can "
               "run either arrangement yourself, but the paperwork (plan documents, notices, substantiating "
               "every reimbursement) is why almost everyone pays an administrator. Published administrator "
               "pricing on September 29, 2026: PeopleKeep, $50 a month plus $25 per employee per month for "
               "QSEHRA (three-seat minimum); Take Command, from $25 per employee per month for QSEHRA and from "
               "$40 for ICHRA. Verify before you buy; these change.")]

    # p15 example + verify
    s += [KeepTogether([example_box([
        ("Employees offered the benefit", "3 (Maria, Devon, Priya; Sam offers it to all three)"),
        ("Monthly allowance per employee", "$300 (self-only; under the $537.50 monthly cap)"),
        ("Allowance per month", "3 x $300 = $900"),
        ("Administrator fee per month", "$50 + 3 x $25 = $125 (PeopleKeep published pricing, September 2026)"),
        ("Total per month", "$900 + $125 = $1,025"),
        ("Total per year", "$1,025 x 12 = $12,300"),
        ("Per employee per year", "$4,100, of which $3,600 reaches the employee"),
    ], widths=[CW * 0.36, CW * 0.64],
        after="Sam picked $300 because a marketplace bronze plan in his county runs roughly $400 to $500 a month for a 30-year-old before subsidies (check your own county at healthcare.gov). $300 doesn't cover it; it makes it easier, which is the point. Employees who get a marketplace subsidy should compare, because the allowance reduces the subsidy. If an employee is on a spouse's plan or Medicaid they can decline and Sam pays nothing for them. Unused allowance stays with Sam."),
        Spacer(1, 12),
        note("The limits are indexed and change every January. Verify the current-year QSEHRA limits "
             "(search \"IRS QSEHRA limit\" and the current revenue procedure) before you set an allowance.",
             title="Verify the limits every year")]),
        Spacer(1, 12),
        h2("Your allowance math, by the numbers"),
        para("Three things decide the yearly cost: how many people you offer it to, the monthly allowance, "
             "and the administrator. Work them in that order on Worksheet 4 (next page). Two checks before "
             "you commit:", "body"),
        ] + bullets([
            "The self-only allowance must stay at or under the IRS cap for the year ($6,450 for 2026, which is $537.50 a month).",
            "Notice must go out at least 90 days before the plan year. For a January 1 start, that means October 1 at the latest.",
        ]) + [PB()]

    # p16 worksheet 4
    s += [kicker("Your worksheet (write here)"), h1("Worksheet 4: benefits cost worksheet"),
          para("Allowance times employees, plus the administrator, times twelve. Write the math so you can see it.", "small"),
          worksheet_rows(["Arrangement (QSEHRA or ICHRA)", "Employees offered",
                          "Monthly allowance per employee (self-only)",
                          "Monthly allowance per employee (family), if different",
                          "Allowance per month (allowance x employees)", "Administrator and monthly fee",
                          "Total per month", "Total per year"], row_h=36),
          Spacer(1, 10),
          para("Decision and start date (QSEHRA needs written notice 90 days before the plan year; most "
               "first-timers start January 1 and send notice by October 1):", "small"),
          Lines(CW, 4, gap=22),
          Spacer(1, 10),
          para("Questions for the administrator (write the answers here):", "small"),
          worksheet_rows(["Do you handle the plan documents and the 90-day notice?",
                          "How are reimbursements substantiated?", "What is the fee after any promotion?"],
                         row_h=30),
          PB()]

    # p17 section 6 stub
    s += [kicker("Section 6"), h1("Your first payroll run, line by line"),
          para("Here is Maria's first paycheck, line by line, and then the part nobody warns you about: what "
               "she costs Blue Door on top of what she's paid.", "intro"),
          h2("Maria's pay stub, week 1 (30 hours at $20)"),
          grid(["Line", "Amount", "What it means"], [
              ["Gross pay", "$600.00", "Hours times rate before anything is taken out. 30 hours x $20."],
              ["Federal income tax withheld", "$30.00", "Estimated federal income tax, calculated from Maria's W-4 and the IRS tables. Illustrative amount; her real number depends on her W-4."],
              ["Social Security (employee)", "$37.20", "6.2% of gross, up to the annual wage base ($184,500 in 2026). Maria's share of the 12.4% total."],
              ["Medicare (employee)", "$8.70", "1.45% of gross, no cap. Maria's share of the 2.9% total."],
              ["Ohio income tax withheld", "$6.00", "State income tax from the state form and Ohio's tables. Illustrative."],
              ["City income tax withheld", "$15.00", "2.5% local tax where Blue Door operates. Many states have no local tax at all."],
              ["Net pay", "$503.10", "What lands in Maria's bank account. $600.00 minus the five lines above."],
          ], [CW * 0.28, CW * 0.14, CW * 0.58], bold_first=True),
          Spacer(1, 8),
          note("Everything withheld from Maria is her money that you're holding and must deposit on time. It "
               "is not income to you and it is not a cushion. This is the sentence Mistake 1 in Section 7 is "
               "about.", title="The money you're holding"),
          h2("What Maria costs on top of her pay"),
          para("On top of the $600 you owe Maria, you owe these, and they don't appear on her stub:", "small"),
          grid(["Employer tax or insurance", "Rate", "On $600 / week", "Notes"], [
              ["Social Security (employer match)", "6.2%", "$37.20", "Same as her share. Stops at the wage base."],
              ["Medicare (employer match)", "1.45%", "$8.70", "Same as her share. No cap."],
              ["FUTA (federal unemployment)", "0.6% of the first $7,000", "$3.60", "6.0% minus a 5.4% credit for paying state unemployment on time. $42 a year per employee, all of it in the first few months. A few states that owe the federal government lose part of the credit (California paid 1.8% net for 2025); your provider knows if yours is one."],
              ["SUTA (state unemployment)", "2.85% of the first $9,000", "$17.10", "Ohio's 2026 new-employer rate on Ohio's wage base (verify each January). Your state's rate and base will differ. $256.50 a year per employee at these figures."],
              ["Workers' comp (estimate)", "about $4 per $100 of wages", "$24.00", "Estimate for residential cleaning. Physical work runs several dollars per $100; office work well under $1. Your quote is the real number."],
          ], [CW * 0.24, CW * 0.17, CW * 0.12, CW * 0.47], bold_first=True)]

    # p18 true hourly cost
    s += [KeepTogether([h2("The true hourly cost of a $20-an-hour employee"),
          grid([], [
              ["Wage", "$20.00"],
              ["Social Security + Medicare match (7.65%)", "$1.53"],
              ["FUTA, spread over her hours ($42 / 1,560 hours a year)", "$0.03"],
              ["SUTA, spread over her hours ($256.50 / 1,560 hours; Ohio example)", "$0.16"],
              ["Workers' comp estimate (4% of wage)", "$0.80"],
              [Paragraph("True hourly cost before software and benefits", ST["cellb"]), Paragraph("$22.52", ST["cellb"])],
              ["Payroll software, Blue Door's share for Maria ($804 / 3 / 1,560 hours)", "$0.17"],
              ["QSEHRA allowance ($300 a month / 130 hours)", "$2.31"],
              [Paragraph("True hourly cost, all in", ST["cellb"]), Paragraph("$25.00", ST["cellb"])],
          ], [CW * 0.8, CW * 0.2], head=False, row_pad=5)]),
          Spacer(1, 8),
          para("So Maria at \"$20 an hour\" is $22.52 an hour before you've bought software or offered a single "
               "benefit, and $25 with the benefit from Section 5. The rule of thumb that survives: budget 10% "
               "to 15% on top of wages for taxes and insurance alone, more for physical work, and know your "
               "state's numbers. Unemployment taxes front-load: FUTA and most of SUTA are paid in the first "
               "months of the year, so January through March cost more than the rest."),
          Spacer(1, 6),
          para("Sources for every rate on these two pages: SSA Contribution and Benefit Base page (wage base "
               "$184,500 for 2026); IRS Tax Topic 751 (6.2% and 1.45%); IRS Tax Topic 759 (FUTA 6.0%, $7,000, "
               "5.4% credit); Ohio Department of Job and Family Services 2026 Rate Details and Ohio H.B. 96 "
               "(2.85% on $9,000). All checked " + AS_OF + ". The full list is on the Where the numbers come from page near the back.", "small"),
          h2("Your own employee, the same way"),
          para("Run the same lines for your first hire. Your state's SUTA rate and wage base come from "
               "Worksheet 3; the workers' comp rate comes from your quote.", "small"),
          worksheet_rows(["Wage per hour", "Social Security + Medicare match (wage x 7.65%)",
                          "FUTA per hour ($42 / hours a year)", "SUTA per hour (rate x wage base / hours a year)",
                          "Workers' comp per hour (rate x wage)", "True hourly cost before software and benefits",
                          "Payroll software per hour (yearly fee / employees / hours)",
                          "Benefit allowance per hour (monthly allowance / monthly hours)",
                          "True hourly cost, all in"], label_w=CW * 0.62, row_h=26),
          PB()]

    # p19 filing calendar
    s += [h1("The filing calendar"),
          para("What gets filed when. Put it on the wall.", "intro"),
          note("A due date that lands on a weekend or holiday moves to the next business day: January 31, "
               "2027 is a Sunday, so the January filings for 2026 are due February 1, 2027. A full-service "
               "provider does every filing on this list. Your job is the calendar on the wall and a "
               "two-minute check each deadline that it happened. If you ever see a notice from the IRS or the "
               "state, open it the day it arrives and send it to your provider the same day."),
          Spacer(1, 8),
          grid(["When", "What", "Notes", "Checked"], [
              ["Monthly, by the 15th", "Federal deposit (income tax withheld + both halves of Social Security and Medicare)", "New employers deposit monthly: everything withheld in a month is due by the 15th of the following month. Once your liability in the lookback period passes $50,000 you switch to semiweekly. $100,000 in a single day means next business day. Your provider deposits; you check.", CheckBox()],
              ["As your state sets it", "State withholding deposit", "Frequency set by your state when you registered (monthly or quarterly for small employers). Provider deposits.", CheckBox()],
              ["April 30, July 31, October 31, January 31", "Form 941, quarterly federal return", "Reports wages and the taxes you deposited that quarter. Provider files. Employers with $1,000 or less in annual liability may be told by the IRS to file Form 944 once a year instead.", CheckBox()],
              ["Quarterly, state deadlines vary", "State unemployment (SUTA) report and payment", "Wages per employee and the tax due. Provider files. Also the quarterly state withholding reconciliation in most states.", CheckBox()],
              ["Quarter-end + 1 month, when FUTA owed passes $500", "FUTA deposit", "Small employers often owe under $500 for the year and pay it all with Form 940.", CheckBox()],
              ["January 31", "Forms W-2 to employees and W-3 to the Social Security Administration", "Provider generates and files. You check every employee has one and the totals match your records.", CheckBox()],
              ["January 31", "Form 940, annual federal unemployment return", "Due January 31, or February 10 if you deposited everything on time.", CheckBox()],
              ["January 31", "Forms 1099-NEC to contractors", "Only if you paid any contractor at or above the threshold. Provider files if they're set up in it.", CheckBox()],
              ["Within 20 days of each hire", "New-hire report to the state", "Provider usually files. Confirm.", CheckBox()],
          ], [CW * 0.2, CW * 0.26, CW * 0.46, CW * 0.08], bold_first=True, row_pad=4.5),
          Spacer(1, 4),
          para("Sources: IRS Employment Tax Due Dates page and Publication 15 (deposit schedules, $50,000 "
               "lookback, $100,000 next-day rule, Form 944); IRS Tax Topic 759 (Form 940 dates and the $500 "
               "rule); IRS General Instructions for Forms W-2 and W-3 (February 1, 2027); IRS Instructions "
               "for Forms 1099-MISC and 1099-NEC; HHS Office of Child Support Services new-hire page (20 "
               "days). Checked " + AS_OF + ".", "small"),
          PB()]

    # p20 section 7 mistakes 1-3
    def mistake(num, title, story, cost, fix):
        return [KeepTogether([h2(f"{num}&nbsp;&nbsp;{title}"),
                              para(story, "body"),
                              para("<b>The cost.</b> " + cost),
                              note("<b>The fix.</b> " + fix, size=9.2)]), Spacer(1, 6)]

    s += [kicker("Section 7"), h1("Don't do this: five first-timer mistakes"),
          para("Patterns, not real people: each mistake is a composite of what first-time employers get "
               "wrong, with the cost and the one fix, mapped back to the sections you've just read.", "intro")]
    s += mistake(1, "Not knowing payroll taxes were a separate thing",
                 "Composite, not one person's quote: the owner who pays his people on time every week and never knew the withholding and the employer match had to be deposited separately, on a schedule, with the IRS, until the notices arrived.",
                 "The money withheld from employees was never yours, and the IRS can assess that withheld portion personally against the owner through the trust fund recovery penalty. Interest and failure-to-deposit penalties on top.",
                 "Full-service payroll from day one (Section 1, step 4), so deposits happen without you, and Section 6's stub walkthrough so you know what the deposits are. Then the calendar on the wall.")
    s += mistake(2, "Assuming the payroll company handled the other state",
                 "Composite, not one person's quote: the owner who hires a first out-of-state employee, assumes the payroll company is handling that state's registrations and filings, and finds out a year later that nothing was ever filed there.",
                 "Fines from the second state for unregistered, unfiled, unpaid unemployment and withholding, plus the back taxes, plus the time to untangle it.",
                 "Section 4's rule: register in every state where an employee works, and get your provider's answer to \"which states will you register me in?\" in writing before the hire starts.")
    s += mistake(3, "Calling the first hire a contractor to keep it simple",
                 "Composite, not one person's quote: the owner who pays a full-time, scheduled, supervised worker as a 1099 contractor because \"it's easier\" and \"they said it was fine.\" It's the most common first-hire mistake in every CPA's inbox, and it's why Section 2 comes before the provider comparison.",
                 "Reclassification: the employment taxes you should have paid, potentially including the employee's share, penalties and interest, back to the start. Plus state unemployment and workers' comp exposure, which is where the injury claim you weren't insured for lands.",
                 "Run the ten questions in Section 2 before you agree on a rate. If the answer is W-2, hire them as W-2. If it's unclear, Form SS-8 or a CPA.")

    # p21 mistakes 4-5
    s += mistake(4, "Postponing benefits because it looked expensive or complicated",
                 "\"Have you found yourself postponing decisions about employee benefits because the options seem either too expensive or too complicated?\" The question a Michigan law firm's blog (Coonen Law) put to small-business owners, because it's what they hear.",
                 "The good employee who leaves for the job with health coverage. Replacing a trained person costs weeks of your time; the allowance that would have kept them costs $300 a month.",
                 "Section 5: a QSEHRA or ICHRA at a budget you set, with the math worked out. A $300 allowance for three people is about $1,025 a month all in, and it's deductible.")
    s += mistake(5, "Hiring before you could cover payroll",
                 "Composite, not one person's quote: the owner who hires because the work is there, then discovers on the first payday that the true cost is 12% above the wage, that the taxes leave the account whether or not a client has paid, and that a late paycheck isn't an option. The fear that arrives on the first payday is the most common one in this guide.",
                 "Late paychecks are a wage-law violation in most states, not just a bad look. Late deposits are Mistake 1. And the stress of it makes every other decision worse.",
                 "Before the hire, Section 6's true-cost math (Maria is $22.52 an hour, not $20) and two payrolls' worth of cash set aside in a separate account, taxes included. Payroll is the bill you pay first, every time.")
    s += [Spacer(1, 6),
          para("Five mistakes, five fixes, all of them in the sequence you've just read. Each one is the "
               "pattern, not one person's story. The guide exists so none of these are yours.", "intro"),
          h2("Your two-payroll reserve"),
          para("Mistake 5's fix, worked for your own numbers. Fill it in before the first hire.", "small"),
          worksheet_rows(["Gross wages for one pay period, all employees",
                          "Employer taxes and insurance for one period (about 10% to 15% of wages; your Section 6 math)",
                          "Cash out for one payroll (wages + employer taxes)",
                          "Two payrolls' worth, the reserve to set aside",
                          "Separate account it sits in"], label_w=CW * 0.6, row_h=28),
          PB()]

    # p22 whole thing on one page
    s += [h1("The whole thing on one page"),
          para("Tick them off in order. When every box is checked, you're an employer.", "intro"),
          checklist([
              "EIN received from irs.gov (free)",
              "State withholding account registered, number received",
              "State unemployment account registered, number and new-employer rate received",
              "Local tax accounts, if your state has them",
              "Workers' comp policy in force before day one",
              "W-2 vs 1099 test done (Section 2), result recorded",
              "Payroll provider chosen (Section 3), full service, account set up and bank connected",
              "Provider confirmed in writing which states they register and which filings they make",
              "Employee's I-9 Section 1 by day one, your Section 2 within three business days",
              "W-4 and state withholding form entered exactly as the employee wrote them",
              "New-hire report filed within 20 days (confirm who files)",
              "First payroll previewed: hours, rate, total cash out; then approved",
              "Filing calendar (Section 6) on the wall",
              "Two payrolls of cash, taxes included, set aside",
              "Benefits decision made or scheduled (Section 5)",
          ], size=9.8, gap=7),
          Spacer(1, 10),
          para("Dates and account numbers (keep them here; this page will hold your EIN and state account "
               "numbers, so store this book somewhere secure):", "small"),
          Lines(CW, 8, gap=22),
          PB()]

    # p23 sources
    s += [h1("Where the numbers come from"),
          para("Verified September 29, 2026; re-checked " + AS_OF + ". Everything that changes by year or by "
               "state is marked in the text; verify it for your own state and year.", "intro"),
          grid([], [
              ["Social Security wage base and FICA rates, 2026", "Social Security Administration, Contribution and Benefit Base (ssa.gov/oact/cola/cbb.html)"],
              ["FUTA rate, wage base, credit, Form 940 due dates and deposit rule", "IRS Tax Topic 759, Form 940"],
              ["Form 941 due dates, deposit schedules, $100,000 rule, Form 944, W-2 due date", "IRS, Employment Tax Due Dates and Publication 15 (Circular E)"],
              ["Form I-9 timing and retention", "USCIS, I-9 Central and Handbook for Employers M-274; 8 CFR 274a.2"],
              ["New-hire reporting, 20 days", "HHS Office of Child Support Services, Employer Responsibilities: New Hire Reporting"],
              ["Worker classification factors, Form SS-8, VCSP", "IRS, Independent Contractor (Self-Employed) or Employee?"],
              ["QSEHRA 2026 limits and rules", "IRS Rev. Proc. 2025-32, section 4.63 (irs.gov/pub/irs-drop/rp-25-32.pdf); IRS Notice 2017-67; healthcare.gov QSEHRA page"],
              ["Provider pricing, September 29 and " + AS_OF, "Gusto, Patriot Software, Rippling, ADP, PeopleKeep and Take Command public pricing pages; Intuit's QuickBooks Payroll pricing page (payroll-only price not published on the date checked)"],
              ["Ohio 2026 new-employer rate and wage base", "Ohio Department of Job and Family Services, 2026 Rate Details (jfs.ohio.gov); Ohio H.B. 96 (0.15% fee, 2026-2027)"],
              ["Quotation (Sections 5, 7)", "Coonen Law, PLLC blog (June 9, 2025), quoted with attribution. All Section 7 mistakes are composites."],
          ], [CW * 0.36, CW * 0.64], head=False, bold_first=True, row_pad=5),
          Spacer(1, 10),
          note("This is an operator's guide, not legal or tax advice. Confirm with a CPA or attorney for "
               "your state. Rates, limits, prices and deadlines were verified September 29, 2026, re-checked "
               + AS_OF + ", and will change. Nothing here guarantees compliance or a penalty-free outcome; it "
               "lowers the odds, in order. The business, owner and employees in the examples are fictional. "
               "Built September 2026; " + VERSION_LINE.lower() + ".", title="The honest fine print"),
          Spacer(1, 14),
          Paragraph("Go hire your first person.", ParagraphStyle("go", fontName="Head", fontSize=14, leading=18)),
          PB()]

    # p24 terms
    terms = [
        ("License.", "Your purchase gives you a personal license to use this book for yourself or one business you own. You may write in it and copy its pages for that use. You may not resell, share, give away, upload, scan for distribution or redistribute it, in original or edited form, or use it to make a competing product."),
        ("Ownership.", "The design, text and formulas belong to ProofNotFluff. Buying the product doesn't transfer ownership."),
        ("Information only.", "This product shares general information and tools for planning. It is not legal, tax, accounting, financial, employment, medical or other professional advice, and it doesn't create a client relationship of any kind. Your situation may differ. For decisions that matter, check with a qualified professional and the official source."),
        ("Accuracy.", "Rates, rules and figures were checked against the sources named in the product on the date above. Laws, prices and platform rules change, and state and local rules vary. You're responsible for confirming anything you rely on."),
        ("Estimates.", "Calculations depend on the numbers you enter and simplify real-world conditions. They are estimates, not promises of any result, income, savings, approval or outcome."),
        ("No warranty.", "The product is provided \"as is\", without warranties of any kind, to the extent the law allows."),
        ("Limit of liability.", "To the extent the law allows, ProofNotFluff is not liable for any loss or damage from using or relying on this product, and its total liability for any claim is limited to the price you paid for it. Nothing here limits rights you have under consumer protection laws that can't be waived."),
        ("Trademarks.", "Gusto, Rippling, QuickBooks, ADP, Patriot Software, PeopleKeep, Take Command, Amazon and Etsy are trademarks of their owners. ProofNotFluff isn't affiliated with, sponsored or endorsed by them. Prices and features are quoted from their public pages on the date stated in the product and are not offers."),
        ("AI assistance.", "This product was made with AI assistance and reviewed and tested by the shop owner."),
        ("Help.", "If this book arrives damaged or misprinted, ask the store you bought it from for a replacement. If something in the text looks wrong, the correction goes into the next printing, and the edition line below tells you which printing you have."),
        ("Examples.", "Blue Door Cleaning Co., its owner and its employees are fictional. The mistakes in Section 7 are composites, not real people."),
    ]
    s += [h1("Terms of Use and Disclaimer"),
          para("ProofNotFluff | First-Time Employer Payroll and Benefits Setup Guide, paperback edition | "
               "Version 2, " + AS_OF, "small"),
          note(SHORT_NOTICE + "\n" + TIER_CLAUSE, title="Notice", size=8.8), Spacer(1, 8)]
    tstyle = ParagraphStyle("terms", fontName="Body", fontSize=9.6, leading=12.2, spaceAfter=5)
    s += [Paragraph(f"<b>{a}</b> {b}", tstyle) for a, b in terms]
    s += [Spacer(1, 8), para("Made by ProofNotFluff. Written by a finance executive. " + VERSION_LINE + ".", "small"),
          PB()]

    # p25 notes
    s += [h1("Notes"),
          para("Account numbers (last 4 only), who you spoke to, what they said, what's next.", "intro"),
          Lines(CW, 26, gap=22), PB()]

    # p26 review
    s += [h1("A small favor"),
          para("If this guide got you to a first legal paycheck, a short review on Amazon helps the next "
               "first-time employer find it.", "intro"),
          para("A sentence about which step you were stuck on, or what the true-cost math changed for you, is "
               "enough. Reviews are read by real people deciding whether to start, and yours might be the "
               "nudge. No incentive is offered for a review, and none should be."),
          para("ProofNotFluff makes plain tools for money, hiring and family planning, written by a finance "
               "executive. More titles in this series are listed under the ProofNotFluff author page on "
               "Amazon."),
          Spacer(1, 10),
          h2("Your first payroll, for the record"),
          worksheet_rows(["Date of the first legal paycheck", "Employee number one's role",
                          "Provider you chose", "What you'd tell a friend about to hire"], row_h=30),
          Spacer(1, 14),
          para("First-Time Employer Payroll and Benefits Setup Guide. " + VERSION_LINE + ". ProofNotFluff.", "small")]
    return s


def build_interior(path):
    P.register_fonts()
    styles()
    P._base_font()
    doc = BaseDocTemplate(path, pagesize=(P.TRIM_W, P.TRIM_H), title="First-Time Employer Payroll and Benefits Setup Guide",
                          author="ProofNotFluff", subject="Payroll and benefits setup guide, paperback",
                          creator="ProofNotFluff print build", keywords="", pageCompression=1,
                          initialFontName="Body")
    frame = Frame(SIDE, BOTTOM, CW, P.TRIM_H - TOP - BOTTOM, leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0, id="body")
    doc.addPageTemplates([
        PageTemplate(id="title", frames=[Frame(SIDE, BOTTOM, CW, 10, id="t")], onPage=title_page),
        PageTemplate(id="body", frames=[frame], onPage=body_footer),
    ])
    st = [NextPageTemplate("body"), PageBreak()] + story()
    doc.build(st)
    P.strip_unused_fonts(path)
    return doc.page


def build_cover(path, pages):
    return P.build_cover(
        path, pages,
        title_lines=["First-Time Employer", "Payroll and Benefits", "Setup Guide"],
        title_size=40,
        subtitle="From \"I want to hire\" to a first legal paycheck in 30 days. Every step in order, "
                 "nothing assumed, with four worksheets you fill in by hand.",
        kicker="A ProofNotFluff operator's guide",
        back_hook="From \"I want to hire\" to a first legal paycheck in 30 days.",
        back_intro="Written for the owner about to hire employee number one, who knows nothing about "
                   "employer payroll and is afraid of the IRS. The fear is reasonable. The fix is a "
                   "sequence, not a lawyer.",
        bullets=[
            "The 30-day sequence: EIN, state accounts, workers' comp, provider, paperwork, first payroll, "
            "each with a \"you're done when\" checkpoint.",
            "The W-2 vs 1099 test, a payroll-provider comparison with dated pricing, and ICHRA and QSEHRA "
            "explained with the cost worked out.",
            "Every pay-stub line defined, the true hourly cost of a $20-an-hour employee ($22.52 before "
            "software or benefits), the filing calendar, and five first-timer mistakes with the one fix "
            "for each.",
        ],
        back_close="Federal rules summarized from IRS, SSA and HHS pages as of the date printed inside. "
                   "State and local rules can add to or change them. Information and planning tool "
                   "only, not legal, tax or HR advice.",
        byline="Written by a finance executive",
        spine_text=None,
        panel_title="Inside",
        panel_items=["The 30-day sequence", "W-2 or 1099? Ten questions",
                     "Choosing a payroll provider", "Registering in your state",
                     "ICHRA and QSEHRA, with the math", "Your first payroll, line by line",
                     "The true hourly cost of a hire", "The filing calendar",
                     "Five first-timer mistakes", "Four worksheets, worked examples"],
    )


if __name__ == "__main__":
    interior = os.path.join(HERE, "interior.pdf")
    cover = os.path.join(HERE, "cover.pdf")
    pages = build_interior(interior)
    print(f"interior: {pages} pages -> {interior}")
    assert PAGES_EXPECTED is None or pages == PAGES_EXPECTED, (pages, PAGES_EXPECTED)
    assert 24 <= pages <= 110, pages
    geo = build_cover(cover, pages)
    print(f"cover: spine {geo['spine_in']} in, spread {geo['width_in']} x {geo['height_in']} in -> {cover}")
