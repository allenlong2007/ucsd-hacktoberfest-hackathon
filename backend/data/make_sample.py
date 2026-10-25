"""Write small committed samples (default 200 rows) from the full out/ files.

Usage: python backend/data/make_sample.py [--n 200]
Output: backend/data/sample/historical_prs_sample.csv, live_stale_prs_sample.jsonl
Historical rows are spread across repos and weak labels so consumers see every class.
"""
import argparse
import csv
import random
from collections import defaultdict
from itertools import islice
from pathlib import Path

DATA = Path(__file__).parent
OUT = DATA / "out"
SAMPLE = DATA / "sample"


def sample_historical(n):
    with open(OUT / "historical_prs.csv", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fields = reader.fieldnames
        groups = defaultdict(list)
        for row in reader:
            groups[(row["repo"], row.get("weak_label", ""))].append(row)
    rng = random.Random(0)
    for g in groups.values():
        rng.shuffle(g)
    picked = []
    while len(picked) < n and any(groups.values()):  # round-robin across repo/label groups
        for g in groups.values():
            if g and len(picked) < n:
                picked.append(g.pop())
    with open(SAMPLE / "historical_prs_sample.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(picked)
    return len(picked)


def sample_live(n):
    src = OUT / "live_stale_prs.jsonl"
    if not src.exists():
        return 0
    with open(src, encoding="utf-8") as fh:
        lines = list(islice(fh, n))
    (SAMPLE / "live_stale_prs_sample.jsonl").write_text("".join(lines), encoding="utf-8")
    return len(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    args = ap.parse_args()
    SAMPLE.mkdir(exist_ok=True)
    print(f"historical sample: {sample_historical(args.n)} rows")
    print(f"live sample: {sample_live(min(args.n, 50))} rows")


if __name__ == "__main__":
    main()
