# R1.2: TKM Implications

**Research basis:** tmux 3.7c internals documented in [R1.1](r1_1-tmux-internals.md).

## Objective

Replace TKM's legacy `cpy_*` shell-helper copy path with native tmux action execution, while preserving the required copy semantics and the three execution environments:

- root
- `copy-mode`
- `copy-mode-vi`

The implementation must not retain a legacy compatibility path.

## 1. The clipboard boundary is available natively

tmux 3.7c has two relevant native clipboard mechanisms:

### Native copy-mode selection

```text
copy-mode selection
        |
        v
copy-selection
        |
        v
tmux terminal clipboard machinery
        |
        v
OSC 52 / terminal clipboard
```

### Native tmux buffer write

```text
data
 |
 v
set-buffer -w
 |
 +--> tmux paste buffer
 |
 +--> terminal clipboard
```

The second mechanism does not solve the TKM capture problem because tmux has no native command that takes an existing paste buffer as the input to `set-buffer -w`.

Therefore the executor should not be designed around a `capture-pane -b` -> `set-buffer` bridge.

## 2. Entire-pane and viewport copy should investigate copy-mode first

The desired TKM callers are:

- `copy_entire_pane`
- `copy_viewport`
- `copy_subset`

The first two have a natural shared abstraction:

```text
                 native tmux copy executor
                           |
              +------------+------------+
              |                         |
       entire-pane range          viewport range
              |                         |
              +------------+------------+
                           |
                    copy-mode selection
                           |
                     copy-selection
                           |
                      clipboard
```

Their difference is the desired starting boundary.

The implementation should therefore avoid separate copy implementations merely because the starting range differs.

## 3. Root execution is the first important special case

For a root binding, the user is not already in copy mode.

A root binding therefore cannot simply assume that a copy-mode command is operating on an existing selection.

The candidate native choreography is conceptually:

```text
root binding
    |
    v
enter copy mode
    |
    v
position copy-mode cursor / selection
    |
    v
copy-selection
    |
    v
clipboard
    |
    v
leave/cancel copy mode as required
```

This must be tested as an actual tmux 3.7c binding because the transition into copy mode changes the target pane's mode state.

## 4. copy-mode and copy-mode-vi are separate execution contexts

The same logical TKM action must work when the current key table is:

```text
copy-mode
copy-mode-vi
```

A native copy action cannot assume that the root-table transition sequence is appropriate in those tables.

The implementation should bind the same logical action separately into all three contexts, while keeping the underlying executor semantics centralized.

The binding layer should describe the context-specific entry/exit behavior; the copy executor should own the common copy operation.

## 5. Do not confuse pane cursor and copy-mode cursor

The old implementation used:

```text
capture-pane -E '#{cursor_y}'
```

That references pane/application state.

A native copy-mode implementation instead manipulates tmux's copy-mode cursor and selection state.

Therefore the old endpoint expression is not automatically equivalent to a copy-mode selection endpoint.

Before implementation, verify the exact 3.7c copy-mode commands and coordinates needed to select:

- history beginning -> current pane cursor
- viewport beginning -> current pane cursor

Do not substitute `#{cursor_y}` merely because it appears in the old helper.

## 6. Semantic subsets are the hard part

The required semantic subset behavior is:

### Pytest

```text
latest pytest result/progress line
        through
line immediately before final terminal prompt
```

The prompt itself is excluded.

### Patch Failed

```text
Patch Failed
     through
line immediately before final terminal prompt
```

The prompt itself is excluded.

tmux copy mode provides searching, cursor movement, marks, selection, and copy commands. That makes some semantic subset selection potentially expressible natively.

But tmux is not a general text-processing engine. There is no generic native operation equivalent to:

```text
capture all lines
 -> run an arbitrary predicate
 -> calculate semantic boundaries
 -> copy resulting text
```

Therefore the semantic subset requirements must be demonstrated, not assumed.

## 7. copy-pipe is a valid non-legacy boundary if native selection is insufficient

If a subset cannot be expressed completely through copy-mode primitives, the correct fallback is not restoration of `cpy_*`.

A possible architecture is:

```text
native tmux selection
        |
        v
copy-pipe-and-cancel
        |
        v
small explicit external clipboard/extraction executor
```

This still makes the TKM action a tmux action and removes the Bash helper layer.

However, the exact external executor must be designed from the subset contract. It should not become a disguised reintroduction of the old `cpy_* ` architecture.

## 8. Legacy decommissioning remains absolute

The target state must not contain:

- `cpy`
- `cpy_all`
- `cpy_test`
- `cpy_pytest`
- tmux bindings that invoke those helpers
- compatibility fallbacks to those helpers
- dual native/legacy implementations kept "just in case"

The native implementation becomes the sole TKM copy implementation.

## 9. TMUX_ACTION_NATIVE needs evidence-driven treatment

Current source contains:

```python
TMUX_ACTION_NATIVE = {
    "clear_terminal",
}
```

Its current role is to distinguish commands emitted directly to tmux from commands wrapped in `run-shell`.

Once copy actions become native/context-specific definitions, the existing distinction may either:

- continue to be useful, or
- become unnecessary because the action representation itself identifies native commands.

Do not preserve or remove it by assumption.

Inspect all consumers and tests after the new representation is established.

## 10. Recommended implementation shape

The intended architecture remains:

```text
                    native tmux copy executor
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
       copy_entire_pane  copy_viewport   copy_subset
              |               |          /           \
              |               |      pytest      Patch Failed
              +---------------+---------------+
                              |
                         clipboard
```

The executor should centralize:

- copy-mode/native tmux mechanics
- clipboard invocation
- common cancellation/cleanup where applicable

The callers should supply:

- requested range
- semantic subset selector, where applicable
- context-specific entry/exit requirements

## 11. Required verification sequence before implementation

The next implementation work should establish observable behavior in tmux 3.7c before changing TKM source.

### A. Entire pane

Verify a native binding can select:

```text
history beginning
       ->
current pane cursor
```

and send the selection through tmux's clipboard mechanism.

### B. Viewport

Verify a native binding can select:

```text
viewport line 0
       ->
current pane cursor
```

and use the same clipboard path.

### C. Three contexts

Verify each action independently from:

```text
root
copy-mode
copy-mode-vi
```

with no mode-specific state leaking between invocations.

### D. Format behavior

Directly verify any use of:

```text
#{cursor_y}
```

or related formats in an actual binding. Do not infer behavior from configuration parsing alone.

### E. Semantic subset feasibility

Construct controlled pane content containing:

- ordinary output
- pytest progress/result lines
- `Patch Failed`
- prompt lines
- blank lines
- unrelated commands

Then determine whether tmux copy-mode primitives can select exactly the required ranges.

## 12. Design conclusion

The tmux 3.7c source supports a native clipboard path through copy-mode selection and `set-clipboard`.

It does **not** support a generic paste-buffer-to-clipboard transformation pipeline.

Therefore the TKM refactor should pivot from:

```text
capture-pane
 -> shell text processing
 -> termux-clipboard-set
```

toward:

```text
native tmux copy-mode selection
 -> copy-selection
 -> tmux clipboard
```

where the selection semantics can be expressed directly.

Where semantic extraction cannot be expressed by tmux itself, the fallback should remain a native tmux copy action using `copy-pipe`, not a return to `cpy_*` helpers.

The key implementation question is consequently no longer "how do we copy a captured tmux buffer?"

It is:

> **Can tmux 3.7c's copy-mode state machine express each TKM range contract exactly enough to make the selection itself the native executor input?**

That is the next behavior to prove before writing the TKM refactor.
