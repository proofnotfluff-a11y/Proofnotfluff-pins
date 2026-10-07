# #7 Shipping True-Cost Calculator: v1 (Drive folder 07, Sep 29, 2026) vs v3 (Oct 7, 2026)

Run: python3 tools/compare_xlsx.py old.xlsx new.xlsx engines/shipping-true-cost/compare_map.json
8 cases (example, high, low, blank key inputs, overrides and edits incl. a new 11th product, edge incl. row 30 and zone 9,
quote picked but blank, blank shop) x 521 outputs: every number matches.

Intended differences, all words, no numbers:
- 386 rows: status words in sentence case ("Under-recovered" for "UNDER-RECOVERED", "OK" for "ok", "Yes"/"No" for "YES"/"no",
  "Dim weight bites: +12 lb" for "DIM WEIGHT BITES: +12 lb"). Same word, same rule.
- 8 rows: the Free Shipping baseline column reads "Today" (v1 "baseline").
- 1 row: the blank-shop recommendation names tab 1 instead of the old tab name.
- 3 rows: with no parcel cost (blank shop) the scenario verdicts stay blank; v1 still printed a verdict with no parcel cost to compare.

Hardening that LibreOffice cannot show (both files read blank there), fixed for Excel:
- blank zone: v1 passed zone 0 to INDEX, which reads a whole rate row in Excel; v3 waits for a zone ("Enter postage").
- "Your quote A/B" picked with no quote typed: in Excel v1's INDEX returned 0, so postage counted as $0 and the row could
  read COVERED; v3 shows "Enter postage".
New in v3 (not in v1, so not in the map): the "Add USPS holiday prices" switch on tab 4 ships set to No. Checked by hand
with it on: Ground Advantage commercial 2 lb zone 8 $12.87 + $0.55 = $13.42; Priority 4 lb zone 5 $19.88 + $1.75 = $21.63;
15 lb zone 5 $21.15 + $1.75 = $22.90 (USPS release Aug 25, 2026).
All 567 USPS and 160 UPS rate-table cells were also compared cell by cell with v1: 0 differences.

