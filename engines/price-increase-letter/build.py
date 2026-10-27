#!/usr/bin/env python3
"""Free Price Increase Letter Template (site freebie, built Oct 26, 2026 on Todd's go in a live chat).

One content source, three outputs, so the words never drift:
  docs/downloads/price-increase-letter-template.docx   editable, plain brackets (typing over a field keeps no styling)
  docs/downloads/price-increase-letter-template.pdf    printable, fields tinted, rendered with Chromium (Playwright)
  docs/free-price-increase-letter-template/index.html  the <!--pnf-preview--> block between its markers is rewritten

Usage: python3 engines/price-increase-letter/build.py
"""
import html, io, os, re, sys, zipfile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DL = os.path.join(ROOT, "docs", "downloads")
SLUG = "free-price-increase-letter-template"
PAGE = os.path.join(ROOT, "docs", SLUG, "index.html")
NAME = "price-increase-letter-template"
PRODUCT = "Price Increase Letter Template"
CHECKED = "October 26, 2026"
CALC = "proofnotfluff.com/price-increase-calculator/"
DOCX_URL = "proofnotfluff.com/downloads/price-increase-letter-template.docx"

FIELD = re.compile(r"\[[^\[\]]+\]")

HEAD = ["[Your business name]", "[Phone]  |  [Email]", "", "[Date]", "", "Dear [Customer first name],"]
SIGN = ["[Your name]", "[Your business name]"]

LETTERS = [
    {"key": "standard", "title": "Standard notice", "use": "For most customers. Short, clear, and it answers the questions people ask first: how much, from when, and what stays the same.",
     "body": [
         "Thank you for choosing [Your business name] for your [service, for example every-other-week house cleaning].",
         "Starting [effective date], the price of your [service] will change from [old price] to [new price] per [visit, month or job]. Everything else stays the same: the same [team, day and checklist].",
         "We review our prices [once a year] so we can keep paying our team fairly and keep doing the work the way you expect. [Optional: This is our first price change since (year).]",
         "Any [visits] before [effective date] stay at your current price. If you have questions, call or text me at [phone] or reply to this [email].",
         "Thank you for your business.",
     ]},
    {"key": "loyal", "title": "Long-time customer", "use": "For customers who have been with you for years. It thanks them first and gives them something for staying: a later start date or a small loyalty discount.",
     "body": [
         "You have been with us since [year], and we don't take that for granted. [Optional: a personal thank-you, for example: Thank you for always making room for us on short notice.]",
         "I wanted you to hear this from me first. Starting [effective date], the price of your [service] will go from [old price] to [new price] per [visit]. [Optional: It is the first change to your price in (number) years.]",
         "Because you have been with us so long, [pick one and delete the other: your new price won't start until (later date) / we are keeping a (dollar amount) loyalty discount on your new price].",
         "Nothing else changes. Same [team], same [day], same care.",
         "If you would like to talk it over, call me at [phone]. Thank you for [number] years.",
     ]},
    {"key": "cost", "title": "Rising costs", "use": "When one cost, such as fuel, supplies, insurance or labor, is the reason. It names the cost and shows the change in dollars.",
     "body": [
         "I'm writing to let you know about a change to our prices, and the reason for it.",
         "Over the past [12 months], what we pay for [supplies, fuel, insurance or labor] has gone up. [Optional: name the cost, for example: Our fuel bill went from about (old amount) to (new amount) a month.] We have covered the difference ourselves until now, but to keep [the same products, crew and schedule] on every visit, we need to adjust.",
         "Starting [effective date], your [service] will be [new price] per [visit], up from [old price]. That is [difference] more per [visit].",
         "[Optional: If (cost) comes back down, we will look at our prices again in (month).]",
         "Questions? Call or text me at [phone]. Thank you for sticking with us.",
     ]},
]

