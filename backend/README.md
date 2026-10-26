# backend

Owned by the `dev/backend` branch (see ../OWNERSHIP.md). Data shapes are defined in
`../shared/CONTRACT.md`. Python 3 standard library only; GitHub access goes through `gh`.

## `data/fetch_stale_closures.py`: collect stale-bot closures
Scans closed (and reopened) PRs in each repo, keeps the ones a stale bot closed, and records
only what was visible before the close: files, comments, reviews and linked issues. Each PR
also gets an inferred outcome, which is a label only and never shown to the model:
`reopened` (reopened after the close), `redone_later` (a near-identical change merged within
180 days), or `no_evidence`.

```
gh auth status
python3 backend/data/fetch_stale_closures.py [--repos home-assistant/core,jestjs/jest] [--max 1500] [--no-extra]
```
Writes `data/out/stale_closures.jsonl` (gitignored) and a committed sample of up to 200 rows,
including every wrongful closure, at `data/sample/stale_closures_sample.jsonl`.
It uses the GraphQL helper in `data/fetch_live.py`.

## `data/fetch_pr.py`: fetch one PR for a live audit
Prints one PR as a single `stale_closure` JSON line, with `outcome: null` and `evidence: {}`.
Comments, reviews and linked issues stop at the close (the stale-bot close if there was one);
for an open PR the cutoff is now and `close_actor` is null.

```
python3 backend/data/fetch_pr.py jestjs/jest 15880 > /tmp/pr.jsonl
```

## `verifier/`: claim fact-checker
`verify_claims(pr, claims)` in `verifier/verify.py` checks each model-written claim against
the PR data: the referenced comment, review or issue must exist, have that author, come from
before `closed_at`, and contain the quoted text. It fills in `verified` and `check`. No AI.

```
python3 backend/verifier/test_verify.py
```

## `eval/baselines.py`: baselines
The stale bot (closes everything) and the metadata heuristic from `shared/PLAN.md`: flag as
still wanted if there was an approving review, a maintainer comment, or author activity in
the 30 days before the close. Uses only pre-close data.

```
python3 backend/eval/baselines.py --input backend/data/out/stale_closures.jsonl
python3 backend/eval/test_baselines.py
```
