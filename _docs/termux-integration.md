# Termux Integration

TKM integrates with normal Termux configuration through generated files.

## Keyboard

`properties.py` reads `macros.jsonc`, converts the layout, serializes it as JSON, and writes:

    ~/.termux/termux.properties

Only the `extra-keys` setting is replaced. Other properties are preserved.

## Helpers

`helpers.py` generates:

    ~/.termux/helpers.sh

The generated file contains the TKM shell functions and the generated `HISTIGNORE` value.

## Bash

The same module maintains a marked section in:

    ~/.bashrc

The generated section exports `HISTIGNORE` and sources `~/.termux/helpers.sh`.

On subsequent updates the existing TKM block is replaced rather than appended indefinitely.

## tmux

`tmux.py` maintains a marked section in:

    ~/.tmux.conf

The section is derived from tmux actions present in the source definitions.

## Reload

`update.py` performs generation and then invokes:

    termux-reload-settings

If generation fails, the reload is not reached and the update reports failure.

## Execution boundary

The normal Termux Bash remains the shell.

TKM supplies keyboard macros and shell helpers around that environment. It does not replace or wrap the shell, take over the PTY, or provide a terminal-output capture service.