# Clipboard Workflows

TKM's clipboard helpers use tmux capture and the Termux clipboard commands.

## cpy

Captures the current tmux pane.

The generated pipeline:

1. capture the pane
2. remove the triggering `cpy` command
3. remove trailing blank lines
4. send the result to `termux-clipboard-set`

## cpy_all

Captures the current tmux pane including scrollback.

It applies the same trigger-command and trailing-blank cleanup before sending the result to the clipboard.

## cpy_pytest

Operates on existing clipboard content.

It:

1. reads the clipboard with `termux-clipboard-get`
2. searches for pytest progress lines ending in `[100%]`
3. selects the latest matching run
4. replaces the clipboard with that result section

If no match is found, the original clipboard content is retained.

## Important distinction

Bash history contains commands. It does not contain terminal output.

TKM obtains terminal content for copying through tmux capture, then optionally transforms that captured text.

## Related helpers

`clr` clears terminal state.

`refresh` regenerates TKM configuration and reloads the generated shell environment.

See `_docs/commands.md` for the complete helper behavior.