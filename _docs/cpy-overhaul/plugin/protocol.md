# TKM Termux Host/Plugin Protocol

## Purpose

This protocol defines the boundary between:

1. the small TKM integration hook inside the Termux host process, and
2. the external TKM plugin/recorder process.

The host hook has access to `TerminalSession`.

The plugin does not.

The host hook therefore observes the existing TerminalSession and forwards
events and raw PTY output to the TKM plugin.

## Architecture

```text
Normal Bash
    │
    ▼
TerminalSession
    │
    │ raw PTY bytes
    ▼
TKM Host Hook
    │
    │ local IPC
    ▼
TKM Plugin
    │
    ├── Recorder
    ├── Record Store
    ├── gst
    ├── cpy
    └── clr
```

The host hook MUST NOT:

- replace Bash
- launch Bash
- create a replacement PTY
- redirect terminal output
- write terminal output to the user's stdout/stderr
- modify shell prompts
- execute recorder commands
- perform recorder persistence
- block the PTY reader thread on disk I/O

The host hook is strictly a transport bridge.

---

## Transport

Initial transport:

```text
Unix-domain socket
```

The transport is local-only.

The first implementation may use a filesystem Unix socket under the
Termux-private TKM runtime directory.

Future implementations may use an Android-passed file descriptor if that
becomes necessary for stronger process authentication or SELinux compatibility.

The transport MUST support a persistent connection for the lifetime of a
Termux session.

---

## Framing

Every message uses:

```text
uint32_be length
uint8[] payload
```

The payload begins with:

```text
uint8 message_type
```

Maximum payload size for the initial implementation:

```text
1 MiB
```

Raw output is therefore split into multiple OUTPUT messages when necessary.

The receiver MUST reassemble messages without assuming that one socket read
equals one protocol message.

---

## Message Types

```text
0x01 HELLO
0x02 SESSION_ATTACH
0x03 SESSION_DETACH
0x04 OUTPUT
0x05 SESSION_CHANGED
0x06 SESSION_CLOSED
0x07 PING
0x08 PONG
0x09 ERROR
```

---

## HELLO

Sent by the host immediately after connection.

Payload:

```text
message_type = 0x01

uint16 protocol_major
uint16 protocol_minor
uint32 host_capabilities
```

Initial capabilities:

```text
0x00000001 RAW_OUTPUT
0x00000002 SESSION_LIFECYCLE
```

---

## SESSION_ATTACH

Sent when the host begins observing a TerminalSession.

Payload:

```text
message_type = 0x02

uint16 handle_length
uint8[] session_handle

int32 shell_pid
```

`session_handle` is the TerminalSession handle.

The plugin treats the handle as opaque.

---

## OUTPUT

Carries raw bytes received from the PTY.

Payload:

```text
message_type = 0x04

uint16 handle_length
uint8[] session_handle

uint32 sequence
uint32 data_length
uint8[] data
```

`sequence` starts at zero for each attached session and increments by one for
each OUTPUT message.

The bytes in `data` are the exact bytes received from the PTY observer.

They MUST NOT be:

- decoded as UTF-8 by the host
- stripped
- normalized
- interpreted as ANSI
- line-buffered
- modified
- passed through a terminal emulator

The recorder owns interpretation.

---

## SESSION_DETACH

Sent when observation of a session ends but the session itself may continue
to exist.

Payload:

```text
message_type = 0x03

uint16 handle_length
uint8[] session_handle
```

---

## SESSION_CHANGED

Sent when Termux changes the currently displayed TerminalSession.

Payload:

```text
message_type = 0x05

uint16 handle_length
uint8[] session_handle
```

This is informational.

A session being displayed does not imply that the recorder should lose
observation of another still-running session.

---

## SESSION_CLOSED

Sent when the observed TerminalSession terminates.

Payload:

```text
message_type = 0x06

uint16 handle_length
uint8[] session_handle

int32 exit_status
```

---

## Ordering

For one session:

```text
SESSION_ATTACH
    ↓
OUTPUT*
    ↓
SESSION_DETACH
```

or:

```text
SESSION_ATTACH
    ↓
OUTPUT*
    ↓
SESSION_CLOSED
```

`OUTPUT` sequence numbers provide a diagnostic ordering check.

The recorder MUST NOT infer command boundaries from socket message boundaries.

---

## Backpressure

The PTY reader thread MUST NEVER synchronously wait for the plugin.

The host implementation therefore uses:

```text
PTY reader
    │
    ▼
bounded/in-memory queue
    │
    ▼
transport writer
    │
    ▼
Unix socket
```

If the transport becomes unavailable:

1. the host stops forwarding to the plugin;
2. the terminal continues normally;
3. the plugin may reconnect;
4. the host does not alter the user's shell.

The initial diagnostic implementation may use an unbounded queue only while
measuring throughput. Production implementation must establish an explicit
memory/backpressure policy.

---

## Security

The transport is not a generic public socket.

The production host must authenticate the peer before accepting a recorder
connection.

Preferred order:

1. same-UID verification where available;
2. Android package/signature verification where applicable;
3. authenticated FD transfer through an Android component;
4. filesystem permissions as defense-in-depth.

The protocol itself does not grant access to TerminalSession.

Only the Termux host hook has that access.

---

## Important distinction

This protocol transports:

```text
raw terminal output
```

It does NOT transport:

```text
command boundaries
```

Command detection remains a separate TKM mechanism.

Therefore:

```text
raw PTY stream
       +
native Bash command-boundary events
       +
session lifecycle
       ↓
TKM Recorder
```

This separation is intentional.

---

## Capture guarantees

Two capture levels remain distinct:

### BUFFER_CAPTURE

Reads the current TerminalBuffer/transcript.

It is limited by terminal scrollback.

### STREAM_CAPTURE

Observes raw PTY output before it enters the TerminalBuffer.

This is the preferred mechanism for complete output capture.

The protocol's OUTPUT messages implement STREAM_CAPTURE.

---

## Non-interference invariant

The following must remain true:

```text
User's Bash
     │
     ▼
TerminalSession
     │
     ├──► Terminal emulator
     │
     └──► TKM observer
             │
             ▼
         async transport
```

TKM is a passive observer.

If TKM crashes:

```text
Bash continues.
Termux continues.
Terminal output continues.
```

