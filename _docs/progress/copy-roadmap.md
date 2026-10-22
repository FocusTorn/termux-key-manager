# Native Tmux Copy Refactor — Roadmap

**Status updated:** 2026-10-22  
**Implementation status:** Live OSC 133 markers and focused pytest selector tests are verified. The shared native copy executor and three action bindings are implemented; the corrected focused executor contract tests are user-reported green. Broader regression and production Termux runtime verification remain pending. The initial assertion mismatch and corrected rerun are recorded in [Runtime Log §§20–21](copy-runtime-log.md#21-focused-executor-test-rerun-reported-green-2026-10-22).

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
- [x] Define the pytest subset boundary contract and write positive/negative selector tests before implementing the parser.
- [x] Run the selector tests through the project's normal `_test/run` harness (user-reported green on 2026-10-22).
- [x] Integrate the selector into the central native copy executor and wire all three callers (runtime verification pending).
- [x] Remove legacy cpy_* implementation and binding references from generated runtime code and action definitions.
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

**Status: live prompt/output marker proof and focused selector test run passed on 2026-10-22.** The
active shell is Zsh 5.9.2 with `ZSH_THEME=focused2-termux`, using the custom
Oh My Zsh theme at
`FocusTorn/zsh-customized-overlay/zsh/custom/themes/focused2-termux.zsh-theme`.
The source initially had no OSC 133 markers. The integration change is
committed at
https://github.com/FocusTorn/zsh-customized-overlay/commit/9a61d8ce444132b55435ddc3080ee964e80e476c
and live prompt/output flags were verified on 2026-10-22; see
[Runtime Log §15](copy-runtime-log.md#15-live-osc-133-promptoutput-flags-confirmed-2026-10-22).
The `Patch Failed` range remains deferred.

**Preferred boundary mechanism: OSC 133.** `capture-pane -F` exposes tmux
line flags (`P` prompt and `O` output); inspect these flags rather than
matching visible prompt text. The earlier live capture had `X ~ ❯ tkm` and
no `P`. In tmux 3.8, `X` means extended cells and `W` marks wrapping;
`WX` is not a prompt flag. See:
https://fossies.org/diffs/tmux/3.7c_vs_3.8/cmd-capture-pane.c-diff.html

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

1. [x] Verify controlled OSC 133 handling. The disposable pane showed
   `P TKM_OSC133_A_PROBE`, `- TKM_OSC133_B_PROBE`, and
   `O TKM_OSC133_C_PROBE`.

2. [x] Identify the live prompt source and marker-free state. Runtime
   diagnostics reported Zsh 5.9.2 and `ZSH_THEME=focused2-termux`; neither
   `starship`, `oh-my-posh`, nor `p10k` was installed. The theme had no
   OSC 133 markers.

3. [x] Commit OSC 133 A/B/C/D integration to the theme source. The update
   preserves the existing prompt under zero-width markers, emits C in
   `preexec`, and emits D with the command status in a first-position
   `precmd` hook.

4. [x] Sync and reload the shell, then inspect live prompt/output flags.

   The user ran the sync/reload sequence and the probe. The capture showed
   `PX` on the prompt top-rule row and `O TKM_OSC133_OUTPUT_PROBE` on the
   command output row. This passes live marker integration. It does not prove
   pytest semantic selection or production action behavior.

   The detailed dated evidence is in
   [Runtime Log §15](copy-runtime-log.md#15-live-osc-133-promptoutput-flags-confirmed-2026-10-22).

5. [x] Add selector behavior tests and a pure parser for the agreed
   range contract. The tests cover latest-run selection, missing prompt and
   progress boundaries, blank/multiline evidence, prompt-like output without
   `P`, and malformed capture rows. The parser is not yet wired into TKM's
   copy actions.

6. [x] Run the focused tests with the normal project runner (user reported green):

   ```sh
   ./_test/run test_pytest_clipboard.py
   ```

   The first invocation was rejected before tests ran because `_test/run`
   passed both the suite directory and the extra filename. The wrapper was
   corrected, and the user subsequently reported the focused run as green.

**Exit condition: PASS.** Live prompt/output markers are verified and the user
reported the focused positive/negative selector tests green.

### Gate 5 — Integrate selector into the native copy executor

**Status: implementation committed; runtime verification pending.** The
shared `copy_executor.py` now dispatches whole-pane, viewport, and pytest
subset copies. Macro bindings call it directly, and generated `helpers.sh`
no longer contains the legacy `cpy_*` functions. Successful copies update the
tmux paste buffer and send the same text to `termux-clipboard-set`. The
selector fails closed when required prompt/progress boundaries are absent.

The first user-run `./_test/run test_copy_executor.py` reported **1 failed, 5 passed** because the assertion expected a standalone `-F` argv element while the executor sends the documented combined `-pF` option. The assertion was corrected, and the user subsequently reported the focused rerun green; see [Runtime Log §§20–21](copy-runtime-log.md#21-focused-executor-test-rerun-reported-green-2026-10-22). This remains mocked contract-test evidence, not production runtime proof.

- [x] Add the pure pytest selector and pass its focused tests (user-reported).
- [x] Add executor contract tests for each action, clipboard output, fail-closed
  selection, and cancellation from copy mode.
- [x] Wire the three actions to the shared executor and remove legacy helper
  implementations from generated runtime code and action definitions.
- [x] Re-run the focused executor tests after correcting the combined `-pF` assertion (user-reported green; Runtime Log §21).
- [ ] Run `./_test/run`, review the Testmon-selected coverage, and verify generated configuration in Termux.
- [ ] Runtime-test the production actions from root and emacs-style
  `copy-mode`, including clipboard contents and mode exit.

The native tmux `load-buffer -w` clipboard path remains untested; the executor
uses the already-proven `termux-clipboard-set` endpoint instead. The
`copy-mode-vi` table remains out of scope, and `Patch Failed` selection is
deferred.

**Exit condition:** executor and regression tests pass, and the three
production actions are runtime-verified in both required contexts.

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
- Native tmux selection is preferred; the proven `termux-clipboard-set` endpoint
  is used by the shared tmux action executor. tmux's native `load-buffer -w`
  terminal clipboard path remains untested.
- capture-pane -b is a tmux paste-buffer operation, not a clipboard write.
- The cursor_y format is not assumed to represent the copy-mode cursor.
- Do not change TMUX_ACTION_NATIVE or binding representation by assumption;
  inspect consumers and tests when implementation begins.
