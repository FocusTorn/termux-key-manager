# Roadmap: Shared Copy Duplicate-Empty-Prompt Filtering

**Feature:** copy-prompt-dedup
**Parent:** none
**Depends on:** copy-refactor:G1

## Objective

Update the main shared copy orchestrator so every copy action removes redundant consecutive empty prompts when they represent the same prompt identity. Preserve distinct empty prompts, including a final prompt whose project alias or Git status differs from the prompt above it. Preserve all other copied content and keep CPY_ALL's protocol-based final-prompt cutoff independent.

## End state and acceptance criteria

- [x] Map every copy action and identify its capture, selection, and formatting stages; establish where prompt identity is available (PL-0002).
- [x] Define prompt identity for the supplied visible prompt layout. Ignore changing display time; compare project/alias, branch, and Git status. Retain unfamiliar layouts rather than guessing (PL-0002).
- [x] Add the shared deterministic filter for redundant adjacent empty prompt rows with matching identity (PL-0002).
- [x] Apply the filter to all three copy actions through the shared path; do not revive legacy `cpy_*` helpers (PL-0002; passing test output reported in PL-0004).
- [x] Preserve one representative of matching empty-prompt runs and preserve command-bearing prompts (PL-0002; passing test output reported in PL-0004).
- [x] Preserve distinct empty prompts when alias/project or Git status differs (PL-0002; passing test output reported in PL-0004).
- [x] Preserve non-duplicate text, ordering, trailing whitespace, and line endings according to the exercised contracts (PL-0002; passing test output reported in PL-0004).
- [x] Add core contract tests for timestamp-only differences, distinct aliases/statuses, command-bearing prompts, unrecognized or unflagged prompt-like rows, line endings/whitespace, and all three copy actions (PL-0002; test pass reported in PL-0004).
- [ ] Add or confirm direct boundary/empty-selection coverage and explicit CPY_ALL cutoff interaction coverage.
- [ ] Verify that CPY_ALL still uses its protocol-flagged final prompt boundary and that deduplication does not remove or move the cutoff.
- [ ] Run the focused tests through the project runner, the full regression suite, relevant coverage, and target Termux/tmux runtime checks for every copy action.
- [ ] Synchronize research/development documentation and continuity records with observed behavior; run the continuity checker.

## Synchronization

**Progress through:** PL-0004

`Progress through` is the newest actual log entry reviewed and reconciled here. Advance only after a material log entry is appended and reconciled.

## Gates

### G1 — Map copy orchestration and prompt identity
**Status:** DONE (PL-0002)
**Requires:** copy-refactor:G1
**Exit condition:** All copy actions/callers and relevant capture/rendering stages are mapped; available prompt identity fields and their limits are documented.
**Evidence:** PL-0002 maps all three callers and the capture-to-clipboard path, and documents the visible identity fields plus the lack of a source-controlled prompt renderer.
**Remaining:** No source-mapping work remains; confirm live P-flag placement as part of G3 runtime acceptance.

### G2 — Shared filter and contract tests
**Status:** DONE (PL-0004)
**Requires:** G1 (DONE, PL-0002)
**Exit condition:** The shared filter and contract tests pass, proving that matching duplicate empty prompts collapse to one, distinct identities survive, and all other text is preserved.
**Evidence:** PL-0002 records the shared implementation and contract tests; PL-0003 identifies the original failure as an incorrect separator-count assertion; PL-0004 records the user's subsequent report of 71 passing tests and 94% aggregate coverage.
**Remaining:** Finish or explicitly scope the boundary/empty-selection tests tracked in the acceptance checklist. The exact invocation was not included, so the forced full-regression mode remains tracked under G3.

### G3 — Integration, regression, and runtime acceptance
**Status:** IN PROGRESS
**Requires:** G2
**Exit condition:** Every copy action routes through the shared filter; focused and full regression tests, relevant coverage, and target Termux/tmux runtime checks pass; continuity and user documentation agree.
**Evidence:** PL-0002 records source-level selection-before-dedup handling; PL-0004 records a user-reported 71-pass run and 94% aggregate coverage. The exact test command was omitted.
**Remaining:** Run `./_test/run force` explicitly; run the continuity checker; verify actual P-flag placement, CPY_ALL cutoff interaction, and exact clipboard content for every copy action in target Termux/tmux.

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
3. **Test execution — passing result reported, invocation unspecified:** PL-0004 records 71 passed and 94% coverage. Run `./_test/run force` explicitly to establish a fresh full-suite regression result; retain the original failed run as historical evidence.
4. **Core contract validation — passing result reported:** Current tests cover timestamp-only duplicates, differing identities, command-bearing prompts, unknown/unflagged formats, whitespace/line endings, and all three action paths (PL-0002, PL-0004). Boundary/empty-selection coverage still needs confirmation.
5. **CPY_ALL boundary interaction — source-level handling inspected / runtime NOT TESTED:** Confirm the final P-flag cutoff remains selected before deduplication, including empty/malformed boundary fail-closed behavior.
6. **Regression and coverage — partial evidence:** PL-0004 reports 71 passed and 94% coverage, but the command is unknown. Run `./_test/run force` explicitly; coverage has been reported but is not independently tied to that invocation.
7. **Target runtime — open:** Exercise all three actions in accepted root and Emacs-style `copy-mode` contexts; verify exact clipboard content, preserving distinct alias/status prompts while removing only redundant matching empty prompts. `copy-mode-vi` remains out of scope.
8. **Continuity verification — open:** Run `bash _docs/_continuity/check.sh copy-prompt-dedup` in the project checkout and record its actual output.

## Next action

**Next action:** Run `./_test/run force` for an explicitly identified fresh full-suite regression, then run `bash _docs/_continuity/check.sh copy-prompt-dedup`; verify actual P-flag placement, CPY_ALL's protocol cutoff, and exact clipboard output for all three copy actions in Termux/tmux. Add or confirm boundary/empty-selection contract coverage before closeout.
