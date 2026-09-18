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

## Actions

`actions` is an ordered list of action objects. Each action has exactly one action type:

| Action | Meaning |
|---|---|
| `macro` | Emit a native Termux macro sequence |
| `shell` | Convert a shell command to a macro sequence, including the terminating Enter |
| `tmux` | Emit a private terminal sequence handled by the TKM/tmux integration |

For example:

    "actions": [
        { "tmux": "cancel-copy-mode" },
        { "shell": "cpy_all" }
    ]

The actions are emitted in order. The tmux action does not execute a Bash command; the shell action does.

Shell actions are also included when TKM dynamically builds `HISTIGNORE`, so shell helpers invoked through a macro do not remain in Bash history. Tmux and native macro actions are not included because they are not Bash commands.

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

Nested popup definitions are passed through the same conversion logic as normal definitions. Their `actions` are therefore processed in the same order and their shell actions are also included in the generated `HISTIGNORE`.

## Editing rule

Change keyboard behavior in `macros.jsonc`. Do not patch generated `termux.properties` as the permanent fix.

The source describes intent. Generated files describe the current compiled result.
