from copy_selector import select_pytest_subset



def test_select_pytest_subset_uses_latest_progress_before_prompt():
    capture = (
        "- old terminal noise\n"
        "P old prompt\n"
        "O old pytest run\n"
        "O ........F                         [100%]\n"
        "O old failure evidence\n"
        "P previous prompt\n"
        "O pytest -q new_suite.py\n"
        "O ....E..                         [100%]\n"
        "O ================== ERRORS ==================\n"
        "- \n"
        "O     Traceback (most recent call last):\n"
        "O         raise ValueError('bad')\n"
        "O     ValueError: bad\n"
        "O     continuation detail\n"
        "O 1 error, 8 passed\n"
        "PX current prompt top rule\n"
        "X current prompt info\n"
    )
    expected = (
        "....E..                         [100%]\n"
        "================== ERRORS ==================\n"
        "\n"
        "    Traceback (most recent call last):\n"
        "        raise ValueError('bad')\n"
        "    ValueError: bad\n"
        "    continuation detail\n"
        "1 error, 8 passed\n"
    )

    assert select_pytest_subset(capture) == expected


def test_select_pytest_subset_fails_closed_without_prompt_marker():
    capture = (
        "O .......                         [100%]\n"
        "O 7 passed in 0.12s\n"
    )

    assert select_pytest_subset(capture) is None


def test_select_pytest_subset_requires_progress_before_final_prompt():
    capture = (
        "O not-a-progress-line [100%]\n"
        "PX current prompt top rule\n"
        "O ....F                         [100%]\n"
    )

    assert select_pytest_subset(capture) is None


def test_select_pytest_subset_keeps_prompt_like_output_without_prompt_flag():
    capture = (
        "O .......                         [100%]\n"
        "O ~/projects/demo $\n"
        "PX current prompt top rule\n"
    )
    expected = (
        ".......                         [100%]\n"
        "~/projects/demo $\n"
    )

    assert select_pytest_subset(capture) == expected


def test_select_pytest_subset_fails_closed_on_unflagged_capture_rows():
    capture = (
        "O .......                         [100%]\n"
        "unflagged row\n"
        "PX current prompt top rule\n"
    )

    assert select_pytest_subset(capture) is None



def test_select_pytest_subset_preserves_crlf_and_accepts_unterminated_prompt():
    capture = (
        "O .......                         [100%]\r\n"
        "O 7 passed in 0.12s\r\n"
        "PX current prompt without final newline"
    )
    expected = (
        ".......                         [100%]\r\n"
        "7 passed in 0.12s\r\n"
    )

    assert select_pytest_subset(capture) == expected
