from __future__ import annotations

import json
import unittest
from pathlib import Path

ROUTER_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = ROUTER_ROOT.parents[1]
LOCK_PATH = ROUTER_ROOT / "upstream.lock.json"


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


if __name__ == "__main__":
    unittest.main()
