# Roadmap: Shared Copy Duplicate-Empty-Prompt Filtering

**Feature:** copy-prompt-dedup
**Parent:** none
**Depends on:** copy-refactor:G1

## Objective

Update the main shared copy orchestrator so every copy action removes redundant consecutive empty prompts when they represent the same prompt identity. Preserve distinct empty prompts, including a final prompt whose project alias or Git status differs from the prompt above it. Preserve all other copied content and keep CPY_ALL's protocol-based final-prompt cutoff independent.

## End state and acceptance criteria

- [ ] Map every copy action and identify its capture, selection, and formatting stages; establish where prompt identity is available.
- [ ] Define prompt identity from reliable available fields. At minimum, differing project/alias or Git status means prompts are distinct. Do not infer duplicates from blank input alone.
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

**Progress through:** PL-0001

`Progress through` is the newest actual log entry reviewed and reconciled here. Advance only after a material log entry is appended and reconciled.

## Gates

### G1 — Map copy orchestration and prompt identity
**Status:** NOT STARTED
**Requires:** copy-refactor:G1
**Exit condition:** All copy actions/callers and relevant capture/rendering stages are mapped; reliable prompt identity fields and their availability are documented.
**Evidence:** PL-0001 records the initial examples and open inspection questions.
**Remaining:** Inspect the orchestrator, selector, executor, every caller, prompt theme/rendering, and current tests.

### G2 — Shared filter and contract tests
**Status:** NOT STARTED
**Requires:** G1
**Exit condition:** A shared filter and tests prove matching duplicate empty prompts collapse to one, distinct prompt identities survive, and all other text is preserved.
**Evidence:** none yet.
**Remaining:** Establish contracts first; implement only after the available representation supports safe identity comparison.

### G3 — Integration, regression, and runtime acceptance
**Status:** NOT STARTED
**Requires:** G2
**Exit condition:** Every copy action routes through the shared filter; focused and full regression tests, relevant coverage, and target Termux/tmux runtime checks pass; continuity and user documentation agree.
**Evidence:** none yet.
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
Chosen approach: Integrate one filter into the main copy orchestrator/shared path after mapping the action flow and before clipboard delivery, without duplicating implementations.
Why this approach: A common policy in the common path avoids inconsistent action-specific behavior.
Evidence / authorization: User clarification on 2026-10-23; PL-0001.
Constraints that must survive: Apply to all copy actions, keep each action's existing selection/cutoff contract, and do not revive the retired `cpy_*` helper family.
Open alternatives/questions: Exact insertion point depends on the inspection in G1.

## Complete remaining-work inventory

1. Inspect the main copy orchestrator and all copy action entry points.
2. Establish how empty prompt rows and prompt identity fields are represented at each relevant stage.
3. Write behavior-first unit tests for matching duplicates, above/below positions, differing alias/project, differing Git status, and content preservation.
4. Implement one shared identity-aware filter and route every action through it.
5. Verify interaction with CPY_ALL's P-flag final-prompt cutoff and empty/malformed boundary behavior.
6. Run focused project-runner tests, full regression suite, relevant coverage, and target Termux/tmux checks for every action.
7. Update architecture/development docs and record results; run `bash _docs/_continuity/check.sh copy-prompt-dedup`.

## Next action

**Next action:** Inspect `copy_executor.py`, `copy_selector.py`, `tmux.py`, every copy-action caller, prompt configuration/rendering, and related tests; document the capture-to-clipboard path and available prompt identity fields before writing the filter implementation.
