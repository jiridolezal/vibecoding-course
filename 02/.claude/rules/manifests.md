---
paths:
  - "**/*.manifest.json"
  - "config/package-solution.json"
  - "config/config.json"
---

# Manifest and solution config

- **Every component `id` is a unique GUID.** Never copy one from another component or from the template. Colliding GUIDs break the app catalog in ways that are very hard to diagnose.
- **`preconfiguredEntries[].properties` ships to every consumer.** No tenant URL, site URL, list GUID or customer name. Blank, or a genuinely universal default.
- **`supportsThemeVariants` must match reality.** Do not claim theme support the styles do not deliver.
- New API permissions in `webApiPermissionRequests` are **tenant-wide** and need admin approval. Record them in `docs/permissions.md` and tell the user approval is required, or the solution fails silently for everyone.
- Registering a new component means an entrypoint and manifest pair in `config/config.json`. Separate bundles keep pages fast; share a bundle only when components are always used together.
