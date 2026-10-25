import type { AuditResult, EvalSummary, StaleClosure } from '../types'

// Files live in public/data/. At 5:15 the fixtures are swapped for the real ai/out/ files.
const BASE = `${import.meta.env.BASE_URL}data/`

async function fetchText(name: string): Promise<string> {
  const res = await fetch(BASE + name)
  if (!res.ok) throw new Error(`Failed to load ${name}: HTTP ${res.status}`)
  return res.text()
}

export function parseJsonl<T>(text: string): T[] {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .map((line, i) => {
      try {
        return JSON.parse(line) as T
      } catch {
        throw new Error(`Bad JSON on line ${i + 1}`)
      }
    })
}

export async function loadAudits(): Promise<AuditResult[]> {
  return parseJsonl<AuditResult>(await fetchText('audits.jsonl'))
}

export async function loadEvalSummary(): Promise<EvalSummary> {
  return JSON.parse(await fetchText('eval_summary.json')) as EvalSummary
}

// Optional: PR title/author/closed_at for PRCard. If the file is missing, cards show "Unavailable".
export async function loadStaleClosures(): Promise<StaleClosure[]> {
  try {
    return parseJsonl<StaleClosure>(await fetchText('stale_closures.jsonl'))
  } catch {
    return []
  }
}
