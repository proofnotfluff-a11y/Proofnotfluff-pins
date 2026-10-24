#!/usr/bin/env python3
"""Owner names a business publishes on its own website (the free owner-name rung, Todd, Oct 24, 2026, "go 1 to 4",
coo/DECISIONS-2026-10-24.md item 1). Runs inside GitHub Actions only (tools/enrich_ci.py --site-owners, or the
counts-only dry run below), after the City's owner record and before Hunter.

What it reads, from the pages tools/site_emails.py fetches (home, about, team, story, contact):
  1. schema.org data the business publishes (extruct, JSON-LD and microdata only): a founder or founders field, or a
     Person whose jobTitle names an owner role.
  2. the visible text (spaCy en_core_web_sm): a PERSON named within a few words of owner, co-owner, founder,
     co-founder, "founded by", president, CEO or proprietor, in the same sentence. Testimonial and review blocks are
     dropped first, and customer phrases ("business owner", "home owner", "former owner", "vice president") never count.
  3. probablepeople then decides person versus company: only a Person with a given name and a surname passes, and both
     must pass pnf_rules.NAME_RE with at least two letters each.
The owner's address comes only from tools/site_emails.py: the owner's own published address, else a published
owner-read inbox (owner_source "site_about", pnf_rules.owner_read_inbox). No address is ever guessed.

Names are personal data: they stay in the runner and leave it only inside the sealed box (tools/data_box.py). Nothing
here prints a name, an address, page text or an error message; output is counts only. The libraries never see the
network: every parse runs inside no_network(), which refuses any socket the parsing code tries to open.

Libraries: tools/requirements-owner-rung.txt, pinned by hash, Python 3.13 (audit Oct 24, legal/reviews/2026-10-24-owner-rung-libraries.md).

Usage as a library: site_owners.find_owner(pages) -> (owner or None, reason)
       python3 tools/site_owners.py --selftest
       python3 tools/site_owners.py --dry-run [--businesses prospects/businesses.json] [--state prospects/enrich_state.json]
"""
import argparse
import collections
import concurrent.futures as cf
import contextlib
import json
import os
import re
import socket
import sys
import warnings

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pnf_rules as R  # noqa: E402
import site_emails  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATHS = ("", "about", "about-us", "our-team", "team", "our-story", "contact", "contact-us")
# owner words, best first, and the title we store (each passes pnf_rules.DECISION_TITLE)
ROLES = [("co-owner", "Co-Owner"), ("coowner", "Co-Owner"), ("owner/operator", "Owner"), ("owner-operator", "Owner"),
         ("owner / operator", "Owner"), ("owner", "Owner"), ("proprietor", "Owner"),
         ("owned and operated by", "Owner"), ("owned by", "Owner"),
         ("co-founder", "Co-Founder"), ("cofounder", "Co-Founder"), ("founded by", "Founder"), ("founder", "Founder"),
         ("president", "President"), ("ceo", "CEO"), ("chief executive officer", "CEO")]
RANK = {"Owner": 0, "Co-Owner": 1, "Founder": 2, "Co-Founder": 3, "President": 4, "CEO": 5}
ROLE_RX = re.compile(r"\b(co-?owner|owner\s*/\s*operator|owner-operator(?!d)|owner|proprietor|owned and operated by|owned by|co-?founder|founded by|founder|president|ceo|"
                     r"chief executive officer)\b", re.I)
# a customer or a past holder, never the business's owner
NOT_OURS = re.compile(r"\b(?:business|home|property|building|restaurant|store|shop|office|facility|hotel|bar|gym|salon|"
                      r"company|small[- ]business|land|pet|dog|car|vehicle|former|previous|past|prior|new|vice|"
                      r"assistant|deputy|chapter|association|club|board|chamber)\s+(?:co-?owner|owner|president|founder)\b"
                      r"|\b(?:owners?|president|founder)\s+of\s+(?:the\s+)?(?:a|an|another|several|many|local)\b"
                      r"|\bowners?\s+of\s+(?:the|this|that|his|her|their)\s+(?:property|building|home|house)\b", re.I)
DROP_BLOCKS = re.compile(r"testimonial|review|quote|rating|comment|feedback|client-say|clients-say|what-our|slide|swiper|"
                         r"slick|carousel|owl-|trustindex|elfsight|yelp|google|stars|project|portfolio|case-stud|gallery",
                         re.I)
# lines that are a project card, a credit or a login link, never the business's own owner
DROP_LINES = re.compile(r"\b(?:architect|general contractor|square feet|sq\.? ?ft|completed in|client:|website by|"
                        r"designed by|powered by|built by|log ?in)\b", re.I)
PROJECT_LABEL = re.compile(r"\s*(?:architect|general contractor|gc|client|square feet|sq\.? ?ft|completed|scope|"
                           r"location|project|budget)\s*:", re.I)
# a founder from long ago or one who has died is not who reads the inbox
PAST = re.compile(r"\b(?:memory|memoriam|late|passed|legacy|grand(?:father|mother)|father|mother|in (?:18|19)\d\d|"
                  r"retired|took over|bought|sold|acquired|from (?:our )?founder|since (?:18|19|20)\d\d)\b", re.I)
