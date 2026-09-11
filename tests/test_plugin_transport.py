#!/usr/bin/env python3

from __future__ import annotations

import socket
import threading
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tkm_plugin_protocol import pack_output
from tkm_plugin_transport import TkmUnixServer, recv_frame, send_frame


class PluginTransportTests(unittest.TestCase):
    def test_server_client_transport_preserves_frame_payload(self) -> None:
        expected = pack_output(
            "session-transport-test",
            42,
            b"\x00\xff\x1b[31mTKM\x1b[0m\r\n",
        )

        with TemporaryDirectory() as tmp:
            socket_path = Path(tmp) / "test-plugin.sock"
            result: dict[str, bytes] = {}
            errors: list[BaseException] = []

            def server() -> None:
                try:
                    with TkmUnixServer(socket_path) as server_socket:
                        result["ready"] = b"1"

                        with server_socket.accept() as client:
                            result["received"] = recv_frame(client)
                except BaseException as exc:
                    errors.append(exc)

            thread = threading.Thread(target=server, daemon=True)
            thread.start()

            deadline = time.monotonic() + 5
            while not result.get("ready"):
                if errors:
                    raise errors[0]
                if time.monotonic() >= deadline:
                    self.fail("transport server was not ready")
                time.sleep(0.01)

            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.connect(str(socket_path))
                send_frame(client, expected)

            thread.join(timeout=5)

            if thread.is_alive():
                self.fail("transport server thread did not finish")

            if errors:
                raise errors[0]

            self.assertEqual(result.get("received"), expected)
            self.assertFalse(socket_path.exists())


if __name__ == "__main__":
    unittest.main()
