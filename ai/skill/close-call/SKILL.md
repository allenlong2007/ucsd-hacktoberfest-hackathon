---
name: close-call
description: Audit whether a stale GitHub pull request closure is supported by verifiable evidence, using local or hosted Gemma and human escalation.
---

# Close Call

Close Call audits whether a stale-bot pull-request closure was supported by the
evidence visible at close time. It advises a maintainer; it never closes, reopens,
comments on, or edits a GitHub pull request.

## Install

1. Install Ollama from <https://ollama.com> (macOS: `brew install ollama`).
2. Start the local server with `ollama serve`.
3. Download the model with `ollama pull gemma4:e4b`.
4. From the repository root, run the audit command below.

## Live audit from GitHub

Run from the repository root after the backend live fetcher is merged. Install
GitHub CLI and authenticate with `gh auth login`. Set `GEMINI_API_KEY` in the
ignored project `.env` or `ai/.env` file. The Gemini backend discovers an available
Gemma 4 model; the real verifier is required for live records.

```bash
python3 backend/data/fetch_pr.py OWNER/REPO NUMBER > /tmp/pr.jsonl
python3 ai/closecall/run.py /tmp/pr.jsonl --backend gemini
```

Check that fetching succeeded before running inference. For the video example,
replace `OWNER/REPO NUMBER` with `jestjs/jest 15880`. If Lio already supplied
`/tmp/pr.jsonl`, run only the second command. The result is written to
`ai/out/audits.jsonl`; keep live outputs separate from the frozen evaluation files.

## Audit saved PR records

```bash
python3 ai/closecall/run.py backend/data/sample/stale_closures_sample.jsonl \
  --output ai/out/audits.jsonl
```

For a local smoke test before the model or verifier is installed:

```bash
python3 ai/closecall/run.py shared/fixtures/stale_closures_sample.jsonl \
  --stub --output /tmp/closecall-audits.jsonl
```

The runner strips `outcome` and `evidence` before calling Gemma. Gemma returns
evidence-backed claims, and the deterministic verifier checks every reference and
quote before verdict rules use it. If evidence is missing or conflicting, the
safe result is `ESCALATE`.
