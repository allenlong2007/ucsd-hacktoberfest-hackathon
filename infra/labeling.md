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

## Source filtering and final label rule

`label_source_1` and `label_source_2` record human / ai_assisted per submitted
entry (blank for absent second entries). Lio's 9 entries are ai_assisted: label_1
on slots 3, 7, 11, 15, 19, 23, 27; label_2 on 17, 30. All other submitted entries
are human. No submitted label, reviewer or reason is changed.

Derive human_label using human-source entries only: one label passes through;
two matching labels pass through; conflicting human labels resolve to UNCERTAIN.
Rows without human-source entries have blank human_label and are excluded from the
answer key. Slots 7, 11, 15, 19, 23, 27 are excluded; slot 17 now uses Allen's
JUSTIFIED label alone. `answer_key_eligible` records inclusion explicitly.
Review timestamps remain blank because actual review times were not provided.

## Interpretation and export

`infra/gold_summary.md` gives counts on 24 human-labeled PRs only.
Human-human agreement: 1 of 2 (too small to interpret), on slots 10 and 24 only.
The export `infra/gold_labels.json` contains 24 PRs, 3 human-source reviewers and
2 double-human slots; assisted entries are not exported as answer-key labels.
Score rePRieve against human_label using UNSUPPORTED ↔ NOT_JUSTIFIED,
CONFIRMED ↔ JUSTIFIED, ESCALATE ↔ UNCERTAIN. Nilesh owns the evaluation code and
`eval_summary.json`; infra does not edit his files.

Use only information visible before each PR's closed_at for closure judgments.
Later outcomes are inference labels, not model inputs. no_evidence is not a label
of justified closure. Sample selection includes all five inferred redone_later
cases and 25 of the other 37 Jest PRs (sorted PR numbers, Random(0).sample).
The CSV retains the pinned sample commit, SHA-256, and agent suggestions separately.

## Limitations

Lio's 9 labels were AI-assisted and are excluded from the answer key; only Emmanuel saw AI suggestions before labeling.
Reviewer independence and exposure follow the team's report. The sample is
outcome-stratified; do not infer population prevalence from it. Present-day pages
may not reconstruct past edits. User explanations have been transcribed, not
independently reverified during finalization. Source entries with missing evidence
permalinks remain missing; they were not fabricated.
