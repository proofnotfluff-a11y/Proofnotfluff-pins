# Video engine ledger (Phase 0, the Rat check MVP)

Written only by tools/video_ledger.py (blueprint: Publishing operations). The lock keeps one run at a time; every row
names the state it replaces; "posting" is written before a post and "published" with its link after it. Fingerprints
bind Todd's "post" to the exact spec, MP4 and caption he saw. Touches are his words with their times (the MVP's
effort test: at most one per video after setup). Read: `python3 tools/video_ledger.py state --video <id>`.

## Lock
lock: none

## Rows

## Touches

