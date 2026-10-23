# Clipboard Workflows

Clipboard keys in `macros.jsonc` dispatch through generated tmux bindings to
the shared `copy_executor.py`. They no longer depend on generated clipboard
shell helper functions.

## Production actions

| Key | Action | Behavior |
|---|---|---|
| CPY_ALL main key | `copy_entire_pane` | Capture available pane history with `capture-pane -pJ -S -` |
| CPY_ALL popup labelled COPY | `copy_viewport` | Capture the visible viewport with `capture-pane -pJ` |
| CPY_TEST | `copy_subset` | Select the latest valid pytest progress range before the final prompt-marked row |
| CPY_PASTE | `copy_entire_pane` after `PASTE ENTER` | Emit the paste macro first, then copy pane history |

Whole-pane and viewport copies trim trailing whitespace on each line and
remove trailing blank rows. Successful content is loaded into the tmux paste
buffer and sent to the Termux clipboard using `termux-clipboard-set`.

## Pytest subset contract

The subset action uses `capture-pane -pF -S -` and the parser in
`copy_selector.py`. It starts at the latest valid progress row ending in
`[100%]` before the last row flagged as a prompt. The prompt row and
everything after it are excluded; content inside the selected range, including
blank lines and multiline evidence, is retained.

If a required boundary is missing or a capture row is malformed, the action
fails closed without replacing the tmux paste buffer or Termux clipboard.
Live selection of a real `Patch Failed` range remains deferred.

## Runtime contexts and limits

All three production actions passed checks from root and emacs-style
`copy-mode`. The `copy-mode-vi` table is explicitly out of scope. The native
tmux `load-buffer -w` clipboard path remains untested; the executor uses the
proven `termux-clipboard-set` endpoint.

## Related utilities

The generated shell utility file provides `clr` and `refresh`, plus edit
helpers. The CLR keyboard macro uses native `clear_terminal`, and its popup
invokes `refresh`.

See `_docs/commands.md` for the current utility/key-action map.
