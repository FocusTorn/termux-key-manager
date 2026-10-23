# Testing

TKM tests the transformation from declarative source definitions to generated behavior.

## Test files

Current tests include:

- `_test/test_manager.py`
- `_test/test_pytest_clipboard.py`
- `_test/test_copy_executor.py`
- `_test/test_tmux_replacement.py`

## test_manager.py

The manager tests cover:

- shell-to-macro conversion
- action conversion and ordering
- popup conversion
- invalid action handling
- JSONC comment stripping
- shell-command discovery
- Bash integration
- helper generation
- Termux layout generation
- update orchestration
- tmux configuration

## test_pytest_clipboard.py

This suite covers:

- retaining pytest failure evidence
- leaving non-pytest clipboard content unchanged
- selecting the latest pytest run
- latest pytest progress selection before the final prompt marker
- blank/multiline evidence and fail-closed behavior for missing/malformed boundaries

## test_copy_executor.py

This suite uses mocked subprocess calls to check whole-history and viewport
capture options, selected pytest output, shared tmux/Termux clipboard writes,
fail-closed behavior, and copy-mode cancellation. It is contract evidence,
not live Termux runtime evidence.

## test_tmux_replacement.py

This suite verifies that replacement of the generated tmux block preserves literal backslash sequences and surrounding user configuration.

## Running the suite

Run the full test suite from the repository root with `./_test/run`.
The wrapper invokes pytest against `_test` and accepts zero or one test path.

## Focused testing

During development, test the affected component first.

    macros.py      -> macro/action tests
    helpers.py     -> helper/Bash tests
    properties.py  -> layout/property tests
    tmux.py        -> tmux tests
    update.py      -> orchestration tests

Use the broader suite as a regression checkpoint after a completed change slice.

## Integration evidence

A passing test proves behavior in the test environment. It does not by itself prove that live Termux configuration was reloaded.

When a change crosses the live configuration boundary, inspect or exercise the generated result separately.