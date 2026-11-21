import sys
import tempfile
import unittest
from pathlib import Path

import capability


def make_cap(store: Path, name: str, *, status="candidate", side_effects="read-only", tests=None, body="", test_command=""):
    folder = store / name
    folder.mkdir(parents=True)
    extra = f"test-command: {test_command}\n" if test_command else ""
    skill = f"---\nname: {name}\ndescription: Does {name} things for tests\nstatus: {status}\nside-effects: {side_effects}\n{extra}---\n"
    if body:
        skill += body
    (folder / "SKILL.md").write_text(skill)
    if tests is not None:
        (folder / "tests").mkdir()
        assertion = "self.assertTrue(True)" if tests == "pass" else "self.assertTrue(False)"
        (folder / "tests" / f"test_{name.replace('-', '_')}.py").write_text(
            f"import unittest\n\nclass T(unittest.TestCase):\n    def test_it(self):\n        {assertion}\n"
        )
    return folder


class CapabilityTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store = self.root / ".agents" / "skills"
        self.store.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_list_hides_deprecated(self):
        make_cap(self.store, "one")
        make_cap(self.store, "gone", status="deprecated")
        out = self.run_cmd("list")
        self.assertIn("one", out)
        self.assertNotIn("gone", out)
        self.assertIn("gone", self.run_cmd("list --all"))

    def test_find_matches_description_case_insensitively(self):
        make_cap(self.store, "normalize-csv")
        self.assertIn("normalize-csv", self.run_cmd("find NORMALIZE"))
        self.assertNotIn("normalize-csv", self.run_cmd("find kubernetes"))

    def test_inspect_flags_name_mismatch(self):
        folder = make_cap(self.store, "a")
        (folder / "SKILL.md").write_text(
            "---\nname: b\ndescription: x\nstatus: candidate\nside-effects: read-only\n---\n"
        )
        self.assertEqual(capability.main(["--root", str(self.root), "inspect", "a"]), 1)

    def test_folded_description_parses(self):
        folder = make_cap(self.store, "folded")
        (folder / "SKILL.md").write_text(
            "---\nname: folded\ndescription: >-\n  Long description\n  across lines\nstatus: candidate\n---\n"
        )
        cap = capability.load(folder)
        self.assertIn("Long description across lines", cap.description)

    def test_test_without_tests_fails(self):
        make_cap(self.store, "bare")
        self.assertEqual(capability.main(["--root", str(self.root), "test", "bare"]), 1)

    def test_promote_blocks_without_tests(self):
        make_cap(self.store, "bare")
        self.assertEqual(capability.main(["--root", str(self.root), "promote", "bare"]), 1)
        self.assertIn("candidate", (self.store / "bare" / "SKILL.md").read_text())

    def test_promote_blocks_failing_tests(self):
        make_cap(self.store, "broken", tests="fail")
        self.assertEqual(capability.main(["--root", str(self.root), "promote", "broken"]), 1)
        self.assertIn("status: candidate", (self.store / "broken" / "SKILL.md").read_text())

    def test_promote_blocks_secret_looking_material(self):
        folder = make_cap(self.store, "leaky", tests="pass")
        (folder / "notes.txt").write_text("key = AKIAIOSFODNN7EXAMPLE")
        self.assertEqual(capability.main(["--root", str(self.root), "promote", "leaky"]), 1)

    def test_promote_requires_reviewed_for_beyond_repo(self):
        make_cap(self.store, "deploy", side_effects="beyond-repo", tests="pass")
        code = capability.main(["--root", str(self.root), "promote", "deploy"])
        self.assertEqual(code, 1)
        code = capability.main(["--root", str(self.root), "promote", "deploy", "--reviewed"])
        self.assertEqual(code, 0)
        self.assertIn("status: verified", (self.store / "deploy" / "SKILL.md").read_text())

    def test_split_command_keeps_windows_paths(self):
        raw = r"C:\tools\check.bat -c 'import sys; sys.exit(0)'"
        self.assertEqual(
            capability.split_command(raw, windows=True),
            [r"C:\tools\check.bat", "-c", "import sys; sys.exit(0)"],
        )
        self.assertEqual(capability.split_command("a 'b c'"), ["a", "b c"])

    def test_test_command_overrides_unittest(self):
        make_cap(self.store, "shellcap", test_command=f"{sys.executable} -c 'import sys; sys.exit(0)'")
        self.assertEqual(capability.main(["--root", str(self.root), "test", "shellcap"]), 0)
        self.assertEqual(capability.main(["--root", str(self.root), "promote", "shellcap"]), 0)

    def test_failing_test_command_blocks_promotion(self):
        make_cap(self.store, "badcmd", test_command=f"{sys.executable} -c 'import sys; sys.exit(3)'")
        self.assertEqual(capability.main(["--root", str(self.root), "promote", "badcmd"]), 1)
        self.assertIn("status: candidate", (self.store / "badcmd" / "SKILL.md").read_text())

    def test_missing_side_effects_blocks_promotion(self):
        folder = make_cap(self.store, "unclassified", tests="pass")
        (folder / "SKILL.md").write_text(
            "---\nname: unclassified\ndescription: x\nstatus: candidate\n---\n"
        )
        self.assertEqual(capability.main(["--root", str(self.root), "promote", "unclassified"]), 1)

    def test_promote_verifies_green_candidate_once(self):
        make_cap(self.store, "good", tests="pass")
        self.assertEqual(capability.main(["--root", str(self.root), "promote", "good"]), 0)
        skill = (self.store / "good" / "SKILL.md").read_text()
        self.assertIn("status: verified", skill)
        self.assertEqual(capability.main(["--root", str(self.root), "promote", "good"]), 1)

    def test_promote_preserves_other_lines(self):
        folder = make_cap(self.store, "keep", tests="pass")
        before = (folder / "SKILL.md").read_text()
        capability.main(["--root", str(self.root), "promote", "keep"])
        after = (folder / "SKILL.md").read_text()
        self.assertEqual(after.replace("candidate", "verified"), before.replace("candidate", "verified"))

    def test_disable_excludes_from_discovery(self):
        make_cap(self.store, "old", status="verified", tests="pass")
        self.assertEqual(capability.main(["--root", str(self.root), "disable", "old"]), 0)
        self.assertNotIn("old", self.run_cmd("find old"))
        self.assertIn("status: deprecated", (self.store / "old" / "SKILL.md").read_text())

    def test_report_counts_statuses(self):
        make_cap(self.store, "one")
        make_cap(self.store, "two", status="verified", tests="pass")
        make_cap(self.store, "three", status="deprecated")
        out = self.run_cmd("report")
        self.assertIn("capabilities: 3", out)
        self.assertIn("candidate: 1", out)
        self.assertIn("verified: 1", out)
        self.assertIn("deprecated: 1", out)
        self.assertIn("without tests: one", out)
        self.assertNotIn("three", out.split("without tests:")[1])

    def run_cmd(self, command: str) -> str:
        import contextlib
        import io

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            capability.main(["--root", str(self.root), *command.split()])
        return buffer.getvalue()


if __name__ == "__main__":
    unittest.main()
