#!/usr/bin/env python3
"""Leak scan around the plain gitleaks binary (Todd's go, Oct 24, 2026, coo/DECISIONS-2026-10-24.md item 2).
Rules live in .gitleaks.toml. Every line printed is "OK <name>", "WARN <name>: ..." or "ERROR <name>: ..."; a finding
is named by rule, file, line and commit only, never by any character of the value (gitleaks runs with --redact too).

  python3 tools/leak_scan.py push --before SHA --after SHA   scan the commits in one push (.github/workflows/leak-scan.yml)
  python3 tools/leak_scan.py history                          scan every commit reachable from HEAD (leak-scan-history.yml)
  python3 tools/leak_scan.py sealed                           every tracked *.sealed.json and *.enc.json is a well-formed box
  python3 tools/leak_scan.py selftest                         planted leaks for every rule are caught, our own addresses and
                                                              the allowlist entries pass, the push range is honoured, and
                                                              no planted value reaches stdout or the report
Needs gitleaks on PATH (or GITLEAKS=/path/to/gitleaks) for push, history and selftest. Exit 1 on any ERROR.
"""
import argparse, collections, json, os, random, shutil, string, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, ".gitleaks.toml")
ZERO = "0" * 40
BOX_KEYS = {"v", "alg", "kdf", "rounds", "salt", "iv", "nonce", "key", "gzip", "ct"}
OURS = ["rules", "pnf-email", "pnf-phone", "pnf-hunter-key", "pnf-gumroad-token", "pnf-kit-key", "pnf-kit-v4-key",
        "pnf-bouncer-key"]


def gitleaks_bin():
    b = os.environ.get("GITLEAKS") or shutil.which("gitleaks")
    if not b:
        print("ERROR leak-scan: gitleaks binary not found (PATH or GITLEAKS)")
        sys.exit(1)
    return b


def run_gitleaks(repo, log_opts=None, config=CONFIG):
    """Run gitleaks in git mode with --redact; return its findings (list of dicts) and its combined output."""
    fd, rep = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    cmd = [gitleaks_bin(), "git", repo, "-c", config, "--redact", "--no-banner", "--exit-code", "0",
           "--report-format", "json", "--report-path", rep]
    if log_opts:
        cmd += ["--log-opts", log_opts]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = p.stdout + p.stderr
    try:
        findings = json.load(open(rep)) or []
    except (OSError, ValueError):
        findings = None
    os.unlink(rep)
    if p.returncode != 0 or findings is None:
        tail = " | ".join(l for l in out.splitlines() if "ERR" in l or "error" in l.lower())[-400:]
        print(f"ERROR leak-scan: gitleaks did not finish (exit {p.returncode}) {tail}")
        sys.exit(1)
    return findings, out


def report(name, findings):
    """Counts by rule and by file, then one line per finding: rule, file:line, short commit. No values."""
    if not findings:
        print(f"OK {name} (0 findings)")
        return 0
    by_rule = collections.Counter(f["RuleID"] for f in findings)
    by_file = collections.Counter(f["File"] for f in findings)
    print(f"ERROR {name}: {len(findings)} findings; by rule: " + ", ".join(f"{r} {n}" for r, n in by_rule.most_common()))
    print(f"ERROR {name}: by file: " + ", ".join(f"{p} {n}" for p, n in by_file.most_common(25))
          + (f" (+{len(by_file) - 25} more files)" if len(by_file) > 25 else ""))
    for f in findings[:200]:
        print(f"  {f['RuleID']} {f['File']}:{f['StartLine']} commit {f.get('Commit', '')[:7]}")
    if len(findings) > 200:
        print(f"  ... {len(findings) - 200} more")
    return 1


def cmd_push(before, after):
    after = after or "HEAD"
    if not before or before == ZERO:   # new branch or a manual run: the pushed commit itself
        opts = f"-1 {after}"
    else:
        opts = f"{before}..{after}"
    findings, _ = run_gitleaks(ROOT, opts)
    return report("leak-scan-push", findings)


def cmd_history():
    n = subprocess.run(["git", "-C", ROOT, "rev-list", "--count", "HEAD"], capture_output=True, text=True).stdout.strip()
    shallow = subprocess.run(["git", "-C", ROOT, "rev-parse", "--is-shallow-repository"], capture_output=True, text=True).stdout.strip()
    if shallow == "true":
        print("ERROR leak-scan-history: the checkout is shallow; fetch the whole history first (fetch-depth: 0)")
        return 1
    findings, _ = run_gitleaks(ROOT)
    print(f"OK leak-scan-history scanned {n} commits")
    return report("leak-scan-history", findings)


