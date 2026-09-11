#!/usr/bin/env python3
"""
TMK PTY session recorder.

The recorder owns a PTY master and runs an interactive Bash child.
Bash emits invisible DCS markers describing command boundaries.
The PTY stream remains untouched from Bash's point of view.

Record format:

    <records>/<id>       terminal output for the command
    <records>/<id>.cmd   command/simple-command aggregation

No shell stdout/stderr redirection is performed.
"""

from __future__ import annotations

import argparse
import base64
import os
import pty
import select
import signal
import struct
import sys
import termios
import time
import tty
from pathlib import Path


DCS_START = b"\x1bP"
DCS_END = b"\x1b\\"

TMK_START = b"TMK_START:"
TMK_END = b"TMK_END:"


def decode_payload(value: bytes) -> str:
    return base64.b64decode(value).decode(
        "utf-8",
        "replace",
    )


def terminal_size(fd: int) -> tuple[int, int]:
    try:
        size = os.get_terminal_size(fd)
        return size.lines, size.columns
    except OSError:
        return 24, 80


def set_winsize(
    fd: int,
    rows: int,
    cols: int,
) -> None:
    import fcntl

    fcntl.ioctl(
        fd,
        termios.TIOCSWINSZ,
        struct.pack(
            "HHHH",
            rows,
            cols,
            0,
            0,
        ),
    )


