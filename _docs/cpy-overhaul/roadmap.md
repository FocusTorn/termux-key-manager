# TKM — Native Terminal Recorder Roadmap v2

## Goal

Replace the current `cpy_all`/tmux-dependent approach with a native-terminal
recording system that works from the user's normal Termux Bash session.

TKM must operate as a sidecar to the existing shell.

The end state is:

    Native Bash
        │
        ├── command boundary detection
        │
        ├── terminal/output observation
        │
        ▼
    TKM Recorder
        │
        ├── records
        ├── current/open record
        └── capture backend
             ├── native terminal
             └── tmux fallback
        │
        ▼
    gst / cpy / clr

The user's Bash remains the shell.

TKM never becomes the shell.

---

# Stage 0 — Lock Down the Architecture

## Objectives

- Keep the user's normal Bash shell completely untouched.
- Do NOT automatically launch `tkm-launcher.py` from `.bashrc`.
- Do NOT use a PTY child shell as the normal architecture.
- Do NOT replace or wrap the user's interactive Bash.
- Keep `[TMK] $` only for legacy/testing code if needed.
- Treat `cpy_all` as the existing tmux proof of concept.
- Establish a backend-independent recorder architecture.

## Hard Architecture Invariant

TKM MUST NEVER become the user's interactive shell.

The user's existing/standard Bash is the only working shell.

TKM is a non-hijacking sidecar whose sole job is to observe/capture
that shell's terminal I/O and persist the session.

Therefore:

    Termux
      │
      └── normal Bash
             │
             └── TKM sidecar

NOT:

    Termux
      │
      └── TKM
             │
             └── replacement Bash

## Exit Criteria

Running:

    bash
    tmux
    tmux new

must produce normal shell behavior.

---

# Stage 1 — Define the Record Model

Create the internal command/output record model.

Each record contains:

    record_id
    command
    output
    state

Where:

    state = open | closed

Example:

    Record 1
      command = "ls -la"
      output  = "..."
      state   = closed

    Record 2
      command = "echo hello"
      output  = "hello\n"
      state   = open

## Record Framing

The command boundary provides the framing event.

Output does not require an explicit output-end marker.

Conceptually:

    command A
    output A
    command B
    output B

The beginning of command B closes the output region belonging to
command A.

## Exit Criteria

The recorder can represent:

    command + completed output
    command + currently accumulating output

without requiring an output-end marker.

---

# Stage 2 — Native Command Boundary Detection

Determine the most reliable way for native Bash to notify TKM of
command boundaries.

Investigate:

- Bash history
- `PROMPT_COMMAND`
- `DEBUG` trap
- Bash command hooks
- history state
- existing TKM helper instrumentation

## Required Property

The command must execute in the user's actual Bash session.

TKM must not create a second interactive shell.

For:

    $ ls
    file1
    file2
    $ echo hello
    hello
    $

TKM should identify:

    Record 1 → ls
    Record 2 → echo hello

without changing the visible terminal experience.

## Exit Criteria

A native Bash session can reliably generate command-boundary events.

---

# Stage 3 — Native Terminal Capture Research

This is the critical architecture stage.

The question is:

    How can TKM obtain the terminal data associated with the user's
    real Bash session without replacing or hijacking that session?

Command detection and terminal capture are separate problems.

We already have evidence that Termux itself can access its native terminal
buffer.

Termux exposes the conceptual path:

    TerminalSession
        ↓
    TerminalEmulator
        ↓
    TerminalBuffer
        ↓
    transcript text

Termux already uses this mechanism for operations such as sharing the
terminal transcript.

## Important Discovery

The native Termux terminal buffer is not the same thing as the raw shell
output stream.

Terminal-buffer capture can only provide data still retained by the
terminal buffer.

Therefore:

    terminal-buffer capture
        ≠
    guaranteed complete raw output capture

This distinction must remain explicit throughout the project.

---

# Stage 3A — Native TerminalBuffer Capture

Investigate the existing Termux transcript mechanism.

Relevant conceptual API:

    getTerminalSessionTranscriptText(...)

The native terminal buffer can provide:

- visible terminal contents
- retained scrollback
- transcript text
- terminal state represented by the emulator

## Known Limitation

The terminal buffer is finite.

The default transcript size is limited, although Termux supports a larger
maximum.

Therefore a command producing more output than the retained buffer may
lose its earliest output before TKM captures it.

## Purpose

Determine whether TerminalBuffer capture is sufficient for the initial
TKM recorder.

## Exit Criteria

