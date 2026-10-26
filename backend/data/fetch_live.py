"""Pull PRs from GitHub with `gh api graphql`.

Default: open PRs created more than 180 days ago -> out/live_stale_prs.jsonl
Fallback (--closed N): N closed PRs per repo set -> out/historical_prs.csv (+ out/closed_comments.jsonl)

Usage: python backend/data/fetch_live.py [--repos a/b c/d] [--days 180] [--max 500]
       python backend/data/fetch_live.py --closed 1000
"""
import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUT_DIR = Path(__file__).parent / "out"
REPOS = ["pallets/flask", "psf/requests", "encode/httpx"]
PAGE = 100

QUERY = """
query($q: String!, $cursor: String) {
  search(query: $q, type: ISSUE, first: %d, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes { ... on PullRequest {
      number url title body state merged createdAt updatedAt closedAt mergedAt
      author { login }
      additions deletions changedFiles
      files(first: 100) { nodes { path } }
      reviewThreads { totalCount }
      comments(last: 20) { nodes { author { login } createdAt body } }
    } }
  }
}
""" % PAGE

HISTORICAL_COLUMNS = ["repo", "pr_number", "title", "author", "created_at", "closed_at", "state",
                      "merged", "abandoned_label", "lines_added", "lines_deleted", "files_changed",
                      "review_comments"]


def run_graphql(query, **variables):
    """Run a GraphQL query through `gh api graphql`; returns the `data` object."""
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        if v is not None:  # -F sends ints as GraphQL Int; -f keeps strings as-is
            cmd += ["-F" if isinstance(v, int) else "-f", f"{k}={v}"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(res.stdout.strip() or res.stderr.strip())
    data = json.loads(res.stdout)
    if "errors" in data:
        raise RuntimeError(json.dumps(data["errors"]))
    return data["data"]


def gql(q, cursor):
    return run_graphql(QUERY, q=q, cursor=cursor)["search"]


def search(q, limit):
    """Yield up to `limit` PR nodes, 100 per query."""
    cursor, n = None, 0
    while n < limit:
        page = gql(q, cursor)
        for node in page["nodes"]:
            if node:
                yield node
                n += 1
                if n >= limit:
                    return
        if not page["pageInfo"]["hasNextPage"]:
            return
        cursor = page["pageInfo"]["endCursor"]


def author(node):
    return (node.get("author") or {}).get("login") or ""


def live(args):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=args.days)).strftime("%Y-%m-%d")
    path = OUT_DIR / "live_stale_prs.jsonl"
    total = 0
    with open(path, "w", encoding="utf-8") as out:
        for repo in args.repos:
            q = f"repo:{repo} is:pr is:open created:<{cutoff} sort:created-asc"
            n = 0
            for node in search(q, args.max):
                node["repo"] = repo
                node["author"] = author(node)
                node["files"] = [f["path"] for f in node["files"]["nodes"]]
                node["comments"] = [
                    {"author": author(c), "created_at": c["createdAt"], "body": c["body"]}
                    for c in node["comments"]["nodes"]
                ]
                out.write(json.dumps(node) + "\n")
                n += 1
            print(f"{repo}: {n} open PRs older than {args.days} days")
            total += n
    print(f"Wrote {total} rows to {path}")
    return total


def closed(args):
    """Fallback: closed PRs from the same repos in the historical schema."""
    per_repo = max(1, args.closed // len(args.repos))
    csv_path = OUT_DIR / "historical_prs.csv"
    comments_path = OUT_DIR / "closed_comments.jsonl"
    total = 0
    with open(csv_path, "w", newline="", encoding="utf-8") as fh, \
            open(comments_path, "w", encoding="utf-8") as cf:
        w = csv.DictWriter(fh, fieldnames=HISTORICAL_COLUMNS)
        w.writeheader()
        for repo in args.repos:
            n = 0
            for node in search(f"repo:{repo} is:pr is:closed sort:created-desc", per_repo):
                w.writerow({
                    "repo": repo, "pr_number": node["number"], "title": node["title"],
                    "author": author(node), "created_at": node["createdAt"],
                    "closed_at": node["closedAt"] or "", "state": node["state"].lower(),
                    "merged": node["merged"], "abandoned_label": "",
                    "lines_added": node["additions"], "lines_deleted": node["deletions"],
                    "files_changed": node["changedFiles"],
                    "review_comments": node["reviewThreads"]["totalCount"],
                })
                cf.write(json.dumps({"repo": repo, "pr_number": node["number"],
                                     "comments": [c["body"] for c in node["comments"]["nodes"]]}) + "\n")
                n += 1
            print(f"{repo}: {n} closed PRs")
            total += n
    print(f"Wrote {total} rows to {csv_path}")
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", nargs="+", default=REPOS)
    ap.add_argument("--days", type=int, default=180)
    ap.add_argument("--max", type=int, default=500, help="max open PRs per repo")
    ap.add_argument("--closed", type=int, metavar="N", help="fallback: fetch N closed PRs total instead")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        closed(args) if args.closed else live(args)
    except (RuntimeError, FileNotFoundError) as e:
        print(f"fetch failed: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
