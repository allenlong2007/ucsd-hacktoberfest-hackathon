import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { EvalSummary } from '../types'

// TODO: replace the inline headline and chart with HeadlineStat and ResultsChart from
// src/components/ once agent 2's PR (dev/frontend-ui) merges.

function pct(x: number | null | undefined): string {
  return x == null ? '—' : `${(x * 100).toFixed(0)}%`
}

export default function ResultsPage({ summary }: { summary: EvalSummary }) {
  const { headline, approaches, hallucination, gold_set } = summary
  const chartData = approaches.map((a) => ({
    name: `${a.name} (n=${a.n})`,
    Recall: a.recall == null ? null : Math.round(a.recall * 100),
    Precision: a.precision == null ? null : Math.round(a.precision * 100),
  }))
  const hallucinationRate = hallucination.claims_total > 0 ? hallucination.claims_rejected / hallucination.claims_total : null

  return (
    <section>
      <div className="headline">
        <div className="headline-number">{pct(headline.wrongful_rate)}</div>
        <div>
          of stale-bot closures were wrongful: {headline.wrongful} of {headline.stale_closures} (n=
          {headline.stale_closures}) across {headline.repos.length} repo{headline.repos.length === 1 ? '' : 's'}:{' '}
          {headline.repos.join(', ')}
        </div>
      </div>

      <p className="note">
        Labels are inferred: a closure counts as wrongful if the PR was later reopened or a near-identical change was
        merged within 180 days. The model never sees these labels.
      </p>

      <h2>Comparing approaches</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Approach</th>
              <th>n</th>
              <th>Wrongful closures caught</th>
              <th>Recall</th>
              <th>Precision (UNSUPPORTED)</th>
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

      <div className="chart">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis unit="%" domain={[0, 100]} />
            <Tooltip formatter={(v: number) => `${v}%`} />
            <Legend />
            <Bar dataKey="Recall" fill="#2563eb" isAnimationActive={false} />
            <Bar dataKey="Precision" fill="#16a34a" isAnimationActive={false} />
          </BarChart>
        </ResponsiveContainer>
        <p className="muted">Precision is not defined for the stale bot (it never flags anything), so it has no bar.</p>
      </div>

      <h2>Hallucinated claims caught</h2>
      <p>
        The verifier rejected <strong>{hallucination.claims_rejected}</strong> of {hallucination.claims_total} claims
        the model wrote ({pct(hallucinationRate)}, n={hallucination.claims_total}). Rejected claims never count toward a
        verdict.
      </p>

      {gold_set && (
        <p className="muted">
          Hand-checked gold set: n={gold_set.n}, agreement with inferred labels {pct(gold_set.agreement_with_inferred_labels)}.
        </p>
      )}

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
