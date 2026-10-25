import type { EvalSummary } from '../types'

export interface HeadlineStatProps {
  headline: EvalSummary['headline']
  /** Pass summary._fixture so synthetic results remain visibly labeled. */
  _fixture?: boolean
}

export function HeadlineStat({ headline, _fixture }: HeadlineStatProps) {
  const { wrongful_rate, wrongful, stale_closures, repos } = headline
  const hasRate = stale_closures > 0 && Number.isFinite(wrongful_rate) && wrongful_rate >= 0 && wrongful_rate <= 1

  return (
    <section className="cc-headline" aria-label="Wrongful stale closures">
      {_fixture && <p className="cc-fixture">SAMPLE DATA · fake fixture, not real results</p>}
      <p className="cc-headline-number">{hasRate ? new Intl.NumberFormat('en-US', { style: 'percent', maximumFractionDigits: 1 }).format(wrongful_rate) : '—'}</p>
      <h2 className="cc-headline-label">of stale-bot closures were wrongful</h2>
      <p>{wrongful.toLocaleString('en-US')} of {stale_closures.toLocaleString('en-US')} closures · n={stale_closures.toLocaleString('en-US')}</p>
      {repos.length > 0 && <p className="cc-muted">Across {repos.length} {repos.length === 1 ? 'repository' : 'repositories'}: {repos.join(', ')}</p>}
      {!hasRate && <p className="cc-muted">Percentage unavailable for this sample.</p>}
      <p className="cc-footnote">Labels inferred from later reopen or merge events; these labels are used for scoring only.</p>
    </section>
  )
}
