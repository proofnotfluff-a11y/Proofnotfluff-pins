# growth-research (on request, live session with Todd)

One job: evidence-based growth work in two phases. A: better first emails from what proven cold-email practitioners do today. B: new Chicago niches with tailored lead products. Research and drafts only: nothing is sent, published, listed or bought, and no live template or gate changes without Todd's yes in chat.

## Inputs (Reads)
- .claude/skills/outreach-drafter/templates.md, email/SEND_RULES.md, tools/pnf_rules.py (copy_problems, the Inbox Gate, TRADE_VERTICALS).
- launches/*.md (what exists; chicago-new-business-licenses.md is built and not launched), permits/downstream/README.md, docstrings of tools/*_chicago.py and tools/rest_*.py, .github/workflows/.
- CRM meta/desk (ArtifactData) for send and reply history. Web search and fetch; Agent subagents for parallel research.

## Process (Executes)
A1. Experts: shortlist 6 to 8 practitioners who publish real cold emails, teardowns or reply data from campaigns, current within about two years. Record what each is known for, where they publish, how recent. Prefer shown evidence over course sales.
A2. Examples: 15 to 25 real emails or teardowns, weighted to trigger or public-record emails to small owner-run businesses. For each: URL, context, trigger, structure line by line, the ask, length, reported result and how credible it is. Quote a sentence or two at most, with attribution; explain structure in our words; never copy a full email or paid material.
A3. Patterns and disagreements; which side fits a one-person cleaning owner reading on a phone.
A4. Diagnose our past sends against them; the three changes most likely to earn replies, with evidence.
A5. Two or three variants per vertical and stage, each naming its source principle. `python3 tools/copy_gate.py --templates` must pass with them in a scratch copy of templates.md. A/B plan sized to real volume (about 25 a day per sender): one variable at a time, read replies over two to three weeks, a variant id on every draft.
STOP: show Todd the shortlist, the three changes and the variants; adopt into templates.md only on his yes, ideally before Monday's outreach run.
B1. Map City of Chicago datasets that signal a vendor need soon (licenses, permits by type, building violations, food inspections, liquor, sidewalk cafe, signs, elevator and boiler). Dataset id, cadence, signal fields, business-level only, and what we already pull.
B2. Match signals to buyer trades. Score urgency, monthly volume (counted in Actions, never estimated), reachability of owner-run vendors, fit with our data. Pick 2 or 3, and answer the open licenses or violations question with evidence.
B3. One-page spec per niche: buyer, problem, fields and filters, cadence, free sample versus paid list, price inside $29 to $199 with reasons, the honest timing claim, risks and Legal desk questions.
B4. Proof: one tool and one workflow per niche that pulls a sample and prints counts only, modeled on tools/licenses_chicago.py with a selftest; check_repo, push, run, report real counts.
B5. One email per niche from the Phase A patterns, checked with `python3 -c "import sys; sys.path.insert(0,'tools'); import pnf_rules as R; print(R.copy_problems(SUBJECT, BODY, 'Dana'))"` (an empty list passes). A non-permit signal is not yet in the copy gate: propose the gate extension to Todd, never edit a gate to pass.

## Outputs (Writes)
- A Claude Doc "ProofNotFluff growth research, <date>": Expert shortlist, Real examples (cited), Patterns, Diagnosis, New templates, Niche map, Product specs, Open questions for Todd.
- research_notes/cold-email-<date>.md (sources and patterns, no full copied emails); launches/<niche>.md specs; tools and workflows with selftests; pushed only after check_repo exits 0.
- One short status to Todd at each stop: done, decisions he needs, next step. No person's name or email in the repo, the doc or the scoreboard.
