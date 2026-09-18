# TKM Architecture

TKM is a configuration manager for Termux keyboard behavior and its supporting shell helpers.

## System flow

    macros.jsonc
        |
        +--> macros.py
        |      +--> properties.py -> ~/.termux/termux.properties
        |      +--> helpers.py    -> ~/.termux/helpers.sh + ~/.bashrc
        |      +--> tmux.py       -> ~/.tmux.conf
        |
        +--> update.py coordinates generation and reload

macros.jsonc is the authoritative source for keyboard definitions and layout.

TKM does not replace Bash, become an interactive shell, own the PTY, provide terminal-output recording, or act as a terminal sidecar. Termux remains responsible for terminal and shell execution. tmux remains responsible for tmux behavior.

Generated files are runtime outputs, not alternate configuration sources. Shared files are modified only in TKM-owned sections.

Design principle: keep keyboard policy in macros.jsonc, transformation logic in Python, and generated configuration at the Termux boundary.