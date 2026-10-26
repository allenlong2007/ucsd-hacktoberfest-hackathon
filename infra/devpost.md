# Close Call — Devpost draft

Draft only. Replace every bracketed field with verified information before
submission. Evaluation results below are sourced from the AI branch; video, eligibility,
and submission completion still require confirmation.

## Project name
Close Call

## Selected prize tracks

- [x] Open-Source AI
- [x] Best Use of Gemma 4

Selected at the team's request. Open-Source AI team entry was confirmed verbally;
Best Use of Gemma 4 eligibility is not confirmed by the recorded organizer answer.
See `infra/organizer_questions.md`. These selections are in this draft only;
no Devpost entry has been submitted or changed.

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
Team-provided runtime statement: Close Call runs Gemma 4 locally through Ollama or
through the Gemini API, and the demo uses the Gemini API. This statement has not
been verified by this documentation task; confirm the actual model identifier,
API support, and demo execution before publication.

Our design uses Gemma 4 to write structured claims. A Python
verifier checks each claim's source, author, timestamp, and quotation. Verdicts use
verified claims only. A React/TypeScript/Vite viewer presents audits and comparisons
with stale-bot and metadata baselines. [Before submission: describe which components
actually ran, exact model/version, hardware, and the final integration commit.]

## What makes the evaluation useful
Future reopening or near-identical merges within 180 days provide inferred outcome
labels. These future events stay out of model inputs. Diff similarity is used for
labeling only. Emmanuel will hand-review 30 real PRs, and Nilesh will independently double-check
5 selected PRs. Preserve and adjudicate disagreements on that overlap.

## Evaluation results

Source: `ai/out/eval_summary.json` at `main` commit `a01c7452b140ddbecef5caa5898936b0bcdb9654`
(generated `2026-10-25T23:46:48.247427+00:00`), plus `infra/gold_summary.md`.
The evaluation file is on main, but `gold_set` is currently null.
**Close Call versus human answer-key score: pending.**

**Of 25 stale-bot closures in Jest old enough to judge, 5 (20%) were wrongful
under the inferred later-redo label. The stale bot let all 5 close; Close Call
approved none of them and sent all 5 to a human.** These are historical replay
results, not actions taken on GitHub or proof of maintainer intent.

Seventeen newer closures were excluded because their 180-day window was incomplete.
All approaches below use the same 25 eligible closures.

| Approach | Inferred wrongful closures approved for closing | Inferred wrongful closures escalated | UNSUPPORTED recall | UNSUPPORTED precision | Overall escalation rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| Stale bot | 5 | 0 | 0 | undefined | 0% |
| Metadata heuristic | 5 | 0 | 0 | 0 | 0% |
| Gemma 4 26B via Gemini API | 0 | 5 | 0 | 0 | 88% |
| Gemma 4 E2B via local Ollama | 0 | 5 | 0 | 0 | 88% |

All five inferred wrongful cases were ESCALATE, not UNSUPPORTED. The result shows
conservative deferral to humans, not five affirmative wrongful-closure predictions.
An 88% escalation rate also means substantial human review remains.
Exact reported models: `gemini:models/gemma-4-26b-a4b-it` and `ollama:gemma4:e2b`.

The source-filtered gold set contains 24 PRs with human labels from Allen,
Emmanuel and Nilesh; Lio's 9 AI-assisted entries are excluded. Human-human agreement
is 1 of 2 (too small to interpret), with disagreement on slot 10. Final labels:
3 JUSTIFIED, 4 NOT_JUSTIFIED, 17 UNCERTAIN.
AI suggestions, not ground truth, matched 22 of 24 final labels. Only Emmanuel
saw AI suggestions before labeling. These 24 are a filtered, outcome-stratified
selection from 42 PRs and have a different denominator from the 25 eligible-closure
evaluation; do not combine their counts or percentages.


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
Planned: Python, GitHub CLI, Ollama, Gemini API, Gemma 4, React, TypeScript, Vite.
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
- [x] Select Open-Source AI and Best Use of Gemma 4 in this draft at the team
  request.
- [ ] Confirm Best Use of Gemma 4 eligibility with the organizer/rules.
- [ ] Verify the team-provided Gemini API demo statement against the actual run.
- [x] Add sourced evaluation counts and human-label summary with inferred-label caveats.
- [ ] Recheck results after the evaluation file merges; fill the pending gold_set score.
- [ ] Confirm author/team details and correct prize tracks; no eligibility guesses.
- [ ] Verify final code, model/license, setup, and real-data demo.
- [ ] Attach final video and verify links signed out.
- [ ] Review for secrets, personal information, and security-sensitive disclosures.
- [ ] Submit by the team's 6:15 PM target; confirm event date/timezone and official cutoff.
- [ ] Record submission URL and confirmation timestamp here: [pending].
