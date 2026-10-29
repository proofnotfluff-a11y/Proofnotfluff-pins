# KDP print packs

One folder per product id: `build.py` (rebuilds `interior.pdf` and `cover.pdf` from the legally cleared digital edition), `kdp.md` (title, subtitle, description, keywords, categories, price, KDP answers), `preflight.json` (QA results) and `render/` (contact sheet, sample pages and the cover as PNG).

Shared code in `_common/`: `pnfprint.py` (fonts, margins, page flow, cover builder, copy rules) and `preflight.py` (page count, trim size, margin checks by vector and by pixel, embedded fonts, no form fields, grayscale, cover spread size, em dash and banned-word scan, renders).

Rebuild and check:

    python3 kdp/11/build.py && python3 kdp/_common/preflight.py kdp/11 42 --render-pages 1,2,41
    python3 kdp/8/build.py  && python3 kdp/_common/preflight.py kdp/8 26 --render-pages 1,2,24

Spec (shop-run prompt, AMAZON KDP): 8.5 x 11 in, black and white, no bleed, no fillable fields, fonts embedded, gutter at least 0.375 in and outside margins at least 0.25 in, 24 to 110 pages; cover spine = pages x 0.002252 in, spread = 2 x 8.5 + spine + 0.25 in wide by 11.25 in high, barcode zone 2 x 1.2 in bottom right of the back, spine text only from 79 pages.
