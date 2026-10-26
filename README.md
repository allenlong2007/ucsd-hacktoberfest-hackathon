# rePRieve

**Before a stale bot closes someone's pull request, check whether closing it is justified.**

rePRieve is an agent skill that audits stale-bot pull request closures. Gemma 4 reads
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

rePRieve checks quotes, not meaning: a verified quote proves the source exists, not
that the model read it correctly. That's why the safe default is `ESCALATE`.

## Results (jestjs/jest, small sample)

Of **25** stale-bot closures old enough to judge, **5 (20%)** were wrongful: a
near-identical change was merged later anyway.

| Approach | Wrongful closures let through (of 5) | Sent to a human |
|---|---|---|
| Stale bot (today's practice) | **5** | 0% |
| Metadata heuristic | **5** | 0% |
| rePRieve: Gemma 4 26B via Gemini API (`gemma-4-26b-a4b-it`) | **0** | 88% |
| rePRieve: Gemma 4 E2B, local via Ollama (`gemma4:e2b`) | **0** | 88% |

- **rePRieve approved none of the wrongful closures**, and it sent all 5 to a human. It
  is conservative: most closures in this data had no human decision at all.
- **The verifier matters.** Across all 42 audits, it rejected 21 of 148 citations from the
  local E2B model and 0 of 101 from Gemma 4 26B. A rejection is a failed citation check,
  not necessarily an invented claim.
- **Human answer key:** 24 PRs labeled by three team members, judging only what was visible
  at close time. On the 7 PRs humans judged confidently, rePRieve escalated all 7 and
  never contradicted them. Its only 2 confident verdicts were on PRs humans rated
  uncertain. Most of its 15/24 agreement is shared uncertainty, so we don't present it as
  accuracy.

Full numbers: `ai/out/eval_summary.json`. Per-PR audits: `ai/out/audits_gemini.jsonl`
and `ai/out/audits_ollama.jsonl`. Labels: `infra/gold_set.csv`.

## Quick start

### 1. Get the code

```bash
git clone https://github.com/allenlong2007/ucsd-hacktoberfest-hackathon.git
cd ucsd-hacktoberfest-hackathon
```

Run everything below from this folder.

### 2. See the results (2 minutes, no API key)

```bash
cd frontend && npm ci && npm run dev
```

Open **http://localhost:5173/#/results** for the comparison chart, or
**http://localhost:5173/#/audit** for all 42 audited PRs. Press `Ctrl+C` to stop, then `cd ..`.

### 3. Audit a real pull request (5 minutes)

**Set up once:**

```bash
gh auth login                  # GitHub CLI, so rePRieve can read PRs
cp ai/.env.example ai/.env     # then paste a free key from https://aistudio.google.com/apikey after GEMINI_API_KEY=
```

**Run it:**

```bash
python3 backend/data/fetch_pr.py jestjs/jest 15880 > /tmp/pr.jsonl
python3 ai/closecall/run.py /tmp/pr.jsonl --backend gemini --output /tmp/audit.jsonl
cat /tmp/audit.jsonl
```

You should see `"verdict": "ESCALATE"` with 3 verified claims: the author asked for review,
nobody from the project answered, and the bot closed it anyway. To audit a different PR,
replace `jestjs/jest 15880` with any `OWNER/REPO NUMBER`.

> **No Gemini key?** Run Gemma 4 locally instead: install [Ollama](https://ollama.com), run
> `ollama pull gemma4:e2b`, then use
> `--backend ollama --model gemma4:e2b` in the second command.
>
> **Certificate error on a Mac?** Run `export SSL_CERT_FILE=/etc/ssl/cert.pem` first.

### 4. Use it as an agent skill

Open your coding agent (Claude Code, Codex, Cursor and so on) **in this folder** and ask:

> Read `ai/skill/reprieve/SKILL.md` and use it to audit jestjs/jest#15880.

or, for a whole repository:

> Read `ai/skill/reprieve/SKILL.md`, collect the stale-bot closures in jestjs/jest with
> `--max 200`, audit them, and tell me which ones look wrongly closed.

The agent runs the same commands and explains the verdicts. Point it at the skill file as
shown; the skill isn't installed globally.

### Repos to try

| Repo | Why | |
|---|---|---|
| `jestjs/jest` | Our evaluation repo, so results are known. Try PR **15880** (ESCALATE) or **15228** (UNSUPPORTED) | ✅ tested |
| `apache/spark` | Very large project that closes inactive PRs with a stale workflow | untested |
| `kubernetes/kubernetes` | Closes inactive PRs through its triage bot (`lifecycle/rotten`) | untested |
| `pytorch/pytorch` | Runs a stale-PR workflow | untested |

For a whole repo, collect first (a few minutes), then audit:

```bash
python3 backend/data/fetch_stale_closures.py --repos apache/spark --max 200 --no-extra
python3 ai/closecall/run.py backend/data/out/stale_closures.jsonl --backend gemini --workers 2 --resume --output /tmp/audits.jsonl
```

The first command prints how many stale-bot closures it found. **If it says 0, that repo
doesn't use a stale bot we recognize**, so try another. Each audit takes about a minute.

### Run the tests (optional, no API key)

```bash
python3 backend/verifier/test_verify.py && python3 backend/eval/test_baselines.py && python3 -m unittest ai.closecall.test_backends ai.closecall.test_verdict ai.eval.test_score
```

More detail: `ai/skill/reprieve/SKILL.md` (the agent skill), `backend/README.md`,
`frontend/README.md`, and `infra/README_draft.md` (the full write-up).

## Data and limitations

Our dataset comes from a single repository, jestjs/jest: 42 pull requests closed by its
stale bot (github-actions) between October 2024 and October 2026, of which 5 were later
redone in a near-identical merged PR and 0 were reopened. We also scanned 1,000 closed
home-assistant/core PRs, but only one looked like a stale-bot closure, and on
inspection it was the author closing their own PR, so we dropped that repo and tightened
the detector to require the bot's own wording and to never count self-closes. Outcome
labels are inferred from later events, not confirmed by maintainers, and a closure only
counts as "redone later" if a merged PR touched at least half the same files with at
least 40% of the same added lines. 17 of the 42 closures happened less than 180 days
ago, so their redo window isn't complete; they're excluded from the headline
wrongful-closure rate. With 5 wrongful cases, every result here is a small-sample result.

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