NOTICE_CHOICES = [
    ("2 weeks", "Short. Some owners use it for one-time or on-call work, where there is no regular schedule to plan around."),
    ("30 days", "About one billing cycle for customers you bill monthly, so the new price lands on the next full month."),
    ("60 days or more", "More time to plan. Some owners give this to long-time customers or customers on a set schedule."),
    ("At renewal", "If you sell seasonal or yearly plans, change the price when the plan renews instead of in the middle of it."),
]

STEPS = [
    ("Pick the new price first.", f"The free price increase calculator ({CALC}) shows the price that keeps your profit or your margin after your costs rise, and how many customers you can lose before you earn less than today."),
    ("Pick a version.", "Standard notice for most customers, long-time customer for people who have been with you for years, rising costs when one cost is the reason."),
    ("Fill every bracket.", "In the Word file, search for [ to find each field. Delete any Optional line you don't use, and the version box at the top of the page."),
    ("Pick how much notice to give.", "These are choices, not rules. Pick one and use the same date for every customer who gets the same letter."),
    ("Send it the way you bill.", "Email it to customers you invoice by email. Print it and leave it with the invoice for customers you see in person. A short text can point to the email. Send every copy on the same day."),
    ("Keep a record.", "Note the date you sent each letter in your client list, so you can answer \"when did you tell me?\" later."),
]
AGREEMENT = ("If a customer has a written agreement with you, check what it says about price changes before you pick a date. "
             "This page doesn't say what any law requires, and rules can vary by place and by contract.")
SAMPLE = "These are sample letters to adapt, not legal documents written for your state or business."
SHORT_NOTICE = ("For general information and planning only. This is not legal, tax, financial, medical or other professional advice, "
                "and using it doesn't create a professional relationship. Results are estimates based on the numbers you enter. "
                f"Figures were checked on {CHECKED} and can change. See the Terms of Use page before you rely on anything here.")
TERMS = [
    ("License", "This free template is for your own use or one business you own. You may edit it, print it and send the letters to your own customers. You may not resell, upload or redistribute the template, or use it to make a competing product."),
    ("Ownership", "The design and text of the template belong to ProofNotFluff. The letters you fill in and send are yours."),
    ("Information only", "This product shares general information and tools for planning. It is not legal, tax, accounting, financial, employment, medical or other professional advice, and it doesn't create a client relationship of any kind. Your situation may differ. For decisions that matter, check with a qualified professional and the official source."),
    ("Accuracy", "Rates, rules and figures were checked against the sources named in the product on the date above. Laws, prices and platform rules change, and state and local rules vary. You're responsible for confirming anything you rely on. The template uses no outside rates or rules: every price and date in a letter comes from you."),
    ("Estimates", "Calculations depend on the numbers you enter and simplify real-world conditions. They are estimates, not promises of any result, income, savings, approval or outcome."),
    ("No warranty", "The product is provided \"as is\", without warranties of any kind, to the extent the law allows."),
    ("Limit of liability", "To the extent the law allows, ProofNotFluff is not liable for any loss or damage from using or relying on this product. Nothing here limits rights you have under consumer protection laws that can't be waived."),
    ("Trademarks", "Microsoft Word and Google Docs are trademarks of their owners. ProofNotFluff isn't affiliated with, sponsored or endorsed by them."),
    ("AI assistance", "This product was made with AI assistance and reviewed and tested by the shop owner."),
    ("Help", "Reply to any ProofNotFluff email if something looks wrong and it will be fixed."),
]
AI_LINE = "Made with AI assistance and reviewed and tested by the shop owner."


def check_text():
    """No nested brackets, no em or en dashes, nothing a buyer could read as a promise."""
    alltext = " ".join(HEAD + SIGN + [x for L in LETTERS for x in [L["title"], L["use"]] + L["body"]]
                       + [a + b for a, b in NOTICE_CHOICES + STEPS + TERMS] + [AGREEMENT, SAMPLE, SHORT_NOTICE])
    assert "\u2014" not in alltext and "\u2013" not in alltext, "dash"
    for L in LETTERS:
        for p in L["body"]:
            depth = 0
            for ch in p:
                depth += ch == "["; depth -= ch == "]"
                assert 0 <= depth <= 1, ("nested bracket", p)
    assert not re.search(r"guarantee|risk-free|legally binding|ensures? compliance", alltext, re.I)


