# Roadmap: CPY_ALL / Native Tmux Copy Refactor (PARTIAL)

**Feature:** copy-refactor
**Parent:** none
**Depends on:** none
**Delivery assessment:** PARTIAL — the shared executor checkpoint is complete, but CPY_ALL does not yet satisfy the M-w whole-pane PRD.

## Objective

Retain the completed shared native tmux copy executor for `copy_entire_pane`, `copy_viewport`, and `copy_subset`, then bring CPY_ALL / M-w whole-pane copying into conformance with `_docs/PRD/2026-09-23-m-w-select-all-copy.md`. CPY_ALL must copy everything before the final shell prompt boundary, exclude that final prompt and all later content, and preserve the retained text exactly.

## End state and acceptance criteria

- [x] The three copy actions use the shared executor and the active generated production path has no legacy `cpy_*` helper implementation/fallback (recorded evidence in legacy log §§18, 24–25; reconciled at PL-0001).
- [x] Recorded test/coverage evidence and the production action matrix cover the accepted root and Emacs-style `copy-mode` scope (legacy log §§24, 28–29; PL-0001). This is inherited user-run evidence, not a test run by the migration agent.
- [ ] CPY_ALL finds the final prompt boundary reliably without visible-prompt-text matching and excludes that prompt and everything after it.
- [ ] CPY_ALL preserves all content before the cutoff exactly: blank lines, trailing whitespace, earlier prompts, and line endings; no trailing whitespace stripping or newline normalization.
- [ ] Missing or invalid boundaries and an empty selection fail closed without overwriting the clipboard.
- [ ] CPY_ALL behavior is tested and observed in the target Termux/tmux runtime, not inferred solely from mocked contract tests.
- [ ] Feature documentation and the implementation-research record agree with the final source and observed behavior.

## Synchronization

**Progress through:** PL-0006

`Progress through` is the newest actual log entry reviewed and reconciled here. Advance it only after appending a material log entry and reconciling the plan.

## Gates

### G1 — Shared executor checkpoint
**Status:** DONE (PL-0001)
**Requires:** none
**Exit condition:** All three callers use the shared executor, active production paths no longer define/invoke the legacy helper family, recorded focused/full coverage is passing, and the production matrix passes from root and Emacs-style `copy-mode`.
**Evidence:** PL-0001, with recorded details in legacy log sections 24 and 28–29.
**Remaining:** none within this gate's accepted executor checkpoint. This gate does not imply CPY_ALL meets the separate M-w PRD.

### G2 — CPY_ALL final-prompt and exact-preservation contract
**Status:** IN PROGRESS
**Requires:** G1 (DONE, PL-0001)
**Exit condition:** A tested whole-pane selector uses a verified prompt-boundary representation, cuts off at the final prompt, retains exactly the preceding content, and leaves the clipboard unchanged when no valid non-empty range exists; target-runtime behavior is demonstrated.
**Evidence:** PL-0002 documents the source mismatch; PL-0005 records expected RED failures; PL-0006 records 23 passing focused Python tests after the source change.
**Remaining:** Verify the exact flagged full-history capture and its final P row on the target Termux/tmux environment; then prove exact clipboard content and fail-closed behavior through the actual CPY_ALL binding in both accepted contexts.

### G3 — Regression, runtime acceptance, and documentation convergence
**Status:** NOT STARTED
**Requires:** G2 (must be DONE with supporting progress-log evidence)
**Exit condition:** Focused tests, the complete suite, target-module coverage report, and CPY_ALL runtime checks pass; the M-w research record and active guides match the proven behavior; all continuity references and markers are synchronized.
**Evidence:** none yet for the remaining CPY_ALL contract.
**Remaining:** Run the focused tests through `./_test/run` and the complete repository suite; generate a fresh coverage report; exercise CPY_ALL in root and Emacs-style copy mode with prompt/whitespace fixtures; run the continuity checker; record only results actually observed.

## Blocked

None. G2 is in progress rather than blocked: the known source/spec mismatch is actionable and has no unresolved external dependency.

## Decisions

### D-001 — One shared executor; no legacy helper fallback [ACTIVE]
Problem/requirement: Whole-pane, viewport, and subset copies must not grow parallel implementations.
Chosen approach: Keep the shared `copy_executor.py` route and remove the `cpy_*` helper family from active production paths.
Why this approach: The recorded production matrix and coverage audit support the shared executor checkpoint.
Evidence / authorization: PL-0001; legacy log sections 18 and 24–29.
Constraints that must survive: No fallback, compatibility function family, or duplicate implementation.
Open alternatives/questions: None for this architectural constraint.

