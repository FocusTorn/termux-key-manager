# Installer and Update Model

TKM's current runtime update path is centered on update.py.

Run from the repository:

    python update.py

The operation:

1. generates ~/.termux/helpers.sh and the TKM block in .bashrc
2. generates extra-keys in ~/.termux/termux.properties
3. generates the TKM block in .tmux.conf
4. runs termux-reload-settings

If any stage raises an exception, the update reports failure rather than printing the success message.

## Safe-update principles

The update path should remain deterministic from repository source, limited to TKM-owned generated content, safe to repeat, and non-destructive to unrelated user configuration.

Do not describe historical installer, PTY, terminal-sidecar, or unrelated-project experiments as TKM architecture.