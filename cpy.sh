#!/data/data/com.termux/files/usr/bin/bash

tmux capture-pane -p |
    sed ':a;/^[[:space:]]*$/{$d;N;ba;}' |
    termux-clipboard-set
