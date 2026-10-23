# Roadmap: Shared Copy Duplicate-Empty-Prompt Filtering

**Feature:** copy-prompt-dedup
**Parent:** none
**Depends on:** copy-refactor:G1

## Objective

Update the main shared copy orchestrator so every copy action removes redundant consecutive empty prompts when they represent the same prompt identity. Preserve distinct empty prompts, including a final prompt whose project alias or Git status differs from the prompt above it. Preserve all other copied content and keep CPY_ALL's protocol-based final-prompt cutoff independent.

## End state and acceptance criteria

- [x] Map every copy action and identify its capture, selection, and formatting stages; establish where prompt identity is available (PL-0002).
- [x] Define prompt identity for the supplied visible prompt layout. Ignore changing display time; compare project/alias, branch, and Git status. Retain unfamiliar layouts rather than guessing (PL-0002).
- [ ] Add a shared, deterministic filter that removes only redundant adjacent empty prompt rows with matching identity, including duplicates appearing above or below the retained row in the captured/copy range.
- [ ] Apply the filter to every copy action through the main copy orchestrator/shared path; do not add per-action parallel implementations or revive legacy `cpy_*` helpers.
- [ ] Preserve one representative of a run of matching empty prompts and preserve every non-empty prompt.
- [ ] Preserve distinct empty prompts. In particular, a final prompt with a different alias/project or Git status must not be stripped just because the preceding row is also an empty prompt.
- [ ] Preserve all non-duplicate text, ordering, blank output lines, trailing whitespace, and line endings according to each copy action's existing contract.
- [ ] Add contract tests for duplicates above and below; repeated runs of 2+; distinct aliases; distinct Git status; same alias with different Git status; non-empty prompt rows; prompt-like output; and boundaries/empty selections.
- [ ] Verify that CPY_ALL still uses its protocol-flagged final prompt boundary and that deduplication does not remove or move the cutoff.
- [ ] Run the focused tests through the project runner, the full regression suite, relevant coverage, and target Termux/tmux runtime checks for every copy action.
- [ ] Synchronize research/development documentation and continuity records with observed behavior; run the continuity checker.

## Synchronization

**Progress through:** PL-0003

`Progress through` is the newest actual log entry reviewed and reconciled here. Advance only after a material log entry is appended and reconciled.

## Gates

### G1 — Map copy orchestration and prompt identity
**Status:** DONE (PL-0002)
**Requires:** copy-refactor:G1
**Exit condition:** All copy actions/callers and relevant capture/rendering stages are mapped; available prompt identity fields and their limits are documented.
**Evidence:** PL-0002 maps all three callers and the capture-to-clipboard path, and documents the visible identity fields plus the lack of a source-controlled prompt renderer.
**Remaining:** No source-mapping work remains; confirm live P-flag placement as part of G3 runtime acceptance.

### G2 — Shared filter and contract tests
**Status:** IN PROGRESS
**Requires:** G1 (DONE, PL-0002)
**Exit condition:** The shared filter and contract tests pass, proving that matching duplicate empty prompts collapse to one, distinct identities survive, and all other text is preserved.
**Evidence:** PL-0002 records the filter and tests written. PL-0003 records the first focused run (29 passed, 1 failed) and corrects an assertion that counted two delimiters per context row rather than counting prompt rows.
**Remaining:** Re-run the corrected focused contract tests and address any further failures before considering this gate DONE.

### G3 — Integration, regression, and runtime acceptance
**Status:** NOT STARTED
**Requires:** G2
**Exit condition:** Every copy action routes through the shared filter; focused and full regression tests, relevant coverage, and target Termux/tmux runtime checks pass; continuity and user documentation agree.
**Evidence:** PL-0002 records source-level boundary handling; test execution and target-runtime acceptance remain open.
**Remaining:** Exercise every copy action, including CPY_ALL, in accepted runtime contexts; confirm the final distinct prompt remains and redundant matching empty prompts do not.

## Blocked

None. The feature is actionable; reliable prompt-identity availability is an investigation task, not yet an external blocker.

## Decisions

