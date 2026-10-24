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
// #23 Junk Removal Pricing Calculator price sheet, truck loads (recalculated workbook, Oct 13, 2026)
const JR = { takeHome: 60000, weeks: 48, hours: 50, paidShare: 60, incomeTax: 12, margin: 15, monthlyCosts: 715, perMile: 0.76, mph: 30 };
[["1/8 load", 0.5, 20, 229.89, 275], ["1/4 load", 1, 40, 312.25, 370], ["1/2 load", 1.5, 75, 409.62, 485],
 ["3/4 load", 2, 110, 506.98, 600], ["full load", 2.5, 150, 609.34, 720]].forEach(function (t) {
  const r = P.service(Object.assign({}, JR, { jobHours: t[1], people: 2, supplies: t[2], miles: 30 }));
  check("#23 " + t[0] + " floor", r.floor, t[3]);
  check("#23 " + t[0] + " quote", r.quote, t[4]);
});
// #23 cleanouts for the estate cleanout page (4 Price Sheet rows 21 to 23 and 28, recalculated Oct 15, 2026)
[["garage cleanout", 4, 2, 225, 50, 969.79, 1145], ["basement cleanout", 5, 2, 225, 50, 1094.51, 1290],
 ["estate cleanout 3-bed", 10, 3, 600, 120, 3310.46, 3895], ["shed tear-down", 5, 2, 180, 50, 1049.51, 1235]].forEach(function (t) {
  const r = P.service(Object.assign({}, JR, { jobHours: t[1], people: t[2], supplies: t[3], miles: t[4] }));
  check("#23 " + t[0] + " floor", r.floor, t[5]);
  check("#23 " + t[0] + " quote", r.quote, t[6]);
});
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
// soft-wash-pricing-calculator page: #22 price sheet soft wash rows (recalculated workbook, Oct 14, 2026)
const PWS = { takeHome: 55000, weeks: 44, hours: 45, paidShare: 65, incomeTax: 12, margin: 15, monthlyCosts: 755, perMile: 0.76, mph: 30 };
[["1-story soft wash", 2.5, 1, 30, 250.69, 295], ["2-story soft wash", 3, 1, 45, 298.13, 355],
 ["roof soft wash, 1-story", 2, 2, 70, 431.29, 510], ["gutter face brightening", 1.5, 1, 15, 170.80, 205]].forEach(function (t) {
  const r = P.service(Object.assign({}, PWS, { jobHours: t[1], people: t[2], supplies: t[3], miles: 20 }));
  check("PW " + t[0] + " floor", r.floor, t[4]);
  check("PW " + t[0] + " quote", r.quote, t[5]);
});
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
// snowball page (debt-snowball-calculator): saving vs minimums and the gap to avalanche, from 1 Dashboard I16, I20, I24
check("#16 snowball saved vs minimums", dp.snoSaved, 5858.9491379297);
check("#16 avalanche less interest than snowball", dp.avaVsSno, 268.28);
check("#16 edge: snowball saving blank when minimums never end", d1.snoSaved, 0);
check("#16 edge 2: snowball saved vs minimums", d2.snoSaved, 1521.56213131759);
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
// #6 inventory turnover (expected values from the recalculated sample shop, Oct 10, 2026: 1 Your Shop I15, I26:I28; 2 SKU List P, U, Y)
const T1 = P.inventoryTurnover({ cogsYear: 70404.85, stockValue: 3368.9, daily: 0.9, onHand: 130 });
check("#6 shop inventory turns a year (I27)", T1.turns, 20.89847);
check("#6 shop days to sell through stock (I28)", T1.days, 17.46539);
check("#6 SKU-009 days of stock (P)", T1.pDays, 144.44444);
check("#6 SKU-009 OVERSTOCK at 120 days", T1.overstock, 1);
const T2 = P.inventoryTurnover({ cogsYear: 678.9, stockValue: 93, daily: 0.6, onHand: 30 });
check("#6 SKU-003 turns (Y / U)", T2.turns, 7.3);
check("#6 SKU-003 product turns match the shop maths", T2.pTurns, 7.3);
check("#6 SKU-003 days of stock (P)", T2.pDays, 50);
check("#6 SKU-003 not overstock", T2.overstock, 0);
const T3 = P.inventoryTurnover({ cogsYear: 0, stockValue: 0, daily: 0, onHand: 6 });
check("#6 SKU-005 no sales: turns 0, no error", T3.turns, 0);
check("#6 SKU-005 flagged no sales", T3.noSales, 1);
check("#6 blank stock value flagged", T3.noStock, 1);
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
// #19 Rental Property Spreadsheet, 4 Property P&L (example log, 2026; engine asserts oak 4844/2844/1450/550, all 13569/6683)
const RC1 = P.rentalCashFlow({ income: 14850, expenses: 5200, interest: 4806, principal: 2844, improve: 1450, months: 9 });
check("#19 Oak Street House profit before depreciation", RC1.profit, 4844);
check("#19 Oak Street House cash flow", RC1.cash, 550);
check("#19 Oak Street House cash flow per month", RC1.cashMonth, 61.11111);
const RC2 = P.rentalCashFlow({ income: 22050, expenses: 7817, interest: 5508, principal: 2592, improve: 0, months: 10 });
check("#19 Maple Duplex profit before depreciation", RC2.profit, 8725);
check("#19 Maple Duplex cash flow", RC2.cash, 6133);
const RC3 = P.rentalCashFlow({ income: 36900, expenses: 13017, interest: 10314, principal: 5436, improve: 1450, months: 10 });
check("#19 all properties profit", RC3.profit, 13569);
check("#19 all properties cash flow", RC3.cash, 6683);
const RC4 = P.rentalCashFlow({ income: 14850, expenses: 5200, interest: 4806, principal: 2844, improve: 3000, months: 9 });
check("#19 profit but negative cash flow flagged", RC4.gap, 1);
check("#19 negative cash flow", RC4.cash, -1000);
check("#19 cash went down by", RC4.down, 1000);
check("#19 profit case is not the loss callout", RC4.neg, 0);
// #18 One-Tab Business Expense Tracker, Summary tab (example workbook recalculated Oct 9, 2026: Year P27 4209, P29 837.9, P50 1984.75, P51 1386.35; Jan D51 -164.76)
const BE1 = P.businessExpense({ sales: 4233, otherIncome: 0, refunds: 24, inventory: 837.9, fees: 292.41, rent: 1125, supplies: 96.25, ads: 45, car: 14, otherExp: 142.59, more: 269.5, equipment: 329, draw: 500, months: 3 });
check("#18 income after refunds, Jan to Mar", BE1.income, 4209);
check("#18 total expenses, Jan to Mar", BE1.expenses, 1984.75);
check("#18 profit before inventory count, Jan to Mar", BE1.profit, 1386.35);
check("#18 expenses per month", BE1.expMonth, 661.58333);
check("#18 logged but kept out of profit", BE1.offProfit, 829);
const BE2 = P.businessExpense({ sales: 858, refunds: 24, inventory: 412.6, fees: 81.51, rent: 350, supplies: 96.25, otherExp: 58.4, draw: 500, months: 1 });
check("#18 January expenses", BE2.expenses, 586.16);
check("#18 January loss", BE2.profit, -164.76);
check("#18 January loss flagged", BE2.neg, 1);
const BE3 = P.businessExpense({ sales: 0, fees: 50, months: 0 });
check("#18 no income flagged", BE3.noIncome, 1);
check("#18 no income gives no share", BE3.expShare, 0);
// #20 Quick quote and "Bill more of your week", values from the recalculated #20 workbook (Oct 9) with these inputs
const hq = P.hourly({ takeHome: 60000, taxRate: 25, expenses: 6000, weeks: 48, hours: 40, billableShare: 60, checkRate: 40, jobHours: 12, materials: 150, markup: 15 });
check("#20 quote labor (I41)", hq.quoteLabor, 900);
check("#20 materials with markup (I42)", hq.quoteMaterials, 172.5);
check("#20 quote total (I43)", hq.quote, 1072.5);
check("#20 rate at 50% billed (I31)", hq.rateAt50, 89.58);
check("#20 rate at 80% billed (I34)", hq.rateAt80, 55.99);
const hb = P.hourly({ takeHome: 45000, taxRate: 22, expenses: 3600, weeks: 46, hours: 35, billableShare: 55, checkRate: 50, jobHours: 20, materials: 0, markup: 0 });
check("#20 case B minimum rate (I21)", hb.rate, 69.22);
check("#20 case B take-home at $50 (D31)", hb.keep, 31726.5);
check("#20 case B per hour worked (D32)", hb.keepPerHour, 19.71);
check("#20 case B quote, 20 h at $70 (I43)", hb.quote, 1400);
check("#20 case B rate at 70% billed (I33)", hb.rateAt70, 54.39);
const hc = P.hourly({ takeHome: 90000, taxRate: 30, expenses: 12000, weeks: 44, hours: 45, billableShare: 70, checkRate: 120, jobHours: 2.5, materials: 80, markup: 25 });
check("#20 case C minimum rate (I21)", hc.rate, 101.42);
check("#20 case C take-home at $120 (D31)", hc.keep, 108024);
check("#20 case C quote, 2.5 h at $105 plus $100 (I43)", hc.quote, 362.5);
check("#20 case C rate at 60% billed (I32)", hc.rateAt60, 118.33);
// Self-employment tax (Schedule SE arithmetic; hand-computed Oct 9, 2026 with the 2026 wage base $184,500)
const SE1 = P.seTax({ net: 15570, wages: 0 });  // #21 example: $15,570 received in 2026, treated as net profit
check("SE tax on #21's $15,570", SE1.se, 2199.97);
check("SE net earnings 92.35%", SE1.earnings, 14378.90);
check("SE deductible half", SE1.half, 1099.99);
check("SE a quarter", SE1.quarter, 549.99);
const SE2 = P.seTax({ net: 70394, wages: 0 });  // #13 example profit before tax ($70,394): 15.3% x 92.35% = 14.13%
check("SE tax on #13's $70,394 profit", SE2.se, 70394 * 0.153 * 0.9235);
const SE3 = P.seTax({ net: 250000, wages: 0 });
check("SE Social Security capped at $184,500", SE3.ssPart, 22878);
check("SE tax above the wage base", SE3.se, 29573.38);
check("SE above base flagged", SE3.capped, 1);
const SE4 = P.seTax({ net: 100000, wages: 150000 });
check("SE with $150,000 of W-2 wages", SE4.se, 6956.15);
const SE5 = P.seTax({ net: 400, wages: 0 });
check("SE under $400 of net earnings owes nothing", SE5.se, 0);
check("SE under $400 flagged", SE5.under, 1);
check("SE loss owes nothing", P.seTax({ net: -500 }).se, 0);
// Window cleaning page: #13 engine with the compare_map storefront job (1.25 h, 1 person, $4, 12 miles)
const W1 = P.service({ takeHome: 52000, weeks: 48, hours: 45, paidShare: 65, incomeTax: 12, margin: 15, monthlyCosts: 545,
  perMile: 0.76, mph: 30, jobHours: 1.25, people: 1, supplies: 4, miles: 12 });
