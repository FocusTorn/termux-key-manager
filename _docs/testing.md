# Testing

TKM tests the transformation from declarative source definitions to generated
behavior and the shared copy executor's contract.

## Test files

- `_test/test_manager.py`
- `_test/test_pytest_clipboard.py`
- `_test/test_copy_executor.py`
- `_test/test_tmux_replacement.py`
- `_test/test_shell_rc.py`

## test_manager.py

The manager tests cover shell-to-macro conversion, action conversion and
ordering, popup conversion, invalid action handling, JSONC comment stripping,
shell-command discovery, Bash integration, helper generation, Termux layout
generation, update orchestration, and tmux configuration. Helper-generation
assertions intentionally verify that the removed `cpy*` clipboard functions
are not emitted.

## test_pytest_clipboard.py

This suite tests the pure parser for flagged tmux capture rows. It covers:

- selecting the latest valid pytest progress row before the final prompt row
- preserving blank lines and multiline failure evidence
- treating prompt-like output without a prompt flag as ordinary output
- returning no range when prompt/progress boundaries are missing or rows are malformed

The selector does not call the clipboard. Clipboard-preservation behavior
when the selector fails is covered by the executor contract tests.

## test_copy_executor.py

This suite uses mocked subprocess calls to check whole-history and viewport
capture options, selected pytest output, shared tmux/Termux clipboard writes,
fail-closed behavior, and copy-mode cancellation. It is contract evidence,
not live Termux runtime evidence.

## Replacement and shell rc tests

`test_tmux_replacement.py` verifies that replacing the generated tmux block
preserves literal backslash sequences and surrounding user configuration.
`test_shell_rc.py` verifies that managed shell rc blocks update without
duplicating or overwriting surrounding user content.

## Running tests

Run the full test suite from the repository root:

    ./_test/run

The wrapper invokes pytest against `_test` and accepts zero or one test path.
Focused examples:

    ./_test/run test_pytest_clipboard.py
    ./_test/run test_copy_executor.py

The 2026-10-22 user-run coverage checkpoint reported 49 passed and 90% total
statement coverage. The durable log preserves aggregate percentages but not
the exact line-specific missing-coverage report.

## Integration evidence

A passing unit/contract test proves behavior in the test environment. It does
not by itself prove live Termux configuration was regenerated and reloaded.
When a change crosses that boundary, inspect or exercise the generated result
separately.
