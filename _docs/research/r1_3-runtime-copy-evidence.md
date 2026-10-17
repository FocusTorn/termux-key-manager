# R1.3: Native Copy Runtime Evidence

**Date:** 2026-10-16  
**Purpose:** Record runtime evidence gathered while evaluating replacement of
TKM's legacy `cpy_*` shell helpers with tmux copy-mode actions.

This document records only behavior demonstrated by the test outputs returned
from the Termux environment. Source-level analysis is recorded in
[R1.1: tmux Internals](r1_1-tmux-internals.md) and
[R1.2: TKM Implications](r1_2-tkm-implications.md).

## Evidence summary

| Behavior | Status | Evidence |
|---|---|---|
| Termux clipboard set/get utilities work | **PASS** | A known marker was written and read back |
| Copy the available pane history | **PASS** | Clipboard contained all 30 test markers, first through last |
| Copy only the visible viewport | **PASS** | Clipboard matched visible markers 24 through 30 |
| Copy an explicitly selected line range | **PASS** | Clipboard contained exactly the three selected lines |
| tmux copy-mode pipe to Termux clipboard | **PASS** | `copy-pipe-and-cancel 'termux-clipboard-set'` worked in the tests above |
| Root binding invocation | **NOT TESTED** | No actual TKM root-table binding was exercised |
| Invocation from `copy-mode` and `copy-mode-vi` | **NOT TESTED** | No actual TKM bindings were exercised in either table |
| Exclude a real interactive shell prompt | **NOT TESTED** | The subset test used a printed marker, not a live shell prompt |
| Locate pytest or `Patch Failed` semantic boundaries | **NOT TESTED** | The test selected a known line range rather than discovering markers |
| Missing-marker and failure behavior | **NOT TESTED** | No negative semantic-selector test was run |
| Native tmux terminal clipboard path without an external command | **NOT TESTED** | The passing clipboard tests used `termux-clipboard-set` as the pipe command |

## 1. Clipboard utility sanity check

The following marker was passed through `termux-clipboard-set` and retrieved
with `termux-clipboard-get`:

```text
TKM_CLIPBOARD_UTILITY_PROBE_20261016
```

**Result: PASS.** The Termux clipboard utilities were available and returned
the probe marker. This establishes a working clipboard endpoint for the tmux
pipe tests; it does not by itself prove tmux selection behavior.

## 2. Entire-pane history selection

An isolated tmux server was started with configuration `/dev/null`, and a
pane emitted 30 numbered markers, from `TKM_LINE_01` through
`TKM_LINE_30`.

The test entered copy mode, moved to `history-top`, began a selection at the
start of the line, moved to `history-bottom`, extended to the end of the
line, then invoked:

```sh
copy-pipe-and-cancel 'termux-clipboard-set'
```

Reading the Termux clipboard returned all 30 markers in order. The first was
`TKM_LINE_01` and the last was `TKM_LINE_30`.

**Result: PASS.** A copy-mode selection can span the tested available pane
history and reach the Termux clipboard through the pipe command.

## 3. Visible viewport selection

A separate isolated server used an 80-column by 8-row pane. After emitting
numbered lines and holding the pane open, `capture-pane -p` showed the
visible marker range as `TKM_LINE_24` through `TKM_LINE_30`.

The test entered copy mode, positioned at `top-line`, selected from the start
of that line to `history-bottom` and the end of the line, then used the same
`copy-pipe-and-cancel` clipboard command.

The clipboard's marker range matched the visible viewport: lines 24 through
30.

**Result: PASS.** The tested selection copied the viewport range without
including the earlier, off-screen markers.

## 4. Explicit semantic-range selection primitive

The subset test pane was configured to emit these lines:

```text
TKM_SUBSET_BEFORE
TKM_SUBSET_START
TKM_SUBSET_RESULT_1
TKM_SUBSET_RESULT_2
TKM_SUBSET_PROMPT
TKM_SUBSET_AFTER
```

In copy mode, the test moved to the known start line, began a selection, moved
down two lines, extended to the line end, and used
`copy-pipe-and-cancel 'termux-clipboard-set'`.

The retrieved clipboard was exactly:

```text
TKM_SUBSET_START
TKM_SUBSET_RESULT_1
TKM_SUBSET_RESULT_2
```

Neither the preceding line nor the following prompt/trailing markers were
copied.

**Result: PASS.** tmux selection can express and copy a specifically bounded
line range.

**Important limitation:** `TKM_SUBSET_PROMPT` was a line printed by the test
command. It was not an actual interactive shell prompt. This test proves the
selection primitive, not automatic discovery of a prompt boundary or the
required pytest/`Patch Failed` semantic rules.

### Test-setup correction

The first subset attempt ran the test command in the invoking shell rather
than inside the isolated tmux pane. As a result, the captured content included
the invoking command and prompt instead of the intended marker output. That
attempt was invalid for the intended selection test.

The test was then corrected by starting the isolated tmux pane with the marker
command itself. The corrected run produced the exact three-line result shown
above. Treat the first attempt as a test-setup error, not evidence of a tmux
selection limitation.

## 5. Conclusions supported by current evidence

1. Termux clipboard set/get works in the tested environment.
2. tmux copy-mode can select the tested entire-history, viewport, and explicit
   line ranges.
3. `copy-pipe-and-cancel 'termux-clipboard-set'` successfully transfers those
   selected ranges to the Termux clipboard.
4. A shared selection-and-clipboard mechanism for multiple copy actions is
   technically plausible and worth continuing to test.
5. These tests do not yet establish how TKM should enter, operate within, or
   exit each of its three binding contexts.
6. These tests do not yet prove automatic pytest/`Patch Failed` boundary
   discovery or reliable exclusion of a real terminal prompt.
7. These tests do not compare the external Termux clipboard pipe with tmux's
   own terminal clipboard integration.

The tmux runtime version was not recorded alongside the outputs summarized
here. The source-level investigation's target version is documented
separately in R1.1.

## 6. Required next proof gates

Before changing TKM source, test and record:

1. **Execution contexts:** invoke the action from actual bindings in
   `root`, `copy-mode`, and `copy-mode-vi`.
2. **Cursor and prompt boundaries:** determine how the selection endpoint
   relates to pane output, the live shell prompt, and the application cursor.
3. **Semantic selection:** identify the required pytest result/progress start
   and `Patch Failed` start, ending immediately before a real final prompt.
4. **Negative cases:** missing markers, blank lines, multiline output, and
   other boundary cases must not silently copy an incorrect range.
5. **Clipboard path:** retain the proven Termux pipe unless and until the
   native tmux terminal clipboard path is separately demonstrated to satisfy
   the same contract.

No TKM implementation change is implied by this evidence record alone.
