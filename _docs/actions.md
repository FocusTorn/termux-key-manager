# Actions

An `actions` list expresses ordered work associated with one key definition.

Each action object must contain exactly one supported action field:

- `macro`
- `shell`
- `tmux`

## macro

Injects a native Termux macro fragment directly.

    { "macro": "TAB" }

## shell

Converts a shell command into Termux macro tokens.

    { "shell": "clr" }

Conversion rules:

- space -> `SPACE`
- tab -> `TAB`
- newline -> `ENTER`
- a command without a final `ENTER` receives one

The command itself is not executed by Python during macro conversion. It is emitted into the Termux macro.

## tmux

Requests a named tmux integration action.

    { "tmux": "cancel-copy-mode" }

The same action is represented on two sides:

1. `macros.py` emits its private terminal sequence.
2. `tmux.py` generates the matching tmux user-key binding.

## Ordering

Actions are compiled in source order.

For example:

    [
        { "tmux": "cancel-copy-mode" },
        { "shell": "cpy_all" }
    ]

first emits the tmux action and then the clipboard helper.

## Validation

An action that is not a dictionary is invalid.

A dictionary containing anything other than exactly one of `macro`, `shell`, or `tmux` is invalid.

An unknown tmux action name is invalid.

Current code raises `ValueError` for these cases rather than silently ignoring them.

## Current tmux action

The only currently registered tmux action is:

    cancel-copy-mode
