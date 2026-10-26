"""Produce the section-4 evaluation summary using mature outcome windows only."""
from __future__ import annotations

import argparse
import csv
import io
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ai.eval.report import read_jsonl, summarize
from backend.eval.baselines import WRONGFUL, heuristic

VERDICTS = {"CONFIRMED", "UNSUPPORTED", "ESCALATE"}
NOTES = ["Labels inferred from later merges of near-identical changes",
         "One repository (jestjs/jest)",
         "rePRieve is conservative: it escalates most closures to a human"]
HUMAN_LABELS = {"UNSUPPORTED": "NOT_JUSTIFIED", "CONFIRMED": "JUSTIFIED", "ESCALATE": "UNCERTAIN"}
GOLD_NOTE = "Answer key excludes 6 AI-assisted labels."
REVIEWERS = {"Allen", "Emmanuel", "Nilesh"}
EXCLUDED_SLOTS = {7, 11, 15, 19, 23, 27}


def human_only_key(payload, rows):
    """Select reviewer labels before looking at any model prediction."""
    source = {(r["repo"], r["pr_number"]): r for r in payload["labels"]}
    if len(rows) != 30 or {int(r["slot"]) for r in rows} != set(range(1, 31)):
        raise ValueError("Expected exactly the assigned 30 gold slots")
    labels, excluded, reviewers, double_labels = [], set(), set(), []
    for row in rows:
        slot = int(row["slot"])
        key = (row["repo"], int(row["pr_number"]))
        if key not in source:
            raise ValueError("CSV PR is missing from gold_labels.json")
        retained = [(row[f"reviewer_{i}"], row[f"label_{i}"])
                    for i in (1, 2) if row[f"reviewer_{i}"] in REVIEWERS]
        if not retained:
            excluded.add(slot)
            continue
        if any(label not in HUMAN_LABELS.values() for _, label in retained):
            raise ValueError("Retained reviewer has an invalid or unfinished label")
        reviewers.update(reviewer for reviewer, _ in retained)
        if len(retained) == 1:
            label = retained[0][1]
        else:
            double_labels.append(retained[0][1] == retained[1][1])
            label = row["human_label"]
            if label not in {value for _, value in retained}:
                raise ValueError("Adjudicated label is unsupported by retained human labels")
        labels.append({"repo": key[0], "pr_number": key[1], "human_label": label})
    if excluded != EXCLUDED_SLOTS or len(labels) != 24 or reviewers != REVIEWERS:
        raise ValueError("Human-only selection does not match the assigned exclusions/reviewers")
    agreement = f"{sum(double_labels)}/{len(double_labels)}"
    if agreement != "1/2":
        raise ValueError("Human-human double-label agreement changed; review the source labels")
    return {"labels": labels, "reviewers": len(reviewers), "excluded_ai_assisted": len(excluded),
            "agreement_reviewers": agreement + " (human-human double labels; too small to interpret)"}


def score_human_only(payload, rows, gemini):
    key = human_only_key(payload, rows)
    result = gold_agreement(key, gemini)
    predictions = {(r["repo"], r["pr_number"]): r["verdict"] for r in gemini}
    confusion = {label: {verdict: 0 for verdict in HUMAN_LABELS} for label in HUMAN_LABELS.values()}
    for row in key["labels"]:
        confusion[row["human_label"]][predictions[(row["repo"], row["pr_number"])]] += 1
    result.update(reviewers=key["reviewers"], excluded_ai_assisted=key["excluded_ai_assisted"], confusion=confusion)
    return result


def gold_agreement(payload, gemini):
    """Score supplied consensus human labels; never generate or infer human labels."""
    labels = payload if isinstance(payload, list) else payload["labels"]
    predictions = {(r["repo"], r["pr_number"]): HUMAN_LABELS[r["verdict"]] for r in gemini}
    seen, matches = set(), 0
    for row in labels:
        key = (row.get("repo", "jestjs/jest"), row["pr_number"])
        if key in seen or key not in predictions or row["human_label"] not in HUMAN_LABELS.values():
            raise ValueError("Gold labels must be unique, final human labels for audited PRs")
        seen.add(key)
        matches += predictions[key] == row["human_label"]
    if not seen:
        raise ValueError("Gold labels file contains no labeled PRs")
    result = {"n": len(seen), "close_call_agreement": f"{matches}/{len(seen)}"}
    if isinstance(payload, dict) and "agreement_reviewers" in payload:
        result["agreement_reviewers"] = payload["agreement_reviewers"]
    return result


