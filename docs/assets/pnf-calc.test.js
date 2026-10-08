// node docs/assets/pnf-calc.test.js : the free calculators must give the paid workbooks' own example answers.
const P = require("./pnf-calc.js");
const near = (a, b, tol = 0.006) => Math.abs(a - b) <= tol;
let fails = 0;
function check(name, got, want) {
  const ok = near(got, want);
  if (!ok) fails++;
  console.log(`${ok ? "ok  " : "FAIL"} ${name}: ${got.toFixed(2)} (workbook ${want})`);
}
// #20 Hourly Rate Quick Calculator example (recalculated workbook values)
const h = P.hourly({ takeHome: 60000, taxRate: 25, expenses: 6000, weeks: 48, hours: 40, billableShare: 60, checkRate: 40 });
check("#20 minimum hourly rate", h.rate, 74.65);
check("#20 rate card", h.rateCard, 75);
check("#20 revenue at $40", h.checkRevenue, 46080);
check("#20 take-home at $40", h.keep, 30060);
check("#20 per hour worked at $40", h.keepPerHour, 15.66);
// #13 Service Pricing Calculator example
const s = P.service({ takeHome: 52000, weeks: 48, hours: 45, paidShare: 65, incomeTax: 12, margin: 15, monthlyCosts: 545,
  perMile: 0.76, mph: 30, jobHours: 2.5, people: 1, supplies: 8, miles: 15 });
check("#13 break-even", s.breakEven, 54.80);
check("#13 target", s.target, 64.47);
check("#13 guess", s.guess, 24.07);
check("#13 standard clean floor", s.floor, 183.79);
check("#13 standard clean quote", s.quote, 220);
check("#13 profit in quote", s.quoteProfit, 36.21);
// Pressure washing edition example
const p = P.service({ takeHome: 55000, weeks: 44, hours: 45, paidShare: 65, incomeTax: 12, margin: 15, monthlyCosts: 755,
  perMile: 0.76, mph: 30, jobHours: 1.5, people: 1, supplies: 12, miles: 20 });
check("PW break-even", p.breakEven, 64.89);
check("PW target", p.target, 76.34);
check("PW 2-car driveway floor", p.floor, 167.80);
check("PW 2-car driveway quote", p.quote, 200);
check("PW profit in quote", p.quoteProfit, 32.20);
const p2 = P.service({ takeHome: 55000, weeks: 44, hours: 45, paidShare: 65, incomeTax: 12, margin: 15, monthlyCosts: 755,
  perMile: 0.76, mph: 30, jobHours: 3, people: 1, supplies: 45, miles: 40 });
