# Clipboard Workflows

TKM provides clipboard helpers through the generated ~/.termux/helpers.sh.

## cpy

Captures the current tmux pane, removes the triggering cpy command, trims trailing blank lines, and sends the result to the Termux clipboard.

## cpy_all

Captures the current tmux pane including scrollback, removes the triggering cpy_all command, trims trailing blank lines, and sends the result to the Termux clipboard.

## cpy_pytest

Reads current clipboard content and searches for the final recognized pytest progress line ending in [100%]. When found, it replaces the clipboard with the output beginning at that result section.

This is a formatting helper for already captured test output. It does not obtain terminal output from Bash history.

Bash history records commands, not terminal output.

## Related helpers

clr clears the terminal state, using the active tmux path when running under tmux.

refresh reruns the TKM update path and reloads the generated helper environment.