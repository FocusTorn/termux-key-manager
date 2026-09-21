import os


# ============================================================
# PROJECT
# ============================================================

PROJECT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ============================================================
# TERMUX
# ============================================================

TERMUX_HOME = os.path.expanduser("~")

TERMUX_DIR = os.path.join(
    TERMUX_HOME,
    ".termux"
)


# ============================================================
# SOURCE
# ============================================================

JSON_PATH = os.path.join(
    PROJECT_DIR,
    "macros.jsonc"
)


# ============================================================
# GENERATED FILES
# ============================================================

PROPS_PATH = os.path.join(
    TERMUX_DIR,
    "termux.properties"
)

HELPERS_PATH = os.path.join(
    TERMUX_DIR,
    "helpers.sh"
)

TKM_REFRESH_PATH = os.path.join(
    TERMUX_DIR,
    "tkm-refresh"
)

TMUX_CONF_PATH = os.path.join(
    TERMUX_HOME,
    ".tmux.conf"
)

BASHRC_PATH = os.path.join(
    TERMUX_HOME,
    ".bashrc"
)

ZSHRC_PATH = os.path.join(
    TERMUX_HOME,
    ".zshrc"
)
