# M-w Implementation Research

> **AGENT INSTRUCTIONS**
>
> This document is a reusable living implementation-research record.
>
> Read this section before modifying the document.
>
> Do not treat proposed behavior as verified behavior.
>
> For every stage:
>
> 1. Read the current hypothesis.
> 2. Inspect current source, tests, and documentation.
> 3. Identify the smallest deterministic probe.
> 4. Run the probe before making speculative production changes.
> 5. Record the exact finding.
> 6. Record the resulting decision.
> 7. Implement only behavior justified by the finding.
> 8. Record validation results.
> 9. Update dependent stages when new evidence changes an earlier assumption.
>
> Preserve superseded hypotheses and findings.
>
> Do not rewrite historical research to make the implementation appear linear.
>
> Pending means the behavior has not been established.
>
> Verified means the behavior has been established by source inspection, a deterministic probe, or an appropriate automated test.
>
> When this document conflicts with current production source or verified tests, investigate the conflict and update this document.
>
> Do not skip unresolved dependencies by assuming the proposed implementation is correct.
>
> Continue directly to the next justified research or implementation step when no blocking uncertainty remains.

Status: PARTIAL — CPY_ALL cutoff logic implemented; target runtime acceptance remains pending  
Implementation: Shared executor + final-prompt selector implemented; focused contract/regression tests pass locally; target Termux behavior NOT TESTED  
Last verified: 2026-10-23

---

# 1. Objective

## Feature

M-w whole-pane Select All → Copy

## Objective

Implement M-w as a terminal-level Select All → Copy operation.

The operation must copy the complete available content of the current tmux pane's scrollback into the system clipboard, except for the final shell prompt and anything rendered after that final prompt.

All content before the final prompt must otherwise be preserved exactly. No whitespace trimming or normalization is permitted.

## Target Flow

~~~
M-w
    ↓
capture complete tmux scrollback
    ↓
identify the LAST shell prompt boundary
    ↓
discard the final prompt and everything after it
    ↓
copy remaining content to system clipboard
~~~

The preferred prompt-boundary mechanism is OSC 133.

---

# 2. Scope

## Include

- M-w behavior for the current tmux pane.
- Complete available tmux scrollback capture.
- Reliable identification of the final shell prompt boundary.
- Exclusion of the final prompt and all content after it.
- Preservation of all content before the final prompt.
- System clipboard delivery.
- Deterministic verification on the target tmux/Termux environment.
- Integration with the TKM-generated tmux configuration.

## Exclude

- Patch Gate execution.
- Patch Gate validation or policy.
- pytest-specific extraction.
- Patch Failed-specific extraction.
- Generic semantic text processing.
- Patch Gate clipboard-to-executor behavior.
- Any requirement to modify arbitrary terminal output.

## Constraints

- M-w is conceptually Select All → Copy.
- Earlier prompts are part of the copied content.
- Only the final prompt and everything after it are excluded.
- Output whitespace must be preserved.
- Do not identify prompts by guessing from visible prompt text when a protocol boundary is available.
- Prefer standardized OSC 133 prompt/command boundaries over a custom private marker.
- Do not make production changes until the required tmux/OSC 133 behavior is verified.
- Target tmux version is 3.7c.
- Target environment is Termux.

---

# 3. Initial Architectural Hypothesis

~~~
shell prompt
    ↓
emit OSC 133 prompt boundary
    ↓
tmux records terminal state/output
    ↓
M-w invokes tmux scrollback capture
    ↓
captured content contains usable prompt boundary information
    ↓
locate the LAST prompt boundary
    ↓
discard from that boundary through end of capture
    ↓
send remaining content to termux-clipboard-set
~~~

The architecture remains a hypothesis until each required boundary is verified. Historical stage notes below retain their original chronology; the current implementation/test state is summarized in the 2026-10-23 update at the end of this document.

A textual prompt such as:

~~~
~/projects/gpt-termux-rules $
~~~

must not be the primary delimiter. Such text can legitimately occur inside command output.

