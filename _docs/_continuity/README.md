# Project Continuity: TKM

## Purpose and reading order

This directory is TKM's canonical continuity system. Use it to preserve decisions and evidence across sessions without mixing history, plans, and resume snapshots.

Read in this order:

1. `README.md` — operating rules and TKM-specific constraints.
2. `INDEX.md` — feature inventory and lifecycle status.
3. The selected feature's `handoff.md` — resume snapshot.
4. Its `roadmap.md` — gates, decisions, dependencies, and complete remaining-work inventory.
5. Only the progress-log entries cited by the handoff/roadmap.

For the active copy work, start at `_docs/_continuity/features/copy-refactor/handoff.md`. For duplicate empty prompt filtering across all copy actions, use `_docs/_continuity/features/copy-prompt-dedup/handoff.md`.

## Canonical file responsibilities

| File | Authoritative for | Mutability |
|---|---|---|
| `features/<slug>/progress-log.md` | What was observed; append-only evidence entries with IDs `PL-####` | Append-only; corrections are new entries |
| `features/<slug>/roadmap.md` | Objective, gates, decisions (`D-###`), dependencies, all remaining work | Edited in place |
| `features/<slug>/handoff.md` | Resume snapshot | Replaced at transfer boundaries; never outranks the log or roadmap |
| `features/<slug>/closeout.md` | Final outcome and evidence | Written once, only at close |
| `INDEX.md` | Feature lifecycle status and short summary | Change only when status/final SHA changes |
| `check.sh` | Structural and synchronization checks | Change only when continuity rules need a justified update |

A feature remains ACTIVE while work is in progress. PARTIAL is a delivery assessment, not an additional INDEX lifecycle status: state it explicitly in the feature summary and roadmap. Do not create `closeout.md` or claim CLOSED while acceptance criteria remain unmet.

## Checkpoint/update order

When material evidence, requirements, decisions, dependencies, blockers, or next actions change:

1. Append a material entry to the progress log.
2. Reconcile the roadmap, decisions, gates, and complete remaining-work inventory.
3. Advance `**Progress through:**` to the newest real `PL-####` entry.
4. Refresh the handoff last at transfer boundaries or when materially outdated. Its `**Next action:**` must match the roadmap exactly.
5. Update the INDEX only when feature status or final SHA changes.

Continuity is not an activity diary. Do not log routine output, repeatedly run the checker without a concrete reason, or create entries only to move a marker. Preserve failures and uncertainty; inspected is not the same as executed or accepted.

## Initialization and migration

Initialization is an inspect-first semantic merge, not template copying. Retain useful content and history from legacy sources, map each artifact to one authoritative responsibility, redirect references, and retire legacy paths only after their content is preserved and validation is planned/performed. A migrated progress log remains append-only: keep inherited chronological sections in order and append continuity entries.

When shell execution is available, run:

```sh
bash _docs/_continuity/check.sh copy-refactor
bash _docs/_continuity/check.sh copy-prompt-dedup
```

In connector-only work, verify the actual remote tree, required paths, allowed statuses, PL/D/G references, synchronization markers, and identical next-action lines. Do not claim the checker script itself ran unless it was executed and its output inspected.

## TKM project constraints

- The PRD `_docs/PRD/2026-09-23-m-w-select-all-copy.md` governs CPY_ALL/M-w whole-pane copy acceptance: exclude the final shell prompt and everything after it, and preserve all preceding content exactly, including blank lines, trailing whitespace, and earlier prompts.
- Duplicate-empty-prompt filtering is a separate shared behavior requirement tracked in `features/copy-prompt-dedup/`. It applies to every copy action, not only CPY_ALL. Remove only redundant empty prompt rows when the prompt identity is the same; preserve distinct prompts even when their command input is empty. Prompt identity includes visible context such as the active project/alias and Git status. Do not confuse a distinct final prompt with a duplicate merely because it is empty.
- Do not use visible prompt text as the primary delimiter for the CPY_ALL protocol boundary when the protocol boundary is available. Prompt deduplication is a separate post-selection/filtering concern and must not weaken CPY_ALL's cutoff contract.
- The legacy `cpy_*` shell-helper family is decommissioned. No fallback, parallel implementation, or compatibility path is allowed.
- Define behavior contracts and write relevant tests before changing implementation. Follow `_docs/development.md`'s source-first workflow and verify generated/runtime behavior separately from unit tests.
- Root and Emacs-style `copy-mode` are the accepted runtime contexts for the current refactor. `copy-mode-vi` is explicitly out of scope unless scope is authorized to change.
- The proven clipboard endpoint is `termux-clipboard-set`. Native tmux `load-buffer -w` clipboard delivery is not established and is not a blocker to the current path. It is an untested alternative, not a known failure: tmux's terminal clipboard path uses OSC 52 and depends on `set-clipboard`, the terminal `Ms` clipboard capability, and terminal support; see the [tmux clipboard guide](https://github.com/tmux/tmux/wiki/Clipboard).
- Patch Failed-specific range selection is separate from the M-w PRD and remains deferred; it must not be silently included in CPY_ALL scope.
- Historical runtime outcomes in the progress log were reported from the user's Termux environment. Distinguish those recorded results from any checks executed by a future agent.

## Feature system

All unfinished work must remain visible in the feature roadmap. The INDEX status vocabulary is ACTIVE, PAUSED, BLOCKED, CLOSED, or ABANDONED; gate statuses are NOT STARTED, IN PROGRESS, BLOCKED, or DONE (with a supporting `PL-####` citation); log statuses are PASS, FAIL, INCONCLUSIVE, INVALID TEST, or NOT TESTED.
