"""Registry commands over a project's capability store.

A capability is a project skill folder under ``.agents/skills/<name>/`` whose
``SKILL.md`` frontmatter carries ``name``, ``description``, ``status``,
``side-effects`` and an optional ``version``. Promotion is machine-checked: a
candidate becomes verified only when its tests run green and its files carry
nothing that looks like a secret.
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

STATUSES = ("candidate", "verified", "deprecated")
SIDE_EFFECTS = ("read-only", "repo-write", "beyond-repo")
SECRET_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\bpassword\s*[:=]\s*\S+"),
)
STORE_REL = Path(".agents") / "skills"


@dataclass
class Capability:
    path: Path
    name: str = ""
    description: str = ""
    status: str = ""
    side_effects: str = ""
    version: str = ""
    test_command: str = ""
    problems: list[str] = field(default_factory=list)


def parse_frontmatter(text: str) -> dict[str, str]:
    """Read the flat ``key: value`` frontmatter, joining folded scalars."""
    lines = text.splitlines()
    fields: dict[str, str] = {}
    if not lines or lines[0].strip() != "---":
        return fields
    key = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith((" ", "\t")) and key:
            fields[key] += " " + line.strip()
        elif ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            fields[key] = value.strip()
    return fields


def set_status(path: Path, new: str) -> None:
    """Rewrite only the ``status:`` line, leaving every other byte alone."""
    lines = path.read_text().splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith("status:"):
            lines[i] = f"status: {new}\n"
            tmp = path.parent / (path.name + ".tmp")
            tmp.write_text("".join(lines))
            os.replace(tmp, path)
            return
    raise SystemExit(f"no status field in {path}")


def load(path: Path) -> Capability:
    skill = path / "SKILL.md"
    cap = Capability(path=path)
    if not skill.is_file():
        cap.problems.append("no SKILL.md")
        return cap
    fields = parse_frontmatter(skill.read_text())
    cap.name = fields.get("name", "")
    cap.description = fields.get("description", "")
    cap.status = fields.get("status", "")
    cap.side_effects = fields.get("side-effects", "")
    cap.version = fields.get("version", "")
    cap.test_command = fields.get("test-command", "")
    if not cap.name:
        cap.problems.append("frontmatter has no name")
    elif cap.name != path.name:
        cap.problems.append(f"name {cap.name!r} does not match folder {path.name!r}")
    if not cap.description:
        cap.problems.append("frontmatter has no description")
    if cap.status not in STATUSES:
        cap.problems.append(f"status {cap.status!r} is not one of {STATUSES}")
    if not cap.side_effects:
        cap.problems.append("frontmatter has no side-effects")
    elif cap.side_effects not in SIDE_EFFECTS:
        cap.problems.append(f"side-effects {cap.side_effects!r} is not one of {SIDE_EFFECTS}")
    return cap


def load_store(root: Path) -> list[Capability]:
    store = root / STORE_REL
    if not store.is_dir():
        return []
    return [load(p) for p in sorted(store.iterdir()) if p.is_dir()]


def visible(cap: Capability) -> bool:
    return cap.status != "deprecated"


def scan_secrets(path: Path) -> list[str]:
    hits: list[str] = []
    for file in sorted(path.rglob("*")):
        if not file.is_file() or file.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip"}:
            continue
        try:
            text = file.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                hits.append(str(file.relative_to(path)))
                break
    return hits


def split_command(command: str, windows: bool = os.name == "nt") -> list[str]:
    """Split a test-command into argv, keeping backslash paths intact on Windows."""
    if windows:
        return [token.strip("\"'") for token in shlex.split(command, posix=False)]
    return shlex.split(command)


def run_tests(path: Path, test_command: str = "") -> tuple[bool, str]:
    if test_command:
        argv = split_command(test_command)
        if not argv:
            return False, "empty test-command"
        proc = subprocess.run(argv, cwd=path, capture_output=True, text=True, check=False)
        tail = ((proc.stderr or "") + (proc.stdout or "")).strip().splitlines()
        return proc.returncode == 0, tail[-1] if tail else f"exit {proc.returncode}"
    tests = path / "tests"
    if not tests.is_dir() or not any(tests.glob("test_*.py")):
        return False, "no tests under tests/"
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(tests), "-p", "test_*.py"],
        capture_output=True,
        text=True,
        check=False,
    )
    tail = ((proc.stderr or "") + (proc.stdout or "")).strip().splitlines()
    return proc.returncode == 0, tail[-1] if tail else f"exit {proc.returncode}"


def print_rows(caps: list[Capability]) -> None:
    for cap in caps:
        mark = "!" if cap.problems else " "
        print(f"{mark} {cap.name:<24} {cap.status:<10} {cap.side_effects:<11} {cap.description[:60]}")


def find_capability(root: Path, name: str) -> Capability:
    path = root / STORE_REL / name
    if not path.is_dir():
        raise SystemExit(f"no capability named {name}")
    return load(path)


def cmd_list(args: argparse.Namespace) -> int:
    caps = [c for c in load_store(Path(args.root)) if visible(c) or args.all]
    print_rows(caps)
    return 0


def cmd_find(args: argparse.Namespace) -> int:
    query = args.query.lower()
    caps = [
        c
        for c in load_store(Path(args.root))
        if visible(c) and (query in c.name.lower() or query in c.description.lower())
    ]
    print_rows(caps)
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    cap = find_capability(Path(args.root), args.name)
    print(f"name:         {cap.name}")
    print(f"status:       {cap.status}")
    print(f"side-effects: {cap.side_effects}")
    print(f"version:      {cap.version}")
    print(f"folder:       {cap.path}")
    print(f"description:  {cap.description}")
    for problem in cap.problems:
        print(f"problem:      {problem}")
    return 1 if cap.problems else 0


def cmd_test(args: argparse.Namespace) -> int:
    cap = find_capability(Path(args.root), args.name)
    ok, detail = run_tests(cap.path, cap.test_command)
    print(f"{cap.name}: {detail}")
    return 0 if ok else 1


def cmd_promote(args: argparse.Namespace) -> int:
    cap = find_capability(Path(args.root), args.name)
    if cap.status != "candidate":
        print(f"{cap.name}: only candidates promote, this one is {cap.status}")
        return 1
    if cap.problems:
        for problem in cap.problems:
            print(f"{cap.name}: {problem}")
        return 1
    if cap.side_effects == "beyond-repo" and not args.reviewed:
        print(f"{cap.name}: acts beyond the repository; promote needs the user's --reviewed")
        return 1
    if scan_secrets(cap.path):
        print(f"{cap.name}: secret-looking material in the capability folder; find and remove it before promoting")
        return 1
    ok, detail = run_tests(cap.path, cap.test_command)
    if not ok:
        print(f"{cap.name}: promotion blocked, {detail}")
        return 1
    set_status(cap.path / "SKILL.md", "verified")
    print(f"{cap.name}: verified ({detail})")
    return 0


def cmd_disable(args: argparse.Namespace) -> int:
    cap = find_capability(Path(args.root), args.name)
    set_status(cap.path / "SKILL.md", "deprecated")
    print(f"{cap.name}: deprecated, excluded from list and find")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    caps = load_store(Path(args.root))
    counts = {status: 0 for status in STATUSES}
    untested = []
    broken = 0
    for cap in caps:
        if cap.status in counts:
            counts[cap.status] += 1
        if cap.problems:
            broken += 1
        if visible(cap) and not any((cap.path / "tests").glob("test_*.py")):
            untested.append(cap.name)
    print(f"capabilities: {len(caps)}  " + "  ".join(f"{s}: {n}" for s, n in counts.items()))
    if untested:
        print(f"without tests: {', '.join(untested)}")
    if broken:
        print(f"with problems: {broken}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="list, find, inspect, test, promote, disable and report project capabilities")
    parser.add_argument("--root", default=".", help="project root holding .agents/skills")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="show every capability").add_argument("--all", action="store_true")
    find_p = sub.add_parser("find", help="search names and descriptions")
    find_p.add_argument("query")
    inspect_p = sub.add_parser("inspect", help="print one capability's full record")
    inspect_p.add_argument("name")
    test_p = sub.add_parser("test", help="run one capability's tests")
    test_p.add_argument("name")
    promote_p = sub.add_parser("promote", help="verify a candidate and mark it verified")
    promote_p.add_argument("name")
    promote_p.add_argument("--reviewed", action="store_true", help="the user reviewed a beyond-repo capability")
    disable_p = sub.add_parser("disable", help="deprecate a capability")
    disable_p.add_argument("name")
    sub.add_parser("report", help="counts and health of the store")
    args = parser.parse_args(argv)
    handlers = {
        "list": cmd_list,
        "find": cmd_find,
        "inspect": cmd_inspect,
        "test": cmd_test,
        "promote": cmd_promote,
        "disable": cmd_disable,
        "report": cmd_report,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
