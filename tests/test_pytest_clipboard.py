from helpers import trim_pytest_output


def test_trim_pytest_output_keeps_progress_line_and_failure_evidence():
    source = """old terminal noise
~/projects/termux-dev-tools $ cd ~/projects/termux-dev-tools
python -m pytest -q _tests/test_validator.py
..................F....                 [100%]
================== FAILURES ===================
___ test_renderer_renders_results_in_order ____

    def test_renderer_renders_results_in_order():
        from validator import ValidationResult
>       from validator.renderer import render_results
E       ImportError: cannot import name 'render_results'

_tests/test_validator.py:503: ImportError
=========== short test summary info ===========
1 failed, 22 passed in 6.16s
~/projects/termux-dev-tools $
"""

    expected = """..................F....                 [100%]
================== FAILURES ===================
___ test_renderer_renders_results_in_order ____

    def test_renderer_renders_results_in_order():
        from validator import ValidationResult
>       from validator.renderer import render_results
E       ImportError: cannot import name 'render_results'

_tests/test_validator.py:503: ImportError
=========== short test summary info ===========
1 failed, 22 passed in 6.16s
~/projects/termux-dev-tools $
"""

    assert trim_pytest_output(source) == expected


def test_trim_pytest_output_leaves_non_pytest_clipboard_unchanged():
    source = """terminal output
some command
nothing resembling pytest progress
~/projects/termux-dev-tools $
"""
    assert trim_pytest_output(source) == source


def test_trim_pytest_output_uses_latest_pytest_run():
    source = """old pytest run
........F                         [100%]
old failure evidence
1 failed, 10 passed

new terminal noise
......E..                         [100%]
================== ERRORS ===================
new failure evidence
1 error, 8 passed
"""
    expected = """......E..                         [100%]
================== ERRORS ===================
new failure evidence
1 error, 8 passed
"""
    assert trim_pytest_output(source) == expected


def test_generate_helpers_includes_cpy_pytest():
    import json
    import os
    import tempfile
    import helpers

    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "macros.jsonc")
        helpers_path = os.path.join(tmpdir, "helpers.sh")
        bashrc_path = os.path.join(tmpdir, ".bashrc")

        data = {"definitions": {}}

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        original_json = helpers.JSON_PATH
        original_helpers = helpers.HELPERS_PATH
        original_bashrc = helpers.BASHRC_PATH

        helpers.JSON_PATH = json_path
        helpers.HELPERS_PATH = helpers_path
        helpers.BASHRC_PATH = bashrc_path

        try:
            helpers.generate_helpers()

            with open(helpers_path, "r", encoding="utf-8") as f:
                content = f.read()

            assert "cpy_pytest()" in content
            assert "termux-clipboard-get" in content
            assert "termux-clipboard-set" in content
        finally:
            helpers.JSON_PATH = original_json
            helpers.HELPERS_PATH = original_helpers
            helpers.BASHRC_PATH = original_bashrc
