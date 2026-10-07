#!/usr/bin/env python3
"""Updates the v2 forms PDFs (from the live #14 zip, scoreboard asset f1d35d30) for the v3 workbook.
Usage: python3 patch_forms.py <v2 Cleaning-Business-Forms-Letter.pdf or -A4.pdf> <out.pdf>
Plain text replacements in the content streams; fillable fields are kept.
Gate round 2 (Oct 7) low item still open: the A4 page 1 kit list keeps the old tab order and
pdftotext shows the "This PDF, 10 pages" line twice; rebuild that page cleanly if possible."""
import sys, pypdf
from pypdf.generic import NameObject, DecodedStreamObject
REP = [(b'tab 7 Job Log', b'tab 6 Job Log'),
       (b'business info, your numbers, cleaning rates, quote builder, price sheet,', b'your numbers and business info, cleaning rates, price sheet, quote builder,'),
       (b'business info, your numbers, cleaning rates, quote builder, price)', b'your numbers and business info, cleaning rates, quote builder, price)'),
       (b'client list, job log, money by month', b'client list, job log with money by month'),
       (b'This PDF, 9 pages:', b'This PDF, 10 pages:'),
       (b'Cleaning Quote, Visit Log, Thank You)', b'Cleaning Quote, Visit Log, Thank You, Terms of Use)'),
       (b'October 6, 2026', b'October 7, 2026'), (b'October 6\\054 2026', b'October 7\\054 2026'),
       (b'Oct 4, 2026', b'Oct 7, 2026'), (b'Version 2,', b'Version 3,'),
       (b'\\050news release IR\\0552026\\05529\\051', b'\\050IR Bulletin 2026\\05529\\051')]
w = pypdf.PdfWriter(clone_from=sys.argv[1])
for p in w.pages:
    c = p.get_contents().get_data(); o = c
    for a, b in REP:
        c = c.replace(a, b)
    if c != o:
        s = DecodedStreamObject(); s.set_data(c); p[NameObject('/Contents')] = w._add_object(s)
w.add_metadata({'/ModDate': "D:20261007120000+00'00'"})
w.write(sys.argv[2])
