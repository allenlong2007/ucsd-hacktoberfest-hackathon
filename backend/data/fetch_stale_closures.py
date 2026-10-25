"""Collect PRs closed by a stale bot, with what was visible at close time plus a later outcome.

Writes out/stale_closures.jsonl (shape: shared/CONTRACT.md section 1) and a sample of up to
200 rows (every wrongful one included) to sample/stale_closures_sample.jsonl.

Usage: python backend/data/fetch_stale_closures.py [--repos home-assistant/core,jestjs/jest] [--max 1500]

--max is the number of PRs scanned per repo (newest first), not the number kept.
A PR is kept if a stale bot closed it (close actor, or close comment text). closed_at is the
time of that close event, so PRs that were reopened afterwards are found too (--states).
outcome: reopened = a ReopenedEvent after the close; redone_later = a PR merged within
180 days after the close touching >= 50% of its files with added-line Jaccard >= 0.4
(patches fetched for the top 3 candidates only); else no_evidence. Closures younger than
180 days can't be fully labeled; their count is reported.
"""
import argparse
import json
import random
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fetch_live import run_graphql  # noqa: E402

DATA = Path(__file__).parent
OUT_PATH = DATA / "out" / "stale_closures.jsonl"
SAMPLE_PATH = DATA / "sample" / "stale_closures_sample.jsonl"

# k8s-ci-robot is left out on purpose: Prow closes a PR as k8s-ci-robot whenever anyone types
# "/close", so its stale closes are caught by the k8s-triage-robot comment text instead.
STALE_ACTORS = {"github-actions", "stale", "k8s-triage-robot"}
STALE_TEXT = re.compile(
    r"closed because it has not had recent activity|has been automatically closed|"
    r"marked as stale|closing this (pr|pull request) (due to|because)[^.]*(inactiv|stale)|"
    r"lifecycle/rotten|no activity", re.I)
WINDOW_DAYS = 180
MIN_OVERLAP, MIN_JACCARD, TOP_K = 0.5, 0.4, 3
MIN_WRONGFUL = 15
EXTRA_REPOS = ["pytorch/pytorch", "kubernetes/kubernetes"]  # stale-bot repos, used if too few wrongful

COMMENT = "id author { login } authorAssociation createdAt body"
PR_QUERY = """
query($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequests(first: 50, after: $cursor, states: [%s], orderBy: {field: CREATED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number title createdAt closedAt author { login }
        files(first: 100) { nodes { path additions deletions } }
        comments(first: 100) { totalCount nodes { %s } }
        tail: comments(last: 5) { nodes { %s } }
        reviews(first: 100) { nodes { id author { login } state submittedAt } }
        closingIssuesReferences(first: 20) { nodes { number state createdAt closedAt } }
        closedEvents: timelineItems(itemTypes: [CLOSED_EVENT], first: 10) {
          nodes { ... on ClosedEvent { createdAt actor { login } } } }
        reopenedEvents: timelineItems(itemTypes: [REOPENED_EVENT], first: 10) {
          nodes { ... on ReopenedEvent { createdAt actor { login } } } }
      }
    }
  }
}
"""
MERGED_QUERY = """
query($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequests(first: 100, after: $cursor, states: [MERGED], orderBy: {field: UPDATED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes { number mergedAt updatedAt files(first: 100) { nodes { path } } }
    }
  }
}
"""


def ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def login(node):
    return ((node or {}).get("author") or (node or {}).get("actor") or {}).get("login") or ""


def paginate(query, repo, limit):
    owner, name = repo.split("/")
    cursor, n = None, 0
    while n < limit:
        page = run_graphql(query, owner=owner, name=name, cursor=cursor)["repository"]["pullRequests"]
        for node in page["nodes"]:
            yield node
            n += 1
            if n >= limit:
                return
        if not page["pageInfo"]["hasNextPage"]:
            return
        cursor = page["pageInfo"]["endCursor"]


def is_stale_close(actor, close_comment):
    return actor in STALE_ACTORS or actor.removesuffix("[bot]") in STALE_ACTORS or \
        bool(STALE_TEXT.search(close_comment or ""))


def find_close_comment(comments, closed_at):
    """The comment nearest the close event (within 10 minutes), bots preferred."""
    near = [c for c in comments if abs((ts(c["created_at"]) - ts(closed_at)).total_seconds()) <= 600]
    near.sort(key=lambda c: (c["author"].removesuffix("[bot]") not in STALE_ACTORS,
                             abs((ts(c["created_at"]) - ts(closed_at)).total_seconds())))
    return near[0] if near else None


