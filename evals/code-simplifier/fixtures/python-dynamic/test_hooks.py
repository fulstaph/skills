import unittest

from hooks import dispatch


class HookTests(unittest.TestCase):
    def test_dynamic_hook_remains_callable(self):
        self.assertEqual(dispatch("after_save", "record"), "saved:record")

    def test_unknown_hook_preserves_key_error(self):
        with self.assertRaises(KeyError) as raised:
            dispatch("missing", "record")
        self.assertEqual(raised.exception.args, ("missing",))


if __name__ == "__main__":
    unittest.main()