console.log("info window storefront floor", W1.floor.toFixed(2), "quote", W1.quote);
// Profit margin page: #5 engine, 3 Pricing "Your price for that margin" (I29, I30, I31), recalculated in LibreOffice Oct 10, 2026
const FEES5 = { tfRate: 6.5, procRate: 3, procFixed: 0.25, listFee: 0.2 };
const PM1 = P.profitMargin({ ...FEES5, target: 30, materials: 9.8, labor: 4, ship: 6.5, label: 7.4, packaging: 1.6, adsRate: 15 });
check("#5 example: list price for a 30% margin (I29)", PM1.price, 31.92975);
check("#5 example: ad-sale price (I30)", PM1.adPrice, 44.5989);
check("#5 example: net profit per unit (I31)", PM1.profit, 11.52893);
check("#5 example: round up to $0.50", PM1.roundHalf, 32);
const PM2 = P.profitMargin({ ...FEES5, target: 40, materials: 5, labor: 2, ship: 0, label: 4.5, packaging: 0.8, adsRate: 12 });
check("#5 40% margin, free shipping, $10K tier: price", PM2.price, 25.24752);
check("#5 40% margin: ad-sale price at 12%", PM2.adPrice, 33.11688);
check("#5 40% margin: net profit", PM2.profit, 10.09901);
const PM3 = P.profitMargin({ ...FEES5, target: 20, materials: 12, labor: 0, ship: 8, label: 9.1, packaging: 2, adsRate: 15 });
check("#5 20% margin: price", PM3.price, 25.40426);
check("#5 20% margin: ad-sale price", PM3.adPrice, 34.43243);
check("#5 20% margin: net profit", PM3.profit, 6.68085);
const PM4 = P.profitMargin({ ...FEES5, target: 76, materials: 9.8, labor: 4, ship: 6.5, label: 7.4, packaging: 1.6, adsRate: 15 });
check("#5 76% margin: price (I29)", PM4.price, 153.84483);
check("#5 76% margin: no ad-sale price (I30 blank)", PM4.adNone, 1);
check("#5 76% margin: net profit (I31)", PM4.profit, 121.86207);
const PM5 = P.profitMargin({ ...FEES5, target: 95, materials: 9.8 });
check("#5 95% margin: no price works", PM5.none, 1);
check("#5 95% margin: price 0, no Infinity", PM5.price, 0);
// #8 First-Time Employer guide, Section 6 (hand-checked in legal/reviews/8-2026-10-06.md): $20 an hour, 30 hours a week,
// 52 weeks (1,560 hours), Ohio example 2.85% on $9,000, workers' comp $4 per $100, FUTA 0.6% net, Gusto $804 / 3, $300 a month
const EC = P.employerCost({ wage: 20, hours: 30, weeks: 52, sutaRate: 2.85, sutaBase: 9000, compRate: 4, futaRate: 0.6, software: 268, benefit: 300 });
check("#8 week 1 SS + Medicare match ($37.20 + $8.70)", EC.weekFica, 45.90);
check("#8 week 1 FUTA", EC.weekFuta, 3.60);
check("#8 week 1 SUTA", EC.weekSuta, 17.10);
check("#8 week 1 workers' comp", EC.weekComp, 24.00);
check("#8 FUTA a year ($42)", EC.futa, 42);
check("#8 SUTA a year ($256.50)", EC.suta, 256.50);
check("#8 SS + Medicare match per hour", EC.ficaHr, 1.53);
check("#8 true hourly cost before software and benefits", EC.trueHourly, 22.5213);
check("#8 software per hour", EC.softwareHr, 0.1718);
check("#8 benefit per hour", EC.benefitHr, 2.3077);
check("#8 true hourly cost, all in", EC.allIn, 25.0008);
const EC2 = P.employerCost({ wage: 100, hours: 40, weeks: 52, sutaRate: 2.85, sutaBase: 9000, compRate: 0.5, futaRate: 0.6 });
check("high wage: SS stops at $184,500 (pay $208,000)", EC2.ss, 0.062 * 184500);
check("high wage: Medicare has no cap", EC2.med, 0.0145 * 208000);
const EC3 = P.employerCost({ wage: 15, hours: 10, weeks: 20, sutaRate: 2.85, sutaBase: 9000, compRate: 4, futaRate: 0.6 });
check("part-time $3,000 a year: FUTA on all of it", EC3.futa, 18);
check("part-time: SUTA on all of it", EC3.suta, 85.50);
check("blank wage: no cost shown", P.employerCost({}).trueHourly, 0);
// Startup cost pages: profit per job from the recalculated workbooks (#14 Quote Builder "Profit per visit" $18.61 on the
// $245 every-2-weeks visit, $505 a month of business costs; junk removal edition half truck load "Profit in this quote"
// $75.38 on $485, $715 a month; pressure washing edition example job $32.20 on $200, $755 a month)
const SC = P.startupCost({ s1: 600, s2: 250, s3: 400, s4: 300, s5: 0, monthly: 505, months: 3, profitJob: 18.61, jobsWeek: 10 });
check("#14 one-time spend", SC.oneTime, 1550);
check("#14 cushion, 3 months of $505", SC.cushion, 1515);
check("#14 cash to start", SC.cash, 3065);
check("#14 visits to earn back $1,550 at $18.61", SC.jobs, 84);
check("#14 weeks at 10 visits a week", SC.weeks, 9);
const SJ = P.startupCost({ s1: 4000, s2: 400, s3: 600, s4: 500, s5: 0, monthly: 715, months: 3, profitJob: 75.38, jobsWeek: 6 });
check("#23 cash to start", SJ.cash, 7645);
check("#23 half loads to earn back $5,500 at $75.38", SJ.jobs, 73);
check("#23 weeks at 6 jobs a week", SJ.weeks, 13);
const SP = P.startupCost({ s1: 3000, s2: 0, s3: 0, s4: 0, s5: 0, monthly: 755, months: 2, profitJob: 32.20, jobsWeek: 0 });
check("PW cash to start", SP.cash, 4510);
check("PW jobs to earn back $3,000 at $32.20", SP.jobs, 94);
check("PW no pace typed: weeks 0", SP.weeks, 0);
// #22 pressure washing startup page example: $4,500 one-time, 3 months of $755, $32.20 on the $200 driveway, 8 a week
const SW = P.startupCost({ s1: 3000, s2: 500, s3: 600, s4: 400, s5: 0, monthly: 755, months: 3, profitJob: 32.20, jobsWeek: 8 });
check("#22 cash to start", SW.cash, 6765);
check("#22 driveways to earn back $4,500 at $32.20", SW.jobs, 140);
check("#22 weeks at 8 jobs a week", SW.weeks, 18);
check("#22 machine already owned: jobs", P.startupCost({ s1: 0, s2: 500, s3: 600, s4: 400, profitJob: 32.20 }).jobs, 47);
check("exact multiple: $300 at $75 is 4 jobs", P.startupCost({ s1: 300, profitJob: 75 }).jobs, 4);
check("zero profit: no job count", P.startupCost({ s1: 1000, profitJob: 0 }).jobs, 0);
check("zero profit flag", P.startupCost({ s1: 1000, profitJob: 0 }).noProfit, 1);
// #29 Budget Planner Spreadsheet example, 1 Setup "Your month at a glance" recalculated Oct 12: take-home 7,275,
// bills 3,049, everyday spending 2,345 (2,325 monthly lines plus $240 car registration a year), savings 950, out 6,344,
// left to plan 931
const BP = P.budgetPlan({ pay1: 1950, freq1: "biweekly", pay2: 1400, freq2: "twice", other: 250, bills: 3049, spend: 2325, yearly: 240, save: 950 });
check("#29 paycheck 1 every 2 weeks per month", BP.pay1, 4225);
check("#29 take-home income per month", BP.income, 7275);
check("#29 everyday spending with yearly costs", BP.everyday, 2345);
check("#29 planned out each month", BP.out, 6344);
check("#29 left to plan", BP.left, 931);
check("#29 bills share of take-home", BP.billsShare, 0.419106529209622);
const BW = P.budgetPlan({ pay1: 500, freq1: "weekly", bills: 2500 });
check("weekly pay: 52/12 a month", BW.income, 2166.666667);
check("over plan shows the gap", BW.over, 333.333333);
check("blank budget: no income flag", P.budgetPlan({}).none, 1);
// #28 Profit and Loss Template, 2 Statement recalculated in LibreOffice Oct 12 (example file, Sep 2026)
const PLy = P.profitLoss({ sales: 29500, other: 40, refunds: 300, goods: 11000, stock0: 1200, stock1: 1450, expenses: 12675.66 });
check("#28 YTD net revenue", PLy.revenue, 29240);
check("#28 YTD cost of goods sold with counts", PLy.cogs, 10750);
check("#28 YTD gross profit", PLy.gross, 18490);
check("#28 YTD net profit", PLy.net, 5814.34);
check("#28 YTD net margin", PLy.netMargin, 0.198848837);
const PLs = P.profitLoss({ sales: 3400, refunds: 75, goods: 1260, expenses: 1551.99 });
check("#28 September net profit", PLs.net, 513.01);
check("#28 September gross margin", PLs.grossMargin, 0.621052632);
const PLb = P.profitLoss({ sales: 29500, other: 40, refunds: 300, goods: 11000, stock0: 1200, stock1: "", expenses: 12675.66 });
check("#28 one count blank: counts ignored (workbook with counts cleared)", PLb.net, 5564.34);
const PLa = P.profitLoss({ sales: 4550, goods: 1800, expenses: 1388.09 });
check("#28 August net margin", PLa.netMargin, 0.299320879);
check("blank P&L: none flag", P.profitLoss({}).none, 1);
// #26 Cake Order Form, 2 Order Form recalculated in LibreOffice Oct 12
const CK = P.cakeQuote({ style: "wedding", t1: "10 in round", t2: "8 in round", t3: "6 in round", pps: 6, minCake: 60, extras: 98,
  method: "delivery", delivBase: 10, miles: 18, perMile: 1, days: 36, rushDays: 7, rushPct: 20, taxRate: 0, depositPct: 50 });
