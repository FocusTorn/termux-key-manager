#!/usr/bin/env python3

from __future__ import annotations

import os
import socket
import struct
from pathlib import Path

from tkm_plugin_protocol import MAX_PAYLOAD


DEFAULT_SOCKET = (
    Path.home() / ".termux" / "tmk-session" / "tkm-plugin.sock"
)


class ProtocolError(RuntimeError):
    pass


def _recv_exact(sock: socket.socket, size: int) -> bytes:
    chunks = bytearray()

    while len(chunks) < size:
        chunk = sock.recv(size - len(chunks))

        if not chunk:
            raise EOFError("TKM plugin socket closed")

        chunks.extend(chunk)

    return bytes(chunks)


def recv_frame(sock: socket.socket) -> bytes:
    header = _recv_exact(sock, 4)
    length = struct.unpack(">I", header)[0]

    if length < 1:
        raise ProtocolError("invalid zero-length TKM message")

    if length > MAX_PAYLOAD:
        raise ProtocolError(
            f"TKM message exceeds MAX_PAYLOAD: {length}"
        )

    return _recv_exact(sock, length)


def send_frame(sock: socket.socket, frame: bytes) -> None:
    sock.sendall(frame)


class TkmUnixServer:
    def __init__(
        self,
        path: str | os.PathLike[str] = DEFAULT_SOCKET,
    ) -> None:
        self.path = Path(path)
        self.server: socket.socket | None = None

    def open(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        try:
            self.path.unlink()
        except FileNotFoundError:
            pass

        server = socket.socket(
            socket.AF_UNIX,
            socket.SOCK_STREAM,
        )

        server.bind(str(self.path))

        # Socket is private to the Termux/TKM user.
        os.chmod(self.path, 0o600)

        server.listen(1)
        self.server = server

    def accept(self) -> socket.socket:
        if self.server is None:
            raise RuntimeError("TKM Unix server is not open")

        client, _ = self.server.accept()
        return client

    def close(self) -> None:
        if self.server is not None:
            self.server.close()
            self.server = None

        try:
            self.path.unlink()
        except FileNotFoundError:
            pass

    def __enter__(self) -> "TkmUnixServer":
        self.open()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def connect(
    path: str | os.PathLike[str] = DEFAULT_SOCKET,
) -> socket.socket:
    sock = socket.socket(
        socket.AF_UNIX,
        socket.SOCK_STREAM,
    )

    sock.connect(str(path))
    return sock
