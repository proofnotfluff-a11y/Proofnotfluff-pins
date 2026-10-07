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
// blank inputs never produce NaN or Infinity
const b = P.service({});
const bh = P.hourly({});
const bc = P.cashflow({});
const bad = [...Object.values(b), ...Object.values(bh), ...Object.values(bc)].filter(v => !isFinite(v));
if (bad.length) { fails++; console.log("FAIL blank inputs give non-finite values"); } else console.log("ok   blank inputs stay finite");
process.exit(fails ? 1 : 0);
