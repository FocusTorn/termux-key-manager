# Macro Definitions

macros.jsonc is TKM's source of truth for keyboard definitions.

It contains definitions and layout.

## Definition fields

| Field | Purpose |
|---|---|
| display | Text or symbol shown on the key |
| key | Native Termux key |
| macro | Native Termux macro sequence |
| shell | Shell command converted to a macro |
| actions | Ordered action list |
| popup | Alternate definition or key |

Every ID in layout must exist in definitions.

## Popups

A popup may be a string such as PGUP or PGDN, or a nested definition object. Nested definitions are converted recursively.

## Source versus generated format

Write intent in macros.jsonc. Do not edit generated termux.properties to permanently change behavior. Change the source definition and regenerate.