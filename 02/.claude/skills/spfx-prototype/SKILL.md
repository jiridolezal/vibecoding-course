---
name: spfx-prototype
description: Stage 2 of the lifecycle - build a static HTML prototype of the UI using the project's real compiled design system and React Aria markup, and publish it as a shareable Artifact for sign-off, before any SPFx code is written. Use after specs and architecture are agreed, or when the user says "prototype", "mockup", "design it first", "what will it look like", "show the customer", or wants a design approved before implementation.
---

# spfx-prototype

Stage 2. Design gets signed off **before** anyone waits on the dev server.

Iterating on visuals inside SPFx is slow - bundle, auth, workbench, repeat. A static page renders instantly, and it can show every state side by side, which a running web part cannot.

## The one rule that makes this worth doing

**The prototype uses the project's real CSS, not an approximation of it.**

A prototype styled with hand-written CSS that looks like React Aria gets signed off and then does not match what ships, and every difference becomes an argument after the code exists. So compile the actual design system and inline it:

```bash
node scripts/build-prototype-css.js button textfield select dialog --out temp/prototype.css
```

That emits the real `--mc-*` tokens from `src/theme/_tokens.scss`, the real reset, and the real `.react-aria-*` rules from `src/theme/components/`. Pass the component names the design needs; pass none for all forty. Then paste the result into a single `<style>` block in the prototype and write markup with the class names those rules target:

```html
<div class="mc-theme">
  <button class="react-aria-Button" data-variant="primary">Ulozit</button>
</div>
```

`.mc-theme` is the wrapper the tokens are scoped to - the same one `<Name>ContextWrapper.tsx` applies at runtime - so the prototype must have it on an ancestor or every token falls back.

## Colour is collected here, before anything is drawn

**This is the stage where the customer's colours enter the solution.** Nothing earlier asks for them: `src/theme/theme.ts` ships with every override commented out, so a prototype built without this step shows the design system's defaults and gets signed off in the wrong colours.

So, first job, before compiling anything:

1. Ask for the brand colours - primary, and its hover/pressed shade if they have one. A hex, a brand guideline PDF or an existing site is all fine. If the customer has no brand of their own, say the defaults are being used and move on; that is a real answer, not a gap.
2. Write them into `src/theme/theme.ts` as `projectTheme` overrides. Never a hex anywhere else, and never a token value edited inside `_tokens.scss`.
3. Check the contrast of anything you overrode. A default token has been checked for WCAG AA; the moment it is overridden that becomes ours, including under `prefers-contrast: more`. `spfx-a11y` has the thresholds.

`createTheme()` applies those overrides at runtime, so the **compiled CSS will not contain them** - `build-prototype-css.js` reads `_tokens.scss`, not `theme.ts`. Carry them over by hand: read `theme.ts` and put every overridden token as an inline `style` on the prototype's `.mc-theme` wrapper.

```html
<div class="mc-theme" style="--mc-color-primary: #7a1f2b; --mc-color-primary-hover: #5e1721;">
```

Get this wrong and the prototype is a picture of a different product. It is two minutes and it is the whole point of stage 2.

## Rules

- **One self-contained HTML file.** No build step, no external dependency, no framework. Vanilla JS only where a screen genuinely cannot be judged without interaction - a tab switch, opening a dialog.
- **React Aria markup and class names**, taken from the compiled CSS. Translating to `react-aria-components` in stage 3 is then mechanical: `.react-aria-Select` becomes `<Select>`, and the styling already works.
- **Every state from `docs/specs.md`, labelled on the page**: loading, empty, error, no permission, populated. Side by side, all visible at once - this is the thing the running web part cannot show and the main reason to do this.
- **Realistic data** drawn from the specs. Never lorem ipsum, and never a real customer's personal data.
- **Show it in a one-third column too.** SharePoint web parts live in narrow columns as often as full width, and a design that only works at 1200 px is not signed off. Two frames on the page, or a width control.
- **No colour that is not a token.** If the design needs a colour the tokens do not have, that is a `theme.ts` change to raise, not a hex in the prototype.

## Process

1. Read `docs/specs.md` and `docs/architecture.md`. If specs are missing, run `spfx-specs`; if architecture is, run `spfx-architecture`.
2. Collect the brand colours and write `theme.ts`, as above. Before compiling, not after.
3. Decide which React Aria components the design needs, and compile their CSS with the command above.
4. Load the `artifact-design` skill.
5. Write the page to `docs/prototypes/<feature>.html`.
6. Publish it as an Artifact and hand the user the link to share.
7. **Record which components were used** at the top of the file as an HTML comment. Stage 3 has to uncomment exactly those `@use` lines in `src/theme/theme.global.scss`, and this is the list.
8. Record what was approved, and any change requests, as a short entry in `docs/decisions/`.

## After sign-off

The approved prototype is the implementation brief for stage 3. Reference it by path when building components, and keep it - `spfx-review` checks the built UI against it.

First job in stage 3: uncomment the `@use` lines for the components listed in step 7. Until they are uncommented, every React Aria control renders unstyled and the built UI looks nothing like the approved design. That failure looks like a theming bug and is not one - see `.claude/CLAUDE.md`.
