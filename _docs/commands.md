# TKM Shell Utilities and Copy Actions

TKM generates shell utilities into `~/.termux/helpers.sh`.

| Function | Purpose |
|---|---|
| `edit_create` | Prepare an edit target/specification |
| `edit_execute` | Apply the prepared edit specification |
| `clr` | Clear/reset terminal state when called from the shell |
| `refresh` | Delegate to the generated `~/.termux/tkm-refresh` script |

Clipboard copying is not implemented by generated shell functions. Keyboard
definitions dispatch through tmux private user keys to `copy_executor.py`.

## Copy key actions

| Key | Action | Purpose |
|---|---|---|
| CPY_ALL main key | `copy_entire_pane` | Capture available pane history |
| CPY_ALL popup labelled COPY | `copy_viewport` | Copy visible viewport |
| CPY_TEST | `copy_subset` | Copy latest valid pytest range before the final prompt-marked row |
| CPY_PASTE | `copy_entire_pane` after `PASTE ENTER` | Emit the paste macro, then copy pane history |

Each successful copy updates the tmux paste buffer and Termux clipboard through
`termux-clipboard-set`. The legacy `cpy`, `cpy_all`, `cpy_test`, and
`cpy_pytest` shell functions are not generated; regression tests intentionally
assert that the old definitions do not return.

## History behavior

TKM derives Bash `HISTIGNORE` from shell commands declared in
`macros.jsonc`, including nested popup shell actions. A `tmux` action is not
a Bash command, so the copy key bindings do not add obsolete `cpy_*` command
names to history-ignore configuration.

## clr and refresh

The `clr` shell function remains available as a shell utility. The CLR key
uses the `clear_terminal` tmux action, while its popup uses `refresh`.
The refresh function delegates to `$HOME/.termux/tkm-refresh`.

## Important boundary

Bash history records commands, not terminal output. Copy actions obtain
terminal text through tmux pane capture.
