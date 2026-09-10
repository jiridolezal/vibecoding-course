---
description: List what this SPFx setup can do and when to use each part
---

Print a short guide to this repo's SPFx standard. Read `.claude/CLAUDE.md` and `.claude/skills/*/SKILL.md`, then output:

0. If `package.json` still contains `__name_slug__`, open with one line saying this is an uninitialised template, nothing compiles yet, and `spfx-setup` comes first.
1. The five lifecycle stages, one line each, with the skill that drives each - specs (and architecture), prototype, implement, verify, report.
2. A table of every available skill: name, one line on what it does, and the phrase a developer would naturally say to trigger it.
3. The agents available and when they are worth running.
4. The hard rules, as a short list, marking which are enforced by lint (`lint/README.md`) and which are checked by eye.
5. What is enforced automatically: the version guard, the formatter, and the `Stop` verify gate that runs `tsc` and eslint, plus stylelint when a stylesheet changed.
6. How git is handled without being asked - `main` plus short-lived `feature/`, `improvement/` and `bugfix/` branches, every commit pushed, merged and deleted when stage 4 passes, so GitHub is always current - and the short list that still needs the user's go-ahead.
7. Where documentation lives: `docs/specs.md`, `docs/architecture.md`, `docs/data-sources.md`, `docs/permissions.md`, `docs/decisions/`, `docs/handoff/`.

Keep it to one screen. This is the first thing a new developer on the team reads, so it must be readable in under a minute, not exhaustive.
