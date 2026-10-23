# Copy Runtime Progress Log

**Started:** 2026-10-16  
**Updated:** 2026-10-22  
**Purpose:** Record dated runtime evidence, failures and inconclusive trials, and test-harness corrections while evaluating replacement of TKM's legacy `cpy_*` shell helpers with tmux copy-mode actions.

This document records only behavior demonstrated by the test outputs returned
from the Termux environment. Source-level analysis is recorded in
[R1.1: tmux Internals](../research/r1_1-tmux-internals.md) and
[R1.2: TKM Implications](../research/r1_2-tkm-implications.md).

## Evidence summary

| Behavior | Status | Evidence |
|---|---|---|
| Termux clipboard set/get utilities work | **PASS** | A known marker was written and read back |
| Copy the available pane history | **PASS** | Clipboard contained all 30 test markers, first through last |
| Copy only the visible viewport | **PASS** | Clipboard matched visible markers 24 through 30 |
| Copy an explicitly selected line range | **PASS** | Clipboard contained exactly the three selected lines |
| tmux copy-mode pipe to Termux clipboard | **PASS** | Manually selected ranges and isolated root/copy-mode test bindings transferred text through the pipe |
| Isolated root-table key recognition | **PASS** | Attached client Ctrl+G displayed `TKM_ROOT_KEY_OK` |
| Root binding enters copy mode | **PASS** | Copy-mode position indicator appeared after Ctrl+G |
| Chained `copy-mode` + `history-top` binding | **PASS** | Cursor observed at `1,1` while copy mode remained active |
| Root binding selection anchor and visible extension | **PASS** | Moving down to line end after beginning selection visibly highlighted fixture lines 1–2 |
| End-to-end root binding with selection and clipboard | **PASS** | The isolated root Ctrl+G binding copied exactly the first two fixture lines to Android clipboard on a subsequent attach/copy attempt |
| Invocation from the `copy-mode` table | **PASS** | The isolated Ctrl+G test binding copied the intended two fixture lines to Android clipboard and exited copy mode |
| Invocation from the `copy-mode-vi` table | **NOT TESTED** | Explicitly excluded from the current acceptance scope by the 2026-10-17 scope decision; no vi-mode trial will be run |
| Exclude a real interactive shell prompt | **NOT TESTED** | The subset test used a printed marker, not a live shell prompt |
| Automatic prompt flag before theme update | **FAIL (observed)** | Live capture row `X ~ ❯ tkm` had no `P`; see Sections 13–14 |
| Updated `focused2-termux` OSC 133 integration | **PASS** | User's 2026-10-22 capture showed `PX` on the prompt top-rule row and `O` on the output probe row |
| Direct OSC 133 marker handling in tmux 3.8 | **PASS** | Direct A/B/C sentinels appeared with prefixes `P`, `-`, and `O` |
| Interpret tmux 3.8 `W`/`X` flags | **PASS** | `X` appeared on Unicode prompt rows and `WX` on a wrapped line; tmux 3.8 maps `W` to wrapped and `X` to extended cells |
| Pytest semantic selector | **PASS (user-reported)** | The user reported the focused `test_pytest_clipboard.py` run as green on 2026-10-22 |
| Missing-marker and failure behavior | **TESTS ADDED; RUN PENDING** | Tests cover absent prompt, absent valid progress before the prompt, malformed rows, and prompt-like output without a `P` flag |
| Production `copy_entire_pane` via CPY_ALL | **PASS** | Fresh clipboard sentinel verified from root and emacs-style copy mode |
| Production `copy_subset` via CPY_TEST | **PASS** | Progress and end markers included; preceding marker excluded from root and copy-mode results |
| Production `copy_viewport` via the COPY popup | **PASS** | Visible sentinel included and older scrollback sentinel excluded from root and copy-mode results |
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
5. Isolated root- and `copy-mode`-table test bindings have copied a known
   range to Android clipboard; the `copy-mode` test also exited copy mode.
   The `copy-mode-vi` context is deliberately out of scope by the
   2026-10-17 decision recorded below. Actual TKM binding integration and
   semantic boundary discovery remain untested.
6. These tests do not yet prove automatic pytest/`Patch Failed` boundary
   discovery or reliable exclusion of a real terminal prompt.
7. These tests do not compare the external Termux clipboard pipe with tmux's
   own terminal clipboard integration.

The tmux runtime version was not recorded alongside the outputs summarized
here. The source-level investigation's target version is documented
separately in R1.1.

## 6. Root-key binding trials (2026-10-17)

These were isolated tmux probes, not TKM's configured macro bindings. They
establish individual key-table and copy-mode operations, not the complete copy
contract.

