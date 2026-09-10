---
paths:
  - "package.json"
  - "config/package-solution.json"
---

# Version fields

**Do not hand-edit any version field in these files.** A PreToolUse hook denies it, with no environment-variable escape. `scripts/set-version.js` is the only writer, and the `spfx-version` skill drives it:

```bash
node scripts/set-version.js patch      # or minor / major / an explicit x.y.z
node scripts/set-version.js --check    # verify the three fields agree
```

Three fields move together:

| File | Field | Format |
|---|---|---|
| `package.json` | `version` | `x.y.z` |
| `config/package-solution.json` | `solution.version` | `x.y.z.0` |
| `config/package-solution.json` | `solution.features[].version` | `x.y.z.0` |

The feature version is not decoration: if it does not move, SharePoint may skip the feature upgrade and the deployment silently does nothing.

A change to a property's shape is a major bump **and** needs a `dataVersion` bump plus a migration, or web part instances already on pages break.
