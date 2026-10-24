# Handoff: Shared Copy Duplicate-Empty-Prompt Filtering

**Feature:** copy-prompt-dedup
**Snapshot:** 2026-10-23 UTC
**Valid as of:** `5e8484bcf7596d7607ca9091129a88fa4d82ca12` (PL-0005 checkpoint on `main`, before this handoff refresh; repo `FocusTorn/termux-key-manager`)
**Objective:** Remove only redundant matching empty prompts across all copy actions; preserve distinct prompts and other content.
**Roadmap reviewed through:** PL-0005

## State

- Gate summary: G1 DONE (PL-0002); G2 DONE (PL-0004, core contract suite passing); G3 IN PROGRESS.
- Source mapping: all three copy actions converge on `copy_executor.py`; `copy_selector.py` applies the shared filter after each action's selection.
- Filter strategy: recognize a P-flagged `HHMM.SS | project/alias branch | Git status` context row followed by an empty `❯` row. Ignore the volatile timestamp and compare all remaining identity fields. Preserve command-bearing prompts and unfamiliar layouts.
- CPY_ALL boundary: source flow selects the final P-flagged cutoff before deduplication. Direct cutoff interaction and empty/malformed boundary behavior still need explicit coverage/runtime verification.
- Viewport: capture requests row flags via `-pFJ` so its content can share the filter; existing viewport whitespace normalization remains.
- Contract coverage in `_test/test_copy_prompt_dedup.py` includes timestamp-only duplicates, differing alias/status identities, command-bearing prompts, unknown or unflagged prompt-like rows, CRLF/trailing whitespace, and all three action paths.
- Implementation and copy documentation landed in `6c91e48d790ef81a4903fa464c7798b37905b00f`; the corrected identity assertion and PL-0003 are in `2f5e2ac35f54cf820bd2aacbb8d7b10e4e13d4bb`.
- PL-0005 records the user-provided explicit `./_test/run force` result: `71 passed in 0.61s`, 94% aggregate statement coverage (464 statements, 18 missed; 186 branches, 18 partially covered). `copy_executor.py` reported 97% coverage and `copy_selector.py` 96%.
- Remaining: continuity-checker output, direct boundary/empty-selection and CPY_ALL cutoff coverage, live P-flag placement, and exact clipboard behavior in Termux/tmux.
- Runtime constraint: TKM does not own the shell prompt renderer. Confirm the P flag is placed on the context row used by this parser before acceptance. Accepted contexts are root and Emacs-style `copy-mode`; `copy-mode-vi` is out of scope.

## Resume

**Next action:** Run `bash _docs/_continuity/check.sh copy-prompt-dedup`; then verify actual P-flag placement and exact clipboard output for all three copy actions in Termux/tmux, including CPY_ALL's protocol cutoff and empty/malformed boundary behavior. Add or confirm direct boundary/empty-selection contract coverage before closeout.
**Read first:** `_docs/_continuity/features/copy-prompt-dedup/roadmap.md`, the PL-0001 through PL-0005 entries in `progress-log.md`, and `_docs/_continuity/README.md`.
**Success criteria for next gate:** Continuity check passes; boundary/cutoff behavior is directly covered; actual Termux/tmux capture demonstrates expected prompt flags; all three actions remove only duplicate empty prompts with matching identity while preserving distinct alias/status prompts and unrelated text.
