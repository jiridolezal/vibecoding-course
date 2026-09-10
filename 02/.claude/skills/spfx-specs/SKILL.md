---
name: spfx-specs
description: Stage 1 of the lifecycle - collect and write down what a web part or extension must do before any design or code exists, producing docs/specs.md including data sources, states, permissions and the acceptance checklist used later to verify. Use when starting a new web part, extension or feature, or when the user says "new web part", "collect specs", "what are we building", "requirements", or begins describing something to build.
---

# spfx-specs

Stage 1. Nothing gets designed or built until this exists, because the acceptance checklist written here is what stage 4 verifies against - we have no unit tests, so this document is the test plan.

## What to collect

Ask about anything unclear; do not invent answers. Keep it to one or two rounds of questions.

**Purpose** - who uses this, what do they accomplish, on what page.

**Data** - for each source:
- SharePoint list / library / Graph endpoint / search
- Which fields, and their internal names (not display names)
- Expected volume - this decides paging, and whether PnPjs earns its place
- Who owns it, and does it exist yet
- Required permissions, and whether an admin has granted them

**Prefer a SharePoint list or library.** When the same data could reasonably live in a list or come from Graph, choose the list. A list on this tenant is read with the user's own context and needs nobody's approval. A Graph endpoint needs a `webApiPermissionRequests` entry and a **tenant administrator** to approve it - a person outside the project, on their own timescale, granting a permission that is tenant-wide rather than scoped to this solution. Until they do, the call fails for every user. That is a dependency on someone who has not agreed to be one, and it belongs in the specs as a risk, not discovered in stage 3.

Reach for Graph only when the data genuinely lives nowhere else - a mailbox, a calendar, Teams, presence, the org chart. When you do, write down why the list was not an option, which scopes are needed, and who is going to ask the admin. Same for any external API. See `spfx-security` for the client that goes with each source.

**Configuration** - what the site owner sets in the property pane, and what the web part shows before it is configured.

**States** - what the user sees when: loading, no results, request failed, no permission, populated. All five are required.

**Out of scope** - write this down. It is the cheapest section here and it prevents the most argument later.

**Acceptance checklist** - 5 to 15 concrete, checkable statements. "Searching without diacritics finds the accented record", not "search works".

## Output

Write `docs/specs.md`, or `docs/specs/<feature>.md` when adding to an existing solution, with those sections in that order.

If a data source is a SharePoint list or library that does not exist yet, say so plainly and do not design the schema here - `spfx-data-sources` does that, and it produces both `docs/data-sources.md` and instructions the user can follow in the browser to create it.

If permissions beyond the current user's context are required, record the exact scopes in `docs/permissions.md` and say plainly that a tenant admin must approve them - Graph permission grants are tenant-wide, not per-solution.

## Then

Offer `spfx-architecture` - the specs say what, that says how, and it is the last cheap moment to notice the plan does not work. Then `spfx-prototype` for stage 2.

Do not start writing SPFx code.
