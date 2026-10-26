# rePRieve frontend

A static site with two pages:

- **Audit** (`#/audit`): every audited stale-bot closure with its verdict (CONFIRMED, UNSUPPORTED or ESCALATE). Click one to see its verified and rejected claims and its reasons not to close.
- **Results** (`#/results`): the headline wrongful-closure rate, wrongful closures let through by each approach, the fact-checker stats per model, and the hand-checked gold set.

```sh
cd frontend && npm ci && npm run dev   # local dev server
npm run build                          # production build in dist/
```

There's no backend server. The app reads static files from `public/data/`:

| File | Copied from |
|---|---|
| `audits.jsonl` | `ai/out/audits_gemini.jsonl` |
| `eval_summary.json` | `ai/out/eval_summary.json` |
| `stale_closures.jsonl` | `backend/data/sample/stale_closures_sample.jsonl` |

A SAMPLE DATA banner appears if any record has `"_fixture": true`.

Owned by `dev/frontend` (allenlong2007), except `src/components/` and `src/styles/` (`dev/frontend-ui`). See ../OWNERSHIP.md.