A reproducible external mechanism can obtain the current native terminal
transcript without creating or replacing a shell.

---

# Stage 3B — Native Terminal I/O Investigation

Investigate the lower-level path:

    Bash process
        ↓
    TerminalSession
        ↓
    terminal I/O
        ↓
    TerminalEmulator
        ↓
    TerminalBuffer

The goal is to determine whether TKM can observe terminal output before
it is reduced to finite scrollback.

## Required Property

Observation must be passive.

It must not:

- replace the shell
- proxy the PTY
- redirect stdout/stderr
- change the user's prompt
- require a replacement Bash
- require the user to work inside a TKM shell

## Desired Capability

Ideally TKM can observe the terminal's incoming data stream and maintain
its own output record independently of terminal scrollback.

This would allow:

    very large output
    streaming output
    output exceeding terminal scrollback

to remain recordable.

## Exit Criteria

Either:

1. A passive native I/O observation point is found, or
2. The investigation conclusively establishes that only terminal-buffer
   capture is available.

---

# Stage 3C — Large-Output Validation

Regardless of which native mechanism is selected, test its limits.

Required tests include:

    10 lines
    100 lines
    1,000 lines
    10,000 lines
    output larger than terminal scrollback
    continuously streaming output
    rapid output followed immediately by another command

Also test:

- ANSI escape sequences
- cursor movement
- progress indicators
- carriage returns
- terminal clearing
- terminal reset
- alternate screen behavior
- Ctrl-C

## Required Result

The implementation must explicitly document whether it provides:

    BUFFER_COMPLETE

or:

    STREAM_COMPLETE

or:

    BEST_EFFORT

Do not describe bounded terminal-buffer capture as arbitrary complete
output capture.

---

# Stage 3D — External Termux Bridge

Investigate the smallest possible bridge between a TKM companion and the
running Termux process.

Desired architecture:

    TKM
      │
      │ request
      ▼
    TermuxActivity
      │
      ▼
    current TerminalSession
      │
      ▼
    native terminal data

The bridge must operate on the existing terminal session.

It must NOT:

- create another shell
- create another interactive session
- replace Bash
- launch a PTY proxy
- redirect shell output

## Candidate Boundary

TermuxActivity is an exported activity using a single-task launch model.

This makes an intent-based bridge a viable investigation target.

The bridge should expose only the minimum functionality required by TKM.

Conceptually:

    captureCurrentTranscript()
    captureSessionTranscript(sessionHandle)

The exact API is not fixed.

## Exit Criteria

A minimal bridge can communicate with the already-running Termux terminal
without altering normal shell execution.

---

# Stage 3E — Select the Native Capture Strategy

Compare the discovered mechanisms.

Candidate A:

    TerminalBuffer transcript

Candidate B:

    passive terminal I/O observation

Candidate C:

    another native Termux extension boundary

Candidate D:

    shell-side mechanism

Candidate E:

    tmux fallback

Select the least invasive mechanism that satisfies the required
recording guarantees.

The decision must explicitly document:

- completeness
- latency
- large-output behavior
- terminal-state behavior
- security implications
- maintenance cost
- dependence on Termux internals

---

# Stage 4 — Build the Capture Backend Interface

Define:

    CaptureBackend

Conceptual methods:

    available()
    capture_current()
    capture_since(...)
    reset()

Potential implementations:

    NativeTerminalBackend
    TmuxBackend

The recorder must not contain tmux-specific logic.

The recorder asks the backend for terminal information.

## Important Extension

If stream capture is discovered, the backend may additionally expose a
passive event/stream interface.

For example:

    start_observing()
    stop_observing()

The exact interface should be determined by the selected mechanism rather
than prematurely hard-coding it.

## Exit Criteria

The recorder can obtain terminal data without knowing whether the source
is native Termux or tmux.

---

# Stage 5 — Build the Recorder Engine

Implement the recorder state machine.

Responsibilities:

- receive command-boundary events
- associate command with terminal/output data
- maintain the current/open record
- close the previous record when a new command starts
- persist records
- reset active state
- expose records to consumers

## State Model

    START_COMMAND
          │
          ▼
    finalize previous record
          │
          ▼
    create current record
          │
          ▼
    accumulate/capture output
          │
          ▼
    next START_COMMAND
          │
          ▼
    close previous record
    create next record

There is intentionally no `OUTPUT_END` requirement.

## Exit Criteria

The recorder works independently of `cpy`, `gst`, and the terminal
capture implementation.

---

# Stage 6 — Implement `gst`