---

# 4. Research Status

| Stage | Status | Evidence | Decision |
|---|---|---|---|
| Prompt boundary protocol | Partially verified; full-history CPY_ALL use pending | The inherited runtime log §15 records live P/O flags; subset capture used `-pF`. The exact full-history CPY_ALL capture must still be confirmed in Termux. | Use the P line flag as a protocol boundary, not visible prompt text, and keep target-runtime proof open. |
| Scrollback capture | Source updated; runtime pending | CPY_ALL now requests `capture-pane -pF -S -` so prompt flags are present and wrapped rows are not joined. | Verify this exact full-history invocation on the target. |
| Final-boundary extraction | Implemented; focused contract tests pass locally | `select_entire_pane` keeps rows before the last P-flagged row, preserves visible text/endings, and fails closed; PL-0005–PL-0006. | Preserve earlier prompts and all prior captured content exactly. |
| Clipboard delivery | Existing endpoint recorded PASS; native tmux path remains untested | The executor writes the selected text to tmux's paste buffer and `termux-clipboard-set`. `load-buffer -w` was not established. | Retain the recorded Termux endpoint for current acceptance. |
| M-w integration | Source updated; target runtime pending | The shared executor routes CPY_ALL through flagged capture and final-prompt selection; the isolated focused suites passed 23 tests. | Validate the production key binding and exact clipboard result in Termux before closing the gate. |

---

# Stage 1: Prompt Boundary Protocol

## Objective

Establish how the target shell can emit an explicit prompt boundary using OSC 133 and whether that boundary is preserved or otherwise exposed through the tmux capture path used by M-w.

## Current Hypothesis

OSC 133 provides a standardized terminal protocol for identifying shell prompt and command boundaries.

The intended conceptual sequence is:

~~~
OSC 133;A
prompt
OSC 133;B
command
output
OSC 133;C
OSC 133;D
next prompt
~~~

The final prompt boundary should provide an unambiguous cutoff for M-w.

## Existing Evidence

- tmux 3.7c documentation describes command-output boundaries associated with OSC 133.
- tmux capture/copy behavior provides access to pane content and command-output boundary concepts.
- TKM research identifies textual prompt matching as insufficient for an unambiguous final-prompt delimiter.
- The visible TKM prompt convention is path-based, for example ~/projects/gpt-termux-rules $, but this is not sufficient as a protocol-level delimiter.

## Relevant Sources

- _docs/research/r1_1-tmux-internals.md
- _docs/research/r1_2-tkm-implications.md
- _docs/PRD/2026-09-23-m-w-select-all-copy.md
- Target shell initialization source once identified.
- Generated ~/.bashrc once the source path is identified.
- Generated ~/.tmux.conf once the M-w source is identified.
- tmux 3.7c manual.

## Probe

Status: Pending

Create a disposable tmux session using the target shell.

Emit controlled OSC 133 markers around a known prompt and command output. Capture the pane using the exact capture mode intended for M-w. Inspect the captured representation and determine whether the markers survive or whether tmux exposes equivalent boundary state through another interface.

## Probe Command

~~~bash
# Record the exact deterministic probe after the target shell
# initialization path is confirmed.
~~~

## Expected Result

The prompt boundary must be observable in a deterministic form that M-w can use to identify the final prompt without textual prompt matching.

## Finding

Status: Pending

~~~text
Not yet established on the target Termux/tmux environment.
~~~

## Decision

Status: Pending

~~~text
If OSC 133 survives in a directly usable capture representation, use it.
If tmux consumes the markers and exposes equivalent boundary state through
its capture/copy-mode interfaces, use that verified representation instead.
Do not invent a custom marker unless OSC 133 cannot provide the required
boundary and a separate decision is recorded.
~~~

## Implementation

Status: Not started

~~~text
No production prompt change until the probe establishes the exact mechanism.
~~~

## Validation

