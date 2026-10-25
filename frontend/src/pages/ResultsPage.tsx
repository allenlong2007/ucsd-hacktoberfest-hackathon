import { HeadlineStat, ResultsChart } from '../components'
import type { EvalSummary } from '../types'

function pct(x: number | null | undefined): string {
  return x == null ? '—' : `${(x * 100).toFixed(0)}%`
}

export default function ResultsPage({ summary }: { summary: EvalSummary }) {
  const { headline, approaches, hallucination, gold_set } = summary
  const hallucinationRate = hallucination.claims_total > 0 ? hallucination.claims_rejected / hallucination.claims_total : null

  return (
    <section>
      <HeadlineStat headline={headline} _fixture={summary._fixture} />

      <p className="note">
        Labels are inferred: a closure counts as wrongful if the PR was later reopened or a near-identical change was
        merged within 180 days. The model never sees these labels.
      </p>

      <ResultsChart approaches={approaches} _fixture={summary._fixture} />

      {/* ResultsChart's table covers n, recall and precision; this one adds the other plan metrics. */}
      <h3>All metrics</h3>
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