def box_problem(path):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return "not JSON"
    if not isinstance(d, dict) or not isinstance(d.get("v"), int) or not isinstance(d.get("ct"), str) or len(d["ct"]) < 24:
        return "no version and ciphertext"
    extra = set(d) - BOX_KEYS
    if extra:
        return f"keys a box never has: {sorted(extra)[:5]}"
    if not ({"iv", "nonce"} & set(d)):
        return "no iv or nonce"
    for k, v in d.items():
        if k != "ct" and isinstance(v, str) and len(v) > 1024:
            return f"field {k} too long for a box header"
    import base64, binascii
    try:
        base64.b64decode(d["ct"], validate=True)
    except (binascii.Error, ValueError):
        return "ciphertext is not base64"
    return ""


def cmd_sealed(root=ROOT):
    files = subprocess.run(["git", "-C", root, "ls-files", "*.sealed.json", "*.enc.json", "**/*.sealed.json", "**/*.enc.json"],
                           capture_output=True, text=True).stdout.split()
    files = sorted(set(files))
    bad = [f"{f} ({p})" for f in files if (p := box_problem(os.path.join(root, f)))]
    if bad:
        print("ERROR leak-scan-sealed: allowlisted names that are not sealed boxes: " + "; ".join(bad))
        return 1
    print(f"OK leak-scan-sealed ({len(files)} sealed files are well-formed boxes)")
    return 0


# ---------------------------------------------------------------- planted tests
def _rand(n, alphabet):
    r = random.SystemRandom()
    return "".join(r.choice(alphabet) for _ in range(n))


def _git(repo, *a):
    subprocess.run(["git", "-C", repo, *a], check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "selftest", "GIT_AUTHOR_EMAIL": "selftest@example.com",
                        "GIT_COMMITTER_NAME": "selftest", "GIT_COMMITTER_EMAIL": "selftest@example.com"})


