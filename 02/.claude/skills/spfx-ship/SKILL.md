---
name: spfx-ship
description: Package and release an SPFx solution - production bundle, sppkg, app catalog deployment, permission approval, tagging and release notes. Use when the user says "ship it", "deploy", "package", "release", "build for production", "make the sppkg", or "upload to the app catalog".
---

# spfx-ship

Release. There is no pipeline yet, so this is a documented manual procedure. Do not skip the verification stage to get here.

## Step 1 - Preconditions

- `spfx-review` passed, and `spfx-security` run if this release touches permissions, an API call or rendered HTML
- Version bumped via `spfx-version`
- Working tree clean, on `main`, with the feature branch already merged
- `CHANGELOG.md` updated

## Step 2 - Production build

```bash
npx heft clean
npx heft build --production
npx heft package-solution --production
```

`npm run build` does the last two in one command.

**`--production` matters.** Without it the package points at `localhost:4321` and the solution silently does nothing once deployed - the web part appears in the toolbox and renders nothing, which reads as a code bug and is not one.

The package lands at the `paths.zippedPackage` location in `config/package-solution.json`, which is resolved relative to `sharepoint/` - so the default `solution/<name>.sppkg` is really `sharepoint/solution/<name>.sppkg`.

## Step 3 - Sanity checks before upload

- The `.sppkg` exists and its timestamp is from this build
- The solution version inside matches what you intended
- Bundle size is not wildly larger than the last release - if it is, run the `bundle-auditor` agent before shipping
- `includeClientSideAssets` is `true` unless assets are hosted elsewhere
- Lint clean, including the `no-console` rule that catches leftover logging

## Step 4 - Deploy

Upload the `.sppkg` to the app catalog:

- **Tenant app catalog** - available across the tenant
- **Site collection app catalog** - scoped to one site

Which one is a governance decision, not a default. Record it in `docs/decisions/` the first time.

If `skipFeatureDeployment` is `false`, the solution must be added to each site explicitly.

## Step 5 - Permissions

If `webApiPermissionRequests` changed, a tenant administrator must approve the new scopes in the SharePoint admin centre. **The solution will fail silently for every user until they do.**

Tell the user exactly which scopes need approving, and record them in `docs/permissions.md`.

## Step 6 - After deployment

- Load a real page and verify the deployed version, not the local one
- Check an existing placed instance still works - property migrations bite here
- Tag the release and write release notes from `CHANGELOG.md`
- If anything is wrong, the rollback is redeploying the previous `.sppkg`; make sure it still exists before you need it

## When a pipeline arrives

Steps 2 and 3 become CI. Steps 4 and 5 stay manual - deployment and permission grants are decisions, not automation.
