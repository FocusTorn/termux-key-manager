# Handoff: Shared Copy Duplicate-Empty-Prompt Filtering

**Feature:** copy-prompt-dedup
**Snapshot:** 2026-10-23 UTC
**Valid as of:** `279a147d5af497c859fae985c2d448d028c9df1d` (branch `main`; repo `FocusTorn/termux-key-manager`)
**Objective:** Remove only redundant matching empty prompts across all copy actions; preserve distinct prompts and other content.
**Roadmap reviewed through:** PL-0001

## State

- Gate summary: G1 NOT STARTED; G2 NOT STARTED; G3 NOT STARTED.
- Demonstrated: the user requirement and sample distinction are recorded in PL-0001.
- Not demonstrated: source-level prompt identity availability, filter implementation, tests, project-runner/full-suite results, coverage, and target runtime behavior.
- Key decision: an empty prompt is not automatically a duplicate. The shown `tkm` prompt with Git status `✔` differs from the later `spl` prompt with status `Ø1`; preserve the latter. See D-001.
- Scope: all copy actions, through one shared path; no legacy `cpy_*` fallback. Keep CPY_ALL's protocol-based final prompt cutoff independent.
- Remaining work: see the complete inventory in `roadmap.md`; the next task is source/caller/capture-path mapping.

## Resume

**Next action:** Inspect `copy_executor.py`, `copy_selector.py`, `tmux.py`, every copy-action caller, prompt configuration/rendering, and related tests; document the capture-to-clipboard path and available prompt identity fields before writing the filter implementation.
**Read first:** `_docs/_continuity/features/copy-prompt-dedup/roadmap.md`, `PL-0001`, and `_docs/_continuity/README.md`.
**Success criteria for next gate:** Every copy action and the reliable prompt identity fields are mapped, including how project/alias and Git status differences are represented.
