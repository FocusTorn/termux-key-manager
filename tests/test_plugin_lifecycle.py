#!/usr/bin/env python3

from __future__ import annotations

import socket
import threading
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tkm_plugin_protocol import (
    MessageType,
    pack_output,
    pack_session_attach,
    pack_session_closed,
)
from tkm_plugin_receiver import receive_forever
from tkm_plugin_transport import connect


class PluginLifecycleTests(unittest.TestCase):
    def test_receiver_accepts_reconnect_after_client_disconnect(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            socket_path = root / "tkm-plugin.sock"
            output_path = root / "plugin-raw-output.bin"

            result: dict[str, object] = {}

            def run_receiver() -> None:
                try:
                    receive_forever(
                        socket_path=socket_path,
                        output_path=output_path,
                        expected_connections=2,
                    )
                    result["completed"] = True
                except BaseException as exc:
                    result["error"] = exc

            thread = threading.Thread(target=run_receiver, daemon=True)
            thread.start()

            deadline = time.monotonic() + 5
            while not socket_path.exists():
                if time.monotonic() >= deadline:
                    self.fail("receiver socket was not created")
                time.sleep(0.01)

            with connect(socket_path) as client:
                client.sendall(
                    pack_session_attach("lifecycle-test", 1234)
                )
                client.sendall(
                    pack_output("lifecycle-test", 0, b"first\r\n")
                )
                client.sendall(
                    pack_session_closed("lifecycle-test", 0)
                )

            with connect(socket_path) as client:
                client.sendall(
                    pack_session_attach("lifecycle-test", 1234)
                )
                client.sendall(
                    pack_output("lifecycle-test", 0, b"second\r\n")
                )
                client.sendall(
                    pack_session_closed("lifecycle-test", 0)
                )

            thread.join(timeout=5)

            self.assertFalse(thread.is_alive(), "receiver did not finish")
            self.assertNotIn("error", result, result.get("error"))
            self.assertTrue(result.get("completed"))
            self.assertEqual(
                output_path.read_bytes(),
                b"first\r\nsecond\r\n",
            )


if __name__ == "__main__":
    unittest.main()
