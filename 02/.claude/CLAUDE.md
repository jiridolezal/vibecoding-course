# SPFx solution — working agreement

## FIRST: is this still an uninitialised template?

If `package.json` still contains `__name_slug__`, this is a fresh clone of the template and **nothing compiles yet** — every per-solution value is a double-underscore token, in file contents and in file and folder names.

Run `spfx-setup` before anything else, whatever the user asked for. Say that is what you are doing and why. Do not build, lint, or "fix" the tokens by hand, and do not start on the user's actual request until setup has run.

---

# WORKFLOW — MANDATORY FOR ANY PROMPT THAT RESULTS IN CODE CHANGES

If you are going to use Edit or Write, you **MUST** complete every applicable stage below before reporting completion. Bug fixes, features, refactors, config changes — no exceptions.

1. **Specs** — understand what is being built, for whom, the data, and the states. Ask about gaps; do not invent answers. → `spfx-specs`, then `spfx-architecture` for the plan and its diagrams
2. **Prototype** — for anything with new UI, get the design signed off before writing SPFx code. → `spfx-prototype`
3. **Implement** — build it, refactoring as you go. → `spfx-structure`, `spfx-data`, `spfx-ui`. If a list or library does not exist yet, that is stage 1b: `spfx-data-sources` first — never write a fetch against a source nobody has created
4. **Verify** — `tsc --noEmit`, eslint, stylelint, a production build, then **run it in the workbench and look at it**. → `spfx-preview`, `spfx-a11y`, `spfx-review`
5. **Report** — hand back a written summary. → `spfx-handoff`

**We write no automated tests at all. Stage 4 is what replaces them, and it is yours.** If you write code and stop without seeing it run, you have failed the task. Never report completion on the basis that the code looks correct.

A Stop hook runs `tsc` and eslint for you, plus stylelint when a stylesheet changed, and blocks on failure. It cannot open a browser — the workbench half of stage 4 is still on you.

**Trivial changes** — a typo, a one-line fix, a config tweak: skip stages 1–2. Say what you are doing and proceed. Stage 4 still applies.

**Branch before you edit.** `main` is the only long-lived branch and always holds working code. Create `feature/`, `improvement/` or `bugfix/<short-name>` first, commit at checkpoints, push every commit, and merge back and delete the branch when stage 4 passes. **Git is yours, not the user's** — they never ask for a commit and never ask for a push, and GitHub is always current. Full agreement in `.claude/rules/conventions.md`.

---

## The invariants

These hold in every file, so they are here rather than in a path-scoped rule that may not have loaded yet. The elaboration is in `.claude/rules/`, and most of them fail the lint gate — see `lint/README.md`.

1. No colour literal outside `src/theme/`. Colour is `var(--mc-color-*)`.
2. No user-facing string literal. Always `strings.X`, even on a Czech-only project.
3. No HTTP outside `data/`, and one HTTP client per solution.
4. No logic in the web part class, and no JSX in `utils/`.
5. Every provider exposes `isLoading` and `error`, and aborts on unmount.
6. Every view that loads data renders loading, empty, error and populated.
7. Never hand-edit a version field — `scripts/set-version.js` is the only writer, and a hook blocks the rest.
8. Never hardcode a tenant URL, site URL or list GUID — including in `preconfiguredEntries` and `.claude/settings.json`. The one carve-out is `config/serve.json`, SPFx's own dev-server config, which is useless empty.
9. Nothing secret ships in the bundle. Every user can read it.
10. Never pass a plain string `className` to a React Aria component. It *replaces* `.react-aria-*` and the focus ring with it. Use `cx()`.

---

## Traps specific to SPFx

You will not think to ask about these.

