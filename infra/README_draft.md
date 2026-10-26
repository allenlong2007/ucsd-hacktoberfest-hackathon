# Close Call — README draft

Status: documentation draft for Allen to incorporate through a shared-files PR. The
architecture below is the agreed design in `shared/PLAN.md` and `shared/CONTRACT.md`;
the complete collector → model → verifier → evaluation pipeline is not yet present
on the inspected main checkout. Reported evaluation results are transcribed below; this infra task did not rerun
the model evaluation.

## The problem

Inactivity is not proof that a contribution is unwanted. Stale bots can close pull
requests while maintainers still want the work. Close Call asks whether closure is
justified, and shows evidence a maintainer can inspect before making a decision.

## How it works

1. Collect a stale-bot closure and reconstruct the information visible before
   `closed_at`: PR content, comments, reviews, and linked-issue state.
2. Run Gemma 4 locally through Ollama to propose structured, source-quoted claims.
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
claim schema, verifier, or evaluation. Use the AI owner's runner and pinned model
instructions once merged; no working pipeline command or skill installation command
is available on main yet. Never show a guessed install command in the submission.

### Viewer setup

From the repository root, using its committed npm lockfile:

```bash
cd frontend
npm ci
npm run build
npm run dev -- --host 127.0.0.1
```

These are repository-defined commands, not a claim that this infra task tested the
viewer. Current `frontend/public/data/` files are synthetic fixtures. They can
illustrate UI behavior but cannot support a real-data demo or reported metrics.
The frontend owner publishes real `ai/out/audits.jsonl` and
`ai/out/eval_summary.json` into the viewer after evaluation.

## Data and evaluation

Planned real source: public GitHub PR timelines, comments, reviews, linked issues,
and diffs collected by Lio. The contract's sample path is
`backend/data/sample/stale_closures_sample.jsonl`; it is now available on the backend branch (see `infra/gold_set.csv` for the pinned
commit). The 42 Jest PRs supplied 30 agent-assisted reviews pending human confirmation. `shared/fixtures/` is explicitly FAKE, including example
repository names and results. Do not copy those rows into the gold set.

The inference input must exclude `outcome`, `evidence`, post-close events, and
future diff matches. Later reopening or a near-identical merge within 180 days is
an **inferred** wrongful-closure label, not proof of maintainer intent. Diff
similarity is used only for outcome labeling, never as a predictor. `no_evidence`
does not mean closure was justified, especially with incomplete follow-up.

Emmanuel reviews all 30 real PRs; Nilesh independently double-checks 5 selected PRs
using `infra/gold_set.csv` and `infra/labeling.md`. Report reviewer agreement only
on those 5, with its actual denominator. Hand judgments of closure justification are distinct from
future-event labels; retain disagreements and ambiguous cases.

Report wrongful-closure recall, UNSUPPORTED precision, escalation rate, and rejected
claim counts against the stale-bot and metadata baselines. Compare approaches on
the same eligible records or explicitly disclose different denominators. Give n,
repository list, collection date, exclusions, missing data, and observation-window
coverage. Leave undefined metrics null rather than claiming zero.

## Evaluation results

Source: `ai/out/eval_summary.json` at `dev/ai` commit `d7218c4c341d6f0191e1d41e509bbdf3da59cf30`
(generated `2026-10-25T23:46:48.247427+00:00`), plus `infra/gold_summary.md`.
The evaluation source was not yet merged into main when this draft was updated;
recheck against the merged file before publication. `gold_set` is currently null,
so no Close Call-versus-human gold score is available yet.

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
Open-Source AI; Best Use of Gemma 4 eligibility needs clarification. Evaluation counts are reported above; model-versus-human gold scoring,
recorded video, and Devpost submission remain pending.
