# Two saved-audit demo examples

## jest#15877: verified citations do not settle interpretation

Hosted Gemma 4 26B returns **UNSUPPORTED**; local Gemma E2B returns **CONFIRMED**.
Both runs have zero rejected claims for this PR. The hosted model treats the
maintainer's preference to fix resolution inside Jest as a keep-open signal;
the local model treats the author's clarification as a close-supporting signal.

The verifier establishes that quotes exist, with matching authors and timestamps.
It does not establish that the model interpreted the quotes correctly. Show the
disagreement as a case needing human judgment, not as a disagreement the verifier
automatically resolved. There is no implemented cross-model adjudicator, and
`no_evidence` does not prove the local CONFIRMED verdict is correct.

Source: https://github.com/jestjs/jest/pull/15877

## jest#15880: rePRieve refused to approve closure

Both models return **ESCALATE**, with real verified evidence of the author's
pre-closure request for review. The inferred outcome is `redone_later`.
Describe this as an inferred wrongful closure routed to a human. Do not count
ESCALATE as UNSUPPORTED or report it as a positive detection in recall.

Source: https://github.com/jestjs/jest/pull/15880

## Evaluation denominator

Headline and verdict metrics use 25 PRs with complete 180-day follow-up windows
as of 2026-10-25. Five have inferred wrongful outcomes (20%). Each model lets zero
of these five close and escalates all five; neither positively flags any of them.
Both models escalate 22/25 eligible PRs (88%), a substantial review workload.
Claims and latency statistics use all 42 audits; the 17 newer closures are excluded
only from outcome-based evaluation. The 26B and E2B models also differ in runtime,
hardware, and concurrency, so latency is an operational comparison, not a controlled
backend speed benchmark.
