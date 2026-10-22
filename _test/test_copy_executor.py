import subprocess
from unittest.mock import patch

import pytest

import copy_executor


def _mock_tmux(capture_text, pane_mode="0"):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        if command[:2] == ["tmux", "display-message"]:
            return subprocess.CompletedProcess(command, 0, stdout=f"{pane_mode}\n", stderr="")
        if command[:2] == ["tmux", "capture-pane"]:
            return subprocess.CompletedProcess(command, 0, stdout=capture_text, stderr="")
        if command[:2] in (["tmux", "load-buffer"], ["tmux", "send-keys"]) or command == ["termux-clipboard-set"]:
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        raise AssertionError(f"unexpected command: {command}")

    return calls, fake_run


def _commands(calls, prefix):
    return [command for command, _ in calls if command[:len(prefix)] == prefix]


def test_copy_entire_pane_uses_history_capture_and_proven_clipboard():
    calls, fake_run = _mock_tmux("alpha  \nbeta\n\n")
    with patch("copy_executor.subprocess.run", side_effect=fake_run):
        assert copy_executor.execute_copy("copy_entire_pane", "%1") is True
    capture = _commands(calls, ["tmux", "capture-pane"])[0]
    assert "-S" in capture and capture[capture.index("-S") + 1] == "-"
    assert "-t" in capture and capture[capture.index("-t") + 1] == "%1"
    buffer_writes = [kwargs for command, kwargs in calls if command == ["tmux", "load-buffer", "-"]]
    clipboard = [kwargs for command, kwargs in calls if command == ["termux-clipboard-set"]]
    assert len(buffer_writes) == len(clipboard) == 1
    assert buffer_writes[0]["input"] == "alpha\nbeta\n"
    assert clipboard[0]["input"] == "alpha\nbeta\n"


def test_copy_viewport_uses_visible_capture_and_shared_clipboard_path():
    calls, fake_run = _mock_tmux("visible one\nvisible two\n")
    with patch("copy_executor.subprocess.run", side_effect=fake_run):
        assert copy_executor.execute_copy("copy_viewport", "%7") is True
    capture = _commands(calls, ["tmux", "capture-pane"])[0]
    assert "-S" not in capture
    assert "-t" in capture and capture[capture.index("-t") + 1] == "%7"
    assert _commands(calls, ["tmux", "load-buffer", "-"])
    assert [kwargs["input"] for command, kwargs in calls if command == ["termux-clipboard-set"]] == ["visible one\nvisible two\n"]


def test_copy_subset_selects_latest_pytest_range_and_uses_shared_clipboard():
    capture_text = (
        "O ........F                         [100%]\n"
        "O old run failure\n"
        "P old prompt\n"
        "O ....E..                         [100%]\n"
        "O ================== ERRORS ==================\n"
        "O \n"
        "O     ValueError: bad\n"
        "PX current prompt\n"
        "X prompt info\n"
    )
    calls, fake_run = _mock_tmux(capture_text)
    with patch("copy_executor.subprocess.run", side_effect=fake_run):
        assert copy_executor.execute_copy("copy_subset", "%2") is True
    capture = _commands(calls, ["tmux", "capture-pane"])[0]
    assert "-F" in capture and "-S" in capture
    clipboard = [kwargs for command, kwargs in calls if command == ["termux-clipboard-set"]]
    buffer_writes = [kwargs for command, kwargs in calls if command == ["tmux", "load-buffer", "-"]]
    assert buffer_writes[0]["input"] == clipboard[0]["input"]
    assert clipboard[0]["input"] == (
        "....E..                         [100%]\n"
        "================== ERRORS ==================\n"
        "\n"
        "    ValueError: bad\n"
    )


def test_copy_subset_fails_closed_without_prompt_and_preserves_clipboard():
    calls, fake_run = _mock_tmux("O .......                         [100%]\nO 7 passed\n", pane_mode="1")
    with patch("copy_executor.subprocess.run", side_effect=fake_run):
        assert copy_executor.execute_copy("copy_subset", "%3") is False
    assert not _commands(calls, ["tmux", "load-buffer"])
    assert not _commands(calls, ["termux-clipboard-set"])
    assert _commands(calls, ["tmux", "send-keys"]) == [
        ["tmux", "send-keys", "-t", "%3", "-X", "cancel"]
    ]


def test_copy_from_copy_mode_exits_mode_after_copy():
    calls, fake_run = _mock_tmux("line one\nline two\n", pane_mode="1")
    with patch("copy_executor.subprocess.run", side_effect=fake_run):
        assert copy_executor.execute_copy("copy_viewport", "%4") is True
    load_index = next(i for i, (command, _) in enumerate(calls) if command == ["tmux", "load-buffer", "-"])
    cancel_index = next(i for i, (command, _) in enumerate(calls) if command == ["tmux", "send-keys", "-t", "%4", "-X", "cancel"])
    assert load_index < cancel_index


def test_unknown_copy_action_is_rejected_before_tmux_calls():
    calls, fake_run = _mock_tmux("irrelevant\n")
    with patch("copy_executor.subprocess.run", side_effect=fake_run):
        with pytest.raises(ValueError, match="unknown copy action"):
            copy_executor.execute_copy("copy_legacy", "%1")
    assert calls == []
