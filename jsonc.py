def strip_comments(text):
    """Remove JSONC comments without touching strings."""

    result = []

    i = 0
    in_string = False
    escape = False

    while i < len(text):

        char = text[i]

        if in_string:

            result.append(char)

            if escape:
                escape = False

            elif char == "\\":
                escape = True

            elif char == '"':
                in_string = False

            i += 1
            continue

        if char == '"':
            in_string = True
            result.append(char)
            i += 1
            continue

        # ----------------------------------------------------
        # Line comment
        # ----------------------------------------------------

        if (
            char == "/"
            and i + 1 < len(text)
            and text[i + 1] == "/"
        ):
            i += 2

            while (
                i < len(text)
                and text[i] != "\n"
            ):
                i += 1

            continue

        # ----------------------------------------------------
        # Block comment
        # ----------------------------------------------------

        if (
            char == "/"
            and i + 1 < len(text)
            and text[i + 1] == "*"
        ):
            i += 2

            while i + 1 < len(text):

                if (
                    text[i] == "*"
                    and text[i + 1] == "/"
                ):
                    i += 2
                    break

                i += 1

            continue

        result.append(char)
        i += 1

    return "".join(result)
