# TKM: Primer

**Project:** Termux Key Manager  
**Repository:** `FocusTorn/termux-key-manager`

> **Read this first when entering the repository in a new AI coding session.**

This document is the entry point for understanding TKM before changing code.

TKM is a **native Termux terminal sidecar**. It observes terminal activity and provides command/output capture and copy workflows without becoming the shell, replacing Bash, or inserting itself into the PTY execution path.

---

## 1. What TKM Is

TKM extends a normal Termux terminal session with structured capture and copy operations.

The fundamental execution model is:

```text
Normal Termux Bash
       │
       │ command execution
       ▼
TerminalSession / PTY
       │
       │ terminal output
       ▼
Termux host hook
       │
       │ transport only
       ▼
Unix socket
       │
       ▼
TKM recorder / sidecar
       │
       ▼
records + copy/query operations
```

**Bash remains the source of command execution.**

TKM observes terminal activity. It does not become the command interpreter.

---

## 2. What TKM Is Not

These boundaries are architectural requirements, not implementation preferences.

TKM must **not**:

- launch an interactive replacement shell
- become a child PTY process
- replace or wrap the user's Bash process
- redirect the terminal's output stream
- modify the user's shell prompt
- automatically launch from `.bashrc`
- block the terminal's PTY reader
- persist terminal output from the host hook itself
- require a TKM-specific shell prompt
- depend on `[TMK] $` as a production interface

The legacy `[TMK] $` behavior may exist in historical or testing code, but it is not the target architecture.

---

## 3. Core Architecture

The host-side hook has one responsibility:

**bridge terminal data to TKM.**

It should not acquire ownership of the terminal.

The intended separation is:

```text
Termux terminal
     │
     ├── Bash owns command execution
     │
     └── host hook observes/captures terminal data
                    │
                    ▼
              Unix socket
                    │
                    ▼
              TKM sidecar
                    │
                    ├── protocol
                    ├── recorder
                    └── record storage
```

This separation is important because TKM must remain independent of the mechanism that actually executes commands.

---

## 4. Transport Protocol

The native sidecar communicates through a local Unix socket.

Messages use:

```text
4-byte length
4-byte/type protocol framing
payload
```

The protocol has a **1 MiB message limit**.

Important message concepts include:

- `HELLO`
- `SESSION_ATTACH`
- `OUTPUT`
- additional session/control messages as defined by the protocol specification

### OUTPUT

`OUTPUT` carries **raw terminal bytes**.

Do not turn terminal output into shell commands, prompt text, or reconstructed semantic output at the transport layer.

Raw bytes are the source material from which higher-level capture behavior can be built.

---

## 5. Capture Model

TKM distinguishes between two capture sources:

```text
BUFFER_CAPTURE
STREAM_CAPTURE
```

### BUFFER_CAPTURE

Represents terminal-buffer capture.

### STREAM_CAPTURE

Represents raw terminal-stream capture.

The distinction matters. Terminal history and terminal output are not interchangeable.

In particular:

**shell history does not provide terminal output.**

A command recorded by Bash history is not evidence of what the terminal displayed.

---

## 6. Record Model

The core TKM record is:

```text
record_id
command
output
state
```

`state` is one of:

```text
open
closed
```

Conceptually:

```text
command starts
      │
      ▼
  record=open
      │
      │ output arrives
      ▼
 output accumulated
      │
      ▼
 command/session completion
      │
      ▼
 record=closed
```

The recorder must preserve the relationship between a command and the output produced by that command without taking ownership of command execution.

---

## 7. User-Facing Operations

The intended command families include:

```text
gst all
gst out
gst rec

cpy out
cpy rec
cpy all

clr
```

Where appropriate:

- `gst` retrieves/inspects captured state
- `cpy` copies captured content
- `clr` clears captured state

The exact implementation may evolve, but these operations should remain consumers of the capture/recording architecture rather than becoming a second shell system.

---

## 8. Installer Architecture

TKM is moving toward a **safe installer architecture**.

The installer must distinguish between:

```text
generated configuration
        │
        ▼
staging / validation
        │
        ▼
explicit installation
        │
        ▼
live Termux configuration
```

TKM should not blindly overwrite live user configuration as a side effect of ordinary development or testing.

Important live locations include:

```text
~/.termux/termux.properties
~/.termux/helpers.sh
```

The installer work exists to make changes to these locations deliberate, inspectable, and recoverable.

