"""Pure parsing for semantic text ranges in tmux capture-pane output."""

_PROGRESS_CHARS = frozenset(".FEsxXfPp-")


def _parse_capture_row(raw_line):
    """Return (flags, visible_text_with_line_ending), or None if malformed."""
    if raw_line.endswith("\r\n"):
        row = raw_line[:-2]
        ending = "\r\n"
    elif raw_line.endswith("\n"):
        row = raw_line[:-1]
        ending = "\n"
    else:
        row = raw_line
        ending = ""

    flags, separator, visible_text = row.partition(" ")
    if (
        not separator
        or not flags
        or any(not ("A" <= char <= "Z" or char == "-") for char in flags)
    ):
        return None

    return flags, visible_text + ending


def _is_pytest_progress(visible_text):
    """Recognize pytest's percentage-complete progress row."""
    line = visible_text.strip()
    suffix = "[100%]"
    if not line.endswith(suffix):
        return False

    progress = line[:-len(suffix)].rstrip()
    return bool(progress) and all(char in _PROGRESS_CHARS for char in progress)


def select_pytest_subset(capture):
    """Return the latest pytest result through the final prompt, or None.

    Input is output from tmux capture-pane -pF -S -. Each row has a tmux
    flag prefix followed by one space and the visible row text.

    Selection begins at the latest valid pytest progress row before the last
    prompt-flagged row. The prompt and every row after it are excluded.
    Visible row text and line endings inside the selection are preserved
    exactly, while tmux's per-row flag prefixes are removed.

    None is returned for missing boundaries or malformed capture rows.
    Callers must not replace the clipboard when this function returns None.
    """
    rows = []
    for raw_line in capture.splitlines(keepends=True):
        row = _parse_capture_row(raw_line)
        if row is None:
            return None
        rows.append(row)

    prompt_index = next(
        (
            index
            for index in range(len(rows) - 1, -1, -1)
            if "P" in rows[index][0]
        ),
        None,
    )
    if prompt_index is None:
        return None

    progress_index = next(
        (
            index
            for index in range(prompt_index - 1, -1, -1)
            if _is_pytest_progress(rows[index][1])
        ),
        None,
    )
    if progress_index is None:
        return None

    return "".join(visible_text for _, visible_text in rows[progress_index:prompt_index])


def select_entire_pane(capture):
    """Return whole-pane content before the final prompt-flagged row, or None.

    Input is output from tmux capture-pane -pF -S -. Each row starts with
    tmux's line flags and one delimiter space. The final row carrying the P
    prompt flag and everything after it are excluded; earlier prompts remain
    ordinary content. Visible text and row endings before the cutoff are
    preserved exactly. Missing/malformed boundaries and an empty selection
    fail closed so callers can leave the current clipboard untouched.
    """
    rows = []
    for raw_line in capture.splitlines(keepends=True):
        row = _parse_capture_row(raw_line)
        if row is None:
            return None
        rows.append(row)

    prompt_index = next(
        (
            index
            for index in range(len(rows) - 1, -1, -1)
            if "P" in rows[index][0]
        ),
        None,
    )
    if prompt_index is None:
        return None

    output = "".join(visible_text for _, visible_text in rows[:prompt_index])
    return output if output else None