check("#26 servings", CK.servings, 74);
check("#26 cake price", CK.cake, 444);
check("#26 delivery", CK.delivery, 28);
check("#26 total", CK.total, 570);
check("#26 deposit", CK.deposit, 285);
const CKr = P.cakeQuote({ style: "wedding", t1: "10 in round", t2: "8 in round", t3: "6 in round", pps: 6, minCake: 60, extras: 98,
  method: "delivery", delivBase: 10, miles: 18, perMile: 1, days: 4, rushDays: 7, rushPct: 20, taxRate: 8.25, depositPct: 50 });
check("#26 rush fee, 4 days out", CKr.rush, 108.4);
check("#26 sales tax 8.25%", CKr.tax, 55.97);
check("#26 total with rush and tax", CKr.total, 734.37);
check("#26 deposit with rush and tax", CKr.deposit, 367.19);
check("#26 balance with rush and tax", CKr.balance, 367.18);
const CKm = P.cakeQuote({ style: "party", t1: "6 in round", pps: 4.5, minCake: 60, extras: 98, method: "pickup", miles: 18, delivBase: 10, perMile: 1,
  days: 36, rushDays: 7, rushPct: 20, taxRate: 0, depositPct: 50 });
check("#26 minimum cake price applies", CKm.cake, 60);
check("#26 pickup total", CKm.total, 158);
check("blank cake quote: none flag", P.cakeQuote({}).none, 1);
// #25 Inventory Tracker, 1 Items recalculated in LibreOffice Oct 12 (example candle and soap maker)
const UC = P.unitCost({ materials: 4.2, labor: 2, packaging: 1.3, price: 24, feePct: 10, onHand: 26 });
check("#25 lavender unit cost (L16)", UC.uc, 7.5);
check("#25 lavender profit per unit (M16)", UC.ppu, 14.1);
check("#25 lavender stock value (P16)", UC.stockValue, 195);
check("#25 lavender margin", UC.margin, 0.5875);
const UCc = P.unitCost({ materials: 7.6, labor: 3, packaging: 1.9, price: 38, feePct: 10, onHand: 11 });
check("#25 citrus profit per unit (M18)", UCc.ppu, 21.7);
check("#25 citrus stock value (P18)", UCc.stockValue, 137.5);
const UCl = P.unitCost({ materials: 0.9, labor: 0.5, packaging: 0.3, price: 5, feePct: 10, onHand: 27 });
check("#25 lip balm profit per unit (M25)", UCl.ppu, 2.8);
check("#25 lip balm stock value (P25)", UCl.stockValue, 45.9);
const UCn = P.unitCost({ materials: 4.2, labor: 2, packaging: 1.3, price: 8, feePct: 10, onHand: -3 });
check("#25 price under cost: loss per unit", UCn.loss, 0.3);
check("#25 negative stock counts as 0 (workbook MAX(0, on hand))", UCn.stockValue, 0);
check("blank unit cost: none flag", P.unitCost({}).none, 1);
// #24 Fair Share Chore Chart, Fair Split tab recalculated in LibreOffice Oct 12 (real minutes a week, column F)
const CS = P.choreSplit({ a: 468.846153846154, b: 478.076923076923 });
check("#24 whole home minutes (F11)", CS.total, 946.923076923077);
check("#24 even split target", CS.aTarget, 473.461538461538);
check("#24 Alex under target", CS.aDiff, -4.615384615384);
check("#24 minutes to move", CS.move, 4.615384615384);
check("#24 even within 15 min", CS.even, 1);
const CS6 = P.choreSplit({ a: 566.923076923077, aShare: 60, b: 380, bShare: 40 });
check("#24 60/40 target for Alex", CS6.aTarget, 568.153846153846);
check("#24 60/40 Jordan over", CS6.bDiff, 1.230769230769);
const CS3 = P.choreSplit({ a: 313.461538461538, b: 314.615384615385, c: 318.846153846154 });
check("#24 three people: target each", CS3.aTarget, 315.641025641026);
check("#24 three people: Sam over", CS3.cDiff, 3.205128205128);
const CSu = P.choreSplit({ a: 300, b: 600, aShare: 50 });
check("#24 one share typed: even split used", CSu.useShares, 0);
check("#24 uneven: move 150", CSu.move, 150);
check("blank chore split: none flag", P.choreSplit({}).none, 1);
// #27 Client Tracker, 1 Today recalculated in LibreOffice Oct 12 (example house cleaner, as-of Oct 9, 2026):
// D31:D33 1,010 / 635 / 600, J24 revenue 5,150 (so everyone else 2,905), J25 unpaid 515, I7 open quotes 720, C39 "Top client: 20%".
const CM = P.clientMix({ c1: 1010, c2: 635, c3: 600, rest: 2905, unpaid: 515, quotes: 720 });
check("#27 revenue, done jobs (J24)", CM.total, 5150);
check("#27 top client share (C39 rounds to 20%)", CM.topPct, 20);
check("#27 top client share exact", CM.topShare, 0.196117);
check("#27 top three share", CM.top3Share, 0.435922);
check("#27 revenue without the top client", CM.withoutTop, 4140);
check("#27 unpaid balance (J25)", CM.unpaid, 515);
check("#27 collected", CM.collected, 4635);
check("#27 open quotes (I7)", CM.quotes, 720);
check("#27 second bar vs top (D32/D31)", CM.secondVsTop, 0.628713);
const CMs = P.clientMix({ c1: 600, c2: 1010, c3: 635, rest: 2905 });
check("#27 order typed does not matter: top", CMs.top, 1010);
check("#27 order typed does not matter: share", CMs.topPct, 20);
const CM1 = P.clientMix({ c1: 1200, unpaid: 2000 });
check("#27 one client: 100%", CM1.topPct, 100);
check("#27 one client: big flag", CM1.big, 1);
check("#27 unpaid capped at revenue", CM1.unpaid, 1200);
check("blank client mix: none flag", P.clientMix({}).none, 1);
// blank inputs never produce NaN or Infinity
const b = P.service({});
const bh = P.hourly({});
const bc = P.cashflow({});
const more = [P.etsyFees({}), P.craftFair({}), P.strNightly({}), P.debtPayoff({}), P.shippingCost({}), P.reorderPoint({}), P.strBreakEven({}), P.rentalCashFlow({}), P.businessExpense({}), P.seTax({}), P.profitMargin({}), P.employerCost({}), P.startupCost({}), P.budgetPlan({}), P.profitLoss({}), P.cakeQuote({}), P.unitCost({}), P.choreSplit({}), P.choreSplit({ a: 0, b: 0 }), P.clientMix({}), P.clientMix({ unpaid: 50 })]
  .flatMap(o => Object.values(o)).filter(v => typeof v === "number");