def eligible_records(records, as_of="2026-10-25"):
    cutoff = datetime.fromisoformat(as_of).replace(tzinfo=timezone.utc) - timedelta(days=180)
    return [r for r in records
            if datetime.fromisoformat(r["closed_at"].replace("Z", "+00:00")) <= cutoff]


def approach(name, eligible, predictions):
    counts = {verdict: 0 for verdict in VERDICTS}
    wrongful_counts = dict(counts)
    for record in eligible:
        prediction = predictions[(record["repo"], record["pr_number"])]
        if prediction not in VERDICTS:
            raise ValueError(f"Unknown verdict: {prediction}")
        counts[prediction] += 1
        if record["outcome"] in WRONGFUL:
            wrongful_counts[prediction] += 1
    wrongful = sum(wrongful_counts.values())
    caught = wrongful_counts["UNSUPPORTED"]
    return {"name": name, "n": len(eligible),
            "wrongful_closed": wrongful_counts["CONFIRMED"],
            "wrongful_escalated": wrongful_counts["ESCALATE"],
            "wrongful_caught": caught,
            "recall": caught / wrongful if wrongful else None,
            "precision": caught / counts["UNSUPPORTED"] if counts["UNSUPPORTED"] else None,
            "escalation_rate": counts["ESCALATE"] / len(eligible) if eligible else 0.0}


def build_summary(records, gemini, ollama, as_of="2026-10-25"):
    eligible = eligible_records(records, as_of)
    if not eligible:
        raise ValueError("No PRs have a complete 180-day outcome window")
    models = []
    for audits in (gemini, ollama):
        models.append(summarize(records, audits))  # Require full, real-verified coverage.
    wrongful = sum(r["outcome"] in WRONGFUL for r in eligible)
    stale = {(r["repo"], r["pr_number"]): "CONFIRMED" for r in eligible}
    metadata = {(r["repo"], r["pr_number"]): heuristic(
        {key: value for key, value in r.items() if key not in {"outcome", "evidence"}})[0]
        for r in eligible}
    approaches = [approach("Stale bot", eligible, stale),
                  approach("Metadata heuristic", eligible, metadata)]
    for name, audits, stats in zip(
            ("rePRieve: Gemma 4 26B (Gemini API)", "rePRieve: Gemma 4 E2B (local)"),
            (gemini, ollama), models):
        if len(stats["models"]) != 1:
            raise ValueError("Expected exactly one model per backend")
        predictions = {(row["repo"], row["pr_number"]): row["verdict"] for row in audits}
        row = approach(name, eligible, predictions)
        row.update(model=stats["models"][0], claims_total=stats["claims_total"],
                   claims_rejected=stats["claims_rejected"], avg_latency_s=stats["average_latency_s"])
        approaches.append(row)
    return {"generated_at": datetime.now(timezone.utc).isoformat(),
            "headline": {"repos": sorted({r["repo"] for r in eligible}),
                         "stale_closures": len(eligible), "wrongful": wrongful,
                         "wrongful_rate": wrongful / len(eligible),
                         "eligible_note": f"{len(records) - len(eligible)} newer closures excluded: their 180-day window isn't complete"},
            "approaches": approaches,
            "hallucination": {key: models[0][key] for key in ("claims_total", "claims_rejected")},
            "gold_set": None, "notes": list(NOTES)}


