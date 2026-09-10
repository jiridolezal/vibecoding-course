---
name: spfx-setup
description: Turn a fresh clone of the SPFx template into a named solution - collects project details, replaces every template token, generates fresh GUIDs, renames files and folders, initialises git, verifies the build, then hands off to spfx-specs. Use on a fresh clone of the template, or when the user says "set up this project", "rename the solution", "initialise the repo", "start a new SPFx solution", or "I just cloned the template".
---

# spfx-setup

Run **once**, on a fresh clone. Turns the template into a named solution.

This template is token-based: every value that changes per solution is written as a name wrapped in double underscores, in file contents **and in file and folder names**. Nothing compiles until they are all replaced.

> Forgetting to regenerate GUIDs is the classic template bug: two solutions
> collide in the app catalog and the failure mode is baffling. The script below
> always generates fresh ones, which is most of why it exists.

## The thirteen tokens

These are **our** placeholders, and the only ones `--check` reports. Do not confuse them with the demo values the Yeoman generator left behind (`description`, `"Group Name"`, `"Description Field"`) - those are not tokens, they are scaffolding, and step 4 deals with them separately.

Tokens are `snake_case` so they are valid TypeScript and SCSS identifiers and legal in filenames on every OS. The three casings of the web part name are separate tokens because SPFx needs all three.

| Token | Value comes from | Example |
|---|---|---|
| `__name_full__` | asked | `Contoso Intranet Tools` |
| `__name_slug__` | derived, kebab-case of the name; `--name-slug` overrides | `contoso-intranet-tools` |
| `__description_short__` | asked | `Intranet helper web parts` |
| `__description_full__` | asked | `A set of web parts for the Contoso intranet.` |
| `__solution_id__` | **generated** GUID | new every run |
| `__feature_id__` | **generated** GUID, always different from the solution id | new every run |
| `__solution_sharepoint_url__` | asked; any `https://` is stripped | `contoso.sharepoint.com/sites/dev` |
| `__webpart_pascal__` | asked; must be PascalCase ASCII | `NewsFeed` |
| `__webpart_camel__` | derived; `--webpart-camel` overrides | `newsFeed` |
| `__webpart_slug__` | derived; `--webpart-slug` overrides | `news-feed` |
| `__webpart_title__` | asked; defaults to the PascalCase name | `News Feed` |
| `__webpart_description__` | asked | `Shows the latest intranet news.` |
| `__webpart_id__` | **generated** GUID | new every run |

Where they land: `package.json`, `.yo-rc.json`, `config/*.json`, `templates/README.md`, and everything under `src/webparts/<name>/` - file and folder names included. `.claude/` and `docs/decisions/` are deliberately skipped, because they describe the standard rather than this solution and name the tokens as examples.

The root `README.md` is not tokenised at all: it is the template's GitHub landing page, addressed to whoever is about to use the template. The initialiser replaces it with `templates/README.md`, which *is* tokenised and is the solution's own README, then removes the `templates/` folder.

`node scripts/init-template.js --check` is the authority on what is left.

## Step 0 - Install dependencies, and check setup has not already run

A fresh clone has no `node_modules`, and nothing works without it - not the build, not `tsc`, not eslint, not stylelint. Install first:

```bash
npm ci
node scripts/init-template.js --check
```

`OK  no template tokens remain` means setup has already run. Say so and stop, unless the user explicitly wants to redo it. Otherwise the output lists exactly what is still to be replaced.

`npm ci` is the once-per-clone install. Afterwards **every new dependency is `npm install <package>`**, which updates `package-lock.json` too - commit both, and run `npm ci` again after any pull that changed the lockfile. React Aria Components and `react-icons` are already declared, so most solutions never need to add one; read `dont-reinvent` before you do.

## Step 1 - Collect

Ask in **one** message, offering defaults inferred from the folder name. Do not invent answers; every one of these ends up in a customer-facing artefact.

| Need | Example | Notes |
|---|---|---|
| Solution display name | `Contoso Intranet Tools` | The slug is derived from the display name |
| Short description | `Intranet helper web parts` | One line, customer-facing |
| Long description | `A set of web parts for the Contoso intranet.` | |
| First web part, PascalCase | `NewsFeed` | camelCase and kebab-case are derived |
| Web part title | `News Feed` | Shown in the toolbox |
| Web part description | `Shows the latest intranet news.` | Also the default `description` property |
| Dev workbench site | `contoso.sharepoint.com/sites/dev` | **Required.** Stage 4 is impossible without it |
| Default locale | `cs-cz` | Goes in project choices; decides which locale files exist |
| Icon set / HTTP client | | Only if they differ from `.claude/rules/project-choices.md` |

The workbench site is not optional, however tempting it is to skip. Stage 4 - running the solution and looking at it - is what this standard uses instead of tests, and it needs a real SharePoint site the user can sign in to. If they do not have one yet, stop and tell them to create a site (or ask their SharePoint administrator for one) before continuing. Do not invent a URL and do not proceed with it blank.

## Step 2 - Run the initialiser

It replaces every token, renames the files and folders that carry one, generates three fresh GUIDs - solution, feature and web part - and installs `templates/README.md` as the solution's `README.md` over the template's landing page.

```bash
node scripts/init-template.js \
  --name-full "Contoso Intranet Tools" \
  --description-short "Intranet helper web parts" \
  --description-full "A set of web parts for the Contoso intranet." \
  --webpart-pascal NewsFeed \
  --webpart-title "News Feed" \
  --webpart-description "Shows the latest intranet news." \
  --sharepoint-url contoso.sharepoint.com/sites/dev
```

Optional overrides when a derived casing is wrong: `--name-slug`, `--webpart-camel`, `--webpart-slug`.