const bad = [...Object.values(b), ...Object.values(bh), ...Object.values(bc), ...more].filter(v => !isFinite(v));
if (bad.length) { fails++; console.log("FAIL blank inputs give non-finite values"); } else console.log("ok   blank inputs stay finite");
// #22 per square foot page: deck presets from the #22 workbook (4 Price Sheet rows 19 and 20; 3 Quote Builder with
// the deck job and a $150 current price, recalculated Oct 13, 2026)
const PWB = { takeHome: 55000, weeks: 44, hours: 45, paidShare: 65, incomeTax: 12, margin: 15, monthlyCosts: 755, perMile: 0.76, mph: 30 };
const SQ1 = P.serviceSqft(Object.assign({}, PWB, { area: 300, jobHours: 3, people: 1, supplies: 30, miles: 20, checkPerSqFt: 0.5 }));
check("#22 deck clean floor", SQ1.floor, 283.13);
check("#22 deck clean quote", SQ1.quote, 335);
check("#22 deck clean quote per sq ft", SQ1.perSqFt, 1.1167);
check("#22 deck clean floor per sq ft", SQ1.floorPerSqFt, 0.9438);
check("#22 deck clean at $0.50/sq ft vs floor", SQ1.checkGap, -133.13);
check("#22 deck clean sq ft per person-hour", SQ1.sqftPerHour, 100);
const SQ2 = P.serviceSqft(Object.assign({}, PWB, { area: 300, jobHours: 7, people: 1, supplies: 150, miles: 40 }));
check("#22 deck stain floor", SQ2.floor, 721.16);
check("#22 deck stain quote", SQ2.quote, 850);
check("#22 deck stain per sq ft", SQ2.perSqFt, 2.8333);
const SQ0 = P.serviceSqft(Object.assign({}, PWB, { area: "", jobHours: "", people: "", supplies: "", miles: "", checkPerSqFt: 0.5 }));
check("#22 blank job gives 0 per sq ft", SQ0.perSqFt, 0);
check("#22 blank job: no check warning", SQ0.checkShort, 0);
if (![SQ0.perSqFt, SQ0.floorPerSqFt, SQ0.sqftPerHour, SQ0.checkGap].every(isFinite)) { fails++; console.log("FAIL sq ft blank non-finite"); }
// contractor hourly page: the #20 workbook with contractor inputs (Calculator D15:D43 changed, recalculated Oct 13, 2026)
const HC = P.hourly({ takeHome: 65000, taxRate: 25, expenses: 14000, weeks: 48, hours: 50, billableShare: 55, checkRate: 45, jobHours: 16, materials: 600, markup: 20 });
check("contractor revenue needed", HC.revenue, 100666.67);
check("contractor minimum rate", HC.rate, 76.26);
check("contractor rate card", HC.rateCard, 80);
check("contractor take-home at $45", HC.keep, 34050);
check("contractor per hour worked at $45", HC.keepPerHour, 14.19);
check("contractor short by", HC.shortBy, 30950);
check("contractor job quote", HC.quote, 2000);
check("contractor rate at 80% billed", HC.rateAt80, 52.43);

