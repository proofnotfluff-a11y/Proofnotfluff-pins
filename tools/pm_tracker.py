#!/usr/bin/env python3
"""Prediction-market paper tracker (Todd, Oct 17, 2026: "prediction markets, paper only ... to see how you can build it").

The hypothesis under test: copying the trades of the top Polymarket wallets, after a realistic delay, fees and
slippage, makes money. This tool tests it with paper money only. It reads Polymarket's public Data API
(https://data-api.polymarket.com/v2, no key, no account) and never touches a trading endpoint, a wallet or
a dollar. Real stakes, if the paper record ever earns them, are Todd's to place, on his own word; nothing
here is investment advice.

Runs in GitHub Actions every 6 hours (.github/workflows/pm-tracker.yml) because the cloud agents' network
cannot reach the API. Everything it writes lives in pm/:

  config.json   the rules (cohort size, stake, fees, slippage, verdict date); edited only by a commit
  state.json    cohort, watched wallets, open and closed paper positions, cash
  equity.csv    one row per run: equity, cash, open value, realized and unrealized P&L, signal counts
  raw/          one trimmed sample of each API response shape, for checking the parser against reality

How the copy works (honest version):
- Cohort: the top N wallets on the month PNL board, re-picked every cohort_refresh_days. A wallet that drops
  out stays watched until our copied positions from it are closed.
- A wallet's BUY of a token we do not hold opens a paper position at the CURRENT price (what we could get
  when we notice it, up to 6 hours after they traded) plus slippage, minus fees. Trades older than our
  first look at a wallet are never copied: we only copy what happens after we start watching.
- That wallet's SELL of a token we hold closes our position at the current price minus slippage and fees.
- Open positions are marked to market every run; a market that resolves settles at 1 or 0.
- Prices under 0.05 or over 0.95 are skipped (fees eat the edge), and one token is held once.
- An invariant is checked every run: cash + open cost - realized P&L (fees included) == starting bankroll.

Verdict (pm/config.json verdict_at): kill unless equity is above the starting bankroll after fees AND at
least min_closed_for_verdict positions have closed AND the mean P&L per closed position is positive. Fewer
closed positions than that is "inconclusive", never "kept".

Usage: python3 tools/pm_tracker.py run        one tracking step (needs network)
       python3 tools/pm_tracker.py --selftest  offline: canned API answers, the maths and the invariant
"""
import csv, datetime as dt, json, os, sys, time, urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PM = os.path.join(ROOT, "pm")
API = "https://data-api.polymarket.com/v2"
UA = {"User-Agent": "ProofNotFluff paper tracker (github.com/proofnotfluff-a11y/Proofnotfluff-pins); read-only"}

DEFAULT_CONFIG = {
    "started": "2026-10-17",
    "bankroll": 200.0,            # paper dollars; the size Todd named as what he would risk, so the numbers are in his units
    "stake_per_signal": 5.0,      # 2.5% of the bankroll per copied trade
    "top_n": 20,
    "time_period": "month",
    "cohort_refresh_days": 7,
    "fee_rate": 0.02,             # a conservative stand-in: 2% of notional each way (Polymarket's fees vary by market; Kalshi's are 0.07 x price x (1 - price) per contract)
    "slippage": 0.01,             # one cent against us on every fill
    "min_price": 0.05,
    "max_price": 0.95,
    "max_open": 40,
    "verdict_at": "2026-12-12",   # 8 weeks
    "min_closed_for_verdict": 100
}


def now():
    return dt.datetime.now(dt.timezone.utc)


def iso(t=None):
    return (t or now()).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_json(path, params, retries=3):
    """GET one Data API path. Read-only by construction: only data-api.polymarket.com, only /v2 reads."""
    url = API + path + "?" + urllib.parse.urlencode(params)
    host = urllib.parse.urlparse(url).hostname
    if host != "data-api.polymarket.com":
        raise ValueError("refusing a request outside the Data API")
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < retries - 1:
                time.sleep(float(e.headers.get("Retry-After", 5)))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < retries - 1:
                time.sleep(3)
                continue
            raise
    return None


