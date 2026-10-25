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

Fixture output is demonstration data, not evaluation evidence. Until the backend
verifier is available, the existing temporary verifier marks every claim verified;
do not present these audits as validated results.