# ------------------------------------------------------------------ docx
def build_docx(path):
    from docx import Document
    from docx.enum.section import WD_SECTION
    from docx.enum.text import WD_BREAK
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Pt, RGBColor, Inches

    FIELD_BLUE = RGBColor(0x1F, 0x4E, 0x9E)
    INK, MUTED, ACCENT, TEAL = RGBColor(0x1D, 0x24, 0x33), RGBColor(0x5C, 0x62, 0x70), RGBColor(0xA6, 0x3E, 0x21), RGBColor(0x2E, 0x6B, 0x66)
    d = Document()
    sec = d.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    for side in ("left_margin", "right_margin"):
        setattr(sec, side, Inches(1))
    sec.top_margin, sec.bottom_margin = Inches(0.9), Inches(0.9)
    st = d.styles["Normal"]
    st.font.name = "Arial"; st.font.size = Pt(11); st.font.color.rgb = INK
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    st.paragraph_format.space_after = Pt(8); st.paragraph_format.line_spacing = 1.15
    for lvl, size in (("Heading 1", 20), ("Heading 2", 13)):
        h = d.styles[lvl]; h.font.name = "Arial"; h.font.size = Pt(size); h.font.bold = True; h.font.color.rgb = INK
        rf = h.element.rPr.find(qn("w:rFonts"))
        if rf is not None:
            for a in list(rf.attrib):
                del rf.attrib[a]
            rf.set(qn("w:ascii"), "Arial"); rf.set(qn("w:hAnsi"), "Arial")
        h.paragraph_format.space_before = Pt(14 if lvl == "Heading 2" else 0); h.paragraph_format.space_after = Pt(6)

    def para(text, size=None, color=None, bold=False, after=None, lead=None):
        p = d.add_paragraph()
        if lead:
            r = p.add_run(lead + " "); r.bold = True
            if size: r.font.size = Pt(size)
        r = p.add_run(text); r.bold = bold
        if size: r.font.size = Pt(size)
        if color is not None: r.font.color.rgb = color
        if after is not None: p.paragraph_format.space_after = Pt(after)
        return p

    def shade(run, hexfill):
        rpr = run._r.get_or_add_rPr()
        shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hexfill)
        rpr.append(shd)

    def letter_para(text, after):
        """Bracket fields in input blue, bold, on a light yellow fill, as in the PDF and on the page."""
        p = d.add_paragraph(); last = 0
        for m in FIELD.finditer(text):
            if m.start() > last:
                p.add_run(text[last:m.start()])
            r = p.add_run(m.group(0)); r.bold = True; r.font.color.rgb = FIELD_BLUE; shade(r, "FDF6DC")
            last = m.end()
        if last < len(text):
            p.add_run(text[last:])
        p.paragraph_format.space_after = Pt(after)
        return p

    def boxed_note(text, lead):
        """The version note in a bordered, tinted box (a one-cell table), as in the PDF."""
        tb = d.add_table(rows=1, cols=1)
        cell = tb.rows[0].cells[0]
        tcpr = cell._tc.get_or_add_tcPr()
        borders = OxmlElement("w:tcBorders")
        for side in ("top", "left", "bottom", "right"):
            e = OxmlElement(f"w:{side}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "6"); e.set(qn("w:color"), "E2DDD3")
            borders.append(e)
        tcpr.append(borders)
        shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), "FAF8F4")
        tcpr.append(shd)
        cp_ = cell.paragraphs[0]; cp_.paragraph_format.space_after = Pt(2); cp_.paragraph_format.space_before = Pt(2)
        r = cp_.add_run(lead + " "); r.bold = True; r.font.size = Pt(8.5)
        r = cp_.add_run(text); r.font.size = Pt(8.5); r.font.color.rgb = MUTED
        sp = d.add_paragraph(); sp.paragraph_format.space_after = Pt(6)

    def eyebrow(text):
        p = para(text.upper(), size=8.5, color=ACCENT, bold=True, after=2)
        return p

    def page_break():
        d.paragraphs[-1].add_run().add_break(WD_BREAK.PAGE)

    # page 1: how to send it
    eyebrow("Free template from ProofNotFluff")
    d.add_heading("Price increase letter template", level=1)
    para("Three short letters that tell your customers about a new rate. Pick one, fill in the brackets, and send it. "
         "Version 1 is on page 2, version 2 on page 3, version 3 on page 4.", color=MUTED)
    d.add_heading("How to send it", level=2)
    for i, (lead, text) in enumerate(STEPS, 1):
        p = para(text, lead=f"{i}. {lead}", after=5, size=10.5)
        p.paragraph_format.left_indent = Inches(0.0)
    d.add_heading("How much notice: choices, not rules", level=2)
    t = d.add_table(rows=0, cols=2)
    t.autofit = False
    grid = t._tbl.tblGrid.findall(qn("w:gridCol"))
    for gc, w in zip(grid, (Inches(1.45), Inches(5.05))):
        gc.set(qn("w:w"), str(int(w.twips)))
    for k, v in NOTICE_CHOICES:
        row = t.add_row().cells
        row[0].width, row[1].width = Inches(1.45), Inches(5.05)
        row[0].paragraphs[0].add_run(k).bold = True
        row[1].paragraphs[0].add_run(v)
        for c in row:
            for pp in c.paragraphs:
                pp.paragraph_format.space_after = Pt(4)
                for r in pp.runs:
                    r.font.size = Pt(10)
    para(AGREEMENT, size=9.5, color=MUTED, after=10).paragraph_format.space_before = Pt(6)
    para(SAMPLE + " " + SHORT_NOTICE, size=8.5, color=MUTED, after=0)

    for i, L in enumerate(LETTERS, 1):
        page_break()
        boxed_note(f"{L['use']} Delete this box before you send.", f"Version {i} of 3: {L['title']}.")
        for line in HEAD:
            letter_para(line, after=0 if line != HEAD[-1] else 10)
        for b in L["body"]:
            letter_para(b, after=10)
        para("", after=18)
        for line in SIGN:
            letter_para(line, after=0)

    page_break()
    eyebrow("Terms")
    d.add_heading("Terms of Use and Disclaimer", level=1)
    para(f"ProofNotFluff | {PRODUCT} | Version 1, {CHECKED}", size=9.5, color=MUTED, bold=True)
    for lead, text in TERMS:
        para(text, lead=lead + ".", size=9.5, after=6)
    para(f"Free calculator to pick your new price: {CALC}", size=9.5, color=TEAL, after=0)

    # footer: product and page number
    fp = sec.footer.paragraphs[0]
    r = fp.add_run(f"{PRODUCT}  |  ProofNotFluff  |  Sample letters to adapt. Not legal advice."); r.font.size = Pt(8); r.font.color.rgb = MUTED

    cp = d.core_properties
    now = datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None)
    cp.author = "ProofNotFluff"; cp.last_modified_by = "ProofNotFluff"   # legal_scan accepts only ProofNotFluff here; the LLC is the Company; cp.title = PRODUCT
    cp.subject = "Free template, version 1"; cp.keywords = "ProofNotFluff"; cp.comments = ""; cp.category = ""
    cp.created = now; cp.modified = now; cp.revision = 1
    buf = io.BytesIO(); d.save(buf)
    # drop python-docx's stock thumbnail and set the company and application in docProps/app.xml
    zin = zipfile.ZipFile(io.BytesIO(buf.getvalue()))
    out = io.BytesIO(); zout = zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        if item.filename == "docProps/thumbnail.jpeg":
            continue
        data = zin.read(item.filename)
        if item.filename == "_rels/.rels":
            data = re.sub(rb'<Relationship Id="[^"]+" Type="[^"]+/thumbnail" Target="docProps/thumbnail.jpeg"/>', b"", data)
        if item.filename == "[Content_Types].xml":
            data = data.replace(b'<Default Extension="jpeg" ContentType="image/jpeg"/>', b"")
        if item.filename == "docProps/app.xml":
            data = data.replace(b"<Company/>", b"<Company>ProofNotFluff LLC</Company>")
            data = data.replace(b"<Application>Microsoft Macintosh Word</Application>", b"<Application>ProofNotFluff</Application>")
        zout.writestr(item, data)
    zout.close()
    open(path, "wb").write(out.getvalue())


