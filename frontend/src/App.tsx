import { useEffect, useState } from 'react'
import { loadAudits, loadEvalSummary, loadStaleClosures } from './api/data'
import type { AuditResult, EvalSummary, StaleClosure } from './types'
import AuditPage from './pages/AuditPage'
import ResultsPage from './pages/ResultsPage'

// Hash routing (#/audit, #/results, #/audit/owner/name/123) so static hosting needs no server config.
function useHashRoute(): string {
  const [hash, setHash] = useState(() => window.location.hash.slice(1) || '/audit')
  useEffect(() => {
    const onChange = () => setHash(window.location.hash.slice(1) || '/audit')
    window.addEventListener('hashchange', onChange)
    return () => window.removeEventListener('hashchange', onChange)
  }, [])
  return hash
}

export default function App() {
  const route = useHashRoute()
  const [audits, setAudits] = useState<AuditResult[] | null>(null)
  const [summary, setSummary] = useState<EvalSummary | null>(null)
  const [closures, setClosures] = useState<StaleClosure[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([loadAudits(), loadEvalSummary(), loadStaleClosures()])
      .then(([a, s, c]) => {
        setAudits(a)
        setSummary(s)
        setClosures(c)
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)))
  }, [])

  const isSample = Boolean(summary?._fixture || audits?.some((a) => a._fixture))
  const onResults = route.startsWith('/results')

  return (
    <div className="app">
      {isSample && (
        <div className="sample-banner" role="alert">
          SAMPLE DATA: these are fake fixtures for building the UI, not real results.
        </div>
      )}
      <header className="app-header">
        <a className="brand" href="#/audit">
          rePRieve
        </a>
        <span className="tagline">Is closing this stale PR actually justified?</span>
        <nav>
          <a href="#/audit" className={onResults ? '' : 'active'}>
            Audit
          </a>
          <a href="#/results" className={onResults ? 'active' : ''}>
            Results
          </a>
        </nav>
      </header>
      <main>
        {error && <p className="error">Could not load data: {error}</p>}
        {!error && (!audits || !summary) && <p>Loading…</p>}
        {audits && summary && (onResults ? <ResultsPage summary={summary} auditCount={audits.length} /> : <AuditPage audits={audits} closures={closures} route={route} />)}
      </main>
    </div>
  )
}
