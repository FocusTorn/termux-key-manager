"""Pure parsing for semantic text ranges in tmux capture-pane output."""

import re

_PROGRESS_CHARS = frozenset(".FEsxXfPp-")
_PROMPT_TIME = re.compile(r"\d{4}\.\d{2}\Z")
_PROMPT_INPUT = "❯"


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


def _parse_capture_rows(capture):
    """Parse every capture row; return None for malformed row prefixes."""
    rows = []
    for raw_line in capture.splitlines(keepends=True):
        row = _parse_capture_row(raw_line)
        if row is None:
            return None
        rows.append(row)
    return rows


def _line_body(text):
    """Remove only the line-ending characters, preserving all other text."""
    if text.endswith("\r\n"):
        return text[:-2]
    if text.endswith("\n") or text.endswith("\r"):
        return text[:-1]
    return text


def _prompt_identity(context_text):
    """Return stable identity for the recognized context row, or None.

    The first field is a display clock (HHMM.SS), not prompt identity. The
    project/alias, branch, and Git-status fields after the first pipe are
    identity-bearing. Unknown formats are preserved rather than guessed.
    """
    fields = _line_body(context_text).split("|")
    if len(fields) < 3 or not _PROMPT_TIME.fullmatch(fields[0].strip()):
        return None

    identity_fields = tuple(field.strip() for field in fields[1:])
    if not identity_fields[0]:
        return None
    return identity_fields


def _empty_prompt_identity(segment):
    """Return identity for a recognized empty prompt segment, else None.

    The currently observed layout is a P-flagged context row such as
    '1526.12 | tkm main | ✔', immediately followed by an empty '❯' input row.
    """
    if len(segment) != 2 or "P" not in segment[0][0]:
        return None
    if _line_body(segment[1][1]).strip() != _PROMPT_INPUT:
        return None
    return _prompt_identity(segment[0][1])


def _deduplicate_empty_prompts(rows):
    """Collapse adjacent recognized empty prompts with identical identity.

    A prompt segment starts at a P-flagged row and ends before the next P row.
    Only the known two-row prompt format is eligible. Command-bearing prompts
    and unknown layouts are preserved. Callers determine their selection range
    before invoking this filter, keeping protocol boundaries independent.
    """
    prompt_starts = [
        index for index, (flags, _) in enumerate(rows) if "P" in flags
    ]
    if not prompt_starts:
        return rows

    filtered = list(rows[:prompt_starts[0]])
    previous_empty_identity = None

    for offset, start in enumerate(prompt_starts):
        end = (
            prompt_starts[offset + 1]
            if offset + 1 < len(prompt_starts)
            else len(rows)
        )
        segment = rows[start:end]
        identity = _empty_prompt_identity(segment)

        if identity is not None and identity == previous_empty_identity:
            continue

        filtered.extend(segment)
        previous_empty_identity = identity

    return filtered


def _visible_text(rows):
    return "".join(visible_text for _, visible_text in rows)


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
    Visible row text and line endings inside the selection are preserved,
    except redundant recognized empty prompts with matching identities.

    None is returned for missing boundaries or malformed capture rows.
    Callers must not replace the clipboard when this function returns None.
    """
    rows = _parse_capture_rows(capture)
    if rows is None:
        return None

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

    selected_rows = _deduplicate_empty_prompts(rows[progress_index:prompt_index])
    return _visible_text(selected_rows)


def select_entire_pane(capture):
    """Return whole-pane content before the final prompt-flagged row, or None.

    The final P-flagged prompt and everything after it are excluded before
    deduplication; earlier prompts remain ordinary content. Visible text and row
    endings before the cutoff are preserved exactly except for redundant
    matching empty prompts. Missing/malformed boundaries and an empty selection
    fail closed so callers can leave the clipboard untouched.
    """
    rows = _parse_capture_rows(capture)
    if rows is None:
        return None

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

    selected_rows = _deduplicate_empty_prompts(rows[:prompt_index])
    output = _visible_text(selected_rows)
    return output if output else None


def select_viewport(capture):
    """Return visible capture text after shared duplicate-empty-prompt filtering.

    The capture must use -F so tmux row flags identify prompt starts.
    Line endings and visible text are preserved here; viewport normalization
    remains the executor's separate existing step.
    """
    rows = _parse_capture_rows(capture)
    if rows is None:
        return None
    return _visible_text(_deduplicate_empty_prompts(rows))
