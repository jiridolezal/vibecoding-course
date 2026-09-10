---
name: spfx-review
description: Definition of Done for an SPFx change - the checklist that must pass before the work is merged into main, covering build gates, the hard rules, states, accessibility, permissions, versioning and documentation. Use when the user says "is this done", "review my changes", "ready to ship", "check my work", before merging a branch, or at the end of a feature.
---

# spfx-review

Run this before merging any branch into `main`. Report honestly - a checklist that always passes is worthless.

## Build gates

```bash
npx tsc --noEmit
npx eslint src
npx stylelint "src/**/*.scss"
npx heft build --production
```

All of them must pass. Warnings are not "passing".

## The hard rules

Most of them are lint rules now, so the commands above *are* the check - see `lint/README.md` for the mapping. Do not re-grep what lint already covers; a green lint run is the evidence.

Three rules lint cannot see. Check these by reading the diff:

| Rule | How to check |
|---|---|
| No user-facing string literal | Read every changed `.tsx`. No tool tells a label from a `data-*` value |
| No tenant URL, site URL or list GUID | Read `preconfiguredEntries`, `serve.json` and every default. Also `.claude/settings.json` |
| Icons follow the theme | No colour passed to an icon anywhere in the diff |

If lint is not wired up in this repo yet, say so in the report rather than claiming the rules passed.

## Behaviour

- All four states implemented and actually seen in the workbench: loading, empty, error, populated
- Unconfigured web part shows a configuration placeholder
- Every acceptance item in `docs/specs.md` verified, not assumed
- Verified in a one-third column, not only full width
- Providers abort in-flight work on unmount, and `onDispose` unmounts the React tree
- `disableReactivePropertyChanges` set if a property drives a fetch

## Accessibility

- `spfx-a11y` run, no critical or serious violations outstanding
- Keyboard reaches everything, focus always visible

## Configuration and security

Run `spfx-security` if the change touched permissions, an API call, HTML rendering, URL parameters or personal data. Otherwise the short version:

- No tenant URL, site URL or list GUID in `preconfiguredEntries`
- No secrets anywhere in `src/` or `config/` - the bundle is public to every user, and so are property pane values
- Any HTML from a list is sanitised before rendering
- New API permissions least-privilege, documented in `docs/permissions.md`, with the admin approval step called out to the user

## Versioning and docs

- `dataVersion` bumped if a property shape changed, with a migration
- Version moved via `spfx-version` if this is going out (`node scripts/set-version.js --check` passes)
- `docs/` updated: specs, data sources, and a decision entry for anything a future reader would otherwise have to guess at
- `README.md` **checked section by section**, not glanced at. The four marked `(keep current)`: does the web part table list every web part that exists, does "What it reads" name every list and endpoint the code actually calls, do the property pane options match what is in the pane, and do the known limitations match "What I did not verify"? "Still accurate" is not an answer - name the sections you compared

## Hygiene

- Dead code removed - run the `dead-code-analyzer` agent if the change was large
- No unreferenced asset added; images sized for their largest render
- No commented-out code, no TODOs
- No dependency added without justification - see `dont-reinvent`
- No new dependency that nothing imports

## Report

Group as: **blocking**, **should fix**, **noted**. Say plainly which checks you actually ran and which you could not.

Nothing blocking left means the branch can be merged into `main` and deleted - see `.claude/rules/conventions.md`. Then `spfx-handoff` closes the iteration and reports back to the user.
