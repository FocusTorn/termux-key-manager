# TKM Migration Notes

## Native Plugin / PTY Experiment moved to TAP

The native plugin / PTY recorder experiment was originally developed inside this repository but has been deliberately moved to:

    ~/projects/termux-action-pipeline/tap-core/

The preserved reference snapshot is:

    tap-core/reference/tkm-native-experiment/

**Do not recreate these files in TKM.**

If work refers to the native plugin, PTY recorder, terminal-output transport, plugin protocol, or plugin receiver, continue that work in TAP.

## Why the experiment moved

TKM's responsibility is the Termux keyboard/configuration manager.

The experiment expanded into broader concerns:

- PTY recording
- terminal-output capture
- Unix-socket transport
- plugin protocol
- plugin receiver
- plugin lifecycle
- recorder prototypes
- action/session transport

Those concerns belong in TAP rather than TKM.

## Files moved

```text
TKM                                      TAP

_docs/cpy-overhaul/                 →    reference/tkm-native-experiment/_docs/cpy-overhaul/

helpers.py.bak-pty                 →    reference/tkm-native-experiment/helpers.py.bak-pty

pty_recorder.py                    →    reference/tkm-native-experiment/pty_recorder.py
pty_recorder_prototype.py          →    reference/tkm-native-experiment/pty_recorder_prototype.py

tests/integration/                 →    reference/tkm-native-experiment/tests/integration/

tests/test_plugin_lifecycle.py     →    reference/tkm-native-experiment/tests/test_plugin_lifecycle.py
tests/test_plugin_protocol.py      →    reference/tkm-native-experiment/tests/test_plugin_protocol.py
tests/test_plugin_receiver.py      →    reference/tkm-native-experiment/tests/test_plugin_receiver.py
tests/test_plugin_transport.py     →    reference/tkm-native-experiment/tests/test_plugin_transport.py

tkm-launcher.py                    →    reference/tkm-native-experiment/tkm-launcher.py

tkm_plugin_protocol.py             →    reference/tkm-native-experiment/tkm_plugin_protocol.py
tkm_plugin_receiver.py             →    reference/tkm-native-experiment/tkm_plugin_receiver.py
tkm_plugin_transport.py            →    reference/tkm-native-experiment/tkm_plugin_transport.py
```

## Files intentionally restored in TKM

These files were modified during the experiment but were restored to the normal TKM versions:

```text
helpers.py
macros.jsonc
```

These remain authoritative TKM files.

Do not replace them with the experimental versions from TAP unless a new, explicit TKM change requires it.

## cpy.sh

`cpy.sh` was an older standalone tmux whole-buffer capture experiment.

It was intentionally removed because it was obsolete and was not part of the native plugin experiment moved to TAP.

Do not recreate it unless there is a new explicit reason to do so.

## Git history

The native plugin experiment was introduced in TKM by:

```text
2e5f027 Add TKM native plugin transport and recorder groundwork
```

TKM was restored to its core-manager state by:

```text
cae2061 Restore TKM to core macro manager
```

The preserved experiment was committed into TAP by:

```text
202ab9a Preserve TKM native plugin experiment
```

## Transport test WIP

There was one uncommitted change to:

```text
tests/test_plugin_transport.py
```

It corrected the test to account for `recv_frame()` consuming the 4-byte length prefix:

```python
# recv_frame() consumes the 4-byte length prefix
# and returns only the framed payload.
self.assertEqual(result.get("received"), expected[4:])
```

That WIP was preserved in the TAP reference snapshot and verified byte-for-byte before the temporary TKM stash was removed.

## Future-session rule

If a future session starts in `~/projects/termux-key-manager` and discovers that the files listed above are missing:

**They were intentionally moved. Nothing is broken.**

Look in:

```text
~/projects/termux-action-pipeline/tap-core/reference/tkm-native-experiment/
```

for the preserved historical snapshot.

Active development of that functionality belongs in:

```text
~/projects/termux-action-pipeline/tap-core/
```

## Current TKM boundary

TKM remains focused on:

```text
macros.jsonc
    ↓
macros.py
    ↓
properties.py
    ↓
Termux configuration
    ↓
helpers / update workflow
```

TAP is the home for the broader action/session/PTY/transport pipeline work.
