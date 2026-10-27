# Launch record: Chicago Public Way Permit Cost Calculator (B6 item 1), ON HOLD Oct 27, 2026

Decided: Todd, Oct 27, 12:17 pm ("Let's do them all", coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md), research_notes/kimi-2026-10-27-r10.md item 6. Todd's rule for this page: build only from the City's own CDOT 2026 Permit Fee Schedule PDF, downloaded in an Action; if the Action cannot get it, stop and tell him, and never use other sites' numbers.

## Status
- Oct 27: .github/workflows/dp_cdot_fees.yml with tools/dp_cdot_fees_pull.py ran twice on GitHub's runner. Run 1 failed installing pdftotext (fixed). Run 2: the download step failed against https://www.chicago.gov/content/dam/city/depts/cdot/permit/2026/CDOT%202026%20Permit%20Fee%20Schedule.pdf; nothing was written.
- Stopped there, as Todd asked. No retries, no other routes. The workflow now runs only by hand (workflow_dispatch), no push trigger and no schedule.
- The page entry in site/pages.json stays draft, and tools/dp_cdot_fees.py is not written, so the build keeps its noindex stub.

## What unblocks it (Todd's call)
- Todd downloads the PDF in his own browser and attaches it in a build chat (or drops it in a connected folder). The chat commits it to site/datapages/dp_cdot_fees/fee-schedule.pdf with its sha256, extracts the text and builds the calculator from that text only.
- The dumpster permits page links to CDOT's PDF until this calculator is live, then switches to the calculator by itself.
