import unittest
import sys
import os
import tempfile
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from macros import shell_to_macro, convert_definition
from jsonc import strip_comments
from helpers import get_shell_commands, update_bashrc, generate_helpers
from properties import remove_extra_keys, build_termux_layout
import helpers
import properties
import config
import update

class TestTermuxKeyManager(unittest.TestCase):

    def test_shell_to_macro(self):
        self.assertEqual(shell_to_macro("ls"), "ls ENTER")
        self.assertEqual(shell_to_macro("echo test"), "echo SPACE test ENTER")
        self.assertEqual(shell_to_macro("a\tb"), "a TAB b ENTER")
        self.assertEqual(shell_to_macro("line1\nline2"), "line1 ENTER line2 ENTER")
        self.assertEqual(shell_to_macro(""), "ENTER")

    def test_convert_definition(self):
        self.assertEqual(convert_definition("string"), "string")

        defn = {"display": "Test", "shell": "echo test"}
        converted = convert_definition(defn)
        self.assertEqual(converted["macro"], "echo SPACE test ENTER")
        self.assertNotIn("shell", converted)

        popup_defn = {"display": "Pop", "popup": {"shell": "pwd"}}
        converted_popup = convert_definition(popup_defn)
        self.assertEqual(converted_popup["popup"]["macro"], "pwd ENTER")

    def test_jsonc_stripping(self):
        raw = "{\n    // line comment\n    \"key\": \"value // not a comment\",\n    /* block comment */\n    \"definitions\": {}\n}"
        cleaned = strip_comments(raw)
        self.assertNotIn("// line comment", cleaned)
        self.assertNotIn("/* block comment */", cleaned)
        self.assertIn('"key": "value // not a comment"', cleaned)
        self.assertIn('"definitions": {}', cleaned)

    def test_get_shell_commands(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "macros.jsonc")
            data = {
                "definitions": {
                    "CMD1": {"shell": "echo one"},
                    "CMD2": {"popup": {"shell": "echo two"}},
                    "NOCMD": {"key": "ENTER"}
                }
            }
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f)

            original_json_path = helpers.JSON_PATH
            helpers.JSON_PATH = json_path
            try:
                cmds = get_shell_commands()
                self.assertIn("echo one", cmds)
                self.assertIn("echo two", cmds)
                self.assertEqual(len(cmds), 2)
            finally:
                helpers.JSON_PATH = original_json_path

    def test_update_bashrc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bashrc_path = os.path.join(tmpdir, ".bashrc")
            original_bashrc = helpers.BASHRC_PATH
            helpers.BASHRC_PATH = bashrc_path
            try:
                update_bashrc(["echo one", "cpy"])
                self.assertTrue(os.path.exists(bashrc_path))
                with open(bashrc_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.assertIn("export HISTIGNORE='echo one:cpy*'", content)
                self.assertIn("# >>> termux-key-manager history >>>", content)

                update_bashrc(["echo two"])
                with open(bashrc_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.assertIn("export HISTIGNORE='echo two'", content)
                self.assertNotIn("echo one", content)
            finally:
                helpers.BASHRC_PATH = original_bashrc

    def test_generate_helpers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "macros.jsonc")
            helpers_path = os.path.join(tmpdir, "helpers.sh")
            bashrc_path = os.path.join(tmpdir, ".bashrc")

            data = {
                "definitions": {
                    "TEST_CMD": {"shell": "echo hello"}
                }
            }
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f)

            orig_json = helpers.JSON_PATH
            orig_helpers = helpers.HELPERS_PATH
            orig_bashrc = helpers.BASHRC_PATH

            helpers.JSON_PATH = json_path
            helpers.HELPERS_PATH = helpers_path
            helpers.BASHRC_PATH = bashrc_path

            try:
                generate_helpers()
                self.assertTrue(os.path.exists(helpers_path))
                with open(helpers_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.assertIn("echo hello", content)
                self.assertIn("refresh()", content)
                mode = os.stat(helpers_path).st_mode & 0o777
                self.assertEqual(mode, 0o700)
            finally:
                helpers.JSON_PATH = orig_json
                helpers.HELPERS_PATH = orig_helpers
                helpers.BASHRC_PATH = orig_bashrc

    def test_remove_extra_keys(self):
        lines = [
            "allow-external-apps = true\n",
            "extra-keys = [['A', 'B']]\n",
            "terminal-cursor-style = block\n"
        ]
        cleaned = remove_extra_keys(lines)
        cleaned_text = "".join(cleaned)
        self.assertNotIn("extra-keys", cleaned_text)
        self.assertIn("allow-external-apps = true", cleaned_text)
        self.assertIn("terminal-cursor-style = block", cleaned_text)

    def test_build_termux_layout(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "macros.jsonc")
            props_path = os.path.join(tmpdir, "termux.properties")

            data = {
                "definitions": {
                    "A": {"key": "A"},
                    "B": {"shell": "echo b"}
                },
                "layout": [["A", "B"]]
            }
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f)

            orig_config_json = config.JSON_PATH
            orig_config_props = config.PROPS_PATH
            orig_prop_json = properties.JSON_PATH
            orig_prop_props = properties.PROPS_PATH

            config.JSON_PATH = json_path
            config.PROPS_PATH = props_path
            properties.JSON_PATH = json_path
            properties.PROPS_PATH = props_path

            try:
                build_termux_layout()
                self.assertTrue(os.path.exists(props_path))
                with open(props_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.assertIn("extra-keys =", content)
                self.assertIn("echo SPACE b ENTER", content)
            finally:
                config.JSON_PATH = orig_config_json
                config.PROPS_PATH = orig_config_props
                properties.JSON_PATH = orig_prop_json
                properties.PROPS_PATH = orig_prop_props

    def test_update_main(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "macros.jsonc")
            helpers_path = os.path.join(tmpdir, "helpers.sh")
            bashrc_path = os.path.join(tmpdir, ".bashrc")
            props_path = os.path.join(tmpdir, "termux.properties")

            data = {
                "definitions": {"A": {"key": "A"}},
                "layout": [["A"]]
            }
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f)

            orig_json = config.JSON_PATH
            orig_helpers = helpers.HELPERS_PATH
            orig_bashrc = helpers.BASHRC_PATH
            orig_props = config.PROPS_PATH
            orig_prop_json = properties.JSON_PATH
            orig_prop_props = properties.PROPS_PATH

            config.JSON_PATH = json_path
            helpers.JSON_PATH = json_path
            helpers.HELPERS_PATH = helpers_path
            helpers.BASHRC_PATH = bashrc_path
            config.PROPS_PATH = props_path
            properties.JSON_PATH = json_path
            properties.PROPS_PATH = props_path

            orig_run = update.subprocess.run
            update.subprocess.run = lambda *args, **kwargs: None

            try:
                code = update.main()
                self.assertEqual(code, 0)
                self.assertTrue(os.path.exists(helpers_path))
                self.assertTrue(os.path.exists(props_path))
            finally:
                config.JSON_PATH = orig_json
                helpers.JSON_PATH = orig_json
                helpers.HELPERS_PATH = orig_helpers
                helpers.BASHRC_PATH = orig_bashrc
                config.PROPS_PATH = orig_props
                properties.JSON_PATH = orig_prop_json
                properties.PROPS_PATH = orig_prop_props
                update.subprocess.run = orig_run

if __name__ == "__main__":
    unittest.main()
