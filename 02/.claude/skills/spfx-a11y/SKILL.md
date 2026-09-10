---
name: spfx-a11y
description: Check accessibility of the running solution - static lint with jsx-a11y, an axe-core audit against the live web part in the workbench, and the manual checks tools cannot do. Use when the user asks about accessibility, a11y, WCAG, screen readers, keyboard navigation, contrast, or before shipping a release.
---

# spfx-a11y

Three layers. Run the cheap ones first.

## 1 - Static

```bash
npx eslint src
```

`eslint-plugin-jsx-a11y` catches the common structural failures: a clickable `div` with no keyboard handler, an image with no `alt`, a form control with no label, a positive `tabindex`. Fix these before running anything else - they are also the cheapest to fix.

## 2 - Runtime audit with axe

React Aria gives correct roles and keyboard behaviour, but it cannot know whether your labels are meaningful or your palette has enough contrast.

1. Get the solution running and open in the workbench - see `spfx-preview`
2. Inject `axe-core` from cdnjs into the page
3. Run it scoped to the web part's DOM element, not the whole page - the rest is SharePoint's chrome and not ours to fix
4. Report violations grouped by impact: critical, serious, moderate, minor

Re-run after any theme change. A customer's brand colour can quietly drop text below 4.5:1.

## 3 - Manual

What neither tool can check:

- **Keyboard only.** Tab through the whole web part. Every interactive element reachable, focus always visible, no trap, dialogs return focus on close
- **Labels read sensibly out of context.** "Open" is useless; "Open branch detail for Brno" is not. Labels come from `strings.X`
- **Colour is never the only signal.** A red border alone does not communicate an error
- **Zoom to 200%.** Text reflows, nothing clipped, nothing overlapping
- **Reduced motion.** Animations respect `prefers-reduced-motion`

## Report

Group by severity, name the file and line, and say what to change. Fix what is clearly wrong; raise anything that needs a design decision rather than guessing at intent.
