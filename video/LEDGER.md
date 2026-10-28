# Video engine ledger (Phase 0, the Rat check MVP)

Written only by tools/video_ledger.py (blueprint: Publishing operations). The lock keeps one run at a time; every row
names the state it replaces; "posting" is written before a post and "published" with its link after it. Fingerprints
bind Todd's "post" to the exact spec, MP4 and caption he saw. Touches are his words with their times (the MVP's
effort test: at most one per video after setup). Read: `python3 tools/video_ledger.py state --video <id>`.

## Lock
lock: none

## Rows
{"area": 46, "at": "2026-10-27T22:28:05-05:00", "captionSha256": "0000000000000000000000000000000000000000000000000000000000000000", "mp4Sha256": "0000000000000000000000000000000000000000000000000000000000000000", "note": "golden render: reference for the send test and Todd's voice pick", "postUrl": null, "prev": null, "round": 0, "run": "build-chat-1027", "schema": "pnf.video.ledger_row.v1", "specSha256": "0000000000000000000000000000000000000000000000000000000000000000", "state": "planned", "storyType": "A", "touches": 0, "videoId": "2026-10-27-rats-a"}
{"area": 46, "at": "2026-10-27T22:28:05-05:00", "captionSha256": "0000000000000000000000000000000000000000000000000000000000000000", "mp4Sha256": "0000000000000000000000000000000000000000000000000000000000000000", "postUrl": null, "prev": "planned", "round": 0, "run": "build-chat-1027", "schema": "pnf.video.ledger_row.v1", "specSha256": "0903cf8a749a8e744cbb33b127ef74da3d7fabf06dcf7a101a6c1e2823cc081d", "state": "drafted", "storyType": "A", "touches": 0, "videoId": "2026-10-27-rats-a"}
{"area": 46, "at": "2026-10-27T22:28:05-05:00", "captionSha256": "0000000000000000000000000000000000000000000000000000000000000000", "mp4Sha256": "0000000000000000000000000000000000000000000000000000000000000000", "note": "gates 1 to 3 PASS; hook pick 6 of 6; facts FAIL round 0 (community areas), PASS round 1 and re-check", "postUrl": null, "prev": "drafted", "round": 1, "run": "build-chat-1027", "schema": "pnf.video.ledger_row.v1", "specSha256": "0903cf8a749a8e744cbb33b127ef74da3d7fabf06dcf7a101a6c1e2823cc081d", "state": "gated", "storyType": "A", "touches": 0, "videoId": "2026-10-27-rats-a"}

## Touches

