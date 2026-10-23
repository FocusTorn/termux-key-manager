# Handoff: Shared Copy Duplicate-Empty-Prompt Filtering

**Feature:** copy-prompt-dedup
**Snapshot:** 2026-10-23 UTC
**Valid as of:** `d9966fafebe5f7712eda497dd4393812410f4ec9` (branch `main` before this correction; repo `FocusTorn/termux-key-manager`)
**Objective:** Remove only redundant matching empty prompts across all copy actions; preserve distinct prompts and other content.
**Roadmap reviewed through:** PL-0003

## State

- Gate summary: G1 DONE (PL-0002); G2 IN PROGRESS; G3 NOT STARTED.
- Source mapping: all three actions converge on `copy_executor.py`; `copy_selector.py` now applies the shared filter after each action's selection.
- Filter strategy: recognize a P-flagged `HHMM.SS | project/alias branch | Git status` context row followed by an empty `❯` row. Ignore the volatile timestamp and compare all remaining context fields. Preserve command-bearing prompts and unknown layouts.
- CPY_ALL boundary: select the final P-flagged cutoff before deduplication. The protocol cutoff is independent from text deduplication.
- Viewport: capture requests row flags via `-pFJ` so its content can share the same filter; the existing viewport whitespace normalization remains.
- New contract coverage: `_test/test_copy_prompt_dedup.py` tests timestamp-only changes, differing aliases/statuses, command-bearing prompts, unknown layouts, CRLF/trailing whitespace, and all three action paths.
- Code, tests, architecture/tmux/testing docs, and progress/roadmap records are committed at `6c91e48d790ef81a4903fa464c7798b37905b00f`.
- User-run focused test result: 29 passed, 1 failed. PL-0003 identifies the failure as a bad assertion that expected three separator occurrences although each of three context rows contains two. The assertion now compares the exact three context rows; this correction still needs a rerun.
- Full regression, coverage, continuity-checker output, live P-flag placement, and actual Termux clipboard output remain unverified.
- Source limitation: TKM does not own the shell prompt renderer. Target capture must confirm the P flag is placed on the context row used by this parser before the feature can be accepted.

## Resume

**Next action:** Re-run the focused prompt-dedup tests after PL-0003's assertion correction, then run `./_test/run force` for a fresh full-suite regression and `./_test/run coverage`; run `bash _docs/_continuity/check.sh copy-prompt-dedup`, then verify all three copy actions in target Termux/tmux with identical-context empty prompts, timestamp-only changes, alias/status changes, and command-bearing prompts.
**Read first:** `_docs/_continuity/features/copy-prompt-dedup/roadmap.md`, `PL-0001`, `PL-0002`, and `_docs/_continuity/README.md`.
**Success criteria for next gate:** Focused contract tests and a fresh full-suite regression pass; actual Termux/tmux capture demonstrates the expected prompt flags; all three actions remove only duplicate empty prompts with matching identity and preserve differing alias/status prompts and unrelated text.
