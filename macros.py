def shell_to_macro(command):
    """
    Convert a shell command into Termux macro syntax.
    """

    result = []
    current = []

    def flush():

        if current:
            result.append(
                "".join(current)
            )

            current.clear()

    for char in command:

        if char == " ":
            flush()
            result.append("SPACE")

        elif char == "\t":
            flush()
            result.append("TAB")

        elif char == "\n":
            flush()
            result.append("ENTER")

        else:
            current.append(char)

    flush()

    if not result or result[-1] != "ENTER":
        result.append("ENTER")

    return " ".join(result)


TMUX_ACTION_SEQUENCES = {
    "copy_mode_exit": "\x1b[5;30012~",
    "copy_entire_pane": "\x1b[5;30013~",
    "copy_test_result": "\x1b[5;30014~",
}

TMUX_ACTION_COMMANDS = {
    "copy_mode_exit": None,
    "copy_entire_pane": "bash -c '. ~/.termux/helpers.sh && cpy_all'",
    "copy_test_result": "bash -c '. ~/.termux/helpers.sh && cpy_test'",
}


def tmux_action_to_macro(action):
    """
    Convert a TKM tmux action into a private terminal sequence.

    The sequence is registered as a tmux user key and therefore
    remains distinct from following Termux macro actions.
    """

    try:
        return TMUX_ACTION_SEQUENCES[action]
    except KeyError:
        raise ValueError(
            f"unknown tmux action: {action}"
        )


def convert_definition(definition):
    """
    Convert a source definition into native Termux syntax.

    shell   → macro
    actions → ordered native macro sequence

    Conversion is recursive so popup definitions work too.
    """

    if not isinstance(definition, dict):
        return definition

    result = definition.copy()

    if "actions" in result:
        actions = result.pop("actions")

        if not isinstance(actions, list):
            raise ValueError("actions must be a list")

        compiled = []

        for action in actions:
            if not isinstance(action, dict):
                raise ValueError("each action must be an object")

            if set(action) == {"macro"}:
                compiled.append(action["macro"])

            elif set(action) == {"shell"}:
                compiled.append(
                    shell_to_macro(action["shell"])
                )

            elif set(action) == {"tmux"}:
                compiled.append(
                    tmux_action_to_macro(action["tmux"])
                )

            else:
                raise ValueError(
                    "each action must contain exactly one of: "
                    "macro, shell, tmux"
                )

        result["macro"] = " ".join(compiled)

    if "shell" in result:

        command = result.pop("shell")

        result["macro"] = shell_to_macro(
            command
        )

    if (
        "popup" in result
        and isinstance(result["popup"], dict)
    ):

        result["popup"] = convert_definition(
            result["popup"]
        )

    return result
