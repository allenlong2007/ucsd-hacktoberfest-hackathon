// Mirrors shared/CONTRACT.md. Change that file first (shared-files PR) before changing these.

export type Verdict = 'CONFIRMED' | 'UNSUPPORTED' | 'ESCALATE'
export type Outcome = 'reopened' | 'redone_later' | 'no_evidence'

export interface Claim {
  type: 'comment' | 'review' | 'issue' | 'activity'
  ref: string
  author: string
  quote: string
  supports: 'keep_open' | 'close'
  verified: boolean
  check: string
}

export interface AuditResult {
  _fixture?: boolean
  repo: string
  pr_number: number
  verdict: Verdict
  summary: string
  claims: Claim[]
  reasons_not_to_close: string[]
  claims_total: number
  claims_rejected: number
  model: string
  latency_s: number
  outcome?: Outcome
}

export interface Approach {
  name: string
  n: number
  wrongful_caught: number
  recall: number | null
  precision: number | null
  escalation_rate: number | null
}

export interface EvalSummary {
  _fixture?: boolean
  generated_at: string
  headline: {
    repos: string[]
    stale_closures: number
    wrongful: number
    wrongful_rate: number
  }
  approaches: Approach[]
  hallucination: { claims_total: number; claims_rejected: number }
  gold_set?: { n: number; agreement_with_inferred_labels: number }
  notes: string[]
}

// Only the stale_closure fields the UI shows (PRCard metadata). The full shape is in CONTRACT.md.
export interface StaleClosure {
  _fixture?: boolean
  repo: string
  pr_number: number
  title: string
  author: string
  created_at: string
  closed_at: string
}
