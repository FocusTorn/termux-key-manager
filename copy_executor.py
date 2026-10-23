"""Shared native tmux copy executor for TKM copy actions."""

import argparse
import subprocess
import sys

from copy_selector import select_entire_pane, select_pytest_subset


_COPY_ACTIONS = {
    "copy_entire_pane": ("-pF", "-S", "-"),
    "copy_viewport": ("-pJ",),
    "copy_subset": ("-pF", "-S", "-"),
}


def _run_tmux(arguments, *, capture_output=False, input_text=None):
    command = ["tmux", *arguments]
    kwargs = {"check": True}
    if capture_output:
        kwargs.update(capture_output=True, text=True)
    if input_text is not None:
        kwargs.update(input=input_text, text=True)
    return subprocess.run(command, **kwargs)


def _normalize_pane_text(text):
    """Trim per-line trailing whitespace and terminal blank rows."""
    lines = [line.rstrip() for line in text.splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + ("\n" if lines else "")


def execute_copy(action, pane_id):
    """Execute one copy action; return False without changing clipboard on failure."""
    if action not in _COPY_ACTIONS:
        raise ValueError(f"unknown copy action: {action}")
    if not pane_id:
        raise ValueError("pane_id is required")

    mode_result = _run_tmux(
        ["display-message", "-p", "-t", pane_id, "#{pane_in_mode}"],
        capture_output=True,
    )
    in_copy_mode = mode_result.stdout.strip() == "1"

    try:
        capture_args = ["capture-pane", *_COPY_ACTIONS[action], "-t", pane_id]
        captured = _run_tmux(capture_args, capture_output=True).stdout

        if action == "copy_entire_pane":
            output = select_entire_pane(captured)
        elif action == "copy_subset":
            output = select_pytest_subset(captured)
        else:
            output = _normalize_pane_text(captured)

        if not output:
            return False

        _run_tmux(["load-buffer", "-"], input_text=output)
        subprocess.run(
            ["termux-clipboard-set"],
            input=output,
            text=True,
            check=True,
        )
        return True
    finally:
        if in_copy_mode:
            _run_tmux(["send-keys", "-t", pane_id, "-X", "cancel"])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=tuple(_COPY_ACTIONS))
    parser.add_argument("pane_id")
    args = parser.parse_args(argv)

    try:
        copied = execute_copy(args.action, args.pane_id)
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"TKM copy failed: {exc}", file=sys.stderr)
        return 1

    if not copied:
        print("TKM copy skipped: no valid content range", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
