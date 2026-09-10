---
name: spfx-ui
description: Write components for an SPFx solution using React Aria Components and the project design tokens - component shape, the cx helper, styling through data attributes, theming with createTheme, the four required UI states, portals and z-index inside SharePoint, memoization, and accessibility. Use when creating or changing any component, styling anything, asking about colours or fonts, adding a dialog or overlay, or when the user says "build the UI", "style this", "make it look right", or "the popover is behind the SharePoint header".
---

# spfx-ui

We build on **React Aria Components** for behaviour and accessibility, and style them ourselves with SCSS modules driven by design tokens.

## Component shape

Function components. Props interface `I<Name>Props`. Export named, not default.

```tsx
export interface IBranchCardProps {
  branch: BranchItem;
  onSelect: (branch: BranchItem) => void;
}

export const BranchCard = ({ branch, onSelect }: IBranchCardProps): JSX.Element => {
  ...
};
```

Wrapping a React Aria component: forward the ref, pass a `data-*` attribute for the variant, and let SCSS do the rest.

```tsx
import { Button as RACButton } from 'react-aria-components';
import type { ButtonProps as RACButtonProps } from 'react-aria-components';

export type ButtonVariant = 'primary' | 'secondary' | 'tertiary' | 'destructive';

export interface IButtonProps extends RACButtonProps {
  variant?: ButtonVariant;
}

export const Button = forwardRef<HTMLButtonElement, IButtonProps>(
  function Button({ variant = 'primary', ...props }, ref) {
    return <RACButton {...props} ref={ref} data-variant={variant} />;
  }
);
```

Style states through the attributes React Aria already sets - `[data-hovered]`, `[data-pressed]`, `[data-focus-visible]`, `[data-disabled]`, `[data-selected]`. Do not track hover or focus in React state.

## Hover must not move the layout

**An element's box is the same size hovered as not hovered.** This is the rule that separates a solution that feels built from one that feels generated.

The failure is familiar: a card scales up on hover, so the grid row grows and everything below it shifts down; a button gains padding, so the toolbar reflows; a label goes bold, so the text rewraps. Move the mouse across a list and the page ripples. Users cannot name it, but they feel it, and it is the most recognisable signature of a UI nobody looked at.

Never transition these on hover, focus or press - each one resizes the box and reflows its neighbours:

`width` · `height` · `padding` · `margin` · `font-size` · `font-weight` · `border-width` · `letter-spacing` · `gap`

Use instead, none of which affect layout:

| Want | Use |
|---|---|
| Lift, grow, nudge | `transform: scale()` / `translateY()` - it paints outside the box without changing it |
| Depth | `box-shadow` |
| Emphasis | `background-color`, `color` |
| A ring or edge | `outline` and `outline-offset`, never `border` |

Two corollaries worth knowing:

- **A border that appears on hover must exist unhovered**, as `border-color: transparent`, or the element jumps by its width the moment the pointer arrives. Same for `outline` if you give it a width.
- **Bold on hover needs the space reserved.** Simplest is not to do it; if the design insists, `text-shadow` fakes the weight without remeasuring the text.

```scss
.card {
  border: var(--mc-border-width) solid transparent;  // reserved, not added on hover
  box-shadow: var(--mc-shadow-sm);
  transition: transform 140ms ease, box-shadow 140ms ease;

  &[data-hovered] {
    transform: translateY(-2px);                     // not width, not padding
    box-shadow: var(--mc-shadow-md);
  }
}
```

Keep transitions at 120-180ms and name the properties - never `transition: all`, which animates layout properties the moment someone adds one. `_reset.scss` already honours `prefers-reduced-motion`, so a user who asked for stillness gets it without anything extra here.

`spfx-preview` checks this by hovering everything and watching for movement.

## Never pass a plain className to a React Aria component

React Aria resolves `className` as `computed ?? defaultClassName`. A plain string **replaces** `.react-aria-Button` and every rule hanging off it, including the focus ring. TypeScript accepts it, the control still looks roughly right, and you have a silent WCAG 2.4.7 failure that nobody notices until someone tabs to it.

