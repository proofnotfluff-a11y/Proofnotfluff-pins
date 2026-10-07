# Conversion standard for every post, pin and video (Todd, Oct 7, 2026: "fixated on the funnel ... content that can be linked back to our actual selling page ... quality top-notch and made for conversion")

Binds the CMO, both promote runs, the shop run's X and LinkedIn posts, and any run that publishes anything. The ledger's safety rules (VERIFY BEFORE POSTING, no invented people, no em dashes, the banned words, the AI line on listings) sit on top of this.

## 1. The funnel, and the one link
Every piece exists to move one person one step: see the product solve their problem, click, land where they can buy or where they can use the free version and then buy. Nothing is published "for reach".

The hub, https://proofnotfluff-a11y.github.io/Proofnotfluff-pins/go/, is the single bio link on every platform (Instagram, TikTok, YouTube channel, Pinterest profile, X, LinkedIn). It leads with the free calculators, then the shop, then every product by audience. Short links for captions and descriptions: `/go/<product id>/` (Etsy listing through the Share & Save domain, so Etsy credits the click and shows our referrer), `/go/free-<page slug>/` (a free calculator page), `/go/shop/`, and `/go/<gumroad slug>/` for premium products (UTM tagged). The builder regenerates them with tools/make_site.py from site/links.json; the COO keeps links.json in step with the products collection.

Which link each piece carries:
- Pinterest pins: the product's listing on the Share & Save domain (https://proofnotfluff.etsy.com/listing/<id>), or the free page when the slate says the pin sells the free tool. Never the shop page.
- YouTube Short: description line one is the product's short link, line two the matching free page when one exists; the related-video link goes to the product's walkthrough. Links in Short descriptions do not click on phones, so the spoken and captioned CTA says the free calculator's name and "link in the description or in the bio".
- YouTube walkthrough (regular video): description line one is the product's short link; the first line of the video names the free page.
- Instagram Reel and TikTok: "Link in bio" (the hub). Until the TikTok account is a business account, the TikTok caption says "Search ProofNotFluff on Etsy" instead.
- X: the post carries no link; the reply-to-self carries the short link. LinkedIn: the link goes in the first comment, never in the post body. Both end with the hub.
- Email (once Kit exists): every email links one product and one free page.

## 2. What a converting piece looks like (the demo format, tools/make_demo.py)
- Frame one shows the product and the hook. The hook is one true number from the product's own files, in the buyer's words ("A $40 hourly rate pays you about $20"). No question openers, no "did you know".
- The body is the product doing the work: inputs typed, the result revealed, one fix that changes the number. Seven rows or fewer.
- Narration: every "say" line is spoken (tools/voice.py, the brand voice in the ledger PROMO STUDIO line) and captioned, so it works muted and with sound. Lines are short, plain, numbers read naturally. Walkthroughs use the "why" lines.
- The close names the product once and the free page once, then the platform's link path. One CTA, never two.
- Length: Shorts and Reels 15 to 40 seconds; walkthroughs 60 to 180 seconds with chapters in the description; pins one headline, one number, the product drawn, no stock photos.
- Proof over polish: real inputs, real outputs, the Terms line where a claim needs it. Nothing the product cannot show.

## 3. Per-platform cadence (the CMO plans, the runs publish)
- Pinterest: 5 pins a day (3 am, 2 pm), each to a different product or free page; boards by audience; fresh pins beat repins.
- YouTube: 2 Shorts a day plus a voiced walkthrough for every product that has a Short past 100 views; the walkthrough is the search piece ("how to price a pressure washing job"), titled with the phrase people search.
- Instagram and TikTok: the two daily demos, captioned for sound-off.
- X: Tuesday thread and Saturday post (shop run), each a worked example with one number, link in the reply.
- LinkedIn: Monday post and Friday story (shop run) under the brand's alias profile, link in the first comment.
- A premium product takes one of the two daily video slots while it is under 45 days live.

## 4. Measurement and kill rules (clicks, not views)
- A piece is judged on clicks to the hub or the listing, then on orders, never on views alone. Sources: Pinterest outbound clicks; Etsy Stats sources (the hub shows as proofnotfluff-a11y.github.io, Share & Save links as their own line); the site's analytics once Todd adds the GA4 id (site/analytics.json); Gumroad sales rows (platform gumroad in the Sales Log).
- The CMO writes promoStats daily and keeps cmo/HOOKS.md scored by clicks per piece where clicks are recorded, views where they are not. After 20 pieces of a hook pattern, a pattern under the median is retired. After 30 pieces on a platform with zero attributable clicks, that platform drops to one piece a day and the slot goes to the platform that clicks.
- Every slate records, per piece, the link it carried and the number it led with, so the COO can tie clicks back to pieces.

## 5. Things that never ship
Engagement bait, fake urgency, invented customers, AI-generated people or faces, stock b-roll of other people's work, claims about income or results, anything that needs an AI-content label on the platform, and any post whose only link is the shop page.
