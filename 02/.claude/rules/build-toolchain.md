# Build toolchain

This solution builds with **Heft**. SPFx changed build systems at v1.22 and we do not carry the old one - there is no `gulpfile.js`, gulp is not installed, and a gulp command in this repo is a mistake, not a fallback.

| Task | Command |
|---|---|
| Install dependencies | `npm ci` once per clone; `npm install <pkg>` per new dependency |
| Dev server + workbench | `npx heft start` |
| Trust dev certificate | `npx heft trust-dev-cert` |
| Production bundle | `npx heft build --production` |
| Package | `npx heft package-solution --production` |
| Clean | `npx heft clean` |

`npm start`, `npm run verify` and `npm run build` in `package.json` wrap the ones used most; prefer those.

Two things that cost a session each:

- **The dev server never exits.** Start it in the background and never block on it.
- **`tsc` needs one build first.** Heft generates the `*.module.scss` typings into `temp/sass-ts`, which the rig's tsconfig lists in `rootDirs`. On a fresh clone `npm run verify` therefore reports `TS2307 Cannot find module './Foo.module.scss'` on every stylesheet import. Run `npx heft build` once; do not "fix" the imports.

Never assume an SPFx, Node, React or TypeScript version - read them from the repo, or run `spfx-doctor`.
