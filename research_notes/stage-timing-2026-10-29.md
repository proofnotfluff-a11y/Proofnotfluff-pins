# How early are our Chicago leads? (stage timing check, Oct 29, 2026)

Asked by Todd's go (Oct 29, 3:56 pm, "Go with your recommendations for everything") after Kimi flagged that "weeks before move-in" was never checked.
Source: Chicago Building Permits ydr8-5enu, 8,461 permits issued since Jan 1, 2021, new construction or renovation, reported cost $500,000 or more.
Tool: tools/stage_timing_probe.py, GitHub Actions runs 40953694825 and 40953833055 (branch claude/project-thread-4bg5nr). Aggregates only.

## Result: the claim does not hold
- "Inspections under way" starts soon after the permit is issued. It means work has started and the job needs a certificate of occupancy (CO), not that it is nearly done.
- The City's row update stamps are a bulk refresh (8,401 of 8,461 rows stamped Oct 26 or 27), so the dataset gives no date for when a CO was issued. Finish timing comes from issue-year cohorts instead.
- New buildings that need a CO, share with the CO issued today, by permit year: 2026 2% (3 of 148), 2025 22% (39 of 176), 2024 64% (101 of 159), 2023 76% (127 of 168), 2022 82% (155 of 190), 2021 78% (128 of 165). So a big new building usually gets its CO one to two years after its permit.
- Renovations that need a CO finish faster: 2026 12% (29 of 249), 2025 55% (179 of 325), 2024 68% (187 of 277).
- Our 574 Chicago "Inspections Under Way" leads: permit age median 246 days, middle half 111 to 430 days, youngest 8 days, oldest 730. Most are months from a CO, not weeks.
- "Partial occupancy approved" (17 leads, median 359 days old) means people already live or work in part of the building. That is late for a final clean, not early.
- About a third of new-construction permits from 2021 to 2023 still show plain "INSPECTIONS" with no CO: closed out without a CO, stalled, or never updated. Age alone cannot tell which.

## What changes
- No page, video or email says "weeks before move-in". Live pages say "near finish" only for partial occupancy, defined on the page; that stays accurate.
- The free page groups big open jobs by months since permit (0 to 6, 6 to 12, 12 to 24, over 24) and area, and says plainly what each stage means.
- Start a weekly snapshot of permit id and milestone (sealed, on the Monday permit run, no new schedule) so stage-to-CO time can be measured directly; first useful read after about 8 weeks.
- Video: bank lesson 22 in video/studio/research/IDEAS.md (end of the trades-first bank); the daily studio makes it in turn.
