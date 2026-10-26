# Close Call

**Before a stale bot closes someone's pull request, check whether closing it is justified.**

Close Call is an agent skill that audits stale-bot pull request closures. Gemma 4 reads
what was visible when the bot closed the PR and writes claims that quote specific
comments, reviews and issues. A plain-Python verifier checks every claim against the
PR data, and the verdict uses only the claims that pass. It advises a maintainer and
never closes, reopens or comments on anything.

Built at UCSD Hacktoberfest Hack Day 2026 for the MLH Open-Source AI challenge and
Best Use of Gemma 4.

## Why

Stale bots close pull requests after a period of inactivity, whether or not the project
still wanted the work. Volunteer work gets thrown away, and contributors are
discouraged from coming back. Nobody checks the bot's reasoning, so we built something
that does.

## How it works

1. **Collect:** `backend/data/fetch_stale_closures.py` (many PRs) or
   `backend/data/fetch_pr.py` (one PR) rebuilds the PR as it was at `closed_at`:
   comments, reviews and linked issues from before the close only.
2. **Claim:** Gemma 4 (`ai/closecall/run.py`) returns JSON claims, each citing a source
   by ID and quoting it, plus reasons not to close.
3. **Verify:** `backend/verifier/verify.py` checks that each cited item exists, that its
   author matches, that it predates the close, and that the quote appears in it. Failed
   claims are dropped.
4. **Decide:** using verified claims only, the verdict is
   - `CONFIRMED`: closing was justified (the author abandoned it, or a maintainer rejected it)
   - `UNSUPPORTED`: the work was still wanted (maintainer interest, an approval, an open linked issue)
   - `ESCALATE`: security-related, conflicting signals, or not enough evidence, so a human decides

Close Call checks quotes, not meaning: a verified quote proves the source exists, not
that the model read it correctly. That's why the safe default is `ESCALATE`.

## Results (jestjs/jest, small sample)

Of **25** stale-bot closures old enough to judge, **5 (20%)** were wrongful: a
near-identical change was merged later anyway.

| Approach | Wrongful closures let through (of 5) | Sent to a human |
|---|---|---|
| Stale bot (today's practice) | **5** | 0% |
| Metadata heuristic | **5** | 0% |
| Close Call: Gemma 4 26B via Gemini API (`gemma-4-26b-a4b-it`) | **0** | 88% |
| Close Call: Gemma 4 E2B, local via Ollama (`gemma4:e2b`) | **0** | 88% |

- **Close Call approved none of the wrongful closures**, and it sent all 5 to a human. It
  is conservative: most closures in this data had no human decision at all.
- **The verifier matters.** Across all 42 audits, it rejected 21 of 148 citations from the
  local E2B model and 0 of 101 from Gemma 4 26B. A rejection is a failed citation check,
  not necessarily an invented claim.
- **Human answer key:** 24 PRs labeled by three team members, judging only what was visible
  at close time. On the 7 PRs humans judged confidently, Close Call escalated all 7 and
  never contradicted them. Its only 2 confident verdicts were on PRs humans rated
  uncertain. Most of its 15/24 agreement is shared uncertainty, so we don't present it as
  accuracy.

Full numbers: `ai/out/eval_summary.json`. Per-PR audits: `ai/out/audits_gemini.jsonl`
and `ai/out/audits_ollama.jsonl`. Labels: `infra/gold_set.csv`.

## Quick start

Requirements: Python 3, the GitHub CLI (`gh auth login`), and either a Gemini API key
or [Ollama](https://ollama.com). Node.js is needed for the viewer.

```bash
# Audit one PR live (needs gh, and GEMINI_API_KEY in ai/.env, which is gitignored)
python3 backend/data/fetch_pr.py jestjs/jest 15880 > /tmp/pr.jsonl
python3 ai/closecall/run.py /tmp/pr.jsonl --backend gemini

# Or fully local
ollama pull gemma4:e2b
python3 ai/closecall/run.py /tmp/pr.jsonl --backend ollama --model gemma4:e2b

# Tests
python3 backend/verifier/test_verify.py
python3 backend/eval/test_baselines.py
python3 -m unittest ai.closecall.test_backends ai.closecall.test_verdict ai.eval.test_score

# Viewer (static site that reads frontend/public/data/)
cd frontend && npm ci && npm run dev
```

More detail: `ai/skill/close-call/SKILL.md` (the agent skill), `backend/README.md`,
`frontend/README.md`, and `infra/README_draft.md` (the full write-up).

## Data and limitations

Our dataset comes from a single repository, jestjs/jest: 42 pull requests closed by its stale bot (github-actions) between October 2024 and October 2026, of which 5 were later redone in a near-identical merged PR and 0 were reopened. We also scanned 1,000 closed home-assistant/core PRs, but only one looked like a stale-bot closure, and on inspection it was the author closing their own PR, so we dropped that repo and tightened the detector to require the bot's own wording and to never count self-closes. Outcome labels are inferred from later events, not confirmed by maintainers, and a closure only counts as 'redone later' if a merged PR touched at least half the same files with at least 40% of the same added lines. 17 of the 42 closures happened less than 180 days ago, so their redo window isn't complete; they're excluded from the headline wrongful-closure rate. With 5 wrongful cases, every result here is a small-sample result.

Our answer key is 24 PRs labeled by three team members. Lio's 9 AI-assisted labels are
excluded, and only Emmanuel had seen AI-suggested labels before labeling. Human-human
agreement was measured on just 2 PRs (1 agreed), which is too few to interpret.

## License

Code: MIT (see `LICENSE`). Gemma 4 is published by Google under Apache 2.0; check the model
card of the exact model you download. The MIT license does not cover model weights or
third-party GitHub content.

## Team

Allen Long (frontend), Lio (data collection, verifier, baselines), Nilesh Behera (Gemma
runner, evaluation, skill), Emmanuel (docs, gold labels, demo, submission).
