import { Bar, BarChart, CartesianGrid, LabelList, ResponsiveContainer, XAxis, YAxis } from 'recharts'
import { HeadlineStat, ResultsChart } from '../components'
import { modelName } from '../modelNames'
import type { Approach, EvalSummary, GoldSet, Verdict } from '../types'

function pct(x: number | null | undefined): string {
  return x == null ? '—' : `${(x * 100).toFixed(0)}%`
}

// Main comparison: how many of the wrongful closures each approach would let close. Lower is better.
function LetThrough({ approaches, wrongful }: { approaches: Approach[]; wrongful: number }) {
  const rows = approaches.filter((a) => a.wrongful_closed != null)
  if (rows.length === 0) return null
  const data = rows.map((a) => ({ name: a.name, closed: a.wrongful_closed!, label: `${a.wrongful_closed} of ${wrongful}` }))
  const height = Math.max(200, rows.length * 64)

  return (
    <section className="let-through">
      <h2>Wrongful closures let through</h2>
      <p className="muted">
        Out of the {wrongful} closures labeled wrongful (inferred). Lower is better: every one of these is wanted work
        that gets closed.
      </p>
      <div className="chart" role="img" aria-label={data.map((d) => `${d.name}: ${d.label} let through`).join('; ')}>
        <ResponsiveContainer width="100%" height={height}>
          <BarChart data={data} layout="vertical" margin={{ top: 4, right: 72, bottom: 4, left: 8 }}>
            <CartesianGrid horizontal={false} stroke="var(--cc-border, #ddd)" />
            <XAxis type="number" domain={[0, Math.max(wrongful, 1)]} ticks={wrongful <= 10 ? Array.from({ length: wrongful + 1 }, (_, i) => i) : undefined} allowDecimals={false} tick={{ fill: 'var(--cc-muted, #666)' }} />
            <YAxis type="category" dataKey="name" width={190} tick={{ fill: 'var(--cc-text, #111)', fontSize: 14 }} />
            <Bar dataKey="closed" fill="var(--cc-unsupported, #b91c1c)" isAnimationActive={false}>
              <LabelList dataKey="label" position="right" fill="var(--cc-text, #111)" />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Approach</th>
              <th>Let through</th>
              <th>Wrongful sent to a human</th>
              <th>All PRs sent to a human</th>
              <th>n</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((a) => (
              <tr key={a.name}>
                <td>{a.name}</td>
                <td>
                  {a.wrongful_closed} of {wrongful}
                </td>
                <td>{a.wrongful_escalated == null ? '—' : `${a.wrongful_escalated} of ${wrongful}`}</td>
                <td>{pct(a.escalation_rate)}</td>
                <td>{a.n}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="muted">"Sent to a human" means ESCALATE: Close Call advises a person to review, it never closes or reopens anything.</p>
    </section>
  )
}

function FactChecker({ summary, auditCount }: { summary: EvalSummary; auditCount: number }) {
  const models = summary.approaches.filter((a) => a.model && a.claims_total != null)
  const { hallucination } = summary
  if (models.length === 0 && !hallucination) return null

  return (
    <section className="fact-checker">
      <h2>Fact-checker</h2>
      <p className="muted">Every claim the model writes is checked against the PR's real comments, reviews and issues. Claims that don't match are thrown out before the verdict.</p>
      <div className="fact-grid">
        {models.map((a) => (
          <div className="fact-item" key={a.name}>
            <div className="fact-model">{modelName(a.model!)}</div>
            <div className="fact-number">
              {a.claims_rejected ?? 0} <span>of {a.claims_total}</span>
            </div>
            <div>invented claims caught</div>
            {a.avg_latency_s != null && <div className="muted">avg {a.avg_latency_s.toFixed(1)} s per PR</div>}
          </div>
        ))}
      </div>
      {models.length === 0 && hallucination && (
        <p>
          The verifier rejected <strong>{hallucination.claims_rejected}</strong> of {hallucination.claims_total} claims
          (n={hallucination.claims_total}).
        </p>
      )}
      <p className="muted">
        A rejected claim is one whose quote, author or date didn't match the PR data. That's a failed citation, not
        always a fabrication. Claim counts and latency cover every audited PR (n={auditCount}), including newer closures
        left out of the comparison above. Latencies come from different hardware and settings, so they aren't a controlled
        speed test.
      </p>
    </section>
  )
}

const HUMAN_LABELS = ['NOT_JUSTIFIED', 'JUSTIFIED', 'UNCERTAIN']
const HUMAN_LABEL_TEXT: Record<string, string> = {
  NOT_JUSTIFIED: 'Closing not justified',
  JUSTIFIED: 'Closing justified',
  UNCERTAIN: 'Uncertain',
}
const VERDICT_COLS: Verdict[] = ['UNSUPPORTED', 'CONFIRMED', 'ESCALATE']

// Gold set: shown as a confusion table, not a single accuracy number, because most of
// close_call_agreement comes from both sides being uncertain.
function GoldSetPanel({ gold }: { gold: GoldSet }) {
  const c = gold.confusion
  const confident = c ? ['NOT_JUSTIFIED', 'JUSTIFIED'].map((h) => c[h] ?? {}) : []
  const confidentTotal = confident.reduce((t, row) => t + VERDICT_COLS.reduce((u, v) => u + (row[v] ?? 0), 0), 0)
  const confidentEscalated = confident.reduce((t, row) => t + (row.ESCALATE ?? 0), 0)
  // Contradiction: human says not justified but Close Call CONFIRMED, or justified but UNSUPPORTED.
  const contradictions = c ? (c.NOT_JUSTIFIED?.CONFIRMED ?? 0) + (c.JUSTIFIED?.UNSUPPORTED ?? 0) : 0
  const facts = [
    `${gold.n} PRs`,
    gold.reviewers != null && `${gold.reviewers} human reviewers`,
    gold.excluded_ai_assisted != null && `${gold.excluded_ai_assisted} AI-assisted labels excluded`,
  ].filter(Boolean)

  return (
    <section className="gold-set">
      <h2>Hand-checked gold set</h2>
      <p>{facts.join(', ')}</p>
      {c && (
        <div className="table-wrap">
          <table className="confusion">
            <caption>
              {confidentTotal > 0 && confidentEscalated === confidentTotal && contradictions === 0
                ? `On the ${confidentTotal} PRs humans judged confidently, Close Call escalated all ${confidentTotal} and never contradicted them. Most agreement comes from shared uncertainty.`
                : 'Human label (rows) vs Close Call verdict (columns).'}
            </caption>
            <thead>
              <tr>
                <th scope="col">Human label ↓ / Close Call →</th>
                {VERDICT_COLS.map((v) => (
                  <th scope="col" key={v}>{v}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {HUMAN_LABELS.filter((h) => c[h]).map((h) => (
                <tr key={h}>
                  <th scope="row">{HUMAN_LABEL_TEXT[h]}</th>
                  {VERDICT_COLS.map((v) => (
                    <td key={v}>{c[h][v] ?? 0}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <p className="muted">
        {gold.close_call_agreement && <>Raw agreement with Close Call: {gold.close_call_agreement} (mostly uncertain ↔ ESCALATE). </>}
        {gold.agreement_reviewers && <>Reviewer agreement: {gold.agreement_reviewers}. </>}
        {gold.agreement_with_inferred_labels != null && <>Agreement with inferred labels: {pct(gold.agreement_with_inferred_labels)}.</>}
      </p>
    </section>
  )
}

export default function ResultsPage({ summary, auditCount }: { summary: EvalSummary; auditCount: number }) {
  const { headline, approaches, gold_set } = summary

  return (
    <section>
      <HeadlineStat headline={headline} _fixture={summary._fixture} />
      {headline.eligible_note && <p className="muted eligible-note">{headline.eligible_note}</p>}

      <p className="note">
        Labels are inferred: a closure counts as wrongful if the PR was later reopened or a near-identical change was
        merged within 180 days. The model never sees these labels.
      </p>

      <LetThrough approaches={approaches} wrongful={headline.wrongful} />

      <FactChecker summary={summary} auditCount={auditCount} />

      <details className="more-metrics">
        <summary>More metrics: recall and precision of UNSUPPORTED</summary>
        <ResultsChart approaches={approaches} _fixture={summary._fixture} />
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Approach</th>
                <th>n</th>
                <th>Wrongful closures caught (UNSUPPORTED)</th>
                <th>Recall</th>
                <th>Precision</th>
                <th>Escalation rate</th>
              </tr>
            </thead>
            <tbody>
              {approaches.map((a) => (
                <tr key={a.name}>
                  <td>{a.name}</td>
                  <td>{a.n}</td>
                  <td>{a.wrongful_caught}</td>
                  <td>{pct(a.recall)}</td>
                  <td>{pct(a.precision)}</td>
                  <td>{pct(a.escalation_rate)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>

      {gold_set && <GoldSetPanel gold={gold_set} />}

      {summary.notes.length > 0 && (
        <ul className="muted">
          {summary.notes.map((n, i) => (
            <li key={i}>{n}</li>
          ))}
        </ul>
      )}
      <p className="muted">Generated: {summary.generated_at}</p>
    </section>
  )
}
