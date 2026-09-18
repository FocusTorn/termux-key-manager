# Generated Files

TKM generates runtime configuration from repository sources.

| Path | Generator | TKM-owned content |
|---|---|---|
| ~/.termux/termux.properties | properties.py | extra-keys setting |
| ~/.termux/helpers.sh | helpers.py | Entire generated file |
| ~/.bashrc | helpers.py | Marked TKM block |
| ~/.tmux.conf | tmux.py | Marked TKM block |

macros.jsonc is the source of truth. Generated files are outputs and may be overwritten by the next update.

TKM must preserve user content outside its owned sections.

The .bashrc marker is:

    # >>> termux-key-manager history >>>
    # <<< termux-key-manager history <<<

The .tmux.conf marker is:

    # >>> termux-key-manager tmux >>>
    # <<< termux-key-manager tmux <<<

The extra-keys property is structurally replaced in termux.properties; unrelated properties remain.