- [ ] OSC 133 prompt marker emitted by target shell.
- [ ] Marker survives or is otherwise exposed to the M-w capture path.
- [ ] Multiple prompt boundaries can be distinguished.
- [ ] Prompt-like ordinary output does not create a false boundary.

---

# Stage 2: Complete Scrollback Capture

## Objective

Establish the exact tmux capture operation required to obtain all available pane scrollback for M-w.

## Current Hypothesis

The full pane scrollback can be obtained with:

~~~bash
tmux capture-pane -p -J -S -
~~~

The capture is the raw input to the boundary-processing stage.

## Existing Evidence

- tmux 3.7c documents capture-pane, -p, -J, and -S -.
- Existing TKM research records the full-scrollback capture direction.
- The known M-w implementation direction uses capture-pane -p -J -S - followed by processing and clipboard delivery.

## Relevant Sources

- _docs/research/r1_1-tmux-internals.md
- _docs/research/r1_2-tkm-implications.md
- Current M-w binding/source.
- tmux 3.7c manual.

## Probe

Status: Verified

Use a controlled pane containing output before and after multiple prompts, including blank viewport space, and capture with capture-pane -p -J -S -.

## Probe Command

~~~bash
tmux capture-pane -p -J -S -
~~~

## Expected Result

The command produces the complete available scrollback for the current pane on stdout.

## Finding

Status: Verified

tmux 3.7c supports full-scrollback capture using capture-pane -p -J -S -.

## Decision

Status: Verified

Use tmux full-scrollback capture as the input to M-w.

The capture stage must not perform whitespace trimming or content normalization.

## Implementation

Status: Not started

Retain the full-scrollback capture mechanism and replace only the current post-capture processing with the verified final-prompt boundary operation.

## Validation

- [x] Full-scrollback capture command established.
- [ ] Verify exact interaction with the final OSC 133 boundary.
- [ ] Verify preservation of output whitespace.
- [ ] Verify content after the final prompt can be discarded deterministically.

---

# Stage 3: Final Prompt Boundary Extraction

## Objective

Establish the smallest deterministic operation that removes the final prompt and everything after it while preserving everything before it exactly.

## Current Hypothesis

Once Stage 1 establishes the captured representation of OSC 133 prompt boundaries, M-w can locate the LAST prompt boundary and use it as the exclusive end of the selected content.

Conceptually:

~~~
capture
    ↓
last prompt boundary
    ↓
keep content before boundary
    ↓
discard boundary and following content
~~~

Earlier prompt boundaries remain in the result.

## Existing Evidence

Required behavior has been established as the product requirement.

Input:

~~~text
output
output
~/projects/old $
output
output
~/projects/current $
~/projects/current $
~~~

Expected result:

~~~text
output
output
~/projects/old $
output
output
~~~

The visible prompt text is not a reliable delimiter, so extraction must use the verified protocol boundary.

## Relevant Sources

- _docs/PRD/2026-09-23-m-w-select-all-copy.md
- _docs/research/r1_1-tmux-internals.md
- _docs/research/r1_2-tkm-implications.md
- Stage 1 findings in this document.
- Stage 2 findings in this document.

## Probe

Status: Pending

Create controlled pane content with:

1. multiple earlier prompts;
2. output containing text resembling a prompt;
3. a final prompt;
4. blank lines after the final prompt;
5. additional terminal content after the final prompt.

Capture it and apply the candidate boundary extraction.

## Probe Command

~~~bash
# Record the exact extraction command after Stage 1 establishes
# the captured OSC 133 representation.
~~~

## Expected Result

Only content before the final prompt boundary is retained.

Everything before that boundary must remain unchanged, including ordinary output, earlier prompts, blank lines, trailing spaces, and other whitespace.

## Finding

Status: Pending

~~~text
Not yet established.
~~~

## Decision

Status: Pending

~~~text
Implement only the extraction operation demonstrated by the Stage 1
and Stage 3 probes.
~~~

## Implementation

Status: Not started

~~~text
No production implementation until the exact boundary representation
and extraction operation are verified.
~~~

