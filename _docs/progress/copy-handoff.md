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
- The isolated root Ctrl+G binding copied exactly TKM_CONTEXT_BEFORE and
  TKM_CONTEXT_START to the Android clipboard through the copy pipe. The
  selected buffer has no trailing newline.
- A separate isolated Ctrl+G binding in the `copy-mode` table (with
  `mode-keys emacs`) copied the same two lines to Android clipboard, left the
  matching tmux paste buffer, and exited copy mode (`PANE_IN_MODE=0`). The
  clipboard output had no trailing newline after `TKM_CONTEXT_START`.

These are test bindings and manually selected ranges, not a completed TKM
implementation. Root and `copy-mode` have passed. `copy-mode-vi` is explicitly
out of scope by the 2026-10-17 decision below; actual TKM binding integration
and semantic boundary discovery remain untested. Source-level research found
a tmux 3.7c prompt-line flag candidate (`capture-pane -F`), but its availability
in the target shell has not been runtime verified.

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
`source-file` registered the command list correctly. The selection-only
binding visibly highlighted the first two fixture lines.

The subsequent binding added `copy-pipe-and-cancel 'termux-clipboard-set'`.
The first clipboard check remained empty, so that attempt was inconclusive.
A later retry superseded that state for the isolated root-binding path: the
server was recreated from the outer Termux shell (with `TMUX` unset), the
binding was loaded and verified, and a subsequent attach/copy/detach cycle
returned exactly `TKM_CONTEXT_BEFORE` and `TKM_CONTEXT_START`. The buffer
was 36 bytes with no trailing newline, matching the clipboard output. The
cause of the initial empty read remains unknown; the end-to-end root binding
is now **PASS**. The user confirmed seeing `TKM-PROOF:proof` in the attached
Test Session and pressing Ctrl+G there, resolving the earlier ambiguity about
where the interactive trial occurred. The later `copy-mode` trial also passed;
`copy-mode-vi` and TKM bindings remain untested.

## Immediate next action

Continue with OSC 133; do not switch to visible-prompt matching. The user's
full-history prompt grep found no `P` lines. The direct-emission test then
showed only twelve blank rows because the capture was truncated with `tail`;
that result is inconclusive and does not show whether the sentinel lines were
present earlier in the capture.

Use a disposable pane to emit the sequences directly, bypassing interactive
`send-keys` parsing:

```sh
(
    probe="tkm-osc133-probe-$$"
    tmux new-session -d -s "$probe" "sh -c 'printf \"\\033]133;A\\007TKM_OSC133_A_PROBE\\n\\033]133;B\\007TKM_OSC133_B_PROBE\\n\\033]133;C\\007TKM_OSC133_C_PROBE\\n\\033]133;D;0\\007\"; sleep 30'" || exit 1
    trap 'tmux kill-session -t "$probe" 2>/dev/null || true' EXIT
    sleep 1
    tmux capture-pane -pF -t "$probe:0.0" -S - | sed -n 'l'
)
```

First verify `TKM_OSC133_A_PROBE`, `TKM_OSC133_B_PROBE`, and
`TKM_OSC133_C_PROBE` all appear in the untruncated output. Then inspect the A
line for `P` and the C line for `O`; B marks the command-start transition. If
the strings are missing, report the entire raw capture; the controlled test
still has not run successfully. If they show the expected flags but the regular zsh prompt is
unmarked, investigate the actual prompt framework's OSC 133 support before
changing hooks. The `Patch Failed` selector remains deferred. Once prompt
flags work, return to the pytest range contract and tests in the existing
`_test/test_pytest_clipboard.py`, using the normal project runner.

**Scope decision (2026-10-17):** do not run a `copy-mode-vi` trial. Vi-mode
proof is intentionally excluded from this refactor's acceptance criteria. The
required isolated contexts are root and emacs-style `copy-mode`; no claim is
made about invocation from the vi key table.

## Constraints

- No TKM source changes until behavior contracts are understood and tests are
  written first.
- Explicitly distinguish PASS, FAIL, INCONCLUSIVE, invalid setup, and
  untested behavior.
- Never infer that an operation works just because its binding is stored.
- Keep selection, semantic boundary discovery, mode behavior, and clipboard
  output as independently verified stages.
