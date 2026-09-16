import re


def reconcile_managed_block(text, start_marker, end_marker, block):
    """Replace all occurrences of one managed block with its canonical form."""
    pattern = re.compile(
        re.escape(start_marker)
        + r".*?"
        + re.escape(end_marker),
        re.DOTALL,
    )

    if pattern.search(text):
        result = pattern.sub(lambda _: block, text)
    else:
        result = text
        if result and not result.endswith("\n"):
            result += "\n"
        result += "\n" + block + "\n"

    return result


def main():
    print("TKM installer is not yet wired to live configuration.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