## Validation

- [ ] Multiple prompts.
- [ ] Prompt-like output.
- [ ] Final prompt.
- [ ] Content after final prompt.
- [ ] Blank lines before final prompt.
- [ ] Trailing whitespace before final prompt.
- [ ] Empty pre-prompt selection.
- [ ] No accidental normalization.

---

# Stage 4: Clipboard Delivery

## Objective

Establish the final clipboard path after boundary extraction.

## Current Hypothesis

The selected content can be piped to termux-clipboard-set.

## Existing Evidence

- Existing TKM copy behavior uses termux-clipboard-set.
- tmux capture-pane -p provides captured content on stdout.
- The M-w requirement is delivery of the selected content to the system clipboard.

## Relevant Sources

- Current TKM copy implementation.
- _docs/research/r1_1-tmux-internals.md
- _docs/research/r1_2-tkm-implications.md
- Termux clipboard tooling.

## Probe

Status: Pending

Feed a known multiline payload containing blank lines and trailing spaces into termux-clipboard-set, then retrieve the clipboard and compare it with the source payload.

## Probe Command

~~~bash
payload='first
second  '

printf '%s' "$payload" | termux-clipboard-set
termux-clipboard-get
~~~

## Expected Result

The clipboard contains the supplied payload without M-w-specific trimming or normalization.

## Finding

Status: Pending

~~~text
Not yet established for the exact target preservation requirements.
~~~

## Decision

Status: Pending

~~~text
Use the clipboard path that preserves the verified M-w selection semantics.
~~~

## Implementation

Status: Not started

~~~text
Connect the verified Stage 3 result directly to the selected clipboard
delivery mechanism.
~~~

## Validation

- [ ] Multiline content.
- [ ] Blank lines.
- [ ] Trailing spaces.
- [ ] Earlier prompt text.
- [ ] No final prompt.
- [ ] No post-prompt content.

---

# Stage 5: M-w Integration

## Objective

Integrate the verified capture, prompt-boundary, extraction, and clipboard operations into the TKM M-w binding.

## Current Hypothesis

M-w can remain a tmux root binding because its operation applies to the current pane.

The binding should invoke one deterministic operation implementing the complete Select All → Copy flow.

## Existing Evidence

- TKM uses tmux bindings for terminal actions.
- tmux root, copy-mode, and copy-mode-vi key tables are distinct.
- M-w is a whole-pane copy operation, not a copy-mode selection movement.
- tmux can capture full pane history without entering copy mode.

## Relevant Sources

- macros.jsonc
- Current TKM tmux generation source.
- Current M-w tests.
- _docs/research/r1_1-tmux-internals.md
- _docs/research/r1_2-tkm-implications.md
- _docs/PRD/2026-09-23-m-w-select-all-copy.md

## Probe

Status: Pending

After Stages 1–4 are verified, generate the TKM tmux configuration and invoke M-w in a controlled pane.

Verify that the resulting clipboard exactly matches the Select All → Copy contract.

## Probe Command

~~~bash
# Record exact TKM generation/update and M-w integration commands
# after the implementation boundary is established.
~~~

## Expected Result

Pressing M-w:

1. captures complete scrollback;
2. identifies the final prompt boundary;
3. excludes the final prompt and everything after it;
4. preserves all earlier content exactly;
5. places the selected content in the system clipboard.

## Finding

Status: Pending

~~~text
Not yet established.
~~~

## Decision

Status: Pending

~~~text
Integrate only the implementation justified by Stages 1–4.
~~~

## Implementation

Status: Not started

~~~text
Production M-w integration is blocked until the OSC 133 capture boundary
is verified.
~~~

## Validation

- [ ] Generated tmux configuration contains the intended M-w behavior.
- [ ] M-w works from the root key table.
- [ ] Full scrollback is copied.
- [ ] Final prompt is excluded.
- [ ] Post-prompt content is excluded.
- [ ] Earlier prompts remain.
- [ ] Whitespace is preserved.
- [ ] Clipboard result is correct.

