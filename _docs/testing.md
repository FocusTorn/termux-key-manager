# Testing

TKM tests the transformation from declarative source definitions to generated configuration behavior.

## Current coverage

The manager tests cover shell-to-macro conversion, action conversion and ordering, popup conversion, invalid action handling, JSONC parsing, shell-command discovery, Bash integration, helper generation, Termux layout generation, update orchestration, and tmux configuration.

## Focused testing

During an implementation change, run tests for the affected component first.

    macros.py      -> macro/action tests
    helpers.py     -> helper/Bash tests
    properties.py  -> layout/property tests
    tmux.py        -> tmux tests
    update.py      -> orchestration tests

Use the broader suite as a regression checkpoint after a completed change slice.

A passing test does not by itself prove that live Termux configuration was reloaded. When a change crosses that boundary, verify the generated or live result separately.