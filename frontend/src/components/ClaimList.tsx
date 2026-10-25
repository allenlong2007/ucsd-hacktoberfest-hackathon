import type { Claim } from '../types'

export interface ClaimListProps {
  claims: readonly Claim[]
  emptyMessage?: string
}

export function ClaimList({ claims, emptyMessage = 'No claims to display.' }: ClaimListProps) {
  if (claims.length === 0) return <p className="cc-muted">{emptyMessage}</p>

  return (
    <ul className="cc-claims">
      {claims.map((claim, index) => (
        <li className={`cc-claim cc-claim--${claim.verified ? 'verified' : 'rejected'}`} key={`${claim.type}-${claim.ref}-${index}`}>
          <div className="cc-claim-status">
            <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="22" height="22">
              <path d={claim.verified ? 'm5 12 4 4L19 6' : 'm6 6 12 12M18 6 6 18'} />
            </svg>
            <strong>{claim.verified ? 'Verified claim' : 'hallucinated: rejected by verifier'}</strong>
          </div>
          <p className="cc-claim-quote">
            {claim.verified ? <q>{claim.quote}</q> : <del><q>{claim.quote}</q></del>}
          </p>
          <p className="cc-muted">
            {claim.type} <code>{claim.ref}</code> · @{claim.author} · supports {claim.supports === 'keep_open' ? 'keeping open' : 'closing'}
          </p>
          <p className="cc-claim-check">Verifier: {claim.check}</p>
        </li>
      ))}
    </ul>
  )
}
