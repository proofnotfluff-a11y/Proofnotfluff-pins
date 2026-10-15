#!/usr/bin/env python3
"""Tests for the code gate (tools/check_repo.py). Rule (Todd's Oct 15 note on agentic engineering): a model can
write the checks, so the checks get tested too. Each check must catch a failure planted in a throwaway copy of the
repo, and the secrets check must never print any part of a planted value. Nothing in the real tree changes.

Usage: python3 tools/test_check_repo.py      exit 1 if any planted failure slips through
check_repo.py runs this file as its gate-tests check, so the nightly optimizer and every push see a broken gate.
"""
import json, os, random, shutil, string, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKS = ["json", "python", "calc-tests", "site-sync", "drafts", "em-dash", "secrets", "permit-data"]
rng = random.Random()


def tracked():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True)
    if out.returncode == 0 and out.stdout.strip():
        return [l for l in out.stdout.splitlines() if l]
    return [os.path.relpath(os.path.join(d, n), ROOT) for d, _, ns in os.walk(ROOT) if "/.git" not in d + "/" for n in ns]


def run(tmp, only):
    r = subprocess.run([sys.executable, os.path.join(tmp, "tools", "check_repo.py"), "--only", only],
                       cwd=tmp, capture_output=True, text=True, timeout=600)
    return r.returncode, r.stdout + r.stderr


def rand(n, chars=string.ascii_letters + string.digits):
    return "".join(rng.choice(chars) for _ in range(n))


class Plant:
    """Change one file in the copy, and put it back afterwards (or remove it if it was new)."""
    def __init__(self, tmp, rel):
        self.path = os.path.join(tmp, rel)
        self.old = open(self.path, "rb").read() if os.path.exists(self.path) else None

    def write(self, text):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        open(self.path, "w", encoding="utf-8").write(text)

    def text(self):
        return self.old.decode("utf-8")

    def restore(self):
        if self.old is None:
            os.remove(self.path)
        else:
            open(self.path, "wb").write(self.old)


def plants(tmp):
    """(check, label, apply) triples; apply plants the failure and returns (Plant, secret or None)."""
    out = []

    def new_file(rel, body):
        def go():
            p = Plant(tmp, rel); p.write(body); return p, None
        return go

    def edit(rel, fn):
        def go():
            p = Plant(tmp, rel); p.write(fn(p.text())); return p, None
        return go

    out.append(("json", "invalid JSON under site/", new_file("site/zz_planted.json", "{not json")))
    out.append(("python", "a tools/ script that does not compile", new_file("tools/zz_planted.py", "def broken(:\n    pass\n")))
    out.append(("calc-tests", "a calculator answer off by $1", edit("docs/assets/pnf-calc.js", lambda t: t + (
        "\nif (typeof module !== 'undefined' && module.exports && module.exports.hourly) {"
        " const _h = module.exports.hourly; module.exports.hourly = function (i) { const r = _h(i); r.rate += 1; return r; }; }\n"))))
    out.append(("site-sync", "a generated page edited by hand", edit("docs/index.html", lambda t: t + "\n<!-- planted hand edit -->\n")))

    pages = json.load(open(os.path.join(tmp, "site", "pages.json"), encoding="utf-8"))["pages"]
    draft = next((p["slug"] for p in pages if p.get("draft")), None)
    if draft:
        out.append(("drafts", f"draft page {draft} made indexable", edit(f"docs/{draft}/index.html",
                    lambda t: t.replace('name="robots" content="noindex', 'name="robots" content="index'))))
    out.append(("em-dash", "an em dash in docs/", new_file("docs/zz_planted.txt", "planted " + "—" + " dash\n")))

    # Secrets: values are built here at run time, so this file itself never matches a pattern.
    secret_cases = {
        "github_token": lambda: "gh" + "p_" + rand(36),
        "anthropic_key": lambda: "sk-" + "ant-" + rand(32),
        "aws_key": lambda: "AK" + "IA" + rand(16, string.ascii_uppercase + string.digits),
        "slack_token": lambda: "xo" + "xb-" + rand(24),
        "private_key": lambda: "-----BEGIN " + "RSA PRIVATE KEY-----\n" + rand(64) + "\n-----END RSA PRIVATE KEY-----",
        "etsy_token": lambda: rand(9, string.digits) + "." + rand(48),
        "etsy_key": lambda: "ETSY_" + "KEYSTRING=" + rand(24),
    }
    for kind, make in secret_cases.items():
        def go(kind=kind, make=make):
            value = make()
            p = Plant(tmp, f"tools/zz_planted_{kind}.txt"); p.write(f"config line\n{value}\n")
            return p, value
        out.append(("secrets", f"planted {kind}", go))

    sample = os.path.join("permits", "chicago", "sample.json")
    if os.path.exists(os.path.join(tmp, sample)):
        def personal_key(t):
            d = json.loads(t); d["projects"][0]["ownerName"] = "Planted Person"; return json.dumps(d)
        def person_tag(t):
            d = json.loads(t); d["projects"][0]["scope"] = d["projects"][0].get("scope", "") + " Consultant reviewer: Planted Person"; return json.dumps(d)
        out.append(("permit-data", "a personal field in the permit sample", edit(sample, personal_key)))
        out.append(("permit-data", "a reviewer tag in a permit scope", edit(sample, person_tag)))
    return out


def leaked(value, output):
    """True if any 6-character piece of the value's random part shows up in the output."""
    core = value.split("=", 1)[-1].replace("-----BEGIN RSA PRIVATE KEY-----", "").replace("-----END RSA PRIVATE KEY-----", "")
    core = "".join(ch for ch in core if ch.isalnum())
    return any(core[i:i + 6] in output for i in range(0, max(1, len(core) - 5)))


def main():
    tmp = tempfile.mkdtemp(prefix="pnf-gate-")
    failures, skipped, passed = [], [], 0
    try:
        for f in tracked():
            src = os.path.join(ROOT, f)
            if os.path.isfile(src):
                dst = os.path.join(tmp, f)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
        code, out = run(tmp, ",".join(CHECKS))
        clean = {c for c in CHECKS if f"ERROR {c}:" not in out}
        if code != 0:
            print("note: the repo itself has errors now, so planted tests on those checks are skipped:",
                  ", ".join(sorted(set(CHECKS) - clean)))
        for check, label, apply in plants(tmp):
            if check not in clean:
                skipped.append(f"{check}: {label}"); continue
            plant, secret = apply()
            try:
                code, out = run(tmp, check)
            finally:
                plant.restore()
            caught = code == 1 and f"ERROR {check}:" in out
            if check == "secrets" and caught:
                kind = label.split()[1]
                if f"({kind})" not in out:
                    caught = False; label += f" (reported, but not as {kind})"
                if leaked(secret, out):
                    failures.append(f"secrets: {label}: part of the value was printed"); continue
            if caught:
                passed += 1
            else:
                failures.append(f"{check}: {label} was not caught")
        code, out = run(tmp, ",".join(sorted(clean)))
        if code != 0:
            failures.append("restore: the copy did not come back clean after the planted tests")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for f in failures:
        print("FAIL", f)
    for s in skipped:
        print("SKIP", s)
    print(f"test_check_repo: {passed} planted failures caught, {len(failures)} missed, {len(skipped)} skipped")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