1. **PASS — root key dispatch.** A root-table binding mapped Ctrl+G to a
   five-second `display-message`. Pressing Ctrl+G in the attached client
   visibly displayed `TKM_ROOT_KEY_OK`.
2. **PASS — copy-mode entry.** Rebinding Ctrl+G to `copy-mode` displayed the
   copy-mode position indicator.
3. **PASS — chained history-top.** The binding
   `copy-mode \; send-keys -X -t proof:0.0 history-top` entered copy mode and
   moved the cursor to `1,1`.
4. **INCONCLUSIVE — full selection and clipboard chain.** An earlier combined
   binding did not return the expected marker lines; the clipboard instead
   contained the literal `termux-clipboard-get` command text. A later state
   check reported `PANE_IN_MODE=0`, and a subsequent server had lost its
   binding. The test did not prove a successful full chain, but it also did
   not isolate the cause to selection or clipboard piping.

5. **PASS — root-binding selection anchor and extension.** In the fresh
   long-lived `proof` fixture, the root Ctrl+G binding chained `copy-mode`,
   `history-top`, `start-of-line`, and `begin-selection`. The cursor was
   observed at `1,1`. After adding `cursor-down` and `end-of-line`, the user
   reported that fixture lines 1 and 2 were visibly highlighted. This proves
   the selection anchor and visible extension; clipboard transfer from this
   complete binding remains untested.

### Command-queue correction

The direct command entered at the outer zsh prompt returned `not in a mode`.
Loading the full command list from a tmux configuration file with `source-file`
registered the chained binding, after which the selection test passed. Treat
the first command form as a command-parsing/setup issue, not a selection
failure.

6. **INCONCLUSIVE — root-binding clipboard attempt.** The binding was extended
   with `copy-pipe-and-cancel 'termux-clipboard-set'`. The user reported no
   visible highlight after pressing Ctrl+G and then an empty result from
   `termux-clipboard-get`. Because `copy-pipe-and-cancel` exits copy mode and
   clears the selection, the missing highlight alone does not establish that
   selection failed. The empty clipboard means the end-to-end path was not
   demonstrated. The transcript did not conclusively identify whether the
   client was attached to the isolated `tkm-root-key-proof` server, so the
   binding target also remains unconfirmed.

   Next, sanity-check the current `termux-clipboard-set`/`get` round trip,
   inspect the isolated server's sessions and stored Ctrl+G binding, and
   explicitly attach with `tmux -L tkm-root-key-proof attach-session -t proof`
   before retrying. Do not infer selection or clipboard success from a stored
   binding or from copy mode closing.


7. **PASS — root-binding selection-to-clipboard path (2026-10-17).** The
   isolated server was stopped and recreated from the outer Termux shell,
   with `TMUX` and `TMUX_PANE` unset and a long-lived `sleep 3600` fixture.
   The root Ctrl+G binding was loaded from a configuration file and verified
   in the root key table. The first clipboard check after an attempt was
   empty; after a subsequent attach/copy/detach cycle,
   `termux-clipboard-get | cat -vet` returned the intended fixture text:

   ```text
   TKM_CONTEXT_BEFORE$
   TKM_CONTEXT_START
   ```

   The second line had no trailing newline, matching the tmux buffer: both
   stored buffers were 36 bytes and contained
   `TKM_CONTEXT_BEFORE\\nTKM_CONTEXT_START`. The shell prompt appeared
   immediately after the second line, consistent with that buffer content.

   The user subsequently confirmed seeing the `TKM-PROOF:proof` status bar and
   pressing Ctrl+G inside the attached Test Session. This resolves the earlier
   transcript ambiguity about whether the successful copy was triggered from
   the intended interactive client.

   **Result: PASS for this isolated root-table binding.** The complete path
   selected the expected range and transferred it to Android clipboard through
   `copy-pipe-and-cancel 'termux-clipboard-set'`. The cause of the earlier
   empty clipboard read remains undetermined. This does not prove behavior
   from `copy-mode-vi`, actual TKM bindings, or semantic boundary
   discovery.

### Test-fixture lifetime finding

The isolated pane's foreground command ended with `sleep 300`, a five-minute
lifetime. The 2026-10-17 session was created around 03:18 and the next attach
attempt around 03:23 returned `[exited]`. The earlier session was created
around 22:43 and inspected around 22:48, with the same disappearance. Both
intervals match expiration of `sleep 300`; when that pane command exits, the
only session can close and the isolated server can disappear.

This is the likely explanation for the apparent session timeout. Ctrl+B then
D returns the client to Termux by detaching; that behavior alone does not
show that the server was killed. Future test fixtures must use a long-lived
foreground process such as `sleep 3600`, and the next test should be run before
that process expires.

