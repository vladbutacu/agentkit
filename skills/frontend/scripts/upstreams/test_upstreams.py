from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROUTER_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = ROUTER_ROOT.parents[1]
LOCK_PATH = ROUTER_ROOT / "upstream.lock.json"
SCRIPT = Path(__file__).with_name("upstreams.py")


class LockTest(unittest.TestCase):
    def test_upstreams_are_exactly_pinned_and_acknowledged(self):
        lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        skills = lock["skills"]
        ids = [item["id"] for item in skills]
        self.assertTrue(ids and len(ids) == len(set(ids)))
        notices = (REPO_ROOT / "THIRD-PARTY-NOTICES.md").read_text(encoding="utf-8")
        for item in skills:
            self.assertEqual(len(item["commit"]), 40)
            self.assertTrue(all(c in "0123456789abcdef" for c in item["commit"]))
            self.assertTrue(item["repository"] and item["source_path"])
            self.assertIn(item["repository"], notices)
            self.assertIn(item["commit"], notices)


class CliTest(unittest.TestCase):
    def test_reports_missing_and_unknown_skills(self):
        with tempfile.TemporaryDirectory() as td:
            missing = subprocess.run(
                [sys.executable, str(SCRIPT), "--data-dir", td, "verify"],
                capture_output=True, text=True,
            )
            self.assertEqual(missing.returncode, 1)
            self.assertIn("\tmissing", missing.stdout)
            unknown = subprocess.run(
                [sys.executable, str(SCRIPT), "--data-dir", td, "path", "not-a-skill"],
                capture_output=True, text=True,
            )
            self.assertEqual(unknown.returncode, 2)
            self.assertIn("unknown specialist skill", unknown.stderr)


@unittest.skipUnless(os.name != "nt", "pinned-clone fixture needs POSIX git url rewriting")
class ManagerTest(unittest.TestCase):
    def test_fetches_exact_commit_and_detects_modification(self):
        import upstreams

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            home = tmp / "home"
            home.mkdir()
            source = tmp / "source"
            source.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=source, check=True)
            subprocess.run(["git", "config", "user.email", "frontend-test@example.invalid"],
                           cwd=source, check=True)
            subprocess.run(["git", "config", "user.name", "Frontend Test"], cwd=source, check=True)
            skill_dir = source / "skills/test"
            skill_dir.mkdir(parents=True)
            original = "---\nname: test\ndescription: fixture\n---\n\nExact upstream fixture.\n"
            (skill_dir / "SKILL.md").write_text(original, encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=source, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "fixture"], cwd=source, check=True)
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source,
                                             text=True).strip()

            remote = tmp / "remotes/test/repo.git"
            remote.parent.mkdir(parents=True)
            subprocess.run(["git", "clone", "-q", "--bare", str(source), str(remote)], check=True)

            with mock.patch.dict(os.environ, {"HOME": str(home)}):
                subprocess.run([
                    "git", "config", "--global",
                    f"url.file://{tmp}/remotes/.insteadOf",
                    "https://github.com/",
                ], check=True)
                lock = tmp / "lock.json"
                lock.write_text(json.dumps({"skills": [{
                    "id": "fixture",
                    "repository": "test/repo",
                    "commit": commit,
                    "source_path": "skills/test",
                }]}), encoding="utf-8")
                with mock.patch.object(upstreams, "LOCK_PATH", lock):
                    data = tmp / "data"
                    self.assertEqual(upstreams.verify(data, ["fixture"]), {"fixture": "missing"})
                    paths = upstreams.ensure(data, ["fixture"])
                    self.assertEqual(
                        (paths["fixture"] / "SKILL.md").read_text(encoding="utf-8"), original)
                    checkout = upstreams.repo_dir(data, "test/repo", commit)
                    self.assertEqual(
                        upstreams.run_git(["rev-parse", "HEAD"], cwd=checkout, capture=True),
                        commit)
                    self.assertTrue((checkout / ".fex-verified").is_file())
                    self.assertEqual(upstreams.verify(data, ["fixture"])["fixture"], "ok")
                    (paths["fixture"] / "SKILL.md").write_text(original + "tampered\n",
                                                               encoding="utf-8")
                    self.assertEqual(upstreams.verify(data, ["fixture"])["fixture"], "modified")
                    with self.assertRaises(KeyError):
                        upstreams.ensure(data, ["unknown"])


if __name__ == "__main__":
    unittest.main()
