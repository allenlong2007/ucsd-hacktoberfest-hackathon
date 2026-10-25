import type { AuditResult } from '../types'
import { VerdictBadge } from './VerdictBadge'

export interface PRCardProps extends Pick<AuditResult, 'repo' | 'pr_number' | 'verdict' | '_fixture'> {
  /** Join these fields from stale_closure by repo + pr_number; audits omit them. */
  title: string | null
  author: string | null
  closed_at: string | null
  summary?: string
  /** Optional app detail URL supplied by the caller. Defaults to the GitHub PR. */
  href?: string
}

export function PRCard({ repo, pr_number, title, author, closed_at, verdict, summary, href, _fixture }: PRCardProps) {
  const date = closed_at ? new Date(closed_at) : null
  const validDate = date !== null && Number.isFinite(date.getTime())
  const githubUrl = `https://github.com/${repo.split('/').map(encodeURIComponent).join('/')}/pull/${pr_number}`

  return (
    <article className="cc-pr-card">
      {_fixture && <p className="cc-fixture">SAMPLE DATA · fake fixture</p>}
      <div className="cc-pr-card-top">
        <a className="cc-pr-link" href={href ?? githubUrl}>{repo}#{pr_number}</a>
        <VerdictBadge verdict={verdict} />
      </div>
      <h3 className="cc-pr-title">{title || 'Title unavailable'}</h3>
      {summary && <p className="cc-pr-summary">{summary}</p>}
      <dl className="cc-pr-meta">
        <div><dt>Author</dt><dd>{author ? `@${author}` : 'Unavailable'}</dd></div>
        <div>
          <dt>Closed (UTC)</dt>
          <dd>{validDate ? <time dateTime={closed_at!}>{new Intl.DateTimeFormat('en-US', { dateStyle: 'medium', timeStyle: 'short', timeZone: 'UTC' }).format(date)}</time> : 'Unavailable'}</dd>
        </div>
      </dl>
    </article>
  )
}