## 7. Copy-mode table binding trial (2026-10-17)

**Setup:** The isolated `proof` session was recreated with a long-lived
`sleep 3600` foreground process. A config file loaded Ctrl+G test bindings
into both `copy-mode` and `copy-mode-vi`; the window was explicitly set to
`mode-keys emacs`, so this trial exercised only the `copy-mode` table.
These are isolated test bindings, not TKM's configured macros.

**PASS — selection, tmux buffer, clipboard, and mode exit.** After resetting
the Android clipboard, the client attached to `proof`; Ctrl+B then `[` entered
copy mode, and Ctrl+G ran the `copy-mode` binding. The selected fixture range
was exactly:

```text
TKM_CONTEXT_BEFORE
TKM_CONTEXT_START
```

The tmux paste buffer contained those two lines. The mode-state check returned
`PANE_IN_MODE=0`, showing that `copy-pipe-and-cancel` exited copy mode. The
subsequent, separately typed `termux-clipboard-get | cat -vet` check returned
the same two lines with no trailing newline after `TKM_CONTEXT_START`; the
Termux prompt appeared immediately after the marker. This is the successful
Android clipboard read, not the earlier diagnostic text.

An earlier diagnostic block had overwritten the clipboard with its own
shell-command text, so that read was inconclusive. The clipboard was reset,
the copy action was repeated, and the result was retrieved by manually typing
the getter command. That subsequent check is the passing evidence.

**Scope:** This proves the isolated `copy-mode`-table binding in emacs mode.
The similarly installed `copy-mode-vi` binding was not exercised because the
window remained in emacs mode. Actual TKM bindings and semantic boundary
discovery remain untested.

## 8. Required next proof gates

Before changing TKM source, test and record:

1. **Execution contexts:** root and `copy-mode` isolated test bindings pass.
   `copy-mode-vi` is explicitly out of scope by the decision in Section 9; it
   is not a remaining proof gate. Verify actual TKM binding integration when
   implementation begins.
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


## 9. Scope decision — omit vi-mode proof (2026-10-17)

The user explicitly chose not to spend time proving the `copy-mode-vi` key
table. This is a scope decision, not a test result: vi-mode was not tested,
and this work makes no claim that the copy binding works when invoked from
that table.

For this refactor, the required execution contexts are the root table and
emacs-style `copy-mode`. Do not run another `copy-mode-vi` trial or treat it
as a blocker. Continue with semantic subset and prompt-boundary contracts,
negative cases, behavior tests, then implementation.


## 10. OSC 133 prompt-flag discovery (2026-10-17)

**Command supplied and run by the user:**

```sh
tmux capture-pane -pF -S - | grep -E '^[A-Z-]*P[A-Z-]* ' | tail -n 5
```

**Observed:** no lines matched the `P` prompt-flag pattern. The probe did
not demonstrate that the active shell's real prompt is marked by tmux.

**Classification: FAIL for automatic prompt-flag discovery; cause unresolved.**
This is not evidence that tmux cannot expose OSC 133 marks. The probe filtered
out all non-matching lines, so it did not show the raw line prefixes. Two
questions remain separate:

1. Does tmux mark a line when a controlled OSC 133 sequence is emitted?
2. Does the user's normal zsh prompt emit the marker automatically?

Next, inspect raw `capture-pane -F` prefixes and run a controlled marker probe
in a disposable `zsh -f` tmux session. If the controlled markers appear as
`P` and `O` but the normal prompt does not appear as `P`, investigate the
active zsh prompt integration. Do not switch to visible-prompt matching or
change production shell configuration before this distinction is established.


## 11. Controlled marker probe did not emit evidence (2026-10-17)

The user reports `tmux 3.8`. The first full-history capture piped into
a grep for `P`-prefixed lines returned no matches, so the active shell's
prompt marking was not demonstrated. This does not establish why the prompt
was unmarked.

The user then ran the direct-emission probe in a disposable pane. Its capture
ended with `tail -n 12 | sed -n 'l'` and showed twelve dash-prefixed blank
rows. Because `tail` retained only the final rows of the pane capture, it
could have dropped the sentinel lines that were printed earlier. That output
does not establish whether the sentinels appeared or whether tmux assigned
`P` / `O` flags to them.

**Classification: INCONCLUSIVE (capture truncated).** The marker test did not
yield interpretable evidence; do not classify it as a failure of OSC 133 or
tmux's flag handling.

