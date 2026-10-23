# Native Tmux Copy Refactor — Handoff

**Snapshot date:** 2026-10-22  
**Repository:** FocusTorn/termux-key-manager  
**Branch:** main  
**Implementation:** The shared executor and selector are committed. The full coverage target reported 49 passed and 90% total statement coverage. All three production copy actions passed runtime checks from root and emacs-style `copy-mode`; the Gate 5 runtime acceptance criteria are met. Line-specific coverage review and final repository audit remain.

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
- The user-run `test-runner coverage` command reported **49 passed in 0.47s**
  and **90% total statement coverage**. Aggregate module coverage was
  `copy_executor.py` 75%, `copy_selector.py` 88%, and `tmux.py` 94%
  (Runtime Log §23).
- The focused selector and executor runs were reported green. Live OSC 133
  integration was also confirmed: the user's capture showed `PX` on the
  prompt top-rule row and `O TKM_OSC133_OUTPUT_PROBE` on the output row
  (Runtime Log §15).

## Remaining work and constraints

- Gate 6: inspect the line-specific missing-coverage report from the last
  coverage run if available; otherwise rerun the coverage target and capture
  the detailed missing-line output or report path. The durable log currently
  contains aggregate percentages only.
- The source/helper-template audit found no active `cpy_*` function
  definitions or invocation in the inspected production path. The nine stale
  operational guides were reconciled; old names remain in historical research
  and progress records plus deliberate negative regression assertions
  (Runtime Log §25).
- Source/test inspection suggests edge cases worth checking include missing
  `pane_id`, empty non-subset capture output, tmux/clipboard subprocess
  failures, and CRLF or unterminated final rows in selector parsing. These are
  candidates, not confirmed exact coverage misses.
- `Patch Failed` subset selection remains deferred. The production subset
  runtime check used a controlled progress marker, not a real `Patch Failed`
  output range.
- `copy-mode-vi` is explicitly out of scope. Do not run another vi-mode proof
  or imply behavior there has been verified.
- tmux's native `load-buffer -w` terminal clipboard path remains untested;
  retain the proven `termux-clipboard-set` endpoint.
- Do not mark the line-specific coverage audit complete from aggregate
  percentages alone.


## Fixed workflow constraints

- Record observed evidence in the runtime log first, reconcile the roadmap
  second, and refresh this handoff last.
- Preserve failures, inconclusive trials, and setup corrections instead of
  rewriting the sequence to look clean.
- No future scope change without behavior contracts and relevant tests.
- Continue using the repository's connected GitHub workflow for remote
  commits; check the current branch tip and affected blob SHAs before mutation.

**Next action:** Retrieve the line-specific missing-coverage report from the
last `test-runner coverage` run, or rerun coverage and preserve its detailed
report. Then verify the final diff, branch state, and commit history.
