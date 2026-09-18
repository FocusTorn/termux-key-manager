# Testing

TKM tests the transformation from declarative source definitions to generated behavior.

## Test files

Current tests include:

- `tests/test_manager.py`
- `tests/test_pytest_clipboard.py`
- `tests/test_tmux_replacement.py`

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
- generation of the `cpy_pytest` helper

## test_tmux_replacement.py

This suite verifies that replacement of the generated tmux block preserves literal backslash sequences and surrounding user configuration.

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