# Development

## Entry point

Start with:

    _docs/primer.md

Then read the detailed document covering the behavior being changed.

## Change flow

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

## Source-first rule

When behavior is declarative, change macros.jsonc rather than patching generated output.

Keep transformation logic in the appropriate module:

- macros.py for definition and action conversion
- properties.py for Termux keyboard configuration
- helpers.py for shell and Bash helpers
- tmux.py for tmux configuration
- update.py for orchestration

## Documentation rule

Document current TKM behavior and boundaries.

Do not carry obsolete PTY, terminal-sidecar, receiver, plugin, TAP, or experiment architecture into active TKM documentation. Historical material that belongs to another project remains outside TKM.

Treat command output, test results, and inspected generated files as evidence. Do not claim verification unless it actually occurred.