# a sentence about a customer, a client or a supplier: its owner is not this business's owner
CUSTOMER = re.compile(r"\b(?:client|customer|homeowner|landlord|tenant|supplier|vendor|farm|property|remodel|renovation|"
                      r"replied|called|wanted|chose|pleased|hired us|thanks|thank you)\b|"
                      r"\b(?:this|that|his|her|their)\s+project\b", re.I)
# the only words allowed before a role word that binds to the name after it
PREFIX_OK = re.compile(r"(?:^|[.:;!?]|\b(?:our|the|meet|and|with)\b|&|\s-|\|)\s*[,:]?\s*$", re.I)
JOB_ONLY = re.compile(r"^\s*(?:co-?owner|owner|proprietor|operator|co-?founder|founder|president|ceo|"
                      r"chief executive officer)(?:\s*(?:&|and|/|,)\s*(?:co-?owner|owner|operator|co-?founder|founder|"
                      r"president|ceo))*\s*$", re.I)
# what may sit between a name and its owner word: a comma, a colon, a bracket, "is the", "our"
BEFORE_OK = re.compile(r"^[\s,:(|]*(?:\s-\s*)?(?:is\s+(?:now\s+)?)?(?:the\s+|our\s+)?$", re.I)
AFTER_OK = re.compile(r"^[\s,:]*(?:is\s+)?$", re.I)
BUSINESS_TYPES = re.compile(r"organization|business|restaurant|contractor|service|store|company|corporation|"
                            r"cleaning|plumber|electrician|roofing|establishment|place", re.I)
NESTED_NOT_OURS = {"review", "reviews", "author", "comment", "comments", "itemreviewed", "creator", "publisher",
                   "contributor", "editor", "sponsor", "funder", "brand", "manufacturer"}
# a word that makes a name a business, not a person (probablepeople alone reads "Sparkle Co" as a person)
BIZ_WORDS = {"co", "inc", "llc", "ltd", "corp", "corporation", "company", "group", "services", "service", "cleaning",
             "cleaners", "clean", "janitorial", "maids", "maid", "solutions", "enterprises", "enterprise", "pros", "pro",
             "construction", "builders", "contractors", "contracting", "pest", "control", "exterminating", "restaurant",
             "kitchen", "grill", "cafe", "bar", "the", "and", "of", "chicago", "austin", "texas", "illinois", "team",
             "crew", "family", "partners", "associates", "holdings", "management", "facility", "facilities", "commercial",
             "residential", "window", "windows", "dumpster", "security", "office", "studio", "shop", "store", "us", "our"}
MAX_BLOCKS = 60     # text blocks with an owner word read per site
MAX_BLOCK_CHARS = 600
PERSON_TYPES = ("person",)
_NLP = None


class NetworkRefused(RuntimeError):
    pass


@contextlib.contextmanager
def no_network(counter=None):
    """Refuse any socket opened while parsing; counter["attempts"] records tries."""
    saved = (socket.socket.connect, socket.socket.connect_ex, socket.create_connection, socket.getaddrinfo)

    def refuse(*a, **k):
        if counter is not None:
            counter["attempts"] = counter.get("attempts", 0) + 1
        raise NetworkRefused("network refused while parsing")
    socket.socket.connect = refuse
    socket.socket.connect_ex = refuse
    socket.create_connection = refuse
    socket.getaddrinfo = refuse
    try:
        yield
    finally:
        socket.socket.connect, socket.socket.connect_ex, socket.create_connection, socket.getaddrinfo = saved


def nlp():
    global _NLP
    if _NLP is None:
        import spacy
        warnings.filterwarnings("ignore")
        _NLP = spacy.load("en_core_web_sm", disable=["lemmatizer"])
    return _NLP


def title_for(word):
    w = re.sub(r"\s*/\s*", "/", re.sub(r"\s+", " ", word.lower())).strip()
    return next((t for k, t in ROLES if k == w), "")


def person_name(raw):
    """{first_name, last_name} when probablepeople reads raw as one person with a given name and a surname, else None."""
    import probablepeople
    s = re.sub(r"\s+", " ", str(raw or "")).strip(" ,.;:-")
    s = re.sub(r"^(?:mr|mrs|ms|miss|dr)\.?\s+", "", s, flags=re.I)
    if re.search(r"\b(?:sr|senior|ii|iii|iv)\b\.?", s, re.I):
        return None   # a Sr. or a numbered name is usually the founder of an older generation
    s = re.sub(r",?\s+jr\.?$", "", s, flags=re.I)
    if not s or len(s) > 60 or any(ch.isdigit() for ch in s) or "@" in s or len(s.split()) > 4:
        return None
    if any(w.lower().strip(".,&'") in BIZ_WORDS for w in s.split()):
        return None
    try:
        tags, kind = probablepeople.tag(s)
    except Exception:
        return None
    if kind != "Person" or any(k.startswith("Corporation") for k in tags):
        return None
    first, last = tags.get("GivenName", ""), tags.get("Surname", "")
    if not first or not last or "LastInitial" in tags or "FirstInitial" in tags:
        return None
    fix = lambda x: x.title() if x.isupper() or x.islower() else x
    first, last = fix(first.strip(" .,")), fix(last.strip(" .,"))
    for part in (first, last):
        if not R.NAME_RE.match(part) or sum(c.isalpha() for c in part) < 2:
            return None
    if last.lower() == "doe":
        return None   # theme placeholder ("John Doe")
    return {"first_name": first, "last_name": last}


