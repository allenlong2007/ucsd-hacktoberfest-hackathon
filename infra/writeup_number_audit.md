# Final write-up number audit

Sources: merged `ai/out/eval_summary.json` and `infra/gold_summary.md`.
Applies to `infra/devpost.md` and `infra/README_draft.md`.

## Comparable result counts — match

| Claim | Source |
| --- | --- |
| 25 eligible closures, 5 inferred wrongful, 20%; 17 excluded for incomplete 180-day window | eval_summary.headline |
| Stale bot and heuristic: 5 wrongful approved, 0 escalated | eval_summary.approaches |
| Both models: 0 wrongful approved, 5 escalated; 88% overall escalation | eval_summary.approaches |
| UNSUPPORTED recall 0 for all approaches; precision undefined for stale bot and 0 for the rest | eval_summary.approaches |
| Local 21 rejected / 148 citations; hosted 0 / 101 | eval_summary.approaches; full-run scope documented in ai/README.md |
| 24 gold PRs; 15 matched labels | eval_summary.gold_set.n and close_call_agreement |
| 7 confident human cases all escalated | confusion JUSTIFIED row total 3 + NOT_JUSTIFIED row total 4 |
| 2 confident model verdicts on uncertain-human PRs | confusion UNCERTAIN: 1 CONFIRMED + 1 UNSUPPORTED |
| Confusion rows: NOT_JUSTIFIED 0/0/4; JUSTIFIED 0/0/3; UNCERTAIN 1/1/15 | eval_summary.gold_set.confusion, columns UNSUPPORTED/CONFIRMED/ESCALATE |
| 3 human-source reviewers, 1/2 human-human agreement | eval_summary.gold_set and gold_summary |
| 3 JUSTIFIED, 4 NOT_JUSTIFIED, 17 UNCERTAIN; AI suggestions match 22/24 | gold_summary |
| 42-PR source population, 5 inferred redone_later cases | gold_summary |

No numerical discrepancy was found among the comparable benchmark claims. 15/24
is label agreement, not accuracy. Abstention on the 7 confident human cases is not
agreement with those decisions or proof of correct classification.

## Exclusion units differ — not competing counts

Gold summary excludes **9 assisted label entries** and **6 assisted-only PRs**.
The evaluation field excluded_ai_assisted=6 counts PRs, though its note loosely
calls them labels. Drafts retain 9 entries excluded and an answer key of 24 PRs.
Do not change 9 entries to 6 entries or describe 6 excluded PRs as 9 PRs.

## Not substantiated by the two summary files

The following facts remain in Lio's user-supplied, explicitly approved paragraph
verbatim. They are not numerical contradictions, but these two summary files alone
do not verify them:

- 0 reopened PRs.
- 1,000 home-assistant/core PRs scanned; one candidate rejected as an author self-close.
- Collection range October 2024 through October 2026.
- Matching thresholds: at least half the files and at least 40% of added lines.

Technical versions (Python 3.12, Node 24, npm 11), model IDs containing 4/26b/e2b,
the requested Apache 2.0 license claim pending artifact verification, PR numbers,
source commit/timestamps, and team target times are not outcome statistics and are
not sourced from those result summaries. They remain attributed to runtime checks,
repository interfaces, the project brief or the team's instructions as appropriate.

## Exposure limitation needing team awareness

The requested drafts say only Emmanuel saw AI suggestions before labeling, following
the team's explicit instruction. The merged ai/out/README.md also describes Nilesh's
labels as human-finalized after suggestions. This is a provenance wording conflict,
not a numerical discrepancy; resolve with the team before claiming a blinded study.
The write-up makes no claim that the answer key is fully blinded or unassisted.
