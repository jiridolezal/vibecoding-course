# Engineering principles

The invariants in `CLAUDE.md` say what this solution may not do. These say how to decide everything the invariants do not cover. They are tie-breakers, not trump cards: an invariant beats a principle, and a principle beats a preference.

Each one is written in terms of this codebase, because a generic list of acronyms changes nobody's code.

## KISS - the simplest thing that renders correctly

The reader of this code is a developer six months from now with no context. Prefer the boring construction: a `map` over a reduce, an early return over a nested ternary, three obvious components over one clever configurable one. If explaining a piece of code takes longer than rewriting it simply, rewrite it.

Cleverness has a cost that lands on someone else. Complexity that the specs actually demand is fine; complexity you introduced to feel good about the solution is not.

## DRY - on the second occurrence, not the first

Duplication is a problem when the same **knowledge** lives in two places, so that changing it means remembering both. Two functions that happen to look similar but answer to different requirements are not duplication, and merging them couples two things that will diverge.

So: write it twice, extract on the third. The one exception is knowledge that is already load-bearing - a field's internal name, a token, a URL - which has exactly one home from the start. This is the same rule as `spfx-structure`'s "promote on the second consumer", seen from the other end.

## YAGNI - build what the specs asked for

No provider for data no view shows. No property nobody sets. No `variant` prop with one variant. No abstraction layer over `SPHttpClient` in case we swap it, because we will not, and `docs/decisions/` records that.

Every speculative feature is code that must be read, built, shipped and kept working, in exchange for a possibility. When something genuinely might be needed later, the answer is a line in `docs/decisions/`, not an interface.

## Single responsibility - one file, one job

A file has one reason to change. This is why the layering exists: `data/` changes when the API changes, `providers/` when orchestration changes, `components/` when the design changes. A component that fetches its own data has two reasons to change and will be edited by two people for two reasons.

The practical test is the sentence: if describing what a file does needs an "and", it is two files. One component per file - `spfx-structure` has the mechanics.

## Interface segregation - narrow props

A component receives what it renders, not the object it came from. `<BranchCard branch={branch} />` where the card shows two fields makes the card depend on every field, so a schema change touches components that display none of it.

Pass the two fields. Props interfaces stay small, and a small props interface is what makes a component reusable and testable by eye.

## Open/closed - extend by prop, not by editing

A shared component grows by gaining a prop with a sensible default, never by gaining another `if (context === 'dialog')`. The second variant is where a shared component starts becoming a switchboard that nobody dares touch.

If a new consumer needs behaviour that contradicts the existing one, that is two components, not one with a mode flag.

## Liskov substitution - a wrapper must honour its contract

The concrete form of this here: **our wrapper around a React Aria component must be usable everywhere the React Aria component is.** Spread the rest of the props, forward the ref, and do not swallow anything.

```tsx
// Honours the contract - everything RACButton accepts still works
export const Button = forwardRef<HTMLButtonElement, IButtonProps>(
  function Button({ variant = 'primary', ...props }, ref) {
    return <RACButton {...props} ref={ref} data-variant={variant} />;
  }
);
```

Three ways to break it, all of which typecheck:

- **Dropping `...props`**, so `onPress`, `isDisabled` and `aria-label` silently do nothing at the call site
- **Not forwarding `ref`**, so focus management and overlay positioning break in ways that look like React Aria bugs
- **Taking `className` as a string** and passing it straight through, which replaces `.react-aria-Button` and the focus ring - invariant 10, and `cx()` is the fix

A component that accepts a prop and ignores it is worse than one that does not accept it, because the caller has no way to find out.

## Dependency inversion - dependencies point downward

`components/` depends on `providers/`, which depends on `data/`, which depends on `types/`. Never upward, never sideways between web parts. A component knows it has `items`, `isLoading` and `error`; it does not know they came from SharePoint.

This is what makes a view renderable in a prototype, a provider replaceable, and a data function readable on its own. It is enforced by lint for the HTTP boundary and by review for the rest.

## Composition over inheritance

Function components and props. No class components outside the SPFx web part class itself, which the framework requires, and no base component that others extend. Shared behaviour is a hook or a wrapper component, both of which compose without coupling.

## Least astonishment

A reader guessing where something lives, or what a name means, should be right. That is the whole purpose of the naming table in `conventions.md` and the folder contract in `spfx-structure` - not tidiness, predictability. A correctly named thing in the expected folder costs nobody any attention.

## When two principles disagree

They will. DRY pulls toward extraction, KISS pulls against it; YAGNI pulls against open/closed. The order to resolve them in:

1. An invariant in `CLAUDE.md` - never negotiable
2. Accessibility and correctness - a broken keyboard path is not a trade-off
3. Clarity for the next reader
4. Everything else

If a decision was genuinely close, that is what `docs/decisions/` is for. One paragraph now saves the same argument being had again in six months.
