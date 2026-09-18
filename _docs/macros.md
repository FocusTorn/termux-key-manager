# Macro Definitions

`macros.jsonc` is TKM's source of truth.

It contains:

    definitions
    layout

## Definition fields

| Field | Meaning |
|---|---|
| `display` | Label shown on the key |
| `key` | Native Termux key |
| `macro` | Native Termux macro |
| `shell` | Shell command converted to a macro |
| `actions` | Ordered action list |
| `popup` | Popup definition or key |

A definition may contain fields together when the resulting Termux representation supports them.

## Layout

`layout` contains rows of definition IDs. Every referenced ID must exist in `definitions`.

The current layout is:

    SHFT TAB [blank] [blank] PST CLR [blank] [blank] UP [blank]
    CTRL ALT [blank] CPY_ALL CPY_TEST CPY_PASTE [blank] LT DN RT

The blank key is the definition whose ID is a single space.

## Current definitions

The current source includes:

- modifier/navigation keys: `CTRL`, `SHFT`, `ALT`, `TAB`, `UP`, `DN`, `LT`, `RT`
- undo: `UDO`
- clear/refresh: `CLR`
- clipboard/test workflows: `CPY_ALL`, `CPY_TEST`, `CPY_PASTE`
- paste: `PST`
- the blank definition
- `?`, which emits the tmux next-window sequence

## Popups

Popups may be simple strings, such as `PGUP`, or nested definition objects.

Nested popup definitions are passed through the same conversion logic as normal definitions.

## Editing rule

Change keyboard behavior in `macros.jsonc`. Do not patch generated `termux.properties` as the permanent fix.

The source describes intent. Generated files describe the current compiled result.
