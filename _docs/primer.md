# TKM Primer

**Project:** Termux Key Manager  
**Repository:** `FocusTorn/termux-key-manager`

> Read this first when entering TKM in a new coding session.

TKM is a small configuration manager for Termux keyboard behavior and the shell helpers that support it.

## Mission

TKM turns declarative keyboard definitions into the user's Termux configuration:

    macros.jsonc
        |
        +--> macros.py
        +--> properties.py -> ~/.termux/termux.properties
        +--> helpers.py    -> ~/.termux/helpers.sh + ~/.bashrc
        +--> tmux.py       -> ~/.tmux.conf
        |
        +--> update.py coordinates the update

`macros.jsonc` is the source of truth.

## Current scope

TKM owns:

- keyboard definitions and layout
- popup definitions
- ordered macro, shell, and tmux actions
- generated Termux `extra-keys`
- generated shell helpers
- generated Bash history configuration
- generated tmux integration
- clipboard workflows implemented by those helpers
- update behavior
- tests for the above

TKM does not own a shell, PTY, terminal-output recorder, terminal-sidecar, plugin transport, receiver, or terminal-session pipeline.

TAP is a separate project. Do not introduce TAP architecture or historical PTY experiments into TKM.

## Source files

    macros.jsonc   authoritative keyboard definitions
    macros.py      definition and action conversion
    properties.py  Termux extra-keys generation
    helpers.py     shell helpers and Bash integration
    tmux.py        tmux configuration generation
    jsonc.py       JSONC comment stripping
    config.py      project and generated-file paths
    update.py      update entry point
    tests/         behavioral coverage

## Generated files

    ~/.termux/termux.properties
    ~/.termux/helpers.sh
    ~/.bashrc
    ~/.tmux.conf

TKM owns only the generated portions described in `generated-files.md`. User configuration outside those portions must be preserved.

## Available TKM commands

The generated helper file currently provides:

    cpy
    cpy_all
    cpy_pytest
    clr
    refresh

See `_docs/commands.md` for exact behavior.

These are shell helpers. They are not separate TKM executables.

## Macro actions

An `actions` list is ordered and supports exactly one action type per entry:

    { "macro": "..." }
    { "shell": "..." }
    { "tmux": "..." }

See `_docs/actions.md`.

## Normal development flow

1. Read this primer.
2. Read the relevant detailed document.
3. Inspect the current implementation and tests.
4. Change the smallest relevant source file.
5. Run focused tests.
6. Verify generated output when the change crosses a generation boundary.
7. Run the broader regression checkpoint when the completed slice warrants it.
8. Update documentation when behavior or architecture changes.

Do not infer current TKM behavior from removed experiments or historical code.

## Documentation map

- `_docs/architecture.md` — system boundaries and data flow
- `_docs/macros.md` — source definition format
- `_docs/actions.md` — action semantics
- `_docs/commands.md` — generated shell commands
- `_docs/termux-integration.md` — Termux integration
- `_docs/generated-files.md` — generated-file ownership
- `_docs/clipboard.md` — clipboard workflows
- `_docs/tmux.md` — tmux integration
- `_docs/installer.md` — current update/installation boundary
- `_docs/testing.md` — test coverage and strategy
- `_docs/development.md` — development workflow

The primer is the entry point. Detailed documents describe the current implementation.
