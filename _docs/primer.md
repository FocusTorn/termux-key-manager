# TKM Primer

**Project:** Termux Key Manager  
**Repository:** `FocusTorn/termux-key-manager`

> Read this first when entering TKM in a new coding session.

TKM manages a Termux keyboard configuration and the shell helpers that support it.

## Mission

TKM turns one source definition into the user's Termux configuration:

```
macros.jsonc
    ↓
Python generators
    ↓
Termux configuration + shell helpers + tmux configuration
```

The source of truth for keyboard definitions is `macros.jsonc`.

TKM is a configuration manager. It is not a shell, PTY manager, terminal recorder, terminal-output capture system, or terminal-sidecar project.

## What belongs in TKM

- keyboard and popup definitions
- macro/action conversion
- generated Termux properties
- generated shell helpers
- generated Bash history configuration
- generated tmux configuration
- clipboard workflows implemented by those helpers
- safe installation and update behavior
- tests for the above

## What does not belong in TKM

Do not add terminal-sidecar, PTY, plugin, receiver, transport, terminal-output recording, or experimental terminal-hook architecture here.

Those concerns were explored historically but are outside TKM's current scope. TKM and TAP are separate projects.

## Important source files

```
macros.jsonc   source definitions
macros.py      macro/action conversion
properties.py  Termux extra-keys generation
helpers.py     shell helper and .bashrc generation
tmux.py        tmux configuration generation
config.py      project and generated-file paths
update.py      update entry point
tests/         behavioral coverage
```

## Generated user files

TKM writes generated configuration to:

```
~/.termux/termux.properties
~/.termux/helpers.sh
~/.bashrc
~/.tmux.conf
```

Generated sections are marked so TKM can replace its own content without treating the surrounding user configuration as TKM-owned.

## Development rule

Before changing behavior:

1. Read this primer.
2. Read the relevant detailed document.
3. Inspect the current implementation and tests.
4. Make the smallest change that satisfies the requirement.
5. Run the relevant tests.
6. Verify generated output when the change crosses a generation boundary.
7. Update the relevant documentation when behavior or architecture changes.

Do not infer current behavior from old experiments or historical code.

## Documentation map

- `_docs/architecture.md` — current system boundaries and data flow
- `_docs/macros.md` — source definition format and conversion
- `_docs/actions.md` — action semantics
- `_docs/termux-integration.md` — generated Termux integration
- `_docs/generated-files.md` — generated-file ownership
- `_docs/clipboard.md` — clipboard helpers
- `_docs/tmux.md` — tmux integration
- `_docs/installer.md` — installation/update model
- `_docs/testing.md` — test strategy
- `_docs/development.md` — development workflow

The primer is the map. Detailed documents are the authority for their respective subjects.
