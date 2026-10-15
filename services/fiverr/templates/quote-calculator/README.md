# Website quote calculator (Gig 3, Premium)

One web page, `index.html`, that a buyer's customers fill in to see a price: the job, the size, how far they are, how often and any extras. It carries the buyer's name, logo and colors and nothing of ours. It runs entirely in the visitor's browser: no outside requests (its Content-Security-Policy blocks them), no cookies, nothing sent anywhere.

Every price is the pricing workbook's own maths. The job lines are `service()` from `docs/assets/pnf-calc.js` (the #13 engine's 3 Quote Builder: floor, add-ons at cost, CEILING to $5, deposit), copied into the page's `<script id="quote-math">`; the minimum charge and the frequency discount follow the cleaning workbook (engines/cleaning-business-kit, 4 Quote Builder, price per visit); an optional helper rate prices each person after the first like the gig 3 workbook. `quote-calculator.test.js` proves all three against the recalculated workbooks to the cent.

Parts 1 to 4 are for the crew. Part 5 is written for the buyer's web person: paste it into the delivery.

## 1. Files

| File | What it is |
|---|---|
| `index.html` | The page. Its config sits inside `<script type="application/json" id="quote-config">`; the template carries `config.sample.json`. |
| `config.sample.json` | Sample Cleaning Co., a made-up business. Every number in it is made up; it came from a sample workbook built with engines/service-pricing (break-even $52.74 an hour, 12 cleaning job types). |
| `quote-calculator.test.js` | The test (part 4). |

## 2. Fill the config from the buyer's numbers

Build and test the buyer's workbook first (services/fiverr/README.md, How an order runs, step 3). The page takes every number from that workbook, so its prices match the buyer's price sheet.

| Config | Where it comes from |
|---|---|
| `business.name` | The buyer's business name. |
| `business.logo` | `file`: their file's name, for the record. `src`: the file as a base64 data URI (command 2). `alt`: leave "" while the name shows beside the logo. |
| `business.notice`, `sample` | Delete both. Only the sample shows a notice band. |
| `colors` | `brand` (price card, buttons, chosen answers), `brandText` (text on brand; leave it out and the page picks white or dark), `accent` and `accentText` (the "Save 10%" tags and the notice band), `background`, `surface` (cards), `text`, `muted`, `border`, optional `focus` (keyboard ring). The test fails anything under 4.5:1 for text or 3:1 for the focus ring. |
| `fontFamily` (optional) | A font list the visitor's device already has, for example `Georgia, serif`. No web fonts: they would be an outside request. |
| `text` | Every word on the page. Placeholders: `{frequency}`, `{people}`, `{hours}`, `{minimum}`, `{deposit}`; `save` takes `{percent}`. Keys left out fall back to plain defaults. |
| `rates.breakEvenPerHour` | '1 Your Numbers' I21, Break-even per paid hour, with all its decimals (command 1). Rounded to cents it can move a price by $5. |
| `rates.marginPercent` | '1 Your Numbers' I37 times 100 (15% is 15). |
| `rates.vehicleCostPerMile`, `rates.driveSpeedMph` | '1 Your Numbers' I38 and I39. |
| `rates.helperCostPerHour` (optional) | Only when the buyer pays helpers by the hour: the gig 3 workbook's "Each helper hour costs" on 1 Your Numbers (helper pay plus the employer cost on top of wages). Leave it out and every person on a crew costs the break-even rate, as in the #13 workbooks. |
| `pricing.roundUpTo` | 5, the workbook's own rounding. Change it only if the workbook changes too. |
| `pricing.minimumCharge` | The buyer's minimum per job, a multiple of `roundUpTo`; 0 for none. |
| `pricing.depositPercent` | '3 Quote Builder' D26 times 100 if the buyer wants the deposit shown; 0 hides it. |
| `services` (optional) | The order services appear in, each with a one-line `note`. Without it the order follows `jobs`. |
| `jobs` | One per row of '2 Trade Presets' the buyer wants on the website (their answer to "which jobs customers should be able to price"): `service` = Trade (C), `size` = Job type (D), `hoursPerPerson` = E, `people` = F, `supplies` = G, `miles` = H, round trip. |
| `zones` (optional) | The buyer's service area in distance bands. `roundTripMiles` = twice a typical one-way distance in the band (the workbook's miles are round trip). `tripFee`: a flat fee billed at cost if the buyer charges one, else 0. Without zones every job is priced at its own preset miles. |
| `frequencies` (optional) | Cleaning only. The first entry is the one-time option and takes no discount. Discounts: the buyer's, or the cleaning workbook's '2 Cleaning Rates' How often table. |
| `extras` (optional) | Billed at cost, like the workbook's "Add-ons billed at cost": the price typed is what the customer pays. For a cleaning buyer, take Price each from the cleaning workbook's '2 Cleaning Rates' Add-ons table. |
| `defaults` (optional) | The answers already chosen when the page opens: `service`, `size`, `zone`, `frequency`, by label. |
| `booking` | `label` and `href`: the buyer's booking or contact page, or a `mailto:` or `sms:` link (the page adds the customer's choices and price to the message). An empty `href` hides the button. The sample's `#request-this-clean` is a placeholder and the buyer test fails it. |

