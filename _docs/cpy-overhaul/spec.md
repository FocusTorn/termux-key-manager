# TKM — Native Terminal Recorder Specification v2

## 1. Purpose

TKM provides command/output recording and retrieval from a normal native
Termux Bash session.

TKM operates alongside the user's shell.

It must never replace the user's shell.

The terminal experience remains:

    $ command
    output
    $ command
    output

TKM is a non-hijacking sidecar.

---

# 2. Architecture Invariant

TKM MUST NEVER become the user's interactive shell.

The user's existing Bash is the only working shell.

Required architecture:

    Normal Termux
        │
        └── Bash
             │
             └── TKM sidecar

Forbidden architecture:

    Termux
        │
        └── TKM launcher
             │
             └── replacement Bash

TKM must not:

- replace Bash
- `exec()` over Bash
- launch a replacement interactive Bash
- proxy the user's PTY
- redirect the user's stdout/stderr
- modify the visible prompt to `[TMK] $`
- require tmux
- require the user to work inside a TKM shell

---

# 3. Core Concept

Bash naturally knows about commands.

Bash history does not naturally provide terminal-output boundaries.

TKM therefore uses command boundaries as the primary framing mechanism.

Conceptually:

    START_COMMAND
    command
    COMMAND_END
    output...
    START_COMMAND
    command
    COMMAND_END
    output...

These markers are conceptual.

They must not be visibly emitted into the user's terminal.

---

# 4. Record Framing

A record consists of:

    command
    output

The command is explicitly bounded by command events.

The output is implicitly bounded.

For records N and N+1:

    command_N
    output_N
    command_N+1
    output_N+1

The start of command N+1 closes the output region associated with
command N.

There is intentionally no required `OUTPUT_END` marker.

---

# 5. Record Object

Logical representation:

    Record {
        id
        command
        output
        state
    }

Where:

    id
        Sequential record identifier.

    command
        Command associated with the record.

    output
        Captured terminal/output data associated with the command.

    state
        open | closed

Example:

    {
        "id": 7,
        "command": "git status",
        "output": "...",
        "state": "closed"
    }

---

# 6. Open Record

The latest command has an open output region.

Example:

    Record 1
      command = ls
      output = file1
               file2
      state = closed

    Record 2
      command = echo hello
      output = hello
      state = open

Record 2 remains open until:

- another command begins
- `clr` resets the recorder
- the recording session ends

The recorder must not require an output-end marker.

---

# 7. Command Detection

Command detection occurs in the user's native Bash session.

Candidate mechanisms include:

- Bash history
- `PROMPT_COMMAND`
- DEBUG trap
- Bash command hooks
- existing TKM helper instrumentation

The selected mechanism must minimize interference with Bash.

The user's actual command must remain the command that executes.

TKM must not create a child interactive shell for command detection.

---

# 8. Terminal Capture

Terminal capture is independent from command detection.

The recorder needs terminal/output information associated with command
boundaries.

Conceptually:

    capture(A)
    capture(B)

allows TKM to determine the terminal data associated with:

    A → B

The exact mechanism is backend-specific.

---

# 9. Native Termux Terminal Model

Termux internally represents the native terminal through a chain
conceptually equivalent to:

    TerminalSession
        ↓
    TerminalEmulator
        ↓
    TerminalBuffer
        ↓
    transcript

The terminal buffer can expose transcript text.

This establishes a viable native terminal capture mechanism.

However, the terminal buffer is finite.

Therefore:

    terminal transcript
        ≠
    guaranteed complete raw command output

when output exceeds the retained terminal buffer.

---

# 10. Capture Guarantees

TKM must explicitly distinguish capture modes.

## BUFFER_COMPLETE

Means all relevant data still retained by the native terminal buffer was
captured.

It does NOT mean all bytes ever produced by the command.

---

## STREAM_COMPLETE

Means TKM observed the terminal output stream before data could be lost
through terminal-buffer eviction.

This is the preferred guarantee for arbitrary output.

---

## BEST_EFFORT

Means TKM captured the available terminal representation but cannot
guarantee completeness.

The implementation must document which guarantee the active backend
provides.

---

# 11. Native Terminal Backend

The native backend is the primary target.

Requirements:

- no tmux
- no PTY replacement
- no replacement Bash
- no visible prompt changes
- no visible markers
- no user interaction required to maintain recording

The native backend may use Android/Termux APIs internally.

Those implementation details must remain isolated from the recorder.

---

# 12. TerminalBuffer Capture

The first native mechanism to evaluate is Termux's existing terminal
transcript functionality.

Conceptually:

    current TerminalSession
          ↓
    TerminalEmulator
          ↓
    TerminalBuffer
          ↓
    transcript text

Advantages:

