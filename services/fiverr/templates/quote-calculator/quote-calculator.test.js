// Test for the website quote calculator template. No installs needed; Playwright is used when it is available.
//
//   node quote-calculator.test.js                      the template: index.html and config.sample.json in this folder
//   node quote-calculator.test.js PAGE.html EXPECT.json   a buyer's page against their workbook (README.md, part 4)
//
// The page's own maths block (<script id="quote-math">) is loaded and run against the pricing workbooks' answers,
// recalculated in LibreOffice on Oct 15, 2026 (tools/render_xlsx.py's office helpers), to the cent:
//   engines/service-pricing (#13 general edition, the pressure washing and junk removal editions, and the sample
//   cleaning workbook built from the same engine with made-up numbers), and engines/cleaning-business-kit (#14 price
//   sheet, and its Quote Builder set to the same job for prices per visit).
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const HERE = __dirname;
const args = process.argv.slice(2);
const PAGE = path.resolve(args[0] || path.join(HERE, "index.html"));
const EXPECT = args[1] ? path.resolve(args[1]) : null;
const TEMPLATE_MODE = !args.length;

let fails = 0, passes = 0;
function result(good, name, detail) {
  if (good) passes++; else fails++;
  console.log(`${good ? "ok  " : "FAIL"} ${name}${detail ? ": " + detail : ""}`);
}
function cents(name, got, want) {
  result(Math.abs(got - want) < 0.005, name, `${Number(got).toFixed(2)} (workbook ${Number(want).toFixed(2)})`);
}

// ---------------------------------------------------------------- the page
const html = fs.readFileSync(PAGE, "utf8");
const mathBlock = /<script id="quote-math">([\s\S]*?)<\/script>/.exec(html);
const cfgBlock = /<script type="application\/json" id="quote-config">([\s\S]*?)<\/script>/.exec(html);
if (!mathBlock || !cfgBlock) {
  console.log("FAIL the page has no quote-math or quote-config block");
  process.exit(1);
}
const box = { module: { exports: {} } };
vm.runInNewContext(mathBlock[1], box);
const Q = box.module.exports;
const cfg = JSON.parse(cfgBlock[1]);

