# Legal desk: free phone sources for restaurant and license lists (Oct 23, 2026)
A risk-control review written by an AI under legal/README.md. Not legal advice; nothing here is "approved". Tier: Medium.
Fresh reviewer (never opened tools/), web pages read Oct 23, 2026. Scope: move 2 (coo/DECISIONS-2026-10-23.md), a listed
business phone on each row of the members' lists, free sources only, numbers only in sealed or encrypted members' files.

## Sources

### 1. Overture Maps Foundation, places theme (S3 bucket overturemaps-us-west-2, anonymous)
- (a) License: no single license; each upstream source carries its own. Latest release 2026-10-21.0. Meta (the large majority), BrightQuery, Microsoft, PinMeTo, Krick, RenderSEO, DAC, Birdeye, Uberall and OpenTravel Alliance: CDLA Permissive 2.0. Foursquare: Apache 2.0. AllThePlaces: CC0 1.0. Overture's guide says places holds no OpenStreetMap data (ODbL covers the base, buildings, divisions and transportation themes only).
- (b) Commercial use in a sold members' file: yes (CDLA 2.0 section 1.1 lets a recipient use, modify and share; Apache 2.0 and CC0 have no commercial limits).
- (c) Attribution: CDLA 2.0 section 2.1, the agreement text goes with shared data; Apache 2.0 section 4 (a) and (d), the license and the NOTICE attribution text for Foursquare rows; Overture's per-source credit lines. Where: inside every members' bundle (a licenses file plus the per-provider lines), and a data-sources line on the Terms page.
- (d) Share-alike: none (CDLA has none and section 3.1 puts no duty on Results; Apache 2.0 and CC0 have none). We treat the copied phone values as Data, not Results, and ship the license text: the conservative reading.
- (e) Access route: the AWS Registry of Open Data sets no separate terms and asks for a citation line. Overture warns places has duplicates and junk: a quality risk, not a legal one.
- (f) Verdict: USE WITH CONDITIONS. 1 Places theme only. 2 Each row carries a source tag (overture:provider) and the Overture release. 3 Each members' bundle includes the CDLA Permissive 2.0 and Apache 2.0 texts, the Foursquare copyright line and NOTICE text, the per-source lines and the AWS citation line. 4 The Terms page names Overture Maps Foundation as a phone source. 5 A phone only when both name and address match the City record; blank otherwise.

### 2. Foursquare Open Source Places, direct
- Apache 2.0, no share-alike. But every direct route has a problem: the Places Portal needs sign-up and a token (breaks the no-key rule); Hugging Face is gated and its "I agree" lets Foursquare use the entity's name and logo as a partner (not for ProofNotFluff LLC); the source.coop mirror's newest partition is Feb 2025, too old.
- Verdict: DO NOT USE as a separate feed. Foursquare records already reach us inside Overture places under Apache 2.0.

### 3. OpenStreetMap phone tags (Overpass API or a Geofabrik extract)
- ODbL 1.0. A daily, systematic join of OSM phones onto our records is a substantial extract under the OSMF Substantial guideline, the joined file is a Derivative Database, the Collective Database guideline does not cover a mixed phone column, selling to members is Public use, and a CSV of phones is not a Produced Work. So ODbL 4.4 and 4.6 apply (license the result under ODbL and offer members a machine-readable copy), which any member could then republish. Overpass public instances also discourage app backends.
- Verdict: DO NOT USE, not even to check or choose between numbers.

### 4. The business's own website (tel: link or schema.org telephone)
- A bare phone number is an uncopyrightable fact (Feist v. Rural Telephone, 499 U.S. 340, 1991); the site's text, photos and layout stay copyrighted. No attribution or share-alike.
- robots.txt is not access authorization (RFC 9309) but we treat it as binding and re-read it at least every 24 hours. Some site terms ban automated access (enforceability against a visitor who never agreed goes to the attorney). A few dozen sites a day is low volume. Yelp, Google Maps, DoorDash, Grubhub, OpenTable and similar platforms ban automated collection and are not the business's own site.
- Verdict: USE WITH CONDITIONS. 1 The business's own domain only. 2 robots.txt first; skip if our agent or * is disallowed. 3 At most the home page and one contact page per business per 30 days, at least 5 seconds apart, honest User-Agent with a contact URL. 4 No logins, CAPTCHAs, paywalls or blocks bypassed. 5 Skip a site whose visible terms ban automated access. 6 Store only the number, its source URL and the fetch date. 7 Remove a business's phone within 5 business days if it asks.

