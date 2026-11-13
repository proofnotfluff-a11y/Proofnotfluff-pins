"""Sample household statement for the trial demo: 3 months, one checking account and one card. Every merchant is invented.
Seeded, so the same file comes out every time. Writes statement.csv (what the AI is given) and truth.json (what a correct
answer must find; the AI never sees it)."""
import csv, datetime as dt, json, random
R = random.Random(20261113)
D = dt.date
rows = []
def add(d, desc, amt, acct):
    rows.append((d, desc, round(amt, 2), acct))
months = [(2026, 8), (2026, 9), (2026, 10)]
subs = {  # name: (day, amount by month, account)
    "STREAMLY PLUS": (3, [15.99, 15.99, 15.99], "card"),
    "VIEWBOX PREMIUM": (11, [17.99, 17.99, 17.99], "card"),
    "KINOFLIX": (19, [9.99, 9.99, 9.99], "card"),
    "FITHAUS GYM MEMBERSHIP": (1, [49.00, 49.00, 49.00], "checking"),
    "CLOUDBOX STORAGE": (7, [2.99, 9.99, 9.99], "card"),          # the price jump
    "TUNEWAVE FAMILY": (14, [16.99, 16.99, 16.99], "card"),
    "MEALCRATE WEEKLY BOX": (22, [71.96, 71.96, 71.96], "card"),
    "NEWSDAILY DIGITAL": (26, [12.00, 12.00, 12.00], "card"),
    "PHOTOPRO APP": (9, [7.99, 7.99, 7.99], "card"),
    "WORDGAME GOLD": (17, [4.99, 4.99, 4.99], "card"),
}
delivery_plan = [(6, 212.0), (9, 301.0), (12, 394.0)]   # orders and rough total a month: it climbs
for mi, (y, m) in enumerate(months):
    last = (D(y, m + 1, 1) - dt.timedelta(days=1)).day
    for d in (1, 15):
        add(D(y, m, d), "PAYROLL DIRECT DEP NORTHLINE SUPPLY", 2385.40, "checking")
    add(D(y, m, 1), "RENT PAYMENT MAPLE COURT APTS", -1650.00, "checking")
    add(D(y, m, 5), "CITY POWER AND LIGHT", -R.uniform(88, 131), "checking")
    add(D(y, m, 8), "MOBILINK WIRELESS", -84.00, "checking")
    add(D(y, m, 12), "HARBOR MUTUAL AUTO INS", -118.50, "checking")
    add(D(y, m, 20), "FIBERNEST INTERNET", -65.00, "checking")
    add(D(y, m, 28), "CARD PAYMENT THANK YOU", -R.uniform(900, 1250), "checking")
    for name, (day, amts, acct) in subs.items():
        add(D(y, m, day), name, -amts[mi], acct)
    for _ in range(9):
        add(D(y, m, R.randint(1, last)), R.choice(["GREENLEAF MARKET", "GREENLEAF MARKET", "CORNER GROCER", "BULKBARN WHOLESALE"]), -R.uniform(38, 142), "card")
    for _ in range(5):
        add(D(y, m, R.randint(1, last)), R.choice(["FUELSTOP #212", "FUELSTOP #087"]), -R.uniform(34, 58), "card")
    for _ in range(7):
        add(D(y, m, R.randint(1, last)), R.choice(["BLUE DOOR CAFE", "TACO LINDO", "NOODLE HOUSE", "MORNING BUN BAKERY", "PIZZERIA SOLE"]), -R.uniform(9, 46), "card")
    n, total = delivery_plan[mi]
    cuts = sorted(R.uniform(0.6, 1.4) for _ in range(n)); s = sum(cuts)
    for c in cuts:
        add(D(y, m, R.randint(1, last)), "DASHDISH DELIVERY", -total * c / s, "card")
    for _ in range(4):
        add(D(y, m, R.randint(1, last)), R.choice(["HOMEBASE HARDWARE", "PAGE AND SPINE BOOKS", "TRENDLINE CLOTHING", "PETPANTRY", "PHARMAPLUS"]), -R.uniform(12, 96), "card")
# the double charge: same merchant, same amount, same day
add(D(2026, 10, 16), "HOMEBASE HARDWARE", -86.42, "card")
add(D(2026, 10, 16), "HOMEBASE HARDWARE", -86.42, "card")
# a yearly renewal that is easy to miss
add(D(2026, 9, 23), "SAFEVAULT PASSWORDS ANNUAL", -59.88, "card")
rows.sort(key=lambda r: (r[0], r[1]))
with open("statement.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["date", "description", "amount", "account"])
    for d, desc, amt, acct in rows:
        w.writerow([d.isoformat(), desc, f"{amt:.2f}", acct])
oct_subs = {k: v[1][2] for k, v in subs.items()}
deliv = {f"{y}-{m:02d}": round(-sum(a for d, s_, a, _ in rows if s_ == "DASHDISH DELIVERY" and (d.year, d.month) == (y, m)), 2) for y, m in months}
truth = {"transactions": len(rows), "months": 3,
         "subscriptions": oct_subs, "subscription_count": len(oct_subs), "subscriptions_monthly_total": round(sum(oct_subs.values()), 2),
         "subscriptions_yearly_total": round(sum(oct_subs.values()) * 12, 2),
         "price_jump": {"merchant": "CLOUDBOX STORAGE", "from": 2.99, "to": 9.99, "first_month_at_new_price": "2026-09"},
         "double_charge": {"merchant": "HOMEBASE HARDWARE", "date": "2026-10-16", "amount": 86.42},
         "yearly_renewal": {"merchant": "SAFEVAULT PASSWORDS ANNUAL", "date": "2026-09-23", "amount": 59.88},
         "delivery_by_month": deliv, "delivery_orders_by_month": {"2026-08": 6, "2026-09": 9, "2026-10": 12},
         "streaming_video_services": ["STREAMLY PLUS", "VIEWBOX PREMIUM", "KINOFLIX"], "streaming_video_monthly": 43.97}
json.dump(truth, open("truth.json", "w"), indent=1)
print(json.dumps(truth, indent=1))