Next, repeat the direct-emission probe without `tail`. The disposable pane
contains only a few test lines, so print the entire bounded capture using
`sed -n 'l'`. First verify the A, B, and C sentinel text is present; only
then interpret the line flags. Keep controlled-marker handling distinct from
testing whether the user's ordinary zsh prompt emits OSC 133.


## 12. Direct OSC 133 marker handling confirmed (2026-10-17)

**Setup:** The user ran the direct-emission probe in a disposable pane on
`tmux 3.8`. The probe printed the OSC 133 A, B, C, and D sequences directly
from its child command, avoiding interactive `send-keys` parsing. The full
capture was inspected without `tail`.

**Observed output:**

```text
P TKM_OSC133_A_PROBE$
- TKM_OSC133_B_PROBE$
O TKM_OSC133_C_PROBE$
```

**Result: PASS for controlled marker handling.** tmux recognized the direct
OSC 133 sequence: the A sentinel line was flagged `P`, the B sentinel line
had no flag (`-`), and the C sentinel line was flagged `O`. The earlier
truncated capture was correctly inconclusive; this output supersedes that
uncertainty about tmux handling explicit marker sequences.

**Still unresolved:** the ordinary interactive zsh prompt has not been
observed with a `P` flag. The previous full-history grep found no matching
lines, so the next test must inspect raw flags around the live prompt. That
result will determine whether the active shell or its prompt framework needs
OSC 133 integration. Do not change production shell hooks or TKM source yet.

Inspect recent rows of the live pane:

```sh
tmux capture-pane -pF -S - | tail -n 40 | sed -n 'l'
```

The expected decision point is the actual prompt row's prefix, not merely
whether unrelated controlled markers can be flagged. If no live prompt row is
marked `P`, identify the active prompt framework and supported integration
before changing configuration. The `Patch Failed` selector remains deferred.


## 13. Live shell prompt capture (2026-10-17)

**Command run by the user:**

```sh
tmux capture-pane -pF -S - | tail -n 40 | sed -n 'l'
```

**Relevant output:**

```text
X ~ \342\235\257 tkm$
WX \342\235\257 tmux capture-pane -pF -S - | tail -n 40 | s$
- ed -n 'l'$
```

The live prompt row appears with `X`, not `P`. The command line was wrapped,
so its first row has `WX`; neither prefix contains the prompt flag. The tmux
3.8 source shows `W` represents a wrapped line and `X` represents a line
containing extended cells:
https://fossies.org/diffs/tmux/3.7c_vs_3.8/cmd-capture-pane.c-diff.html

**Result: FAIL for automatic prompt marking in this live sample.** This does
not contradict the passing direct-emission test: tmux recognized explicit
OSC 133 A/C markers, but the interactive shell prompt did not receive a `P`
flag in the captured state. No TKM source or production prompt hooks have
been changed.

**Next diagnostic — identify the active zsh prompt framework without making
configuration changes:**

```zsh
printf 'ZSH_VERSION=%s\nZSH_THEME=%s\n' "${ZSH_VERSION:-<unset>}" "${ZSH_THEME:-<unset>}"
typeset -p PROMPT RPROMPT precmd_functions preexec_functions 2>/dev/null
for cmd in starship oh-my-posh p10k; do whence -va "$cmd" 2>/dev/null; done
```

Use these results to identify the actual prompt renderer and its hook setup.
Do not infer a framework from the glyphs alone, replace the current prompt, or
install/enable OSC 133 hooks speculatively. The `Patch Failed` selector remains
deferred.


## 14. Active prompt theme identified and OSC 133 integration committed (2026-10-17)

The user reported these read-only runtime diagnostics:

```text
ZSH_VERSION=5.9.2
ZSH_THEME=focused2-termux
PROMPT: assembled from FOCUSED_PROMPT_RULE, FOCUSED_PROMPT_INFO,
        FOCUSED_PROMPT_DIR, and the prompt glyph
precmd_functions:
  _omz_async_request
  omz_termsupport_precmd
  omz_termsupport_cwd
  precmd_update_git_vars
  _zsh_autosuggest_start
  _zsh_highlight_main__precmd_hook
  focused2_prompt_refresh
preexec_functions:
  omz_termsupport_preexec
  preexec_update_git_vars
  _zsh_highlight_preexec_hook
starship not found
oh-my-posh not found
p10k not found
```

**Source finding:** the active source is
`FocusTorn/zsh-customized-overlay/zsh/custom/themes/focused2-termux.zsh-theme`.
Before the update it built the multiline prompt from the three variables
listed above; it did not emit OSC 133 markers. This explains the live
capture's missing `P` prompt flag without contradicting the controlled tmux
marker test.

