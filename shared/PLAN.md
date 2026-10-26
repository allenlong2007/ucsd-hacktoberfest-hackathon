# rePRieve: build plan (3:00 PM to 6:30 PM)

**One line:** before a stale bot closes someone's pull request, rePRieve checks whether
closing it is actually justified, using evidence that is verified against the PR's real data.

## The core task (read this first)

Input: a PR that a stale bot closed, using **only what was visible at the moment it closed**
(the diff, comments, reviews and linked issues up to `closed_at`).

rePRieve outputs one verdict:
- `CONFIRMED`: closing was justified (the author abandoned it, it was superseded, or the
  maintainers rejected it), with verified evidence.
- `UNSUPPORTED`: there is evidence the work was still wanted (a maintainer asked for it, an
  approving review, an open linked issue, the author was still active), so it should be
  reviewed, not closed.
- `ESCALATE`: security-related, conflicting signals, or not enough evidence. A human decides.

How it works:
1. Gemma 4 (local, Ollama) reads the PR and writes **claims**, each quoting a source:
   "maintainer @x commented 'we want this' on 2024-03-02".
2. The **verifier** (plain Python, no AI) checks every claim against the fetched PR data: does
   the comment, review or issue exist, with that author, date and quoted text? Failed claims
   are dropped and counted as hallucinations.
3. The verdict is computed from the verified claims only. If unsure, the answer is ESCALATE.

**Ground truth comes from the future**, which the model never sees. A stale closure counts
as WRONGFUL if the PR was later reopened, or if a near-identical change was merged within
180 days (`redone_later`). That makes this an honest prediction task: can we tell at close
time which closures will turn out wrong?

> Watch out for circularity: `redone_later` labels are built from diff similarity, so never
> use diff similarity *as a predictor*. The baselines below only use information from before
> the close.

## Evaluation (the data science story)

| Approach | What it uses |
|---|---|
| Stale bot (today's practice) | closes everything, so it misses every wrongful closure |
| Metadata heuristic | flags as wanted if there was an approving review, a maintainer comment, or author activity in the last 30 days |
| Gemma 4 + verifier (rePRieve) | verified claims |

Metrics, on all labeled closures plus a 30-PR hand-checked gold set:
- **Wrongful closures caught** (recall on wrongful)
- **Precision** of UNSUPPORTED
- **Escalation rate**
- **Hallucinated claims caught**: claims written, claims that failed verification
- Headline: **% of stale-bot closures that were wrongful**, shown with n and the repo list

Report sample sizes. Call the labels "inferred". No claims beyond the data.

## Timeline

| Time | Lio (backend) | Nilesh (ai) | Allen, frontend agent 1 | Allen, frontend agent 2 | Emmanuel (infra) |
|---|---|---|---|---|---|
| 3:00–3:10 | pull `main`, read this file and `shared/CONTRACT.md` | same | same | same | same |
| 3:10–4:00 | `fetch_stale_closures.py` (local Claude Code, Opus). Second agent: `backend/verifier/` | Ollama + Gemma 4 E4B running; claim prompt working on `shared/fixtures/` | app shell, 2 pages (Audit, Results) on fixtures | VerdictBadge, ClaimList, PRCard, ResultsChart, HeadlineStat | README draft, Devpost draft, **ask organizers whether local Gemma counts for Best Use of Gemma 4** |
| **4:00** | **CHECKPOINT 1:** sample data pushed with counts. If fewer than 15 wrongful closures, add repos or use the fallback | Gemma returns valid claims JSON | pages render fixtures | components done | gold-set labeling sheet ready |
| 4:00–5:15 | verifier finished and tested; `backend/eval/baselines.py` | run rePRieve on 60–100 PRs → `ai/out/audits.jsonl`; metrics → `ai/out/eval_summary.json` | swap fixtures for real files | polish, dark mode, mobile | hand-label 30 gold PRs with Nilesh; record a draft demo video |
| **5:15** | **CHECKPOINT 2:** real numbers exist. Freeze scope | | | | |
| 5:15–5:45 | everyone opens a PR into `main`, Allen merges. `ai/skill/reprieve/SKILL.md` is final | | | | |
| **5:45** | **CODE FREEZE.** Only bug fixes after this | | | | |
| 5:45–6:15 | rehearse the 3-minute demo, final video, Devpost submitted **by 6:15** | | | | |
| 6:15–6:30 | buffer. Don't start anything new | | | | |

## Cut (don't build)
Fine-tuning, Zenodo, the rescue/cherry-pick code, live scans of many repos, posting to
GitHub, running PR code, and a separate skeptic pass (fold it into the prompt as
`reasons_not_to_close`).

## Fallback (decide at 4:00)
If the data pull fails: use 30–40 stale closures from one repo, label them by hand, and run
the same evaluation. Smaller, but still honest.

## Demo script (3 minutes)
1. Problem plus headline number (30 s)
2. Live audit of 3 PRs: CONFIRMED, UNSUPPORTED (shows a hallucinated claim being rejected),
   ESCALATE (60 s)
3. Results table: stale bot vs heuristic vs rePRieve (45 s)
4. Install it as a skill: one command, local Gemma, Apache 2.0 (30 s)
5. Limits: inferred labels, small n, it advises and never acts (15 s)
