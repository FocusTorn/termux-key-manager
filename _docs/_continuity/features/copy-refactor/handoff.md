# Handoff: CPY_ALL / Native Tmux Copy Refactor (PARTIAL)

**Feature:** copy-refactor
**Snapshot:** 2026-10-23 UTC
**Valid as of:** \`aeea8353b979fb17830a27e9d5bad7073c6f9313\` (branch \`main\`; repo \`FocusTorn/termux-key-manager\`)
**Transfer:** Refreshed working snapshot; feature remains open.
**Objective:** Prove CPY_ALL/M-w final-prompt exclusion and exact content preservation on target Termux/tmux.
**Roadmap reviewed through:** PL-0007

## State

- Gate summary: G1 DONE (PL-0001); G2 IN PROGRESS; G3 NOT STARTED.
- Demonstrated from inherited user-run evidence: the shared executor, production action/context matrix, 57 passing tests, and 100% statement/branch coverage for the three target modules (PL-0001; legacy log sections 24 and 28–29).
- New source/test checkpoint: CPY_ALL now uses flagged full-history capture and cuts at the final P row. Pre-change contract tests produced expected RED failures; the focused local Python slice then passed 23 tests (PL-0005–PL-0006).
- Remote state verified: current \`main\` contains the source change, new test file, refreshed research record, and synchronized progress/roadmap files. All 29 inherited numbered log sections remain intact (PL-0007).
- Not demonstrated: live \`capture-pane -pF -S -\` output on the target; actual CPY_ALL Android clipboard result and exact preservation from root and Emacs-style \`copy-mode\`; full project test/coverage results after this source change.
- Source implementation: \`copy_selector.py\` adds \`select_entire_pane\`; \`copy_executor.py\` routes only \`copy_entire_pane\` through flagged capture and that selector. Viewport normalization and pytest subset behavior are retained.
- Clipboard decision: keep \`tmux load-buffer -\` plus \`termux-clipboard-set\`. Native \`load-buffer -w\`/OSC 52 is untested on target, not a demonstrated failure and not a blocker (D-003).
- Constraints to preserve: D-001 shared executor/no \`cpy_*\` fallback; D-002 last-P cutoff and exact pre-boundary content; D-003 deferred scopes and known clipboard route; D-004 keep PARTIAL until runtime acceptance. G2 remains open.
- Remaining-work inventory: full-history P/O flag proof; target binding and exact clipboard tests in both accepted contexts; full repository tests and fresh coverage; execute continuity checker; keep research and handoff status synchronized.

## Resume

**Next action:** After syncing the updated main branch, run `./_test/run test_copy_entire_pane.py && ./_test/run test_copy_executor.py && ./_test/run test_pytest_clipboard.py && ./_test/run`, then run `test-runner coverage && coverage report -m copy_executor.py copy_selector.py tmux.py`; finally exercise the CPY_ALL binding from root and Emacs-style `copy-mode` with output/prompt sentinels and verify the Android clipboard preserves every pre-prompt character while excluding the final prompt and everything after it.
**Read first:** \`_docs/PRD/2026-09-23-m-w-select-all-copy.md\`, \`_docs/_continuity/features/copy-refactor/roadmap.md\`, \`PL-0005\`, \`PL-0006\`, and \`PL-0007\`.
**Success criteria for next gate:** Target Termux confirms the final P row is found from full-history capture, only the pre-prompt text reaches tmux/Android clipboard unchanged, no-boundary/empty cases leave the clipboard untouched, and both root and Emacs-style copy-mode runs pass.
