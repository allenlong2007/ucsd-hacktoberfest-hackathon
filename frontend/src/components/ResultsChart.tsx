import { useId } from 'react'
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { Approach } from '../types'

export interface ResultsChartProps {
  approaches: readonly Approach[]
  _fixture?: boolean
}

function percent(value: number | null): number | null {
  return value !== null && Number.isFinite(value) && value >= 0 && value <= 1 ? value * 100 : null
}

function label(value: number | null): string {
  const result = percent(value)
  return result === null ? 'Unavailable' : `${Number(result.toFixed(1))}%`
}

export function ResultsChart({ approaches, _fixture }: ResultsChartProps) {
  const captionId = useId()
  const data = approaches.map((approach) => ({
    name: `${approach.name} (n=${approach.n})`,
    Recall: percent(approach.recall),
    Precision: percent(approach.precision),
  }))

  return (
    <figure className="cc-results" aria-labelledby={captionId}>
      <figcaption id={captionId} className="cc-chart-title">Comparing approaches</figcaption>
      {_fixture && <p className="cc-fixture">SAMPLE DATA · fake fixture, not real results</p>}
      {approaches.length === 0 ? <p className="cc-muted">No approach results available.</p> : <>
        <div className="cc-chart-plot" aria-hidden="true">
          <ResponsiveContainer width="100%" height={Math.max(320, approaches.length * 120)}>
            <BarChart data={data} layout="vertical" margin={{ top: 12, right: 48, bottom: 12, left: 0 }} accessibilityLayer={false}>
              <CartesianGrid horizontal={false} stroke="var(--cc-border)" />
              <XAxis type="number" domain={[0, 100]} unit="%" tick={{ fill: 'var(--cc-muted)', fontSize: 16 }} />
              <YAxis type="category" dataKey="name" hide />
              <Tooltip
                formatter={(value: number) => `${Number(value.toFixed(1))}%`}
                contentStyle={{ background: 'var(--cc-surface)', color: 'var(--cc-text)', border: '1px solid var(--cc-border)' }}
                labelStyle={{ color: 'var(--cc-text)' }}
                cursor={{ fill: 'var(--cc-surface-alt)' }}
              />
              <Legend />
              <Bar dataKey="Recall" fill="var(--cc-chart-recall)" isAnimationActive={false} label={{ position: 'right', formatter: (value: number | null) => value == null ? '' : `${Number(value.toFixed(1))}%`, fill: 'var(--cc-text)', fontSize: 16 }} />
              <Bar dataKey="Precision" fill="var(--cc-chart-precision)" isAnimationActive={false} />
            </BarChart>
          </ResponsiveContainer>
          <ol className="cc-chart-labels" style={{ height: Math.max(320, approaches.length * 120) - 72 }}>
            {approaches.map((approach, index) => <li key={`${approach.name}-${index}`}><strong>{approach.name}</strong><span>n={approach.n.toLocaleString('en-US')}</span></li>)}
          </ol>
        </div>
        <div className="cc-table-wrap" tabIndex={0} role="region" aria-label="Approach comparison data">
          <table className="cc-results-table">
            <caption>Exact values for each approach</caption>
            <thead><tr><th scope="col">Approach</th><th scope="col">n</th><th scope="col">Recall</th><th scope="col">Precision</th></tr></thead>
            <tbody>{approaches.map((approach, index) => <tr key={`${approach.name}-${index}`}><th scope="row">{approach.name}</th><td>{approach.n.toLocaleString('en-US')}</td><td>{label(approach.recall)}</td><td>{label(approach.precision)}</td></tr>)}</tbody>
          </table>
        </div>
        <p className="cc-footnote">Recall and precision use inferred labels. Missing metrics have no bar; 0% is a measured zero. Sample sizes may differ between approaches.</p>
      </>}
    </figure>
  )
}
