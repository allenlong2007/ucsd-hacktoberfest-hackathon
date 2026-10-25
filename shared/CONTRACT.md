# Data contract

Every area reads and writes these shapes. Don't change a field without a shared-files PR.
Example files are in `shared/fixtures/`. They are **fake, for building the UI only**, and must
never be used in results.

All files are JSON Lines (one object per line) unless they end in `.json`.

## 1. `stale_closure` (written by backend)
Written to `backend/data/out/stale_closures.jsonl`. A sample is committed at
`backend/data/sample/stale_closures_sample.jsonl`.

```json
{
  "repo": "owner/name",
  "pr_number": 123,
  "title": "Fix race in scheduler",
  "author": "alice",
  "created_at": "2024-01-02T10:00:00Z",
  "closed_at": "2024-04-02T10:00:00Z",
  "close_actor": "github-actions",
  "close_comment": "This PR was closed because it has not had recent activity...",
  "files": [{"path": "src/a.py", "additions": 10, "deletions": 2}],
  "comments": [{"id": "IC_1", "author": "bob", "author_association": "MEMBER",
                "created_at": "2024-02-01T00:00:00Z", "body": "..."}],
  "reviews": [{"id": "R_1", "author": "bob", "state": "APPROVED", "submitted_at": "..."}],
  "linked_issues": [{"number": 99, "state_at_close": "OPEN"}],
  "outcome": "reopened | redone_later | no_evidence",
  "evidence": {"reopened_at": null, "matched_pr": 456, "file_overlap": 0.8, "line_jaccard": 0.55}
}
```
`comments`, `reviews` and `linked_issues` contain **only items from before `closed_at`**.
`outcome` and `evidence` are labels only. The model must never see them.

## 2. `claim` (written by Gemma, checked by the verifier)
```json
{"type": "comment | review | issue | activity",
 "ref": "IC_1",
 "author": "bob",
 "quote": "we want this",
 "supports": "keep_open | close",
 "verified": true,
 "check": "comment IC_1 by bob contains quote"}
```
The verifier is `backend/verifier/verify.py`, exposing
`verify_claims(pr: dict, claims: list[dict]) -> list[dict]`. It fills in `verified` and
`check`. A claim passes only if `ref` exists in the PR data, its author matches, its
timestamp is before `closed_at`, and `quote` appears in the body (case-insensitive,
whitespace-normalized).

## 3. `audit_result` (written by ai)
Written to `ai/out/audits.jsonl`:
```json
{"repo": "owner/name", "pr_number": 123,
 "verdict": "CONFIRMED | UNSUPPORTED | ESCALATE",
 "summary": "One sentence a maintainer can read.",
 "claims": ["...claim objects..."],
 "reasons_not_to_close": ["..."],
 "claims_total": 5, "claims_rejected": 1,
 "model": "gemma4:e4b", "latency_s": 12.3,
 "outcome": "reopened"}
```
`outcome` is copied in **after** inference, for scoring only.

## 4. `eval_summary` (written by ai)
Written to `ai/out/eval_summary.json`:
```json
{"generated_at": "...",
 "headline": {"repos": ["owner/name"], "stale_closures": 300, "wrongful": 42, "wrongful_rate": 0.14},
 "approaches": [
   {"name": "Stale bot", "n": 300, "wrongful_caught": 0, "recall": 0.0, "precision": null, "escalation_rate": 0.0},
   {"name": "Metadata heuristic", "n": 300, "wrongful_caught": 20, "recall": 0.48, "precision": 0.31, "escalation_rate": 0.0},
   {"name": "Close Call (Gemma 4 + verifier)", "n": 80, "wrongful_caught": 15, "recall": 0.6, "precision": 0.5, "escalation_rate": 0.2}
 ],
 "hallucination": {"claims_total": 400, "claims_rejected": 37},
 "gold_set": {"n": 30, "agreement_with_inferred_labels": 0.83},
 "notes": ["Labels are inferred from later reopen or merge events."]}
```

## Where the frontend reads from
Frontend agent 1 copies the final files into `frontend/public/data/` at 5:15
(`audits.jsonl`, `eval_summary.json`). Until then, it uses copies of `shared/fixtures/`.
