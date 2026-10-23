#!/usr/bin/env python3
"""Tests for the code gate (tools/check_repo.py). Rule (Todd's Oct 15 note on agentic engineering): a model can
write the checks, so the checks get tested too. Each check must catch a failure planted in a throwaway copy of the
repo, and the secrets check must never print any part of a planted value. Nothing in the real tree changes.

Usage: python3 tools/test_check_repo.py      exit 1 if any planted failure slips through
check_repo.py runs this file as its gate-tests check, so the nightly optimizer and every push see a broken gate.
"""
import json, os, random, re, shutil, string, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKS = ["json", "python", "calc-tests", "site-sync", "drafts", "em-dash", "secrets", "permit-data", "builder-contacts", "video-specs", "voice", "fiverr-kit", "monday"]
rng = random.Random()
# Key markers are assembled here so this file never matches the secrets check itself.
KEY_BEGIN = "-----BEGIN " + "RSA PRIVATE " + "KEY-----"
KEY_END = "-----END " + "RSA PRIVATE " + "KEY-----"


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
    # Runs even when no page is a draft (Oct 17: the last draft went live), so the drafts check is always tested.
    live = next((p["slug"] for p in pages if not p.get("draft") and p.get("kind") != "leads"), None)
    if live:
        out.append(("drafts", f"live page {live} made noindex", edit(f"docs/{live}/index.html",
                    lambda t: t.replace('<link rel="canonical"', '<meta name="robots" content="noindex, nofollow"><link rel="canonical"', 1))))
    out.append(("copy", "a licenses outreach template over 75 words", edit("email/L1-OUTREACH.md",
                lambda t: t.replace("in the first few weeks.", "in the first few weeks. " + " ".join(["more"] * 40), 1))))
    out.append(("copy", "a licenses outreach template with the wrong signal word", edit("email/L1-OUTREACH.md",
                lambda t: t.replace("got its new City business license", "was cited", 1))))
    out.append(("monday", "a link in the free Monday email", edit("email/M1-MONDAY.md",
                lambda t: t.replace("To use one: call", "See proofnotfluff.com. To use one: call", 1))))
    out.append(("monday", "the stop line dropped from the Monday footer", edit("email/M1-MONDAY.md",
                lambda t: t.replace(' Reply "stop" and you won\'t get another one.', "", 1))))
    out.append(("monday", "the price dropped from the trial email", edit("email/M1-MONDAY.md",
                lambda t: t.replace("it is ${price} a month until", "it renews until", 1))))
    out.append(("em-dash", "an em dash in docs/", new_file("docs/zz_planted.txt", "planted " + "—" + " dash\n")))

    # Secrets: values are built here at run time, so this file itself never matches a pattern.
    secret_cases = {
        "github_token": lambda: "gh" + "p_" + rand(36),
        "anthropic_key": lambda: "sk-" + "ant-" + rand(32),
        "aws_key": lambda: "AK" + "IA" + rand(16, string.ascii_uppercase + string.digits),
        "slack_token": lambda: "xo" + "xb-" + rand(24),
        "private_key": lambda: KEY_BEGIN + "\n" + rand(64) + "\n" + KEY_END,
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

    # Builder contacts (Legal desk round 2, Fix 1): the repo is public, so a plain file coming back is an error, and the
    # encrypted box must keep its shape. The entry plants decrypt and re-encrypt, so they run only with LEADS_PASSWORD.
    out.append(("builder-contacts", "a plain builder_contacts.json back in the repo",
                new_file(os.path.join("permits", "chicago", "builder_contacts.json"), json.dumps({"ACMEBUILDERS": {"name": "Acme Builders"}}))))
    enc = os.path.join("permits", "chicago", "builder_contacts.enc.json")
    if os.path.exists(os.path.join(tmp, enc)):
        def weak_box(t):
            d = json.loads(t); d["rounds"] = 1000; return json.dumps(d)
        out.append(("builder-contacts", "the encrypted contacts box with weak key rounds", edit(enc, weak_box)))
        pw = os.environ.get("LEADS_PASSWORD", "")
        try:
            sys.path.insert(0, os.path.join(tmp, "tools"))
            from leads_page import decrypt, encrypt
        except ImportError:
            pw = ""
        if len(pw) >= 12:
            def reseal(fn):
                def go(t):
                    d = json.loads(decrypt(pw, json.loads(t))); fn(d); return json.dumps(encrypt(pw, json.dumps(d).encode()))
                return go
            def first_verified(d):
                return next(k for k, c in d.items() if c.get("status") == "verified")
            def person_email(d):
                k = first_verified(d); d[k]["email"] = "jane.planted@" + d[k]["website"].split("//")[-1].strip("/").removeprefix("www.")
            def directory_source(d):
                d[first_verified(d)]["source"] = "https://www.yelp.com/biz/planted-builder"
            out.append(("builder-contacts", "a person's email in the builder contacts", edit(enc, reseal(person_email))))
            out.append(("builder-contacts", "a directory as a builder contact source", edit(enc, reseal(directory_source))))
            dnl = os.path.join("permits", "chicago", "builder_do_not_list.json")
            def removed_but_verified(_):
                d = json.loads(decrypt(pw, json.load(open(os.path.join(tmp, enc), encoding="utf-8"))))
                return json.dumps([next(k for k, c in d.items() if c.get("status") == "verified")])
            out.append(("builder-contacts", "a do-not-list builder that still has a verified contact", edit(dnl, removed_but_verified)))

    example = os.path.join("promo", "specs", "examples", "f2-spot-the-mistake-40-rate.json")
    if os.path.exists(os.path.join(tmp, example)):
        def old_close(_):
            d = json.load(open(os.path.join(tmp, example), encoding="utf-8"))
            d["cta"]["say"] = "Search ProofNotFluff for the free calculator and the full workbook."
            return json.dumps(d)
        def no_formula(_):
            d = json.load(open(os.path.join(tmp, example), encoding="utf-8")); d.pop("formula", None); return json.dumps(d)
        def etsy_after_pivot(_):  # e-commerce kicker, but the captions still send viewers to Etsy (coo/PIVOT.md)
            d = json.load(open(os.path.join(tmp, example), encoding="utf-8"))
            d["audience"] = "PROOF CHECK #9 · FOR SHOPIFY SELLERS"
            d["cta"]["what"] = "Free online. No sign-up."
            return json.dumps(d)
        out.append(("video-specs", "a short with the old close", new_file(os.path.join("promo", "specs", "2026-10-16-zz-planted.json"), old_close(None))))
        out.append(("video-specs", "a dated short without a formula", new_file(os.path.join("promo", "specs", "2026-10-17-zz-planted.json"), no_formula(None))))
        out.append(("video-specs", "a pivot-era short whose captions send viewers to Etsy", new_file(os.path.join("promo", "specs", "2026-10-18-zz-planted.json"), etsy_after_pivot(None))))

        def hype_hook(_):  # fake secrecy in the headline (playbook rule 11)
            d = json.load(open(os.path.join(tmp, example), encoding="utf-8"))
            d["hook_say"] = "The secret pricing math they don't want you to know. " + d.get("hook_say", "")
            return json.dumps(d)
        out.append(("video-specs", "a short with fake secrecy in its hook", new_file(os.path.join("promo", "specs", "examples", "zz-planted-hype.json"), hype_hook(None))))

        # Heard lines (Todd, Oct 17: "No one would say 'at five ten cost'"): a price read like a price tag.
        def price_tag_read(_):
            d = json.load(open(os.path.join(tmp, example), encoding="utf-8"))
            d["fix"]["tts"] = "Want sixty grand in your pocket? Charge seventy-five."
            return json.dumps(d)
        def run_together(_):
            d = json.load(open(os.path.join(tmp, example), encoding="utf-8"))
            d["rows"][4]["tts"] = "Take out tax and costs, and you keep fifteen sixty-six dollars an hour. Fifteen."
            return json.dumps(d)
        out.append(("video-specs", "a heard price without its money word", new_file(os.path.join("promo", "specs", "examples", "zz-planted-moneyword.json"), price_tag_read(None))))
        out.append(("video-specs", "a heard price run together like a price tag", new_file(os.path.join("promo", "specs", "examples", "zz-planted-runtogether.json"), run_together(None))))

    def planted_tell(text):
        d = json.loads(text); d["pages"][0]["plantedNote"] = "Unlock your pricing potential."; return json.dumps(d)
    out.append(("voice", "an AI-sounding phrase on a site page", edit(os.path.join("site", "pages.json"), planted_tell)))

    # Fiverr kit: plants keyed to the file's structure, not its wording, so copy edits never break these tests.
    gigs, replies = os.path.join("services", "fiverr", "gigs.md"), os.path.join("services", "fiverr", "replies.md")
    if os.path.exists(os.path.join(tmp, gigs)):
        def long_title(t):  # the first title becomes 90+ characters with an ampersand
            return re.sub(r"(\*\*Title\*\*\n```\n)[^\n]*", lambda m: m.group(1) + "I will plan & build " + "a very " * 12 + "long model", t, count=1)
        def link_in_description(t):
            return re.sub(r"(\*\*Description\*\*\n```\n)", lambda m: m.group(1) + "See www.example.com first. ", t, count=1)
        def no_license(t):
            return re.sub(r"stays? ProofNotFluff's", "come with it", re.sub(r"(?i)licen[cs]e", "copy", t))
        out.append(("fiverr-kit", "an overlong gig title with &", edit(gigs, long_title)))
        out.append(("fiverr-kit", "a web address in a gig description", edit(gigs, link_in_description)))
        out.append(("fiverr-kit", "the license line removed", edit(gigs, no_license)))
    if os.path.exists(os.path.join(tmp, replies)):
        out.append(("fiverr-kit", "review bait in a reply", edit(replies, lambda t: t + "\n## Planted\n```\nPlease leave a 5-star review.\n```\n")))
    return out


def leaked(value, output):
    """True if any 6-character piece of the value's random part shows up in the output."""
    core = value.split("=", 1)[-1].replace(KEY_BEGIN, "").replace(KEY_END, "")
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