# ------------------------------------------------------------------ html (pdf and page preview)
def fields_html(text):
    out, last = [], 0
    for m in FIELD.finditer(text):
        out.append(html.escape(text[last:m.start()]))
        out.append(f'<span class="fld">{html.escape(m.group(0))}</span>')
        last = m.end()
    out.append(html.escape(text[last:]))
    return "".join(out)


def letter_html(L, cls="letter"):
    head = "".join(f"<p>{fields_html(x)}</p>" if x else '<p class="gap" aria-hidden="true"></p>' for x in HEAD)
    body = "".join(f"<p>{fields_html(b)}</p>" for b in L["body"])
    sign = "".join(f"<p>{fields_html(x)}</p>" for x in SIGN)
    return f'<div class="{cls}">{head}{body}<div class="sign">{sign}</div></div>'


PDF_CSS = """
@page{size:Letter;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Arial,"Liberation Sans",Helvetica,sans-serif;color:#1d2433;background:#fff;font-size:10.5pt;line-height:1.42}
.page{width:8.5in;height:11in;padding:.62in .75in .7in;position:relative;page-break-after:always;overflow:hidden}
.page:last-child{page-break-after:auto}
h1,h2{font-family:Poppins,Arial,sans-serif;font-weight:700;letter-spacing:-.01em}
.eyebrow{font-size:8pt;letter-spacing:.14em;text-transform:uppercase;color:#a63e21;font-weight:700}
h1{font-size:24pt;line-height:1.08;margin:.06in 0 .08in}
h2{font-size:12.5pt;margin:.2in 0 .06in}
.lede{color:#4a5163;font-size:11pt;max-width:6.6in}
.bars{display:flex;gap:4px;margin:.08in 0 .04in}.bars i{display:block;width:.26in;height:4px;border-radius:2px}
.bars i:nth-child(1){background:#c8502f}.bars i:nth-child(2){background:#2e6b66}.bars i:nth-child(3){background:#6b4fa0}.bars i:nth-child(4){background:#2f5f9e}.bars i:nth-child(5){background:#a87c1f}
ol.steps{list-style:none;counter-reset:s}
ol.steps li{counter-increment:s;position:relative;padding:.045in 0 .045in .34in;border-bottom:1px solid #efebe3;font-size:10pt}
ol.steps li::before{content:counter(s);position:absolute;left:0;top:.05in;width:.22in;height:.22in;border-radius:50%;background:#2e6b66;color:#fff;font-weight:700;font-size:8.5pt;line-height:.22in;text-align:center}
table{width:100%;border-collapse:collapse;font-size:9.8pt;margin-top:.04in}
th{text-align:left;font-size:7.6pt;letter-spacing:.08em;text-transform:uppercase;color:#5c6270;font-weight:700;padding:.03in .06in;border-bottom:1px solid #1d2433}
td{padding:.055in .06in;border-bottom:1px solid #efebe3;vertical-align:top}
td.k{font-weight:700;white-space:nowrap;width:1.35in}
.note{font-size:9pt;color:#4a5163;margin-top:.1in}
.small{font-size:8.2pt;color:#4a5163;margin-top:.14in}
.calc{margin-top:.16in;background:#e2efec;border-left:4px solid #2e6b66;border-radius:8px;padding:.1in .14in;font-size:10pt}
.tag{font-size:8.4pt;color:#5c6270;border:1px solid #e2ddd3;border-radius:8px;padding:.07in .11in;margin-bottom:.3in;background:#faf8f4}
.tag b{color:#1d2433}
.letter{font-size:11pt;line-height:1.5}
.letter p{margin:0 0 .13in}
.letter p:nth-child(-n+5){margin:0}
.letter p.gap{height:.15in}
.letter .sign{margin-top:.3in}.letter .sign p{margin:0}
.fld{background:#fdf6dc;color:#1f4f9a;font-weight:700;border-radius:3px;padding:0 0 0 2px;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.terms p{font-size:9pt;margin-bottom:.075in}
.foot{position:absolute;left:.75in;right:.75in;bottom:.38in;font-size:7.4pt;color:#5c6270;border-top:1px solid #e2ddd3;padding-top:.06in;display:flex;justify-content:space-between}
"""