Commands, run from the repo root in the cloud container:

1. The exact break-even rate, from the recalculated copy that `python3 tools/render_xlsx.py buyer.xlsx out/` writes:
```
python3 -c "import openpyxl,sys;print(repr(openpyxl.load_workbook(sys.argv[1],data_only=True)['1 Your Numbers']['I21'].value))" out/recalc.xlsx
```
2. A logo file as a data URI (keep it small: an SVG, or a PNG about 200 px wide and under 100 KB):
```
python3 -c "import base64,mimetypes,sys;p=sys.argv[1];print('data:'+mimetypes.guess_type(p)[0]+';base64,'+base64.b64encode(open(p,'rb').read()).decode())" logo.png
```
3. The buyer's page: this template with their config in place of the sample's:
```
python3 - buyer-config.json services/fiverr/templates/quote-calculator/index.html buyer/index.html <<'EOF'
import json, re, sys
blob = json.dumps(json.load(open(sys.argv[1], encoding="utf-8")), indent=2, ensure_ascii=False)
assert "</" not in blob, "a value contains '</'"
page = open(sys.argv[2], encoding="utf-8").read()
page, n = re.subn(r'(<script type="application/json" id="quote-config">\n).*?(\n</script>)',
                  lambda m: m.group(1) + blob + m.group(2), page, count=1, flags=re.S)
assert n == 1
open(sys.argv[3], "w", encoding="utf-8").write(page)
EOF
```

## 3. The maths, for checking by hand

- Drive hours = round-trip miles / average speed.
- Floor = (hours on site per person x people + drive hours x people) x break-even rate + miles x cost per mile + supplies + extras and trip fee at cost.
- With a helper rate: the first person is the owner at the break-even rate and each other person a helper, so the floor adds (hours on site + drive hours) x (people - 1) x (helper rate - break-even rate). Without one, nothing is added.
- Price = (floor without the at-cost part) / (1 - margin) + the at-cost part, rounded up to the next $5, never under the minimum.
- Per visit = that price less the frequency discount, rounded up to $5 again, never under the minimum.

Worked example from the sample: Standard clean, 3 bedrooms, up to 8 miles (16 round trip): (1.75 x 2 + 0.64 x 2) x $52.7394 + 16 x $0.76 + $10 = $274.25; $274.25 / 0.85 = $322.65, up to $325. The sample workbook's Quote Builder and Price Sheet say $325 for the same job. Weekly at 15% off: $325 x 0.85 = $276.25, up to $280, which is what the cleaning workbook's Quote Builder shows as the price per visit for the same job.

## 4. Test before every delivery

