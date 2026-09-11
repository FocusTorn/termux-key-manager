#!/usr/bin/env python3

from __future__ import annotations

import enum
import struct


PROTOCOL_MAJOR = 1
PROTOCOL_MINOR = 0

MAX_PAYLOAD = 1024 * 1024


class MessageType(enum.IntEnum):
    HELLO = 0x01
    SESSION_ATTACH = 0x02
    SESSION_DETACH = 0x03
    OUTPUT = 0x04
    SESSION_CHANGED = 0x05
    SESSION_CLOSED = 0x06
    PING = 0x07
    PONG = 0x08
    ERROR = 0x09


CAP_RAW_OUTPUT = 0x00000001
CAP_SESSION_LIFECYCLE = 0x00000002


def pack_message(message_type: MessageType, payload: bytes = b"") -> bytes:
    body = bytes([int(message_type)]) + payload

    if len(body) > MAX_PAYLOAD:
        raise ValueError("TKM protocol payload exceeds MAX_PAYLOAD")

    return struct.pack(">I", len(body)) + body


def pack_hello() -> bytes:
    payload = struct.pack(
        ">HHI",
        PROTOCOL_MAJOR,
        PROTOCOL_MINOR,
        CAP_RAW_OUTPUT | CAP_SESSION_LIFECYCLE,
    )
    return pack_message(MessageType.HELLO, payload)


def pack_session_handle(
    message_type: MessageType,
    session_handle: str,
) -> bytes:
    encoded = session_handle.encode("utf-8")

    if len(encoded) > 0xFFFF:
        raise ValueError("session handle too long")

    payload = struct.pack(">H", len(encoded)) + encoded
    return pack_message(message_type, payload)


def pack_session_attach(
    session_handle: str,
    shell_pid: int,
) -> bytes:
    encoded = session_handle.encode("utf-8")

    if len(encoded) > 0xFFFF:
        raise ValueError("session handle too long")

    payload = (
        struct.pack(">H", len(encoded))
        + encoded
        + struct.pack(">i", shell_pid)
    )

    return pack_message(MessageType.SESSION_ATTACH, payload)


def pack_output(
    session_handle: str,
    sequence: int,
    data: bytes,
) -> bytes:
    encoded = session_handle.encode("utf-8")

    if len(encoded) > 0xFFFF:
        raise ValueError("session handle too long")

    payload = (
        struct.pack(">H", len(encoded))
        + encoded
        + struct.pack(">II", sequence, len(data))
        + data
    )

    return pack_message(MessageType.OUTPUT, payload)


def pack_session_closed(
    session_handle: str,
    exit_status: int,
) -> bytes:
    encoded = session_handle.encode("utf-8")

    if len(encoded) > 0xFFFF:
        raise ValueError("session handle too long")

    payload = (
        struct.pack(">H", len(encoded))
        + encoded
        + struct.pack(">i", exit_status)
    )

    return pack_message(MessageType.SESSION_CLOSED, payload)