**Theme integration committed:**
https://github.com/FocusTorn/zsh-customized-overlay/commit/9a61d8ce444132b55435ddc3080ee964e80e476c

The change:
- wraps the existing `PROMPT` with zero-width OSC 133 A/B markers,
  preserving the visible multiline layout;
- emits OSC 133 C from the `preexec` hook before command output;
- emits OSC 133 D with the last command's status from a `precmd` hook;
- puts that `precmd` hook first so other hooks cannot change the captured
  status first, and removes/re-adds hooks to avoid duplicate registration.

**Classification: COMMITTED, RUNTIME NOT TESTED.** Remote source checks
confirmed the prompt wrapper and C/D hook code are present. No zsh runtime or
Termux test has yet verified the modified prompt. The user must sync/load the
new overlay theme before testing it. Use the UTR G suite's `g l` selector to
pull and check repository review state; `g n` copies the normalized origin
URL. These are the canonical Git operations for this workflow.

**Runtime proof after loading the update:** first sync the overlay and reload
the shell:

```sh
cd "$HOME/projects/_universal-termux-resources" && g l || exit
cd "$HOME/projects/zsh-customized-overlay" && g l || exit
exec zsh -l
```

Then run the output probe in the reloaded shell:

```sh
printf '%s\n' 'TKM_OSC133_OUTPUT_PROBE'
tmux capture-pane -pF -S - | tail -n 40 | sed -n 'l'
```

Expected evidence: the current prompt's top rule row carries a `P` flag, and
`TKM_OSC133_OUTPUT_PROBE` appears on an `O`-flagged row. A wrapped row may
also have `W`; that is independent of the prompt/output flags. If either
expected marker is missing, preserve the complete capture and diagnose before
implementing the TKM subset selector.


## 15. Live OSC 133 prompt/output flags confirmed (2026-10-22)

**Command run by the user:**

```sh
printf '%s\n' 'TKM_OSC133_OUTPUT_PROBE'; tmux capture-pane -pF -S - | tail -n 40 | sed -n 'l'
```

**Observed flag evidence:**

```text
PX <prompt top-rule row>
X 0931.58 | zco ... main | ✔
WX <wrapped command row>
O TKM_OSC133_OUTPUT_PROBE
```

**Result: PASS for live shell integration.** The `P` flag appears on the
interactive prompt's top-rule row; `X` identifies extended cells, and `W`
identifies a wrapped row. The probe output carries `O`. This confirms that
the updated `focused2-termux` theme and tmux's `capture-pane -F` metadata
work together in the live Termux session.

This verifies the prerequisite marker path, not the selector's behavior on a
completed pytest run and not the production TKM action binding.

**Selector slice added:** `copy_selector.select_pytest_subset` reads these
flagged capture rows, selects the latest valid pytest progress line before the
last `P` row, removes each row's flag prefix, and preserves selected text
and line endings. It returns `None` when either boundary is missing or a
capture row is malformed, so the caller can leave the clipboard untouched.
Focused tests were added to `_test/test_pytest_clipboard.py` for repeated
runs, missing boundaries, blank and multiline output, prompt-like output
without `P`, and malformed rows.

**Validation status: TEST RUN PENDING.** Run the test through the project's
normal runner before wiring the selector into TKM's native copy actions:

```sh
./_test/run test_pytest_clipboard.py
```


## 16. Focused test runner argument correction (2026-10-22)

**User-run command:**

```sh
./_test/run test_pytest_clipboard.py
```

**Observed result:**

```text
test-runner: only one test path is allowed
```

**Classification: INVALID TEST INVOCATION, not a selector-test failure.** The
wrapper always passed the whole `_test` directory and then appended any
provided argument, so the focused invocation reached `test-runner` with two
test paths. No pytest assertions ran.

Updated `_test/run` to accept zero or one test path: no arguments runs the
entire `_test` suite; one argument selects that path, resolving relative paths
from the project root first and then allowing a suite-relative filename. More
than one argument is rejected by the wrapper with a specific usage error.

**Validation status: RETRY PENDING.** Re-run the original focused command after
pulling this correction:

```sh
./_test/run test_pytest_clipboard.py
```


## 17. Focused pytest selector tests passed (2026-10-22)

The user reported the corrected command's result as **green** after running:

```sh
./_test/run test_pytest_clipboard.py
```

**Classification: PASS, user-reported.** The focused selector test gate is treated
as passed. No test count or detailed runner transcript was supplied, so none is
inferred. The earlier `test-runner: only one test path is allowed` result remains
classified as an invalid invocation, not a test failure.

## 18. Shared native copy executor added (2026-10-22)

