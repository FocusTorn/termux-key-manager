#!/data/data/com.termux/files/usr/bin/python

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
RECORDER = PROJECT_DIR / "pty_recorder.py"
RCFILE = Path.home() / ".termux" / "helpers.sh"
RECORDS = Path.home() / ".termux" / "tmk-session" / "records"


def main() -> int:
    RECORDS.mkdir(parents=True, exist_ok=True)

    return subprocess.call(
        [
            sys.executable,
            str(RECORDER),
            "--records",
            str(RECORDS),
            "--rcfile",
            str(RCFILE),
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