// ---------------------------------------------------------------- what a customer could see or load
result(!html.includes(String.fromCharCode(0x2014)), "no em dash in the page");
result(!/https?:\/\//i.test(html), "no web address in the page (nothing loads from elsewhere)");
result(!/(src|href)\s*=\s*["']\s*\/\//i.test(html), "no protocol-relative src or href");
result(!/\bfetch\s*\(|XMLHttpRequest|sendBeacon|WebSocket|EventSource|import\s*\(|<link\b(?! rel="icon" href="data:,">)|<iframe\b|@import|url\(/i.test(html),
  "no fetch, beacon, socket, link (but the empty icon), iframe or CSS url() in the page");
result(/default-src 'none'/.test(html), "a Content-Security-Policy that blocks outside requests");
result(!/proof\s*not\s*fluff|\bpnf\b|etsy|fiverr/i.test(html), "no seller or marketplace name in the page");

// ---------------------------------------------------------------- the config
const problems = Q.check(cfg);
result(problems.length === 0, "the config passes the page's own check", problems.join("; "));
const C = Object.assign({ brand: "#1E6B5C", accent: "#F2C14E", background: "#F6F4EF", surface: "#FFFFFF", text: "#1B2330",
  muted: "#555F6E" }, cfg.colors || {});
const readable = (bg) => Q.contrast("#FFFFFF", bg) >= Q.contrast("#1B2330", bg) ? "#FFFFFF" : "#1B2330";
const brandText = C.brandText || readable(C.brand), accentText = C.accentText || readable(C.accent);
const tint = Q.mix(C.brand, C.surface, 0.1), accentTint = Q.mix(C.accent, C.surface, 0.22);
[["price text on the brand color", brandText, C.brand, 4.5], ["text on the page background", C.text, C.background, 4.5],
 ["text on cards", C.text, C.surface, 4.5], ["muted text on cards", C.muted, C.surface, 4.5],
 ["muted text on a chosen option", C.muted, tint, 4.5], ["text on a chosen option", C.text, tint, 4.5],
 ["tag text on the accent color", accentText, C.accent, 4.5], ["notice text on its band", C.text, accentTint, 4.5],
 ["focus ring against cards", C.focus || C.brand, C.surface, 3]].forEach(([name, fg, bg, min]) => {
  const r = Q.contrast(fg, bg);
  result(r >= min, `contrast, ${name}`, `${r.toFixed(2)}:1 (at least ${min}:1)`);
});

// ---------------------------------------------------------------- engine cases (template mode)
function cfgWith(be, mph, extra) {
  return Object.assign({ business: { name: "Test" }, pricing: { roundUpTo: 5, minimumCharge: 0, depositPercent: 0 },
    rates: { breakEvenPerHour: be, marginPercent: 15, vehicleCostPerMile: 0.76, driveSpeedMph: mph }, jobs: [] }, extra || {});
}
function oneJob(be, mph, job, opts) {
  opts = opts || {};
  const c = cfgWith(be, mph, { jobs: [job] });
  if (opts.extras !== undefined) c.extras = [{ label: "Add-ons at cost", price: opts.extras }];
  if (opts.deposit !== undefined) c.pricing.depositPercent = opts.deposit;
  if (opts.min !== undefined) c.pricing.minimumCharge = opts.min;
  if (opts.freq !== undefined) c.frequencies = [{ label: "One time", discountPercent: 0 }, { label: "Repeat", discountPercent: opts.freq }];
  return Q.price(c, { job: 0, extras: opts.extras !== undefined ? [0] : [], frequency: opts.freq !== undefined ? 1 : undefined });
}
const J = (h, people, supplies, miles) => ({ service: "Job", size: "", hoursPerPerson: h, people: people, supplies: supplies, miles: miles });

if (TEMPLATE_MODE) {
  // #13 Service Pricing Calculator, general edition (break-even 1 Your Numbers I21; quotes from 3 Quote Builder)
  const BE13 = 54.795944779040184;
  let r = oneJob(BE13, 30, J(2.5, 1, 8, 15), { deposit: 25 });
  cents("#13 standard clean, 2 bed: price floor (I32)", r.floor, 183.78783433712053);
  cents("#13 standard clean, 2 bed: quote (I34)", r.price, 220);
  cents("#13 standard clean, 2 bed: deposit at 25% (I35)", r.deposit, 55);
  cents("#13 standard clean, 2 bed: profit in the quote (I36)", r.profit, 36.21216566287947);
  r = oneJob(BE13, 30, J(2.5, 1, 8, 15), { extras: 30, deposit: 25 });
  cents("#13 $30 of add-ons at cost: floor", r.floor, 213.78783433712053);
  cents("#13 $30 of add-ons at cost: quote", r.price, 250);
  cents("#13 $30 of add-ons at cost: deposit", r.deposit, 62.5);
  r = oneJob(BE13, 30, J(2.5, 1, 8, 15), { extras: 12.5 });
  cents("#13 $12.50 of add-ons at cost: quote", r.price, 230);
  cents("#13 $12.50 of add-ons at cost: profit", r.profit, 33.71216566287947);
  r = oneJob(BE13, 30, J(2.5, 1, 8, 33), { deposit: 33 });
  cents("#13 33 round-trip miles: floor", r.floor, 230.34540120454466);
  cents("#13 33 round-trip miles: quote", r.price, 275);
  cents("#13 33 round-trip miles: deposit at 33%", r.deposit, 90.75);
  [["deep clean, 2 bed", J(5, 1, 15, 15), 327.777696284721, 390], ["weekly mow", J(0.75, 1, 3, 10), 69.96227351062686, 85],
   ["spring cleanup, 2 people", J(4, 2, 20, 10), 502.49818808501493, 595], ["wedding, 38 hours", J(38, 1, 60, 40), 2245.7071613089142, 2645],
   ["cut and style, 0 miles", J(1, 1, 6, 0), 60.795944779040184, 75], ["driveway", J(2, 1, 10, 20), 171.3225194107738, 205]]
    .forEach(([name, job, floor, price]) => {
      const x = oneJob(BE13, 30, job);
      cents(`#13 price sheet, ${name}: floor`, x.floor, floor);
      cents(`#13 price sheet, ${name}: price`, x.price, price);
    });

  // Pressure washing edition (#22)
  const BEPW = 64.89096371761227;
  r = oneJob(BEPW, 30, J(1.5, 1, 12, 20), { deposit: 25 });
  cents("PW 2-car driveway: floor (I32)", r.floor, 167.79708805482656);
  cents("PW 2-car driveway: quote (I34)", r.price, 200);
  cents("PW 2-car driveway: deposit (I35)", r.deposit, 50);
  r = oneJob(BEPW, 30, J(3, 1, 45, 40));
  cents("PW 2-story soft wash at 40 miles: floor", r.floor, 356.5941761096531);
  cents("PW 2-story soft wash at 40 miles: quote", r.price, 420);
  r = oneJob(BEPW, 30, J(6, 2, 180, 40));
  cents("PW paver clean, re-sand and seal: floor", r.floor, 1162.1341345249798);
  cents("PW paver clean, re-sand and seal: price", r.price, 1370);
  r = oneJob(BEPW, 30, J(2, 2, 70, 20));
  cents("PW roof soft wash: price", r.price, 510);

  // Junk removal edition (#23)
  const BEJR = 62.363386594368926;
  r = oneJob(BEJR, 30, J(1.5, 2, 75, 30), { deposit: 25 });
  cents("Junk half truck load: floor (I32)", r.floor, 409.6169329718446);
  cents("Junk half truck load: quote (I34)", r.price, 485);
  cents("Junk half truck load: deposit (I35)", r.deposit, 121.25);
  r = oneJob(BEJR, 30, J(0.75, 2, 25, 30), { extras: 25 });
  cents("Junk couch with a $25 fee at cost: floor", r.floor, 291.07185308029125);
  cents("Junk couch with a $25 fee at cost: quote", r.price, 340);
  r = oneJob(BEJR, 30, J(10, 3, 600, 120));
  cents("Junk estate cleanout, 3 people, 120 miles: floor", r.floor, 3310.462236963495);
  cents("Junk estate cleanout: price", r.price, 3895);

  // #14 Cleaning Business Starter Kit, 3 Price Sheet: one cleaner, 90 person-minutes per 1,000 sq ft times the service
  // multiplier, 16 typical miles, $120 minimum; every 2 weeks and weekly take 10% and 15% off the one-time price.
  const BE14 = 46.98321518301125;
  const sq = (sqft, mult, sup) => J(sqft / 1000 * 90 / 60 * mult, 1, sup, 16);
  [[1000, 145, 135, 125, 215, 240], [1500, 185, 170, 160, 285, 325], [2000, 225, 205, 195, 360, 405],
   [2500, 270, 245, 230, 435, 490], [3000, 310, 280, 265, 505, 575], [3500, 350, 315, 300, 580, 655]].forEach((t) => {
    const s = sq(t[0], 1, 8);
    cents(`#14 ${t[0]} sq ft one-time`, oneJob(BE14, 25, s, { min: 120 }).price, t[1]);
    cents(`#14 ${t[0]} sq ft every 2 weeks`, oneJob(BE14, 25, s, { min: 120, freq: 10 }).price, t[2]);
    cents(`#14 ${t[0]} sq ft weekly`, oneJob(BE14, 25, s, { min: 120, freq: 15 }).price, t[3]);
    cents(`#14 ${t[0]} sq ft deep clean`, oneJob(BE14, 25, sq(t[0], 1.75, 15), { min: 120 }).price, t[4]);
    cents(`#14 ${t[0]} sq ft move-out`, oneJob(BE14, 25, sq(t[0], 2, 20), { min: 120 }).price, t[5]);
  });
  const small = oneJob(BE14, 25, sq(300, 1, 8), { min: 120 });
  cents("#14 300 sq ft: the $120 minimum applies", small.price, 120);
  cents("#14 300 sq ft: one-time price is the minimum too (the I42 rule)", small.oneTime, 120);
  result(small.atMinimum === true, "#14 300 sq ft: flagged as at the minimum");
  cents("#14 300 sq ft every 2 weeks: still the minimum", oneJob(BE14, 25, sq(300, 1, 8), { min: 120, freq: 10 }).price, 120);
  cents("#14 300 sq ft move-out: above the minimum", oneJob(BE14, 25, sq(300, 2, 20), { min: 120 }).price, 125);
  result(oneJob(BE14, 25, sq(300, 2, 20), { min: 120 }).atMinimum === false, "#14 300 sq ft move-out: not flagged");

  // The sample cleaning business (engines/service-pricing with made-up numbers): every job on its 4 Price Sheet, at
  // the preset 16 miles, through the sample config itself.
  const sample = JSON.parse(fs.readFileSync(path.join(HERE, "config.sample.json"), "utf8"));
  result(JSON.stringify(sample) === JSON.stringify(cfg), "index.html carries config.sample.json exactly");
  result(/sample/i.test(sample.business.name) && /SAMPLE/.test(sample.business.notice || "") && !!sample.sample,
    "the sample config is marked as a sample");
  const SHEET = [["Standard clean", "1 bedroom", 159.39191505054185, 190], ["Standard clean", "2 bedrooms", 185.7615959313263, 220],
    ["Standard clean", "3 bedrooms", 274.2541492202993, 325], ["Standard clean", "4 bedrooms", 328.9935109818682, 390],
    ["Deep clean", "1 bedroom", 245.50095769289518, 290], ["Deep clean", "2 bedrooms", 358.3631918626526, 425],
    ["Deep clean", "3 bedrooms", 440.472234505006, 520], ["Deep clean", "4 bedrooms", 523.5812771473593, 620],
    ["Move-out clean", "1 bedroom", 274.8706385736796, 325], ["Move-out clean", "2 bedrooms", 416.1025536242215, 490],
    ["Move-out clean", "3 bedrooms", 499.2115962665748, 590], ["Move-out clean", "4 bedrooms", 582.3206389089281, 690]];
  const jobIndex = (service, size) => sample.jobs.findIndex((j) => j.service === service && j.size === size);
  const zone = (label) => sample.zones.findIndex((z) => z.label === label);
  const freq = (label) => sample.frequencies.findIndex((f) => f.label === label);
  const extra = (label) => sample.extras.findIndex((x) => x.label === label);
  result(sample.jobs.length === SHEET.length, "the sample config has the workbook's 12 job types");
  SHEET.forEach(([service, size, floor, price]) => {
    const x = Q.price(sample, { job: jobIndex(service, size) });
    cents(`sample price sheet, ${service}, ${size}: floor`, x.floor, floor);
    cents(`sample price sheet, ${service}, ${size}: price`, x.price, price);
  });
  // The states shown in the gallery, the demo video and the PDF, each recalculated in the workbooks.
  const S = (service, size, z, f, ex) => Q.price(sample, { job: jobIndex(service, size), zone: zone(z), frequency: freq(f),
    extras: (ex || []).map(extra) });
  let x = S("Standard clean", "3 bedrooms", "Up to 8 miles", "One time");
  cents("sample default: floor (3 Quote Builder I32)", x.floor, 274.25414922029927);
  cents("sample default: price (I34)", x.price, 325);
  cents("sample deep clean, 3 bedrooms, up to 8 miles (I34)", S("Deep clean", "3 bedrooms", "Up to 8 miles", "One time").price, 520);
  x = S("Deep clean", "3 bedrooms", "15 to 25 miles", "One time");
  cents("sample deep clean, 3 bedrooms, 50 round-trip miles: floor (I32)", x.floor, 609.7632984964733);
  cents("sample deep clean, 3 bedrooms, 50 round-trip miles: price (I34)", x.price, 720);
  x = S("Deep clean", "3 bedrooms", "8 to 15 miles", "One time", ["Inside oven"]);
  cents("sample deep clean, 30 miles, inside oven at cost: floor (I32)", x.floor, 544.1803196779631);
  cents("sample deep clean, 30 miles, inside oven at cost: price (I34)", x.price, 635);
  // Prices per visit: the cleaning kit's Quote Builder set to the same job (its floor matches the line above to the cent)
  cents("sample deep clean, 3 bedrooms, 50 miles, every 2 weeks (kit I44)", S("Deep clean", "3 bedrooms", "15 to 25 miles", "Every 2 weeks").price, 650);
  cents("sample standard clean, 2 bedrooms, every 2 weeks (kit I44)", S("Standard clean", "2 bedrooms", "Up to 8 miles", "Every 2 weeks").price, 200);
  cents("sample standard clean, 3 bedrooms, weekly (kit I44)", S("Standard clean", "3 bedrooms", "Up to 8 miles", "Weekly").price, 280);
  cents("sample deep clean, 2 bedrooms, 30 miles, monthly (kit I44)", S("Deep clean", "2 bedrooms", "8 to 15 miles", "Monthly").price, 480);
  [["Deep clean", "3 bedrooms", "15 to 25 miles", "Every 2 weeks", 720], ["Standard clean", "2 bedrooms", "Up to 8 miles", "Every 2 weeks", 220],
   ["Standard clean", "3 bedrooms", "Up to 8 miles", "Weekly", 325], ["Deep clean", "2 bedrooms", "8 to 15 miles", "Monthly", 505]]
    .forEach(([service, size, z, f, one]) => cents(`sample ${service}, ${size}, ${f}: one-time price before the discount (kit I42)`, S(service, size, z, f).oneTime, one));
  x = S("Deep clean", "2 bedrooms", "8 to 15 miles", "One time");
  cents("sample deep clean, 2 bedrooms, 30 miles: floor (kit I40)", x.floor, 428.0712770356098);
  cents("sample deep clean, 2 bedrooms, 30 miles: one-time (kit I42)", x.price, 505);

  // The copied lines match docs/assets/pnf-calc.js service(), which the free calculators and their tests use.
  const pnf = path.join(HERE, "..", "..", "..", "..", "docs", "assets", "pnf-calc.js");
  if (fs.existsSync(pnf)) {
    const P = require(pnf);
    let worst = 0, n = 0, seed = 7;
    const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
    for (let k = 0; k < 500; k++) {
      const i = { takeHome: 20000 + rnd() * 150000, weeks: 20 + Math.floor(rnd() * 33), hours: 20 + Math.floor(rnd() * 50),
        paidShare: 30 + rnd() * 70, incomeTax: rnd() * 30, margin: rnd() * 40, monthlyCosts: rnd() * 3000, perMile: rnd(),
        mph: 10 + rnd() * 50, jobHours: Math.round(rnd() * 400) / 20, people: 1 + Math.floor(rnd() * 4),
        supplies: Math.round(rnd() * 300), miles: Math.round(rnd() * 120) };
      const want = P.service(i);
      const c = cfgWith(want.breakEven, i.mph, { jobs: [J(i.jobHours, i.people, i.supplies, i.miles)] });
      c.rates.marginPercent = i.margin; c.rates.vehicleCostPerMile = i.perMile;
      const got = Q.price(c, { job: 0 });
      worst = Math.max(worst, Math.abs(got.floor - want.floor), Math.abs(got.price - want.quote));
      n++;
    }
    result(worst === 0, `the page's maths equals pnf-calc.js service() on ${n} random jobs`, `largest gap ${worst}`);
  } else console.log("skip pnf-calc.js cross-check (not found next to this repo copy)");
}

// ---------------------------------------------------------------- a buyer's page against their workbook
if (EXPECT) {
  const want = JSON.parse(fs.readFileSync(EXPECT, "utf8"));
  result(Math.abs(cfg.rates.breakEvenPerHour - want.breakEvenPerHour) < 1e-9, "break-even rate matches the workbook",
    `${cfg.rates.breakEvenPerHour} (workbook ${want.breakEvenPerHour})`);
  (want.jobs || []).forEach((w) => {
    const k = cfg.jobs.findIndex((j) => j.service === w.service && (j.size || "") === (w.size || ""));
    if (k < 0) return console.log(`note: ${w.service}, ${w.size} is on the price sheet but not on the website`);
    const x = Q.price(Object.assign({}, cfg, { pricing: Object.assign({}, cfg.pricing, { minimumCharge: 0 }) }), { job: k });
    cents(`${w.service}, ${w.size}: floor at ${cfg.jobs[k].miles} miles`, x.floor, w.floor);
    cents(`${w.service}, ${w.size}: price at ${cfg.jobs[k].miles} miles`, x.price, w.price);
  });
  result(!/sample/i.test(cfg.business.name) && !cfg.business.notice && !cfg.sample, "no sample name, notice or note left");
  result(!cfg.booking || cfg.booking.href !== "#request-this-clean", "booking link is the buyer's own");
}

// ---------------------------------------------------------------- the page in a real browser, when Playwright is here
(async () => {
  let chromium = null;
  try { ({ chromium } = require("playwright")); } catch (e) { /* not installed */ }
  if (!chromium) {
    console.log("skip browser checks (Playwright not found; in the cloud container run with NODE_PATH=$(npm root -g))");
    return finish();
  }
  const browser = await chromium.launch();
  try {
    for (const [w, h] of [[1280, 900], [390, 844]]) {
      const page = await browser.newPage({ viewport: { width: w, height: h } });
      const outside = [], errors = [];
      page.on("request", (q) => { const u = q.url(); if (!u.startsWith("file:") && !u.startsWith("data:")) outside.push(u); });
      page.on("pageerror", (e) => errors.push(e.message));
      page.on("console", (m) => { if (m.type() === "error" || m.type() === "warning") errors.push(m.text()); });
      await page.goto("file://" + PAGE);
      const info = await page.evaluate(() => {
        const inputs = [...document.querySelectorAll("input, select, textarea")];
        return {
          inputs: inputs.length,
          unlabeled: inputs.filter((i) => !(i.labels && [...i.labels].some((l) => l.textContent.trim()))).length,
          overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
          price: document.getElementById("qc-price").textContent
        };
      });
      result(outside.length === 0, `${w}px: no outside requests`, outside.join(", "));
      result(errors.length === 0, `${w}px: no console errors or warnings`, errors.join(" | "));
      result(info.inputs > 0 && info.unlabeled === 0, `${w}px: every one of ${info.inputs} inputs has a label`);
      result(info.overflow <= 0, `${w}px: no sideways scrolling`, `${info.overflow}px`);
      if (w === 1280) {
        // every job, picked the way a customer picks it, shows the maths' price for the default distance and frequency
        const services = Q.services(cfg), d = cfg.defaults || {};
        const zi = Math.max(0, (cfg.zones || []).findIndex((z) => z.label === d.zone));
        const fi = Math.max(0, (cfg.frequencies || []).findIndex((f) => f.label === d.frequency));
        let shown = 0, wrong = [];
        for (let s = 0; s < services.length; s++) {
          if (services.length > 1) await page.locator('input[name="qc-service"]').nth(s).check();
          for (let k = 0; k < services[s].jobs.length; k++) {
            const sizes = page.locator('input[name="qc-size"]');
            if (await sizes.count()) await sizes.nth(k).check();
            const want = Q.money(Q.price(cfg, { job: services[s].jobs[k], zone: (cfg.zones || []).length ? zi : undefined,
              frequency: (cfg.frequencies || []).length ? fi : undefined }).price);
            const got = await page.locator("#qc-price").textContent();
            shown++;
            if (got !== want) wrong.push(`${cfg.jobs[services[s].jobs[k]].service} ${cfg.jobs[services[s].jobs[k]].size}: ${got} not ${want}`);
          }
        }
        result(wrong.length === 0, `every one of ${shown} jobs shows the maths' price on the page`, wrong.join("; "));
        // the default job at every distance and frequency, with and without each extra: the page against the maths
        await page.reload();
        const firstSvc = Math.max(0, services.findIndex((s) => s.name === d.service));
        const dj = services[firstSvc].jobs.find((j) => cfg.jobs[j].size === d.size);
        const job0 = dj !== undefined ? dj : services[firstSvc].jobs[0];
        const Z = (cfg.zones || []).length ? cfg.zones.map((z, i) => i) : [undefined];
        const F = (cfg.frequencies || []).length ? cfg.frequencies.map((f, i) => i) : [undefined];
        const X = [[]].concat((cfg.extras || []).map((x, i) => [i]));
        let combos = 0;
        wrong = [];
        for (const z of Z) {
          if (z !== undefined && Z.length > 1) await page.locator('input[name="qc-zone"]').nth(z).check();
          for (const f of F) {
            if (f !== undefined && F.length > 1) await page.locator('input[name="qc-frequency"]').nth(f).check();
            for (const ex of X) {
              const boxes = page.locator('input[name="qc-extra"]');
              for (let i = 0; i < (cfg.extras || []).length; i++) await boxes.nth(i).setChecked(ex.includes(i));
              const r = Q.price(cfg, { job: job0, zone: z, frequency: f, extras: ex });
              const got = await page.locator("#qc-price").textContent();
              combos++;
              if (got !== Q.money(r.price)) wrong.push(`zone ${z}, frequency ${f}, extras ${ex}: ${got} not ${Q.money(r.price)}`);
              const deposit = (cfg.pricing || {}).depositPercent > 0;
              const facts = await page.locator("#qc-facts").textContent();
              if (deposit && !facts.includes(Q.money(r.deposit))) wrong.push(`deposit ${Q.money(r.deposit)} not shown`);
              if (r.atMinimum && !facts.includes(Q.money(cfg.pricing.minimumCharge))) wrong.push("minimum charge line not shown");
            }
          }
        }
        result(wrong.length === 0, `${combos} distance, frequency and extra choices show the maths' price`, wrong.slice(0, 3).join("; "));
        // keyboard: Tab into the first group, an arrow key moves the choice and the price follows
        await page.reload();
        await page.keyboard.press("Tab");
        const before = await page.locator("#qc-price").textContent();
        const focused = await page.evaluate(() => document.activeElement && document.activeElement.name);
        await page.keyboard.press("ArrowRight");
        const after = await page.locator("#qc-price").textContent();
        result(!!focused && focused.startsWith("qc-"), "keyboard: Tab reaches the first question", String(focused));
        result(before !== after || services.length < 2, "keyboard: an arrow key changes the choice and the price", `${before} then ${after}`);
      }
      await page.close();
    }
  } finally {
    await browser.close();
  }
  finish();
})();

function finish() {
  console.log(`\n${passes} passed, ${fails} failed`);
  process.exit(fails ? 1 : 0);
}