def _items(node):
    """(dict, keys above it) for every dict inside JSON-LD or microdata output, microdata items flattened to their
    properties."""
    stack = [(node, ())]
    while stack:
        x, keys = stack.pop()
        if isinstance(x, list):
            stack.extend((v, keys) for v in x)
        elif isinstance(x, dict):
            if isinstance(x.get("properties"), dict):
                d = dict(x["properties"])
                d.setdefault("@type", x.get("type"))
            else:
                d = x
            stack.extend((v, keys + (str(k).lower(),)) for k, v in d.items())
            yield d, keys


def _type(d):
    t = d.get("@type") or d.get("type") or ""
    return (" ".join(t) if isinstance(t, list) else str(t)).lower()


def _on_site(d, domain):
    url = d.get("url") or d.get("@id") or ""
    url = url[0] if isinstance(url, list) and url else url
    return not domain or not isinstance(url, str) or not url.startswith("http") or R.domain_of(url) == domain


def _is_person(d):
    return any(p in _type(d).rsplit("/", 1)[-1] for p in PERSON_TYPES)


def _first_word(name):
    w = [x for x in re.sub(r"[^a-z0-9 ]", " ", str(name or "").lower()).split() if x not in {"the", "a", "and", "of"}]
    return w[0] if w else ""


def structured_candidates(html, domain="", business=""):
    from extruct.jsonld import JsonLdExtractor
    from extruct.w3cmicrodata import MicrodataExtractor
    data = []
    for ex in (JsonLdExtractor(), MicrodataExtractor()):
        try:
            data.append(ex.extract(html))
        except Exception:
            pass
    nodes = [(d, keys) for d, keys in _items(data) if not NESTED_NOT_OURS & set(keys)]
    # an author, creator or publisher referenced by @id anywhere is the site's author or agency, not its owner
    cited = set()
    for d, keys in _items(data):
        if NESTED_NOT_OURS & set(keys) and isinstance(d.get("@id"), str):
            cited.add(d["@id"])
    biz = [d for d, _ in nodes if BUSINESS_TYPES.search(_type(d)) and not _is_person(d)]

    def ours(d):
        url = d.get("url") or ""
        url = url[0] if isinstance(url, list) and url else url
        if isinstance(url, str) and url.startswith("http"):
            return bool(domain) and R.domain_of(url) == domain
        named = _first_word(business) and _first_word(d.get("name")) == _first_word(business)
        return named or len(biz) == 1   # no url: ours only if it names us or is the page's only business
    out = []
    for d in biz:
        if not ours(d):
            continue
        for key in ("founder", "founders"):
            for f in (d.get(key) if isinstance(d.get(key), list) else [d.get(key)]):
                if isinstance(f, dict) and f.get("@id") in cited:
                    continue
                name = f.get("name") if isinstance(f, dict) else f
                p = person_name(name) if isinstance(name, str) else None
                if p:
                    out.append(dict(p, title="Founder", via="structured"))
    for d, _keys in nodes:
        if not (_is_person(d) and isinstance(d.get("name"), str)) or d.get("@id") in cited:
            continue
        jt = d.get("jobTitle")
        jt = " ".join(jt) if isinstance(jt, list) else str(jt or "")
        p = person_name(d["name"])
        if p and JOB_ONLY.match(jt) and _on_site(d, domain):
            m = ROLE_RX.search(jt)
            if m:
                out.append(dict(p, title=title_for(m.group(1)), via="structured"))
    return out


def text_blocks(html):
    """Visible text blocks that carry an owner word, with testimonial and review blocks removed."""
    import lxml.html
    import html_text
    try:
        tree = lxml.html.fromstring(html)
    except Exception:
        return []
    for el in tree.xpath("//script|//style|//noscript|//template|//blockquote|//q|//cite|//form|//footer|//nav"):
        el.drop_tree()
    for el in tree.xpath("//*[@class or @id]"):
        if el.getparent() is not None and DROP_BLOCKS.search(f"{el.get('class', '')} {el.get('id', '')}"):
            el.drop_tree()
    text = html_text.extract_text(tree, guess_layout=True)
    blocks = [re.sub(r"\s+", " ", b).strip() for b in re.split(r"\n+", text)]
    blocks = [b.title() if sum(c.isupper() for c in b) > 0.8 * max(1, sum(c.isalpha() for c in b)) else b for b in blocks]
    for i in range(1, len(blocks)):
        # a team card: the name on one line, the title alone on the next
        if JOB_ONLY.match(blocks[i]) and blocks[i - 1] and len(blocks[i - 1].split()) <= 4 \
                and not ROLE_RX.search(blocks[i - 1]):
            blocks[i] = f"{blocks[i - 1]}, {blocks[i]}"
    if any(PROJECT_LABEL.match(b) for b in blocks):
        # a project page: "Owner: ..." there is the client who owned the building
        blocks = [b for b in blocks if not re.match(r"\s*(?:co-?owner|owner)\s*:", b, re.I)]
    return [b[:MAX_BLOCK_CHARS] for b in blocks if b and ROLE_RX.search(b) and not DROP_LINES.search(b)
            and not re.search("[\"\u201c\u201d\u2018\u2019\u00ab\u00bb]", b)]


