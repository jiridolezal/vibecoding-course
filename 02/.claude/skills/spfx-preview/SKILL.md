---
name: spfx-preview
description: Run the solution and look at it - start the dev server in the background, open the SharePoint hosted workbench or a real page in Chrome, build the debug query string for extensions, read console and network errors, and iterate on what is actually rendered. Use when the user says "run it", "show me", "preview", "does it work", "debug this", "open the workbench", or after any change to rendered UI.
---

# spfx-preview

We write no unit tests. **This skill is the test harness.** Treat running the solution and looking at it as a required step, not a convenience.

Use Claude in Chrome rather than a headless browser: SharePoint needs a real authenticated session, and the user's Chrome profile already has one.

## Step 1 - Start the dev server in the background

The dev server never exits. Run it in the background and never block on it.

```bash
npx heft start
```

If it fails, run `spfx-doctor` before trying anything else. The two usual causes are an untrusted dev certificate and a Node version mismatch.

## Step 2 - Work out the URL

**Read `config/serve.json`.** It already holds the right patterns for this solution and this SPFx version, including the debug parameters for any extension. Do not reconstruct URLs from memory - the manifest path has moved between SPFx releases.

**Web parts** - the hosted workbench:

```
https://<tenant>.sharepoint.com/sites/<site>/_layouts/15/workbench.aspx
```

There is no local workbench any more.

**Extensions** - the workbench will not do; they need a real page, with the debug parameters from `serve.json`:

```
<page>?loadSPFX=true
      &debugManifestsFile=https://localhost:4321/temp/build/manifests.js
      &customActions={"<component-guid>":{"location":"...","properties":{...}}}
```

- Application customizer -> any site page, `location` is `ClientSideExtension.ApplicationCustomizer`
- List view command set -> a **list** page, `ClientSideExtension.ListViewCommandSet.CommandBar`
- Field customizer -> a list page, using the `fieldCustomizers` parameter

Take the component GUID from the component's `.manifest.json`.

## Step 3 - Open it

Load the `claude-in-chrome` skill, open a new tab, navigate. Expect a certificate warning for `localhost:4321` on first use - if it appears, the dev cert is not trusted; stop and run `npx heft trust-dev-cert`.

### The debug scripts dialog - accept it

SharePoint asks, every single load, whether to run scripts from `localhost`:

| | English | Czech |
|---|---|---|
| Title | Allow debug scripts? | Chcete povolit ladění skriptů? |
| **Accept this** | **Load debug scripts** | **Načíst ladicí skripty** |
| Not this | Don't load debug scripts | Nenačítat ladicí skripty |

**The wrong button is the highlighted one**, the warning text is red and alarming, and declining is what a careful person does by default. Decline and the page loads perfectly with the web part simply absent - no error, nothing in the console, just a blank spot. That looks exactly like a broken build, and time gets spent on it.

So: click **Load debug scripts** yourself, and when you are handing the URL to the user, tell them in the same message which button to press and that it reappears on every reload. Do not just send the link.

### When you cannot drive a browser

Browser control needs a real authenticated SharePoint session, so it is not always available - the extension may not be connected, or the session may be running unattended. **Do not silently skip stage 4 when that happens, and do not claim the change works.** Hand the verification to the user instead:

1. Give them the exact URL to open, already assembled from `serve.json`
2. Tell them precisely what to look at - which states, which column width, and which acceptance items from `docs/specs.md` you need confirmed. Include the **Load debug scripts** instruction above; without it they will see nothing and report the web part as broken
3. Ask for a screenshot, plus the console filtered to errors and the network tab filtered to failures
4. Wait for that before reporting. Then report what *they* saw, attributed as such

An unverified change is reported as unverified. That is a normal outcome, and it is much cheaper than a wrong claim.

## Step 4 - Actually look

Take a screenshot and read it. Then check the things a screenshot does not show:

- **Console** - filter for errors and warnings, not the whole log
- **Network** - failed requests, 403s (permissions), 429s (throttling), and any response far larger than expected
- **The states** - do not only check the happy path. Verify empty and error states by pointing the web part at an empty list or a bad URL
- **Resize** - SharePoint web parts live in one-third columns as often as full width
- **Hover every interactive thing and watch what else moves.** Nothing should. A card that grows on hover, a button that gets taller and pushes the row down, text that reflows because the font got heavier - that judder is the single clearest tell of a thrown-together app, and it is the easiest thing in this list to fix. `spfx-ui` says how; here you just have to look for it

## Step 5 - Report

Say what you saw, not what should have happened. Include the screenshot, any console errors verbatim, and a plain statement of whether the acceptance checklist items in `docs/specs.md` pass.

If something is wrong, fix it and look again. Do not report a change as working because the code looks right.

## Notes

- Changes rebuild automatically; refresh the page rather than restarting serve
- Property pane changes remount the whole provider tree and refetch - if the network tab fills up while you type, see `spfx-data`
- Stop the background server when the session's preview work is done
