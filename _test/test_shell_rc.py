import os
import tempfile
import unittest

import helpers


class TestShellRcUpdates(unittest.TestCase):

    def test_zshrc_is_updated_without_duplicate_blocks(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            zshrc = os.path.join(tmpdir, ".zshrc")
            with open(zshrc, "w", encoding="utf-8") as stream:
                stream.write("before\n")

            original = helpers.ZSHRC_PATH
            helpers.ZSHRC_PATH = zshrc
            try:
                helpers.update_zshrc(["echo one", "cpy"])
                helpers.update_zshrc(["echo two", "cpy"])

                with open(zshrc, "r", encoding="utf-8") as stream:
                    content = stream.read()

                self.assertTrue(content.startswith("before\n"))
                self.assertIn("HISTORY_IGNORE='(echo two|cpy*)'", content)
                self.assertNotIn("HISTORY_IGNORE=(", content.replace(
                    "HISTORY_IGNORE='(", ""
                ))
                self.assertNotIn("echo one", content)
                self.assertEqual(content.count(helpers.BASHRC_START), 1)
                self.assertEqual(content.count(helpers.BASHRC_END), 1)
            finally:
                helpers.ZSHRC_PATH = original

    def test_missing_zshrc_is_not_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            zshrc = os.path.join(tmpdir, ".zshrc")
            original = helpers.ZSHRC_PATH
            helpers.ZSHRC_PATH = zshrc
            try:
                helpers.update_zshrc(["echo one"])
                self.assertFalse(os.path.exists(zshrc))
            finally:
                helpers.ZSHRC_PATH = original

    def test_zshrc_preserves_content_outside_managed_block(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            zshrc = os.path.join(tmpdir, ".zshrc")
            with open(zshrc, "w", encoding="utf-8") as stream:
                stream.write(
                    "before\n"
                    + helpers.BASHRC_START
                    + "\nold block\n"
                    + helpers.BASHRC_END
                    + "\nafter\n"
                )

            original = helpers.ZSHRC_PATH
            helpers.ZSHRC_PATH = zshrc
            try:
                helpers.update_zshrc(["echo one"])
                with open(zshrc, "r", encoding="utf-8") as stream:
                    content = stream.read()

                self.assertTrue(content.startswith("before\n"))
                self.assertTrue(content.endswith("\nafter\n"))
                self.assertEqual(content.count(helpers.BASHRC_START), 1)
                self.assertEqual(content.count(helpers.BASHRC_END), 1)
            finally:
                helpers.ZSHRC_PATH = original


if __name__ == "__main__":
    unittest.main()
