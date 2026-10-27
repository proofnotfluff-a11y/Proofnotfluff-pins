# verify (every run that changes docs/; Todd, Oct 27, 2026: "Ensure this is a skill we bake into the PNF system")

One job: check site work the way Todd would, by using it, before anyone says it is done. Kem's rule (Glitch Cat Club, Oct 27): an agent that never looked has not verified. The CLI is `tools/verify_site.py`; the evidence is files, not a claim.

## Inputs (Reads)
- The built docs/ (the change), origin/main's committed docs/ (the before), verify/flows/*.json (what Todd would click).

The five questions, answered for PNF:
1. What does working mean? The page opens (HTTP 200), no script or console error, no failed request on our own site, nothing cut off or scrolling sideways, axe WCAG 2.1 AA 0, and each flow does what a buyer would do.
2. Who uses it, on what? Trade owners on a phone (390 px) and a desktop (1280 px), light and dark. Every check runs at both widths in both schemes.
3. What would Todd click? The flows in verify/flows/*.json (taps, typing, list picks, expected text and counts). A new interactive feature ships with its own flow file in the same commit.
4. What breaks that nobody sees? Dark mode text, a moved button, a member map with no pins. `--before` shoots the same pages at origin/main and diffs every pair pixel by pixel; a DIFF on a page you did not mean to change is a bug until shown otherwise.
5. What goes back? The PASS and FAIL lines, and for any visible change the before and after pair image from data/verify/<stamp>/diff/.

## Process (Executes)
1. Build as usual (`python3 tools/make_site.py`), then `python3 tools/verify_site.py --changed --before --flows`.
2. Any FAIL: open the shot named in the report (Read the PNG), fix the cause, rerun. Never edit verify_site.py, a flow or a threshold to make a FAIL go away; a flow that is wrong is fixed in its own commit with the reason.
3. Every DIFF line: open the pair image and confirm the change is the one intended.
4. Members' apps are encrypted: their flows build a planted page (for example `python3 tools/seat_app.py preview docs/zz-verify-pest/index.html <pw>`), never real rows; docs/zz-* is never committed.
5. Map tiles, analytics and fonts from other hosts do not load in the cloud sandbox: those show as notes, not FAILs. Leaflet is served from npm with its pinned hash.
6. Report in the run's message or log: the summary line (`verify: PASS, 0 failing of N checks`) and the evidence folder; send Todd the pair image when the change is one he will see.

## Outputs (Writes)
- data/verify/<stamp>/ (gitignored): report.md, report.json, after/, before/, diff/, flows/.
- New or fixed flow files under verify/flows/.
- On every push to main touching docs/, the Verify site workflow (.github/workflows/verify-site.yml) runs the same checks on the changed pages and all flows, and fails red if anything fails.
