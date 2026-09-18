# tmux Integration

tmux is an integration dependency for TKM's current terminal and clipboard workflows.

## Action discovery

`tmux.py` scans source definitions and nested popup definitions for `tmux` actions.

Duplicate action names are reduced to one generated binding.

## Private user keys

Each supported action receives a tmux user key.

The corresponding terminal sequence is emitted by `macros.py` and registered by `tmux.py`.

For each action, bindings are generated in both:

    copy-mode
    copy-mode-vi

## cancel-copy-mode

The current supported action is:

    cancel-copy-mode

Its private terminal sequence is:

    ESC [ 5 ; 3 0 0 1 2 ~

The generated tmux binding maps that user key to:

    send-keys -X cancel

The generated configuration also sets:

    set -g assume-paste-time 0

## Replacement

TKM maintains a marked block in:

    ~/.tmux.conf

When tmux actions are no longer required, the generated TKM block is removed.

Existing configuration outside the TKM block is preserved.

## Responsibility boundary

TKM declares and generates the integration. tmux interprets the resulting configuration.