def spans(sent):
    """Name-shaped spans in a sentence: spaCy PERSON and ORG entities (the small model often tags a person as ORG) and
    runs of two or three proper nouns. probablepeople decides afterwards which are people."""
    out = [e for e in sent.ents if e.label_ in ("PERSON", "ORG")]
    taken = {i for e in out for i in range(e.start, e.end)}
    run = []
    for tok in list(sent) + [None]:
        if tok is not None and tok.pos_ == "PROPN" and tok.i not in taken and tok.text[:1].isupper():
            run.append(tok)
            continue
        if 2 <= len(run) <= 3:
            out.append(sent.doc[run[0].i:run[-1].i + 1])
        run = []
    return sorted(out, key=lambda e: e.start_char)


def _of_other(s, re_, business):
    """True when the owner word is followed by "of X", "at X" or ", X" and X is not this business."""
    m = re.match(r"\s*(?:,\s*|\s+(?:of|at)\s+(?:the\s+)?)([A-Z][\w&'.-]*(?:\s+[A-Z][\w&'.-]*){0,4})", s[re_:])
    if not m:
        return False
    tail = re.sub(r"[^a-z0-9 ]", "", m.group(1).lower()).split()
    own = [w for w in re.sub(r"[^a-z0-9 ]", "", (business or "").lower()).split() if w not in {"the", "and", "of"}]
    return not (own and tail and tail[0] == own[0])


def text_candidates(blocks, business=""):
    """People bound to an owner word. Each owner word binds to one name only: the name right after it if there is one
    ("owner Dana Reyes", "founded by Dana Reyes"), else the name right before it ("Dana Reyes, owner"), with nothing
    between them but a comma, a colon, a bracket or "is the"."""
    out = []
    for doc in nlp().pipe(blocks[:MAX_BLOCKS], batch_size=16):
        for sent in doc.sents:
            s = sent.text
            bad = [(m.start(), m.end()) for m in NOT_OURS.finditer(s)]
            roles_at = [(m.start(), m.end()) for m in ROLE_RX.finditer(s)]
            people = []   # (span, name) for spans probablepeople reads as a person, never a role word itself
            for e in spans(sent):
                es, ee = e.start_char - sent.start_char, e.end_char - sent.start_char
                hit = [rs for rs, re_ in roles_at if rs < ee and es < re_]
                if hit:   # the model ran the name into the role ("Dana Reyes - Owner"): keep the part before it
                    cut = s[es:min(hit)].rstrip(" -|,:(")
                    e = sent.doc.char_span(sent.start_char + es, sent.start_char + es + len(cut)) if cut else None
                    if e is None or min(hit) <= es:
                        continue
                    ee = e.end_char - sent.start_char
                if re.match(r"['\u2019]s\b", s[ee:]):
                    continue
                name = person_name(e.text)
                if name:
                    people.append((e, name))
            if CUSTOMER.search(s):
                continue   # a story about a client, a customer or a supplier
            own = set(re.sub(r"[^a-z0-9 ]", " ", (business or "").lower()).split())
            for m in ROLE_RX.finditer(s):
                rs, re_, word = m.start(), m.end(), m.group(1)
                if any(bs <= rs < be for bs, be in bad) or re.match(r"['\u2019]s\b", s[re_:]):
                    continue   # a customer's or past holder's role, or "the owner's son"
                pre = s[:rs]
                adj = re.search(r"([A-Za-z][\w'\u2019&.-]*)\s+$", pre)
                adj_ours = bool(adj) and re.sub(r"['\u2019]s$", "", adj.group(1)).lower().strip(".") in own
                if adj and adj.group(1)[0].isupper() and adj.start(1) > 0 and not adj_ours \
                        and adj.group(1).lower() not in {"our", "the", "meet", "and", "chef", "co"}:
                    continue   # "BBB President", "Hill Roofing owner": another organization's role
                if word.lower().endswith(" by") and not ((own and own & set(re.sub(r"[^a-z0-9 ]", " ", pre.lower()).split()))
                                                         or re.match(r"\s*(?:we|our)\b", s, re.I)):
                    continue   # "founded by" binds only in a sentence about us
                title = title_for(word)
                if title in ("Founder", "Co-Founder") and PAST.search(s):
                    continue
                after = [(e, n) for e, n in people if e.start_char - sent.start_char >= re_
                         and AFTER_OK.match(s[re_:e.start_char - sent.start_char])]
                if after and not (word.lower().endswith(" by") or adj_ours or PREFIX_OK.search(pre)):
                    continue   # "for owner X", "Forbes, CEO X": the role does not start a statement about us
                bound = after[:1]
                if not bound and not word.lower().endswith(" by"):
                    if _of_other(s, re_, business):
                        continue   # "Mike Brown, President of ABC Development": someone else's company
                    before = [(e, n) for e, n in people if e.end_char - sent.start_char <= rs
                              and BEFORE_OK.match(s[e.end_char - sent.start_char:rs])]
                    bound = before[-1:]
                for _e, name in bound:
                    out.append(dict(name, title=title, via="text"))
    return out


