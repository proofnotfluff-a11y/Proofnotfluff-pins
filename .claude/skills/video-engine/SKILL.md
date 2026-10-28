# video-engine (Phase 0, Rat check MVP; Mon, Wed, Fri)

One job: make one Rat check Reel from this week's rat file, pass every gate, send Todd the preview, post it only after his "post" on it. Spec: blueprint https://claude.ai/artifact/3ssi8yGEKVxiL7JTD87kzS; settings video/config.json. "stop videos" in any chat halts every run (config "stop": true).

## Inputs (Reads)
- video/config.json, video/LEDGER.md, permits/rodents-chicago/weekly.json, video/candidates/, video/prompts/*.md, cmo/CONTENT_PLAYBOOK.md section 9, design/DESIGN_DIRECTOR.md, design/CAROUSEL_STANDARD.md, .claude/skills/social-carousel/SKILL.md step 6a (account checks).

## Process (Executes)
1. Date, preflight `video-engine`. config stop: tell Todd, end. `tools/video_ledger.py lock --run <id>` (exit 3: end). A row in "posting": check the account first, then write "published" or "approved".
2. Metrics: each published video past 24 h, 72 h or 7 d with no file for that checkpoint: read its Insights in Chrome (plays, average watch, shares, saves, profile visits) into video/metrics/<id>-<checkpoint>.json (pathVisits from seo/traffic/weekly.json when it has /rats, else null).
3. Story: `tools/video_story.py candidates`, then `draft --slot <Mon|Wed|Fri> --video-id <date>-rats-<letter>` (a, then b, c for replacements). Stale or malformed file: one line to Todd, end. Ledger: none -> planned -> drafted.
4. Script by video/prompts/scriptwriter.md. `tools/video_gates.py code <spec> --write` (gates 1 to 3 and the number recompute) must PASS.
5. Hook pick: two fresh judges (Agent, opus) on pairwise-hook.md with `video_pairwise.py pairs`; `video_pairwise.py hook` sets spec.hook; gates rerun.
6. Gate 4 facts: fresh agent, facts.md -> video/reviews/<id>/facts.json. Ledger -> gated.
7. Render: write video/jobs/<id>.json (voices: config voice.chosen, or all five while it is null), check_repo, push; ledger -> rendering. Wait for video/renders/<id>/result.json on main (pull every 2 min, up to 40 min). Blocked (no key): tell Todd, end. Fetch branch video-renders; the MP4's sha256 must equal manifest.json.
8. Gate 5: qa.json pass, else one re-render. 5b: fresh agent, render-critic.md on strips/ and transcript.txt; each fault through `video_qa.py recheck`; only a CONFIRMED fault counts. Ledger -> rendered -> qa_passed.
9. Gate 6 send test (pairwise-send.md, reference = the posted video with the most 7-day plays, else the golden render; `video_pairwise.py send`), 7 buyer (buyer.md), 8 design (design.md: no score under 4, average 4.61). Ledger -> reviewed.
10. Preview: SendUserFile the MP4 and sheet.jpg; SendUserMessage the caption in a code block, gate lines as PASS/FAIL with values, and spec, MP4 and caption fingerprints (12 characters). Ledger -> preview_sent. Ask: "post", or a fix note.
11. On Todd's "post" for that preview: `video_ledger.py touch` with his words; -> approved with --spec --mp4 --caption-file; `bound` must PASS. Load the chrome-browser skill. Instagram as proofnotfluff only (switch if not); read the last 5 posts' captions and stop on a match; ledger -> posting; Create, Reel, file_upload the MP4, cover = frame one, paste the caption and check its length, Share to Facebook off, Share. Screenshot; the new /reel/ link; -> published. A fix note: one fix round from the gate it touches.
12. Fix rounds: one per gate, then that gate and every gate after it rerun. A second FAIL: -> failed, the slot's next candidate as a new id, tell Todd one line. No agent overrides a FAIL.

## Outputs (Writes)
- video/specs/, video/jobs/, video/reviews/, video/metrics/, video/candidates/, ledger rows (only through video_ledger.py); check_repo exits 0, push to main, unlock.
- Scoreboard rows (video engine todos, agents/video-engine): counts only. coo/HANDOFF.md one line only when state changes.
- Never: post without every PASS and Todd's "post" on that exact preview, or twice; a standing post rule, Meta or YouTube apps, Buffer, spend, another platform, boosts, replies, profile or setting changes, a password; delete a post (a wrong post goes to Todd); print or log the key.
