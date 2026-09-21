# R1.1: tmux Internals

**Research target:** tmux 3.7c  
**Purpose:** Establish the actual tmux command semantics relevant to replacing TKM's `cpy_*` shell helpers with native tmux bindings.

## Scope

This research covers:

- `capture-pane -b`
- `set-buffer`
- `load-buffer`
- `paste-buffer`
- `copy-selection`
- `copy-pipe` / `copy-pipe-and-cancel`
- `set-clipboard`
- command queues and chained bindings
- format expansion such as `#{cursor_y}`
- root, `copy-mode`, and `copy-mode-vi` binding tables

The source reference is the **3.7c tag**, not an inferred behavior from another tmux release.

## 1. capture-pane

In tmux 3.7c, `capture-pane` has two materially different output paths:

- With `-p`, captured text is written to the client/stdout.
- Without `-p`, captured text is stored in a tmux paste buffer.
- `-b buffer-name` names the destination paste buffer.
- `-S` and `-E` select the capture range.
- `-S -` means the beginning of available history.
- `-E -` means the end of the visible content.

The source ultimately passes non-`-p` capture data to `paste_set()`.

Therefore:

```text
capture-pane -b captured
        |
        v
tmux paste buffer
```

does **not** itself mean "copy to the system clipboard."

Source: [tmux 3.7c cmd-capture-pane.c](https://github.com/tmux/tmux/blob/3.7c/cmd-capture-pane.c)

## 2. set-buffer

`set-buffer` creates or replaces a tmux paste buffer from command data.

The important 3.7c behavior is its `-w` option. When `-w` is supplied and a target client exists, the implementation calls:

```c
tty_set_selection(&tc->tty, "", bufdata, bufsize);
```

after storing the data.

That is the tmux-side external clipboard path.

Conceptually:

```text
set-buffer -w DATA
       |
       +--> tmux paste buffer
       |
       +--> tty_set_selection()
                    |
                    v
             terminal clipboard
```

This is a real native tmux clipboard operation. It does not require `termux-clipboard-set`.

However, `set-buffer` accepts data as its argument. It does **not** provide an operation equivalent to "take the contents of paste buffer X and feed them back into `set-buffer -w`."

Source: [tmux 3.7c cmd-set-buffer.c](https://github.com/tmux/tmux/blob/3.7c/cmd-set-buffer.c)

## 3. load-buffer

`load-buffer` reads a file and stores the file contents in a tmux paste buffer.

Its `-w` option likewise causes the loaded data to be passed to `tty_set_selection()` for the target client.

Conceptually:

```text
file
 |
 v
load-buffer -w
 |
 +--> tmux paste buffer
 |
 +--> tty_set_selection()
              |
              v
       terminal clipboard
```

This proves that tmux has a native "data -> external clipboard" boundary.

It does **not**, however, make a tmux paste buffer readable by another tmux command as data. The input to `load-buffer` is a file path.

Source: [tmux 3.7c cmd-load-buffer.c](https://github.com/tmux/tmux/blob/3.7c/cmd-load-buffer.c)

## 4. paste-buffer

`paste-buffer` consumes a tmux paste buffer and writes it into the target pane's input stream.

The 3.7c implementation obtains the paste buffer data and sends it through the pane's `bufferevent`.

Therefore:

```text
paste-buffer
     |
     v
pane/application input
```

It is **not** a "paste this buffer into the system clipboard" command.

Consequently this does not form a clipboard bridge:

```text
capture-pane -b captured
        |
        v
paste-buffer -b captured
        |
        v
system clipboard
```

It would instead inject the captured text into the running application.

Source: [tmux 3.7c cmd-paste-buffer.c](https://github.com/tmux/tmux/blob/3.7c/cmd-paste-buffer.c)

## 5. copy-selection

`copy-selection` belongs to tmux copy-mode.

Its input is the **current copy-mode selection**, not an arbitrary paste buffer produced by `capture-pane`.

The copy-mode implementation builds the selected text and, when clipboard integration is enabled, reaches tmux's terminal selection machinery.

The relevant path is conceptually:

```text
copy-mode selection
        |
        v
copy-selection
        |
        v
tmux clipboard machinery
        |
        v
set-clipboard / terminal selection
        |
        v
outer terminal clipboard
```

This is the cleanest fully-native clipboard mechanism available to a TKM copy action.

Source: [tmux 3.7c window-copy.c](https://github.com/tmux/tmux/blob/3.7c/window-copy.c)

## 6. copy-pipe and copy-pipe-and-cancel

The copy-mode family also provides:

- `copy-pipe`
- `copy-pipe-and-cancel`
- related line/end-of-line/no-clear variants

These operate on the current copy-mode selection and pass the selected text to an external command.

`copy-pipe-and-cancel` additionally exits copy mode.

Conceptually:

```text
copy-mode selection
        |
        v
copy-pipe-and-cancel
        |
        v
external command
```

This is materially different from the old TKM architecture. An external clipboard command can be attached directly to the native tmux copy operation without a Bash helper such as `cpy` or `cpy_all`.

The remaining question for TKM is whether the semantic subset selection can be expressed natively before invoking the pipe.

Source: [tmux 3.7c window-copy.c](https://github.com/tmux/tmux/blob/3.7c/window-copy.c)

## 7. set-clipboard

tmux's `set-clipboard` option controls whether tmux sends copied selections to the outside terminal's clipboard mechanism.

For native copy operations, this is the relevant clipboard boundary:

```text
tmux copy operation
       |
       v
terminal selection
       |
       v
OSC 52 / terminal clipboard capability
       |
       v
outer terminal
```

The important point is that this is implemented inside tmux. A TKM native copy action does not have to shell out merely to reach the terminal clipboard if the terminal path supports it.

The tmux clipboard documentation describes this mechanism as tmux packaging copied text and sending it to the outside terminal.

Source: [tmux Clipboard documentation](https://github.com/tmux/tmux/wiki/Clipboard)

## 8. There is no native tmux-buffer-to-clipboard command

The relevant primitives produce an important negative result.

tmux can:

```text
capture-pane -> paste buffer
set-buffer   -> paste buffer
load-buffer  -> paste buffer
paste-buffer -> pane input
copy-selection -> clipboard
set-buffer -w -> clipboard
load-buffer -w -> clipboard
```

But there is no general command equivalent to:

```text
capture-pane -b A
set-buffer -w -b A
```

where the second command consumes paste buffer A as its data.

Therefore a design based on:

```text
capture-pane
    -> tmux buffer
    -> another tmux command
    -> clipboard
```

cannot be constructed from these primitives alone.

## 9. Command chaining

tmux stores key bindings as parsed command lists and executes them through its command queue.

A binding can therefore contain multiple commands separated with tmux command-list syntax.

The important architectural consequence is that a sequence such as:

```text
command 1
  ;
command 2
  ;
command 3
```

is a sequential tmux command queue, not a shell pipeline.

That makes native multi-step bindings possible.

However, each command still has its own command semantics and target resolution. A later command does not acquire arbitrary data from an earlier command merely because the commands are in the same queue.

Source: [tmux 3.7c cmd-bind-key.c](https://github.com/tmux/tmux/blob/3.7c/cmd-bind-key.c)

## 10. Format expansion

tmux formats such as `#{cursor_y}` are expanded by tmux when a command consumes the format.

This means format expansion is not equivalent to hard-coding a value when the configuration file is generated.

The exact target and state available to a format therefore matter.

In particular, TKM must distinguish:

- the pane/application cursor position
- the copy-mode cursor position

Entering copy mode introduces copy-mode state. A format referring to pane state should not be assumed to describe the copy-mode cursor.

For TKM, this means `#{cursor_y}` should be treated as a tmux format primitive requiring direct runtime verification, not assumed to be interchangeable with copy-mode selection coordinates.

Source: [tmux Formats documentation](https://github.com/tmux/tmux/wiki/Formats)

## 11. Root versus copy-mode key tables

tmux maintains separate key tables, including:

- root/no-prefix bindings
- `copy-mode`
- `copy-mode-vi`

A binding installed with `bind-key -n` belongs to the root table.

A binding installed with:

```text
bind-key -T copy-mode ...
bind-key -T copy-mode-vi ...
```

belongs to those copy-mode tables.

The same command chain can therefore be installed into multiple tables, but the **state in which that chain executes is different**.

A copy-mode command such as `send-keys -X copy-selection` depends on copy-mode state. It is not a generic root-table operation merely because the same text appears in a root binding.

Source: [tmux 3.7c cmd-bind-key.c](https://github.com/tmux/tmux/blob/3.7c/cmd-bind-key.c)

## 12. Findings relevant to TKM

The source establishes these facts:

1. `capture-pane -b` is a tmux-buffer operation, not a clipboard operation.
2. `set-buffer -w` and `load-buffer -w` can invoke tmux's terminal clipboard machinery.
3. `paste-buffer` writes into pane input and is not a clipboard bridge.
4. `copy-selection` is a native tmux clipboard path based on copy-mode selection.
5. `copy-pipe-and-cancel` is a native copy-mode selection path to an explicitly supplied external command.
6. A tmux command queue can execute multiple commands sequentially.
7. Format expansion is runtime tmux behavior and must be reasoned about in the command's target/state context.
8. Root and copy-mode bindings are separate key tables and must be tested in their actual execution modes.
9. There is no direct native operation that takes an arbitrary existing tmux paste buffer and feeds it to `set-buffer -w`.

These findings constrain, but do not yet choose, the TKM implementation.

