import unittest

from install import reconcile_managed_block


class TestManagedBlockReconciliation(unittest.TestCase):

    START = "# >>> termux-key-manager test >>>"
    END = "# <<< termux-key-manager test <<<"

    def test_adds_missing_block_without_touching_user_content(self):
        text = "set -g mouse on\n"
        block = f"{self.START}\nTKM\n{self.END}"

        result = reconcile_managed_block(
            text,
            self.START,
            self.END,
            block,
        )

        self.assertEqual(
            result,
            "set -g mouse on\n\n" + block + "\n",
        )

    def test_replaces_existing_block(self):
        text = (
            "before\n"
            f"{self.START}\nold\n{self.END}\n"
            "after\n"
        )
        block = f"{self.START}\nnew\n{self.END}"

        result = reconcile_managed_block(
            text,
            self.START,
            self.END,
            block,
        )

        self.assertEqual(
            result,
            "before\n" + block + "\nafter\n",
        )

    def test_collapses_duplicate_blocks_to_one(self):
        text = (
            f"{self.START}\none\n{self.END}\n"
            "user\n"
            f"{self.START}\ntwo\n{self.END}\n"
        )
        block = f"{self.START}\nnew\n{self.END}"

        result = reconcile_managed_block(
            text,
            self.START,
            self.END,
            block,
        )

        self.assertEqual(
            result,
            block + "\nuser\n",
        )

    def test_repeated_reconciliation_is_identical(self):
        block = f"{self.START}\nTKM\n{self.END}"

        first = reconcile_managed_block("user\n", self.START, self.END, block)
        second = reconcile_managed_block(first, self.START, self.END, block)

        self.assertEqual(first, second)

    def test_literal_backslash_e_in_block_is_preserved(self):
        block = (
            f'{self.START}\n'
            'set -s user-keys[0] "\\e[5;30012~"\n'
            f'{self.END}'
        )

        result = reconcile_managed_block(
            f"{self.START}\nold\n{self.END}\n",
            self.START,
            self.END,
            block,
        )

        self.assertIn('set -s user-keys[0] "\\e[5;30012~"', result)


if __name__ == "__main__":
    unittest.main()
