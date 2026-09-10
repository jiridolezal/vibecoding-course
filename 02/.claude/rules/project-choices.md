# Project choices

The decisions that vary between solutions. **This is the only file in `.claude/` that a project is expected to edit** - everything else stays identical to the template, so drift is visible.

`spfx-setup` fills this in. Changing an entry afterwards is a decision for `docs/decisions/`, not a preference.

| Choice | This solution |
|---|---|
| Icon set | `react-icons/fi` (Feather, MIT) |
| HTTP client | `SPHttpClient` |
| Default locale | `cs-cz` |

Importing an icon from any other `react-icons` subpath, or introducing a second HTTP client, is a review failure.
