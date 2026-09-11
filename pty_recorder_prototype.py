#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import json
import os
import pty
import select
import signal
import struct
import sys
import termios
import time
import tty
from dataclasses import dataclass, asdict


DCS_START = b"\x1bP"
DCS_END = b"\x1b\\"


@dataclass
class Record:
    id: int
    command: str
    commands: str
    status: int | None
    started_at: float
    ended_at: float | None


def decode(value: str) -> str:
    return base64.b64decode(value).decode("utf-8", "replace")


def terminal_size():
    try:
        size = os.get_terminal_size(sys.stdout.fileno())
        return size.lines, size.columns
    except OSError:
        return 24, 80


def set_winsize(fd, rows, cols):
    import fcntl

    fcntl.ioctl(
        fd,
        termios.TIOCSWINSZ,
        struct.pack("HHHH", rows, cols, 0, 0),
    )


def parse_marker(payload, records):
    text = payload.decode("ascii", "replace")
    parts = text.split(":", 3)

    if parts[0] == "TMK_START" and len(parts) == 3:
        try:
            record_id = int(parts[1])
            command = decode(parts[2])

            records[record_id] = Record(
                id=record_id,
                command=command,
                commands=command,
                status=None,
                started_at=time.time(),
                ended_at=None,
            )
        except Exception:
            pass

    elif parts[0] == "TMK_END" and len(parts) == 4:
        try:
            record_id = int(parts[1])
            status = int(parts[2])
            commands = decode(parts[3])

            record = records.get(record_id)

            if record is None:
                record = Record(
                    id=record_id,
                    command=commands.splitlines()[0] if commands else "",
                    commands=commands,
                    status=status,
                    started_at=time.time(),
                    ended_at=time.time(),
                )
                records[record_id] = record
            else:
                record.commands = commands
                record.status = status
                record.ended_at = time.time()

        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json")
    args = parser.parse_args()

    root = os.path.abspath(
        os.path.dirname(__file__)
    )

    rcfile = os.path.join(
        root,
        ".tmk-pty-test-rc",
    )

    hook = r'''
TMK_RECORD_ACTIVE=0
TMK_RECORD_ID=0
TMK_COMMANDS=

_tmk_emit()
{
    local payload="$1"

    trap - DEBUG
    builtin printf '\033P%s\033\\' "$payload"
    trap '_tmk_debug' DEBUG
}

_tmk_debug()
{
    case "$BASH_COMMAND" in
        _tmk_*|TMK_*|PROMPT_COMMAND=*|return\ *|trap\ *)
            return
            ;;
    esac

    [[ "$BASH_SUBSHELL" -gt 0 ]] && return

    if [[ "$TMK_RECORD_ACTIVE" != 1 ]]; then
        TMK_RECORD_ACTIVE=1
        TMK_RECORD_ID=$((TMK_RECORD_ID + 1))
        TMK_COMMANDS="$BASH_COMMAND"

        local encoded
        encoded="$(
            builtin printf '%s' "$BASH_COMMAND" |
            base64 |
            tr -d '\n'
        )"

        _tmk_emit \
            "TMK_START:${TMK_RECORD_ID}:${encoded}"
    else
        TMK_COMMANDS+=$'\n'"$BASH_COMMAND"
    fi
}

_tmk_prompt()
{
    local status=$?

    if [[ "$TMK_RECORD_ACTIVE" == 1 ]]; then
        local encoded

        encoded="$(
            builtin printf '%s' "$TMK_COMMANDS" |
            base64 |
            tr -d '\n'
        )"

        _tmk_emit \
            "TMK_END:${TMK_RECORD_ID}:${status}:${encoded}"

        TMK_RECORD_ACTIVE=0
        TMK_COMMANDS=
    fi

    return "$status"
}

trap '_tmk_debug' DEBUG
PROMPT_COMMAND='_tmk_prompt'
PS1='TMK> '
'''

    with open(rcfile, "w", encoding="utf-8") as fh:
        fh.write(hook)

    rows, cols = terminal_size()

    records = {}
    marker_buffer = bytearray()

    pid, master = pty.fork()

    if pid == 0:
        os.environ["TMK_PTY_RECORDER"] = "1"

        os.execvp(
            os.environ.get("SHELL", "/bin/bash"),
            [
                os.environ.get("SHELL", "/bin/bash"),
                "--rcfile",
                rcfile,
                "-i",
            ],
        )

    set_winsize(master, rows, cols)

    old_tty = None

    if sys.stdin.isatty():
        old_tty = termios.tcgetattr(sys.stdin.fileno())
        tty.setraw(sys.stdin.fileno())

    def resize(_signum, _frame):
        try:
            rows, cols = terminal_size()
            set_winsize(master, rows, cols)
        except OSError:
            pass

    old_winch = signal.signal(
        signal.SIGWINCH,
        resize,
    )

    try:
        while True:
            readable, _, _ = select.select(
                [master, sys.stdin],
                [],
                [],
                0.25,
            )

            if master in readable:
                try:
                    chunk = os.read(master, 65536)
                except OSError:
                    break

                if not chunk:
                    break

                marker_buffer.extend(chunk)

                while True:
                    start = marker_buffer.find(DCS_START)

                    if start < 0:
                        # Keep a possible ESC byte for the next read.
                        if marker_buffer[-1:] == b"\x1b":
                            marker_buffer = bytearray(b"\x1b")
                        else:
                            marker_buffer.clear()
                        break

                    if start:
                        del marker_buffer[:start]

                    end = marker_buffer.find(
                        DCS_END,
                        len(DCS_START),
                    )

                    if end < 0:
                        break

                    payload = bytes(
                        marker_buffer[
                            len(DCS_START):end
                        ]
                    )

                    del marker_buffer[:end + len(DCS_END)]

                    parse_marker(
                        payload,
                        records,
                    )

                os.write(
                    sys.stdout.fileno(),
                    chunk,
                )
                sys.stdout.flush()

            if sys.stdin in readable:
                chunk = os.read(
                    sys.stdin.fileno(),
                    65536,
                )

                if not chunk:
                    break

                os.write(master, chunk)

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

        try:
            os.close(master)
        except OSError:
            pass

    if args.json:
        output = []

        for record in sorted(
            records.values(),
            key=lambda item: item.id,
        ):
            item = asdict(record)

            if record.ended_at is not None:
                item["duration"] = (
                    record.ended_at -
                    record.started_at
                )
            else:
                item["duration"] = None

            output.append(item)

        with open(
            args.json,
            "w",
            encoding="utf-8",
        ) as fh:
            json.dump(
                output,
                fh,
                indent=2,
            )
            fh.write("\n")

    try:
        os.unlink(rcfile)
    except OSError:
        pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