### D-001 — Duplicate means matching prompt identity, not merely an empty row [ACTIVE]
Problem/requirement: Repeated empty prompts pollute copied output, but the last prompt can be a distinct shell state and must not be stripped.
Chosen approach: Collapse only adjacent empty prompt rows with matching prompt identity, retaining one representative. Treat project/alias and Git status differences as identity differences whenever those fields are available.
Why this approach: The user's example explicitly contrasts repeated `utr` prompts with a later `spl` prompt and different Git status. The final prompt is distinct even though its command input is empty.
Evidence / authorization: User-provided examples and clarification on 2026-10-23; PL-0001.
Constraints that must survive: Never drop a prompt solely because it is empty; never collapse across a differing project/alias or Git status; preserve non-prompt output and exact text outside removed duplicates.
Open alternatives/questions: Determine the strongest reliable structured identity available from the prompt-generation/capture path; do not assume all prompt fields are present in all copy actions.

### D-002 — Filter all copy actions in the shared path [ACTIVE]
Problem/requirement: The behavior must be consistent across every copy action.
Chosen approach: Use one shared filter from action-specific selectors after each action's selection; add row flags to viewport capture so all three actions have prompt markers.
Why this approach: A common selector-layer policy avoids inconsistent action-specific implementations while preserving existing range rules.
Evidence / authorization: User clarification on 2026-10-23; PL-0001 and PL-0002.
Constraints that must survive: Apply to all copy actions, keep each action's existing selection/cutoff contract, and do not revive the retired `cpy_*` helper family.
Open alternatives/questions: Runtime capture still needs to confirm the P-flag placement in the active multi-line prompt.

### D-003 — Ignore volatile time; preserve unfamiliar prompt layouts [ACTIVE]
Problem/requirement: Display-time changes alone must not prevent duplicate prompts from collapsing, while unsupported row layouts must not be guessed into duplicates.
Chosen approach: For the supplied `HHMM.SS | project/alias branch | Git status` row format, compare all fields after the timestamp; require the following row to be exactly the empty `❯` input.
Why this approach: The timestamp changes independently of prompt identity. Project/alias, branch, and Git status distinguish the prompts shown in the user's example.
Evidence / authorization: User-provided example and PL-0002 source/test work.
Constraints that must survive: If the context row does not match the known format, or the prompt input is not empty, preserve it. Runtime confirmation of P-flag placement remains open.
Open alternatives/questions: If the active shell's prompt renderer changes layout, expand the parser only with a captured example and tests.

## Complete remaining-work inventory

1. **Source mapping — complete:** Map all three callers, shared executor, selectors, and clipboard path (PL-0002). The shell prompt renderer is external to this repository.
2. **Runtime identity confirmation — open:** Inspect actual `capture-pane -pF -S -` output on target Termux/tmux and confirm the P flag marks the context row used by the current two-line prompt.
3. **Focused contract tests — assertion corrected / rerun pending:** The reported failure was an incorrect separator-count expectation; re-run the focused tests to verify the correction (PL-0003).
4. **Implementation validation — open:** Confirm matching empty prompt groups collapse to one and differing project/alias or Git status, command-bearing prompts, and unknown formats remain unchanged.
5. **CPY_ALL boundary interaction — source/test written / NOT TESTED:** Confirm the final P-flag cutoff is selected before deduplication, including empty/malformed boundary fail-closed behavior.
6. **Regression and coverage — open:** Run `./_test/run force` for fresh full-suite execution and `./_test/run coverage` for fresh coverage results.
7. **Target runtime — open:** Exercise all three actions in accepted root and Emacs-style `copy-mode` contexts; verify exact clipboard content, preserving distinct alias/status prompts while removing only redundant matching empty prompts. `copy-mode-vi` remains out of scope.
8. **Continuity verification — open:** Run `bash _docs/_continuity/check.sh copy-prompt-dedup` in the project checkout and record its actual output.

## Next action

**Next action:** Re-run the focused prompt-dedup tests after PL-0003's assertion correction, then run `./_test/run force` for a fresh full-suite regression and `./_test/run coverage`; run `bash _docs/_continuity/check.sh copy-prompt-dedup`, then verify all three copy actions in target Termux/tmux with identical-context empty prompts, timestamp-only changes, alias/status changes, and command-bearing prompts.