def save_raw(name, payload):
    """Keep one trimmed sample of each response shape so the parser can be checked against reality."""
    d = os.path.join(PM, "raw")
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, name + ".json")
    if os.path.exists(f):
        return
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        payload = dict(payload, data=payload["data"][:2])
    json.dump(payload, open(f, "w"), indent=1)


def rows(payload):
    d = payload.get("data") if isinstance(payload, dict) else payload
    return d if isinstance(d, list) else ([] if d is None else [d])


def leaderboard(cfg):
    p = fetch_json("/leaderboard", {"time_period": cfg["time_period"], "sort_by": "PNL", "limit": max(cfg["top_n"], 10)})
    save_raw("leaderboard", p)
    out = []
    for r in rows(p):
        uid = r.get("user_id") or r.get("proxy_wallet") or r.get("proxyWallet")
        if uid:
            out.append({"user_id": uid, "user_name": r.get("user_name") or "", "pnl": r.get("pnl"), "rank": r.get("rank")})
    return out[:cfg["top_n"]]


def activity(wallet):
    p = fetch_json("/activity", {"user": wallet, "limit": 100})
    save_raw("activity", p)
    out = []
    for r in rows(p):
        if (r.get("type") or "").upper() != "TRADE":
            continue
        try:
            out.append({"t": int(r.get("timestamp") or 0), "token_id": str(r.get("token_id") or r.get("asset") or ""),
                        "condition_id": r.get("condition_id") or r.get("conditionId") or "", "side": (r.get("side") or "").upper(),
                        "price": float(r.get("price") or 0), "size": float(r.get("size") or 0), "title": r.get("title") or "",
                        "outcome": r.get("outcome") or "", "outcome_index": r.get("outcome_index", r.get("outcomeIndex"))})
        except (TypeError, ValueError):
            continue
    return sorted(out, key=lambda x: x["t"])


def current_price(token_id):
    """Last traded price for a token from its price history (independent of any wallet). None when unknown."""
    t = int(now().timestamp())
    p = fetch_json("/prices-history", {"token_id": token_id, "start": t - 3 * 86400, "end": t, "bucket_seconds": 1800})
    save_raw("prices-history", p)
    hist = p.get("history") if isinstance(p, dict) else None
    if hist is None:
        hist = rows(p)
    last = None
    for h in hist or []:
        v = h.get("p", h.get("price", h.get("close")))
        if v is not None:
            last = float(v)
    return last


def resolution(condition_id):
    """(resolved, winning_outcome_index or None). Parsed defensively; the raw sample shows the real shape."""
    try:
        p = fetch_json("/resolutions", {"condition": condition_id})
    except Exception:
        return False, None
    save_raw("resolutions", p)
    for r in rows(p):
        status = str(r.get("status") or r.get("state") or "").lower()
        resolved = bool(r.get("resolved")) or status in ("resolved", "finalized", "settled")
        if not resolved:
            continue
        win = r.get("winning_outcome_index", r.get("winningOutcomeIndex", r.get("winner_index")))
        payouts = r.get("payouts") or r.get("payout_numerators")
        if win is None and isinstance(payouts, list) and payouts:
            try:
                win = max(range(len(payouts)), key=lambda i: float(payouts[i]))
            except (TypeError, ValueError):
                win = None
        return True, (int(win) if win is not None else None)
    return False, None


def load_state(cfg):
    f = os.path.join(PM, "state.json")
    if os.path.exists(f):
        return json.load(open(f))
    return {"started_at": iso(), "cash": float(cfg["bankroll"]), "realized_pnl": 0.0, "cohort": {"picked_at": None, "wallets": []},
            "watch": {}, "last_seen": {}, "positions": {}, "closed": [], "signals": {"buy": 0, "sell": 0, "skipped": 0, "fallback_price": 0},
            "errors": 0}


