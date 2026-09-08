import subprocess

from config import JSON_PATH
from helpers import generate_helpers
from properties import build_termux_layout


def main():

    try:
        generate_helpers()
        build_termux_layout()

        subprocess.run(
            ["termux-reload-settings"],
            check=True
        )

    except Exception as e:
        print(
            f"❌ Termux configuration update failed: {e}"
        )
        return 1

    print(
        "✅ Termux configuration updated"
    )
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