def _repo(base, files):
    repo = tempfile.mkdtemp(dir=base)
    _git(repo, "init", "-q")
    shutil.copy(CONFIG, os.path.join(repo, ".gitleaks.toml"))
    for path, text in files.items():
        full = os.path.join(repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w", encoding="utf-8").write(text)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "planted")
    return repo


def cmd_selftest():
    hexs, b64u, alnum = "0123456789abcdef", string.ascii_letters + string.digits + "_-", string.ascii_letters + string.digits
    # Every planted value is made at run time so this file never holds one (it would trip the scan of this repo).
    dom = "mailbox" + _rand(6, string.ascii_lowercase) + ".com"
    hunter, gumroad, kitsec, kit4, bouncer, bouncer2 = (_rand(40, hexs), _rand(43, b64u), _rand(43, alnum),
                                                       "kit_" + _rand(32, alnum), _rand(40, alnum), _rand(36, alnum))
    generic, beacon = "Zq" + _rand(30, alnum) + "9x", _rand(32, hexs)
    at, dash = "@", "-"
    ph1, ph2, ph3 = f"(773) 482{dash}7719", f"312.640.{'2283'}", f"+1 312{dash}640{dash}2284"
    catch = {   # path -> (text, rule ids that must be found in that file)
        "notes/a.md": (f"Owner reply from jane.planted{at}{dom} today.\n", {"pnf-email"}),
        "notes/b.md": (f"Call {ph1} or {ph2} or {ph3}.\n", {"pnf-phone"}),
        "tools/c.py": (f'HUNTER_API_KEY = "{hunter}"\nurl = "https://api.hunter.io/v2/domain-search?domain=a.org&api_key={hunter}"\n',
                       {"pnf-hunter-key"}),
        "ops/d.env": (f"GUMROAD_ACCESS_TOKEN={gumroad}\n", {"pnf-gumroad-token"}),
        "email/e.json": (f'{{"kit_api_secret": "{kitsec}", "key": "{kit4}"}}\n', {"pnf-kit-key", "pnf-kit-v4-key"}),
        "tools/f.sh": (f'BOUNCER_API_KEY="{bouncer}"\ncurl -H "x-api-key: {bouncer2}" https://api.usebouncer.com/v1.1/email/verify\n',
                       {"pnf-bouncer-key"}),
        # gitleaks' own generic rule still fires on a token that is not the analytics beacon
        "site/g.json": (f'{{"api_token": "{generic}"}}\n', {"generic-api-key"}),
        # the sender fixtures' path allowlist covers emails only: a key in the same file is still caught
        "email/sender/test.js": (f"const HUNTER_KEY = '{hunter}';\n", {"pnf-hunter-key"}),
    }
    passing = {   # must give 0 findings
        "docs/ours.md": ("Write to hello@proofnotfluff.com or sales@getproofnotfluff.com, data@getproofnotfluff.com.\n"
                         "Tests: proofnotfluff+monday-chicago@gmail.com, outlandiastays@gmail.com, you@example.com, x@other.example.\n"
                         "Bot: 41898282+github-actions[bot]@users.noreply.github.com and noreply@anthropic.com.\n"
                         "Fiction: (312) 555-0100, 773-555-0199. Poison Control 1-800-222-1222. Permit 100912345, ZIP 60611.\n"
                         "Commit a4606687d5fb3e787df937e334c97743cee8c5fe on main. Price $2.99, 3 seats.\n"),
        "tools/env.py": ('HUNTER_API_KEY = os.environ["HUNTER_API_KEY"]\nkit_api_key = os.environ.get("KIT_API_KEY", "")\n'
                         'GUMROAD_URL = "https://proofnotfluff.gumroad.com/l/bzemcy"\nbouncer_status = "deliverable"\n'),
        ".github/workflows/w.yml": ("env:\n  BOUNCER_API_KEY: ${{ secrets.BOUNCER_API_KEY }}\n  KIT_API_SECRET: ${{ secrets.KIT_API_SECRET }}\n"),
        "email/sender/test.js": (f"send('a{at}x.com'); send('z{at}bad.com'); send('lead{at}co90.com');\n"),
        "prospects/enriched.sealed.json": ('{"v": 1, "alg": "x", "salt": "AAAA", "nonce": "AAAA", "ct": "'
                                           + f"owner{at}{dom} {ph1}" + '"}\n'),
        "docs/form/index.html": ('<input type="email" placeholder="you@company.com">\n'
                                 'const PKEY="pnf-pest-seat-pw",SKEY="pnf-pest-seat-marks-v2";\n'),
        "tools/site.py": ('INDEXNOW_KEY = "cdccc9befa99e9cfa2a85549b2b1160d"\n'),
        "docs/q/index.html": ('<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
                              f'data-cf-beacon=\'{{"token": "{beacon}"}}\'></script>\n'),
        "kdp/book.pdf": (f"%PDF-1.4 call {ph1} jane{at}{dom}\n"),
    }
    planted_values = [f"jane.planted{at}{dom}", ph1, ph2, ph3, hunter, gumroad, kitsec, kit4, bouncer, bouncer2, generic]
    fails, n = [], 0
    base = tempfile.mkdtemp(prefix="leakscan-")
    try:
        repo = _repo(base, {p: t for p, (t, _) in catch.items()})
        found, out = run_gitleaks(repo)
        got = collections.defaultdict(set)
        for f in found:
            got[f["File"]].add(f["RuleID"])
        for path, (_, want) in catch.items():
            n += 1
            if not want <= got.get(path, set()):
                fails.append(f"{path}: wanted {sorted(want)}, got {sorted(got.get(path, set()))}")
        n += 1
        blob = json.dumps(found) + out
        leaked = [v for v in planted_values if v in blob]
        if leaked:
            fails.append(f"{len(leaked)} planted values reached the report or output (redaction broken)")

        repo2 = _repo(base, passing)
        found2, _ = run_gitleaks(repo2)
        n += 1
        if found2:
            fails.append("allowlisted cases flagged: " + ", ".join(f"{f['RuleID']} {f['File']}" for f in found2[:10]))

        # push range: a leak in commit 1, a clean commit 2; the range 1..2 must not see the leak, the root range must
        repo3 = _repo(base, {"a.md": f"jane.planted{at}{dom}\n"})
        first = subprocess.run(["git", "-C", repo3, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        open(os.path.join(repo3, "b.md"), "w").write("clean\n")
        _git(repo3, "add", "-A")
        _git(repo3, "commit", "-q", "-m", "clean")
        n += 2
        if run_gitleaks(repo3, f"{first}..HEAD")[0]:
            fails.append("push range scanned a commit outside the range")
        if len(run_gitleaks(repo3)[0]) != 1:
            fails.append("full history scan missed the leak in the first commit")

        # sealed check: a plain file wearing a sealed name is refused, a real box shape passes
        repo4 = _repo(base, {"p/plain.sealed.json": '{"owner": "x", "email": "y"}\n',
                             "p/box.sealed.json": '{"v": 1, "alg": "a", "salt": "AAAA", "nonce": "AAAA", "ct": "QUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFB"}\n'})
        n += 1
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = cmd_sealed(repo4)
        if rc != 1 or "plain.sealed.json" not in buf.getvalue() or "box.sealed.json (" in buf.getvalue():
            fails.append("sealed check did not refuse the plain file alone")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    if fails:
        print("ERROR leak-scan-selftest: " + "; ".join(fails))
        return 1
    rules = sum(len(w) for _, w in catch.values())
    print(f"OK leak-scan-selftest ({n} planted checks: {rules} rule hits caught across {len(catch)} files, "
          f"{len(passing)} allowlisted files clean, push range honoured, sealed impostor refused, no value printed)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["push", "history", "sealed", "selftest"])
    ap.add_argument("--before", default="")
    ap.add_argument("--after", default="")
    a = ap.parse_args()
    rc = {"push": lambda: cmd_push(a.before, a.after), "history": cmd_history, "sealed": cmd_sealed,
          "selftest": cmd_selftest}[a.cmd]()
    sys.exit(rc)


if __name__ == "__main__":
    main()
