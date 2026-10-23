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

    { "tmux": "copy_mode_exit" }

The same action is represented on two sides:

1. `macros.py` emits its private terminal sequence.
2. `tmux.py` generates the matching tmux user-key binding.

## Ordering

Actions are compiled in source order.

For example:

    [
        { "macro": "PASTE" },
        { "shell": "refresh" }
    ]

first emits the macro fragment and then the shell command.

## Validation

An action that is not a dictionary is invalid.

A dictionary containing anything other than exactly one of `macro`, `shell`, or `tmux` is invalid.

An unknown tmux action name is invalid.

Current code raises `ValueError` for these cases rather than silently ignoring them.

## Current tmux actions

| Action | Behavior |
|---|---|
| `copy_mode_exit` | Cancel active tmux copy mode |
| `copy_entire_pane` | Capture available pane history and update tmux paste buffer and Termux clipboard |
| `copy_subset` | Select the latest valid pytest progress range before the final prompt-marked row; fail closed when boundaries are missing |
| `copy_viewport` | Copy the visible pane viewport |
| `clear_terminal` | Use context-specific native tmux commands to reset/clear terminal state |

Copy actions dispatch through the shared `copy_executor.py`. Acceptance
testing covers root and emacs-style `copy-mode`; `copy-mode-vi` is out of
scope.