class Recorder:
    def __init__(self, records_dir: Path):
        self.records_dir = records_dir
        self.records_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.marker_buffer = bytearray()

        self.active_id: int | None = None
        self.active_command = ""
        self.active_output = bytearray()

        self.next_id = self._find_next_id()
        self.session_ids: dict[int, int] = {}

    def _find_next_id(self) -> int:
        ids = []

        for path in self.records_dir.iterdir():
            if not path.is_file():
                continue

            if path.name.endswith(".cmd"):
                continue

            try:
                ids.append(int(path.name))
            except ValueError:
                continue

        return max(ids, default=0) + 1

    def _start(
        self,
        record_id: int,
        command: str,
    ) -> None:
        # If a previous record somehow remained open,
        # close it before beginning the next one.
        if self.active_id is not None:
            self._finish(None)

        # Bash record IDs restart at 1 for every PTY session.
        # Allocate a persistent ID from the records directory instead.
        persistent_id = self.next_id
        self.next_id += 1
        self.session_ids[record_id] = persistent_id

        self.active_id = persistent_id
        self.active_command = command
        self.active_output.clear()

    def _finish(
        self,
        status: int | None,
    ) -> None:
        if self.active_id is None:
            return

        record_id = self.active_id

        cmd_path = (
            self.records_dir /
            f"{record_id}.cmd"
        )

        out_path = (
            self.records_dir /
            str(record_id)
        )

        # The command file contains the exact Bash
        # simple-command aggregation emitted by DEBUG.
        cmd_path.write_text(
            self.active_command + "\n",
            encoding="utf-8",
        )

        # Terminal output is deliberately binary-safe.
        # ANSI/control sequences are retained because this
        # represents what the terminal actually received.
        out_path.write_bytes(
            bytes(self.active_output)
        )

        self.active_id = None
        self.active_command = ""
        self.active_output.clear()

    def feed(self, chunk: bytes) -> bytes:
        """
        Consume PTY data.

        Returns the exact bytes that should be forwarded
        to the real terminal. DCS markers are retained in
        the returned stream because they are invisible terminal
        control sequences, but are excluded from record output.
        """

        self.marker_buffer.extend(chunk)

        terminal_output = bytearray()

        while True:
            start = self.marker_buffer.find(
                DCS_START
            )

            if start < 0:
                # Everything currently buffered is ordinary
                # terminal data except a possible ESC at the end.
                if self.marker_buffer[-1:] == b"\x1b":
                    terminal_output.extend(
                        self.marker_buffer[:-1]
                    )
                    self.marker_buffer = bytearray(
                        b"\x1b"
                    )
                else:
                    terminal_output.extend(
                        self.marker_buffer
                    )
                    self.marker_buffer.clear()

                break

            # Bytes before the DCS belong to the current
            # terminal stream.
            before = self.marker_buffer[:start]

            if before:
                terminal_output.extend(before)

            del self.marker_buffer[:start]

            end = self.marker_buffer.find(
                DCS_END,
                len(DCS_START),
            )

            if end < 0:
                # Incomplete DCS. Wait for the next PTY read.
                break

            payload = bytes(
                self.marker_buffer[
                    len(DCS_START):end
                ]
            )

            del self.marker_buffer[
                :end + len(DCS_END)
            ]

            self._handle_marker(payload)

        # Only ordinary terminal bytes belong to command output.
        if self.active_id is not None:
            self.active_output.extend(
                terminal_output
            )

        # DCS is invisible and is still forwarded exactly
        # as received so terminal behavior remains unchanged.
        return chunk

    def _handle_marker(
        self,
        payload: bytes,
    ) -> None:
        if payload.startswith(TMK_START):
            body = payload[len(TMK_START):]
            parts = body.split(b":", 1)

            if len(parts) != 2:
                return

            try:
                record_id = int(parts[0])
                command = decode_payload(parts[1])
            except Exception:
                return

            self._start(
                record_id,
                command,
            )

        elif payload.startswith(TMK_END):
            body = payload[len(TMK_END):]
            parts = body.split(b":", 2)

            if len(parts) != 3:
                return

            try:
                record_id = int(parts[0])
                int(parts[1])
            except ValueError:
                return

            persistent_id = self.session_ids.get(record_id)

            if (
                persistent_id is not None and
                self.active_id == persistent_id
            ):
                self._finish(
                    int(parts[1])
                )

    def finish(self) -> None:
        if self.active_id is not None:
            self._finish(None)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--records",
        required=True,
        help="TMK session record directory",
    )

    parser.add_argument(
        "--shell",
        default=os.environ.get(
            "SHELL",
            "/data/data/com.termux/files/usr/bin/bash",
        ),
    )

    parser.add_argument(
        "--rcfile",
        required=True,
        help="Bash recorder rcfile",
    )

    args = parser.parse_args()

    recorder = Recorder(
        Path(args.records)
    )

    rows, cols = terminal_size(
        sys.stdin.fileno()
    )

    pid, master = pty.fork()

    if pid == 0:
        os.environ["TMK_PTY_RECORDER"] = "1"

        os.execvp(
            args.shell,
            [
                args.shell,
                "--rcfile",
                args.rcfile,
                "-i",
            ],
        )

    try:
        set_winsize(
            master,
            rows,
            cols,
        )
    except OSError:
        pass

    old_tty = None

    if sys.stdin.isatty():
        old_tty = termios.tcgetattr(
            sys.stdin.fileno()
        )

        tty.setraw(
            sys.stdin.fileno()
        )

    def resize(
        _signum,
        _frame,
    ):
        try:
            rows, cols = terminal_size(
                sys.stdin.fileno()
            )

            set_winsize(
                master,
                rows,
                cols,
            )
        except OSError:
            pass

    old_winch = signal.signal(
        signal.SIGWINCH,
        resize,
    )

    child_alive = True

    try:
        while child_alive:
            stdin_fd = sys.stdin.fileno()

            readable, _, _ = select.select(
                [master, stdin_fd],
                [],
                [],
                0.25,
            )

            if master in readable:
                try:
                    chunk = os.read(
                        master,
                        65536,
                    )
                except OSError as e:
                    if e.errno == 5:
                        child_alive = False
                        break

                    raise

                if not chunk:
                    break

                output = recorder.feed(
                    chunk
                )

                os.write(
                    sys.stdout.fileno(),
                    output,
                )

                sys.stdout.flush()

            if stdin_fd in readable:
                try:
                    chunk = os.read(
                        stdin_fd,
                        65536,
                    )
                except OSError as e:
                    raise RuntimeError(
                        f"stdin read failed: {e}"
                    ) from e

                if not chunk:
                    child_alive = False
                    break

                os.write(
                    master,
                    chunk,
                )

            try:
                waited_pid, _ = os.waitpid(
                    pid,
                    os.WNOHANG,
                )

                if waited_pid == pid:
                    child_alive = False

            except ChildProcessError:
                child_alive = False

    finally:
        signal.signal(
            signal.SIGWINCH,
            old_winch,
        )

        if old_tty is not None:
            termios.tcsetattr(
                sys.stdin.fileno(),
                termios.TCSADRAIN,
                old_tty,
            )

        recorder.finish()

        try:
            os.close(master)
        except OSError:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
