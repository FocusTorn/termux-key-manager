import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from macros import shell_to_macro, convert_definition
from jsonc import strip_comments
from helpers import get_shell_commands

class TestTermuxKeyManager(unittest.TestCase):

    def test_shell_to_macro(self):
        self.assertEqual(shell_to_macro("ls"), "ls ENTER")
        self.assertEqual(shell_to_macro("echo test"), "echo SPACE test ENTER")

    def test_jsonc_stripping(self):
        raw = '{\n    // comment\n    "definitions": {}\n}'
        cleaned = strip_comments(raw)
        self.assertNotIn("// comment", cleaned)
        self.assertIn('"definitions": {}', cleaned)

    def test_get_shell_commands(self):
        cmds = get_shell_commands()
        self.assertIsInstance(cmds, list)

if __name__ == "__main__":
    unittest.main()
