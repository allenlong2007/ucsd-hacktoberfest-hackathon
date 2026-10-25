"""Summarize paired real-verifier runs, checking coverage before publication."""
import argparse
import collections
import hashlib
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def summarize(records, audits):
    expected = {(r["repo"], r["pr_number"]): r for r in records}
    actual = {(r["repo"], r["pr_number"]): r for r in audits}
    if len(actual) != len(audits) or actual.keys() != expected.keys():
        raise ValueError("Audit IDs must cover the input exactly once")
    if any(r.get("verifier") != "real" for r in audits):
        raise ValueError("Every audit must use the real verifier")
    for key, row in actual.items():
        if row.get("outcome") != expected[key].get("outcome"):
            raise ValueError("Copied outcome does not match source record")
        if row["claims_total"] != len(row["claims"]) or row["claims_rejected"] != sum(
                c.get("verified") is False for c in row["claims"]):
            raise ValueError("Claim counts do not match verifier results")
    redone = [row for key, row in actual.items() if expected[key]["outcome"] == "redone_later"]
    counts = collections.Counter(r["verdict"] for r in audits)
    redone_counts = collections.Counter(r["verdict"] for r in redone)
    return {
        "n": len(audits), "models": sorted({r["model"] for r in audits}),
        "verdict_counts": {key: counts[key] for key in ("CONFIRMED", "UNSUPPORTED", "ESCALATE")},
        "claims_total": sum(r["claims_total"] for r in audits),
        "claims_rejected": sum(r["claims_rejected"] for r in audits),
        "average_latency_s": round(statistics.mean(r["latency_s"] for r in audits), 3),
        "redone_later": {"n": len(redone), "unsupported": redone_counts["UNSUPPORTED"],
                         "escalate": redone_counts["ESCALATE"],
                         "unsupported_or_escalate": redone_counts["UNSUPPORTED"] + redone_counts["ESCALATE"]},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--gemini", type=Path, default=Path("ai/out/audits_gemini.jsonl"))
    parser.add_argument("--ollama", type=Path, default=Path("ai/out/audits_ollama.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("ai/out/backend_summary.json"))
    args = parser.parse_args()
    records = read_jsonl(args.input)
    result = {"generated_at": datetime.now(timezone.utc).isoformat(),
              "dataset_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
              "backends": {name: summarize(records, read_jsonl(path))
                           for name, path in (("gemini", args.gemini), ("ollama", args.ollama))},
              "notes": ["redone_later labels are inferred and are not proof of a wrongful closure.",
                        "ESCALATE means human review, not an affirmative prediction of wrongful closure.",
                        "Latency includes retries/backoff within successful audits; excludes prior failed attempts, scheduling, and between-PR delay.",
                        "Rejected claims measure citation verification failures, not necessarily fabricated content."]}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
