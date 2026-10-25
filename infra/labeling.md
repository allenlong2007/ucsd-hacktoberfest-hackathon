# Human label protocol and finalization

## Reviewers and assignment

Four human reviewers used the team's round-robin assignment (corrected by the
team's explicit slot list):

| Primary reviewer | Slots |
| --- | --- |
| Allen | 1, 5, 9, 13, 17, 21, 25, 29 |
| Emmanuel | 2, 6, 10, 14, 18, 22, 26, 30 |
| Lio | 3, 7, 11, 15, 19, 23, 27 |
| Nilesh | 4, 8, 12, 16, 20, 24, 28 |

Second reviewers: slot 3 Allen; 10 Nilesh; 17 Lio; 24 Emmanuel; 30 Lio.
Original message blocks identify the labels and explanations on these slots.
Slots 17 and 24 were reordered to put the primary reviewer first; no label or
explanation was changed.

## Source and transcription

35 submitted label entries cover 30 unique Jest PRs. Labels are restricted to
JUSTIFIED, NOT_JUSTIFIED, UNCERTAIN. At the user's instruction, casing/spaces were
normalized (e.g. Not Justified → NOT_JUSTIFIED); explanation text is retained,
with the AI-assisted source tags removed. No missing label was filled by the agent.
`label_1/reviewer_1/reason_1` and `label_2/reviewer_2/reason_2` preserve label/explanation pairs with the primary reviewer first. The second group exists only on slots 3, 10, 17, 24, 30.

## Final label rule

For a single entry, human_label is that entry. For identical repeated entries,
it is the shared label. For conflicting entries, human_label is UNCERTAIN and
adjudication_rationale notes "reviewers disagreed".
Original submitted labels are never overwritten by this resolution rule.
Review timestamps remain blank because the actual times were not provided.

## Interpretation and export

`infra/gold_summary.md` gives count tables and inter-reviewer agreement.
`infra/gold_labels.json` exports the final labels with reviewers=4 and both assigned
reviewers per PR. Inter-reviewer agreement: 2 of 5 double-labeled PRs (different reviewers, labeling independently). Small n, so indicative only.
Score Close Call against human_label using UNSUPPORTED ↔ NOT_JUSTIFIED,
CONFIRMED ↔ JUSTIFIED, ESCALATE ↔ UNCERTAIN. Nilesh owns the evaluation code and
`eval_summary.json`; infra does not edit his files.

Use only information visible before each PR's closed_at for closure judgments.
Later outcomes are inference labels, not model inputs. no_evidence is not a label
of justified closure. Sample selection includes all five inferred redone_later
cases and 25 of the other 37 Jest PRs (sorted PR numbers, Random(0).sample).
The CSV retains the pinned sample commit, SHA-256, and agent suggestions separately.

## Limitations

Only Emmanuel saw the AI suggestions before labeling.
Reviewer independence and exposure follow the team's report. The sample is
outcome-stratified; do not infer population prevalence from it. Present-day pages
may not reconstruct past edits. User explanations have been transcribed, not
independently reverified during finalization. Source entries with missing evidence
permalinks remain missing; they were not fabricated.
