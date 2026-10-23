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

**Progress through:** PL-0003

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
**Exit condition:** A tested whole-pane selector uses a proven prompt-boundary representation, cuts off at the final prompt, retains exactly the preceding content, and leaves the clipboard unchanged when no valid non-empty range exists.
**Evidence:** PL-0002 records the inspected source mismatch; no passing acceptance evidence yet.
**Remaining:** Prove the flagged-capture representation for whole-pane capture; add positive/negative selector and executor tests; remove whole-pane normalization that violates the PRD without regressing viewport/subset behavior; observe the contract on-device.

### G3 — Regression, runtime acceptance, and documentation convergence
**Status:** NOT STARTED
**Requires:** G2 (must be DONE with supporting progress-log evidence)
**Exit condition:** Focused tests, the complete suite, target-module coverage report, and CPY_ALL runtime checks pass; the M-w research record and active guides match the proven behavior; all continuity references and markers are synchronized.
**Evidence:** none yet for the remaining CPY_ALL contract.
**Remaining:** Run focused and full regressions, inspect detailed coverage, exercise CPY_ALL in root and Emacs-style copy mode with prompt/whitespace fixtures, update the M-w research record, then refresh this roadmap and handoff. Record only results actually observed.

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
Chosen approach: Use a deterministic protocol/capture boundary, not visible prompt-text matching; retain the pre-boundary content without trimming or normalization.
Why this approach: The PRD states the contract explicitly; inspected source currently normalizes content and has no final-prompt cutoff.
Evidence / authorization: PRD `_docs/PRD/2026-09-23-m-w-select-all-copy.md`; source finding PL-0002.
Constraints that must survive: Prove flag/capture behavior before relying on it; fail closed if the boundary or non-empty selection is missing.
Open alternatives/questions: Verify that `capture-pane -pF -S -` exposes the final prompt reliably for the full history path before committing to the exact selector interface.

### D-003 — Keep deferred copy scopes separate [ACTIVE]
Problem/requirement: The CPY_ALL refactor must not silently absorb separate or explicitly excluded behaviors.
Chosen approach: Keep Patch Failed-specific subset selection deferred as independent scope; keep `copy-mode-vi` and the native `load-buffer -w` clipboard path out of current acceptance.
Why this approach: The recorded scope decision explicitly excludes vi-mode; the M-w PRD separately excludes Patch Failed extraction; the external clipboard path is already proven through `termux-clipboard-set`.
Evidence / authorization: PL-0001; M-w PRD; legacy log section 9 and sections 24 and 29.
Constraints that must survive: Do not treat these deferred items as CPY_ALL blockers or claim they were tested.
Open alternatives/questions: Any future Patch Failed work needs its own behavior contract and tests.

### D-004 — Keep the feature partial until PRD gates pass [ACTIVE]
Problem/requirement: The user explicitly requested that the recently finished CPY_ALL refactor be marked partial and that remaining work be made clear.
Chosen approach: Keep lifecycle status ACTIVE and label delivery PARTIAL until G2/G3 acceptance evidence is recorded.
Why this approach: Core executor test success does not prove final-prompt exclusion or exact content preservation, and the inspected code contradicts the preservation requirement.
Evidence / authorization: User instruction on 2026-10-23; PL-0002.
Constraints that must survive: Do not create `closeout.md` or change the feature to CLOSED while the PRD acceptance criteria remain unmet.
Open alternatives/questions: None; the next action is to establish the contract tests.

## Complete remaining-work inventory

1. **Capture/boundary proof:** Confirm that a full-history `capture-pane -F` capture reliably marks the final shell prompt on the target Termux/tmux setup. Record exactly what the P/O flags mean for this whole-pane use; do not infer that the subset parser automatically satisfies CPY_ALL.
2. **Selector contract:** Add tests in `test_copy_entire_pane.py` covering multiple prompt boundaries (use the last one), prompt-like ordinary output without a P flag, content after the final prompt, blank lines, trailing spaces, earlier prompts, preserved line endings, no/malformed prompt boundary, and empty pre-prompt selection.
3. **Executor integration:** Have `copy_entire_pane` request/use the verified boundary representation, preserve selected content byte-for-byte (as the PRD requires), and leave both tmux/Android clipboard content untouched on invalid/empty selection. Keep viewport normalization and subset behavior isolated unless their contracts require a separate change.
4. **Target-runtime proof:** Exercise the actual CPY_ALL binding in root and Emacs-style `copy-mode` with sentinel rows around the final prompt and whitespace-sensitive fixtures. Verify the clipboard omits the final prompt and later content while preserving all earlier content exactly.
5. **Regression/coverage:** Run `./_test/run test_copy_entire_pane.py`, then `./_test/run`, `test-runner coverage`, and `coverage report -m copy_executor.py copy_selector.py tmux.py`. Review real output; after implementation changes, previous 100% coverage does not substitute for a fresh result.
6. **Docs and continuity:** Reconcile `_docs/mods/copy_entire_pane/research/implementation-research.md` (currently still says implementation not started / last verified 2026-09-23) with current source and new findings; update operational docs if behavior changes; run `bash _docs/_continuity/check.sh copy-refactor` in Termux and record actual output.

Deferred, not part of the active CPY_ALL gate: Patch Failed-specific subset selection. Explicitly out of current acceptance: `copy-mode-vi` and native tmux `load-buffer -w` clipboard delivery.

## Next action

**Next action:** Add CPY_ALL-specific contract tests in `test_copy_entire_pane.py` for last-`P` prompt cutoff, multiple prompts, prompt-like `O` output, text after the final prompt, empty/missing boundaries, blank rows, trailing spaces, exact line endings, and unchanged clipboard on fail-closed cases; then run `./_test/run test_copy_entire_pane.py` and use results to drive the smallest selector/executor change.
