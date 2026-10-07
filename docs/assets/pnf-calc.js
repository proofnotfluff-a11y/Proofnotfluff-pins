/* ProofNotFluff free calculators. The maths is the same as the paid workbooks:
   hourly: engines/hourly-rate-quick-calculator (#20); service: engines/service-pricing (#13 and its trade editions);
   cashflow: the premium 13-Week E-commerce Cash Flow workbook's ending-cash row.
   Tested against the workbooks' own example outputs in docs/assets/pnf-calc.test.js. */
(function (root) {
  "use strict";
  var SE_RATE = 0.153, SE_BASE = 0.9235; // IRS Topic 554, Schedule SE (checked Oct 6, 2026)

  function num(v) { var n = parseFloat(String(v).replace(/[$,%\s]/g, "")); return isFinite(n) ? n : 0; }
  function ceilTo(x, step) { return Math.ceil(x / step - 1e-9) * step; }

  // #20 Hourly Rate Quick Calculator
  function hourly(i) {
    var takeHome = num(i.takeHome), tax = num(i.taxRate) / 100, expenses = num(i.expenses);
    var weeks = num(i.weeks), hours = num(i.hours), share = num(i.billableShare) / 100;
    var revenue = (tax < 1 ? takeHome / (1 - tax) : 0) + expenses;
    var worked = weeks * hours, billable = worked * share;
    var rate = billable > 0 ? revenue / billable : 0;
    var check = num(i.checkRate);
    var checkRevenue = check * billable;
    var profit = checkRevenue - expenses;
    var keep = profit - Math.max(0, profit) * tax;
    return {
      revenue: revenue, worked: worked, billable: billable, rate: rate, rateCard: ceilTo(rate, 5),
      taxSetAside: tax < 1 ? takeHome / (1 - tax) - takeHome : 0,
      checkRevenue: checkRevenue, keep: keep, keepPerHour: worked > 0 ? keep / worked : 0,
      shortBy: takeHome - keep
    };
  }

  // #13 Service Pricing Calculator engine (also every trade edition)
  function service(i) {
    var takeHome = num(i.takeHome), weeks = num(i.weeks), hours = num(i.hours), paid = num(i.paidShare) / 100;
    var income = num(i.incomeTax) / 100, margin = num(i.margin) / 100, monthly = num(i.monthlyCosts);
    var perMile = num(i.perMile), mph = num(i.mph);
    var denom = 1 - SE_RATE * SE_BASE - income;
    var profit = denom > 0 ? takeHome / denom : 0;
    var costsYear = monthly * 12;
    var paidHours = weeks * hours * paid;
    var be = paidHours > 0 ? (profit + costsYear) / paidHours : 0;
    var target = margin < 1 ? be / (1 - margin) : 0;
    var guess = weeks * hours > 0 ? takeHome / (weeks * hours) : 0;
    var jh = num(i.jobHours), people = num(i.people), supplies = num(i.supplies), miles = num(i.miles);
    var drive = mph > 0 ? miles / mph : 0;
    var labor = jh * people * be, driveCost = drive * people * be, vehicle = miles * perMile;
    var floor = labor + driveCost + vehicle + supplies;
    var quote = margin < 1 ? ceilTo(floor / (1 - margin), 5) : 0;
    var worked = (jh + drive) * people;
    return {
      profit: profit, costsYear: costsYear, paidHours: paidHours, breakEven: be, target: target, guess: guess,
      drive: drive, labor: labor, driveCost: driveCost, vehicle: vehicle, supplies: supplies, floor: floor,
      quote: quote, quoteProfit: quote - floor, perHourWorked: worked > 0 ? (quote - vehicle - supplies) / worked : 0
    };
  }

  // Premium 13-Week E-commerce Cash Flow, lite: one weekly cash-in and cash-out figure and one PO payment.
  // Same maths as the workbook's ending-cash row with a single channel paid the week of the sale.
  function cashflow(i) {
    var open = num(i.openingCash), cin = num(i.weeklyIn), cout = num(i.weeklyOut);
    var po = num(i.poAmount), wk = Math.round(num(i.poWeek));
    var r = {}, cash = open, low = Infinity, lowWeek = 1;
    for (var t = 1; t <= 13; t++) {
      cash += cin - cout - (t === wk ? po : 0);
      r["end" + t] = cash;
      if (cash < low - 1e-9) { low = cash; lowWeek = t; }
    }
    r.lowest = low; r.lowWeek = lowWeek; r.gap = Math.max(0, -low); r.end13 = cash; r.perWeek = cin - cout;
    r.poInWindow = (wk >= 1 && wk <= 13) ? 1 : 0;
    return r;
  }

  function money(x, cents) {
    var neg = x < 0; x = Math.abs(x);
    var s = cents === false ? Math.round(x).toLocaleString("en-US")
                            : x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    return (neg ? "-$" : "$") + s;
  }

  // Wire a page: every [data-in] input feeds the model; every [data-out] element shows a result.
  function wire(form, model) {
    var outs = document.querySelectorAll("[data-out]");
    function read() {
      var vals = {};
      form.querySelectorAll("[data-in]").forEach(function (el) { vals[el.getAttribute("data-in")] = el.value; });
      return vals;
    }
    function render() {
      var r = model(read());
      outs.forEach(function (el) {
        var key = el.getAttribute("data-out"), fmt = el.getAttribute("data-fmt") || "money";
        var v = r[key];
        el.textContent = fmt === "week" ? "Week " + v : fmt === "int" ? Math.round(v).toLocaleString("en-US")
                       : fmt === "hrs" ? v.toFixed(2) + " hrs"
                       : fmt === "money0" ? money(v, false) : money(v);
        el.classList.toggle("neg", v < 0);
      });
      document.querySelectorAll("[data-show-if]").forEach(function (el) {
        var cond = el.getAttribute("data-show-if").split(/\s*(<|>)\s*/);
        var a = r[cond[0]], b = num(cond[2]);
        el.hidden = !(cond[1] === "<" ? a < b : a > b);
      });
    }
    form.addEventListener("input", render);
    form.addEventListener("submit", function (e) { e.preventDefault(); render(); });
    render();
  }

  var api = { hourly: hourly, service: service, cashflow: cashflow, money: money, ceilTo: ceilTo, wire: wire };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.PNF = api;
})(this);
