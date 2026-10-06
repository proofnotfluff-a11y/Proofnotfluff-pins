#!/usr/bin/env python3
"""List a packed ProofNotFluff product on Etsy through the official API (no Chrome, no page cap).
Runs only in a cloud session on Todd's Default environment (see tools/etsy_oauth.py). Never prints secrets or tokens.

  python3 tools/etsy_list.py inspect LISTING_ID          read-only: the fields a new listing copies (who_made, when_made, taxonomy...)
  python3 tools/etsy_list.py taxonomy "Planner Templates"  read-only: seller taxonomy ids whose name matches
  python3 tools/etsy_list.py check listing.md            parse and validate listing.md, print the payload, call nothing
  python3 tools/etsy_list.py create listing.md product.zip img1.png ... img5.png [--video v.mp4] [--like LISTING_ID] [--publish]
        creates a DRAFT, uploads images in order, the zip as the digital file and the optional video, then
        with --publish sets it active ($0.20 listing fee). Without --publish it stays a draft for review.
  python3 tools/etsy_list.py publish LISTING_ID           sets an existing draft active
  python3 tools/etsy_list.py show LISTING_ID              read-only: state, title, price, images, files, url
  python3 tools/etsy_list.py retitle LISTING_ID "New title"   changes ONLY the title of a live listing (Todd-approved
        retitles only; log the old and new title in the ledger's Listing edits first). Prints old and new title.
  python3 tools/etsy_list.py strip-line LISTING_ID "phrase" [--dry-run]   correction edit: deletes the description
        line(s) containing the phrase (at most 2 lines, each under 300 characters); nothing else changes

Field defaults (who_made, when_made, is_supply, should_auto_renew, return_policy_id) are copied from --like
(default: a "Like: LISTING_ID" line under listing.md's ## Category, else #16, 4588972193) so every listing
matches what Etsy already accepted. Category: when the category name matches several Etsy nodes, the one the
like-listing uses wins; a "Like:" line in listing.md puts a trade edition in its parent listing's exact category.
"""
import json, mimetypes, os, re, sys, time, uuid, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import etsy_oauth as eo

API = eo.API
LIKE_DEFAULT = "4588972193"
CURRENT_PRICE = 2.99  # Todd, Oct 6, 3:23 pm: every product $2.99 while the shop gets established; change only on his word
PRICE_LADDER = [2.99, 4.99, 6.99, 8.99, 11.99, 12.99, 14.99, 19.99, 24.99, 49.00]
AI_LINE = "Made with AI assistance and reviewed and tested by the shop owner."
REQUIRED_LINES = [AI_LINE, "Digital download. No physical item ships."]
CATEGORY_TAXONOMY = {  # ledger category rule -> seller taxonomy name to search for
    "planner templates": "Planner Templates", "bookkeeping templates": "Bookkeeping Templates",
    "templates": "Templates", "résumé templates": "Résumé Templates", "resume templates": "Résumé Templates",
    "guides & how tos": "Guides & How Tos", "books > guides & how tos": "Guides & How Tos",
}

def die(m): eo.die(m)
def headers(extra=None):
    h = {"Authorization": f"Bearer {eo.access_token()}"}
    sec = os.environ.get("ETSY_SHARED_SECRET", "").strip()
    if sec: h["x-api-key"] = f"{eo.keystring()}:{sec}"
    if extra: h.update(extra)
    return h
def req(method, path, form=None, body=None, ctype=None):
    data = body if body is not None else (urllib.parse.urlencode(form).encode() if form is not None else None)
    h = headers({"Content-Type": ctype or "application/x-www-form-urlencoded"} if data is not None else None)
    for attempt in range(3):
        c, t = eo.call(f"{API}{path}", data=data, headers=h, method=method)
        if c == 429: time.sleep(2 + attempt * 2); continue
        return c, t
    return c, t
def ok(c, t, what):
    if c not in (200, 201): die(f"{what}: HTTP {c}: {t[:400]}")
    return json.loads(t) if t.strip() else {}
def shop_id():
    v = eo.load_vault()
    if v.get("shop_id"): return v["shop_id"]
    eo.cmd_me(); return eo.load_vault()["shop_id"]

