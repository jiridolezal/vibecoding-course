---
name: spfx-property-pane
description: Build a good SPFx property pane - PnP reusable property controls instead of plain text fields, custom IPropertyPaneField controls, reactive versus non-reactive changes, dataVersion and property migration, and keeping tenant URLs out of preconfiguredEntries. Use when adding or changing web part properties, when the user says "property pane", "web part settings", "configuration", "let the site owner choose", or when the property pane is causing refetches.
---

# spfx-property-pane

The property pane is the only part of the solution a site owner ever touches. A column of bare text fields is a bad product.

## Do not hand-roll a control

Check `@pnp/spfx-property-controls` first. It already provides, among others: people picker, list picker, list-item picker, term picker, colour picker, date/time picker, dropdown with search, spin button, swatch colour picker, message, order list, and **collection data** - an editable table of rows, which covers most of what people reach for a custom control to do.

Order of preference:

1. A PnP property control
2. A built-in `PropertyPane*` field
3. `PropertyFieldCollectionData` for anything list-shaped
4. A custom `IPropertyPaneField` - only when the above genuinely cannot express it

See `dont-reinvent` before writing a custom control.

## Structure

Group related fields into pages and groups with real headers. If the pane has more than about eight fields, it needs a second page. Every label and description comes from `strings.X` - see `spfx-localization`.

## Reactive vs non-reactive

By default SPFx applies each keystroke immediately, calling `render()` and remounting the whole provider tree. With a data-loading web part that is one full fetch per character.

```ts
protected get disableReactivePropertyChanges(): boolean {
  return true;
}
```

Use non-reactive whenever a property feeds a data query. Keep reactive only for cheap visual properties where live preview genuinely helps.

## dataVersion and migration

Changing the shape of a property - renaming it, changing its type, splitting one into two - breaks web part instances already placed on pages. They carry the old serialised shape.

When a property's shape changes: bump `dataVersion` and handle the migration so existing instances keep working. Record the change in `docs/decisions/`.

## Defaults

`preconfiguredEntries[].properties` ships with the package to every consumer.

- **Never** a tenant URL, site URL, list GUID or customer name
- Blank, or a genuinely universal default
- The web part must render a configuration placeholder when required properties are empty, not a crash and not an empty div

## Theming from the property pane

Because the palette is applied at runtime through `createTheme()`, colour properties can be exposed to the site owner directly - a PnP colour picker writing into the theme object. Offer this when a customer wants to retune brand colours without a redeploy. Warn that overriding a colour makes contrast the overrider's responsibility.

## Before you finish

- No plain text field where a typed control exists
- No literal strings - all labels from `strings.X`
- `disableReactivePropertyChanges` set if any property drives a fetch
- `preconfiguredEntries` contains no environment-specific value
- `dataVersion` bumped if a property shape changed
