import subprocess

from config import JSON_PATH
from helpers import generate_helpers
from properties import build_termux_layout
from tmux import generate_tmux_config


def main():

    try:
        generate_helpers()
        build_termux_layout()
        generate_tmux_config()

        subprocess.run(
            ["termux-reload-settings"],
            check=True
        )

    except Exception as e:
        print(
            f"❌ Termux configuration update failed: {e}"
        )
        return 1

    print()
    print(
        "✅ Termux configuration updated"
    )
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
