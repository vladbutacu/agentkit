# Reuse

A capability is a workflow a repository keeps as a tested project skill: a folder `.agents/skills/<name>/` holding a `SKILL.md`, with the scripts and tests that do the work beside it. The `SKILL.md` description is the index, its body is the contract, and the code loads only while the capability runs or changes. Tools that read `.agents/skills/` natively list the descriptions themselves; `repo-bootstrap` links the folder into the others.

## Find before you build

Before deterministic work that repeats:

1. Read the session's project-skill listing. Every capability description is already in it.
2. When the session lists no skills, or the store has grown past what the listing shows, search it from this skill's folder: `python3 scripts/registry/capability.py --root <project> find <term>`. `inspect <name>` prints the full record, and `list` shows every capability with its status. Where the script cannot run, `rg -l -i '<term>' .agents/skills --glob 'SKILL.md'` over the frontmatter does the same job.
3. Read the matching `SKILL.md` body for the contract before running anything: inputs, outputs, side effects, exit behavior.
4. Run the capability the way its `SKILL.md` documents, usually a script under its folder, and check the output against the task, not just the exit code.

## Choose how to execute

- One simple action with a native tool for it: the native tool.
- Work a capability covers: the capability, through its contract.
- Anything else: the smallest fresh code that solves it, in the repository's own language and conventions. Loops, polling, joins, filtering of large results and dependent multi-step sequences belong in code, not in tool calls an agent steers one at a time.

Judgement, ambiguous goals and interpreting exceptions stay with the agent. Deterministic iteration does not.

## Overlap

When a variation of an existing capability appears, extend that capability: add the variation to its contract and a regression test for it. Create a sibling folder only when one contract cannot describe both uses without lying.

## Verify

A reused capability is healthy when `capability test <name>` passes and its output meets the current task. When a capability wraps an external tool or API that changed shape, re-run its tests before reusing it; a capability whose tests keep failing or whose contract no longer matches the repository is retired with `capability disable <name>`. Deletion is optional, and git holds the history.
