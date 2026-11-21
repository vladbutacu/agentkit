# Registry

The store's command surface. From this skill's folder, run `python3 scripts/registry/capability.py --root <project> <command>`:

| Command | What it does |
| :--- | :--- |
| `list` | every capability with status and side-effects; `--all` includes deprecated |
| `find <term>` | search over names and descriptions |
| `inspect <name>` | the full record, problems included |
| `test <name>` | run the capability's tests |
| `promote <name>` | enforce the gates, then flip `candidate` to `verified` |
| `disable <name>` | deprecate, excluding the capability from discovery |
| `report` | counts by status and capabilities without tests |

Tests default to Python's unittest over the capability's `tests/` folder. A capability in another language, or with its own runner, sets a `test-command` line in its frontmatter; it runs from the capability folder, splits like a shell command (quote an argument that has spaces), and keeps backslash paths on Windows. The creation contract, including every frontmatter field, is in [`extraction`](extraction.md).

Two deliberate absences. There is no `run` command: each capability's `SKILL.md` documents its invocation and the host's approval gates govern it, and a wrapper would add no authority. There is no `trusted` status: repeated success adds no permissions, so `verified` is the ceiling. The secret scan in `promote` is a floor, four common patterns, not a real secret scanner.

agentkit ships no token or latency numbers. Measure a baseline per repository by running a repeated task with and without its capability, and record the result in that repository.
