# Native Tmux Copy Refactor — Handoff

**Snapshot date:** 2026-10-23  
**Repository:** FocusTorn/termux-key-manager  
**Branch:** main  
**Valid as of:** 9134ebdb9dbced13e390cf02892a00c17509643f  
**Status:** The accepted copy-refactor verification gate is complete. The most
recent full test run passed 57 tests; total suite coverage was 95%. The
corrected detailed report then confirmed 100% statement and branch coverage in
`copy_executor.py`, `copy_selector.py`, and `tmux.py`. The final local branch,
worktree, diff checks, and recent history audit were clean and synchronized.

## Mission

Replace TKM's legacy `cpy_*` shell-helper behavior with one shared native tmux
copy executor and three callers: `copy_entire_pane`, `copy_viewport`, and
`copy_subset`. There must be no legacy fallback or second implementation.

## Read these files first

1. [Progress workspace guide](README.md) — roles and update order for the
   handoff, roadmap, and runtime log.
2. [Copy roadmap](copy-roadmap.md) — gates and remaining scope boundaries.
3. [Copy runtime progress log](copy-runtime-log.md) — observed runtime and
   test evidence, including the final coverage audit in §29.
4. [R1.1 tmux internals](../research/r1_1-tmux-internals.md) and
   [R1.2 TKM implications](../research/r1_2-tkm-implications.md) — source
   analysis and architecture constraints.

## Current verified state

- `copy_executor.py` is the shared executor for `copy_entire_pane`,
  `copy_viewport`, and `copy_subset`. It captures through tmux, loads
  successful text into the tmux paste buffer, writes it with
  `termux-clipboard-set`, and cancels copy mode after actions initiated there.
- The production macro runtime matrix passed for all six action/context pairs:

  | Action | Root | Emacs-style `copy-mode` |
  |---|---|---|
  | `copy_entire_pane` / CPY_ALL | PASS | PASS |
  | `copy_subset` / CPY_TEST | PASS | PASS |
  | `copy_viewport` / CPY_ALL's COPY popup | PASS | PASS |

  Fresh clipboard sentinels and subset/viewport boundaries were checked.
  The copy-mode actions returned to the shell. Full evidence is in Runtime Log
  §24.
- The latest full `test-runner coverage` run passed **57 tests in 0.92s**.
  Its whole-suite report showed 95% overall coverage and 100% statement and
  branch coverage for each of the three target modules (Runtime Log §28).
- The corrected focused report independently confirmed:

  | Module | Statements | Missed | Branches | Partial | Coverage |
  |---|---:|---:|---:|---:|---:|
  | `copy_executor.py` | 52 | 0 | 16 | 0 | 100% |
  | `copy_selector.py` | 35 | 0 | 16 | 0 | 100% |
  | `tmux.py` | 74 | 0 | 28 | 0 | 100% |
  | **Total** | **161** | **0** | **60** | **0** | **100%** |

  See Runtime Log §29.
- The final local audit showed `main...origin/main` with no changed paths,
  both `git diff --check` commands passed, and the recent commit sequence
  matched the verified remote history (Runtime Log §29).
- Review intake was checked in this session. `for-review` had no `.review-id`
  and zero commits ahead of `main`, so no snapshot was pending.

## Scope boundaries kept explicit

- `Patch Failed`-specific subset selection remains deferred. The production
  subset runtime check used a controlled pytest progress marker, not a real
  `Patch Failed` output range. Any future work on that behavior needs a
  separately scoped contract and tests.
- `copy-mode-vi` is intentionally out of scope. Do not run another vi-mode
  trial or imply behavior there was verified.
- tmux's native `load-buffer -w` terminal clipboard path remains untested.
  Retain the proven `termux-clipboard-set` endpoint unless scope changes.
- Historical `cpy_*` references in append-only logs/research and intentional
  negative regression assertions remain by design; the inspected production
  path and reconciled operational guides contain no active legacy copy
  definitions or invocations (Runtime Log §25).

## Fixed workflow constraints

- Record observed evidence in the runtime log first, reconcile the roadmap
  second, and refresh this handoff last.
- Preserve failures, inconclusive trials, and setup corrections instead of
  rewriting the sequence to look clean.
- No future scope change without behavior contracts and relevant tests.
- Continue using the repository's connected GitHub workflow for remote
  commits; check the current branch tip and affected blob SHAs before mutation.

**Next action:** None for the accepted copy-refactor scope. Any future
work on `Patch Failed`-specific subset selection should be scoped and tested
separately. Keep the native tmux `load-buffer -w` clipboard path and
`copy-mode-vi` proof explicitly out of scope unless authorized scope changes.