`gst` becomes the read/query interface to recorder state.

Initial commands:

    gst all
    gst out
    gst rec

Definitions:

    gst all
        All currently retained recorder data.

    gst out
        Output from the most recent record.

    gst rec
        Most recent command plus its output.

## Exit Criteria

`gst` reads recorder state rather than directly depending on tmux.

---

# Stage 7 — Replace `cpy_all` With `cpy`

`cpy` becomes the consumer/orchestration interface.

Initial commands:

    cpy
    cpy out
    cpy rec
    cpy all

Responsibilities:

1. synchronize if required
2. select recorder data
3. invoke capture if required
4. write clipboard content
5. perform cleanup
6. return immediately to native Bash

`cpy` is NOT the recorder.

---

# Stage 8 — Clipboard Synchronization

If the final native capture mechanism requires synchronization with Bash
history or command boundaries, isolate that mechanism here.

Test:

- normal commands
- empty output
- multiline output
- quotes
- pipes
- `&`
- redirects
- failed commands
- large output
- repeated `cpy`
- immediate `cpy`
- `cpy` after a command with no output

Temporary synchronization data must never contaminate requested
clipboard content.

---

# Stage 9 — `clr`

`clr` resets both terminal context and recording context.

Required:

    clr
      ├── clear terminal
      ├── reset recorder
      ├── discard records
      ├── discard current output
      └── reset capture state

After:

    clr

the next command begins a new logical recording context.

---

# Stage 10 — tmux Compatibility

tmux remains supported as a backend.

Architecture:

    Recorder
        │
        ▼
    CaptureBackend
       ├── Native
       └── tmux

The existing `cpy_all` behavior remains the known-good tmux capture
implementation during development.

Eventually:

    cpy_all → cpy all

may become a compatibility alias.

tmux is compatibility infrastructure, not the target architecture.

---

# Stage 11 — Remove Legacy PTY Architecture

Only after native recording is proven.

Candidates:

- automatic TKM launcher
- PTY shell replacement
- `[TMK] $`
- PTY marker assumptions
- unnecessary PTY proxy code

`pty_recorder.py` may be retained as a diagnostic/testing backend if it
provides useful automated test coverage.

Do not remove useful test infrastructure merely because it is unsuitable
for production recording.

---

# Stage 12 — Expand the Query Language

Expand:

    gst all
    gst out
    gst rec

toward:

    gst all out
    gst all cmd
    gst rec 2
    gst rec 2,4
    gst out 2
    gst cmd 2

And:

    cpy
    cpy out
    cpy rec
    cpy all
    cpy rec 2,4
    cpy out 2

The parser should be data-driven.

---

# Stage 13 — Stress Testing and Validation

Before declaring the native recorder complete, validate:

- normal Bash
- tmux
- no tmux
- empty output
- multiline output
- failed commands
- very long commands
- very large output
- streaming output
- ANSI output
- terminal resize
- terminal reset
- Ctrl-C
- rapid commands
- repeated `gst`
- repeated `cpy`
- `clr`
- terminal scrollback eviction
- user scrolling
- session switching
- Termux Activity recreation

## Non-Interference Test

The user must be able to continue using Bash normally if TKM's capture
mechanism fails.

A recorder failure must never become a shell failure.

---

# Final Architecture

    ┌──────────────────────────────┐
    │       Native Termux Bash     │
    │                              │
    │  $ command                   │
    │  output                      │
    │  $ command                   │
    │  output                      │
    └──────────────┬───────────────┘
                   │
             command events
                   │
                   ▼
    ┌──────────────────────────────┐
    │       TKM Recorder           │
    │                              │
    │  Record 1                    │
    │    command                   │
    │    output                    │
    │                              │
    │  Record 2                    │
    │    command                   │
    │    output...                 │
    └──────────────┬───────────────┘
                   │
             CaptureBackend
              ┌────┴────┐
              ▼         ▼
          Native       tmux
          terminal     backend
              │
              ▼
       ┌─────────────────┐
       │ cpy / gst / clr │
       └─────────────────┘

The native terminal path is primary.

tmux is compatibility/fallback infrastructure.

---

# Success Condition

The user can open Termux normally and see only:

    $ command
    output
    $ command
    output

while TKM silently maintains structured command/output records.

The user can then use:

    gst all
    gst out
    gst rec

    cpy
    cpy out
    cpy rec
    cpy all

    clr

without requiring tmux.

The user's shell remains the source of truth for command execution.

No TKM shell exists in the final architecture.