---

# Evidence Log

## Entry 001

Date: 2026-09-23

Stage:

~~~text
Requirement definition
~~~

Observation:

~~~text
M-w is a generic Select All → Copy operation. It is not a semantic
copy operation for pytest, Patch Failed, or other specialized subsets.
~~~

Impact:

~~~text
The implementation must remain narrowly scoped to complete pane/session
content bounded by the final prompt.
~~~

Decision:

~~~text
Keep M-w as an independent feature.
~~~

---

## Entry 002

Date: 2026-09-23

Stage:

~~~text
Final prompt boundary
~~~

Observation:

~~~text
The final prompt must be excluded, while earlier prompts remain part
of the copied content.
~~~

Impact:

~~~text
The operation cannot simply remove all prompt-looking lines.
~~~

Decision:

~~~text
Use the LAST explicit prompt boundary as the exclusive cutoff.
~~~

---

## Entry 003

Date: 2026-09-23

Stage:

~~~text
Output preservation
~~~

Observation:

~~~text
Trailing whitespace before the final prompt is part of the captured
output and must not be trimmed.
~~~

Impact:

~~~text
Whitespace normalization is prohibited from the M-w processing pipeline.
~~~

Decision:

~~~text
Boundary removal is the only content transformation required by M-w.
~~~

---

## Entry 004

Date: 2026-09-23

Stage:

~~~text
Prompt identification
~~~

Observation:

~~~text
The visible shell prompt has a path form such as:
~/projects/gpt-termux-rules $
~~~

Impact:

~~~text
A textual regular expression could confuse ordinary output with a prompt.
~~~

Decision:

~~~text
Prefer OSC 133 as the explicit prompt boundary.
~~~

---

## Entry 005

Date: 2026-09-23

Stage:

~~~text
tmux capture
~~~

Observation:

~~~text
tmux 3.7c supports capture-pane -p -J -S - for full scrollback capture.
~~~

Impact:

~~~text
A complete scrollback capture path is available without relying on
the visible viewport.
~~~

Decision:

~~~text
Use full scrollback capture as the M-w input.
~~~

---

# Superseded Assumptions

## Assumption 001

Original assumption:

~~~text
M-w can identify the final prompt by matching the visible textual
prompt, such as a path ending in "$".
~~~

Status:

~~~text
Superseded
~~~

Evidence:

~~~text
Prompt-like text can legitimately occur in command output, and the
requirement explicitly preserves earlier prompts.
~~~

Replacement:

~~~text
Use an explicit prompt boundary, preferably OSC 133, once its behavior
in the target capture path is verified.
~~~

---

## Assumption 002

Original assumption:

~~~text
Captured output should be trimmed before being copied.
~~~

Status:

~~~text
Superseded
~~~

Evidence:

~~~text
Trailing whitespace can be legitimate terminal output and must be
preserved.
~~~

Replacement:

~~~text
Do not trim or normalize captured output. Only remove the final prompt
boundary and everything after it.
~~~

---

# Implementation Change Log

## Change 001

Date: Pending

Stage:

~~~text
Pending
~~~

Change:

~~~text
No production change yet.
~~~

Reason:

~~~text
The prompt-boundary capture behavior remains unverified.
~~~

Validation:

~~~text
Pending
~~~

---

# End-to-End Validation

## Target Flow

~~~
M-w
        ↓
capture complete tmux scrollback
        ↓
locate final OSC 133 prompt boundary
        ↓
discard final prompt and all following content
        ↓
preserve preceding content exactly
        ↓
system clipboard
~~~

## Required Tests

- [ ] Primary successful path.
- [ ] Multiple earlier prompts remain copied.
- [ ] Final prompt is excluded.
- [ ] Content after final prompt is excluded.
- [ ] Prompt-like ordinary output is preserved.
- [ ] Blank lines are preserved.
- [ ] Trailing whitespace is preserved.
- [ ] Empty selection is handled deterministically.
- [ ] No prompt-boundary condition is handled deterministically.
- [ ] Root tmux binding works.
- [ ] Clipboard receives the exact selected content.
- [ ] Generated TKM configuration is correct.
- [ ] Relevant TKM regression tests pass.

