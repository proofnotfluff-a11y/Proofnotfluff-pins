# Moving the free site to its own domain

Todd approved buying a site domain on Oct 13, 2026 (about $12 a year; he buys it himself, quest buy-domain). Why it matters: today robots.txt and the sitemap sit under /Proofnotfluff-pins/, where crawlers never read them. On a domain of its own they sit at the root, the free pages look like a real site, and the site can move hosts without breaking a link.

Once Todd names the domain in chat, in this order:

1. **GitHub domain check** (Todd, about 3 minutes; prevents takeover, per GitHub Docs "Verifying your custom domain for GitHub Pages"): GitHub, profile Settings, Pages, Add a domain. Enter the domain, copy the TXT record GitHub shows into Cloudflare DNS, press Verify.
2. **DNS in Cloudflare** (Todd, about 5 minutes, or a live session in his browser with his OK). Apex (@): four A records 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153; four AAAA records 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153. www: CNAME to proofnotfluff-a11y.github.io (no repo name). Proxy status "DNS only" so GitHub can issue the certificate. No wildcard records. Source: GitHub Docs, "Managing a custom domain for your GitHub Pages site" (read Oct 13, 2026).
3. **Repo** (crew): commit docs/CNAME holding the bare domain (the site publishes from a branch, so GitHub reads that file). When the Pages settings show the certificate, Todd ticks Enforce HTTPS (it can take up to 24 hours to appear).
4. **Site** (crew): set BASE in tools/make_site.py to https://<domain>/ and rebuild every page (canonical links, sitemap, Open Graph URLs, /go/ redirects); put robots.txt and sitemap.xml at the site root; keep the IndexNow key file at the root and run the IndexNow workflow once.
5. **Links** (crew): first open one old github.io page and one old /go/ link and confirm they land on the new domain (GitHub redirects the old address when a custom domain is set; check it, don't assume it). Then the hub becomes https://<domain>/go/ in cmo/CONVERSION_STANDARD.md, the CMO and promote prompts and the ledger FUNNEL line. Bio links can move at Todd's pace.
6. **Search and analytics** (Todd, quests verify-search-console and adopt-cloudflare-web-analytics): a Search Console Domain property verified through Cloudflare DNS, Bing Webmaster imported from Search Console, and Cloudflare Web Analytics on the same Cloudflare account.

## Status (Oct 15, 2026)
- proofnotfluff.com bought by Todd in Cloudflare; GitHub domain check verified; apex A and AAAA plus www CNAME added as DNS only (steps 1 and 2 done).
- Step 3 and 4 done by the live CMO session: docs/CNAME, BASE and IndexNow HOST set to https://proofnotfluff.com/, every page rebuilt. tools/etsy_oauth.py keeps the github.io callback (it is registered with Etsy); GitHub forwards it, and the OAuth app's redirect is changed only on Todd's word.
- Waiting: certificate, then Todd ticks Enforce HTTPS; step 5 (old-link check, then the hub URL in the standard, prompts and ledger) once proofnotfluff.com serves.
- Oct 17 (COO): HTTPS live; link-check workflow run 39025655246 on GitHub's runner: every old github.io page and /go/ link lands on proofnotfluff.com in one redirect with 200, and https://proofnotfluff.com/go/ serves directly. Step 5: hub now https://proofnotfluff.com/go/ in cmo/CONVERSION_STANDARD.md, agents/cmo.md (repo copy) and the ledger FUNNEL line; the promote prompts' github.io short links keep working through the redirect and move when their stored prompts are next updated.