## Member terms lines (exact wording, for the members' Terms of every list that carries phones)
1. Phone numbers are the number each business lists publicly (from Overture Maps data or the business's own website). We do not verify who answers, and some may be cell phones.
2. You must follow all calling laws, including do-not-call rules and Illinois calling hours, never use an autodialer, prerecorded or AI voice without the consent the law requires, and never say or imply you call for the City.

## For the owner's attorney (no wording change can settle these)
1. TCPA and cell phones: 47 U.S.C. 227(b)(1)(A)(iii) bars autodialed or artificial or prerecorded voice calls to cell numbers without prior express consent, with no business-number exception in the text read; an FCC ruling of Feb 2024 treats AI voice as artificial (not re-read today). We cannot tell which listed numbers are cells without a paid lookup. Is the Terms line enough, or should the file flag that numbers may be wireless?
2. Do-not-call: can a restaurant owner's mixed-use cell count as residential, so members must scrub against the National Do Not Call Registry?
3. Telemarketing Sales Rule: the 2024 amendment ended the full B2B exemption (no misrepresentations on B2B calls). Could the list seller face "assisting and facilitating" exposure (310.3(b)) if a member implies City affiliation or that an inspection requires their service? More pressing now that the list prompts calls right after a failed inspection.
4. Illinois Telephone Solicitations Act (815 ILCS 413): no B2B exclusion in the text read, no solicitation calls 9 pm to 8 am, live-caller disclosures in section 15(b). HB2435 (104th General Assembly) would add autodialer consent with a $500 per violation private right of action; status not shown. The Automatic Telephone Dialers Act (815 ILCS 305) not read today. Confirm current law.
5. CDLA Permissive 2.0: is a joined, sold members' file "sharing Data" (license text needed) or "Results" (no duties)? We assume Data.
6. Website terms: are "no automated access" clauses on a restaurant site enforceable against one fetch of a public phone number? Do site-builder platform terms bind a visitor?
7. Personal data: a sole proprietor's listed cell may be personal information under some state laws. Does adding it change the data-sale posture (any data-broker registration) for the restaurant, license and members' lists?

## Sources read (Oct 23, 2026)
docs.overturemaps.org/attribution/; docs.overturemaps.org/guides/places/; docs.overturemaps.org/blog/tags/releases/; registry.opendata.aws/overture/; overturemaps.org/terms-of-use/; cdla.dev/permissive-2-0/; docs.foursquare.com (access-fsq-os-places, fsq-places-open-source, places-os-data-schema); huggingface.co/datasets/foursquare/fsq-os-places; source.coop/fused/fsq-os-places; Apache 2.0 text (askapache.com mirror); openstreetmap.org/copyright; ODbL 1.0 text (lxr.kde.org mirror); osmfoundation.org Substantial, Collective Database and Produced Work guidelines; dev.overpass-api.de commons page; download.geofabrik.de; law.cornell.edu Feist; datatracker.ietf.org RFC 9309; govinfo.gov 47 U.S.C. 227; huschblackwell.com on the 2024 TSR amendment; law.justia.com 815 ILCS 413 (2010 text); ilga.gov HB2435. Not reachable today, mirrors or substitutes used: opendatacommons.org, apache.org, rfc-editor.org, Cornell 227, Justia Feist, ftc.gov TSR guide, Hunton TSR article, ilga.gov ILCS 413, geofabrik.de download page, the OSM wiki Overpass page.

## Conditions applied (build session, Oct 23, 2026)
- Overture places theme only; OpenStreetMap and direct Foursquare not used (tools/phones.py).
- Name AND address both required: same street number, street and direction, within 300 m of the City's point, and every word of the shorter name in the longer one with at least one of the business's own words (independent check, Oct 23). A looser name-nearby rule is kept only to measure coverage.
- Each row: phoneSource (overture:provider or website), phoneRef (release or site URL), phoneDate. The sealed list carries the attribution lines for the providers used, the two member terms lines and a pointer to legal/licenses/phone-sources.txt (CDLA Permissive 2.0 and Apache 2.0 texts verbatim from SPDX, every per-source line, the AWS citation).
- Website: own domain only (listing, delivery, social and chain domains skipped), robots.txt read fresh every run, home page only, 5 seconds between the two requests, a page whose text bans robots or scraping left alone, one read per site per 30 days (logged in the runner cache, never committed).
- Opt-out: tools/phones.py --optout-add keeps the row and drops the phone, stored as a hash in permits/phone-optout.json.
- Open before the first members' delivery (move 3): Foursquare's NOTICE text copied verbatim into legal/licenses/phone-sources.txt (the page would not load from the build sandbox), and the two member terms lines and the data-sources line added to that delivery's Terms.

legal.status: cleared for the Overture Maps places theme (S3) and the business's own website with the conditions above; Foursquare OS Places direct and OpenStreetMap blocked.
