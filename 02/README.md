# Assignment 02 — the coding agent we actually use

This is not a configuration written for the assignment. It is the one we work in every day: the `.claude/` directory of our SPFx delivery template, the thing that turns Claude Code into a SharePoint Framework developer who already knows our conventions.

It is copied here almost untouched. 37 of the 40 files are byte-identical to the ones in the live repository; the only additions are the layer it was missing — MCP servers — which is `.mcp.json` plus three paragraphs, one in `CLAUDE.md` and one each in the two skills that now reach for a server instead of guessing.

No plugins. No marketplace. Everything is a plain file in this folder.

## What is in it

| Element | Count | Where |
|---|---|---|
| Skills | 20 | `.claude/skills/` |
| Subagents | 2 | `.claude/agents/` |
| MCP servers | 2 | `.mcp.json` |
| Hooks | 3 events, 4 files | `.claude/hooks/` |
| Rules | 10 | `.claude/rules/` |
| Slash command | 1 | `.claude/commands/` |
| Project instructions | 1 | `.claude/CLAUDE.md` |
| Permissions | allow / ask / deny | `.claude/settings.json` |

## The idea

An SPFx solution has a large amount of knowledge attached to it that a model cannot infer from the code: which of the forty React Aria components we style, that only `*.global.scss` compiles as plain CSS, that a property shape change breaks every deployed instance unless `dataVersion` moves with it. Put all of that in `CLAUDE.md` and it is in context for every prompt, including "fix this typo".

So it is split by when it is needed:

- **`CLAUDE.md`** — the workflow, and the ten invariants that hold in every file. Always loaded, deliberately short.
- **`rules/`** — the elaboration. Four carry no `paths:` and load at launch; the other six wait until Claude opens a matching file, so property pane rules cost nothing on a styling task.
- **`skills/`** — one per situation, loaded when that situation comes up. `CLAUDE.md` ends with a router table mapping situation to skill.
- **`agents/`** — the two questions worth their own context window rather than yours.

The whole thing is about 250 KB on disk, of which roughly 31 KB is in context at rest: `CLAUDE.md`, the four always-loaded rules, and the twenty skill descriptions that let Claude decide which skill to open. The six path-scoped rules and every skill body — the other 200 KB — load only when something actually needs them.

## Skills

Twenty, and the interesting thing is that they are a lifecycle rather than a toolbox. `CLAUDE.md` makes stages 1–5 mandatory for any prompt that ends in an `Edit` or `Write`, and names the skill that drives each one. Grouped by the stage they serve:

| Stage | Skills |
|---|---|
| 1. Specs | `spfx-specs`, `spfx-architecture`, `spfx-data-sources` |
| 2. Prototype | `spfx-prototype` |
| 3. Implement | `spfx-structure`, `spfx-data`, `spfx-ui`, `spfx-assets`, `spfx-property-pane`, `spfx-localization`, `dont-reinvent`, `spfx-security` |
| 4. Verify | `spfx-preview`, `spfx-a11y`, `spfx-review` |
| 5. Report | `spfx-handoff` |
| Outside the lifecycle | `spfx-setup`, `spfx-doctor`, `spfx-version`, `spfx-ship` |

**We write no automated tests on these projects** — that is a recorded decision, in `docs/decisions/0002-no-automated-tests.md` in the real repo. Stage 4 is what replaces them, which is why three skills and a hook are pointed at it. `spfx-prototype` is the one that changed how the work goes most: a static HTML page using the project's *real* compiled CSS, published as an Artifact for sign-off, before any SPFx code exists.

## Subagents

Both exist because the answer needs to read a great many files to produce a short verdict — exactly what a separate context window is for. Both are report-only: they say so in their own first line, they never edit source, and removing a dependency or deleting a file is left as a decision for the developer. `bundle-auditor` does run a production build, because it cannot measure a bundle that does not exist yet.

| Agent | Model | Question |
|---|---|---|
| `bundle-auditor` | sonnet | "What is in this bundle, and why is it this big?" |
| `dead-code-analyzer` | sonnet | "Is any of this still used?" |

