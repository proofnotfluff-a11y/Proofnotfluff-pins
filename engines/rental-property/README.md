# #19 Rental Property Spreadsheet for 1 to 10 Doors (v2, v3 design)

Redesign desk, Oct 7, 2026. Rebuilt to design/WORKBOOK_STANDARD.md section 0 with the same inputs, categories, example and maths as the v1 file live on Etsy (shelf zip sha 6698db13). The v1 engine is in git history (commit before this one).

Rebuild:
1. `python3 engines/rental-property/build_xlsx.py out.xlsx` (add `--blank` for a blank copy). Prints the key row numbers and writes addresses.json.
2. `python3 tools/compare_xlsx.py old.xlsx out.xlsx engines/rental-property/compare_map.json --report engines/rental-property/compare_report.md`
3. `python3 tools/render_xlsx.py out.xlsx dir [--print]`, then `python3 tools/pack_product.py out.xlsx engines/rental-property/LICENSE-AND-DISCLAIMER.txt newdir --tier high`
4. Images: render at `--dpi 300`, point listing_images.json "base" at it, run tools/listing_images.py. Video: tools/listing_video.py with listing_video.json.

Sources checked Oct 7, 2026: IRS Schedule E (Form 1040) 2025 Part I lines 3 to 20; draft 2026 Schedule E (created May 6, 2026: line 13 split into 13a and 13b); 2025 Instructions for Schedule E line 14 (page updated Apr 30, 2026); IRS Publication 527 (2025) security deposits and advance rent; Etsy Help "Downloading a Digital Item"; Microsoft support, mobile apps screen size limit 10.1 inches.
