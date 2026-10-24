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


## PL-0003 — 2026-10-23 — Corrected prompt-identity test assertion

Status: NOT TESTED

Hypothesis/question: Does the reported failure indicate a filtering defect, or an incorrect assertion in the identity-preservation test?

Setup: User ran the focused tests and reported 29 passed, 1 failed at `test_alias_or_git_status_difference_keeps_distinct_empty_prompts`.

Action: Traced the failure to `selected.count(" | ") == 3`. Each context row contains two ` | ` separators, so three distinct context rows correctly produce a count of six. Replaced the delimiter count with an exact assertion over the three expected timestamped context rows, including their differing alias/status identities.

Observed:
- The reported value of six is consistent with three context rows, each containing two separators.
- The failed assertion did not establish that the filter collapsed distinct prompts; it counted separators rather than prompt rows.
- The corrected assertion directly checks that all three expected rows remain in order with their respective alias and Git status.

Not established:
- The corrected test has not yet been rerun.
- Full regression, coverage, continuity-checker output, and live Termux/tmux behavior remain unverified.

Next implication: Re-run the focused prompt-dedup test, then run fresh full-suite regression and coverage before target-runtime acceptance.

Corrects: PL-0002's test-execution status is updated with the failure evidence supplied by the user; earlier source-mapping evidence remains unchanged.


## PL-0004 — 2026-10-23 — Passing test and coverage results reported

Status: PASS

Hypothesis/question: Does the corrected prompt-identity assertion pass with the shared copy filter and contract tests?

Setup: User supplied a test summary and per-module coverage report after PL-0003 corrected the separator-count assertion. The command line was not included in the report.

Action: Recorded the user-provided test and coverage result against the implementation at the current main tip.

Observed:
- The test runner reported `71 passed in 0.64s`.
- A JSON coverage report was written.
- Aggregate coverage was 94% across 464 statements, with 18 missed statements, 186 branches, and 18 partially covered branches.
- `copy_executor.py` reported 97% coverage and `copy_selector.py` reported 96%.

Interpretation:
- The user-reported test invocation passed all 71 tests it executed. This resolves the observed failing-assertion checkpoint at test-run level.
- The output includes coverage metrics, but the exact command and selected test scope were not included. This entry therefore does not claim that the explicit `./_test/run force` mode was run.
- The report is evidence for the test invocation as shown, not for live Termux/tmux behavior.

Not established:
- Whether the invocation was the dedicated prompt-dedup test selection or the explicit forced full-regression mode.
- Continuity-checker output.
- Live placement of the tmux P flag in the active shell prompt, exact clipboard payloads, and runtime behavior of all three copy actions.
- Direct runtime verification of CPY_ALL's protocol-flagged cutoff interaction with deduplication.

Next implication: Run `./_test/run force` explicitly, run `bash _docs/_continuity/check.sh copy-prompt-dedup`, then verify the capture flags and exact clipboard output for all three copy actions in Termux/tmux.

Corrects: PL-0003's statement that the corrected assertion had not been rerun. The earlier failed run remains preserved as history.


## PL-0005 — 2026-10-23 — Forced full regression and coverage pass

Status: PASS

Hypothesis/question: Does the explicitly requested fresh full-suite regression pass after the prompt-identity assertion correction?

Setup: After PL-0004, the user was asked to run `./_test/run force` and supplied the resulting test summary and coverage report.

Action: Recorded the user-provided result for the forced regression invocation.

Observed:
- The test runner reported `71 passed in 0.61s`.
- A JSON coverage report was written.
- Aggregate coverage was 94% across 464 statements, with 18 missed statements, 186 branches, and 18 partially covered branches.
- `copy_executor.py` reported 97% coverage and `copy_selector.py` reported 96%.

Interpretation:
- The forced full-suite regression passed all 71 tests reported by the runner.
- The accompanying coverage report totals 94% statement coverage; the earlier PL-0004 report showed the same totals with a slightly different elapsed time.
- This test evidence does not establish live Termux/tmux capture flags, actual clipboard contents, or prompt-renderer behavior.

Not established:
- Continuity-checker output.
- Actual placement of the tmux P flag in the active shell prompt.
- Exact clipboard output of all three copy actions in the target runtime.
- Direct verification of CPY_ALL cutoff behavior at empty or malformed boundaries, and dedicated boundary/empty-selection test coverage.

Next implication: Run `bash _docs/_continuity/check.sh copy-prompt-dedup`, then complete target Termux/tmux acceptance checks for all three copy actions, including CPY_ALL's cutoff and edge boundaries.

Corrects: PL-0004's open question about whether the reported 71-test result came from the explicit forced regression invocation. The PL-0004 result remains valid as an earlier run.
