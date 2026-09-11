#!/usr/bin/env python3

from __future__ import annotations

import socket
import threading
from pathlib import Path

from tkm_plugin_protocol import (
    pack_output,
    pack_session_attach,
    pack_session_closed,
)
from tkm_plugin_receiver import receive_once


ROOT = (
    Path.home()
    / ".termux"
    / "tmk-session"
)

SOCKET = ROOT / "test-receiver.sock"
OUTPUT = ROOT / "test-receiver-output.bin"


def main() -> None:
    raw_parts = [
        b"\x1b[31mTKM TEST 1\x1b[0m\r\n",
        b"\x1b[2K\x1b[1G",
        b"\x00\x01\x02\xff",
        b"TKM TEST 2\r\n",
    ]

    received_errors: list[BaseException] = []

    def worker() -> None:
        try:
            receive_once(SOCKET, OUTPUT)
        except BaseException as exc:
            received_errors.append(exc)

    thread = threading.Thread(
        target=worker,
        name="TKM-ReceiverTest",
    )
    thread.start()

    # Give the Unix socket server time to bind.
    import time
    time.sleep(0.2)

    with socket.socket(
        socket.AF_UNIX,
        socket.SOCK_STREAM,
    ) as sock:
        sock.connect(str(SOCKET))

        sock.sendall(
            pack_session_attach(
                "receiver-test",
                4242,
            )
        )

        for sequence, data in enumerate(raw_parts):
            sock.sendall(
                pack_output(
                    "receiver-test",
                    sequence,
                    data,
                )
            )

        sock.sendall(
            pack_session_closed(
                "receiver-test",
                0,
            )
        )

    thread.join(timeout=5)

    if thread.is_alive():
        raise RuntimeError("receiver did not terminate")

    if received_errors:
        raise received_errors[0]

    expected = b"".join(raw_parts)
    actual = OUTPUT.read_bytes()

    assert actual == expected

    OUTPUT.unlink()

    print("✅ TKM plugin receiver passed")
    print("   session attach:       OK")
    print("   OUTPUT parsing:       OK")
    print("   sequence validation:  OK")
    print("   raw byte preservation: OK")
    print("   session close:        OK")
    print("   diagnostic output:    OK")


if __name__ == "__main__":
    main()
