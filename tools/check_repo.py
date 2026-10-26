#!/usr/bin/env python3
"""Repo checks: the code gate every push goes through (.github/workflows/repo-checks.yml) and the nightly
optimizer runs first. Rule (Todd's Oct 15 note on agent harnesses): code decides wherever it can, a model
judges only where it must. Every check prints one line, "OK <name>" or "ERROR <name>: <detail>", so a run
can grep for ERROR; the exit code is 1 when anything failed.

Checks
  json          every JSON file the site and the crew read parses
  python        every tools/*.py compiles
  calc-tests    node docs/assets/pnf-calc.test.js passes (the free calculators' maths against the workbooks)
  site-sync     python3 tools/make_site.py on a clean copy reproduces the committed docs/ (someone edited
                site/pages.json or tools/make_site.py without rebuilding, or edited a generated page by hand);
                docs/go/index.html is skipped because its featured block follows the calendar
  drafts        draft pages (and leads pages without a Kit form) carry noindex and stay out of the sitemap,
                index and hub; live pages are in the sitemap without noindex
  sender-tests  node email/sender/test.js and test_glue.js pass (the Apps Script sender's caps, ramp, window,
                do-not-email, bounces, opt-outs, follow-up threading, through a simulated sending week)
  em-dash       no em dash in anything public: docs/, site/, email/, promo/specs/, agents/, services/
  secrets       no token or private key pattern in any tracked text file
  permit-data   permits/*/sample.json holds business-level fields only, and no scope text carries a
                reviewer, consultant, architect, engineer or owner tag (where a person's name can follow)
  builder-contacts  no plain permits/chicago/builder_contacts.json in the repo (it is public); builder_contacts.enc.json is a
                well-formed AES-256-GCM box and the do-not-list is a list of keys; with LEADS_PASSWORD set, the entries,
                decrypted in memory, keep tools/builder_contacts.py's rules: sources and sites on the builder's own domain
                (never a directory or social site), general inboxes only, no person, no em dash, do-not-list builders
                with no phone or email
  video-specs   tools/spec_lint.py on every promo/specs/ spec: the content playbook's hard rules for Proof Check shorts
                (make_demo.py refuses the same specs before rendering)
  voice         tools/voice_lint.py on the free site's page text (site/pages.json) and the email copy (email/): no
                AI-sounding phrase in anything public (the video specs and Fiverr copy get the same check in their own)
  fiverr-kit    tools/fiverr_kit.py: the paste-ready Fiverr copy in services/fiverr/ keeps to Fiverr's field limits
                and our rules (AI-assisted, not-advice and license lines; no links, contacts, review bait or
                off-Fiverr asks)
  context       tools/context_gate.py: Layer 0 CLAUDE.md and Layer 1 coo/HANDOFF.md under 2 KB, each
                .claude/skills/<job>/SKILL.md under 5 KB with Inputs, Process and Outputs sections, Layer 0 + Layer 1 + any
                one SKILL.md under 10,240 bytes, no legacy areas/digital-products*.md outside archive/
  moat          permits/downstream/gc_leads.json (when present): schema pnf.gc_lead.v1 and the Timing Moat Gate on every lead
  schema        Two-Entity Schema and Inbox Gate: no prospect data tracked in this public repo (data/ or a pnf.prospect.v1
                file), and a local data/prospects/prospects.json, when present, passes the named decision-maker rules
  copy          tools/copy_gate.py: every template in .claude/skills/outreach-drafter/templates.md (one or more per trade
                vertical in pnf_rules.TRADE_VERTICALS) renders under 75 words, link-free, downstream and permission-based,
                every live GC lead renders through each vertical allowed its stage and city, and a local
                data/work/drafts.json, when present, passes the same gate; signal products (pnf_rules.SIGNAL_PRODUCTS,
                email/L1-OUTREACH.md) get the same: templates, the live license sample, local data/work/signal_drafts.json
  monday        tools/monday_email.py --check: the free Monday email and the trial offer (email/M1-MONDAY.md) render for each
                city from the live GC leads, 2 or 3 fresh leads one per builder, no link, price or trial talk in the issue, the
                footer with our mailing address and stop line byte for byte, the trial email's one Gumroad link, price, 7 days,
                card and cancel lines; plus its planted selftest
  radar         the radar agent's code (Todd, Oct 23, 2026): tools/product_wire.py (no live lead page without a complete
                launches/WIRING.json entry; a non-legacy product missing any piece fails), tools/opportunity_score.py --check
                on scout/candidates/ and scout/reviews/, and the planted selftests of opportunity_score, product_wire,
                product_health and ai_visibility
  cos           tools/cos_agenda.py --selftest: the Chief of Staff's ranking (money, blockers, deadlines, Day 3 and Day 7
                nudges, at most 3 do-now items), its quiet rule, its gap finder and its privacy gate on everything it writes
                to the scoreboard (Todd, Oct 25, 2026); in the preflight for chief-of-staff
  gate-selftest tools/test_gates.py plants a failure for each of the four gates above and confirms each is caught
  gate-tests    tools/test_check_repo.py plants a failure for every check above in a throwaway copy and
                confirms each one is caught and no secret value is printed (Todd's Oct 15 note: the checks get
                tested too). An ERROR here means the gate itself is broken: tell Todd, never edit the gate to clear it

Usage: python3 tools/check_repo.py [--only name,name]
       python3 tools/check_repo.py --preflight <job>   the fast pre-run gate every scheduled run starts with: context
                                                       (with that job's SKILL.md), moat, schema, copy and gate-selftest
"""
import argparse, filecmp, glob, importlib.util, json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EM = "\u2014"
SECRETS = [("github_token", r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}"), ("anthropic_key", r"sk-ant-[A-Za-z0-9-]{10,}"),
           ("aws_key", r"AKIA[0-9A-Z]{16}"), ("slack_token", r"xox[baprs]-[A-Za-z0-9-]{10,}"), ("private_key", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
           ("etsy_token", r"\b\d{5,12}\.[A-Za-z0-9_-]{40,}"),
           ("etsy_key", r"(?i:ETSY_[A-Z_]*|keystring|shared[_-]?secret|refresh[_-]?token|access[_-]?token)[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9]{10,}")]
SECRET = re.compile("|".join(f"(?P<{k}>{v})" for k, v in SECRETS))
BINARY = re.compile(r"\.(png|jpe?g|gif|webp|ico|mp4|mov|mp3|wav|m4a|zip|pdf|xlsx|xls|docx|pptx|ttf|otf|woff2?|parquet|npz|onnx|bin)$", re.I)
PERSONAL_KEYS = re.compile(r"(phone|email|owner|contact_\d+|skip|ssn|dob)", re.I)
PERSON_TAG = re.compile(r"\b(?:reviewers?|consultants?|architects?|engineers?|owners?(?!['\u2019]s)|designers?|expeditors?|prepared by|drawn by|designed by|attn|c/o)\b", re.I)

results = []


def ok(name, detail=""):
    results.append(("OK", name, detail))


def err(name, detail):
    results.append(("ERROR", name, detail))


def tracked():
    try:
        out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        return [l for l in out.splitlines() if l]
    except Exception:
        return [os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, "**", "*"), recursive=True) if os.path.isfile(p)]