check("PW 2-story soft wash, 40 miles", p2.quote, 420);
// Premium 13-Week E-commerce Cash Flow, lite. Expected values from the workbook (3 Cash Flow, ending cash row)
// built with one channel paid in the week of sale (0-day lag, 0% fees) and the PO paid in full in its week.
const c1 = P.cashflow({ openingCash: 20000, weeklyIn: 53700, weeklyOut: 32000, poAmount: 117000, poWeek: 4 });
check("cash flow lite example lowest", c1.lowest, -10200);
check("cash flow lite example low week", c1.lowWeek, 4);
check("cash flow lite example gap", c1.gap, 10200);
check("cash flow lite example week 13", c1.end13, 185100);
const c2 = P.cashflow({ openingCash: 120000, weeklyIn: 53700, weeklyOut: 32000, poAmount: 117000, poWeek: 7 });
check("cash flow lite PO week 7 lowest", c2.lowest, 141700);
check("cash flow lite PO week 7 low week", c2.lowWeek, 1);
const c3 = P.cashflow({ openingCash: 50000, weeklyIn: 30000, weeklyOut: 45000, poAmount: 60000, poWeek: 13 });
check("cash flow lite burn lowest", c3.lowest, -205000);
check("cash flow lite burn gap", c3.gap, 205000);
// #5 True Profit System for Etsy Sellers, 2 Listings row 16 (8 oz Soy Candle, recalculated Oct 7, 2026).
// The page rounds each fee to the cent; the workbook does not, so fees are checked to the half cent and profit to the cent.
const near2 = (name, got, want, tol) => { const ok = Math.abs(got - want) <= tol; if (!ok) fails++; console.log(`${ok ? "ok  " : "FAIL"} ${name}: ${got.toFixed(4)} (workbook ${want})`); };
const ETSY = { price: 24, ship: 5.5, tax: 0, cost: 10.2, label: 6.25, adsRate: 0, tfRate: 6.5, procRate: 3, procFixed: 0.25, listFee: 0.2 };
const e = P.etsyFees(ETSY, 100);
check("#5 revenue", e.revenue, 29.5);
near2("#5 transaction fee", e.tf, 1.9175, 0.005);
near2("#5 processing fee", e.pf, 1.135, 0.005);
check("#5 listing fee", e.lf, 0.2);
near2("#5 total Etsy fees", e.fees, 3.2525, 0.01);
near2("#5 net profit", e.profit, 9.7975, 0.01);
near2("#5 margin", e.margin, 0.332118644067797, 0.0005);
check("#5 page example: profit to the cent", e.profit, 9.79);
check("#5 page example: Offsite Ads fee at 15%", e.adsIf, 4.43);
check("#5 page example: profit if an ad sale", e.profitIfAds, 5.36);
const eCap = P.etsyFees(Object.assign({}, ETSY, { price: 900, adsRate: 15 }), 100);
check("#5 Offsite Ads fee capped at $100", eCap.ads, 100);
// #12 Craft Fair Profit Calculator, 3 Break-Even (recalculated Oct 7, 2026)
const cf = P.craftFair({ booth: 150, other: 165.6, price: 13.84, cpp: 7.3, cardPct: 2.6, cardFlat: 0.15, cardShare: 70, avgSale: 30, target: 300 });
near2("#12 contribution per piece (workbook blends 15 products; same to the cent)", cf.contrib, 6.237672, 0.005);
check("#12 total fixed show cost", cf.total, 315.6);
check("#12 pieces to break even", cf.bePieces, 51);
check("#12 break-even sales", cf.beSales, 705.84);
check("#12 pieces for $300 profit", cf.tgtPieces, 99);
check("#12 sales for $300 profit", cf.tgtSales, 1370.16);
const cfNever = P.craftFair({ booth: 150, other: 0, price: 5, cpp: 6, cardPct: 0, cardFlat: 0, cardShare: 0, avgSale: 30, target: 0 });
check("#12 price under cost never breaks even", cfNever.never, 1);
// #9 STR Nightly Pricing Worksheet: example cabin (recalculated Oct 7, 2026), 2 Seasonality L and M, 4 Stay Discounts E
const HIST = [4800, 5200, 3900, 2600, 3100, 4400, 5600, 5300, 4300, 4700, 2400, 5000];
const strIn = (base, floor, hist, extra) => { const o = Object.assign({ base, floor, cleaning: 120, minStay: 2, fee: 15.5 }, extra || {}); hist.forEach((v, k) => { o["h" + (k + 1)] = v; }); return o; };
const st = P.strNightly(strIn(185, 115, HIST));
const ST_BASE = [208, 225, 169, 113, 134, 190, 242, 229, 186, 203, 104, 216], ST_NIGHT = [208, 225, 169, 115, 134, 190, 242, 229, 186, 203, 115, 216];
let stBad = 0;
for (let m = 1; m <= 12; m++) if (st["base" + m] !== ST_BASE[m - 1] || st["night" + m] !== ST_NIGHT[m - 1]) stBad++;
if (stBad) fails++; console.log(`${stBad ? "FAIL" : "ok  "} #9 all 12 base and nightly rates match 2 Seasonality M and 4 Stay Discounts E`);
check("#9 July multiplier", st.mult7, 1.30994152046784);
check("#9 July nightly rate", st.hiNight, 242);
check("#9 November base rate", st.loBase, 104);
check("#9 November held at the floor", st.loNight, 115);
check("#9 months at floor", st.atFloor, 2);
check("#9 July payout per night at 15.5%", st.hiPay, 204.49);
check("#9 2-night November stay with cleaning", st.stayTotal, 350);
if (st.hiMonth !== "July" || st.loMonth !== "November") { fails++; console.log("FAIL #9 busiest and quietest month names"); } else console.log("ok   #9 busiest July, quietest November");
// edge cases, each checked against the engine recalculated in LibreOffice with these inputs typed in (Oct 7, 2026)
const LAKE = [0.6, 0.6, 0.7, 0.85, 1.1, 1.4, 1.55, 1.45, 1.15, 0.9, 0.8, 0.9];
const s1 = P.strNightly(strIn(210, 140, LAKE)), S1N = [140, 140, 147, 179, 231, 294, 326, 305, 241, 189, 168, 189];
let s1Bad = 0; for (let m = 1; m <= 12; m++) if (s1["night" + m] !== S1N[m - 1]) s1Bad++;
if (s1Bad) fails++; console.log(`${s1Bad ? "FAIL" : "ok  "} #9 edge: lake curve as history, $210 base, $140 floor (engine 4 Stay Discounts E)`);
check("#9 edge: lake curve months at floor", s1.atFloor, 2);
const s2 = P.strNightly(strIn(99, 250, HIST));
check("#9 edge: floor above every month holds all 12", s2.atFloor, 12);
check("#9 edge: floor above every month, July base 130", s2.base7, 130);
check("#9 blank history stays valid=0", P.strNightly({ base: 185 }).valid, 0);
// #16 Debt Payoff Tracker: example (recalculated Oct 7, 2026). Balances are 2 Debts L17:L21.
const debtIn = (rows, extra) => { const o = { extra }; rows.forEach((r, k) => { o["b" + (k + 1)] = r[0]; o["a" + (k + 1)] = r[1]; o["m" + (k + 1)] = r[2]; }); return o; };
const EX = [[4751.76, 24.99, 145], [854.32, 26.99, 40], [10748.15, 7.4, 329], [18658.05, 5.5, 205], [3142.59, 12.9, 112]];
const dp = P.debtPayoff(debtIn(EX, 269));
check("#16 owed today", dp.owed, 38154.87);
check("#16 sum of minimums", dp.minSum, 831);
check("#16 monthly amount", dp.monthly, 1100);
check("#16 avalanche months", dp.avaMonths, 40);
check("#16 avalanche interest", dp.avaInt, 4965.45);
check("#16 snowball months", dp.snoMonths, 40);
check("#16 snowball interest", dp.snoInt, 5233.73);
check("#16 minimums only months", dp.minMonths, 119);
check("#16 minimums only interest", dp.minInt, 11092.6791379297);
check("#16 avalanche saved vs minimums", dp.avaSaved, 6127.22913792965);
const offs = (r, key) => [1, 2, 3, 4, 5].map(k => r[key + k]).join(",");
const wantOff = { ava: "Month 15,Month 3,Month 25,Month 40,Month 18", sno: "Month 19,Month 3,Month 25,Month 40,Month 11", min: "Month 56,Month 30,Month 37,Month 119,Month 34" };
for (const k of ["ava", "sno", "min"]) { const ok = offs(dp, k) === wantOff[k]; if (!ok) fails++; console.log(`${ok ? "ok  " : "FAIL"} #16 per-debt payoff months, ${k}: ${offs(dp, k)}`); }
// edge 1: the card's minimum ($50) does not cover its interest; monthly = the minimums, no extra
const d1 = P.debtPayoff(debtIn([[4751.76, 24.99, 50], ...EX.slice(1)], 0));
check("#16 edge: minimums only never (flag)", d1.minNever, 1);
check("#16 edge: avalanche months", d1.avaMonths, 69);
check("#16 edge: avalanche interest", d1.avaInt, 11968.5);
check("#16 edge: snowball months", d1.snoMonths, 69);
check("#16 edge: snowball interest", d1.snoInt, 11972.64);
{ const ok = offs(d1, "ava") === "Month 52,Month 30,Month 37,Month 69,Month 34" && offs(d1, "sno") === "Month 52,Month 30,Month 37,Month 69,Month 33" && d1.min1 === "Never";
  if (!ok) fails++; console.log(`${ok ? "ok  " : "FAIL"} #16 edge: per-debt months ${offs(d1, "ava")} / ${offs(d1, "sno")} / ${d1.min1}`); }
