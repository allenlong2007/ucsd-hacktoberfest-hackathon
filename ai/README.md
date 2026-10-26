# ai

Owned by the `dev/ai` branch. See ../OWNERSHIP.md.
Owner: nileshbehera

## Backends

Ollama is the default. For the locally installed E2B model:

```sh
python3 ai/closecall/run.py shared/fixtures/stale_closures_sample.jsonl --backend ollama --model gemma4:e2b --output ai/out/fixture_ollama.jsonl
```

For the Gemini API, copy `ai/.env.example` to `ai/.env` and enter your AI Studio
key there as `GEMINI_API_KEY=...`. Both root `.env` and `ai/.env` are supported;
exported environment values take precedence. These files are gitignored.

```sh
python3 ai/closecall/run.py --backend gemini --list-models
python3 ai/closecall/run.py shared/fixtures/stale_closures_sample.jsonl --backend gemini --output ai/out/fixture_gemini.jsonl
```

Gemini always queries the model list and selects a returned Gemma 4 model supporting
`generateContent`. Use `--model` to select a particular returned ID. No available
Gemma 4 model produces an explicit error; it never silently substitutes Gemini.
Both backends use the same prompt, parse JSON, and retry once on invalid output.
Ollama retries without constrained JSON when the local runtime returns HTTP 501.
Each audit's `model` field includes the backend and model ID.

Fixture output is demonstration data, not evaluation evidence. A temporary
verifier is allowed only for records explicitly marked `_fixture: true`.
Real inputs fail before inference if the real verifier cannot be imported.

## Real-data runs

Set `PYTHONPATH` to the directory containing Lio's `verify.py` (or merge the backend
verifier into the checkout). Every real audit records `"verifier": "real"`.

```sh
PYTHONPATH=/tmp/cc_verifier python3 ai/closecall/run.py /tmp/jest_sample.jsonl --backend gemini --delay 2 --workers 4 --output ai/out/audits_gemini.jsonl
PYTHONPATH=/tmp/cc_verifier python3 ai/closecall/run.py /tmp/jest_sample.jsonl --backend ollama --model gemma4:e2b --delay 2 --output ai/out/audits_ollama.jsonl
python3 ai/eval/report.py /tmp/jest_sample.jsonl
```

`--delay` defaults to two seconds between audit starts; `--workers` defaults to 1.
Gemini HTTP 429 responses retry up to five times with exponential backoff and
respect a numeric `Retry-After` header. `--resume` preserves completed real audits
for the same backend/model. The report checks complete, unique input coverage.
For Python installations missing a CA bundle, set `SSL_CERT_FILE` to your system
CA file (on this Mac, `/etc/ssl/cert.pem`); keep certificate verification enabled.

## Outcome evaluation

```sh
python3 ai/eval/score.py
```

This writes `ai/out/eval_summary.json` per CONTRACT.md section 4. Verdict metrics
include only closures at least 180 days before 2026-10-25; claims and latency use
all 42 audits. The heuristic is imported from `backend/eval/baselines.py`.

`gold_set` is null until infra's gold JSON and reviewer CSV are available. To use
the infra branch before it merges, without copying its files into `ai/`:

```sh
git fetch origin dev/infra
python3 ai/eval/score.py --gold-ref origin/dev/infra
```

The scorer selects Allen, Emmanuel, and Nilesh's finalized reviewer columns from
`gold_set.csv`, not the previously mixed `human_label` aggregates. It keeps Allen's
label_2 for slot 3, Allen's label_1 for slot 17, and Emmanuel's label_1 for slot 30.
Slots 7, 11, 15, 19, 23, and 27 have only AI-assisted labels and are excluded.
The remaining 24 PRs are compared to Gemini using the three-way contract mapping.
Human-human agreement is recomputed from the two retained double-labeled slots;
it is too small a sample to interpret. Confusion rows are human labels; columns
are Gemini verdicts. No `agent_label` or rationale field is used as ground truth.
Missing or inconsistent slots, unknown labels, and duplicate PRs are rejected.
