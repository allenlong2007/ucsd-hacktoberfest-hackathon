import copy
import unittest

from ai.eval.score import ROOT, approach, build_summary, eligible_records, gold_agreement, read_jsonl, validate_summary


class ScoreTests(unittest.TestCase):
    def test_gold_uses_three_way_human_agreement_without_outcome_labels(self):
        audits = [{"repo": "jestjs/jest", "pr_number": i, "verdict": verdict}
                  for i, verdict in enumerate(("CONFIRMED", "UNSUPPORTED", "ESCALATE"))]
        gold = {"labels": [{"pr_number": i, "human_label": label}
                           for i, label in enumerate(("JUSTIFIED", "NOT_JUSTIFIED", "UNCERTAIN"))],
                "agreement_reviewers": "4/5"}
        self.assertEqual(gold_agreement(gold, audits),
                         {"n": 3, "close_call_agreement": "3/3", "agreement_reviewers": "4/5"})
        gold["labels"].append(gold["labels"][0])
        with self.assertRaises(ValueError):
            gold_agreement(gold, audits)

    def test_exact_180_day_boundary(self):
        records = [{"closed_at": "2026-04-28T00:00:00Z"},
                   {"closed_at": "2026-04-28T00:00:01Z"}]
        self.assertEqual(eligible_records(records), records[:1])

    def test_escalations_are_not_positive_predictions(self):
        records = [{"repo": "r", "pr_number": i, "outcome": outcome}
                   for i, outcome in enumerate(("redone_later", "reopened", "no_evidence"))]
        row = approach("test", records, {("r", 0): "ESCALATE", ("r", 1): "UNSUPPORTED",
                                         ("r", 2): "UNSUPPORTED"})
        self.assertEqual(row["wrongful_caught"], 1)
        self.assertEqual(row["wrongful_escalated"], 1)
        self.assertEqual(row["wrongful_closed"], 0)
        self.assertEqual(row["recall"], 0.5)
        self.assertEqual(row["precision"], 0.5)
        self.assertEqual(row["escalation_rate"], 1 / 3)

    def test_precision_undefined_when_nothing_is_flagged(self):
        records = [{"repo": "r", "pr_number": 1, "outcome": "redone_later"}]
        row = approach("test", records, {("r", 1): "CONFIRMED"})
        self.assertIsNone(row["precision"])
        self.assertEqual(row["wrongful_closed"], 1)

    def test_real_artifacts_keep_eligible_metrics_and_full_run_stats_separate(self):
        records = read_jsonl(ROOT / "backend/data/sample/stale_closures_sample.jsonl")
        gemini = read_jsonl(ROOT / "ai/out/audits_gemini.jsonl")
        ollama = read_jsonl(ROOT / "ai/out/audits_ollama.jsonl")
        result = build_summary(records, gemini, ollama)
        validate_summary(result)
        self.assertEqual(result["headline"]["stale_closures"], 25)
        self.assertEqual(result["headline"]["wrongful"], 5)
        self.assertEqual(result["headline"]["wrongful_rate"], 0.2)
        self.assertEqual([r["n"] for r in result["approaches"]], [25] * 4)
        self.assertEqual(result["hallucination"], {"claims_total": 101, "claims_rejected": 0})
        self.assertIsNone(result["gold_set"])
        for row in result["approaches"][2:]:
            self.assertEqual(row["wrongful_closed"], 0)
            self.assertEqual(row["wrongful_escalated"], 5)
            self.assertEqual(row["wrongful_caught"], 0)
            self.assertEqual(row["escalation_rate"], 0.88)
        self.assertEqual(result["approaches"][2]["claims_total"], 101)
        self.assertEqual(result["approaches"][3]["claims_total"], 148)
        bad = copy.deepcopy(result)
        bad["approaches"][2]["n"] = 42
        with self.assertRaises(ValueError):
            validate_summary(bad)


if __name__ == "__main__":
    unittest.main()
