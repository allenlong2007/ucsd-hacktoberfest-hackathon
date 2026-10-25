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

Emmanuel and Nilesh each open every PR's `pr_url` and its relevant comments,
reviews, and linked issues. Confirm the stale close event and its timestamp. Record
whether closing was justified using only evidence strictly before `closed_at`:

- `JUSTIFIED`: explicit abandonment, supersession, or maintainer rejection supports closing.
- `NOT_JUSTIFIED`: evidence shows continued interest or work that warranted review.
- `UNCERTAIN`: incomplete/conflicting evidence, security concerns, or no sufficient basis.

Record each reviewer's label, source permalinks, brief rationale, and UTC review
timestamp in their own columns without inspecting the other's label or model output.
Use archived/historical context where possible: a current diff or edited comment
may not represent the close-time record. Mark uncertainty when reconstruction fails.
Do not equate inactivity or lack of a later reopening with justified closure.

## Future outcome pass and adjudication

Only after both independent labels are recorded, inspect later reopen/merge events.
Record `inferred_outcome` as `reopened`, `redone_later`, or `no_evidence`, include
source permalinks, and mark `followup_180d_complete` as `YES`, `NO`, or `UNKNOWN`.
For a later merge, manually check similarity and the 180-day timing; do not accept
the collector's match blindly. An event outside the defined window needs an explicit
note rather than silently broadening the label definition. Do not alter earlier
independent judgments to agree with the future outcome.

Review disagreements together; preserve original labels. Set `adjudicated_label`
to one of the same three values and explain the resolution (including unresolved
UNCERTAIN). `review_status` progresses from `AWAITING_SAMPLE` to `READY`,
`ONE_REVIEW`, `TWO_REVIEWS`, then `ADJUDICATED`. Mark `BLOCKED` when sources are
unavailable; do not count blocked or placeholder rows as completed.

## Reporting

Use only rows with a real repo/PR, source evidence, both review timestamps and
labels, and an adjudicated label for completed-set metrics. Report the actual N,
initial agreement before adjudication, uncertain count, and valid denominator for
agreement with inferred outcomes. A future-event proxy and a judgment about closure
justification answer different questions; explain the mapping and do not treat
`no_evidence` as a definite justified label. Do not report 30 reviewed until 30 meet
these requirements. Do not show future labels to the model or execute PR code.