def build_record(repo, node):
    """Turn a GraphQL PR node into a stale_closure record (no outcome yet), or None if not stale-closed."""
    all_comments = {}
    for c in node["comments"]["nodes"] + node["tail"]["nodes"]:
        all_comments[c["id"]] = {"id": c["id"], "author": login(c), "author_association": c["authorAssociation"],
                                 "created_at": c["createdAt"], "body": c["body"]}
    comments = sorted(all_comments.values(), key=lambda c: c["created_at"])
    for ev in node["closedEvents"]["nodes"]:
        actor = login(ev)
        cc = find_close_comment(comments, ev["createdAt"])
        if is_stale_close(actor, cc["body"] if cc else ""):
            closed_at, close_actor, close_comment = ev["createdAt"], actor, cc
            break
    else:
        return None
    before = ts(closed_at)
    reopened = [e["createdAt"] for e in node["reopenedEvents"]["nodes"] if ts(e["createdAt"]) > before]
    return {
        "repo": repo, "pr_number": node["number"], "title": node["title"], "author": login(node),
        "created_at": node["createdAt"], "closed_at": closed_at, "close_actor": close_actor,
        "close_comment": close_comment["body"] if close_comment else "",
        "files": [{"path": f["path"], "additions": f["additions"], "deletions": f["deletions"]}
                  for f in node["files"]["nodes"]],
        "comments": [c for c in comments if ts(c["created_at"]) < before],
        "reviews": [{"id": r["id"], "author": login(r), "state": r["state"], "submitted_at": r["submittedAt"]}
                    for r in node["reviews"]["nodes"] if r["submittedAt"] and ts(r["submittedAt"]) < before],
        "linked_issues": [
            {"number": i["number"],
             "state_at_close": "OPEN" if not i["closedAt"] or ts(i["closedAt"]) > before else "CLOSED"}
            for i in node["closingIssuesReferences"]["nodes"] if ts(i["createdAt"]) < before],
        "outcome": "reopened" if reopened else "no_evidence",
        "evidence": {"reopened_at": reopened[0] if reopened else None, "matched_pr": None,
                     "file_overlap": None, "line_jaccard": None},
    }


def file_overlap(a_paths, b_paths):
    """Share of the closed PR's files that the merged PR also touched."""
    a, b = set(a_paths), set(b_paths)
    return len(a & b) / len(a) if a else 0.0


def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 0.0


def added_lines(repo, number):
    res = subprocess.run(
        ["gh", "api", f"repos/{repo}/pulls/{number}/files", "--paginate", "--jq",
         ".[] | (.patch // \"\")"], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or res.stdout.strip())
    return {line[1:].strip() for line in res.stdout.splitlines()
            if line.startswith("+") and not line.startswith("+++") and line[1:].strip()}


def index_merged(repo, oldest_close, limit):
    """Merged PRs (number, mergedAt, paths), newest-updated first, until older than the earliest close."""
    out = []
    for node in paginate(MERGED_QUERY, repo, limit):
        if ts(node["updatedAt"]) < oldest_close:
            break
        out.append({"number": node["number"], "merged_at": ts(node["mergedAt"]),
                    "paths": [f["path"] for f in node["files"]["nodes"]]})
    return out


def label_redone(rec, merged_index, fetch_lines=added_lines):
    """Set outcome=redone_later if a later merged PR is a near-identical change."""
    closed = ts(rec["closed_at"])
    paths = [f["path"] for f in rec["files"]]
    cands = []
    for m in merged_index:
        if m["number"] != rec["pr_number"] and closed < m["merged_at"] <= closed + timedelta(days=WINDOW_DAYS):
            ov = file_overlap(paths, m["paths"])
            if ov >= MIN_OVERLAP:
                cands.append((ov, m["number"]))
    cands.sort(reverse=True)
    if not cands:
        return
    mine = fetch_lines(rec["repo"], rec["pr_number"])
    for ov, number in cands[:TOP_K]:
        jac = jaccard(mine, fetch_lines(rec["repo"], number))
        if jac >= MIN_JACCARD:
            rec["outcome"] = "redone_later"
            rec["evidence"].update(matched_pr=number, file_overlap=round(ov, 3), line_jaccard=round(jac, 3))
            return


def rate_limit_line():
    res = subprocess.run(["gh", "api", "rate_limit", "--jq", ".resources.graphql"], capture_output=True, text=True)
    return (res.stdout or res.stderr).strip()


def report_rate_limit_reset():
    res = subprocess.run(["gh", "api", "rate_limit", "--jq", ".resources.graphql.resetAt // .resources.graphql.reset"],
                         capture_output=True, text=True)
    raw = res.stdout.strip()
    if raw.isdigit():
        raw = datetime.fromtimestamp(int(raw), timezone.utc).isoformat()
    print(f"Rate limit hit. GraphQL limit resets at {raw or 'unknown'}.", file=sys.stderr)