def multipart(fields, file_field, path, mime=None):
    b = uuid.uuid4().hex; out = []
    for k, v in fields.items():
        out += [f"--{b}\r\n".encode(), f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode(), str(v).encode(), b"\r\n"]
    name = os.path.basename(path); mime = mime or mimetypes.guess_type(name)[0] or "application/octet-stream"
    out += [f"--{b}\r\n".encode(), f'Content-Disposition: form-data; name="{file_field}"; filename="{name}"\r\n'.encode(),
            f"Content-Type: {mime}\r\n\r\n".encode(), open(path, "rb").read(), b"\r\n", f"--{b}--\r\n".encode()]
    return b"".join(out), f"multipart/form-data; boundary={b}"

# ---------- listing.md ----------
def section(md, name):
    m = re.search(r"^## " + re.escape(name) + r"[^\n]*\n(.*?)(?=^## |\Z)", md, re.S | re.M)
    return m.group(1).strip() if m else ""
def parse(md_path):
    md = open(md_path, encoding="utf-8").read()
    title = section(md, "Title").splitlines()[0].strip()
    tags = [t.strip() for t in section(md, "Tags").replace("\n", ",").split(",") if t.strip()]
    cat_sec = section(md, "Category")
    cat = cat_sec.splitlines()[0].split("(")[0].strip() if cat_sec else ""
    lm = re.search(r"^Like:\s*(\d+)", cat_sec, re.M)  # an edition sits in its parent listing's exact category
    pm = re.search(r"List price:\s*\$([0-9]+(?:\.[0-9]{2})?)", section(md, "Price"))
    rp = re.search(r"Real price[^$]*\$([0-9]+(?:\.[0-9]{2})?)", section(md, "Price"))
    desc = section(md, "Description")
    return {"title": title, "tags": tags, "category": cat, "like": lm.group(1) if lm else None, "price": float(pm.group(1)) if pm else None,
            "realPrice": float(rp.group(1)) if rp else None, "description": desc,
            "pinFacts": [re.sub(r"^\d+\.\s*", "", l).strip() for l in section(md, "Pin facts").splitlines() if l.strip()],
            "board": section(md, "Pinterest board").splitlines()[0].strip() if section(md, "Pinterest board") else ""}
def validate(p):
    errs = []
    if not p["title"] or len(p["title"]) > 140: errs.append(f"title missing or over 140 characters ({len(p['title'])})")
    if len(p["tags"]) > 13: errs.append(f"{len(p['tags'])} tags (max 13)")
    errs += [f"tag over 20 characters: {t}" for t in p["tags"] if len(t) > 20]
    if p["price"] not in PRICE_LADDER: errs.append(f"price {p['price']} is not on the ledger price ladder")
    if CURRENT_PRICE is not None and p["price"] != CURRENT_PRICE:
        errs.append(f"price {p['price']} but the ledger PRICE rule (Todd, Oct 6) puts every product at ${CURRENT_PRICE}")
    low = p["description"].lower()
    for bad in ("founding price", "then $", "real price", "regular price", "was $"):
        if bad in low: errs.append(f"description names a former or future price ('{bad}'); the ledger PRICE rule forbids it")
    for line in REQUIRED_LINES:
        if line not in p["description"]: errs.append(f"description is missing: {line}")
    for field in ("title", "description"):
        if chr(0x2014) in p[field]: errs.append(f"em dash in {field}")
    if len(p["title"].split()) > 15: print(f"warning: title is {len(p['title'].split())} words; the COO title format asks for under 15", file=sys.stderr)
    if p["category"].lower() not in CATEGORY_TAXONOMY: errs.append(f"category '{p['category']}' is not in the ledger category rule")
    return errs

# ---------- read-only helpers ----------
def get_listing(lid):
    return ok(*req("GET", f"/listings/{lid}?includes=Images,Videos"), f"GET listing {lid}")
def taxonomy(name):
    nodes = ok(*req("GET", "/seller-taxonomy/nodes"), "seller taxonomy")["results"]; hits = []
    def walk(ns, path):
        for n in ns:
            p = path + [n["name"]]
            if n["name"].lower() == name.lower(): hits.append({"id": n["id"], "path": " > ".join(p)})
            walk(n.get("children") or [], p)
    walk(nodes, []); return hits