// edge 2: a 0% debt, an empty row in the middle, four rows used, $50 extra
const d2 = P.debtPayoff(debtIn([[2000, 0, 100], [9000, 19.99, 250], [0, 10, 0], [15000, 3.9, 300], [0, 0, 0]], 50));
check("#16 edge 2: sum of minimums", d2.minSum, 650);
check("#16 edge 2: avalanche months", d2.avaMonths, 44);
check("#16 edge 2: avalanche interest", d2.avaInt, 4558.89);
check("#16 edge 2: snowball months", d2.snoMonths, 44);
check("#16 edge 2: snowball interest", d2.snoInt, 4728.43);
check("#16 edge 2: minimums only months", d2.minMonths, 56);
check("#16 edge 2: minimums only interest", d2.minInt, 6249.99213131759);
{ const ok = offs(d2, "ava") === "Month 20,Month 36,-,Month 44,-" && offs(d2, "sno") === "Month 14,Month 37,-,Month 44,-" && offs(d2, "min") === "Month 20,Month 56,-,Month 55,-";
  if (!ok) fails++; console.log(`${ok ? "ok  " : "FAIL"} #16 edge 2: per-debt months ${offs(d2, "ava")} / ${offs(d2, "sno")} / ${offs(d2, "min")}`); }
const d3 = P.debtPayoff(debtIn([[50000, 29.99, 1250.5]], 0));
check("#16 a plan past 240 months flags 20+ years", d3.avaNever, 1);
// #7 Shipping True-Cost Calculator: Ceramic Mug 12 oz, 1 Parcel Costs row 22 (recalculated Oct 7, 2026)
const SH = { charged: 4.95, postage: 9.95, box: 0.85, filler: 0.45, tape: 0.08, labelPaper: 0.06, minutes: 6, hourly: 18, feePct: 9.5 };
const sh = P.shippingCost(SH);
check("#7 packing labor", sh.labor, 1.8);
check("#7 true cost per parcel", sh.parcel, 13.19);
check("#7 shortfall before fees", sh.shortfall, -8.24);
check("#7 fees on shipping (5 Dashboard I27 2.72525 less 9.5% x $19 and $0.45)", sh.fees, 2.72525 - 0.095 * 19 - 0.45);
check("#7 true cost per order", sh.total, 13.66025);
check("#7 over or under per order", sh.net, -8.71025);
check("#7 break-even shipping", sh.breakEven, 14.58);
const sh1 = P.shippingCost({ charged: 0, postage: 7.5, box: 0.3, filler: 0, tape: 0, labelPaper: 0.06, minutes: 3, hourly: 25, feePct: 9.5 });
check("#7 edge: free shipping parcel cost (engine P22)", sh1.parcel, 9.11);
check("#7 edge: free shipping shortfall (engine Q22)", sh1.shortfall, -9.11);
check("#7 edge: free shipping has no fee on shipping (engine I27 2.255 = 9.5% x $19 + $0.45)", sh1.fees, 0);
const sh2 = P.shippingCost({ charged: 17.95, postage: 12.84, box: 1.4, filler: 0.35, tape: 0.1, labelPaper: 0.06, minutes: 7, hourly: 0, feePct: 13.25 });
check("#7 edge: $0 hourly, parcel (engine P22)", sh2.parcel, 14.75);
check("#7 edge: $0 hourly, shortfall (engine Q22, Covered)", sh2.shortfall, 3.2);
check("#7 edge: 13.25% fee on shipping (engine I27 less 13.25% x $19 and $0.45)", sh2.fees, 5.345875 - 0.1325 * 19 - 0.45);
check("#7 edge: covered after fees", sh2.isUnder, 0);
// #6 Cash-Aware Reorder Planner, 2 SKU List rows (recalculated workbook, Oct 8, 2026): safety 20%, 14 days between orders
const R12 = P.reorderPoint({ daily: 6, lead: 7, safety: 20, cycle: 14, onHand: 46, onOrder: 0, unitCost: 2.6 });
check("#6 SKU-012 reorder point (Q)", R12.rop, 50.4);
check("#6 SKU-012 order up to (R)", R12.upTo, 151.2);
check("#6 SKU-012 days of stock (P)", R12.days, 7.6667);
check("#6 SKU-012 days until reorder (W)", R12.until, -0.7333);
check("#6 SKU-012 REORDER, order cost (X)", R12.status === "REORDER" ? R12.orderCost : -1, 275.6);
const R1 = P.reorderPoint({ daily: 1.4, lead: 21, safety: 20, cycle: 14, onHand: 48, onOrder: 0, unitCost: 6.5 });
check("#6 SKU-001 reorder point (Q)", R1.rop, 35.28);
check("#6 SKU-001 days until reorder (W)", R1.until, 9.0857);
check("#6 SKU-001 OK, next order cost within 30 days (X)", R1.status === "OK" ? R1.orderCost : -1, 156);
const R2 = P.reorderPoint({ daily: 1.8, lead: 21, safety: 20, cycle: 14, onHand: 30, onOrder: 0, unitCost: 7.2 });
check("#6 SKU-002 STOCKOUT RISK, order cost (X)", R2.status === "STOCKOUT RISK" ? R2.orderCost : -1, 331.2);
check("#6 SKU-002 order up to (R)", R2.upTo, 75.6);
const R11 = P.reorderPoint({ daily: 3.5, lead: 7, safety: 20, cycle: 14, onHand: 24, onOrder: 48, unitCost: 5.6 });
check("#6 SKU-011 on order keeps it OK, days until reorder (W)", R11.status === "OK" ? R11.until : -1, 12.1714);
check("#6 SKU-011 next order cost within 30 days (X)", R11.orderCost, 330.4);
const R0 = P.reorderPoint({ daily: 0, lead: 21, safety: 20, cycle: 14, onHand: 6, onOrder: 0, unitCost: 17 });
check("#6 SKU-005 no sales: reorder point 0 (Q)", R0.status === "NO SALES" ? R0.rop : -1, 0);
// STR break-even nights (lite page; expected values worked by hand in Python, Oct 8, 2026)
const B1 = P.strBreakEven({ fixed: 2400, rate: 185, cleanKept: 20, stay: 3, fee: 15.5 });
check("STR break-even: payout per booked night", B1.perNight, 162.99167);
check("STR break-even: exact nights", B1.exact, 14.72468);
check("STR break-even: nights a month", B1.nights, 15);
check("STR break-even: occupancy", B1.occupancy, 0.49315);
check("STR break-even: rate to break even at half the month", B1.rateAtHalf, 178.86574);
const B2 = P.strBreakEven({ fixed: 3800, rate: 140, cleanKept: 0, stay: 2, fee: 15.5 });
check("STR break-even: no cleaning kept, nights", B2.nights, 33);
check("STR break-even: more nights than a month flagged", B2.over, 1);
const B3 = P.strBreakEven({ fixed: 1500, rate: 0, cleanKept: 0, stay: 3, fee: 15.5 });
check("STR break-even: zero payout can never break even", B3.never, 1);
// blank inputs never produce NaN or Infinity
const b = P.service({});
const bh = P.hourly({});
const bc = P.cashflow({});
const more = [P.etsyFees({}), P.craftFair({}), P.strNightly({}), P.debtPayoff({}), P.shippingCost({}), P.reorderPoint({}), P.strBreakEven({})]
  .flatMap(o => Object.values(o)).filter(v => typeof v === "number");
const bad = [...Object.values(b), ...Object.values(bh), ...Object.values(bc), ...more].filter(v => !isFinite(v));
if (bad.length) { fails++; console.log("FAIL blank inputs give non-finite values"); } else console.log("ok   blank inputs stay finite");
process.exit(fails ? 1 : 0);
