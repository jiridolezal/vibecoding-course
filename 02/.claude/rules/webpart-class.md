---
paths:
  - "src/webparts/*/*WebPart.ts"
  - "src/extensions/*/*.ts"
---

# The web part class

The invariants are in CLAUDE.md. This file is the elaboration; the folder contract is in the `spfx-structure` skill.

- **Wiring only.** Properties in, `ContextWrapper` out. No fetching, no mapping, no conditionals on data, no formatting. If a change here needs a test to be sure it works, it belongs one layer down.
- **`onDispose()` must unmount the React tree.** SPFx calls it when the web part goes away but does not unmount React for you, and edit mode creates a new instance every time - so a missing `root.unmount()` leaks a live tree with its timers, subscriptions and in-flight requests on every remount.
- **`render()` runs again on every property pane change**, remounting the provider tree and refetching everything. Set `disableReactivePropertyChanges` unless a property genuinely wants live preview.
- **Changing the shape of a property breaks web parts already on pages.** Bump `dataVersion` and write the migration in the same change, or instances deployed against the old shape fail on load.
- **Read context off `this.context`, pass it down as props.** A component that reaches for a global SPFx context cannot be prototyped or rendered anywhere else.

Procedure: `spfx-structure`, `spfx-property-pane`.
