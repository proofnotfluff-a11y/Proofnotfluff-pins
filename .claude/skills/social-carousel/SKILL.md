# social-carousel (daily 11:40 am Central, Todd's PC; Todd, Oct 25, 2026) RETIRED Oct 29, 2026: replaced by video-studio (Todd, live chat: "We don't need to do these carousels anymore now that we are doing video generation."); scheduled task paused, not deleted

One job: build one on-brand carousel from today's real data, gate it, and post it to Instagram (proofnotfluff) and the Proofnotfluff Facebook Page. Organic only; LinkedIn off. Todd, Oct 25, 3:05 pm: "Post when all checks pass" (coo/DECISIONS-2026-10-25.md). Step 6 runs only if coo/CONSTITUTION.md section 2 carries a standing carousel post rule; until then stop after step 5 and send Todd the slides. A second FAIL, a blocked tool or a doubt stops the run and goes to Todd.

## Inputs (Reads)
- design/CAROUSEL_STANDARD.md, design/DESIGN_DIRECTOR.md, cmo/CONVERSION_STANDARD.md sections 1, 2 and 5, cmo/HOOKS.md, cmo/CAROUSELS.md (past topics, lead numbers, hooks).
- Topics in turn after the last posted line in cmo/CAROUSELS.md (pest, construction, rats, licenses, season, question, then pest): pest = permits/inspections-chicago/daily.json; construction = permits/chicago/sample.json via tools/question_site.py stats("chicago_construction"); rats = permits/rodents-chicago/weekly.json (counts only); licenses = permits/licenses-chicago/sample.json; season = the calculator in season today (cmo/CAROUSEL_TOPICS.md); question = newest page in seo/QUESTIONS.md. Offer facts from site/pages.json only.
- cmo/CAROUSEL_TOPICS.md: the season list and the buyer test for rats and season.
- Never repeat a lead number or hook from the last 14 days. If a topic's data is unchanged since its last carousel, take another true angle from the file (area, cost band, stage, weekday) or the next topic. No fresh angle anywhere: post nothing, tell Todd.

## Process (Executes)
1. Date from bash. Preflight. Write cmo/carousels/<date>.json shaped like cmo/carousels/2026-10-25.json: 7 slides in the tools/make_carousel.py roles, per number its file and key, source lines, captions.instagram (ends "Free sample: link in bio (proofnotfluff.com).") and captions.facebook (ends proofnotfluff.com/go/free-<page slug>/, which must exist in docs/go/), 60 to 120 words, hook first.
2. Facts gate: a fresh Agent (model fable, else opus) recomputes every number from the files and checks copy rules (dashes, tools/legal_scan.py, no business with a failed record). One fix round.
3. Buyer test: a fresh Agent (opus) reads only copy and captions as a small cleaning or pest company owner: trial, free sample, or do it yourself; does any slide teach the do-it-yourself route. PASS: trial or sample, no how-to. One fix round, facts gate rerun on changed lines.
4. Render: `python3 tools/make_carousel.py cmo/carousels/<date>.json --out /home/claude/carousel/<date>`. Exit 1 means fix the copy and render again.
5. Design gate: a fresh Agent (opus) that never saw the build reads slide-N.jpg and sheet.jpg with DESIGN_DIRECTOR.md and CAROUSEL_STANDARD.md, loads `anthropic-skills:impeccable` and `design:accessibility-review`, scores the seven criteria. Pass: none under 4, average 4.61 or more. One fix round (copy, or the tool if 2026-10-25 still renders the same), then a fresh agent scores again.
6. Post only when 2, 3 and 5 PASS. Claude in Chrome on Todd's browser (load the chrome-browser skill; own tabs, closed after).
   a. Instagram: the signed-in account must be proofnotfluff (switch if not; never post as another account). Create, Post, file_upload slide-1 to slide-N in order, crop 4:5, Next, Next, paste captions.instagram, "Share to" Facebook off. Screenshot: account, slide order, caption length equals the json. Share. Record the newest /p/ link.
   b. Facebook: https://www.facebook.com/profile.php?id=61594865921562 acting as the Page. Photo/video, file_upload the same files, check 7 in order (Edit all), paste captions.facebook and check it, Next, Public, Publish now, boost off, Post. Decline Call Now and reel prompts.
   c. Computer or Chrome unreachable, a sign-in or password prompt, or a screen that does not match: stop, tell Todd where.

## Outputs (Writes)
- The json with gates and post links, one cmo/CAROUSELS.md line (date, topic, lead number, scores, links). check_repo exits 0, push to main. JPGs stay out of the repo.
- One SendUserMessage to Todd: posted (links), or stopped (where, scores, sheet.jpg via SendUserFile).
- Never: post without three PASSes or as another account, boost or spend, reply to comments or messages, change a profile or setting, enter a password, Zapier, video tools.
