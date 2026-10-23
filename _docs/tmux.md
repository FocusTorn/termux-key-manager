# tmux Integration

tmux is an integration dependency for TKM's current terminal and clipboard workflows.

## Action discovery

`tmux.py` scans source definitions and nested popup definitions for `tmux` actions.

Duplicate action names are reduced to one generated binding.

A `tmux` action is not a shell command. It does not become a Bash command and therefore is not included in Bash `HISTIGNORE`.

## Private user keys

Each supported action receives a tmux user key.

The corresponding terminal sequence is emitted by `macros.py` and registered by `tmux.py`.

For each action, bindings are generated in both:

    copy-mode
    copy-mode-vi

The sequence is private to the TKM/tmux integration. It is the transport between the Termux macro and the tmux binding, rather than a command typed into Bash.

## Registered actions

| Action | Sequence suffix | Runtime behavior |
|---|---:|---|
| `copy_mode_exit` | `30012` | Cancel active copy mode |
| `copy_entire_pane` | `30013` | Run shared executor on available pane history |
| `copy_subset` | `30014` | Run shared executor with pytest-range selection |
| `clear_terminal` | `30015` | Use context-specific native tmux commands |
| `copy_viewport` | `30016` | Run shared executor on visible viewport |

The three copy actions invoke `copy_executor.py` with the targeted
`#{pane_id}`. Successful copies update the tmux paste buffer and Termux
clipboard using `termux-clipboard-set`.

## Mixed action sequences

A definition can combine an input macro and a shell action:

    "actions": [
        { "macro": "PASTE" },
        { "shell": "refresh" }
    ]

The actions are emitted in source order. A `tmux` action is not a Bash
command, so it does not belong in `HISTIGNORE`.

## Generated key tables

Bindings are generated for root, `copy-mode`, and `copy-mode-vi`. Runtime
acceptance checks cover root and emacs-style `copy-mode`; `copy-mode-vi` is
explicitly out of scope. The generated configuration sets:

    set -g assume-paste-time 0

Before new bindings are written, `tmux.py` clears stale TKM user-key
assignments and bindings in the managed range.

## Copy key mapping

- CPY_ALL main key -> `copy_entire_pane`, including available scrollback.
- CPY_ALL popup labelled COPY -> `copy_viewport`, visible viewport only.
- CPY_TEST -> `copy_subset`, semantic pytest result range.
- CPY_PASTE emits `PASTE ENTER` before invoking `copy_entire_pane`.

The subset selector uses flags from `capture-pane -pF -S -` and requires a
pytest progress row ending in `[100%]` before the final prompt-marked row.
The `Patch Failed` selector remains deferred.

## Replacement

TKM maintains a marked block in:

    ~/.tmux.conf

When tmux actions are no longer required, the generated TKM block is removed.

Existing configuration outside the TKM block is preserved.

## Responsibility boundary

TKM declares and generates the integration. tmux interprets the resulting configuration. TKM does not replace tmux or treat tmux actions as shell commands.