def check_json(files):
    want = [f for f in files if f.endswith(".json") and f.split("/")[0] in ("site", "permits", "promo", "cmo", "research", "ops")]
    bad = []
    for f in want:
        try:
            json.load(open(os.path.join(ROOT, f), encoding="utf-8"))
        except Exception as e:
            bad.append(f"{f} ({str(e)[:60]})")
    err("json", "; ".join(bad[:8])) if bad else ok("json", f"{len(want)} files")


def check_python(files):
    bad = []
    for f in files:
        if f.startswith("tools/") and f.endswith(".py"):
            try:
                compile(open(os.path.join(ROOT, f), encoding="utf-8").read(), f, "exec")
            except SyntaxError as e:
                bad.append(f"{f} line {e.lineno}: {e.msg}")
    err("python", "; ".join(bad[:8])) if bad else ok("python")


def check_calc():
    test = os.path.join(ROOT, "docs", "assets", "pnf-calc.test.js")
    if not os.path.exists(test):
        return ok("calc-tests", "no test file")
    if not shutil.which("node"):
        return err("calc-tests", "node is not installed here")
    r = subprocess.run(["node", test], cwd=ROOT, capture_output=True, text=True)
    fails = [l for l in (r.stdout + r.stderr).splitlines() if re.match(r"\s*(FAIL|not ok|Error|AssertionError)", l)]
    if r.returncode != 0 or fails:
        err("calc-tests", "; ".join(fails[:5]) or f"exit {r.returncode}")
    else:
        ok("calc-tests", f"{sum(1 for l in r.stdout.splitlines() if l.startswith('ok'))} passed")


