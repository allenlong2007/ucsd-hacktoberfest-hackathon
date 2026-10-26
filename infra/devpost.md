# Close Call — Devpost draft

Draft only. Replace every bracketed field with verified information before
submission. Evaluation results below are sourced from main; video, eligibility,
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
The workflow audits stale-bot closures using only information available
before closure. It returns CONFIRMED when verified evidence supports closure,
UNSUPPORTED when evidence supports continued review, and ESCALATE when the record
is ambiguous, incomplete, conflicting, or security-sensitive. It advises maintainers
and takes no action on GitHub.

## How we built it
Close Call runs Gemma 4 locally through Ollama (`gemma4:e2b`) or through the
Gemini API (`gemma-4-26b-a4b-it`). Committed audits cover both backends; the
planned live demo uses the Gemini API.

Our design uses Gemma 4 to write structured claims. A Python
verifier checks each claim's source, author, timestamp, and quotation. Verdicts use
verified claims only. A React/TypeScript/Vite viewer presents audits and comparisons
with stale-bot and metadata baselines. The committed evaluation includes both
backends; runtime, model size, hardware and concurrency differ, so this is not a
controlled speed comparison.

## What makes the evaluation useful
Future reopening or near-identical merges within 180 days provide inferred outcome
labels. These future events stay out of model inputs. Diff similarity is used for
labeling only. The filtered answer key retains 24 PRs with human-source labels
from three team members; assisted entries are excluded and uncertainty is retained.

## Evaluation results

Source: `ai/out/eval_summary.json` at `main` commit `9f304172d22a70866e619a749a5f183adb17e613`
(generated `2026-10-26T00:05:06.437978+00:00`), plus `infra/gold_summary.md`.
On the 24 human-labeled PRs, Close Call matched the human label on 15. On the 7 PRs where humans were confident, Close Call escalated all 7 and never contradicted a human. Its only 2 confident verdicts came on PRs that humans rated uncertain.

| Human label | UNSUPPORTED | CONFIRMED | ESCALATE |
| --- | ---: | ---: | ---: |
| NOT_JUSTIFIED | 0 | 0 | 4 |
| JUSTIFIED | 0 | 0 | 3 |
| UNCERTAIN | 1 | 1 | 15 |

Rows are human labels; columns are hosted Gemma 4 verdicts via the Gemini API.
The label mapping is NOT_JUSTIFIED ↔ UNSUPPORTED, JUSTIFIED ↔ CONFIRMED,
UNCERTAIN ↔ ESCALATE. This is label agreement, not accuracy. On the confident
human cases, Close Call abstained rather than making an opposite confident call;
it did not reproduce those human decisions. This is not a claim of error-free
classification. Human-human agreement is 1 of 2, too small to interpret.


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

Citation checks across the full 42-audit runs (not just the 25 eligible closures):
the local model had 21 of 148 citations rejected; the hosted model had 0 of 101
rejected. These are citation-verification failures, not necessarily fabricated
claims. Model size, hardware and concurrency differ; latency is not a controlled
backend speed comparison.

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
without confusing source matching with correct interpretation.

## Accomplishments and what we learned
The evaluation shows that a conservative system can decline to endorse stale
closures while still imposing substantial human review. Verified quotations do
not settle interpretation: on jest#15877 the hosted model returns UNSUPPORTED
and the local model returns CONFIRMED. A human must decide between those readings.

## What's next
Broader sampling, stronger historical snapshots and semantic verification, and
maintainer studies before any production use. Automatic PR actions are out of scope.

## Built with
Gemma 4 (`gemma-4-26b-a4b-it` via the Gemini API and `gemma4:e2b` via Ollama),
Python, React, TypeScript, Vite, GitHub GraphQL API.

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
- [x] Read the merged gold_set results and include hosted-model label agreement
  and the full confusion table without presenting agreement as accuracy.
- [ ] Add all four teammates to the Devpost project: Allen (`allenlong2007`),
  Emmanuel (`EmmanuelR21-del`), Lio (`liogular-hash`), Nilesh (`nileshbehera`).
- [ ] Select both Open-Source AI and Best Use of Gemma 4 in Devpost; confirm track requirements.
- [ ] Verify final code, model/license, setup, and real-data demo.
- [ ] Upload the final video unlisted to YouTube, paste its URL into Devpost,
  and verify links signed out.
- [ ] Review for secrets, personal information, and security-sensitive disclosures.
- [ ] Submit by the team's 6:15 PM target; confirm event date/timezone and official cutoff.
- [ ] Record submission URL and confirmation timestamp here: [pending].
