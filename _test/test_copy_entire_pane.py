import subprocess
from unittest.mock import patch

import copy_executor


def _mock_tmux(capture_text, pane_mode="0"):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        if command[:2] == ["tmux", "display-message"]:
            return subprocess.CompletedProcess(command, 0, stdout=f"{pane_mode}\n", stderr="")
        if command[:2] == ["tmux", "capture-pane"]:
            return subprocess.CompletedProcess(command, 0, stdout=capture_text, stderr="")
        if command[:2] == ["tmux", "load-buffer"] or command[:2] == ["tmux", "send-keys"] or command == ["termux-clipboard-set"]:
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        raise AssertionError(f"unexpected command: {command}")

    return calls, fake_run


def _commands(calls, prefix):
    return [command for command, _ in calls if command[:len(prefix)] == prefix]


def test_copy_entire_pane_cuts_at_last_prompt_and_preserves_prior_content_exactly():
    capture_text = (
        "O earlier output  \r\n"
        "P previous prompt\r\n"
        "O ~/projects/demo $ is ordinary output  \r\n"
        "-   \r\n"
        "O final output line  \r\n"
        "PX current prompt\r\n"
        "X current prompt metadata\r\n"
        "O content after prompt\r\n"
    )
    expected = (
        "earlier output  \r\n"
        "previous prompt\r\n"
        "~/projects/demo $ is ordinary output  \r\n"
        "  \r\n"
        "final output line  \r\n"
    )
    calls, fake_run = _mock_tmux(capture_text)

    with patch("copy_executor.subprocess.run", side_effect=fake_run):
        assert copy_executor.execute_copy("copy_entire_pane", "%1") is True

    capture = _commands(calls, ["tmux", "capture-pane"])[0]
    assert "-pF" in capture
    assert "-J" not in capture
    assert "-S" in capture and capture[capture.index("-S") + 1] == "-"
    buffer_writes = [kwargs for command, kwargs in calls if command == ["tmux", "load-buffer", "-"]]
    clipboard = [kwargs for command, kwargs in calls if command == ["termux-clipboard-set"]]
    assert len(buffer_writes) == len(clipboard) == 1
    assert buffer_writes[0]["input"] == expected
    assert clipboard[0]["input"] == expected


def test_copy_entire_pane_fails_closed_without_prompt_boundary():
    calls, fake_run = _mock_tmux("O useful output\n- more output\n")

    with patch("copy_executor.subprocess.run", side_effect=fake_run):
        assert copy_executor.execute_copy("copy_entire_pane", "%2") is False

    assert not _commands(calls, ["tmux", "load-buffer"])
    assert not _commands(calls, ["termux-clipboard-set"])


def test_copy_entire_pane_fails_closed_when_prompt_is_first_row():
    calls, fake_run = _mock_tmux("PX current prompt\nX prompt metadata\n")

    with patch("copy_executor.subprocess.run", side_effect=fake_run):
        assert copy_executor.execute_copy("copy_entire_pane", "%3") is False

    assert not _commands(calls, ["tmux", "load-buffer"])
    assert not _commands(calls, ["termux-clipboard-set"])


def test_selector_preserves_carriage_returns_blank_rows_and_trailing_spaces():
    from copy_selector import select_entire_pane

    capture = (
        "- before  \r\n"
        "-   \r\n"
        "P earlier prompt\r\n"
        "O ~/demo $ ordinary output  \r\n"
        "PX final prompt without newline"
    )
    assert select_entire_pane(capture) == (
        "before  \r\n"
        "  \r\n"
        "earlier prompt\r\n"
        "~/demo $ ordinary output  \r\n"
    )


def test_selector_fails_closed_when_prompt_boundary_is_missing_or_malformed():
    from copy_selector import select_entire_pane

    assert select_entire_pane("O output\n- more output\n") is None
    assert select_entire_pane("O output\nmalformed row\nPX prompt\n") is None


def test_selector_fails_closed_when_final_prompt_has_no_preceding_content():
    from copy_selector import select_entire_pane

    assert select_entire_pane("PX final prompt\nX after prompt\n") is None


def test_copy_entire_pane_cancels_copy_mode_without_touching_clipboards_on_invalid_capture():
    calls, fake_run = _mock_tmux("O no prompt marker\n", pane_mode="1")

    with patch("copy_executor.subprocess.run", side_effect=fake_run):
        assert copy_executor.execute_copy("copy_entire_pane", "%4") is False

    assert not _commands(calls, ["tmux", "load-buffer"])
    assert not _commands(calls, ["termux-clipboard-set"])
    assert _commands(calls, ["tmux", "send-keys"]) == [
        ["tmux", "send-keys", "-t", "%4", "-X", "cancel"]
    ]
