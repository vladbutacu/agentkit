---
name: capabilities
description: >-
  Use when deterministic work repeats: to find and reuse the repository's tested capabilities before doing it again, to decide after a meaningful workflow whether it becomes one, and when running a capability command or checking the store's health. Skip one-off actions and single reads.
metadata:
  opencode/autoinvoke: true
---

# Capabilities Workflow Router

You are handling a task related to reusing and growing the repository's tested capabilities. **Do not rely on generic defaults.**
Identify the user's specific intent from the routing table below and **read the
corresponding file(s)** before taking action.

## Routing Table

| User Intent / Trigger | Reference File to Read |
| :--- | :--- |
| Deterministic work that repeats, or checking what the repository's capabilities already carry | `references/reuse.md` |
| A meaningful workflow finished and may be worth keeping as a tested capability | `references/extraction.md` |
| Running a capability command, or checking the store's health | `references/registry.md` |

## Rules
1. **Load selectively:** Open ONLY the file(s) that match the current request. Never bulk-read the entire `references/` directory.
2. **Compose when needed:** Read at most one workflow row. Other rows may join it.
3. **Re-route on pivot:** If the conversation shifts to another domain, trigger the appropriate domain skill rather than guessing.
