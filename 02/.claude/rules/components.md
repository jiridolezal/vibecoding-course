---
paths:
  - "src/**/*.tsx"
  - "src/**/*.module.scss"
  - "src/utils/**"
---

# Component rules

The invariants are in CLAUDE.md and most of them fail the lint gate. This file is the elaboration - the *why*, and the cases lint cannot see.

- **A hex here cannot follow a customer's `createTheme()` override** or the high-contrast layer. That is why colour comes from `var(--mc-color-*)`, defined only in `src/theme/`. stylelint enforces it.
- **Strings go through `strings.X` even on a Czech-only project**, because retrofitting localization across a finished solution is a job nobody ever does. No lint rule can tell a user-facing literal from a `data-*` value, so this one is on you and on review.
- **A function returning JSX is a component, not a util.** It belongs in `components/`, whatever it feels like.
- **One component per file, named after the file.** A file that exports two components is two files that have not been separated yet, and neither can be reused or moved. A long file is the symptom, not the problem: past ~200 lines a component is doing two jobs. Split by responsibility. The folder contract and the grouping (`shared/`, `dialogs/`, and whatever else the project needs) are in `spfx-structure`.
- **Reuse before you write.** Check `components/shared/` and `src/components/` first, and extend what is there with a prop rather than copying it. Two near-identical components drift apart, and the second one is always the one nobody updates.
- **All four states rendered** wherever data loads: loading, empty, error, populated. An unconfigured web part shows a configuration placeholder instead. Empty and error are designed, not an afterthought.
- **Never `<div onClick>`.** If it is clickable it is a `Button` or a `Link` - otherwise it is unreachable by keyboard and invisible to a screen reader.
- **Icons come from `components/icons`**, never from `react-icons` directly, and are never passed a colour - a coloured icon cannot follow the theme. Icon-only controls carry a label from `strings.X`.
- **Never pass a plain string `className` to a React Aria component.** React Aria resolves `className` as `computed ?? defaultClassName`, so a plain string *replaces* `.react-aria-Button` and every rule hanging off it, including the focus ring. TypeScript accepts it, it still looks roughly right, and it is a silent WCAG 2.4.7 failure. Use `cx()`.

Procedure and examples: `spfx-ui`, `spfx-assets`.
