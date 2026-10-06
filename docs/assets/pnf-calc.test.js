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
// blank inputs never produce NaN or Infinity
const b = P.service({});
const bh = P.hourly({});
const bad = [...Object.values(b), ...Object.values(bh)].filter(v => !isFinite(v));
if (bad.length) { fails++; console.log("FAIL blank inputs give non-finite values"); } else console.log("ok   blank inputs stay finite");
process.exit(fails ? 1 : 0);
