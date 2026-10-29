# BREAKING Oct 15, 2026: SSA 2027 wage base, file swaps for live listings

Source: SSA 2027 COLA Fact Sheet, https://www.ssa.gov/news/en/cola/factsheets/2027.html (checked Oct 15, 2026): Social Security wage base $184,500 for 2026, $192,300 for 2027; 2027 COLA 3.6%.

What changed: the "Notes and sources" text in each workbook now gives the 2027 base beside the 2026 base. Nothing else. The maths does not use the wage base. Each new xlsx is the shipped xlsx patched at XML level (tools/patch_xlsx_text.py): only the named cells' text and their row heights differ; every recalculated value matches the shipped file (LibreOffice, 0 error values); every other file in each zip is byte-identical. Gate review (Opus): FAIL round 1 (a full rebuild had drifted styles on #21 and #22), PASS round 2 on the XML patch.
#13 and #22 also gain the federal-rules summary clause already shipped in #23 (Start Here C41 and 1 Your Numbers C48 on #13; 1 Your Numbers C48 on #22).

| id | live listing it replaces the file on | zip | shelf asset (base64) | sha256 | cells |
|---|---|---|---|---|---|
| 13 | https://www.etsy.com/listing/4587962930 | Service-Pricing-Calculator.zip | 6054bad668a43aff7fdb527c042543d9 | cd716c9ba5a81ca9ba825a686f8c68ac0f554f8dc3cb540524d1c4b1b400fb32 | 1 Your Numbers C45, C48; Start Here C41 |
| 14 | https://www.etsy.com/listing/4588330888 | Cleaning-Business-Starter-Kit-v3.zip | b1be942bb8549da852d98c655fd274f5 | a1dc9b73dbd6a28c3f21abb49a449a3e8823569042095ddde5a5a7ec1127f300 | 1 Your Numbers C82 |
| 21 | https://www.etsy.com/listing/4589995309 | Freelance-Income-Tracker.zip | b10424879bd4e0be409bac88f844da36 | 4b2f8a074d208401e0a8919297945223e7d5c440ee9e1fc4a60721ab25a33ff8 | Dashboard C61 |
| 22 | https://www.etsy.com/listing/4590258713 | Pressure-Washing-Pricing-Calculator.zip | 087543bfa719b3ef4cb5534532292171 | 5c3745898bd2e58f6e0605ed4e1378fd99e72db734a64d2cec99fb5b30f693d9 | 1 Your Numbers C45, C48 |
| 23 | https://www.etsy.com/listing/4590270056 | Junk-Removal-Pricing-Calculator.zip | c9f547cd46ed4a0d4f9c339ecc67107e | 04d1466e1f26af919385daab70472cee26998b7b8c1405a6a17c1e26d77d0040 | 1 Your Numbers C45 |

#13 and #14: the new zip replaces the v3 zip in their queued redesign packs (scoreboard legal/13, legal/14). #23: the zip rides its queued flagship pack (legal/23 v3). #21: legal-only file pack (legal/21). #22: its flagship pack is done; the file pack waits in legal/22 breakingFilePack (a requeue would re-run the flagship photo and video edit inside the 14-day window).

Still open on the BREAKING line: #8 (Etsy PDF guide, built by redaction with no source script; its pay stub line says "$184,500 in 2026"), the kdp/8 paperback (source patched here, not rebuilt), and the 2027 Self-Employed Quarterly Tax Planner pre-build (waits for the IRS 2027 brackets).
Free pages self-employment-tax-calculator and employer-cost-calculator: 2027 base added to the callout, FAQ and sources; maths still computes 2026 earnings.
