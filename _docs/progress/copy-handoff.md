# Native Tmux Copy Refactor — Handoff

**Snapshot date:** 2026-10-23  
**Repository:** FocusTorn/termux-key-manager  
**Branch:** main  
**Valid as of:** a26884e0db8bd9f0d877dd686bc51fc683a35bae  
**Implementation:** The shared executor and selector are committed. The latest full coverage target reported 57 passed in 0.92s and 95% total coverage. `copy_executor.py`, `copy_selector.py`, and `tmux.py` each have 100% statement and branch coverage in the full-suite summary. All three production copy actions passed runtime checks from root and emacs-style `copy-mode`; the Gate 5 runtime acceptance criteria are met. Only the corrected detailed report and final local repository audit remain.

## Mission

Replace TKM's legacy `cpy_*` shell-helper behavior with one shared native tmux
copy executor and three callers: `copy_entire_pane`, `copy_viewport`, and
`copy_subset`. There must be no legacy fallback or second implementation.

## Read these files first

1. [Progress workspace guide](README.md) — roles and update order for the
   handoff, roadmap, and runtime log.
2. [Copy roadmap](copy-roadmap.md) — current gates and remaining work.
3. [Copy runtime progress log](copy-runtime-log.md) — observed runtime evidence
   and important test-harness corrections.
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
  The copy-mode tests returned to the shell; CPY_ALL's copy-mode run explicitly
  reported automatic mode exit. Full evidence is in Runtime Log §24.
- The latest user-run `test-runner coverage` command reported **57 passed
  in 0.92s** and **95% total coverage**. The full-suite report showed
  `copy_executor.py`, `copy_selector.py`, and `tmux.py` at 100% statement
  and branch coverage (Runtime Log §28).
- The detailed follow-up report also showed 100% statement and branch coverage
  for `copy_executor.py` and `copy_selector.py`. The command misspelled
  `tmux.py` as `tmux.p`, so coverage.py emitted a path warning and omitted
  only that module from the detailed report; the full-suite summary still
  included `tmux.py` at 100%.
- The focused selector and executor runs were reported green. Live OSC 133
  integration was also confirmed: the user's capture showed `PX` on the
  prompt top-rule row and `O TKM_OSC133_OUTPUT_PROBE` on the output row
  (Runtime Log §15).

## Remaining work and constraints

- The targeted coverage regression tests from Runtime Log §27 have now run
  successfully. The three production modules each report 100% statement and
  branch coverage in the full-suite summary (Runtime Log §28).
- The detailed report command contained the typo `tmux.p`. Run the corrected
  detailed report, then finish the local status/ref/history audit before
  closing Gate 6. The test suite does not need to be rerun for that report.
- The source/helper-template audit found no active `cpy_*` function
  definitions or invocations in the inspected production path. The nine stale
  operational guides were reconciled; old names remain in historical research
  and progress records plus deliberate negative regression assertions
  (Runtime Log §25).
- `Patch Failed` subset selection remains deferred. The production subset
  runtime check used a controlled progress marker, not a real `Patch Failed`
  output range.
- `copy-mode-vi` is explicitly out of scope. Do not run another vi-mode proof
  or imply behavior there has been verified.
- tmux's native `load-buffer -w` terminal clipboard path remains untested;
  retain the proven `termux-clipboard-set` endpoint.


## Fixed workflow constraints

- Record observed evidence in the runtime log first, reconcile the roadmap
  second, and refresh this handoff last.
- Preserve failures, inconclusive trials, and setup corrections instead of
  rewriting the sequence to look clean.
- No future scope change without behavior contracts and relevant tests.
- Continue using the repository's connected GitHub workflow for remote
  commits; check the current branch tip and affected blob SHAs before mutation.

**Next action:** Run `g l && coverage report -m copy_executor.py copy_selector.py tmux.py && git status --short --branch && git branch -vv && git diff --check && git diff --cached --check && git log -5 --oneline --decorate`
from the TKM repository root. Confirm the corrected report includes all three
modules, the local branch is synchronized and clean, both diff checks pass,
and the recent history matches the verified remote sequence.