def find_owner(pages, counter=None, domain="", business=""):
    """(owner, reason). owner = {first_name, last_name, title, via, pages}. Structured data beats text; within each,
    the best title, then the most mentions. Two people tied on both is ambiguous: no owner."""
    counter = counter if counter is not None else {}
    with no_network(counter):
        try:
            structured, text = [], []
            for path, html in pages.items():
                structured += [dict(c, page=path) for c in structured_candidates(html, domain, business)]
            if not structured:
                seen = set()
                for path, html in pages.items():
                    blocks = [b for b in text_blocks(html) if b not in seen]
                    seen.update(blocks)
                    text += [dict(c, page=path) for c in text_candidates(blocks, business)]
        except NetworkRefused:
            return None, "network refused"
    cands = structured or text
    if not cands:
        return None, "no owner named"
    tally = collections.OrderedDict()
    for c in cands:
        k = (c["first_name"].lower(), c["last_name"].lower())
        if k not in tally:
            tally[k] = dict(c, n=0, pages=set())
        tally[k]["n"] += 1
        tally[k]["pages"].add(c["page"])
        if RANK[c["title"]] < RANK[tally[k]["title"]]:
            tally[k]["title"] = c["title"]
    ranked = sorted(tally.values(), key=lambda c: (RANK[c["title"]], -c["n"]))
    if len(ranked) > 1 and (RANK[ranked[0]["title"]], ranked[0]["n"]) == (RANK[ranked[1]["title"]], ranked[1]["n"]):
        return None, "ambiguous"
    best = {k: ranked[0][k] for k in ("first_name", "last_name", "title", "via")}
    best["pages"] = len(ranked[0]["pages"])
    return best, ("one person" if len(ranked) == 1 else "several people, best title kept")


# ---------------------------------------------------------------- counts-only dry run

def _baseline(state_path):
    d = json.load(open(state_path, encoding="utf-8")).get("domains", {})
    return sum(1 for v in d.values() if v.get("result") == "named"), len(d)


def _tried_none(state_path, businesses_path):
    state = json.load(open(state_path, encoding="utf-8")).get("domains", {})
    doc = json.load(open(businesses_path, encoding="utf-8"))
    seen, out = set(), []
    for b in doc["businesses"]:
        dom = R.domain_of(b.get("website"))
        st = state.get(dom)
        if dom and st and st.get("result") != "named" and dom not in seen:
            seen.add(dom)
            out.append((dom, b["product"], b.get("business", "")))
    return out


def dry_run(a):
    todo = _tried_none(a.state, a.businesses)[: a.limit]
    base = _baseline(a.state)
    c = collections.Counter()
    by_product = collections.defaultdict(collections.Counter)
    net = {}
    nlp()   # load once before the threads start fetching

    def fetch(item):
        try:
            return item, site_emails.fetch_pages(item[0], pause=a.pause, timeout=a.timeout, paths=PATHS,
                                                     stop_if_home_fails=True)
        except Exception:
            return item, {}
    batches = [todo[i:i + a.batch] for i in range(0, len(todo), a.batch)]
    for chunk in batches:
        # fetch the whole batch first, then parse with the network guard on: no fetch runs while a parse does
        with cf.ThreadPoolExecutor(max_workers=a.workers) as pool:
            fetched = list(pool.map(fetch, chunk))
        for (dom, product, business), pages in fetched:
            p = by_product[product]
            c["domains"] += 1
            p["domains"] += 1
            c["pages read"] += len(pages)
            if not pages:
                c["site did not answer"] += 1
                p["site did not answer"] += 1
                continue
            c["sites reached"] += 1
            try:
                owner, reason = find_owner(pages, net, dom, business)
            except Exception:
                owner, reason = None, "parse error"
            if not owner:
                c[f"no owner: {reason}"] += 1
                continue
            c["owner named"] += 1
            p["owner named"] += 1
            c[f"owner via {owner['via']}"] += 1
            c[f"title {owner['title']}"] += 1
            if owner["pages"] >= 2:
                c["owner named on 2+ of its own pages"] += 1
            if reason != "one person":
                c["owner chosen among several people"] += 1
            addr, kind = site_emails.choose(site_emails.collect_from(pages, dom), dom, owner, "site_about")
            rec_ok = False
            if addr:
                rec = {"prospect_id": "dry", "product": product, "business": "dry", "website_domain": dom,
                       "city": R.PRODUCTS.get(product, ""), "first_name": owner["first_name"],
                       "last_name": owner["last_name"], "title": owner["title"], "email": addr, "email_source": "site",
                       "email_status": R.PENDING_STATUS, "owner_source": "site_about", "source_url": "",
                       "do_not_email": False, "status": "candidate", "trade_vertical": R.TRADE_DEFAULT,
                       "importedAt": "2026-10-24"}
                rec_ok = not R.validate_prospect(rec, pending=True)
            if addr and rec_ok:
                c[f"usable: {kind}"] += 1
                p["usable"] += 1
            elif addr:
                c["address failed the Inbox Gate"] += 1
            else:
                c["owner named, no usable address on the site"] += 1
    c["network attempts refused while parsing"] = net.get("attempts", 0)
    usable = sum(v for k, v in c.items() if k.startswith("usable"))
    print(f"DRY RUN site owners (counts only, nothing stored or committed): {c['domains']} domains with no owner tried")
    for k in sorted(c):
        print(f"  {k}: {c[k]}")
    for prod in sorted(by_product):
        q = by_product[prod]
        print(f"  product {prod}: {q['domains']} tried, {q['owner named']} named, {q['usable']} with a usable address")
    print(f"YIELD: {c['owner named']} of {c['domains']} named an owner; {usable} of {c['domains']} have a usable "
          f"published address (the ladder had named {base[0]} of {base[1]} before)")
    return 0


