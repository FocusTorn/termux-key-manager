from subprocess import CompletedProcess
from unittest.mock import patch

from copy_executor import execute_copy
from copy_selector import select_viewport


def _prompt(timestamp, alias="utr", status="✔", command=""):
    input_text = f"❯ {command}" if command else "❯"
    return (
        f"P {timestamp} | {alias} main | {status}\n"
        f"- {input_text}\n"
    )


def _copy_with_capture(action, capture):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        if command[:2] == ["tmux", "display-message"]:
            return CompletedProcess(command, 0, stdout="0\n", stderr="")
        if command[:2] == ["tmux", "capture-pane"]:
            return CompletedProcess(command, 0, stdout=capture, stderr="")
        return CompletedProcess(command, 0, stdout="", stderr="")

    with patch("copy_executor.subprocess.run", side_effect=fake_run):
        copied = execute_copy(action, "%1")

    capture_command = next(
        command for command, _ in calls if command[:2] == ["tmux", "capture-pane"]
    )
    buffer_values = [
        kwargs["input"]
        for command, kwargs in calls
        if command == ["tmux", "load-buffer", "-"]
    ]
    clipboard_values = [
        kwargs["input"]
        for command, kwargs in calls
        if command == ["termux-clipboard-set"]
    ]
    return copied, capture_command, buffer_values, clipboard_values


def test_three_empty_prompts_with_same_identity_ignore_timestamp_changes():
    capture = _prompt("1526.12") + _prompt("1526.16") + _prompt("1526.20")
    assert select_viewport(capture) == "1526.12 | utr main | ✔\n❯\n"


def test_alias_or_git_status_difference_keeps_distinct_empty_prompts():
    capture = (
        _prompt("1526.12", alias="tkm", status="✔")
        + _prompt("1526.16", alias="tkm", status="Ø1")
        + _prompt("1526.20", alias="spl", status="Ø1")
    )
    selected = select_viewport(capture)
    assert selected is not None
    assert selected.count(" | ") == 3
    assert "tkm main | ✔" in selected
    assert "tkm main | Ø1" in selected
    assert "spl main | Ø1" in selected


def test_command_bearing_prompts_are_not_deduplicated():
    capture = _prompt("1526.12", alias="tkm", command="tkm") + _prompt(
        "1526.16", alias="tkm", command="tkm"
    )
    assert select_viewport(capture) == (
        "1526.12 | tkm main | ✔\n❯ tkm\n"
        "1526.16 | tkm main | ✔\n❯ tkm\n"
    )


def test_unrecognized_prompt_layout_is_preserved():
    capture = "P ordinary prompt context\n- ❯\nP ordinary prompt context\n- ❯\n"
    assert select_viewport(capture) == (
        "ordinary prompt context\n❯\nordinary prompt context\n❯\n"
    )


def test_prompt_like_output_without_prompt_flags_is_preserved():
    capture = (
        "O 1526.12 | utr main | ✔\n- ❯\n"
        "O 1526.12 | utr main | ✔\n- ❯\n"
    )
    assert select_viewport(capture) == (
        "1526.12 | utr main | ✔\n❯\n1526.12 | utr main | ✔\n❯\n"
    )


def test_non_prompt_rows_and_crlf_trailing_whitespace_are_preserved():
    capture = (
        "O retain this  \r\n"
        + _prompt("1526.12").replace("\n", "\r\n")
        + _prompt("1526.16").replace("\n", "\r\n")
        + _prompt("1527.12", alias="spl", status="Ø1").replace("\n", "\r\n")
    )
    assert select_viewport(capture) == (
        "retain this  \r\n"
        "1526.12 | utr main | ✔\r\n❯\r\n"
        "1527.12 | spl main | Ø1\r\n❯\r\n"
    )


def test_all_copy_actions_filter_after_their_selection_step():
    capture = (
        "O useful output  \n"
        + _prompt("1526.12")
        + _prompt("1526.16")
        + _prompt("1526.20")
        + _prompt("1527.12", alias="spl", status="Ø1")
    )
    subset_capture = "O .......                         [100%]\n" + capture
    expected = {
        "copy_entire_pane": "useful output  \n1526.12 | utr main | ✔\n❯\n",
        "copy_subset": ".......                         [100%]\nuseful output  \n1526.12 | utr main | ✔\n❯\n",
        "copy_viewport": "useful output\n1526.12 | utr main | ✔\n❯\n1527.12 | spl main | Ø1\n❯\n",
    }
    captures = {
        "copy_entire_pane": capture,
        "copy_subset": subset_capture,
        "copy_viewport": capture,
    }
    for action, source in captures.items():
        copied, capture_command, buffer_values, clipboard_values = _copy_with_capture(action, source)
        assert copied is True
        assert len(buffer_values) == len(clipboard_values) == 1
        assert buffer_values[0] == clipboard_values[0] == expected[action]
        assert ("-pFJ" in capture_command) if action == "copy_viewport" else ("-pF" in capture_command)
