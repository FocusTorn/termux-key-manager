# Handoff: CPY_ALL / Native Tmux Copy Refactor (PARTIAL)

**Feature:** copy-refactor
**Snapshot:** 2026-10-23 UTC
**Valid as of:** `7711f3b2e8d1cbfcc6a37803426e0e27ae01a200` (branch `main`; repo `FocusTorn/termux-key-manager`)
**Transfer:** Refreshed resume snapshot after migration verification; no feature closeout has occurred.
**Objective:** Finish CPY_ALL/M-w final-prompt exclusion and exact content preservation.
**Roadmap reviewed through:** PL-0004

## State

- Gate summary: G1 DONE (PL-0001); G2 IN PROGRESS; G3 NOT STARTED.
- Demonstrated: The legacy log records the shared-executor refactor, production action/context matrix, 57 passing tests, and 100% statement/branch coverage in the three target modules (PL-0001; legacy log sections 24 and 28–29). These are inherited user-run results, not tests executed during this migration.
- Migration verified: canonical continuity paths exist, the legacy flat workspace is retired, all inherited numbered sections remain in order, and feature markers are synchronized (PL-0004). The shell checker is NOT TESTED.
- Not demonstrated: CPY_ALL excludes the final shell prompt and all later content; retained content preserves trailing spaces, blank lines, and line endings exactly.
- Source/spec gap: `copy_executor.py` currently captures whole-pane content without a final-`P` cutoff and applies `_normalize_pane_text` (PL-0002). The M-w PRD forbids that normalization.
- Failures / blockers / open questions: No external blocker. Prove whether flagged full-history capture exposes a reliable final prompt; then write contract tests before production edits (PL-0002).
- Constraints and decisions to preserve: D-001 (shared executor/no `cpy_*` fallback); D-002 (M-w boundary and exact preservation); D-003 (Patch Failed separate; vi/native tmux clipboard out of scope); D-004 (remain PARTIAL until acceptance). Depends on: none.
- Remaining-work inventory: See the six ordered items in the roadmap: capture-boundary proof, selector tests, executor integration, live CPY_ALL checks, fresh regression/coverage results, and reconciliation of the stale M-w research record.

## Resume

**Next action:** Add CPY_ALL-specific contract tests in `test_copy_entire_pane.py` for last-`P` prompt cutoff, multiple prompts, prompt-like `O` output, text after the final prompt, empty/missing boundaries, blank rows, trailing spaces, exact line endings, and unchanged clipboard on fail-closed cases; then run `./_test/run test_copy_entire_pane.py` and use results to drive the smallest selector/executor change.
**Read first:** `_docs/PRD/2026-09-23-m-w-select-all-copy.md`, `_docs/_continuity/features/copy-refactor/roadmap.md`, `PL-0002`.
**Success criteria for next gate:** A focused test suite proves final-prompt cutoff, exact pre-boundary preservation, and fail-closed no-boundary/empty-range behavior before implementation is changed.
