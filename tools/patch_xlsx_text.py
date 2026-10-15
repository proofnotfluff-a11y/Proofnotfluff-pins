"""Patch a shipped xlsx at XML level: copy the text and row height of target cells from a fresh build."""
import sys, zipfile, re, openpyxl
from xml.sax.saxutils import escape
old, new, out = sys.argv[1:4]
targets = [t.split('!') for t in sys.argv[4:]]
wo = openpyxl.load_workbook(old); wn = openpyxl.load_workbook(new)
zin = zipfile.ZipFile(old)
files = {i.filename: zin.read(i.filename) for i in zin.infolist()}
wbx = files['xl/workbook.xml'].decode(); rels = files['xl/_rels/workbook.xml.rels'].decode()
rid = {m.group(1): m.group(2) for m in re.finditer(r'<sheet [^>]*name="([^"]+)"[^>]*r:id="([^"]+)"', wbx)}
tgt = {m.group(1): m.group(2) for m in re.finditer(r'<Relationship [^>]*Id="([^"]+)"[^>]*Target="([^"]+)"', rels)}
tgt.update({m.group(2): m.group(1) for m in re.finditer(r'<Relationship [^>]*Target="([^"]+)"[^>]*Id="([^"]+)"', rels)})
for sheet, cell in targets:
    ov = wo[sheet][cell].value; nv = wn[sheet][cell].value
    assert ov != nv
    t = tgt[rid[sheet]]
    p = t.lstrip('/') if t.startswith('/') else 'xl/' + t
    x = files[p].decode()
    m = re.search(r'<c r="%s"[^>]*>.*?</c>' % cell, x, re.S)
    c = m.group(0)
    # shortest unique differing segment (rich-text cells keep their runs)
    i = 0
    while i < min(len(ov), len(nv)) and ov[i] == nv[i]: i += 1
    j = 0
    while j < min(len(ov), len(nv)) - i and ov[-1-j] == nv[-1-j]: j += 1
    k = 40
    while True:
        a = max(0, i - k); seg_o = ov[a:len(ov)-j]; seg_n = nv[a:len(nv)-j]
        if c.count(escape(seg_o)) == 1 or a == 0: break
        k += 40
    assert c.count(escape(seg_o)) == 1, (sheet, cell, seg_o[:80])
    x = x.replace(c, c.replace(escape(seg_o), escape(seg_n)), 1)
    row = int(re.sub(r'\D', '', cell))
    h = max(wn[sheet].row_dimensions[row].height or 0, wo[sheet].row_dimensions[row].height or 0)
    tag = re.search(r'<row r="%d"[^>]*>' % row, x).group(0)
    ntag = re.sub(r' ht="[^"]*"', ' ht="%s"' % h, tag) if ' ht=' in tag else tag.replace('<row ', '<row ht="%s" customHeight="1" ' % h, 1)
    x = x.replace(tag, ntag, 1)
    files[p] = x.encode()
    print(sheet, cell, 'row', row, wo[sheet].row_dimensions[row].height, '->', h)
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for i in zin.infolist():
        z.writestr(i, files[i.filename], compress_type=zipfile.ZIP_DEFLATED)
