# UCSD Hacktoberfest Hackathon

Team repo. The project idea is still to be decided.

## Branches
- `main`: stable, demo-ready code. Changes land only through pull requests.
- `dev/frontend`, `dev/backend`, `dev/ai`, `dev/infra`: one per member, see [OWNERSHIP.md](OWNERSHIP.md).

## Layout
```
frontend/   dev/frontend's area
backend/    dev/backend's area
ai/         dev/ai's area
infra/      dev/infra's area
shared/     contracts and types used by several areas (edit only through shared-files PRs)
scripts/    team tooling (check-setup.sh)
```

## Getting started
```bash
gh repo clone allenlong2007/ucsd-hacktoberfest-hackathon
cd ucsd-hacktoberfest-hackathon
git checkout dev/<your-area>
./scripts/check-setup.sh dev/<your-area>
```

AI agents: read [AGENTS.md](AGENTS.md) first.
