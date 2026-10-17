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

**Status: blocked on prompt-marker discovery.** The user's tmux 3.8 capture
shows no `P` flags. The controlled `zsh -f` plus `send-keys` trial also
did not show its sentinel text, so it is inconclusive about tmux's handling
of emitted markers. The `Patch Failed` range remains deferred.

**Preferred boundary mechanism: OSC 133.** `capture-pane -F` exposes tmux
line flags (`P` prompt and `O` output); it is a way to inspect semantic
markers, not a replacement for them. Do not fall back to visible-prompt text.

**Pytest subset contract**

- Capture full available history with `capture-pane -pF -S -`.
- Start at the latest valid pytest progress line before the final prompt line,
  including the progress line.
- Exclude the final line flagged `P` and everything after it.
- Preserve content between the boundaries, including blank lines and
  multiline failure evidence.
- Fail closed if either required boundary is missing.
- A prompt-like line without a `P` flag is ordinary output.

**Required proof sequence**

1. Inspect the raw flags from the live shell; the reported sample showed no
   `P` marks.
2. Use a disposable pane whose command emits OSC 133 markers directly, rather
   than typing a nested `printf` through `send-keys`:

   ```sh
   (
       probe="tkm-osc133-probe-$$"
       tmux new-session -d -s "$probe" "sh -c 'printf \"\\033]133;A\\007TKM_OSC133_A_PROBE\\n\\033]133;C\\007TKM_OSC133_C_PROBE\\n\"; sleep 30'" || exit 1
       trap 'tmux kill-session -t "$probe" 2>/dev/null || true' EXIT
       sleep 1
       tmux capture-pane -pF -t "$probe:0.0" -S - | tail -n 12 | sed -n 'l'
   )
   ```

   First confirm that both sentinel strings are visible. Only then interpret
   whether their flags are `P` and `O`.
3. If controlled markers get the expected flags but the normal zsh prompt
   does not, identify the active prompt framework and its supported OSC 133
   integration before changing shell configuration.
4. Once the real prompt is marked, cover repeated/missing progress markers,
   missing prompt markers, blank lines, multiline output and safe failure.
5. Add selector tests to the existing `_test/test_pytest_clipboard.py` and
   use the normal project runner; do not create an isolated pytest harness.

**Exit condition:** direct marker emission is visibly captured with expected
flags, the normal prompt is reliably marked, and positive/negative cases prove
the range contract. No TKM implementation change until the behavior contract
and tests are clear.

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
