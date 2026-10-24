#!/usr/bin/env python3
"""GitHub-native decision-maker enrichment (runs in .github/workflows/prospect-enrichment.yml).

Input: prospects/businesses.json (schema pnf.business.v1, business-level fields only, committed by the prospect-matching
run): {"businesses": [{prospect_id, product, business, website, trade_vertical}]}. trade_vertical is optional (blank
means commercial_cleaning) and rides onto each sealed prospect by website domain.
The enrichment ladder (Todd, Oct 22, 2026, live chat), for each business with no decision-maker yet, free rungs first:
  1. The City's owner record (Chicago products): tools/owners_chicago.py, exact name match on the license account.
  2. The business's own site: tools/site_emails.py picks the owner's own published address, else a published owner-read
     inbox (info@, office@ ...). These leave as "pending" with email_status unverified: Bouncer checks them in the
     outreach run before any draft.
  2b. Owner names the business publishes on its own site (tools/site_owners.py, Todd, Oct 24, 2026), only with
     --site-owners: schema.org founder fields, a person named beside an owner word, probablepeople for person versus
     company. The address again comes only from tools/site_emails.py (owner_source "site_about"); none is guessed.
     Each domain is read once (siteOwnerAt in the state file), whatever its last checkedAt.
  3. Hunter (HUNTER_API_KEY secret), the paid fallback: at most --hunter-max domain searches a run, each domain once
     ever, "valid" addresses only. Apollo (APOLLO_API_KEY) only when Hunter is not used for that business.
  4. Local CSV drops data/enrichment/<product>-*.csv (gitignored), for runs on a machine where Todd dropped a file.
The previous box is opened and carried forward, so a business named once is never searched again. Which domains each
rung tried is kept in prospects/enrich_state.json (business-level only, committed). Every record goes through the Inbox
Gate. The validated pnf.prospect.v1 file ({prospects, pending}) is sealed with tools/data_box.py (PNF_DATA_KEY secret)
to prospects/enriched.sealed.json; the plain file never leaves the runner. Output on stdout is counts only.

Exit 0 when the sealed box was written; 1 when PNF_DATA_KEY is missing, an API fails, or the result fails validation.

Usage: python3 tools/enrich_ci.py [--businesses prospects/businesses.json] [--out prospects/enriched.sealed.json]
                                  [--state prospects/enrich_state.json] [--limit 400] [--hunter-max 5] [--site-owners]
"""
import argparse
import csv
import datetime as dt
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data_box  # noqa: E402
import owners_chicago  # noqa: E402
import site_emails  # noqa: E402
import enrich_apollo  # noqa: E402
import enrich_hunter  # noqa: E402
import pnf_rules as R  # noqa: E402
import prospects_import as PI  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUSINESSES = os.path.join(ROOT, "prospects", "businesses.json")
OUT = os.path.join(ROOT, "prospects", "enriched.sealed.json")
STATE = os.path.join(ROOT, "prospects", "enrich_state.json")
DROPS = os.path.join(ROOT, "data", "enrichment")
BUSINESS_KEYS = {"prospect_id", "product", "business", "website", "trade_vertical"}


def validate_businesses(doc):
    p = []
    if not isinstance(doc, dict) or doc.get("schema") != "pnf.business.v1" or not isinstance(doc.get("businesses"), list):
        return ["businesses file: schema must be pnf.business.v1 with a businesses list"]
    for b in doc["businesses"]:
        extra = set(b) - BUSINESS_KEYS
        if extra:
            p.append(f"{b.get('prospect_id')}: business-level fields only, found {sorted(extra)}")
        if b.get("product") not in R.PRODUCTS:
            p.append(f"{b.get('prospect_id')}: unknown product")
        else:
            p += [f"{b.get('prospect_id')}: {m}" for m in R.trade_problems(b["product"], R.trade_of(b))]
        if not R.domain_of(b.get("website")):
            p.append(f"{b.get('prospect_id')}: no website")
        if "@" in json.dumps(b):
            p.append(f"{b.get('prospect_id')}: an email address in a business-level file")
    return p


def to_prospects(rows, product, source):
    kept, rejected = {}, 0
    for row in rows:
        p = PI.to_prospect(PI.map_row(row), product, source)
        if R.validate_prospect(p) or p["prospect_id"] in kept:
            rejected += 1
            continue
        kept[p["prospect_id"]] = p
    return kept, rejected


def load_box(path, key):
    """The previous run's sealed result, so named prospects carry forward; empty when there is none yet."""
    try:
        doc = json.loads(data_box.unseal(json.load(open(path, encoding="utf-8")), key).decode("utf-8"))
    except (OSError, ValueError, KeyError, SystemExit, Exception):
        return {}, {}
    if doc.get("schema") != "pnf.prospect.v1":
        return {}, {}
    return ({x["prospect_id"]: x for x in doc.get("prospects", [])},
            {x["prospect_id"]: x for x in doc.get("pending", [])})