| case | output | old | new | match |
|---|---|---|---|---|
| example | p1_postage | 9.95 | 9.95 | yes |
| example | p1_labor | 1.8 | 1.8 | yes |
| example | p1_true | 13.19 | 13.19 | yes |
| example | p1_short | -8.24 | -8.24 | yes |
| example | p1_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| example | p1_share | 0.7544 | 0.7544 | yes |
| example | p1_d_name | Ceramic Mug 12 oz | Ceramic Mug 12 oz | yes |
| example | p1_d_lb | 1.125 | 1.125 | yes |
| example | p1_d_cubic | 288 | 288 | yes |
| example | p1_d_over | no | No | intended: sentence case only, same status word |
| example | p1_d_uspsdim | - | - | yes |
| example | p1_d_uspsbill | 2 | 2 | yes |
| example | p1_d_upsdim | 2.0719 | 2.0719 | yes |
| example | p1_d_upsbill | 3 | 3 | yes |
| example | p1_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| example | p1_d_upsflag | DIM WEIGHT BITES: +1 lb | Dim weight bites: +1 lb | intended: sentence case only, same status word |
| example | p1_s_usps | 2 | 2 | yes |
| example | p1_s_ups | 3 | 3 | yes |
| example | p1_s_zone | 5 | 5 | yes |
| example | p1_s_gacom | 9.95 | 9.95 | yes |
| example | p1_s_garet | 14.1 | 14.1 | yes |
| example | p1_s_pri | 13.17 | 13.17 | yes |
| example | p1_s_upsgs | 23.6596 | 23.6596 | yes |
| example | p1_s_cheap | 9.95 | 9.95 | yes |
| example | p1_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| example | p1_s_saved | 4.15 | 4.15 | yes |
| example | p1_b_name | Ceramic Mug 12 oz | Ceramic Mug 12 oz | yes |
| example | p1_b_sale | 19 | 19 | yes |
| example | p1_b_ship | 4.95 | 4.95 | yes |
| example | p1_b_true | 13.19 | 13.19 | yes |
| example | p1_b_fees | 2.7252 | 2.7252 | yes |
| example | p1_b_net | -0.4652 | -0.4652 | yes |
| example | p1_b_margin | -0.0194 | -0.0194 | yes |
| example | p1_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| example | p1_b_flag | LOSING MONEY | Losing money | intended: sentence case only, same status word |
| example | p2_postage | 7.3 | 7.3 | yes |
| example | p2_labor | 0.9 | 0.9 | yes |
| example | p2_true | 8.48 | 8.48 | yes |
| example | p2_short | -3.53 | -3.53 | yes |
| example | p2_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| example | p2_share | 0.8608 | 0.8608 | yes |
| example | p2_d_name | Graphic T-Shirt | Graphic T-Shirt | yes |
| example | p2_d_lb | 0.4375 | 0.4375 | yes |
| example | p2_d_cubic | 130 | 130 | yes |
| example | p2_d_over | no | No | intended: sentence case only, same status word |
| example | p2_d_uspsdim | - | - | yes |
| example | p2_d_uspsbill | 0.4375 | 0.4375 | yes |
| example | p2_d_upsdim | 0.9353 | 0.9353 | yes |
| example | p2_d_upsbill | 1 | 1 | yes |
| example | p2_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| example | p2_d_upsflag | ok | OK | intended: sentence case only, same status word |
| example | p2_s_usps | 0.4375 | 0.4375 | yes |
| example | p2_s_ups | 1 | 1 | yes |
| example | p2_s_zone | 3 | 3 | yes |
| example | p2_s_gacom | 7.3 | 7.3 | yes |
| example | p2_s_garet | 8.15 | 8.15 | yes |
| example | p2_s_pri | 9.71 | 9.71 | yes |
| example | p2_s_upsgs | 17.4954 | 17.4954 | yes |
| example | p2_s_cheap | 7.3 | 7.3 | yes |
| example | p2_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| example | p2_s_saved | 0.85 | 0.85 | yes |
| example | p2_b_name | Graphic T-Shirt | Graphic T-Shirt | yes |
| example | p2_b_sale | 28 | 28 | yes |
| example | p2_b_ship | 4.95 | 4.95 | yes |
| example | p2_b_true | 8.48 | 8.48 | yes |
| example | p2_b_fees | 3.5803 | 3.5803 | yes |
| example | p2_b_net | 8.8898 | 8.8898 | yes |
| example | p2_b_margin | 0.2698 | 0.2698 | yes |
| example | p2_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| example | p2_b_flag | OK | OK | yes |
| example | p3_postage | 15.16 | 15.16 | yes |
| example | p3_labor | 3.6 | 3.6 | yes |
| example | p3_true | 22.47 | 22.47 | yes |
| example | p3_short | -10.47 | -10.47 | yes |
| example | p3_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| example | p3_share | 0.6747 | 0.6747 | yes |
| example | p3_d_name | Framed Print 11x14 | Framed Print 11x14 | yes |
| example | p3_d_lb | 3.25 | 3.25 | yes |
| example | p3_d_cubic | 756 | 756 | yes |
| example | p3_d_over | no | No | intended: sentence case only, same status word |
| example | p3_d_uspsdim | - | - | yes |
| example | p3_d_uspsbill | 4 | 4 | yes |
| example | p3_d_upsdim | 5.4388 | 5.4388 | yes |
| example | p3_d_upsbill | 6 | 6 | yes |
| example | p3_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| example | p3_d_upsflag | DIM WEIGHT BITES: +2 lb | Dim weight bites: +2 lb | intended: sentence case only, same status word |
| example | p3_s_usps | 4 | 4 | yes |
| example | p3_s_ups | 6 | 6 | yes |
| example | p3_s_zone | 6 | 6 | yes |
| example | p3_s_gacom | 15.16 | 15.16 | yes |
| example | p3_s_garet | 18.3 | 18.3 | yes |
| example | p3_s_pri | 24.51 | 24.51 | yes |
| example | p3_s_upsgs | 27.0526 | 27.0526 | yes |
| example | p3_s_cheap | 15.16 | 15.16 | yes |
| example | p3_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| example | p3_s_saved | 3.14 | 3.14 | yes |
| example | p3_b_name | Framed Print 11x14 | Framed Print 11x14 | yes |
| example | p3_b_sale | 65 | 65 | yes |
| example | p3_b_ship | 12 | 12 | yes |
| example | p3_b_true | 22.47 | 22.47 | yes |
| example | p3_b_fees | 7.765 | 7.765 | yes |
| example | p3_b_net | 24.765 | 24.765 | yes |
| example | p3_b_margin | 0.3216 | 0.3216 | yes |
| example | p3_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| example | p3_b_flag | OK | OK | yes |
| example | p4_postage | 8.4 | 8.4 | yes |
| example | p4_labor | 0.9 | 0.9 | yes |
| example | p4_true | 9.76 | 9.76 | yes |
| example | p4_short | -9.76 | -9.76 | yes |
| example | p4_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| example | p4_share | 0.8607 | 0.8607 | yes |
| example | p4_d_name | Sterling Silver Earrings | Sterling Silver Earrings | yes |
| example | p4_d_lb | 0.125 | 0.125 | yes |
| example | p4_d_cubic | 54 | 54 | yes |
| example | p4_d_over | no | No | intended: sentence case only, same status word |
| example | p4_d_uspsdim | - | - | yes |
| example | p4_d_uspsbill | 0.125 | 0.125 | yes |
| example | p4_d_upsdim | 0.3885 | 0.3885 | yes |
| example | p4_d_upsbill | 1 | 1 | yes |
| example | p4_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| example | p4_d_upsflag | ok | OK | intended: sentence case only, same status word |
| example | p4_s_usps | 0.125 | 0.125 | yes |
| example | p4_s_ups | 1 | 1 | yes |
| example | p4_s_zone | 8 | 8 | yes |
| example | p4_s_gacom | 8.4 | 8.4 | yes |
| example | p4_s_garet | 9.45 | 9.45 | yes |
| example | p4_s_pri | 15.22 | 15.22 | yes |
| example | p4_s_upsgs | 21.0567 | 21.0567 | yes |
| example | p4_s_cheap | 8.4 | 8.4 | yes |
| example | p4_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| example | p4_s_saved | 1.05 | 1.05 | yes |
| example | p4_b_name | Sterling Silver Earrings | Sterling Silver Earrings | yes |
| example | p4_b_sale | 42 | 42 | yes |
| example | p4_b_ship | 0 | 0 | yes |
| example | p4_b_true | 9.76 | 9.76 | yes |
| example | p4_b_fees | 4.44 | 4.44 | yes |
| example | p4_b_net | 16.8 | 16.8 | yes |
| example | p4_b_margin | 0.4 | 0.4 | yes |
| example | p4_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| example | p4_b_flag | OK | OK | yes |
| example | p5_postage | 8.51 | 8.51 | yes |
| example | p5_labor | 1.5 | 1.5 | yes |
| example | p5_true | 11.25 | 11.25 | yes |
| example | p5_short | -2.3 | -2.3 | yes |
| example | p5_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| example | p5_share | 0.7564 | 0.7564 | yes |
| example | p5_d_name | Soy Candle 8 oz | Soy Candle 8 oz | yes |
| example | p5_d_lb | 1.25 | 1.25 | yes |
| example | p5_d_cubic | 216 | 216 | yes |
| example | p5_d_over | no | No | intended: sentence case only, same status word |
| example | p5_d_uspsdim | - | - | yes |
| example | p5_d_uspsbill | 2 | 2 | yes |
| example | p5_d_upsdim | 1.554 | 1.554 | yes |
| example | p5_d_upsbill | 2 | 2 | yes |
| example | p5_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| example | p5_d_upsflag | ok | OK | intended: sentence case only, same status word |
| example | p5_s_usps | 2 | 2 | yes |
| example | p5_s_ups | 2 | 2 | yes |
| example | p5_s_zone | 4 | 4 | yes |
| example | p5_s_gacom | 8.51 | 8.51 | yes |
| example | p5_s_garet | 13 | 13 | yes |
| example | p5_s_pri | 10.79 | 10.79 | yes |
| example | p5_s_upsgs | 21.6395 | 21.6395 | yes |
| example | p5_s_cheap | 8.51 | 8.51 | yes |
| example | p5_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| example | p5_s_saved | 4.49 | 4.49 | yes |
| example | p5_b_name | Soy Candle 8 oz | Soy Candle 8 oz | yes |
| example | p5_b_sale | 22 | 22 | yes |
| example | p5_b_ship | 8.95 | 8.95 | yes |
| example | p5_b_true | 11.25 | 11.25 | yes |
| example | p5_b_fees | 3.3902 | 3.3902 | yes |
| example | p5_b_net | 10.7097 | 10.7097 | yes |
| example | p5_b_margin | 0.346 | 0.346 | yes |
| example | p5_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| example | p5_b_flag | OK | OK | yes |
| example | p6_postage | 21.15 | 21.15 | yes |
| example | p6_labor | 3 | 3 | yes |
| example | p6_true | 28.21 | 28.21 | yes |
| example | p6_short | -13.26 | -13.26 | yes |
| example | p6_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| example | p6_share | 0.7497 | 0.7497 | yes |
| example | p6_d_name | Grapevine Wreath 16 in | Grapevine Wreath 16 in | yes |
| example | p6_d_lb | 2.5 | 2.5 | yes |
| example | p6_d_cubic | 2,048 | 2,048 | yes |
| example | p6_d_over | YES | Yes | intended: sentence case only, same status word |
| example | p6_d_uspsdim | 14.7338 | 14.7338 | yes |
| example | p6_d_uspsbill | 15 | 15 | yes |
| example | p6_d_upsdim | 14.7338 | 14.7338 | yes |
| example | p6_d_upsbill | 15 | 15 | yes |
| example | p6_d_uspsflag | DIM WEIGHT BITES: +12 lb | Dim weight bites: +12 lb | intended: sentence case only, same status word |
| example | p6_d_upsflag | DIM WEIGHT BITES: +12 lb | Dim weight bites: +12 lb | intended: sentence case only, same status word |
| example | p6_s_usps | 15 | 15 | yes |
| example | p6_s_ups | 15 | 15 | yes |
| example | p6_s_zone | 5 | 5 | yes |
| example | p6_s_gacom | 21.15 | 21.15 | yes |
| example | p6_s_garet | 28.95 | 28.95 | yes |
| example | p6_s_pri | 35.25 | 35.25 | yes |
| example | p6_s_upsgs | 39.9637 | 39.9637 | yes |
| example | p6_s_cheap | 21.15 | 21.15 | yes |
| example | p6_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| example | p6_s_saved | 7.8 | 7.8 | yes |
| example | p6_b_name | Grapevine Wreath 16 in | Grapevine Wreath 16 in | yes |
| example | p6_b_sale | 58 | 58 | yes |
| example | p6_b_ship | 14.95 | 14.95 | yes |
| example | p6_b_true | 28.21 | 28.21 | yes |
| example | p6_b_fees | 7.3803 | 7.3803 | yes |
| example | p6_b_net | 19.3598 | 19.3598 | yes |
| example | p6_b_margin | 0.2654 | 0.2654 | yes |
| example | p6_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| example | p6_b_flag | OK | OK | yes |
| example | p7_postage | 6.94 | 6.94 | yes |
| example | p7_labor | 0.9 | 0.9 | yes |
| example | p7_true | 8.15 | 8.15 | yes |
| example | p7_short | -1.2 | -1.2 | yes |
| example | p7_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| example | p7_share | 0.8515 | 0.8515 | yes |
| example | p7_d_name | Canvas Tote Bag | Canvas Tote Bag | yes |
| example | p7_d_lb | 0.5625 | 0.5625 | yes |
| example | p7_d_cubic | 180 | 180 | yes |
| example | p7_d_over | no | No | intended: sentence case only, same status word |
| example | p7_d_uspsdim | - | - | yes |
| example | p7_d_uspsbill | 0.5625 | 0.5625 | yes |
| example | p7_d_upsdim | 1.295 | 1.295 | yes |
| example | p7_d_upsbill | 2 | 2 | yes |
| example | p7_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| example | p7_d_upsflag | DIM WEIGHT BITES: +1 lb | Dim weight bites: +1 lb | intended: sentence case only, same status word |
| example | p7_s_usps | 0.5625 | 0.5625 | yes |
| example | p7_s_ups | 2 | 2 | yes |
| example | p7_s_zone | 2 | 2 | yes |
| example | p7_s_gacom | 6.94 | 6.94 | yes |
| example | p7_s_garet | 9.95 | 9.95 | yes |
| example | p7_s_pri | 9.32 | 9.32 | yes |
| example | p7_s_upsgs | 18.117 | 18.117 | yes |
| example | p7_s_cheap | 6.94 | 6.94 | yes |
| example | p7_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| example | p7_s_saved | 3.01 | 3.01 | yes |
| example | p7_b_name | Canvas Tote Bag | Canvas Tote Bag | yes |
| example | p7_b_sale | 30 | 30 | yes |
| example | p7_b_ship | 6.95 | 6.95 | yes |
| example | p7_b_true | 8.15 | 8.15 | yes |
| example | p7_b_fees | 3.9603 | 3.9603 | yes |
| example | p7_b_net | 15.3398 | 15.3398 | yes |
| example | p7_b_margin | 0.4151 | 0.4151 | yes |
| example | p7_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| example | p7_b_flag | OK | OK | yes |
| example | p8_postage | 7.69 | 7.69 | yes |
| example | p8_labor | 1.2 | 1.2 | yes |
| example | p8_true | 9.75 | 9.75 | yes |
| example | p8_short | 0.2 | 0.2 | yes |
| example | p8_flag | COVERED | Covered | intended: sentence case only, same status word |
| example | p8_share | 0.7887 | 0.7887 | yes |
| example | p8_d_name | Handmade Soap Set (3) | Handmade Soap Set (3) | yes |
| example | p8_d_lb | 0.875 | 0.875 | yes |
| example | p8_d_cubic | 105 | 105 | yes |
| example | p8_d_over | no | No | intended: sentence case only, same status word |
| example | p8_d_uspsdim | - | - | yes |
| example | p8_d_uspsbill | 0.875 | 0.875 | yes |
| example | p8_d_upsdim | 0.7554 | 0.7554 | yes |
| example | p8_d_upsbill | 1 | 1 | yes |
| example | p8_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| example | p8_d_upsflag | ok | OK | intended: sentence case only, same status word |
| example | p8_s_usps | 0.875 | 0.875 | yes |
| example | p8_s_ups | 1 | 1 | yes |
| example | p8_s_zone | 5 | 5 | yes |
| example | p8_s_gacom | 7.69 | 7.69 | yes |
| example | p8_s_garet | 10.95 | 10.95 | yes |
| example | p8_s_pri | 12.97 | 12.97 | yes |
| example | p8_s_upsgs | 19.8265 | 19.8265 | yes |
| example | p8_s_cheap | 7.69 | 7.69 | yes |
| example | p8_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| example | p8_s_saved | 3.26 | 3.26 | yes |
| example | p8_b_name | Handmade Soap Set (3) | Handmade Soap Set (3) | yes |
| example | p8_b_sale | 26 | 26 | yes |
| example | p8_b_ship | 9.95 | 9.95 | yes |
| example | p8_b_true | 9.75 | 9.75 | yes |
| example | p8_b_fees | 3.8653 | 3.8653 | yes |
| example | p8_b_net | 16.3347 | 16.3347 | yes |
| example | p8_b_margin | 0.4544 | 0.4544 | yes |
| example | p8_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| example | p8_b_flag | OK | OK | yes |
| example | p9_postage | 8.51 | 8.51 | yes |
| example | p9_labor | 1.5 | 1.5 | yes |
| example | p9_true | 11.4 | 11.4 | yes |
| example | p9_short | 1.55 | 1.55 | yes |
| example | p9_flag | COVERED | Covered | intended: sentence case only, same status word |
| example | p9_share | 0.7465 | 0.7465 | yes |
| example | p9_d_name | Wooden Puzzle | Wooden Puzzle | yes |
| example | p9_d_lb | 1.875 | 1.875 | yes |
| example | p9_d_cubic | 160 | 160 | yes |
| example | p9_d_over | no | No | intended: sentence case only, same status word |
| example | p9_d_uspsdim | - | - | yes |
| example | p9_d_uspsbill | 2 | 2 | yes |
| example | p9_d_upsdim | 1.1511 | 1.1511 | yes |
| example | p9_d_upsbill | 2 | 2 | yes |
| example | p9_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| example | p9_d_upsflag | ok | OK | intended: sentence case only, same status word |
| example | p9_s_usps | 2 | 2 | yes |
| example | p9_s_ups | 2 | 2 | yes |
| example | p9_s_zone | 4 | 4 | yes |
| example | p9_s_gacom | 8.51 | 8.51 | yes |
| example | p9_s_garet | 13 | 13 | yes |
| example | p9_s_pri | 10.79 | 10.79 | yes |
| example | p9_s_upsgs | 21.6395 | 21.6395 | yes |
| example | p9_s_cheap | 8.51 | 8.51 | yes |
| example | p9_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| example | p9_s_saved | 4.49 | 4.49 | yes |
| example | p9_b_name | Wooden Puzzle | Wooden Puzzle | yes |
| example | p9_b_sale | 34 | 34 | yes |
| example | p9_b_ship | 12.95 | 12.95 | yes |
| example | p9_b_true | 11.4 | 11.4 | yes |
| example | p9_b_fees | 4.9103 | 4.9103 | yes |
| example | p9_b_net | 21.6398 | 21.6398 | yes |
| example | p9_b_margin | 0.4609 | 0.4609 | yes |
| example | p9_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| example | p9_b_flag | OK | OK | yes |
| example | p10_postage | 12.84 | 12.84 | yes |
| example | p10_labor | 2.1 | 2.1 | yes |
| example | p10_true | 16.85 | 16.85 | yes |
| example | p10_short | 1.1 | 1.1 | yes |
| example | p10_flag | COVERED | Covered | intended: sentence case only, same status word |
| example | p10_share | 0.762 | 0.762 | yes |
| example | p10_d_name | Board Game | Board Game | yes |
| example | p10_d_lb | 3.75 | 3.75 | yes |
| example | p10_d_cubic | 432 | 432 | yes |
| example | p10_d_over | no | No | intended: sentence case only, same status word |
| example | p10_d_uspsdim | - | - | yes |
| example | p10_d_uspsbill | 4 | 4 | yes |
| example | p10_d_upsdim | 3.1079 | 3.1079 | yes |
| example | p10_d_upsbill | 4 | 4 | yes |
| example | p10_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| example | p10_d_upsflag | ok | OK | intended: sentence case only, same status word |
| example | p10_s_usps | 4 | 4 | yes |
| example | p10_s_ups | 4 | 4 | yes |
| example | p10_s_zone | 5 | 5 | yes |
| example | p10_s_gacom | 12.84 | 12.84 | yes |
| example | p10_s_garet | 16.4 | 16.4 | yes |
| example | p10_s_pri | 19.88 | 19.88 | yes |
| example | p10_s_upsgs | 24.9287 | 24.9287 | yes |
| example | p10_s_cheap | 12.84 | 12.84 | yes |
| example | p10_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| example | p10_s_saved | 3.56 | 3.56 | yes |
| example | p10_b_name | Board Game | Board Game | yes |
| example | p10_b_sale | 48 | 48 | yes |
| example | p10_b_ship | 17.95 | 17.95 | yes |
| example | p10_b_true | 16.85 | 16.85 | yes |
| example | p10_b_fees | 6.7153 | 6.7153 | yes |
| example | p10_b_net | 26.3848 | 26.3848 | yes |
| example | p10_b_margin | 0.4001 | 0.4001 | yes |
| example | p10_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| example | p10_b_flag | OK | OK | yes |
| example | p11_postage | (blank) | (blank) | yes |
| example | p11_labor | (blank) | (blank) | yes |
| example | p11_true | (blank) | (blank) | yes |
| example | p11_short | (blank) | (blank) | yes |
| example | p11_flag | (blank) | (blank) | yes |
| example | p11_share | (blank) | (blank) | yes |
| example | p11_d_name | (blank) | (blank) | yes |
| example | p11_d_lb | (blank) | (blank) | yes |
| example | p11_d_cubic | (blank) | (blank) | yes |
| example | p11_d_over | (blank) | (blank) | yes |
| example | p11_d_uspsdim | (blank) | (blank) | yes |
| example | p11_d_uspsbill | (blank) | (blank) | yes |
| example | p11_d_upsdim | (blank) | (blank) | yes |
| example | p11_d_upsbill | (blank) | (blank) | yes |
| example | p11_d_uspsflag | (blank) | (blank) | yes |
| example | p11_d_upsflag | (blank) | (blank) | yes |
| example | p11_s_usps | (blank) | (blank) | yes |
| example | p11_s_ups | (blank) | (blank) | yes |
| example | p11_s_zone | (blank) | (blank) | yes |
| example | p11_s_gacom | (blank) | (blank) | yes |
| example | p11_s_garet | (blank) | (blank) | yes |
| example | p11_s_pri | (blank) | (blank) | yes |
| example | p11_s_upsgs | (blank) | (blank) | yes |
| example | p11_s_cheap | (blank) | (blank) | yes |
| example | p11_s_cheapname | (blank) | (blank) | yes |
| example | p11_s_saved | (blank) | (blank) | yes |
| example | p11_b_name | (blank) | (blank) | yes |
| example | p11_b_sale | (blank) | (blank) | yes |
| example | p11_b_ship | (blank) | (blank) | yes |
| example | p11_b_true | (blank) | (blank) | yes |
| example | p11_b_fees | (blank) | (blank) | yes |
| example | p11_b_net | (blank) | (blank) | yes |
| example | p11_b_margin | (blank) | (blank) | yes |
| example | p11_b_shipflag | (blank) | (blank) | yes |
| example | p11_b_flag | (blank) | (blank) | yes |
| example | p12_postage | (blank) | (blank) | yes |
| example | p12_labor | (blank) | (blank) | yes |
| example | p12_true | (blank) | (blank) | yes |
| example | p12_short | (blank) | (blank) | yes |
| example | p12_flag | (blank) | (blank) | yes |
| example | p12_share | (blank) | (blank) | yes |
| example | p12_d_name | (blank) | (blank) | yes |
| example | p12_d_lb | (blank) | (blank) | yes |
| example | p12_d_cubic | (blank) | (blank) | yes |
| example | p12_d_over | (blank) | (blank) | yes |
| example | p12_d_uspsdim | (blank) | (blank) | yes |
| example | p12_d_uspsbill | (blank) | (blank) | yes |
| example | p12_d_upsdim | (blank) | (blank) | yes |
| example | p12_d_upsbill | (blank) | (blank) | yes |
| example | p12_d_uspsflag | (blank) | (blank) | yes |
| example | p12_d_upsflag | (blank) | (blank) | yes |
| example | p12_s_usps | (blank) | (blank) | yes |
| example | p12_s_ups | (blank) | (blank) | yes |
| example | p12_s_zone | (blank) | (blank) | yes |
| example | p12_s_gacom | (blank) | (blank) | yes |
| example | p12_s_garet | (blank) | (blank) | yes |
| example | p12_s_pri | (blank) | (blank) | yes |
| example | p12_s_upsgs | (blank) | (blank) | yes |
| example | p12_s_cheap | (blank) | (blank) | yes |
| example | p12_s_cheapname | (blank) | (blank) | yes |
| example | p12_s_saved | (blank) | (blank) | yes |
| example | p12_b_name | (blank) | (blank) | yes |
| example | p12_b_sale | (blank) | (blank) | yes |
| example | p12_b_ship | (blank) | (blank) | yes |
| example | p12_b_true | (blank) | (blank) | yes |
| example | p12_b_fees | (blank) | (blank) | yes |
| example | p12_b_net | (blank) | (blank) | yes |
| example | p12_b_margin | (blank) | (blank) | yes |
| example | p12_b_shipflag | (blank) | (blank) | yes |
| example | p12_b_flag | (blank) | (blank) | yes |
| example | p30_postage | (blank) | (blank) | yes |
| example | p30_labor | (blank) | (blank) | yes |
| example | p30_true | (blank) | (blank) | yes |
| example | p30_short | (blank) | (blank) | yes |
| example | p30_flag | (blank) | (blank) | yes |
| example | p30_share | (blank) | (blank) | yes |
| example | p30_d_name | (blank) | (blank) | yes |
| example | p30_d_lb | (blank) | (blank) | yes |
| example | p30_d_cubic | (blank) | (blank) | yes |
| example | p30_d_over | (blank) | (blank) | yes |
| example | p30_d_uspsdim | (blank) | (blank) | yes |
| example | p30_d_uspsbill | (blank) | (blank) | yes |
| example | p30_d_upsdim | (blank) | (blank) | yes |
| example | p30_d_upsbill | (blank) | (blank) | yes |
| example | p30_d_uspsflag | (blank) | (blank) | yes |
| example | p30_d_upsflag | (blank) | (blank) | yes |
| example | p30_s_usps | (blank) | (blank) | yes |
| example | p30_s_ups | (blank) | (blank) | yes |
| example | p30_s_zone | (blank) | (blank) | yes |
| example | p30_s_gacom | (blank) | (blank) | yes |
| example | p30_s_garet | (blank) | (blank) | yes |
| example | p30_s_pri | (blank) | (blank) | yes |
| example | p30_s_upsgs | (blank) | (blank) | yes |
| example | p30_s_cheap | (blank) | (blank) | yes |
| example | p30_s_cheapname | (blank) | (blank) | yes |
| example | p30_s_saved | (blank) | (blank) | yes |
| example | p30_b_name | (blank) | (blank) | yes |
| example | p30_b_sale | (blank) | (blank) | yes |
| example | p30_b_ship | (blank) | (blank) | yes |
| example | p30_b_true | (blank) | (blank) | yes |
| example | p30_b_fees | (blank) | (blank) | yes |
| example | p30_b_net | (blank) | (blank) | yes |
| example | p30_b_margin | (blank) | (blank) | yes |
| example | p30_b_shipflag | (blank) | (blank) | yes |
| example | p30_b_flag | (blank) | (blank) | yes |
| example | avg_true | 13.951 | 13.951 | yes |
| example | avg_short | -4.591 | -4.591 | yes |
| example | avg_share | 0.7805 | 0.7805 | yes |
| example | sc_cheap_total | 106.45 | 106.45 | yes |
| example | sc_saved_total | 35.8 | 35.8 | yes |
| example | db_losing | 1 | 1 | yes |
| example | db_under | 7 | 7 | yes |
| example | db_avgtrue | 13.951 | 13.951 | yes |
| example | db_avgshort | -4.591 | -4.591 | yes |
| example | db_shipcost | 139.51 | 139.51 | yes |
| example | db_collected | 93.6 | 93.6 | yes |
| example | db_netship | -45.91 | -45.91 | yes |
| example | db_share | 0.7805 | 0.7805 | yes |
| example | db_tot_true | 139.51 | 139.51 | yes |
| example | db_tot_fees | 48.732 | 48.732 | yes |
| example | db_tot_net | 159.758 | 159.758 | yes |
| example | fs_tc | 13.951 | 13.951 | yes |
| example | fs_tcused | 13.951 | 13.951 | yes |
| example | fs_profit_order | 14.149 | 14.149 | yes |
| example | fs_cost | 6.5 | 6.5 | yes |
| example | fs_breakeven | 62.4444 | 62.4444 | yes |
| example | fs_recommendation | Best of the three: free shipping over $75, about $396 more profit per 100 orders than today. An estimate built on your assumptions above, not a promise. | Best of the three: free shipping over $75, about $396 more profit per 100 orders than today. An estimate built on your assumptions above, not a promise. | yes |
| example | fs_avgo_today | 48 | 48 | yes |
| example | fs_avgo_s1 | 48 | 48 | yes |
| example | fs_avgo_s2 | 48 | 48 | yes |
| example | fs_avgo_s3 | 48 | 48 | yes |
| example | fs_orders_today | 100 | 100 | yes |
| example | fs_orders_s1 | 115 | 115 | yes |
| example | fs_orders_s2 | 115 | 115 | yes |
| example | fs_orders_s3 | 115 | 115 | yes |
| example | fs_qual_today | 0 | 0 | yes |
| example | fs_qual_s1 | 63.25 | 63.25 | yes |
| example | fs_qual_s2 | 34.5 | 34.5 | yes |
| example | fs_qual_s3 | 13.8 | 13.8 | yes |
| example | fs_other_today | 100 | 100 | yes |
| example | fs_other_s1 | 51.75 | 51.75 | yes |
| example | fs_other_s2 | 80.5 | 80.5 | yes |
| example | fs_other_s3 | 101.2 | 101.2 | yes |
| example | fs_rev_today | 4,800 | 4,800 | yes |
| example | fs_rev_s1 | 5,646.5 | 5,646.5 | yes |
| example | fs_rev_s2 | 6,072 | 6,072 | yes |
| example | fs_rev_s3 | 6,127.2 | 6,127.2 | yes |
| example | fs_coll_today | 650 | 650 | yes |
| example | fs_coll_s1 | 336.375 | 336.375 | yes |
| example | fs_coll_s2 | 523.25 | 523.25 | yes |
| example | fs_coll_s3 | 657.8 | 657.8 | yes |
| example | fs_parc_today | 1,395.1 | 1,395.1 | yes |
| example | fs_parc_s1 | 1,604.365 | 1,604.365 | yes |
| example | fs_parc_s2 | 1,604.365 | 1,604.365 | yes |
| example | fs_parc_s3 | 1,604.365 | 1,604.365 | yes |
| example | fs_profit_today | 1,414.9 | 1,414.9 | yes |
| example | fs_profit_s1 | 1,272.935 | 1,272.935 | yes |
| example | fs_profit_s2 | 1,651.285 | 1,651.285 | yes |
| example | fs_profit_s3 | 1,810.675 | 1,810.675 | yes |
| example | fs_per_today | 14.149 | 14.149 | yes |
| example | fs_per_s1 | 11.069 | 11.069 | yes |
| example | fs_per_s2 | 14.359 | 14.359 | yes |
| example | fs_per_s3 | 15.745 | 15.745 | yes |
| example | fs_chg_today | 0 | 0 | yes |
| example | fs_chg_s1 | -141.965 | -141.965 | yes |
| example | fs_chg_s2 | 236.385 | 236.385 | yes |
| example | fs_chg_s3 | 395.775 | 395.775 | yes |
| example | fs_verdict_today | baseline | Today | intended: baseline column now reads Today |
| example | fs_verdict_s1 | WORSE THAN TODAY | Worse than today | intended: sentence case only, same status word |
| example | fs_verdict_s2 | BEATS TODAY | Beats today | intended: sentence case only, same status word |
| example | fs_verdict_s3 | BEATS TODAY | Beats today | intended: sentence case only, same status word |
| high | p1_postage | 12.87 | 12.87 | yes |
| high | p1_labor | 4.5 | 4.5 | yes |
| high | p1_true | 18.81 | 18.81 | yes |
| high | p1_short | -13.86 | -13.86 | yes |
| high | p1_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p1_share | 0.6842 | 0.6842 | yes |
| high | p1_d_name | Ceramic Mug 12 oz | Ceramic Mug 12 oz | yes |
| high | p1_d_lb | 1.125 | 1.125 | yes |
| high | p1_d_cubic | 288 | 288 | yes |
| high | p1_d_over | no | No | intended: sentence case only, same status word |
| high | p1_d_uspsdim | - | - | yes |
| high | p1_d_uspsbill | 2 | 2 | yes |
| high | p1_d_upsdim | 2.0719 | 2.0719 | yes |
| high | p1_d_upsbill | 3 | 3 | yes |
| high | p1_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| high | p1_d_upsflag | DIM WEIGHT BITES: +1 lb | Dim weight bites: +1 lb | intended: sentence case only, same status word |
| high | p1_s_usps | 2 | 2 | yes |
| high | p1_s_ups | 3 | 3 | yes |
| high | p1_s_zone | 8 | 8 | yes |
| high | p1_s_gacom | 12.87 | 12.87 | yes |
| high | p1_s_garet | 19.05 | 19.05 | yes |
| high | p1_s_pri | 16.37 | 16.37 | yes |
| high | p1_s_upsgs | 26.6252 | 26.6252 | yes |
| high | p1_s_cheap | 12.87 | 12.87 | yes |
| high | p1_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| high | p1_s_saved | 6.18 | 6.18 | yes |
| high | p1_b_name | Ceramic Mug 12 oz | Ceramic Mug 12 oz | yes |
| high | p1_b_sale | 19 | 19 | yes |
| high | p1_b_ship | 4.95 | 4.95 | yes |
| high | p1_b_true | 18.81 | 18.81 | yes |
| high | p1_b_fees | 3.4752 | 3.4752 | yes |
| high | p1_b_net | -6.8352 | -6.8352 | yes |
| high | p1_b_margin | -0.2854 | -0.2854 | yes |
| high | p1_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p1_b_flag | LOSING MONEY | Losing money | intended: sentence case only, same status word |
| high | p2_postage | 7.3 | 7.3 | yes |
| high | p2_labor | 2.25 | 2.25 | yes |
| high | p2_true | 9.83 | 9.83 | yes |
| high | p2_short | -4.88 | -4.88 | yes |
| high | p2_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p2_share | 0.7426 | 0.7426 | yes |
| high | p2_d_name | Graphic T-Shirt | Graphic T-Shirt | yes |
| high | p2_d_lb | 0.4375 | 0.4375 | yes |
| high | p2_d_cubic | 130 | 130 | yes |
| high | p2_d_over | no | No | intended: sentence case only, same status word |
| high | p2_d_uspsdim | - | - | yes |
| high | p2_d_uspsbill | 0.4375 | 0.4375 | yes |
| high | p2_d_upsdim | 0.9353 | 0.9353 | yes |
| high | p2_d_upsbill | 1 | 1 | yes |
| high | p2_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| high | p2_d_upsflag | ok | OK | intended: sentence case only, same status word |
| high | p2_s_usps | 0.4375 | 0.4375 | yes |
| high | p2_s_ups | 1 | 1 | yes |
| high | p2_s_zone | 3 | 3 | yes |
| high | p2_s_gacom | 7.3 | 7.3 | yes |
| high | p2_s_garet | 8.15 | 8.15 | yes |
| high | p2_s_pri | 9.71 | 9.71 | yes |
| high | p2_s_upsgs | 17.4954 | 17.4954 | yes |
| high | p2_s_cheap | 7.3 | 7.3 | yes |
| high | p2_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| high | p2_s_saved | 0.85 | 0.85 | yes |
| high | p2_b_name | Graphic T-Shirt | Graphic T-Shirt | yes |
| high | p2_b_sale | 28 | 28 | yes |
| high | p2_b_ship | 4.95 | 4.95 | yes |
| high | p2_b_true | 9.83 | 9.83 | yes |
| high | p2_b_fees | 7.79 | 7.79 | yes |
| high | p2_b_net | 3.33 | 3.33 | yes |
| high | p2_b_margin | 0.1011 | 0.1011 | yes |
| high | p2_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p2_b_flag | THIN | Thin | intended: sentence case only, same status word |
| high | p3_postage | 15.16 | 15.16 | yes |
| high | p3_labor | 45 | 45 | yes |
| high | p3_true | 63.87 | 63.87 | yes |
| high | p3_short | -51.87 | -51.87 | yes |
| high | p3_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p3_share | 0.2374 | 0.2374 | yes |
| high | p3_d_name | Framed Print 11x14 | Framed Print 11x14 | yes |
| high | p3_d_lb | 3.25 | 3.25 | yes |
| high | p3_d_cubic | 756 | 756 | yes |
| high | p3_d_over | no | No | intended: sentence case only, same status word |
| high | p3_d_uspsdim | - | - | yes |
| high | p3_d_uspsbill | 4 | 4 | yes |
| high | p3_d_upsdim | 5.4388 | 5.4388 | yes |
| high | p3_d_upsbill | 6 | 6 | yes |
| high | p3_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| high | p3_d_upsflag | DIM WEIGHT BITES: +2 lb | Dim weight bites: +2 lb | intended: sentence case only, same status word |
| high | p3_s_usps | 4 | 4 | yes |
| high | p3_s_ups | 6 | 6 | yes |
| high | p3_s_zone | 6 | 6 | yes |
| high | p3_s_gacom | 15.16 | 15.16 | yes |
| high | p3_s_garet | 18.3 | 18.3 | yes |
| high | p3_s_pri | 24.51 | 24.51 | yes |
| high | p3_s_upsgs | 27.0526 | 27.0526 | yes |
| high | p3_s_cheap | 15.16 | 15.16 | yes |
| high | p3_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| high | p3_s_saved | 3.14 | 3.14 | yes |
| high | p3_b_name | Framed Print 11x14 | Framed Print 11x14 | yes |
| high | p3_b_sale | 65 | 65 | yes |
| high | p3_b_ship | 12 | 12 | yes |
| high | p3_b_true | 63.87 | 63.87 | yes |
| high | p3_b_fees | 8.515 | 8.515 | yes |
| high | p3_b_net | -17.385 | -17.385 | yes |
| high | p3_b_margin | -0.2258 | -0.2258 | yes |
| high | p3_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p3_b_flag | LOSING MONEY | Losing money | intended: sentence case only, same status word |
| high | p4_postage | 8.4 | 8.4 | yes |
| high | p4_labor | 2.25 | 2.25 | yes |
| high | p4_true | 11.11 | 11.11 | yes |
| high | p4_short | -11.11 | -11.11 | yes |
| high | p4_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p4_share | 0.7561 | 0.7561 | yes |
| high | p4_d_name | Sterling Silver Earrings | Sterling Silver Earrings | yes |
| high | p4_d_lb | 0.125 | 0.125 | yes |
| high | p4_d_cubic | 54 | 54 | yes |
| high | p4_d_over | no | No | intended: sentence case only, same status word |
| high | p4_d_uspsdim | - | - | yes |
| high | p4_d_uspsbill | 0.125 | 0.125 | yes |
| high | p4_d_upsdim | 0.3885 | 0.3885 | yes |
| high | p4_d_upsbill | 1 | 1 | yes |
| high | p4_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| high | p4_d_upsflag | ok | OK | intended: sentence case only, same status word |
| high | p4_s_usps | 0.125 | 0.125 | yes |
| high | p4_s_ups | 1 | 1 | yes |
| high | p4_s_zone | 8 | 8 | yes |
| high | p4_s_gacom | 8.4 | 8.4 | yes |
| high | p4_s_garet | 9.45 | 9.45 | yes |
| high | p4_s_pri | 15.22 | 15.22 | yes |
| high | p4_s_upsgs | 21.0567 | 21.0567 | yes |
| high | p4_s_cheap | 8.4 | 8.4 | yes |
| high | p4_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| high | p4_s_saved | 1.05 | 1.05 | yes |
| high | p4_b_name | Sterling Silver Earrings | Sterling Silver Earrings | yes |
| high | p4_b_sale | 42 | 42 | yes |
| high | p4_b_ship | 0 | 0 | yes |
| high | p4_b_true | 11.11 | 11.11 | yes |
| high | p4_b_fees | 5.19 | 5.19 | yes |
| high | p4_b_net | 14.7 | 14.7 | yes |
| high | p4_b_margin | 0.35 | 0.35 | yes |
| high | p4_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p4_b_flag | OK | OK | yes |
| high | p5_postage | 8.51 | 8.51 | yes |
| high | p5_labor | 3.75 | 3.75 | yes |
| high | p5_true | 13.5 | 13.5 | yes |
| high | p5_short | -4.55 | -4.55 | yes |
| high | p5_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p5_share | 0.6304 | 0.6304 | yes |
| high | p5_d_name | Soy Candle 8 oz | Soy Candle 8 oz | yes |
| high | p5_d_lb | 1.25 | 1.25 | yes |
| high | p5_d_cubic | 216 | 216 | yes |
| high | p5_d_over | no | No | intended: sentence case only, same status word |
| high | p5_d_uspsdim | - | - | yes |
| high | p5_d_uspsbill | 2 | 2 | yes |
| high | p5_d_upsdim | 1.554 | 1.554 | yes |
| high | p5_d_upsbill | 2 | 2 | yes |
| high | p5_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| high | p5_d_upsflag | ok | OK | intended: sentence case only, same status word |
| high | p5_s_usps | 2 | 2 | yes |
| high | p5_s_ups | 2 | 2 | yes |
| high | p5_s_zone | 4 | 4 | yes |
| high | p5_s_gacom | 8.51 | 8.51 | yes |
| high | p5_s_garet | 13 | 13 | yes |
| high | p5_s_pri | 10.79 | 10.79 | yes |
| high | p5_s_upsgs | 21.6395 | 21.6395 | yes |
| high | p5_s_cheap | 8.51 | 8.51 | yes |
| high | p5_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| high | p5_s_saved | 4.49 | 4.49 | yes |
| high | p5_b_name | Soy Candle 8 oz | Soy Candle 8 oz | yes |
| high | p5_b_sale | 22 | 22 | yes |
| high | p5_b_ship | 8.95 | 8.95 | yes |
| high | p5_b_true | 13.5 | 13.5 | yes |
| high | p5_b_fees | 4.1402 | 4.1402 | yes |
| high | p5_b_net | 7.7097 | 7.7097 | yes |
| high | p5_b_margin | 0.2491 | 0.2491 | yes |
| high | p5_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p5_b_flag | OK | OK | yes |
| high | p6_postage | 37.84 | 37.84 | yes |
| high | p6_labor | 7.5 | 7.5 | yes |
| high | p6_true | 49.4 | 49.4 | yes |
| high | p6_short | -34.45 | -34.45 | yes |
| high | p6_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p6_share | 0.766 | 0.766 | yes |
| high | p6_d_name | Grapevine Wreath 16 in | Grapevine Wreath 16 in | yes |
| high | p6_d_lb | 18.75 | 18.75 | yes |
| high | p6_d_cubic | 2,048 | 2,048 | yes |
| high | p6_d_over | YES | Yes | intended: sentence case only, same status word |
| high | p6_d_uspsdim | 14.7338 | 14.7338 | yes |
| high | p6_d_uspsbill | 19 | 19 | yes |
| high | p6_d_upsdim | 14.7338 | 14.7338 | yes |
| high | p6_d_upsbill | 19 | 19 | yes |
| high | p6_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| high | p6_d_upsflag | ok | OK | intended: sentence case only, same status word |
| high | p6_s_usps | 19 | 19 | yes |
| high | p6_s_ups | 19 | 19 | yes |
| high | p6_s_zone | 9 | 9 | yes |
| high | p6_s_gacom | 37.84 | 37.84 | yes |
| high | p6_s_garet | 68 | 68 | yes |
| high | p6_s_pri | 137.58 | 137.58 | yes |
| high | p6_s_upsgs | n/a | n/a | yes |
| high | p6_s_cheap | 37.84 | 37.84 | yes |
| high | p6_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| high | p6_s_saved | 30.16 | 30.16 | yes |
| high | p6_b_name | Grapevine Wreath 16 in | Grapevine Wreath 16 in | yes |
| high | p6_b_sale | 58 | 58 | yes |
| high | p6_b_ship | 14.95 | 14.95 | yes |
| high | p6_b_true | 49.4 | 49.4 | yes |
| high | p6_b_fees | 8.1303 | 8.1303 | yes |
| high | p6_b_net | -2.5803 | -2.5803 | yes |
| high | p6_b_margin | -0.0354 | -0.0354 | yes |
| high | p6_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p6_b_flag | LOSING MONEY | Losing money | intended: sentence case only, same status word |
| high | p7_postage | 6.94 | 6.94 | yes |
| high | p7_labor | 2.25 | 2.25 | yes |
| high | p7_true | 9.5 | 9.5 | yes |
| high | p7_short | -2.55 | -2.55 | yes |
| high | p7_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p7_share | 0.7305 | 0.7305 | yes |
| high | p7_d_name | Canvas Tote Bag | Canvas Tote Bag | yes |
| high | p7_d_lb | 0.5625 | 0.5625 | yes |
| high | p7_d_cubic | 180 | 180 | yes |
| high | p7_d_over | no | No | intended: sentence case only, same status word |
| high | p7_d_uspsdim | - | - | yes |
| high | p7_d_uspsbill | 0.5625 | 0.5625 | yes |
| high | p7_d_upsdim | 1.295 | 1.295 | yes |
| high | p7_d_upsbill | 2 | 2 | yes |
| high | p7_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| high | p7_d_upsflag | DIM WEIGHT BITES: +1 lb | Dim weight bites: +1 lb | intended: sentence case only, same status word |
| high | p7_s_usps | 0.5625 | 0.5625 | yes |
| high | p7_s_ups | 2 | 2 | yes |
| high | p7_s_zone | 2 | 2 | yes |
| high | p7_s_gacom | 6.94 | 6.94 | yes |
| high | p7_s_garet | 9.95 | 9.95 | yes |
| high | p7_s_pri | 9.32 | 9.32 | yes |
| high | p7_s_upsgs | 18.117 | 18.117 | yes |
| high | p7_s_cheap | 6.94 | 6.94 | yes |
| high | p7_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| high | p7_s_saved | 3.01 | 3.01 | yes |
| high | p7_b_name | Canvas Tote Bag | Canvas Tote Bag | yes |
| high | p7_b_sale | 30 | 30 | yes |
| high | p7_b_ship | 6.95 | 6.95 | yes |
| high | p7_b_true | 9.5 | 9.5 | yes |
| high | p7_b_fees | 4.7103 | 4.7103 | yes |
| high | p7_b_net | 13.2398 | 13.2398 | yes |
| high | p7_b_margin | 0.3583 | 0.3583 | yes |
| high | p7_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p7_b_flag | OK | OK | yes |
| high | p8_postage | 7.69 | 7.69 | yes |
| high | p8_labor | 3 | 3 | yes |
| high | p8_true | 11.55 | 11.55 | yes |
| high | p8_short | -1.6 | -1.6 | yes |
| high | p8_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p8_share | 0.6658 | 0.6658 | yes |
| high | p8_d_name | Handmade Soap Set (3) | Handmade Soap Set (3) | yes |
| high | p8_d_lb | 0.875 | 0.875 | yes |
| high | p8_d_cubic | 105 | 105 | yes |
| high | p8_d_over | no | No | intended: sentence case only, same status word |
| high | p8_d_uspsdim | - | - | yes |
| high | p8_d_uspsbill | 0.875 | 0.875 | yes |
| high | p8_d_upsdim | 0.7554 | 0.7554 | yes |
| high | p8_d_upsbill | 1 | 1 | yes |
| high | p8_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| high | p8_d_upsflag | ok | OK | intended: sentence case only, same status word |
| high | p8_s_usps | 0.875 | 0.875 | yes |
| high | p8_s_ups | 1 | 1 | yes |
| high | p8_s_zone | 5 | 5 | yes |
| high | p8_s_gacom | 7.69 | 7.69 | yes |
| high | p8_s_garet | 10.95 | 10.95 | yes |
| high | p8_s_pri | 12.97 | 12.97 | yes |
| high | p8_s_upsgs | 19.8265 | 19.8265 | yes |
| high | p8_s_cheap | 7.69 | 7.69 | yes |
| high | p8_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| high | p8_s_saved | 3.26 | 3.26 | yes |
| high | p8_b_name | Handmade Soap Set (3) | Handmade Soap Set (3) | yes |
| high | p8_b_sale | 26 | 26 | yes |
| high | p8_b_ship | 9.95 | 9.95 | yes |
| high | p8_b_true | 11.55 | 11.55 | yes |
| high | p8_b_fees | 4.6153 | 4.6153 | yes |
| high | p8_b_net | 13.7848 | 13.7848 | yes |
| high | p8_b_margin | 0.3834 | 0.3834 | yes |
| high | p8_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p8_b_flag | OK | OK | yes |
| high | p9_postage | 8.51 | 8.51 | yes |
| high | p9_labor | 3.75 | 3.75 | yes |
| high | p9_true | 13.65 | 13.65 | yes |
| high | p9_short | -0.7 | -0.7 | yes |
| high | p9_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p9_share | 0.6234 | 0.6234 | yes |
| high | p9_d_name | Wooden Puzzle | Wooden Puzzle | yes |
| high | p9_d_lb | 1.875 | 1.875 | yes |
| high | p9_d_cubic | 160 | 160 | yes |
| high | p9_d_over | no | No | intended: sentence case only, same status word |
| high | p9_d_uspsdim | - | - | yes |
| high | p9_d_uspsbill | 2 | 2 | yes |
| high | p9_d_upsdim | 1.1511 | 1.1511 | yes |
| high | p9_d_upsbill | 2 | 2 | yes |
| high | p9_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| high | p9_d_upsflag | ok | OK | intended: sentence case only, same status word |
| high | p9_s_usps | 2 | 2 | yes |
| high | p9_s_ups | 2 | 2 | yes |
| high | p9_s_zone | 4 | 4 | yes |
| high | p9_s_gacom | 8.51 | 8.51 | yes |
| high | p9_s_garet | 13 | 13 | yes |
| high | p9_s_pri | 10.79 | 10.79 | yes |
| high | p9_s_upsgs | 21.6395 | 21.6395 | yes |
| high | p9_s_cheap | 8.51 | 8.51 | yes |
| high | p9_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| high | p9_s_saved | 4.49 | 4.49 | yes |
| high | p9_b_name | Wooden Puzzle | Wooden Puzzle | yes |
| high | p9_b_sale | 34 | 34 | yes |
| high | p9_b_ship | 12.95 | 12.95 | yes |
| high | p9_b_true | 13.65 | 13.65 | yes |
| high | p9_b_fees | 5.6603 | 5.6603 | yes |
| high | p9_b_net | 18.6398 | 18.6398 | yes |
| high | p9_b_margin | 0.397 | 0.397 | yes |
| high | p9_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p9_b_flag | OK | OK | yes |
| high | p10_postage | 12.84 | 12.84 | yes |
| high | p10_labor | 5.25 | 5.25 | yes |
| high | p10_true | 20 | 20 | yes |
| high | p10_short | -2.05 | -2.05 | yes |
| high | p10_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p10_share | 0.642 | 0.642 | yes |
| high | p10_d_name | Board Game | Board Game | yes |
| high | p10_d_lb | 3.75 | 3.75 | yes |
| high | p10_d_cubic | 432 | 432 | yes |
| high | p10_d_over | no | No | intended: sentence case only, same status word |
| high | p10_d_uspsdim | - | - | yes |
| high | p10_d_uspsbill | 4 | 4 | yes |
| high | p10_d_upsdim | 3.1079 | 3.1079 | yes |
| high | p10_d_upsbill | 4 | 4 | yes |
| high | p10_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| high | p10_d_upsflag | ok | OK | intended: sentence case only, same status word |
| high | p10_s_usps | 4 | 4 | yes |
| high | p10_s_ups | 4 | 4 | yes |
| high | p10_s_zone | 5 | 5 | yes |
| high | p10_s_gacom | 12.84 | 12.84 | yes |
| high | p10_s_garet | 16.4 | 16.4 | yes |
| high | p10_s_pri | 19.88 | 19.88 | yes |
| high | p10_s_upsgs | 24.9287 | 24.9287 | yes |
| high | p10_s_cheap | 12.84 | 12.84 | yes |
| high | p10_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| high | p10_s_saved | 3.56 | 3.56 | yes |
| high | p10_b_name | Board Game | Board Game | yes |
| high | p10_b_sale | 48 | 48 | yes |
| high | p10_b_ship | 17.95 | 17.95 | yes |
| high | p10_b_true | 20 | 20 | yes |
| high | p10_b_fees | 7.4653 | 7.4653 | yes |
| high | p10_b_net | 22.4848 | 22.4848 | yes |
| high | p10_b_margin | 0.3409 | 0.3409 | yes |
| high | p10_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| high | p10_b_flag | OK | OK | yes |
| high | p11_postage | (blank) | (blank) | yes |
| high | p11_labor | (blank) | (blank) | yes |
| high | p11_true | (blank) | (blank) | yes |
| high | p11_short | (blank) | (blank) | yes |
| high | p11_flag | (blank) | (blank) | yes |
| high | p11_share | (blank) | (blank) | yes |
| high | p11_d_name | (blank) | (blank) | yes |
| high | p11_d_lb | (blank) | (blank) | yes |
| high | p11_d_cubic | (blank) | (blank) | yes |
| high | p11_d_over | (blank) | (blank) | yes |
| high | p11_d_uspsdim | (blank) | (blank) | yes |
| high | p11_d_uspsbill | (blank) | (blank) | yes |
| high | p11_d_upsdim | (blank) | (blank) | yes |
| high | p11_d_upsbill | (blank) | (blank) | yes |
| high | p11_d_uspsflag | (blank) | (blank) | yes |
| high | p11_d_upsflag | (blank) | (blank) | yes |
| high | p11_s_usps | (blank) | (blank) | yes |
| high | p11_s_ups | (blank) | (blank) | yes |
| high | p11_s_zone | (blank) | (blank) | yes |
| high | p11_s_gacom | (blank) | (blank) | yes |
| high | p11_s_garet | (blank) | (blank) | yes |
| high | p11_s_pri | (blank) | (blank) | yes |
| high | p11_s_upsgs | (blank) | (blank) | yes |
| high | p11_s_cheap | (blank) | (blank) | yes |
| high | p11_s_cheapname | (blank) | (blank) | yes |
| high | p11_s_saved | (blank) | (blank) | yes |
| high | p11_b_name | (blank) | (blank) | yes |
| high | p11_b_sale | (blank) | (blank) | yes |
| high | p11_b_ship | (blank) | (blank) | yes |
| high | p11_b_true | (blank) | (blank) | yes |
| high | p11_b_fees | (blank) | (blank) | yes |
| high | p11_b_net | (blank) | (blank) | yes |
| high | p11_b_margin | (blank) | (blank) | yes |
| high | p11_b_shipflag | (blank) | (blank) | yes |
| high | p11_b_flag | (blank) | (blank) | yes |
| high | p12_postage | (blank) | (blank) | yes |
| high | p12_labor | (blank) | (blank) | yes |
| high | p12_true | (blank) | (blank) | yes |
| high | p12_short | (blank) | (blank) | yes |
| high | p12_flag | (blank) | (blank) | yes |
| high | p12_share | (blank) | (blank) | yes |
| high | p12_d_name | (blank) | (blank) | yes |
| high | p12_d_lb | (blank) | (blank) | yes |
| high | p12_d_cubic | (blank) | (blank) | yes |
| high | p12_d_over | (blank) | (blank) | yes |
| high | p12_d_uspsdim | (blank) | (blank) | yes |
| high | p12_d_uspsbill | (blank) | (blank) | yes |
| high | p12_d_upsdim | (blank) | (blank) | yes |
| high | p12_d_upsbill | (blank) | (blank) | yes |
| high | p12_d_uspsflag | (blank) | (blank) | yes |
| high | p12_d_upsflag | (blank) | (blank) | yes |
| high | p12_s_usps | (blank) | (blank) | yes |
| high | p12_s_ups | (blank) | (blank) | yes |
| high | p12_s_zone | (blank) | (blank) | yes |
| high | p12_s_gacom | (blank) | (blank) | yes |
| high | p12_s_garet | (blank) | (blank) | yes |
| high | p12_s_pri | (blank) | (blank) | yes |
| high | p12_s_upsgs | (blank) | (blank) | yes |
| high | p12_s_cheap | (blank) | (blank) | yes |
| high | p12_s_cheapname | (blank) | (blank) | yes |
| high | p12_s_saved | (blank) | (blank) | yes |
| high | p12_b_name | (blank) | (blank) | yes |
| high | p12_b_sale | (blank) | (blank) | yes |
| high | p12_b_ship | (blank) | (blank) | yes |
| high | p12_b_true | (blank) | (blank) | yes |
| high | p12_b_fees | (blank) | (blank) | yes |
| high | p12_b_net | (blank) | (blank) | yes |
| high | p12_b_margin | (blank) | (blank) | yes |
| high | p12_b_shipflag | (blank) | (blank) | yes |
| high | p12_b_flag | (blank) | (blank) | yes |
| high | p30_postage | (blank) | (blank) | yes |
| high | p30_labor | (blank) | (blank) | yes |
| high | p30_true | (blank) | (blank) | yes |
| high | p30_short | (blank) | (blank) | yes |
| high | p30_flag | (blank) | (blank) | yes |
| high | p30_share | (blank) | (blank) | yes |
| high | p30_d_name | (blank) | (blank) | yes |
| high | p30_d_lb | (blank) | (blank) | yes |
| high | p30_d_cubic | (blank) | (blank) | yes |
| high | p30_d_over | (blank) | (blank) | yes |
| high | p30_d_uspsdim | (blank) | (blank) | yes |
| high | p30_d_uspsbill | (blank) | (blank) | yes |
| high | p30_d_upsdim | (blank) | (blank) | yes |
| high | p30_d_upsbill | (blank) | (blank) | yes |
| high | p30_d_uspsflag | (blank) | (blank) | yes |
| high | p30_d_upsflag | (blank) | (blank) | yes |
| high | p30_s_usps | (blank) | (blank) | yes |
| high | p30_s_ups | (blank) | (blank) | yes |
| high | p30_s_zone | (blank) | (blank) | yes |
| high | p30_s_gacom | (blank) | (blank) | yes |
| high | p30_s_garet | (blank) | (blank) | yes |
| high | p30_s_pri | (blank) | (blank) | yes |
| high | p30_s_upsgs | (blank) | (blank) | yes |
| high | p30_s_cheap | (blank) | (blank) | yes |
| high | p30_s_cheapname | (blank) | (blank) | yes |
| high | p30_s_saved | (blank) | (blank) | yes |
| high | p30_b_name | (blank) | (blank) | yes |
| high | p30_b_sale | (blank) | (blank) | yes |
| high | p30_b_ship | (blank) | (blank) | yes |
| high | p30_b_true | (blank) | (blank) | yes |
| high | p30_b_fees | (blank) | (blank) | yes |
| high | p30_b_net | (blank) | (blank) | yes |
| high | p30_b_margin | (blank) | (blank) | yes |
| high | p30_b_shipflag | (blank) | (blank) | yes |
| high | p30_b_flag | (blank) | (blank) | yes |
| high | avg_true | 22.122 | 22.122 | yes |
| high | avg_short | -12.762 | -12.762 | yes |
| high | avg_share | 0.6478 | 0.6478 | yes |
| high | sc_cheap_total | 126.06 | 126.06 | yes |
| high | sc_saved_total | 60.19 | 60.19 | yes |
| high | db_losing | 3 | 3 | yes |
| high | db_under | 10 | 10 | yes |
| high | db_avgtrue | 22.122 | 22.122 | yes |
| high | db_avgshort | -12.762 | -12.762 | yes |
| high | db_shipcost | 221.22 | 221.22 | yes |
| high | db_collected | 93.6 | 93.6 | yes |
| high | db_netship | -127.62 | -127.62 | yes |
| high | db_share | 0.6478 | 0.6478 | yes |
| high | db_tot_true | 221.22 | 221.22 | yes |
| high | db_tot_fees | 59.6917 | 59.6917 | yes |
| high | db_tot_net | 67.0883 | 67.0883 | yes |
| high | fs_tc | 22.122 | 22.122 | yes |
| high | fs_tcused | 22.122 | 22.122 | yes |
| high | fs_profit_order | 43.878 | 43.878 | yes |
| high | fs_cost | 12 | 12 | yes |
| high | fs_breakeven | 146.6667 | 146.6667 | yes |
| high | fs_recommendation | Best of the three: free shipping over $150, about $2,096 more profit per 100 orders than today. An estimate built on your assumptions above, not a promise. | Best of the three: free shipping over $150, about $2,096 more profit per 100 orders than today. An estimate built on your assumptions above, not a promise. | yes |
| high | fs_avgo_today | 120 | 120 | yes |
| high | fs_avgo_s1 | 120 | 120 | yes |
| high | fs_avgo_s2 | 120 | 120 | yes |
| high | fs_avgo_s3 | 120 | 120 | yes |
| high | fs_orders_today | 100 | 100 | yes |
| high | fs_orders_s1 | 130 | 130 | yes |
| high | fs_orders_s2 | 130 | 130 | yes |
| high | fs_orders_s3 | 130 | 130 | yes |
| high | fs_qual_today | 0 | 0 | yes |
| high | fs_qual_s1 | 71.5 | 71.5 | yes |
| high | fs_qual_s2 | 39 | 39 | yes |
| high | fs_qual_s3 | 52 | 52 | yes |
| high | fs_other_today | 100 | 100 | yes |
| high | fs_other_s1 | 58.5 | 58.5 | yes |
| high | fs_other_s2 | 91 | 91 | yes |
| high | fs_other_s3 | 78 | 78 | yes |
| high | fs_rev_today | 12,000 | 12,000 | yes |
| high | fs_rev_s1 | 10,595 | 10,595 | yes |
| high | fs_rev_s2 | 13,416 | 13,416 | yes |
| high | fs_rev_s3 | 18,720 | 18,720 | yes |
| high | fs_coll_today | 1,200 | 1,200 | yes |
| high | fs_coll_s1 | 702 | 702 | yes |
| high | fs_coll_s2 | 1,092 | 1,092 | yes |
| high | fs_coll_s3 | 936 | 936 | yes |
| high | fs_parc_today | 2,212.2 | 2,212.2 | yes |
| high | fs_parc_s1 | 2,875.86 | 2,875.86 | yes |
| high | fs_parc_s2 | 2,875.86 | 2,875.86 | yes |
| high | fs_parc_s3 | 2,875.86 | 2,875.86 | yes |
| high | fs_profit_today | 4,387.8 | 4,387.8 | yes |
| high | fs_profit_s1 | 2,593.89 | 2,593.89 | yes |
| high | fs_profit_s2 | 4,253.34 | 4,253.34 | yes |
| high | fs_profit_s3 | 6,484.14 | 6,484.14 | yes |
| high | fs_per_today | 43.878 | 43.878 | yes |
| high | fs_per_s1 | 19.953 | 19.953 | yes |
| high | fs_per_s2 | 32.718 | 32.718 | yes |
| high | fs_per_s3 | 49.878 | 49.878 | yes |
| high | fs_chg_today | 0 | 0 | yes |
| high | fs_chg_s1 | -1,793.91 | -1,793.91 | yes |
| high | fs_chg_s2 | -134.46 | -134.46 | yes |
| high | fs_chg_s3 | 2,096.34 | 2,096.34 | yes |
| high | fs_verdict_today | baseline | Today | intended: baseline column now reads Today |
| high | fs_verdict_s1 | WORSE THAN TODAY | Worse than today | intended: sentence case only, same status word |
| high | fs_verdict_s2 | WORSE THAN TODAY | Worse than today | intended: sentence case only, same status word |
| high | fs_verdict_s3 | BEATS TODAY | Beats today | intended: sentence case only, same status word |
| low | p1_postage | 7.99 | 7.99 | yes |
| low | p1_labor | 0 | 0 | yes |
| low | p1_true | 9.43 | 9.43 | yes |
| low | p1_short | -4.48 | -4.48 | yes |
| low | p1_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| low | p1_share | 0.8473 | 0.8473 | yes |
| low | p1_d_name | Ceramic Mug 12 oz | Ceramic Mug 12 oz | yes |
| low | p1_d_lb | 1.125 | 1.125 | yes |
| low | p1_d_cubic | 288 | 288 | yes |
| low | p1_d_over | no | No | intended: sentence case only, same status word |
| low | p1_d_uspsdim | - | - | yes |
| low | p1_d_uspsbill | 2 | 2 | yes |
| low | p1_d_upsdim | 2.0719 | 2.0719 | yes |
| low | p1_d_upsbill | 3 | 3 | yes |
| low | p1_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| low | p1_d_upsflag | DIM WEIGHT BITES: +1 lb | Dim weight bites: +1 lb | intended: sentence case only, same status word |
| low | p1_s_usps | 2 | 2 | yes |
| low | p1_s_ups | 3 | 3 | yes |
| low | p1_s_zone | 1 | 1 | yes |
| low | p1_s_gacom | 7.99 | 7.99 | yes |
| low | p1_s_garet | 10.8 | 10.8 | yes |
| low | p1_s_pri | 9.1 | 9.1 | yes |
| low | p1_s_upsgs | 14.54 | 14.54 | yes |
| low | p1_s_cheap | 7.99 | 7.99 | yes |
| low | p1_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| low | p1_s_saved | 2.81 | 2.81 | yes |
| low | p1_b_name | Ceramic Mug 12 oz | Ceramic Mug 12 oz | yes |
| low | p1_b_sale | 19 | 19 | yes |
| low | p1_b_ship | 4.95 | 4.95 | yes |
| low | p1_b_true | 9.43 | 9.43 | yes |
| low | p1_b_fees | 2.2752 | 2.2752 | yes |
| low | p1_b_net | 3.7447 | 3.7447 | yes |
| low | p1_b_margin | 0.1564 | 0.1564 | yes |
| low | p1_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| low | p1_b_flag | OK | OK | yes |
| low | p2_postage | 6.93 | 6.93 | yes |
| low | p2_labor | 0 | 0 | yes |
| low | p2_true | 7.21 | 7.21 | yes |
| low | p2_short | -2.26 | -2.26 | yes |
| low | p2_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| low | p2_share | 0.9612 | 0.9612 | yes |
| low | p2_d_name | Graphic T-Shirt | Graphic T-Shirt | yes |
| low | p2_d_lb | 0.4375 | 0.4375 | yes |
| low | p2_d_cubic | 130 | 130 | yes |
| low | p2_d_over | no | No | intended: sentence case only, same status word |
| low | p2_d_uspsdim | - | - | yes |
| low | p2_d_uspsbill | 0.4375 | 0.4375 | yes |
| low | p2_d_upsdim | 0.9353 | 0.9353 | yes |
| low | p2_d_upsbill | 1 | 1 | yes |
| low | p2_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| low | p2_d_upsflag | ok | OK | intended: sentence case only, same status word |
| low | p2_s_usps | 0.4375 | 0.4375 | yes |
| low | p2_s_ups | 1 | 1 | yes |
| low | p2_s_zone | 1 | 1 | yes |
| low | p2_s_gacom | 6.93 | 6.93 | yes |
| low | p2_s_garet | 7.9 | 7.9 | yes |
| low | p2_s_pri | 9.04 | 9.04 | yes |
| low | p2_s_upsgs | 13 | 13 | yes |
| low | p2_s_cheap | 6.93 | 6.93 | yes |
| low | p2_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| low | p2_s_saved | 0.97 | 0.97 | yes |
| low | p2_b_name | Graphic T-Shirt | Graphic T-Shirt | yes |
| low | p2_b_sale | 28 | 28 | yes |
| low | p2_b_ship | 4.95 | 4.95 | yes |
| low | p2_b_true | 7.21 | 7.21 | yes |
| low | p2_b_fees | 3.1303 | 3.1303 | yes |
| low | p2_b_net | 10.6098 | 10.6098 | yes |
| low | p2_b_margin | 0.322 | 0.322 | yes |
| low | p2_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| low | p2_b_flag | OK | OK | yes |
| low | p3_postage | 9.34 | 9.34 | yes |
| low | p3_labor | 0 | 0 | yes |
| low | p3_true | 13.05 | 13.05 | yes |
| low | p3_short | -1.05 | -1.05 | yes |
| low | p3_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| low | p3_share | 0.7157 | 0.7157 | yes |
| low | p3_d_name | Framed Print 11x14 | Framed Print 11x14 | yes |
| low | p3_d_lb | 3.25 | 3.25 | yes |
| low | p3_d_cubic | 756 | 756 | yes |
| low | p3_d_over | no | No | intended: sentence case only, same status word |
| low | p3_d_uspsdim | - | - | yes |
| low | p3_d_uspsbill | 4 | 4 | yes |
| low | p3_d_upsdim | 5.4388 | 5.4388 | yes |
| low | p3_d_upsbill | 6 | 6 | yes |
| low | p3_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| low | p3_d_upsflag | DIM WEIGHT BITES: +2 lb | Dim weight bites: +2 lb | intended: sentence case only, same status word |
| low | p3_s_usps | 4 | 4 | yes |
| low | p3_s_ups | 6 | 6 | yes |
| low | p3_s_zone | 2 | 2 | yes |
| low | p3_s_gacom | 9.34 | 9.34 | yes |
| low | p3_s_garet | 12.75 | 12.75 | yes |
| low | p3_s_pri | 11.22 | 11.22 | yes |
| low | p3_s_upsgs | 15.44 | 15.44 | yes |
| low | p3_s_cheap | 9.34 | 9.34 | yes |
| low | p3_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| low | p3_s_saved | 3.41 | 3.41 | yes |
| low | p3_b_name | Framed Print 11x14 | Framed Print 11x14 | yes |
| low | p3_b_sale | 65 | 65 | yes |
| low | p3_b_ship | 12 | 12 | yes |
| low | p3_b_true | 13.05 | 13.05 | yes |
| low | p3_b_fees | 7.315 | 7.315 | yes |
| low | p3_b_net | 34.635 | 34.635 | yes |
| low | p3_b_margin | 0.4498 | 0.4498 | yes |
| low | p3_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| low | p3_b_flag | OK | OK | yes |
| low | p4_postage | 8.4 | 8.4 | yes |
| low | p4_labor | 0 | 0 | yes |
| low | p4_true | 8.86 | 8.86 | yes |
| low | p4_short | -8.86 | -8.86 | yes |
| low | p4_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| low | p4_share | 0.9481 | 0.9481 | yes |
| low | p4_d_name | Sterling Silver Earrings | Sterling Silver Earrings | yes |
| low | p4_d_lb | 0.0625 | 0.0625 | yes |
| low | p4_d_cubic | 54 | 54 | yes |
| low | p4_d_over | no | No | intended: sentence case only, same status word |
| low | p4_d_uspsdim | - | - | yes |
| low | p4_d_uspsbill | 0.0625 | 0.0625 | yes |
| low | p4_d_upsdim | 0.3885 | 0.3885 | yes |
| low | p4_d_upsbill | 1 | 1 | yes |
| low | p4_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| low | p4_d_upsflag | ok | OK | intended: sentence case only, same status word |
| low | p4_s_usps | 0.0625 | 0.0625 | yes |
| low | p4_s_ups | 1 | 1 | yes |
| low | p4_s_zone | 8 | 8 | yes |
| low | p4_s_gacom | 8.4 | 8.4 | yes |
| low | p4_s_garet | 9.45 | 9.45 | yes |
| low | p4_s_pri | 15.22 | 15.22 | yes |
| low | p4_s_upsgs | 16.26 | 16.26 | yes |
| low | p4_s_cheap | 8.4 | 8.4 | yes |
| low | p4_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| low | p4_s_saved | 1.05 | 1.05 | yes |
| low | p4_b_name | Sterling Silver Earrings | Sterling Silver Earrings | yes |
| low | p4_b_sale | 42 | 42 | yes |
| low | p4_b_ship | 0 | 0 | yes |
| low | p4_b_true | 8.86 | 8.86 | yes |
| low | p4_b_fees | 3.99 | 3.99 | yes |
| low | p4_b_net | 18.15 | 18.15 | yes |
| low | p4_b_margin | 0.4321 | 0.4321 | yes |
| low | p4_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| low | p4_b_flag | OK | OK | yes |
| low | p5_postage | 8.51 | 8.51 | yes |
| low | p5_labor | 0 | 0 | yes |
| low | p5_true | 9.75 | 9.75 | yes |
| low | p5_short | -0.8 | -0.8 | yes |
| low | p5_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| low | p5_share | 0.8728 | 0.8728 | yes |
| low | p5_d_name | Soy Candle 8 oz | Soy Candle 8 oz | yes |
| low | p5_d_lb | 1.25 | 1.25 | yes |
| low | p5_d_cubic | 216 | 216 | yes |
| low | p5_d_over | no | No | intended: sentence case only, same status word |
| low | p5_d_uspsdim | - | - | yes |
| low | p5_d_uspsbill | 2 | 2 | yes |
| low | p5_d_upsdim | 1.554 | 1.554 | yes |
| low | p5_d_upsbill | 2 | 2 | yes |
| low | p5_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| low | p5_d_upsflag | ok | OK | intended: sentence case only, same status word |
| low | p5_s_usps | 2 | 2 | yes |
| low | p5_s_ups | 2 | 2 | yes |
| low | p5_s_zone | 4 | 4 | yes |
| low | p5_s_gacom | 8.51 | 8.51 | yes |
| low | p5_s_garet | 13 | 13 | yes |
| low | p5_s_pri | 10.79 | 10.79 | yes |
| low | p5_s_upsgs | 16.71 | 16.71 | yes |
| low | p5_s_cheap | 8.51 | 8.51 | yes |
| low | p5_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| low | p5_s_saved | 4.49 | 4.49 | yes |
| low | p5_b_name | Soy Candle 8 oz | Soy Candle 8 oz | yes |
| low | p5_b_sale | 22 | 22 | yes |
| low | p5_b_ship | 8.95 | 8.95 | yes |
| low | p5_b_true | 9.75 | 9.75 | yes |
| low | p5_b_fees | 2.9402 | 2.9402 | yes |
| low | p5_b_net | 18.2598 | 18.2598 | yes |
| low | p5_b_margin | 0.59 | 0.59 | yes |
| low | p5_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| low | p5_b_flag | OK | OK | yes |
| low | p6_postage | 21.15 | 21.15 | yes |
| low | p6_labor | 0 | 0 | yes |
| low | p6_true | 25.21 | 25.21 | yes |
| low | p6_short | -10.26 | -10.26 | yes |
| low | p6_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| low | p6_share | 0.839 | 0.839 | yes |
| low | p6_d_name | Grapevine Wreath 16 in | Grapevine Wreath 16 in | yes |
| low | p6_d_lb | 2.5 | 2.5 | yes |
| low | p6_d_cubic | 2,048 | 2,048 | yes |
| low | p6_d_over | YES | Yes | intended: sentence case only, same status word |
| low | p6_d_uspsdim | 14.7338 | 14.7338 | yes |
| low | p6_d_uspsbill | 15 | 15 | yes |
| low | p6_d_upsdim | 14.7338 | 14.7338 | yes |
| low | p6_d_upsbill | 15 | 15 | yes |
| low | p6_d_uspsflag | DIM WEIGHT BITES: +12 lb | Dim weight bites: +12 lb | intended: sentence case only, same status word |
| low | p6_d_upsflag | DIM WEIGHT BITES: +12 lb | Dim weight bites: +12 lb | intended: sentence case only, same status word |
| low | p6_s_usps | 15 | 15 | yes |
| low | p6_s_ups | 15 | 15 | yes |
| low | p6_s_zone | 5 | 5 | yes |
| low | p6_s_gacom | 21.15 | 21.15 | yes |
| low | p6_s_garet | 28.95 | 28.95 | yes |
| low | p6_s_pri | 35.25 | 35.25 | yes |
| low | p6_s_upsgs | 30.86 | 30.86 | yes |
| low | p6_s_cheap | 21.15 | 21.15 | yes |
| low | p6_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| low | p6_s_saved | 7.8 | 7.8 | yes |
| low | p6_b_name | Grapevine Wreath 16 in | Grapevine Wreath 16 in | yes |
| low | p6_b_sale | 58 | 58 | yes |
| low | p6_b_ship | 14.95 | 14.95 | yes |
| low | p6_b_true | 25.21 | 25.21 | yes |
| low | p6_b_fees | 6.9303 | 6.9303 | yes |
| low | p6_b_net | 22.8098 | 22.8098 | yes |
| low | p6_b_margin | 0.3127 | 0.3127 | yes |
| low | p6_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| low | p6_b_flag | OK | OK | yes |
| low | p7_postage | 6.94 | 6.94 | yes |
| low | p7_labor | 0 | 0 | yes |
| low | p7_true | 7.25 | 7.25 | yes |
| low | p7_short | -0.3 | -0.3 | yes |
| low | p7_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| low | p7_share | 0.9572 | 0.9572 | yes |
| low | p7_d_name | Canvas Tote Bag | Canvas Tote Bag | yes |
| low | p7_d_lb | 0.5625 | 0.5625 | yes |
| low | p7_d_cubic | 180 | 180 | yes |
| low | p7_d_over | no | No | intended: sentence case only, same status word |
| low | p7_d_uspsdim | - | - | yes |
| low | p7_d_uspsbill | 0.5625 | 0.5625 | yes |
| low | p7_d_upsdim | 1.295 | 1.295 | yes |
| low | p7_d_upsbill | 2 | 2 | yes |
| low | p7_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| low | p7_d_upsflag | DIM WEIGHT BITES: +1 lb | Dim weight bites: +1 lb | intended: sentence case only, same status word |
| low | p7_s_usps | 0.5625 | 0.5625 | yes |
| low | p7_s_ups | 2 | 2 | yes |
| low | p7_s_zone | 2 | 2 | yes |
| low | p7_s_gacom | 6.94 | 6.94 | yes |
| low | p7_s_garet | 9.95 | 9.95 | yes |
| low | p7_s_pri | 9.32 | 9.32 | yes |
| low | p7_s_upsgs | 13.99 | 13.99 | yes |
| low | p7_s_cheap | 6.94 | 6.94 | yes |
| low | p7_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| low | p7_s_saved | 3.01 | 3.01 | yes |
| low | p7_b_name | Canvas Tote Bag | Canvas Tote Bag | yes |
| low | p7_b_sale | 30 | 30 | yes |
| low | p7_b_ship | 6.95 | 6.95 | yes |
| low | p7_b_true | 7.25 | 7.25 | yes |
| low | p7_b_fees | 3.5103 | 3.5103 | yes |
| low | p7_b_net | 16.6898 | 16.6898 | yes |
| low | p7_b_margin | 0.4517 | 0.4517 | yes |
| low | p7_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| low | p7_b_flag | OK | OK | yes |
| low | p8_postage | 7.69 | 7.69 | yes |
| low | p8_labor | 0 | 0 | yes |
| low | p8_true | 8.55 | 8.55 | yes |
| low | p8_short | 1.4 | 1.4 | yes |
| low | p8_flag | COVERED | Covered | intended: sentence case only, same status word |
| low | p8_share | 0.8994 | 0.8994 | yes |
| low | p8_d_name | Handmade Soap Set (3) | Handmade Soap Set (3) | yes |
| low | p8_d_lb | 0.875 | 0.875 | yes |
| low | p8_d_cubic | 105 | 105 | yes |
| low | p8_d_over | no | No | intended: sentence case only, same status word |
| low | p8_d_uspsdim | - | - | yes |
| low | p8_d_uspsbill | 0.875 | 0.875 | yes |
| low | p8_d_upsdim | 0.7554 | 0.7554 | yes |
| low | p8_d_upsbill | 1 | 1 | yes |
| low | p8_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| low | p8_d_upsflag | ok | OK | intended: sentence case only, same status word |
| low | p8_s_usps | 0.875 | 0.875 | yes |
| low | p8_s_ups | 1 | 1 | yes |
| low | p8_s_zone | 5 | 5 | yes |
| low | p8_s_gacom | 7.69 | 7.69 | yes |
| low | p8_s_garet | 10.95 | 10.95 | yes |
| low | p8_s_pri | 12.97 | 12.97 | yes |
| low | p8_s_upsgs | 15.31 | 15.31 | yes |
| low | p8_s_cheap | 7.69 | 7.69 | yes |
| low | p8_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| low | p8_s_saved | 3.26 | 3.26 | yes |
| low | p8_b_name | Handmade Soap Set (3) | Handmade Soap Set (3) | yes |
| low | p8_b_sale | 26 | 26 | yes |
| low | p8_b_ship | 9.95 | 9.95 | yes |
| low | p8_b_true | 8.55 | 8.55 | yes |
| low | p8_b_fees | 3.4153 | 3.4153 | yes |
| low | p8_b_net | 17.9848 | 17.9848 | yes |
| low | p8_b_margin | 0.5003 | 0.5003 | yes |
| low | p8_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| low | p8_b_flag | OK | OK | yes |
| low | p9_postage | 8.51 | 8.51 | yes |
| low | p9_labor | 0 | 0 | yes |
| low | p9_true | 9.9 | 9.9 | yes |
| low | p9_short | 3.05 | 3.05 | yes |
| low | p9_flag | COVERED | Covered | intended: sentence case only, same status word |
| low | p9_share | 0.8596 | 0.8596 | yes |
| low | p9_d_name | Wooden Puzzle | Wooden Puzzle | yes |
| low | p9_d_lb | 1.875 | 1.875 | yes |
| low | p9_d_cubic | 160 | 160 | yes |
| low | p9_d_over | no | No | intended: sentence case only, same status word |
| low | p9_d_uspsdim | - | - | yes |
| low | p9_d_uspsbill | 2 | 2 | yes |
| low | p9_d_upsdim | 1.1511 | 1.1511 | yes |
| low | p9_d_upsbill | 2 | 2 | yes |
| low | p9_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| low | p9_d_upsflag | ok | OK | intended: sentence case only, same status word |
| low | p9_s_usps | 2 | 2 | yes |
| low | p9_s_ups | 2 | 2 | yes |
| low | p9_s_zone | 4 | 4 | yes |
| low | p9_s_gacom | 8.51 | 8.51 | yes |
| low | p9_s_garet | 13 | 13 | yes |
| low | p9_s_pri | 10.79 | 10.79 | yes |
| low | p9_s_upsgs | 16.71 | 16.71 | yes |
| low | p9_s_cheap | 8.51 | 8.51 | yes |
| low | p9_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| low | p9_s_saved | 4.49 | 4.49 | yes |
| low | p9_b_name | Wooden Puzzle | Wooden Puzzle | yes |
| low | p9_b_sale | 34 | 34 | yes |
| low | p9_b_ship | 12.95 | 12.95 | yes |
| low | p9_b_true | 9.9 | 9.9 | yes |
| low | p9_b_fees | 4.4603 | 4.4603 | yes |
| low | p9_b_net | 23.5898 | 23.5898 | yes |
| low | p9_b_margin | 0.5024 | 0.5024 | yes |
| low | p9_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| low | p9_b_flag | OK | OK | yes |
| low | p10_postage | 9.28 | 9.28 | yes |
| low | p10_labor | 0 | 0 | yes |
| low | p10_true | 11.19 | 11.19 | yes |
| low | p10_short | 6.76 | 6.76 | yes |
| low | p10_flag | COVERED | Covered | intended: sentence case only, same status word |
| low | p10_share | 0.8293 | 0.8293 | yes |
| low | p10_d_name | Board Game | Board Game | yes |
| low | p10_d_lb | 3.75 | 3.75 | yes |
| low | p10_d_cubic | 432 | 432 | yes |
| low | p10_d_over | no | No | intended: sentence case only, same status word |
| low | p10_d_uspsdim | - | - | yes |
| low | p10_d_uspsbill | 4 | 4 | yes |
| low | p10_d_upsdim | 3.1079 | 3.1079 | yes |
| low | p10_d_upsbill | 4 | 4 | yes |
| low | p10_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| low | p10_d_upsflag | ok | OK | intended: sentence case only, same status word |
| low | p10_s_usps | 4 | 4 | yes |
| low | p10_s_ups | 4 | 4 | yes |
| low | p10_s_zone | 1 | 1 | yes |
| low | p10_s_gacom | 9.28 | 9.28 | yes |
| low | p10_s_garet | 12.25 | 12.25 | yes |
| low | p10_s_pri | 10.97 | 10.97 | yes |
| low | p10_s_upsgs | 14.94 | 14.94 | yes |
| low | p10_s_cheap | 9.28 | 9.28 | yes |
| low | p10_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| low | p10_s_saved | 2.97 | 2.97 | yes |
| low | p10_b_name | Board Game | Board Game | yes |
| low | p10_b_sale | 48 | 48 | yes |
| low | p10_b_ship | 17.95 | 17.95 | yes |
| low | p10_b_true | 11.19 | 11.19 | yes |
| low | p10_b_fees | 6.2652 | 6.2652 | yes |
| low | p10_b_net | 32.4948 | 32.4948 | yes |
| low | p10_b_margin | 0.4927 | 0.4927 | yes |
| low | p10_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| low | p10_b_flag | OK | OK | yes |
| low | p11_postage | (blank) | (blank) | yes |
| low | p11_labor | (blank) | (blank) | yes |
| low | p11_true | (blank) | (blank) | yes |
| low | p11_short | (blank) | (blank) | yes |
| low | p11_flag | (blank) | (blank) | yes |
| low | p11_share | (blank) | (blank) | yes |
| low | p11_d_name | (blank) | (blank) | yes |
| low | p11_d_lb | (blank) | (blank) | yes |
| low | p11_d_cubic | (blank) | (blank) | yes |
| low | p11_d_over | (blank) | (blank) | yes |
| low | p11_d_uspsdim | (blank) | (blank) | yes |
| low | p11_d_uspsbill | (blank) | (blank) | yes |
| low | p11_d_upsdim | (blank) | (blank) | yes |
| low | p11_d_upsbill | (blank) | (blank) | yes |
| low | p11_d_uspsflag | (blank) | (blank) | yes |
| low | p11_d_upsflag | (blank) | (blank) | yes |
| low | p11_s_usps | (blank) | (blank) | yes |
| low | p11_s_ups | (blank) | (blank) | yes |
| low | p11_s_zone | (blank) | (blank) | yes |
| low | p11_s_gacom | (blank) | (blank) | yes |
| low | p11_s_garet | (blank) | (blank) | yes |
| low | p11_s_pri | (blank) | (blank) | yes |
| low | p11_s_upsgs | (blank) | (blank) | yes |
| low | p11_s_cheap | (blank) | (blank) | yes |
| low | p11_s_cheapname | (blank) | (blank) | yes |
| low | p11_s_saved | (blank) | (blank) | yes |
| low | p11_b_name | (blank) | (blank) | yes |
| low | p11_b_sale | (blank) | (blank) | yes |
| low | p11_b_ship | (blank) | (blank) | yes |
| low | p11_b_true | (blank) | (blank) | yes |
| low | p11_b_fees | (blank) | (blank) | yes |
| low | p11_b_net | (blank) | (blank) | yes |
| low | p11_b_margin | (blank) | (blank) | yes |
| low | p11_b_shipflag | (blank) | (blank) | yes |
| low | p11_b_flag | (blank) | (blank) | yes |
| low | p12_postage | (blank) | (blank) | yes |
| low | p12_labor | (blank) | (blank) | yes |
| low | p12_true | (blank) | (blank) | yes |
| low | p12_short | (blank) | (blank) | yes |
| low | p12_flag | (blank) | (blank) | yes |
| low | p12_share | (blank) | (blank) | yes |
| low | p12_d_name | (blank) | (blank) | yes |
| low | p12_d_lb | (blank) | (blank) | yes |
| low | p12_d_cubic | (blank) | (blank) | yes |
| low | p12_d_over | (blank) | (blank) | yes |
| low | p12_d_uspsdim | (blank) | (blank) | yes |
| low | p12_d_uspsbill | (blank) | (blank) | yes |
| low | p12_d_upsdim | (blank) | (blank) | yes |
| low | p12_d_upsbill | (blank) | (blank) | yes |
| low | p12_d_uspsflag | (blank) | (blank) | yes |
| low | p12_d_upsflag | (blank) | (blank) | yes |
| low | p12_s_usps | (blank) | (blank) | yes |
| low | p12_s_ups | (blank) | (blank) | yes |
| low | p12_s_zone | (blank) | (blank) | yes |
| low | p12_s_gacom | (blank) | (blank) | yes |
| low | p12_s_garet | (blank) | (blank) | yes |
| low | p12_s_pri | (blank) | (blank) | yes |
| low | p12_s_upsgs | (blank) | (blank) | yes |
| low | p12_s_cheap | (blank) | (blank) | yes |
| low | p12_s_cheapname | (blank) | (blank) | yes |
| low | p12_s_saved | (blank) | (blank) | yes |
| low | p12_b_name | (blank) | (blank) | yes |
| low | p12_b_sale | (blank) | (blank) | yes |
| low | p12_b_ship | (blank) | (blank) | yes |
| low | p12_b_true | (blank) | (blank) | yes |
| low | p12_b_fees | (blank) | (blank) | yes |
| low | p12_b_net | (blank) | (blank) | yes |
| low | p12_b_margin | (blank) | (blank) | yes |
| low | p12_b_shipflag | (blank) | (blank) | yes |
| low | p12_b_flag | (blank) | (blank) | yes |
| low | p30_postage | (blank) | (blank) | yes |
| low | p30_labor | (blank) | (blank) | yes |
| low | p30_true | (blank) | (blank) | yes |
| low | p30_short | (blank) | (blank) | yes |
| low | p30_flag | (blank) | (blank) | yes |
| low | p30_share | (blank) | (blank) | yes |
| low | p30_d_name | (blank) | (blank) | yes |
| low | p30_d_lb | (blank) | (blank) | yes |
| low | p30_d_cubic | (blank) | (blank) | yes |
| low | p30_d_over | (blank) | (blank) | yes |
| low | p30_d_uspsdim | (blank) | (blank) | yes |
| low | p30_d_uspsbill | (blank) | (blank) | yes |
| low | p30_d_upsdim | (blank) | (blank) | yes |
| low | p30_d_upsbill | (blank) | (blank) | yes |
| low | p30_d_uspsflag | (blank) | (blank) | yes |
| low | p30_d_upsflag | (blank) | (blank) | yes |
| low | p30_s_usps | (blank) | (blank) | yes |
| low | p30_s_ups | (blank) | (blank) | yes |
| low | p30_s_zone | (blank) | (blank) | yes |
| low | p30_s_gacom | (blank) | (blank) | yes |
| low | p30_s_garet | (blank) | (blank) | yes |
| low | p30_s_pri | (blank) | (blank) | yes |
| low | p30_s_upsgs | (blank) | (blank) | yes |
| low | p30_s_cheap | (blank) | (blank) | yes |
| low | p30_s_cheapname | (blank) | (blank) | yes |
| low | p30_s_saved | (blank) | (blank) | yes |
| low | p30_b_name | (blank) | (blank) | yes |
| low | p30_b_sale | (blank) | (blank) | yes |
| low | p30_b_ship | (blank) | (blank) | yes |
| low | p30_b_true | (blank) | (blank) | yes |
| low | p30_b_fees | (blank) | (blank) | yes |
| low | p30_b_net | (blank) | (blank) | yes |
| low | p30_b_margin | (blank) | (blank) | yes |
| low | p30_b_shipflag | (blank) | (blank) | yes |
| low | p30_b_flag | (blank) | (blank) | yes |
| low | avg_true | 11.04 | 11.04 | yes |
| low | avg_short | -1.68 | -1.68 | yes |
| low | avg_share | 0.873 | 0.873 | yes |
| low | sc_cheap_total | 94.74 | 94.74 | yes |
| low | sc_saved_total | 34.26 | 34.26 | yes |
| low | db_losing | 0 | 0 | yes |
| low | db_under | 7 | 7 | yes |
| low | db_avgtrue | 11.04 | 11.04 | yes |
| low | db_avgshort | -1.68 | -1.68 | yes |
| low | db_shipcost | 110.4 | 110.4 | yes |
| low | db_collected | 93.6 | 93.6 | yes |
| low | db_netship | -16.8 | -16.8 | yes |
| low | db_share | 0.873 | 0.873 | yes |
| low | db_tot_true | 110.4 | 110.4 | yes |
| low | db_tot_fees | 44.232 | 44.232 | yes |
| low | db_tot_net | 198.968 | 198.968 | yes |
| low | fs_tc | 11.04 | 11.04 | yes |
| low | fs_tcused | 11.04 | 11.04 | yes |
| low | fs_profit_order | -2.14 | -2.14 | yes |
| low | fs_cost | 6.5 | 6.5 | yes |
| low | fs_breakeven | 178 | 178 | yes |
| low | fs_recommendation | Keep charging shipping. With these assumptions, none of the three thresholds beats what you earn today. | Keep charging shipping. With these assumptions, none of the three thresholds beats what you earn today. | yes |
| low | fs_avgo_today | 48 | 48 | yes |
| low | fs_avgo_s1 | 48 | 48 | yes |
| low | fs_avgo_s2 | 48 | 48 | yes |
| low | fs_avgo_s3 | 48 | 48 | yes |
| low | fs_orders_today | 100 | 100 | yes |
| low | fs_orders_s1 | 100 | 100 | yes |
| low | fs_orders_s2 | 100 | 100 | yes |
| low | fs_orders_s3 | 100 | 100 | yes |
| low | fs_qual_today | 0 | 0 | yes |
| low | fs_qual_s1 | 55 | 55 | yes |
| low | fs_qual_s2 | 30 | 30 | yes |
| low | fs_qual_s3 | 12 | 12 | yes |
| low | fs_other_today | 100 | 100 | yes |
| low | fs_other_s1 | 45 | 45 | yes |
| low | fs_other_s2 | 70 | 70 | yes |
| low | fs_other_s3 | 88 | 88 | yes |
| low | fs_rev_today | 4,800 | 4,800 | yes |
| low | fs_rev_s1 | 4,910 | 4,910 | yes |
| low | fs_rev_s2 | 5,280 | 5,280 | yes |
| low | fs_rev_s3 | 5,328 | 5,328 | yes |
| low | fs_coll_today | 650 | 650 | yes |
| low | fs_coll_s1 | 292.5 | 292.5 | yes |
| low | fs_coll_s2 | 455 | 455 | yes |
| low | fs_coll_s3 | 572 | 572 | yes |
| low | fs_parc_today | 1,104 | 1,104 | yes |
| low | fs_parc_s1 | 1,104 | 1,104 | yes |
| low | fs_parc_s2 | 1,104 | 1,104 | yes |
| low | fs_parc_s3 | 1,104 | 1,104 | yes |
| low | fs_profit_today | -214 | -214 | yes |
| low | fs_profit_s1 | -566 | -566 | yes |
| low | fs_profit_s2 | -385 | -385 | yes |
| low | fs_profit_s3 | -265.6 | -265.6 | yes |
| low | fs_per_today | -2.14 | -2.14 | yes |
| low | fs_per_s1 | -5.66 | -5.66 | yes |
| low | fs_per_s2 | -3.85 | -3.85 | yes |
| low | fs_per_s3 | -2.656 | -2.656 | yes |
| low | fs_chg_today | 0 | 0 | yes |
| low | fs_chg_s1 | -352 | -352 | yes |
| low | fs_chg_s2 | -171 | -171 | yes |
| low | fs_chg_s3 | -51.6 | -51.6 | yes |
| low | fs_verdict_today | baseline | Today | intended: baseline column now reads Today |
| low | fs_verdict_s1 | WORSE THAN TODAY | Worse than today | intended: sentence case only, same status word |
| low | fs_verdict_s2 | WORSE THAN TODAY | Worse than today | intended: sentence case only, same status word |
| low | fs_verdict_s3 | WORSE THAN TODAY | Worse than today | intended: sentence case only, same status word |
| blank key inputs | p1_postage | (blank) | (blank) | yes |
| blank key inputs | p1_labor | 0 | 0 | yes |
| blank key inputs | p1_true | (blank) | (blank) | yes |
| blank key inputs | p1_short | (blank) | (blank) | yes |
| blank key inputs | p1_flag | ENTER POSTAGE | Enter postage | intended: sentence case only, same status word |
| blank key inputs | p1_share | (blank) | (blank) | yes |
| blank key inputs | p1_d_name | Ceramic Mug 12 oz | Ceramic Mug 12 oz | yes |
| blank key inputs | p1_d_lb | 1.125 | 1.125 | yes |
| blank key inputs | p1_d_cubic | 288 | 288 | yes |
| blank key inputs | p1_d_over | no | No | intended: sentence case only, same status word |
| blank key inputs | p1_d_uspsdim | - | - | yes |
| blank key inputs | p1_d_uspsbill | 2 | 2 | yes |
| blank key inputs | p1_d_upsdim | 2.0719 | 2.0719 | yes |
| blank key inputs | p1_d_upsbill | 3 | 3 | yes |
| blank key inputs | p1_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| blank key inputs | p1_d_upsflag | DIM WEIGHT BITES: +1 lb | Dim weight bites: +1 lb | intended: sentence case only, same status word |
| blank key inputs | p1_s_usps | 2 | 2 | yes |
| blank key inputs | p1_s_ups | 3 | 3 | yes |
| blank key inputs | p1_s_zone | 0 | (blank) | yes |
| blank key inputs | p1_s_gacom | (blank) | (blank) | yes |
| blank key inputs | p1_s_garet | (blank) | (blank) | yes |
| blank key inputs | p1_s_pri | (blank) | (blank) | yes |
| blank key inputs | p1_s_upsgs | (blank) | (blank) | yes |
| blank key inputs | p1_s_cheap | (blank) | (blank) | yes |
| blank key inputs | p1_s_cheapname | (blank) | (blank) | yes |
| blank key inputs | p1_s_saved | (blank) | (blank) | yes |
| blank key inputs | p1_b_name | Ceramic Mug 12 oz | Ceramic Mug 12 oz | yes |
| blank key inputs | p1_b_sale | 19 | 19 | yes |
| blank key inputs | p1_b_ship | 4.95 | 4.95 | yes |
| blank key inputs | p1_b_true | (blank) | (blank) | yes |
| blank key inputs | p1_b_fees | 2.7252 | 2.7252 | yes |
| blank key inputs | p1_b_net | (blank) | (blank) | yes |
| blank key inputs | p1_b_margin | (blank) | (blank) | yes |
| blank key inputs | p1_b_shipflag | ENTER POSTAGE | Enter postage | intended: sentence case only, same status word |
| blank key inputs | p1_b_flag | (blank) | (blank) | yes |
| blank key inputs | p2_postage | (blank) | (blank) | yes |
| blank key inputs | p2_labor | 0 | 0 | yes |
| blank key inputs | p2_true | (blank) | (blank) | yes |
| blank key inputs | p2_short | (blank) | (blank) | yes |
| blank key inputs | p2_flag | ENTER POSTAGE | Enter postage | intended: sentence case only, same status word |
| blank key inputs | p2_share | (blank) | (blank) | yes |
| blank key inputs | p2_d_name | Graphic T-Shirt | Graphic T-Shirt | yes |
| blank key inputs | p2_d_lb | (blank) | (blank) | yes |
| blank key inputs | p2_d_cubic | 130 | 130 | yes |
| blank key inputs | p2_d_over | no | No | intended: sentence case only, same status word |
| blank key inputs | p2_d_uspsdim | - | - | yes |
| blank key inputs | p2_d_uspsbill | (blank) | (blank) | yes |
| blank key inputs | p2_d_upsdim | 0.9353 | 0.9353 | yes |
| blank key inputs | p2_d_upsbill | (blank) | (blank) | yes |
| blank key inputs | p2_d_uspsflag | (blank) | (blank) | yes |
| blank key inputs | p2_d_upsflag | (blank) | (blank) | yes |
| blank key inputs | p2_s_usps | (blank) | (blank) | yes |
| blank key inputs | p2_s_ups | (blank) | (blank) | yes |
| blank key inputs | p2_s_zone | 3 | 3 | yes |
| blank key inputs | p2_s_gacom | (blank) | (blank) | yes |
| blank key inputs | p2_s_garet | (blank) | (blank) | yes |
| blank key inputs | p2_s_pri | (blank) | (blank) | yes |
| blank key inputs | p2_s_upsgs | (blank) | (blank) | yes |
| blank key inputs | p2_s_cheap | (blank) | (blank) | yes |
| blank key inputs | p2_s_cheapname | (blank) | (blank) | yes |
| blank key inputs | p2_s_saved | (blank) | (blank) | yes |
| blank key inputs | p2_b_name | Graphic T-Shirt | Graphic T-Shirt | yes |
| blank key inputs | p2_b_sale | 28 | 28 | yes |
| blank key inputs | p2_b_ship | 4.95 | 4.95 | yes |
| blank key inputs | p2_b_true | (blank) | (blank) | yes |
| blank key inputs | p2_b_fees | 3.5803 | 3.5803 | yes |
| blank key inputs | p2_b_net | (blank) | (blank) | yes |
| blank key inputs | p2_b_margin | (blank) | (blank) | yes |
| blank key inputs | p2_b_shipflag | ENTER POSTAGE | Enter postage | intended: sentence case only, same status word |
| blank key inputs | p2_b_flag | (blank) | (blank) | yes |
| blank key inputs | p3_postage | (blank) | (blank) | yes |
| blank key inputs | p3_labor | 0 | 0 | yes |
| blank key inputs | p3_true | (blank) | (blank) | yes |
| blank key inputs | p3_short | (blank) | (blank) | yes |
| blank key inputs | p3_flag | ENTER POSTAGE | Enter postage | intended: sentence case only, same status word |
| blank key inputs | p3_share | (blank) | (blank) | yes |
| blank key inputs | p3_d_name | Framed Print 11x14 | Framed Print 11x14 | yes |
| blank key inputs | p3_d_lb | 3.25 | 3.25 | yes |
| blank key inputs | p3_d_cubic | (blank) | (blank) | yes |
| blank key inputs | p3_d_over | (blank) | (blank) | yes |
| blank key inputs | p3_d_uspsdim | (blank) | (blank) | yes |
| blank key inputs | p3_d_uspsbill | (blank) | (blank) | yes |
| blank key inputs | p3_d_upsdim | (blank) | (blank) | yes |
| blank key inputs | p3_d_upsbill | (blank) | (blank) | yes |
| blank key inputs | p3_d_uspsflag | (blank) | (blank) | yes |
| blank key inputs | p3_d_upsflag | (blank) | (blank) | yes |
| blank key inputs | p3_s_usps | (blank) | (blank) | yes |
| blank key inputs | p3_s_ups | (blank) | (blank) | yes |
| blank key inputs | p3_s_zone | 6 | 6 | yes |
| blank key inputs | p3_s_gacom | (blank) | (blank) | yes |
| blank key inputs | p3_s_garet | (blank) | (blank) | yes |
| blank key inputs | p3_s_pri | (blank) | (blank) | yes |
| blank key inputs | p3_s_upsgs | (blank) | (blank) | yes |
| blank key inputs | p3_s_cheap | (blank) | (blank) | yes |
| blank key inputs | p3_s_cheapname | (blank) | (blank) | yes |
| blank key inputs | p3_s_saved | (blank) | (blank) | yes |
| blank key inputs | p3_b_name | Framed Print 11x14 | Framed Print 11x14 | yes |
| blank key inputs | p3_b_sale | 65 | 65 | yes |
| blank key inputs | p3_b_ship | 12 | 12 | yes |
| blank key inputs | p3_b_true | (blank) | (blank) | yes |
| blank key inputs | p3_b_fees | 7.765 | 7.765 | yes |
| blank key inputs | p3_b_net | (blank) | (blank) | yes |
| blank key inputs | p3_b_margin | (blank) | (blank) | yes |
| blank key inputs | p3_b_shipflag | ENTER POSTAGE | Enter postage | intended: sentence case only, same status word |
| blank key inputs | p3_b_flag | (blank) | (blank) | yes |
| blank key inputs | p4_postage | 8.4 | 8.4 | yes |
| blank key inputs | p4_labor | 0 | 0 | yes |
| blank key inputs | p4_true | 8.86 | 8.86 | yes |
| blank key inputs | p4_short | -8.86 | -8.86 | yes |
| blank key inputs | p4_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| blank key inputs | p4_share | 0.9481 | 0.9481 | yes |
| blank key inputs | p4_d_name | Sterling Silver Earrings | Sterling Silver Earrings | yes |
| blank key inputs | p4_d_lb | 0.125 | 0.125 | yes |
| blank key inputs | p4_d_cubic | 54 | 54 | yes |
| blank key inputs | p4_d_over | no | No | intended: sentence case only, same status word |
| blank key inputs | p4_d_uspsdim | - | - | yes |
| blank key inputs | p4_d_uspsbill | 0.125 | 0.125 | yes |
| blank key inputs | p4_d_upsdim | 0.3885 | 0.3885 | yes |
| blank key inputs | p4_d_upsbill | 1 | 1 | yes |
| blank key inputs | p4_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| blank key inputs | p4_d_upsflag | ok | OK | intended: sentence case only, same status word |
| blank key inputs | p4_s_usps | 0.125 | 0.125 | yes |
| blank key inputs | p4_s_ups | 1 | 1 | yes |
| blank key inputs | p4_s_zone | 8 | 8 | yes |
| blank key inputs | p4_s_gacom | 8.4 | 8.4 | yes |
| blank key inputs | p4_s_garet | 9.45 | 9.45 | yes |
| blank key inputs | p4_s_pri | 15.22 | 15.22 | yes |
| blank key inputs | p4_s_upsgs | 21.0567 | 21.0567 | yes |
| blank key inputs | p4_s_cheap | 8.4 | 8.4 | yes |
| blank key inputs | p4_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| blank key inputs | p4_s_saved | 1.05 | 1.05 | yes |
| blank key inputs | p4_b_name | Sterling Silver Earrings | Sterling Silver Earrings | yes |
| blank key inputs | p4_b_sale | 42 | 42 | yes |
| blank key inputs | p4_b_ship | 0 | 0 | yes |
| blank key inputs | p4_b_true | 8.86 | 8.86 | yes |
| blank key inputs | p4_b_fees | 0.45 | 0.45 | yes |
| blank key inputs | p4_b_net | 21.69 | 21.69 | yes |
| blank key inputs | p4_b_margin | 0.5164 | 0.5164 | yes |
| blank key inputs | p4_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| blank key inputs | p4_b_flag | OK | OK | yes |
| blank key inputs | p5_postage | 8.51 | 8.51 | yes |
| blank key inputs | p5_labor | 0 | 0 | yes |
| blank key inputs | p5_true | 9.75 | 9.75 | yes |
| blank key inputs | p5_short | -0.8 | -0.8 | yes |
| blank key inputs | p5_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| blank key inputs | p5_share | 0.8728 | 0.8728 | yes |
| blank key inputs | p5_d_name | Soy Candle 8 oz | Soy Candle 8 oz | yes |
| blank key inputs | p5_d_lb | 1.25 | 1.25 | yes |
| blank key inputs | p5_d_cubic | 216 | 216 | yes |
| blank key inputs | p5_d_over | no | No | intended: sentence case only, same status word |
| blank key inputs | p5_d_uspsdim | - | - | yes |
| blank key inputs | p5_d_uspsbill | 2 | 2 | yes |
| blank key inputs | p5_d_upsdim | 1.554 | 1.554 | yes |
| blank key inputs | p5_d_upsbill | 2 | 2 | yes |
| blank key inputs | p5_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| blank key inputs | p5_d_upsflag | ok | OK | intended: sentence case only, same status word |
| blank key inputs | p5_s_usps | 2 | 2 | yes |
| blank key inputs | p5_s_ups | 2 | 2 | yes |
| blank key inputs | p5_s_zone | 4 | 4 | yes |
| blank key inputs | p5_s_gacom | 8.51 | 8.51 | yes |
| blank key inputs | p5_s_garet | 13 | 13 | yes |
| blank key inputs | p5_s_pri | 10.79 | 10.79 | yes |
| blank key inputs | p5_s_upsgs | 21.6395 | 21.6395 | yes |
| blank key inputs | p5_s_cheap | 8.51 | 8.51 | yes |
| blank key inputs | p5_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| blank key inputs | p5_s_saved | 4.49 | 4.49 | yes |
| blank key inputs | p5_b_name | Soy Candle 8 oz | Soy Candle 8 oz | yes |
| blank key inputs | p5_b_sale | 22 | 22 | yes |
| blank key inputs | p5_b_ship | 8.95 | 8.95 | yes |
| blank key inputs | p5_b_true | 9.75 | 9.75 | yes |
| blank key inputs | p5_b_fees | 3.3902 | 3.3902 | yes |
| blank key inputs | p5_b_net | 12.2097 | 12.2097 | yes |
| blank key inputs | p5_b_margin | 0.3945 | 0.3945 | yes |
| blank key inputs | p5_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| blank key inputs | p5_b_flag | OK | OK | yes |
| blank key inputs | p6_postage | 21.15 | 21.15 | yes |
| blank key inputs | p6_labor | 0 | 0 | yes |
| blank key inputs | p6_true | 25.21 | 25.21 | yes |
| blank key inputs | p6_short | -10.26 | -10.26 | yes |
| blank key inputs | p6_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| blank key inputs | p6_share | 0.839 | 0.839 | yes |
| blank key inputs | p6_d_name | Grapevine Wreath 16 in | Grapevine Wreath 16 in | yes |
| blank key inputs | p6_d_lb | 2.5 | 2.5 | yes |
| blank key inputs | p6_d_cubic | 2,048 | 2,048 | yes |
| blank key inputs | p6_d_over | YES | Yes | intended: sentence case only, same status word |
| blank key inputs | p6_d_uspsdim | 14.7338 | 14.7338 | yes |
| blank key inputs | p6_d_uspsbill | 15 | 15 | yes |
| blank key inputs | p6_d_upsdim | 14.7338 | 14.7338 | yes |
| blank key inputs | p6_d_upsbill | 15 | 15 | yes |
| blank key inputs | p6_d_uspsflag | DIM WEIGHT BITES: +12 lb | Dim weight bites: +12 lb | intended: sentence case only, same status word |
| blank key inputs | p6_d_upsflag | DIM WEIGHT BITES: +12 lb | Dim weight bites: +12 lb | intended: sentence case only, same status word |
| blank key inputs | p6_s_usps | 15 | 15 | yes |
| blank key inputs | p6_s_ups | 15 | 15 | yes |
| blank key inputs | p6_s_zone | 5 | 5 | yes |
| blank key inputs | p6_s_gacom | 21.15 | 21.15 | yes |
| blank key inputs | p6_s_garet | 28.95 | 28.95 | yes |
| blank key inputs | p6_s_pri | 35.25 | 35.25 | yes |
| blank key inputs | p6_s_upsgs | 39.9637 | 39.9637 | yes |
| blank key inputs | p6_s_cheap | 21.15 | 21.15 | yes |
| blank key inputs | p6_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| blank key inputs | p6_s_saved | 7.8 | 7.8 | yes |
| blank key inputs | p6_b_name | Grapevine Wreath 16 in | Grapevine Wreath 16 in | yes |
| blank key inputs | p6_b_sale | 58 | 58 | yes |
| blank key inputs | p6_b_ship | 14.95 | 14.95 | yes |
| blank key inputs | p6_b_true | 25.21 | 25.21 | yes |
| blank key inputs | p6_b_fees | 7.3803 | 7.3803 | yes |
| blank key inputs | p6_b_net | 22.3598 | 22.3598 | yes |
| blank key inputs | p6_b_margin | 0.3065 | 0.3065 | yes |
| blank key inputs | p6_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| blank key inputs | p6_b_flag | OK | OK | yes |
| blank key inputs | p7_postage | 6.94 | 6.94 | yes |
| blank key inputs | p7_labor | 0 | 0 | yes |
| blank key inputs | p7_true | 7.25 | 7.25 | yes |
| blank key inputs | p7_short | -0.3 | -0.3 | yes |
| blank key inputs | p7_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| blank key inputs | p7_share | 0.9572 | 0.9572 | yes |
| blank key inputs | p7_d_name | Canvas Tote Bag | Canvas Tote Bag | yes |
| blank key inputs | p7_d_lb | 0.5625 | 0.5625 | yes |
| blank key inputs | p7_d_cubic | 180 | 180 | yes |
| blank key inputs | p7_d_over | no | No | intended: sentence case only, same status word |
| blank key inputs | p7_d_uspsdim | - | - | yes |
| blank key inputs | p7_d_uspsbill | 0.5625 | 0.5625 | yes |
| blank key inputs | p7_d_upsdim | 1.295 | 1.295 | yes |
| blank key inputs | p7_d_upsbill | 2 | 2 | yes |
| blank key inputs | p7_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| blank key inputs | p7_d_upsflag | DIM WEIGHT BITES: +1 lb | Dim weight bites: +1 lb | intended: sentence case only, same status word |
| blank key inputs | p7_s_usps | 0.5625 | 0.5625 | yes |
| blank key inputs | p7_s_ups | 2 | 2 | yes |
| blank key inputs | p7_s_zone | 2 | 2 | yes |
| blank key inputs | p7_s_gacom | 6.94 | 6.94 | yes |
| blank key inputs | p7_s_garet | 9.95 | 9.95 | yes |
| blank key inputs | p7_s_pri | 9.32 | 9.32 | yes |
| blank key inputs | p7_s_upsgs | 18.117 | 18.117 | yes |
| blank key inputs | p7_s_cheap | 6.94 | 6.94 | yes |
| blank key inputs | p7_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| blank key inputs | p7_s_saved | 3.01 | 3.01 | yes |
| blank key inputs | p7_b_name | Canvas Tote Bag | Canvas Tote Bag | yes |
| blank key inputs | p7_b_sale | 30 | 30 | yes |
| blank key inputs | p7_b_ship | 6.95 | 6.95 | yes |
| blank key inputs | p7_b_true | 7.25 | 7.25 | yes |
| blank key inputs | p7_b_fees | 3.9603 | 3.9603 | yes |
| blank key inputs | p7_b_net | 16.2398 | 16.2398 | yes |
| blank key inputs | p7_b_margin | 0.4395 | 0.4395 | yes |
| blank key inputs | p7_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| blank key inputs | p7_b_flag | OK | OK | yes |
| blank key inputs | p8_postage | 7.69 | 7.69 | yes |
| blank key inputs | p8_labor | 0 | 0 | yes |
| blank key inputs | p8_true | 8.55 | 8.55 | yes |
| blank key inputs | p8_short | 1.4 | 1.4 | yes |
| blank key inputs | p8_flag | COVERED | Covered | intended: sentence case only, same status word |
| blank key inputs | p8_share | 0.8994 | 0.8994 | yes |
| blank key inputs | p8_d_name | Handmade Soap Set (3) | Handmade Soap Set (3) | yes |
| blank key inputs | p8_d_lb | 0.875 | 0.875 | yes |
| blank key inputs | p8_d_cubic | 105 | 105 | yes |
| blank key inputs | p8_d_over | no | No | intended: sentence case only, same status word |
| blank key inputs | p8_d_uspsdim | - | - | yes |
| blank key inputs | p8_d_uspsbill | 0.875 | 0.875 | yes |
| blank key inputs | p8_d_upsdim | 0.7554 | 0.7554 | yes |
| blank key inputs | p8_d_upsbill | 1 | 1 | yes |
| blank key inputs | p8_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| blank key inputs | p8_d_upsflag | ok | OK | intended: sentence case only, same status word |
| blank key inputs | p8_s_usps | 0.875 | 0.875 | yes |
| blank key inputs | p8_s_ups | 1 | 1 | yes |
| blank key inputs | p8_s_zone | 5 | 5 | yes |
| blank key inputs | p8_s_gacom | 7.69 | 7.69 | yes |
| blank key inputs | p8_s_garet | 10.95 | 10.95 | yes |
| blank key inputs | p8_s_pri | 12.97 | 12.97 | yes |
| blank key inputs | p8_s_upsgs | 19.8265 | 19.8265 | yes |
| blank key inputs | p8_s_cheap | 7.69 | 7.69 | yes |
| blank key inputs | p8_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| blank key inputs | p8_s_saved | 3.26 | 3.26 | yes |
| blank key inputs | p8_b_name | Handmade Soap Set (3) | Handmade Soap Set (3) | yes |
| blank key inputs | p8_b_sale | 26 | 26 | yes |
| blank key inputs | p8_b_ship | 9.95 | 9.95 | yes |
| blank key inputs | p8_b_true | 8.55 | 8.55 | yes |
| blank key inputs | p8_b_fees | 3.8653 | 3.8653 | yes |
| blank key inputs | p8_b_net | 17.5347 | 17.5347 | yes |
| blank key inputs | p8_b_margin | 0.4878 | 0.4878 | yes |
| blank key inputs | p8_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| blank key inputs | p8_b_flag | OK | OK | yes |
| blank key inputs | p9_postage | 8.51 | 8.51 | yes |
| blank key inputs | p9_labor | 0 | 0 | yes |
| blank key inputs | p9_true | 9.9 | 9.9 | yes |
| blank key inputs | p9_short | 3.05 | 3.05 | yes |
| blank key inputs | p9_flag | COVERED | Covered | intended: sentence case only, same status word |
| blank key inputs | p9_share | 0.8596 | 0.8596 | yes |
| blank key inputs | p9_d_name | Wooden Puzzle | Wooden Puzzle | yes |
| blank key inputs | p9_d_lb | 1.875 | 1.875 | yes |
| blank key inputs | p9_d_cubic | 160 | 160 | yes |
| blank key inputs | p9_d_over | no | No | intended: sentence case only, same status word |
| blank key inputs | p9_d_uspsdim | - | - | yes |
| blank key inputs | p9_d_uspsbill | 2 | 2 | yes |
| blank key inputs | p9_d_upsdim | 1.1511 | 1.1511 | yes |
| blank key inputs | p9_d_upsbill | 2 | 2 | yes |
| blank key inputs | p9_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| blank key inputs | p9_d_upsflag | ok | OK | intended: sentence case only, same status word |
| blank key inputs | p9_s_usps | 2 | 2 | yes |
| blank key inputs | p9_s_ups | 2 | 2 | yes |
| blank key inputs | p9_s_zone | 4 | 4 | yes |
| blank key inputs | p9_s_gacom | 8.51 | 8.51 | yes |
| blank key inputs | p9_s_garet | 13 | 13 | yes |
| blank key inputs | p9_s_pri | 10.79 | 10.79 | yes |
| blank key inputs | p9_s_upsgs | 21.6395 | 21.6395 | yes |
| blank key inputs | p9_s_cheap | 8.51 | 8.51 | yes |
| blank key inputs | p9_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| blank key inputs | p9_s_saved | 4.49 | 4.49 | yes |
| blank key inputs | p9_b_name | Wooden Puzzle | Wooden Puzzle | yes |
| blank key inputs | p9_b_sale | 34 | 34 | yes |
| blank key inputs | p9_b_ship | 12.95 | 12.95 | yes |
| blank key inputs | p9_b_true | 9.9 | 9.9 | yes |
| blank key inputs | p9_b_fees | 4.9103 | 4.9103 | yes |
| blank key inputs | p9_b_net | 23.1398 | 23.1398 | yes |
| blank key inputs | p9_b_margin | 0.4929 | 0.4929 | yes |
| blank key inputs | p9_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| blank key inputs | p9_b_flag | OK | OK | yes |
| blank key inputs | p10_postage | 12.84 | 12.84 | yes |
| blank key inputs | p10_labor | 0 | 0 | yes |
| blank key inputs | p10_true | 14.75 | 14.75 | yes |
| blank key inputs | p10_short | 3.2 | 3.2 | yes |
| blank key inputs | p10_flag | COVERED | Covered | intended: sentence case only, same status word |
| blank key inputs | p10_share | 0.8705 | 0.8705 | yes |
| blank key inputs | p10_d_name | Board Game | Board Game | yes |
| blank key inputs | p10_d_lb | 3.75 | 3.75 | yes |
| blank key inputs | p10_d_cubic | 432 | 432 | yes |
| blank key inputs | p10_d_over | no | No | intended: sentence case only, same status word |
| blank key inputs | p10_d_uspsdim | - | - | yes |
| blank key inputs | p10_d_uspsbill | 4 | 4 | yes |
| blank key inputs | p10_d_upsdim | 3.1079 | 3.1079 | yes |
| blank key inputs | p10_d_upsbill | 4 | 4 | yes |
| blank key inputs | p10_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| blank key inputs | p10_d_upsflag | ok | OK | intended: sentence case only, same status word |
| blank key inputs | p10_s_usps | 4 | 4 | yes |
| blank key inputs | p10_s_ups | 4 | 4 | yes |
| blank key inputs | p10_s_zone | 5 | 5 | yes |
| blank key inputs | p10_s_gacom | 12.84 | 12.84 | yes |
| blank key inputs | p10_s_garet | 16.4 | 16.4 | yes |
| blank key inputs | p10_s_pri | 19.88 | 19.88 | yes |
| blank key inputs | p10_s_upsgs | 24.9287 | 24.9287 | yes |
| blank key inputs | p10_s_cheap | 12.84 | 12.84 | yes |
| blank key inputs | p10_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| blank key inputs | p10_s_saved | 3.56 | 3.56 | yes |
| blank key inputs | p10_b_name | Board Game | Board Game | yes |
| blank key inputs | p10_b_sale | 48 | 48 | yes |
| blank key inputs | p10_b_ship | 17.95 | 17.95 | yes |
| blank key inputs | p10_b_true | 14.75 | 14.75 | yes |
| blank key inputs | p10_b_fees | 6.7153 | 6.7153 | yes |
| blank key inputs | p10_b_net | 28.4848 | 28.4848 | yes |
| blank key inputs | p10_b_margin | 0.4319 | 0.4319 | yes |
| blank key inputs | p10_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| blank key inputs | p10_b_flag | OK | OK | yes |
| blank key inputs | p11_postage | (blank) | (blank) | yes |
| blank key inputs | p11_labor | (blank) | (blank) | yes |
| blank key inputs | p11_true | (blank) | (blank) | yes |
| blank key inputs | p11_short | (blank) | (blank) | yes |
| blank key inputs | p11_flag | (blank) | (blank) | yes |
| blank key inputs | p11_share | (blank) | (blank) | yes |
| blank key inputs | p11_d_name | (blank) | (blank) | yes |
| blank key inputs | p11_d_lb | (blank) | (blank) | yes |
| blank key inputs | p11_d_cubic | (blank) | (blank) | yes |
| blank key inputs | p11_d_over | (blank) | (blank) | yes |
| blank key inputs | p11_d_uspsdim | (blank) | (blank) | yes |
| blank key inputs | p11_d_uspsbill | (blank) | (blank) | yes |
| blank key inputs | p11_d_upsdim | (blank) | (blank) | yes |
| blank key inputs | p11_d_upsbill | (blank) | (blank) | yes |
| blank key inputs | p11_d_uspsflag | (blank) | (blank) | yes |
| blank key inputs | p11_d_upsflag | (blank) | (blank) | yes |
| blank key inputs | p11_s_usps | (blank) | (blank) | yes |
| blank key inputs | p11_s_ups | (blank) | (blank) | yes |
| blank key inputs | p11_s_zone | (blank) | (blank) | yes |
| blank key inputs | p11_s_gacom | (blank) | (blank) | yes |
| blank key inputs | p11_s_garet | (blank) | (blank) | yes |
| blank key inputs | p11_s_pri | (blank) | (blank) | yes |
| blank key inputs | p11_s_upsgs | (blank) | (blank) | yes |
| blank key inputs | p11_s_cheap | (blank) | (blank) | yes |
| blank key inputs | p11_s_cheapname | (blank) | (blank) | yes |
| blank key inputs | p11_s_saved | (blank) | (blank) | yes |
| blank key inputs | p11_b_name | (blank) | (blank) | yes |
| blank key inputs | p11_b_sale | (blank) | (blank) | yes |
| blank key inputs | p11_b_ship | (blank) | (blank) | yes |
| blank key inputs | p11_b_true | (blank) | (blank) | yes |
| blank key inputs | p11_b_fees | (blank) | (blank) | yes |
| blank key inputs | p11_b_net | (blank) | (blank) | yes |
| blank key inputs | p11_b_margin | (blank) | (blank) | yes |
| blank key inputs | p11_b_shipflag | (blank) | (blank) | yes |
| blank key inputs | p11_b_flag | (blank) | (blank) | yes |
| blank key inputs | p12_postage | (blank) | (blank) | yes |
| blank key inputs | p12_labor | (blank) | (blank) | yes |
| blank key inputs | p12_true | (blank) | (blank) | yes |
| blank key inputs | p12_short | (blank) | (blank) | yes |
| blank key inputs | p12_flag | (blank) | (blank) | yes |
| blank key inputs | p12_share | (blank) | (blank) | yes |
| blank key inputs | p12_d_name | (blank) | (blank) | yes |
| blank key inputs | p12_d_lb | (blank) | (blank) | yes |
| blank key inputs | p12_d_cubic | (blank) | (blank) | yes |
| blank key inputs | p12_d_over | (blank) | (blank) | yes |
| blank key inputs | p12_d_uspsdim | (blank) | (blank) | yes |
| blank key inputs | p12_d_uspsbill | (blank) | (blank) | yes |
| blank key inputs | p12_d_upsdim | (blank) | (blank) | yes |
| blank key inputs | p12_d_upsbill | (blank) | (blank) | yes |
| blank key inputs | p12_d_uspsflag | (blank) | (blank) | yes |
| blank key inputs | p12_d_upsflag | (blank) | (blank) | yes |
| blank key inputs | p12_s_usps | (blank) | (blank) | yes |
| blank key inputs | p12_s_ups | (blank) | (blank) | yes |
| blank key inputs | p12_s_zone | (blank) | (blank) | yes |
| blank key inputs | p12_s_gacom | (blank) | (blank) | yes |
| blank key inputs | p12_s_garet | (blank) | (blank) | yes |
| blank key inputs | p12_s_pri | (blank) | (blank) | yes |
| blank key inputs | p12_s_upsgs | (blank) | (blank) | yes |
| blank key inputs | p12_s_cheap | (blank) | (blank) | yes |
| blank key inputs | p12_s_cheapname | (blank) | (blank) | yes |
| blank key inputs | p12_s_saved | (blank) | (blank) | yes |
| blank key inputs | p12_b_name | (blank) | (blank) | yes |
| blank key inputs | p12_b_sale | (blank) | (blank) | yes |
| blank key inputs | p12_b_ship | (blank) | (blank) | yes |
| blank key inputs | p12_b_true | (blank) | (blank) | yes |
| blank key inputs | p12_b_fees | (blank) | (blank) | yes |
| blank key inputs | p12_b_net | (blank) | (blank) | yes |
| blank key inputs | p12_b_margin | (blank) | (blank) | yes |
| blank key inputs | p12_b_shipflag | (blank) | (blank) | yes |
| blank key inputs | p12_b_flag | (blank) | (blank) | yes |
| blank key inputs | p30_postage | (blank) | (blank) | yes |
| blank key inputs | p30_labor | (blank) | (blank) | yes |
| blank key inputs | p30_true | (blank) | (blank) | yes |
| blank key inputs | p30_short | (blank) | (blank) | yes |
| blank key inputs | p30_flag | (blank) | (blank) | yes |
| blank key inputs | p30_share | (blank) | (blank) | yes |
| blank key inputs | p30_d_name | (blank) | (blank) | yes |
| blank key inputs | p30_d_lb | (blank) | (blank) | yes |
| blank key inputs | p30_d_cubic | (blank) | (blank) | yes |
| blank key inputs | p30_d_over | (blank) | (blank) | yes |
| blank key inputs | p30_d_uspsdim | (blank) | (blank) | yes |
| blank key inputs | p30_d_uspsbill | (blank) | (blank) | yes |
| blank key inputs | p30_d_upsdim | (blank) | (blank) | yes |
| blank key inputs | p30_d_upsbill | (blank) | (blank) | yes |
| blank key inputs | p30_d_uspsflag | (blank) | (blank) | yes |
| blank key inputs | p30_d_upsflag | (blank) | (blank) | yes |
| blank key inputs | p30_s_usps | (blank) | (blank) | yes |
| blank key inputs | p30_s_ups | (blank) | (blank) | yes |
| blank key inputs | p30_s_zone | (blank) | (blank) | yes |
| blank key inputs | p30_s_gacom | (blank) | (blank) | yes |
| blank key inputs | p30_s_garet | (blank) | (blank) | yes |
| blank key inputs | p30_s_pri | (blank) | (blank) | yes |
| blank key inputs | p30_s_upsgs | (blank) | (blank) | yes |
| blank key inputs | p30_s_cheap | (blank) | (blank) | yes |
| blank key inputs | p30_s_cheapname | (blank) | (blank) | yes |
| blank key inputs | p30_s_saved | (blank) | (blank) | yes |
| blank key inputs | p30_b_name | (blank) | (blank) | yes |
| blank key inputs | p30_b_sale | (blank) | (blank) | yes |
| blank key inputs | p30_b_ship | (blank) | (blank) | yes |
| blank key inputs | p30_b_true | (blank) | (blank) | yes |
| blank key inputs | p30_b_fees | (blank) | (blank) | yes |
| blank key inputs | p30_b_net | (blank) | (blank) | yes |
| blank key inputs | p30_b_margin | (blank) | (blank) | yes |
| blank key inputs | p30_b_shipflag | (blank) | (blank) | yes |
| blank key inputs | p30_b_flag | (blank) | (blank) | yes |
| blank key inputs | avg_true | 12.0386 | 12.0386 | yes |
| blank key inputs | avg_short | -1.7957 | -1.7957 | yes |
| blank key inputs | avg_share | 0.8924 | 0.8924 | yes |
| blank key inputs | sc_cheap_total | 74.04 | 74.04 | yes |
| blank key inputs | sc_saved_total | 27.66 | 27.66 | yes |
| blank key inputs | db_losing | 0 | 0 | yes |
| blank key inputs | db_under | 4 | 4 | yes |
| blank key inputs | db_avgtrue | 12.0386 | 12.0386 | yes |
| blank key inputs | db_avgshort | -1.7957 | -1.7957 | yes |
| blank key inputs | db_shipcost | 84.27 | 84.27 | yes |
| blank key inputs | db_collected | 93.6 | 93.6 | yes |
| blank key inputs | db_netship | 9.33 | 9.33 | yes |
| blank key inputs | db_share | 0.8924 | 0.8924 | yes |
| blank key inputs | db_tot_true | 84.27 | 84.27 | yes |
| blank key inputs | db_tot_fees | 44.742 | 44.742 | yes |
| blank key inputs | db_tot_net | 141.6585 | 141.6585 | yes |
| blank key inputs | fs_tc | 12.0386 | 12.0386 | yes |
| blank key inputs | fs_tcused | 12.0386 | 12.0386 | yes |
| blank key inputs | fs_profit_order | -5.5386 | -5.5386 | yes |
| blank key inputs | fs_cost | 6.5 | 6.5 | yes |
| blank key inputs | fs_breakeven | 0 | 0 | yes |
| blank key inputs | fs_recommendation | Keep charging shipping. With these assumptions, none of the three thresholds beats what you earn today. | Keep charging shipping. With these assumptions, none of the three thresholds beats what you earn today. | yes |
| blank key inputs | fs_avgo_today | 0 | 0 | yes |
| blank key inputs | fs_avgo_s1 | 0 | 0 | yes |
| blank key inputs | fs_avgo_s2 | 0 | 0 | yes |
| blank key inputs | fs_avgo_s3 | 0 | 0 | yes |
| blank key inputs | fs_orders_today | 100 | 100 | yes |
| blank key inputs | fs_orders_s1 | 115 | 115 | yes |
| blank key inputs | fs_orders_s2 | 115 | 115 | yes |
| blank key inputs | fs_orders_s3 | 115 | 115 | yes |
| blank key inputs | fs_qual_today | 0 | 0 | yes |
| blank key inputs | fs_qual_s1 | 63.25 | 63.25 | yes |
| blank key inputs | fs_qual_s2 | 0 | 0 | yes |
| blank key inputs | fs_qual_s3 | 13.8 | 13.8 | yes |
| blank key inputs | fs_other_today | 100 | 100 | yes |
| blank key inputs | fs_other_s1 | 51.75 | 51.75 | yes |
| blank key inputs | fs_other_s2 | 115 | 115 | yes |
| blank key inputs | fs_other_s3 | 101.2 | 101.2 | yes |
| blank key inputs | fs_rev_today | 0 | 0 | yes |
| blank key inputs | fs_rev_s1 | 3,162.5 | 3,162.5 | yes |
| blank key inputs | fs_rev_s2 | 0 | 0 | yes |
| blank key inputs | fs_rev_s3 | 1,269.6 | 1,269.6 | yes |
| blank key inputs | fs_coll_today | 650 | 650 | yes |
| blank key inputs | fs_coll_s1 | 336.375 | 336.375 | yes |
| blank key inputs | fs_coll_s2 | 747.5 | 747.5 | yes |
| blank key inputs | fs_coll_s3 | 657.8 | 657.8 | yes |
| blank key inputs | fs_parc_today | 1,203.8571 | 1,203.8571 | yes |
| blank key inputs | fs_parc_s1 | 1,384.4357 | 1,384.4357 | yes |
| blank key inputs | fs_parc_s2 | 1,384.4357 | 1,384.4357 | yes |
| blank key inputs | fs_parc_s3 | 1,384.4357 | 1,384.4357 | yes |
| blank key inputs | fs_profit_today | -553.8571 | -553.8571 | yes |
| blank key inputs | fs_profit_s1 | -1,048.0607 | -1,048.0607 | yes |
| blank key inputs | fs_profit_s2 | -636.9357 | -636.9357 | yes |
| blank key inputs | fs_profit_s3 | -726.6357 | -726.6357 | yes |
| blank key inputs | fs_per_today | -5.5386 | -5.5386 | yes |
| blank key inputs | fs_per_s1 | -9.1136 | -9.1136 | yes |
| blank key inputs | fs_per_s2 | -5.5386 | -5.5386 | yes |
| blank key inputs | fs_per_s3 | -6.3186 | -6.3186 | yes |
| blank key inputs | fs_chg_today | 0 | 0 | yes |
| blank key inputs | fs_chg_s1 | -494.2036 | -494.2036 | yes |
| blank key inputs | fs_chg_s2 | -83.0786 | -83.0786 | yes |
| blank key inputs | fs_chg_s3 | -172.7786 | -172.7786 | yes |
| blank key inputs | fs_verdict_today | baseline | Today | intended: baseline column now reads Today |
| blank key inputs | fs_verdict_s1 | WORSE THAN TODAY | Worse than today | intended: sentence case only, same status word |
| blank key inputs | fs_verdict_s2 | WORSE THAN TODAY | Worse than today | intended: sentence case only, same status word |
| blank key inputs | fs_verdict_s3 | WORSE THAN TODAY | Worse than today | intended: sentence case only, same status word |
| overrides and edits | p1_postage | 7.5 | 7.5 | yes |
| overrides and edits | p1_labor | 1.8 | 1.8 | yes |
| overrides and edits | p1_true | 10.74 | 10.74 | yes |
| overrides and edits | p1_short | -5.79 | -5.79 | yes |
| overrides and edits | p1_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| overrides and edits | p1_share | 0.6983 | 0.6983 | yes |
| overrides and edits | p1_d_name | Ceramic Mug 12 oz | Ceramic Mug 12 oz | yes |
| overrides and edits | p1_d_lb | 1.125 | 1.125 | yes |
| overrides and edits | p1_d_cubic | 288 | 288 | yes |
| overrides and edits | p1_d_over | no | No | intended: sentence case only, same status word |
| overrides and edits | p1_d_uspsdim | - | - | yes |
| overrides and edits | p1_d_uspsbill | 2 | 2 | yes |
| overrides and edits | p1_d_upsdim | 2.0719 | 2.0719 | yes |
| overrides and edits | p1_d_upsbill | 3 | 3 | yes |
| overrides and edits | p1_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| overrides and edits | p1_d_upsflag | DIM WEIGHT BITES: +1 lb | Dim weight bites: +1 lb | intended: sentence case only, same status word |
| overrides and edits | p1_s_usps | 2 | 2 | yes |
| overrides and edits | p1_s_ups | 3 | 3 | yes |
| overrides and edits | p1_s_zone | 5 | 5 | yes |
| overrides and edits | p1_s_gacom | 9.95 | 9.95 | yes |
| overrides and edits | p1_s_garet | 14.1 | 14.1 | yes |
| overrides and edits | p1_s_pri | 13.17 | 13.17 | yes |
| overrides and edits | p1_s_upsgs | 23.6596 | 23.6596 | yes |
| overrides and edits | p1_s_cheap | 9.95 | 9.95 | yes |
| overrides and edits | p1_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| overrides and edits | p1_s_saved | 4.15 | 4.15 | yes |
| overrides and edits | p1_b_name | Ceramic Mug 12 oz | Ceramic Mug 12 oz | yes |
| overrides and edits | p1_b_sale | 19 | 19 | yes |
| overrides and edits | p1_b_ship | 4.95 | 4.95 | yes |
| overrides and edits | p1_b_true | 10.74 | 10.74 | yes |
| overrides and edits | p1_b_fees | 2.7252 | 2.7252 | yes |
| overrides and edits | p1_b_net | 1.9848 | 1.9848 | yes |
| overrides and edits | p1_b_margin | 0.0829 | 0.0829 | yes |
| overrides and edits | p1_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| overrides and edits | p1_b_flag | THIN | Thin | intended: sentence case only, same status word |
| overrides and edits | p2_postage | 9.71 | 9.71 | yes |
| overrides and edits | p2_labor | 0.9 | 0.9 | yes |
| overrides and edits | p2_true | 10.89 | 10.89 | yes |
| overrides and edits | p2_short | -5.94 | -5.94 | yes |
| overrides and edits | p2_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| overrides and edits | p2_share | 0.8916 | 0.8916 | yes |
| overrides and edits | p2_d_name | Graphic T-Shirt | Graphic T-Shirt | yes |
| overrides and edits | p2_d_lb | 0.4375 | 0.4375 | yes |
| overrides and edits | p2_d_cubic | 130 | 130 | yes |
| overrides and edits | p2_d_over | no | No | intended: sentence case only, same status word |
| overrides and edits | p2_d_uspsdim | - | - | yes |
| overrides and edits | p2_d_uspsbill | 0.4375 | 0.4375 | yes |
| overrides and edits | p2_d_upsdim | 0.9353 | 0.9353 | yes |
| overrides and edits | p2_d_upsbill | 1 | 1 | yes |
| overrides and edits | p2_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| overrides and edits | p2_d_upsflag | ok | OK | intended: sentence case only, same status word |
| overrides and edits | p2_s_usps | 0.4375 | 0.4375 | yes |
| overrides and edits | p2_s_ups | 1 | 1 | yes |
| overrides and edits | p2_s_zone | 3 | 3 | yes |
| overrides and edits | p2_s_gacom | 7.3 | 7.3 | yes |
| overrides and edits | p2_s_garet | 8.15 | 8.15 | yes |
| overrides and edits | p2_s_pri | 9.71 | 9.71 | yes |
| overrides and edits | p2_s_upsgs | 17.4954 | 17.4954 | yes |
| overrides and edits | p2_s_cheap | 7.3 | 7.3 | yes |
| overrides and edits | p2_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| overrides and edits | p2_s_saved | 0.85 | 0.85 | yes |
| overrides and edits | p2_b_name | Graphic T-Shirt | Graphic T-Shirt | yes |
| overrides and edits | p2_b_sale | 28 | 28 | yes |
| overrides and edits | p2_b_ship | 4.95 | 4.95 | yes |
| overrides and edits | p2_b_true | 10.89 | 10.89 | yes |
| overrides and edits | p2_b_fees | 3.5803 | 3.5803 | yes |
| overrides and edits | p2_b_net | 6.4798 | 6.4798 | yes |
| overrides and edits | p2_b_margin | 0.1967 | 0.1967 | yes |
| overrides and edits | p2_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| overrides and edits | p2_b_flag | OK | OK | yes |
| overrides and edits | p3_postage | 15.16 | 15.16 | yes |
| overrides and edits | p3_labor | 3.6 | 3.6 | yes |
| overrides and edits | p3_true | 22.47 | 22.47 | yes |
| overrides and edits | p3_short | -10.47 | -10.47 | yes |
| overrides and edits | p3_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| overrides and edits | p3_share | 0.6747 | 0.6747 | yes |
| overrides and edits | p3_d_name | Framed Print 11x14 | Framed Print 11x14 | yes |
| overrides and edits | p3_d_lb | 3.25 | 3.25 | yes |
| overrides and edits | p3_d_cubic | 756 | 756 | yes |
| overrides and edits | p3_d_over | no | No | intended: sentence case only, same status word |
| overrides and edits | p3_d_uspsdim | - | - | yes |
| overrides and edits | p3_d_uspsbill | 4 | 4 | yes |
| overrides and edits | p3_d_upsdim | 5.4388 | 5.4388 | yes |
| overrides and edits | p3_d_upsbill | 6 | 6 | yes |
| overrides and edits | p3_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| overrides and edits | p3_d_upsflag | DIM WEIGHT BITES: +2 lb | Dim weight bites: +2 lb | intended: sentence case only, same status word |
| overrides and edits | p3_s_usps | 4 | 4 | yes |
| overrides and edits | p3_s_ups | 6 | 6 | yes |
| overrides and edits | p3_s_zone | 6 | 6 | yes |
| overrides and edits | p3_s_gacom | 15.16 | 15.16 | yes |
| overrides and edits | p3_s_garet | 18.3 | 18.3 | yes |
| overrides and edits | p3_s_pri | 24.51 | 24.51 | yes |
| overrides and edits | p3_s_upsgs | 27.0526 | 27.0526 | yes |
| overrides and edits | p3_s_cheap | 15.16 | 15.16 | yes |
| overrides and edits | p3_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| overrides and edits | p3_s_saved | 3.14 | 3.14 | yes |
| overrides and edits | p3_b_name | Framed Print 11x14 | Framed Print 11x14 | yes |
| overrides and edits | p3_b_sale | 65 | 65 | yes |
| overrides and edits | p3_b_ship | 12 | 12 | yes |
| overrides and edits | p3_b_true | 22.47 | 22.47 | yes |
| overrides and edits | p3_b_fees | 7.765 | 7.765 | yes |
| overrides and edits | p3_b_net | 24.765 | 24.765 | yes |
| overrides and edits | p3_b_margin | 0.3216 | 0.3216 | yes |
| overrides and edits | p3_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| overrides and edits | p3_b_flag | OK | OK | yes |
| overrides and edits | p4_postage | 8.4 | 8.4 | yes |
| overrides and edits | p4_labor | 0.9 | 0.9 | yes |
| overrides and edits | p4_true | 9.76 | 9.76 | yes |
| overrides and edits | p4_short | -9.76 | -9.76 | yes |
| overrides and edits | p4_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| overrides and edits | p4_share | 0.8607 | 0.8607 | yes |
| overrides and edits | p4_d_name | Sterling Silver Earrings | Sterling Silver Earrings | yes |
| overrides and edits | p4_d_lb | 0.125 | 0.125 | yes |
| overrides and edits | p4_d_cubic | 54 | 54 | yes |
| overrides and edits | p4_d_over | no | No | intended: sentence case only, same status word |
| overrides and edits | p4_d_uspsdim | - | - | yes |
| overrides and edits | p4_d_uspsbill | 0.125 | 0.125 | yes |
| overrides and edits | p4_d_upsdim | 0.3885 | 0.3885 | yes |
| overrides and edits | p4_d_upsbill | 1 | 1 | yes |
| overrides and edits | p4_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| overrides and edits | p4_d_upsflag | ok | OK | intended: sentence case only, same status word |
| overrides and edits | p4_s_usps | 0.125 | 0.125 | yes |
| overrides and edits | p4_s_ups | 1 | 1 | yes |
| overrides and edits | p4_s_zone | 8 | 8 | yes |
| overrides and edits | p4_s_gacom | 8.4 | 8.4 | yes |
| overrides and edits | p4_s_garet | 9.45 | 9.45 | yes |
| overrides and edits | p4_s_pri | 15.22 | 15.22 | yes |
| overrides and edits | p4_s_upsgs | 21.0567 | 21.0567 | yes |
| overrides and edits | p4_s_cheap | 8.4 | 8.4 | yes |
| overrides and edits | p4_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| overrides and edits | p4_s_saved | 1.05 | 1.05 | yes |
| overrides and edits | p4_b_name | Sterling Silver Earrings | Sterling Silver Earrings | yes |
| overrides and edits | p4_b_sale | 42 | 42 | yes |
| overrides and edits | p4_b_ship | 0 | 0 | yes |
| overrides and edits | p4_b_true | 9.76 | 9.76 | yes |
| overrides and edits | p4_b_fees | 4.44 | 4.44 | yes |
| overrides and edits | p4_b_net | 16.8 | 16.8 | yes |
| overrides and edits | p4_b_margin | 0.4 | 0.4 | yes |
| overrides and edits | p4_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| overrides and edits | p4_b_flag | OK | OK | yes |
| overrides and edits | p5_postage | 6.2 | 6.2 | yes |
| overrides and edits | p5_labor | 1.5 | 1.5 | yes |
| overrides and edits | p5_true | 8.94 | 8.94 | yes |
| overrides and edits | p5_short | 0.01 | 0.01 | yes |
| overrides and edits | p5_flag | COVERED | Covered | intended: sentence case only, same status word |
| overrides and edits | p5_share | 0.6935 | 0.6935 | yes |
| overrides and edits | p5_d_name | Soy Candle 8 oz | Soy Candle 8 oz | yes |
| overrides and edits | p5_d_lb | 1.25 | 1.25 | yes |
| overrides and edits | p5_d_cubic | 216 | 216 | yes |
| overrides and edits | p5_d_over | no | No | intended: sentence case only, same status word |
| overrides and edits | p5_d_uspsdim | - | - | yes |
| overrides and edits | p5_d_uspsbill | 2 | 2 | yes |
| overrides and edits | p5_d_upsdim | 1.554 | 1.554 | yes |
| overrides and edits | p5_d_upsbill | 2 | 2 | yes |
| overrides and edits | p5_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| overrides and edits | p5_d_upsflag | ok | OK | intended: sentence case only, same status word |
| overrides and edits | p5_s_usps | 2 | 2 | yes |
| overrides and edits | p5_s_ups | 2 | 2 | yes |
| overrides and edits | p5_s_zone | 4 | 4 | yes |
| overrides and edits | p5_s_gacom | 8.51 | 8.51 | yes |
| overrides and edits | p5_s_garet | 13 | 13 | yes |
| overrides and edits | p5_s_pri | 10.79 | 10.79 | yes |
| overrides and edits | p5_s_upsgs | 21.6395 | 21.6395 | yes |
| overrides and edits | p5_s_cheap | 6.2 | 6.2 | yes |
| overrides and edits | p5_s_cheapname | Your quote A | Your quote A | yes |
| overrides and edits | p5_s_saved | 6.8 | 6.8 | yes |
| overrides and edits | p5_b_name | Soy Candle 8 oz | Soy Candle 8 oz | yes |
| overrides and edits | p5_b_sale | 22 | 22 | yes |
| overrides and edits | p5_b_ship | 8.95 | 8.95 | yes |
| overrides and edits | p5_b_true | 8.94 | 8.94 | yes |
| overrides and edits | p5_b_fees | 3.3902 | 3.3902 | yes |
| overrides and edits | p5_b_net | 13.0197 | 13.0197 | yes |
| overrides and edits | p5_b_margin | 0.4207 | 0.4207 | yes |
| overrides and edits | p5_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| overrides and edits | p5_b_flag | OK | OK | yes |
| overrides and edits | p6_postage | 19.62 | 19.62 | yes |
| overrides and edits | p6_labor | 3 | 3 | yes |
| overrides and edits | p6_true | 26.68 | 26.68 | yes |
| overrides and edits | p6_short | -11.73 | -11.73 | yes |
| overrides and edits | p6_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| overrides and edits | p6_share | 0.7354 | 0.7354 | yes |
| overrides and edits | p6_d_name | Grapevine Wreath 16 in | Grapevine Wreath 16 in | yes |
| overrides and edits | p6_d_lb | 2.5 | 2.5 | yes |
| overrides and edits | p6_d_cubic | 2,048 | 2,048 | yes |
| overrides and edits | p6_d_over | YES | Yes | intended: sentence case only, same status word |
| overrides and edits | p6_d_uspsdim | 12.3373 | 12.3373 | yes |
| overrides and edits | p6_d_uspsbill | 13 | 13 | yes |
| overrides and edits | p6_d_upsdim | 14.7338 | 14.7338 | yes |
| overrides and edits | p6_d_upsbill | 15 | 15 | yes |
| overrides and edits | p6_d_uspsflag | DIM WEIGHT BITES: +10 lb | Dim weight bites: +10 lb | intended: sentence case only, same status word |
| overrides and edits | p6_d_upsflag | DIM WEIGHT BITES: +12 lb | Dim weight bites: +12 lb | intended: sentence case only, same status word |
| overrides and edits | p6_s_usps | 13 | 13 | yes |
| overrides and edits | p6_s_ups | 15 | 15 | yes |
| overrides and edits | p6_s_zone | 5 | 5 | yes |
| overrides and edits | p6_s_gacom | 19.62 | 19.62 | yes |
| overrides and edits | p6_s_garet | 26.4 | 26.4 | yes |
| overrides and edits | p6_s_pri | 31.99 | 31.99 | yes |
| overrides and edits | p6_s_upsgs | 39.9637 | 39.9637 | yes |
| overrides and edits | p6_s_cheap | 19.62 | 19.62 | yes |
| overrides and edits | p6_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| overrides and edits | p6_s_saved | 6.78 | 6.78 | yes |
| overrides and edits | p6_b_name | Grapevine Wreath 16 in | Grapevine Wreath 16 in | yes |
| overrides and edits | p6_b_sale | 58 | 58 | yes |
| overrides and edits | p6_b_ship | 14.95 | 14.95 | yes |
| overrides and edits | p6_b_true | 26.68 | 26.68 | yes |
| overrides and edits | p6_b_fees | 7.3803 | 7.3803 | yes |
| overrides and edits | p6_b_net | 20.8897 | 20.8897 | yes |
| overrides and edits | p6_b_margin | 0.2864 | 0.2864 | yes |
| overrides and edits | p6_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| overrides and edits | p6_b_flag | OK | OK | yes |
| overrides and edits | p7_postage | 18.117 | 18.117 | yes |
| overrides and edits | p7_labor | 0.9 | 0.9 | yes |
| overrides and edits | p7_true | 19.327 | 19.327 | yes |
| overrides and edits | p7_short | -12.377 | -12.377 | yes |
| overrides and edits | p7_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| overrides and edits | p7_share | 0.9374 | 0.9374 | yes |
| overrides and edits | p7_d_name | Canvas Tote Bag | Canvas Tote Bag | yes |
| overrides and edits | p7_d_lb | 0.5625 | 0.5625 | yes |
| overrides and edits | p7_d_cubic | 180 | 180 | yes |
| overrides and edits | p7_d_over | no | No | intended: sentence case only, same status word |
| overrides and edits | p7_d_uspsdim | - | - | yes |
| overrides and edits | p7_d_uspsbill | 0.5625 | 0.5625 | yes |
| overrides and edits | p7_d_upsdim | 1.295 | 1.295 | yes |
| overrides and edits | p7_d_upsbill | 2 | 2 | yes |
| overrides and edits | p7_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| overrides and edits | p7_d_upsflag | DIM WEIGHT BITES: +1 lb | Dim weight bites: +1 lb | intended: sentence case only, same status word |
| overrides and edits | p7_s_usps | 0.5625 | 0.5625 | yes |
| overrides and edits | p7_s_ups | 2 | 2 | yes |
| overrides and edits | p7_s_zone | 2 | 2 | yes |
| overrides and edits | p7_s_gacom | 6.94 | 6.94 | yes |
| overrides and edits | p7_s_garet | 9.95 | 9.95 | yes |
| overrides and edits | p7_s_pri | 9.32 | 9.32 | yes |
| overrides and edits | p7_s_upsgs | 18.117 | 18.117 | yes |
| overrides and edits | p7_s_cheap | 6.94 | 6.94 | yes |
| overrides and edits | p7_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| overrides and edits | p7_s_saved | 3.01 | 3.01 | yes |
| overrides and edits | p7_b_name | Canvas Tote Bag | Canvas Tote Bag | yes |
| overrides and edits | p7_b_sale | 30 | 30 | yes |
| overrides and edits | p7_b_ship | 6.95 | 6.95 | yes |
| overrides and edits | p7_b_true | 19.327 | 19.327 | yes |
| overrides and edits | p7_b_fees | 3.9603 | 3.9603 | yes |
| overrides and edits | p7_b_net | 4.1627 | 4.1627 | yes |
| overrides and edits | p7_b_margin | 0.1127 | 0.1127 | yes |
| overrides and edits | p7_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| overrides and edits | p7_b_flag | THIN | Thin | intended: sentence case only, same status word |
| overrides and edits | p8_postage | 5.1 | 5.1 | yes |
| overrides and edits | p8_labor | 1.2 | 1.2 | yes |
| overrides and edits | p8_true | 7.16 | 7.16 | yes |
| overrides and edits | p8_short | 2.79 | 2.79 | yes |
| overrides and edits | p8_flag | COVERED | Covered | intended: sentence case only, same status word |
| overrides and edits | p8_share | 0.7123 | 0.7123 | yes |
| overrides and edits | p8_d_name | Handmade Soap Set (3) | Handmade Soap Set (3) | yes |
| overrides and edits | p8_d_lb | 0.875 | 0.875 | yes |
| overrides and edits | p8_d_cubic | 105 | 105 | yes |
| overrides and edits | p8_d_over | no | No | intended: sentence case only, same status word |
| overrides and edits | p8_d_uspsdim | - | - | yes |
| overrides and edits | p8_d_uspsbill | 0.875 | 0.875 | yes |
| overrides and edits | p8_d_upsdim | 0.7554 | 0.7554 | yes |
| overrides and edits | p8_d_upsbill | 1 | 1 | yes |
| overrides and edits | p8_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| overrides and edits | p8_d_upsflag | ok | OK | intended: sentence case only, same status word |
| overrides and edits | p8_s_usps | 0.875 | 0.875 | yes |
| overrides and edits | p8_s_ups | 1 | 1 | yes |
| overrides and edits | p8_s_zone | 5 | 5 | yes |
| overrides and edits | p8_s_gacom | 7.69 | 7.69 | yes |
| overrides and edits | p8_s_garet | 10.95 | 10.95 | yes |
| overrides and edits | p8_s_pri | 12.97 | 12.97 | yes |
| overrides and edits | p8_s_upsgs | 19.8265 | 19.8265 | yes |
| overrides and edits | p8_s_cheap | 5.1 | 5.1 | yes |
| overrides and edits | p8_s_cheapname | Your quote B | Your quote B | yes |
| overrides and edits | p8_s_saved | 5.85 | 5.85 | yes |
| overrides and edits | p8_b_name | Handmade Soap Set (3) | Handmade Soap Set (3) | yes |
| overrides and edits | p8_b_sale | 26 | 26 | yes |
| overrides and edits | p8_b_ship | 9.95 | 9.95 | yes |
| overrides and edits | p8_b_true | 7.16 | 7.16 | yes |
| overrides and edits | p8_b_fees | 3.8653 | 3.8653 | yes |
| overrides and edits | p8_b_net | 18.9247 | 18.9247 | yes |
| overrides and edits | p8_b_margin | 0.5264 | 0.5264 | yes |
| overrides and edits | p8_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| overrides and edits | p8_b_flag | OK | OK | yes |
| overrides and edits | p9_postage | 9.99 | 9.99 | yes |
| overrides and edits | p9_labor | 1.5 | 1.5 | yes |
| overrides and edits | p9_true | 12.88 | 12.88 | yes |
| overrides and edits | p9_short | 0.07 | 0.07 | yes |
| overrides and edits | p9_flag | COVERED | Covered | intended: sentence case only, same status word |
| overrides and edits | p9_share | 0.7756 | 0.7756 | yes |
| overrides and edits | p9_d_name | Wooden Puzzle | Wooden Puzzle | yes |
| overrides and edits | p9_d_lb | 1.875 | 1.875 | yes |
| overrides and edits | p9_d_cubic | 160 | 160 | yes |
| overrides and edits | p9_d_over | no | No | intended: sentence case only, same status word |
| overrides and edits | p9_d_uspsdim | - | - | yes |
| overrides and edits | p9_d_uspsbill | 2 | 2 | yes |
| overrides and edits | p9_d_upsdim | 1.1511 | 1.1511 | yes |
| overrides and edits | p9_d_upsbill | 2 | 2 | yes |
| overrides and edits | p9_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| overrides and edits | p9_d_upsflag | ok | OK | intended: sentence case only, same status word |
| overrides and edits | p9_s_usps | 2 | 2 | yes |
| overrides and edits | p9_s_ups | 2 | 2 | yes |
| overrides and edits | p9_s_zone | 4 | 4 | yes |
| overrides and edits | p9_s_gacom | 8.51 | 8.51 | yes |
| overrides and edits | p9_s_garet | 13 | 13 | yes |
| overrides and edits | p9_s_pri | 10.79 | 10.79 | yes |
| overrides and edits | p9_s_upsgs | 21.6395 | 21.6395 | yes |
| overrides and edits | p9_s_cheap | 8.51 | 8.51 | yes |
| overrides and edits | p9_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| overrides and edits | p9_s_saved | 4.49 | 4.49 | yes |
| overrides and edits | p9_b_name | Wooden Puzzle | Wooden Puzzle | yes |
| overrides and edits | p9_b_sale | 34 | 34 | yes |
| overrides and edits | p9_b_ship | 12.95 | 12.95 | yes |
| overrides and edits | p9_b_true | 12.88 | 12.88 | yes |
| overrides and edits | p9_b_fees | 4.9103 | 4.9103 | yes |
| overrides and edits | p9_b_net | 20.1598 | 20.1598 | yes |
| overrides and edits | p9_b_margin | 0.4294 | 0.4294 | yes |
| overrides and edits | p9_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| overrides and edits | p9_b_flag | OK | OK | yes |
| overrides and edits | p10_postage | 12.84 | 12.84 | yes |
| overrides and edits | p10_labor | 2.1 | 2.1 | yes |
| overrides and edits | p10_true | 16.85 | 16.85 | yes |
| overrides and edits | p10_short | 1.1 | 1.1 | yes |
| overrides and edits | p10_flag | COVERED | Covered | intended: sentence case only, same status word |
| overrides and edits | p10_share | 0.762 | 0.762 | yes |
| overrides and edits | p10_d_name | Board Game | Board Game | yes |
| overrides and edits | p10_d_lb | 3.75 | 3.75 | yes |
| overrides and edits | p10_d_cubic | 432 | 432 | yes |
| overrides and edits | p10_d_over | no | No | intended: sentence case only, same status word |
| overrides and edits | p10_d_uspsdim | - | - | yes |
| overrides and edits | p10_d_uspsbill | 4 | 4 | yes |
| overrides and edits | p10_d_upsdim | 3.1079 | 3.1079 | yes |
| overrides and edits | p10_d_upsbill | 4 | 4 | yes |
| overrides and edits | p10_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| overrides and edits | p10_d_upsflag | ok | OK | intended: sentence case only, same status word |
| overrides and edits | p10_s_usps | 4 | 4 | yes |
| overrides and edits | p10_s_ups | 4 | 4 | yes |
| overrides and edits | p10_s_zone | 5 | 5 | yes |
| overrides and edits | p10_s_gacom | 12.84 | 12.84 | yes |
| overrides and edits | p10_s_garet | 16.4 | 16.4 | yes |
| overrides and edits | p10_s_pri | 19.88 | 19.88 | yes |
| overrides and edits | p10_s_upsgs | 24.9287 | 24.9287 | yes |
| overrides and edits | p10_s_cheap | 12.84 | 12.84 | yes |
| overrides and edits | p10_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| overrides and edits | p10_s_saved | 3.56 | 3.56 | yes |
| overrides and edits | p10_b_name | Board Game | Board Game | yes |
| overrides and edits | p10_b_sale | 48 | 48 | yes |
| overrides and edits | p10_b_ship | 17.95 | 17.95 | yes |
| overrides and edits | p10_b_true | 16.85 | 16.85 | yes |
| overrides and edits | p10_b_fees | 6.7153 | 6.7153 | yes |
| overrides and edits | p10_b_net | 26.3848 | 26.3848 | yes |
| overrides and edits | p10_b_margin | 0.4001 | 0.4001 | yes |
| overrides and edits | p10_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| overrides and edits | p10_b_flag | OK | OK | yes |
| overrides and edits | p11_postage | 7.86 | 7.86 | yes |
| overrides and edits | p11_labor | 0.6 | 0.6 | yes |
| overrides and edits | p11_true | 8.86 | 8.86 | yes |
| overrides and edits | p11_short | -3.86 | -3.86 | yes |
| overrides and edits | p11_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| overrides and edits | p11_share | 0.8871 | 0.8871 | yes |
| overrides and edits | p11_d_name | Notebook | Notebook | yes |
| overrides and edits | p11_d_lb | 0.6875 | 0.6875 | yes |
| overrides and edits | p11_d_cubic | 63 | 63 | yes |
| overrides and edits | p11_d_over | no | No | intended: sentence case only, same status word |
| overrides and edits | p11_d_uspsdim | - | - | yes |
| overrides and edits | p11_d_uspsbill | 0.6875 | 0.6875 | yes |
| overrides and edits | p11_d_upsdim | 0.4532 | 0.4532 | yes |
| overrides and edits | p11_d_upsbill | 1 | 1 | yes |
| overrides and edits | p11_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| overrides and edits | p11_d_upsflag | ok | OK | intended: sentence case only, same status word |
| overrides and edits | p11_s_usps | 0.6875 | 0.6875 | yes |
| overrides and edits | p11_s_ups | 1 | 1 | yes |
| overrides and edits | p11_s_zone | 6 | 6 | yes |
| overrides and edits | p11_s_gacom | 7.86 | 7.86 | yes |
| overrides and edits | p11_s_garet | 11.35 | 11.35 | yes |
| overrides and edits | p11_s_pri | 14.47 | 14.47 | yes |
| overrides and edits | p11_s_upsgs | 20.4869 | 20.4869 | yes |
| overrides and edits | p11_s_cheap | 7.86 | 7.86 | yes |
| overrides and edits | p11_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| overrides and edits | p11_s_saved | 3.49 | 3.49 | yes |
| overrides and edits | p11_b_name | Notebook | Notebook | yes |
| overrides and edits | p11_b_sale | 15 | 15 | yes |
| overrides and edits | p11_b_ship | 5 | 5 | yes |
| overrides and edits | p11_b_true | 8.86 | 8.86 | yes |
| overrides and edits | p11_b_fees | 2.35 | 2.35 | yes |
| overrides and edits | p11_b_net | 4.79 | 4.79 | yes |
| overrides and edits | p11_b_margin | 0.2395 | 0.2395 | yes |
| overrides and edits | p11_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| overrides and edits | p11_b_flag | OK | OK | yes |
| overrides and edits | p12_postage | (blank) | (blank) | yes |
| overrides and edits | p12_labor | (blank) | (blank) | yes |
| overrides and edits | p12_true | (blank) | (blank) | yes |
| overrides and edits | p12_short | (blank) | (blank) | yes |
| overrides and edits | p12_flag | (blank) | (blank) | yes |
| overrides and edits | p12_share | (blank) | (blank) | yes |
| overrides and edits | p12_d_name | (blank) | (blank) | yes |
| overrides and edits | p12_d_lb | (blank) | (blank) | yes |
| overrides and edits | p12_d_cubic | (blank) | (blank) | yes |
| overrides and edits | p12_d_over | (blank) | (blank) | yes |
| overrides and edits | p12_d_uspsdim | (blank) | (blank) | yes |
| overrides and edits | p12_d_uspsbill | (blank) | (blank) | yes |
| overrides and edits | p12_d_upsdim | (blank) | (blank) | yes |
| overrides and edits | p12_d_upsbill | (blank) | (blank) | yes |
| overrides and edits | p12_d_uspsflag | (blank) | (blank) | yes |
| overrides and edits | p12_d_upsflag | (blank) | (blank) | yes |
| overrides and edits | p12_s_usps | (blank) | (blank) | yes |
| overrides and edits | p12_s_ups | (blank) | (blank) | yes |
| overrides and edits | p12_s_zone | (blank) | (blank) | yes |
| overrides and edits | p12_s_gacom | (blank) | (blank) | yes |
| overrides and edits | p12_s_garet | (blank) | (blank) | yes |
| overrides and edits | p12_s_pri | (blank) | (blank) | yes |
| overrides and edits | p12_s_upsgs | (blank) | (blank) | yes |
| overrides and edits | p12_s_cheap | (blank) | (blank) | yes |
| overrides and edits | p12_s_cheapname | (blank) | (blank) | yes |
| overrides and edits | p12_s_saved | (blank) | (blank) | yes |
| overrides and edits | p12_b_name | (blank) | (blank) | yes |
| overrides and edits | p12_b_sale | (blank) | (blank) | yes |
| overrides and edits | p12_b_ship | (blank) | (blank) | yes |
| overrides and edits | p12_b_true | (blank) | (blank) | yes |
| overrides and edits | p12_b_fees | (blank) | (blank) | yes |
| overrides and edits | p12_b_net | (blank) | (blank) | yes |
| overrides and edits | p12_b_margin | (blank) | (blank) | yes |
| overrides and edits | p12_b_shipflag | (blank) | (blank) | yes |
| overrides and edits | p12_b_flag | (blank) | (blank) | yes |
| overrides and edits | p30_postage | (blank) | (blank) | yes |
| overrides and edits | p30_labor | (blank) | (blank) | yes |
| overrides and edits | p30_true | (blank) | (blank) | yes |
| overrides and edits | p30_short | (blank) | (blank) | yes |
| overrides and edits | p30_flag | (blank) | (blank) | yes |
| overrides and edits | p30_share | (blank) | (blank) | yes |
| overrides and edits | p30_d_name | (blank) | (blank) | yes |
| overrides and edits | p30_d_lb | (blank) | (blank) | yes |
| overrides and edits | p30_d_cubic | (blank) | (blank) | yes |
| overrides and edits | p30_d_over | (blank) | (blank) | yes |
| overrides and edits | p30_d_uspsdim | (blank) | (blank) | yes |
| overrides and edits | p30_d_uspsbill | (blank) | (blank) | yes |
| overrides and edits | p30_d_upsdim | (blank) | (blank) | yes |
| overrides and edits | p30_d_upsbill | (blank) | (blank) | yes |
| overrides and edits | p30_d_uspsflag | (blank) | (blank) | yes |
| overrides and edits | p30_d_upsflag | (blank) | (blank) | yes |
| overrides and edits | p30_s_usps | (blank) | (blank) | yes |
| overrides and edits | p30_s_ups | (blank) | (blank) | yes |
| overrides and edits | p30_s_zone | (blank) | (blank) | yes |
| overrides and edits | p30_s_gacom | (blank) | (blank) | yes |
| overrides and edits | p30_s_garet | (blank) | (blank) | yes |
| overrides and edits | p30_s_pri | (blank) | (blank) | yes |
| overrides and edits | p30_s_upsgs | (blank) | (blank) | yes |
| overrides and edits | p30_s_cheap | (blank) | (blank) | yes |
| overrides and edits | p30_s_cheapname | (blank) | (blank) | yes |
| overrides and edits | p30_s_saved | (blank) | (blank) | yes |
| overrides and edits | p30_b_name | (blank) | (blank) | yes |
| overrides and edits | p30_b_sale | (blank) | (blank) | yes |
| overrides and edits | p30_b_ship | (blank) | (blank) | yes |
| overrides and edits | p30_b_true | (blank) | (blank) | yes |
| overrides and edits | p30_b_fees | (blank) | (blank) | yes |
| overrides and edits | p30_b_net | (blank) | (blank) | yes |
| overrides and edits | p30_b_margin | (blank) | (blank) | yes |
| overrides and edits | p30_b_shipflag | (blank) | (blank) | yes |
| overrides and edits | p30_b_flag | (blank) | (blank) | yes |
| overrides and edits | avg_true | 14.0506 | 14.0506 | yes |
| overrides and edits | avg_short | -5.087 | -5.087 | yes |
| overrides and edits | avg_share | 0.7844 | 0.7844 | yes |
| overrides and edits | sc_cheap_total | 107.88 | 107.88 | yes |
| overrides and edits | sc_saved_total | 43.17 | 43.17 | yes |
| overrides and edits | db_losing | 0 | 0 | yes |
| overrides and edits | db_under | 7 | 7 | yes |
| overrides and edits | db_avgtrue | 14.0506 | 14.0506 | yes |
| overrides and edits | db_avgshort | -5.087 | -5.087 | yes |
| overrides and edits | db_shipcost | 154.5571 | 154.5571 | yes |
| overrides and edits | db_collected | 98.6 | 98.6 | yes |
| overrides and edits | db_netship | -55.9571 | -55.9571 | yes |
| overrides and edits | db_share | 0.7844 | 0.7844 | yes |
| overrides and edits | db_tot_true | 154.5571 | 154.5571 | yes |
| overrides and edits | db_tot_fees | 51.082 | 51.082 | yes |
| overrides and edits | db_tot_net | 158.361 | 158.361 | yes |
| overrides and edits | fs_tc | 14.0506 | 14.0506 | yes |
| overrides and edits | fs_tcused | 10 | 10 | yes |
| overrides and edits | fs_profit_order | 18.1 | 18.1 | yes |
| overrides and edits | fs_cost | 6.5 | 6.5 | yes |
| overrides and edits | fs_breakeven | 62.4444 | 62.4444 | yes |
| overrides and edits | fs_recommendation | Best of the three: free shipping over $75, about $455 more profit per 100 orders than today. An estimate built on your assumptions above, not a promise. | Best of the three: free shipping over $75, about $455 more profit per 100 orders than today. An estimate built on your assumptions above, not a promise. | yes |
| overrides and edits | fs_avgo_today | 48 | 48 | yes |
| overrides and edits | fs_avgo_s1 | 48 | 48 | yes |
| overrides and edits | fs_avgo_s2 | 48 | 48 | yes |
| overrides and edits | fs_avgo_s3 | 48 | 48 | yes |
| overrides and edits | fs_orders_today | 100 | 100 | yes |
| overrides and edits | fs_orders_s1 | 115 | 115 | yes |
| overrides and edits | fs_orders_s2 | 115 | 115 | yes |
| overrides and edits | fs_orders_s3 | 115 | 115 | yes |
| overrides and edits | fs_qual_today | 0 | 0 | yes |
| overrides and edits | fs_qual_s1 | 63.25 | 63.25 | yes |
| overrides and edits | fs_qual_s2 | 34.5 | 34.5 | yes |
| overrides and edits | fs_qual_s3 | 13.8 | 13.8 | yes |
| overrides and edits | fs_other_today | 100 | 100 | yes |
| overrides and edits | fs_other_s1 | 51.75 | 51.75 | yes |
| overrides and edits | fs_other_s2 | 80.5 | 80.5 | yes |
| overrides and edits | fs_other_s3 | 101.2 | 101.2 | yes |
| overrides and edits | fs_rev_today | 4,800 | 4,800 | yes |
| overrides and edits | fs_rev_s1 | 5,646.5 | 5,646.5 | yes |
| overrides and edits | fs_rev_s2 | 6,072 | 6,072 | yes |
| overrides and edits | fs_rev_s3 | 6,127.2 | 6,127.2 | yes |
| overrides and edits | fs_coll_today | 650 | 650 | yes |
| overrides and edits | fs_coll_s1 | 336.375 | 336.375 | yes |
| overrides and edits | fs_coll_s2 | 523.25 | 523.25 | yes |
| overrides and edits | fs_coll_s3 | 657.8 | 657.8 | yes |
| overrides and edits | fs_parc_today | 1,000 | 1,000 | yes |
| overrides and edits | fs_parc_s1 | 1,150 | 1,150 | yes |
| overrides and edits | fs_parc_s2 | 1,150 | 1,150 | yes |
| overrides and edits | fs_parc_s3 | 1,150 | 1,150 | yes |
| overrides and edits | fs_profit_today | 1,810 | 1,810 | yes |
| overrides and edits | fs_profit_s1 | 1,727.3 | 1,727.3 | yes |
| overrides and edits | fs_profit_s2 | 2,105.65 | 2,105.65 | yes |
| overrides and edits | fs_profit_s3 | 2,265.04 | 2,265.04 | yes |
| overrides and edits | fs_per_today | 18.1 | 18.1 | yes |
| overrides and edits | fs_per_s1 | 15.02 | 15.02 | yes |
| overrides and edits | fs_per_s2 | 18.31 | 18.31 | yes |
| overrides and edits | fs_per_s3 | 19.696 | 19.696 | yes |
| overrides and edits | fs_chg_today | 0 | 0 | yes |
| overrides and edits | fs_chg_s1 | -82.7 | -82.7 | yes |
| overrides and edits | fs_chg_s2 | 295.65 | 295.65 | yes |
| overrides and edits | fs_chg_s3 | 455.04 | 455.04 | yes |
| overrides and edits | fs_verdict_today | baseline | Today | intended: baseline column now reads Today |
| overrides and edits | fs_verdict_s1 | WORSE THAN TODAY | Worse than today | intended: sentence case only, same status word |
| overrides and edits | fs_verdict_s2 | BEATS TODAY | Beats today | intended: sentence case only, same status word |
| overrides and edits | fs_verdict_s3 | BEATS TODAY | Beats today | intended: sentence case only, same status word |
| edge | p1_postage | 9.95 | 9.95 | yes |
| edge | p1_labor | 1.8 | 1.8 | yes |
| edge | p1_true | 13.19 | 13.19 | yes |
| edge | p1_short | -8.24 | -8.24 | yes |
| edge | p1_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| edge | p1_share | 0.7544 | 0.7544 | yes |
| edge | p1_d_name | Ceramic Mug 12 oz | Ceramic Mug 12 oz | yes |
| edge | p1_d_lb | 1.125 | 1.125 | yes |
| edge | p1_d_cubic | 288 | 288 | yes |
| edge | p1_d_over | no | No | intended: sentence case only, same status word |
| edge | p1_d_uspsdim | - | - | yes |
| edge | p1_d_uspsbill | 2 | 2 | yes |
| edge | p1_d_upsdim | 0.72 | 0.72 | yes |
| edge | p1_d_upsbill | 2 | 2 | yes |
| edge | p1_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| edge | p1_d_upsflag | ok | OK | intended: sentence case only, same status word |
| edge | p1_s_usps | 2 | 2 | yes |
| edge | p1_s_ups | 2 | 2 | yes |
| edge | p1_s_zone | 5 | 5 | yes |
| edge | p1_s_gacom | 9.95 | 9.95 | yes |
| edge | p1_s_garet | 14.1 | 14.1 | yes |
| edge | p1_s_pri | 13.17 | 13.17 | yes |
| edge | p1_s_upsgs | 22.1057 | 22.1057 | yes |
| edge | p1_s_cheap | 9.95 | 9.95 | yes |
| edge | p1_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| edge | p1_s_saved | 4.15 | 4.15 | yes |
| edge | p1_b_name | Ceramic Mug 12 oz | Ceramic Mug 12 oz | yes |
| edge | p1_b_sale | 19 | 19 | yes |
| edge | p1_b_ship | 4.95 | 4.95 | yes |
| edge | p1_b_true | 13.19 | 13.19 | yes |
| edge | p1_b_fees | 2.7252 | 2.7252 | yes |
| edge | p1_b_net | -0.4652 | -0.4652 | yes |
| edge | p1_b_margin | -0.0194 | -0.0194 | yes |
| edge | p1_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| edge | p1_b_flag | LOSING MONEY | Losing money | intended: sentence case only, same status word |
| edge | p2_postage | 7.3 | 7.3 | yes |
| edge | p2_labor | 0.9 | 0.9 | yes |
| edge | p2_true | 8.48 | 8.48 | yes |
| edge | p2_short | -3.53 | -3.53 | yes |
| edge | p2_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| edge | p2_share | 0.8608 | 0.8608 | yes |
| edge | p2_d_name | Graphic T-Shirt | Graphic T-Shirt | yes |
| edge | p2_d_lb | 0.4375 | 0.4375 | yes |
| edge | p2_d_cubic | 130 | 130 | yes |
| edge | p2_d_over | no | No | intended: sentence case only, same status word |
| edge | p2_d_uspsdim | - | - | yes |
| edge | p2_d_uspsbill | 0.4375 | 0.4375 | yes |
| edge | p2_d_upsdim | 0.325 | 0.325 | yes |
| edge | p2_d_upsbill | 1 | 1 | yes |
| edge | p2_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| edge | p2_d_upsflag | ok | OK | intended: sentence case only, same status word |
| edge | p2_s_usps | 0.4375 | 0.4375 | yes |
| edge | p2_s_ups | 1 | 1 | yes |
| edge | p2_s_zone | 3 | 3 | yes |
| edge | p2_s_gacom | 7.3 | 7.3 | yes |
| edge | p2_s_garet | 8.15 | 8.15 | yes |
| edge | p2_s_pri | 9.71 | 9.71 | yes |
| edge | p2_s_upsgs | 17.4954 | 17.4954 | yes |
| edge | p2_s_cheap | 7.3 | 7.3 | yes |
| edge | p2_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| edge | p2_s_saved | 0.85 | 0.85 | yes |
| edge | p2_b_name | Graphic T-Shirt | Graphic T-Shirt | yes |
| edge | p2_b_sale | 28 | 28 | yes |
| edge | p2_b_ship | 4.95 | 4.95 | yes |
| edge | p2_b_true | 8.48 | 8.48 | yes |
| edge | p2_b_fees | 3.5803 | 3.5803 | yes |
| edge | p2_b_net | 8.8898 | 8.8898 | yes |
| edge | p2_b_margin | 0.2698 | 0.2698 | yes |
| edge | p2_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| edge | p2_b_flag | OK | OK | yes |
| edge | p3_postage | 16.89 | 16.89 | yes |
| edge | p3_labor | 3.6 | 3.6 | yes |
| edge | p3_true | 24.2 | 24.2 | yes |
| edge | p3_short | -12.2 | -12.2 | yes |
| edge | p3_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| edge | p3_share | 0.6979 | 0.6979 | yes |
| edge | p3_d_name | Framed Print 11x14 | Framed Print 11x14 | yes |
| edge | p3_d_lb | 3.25 | 3.25 | yes |
| edge | p3_d_cubic | 756 | 756 | yes |
| edge | p3_d_over | YES | Yes | intended: sentence case only, same status word |
| edge | p3_d_uspsdim | 5.4388 | 5.4388 | yes |
| edge | p3_d_uspsbill | 6 | 6 | yes |
| edge | p3_d_upsdim | 1.89 | 1.89 | yes |
| edge | p3_d_upsbill | 4 | 4 | yes |
| edge | p3_d_uspsflag | DIM WEIGHT BITES: +2 lb | Dim weight bites: +2 lb | intended: sentence case only, same status word |
| edge | p3_d_upsflag | ok | OK | intended: sentence case only, same status word |
| edge | p3_s_usps | 6 | 6 | yes |
| edge | p3_s_ups | 4 | 4 | yes |
| edge | p3_s_zone | 6 | 6 | yes |
| edge | p3_s_gacom | 16.89 | 16.89 | yes |
| edge | p3_s_garet | 21.05 | 21.05 | yes |
| edge | p3_s_pri | 28.16 | 28.16 | yes |
| edge | p3_s_upsgs | 25.6021 | 25.6021 | yes |
| edge | p3_s_cheap | 16.89 | 16.89 | yes |
| edge | p3_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| edge | p3_s_saved | 4.16 | 4.16 | yes |
| edge | p3_b_name | Framed Print 11x14 | Framed Print 11x14 | yes |
| edge | p3_b_sale | 65 | 65 | yes |
| edge | p3_b_ship | 12 | 12 | yes |
| edge | p3_b_true | 24.2 | 24.2 | yes |
| edge | p3_b_fees | 7.765 | 7.765 | yes |
| edge | p3_b_net | 23.035 | 23.035 | yes |
| edge | p3_b_margin | 0.2992 | 0.2992 | yes |
| edge | p3_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| edge | p3_b_flag | OK | OK | yes |
| edge | p4_postage | 8.4 | 8.4 | yes |
| edge | p4_labor | 0.9 | 0.9 | yes |
| edge | p4_true | 9.76 | 9.76 | yes |
| edge | p4_short | -9.76 | -9.76 | yes |
| edge | p4_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| edge | p4_share | 0.8607 | 0.8607 | yes |
| edge | p4_d_name | Sterling Silver Earrings | Sterling Silver Earrings | yes |
| edge | p4_d_lb | 0.125 | 0.125 | yes |
| edge | p4_d_cubic | 54 | 54 | yes |
| edge | p4_d_over | no | No | intended: sentence case only, same status word |
| edge | p4_d_uspsdim | - | - | yes |
| edge | p4_d_uspsbill | 0.125 | 0.125 | yes |
| edge | p4_d_upsdim | 0.135 | 0.135 | yes |
| edge | p4_d_upsbill | 1 | 1 | yes |
| edge | p4_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| edge | p4_d_upsflag | ok | OK | intended: sentence case only, same status word |
| edge | p4_s_usps | 0.125 | 0.125 | yes |
| edge | p4_s_ups | 1 | 1 | yes |
| edge | p4_s_zone | 8 | 8 | yes |
| edge | p4_s_gacom | 8.4 | 8.4 | yes |
| edge | p4_s_garet | 9.45 | 9.45 | yes |
| edge | p4_s_pri | 15.22 | 15.22 | yes |
| edge | p4_s_upsgs | 21.0567 | 21.0567 | yes |
| edge | p4_s_cheap | 8.4 | 8.4 | yes |
| edge | p4_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| edge | p4_s_saved | 1.05 | 1.05 | yes |
| edge | p4_b_name | Sterling Silver Earrings | Sterling Silver Earrings | yes |
| edge | p4_b_sale | 42 | 42 | yes |
| edge | p4_b_ship | 0 | 0 | yes |
| edge | p4_b_true | 9.76 | 9.76 | yes |
| edge | p4_b_fees | 4.44 | 4.44 | yes |
| edge | p4_b_net | 16.8 | 16.8 | yes |
| edge | p4_b_margin | 0.4 | 0.4 | yes |
| edge | p4_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| edge | p4_b_flag | OK | OK | yes |
| edge | p5_postage | 8.51 | 8.51 | yes |
| edge | p5_labor | 1.5 | 1.5 | yes |
| edge | p5_true | 11.25 | 11.25 | yes |
| edge | p5_short | -2.3 | -2.3 | yes |
| edge | p5_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| edge | p5_share | 0.7564 | 0.7564 | yes |
| edge | p5_d_name | Soy Candle 8 oz | Soy Candle 8 oz | yes |
| edge | p5_d_lb | 1.25 | 1.25 | yes |
| edge | p5_d_cubic | 216 | 216 | yes |
| edge | p5_d_over | no | No | intended: sentence case only, same status word |
| edge | p5_d_uspsdim | - | - | yes |
| edge | p5_d_uspsbill | 2 | 2 | yes |
| edge | p5_d_upsdim | 0.54 | 0.54 | yes |
| edge | p5_d_upsbill | 2 | 2 | yes |
| edge | p5_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| edge | p5_d_upsflag | ok | OK | intended: sentence case only, same status word |
| edge | p5_s_usps | 2 | 2 | yes |
| edge | p5_s_ups | 2 | 2 | yes |
| edge | p5_s_zone | 4 | 4 | yes |
| edge | p5_s_gacom | 8.51 | 8.51 | yes |
| edge | p5_s_garet | 13 | 13 | yes |
| edge | p5_s_pri | 10.79 | 10.79 | yes |
| edge | p5_s_upsgs | 21.6395 | 21.6395 | yes |
| edge | p5_s_cheap | 8.51 | 8.51 | yes |
| edge | p5_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| edge | p5_s_saved | 4.49 | 4.49 | yes |
| edge | p5_b_name | Soy Candle 8 oz | Soy Candle 8 oz | yes |
| edge | p5_b_sale | 22 | 22 | yes |
| edge | p5_b_ship | 8.95 | 8.95 | yes |
| edge | p5_b_true | 11.25 | 11.25 | yes |
| edge | p5_b_fees | 3.3902 | 3.3902 | yes |
| edge | p5_b_net | 10.7097 | 10.7097 | yes |
| edge | p5_b_margin | 0.346 | 0.346 | yes |
| edge | p5_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| edge | p5_b_flag | OK | OK | yes |
| edge | p6_postage | (blank) | (blank) | yes |
| edge | p6_labor | 3 | 3 | yes |
| edge | p6_true | (blank) | (blank) | yes |
| edge | p6_short | (blank) | (blank) | yes |
| edge | p6_flag | ENTER POSTAGE | Enter postage | intended: sentence case only, same status word |
| edge | p6_share | (blank) | (blank) | yes |
| edge | p6_d_name | Grapevine Wreath 16 in | Grapevine Wreath 16 in | yes |
| edge | p6_d_lb | 68.75 | 68.75 | yes |
| edge | p6_d_cubic | 27,000 | 27,000 | yes |
| edge | p6_d_over | YES | Yes | intended: sentence case only, same status word |
| edge | p6_d_uspsdim | 194.2446 | 194.2446 | yes |
| edge | p6_d_uspsbill | 195 | 195 | yes |
| edge | p6_d_upsdim | 67.5 | 67.5 | yes |
| edge | p6_d_upsbill | 69 | 69 | yes |
| edge | p6_d_uspsflag | DIM WEIGHT BITES: +126 lb | Dim weight bites: +126 lb | intended: sentence case only, same status word |
| edge | p6_d_upsflag | ok | OK | intended: sentence case only, same status word |
| edge | p6_s_usps | 195 | 195 | yes |
| edge | p6_s_ups | 69 | 69 | yes |
| edge | p6_s_zone | 5 | 5 | yes |
| edge | p6_s_gacom | over 20 lb | over 20 lb | yes |
| edge | p6_s_garet | over 20 lb | over 20 lb | yes |
| edge | p6_s_pri | over 20 lb | over 20 lb | yes |
| edge | p6_s_upsgs | over 20 lb | over 20 lb | yes |
| edge | p6_s_cheap | (blank) | (blank) | yes |
| edge | p6_s_cheapname | (blank) | (blank) | yes |
| edge | p6_s_saved | (blank) | (blank) | yes |
| edge | p6_b_name | Grapevine Wreath 16 in | Grapevine Wreath 16 in | yes |
| edge | p6_b_sale | 58 | 58 | yes |
| edge | p6_b_ship | 14.95 | 14.95 | yes |
| edge | p6_b_true | (blank) | (blank) | yes |
| edge | p6_b_fees | 7.3803 | 7.3803 | yes |
| edge | p6_b_net | (blank) | (blank) | yes |
| edge | p6_b_margin | (blank) | (blank) | yes |
| edge | p6_b_shipflag | ENTER POSTAGE | Enter postage | intended: sentence case only, same status word |
| edge | p6_b_flag | (blank) | (blank) | yes |
| edge | p7_postage | 8.4 | 8.4 | yes |
| edge | p7_labor | 0.9 | 0.9 | yes |
| edge | p7_true | 9.61 | 9.61 | yes |
| edge | p7_short | -2.66 | -2.66 | yes |
| edge | p7_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| edge | p7_share | 0.8741 | 0.8741 | yes |
| edge | p7_d_name | Canvas Tote Bag | Canvas Tote Bag | yes |
| edge | p7_d_lb | 0.5625 | 0.5625 | yes |
| edge | p7_d_cubic | 180 | 180 | yes |
| edge | p7_d_over | no | No | intended: sentence case only, same status word |
| edge | p7_d_uspsdim | - | - | yes |
| edge | p7_d_uspsbill | 0.5625 | 0.5625 | yes |
| edge | p7_d_upsdim | 0.45 | 0.45 | yes |
| edge | p7_d_upsbill | 1 | 1 | yes |
| edge | p7_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| edge | p7_d_upsflag | ok | OK | intended: sentence case only, same status word |
| edge | p7_s_usps | 0.5625 | 0.5625 | yes |
| edge | p7_s_ups | 1 | 1 | yes |
| edge | p7_s_zone | 9 | 9 | yes |
| edge | p7_s_gacom | 8.4 | 8.4 | yes |
| edge | p7_s_garet | 12.9 | 12.9 | yes |
| edge | p7_s_pri | 32.48 | 32.48 | yes |
| edge | p7_s_upsgs | n/a | n/a | yes |
| edge | p7_s_cheap | 8.4 | 8.4 | yes |
| edge | p7_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| edge | p7_s_saved | 4.5 | 4.5 | yes |
| edge | p7_b_name | Canvas Tote Bag | Canvas Tote Bag | yes |
| edge | p7_b_sale | 30 | 30 | yes |
| edge | p7_b_ship | 6.95 | 6.95 | yes |
| edge | p7_b_true | 9.61 | 9.61 | yes |
| edge | p7_b_fees | 3.9603 | 3.9603 | yes |
| edge | p7_b_net | 13.8797 | 13.8797 | yes |
| edge | p7_b_margin | 0.3756 | 0.3756 | yes |
| edge | p7_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| edge | p7_b_flag | OK | OK | yes |
| edge | p8_postage | 7.69 | 7.69 | yes |
| edge | p8_labor | 1.2 | 1.2 | yes |
| edge | p8_true | 9.75 | 9.75 | yes |
| edge | p8_short | 0.2 | 0.2 | yes |
| edge | p8_flag | COVERED | Covered | intended: sentence case only, same status word |
| edge | p8_share | 0.7887 | 0.7887 | yes |
| edge | p8_d_name | Handmade Soap Set (3) | Handmade Soap Set (3) | yes |
| edge | p8_d_lb | 0.0312 | 0.0312 | yes |
| edge | p8_d_cubic | 105 | 105 | yes |
| edge | p8_d_over | no | No | intended: sentence case only, same status word |
| edge | p8_d_uspsdim | - | - | yes |
| edge | p8_d_uspsbill | 0.0312 | 0.0312 | yes |
| edge | p8_d_upsdim | 0.2625 | 0.2625 | yes |
| edge | p8_d_upsbill | 1 | 1 | yes |
| edge | p8_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| edge | p8_d_upsflag | ok | OK | intended: sentence case only, same status word |
| edge | p8_s_usps | 0.0312 | 0.0312 | yes |
| edge | p8_s_ups | 1 | 1 | yes |
| edge | p8_s_zone | 5 | 5 | yes |
| edge | p8_s_gacom | 7.69 | 7.69 | yes |
| edge | p8_s_garet | 8.6 | 8.6 | yes |
| edge | p8_s_pri | 12.97 | 12.97 | yes |
| edge | p8_s_upsgs | 19.8265 | 19.8265 | yes |
| edge | p8_s_cheap | 7.69 | 7.69 | yes |
| edge | p8_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| edge | p8_s_saved | 0.91 | 0.91 | yes |
| edge | p8_b_name | Handmade Soap Set (3) | Handmade Soap Set (3) | yes |
| edge | p8_b_sale | 26 | 26 | yes |
| edge | p8_b_ship | 9.95 | 9.95 | yes |
| edge | p8_b_true | 9.75 | 9.75 | yes |
| edge | p8_b_fees | 3.8653 | 3.8653 | yes |
| edge | p8_b_net | 16.3347 | 16.3347 | yes |
| edge | p8_b_margin | 0.4544 | 0.4544 | yes |
| edge | p8_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| edge | p8_b_flag | OK | OK | yes |
| edge | p9_postage | 8.51 | 8.51 | yes |
| edge | p9_labor | 1.5 | 1.5 | yes |
| edge | p9_true | 11.4 | 11.4 | yes |
| edge | p9_short | 1.55 | 1.55 | yes |
| edge | p9_flag | COVERED | Covered | intended: sentence case only, same status word |
| edge | p9_share | 0.7465 | 0.7465 | yes |
| edge | p9_d_name | Wooden Puzzle | Wooden Puzzle | yes |
| edge | p9_d_lb | 1.875 | 1.875 | yes |
| edge | p9_d_cubic | 160 | 160 | yes |
| edge | p9_d_over | no | No | intended: sentence case only, same status word |
| edge | p9_d_uspsdim | - | - | yes |
| edge | p9_d_uspsbill | 2 | 2 | yes |
| edge | p9_d_upsdim | 0.4 | 0.4 | yes |
| edge | p9_d_upsbill | 2 | 2 | yes |
| edge | p9_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| edge | p9_d_upsflag | ok | OK | intended: sentence case only, same status word |
| edge | p9_s_usps | 2 | 2 | yes |
| edge | p9_s_ups | 2 | 2 | yes |
| edge | p9_s_zone | 4 | 4 | yes |
| edge | p9_s_gacom | 8.51 | 8.51 | yes |
| edge | p9_s_garet | 13 | 13 | yes |
| edge | p9_s_pri | 10.79 | 10.79 | yes |
| edge | p9_s_upsgs | 21.6395 | 21.6395 | yes |
| edge | p9_s_cheap | 8.51 | 8.51 | yes |
| edge | p9_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| edge | p9_s_saved | 4.49 | 4.49 | yes |
| edge | p9_b_name | Wooden Puzzle | Wooden Puzzle | yes |
| edge | p9_b_sale | 34 | 34 | yes |
| edge | p9_b_ship | 12.95 | 12.95 | yes |
| edge | p9_b_true | 11.4 | 11.4 | yes |
| edge | p9_b_fees | 4.9103 | 4.9103 | yes |
| edge | p9_b_net | 21.6398 | 21.6398 | yes |
| edge | p9_b_margin | 0.4609 | 0.4609 | yes |
| edge | p9_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| edge | p9_b_flag | OK | OK | yes |
| edge | p10_postage | 12.84 | 12.84 | yes |
| edge | p10_labor | 2.1 | 2.1 | yes |
| edge | p10_true | 16.85 | 16.85 | yes |
| edge | p10_short | 1.1 | 1.1 | yes |
| edge | p10_flag | COVERED | Covered | intended: sentence case only, same status word |
| edge | p10_share | 0.762 | 0.762 | yes |
| edge | p10_d_name | Board Game | Board Game | yes |
| edge | p10_d_lb | 3.75 | 3.75 | yes |
| edge | p10_d_cubic | 432 | 432 | yes |
| edge | p10_d_over | no | No | intended: sentence case only, same status word |
| edge | p10_d_uspsdim | - | - | yes |
| edge | p10_d_uspsbill | 4 | 4 | yes |
| edge | p10_d_upsdim | 1.08 | 1.08 | yes |
| edge | p10_d_upsbill | 4 | 4 | yes |
| edge | p10_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| edge | p10_d_upsflag | ok | OK | intended: sentence case only, same status word |
| edge | p10_s_usps | 4 | 4 | yes |
| edge | p10_s_ups | 4 | 4 | yes |
| edge | p10_s_zone | 5 | 5 | yes |
| edge | p10_s_gacom | 12.84 | 12.84 | yes |
| edge | p10_s_garet | 16.4 | 16.4 | yes |
| edge | p10_s_pri | 19.88 | 19.88 | yes |
| edge | p10_s_upsgs | 24.9287 | 24.9287 | yes |
| edge | p10_s_cheap | 12.84 | 12.84 | yes |
| edge | p10_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| edge | p10_s_saved | 3.56 | 3.56 | yes |
| edge | p10_b_name | Board Game | Board Game | yes |
| edge | p10_b_sale | 48 | 48 | yes |
| edge | p10_b_ship | 17.95 | 17.95 | yes |
| edge | p10_b_true | 16.85 | 16.85 | yes |
| edge | p10_b_fees | 6.7153 | 6.7153 | yes |
| edge | p10_b_net | 26.3848 | 26.3848 | yes |
| edge | p10_b_margin | 0.4001 | 0.4001 | yes |
| edge | p10_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| edge | p10_b_flag | OK | OK | yes |
| edge | p11_postage | (blank) | (blank) | yes |
| edge | p11_labor | (blank) | (blank) | yes |
| edge | p11_true | (blank) | (blank) | yes |
| edge | p11_short | (blank) | (blank) | yes |
| edge | p11_flag | (blank) | (blank) | yes |
| edge | p11_share | (blank) | (blank) | yes |
| edge | p11_d_name | (blank) | (blank) | yes |
| edge | p11_d_lb | (blank) | (blank) | yes |
| edge | p11_d_cubic | (blank) | (blank) | yes |
| edge | p11_d_over | (blank) | (blank) | yes |
| edge | p11_d_uspsdim | (blank) | (blank) | yes |
| edge | p11_d_uspsbill | (blank) | (blank) | yes |
| edge | p11_d_upsdim | (blank) | (blank) | yes |
| edge | p11_d_upsbill | (blank) | (blank) | yes |
| edge | p11_d_uspsflag | (blank) | (blank) | yes |
| edge | p11_d_upsflag | (blank) | (blank) | yes |
| edge | p11_s_usps | (blank) | (blank) | yes |
| edge | p11_s_ups | (blank) | (blank) | yes |
| edge | p11_s_zone | (blank) | (blank) | yes |
| edge | p11_s_gacom | (blank) | (blank) | yes |
| edge | p11_s_garet | (blank) | (blank) | yes |
| edge | p11_s_pri | (blank) | (blank) | yes |
| edge | p11_s_upsgs | (blank) | (blank) | yes |
| edge | p11_s_cheap | (blank) | (blank) | yes |
| edge | p11_s_cheapname | (blank) | (blank) | yes |
| edge | p11_s_saved | (blank) | (blank) | yes |
| edge | p11_b_name | (blank) | (blank) | yes |
| edge | p11_b_sale | (blank) | (blank) | yes |
| edge | p11_b_ship | (blank) | (blank) | yes |
| edge | p11_b_true | (blank) | (blank) | yes |
| edge | p11_b_fees | (blank) | (blank) | yes |
| edge | p11_b_net | (blank) | (blank) | yes |
| edge | p11_b_margin | (blank) | (blank) | yes |
| edge | p11_b_shipflag | (blank) | (blank) | yes |
| edge | p11_b_flag | (blank) | (blank) | yes |
| edge | p12_postage | (blank) | (blank) | yes |
| edge | p12_labor | (blank) | (blank) | yes |
| edge | p12_true | (blank) | (blank) | yes |
| edge | p12_short | (blank) | (blank) | yes |
| edge | p12_flag | (blank) | (blank) | yes |
| edge | p12_share | (blank) | (blank) | yes |
| edge | p12_d_name | (blank) | (blank) | yes |
| edge | p12_d_lb | (blank) | (blank) | yes |
| edge | p12_d_cubic | (blank) | (blank) | yes |
| edge | p12_d_over | (blank) | (blank) | yes |
| edge | p12_d_uspsdim | (blank) | (blank) | yes |
| edge | p12_d_uspsbill | (blank) | (blank) | yes |
| edge | p12_d_upsdim | (blank) | (blank) | yes |
| edge | p12_d_upsbill | (blank) | (blank) | yes |
| edge | p12_d_uspsflag | (blank) | (blank) | yes |
| edge | p12_d_upsflag | (blank) | (blank) | yes |
| edge | p12_s_usps | (blank) | (blank) | yes |
| edge | p12_s_ups | (blank) | (blank) | yes |
| edge | p12_s_zone | (blank) | (blank) | yes |
| edge | p12_s_gacom | (blank) | (blank) | yes |
| edge | p12_s_garet | (blank) | (blank) | yes |
| edge | p12_s_pri | (blank) | (blank) | yes |
| edge | p12_s_upsgs | (blank) | (blank) | yes |
| edge | p12_s_cheap | (blank) | (blank) | yes |
| edge | p12_s_cheapname | (blank) | (blank) | yes |
| edge | p12_s_saved | (blank) | (blank) | yes |
| edge | p12_b_name | (blank) | (blank) | yes |
| edge | p12_b_sale | (blank) | (blank) | yes |
| edge | p12_b_ship | (blank) | (blank) | yes |
| edge | p12_b_true | (blank) | (blank) | yes |
| edge | p12_b_fees | (blank) | (blank) | yes |
| edge | p12_b_net | (blank) | (blank) | yes |
| edge | p12_b_margin | (blank) | (blank) | yes |
| edge | p12_b_shipflag | (blank) | (blank) | yes |
| edge | p12_b_flag | (blank) | (blank) | yes |
| edge | p30_postage | 37.814 | 37.814 | yes |
| edge | p30_labor | 0 | 0 | yes |
| edge | p30_true | 37.814 | 37.814 | yes |
| edge | p30_short | -37.814 | -37.814 | yes |
| edge | p30_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| edge | p30_share | 1 | 1 | yes |
| edge | p30_d_name | Last row | Last row | yes |
| edge | p30_d_lb | 10 | 10 | yes |
| edge | p30_d_cubic | 8,000 | 8,000 | yes |
| edge | p30_d_over | YES | Yes | intended: sentence case only, same status word |
| edge | p30_d_uspsdim | 57.554 | 57.554 | yes |
| edge | p30_d_uspsbill | 58 | 58 | yes |
| edge | p30_d_upsdim | 20 | 20 | yes |
| edge | p30_d_upsbill | 20 | 20 | yes |
| edge | p30_d_uspsflag | DIM WEIGHT BITES: +48 lb | Dim weight bites: +48 lb | intended: sentence case only, same status word |
| edge | p30_d_upsflag | DIM WEIGHT BITES: +10 lb | Dim weight bites: +10 lb | intended: sentence case only, same status word |
| edge | p30_s_usps | 58 | 58 | yes |
| edge | p30_s_ups | 20 | 20 | yes |
| edge | p30_s_zone | 3 | 3 | yes |
| edge | p30_s_gacom | over 20 lb | over 20 lb | yes |
| edge | p30_s_garet | over 20 lb | over 20 lb | yes |
| edge | p30_s_pri | over 20 lb | over 20 lb | yes |
| edge | p30_s_upsgs | 37.814 | 37.814 | yes |
| edge | p30_s_cheap | 37.814 | 37.814 | yes |
| edge | p30_s_cheapname | UPS Ground Saver | UPS Ground Saver | yes |
| edge | p30_s_saved | (blank) | (blank) | yes |
| edge | p30_b_name | Last row | Last row | yes |
| edge | p30_b_sale | 0 | 0 | yes |
| edge | p30_b_ship | 0 | 0 | yes |
| edge | p30_b_true | 37.814 | 37.814 | yes |
| edge | p30_b_fees | 0.45 | 0.45 | yes |
| edge | p30_b_net | -38.264 | -38.264 | yes |
| edge | p30_b_margin | (blank) | (blank) | yes |
| edge | p30_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| edge | p30_b_flag | LOSING MONEY | Losing money | intended: sentence case only, same status word |
| edge | avg_true | 15.2304 | 15.2304 | yes |
| edge | avg_short | -7.3654 | -7.3654 | yes |
| edge | avg_share | 0.8102 | 0.8102 | yes |
| edge | sc_cheap_total | 126.304 | 126.304 | yes |
| edge | sc_saved_total | 28.16 | 28.16 | yes |
| edge | db_losing | 2 | 2 | yes |
| edge | db_under | 7 | 7 | yes |
| edge | db_avgtrue | 15.2304 | 15.2304 | yes |
| edge | db_avgshort | -7.3654 | -7.3654 | yes |
| edge | db_shipcost | 152.304 | 152.304 | yes |
| edge | db_collected | 93.6 | 93.6 | yes |
| edge | db_netship | -58.704 | -58.704 | yes |
| edge | db_share | 0.8102 | 0.8102 | yes |
| edge | db_tot_true | 152.304 | 152.304 | yes |
| edge | db_tot_fees | 49.182 | 49.182 | yes |
| edge | db_tot_net | 98.9443 | 98.9443 | yes |
| edge | fs_tc | 15.2304 | 15.2304 | yes |
| edge | fs_tcused | 15.2304 | 15.2304 | yes |
| edge | fs_profit_order | 36.8696 | 36.8696 | yes |
| edge | fs_cost | 6.5 | 6.5 | yes |
| edge | fs_breakeven | 54.8421 | 54.8421 | yes |
| edge | fs_recommendation | Best of the three: free shipping over $75, about $1,040 more profit per 100 orders than today. An estimate built on your assumptions above, not a promise. | Best of the three: free shipping over $75, about $1,040 more profit per 100 orders than today. An estimate built on your assumptions above, not a promise. | yes |
| edge | fs_avgo_today | 48 | 48 | yes |
| edge | fs_avgo_s1 | 48 | 48 | yes |
| edge | fs_avgo_s2 | 48 | 48 | yes |
| edge | fs_avgo_s3 | 48 | 48 | yes |
| edge | fs_orders_today | 100 | 100 | yes |
| edge | fs_orders_s1 | 115 | 115 | yes |
| edge | fs_orders_s2 | 115 | 115 | yes |
| edge | fs_orders_s3 | 115 | 115 | yes |
| edge | fs_qual_today | 0 | 0 | yes |
| edge | fs_qual_s1 | 115 | 115 | yes |
| edge | fs_qual_s2 | 34.5 | 34.5 | yes |
| edge | fs_qual_s3 | 13.8 | 13.8 | yes |
| edge | fs_other_today | 100 | 100 | yes |
| edge | fs_other_s1 | 0 | 0 | yes |
| edge | fs_other_s2 | 80.5 | 80.5 | yes |
| edge | fs_other_s3 | 101.2 | 101.2 | yes |
| edge | fs_rev_today | 4,800 | 4,800 | yes |
| edge | fs_rev_s1 | 0 | 0 | yes |
| edge | fs_rev_s2 | 6,072 | 6,072 | yes |
| edge | fs_rev_s3 | 6,127.2 | 6,127.2 | yes |
| edge | fs_coll_today | 650 | 650 | yes |
| edge | fs_coll_s1 | 0 | 0 | yes |
| edge | fs_coll_s2 | 523.25 | 523.25 | yes |
| edge | fs_coll_s3 | 657.8 | 657.8 | yes |
| edge | fs_parc_today | 1,523.04 | 1,523.04 | yes |
| edge | fs_parc_s1 | 1,751.496 | 1,751.496 | yes |
| edge | fs_parc_s2 | 1,751.496 | 1,751.496 | yes |
| edge | fs_parc_s3 | 1,751.496 | 1,751.496 | yes |
| edge | fs_profit_today | 3,686.96 | 3,686.96 | yes |
| edge | fs_profit_s1 | -1,751.496 | -1,751.496 | yes |
| edge | fs_profit_s2 | 4,540.154 | 4,540.154 | yes |
| edge | fs_profit_s3 | 4,727.144 | 4,727.144 | yes |
| edge | fs_per_today | 36.8696 | 36.8696 | yes |
| edge | fs_per_s1 | -15.2304 | -15.2304 | yes |
| edge | fs_per_s2 | 39.4796 | 39.4796 | yes |
| edge | fs_per_s3 | 41.1056 | 41.1056 | yes |
| edge | fs_chg_today | 0 | 0 | yes |
| edge | fs_chg_s1 | -5,438.456 | -5,438.456 | yes |
| edge | fs_chg_s2 | 853.194 | 853.194 | yes |
| edge | fs_chg_s3 | 1,040.184 | 1,040.184 | yes |
| edge | fs_verdict_today | baseline | Today | intended: baseline column now reads Today |
| edge | fs_verdict_s1 | WORSE THAN TODAY | Worse than today | intended: sentence case only, same status word |
| edge | fs_verdict_s2 | BEATS TODAY | Beats today | intended: sentence case only, same status word |
| edge | fs_verdict_s3 | BEATS TODAY | Beats today | intended: sentence case only, same status word |
| quote picked but blank | p1_postage | 9.95 | 9.95 | yes |
| quote picked but blank | p1_labor | 1.8 | 1.8 | yes |
| quote picked but blank | p1_true | 13.19 | 13.19 | yes |
| quote picked but blank | p1_short | -8.24 | -8.24 | yes |
| quote picked but blank | p1_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| quote picked but blank | p1_share | 0.7544 | 0.7544 | yes |
| quote picked but blank | p1_d_name | Ceramic Mug 12 oz | Ceramic Mug 12 oz | yes |
| quote picked but blank | p1_d_lb | 1.125 | 1.125 | yes |
| quote picked but blank | p1_d_cubic | 288 | 288 | yes |
| quote picked but blank | p1_d_over | no | No | intended: sentence case only, same status word |
| quote picked but blank | p1_d_uspsdim | - | - | yes |
| quote picked but blank | p1_d_uspsbill | 2 | 2 | yes |
| quote picked but blank | p1_d_upsdim | 2.0719 | 2.0719 | yes |
| quote picked but blank | p1_d_upsbill | 3 | 3 | yes |
| quote picked but blank | p1_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| quote picked but blank | p1_d_upsflag | DIM WEIGHT BITES: +1 lb | Dim weight bites: +1 lb | intended: sentence case only, same status word |
| quote picked but blank | p1_s_usps | 2 | 2 | yes |
| quote picked but blank | p1_s_ups | 3 | 3 | yes |
| quote picked but blank | p1_s_zone | 5 | 5 | yes |
| quote picked but blank | p1_s_gacom | 9.95 | 9.95 | yes |
| quote picked but blank | p1_s_garet | 14.1 | 14.1 | yes |
| quote picked but blank | p1_s_pri | 13.17 | 13.17 | yes |
| quote picked but blank | p1_s_upsgs | 23.6596 | 23.6596 | yes |
| quote picked but blank | p1_s_cheap | 9.95 | 9.95 | yes |
| quote picked but blank | p1_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| quote picked but blank | p1_s_saved | 4.15 | 4.15 | yes |
| quote picked but blank | p1_b_name | Ceramic Mug 12 oz | Ceramic Mug 12 oz | yes |
| quote picked but blank | p1_b_sale | 19 | 19 | yes |
| quote picked but blank | p1_b_ship | 4.95 | 4.95 | yes |
| quote picked but blank | p1_b_true | 13.19 | 13.19 | yes |
| quote picked but blank | p1_b_fees | 2.7252 | 2.7252 | yes |
| quote picked but blank | p1_b_net | -0.4652 | -0.4652 | yes |
| quote picked but blank | p1_b_margin | -0.0194 | -0.0194 | yes |
| quote picked but blank | p1_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| quote picked but blank | p1_b_flag | LOSING MONEY | Losing money | intended: sentence case only, same status word |
| quote picked but blank | p2_postage | 0 | (blank) | yes |
| quote picked but blank | p2_labor | 0.9 | 0.9 | yes |
| quote picked but blank | p2_true | (blank) | (blank) | yes |
| quote picked but blank | p2_short | (blank) | (blank) | yes |
| quote picked but blank | p2_flag | ENTER POSTAGE | Enter postage | intended: sentence case only, same status word |
| quote picked but blank | p2_share | (blank) | (blank) | yes |
| quote picked but blank | p2_d_name | Graphic T-Shirt | Graphic T-Shirt | yes |
| quote picked but blank | p2_d_lb | 0.4375 | 0.4375 | yes |
| quote picked but blank | p2_d_cubic | 130 | 130 | yes |
| quote picked but blank | p2_d_over | no | No | intended: sentence case only, same status word |
| quote picked but blank | p2_d_uspsdim | - | - | yes |
| quote picked but blank | p2_d_uspsbill | 0.4375 | 0.4375 | yes |
| quote picked but blank | p2_d_upsdim | 0.9353 | 0.9353 | yes |
| quote picked but blank | p2_d_upsbill | 1 | 1 | yes |
| quote picked but blank | p2_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| quote picked but blank | p2_d_upsflag | ok | OK | intended: sentence case only, same status word |
| quote picked but blank | p2_s_usps | 0.4375 | 0.4375 | yes |
| quote picked but blank | p2_s_ups | 1 | 1 | yes |
| quote picked but blank | p2_s_zone | 3 | 3 | yes |
| quote picked but blank | p2_s_gacom | 7.3 | 7.3 | yes |
| quote picked but blank | p2_s_garet | 8.15 | 8.15 | yes |
| quote picked but blank | p2_s_pri | 9.71 | 9.71 | yes |
| quote picked but blank | p2_s_upsgs | 17.4954 | 17.4954 | yes |
| quote picked but blank | p2_s_cheap | 7.3 | 7.3 | yes |
| quote picked but blank | p2_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| quote picked but blank | p2_s_saved | 0.85 | 0.85 | yes |
| quote picked but blank | p2_b_name | Graphic T-Shirt | Graphic T-Shirt | yes |
| quote picked but blank | p2_b_sale | 28 | 28 | yes |
| quote picked but blank | p2_b_ship | 4.95 | 4.95 | yes |
| quote picked but blank | p2_b_true | (blank) | (blank) | yes |
| quote picked but blank | p2_b_fees | 3.5803 | 3.5803 | yes |
| quote picked but blank | p2_b_net | (blank) | (blank) | yes |
| quote picked but blank | p2_b_margin | (blank) | (blank) | yes |
| quote picked but blank | p2_b_shipflag | ENTER POSTAGE | Enter postage | intended: sentence case only, same status word |
| quote picked but blank | p2_b_flag | (blank) | (blank) | yes |
| quote picked but blank | p3_postage | 0 | (blank) | yes |
| quote picked but blank | p3_labor | 3.6 | 3.6 | yes |
| quote picked but blank | p3_true | (blank) | (blank) | yes |
| quote picked but blank | p3_short | (blank) | (blank) | yes |
| quote picked but blank | p3_flag | ENTER POSTAGE | Enter postage | intended: sentence case only, same status word |
| quote picked but blank | p3_share | (blank) | (blank) | yes |
| quote picked but blank | p3_d_name | Framed Print 11x14 | Framed Print 11x14 | yes |
| quote picked but blank | p3_d_lb | 3.25 | 3.25 | yes |
| quote picked but blank | p3_d_cubic | 756 | 756 | yes |
| quote picked but blank | p3_d_over | no | No | intended: sentence case only, same status word |
| quote picked but blank | p3_d_uspsdim | - | - | yes |
| quote picked but blank | p3_d_uspsbill | 4 | 4 | yes |
| quote picked but blank | p3_d_upsdim | 5.4388 | 5.4388 | yes |
| quote picked but blank | p3_d_upsbill | 6 | 6 | yes |
| quote picked but blank | p3_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| quote picked but blank | p3_d_upsflag | DIM WEIGHT BITES: +2 lb | Dim weight bites: +2 lb | intended: sentence case only, same status word |
| quote picked but blank | p3_s_usps | 4 | 4 | yes |
| quote picked but blank | p3_s_ups | 6 | 6 | yes |
| quote picked but blank | p3_s_zone | 6 | 6 | yes |
| quote picked but blank | p3_s_gacom | 15.16 | 15.16 | yes |
| quote picked but blank | p3_s_garet | 18.3 | 18.3 | yes |
| quote picked but blank | p3_s_pri | 24.51 | 24.51 | yes |
| quote picked but blank | p3_s_upsgs | 27.0526 | 27.0526 | yes |
| quote picked but blank | p3_s_cheap | 15.16 | 15.16 | yes |
| quote picked but blank | p3_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| quote picked but blank | p3_s_saved | 3.14 | 3.14 | yes |
| quote picked but blank | p3_b_name | Framed Print 11x14 | Framed Print 11x14 | yes |
| quote picked but blank | p3_b_sale | 65 | 65 | yes |
| quote picked but blank | p3_b_ship | 12 | 12 | yes |
| quote picked but blank | p3_b_true | (blank) | (blank) | yes |
| quote picked but blank | p3_b_fees | 7.765 | 7.765 | yes |
| quote picked but blank | p3_b_net | (blank) | (blank) | yes |
| quote picked but blank | p3_b_margin | (blank) | (blank) | yes |
| quote picked but blank | p3_b_shipflag | ENTER POSTAGE | Enter postage | intended: sentence case only, same status word |
| quote picked but blank | p3_b_flag | (blank) | (blank) | yes |
| quote picked but blank | p4_postage | n/a | n/a | yes |
| quote picked but blank | p4_labor | 0.9 | 0.9 | yes |
| quote picked but blank | p4_true | (blank) | (blank) | yes |
| quote picked but blank | p4_short | (blank) | (blank) | yes |
| quote picked but blank | p4_flag | ENTER POSTAGE | Enter postage | intended: sentence case only, same status word |
| quote picked but blank | p4_share | (blank) | (blank) | yes |
| quote picked but blank | p4_d_name | Sterling Silver Earrings | Sterling Silver Earrings | yes |
| quote picked but blank | p4_d_lb | 0.125 | 0.125 | yes |
| quote picked but blank | p4_d_cubic | 54 | 54 | yes |
| quote picked but blank | p4_d_over | no | No | intended: sentence case only, same status word |
| quote picked but blank | p4_d_uspsdim | - | - | yes |
| quote picked but blank | p4_d_uspsbill | 0.125 | 0.125 | yes |
| quote picked but blank | p4_d_upsdim | 0.3885 | 0.3885 | yes |
| quote picked but blank | p4_d_upsbill | 1 | 1 | yes |
| quote picked but blank | p4_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| quote picked but blank | p4_d_upsflag | ok | OK | intended: sentence case only, same status word |
| quote picked but blank | p4_s_usps | 0.125 | 0.125 | yes |
| quote picked but blank | p4_s_ups | 1 | 1 | yes |
| quote picked but blank | p4_s_zone | 9 | 9 | yes |
| quote picked but blank | p4_s_gacom | 8.4 | 8.4 | yes |
| quote picked but blank | p4_s_garet | 9.45 | 9.45 | yes |
| quote picked but blank | p4_s_pri | 32.48 | 32.48 | yes |
| quote picked but blank | p4_s_upsgs | n/a | n/a | yes |
| quote picked but blank | p4_s_cheap | 8.4 | 8.4 | yes |
| quote picked but blank | p4_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| quote picked but blank | p4_s_saved | 1.05 | 1.05 | yes |
| quote picked but blank | p4_b_name | Sterling Silver Earrings | Sterling Silver Earrings | yes |
| quote picked but blank | p4_b_sale | 42 | 42 | yes |
| quote picked but blank | p4_b_ship | 0 | 0 | yes |
| quote picked but blank | p4_b_true | (blank) | (blank) | yes |
| quote picked but blank | p4_b_fees | 4.44 | 4.44 | yes |
| quote picked but blank | p4_b_net | (blank) | (blank) | yes |
| quote picked but blank | p4_b_margin | (blank) | (blank) | yes |
| quote picked but blank | p4_b_shipflag | ENTER POSTAGE | Enter postage | intended: sentence case only, same status word |
| quote picked but blank | p4_b_flag | (blank) | (blank) | yes |
| quote picked but blank | p5_postage | 8.51 | 8.51 | yes |
| quote picked but blank | p5_labor | 1.5 | 1.5 | yes |
| quote picked but blank | p5_true | 11.25 | 11.25 | yes |
| quote picked but blank | p5_short | -2.3 | -2.3 | yes |
| quote picked but blank | p5_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| quote picked but blank | p5_share | 0.7564 | 0.7564 | yes |
| quote picked but blank | p5_d_name | Soy Candle 8 oz | Soy Candle 8 oz | yes |
| quote picked but blank | p5_d_lb | 1.25 | 1.25 | yes |
| quote picked but blank | p5_d_cubic | 216 | 216 | yes |
| quote picked but blank | p5_d_over | no | No | intended: sentence case only, same status word |
| quote picked but blank | p5_d_uspsdim | - | - | yes |
| quote picked but blank | p5_d_uspsbill | 2 | 2 | yes |
| quote picked but blank | p5_d_upsdim | 1.554 | 1.554 | yes |
| quote picked but blank | p5_d_upsbill | 2 | 2 | yes |
| quote picked but blank | p5_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| quote picked but blank | p5_d_upsflag | ok | OK | intended: sentence case only, same status word |
| quote picked but blank | p5_s_usps | 2 | 2 | yes |
| quote picked but blank | p5_s_ups | 2 | 2 | yes |
| quote picked but blank | p5_s_zone | 4 | 4 | yes |
| quote picked but blank | p5_s_gacom | 8.51 | 8.51 | yes |
| quote picked but blank | p5_s_garet | 13 | 13 | yes |
| quote picked but blank | p5_s_pri | 10.79 | 10.79 | yes |
| quote picked but blank | p5_s_upsgs | 21.6395 | 21.6395 | yes |
| quote picked but blank | p5_s_cheap | 8.51 | 8.51 | yes |
| quote picked but blank | p5_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| quote picked but blank | p5_s_saved | 4.49 | 4.49 | yes |
| quote picked but blank | p5_b_name | Soy Candle 8 oz | Soy Candle 8 oz | yes |
| quote picked but blank | p5_b_sale | 22 | 22 | yes |
| quote picked but blank | p5_b_ship | 8.95 | 8.95 | yes |
| quote picked but blank | p5_b_true | 11.25 | 11.25 | yes |
| quote picked but blank | p5_b_fees | 3.3902 | 3.3902 | yes |
| quote picked but blank | p5_b_net | 10.7097 | 10.7097 | yes |
| quote picked but blank | p5_b_margin | 0.346 | 0.346 | yes |
| quote picked but blank | p5_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| quote picked but blank | p5_b_flag | OK | OK | yes |
| quote picked but blank | p6_postage | 21.15 | 21.15 | yes |
| quote picked but blank | p6_labor | 3 | 3 | yes |
| quote picked but blank | p6_true | 28.21 | 28.21 | yes |
| quote picked but blank | p6_short | -13.26 | -13.26 | yes |
| quote picked but blank | p6_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| quote picked but blank | p6_share | 0.7497 | 0.7497 | yes |
| quote picked but blank | p6_d_name | Grapevine Wreath 16 in | Grapevine Wreath 16 in | yes |
| quote picked but blank | p6_d_lb | 2.5 | 2.5 | yes |
| quote picked but blank | p6_d_cubic | 2,048 | 2,048 | yes |
| quote picked but blank | p6_d_over | YES | Yes | intended: sentence case only, same status word |
| quote picked but blank | p6_d_uspsdim | 14.7338 | 14.7338 | yes |
| quote picked but blank | p6_d_uspsbill | 15 | 15 | yes |
| quote picked but blank | p6_d_upsdim | 14.7338 | 14.7338 | yes |
| quote picked but blank | p6_d_upsbill | 15 | 15 | yes |
| quote picked but blank | p6_d_uspsflag | DIM WEIGHT BITES: +12 lb | Dim weight bites: +12 lb | intended: sentence case only, same status word |
| quote picked but blank | p6_d_upsflag | DIM WEIGHT BITES: +12 lb | Dim weight bites: +12 lb | intended: sentence case only, same status word |
| quote picked but blank | p6_s_usps | 15 | 15 | yes |
| quote picked but blank | p6_s_ups | 15 | 15 | yes |
| quote picked but blank | p6_s_zone | 5 | 5 | yes |
| quote picked but blank | p6_s_gacom | 21.15 | 21.15 | yes |
| quote picked but blank | p6_s_garet | 28.95 | 28.95 | yes |
| quote picked but blank | p6_s_pri | 35.25 | 35.25 | yes |
| quote picked but blank | p6_s_upsgs | 39.9637 | 39.9637 | yes |
| quote picked but blank | p6_s_cheap | 21.15 | 21.15 | yes |
| quote picked but blank | p6_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| quote picked but blank | p6_s_saved | 7.8 | 7.8 | yes |
| quote picked but blank | p6_b_name | Grapevine Wreath 16 in | Grapevine Wreath 16 in | yes |
| quote picked but blank | p6_b_sale | 58 | 58 | yes |
| quote picked but blank | p6_b_ship | 14.95 | 14.95 | yes |
| quote picked but blank | p6_b_true | 28.21 | 28.21 | yes |
| quote picked but blank | p6_b_fees | 7.3803 | 7.3803 | yes |
| quote picked but blank | p6_b_net | 19.3598 | 19.3598 | yes |
| quote picked but blank | p6_b_margin | 0.2654 | 0.2654 | yes |
| quote picked but blank | p6_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| quote picked but blank | p6_b_flag | OK | OK | yes |
| quote picked but blank | p7_postage | 6.94 | 6.94 | yes |
| quote picked but blank | p7_labor | 0.9 | 0.9 | yes |
| quote picked but blank | p7_true | 8.15 | 8.15 | yes |
| quote picked but blank | p7_short | -1.2 | -1.2 | yes |
| quote picked but blank | p7_flag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| quote picked but blank | p7_share | 0.8515 | 0.8515 | yes |
| quote picked but blank | p7_d_name | Canvas Tote Bag | Canvas Tote Bag | yes |
| quote picked but blank | p7_d_lb | 0.5625 | 0.5625 | yes |
| quote picked but blank | p7_d_cubic | 180 | 180 | yes |
| quote picked but blank | p7_d_over | no | No | intended: sentence case only, same status word |
| quote picked but blank | p7_d_uspsdim | - | - | yes |
| quote picked but blank | p7_d_uspsbill | 0.5625 | 0.5625 | yes |
| quote picked but blank | p7_d_upsdim | 1.295 | 1.295 | yes |
| quote picked but blank | p7_d_upsbill | 2 | 2 | yes |
| quote picked but blank | p7_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| quote picked but blank | p7_d_upsflag | DIM WEIGHT BITES: +1 lb | Dim weight bites: +1 lb | intended: sentence case only, same status word |
| quote picked but blank | p7_s_usps | 0.5625 | 0.5625 | yes |
| quote picked but blank | p7_s_ups | 2 | 2 | yes |
| quote picked but blank | p7_s_zone | 2 | 2 | yes |
| quote picked but blank | p7_s_gacom | 6.94 | 6.94 | yes |
| quote picked but blank | p7_s_garet | 9.95 | 9.95 | yes |
| quote picked but blank | p7_s_pri | 9.32 | 9.32 | yes |
| quote picked but blank | p7_s_upsgs | 18.117 | 18.117 | yes |
| quote picked but blank | p7_s_cheap | 6.94 | 6.94 | yes |
| quote picked but blank | p7_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| quote picked but blank | p7_s_saved | 3.01 | 3.01 | yes |
| quote picked but blank | p7_b_name | Canvas Tote Bag | Canvas Tote Bag | yes |
| quote picked but blank | p7_b_sale | 30 | 30 | yes |
| quote picked but blank | p7_b_ship | 6.95 | 6.95 | yes |
| quote picked but blank | p7_b_true | 8.15 | 8.15 | yes |
| quote picked but blank | p7_b_fees | 3.9603 | 3.9603 | yes |
| quote picked but blank | p7_b_net | 15.3398 | 15.3398 | yes |
| quote picked but blank | p7_b_margin | 0.4151 | 0.4151 | yes |
| quote picked but blank | p7_b_shipflag | UNDER-RECOVERED | Under-recovered | intended: sentence case only, same status word |
| quote picked but blank | p7_b_flag | OK | OK | yes |
| quote picked but blank | p8_postage | 7.69 | 7.69 | yes |
| quote picked but blank | p8_labor | 1.2 | 1.2 | yes |
| quote picked but blank | p8_true | 9.75 | 9.75 | yes |
| quote picked but blank | p8_short | 0.2 | 0.2 | yes |
| quote picked but blank | p8_flag | COVERED | Covered | intended: sentence case only, same status word |
| quote picked but blank | p8_share | 0.7887 | 0.7887 | yes |
| quote picked but blank | p8_d_name | Handmade Soap Set (3) | Handmade Soap Set (3) | yes |
| quote picked but blank | p8_d_lb | 0.875 | 0.875 | yes |
| quote picked but blank | p8_d_cubic | 105 | 105 | yes |
| quote picked but blank | p8_d_over | no | No | intended: sentence case only, same status word |
| quote picked but blank | p8_d_uspsdim | - | - | yes |
| quote picked but blank | p8_d_uspsbill | 0.875 | 0.875 | yes |
| quote picked but blank | p8_d_upsdim | 0.7554 | 0.7554 | yes |
| quote picked but blank | p8_d_upsbill | 1 | 1 | yes |
| quote picked but blank | p8_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| quote picked but blank | p8_d_upsflag | ok | OK | intended: sentence case only, same status word |
| quote picked but blank | p8_s_usps | 0.875 | 0.875 | yes |
| quote picked but blank | p8_s_ups | 1 | 1 | yes |
| quote picked but blank | p8_s_zone | 5 | 5 | yes |
| quote picked but blank | p8_s_gacom | 7.69 | 7.69 | yes |
| quote picked but blank | p8_s_garet | 10.95 | 10.95 | yes |
| quote picked but blank | p8_s_pri | 12.97 | 12.97 | yes |
| quote picked but blank | p8_s_upsgs | 19.8265 | 19.8265 | yes |
| quote picked but blank | p8_s_cheap | 7.69 | 7.69 | yes |
| quote picked but blank | p8_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| quote picked but blank | p8_s_saved | 3.26 | 3.26 | yes |
| quote picked but blank | p8_b_name | Handmade Soap Set (3) | Handmade Soap Set (3) | yes |
| quote picked but blank | p8_b_sale | 26 | 26 | yes |
| quote picked but blank | p8_b_ship | 9.95 | 9.95 | yes |
| quote picked but blank | p8_b_true | 9.75 | 9.75 | yes |
| quote picked but blank | p8_b_fees | 3.8653 | 3.8653 | yes |
| quote picked but blank | p8_b_net | 16.3347 | 16.3347 | yes |
| quote picked but blank | p8_b_margin | 0.4544 | 0.4544 | yes |
| quote picked but blank | p8_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| quote picked but blank | p8_b_flag | OK | OK | yes |
| quote picked but blank | p9_postage | 8.51 | 8.51 | yes |
| quote picked but blank | p9_labor | 1.5 | 1.5 | yes |
| quote picked but blank | p9_true | 11.4 | 11.4 | yes |
| quote picked but blank | p9_short | 1.55 | 1.55 | yes |
| quote picked but blank | p9_flag | COVERED | Covered | intended: sentence case only, same status word |
| quote picked but blank | p9_share | 0.7465 | 0.7465 | yes |
| quote picked but blank | p9_d_name | Wooden Puzzle | Wooden Puzzle | yes |
| quote picked but blank | p9_d_lb | 1.875 | 1.875 | yes |
| quote picked but blank | p9_d_cubic | 160 | 160 | yes |
| quote picked but blank | p9_d_over | no | No | intended: sentence case only, same status word |
| quote picked but blank | p9_d_uspsdim | - | - | yes |
| quote picked but blank | p9_d_uspsbill | 2 | 2 | yes |
| quote picked but blank | p9_d_upsdim | 1.1511 | 1.1511 | yes |
| quote picked but blank | p9_d_upsbill | 2 | 2 | yes |
| quote picked but blank | p9_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| quote picked but blank | p9_d_upsflag | ok | OK | intended: sentence case only, same status word |
| quote picked but blank | p9_s_usps | 2 | 2 | yes |
| quote picked but blank | p9_s_ups | 2 | 2 | yes |
| quote picked but blank | p9_s_zone | 4 | 4 | yes |
| quote picked but blank | p9_s_gacom | 8.51 | 8.51 | yes |
| quote picked but blank | p9_s_garet | 13 | 13 | yes |
| quote picked but blank | p9_s_pri | 10.79 | 10.79 | yes |
| quote picked but blank | p9_s_upsgs | 21.6395 | 21.6395 | yes |
| quote picked but blank | p9_s_cheap | 8.51 | 8.51 | yes |
| quote picked but blank | p9_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| quote picked but blank | p9_s_saved | 4.49 | 4.49 | yes |
| quote picked but blank | p9_b_name | Wooden Puzzle | Wooden Puzzle | yes |
| quote picked but blank | p9_b_sale | 34 | 34 | yes |
| quote picked but blank | p9_b_ship | 12.95 | 12.95 | yes |
| quote picked but blank | p9_b_true | 11.4 | 11.4 | yes |
| quote picked but blank | p9_b_fees | 4.9103 | 4.9103 | yes |
| quote picked but blank | p9_b_net | 21.6398 | 21.6398 | yes |
| quote picked but blank | p9_b_margin | 0.4609 | 0.4609 | yes |
| quote picked but blank | p9_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| quote picked but blank | p9_b_flag | OK | OK | yes |
| quote picked but blank | p10_postage | 12.84 | 12.84 | yes |
| quote picked but blank | p10_labor | 2.1 | 2.1 | yes |
| quote picked but blank | p10_true | 16.85 | 16.85 | yes |
| quote picked but blank | p10_short | 1.1 | 1.1 | yes |
| quote picked but blank | p10_flag | COVERED | Covered | intended: sentence case only, same status word |
| quote picked but blank | p10_share | 0.762 | 0.762 | yes |
| quote picked but blank | p10_d_name | Board Game | Board Game | yes |
| quote picked but blank | p10_d_lb | 3.75 | 3.75 | yes |
| quote picked but blank | p10_d_cubic | 432 | 432 | yes |
| quote picked but blank | p10_d_over | no | No | intended: sentence case only, same status word |
| quote picked but blank | p10_d_uspsdim | - | - | yes |
| quote picked but blank | p10_d_uspsbill | 4 | 4 | yes |
| quote picked but blank | p10_d_upsdim | 3.1079 | 3.1079 | yes |
| quote picked but blank | p10_d_upsbill | 4 | 4 | yes |
| quote picked but blank | p10_d_uspsflag | ok | OK | intended: sentence case only, same status word |
| quote picked but blank | p10_d_upsflag | ok | OK | intended: sentence case only, same status word |
| quote picked but blank | p10_s_usps | 4 | 4 | yes |
| quote picked but blank | p10_s_ups | 4 | 4 | yes |
| quote picked but blank | p10_s_zone | 5 | 5 | yes |
| quote picked but blank | p10_s_gacom | 12.84 | 12.84 | yes |
| quote picked but blank | p10_s_garet | 16.4 | 16.4 | yes |
| quote picked but blank | p10_s_pri | 19.88 | 19.88 | yes |
| quote picked but blank | p10_s_upsgs | 24.9287 | 24.9287 | yes |
| quote picked but blank | p10_s_cheap | 12.84 | 12.84 | yes |
| quote picked but blank | p10_s_cheapname | USPS GA Commercial | USPS GA Commercial | yes |
| quote picked but blank | p10_s_saved | 3.56 | 3.56 | yes |
| quote picked but blank | p10_b_name | Board Game | Board Game | yes |
| quote picked but blank | p10_b_sale | 48 | 48 | yes |
| quote picked but blank | p10_b_ship | 17.95 | 17.95 | yes |
| quote picked but blank | p10_b_true | 16.85 | 16.85 | yes |
| quote picked but blank | p10_b_fees | 6.7153 | 6.7153 | yes |
| quote picked but blank | p10_b_net | 26.3848 | 26.3848 | yes |
| quote picked but blank | p10_b_margin | 0.4001 | 0.4001 | yes |
| quote picked but blank | p10_b_shipflag | COVERED | Covered | intended: sentence case only, same status word |
| quote picked but blank | p10_b_flag | OK | OK | yes |
| quote picked but blank | p11_postage | (blank) | (blank) | yes |
| quote picked but blank | p11_labor | (blank) | (blank) | yes |
| quote picked but blank | p11_true | (blank) | (blank) | yes |
| quote picked but blank | p11_short | (blank) | (blank) | yes |
| quote picked but blank | p11_flag | (blank) | (blank) | yes |
| quote picked but blank | p11_share | (blank) | (blank) | yes |
| quote picked but blank | p11_d_name | (blank) | (blank) | yes |
| quote picked but blank | p11_d_lb | (blank) | (blank) | yes |
| quote picked but blank | p11_d_cubic | (blank) | (blank) | yes |
| quote picked but blank | p11_d_over | (blank) | (blank) | yes |
| quote picked but blank | p11_d_uspsdim | (blank) | (blank) | yes |
| quote picked but blank | p11_d_uspsbill | (blank) | (blank) | yes |
| quote picked but blank | p11_d_upsdim | (blank) | (blank) | yes |
| quote picked but blank | p11_d_upsbill | (blank) | (blank) | yes |
| quote picked but blank | p11_d_uspsflag | (blank) | (blank) | yes |
| quote picked but blank | p11_d_upsflag | (blank) | (blank) | yes |
| quote picked but blank | p11_s_usps | (blank) | (blank) | yes |
| quote picked but blank | p11_s_ups | (blank) | (blank) | yes |
| quote picked but blank | p11_s_zone | (blank) | (blank) | yes |
| quote picked but blank | p11_s_gacom | (blank) | (blank) | yes |
| quote picked but blank | p11_s_garet | (blank) | (blank) | yes |
| quote picked but blank | p11_s_pri | (blank) | (blank) | yes |
| quote picked but blank | p11_s_upsgs | (blank) | (blank) | yes |
| quote picked but blank | p11_s_cheap | (blank) | (blank) | yes |
| quote picked but blank | p11_s_cheapname | (blank) | (blank) | yes |
| quote picked but blank | p11_s_saved | (blank) | (blank) | yes |
| quote picked but blank | p11_b_name | (blank) | (blank) | yes |
| quote picked but blank | p11_b_sale | (blank) | (blank) | yes |
| quote picked but blank | p11_b_ship | (blank) | (blank) | yes |
| quote picked but blank | p11_b_true | (blank) | (blank) | yes |
| quote picked but blank | p11_b_fees | (blank) | (blank) | yes |
| quote picked but blank | p11_b_net | (blank) | (blank) | yes |
| quote picked but blank | p11_b_margin | (blank) | (blank) | yes |
| quote picked but blank | p11_b_shipflag | (blank) | (blank) | yes |
| quote picked but blank | p11_b_flag | (blank) | (blank) | yes |
| quote picked but blank | p12_postage | (blank) | (blank) | yes |
| quote picked but blank | p12_labor | (blank) | (blank) | yes |
| quote picked but blank | p12_true | (blank) | (blank) | yes |
| quote picked but blank | p12_short | (blank) | (blank) | yes |
| quote picked but blank | p12_flag | (blank) | (blank) | yes |
| quote picked but blank | p12_share | (blank) | (blank) | yes |
| quote picked but blank | p12_d_name | (blank) | (blank) | yes |
| quote picked but blank | p12_d_lb | (blank) | (blank) | yes |
| quote picked but blank | p12_d_cubic | (blank) | (blank) | yes |
| quote picked but blank | p12_d_over | (blank) | (blank) | yes |
| quote picked but blank | p12_d_uspsdim | (blank) | (blank) | yes |
| quote picked but blank | p12_d_uspsbill | (blank) | (blank) | yes |
| quote picked but blank | p12_d_upsdim | (blank) | (blank) | yes |
| quote picked but blank | p12_d_upsbill | (blank) | (blank) | yes |
| quote picked but blank | p12_d_uspsflag | (blank) | (blank) | yes |
| quote picked but blank | p12_d_upsflag | (blank) | (blank) | yes |
| quote picked but blank | p12_s_usps | (blank) | (blank) | yes |
| quote picked but blank | p12_s_ups | (blank) | (blank) | yes |
| quote picked but blank | p12_s_zone | (blank) | (blank) | yes |
| quote picked but blank | p12_s_gacom | (blank) | (blank) | yes |
| quote picked but blank | p12_s_garet | (blank) | (blank) | yes |
| quote picked but blank | p12_s_pri | (blank) | (blank) | yes |
| quote picked but blank | p12_s_upsgs | (blank) | (blank) | yes |
| quote picked but blank | p12_s_cheap | (blank) | (blank) | yes |
| quote picked but blank | p12_s_cheapname | (blank) | (blank) | yes |
| quote picked but blank | p12_s_saved | (blank) | (blank) | yes |
| quote picked but blank | p12_b_name | (blank) | (blank) | yes |
| quote picked but blank | p12_b_sale | (blank) | (blank) | yes |
| quote picked but blank | p12_b_ship | (blank) | (blank) | yes |
| quote picked but blank | p12_b_true | (blank) | (blank) | yes |
| quote picked but blank | p12_b_fees | (blank) | (blank) | yes |
| quote picked but blank | p12_b_net | (blank) | (blank) | yes |
| quote picked but blank | p12_b_margin | (blank) | (blank) | yes |
| quote picked but blank | p12_b_shipflag | (blank) | (blank) | yes |
| quote picked but blank | p12_b_flag | (blank) | (blank) | yes |
| quote picked but blank | p30_postage | (blank) | (blank) | yes |
| quote picked but blank | p30_labor | (blank) | (blank) | yes |
| quote picked but blank | p30_true | (blank) | (blank) | yes |
| quote picked but blank | p30_short | (blank) | (blank) | yes |
| quote picked but blank | p30_flag | (blank) | (blank) | yes |
| quote picked but blank | p30_share | (blank) | (blank) | yes |
| quote picked but blank | p30_d_name | (blank) | (blank) | yes |
| quote picked but blank | p30_d_lb | (blank) | (blank) | yes |
| quote picked but blank | p30_d_cubic | (blank) | (blank) | yes |
| quote picked but blank | p30_d_over | (blank) | (blank) | yes |
| quote picked but blank | p30_d_uspsdim | (blank) | (blank) | yes |
| quote picked but blank | p30_d_uspsbill | (blank) | (blank) | yes |
| quote picked but blank | p30_d_upsdim | (blank) | (blank) | yes |
| quote picked but blank | p30_d_upsbill | (blank) | (blank) | yes |
| quote picked but blank | p30_d_uspsflag | (blank) | (blank) | yes |
| quote picked but blank | p30_d_upsflag | (blank) | (blank) | yes |
| quote picked but blank | p30_s_usps | (blank) | (blank) | yes |
| quote picked but blank | p30_s_ups | (blank) | (blank) | yes |
| quote picked but blank | p30_s_zone | (blank) | (blank) | yes |
| quote picked but blank | p30_s_gacom | (blank) | (blank) | yes |
| quote picked but blank | p30_s_garet | (blank) | (blank) | yes |
| quote picked but blank | p30_s_pri | (blank) | (blank) | yes |
| quote picked but blank | p30_s_upsgs | (blank) | (blank) | yes |
| quote picked but blank | p30_s_cheap | (blank) | (blank) | yes |
| quote picked but blank | p30_s_cheapname | (blank) | (blank) | yes |
| quote picked but blank | p30_s_saved | (blank) | (blank) | yes |
| quote picked but blank | p30_b_name | (blank) | (blank) | yes |
| quote picked but blank | p30_b_sale | (blank) | (blank) | yes |
| quote picked but blank | p30_b_ship | (blank) | (blank) | yes |
| quote picked but blank | p30_b_true | (blank) | (blank) | yes |
| quote picked but blank | p30_b_fees | (blank) | (blank) | yes |
| quote picked but blank | p30_b_net | (blank) | (blank) | yes |
| quote picked but blank | p30_b_margin | (blank) | (blank) | yes |
| quote picked but blank | p30_b_shipflag | (blank) | (blank) | yes |
| quote picked but blank | p30_b_flag | (blank) | (blank) | yes |
| quote picked but blank | avg_true | 14.1143 | 14.1143 | yes |
| quote picked but blank | avg_short | -3.1643 | -3.1643 | yes |
| quote picked but blank | avg_share | 0.7728 | 0.7728 | yes |
| quote picked but blank | sc_cheap_total | 106.45 | 106.45 | yes |
| quote picked but blank | sc_saved_total | 35.8 | 35.8 | yes |
| quote picked but blank | db_losing | 1 | 1 | yes |
| quote picked but blank | db_under | 4 | 4 | yes |
| quote picked but blank | db_avgtrue | 14.1143 | 14.1143 | yes |
| quote picked but blank | db_avgshort | -3.1643 | -3.1643 | yes |
| quote picked but blank | db_shipcost | 98.8 | 98.8 | yes |
| quote picked but blank | db_collected | 93.6 | 93.6 | yes |
| quote picked but blank | db_netship | -5.2 | -5.2 | yes |
| quote picked but blank | db_share | 0.7728 | 0.7728 | yes |
| quote picked but blank | db_tot_true | 98.8 | 98.8 | yes |
| quote picked but blank | db_tot_fees | 48.732 | 48.732 | yes |
| quote picked but blank | db_tot_net | 109.3033 | 109.3033 | yes |
| quote picked but blank | fs_tc | 14.1143 | 14.1143 | yes |
| quote picked but blank | fs_tcused | 14.1143 | 14.1143 | yes |
| quote picked but blank | fs_profit_order | 13.9857 | 13.9857 | yes |
| quote picked but blank | fs_cost | 6.5 | 6.5 | yes |
| quote picked but blank | fs_breakeven | 62.4444 | 62.4444 | yes |
| quote picked but blank | fs_recommendation | Best of the three: free shipping over $75, about $393 more profit per 100 orders than today. An estimate built on your assumptions above, not a promise. | Best of the three: free shipping over $75, about $393 more profit per 100 orders than today. An estimate built on your assumptions above, not a promise. | yes |
| quote picked but blank | fs_avgo_today | 48 | 48 | yes |
| quote picked but blank | fs_avgo_s1 | 48 | 48 | yes |
| quote picked but blank | fs_avgo_s2 | 48 | 48 | yes |
| quote picked but blank | fs_avgo_s3 | 48 | 48 | yes |
| quote picked but blank | fs_orders_today | 100 | 100 | yes |
| quote picked but blank | fs_orders_s1 | 115 | 115 | yes |
| quote picked but blank | fs_orders_s2 | 115 | 115 | yes |
| quote picked but blank | fs_orders_s3 | 115 | 115 | yes |
| quote picked but blank | fs_qual_today | 0 | 0 | yes |
| quote picked but blank | fs_qual_s1 | 63.25 | 63.25 | yes |
| quote picked but blank | fs_qual_s2 | 34.5 | 34.5 | yes |
| quote picked but blank | fs_qual_s3 | 13.8 | 13.8 | yes |
| quote picked but blank | fs_other_today | 100 | 100 | yes |
| quote picked but blank | fs_other_s1 | 51.75 | 51.75 | yes |
| quote picked but blank | fs_other_s2 | 80.5 | 80.5 | yes |
| quote picked but blank | fs_other_s3 | 101.2 | 101.2 | yes |
| quote picked but blank | fs_rev_today | 4,800 | 4,800 | yes |
| quote picked but blank | fs_rev_s1 | 5,646.5 | 5,646.5 | yes |
| quote picked but blank | fs_rev_s2 | 6,072 | 6,072 | yes |
| quote picked but blank | fs_rev_s3 | 6,127.2 | 6,127.2 | yes |
| quote picked but blank | fs_coll_today | 650 | 650 | yes |
| quote picked but blank | fs_coll_s1 | 336.375 | 336.375 | yes |
| quote picked but blank | fs_coll_s2 | 523.25 | 523.25 | yes |
| quote picked but blank | fs_coll_s3 | 657.8 | 657.8 | yes |
| quote picked but blank | fs_parc_today | 1,411.4286 | 1,411.4286 | yes |
| quote picked but blank | fs_parc_s1 | 1,623.1429 | 1,623.1429 | yes |
| quote picked but blank | fs_parc_s2 | 1,623.1429 | 1,623.1429 | yes |
| quote picked but blank | fs_parc_s3 | 1,623.1429 | 1,623.1429 | yes |
| quote picked but blank | fs_profit_today | 1,398.5714 | 1,398.5714 | yes |
| quote picked but blank | fs_profit_s1 | 1,254.1571 | 1,254.1571 | yes |
| quote picked but blank | fs_profit_s2 | 1,632.5071 | 1,632.5071 | yes |
| quote picked but blank | fs_profit_s3 | 1,791.8971 | 1,791.8971 | yes |
| quote picked but blank | fs_per_today | 13.9857 | 13.9857 | yes |
| quote picked but blank | fs_per_s1 | 10.9057 | 10.9057 | yes |
| quote picked but blank | fs_per_s2 | 14.1957 | 14.1957 | yes |
| quote picked but blank | fs_per_s3 | 15.5817 | 15.5817 | yes |
| quote picked but blank | fs_chg_today | 0 | 0 | yes |
| quote picked but blank | fs_chg_s1 | -144.4143 | -144.4143 | yes |
| quote picked but blank | fs_chg_s2 | 233.9357 | 233.9357 | yes |
| quote picked but blank | fs_chg_s3 | 393.3257 | 393.3257 | yes |
| quote picked but blank | fs_verdict_today | baseline | Today | intended: baseline column now reads Today |
| quote picked but blank | fs_verdict_s1 | WORSE THAN TODAY | Worse than today | intended: sentence case only, same status word |
| quote picked but blank | fs_verdict_s2 | BEATS TODAY | Beats today | intended: sentence case only, same status word |
| quote picked but blank | fs_verdict_s3 | BEATS TODAY | Beats today | intended: sentence case only, same status word |
| blank shop | p1_postage | (blank) | (blank) | yes |
| blank shop | p1_labor | (blank) | (blank) | yes |
| blank shop | p1_true | (blank) | (blank) | yes |
| blank shop | p1_short | (blank) | (blank) | yes |
| blank shop | p1_flag | (blank) | (blank) | yes |
| blank shop | p1_share | (blank) | (blank) | yes |
| blank shop | p1_d_name | (blank) | (blank) | yes |
| blank shop | p1_d_lb | (blank) | (blank) | yes |
| blank shop | p1_d_cubic | (blank) | (blank) | yes |
| blank shop | p1_d_over | (blank) | (blank) | yes |
| blank shop | p1_d_uspsdim | (blank) | (blank) | yes |
| blank shop | p1_d_uspsbill | (blank) | (blank) | yes |
| blank shop | p1_d_upsdim | (blank) | (blank) | yes |
| blank shop | p1_d_upsbill | (blank) | (blank) | yes |
| blank shop | p1_d_uspsflag | (blank) | (blank) | yes |
| blank shop | p1_d_upsflag | (blank) | (blank) | yes |
| blank shop | p1_s_usps | (blank) | (blank) | yes |
| blank shop | p1_s_ups | (blank) | (blank) | yes |
| blank shop | p1_s_zone | (blank) | (blank) | yes |
| blank shop | p1_s_gacom | (blank) | (blank) | yes |
| blank shop | p1_s_garet | (blank) | (blank) | yes |
| blank shop | p1_s_pri | (blank) | (blank) | yes |
| blank shop | p1_s_upsgs | (blank) | (blank) | yes |
| blank shop | p1_s_cheap | (blank) | (blank) | yes |
| blank shop | p1_s_cheapname | (blank) | (blank) | yes |
| blank shop | p1_s_saved | (blank) | (blank) | yes |
| blank shop | p1_b_name | (blank) | (blank) | yes |
| blank shop | p1_b_sale | (blank) | (blank) | yes |
| blank shop | p1_b_ship | (blank) | (blank) | yes |
| blank shop | p1_b_true | (blank) | (blank) | yes |
| blank shop | p1_b_fees | (blank) | (blank) | yes |
| blank shop | p1_b_net | (blank) | (blank) | yes |
| blank shop | p1_b_margin | (blank) | (blank) | yes |
| blank shop | p1_b_shipflag | (blank) | (blank) | yes |
| blank shop | p1_b_flag | (blank) | (blank) | yes |
| blank shop | p2_postage | (blank) | (blank) | yes |
| blank shop | p2_labor | (blank) | (blank) | yes |
| blank shop | p2_true | (blank) | (blank) | yes |
| blank shop | p2_short | (blank) | (blank) | yes |
| blank shop | p2_flag | (blank) | (blank) | yes |
| blank shop | p2_share | (blank) | (blank) | yes |
| blank shop | p2_d_name | (blank) | (blank) | yes |
| blank shop | p2_d_lb | (blank) | (blank) | yes |
| blank shop | p2_d_cubic | (blank) | (blank) | yes |
| blank shop | p2_d_over | (blank) | (blank) | yes |
| blank shop | p2_d_uspsdim | (blank) | (blank) | yes |
| blank shop | p2_d_uspsbill | (blank) | (blank) | yes |
| blank shop | p2_d_upsdim | (blank) | (blank) | yes |
| blank shop | p2_d_upsbill | (blank) | (blank) | yes |
| blank shop | p2_d_uspsflag | (blank) | (blank) | yes |
| blank shop | p2_d_upsflag | (blank) | (blank) | yes |
| blank shop | p2_s_usps | (blank) | (blank) | yes |
| blank shop | p2_s_ups | (blank) | (blank) | yes |
| blank shop | p2_s_zone | (blank) | (blank) | yes |
| blank shop | p2_s_gacom | (blank) | (blank) | yes |
| blank shop | p2_s_garet | (blank) | (blank) | yes |
| blank shop | p2_s_pri | (blank) | (blank) | yes |
| blank shop | p2_s_upsgs | (blank) | (blank) | yes |
| blank shop | p2_s_cheap | (blank) | (blank) | yes |
| blank shop | p2_s_cheapname | (blank) | (blank) | yes |
| blank shop | p2_s_saved | (blank) | (blank) | yes |
| blank shop | p2_b_name | (blank) | (blank) | yes |
| blank shop | p2_b_sale | (blank) | (blank) | yes |
| blank shop | p2_b_ship | (blank) | (blank) | yes |
| blank shop | p2_b_true | (blank) | (blank) | yes |
| blank shop | p2_b_fees | (blank) | (blank) | yes |
| blank shop | p2_b_net | (blank) | (blank) | yes |
| blank shop | p2_b_margin | (blank) | (blank) | yes |
| blank shop | p2_b_shipflag | (blank) | (blank) | yes |
| blank shop | p2_b_flag | (blank) | (blank) | yes |
| blank shop | p3_postage | (blank) | (blank) | yes |
| blank shop | p3_labor | (blank) | (blank) | yes |
| blank shop | p3_true | (blank) | (blank) | yes |
| blank shop | p3_short | (blank) | (blank) | yes |
| blank shop | p3_flag | (blank) | (blank) | yes |
| blank shop | p3_share | (blank) | (blank) | yes |
| blank shop | p3_d_name | (blank) | (blank) | yes |
| blank shop | p3_d_lb | (blank) | (blank) | yes |
| blank shop | p3_d_cubic | (blank) | (blank) | yes |
| blank shop | p3_d_over | (blank) | (blank) | yes |
| blank shop | p3_d_uspsdim | (blank) | (blank) | yes |
| blank shop | p3_d_uspsbill | (blank) | (blank) | yes |
| blank shop | p3_d_upsdim | (blank) | (blank) | yes |
| blank shop | p3_d_upsbill | (blank) | (blank) | yes |
| blank shop | p3_d_uspsflag | (blank) | (blank) | yes |
| blank shop | p3_d_upsflag | (blank) | (blank) | yes |
| blank shop | p3_s_usps | (blank) | (blank) | yes |
| blank shop | p3_s_ups | (blank) | (blank) | yes |
| blank shop | p3_s_zone | (blank) | (blank) | yes |
| blank shop | p3_s_gacom | (blank) | (blank) | yes |
| blank shop | p3_s_garet | (blank) | (blank) | yes |
| blank shop | p3_s_pri | (blank) | (blank) | yes |
| blank shop | p3_s_upsgs | (blank) | (blank) | yes |
| blank shop | p3_s_cheap | (blank) | (blank) | yes |
| blank shop | p3_s_cheapname | (blank) | (blank) | yes |
| blank shop | p3_s_saved | (blank) | (blank) | yes |
| blank shop | p3_b_name | (blank) | (blank) | yes |
| blank shop | p3_b_sale | (blank) | (blank) | yes |
| blank shop | p3_b_ship | (blank) | (blank) | yes |
| blank shop | p3_b_true | (blank) | (blank) | yes |
| blank shop | p3_b_fees | (blank) | (blank) | yes |
| blank shop | p3_b_net | (blank) | (blank) | yes |
| blank shop | p3_b_margin | (blank) | (blank) | yes |
| blank shop | p3_b_shipflag | (blank) | (blank) | yes |
| blank shop | p3_b_flag | (blank) | (blank) | yes |
| blank shop | p4_postage | (blank) | (blank) | yes |
| blank shop | p4_labor | (blank) | (blank) | yes |
| blank shop | p4_true | (blank) | (blank) | yes |
| blank shop | p4_short | (blank) | (blank) | yes |
| blank shop | p4_flag | (blank) | (blank) | yes |
| blank shop | p4_share | (blank) | (blank) | yes |
| blank shop | p4_d_name | (blank) | (blank) | yes |
| blank shop | p4_d_lb | (blank) | (blank) | yes |
| blank shop | p4_d_cubic | (blank) | (blank) | yes |
| blank shop | p4_d_over | (blank) | (blank) | yes |
| blank shop | p4_d_uspsdim | (blank) | (blank) | yes |
| blank shop | p4_d_uspsbill | (blank) | (blank) | yes |
| blank shop | p4_d_upsdim | (blank) | (blank) | yes |
| blank shop | p4_d_upsbill | (blank) | (blank) | yes |
| blank shop | p4_d_uspsflag | (blank) | (blank) | yes |
| blank shop | p4_d_upsflag | (blank) | (blank) | yes |
| blank shop | p4_s_usps | (blank) | (blank) | yes |
| blank shop | p4_s_ups | (blank) | (blank) | yes |
| blank shop | p4_s_zone | (blank) | (blank) | yes |
| blank shop | p4_s_gacom | (blank) | (blank) | yes |
| blank shop | p4_s_garet | (blank) | (blank) | yes |
| blank shop | p4_s_pri | (blank) | (blank) | yes |
| blank shop | p4_s_upsgs | (blank) | (blank) | yes |
| blank shop | p4_s_cheap | (blank) | (blank) | yes |
| blank shop | p4_s_cheapname | (blank) | (blank) | yes |
| blank shop | p4_s_saved | (blank) | (blank) | yes |
| blank shop | p4_b_name | (blank) | (blank) | yes |
| blank shop | p4_b_sale | (blank) | (blank) | yes |
| blank shop | p4_b_ship | (blank) | (blank) | yes |
| blank shop | p4_b_true | (blank) | (blank) | yes |
| blank shop | p4_b_fees | (blank) | (blank) | yes |
| blank shop | p4_b_net | (blank) | (blank) | yes |
| blank shop | p4_b_margin | (blank) | (blank) | yes |
| blank shop | p4_b_shipflag | (blank) | (blank) | yes |
| blank shop | p4_b_flag | (blank) | (blank) | yes |
| blank shop | p5_postage | (blank) | (blank) | yes |
| blank shop | p5_labor | (blank) | (blank) | yes |
| blank shop | p5_true | (blank) | (blank) | yes |
| blank shop | p5_short | (blank) | (blank) | yes |
| blank shop | p5_flag | (blank) | (blank) | yes |
| blank shop | p5_share | (blank) | (blank) | yes |
| blank shop | p5_d_name | (blank) | (blank) | yes |
| blank shop | p5_d_lb | (blank) | (blank) | yes |
| blank shop | p5_d_cubic | (blank) | (blank) | yes |
| blank shop | p5_d_over | (blank) | (blank) | yes |
| blank shop | p5_d_uspsdim | (blank) | (blank) | yes |
| blank shop | p5_d_uspsbill | (blank) | (blank) | yes |
| blank shop | p5_d_upsdim | (blank) | (blank) | yes |
| blank shop | p5_d_upsbill | (blank) | (blank) | yes |
| blank shop | p5_d_uspsflag | (blank) | (blank) | yes |
| blank shop | p5_d_upsflag | (blank) | (blank) | yes |
| blank shop | p5_s_usps | (blank) | (blank) | yes |
| blank shop | p5_s_ups | (blank) | (blank) | yes |
| blank shop | p5_s_zone | (blank) | (blank) | yes |
| blank shop | p5_s_gacom | (blank) | (blank) | yes |
| blank shop | p5_s_garet | (blank) | (blank) | yes |
| blank shop | p5_s_pri | (blank) | (blank) | yes |
| blank shop | p5_s_upsgs | (blank) | (blank) | yes |
| blank shop | p5_s_cheap | (blank) | (blank) | yes |
| blank shop | p5_s_cheapname | (blank) | (blank) | yes |
| blank shop | p5_s_saved | (blank) | (blank) | yes |
| blank shop | p5_b_name | (blank) | (blank) | yes |
| blank shop | p5_b_sale | (blank) | (blank) | yes |
| blank shop | p5_b_ship | (blank) | (blank) | yes |
| blank shop | p5_b_true | (blank) | (blank) | yes |
| blank shop | p5_b_fees | (blank) | (blank) | yes |
| blank shop | p5_b_net | (blank) | (blank) | yes |
| blank shop | p5_b_margin | (blank) | (blank) | yes |
| blank shop | p5_b_shipflag | (blank) | (blank) | yes |
| blank shop | p5_b_flag | (blank) | (blank) | yes |
| blank shop | p6_postage | (blank) | (blank) | yes |
| blank shop | p6_labor | (blank) | (blank) | yes |
| blank shop | p6_true | (blank) | (blank) | yes |
| blank shop | p6_short | (blank) | (blank) | yes |
| blank shop | p6_flag | (blank) | (blank) | yes |
| blank shop | p6_share | (blank) | (blank) | yes |
| blank shop | p6_d_name | (blank) | (blank) | yes |
| blank shop | p6_d_lb | (blank) | (blank) | yes |
| blank shop | p6_d_cubic | (blank) | (blank) | yes |
| blank shop | p6_d_over | (blank) | (blank) | yes |
| blank shop | p6_d_uspsdim | (blank) | (blank) | yes |
| blank shop | p6_d_uspsbill | (blank) | (blank) | yes |
| blank shop | p6_d_upsdim | (blank) | (blank) | yes |
| blank shop | p6_d_upsbill | (blank) | (blank) | yes |
| blank shop | p6_d_uspsflag | (blank) | (blank) | yes |
| blank shop | p6_d_upsflag | (blank) | (blank) | yes |
| blank shop | p6_s_usps | (blank) | (blank) | yes |
| blank shop | p6_s_ups | (blank) | (blank) | yes |
| blank shop | p6_s_zone | (blank) | (blank) | yes |
| blank shop | p6_s_gacom | (blank) | (blank) | yes |
| blank shop | p6_s_garet | (blank) | (blank) | yes |
| blank shop | p6_s_pri | (blank) | (blank) | yes |
| blank shop | p6_s_upsgs | (blank) | (blank) | yes |
| blank shop | p6_s_cheap | (blank) | (blank) | yes |
| blank shop | p6_s_cheapname | (blank) | (blank) | yes |
| blank shop | p6_s_saved | (blank) | (blank) | yes |
| blank shop | p6_b_name | (blank) | (blank) | yes |
| blank shop | p6_b_sale | (blank) | (blank) | yes |
| blank shop | p6_b_ship | (blank) | (blank) | yes |
| blank shop | p6_b_true | (blank) | (blank) | yes |
| blank shop | p6_b_fees | (blank) | (blank) | yes |
| blank shop | p6_b_net | (blank) | (blank) | yes |
| blank shop | p6_b_margin | (blank) | (blank) | yes |
| blank shop | p6_b_shipflag | (blank) | (blank) | yes |
| blank shop | p6_b_flag | (blank) | (blank) | yes |
| blank shop | p7_postage | (blank) | (blank) | yes |
| blank shop | p7_labor | (blank) | (blank) | yes |
| blank shop | p7_true | (blank) | (blank) | yes |
| blank shop | p7_short | (blank) | (blank) | yes |
| blank shop | p7_flag | (blank) | (blank) | yes |
| blank shop | p7_share | (blank) | (blank) | yes |
| blank shop | p7_d_name | (blank) | (blank) | yes |
| blank shop | p7_d_lb | (blank) | (blank) | yes |
| blank shop | p7_d_cubic | (blank) | (blank) | yes |
| blank shop | p7_d_over | (blank) | (blank) | yes |
| blank shop | p7_d_uspsdim | (blank) | (blank) | yes |
| blank shop | p7_d_uspsbill | (blank) | (blank) | yes |
| blank shop | p7_d_upsdim | (blank) | (blank) | yes |
| blank shop | p7_d_upsbill | (blank) | (blank) | yes |
| blank shop | p7_d_uspsflag | (blank) | (blank) | yes |
| blank shop | p7_d_upsflag | (blank) | (blank) | yes |
| blank shop | p7_s_usps | (blank) | (blank) | yes |
| blank shop | p7_s_ups | (blank) | (blank) | yes |
| blank shop | p7_s_zone | (blank) | (blank) | yes |
| blank shop | p7_s_gacom | (blank) | (blank) | yes |
| blank shop | p7_s_garet | (blank) | (blank) | yes |
| blank shop | p7_s_pri | (blank) | (blank) | yes |
| blank shop | p7_s_upsgs | (blank) | (blank) | yes |
| blank shop | p7_s_cheap | (blank) | (blank) | yes |
| blank shop | p7_s_cheapname | (blank) | (blank) | yes |
| blank shop | p7_s_saved | (blank) | (blank) | yes |
| blank shop | p7_b_name | (blank) | (blank) | yes |
| blank shop | p7_b_sale | (blank) | (blank) | yes |
| blank shop | p7_b_ship | (blank) | (blank) | yes |
| blank shop | p7_b_true | (blank) | (blank) | yes |
| blank shop | p7_b_fees | (blank) | (blank) | yes |
| blank shop | p7_b_net | (blank) | (blank) | yes |
| blank shop | p7_b_margin | (blank) | (blank) | yes |
| blank shop | p7_b_shipflag | (blank) | (blank) | yes |
| blank shop | p7_b_flag | (blank) | (blank) | yes |
| blank shop | p8_postage | (blank) | (blank) | yes |
| blank shop | p8_labor | (blank) | (blank) | yes |
| blank shop | p8_true | (blank) | (blank) | yes |
| blank shop | p8_short | (blank) | (blank) | yes |
| blank shop | p8_flag | (blank) | (blank) | yes |
| blank shop | p8_share | (blank) | (blank) | yes |
| blank shop | p8_d_name | (blank) | (blank) | yes |
| blank shop | p8_d_lb | (blank) | (blank) | yes |
| blank shop | p8_d_cubic | (blank) | (blank) | yes |
| blank shop | p8_d_over | (blank) | (blank) | yes |
| blank shop | p8_d_uspsdim | (blank) | (blank) | yes |
| blank shop | p8_d_uspsbill | (blank) | (blank) | yes |
| blank shop | p8_d_upsdim | (blank) | (blank) | yes |
| blank shop | p8_d_upsbill | (blank) | (blank) | yes |
| blank shop | p8_d_uspsflag | (blank) | (blank) | yes |
| blank shop | p8_d_upsflag | (blank) | (blank) | yes |
| blank shop | p8_s_usps | (blank) | (blank) | yes |
| blank shop | p8_s_ups | (blank) | (blank) | yes |
| blank shop | p8_s_zone | (blank) | (blank) | yes |
| blank shop | p8_s_gacom | (blank) | (blank) | yes |
| blank shop | p8_s_garet | (blank) | (blank) | yes |
| blank shop | p8_s_pri | (blank) | (blank) | yes |
| blank shop | p8_s_upsgs | (blank) | (blank) | yes |
| blank shop | p8_s_cheap | (blank) | (blank) | yes |
| blank shop | p8_s_cheapname | (blank) | (blank) | yes |
| blank shop | p8_s_saved | (blank) | (blank) | yes |
| blank shop | p8_b_name | (blank) | (blank) | yes |
| blank shop | p8_b_sale | (blank) | (blank) | yes |
| blank shop | p8_b_ship | (blank) | (blank) | yes |
| blank shop | p8_b_true | (blank) | (blank) | yes |
| blank shop | p8_b_fees | (blank) | (blank) | yes |
| blank shop | p8_b_net | (blank) | (blank) | yes |
| blank shop | p8_b_margin | (blank) | (blank) | yes |
| blank shop | p8_b_shipflag | (blank) | (blank) | yes |
| blank shop | p8_b_flag | (blank) | (blank) | yes |
| blank shop | p9_postage | (blank) | (blank) | yes |
| blank shop | p9_labor | (blank) | (blank) | yes |
| blank shop | p9_true | (blank) | (blank) | yes |
| blank shop | p9_short | (blank) | (blank) | yes |
| blank shop | p9_flag | (blank) | (blank) | yes |
| blank shop | p9_share | (blank) | (blank) | yes |
| blank shop | p9_d_name | (blank) | (blank) | yes |
| blank shop | p9_d_lb | (blank) | (blank) | yes |
| blank shop | p9_d_cubic | (blank) | (blank) | yes |
| blank shop | p9_d_over | (blank) | (blank) | yes |
| blank shop | p9_d_uspsdim | (blank) | (blank) | yes |
| blank shop | p9_d_uspsbill | (blank) | (blank) | yes |
| blank shop | p9_d_upsdim | (blank) | (blank) | yes |
| blank shop | p9_d_upsbill | (blank) | (blank) | yes |
| blank shop | p9_d_uspsflag | (blank) | (blank) | yes |
| blank shop | p9_d_upsflag | (blank) | (blank) | yes |
| blank shop | p9_s_usps | (blank) | (blank) | yes |
| blank shop | p9_s_ups | (blank) | (blank) | yes |
| blank shop | p9_s_zone | (blank) | (blank) | yes |
| blank shop | p9_s_gacom | (blank) | (blank) | yes |
| blank shop | p9_s_garet | (blank) | (blank) | yes |
| blank shop | p9_s_pri | (blank) | (blank) | yes |
| blank shop | p9_s_upsgs | (blank) | (blank) | yes |
| blank shop | p9_s_cheap | (blank) | (blank) | yes |
| blank shop | p9_s_cheapname | (blank) | (blank) | yes |
| blank shop | p9_s_saved | (blank) | (blank) | yes |
| blank shop | p9_b_name | (blank) | (blank) | yes |
| blank shop | p9_b_sale | (blank) | (blank) | yes |
| blank shop | p9_b_ship | (blank) | (blank) | yes |
| blank shop | p9_b_true | (blank) | (blank) | yes |
| blank shop | p9_b_fees | (blank) | (blank) | yes |
| blank shop | p9_b_net | (blank) | (blank) | yes |
| blank shop | p9_b_margin | (blank) | (blank) | yes |
| blank shop | p9_b_shipflag | (blank) | (blank) | yes |
| blank shop | p9_b_flag | (blank) | (blank) | yes |
| blank shop | p10_postage | (blank) | (blank) | yes |
| blank shop | p10_labor | (blank) | (blank) | yes |
| blank shop | p10_true | (blank) | (blank) | yes |
| blank shop | p10_short | (blank) | (blank) | yes |
| blank shop | p10_flag | (blank) | (blank) | yes |
| blank shop | p10_share | (blank) | (blank) | yes |
| blank shop | p10_d_name | (blank) | (blank) | yes |
| blank shop | p10_d_lb | (blank) | (blank) | yes |
| blank shop | p10_d_cubic | (blank) | (blank) | yes |
| blank shop | p10_d_over | (blank) | (blank) | yes |
| blank shop | p10_d_uspsdim | (blank) | (blank) | yes |
| blank shop | p10_d_uspsbill | (blank) | (blank) | yes |
| blank shop | p10_d_upsdim | (blank) | (blank) | yes |
| blank shop | p10_d_upsbill | (blank) | (blank) | yes |
| blank shop | p10_d_uspsflag | (blank) | (blank) | yes |
| blank shop | p10_d_upsflag | (blank) | (blank) | yes |
| blank shop | p10_s_usps | (blank) | (blank) | yes |
| blank shop | p10_s_ups | (blank) | (blank) | yes |
| blank shop | p10_s_zone | (blank) | (blank) | yes |
| blank shop | p10_s_gacom | (blank) | (blank) | yes |
| blank shop | p10_s_garet | (blank) | (blank) | yes |
| blank shop | p10_s_pri | (blank) | (blank) | yes |
| blank shop | p10_s_upsgs | (blank) | (blank) | yes |
| blank shop | p10_s_cheap | (blank) | (blank) | yes |
| blank shop | p10_s_cheapname | (blank) | (blank) | yes |
| blank shop | p10_s_saved | (blank) | (blank) | yes |
| blank shop | p10_b_name | (blank) | (blank) | yes |
| blank shop | p10_b_sale | (blank) | (blank) | yes |
| blank shop | p10_b_ship | (blank) | (blank) | yes |
| blank shop | p10_b_true | (blank) | (blank) | yes |
| blank shop | p10_b_fees | (blank) | (blank) | yes |
| blank shop | p10_b_net | (blank) | (blank) | yes |
| blank shop | p10_b_margin | (blank) | (blank) | yes |
| blank shop | p10_b_shipflag | (blank) | (blank) | yes |
| blank shop | p10_b_flag | (blank) | (blank) | yes |
| blank shop | p11_postage | (blank) | (blank) | yes |
| blank shop | p11_labor | (blank) | (blank) | yes |
| blank shop | p11_true | (blank) | (blank) | yes |
| blank shop | p11_short | (blank) | (blank) | yes |
| blank shop | p11_flag | (blank) | (blank) | yes |
| blank shop | p11_share | (blank) | (blank) | yes |
| blank shop | p11_d_name | (blank) | (blank) | yes |
| blank shop | p11_d_lb | (blank) | (blank) | yes |
| blank shop | p11_d_cubic | (blank) | (blank) | yes |
| blank shop | p11_d_over | (blank) | (blank) | yes |
| blank shop | p11_d_uspsdim | (blank) | (blank) | yes |
| blank shop | p11_d_uspsbill | (blank) | (blank) | yes |
| blank shop | p11_d_upsdim | (blank) | (blank) | yes |
| blank shop | p11_d_upsbill | (blank) | (blank) | yes |
| blank shop | p11_d_uspsflag | (blank) | (blank) | yes |
| blank shop | p11_d_upsflag | (blank) | (blank) | yes |
| blank shop | p11_s_usps | (blank) | (blank) | yes |
| blank shop | p11_s_ups | (blank) | (blank) | yes |
| blank shop | p11_s_zone | (blank) | (blank) | yes |
| blank shop | p11_s_gacom | (blank) | (blank) | yes |
| blank shop | p11_s_garet | (blank) | (blank) | yes |
| blank shop | p11_s_pri | (blank) | (blank) | yes |
| blank shop | p11_s_upsgs | (blank) | (blank) | yes |
| blank shop | p11_s_cheap | (blank) | (blank) | yes |
| blank shop | p11_s_cheapname | (blank) | (blank) | yes |
| blank shop | p11_s_saved | (blank) | (blank) | yes |
| blank shop | p11_b_name | (blank) | (blank) | yes |
| blank shop | p11_b_sale | (blank) | (blank) | yes |
| blank shop | p11_b_ship | (blank) | (blank) | yes |
| blank shop | p11_b_true | (blank) | (blank) | yes |
| blank shop | p11_b_fees | (blank) | (blank) | yes |
| blank shop | p11_b_net | (blank) | (blank) | yes |
| blank shop | p11_b_margin | (blank) | (blank) | yes |
| blank shop | p11_b_shipflag | (blank) | (blank) | yes |
| blank shop | p11_b_flag | (blank) | (blank) | yes |
| blank shop | p12_postage | (blank) | (blank) | yes |
| blank shop | p12_labor | (blank) | (blank) | yes |
| blank shop | p12_true | (blank) | (blank) | yes |
| blank shop | p12_short | (blank) | (blank) | yes |
| blank shop | p12_flag | (blank) | (blank) | yes |
| blank shop | p12_share | (blank) | (blank) | yes |
| blank shop | p12_d_name | (blank) | (blank) | yes |
| blank shop | p12_d_lb | (blank) | (blank) | yes |
| blank shop | p12_d_cubic | (blank) | (blank) | yes |
| blank shop | p12_d_over | (blank) | (blank) | yes |
| blank shop | p12_d_uspsdim | (blank) | (blank) | yes |
| blank shop | p12_d_uspsbill | (blank) | (blank) | yes |
| blank shop | p12_d_upsdim | (blank) | (blank) | yes |
| blank shop | p12_d_upsbill | (blank) | (blank) | yes |
| blank shop | p12_d_uspsflag | (blank) | (blank) | yes |
| blank shop | p12_d_upsflag | (blank) | (blank) | yes |
| blank shop | p12_s_usps | (blank) | (blank) | yes |
| blank shop | p12_s_ups | (blank) | (blank) | yes |
| blank shop | p12_s_zone | (blank) | (blank) | yes |
| blank shop | p12_s_gacom | (blank) | (blank) | yes |
| blank shop | p12_s_garet | (blank) | (blank) | yes |
| blank shop | p12_s_pri | (blank) | (blank) | yes |
| blank shop | p12_s_upsgs | (blank) | (blank) | yes |
| blank shop | p12_s_cheap | (blank) | (blank) | yes |
| blank shop | p12_s_cheapname | (blank) | (blank) | yes |
| blank shop | p12_s_saved | (blank) | (blank) | yes |
| blank shop | p12_b_name | (blank) | (blank) | yes |
| blank shop | p12_b_sale | (blank) | (blank) | yes |
| blank shop | p12_b_ship | (blank) | (blank) | yes |
| blank shop | p12_b_true | (blank) | (blank) | yes |
| blank shop | p12_b_fees | (blank) | (blank) | yes |
| blank shop | p12_b_net | (blank) | (blank) | yes |
| blank shop | p12_b_margin | (blank) | (blank) | yes |
| blank shop | p12_b_shipflag | (blank) | (blank) | yes |
| blank shop | p12_b_flag | (blank) | (blank) | yes |
| blank shop | p30_postage | (blank) | (blank) | yes |
| blank shop | p30_labor | (blank) | (blank) | yes |
| blank shop | p30_true | (blank) | (blank) | yes |
| blank shop | p30_short | (blank) | (blank) | yes |
| blank shop | p30_flag | (blank) | (blank) | yes |
| blank shop | p30_share | (blank) | (blank) | yes |
| blank shop | p30_d_name | (blank) | (blank) | yes |
| blank shop | p30_d_lb | (blank) | (blank) | yes |
| blank shop | p30_d_cubic | (blank) | (blank) | yes |
| blank shop | p30_d_over | (blank) | (blank) | yes |
| blank shop | p30_d_uspsdim | (blank) | (blank) | yes |
| blank shop | p30_d_uspsbill | (blank) | (blank) | yes |
| blank shop | p30_d_upsdim | (blank) | (blank) | yes |
| blank shop | p30_d_upsbill | (blank) | (blank) | yes |
| blank shop | p30_d_uspsflag | (blank) | (blank) | yes |
| blank shop | p30_d_upsflag | (blank) | (blank) | yes |
| blank shop | p30_s_usps | (blank) | (blank) | yes |
| blank shop | p30_s_ups | (blank) | (blank) | yes |
| blank shop | p30_s_zone | (blank) | (blank) | yes |
| blank shop | p30_s_gacom | (blank) | (blank) | yes |
| blank shop | p30_s_garet | (blank) | (blank) | yes |
| blank shop | p30_s_pri | (blank) | (blank) | yes |
| blank shop | p30_s_upsgs | (blank) | (blank) | yes |
| blank shop | p30_s_cheap | (blank) | (blank) | yes |
| blank shop | p30_s_cheapname | (blank) | (blank) | yes |
| blank shop | p30_s_saved | (blank) | (blank) | yes |
| blank shop | p30_b_name | (blank) | (blank) | yes |
| blank shop | p30_b_sale | (blank) | (blank) | yes |
| blank shop | p30_b_ship | (blank) | (blank) | yes |
| blank shop | p30_b_true | (blank) | (blank) | yes |
| blank shop | p30_b_fees | (blank) | (blank) | yes |
| blank shop | p30_b_net | (blank) | (blank) | yes |
| blank shop | p30_b_margin | (blank) | (blank) | yes |
| blank shop | p30_b_shipflag | (blank) | (blank) | yes |
| blank shop | p30_b_flag | (blank) | (blank) | yes |
| blank shop | avg_true | 0 | 0 | yes |
| blank shop | avg_short | 0 | 0 | yes |
| blank shop | avg_share | 0 | 0 | yes |
| blank shop | sc_cheap_total | 0 | 0 | yes |
| blank shop | sc_saved_total | 0 | 0 | yes |
| blank shop | db_losing | 0 | 0 | yes |
| blank shop | db_under | 0 | 0 | yes |
| blank shop | db_avgtrue | 0 | 0 | yes |
| blank shop | db_avgshort | 0 | 0 | yes |
| blank shop | db_shipcost | 0 | 0 | yes |
| blank shop | db_collected | 0 | 0 | yes |
| blank shop | db_netship | 0 | 0 | yes |
| blank shop | db_share | 0 | 0 | yes |
| blank shop | db_tot_true | 0 | 0 | yes |
| blank shop | db_tot_fees | 0 | 0 | yes |
| blank shop | db_tot_net | 0 | 0 | yes |
| blank shop | fs_tc | 0 | 0 | yes |
| blank shop | fs_tcused | 0 | 0 | yes |
| blank shop | fs_profit_order | 28.1 | 28.1 | yes |
| blank shop | fs_cost | 6.5 | 6.5 | yes |
| blank shop | fs_breakeven | 62.4444 | 62.4444 | yes |
| blank shop | fs_recommendation | Enter your true parcel cost first (it fills in from the Parcel-Cost Builder, or type one in the override cell). | Enter your true parcel cost first (it fills in from tab 1, or type one in the override cell). | intended: names the new tab 1 instead of the old tab name; same advice |
| blank shop | fs_avgo_today | 48 | 48 | yes |
| blank shop | fs_avgo_s1 | 48 | 48 | yes |
| blank shop | fs_avgo_s2 | 48 | 48 | yes |
| blank shop | fs_avgo_s3 | 48 | 48 | yes |
| blank shop | fs_orders_today | 100 | 100 | yes |
| blank shop | fs_orders_s1 | 115 | 115 | yes |
| blank shop | fs_orders_s2 | 115 | 115 | yes |
| blank shop | fs_orders_s3 | 115 | 115 | yes |
| blank shop | fs_qual_today | 0 | 0 | yes |
| blank shop | fs_qual_s1 | 63.25 | 63.25 | yes |
| blank shop | fs_qual_s2 | 34.5 | 34.5 | yes |
| blank shop | fs_qual_s3 | 13.8 | 13.8 | yes |
| blank shop | fs_other_today | 100 | 100 | yes |
| blank shop | fs_other_s1 | 51.75 | 51.75 | yes |
| blank shop | fs_other_s2 | 80.5 | 80.5 | yes |
| blank shop | fs_other_s3 | 101.2 | 101.2 | yes |
| blank shop | fs_rev_today | 4,800 | 4,800 | yes |
| blank shop | fs_rev_s1 | 5,646.5 | 5,646.5 | yes |
| blank shop | fs_rev_s2 | 6,072 | 6,072 | yes |
| blank shop | fs_rev_s3 | 6,127.2 | 6,127.2 | yes |
| blank shop | fs_coll_today | 650 | 650 | yes |
| blank shop | fs_coll_s1 | 336.375 | 336.375 | yes |
| blank shop | fs_coll_s2 | 523.25 | 523.25 | yes |
| blank shop | fs_coll_s3 | 657.8 | 657.8 | yes |
| blank shop | fs_parc_today | 0 | 0 | yes |
| blank shop | fs_parc_s1 | 0 | 0 | yes |
| blank shop | fs_parc_s2 | 0 | 0 | yes |
| blank shop | fs_parc_s3 | 0 | 0 | yes |
| blank shop | fs_profit_today | 2,810 | 2,810 | yes |
| blank shop | fs_profit_s1 | 2,877.3 | 2,877.3 | yes |
| blank shop | fs_profit_s2 | 3,255.65 | 3,255.65 | yes |
| blank shop | fs_profit_s3 | 3,415.04 | 3,415.04 | yes |
| blank shop | fs_per_today | 28.1 | 28.1 | yes |
| blank shop | fs_per_s1 | 25.02 | 25.02 | yes |
| blank shop | fs_per_s2 | 28.31 | 28.31 | yes |
| blank shop | fs_per_s3 | 29.696 | 29.696 | yes |
| blank shop | fs_chg_today | 0 | 0 | yes |
| blank shop | fs_chg_s1 | 67.3 | 67.3 | yes |
| blank shop | fs_chg_s2 | 445.65 | 445.65 | yes |
| blank shop | fs_chg_s3 | 605.04 | 605.04 | yes |
| blank shop | fs_verdict_today | baseline | Today | intended: baseline column now reads Today |
| blank shop | fs_verdict_s1 | BEATS TODAY | (blank) | intended: verdict stays blank until there is a parcel cost (v1 still printed a verdict with no parcel cost) |
| blank shop | fs_verdict_s2 | BEATS TODAY | (blank) | intended: verdict stays blank until there is a parcel cost (v1 still printed a verdict with no parcel cost) |
| blank shop | fs_verdict_s3 | BEATS TODAY | (blank) | intended: verdict stays blank until there is a parcel cost (v1 still printed a verdict with no parcel cost) |

8 cases x 521 outputs: ALL MATCH (398 intended differences, listed above)
