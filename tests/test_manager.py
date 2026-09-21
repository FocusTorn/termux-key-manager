import unittest
import subprocess
import tempfile
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from macros import shell_to_macro, convert_definition
from jsonc import strip_comments
from helpers import get_shell_commands, update_bashrc, generate_helpers
from properties import remove_extra_keys, build_termux_layout
import helpers
import properties
import config
import update
import tmux

class TestTermuxKeyManager(unittest.TestCase):

    def test_shell_to_macro(self):
        self.assertEqual(shell_to_macro("ls"), "ls ENTER")
        self.assertEqual(shell_to_macro("echo test"), "echo SPACE test ENTER")
        self.assertEqual(shell_to_macro("a\tb"), "a TAB b ENTER")
        self.assertEqual(shell_to_macro("line1\nline2"), "line1 ENTER line2 ENTER")
        self.assertEqual(shell_to_macro(""), "ENTER")

    def test_convert_definition_actions(self):
        definition = {
            "display": "Test",
            "actions": [
                {"tmux": "cancel-copy-mode"},
                {"shell": "clr"},
            ],
        }

        converted = convert_definition(definition)

        self.assertEqual(
            converted["macro"],
            "\x1b[5;30012~ clr ENTER",
        )
        self.assertNotIn("actions", converted)

    def test_convert_definition_tmux_action(self):
        definition = {
            "actions": [
                {"tmux": "cancel-copy-mode"},
            ],
        }

        converted = convert_definition(definition)

        self.assertEqual(
            converted["macro"],
            "\x1b[5;30012~",
        )

    def test_convert_definition_cpy_actions_cancel_copy_mode_first(self):
        definition = {
            "actions": [
                {"tmux": "cancel-copy-mode"},
                {"shell": "cpy_all"},
            ],
            "popup": {
                "actions": [
                    {"tmux": "cancel-copy-mode"},
                    {"shell": "cpy"},
                ],
            },
        }

        converted = convert_definition(definition)

        self.assertEqual(
            converted["macro"],
            "\x1b[5;30012~ cpy_all ENTER",
        )
        self.assertEqual(
            converted["popup"]["macro"],
            "\x1b[5;30012~ cpy ENTER",
        )

    def test_convert_definition_rejects_unknown_tmux_action(self):
        definition = {
            "actions": [
                {"tmux": "does-not-exist"},
            ],
        }

        with self.assertRaises(ValueError):
            convert_definition(definition)

    def test_convert_definition_actions_preserve_order(self):
        definition = {
            "actions": [
                {"shell": "first"},
                {"macro": "TAB"},
                {"shell": "second"},
            ],
        }

        converted = convert_definition(definition)

        self.assertEqual(
            converted["macro"],
            "first ENTER TAB second ENTER",
        )

    def test_convert_definition_rejects_invalid_action(self):
        definition = {
            "actions": [
                {"unknown": "value"},
            ],
        }

        with self.assertRaises(ValueError):
            convert_definition(definition)

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
                    "A": {"shell": "echo one"},
                    "B": {"shell": "echo two"},
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

    def test_get_shell_commands_includes_action_shells(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "macros.jsonc")
            data = {
                "definitions": {
                    "ACTIONS": {
                        "actions": [
                            {"shell": "cpy_all"},
                            {"tmux": "cancel-copy-mode"},
                        ],
                        "popup": {
                            "actions": [
                                {"shell": "cpy"},
                            ]
                        },
                    }
                }
            }
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f)

            original_json_path = helpers.JSON_PATH
            helpers.JSON_PATH = json_path
            try:
                cmds = get_shell_commands()
                self.assertIn("cpy_all", cmds)
                self.assertIn("cpy", cmds)
                self.assertNotIn("cancel-copy-mode", cmds)
            finally:
                helpers.JSON_PATH = original_json_path

    def test_update_bashrc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bashrc_path = os.path.join(tmpdir, ".bashrc")
            original_bashrc = helpers.BASHRC_PATH
            helpers.BASHRC_PATH = bashrc_path
            try:
                update_bashrc(["echo one", "cpy"])
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

    def test_copy_scaffold_filter_removes_prompt_lines(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            helpers_path = os.path.join(tmpdir, "helpers.sh")
            original_helpers_path = helpers.HELPERS_PATH
            helpers.HELPERS_PATH = helpers_path
            try:
                generate_helpers()

                script = f"""
source "{helpers_path}"
printf '%s\\n' \
    '~/projects/old $' \
    '~/projects/old $ cpy' \
    'REAL OUTPUT LINE 1' \
    '/data/data/com.termux/files/home $' \
    '/data/data/com.termux/files/home $ cpy_all' \
    'REAL OUTPUT LINE 2' \
    'ordinary $ output' \
    'another real line' |
    _tkm_filter_copy_scaffold cpy
"""
                result = subprocess.run(
                    ["bash", "-c", script],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                self.assertEqual(
                    result.stdout,
                    "REAL OUTPUT LINE 1\n"
                    "/data/data/com.termux/files/home $ cpy_all\n"
                    "REAL OUTPUT LINE 2\n"
                    "ordinary $ output\n"
                    "another real line\n",
                )
                self.assertEqual(result.stderr, "")
            finally:
                helpers.HELPERS_PATH = original_helpers_path

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
                with open(helpers_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.assertIn("echo hello", content)
                self.assertIn("refresh()", content)
                self.assertIn(
                    'tmux new-session -d -c "$HOME"',
                    content,
                )
                self.assertIn('_tkm_filter_copy_scaffold() {', content)
                self.assertIn('awk -v command="$command"', content)
                self.assertIn('marker = index(line, " $")', content)
                self.assertIn('prefix = substr(line, 1, marker - 1)', content)
                self.assertIn('suffix = substr(line, marker)', content)
                self.assertIn('suffix == " $ " command', content)
                self.assertIn("tmux capture-pane -pJ |", content)
                self.assertIn("tmux capture-pane -pJ -S - |", content)
                self.assertIn("sed 's/[[:space:]]*$//' |", content)
                self.assertIn("tmux load-buffer -w -", content)
                self.assertIn("termux-clipboard-set < \"$PREFIX/tmp/cpy_pytest.out\"", content)
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
            orig_tmux = config.TMUX_CONF_PATH
            orig_tmux_json = tmux.JSON_PATH
            orig_prop_json = properties.JSON_PATH
            orig_prop_props = properties.PROPS_PATH

            tmux_path = os.path.join(tmpdir, ".tmux.conf")

            config.JSON_PATH = json_path
            helpers.JSON_PATH = json_path
            helpers.HELPERS_PATH = helpers_path
            helpers.BASHRC_PATH = bashrc_path
            config.PROPS_PATH = props_path
            config.TMUX_CONF_PATH = tmux_path
            tmux.JSON_PATH = json_path
            properties.JSON_PATH = json_path
            properties.PROPS_PATH = props_path

            orig_run = update.subprocess.run
            update.subprocess.run = lambda *args, **kwargs: None

            try:
                code = update.main()
                self.assertEqual(code, 0)
                with open(helpers_path, "r", encoding="utf-8") as f:
                    helpers_content = f.read()
                with open(props_path, "r", encoding="utf-8") as f:
                    props_content = f.read()
                self.assertIn("AUTO-GENERATED", helpers_content)
                self.assertIn("extra-keys =", props_content)
            finally:
                config.JSON_PATH = orig_json
                helpers.JSON_PATH = orig_json
                helpers.HELPERS_PATH = orig_helpers
                helpers.BASHRC_PATH = orig_bashrc
                config.PROPS_PATH = orig_props
                config.TMUX_CONF_PATH = orig_tmux
                tmux.JSON_PATH = orig_tmux_json
                properties.JSON_PATH = orig_prop_json
                properties.PROPS_PATH = orig_prop_props
                update.subprocess.run = orig_run

if __name__ == "__main__":
    unittest.main()


class TestTmuxConfig(unittest.TestCase):

    def test_get_tmux_actions_preserves_mixed_action_sequence(self):
        import tmux

        orig_json = tmux.JSON_PATH

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".jsonc",
                delete=False,
            ) as f:
                json.dump(
                    {
                        "definitions": {
                            "CLR": {
                                "actions": [
                                    {"tmux": "cancel-copy-mode"},
                                    {"shell": "clr"},
                                ]
                            },
                            "CPY": {
                                "actions": [
                                    {"shell": "cpy_all"},
                                ]
                            },
                        }
                    },
                    f,
                )
                json_path = f.name

            tmux.JSON_PATH = json_path

            self.assertEqual(
                tmux.get_tmux_actions(),
                [
                    ("cancel-copy-mode", "clr"),
                ],
            )
        finally:
            tmux.JSON_PATH = orig_json
            os.unlink(json_path)

    def test_tmux_config_for_mixed_shell_then_cancel_action(self):
        from tmux import build_tmux_config

        config = build_tmux_config({
            ("clr", "cancel-copy-mode"),
        })

        expected_binding = (
            'bind-key -T copy-mode User0 '
            'run-shell "clr" \\; send-keys -X cancel'
        )
        expected_vi_binding = (
            'bind-key -T copy-mode-vi User0 '
            'run-shell "clr" \\; send-keys -X cancel'
        )

        self.assertIn(expected_binding, config)
        self.assertIn(expected_vi_binding, config)

    def test_tmux_config_for_mixed_cancel_and_shell_action(self):
        from tmux import build_tmux_config

        config = build_tmux_config({
            ("cancel-copy-mode", "clr"),
        })

        self.assertIn(
            'set -s user-keys[0] "\\e[5;30012~"',
            config,
        )
        expected_binding = (
            'bind-key -T copy-mode User0 '
            'send-keys -X cancel \\; run-shell "clr"'
        )
        expected_vi_binding = (
            'bind-key -T copy-mode-vi User0 '
            'send-keys -X cancel \\; run-shell "clr"'
        )

        self.assertIn(expected_binding, config)
        self.assertIn(expected_vi_binding, config)

    def test_tmux_config_for_cancel_copy_mode(self):
        from tmux import build_tmux_config

        config = build_tmux_config({
            "cancel-copy-mode"
        })

        self.assertIn(
            'set -g assume-paste-time 0',
            config
        )
        self.assertIn(
            'set -s user-keys[0] "\\e[5;30012~"',
            config
        )
        self.assertIn(
            'bind-key -T copy-mode User0 send-keys -X cancel',
            config
        )
        self.assertIn(
            'bind-key -T copy-mode-vi User0 send-keys -X cancel',
            config
        )
        self.assertNotIn(
            'bind-key -T root User0',
            config
        )