The template itself (the browser checks need Playwright, which the cloud container has):
```
NODE_PATH=$(npm root -g) node services/fiverr/templates/quote-calculator/quote-calculator.test.js
```
A buyer's page, against their recalculated workbook. First write the workbook's answers:
```
python3 - out/recalc.xlsx buyer/expected.json <<'EOF'
import json, sys, openpyxl
wb = openpyxl.load_workbook(sys.argv[1], data_only=True)
tp, ps = wb["2 Trade Presets"], wb["4 Price Sheet"]
jobs = [{"service": tp[f"C{r}"].value, "size": tp[f"D{r}"].value or "", "floor": ps[f"E{r}"].value, "price": ps[f"F{r}"].value}
        for r in range(11, 51) if tp[f"D{r}"].value]
json.dump({"breakEvenPerHour": wb["1 Your Numbers"]["I21"].value, "jobs": jobs}, open(sys.argv[2], "w"), indent=1)
EOF
NODE_PATH=$(npm root -g) node services/fiverr/templates/quote-calculator/quote-calculator.test.js buyer/index.html buyer/expected.json
```
It must end with 0 failed. It checks: no outside request, web address, seller or marketplace name or em dash in the page; the config's own check; color contrast; the break-even rate and every job's floor and price at its preset miles against the workbook; the sample's name, notice and booking placeholder are gone; and in a real browser at 1280 and 390 px, every input has a label, nothing scrolls sideways, the console stays clean and the price shown for every job, distance, frequency and extra equals the maths. Then open the page yourself at both widths, and price two jobs at a farther distance in the workbook's Quote Builder (Round-trip miles override) to see the same numbers.

## 5. Setup steps for the web person (paste into the delivery)

Your price calculator is one file, `index.html`. Rename it if you like, for example `price-calculator.html`. It needs no account, plugin or outside service, and it sends nothing anywhere: customers' choices stay in their browser until they press the booking button.

**Option A, works with every site builder: host the file, then show it in a frame.**
1. Upload the file where your website can serve it: your host's file manager, your site builder's file or media upload if it takes .html files, or any static file host. Open the file's address in a browser to check that the calculator shows.
2. On the page where the calculator belongs, add your builder's HTML or embed block and paste this, with your file's address in place of PASTE-THE-FILE-ADDRESS-HERE:
```html
<iframe id="price-calculator" src="PASTE-THE-FILE-ADDRESS-HERE" title="Price calculator" style="width:100%;height:1150px;border:0" loading="lazy"></iframe>
```
3. Recommended: paste this right after it. It sets the frame to the calculator's exact height, which changes with the screen (about 1,100 px on a computer and 2,100 px on a phone), so nothing scrolls inside the frame:
```html
<script>
window.addEventListener("message", function (e) {
  var f = document.getElementById("price-calculator");
  if (f && e.source === f.contentWindow && e.data && e.data.type === "quote-calculator-height") f.style.height = e.data.height + "px";
});
</script>
```

**Option B: paste the whole file** into an embed block that takes a full page of HTML and runs scripts. The builder shows it in its own frame; set that frame tall enough that nothing is cut off (about 1,150 px on a computer and 2,100 px on a phone).

Where to paste, by builder (menus get renamed; your builder's help pages have the current names):
- WordPress (block editor): a Custom HTML block, with the code from steps 2 and 3. If the media library refuses .html files, upload with your host's file manager.
- Wix: Add, Embed Code, Embed HTML. Choose Code and paste the steps 2 and 3 code, or the whole file (Option B).
- Squarespace: a Code block with the steps 2 and 3 code. Some plans don't run code in blocks; if the block stays empty, check your plan.
- Shopify: Online Store, Pages, open the page, switch the editor to HTML (the <> button) and paste the step 2 code. If Shopify's file upload refuses .html files, host the file elsewhere.
- Webflow: an Embed element with the steps 2 and 3 code.
- GoDaddy Websites + Marketing: an HTML section with the steps 2 and 3 code.

On a phone, when the calculator is opened on its own rather than in a frame, a bar at the bottom keeps the price in view.

To change prices later, replace the file with the new one under the same name and address.

What customers see: the price for their choices, the crew size and time on site, and your notes. They never see your pay, taxes or costs. The rates the prices are built from (break-even per hour, margin, cost per mile) are in the page's code, as with any calculator that runs in the browser.

## 6. Limits worth knowing

- One price per job type, distance band, frequency and set of extras. No square feet box: for homes priced by size, list the sizes as job types, as the sample does.
- The minimum charge and frequency discounts follow the cleaning workbook; the #13 workbooks have neither, so leave them out unless the buyer uses them.
- No booking, payment or calendar: the button opens the buyer's own booking page or a message.
- Don't add web fonts, analytics, maps or images from other sites. The page's security setting blocks them, on purpose, and the test fails them.
