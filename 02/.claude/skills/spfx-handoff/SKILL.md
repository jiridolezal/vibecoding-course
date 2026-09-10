---
name: spfx-handoff
description: Stage 5 of the lifecycle - close an iteration by writing a handoff note in docs/handoff/ and reporting back in plain language what changed, what was actually verified, what was not, and what happens next. Use at the end of any unit of work, when the user says "are we done", "summarise", "what did you do", "wrap up", "hand over", "next steps", or before a session ends with work completed.
---

# spfx-handoff

Stage 5. The work is not finished when the code compiles; it is finished when the person who asked for it knows what they have got.

Two audiences, one skill:

- **The user**, who may not be a developer, and needs to know what to look at, what to decide, and what is still missing.
- **The next session**, which will have none of this conversation and will read `docs/` to find out where things stand.

## Step 1 - Write the handoff note

`docs/handoff/YYYY-MM-DD-<short-slug>.md`, one file per iteration. Never overwrite a previous one - the sequence of them *is* the project history in prose, next to the git history in commits.

Six headings, in this order, and none of them omitted:

```markdown
# <What this iteration was> - 2026-09-02

## What changed
Plain language, not a file list. "The news feed now filters out unpublished
items and shows a message when there are none." Then the files, briefly.

## What I verified
Only what actually happened. Name the command or the observation:
- `npx heft build --production` passed
- `npm run verify` passed
- Opened the workbench at <url>, saw the populated and empty states
- Console clean, no failed requests

## What I did not verify
The honest half. "Did not test the error state - I could not make the list
return a 403." "Not checked in a one-third column." "Not run through
spfx-a11y." An empty section here is almost always a lie.

## Decisions taken
Anything chosen without asking, and why - so it can be overruled cheaply.
Anything that belongs in `docs/decisions/` gets a record there and a link here.

## Open questions
Every question waiting on the user, numbered, each one answerable without
reading code.

## Next steps
Two or three, in the order they should happen, each naming the skill that
drives it.
```

Where the work also changed the plan, update the document it belongs in rather than describing the change here: specs in `docs/specs.md`, structure in `docs/architecture.md`, a schema in `docs/data-sources.md`, a scope in `docs/permissions.md`. The handoff note links to them. It is a covering letter, not a second copy of the project.

## Step 2 - Bring `README.md` up to date

**This is the moment to write the README, and the only one.** `spfx-setup` could not: it ran before specs existed, so all it had was one sentence the user typed. You have just finished a working increment and know exactly what the solution does, what it reads and what it does not do yet. Nobody will know it better later.

Four sections carry the `(keep current)` marker, and the reader they exist for is the customer's next developer, or whoever deploys this to a second site, or you in a year:

| Section | Update when | Fails how |
|---|---|---|
| **What is in here** | a web part was added, removed or repurposed | still one row, three web parts later |
| **What it reads** | a list, library, field or endpoint changed | someone deploys to a new site and finds out the hard way which lists it needs |
| **What a site owner configures** | a property pane option changed | the property pane has options nobody can explain |
| **Known limitations** | every iteration - it mirrors "What I did not verify" | reads as finished when it is not |

Also replace the placeholder paragraph under the title the first time round: what this solution does, who uses it, and on what page. Two or three sentences, in the customer's language, no SPFx vocabulary.

What does **not** go in the README: anything already owned elsewhere. Not the invariants (`CLAUDE.md` numbers them and a second copy drifts), not the lifecycle (`/spfx-help`), not the folder contract (`spfx-structure`), not the full schema (`docs/data-sources.md` - the README carries the short version and links). A README that restates the standard is the failure mode here; every solution from this template would then have the same README with a different title.

If nothing user-visible changed - a refactor, a lint fix - say so and leave it alone. An untouched README is a fine outcome; a stale one is not.

## Step 3 - Commit and close the branch

The handoff note is part of the iteration, so it goes in the same history. Per `.claude/rules/conventions.md`: commit and push, then - if the unit of work is genuinely complete and stage 4 passed - merge into `main`, push `main`, and delete the branch here and on GitHub. If stage 4 did not pass, the branch stays open and pushed, and the note says so. Either way the user has nothing to do in git.

## Step 4 - Report back in the conversation

Short. Five lines, not five paragraphs, because the detail is now in the note:

1. What the user can now do that they could not before
2. What you verified, in one line, and how
3. What you did **not** verify, in one line
4. The open questions, if any - numbered, so they can answer "1 yes, 2 later"
5. What you suggest next, and offer to start it

Then link the handoff note by path.

## The rules of an honest report

- **Never report a change as working because the code looks right.** If it was not run, say it was not run. `spfx-preview` covers the case where a browser is unavailable: hand the verification to the user, with the URL and the exact things to look at, and report what *they* saw, attributed to them.
- **Do not pad with what did not change.** A list of untouched files is noise.
- **Do not claim a check the gate ran for you.** The `Stop` hook runs `tsc`, eslint and stylelint. That is worth one line, not a section.
- **One iteration, one note.** If two unrelated things happened, that was two iterations and it is two notes.
- **No open question left implied.** If you guessed, it goes in "Decisions taken"; if you are still unsure, it goes in "Open questions".
