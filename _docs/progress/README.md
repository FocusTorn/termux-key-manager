# Progress Workspace Guide

This directory is the working record for the native tmux copy refactor. It
separates **what happened**, **what remains**, and **what another chat needs
to continue**.

## Documents

- [Copy Runtime Progress Log](copy-runtime-log.md) — dated evidence: passing
  trials, failures, inconclusive results, invalid test setups, and corrections.
  It is the detailed record of observed behavior.
- [Copy Roadmap](copy-roadmap.md) — the current ordered work plan, statuses,
  dependencies, and exit conditions. It is the current planning source.
- [Copy Handoff](copy-handoff.md) — the concise status report used when moving
  this work into another chat. It identifies the objective, verified facts,
  unresolved questions, constraints, and the exact next action.

The source-level analysis remains in
[R1.1: tmux Internals](../research/r1_1-tmux-internals.md) and
[R1.2: TKM Implications](../research/r1_2-tkm-implications.md). The runtime
log links back to those documents.

## Each document has one job

### Progress log: evidence and history

Record each meaningful runtime trial with its date, observed result, and
classification: **PASS**, **FAIL**, **INCONCLUSIVE**, **INVALID TEST**, or
**NOT TESTED**. Include enough detail to distinguish an observed fact from an
inference. Keep failed attempts and setup mistakes; do not rewrite history to
make the sequence look clean.

The log is not the work plan. It should tell a reader what has actually been
tried and what the output did or did not establish.

### Roadmap: current plan

Maintain one current status for each work stage. Link to the progress log for
evidence instead of duplicating long transcripts. Reorder or split tasks when
evidence changes the dependencies. Do not mark an item complete merely because
a test was attempted.

The roadmap should make the next proof gate obvious.

### Handoff: switching chats

The handoff is a compact, replaceable status snapshot for a fresh chat. Its
purpose is to let the next chat resume without reconstructing the entire
conversation. It is not an independent source of truth and must not replace
the log or roadmap.

**Update the handoff last.** First record new evidence in the progress log,
then update roadmap statuses and the next gate, and only then rewrite the
handoff to summarize those updated documents. A handoff that predates the
latest log or roadmap state is stale.

## Update sequence

After each meaningful experiment or design decision:

1. Update **copy-runtime-log.md** with what happened and what the evidence proves.
2. Update **copy-roadmap.md** to reflect the new status and next dependency.
3. Rewrite **copy-handoff.md** last, using the log and roadmap as its sources.
4. Commit those related document updates together when practical.

If no experiment occurred but the plan changed, update the roadmap and then
the handoff. Update this README when the document roles or procedure change.

## Starting a new chat

1. Read this README for the workflow.
2. Read the handoff for the current state and immediate next action.
3. Check the roadmap for current priorities.
4. Open the progress-log section or research document linked by the handoff
   before repeating a test or treating a question as unanswered.

## Project constraints

- Do not change TKM implementation until the required behavior contracts have
  been demonstrated and the relevant tests have been written.
- The legacy helper family `cpy_*` must be decommissioned; no fallback,
  parallel implementation, or compatibility path is part of the target design.
- Keep evidence, inference, and open questions explicitly separate.
