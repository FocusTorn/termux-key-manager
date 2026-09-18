# TKM Architecture

TKM is a configuration manager for Termux keyboard behavior and its supporting shell helpers.

## System flow

    macros.jsonc
        |
        +--> macros.py
        |       |
        |       +--> native macro definitions
        |       +--> action sequences
        |
        +--> properties.py -> ~/.termux/termux.properties
        |
        +--> helpers.py    -> ~/.termux/helpers.sh
        |                    ~/.bashrc
        |
        +--> tmux.py       -> ~/.tmux.conf
        |
        +--> update.py coordinates generation and reload

## Source of truth

`macros.jsonc` is the authoritative source for keyboard definitions and layout.

The Python modules transform that source into runtime configuration. Generated files are outputs, not alternate sources of truth.

## Action model

Definitions may contain an ordered `actions` list. Each action has exactly one type:

| Action | Transformation | Runtime role |
|---|---|---|
| `macro` | Native Termux macro sequence | Emits keyboard input directly |
| `shell` | Shell command converted to a macro sequence | Executes through the normal Termux shell |
| `tmux` | Private terminal sequence | Reaches the TKM-generated tmux binding |

Actions are emitted in source order.

For example:

    "actions": [
        { "tmux": "cancel-copy-mode" },
        { "shell": "cpy_all" }
    ]

The first action is handled by the tmux integration. The second becomes a normal shell command. Because it is a shell command, it is also included in the dynamically generated Bash `HISTIGNORE`.

Nested popup definitions use the same action conversion and discovery rules.

## Responsibilities

### macros.py

Converts source definitions into native Termux definitions.

It handles:

- direct macro definitions
- shell-to-macro conversion
- ordered actions
- tmux action sequences
- nested popup definitions

### properties.py

Builds the Termux `extra-keys` layout and replaces the existing `extra-keys` property while preserving other properties.

### helpers.py

Generates the TKM shell helper file and updates the marked TKM section in `.bashrc`.

It derives Bash `HISTIGNORE` from shell commands declared in source definitions, including `actions[].shell` entries and nested popup actions.

### tmux.py

Discovers tmux actions declared by the source and generates the matching marked section in `.tmux.conf`.

### update.py

Runs the generators and then invokes `termux-reload-settings`. An exception prevents the success result.

### jsonc.py

Strips line and block comments while preserving comment-like text inside JSON strings.

## Runtime boundaries

TKM configures the Termux environment. It does not replace Bash, own the PTY, capture terminal output as a service, or run a terminal-sidecar process.

Termux remains responsible for terminal and shell execution. tmux remains responsible for tmux behavior.

A `tmux` action is therefore not a Bash command. It uses a private terminal sequence to invoke behavior registered by the TKM-generated tmux configuration.

## Configuration ownership

TKM may modify:

- the `extra-keys` property in `termux.properties`
- the entire generated `helpers.sh`
- its marked block in `.bashrc`
- its marked block in `.tmux.conf`

Unrelated user configuration remains outside TKM ownership.

## Design rule

Keep intent in `macros.jsonc`, transformation in Python, and runtime configuration at the Termux boundary.