def check_site_sync(files):
    if not os.path.exists(os.path.join(ROOT, "tools", "make_site.py")):
        return ok("site-sync", "no site")
    tmp = tempfile.mkdtemp(prefix="pnf-site-")
    try:
        for f in files:
            src = os.path.join(ROOT, f)
            if os.path.isfile(src):
                dst = os.path.join(tmp, f)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
        r = subprocess.run([sys.executable, os.path.join(tmp, "tools", "make_site.py")], cwd=tmp, capture_output=True, text=True)
        if r.returncode != 0:
            return err("site-sync", "make_site.py failed: " + (r.stderr.strip().splitlines() or ["?"])[-1][:120])
        differ, missing = [], []
        for dirpath, _, names in os.walk(os.path.join(tmp, "docs")):
            for n in names:
                built = os.path.join(dirpath, n)
                rel = os.path.relpath(built, tmp)
                if rel == os.path.join("docs", "go", "index.html"):
                    continue
                committed = os.path.join(ROOT, rel)
                if not os.path.exists(committed):
                    missing.append(rel)
                elif not filecmp.cmp(built, committed, shallow=False):
                    differ.append(rel)
        if differ or missing:
            err("site-sync", "run python3 tools/make_site.py and commit docs/: "
                + ", ".join((differ + [m + " (not committed)" for m in missing])[:8]))
        else:
            ok("site-sync")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_drafts():
    spec_f = os.path.join(ROOT, "site", "pages.json")
    if not os.path.exists(spec_f):
        return ok("drafts", "no pages")
    spec = importlib.util.spec_from_file_location("make_site", os.path.join(ROOT, "tools", "make_site.py"))
    ms = importlib.util.module_from_spec(spec); spec.loader.exec_module(ms)
    pages = json.load(open(spec_f, encoding="utf-8"))["pages"]
    sitemap = open(os.path.join(ROOT, "docs", "sitemap.xml"), encoding="utf-8").read()
    index = open(os.path.join(ROOT, "docs", "index.html"), encoding="utf-8").read()
    hub_f = os.path.join(ROOT, "docs", "go", "index.html")
    hub = open(hub_f, encoding="utf-8").read() if os.path.exists(hub_f) else ""
    bad = []
    for p in pages:
        slug = p["slug"]
        f = os.path.join(ROOT, "docs", slug, "index.html")
        if not os.path.exists(f):
            bad.append(f"{slug}: page not built"); continue
        noindex = 'name="robots" content="noindex' in open(f, encoding="utf-8").read()
        listed = f"/{slug}/" in sitemap
        if ms.is_live(p):
            if noindex or not listed:
                bad.append(f"{slug}: live but {'noindex' if noindex else 'missing from sitemap'}")
        else:
            if not noindex:
                bad.append(f"{slug}: not live but indexable")
            if listed or f'href="{slug}/"' in index or f'../{slug}/"' in hub:
                bad.append(f"{slug}: not live but listed in the sitemap, index or hub")
    err("drafts", "; ".join(bad[:8])) if bad else ok("drafts", f"{len(pages)} pages")


def check_em_dash(files):
    roots = ("docs/", "site/", "email/", "promo/specs/", "agents/", "services/")
    hits = []
    for f in files:
        if f.startswith(roots) and not BINARY.search(f):
            try:
                if EM in open(os.path.join(ROOT, f), encoding="utf-8", errors="ignore").read():
                    hits.append(f)
            except OSError:
                pass
    err("em-dash", ", ".join(hits[:10])) if hits else ok("em-dash")