# ---------------------------------------------------------------- selftest

SITE = "sparkleco.example"
CASES = [
    # (label, html, want first, want last, want title, want via) ; want first None means no owner
    ("JSON-LD founder", '<script type="application/ld+json">{"@context":"https://schema.org","@type":"LocalBusiness",'
     '"name":"Sparkle Co","founder":{"@type":"Person","name":"Dana Reyes"}}</script><p>We clean.</p>',
     "Dana", "Reyes", "Founder", "structured"),
    ("JSON-LD founders list as strings", '<script type="application/ld+json">{"@type":"Organization","founders":'
     '["Marcus Bell"]}</script>', "Marcus", "Bell", "Founder", "structured"),
    ("JSON-LD Person with owner jobTitle", '<script type="application/ld+json">[{"@type":"Person","name":"Priya Natarajan",'
     '"jobTitle":"Owner and Operator"}]</script>', "Priya", "Natarajan", "Owner", "structured"),
    ("microdata Person", '<div itemscope itemtype="https://schema.org/Person"><span itemprop="name">Elena Vasquez</span>'
     '<span itemprop="jobTitle">President</span></div>', "Elena", "Vasquez", "President", "structured"),
    ("JSON-LD founder that is a company", '<script type="application/ld+json">{"@type":"Organization","founder":'
     '"Bright Holdings LLC"}</script>', None, None, None, None),
    ("text: name then owner", "<p>Dana Reyes, owner of Sparkle Co, started the company in 2009.</p>",
     "Dana", "Reyes", "Owner", "text"),
    ("text: founded by", "<p>Sparkle Co was founded by Marcus Bell in 2012 after ten years in the trade.</p>",
     "Marcus", "Bell", "Founder", "text"),
    ("text: role then name", "<h3>Meet our owner, Priya Natarajan</h3><p>She runs every crew.</p>",
     "Priya", "Natarajan", "Owner", "text"),
    ("text: testimonial block dropped", '<div class="testimonials"><p>Great work. Mark Thompson, business owner</p></div>'
     "<p>We clean offices.</p>", None, None, None, None),
    ("text: customer owner phrase", "<p>Restaurant owner Mark Thompson calls us every spring.</p>",
     None, None, None, None),
    ("text: quoted review", '<p>"Best crew in town," says Mark Thompson, owner of a local bakery.</p>',
     None, None, None, None),
    ("text: vice president", "<p>Mark Thompson, vice president of sales, leads our bids.</p>", None, None, None, None),
    ("text: first name only", "<p>Dana, our owner, answers every call.</p>", None, None, None, None),
    ("text: person too far from the role", "<p>Dana Reyes joined us in 2015 and has since trained crews across "
     "the north side and the suburbs for the owner.</p>", None, None, None, None),
    ("text: two people, owner wins", "<p>Our office manager is Lisa Grant.</p><p>Marcus Bell, owner, handles every quote.</p>",
     "Marcus", "Bell", "Owner", "text"),
    ("structured beats text", '<script type="application/ld+json">{"@type":"LocalBusiness","founder":"Dana Reyes"}</script>'
     "<p>Marcus Bell, owner, handles every quote.</p>", "Dana", "Reyes", "Founder", "structured"),
    ("text: company beside owner", "<p>Bell Cleaning Group, owner-operated since 1998.</p>", None, None, None, None),
    ("text: heading with no person", "<h2>Talk to the Owner Today</h2><p>Call for a quote.</p>", None, None, None, None),
    ("text: owned and operated by", "<p>Sparkle Co is owned and operated by Dana Reyes, a Chicago native.</p>",
     "Dana", "Reyes", "Owner", "text"),
    ("text: family surname only", "<p>Family owned and operated by the Reyes family since 1990.</p>", None, None, None, None),
    ("text: label and colon", "<p>Owner: Priya Natarajan</p>", "Priya", "Natarajan", "Owner", "text"),
    ("text: CEO before name", "<p>CEO Marcus Bell started the firm with one van.</p>", "Marcus", "Bell", "CEO", "text"),
    # wrong-person phrasings from the Oct 24 review: each must name nobody, or the right person
    ("bound to the next name", "<p>Executive Chef John Carter and owner Maria Lopez run the kitchen.</p>",
     "Maria", "Lopez", "Owner", "text"),
    ("verb then owner (missed on purpose)", "<p>The league team is coached by owner Sam Ortiz every spring.</p>",
     None, None, None, None),
    ("two names around the role", "<p>Mia Francesca owner Scott Harris opened a second room.</p>", None, None, None, None),
    ("assistant to the owner", "<p>Lisa Grant, assistant to the owner, books every job.</p>", None, None, None, None),
    ("works for the owner (missed on purpose)", "<p>Lisa Grant manages the office for owner Dana Reyes.</p>",
     None, None, None, None),
    ("alongside the owner", "<p>Lisa Grant has worked alongside the owner since 2010.</p>", None, None, None, None),
    ("reports to the president", "<p>Lisa Grant reports directly to the president.</p>", None, None, None, None),
    ("relative of the owner", "<p>Ana Lopez, wife of owner Carlos, runs the front desk.</p>", None, None, None, None),
    ("the owner's son", "<p>Jose Garcia, the owner's son, leads crew two.</p>", None, None, None, None),
    ("owner's representative", "<p>John Smith, Owner's Representative</p>", None, None, None, None),
    ("project card with a class", '<div class="project-card"><p>Owner: John Smith</p><p>Architect: Studio K</p></div>',
     None, None, None, None),
    ("project card without a class", "<p>Owner: John Smith</p><p>Architect: Studio K</p><p>Completed: 2023</p>",
     None, None, None, None),
    ("president of a client", "<p>Mike Brown, President of ABC Development, hired us twice.</p>", None, None, None, None),
    ("testimonial slider", '<div class="swiper-slide"><p>Sarah Kim, Owner of Kim Dental</p></div>', None, None, None, None),
    ("curly single quotes", "<p>\u2018Great job\u2019 Mark Lee, owner, Lee Dental</p>", None, None, None, None),
    ("namesake restaurant", "<p>Lou Malnati's owner, Marc Malnati, greets every guest.</p>",
     "Marc", "Malnati", "Owner", "text", "Lou Malnati's"),
    ("founder in memory", "<p>In loving memory of our founder, Joe Smith.</p>", None, None, None, None),
    ("founder long ago", "<p>Founded by Giuseppe Rossi in 1952, we still use his recipes.</p>", None, None, None, None),
    ("founder senior", "<p>Joe Smith Sr., founder, opened the first shop.</p>", None, None, None, None),
    ("footer credit", "<footer>Website by Jane Webb | Owner Login</footer><p>We clean.</p>", None, None, None, None),
    ("review author in JSON-LD", '<script type="application/ld+json">{"@type":"LocalBusiness","review":{"@type":"Review",'
     '"author":{"@type":"Person","name":"Sarah Kim","jobTitle":"Owner, Kim Dental"}}}</script>'
     "<p>Dana Reyes, owner, answers every call.</p>", "Dana", "Reyes", "Owner", "text"),
    ("web agency founder", '<script type="application/ld+json">{"@type":"Organization","url":"https://webagency.example",'
     '"founder":"Pat Morgan"}</script><p>We clean.</p>', None, None, None, None),
    ("placeholder founder", '<script type="application/ld+json">{"@type":"LocalBusiness","founder":"John Doe"}</script>',
     None, None, None, None),
    ("two owners tied", "<p>Dana Reyes, owner, quotes jobs.</p><p>Marcus Bell, owner, runs crews.</p>",
     None, None, None, None),
    ("signature with our name", "<p>Dana Reyes, Owner, Sparkle Co</p>", "Dana", "Reyes", "Owner", "text"),
    # second review, Oct 24
    ("agency node with no url", '<script type="application/ld+json">[{"@type":"LocalBusiness","name":"Sparkle Co"},'
     '{"@type":"Organization","name":"Pixel Web Design","founder":"Jane Webb"}]</script><p>We clean.</p>',
     None, None, None, None),
    ("our node with no url", '<script type="application/ld+json">[{"@type":"LocalBusiness","name":"Sparkle Co",'
     '"founder":"Dana Reyes"},{"@type":"Organization","name":"Pixel Web Design","founder":"Jane Webb"}]</script>',
     "Dana", "Reyes", "Founder", "structured"),
    ("assistant jobTitle", '<script type="application/ld+json">{"@type":"LocalBusiness","employee":{"@type":"Person",'
     '"name":"Lisa Grant","jobTitle":"Assistant to the Owner"}}</script>', None, None, None, None),
    ("graph author as CEO", '<script type="application/ld+json">{"@graph":[{"@type":"WebPage","author":{"@id":"#p1"}},'
     '{"@type":"Person","@id":"#p1","name":"Jane Webb","jobTitle":"CEO"}]}</script>', None, None, None, None),
    ("another org's president", "<p>Award presented by BBB President Bob Jones last spring.</p>", None, None, None, None),
    ("franchisor CEO", "<p>Sparkle is a franchise of Jan-Pro. Jan-Pro CEO Jacques Lapointe visited.</p>",
     None, None, None, None),
    ("press mention", "<p>As featured by Forbes, CEO Jeff Bezos praised local trades.</p>", None, None, None, None),
    ("trained under another owner", "<p>Dana learned the trade under Hill Roofing owner Tom Hill.</p>",
     None, None, None, None),
    ("case study owner", "<p>For this kitchen remodel, owner Tom Hill wanted an open plan.</p>", None, None, None, None),
    ("customer call", "<p>When owner Tom Hill called about his flooded basement, we came that night.</p>",
     None, None, None, None),
    ("supplier owner", "<p>We buy all our produce from Green Acres Farm, owner Tom Hill.</p>", None, None, None, None),
    ("our client the owner", "<p>Our client, Tom Hill, the owner, was pleased.</p>", None, None, None, None),
    ("owner of the property", "<p>Tom Hill, owner of the property, chose us.</p>", None, None, None, None),
    ("owner replied", "<p>Owner Tom Hill replied: thanks!</p>", None, None, None, None),
    ("took over from founder", "<p>In 2018 Mike Brady took over from founder Tom Brady.</p>", None, None, None, None),
    ("bought from founder", "<p>Ann Lee bought the company from founder Joe Smith.</p>", None, None, None, None),
    ("retired founder, new owner", "<p>Our founder, Joe Smith, retired in 2015 and Ann Lee is now our owner.</p>",
     "Ann", "Lee", "Owner", "text"),
    ("team card on two lines", "<div><h4>Dana Reyes</h4><p>Owner</p></div>", "Dana", "Reyes", "Owner", "text"),
    ("dash form", "<p>Dana Reyes - Owner</p>", "Dana", "Reyes", "Owner", "text"),
    ("pipe form", "<p>Dana Reyes | Owner</p>", "Dana", "Reyes", "Owner", "text"),
    ("all caps label", "<p>OWNER: DANA REYES</p>", "Dana", "Reyes", "Owner", "text"),
    ("owner/operator", "<p>Owner/Operator Dana Reyes answers every call.</p>", "Dana", "Reyes", "Owner", "text"),
    ("business name before owner", "<p>Sparkle Co owner Dana Reyes started with one van.</p>",
     "Dana", "Reyes", "Owner", "text"),
    ("no owner anywhere", "<p>Commercial cleaning for offices and new builds.</p>", None, None, None, None),
    ("broken JSON-LD ignored", '<script type="application/ld+json">{"@type": "LocalBusiness", founder: }</script>'
     "<p>Nothing here.</p>", None, None, None, None),
]


