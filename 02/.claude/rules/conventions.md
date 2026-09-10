# Conventions

## Naming

This table is the single home for naming. Skills reference it; they do not repeat it.

| Kind | Convention | Example |
|---|---|---|
| Raw API response shape | `T` prefix | `TReceivedBranch` |
| Domain model (class) | plain noun | `BranchItem` |
| Interface / props | `I` prefix | `IPaginationProps` |
| Provider | `<Domain>Provider` + `use<Domain>()` | `BranchProvider`, `useBranch()` |
| Data function | verb first | `loadBranches`, `fetchEmployees` |
| Component folder | camelCase; file PascalCase | `branchCard/BranchCard.tsx` |
| Style | sibling of its component | `BranchCard.module.scss` |
| Icon alias in the barrel | purpose, `Icon` suffix | `FiSearch as SearchIcon` |

Raw to domain mapping happens in `data/`, never in a component. The folder contract is in the `spfx-structure` skill.

## Comments

Brief, and only where the code cannot speak for itself. Explain **why**, never what. No essays, no narration of your reasoning, no TODOs, no commented-out code. A JSDoc line on an exported function is welcome; a paragraph above an obvious `useState` is noise.

## Markdown

**Never hard-wrap prose.** A paragraph is one line, however long; the editor soft-wraps it and Markdown renders it identically either way. Wrapping at a column means every later edit reflows the paragraph and the diff hides the change. This applies to everything in `docs/`, `.claude/` and the READMEs.

Tables, code fences and frontmatter keep their own line structure, and prettier does not touch `.md` — this one is on you.

## Git

GitHub. **`main` is the only long-lived branch** and always holds the complete, working solution. There is no `dev` branch and we do not use pull requests — see `docs/decisions/0000-spfx-standard.md`.

Work happens on a short-lived branch, one per unit of work:

| Prefix | For |
|---|---|
| `feature/` | Something the solution could not do before |
| `improvement/` | Something it already did, done better — refactor, polish, perf |
| `bugfix/` | Something that was broken |

**Claude manages the repository, local and remote, without being asked.** The user never has to think about git, and never has to ask for a commit or a push. GitHub is always up to date. Specifically:

- **Branch before working.** Never commit onto `main` directly. If the current branch is `main`, create `feature/<short-name>` (or `improvement/`, `bugfix/`) first. Branch names are kebab-case and short: `feature/news-feed`, `bugfix/empty-state-flash`.
- **Commit at logical checkpoints** — a working increment, a completed refactor, a fix — rather than one commit at the end of a session.
- **Push every commit, straight away.** `git push -u origin <branch>` on the first one, `git push` after each one after that. The remote is never behind the machine.
- **Only commit what passes the verify gate.** A commit that does not compile is worse than no commit — and a pushed commit is public, so the gate is the last line of defence, not a formality.
- **Never stage blindly.** `git add` the files the change touched, not `-A`. Check `git status` for stray build output, `.env` files and scratch files first.
- **Merge and clean up when the work is done.** Once the unit of work is verified — stage 4 complete, including the workbench — merge it into `main` and delete the branch:

  ```bash
  git switch main && git merge --no-ff feature/news-feed
  git push
  git branch -d feature/news-feed
  git push origin --delete feature/news-feed
  ```

  `--no-ff` keeps the unit of work visible as one merge in the history. Never leave a merged branch lying around, on the machine or on GitHub, and never delete an unmerged one with `-D` without asking.

**Ask before rewriting history or throwing work away**: `reset --hard`, `checkout` or `restore` over uncommitted changes, `git branch -D`, any force push, and tagging a release. Everything else — branching, committing, pushing, merging, deleting a merged branch — happens without asking. Permissions enforce the line; do not look for a way around it.

## Commit messages

**Subject: a capital letter, then an imperative verb, then plain words.** Short — aim for under 50 characters. No prefix, no `feat:` or `fix:`, no full stop, no ticket number. Write it so someone who has never opened the repo knows what changed.

| Good | Bad |
|---|---|
| `Fix the wrong address on contact cards` | `refactor(contact): normalise address per ADR-3` |
| `Add a search box to the news feed` | `wip` |
| `Make the empty state stop flashing` | `Fixed some stuff and cleaned up` |

**Body: usually none.** Only when the subject cannot carry the reason. Then one or two short sentences of plain language — why, never what. Never a bullet list of the things you did; the diff already says that.

**Never add a co-author trailer**, and never name Claude, an agent or a tool anywhere in a message. The message describes the change, not who typed it.