def cmd_inspect(lid):
    l = get_listing(lid)
    keep = ["listing_id", "state", "title", "type", "who_made", "when_made", "is_supply", "should_auto_renew", "taxonomy_id",
            "return_policy_id", "shop_section_id", "is_personalizable", "price"]
    print(json.dumps({k: l.get(k) for k in keep}, indent=1))

def cmd_show(lid):
    l = get_listing(lid); sid = shop_id()
    files = ok(*req("GET", f"/shops/{sid}/listings/{lid}/files"), "files")
    print(json.dumps({"state": l.get("state"), "title": l.get("title"), "price": l.get("price"), "tags": l.get("tags"),
                      "images": len(l.get("images") or []), "videos": len(l.get("videos") or []),
                      "files": [f.get("filename") for f in files.get("results", [])], "url": l.get("url")}, indent=1))

# ---------- create and publish ----------
def cmd_create(md, zip_path, images, video=None, like=None, publish=False):
    p = parse(md); errs = validate(p)
    if errs: die("listing.md failed checks:\n- " + "\n- ".join(errs))
    if not (1 <= len(images) <= 20): die("need 1 to 20 images (Etsy's per-listing limit is 20)")
    for f in [zip_path] + images + ([video] if video else []):
        if not os.path.exists(f): die(f"missing file: {f}")
    if os.path.getsize(zip_path) > 20 * 1024 * 1024: die("digital file over Etsy's 20 MB limit")
    if like is None: like = p.get("like") or LIKE_DEFAULT
    base = get_listing(like); sid = shop_id()
    tax = taxonomy(CATEGORY_TAXONOMY[p["category"].lower()])
    if p.get("like") and like == p["like"] and base.get("taxonomy_id"):
        # listing.md names its parent listing (Category "Like:" line): use that listing's exact category
        tax = [t for t in tax if t["id"] == base["taxonomy_id"]] or [{"id": base["taxonomy_id"], "path": f"same as listing {like}"}]
    elif len(tax) > 1 and base.get("taxonomy_id") in [t["id"] for t in tax]:
        tax = [t for t in tax if t["id"] == base["taxonomy_id"]]  # several nodes share the name: take the one the model listing uses
    if len(tax) != 1: die(f"taxonomy for '{p['category']}' matched {len(tax)} nodes: {tax}; add a 'Like: <listing id>' line under ## Category naming a listing in the right category")
    print(f"category: {tax[0]['path']} ({tax[0]['id']})")
    form = {"quantity": 999, "title": p["title"], "description": p["description"], "price": f"{p['price']:.2f}",
            "who_made": base["who_made"], "when_made": base["when_made"], "taxonomy_id": tax[0]["id"], "type": "download",
            "is_supply": str(bool(base.get("is_supply"))).lower(), "should_auto_renew": str(bool(base.get("should_auto_renew", True))).lower(),
            "tags": ",".join(p["tags"]), "is_personalizable": "false"}
    if base.get("return_policy_id"): form["return_policy_id"] = base["return_policy_id"]
    d = ok(*req("POST", f"/shops/{sid}/listings", form=form), "createDraftListing"); lid = d["listing_id"]
    print(f"draft {lid} created")
    for i, img in enumerate(images, 1):
        body, ct = multipart({"rank": i, "alt_text": p["title"][:250]}, "image", img)
        ok(*req("POST", f"/shops/{sid}/listings/{lid}/images", body=body, ctype=ct), f"image {i}")
    body, ct = multipart({"name": os.path.basename(zip_path), "rank": 1}, "file", zip_path, "application/zip")
    ok(*req("POST", f"/shops/{sid}/listings/{lid}/files", body=body, ctype=ct), "digital file")
    if video:
        body, ct = multipart({"name": os.path.basename(video)}, "video", video, "video/mp4")
        c, t = req("POST", f"/shops/{sid}/listings/{lid}/videos", body=body, ctype=ct)
        print("video uploaded" if c in (200, 201) else f"video not uploaded (HTTP {c}); listing continues without it")
    print(f"images {len(images)}, file 1 uploaded")
    if publish: cmd_publish(lid)
    else: print(f"left as a DRAFT: https://www.etsy.com/your/shops/me/listing-editor/edit/{lid}")
    print(json.dumps({"listing_id": lid, "url": f"https://www.etsy.com/listing/{lid}", "title": p["title"], "price": p["price"],
                      "realPrice": p["realPrice"], "board": p["board"], "pinFacts": p["pinFacts"]}))

