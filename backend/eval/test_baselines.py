"""Run: python backend/eval/test_baselines.py"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from baselines import heuristic, metrics  # noqa: E402

PR = {"author": "alice", "close_actor": "github-actions", "closed_at": "2024-04-02T10:00:00Z",
      "comments": [], "reviews": []}


class BaselineTest(unittest.TestCase):
    def test_nothing_means_confirmed(self):
        self.assertEqual(heuristic(PR)[0], "CONFIRMED")

    def test_approving_review(self):
        pr = {**PR, "reviews": [{"state": "APPROVED"}]}
        self.assertEqual(heuristic(pr), ("UNSUPPORTED", ["approving review"]))

    def test_maintainer_comment_but_not_own_or_bot(self):
        c = lambda a, assoc: {"author": a, "author_association": assoc, "created_at": "2024-01-01T00:00:00Z"}
        self.assertEqual(heuristic({**PR, "comments": [c("bob", "MEMBER")]})[0], "UNSUPPORTED")
        self.assertEqual(heuristic({**PR, "comments": [c("alice", "OWNER")]})[0], "CONFIRMED")
        self.assertEqual(heuristic({**PR, "comments": [c("github-actions", "MEMBER")]})[0], "CONFIRMED")

    def test_author_activity_window(self):
        c = lambda t: {"author": "alice", "author_association": "NONE", "created_at": t}
        self.assertEqual(heuristic({**PR, "comments": [c("2024-03-20T00:00:00Z")]})[0], "UNSUPPORTED")
        self.assertEqual(heuristic({**PR, "comments": [c("2024-02-01T00:00:00Z")]})[0], "CONFIRMED")

    def test_ignores_outcome_label(self):
        self.assertEqual(heuristic({**PR, "outcome": "reopened"})[0], "CONFIRMED")

    def test_metrics(self):
        rows = [{"h": "UNSUPPORTED", "outcome": "reopened"}, {"h": "UNSUPPORTED", "outcome": "no_evidence"},
                {"h": "CONFIRMED", "outcome": "redone_later"}]
        m = metrics(rows, "h")
        self.assertEqual((m["wrongful"], m["wrongful_caught"], m["flagged"]), (2, 1, 2))
        self.assertEqual((m["recall"], m["precision"]), (0.5, 0.5))


if __name__ == "__main__":
    unittest.main()
