# Third-party notices

Content adapted from third-party work retains its upstream license. Everything
else in this repository is covered by the root `LICENSE`.

## Skills adapted from Matt Pocock's skills (MIT)

The following skills and their supporting reference files are adapted from
https://github.com/mattpocock/skills:

- `skills/design/references/codebase-design.md`
- `skills/design/references/domain-modeling.md`
- `skills/inquiry/references/research.md`
- `skills/inquiry/references/retro.md`
- `skills/design/references/to-tickets.md`
- `skills/writing/references/writing-for-agents.md`

MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Desloppify skill (OSNL 0.2)

`skills/repo-ops/references/desloppify.md` adapts the skill text from https://github.com/peteromallet/desloppify.
Copyright (c) 2025-2026 Peter O'Malley, licensed under the Open Source Native
License 0.2; see `skills/repo-ops/references/desloppify/LICENSE`. Provenance is recorded in
`skills/repo-ops/references/desloppify/workflow.md`. Redistribution here is permitted
because this repository is open source; a closed-source product embedding this
skill would need the licensor's commercial license.

## Tool logos

The marks in `assets/logos/` identify the tools agentkit supports and are
trademarks of their owners. Sources and usage notes are in
`assets/logos/README.md`.

## Engineering references

The ideas in these references are adapted, and the text rewritten, from a
third-party MIT-licensed skill collection:

- `skills/design/references/brainstorming.md`
- `skills/design/references/writing-plans.md`
- `skills/engineering/references/`

Copyright (c) 2025 Jesse Vincent

Permission is hereby granted, free of charge, to any person obtaining a copy of
the original software and associated documentation files, to deal in it without
restriction, subject to the following condition: the above copyright notice and
this permission notice shall be included in all copies or substantial portions
of it. The software is provided "as is", without warranty of any kind.

## Frontend specialist skills fetched at runtime

The `frontend` skill routes frontend work to third-party specialist skills. These
upstream projects are independent works; agentkit does not claim authorship of
them and does not republish them in this repository. `skills/frontend/scripts/upstreams/upstreams.py`
fetches each repository from GitHub at the immutable commit pinned in
`skills/frontend/upstream.lock.json`, verifies the checkout, and returns the
original skill path. Cached upstream files are never rewritten.

| Id | Upstream project | Pinned commit | License | Use |
|---|---|---|---|---|
| `ui-ux-pro-max` | `nextlevelbuilder/ui-ux-pro-max-skill` | `28b3b8dee8c976df4fa3e94aed4e092ad43fcb03` | MIT © Next Level Builder | UI/UX, accessibility, responsive and design-system intelligence |
| `taste-skill` | `Leonxlnx/taste-skill` | `12af471f627f866411b4bd785b19646d3672784c` | MIT © Leonxlnx | Art direction and anti-generic visual design |
| `frontend-design` | `anthropics/skills` | `ca45fc496a3436251f191354091d557da31c15b5` | Apache-2.0 © Anthropic, PBC | Bounded frontend visual design doctrine |
| `web-artifacts-builder` | `anthropics/skills` | `ca45fc496a3436251f191354091d557da31c15b5` | Apache-2.0 © Anthropic, PBC | Standalone interactive artifact/prototype workflow |
| `transitions-dev` | `Jakubantalik/transitions.dev` | `6a7d68260d624eb66661cc3af17e0989476f48ae` | Transitions.dev License © Jakub Antalik | Semantic UI transition recipes |
| `transitions-polish` | `Jakubantalik/transitions.dev` | `6a7d68260d624eb66661cc3af17e0989476f48ae` | Transitions.dev License © Jakub Antalik | Motion timing/easing polish |
| `vercel-react-best-practices` | `vercel-labs/agent-skills` | `1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62` | MIT © Vercel | React/Next.js performance and implementation guidance |
| `frontend-design-audit` | `mistyhx/frontend-design-audit` | `40c9a5f91a523dc152deb789033ef556ca8fd252` | MIT © mistyhx | Final usability/accessibility audit with severity-rated findings |

Fetching at a pinned commit rather than redistributing keeps attribution clear
and matters for Transitions.dev in particular: its license permits installing
and using its skills in coding agents but restricts redistribution of the
transitions library itself as a competing library/motion pack. Users remain
responsible for complying with each upstream license. Upstream names and
trademarks belong to their respective owners; agentkit is not affiliated with,
endorsed by, or sponsored by these projects.

## Plugin checkouts

The third-party plugins declared in `plugins/manifest.json` are fetched into
`~/.local/share/agentkit/plugins/` at install time. They are not part of this
repository and carry their own upstream licenses.
