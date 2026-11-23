---
name: frontend
description: >-
  Use when the task builds, redesigns, improves, polishes or reviews a user-facing frontend, or when a pinned frontend specialist cannot be loaded. Skip backend-only work and pure design-process planning.
metadata:
  opencode/autoinvoke: true
---

# Frontend Router

You are handling a task that changes or judges what a user sees. **Do not rely on generic defaults.**
Identify the user's specific intent from the routing table below and **read the
corresponding file(s)** before taking action.

Inspect the repository before asking technical questions. The pipeline, its modes and the prime directive live in `references/workflow.md`.

## Routing Table

| User Intent / Trigger | Reference File to Read |
| :--- | :--- |
| Build, redesign, improve or polish a frontend end to end, or review one without editing | `references/workflow.md` |
| Choose, fetch or repair a pinned third-party specialist | `references/specialist-map.md` |
| Final functional, responsive, accessibility, visual, performance and motion gates | `references/qa-gates.md` |

## Rules
1. **Load selectively:** Open ONLY the file(s) that match the current request. Never bulk-read the entire `references/` directory.
2. **Compose when needed:** Read at most one workflow row. Other rows may join it.
3. **Re-route on pivot:** If the conversation shifts to another domain, trigger the appropriate domain skill rather than guessing.
