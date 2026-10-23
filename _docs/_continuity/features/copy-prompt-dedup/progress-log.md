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
