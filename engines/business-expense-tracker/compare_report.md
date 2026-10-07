# #18 compare report (v1 live file vs v2 v3-design build), Oct 7, 2026

## EXAMPLE workbook (compare_map.json)
| case | output | old | new | match |
|---|---|---|---|---|
| example | sales_year | 4,233 | 4,233 | yes |
| example | sales_jan | 858 | 858 | yes |
| example | sales_feb | 1,855 | 1,855 | yes |
| example | sales_mar | 1,520 | 1,520 | yes |
| example | sales_dec | 0 | 0 | yes |
| example | other_inc_year | 0 | 0 | yes |
| example | refunds_year | 24 | 24 | yes |
| example | refunds_jan | 24 | 24 | yes |
| example | refunds_feb | 0 | 0 | yes |
| example | refunds_mar | 0 | 0 | yes |
| example | refunds_dec | 0 | 0 | yes |
| example | income_after_refunds_year | 4,209 | 4,209 | yes |
| example | income_after_refunds_jan | 834 | 834 | yes |
| example | income_after_refunds_feb | 1,855 | 1,855 | yes |
| example | income_after_refunds_mar | 1,520 | 1,520 | yes |
| example | income_after_refunds_dec | 0 | 0 | yes |
| example | inventory_year | 837.9 | 837.9 | yes |
| example | inventory_jan | 412.6 | 412.6 | yes |
| example | inventory_feb | 188.9 | 188.9 | yes |
| example | inventory_mar | 236.4 | 236.4 | yes |
| example | inventory_dec | 0 | 0 | yes |
| example | exp_line_01_year | 45 | 45 | yes |
| example | exp_line_02_year | 14 | 14 | yes |
| example | exp_line_03_year | 292.41 | 292.41 | yes |
| example | exp_line_04_year | 0 | 0 | yes |
| example | exp_line_05_year | 0 | 0 | yes |
| example | exp_line_06_year | 31 | 31 | yes |
| example | exp_line_07_year | 0 | 0 | yes |
| example | exp_line_08_year | 150 | 150 | yes |
| example | exp_line_09_year | 0 | 0 | yes |
| example | exp_line_10_year | 0 | 0 | yes |
| example | exp_line_11_year | 1,125 | 1,125 | yes |
| example | exp_line_12_year | 0 | 0 | yes |
| example | exp_line_13_year | 96.25 | 96.25 | yes |
| example | exp_line_14_year | 50 | 50 | yes |
| example | exp_line_15_year | 0 | 0 | yes |
| example | exp_line_16_year | 38.5 | 38.5 | yes |
| example | exp_line_17_year | 0 | 0 | yes |
| example | exp_line_18_year | 0 | 0 | yes |
| example | exp_line_19_year | 142.59 | 142.59 | yes |
| example | total_exp_year | 1,984.75 | 1,984.75 | yes |
| example | total_exp_jan | 586.16 | 586.16 | yes |
| example | total_exp_feb | 723 | 723 | yes |
| example | total_exp_mar | 675.59 | 675.59 | yes |
| example | total_exp_dec | 0 | 0 | yes |
| example | profit_year | 1,386.35 | 1,386.35 | yes |
| example | profit_jan | -164.76 | -164.76 | yes |
| example | profit_feb | 943.1 | 943.1 | yes |
| example | profit_mar | 608.01 | 608.01 | yes |
| example | profit_dec | 0 | 0 | yes |
| example | equipment_year | 329 | 329 | yes |
| example | draws_year | 500 | 500 | yes |
| example | transfers_year | 1,200 | 1,200 | yes |
| example | chk_no_category | 0 | 0 | yes |
| example | chk_no_date | 0 | 0 | yes |
| example | chk_not_on_list | 0 | 0 | yes |
| example | chk_outside_year | 0 | 0 | yes |
| example | tile_profit | 1,386.35 | 1,386.35 | yes |
| example | tile_income | 4,209 | 4,209 | yes |
| example | strip_inventory | 837.9 | 837.9 | yes |
| example | strip_expenses | 1,984.75 | 1,984.75 | yes |
| high amounts | sales_year | 1,003,746.99 | 1,003,746.99 | yes |
| high amounts | sales_jan | 1,000,371.99 | 1,000,371.99 | yes |
| high amounts | sales_feb | 1,855 | 1,855 | yes |
| high amounts | sales_mar | 1,520 | 1,520 | yes |
| high amounts | sales_dec | 0 | 0 | yes |
| high amounts | other_inc_year | 0 | 0 | yes |
| high amounts | refunds_year | 5,000 | 5,000 | yes |
| high amounts | refunds_jan | 5,000 | 5,000 | yes |
| high amounts | refunds_feb | 0 | 0 | yes |
| high amounts | refunds_mar | 0 | 0 | yes |
| high amounts | refunds_dec | 0 | 0 | yes |
| high amounts | income_after_refunds_year | 998,746.99 | 998,746.99 | yes |
| high amounts | income_after_refunds_jan | 995,371.99 | 995,371.99 | yes |
| high amounts | income_after_refunds_feb | 1,855 | 1,855 | yes |
| high amounts | income_after_refunds_mar | 1,520 | 1,520 | yes |
| high amounts | income_after_refunds_dec | 0 | 0 | yes |
| high amounts | inventory_year | 250,425.3 | 250,425.3 | yes |
| high amounts | inventory_jan | 250,000 | 250,000 | yes |
| high amounts | inventory_feb | 188.9 | 188.9 | yes |
| high amounts | inventory_mar | 236.4 | 236.4 | yes |
| high amounts | inventory_dec | 0 | 0 | yes |
| high amounts | exp_line_01_year | 45 | 45 | yes |
| high amounts | exp_line_02_year | 14 | 14 | yes |
| high amounts | exp_line_03_year | 292.41 | 292.41 | yes |
| high amounts | exp_line_04_year | 0 | 0 | yes |
| high amounts | exp_line_05_year | 0 | 0 | yes |
| high amounts | exp_line_06_year | 31 | 31 | yes |
| high amounts | exp_line_07_year | 0 | 0 | yes |
| high amounts | exp_line_08_year | 150 | 150 | yes |
| high amounts | exp_line_09_year | 0 | 0 | yes |
| high amounts | exp_line_10_year | 0 | 0 | yes |
| high amounts | exp_line_11_year | 1,125 | 1,125 | yes |
| high amounts | exp_line_12_year | 0 | 0 | yes |
| high amounts | exp_line_13_year | 96.25 | 96.25 | yes |
| high amounts | exp_line_14_year | 50 | 50 | yes |
| high amounts | exp_line_15_year | 0 | 0 | yes |
| high amounts | exp_line_16_year | 38.5 | 38.5 | yes |
| high amounts | exp_line_17_year | 0 | 0 | yes |
| high amounts | exp_line_18_year | 0 | 0 | yes |
| high amounts | exp_line_19_year | 142.59 | 142.59 | yes |
| high amounts | total_exp_year | 1,984.75 | 1,984.75 | yes |
| high amounts | total_exp_jan | 586.16 | 586.16 | yes |
| high amounts | total_exp_feb | 723 | 723 | yes |
| high amounts | total_exp_mar | 675.59 | 675.59 | yes |
| high amounts | total_exp_dec | 0 | 0 | yes |
| high amounts | profit_year | 746,336.94 | 746,336.94 | yes |
| high amounts | profit_jan | 744,785.83 | 744,785.83 | yes |
| high amounts | profit_feb | 943.1 | 943.1 | yes |
| high amounts | profit_mar | 608.01 | 608.01 | yes |
| high amounts | profit_dec | 0 | 0 | yes |
| high amounts | equipment_year | 329 | 329 | yes |
| high amounts | draws_year | 500 | 500 | yes |
| high amounts | transfers_year | 1,200 | 1,200 | yes |
| high amounts | chk_no_category | 0 | 0 | yes |
| high amounts | chk_no_date | 0 | 0 | yes |
| high amounts | chk_not_on_list | 0 | 0 | yes |
| high amounts | chk_outside_year | 0 | 0 | yes |
| high amounts | tile_profit | 746,336.94 | 746,336.94 | yes |
| high amounts | tile_income | 998,746.99 | 998,746.99 | yes |
| high amounts | strip_inventory | 250,425.3 | 250,425.3 | yes |
| high amounts | strip_expenses | 1,984.75 | 1,984.75 | yes |
| low amounts | sales_year | 3,747 | 3,747 | yes |
| low amounts | sales_jan | 372 | 372 | yes |
| low amounts | sales_feb | 1,855 | 1,855 | yes |
| low amounts | sales_mar | 1,520 | 1,520 | yes |
| low amounts | sales_dec | 0 | 0 | yes |
| low amounts | other_inc_year | 0 | 0 | yes |
| low amounts | refunds_year | 0.01 | 0.01 | yes |
| low amounts | refunds_jan | 0.01 | 0.01 | yes |
| low amounts | refunds_feb | 0 | 0 | yes |
| low amounts | refunds_mar | 0 | 0 | yes |
| low amounts | refunds_dec | 0 | 0 | yes |
| low amounts | income_after_refunds_year | 3,746.99 | 3,746.99 | yes |
| low amounts | income_after_refunds_jan | 371.99 | 371.99 | yes |
| low amounts | income_after_refunds_feb | 1,855 | 1,855 | yes |
| low amounts | income_after_refunds_mar | 1,520 | 1,520 | yes |
| low amounts | income_after_refunds_dec | 0 | 0 | yes |
| low amounts | inventory_year | 425.31 | 425.31 | yes |
| low amounts | inventory_jan | 0.01 | 0.01 | yes |
| low amounts | inventory_feb | 188.9 | 188.9 | yes |
| low amounts | inventory_mar | 236.4 | 236.4 | yes |
| low amounts | inventory_dec | 0 | 0 | yes |
| low amounts | exp_line_01_year | 45 | 45 | yes |
| low amounts | exp_line_02_year | 14 | 14 | yes |
| low amounts | exp_line_03_year | 292.41 | 292.41 | yes |
| low amounts | exp_line_04_year | 0 | 0 | yes |
| low amounts | exp_line_05_year | 0 | 0 | yes |
| low amounts | exp_line_06_year | 31 | 31 | yes |
| low amounts | exp_line_07_year | 0 | 0 | yes |
| low amounts | exp_line_08_year | 150 | 150 | yes |
| low amounts | exp_line_09_year | 0 | 0 | yes |
| low amounts | exp_line_10_year | 0 | 0 | yes |
| low amounts | exp_line_11_year | 1,125 | 1,125 | yes |
| low amounts | exp_line_12_year | 0 | 0 | yes |
| low amounts | exp_line_13_year | 96.25 | 96.25 | yes |
| low amounts | exp_line_14_year | 50 | 50 | yes |
| low amounts | exp_line_15_year | 0 | 0 | yes |
| low amounts | exp_line_16_year | 38.5 | 38.5 | yes |
| low amounts | exp_line_17_year | 0 | 0 | yes |
| low amounts | exp_line_18_year | 0 | 0 | yes |
| low amounts | exp_line_19_year | 142.59 | 142.59 | yes |
| low amounts | total_exp_year | 1,984.75 | 1,984.75 | yes |
| low amounts | total_exp_jan | 586.16 | 586.16 | yes |
| low amounts | total_exp_feb | 723 | 723 | yes |
| low amounts | total_exp_mar | 675.59 | 675.59 | yes |
| low amounts | total_exp_dec | 0 | 0 | yes |
| low amounts | profit_year | 1,336.93 | 1,336.93 | yes |
| low amounts | profit_jan | -214.18 | -214.18 | yes |
| low amounts | profit_feb | 943.1 | 943.1 | yes |
| low amounts | profit_mar | 608.01 | 608.01 | yes |
| low amounts | profit_dec | 0 | 0 | yes |
| low amounts | equipment_year | 329 | 329 | yes |
| low amounts | draws_year | 500 | 500 | yes |
| low amounts | transfers_year | 1,200 | 1,200 | yes |
| low amounts | chk_no_category | 0 | 0 | yes |
| low amounts | chk_no_date | 0 | 0 | yes |
| low amounts | chk_not_on_list | 0 | 0 | yes |
| low amounts | chk_outside_year | 0 | 0 | yes |
| low amounts | tile_profit | 1,336.93 | 1,336.93 | yes |
| low amounts | tile_income | 3,746.99 | 3,746.99 | yes |
| low amounts | strip_inventory | 425.31 | 425.31 | yes |
| low amounts | strip_expenses | 1,984.75 | 1,984.75 | yes |
| blank year | sales_year | 0 | 4,233 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | sales_jan | 0 | 858 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | sales_feb | 0 | 1,855 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | sales_mar | 0 | 1,520 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | sales_dec | 0 | 0 | yes |
| blank year | other_inc_year | 0 | 0 | yes |
| blank year | refunds_year | 0 | 24 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | refunds_jan | 0 | 24 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | refunds_feb | 0 | 0 | yes |
| blank year | refunds_mar | 0 | 0 | yes |
| blank year | refunds_dec | 0 | 0 | yes |
| blank year | income_after_refunds_year | 0 | 4,209 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | income_after_refunds_jan | 0 | 834 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | income_after_refunds_feb | 0 | 1,855 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | income_after_refunds_mar | 0 | 1,520 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | income_after_refunds_dec | 0 | 0 | yes |
| blank year | inventory_year | 0 | 837.9 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | inventory_jan | 0 | 412.6 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | inventory_feb | 0 | 188.9 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | inventory_mar | 0 | 236.4 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | inventory_dec | 0 | 0 | yes |
| blank year | exp_line_01_year | 0 | 45 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | exp_line_02_year | 0 | 14 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | exp_line_03_year | 0 | 292.41 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | exp_line_04_year | 0 | 0 | yes |
| blank year | exp_line_05_year | 0 | 0 | yes |
| blank year | exp_line_06_year | 0 | 31 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | exp_line_07_year | 0 | 0 | yes |
| blank year | exp_line_08_year | 0 | 150 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | exp_line_09_year | 0 | 0 | yes |
| blank year | exp_line_10_year | 0 | 0 | yes |
| blank year | exp_line_11_year | 0 | 1,125 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | exp_line_12_year | 0 | 0 | yes |
| blank year | exp_line_13_year | 0 | 96.25 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | exp_line_14_year | 0 | 50 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | exp_line_15_year | 0 | 0 | yes |
| blank year | exp_line_16_year | 0 | 38.5 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | exp_line_17_year | 0 | 0 | yes |
| blank year | exp_line_18_year | 0 | 0 | yes |
| blank year | exp_line_19_year | 0 | 142.59 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | total_exp_year | 0 | 1,984.75 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | total_exp_jan | 0 | 586.16 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | total_exp_feb | 0 | 723 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | total_exp_mar | 0 | 675.59 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | total_exp_dec | 0 | 0 | yes |
| blank year | profit_year | 0 | 1,386.35 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | profit_jan | 0 | -164.76 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | profit_feb | 0 | 943.1 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | profit_mar | 0 | 608.01 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | profit_dec | 0 | 0 | yes |
| blank year | equipment_year | 0 | 329 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | draws_year | 0 | 500 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | transfers_year | 0 | 1,200 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | chk_no_category | 0 | 0 | yes |
| blank year | chk_no_date | 0 | 0 | yes |
| blank year | chk_not_on_list | 0 | 0 | yes |
| blank year | chk_outside_year | 31 | 0 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | tile_profit | 0 | 1,386.35 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | tile_income | 0 | 4,209 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | strip_inventory | 0 | 837.9 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| blank year | strip_expenses | 0 | 1,984.75 | intended: v1's EXAMPLE file shows all zeros when the year cell is cleared (DATE(0,1,1) is year 1900); v2 shows this year when the year cell is blank, the rule v1's blank file already used with =YEAR(TODAY()) |
| another year | sales_year | 0 | 0 | yes |
| another year | sales_jan | 0 | 0 | yes |
| another year | sales_feb | 0 | 0 | yes |
| another year | sales_mar | 0 | 0 | yes |
| another year | sales_dec | 0 | 0 | yes |
| another year | other_inc_year | 0 | 0 | yes |
| another year | refunds_year | 0 | 0 | yes |
| another year | refunds_jan | 0 | 0 | yes |
| another year | refunds_feb | 0 | 0 | yes |
| another year | refunds_mar | 0 | 0 | yes |
| another year | refunds_dec | 0 | 0 | yes |
| another year | income_after_refunds_year | 0 | 0 | yes |
| another year | income_after_refunds_jan | 0 | 0 | yes |
| another year | income_after_refunds_feb | 0 | 0 | yes |
| another year | income_after_refunds_mar | 0 | 0 | yes |
| another year | income_after_refunds_dec | 0 | 0 | yes |
| another year | inventory_year | 0 | 0 | yes |
| another year | inventory_jan | 0 | 0 | yes |
| another year | inventory_feb | 0 | 0 | yes |
| another year | inventory_mar | 0 | 0 | yes |
| another year | inventory_dec | 0 | 0 | yes |
| another year | exp_line_01_year | 0 | 0 | yes |
| another year | exp_line_02_year | 0 | 0 | yes |
| another year | exp_line_03_year | 0 | 0 | yes |
| another year | exp_line_04_year | 0 | 0 | yes |
| another year | exp_line_05_year | 0 | 0 | yes |
| another year | exp_line_06_year | 0 | 0 | yes |
| another year | exp_line_07_year | 0 | 0 | yes |
| another year | exp_line_08_year | 0 | 0 | yes |
| another year | exp_line_09_year | 0 | 0 | yes |
| another year | exp_line_10_year | 0 | 0 | yes |
| another year | exp_line_11_year | 0 | 0 | yes |
| another year | exp_line_12_year | 0 | 0 | yes |
| another year | exp_line_13_year | 0 | 0 | yes |
| another year | exp_line_14_year | 0 | 0 | yes |
| another year | exp_line_15_year | 0 | 0 | yes |
| another year | exp_line_16_year | 0 | 0 | yes |
| another year | exp_line_17_year | 0 | 0 | yes |
| another year | exp_line_18_year | 0 | 0 | yes |
| another year | exp_line_19_year | 0 | 0 | yes |
| another year | total_exp_year | 0 | 0 | yes |
| another year | total_exp_jan | 0 | 0 | yes |
| another year | total_exp_feb | 0 | 0 | yes |
| another year | total_exp_mar | 0 | 0 | yes |
| another year | total_exp_dec | 0 | 0 | yes |
| another year | profit_year | 0 | 0 | yes |
| another year | profit_jan | 0 | 0 | yes |
| another year | profit_feb | 0 | 0 | yes |
| another year | profit_mar | 0 | 0 | yes |
| another year | profit_dec | 0 | 0 | yes |
| another year | equipment_year | 0 | 0 | yes |
| another year | draws_year | 0 | 0 | yes |
| another year | transfers_year | 0 | 0 | yes |
| another year | chk_no_category | 0 | 0 | yes |
| another year | chk_no_date | 0 | 0 | yes |
| another year | chk_not_on_list | 0 | 0 | yes |
| another year | chk_outside_year | 31 | 31 | yes |
| another year | tile_profit | 0 | 0 | yes |
| another year | tile_income | 0 | 0 | yes |
| another year | strip_inventory | 0 | 0 | yes |
| another year | strip_expenses | 0 | 0 | yes |
| new rows Dec and next year | sales_year | 6,333 | 6,333 | yes |
| new rows Dec and next year | sales_jan | 858 | 858 | yes |
| new rows Dec and next year | sales_feb | 1,855 | 1,855 | yes |
| new rows Dec and next year | sales_mar | 1,520 | 1,520 | yes |
| new rows Dec and next year | sales_dec | 2,100 | 2,100 | yes |
| new rows Dec and next year | other_inc_year | 0 | 0 | yes |
| new rows Dec and next year | refunds_year | 24 | 24 | yes |
| new rows Dec and next year | refunds_jan | 24 | 24 | yes |
| new rows Dec and next year | refunds_feb | 0 | 0 | yes |
| new rows Dec and next year | refunds_mar | 0 | 0 | yes |
| new rows Dec and next year | refunds_dec | 0 | 0 | yes |
| new rows Dec and next year | income_after_refunds_year | 6,309 | 6,309 | yes |
| new rows Dec and next year | income_after_refunds_jan | 834 | 834 | yes |
| new rows Dec and next year | income_after_refunds_feb | 1,855 | 1,855 | yes |
| new rows Dec and next year | income_after_refunds_mar | 1,520 | 1,520 | yes |
| new rows Dec and next year | income_after_refunds_dec | 2,100 | 2,100 | yes |
| new rows Dec and next year | inventory_year | 837.9 | 837.9 | yes |
| new rows Dec and next year | inventory_jan | 412.6 | 412.6 | yes |
| new rows Dec and next year | inventory_feb | 188.9 | 188.9 | yes |
| new rows Dec and next year | inventory_mar | 236.4 | 236.4 | yes |
| new rows Dec and next year | inventory_dec | 0 | 0 | yes |
| new rows Dec and next year | exp_line_01_year | 45 | 45 | yes |
| new rows Dec and next year | exp_line_02_year | 14 | 14 | yes |
| new rows Dec and next year | exp_line_03_year | 292.41 | 292.41 | yes |
| new rows Dec and next year | exp_line_04_year | 0 | 0 | yes |
| new rows Dec and next year | exp_line_05_year | 0 | 0 | yes |
| new rows Dec and next year | exp_line_06_year | 31 | 31 | yes |
| new rows Dec and next year | exp_line_07_year | 0 | 0 | yes |
| new rows Dec and next year | exp_line_08_year | 150 | 150 | yes |
| new rows Dec and next year | exp_line_09_year | 0 | 0 | yes |
| new rows Dec and next year | exp_line_10_year | 0 | 0 | yes |
| new rows Dec and next year | exp_line_11_year | 1,125 | 1,125 | yes |
| new rows Dec and next year | exp_line_12_year | 0 | 0 | yes |
| new rows Dec and next year | exp_line_13_year | 96.25 | 96.25 | yes |
| new rows Dec and next year | exp_line_14_year | 50 | 50 | yes |
| new rows Dec and next year | exp_line_15_year | 0 | 0 | yes |
| new rows Dec and next year | exp_line_16_year | 38.5 | 38.5 | yes |
| new rows Dec and next year | exp_line_17_year | 0 | 0 | yes |
| new rows Dec and next year | exp_line_18_year | 0 | 0 | yes |
| new rows Dec and next year | exp_line_19_year | 142.59 | 142.59 | yes |
| new rows Dec and next year | total_exp_year | 1,984.75 | 1,984.75 | yes |
| new rows Dec and next year | total_exp_jan | 586.16 | 586.16 | yes |
| new rows Dec and next year | total_exp_feb | 723 | 723 | yes |
| new rows Dec and next year | total_exp_mar | 675.59 | 675.59 | yes |
| new rows Dec and next year | total_exp_dec | 0 | 0 | yes |
| new rows Dec and next year | profit_year | 3,486.35 | 3,486.35 | yes |
| new rows Dec and next year | profit_jan | -164.76 | -164.76 | yes |
| new rows Dec and next year | profit_feb | 943.1 | 943.1 | yes |
| new rows Dec and next year | profit_mar | 608.01 | 608.01 | yes |
| new rows Dec and next year | profit_dec | 2,100 | 2,100 | yes |
| new rows Dec and next year | equipment_year | 329 | 329 | yes |
| new rows Dec and next year | draws_year | 500 | 500 | yes |
| new rows Dec and next year | transfers_year | 1,200 | 1,200 | yes |
| new rows Dec and next year | chk_no_category | 0 | 0 | yes |
| new rows Dec and next year | chk_no_date | 0 | 0 | yes |
| new rows Dec and next year | chk_not_on_list | 0 | 0 | yes |
| new rows Dec and next year | chk_outside_year | 1 | 1 | yes |
| new rows Dec and next year | tile_profit | 3,486.35 | 3,486.35 | yes |
| new rows Dec and next year | tile_income | 6,309 | 6,309 | yes |
| new rows Dec and next year | strip_inventory | 837.9 | 837.9 | yes |
| new rows Dec and next year | strip_expenses | 1,984.75 | 1,984.75 | yes |
| row missing category and date | sales_year | 3,747 | 3,747 | yes |
| row missing category and date | sales_jan | 372 | 372 | yes |
| row missing category and date | sales_feb | 1,855 | 1,855 | yes |
| row missing category and date | sales_mar | 1,520 | 1,520 | yes |
| row missing category and date | sales_dec | 0 | 0 | yes |
| row missing category and date | other_inc_year | 0 | 0 | yes |
| row missing category and date | refunds_year | 0 | 0 | yes |
| row missing category and date | refunds_jan | 0 | 0 | yes |
| row missing category and date | refunds_feb | 0 | 0 | yes |
| row missing category and date | refunds_mar | 0 | 0 | yes |
| row missing category and date | refunds_dec | 0 | 0 | yes |
| row missing category and date | income_after_refunds_year | 3,747 | 3,747 | yes |
| row missing category and date | income_after_refunds_jan | 372 | 372 | yes |
| row missing category and date | income_after_refunds_feb | 1,855 | 1,855 | yes |
| row missing category and date | income_after_refunds_mar | 1,520 | 1,520 | yes |
| row missing category and date | income_after_refunds_dec | 0 | 0 | yes |
| row missing category and date | inventory_year | 837.9 | 837.9 | yes |
| row missing category and date | inventory_jan | 412.6 | 412.6 | yes |
| row missing category and date | inventory_feb | 188.9 | 188.9 | yes |
| row missing category and date | inventory_mar | 236.4 | 236.4 | yes |
| row missing category and date | inventory_dec | 0 | 0 | yes |
| row missing category and date | exp_line_01_year | 45 | 45 | yes |
| row missing category and date | exp_line_02_year | 14 | 14 | yes |
| row missing category and date | exp_line_03_year | 292.41 | 292.41 | yes |
| row missing category and date | exp_line_04_year | 0 | 0 | yes |
| row missing category and date | exp_line_05_year | 0 | 0 | yes |
| row missing category and date | exp_line_06_year | 31 | 31 | yes |
| row missing category and date | exp_line_07_year | 0 | 0 | yes |
| row missing category and date | exp_line_08_year | 150 | 150 | yes |
| row missing category and date | exp_line_09_year | 0 | 0 | yes |
| row missing category and date | exp_line_10_year | 0 | 0 | yes |
| row missing category and date | exp_line_11_year | 1,125 | 1,125 | yes |
| row missing category and date | exp_line_12_year | 0 | 0 | yes |
| row missing category and date | exp_line_13_year | 96.25 | 96.25 | yes |
| row missing category and date | exp_line_14_year | 50 | 50 | yes |
| row missing category and date | exp_line_15_year | 0 | 0 | yes |
| row missing category and date | exp_line_16_year | 38.5 | 38.5 | yes |
| row missing category and date | exp_line_17_year | 0 | 0 | yes |
| row missing category and date | exp_line_18_year | 0 | 0 | yes |
| row missing category and date | exp_line_19_year | 142.59 | 142.59 | yes |
| row missing category and date | total_exp_year | 1,984.75 | 1,984.75 | yes |
| row missing category and date | total_exp_jan | 586.16 | 586.16 | yes |
| row missing category and date | total_exp_feb | 723 | 723 | yes |
| row missing category and date | total_exp_mar | 675.59 | 675.59 | yes |
| row missing category and date | total_exp_dec | 0 | 0 | yes |
| row missing category and date | profit_year | 924.35 | 924.35 | yes |
| row missing category and date | profit_jan | -626.76 | -626.76 | yes |
| row missing category and date | profit_feb | 943.1 | 943.1 | yes |
| row missing category and date | profit_mar | 608.01 | 608.01 | yes |
| row missing category and date | profit_dec | 0 | 0 | yes |
| row missing category and date | equipment_year | 329 | 329 | yes |
| row missing category and date | draws_year | 500 | 500 | yes |
| row missing category and date | transfers_year | 1,200 | 1,200 | yes |
| row missing category and date | chk_no_category | 1 | 1 | yes |
| row missing category and date | chk_no_date | 1 | 1 | yes |
| row missing category and date | chk_not_on_list | 0 | 0 | yes |
| row missing category and date | chk_outside_year | 0 | 0 | yes |
| row missing category and date | tile_profit | 924.35 | 924.35 | yes |
| row missing category and date | tile_income | 3,747 | 3,747 | yes |
| row missing category and date | strip_inventory | 837.9 | 837.9 | yes |
| row missing category and date | strip_expenses | 1,984.75 | 1,984.75 | yes |
| renamed category | sales_year | 4,233 | 4,233 | yes |
| renamed category | sales_jan | 858 | 858 | yes |
| renamed category | sales_feb | 1,855 | 1,855 | yes |
| renamed category | sales_mar | 1,520 | 1,520 | yes |
| renamed category | sales_dec | 0 | 0 | yes |
| renamed category | other_inc_year | 0 | 0 | yes |
| renamed category | refunds_year | 24 | 24 | yes |
| renamed category | refunds_jan | 24 | 24 | yes |
| renamed category | refunds_feb | 0 | 0 | yes |
| renamed category | refunds_mar | 0 | 0 | yes |
| renamed category | refunds_dec | 0 | 0 | yes |
| renamed category | income_after_refunds_year | 4,209 | 4,209 | yes |
| renamed category | income_after_refunds_jan | 834 | 834 | yes |
| renamed category | income_after_refunds_feb | 1,855 | 1,855 | yes |
| renamed category | income_after_refunds_mar | 1,520 | 1,520 | yes |
| renamed category | income_after_refunds_dec | 0 | 0 | yes |
| renamed category | inventory_year | 837.9 | 837.9 | yes |
| renamed category | inventory_jan | 412.6 | 412.6 | yes |
| renamed category | inventory_feb | 188.9 | 188.9 | yes |
| renamed category | inventory_mar | 236.4 | 236.4 | yes |
| renamed category | inventory_dec | 0 | 0 | yes |
| renamed category | exp_line_01_year | 0 | 0 | yes |
| renamed category | exp_line_02_year | 14 | 14 | yes |
| renamed category | exp_line_03_year | 292.41 | 292.41 | yes |
| renamed category | exp_line_04_year | 0 | 0 | yes |
| renamed category | exp_line_05_year | 0 | 0 | yes |
| renamed category | exp_line_06_year | 31 | 31 | yes |
| renamed category | exp_line_07_year | 0 | 0 | yes |
| renamed category | exp_line_08_year | 150 | 150 | yes |
| renamed category | exp_line_09_year | 0 | 0 | yes |
| renamed category | exp_line_10_year | 0 | 0 | yes |
| renamed category | exp_line_11_year | 1,125 | 1,125 | yes |
| renamed category | exp_line_12_year | 0 | 0 | yes |
| renamed category | exp_line_13_year | 96.25 | 96.25 | yes |
| renamed category | exp_line_14_year | 50 | 50 | yes |
| renamed category | exp_line_15_year | 0 | 0 | yes |
| renamed category | exp_line_16_year | 38.5 | 38.5 | yes |
| renamed category | exp_line_17_year | 0 | 0 | yes |
| renamed category | exp_line_18_year | 0 | 0 | yes |
| renamed category | exp_line_19_year | 142.59 | 142.59 | yes |
| renamed category | total_exp_year | 1,939.75 | 1,939.75 | yes |
| renamed category | total_exp_jan | 586.16 | 586.16 | yes |
| renamed category | total_exp_feb | 678 | 678 | yes |
| renamed category | total_exp_mar | 675.59 | 675.59 | yes |
| renamed category | total_exp_dec | 0 | 0 | yes |
| renamed category | profit_year | 1,431.35 | 1,431.35 | yes |
| renamed category | profit_jan | -164.76 | -164.76 | yes |
| renamed category | profit_feb | 988.1 | 988.1 | yes |
| renamed category | profit_mar | 608.01 | 608.01 | yes |
| renamed category | profit_dec | 0 | 0 | yes |
| renamed category | equipment_year | 329 | 329 | yes |
| renamed category | draws_year | 500 | 500 | yes |
| renamed category | transfers_year | 1,200 | 1,200 | yes |
| renamed category | chk_no_category | 0 | 0 | yes |
| renamed category | chk_no_date | 0 | 0 | yes |
| renamed category | chk_not_on_list | 1 | 1 | yes |
| renamed category | chk_outside_year | 0 | 0 | yes |
| renamed category | tile_profit | 1,431.35 | 1,431.35 | yes |
| renamed category | tile_income | 4,209 | 4,209 | yes |
| renamed category | strip_inventory | 837.9 | 837.9 | yes |
| renamed category | strip_expenses | 1,939.75 | 1,939.75 | yes |
| cleared category name | sales_year | 0 | 0 | yes |
| cleared category name | sales_jan | 0 | 0 | yes |
| cleared category name | sales_feb | 0 | 0 | yes |
| cleared category name | sales_mar | 0 | 0 | yes |
| cleared category name | sales_dec | 0 | 0 | yes |
| cleared category name | other_inc_year | 0 | 0 | yes |
| cleared category name | refunds_year | 24 | 24 | yes |
| cleared category name | refunds_jan | 24 | 24 | yes |
| cleared category name | refunds_feb | 0 | 0 | yes |
| cleared category name | refunds_mar | 0 | 0 | yes |
| cleared category name | refunds_dec | 0 | 0 | yes |
| cleared category name | income_after_refunds_year | -24 | -24 | yes |
| cleared category name | income_after_refunds_jan | -24 | -24 | yes |
| cleared category name | income_after_refunds_feb | 0 | 0 | yes |
| cleared category name | income_after_refunds_mar | 0 | 0 | yes |
| cleared category name | income_after_refunds_dec | 0 | 0 | yes |
| cleared category name | inventory_year | 837.9 | 837.9 | yes |
| cleared category name | inventory_jan | 412.6 | 412.6 | yes |
| cleared category name | inventory_feb | 188.9 | 188.9 | yes |
| cleared category name | inventory_mar | 236.4 | 236.4 | yes |
| cleared category name | inventory_dec | 0 | 0 | yes |
| cleared category name | exp_line_01_year | 45 | 45 | yes |
| cleared category name | exp_line_02_year | 14 | 14 | yes |
| cleared category name | exp_line_03_year | 292.41 | 292.41 | yes |
| cleared category name | exp_line_04_year | 0 | 0 | yes |
| cleared category name | exp_line_05_year | 0 | 0 | yes |
| cleared category name | exp_line_06_year | 31 | 31 | yes |
| cleared category name | exp_line_07_year | 0 | 0 | yes |
| cleared category name | exp_line_08_year | 150 | 150 | yes |
| cleared category name | exp_line_09_year | 0 | 0 | yes |
| cleared category name | exp_line_10_year | 0 | 0 | yes |
| cleared category name | exp_line_11_year | 1,125 | 1,125 | yes |
| cleared category name | exp_line_12_year | 0 | 0 | yes |
| cleared category name | exp_line_13_year | 96.25 | 96.25 | yes |
| cleared category name | exp_line_14_year | 50 | 50 | yes |
| cleared category name | exp_line_15_year | 0 | 0 | yes |
| cleared category name | exp_line_16_year | 38.5 | 38.5 | yes |
| cleared category name | exp_line_17_year | 0 | 0 | yes |
| cleared category name | exp_line_18_year | 0 | 0 | yes |
| cleared category name | exp_line_19_year | 142.59 | 142.59 | yes |
| cleared category name | total_exp_year | 1,984.75 | 1,984.75 | yes |
| cleared category name | total_exp_jan | 586.16 | 586.16 | yes |
| cleared category name | total_exp_feb | 723 | 723 | yes |
| cleared category name | total_exp_mar | 675.59 | 675.59 | yes |
| cleared category name | total_exp_dec | 0 | 0 | yes |
| cleared category name | profit_year | -2,846.65 | -2,846.65 | yes |
| cleared category name | profit_jan | -1,022.76 | -1,022.76 | yes |
| cleared category name | profit_feb | -911.9 | -911.9 | yes |
| cleared category name | profit_mar | -911.99 | -911.99 | yes |
| cleared category name | profit_dec | 0 | 0 | yes |
| cleared category name | equipment_year | 329 | 329 | yes |
| cleared category name | draws_year | 500 | 500 | yes |
| cleared category name | transfers_year | 1,200 | 1,200 | yes |
| cleared category name | chk_no_category | 0 | 0 | yes |
| cleared category name | chk_no_date | 0 | 0 | yes |
| cleared category name | chk_not_on_list | 6 | 6 | yes |
| cleared category name | chk_outside_year | 0 | 0 | yes |
| cleared category name | tile_profit | -2,846.65 | -2,846.65 | yes |
| cleared category name | tile_income | -24 | -24 | yes |
| cleared category name | strip_inventory | 837.9 | 837.9 | yes |
| cleared category name | strip_expenses | 1,984.75 | 1,984.75 | yes |
| amount with no category on an empty row | sales_year | 4,233 | 4,233 | yes |
| amount with no category on an empty row | sales_jan | 858 | 858 | yes |
| amount with no category on an empty row | sales_feb | 1,855 | 1,855 | yes |
| amount with no category on an empty row | sales_mar | 1,520 | 1,520 | yes |
| amount with no category on an empty row | sales_dec | 0 | 0 | yes |
| amount with no category on an empty row | other_inc_year | 0 | 0 | yes |
| amount with no category on an empty row | refunds_year | 24 | 24 | yes |
| amount with no category on an empty row | refunds_jan | 24 | 24 | yes |
| amount with no category on an empty row | refunds_feb | 0 | 0 | yes |
| amount with no category on an empty row | refunds_mar | 0 | 0 | yes |
| amount with no category on an empty row | refunds_dec | 0 | 0 | yes |
| amount with no category on an empty row | income_after_refunds_year | 4,209 | 4,209 | yes |
| amount with no category on an empty row | income_after_refunds_jan | 834 | 834 | yes |
| amount with no category on an empty row | income_after_refunds_feb | 1,855 | 1,855 | yes |
| amount with no category on an empty row | income_after_refunds_mar | 1,520 | 1,520 | yes |
| amount with no category on an empty row | income_after_refunds_dec | 0 | 0 | yes |
| amount with no category on an empty row | inventory_year | 837.9 | 837.9 | yes |
| amount with no category on an empty row | inventory_jan | 412.6 | 412.6 | yes |
| amount with no category on an empty row | inventory_feb | 188.9 | 188.9 | yes |
| amount with no category on an empty row | inventory_mar | 236.4 | 236.4 | yes |
| amount with no category on an empty row | inventory_dec | 0 | 0 | yes |
| amount with no category on an empty row | exp_line_01_year | 45 | 45 | yes |
| amount with no category on an empty row | exp_line_02_year | 14 | 14 | yes |
| amount with no category on an empty row | exp_line_03_year | 292.41 | 292.41 | yes |
| amount with no category on an empty row | exp_line_04_year | 0 | 0 | yes |
| amount with no category on an empty row | exp_line_05_year | 0 | 0 | yes |
| amount with no category on an empty row | exp_line_06_year | 31 | 31 | yes |
| amount with no category on an empty row | exp_line_07_year | 0 | 0 | yes |
| amount with no category on an empty row | exp_line_08_year | 150 | 150 | yes |
| amount with no category on an empty row | exp_line_09_year | 0 | 0 | yes |
| amount with no category on an empty row | exp_line_10_year | 0 | 0 | yes |
| amount with no category on an empty row | exp_line_11_year | 1,125 | 1,125 | yes |
| amount with no category on an empty row | exp_line_12_year | 0 | 0 | yes |
| amount with no category on an empty row | exp_line_13_year | 96.25 | 96.25 | yes |
| amount with no category on an empty row | exp_line_14_year | 50 | 50 | yes |
| amount with no category on an empty row | exp_line_15_year | 0 | 0 | yes |
| amount with no category on an empty row | exp_line_16_year | 38.5 | 38.5 | yes |
| amount with no category on an empty row | exp_line_17_year | 0 | 0 | yes |
| amount with no category on an empty row | exp_line_18_year | 0 | 0 | yes |
| amount with no category on an empty row | exp_line_19_year | 142.59 | 142.59 | yes |
| amount with no category on an empty row | total_exp_year | 1,984.75 | 1,984.75 | yes |
| amount with no category on an empty row | total_exp_jan | 586.16 | 586.16 | yes |
| amount with no category on an empty row | total_exp_feb | 723 | 723 | yes |
| amount with no category on an empty row | total_exp_mar | 675.59 | 675.59 | yes |
| amount with no category on an empty row | total_exp_dec | 0 | 0 | yes |
| amount with no category on an empty row | profit_year | 1,386.35 | 1,386.35 | yes |
| amount with no category on an empty row | profit_jan | -164.76 | -164.76 | yes |
| amount with no category on an empty row | profit_feb | 943.1 | 943.1 | yes |
| amount with no category on an empty row | profit_mar | 608.01 | 608.01 | yes |
| amount with no category on an empty row | profit_dec | 0 | 0 | yes |
| amount with no category on an empty row | equipment_year | 329 | 329 | yes |
| amount with no category on an empty row | draws_year | 500 | 500 | yes |
| amount with no category on an empty row | transfers_year | 1,200 | 1,200 | yes |
| amount with no category on an empty row | chk_no_category | 1 | 1 | yes |
| amount with no category on an empty row | chk_no_date | 1 | 1 | yes |
| amount with no category on an empty row | chk_not_on_list | 0 | 0 | yes |
| amount with no category on an empty row | chk_outside_year | 0 | 0 | yes |
| amount with no category on an empty row | tile_profit | 1,386.35 | 1,386.35 | yes |
| amount with no category on an empty row | tile_income | 4,209 | 4,209 | yes |
| amount with no category on an empty row | strip_inventory | 837.9 | 837.9 | yes |
| amount with no category on an empty row | strip_expenses | 1,984.75 | 1,984.75 | yes |

