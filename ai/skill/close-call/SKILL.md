# Close Call

Close Call audits whether a stale-bot pull-request closure was supported by the
evidence visible at close time. It advises a maintainer; it never closes, reopens,
comments on, or edits a GitHub pull request.

## Install

1. Install Ollama from <https://ollama.com> (macOS: `brew install ollama`).
2. Start the local server with `ollama serve`.
3. Download the model with `ollama pull gemma4:e4b`.
4. From the repository root, run the audit command below.

## Audit one PR record

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
