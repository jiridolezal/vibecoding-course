---
name: spfx-assets
description: Icons, images and media in an SPFx solution - where each kind of file belongs, the one-icon-set rule and the icon barrel, image formats and responsive sizing, and what must never be bundled. Use when adding an icon, image, logo, photo or video, when the user says "add an icon", "which icon", "this image is huge", "the bundle is full of assets", or when placing any binary file.
---

# spfx-assets

Assets are where SPFx bundles quietly get fat, and where a solution quietly stops matching its own theme.

## Where things go

| Kind | Location | Notes |
|---|---|---|
| Icon re-exports | `components/icons/index.ts` | The barrel. See below |
| Raw file imported by code, one web part | `src/webparts/<name>/assets/` | Bundled; travels in the `.sppkg` |
| Raw file imported by two web parts | `src/assets/` | Promote on the second consumer |
| File deployed to a SharePoint library | `sharepoint/assets/` | Provisioned, referenced by URL |

Never put a binary anywhere else in `src/`.

## Icons

We use **one icon library, and exactly one set within it.**

`react-icons` is a single dependency containing roughly twenty-five different visual languages. That makes the *dependency* unified, not the *design* - nothing stops one developer using `FiSearch` and another `MdSearch` in the same solution. So the set is a project-level decision, recorded in CLAUDE.md, and importing from any other subpath is a review failure.

**Choosing the set.** Prefer a permissive licence: Feather (`fi`), Lucide (`lu`) and Tabler (`tb`) are MIT or ISC. Avoid the Font Awesome sets - the free tier is CC BY 4.0 and carries attribution obligations that do not belong in a customer deliverable. Verify what your installed `react-icons` version actually ships before assuming a set exists.

### The barrel

Components never import from `react-icons` directly. They import from `components/icons`, which re-exports under semantic names:

```ts
// components/icons/index.ts
export {
  FiSearch as SearchIcon,
  FiX as CloseIcon,
  FiChevronLeft as PreviousIcon,
  FiChevronRight as NextIcon,
} from 'react-icons/fi';
```

```tsx
import { SearchIcon } from '../../components/icons';

<SearchIcon size={20} aria-hidden focusable={false} />
```

This buys three things for one file: the app never names a library icon, swapping sets later is a single-file edit, and the barrel is the exhaustive answer to "which icons does this solution use".

### Rules

- **Never pass a colour.** `react-icons` renders `fill="currentColor"`, so icons follow `var(--mc-color-*)` from CSS automatically. An icon given a hex colour cannot follow a customer's `createTheme()` override or the high-contrast layer, and it violates the no-hex rule.
- **Size through the `size` prop or CSS**, consistently. Pick a small scale (16 / 20 / 24) and stay on it.
- **`aria-hidden` and `focusable={false}` by default.** An icon beside a text label is decorative and must not be announced twice.
- **An icon that carries meaning alone** needs a name on the interactive element wrapping it, from `strings.X`. Never an unnamed icon-only button.
- **A one-off illustration** that is not part of the icon set - a logo, an empty-state graphic - is an asset, not an icon. It goes in `assets/` as an SVG file.

### Verify tree-shaking once, early

Build with three icons and note the bundle size, then add three more and check the delta. A small delta means tree-shaking is working. If the whole set is landing in the bundle, stop and reconsider before the solution grows.

## Images

**Format**

| Content | Use |
|---|---|
| Logo, illustration, anything vector | SVG |
| Photograph | WebP or AVIF, with a JPEG fallback if support matters |
| Needs transparency, not vector | PNG |
| Anything | Never BMP, never TIFF, never an uncompressed original |

**Size.** Never ship an image larger than twice its biggest rendered size. A 3000px hero scaled to a 400px card is 95% waste downloaded on every page load.

**Layout stability.** Always set `width` and `height`, or an `aspect-ratio`. SharePoint pages are a stack of web parts; an image that resizes after load shoves everything below it, and the shift is very visible.

**Responsive.** A web part renders in a one-third column as often as full width. When the same image serves both, use `srcset` and `sizes` rather than shipping the full-width asset to a narrow column.

**Loading.** `loading="lazy"` and `decoding="async"` for anything not visible on first paint. Not for the first image in view - lazy-loading that only delays it.

**Accessibility.** `alt` is required. Decorative images get `alt=""`, not a missing attribute and not a filename.

**Do not bundle what SharePoint already hosts.** Images in a site's asset library are referenced by URL. Bundling a copy means two sources of truth and a redeploy to change a picture.

**User photos** come from SharePoint or Graph, not from your own storage. Handle the missing-photo case with a designed fallback - initials or a placeholder icon - never a broken image.

## Fonts

**We do not ship custom fonts.** The theme tokens use a system font stack: it renders instantly, costs nothing, needs no licence, and looks native on every platform.

If a customer contract genuinely requires a brand typeface, that is a decision to record in `docs/decisions/` before anyone adds a file - it brings licensing, subsetting for Czech diacritics, weight count and load-performance questions that are all avoidable by default.

## Video and audio

**Never self-host video in an SPFx bundle.** Use Microsoft Stream, or an embed. A single video is larger than every other asset in the solution combined.

For any embedded player: `preload="none"`, a poster image, no autoplay with sound, and captions - captions are an accessibility requirement, not a nicety.

## Before you finish

- Every icon imported from `components/icons`, never from `react-icons` directly
- One icon set in the barrel
- No colour passed to an icon
- Every image has `alt` and explicit dimensions
- No font files in the repo
- No binary in `src/` outside an `assets/` folder
- Run the `bundle-auditor` agent if assets grew noticeably
