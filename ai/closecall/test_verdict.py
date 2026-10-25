import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from run import verdict


FIXTURE = Path(__file__).parents[2] / "shared" / "fixtures" / "stale_closures_sample.jsonl"


def load_pr(number):
    with FIXTURE.open() as source:
        records = [json.loads(line) for line in source if line.strip()]
    return next(record for record in records if record["pr_number"] == number)


def claim(kind, ref, supports, **extra):
    return {"type": kind, "ref": ref, "author": extra.pop("author", "someone"),
            "quote": "real source quote", "supports": supports, "verified": True, **extra}


class VerdictTests(unittest.TestCase):
    def test_member_keep_open_is_unsupported_from_pr_source(self):
        self.assertEqual(verdict(load_pr(101), [claim("comment", "IC_1", "keep_open")]), "UNSUPPORTED")

    def test_approved_review_is_unsupported(self):
        self.assertEqual(verdict(load_pr(101), [claim("review", "R_1", "keep_open")]), "UNSUPPORTED")

    def test_open_linked_issue_is_unsupported(self):
        self.assertEqual(verdict(load_pr(101), [claim("issue", "99", "keep_open")]), "UNSUPPORTED")

    def test_author_abandonment_is_confirmed(self):
        self.assertEqual(verdict(load_pr(102), [claim("comment", "IC_2", "close", author="alice")]), "CONFIRMED")

    def test_maintainer_rejection_is_confirmed(self):
        pr = load_pr(102)
        pr["comments"][0]["author_association"] = "MEMBER"
        self.assertEqual(verdict(pr, [claim("comment", "IC_2", "close", author="bob")]), "CONFIRMED")

    def test_security_title_or_path_escalates(self):
        for field in ("title", "files"):
            pr = copy.deepcopy(load_pr(101))
            if field == "title":
                pr["title"] = "Fix auth bypass"
            else:
                pr["files"][0]["path"] = "src/csrf_middleware.py"
            self.assertEqual(verdict(pr, []), "ESCALATE")

    def test_model_cannot_spoof_source_metadata(self):
        spoofed = claim("comment", "IC_2", "keep_open", author_association="MEMBER")
        self.assertEqual(verdict(load_pr(102), [spoofed]), "ESCALATE")

    def test_unverified_claim_is_ignored(self):
        self.assertEqual(verdict(load_pr(101), [dict(claim("comment", "IC_1", "keep_open"), verified=False)]), "ESCALATE")


if __name__ == "__main__":
    unittest.main()
