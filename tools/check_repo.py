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
  em-dash       no em dash in anything public: docs/, site/, email/, promo/specs/, agents/
  secrets       no token or private key pattern in any tracked text file
  permit-data   permits/*/sample.json holds business-level fields only, and no scope text carries a
                reviewer, consultant, architect, engineer or owner tag (where a person's name can follow)
  gate-tests    tools/test_check_repo.py plants a failure for every check above in a throwaway copy and
                confirms each one is caught and no secret value is printed (Todd's Oct 15 note: the checks get
                tested too). An ERROR here means the gate itself is broken: tell Todd, never edit the gate to clear it

Usage: python3 tools/check_repo.py [--only name,name]
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
    roots = ("docs/", "site/", "email/", "promo/specs/", "agents/")
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
    err("permit-data", "; ".join(bad)) if bad else ok("permit-data")


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    only = {x.strip() for x in ap.parse_args().only.split(",") if x.strip()}
    files = tracked()
    checks = [("json", lambda: check_json(files)), ("python", lambda: check_python(files)), ("calc-tests", check_calc),
              ("site-sync", lambda: check_site_sync(files)), ("drafts", check_drafts), ("em-dash", lambda: check_em_dash(files)),
              ("secrets", lambda: check_secrets(files)), ("permit-data", check_permit_data), ("gate-tests", check_gate_tests)]
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
    partial = f" (partial run: only {', '.join(sorted(only))}; run the full check before pushing)" if only else ""
    print(f"check_repo: {n} error{'s' if n != 1 else ''}{partial}")
    sys.exit(1 if n else 0)


if __name__ == "__main__":
    main()
