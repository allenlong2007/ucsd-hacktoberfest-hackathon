# Instructions for AI coding agents (Claude, Codex, Gemini, Copilot, Cursor, etc.)

Four people work in this repo at the same time, each with their own AI model.
Follow these rules exactly so we don't cause merge conflicts.

## 1. Find out who you're working for
Run `git config user.name` and `gh api user --jq .login`, then look the user up in
`OWNERSHIP.md`. That table gives **their branch** and **the one folder they own**.
If the user isn't listed, the table still says `TODO`, or the user has more than one row
(Allen has two frontend agents), stop and ask them which row is yours before you edit
anything, unless your instructions already name your branch.

## 2. Stay on your branch
- Work only on the user's `dev/<area>` branch. Never commit directly to `main`.
- At the start of every session, run `git checkout dev/<area> && git pull --rebase origin main`.

## 3. Stay in your folder
- You may read any file in the repo.
- You may **create, edit, or delete files only inside the user's own folder** (for example `backend/`).
- Don't edit another member's folder, and don't edit the shared files listed in
  `OWNERSHIP.md` (`shared/`, root docs, `.github/`, `.claude/`, `scripts/`) on a dev branch.
  If you need a change there, tell the user what change you need and who owns that area.
- CI rejects any PR that breaks this rule, so it's cheaper to follow it up front.

## 4. Commit and sync often
- Make small commits with clear messages, for example `backend: add /login endpoint`.
- Push to the user's branch: `git push -u origin dev/<area>`.
- Merge into `main` only through a pull request: `gh pr create --base main --head dev/<area>`.
- After someone else's PR merges, run `git pull --rebase origin main` again.

## 5. Interfaces between areas
When your area talks to another one (for example frontend calling backend), the contract
(routes, request and response shapes, shared types) lives in `shared/`. Propose changes to
it in a small shared-files PR. Don't hard-code guesses in your own folder without telling
the user.

## 6. Never
- `git push --force` to `main`, or to another member's branch
- Commit secrets. Put API keys in `.env`, which is gitignored.
- Run `git add -A` from the repo root without checking `git status` first
