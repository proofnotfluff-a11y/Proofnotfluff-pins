#!/usr/bin/env python3
"""Updates the v2 forms PDFs (from the live #14 zip, scoreboard asset f1d35d30) for the v3 workbook.
Usage: python3 patch_forms.py <v2 Cleaning-Business-Forms-Letter.pdf or -A4.pdf> <out.pdf>
Plain text replacements in each content stream; fillable fields are kept.

Page 1 of the v2 PDFs carries the Legal desk's overlay stream (a paper-colored box over
"9 pages ... Thank You" and the "10 pages ... Terms of Use" text on top). The old text under
the box still sat in the base stream, so text extraction and screen readers read the line twice.
Oct 8: the covered words are removed from the base stream ("This PDF," stays, the overlay
supplies the rest), and the kit list follows the v3 tab order (price sheet before quote builder)."""
import re
import sys

import pypdf
from pypdf.generic import ArrayObject, DecodedStreamObject, NameObject

REP = [(b'tab 7 Job Log', b'tab 6 Job Log'),
       # Letter kit list: one line, then "client list, job log, money by month"
       (b'business info, your numbers, cleaning rates, quote builder, price sheet,',
        b'your numbers and business info, cleaning rates, price sheet, quote builder,'),
       # A4 kit list: the line breaks after "price", so the order is fixed across both lines
       (b'business info, your numbers, cleaning rates, quote builder, price)',
        b'your numbers and business info, cleaning rates, price sheet, quote)'),
       (b'(sheet, client list, job log, money by month)', b'(builder, client list, job log with money by month)'),
       (b'client list, job log, money by month', b'client list, job log with money by month'),
       (b'October 6, 2026', b'October 8, 2026'), (b'October 6\\054 2026', b'October 8\\054 2026'),
       (b'Oct 4, 2026', b'Oct 8, 2026'), (b'Version 2,', b'Version 3,'),
       (b'\\050news release IR\\0552026\\05529\\051', b'\\050IR Bulletin 2026\\05529\\051')]

# Base-stream text the page 1 overlay paints over: keep "This PDF," and drop the rest.
COVERED_FIRST = re.compile(rb'\(This PDF, 9 pages: [^)]*\) Tj')
COVERED_DROP = re.compile(rb'BT 1 0 0 1 60 [\d.]+ Tm /F3\+0 10\.5 Tf 12\.6 TL \((?:checklists, )?Cleaning Quote, Visit Log, Thank You\) Tj T\* ET\n?')


def fix(data, base):
    o = data
    if base:
        data = COVERED_FIRST.sub(b'(This PDF,) Tj', data)
        data = COVERED_DROP.sub(b'', data)
    for a, b in REP:
        data = data.replace(a, b)
    return data, data != o


w = pypdf.PdfWriter(clone_from=sys.argv[1])
for i, p in enumerate(w.pages):
    cs = p['/Contents'].get_object()
    parts = list(cs) if isinstance(cs, ArrayObject) else [p['/Contents']]
    new, changed = [], False
    for k, ref in enumerate(parts):
        d, ch = fix(ref.get_object().get_data(), base=(i == 0 and k == 0 and len(parts) > 1))
        changed |= ch
        s = DecodedStreamObject(); s.set_data(d); new.append(w._add_object(s))
    if changed:
        p[NameObject('/Contents')] = ArrayObject(new) if len(new) > 1 else new[0]
w.add_metadata({'/ModDate': "D:20261008120000+00'00'"})
w.write(sys.argv[2])
