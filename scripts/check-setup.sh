#!/usr/bin/env bash
# Checks that this machine is ready to work on the team repo.
# Usage: ./scripts/check-setup.sh dev/<area>
set -u
BRANCH="${1:-}"
ok=0
pass() { echo "  [ok]   $1"; }
fail() { echo "  [FAIL] $1"; ok=1; }

echo "Checking setup..."
command -v git >/dev/null && pass "git installed" || fail "git not installed"
command -v gh  >/dev/null && pass "GitHub CLI (gh) installed" || fail "gh not installed: https://cli.github.com"

if gh auth status >/dev/null 2>&1; then
  pass "gh logged in as $(gh api user --jq .login 2>/dev/null)"
else
  fail "gh not logged in: run 'gh auth login' (choose HTTPS, then login with a web browser)"
fi

[ -n "$(git config user.name)" ]  && pass "git user.name = $(git config user.name)"   || fail "run: git config --global user.name \"Your Name\""
[ -n "$(git config user.email)" ] && pass "git user.email = $(git config user.email)" || fail "run: git config --global user.email \"you@example.com\""

REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null || git remote get-url origin 2>/dev/null)
[ -n "$REPO" ] && pass "repo: $REPO" || fail "not inside the cloned repo"

if [ -n "$BRANCH" ]; then
  CUR=$(git branch --show-current)
  [ "$CUR" = "$BRANCH" ] && pass "on branch $BRANCH" || fail "on '$CUR', expected '$BRANCH': run 'git checkout $BRANCH'"
  if git push --dry-run origin "$BRANCH" >/dev/null 2>&1; then
    pass "can push to $BRANCH"
  else
    fail "cannot push to $BRANCH: ask the repo owner to add you as a collaborator, then accept the email invite"
  fi
fi

[ $ok -eq 0 ] && echo "All good." || echo "Fix the items marked FAIL, then rerun."
exit $ok