Added `copy_executor.py` as the single execution path for `copy_entire_pane`,
`copy_viewport`, and `copy_subset`. The executor uses `capture-pane` for the
requested range, stores successful text in the tmux paste buffer with `load-buffer -`, and sends the same text to the proven `termux-clipboard-set` endpoint. The
pytest subset path consumes `capture-pane -pF -S -` and fails closed when its
prompt/progress boundaries are missing, leaving the clipboard unchanged. When
the action starts in copy mode, the executor cancels that mode after the copy
attempt to avoid state leakage.

The macro definitions now dispatch directly to the executor; the generated
`helpers.sh` no longer contains the legacy `cpy`, `cpy_all`, `cpy_test`,
or `cpy_pytest` implementations. `copy_viewport` is wired to the existing
COPY popup, `copy_entire_pane` to CPY_ALL/CPY_PASTE, and `copy_subset` to
CPY_TEST.

**Clipboard-path decision:** use `termux-clipboard-set`, which was proven in the
isolated copy-pipe tests, rather than relying on tmux's native `load-buffer -w`
terminal clipboard path. That native `-w` path remains untested.

**Verification status: SOURCE AND CONTRACT TESTS ADDED; RUNTIME PENDING.** The
selector suite was user-reported green before this implementation. The new
executor tests and updated binding/configuration tests have not yet been run
against this implementation in Termux. `Patch Failed` remains deferred.


## 19. Static integration review correction (2026-10-22)

A post-commit source review found one stale unit-test expectation: the
`get_tmux_actions` fixture included the new `copy_viewport` action, but its
expected list omitted it. The expected list is corrected before the new
executor tests are run. The executor failure-path test also now asserts that
neither the tmux paste buffer nor Android clipboard is written when the pytest
selector cannot find its required boundaries.

**Classification: STATIC REVIEW CORRECTION; RUNTIME NOT TESTED.** No new test
result is inferred. The focused executor suite remains the next runtime gate.


## 20. Executor focused test run exposed a capture-flag assertion mismatch (2026-10-22)

**User-run command:**

```sh
./_test/run test_copy_executor.py
```

**Observed result:** 1 failed, 5 passed. The failure was in
`test_copy_subset_selects_latest_pytest_range_and_uses_shared_clipboard`:
the assertion expected a standalone `-F` element, but the captured argv
contains `-pF` as one argument.

**Classification: FAIL (test assertion mismatch).** The executor invokes
`capture-pane -pF -S -`, matching the roadmap's documented command. The
test uses a mocked tmux process, so this failure does not show that the live
tmux operation or copy executor runtime is broken.

The assertion is now aligned to check `-pF` instead of a standalone `-F`.
That source correction has not yet been re-run. Focused executor verification,
the broader regression suite, and production action runtime verification
remain pending.

**Next action:** run `./_test/run test_copy_executor.py`; if green, run
`./_test/run` and continue the required production-binding runtime checks.


## 21. Focused executor test rerun reported green (2026-10-22)

**User report:** the corrected focused command completed green after the
assertion was changed to check the combined `-pF` argument.

```sh
./_test/run test_copy_executor.py
```

**Classification: PASS (user-reported).** The user confirmed a green run.
No test count or full runner transcript was supplied, so neither is inferred.
The earlier `1 failed, 5 passed` result remains valid evidence for the
initial, incorrect assertion; this subsequent report supersedes its status as
the current focused-test result.

This proves the focused executor test run was reported green. It does not
prove that the production copy actions work in the live Termux/tmux runtime.
The runner's Testmon-selected mode can omit tests; omitted tests are not
executed.

**Next action:** run `./_test/run` for the repository runner's broader
regression pass, review what Testmon selected, then verify the production
actions from root and emacs-style `copy-mode`, including clipboard contents
and mode exit. Keep Gate 5 open until those runtime checks pass.

## 22. Testmon-selected runner run exposed a f-string NameError in the config test (2026-10-22)

**User-run command:**

```sh
./_test/run
```

**Observed result:** the runner stated that it was using Testmon-selected
coverage. Pytest reported **1 failed, 31 deselected**. The selected failure
was `TestTmuxConfig.test_tmux_config_for_copy_actions` at
`_test/test_manager.py:673`; Python raised
`NameError: name 'pane_id' is not defined` while evaluating the expected
string, before the config assertion could compare values.

**Root cause:** the expected string is a Python f-string that contains the
tmux format token `#{pane_id}`. Python interpreted the braces as f-string
interpolation. The expectation must escape the braces as `#{{pane_id}}` in
the source to produce the literal `#{pane_id}` at runtime.

