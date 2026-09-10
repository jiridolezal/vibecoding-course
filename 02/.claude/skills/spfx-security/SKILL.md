---
name: spfx-security
description: Security review of an SPFx solution - what the public bundle must never contain, calling AAD-secured APIs without a secret, least-privilege API permissions and admin consent, sanitising SharePoint list HTML, trusting the server rather than the client, and handling personal data. Use when adding an API permission, calling a custom or third-party API, rendering HTML or rich text from a list, reading URL parameters, storing anything client-side, handling personal data, or when the user says "is this secure", "security review", "secrets", "permissions", "sanitise", "XSS", or before a release.
---

# spfx-security

Two facts drive everything here:

1. **The bundle is public.** Every authenticated user in the tenant can read your JavaScript, and so can their browser devtools. Anything in it is published, not hidden.
2. **The client is not a trust boundary.** Code runs on the user's machine, under the user's identity. It can be read, modified and replayed.

Most SPFx security defects are one of those two facts being forgotten.

## What must never be in the bundle

- API keys, client secrets, connection strings, SAS tokens, passwords
- A "hidden" admin URL, list GUID or endpoint treated as if it were a secret
- Personal data hardcoded as sample or fallback content
- Internal hostnames or infrastructure detail that is not already public

This includes `preconfiguredEntries[].properties` and every default in the property pane. **Property pane values are not secret either** - they are stored on the page and readable by anyone who can read the page. A site owner typing an API key into a text field is a defect in your property pane, not their mistake: do not offer the field.

If a call genuinely needs a secret, the secret belongs server-side - an Azure Function or API the client calls with the *user's* token, never with a shared credential.

## Calling APIs without a secret

| Target | Client | Notes |
|---|---|---|
| SharePoint on this tenant | `SPHttpClient` | User context, no extra permission |
| Microsoft Graph | `MSGraphClientV3` | Needs `webApiPermissionRequests` + admin consent |
| Your own AAD-secured API | `AadHttpClient` | Needs a permission request naming the app |
| A public, unauthenticated API | `HttpClient` | No token attached - check what you are leaking |

`AadHttpClient` gets a token for the signed-in user from the SharePoint Online Client Extensibility service principal. You never hold a secret; your API validates the token and enforces authorization itself. See `spfx-data`.

Never send an OAuth token to an endpoint other than the one it was issued for, and never put a token in a URL, a log line or `localStorage`.

## Permissions: least privilege, and admin consent

`webApiPermissionRequests` in `config/package-solution.json` is **tenant-wide**. Approving `Group.ReadWrite.All` for your web part approves it for every SPFx solution in the tenant, because they share one service principal.

- Request the narrowest scope that works: `.Read` before `.ReadWrite`, `Sites.Selected` before `Sites.Read.All`, a specific resource before `.All`
- Delegated permissions, so the user's own access still limits the result
- Every scope recorded in `docs/permissions.md` with who approved it and when
- Tell the user plainly that an administrator must approve it, and that the solution **fails silently for everyone** until they do

Removing a scope from the manifest does not revoke it. Revocation is a separate admin action - say so when a scope is dropped.

**`isDomainIsolated`** puts the web part in its own iframe with its own AAD application, so its tokens are not shared with other SPFx code on the page. Worth it for a web part calling a sensitive custom API. It constrains what else the web part can do, so it is a decision for `docs/decisions/`, not a default.

## Authorization is the server's job

Hiding a button is user experience, not security. A user who can read the page can call the same endpoint the button would have called.

- Never gate anything that matters on a client-side role check
- SharePoint trims list results by the user's permissions - lean on that rather than filtering sensitive rows in the browser
- Do not fetch data the user is not allowed to see and then hide it
- A "no permission" state means the request was refused by the server, not that you decided not to make it

## Injection

SharePoint list content is written by users. Treat every field as hostile.

- **Never `dangerouslySetInnerHTML` with list content.** Rich text, multi-line enhanced text and anything pasted from Word are the usual vectors
- If HTML genuinely must render, sanitise with a maintained sanitiser (DOMPurify) with an allow-list. **Never a regex** - the lint config flags the attribute so this decision is always explicit
- React escapes text children by default. Keep it that way
- URL-valued fields: validate the scheme. A `javascript:` URL in a `Link` field executes on click
- URL parameters bootstrapped in the ContextWrapper are attacker-controlled. Encode them into queries with `encodeURIComponent`, never string-concatenate them into an OData filter
- `$filter` built from user input needs the same care as SQL. Escape quotes

## Client-side storage and logging

- No personal data in `localStorage` or `sessionStorage` - it is unencrypted, survives sign-out and is readable by any script on the page
- Cache reference data, not people
- Never log tokens, full response bodies, or anything with personal data. Console output is visible to the user and to anyone at their screen
- Remove diagnostic logging before shipping - `spfx-review` checks for it

## Personal data

Most of our solutions render employee data, so this is routine rather than exotic.

- Fetch the fields the UI shows, not the whole item. `$select` is a privacy control as well as a performance one
- User photos come from SharePoint or Graph, never copied into our own storage
- Never real personal data in prototypes, screenshots, test fixtures or issue reports - see `spfx-prototype`
- If a solution processes personal data in a new way, that is a decision worth recording, and possibly a question for the customer, not an implementation detail

## Dependencies

The whole dependency tree ships to every user.

```bash
npm audit --omit=dev
```

Triage what it reports rather than running `--force`. A build-time-only vulnerability in a devDependency is not the same risk as one in a package that lands in the bundle. Never load a script from a CDN at runtime - that hands a third party the ability to run code in your customer's SharePoint page.

## Before you finish

- No secret, key, token or connection string anywhere in `src/` or `config/`
- No environment-specific or sensitive value in `preconfiguredEntries`
- Every API permission least-privilege, documented, and the admin consent step stated to the user
- All list-sourced HTML sanitised; no unreviewed `dangerouslySetInnerHTML`
- URL parameters and user input encoded before they enter a query
- No personal data in client-side storage or logs
- `npm audit --omit=dev` triaged
- Nothing important gated only in the browser