def invariant(state, cfg):
    open_cost = sum(p["cost"] for p in state["positions"].values())
    total = state["cash"] + open_cost - state["realized_pnl"]
    if abs(total - cfg["bankroll"]) > 0.005:
        raise AssertionError(f"money does not add up: cash {state['cash']:.2f} + open cost {open_cost:.2f} - realized {state['realized_pnl']:.2f} != {cfg['bankroll']}")


def open_position(state, cfg, leader, trade, price):
    stake = min(cfg["stake_per_signal"], state["cash"])
    if stake < 1.0:
        state["signals"]["skipped"] += 1
        return
    entry = round(price + cfg["slippage"], 4)
    fee = round(stake * cfg["fee_rate"], 4)
    shares = round((stake - fee) / entry, 4)
    state["cash"] = round(state["cash"] - stake, 4)
    state["positions"][trade["token_id"]] = {"leader": leader, "condition_id": trade["condition_id"], "title": trade["title"], "outcome": trade["outcome"],
                                            "outcome_index": trade["outcome_index"], "opened_at": iso(), "leader_price": trade["price"],
                                            "entry_price": entry, "shares": shares, "cost": stake, "fee_in": fee, "last_price": price, "value": round(shares * price, 4)}
    state["signals"]["buy"] += 1


def close_position(state, cfg, token_id, price, reason):
    p = state["positions"].pop(token_id)
    exit_price = max(0.0, min(1.0, price - (cfg["slippage"] if reason == "leader sold" else 0.0)))
    proceeds = round(p["shares"] * exit_price, 4)
    fee = round(proceeds * cfg["fee_rate"], 4) if reason == "leader sold" else 0.0
    net = round(proceeds - fee, 4)
    pnl = round(net - p["cost"], 4)
    state["cash"] = round(state["cash"] + net, 4)
    state["realized_pnl"] = round(state["realized_pnl"] + pnl, 4)
    p.update({"closed_at": iso(), "exit_price": exit_price, "fee_out": fee, "pnl": pnl, "reason": reason})
    state["closed"].append(p)
    if reason == "leader sold":
        state["signals"]["sell"] += 1


def step(cfg, state, log=print):
    """One tracking step. Network calls go through leaderboard(), activity(), current_price(), resolution()."""
    t0 = now()
    # 1. Cohort
    picked = state["cohort"]["picked_at"]
    stale = (not picked) or (t0 - dt.datetime.strptime(picked, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)).days >= cfg["cohort_refresh_days"]
    if stale:
        try:
            wallets = leaderboard(cfg)
            if wallets:
                state["cohort"] = {"picked_at": iso(t0), "wallets": wallets}
                for w in wallets:
                    state["watch"].setdefault(w["user_id"], {"name": w["user_name"], "since": iso(t0)})
        except Exception as e:
            state["errors"] += 1
            log(f"leaderboard error: {e}")
    cohort_ids = {w["user_id"] for w in state["cohort"]["wallets"]}
    # 2. New trades from every watched wallet
    for wallet in list(state["watch"]):
        held_from = [tid for tid, p in state["positions"].items() if p["leader"] == wallet]
        if wallet not in cohort_ids and not held_from:
            del state["watch"][wallet]
            continue
        try:
            trades = activity(wallet)
        except Exception as e:
            state["errors"] += 1
            log(f"activity error for a wallet: {e}")
            continue
        seen = state["last_seen"].get(wallet)
        if seen is None:   # first look: never copy history
            state["last_seen"][wallet] = int(t0.timestamp())
            continue
        new = [t for t in trades if t["t"] > seen]
        for t in new:
            tid = t["token_id"]
            if t["side"] == "BUY" and wallet in cohort_ids:
                if tid in state["positions"] or len(state["positions"]) >= cfg["max_open"] or not tid:
                    state["signals"]["skipped"] += 1
                    continue
                price = None
                try:
                    price = current_price(tid)
                except Exception:
                    state["errors"] += 1
                if price is None:
                    price = t["price"]
                    state["signals"]["fallback_price"] += 1
                if price < cfg["min_price"] or price > cfg["max_price"]:
                    state["signals"]["skipped"] += 1
                    continue
                open_position(state, cfg, wallet, t, price)
            elif t["side"] == "SELL" and tid in state["positions"] and state["positions"][tid]["leader"] == wallet:
                price = None
                try:
                    price = current_price(tid)
                except Exception:
                    state["errors"] += 1
                if price is None:
                    price = t["price"]
                    state["signals"]["fallback_price"] += 1
                close_position(state, cfg, tid, price, "leader sold")
        if new:
            state["last_seen"][wallet] = max(t["t"] for t in new)
    # 3. Mark to market and settle
    for tid in list(state["positions"]):
        p = state["positions"][tid]
        resolved, win = resolution(p["condition_id"]) if p["condition_id"] else (False, None)
        if resolved:
            settle = None
            if win is not None and p.get("outcome_index") is not None:
                settle = 1.0 if int(p["outcome_index"]) == win else 0.0
            elif p["last_price"] >= 0.99:
                settle = 1.0
            elif p["last_price"] <= 0.01:
                settle = 0.0
            if settle is not None:
                close_position(state, cfg, tid, settle, "resolved")
                continue
        try:
            price = current_price(tid)
        except Exception:
            price = None
            state["errors"] += 1
        if price is not None:
            p["last_price"] = price
            p["value"] = round(p["shares"] * price, 4)
    invariant(state, cfg)
    open_value = round(sum(p["value"] for p in state["positions"].values()), 4)
    open_cost = round(sum(p["cost"] for p in state["positions"].values()), 4)
    equity = round(state["cash"] + open_value, 4)
    row = {"run_at": iso(t0), "equity": equity, "cash": round(state["cash"], 4), "open_value": open_value, "open_count": len(state["positions"]),
           "realized_pnl": round(state["realized_pnl"], 4), "unrealized_pnl": round(open_value - open_cost, 4),
           "buys": state["signals"]["buy"], "closed": len(state["closed"]), "skipped": state["signals"]["skipped"],
           "fallback_price": state["signals"]["fallback_price"], "errors": state["errors"], "cohort": len(state["cohort"]["wallets"])}
    return row


