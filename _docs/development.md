# Development

## Entry point

Start with:

    _docs/primer.md

Then read the detailed document for the behavior being changed.

## Source-first workflow

For declarative keyboard behavior:

    macros.jsonc
        |
        v
    implementation
        |
        v
    focused tests
        |
        v
    generated-output verification
        |
        v
    broader regression checkpoint

Keep source intent in `macros.jsonc`.

## Module boundaries

Use the module responsible for the behavior:

- `macros.py` — definition and action conversion
- `properties.py` — Termux keyboard layout generation
- `helpers.py` — shell helpers and Bash integration
- `tmux.py` — tmux configuration
- `jsonc.py` — JSONC comment handling
- `update.py` — generation orchestration

## Change discipline

Keep changes narrow and preserve unrelated behavior.

Do not patch generated files as a permanent solution.

When a change affects generated configuration, verify the generated result in addition to focused tests.

## Documentation discipline

Documentation describes the current repository.

Do not carry removed PTY, terminal-sidecar, receiver, plugin, or experiment architecture into active TKM docs.

TKM and TAP are separate projects. TKM documentation should describe TKM, not establish a live dependency on TAP.

## Evidence

Treat inspected files, command output, and test results as evidence.

Do not claim verification that was not actually performed.