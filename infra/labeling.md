# Thirty-PR gold-set protocol

Status: sheet prepared; 0 real PRs assigned or reviewed. Lio's real sample is not
available in the inspected checkout or backend branch. Never label the fake
`shared/fixtures/` records as real observations.

## Select and record the sample

Use `backend/data/sample/stale_closures_sample.jsonl` once Lio supplies it. Record
its commit SHA and SHA-256 in every assigned row. Confirm `_fixture` is absent/false,
repo/PR pairs are unique, and the rows describe actual stale-bot closures. Pin an
eligible population before looking at human judgments. For a simple reproducible
selection, sort unique eligible repo/PR pairs lexicographically and sample 30
without replacement using Python `random.Random(0).sample`; save the selected
order in the sheet. If fewer than 30 are available, use all and report the shortfall;
do not duplicate rows. Document exclusions and reasons separately in notes.
Do not change selection to produce more favorable model results.

## Independent close-time judgments

Emmanuel opens all 30 PRs at their `pr_url` and their relevant comments,
reviews, and linked issues. Confirm the stale close event and its timestamp. Record
whether closing was justified using only evidence strictly before `closed_at`:

- `JUSTIFIED`: explicit abandonment, supersession, or maintainer rejection supports closing.
- `NOT_JUSTIFIED`: evidence shows continued interest or work that warranted review.
- `UNCERTAIN`: incomplete/conflicting evidence, security concerns, or no sufficient basis.

Emmanuel records each label, source permalinks, rationale, and UTC timestamp in his
columns without inspecting model output. Before reviewing labels, select 5 of the
assigned slots using `random.Random(1).sample(sorted(assigned_slots), 5)` and mark
`nilesh_double_check=YES`; mark the remaining slots `NO`. If fewer than 5 real PRs
are assigned, double-check all of them and report the actual overlap size.
Nilesh independently reviews only those 5, without seeing Emmanuel's label, model
output, or future outcomes, and fills his own evidence, rationale, and timestamp.
Leave Nilesh's review fields blank for the other 25; blank means not assigned,
not agreement. This is 35 reviews total, not 60.
Use archived/historical context where possible: a current diff or edited comment
may not represent the close-time record. Mark uncertainty when reconstruction fails.
Do not equate inactivity or lack of a later reopening with justified closure.

## Future outcome pass and adjudication

Inspect later reopen/merge events only after Emmanuel's close-time label is frozen;
for the 5 double-checked PRs, wait until Nilesh's independent label is frozen too.
Record `inferred_outcome` as `reopened`, `redone_later`, or `no_evidence`, include
source permalinks, and mark `followup_180d_complete` as `YES`, `NO`, or `UNKNOWN`.
For a later merge, manually check similarity and the 180-day timing; do not accept
the collector's match blindly. An event outside the defined window needs an explicit
note rather than silently broadening the label definition. Do not alter earlier
independent judgments to agree with the future outcome.

Review disagreements on the 5 overlapping PRs together; preserve original labels.
For the other 25, retain Emmanuel's label as the final label and explicitly note
"single reviewer" in `adjudication_rationale`; do not call it independent consensus.
Set `adjudicated_label`
to one of the same three values and explain the resolution (including unresolved
UNCERTAIN). `review_status` progresses from `AWAITING_SAMPLE` to `READY`,
`ONE_REVIEW`, then `COMPLETE_SINGLE` for the 25 single-reviewed PRs. For the 5
double-checked PRs, use `TWO_REVIEWS` then `ADJUDICATED`. Mark `BLOCKED` when sources are
unavailable; do not count blocked or placeholder rows as completed.

## Reporting

Count a single-reviewed row as completed only with a real repo/PR, Emmanuel's label,
evidence and timestamp, a final `adjudicated_label`, and `COMPLETE_SINGLE` status.
Double-checked rows require both reviewers' evidence, timestamps and labels plus a
final label and `ADJUDICATED` status. Report 30 primary reviews and 5 independent
double-checks only when those counts are actually completed.
Compute inter-reviewer agreement only on the double-checked rows before adjudication:
exact matches / completed independent pairs (target denominator 5, not 30).
Include UNCERTAIN as a label for exact agreement and report its count. Do not
present agreement on 5 PRs as a reliable estimate for all 30 or the full dataset.
Report actual completed N, single/double-reviewed counts, uncertain count, and the
valid denominator for agreement with inferred outcomes separately. A future-event proxy and a judgment about closure
justification answer different questions; explain the mapping and do not treat
`no_evidence` as a definite justified label. Do not report 30 reviewed until 30 meet
these requirements. Do not show future labels to the model or execute PR code.
