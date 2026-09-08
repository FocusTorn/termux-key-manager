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


def convert_definition(definition):
    """
    Convert a source definition into native Termux syntax.

    shell → macro

    Conversion is recursive so popup definitions work too.
    """

    if not isinstance(definition, dict):
        return definition

    result = definition.copy()

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
