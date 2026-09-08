import json
import re

from config import JSON_PATH
from config import PROPS_PATH

from jsonc import strip_comments
from macros import convert_definition


def remove_extra_keys(lines):
    """
    Remove an existing extra-keys definition while preserving
    other termux.properties settings.
    """

    output = []
    skipping = False

    for line in lines:

        stripped = line.lstrip()

        if (
            not skipping
            and re.match(
                r"^extra-keys\s*=",
                stripped,
                re.IGNORECASE
            )
        ):

            skipping = True
            continue

        if skipping:

            if re.match(
                r"^[A-Za-z0-9_.-]+\s*=",
                stripped
            ):

                skipping = False
                output.append(line)

            continue

        output.append(line)

    return output


def build_termux_layout():

    # --------------------------------------------------------
    # Read source
    # --------------------------------------------------------

    with open(
        JSON_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.loads(
            strip_comments(
                f.read()
            )
        )

    definitions = data.get(
        "definitions",
        {}
    )

    layout = data.get(
        "layout",
        []
    )

    # --------------------------------------------------------
    # Build native Termux layout
    # --------------------------------------------------------

    termux_layout = []

    for row in layout:

        termux_row = []

        for button_id in row:

            if button_id not in definitions:

                raise ValueError(
                    f"Button ID '{button_id}' not found."
                )

            termux_row.append(
                convert_definition(
                    definitions[button_id]
                )
            )

        termux_layout.append(
            termux_row
        )

    # --------------------------------------------------------
    # Serialize
    # --------------------------------------------------------

    formatted_keys = json.dumps(
        termux_layout,
        ensure_ascii=False,
        separators=(",", ":")
    )

    # --------------------------------------------------------
    # Read existing properties
    # --------------------------------------------------------

    try:

        with open(
            PROPS_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            lines = f.readlines()

    except FileNotFoundError:

        lines = []

    # --------------------------------------------------------
    # Remove old layout
    # --------------------------------------------------------

    lines = remove_extra_keys(lines)

    while (
        lines
        and not lines[-1].strip()
    ):

        lines.pop()

    if lines:
        lines.append("\n")

    # --------------------------------------------------------
    # Add new layout
    # --------------------------------------------------------

    lines.append(
        f"extra-keys = {formatted_keys}\n"
    )

    # --------------------------------------------------------
    # Write
    # --------------------------------------------------------

    with open(
        PROPS_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        f.writelines(lines)
