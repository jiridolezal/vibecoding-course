---
name: dont-reinvent
description: Check whether the thing about to be written already exists - PnP reusable controls and property controls, PnPjs, CLI for Microsoft 365, React Aria, and the rules for when adding a dependency is justified. Use before writing any non-trivial utility, control, picker, dialog, or helper, when the user says "do not reinvent the wheel", "is there a library", "does this exist", or when about to add a dependency.
---

# dont-reinvent

Before writing something non-trivial, check this list. Most of it is maintained by the PnP community and is already used by thousands of solutions.

**Then check the current API, not the remembered one.** This list says what exists; it does not say what today's version of it looks like. `context7` has live docs for `react-aria-components`, PnPjs and `react-icons`, and `mslearn` has them for anything Microsoft ships. A prop that moved or a control that was renamed is the usual reason a correct "that already exists" answer still does not compile.

## UI controls

**`@pnp/spfx-controls-react`** - among others:

| Need | Control |
|---|---|
| Web part not configured yet | `Placeholder` |
| Pick a file from SharePoint or OneDrive | `FilePicker` |
| Show a list of items | `ListView` |
| Rich text editing | `RichText` |
| A dialog hosting an SPFx page | `IFrameDialog` |
| Carousel, charts, file type icons, taxonomy pickers | several |

**`react-aria-components`** - every interactive primitive: button, select, combobox, dialog, popover, tabs, table, tag group, date pickers, sliders. Accessible and keyboard-correct by default. See `spfx-ui`.

Write a custom component when the behaviour is genuinely specific to this solution. Do not write a dropdown.

## Property pane

**`@pnp/spfx-property-controls`** - people picker, list picker, term picker, colour picker, date picker, collection data, and more. See `spfx-property-pane`.

## Data

**PnPjs** for paging, batching, caching, files and Graph. See `spfx-data` for when it earns its place - it is not the automatic answer.

**CLI for Microsoft 365** for tenant operations from the terminal: app catalog deployment, list and site provisioning, permission grants, and `spfx project upgrade`, which produces an exact step-by-step report for moving a solution to a newer SPFx version. Do not hand-plan an SPFx upgrade.

## Things not to hand-write

- Date formatting and parsing - use the platform `Intl` APIs
- Deep clone, debounce, throttle - `@microsoft/sp-lodash-subset` is already a dependency of SPFx
- HTML sanitisation - use a maintained sanitiser, never a regex
- GUID generation - `crypto.randomUUID()`
- Accessible widget behaviour - React Aria

## Adding a dependency

Justify all of:

1. It solves a real problem in this solution, not a hypothetical one
2. Nothing already in the tree does it - check `package.json` first
3. Its bundle cost is acceptable for what it gives
4. It is maintained, and selective imports are possible
5. It works with the React version this SPFx release ships

Record anything non-obvious in `docs/decisions/`. And remove dependencies nothing imports - check with the `dead-code-analyzer` agent.

## The reverse

The rule is not "always take the library". A twelve-line pure function we own beats a transitive dependency tree. The test is whether the problem is **generic** - accessibility, date maths, sanitisation, protocol handling - or **ours**. Take the library for generic problems. Write the code for our own.