## End-to-End Finding

Status: Pending

~~~text
Complete-system behavior has not yet been verified.
~~~

## Final Decision

Status: Pending

~~~text
Pending completion of the required research and validation stages.
~~~

---

# Final Verification

Status: Pending

## Required Conditions

- [ ] Every required stage has a verified finding.
- [ ] Every implementation decision is documented.
- [ ] No unresolved dependency remains.
- [ ] Production implementation is complete.
- [ ] Focused tests pass.
- [ ] Relevant regression tests pass.
- [ ] End-to-end behavior is verified.
- [ ] Known constraints are documented.

## Completion Record

Status:

~~~text
Pending
~~~

Implementation:

~~~text
Not verified
~~~

Last verified:

~~~text
2026-09-23
~~~

Final notes:

~~~text
M-w is defined as a narrow Select All → Copy operation. The required
selection consists of all captured pane content before the final shell
prompt boundary. Earlier prompts remain part of the selection. The
preferred boundary mechanism is OSC 133, but its exact behavior through
the target Termux shell, tmux 3.7c, and capture-pane path must be
verified before production implementation.

No whitespace trimming or output normalization is permitted.
Patch Gate Execution is a separate feature and is intentionally not
specified here.
~~~


# Current Status Update — 2026-10-23

This update supersedes the older stage-status summaries above where they say implementation has not started. The original stage narratives and dated findings are retained as historical research.

## Current source change

- `copy_executor.py` now captures CPY_ALL with `capture-pane -pF -S -`. It deliberately does not use `-J`, so this processing stage does not join pane rows.
- New `select_entire_pane` parsing uses the existing flagged-row parser, selects the last row whose flags include `P`, and returns only visible content preceding that row. Earlier prompt rows and prompt-like ordinary output without `P` remain included.
- Visible text and row endings from the captured pre-prompt rows are passed through without `rstrip`, trimming, or newline reconstruction. Missing/malformed prompt boundaries and empty selections return no result; the executor therefore skips both the tmux-buffer write and the Android clipboard write.
- Viewport copy retains its existing normalization path. Pytest subset copy retains its existing selector and fail-closed behavior.
- Clipboard routing remains `tmux load-buffer -` plus `termux-clipboard-set`.

## Test evidence

Before the source change, the new executor-level RED check produced three expected failures against the prior implementation: CPY_ALL did not request flagged capture, included the current prompt instead of cutting it off, and overwrote the clipboard when a valid prompt boundary was absent.

After the implementation change, the local staged source/test slice passed:

```sh
pytest -q test_copy_entire_pane.py test_copy_executor.py test_pytest_clipboard.py
```

Observed: **23 passed**. This was a focused Python run against the changed module/test slice assembled from the inspected remote sources; it was not the repository's `./_test/run` harness, the complete test suite, or a Termux runtime test.

## Still not established

- The exact `capture-pane -pF -S -` output and final P boundary for the live CPY_ALL key action on the target Termux/tmux setup.
- End-to-end exact clipboard preservation from both root and Emacs-style `copy-mode`.
- Full repository regressions, fresh coverage after this change, or execution of `_docs/_continuity/check.sh`.

The feature remains PARTIAL until these are demonstrated. Run the project test harness and check the production macro with sentinels before changing the gate to DONE.

## Clipboard-path note

The native tmux `load-buffer -w` route remains an untested alternative, not an observed failure. tmux's terminal clipboard integration uses OSC 52 and depends on tmux's `set-clipboard` setting, terminal clipboard capability (`Ms`), and terminal support. See the [tmux clipboard guide](https://github.com/tmux/tmux/wiki/Clipboard). The existing `termux-clipboard-set` route remains the proven current path.