def check_secrets(files):
    hits = []
    for f in files:
        if BINARY.search(f):
            continue
        p = os.path.join(ROOT, f)
        try:
            if os.path.getsize(p) > 5_000_000:
                continue
            text = open(p, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        m = SECRET.search(text)
        if m:  # name the kind and line only; never print any character of the value
            hits.append(f"{f} line {text.count(chr(10), 0, m.start()) + 1} ({m.lastgroup})")
    err("secrets", ", ".join(hits[:10])) if hits else ok("secrets")


def check_permit_data():
    bad = []
    for f in glob.glob(os.path.join(ROOT, "permits", "*", "sample.json")):
        d = json.load(open(f, encoding="utf-8"))
        for p in d.get("projects", []) + d.get("nearFinish", []):
            keys = [k for k in p if PERSONAL_KEYS.search(k)]
            if keys:
                bad.append(f"{os.path.relpath(f, ROOT)}: {keys}"); break
            if PERSON_TAG.search(p.get("scope", "")):   # a tag that can carry a person's name (Legal desk, Oct 15)
                bad.append(f"{os.path.relpath(f, ROOT)}: permit {p.get('permit')} scope has a reviewer, consultant or owner tag"); break
    # Move 2 (Oct 23): listed phones go only into sealed members' files (tools/phones.py), never a public data file
    for f in glob.glob(os.path.join(ROOT, "permits", "**", "*.json"), recursive=True):
        if f.endswith(".sealed.json"):
            continue
        t = open(f, encoding="utf-8").read()
        if re.search(r'"phone"\s*:\s*"[^"]', t) or re.search(r"\(\d{3}\) \d{3}-\d{4}", t):
            bad.append(f"{os.path.relpath(f, ROOT)}: a phone number in a public data file")
    err("permit-data", "; ".join(bad)) if bad else ok("permit-data")


def check_builder_contacts(files):
    """Legal desk round 2, Fix 1: this repo is public, so the contacts live only in builder_contacts.enc.json. A plain
    builder_contacts.json in the repo is an error. With LEADS_PASSWORD set (CI passes the secret) the entries are
    decrypted in memory and checked against tools/builder_contacts.py's rules; without it only the box's shape is."""
    rel = "permits/chicago/"
    if rel + "builder_contacts.json" in files:
        return err("builder-contacts", "a plain permits/chicago/builder_contacts.json is in the repo; this repo is public, so the contacts "
                   "live only in builder_contacts.enc.json (tools/builder_contacts.py --encrypt-from), never in the clear")
    spec = importlib.util.spec_from_file_location("builder_contacts", os.path.join(ROOT, "tools", "builder_contacts.py"))
    bc = importlib.util.module_from_spec(spec); spec.loader.exec_module(bc)
    bad = bc.do_not_list_problems(os.path.join(ROOT, "permits", "chicago", "builder_do_not_list.json"))
    f = os.path.join(ROOT, "permits", "chicago", "builder_contacts.enc.json")
    if not os.path.exists(f):
        return err("builder-contacts", "; ".join(bad)) if bad else ok("builder-contacts", "no file")
    try:
        box = json.load(open(f, encoding="utf-8"))
    except ValueError:
        return err("builder-contacts", "builder_contacts.enc.json does not parse")
    bad += bc.box_problems(box)
    if bad:
        return err("builder-contacts", "; ".join(bad[:6]))
    pw = os.environ.get("LEADS_PASSWORD", "")
    if len(pw) < 12:
        return ok("builder-contacts", "encrypted box checked; entries not checked without LEADS_PASSWORD")
    try:
        data = bc.load(f, pw)
    except ImportError as e:
        return ok("builder-contacts", f"encrypted box checked; entries not decrypted here ({e.name} is not installed)")
    except Exception as e:
        return err("builder-contacts", f"builder_contacts.enc.json did not decrypt with LEADS_PASSWORD ({type(e).__name__})")
    found = bc.problems(data, bc.do_not_list(os.path.join(ROOT, "permits", "chicago", "builder_do_not_list.json")))
    if found:
        return err("builder-contacts", "; ".join(found[:6]))
    old = bc.stale(data)
    ok("builder-contacts", f"{len(data)} entries" + (f"; {len(old)} checked more than {bc.STALE_DAYS} days ago, run "
                                                     "tools/builder_contacts.py --check" if old else ""))


def check_video_specs(files):
    specs = [f for f in files if f.startswith("promo/specs/") and f.endswith(".json")]
    spec = importlib.util.spec_from_file_location("spec_lint", os.path.join(ROOT, "tools", "spec_lint.py"))
    sl = importlib.util.module_from_spec(spec); spec.loader.exec_module(sl)
    bad = []
    for f in specs:
        try:
            found = sl.problems(json.load(open(os.path.join(ROOT, f), encoding="utf-8")), f)
        except Exception as e:
            found = [f"does not parse ({str(e)[:60]})"]
        bad += [f"{f}: {p}" for p in found[:2]]
    err("video-specs", "; ".join(bad[:6])) if bad else ok("video-specs", f"{len(specs)} specs")


def check_voice(files):
    spec = importlib.util.spec_from_file_location("voice_lint", os.path.join(ROOT, "tools", "voice_lint.py"))
    vl = importlib.util.module_from_spec(spec); spec.loader.exec_module(vl)
    bad = []
    pages_f = os.path.join(ROOT, "site", "pages.json")
    if os.path.exists(pages_f):
        for p in json.load(open(pages_f, encoding="utf-8")).get("pages", []):
            bad += [f"site page {p.get('slug')}: {n} ({w.strip()!r})" for n, w in vl.tells(json.dumps(p, ensure_ascii=False))]
    for f in files:
        if f.startswith("email/") and f.endswith((".md", ".txt", ".html")):
            bad += [f"{f}: {n} ({w.strip()!r})" for n, w in vl.tells(open(os.path.join(ROOT, f), encoding="utf-8", errors="ignore").read())]
    err("voice", "; ".join(bad[:8])) if bad else ok("voice")


def check_fiverr_kit():
    kit = os.path.join(ROOT, "services", "fiverr")
    if not os.path.isdir(kit):
        return ok("fiverr-kit", "no kit")
    spec = importlib.util.spec_from_file_location("fiverr_kit", os.path.join(ROOT, "tools", "fiverr_kit.py"))
    fk = importlib.util.module_from_spec(spec); spec.loader.exec_module(fk)
    found = fk.problems(kit)
    err("fiverr-kit", "; ".join(found[:8])) if found else ok("fiverr-kit")


def check_gate_tests():
    test = os.path.join(ROOT, "tools", "test_check_repo.py")
    if not os.path.exists(test):
        return err("gate-tests", "tools/test_check_repo.py is missing, so nothing proves the checks above still catch anything")
    r = subprocess.run([sys.executable, test], cwd=ROOT, capture_output=True, text=True, timeout=900)
    lines = (r.stdout + r.stderr).strip().splitlines()
    if r.returncode != 0:
        fails = [l[5:] for l in lines if l.startswith("FAIL ")] or lines[-1:]
        err("gate-tests", "the gate itself is broken (" + "; ".join(fails[:6]) + "); never edit tools/check_repo.py or "
            "tools/test_check_repo.py to clear this, tell Todd")
    else:
        ok("gate-tests", (lines[-1].split(": ", 1)[-1] if lines else "passed"))


def check_sender():
    tests = [os.path.join(ROOT, "email", "sender", t) for t in ("test.js", "test_glue.js")]
    tests = [t for t in tests if os.path.exists(t)]
    if not tests:
        return ok("sender-tests", "no test file")
    if not shutil.which("node"):
        return err("sender-tests", "node is not installed here")
    out = []
    for t in tests:
        r = subprocess.run(["node", t], cwd=ROOT, capture_output=True, text=True)
        last = (r.stdout.strip().splitlines() or ["no output"])[-1]
        if r.returncode != 0 or not last.startswith("PASS"):
            return err("sender-tests", f"{os.path.basename(t)}: {last} {r.stderr.strip()[:120]}")
        out.append(last.replace("PASS ", ""))
    ok("sender-tests", "; ".join(out))


def _run_tool(args, timeout=300):
    r = subprocess.run([sys.executable] + args, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    lines = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]
    return r.returncode, lines


def check_context(skill=None):
    code, lines = _run_tool([os.path.join("tools", "context_gate.py")] + (["--skill", skill] if skill else []))
    if code:
        err("context", "; ".join(l.replace("ERROR context: ", "") for l in lines if l.startswith("ERROR"))[:600] or "exit 1")
    else:
        ok("context", lines[-1].replace("OK context: ", "") if lines else "")


def check_moat():
    path = os.path.join(ROOT, "permits", "downstream", "gc_leads.json")
    if not os.path.exists(path):
        return ok("moat", "no permits/downstream/gc_leads.json yet (the downstream-leads workflow writes it)")
    code, lines = _run_tool([os.path.join("tools", "validate_leads.py"), "gc", path])
    if code:
        err("moat", "; ".join(l.replace("ERROR gc: ", "") for l in lines if l.startswith("ERROR"))[:600] or "exit 1")
    else:
        ok("moat", lines[-1].replace("OK gc: ", "") if lines else "")


def check_schema(files):
    leaked = [f for f in files if f.startswith("data/")]
    for f in files:
        if f.endswith(".json") and not f.startswith("data/"):
            try:
                with open(os.path.join(ROOT, f), encoding="utf-8") as fh:
                    head = fh.read(400)
            except (OSError, UnicodeDecodeError):
                continue
            if '"pnf.prospect.v1"' in head:
                leaked.append(f)
    if leaked:
        return err("schema", "prospect data (named people) is tracked in this public repo: " + ", ".join(leaked[:5]))
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import enrich_ci
    bpath = os.path.join(ROOT, "prospects", "businesses.json")
    if os.path.exists(bpath):
        probs = enrich_ci.validate_businesses(json.load(open(bpath, encoding="utf-8")))
        if probs:
            return err("schema", "prospects/businesses.json: " + "; ".join(probs[:4]))
    spath = os.path.join(ROOT, "prospects", "enrich_state.json")
    if os.path.exists(spath):
        st = json.load(open(spath, encoding="utf-8"))
        allowed = {"checkedAt", "result", "rung", "hunterAt"}
        if st.get("schema") != "pnf.enrich_state.v1" or "@" in json.dumps(st) or any(
                set(v) - allowed for v in (st.get("domains") or {}).values()):
            return err("schema", "prospects/enrich_state.json must be pnf.enrich_state.v1 with business-level fields only")
    box = os.path.join(ROOT, "prospects", "enriched.sealed.json")
    if os.path.exists(box):
        b = json.load(open(box, encoding="utf-8"))
        if set(b) != {"v", "alg", "salt", "nonce", "ct"}:
            return err("schema", "prospects/enriched.sealed.json is not a sealed box (tools/data_box.py); named people must never be committed in the clear")
    local = os.path.join(ROOT, "data", "prospects", "prospects.json")
    if not os.path.exists(local):
        return ok("schema", "no prospect data tracked; no local prospect file in this checkout")
    code, lines = _run_tool([os.path.join("tools", "validate_leads.py"), "prospects", local])
    if code:
        err("schema", "; ".join(l.replace("ERROR prospects: ", "") for l in lines if l.startswith("ERROR"))[:600] or "exit 1")
    else:
        ok("schema", lines[-1].replace("OK prospects: ", "") if lines else "")


def check_copy():
    code, lines = _run_tool([os.path.join("tools", "copy_gate.py"), "--templates"])
    if code:
        return err("copy", "; ".join(l.replace("ERROR copy: ", "") for l in lines if l.startswith("ERROR"))[:600] or "exit 1")
    detail = lines[-1].replace("OK copy: ", "") if lines else ""
    if os.path.exists(os.path.join(ROOT, "permits", "downstream", "gc_leads.json")):
        code, lines = _run_tool([os.path.join("tools", "copy_gate.py"), "--live"])
        if code:
            return err("copy", "; ".join(l.replace("ERROR copy: ", "") for l in lines if l.startswith("ERROR"))[:600] or "exit 1")
        detail += "; " + (lines[-1].replace("OK copy: ", "") if lines else "")
    # Signal leads (Todd, Oct 22, 2026, decision 2): license and citation templates, the live license sample, and local
    # signal drafts, checked the same way as the permit ones
    code, lines = _run_tool([os.path.join("tools", "copy_gate.py"), "--signal-templates"])
    if code:
        return err("copy", "; ".join(l.replace("ERROR copy: ", "") for l in lines if l.startswith("ERROR"))[:600] or "exit 1")
    detail += "; " + (lines[-1].replace("OK copy: ", "") if lines else "")
    if os.path.exists(os.path.join(ROOT, "permits", "licenses-chicago", "sample.json")):
        code, lines = _run_tool([os.path.join("tools", "copy_gate.py"), "--signal-live"])
        if code:
            return err("copy", "; ".join(l.replace("ERROR copy: ", "") for l in lines if l.startswith("ERROR"))[:600] or "exit 1")
        detail += "; " + (lines[-1].replace("OK copy: ", "") if lines else "")
    # Pest seat email (Todd, Oct 24, 2026): {n} is the 7-day restaurant count, never the daily file's total
    code, lines = _run_tool([os.path.join("tools", "copy_gate.py"), "--pest-templates"])
    if code:
        return err("copy", "; ".join(l.replace("ERROR copy: ", "") for l in lines if l.startswith("ERROR"))[:600] or "exit 1")
    detail += "; " + (lines[-1].replace("OK copy: ", "") if lines else "")
    # Area seat email for construction cleaning (Todd, Oct 26, 2026): the lead is in the seat it names, the seat is open,
    # {open} is this week's count for that seat
    code, lines = _run_tool([os.path.join("tools", "copy_gate.py"), "--seat-templates"])
    if code:
        return err("copy", "; ".join(l.replace("ERROR copy: ", "") for l in lines if l.startswith("ERROR"))[:600] or "exit 1")
    detail += "; " + (lines[-1].replace("OK copy: ", "") if lines else "")
    # License count email to commission sellers (Todd, Oct 24, 2026): the City's weekly counts, no business named, sales@ only
    if os.path.exists(os.path.join(ROOT, "permits", "inspections-chicago", "sample.json")):
        code, lines = _run_tool([os.path.join("tools", "copy_gate.py"), "--lic-templates"])
        if code:
            return err("copy", "; ".join(l.replace("ERROR copy: ", "") for l in lines if l.startswith("ERROR"))[:600] or "exit 1")
        detail += "; " + (lines[-1].replace("OK copy: ", "") if lines else "")
    ldrafts = os.path.join(ROOT, "data", "work", "lic_drafts.json")
    if os.path.exists(ldrafts):
        code, lines = _run_tool([os.path.join("tools", "copy_gate.py"), "--lic", ldrafts])
        if code:
            return err("copy", "; ".join(l.replace("ERROR copy: ", "") for l in lines if l.startswith("ERROR"))[:600] or "exit 1")
        detail += "; " + (lines[-1].replace("OK copy: ", "") if lines else "")
    pdrafts = os.path.join(ROOT, "data", "work", "pest_drafts.json")
    if os.path.exists(pdrafts):
        code, lines = _run_tool([os.path.join("tools", "copy_gate.py"), "--pest", pdrafts])
        if code:
            return err("copy", "; ".join(l.replace("ERROR copy: ", "") for l in lines if l.startswith("ERROR"))[:600] or "exit 1")
        detail += "; " + (lines[-1].replace("OK copy: ", "") if lines else "")
    sdrafts = os.path.join(ROOT, "data", "work", "signal_drafts.json")
    if os.path.exists(sdrafts):
        code, lines = _run_tool([os.path.join("tools", "copy_gate.py"), "--signal", sdrafts])
        if code:
            return err("copy", "; ".join(l.replace("ERROR copy: ", "") for l in lines if l.startswith("ERROR"))[:600] or "exit 1")
        detail += "; " + (lines[-1].replace("OK copy: ", "") if lines else "")
    drafts = os.path.join(ROOT, "data", "work", "drafts.json")
    if os.path.exists(drafts):
        code, lines = _run_tool([os.path.join("tools", "copy_gate.py"), drafts])
        if code:
            return err("copy", "; ".join(l.replace("ERROR copy: ", "") for l in lines if l.startswith("ERROR"))[:600] or "exit 1")
        detail += "; " + (lines[-1].replace("OK copy: ", "") if lines else "")
    ok("copy", detail)


def check_monday():
    code, lines = _run_tool([os.path.join("tools", "monday_email.py"), "--check"])
    last = next((l for l in reversed(lines) if l.startswith(("OK monday", "ERROR monday"))), "")
    if code or not last.startswith("OK"):
        err("monday", (last.split(": ", 1)[-1] if last else "monday_email.py --check failed")[:600])
    else:
        ok("monday", last[len("OK monday "):].strip("()"))


def check_radar():
    code, lines = _run_tool([os.path.join("tools", "product_wire.py")])
    if code:
        return err("radar", "; ".join(l for l in lines if l.startswith("ERROR"))[:600] or "product_wire exit 1")
    warns = sum(1 for l in lines if l.startswith("WARN"))
    code, olines = _run_tool([os.path.join("tools", "opportunity_score.py"), "--check"])
    if code:
        return err("radar", "; ".join(l for l in olines if l.startswith("ERROR"))[:600] or "opportunity_score --check exit 1")
    for tool in ("opportunity_score.py", "product_wire.py", "product_health.py", "ai_visibility.py", "kimi_intake.py"):
        code, tl = _run_tool([os.path.join("tools", tool), "--selftest"])
        if code:
            return err("radar", f"{tool} --selftest: " + "; ".join(l for l in tl if l.startswith(("FAIL", "ERROR")))[:500])
    ok("radar", f"{sum(1 for l in lines if l.startswith('OK wire') or (l.startswith('WARN wire') and ' pieces wired' in l))} products wired"
       f" ({warns} legacy gaps as WARN); {olines[-1].split(': ', 1)[-1] if olines else ''}; 5 selftests pass")


def check_cos():
    code, lines = _run_tool([os.path.join("tools", "cos_agenda.py"), "--selftest"])
    last = next((l for l in reversed(lines) if "cos selftest" in l), "")
    if code:
        err("cos", ("; ".join(l[5:] for l in lines if l.startswith("FAIL ")) or last or "cos_agenda.py --selftest failed")[:500])
    else:
        ok("cos", last.split(": ", 1)[-1])


def check_gate_selftest():
    code, lines = _run_tool([os.path.join("tools", "test_gates.py")])
    if code:
        err("gate-selftest", "a pipeline gate stopped catching a planted failure (" + "; ".join(l[5:] for l in lines if l.startswith("FAIL "))[:500]
            + "); never edit the gates or tools/test_gates.py to clear this, tell Todd")
    else:
        ok("gate-selftest", lines[-1].split(": ", 1)[-1] if lines else "passed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--preflight", metavar="JOB", default=None)
    args = ap.parse_args()
    only = {x.strip() for x in args.only.split(",") if x.strip()}
    if args.preflight:
        only = {"context", "moat", "schema", "copy", "gate-selftest"} | ({"cos"} if args.preflight == "chief-of-staff" else set())
    files = tracked()
    checks = [("json", lambda: check_json(files)), ("python", lambda: check_python(files)), ("calc-tests", check_calc), ("sender-tests", check_sender),
              ("site-sync", lambda: check_site_sync(files)), ("drafts", check_drafts), ("em-dash", lambda: check_em_dash(files)),
              ("secrets", lambda: check_secrets(files)), ("permit-data", check_permit_data), ("builder-contacts", lambda: check_builder_contacts(files)), ("video-specs", lambda: check_video_specs(files)),
              ("voice", lambda: check_voice(files)),
              ("fiverr-kit", check_fiverr_kit),
              ("context", lambda: check_context(args.preflight)), ("moat", check_moat), ("schema", lambda: check_schema(files)),
              ("copy", check_copy), ("monday", check_monday), ("radar", check_radar), ("cos", check_cos), ("gate-selftest", check_gate_selftest),
              ("gate-tests", check_gate_tests)]
    for name, fn in checks:
        if only and name not in only:
            continue
        try:
            fn()
        except Exception as e:  # a check that crashes is a failed check, never a silent pass
            err(name, f"check crashed: {type(e).__name__}: {str(e)[:120]}")
    for status, name, detail in results:
        print(f"{status} {name}" + (f": {detail}" if status == "ERROR" else (f" ({detail})" if detail else "")))
    n = sum(1 for r in results if r[0] == "ERROR")
    partial = (f" (preflight for {args.preflight}: the four pipeline gates and their planted tests)" if args.preflight else
               f" (partial run: only {', '.join(sorted(only))}; run the full check before pushing)" if only else "")
    print(f"check_repo: {n} error{'s' if n != 1 else ''}{partial}")
    sys.exit(1 if n else 0)


if __name__ == "__main__":
    main()
