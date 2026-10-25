# Thirty-PR gold-set protocol

Status: 30 real Jest PRs assigned and inspected by the agent on GitHub. Provisional
labels and rationales are in the `agent_*` columns of `infra/gold_set.csv`, with
source excerpts and page hashes in `infra/gold_set_agent_evidence.jsonl`.
**0 human reviews are claimed.** Emmanuel must confirm or replace each agent label
in his own columns; Nilesh's independent fields remain blank.

## Selected sample and provenance

The supplied backend sample has 42 Jest PRs: 5 `redone_later` and 37 `no_evidence`.
At Emmanuel's instruction, include all 5 inferred wrongful closures and 25 others.
The latter are sampled without replacement from PR-number-sorted `no_evidence`
records with `random.Random(0).sample(..., 25)`. Preserve this order in the sheet.
Every row records the backend commit and SHA-256 of the full input sample.
No fixture records or duplicate PRs are included.

This replaces the earlier plan to sample 30 uniformly. It is outcome-stratified:
**do not estimate the 42-PR population's wrongful-closure rate from these 30**.
The five collector labels are inferred, not human-confirmed wrongful closures.
The agent saw the outcome strata during selection and opened present-day GitHub
pages, so these are neither blinded human labels nor fully reconstructed historical
snapshots. A human should make their own close-time judgment, without copying the
outcome or accepting an agent label uncritically.

Agent review fetched all 30 PR conversation pages and inspected their descriptions,
visible comments and reviews, alongside the sample's close-time fields. Relevant
linked issues were opened where needed for the rationale. Full diffs, edit history,
and all linked issue timelines were not reconstructed. Unresolved cases are marked
UNCERTAIN rather than treating inactivity as proof of abandonment.

`AGENT_REVIEWED_PENDING_HUMAN` does not count toward completed gold labels.
The agent columns are suggestions with rationale and source URLs; human reviewer
and adjudication columns stay empty until the corresponding work is actually done.
`inferred_outcome` is copied from the collector, not independently verified by this
review. `followup_180d_complete` indicates elapsed observation opportunity only,
not that all later events were collected or inspected.

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
