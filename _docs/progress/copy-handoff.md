# Native Tmux Copy Refactor — Handoff

**Snapshot date:** 2026-10-17  
**Repository:** FocusTorn/termux-key-manager  
**Branch:** main  
**Implementation:** Not started

## Mission

Replace TKM's cpy_* shell-helper copy behavior with native tmux actions. The
target has one shared copy executor and three callers: copy_entire_pane,
copy_viewport, and copy_subset. There must be no legacy fallback or second
implementation.

## Read these files first

1. [Progress workspace guide](README.md) — rules for keeping this handoff,
   the log, and roadmap synchronized.
2. [Copy roadmap](copy-roadmap.md) — current gate order and exit conditions.
3. [Copy runtime progress log](copy-runtime-log.md) — observed tests and
   failed/inconclusive trials.
4. [R1.1 tmux internals](../research/r1_1-tmux-internals.md) and
   [R1.2 TKM implications](../research/r1_2-tkm-implications.md) — source
   analysis and architecture constraints.

## What is proven

- Manual tmux copy-mode selection copied the available pane history, the
  visible viewport, and an explicitly selected three-line range.
- The Termux clipboard utilities work, and the copy-pipe-and-cancel path to
  termux-clipboard-set copied manually selected text.
- In an isolated attached client, root-table Ctrl+G invoked a visible
  display-message binding.
- A root binding entered copy mode.
- A chained root binding, copy-mode followed by send-keys -X history-top,
  entered copy mode and moved the cursor to 1,1.
- The root Ctrl+G test binding started selection at history-top; after moving
  down and to line end, fixture lines 1–2 were visibly highlighted.

These were test bindings and manually selected ranges, not a completed TKM
implementation or proof across all three key tables.

## Most recent correction

The isolated fixture used sleep 300 (five minutes). The run created around
03:18 and attached around 03:23 returned [exited], matching expiration of the
foreground test command. The missing server is therefore best explained by
the fixture ending, not by copy-mode behavior. Ctrl+B, then D, returns the
client to Termux by detaching; do not treat that alone as evidence that the
server was killed.

An earlier all-in-one binding did not place the expected markers on the
clipboard; it placed literal termux-clipboard-get command text there. That
trial remains inconclusive because the correct binding/client/pane state was
not established throughout the attempt.

The direct multi-command `bind-key` invocation at the outer zsh prompt returned
`not in a mode`. Loading the binding from a tmux configuration file with
`source-file` registered the command list correctly. The current selection
binding then visibly highlighted the first two fixture lines.

## Immediate next action

Resume at Roadmap Gate 2 using the existing long-lived `proof` session. Keep
the successful sequence and append `copy-pipe-and-cancel` with
`termux-clipboard-set` to the root Ctrl+G binding, so the binding copies the
currently selected first two lines and exits copy mode. Store the sequence in
a tmux configuration file and load it with `source-file`; then verify it with
`list-keys`, attach, and press Ctrl+G.

Detach back to Termux and inspect `termux-clipboard-get`. Expected content is
exactly `TKM_CONTEXT_BEFORE` and `TKM_CONTEXT_START` on separate lines, with
no other marker lines. Keep the test isolated and do not change TKM source.
After the trial, record the result in the runtime log, update roadmap status,
and rewrite this handoff last.

## Constraints

- No TKM source changes until behavior contracts are understood and tests are
  written first.
- Explicitly distinguish PASS, FAIL, INCONCLUSIVE, invalid setup, and
  untested behavior.
- Never infer that an operation works just because its binding is stored.
- Keep selection, semantic boundary discovery, mode behavior, and clipboard
  output as independently verified stages.
