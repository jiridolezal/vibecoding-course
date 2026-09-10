---
name: spfx-data-sources
description: Design and prepare the SharePoint lists and libraries a solution reads and writes - schema design with internal field names, click-by-click instructions the site owner can follow in the browser, sample data, permissions, and the docs/data-sources.md record. Use when a spec needs a list or library that does not exist yet, when the user says "where does the data live", "create the list", "set up the list", "prepare the data", "add the columns", "SharePoint list", "document library", or when a data function needs a field nobody has created.
---

# spfx-data-sources

The data for our solutions lives in SharePoint lists and libraries on the site the solution is developed against. Those lists have to exist, with the right columns, before a single fetch works - and **the person who can create them is the user, not you.** This skill designs the schema and hands them instructions they can follow.

`spfx-data` is how the solution *reads and writes* a source. This is how the source comes to exist.

## Step 1 - Design the schema

One list per kind of thing. Resist the single wide list holding three unrelated concepts, and resist a list per screen.

For each column, decide four things:

| Decide | Why it matters |
|---|---|
| Display name | What the user sees, and what they will rename later |
| **Internal name** | What the code uses. Fixed at creation, forever |
| Type | Decides how it comes back over REST |
| Required / default | Decides whether the mapping needs a fallback |

**The internal name is the trap.** SharePoint derives it from the display name at creation and then never changes it, so a column created as "Publish date" is `Publish_x0020_date` in every query for the rest of its life, even after someone renames the column to "Date". Two ways out, and pick one deliberately:

- **Create the column with a code-friendly name, then rename it.** Create `PublishDate`, save, then change the display name to "Datum publikovani". The internal name stays `PublishDate`. This is what we do.
- Accept the escaped name, and write it in `docs/data-sources.md` exactly as SharePoint returns it.

Types worth knowing before choosing one:

| Need | Column type | How it comes back |
|---|---|---|
| Short text | Single line of text | `string` |
| Long text, no formatting | Multiple lines, plain text | `string` |
| Rich text | Multiple lines, rich text | HTML - **must be sanitised**, see `spfx-security` |
| A date | Date and time | ISO 8601 `string`, always UTC |
| Yes/no | Yes/No | `boolean` |
| A number | Number / Currency | `number` |
| One of a fixed set | Choice | `string`. Prefer this over a lookup for a stable set |
| A person | Person or Group | Needs `$expand`; select `AuthorId` or `<Field>Id` and expand |
| A link to another list | Lookup | Needs `$expand=Field/Title` and `$select=Field/Title` |
| An image or file | Document library, or attachment | A library is usually the better answer |

Every list already has `Id`, `Title`, `Created`, `Modified`, `Author` and `Editor`. Do not create a "Name" column when `Title` is what you mean.

## Step 2 - Write it down first

Write `docs/data-sources.md` **before** anything is created, so the user is approving a schema rather than discovering one. One section per source, holding the site, the purpose, the owner, the expected volume, whether it exists yet, a column table, the domain model it maps to, and the query that will read it.

The column table is the load-bearing part - display name, internal name, type, required, and a note where the internal name differs from the display name or a default matters.

`docs/data-sources.md` is the answer to "which field was that again" a year from now, and `spfx-review` checks it is current.

## Step 3 - Hand the user instructions they can actually follow

They are in a browser, on their own site, and may never have made a list before. Write numbered steps, name the exact button text, and say what they should see afterwards. Never say "create a list with these columns".

The shape that works:

1. Open the dev site (the URL is in `config/serve.json`)
2. Gear icon, top right, then **Site contents**
3. **+ New**, then **List**, then **Blank list**
4. Name it exactly as the code expects, and say so - then **Create**
5. Add each column one at a time, naming the menu item to pick (**+ Add column**, then the type, then the code-friendly name, **Save**)
6. Rename the display names afterwards, so internal names survive - column heading, **Column settings**, **Rename**
7. Add the sample rows from step 4, including the awkward ones
8. Come back and say it is done

Steps 3 to 7 collapse into one if you generate a CSV with the schema in it - see step 4. Prefer that: it is fewer instructions, and the internal names come out right by construction.