**Classification: INVALID TEST (assertion construction error).** This
traceback is not evidence of a broken production binding; the assertion did
not reach its comparison. The expected-string source has been corrected.
No passing rerun is inferred.

**Next action:** rerun `./_test/run`, inspect the Testmon selection and result,
and keep broader regression and production action runtime verification
pending until separately established.

## 23. Full coverage test run passed (2026-10-22)

**User-run command:** `test-runner coverage`

The runner explicitly reported that coverage mode runs all tests in the
selected target, rather than Testmon-selecting a subset.

**Observed result: PASS.** Pytest reported `49 passed in 0.47s`. A JSON
coverage report was written to the Termux temporary directory. The displayed
coverage summary was:

| Module | Statement coverage |
| --- | ---: |
| `copy_executor.py` | 75% |
| `copy_selector.py` | 88% |
| `tmux.py` | 94% |
| Total | 90% |

The report showed 400 statements, 36 missed statements, 158 branches, and 19
partial branches across the listed modules. This is full-suite test evidence
for the selected target and confirms the f-string assertion correction no
longer causes the suite to fail. Coverage percentages do not establish that
the uncovered branches are harmless, nor do unit/contract tests establish
live production copy behavior.

**Next action:** verify the generated configuration and run the three
production copy actions from root and emacs-style `copy-mode`, checking
selected text, Termux clipboard contents, and mode exit. Keep Gate 5 open
until the required runtime checks pass.


## 24. Production macro runtime matrix passed (2026-10-22)

**Setup:** The user exercised the production TKM macro bindings in live
Termux/tmux. CPY_ALL invokes `copy_entire_pane`; the `COPY` popup on CPY_ALL
invokes `copy_viewport`; and CPY_TEST invokes `copy_subset`. Root-mode
checks used fresh sentinels and read them back with
`termux-clipboard-get`. Copy-mode checks were armed before entering copy
mode so no follow-up pasted command could overwrite the clipboard under test.

| Production action | Root | Emacs-style `copy-mode` |
|---|---|---|
| `copy_entire_pane` — CPY_ALL | **PASS** — the fresh root sentinel was found in the Termux clipboard | **PASS** — the copy-mode sentinel was found and the output explicitly reported that CPY_ALL exited copy mode automatically |
| `copy_subset` — CPY_TEST | **PASS** — clipboard contained `... [100%]` and the end sentinel; the before sentinel was absent | **PASS** — the armed checker verified the progress and end markers, excluded the before sentinel, and returned to the shell after the macro |
| `copy_viewport` — CPY_ALL's `COPY` popup | **PASS** — the visible sentinel was present and the older scrollback sentinel was absent | **PASS** — the final checker observed copy-mode exit, found the visible sentinel, excluded the older scrollback sentinel, and printed a PASS result |

**Observed:** All six production action/context checks reported PASS. The
copy-mode viewport capture also included other shell text that was visible in
the viewport; that is expected for a viewport copy. The acceptance assertion
was that the fresh visible marker was present and the intentionally older
marker was absent.

**Interpretation:** the required production runtime matrix is now demonstrated
for root and emacs-style `copy-mode`. This does not extend the acceptance
scope to `copy-mode-vi`, prove the native tmux `load-buffer -w` clipboard
path, or demonstrate live selection of a real `Patch Failed` range.

### Harness corrections and preserved uncertainty

Early copy-mode viewport attempts were not used as product-failure evidence:
one attempt did not reliably establish that the earlier marker was off-screen,
and another checker was suspended by interactive shell job control. A later
Zsh test block also hit history expansion while validating a shell pattern.
The final successful viewport trial used 60 filler lines, printed the visible
sentinel immediately before entering copy mode, detached the background
checker from terminal input, and reported that the older marker was absent.
These setup problems explain why the earlier attempts were inconclusive; they
do not override the final observed PASS.

### Coverage follow-up note

A static review of the current executor, selector, and tests identified
candidate edge cases that do not have explicit assertions in the inspected
test files: missing `pane_id`, empty non-subset capture output, subprocess
failures during tmux/clipboard operations, and selector parsing for CRLF or
an unterminated final row. The last full coverage run reported 75% statement
coverage for `copy_executor.py`, 88% for `copy_selector.py`, and 94% for
`tmux.py`; however, its line-level missing-coverage report was not retained
in this repository's evidence. These cases are candidates for review, not
claims about exact uncovered lines. Gate 6 carries the line-specific coverage
audit forward.


## 25. Current helper documentation reconciled (2026-10-22)

**Classification: STATIC REPOSITORY AUDIT; NOT A RUNTIME TEST.**

