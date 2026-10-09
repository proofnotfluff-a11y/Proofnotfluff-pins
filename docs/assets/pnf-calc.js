/* ProofNotFluff free calculators. The maths is the same as the paid workbooks:
   hourly: engines/hourly-rate-quick-calculator (#20); service: engines/service-pricing (#13 and its trade editions);
   cashflow: the premium 13-Week E-commerce Cash Flow workbook's ending-cash row;
   etsyFees: engines/etsy-true-profit (#5); craftFair: engines/craft-fair-profit (#12);
   strNightly: engines/str-nightly-pricing (#9); debtPayoff: engines/debt-payoff-tracker (#16);
   shippingCost: engines/shipping-true-cost (#7); reorderPoint: engines/cash-aware-reorder-planner (#6);
   strBreakEven: the #9 fee stack (engines/str-nightly-pricing), break-even nights for the STR lite page;
   rentalCashFlow: engines/rental-property (#19), 4 Property P&L profit and cash flow rows.
   businessExpense: engines/business-expense-tracker (#18), Summary tab income, expenses and profit rows.
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

  // #5 True Profit System for Etsy Sellers: the per-sale maths of the Listings tab, with sales tax added to the
  // processing base and each fee rounded to the cent so the lines add up to the total shown. cap: the Offsite Ads cap.
  function etsyFees(i, cap) {
    if (cap === undefined) cap = 100;
    var price = num(i.price), ship = num(i.ship), tax = num(i.tax), cost = num(i.cost), label = num(i.label);
    function c(x) { return Math.round(x * 100 + 1e-6) / 100; }
    var rate = num(i.adsRate) / 100, rev = price + ship, tf = c(num(i.tfRate) / 100 * rev),
        pf = c(num(i.procRate) / 100 * (rev + tax) + num(i.procFixed)), lf = c(num(i.listFee));
    var ads = c(Math.min(rate * rev, cap)), fees = tf + pf + lf + ads, payout = rev - fees, profit = payout - cost - label,
        adsIf = c(Math.min(0.15 * rev, cap));
    return { revenue: rev, tf: tf, pf: pf, lf: lf, ads: ads, fees: fees, payout: payout, cost: cost, label: label, profit: profit,
      loss: -profit, margin: rev > 0 ? profit / rev : 0, feeShare: rev > 0 ? fees / rev : 0, adsOff: rate > 0 ? 0 : 1,
      adsIf: adsIf, profitIfAds: profit - adsIf };
  }

  // #12 Craft Fair Profit Calculator, Break-Even tab: card cost per $1 = card share x (percent + flat / average spend);
  // pieces round up to whole pieces.
  function craftFair(i) {
    var booth = num(i.booth), other = num(i.other), price = num(i.price), cpp = num(i.cpp), target = num(i.target);
    var avg = num(i.avgSale), perDollar = num(i.cardShare) / 100 * (num(i.cardPct) / 100 + (avg > 0 ? num(i.cardFlat) / avg : 0));
    var total = booth + other, cardPer = price * perDollar, contrib = price - cpp - cardPer, ok = contrib > 1e-9;
    var be = ok ? Math.max(0, Math.ceil(total / contrib - 1e-9)) : 0, tg = ok ? Math.max(0, Math.ceil((total + target) / contrib - 1e-9)) : 0;
    return { booth: booth, other: other, total: total, price: price, cpp: cpp, cardPer: cardPer, contrib: contrib, bePieces: be,
      beSales: be * price, tgtPieces: tg, tgtSales: tg * price, tgtProfit: ok ? tg * contrib - total : 0,
      boothShare: total > 0 ? booth / total : 0, never: ok ? 0 : 1 };
  }

  var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

  // #9 STR Nightly Pricing Worksheet: each month's multiplier is that month's value over the 12-month average
  // (2 Seasonality L), its base rate is ROUND(base x multiplier, 0) (M), and the nightly rate is the higher of that
  // and the floor (4 Stay Discounts E, "AT FLOOR" when the floor wins). Payout per night is rate x (1 - host fee),
  // the 5 Fee Reset maths. Inputs h1..h12: last year's revenue (or occupancy, or a starter curve) per month.
  function strNightly(i) {
    var base = num(i.base), floor = num(i.floor), fee = num(i.fee) / 100, cleaning = num(i.cleaning), minStay = Math.max(0, Math.round(num(i.minStay)));
    var h = [], sum = 0, m;
    // compensated sum, so twelve multipliers that average 1.00 give exactly 1, as the spreadsheet's AVERAGE does
    var comp = 0;
    for (m = 1; m <= 12; m++) {
      var x = Math.max(0, num(i["h" + m])), t = sum + x;
      comp += Math.abs(sum) >= Math.abs(x) ? (sum - t) + x : (x - t) + sum; sum = t; h.push(x);
    }
    sum += comp;
    var avg = sum / 12, ok = avg > 0;
    var r = { valid: ok ? 1 : 0, hasZero: ok && h.indexOf(0) >= 0 ? 1 : 0, base: base, floor: floor, fee: fee, cleaning: cleaning, minStay: minStay, atFloor: 0 };
    var hi = 0, lo = 0;
    for (m = 0; m < 12; m++) {
      var mult = ok ? h[m] / avg : 0, b = Math.floor(base * mult + 0.5), night = Math.max(b, floor);
      r["mult" + (m + 1)] = mult; r["base" + (m + 1)] = b; r["night" + (m + 1)] = night;
      r["pay" + (m + 1)] = night * (1 - fee);
      r["flag" + (m + 1)] = ok && b < floor ? "Floor" : "";
      if (ok && b < floor) r.atFloor++;
      if (r["mult" + (m + 1)] > r["mult" + (hi + 1)] + 1e-12) hi = m;
      if (r["mult" + (m + 1)] < r["mult" + (lo + 1)] - 1e-12) lo = m;
    }
    r.hiMonth = ok ? MONTHS[hi] : "-"; r.hiMult = r["mult" + (hi + 1)]; r.hiNight = r["night" + (hi + 1)]; r.hiPay = r["pay" + (hi + 1)];
    r.loMonth = ok ? MONTHS[lo] : "-"; r.loMult = r["mult" + (lo + 1)]; r.loBase = r["base" + (lo + 1)]; r.loNight = r["night" + (lo + 1)];
    r.loPay = r["pay" + (lo + 1)]; r.loHeld = ok && r.loBase < floor ? 1 : 0; r.loLift = r.loNight - r.loBase;
    r.stayNights = minStay * r.loNight; r.stayTotal = r.stayNights + cleaning;
    return r;
  }

  // #16 Debt Payoff Tracker: the 4 Snowball and 5 Avalanche plan grids and the minimums-only columns of 2 Debts.
  // Each month: every balance grows by APR / 12 and is rounded to the cent, every minimum is paid, the rest of the monthly
  // amount (minimums plus extra) goes to the debts in plan order, and a paid-off debt's minimum rolls into that pool.
  // Order is set once from today's balances: Snowball smallest balance first, Avalanche highest APR first (ties: the
  // earlier debt). Plans run up to 240 months. Minimums only: NPER per debt, rounded up; "never" when a minimum does not
  // cover a month's interest. Inputs b1..b5 balance, a1..a5 APR (%), m1..m5 minimum, extra.
  function round2(x) { return (x < 0 ? -1 : 1) * Math.round(Math.abs(x) * 100 + 1e-7) / 100; }
  function debtPlan(debts, monthly, order) {
    var n = debts.length, left = debts.map(function (d) { return d.bal; }), interest = 0, months = 0, k;
    var off = debts.map(function () { return 0; }), still = left.reduce(function (a, b) { return a + b; }, 0) > 0.005;
    if (!still) return { months: 0, interest: 0, never: 0, off: off };
    for (var m = 1; m <= 240; m++) {
      var due = [], room = [], prevSum = 0, dueSum = 0, paidMin = 0;
      for (k = 0; k < n; k++) {
        prevSum += left[k];
        due[k] = round2(left[k] * (1 + debts[k].apr / 12));
        room[k] = due[k] - Math.min(due[k], debts[k].min);
        dueSum += due[k]; paidMin += due[k] - room[k];
      }
      var pool = Math.max(0, monthly - paidMin), before = 0, total = 0;
      for (var j = 0; j < order.length; j++) {
        k = order[j];
        left[k] = round2(room[k] - Math.min(room[k], Math.max(0, pool - before)));
        before += room[k];
      }
      for (k = 0; k < n; k++) {
        if (order.indexOf(k) < 0) left[k] = room[k];
        total += left[k];
        if (left[k] > 0.005) off[k] = m + 1;
      }
      interest += dueSum - prevSum;
      if (total > 0.005) months = m;
    }
    var never = months >= 240 ? 1 : 0;
    return { months: never ? 0 : months + 1, interest: never ? 0 : interest, never: never,
      off: off.map(function (x, k) { return debts[k].bal > 0.005 ? (x === 0 ? 1 : x) : 0; }) };
  }
  function debtPayoff(i) {
    var debts = [], k;
    for (k = 1; k <= 5; k++) debts.push({ bal: Math.max(0, num(i["b" + k])), apr: Math.max(0, num(i["a" + k])) / 100, min: Math.max(0, num(i["m" + k])) });
    var active = [], minSum = 0, owed = 0;
    debts.forEach(function (d, k) { if (d.bal > 0.005) { active.push(k); minSum += d.min; owed += d.bal; } });
    var extra = Math.max(0, num(i.extra)), monthly = minSum + extra;
    var snowOrder = active.slice().sort(function (a, b) { return debts[a].bal - debts[b].bal || a - b; });
    var avaOrder = active.slice().sort(function (a, b) { return debts[b].apr - debts[a].apr || a - b; });
    var sno = debtPlan(debts, monthly, snowOrder), ava = debtPlan(debts, monthly, avaOrder);
    // minimums only, no extra and no roll-over (2 Debts P and Q)
    var minMonths = 0, minInt = 0, minNever = 0, minOff = [];
    debts.forEach(function (d) {
      if (d.bal <= 0.005) { minOff.push(0); return; }
      var r = d.apr / 12;
      if (d.min <= 0 || d.min <= d.bal * r) { minNever = 1; minOff.push(-1); return; }
      var nper = r === 0 ? d.bal / d.min : Math.log(d.min / (d.min - r * d.bal)) / Math.log(1 + r);
      var mo = Math.ceil(nper - 1e-9);
      minOff.push(mo); minMonths = Math.max(minMonths, mo); minInt += r === 0 ? 0 : Math.max(0, d.min * nper - d.bal);
    });
    var res = { owed: owed, count: active.length, minSum: minSum, extra: extra, monthly: monthly,
      snoMonths: sno.months, snoInt: sno.interest, snoNever: sno.never,
      avaMonths: ava.months, avaInt: ava.interest, avaNever: ava.never,
      minMonths: minNever ? 0 : minMonths, minInt: minNever ? 0 : minInt, minNever: minNever };
    res.avaSaved = !minNever && !ava.never ? minInt - ava.interest : 0;
    res.snoSaved = !minNever && !sno.never ? minInt - sno.interest : 0;
    res.savedOk = !minNever && !ava.never && active.length ? 1 : 0;
    res.avaVsSno = !ava.never && !sno.never ? sno.interest - ava.interest : 0;
    res.empty = active.length ? 0 : 1;
    for (k = 0; k < 5; k++) {
      var on = debts[k].bal > 0.005;
      res["ava" + (k + 1)] = !on ? "-" : ava.never ? "Over 20 yrs" : "Month " + ava.off[k];
      res["sno" + (k + 1)] = !on ? "-" : sno.never ? "Over 20 yrs" : "Month " + sno.off[k];
      res["min" + (k + 1)] = !on ? "-" : minOff[k] < 0 ? "Never" : "Month " + minOff[k];
    }
    return res;
  }

  // #7 Shipping True-Cost Calculator, 1 Parcel Costs: true cost per parcel = postage + box + filler + tape + label
  // + packing minutes / 60 x hourly rate; shortfall = shipping charged - true cost ("Under-recovered" below -$0.005).
  // The marketplace fee on the shipping you charge is the 5 Dashboard fee column's share for shipping (fee % x shipping).
  function shippingCost(i) {
    var charged = num(i.charged), postage = num(i.postage), box = num(i.box), filler = num(i.filler), tape = num(i.tape),
        labelPaper = num(i.labelPaper), minutes = num(i.minutes), hourly = num(i.hourly), feePct = num(i.feePct) / 100;
    var materials = box + filler + tape + labelPaper, labor = minutes / 60 * hourly;
    var parcel = postage + materials + labor, shortfall = charged - parcel, fees = feePct * charged;
    var total = parcel + fees, net = charged - total;
    var breakEven = feePct < 1 ? Math.ceil(parcel / (1 - feePct) * 100 - 1e-6) / 100 : 0;
    return { charged: charged, postage: postage, materials: materials, labor: labor, parcel: parcel, shortfall: shortfall,
      fees: fees, total: total, net: net, under: -net, breakEven: breakEven, isUnder: net < -0.005 ? 1 : 0,
      before: shortfall < -0.005 ? 1 : 0, postageShare: parcel > 0 ? postage / parcel : 0, underPer100: -net * 100 };
  }

  // #6 Cash-Aware Reorder Planner, one SKU: the 2 SKU List reorder point, order-up-to, days of stock, status and
  // days-until-reorder columns, and the units the 30-day order cost uses. Overstock at 120 days, the workbook default.
  function reorderPoint(i) {
    var daily = num(i.daily), lead = num(i.lead), safety = num(i.safety) / 100, cycle = num(i.cycle);
    var onHand = num(i.onHand), onOrder = num(i.onOrder), cost = num(i.unitCost), over = 120;
    var sales = daily > 0;
    var rop = sales ? daily * lead * (1 + safety) : 0;
    var upTo = sales ? daily * (lead + cycle) * (1 + safety) : 0;
    var days = sales ? onHand / daily : 0;
    var until = sales ? (onHand + onOrder - rop) / daily : 0;
    var status = !sales ? "NO SALES" : (days < lead && onOrder === 0) ? "STOCKOUT RISK"
               : (onHand + onOrder <= rop) ? "REORDER" : (days >= over) ? "OVERSTOCK" : "OK";
    var orderNow = (status === "REORDER" || status === "STOCKOUT RISK");
    var units = orderNow ? Math.max(0, Math.ceil(upTo - onHand - onOrder - 1e-9))
              : (sales && until <= 30) ? Math.ceil(upTo - rop - 1e-9) : 0;
    var words = { "NO SALES": "No sales to plan from", "STOCKOUT RISK": "Order now: stock runs out before an order lands",
                  "REORDER": "Order now: you are at your reorder point", "OVERSTOCK": "Overstocked: 120+ days of stock",
                  "OK": "OK for now" }[status];
    return { rop: rop, upTo: upTo, days: days, until: until, status: status, statusText: words,
      orderNow: orderNow ? 1 : 0, soon: (!orderNow && sales && until <= 30) ? 1 : 0, later: (!orderNow && sales && until > 30) ? 1 : 0,
      noSales: sales ? 0 : 1, units: units, orderCost: units * cost, untilShow: Math.max(0, until),
      shortDays: sales && days < lead ? lead - days : 0, risk: status === "STOCKOUT RISK" ? 1 : 0, atRop: status === "REORDER" ? 1 : 0 };
  }

  // STR break-even nights (free lite page; fee stack from engines/str-nightly-pricing #9: the platform fee comes off the nightly rate)
  function strBreakEven(i) {
    var fixed = num(i.fixed), rate = num(i.rate), kept = num(i.cleanKept), stay = num(i.stay), fee = num(i.fee) / 100;
    var month = 365 / 12;
    var perStayClean = stay > 0 ? kept / stay : 0;
    var perNight = rate * (1 - fee) + perStayClean;
    var exact = perNight > 0 ? fixed / perNight : 0;
    var nights = perNight > 0 ? Math.ceil(exact - 1e-9) : 0;
    var half = month / 2;
    var rateAtHalf = (1 - fee) > 0 ? Math.max(0, (fixed / half - perStayClean) / (1 - fee)) : 0;
    var never = perNight <= 0 && fixed > 0 ? 1 : 0;
    var over = !never && nights > month ? 1 : 0;
    return { perNight: perNight, exact: exact, nights: nights, occupancy: month > 0 ? nights / month : 0,
      stays: stay > 0 ? nights / stay : 0, perStay: perNight * stay, feePerNight: rate * fee, cleanPerNight: perStayClean,
      rateAtHalf: rateAtHalf, never: never, over: over, ok: (!never && !over && fixed > 0) ? 1 : 0, noCosts: fixed > 0 ? 0 : 1 };
  }

  // #19 Rental Property Spreadsheet, 4 Property P&L: profit before depreciation = money in less Schedule E expenses
  // (mortgage interest included); cash flow = profit less mortgage principal and capital improvements.
  function rentalCashFlow(i) {
    var income = num(i.income), expenses = num(i.expenses), interest = num(i.interest);
    var principal = num(i.principal), improve = num(i.improve), months = Math.round(num(i.months));
    var profit = income - expenses - interest;
    var cash = profit - principal - improve;
    var m = months > 0 ? months : 0;
    return { income: income, expenses: expenses, interest: interest, principal: principal, improve: improve, months: m,
      outTotal: expenses + interest + principal + improve, notExpense: principal + improve,
      profit: profit, cash: cash, cashMonth: m > 0 ? cash / m : 0, profitMonth: m > 0 ? profit / m : 0,
      keptShare: income > 0 ? cash / income : 0, down: cash < 0 ? -cash : 0,
      pos: income > 0 && cash > 0 ? 1 : 0, neg: income > 0 && cash < 0 && profit <= 0 ? 1 : 0, even: income > 0 && cash === 0 ? 1 : 0,
      gap: income > 0 && profit > 0 && cash < 0 ? 1 : 0, noIncome: income > 0 ? 0 : 1, noMonths: income > 0 && m === 0 ? 1 : 0 };
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
        el.textContent = fmt === "text" ? String(v) : fmt === "mult" ? v.toFixed(2) + "x"
                       : fmt === "week" ? "Week " + v : fmt === "int" ? Math.round(v).toLocaleString("en-US")
                       : fmt === "hrs" ? v.toFixed(2) + " hrs"
                       : fmt === "dec1" ? (Math.round(v * 10) / 10).toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 })
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

  // Runs after each render, for outputs wire has no format for: data-pct (a share shown as a percent) and data-never
  // (text shown instead of a number when the flag named by data-never-if, default "never", is set).
  function after(f, M) {
    function go() {
      var v = {};
      f.querySelectorAll("[data-in]").forEach(function (e) { v[e.getAttribute("data-in")] = e.value; });
      var r = M(v);
      document.querySelectorAll("[data-pct]").forEach(function (e) {
        var x = r[e.getAttribute("data-pct")];
        e.textContent = (isFinite(x) ? (x * 100).toFixed(1) : "0.0") + "%"; e.classList.toggle("neg", x < 0);
      });
      document.querySelectorAll("[data-never]").forEach(function (e) {
        if (r[e.getAttribute("data-never-if") || "never"]) { e.textContent = e.getAttribute("data-never"); e.classList.add("neg"); }
      });
    }
    f.querySelectorAll("select").forEach(function (s) { s.addEventListener("change", function () { f.dispatchEvent(new Event("input")); }); });
    f.addEventListener("input", go); go();
  }

  // #18 One-Tab Business Expense Tracker: Summary tab, Income after refunds, Total expenses,
  // Profit before inventory count, and the rows logged but kept out of profit.
  function businessExpense(i) {
    var sales = num(i.sales), other = num(i.otherIncome), refunds = num(i.refunds), inv = num(i.inventory);
    var lines = [num(i.fees), num(i.rent), num(i.supplies), num(i.ads), num(i.car), num(i.otherExp), num(i.more)];
    var expenses = lines.reduce(function (a, b) { return a + b; }, 0);
    var equipment = num(i.equipment), draw = num(i.draw), months = Math.round(num(i.months));
    var income = sales + other - refunds;
    var profit = income - inv - expenses;
    var m = months > 0 ? months : 0;
    var costs = inv + expenses;
    return { income: income, refunds: refunds, inventory: inv, expenses: expenses, costs: costs, profit: profit, months: m,
      expMonth: m > 0 ? expenses / m : 0, profitMonth: m > 0 ? profit / m : 0, costsMonth: m > 0 ? costs / m : 0,
      expShare: income > 0 ? expenses / income : 0, kept: income > 0 ? profit / income : 0,
      offProfit: equipment + draw, equipment: equipment, draw: draw, loss: profit < 0 ? -profit : 0,
      pos: income > 0 && profit > 0 ? 1 : 0, neg: income > 0 && profit < 0 ? 1 : 0,
      noIncome: income > 0 ? 0 : 1, noMonths: income > 0 && m === 0 ? 1 : 0, hasOff: equipment + draw > 0 ? 1 : 0 };
  }

  var api = { hourly: hourly, service: service, cashflow: cashflow, etsyFees: etsyFees, craftFair: craftFair,
    strNightly: strNightly, debtPayoff: debtPayoff, shippingCost: shippingCost, reorderPoint: reorderPoint, strBreakEven: strBreakEven, rentalCashFlow: rentalCashFlow, businessExpense: businessExpense, num: num, money: money, ceilTo: ceilTo,
    wire: wire, after: after };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.PNF = api;
})(this);
