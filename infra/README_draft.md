# Close Call — README draft

Status: README draft for Allen to incorporate through PR #16. The merged main
checkout contains the collector, verifier, AI runner, evaluation and viewer.
Results below are transcribed from committed evaluation output; this documentation
task did not rerun the model evaluation.

## The problem

Inactivity is not proof that a contribution is unwanted. Stale bots can close pull
requests while maintainers still want the work. Close Call asks whether closure is
justified, and shows evidence a maintainer can inspect before making a decision.

## How it works

1. Collect a stale-bot closure and reconstruct the information visible before
   `closed_at`: PR content, comments, reviews, and linked-issue state.
2. Run Gemma 4 through Ollama or the Gemini API to propose structured, source-quoted claims.
3. A deterministic Python verifier checks source references, authors, timestamps,
   and normalized quotations. Rejected claims are excluded from the verdict.
4. Compute a verdict using verified claims only:
   - `CONFIRMED`: evidence supports closing, such as explicit abandonment,
     supersession, or maintainer rejection.
   - `UNSUPPORTED`: evidence supports continued review, such as maintainer interest
     or an approving review.
   - `ESCALATE`: insufficient, conflicting, or security-sensitive evidence needs a human.

A matching quote establishes that a source exists; it does not prove the model's
interpretation is correct. Close Call advises. It does not close, reopen, merge,
comment on PRs, or execute code from them.

## Setup

Use the existing checkout in cloud tasks; do not create a worktree. In a local
terminal without a checkout, clone the repository first. Follow `AGENTS.md` and
`OWNERSHIP.md` for your branch and folder. Infra development uses `dev/infra`.

### Prerequisites

- Git and GitHub CLI (`gh`): https://cli.github.com. Collecting real PR data requires
  working GitHub API access; Git clone access alone does not establish API access.
- Python 3.12 is available in the inspected cloud environment. No Python dependency
  manifest is currently on main; use the backend/AI owners' instructions when merged.
- Ollama: install using the official instructions at https://ollama.com/download.
  Run on a machine with enough RAM/disk and suitable CPU/GPU capacity for the actual
  model artifact. Hardware capacity and model availability have not been verified here.
- Node.js and npm for the React/Vite viewer. Node 24 and npm 11 are installed here.

Check prerequisites:

```bash
git --version
gh --version
python3 --version
node --version
npm --version
gh auth status
gh api user --jq .login
```

For local GitHub login, use `gh auth login` and `gh auth setup-git`. In cloud,
reuse platform authentication; do not put tokens into documentation or commit them.
The inspected cloud Git proxy supports Git operations, but `gh api user` returns
Forbidden. Restore API access before attempting collection.

### Planned local model setup (not yet verified)

The older contract names `gemma4:e4b`, but the supplied evaluation reports
`ollama:gemma4:e2b`. The commands below use that evaluated local tag; confirm
availability and follow the AI owner's merged instructions.
With Ollama installed and the tag confirmed:

```bash
# Separate terminal, only if an Ollama service is not already running:
ollama serve
# Another terminal:
ollama pull gemma4:e2b
ollama list
ollama run gemma4:e2b 'Return a short greeting.'
```

The greeting checks local model execution only. It does not validate Close Call's
claim schema, verifier, or evaluation. Use the merged runner from the repository root, with working GitHub API access
and a Gemini API key configured as documented in `ai/README.md`:

```bash
python3 backend/data/fetch_pr.py jestjs/jest 15880 > /tmp/close-call-pr.jsonl
python3 ai/closecall/run.py /tmp/close-call-pr.jsonl --backend gemini --output /tmp/close-call-audit.jsonl
```

The skill instructions are in `ai/skill/close-call/SKILL.md`. These commands are
transcribed from the merged CLI interfaces; this documentation task has not run
a live authenticated model request.

### Viewer setup

From the repository root, using its committed npm lockfile:

```bash
cd frontend
npm ci
npm run build
npm run dev -- --host 127.0.0.1
```

These are repository-defined commands, not a claim that this infra task tested the
viewer. The merged `frontend/public/data/` now contains real evaluated data.
The separate `shared/fixtures/` remains synthetic and must not support results.

## Data and limitations

Our dataset comes from a single repository, jestjs/jest: 42 pull requests closed by its stale bot (github-actions) between October 2024 and October 2026, of which 5 were later redone in a near-identical merged PR and 0 were reopened. We also scanned 1,000 closed home-assistant/core PRs, but only one looked like a stale-bot closure, and on inspection it was the author closing their own PR, so we dropped that repo and tightened the detector to require the bot’s own wording and to never count self-closes. Outcome labels are inferred from later events, not confirmed by maintainers, and a closure only counts as ‘redone later’ if a merged PR touched at least half the same files with at least 40% of the same added lines. 17 of the 42 closures happened less than 180 days ago, so their redo window isn’t complete; they’re excluded from the headline wrongful-closure rate. With 5 wrongful cases, every result here is a small-sample result.

Our answer key is 24 PRs labeled by three team members, judging only what was visible at close time. Lio’s 9 AI-assisted labels are excluded, and Emmanuel had seen AI-suggested labels before labeling.

The inference input must exclude `outcome`, `evidence`, post-close events, and
future diff matches. Diff similarity is used for outcome labeling, never as a
predictor. `no_evidence` does not establish justified closure. The fake records in
`shared/fixtures/` must not be used in results. Human-source filtering and agreement
counts are documented in `infra/gold_summary.md` and `infra/labeling.md`.

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


## Licenses and attribution

Repository code: MIT, as confirmed by the root `LICENSE`; preserve its copyright
and permission notice. The project brief describes the Gemma 4 model as Apache
2.0. **Model license verification remains pending**: confirm the exact downloaded
artifact's official model card, license, attribution, and any additional terms
before publishing that claim. MIT code licensing does not relicense model weights
or third-party GitHub content. Retain source URLs and respect source licenses.

## Limitations

Small or selected samples may not represent GitHub. Bot identification and inferred
labels can be wrong; API pagination, edited/deleted comments, changing issue state,
and current diffs may prevent faithful reconstruction of close-time evidence.
Check historical content rather than assuming a present-day page is a snapshot.
Reject or escalate cases with unrecoverable timing. A failed claim check can reflect
missing source data, not necessarily a model hallucination. Quote verification does
not establish entailment, factual truth, or freedom from prompt injection in PR text.
Human review remains required. Do not publish security-sensitive details.

## Team and delivery

Allen: frontend; Lio: collection/verifier/baselines; Nilesh: model/evaluation;
Emmanuel: docs/gold labels/demo/submission preparation. See `infra/devpost.md`,
`infra/demo_script.md`, and `infra/organizer_questions.md`. Organizer answers are recorded in `infra/organizer_questions.md`: teams may enter
Open-Source AI; Best Use of Gemma 4 eligibility needs clarification. Evaluation and human-label counts are reported above. Recorded video and
Devpost submission remain pending.
