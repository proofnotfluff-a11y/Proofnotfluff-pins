#!/usr/bin/env bash
# Commit and push a data workflow's own files plus the rebuilt site, surviving a busy main.
# Why (QA 2026-10-26 FIX): permits-austin.yml rebuilt docs/ with make_site.py, then `git pull --rebase` hit
# conflicts in pages other commits had rebuilt meanwhile (index, shop, sitemap) and the run died with nothing pushed.
# Generated pages are never merged by hand: on a failed rebase this aborts, resets to the new origin/main, puts back
# only this run's own paths from its commit, rebuilds the site from them and tries again.
# Usage: tools/push_rebuilt.sh "<commit message>" <own path> [<own path> ...]
#   own paths: what this run produced (data files, members' app pages, screenshots); docs/ is always added after
#   make_site.py. Missing paths are skipped.
set -euo pipefail
msg="$1"; shift
own=()
for p in "$@"; do [ -e "$p" ] && own+=("$p"); done
git config user.name "proofnotfluff-bot"
git config user.email "proofnotfluff-bot@users.noreply.github.com"
stage() { git add -A "${own[@]}" docs; }
stage
if git diff --cached --quiet; then echo "no change"; exit 0; fi
git commit -q -m "$msg"
for i in 1 2 3 4; do
  if git pull -q --rebase origin main && git push origin HEAD:main; then exit 0; fi
  git rebase --abort 2>/dev/null || true
  mine=$(git rev-parse HEAD)
  git fetch -q origin main
  git reset -q --hard origin/main
  rm -rf "${own[@]}"
  git checkout "$mine" -- "${own[@]}"
  python3 tools/make_site.py > /dev/null
  stage
  if git diff --cached --quiet; then echo "no change after rebuild on origin/main"; exit 0; fi
  git commit -q -m "$msg"
  echo "rebuilt on origin/main (try $i)"
  sleep 5
done
exit 1
