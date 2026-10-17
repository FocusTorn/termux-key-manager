# Native Tmux Copy Refactor — Roadmap

**Status updated:** 2026-10-17  
**Implementation status:** Not started; Gate 3 is complete for the agreed scope and semantic-boundary work is next.

## Objective

Replace the legacy **cpy_*** shell-helper copy path with native tmux action
execution. Provide one shared copy executor for three callers:

- **copy_entire_pane** — available pane history start through the current pane
  cursor.
- **copy_viewport** — visible viewport line 0 through the current pane cursor.
- **copy_subset** — semantic result ranges, initially pytest output and
  **Patch Failed** output.

All three actions must work from the **root** table and emacs-style
**copy-mode**. The clipboard path must be proven. The **copy-mode-vi** table is
explicitly out of scope for this refactor; do not block work on vi-mode proof
or imply that behavior there has been verified. The legacy helpers and all
references to them must be removed; no legacy fallback or dual implementation
is allowed.

## Current state

### Completed proof and research

- [x] Source-level tmux command semantics documented in
  [R1.1](../research/r1_1-tmux-internals.md).
- [x] TKM architectural implications and target shape documented in
  [R1.2](../research/r1_2-tkm-implications.md).
- [x] Manual copy-mode selection proved for full available history, visible
  viewport, and a known three-line range.
- [x] Termux clipboard set/get round-trip proved.
- [x] The copy-pipe-and-cancel path to termux-clipboard-set proved with
  manually selected text.
- [x] In an isolated client, root-table Ctrl+G dispatch to a visible message
  proved.
- [x] Root-table Ctrl+G entry to copy mode proved.
- [x] The chained root probe, copy-mode followed by history-top, moved the
  cursor to position 1,1.
- [x] A root binding anchored a selection at history-top and visibly
  highlighted fixture lines 1–2 after moving down and to line end.
- [x] The isolated root Ctrl+G binding copied exactly the two intended
  fixture lines to the Android clipboard through the clipboard pipe.
- [x] In the `copy-mode` table with `mode-keys emacs`, an isolated Ctrl+G
  binding copied exactly the first two fixture lines to Android clipboard,
  populated the tmux paste buffer, and exited copy mode.
- [x] The user confirmed the successful root trial was interactive: the
  `TKM-PROOF:proof` status bar was visible and Ctrl+G was pressed inside the
  attached Test Session.

The root and `copy-mode` checks used isolated test bindings, not TKM's actual
configured macros. They prove individual tmux operations only.

### Open work

- [x] Prove the root binding's selection anchor and visible range.
- [x] Prove the isolated root binding's selection-to-clipboard path end-to-end.
- [x] Prove the isolated action behavior in the `copy-mode` table.
- [x] Record `copy-mode-vi` as out of scope; no vi-mode proof is required.
- [ ] Define and test semantic subset discovery and prompt exclusion.
- [ ] Write behavior tests before changing implementation.
- [ ] Implement the central native copy executor and the three callers.
- [ ] Remove legacy cpy_* implementation and binding references.
- [ ] Run focused and broader regressions; verify final repository state.

## Ordered execution plan

### Gate 1 — Keep the interactive test fixture alive

**Status: complete**

The isolated pane used sleep 300, which expired after five minutes. The last
[exited] result aligns with that lifetime; do not misclassify this as a
copy-mode failure.

- Recreate the isolated proof session with a long-lived foreground command
  such as sleep 3600.
- Put known markers in the pane: TKM_CONTEXT_BEFORE, TKM_CONTEXT_START,
  TKM_CONTEXT_RESULT_1, TKM_CONTEXT_RESULT_2, TKM_CONTEXT_AFTER.
- Verify the session and binding, attach, and execute each trial before the
  test process expires.
- Avoid using detachment as a test step unless needed; Ctrl+B, then D, returns
  the client to Termux and can interrupt the observation sequence.

**Exit condition:** a stable isolated session remains available throughout
the multi-step binding trial.

### Gate 2 — Prove selection mechanics from the root table

**Status: complete — the isolated root Ctrl+G binding copied exactly the intended two fixture lines on a subsequent attach/copy attempt.**

- Bind Ctrl+G to enter copy mode, move to history-top, move to line start,
  and begin selection.
- [x] Confirm the cursor/selection anchor is at the first marker and that
  moving down to line end visibly selects the first two fixture lines.
- [x] Extend the selection to the intended end and invoke
  copy-pipe-and-cancel with termux-clipboard-set.
- [x] Verify that the Android clipboard contains exactly
  TKM_CONTEXT_BEFORE and TKM_CONTEXT_START, excluding before/after markers.
