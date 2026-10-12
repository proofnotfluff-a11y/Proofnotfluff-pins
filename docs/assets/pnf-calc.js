/* ProofNotFluff free calculators. The maths is the same as the paid workbooks:
   hourly: engines/hourly-rate-quick-calculator (#20); service: engines/service-pricing (#13 and its trade editions);
   cashflow: the premium 13-Week E-commerce Cash Flow workbook's ending-cash row;
   etsyFees: engines/etsy-true-profit (#5); craftFair: engines/craft-fair-profit (#12);
   strNightly: engines/str-nightly-pricing (#9); debtPayoff: engines/debt-payoff-tracker (#16);
   shippingCost: engines/shipping-true-cost (#7); reorderPoint: engines/cash-aware-reorder-planner (#6);
   inventoryTurnover: engines/cash-aware-reorder-planner (#6), 1 Your Shop turnover rows and 2 SKU List days of stock;
   strBreakEven: the #9 fee stack (engines/str-nightly-pricing), break-even nights for the STR lite page;
   profitMargin: engines/etsy-true-profit (#5), 3 Pricing tab, the list price for a target margin;
   rentalCashFlow: engines/rental-property (#19), 4 Property P&L profit and cash flow rows.
   businessExpense: engines/business-expense-tracker (#18), Summary tab income, expenses and profit rows.
   seTax: Schedule SE arithmetic (the SE_RATE and SE_BASE the #13 engine grosses up for), with the 2026 Social Security
   wage base; links #21 (Freelance Income Tracker), whose set-aside notes cite the same IRS and SSA figures.
   profitLoss: engines/profit-and-loss (#28), 2 Statement; cakeQuote: engines/cake-order-form (#26), 2 Order Form.
   unitCost: engines/inventory-tracker (#25), 1 Items; choreSplit: engines/fair-share-chore-chart (#24), Fair Split.
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
    // Quick quote (workbook rows 41 to 43): labor at the rate-card rate, materials with markup.
    var rateCard = ceilTo(rate, 5);
    var quoteLabor = num(i.jobHours) * rateCard, quoteMaterials = num(i.materials) * (1 + num(i.markup) / 100);
    // Bill more of your week (workbook I31:I34): the rate needed at 50%, 60%, 70% and 80% billed.
    var at = function (s) { return worked * s > 0 ? revenue / (worked * s) : 0; };
    return {
      quoteLabor: quoteLabor, quoteMaterials: quoteMaterials, quote: quoteLabor + quoteMaterials,
      rateAt50: at(0.5), rateAt60: at(0.6), rateAt70: at(0.7), rateAt80: at(0.8),
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

  // Self-employment tax, Schedule SE: net earnings = 92.35% of net profit; none owed under $400 of net earnings;
  // 12.4% Social Security on net earnings up to the 2026 wage base less W-2 wages already taxed, 2.9% Medicare on all.
  // Half is an adjustment to income. Additional Medicare Tax (0.9%, Form 8959) is not included.
  var SS_BASE_2026 = 184500;
  function seTax(i) {
    var net = num(i.net), wages = Math.max(0, num(i.wages));
    var earnings = net > 0 ? net * SE_BASE : 0;
    var owes = earnings >= 400 ? 1 : 0;
    var room = Math.max(0, SS_BASE_2026 - wages);
    var ssPart = owes ? 0.124 * Math.min(earnings, room) : 0;
    var medPart = owes ? 0.029 * earnings : 0;
    var se = ssPart + medPart;
    return { net: net, earnings: earnings, ssPart: ssPart, medPart: medPart, se: se, half: se / 2,
      quarter: se / 4, month: se / 12, share: net > 0 ? se / net : 0, room: room,
      capped: owes && earnings > room ? 1 : 0, under: net > 0 && !owes ? 1 : 0, noNet: net > 0 ? 0 : 1, pos: se > 0 ? 1 : 0 };
  }

  // #6 Cash-Aware Reorder Planner (engines/cash-aware-reorder-planner): 1 Your Shop TURNOVER rows
  // (turns = cost of goods a year / stock value at cost; days = 365 / turns) and 2 SKU List days of stock (P),
  // with the OVERSTOCK rule (days of stock at or above the overstock days, 120 by default).
  function inventoryTurnover(i) {
    var cogs = Math.max(0, num(i.cogsYear)), stock = Math.max(0, num(i.stockValue)), daily = Math.max(0, num(i.daily)), onHand = Math.max(0, num(i.onHand));
    var over = num(i.overDays) > 0 ? num(i.overDays) : 120;
    var turns = stock > 0 ? cogs / stock : 0;
    var days = turns > 0 ? 365 / turns : 0;
    var pDays = daily > 0 ? onHand / daily : 0;
    var pTurns = daily > 0 && onHand > 0 ? 365 * daily / onHand : 0;
    var overstock = daily > 0 && onHand > 0 && pDays >= over ? 1 : 0;
    var noSales = daily > 0 ? 0 : 1;
    var status = noSales ? "No sales" : onHand <= 0 ? "Sold out" : overstock ? "Overstock: stop reordering" : "OK";
    return { turns: turns, days: days, perDay: cogs / 365, perMonth: cogs / 12, pDays: pDays, pTurns: pTurns,
      over: over, overstock: overstock, noSales: noSales, soldOut: !noSales && onHand <= 0 ? 1 : 0,
      okP: !noSales && onHand > 0 && !overstock ? 1 : 0, statusText: status,
      noStock: stock > 0 ? 0 : 1, noCogs: stock > 0 && cogs <= 0 ? 1 : 0, shopOk: stock > 0 && cogs > 0 ? 1 : 0 };
  }


  // #5 True Profit System for Etsy Sellers, 3 Pricing tab "Your price for that margin": price plus shipping =
  // (materials + labor + label + packaging + listing fee + fixed processing) / (1 - transaction - processing - margin),
  // less the shipping charged; the ad-sale price adds the Offsite Ads rate to the rates. A blank price means no price works.
  function profitMargin(i) {
    var t = num(i.target) / 100, mat = num(i.materials), lab = num(i.labor), ship = num(i.ship), label = num(i.label),
        pack = num(i.packaging), ar = num(i.adsRate) / 100, tf = num(i.tfRate) / 100, pr = num(i.procRate) / 100,
        pfx = num(i.procFixed), lf = num(i.listFee);
    var fixed = mat + lab + label + pack + lf + pfx, den = 1 - tf - pr - t, den2 = den - ar;
    var ok = den > 0 ? 1 : 0, adOk = den2 > 0 ? 1 : 0;
    var price = ok ? fixed / den - ship : 0, adPrice = adOk ? fixed / den2 - ship : 0;
    var rev = price + ship, fees = ok ? rev * (tf + pr) + lf + pfx : 0, profit = ok ? rev * t : 0;
    return { ok: ok, none: ok ? 0 : 1, adOk: adOk, adNone: ok && !adOk ? 1 : 0, adBlank: adOk ? 0 : 1, price: price, adPrice: adPrice,
      adGap: ok && adOk ? adPrice - price : 0, profit: profit, revenue: rev, fees: fees, costs: mat + lab + pack,
      label: label, ship: ship, shipGap: label - ship, target: t, fixed: fixed, roundHalf: ok ? ceilTo(price, 0.5) : 0,
      roundOne: ok ? ceilTo(price, 1) : 0, neg: ok && price <= 0 ? 1 : 0, show: ok && price > 0 ? 1 : 0 };
  }

  // #8 First-Time Employer Payroll and Benefits Setup Guide, Section 6 "What Maria costs on top of her pay" and
  // "The true hourly cost of a $20-an-hour employee": employer Social Security 6.2% (to the 2026 wage base) and
  // Medicare 1.45%, FUTA at the net rate on the first $7,000, state unemployment at your rate on your state's wage
  // base, workers' comp per $100 of wages, then payroll software and a monthly benefit spread over the hours worked.
  function employerCost(i) {
    var wage = Math.max(0, num(i.wage)), hrs = Math.max(0, num(i.hours)), wks = Math.min(52, Math.max(0, num(i.weeks)));
    var suta = Math.max(0, num(i.sutaRate)) / 100, sutaBase = Math.max(0, num(i.sutaBase)), comp = Math.max(0, num(i.compRate)) / 100;
    var futa = Math.max(0, num(i.futaRate)) / 100, benefit = Math.max(0, num(i.benefit)), software = Math.max(0, num(i.software));
    var hoursYear = hrs * wks, pay = wage * hoursYear, weekPay = wage * hrs;
    var ss = 0.062 * Math.min(pay, SS_BASE_2026), med = 0.0145 * pay;
    var futaYear = futa * Math.min(pay, 7000), sutaYear = suta * Math.min(pay, sutaBase), compYear = comp * pay;
    var taxes = ss + med + futaYear + sutaYear + compYear, extras = software + benefit * 12;
    var ok = hoursYear > 0 && wage > 0 ? 1 : 0;
    var per = function (x) { return ok ? x / hoursYear : 0; };
    var trueHourly = ok ? wage + per(taxes) : 0, allIn = ok ? wage + per(taxes + extras) : 0;
    return { ok: ok, none: ok ? 0 : 1, hoursYear: hoursYear, pay: pay, weekPay: weekPay,
      ss: ss, med: med, fica: ss + med, futa: futaYear, suta: sutaYear, comp: compYear, taxes: taxes,
      softwareYear: software, benefitYear: benefit * 12, extras: extras, totalYear: pay + taxes + extras,
      ficaHr: per(ss + med), futaHr: per(futaYear), sutaHr: per(sutaYear), compHr: per(compYear),
      softwareHr: per(software), benefitHr: per(benefit * 12), trueHourly: trueHourly, allIn: allIn,
      over: ok ? (trueHourly - wage) / wage : 0, overAll: ok ? (allIn - wage) / wage : 0,
      weekFica: 0.0765 * weekPay, weekFuta: futa * Math.min(weekPay, 7000), weekSuta: suta * Math.min(weekPay, sutaBase),
      weekComp: comp * weekPay, futaWeeks: ok && weekPay > 0 ? Math.min(wks, Math.ceil(7000 / weekPay - 1e-9)) : 0,
      hasExtras: ok && extras > 0 ? 1 : 0, pos: ok };
  }

  // Startup cost pages (#14 Cleaning Business Starter Kit, #23 Junk Removal and #22 Pressure Washing editions of the
  // service-pricing engine): the one-time spend you type, plus a cushion of the workbook's "Total per month" business
  // costs, and the jobs it takes to earn the one-time spend back from the profit in each quote (Quote Builder "Profit
  // per visit" or "Profit in this quote": the price after your pay at the break-even rate, costs and taxes).
  function startupCost(i) {
    var lines = ["s1", "s2", "s3", "s4", "s5"].map(function (k) { return Math.max(0, num(i[k])); });
    var oneTime = lines.reduce(function (a, b) { return a + b; }, 0);
    var monthly = Math.max(0, num(i.monthly)), months = Math.max(0, Math.round(num(i.months)));
    var profit = num(i.profitJob), perWeek = Math.max(0, num(i.jobsWeek));
    var cushion = monthly * months, cash = oneTime + cushion;
    var canPay = profit > 0 && oneTime > 0 ? 1 : 0;
    var jobs = canPay ? Math.ceil(oneTime / profit - 1e-9) : 0;
    var weeks = canPay && perWeek > 0 ? Math.ceil(jobs / perWeek - 1e-9) : 0;
    return { oneTime: oneTime, cushion: cushion, cash: cash, monthly: monthly, months: months, profit: Math.max(0, profit),
      jobs: jobs, weeks: weeks, ok: canPay, noProfit: oneTime > 0 && profit <= 0 ? 1 : 0, none: oneTime > 0 ? 0 : 1,
      noPace: canPay && perWeek <= 0 ? 1 : 0, pace: canPay && perWeek > 0 ? 1 : 0 };
  }

  // #29 Budget Planner Spreadsheet: 1 Setup "Your month at a glance" (Take-home income, Bills, Everyday spending,
  // Savings and extra debt, Planned out each month, Left to plan). Per month = amount x how often, as the Setup tab does.
  var PER_MONTH = { monthly: 1, twice: 2, biweekly: 26 / 12, weekly: 52 / 12, quarterly: 1 / 3, yearly: 1 / 12 };
  function budgetPlan(i) {
    var f1 = PER_MONTH[i.freq1] || 1, f2 = PER_MONTH[i.freq2] || 1;
    var pay1 = Math.max(0, num(i.pay1)) * f1, pay2 = Math.max(0, num(i.pay2)) * f2, other = Math.max(0, num(i.other));
    var income = pay1 + pay2 + other;
    var bills = Math.max(0, num(i.bills)), spend = Math.max(0, num(i.spend)), yearlyMonth = Math.max(0, num(i.yearly)) / 12;
    var save = Math.max(0, num(i.save));
    var everyday = spend + yearlyMonth, out = bills + everyday + save, left = income - out;
    var share = function (x) { return income > 0 ? x / income : 0; };
    return { pay1: pay1, pay2: pay2, other: other, income: income, bills: bills, spend: spend, yearlyMonth: yearlyMonth,
      everyday: everyday, save: save, out: out, left: left, over: left < 0 ? -left : 0,
      billsShare: share(bills), everydayShare: share(everyday), saveShare: share(save), leftShare: share(left),
      pos: income > 0 && left >= 0 ? 1 : 0, neg: income > 0 && left < 0 ? 1 : 0, none: income > 0 ? 0 : 1 };
  }

  // #28 Profit and Loss Template: 2 Statement rows Net revenue, Cost of goods sold (with the optional stock counts,
  // used only when both are typed, as the Statement's "Change in stock on hand" row), Gross profit, Total operating
  // expenses, Net profit, Gross margin and Net margin. Equipment, owner draws and transfers stay out, as in the workbook.
  function blank(v) { return v === undefined || v === null || String(v).replace(/[$,\s]/g, "") === ""; }
  function profitLoss(i) {
    var sales = num(i.sales), other = num(i.other), refunds = Math.abs(num(i.refunds));
    var revenue = sales + other - refunds;
    var goods = num(i.goods), stockOn = !blank(i.stock0) && !blank(i.stock1) ? 1 : 0;
    var stockChange = stockOn ? num(i.stock0) - num(i.stock1) : 0;
    var cogs = goods + stockChange, gross = revenue - cogs, expenses = num(i.expenses), net = gross - expenses;
    var any = sales !== 0 || other !== 0 || refunds !== 0 || goods !== 0 || expenses !== 0;
    return { revenue: revenue, refunds: refunds, goods: goods, stockChange: stockChange, stockOn: stockOn, cogs: cogs,
      gross: gross, expenses: expenses, net: net, loss: net < 0 ? -net : 0,
      grossMargin: revenue !== 0 ? gross / revenue : 0, netMargin: revenue !== 0 ? net / revenue : 0,
      pos: any && revenue !== 0 && net >= 0 ? 1 : 0, neg: any && net < 0 ? 1 : 0, noRev: any && revenue === 0 ? 1 : 0, none: any ? 0 : 1 };
  }

  // #26 Cake Order Form and Order Tracker: 2 Order Form "How it's built" card. Servings per tier from the Price List's
  // size table (Wilton serving guide, 2-layer cakes, as the workbook ships it), cake price = servings x price per
  // serving with the minimum cake price, delivery = base + miles x per mile, rush fee = rush % of cake + extras when
  // the event is fewer days out than the rush window, sales tax on the subtotal, deposit = total x deposit %.
  var CAKE_SIZES = { "6 in round": [12, 12], "8 in round": [20, 24], "9 in round": [24, 32], "10 in round": [28, 38],
    "12 in round": [40, 56], "14 in round": [63, 78], "16 in round": [77, 100], "6 in square": [12, 18], "8 in square": [20, 32],
    "10 in square": [30, 50], "12 in square": [48, 72], "14 in square": [63, 98], "16 in square": [80, 128],
    "7 x 11 in sheet": [24, 32], "9 x 13 in sheet": [36, 50], "11 x 15 in sheet": [54, 74], "12 x 18 in sheet": [72, 98],
    "6 in heart": [8, 14], "8 in heart": [18, 22], "9 in heart": [20, 28], "10 in heart": [24, 38], "12 in heart": [24, 56],
    "14 in heart": [48, 72], "16 in heart": [64, 94] };
  function r2(x) { return Math.round((x + (x >= 0 ? 1e-9 : -1e-9)) * 100) / 100; }
  function cakeQuote(i) {
    var col = i.style === "party" ? 0 : 1, servings = 0;
    ["t1", "t2", "t3", "t4"].forEach(function (k) { var z = CAKE_SIZES[i[k]]; if (z) servings += z[col]; });
    var pps = Math.max(0, num(i.pps)), minCake = Math.max(0, num(i.minCake));
    var base = servings * pps, cake = servings > 0 ? Math.max(minCake, base) : 0;
    var extras = Math.max(0, num(i.extras));
    var delivery = i.method === "delivery" ? Math.max(0, num(i.delivBase)) + Math.max(0, num(i.miles)) * Math.max(0, num(i.perMile)) : 0;
    var rushDays = num(i.rushDays), days = num(i.days);
    var rushOn = !blank(i.days) && rushDays > 0 && days < rushDays ? 1 : 0;
    var rush = rushOn ? r2(num(i.rushPct) / 100 * (cake + extras)) : 0;
    var sub = cake + extras + delivery + rush, tax = r2(sub * num(i.taxRate) / 100), total = sub + tax;
    var deposit = r2(total * num(i.depositPct) / 100);
    return { servings: servings, base: base, cake: cake, extras: extras, delivery: delivery, rush: rush, sub: sub, tax: tax,
      total: total, deposit: deposit, balance: total - deposit, perServing: servings > 0 ? total / servings : 0,
      minUsed: servings > 0 && cake > base ? 1 : 0, rushOn: rushOn, none: servings > 0 ? 0 : 1, ok: servings > 0 ? 1 : 0 };
  }


  // #25 Small Business Inventory Tracker, 1 Items: Unit cost = materials + labor + packaging and other; Profit per unit =
  // price - unit cost - price x fee rate; Stock value = units on hand (never below 0) x unit cost. Margin is profit per
  // unit as a share of the price, as the Dashboard's Profit margin is profit over sales.
  function unitCost(i) {
    var m = Math.max(0, num(i.materials)), l = Math.max(0, num(i.labor)), p = Math.max(0, num(i.packaging));
    var price = Math.max(0, num(i.price)), feeRate = Math.max(0, num(i.feePct)) / 100;
    var uc = m + l + p, fees = price * feeRate, ppu = price - uc - fees, onHand = Math.max(0, num(i.onHand));
    var hasPrice = price > 0 ? 1 : 0, any = uc > 0 || price > 0 ? 1 : 0;
    return { uc: uc, fees: fees, ppu: hasPrice ? ppu : 0, margin: hasPrice ? ppu / price : 0, costShare: hasPrice ? uc / price : 0,
      stockValue: onHand * uc, onHand: onHand, loss: hasPrice && ppu < 0 ? -ppu : 0,
      pos: hasPrice && ppu > 0 ? 1 : 0, neg: hasPrice && ppu <= 0 ? 1 : 0, noPrice: any && !hasPrice ? 1 : 0, none: any ? 0 : 1 };
  }

  // #24 Fair Share Chore Chart, Fair Split tab: fair target = whole-home minutes x each person's share (shares typed
  // for everyone are scaled to 100%, otherwise an even split, as Setup's "Shares" rule), over (+) or under (-) target =
  // assigned - target, hours a week = minutes / 60. This page uses clock minutes; the workbook also weights
  // "nobody wants it" jobs. Up to 3 people here (the workbook takes 4).
  function choreSplit(i) {
    var ks = ["a", "b", "c"], mins = [], shares = [], people = 0;
    ks.forEach(function (k) {
      var on = !blank(i[k]); mins.push(on ? Math.max(0, num(i[k])) : null); shares.push(on ? Math.max(0, num(i[k + "Share"])) : 0);
      if (on) people++;
    });
    var total = 0, typed = 0, sumShare = 0;
    ks.forEach(function (k, n) { if (mins[n] !== null) { total += mins[n]; if (shares[n] > 0) { typed++; sumShare += shares[n]; } } });
    var useShares = people > 0 && typed === people ? 1 : 0, out = { total: total, hours: total / 60, people: people, useShares: useShares,
      mixed: typed > 0 && typed < people ? 1 : 0 };
    var maxOver = 0, maxUnder = 0;
    ks.forEach(function (k, n) {
      var on = mins[n] !== null, sh = on ? (useShares ? shares[n] / sumShare : 1 / people) : 0;
      var t = total * sh, d = on ? mins[n] - t : 0;
      out[k + "Fair"] = sh; out[k + "Target"] = t; out[k + "Diff"] = d; out[k + "Over"] = d > 0 ? d : 0; out[k + "Under"] = d < 0 ? -d : 0;
      out[k + "Hours"] = on ? mins[n] / 60 : 0; out[k + "On"] = on ? 1 : 0;
      if (d > maxOver) maxOver = d; if (-d > maxUnder) maxUnder = -d;
    });
    out.move = Math.min(maxOver, maxUnder); out.gap = maxOver;
    out.even = people > 1 && total > 0 && maxOver < 15 ? 1 : 0; out.uneven = people > 1 && total > 0 && maxOver >= 15 ? 1 : 0;
    out.none = people > 1 && total > 0 ? 0 : 1;
    return out;
  }

  var api = { seTax: seTax, hourly: hourly, service: service, cashflow: cashflow, etsyFees: etsyFees, craftFair: craftFair,
    strNightly: strNightly, debtPayoff: debtPayoff, shippingCost: shippingCost, reorderPoint: reorderPoint, strBreakEven: strBreakEven, rentalCashFlow: rentalCashFlow, businessExpense: businessExpense, inventoryTurnover: inventoryTurnover, profitMargin: profitMargin, employerCost: employerCost, startupCost: startupCost, budgetPlan: budgetPlan, profitLoss: profitLoss, cakeQuote: cakeQuote, unitCost: unitCost, choreSplit: choreSplit, cakeSizes: CAKE_SIZES, num: num, money: money, ceilTo: ceilTo,
    wire: wire, after: after };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.PNF = api;
})(this);
