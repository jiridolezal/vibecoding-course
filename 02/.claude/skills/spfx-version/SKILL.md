---
name: spfx-version
description: Move the solution version, keeping package.json, the solution version and the feature version in lockstep - the only sanctioned writer of those fields, which a hook otherwise blocks. Use when the user says "bump the version", "release", "new version", "patch", "minor", "major", or before packaging a build.
---

# spfx-version

Three fields must move together. `scripts/set-version.js` is the only writer - a PreToolUse hook denies Edit and Write on them, with no escape hatch, because an environment-variable escape is something the model cannot set for its own tool call.

## The convention

| File | Field | Format |
|---|---|---|
| `package.json` | `version` | `x.y.z` |
| `config/package-solution.json` | `solution.version` | `x.y.z.0` |
| `config/package-solution.json` | `solution.features[].version` | `x.y.z.0` |

`package.json` is the source of truth. SharePoint requires four parts; the fourth stays `0` until we have a build pipeline to put a build number there.

**The feature version is not decoration.** If it does not move, SharePoint may not run the feature upgrade, and the deployment silently does nothing.

## Which part moves

| Change | Bump |
|---|---|
| Bug fix, no behaviour change | patch |
| New capability, backwards compatible | minor |
| Breaking change to properties, data shape, or required permissions | major |

A **property shape change** is a major bump *and* requires a `dataVersion` bump plus a migration - see `spfx-property-pane`. Deployed instances carry the old shape.

## Procedure

1. Read the current version from `package.json` and decide which part moves
2. **Confirm the new version with the user before writing anything**
3. Run the script - it writes `package.json`, `solution.version` and every `features[].version` in one pass, so they cannot drift:

```bash
node scripts/set-version.js minor     # or patch / major / an explicit 1.4.0
node scripts/set-version.js --check   # exits non-zero if the three disagree
```

4. Update `CHANGELOG.md` - what changed, for a human, not a commit dump
5. Commit as `Bump version to x.y.z` (see the git policy in `.claude/rules/conventions.md`)

Tagging is part of a release, not of a version bump: tags go on `main` after the release merge, and cutting a tag needs the user's go-ahead even though ordinary commits and pushes do not. `spfx-ship` covers it.

## When a pipeline exists

Switch the fourth digit to the CI build number and make the pipeline the only writer. Until then it stays `0` and this skill is the only writer.