// handyman hourly page: the #20 workbook with handyman inputs (Calculator D15:D43 changed, recalculated in LibreOffice Oct 15, 2026)
const HM = P.hourly({ takeHome: 55000, taxRate: 25, expenses: 9000, weeks: 48, hours: 45, billableShare: 55, checkRate: 50, jobHours: 3, materials: 85, markup: 15 });
check("handyman revenue needed (I17)", HM.revenue, 82333.33);
check("handyman billable hours (I20)", HM.billable, 1188);
check("handyman minimum rate (I21)", HM.rate, 69.30);
check("handyman rate card", HM.rateCard, 70);
check("handyman take-home at $50 (D31)", HM.keep, 37800);
check("handyman per hour worked (D32)", HM.keepPerHour, 17.5);
check("handyman short by (C33)", HM.shortBy, 17200);
check("handyman 3 h job quote (I43)", HM.quote, 307.75);
check("handyman rate at 80% billed (I34)", HM.rateAt80, 47.65);
const HM2 = P.hourly({ takeHome: 40000, taxRate: 20, expenses: 5000, weeks: 46, hours: 40, billableShare: 65, checkRate: 65, jobHours: 6, materials: 240, markup: 10 });
check("handyman case B minimum rate (I21)", HM2.rate, 45.99);
check("handyman case B take-home at $65 (D31)", HM2.keep, 58192);
check("handyman case B above goal (C33)", -HM2.shortBy, 18192);
check("handyman case B quote (I43)", HM2.quote, 564);
const HM3 = P.hourly({ takeHome: 70000, taxRate: 28, expenses: 12000, weeks: 50, hours: 50, billableShare: 50, checkRate: 60, jobHours: 1.5, materials: 0, markup: 0 });
check("handyman case C minimum rate (I21)", HM3.rate, 87.38);
check("handyman case C take-home at $60 (D31)", HM3.keep, 45360);
check("handyman case C quote, 1.5 h at $90 (I43)", HM3.quote, 135);

