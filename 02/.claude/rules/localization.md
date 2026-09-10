---
paths:
  - "src/**/loc/**"
---

# Localization files

- `en-us.js` is the fallback SharePoint uses when a locale has no file. It must always exist, even on a Czech-only project - on which it may contain Czech. Adding English later then means filling in a wired file, not refactoring 80 components.
- **Every key present in every locale file.** A missing key is a runtime blank.
- `mystrings.d.ts` matches the locale files exactly.
- Key names describe **purpose**, not content: `NoResultsMessage`, not `ZadneVysledky`. Content changes; purpose does not.
- Never build a sentence by concatenating fragments - word order differs between languages. One key with a placeholder.
- Czech has three plural forms. Separate keys per form, chosen at the call site.

Exempt from `strings.X`: log messages, developer-facing error text, `data-*` values and CSS class names.

Procedure: `spfx-localization`.
