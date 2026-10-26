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
  /** "real" when the audit went through backend/verifier. */
  verifier?: string
  outcome?: Outcome
}

export interface Approach {
  name: string
  n: number
  wrongful_caught: number
  recall: number | null
  precision: number | null
  escalation_rate: number | null
  // Optional fields added at 4:45 (see CONTRACT.md).
  /** Wrongful closures this approach would let close. The headline safety metric. */
  wrongful_closed?: number
  /** Wrongful closures sent to a human (ESCALATE). */
  wrongful_escalated?: number
  model?: string
  claims_total?: number
  claims_rejected?: number
  avg_latency_s?: number
}

/** Human label (NOT_JUSTIFIED | JUSTIFIED | UNCERTAIN) -> Close Call verdict -> count. */
export type Confusion = Record<string, Partial<Record<Verdict, number>>>

export interface GoldSet {
  n: number
  agreement_with_inferred_labels?: number
  agreement_reviewers?: string
  close_call_agreement?: string
  reviewers?: number
  excluded_ai_assisted?: number
  confusion?: Confusion
}

export interface EvalSummary {
  _fixture?: boolean
  generated_at: string
  headline: {
    repos: string[]
    stale_closures: number
    wrongful: number
    wrongful_rate: number
    eligible_note?: string
  }
  approaches: Approach[]
  hallucination: { claims_total: number; claims_rejected: number }
  gold_set?: GoldSet | null
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
