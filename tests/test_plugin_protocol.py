#!/usr/bin/env python3

from __future__ import annotations

import struct
import unittest

from tkm_plugin_protocol import (
    MessageType,
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    pack_hello,
    pack_output,
    pack_session_attach,
    pack_session_closed,
    pack_session_handle,
)


def unpack(frame: bytes) -> tuple[MessageType, bytes]:
    assert len(frame) >= 5

    length = struct.unpack(">I", frame[:4])[0]
    assert length == len(frame) - 4

    payload = frame[4:]
    return MessageType(payload[0]), payload[1:]


def read_handle(payload: bytes) -> tuple[str, bytes]:
    size = struct.unpack(">H", payload[:2])[0]
    start = 2
    end = start + size
    return payload[start:end].decode("utf-8"), payload[end:]


class PluginProtocolTests(unittest.TestCase):
    def test_hello(self) -> None:
        frame = pack_hello()
        message_type, payload = unpack(frame)

        self.assertIs(message_type, MessageType.HELLO)

        major, minor, capabilities = struct.unpack(">HHI", payload)

        self.assertEqual(major, PROTOCOL_MAJOR)
        self.assertEqual(minor, PROTOCOL_MINOR)
        self.assertEqual(capabilities, 0x00000003)

    def test_session_attach(self) -> None:
        frame = pack_session_attach("session-42", 12345)
        message_type, payload = unpack(frame)

        self.assertIs(message_type, MessageType.SESSION_ATTACH)

        handle, rest = read_handle(payload)
        pid = struct.unpack(">i", rest)[0]

        self.assertEqual(handle, "session-42")
        self.assertEqual(pid, 12345)

    def test_output_preserves_raw_bytes(self) -> None:
        raw = (
            b"\x1b[31mRED\x1b[0m\r\n"
            b"\x1b[2K\x1b[1G"
            b"\x00\x01\x02\xff"
            b"line-after-control\r\n"
        )

        frame = pack_output("session-42", 17, raw)
        message_type, payload = unpack(frame)

        self.assertIs(message_type, MessageType.OUTPUT)

        handle, rest = read_handle(payload)
        sequence, data_length = struct.unpack(">II", rest[:8])
        data = rest[8:]

        self.assertEqual(handle, "session-42")
        self.assertEqual(sequence, 17)
        self.assertEqual(data_length, len(raw))
        self.assertEqual(data, raw)

    def test_session_detach(self) -> None:
        frame = pack_session_handle(
            MessageType.SESSION_DETACH,
            "session-42",
        )
        message_type, payload = unpack(frame)

        self.assertIs(message_type, MessageType.SESSION_DETACH)

        handle, rest = read_handle(payload)

        self.assertEqual(handle, "session-42")
        self.assertEqual(rest, b"")

    def test_session_closed(self) -> None:
        frame = pack_session_closed("session-42", 7)
        message_type, payload = unpack(frame)

        self.assertIs(message_type, MessageType.SESSION_CLOSED)

        handle, rest = read_handle(payload)
        exit_status = struct.unpack(">i", rest)[0]

        self.assertEqual(handle, "session-42")
        self.assertEqual(exit_status, 7)


if __name__ == "__main__":
    unittest.main()
