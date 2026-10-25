"""Add a weak_label column to out/historical_prs.csv from closing-comment text.

Rules (first match wins):
  "duplicate of #"                          -> duplicate
  "superseded by" / "replaced by"           -> superseded
  "fixed in" / "already merged" / "implemented in" -> already_implemented
  merged                                    -> still_valuable
  otherwise                                 -> unlabeled

Comment text comes from a `closing_comment` column if present, else from
out/closed_comments.jsonl (written by fetch_live.py --closed), else the title only.

Usage: python backend/data/label.py
"""
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

OUT_DIR = Path(__file__).parent / "out"
CSV_PATH = OUT_DIR / "historical_prs.csv"
COMMENTS_PATH = OUT_DIR / "closed_comments.jsonl"

RULES = [
    ("duplicate", re.compile(r"duplicate of\s*#", re.I)),
    ("superseded", re.compile(r"superseded by|replaced by", re.I)),
    ("already_implemented", re.compile(r"fixed in|already merged|implemented in", re.I)),
]


def weak_label(text, merged):
    for label, pattern in RULES:
        if pattern.search(text):
            return label
    if str(merged).strip().lower() in ("true", "1", "yes"):
        return "still_valuable"
    return "unlabeled"


def load_comments():
    if not COMMENTS_PATH.exists():
        return {}
    with open(COMMENTS_PATH, encoding="utf-8") as fh:
        rows = (json.loads(line) for line in fh if line.strip())
        return {(r["repo"], str(r["pr_number"])): "\n".join(r["comments"]) for r in rows}


def main():
    if not CSV_PATH.exists():
        print(f"{CSV_PATH} not found; run fetch_zenodo.py or fetch_live.py --closed first", file=sys.stderr)
        return 1
    comments = load_comments()
    with open(CSV_PATH, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fields = [f for f in reader.fieldnames if f != "weak_label"] + ["weak_label"]
        rows = list(reader)
    counts = Counter()
    for row in rows:
        text = row.get("closing_comment") or comments.get((row["repo"], row["pr_number"]), "")
        row["weak_label"] = weak_label(f"{row.get('title', '')}\n{text}" if text else row.get("title", ""),
                                       row.get("merged", ""))
        counts[row["weak_label"]] += 1
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"Labeled {len(rows)} rows in {CSV_PATH}")
    for label, n in counts.most_common():
        print(f"  {label}: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
