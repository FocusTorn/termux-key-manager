# tmux Integration

tmux is an integration dependency for TKM's current terminal and clipboard workflows.

TKM discovers tmux actions from macros.jsonc.

For each supported action, tmux.py assigns a private tmux user key to the corresponding terminal sequence and binds that user key in both copy-mode and copy-mode-vi.

## cancel-copy-mode

The current supported tmux action is cancel-copy-mode.

It is represented by the private terminal sequence:

    ESC [ 5 ; 3 0 0 1 2 ~

The generated binding maps the sequence to tmux's copy-mode cancel action.

## Generated configuration

TKM writes a marked block to ~/.tmux.conf.

If the source definitions no longer require tmux actions, the generated TKM block is removed.

TKM generates the integration; tmux interprets the resulting configuration.