Owned by frontend agent 2 (dev/frontend-ui)

## Integration

Import named components from `./components` (relative to `src/`). The barrel also
loads `styles/theme.css`; import it after the shell's `App.css` so theme colors win.
Direct component-file imports need a separate `styles/theme.css` import.
All data types reuse `src/types.ts`, which mirrors `shared/CONTRACT.md`.

```tsx
import { ClaimList, HeadlineStat, PRCard, ResultsChart, VerdictBadge } from './components'

<VerdictBadge verdict={audit.verdict} />
<ClaimList claims={audit.claims} />
<HeadlineStat headline={summary.headline} _fixture={summary._fixture} />
<ResultsChart approaches={summary.approaches} _fixture={summary._fixture} />
<PRCard
  {...audit}
  title={closure?.title ?? null}
  author={closure?.author ?? null}
  closed_at={closure?.closed_at ?? null}
  href={detailHref}
/>
```

`PRCard` needs metadata joined from `stale_closure` by `repo` and `pr_number`.
Until that data is available, pass null: the component displays “Unavailable”
instead of inventing metadata. `href` is optional and defaults to the GitHub PR;
the caller supplies any internal detail URL. Dates display in UTC.

`ClaimList` reads each claim's own `verified` flag, including mixed lists. Filter
the array before passing it if the page has separate verified/rejected sections.
It supports an optional `emptyMessage`.

`ResultsChart` compares recall and precision on a fixed 0–100% scale, retaining
sample size per approach. Null or invalid metrics are unavailable, not zero.
The visible data table provides exact values and access without chart interaction.
Recharts is the only chart dependency, already declared by frontend agent 1.

Theme defaults to the OS preference. Set `data-theme="light"` or
`data-theme="dark"` on `<html>` for a manual override. Tokens use the `--cc-`
prefix and component classes use `cc-` to avoid shell CSS collisions.
Pass `_fixture` through from evaluation/audit data to keep fake examples labeled.