---

## 9. Authoritative Sources

When resolving a question about behavior, use the most authoritative TKM source available.

Priority should generally be:

```text
current specification / architecture docs
        ↓
tests describing required behavior
        ↓
current implementation
        ↓
historical / legacy implementation
```

The source of truth for the generated keyboard/macros configuration remains:

```text
macros.jsonc
```

Do not infer the intended architecture from legacy shell or PTY experiments when current architecture documentation says otherwise.

---

## 10. Important Project Documentation

The `_docs` tree is the architectural documentation area.

The copy/recording overhaul is documented under:

```text
_docs/cpy-overhaul/
```

Relevant areas include:

```text
_docs/cpy-overhaul/spec.md
_docs/cpy-overhaul/roadmap.md
_docs/cpy-overhaul/plugin/protocol.md
```

These documents describe the capture architecture, roadmap, and native protocol in greater detail.

The primer is the entry point. Detailed implementation decisions belong in the appropriate specification or roadmap document rather than being duplicated here.

---

## 11. Development Rules

Before changing TKM:

1. Read this primer.
2. Identify the authoritative specification for the behavior being changed.
3. Inspect the current implementation and tests.
4. Make the smallest change that satisfies the requirement.
5. Run the relevant tests.
6. Verify behavior directly when tests cannot cover the integration boundary.
7. Do not declare success without evidence.

For architectural changes, update the relevant documentation alongside the implementation.

---

## 12. Testing Philosophy

TKM has several layers that should be tested independently:

```text
protocol
   ↓
transport
   ↓
capture
   ↓
recording
   ↓
user operations
   ↓
installer / live integration
```

A passing unit test does not by itself prove that the Termux host integration works.

Likewise, a manual terminal observation does not replace deterministic tests for protocol and record behavior.

Use both where appropriate.

---

## 13. Legacy Code

TKM contains historical experiments involving:

- interactive shells
- PTY children
- shell traps
- launcher scripts
- tmux-based capture
- prompt-based behavior

These are useful as historical evidence and fallback mechanisms.

They are **not automatically the target architecture**.

In particular:

```text
tmux
```

is a fallback, not the native target.

The native target is:

```text
Termux host terminal
        ↓
host hook
        ↓
Unix socket
        ↓
TKM sidecar
```

When legacy code conflicts with the current architecture, follow the current specification.

---

## 14. Critical Architectural Invariants

These invariants should survive implementation changes:

### Bash owns execution

TKM observes commands and output. Bash remains responsible for executing commands.

### The host hook is transport-only

The hook bridges terminal data. It does not become a recorder, shell, or persistent storage layer.

### OUTPUT remains raw

The transport layer must not reinterpret raw terminal output into higher-level semantics.

### TKM is a sidecar

The terminal must remain usable if TKM is absent or stopped.

### No `.bashrc` auto-launch

Normal shell startup must not require TKM to start.

### No PTY ownership

TKM must not insert itself as the user's command shell or PTY child.

### Native capture is primary

The host-hook/socket architecture is the target. tmux and older shell mechanisms are fallback or historical paths.

---

## 15. Agent Starting Procedure

When beginning work in a fresh TKM session:

```text
1. Read _docs/primer.md
2. Find the relevant specification
3. Inspect current implementation
4. Inspect relevant tests
5. Make the smallest correct change
6. Run verification
7. Report concrete evidence
```

Do not begin by rebuilding an understanding from historical conversation context when the repository documentation contains the current architectural decision.

---

## 16. Current Direction

TKM is being consolidated around a native terminal-sidecar architecture.

The destination is:

```text
                ┌─────────────────────┐
                │   Termux Terminal   │
                │                     │
                │   Bash executes     │
                └──────────┬──────────┘
                           │
                    terminal activity
                           │
                           ▼
                ┌─────────────────────┐
                │     Host Hook       │
                │                     │
                │ transport bridge    │
                └──────────┬──────────┘
                           │
                       Unix socket
                           │
                           ▼
                ┌─────────────────────┐
                │    TKM Sidecar      │
                │                     │
                │ protocol            │
                │ recorder            │
                │ records             │
                │ copy/query          │
                └─────────────────────┘
```

Everything else should be evaluated against that destination.

**If an implementation makes TKM more like a shell, a PTY owner, a prompt wrapper, or an automatically launched terminal process, it is moving in the wrong architectural direction.**