- native terminal state
- no PTY replacement
- no child shell
- no tmux requirement
- uses Termux's own terminal representation

Limitation:

- terminal-buffer capacity is finite
- old output may be evicted
- very large output may therefore become incomplete

TerminalBuffer capture must not be represented as arbitrary-size
complete output.

---

# 13. Native Terminal I/O Observation

The preferred investigation target is the lower-level terminal I/O path.

Conceptually:

    Bash process
        ↓
    TerminalSession
        ↓
    terminal I/O
        ↓
    TerminalEmulator
        ↓
    TerminalBuffer

The goal is to determine whether TKM can passively observe incoming
terminal data before terminal-buffer eviction.

A successful implementation would allow TKM to retain output independently
of terminal scrollback capacity.

The observer must not alter the normal I/O path.

---

# 14. External Termux Bridge

If Android process boundaries prevent direct access to the existing
TerminalSession, TKM may use a minimal Termux-side bridge.

Desired architecture:

    TKM companion
          │
          │ request
          ▼
    TermuxActivity
          │
          ▼
    current TerminalSession
          │
          ▼
    native terminal

The bridge must operate against the existing terminal session.

It must not create a new terminal session.

It must not execute a replacement shell.

It must not become a PTY proxy.

---

# 15. Bridge Responsibilities

The bridge should expose the smallest API necessary.

Possible conceptual operations:

    getCurrentSession()
    getCurrentTranscript()
    getSessionTranscript(sessionHandle)

If stream observation is possible, the bridge may instead expose a
controlled observation interface.

The API is intentionally not fixed until the Termux source investigation
determines the smallest stable integration point.

---

# 16. Accessibility

Accessibility/Android UI inspection is NOT the primary recorder backend.

Accessibility can expose the currently rendered TerminalView content.

That is useful for:

- diagnostics
- visible-terminal operations
- possible `cpy vis`

It is not sufficient for reliable complete recording because:

- only the current viewport may be exposed
- scrollback can be outside the viewport
- fast output can scroll past before observation
- user scrolling changes the observed viewport
- ANSI cursor movement can alter the visible representation

Therefore Accessibility must not be treated as the authoritative recorder
source.

---

# 17. Capture Backend Interface

TKM uses a backend abstraction.

Conceptual interface:

    CaptureBackend

Methods:

    available()
    capture_current()
    capture_since(...)
    reset()

Potential implementations:

    NativeTerminalBackend
    TmuxBackend

If the selected native implementation requires streaming observation,
the abstraction may additionally provide:

    start_observing()
    stop_observing()

The final interface should follow the actual native mechanism rather than
prematurely constraining it.

---

# 18. Recorder Responsibilities

The recorder owns command/output state.

It is responsible for:

1. receiving command events
2. associating command data with records
3. obtaining terminal/output data
4. maintaining the current record
5. closing the previous record
6. persisting records
7. exposing records to consumers
8. resetting active state

The recorder does not know whether capture came from native Termux or
tmux.

---

# 19. Recorder State Machine

## START_COMMAND

Input:

    command

Action:

1. finalize the previous open record
2. capture/calculate its final output
3. create a new record
4. assign the command
5. mark the new record open

---

## COMMAND_END

Input:

    command/status metadata as available

Action:

1. finalize command metadata
2. leave the output region open
3. continue observing/capturing output

`COMMAND_END` does not close the output record.

---

## RESET

Action:

1. discard active records
2. discard current open record
3. reset capture state
4. reset session recording state
5. reset TKM panel state

---

# 20. Large Output

Large output is a first-class requirement.

The recorder must be tested against:

- 10 lines
- 100 lines
- 1,000 lines
- 10,000 lines
- output exceeding terminal scrollback
- continuously streaming output
- rapid output followed by another command

Also test:

- ANSI sequences
- cursor movement
- carriage returns
- progress bars
- screen clearing
- terminal reset
- alternate screen
- Ctrl-C

The implementation must state whether its guarantee is:

    BUFFER_COMPLETE
    STREAM_COMPLETE
    BEST_EFFORT

---

# 21. `gst`

`gst` is read-only.

It consumes recorder state.

Initial commands:

    gst all
    gst out
    gst rec

Definitions:

    gst all
        All active recorder data.

    gst out
        Output from the most recent record.

    gst rec
        Most recent command plus output.

`gst` must not implement its own recording logic.

---

# 22. Future `gst` Grammar

The parser should support:

    gst all
    gst out
    gst rec

    gst all out
    gst all cmd

    gst rec 2
    gst rec 2,4
    gst out 2
    gst cmd 2

The grammar must be composable and data-driven.

---

# 23. `cpy`

`cpy` is the primary consumer/orchestrator.

Initial commands:

    cpy
    cpy out
    cpy rec
    cpy all

`cpy` may coordinate:

