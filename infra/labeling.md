# Human label protocol and finalization

## Actual reviewers and assignment

The collection plan called for four reviewers in a round-robin split, with five
double-labeled slots (3, 10, 17, 24, 30). The user subsequently specified that **all
four submitted blocks belong to Emmanuel**. The final files therefore record one
reviewer, not four; both entries on repeated slots are attributed to Emmanuel.
Do not describe these repeated submissions as independent double reviews.

## Source and transcription

35 submitted label entries cover 30 unique Jest PRs. Labels are restricted to
JUSTIFIED, NOT_JUSTIFIED, UNCERTAIN. At the user's instruction, casing/spaces were
normalized (e.g. Not Justified → NOT_JUSTIFIED); explanation text is retained,
with the AI-assisted source tags removed. No missing label was filled by the agent.
`label_1/reviewer_1/reason_1` and `label_2/reviewer_2/reason_2` preserve entries in
source order. The second group exists only on slots 3, 10, 17, 24, 30.

## Final label rule

For a single entry, human_label is that entry. For identical repeated entries,
it is the shared label. For conflicting entries, human_label is UNCERTAIN and
adjudication_rationale notes disagreement and that both entries belong to Emmanuel.
Original submitted labels are never overwritten by this resolution rule.
Review timestamps remain blank because the actual times were not provided.

## Interpretation and export

`infra/gold_summary.md` gives count tables and same-reviewer consistency only.
`infra/gold_labels.json` exports the final labels with reviewers=1, and explicitly
identifies agreement as repeated-entry consistency, not independent agreement.
Score Close Call against human_label using UNSUPPORTED ↔ NOT_JUSTIFIED,
CONFIRMED ↔ JUSTIFIED, ESCALATE ↔ UNCERTAIN. Nilesh owns the evaluation code and
`eval_summary.json`; infra does not edit his files.

Use only information visible before each PR's closed_at for closure judgments.
Later outcomes are inference labels, not model inputs. no_evidence is not a label
of justified closure. Sample selection includes all five inferred redone_later
cases and 25 of the other 37 Jest PRs (sorted PR numbers, Random(0).sample).
The CSV retains the pinned sample commit, SHA-256, and agent suggestions separately.

## Limitations

Emmanuel saw AI-suggested labels as cross-references before submitting his labels.
The user attributed all four blocks to Emmanuel, so there is no basis to claim
other independent reviewers labeled without seeing suggestions. The sample is
outcome-stratified; do not infer population prevalence from it. Present-day pages
may not reconstruct past edits. User explanations have been transcribed, not
independently reverified during finalization. Source entries with missing evidence
permalinks remain missing; they were not fabricated.
