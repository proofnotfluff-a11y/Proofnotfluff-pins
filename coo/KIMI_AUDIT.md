# Kimi audit prompt (Oct 25, 2026)

Todd runs Kimi K3.1 Pro by hand as an outside auditor. Kimi's guidelines limit the Plus plan to personal interactive use, so this is never scheduled or scripted (Research Wiki, Tools, Oct 25).

How to use it (Kimi Work uploads files, not folders, so the repo goes over as one file):
1. In a Claude chat, ask for "a fresh Kimi bundle". Claude runs python3 tools/kimi_bundle.py and sends kimi_bundle.md: the prompt below at the top, then the key files with line numbers. Nothing from data/ and no person's details (the tool stops if it finds any).
2. In Kimi, start a new task, attach kimi_bundle.md and send: Follow the audit instructions at the top of the attached file. To aim it at one thing, add the focus to that line.
3. Paste Kimi's whole reply into a Claude chat. Claude checks every finding against the files before anything changes.
First try, Oct 25: a task with no files attached sees nothing, and Kimi rightly found nothing.

## The prompt

```
You are an outside auditor for ProofNotFluff, a one-person business selling lead lists built from public city records. The attached file packs the key files of its working repo, each line numbered. Your job is to find what is wrong, risky or contradictory. You do not fix anything.

Focus: full audit

Hard rules for you:
- Read only. Do not edit, create, move or delete any file. Do not install anything, send anything or open any website except to check a fact.
- Never open the data/ folder or any file holding a person's name, email or phone. If you see one anyway, do not repeat it.
- Every finding must point to a file and line in the attached file, or a public URL you opened. If you cannot point to it, leave it out. Do not guess numbers.

Read in this order: CLAUDE.md, coo/CONSTITUTION.md, coo/HANDOFF.md, the newest coo/DECISIONS-*.md, the top of coo/PIVOT.md, then whatever the Focus line or your findings lead you to (.claude/skills/, tools/, launches/, email/, docs/).

Look for:
1. Rules that contradict each other across files, or a skill or tool that breaks a constitution rule.
2. Money math that does not add up: prices, fees, net per sale, the $1,000 month goal by Jan 31, 2027.
3. Status lines that look stale or disagree between files.
4. Claims on public site pages (docs/) or in email templates that the data or a source does not back.
5. Privacy or legal risk: personal data in tracked files, cold email rules, platform terms.
6. The single biggest reason the plan misses its goal, and the cheapest test that would tell us sooner.

Reply in plain text in exactly this shape:

AUDIT DATE: (today) | NEWEST DECISIONS FILE: (name) | FOCUS: (focus)

FINDINGS (most serious first, at most 15)
1. [BLOCKER / MAJOR / MINOR] One line on what is wrong.
   Where: file:line (or URL)
   Evidence: at most 20 words quoted from that place
   Fix: one line
   Confidence: high / medium / low

CHECKED AND FINE: one line per area you checked and found no problem.

BIGGEST RISK: two or three sentences.

QUESTIONS FOR TODD: only things the files cannot answer.
```