def validate_summary(result):
    """Check the fields/types and accounting required by CONTRACT.md section 4."""
    if set(result) != {"generated_at", "headline", "approaches", "hallucination", "gold_set", "notes"}:
        raise ValueError("Invalid top-level eval_summary fields")
    headline = result["headline"]
    if set(headline) != {"repos", "stale_closures", "wrongful", "wrongful_rate", "eligible_note"}:
        raise ValueError("Invalid headline fields")
    if headline["wrongful_rate"] != headline["wrongful"] / headline["stale_closures"]:
        raise ValueError("Headline rate has the wrong denominator")
    for row in result["approaches"]:
        required = {"name", "n", "wrongful_closed", "wrongful_escalated", "wrongful_caught",
                    "recall", "precision", "escalation_rate"}
        if row["name"].startswith("rePRieve:"):
            required |= {"model", "claims_total", "claims_rejected", "avg_latency_s"}
        if set(row) != required or row["n"] != headline["stale_closures"]:
            raise ValueError("Invalid approach fields or eligibility denominator")
        if sum(row[k] for k in ("wrongful_closed", "wrongful_escalated", "wrongful_caught")) != headline["wrongful"]:
            raise ValueError("Wrongful outcomes must partition into closed, caught, or escalated")
        for key in ("recall", "precision", "escalation_rate"):
            if row[key] is not None and not 0 <= row[key] <= 1:
                raise ValueError("Metric must be a rate or null")
    if result["notes"] not in (NOTES, NOTES + [GOLD_NOTE]):
        raise ValueError("Unexpected evaluation notes")
    if result["gold_set"] is not None:
        gold = result["gold_set"]
        if not {"n", "close_call_agreement"} <= gold.keys() or not gold["n"] > 0:
            raise ValueError("Gold agreement requires a nonempty human-labeled sample")
        matches, total = map(int, gold["close_call_agreement"].split("/"))
        if total != gold["n"] or not 0 <= matches <= total:
            raise ValueError("Invalid human/model agreement denominator")
        if "confusion" in gold:
            matrix = gold["confusion"]
            if set(matrix) != set(HUMAN_LABELS.values()) or any(set(row) != set(HUMAN_LABELS) for row in matrix.values()):
                raise ValueError("Confusion rows must be human labels and columns Gemini verdicts")
            cells = [value for row in matrix.values() for value in row.values()]
            if any(type(value) is not int or value < 0 for value in cells) or sum(cells) != total:
                raise ValueError("Confusion counts must sum to the gold denominator")
            if sum(matrix[label][verdict] for verdict, label in HUMAN_LABELS.items()) != matches:
                raise ValueError("Confusion diagonal disagrees with close_call_agreement")
            if gold["n"] != 24 or gold["reviewers"] != 3 or gold["excluded_ai_assisted"] != 6 or GOLD_NOTE not in result["notes"]:
                raise ValueError("Gold provenance or exclusion note is missing")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "backend/data/sample/stale_closures_sample.jsonl")
    parser.add_argument("--gemini", type=Path, default=ROOT / "ai/out/audits_gemini.jsonl")
    parser.add_argument("--ollama", type=Path, default=ROOT / "ai/out/audits_ollama.jsonl")
    parser.add_argument("--output", type=Path, default=ROOT / "ai/out/eval_summary.json")
    parser.add_argument("--as-of", default="2026-10-25")
    parser.add_argument("--gold", type=Path, default=ROOT / "infra/gold_labels.json")
    parser.add_argument("--gold-csv", type=Path, default=ROOT / "infra/gold_set.csv")
    parser.add_argument("--gold-ref", help="Read infra gold JSON/CSV directly from a Git ref without copying files")
    args = parser.parse_args()
    result = build_summary(read_jsonl(args.input), read_jsonl(args.gemini), read_jsonl(args.ollama), args.as_of)
    if args.gold_ref:
        payload = json.loads(subprocess.check_output(
            ["git", "show", f"{args.gold_ref}:infra/gold_labels.json"], cwd=ROOT, text=True))
        csv_text = subprocess.check_output(
            ["git", "show", f"{args.gold_ref}:infra/gold_set.csv"], cwd=ROOT, text=True)
        result["gold_set"] = score_human_only(payload, list(csv.DictReader(io.StringIO(csv_text))), read_jsonl(args.gemini))
        result["notes"].append(GOLD_NOTE)
    elif args.gold.exists():
        if not args.gold_csv.exists():
            raise ValueError("Human-only scoring requires reviewer-specific gold_set.csv")
        result["gold_set"] = score_human_only(json.loads(args.gold.read_text()),
            list(csv.DictReader(io.StringIO(args.gold_csv.read_text()))), read_jsonl(args.gemini))
        result["notes"].append(GOLD_NOTE)
    validate_summary(result)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
