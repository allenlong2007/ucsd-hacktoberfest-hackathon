import copy
import unittest

from ai.eval.score import ROOT, approach, build_summary, eligible_records, gold_agreement, human_only_key, score_human_only, read_jsonl, validate_summary


class ScoreTests(unittest.TestCase):
    def reviewer_rows(self):
        assigned = {1: 'Allen', 2: 'Emmanuel', 3: 'Lio', 4: 'Nilesh', 5: 'Allen',
                    6: 'Emmanuel', 7: 'Lio', 8: 'Nilesh', 9: 'Allen', 10: 'Emmanuel',
                    11: 'Lio', 12: 'Nilesh', 13: 'Allen', 14: 'Emmanuel', 15: 'Lio',
                    16: 'Nilesh', 17: 'Allen', 18: 'Emmanuel', 19: 'Lio', 20: 'Nilesh',
                    21: 'Allen', 22: 'Emmanuel', 23: 'Lio', 24: 'Nilesh', 25: 'Allen',
                    26: 'Emmanuel', 27: 'Lio', 28: 'Nilesh', 29: 'Allen', 30: 'Emmanuel'}
        rows = [{"slot": str(i), "repo": "jestjs/jest", "pr_number": str(i),
                 "reviewer_1": assigned[i], "label_1": "UNCERTAIN", "reviewer_2": "",
                 "label_2": "", "human_label": "UNCERTAIN"} for i in range(1, 31)]
        rows[2].update(label_1="NOT_JUSTIFIED", reviewer_2="Allen", label_2="UNCERTAIN")
        rows[9].update(reviewer_2="Nilesh", label_2="JUSTIFIED")
        rows[16].update(label_1="JUSTIFIED", reviewer_2="Lio", label_2="UNCERTAIN")
        rows[23].update(reviewer_2="Emmanuel", label_2="UNCERTAIN")
        rows[29].update(reviewer_2="Lio", label_2="JUSTIFIED")
        payload = {"labels": [{"repo": r["repo"], "pr_number": int(r["pr_number"]),
                               "human_label": r["human_label"]} for r in rows]}
        return payload, rows

    def test_human_only_key_drops_ai_only_slots_and_uses_human_overrides(self):
        payload, rows = self.reviewer_rows()
        result = human_only_key(payload, rows)
        labels = {r["pr_number"]: r["human_label"] for r in result["labels"]}
        self.assertEqual(len(labels), 24)
        self.assertEqual(set(range(1,31)) - labels.keys(), {7,11,15,19,23,27})
        self.assertEqual(labels[3], "UNCERTAIN")
        self.assertEqual(labels[17], "JUSTIFIED")
        self.assertEqual(labels[30], "UNCERTAIN")
        self.assertEqual(result["reviewers"], 3)
        self.assertEqual(result["agreement_reviewers"], "1/2 (human-human double labels; too small to interpret)")

    def test_human_only_confusion_counts_all_retained_prs(self):
        payload, rows = self.reviewer_rows()
        audits = [{"repo": "jestjs/jest", "pr_number": i, "verdict": "ESCALATE"} for i in range(1,31)]
        result = score_human_only(payload, rows, audits)
        self.assertEqual(result["close_call_agreement"], "23/24")
        self.assertEqual(result["confusion"]["JUSTIFIED"]["ESCALATE"], 1)
        self.assertEqual(result["confusion"]["UNCERTAIN"]["ESCALATE"], 23)
        self.assertEqual(sum(sum(r.values()) for r in result["confusion"].values()), 24)

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