Use `cx` from `src/utils/cx.ts`, which returns the function form:

```tsx
<Button className={cx(styles.myButton)} />
<Button className={cx(styles.chip, isOn && styles.on)} />
```

## Colours, fonts, spacing

**One source of truth: `src/theme/`.** A hex literal anywhere else is a defect.

| File | Holds |
|---|---|
| `_tokens.scss` | The full token set, `--mc-*` custom properties |
| `theme.ts` | This project's palette - the one file you edit to retune a brand |
| `index.ts` | `createTheme()`, `tokenVars`, the `Theme` type |
| `theme.global.scss` | The single global stylesheet, imported once by the ContextWrapper |
| `components/` | The React Aria component styles, vendored |

**Switching a component's styles on is one line.** `theme.global.scss` carries a commented `@use 'components/<name>';` per control. Uncomment it the first time the solution renders that control, and leave the rest commented so the bundle stays proportional to what the solution actually uses.

That file's extension is load-bearing. Every other `.scss` in an SPFx solution compiles as a CSS module with hashed class names, so moving these styles into a plain `.scss` leaves `.react-aria-Button` matching nothing and every control unstyled. Only `*.global.scss` is compiled as plain CSS. Your own component styles stay `*.module.scss` siblings.

The palette is applied once, on the outermost element of the ContextWrapper:

```tsx
<div className="mc-theme" style={projectThemeStyle}>
  ...
</div>
```

A web part cannot claim `:root`, which is why `.mc-theme` exists as a parallel scope. Everything inside inherits the overrides, so the same build serves different customers.

In SCSS, always `var(--mc-color-text)`, never `#0f172a`. Never define a token as `var()` of another token - a custom property holding a `var()` resolves on the element that declares it, so a runtime override arrives too late and the derived token silently keeps the old value. Give the consuming rule a `var(--specific, var(--general))` fallback instead.

We do **not** inherit SharePoint's theme. Customers have their own brand.

## The four states

Every view that loads data renders all four, and the empty and error states are designed, not an afterthought:

| State | Requirement |
|---|---|
| Loading | Skeleton or spinner with an accessible label |
| Empty | Explains why it is empty and what to do next |
| Error | Says something failed, offers retry. Never a blank div |
| Populated | The actual content |

A fifth applies when the web part is unconfigured: show a configuration placeholder, not a broken view.

## Portals, overlays and SharePoint

React Aria renders overlays through a portal into `document.body`, outside the web part's DOM. Two consequences:

- The theme wrapper does not reach them. Configure the portal container, or apply `.mc-theme` to the overlay provider as well.
- SharePoint chrome has its own stacking. Use `--mc-z-overlay` and `--mc-z-tooltip`; if a popover hides behind the header, fix the scale in `_tokens.scss` once rather than adding a `z-index: 9999` at the call site.

## Icons, images and fonts

See `spfx-assets`. The short version: icons are imported from `components/icons` and never given a colour, so they follow the theme; no binary sits loose in `src/`; and we ship no custom fonts.

## Effectiveness

Optimise when there is a reason, not by reflex.

- `React.memo` on a component rendered many times in a list, whose props are stable. Pointless on a component that renders once.
- `useCallback` on handlers passed into a memoized child or an effect dependency array. Pointless otherwise.
- `useMemo` for genuinely expensive derivation - filtering thousands of rows, not concatenating two strings.
- The real wins are elsewhere: fetch less (`$select`), render less (paginate or virtualise long lists), load less (lazy-load a dialog's contents).

## Accessibility

React Aria handles roles, keyboard interaction and focus management. What is still on you:

- Icon-only controls need an accessible name, from `strings.X`
- Images need `alt`, decorative ones `alt=""`
- Never `<div onClick>`. If it is clickable it is a `Button` or a `Link`
- Colour is never the only signal - pair it with text or an icon
- Contrast survives theme overrides. Re-check after changing the palette

## Before you finish

- No hex literal outside `src/theme/`
- No user-facing string literal - always `strings.X`
- No plain string `className` on a React Aria component
- All four states implemented
- No `<div onClick>`
