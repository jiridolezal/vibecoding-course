---
paths:
  - "src/**/data/**"
  - "src/**/providers/**"
---

# Data layer rules

The invariants are in CLAUDE.md. This file is the elaboration; procedure is in the `spfx-data` skill.

- **This is the only layer that does HTTP**, and one client per solution, named in project choices. Mixing two is worse than either choice. eslint enforces the boundary; it cannot tell you that you picked the wrong client.
- **A provider that swallows a failure into `console.error`** leaves the user staring at an empty list forever. That is the single most common defect in our solutions, which is why `isLoading` and `error` are not optional.
- **Always check `response.ok`** before reading a body, and throw an error that names the list and the status. A failed request returning `undefined` produces a bug report three screens away from the cause.
- **Abort in-flight work on unmount.** SPFx remounts web parts constantly in edit mode, and `onDispose` must unmount the React tree - see CLAUDE.md.
- **Raw to domain mapping happens here**, never in a component. `TReceivedX` is what SharePoint returns; `XItem` is what the app uses.
- **`$select` the fields you need**, use internal field names, follow `@odata.nextLink` properly, and honour `Retry-After` on 429. `$select` is a privacy control as much as a performance one - see `spfx-security`.
- Never concatenate user input into an OData `$filter`. Encode it.
- Prefer `undefined` over `null` for absent values.
