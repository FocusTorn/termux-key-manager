# Progress Log: copy-prompt-dedup (append-only evidence)

Newest last. This log preserves material project knowledge, not an activity diary: append only when an event materially changes understanding, a decision/requirement, task or verification status, a genuine blocker, dependencies/next action, or information needed to resume. Skip routine output, unrelated warnings, redundant checks, and uninformative attempts. Corrections are new entries.

## PL-0001 — 2026-10-23 — Feature created; duplicate means matching prompt identity

Status: NOT TESTED

Hypothesis/question: Can all copy actions remove redundant empty prompt rows without deleting a distinct final prompt or altering copied content?

Setup: TKM repository `FocusTorn/termux-key-manager`, main at baseline `279a147d5af497c859fae985c2d448d028c9df1d`. Existing shared copy executor is documented in `features/copy-refactor/`. User-provided terminal capture is the requirement source.

Action: Inspected current continuity index, copy-refactor roadmap/handoff, continuity guidance, and current main tree. No production source or tests changed in this feature initialization.

Observed:
- User explicitly requires the filter to apply to all copy actions.
- Example shows consecutive empty prompt rows that repeat the same prompt identity and should collapse to one.
- A later empty prompt is not necessarily a duplicate: the sample's preceding prompt shows project alias `tkm` and Git status `✔`, while the final prompt shows alias `spl` and status `Ø1`. Those differences identify a distinct prompt, so it must remain.
- The existing CPY_ALL selector has a separate contract to cut off at the final protocol-flagged prompt. Its cutoff must not be redefined by the deduplication work.

Interpretation: "Duplicate" is semantic, not just "an empty prompt row." Filter consecutive empty prompt rows only when the prompt identity matches. Prompt identity includes available visible context, especially project/alias and Git status; never remove a distinct prompt merely because its input is empty.

Not established:
- The exact structured representation available to each copy action and whether prompt identity can be compared reliably before formatting.
- Which copy actions receive already-rendered prompt rows versus raw captured rows.
- Implementation behavior, regression coverage, and live Termux/tmux output.

Next implication: Inspect every shared-executor caller and the capture/rendering contract, then write pure selector tests for matching and differing prompt identities before implementing a shared filter.

Corrects: none


## PL-0002 — 2026-10-23 — Shared prompt filter and contract tests written

Status: NOT TESTED

Hypothesis/question: Can the shared copy path identify repeated empty prompts from captured prompt context while preserving different aliases/statuses and each action's range semantics?

Setup: Repository `FocusTorn/termux-key-manager`; `main` at inspected baseline `193060412089c344397c9b92d4b0acc5c38b37e5`. Review intake found no pending snapshot: `for-review` had no `.review-id` and was behind `main`.

Action: Inspected `copy_executor.py`, `copy_selector.py`, `tmux.py`, `macros.py`, copy tests, testing/architecture/tmux docs, the CPY_ALL PRD, and `copy-refactor` continuity records. Mapped the three actions to the shared executor. Wrote a shared prompt filter, routed every action through it after selection, requested row flags for viewport capture, added contract tests, and updated docs.

Observed:
- All copy actions converge on `copy_executor.py`; no `cpy_*` helper path is needed.
- Whole-pane and subset capture use `capture-pane -pF -S -`. Viewport previously omitted `-F`, so it could not provide the same prompt identity markers; it now requests `-pFJ`.
- The filter recognizes the supplied format: a P-flagged `HHMM.SS | project/alias branch | Git status` row followed by an empty `❯` row. It ignores changing display time and compares remaining visible identity fields. Repeated matching empty prompt segments collapse; differing alias/status, command-bearing prompts, prompt-like unflagged output, and unknown layouts are retained.
- CPY_ALL selects its final P-flagged cutoff before deduplication; subset likewise selects its range before filtering. Existing per-action formatting rules remain.
- Added tests for timestamp-only changes, project/alias and Git-status differences, command-bearing prompts, unknown layouts, CRLF/trailing whitespace, and all three executor actions.
- The TKM repository does not define the user's shell prompt renderer, so live P-flag placement remains to be confirmed in target runtime.

Not established:
- The new or updated tests have not been executed.
- Live Termux/tmux capture flags and clipboard behavior have not been observed.
- Full-suite regression, coverage, and continuity-checker results remain NOT TESTED.

Next implication: Run focused contract tests and fresh full-suite regression, then verify actual prompt-row flags and all three copy actions in Termux before acceptance.

Corrects: PL-0001's open source-mapping task is advanced by this entry; no earlier evidence is replaced.
