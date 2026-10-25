# Real Jest PR comparison

`audits_gemini.jsonl` is the main hosted Gemma 4 result;
`audits_ollama.jsonl` is the local Gemma E2B comparison.
`backend_summary.json` reports both backends on exactly the same 42 PRs.

Data and verifier were read from `origin/dev/backend` at commit
`5fd6519db6925ffeeb8802e2e8c4548419693cf7`, without changing or committing backend files.
The dataset has 5 `redone_later` labels and 37 `no_evidence` labels. The source
dataset SHA-256 is included in the summary. Labels are excluded from model input.
Every committed audit must record `verifier: real` and retains rejected claims.

Both models receive the same prompt and use the same verifier and verdict rules.
Hosted Gemini initially used four concurrent audits, then reduced to two after
rate limiting, with two-second start spacing;
local Ollama runs are sequential. Latencies include model loading/retries/backoff
but exclude scheduling, earlier failed audit attempts, and between-audit delay. The model sizes, generation
defaults, hardware, and concurrency differ, so this is not a controlled speed
benchmark. Ollama temperature is 0; hosted Gemma uses service defaults.

`redone_later` is an inferred label, not proof that closure was wrongful.
`no_evidence` does not prove closure was correct. `ESCALATE` means human review;
only `UNSUPPORTED` is an affirmative finding that closure lacks support. Counts
of rejected claims are citation-check failures, not necessarily fabrications.
This run has no independently hand-checked gold labels.

Any `fixture_*.jsonl` files in a working checkout are fake demonstration outputs,
are excluded from this comparison, and are not part of these real-data results.