Then confirm nothing was missed:

```bash
node scripts/init-template.js --check
```

**Keep the three GUIDs it printed.** They go in the decision record in step 7.

## Step 3 - Finish the token work the script cannot

The script is a text substitution. Three token-adjacent things need judgement:

- **`README.md`** - the initialiser has already replaced the template's landing page with `templates/README.md`, the solution's own README, and deleted the `templates/` folder. Check that happened (the run log says so, and the file should now open with the solution name rather than "SPFx web part template"). **Leave the rest of it alone.** Four sections are marked `(keep current)` and are empty on purpose: nothing has been built yet, so anything written here now would be invented. `spfx-handoff` fills them in at the end of the first iteration, when the answers are known. Do not pad the placeholder paragraph into something that sounds finished.
- **The component manifest** - check `preconfiguredEntries` carries no tenant URL, site URL, list GUID or customer name. A generic web part description is fine; anything environment-specific is not.
- **`.claude/rules/project-choices.md`** - record the icon set, HTTP client and default locale for this solution. The initialiser does not touch anything under `.claude/` and `--check` cannot see a skip here, so this one is on you. **This is the only file under `.claude/` that a project edits**, so drift from the standard stays visible.

## Step 4 - Deal with the Yeoman demo scaffolding

**None of this is a token, and `--check` will report a clean repo with all of it still in place.** It is the demo web part the SharePoint generator scaffolds, which the template kept so that a fresh clone renders *something* in the workbench on the first run. It is deliberately not removed by the initialiser, because what replaces it depends on specs that do not exist yet.

Fix now, because it is customer-facing or misleading:

| Where | What is there | Do |
|---|---|---|
| `loc/en-us.js`, `loc/mystrings.d.ts` | `BasicGroupName: "Group Name"`, `DescriptionFieldLabel: "Description Field"`, `PropertyPaneDescription: "Description"` | Rewrite the values to name what this web part actually configures. Keep the keys until step 3 of the lifecycle replaces the property |
| `loc/*.js` | only `en-us.js` exists | If the locale from step 1 is not `en-us`, create that file too. `en-us.js` always stays as SharePoint's fallback, every key in every file - see `spfx-localization` |
| `<Name>WebPart.manifest.json` | `"officeFabricIconFontName": "Page"` | Pick an icon that suits the web part |

Leave in place, and **say so explicitly in the handover**, because stage 1 to 3 decides what replaces it:

- the `description` property on `I<Name>WebPartProps`, its `PropertyPaneTextField("description")` field, and its default in `preconfiguredEntries[].properties`
- the `userDisplayName` prop and the `SignedInAsLabel` / `WebPartTitle` strings
- the demo markup in `components/<Name>.tsx` - the `<h1>` and two `<p>` elements

The first real property replaces the demo one. When it does, that is a property shape change on a web part that may already be on a page, so it needs a `dataVersion` bump - see `spfx-property-pane`. Doing it before there is a spec means doing it twice.

Do **not** delete `.yo-rc.json`. It records which generator version produced the solution, and `spfx-doctor` reads it.

## Step 5 - Git

The workbench URL collected in step 1 has already been written into `config/serve.json` by the initialiser, and that is the **only** place it lives. `serve.json` is SPFx's own dev-server config, is committed by convention, and is useless empty - a deliberate carve-out from invariant 8, not an oversight. `spfx-preview` reads it to work out where to open the workbench.

Nothing else may hold a tenant URL, site URL or list GUID. In particular **a tenant URL never enters `.claude/settings.json`**, which is committed. If a per-developer value ever genuinely needs storing, `.claude/settings.local.json` is gitignored and is the place for it - but do not create that file with empty placeholders nothing reads.

The app catalog URL is not collected here: it is needed once per release, and `spfx-ship` asks for it then.

If this is not a git repository yet, initialise it. The `Stop` verify gate reads `git diff` to decide what changed and silently does nothing without one, so skipping this quietly disables the gate:

```bash
git init -b main
```

The first commit comes at the end, in step 6, once the build has been proved. `main` is the only long-lived branch in this standard - see `.claude/rules/conventions.md`.

## Step 6 - Verify

**Order matters here.** `tsc` needs `temp/sass-ts`, the `*.module.scss` typings Heft generates during a build. Before the first build it does not exist, and `npm run verify` fails with `TS2307 Cannot find module './Foo.module.scss'` on every stylesheet import - a real-looking error that has nothing to do with anything. Build first, then verify:

```bash
npx heft build                   # also generates temp/sass-ts
npm run verify                   # tsc --noEmit + eslint + stylelint
```

Both must pass before handing over. If `heft build` fails on a dev certificate or a Node version, run `spfx-doctor` rather than guessing. Do not "fix" the TS2307 errors if they appear - they mean the build has not run yet.

## Step 7 - Record, commit and hand off

Write a decision record at the next free number in `docs/decisions/` - the template ships `0000` through `0002`, so a fresh solution writes `docs/decisions/0003-project-setup.md`. It holds: solution name, customer, date, the three GUIDs the script generated, the first web part, the workbench site, and the icon set, HTTP client and locale chosen. This both stops the skill re-running and answers "which GUID is ours" a year from now.

Commit the initialised solution on `main` - this is the one time committing directly to `main` is right, because it *is* the starting point:

```bash
git add -A && git commit -m "Initialise solution from SPFx template"
```

Then tell the user what happens next, briefly:

- `/spfx-help` lists everything available
- `spfx-specs` is stage 1 - what are we building, and for whom
- `spfx-architecture` turns those specs into a plan with diagrams
- `spfx-prototype` is stage 2 - agree the design before writing SPFx code

Offer `spfx-specs` and stop. Do not start writing feature code in the same turn as setup.
