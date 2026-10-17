# Native Tmux Copy Refactor — Roadmap

**Status updated:** 2026-10-17  
**Implementation status:** Not started; runtime proof is still in progress.

## Objective

Replace the legacy **cpy_*** shell-helper copy path with native tmux action
execution. Provide one shared copy executor for three callers:

- **copy_entire_pane** — available pane history start through the current pane
  cursor.
- **copy_viewport** — visible viewport line 0 through the current pane cursor.
- **copy_subset** — semantic result ranges, initially pytest output and
  **Patch Failed** output.

All three actions must work from **root**, **copy-mode**, and
**copy-mode-vi**. The clipboard path must be proven. The legacy helpers and all
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

These last three checks used a test binding, not TKM's actual configured
macros. They prove individual tmux operations only.

### Open work

- [x] Prove the root binding's selection anchor and visible range.
- [ ] Prove the full binding-driven selection-to-clipboard path end-to-end.
- [ ] Prove the equivalent action behavior in copy-mode and copy-mode-vi.
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

**Status: in progress — selection anchor and visible range passed; clipboard transfer remains unproven.**

- Bind Ctrl+G to enter copy mode, move to history-top, move to line start,
  and begin selection.
- [x] Confirm the cursor/selection anchor is at the first marker and that
  moving down to line end visibly selects the first two fixture lines.
- Extend selection to the intended end, use
  copy-pipe-and-cancel with termux-clipboard-set, and inspect the clipboard.
- Verify the exact expected text and confirm that before/after markers are
  excluded.
- Record each successful increment separately in the progress log.

**Exit condition:** one root-table binding selects a known marker range and
copies exactly that range.

### Gate 3 — Establish the three execution contexts

Run the action and verify its state changes independently from:

1. root
2. copy-mode
3. copy-mode-vi

Do not assume an entry or cancellation sequence that works from root works
when copy mode is already active. Keep the executor mechanics shared; use
context-specific dispatch only where runtime evidence requires it.

**Exit condition:** the action's expected selection and exit behavior is
proven in all three contexts, without state leakage.

### Gate 4 — Prove semantic subset contracts

**Pytest range**

- Start at the last relevant pytest result/progress line plus one line, per
  the agreed contract.
- End at the line immediately before the final live terminal prompt.
- Exclude the prompt itself.

**Patch Failed range**

- Start at Patch Failed.
- End at the line immediately before the final live terminal prompt.
- Exclude the prompt itself.

Also prove behavior for repeated/missing markers, blank lines, multiline
output, unrelated output, and cases where no safe endpoint can be found.
Fail safely rather than copying a guessed range.

**Exit condition:** positive and negative cases demonstrate the boundary rules
against controlled content, including the real prompt-boundary case.

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