// #20 day-rate view (Calculator tab recalculated in LibreOffice Oct 13, 2026, hours = days x hours a day)
const DR1 = P.dayRate({ takeHome: 65000, taxRate: 25, expenses: 14000, weeks: 48, daysPerWeek: 5, hoursPerDay: 10, billableShare: 55, checkDayRate: 450 });
check("#20 day: hourly rate I21", DR1.rate, 76.26);
check("#20 day: day rate", DR1.dayRate, 762.63);
check("#20 day: billable days", DR1.billableDays, 132);
check("#20 day: keep at $450 a day D31", DR1.keep, 34050);
check("#20 day: short by", DR1.shortBy, 30950);
const DR2 = P.dayRate({ takeHome: 50000, taxRate: 20, expenses: 9000, weeks: 46, daysPerWeek: 4, hoursPerDay: 8, billableShare: 60, checkDayRate: 600 });
check("#20 day 4x8: hourly I21", DR2.rate, 80.96);
check("#20 day 4x8: day rate", DR2.dayRate, 647.64);
check("#20 day 4x8: billable days", DR2.billableDays, 110.4);
check("#20 day 4x8: keep at $600 D31", DR2.keep, 45792);
const DR0 = P.dayRate({ takeHome: 65000, taxRate: 25, expenses: 14000, weeks: 0, daysPerWeek: 5, hoursPerDay: 10, billableShare: 55, checkDayRate: 450 });
check("#20 day 0 weeks: day rate", DR0.dayRate, 0);
check("#20 day 0 weeks: keep D31", DR0.keep, -14000);
const DRb = P.dayRate({ takeHome: "", taxRate: "", expenses: "", weeks: "", daysPerWeek: "", hoursPerDay: "", billableShare: "", checkDayRate: "" });
check("#20 day blank: day rate", DRb.dayRate, 0);
// #14 Cleaning Business Starter Kit, 3 Price Sheet (recalculated in LibreOffice Oct 13, 2026)
const CLN = { takeHome: 48000, weeks: 48, hours: 45, paidShare: 70, monthlyCosts: 505, incomeTax: 12, margin: 15, perMile: 0.76, mph: 25,
  minPer1000: 90, miles: 16, minCharge: 120 };
