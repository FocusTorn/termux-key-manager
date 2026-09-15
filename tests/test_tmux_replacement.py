import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tmux import TMUX_END, TMUX_START, update_tmux_conf


class TestTmuxReplacement(unittest.TestCase):

    def test_update_tmux_conf_preserves_literal_backslash_e(self):
        config = 'set -s user-keys[0] "\\e[5;30012~"'

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tmux.conf"

            path.write_text(
                f"before\n{TMUX_START}\nold config\n{TMUX_END}\nafter\n",
                encoding="utf-8",
            )

            with patch("tmux.TMUX_CONF_PATH", path):
                update_tmux_conf(config)

            text = path.read_text(encoding="utf-8")

        self.assertIn(config, text)
        self.assertIn("before", text)
        self.assertIn("after", text)


if __name__ == "__main__":
    unittest.main()