10 cases x 61 outputs: ALL MATCH (40 intended differences, listed above)

## Blank workbook (compare_map_blank.json)
| case | output | old | new | match |
|---|---|---|---|---|
| blank file as shipped | sales_year | 0 | 0 | yes |
| blank file as shipped | sales_jan | 0 | 0 | yes |
| blank file as shipped | sales_feb | 0 | 0 | yes |
| blank file as shipped | sales_mar | 0 | 0 | yes |
| blank file as shipped | sales_dec | 0 | 0 | yes |
| blank file as shipped | other_inc_year | 0 | 0 | yes |
| blank file as shipped | refunds_year | 0 | 0 | yes |
| blank file as shipped | refunds_jan | 0 | 0 | yes |
| blank file as shipped | refunds_feb | 0 | 0 | yes |
| blank file as shipped | refunds_mar | 0 | 0 | yes |
| blank file as shipped | refunds_dec | 0 | 0 | yes |
| blank file as shipped | income_after_refunds_year | 0 | 0 | yes |
| blank file as shipped | income_after_refunds_jan | 0 | 0 | yes |
| blank file as shipped | income_after_refunds_feb | 0 | 0 | yes |
| blank file as shipped | income_after_refunds_mar | 0 | 0 | yes |
| blank file as shipped | income_after_refunds_dec | 0 | 0 | yes |
| blank file as shipped | inventory_year | 0 | 0 | yes |
| blank file as shipped | inventory_jan | 0 | 0 | yes |
| blank file as shipped | inventory_feb | 0 | 0 | yes |
| blank file as shipped | inventory_mar | 0 | 0 | yes |
| blank file as shipped | inventory_dec | 0 | 0 | yes |
| blank file as shipped | exp_line_01_year | 0 | 0 | yes |
| blank file as shipped | exp_line_02_year | 0 | 0 | yes |
| blank file as shipped | exp_line_03_year | 0 | 0 | yes |
| blank file as shipped | exp_line_04_year | 0 | 0 | yes |
| blank file as shipped | exp_line_05_year | 0 | 0 | yes |
| blank file as shipped | exp_line_06_year | 0 | 0 | yes |
| blank file as shipped | exp_line_07_year | 0 | 0 | yes |
| blank file as shipped | exp_line_08_year | 0 | 0 | yes |
| blank file as shipped | exp_line_09_year | 0 | 0 | yes |
| blank file as shipped | exp_line_10_year | 0 | 0 | yes |
| blank file as shipped | exp_line_11_year | 0 | 0 | yes |
| blank file as shipped | exp_line_12_year | 0 | 0 | yes |
| blank file as shipped | exp_line_13_year | 0 | 0 | yes |
| blank file as shipped | exp_line_14_year | 0 | 0 | yes |
| blank file as shipped | exp_line_15_year | 0 | 0 | yes |
| blank file as shipped | exp_line_16_year | 0 | 0 | yes |
| blank file as shipped | exp_line_17_year | 0 | 0 | yes |
| blank file as shipped | exp_line_18_year | 0 | 0 | yes |
| blank file as shipped | exp_line_19_year | 0 | 0 | yes |
| blank file as shipped | total_exp_year | 0 | 0 | yes |
| blank file as shipped | total_exp_jan | 0 | 0 | yes |
| blank file as shipped | total_exp_feb | 0 | 0 | yes |
| blank file as shipped | total_exp_mar | 0 | 0 | yes |
| blank file as shipped | total_exp_dec | 0 | 0 | yes |
| blank file as shipped | profit_year | 0 | 0 | yes |
| blank file as shipped | profit_jan | 0 | 0 | yes |
| blank file as shipped | profit_feb | 0 | 0 | yes |
| blank file as shipped | profit_mar | 0 | 0 | yes |
| blank file as shipped | profit_dec | 0 | 0 | yes |
| blank file as shipped | equipment_year | 0 | 0 | yes |
| blank file as shipped | draws_year | 0 | 0 | yes |
| blank file as shipped | transfers_year | 0 | 0 | yes |
| blank file as shipped | chk_no_category | 0 | 0 | yes |
| blank file as shipped | chk_no_date | 0 | 0 | yes |
| blank file as shipped | chk_not_on_list | 0 | 0 | yes |
| blank file as shipped | chk_outside_year | 0 | 0 | yes |
| blank file as shipped | tile_profit | 0 | 0 | yes |
| blank file as shipped | tile_income | 0 | 0 | yes |
| blank file as shipped | strip_inventory | 0 | 0 | yes |
| blank file as shipped | strip_expenses | 0 | 0 | yes |
| blank file, first rows typed | sales_year | 120 | 120 | yes |
| blank file, first rows typed | sales_jan | 120 | 120 | yes |
| blank file, first rows typed | sales_feb | 0 | 0 | yes |
| blank file, first rows typed | sales_mar | 0 | 0 | yes |
| blank file, first rows typed | sales_dec | 0 | 0 | yes |
| blank file, first rows typed | other_inc_year | 0 | 0 | yes |
| blank file, first rows typed | refunds_year | 0 | 0 | yes |
| blank file, first rows typed | refunds_jan | 0 | 0 | yes |
| blank file, first rows typed | refunds_feb | 0 | 0 | yes |
| blank file, first rows typed | refunds_mar | 0 | 0 | yes |
| blank file, first rows typed | refunds_dec | 0 | 0 | yes |
| blank file, first rows typed | income_after_refunds_year | 120 | 120 | yes |
| blank file, first rows typed | income_after_refunds_jan | 120 | 120 | yes |
| blank file, first rows typed | income_after_refunds_feb | 0 | 0 | yes |
| blank file, first rows typed | income_after_refunds_mar | 0 | 0 | yes |
| blank file, first rows typed | income_after_refunds_dec | 0 | 0 | yes |
| blank file, first rows typed | inventory_year | 0 | 0 | yes |
| blank file, first rows typed | inventory_jan | 0 | 0 | yes |
| blank file, first rows typed | inventory_feb | 0 | 0 | yes |
| blank file, first rows typed | inventory_mar | 0 | 0 | yes |
| blank file, first rows typed | inventory_dec | 0 | 0 | yes |
| blank file, first rows typed | exp_line_01_year | 0 | 0 | yes |
| blank file, first rows typed | exp_line_02_year | 0 | 0 | yes |
| blank file, first rows typed | exp_line_03_year | 9.5 | 9.5 | yes |
| blank file, first rows typed | exp_line_04_year | 0 | 0 | yes |
| blank file, first rows typed | exp_line_05_year | 0 | 0 | yes |
| blank file, first rows typed | exp_line_06_year | 0 | 0 | yes |
| blank file, first rows typed | exp_line_07_year | 0 | 0 | yes |
| blank file, first rows typed | exp_line_08_year | 0 | 0 | yes |
| blank file, first rows typed | exp_line_09_year | 0 | 0 | yes |
| blank file, first rows typed | exp_line_10_year | 0 | 0 | yes |
| blank file, first rows typed | exp_line_11_year | 0 | 0 | yes |
| blank file, first rows typed | exp_line_12_year | 0 | 0 | yes |
| blank file, first rows typed | exp_line_13_year | 0 | 0 | yes |
| blank file, first rows typed | exp_line_14_year | 0 | 0 | yes |
| blank file, first rows typed | exp_line_15_year | 0 | 0 | yes |
| blank file, first rows typed | exp_line_16_year | 0 | 0 | yes |
| blank file, first rows typed | exp_line_17_year | 0 | 0 | yes |
| blank file, first rows typed | exp_line_18_year | 0 | 0 | yes |
| blank file, first rows typed | exp_line_19_year | 0 | 0 | yes |
| blank file, first rows typed | total_exp_year | 9.5 | 9.5 | yes |
| blank file, first rows typed | total_exp_jan | 9.5 | 9.5 | yes |
| blank file, first rows typed | total_exp_feb | 0 | 0 | yes |
| blank file, first rows typed | total_exp_mar | 0 | 0 | yes |
| blank file, first rows typed | total_exp_dec | 0 | 0 | yes |
| blank file, first rows typed | profit_year | 110.5 | 110.5 | yes |
| blank file, first rows typed | profit_jan | 110.5 | 110.5 | yes |
| blank file, first rows typed | profit_feb | 0 | 0 | yes |
| blank file, first rows typed | profit_mar | 0 | 0 | yes |
| blank file, first rows typed | profit_dec | 0 | 0 | yes |
| blank file, first rows typed | equipment_year | 0 | 0 | yes |
| blank file, first rows typed | draws_year | 0 | 0 | yes |
| blank file, first rows typed | transfers_year | 0 | 0 | yes |
| blank file, first rows typed | chk_no_category | 1 | 1 | yes |
| blank file, first rows typed | chk_no_date | 1 | 1 | yes |
| blank file, first rows typed | chk_not_on_list | 0 | 0 | yes |
| blank file, first rows typed | chk_outside_year | 0 | 0 | yes |
| blank file, first rows typed | tile_profit | 110.5 | 110.5 | yes |
| blank file, first rows typed | tile_income | 120 | 120 | yes |
| blank file, first rows typed | strip_inventory | 0 | 0 | yes |
| blank file, first rows typed | strip_expenses | 9.5 | 9.5 | yes |
| blank file, last year | sales_year | 0 | 0 | yes |
| blank file, last year | sales_jan | 0 | 0 | yes |
| blank file, last year | sales_feb | 0 | 0 | yes |
| blank file, last year | sales_mar | 0 | 0 | yes |
| blank file, last year | sales_dec | 0 | 0 | yes |
| blank file, last year | other_inc_year | 0 | 0 | yes |
| blank file, last year | refunds_year | 0 | 0 | yes |
| blank file, last year | refunds_jan | 0 | 0 | yes |
| blank file, last year | refunds_feb | 0 | 0 | yes |
| blank file, last year | refunds_mar | 0 | 0 | yes |
| blank file, last year | refunds_dec | 0 | 0 | yes |
| blank file, last year | income_after_refunds_year | 0 | 0 | yes |
| blank file, last year | income_after_refunds_jan | 0 | 0 | yes |
| blank file, last year | income_after_refunds_feb | 0 | 0 | yes |
| blank file, last year | income_after_refunds_mar | 0 | 0 | yes |
| blank file, last year | income_after_refunds_dec | 0 | 0 | yes |
| blank file, last year | inventory_year | 0 | 0 | yes |
| blank file, last year | inventory_jan | 0 | 0 | yes |
| blank file, last year | inventory_feb | 0 | 0 | yes |
| blank file, last year | inventory_mar | 0 | 0 | yes |
| blank file, last year | inventory_dec | 0 | 0 | yes |
| blank file, last year | exp_line_01_year | 0 | 0 | yes |
| blank file, last year | exp_line_02_year | 0 | 0 | yes |
| blank file, last year | exp_line_03_year | 0 | 0 | yes |
| blank file, last year | exp_line_04_year | 0 | 0 | yes |
| blank file, last year | exp_line_05_year | 0 | 0 | yes |
| blank file, last year | exp_line_06_year | 0 | 0 | yes |
| blank file, last year | exp_line_07_year | 0 | 0 | yes |
| blank file, last year | exp_line_08_year | 0 | 0 | yes |
| blank file, last year | exp_line_09_year | 0 | 0 | yes |
| blank file, last year | exp_line_10_year | 0 | 0 | yes |
| blank file, last year | exp_line_11_year | 0 | 0 | yes |
| blank file, last year | exp_line_12_year | 0 | 0 | yes |
| blank file, last year | exp_line_13_year | 30 | 30 | yes |
| blank file, last year | exp_line_14_year | 0 | 0 | yes |
| blank file, last year | exp_line_15_year | 0 | 0 | yes |
| blank file, last year | exp_line_16_year | 0 | 0 | yes |
| blank file, last year | exp_line_17_year | 0 | 0 | yes |
| blank file, last year | exp_line_18_year | 0 | 0 | yes |
| blank file, last year | exp_line_19_year | 0 | 0 | yes |
| blank file, last year | total_exp_year | 30 | 30 | yes |
| blank file, last year | total_exp_jan | 0 | 0 | yes |
| blank file, last year | total_exp_feb | 30 | 30 | yes |
| blank file, last year | total_exp_mar | 0 | 0 | yes |
| blank file, last year | total_exp_dec | 0 | 0 | yes |
| blank file, last year | profit_year | -30 | -30 | yes |
| blank file, last year | profit_jan | 0 | 0 | yes |
| blank file, last year | profit_feb | -30 | -30 | yes |
| blank file, last year | profit_mar | 0 | 0 | yes |
| blank file, last year | profit_dec | 0 | 0 | yes |
| blank file, last year | equipment_year | 0 | 0 | yes |
| blank file, last year | draws_year | 0 | 0 | yes |
| blank file, last year | transfers_year | 0 | 0 | yes |
| blank file, last year | chk_no_category | 0 | 0 | yes |
| blank file, last year | chk_no_date | 0 | 0 | yes |
| blank file, last year | chk_not_on_list | 0 | 0 | yes |
| blank file, last year | chk_outside_year | 0 | 0 | yes |
| blank file, last year | tile_profit | -30 | -30 | yes |
| blank file, last year | tile_income | 0 | 0 | yes |
| blank file, last year | strip_inventory | 0 | 0 | yes |
| blank file, last year | strip_expenses | 30 | 30 | yes |

3 cases x 61 outputs: ALL MATCH
