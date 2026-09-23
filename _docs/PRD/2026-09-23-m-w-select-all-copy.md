# Ad Hoc PRD: M-w Select-All Copy

**Date:** 2026-09-23  
**Status:** Ad hoc product requirement  
**Scope:** TKM M-w terminal copy functionality

## Purpose

Define the behavior of **M-w** as a terminal-level **Select All → Copy** operation.

M-w should copy the complete relevant terminal session content into the system clipboard while excluding the current shell prompt and anything rendered after that final prompt.

This is a standalone functionality. It is not the Patch Gate executor and does not define the Patch Gate implementation.

## User-visible behavior

When M-w is invoked:

1. Capture the complete available tmux scrollback for the current pane.
2. Identify the **last shell prompt boundary**.
3. Treat that boundary as the beginning of the current prompt.
4. Discard the current prompt and everything after it.
5. Copy everything before that boundary to the system clipboard.

The copied content is otherwise preserved exactly as captured.

## Prompt boundary

The preferred mechanism is **OSC 133**, using the terminal's standardized shell prompt/command boundary protocol rather than textual prompt matching.

The intended conceptual structure is:

```
OSC 133;A
prompt
OSC 133;B
command
output
OSC 133;C
OSC 133;D
next prompt
...
```

M-w should use the final prompt boundary as the cutoff.

The implementation must not infer a prompt merely because a line resembles:

```
~/projects/gpt-termux-rules $
```

The visible prompt text is not a reliable delimiter.

## Selection semantics

M-w is conceptually equivalent to:

**Select All → Copy**

For example:

```
output
output
output
~/projects/old $
output
output
~/projects/gpt-termux-rules $
~/projects/gpt-termux-rules $
```

must produce:

```
output
output
output
~/projects/old $
output
output
```

Earlier prompts are therefore part of the selection. Only the final prompt and everything after it are excluded.

## Preservation requirements

The operation must not:

- trim trailing whitespace;
- remove blank lines;
- normalize whitespace;
- rewrite line endings;
- filter terminal output;
- interpret output as commands;
- apply pytest-specific filtering;
- apply Patch Failed filtering;
- use the textual prompt format as the primary delimiter.

If captured output legitimately contains trailing whitespace, that whitespace remains part of the copied content.

## Capture scope

The source capture is the complete available tmux scrollback for the current pane, not merely the visible viewport.

The implementation should use the tmux capture mechanism appropriate for obtaining the full scrollback.

## Clipboard result

The final selected content is written to the system clipboard.

No terminal command should be injected into the pane as part of the copy operation.

## Failure / edge cases

The implementation must define and test behavior for:

- no prompt boundary present;
- exactly one prompt boundary;
- multiple prompt boundaries;
- output containing text that resembles a shell prompt;
- blank lines immediately before the final prompt;
- output containing trailing whitespace;
- an empty selection before the final prompt.

The implementation must not silently fall back to textual prompt matching when OSC 133 is unavailable unless that fallback is explicitly specified and tested as part of the final design.

## Relationship to other TKM copy functionality

This PRD defines **M-w only**.

Future semantic copy operations such as pytest-result or Patch Failed copying may use the same terminal-boundary information, but those are separate requirements and are not part of this PRD.

Likewise, Patch Gate execution is a separate functionality with its own PRD. The two features may share the broader idea of using a clipboard boundary, but their implementations and responsibilities remain independent.

## Implementation direction

Investigate tmux 3.7c behavior with OSC 133 and `capture-pane` first.

Verify that the prompt boundary survives into captured pane content in the form required to locate the final prompt reliably.

Then implement M-w around that verified boundary.

The implementation should prefer the smallest native tmux/terminal mechanism that satisfies the Select All → Copy contract.

## Acceptance criteria

M-w is complete when all of the following are demonstrated:

- Full tmux scrollback is captured.
- The final shell prompt is excluded.
- Everything rendered after the final prompt is excluded.
- Earlier prompts remain in the copied content.
- Prompt-like output is not incorrectly treated as a prompt.
- Captured whitespace is preserved.
- The resulting content reaches the system clipboard.
- The operation does not execute or inject shell commands.
- Behavior is verified on the target tmux/Termux environment.
