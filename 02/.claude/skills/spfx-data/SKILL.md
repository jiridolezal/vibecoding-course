---
name: spfx-data
description: Write the data layer of an SPFx solution - the provider and data-function pattern, choosing between SPHttpClient, PnPjs, MSGraphClient and AadHttpClient, paging, mapping raw list responses to domain models, loading and error state, aborting on unmount, and avoiding refetch storms from the property pane. Use when fetching SharePoint or Graph data, calling a custom or third-party API, writing or changing a provider, adding a list query, or when the user says "load data", "fetch from the list", "call Graph", "call our API", "AadHttpClient", "PnPjs", or "the data is not loading".
---

# spfx-data

Every byte of data enters the solution through this layer, and nowhere else.

**If the list or library does not exist yet, stop.** `spfx-data-sources` designs the schema, records it in `docs/data-sources.md` and hands the user instructions to create it. Writing a fetch against a source nobody has created means guessing the internal field names, and internal names are fixed forever at creation.

## The pattern

```
provider  ->  data function  ->  domain model
 state         fetch + map        what the UI uses
```

**`data/loadBranches.ts`** - one exported async function. Takes the web part context and whatever it needs. Fetches, checks the response, maps raw to domain, returns. No React, no state, no context.

**`providers/BranchProvider.tsx`** - React context. Calls the data function, owns `data` / `isLoading` / `error`, exposes a `use<Domain>()` hook that throws when used outside its provider.

**`types/`** - `TReceivedBranch` for the raw response, `BranchItem` for the domain model.

## Which client

Default to **`SPHttpClient`** - no dependency, smallest bundle, correct for straightforward list reads.

Reach for **PnPjs** when the solution needs any of:

| Need | Why PnPjs |
|---|---|
| Paging beyond one request | Handles `@odata.nextLink` for you |
| Several requests at once | Batching |
| Repeated reads of stable data | Caching behaviours |
| Files and folders | Upload, chunked upload, folder ops |
| Microsoft Graph | One consistent API surface |
| Complex CAML or list provisioning | Far less hand-written XML |

**One client per solution.** Mixing both is worse than either choice. If the solution already uses one, use that one; if this feature genuinely needs the other, raise it as a decision and record it in `docs/decisions/`, do not just add the import.

When adopting PnPjs, use selective imports. A wildcard import pulls the whole library into the bundle.

## Calling something other than SharePoint

`SPHttpClient` and PnPjs cover this tenant. Anything else needs a different client, and picking the wrong one is how a solution ends up with a secret in its bundle.

| Target | Client | Token |
|---|---|---|
| SharePoint, this tenant | `SPHttpClient` | Implicit, user context |
| Microsoft Graph | `MSGraphClientV3` | Issued for the user, needs consent |
| Our own AAD-secured API | `AadHttpClient` | Issued for the user, needs consent |
| A public, unauthenticated API | `HttpClient` | None attached |

**`AadHttpClient` is the answer for a customer's own API.** It obtains a token for the signed-in user, so the solution never holds a credential:

```ts
const client = await context.aadHttpClientFactory.getClient('<aad-app-client-id>');
const res = await client.get(`${apiRoot}/branches`, AadHttpClient.configurations.v1);
```

Two things follow, and both are easy to discover too late:

1. **It needs a permission request in `config/package-solution.json`** (`webApiPermissionRequests`, naming the API's `resource` and `scope`) and a **tenant administrator must approve it**. Until they do, the call fails for every user, silently. Record it in `docs/permissions.md` and say so out loud
   - see `spfx-security` and `spfx-ship`.
2. **The API must accept the SharePoint Online Client Extensibility service principal** as the caller and validate the token itself. Authorization is the API's job, not the web part's.

`HttpClient` attaches no token. Before using it, be clear about what is being sent to a third party and whether the customer has agreed to it.

Never call an API using a shared key from the client - see `spfx-security`.

## The provider contract

Every provider exposes, at minimum:

```ts
interface IBranchContext {
  branchItems: BranchItem[];
  isLoading: boolean;
  error: Error | undefined;
  reload: () => void;
}
```

`isLoading` and `error` are not optional. A provider that swallows failures into `console.error` leaves the user staring at an empty list forever - that is the single most common defect in our solutions.

Requirements:

- **Abort on unmount.** SPFx unmounts and remounts web parts constantly in edit mode. Use an `AbortController` or an `isCancelled` flag; never call `setState` after unmount.
- **Depend on the narrowest thing.** A provider's effect depends on the specific property it uses, not on the whole props object.
- **Do not fetch what the user cannot see.** Data behind a tab or a dialog loads when that view opens.

## The refetch storm

SPFx calls `render()` on **every** property pane change. `render()` creates a new element tree, which remounts the provider pyramid, which refetches everything. Editing a text field character by character can mean one full data load per keystroke.

Mitigations, in order:

1. `disableReactivePropertyChanges` so changes apply on a button press (see `spfx-property-pane`)
2. Providers keyed to the properties they actually consume
3. Caching in the data layer for genuinely stable reference data

## Fetching correctly

- **Always check `response.ok`** before reading the body, and throw an error that names the list and the status. A failed request that returns `undefined` produces a bug report three screens away from the cause.
- **Select the fields you need.** `$select` is not an optimisation, it is the difference between 8 KB and 800 KB.
- **Handle paging properly.** `$top=5000` is a bet that the list stays small. Follow `@odata.nextLink` iteratively; if you are writing that loop by hand more than once, that is the argument for PnPjs.
- **Use internal field names**, not display names. Display names change when someone renames a column in the UI.
- **Expect throttling.** SharePoint returns 429 with `Retry-After`. Honour it.

## Writing back

Reading is most of what we do, but a solution that writes has three extra traps, all of them runtime-only:

- **`SPHttpClient` handles the form digest for you.** Do not fetch `contextinfo` and do not set `X-RequestDigest` by hand - that is pre-SPFx advice and it goes stale.
- **Update and delete need `IF-MATCH` and `X-HTTP-Method`.** `IF-MATCH: "*"` overwrites whatever is there; passing the item's `odata.etag` instead makes the write fail on a concurrent edit rather than silently discarding it. Prefer the etag, and surface the 412 as a "someone else changed this" message.

  ```ts
  await context.spHttpClient.post(itemUrl, SPHttpClient.configurations.v1, {
    headers: { "IF-MATCH": etag, "X-HTTP-Method": "MERGE" },
    body: JSON.stringify({ Title: next.title }),
  });
  ```

- **A write the user is not allowed to make fails with 403 at runtime.** Read permission does not imply contribute. The UI must not offer an action that will 403 - and when it does anyway, the error is shown, not swallowed.

Write operations belong in `data/` like every other request, one function per operation (`createNewsItem`, `updateNewsItem`), and the provider exposes them through its context along with the state. After a successful write, refetch or update local state deliberately - never both, and never neither.

## Mapping

Raw to domain happens in `data/`, in one place. Components never touch a `TReceived*` shape. Prefer `undefined` over `null` for absent values - it is what TypeScript's optional types mean and it avoids two ways to say nothing.

## Before you finish

- No HTTP client imported outside `data/`
- Every data function checks `response.ok`
- Every provider exposes `isLoading` and `error`
- Every effect cleans up
- No `any` on a response shape
- Nothing user-supplied concatenated into a query - see `spfx-security`
