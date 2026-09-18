# Actions

An actions list expresses ordered work associated with one key definition.

Each action object must contain exactly one supported action field:

- macro
- shell
- tmux

## macro

Injects a Termux macro fragment directly.

Example: { "macro": "TAB" }

## shell

Converts a shell command into Termux macro tokens. Spaces become SPACE, tabs become TAB, newlines become ENTER, and a command that does not already end in ENTER receives one.

Example: { "shell": "clr" }

## tmux

Requests a named TKM tmux action.

Example: { "tmux": "cancel-copy-mode" }

The action has two coordinated sides: macros.py emits its private terminal sequence, and tmux.py creates the matching tmux user-key binding.

Actions are compiled in source order.

Unknown action types and unknown tmux action names raise ValueError; they are not silently ignored.