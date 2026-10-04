# Platform rules and conversion measurement for an automated Etsy promo pipeline (as of 2026-10-04)

All pages below were retrieved on 2026-10-04 unless noted. "Primary" means the platform's own help center, legal page, developer docs or newsroom. Anything resting only on a third-party source is labeled UNVERIFIED-PRIMARY.

## YouTube Shorts: linking, Shopping, and altered/synthetic content disclosure

### Takeaway
Shorts still cannot carry a clickable external link. The only clickable link inside the Shorts player is one "related video" pointing to your own channel, so the path to Etsy is two hops: Short, then a long-form video or channel page whose description or header holds the Etsy link. YouTube Shopping is not an option: Etsy is not a supported store platform and Shopping requires YPP. AI disclosure is needed only for realistic synthetic content. Text, slideshows and animated product mockups are exempt.

### Cited Findings
- Links in Shorts comments and descriptions became unclickable on Aug 31, 2023 "to reduce spam." At the same time YouTube added a "related video" link that can point to other videos on your channel (reported Sept 4, 2023). Source: [Search Engine Journal](https://www.searchenginejournal.com/youtube-adds-shorts-links-limits-links-elsewhere/495463)
- Related video rules (primary, undated help page): you can only link videos from your own channel; the video "has to be public or unlisted"; "Viewers will see a clickable link below your channel handle"; it can point to "Videos, Shorts and Live"; "Adding a related video is only available with advanced feature access." Source: [YouTube Help, Add a related video to your Shorts](https://support.google.com/youtube/answer/14075157?hl=en-GB)
- YouTube Shopping store connection supports these platforms: Shopify, Wix, Fourthwall, Spring, Cafe24, SHOPLINE, BASE, Spreadshop, Suzuri, Marpple Shop and TeePublic, plus 60+ named retailers. **Etsy is not listed** (primary, undated). Source: [YouTube Help, Connect your store](https://support.google.com/youtube/answer/12258186?hl=en)
- To feature your own store's products, the channel must be in the YouTube Partner Program, meet the YPP subscriber threshold, not be Made for Kids, and have no active hate speech strikes. Product tagging works in "videos, Shorts, and live streams." The affiliate program is limited to listed countries, US included. Source: [YouTube Help, Get started with Shopping](https://support.google.com/youtube/answer/12257682?hl=en)
- What has to be disclosed: realistic content that is "fully or partially altered or created using AI tools." That covers making real people appear to say or do things they didn't, altering footage of real events or places, generating realistic scenes that never happened, and music as the main focus (primary, undated). Source: [YouTube Help 14328491](https://support.google.com/youtube/answer/14328491)
- Exempt: unrealistic or animated content, plus "production assistance (scripts, thumbnails, outlines)," captions, beauty filters, special effects, and voice cloning of one's own voice. Source: [YouTube Help 14328491](https://support.google.com/youtube/answer/14328491)
- Where the label shows: on the player for photorealistic content, in the expanded description for non-photorealistic content. Per the page, "Disclosing AI content won't limit a video's audience or impact its eligibility to earn money." Channels that consistently don't disclose may get a label applied manually, content removal, or YPP suspension. Source: [YouTube Help 14328491](https://support.google.com/youtube/answer/14328491)
- Since July 15, 2025, YPP policy renamed "repetitious content" to "inauthentic content" to better catch "mass-produced and repetitious" uploads. YouTube's Rene Ritchie called it "a minor update." Source: [BetaNews, 2025-07-10](https://betanews.com/2025/07/10/youtube-is-fighting-ai-slop-with-new-monetization-guidelines/)
- Shorts can run up to 3 minutes for uploads from Oct 15, 2024, and the video must be "square or taller." Source: [PetaPixel, 2024-10-04](https://petapixel.com/2024/10/04/youtube-shorts-expands-video-length-to-three-minutes/)

### Inferences
- Best YouTube link path: point each Short's related video at one evergreen long-form or pinned "shop" video whose first description line is the Etsy link. Also put the Etsy link in the channel header links. Turning on related video requires advanced feature access (usually phone verification or channel history), so the pipeline should check for it before relying on the feature.
- Faceless Shorts that show text overlays, mockups of downloadable templates, or AI voiceover over screen recordings mostly fall under the exemptions. Disclosure is needed only if a Short shows photorealistic AI people or realistic fabricated scenes. A safe rule for the agent is to set the "altered or synthetic" flag whenever a realistic AI human or AI voice impersonating a real person appears.
- The inauthentic-content rule only touches monetization (YPP). This shop is not monetizing, but templated near-duplicate Shorts can still look like spam. Vary hooks and visuals per upload.

### Gaps
- Could not confirm on a primary page whether the related-video link reports click analytics in 2026. SEJ in 2023 said analytics were "coming soon."
- Could not confirm whether pinned comments on Shorts can now hold clickable links. The 2023 change made Shorts comment links unclickable, and no primary page found says otherwise.
- The disclosure help page has no date and doesn't address Shorts specifically.
- YouTube Shopping eligibility for digital products is not stated. It's moot because Etsy isn't a supported platform.

## Instagram Reels: links, comment-to-DM, trial reels, AI labeling, specs, product tagging

### Takeaway
Reel captions don't carry clickable links. The working link surfaces are the bio (up to 5 links), Story link stickers, and comment-to-DM. Comment-to-DM through Meta's Private Replies API allows exactly one DM per comment, sent within 7 days. Trial reels and 100 posts per 24 hours are both supported through the Graph API. Product tagging is not possible for this shop: shopping tags aren't supported via the API, and Meta commerce policy bans downloadable digital goods.

### Cited Findings
- Graph API publishing: "Instagram accounts are limited to 100 API-published posts within a 24-hour moving period." Reels use `media_type=REELS`. **Trial reels are supported via `trial_params` with `graduation_strategy` set to `MANUAL` or `SS_PERFORMANCE`.** "Shopping tags are not supported." Requires a professional account linked to a Page. Source: [Meta for Developers, Content Publishing](https://developers.facebook.com/documentation/instagram-platform/content-publishing)
- Trial reels go to non-followers first. Instagram can auto-share one to followers "if we determine it's performing well based on the views it receives within the first 72 hours," and metrics appear after about 24 hours. Announced Dec 10, 2024. Source: [Instagram Creators blog](https://creators.instagram.com/blog/instagram-trial-reels)
- Private replies (comment-to-DM): "The message must be sent within 7 days of the comment"; "Only one message can be sent to the commenter"; follow-ups "can only be sent if the recipient responds, and must be sent within 24 hours of the response." Works on posts, reels, stories, Live and ad posts. Requires the `instagram_business_manage_comments` / `instagram_manage_comments` permissions. Source: [Meta for Developers, Private Replies](https://developers.facebook.com/docs/instagram-platform/private-replies/)
- ManyChat free plan: "Up to 25 active contacts," ManyChat branding, Essential plan at $14/mo, Business at $69/mo (page last verified Aug 30, 2026). UNVERIFIED-PRIMARY: this is a third-party aggregator and I did not load ManyChat's own pricing page. Older third-party sources cited a 1,000-contact free tier. Source: [Costbench](https://costbench.com/software/ai-chatbot-platforms/manychat/free-plan/)
- Clickable links in Reel captions require a business Meta Verified subscription at Plus or higher, metered "2 a month on Plus, 4 on Premium, 6 on Max," with Plus from $44.99/mo (article updated Jul 21, 2026). UNVERIFIED-PRIMARY. Source: [Inro](https://www.inro.social/blog/meta-verified-clickable-links)
- Bio allows "up to five external links per profile natively, with no follower requirement." The link sticker "is available to all Instagram accounts in 2026." Caption URLs "are not clickable." UNVERIFIED-PRIMARY: third-party, citing Instagram Help Center. Source: [TLinky](https://tlinky.com/link-in-bio-for-instagram/)
- Meta AI labels: introduced as "Made with AI" Apr 5, 2024; renamed "AI info" Jul 1, 2024. Since Sep 12, 2024, "for content that we detect was only modified or edited by AI tools, we are moving the 'AI info' label to the post's menu." Labels come from "industry standard AI image indicators" or from users self-disclosing. Source: [Meta Newsroom](https://about.fb.com/news/2024/04/metas-approach-to-labeling-ai-generated-content-and-manipulated-media/)
- Meta requires labeling of "photorealistic video or realistic-sounding audio that was digitally created or altered" (secondary summary, updated Jun 4, 2026). UNVERIFIED-PRIMARY: I couldn't get the requirement text or penalty language from Meta's Transparency Center, which returned no body. Source: [Everything-PR](https://everything-pr.com/ai-generated-content-disclosure-platform-by-platform-rules)
- Detection uses C2PA metadata, an internal classifier and invisible watermarks. Meta "has not published any evidence that the label itself affects distribution." Third-party. Source: [Lilach Bullock](https://www.lilachbullock.com/why-instagram-ai-info-label/)
- Meta Commerce Policy: "Downloadable digital goods, subscriptions, and digital accounts are prohibited." Quoted by a feed vendor, and the official policy page could not be fetched. Source: [GoDataFeed](https://www.godatafeed.com/disapproval/meta-subscription-or-digital-download-product)

### Inferences
- Set the Zapier/Graph pipeline up so that each Reel ends with "comment WORD for the link" and a private-reply bot sends a per-Reel tracked Etsy URL. This gives per-video click attribution, since each Reel's keyword maps to its own short link. Mind the one-DM-per-comment and 7-day rules.
- On ManyChat's free tier at 25 contacts (if that figure is right), comment-to-DM would hit the cap almost at once. Budget for the Essential tier, or build directly on the Private Replies API.
- Use `trial_params` with `SS_PERFORMANCE` to test hook variants with non-followers before they reach followers. This is very useful for an AI content factory.
- AI-rendered product mockups that are clearly graphic or template images are low risk. AI voiceover that sounds like a real human may fall under the "realistic-sounding audio" disclosure. The agent should turn on the AI label for any photorealistic AI person or human-sounding synthetic voice.
- Instagram Shopping and product tags can't be used for this shop.

### Gaps
- No primary Instagram Help Center confirmation of the 5-link bio limit or link-sticker availability. Both come from third parties.
- Optimal Reel specs (9:16 aspect, 1080x1920, max length via API) were not confirmed on a primary page this session.
- No primary Meta statement on penalties for failing to self-disclose AI content.
- The Meta Verified caption-link feature and its quotas are third-party only.

## TikTok: bio links, TikTok Shop for digital products, AI labeling, US status

### Takeaway
TikTok isn't in the current pipeline, but it is usable. A Business account reportedly gets the bio website link with no follower minimum, while a personal account needs 1,000 followers. TikTok Shop effectively bans digital downloads outside an invite-only Virtual Goods category. Realistic AI content must be labeled. TikTok's US future was settled by the TikTok USDS Joint Venture, announced Jan 23, 2026.

### Cited Findings
- Personal accounts need 1,000+ followers for the Website field. "Business account, any follower count: Website field is available immediately," but Business accounts are limited to the Commercial Music Library (guide updated Jun 1, 2026). UNVERIFIED-PRIMARY: TikTok's own FAQ page [Adding a website link to your profile](https://www.tiktok.com/support/faq_detail?id=7581821550328896012) exists but blocked fetching via robots.txt. Source: [link.boo](https://link.boo/guides/tiktok-website-field-requirements)
- TikTok Shop: "virtual or digital products are prohibited unless approved for sale under the Virtual Goods category," which is invite-only (article Jun 22, 2026). UNVERIFIED-PRIMARY: secondary summary of TikTok Shop's prohibited products policy. Source: [EchoTik](https://www.echotik.live/blog/can-you-sell-digital-products-on-tiktok-shop/)
- TikTok requires creators to "label AI-generated content that contains realistic images, audio or video," using the AI-generated label or "a sticker or caption." An auto-label for detected AI content was announced (Sep 19, 2023). Source: [TikTok Newsroom](https://newsroom.tiktok.com/en-us/new-labels-for-disclosing-ai-generated-content)
- TikTok "may auto-label some content, especially content made with TikTok AI effects or uploaded with Content Credentials" (C2PA). Third-party. Source: [EchoTik 2026](https://www.echotik.live/blog/tiktok-ai-content-labeling-rules-2026/)
- US status: "On January 23, 2026, TikTok announced the establishment of TikTok USDS Joint Venture LLC." Silver Lake, Oracle and MGX hold 15% each, ByteDance 19.9%, with an American-majority board. The app is available in US app stores. Source: [Tom's Guide](https://www.tomsguide.com/computing/online-security/what-will-happen-if-tiktok-is-banned)

### Inferences
- If TikTok is added, open it as a Business account so the Etsy link works on day one. The Commercial Music Library limit doesn't matter for faceless videos with AI voiceover.
- Selling the downloads natively on TikTok Shop is not realistic. TikTok can only send traffic to Etsy.

### Gaps
- The official TikTok support and TikTok Shop policy pages couldn't be fetched (robots.txt), so the follower threshold and digital-goods ban are verified only through secondary sources.
- No primary source on penalties for unlabeled AI content, or on any 2025-26 "see less AI" feed control on TikTok.

## Pinterest: pin formats, rich pins for Etsy, API and spam limits, AI labels, analytics

### Takeaway
Pinterest is the most Etsy-friendly channel: product rich pins work automatically for Etsy URLs. **However, the brief's premise that the account has "Etsy claimed" is likely wrong.** Pinterest discontinued claiming Etsy, Instagram and YouTube accounts in 2022, and its help page says marketplace stores like Etsy can't be claimed. API posting is limited to 300 writes per day on Trial access and 100 per minute per user on Standard. Spam rules penalize repetitive content and deceptive redirects, which is a reason not to use Bitly links on pins.

### Cited Findings
- "You do not need to add any markup if your site is hosted by Etsy, Teachers Pay Teachers, or eBay. New Pins from these sites will have product information on them within 24 hours." Rich pin types: Recipe, Article and Product (primary, undated). Source: [Pinterest Help, Create rich Pins](https://help.pinterest.com/en/business/article/rich-pins)
- "You're unable to claim most social accounts and online stores hosted on marketplaces like Etsy, eBay and Amazon." Source: [Pinterest Help, Claim your website](https://help.pinterest.com/en/business/article/claim-your-website)
- A Pinterest community manager wrote on May 11, 2022: "The claim your account feature is no longer available for Instagram, Etsy or YouTube." Source: [Pinterest Business Community](https://community.pinterest.biz/t/no-option-to-claim-etsy-shop/669?page=2)
- Current pin types per the help page: Image, Video, Rich (Recipe/Article/Product) and Product Pins. "Video Pins automatically play when they appear in your home feed." Idea Pins are not mentioned. Source: [Pinterest Help, Types of Pins](https://help.pinterest.com/en/article/types-of-pins-on-pinterest)
- API rate limits: category `org_write` ("Creating, editing or deleting boards, board sections or Pins") allows 300 requests per day per app on Trial access and 100 requests per minute per user per app on Standard. Source: [Pinterest Developers, Rate limits](https://developers.pinterest.com/docs/reference/rate-limits/)
- Community Guidelines (last updated May 2026): "Don't create or save content that is repetitive, deceptive, or irrelevant in an attempt to make money"; "Don't use automation that hasn't been explicitly approved by Pinterest"; "Links that exhibit excessive or deceptive redirection...may be blocked." Separate GenAI Acceptable Use Guidelines also exist. Source: [Pinterest Community Guidelines](https://policy.pinterest.com/en/community-guidelines)
- Rate-limit blocks can be triggered when you "add or save a lot of Pins from the same website quickly"; "most limits are removed automatically within 24 hours." Source: [Pinterest Help, Rate limit blocks](https://help.pinterest.com/en/article/rate-limit-blocks)
- Gen AI labels: an "AI modified" label is applied based on IPTC metadata and on classifiers that detect AI "even if the content doesn't have obvious markers." Owners can self-disclose and can appeal through support. No effect on distribution is stated. Source: [Pinterest Help, Gen AI labels](https://help.pinterest.com/en/article/gen-ai-labels)
- Users can limit AI pins in their feeds through "Manage GenAI settings," a feed control that rolled out in 2025. Source: [Pinterest Help, Manage GenAI settings](https://help.pinterest.com/en-gb/article/manage-genai-settings); timing per third-party [Zernio](https://zernio.com/blog/pinterest-new-ai-content-filter)
- Analytics metrics: Impressions, Engagements, Saves, Pin clicks, **Outbound clicks** ("actions that lead them to a destination off Pinterest"), and Video views (2s at 50% in view). Filters cover claimed accounts, organic vs paid, device, pin format (image, video, Idea Pin), and a date range up to about 1.5 years plus 48-hour real-time estimates. Source: [Pinterest Help, Analytics](https://help.pinterest.com/en/business/article/pinterest-analytics)
- The API offers per-pin analytics endpoints, including multi-pin analytics and top video pins. Source: [Pinterest Developers, multi-pin analytics](https://developers.pinterest.com/docs/api/v5/multi_pins-analytics/)

### Inferences
- Pin the direct Etsy listing URL so rich product pins sync price and title automatically. Don't use Bitly on Pinterest: redirect chains risk the "deceptive redirection" rule and could cost the rich pin data. Attribute Pinterest per pin through the API's per-pin outbound clicks.
- A Trial-access app at 300 writes per day is plenty for a few pins a day, but it's worth requesting Standard access. Spread pins over the day. Saving many pins to the same domain (etsy.com) in bursts is a named trigger for rate-limit blocks.
- Image pins made with AI tools that embed IPTC/C2PA metadata will probably get the "AI modified" label, and some users filter these out. Product mockups and template previews don't need to be photorealistic AI, so prefer real screenshots of the actual downloads where you can.
- Since the Etsy shop can't be claimed, the "claimed accounts" analytics filter won't separate Etsy-origin saves by other users. Treat the Pinterest analytics view of your own pins as the source of truth.

### Gaps
- Idea Pin status in 2026 is not confirmed. The help page doesn't mention it, but the analytics page still lists an "Idea Pin" format filter.
- No primary Pinterest statement on whether video pins and standard pins differ in distribution or link click-through.
- Contents of the GenAI Acceptable Use Guidelines were not fetched.

## Etsy measurement: Etsy Stats, UTM/GA4, short links, Share & Save, coupon codes

### Takeaway
Etsy Stats groups visits into categories (Social media, Direct & other, Etsy search, and so on) and can show the referring page or domain. Etsy documents no UTM or campaign tracking in Stats. GA4 can be connected but is documented for traffic, not sales. Per-video attribution therefore has to come from your own layer: unique short links or a link-in-bio tool for clicks, Etsy Stats source and domain for visits, and per-channel coupon codes for sales. Share & Save still exists (terms last updated Feb 20, 2024) and refunds 4% of the order on seller-driven sales. Its URLs are per shop, listing or section, not per post, so it can't tell videos apart.

### Cited Findings
- Etsy Stats traffic sources: "Etsy brought" (Etsy search, Etsy app & other Etsy pages, Etsy marketing & SEO) and "You brought" (Direct & other traffic, Social media, Etsy Ads, Offsite Ads). The breakdown "shows the specific page the buyer was on immediately before landing on your shop or listing." Visit data "refreshes a few times per day"; listing views update in real time. The page doesn't mention UTM. Source: [Etsy Help, How to Use Etsy Stats](https://help.etsy.com/hc/en-us/articles/115015774268-How-to-Use-Etsy-Stats-for-Your-Shop)
- Etsy supports Google Analytics with a GA4 Measurement ID (G-XXXXXXXXXX) for "traffic to your website from different traffic sources," with up to 24-hour delay. Sales or conversion tracking and UTM parameters are not mentioned. Source: [Etsy Help, Google Analytics](https://help.etsy.com/hc/en-us/articles/360000337967-How-to-Use-Google-Analytics-for-Your-Etsy-Shop)
- An Etsy community thread titled "Etsy + Google Analytics GA4 + UTM Link Tracking Not Working" exists, but its content couldn't be loaded (login-gated). Source: [Etsy Community](https://community.etsy.com/t5/Technical-Issues/Etsy-Google-Analytics-GA4-UTM-Link-Tracking-Not-Working/td-p/145049655)
- Share & Save: sellers "obtain a refund of four (4) percent of the Qualifying Transaction Total from your transaction fees." The total is item price plus shipping and gift wrap. Link types are a unique shop URL (Shop Manager), unique listing URLs (Listings Manager), and unique shop section URLs (Seller App). The attribution window is 30 days. Links must be shared on "your owned and operated social media pages, websites, blogs, emails," and "URLs may not be shared or linked on the Etsy platforms." Last updated Feb 20, 2024. Source: [Etsy Share & Save Terms](https://www.etsy.com/legal/policy/etsys-share-save-terms-program-terms/1162874007996)
- Etsy fee basics: listing fee $0.20 and transaction fee 6.5% of item price plus shipping and gift wrap. The page shows "Last updated October 5, 2026," a day after the retrieval date, which may be an effective date for an upcoming revision. Source: [Etsy Fees & Payments Policy](https://www.etsy.com/legal/fees/)

### Inferences
- Recommended attribution stack:
  1. One Share & Save listing URL per product, taken from Listings Manager. This gives the 4% fee refund on seller-driven orders and marks those orders as yours.
  2. Wrap that URL in a unique short link per video or post (Bitly, Dub, or the link-in-bio tool's per-link analytics) everywhere except Pinterest. This gives click counts per creative.
  3. On Pinterest, pin the plain or Share & Save Etsy URL directly and use per-pin outbound clicks from the API.
  4. Reconcile daily: clicks per short link against Etsy Stats visits by source (Social media, then the domain breakdown, such as instagram.com, youtube.com, t.co, pinterest.com) against orders.
  5. For sales-level attribution by channel, give each channel its own coupon code (for example PIN10, YT10, IG10), so orders using a code are labeled by channel.
- It's unknown whether Etsy keeps query strings, so UTMs may or may not come through. Test once: add `?utm_source=test` to a Share & Save URL and see whether the Share & Save tracking and the GA4 source both still register. Don't depend on UTMs until this test passes.
- For $5-7 digital products, the 4% Share & Save refund roughly offsets the 6.5% transaction fee by more than half on qualifying orders. That's worth wiring into every link the pipeline posts.

### Gaps
- No primary Etsy statement that Etsy Stats or GA4 reports UTM campaign values. Unverified either way.
- I didn't confirm whether a Share & Save URL keeps working with extra query parameters, or whether it survives a third-party redirect (Bitly). Test before rollout.
- I didn't fetch Etsy's help page on coupon codes and sales (it's a standard Etsy feature, but code limits and reporting weren't verified this session).
- Etsy's rules on promoting your shop off Etsy (house rules on fee avoidance and links) were not fetched this session. No source found says linking to your own Etsy shop from social media is restricted. The Share & Save terms explicitly encourage it.

## Etsy Offsite Ads interplay: do your own social links trigger the fee?

### Takeaway
No. The Offsite Ads fee applies only when a buyer clicked an Etsy-placed offsite ad and then bought within 30 days. Your own social links don't create that click. But if a buyer clicked an Etsy Offsite Ad earlier in the 30 days and later buys through your Share & Save link, the order counts as an Offsite Ads order: no 4% refund, and the 12-15% fee may apply. Shops under $10,000 in trailing 365-day sales can opt out of Offsite Ads.

### Cited Findings
- Fees: 15% for shops that have never hit $10,000 in a 365-day period, 12% for shops that have. "Once you've made $10,000 USD or more in a 365 day period, you'll be required to participate in Offsite Ads from then onwards." "The Offsite Ads fee for any individual order will never exceed $100 USD." "Orders are attributed to Offsite Ads when a buyer clicks on an ad and completes a purchase from your shop within 30 days." Source: [Etsy Help, How Etsy's Offsite Ads Work](https://help.etsy.com/hc/en-us/articles/360000338367-How-Etsy-s-Offsite-Ads-Work)
- Ads run on Google, Facebook, Instagram, Pinterest, Bing, publisher partners and the Google Display Network. Source: [Etsy Help, How Etsy's Offsite Ads Work](https://help.etsy.com/hc/en-us/articles/360000338367-How-Etsy-s-Offsite-Ads-Work)
- Fees policy: a fee applies when the buyer clicks an offsite ad and "places any orders from your shop within 30 days of that click." If an Etsy Ad was the final click, only Etsy Ads fees apply. Source: [Etsy Fees & Payments Policy](https://www.etsy.com/legal/fees/)
- Share & Save exclusion: "if within the thirty (30) day attribution window, after clicking the URL, the buyer later visits and completes the purchase from your shop via an Etsy Offsite Ad, the transaction is not a Qualifying Transaction and you may be charged the Offsite Ads fee." Source: [Etsy Share & Save Terms](https://www.etsy.com/legal/policy/etsys-share-save-terms-program-terms/1162874007996)
- Etsy's 2022 handbook article on Offsite Ads myths doesn't address seller-owned social links. Source: [Etsy Seller Handbook, 2022-08-15](https://www.etsy.com/seller-handbook/article/944446243462)

### Inferences
- While the shop is under $10,000 in trailing 365-day revenue, opting out of Offsite Ads avoids a 15% fee on cheap digital orders and keeps the Share & Save refund clean. Revisit before crossing $10,000, since participation then becomes permanent.
- Etsy's Offsite Ads also run on Pinterest and Instagram, so a buyer who sees both your organic pin and an Etsy promoted pin may be attributed to Etsy's ad. Opting out removes that overlap.

### Gaps
- Etsy doesn't explicitly say that "seller's own organic links never trigger Offsite Ads." That conclusion comes from the click-on-an-ad attribution definition and is consistent with the Share & Save terms.
- I didn't find whether the Offsite Ads help page has a 2026 revision date.

## X and LinkedIn (context for link posts)

### Takeaway
X leadership says link posts are no longer penalized, but independent analysis disputes it. Treat X as a low-reach channel for direct links. No primary data was gathered on LinkedIn link reach or AI labeling.

### Cited Findings
- On Jul 29, 2026, Elon Musk said X hasn't penalized link posts "for over a year," and product head Nikita Bier said "You do not need to put the links in replies anymore." PPC Land's analysis reported that X's recommendation model produced "94% fewer views" for linked posts. Source: [PPC Land](https://ppc.land/x-drops-year-old-link-penalty-musk-tells-zuckerberg-on-platform/)
- X requires disclosure for synthetic media mainly around public figures and elections. LinkedIn is described as "less prescriptive" on AI labeling (secondary, Jun 4, 2026). Source: [Everything-PR](https://everything-pr.com/ai-generated-content-disclosure-platform-by-platform-rules)

### Inferences
- Run a simple A/B on X: link in the main post vs link in a reply, each with its own short link. Use the result instead of trusting either claim.

### Gaps
- No primary X or LinkedIn help-center sources were fetched on link handling, posting limits, or AI labels.
