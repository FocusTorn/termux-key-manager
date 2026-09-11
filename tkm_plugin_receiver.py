#!/usr/bin/env python3

from __future__ import annotations

import struct
from pathlib import Path

from tkm_plugin_protocol import MessageType
from tkm_plugin_transport import TkmUnixServer, recv_frame


DEFAULT_SOCKET = (
    Path.home() / ".termux" / "tmk-session" / "tkm-plugin.sock"
)

DEFAULT_OUTPUT = (
    Path.home() / ".termux" / "tmk-session" / "plugin-raw-output.bin"
)


def parse_output(payload: bytes) -> tuple[str, int, bytes]:
    if not payload or payload[0] != MessageType.OUTPUT:
        raise ValueError("not an OUTPUT message")

    pos = 1

    if len(payload) < pos + 2:
        raise ValueError("truncated OUTPUT handle length")

    handle_length = struct.unpack(">H", payload[pos:pos + 2])[0]
    pos += 2

    if len(payload) < pos + handle_length:
        raise ValueError("truncated OUTPUT session handle")

    handle = payload[pos:pos + handle_length].decode("utf-8")
    pos += handle_length

    if len(payload) < pos + 8:
        raise ValueError("truncated OUTPUT metadata")

    sequence, data_length = struct.unpack(
        ">II",
        payload[pos:pos + 8],
    )
    pos += 8

    if len(payload) != pos + data_length:
        raise ValueError("OUTPUT data length mismatch")

    data = payload[pos:]

    return handle, sequence, data


def _receive_client(
    client: object,
    output,
) -> tuple[int, int]:
    expected_sequence = 0
    message_count = 0
    byte_count = 0

    while True:
        try:
            payload = recv_frame(client)
        except EOFError:
            break

        message_type = MessageType(payload[0])

        if message_type is MessageType.OUTPUT:
            handle, sequence, data = parse_output(payload)

            if sequence != expected_sequence:
                raise RuntimeError(
                    "OUTPUT sequence gap: "
                    f"expected {expected_sequence}, "
                    f"received {sequence}"
                )

            expected_sequence += 1
            message_count += 1
            byte_count += len(data)

            output.write(data)
            output.flush()

            print(
                "OUTPUT "
                f"session={handle!r} "
                f"seq={sequence} "
                f"bytes={len(data)}",
                flush=True,
            )

        elif message_type is MessageType.HELLO:
            print("HELLO", flush=True)
        elif message_type is MessageType.SESSION_ATTACH:
            print("SESSION_ATTACH", flush=True)
        elif message_type is MessageType.SESSION_DETACH:
            print("SESSION_DETACH", flush=True)
        elif message_type is MessageType.SESSION_CHANGED:
            print("SESSION_CHANGED", flush=True)
        elif message_type is MessageType.SESSION_CLOSED:
            print("SESSION_CLOSED", flush=True)
        elif message_type is MessageType.PING:
            print("PING", flush=True)
        else:
            print(f"IGNORED message type={message_type!r}", flush=True)

    return message_count, byte_count


def receive_forever(
    socket_path: Path = DEFAULT_SOCKET,
    output_path: Path = DEFAULT_OUTPUT,
    expected_connections: int | None = None,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with TkmUnixServer(socket_path) as server:
        print(f"TKM_PLUGIN_READY {socket_path}", flush=True)

        connection_count = 0
        total_messages = 0
        total_bytes = 0

        with output_path.open("wb") as output:
            while (
                expected_connections is None
                or connection_count < expected_connections
            ):
                with server.accept() as client:
                    connection_count += 1
                    print("TKM_PLUGIN_CONNECTED", flush=True)

                    message_count, byte_count = _receive_client(
                        client,
                        output,
                    )

                    total_messages += message_count
                    total_bytes += byte_count

        print(
            f"TKM_PLUGIN_DONE messages={total_messages} "
            f"bytes={total_bytes} "
            f"connections={connection_count}",
            flush=True,
        )


def receive_once(
    socket_path: Path = DEFAULT_SOCKET,
    output_path: Path = DEFAULT_OUTPUT,
) -> None:
    receive_forever(
        socket_path=socket_path,
        output_path=output_path,
        expected_connections=1,
    )