`dead-code-analyzer` grades every finding HIGH / MEDIUM / LOW and carries a list of SPFx-specific false positives — a web part class is reached through its manifest, not an import, so a naive scan calls the whole solution dead.

## MCP servers

The two servers are the part added for this assignment, and they close a real gap rather than decorating the config.

| Server | Transport | Gives |
|---|---|---|
| `mslearn` | HTTP, no key | Official Microsoft Learn docs — the `@microsoft/sp-*` API reference, Graph permissions, the SPFx and Node compatibility matrix |
| `context7` | stdio via `npx` | Current docs for everything Microsoft does not publish — `react-aria-components`, PnPjs, `react-icons` |

Both are read-only lookups, so a bad answer costs a wasted read rather than a broken solution. They are wired into the skills that need them, not just declared: `spfx-doctor` asks `mslearn` for the Node matrix instead of guessing at it, and `dont-reinvent` asks `context7` for a control's current API — that skill's whole job is answering "does this already exist", and a correct answer against a renamed prop still does not compile.

**Claude in Chrome is not one of these.** It is a browser extension, allowed in `settings.json` as `mcp__claude-in-chrome`, but it is not a server in `.mcp.json` and cloning this folder does not bring it with you. `spfx-preview` wants it because the SharePoint workbench needs a real authenticated session, which a headless browser cannot have. Without it that skill hands stage 4 back to the developer with the exact URL to open — which is the honest outcome, not a silent skip.

## Hooks

Three events, because a floor nobody can skip has to be enforced rather than requested.

| Event | Hook | Does |
|---|---|---|
| `PreToolUse(Edit\|Write)` | `guard-version.js` | Denies hand-edits to the three version fields. `scripts/set-version.js` is the only writer, so they cannot drift |
| `PostToolUse(Edit\|Write)` | `format-on-write.js` | Runs prettier on the file just written |
| `Stop` | `verify-gate.js` | Runs `tsc --noEmit`, eslint, and stylelint when a stylesheet changed. Exit 2 blocks the stop and hands the errors back |

`local-bin.js` is the shared helper the other two use, and it is there for a specific reason: `execFileSync("npx.cmd", …)` throws `EINVAL` on Windows since the CVE-2024-27980 fix, and `shell: true` then breaks on any project path containing a space. It resolves the tool's entry point under `node_modules` and runs it with the Node binary already executing the hook.

The verify gate caps itself at two blocks per session and no-ops when there is no `package.json`, no git repo, or no toolchain installed — which is why this folder is safe to open on its own.

## Permissions

`settings.json` is `allow` / `ask` / `deny`, evaluated deny-first. `allow` is a specific list of `npm`, `npx heft`, `tsc`, `eslint` and everyday git commands rather than a blanket `Bash`. `ask` holds `npm publish` and `git tag`. `deny` holds `git reset --hard`, every force push, `git branch -D`, and reads of `.env`, `*.pem`, `*.key`, `.npmrc` and `~/.ssh/**`.

The unusual part is that **git is the agent's job, not the developer's**: branching, committing, pushing and merging happen without being asked, and `rules/conventions.md` is the full agreement. What stays behind `ask` or `deny` is only the destructive half — history rewriting and throwing work away.

## Try it

```bash
cd 02
claude
```

Claude Code will ask you to approve the two MCP servers from `.mcp.json` on first run; say yes. Then `/skills` lists the twenty, `/agents` the two, and `/spfx-help` prints the router.

Everything is scoped to this folder. Nothing is written to `~/.claude`, so your own setup is untouched.

### Prerequisites

| Requirement | Needed for |
|---|---|
| Node / `npx` | the `context7` MCP server, and the hooks |
| Network | the `mslearn` MCP server (HTTP, no key, nothing to configure) |
| Claude in Chrome extension | the authenticated workbench check in `spfx-preview` — optional, see above |

### What this folder cannot do

The config is for an SPFx repository, and this folder is not one. Opened on its own it will load, route and answer — the skills, agents, rules and MCP servers all work, and that is what there is to review — but the hooks find no `package.json` and quietly no-op, and anything that wants to build or run needs the actual solution around it.

`rules/project-choices.md` is the one file a real project edits; the values in it here are the template's defaults.
