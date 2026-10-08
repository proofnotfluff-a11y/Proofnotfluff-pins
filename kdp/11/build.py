#!/usr/bin/env python3
"""Build the KDP paperback print pack for #11, "Everything They'll Need"
(End of Life Planner and Emergency Binder).

Source of truth: the legally cleared v1.1 digital binder (legal/reviews/
11-2026-10-06.md). This script re-sets every page for print: no form fields,
ruled lines and checkboxes instead, black and white, fonts embedded,
8.5 x 11 in trim, no bleed. Page numbers 4 to 40 match the digital binder so
every in-text page reference still holds.

Outputs (same folder): interior.pdf, cover.pdf.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_common"))

import pnfprint as P  # noqa: E402

BOOK = "Everything They'll Need"
AS_OF = "October 6, 2026"
VERSION_LINE = "Paperback edition 1.1, October 2026"
PAGES_EXPECTED = 42

SHORT_NOTICE = ("For general information and planning only. This is not legal, tax, "
                "financial, medical or other professional advice, and using it doesn't "
                "create a professional relationship. Results are estimates based on the "
                "numbers you enter. Figures were checked on " + AS_OF + " and can change. "
                "See the Terms of Use page before you rely on anything here.")
ESTATE_CLAUSE = ("This is an organizer, not a legal document. It is not a will, trust, "
                 "power of attorney, health care directive or beneficiary form, and "
                 "filling it in has no legal effect. Laws vary by state. Talk to an estate "
                 "planning attorney about the documents you need. It will hold sensitive "
                 "information: store it somewhere secure and share it only with people "
                 "you trust.")

SECTIONS = [
    ("START HERE", 2), ("ABOUT ME AND MY PEOPLE", 5), ("HEALTH", 8),
    ("IMPORTANT DOCUMENTS", 10), ("MONEY", 12), ("HOME AND PROPERTY", 21),
    ("DIGITAL LIFE", 24), ("PEOPLE AND PETS WHO COUNT ON ME", 26), ("FINAL WISHES", 28),
    ("IN MY OWN WORDS", 31), ("FOR MY FAMILY", 33), ("KEEPING IT CURRENT", 38),
]

CONTENTS = [
    ("START HERE", [("How to use this book", 2), ("Contents", 3), ("Start here", 4)]),
    ("ABOUT ME AND MY PEOPLE", [("About me", 5), ("My family", 6), ("Key contacts", 7)]),
    ("HEALTH", [("Medical information", 8), ("Health care decisions", 9)]),
    ("IMPORTANT DOCUMENTS", [("Where my documents are", 10), ("The documents most people need", 11)]),
    ("MONEY", [("Money at a glance", 12), ("Bank accounts", 13), ("Retirement and investments", 14),
               ("Beneficiary check-up", 15), ("Insurance", 16), ("Debts and credit cards", 17),
               ("Bills, autopays and subscriptions", 18), ("Taxes, business and rentals", 19),
               ("Money that's easy to miss", 20)]),
    ("HOME AND PROPERTY", [("My home", 21), ("Utilities and home services", 22),
                           ("Vehicles, property and valuables", 23)]),
    ("DIGITAL LIFE", [("Getting into my devices", 24), ("Email, accounts and wishes", 25)]),
    ("PEOPLE AND PETS WHO COUNT ON ME", [("Children and dependents", 26), ("Pets", 27)]),
    ("FINAL WISHES", [("Final wishes", 28), ("For my obituary", 29), ("People to tell", 30)]),
    ("IN MY OWN WORDS", [("A few words from me", 31), ("A few more words", 32)]),
    ("FOR MY FAMILY", [("If I'm in the hospital", 33), ("After I die: the first 72 hours", 34),
                       ("The first month", 35), ("The first year", 36), ("Calls and claims log", 37)]),
    ("KEEPING IT CURRENT", [("Once a year", 38), ("Wallet card and door note", 39),
                            ("You did something kind", 40), ("Sources and Terms of Use", 41),
                            ("A small favor", 42)]),
]


def section_for(page_no):
    name = SECTIONS[0][0]
    for s, start in SECTIONS:
        if page_no >= start:
            name = s
    return name


# ------------------------------------------------------------------ pages --

def p01_title(c, n):
    f = P.Flow(c, n)
    L, R, top, bottom = f.L, f.R, f.top, f.bottom
    W = f.W
    y = top - 30
    P.color_bars(c, L, y, w=20, h=4.5, gap=4)
    y -= 26
    P.draw_label(c, "THE FAMILY EMERGENCY BINDER", L, y, size=7.5, gray=0.3, space=1.6)
    y -= 66
    c.setFont("Head", 38)
    c.setFillGray(0)
    c.drawString(L, y, "Everything")
    y -= 44
    c.drawString(L, y, "They'll Need")
    y -= 14
    c.setFillGray(0.15)
    c.rect(L, y, 44, 3.2, stroke=0, fill=1)
    y -= 34
    y = P.draw_wrapped(c, "What my family would need to know, all in one place.",
                       L, y, W, "BodyI", 16, 20, 0.15)
    y -= 34
    # ownership lines
    for label, extra in (("THIS BINDER BELONGS TO", None), ("LAST FULL REVIEW", "IF FOUND, PLEASE CALL")):
        if extra:
            half = (W - 16) / 2
            P.draw_label(c, label, L, y, size=6.5)
            P.rule(c, L, L + half, y - 22)
            P.draw_label(c, extra, L + half + 16, y, size=6.5)
            P.rule(c, L + half + 16, R, y - 22)
        else:
            P.draw_label(c, label, L, y, size=6.5)
            P.rule(c, L, R, y - 22)
        y -= 50
    y -= 16
    # inside list
    P.draw_label(c, "INSIDE", L, y, size=7, gray=0.3, space=1.4)
    y -= 16
    left_items = ["About me and my people", "Health", "Important documents", "Money",
                  "Home and property", "Digital life"]
    right_items = ["People and pets who count on me", "Final wishes", "In my own words",
                   "For my family", "Keeping it current"]
    c.setFont("Body", 10.5)
    c.setFillGray(0.1)
    yy = y
    for it in left_items:
        c.setFillGray(0.2)
        c.rect(L, yy + 2.5, 5, 5, stroke=0, fill=1)
        c.setFillGray(0.1)
        c.drawString(L + 12, yy, it)
        yy -= 18
    yy = y
    for it in right_items:
        c.setFillGray(0.2)
        c.rect(L + W / 2, yy + 2.5, 5, 5, stroke=0, fill=1)
        c.setFillGray(0.1)
        c.drawString(L + W / 2 + 12, yy, it)
        yy -= 18
    y -= 18 * len(left_items) + 14
    # legal notice block, bottom-anchored
    f.y = y
    f.note(SHORT_NOTICE + "\n" + ESTATE_CLAUSE, title="BEFORE YOU RELY ON THIS BOOK",
           size=8.0, at_bottom=True)
    # between the inside list and the note: confidentiality line
    c.setFont("BodyB", 9.5)
    c.setFillGray(0.1)
    c.drawString(L, f.floor + 22, "Private and confidential. Keep this binder somewhere safe, "
                                  "and tell two people where it is.")
    # footer: only the book title, no page number on the title page
    c.setFont("HeadMed", 6.2)
    c.setFillGray(0.4)
    c.drawString(L, bottom - 16, "PROOFNOTFLUFF", charSpace=0.9)
    c.drawRightString(R, bottom - 16, VERSION_LINE.upper(), charSpace=0.6)


def p02_how_to_use(c, n):
    f = P.Flow(c, n)
    f.title("START HERE", "How to use this book",
            "This page is for you, the person filling it in. The rest of the binder is "
            "written so your family can follow it on a hard day.")
    steps = [
        ("Start with page 4 and your key contacts on page 7.",
         "The Start Here page and your key contacts take about 30 minutes, and they cover "
         "most of what your family would need in the first week. If you only do one thing "
         "this month, do those."),
        ("Write in pencil, or in pen with a correction plan.",
         "Every line in this book is spaced for handwriting. Pencil makes updates easy. If "
         "you'd rather type and reprint pages, the fillable digital version is at the "
         "ProofNotFluff shop on Etsy. Every page has a Page updated date in the footer, so "
         "your family can see how current each page is."),
        ("Write where things are, not the secrets themselves.",
         "Don't write full passwords, full account numbers or your Social Security number "
         "here. Write the bank and the last 4 digits, and where the password or card is "
         "kept. A lost binder should not be a gift to a thief."),
        ("Store it somewhere safe.",
         "A fireproof box at home is better than a bank safe deposit box. A box in only your "
         "name can be hard for family to open quickly after a death. If you keep a digital "
         "copy or photos of these pages, keep them somewhere protected, like an encrypted "
         "drive or a password manager's secure file storage. Don't email them to yourself."),
        ("Tell two people where it is.",
         "A binder nobody can find doesn't help anyone. Tell your executor and one other "
         "person you trust. The wallet card on page 39 helps."),
        ("Look at it once a year.",
         "Pick a date you won't miss, like your birthday or when you do your taxes. The "
         "checklist on page 38 takes about 20 minutes."),
    ]
    size, leading = 9.8, 12.6
    for i, (lead, body) in enumerate(steps):
        h = (1 + len(P.wrap(body, "Body", size, f.W - 26))) * leading
        f.need(h + 6, "step")
        c.setFillGray(0.15)
        c.circle(f.L + 7, f.y - 7, 7, stroke=0, fill=1)
        c.setFillGray(1)
        c.setFont("Head", 8.5)
        c.drawCentredString(f.L + 7, f.y - 10, str(i + 1))
        c.setFillGray(0)
        c.setFont("Head", 10.5)
        c.drawString(f.L + 24, f.y - 10.5, lead)
        y = P.draw_wrapped(c, body, f.L + 24, f.y - 10.5 - leading, f.W - 26, "Body",
                           size, leading, 0.12)
        f.y = y + leading - 10
    f.gap(4)
    f.subhead("Your progress", size=11.5)
    boxes = ["About me", "Health", "Documents", "Money", "Home", "Digital",
             "Kids and pets", "Wishes", "My words", "For family", "Updates"]
    f.checklist(boxes, cols=4, size=9.2, row_gap=6)
    f.note("This binder is an organizer, not a legal document. It doesn't replace a will, "
           "a trust, a power of attorney or a health care directive. It tells your family "
           "where those are and what you want. If you don't have those documents yet, the "
           "Documents section shows which ones most people need, so you know what to ask "
           "an attorney about.")
    f.small_caps_head("Notes")
    f.lines(fill=True, min_n=1)


def p03_contents(c, n):
    f = P.Flow(c, n)
    f.title("START HERE", "Contents",
            "Each section's name sits at the top of its pages, and every page has a "
            "Page updated line in the footer.")
    col_w = (f.W - 24) / 2
    cols = [[], []]
    # split sections into two columns, left heavier
    left_names = {"START HERE", "ABOUT ME AND MY PEOPLE", "HEALTH", "IMPORTANT DOCUMENTS",
                  "MONEY", "HOME AND PROPERTY"}
    for sec, items in CONTENTS:
        (cols[0] if sec in left_names else cols[1]).append((sec, items))
    y0 = f.y
    for ci, col in enumerate(cols):
        x = f.L + ci * (col_w + 24)
        y = y0
        for sec, items in col:
            y -= 12
            P.draw_label(c, sec, x, y, size=6.6, gray=0.3, space=1.0)
            y -= 6
            for name, pg in items:
                y -= 14
                c.setFont("Body", 10)
                c.setFillGray(0.1)
                c.drawString(x, y, name)
                c.setFont("HeadMed", 8.5)
                c.drawRightString(x + col_w, y, str(pg))
                # dotted leader
                c.setStrokeGray(0.75)
                c.setLineWidth(0.4)
                c.setDash(1, 3)
                tw = P.pdfmetrics.stringWidth(name, "Body", 10)
                c.line(x + tw + 5, y + 2.5, x + col_w - 16, y + 2.5)
                c.setDash()
            y -= 6
        f.y = min(f.y, y)
    f.y -= 10


def p04_start_here(c, n):
    f = P.Flow(c, n)
    f.title("READ THIS FIRST", "Start here",
            "If you're reading this, something has happened to me. Take a breath. You don't "
            "have to do everything today. This page tells you who to call and where things "
            "are. The pages after it fill in the rest.")
    f.fields([[("This binder was written for", 1), ("Written by", 1)]])
    f.subhead("Call these people first")
    f.table(["Name", "Relationship", "Phone", "Why call them"], [3, 2, 2, 3], nrows=5, row_h=26)
    f.subhead("Where the important things are")
    f.table(["What", "Where it is, or who has it"], [3, 6],
            labels=["My will and other legal papers", "This binder's digital file, if any",
                    "Password manager emergency access", "My phone passcode",
                    "Spare house and car keys", "Fireproof box or safe, and its key or code",
                    "Cash kept at home", "Pet care instructions"], row_h=27)
    f.subhead("Then go to the page that fits")
    f.two_col_notes("Who decides, what to bring, and which bills to keep paying. Page 33",
                    "What to do in the first 72 hours, the first month, and the first year. Page 34",
                    "If I'm in the hospital or can't speak for myself", "If I have died")


def p05_about_me(c, n):
    f = P.Flow(c, n)
    f.title("ABOUT ME AND MY PEOPLE", "About me",
            "The basic facts your family will be asked for again and again: by the hospital, "
            "the funeral home, the bank and the court.")
    f.fields([
        [("Full legal name", 1), ("Other names used (maiden, nicknames)", 1)],
        [("Date of birth", 1), ("Place of birth (city, state)", 1.4), ("Citizenship", 1)],
        [("Home address", 2), ("Phone", 1)],
        [("Email", 1.3), ("SSN: last 4 only", 0.7), ("Where the card is kept", 1)],
        [("Driver's license: state and where kept", 1), ("Passport: where kept", 1)],
    ], h=31, gap=5)
    f.subhead("Family status", size=11.5)
    f.option_row("Marital status", ["Single", "Married", "Partnered", "Divorced", "Widowed"],
                 extra="Since (year)", h=28)
    f.fields([
        [("Spouse or partner's name", 1.2), ("Date married", 0.7), ("Where the marriage certificate is", 1.2)],
        [("Former spouse(s) and divorce year", 1), ("Where the divorce decree is", 1)],
    ], h=28, gap=4)
    f.subhead("Work and service", size=11.5)
    f.fields([
        [("Employer or former employer", 1.2), ("Job title", 1), ("HR or benefits phone", 1)],
        [("Retired from", 1), ("Pension or retiree benefits contact", 1)],
    ], h=28, gap=4)
    f.option_row("Military service", ["No", "Yes"], extra="Branch, years, and where your DD-214 is kept", h=28)
    f.fields([[("Faith community, if any", 1), ("Clubs, unions or groups that should be told", 1)]], h=28, gap=4)
    f.subhead("For the death certificate", size=11.5)
    f.fields([
        [("Father's full name and birthplace", 1), ("Mother's full name (incl. maiden) and birthplace", 1)],
        [("Highest level of education", 1), ("Usual occupation and industry", 1)],
    ], h=28, gap=4)
    f.note("Veterans may be eligible for burial in a national cemetery, a headstone or marker, "
           "and a burial allowance. The family will need the discharge papers (form DD-214) "
           "to apply, which is why it's worth knowing exactly where yours is.", at_bottom=True)


def p06_family(c, n):
    f = P.Flow(c, n)
    f.title("ABOUT ME AND MY PEOPLE", "My family",
            "Close family, so the people helping know who's who and how to reach them.")
    # table fills, then notes area below
    f.table(["Name", "Relationship", "Phone", "Email", "City"], [2.6, 1.6, 1.7, 2.4, 1.4],
            nrows=11, row_h=24)
    f.subhead("Notes about family", size=11.5)
    f.para("Anything helpful to know: someone who should hear the news in person, a relative "
           "who isn't in touch, someone who will need extra support.", size=9.2, gray=0.3)
    f.lines(fill=True)


def p07_key_contacts(c, n):
    f = P.Flow(c, n)
    f.title("ABOUT ME AND MY PEOPLE", "Key contacts",
            "The people with a job to do. If a role doesn't apply, leave it blank.")
    f.note("Ask the people you name before you name them, and tell them where this binder is. "
           "An executor or health care agent who hears about the job for the first time in an "
           "emergency starts from behind.", at_bottom=True)
    roles = ["Executor (named in my will)", "Backup executor", "Health care agent",
             "Financial power of attorney", "Attorney", "Accountant or tax preparer",
             "Financial advisor", "Insurance agent", "Primary doctor", "Employer HR or benefits",
             "Clergy or spiritual contact", "Neighbor with a key", "Landlord, HOA or property manager",
             "Someone who knows my computer", "Other", "Other"]
    avail = f.y - f.floor - 15
    row_h = min(30, (avail) / len(roles))
    f.table(["Role", "Name", "Phone", "Email or notes"], [2.4, 2.6, 1.8, 2.8],
            labels=roles, row_h=row_h)


def p08_medical(c, n):
    f = P.Flow(c, n)
    f.title("HEALTH", "Medical information",
            "What a doctor or EMT would ask, written down so nobody has to guess.")
    f.fields([
        [("Primary doctor", 1.2), ("Phone", 0.8), ("Preferred hospital", 1.2)],
        [("Pharmacy and phone", 1.2), ("Blood type", 0.6), ("Health insurance or Medicare plan", 1.3)],
        [("Where my insurance cards are", 1), ("Medigap, Part D or supplemental plan", 1)],
    ], h=27, gap=4)
    f.subhead("Medications", size=11.5)
    f.table(["Medication", "Dose", "When I take it", "What it's for", "Prescribed by"],
            [2.2, 1, 1.5, 2, 1.6], nrows=8, row_h=22)
    f.subhead("Specialists", size=11.5)
    f.table(["Doctor", "Specialty", "Phone", "Clinic or hospital"], [2.2, 1.8, 1.6, 2.4],
            nrows=5, row_h=22)
    f.fields([[("Allergies and reactions", 1), ("Conditions and past surgeries", 1)]], h=50, gap=4)
    f.option_row("Organ and tissue donor", ["Yes", "No", "Undecided"],
                 extra="Registered where (license, state registry)", h=28)


def p09_health_decisions(c, n):
    f = P.Flow(c, n)
    f.title("HEALTH", "Health care decisions",
            "Who speaks for me if I can't, and what I'd want them to say.")
    f.note("Hospitals need to see your directive and agent document, and the originals are "
           "often locked in a drawer when the call comes. Give your agent and your doctor "
           "copies now. Some states also run an advance directive registry. A HIPAA release "
           "lets doctors talk to the people you name, even if they aren't your agent.",
           at_bottom=True)
    f.table(["Document", "Have it", "Date signed", "Where the original is", "Who has a copy"],
            [2.6, 0.8, 1.2, 2.6, 2.0],
            labels=["Advance directive or living will", "Health care power of attorney (or proxy)",
                    "HIPAA release", "POLST, MOLST or DNR order", "Long-term care insurance policy"],
            row_h=26, checks=(1,))
    f.fields([[("My health care agent", 1.3), ("Phone", 0.8), ("Backup agent and phone", 1.3)]],
             h=28, gap=4)
    f.subhead("What matters to me", size=11.5)
    f.para("Your directive covers the legal part. This is the human part: what a good day looks "
           "like for you, what you'd want to avoid, and what your agent should keep in mind if "
           "it comes to a hard choice. It isn't an advance directive and has no legal effect; "
           "it's notes for the people you've named.", size=9.2, gray=0.3)
    f.lines(fill=True, reserve=44)
    f.option_row("If I'm seriously ill, I'd prefer to be cared for",
                 ["At home if possible", "In a hospital", "In hospice", "No preference"], h=30)


def p10_documents(c, n):
    f = P.Flow(c, n)
    f.title("IMPORTANT DOCUMENTS", "Where my documents are",
            "Finding papers is one of the hardest jobs for a family. Check what you have, and "
            "say exactly where the original is.")
    f.note("If you keep originals in a bank safe deposit box, add a co-owner or check what your "
           "bank and state allow after a death. In some cases the family needs a court order to "
           "open a box held in one name, and the will might be inside it.", at_bottom=True)
    docs = ["Will", "Trust", "Financial power of attorney", "Birth certificate",
            "Marriage certificate", "Divorce papers", "Social Security card", "Passport",
            "Military discharge (DD-214)", "Property deeds", "Vehicle titles",
            "Life insurance policies", "Last 3 years of tax returns", "Prenup or postnup",
            "Pre-paid funeral or cemetery contract", "Adoption or citizenship papers",
            "Business agreements", "Other"]
    avail = f.y - f.floor - 15
    row_h = min(26, avail / len(docs))
    f.table(["Document", "Have it", "Where the original is", "Who has a copy"],
            [2.6, 0.8, 3.2, 2.4], labels=docs, row_h=row_h, checks=(1,))


def p11_documents_needed(c, n):
    f = P.Flow(c, n)
    f.title("IMPORTANT DOCUMENTS", "The documents most people need",
            "A quick check of the big four. If one is missing, this is your list for a "
            "conversation with an estate attorney.")
    f.note("Review your documents after a marriage, divorce, birth, death, move to another "
           "state, or a big change in what you own. Those are the moments when old documents "
           "most often stop matching your life.", at_bottom=True)
    f.checklist([
        ("Will", "Says who gets what and names your executor. If you have minor children, it's "
                 "also where you name a guardian. Without one, state law decides."),
        ("Financial power of attorney", "Lets someone you choose handle money and paperwork if "
                                        "you can't. Without one, your family may have to go to "
                                        "court for a guardianship or conservatorship."),
        ("Health care power of attorney", "Names the person who makes medical decisions when "
                                          "you can't speak for yourself. Sometimes called a "
                                          "health care proxy."),
        ("Advance directive or living will", "Puts your wishes for end-of-life care in writing, "
                                             "so your agent isn't guessing."),
    ], size=9.6, row_gap=7)
    f.para("Also worth asking an attorney about: a revocable living trust (can keep some assets "
           "out of probate), transfer-on-death deeds and accounts where your state allows them, "
           "and a letter or list for personal items that your will can refer to.", size=9.4,
           gray=0.2, after=8)
    f.fields([
        [("Attorney who prepared my documents", 1), ("Firm and phone", 1)],
        [("Last time my will was updated", 1), ("Anything I still need to do", 1)],
    ], h=28, gap=4)
    f.subhead("Notes for my executor", size=11.5)
    f.para("Practical notes only: where things are, who to call, what's unfinished. Who gets "
           "what belongs in your will, not here.", size=9.2, gray=0.3)
    f.lines(fill=True)


def p12_money_glance(c, n):
    f = P.Flow(c, n)
    f.title("MONEY", "Money at a glance",
            "Someone stepping in should be able to read this page and know how money comes in, "
            "where it sits, and how bills get paid.")
    f.note("While you're alive, only your agent under a financial power of attorney (or a joint "
           "owner, for a joint account) should use your accounts. Once you die, that power ends, "
           "and your executor takes over after the court appoints them. Family should not keep "
           "using your cards or accounts during that gap. Mortgage, insurance and utility bills "
           "still need paying, so the executor should ask the estate attorney how to keep them "
           "current.", at_bottom=True)
    f.fields([
        [("Main bank I use", 1), ("How most bills get paid (autopay, online, checks)", 1)],
        [("Where statements go (paper, which email)", 1), ("Who helps me with money", 1)],
    ], h=27, gap=4)
    f.subhead("Money coming in", size=11.5)
    f.table(["Source", "Paid into (bank, last 4)", "About how much", "How often", "Who to call"],
            [2.2, 2, 1.3, 1.1, 1.8], nrows=5, row_h=21)
    f.para("Think about Social Security, a pension, a paycheck, rental income, an annuity, "
           "alimony, or a business.", size=9.0, gray=0.3, after=6)
    f.subhead("If I can't manage my money for a while", size=11.5)
    f.checklist([
        "My financial power of attorney is named on the Key Contacts page, and they know where this binder is.",
        "These bills must keep getting paid no matter what: mortgage or rent, insurance, utilities, car loan.",
        "My bank already has a copy of my power of attorney on file. (Banks can take days to approve one.)",
    ], size=9.2, row_gap=4)
    f.small_caps_head("Bills and deadlines that can't slip")
    f.lines(fill=True, min_n=2)


def p13_bank(c, n):
    f = P.Flow(c, n)
    f.title("MONEY", "Bank accounts",
            "Checking, savings, money market, CDs and credit union accounts. Last 4 digits only.")
    f.note("Joint accounts usually go straight to the surviving owner. Payable-on-death (POD) "
           "accounts go to the person named with the bank. Neither follows your will. That's "
           "often helpful, since it skips probate, but it can also undo a plan by accident. If "
           "your will splits things evenly among your children and one child is the joint owner "
           "on your main account, that account may go to that child alone.", at_bottom=True)
    f.table(["Bank or credit union", "Type", "Last 4", "Owner: me, joint (with whom)", "POD beneficiary"],
            [2.4, 1.2, 0.9, 2.4, 2.0], fill=True, row_h=26, reserve=118)
    f.fields([[("Where my online logins are kept", 1), ("Branch or banker I deal with", 1)]], h=28, gap=4)
    f.subhead("Cash, checks and cards", size=11.5)
    f.fields([[("Where my checkbook is", 1), ("Cash at home and where", 1), ("Debit and credit cards: where", 1)]],
             h=28, gap=4)


def p14_retirement(c, n):
    f = P.Flow(c, n)
    f.title("MONEY", "Retirement and investments",
            "401(k), 403(b), IRA, Roth, brokerage, HSA, 529 and annuities. Include old accounts "
            "from past jobs.")
    f.note("Your beneficiary form beats your will. Retirement accounts, life insurance, "
           "annuities and HSAs go to whoever is named on the company's beneficiary form, even "
           "if your will says something different. One exception: in most workplace plans like "
           "a 401(k) or 403(b), federal law makes your spouse the beneficiary unless they signed "
           "a written waiver, so check the plan's form after a marriage or divorce. The most "
           "common mistakes: an ex-spouse still listed, no backup (contingent) beneficiary, a "
           "minor child named directly, and \"my estate\" listed, which can pull the account "
           "into probate. The next page is a quick check-up.", at_bottom=True)
    f.table(["Company", "Account type", "Last 4", "Beneficiary on file", "Last checked"],
            [2.4, 1.6, 0.9, 2.4, 1.3], fill=True, row_h=26, reserve=150)
    f.fields([[("Financial advisor and phone", 1), ("Where statements and logins are", 1)]], h=28, gap=4)
    f.subhead("Stock options, RSUs, deferred pay or a pension", size=11.5)
    f.lines(fill=True, min_n=2)


def p15_beneficiary(c, n):
    f = P.Flow(c, n)
    f.title("MONEY", "Beneficiary check-up",
            "Log in to each account or call, and confirm who's named. It takes about an hour, "
            "and it can prevent the most expensive mistakes.")
    f.table(["Account", "Primary", "Backup (contingent)", "Confirmed on", "OK"],
            [2.7, 2.2, 2.2, 1.3, 0.6],
            labels=["Life insurance (my own policy)", "Life insurance through work", "401(k) or 403(b)",
                    "Old 401(k) from a past job", "IRA or Roth IRA", "HSA", "Annuity",
                    "Pension survivor option", "Bank accounts (POD)", "Brokerage account (TOD)",
                    "Home (transfer-on-death deed, where allowed)", "Vehicle (TOD title, where allowed)"],
            row_h=26, checks=(4,))
    f.subhead("Check for these", size=11.5)
    f.checklist([
        "No ex-spouse is still named anywhere, unless that's on purpose.",
        "Every account has a backup beneficiary, not just a primary.",
        "No minor child is named directly. Ask the company or an attorney about a custodian or a trust.",
        "Someone who gets needs-based benefits, like SSI or Medicaid, isn't named directly in a way that could affect them.",
        "The names on these forms match what my will says I want.",
    ], size=9.4, row_gap=5)


def p16_insurance(c, n):
    f = P.Flow(c, n)
    f.title("MONEY", "Insurance",
            "Every policy, including the ones that come with a job, a credit card or a "
            "membership. Families often miss these.")
    f.note("If a home will sit empty after a death, tell the homeowners insurer right away. "
           "Many policies limit coverage on a vacant home, and a burst pipe in an empty house "
           "is expensive.", at_bottom=True)
    f.note("Life insurance through work is often worth one or two times salary, and people "
           "forget they have it. Some credit cards and travel bookings include accidental death "
           "coverage too. Ask your HR team for a benefits summary and keep it with this binder.",
           at_bottom=True)
    types = ["Life insurance", "Life insurance through work", "Accidental death (AD&D)", "Health",
             "Medicare supplement or Advantage", "Long-term care", "Disability",
             "Homeowners or renters", "Auto", "Umbrella", "Pet", "Other"]
    avail = f.y - f.floor - 15
    row_h = min(34, avail / len(types))
    f.table(["Type", "Company", "Policy # (last 4) and where", "Agent or phone", "Beneficiary or notes"],
            [2.0, 1.8, 2.0, 1.6, 2.0], labels=types, row_h=row_h)


def p17_debts(c, n):
    f = P.Flow(c, n)
    f.title("MONEY", "Debts and credit cards",
            "What's owed, so your executor can pay what's real and spot anything that isn't.")
    f.note("In general, family members don't inherit your debts. Your estate pays valid debts "
           "before anything is passed on. The exceptions are people who co-signed or own the "
           "account jointly, and spouses in some states. Federal student loans are discharged "
           "when the borrower dies, once the servicer gets a death certificate. Your family "
           "should never pay a debt out of their own pocket before talking to the executor.",
           at_bottom=True)
    f.table(["Debt", "Lender", "Last 4", "Paid from (autopay?)", "Co-signer or joint?", "Notes"],
            [1.7, 1.7, 0.8, 1.7, 1.5, 1.6],
            labels=["Mortgage", "Home equity loan or HELOC", "Car loan", "Student loans",
                    "Personal loan", "Credit card", "Credit card", "Credit card", "Credit card",
                    "Medical bills", "Other"], row_h=23)
    f.subhead("Money owed to me", size=11.5)
    f.table(["Who owes it", "About how much", "Paperwork or terms"], [2.5, 1.5, 3], fill=True,
            row_h=22, min_rows=2)


def p18_bills(c, n):
    f = P.Flow(c, n)
    f.title("MONEY", "Bills, autopays and subscriptions",
            "Autopays keep running after a death, and some of them shouldn't. Mark what to keep "
            "and what to cancel.")
    f.note("Ideas: phone, streaming, software, gym, memberships, newspapers, meal kits, cloud "
           "storage, donations, charities, app subscriptions billed through Apple or Google.",
           title="IDEAS", at_bottom=True)
    f.table(["Bill or subscription", "Paid from (card or bank, last 4)", "About how much",
             "Autopay", "Keep", "Cancel", "Notes"],
            [2.4, 2.0, 1.2, 0.7, 0.6, 0.7, 1.6], fill=True, row_h=23, checks=(3, 4, 5))


def p19_taxes(c, n):
    f = P.Flow(c, n)
    f.title("MONEY", "Taxes, business and rentals",
            "The things that keep running on a schedule, even when nobody's watching.")
    f.note("Short-term rentals keep taking bookings on their own. If you host, write down who "
           "can message guests, change door codes and pause the calendar. Upcoming guests and "
           "cleaners will need someone quickly.", at_bottom=True)
    f.fields([
        [("Tax preparer and phone", 1), ("Where past returns are kept", 1)],
        [("Do I pay estimated taxes?", 1), ("State(s) I file in", 1), ("Tax software login kept where", 1)],
    ], h=27, gap=4)
    f.subhead("Businesses I own or am part of", size=11.5)
    f.table(["Business", "My role and share", "Partners or key person", "Agreement kept where"],
            [2, 1.8, 2, 2], nrows=3, row_h=23)
    f.small_caps_head("Who should keep it running, wind it down, or be called first")
    f.lines(3)
    f.subhead("Rental property", size=11.5)
    f.table(["Property", "Long or short-term", "Manager or co-host", "Booking sites and logins"],
            [2.2, 1.4, 2, 2.2], fill=True, row_h=23, min_rows=2)


def p20_easy_to_miss(c, n):
    f = P.Flow(c, n)
    f.title("MONEY", "Money that's easy to miss",
            "Check each one you have, and say where to find it. These are the accounts families "
            "most often find months later, or never.")
    f.note("Every state keeps a list of unclaimed money. Your family can search most states at "
           "once at missingmoney.com, and find every state's official site at unclaimed.org. A "
           "surviving spouse or child may also qualify for a one-time $255 Social Security death "
           "payment and monthly survivor benefits. They should ask Social Security directly. "
           "(Social Security Administration, ssa.gov, checked " + AS_OF + ".)", at_bottom=True)
    items = [
        "Old 401(k)s and pensions from past jobs", "PayPal, Venmo or Cash App balances",
        "Health savings account (HSA)", "Airline miles, hotel points, credit card rewards",
        "Life insurance through work or a union", "Gift cards and store credit",
        "Accidental death coverage on credit cards", "Security deposits (rent, utilities)",
        "U.S. savings bonds (paper or TreasuryDirect)", "Money people owe me",
        "Annuities", "Refunds, rebates or a pending tax refund",
        "Stock options, RSUs or deferred pay", "Safe deposit box",
        "Cryptocurrency (where the wallet and recovery info are)", "Benefits from a club, union or fraternal group",
    ]
    # two columns, each item followed by a writing line
    colw = (f.W - 18) / 2
    rows = len(items) // 2
    y0 = f.y
    row_gap = 40
    for i, it in enumerate(items):
        col = i % 2
        r = i // 2
        x = f.L + col * (colw + 18)
        y = y0 - r * row_gap
        P.checkbox(c, x, y - 9, 8.5)
        lines = P.wrap(it, "Body", 9.3, colw - 16)
        c.setFont("Body", 9.3)
        c.setFillGray(0.1)
        c.drawString(x + 14, y - 8, lines[0])
        if len(lines) > 1:
            c.drawString(x + 14, y - 19, lines[1])
        P.rule(c, x + 14, x + colw, y - 31)
    f.y = y0 - rows * row_gap - 4
    f.small_caps_head("Anything else only I know about")
    f.lines(fill=True, min_n=1)


def p21_home(c, n):
    f = P.Flow(c, n)
    f.title("HOME AND PROPERTY", "My home",
            "Enough for someone else to walk in, keep it safe, and keep the bills paid.")
    f.fields([
        [("Address", 2), ("Own or rent", 1)],
        [("Mortgage company or landlord", 1), ("HOA or property manager", 1)],
        [("Property taxes paid how", 1), ("Deed is kept where", 1), ("Homeowners insurer", 1)],
    ], h=26, gap=4)
    f.subhead("Getting in and keeping it safe", size=11.5)
    f.fields([
        [("Spare keys are with", 1), ("Alarm company and phone", 1)],
        [("Where alarm, gate and garage codes are kept", 1.3), ("Wi-Fi network", 0.7)],
    ], h=26, gap=4)
    f.subhead("Shutoffs and systems", size=11.5)
    f.fields([
        [("Water main shutoff", 1), ("Gas shutoff", 1), ("Electrical panel", 1)],
        [("Furnace or boiler", 1), ("Water heater", 1), ("Sump pump or well", 1)],
        [("Trash and recycling days", 1), ("Things that need regular care (pool, plants, filters)", 1.6)],
    ], h=26, gap=4)
    f.subhead("If the home will be empty", size=11.5)
    f.checklist([
        "Tell the homeowners insurer, and ask what the policy needs while the home is empty.",
        "Hold or forward the mail, and stop deliveries.",
        "Keep the heat on in winter and have someone check in weekly.",
        "Keep valuables, documents and spare keys locked away.",
    ], cols=2, size=9.0, row_gap=4)
    f.small_caps_head("Notes for whoever looks after the house")
    f.lines(fill=True, min_n=1)


def p22_utilities(c, n):
    f = P.Flow(c, n)
    f.title("HOME AND PROPERTY", "Utilities and home services",
            "Who to call, and how each one is paid. Account numbers: last 4 only.")
    services = ["Electric", "Gas or propane", "Water and sewer", "Trash", "Internet", "Home phone",
                "Cell phone", "Alarm or security", "Lawn or snow", "Cleaning", "Heating and cooling service",
                "Plumber", "Electrician", "Handyman", "Pest control", "Other", "Other"]
    avail = f.y - f.floor - 12
    row_h = min(34, avail / len(services))
    f.table(["Service", "Company", "Acct last 4", "Paid how", "Phone"], [2.0, 2.4, 1.1, 1.5, 1.8],
            labels=services, row_h=row_h)


def p23_vehicles(c, n):
    f = P.Flow(c, n)
    f.title("HOME AND PROPERTY", "Vehicles, property and valuables",
            "Anything with a title, a key, or a story.")
    f.note("This list tells your family what you'd like. It may not be binding on its own. Many "
           "states let a will refer to a separate list of personal items, so ask your attorney "
           "how to make this list count.", at_bottom=True)
    f.subhead("Vehicles", size=11.5)
    f.table(["Year, make, model", "Title is where", "Loan with", "Spare key", "Insurer"],
            [2.4, 1.8, 1.6, 1.4, 1.6], nrows=3, row_h=23)
    f.subhead("Other property", size=11.5)
    f.para("Storage units, land, a cabin, a boat, a timeshare, a cemetery plot, firearms (and "
           "where they're secured).", size=9.0, gray=0.3, after=5)
    f.table(["What", "Where", "Paperwork, keys or access"], [2.4, 2.4, 3], nrows=4, row_h=23)
    f.subhead("Valuables and things that matter", size=11.5)
    f.table(["Item", "Where it is", "Who I'd like to have it", "The story, if there is one"],
            [2, 1.8, 2, 2.6], fill=True, row_h=23, min_rows=3)


def p24_devices(c, n):
    f = P.Flow(c, n)
    f.title("DIGITAL LIFE", "Getting into my devices",
            "Most of life now sits behind a passcode. Without a way in, a family can lose "
            "photos, bills and accounts for good.")
    f.note("Keep the phone line active for a few months after a death. Many accounts send "
           "sign-in codes by text, and losing the number can lock your family out of "
           "everything else.", at_bottom=True)
    f.note("Use a password manager and turn on its emergency access feature, then write down "
           "which one you use and who your emergency contact is. If you don't use one, keep a "
           "sealed envelope with your phone passcode and main passwords somewhere secure, and "
           "write down where it is.", title="DON'T WRITE PASSWORDS HERE")
    f.fields([
        [("Password manager I use", 1), ("Emergency access set up for", 1)],
        [("Where my master password or recovery kit is", 1.4), ("Who knows", 0.8)],
    ], h=27, gap=4)
    f.subhead("Phone and computers", size=11.5)
    f.table(["Device", "Passcode is kept where", "Backed up to", "Notes"], [1.8, 2.2, 1.8, 2.2],
            fill=True, row_h=24, reserve=150, min_rows=3)
    f.subhead("Legacy settings", size=11.5)
    f.checklist([
        "Apple Legacy Contact set up (Settings, your name, Sign-In and Security).",
        "Google Inactive Account Manager set up (in your Google Account, under Data and privacy).",
        "Facebook legacy contact chosen, or I've asked for my account to be deleted.",
        "Backup codes for two-step sign-in are printed and stored with this binder's secure copy.",
    ], size=9.2, row_gap=4)
    f.fields([[("Phone number used for sign-in codes", 1), ("Carrier and who should keep the number active", 1.2)]],
             h=27, gap=2)


def p25_email(c, n):
    f = P.Flow(c, n)
    f.title("DIGITAL LIFE", "Email, accounts and wishes",
            "Usernames and what you'd like done. Not passwords.")
    f.subhead("Email accounts", size=11.5)
    f.table(["Email address", "Used for", "Recovery phone or email"], [2.6, 2.2, 2.4], nrows=3, row_h=23)
    f.subhead("Online accounts", size=11.5)
    f.table(["Service", "Username or email", "Keep", "Close", "Memorialize", "Notes (download photos first, etc.)"],
            [1.8, 2.2, 0.6, 0.6, 0.9, 2.4], fill=True, row_h=23, checks=(2, 3, 4), reserve=72)
    f.fields([
        [("Where my photos and videos are stored", 1), ("Who should get copies", 1)],
        [("Websites, domains or online shops I own", 1), ("Renewal dates and where they're paid from", 1)],
    ], h=27, gap=4)


def p26_children(c, n):
    f = P.Flow(c, n)
    f.title("PEOPLE AND PETS WHO COUNT ON ME", "Children and dependents",
            "What a guardian or caregiver would need on the first day. Your will is where a "
            "guardian is legally named. This page is the everyday part.")
    f.note("If you care for an adult, like a parent or a family member with a disability, use "
           "this page for them too. Write down their doctors, benefits, and the people who "
           "help, so care doesn't stop if you can't be there.", at_bottom=True)
    f.fields([[("Guardian named in my will", 1), ("Backup guardian", 1)]], h=27, gap=4)
    for k in (1, 2):
        f.subhead(f"Child or dependent {k}", size=11.5)
        f.fields([
            [("Name", 1.4), ("Date of birth", 0.8), ("School or program", 1.2)],
            [("Doctor and phone", 1), ("Allergies and medications", 1)],
            [("People they trust", 1), ("Activities and schedule", 1)],
            [("Routines, comfort and what helps on a hard day", 1)],
        ], h=31, gap=4)
    f.small_caps_head("Notes")
    f.lines(fill=True, min_n=1)


def p27_pets(c, n):
    f = P.Flow(c, n)
    f.title("PEOPLE AND PETS WHO COUNT ON ME", "Pets",
            "Pets can't tell anyone what they need. These two cards make sure someone knows.")
    f.note("Ask your caregiver first, and consider leaving money for the pet's care. Every state "
           "allows a pet trust, and your attorney can tell you whether it makes sense for you.",
           at_bottom=True)
    for k in (1, 2):
        f.subhead(f"Pet {k}", size=11.5)
        f.fields([
            [("Name", 1), ("Kind and breed", 1.2), ("Age", 0.5), ("Microchip company and #", 1.2)],
            [("Vet and phone", 1), ("Medications", 1), ("Pet insurance", 1)],
            [("Food, amount and when", 1), ("Walks, habits, fears", 1)],
            [("Who should care for them", 1), ("Backup", 0.8), ("Supplies and records are where", 1)],
            [("Groomer, sitter or daycare", 1), ("Where they go if no one can take them", 1)],
        ], h=25, gap=3)
    f.small_caps_head("Anything else they'd want you to know")
    f.lines(fill=True, min_n=1)


def p28_final_wishes(c, n):
    f = P.Flow(c, n)
    f.title("FINAL WISHES", "Final wishes",
            "Your family will want to get this right. Telling them what you want is a gift, even "
            "if your answer is \"whatever is easiest for you.\"")
    f.note("Wishes written here aren't legally binding in most places, and in some states the "
           "right to decide belongs to a person you name in a separate form. Ask your attorney "
           "or funeral home what your state uses. A pre-paid plan helps, but read what it "
           "covers: many cover the funeral home's services but not the cemetery.", at_bottom=True)
    f.option_row("I'd like", ["Burial", "Cremation", "Green burial", "Body donation", "Let my family decide"], h=28)
    f.fields([
        [("Funeral home I'd prefer", 1), ("Pre-paid plan or contract and where", 1)],
        [("Cemetery or where my ashes go", 1), ("Plot or deed details", 1)],
    ], h=26, gap=4)
    f.option_row("For a gathering", ["Funeral", "Memorial service", "Celebration of life",
                                     "Private family only", "Nothing formal"], h=28)
    f.fields([
        [("Where", 1), ("Who should lead it", 1), ("Religious or not", 1)],
        [("Music, readings or poems", 1), ("People I'd like to speak", 1)],
        [("Flowers, or donations instead to", 1), ("What people should wear", 1)],
    ], h=26, gap=4)
    f.small_caps_head("Anything else: what I'd love, and what I'd rather skip")
    f.lines(fill=True, min_n=1)


def p29_obituary(c, n):
    f = P.Flow(c, n)
    f.title("FINAL WISHES", "For my obituary",
            "The facts people scramble to find. Write as much or as little as you like.")
    f.note("Leave the exact home address out of the obituary and social posts, and have someone "
           "stay at the house during the service. Empty homes during funerals are a known "
           "target for break-ins.", at_bottom=True)
    f.fields([
        [("Full name as I'd like it written", 1.4), ("Nickname", 0.8), ("Photo to use: where", 1)],
        [("Born (date and place)", 1), ("Grew up in", 1)],
        [("Schools", 1), ("Work and career", 1)],
    ], h=27, gap=4)
    f.small_caps_head("Family to name (survived by, and preceded by)")
    f.lines(4)
    f.small_caps_head("What I'd want people to know about my life")
    f.lines(fill=True, reserve=42, min_n=3)
    f.fields([[("Where it should appear (paper, website)", 1), ("Who should write it", 1)]], h=27, gap=0)


def p30_people_to_tell(c, n):
    f = P.Flow(c, n)
    f.title("FINAL WISHES", "People to tell",
            "Friends, colleagues and groups who should hear the news. Your family can tick each "
            "one off.")
    f.table(["Name or group", "How they know me", "Phone or email", "Told"], [2.6, 2.2, 2.6, 0.6],
            fill=True, row_h=24, checks=(3,))


def p31_words(c, n):
    f = P.Flow(c, n)
    f.title("IN MY OWN WORDS", "A few words from me",
            "Not instructions. Just what you'd want them to hear. Write to one person or to "
            "everyone.")
    f.fields([[("To", 2), ("Date", 1)]], h=27, gap=6)
    f.lines(fill=True, gap=22)


def p32_more_words(c, n):
    f = P.Flow(c, n)
    f.title("IN MY OWN WORDS", "A few more words")
    f.fields([[("To", 2), ("Date", 1)]], h=27, gap=6)
    f.lines(fill=True, gap=22)


def p33_hospital(c, n):
    f = P.Flow(c, n)
    f.title("FOR MY FAMILY", "If I'm in the hospital",
            "Or can't speak for myself for a while. You're not deciding everything at once. "
            "Start at the top.")
    f.subhead("Right away", size=11.5)
    f.checklist([
        "Call my health care agent (Key Contacts page). They make medical decisions if I can't.",
        "Bring copies of my advance directive and health care power of attorney, my medication list, and my insurance cards. The Health pages say where they are.",
        "Tell the care team about allergies and medications (Medical Information page).",
        "Make sure someone is looking after children, pets and the house (Kids and Pets pages).",
        "Ask for the hospital social worker or case manager. They help with insurance, discharge planning and next steps.",
    ], size=9.3, row_gap=4)
    f.subhead("In the first week", size=11.5)
    f.checklist([
        "The agent named in my financial power of attorney takes over the bills. Nobody else should use my cards or accounts.",
        "Keep paying what can't slip: mortgage or rent, insurance, utilities, car loan (Money at a Glance).",
        "Tell my employer, and ask HR about sick leave, short-term disability and FMLA paperwork.",
        "Hold the mail, stop deliveries, and check the house every few days.",
        "Keep a notebook: doctors' names, what they said, questions, dates. It helps more than you'd think.",
    ], size=9.3, row_gap=4)
    f.subhead("If it goes on for a while", size=11.5)
    f.checklist([
        "Look at disability and long-term care insurance (Insurance page). Claims often have waiting periods, so start early.",
        "Check which autopays to pause or cancel (Bills page).",
        "Ask the care team whether palliative care or hospice could help. Neither means giving up. Both focus on comfort.",
    ], size=9.3, row_gap=4)
    f.subhead("Who's doing what", size=11.5)
    f.table(["Job", "Who", "Phone"], [3, 2.6, 2], fill=True, row_h=22, min_rows=2)


def p34_first_72(c, n):
    f = P.Flow(c, n)
    f.title("FOR MY FAMILY", "After I die: the first 72 hours",
            "Most things can wait. These can't. You don't need to know how probate works yet.")
    f.note("Keep a running list of every call you make: the date, who you spoke with, and what "
           "happens next. The Calls and Claims Log on page 37 is there for exactly that.",
           at_bottom=True)
    f.checklist([
        ("Get a legal pronouncement of death.", "If I die at home under hospice care, call the hospice nurse, not 911. If it's unexpected, call 911."),
        ("If I wanted to be a donor,", "tell the hospital or hospice right away (Medical Information page). The window is short."),
        ("Call the funeral home", "(Final Wishes page). They'll transport me and guide you through the next steps."),
        ("Tell close family and my executor", "(Start Here and Key Contacts pages)."),
        ("Secure the house, car and pets.", "Lock up, take valuables and spare keys somewhere safe, and make sure pets are fed."),
        ("Find the will and my final wishes.", "Don't hand out belongings or money yet, even things I promised. The executor does that later."),
        ("Order death certificates through the funeral home.", "Get more than you think you'll need. Banks, insurers and others each want a certified copy, and 6 to 10 is common."),
        ("Ask the funeral home to report the death to Social Security.", "They usually do. Don't spend Social Security payments that arrive after the death. The payment for the month of death, and any after it, has to be returned (Social Security Administration, ssa.gov, checked " + AS_OF + ")."),
        ("Tell my employer if I was working,", "and ask about final pay, life insurance and benefits."),
        ("Rest. Eat something. Let people help.", "Give them specific jobs: meals, calls, picking people up from the airport."),
    ], size=9.5, row_gap=5)
    f.subhead("Who's doing what", size=11.5)
    f.table(["Job", "Who's handling it", "Phone", "Done"], [2.6, 2.6, 1.8, 0.6],
            labels=["Calling family and close friends", "Funeral home and arrangements",
                    "Food, visitors and messages", "House, mail and pets", "Travel and airport pickups",
                    "Paperwork and death certificates", "", "", ""],
            row_h=min(30, (f.y - f.floor - 20) / 9), checks=(3,))


def p35_first_month(c, n):
    f = P.Flow(c, n)
    f.title("FOR MY FAMILY", "The first month",
            "Mostly my executor's job. If you're the executor, you don't have to do it alone. "
            "An estate attorney can walk you through your state's process.")
    f.note("Keep the house insured, the heat on, and the essential bills paid. Close accounts "
           "slowly. An account that looks unneeded can be the one a pension or refund gets "
           "paid into.", at_bottom=True)
    f.subhead("Legal and paperwork", size=11.5)
    f.checklist([
        "Meet with an estate attorney and bring the will, death certificates and this binder.",
        "File the original will with the probate court. Many states require this within a set time, even if there's no probate.",
        "Get an EIN for the estate from the IRS and open an estate bank account, if the attorney says you need one (IRS Publication 559, irs.gov, checked " + AS_OF + ").",
        "Keep every receipt for funeral costs and estate bills. They're often repaid from the estate.",
    ], size=9.2, row_gap=4)
    f.subhead("Tell these organizations", size=11.5)
    f.checklist([
        "Social Security, Medicare and any pension (if the funeral home didn't)",
        "Banks and credit unions (Bank Accounts page)",
        "Life insurance companies, to start claims",
        "Retirement account and investment companies",
        "Credit card companies and lenders (Debts page)",
        "Equifax, Experian and TransUnion: ask for a deceased flag",
        "Health, car and home insurers",
        "The DMV, voter registration and passport office",
        "Utilities and services (Home pages)",
        "Post office: forward the mail to the executor",
        "Veterans Affairs, if I served",
        "Clubs, unions and alumni groups (People to Tell page)",
    ], cols=2, size=9.0, row_gap=4)
    f.subhead("Protect against fraud", size=11.5)
    f.checklist([
        "Ask the credit bureaus to flag my credit file, and watch for new accounts.",
        "Cancel my cards (after checking whether any autopays need moving), and don't share details of my death widely online.",
    ], size=9.2, row_gap=4)
    f.small_caps_head("Notes")
    f.lines(fill=True, min_n=1)


def p36_first_year(c, n):
    f = P.Flow(c, n)
    f.title("FOR MY FAMILY", "The first year",
            "Settling an estate usually takes months, sometimes longer. This is the usual order, "
            "as general information, not legal or tax advice (Terms of Use, page 41). Your "
            "attorney will tell you what applies in your state.")
    f.note("Many inherited investments and homes get a new tax cost basis equal to their value "
           "on the date of death. That can sharply lower capital gains tax if they're sold "
           "later, but only if someone records those values. Ask the tax preparer before "
           "selling anything. (IRS, gifts and inheritances FAQ, irs.gov, checked " + AS_OF + ".)",
           at_bottom=True)
    steps = [
        ("List everything", "Use the Money and Home sections to make an inventory of what I owned and what I owed. Get values as of the date of death: statements for accounts, and an appraisal for real estate and valuable items."),
        ("Collect what's owed", "File life insurance claims, roll over or claim retirement accounts, collect final pay, refunds and deposits, and check the Money That's Easy to Miss page."),
        ("Pay valid debts and bills", "From the estate, not your own pocket. The attorney will tell you the order and the deadlines for creditors."),
        ("File the taxes", "My final income tax return is due by the usual April deadline the year after I die. If the estate earns income while it's open, it may need its own return (Form 1041). A tax preparer is worth it here. (IRS Publication 559 and Form 1041 instructions, irs.gov, checked " + AS_OF + ".)"),
        ("Transfer and distribute", "Retitle the house and cars, transfer accounts, and give belongings and money as the will says. Get signed receipts from each person."),
        ("Close the estate", "File the final accounting if the court requires it, close the estate account, and keep the records for several years."),
    ]
    size, leading = 9.3, 11.8
    for i, (lead, body) in enumerate(steps):
        h = (1 + len(P.wrap(body, "Body", size, f.W - 26))) * leading
        f.need(h + 5, "step")
        c.setFillGray(0.15)
        c.circle(f.L + 7, f.y - 7, 7, stroke=0, fill=1)
        c.setFillGray(1)
        c.setFont("Head", 8.5)
        c.drawCentredString(f.L + 7, f.y - 10, str(i + 1))
        c.setFillGray(0)
        c.setFont("Head", 10)
        c.drawString(f.L + 24, f.y - 10.5, lead)
        y = P.draw_wrapped(c, body, f.L + 24, f.y - 10.5 - leading, f.W - 26, "Body",
                           size, leading, 0.12)
        f.y = y + leading - 9
    f.subhead("Estate details", size=11.5)
    f.fields([
        [("Probate court and case number", 1), ("Estate attorney and phone", 1)],
        [("Estate EIN is kept where", 1), ("Estate bank account", 1)],
    ], h=26, gap=3)
    f.small_caps_head("Notes")
    f.lines(fill=True, min_n=1)


def p37_calls_log(c, n):
    f = P.Flow(c, n)
    f.title("FOR MY FAMILY", "Calls and claims log",
            "Every call, form and claim in one place. When someone asks \"did we tell the "
            "bank?\", the answer is here.")
    f.table(["Date", "Organization", "Spoke with", "Reference or claim #", "Next step", "Done"],
            [1.0, 2.0, 1.6, 1.7, 2.2, 0.6], fill=True, row_h=24, checks=(5,))


def p38_once_a_year(c, n):
    f = P.Flow(c, n)
    f.title("KEEPING IT CURRENT", "Once a year",
            "Twenty minutes, once a year. Pick a date you'll remember and put it on your "
            "calendar now.")
    f.fields([[("My yearly review date", 1), ("Calendar reminder set", 1), ("Copies of this binder are with", 1.3)]],
             h=27, gap=4)
    f.subhead("The yearly check", size=11.5)
    f.checklist([
        "Contacts are current: phone numbers, my executor, my agents, my doctors.",
        "Medications and doctors are up to date.",
        "Beneficiaries still match my wishes (Beneficiary Check-up page).",
        "New or closed accounts are added or crossed off.",
        "Insurance policies and agents are current.",
        "Password manager emergency access still points to the right person.",
        "Final wishes and guardian choices still feel right.",
        "Any copies match this book, and the two people who know where it is still know.",
    ], size=9.3, row_gap=4)
    f.subhead("Also update after", size=11.5)
    f.para("A marriage or divorce, a birth or adoption, a death in the family, a move, a new job "
           "or retirement, buying or selling a home, a new diagnosis, or opening or closing a "
           "major account.", size=9.3, gray=0.2, after=6)
    f.subhead("Update log", size=11.5)
    f.table(["Date", "What changed", "Copies updated"], [1.2, 5, 1.4], fill=True, row_h=23,
            checks=(2,))


def p39_wallet(c, n):
    f = P.Flow(c, n)
    f.title("KEEPING IT CURRENT", "Wallet card and door note",
            "Fill in and cut out, or photocopy the page first. One card for your wallet, one "
            "for a partner or your executor. Put the note on the refrigerator door.")
    gap = 16
    cw = (f.W - gap) / 2
    ch = 150
    f.need(ch, "cards")
    top = f.y
    for i in range(2):
        x = f.L + i * (cw + gap)
        c.setStrokeGray(0.45)
        c.setLineWidth(0.6)
        c.setDash(3, 3)
        c.rect(x, top - ch, cw, ch, stroke=1, fill=0)
        c.setDash()
        P.color_bars(c, x + 10, top - 14, w=9, h=2.4, gap=2)
        P.draw_label(c, "IN CASE OF EMERGENCY", x + 10, top - 27, size=7.2, gray=0.1, space=1.2)
        y = top - 42
        for lab in ("Name", "Please call", "Their phone", "My binder is"):
            P.draw_label(c, lab, x + 10, y, size=6.2)
            P.rule(c, x + 10, x + cw - 10, y - 14)
            y -= 24
        c.setFont("BodyI", 8.2)
        c.setFillGray(0.2)
        c.drawString(x + 10, top - ch + 10, "Allergies and medications are listed in my binder.")
    f.y = top - ch - 14
    # door note
    f.subhead("For emergency responders", size=11.5)
    nh = f.y - f.floor - 26
    top = f.y
    c.setStrokeGray(0.45)
    c.setLineWidth(0.6)
    c.setDash(3, 3)
    c.rect(f.L, top - nh, f.W, nh, stroke=1, fill=0)
    c.setDash()
    P.draw_label(c, "INFORMATION FOR EMTS AND FIREFIGHTERS", f.L + 12, top - 16, size=7.2, gray=0.1, space=1.2)
    inner = P.Flow(c, n)
    inner.L, inner.R, inner.W = f.L + 12, f.R - 12, f.W - 24
    inner.y = top - 26
    inner.floor = top - nh + 8
    inner.fields([
        [("Name", 1.6), ("Date of birth", 1)],
        [("Medical conditions", 1)],
        [("Allergies", 1)],
        [("Doctor and phone", 1.6), ("Blood type", 1)],
        [("Medications list is kept", 1), ("Health care agent and phone", 1)],
        [("DNR or POLST: yes or no, and where", 1), ("Emergency contact and phone", 1)],
        [("Pets in the home", 1)],
    ], h=(nh - 44) / 7 - 3, gap=3)
    f.y = top - nh - 8
    c.setFont("BodyI", 8.6)
    c.setFillGray(0.25)
    c.drawString(f.L, f.floor + 4, "Tip: many fire departments ask people to keep this note on the "
                                   "refrigerator, because that's where responders look.")


def p40_kind(c, n):
    f = P.Flow(c, n)
    f.title("KEEPING IT CURRENT", "You did something kind",
            "Most people never get around to this. By filling in even part of this binder, "
            "you've taken a great deal of guesswork off the people you love, in one of the "
            "hardest weeks of their lives.")
    f.para("You don't have to finish it all at once. Come back to a section when you have twenty "
           "minutes. Every page you complete is one less thing someone has to search for.",
           size=10, gray=0.15, after=10)
    f.subhead("Where I'm keeping things", size=11.5)
    f.fields([
        [("This book", 1), ("Copies or digital file", 1)],
        [("People who know where it is", 1), ("Next review date", 1)],
    ], h=28, gap=4)
    f.gap(6)
    f.note("This is an organizer, not a legal document. It is not a will, trust, power of "
           "attorney, health care directive or beneficiary form, and filling it in has no legal "
           "effect. Laws vary by state. Talk to an estate planning attorney about the documents "
           "you need. It will hold sensitive information: store it somewhere secure and share "
           "it only with people you trust. It is general information, not legal, tax, financial, "
           "medical or other professional advice. The full Terms of Use and Disclaimer, and the "
           "sources and as-of date " + AS_OF + " for every rule and figure in this binder, are "
           "on page 41. Read them before you rely on anything here.",
           title="TERMS OF USE AND SOURCES", size=8.8)
    f.para("Made by ProofNotFluff. Written by a finance executive, built for families. "
           + VERSION_LINE + ".", size=9, gray=0.3, after=6)
    # closing line near the bottom
    c.setFont("BodyI", 13)
    c.setFillGray(0.15)
    c.drawCentredString((f.L + f.R) / 2, f.floor + 40, "Thank you for doing this for them.")
    P.color_bars(c, (f.L + f.R) / 2 - 38, f.floor + 22, w=12, h=3, gap=3.5)


SOURCES_TEXT = (
    "Rules and figures in this binder were checked on " + AS_OF + " against: Social Security "
    "Administration, ssa.gov (lump-sum death payment of $255 to an eligible spouse or child, "
    "apply within 2 years; benefits aren't paid for the month of death; funeral homes usually "
    "report deaths); IRS Publication 559 and Form 1041 instructions, irs.gov (final return due "
    "date, estate income tax return, estate EIN, basis of inherited property); Federal Student "
    "Aid, studentaid.gov (federal student loan death discharge); U.S. Department of Veterans "
    "Affairs, va.gov (burial benefits and DD-214); U.S. Department of Labor, EBSA, dol.gov "
    "(spousal rights in workplace retirement plans); NAUPA, unclaimed.org and missingmoney.com "
    "(unclaimed property). State rules vary. Confirm current details with the agency before acting.")

TERMS = [
    ("License.", "Your purchase gives you a personal license to use this book for yourself or one "
                 "business you own. You may write in it and copy its pages for that use. You may "
                 "not resell, share, give away, upload, scan for distribution or redistribute it, in "
                 "original or edited form, or use it to make a competing product."),
    ("Ownership.", "The design, text and formulas belong to ProofNotFluff. Buying the product "
                   "doesn't transfer ownership."),
    ("Information only.", "This product shares general information and tools for planning. It is "
                          "not legal, tax, accounting, financial, employment, medical or other "
                          "professional advice, and it doesn't create a client relationship of any "
                          "kind. Your situation may differ. For decisions that matter, check with a "
                          "qualified professional and the official source."),
    ("Accuracy.", "Rates, rules and figures were checked against the sources named in the product "
                  "on the date above. Laws, prices and platform rules change, and state and local "
                  "rules vary. You're responsible for confirming anything you rely on."),
    ("Estimates.", "Calculations depend on the numbers you enter and simplify real-world "
                   "conditions. They are estimates, not promises of any result, income, savings, "
                   "approval or outcome."),
    ("No warranty.", "The product is provided \"as is\", without warranties of any kind, to the "
                     "extent the law allows."),
    ("Limit of liability.", "To the extent the law allows, ProofNotFluff is not liable for any loss "
                            "or damage from using or relying on this product, and its total "
                            "liability for any claim is limited to the price you paid for it. "
                            "Nothing here limits rights you have under consumer protection laws "
                            "that can't be waived."),
    ("Trademarks.", "Apple, Google, Facebook, PayPal, Venmo, Cash App, Equifax, Experian, "
                    "TransUnion, TreasuryDirect, Amazon, Etsy and other company and product names "
                    "are trademarks of their owners. ProofNotFluff isn't affiliated with, sponsored "
                    "or endorsed by them."),
    ("AI assistance.", "This product was made with AI assistance and reviewed and tested by the "
                       "shop owner."),
    ("Help.", "If this book arrives damaged or misprinted, ask the store you bought it from for a "
              "replacement. If something in the text looks wrong, the correction goes into the next "
              "printing, and the edition line below tells you which printing you have."),
]


def p41_terms(c, n):
    f = P.Flow(c, n)
    f.title("KEEPING IT CURRENT", "Sources and Terms of Use",
            "Please read this before you rely on anything in the binder.")
    f.note(SHORT_NOTICE + "\n" + ESTATE_CLAUSE, title="NOTICE", size=9.0)
    f.small_caps_head("Sources and as-of date")
    f.para(SOURCES_TEXT, size=9.4, gray=0.1, after=8)
    f.small_caps_head("Terms of Use and Disclaimer")
    f.para("ProofNotFluff | Everything They'll Need: Emergency and End-of-Life Binder, paperback "
           "edition | Version 1.1, " + AS_OF, size=9.4, font="BodyB", gray=0.1, after=6)
    size, leading = 9.4, 11.8
    for lead, body in TERMS:
        nlines = f.measure_lead(f.W, lead, body, size)
        f.need(nlines * leading + 3, "terms")
        f.y -= size
        f.lead_text(f.L, f.y, f.W, lead, body, size, leading, 0.1)
        f.y -= (nlines - 1) * leading + 4.5
    f.gap(6)
    f.para("Made by ProofNotFluff. Written by a finance executive, built for families. "
           + VERSION_LINE + ".", size=8.8, gray=0.3)


def p42_review(c, n):
    f = P.Flow(c, n)
    f.title("KEEPING IT CURRENT", "A small favor",
            "If this book helped you get organized, a short review on Amazon helps the next "
            "family find it.")
    f.para("A sentence about what you filled in first, or who you did it for, is enough. Reviews "
           "are read by real people deciding whether to start, and yours might be the nudge. "
           "No incentive is offered for a review, and none should be.", size=10, gray=0.15, after=10)
    f.para("ProofNotFluff makes plain tools for money and family planning, written by a finance "
           "executive. More titles in this series are listed under the ProofNotFluff author "
           "page on Amazon.", size=10, gray=0.15, after=14)
    f.subhead("Notes", size=11.5)
    f.lines(fill=True, gap=22, reserve=40)
    c.setFont("Body", 8.6)
    c.setFillGray(0.35)
    c.drawString(f.L, f.floor + 14, "Everything They'll Need. " + VERSION_LINE + ". ProofNotFluff.")
    P.color_bars(c, f.L, f.floor + 2, w=12, h=3, gap=3.5)


PAGES = [p01_title, p02_how_to_use, p03_contents, p04_start_here, p05_about_me, p06_family,
         p07_key_contacts, p08_medical, p09_health_decisions, p10_documents, p11_documents_needed,
         p12_money_glance, p13_bank, p14_retirement, p15_beneficiary, p16_insurance, p17_debts,
         p18_bills, p19_taxes, p20_easy_to_miss, p21_home, p22_utilities, p23_vehicles, p24_devices,
         p25_email, p26_children, p27_pets, p28_final_wishes, p29_obituary, p30_people_to_tell,
         p31_words, p32_more_words, p33_hospital, p34_first_72, p35_first_month, p36_first_year,
         p37_calls_log, p38_once_a_year, p39_wallet, p40_kind, p41_terms, p42_review]


def build_interior(path):
    P.register_fonts()
    c = P.new_canvas(path, "Everything They'll Need", "Emergency and end-of-life binder, paperback")
    for i, fn in enumerate(PAGES):
        n = i + 1
        fn(c, n)
        if n > 1:
            P.running_head(c, n, section_for(n), BOOK, updated_line=(n >= 4 and n <= 40))
        c.showPage()
    c.save()
    return len(PAGES)


def build_cover(path, pages):
    return P.build_cover(
        path, pages,
        title_lines=["Everything", "They'll Need"],
        subtitle="The family emergency binder: what my family would need to know, all in one "
                 "place. Contacts, documents, money, home, digital life, final wishes, and the "
                 "first year after a death, step by step.",
        kicker="End of life planner and emergency binder",
        back_hook="What my family would need to know, all in one place.",
        back_intro="A 42-page organizer you fill in by hand. Not a will, not a legal document: "
                   "a map of where everything is and who to call, so the people you love "
                   "aren't guessing on the hardest week of their lives.",
        bullets=[
            "Every page your family would reach for: key contacts, medical information, where "
            "the documents are, accounts and beneficiaries, insurance, debts, home, devices, "
            "pets and final wishes.",
            "A beneficiary check-up and the four common mistakes that send money to the wrong "
            "person, in plain words.",
            "Step lists for the first 72 hours, the first month and the first year, plus a calls "
            "and claims log, a yearly review page and a wallet card.",
        ],
        back_close="Rules and figures checked against the agency sources named inside, with the "
                   "as-of date on the page. Information and planning tool only, not legal, tax, "
                   "financial or medical advice.",
        byline="Written by a finance executive",
        spine_text=None,
        panel_items=["Start here and key contacts", "About me and my family", "Health and care decisions",
                     "Where my documents are", "Money, accounts and beneficiaries",
                     "Insurance, debts and bills", "Home, utilities and vehicles", "Digital life",
                     "Children, dependents and pets", "Final wishes and obituary", "A letter in my own words",
                     "For my family: the first 72 hours, the first month, the first year", "Keeping it current"],
    )


if __name__ == "__main__":
    interior = os.path.join(HERE, "interior.pdf")
    cover = os.path.join(HERE, "cover.pdf")
    pages = build_interior(interior)
    assert pages == PAGES_EXPECTED, (pages, PAGES_EXPECTED)
    geo = build_cover(cover, pages)
    print(f"interior: {pages} pages -> {interior}")
    print(f"cover: spine {geo['spine_in']} in, spread {geo['width_in']} x {geo['height_in']} in -> {cover}")