def verdict(cfg, state, equity_rows):
    closed = state["closed"]
    n = len(closed)
    mean = (sum(p["pnl"] for p in closed) / n) if n else 0.0
    equity = equity_rows[-1]["equity"] if equity_rows else cfg["bankroll"]
    if n < cfg["min_closed_for_verdict"]:
        return "inconclusive", f"{n} closed positions (needs {cfg['min_closed_for_verdict']}); equity {equity:.2f} on {cfg['bankroll']:.0f}"
    if equity > cfg["bankroll"] and mean > 0:
        return "kept", f"equity {equity:.2f} on {cfg['bankroll']:.0f} after fees, {n} closed, mean {mean:+.3f} per position"
    return "killed", f"equity {equity:.2f} on {cfg['bankroll']:.0f} after fees, {n} closed, mean {mean:+.3f} per position"


def run():
    os.makedirs(PM, exist_ok=True)
    cf = os.path.join(PM, "config.json")
    cfg = dict(DEFAULT_CONFIG, **(json.load(open(cf)) if os.path.exists(cf) else {}))
    if not os.path.exists(cf):
        json.dump(cfg, open(cf, "w"), indent=1)
    state = load_state(cfg)
    row = step(cfg, state)
    json.dump(state, open(os.path.join(PM, "state.json"), "w"), indent=1)
    ef = os.path.join(PM, "equity.csv")
    new = not os.path.exists(ef)
    with open(ef, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        if new:
            w.writeheader()
        w.writerow(row)
    history = list(csv.DictReader(open(ef)))
    for h in history:
        h["equity"] = float(h["equity"])
    v, why = verdict(cfg, state, history)
    print(json.dumps(row))
    print(f"verdict so far ({cfg['verdict_at']}): {v}: {why}")
    return 0


def selftest():
    """Offline: canned API answers drive two steps; the maths, the no-history rule and the invariant are checked,
    and a planted broken fee must be caught by the invariant (a checker that cannot fail proves nothing)."""
    global leaderboard, activity, current_price, resolution
    cfg = dict(DEFAULT_CONFIG, bankroll=100.0, stake_per_signal=10.0, top_n=2)
    clock = {"t": 1_700_000_000}
    trades = {"0xA": [], "0xB": []}
    prices = {"tokY": 0.40, "tokZ": 0.70}
    leaderboard = lambda c: [{"user_id": "0xA", "user_name": "a", "pnl": 5000, "rank": 1}, {"user_id": "0xB", "user_name": "b", "pnl": 4000, "rank": 2}]
    activity = lambda w: list(trades[w])
    current_price = lambda tid: prices.get(tid)
    resolution = lambda cid: (cid == "cond-done", 0) if cid == "cond-done" else (False, None)
    state = load_state(cfg)
    # Step 1: history exists before we watch; nothing may be copied.
    trades["0xA"].append({"t": clock["t"] - 100, "token_id": "tokY", "condition_id": "cond-y", "side": "BUY", "price": 0.38, "size": 50, "title": "Y?", "outcome": "Yes", "outcome_index": 0})
    r1 = step(cfg, state, log=lambda *a: None)
    assert r1["open_count"] == 0 and r1["equity"] == 100.0, r1
    # Step 2: a new BUY after watching started opens one paper position at the current price plus slippage, minus fee.
    future = int(now().timestamp()) + 60
    trades["0xA"].append({"t": future, "token_id": "tokY", "condition_id": "cond-y", "side": "BUY", "price": 0.39, "size": 50, "title": "Y?", "outcome": "Yes", "outcome_index": 0})
    trades["0xB"].append({"t": future, "token_id": "tokZ", "condition_id": "cond-done", "side": "BUY", "price": 0.70, "size": 50, "title": "Z?", "outcome": "Yes", "outcome_index": 0})
    r2 = step(cfg, state, log=lambda *a: None)
    # tokZ's market is resolved (winner index 0 == our outcome) so it settles at 1.0 in the same step: 9.8 / 0.71 shares x 1.0
    pos = state["positions"]["tokY"]
    assert abs(pos["entry_price"] - 0.41) < 1e-9 and abs(pos["fee_in"] - 0.2) < 1e-9 and abs(pos["shares"] - round(9.8 / 0.41, 4)) < 1e-9, pos
    assert r2["open_count"] == 1 and r2["closed"] == 1, r2
    z = state["closed"][0]
    assert z["reason"] == "resolved" and abs(z["pnl"] - (round(round(9.8 / 0.71, 4) * 1.0, 4) - 10.0)) < 1e-6, z
    # Step 3: the leader sells tokY at a higher price: closed with slippage and the exit fee.
    prices["tokY"] = 0.60
    trades["0xA"].append({"t": future + 10, "token_id": "tokY", "condition_id": "cond-y", "side": "SELL", "price": 0.60, "size": 50, "title": "Y?", "outcome": "Yes", "outcome_index": 0})
    r3 = step(cfg, state, log=lambda *a: None)
    y = state["closed"][-1]
    expect = round(round(round(9.8 / 0.41, 4) * 0.59, 4) * (1 - 0.02), 4) - 10.0
    assert y["reason"] == "leader sold" and abs(y["pnl"] - expect) < 1e-3, (y["pnl"], expect)
    assert abs(r3["equity"] - (100.0 + state["realized_pnl"])) < 1e-6 and r3["open_count"] == 0, r3
    # Planted failure: money that leaks must be caught.
    state["cash"] += 1.0
    try:
        invariant(state, cfg)
        print("selftest FAIL: the invariant let a leak through")
        return 1
    except AssertionError:
        pass
    v, why = verdict(cfg, state, [{"equity": r3["equity"]}])
    assert v == "inconclusive", (v, why)
    print(f"selftest PASS (equity {r3['equity']:.2f} after 2 closed positions; the planted leak was caught; verdict '{v}')")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        sys.exit(selftest())
    if len(sys.argv) == 2 and sys.argv[1] == "run":
        sys.exit(run())
    print(__doc__)
    sys.exit(2)
