# Termux Integration

TKM integrates with Termux through generated configuration and shell helpers.

## Keyboard configuration

properties.py reads macros.jsonc, converts each layout definition, and writes the extra-keys setting to:

    ~/.termux/termux.properties

Existing properties outside extra-keys are preserved.

## Shell helpers

helpers.py generates:

    ~/.termux/helpers.sh

It also updates a marked TKM block in:

    ~/.bashrc

The Bash block supplies generated HISTIGNORE settings and sources the helper file.

## tmux

tmux.py generates a marked section in:

    ~/.tmux.conf

## Reload

After generation succeeds, update.py invokes:

    termux-reload-settings

A failed generation or reload causes the update operation to report failure.

TKM configures Termux. It does not replace the normal Termux shell or terminal execution path.