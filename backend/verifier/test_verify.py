"""Run: python backend/verifier/test_verify.py   (uses shared/fixtures/stale_closures_sample.jsonl)"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from verify import verify_claims  # noqa: E402

FIXTURES = Path(__file__).resolve().parents[2] / "shared" / "fixtures" / "stale_closures_sample.jsonl"


def load():
    with open(FIXTURES, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def claim(**kw):
    base = {"type": "comment", "ref": "IC_1", "author": "bob", "quote": "we want this",
            "supports": "keep_open"}
    return {**base, **kw}


class VerifyTest(unittest.TestCase):
    def setUp(self):
        self.pr = load()[0]  # IC_1 by bob: "Thanks! We want this, just needs a test."

    def one(self, **kw):
        return verify_claims(self.pr, [claim(**kw)])[0]

    def test_real_quote_passes(self):
        r = self.one()
        self.assertTrue(r["verified"])
        self.assertIn("IC_1", r["check"])

    def test_quote_is_case_and_whitespace_insensitive(self):
        self.assertTrue(self.one(quote="WE   want\nthis")["verified"])

    def test_invented_ref_fails(self):
        self.assertFalse(self.one(ref="IC_999")["verified"])

    def test_wrong_author_fails(self):
        self.assertFalse(self.one(author="mallory")["verified"])

    def test_quote_not_in_body_fails(self):
        self.assertFalse(self.one(quote="ship it immediately")["verified"])

    def test_empty_quote_fails(self):
        self.assertFalse(self.one(quote="  ")["verified"])

    def test_timestamp_after_closed_at_fails(self):
        self.pr = {**self.pr, "closed_at": "2024-01-15T00:00:00Z"}  # comment is 2024-02-01
        self.assertFalse(self.one()["verified"])

    def test_review_and_issue_claims(self):
        r = verify_claims(self.pr, [
            claim(type="review", ref="R_1", quote="approved"),
            claim(type="issue", ref="99", author="", quote="open"),
        ])
        self.assertTrue(r[0]["verified"], r[0]["check"])
        self.assertTrue(r[1]["verified"], r[1]["check"])

    def test_activity_resolves_against_comments(self):
        self.assertTrue(self.one(type="activity")["verified"])

    def test_input_not_mutated(self):
        c = claim()
        verify_claims(self.pr, [c])
        self.assertNotIn("verified", c)


if __name__ == "__main__":
    unittest.main()
