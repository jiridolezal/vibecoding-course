---
name: spfx-doctor
description: Preflight check of the local SPFx development environment - Node, npm, Heft, TypeScript, dev certificate - against the SPFx version this repo actually declares. Use before a first build, when npm install fails, when the dev server will not start, when the user says "it does not build", "environment issue", "wrong node version", or when you need to know which SPFx version this repo targets.
---

# spfx-doctor

Twenty wasted minutes usually trace back to a five-second check. **Read requirements from the repo. Never assume a version.**

## Step 1 - What does this repo target?

Read `package.json` and `.yo-rc.json`. Note: `@microsoft/sp-core-library` version (this is the SPFx version), `react`, `typescript`, and the `engines.node` range.

We build with **Heft**. Confirm `heft` is in `package.json` scripts and say so in the report. If it is not — if this is an older solution predating SPFx 1.22 that has not been migrated — stop and say that rather than improvising: nothing else in this standard applies to it.

If CLI for Microsoft 365 is installed, `m365 spfx doctor` cross-checks the environment against the SPFx version and is worth running.

## Step 2 - What is installed?

```bash
node --version
npm --version
npx heft --version
npx tsc --version
```

## Step 3 - Compare

Check installed Node against `engines.node`. If they disagree, that is almost certainly the problem: a Node mismatch produces misleading build errors, not clear ones.

If the SPFx version's Node requirement is not obvious from `engines`, look it up rather than guessing - it changes with nearly every SPFx release. Ask the `mslearn` MCP server for the compatibility matrix; it is the published one, and this is exactly the fact that goes stale in training data.

Confirm `.nvmrc` exists and agrees with `engines`.

## Step 4 - Generated typings

`*.module.scss` has no typings until Heft has generated them into `temp/sass-ts`, which the rig's tsconfig lists in `rootDirs`. On a clone that has never been built, `tsc --noEmit` therefore reports `TS2307: Cannot find module './X.module.scss'` on every stylesheet import, and it reads as a missing file rather than a missing build step.

If `temp/sass-ts` does not exist, say so and run `npx heft build` once. This is the most common "but the code is fine" report on a fresh clone. The `Stop` verify gate detects the same thing and skips tsc rather than blaming the change.

## Step 5 - Dev certificate

The hosted workbench cannot load `localhost:4321` without a trusted cert:

```bash
npx heft trust-dev-cert
```

## Step 6 - Report

A short table: check, expected, found, verdict. Then name the single most likely fix.

Do not change anything without asking. Switching Node versions affects the developer's whole machine, not just this repo.