check("#14 break-even I21", P.cleaningSqft(Object.assign({}, CLN, { sqft: 2000 })).breakEven, 46.98);
[[1000, 145, 135, 125, 215, 240], [1500, 185, 170, 160, 285, 325], [2000, 225, 205, 195, 360, 405],
 [2500, 270, 245, 230, 435, 490], [3000, 310, 280, 265, 505, 575], [3500, 350, 315, 300, 580, 655]].forEach(function (t) {
  const g = function (sv, fq) { return P.cleaningSqft(Object.assign({}, CLN, { sqft: t[0], serviceType: sv, freq: fq })).visit; };
  check("#14 " + t[0] + " one-time", g(0, 0), t[1]); check("#14 " + t[0] + " every 2 weeks", g(0, 2), t[2]);
  check("#14 " + t[0] + " weekly", g(0, 3), t[3]); check("#14 " + t[0] + " deep", g(1, 0), t[4]); check("#14 " + t[0] + " move-out", g(2, 0), t[5]);
});
check("#14 2,000 per sq ft every 2 weeks", P.cleaningSqft(Object.assign({}, CLN, { sqft: 2000, freq: 2 })).perSqFt, 0.1025);
const CLN2 = Object.assign({}, CLN, { takeHome: 60000, margin: 20, minPer1000: 110, minCharge: 150 });
[[1000, 205, 185, 315], [2000, 340, 310, 545], [3500, 535, 485, 895]].forEach(function (t) {
  const g = function (sv, fq) { return P.cleaningSqft(Object.assign({}, CLN2, { sqft: t[0], serviceType: sv, freq: fq })).visit; };
  check("#14 changed " + t[0] + " one-time", g(0, 0), t[1]); check("#14 changed " + t[0] + " every 2 weeks", g(0, 2), t[2]);
  check("#14 changed " + t[0] + " deep", g(1, 0), t[3]);
});
check("#14 0 weeks: minimum charge", P.cleaningSqft(Object.assign({}, CLN, { weeks: 0, sqft: 3500 })).visit, 120);
check("#14 blank: per sq ft", P.cleaningSqft({}).perSqFt, 0);

// #25 Inventory Tracker, 1 Items recalculated in LibreOffice Oct 16, seen as a markup (markup = (G - L) / L)
const MK = P.markup({ unitCost: 7.5, markupPct: 220, feePct: 10, checkPrice: "" });
check("#25 markup: lavender price G16", MK.price, 24);
check("#25 markup: lavender profit per unit M16", MK.ppu, 14.1);
check("#25 markup: lavender gross margin", MK.margin, 0.6875);
check("#25 markup: lavender net margin", MK.netMargin, 0.5875);
const MKc = P.markup({ unitCost: 12.5, markupPct: 204, feePct: 10, checkPrice: 38 });
check("#25 markup: citrus price G18", MKc.price, 38);
check("#25 markup: citrus profit per unit M18", MKc.ppu, 21.7);
check("#25 markup: citrus check markup", MKc.checkMarkup, 2.04);
const MKl = P.markup({ unitCost: 1.7, markupPct: 100, feePct: 10, checkPrice: 5 });
check("#25 markup: lip balm check profit M25", MKl.checkProfit, 2.8);
check("#25 markup: lip balm at 100% markup", MKl.price, 3.4);
check("#25 markup: below cost loss", P.markup({ unitCost: 7.5, markupPct: -20, feePct: 10 }).loss, 2.1);
check("blank markup: none flag", P.markup({}).none, 1);
// #28 Profit and Loss Template, 2 Statement recalculated in LibreOffice Oct 16 (September G30, G36, G41, G57, G59)
const BE = P.breakEven({ sales: 3325, variable: 2040, fixed: 771.99, avgSale: "" });
check("#28 Sep net profit G59", BE.profit, 513.01);
check("#28 Sep break-even sales", BE.be, 1997.56);
check("#28 Sep contribution margin", BE.cm, 0.386466);
check("#28 Sep cushion", BE.cushion, 1327.44);
const BEa = P.breakEven({ sales: 4550, variable: 2495, fixed: 693.09, avgSale: 25 });
check("#28 Aug net profit H59 (Aug)", BEa.profit, 1361.91);
check("#28 Aug break-even sales", BEa.be, 1534.58);
check("#28 Aug orders at $25", BEa.orders, 62);
check("#28 variable over sales: never", P.breakEven({ sales: 1000, variable: 1000, fixed: 500 }).never, 1);
check("blank break-even: none flag", P.breakEven({}).none, 1);

