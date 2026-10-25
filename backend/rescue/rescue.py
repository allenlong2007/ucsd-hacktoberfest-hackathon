"""Rescue a stale PR: replay its commits onto a fresh branch, keep author credit, run tests.

Usage:
  python backend/rescue/rescue.py --repo PATH --base main --head pr-branch \
      --branch rescue/pr-123 [--test-cmd "pytest -q"]

Commits in base..head (merge commits skipped) are cherry-picked in order onto a new
branch cut from --base. Cherry-pick keeps each original author; the rescuer becomes
the committer, and `-x` records the source commit. On conflict the branch is left
clean (cherry-pick aborted) and the failing commit is reported.
Exit code: 0 = applied and tests passed (or no tests), 1 = conflict, 2 = tests failed.
"""
import argparse
import json
import subprocess
import sys


def git(repo, *args, check=True):
    res = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if check and res.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {res.stderr.strip() or res.stdout.strip()}")
    return res


def rescue(repo, base, head, branch, test_cmd=None):
    commits = git(repo, "rev-list", "--reverse", "--no-merges", f"{base}..{head}").stdout.split()
    if not commits:
        return {"status": "nothing_to_rescue", "branch": branch, "applied": []}
    git(repo, "checkout", "-q", "-b", branch, base)
    applied = []
    for sha in commits:
        res = git(repo, "cherry-pick", "-x", sha, check=False)
        if res.returncode != 0:
            git(repo, "cherry-pick", "--abort", check=False)
            return {"status": "conflict", "branch": branch, "applied": applied, "failed_commit": sha,
                    "detail": (res.stderr or res.stdout).strip()}
        applied.append(sha)
    result = {"status": "applied", "branch": branch, "applied": applied}
    if test_cmd:
        t = subprocess.run(test_cmd, shell=True, cwd=repo, capture_output=True, text=True)
        result["tests_passed"] = t.returncode == 0
        result["test_output"] = (t.stdout + t.stderr)[-2000:]
        if t.returncode != 0:
            result["status"] = "tests_failed"
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--base", default="main")
    ap.add_argument("--head", required=True, help="PR head branch or commit")
    ap.add_argument("--branch", required=True, help="name of the new rescue branch")
    ap.add_argument("--test-cmd")
    args = ap.parse_args()
    try:
        result = rescue(args.repo, args.base, args.head, args.branch, args.test_cmd)
    except RuntimeError as e:
        print(json.dumps({"status": "error", "detail": str(e)}))
        return 3
    print(json.dumps(result, indent=2))
    return {"applied": 0, "nothing_to_rescue": 0, "conflict": 1, "tests_failed": 2}[result["status"]]


if __name__ == "__main__":
    sys.exit(main())