### D-002 — CPY_ALL follows the M-w whole-pane PRD [ACTIVE]
Problem/requirement: The original M-w requirement excludes the final prompt and content after it while preserving all earlier content exactly.
Chosen approach: Use `capture-pane -pF -S -`; identify the last P-flagged row through `select_entire_pane`; pass through all prior visible content and line endings without normalization.
Why this approach: It follows the PRD's protocol-boundary and exact-preservation requirements and isolates CPY_ALL from viewport normalization and pytest-specific selection.
Evidence / authorization: PRD `_docs/PRD/2026-09-23-m-w-select-all-copy.md`; source finding PL-0002; red/green focused evidence PL-0005–PL-0006.
Constraints that must survive: Confirm the exact flagged capture on target Termux; fail closed if the boundary is missing/malformed or the pre-prompt selection is empty.
Open alternatives/questions: The parser/executor tests pass locally, but full-history capture and clipboard output still require live target-runtime proof.

### D-003 — Keep deferred copy scopes separate [ACTIVE]
Problem/requirement: The CPY_ALL refactor must not silently absorb separate or explicitly excluded behaviors.
Chosen approach: Keep Patch Failed-specific subset selection deferred as independent scope; keep `copy-mode-vi` and the native `load-buffer -w` clipboard path out of current acceptance.
Why this approach: The recorded scope decision explicitly excludes vi-mode; the M-w PRD separately excludes Patch Failed extraction; `termux-clipboard-set` is the recorded proven endpoint. Native `load-buffer -w` is not a known failure, but depends on tmux terminal-clipboard/OSC 52 configuration and terminal support and has not been tested on the target.
Evidence / authorization: PL-0001; M-w PRD; legacy log sections 9, 24, and 29; PL-0006; [tmux clipboard guide](https://github.com/tmux/tmux/wiki/Clipboard).
Constraints that must survive: Do not treat these deferred items as CPY_ALL blockers or claim they were tested. Keep `termux-clipboard-set` until the alternate route is independently proven and explicitly brought into scope.
Open alternatives/questions: Any future Patch Failed work needs its own behavior contract and tests.

### D-004 — Keep the feature partial until PRD gates pass [ACTIVE]
Problem/requirement: The user explicitly requested that the recently finished CPY_ALL refactor be marked partial and that remaining work be made clear.
Chosen approach: Keep lifecycle status ACTIVE and label delivery PARTIAL until G2/G3 acceptance evidence is recorded.
Why this approach: Core executor test success does not prove final-prompt exclusion or exact content preservation, and the inspected code contradicts the preservation requirement.
Evidence / authorization: User instruction on 2026-10-23; PL-0002.
Constraints that must survive: Do not create `closeout.md` or change the feature to CLOSED while the PRD acceptance criteria remain unmet.
Open alternatives/questions: None; the next action is to establish the contract tests.

## Complete remaining-work inventory

1. **Capture/boundary proof — open:** On the target, inspect `capture-pane -pF -S -` and confirm that the final shell prompt row has the expected P flag in full-history mode.
2. **Contract tests — written / focused-pass:** `_test/test_copy_entire_pane.py` covers multiple prompt boundaries (using the last), prompt-like output without P, post-prompt content, blank rows, trailing spaces, earlier prompts, line endings, malformed/missing boundaries, empty selection, and untouched clipboard on failure. The isolated focused run passed 23 tests (PL-0006); the project runner has not run against this change yet.
3. **Executor integration — implemented / runtime-open:** `copy_entire_pane` now requests flagged full history, preserves prior rows without normalizing, and leaves both buffer and system clipboard unchanged for invalid/empty ranges. Viewport normalization and subset behavior remain separate.
4. **Target-runtime proof — open:** Exercise the actual CPY_ALL binding in root and Emacs-style `copy-mode` with sentinel rows around the final prompt and whitespace-sensitive fixtures. Verify the clipboard omits the final prompt and later content while preserving all earlier content exactly.
5. **Regression/coverage — open:** Run the tests through `./_test/run`, the complete suite, `test-runner coverage`, and `coverage report -m copy_executor.py copy_selector.py tmux.py`. Review actual output; previous 100% coverage does not substitute for a fresh result.
6. **Docs/continuity — partially updated:** The implementation-research record now has a 2026-10-23 current-state update. Run `bash _docs/_continuity/check.sh copy-refactor` in the project checkout and record its real output.

Deferred, not part of the active CPY_ALL gate: Patch Failed-specific subset selection. Explicitly out of current acceptance: `copy-mode-vi` and native tmux `load-buffer -w` clipboard delivery.

## Next action

**Next action:** After syncing the updated main branch, run `./_test/run test_copy_entire_pane.py && ./_test/run test_copy_executor.py && ./_test/run test_pytest_clipboard.py && ./_test/run`, then run `test-runner coverage && coverage report -m copy_executor.py copy_selector.py tmux.py`; finally exercise the CPY_ALL binding from root and Emacs-style `copy-mode` with output/prompt sentinels and verify the Android clipboard preserves every pre-prompt character while excluding the final prompt and everything after it.