def cmd_publish(lid):
    sid = shop_id()
    l = ok(*req("PATCH", f"/shops/{sid}/listings/{lid}", form={"state": "active"}), "publish")
    if l.get("state") != "active": die(f"publish returned state {l.get('state')}")
    print(f"PUBLISHED https://www.etsy.com/listing/{lid}")

def cmd_retitle(lid, title):
    title = title.strip()
    if not title or len(title) > 140: die("title missing or over 140 characters")
    if chr(0x2014) in title: die("em dash in title")
    if len(title.split()) > 15: print(f"warning: {len(title.split())} words; the COO title format asks for under 15", file=sys.stderr)
    old = get_listing(lid).get("title"); sid = shop_id()
    l = ok(*req("PATCH", f"/shops/{sid}/listings/{lid}", form={"title": title}), "retitle")
    if l.get("title") != title: die(f"Etsy returned a different title: {l.get('title')}")
    print(json.dumps({"listing_id": lid, "old": old, "new": title}))

def strip_lines(desc, phrase):
    """Remove every line of desc that contains phrase (case-insensitive), plus a blank line left
    doubled by the removal. Returns (new_desc, removed_lines)."""
    lines = desc.split("\n"); keep, removed = [], []
    for ln in lines:
        (removed if phrase.lower() in ln.lower() else keep).append(ln)
    out = "\n".join(keep)
    while "\n\n\n" in out: out = out.replace("\n\n\n", "\n\n")
    return out.strip("\n"), removed

def cmd_strip_line(lid, phrase, dry=False):
    """Correction edit: delete the description line(s) containing phrase. Refuses when the phrase is
    missing (nothing to do), when it matches more than 2 lines, or when a removed line is longer than
    300 characters (a whole paragraph would go). Never changes title, tags, price, photos or files."""
    l = get_listing(lid); desc = l.get("description") or ""
    new, removed = strip_lines(desc, phrase)
    if not removed: print(json.dumps({"listing_id": lid, "status": "absent", "phrase": phrase})); return
    if len(removed) > 2: die(f"phrase matches {len(removed)} lines; fix by hand: {removed}")
    if any(len(r) > 300 for r in removed): die(f"a matching line is over 300 characters; fix by hand: {removed}")
    if dry: print(json.dumps({"listing_id": lid, "status": "dry-run", "remove": removed})); return
    sid = shop_id()
    r = ok(*req("PATCH", f"/shops/{sid}/listings/{lid}", form={"description": new}), "strip-line")
    if phrase.lower() in (r.get("description") or "").lower(): die("Etsy still shows the phrase after the edit")
    print(json.dumps({"listing_id": lid, "status": "done", "removed": removed}))

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: die(__doc__)
    if a[0] == "inspect": cmd_inspect(a[1])
    elif a[0] == "taxonomy": print(json.dumps(taxonomy(a[1]), indent=1))
    elif a[0] == "check":
        p = parse(a[1]); e = validate(p); print(json.dumps(p, indent=1)[:3000]); print("OK" if not e else "FAIL:\n- " + "\n- ".join(e))
    elif a[0] == "create":
        args = a[1:]; video = like = None; pub = "--publish" in args; args = [x for x in args if x != "--publish"]
        if "--video" in args: i = args.index("--video"); video = args[i + 1]; del args[i:i + 2]
        if "--like" in args: i = args.index("--like"); like = args[i + 1]; del args[i:i + 2]
        cmd_create(args[0], args[1], args[2:], video, like, pub)
    elif a[0] == "publish": cmd_publish(a[1])
    elif a[0] == "show": cmd_show(a[1])
    elif a[0] == "retitle": cmd_retitle(a[1], a[2])
    elif a[0] == "strip-line": cmd_strip_line(a[1], a[2], dry="--dry-run" in a)
    else: die(__doc__)
