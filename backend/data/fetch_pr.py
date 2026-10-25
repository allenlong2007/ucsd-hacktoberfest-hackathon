"""Fetch ONE PR and print it as a stale_closure record (shared/CONTRACT.md section 1), one JSON line.

Usage: python3 backend/data/fetch_pr.py jestjs/jest 15880 > /tmp/pr.jsonl

For live audits: outcome is null and evidence is {}. Comments, reviews and linked issues are
cut off at the close: the stale-bot close if there was one, otherwise the PR's last close.
If the PR is open, the cutoff is now and close_actor is null.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fetch_live import run_graphql  # noqa: E402
from fetch_stale_closures import (PR_FIELDS, find_close_comment, find_stale_close, login,  # noqa: E402
                                  pr_comments, snapshot)

PR_ONE_QUERY = """
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) { state """ + PR_FIELDS + """ }
  }
}
"""


def fetch_pr(repo, number):
    owner, name = repo.split("/")
    node = run_graphql(PR_ONE_QUERY, owner=owner, name=name, number=number)["repository"]["pullRequest"]
    comments = pr_comments(node)
    if node["state"] == "OPEN":
        close = (datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), None, None)
    else:
        close = find_stale_close(node, comments)
        if not close:  # closed by a person (or merged): use the last close event
            events = node["closedEvents"]["nodes"]
            if events:
                last = events[-1]
                close = (last["createdAt"], login(last), find_close_comment(comments, last["createdAt"]))
            else:
                close = (node["closedAt"], None, None)
    rec = snapshot(repo, node, comments, *close)
    rec["outcome"] = None
    rec["evidence"] = {}
    return rec


def main():
    if len(sys.argv) != 3 or "/" not in sys.argv[1] or not sys.argv[2].isdigit():
        print("usage: python3 backend/data/fetch_pr.py OWNER/REPO NUMBER", file=sys.stderr)
        return 2
    try:
        rec = fetch_pr(sys.argv[1], int(sys.argv[2]))
    except (RuntimeError, TypeError, KeyError) as e:
        print(f"fetch failed: {e}", file=sys.stderr)
        return 1
    print(json.dumps(rec))
    return 0


if __name__ == "__main__":
    sys.exit(main())