def pdf_html():
    pages = []
    foot = lambda n: f'<div class="foot"><span>{PRODUCT} | ProofNotFluff | proofnotfluff.com</span><span>Page {n} of 5</span></div>'
    steps = "".join(f"<li><b>{html.escape(a)}</b> {html.escape(b)}</li>" for a, b in STEPS)
    rows = "".join(f'<tr><td class="k">{html.escape(a)}</td><td>{html.escape(b)}</td></tr>' for a, b in NOTICE_CHOICES)
    pages.append(f"""<section class="page">
<p class="eyebrow">Free template · ProofNotFluff</p><div class="bars"><i></i><i></i><i></i><i></i><i></i></div>
<h1>Price increase letter template</h1>
<p class="lede">Three short letters that tell your customers about a new rate. Pick one, fill in the yellow fields, and send it. The letters are on pages 2, 3 and 4. To type yours, use the Word file: {DOCX_URL}</p>
<h2>How to send it</h2><ol class="steps">{steps}</ol>
<h2>How much notice: choices, not rules</h2>
<table><tr><th>Notice</th><th>When owners pick it</th></tr>{rows}</table>
<p class="note">{html.escape(AGREEMENT)}</p>
<p class="small">{html.escape(SAMPLE)} {html.escape(SHORT_NOTICE)}</p>
{foot(1)}</section>""")
    for i, L in enumerate(LETTERS, 1):
        pages.append(f"""<section class="page">
<p class="tag"><b>Version {i} of 3: {html.escape(L['title'])}.</b> {html.escape(L['use'])} Leave this box off the copy you send.</p>
{letter_html(L)}
{foot(i + 1)}</section>""")
    terms = "".join(f"<p><b>{html.escape(a)}.</b> {html.escape(b)}</p>" for a, b in TERMS)
    pages.append(f"""<section class="page terms">
<p class="eyebrow">Terms</p>
<h1 style="font-size:20pt">Terms of Use and Disclaimer</h1>
<p style="font-size:9.6pt;margin-bottom:.14in;color:#4a5163"><b>ProofNotFluff | {PRODUCT} | Version 1, {CHECKED}</b></p>
{terms}
<div class="calc">Pick the new price before you send the letter: the free price increase calculator at <b>{CALC}</b> shows the price that keeps your profit or margin, and how many customers a raise can lose.</div>
{foot(5)}</section>""")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{PRODUCT}</title><style>{PDF_CSS}</style></head><body>{''.join(pages)}</body></html>"""


def render_pdf(html_text, path, title, subject):
    from playwright.sync_api import sync_playwright
    from pypdf import PdfReader, PdfWriter
    tmp = path + ".src.html"
    open(tmp, "w", encoding="utf-8").write(html_text)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        pg.goto("file://" + tmp, wait_until="load"); pg.evaluate("document.fonts.ready")
        raw = pg.pdf(format="Letter", print_background=True, prefer_css_page_size=True, tagged=True, outline=False)
        b.close()
    os.remove(tmp)
    r = PdfReader(io.BytesIO(raw)); w = PdfWriter()
    for page in r.pages:
        w.add_page(page)
    stamp = datetime.now(timezone.utc).strftime("D:%Y%m%d%H%M%S+00'00'")
    w.add_metadata({"/Title": title, "/Author": "ProofNotFluff LLC", "/Subject": subject, "/Creator": "ProofNotFluff LLC",
                    "/Producer": "ProofNotFluff LLC", "/Keywords": "ProofNotFluff", "/CreationDate": stamp, "/ModDate": stamp})
    if "/Lang" not in w._root_object:
        from pypdf.generic import NameObject, TextStringObject
        w._root_object[NameObject("/Lang")] = TextStringObject("en-US")
    with open(path, "wb") as f:
        w.write(f)


def page_preview():
    """The visible template on the sign-up page: version 1 open, versions 2 and 3 one tap away."""
    tabs = []
    for i, L in enumerate(LETTERS, 1):
        body = letter_html(L, cls="pl-letter")
        if i == 1:
            tabs.append(f'<div class="pl-card"><p class="pl-tag"><b>Version 1: {html.escape(L["title"])}.</b> {html.escape(L["use"])}</p>{body}</div>')
        else:
            tabs.append(f'<details class="pl-more"><summary>Version {i}: {html.escape(L["title"])}</summary>'
                        f'<div class="pl-card"><p class="pl-tag">{html.escape(L["use"])}</p>{body}</div></details>')
    return "<!--pnf-preview-->" + "".join(tabs) + "<!--/pnf-preview-->"


def page_howto():
    steps = "".join(f"<li><b>{html.escape(a)}</b> {html.escape(b).replace('The free price increase calculator (' + html.escape(CALC) + ')', '<a href=\"../price-increase-calculator/\">The free price increase calculator</a>')}</li>"
                    for a, b in STEPS)
    rows = "".join(f'<tr><th scope="row">{html.escape(a)}</th><td>{html.escape(b)}</td></tr>' for a, b in NOTICE_CHOICES)
    return (f'<!--pnf-howto--><ol class="pl-steps">{steps}</ol><h3>How much notice: choices, not rules</h3>'
            f'<table class="pl-notice"><caption class="pl-vh">Notice periods owners pick, and when</caption><thead><tr><th scope="col">Notice</th>'
            f'<th scope="col">When owners pick it</th></tr></thead><tbody>{rows}</tbody></table><p class="pl-note">{html.escape(AGREEMENT)}</p><!--/pnf-howto-->')


def main():
    check_text()
    os.makedirs(DL, exist_ok=True)
    build_docx(os.path.join(DL, NAME + ".docx"))
    render_pdf(pdf_html(), os.path.join(DL, NAME + ".pdf"), PRODUCT, "Free template: three price increase letters for service businesses")
    if os.path.isfile(PAGE):
        t = open(PAGE, encoding="utf-8").read()
        t2 = re.sub(r"<!--pnf-preview-->.*?<!--/pnf-preview-->", lambda m: page_preview(), t, flags=re.S)
        t2 = re.sub(r"<!--pnf-howto-->.*?<!--/pnf-howto-->", lambda m: page_howto(), t2, flags=re.S)
        if t2 != t:
            open(PAGE, "w", encoding="utf-8").write(t2)
        sys.path.insert(0, os.path.join(ROOT, "engines"))
        import thanks_page
        thanks_page.write(ROOT, SLUG, "price increase letter template",
                          [(NAME + ".docx", "Download the Word file", "All three letters to type in, 5 pages"),
                           (NAME + ".pdf", "Download the PDF", "Printable, 5 pages")],
                          "No Microsoft Word? Upload the .docx to Google Drive and open it with Google Docs. It works the same.",
                          ("price-increase-calculator", "Pick your new price with the free price increase calculator"))
    print("built", NAME + ".docx", NAME + ".pdf")


if __name__ == "__main__":
    main()
