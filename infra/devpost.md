# Close Call — Devpost draft

Draft only. Replace every bracketed field with verified information before
submission. No real evaluation, video, eligibility, or completed submission is
claimed by this document.

## Project name
Close Call

## Elevator pitch
Before a stale bot closes a pull request, check whether closure is justified using
source-quoted claims and a deterministic evidence verifier.

## Inspiration
A quiet PR can still contain work a maintainer wants. We want inactivity to trigger
a careful review rather than erase the context around a contributor's work.

## What it does
The planned workflow audits stale-bot closures using only information available
before closure. It returns CONFIRMED when verified evidence supports closure,
UNSUPPORTED when evidence supports continued review, and ESCALATE when the record
is ambiguous, incomplete, conflicting, or security-sensitive. It advises maintainers
and takes no action on GitHub.

## How we built it
Our design uses local Gemma 4 through Ollama to write structured claims. A Python
verifier checks each claim's source, author, timestamp, and quotation. Verdicts use
verified claims only. A React/TypeScript/Vite viewer presents audits and comparisons
with stale-bot and metadata baselines. [Before submission: describe which components
actually ran, exact model/version, hardware, and the final integration commit.]

## What makes the evaluation useful
Future reopening or near-identical merges within 180 days provide inferred outcome
labels. These future events stay out of model inputs. Diff similarity is used for
labeling only. Emmanuel will hand-review 30 real PRs, and Nilesh will independently double-check
5 selected PRs. Preserve and adjudicate disagreements on that overlap.

## Results — fill from real output only
- Dataset: [N stale closures], [repository list], collected [date/time and timezone].
- Follow-up coverage and exclusions: [counts and reasons].
- Inferred wrongful closures: [count]/[eligible N] ([rate]).
- Shared comparison subset: [N and sampling method].
- Stale bot: recall [value], precision [value or undefined], escalation [value].
- Metadata heuristic: recall [value], precision [value or undefined], escalation [value].
- Close Call: recall [value], precision [value or undefined], escalation [value].
- Claim verification: [rejected]/[total], with rejection reasons [summary].
- Gold set: [completed N]/30; pre-adjudication agreement on double-checked subset [matches]/[completed pairs, target 5];
  agreement with inferred labels [value and denominator]; uncertain cases [N].

Never substitute `shared/fixtures/` or current viewer example numbers. A rejected
claim is a verification failure; inspect the cause before calling it hallucination.
No evidence of a later event is not proof that closure was correct.

## Challenges
Reconstructing historical evidence without leaking future outcomes; preserving
uncertainty rather than manufacturing a confident verdict; checking quotations
without confusing source matching with correct interpretation. [Add observed
implementation challenges only after the team confirms them.]

## Accomplishments and what we learned
[Add demonstrated accomplishments, concrete failure examples, and lessons after
integration. Avoid saying the pipeline is complete while it remains unverified.]

## What's next
Broader sampling, stronger historical snapshots and semantic verification, and
maintainer studies before any production use. Automatic PR actions are out of scope.

## Built with
Planned: Python, GitHub CLI, Ollama, Gemma 4, React, TypeScript, Vite.
[Confirm final stack and exact model artifact before submission.]

## Links and licenses
- Source: https://github.com/allenlong2007/ucsd-hacktoberfest-hackathon
- Video: [public final video URL; verify signed-out access].
- Demo: [working demo URL if available; otherwise omit].
- Code: MIT (root LICENSE).
- Model: Apache 2.0 according to the project brief; verify the exact artifact's
  official license and attribution before making this a final claim.
- Third-party data: public GitHub content; preserve attribution and source terms.

## Submission checklist (Emmanuel and Allen)
- [x] Emmanuel reports organizer confirmation that teams can enter Open-Source AI.
- [ ] Clarify Best Use of Gemma 4 eligibility; reported answer suggests local/cloud
  execution counts for Open-Source AI only. Do not claim Gemma prize eligibility.
- [ ] Replace placeholders with real results; name inferred labels and sample sizes.
- [ ] Confirm author/team details and correct prize tracks; no eligibility guesses.
- [ ] Verify final code, model/license, setup, and real-data demo.
- [ ] Attach final video and verify links signed out.
- [ ] Review for secrets, personal information, and security-sensitive disclosures.
- [ ] Submit by the team's 6:15 PM target; confirm event date/timezone and official cutoff.
- [ ] Record submission URL and confirmation timestamp here: [pending].