1. synchronization
2. recorder access
3. terminal capture
4. record selection
5. output selection
6. clipboard writing
7. cleanup

`cpy` does not own persistent recording state.

---

# 24. `cpy` / History Synchronization

If the selected capture architecture requires synchronization with Bash
history or command boundaries, that synchronization must be isolated.

Temporary synchronization information must never contaminate the user's
requested clipboard result.

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

---

# 25. `clr`

`clr` resets both terminal and recorder state.

Required conceptual behavior:

    clr
      ├── clear terminal
      ├── reset recorder
      ├── discard records
      ├── discard current output
      └── reset capture state

After `clr`:

    gst all

must return an empty/new recording context.

---

# 26. Persistence

Recorder persistence is separate from active recorder state.

Possible structure:

    ~/.termux/tmk-session/
        records/
            1
            1.cmd
            2
            2.cmd

The exact representation may evolve.

The active in-memory recorder remains authoritative during a live
recording session.

---

# 27. Session Semantics

A recording session begins when TKM recording becomes active.

A session may contain:

    Record 1
    Record 2
    Record 3
    ...

`clr` starts a new logical recording context.

Records must not accidentally leak between unrelated Termux sessions.

---

# 28. Error Handling

The recorder must tolerate:

- no output
- multiline output
- multiline commands
- failed commands
- non-zero exit status
- pipes
- `&`
- redirects
- quotes
- very large output
- streaming output
- rapid commands
- repeated `cpy`
- repeated `gst`
- terminal resize
- terminal reset
- terminal scrolling
- tmux attach/detach
- `clr`
- Termux Activity recreation

Most importantly:

    recorder failure != shell failure

If recording fails, Bash must continue operating normally.

---

# 29. Non-Interference Requirement

This section is mandatory.

TKM must NOT:

- replace Bash
- launch a replacement interactive Bash
- modify the normal prompt
- emit visible recorder markers
- require `[TMK] $`
- require tmux
- proxy the user's PTY
- redirect stdout/stderr merely to capture output
- interfere with command execution
- require the user to work inside a TKM shell

The user's shell remains the source of truth.

---

# 30. Rejected Architectures

The following mechanisms have been experimentally investigated and are
not acceptable as the final recorder architecture.

## PTY Replacement

A PTY recorder can successfully capture command/output data, but it
requires TKM to become the parent/transport layer of the user's shell.

This violates the architecture invariant.

It may remain useful as a testing/diagnostic backend.

---

## TKM Child Bash

Launching Bash under TKM creates a replacement shell.

Rejected.

---

## Automatic `.bashrc` Launcher

Automatically starting the TKM PTY architecture from `.bashrc` causes TKM
to intercept the user's shell lifecycle.

Rejected.

---

## Accessibility Viewport Scraping

Accessibility can expose visible TerminalView text.

It cannot reliably capture arbitrary terminal scrollback or fast output.

Rejected as the authoritative recorder backend.

It may remain useful for diagnostics or visible-screen operations.

---

## Termux RUN_COMMAND

RUN_COMMAND is useful for executing commands in Termux, but it is not a
mechanism for observing the user's already-running interactive Bash
session.

Rejected as the recorder transport.

---

# 31. One Recorder, Multiple Consumers

There must be exactly one conceptual source of command/output state.

    Recorder
       │
       ├── gst
       ├── cpy
       └── future consumers

Do not duplicate recording logic inside:

    gst
    cpy
    cpy_all

---

# 32. One Capture Abstraction

Terminal capture must be isolated behind the backend boundary.

Do not scatter:

    tmux capture-pane

or native Termux capture code throughout TKM.

All terminal capture belongs to the capture backend.

---

# 33. Native First

The native terminal backend is the target architecture.

tmux is compatibility/fallback infrastructure.

The existing tmux implementation is valuable because it gives TKM a
known-good capture backend against which recorder behavior can be tested.

It does not define the native architecture.

---

# 34. Definition of Done

The redesign is complete when the user can:

1. Open Termux normally.
2. Use the normal Bash shell.
3. Run commands normally.
4. Produce ordinary and very large terminal output.
5. Have TKM silently associate commands with output.
6. Run:

       gst out

   and receive the latest output.

7. Run:

       gst rec

   and receive the latest command plus output.

8. Run:

       gst all

   and receive the active recording.

9. Run:

       cpy

   and copy the appropriate recorder data.

10. Run:

       clr

    and reset the recording context.

11. Perform all of the above without tmux.

12. Continue using tmux through the tmux backend.

13. Survive recorder/capture failure without interrupting Bash.

14. Pass large-output and streaming-output validation appropriate to the
    selected capture guarantee.

The terminal must still look and behave like an ordinary Termux Bash
session.

No replacement shell exists in the final architecture.