// #12 Craft Fair Profit Calculator, 2 Products recalculated in LibreOffice Oct 16 (rows 24, 25, 28; card cost per $1 0.0217)
const HP = P.handmadePrice({ materials: 6.5, minutes: 15, rate: 20, packaging: 0.6, feePct: 2.17, price: 22 });
check("#12 candle labor I25", HP.labor, 5);
check("#12 candle unit cost J25", HP.uc, 12.1);
check("#12 candle card cost K25", HP.fees, 0.4774);
check("#12 candle contribution L25", HP.ppu, 9.4226);
check("#12 candle margin M25", HP.margin, 0.4283);
check("#12 candle x2 price N25", HP.x2, 23);
check("#12 candle below formula O25", HP.below, 1);
check("#12 candle lowest price", HP.floor, 12.3684);
const HPs = P.handmadePrice({ materials: 1.6, minutes: 6, rate: 20, packaging: 0.25, feePct: 2.17, price: 8 });
check("#12 soap unit cost J24", HPs.uc, 3.85); check("#12 soap contribution L24", HPs.ppu, 3.9764);
check("#12 soap x2 price N24", HPs.x2, 7.2); check("#12 soap ok O24", HPs.ok, 1);
const HPg = P.handmadePrice({ materials: 10.2, minutes: 30, rate: 20, packaging: 2.5, feePct: 2.17, price: 38 });
check("#12 gift box unit cost J28", HPg.uc, 22.7); check("#12 gift box contribution L28", HPg.ppu, 14.4754);
check("#12 gift box x2 price N28", HPg.x2, 40.4); check("#12 gift box below formula O28", HPg.below, 1);
check("#12 changed: $0 rate drops labor", P.handmadePrice({ materials: 6.5, minutes: 15, rate: 0, packaging: 0.6, feePct: 2.17, price: 22 }).uc, 7.1);
check("#12 price under cost: loss", P.handmadePrice({ materials: 6.5, minutes: 15, rate: 20, packaging: 0.6, feePct: 0, price: 10 }).loss, 2.1);
check("blank handmade: none flag", P.handmadePrice({}).none, 1);
check("handmade 100% fees stays finite", P.handmadePrice({ materials: 5, feePct: 100 }).floor, 500);
// Lead cost per won job: hand-worked, every figure is the owner's own (no workbook behind this page)
const LC = P.leadCost({ spend: "1,200", leads: 40, quotes: 18, jobs: 6, avgJob: 280, jobCost: 110 }, [39, 29]);
check("lead cost per lead", LC.cpl, 30); check("lead cost per quote", LC.cpq, 66.6667); check("lead cost per won job", LC.cpj, 200);
check("lead job profit before leads", LC.perJob, 170); check("lead profit after lead spend", LC.profit, -180);
check("lead loss per job", LC.afterLead, -30); check("lead win rate", LC.winRate, 0.3333); check("lead break-even jobs", LC.breakEvenJobs, 8);
check("lead $39 list covered by 1 job", LC.cover0, 1); check("lead loss flag", LC.neg, 1);
check("lead $39 list, $15 job profit: 3 jobs", P.leadCost({ avgJob: 40, jobCost: 25 }, [39]).cover0, 3);
check("lead no jobs: flag, no divide by zero", P.leadCost({ spend: 500, leads: 10 }).noJobs + P.leadCost({ spend: 500, leads: 10 }).cpj, 1);
check("lead blank: none", P.leadCost({}).none, 1);
check("lead jobs over quotes: odd", P.leadCost({ spend: 100, leads: 5, quotes: 2, jobs: 3 }).odd, 1);
// Amazon DD+7 (help page G202124090, read Oct 24, 2026): sold Jan 1, delivered Jan 6, available Jan 14 = day 14
const AZ = P.payoutGap({ sales: 1000, fulfil: 0, deliverDays: 5, schedule: 1, bankDays: 0, cash: 0, costs: 0 });
check("DD+7 Amazon example: available on day 14", AZ.first, 14);
const DS = P.payoutGap({ sales: 1000, fulfil: 0, deliverDays: 3, schedule: 0, nextPayout: 14, bankDays: 1, cash: 10000, costs: 700 });
check("DD+7 14-day: fastest order to bank", DS.fastest, 12); check("DD+7 14-day: slowest", DS.slowest, 25);
check("DD+7 14-day: held peak", DS.heldMax, 25000); check("DD+7 14-day: held floor", DS.heldMin, 12000);
check("DD+7 14-day: first money day 15", DS.first, 15); check("DD+7 14-day: low point", DS.low, -6600);
check("DD+7 14-day: low on day 28", DS.lowDay, 28); check("DD+7 14-day: cash needed", DS.need, 6600);
const DD = P.payoutGap({ sales: 1000, fulfil: 0, deliverDays: 3, schedule: 1, bankDays: 1, cash: 10000, costs: 700 });
check("DD+7 daily: order to bank", DD.slowest, 12); check("DD+7 daily: held", DD.heldMax, 12000); check("DD+7 daily: low", DD.low, 1600);
const DM = P.payoutGap({ sales: 1000, fulfil: 1, tracked: 0, deliverDays: 4, eddDays: 7, schedule: 0, nextPayout: 14, bankDays: 5, cash: 10000, costs: 700 });
check("DD+7 merchant, no valid tracking: uses latest EDD", DM.dateDays, 7); check("DD+7 merchant slowest", DM.slowest, 33);
check("DD+7 merchant tracked: uses delivery", P.payoutGap({ sales: 1, fulfil: 1, tracked: 1, deliverDays: 4, eddDays: 7 }).dateDays, 4);
check("DD+7 blank: no sales flag", P.payoutGap({}).noSales, 1);
const DF = P.payoutGap({ sales: 500, fulfil: 0, deliverDays: 3, schedule: 0, nextPayout: 14, bankDays: 1, cash: 10000, costs: 700 });
check("DD+7 spend above sales: falling, no short or ok", DF.falling * 10 + DF.short + DF.ok, 10);
check("DD+7 no sales with spend: falling", P.payoutGap({ costs: 100, cash: 1000 }).falling, 1);

process.exit(fails ? 1 : 0);