def selftest():
    bad, n = [], 0

    def check(name, got, want):
        nonlocal n
        n += 1
        if got != want:
            bad.append(f"{name}: got {got!r}, want {want!r}")

    for case in CASES:
        label, html, first, last, title, via = case[:6]
        business = case[6] if len(case) > 6 else "Sparkle Co"
        owner, _reason = find_owner({"": html}, domain=SITE, business=business)
        got = (owner["first_name"], owner["last_name"], owner["title"], owner["via"]) if owner else None
        check(label, got, (first, last, title, via) if first else None)
    two = find_owner({"": "<p>Dana Reyes, owner, answers every call.</p>",
                      "about": "<h3>Meet our owner, Dana Reyes</h3>"}, domain=SITE, business="Sparkle Co")[0]
    check("owner counted on each page that names her", (two or {}).get("pages"), 2)
    # person versus company
    check("probablepeople person", person_name("DANA REYES"), {"first_name": "Dana", "last_name": "Reyes"})
    check("probablepeople company", person_name("Sparkle Cleaning LLC"), None)
    check("initial only refused", person_name("Mark T."), None)
    check("honorific dropped", person_name("Dr. Elena Vasquez"), {"first_name": "Elena", "last_name": "Vasquez"})
    # every title we store must pass the decision-maker gate
    check("titles pass DECISION_TITLE", all(R.DECISION_TITLE.search(t) for t in RANK), True)
    # the address comes only from what the site publishes; nothing is guessed
    owner = {"first_name": "Dana", "last_name": "Reyes"}
    check("owner's own published address", site_emails.choose(["dana@sparkleco.example", "info@sparkleco.example"], SITE,
                                                              owner, "site_about"), ("dana@sparkleco.example", "personal"))
    check("owner-read inbox for a site-named owner", site_emails.choose(["info@sparkleco.example"], SITE, owner, "site_about"),
          ("info@sparkleco.example", "owner-read inbox"))
    check("no address published, none guessed", site_emails.choose([], SITE, owner, "site_about")[0], None)
    check("someone else's address refused", site_emails.choose(["lisa@sparkleco.example"], SITE, owner, "site_about")[0], None)
    # parsing cannot reach the network
    tries = {}
    with no_network(tries):
        try:
            socket.create_connection(("192.0.2.1", 80), timeout=1)
            leaked = True
        except NetworkRefused:
            leaked = False
    check("sockets refused while parsing", (leaked, tries.get("attempts")), (False, 1))
    check("socket restored after parsing", socket.create_connection.__name__, "create_connection")
    if bad:
        for b in bad:
            print(f"ERROR site_owners selftest: {b}")
        sys.exit(1)
    print(f"site_owners selftest: PASS {n} checks")
    sys.exit(0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--businesses", default=os.path.join(ROOT, "prospects", "businesses.json"))
    ap.add_argument("--state", default=os.path.join(ROOT, "prospects", "enrich_state.json"))
    ap.add_argument("--limit", type=int, default=400)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--batch", type=int, default=40, help="domains fetched before each parsing pass")
    ap.add_argument("--pause", type=float, default=0.5)
    ap.add_argument("--timeout", type=float, default=12)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.dry_run:
        try:
            sys.exit(dry_run(a))
        except SystemExit:
            raise
        except Exception as e:   # the type only: a traceback could carry page text
            print(f"ERROR dry run: {type(e).__name__}")
            sys.exit(1)
    print(__doc__)
    sys.exit(1)


if __name__ == "__main__":
    main()
