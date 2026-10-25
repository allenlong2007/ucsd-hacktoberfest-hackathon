import { useState } from 'react'
import { ClaimList, PRCard } from '../components'
import type { AuditResult, StaleClosure, Verdict } from '../types'
import { modelName } from '../modelNames'

const VERDICTS: Verdict[] = ['UNSUPPORTED', 'ESCALATE', 'CONFIRMED']

export function auditKey(a: Pick<AuditResult, 'repo' | 'pr_number'>): string {
  return `${a.repo}/${a.pr_number}`
}

function cardProps(audit: AuditResult, closure: StaleClosure | undefined) {
  return {
    repo: audit.repo,
    pr_number: audit.pr_number,
    verdict: audit.verdict,
    summary: audit.summary,
    _fixture: audit._fixture,
    title: closure?.title ?? null,
    author: closure?.author ?? null,
    closed_at: closure?.closed_at ?? null,
  }
}

function AuditDetail({ audit, closure }: { audit: AuditResult; closure: StaleClosure | undefined }) {
  const verified = audit.claims.filter((c) => c.verified)
  const rejected = audit.claims.filter((c) => !c.verified)
  return (
    <article className="detail">
      <a href="#/audit">← All audits</a>
      <PRCard {...cardProps(audit, closure)} />
      <p className="muted">
        {audit.claims_total} claims written, {audit.claims_rejected} rejected by the verifier · {modelName(audit.model)} ·{' '}
        {audit.latency_s.toFixed(1)} s
        {audit.verifier && <> · verifier: {audit.verifier}</>}
        {audit.outcome && <> · inferred outcome: {audit.outcome}</>}
      </p>

      <h3>Verified claims (n={verified.length})</h3>
      <ClaimList claims={verified} emptyMessage="No verified claims." />

      <h3>Rejected claims (n={rejected.length})</h3>
      <p className="muted">Claims whose quote, author or date did not match the PR's real data (a failed citation, not always a fabrication). They are dropped before the verdict.</p>
      <ClaimList claims={rejected} emptyMessage="No rejected claims." />

      <h3>Reasons not to close</h3>
      {audit.reasons_not_to_close.length === 0 ? (
        <p className="muted">None.</p>
      ) : (
        <ul>
          {audit.reasons_not_to_close.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
      )}
    </article>
  )
}

export default function AuditPage({
  audits,
  closures,
  route,
}: {
  audits: AuditResult[]
  closures: StaleClosure[]
  route: string
}) {
  const [filter, setFilter] = useState<Verdict | null>(null)
  const closureByKey = new Map(closures.map((c) => [auditKey(c), c]))
  const selectedKey = route.startsWith('/audit/') ? decodeURIComponent(route.slice('/audit/'.length)) : null
  const selected = selectedKey ? audits.find((a) => auditKey(a) === selectedKey) : undefined

  if (selectedKey && !selected) {
    return (
      <p>
        No audit found for {selectedKey}. <a href="#/audit">Back to all audits</a>
      </p>
    )
  }
  if (selected) return <AuditDetail audit={selected} closure={closureByKey.get(auditKey(selected))} />

  const shown = filter ? audits.filter((a) => a.verdict === filter) : audits
  const count = (v: Verdict) => audits.filter((a) => a.verdict === v).length

  return (
    <section>
      <h2>Audited PRs (n={audits.length})</h2>
      <div className="filters" role="group" aria-label="Filter by verdict">
        <button type="button" aria-pressed={filter === null} onClick={() => setFilter(null)}>
          All {audits.length}
        </button>
        {VERDICTS.map((v) => (
          <button key={v} type="button" aria-pressed={filter === v} onClick={() => setFilter(v)}>
            {v} {count(v)}
          </button>
        ))}
      </div>
      <ul className="pr-list">
        {shown.map((a) => (
          <li key={auditKey(a)}>
            <PRCard {...cardProps(a, closureByKey.get(auditKey(a)))} href={`#/audit/${encodeURIComponent(auditKey(a))}`} />
          </li>
        ))}
      </ul>
    </section>
  )
}