Then **stop and wait.** Do not write the data function against a list that does not exist yet - the first real fetch is how you find out the schema is wrong, and that is worth finding out before there is code shaped around it.

If the user would rather you did it, and CLI for Microsoft 365 is installed and signed in, `m365 spo list add`, `m365 spo field add` and `m365 spo listitem add` do the same job - see `dont-reinvent`. Ask first: it is their site, and a list created by an agent is still a list they own.

## Step 4 - Sample data

Ask for realistic rows, and specifically for the awkward ones. A list holding three tidy records hides every bug worth finding:

- One row with an empty optional field, so the mapping fallback is exercised
- One with a very long title, so the card layout is tested
- One with diacritics, so search and sorting are tested
- Enough rows to exceed one page, if paging is in the plan
- Nothing that is real personal data - see `spfx-security`

The empty and error states in the specs also need a way to be reached. Write down how: an empty list to point at, and a deliberately wrong list name.

### Hand them a CSV, not a table to retype

Nobody types twenty rows into a browser. Write the list as a definition and generate the file:

```bash
node scripts/make-list-csv.js docs/data-sources/faq.json --check
node scripts/make-list-csv.js docs/data-sources/faq.json --with-schema --out temp/FAQ.csv
```

The definition is JSON - the list name, a field per column with its internal `name`, `type` and `display`, and the sample `rows`. Run the script with no arguments to print the shape. Keep it next to `docs/data-sources.md`: it is the schema in a form that can be re-run, and regenerating the list after a schema change is then one command rather than a click-through.

Two flavours, and the difference decides which instructions the user gets:

| Flavour | What it carries | They do |
|---|---|---|
| default | header row of internal names, then the rows | Open the existing list, **Edit in grid view**, paste |
| `--with-schema` | a `ListSchema=` line of column XML, then the same | **Site contents > New > List > From CSV** - columns and data in one step |

`--with-schema` is usually the one you want: it replaces the whole click-by-click column ritual in step 3, and the internal names come out exactly as the code expects rather than as whatever the browser made of the display name.

What the script will not generate, because the id only exists on one tenant: person, lookup and managed metadata columns. `--check` names them. Add those by hand afterwards, or export a real list from the site and edit that.

Two values that are read in the **site's** locale, not yours - check them on the first import rather than assuming:

- **Dates.** A Czech site reads `1.2.2026` as 1 February. An ISO date is not always safe here.
- **Yes/No.** Read in the site's display language.

Never put real personal data in a sample file - it ends up in the repo, and `temp/` is gitignored but a definition under `docs/` is not.

## Step 5 - Permissions

Say plainly who can see the source, and what a user who cannot see it gets.

- A reader of the site reads the list. A web part running as a user who cannot gets **403, not an empty array** - the provider `error` path must handle it, and the view needs a no-permission state.
- Writing needs contribute on the list, and that failure is also a runtime 403, not a build error.
- **Never rely on list permissions to hide anything that is also in the bundle or in a property pane value.** The client is not a trust boundary - see `spfx-security`.
- Nothing here needs an API permission grant: a list on the same tenant is read with the user's own context. If a source is Graph or an external API, that *is* a grant, it is tenant-wide, and it belongs in `docs/permissions.md` with an admin approval step called out to the user.

## Step 6 - Libraries, when the data is files

A document library is the right home for images, PDFs and attachments. It is a list with `File` and `Folder` on every item, so:

- Read `File/Name`, `File/ServerRelativeUrl` and `File/Length` with `$expand=File`
- Never build a file URL by concatenation - use the one SharePoint returns
- Size images for their largest render before uploading. A 4 MB photo in a 320 px card is the most common performance defect in our solutions
- A library's own columns behave exactly like a list's, internal names included

## Before you finish

- `docs/data-sources.md` exists and matches what was actually created
- Every internal name in it was read back from the live list, not assumed
- The user has confirmed the source exists and has data in it
- Awkward rows exist, not only tidy ones
- A way to reach the empty state and the error state is written down
- `docs/architecture.md` links here rather than duplicating the schema

## Then

Offer `spfx-data` to write the provider and data function against the source that now exists.