def collect(repo, args, sink):
    """Scan one repo; write records to sink as they're labeled. Returns (kept, scanned)."""
    kept, scanned = [], 0
    try:
        for node in paginate(PR_QUERY % (args.states, COMMENT, COMMENT), repo, args.max):
            scanned += 1
            rec = build_record(repo, node)
            if rec:
                kept.append(rec)
    except RuntimeError:
        for r in kept:  # save what we have; these were NOT checked for redone_later
            sink.write(json.dumps(r) + "\n")
        print(f"WARNING: {repo} scan stopped after {scanned} PRs; its {len(kept)} saved rows "
              f"were not checked for redone_later", file=sys.stderr)
        raise
    print(f"{repo}: scanned {scanned} PRs, {len(kept)} closed by a stale bot")
    need = [r for r in kept if r["outcome"] == "no_evidence"]
    if need:
        oldest = min(ts(r["closed_at"]) for r in need)
        merged = index_merged(repo, oldest, args.merged_max)
        for r in need:
            label_redone(r, merged)
    for r in kept:
        sink.write(json.dumps(r) + "\n")
        sink.flush()
    return kept


def summarize(records):
    by_repo, by_outcome = {}, {}
    for r in records:
        by_repo[r["repo"]] = by_repo.get(r["repo"], 0) + 1
        by_outcome[r["outcome"]] = by_outcome.get(r["outcome"], 0) + 1
    print("Per repo:", json.dumps(by_repo))
    print("Per outcome:", json.dumps(by_outcome))
    wrongful = by_outcome.get("reopened", 0) + by_outcome.get("redone_later", 0)
    young = sum(1 for r in records if datetime.now(timezone.utc) - ts(r["closed_at"]) < timedelta(days=WINDOW_DAYS))
    print(f"Total: {len(records)}  wrongful (reopened + redone_later): {wrongful}  "
          f"closed <{WINDOW_DAYS} days ago (redone_later window incomplete): {young}")
    return wrongful


def write_sample(records, n=200):
    wrongful = [r for r in records if r["outcome"] != "no_evidence"]
    rest = [r for r in records if r["outcome"] == "no_evidence"]
    random.Random(0).shuffle(rest)
    rows = wrongful + rest[:max(0, n - len(wrongful))]
    SAMPLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SAMPLE_PATH.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    print(f"Wrote {len(rows)} rows ({len(wrongful)} wrongful) to {SAMPLE_PATH}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", default="home-assistant/core,jestjs/jest")
    ap.add_argument("--max", type=int, default=1500, help="PRs scanned per repo")
    ap.add_argument("--states", default="CLOSED, OPEN", help="PR states to scan (OPEN finds reopened PRs)")
    ap.add_argument("--merged-max", type=int, default=3000, help="merged PRs indexed per repo")
    ap.add_argument("--extra-repos", default=",".join(EXTRA_REPOS))
    ap.add_argument("--no-extra", action="store_true", help="never add extra repos")
    ap.add_argument("--append", action="store_true",
                    help="keep rows already in out/stale_closures.jsonl (from repos not being re-scanned)")
    args = ap.parse_args()

    print("GraphQL rate limit:", rate_limit_line())
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    records = []
    if args.append and OUT_PATH.exists():
        scanning = {r.strip() for r in args.repos.split(",")}
        with open(OUT_PATH, encoding="utf-8") as fh:
            records = [r for r in map(json.loads, filter(str.strip, fh)) if r["repo"] not in scanning]
        print(f"--append: keeping {len(records)} existing rows from other repos")
    try:
        with open(OUT_PATH, "w", encoding="utf-8") as sink:
            for r in records:
                sink.write(json.dumps(r) + "\n")
            for repo in args.repos.split(","):
                records += collect(repo.strip(), args, sink)
            if not args.no_extra and sum(r["outcome"] != "no_evidence" for r in records) < MIN_WRONGFUL:
                print(f"Fewer than {MIN_WRONGFUL} wrongful; adding {args.extra_repos}")
                for repo in args.extra_repos.split(","):
                    records += collect(repo.strip(), args, sink)
    except RuntimeError as e:
        print(f"fetch stopped: {e}", file=sys.stderr)
        if "rate limit" in str(e).lower():
            report_rate_limit_reset()
        print(f"Saved {len(records)} complete records so far to {OUT_PATH}", file=sys.stderr)
        summarize(records)
        write_sample(records)
        return 1
    summarize(records)
    write_sample(records)
    return 0


if __name__ == "__main__":
    sys.exit(main())