- **Every property pane change re-runs `render()`**, remounting the provider tree and refetching everything. Use `disableReactivePropertyChanges`.
- **Changing a property's shape breaks deployed instances** unless you bump `dataVersion` and migrate.
- **Web parts remount constantly in edit mode.** Abort in-flight requests.
- **`onDispose()` must unmount the React tree.** SPFx calls it when the web part goes away, but it does not unmount React for you — without `unmountComponentAtNode(this.domElement)` (or `root.unmount()`) the tree keeps its timers, subscriptions and in-flight requests alive, and edit mode creates a new one every time.
- **Overlays portal into `document.body`**, outside the web part — set the portal container or SharePoint chrome covers them.
- **Only `*.global.scss` compiles as plain CSS.** Every other `.scss` is a CSS module with hashed class names, so putting the React Aria styles in one silently unstyles every control. `src/theme/theme.global.scss` is the one global stylesheet; everything else is a `*.module.scss` sibling of its component.
- `.scss.ts` files are build output — gitignored, never edited.

---

## Where the rules are

Constraints live in `.claude/rules/`. Files with `paths:` frontmatter load when Claude opens a matching file **with the Read tool** — which does not happen when creating a new one, and does not happen when the file is read through `cat`, `sed` or `grep` instead. That is why the invariants above are duplicated here and nowhere else. Do not restate the rest.

Four of them carry no `paths:` and are therefore already in context, loaded at launch at the same priority as this file: `conventions.md` (naming, comments, markdown, git), `principles.md` (KISS, DRY, YAGNI, single responsibility, Liskov — how to decide what the invariants do not cover, and which principle wins when two disagree), `build-toolchain.md` and `project-choices.md`. The other six wait for a matching Read. Nothing needs fetching by hand.

## Skill router

| Situation | Skill |
|---|---|
| Fresh clone of the template | `spfx-setup` |
| Environment broken, wrong Node, install fails | `spfx-doctor` |
| Starting a feature or web part | `spfx-specs` |
| Planning how it will be built, diagrams | `spfx-architecture` |
| A list or library does not exist yet | `spfx-data-sources` |
| Designing UI before implementing | `spfx-prototype` |
| "Where does this file go?" / naming | `spfx-structure` |
| Fetching data, calling any API | `spfx-data` |
| Components, styling, theming | `spfx-ui` |
| Icons, images, media | `spfx-assets` |
| Property pane work | `spfx-property-pane` |
| Adding user-facing strings | `spfx-localization` |
| Reaching for a library or writing a util | `dont-reinvent` |
| Permissions, secrets, sanitising, personal data | `spfx-security` |
| Running or debugging in the workbench | `spfx-preview` |
| Accessibility check | `spfx-a11y` |
| Checking the work is done | `spfx-review` |
| Closing an iteration, reporting back | `spfx-handoff` |
| Releasing | `spfx-version`, `spfx-ship` |

## Agents

Two, both read-only and both worth their own context rather than yours. Neither is part of the lifecycle — run them when the question comes up.

| Question | Agent |
|---|---|
| "What is in this bundle, and why is it this big?" | `bundle-auditor` |
| "Is any of this still used?" | `dead-code-analyzer` |

`spfx-ship` and `spfx-assets` call for `bundle-auditor` when a bundle or its assets grew unexpectedly; `spfx-review` calls for `dead-code-analyzer` after a large change.

## MCP servers

Two, declared in `.mcp.json` at the project root so a clone gets them without anything being written to `~/.claude`. Claude Code asks you to approve them on first run. Both are read-only documentation lookups — a wrong answer costs a wasted read, never a broken solution.

| Question | Server |
|---|---|
| "What does the SPFx, Graph or PnP documentation actually say?" | `mslearn` |
| "What does this library's current version actually expose?" | `context7` |

`mslearn` is Microsoft's own Learn server and needs no key. Use it instead of recalling an API from memory: SPFx changed build system at 1.22, the extension debug manifest path has moved between releases, and the supported Node version is whatever the current matrix says. A remembered answer here is usually a stale one. `spfx-doctor` and `dont-reinvent` both say where to reach for it.

`context7` covers what Microsoft does not document — `react-aria-components`, PnPjs, `react-icons`. `dont-reinvent` tells you to check whether a control already exists before writing one; this is how you check its **current** API rather than the one in training data.

**Claude in Chrome is not one of these.** It is a browser extension, allowed in `settings.json` as `mcp__claude-in-chrome` but not a server in `.mcp.json`, so cloning this config does not bring it with you. `spfx-preview` needs it, because the workbench needs a real authenticated SharePoint session; without it, hand stage 4 to the user as that skill describes.