A source/documentation audit after the production runtime matrix found that
several operational guides still described removed clipboard shell helpers as
current behavior. The stale descriptions covered the helper inventory,
registered tmux actions, generated helper output, and examples invoking
`cpy_all` from a shell. Affected guides: `_docs/actions.md`,
`_docs/architecture.md`, `_docs/clipboard.md`, `_docs/commands.md`,
`_docs/generated-files.md`, `_docs/macros.md`, `_docs/primer.md`,
`_docs/tmux.md`, and `_docs/testing.md`.

**Observed in current source:** the inspected `_templates/helpers.sh.template`
contains no `cpy_*` definitions; `helpers.py` generates that template and
does not implement clipboard-copy functions; `macros.py` maps current copy
actions to `copy_executor.py`; and `copy_executor.py` / `copy_selector.py`
provide the shared executor and pytest selector. `_test/test_manager.py`
retains intentional negative assertions that old helper functions are not
generated.

The nine operational guides were reconciled with the active routes: CPY_ALL
main key -> `copy_entire_pane`, CPY_ALL COPY popup -> `copy_viewport`,
CPY_TEST -> `copy_subset`, and CPY_PASTE -> `PASTE ENTER` followed by
`copy_entire_pane`. The guides now treat the executor and selector as
repository source modules, not generated files.

**Preserved intentionally:** historical references in this append-only log
and source-level research notes remain as history. Regression assertions
mentioning old helper names remain so those functions cannot silently return.
These are not active definitions or invocations.

**Next implication:** stale current-operation guidance is reconciled. Gate 6
remains open for the line-specific missing-coverage audit and final
diff/ref/history verification. Aggregate coverage percentages do not establish
the exact missing lines.


## 26. Detailed coverage command identified (2026-10-22)

**Classification: STATIC TOOLING REVIEW; NOT A TEST RUN.**

The project's `_test/TEST-RUNNER.md` is a symlink to the shared UTR test-runner
guide. The canonical `scripts/test-runner/test-runner.sh` implementation in
`FocusTorn/_universal-termux-resources` shows that coverage mode executes
`coverage run -m pytest`, then formats a Termux-specific summary. The
formatter creates a temporary JSON report with `mktemp`, prints aggregate
per-file statement/branch counts, and deletes the temporary JSON report.

The runner does not delete coverage.py's default `.coverage` data file. The
standard coverage report supports a missing-line column, so the focused
inspection command for the most recent coverage run is:

```sh
coverage report -m copy_executor.py copy_selector.py tmux.py
```

This command is expected to display line numbers; it does not run tests. If the
`.coverage` data file is absent or stale, rerun `test-runner coverage` first,
then issue the command above.

**Next implication:** Gate 6 no longer depends on finding the deleted
temporary JSON report. The line-specific coverage audit remains NOT TESTED
until the command output is observed; candidate missed branches recorded in
Section 24 remain hypotheses until compared with that output.


## 27. Detailed coverage report received and mapped (2026-10-22)

**User-run command:** `coverage report -m copy_executor.py copy_selector.py tmux.py`

**Observed result: PASS — detailed missing-line report retrieved.**

```text
Name               Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------
copy_executor.py      52     14     16      1    75%   40, 74-88
copy_selector.py      35      4     16      2    88%   9-10, 15-16
tmux.py               74      4     28      2    94%   63-64, 103, 124
--------------------------------------------------------------
TOTAL                161     22     60      5    87%
```

This focused report covers these three modules only, so its 87% aggregate
should not be compared to the earlier full-suite 90% total, which used a
different set of files/statements.

### Exact uncovered statements

- `copy_executor.py:40`: rejecting a missing `pane_id`.
- `copy_executor.py:74-88`: CLI parser/dispatch success, handled error, and
  no-content return paths in `main()`.
- `copy_selector.py:9-10`: CRLF row-ending parsing.
- `copy_selector.py:15-16`: rows without a final newline.
- `tmux.py:63-64`: rejecting an unknown tmux action name.
- `tmux.py:103`: config generation when `.tmux.conf` does not yet exist.
- `tmux.py:124`: inserting a separator when an existing config lacks a final
  newline.

### Targeted regression cases added

Added tests for the exact uncovered paths in `test_copy_executor.py`,
`test_pytest_clipboard.py`, `test_manager.py`, and
`test_tmux_replacement.py`. These additions are **NOT TESTED** until the user
runs the coverage command again. Branch coverage still requires the refreshed
report; this report identifies missing statements, not every unvisited branch
destination.

**Next implication:** statement misses now have explicit regression coverage
proposals. Re-run the full coverage target and inspect the refreshed missing
lines and branch counts before changing the coverage audit to PASS.
