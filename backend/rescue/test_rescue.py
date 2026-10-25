"""Tests for rescue.py against a throwaway git repo. Run: python backend/rescue/test_rescue.py"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rescue import git, rescue  # noqa: E402

ENV_ID = ["-c", "user.name=Maintainer", "-c", "user.email=maint@example.com"]


def commit(repo, name, email, msg, files):
    for path, text in files.items():
        (Path(repo) / path).write_text(text)
    git(repo, "add", "-A")
    subprocess.run(["git", "-C", repo, *ENV_ID, "commit", "-q", "-m", msg,
                    f"--author={name} <{email}>"], check=True)


def make_repo(tmp):
    repo = str(Path(tmp) / "practice")
    subprocess.run(["git", "init", "-q", "-b", "main", repo], check=True)
    commit(repo, "Maintainer", "maint@example.com", "init", {"a.txt": "a\n", "t.sh": "exit 0\n"})
    git(repo, "checkout", "-q", "-b", "stale-pr")
    commit(repo, "Alice Contributor", "alice@example.com", "add b", {"b.txt": "b\n"})
    commit(repo, "Alice Contributor", "alice@example.com", "add c", {"c.txt": "c\n"})
    git(repo, "checkout", "-q", "main")
    commit(repo, "Maintainer", "maint@example.com", "main moves on", {"a.txt": "a2\n"})
    return repo


class RescueTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = make_repo(self.tmp.name)
        git(self.repo, "config", "user.name", "Rescuer")
        git(self.repo, "config", "user.email", "rescue@example.com")

    def tearDown(self):
        self.tmp.cleanup()

    def test_applies_keeps_author_and_runs_tests(self):
        r = rescue(self.repo, "main", "stale-pr", "rescue/1", test_cmd="sh t.sh")
        self.assertEqual(r["status"], "applied")
        self.assertTrue(r["tests_passed"])
        log = git(self.repo, "log", "main..rescue/1", "--format=%an|%cn").stdout.splitlines()
        self.assertEqual(log, ["Alice Contributor|Rescuer"] * 2)
        self.assertTrue((Path(self.repo) / "c.txt").exists())

    def test_failing_tests_reported(self):
        r = rescue(self.repo, "main", "stale-pr", "rescue/2", test_cmd="exit 1")
        self.assertEqual(r["status"], "tests_failed")
        self.assertFalse(r["tests_passed"])

    def test_conflict_leaves_clean_branch(self):
        git(self.repo, "checkout", "-q", "stale-pr")
        commit(self.repo, "Alice Contributor", "alice@example.com", "edit a", {"a.txt": "a-alice\n"})
        git(self.repo, "checkout", "-q", "main")
        r = rescue(self.repo, "main", "stale-pr", "rescue/3")
        self.assertEqual(r["status"], "conflict")
        self.assertEqual(len(r["applied"]), 2)
        self.assertEqual(git(self.repo, "status", "--porcelain").stdout, "")

    def test_nothing_to_rescue(self):
        r = rescue(self.repo, "main", "main", "rescue/4")
        self.assertEqual(r["status"], "nothing_to_rescue")


if __name__ == "__main__":
    unittest.main()
