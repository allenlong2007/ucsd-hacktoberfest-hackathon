import type { Verdict } from '../types'

export interface VerdictBadgeProps {
  verdict: Verdict
  className?: string
}

const explanations: Record<Verdict, string> = {
  CONFIRMED: 'Closing justified',
  UNSUPPORTED: 'Closure unsupported by evidence',
  ESCALATE: 'Human review needed',
}

export function VerdictBadge({ verdict, className = '' }: VerdictBadgeProps) {
  return (
    <span
      className={`cc-verdict cc-verdict--${verdict.toLowerCase()} ${className}`}
      title={explanations[verdict]}
      aria-label={`${verdict}: ${explanations[verdict]}`}
    >
      {verdict}
    </span>
  )
}
