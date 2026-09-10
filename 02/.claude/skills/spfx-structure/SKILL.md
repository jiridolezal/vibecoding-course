---
name: spfx-structure
description: Decide where a file belongs in an SPFx solution and what to name it - the folder contract, the layering rules, naming conventions for types, providers, data functions and components, and when to promote something to a shared folder. Use when creating any new file, when the user asks "where does this go", "how should I structure this", "what do I name it", when adding a web part or extension, or when a file feels like it is in the wrong place.
---

# spfx-structure

Answers exactly one question: **where does this go, and what is it called?** How to write providers is `spfx-data`. How to write components is `spfx-ui`.

## The layering

```
<Name>WebPart.ts        wiring only. Properties in, ContextWrapper out.
    |
<Name>ContextWrapper.tsx    composes providers, bootstraps URL params
    |
components/             the UI tree
    |  uses
providers/              React context: state, orchestration, lifecycle
    |  calls
data/                   async fetch + map raw response to domain model
    |  returns
types/                  raw shapes, domain models, interfaces
```

Dependencies point **downward only**. `data/` never imports a component. `utils/` never imports anything from `providers/` or `data/`.

## Where things go

| It is... | It goes in | Notes |
|---|---|---|
| The web part class | `src/webparts/<name>/` | No logic. Ever. |
| Provider composition | `src/webparts/<name>/<Name>ContextWrapper.tsx` | One per web part |
| React context + state | `providers/` | One file per domain concern |
| Anything that does HTTP | `data/` | The only place a client is imported |
| A pure function | `utils/` | No JSX, no fetch, no context |
| A function returning JSX | `components/` | It is a component. Not a util. |
| A type or interface | `types/` | Group by domain in subfolders |
| An icon | `components/icons/index.ts` | Re-export only. See `spfx-assets` |
| A raw image, svg or media file | `assets/` | Never loose in `src/` |
| A custom property pane field | `propertyPane/` | See `spfx-property-pane` |
| Strings | `loc/` | See `spfx-localization` |
| Colours, fonts, spacing | `src/theme/` | Never anywhere else |

## One component per file

**A file exports one component.** Not two, not a component and its three little helpers. If a component is only ever rendered by its neighbour, it still gets its own file - that is what makes it findable, movable and reusable, and it is the difference between a solution someone can work on and a pile of 600-line files.

- The file is named after the component, and the component is named after the file. `BranchCard.tsx` exports `BranchCard`.
- A sub-part that exists only to break up a long render is still a component. Give it a file: `BranchCardHeader.tsx`, next to `BranchCard.tsx`.
- The exception is a tiny presentational fragment used once in the same file and never exported - a `<Row>` of two lines. The moment it is exported, or grows, or a second file wants it, it moves out.
- **If a file is getting long, that is the signal, not a style preference.** Past roughly 200 lines a component is nearly always doing two jobs; past 300 it certainly is. Split by responsibility - the list, the row, the empty state - not by line count.

Same idea one level down: a component's own styles live in its `*.module.scss` sibling, not in a shared stylesheet that every component reaches into.

## Grouping components

`components/` is not one flat folder, and it is not a mirror of the render tree either. Group by **what the thing is**, in folders the project actually needs:

```
components/
  shared/          used in more than one place in this web part
  dialogs/         every modal and its content
  branchChart/     one feature, its own subtree
  icons/           re-export barrel, see spfx-assets
```

`shared/`, `dialogs/`, `layout/`, `forms/` - take what the solution needs and leave the rest. The names are the project's to choose; what is not negotiable is that a reader can guess where something lives from what it does.

## Sharing

Promote on the **second** consumer, never in anticipation of one.

- Used by two components in one web part -> `components/shared/`
- Used by two web parts -> `src/components/`, `src/utils/`, `src/types/`, `src/assets/`
- Used once -> leave it where it is

Promoting is cheap because every component is already its own file with its own styles. That is most of why the rule above exists.

**Look before you write.** A new component that duplicates one already in `shared/` is worse than no component - two things now drift apart. Check `components/shared/`, `src/components/` and `dont-reinvent` before adding, and when you find a near-match, extend it with a prop rather than copying it.

## Naming

The naming table lives in `.claude/rules/conventions.md`, which is loaded every session. Read it there rather than from a copy that can drift.

The one thing worth repeating: `TReceivedBranch` is what SharePoint returns, `BranchItem` is what our code works with, and the mapping between them happens in `data/` - never in a component and never in a provider.

## Depth

Cap nesting under `components/` at three levels. Below that, flatten and let the folder name carry the context. Deep trees mirroring the render hierarchy produce `../../../../` imports and make a component impossible to move.

Bad:  `components/branchChart/regionContainer/branchCardContainer/branchCard/branchCardInfoSegment/` Good: `components/branchChart/branchCard/BranchCardInfoSegment.tsx`

## Adding a web part to an existing solution

1. Create `src/webparts/<name>/` with the full folder set
2. Register the entrypoint and manifest in `config/config.json`
3. Decide the bundle: separate bundles load independently and keep pages fast; one shared bundle is only right when the parts are always used together
4. New GUID in the manifest - never copy another component's id
5. Its own `loc/` folder

## Before you finish

- Nothing outside `data/` imports an HTTP client
- No `.tsx` file in `utils/`
- No component imports another web part's internals
- No import path with more than three `../` segments
