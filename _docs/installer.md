# Installer and Update Model

The repository currently has an update generator, not a separate installer implementation.

## Current update entry point

From the project directory:

    python update.py

`update.py` calls the generators in this order:

1. `generate_helpers()`
2. `build_termux_layout()`
3. `generate_tmux_config()`
4. `termux-reload-settings`

If any step raises an exception, the update reports failure and returns a non-zero status.

## Files that may change

The update path can change:

    ~/.termux/helpers.sh
    ~/.termux/termux.properties
    ~/.bashrc
    ~/.tmux.conf

Ownership rules are documented in `generated-files.md`.

## Repeatability

The generators are designed to replace TKM-owned state rather than accumulate it:

- the TKM `.bashrc` block is replaced
- the TKM `.tmux.conf` block is replaced
- `extra-keys` is replaced structurally
- `helpers.sh` is regenerated

## Current boundary

There is no separate installer implementation in the current repository.

Do not document PTY setup, terminal plugins, package installation, or other historical experiments as part of the current TKM installer architecture.