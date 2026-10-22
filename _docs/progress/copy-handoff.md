# Native Tmux Copy Refactor — Handoff

**Snapshot date:** 2026-10-22  
**Repository:** FocusTorn/termux-key-manager  
**Branch:** main  
**Implementation:** Focused selector tests user-reported green; shared executor and bindings added, runtime verification pending

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
out of scope by the 2026-10-17 decision below. Live OSC 133 integration was
confirmed on 2026-10-22: the user's capture showed `PX` on the prompt top-rule
row and `O` on `TKM_OSC133_OUTPUT_PROBE`. This confirms the flag path in the
target shell, not semantic selection or production action integration.

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

The live OSC 133 proof passed on 2026-10-22. The user's capture included
`PX` on the prompt top-rule row and `O TKM_OSC133_OUTPUT_PROBE` on the output
row. The `X` and `W` flags describe extended cells and wrapping; they are not
prompt boundaries.

A pure parser has been added in `copy_selector.py`:
- Finds the latest valid pytest progress row ending in `[100%]` before the
  final prompt-flagged row.
- Removes tmux flag prefixes while preserving selected text and line endings.
- Returns `None` on missing boundaries or malformed capture rows. Callers must
  leave the clipboard unchanged on `None`.

Focused tests in `_test/test_pytest_clipboard.py` cover latest-run selection,
blank/multiline evidence, missing boundaries, prompt-like output without `P`,
and malformed rows. The user reported the corrected focused run as green.
The earlier runner rejection was an invalid invocation, not a test failure.

A shared `copy_executor.py` now serves `copy_entire_pane`, `copy_viewport`,
and `copy_subset`. It uses tmux capture, preserves the tmux paste buffer with `load-buffer -`, and
uses the proven `termux-clipboard-set` endpoint. It leaves the clipboard
unchanged when subset boundaries fail,
and exits copy mode after actions invoked there. Executor tests and production
binding tests have been added. The first executor test run reported 1 failure
and 5 passes: the test expected a standalone `-F` argv element, while the
executor uses the documented combined `-pF` argument. The test assertion has
been corrected; the focused rerun, broader suite, and production action runtime
verification remain pending.

Run from the TKM repository root:

```sh
./_test/run test_copy_executor.py
```

Then run the broader suite with `./_test/run`. Test root and emacs-style
`copy-mode`; `copy-mode-vi` remains out of scope. `Patch Failed` remains
deferred.

## Constraints

- No TKM source changes until behavior contracts are understood and tests are
  written first.
- Explicitly distinguish PASS, FAIL, INCONCLUSIVE, invalid setup, and
  untested behavior.
- Never infer that an operation works just because its binding is stored.
- Keep selection, semantic boundary discovery, mode behavior, and clipboard
  output as independently verified stages.
