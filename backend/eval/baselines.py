"""Baselines from PLAN.md: the stale bot and the metadata heuristic.

Reads a stale_closures JSONL file, writes one prediction per PR
(UNSUPPORTED = flag as still wanted, CONFIRMED = closing is fine) and prints
recall/precision on wrongful closures.

The heuristic only reads information from before the close (comments, reviews, dates).
It never looks at `outcome`, `evidence` or diff similarity; `outcome` is copied into the
output after prediction, for scoring only.

Usage: python backend/eval/baselines.py --input backend/data/out/stale_closures.jsonl \
           [--output backend/eval/out/baselines.jsonl]
"""
import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

MAINTAINER_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR"}
ACTIVE_DAYS = 30
WRONGFUL = {"reopened", "redone_later"}


def ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def heuristic(pr):
    """Return (prediction, reasons). UNSUPPORTED if any 'still wanted' signal exists."""
    closed_at = ts(pr["closed_at"])
    author = pr.get("author")
    reasons = []
    if any(r.get("state") == "APPROVED" for r in pr.get("reviews") or []):
        reasons.append("approving review")
    if any(c.get("author_association") in MAINTAINER_ASSOCIATIONS and c.get("author") != author
           and c.get("author") != pr.get("close_actor") for c in pr.get("comments") or []):
        reasons.append("maintainer comment")
    cutoff = closed_at - timedelta(days=ACTIVE_DAYS)
    if any(c.get("author") == author and cutoff <= ts(c["created_at"]) < closed_at
           for c in pr.get("comments") or []):
        reasons.append(f"author activity in last {ACTIVE_DAYS} days")
    return ("UNSUPPORTED" if reasons else "CONFIRMED"), reasons


def metrics(rows, key):
    flagged = [r for r in rows if r[key] == "UNSUPPORTED"]
    wrongful = [r for r in rows if r["outcome"] in WRONGFUL]
    caught = [r for r in flagged if r["outcome"] in WRONGFUL]
    return {"n": len(rows), "wrongful": len(wrongful), "flagged": len(flagged),
            "wrongful_caught": len(caught),
            "recall": len(caught) / len(wrongful) if wrongful else None,
            "precision": len(caught) / len(flagged) if flagged else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", default=str(Path(__file__).parent / "out" / "baselines.jsonl"))
    args = ap.parse_args()
    with open(args.input, encoding="utf-8") as fh:
        prs = [json.loads(line) for line in fh if line.strip()]
    rows = []
    for pr in prs:
        pred, reasons = heuristic(pr)
        rows.append({"repo": pr["repo"], "pr_number": pr["pr_number"], "stale_bot": "CONFIRMED",
                     "heuristic": pred, "heuristic_reasons": reasons, "outcome": pr.get("outcome")})
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    print(f"Wrote {len(rows)} predictions to {out}")
    for name, key in (("Stale bot", "stale_bot"), ("Metadata heuristic", "heuristic")):
        print(f"{name}: {json.dumps(metrics(rows, key))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
