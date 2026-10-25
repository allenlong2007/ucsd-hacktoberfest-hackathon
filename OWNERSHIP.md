# Ownership map: who works where

This file is how we avoid merge conflicts. **Each person (and their AI model) edits only
the folder they own, on their own branch.** CI checks every pull request against this map
and fails it if a branch touches a folder it doesn't own.

| Member | GitHub username | Branch | Owns folder | Scope |
|--------|-----------------|--------|-------------|-------|
| Allen (lead), frontend agent 1 | `allenlong2007` | `dev/frontend` | `frontend/` **except** `frontend/src/components/` and `frontend/src/styles/` | Close Call app shell: Audit and Results pages, routing, data loading, `package.json` |
| Allen (lead), frontend agent 2 | `allenlong2007` | `dev/frontend-ui` | `frontend/src/components/`, `frontend/src/styles/` | VerdictBadge, ClaimList, PRCard, ResultsChart, HeadlineStat, theme |
| Lio | `liogular-hash` | `dev/backend` | `backend/` | Stale-closure data collection, claim verifier, baselines |
| Nilesh | `nileshbehera` | `dev/ai` | `ai/` | Gemma 4 claim prompt, Close Call runner, evaluation, `ai/skill/close-call/SKILL.md` |
| Emmanuel | `EmmanuelR21-del` | `dev/infra` | `infra/` | README content, gold-set labeling, demo video, Devpost write-up |

Allen runs two frontend agents at the same time, so `frontend/` is split between them:
agent 1 never edits `components/` or `styles/`, and agent 2 edits nothing else. If agent 2
needs a new npm package, it asks agent 1, which owns `package.json`.

Project: **Close Call**. See `shared/PLAN.md` and `shared/CONTRACT.md`. If you
rename a folder or branch, also update `.github/ownership.json`. CI reads that file.

## Shared files (conflict hotspots)

Nobody edits these on a dev branch. Change them only through a small PR that **only**
touches shared files, and say so in the team chat first:

- `shared/`: API contracts, shared types, and constants that more than one area depends on
- Root files: `README.md`, `OWNERSHIP.md`, `ONBOARDING.md`, `AGENTS.md`, `CLAUDE.md`, `.github/`, `.claude/`, `scripts/`
- Dependency manifests at the repo root, if we add any

**Rule of thumb:** if your change needs someone else's folder, don't make it yourself. Open
an issue or message the owner, and agree on the interface in `shared/` first.