- Note: the first post-copy clipboard check was empty; a subsequent
  attach/copy attempt passed. The cause of the first empty read remains
  undetermined.
- Record each successful increment separately in the progress log.

**Exit condition:** one root-table binding selects a known marker range and
copies exactly that range.

### Gate 3 — Establish the required execution contexts

**Status: complete for the agreed scope — root and emacs-style `copy-mode`
pass; `copy-mode-vi` is explicitly out of scope by the 2026-10-17 decision.**

Run the action and verify its state changes independently from:

1. [x] root — isolated root-table binding passed (Gate 2).
2. [x] `copy-mode` — isolated binding passed with `mode-keys emacs`.

Do not assume an entry or cancellation sequence that works from root works
when copy mode is already active. Keep the executor mechanics shared; use
context-specific dispatch only where runtime evidence requires it. These
trials are test bindings, not TKM's production bindings.

No claim is made about invoking the binding from `copy-mode-vi`; that context
is not an acceptance requirement for this refactor.

**Exit condition:** expected selection and exit behavior is proven in both
required contexts, without state leakage.

### Gate 4 — Prove pytest subset and prompt exclusion

**Status: blocked on marker discovery, not on design.** The live-shell probe
returned no `P`-marked lines. Root cause is not yet isolated. The
`Patch Failed` marker range remains deferred.

**Preferred boundary mechanism: OSC 133.** `capture-pane -F` exposes tmux's
line flags derived from OSC 133; it is a way to inspect the markers, not a
competing boundary strategy. Do not fall back to visible prompt text unless
evidence shows the marker approach cannot satisfy the requirement.

**Pytest subset contract**

- Capture all available history with tmux 3.7c line flags
  (`capture-pane -pF -S -`).
- Select from the latest valid pytest progress line before the final prompt
  line, including that progress line.
- Exclude the final line marked with the tmux prompt flag `P`, and exclude
  everything after it.
- Preserve captured text between the boundaries, including blank lines and
  multiline failure evidence.
- If no final prompt marker or no valid pytest progress line exists before it,
  fail closed without copying a guessed range.
- A prompt-like line without the `P` flag is ordinary output.

**Required proof sequence**

1. Capture the raw line prefixes and check `tmux -V`; the previous grep
   returned no `P` lines but hid all other prefixes.
2. In a disposable `zsh -f` tmux session, emit controlled OSC 133 `A` and
   `C` sequences and confirm that `capture-pane -F` labels their lines `P`
   and `O`. This isolates tmux's handling from the user's shell config.
3. Check whether the ordinary live zsh prompt is marked `P`. If the
   controlled test passes but the ordinary prompt is unmarked, identify the
   active prompt framework and configure its supported OSC 133 integration
   before proceeding; do not guess at or overwrite prompt hooks.
4. After automatic prompt marking is established, cover repeated progress
   markers (choose the latest one before the final prompt), missing progress
   markers, missing prompt markers, blank lines, and multiline output.
5. Add tests to the existing `_test/test_pytest_clipboard.py` and use the
   project runner, not a new isolated pytest harness.

**Exit condition:** controlled markers are exposed as expected, the target
shell's real prompt is reliably marked, and positive/negative cases prove
the subset range. No TKM source change until the contract and tests are clear.

### Gate 5 — Write behavior tests and implement

Before modifying TKM source:

- Define observable contracts for entire-pane, viewport, and each subset.
- Cover success, failure, boundaries, mode state, clipboard side effects,
  cancellation, and integration with the action-binding layer.
- Write the tests first and run the new/changed tests directly.
- Implement the smallest coherent slice; correct the test or implementation
  based on the observed failure.
- Keep the legacy helpers out of the target architecture.

**Exit condition:** tests encode the contract, and each implementation slice
passes its focused tests.

### Gate 6 — Regression and repository verification

- Run focused copy-action regression tests.
- Run the repository's broader required test/validation commands.
- Inspect all remaining cpy_* references and remove obsolete calls and
  definitions.
- Verify the diff, working/ref state, and commit history before calling the
  refactor complete.

**Exit condition:** all three callers use the central native executor, all
required tests pass, and no legacy copy path remains.

## Design decisions that remain fixed

- Entire-pane and viewport copying should share selection/clipboard mechanics;
  the start boundary is the primary difference.
- Subset callers should reuse that executor and supply their semantic range.
- Native tmux selection is preferred; the Termux clipboard pipe is acceptable
  when the pipe remains part of the native tmux action.
- capture-pane -b is a tmux paste-buffer operation, not a clipboard write.
- The cursor_y format is not assumed to represent the copy-mode cursor.
- Do not change TMUX_ACTION_NATIVE or binding representation by assumption;
  inspect consumers and tests when implementation begins.