def load_state(path):
    try:
        doc = json.load(open(path, encoding="utf-8"))
        return doc.get("domains", {}) if doc.get("schema") == "pnf.enrich_state.v1" else {}
    except (OSError, ValueError):
        return {}


def site_owner_record(b, st, today):
    """Rung 2b for one business: (pending record or None, outcome). Reads the site once and marks siteOwnerAt."""
    import site_owners   # imported here so the ladder runs without the rung's libraries when the rung is off
    dom = R.domain_of(b["website"])
    st["siteOwnerAt"] = today.isoformat()
    try:
        pages = site_emails.fetch_pages(dom, paths=site_owners.PATHS)
        owner, _reason = site_owners.find_owner(pages) if pages else (None, "no pages")
    except Exception:
        return None, "error"
    if not owner:
        return None, "none"
    addr, _kind = site_emails.choose(site_emails.collect_from(pages, dom), dom, owner, "site_about")
    if not addr:
        return None, "no address"
    rec = ladder_record(b, owner, "site_about", addr)
    return (None, "rejected") if R.validate_prospect(rec, pending=True) else (rec, "named")


def ladder_record(b, owner, owner_source, email):
    """A pending prospect (address waiting for Bouncer) from a business row, its owner and a site address."""
    return {"prospect_id": b["prospect_id"], "product": b["product"], "business": b["business"],
            "website_domain": R.domain_of(b["website"]), "city": R.PRODUCTS[b["product"]],
            "first_name": owner["first_name"], "last_name": owner["last_name"], "title": owner["title"],
            "email": email, "email_source": "site", "email_status": R.PENDING_STATUS, "owner_source": owner_source,
            "source_url": "", "do_not_email": False, "status": "candidate",
            "trade_vertical": R.trade_of(b), "importedAt": dt.date.today().isoformat()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--businesses", default=BUSINESSES)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--state", default=STATE)
    ap.add_argument("--limit", type=int, default=400, help="businesses read per run (the free rungs)")
    ap.add_argument("--hunter-max", type=int, default=5, help="Hunter domain searches per run (the paid fallback)")
    ap.add_argument("--retry-days", type=int, default=28, help="days before a business with no owner is tried again")
    ap.add_argument("--site-owners", action="store_true", help="rung 2b: owner names the business publishes on its site")
    a = ap.parse_args()
    key = data_box.passphrase()   # exits 1 before any paid API call when the box cannot be sealed
    hunter, apollo = os.environ.get("HUNTER_API_KEY", ""), os.environ.get("APOLLO_API_KEY", "")
    drops = sorted(glob.glob(os.path.join(DROPS, "*.csv")))
    try:
        doc = json.load(open(a.businesses, encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"ERROR enrich: cannot read {a.businesses} ({type(e).__name__})")
        sys.exit(1)
    probs = validate_businesses(doc)
    if probs:
        for p in probs[:20]:
            print(f"ERROR enrich: {p}")
        sys.exit(1)

    found, pending = load_box(a.out, key)
    state = load_state(a.state)
    today = dt.date.today()
    have = {x["website_domain"] for x in list(found.values()) + list(pending.values())}
    todo = []
    for b in doc["businesses"][: a.limit]:
        dom = R.domain_of(b["website"])
        st = state.get(dom, {})
        if dom in have or b["prospect_id"] in found or b["prospect_id"] in pending:
            continue
        if st.get("checkedAt") and (today - dt.date.fromisoformat(st["checkedAt"])).days < a.retry_days and not (
                hunter and not st.get("hunterAt")) and not (a.site_owners and not st.get("siteOwnerAt")):
            continue
        todo.append(b)
    counts = {"businesses": len(todo), "city": 0, "site": 0, "site_owner": 0, "hunter": 0, "apollo": 0, "csv": 0, "rejected": 0,
              "hunter_searched": 0, "carried": len(found) + len(pending)}

    # rung 1: the City's owner record (Chicago products)
    owners = {}
    def fresh(b):
        at = state.get(R.domain_of(b["website"]), {}).get("checkedAt")
        return bool(at) and (today - dt.date.fromisoformat(at)).days < a.retry_days
    # the free rungs skip a business tried within --retry-days; such a business is in todo only for its Hunter turn
    chicago = [b for b in todo if R.PRODUCTS.get(b["product"]) == "chicago" and not fresh(b)]
    if chicago:
        try:
            owners = owners_chicago.find(chicago)
        except Exception as e:   # the portal being down must not cost the Hunter rung or the carried prospects
            print(f"NOTE enrich: City owner records unavailable this run ({type(e).__name__})")
    # rung 2: the business's own site, for each owner found
    left = []
    for b in todo:
        dom = R.domain_of(b["website"])
        owner = owners.get(dom)
        rec = None
        if owner and not fresh(b):
            addr, _kind = site_emails.choose(site_emails.collect(dom), dom, owner, "city_owner_record")
            if addr:
                rec = ladder_record(b, owner, "city_owner_record", addr)
        if rec and not R.validate_prospect(rec, pending=True):
            pending[rec["prospect_id"]] = rec
            counts["city"] += 1
            counts["site"] += 1
            state[dom] = {"checkedAt": today.isoformat(), "result": "named", "rung": "city+site",
                          "hunterAt": state.get(dom, {}).get("hunterAt", "")}
        else:
            if rec:
                counts["rejected"] += 1
            left.append(b)
    # rung 2b: owner names the business publishes on its own site, each domain once (--site-owners)
    if a.site_owners:
        still = []
        for b in left:
            dom = R.domain_of(b["website"])
            st = state.setdefault(dom, {})
            if st.get("siteOwnerAt"):
                still.append(b)
                continue
            rec, outcome = site_owner_record(b, st, today)
            if rec:
                pending[rec["prospect_id"]] = rec
                counts["site_owner"] += 1
                st.update({"checkedAt": today.isoformat(), "result": "named", "rung": "site_owner"})
            else:
                counts["rejected"] += outcome == "rejected"
                still.append(b)
        left = still
    # rung 3: Hunter, capped, each domain at most once, valid addresses only
    try:
        for b in left:
            dom = R.domain_of(b["website"])
            st = state.setdefault(dom, {})
            got = []
            if hunter and not st.get("hunterAt") and counts["hunter_searched"] < a.hunter_max:
                counts["hunter_searched"] += 1
                got, _miss = enrich_hunter.enrich([b], hunter)
                st["hunterAt"] = today.isoformat()
            elif apollo:
                got, _miss = enrich_apollo.enrich([b], apollo)
            kept, rej = to_prospects(got, b["product"], "hunter" if got and got[0].get("Source") == "hunter" else "apollo")
            counts["rejected"] += rej
            for p in kept.values():
                p["prospect_id"] = b["prospect_id"]
                p["owner_source"] = p["email_source"]
                found[p["prospect_id"]] = p
                counts[p["email_source"]] += 1
            st["checkedAt"] = today.isoformat()
            st["result"] = "named" if kept else "none"
            st["rung"] = "hunter" if kept else (st.get("rung") or "none")
    except RuntimeError as e:
        print(f"ERROR enrich: an API call failed ({str(e).split(':')[-1].strip()})")
        sys.exit(1)
    for path in drops:
        product = next((p for p in R.PRODUCTS if os.path.basename(path).startswith(p)), None)
        if not product:
            print(f"ERROR enrich: {os.path.basename(path)} must start with a product key ({', '.join(sorted(R.PRODUCTS))})")
            sys.exit(1)
        with open(path, newline="", encoding="utf-8-sig") as f:
            kept, rej = to_prospects(list(csv.DictReader(f)), product, "manual")
        kept = {k: v for k, v in kept.items() if k not in found}
        counts["csv"] += len(kept)
        counts["rejected"] += rej
        found.update(kept)

    trade = {(b["product"], R.domain_of(b["website"])): R.trade_of(b) for b in doc["businesses"]}
    for x in list(found.values()) + list(pending.values()):
        x["trade_vertical"] = trade.get((x["product"], x["website_domain"]), x.get("trade_vertical") or R.TRADE_DEFAULT)
    # one business, one decision-maker: a verified contact replaces a pending one
    for pid in [p for p in pending if p in found]:
        del pending[pid]
    out = {"schema": "pnf.prospect.v1", "prospects": sorted(found.values(), key=lambda x: x["prospect_id"]),
           "pending": sorted(pending.values(), key=lambda x: x["prospect_id"])}
    probs = R.validate_prospect_file(out)
    if probs:
        print(f"ERROR enrich: the result fails validation ({len(probs)} problems; first: {probs[0].split(':')[-1].strip()})")
        sys.exit(1)
    box = data_box.seal(json.dumps(out).encode("utf-8"), key)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(box, f, indent=1)
        f.write("\n")
    with open(a.state, "w", encoding="utf-8") as f:
        json.dump({"schema": "pnf.enrich_state.v1", "note": "Business-level only: which domains each rung has tried.",
                   "domains": dict(sorted(state.items()))}, f, indent=1)
        f.write("\n")
    print(f"OK enrich: {len(out['prospects'])} verified and {len(out['pending'])} waiting for Bouncer "
          f"({counts['carried']} carried forward; this run: {counts['businesses']} businesses tried, city+site {counts['city']}, "
          f"site owner {counts['site_owner']}, "
          f"hunter {counts['hunter']} from {counts['hunter_searched']} searches, apollo {counts['apollo']}, csv {counts['csv']}, "
          f"rejected {counts['rejected']})")
    sys.exit(0)


if __name__ == "__main__":
    main()
