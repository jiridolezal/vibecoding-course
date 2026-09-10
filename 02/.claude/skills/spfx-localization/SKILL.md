---
name: spfx-localization
description: Wire and use SPFx localization - the loc folder, mystrings.d.ts, locale files, localizedResources in config.json, and the rule that no user-facing string is ever written inline. Use when adding any user-facing text, when the user says "localization", "translations", "strings", "add a label", "Czech", "English", or when a component contains a hardcoded string.
---

# spfx-localization

**The wiring is always present. The translation is optional.**

Most of our solutions ship Czech only. That is fine. What is not fine is hardcoding strings, because retrofitting localization across a finished solution is a job nobody ever does - and then the one project that needs English becomes a rewrite.

## The rule

No user-facing string literal in a component, a provider, or a property pane. Always `strings.X`. This costs nothing while writing and saves a week later.

Exempt: log messages, error messages meant for developers, `data-*` values, and CSS class names.

## Structure

```
src/webparts/<name>/loc/
  mystrings.d.ts     the interface - every key, typed
  en-us.js           required fallback
  cs-cz.js           Czech
```

Wired in `config.json`:

```json
"localizedResources": {
  "<Name>WebPartStrings": "lib/webparts/<name>/loc/{locale}.js"
}
```

`en-us.js` is the fallback SharePoint uses when a user's locale has no file. It must always exist. On a Czech-only project it may contain Czech text - adding English later then means filling in a file that is already wired, not refactoring 80 components.

## Adding a string

1. Add the key to `mystrings.d.ts` with its type
2. Add the value to **every** locale file - a missing key is a runtime blank
3. Use `strings.MyKey` at the call site

Key names describe purpose, not content: `NoResultsMessage`, not `ZadneVysledky`. Content changes; purpose does not.

## Formatting

- Dates and numbers: format for the user's locale, never hand-built strings
- Pluralisation: separate keys per form, chosen at the call site. Czech has three plural forms and string concatenation will get it wrong
- Never build a sentence by concatenating fragments - word order differs between languages. Use one key with a placeholder

## Before you finish

- No user-facing literal in `.tsx`
- Every key present in every locale file
- `mystrings.d.ts` matches the locale files exactly
