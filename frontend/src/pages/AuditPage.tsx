import type { AuditResult, Claim, Verdict } from '../types'

// TODO: replace these placeholders with VerdictBadge, ClaimList and PRCard from
// src/components/ once agent 2's PR (dev/frontend-ui) merges.

const VERDICT_LABEL: Record<Verdict, string> = {
  CONFIRMED: 'Closing justified',
  UNSUPPORTED: 'Should be reviewed, not closed',
  ESCALATE: 'Needs a human',
}

function VerdictBadgePlaceholder({ verdict }: { verdict: Verdict }) {
  return (
    <span className={`verdict verdict-${verdict.toLowerCase()}`} title={VERDICT_LABEL[verdict]}>
      {verdict}
    </span>
  )
}

function ClaimListPlaceholder({ claims, verified }: { claims: Claim[]; verified: boolean }) {
  if (claims.length === 0) return <p className="muted">None.</p>
  return (
    <ul className="claims">
      {claims.map((c, i) => (
        <li key={`${c.ref}-${i}`} className={verified ? 'claim-ok' : 'claim-rejected'}>
          <div>
            <strong>{c.type}</strong> <code>{c.ref}</code> by @{c.author}: “{c.quote}”{' '}
            <span className="muted">(supports {c.supports === 'keep_open' ? 'keeping open' : 'closing'})</span>
          </div>
          <div className="check">{verified ? '✓' : '✗'} {c.check}</div>
        </li>
      ))}
    </ul>
  )
}

export function auditKey(a: AuditResult): string {
  return `${a.repo}/${a.pr_number}`
}

function AuditDetail({ audit }: { audit: AuditResult }) {
  const verified = audit.claims.filter((c) => c.verified)
  const rejected = audit.claims.filter((c) => !c.verified)
  return (
    <article className="detail">
      <a href="#/audit">← All audits</a>
      <h2>
        <a href={`https://github.com/${audit.repo}/pull/${audit.pr_number}`} target="_blank" rel="noreferrer">
          {audit.repo}#{audit.pr_number}
        </a>{' '}
        <VerdictBadgePlaceholder verdict={audit.verdict} />
      </h2>
      <p className="summary">{audit.summary}</p>
      <p className="muted">
        {audit.claims_total} claims written, {audit.claims_rejected} rejected by the verifier · {audit.model} ·{' '}
        {audit.latency_s.toFixed(1)} s
        {audit.outcome && <> · inferred outcome: {audit.outcome}</>}
      </p>

      <h3>Verified claims (n={verified.length})</h3>
      <ClaimListPlaceholder claims={verified} verified />

      <h3>Rejected claims (n={rejected.length})</h3>
      <p className="muted">Claims the model wrote that did not match the PR's real data. They are dropped and counted as hallucinations.</p>
      <ClaimListPlaceholder claims={rejected} verified={false} />

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

export default function AuditPage({ audits, route }: { audits: AuditResult[]; route: string }) {
  const selectedKey = route.startsWith('/audit/') ? decodeURIComponent(route.slice('/audit/'.length)) : null
  const selected = selectedKey ? audits.find((a) => auditKey(a) === selectedKey) : undefined

  if (selectedKey && !selected) {
    return (
      <p>
        No audit found for {selectedKey}. <a href="#/audit">Back to all audits</a>
      </p>
    )
  }
  if (selected) return <AuditDetail audit={selected} />

  return (
    <section>
      <h2>Audited PRs (n={audits.length})</h2>
      <ul className="pr-list">
        {audits.map((a) => (
          <li key={auditKey(a)}>
            <a className="pr-card" href={`#/audit/${encodeURIComponent(auditKey(a))}`}>
              <div className="pr-card-top">
                <span>
                  {a.repo}#{a.pr_number}
                </span>
                <VerdictBadgePlaceholder verdict={a.verdict} />
              </div>
              <p>{a.summary}</p>
              <span className="muted">
                {a.claims_total} claims · {a.claims_rejected} rejected
              </span>
            </a>
          </li>
        ))}
      </ul>
    </section>
  )
}
